# scw-access-images

Container recipes for a materials-science benchmark on NSF ACCESS (NCSA Delta). Each image starts from a digest-pinned base and installs
a fully hash-locked requirements file (`--require-hashes`, no resolution at build time). The `build-images` workflow (manual trigger)
builds each image with Docker, converts it to an Apptainer SIF, smoke-tests it, writes a fail-closed provenance record
(`.github/scripts/provenance.py`), pushes the SIF to GHCR with ORAS, pulls it back and checks the bytes match. The job summary records
the SIF SHA-256 so the file pulled on the cluster can be checked byte for byte.

| Image | Contents |
|---|---|
| `scw` | CPU Python 3.13 analysis environment (numpy, numba, scipy, pymatgen, spglib, ase, torch CPU) |
| `mlip_cuda` | MatterSim 1.2.5 + CHGNet 0.4.2, torch 2.14.1 + CUDA 12.6 (also used on CPU) |
| `crystalformer` | CrystalFormer at commit 31bb734a, jax 0.6.2 + CUDA 12 |
| `mattergen` | MatterGen 1.0.3, torch 2.2.1 + CUDA 11.8, PyG |

No model weights, data or credentials are included.
