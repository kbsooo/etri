#!/usr/bin/env python3
from __future__ import annotations

import duckdb
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ensure_dirs


def q(path) -> str:
    return str(path).replace("'", "''")


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    daily = FEATURE_DIR / "daily_window_features.parquet"
    sleep = FEATURE_DIR / "sleep_proxy_v0.parquet"
    behavioral = FEATURE_DIR / "behavioral_state_features_k8.parquet"
    semantic = FEATURE_DIR / "semantic_features_v1.parquet"
    sleep_block = FEATURE_DIR / "sleep_block_features_v1.parquet"
    timebin_flat = FEATURE_DIR / "timebin_1h_flat_features.parquet"
    routine = FEATURE_DIR / "routine_deviation_features_v1.parquet"
    semantic_topk = FEATURE_DIR / "semantic_topk_features_v2.parquet"
    mechanism = FEATURE_DIR / "mechanism_sleep_load_features_v2.parquet"
    crossnight_flat = FEATURE_DIR / "crossnight_day_flat_features_v2.parquet"
    stress_arousal = FEATURE_DIR / "stress_arousal_q_features_v1.parquet"
    out = FEATURE_DIR / "model_features_v0.parquet"

    joins = [
        f"LEFT JOIN read_parquet('{q(sleep)}') s USING(subject_id, lifelog_date)",
    ]
    selects = ["d.*", "s.* EXCLUDE(subject_id, lifelog_date)"]
    if behavioral.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(behavioral)}') b USING(subject_id, lifelog_date)")
        selects.append("b.* EXCLUDE(subject_id, lifelog_date)")
    if semantic.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(semantic)}') sem USING(subject_id, lifelog_date)")
        selects.append("sem.* EXCLUDE(subject_id, lifelog_date)")
    if sleep_block.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(sleep_block)}') sb USING(subject_id, lifelog_date)")
        selects.append("sb.* EXCLUDE(subject_id, lifelog_date)")
    if timebin_flat.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(timebin_flat)}') tf USING(subject_id, lifelog_date)")
        selects.append("tf.* EXCLUDE(subject_id, lifelog_date)")
    if routine.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(routine)}') rt USING(subject_id, lifelog_date)")
        selects.append("rt.* EXCLUDE(subject_id, lifelog_date)")
    if semantic_topk.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(semantic_topk)}') stk USING(subject_id, lifelog_date)")
        selects.append("stk.* EXCLUDE(subject_id, lifelog_date)")
    if mechanism.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(mechanism)}') mech USING(subject_id, lifelog_date)")
        selects.append("mech.* EXCLUDE(subject_id, lifelog_date)")
    if crossnight_flat.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(crossnight_flat)}') cnf USING(subject_id, lifelog_date)")
        selects.append("cnf.* EXCLUDE(subject_id, lifelog_date)")
    if stress_arousal.exists():
        joins.append(f"LEFT JOIN read_parquet('{q(stress_arousal)}') qsa USING(subject_id, lifelog_date)")
        selects.append("qsa.* EXCLUDE(subject_id, lifelog_date)")

    sql = f"""
    CREATE OR REPLACE TEMP TABLE base AS
    SELECT {', '.join(selects)}
    FROM read_parquet('{q(daily)}') d
    {' '.join(joins)};

    CREATE OR REPLACE TEMP TABLE normalized AS
    SELECT * FROM base;
    """
    con.execute(sql)

    cols = con.execute("DESCRIBE normalized").fetchall()
    numeric_cols = [r[0] for r in cols if r[0] not in {"subject_id", "lifelog_date"} and any(t in r[1].upper() for t in ["DOUBLE", "BIGINT", "INTEGER", "HUGEINT", "FLOAT"])]

    exprs = ["subject_id", "lifelog_date"]
    for c in numeric_cols:
        safe = '"' + c.replace('"', '""') + '"'
        exprs.append(f"{safe}")
        exprs.append(f"AVG({safe}) OVER (PARTITION BY subject_id) AS {c}__subj_mean")
        exprs.append(f"{safe} - AVG({safe}) OVER (PARTITION BY subject_id) AS {c}__subj_delta")
        exprs.append(f"({safe} - AVG({safe}) OVER (PARTITION BY subject_id)) / NULLIF(STDDEV_POP({safe}) OVER (PARTITION BY subject_id), 0) AS {c}__subj_z")

    sql2 = f"""
    CREATE OR REPLACE TEMP TABLE final AS
    SELECT {', '.join(exprs)} FROM normalized;
    COPY final TO '{q(out)}' (FORMAT PARQUET);
    """
    con.execute(sql2)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{q(out)}')").fetchone()[0]
    c = len(con.execute(f"DESCRIBE SELECT * FROM read_parquet('{q(out)}')").fetchall())
    print(f"wrote {out} rows={n} cols={c}")


if __name__ == "__main__":
    main()
