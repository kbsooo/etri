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
    timebin = FEATURE_DIR / "timebin_1h_features.parquet"
    out = FEATURE_DIR / "sleep_proxy_v0.parquet"

    sql = f"""
    CREATE OR REPLACE TEMP TABLE tb AS
    SELECT *,
      CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 5 THEN 1 ELSE 0 END AS is_sleep_window,
      CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN 1 ELSE 0 END AS is_21_03,
      CASE WHEN hour BETWEEN 0 AND 5 THEN 1 ELSE 0 END AS is_00_06
    FROM read_parquet('{q(timebin)}');

    CREATE OR REPLACE TEMP TABLE proxy AS
    SELECT
      subject_id,
      lifelog_date,
      SUM(CASE WHEN is_sleep_window=1 THEN COALESCE(screen_use_sum_h,0) ELSE 0 END) AS sleepwin_screen_sum,
      SUM(CASE WHEN is_sleep_window=1 THEN COALESCE(steps_sum_h,0) ELSE 0 END) AS sleepwin_steps_sum,
      AVG(CASE WHEN is_sleep_window=1 THEN mlight_mean_h ELSE NULL END) AS sleepwin_mlight_mean,
      MAX(CASE WHEN is_sleep_window=1 THEN mlight_max_h ELSE NULL END) AS sleepwin_mlight_max,
      AVG(CASE WHEN is_sleep_window=1 THEN wlight_mean_h ELSE NULL END) AS sleepwin_wlight_mean,
      MAX(CASE WHEN is_sleep_window=1 THEN wlight_max_h ELSE NULL END) AS sleepwin_wlight_max,
      SUM(CASE WHEN is_sleep_window=1 AND COALESCE(screen_use_sum_h,0)=0 AND COALESCE(steps_sum_h,0)=0 THEN 1 ELSE 0 END) AS quiet_hours_screen0_steps0,
      SUM(CASE WHEN is_sleep_window=1 AND COALESCE(screen_use_sum_h,0)>0 THEN 1 ELSE 0 END) AS sleepwin_screen_active_hours,
      SUM(CASE WHEN is_sleep_window=1 AND COALESCE(steps_sum_h,0)>0 THEN 1 ELSE 0 END) AS sleepwin_step_active_hours,
      SUM(CASE WHEN is_21_03=1 THEN COALESCE(screen_use_sum_h,0) ELSE 0 END) AS pre_sleep_screen_sum_21_03,
      SUM(CASE WHEN is_21_03=1 THEN COALESCE(steps_sum_h,0) ELSE 0 END) AS pre_sleep_steps_sum_21_03,
      AVG(CASE WHEN hour BETWEEN 6 AND 11 THEN mlight_mean_h ELSE NULL END) AS morning_mlight_mean,
      AVG(CASE WHEN hour BETWEEN 18 AND 23 THEN mlight_mean_h ELSE NULL END) AS evening_mlight_mean
    FROM tb
    GROUP BY 1,2;

    COPY proxy TO '{q(out)}' (FORMAT PARQUET);
    """
    con.execute(sql)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{q(out)}')").fetchone()[0]
    cols = len(con.execute(f"DESCRIBE SELECT * FROM read_parquet('{q(out)}')").fetchall())
    print(f"wrote {out} rows={n} cols={cols}")


if __name__ == "__main__":
    main()
