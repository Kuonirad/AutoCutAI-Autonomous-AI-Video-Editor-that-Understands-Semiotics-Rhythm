# Step 2: Reconstruct the attractor in 3-D.

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


def _to_numeric(values: pd.Series) -> np.ndarray:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().all():
        return numeric.to_numpy(dtype=float)

    return np.array(
        [
            int(hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:8], 16)
            / 0xFFFFFFFF
            for value in values
        ],
        dtype=float,
    )


trace_path = Path("branches.ns")
if not trace_path.exists():
    x = np.arange(256, dtype=float)
    series = np.sin(x / 5.0) + 0.35 * np.sin(x / 17.0) + ((x * 37) % 19) / 50.0
else:
    series = _to_numeric(pd.read_csv(trace_path, header=None)[0])
    if series.size < 128:
        x = np.arange(256, dtype=float)
        series = np.sin(x / 5.0) + 0.35 * np.sin(x / 17.0) + ((x * 37) % 19) / 50.0

series = (series - series.mean()) / (series.std() or 1.0)
max_lag = max(2, min(49, series.size // 4))
scores = [
    abs(np.corrcoef(series[:-lag], series[lag:])[0, 1]) for lag in range(1, max_lag + 1)
]
tau = int(np.nanargmin(scores)) + 1

print(f"Computed delay (tau): {tau}")

m = 3
rows = series.size - (m - 1) * tau
if rows <= 0:
    raise ValueError("Not enough trace samples to build the attractor")

embedded = np.array([series[i : i + (m - 1) * tau + 1 : tau] for i in range(rows)])
np.savetxt("attractor.txt", embedded)

print("Saved attractor to attractor.txt")
