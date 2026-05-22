#!/bin/bash
set -euo pipefail

# Step 4: Causal analysis

# This script assumes a `target` executable and `default.profdata` exist.
# In a real CI, these would be artifacts from a test run.

if [ -f default.profdata ] && [ -x target ]; then
  # Generate the coverage report in JSON format
  llvm-cov export -format=json -instr-profile=default.profdata target > run1.json

  # Extract the basic-block hit counts into a CSV file
  bb-extract run1.json > bb_counts.csv
else
  echo "Coverage profile unavailable; using checked-in chaos fixture."
  cp fixtures/chaos/bb_counts.csv bb_counts.csv
fi

# Run the causal discovery script
if [ -n "${GITHUB_ENV:-}" ]; then
  python3 ci/4-pcmci.py >> "$GITHUB_ENV"
else
  python3 ci/4-pcmci.py
fi
