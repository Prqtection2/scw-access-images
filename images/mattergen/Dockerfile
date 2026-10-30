# MatterGen v1.0.3: the archived M1 image (SCW_24H_CLAUDE_2026-10-22/scripts/modal_scw_mattergen.py) as a locked Linux image:
# Python 3.10, torch 2.2.1 + cu118, PyG cu118 wheels, the .venv-mattergen pins.  Published as mattergen_v103_torch221_cu118.sif.
# The three config files the PyPI wheel lacks are fetched from tag v1.0.3, as in M1, and must match the sha256 of the local
# .venv-mattergen copies.  Checkpoints are NOT in the image (site checkpoint root + manifest; the template runs with HF_HUB_OFFLINE=1).
# T0C_R1 (Codex D03): the base is pinned by digest (resolved 2026-10-29 from Docker Hub), the uv bootstrap wheel by sha256, and
# the Debian package list (apt is not hash-locked) is recorded in /opt/image/dpkg.txt and hashed into the build provenance.
FROM python:3.10-slim-bookworm@sha256:5be5aaecb962a41567bc8041f1e9e3432cb085b037fe057f9a562630b2e4b370
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_NO_CACHE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
ARG MG=https://raw.githubusercontent.com/microsoft/mattergen/v1.0.3
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates libgomp1 \
 && rm -rf /var/lib/apt/lists/* && mkdir -p /opt/image \
 && printf 'uv==0.12.23 --hash=sha256:565c6e2874dbeae86c02f3dea97255e878fec672659a73d4930c6b93fcab2fff\n' > /tmp/uv.txt \
 && pip install --require-hashes --only-binary :all: -r /tmp/uv.txt && rm /tmp/uv.txt \
 && dpkg-query -W -f='${Package}=${Version}\n' | sort > /opt/image/dpkg.txt
COPY requirements.in requirements.lock /opt/image/
RUN uv pip install --system --require-hashes --no-deps --index-strategy unsafe-best-match \
      --extra-index-url https://download.pytorch.org/whl/cu118 --find-links https://data.pyg.org/whl/torch-2.2.0+cu118.html \
      -r /opt/image/requirements.lock \
 && uv pip freeze --system > /opt/image/freeze.txt
RUN SP=$(python3 -c "import site; print(site.getsitepackages()[0])") && mkdir -p "$SP/sampling_conf" \
 && curl -sfL "$MG/sampling_conf/default.yaml" -o "$SP/sampling_conf/default.yaml" \
 && curl -sfL "$MG/sampling_conf/csp.yaml" -o "$SP/sampling_conf/csp.yaml" \
 && curl -sfL "$MG/mattergen/common/gemnet/gemnet-dT.json" -o "$SP/mattergen/common/gemnet/gemnet-dT.json" \
 && printf '%s  %s\n' \
      88832cc2d18d3ad52a699d4d75b40b9b170cbc1064431b30d76bc2d7db1f025f "$SP/sampling_conf/default.yaml" \
      e45830593cdfcc48402d11d938fd9f9afbb7d9d684d87ca07dd29c6fa99aa2da "$SP/sampling_conf/csp.yaml" \
      867604ed6a605649241cd94d9604f25226fb1e362f332b7d1a9ae40d3f747e90 "$SP/mattergen/common/gemnet/gemnet-dT.json" \
    | sha256sum -c - \
 && python3 -c "import torch, torch_scatter, torch_sparse, torch_cluster, mattergen; print('torch', torch.__version__, 'cuda', torch.version.cuda)"
