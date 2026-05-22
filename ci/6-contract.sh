#!/bin/bash
set -euo pipefail

# Step 6: Prove the patch is a contraction

# 6.1  Build patched bitcode
clang -g -O0 -emit-llvm -c target_patched.c -o patched.bc

# 6.2  Compute the Jacobian norm symbolically
# The `jnorm` tool returns 0 if norm < 1, 1 otherwise.
# The exit code of jnorm determines if the check passes.
if jnorm patched.bc main > norm.txt; then
  echo "CONTRACTIVE"
  exit 0
else
  echo "NOT PROVEN CONTRACTIVE"
  exit 1
fi
