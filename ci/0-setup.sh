#!/bin/bash
# Step 0: One-time setup (run once per repo)

# 0.1  Install the toolchain
sudo apt-get update && sudo apt-get install -y \
  intel-processor-trace libipt-dev zstd \
 feat/chaos-pipeline
  python3-pip python3-venv \
  libllvm15-dev llvm-15-tools libclang-15-dev \
  libgsl-dev zlib1g-dev nlohmann-json3-dev cbmc

  python3-pip python3-venv
 main

python3 -m venv .chaos-env && source .chaos-env/bin/activate
pip install pip --upgrade
pip install pandas numpy scipy matplotlib seaborn \
      zstandard reservoir-py tigramite==5.2.0.5 \
      pygments z3-solver

# Create a lock-file so every runner gets the same bits.
pip freeze > requirements-chaos.txt
 feat/chaos-pipeline

# Build and install the custom C++ tools
echo "Building and installing custom C++ tools..."
g++ -O2 wtmm.cpp -lgsl -lgslcblas -lm -o wtmm
g++ -O2 bb-extract.cpp -o bb-extract
g++ -O2 jnorm.cpp $(llvm-config-15 --cxxflags --ldflags --libs core irreader) -o jnorm

sudo cp wtmm bb-extract jnorm /usr/local/bin
echo "Custom C++ tools installed."

 main