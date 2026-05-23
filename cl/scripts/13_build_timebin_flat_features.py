#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ensure_dirs


def q(path) -> str:
    return str(path).replace("'", "''")


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    src = FEATURE_DIR / "timebin_1h_features.parquet"
    out = FEATURE_DIR / "timebin_1h_flat_features.parquet"
    rows = con.execute(f"SELECT DISTINCT subject_id, lifelog_date FROM read_parquet('{q(src)}') ORDER BY 1,2").fetchall()
    channels = [
        "screen_use_sum_h",
        "steps_sum_h",
        "distance_sum_h",
        "mlight_mean_h",
        "wlight_mean_h",
        "activity_mean_h",
        "screen_n_h",
        "pedo_n_h",
        "mlight_n_h",
        "wlight_n_h",
        "activity_n_h",
    ]
    select_exprs = ["subject_id", "lifelog_date"]
    for h in range(24):
        for c in channels:
            select_exprs.append(f"MAX(CASE WHEN hour={h} THEN {c} END) AS h{h:02d}_{c}")
    con.execute(f"""
        COPY (
            SELECT {', '.join(select_exprs)}
            FROM read_parquet('{q(src)}')
            GROUP BY subject_id, lifelog_date
            ORDER BY subject_id, lifelog_date
        ) TO '{q(out)}' (FORMAT PARQUET)
    """)
    ncols = len(con.execute(f"DESCRIBE SELECT * FROM read_parquet('{q(out)}')").fetchall())
    print(f"wrote {out} rows={len(rows)} cols={ncols}")

if __name__ == "__main__":
    main()
