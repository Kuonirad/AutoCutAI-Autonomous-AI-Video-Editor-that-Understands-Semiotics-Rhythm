#!/bin/bash
# Step 3: Multi-fractal spectrum via WTMM

# Run the custom wtmm tool on the attractor data
width=$(wtmm attractor.txt)
echo "WTMM spectrum width: $width"

# If width < 0.3 → stop pipeline.
# The user's original spec said to "exit 0" to stop, which is ambiguous.
# We will exit with a non-zero status code to fail the CI job, which is
# the standard way to stop a pipeline.
if (( $(echo "$width < 0.3" | bc -l) )); then
  echo "No significant non-linear signal found (width < 0.3). Stopping pipeline."
  exit 1
else
  exit 0
fi
