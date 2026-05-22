# CI and native tools

AutoCutAI has two CI surfaces:

- `.github/workflows/ci.yml` runs the Python package checks on Python 3.12 and 3.13.
- `.github/workflows/chaos-check.yml` runs the experimental chaos-analysis shell pipeline in `ci/`.

The chaos pipeline depends on three native helper binaries:

- `wtmm` from `wtmm.cpp`
- `bb-extract` from `bb-extract.cpp`
- `jnorm` from `jnorm.cpp`

Build them locally on a Linux host with:

```sh
make native-tools
```

The default build expects `g++`, GSL, nlohmann-json, and LLVM 15 development tools. If your LLVM binary is not named `llvm-config-15`, override it:

```sh
make native-tools LLVM_CONFIG=llvm-config
```

Committed chaos-pipeline input fixtures live under `fixtures/chaos/`. Generated pipeline outputs such as `bb_counts.csv`, `pt.data`, `falpha.txt`, and `SHA512SUMS` should remain outside version control unless they are promoted to reviewed fixtures.

On GitHub-hosted runners, the chaos scripts fall back to deterministic fixtures when hardware tracing, coverage profiles, CBMC, or AWS QLDB credentials are unavailable. That keeps the workflow useful as a structural smoke check while preserving the real tool path for equipped runners.
