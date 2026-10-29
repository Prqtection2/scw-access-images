# SCW detector/encoder/SEGAL image (CPU only): the project .venv lock as a Linux environment.  Published as scw_r4.sif.
# Every package comes from requirements.lock with its sha256 enforced (--require-hashes); nothing is resolved at build time.
FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_NO_CACHE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libgl1 libglib2.0-0 ca-certificates \
 && rm -rf /var/lib/apt/lists/* && pip install uv==0.12.23
COPY requirements.in requirements.lock /opt/image/
RUN uv pip install --system --require-hashes --no-deps --index-strategy unsafe-best-match \
      --extra-index-url https://download.pytorch.org/whl/cpu -r /opt/image/requirements.lock \
 && uv pip freeze --system > /opt/image/freeze.txt \
 && python3 -c "import numpy, scipy, numba, pymatgen, spglib, ase, torch; print('numpy', numpy.__version__, 'numba', numba.__version__, 'torch', torch.__version__)"
