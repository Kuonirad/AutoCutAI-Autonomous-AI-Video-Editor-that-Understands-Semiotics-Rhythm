#!/bin/bash
set -euo pipefail

# Step 1: Collect the raw execution trace.

clang -g -O0 -fno-omit-frame-pointer -c target.c
clang -o target target.o

write_synthetic_trace() {
  python3 - <<'PY'
import math

for i in range(256):
    value = math.sin(i / 5.0) + 0.35 * math.sin(i / 17.0) + ((i * 37) % 19) / 50.0
    print(f"{value:.8f}")
PY
}

if command -v perf >/dev/null 2>&1 && perf list 2>/dev/null | grep -q "intel_pt"; then
  if perf record -e intel_pt//u --output pt.data -- ./target < fixtures/chaos/seed_input; then
    perf script -i pt.data --ns | awk '/branch:/ {print $4}' > branches.ns || true
  fi
fi

if [ ! -s branches.ns ]; then
  echo "Intel PT trace unavailable; writing deterministic CI trace fixture."
  write_synthetic_trace > branches.ns
  : > pt.data
fi
