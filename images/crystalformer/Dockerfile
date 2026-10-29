# CrystalFormer (P2 settings): the pins of SCW_24H_CLAUDE_2026-10-22/scripts/modal_scw_cf.py, jax 0.6.2 with CUDA 12 plugins.
# Published as crystalformer_jax062_cuda12.sif.  Source at the archived commit in /opt/CrystalFormer (the site config's cf_dir).
# The checkpoint is NOT in the image; the job template hash-checks the site copy against its pin before generating.
FROM python:3.10-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UV_NO_CACHE=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    XLA_PYTHON_CLIENT_PREALLOCATE=false
ARG CF_COMMIT=31bb734a3fd006af49a021921839061e6184cbf1
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/* && pip install uv==0.12.23
COPY requirements.in requirements.lock /opt/image/
RUN uv pip install --system --require-hashes --no-deps -r /opt/image/requirements.lock \
 && uv pip freeze --system > /opt/image/freeze.txt
RUN git clone https://github.com/deepmodeling/CrystalFormer.git /opt/CrystalFormer \
 && cd /opt/CrystalFormer && git checkout --detach "$CF_COMMIT" \
 && test "$(git rev-parse HEAD)" = "$CF_COMMIT" && git rev-parse HEAD > /opt/image/crystalformer_commit.txt \
 && python3 -c "import jax, haiku, optax, pymatgen, pyxtal; print('jax', jax.__version__)"
