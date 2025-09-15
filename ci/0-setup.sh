#!/bin/bash
# Step 0: One-time setup (run once per repo)

# 0.1  Install the toolchain
sudo apt-get update && sudo apt-get install -y \
  intel-processor-trace libipt-dev zstd \
  python3-pip python3-venv

python3 -m venv .chaos-env && source .chaos-env/bin/activate
pip install pip --upgrade
pip install pandas numpy scipy matplotlib seaborn \
      zstandard reservoir-py tigramite==5.2.0.5 \
      pygments z3-solver

# Create a lock-file so every runner gets the same bits.
pip freeze > requirements-chaos.txt
