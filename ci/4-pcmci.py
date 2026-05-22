# Step 4: Causal root-cause summary.

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


bb_counts_path = Path(os.environ.get("BB_COUNTS_CSV", "bb_counts.csv"))
if not bb_counts_path.exists():
    bb_counts_path = Path("fixtures/chaos/bb_counts.csv")

df = pd.read_csv(bb_counts_path)
if df.empty:
    root_causes: list[int] = []
else:
    error_col = df.iloc[:, 0].to_numpy(dtype=float)
    candidates: list[int] = []
    for idx, column in enumerate(df.columns[1:], start=1):
        values = df[column].to_numpy(dtype=float)
        if len(values) > 1 and np.std(error_col) and np.std(values):
            corr = np.corrcoef(error_col, values)[0, 1]
            if np.isfinite(corr) and abs(corr) >= 0.5:
                candidates.append(idx)
        elif np.any(values):
            candidates.append(idx)
    root_causes = candidates

print(f"ROOT_CAUSES={','.join(map(str, root_causes))}")
