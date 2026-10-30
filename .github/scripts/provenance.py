"""Fail-closed build provenance for one image (T0C_R1, Codex D03).  Exported to the build repository as .github/scripts/provenance.py and
called by .github/workflows/build-images.yml; tested in the campaign (tests/test_t0c_r1.py).

  python3 provenance.py make     --img IMG --work DIR --recipes DIR     (BEFORE publication)
  python3 provenance.py finalize --img IMG --work DIR                   (AFTER the push: the pulled-back bytes must match)

The workflow's shell steps (bash -euo pipefail) write every observation to a file first; this script runs no external command.  It reads
those files as raw bytes, hashes exact bytes, and refuses (exit 1, no provenance written) when anything is missing, empty or
inconsistent:
  IMG.base_ref.txt            the Dockerfile's FROM, which must be pinned by digest (name@sha256:...)
  IMG.base_repo_digests.json  `docker image inspect --format '{{json .RepoDigests}}'` of the pulled base: a nonempty list containing the
                              pinned digest
  IMG.base_id.txt             the pulled base's image id (sha256:<64 hex>)
  IMG.sif, IMG.sif.sha256     the SIF and the hash the conversion step recorded; recomputed here and compared
  IMG.freeze.txt, IMG.dpkg.txt   /opt/image/freeze.txt and /opt/image/dpkg.txt copied out of the SIF (exact bytes)
  IMG.apptainer_version.txt   `apptainer --version`
  IMG.ref, IMG.roundtrip.sif  (finalize) the ORAS reference pushed, and the SIF pulled back from it"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HEX64 = re.compile(r"[0-9a-f]{64}")


def fail(msg):
    raise SystemExit(f"provenance: {msg}")


def need(path: Path) -> bytes:
    if not path.is_file():
        fail(f"{path.name} is missing")
    b = path.read_bytes()
    if not b.strip():
        fail(f"{path.name} is empty")
    return b


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_atomic(path: Path, rec: dict):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def make(a) -> dict:
    w, img, rec_dir = Path(a.work), a.img, Path(a.recipes) / a.img
    base_ref = need(w / f"{img}.base_ref.txt").decode("utf-8").strip()
    m = re.fullmatch(r"(\S+)@(sha256:[0-9a-f]{64})", base_ref)
    if not m:
        fail(f"the Dockerfile FROM {base_ref!r} is not pinned by digest")
    pinned = m.group(2)
    try:
        digests = json.loads(need(w / f"{img}.base_repo_digests.json"))
    except json.JSONDecodeError as e:
        fail(f"base_repo_digests is not JSON ({e})")
    if not isinstance(digests, list) or not digests or not all(isinstance(x, str) for x in digests):
        fail(f"base_repo_digests {digests!r} is not a nonempty list of strings")
    if not any(x.endswith("@" + pinned) for x in digests):
        fail(f"the pulled base {digests} does not carry the pinned digest {pinned}")
    base_id = need(w / f"{img}.base_id.txt").decode("utf-8").strip()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", base_id):
        fail(f"base image id {base_id!r} is malformed")
    sif = w / f"{img}.sif"
    recorded = need(w / f"{img}.sif.sha256").decode("utf-8").strip()
    actual = sha_file(sif) if sif.is_file() else fail("the SIF is missing")
    if not HEX64.fullmatch(recorded) or recorded != actual:
        fail(f"SIF sha256 {actual} does not equal the recorded {recorded!r}")
    commit, run = os.environ.get("GITHUB_SHA", ""), os.environ.get("GITHUB_RUN_ID", "")
    if not re.fullmatch(r"[0-9a-f]{40}", commit) or not run.isdigit():
        fail("GITHUB_SHA / GITHUB_RUN_ID are missing or malformed")
    rec = {
        "image": img, "build_repo_commit": commit, "run_id": run,
        "sif_sha256": actual, "sif_bytes": sif.stat().st_size,
        "base_image": base_ref, "base_repo_digests": digests, "base_image_id": base_id,
        "dockerfile_sha256": sha_file(rec_dir / "Dockerfile"), "lock_sha256": sha_file(rec_dir / "requirements.lock"),
        "freeze_sha256": hashlib.sha256(need(w / f"{img}.freeze.txt")).hexdigest(),
        "dpkg_sha256": hashlib.sha256(need(w / f"{img}.dpkg.txt")).hexdigest(),
        "apptainer": need(w / f"{img}.apptainer_version.txt").decode("utf-8").strip(),
        "published": False,
    }
    if (rec_dir / "constraints.txt").is_file():
        rec["constraints_sha256"] = sha_file(rec_dir / "constraints.txt")
    write_atomic(w / f"{img}.provenance.json", rec)
    print(json.dumps(rec, indent=1))
    return rec


def finalize(a) -> dict:
    w, img = Path(a.work), a.img
    try:
        rec = json.loads(need(w / f"{img}.provenance.json"))
    except json.JSONDecodeError as e:
        fail(f"provenance.json is not JSON ({e})")
    if rec.get("image") != img or not HEX64.fullmatch(str(rec.get("sif_sha256", ""))) or rec.get("published") is not False:
        fail("provenance.json was not made by `make` for this image")
    ref = need(w / f"{img}.ref").decode("utf-8").strip()
    if not re.fullmatch(r"oras://ghcr\.io/[a-z0-9._/-]+:[0-9a-f]{12}", ref) or not ref.endswith(rec["build_repo_commit"][:12]):
        fail(f"ORAS reference {ref!r} is malformed or not tagged with this commit")
    rt = w / f"{img}.roundtrip.sif"
    got = sha_file(rt) if rt.is_file() else fail("the pulled-back SIF is missing")
    if got != rec["sif_sha256"]:
        fail(f"the published bytes ({got}) differ from the built SIF ({rec['sif_sha256']})")
    rec.update(oras_ref=ref, oras_roundtrip_sha256=got, published=True)
    write_atomic(w / f"{img}.provenance.json", rec)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as s:
            s.write(f"### {img}\n```json\n{json.dumps(rec, indent=1)}\n```\n")
    print(json.dumps(rec, indent=1))
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["make", "finalize"])
    ap.add_argument("--img", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--recipes", default="images")
    a = ap.parse_args(argv)
    (make if a.cmd == "make" else finalize)(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
