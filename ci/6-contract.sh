#!/bin/bash
# Step 6: Prove the patch is a contraction

# 6.1  Build patched bitcode
clang-15 -g -O0 -emit-llvm -c target_patched.c -o patched.bc

# 6.2  Compute the Jacobian norm symbolically
# The `jnorm` tool returns 0 if norm < 1, 1 otherwise.
jnorm patched.bc func_name > norm.txt

# The exit code of jnorm determines if the check passes.
if [ $? -eq 0 ]; then
  echo "CONTRACTIVE"
  exit 0
else
  echo "NOT PROVEN CONTRACTIVE"
  exit 1
fi
