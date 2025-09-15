#!/bin/bash
# Step 3: Multi-fractal spectrum via WTMM (one-liner)

wget -qO- https://raw.githubusercontent.com/leonfrank/wtmm/main/wtmm.py | \
  python3 - attractor.txt > falpha.txt

# If width(falpha.txt) < 0.3 → exit 0 (no non-linear signal → stop pipeline).
# This check is implemented as a python snippet for convenience.
# The original prompt implies exiting with 0 on success (width < 0.3),
# but the user's instruction is to "exit 0". We follow the instruction literally.
python3 -c "import pandas as pd; df = pd.read_csv('falpha.txt', sep='\\s+', header=None, names=['q', 'alpha', 'f']); width = df['alpha'].max() - df['alpha'].min(); exit(0) if width < 0.3 else exit(1)"
