from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
KEY = ["subject_id", "lifelog_date"]


def main() -> None:
    src = pd.read_parquet(OUT / "pre_sleep_relative_features.parquet").sort_values(KEY).reset_index(drop=True)
    numeric_cols = [c for c in src.columns if c not in KEY and pd.api.types.is_numeric_dtype(src[c])]
    base = src[KEY].copy()
    values = src[numeric_cols].astype("float32")
    grouped = values.groupby(src["subject_id"], sort=False)

    prev1 = grouped.shift(1)
    prev2 = grouped.shift(2)
    next1 = grouped.shift(-1)
    next2 = grouped.shift(-2)

    blocks = []
    specs = [
        ("dprev1", values - prev1),
        ("dnext1", next1 - values),
        ("prev1", prev1),
        ("next1", next1),
        ("past2dev", values - pd.concat([prev1, prev2]).groupby(level=0).mean()),
        ("future2dev", values - pd.concat([next1, next2]).groupby(level=0).mean()),
        ("neighbor_dev", values - pd.concat([prev1, next1]).groupby(level=0).mean()),
        ("neighbor_slope", next1 - prev1),
    ]
    for suffix, frame in specs:
        part = frame.astype("float32")
        part.columns = [f"{c}_{suffix}" for c in numeric_cols]
        blocks.append(part)

    out = pd.concat([base] + blocks, axis=1)
    out.to_parquet(OUT / "presleep_temporal_context_features.parquet", index=False)
    print({"shape": out.shape, "numeric_source_cols": len(numeric_cols), "derived_cols": out.shape[1] - len(KEY)})


if __name__ == "__main__":
    main()
