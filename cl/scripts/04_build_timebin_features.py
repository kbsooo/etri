#!/usr/bin/env python3
from __future__ import annotations

import duckdb
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ITEM_DIR, ensure_dirs


def q(path) -> str:
    return str(path).replace("'", "''")


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    out = FEATURE_DIR / "timebin_1h_features.parquet"
    sql = f"""
    CREATE OR REPLACE TEMP TABLE screen_h AS
    SELECT subject_id, CAST(timestamp AS DATE) AS lifelog_date, EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           COUNT(*) AS screen_n_h, AVG(m_screen_use) AS screen_use_mean_h, SUM(m_screen_use) AS screen_use_sum_h
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mScreenStatus.parquet')}') GROUP BY 1,2,3;

    CREATE OR REPLACE TEMP TABLE pedo_h AS
    SELECT subject_id, CAST(timestamp AS DATE) AS lifelog_date, EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           COUNT(*) AS pedo_n_h, SUM(step) AS steps_sum_h, SUM(distance) AS distance_sum_h, AVG(speed) AS speed_mean_h
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wPedo.parquet')}') GROUP BY 1,2,3;

    CREATE OR REPLACE TEMP TABLE mlight_h AS
    SELECT subject_id, CAST(timestamp AS DATE) AS lifelog_date, EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           COUNT(*) AS mlight_n_h, AVG(m_light) AS mlight_mean_h, MAX(m_light) AS mlight_max_h
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mLight.parquet')}') GROUP BY 1,2,3;

    CREATE OR REPLACE TEMP TABLE wlight_h AS
    SELECT subject_id, CAST(timestamp AS DATE) AS lifelog_date, EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           COUNT(*) AS wlight_n_h, AVG(w_light) AS wlight_mean_h, MAX(w_light) AS wlight_max_h
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wLight.parquet')}') GROUP BY 1,2,3;

    CREATE OR REPLACE TEMP TABLE activity_h AS
    SELECT subject_id, CAST(timestamp AS DATE) AS lifelog_date, EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           COUNT(*) AS activity_n_h, AVG(m_activity) AS activity_mean_h
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mActivity.parquet')}') GROUP BY 1,2,3;

    CREATE OR REPLACE TEMP TABLE base AS
    SELECT DISTINCT subject_id, lifelog_date, hour FROM screen_h
    UNION SELECT DISTINCT subject_id, lifelog_date, hour FROM pedo_h
    UNION SELECT DISTINCT subject_id, lifelog_date, hour FROM mlight_h
    UNION SELECT DISTINCT subject_id, lifelog_date, hour FROM wlight_h
    UNION SELECT DISTINCT subject_id, lifelog_date, hour FROM activity_h;

    CREATE OR REPLACE TEMP TABLE joined AS
    SELECT b.subject_id, CAST(b.lifelog_date AS VARCHAR) AS lifelog_date, b.hour,
           screen_h.* EXCLUDE(subject_id, lifelog_date, hour),
           pedo_h.* EXCLUDE(subject_id, lifelog_date, hour),
           mlight_h.* EXCLUDE(subject_id, lifelog_date, hour),
           wlight_h.* EXCLUDE(subject_id, lifelog_date, hour),
           activity_h.* EXCLUDE(subject_id, lifelog_date, hour)
    FROM base b
    LEFT JOIN screen_h USING(subject_id, lifelog_date, hour)
    LEFT JOIN pedo_h USING(subject_id, lifelog_date, hour)
    LEFT JOIN mlight_h USING(subject_id, lifelog_date, hour)
    LEFT JOIN wlight_h USING(subject_id, lifelog_date, hour)
    LEFT JOIN activity_h USING(subject_id, lifelog_date, hour);

    COPY joined TO '{q(out)}' (FORMAT PARQUET);
    """
    con.execute(sql)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{q(out)}')").fetchone()[0]
    cols = len(con.execute(f"DESCRIBE SELECT * FROM read_parquet('{q(out)}')").fetchall())
    print(f"wrote {out} rows={n} cols={cols}")


if __name__ == "__main__":
    main()
