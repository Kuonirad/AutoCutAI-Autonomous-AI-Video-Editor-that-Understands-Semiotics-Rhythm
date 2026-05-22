#!/bin/bash
set -euo pipefail

# Step 0: One-time setup (run once per repo)

# 0.1  Install the toolchain
sudo apt-get update && sudo apt-get install -y \
  build-essential make \
  intel-processor-trace libipt-dev zstd \
  python3-pip python3-venv \
  libllvm15-dev llvm-15-tools libclang-15-dev \
  libgsl-dev zlib1g-dev nlohmann-json3-dev cbmc

python3 -m venv .chaos-env
# shellcheck source=/dev/null
source .chaos-env/bin/activate
if [ -n "${GITHUB_PATH:-}" ]; then
  echo "$PWD/.chaos-env/bin" >> "$GITHUB_PATH"
fi
pip install pip --upgrade
pip install pandas numpy scipy matplotlib seaborn \
      zstandard reservoir-py tigramite==5.2.0.5 \
      pygments z3-solver

# Create a lock-file so every runner gets the same bits.
pip freeze > requirements-chaos.txt

# Build and install the custom C++ tools
echo "Building and installing custom C++ tools..."
make native-tools

sudo cp wtmm bb-extract jnorm /usr/local/bin
echo "Custom C++ tools installed."
