#!/bin/bash
set -euo pipefail

# Step 1: Collect the raw execution trace

# 1.1  Build the target with debug + Intel-PT
clang -g -O0 -fno-omit-frame-pointer -c target.c
clang -o target target.o

# 1.2  Record a trace (10 s of wall-clock == ~1 GB)
perf record -e intel_pt//u --output pt.data -- ./target < fixtures/chaos/seed_input

# 1.3  Convert to ASCII branch-flow (takes <30 s on CI)
perf script -i pt.data --ns | \
  awk '/branch:/ {print $4}' > branches.ns
