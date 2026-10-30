# SCW detector/encoder/SEGAL image (CPU only): the project .venv lock as a Linux environment.  Published as scw_r4.sif.
# Every package comes from requirements.lock with its sha256 enforced (--require-hashes); nothing is resolved at build time.
# T0C_R1 (Codex D03): the base is pinned by digest (resolved 2026-10-29 from Docker Hub), the uv bootstrap wheel by sha256, and
# the Debian package list (apt is not hash-locked) is recorded in /opt/image/dpkg.txt and hashed into the build provenance.
FROM python:3.13-slim-bookworm@sha256:281d39ff02e3b389401586134ff9e6572954687822a58055ec07a60ded4e0b7f
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_NO_CACHE=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libgl1 libglib2.0-0 ca-certificates \
 && rm -rf /var/lib/apt/lists/* && mkdir -p /opt/image \
 && printf 'uv==0.12.23 --hash=sha256:565c6e2874dbeae86c02f3dea97255e878fec672659a73d4930c6b93fcab2fff\n' > /tmp/uv.txt \
 && pip install --require-hashes --only-binary :all: -r /tmp/uv.txt && rm /tmp/uv.txt \
 && dpkg-query -W -f='${Package}=${Version}\n' | sort > /opt/image/dpkg.txt
COPY requirements.in requirements.lock /opt/image/
RUN uv pip install --system --require-hashes --no-deps --index-strategy unsafe-best-match \
      --extra-index-url https://download.pytorch.org/whl/cpu -r /opt/image/requirements.lock \
 && uv pip freeze --system > /opt/image/freeze.txt \
 && python3 -c "import numpy, scipy, numba, pymatgen, spglib, ase, torch; print('numpy', numpy.__version__, 'numba', numba.__version__, 'torch', torch.__version__)"
