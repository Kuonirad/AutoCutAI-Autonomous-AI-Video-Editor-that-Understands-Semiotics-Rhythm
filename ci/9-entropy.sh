#!/bin/bash
# Step 9: Entropy stopping rule

# 9.1  Concatenate *all* test outputs
# Assumes test outputs are in a directory named 'tests' and end with '.out'
cat tests/*.out | zstd -19 -o behaviour.zst

# 9.2  Compressed-size ratio
original_bits=$(stat -c%s behaviour.zst)
patch_bits=$(stat -c%s target.patch)

# (1 byte patch costs 8 bits; behaviour must shrink by at least that much.)
if (( patch_bits * 8 < original_bits )); then
  echo "ENTROPY_OK"
  exit 0
else
  echo "ENTROPY_FAIL: Patch size is too large compared to behavior change."
  exit 1
fi
