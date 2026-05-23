#!/usr/bin/env python3
from __future__ import annotations

import duckdb
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cl_common import FEATURE_DIR, ITEM_DIR, ensure_dirs


def q(path: str) -> str:
    return str(path).replace("'", "''")


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    out = FEATURE_DIR / "daily_window_features.parquet"

    # The feature builder intentionally starts with robust, high-signal sensors.
    # Complex list/struct sensors are added as count/density summaries in later scripts.
    sql = f"""
    CREATE OR REPLACE TEMP TABLE base_dates AS
    SELECT DISTINCT subject_id, CAST(timestamp AS DATE) AS lifelog_date
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mScreenStatus.parquet')}')
    UNION
    SELECT DISTINCT subject_id, CAST(timestamp AS DATE) AS lifelog_date
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wPedo.parquet')}')
    UNION
    SELECT DISTINCT subject_id, CAST(timestamp AS DATE) AS lifelog_date
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mLight.parquet')}')
    UNION
    SELECT DISTINCT subject_id, CAST(timestamp AS DATE) AS lifelog_date
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wLight.parquet')}');

    CREATE OR REPLACE TEMP TABLE screen AS
    SELECT
      subject_id,
      CAST(timestamp AS DATE) AS lifelog_date,
      COUNT(*) AS screen_n,
      AVG(m_screen_use) AS screen_use_mean,
      SUM(m_screen_use) AS screen_use_sum,
      SUM(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN m_screen_use ELSE 0 END) AS screen_use_21_03,
      SUM(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 5 THEN m_screen_use ELSE 0 END) AS screen_use_00_06,
      SUM(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 18 AND 23 THEN m_screen_use ELSE 0 END) AS screen_use_18_24,
      MAX(CASE WHEN m_screen_use > 0 THEN EXTRACT('hour' FROM timestamp) + EXTRACT('minute' FROM timestamp)/60.0 ELSE NULL END) AS last_screen_hour_any,
      MIN(CASE WHEN m_screen_use > 0 THEN EXTRACT('hour' FROM timestamp) + EXTRACT('minute' FROM timestamp)/60.0 ELSE NULL END) AS first_screen_hour_any
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mScreenStatus.parquet')}')
    GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE pedo AS
    SELECT
      subject_id,
      CAST(timestamp AS DATE) AS lifelog_date,
      COUNT(*) AS pedo_n,
      SUM(step) AS steps_sum,
      SUM(distance) AS distance_sum,
      SUM(burned_calories) AS calories_sum,
      AVG(speed) AS speed_mean,
      MAX(speed) AS speed_max,
      SUM(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN step ELSE 0 END) AS steps_21_03,
      SUM(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 5 THEN step ELSE 0 END) AS steps_00_06,
      SUM(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 18 AND 23 THEN step ELSE 0 END) AS steps_18_24
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wPedo.parquet')}')
    GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE mlight AS
    SELECT
      subject_id,
      CAST(timestamp AS DATE) AS lifelog_date,
      COUNT(*) AS mlight_n,
      AVG(m_light) AS mlight_mean,
      MAX(m_light) AS mlight_max,
      AVG(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN m_light ELSE NULL END) AS mlight_mean_21_03,
      MAX(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN m_light ELSE NULL END) AS mlight_max_21_03,
      AVG(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 6 AND 11 THEN m_light ELSE NULL END) AS mlight_mean_morning,
      AVG(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 18 AND 23 THEN m_light ELSE NULL END) AS mlight_mean_evening
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mLight.parquet')}')
    GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE wlight AS
    SELECT
      subject_id,
      CAST(timestamp AS DATE) AS lifelog_date,
      COUNT(*) AS wlight_n,
      AVG(w_light) AS wlight_mean,
      MAX(w_light) AS wlight_max,
      AVG(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN w_light ELSE NULL END) AS wlight_mean_21_03,
      MAX(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN w_light ELSE NULL END) AS wlight_max_21_03,
      AVG(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 6 AND 11 THEN w_light ELSE NULL END) AS wlight_mean_morning,
      AVG(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 18 AND 23 THEN w_light ELSE NULL END) AS wlight_mean_evening
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wLight.parquet')}')
    GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE activity AS
    SELECT
      subject_id,
      CAST(timestamp AS DATE) AS lifelog_date,
      COUNT(*) AS activity_n,
      AVG(m_activity) AS activity_mean,
      SUM(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN m_activity ELSE 0 END) AS activity_sum_21_03
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mActivity.parquet')}')
    GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE ac AS
    SELECT
      subject_id,
      CAST(timestamp AS DATE) AS lifelog_date,
      COUNT(*) AS ac_n,
      AVG(m_charging) AS charging_mean,
      MAX(m_charging) AS charging_any,
      AVG(CASE WHEN EXTRACT('hour' FROM timestamp) BETWEEN 21 AND 23 OR EXTRACT('hour' FROM timestamp) BETWEEN 0 AND 2 THEN m_charging ELSE NULL END) AS charging_mean_21_03
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mACStatus.parquet')}')
    GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE joined AS
    SELECT b.subject_id, CAST(b.lifelog_date AS VARCHAR) AS lifelog_date,
           screen.* EXCLUDE(subject_id, lifelog_date),
           pedo.* EXCLUDE(subject_id, lifelog_date),
           mlight.* EXCLUDE(subject_id, lifelog_date),
           wlight.* EXCLUDE(subject_id, lifelog_date),
           activity.* EXCLUDE(subject_id, lifelog_date),
           ac.* EXCLUDE(subject_id, lifelog_date)
    FROM base_dates b
    LEFT JOIN screen USING(subject_id, lifelog_date)
    LEFT JOIN pedo USING(subject_id, lifelog_date)
    LEFT JOIN mlight USING(subject_id, lifelog_date)
    LEFT JOIN wlight USING(subject_id, lifelog_date)
    LEFT JOIN activity USING(subject_id, lifelog_date)
    LEFT JOIN ac USING(subject_id, lifelog_date);

    COPY joined TO '{q(out)}' (FORMAT PARQUET);
    """
    con.execute(sql)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{q(out)}')").fetchone()[0]
    cols = len(con.execute(f"DESCRIBE SELECT * FROM read_parquet('{q(out)}')").fetchall())
    print(f"wrote {out} rows={n} cols={cols}")


if __name__ == "__main__":
    main()
