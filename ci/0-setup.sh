#!/bin/bash
set -euo pipefail

# Step 0: One-time setup (run once per repo)

# 0.1  Install the toolchain
sudo apt-get update && sudo apt-get install -y \
  build-essential make \
  clang llvm llvm-dev libclang-dev \
  libipt-dev zstd \
  python3-pip python3-venv \
  libgsl-dev zlib1g-dev nlohmann-json3-dev

python3 -m venv .chaos-env
# shellcheck source=/dev/null
source .chaos-env/bin/activate
if [ -n "${GITHUB_PATH:-}" ]; then
  echo "$PWD/.chaos-env/bin" >> "$GITHUB_PATH"
fi
pip install pip --upgrade
pip install pandas numpy scipy zstandard pygments z3-solver

# Create a lock-file so every runner gets the same bits.
pip freeze > requirements-chaos.txt

# Build and install the custom C++ tools
echo "Building and installing custom C++ tools..."
make native-tools LLVM_CONFIG="${LLVM_CONFIG:-llvm-config}"

sudo cp wtmm bb-extract jnorm /usr/local/bin
echo "Custom C++ tools installed."
