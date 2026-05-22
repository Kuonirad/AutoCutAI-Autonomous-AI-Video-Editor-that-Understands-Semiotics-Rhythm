#!/bin/bash
set -euo pipefail

# Step 3: Multi-fractal spectrum via the repository WTMM tool.

width=$(wtmm attractor.txt)
echo "WTMM spectrum width: ${width}"
printf "wtmm_width %s\n" "$width" > falpha.txt

python3 - "$width" <<'PY'
import sys

width = float(sys.argv[1])
if width < 0.3:
    print("No significant non-linear signal found (width < 0.3).")
PY
