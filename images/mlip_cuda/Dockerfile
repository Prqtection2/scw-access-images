# MatterSim 1.2.5 + CHGNet 0.4.2 (one environment), torch 2.14.1 + CUDA 12.6 wheels, for the Delta GPU MLIP benchmarks.
# Published as mlip_mattersim125_chgnet042_cuda.sif.  The MatterSim checkpoint is NOT in the image: MatterSimCalculator reads
# ~/.local/mattersim/pretrained_models/mattersim-v1.0.0-1M.pth from the user's home, placed and hash-checked on the site beforehand.
# CHGNet's default weights ship inside the chgnet wheel (pinned by the lock hash).
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_NO_CACHE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 ca-certificates \
 && rm -rf /var/lib/apt/lists/* && pip install uv==0.12.23
COPY requirements.in constraints.txt requirements.lock /opt/image/
RUN uv pip install --system --require-hashes --no-deps --index-strategy unsafe-best-match \
      --extra-index-url https://download.pytorch.org/whl/cu126 -r /opt/image/requirements.lock \
 && uv pip freeze --system > /opt/image/freeze.txt \
 && python3 -c "import torch, mattersim, chgnet, ase, pymatgen, numpy; print('torch', torch.__version__, 'cuda', torch.version.cuda)" \
 && python3 -c "from chgnet.model import CHGNet; CHGNet.load(use_device='cpu', verbose=False)"
