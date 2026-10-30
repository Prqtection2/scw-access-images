# MatterSim 1.2.5 + CHGNet 0.4.2 (one environment), torch 2.14.1 + CUDA 12.6 wheels, for the Delta GPU MLIP benchmarks.
# Published as mlip_mattersim125_chgnet042_cuda.sif (also used on CPU: user decision 2026-10-29).  The MatterSim checkpoint is NOT in the
# image: it sits at ~/.local/mattersim/pretrained_models/mattersim-v1.0.0-1M.pth on the site.  T0C_R1 (Codex D02): the benchmark passes
# that path and its pin explicitly (jobs/mlip_bench.py); the ICT relax worker loads the same default file, which verify_artifacts binds
# to the pinned file before the worker runs.
# CHGNet's default weights ship inside the chgnet wheel (pinned by the lock hash).
# T0C_R1 (Codex D03): the base is pinned by digest (resolved 2026-10-29 from Docker Hub), the uv bootstrap wheel by sha256, and
# the Debian package list (apt is not hash-locked) is recorded in /opt/image/dpkg.txt and hashed into the build provenance.
FROM python:3.12-slim-bookworm@sha256:e697c81897302a4c4333bade000d98038fbb21eb064f8ee1fd42d02ebcd9d337
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_NO_CACHE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 ca-certificates \
 && rm -rf /var/lib/apt/lists/* && mkdir -p /opt/image \
 && printf 'uv==0.12.23 --hash=sha256:565c6e2874dbeae86c02f3dea97255e878fec672659a73d4930c6b93fcab2fff\n' > /tmp/uv.txt \
 && pip install --require-hashes --only-binary :all: -r /tmp/uv.txt && rm /tmp/uv.txt \
 && dpkg-query -W -f='${Package}=${Version}\n' | sort > /opt/image/dpkg.txt
COPY requirements.in constraints.txt requirements.lock /opt/image/
RUN uv pip install --system --require-hashes --no-deps --index-strategy unsafe-best-match \
      --extra-index-url https://download.pytorch.org/whl/cu126 -r /opt/image/requirements.lock \
 && uv pip freeze --system > /opt/image/freeze.txt \
 && python3 -c "import torch, mattersim, chgnet, ase, pymatgen, numpy; print('torch', torch.__version__, 'cuda', torch.version.cuda)" \
 && python3 -c "from chgnet.model import CHGNet; CHGNet.load(use_device='cpu', verbose=False)"
