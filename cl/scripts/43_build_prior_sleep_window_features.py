#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ITEM_DIR, LABELS, ensure_dirs


def q(p: Path | str) -> str:
    return str(p).replace("'", "''")


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    out = FEATURE_DIR / 'prior_sleep_window_features_v1.parquet'
    train = DATA_DIR / 'ch2026_metrics_train.csv'
    sample = DATA_DIR / 'ch2026_submission_sample.csv'
    sql = f"""
    CREATE OR REPLACE TEMP TABLE meta AS
    SELECT subject_id, CAST(sleep_date AS DATE) AS sleep_date, CAST(lifelog_date AS DATE) AS lifelog_date, 1 AS is_train
    FROM read_csv_auto('{q(train)}')
    UNION ALL
    SELECT subject_id, CAST(sleep_date AS DATE) AS sleep_date, CAST(lifelog_date AS DATE) AS lifelog_date, 0 AS is_train
    FROM read_csv_auto('{q(sample)}');

    CREATE OR REPLACE TEMP TABLE win AS
    SELECT * FROM (VALUES
      ('sw_evening', 18, 24),
      ('sw_presleep', 21, 27),
      ('sw_overnight', 24, 32),
      ('sw_morning', 30, 36),
      ('sw_fullctx', 18, 36)
    ) AS t(win_name, start_h, end_h);

    CREATE OR REPLACE TEMP TABLE rowwin AS
    SELECT m.subject_id, m.sleep_date, m.lifelog_date, m.is_train, w.win_name,
           m.lifelog_date::TIMESTAMP + w.start_h * INTERVAL '1 hour' AS ts_start,
           m.lifelog_date::TIMESTAMP + w.end_h * INTERVAL '1 hour' AS ts_end
    FROM meta m CROSS JOIN win w;

    CREATE OR REPLACE TEMP TABLE hr_min AS
    SELECT subject_id, timestamp,
           list_avg(heart_rate) AS heart_rate_mean_min,
           list_stddev_pop(heart_rate) AS heart_rate_std_min,
           list_min(heart_rate) AS heart_rate_min_min,
           list_max(heart_rate) AS heart_rate_max_min
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wHr.parquet')}');

    CREATE OR REPLACE TEMP TABLE pedo AS
    SELECT r.subject_id, r.sleep_date, r.lifelog_date, r.win_name,
           count(p.timestamp) AS pedo_n,
           sum(p.step) AS pedo_step_sum,
           avg(p.step) AS pedo_step_mean,
           max(p.step) AS pedo_step_max,
           sum(p.walking_step) AS pedo_walking_sum,
           sum(p.running_step) AS pedo_running_sum,
           sum(p.distance) AS pedo_distance_sum,
           avg(p.speed) AS pedo_speed_mean,
           max(p.speed) AS pedo_speed_max,
           sum(p.burned_calories) AS pedo_calories_sum
    FROM rowwin r LEFT JOIN read_parquet('{q(ITEM_DIR / 'ch2025_wPedo.parquet')}') p
      ON r.subject_id=p.subject_id AND p.timestamp >= r.ts_start AND p.timestamp < r.ts_end
    GROUP BY 1,2,3,4;

    CREATE OR REPLACE TEMP TABLE screen AS
    SELECT r.subject_id, r.sleep_date, r.lifelog_date, r.win_name,
           count(s.timestamp) AS screen_n,
           sum(s.m_screen_use) AS screen_use_sum,
           avg(s.m_screen_use) AS screen_use_mean,
           max(s.m_screen_use) AS screen_use_max
    FROM rowwin r LEFT JOIN read_parquet('{q(ITEM_DIR / 'ch2025_mScreenStatus.parquet')}') s
      ON r.subject_id=s.subject_id AND s.timestamp >= r.ts_start AND s.timestamp < r.ts_end
    GROUP BY 1,2,3,4;

    CREATE OR REPLACE TEMP TABLE activity AS
    SELECT r.subject_id, r.sleep_date, r.lifelog_date, r.win_name,
           count(a.timestamp) AS act_n,
           avg(a.m_activity) AS act_mean,
           max(a.m_activity) AS act_max,
           sum(CASE WHEN a.m_activity=0 THEN 1 ELSE 0 END) AS act_zero_n,
           sum(CASE WHEN a.m_activity<>0 THEN 1 ELSE 0 END) AS act_nonzero_n
    FROM rowwin r LEFT JOIN read_parquet('{q(ITEM_DIR / 'ch2025_mActivity.parquet')}') a
      ON r.subject_id=a.subject_id AND a.timestamp >= r.ts_start AND a.timestamp < r.ts_end
    GROUP BY 1,2,3,4;

    CREATE OR REPLACE TEMP TABLE ac AS
    SELECT r.subject_id, r.sleep_date, r.lifelog_date, r.win_name,
           count(c.timestamp) AS charge_n,
           avg(c.m_charging) AS charge_mean,
           max(c.m_charging) AS charge_any,
           sum(c.m_charging) AS charge_sum
    FROM rowwin r LEFT JOIN read_parquet('{q(ITEM_DIR / 'ch2025_mACStatus.parquet')}') c
      ON r.subject_id=c.subject_id AND c.timestamp >= r.ts_start AND c.timestamp < r.ts_end
    GROUP BY 1,2,3,4;

    CREATE OR REPLACE TEMP TABLE mlight AS
    SELECT r.subject_id, r.sleep_date, r.lifelog_date, r.win_name,
           count(l.timestamp) AS mlight_n,
           avg(l.m_light) AS mlight_mean,
           stddev_pop(l.m_light) AS mlight_std,
           max(l.m_light) AS mlight_max,
           quantile_cont(l.m_light, 0.25) AS mlight_q25,
           quantile_cont(l.m_light, 0.75) AS mlight_q75
    FROM rowwin r LEFT JOIN read_parquet('{q(ITEM_DIR / 'ch2025_mLight.parquet')}') l
      ON r.subject_id=l.subject_id AND l.timestamp >= r.ts_start AND l.timestamp < r.ts_end
    GROUP BY 1,2,3,4;

    CREATE OR REPLACE TEMP TABLE wlight AS
    SELECT r.subject_id, r.sleep_date, r.lifelog_date, r.win_name,
           count(l.timestamp) AS wlight_n,
           avg(l.w_light) AS wlight_mean,
           stddev_pop(l.w_light) AS wlight_std,
           max(l.w_light) AS wlight_max,
           quantile_cont(l.w_light, 0.25) AS wlight_q25,
           quantile_cont(l.w_light, 0.75) AS wlight_q75
    FROM rowwin r LEFT JOIN read_parquet('{q(ITEM_DIR / 'ch2025_wLight.parquet')}') l
      ON r.subject_id=l.subject_id AND l.timestamp >= r.ts_start AND l.timestamp < r.ts_end
    GROUP BY 1,2,3,4;

    CREATE OR REPLACE TEMP TABLE hr AS
    SELECT r.subject_id, r.sleep_date, r.lifelog_date, r.win_name,
           count(h.timestamp) AS hr_n,
           avg(h.heart_rate_mean_min) AS hr_mean,
           stddev_pop(h.heart_rate_mean_min) AS hr_std,
           min(h.heart_rate_min_min) AS hr_min,
           max(h.heart_rate_max_min) AS hr_max,
           avg(h.heart_rate_std_min) AS hr_within_min_std_mean
    FROM rowwin r LEFT JOIN hr_min h
      ON r.subject_id=h.subject_id AND h.timestamp >= r.ts_start AND h.timestamp < r.ts_end
    GROUP BY 1,2,3,4;

    CREATE OR REPLACE TEMP TABLE long AS
    SELECT p.subject_id, p.sleep_date, p.lifelog_date, p.win_name,
           p.* EXCLUDE(subject_id, sleep_date, lifelog_date, win_name),
           s.* EXCLUDE(subject_id, sleep_date, lifelog_date, win_name),
           a.* EXCLUDE(subject_id, sleep_date, lifelog_date, win_name),
           c.* EXCLUDE(subject_id, sleep_date, lifelog_date, win_name),
           ml.* EXCLUDE(subject_id, sleep_date, lifelog_date, win_name),
           wl.* EXCLUDE(subject_id, sleep_date, lifelog_date, win_name),
           h.* EXCLUDE(subject_id, sleep_date, lifelog_date, win_name)
    FROM pedo p
    LEFT JOIN screen s USING(subject_id, sleep_date, lifelog_date, win_name)
    LEFT JOIN activity a USING(subject_id, sleep_date, lifelog_date, win_name)
    LEFT JOIN ac c USING(subject_id, sleep_date, lifelog_date, win_name)
    LEFT JOIN mlight ml USING(subject_id, sleep_date, lifelog_date, win_name)
    LEFT JOIN wlight wl USING(subject_id, sleep_date, lifelog_date, win_name)
    LEFT JOIN hr h USING(subject_id, sleep_date, lifelog_date, win_name);

    CREATE OR REPLACE TEMP TABLE wide AS
    PIVOT long ON win_name USING
      first(pedo_n) AS pedo_n,
      first(pedo_step_sum) AS pedo_step_sum,
      first(pedo_step_mean) AS pedo_step_mean,
      first(pedo_step_max) AS pedo_step_max,
      first(pedo_walking_sum) AS pedo_walking_sum,
      first(pedo_running_sum) AS pedo_running_sum,
      first(pedo_distance_sum) AS pedo_distance_sum,
      first(pedo_speed_mean) AS pedo_speed_mean,
      first(pedo_speed_max) AS pedo_speed_max,
      first(pedo_calories_sum) AS pedo_calories_sum,
      first(screen_n) AS screen_n,
      first(screen_use_sum) AS screen_use_sum,
      first(screen_use_mean) AS screen_use_mean,
      first(screen_use_max) AS screen_use_max,
      first(act_n) AS act_n,
      first(act_mean) AS act_mean,
      first(act_max) AS act_max,
      first(act_zero_n) AS act_zero_n,
      first(act_nonzero_n) AS act_nonzero_n,
      first(charge_n) AS charge_n,
      first(charge_mean) AS charge_mean,
      first(charge_any) AS charge_any,
      first(charge_sum) AS charge_sum,
      first(mlight_n) AS mlight_n,
      first(mlight_mean) AS mlight_mean,
      first(mlight_std) AS mlight_std,
      first(mlight_max) AS mlight_max,
      first(mlight_q25) AS mlight_q25,
      first(mlight_q75) AS mlight_q75,
      first(wlight_n) AS wlight_n,
      first(wlight_mean) AS wlight_mean,
      first(wlight_std) AS wlight_std,
      first(wlight_max) AS wlight_max,
      first(wlight_q25) AS wlight_q25,
      first(wlight_q75) AS wlight_q75,
      first(hr_n) AS hr_n,
      first(hr_mean) AS hr_mean,
      first(hr_std) AS hr_std,
      first(hr_min) AS hr_min,
      first(hr_max) AS hr_max,
      first(hr_within_min_std_mean) AS hr_within_min_std_mean;

    CREATE OR REPLACE TEMP TABLE feat AS
    SELECT subject_id, CAST(sleep_date AS VARCHAR) AS sleep_date, CAST(lifelog_date AS VARCHAR) AS lifelog_date,
           * EXCLUDE(subject_id, sleep_date, lifelog_date)
    FROM wide;

    COPY feat TO '{q(out)}' (FORMAT PARQUET);
    """
    con.execute(sql)
    df = con.execute(f"SELECT * FROM read_parquet('{q(out)}')").df()
    # Prefix any feature columns missed by pivot naming convention.
    rename = {c: 'psw_' + c for c in df.columns if c not in ('subject_id','sleep_date','lifelog_date') and not c.startswith('psw_')}
    if rename:
        df = df.rename(columns=rename)
        df.to_parquet(out, index=False)
    print(f"wrote {out} rows={len(df)} cols={len(df.columns)}")


if __name__ == '__main__':
    main()
