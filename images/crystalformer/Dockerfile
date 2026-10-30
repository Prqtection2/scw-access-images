# CrystalFormer (P2 settings): the pins of SCW_24H_CLAUDE_2026-10-22/scripts/modal_scw_cf.py, jax 0.6.2 with CUDA 12 plugins.
# Published as crystalformer_jax062_cuda12.sif.  Source at the archived commit in /opt/CrystalFormer (the site config's cf_dir).
# The checkpoint is NOT in the image; the job template hash-checks the site copy against its pin before generating.
# T0C_R1 (Codex D03): the base is pinned by digest (resolved 2026-10-29 from Docker Hub), the uv bootstrap wheel by sha256, and
# the Debian package list (apt is not hash-locked) is recorded in /opt/image/dpkg.txt and hashed into the build provenance.
FROM python:3.10-slim-bookworm@sha256:5be5aaecb962a41567bc8041f1e9e3432cb085b037fe057f9a562630b2e4b370
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_NO_CACHE=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XLA_PYTHON_CLIENT_PREALLOCATE=false
ARG CF_COMMIT=31bb734a3fd006af49a021921839061e6184cbf1
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/* && mkdir -p /opt/image \
 && printf 'uv==0.12.23 --hash=sha256:565c6e2874dbeae86c02f3dea97255e878fec672659a73d4930c6b93fcab2fff\n' > /tmp/uv.txt \
 && pip install --require-hashes --only-binary :all: -r /tmp/uv.txt && rm /tmp/uv.txt \
 && dpkg-query -W -f='${Package}=${Version}\n' | sort > /opt/image/dpkg.txt
COPY requirements.in requirements.lock /opt/image/
RUN uv pip install --system --require-hashes --no-deps -r /opt/image/requirements.lock \
 && uv pip freeze --system > /opt/image/freeze.txt
RUN git clone https://github.com/deepmodeling/CrystalFormer.git /opt/CrystalFormer \
 && cd /opt/CrystalFormer && git checkout --detach "$CF_COMMIT" \
 && test "$(git rev-parse HEAD)" = "$CF_COMMIT" && git rev-parse HEAD > /opt/image/crystalformer_commit.txt \
 && python3 -c "import jax, haiku, optax, pymatgen, pyxtal; print('jax', jax.__version__)"
