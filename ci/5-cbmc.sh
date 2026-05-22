#!/bin/bash
set -euo pipefail

# Step 5: Bounded-model-check the root cause only

# This script assumes that the ROOT_CAUSES environment variable is set,
# likely from the output of the previous step (4-causal.sh).

# 5.1  Extract only the basic-blocks that touch root-cause variables
# NOTE: The original prompt used a non-existent `LLVMAutoDiff.so` pass for this.
# As this tool does not exist, this step is currently a placeholder.
# In a real implementation, a custom LLVM pass would be needed here to
# slice the bitcode based on the root causes.
clang-15 -g -O0 -emit-llvm -c target.c -o target.bc
# opt -load LLVMAutoDiff.so -mark-blocks -root-causes ${ROOT_CAUSES} target.bc -o slice.bc
cp target.bc slice.bc # Placeholder action

# 5.2  Bounded check (bound = 40 steps)
cbmc slice.bc --unwind 40 --property target.spec > cbmc.out

# If VERIFICATION SUCCESSFUL, continue; else fail job.
if grep -q "VERIFICATION SUCCESSFUL" cbmc.out; then
  exit 0
else
  exit 1
fi
