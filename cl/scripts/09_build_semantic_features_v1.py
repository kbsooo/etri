#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ITEM_DIR, ensure_dirs


def q(path) -> str:
    return str(path).replace("'", "''")


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    out = FEATURE_DIR / "semantic_features_v1.parquet"
    sql = f"""
    CREATE OR REPLACE TEMP TABLE hr_flat AS
    SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS lifelog_date,
           EXTRACT('hour' FROM timestamp)::INTEGER AS hour, x::DOUBLE AS hr
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_wHr.parquet')}'), unnest(heart_rate) AS t(x);

    CREATE OR REPLACE TEMP TABLE hr AS
    SELECT subject_id, CAST(lifelog_date AS VARCHAR) AS lifelog_date,
           COUNT(*) AS hr_count,
           AVG(hr) AS hr_mean,
           STDDEV_POP(hr) AS hr_std,
           MIN(hr) AS hr_min,
           MAX(hr) AS hr_max,
           quantile_cont(hr, 0.1) AS hr_p10,
           quantile_cont(hr, 0.5) AS hr_p50,
           quantile_cont(hr, 0.9) AS hr_p90,
           AVG(CASE WHEN hour BETWEEN 0 AND 5 THEN hr ELSE NULL END) AS hr_mean_00_06,
           MIN(CASE WHEN hour BETWEEN 0 AND 5 THEN hr ELSE NULL END) AS hr_min_00_06,
           STDDEV_POP(CASE WHEN hour BETWEEN 0 AND 5 THEN hr ELSE NULL END) AS hr_std_00_06,
           AVG(CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN hr ELSE NULL END) AS hr_mean_21_03,
           AVG(CASE WHEN hour BETWEEN 6 AND 17 THEN hr ELSE NULL END) AS hr_mean_day
    FROM hr_flat GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE gps_flat AS
    SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS lifelog_date,
           EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           g.latitude::DOUBLE AS lat, g.longitude::DOUBLE AS lon, g.altitude::DOUBLE AS alt, g.speed::DOUBLE AS speed
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mGps.parquet')}'), unnest(m_gps) AS t(g);

    CREATE OR REPLACE TEMP TABLE gps AS
    SELECT subject_id, CAST(lifelog_date AS VARCHAR) AS lifelog_date,
           COUNT(*) AS gps_count,
           AVG(speed) AS gps_speed_mean,
           MAX(speed) AS gps_speed_max,
           STDDEV_POP(speed) AS gps_speed_std,
           AVG(CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN speed ELSE NULL END) AS gps_speed_21_03,
           SUM(CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 AND speed > 0.5 THEN 1 ELSE 0 END) AS gps_moving_count_21_03,
           STDDEV_POP(lat) AS gps_lat_std,
           STDDEV_POP(lon) AS gps_lon_std,
           (STDDEV_POP(lat) + STDDEV_POP(lon)) AS gps_radius_proxy,
           COUNT(DISTINCT ROUND(lat, 4) || '_' || ROUND(lon, 4)) AS gps_unique_grid4
    FROM gps_flat GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE app_flat AS
    SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS lifelog_date,
           EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           lower(a.app_name) AS app_name, a.total_time::DOUBLE AS total_time
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mUsageStats.parquet')}'), unnest(m_usage_stats) AS t(a);

    CREATE OR REPLACE TEMP TABLE app AS
    SELECT subject_id, CAST(lifelog_date AS VARCHAR) AS lifelog_date,
           COUNT(*) AS app_records,
           COUNT(DISTINCT app_name) AS app_unique_count,
           SUM(total_time) AS app_total_time,
           MAX(total_time) AS app_top_time,
           MAX(total_time) / NULLIF(SUM(total_time), 0) AS app_top_share,
           SUM(CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN total_time ELSE 0 END) AS app_time_21_03,
           SUM(CASE WHEN app_name LIKE '%kakao%' OR app_name LIKE '%카카오%' OR app_name LIKE '%instagram%' OR app_name LIKE '%facebook%' OR app_name LIKE '%discord%' OR app_name LIKE '%telegram%' THEN total_time ELSE 0 END) AS app_social_time,
           SUM(CASE WHEN app_name LIKE '%youtube%' OR app_name LIKE '%유튜브%' OR app_name LIKE '%netflix%' OR app_name LIKE '%music%' OR app_name LIKE '%뮤직%' THEN total_time ELSE 0 END) AS app_media_time,
           SUM(CASE WHEN app_name LIKE '%naver%' OR app_name LIKE '%chrome%' OR app_name LIKE '%safari%' OR app_name LIKE '%google%' THEN total_time ELSE 0 END) AS app_browser_search_time,
           SUM(CASE WHEN app_name LIKE '%game%' OR app_name LIKE '%게임%' THEN total_time ELSE 0 END) AS app_game_time,
           SUM(CASE WHEN app_name LIKE '%study%' OR app_name LIKE '%class%' OR app_name LIKE '%학교%' OR app_name LIKE '%notion%' THEN total_time ELSE 0 END) AS app_study_work_time
    FROM app_flat GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE wifi_flat AS
    SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS lifelog_date,
           EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           w.bssid AS bssid, w.rssi::DOUBLE AS rssi
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mWifi.parquet')}'), unnest(m_wifi) AS t(w);

    CREATE OR REPLACE TEMP TABLE wifi AS
    SELECT subject_id, CAST(lifelog_date AS VARCHAR) AS lifelog_date,
           COUNT(*) AS wifi_records,
           COUNT(DISTINCT bssid) AS wifi_unique_bssid,
           AVG(rssi) AS wifi_rssi_mean,
           MAX(rssi) AS wifi_rssi_max,
           SUM(CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN 1 ELSE 0 END) AS wifi_records_21_03,
           COUNT(DISTINCT CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN bssid ELSE NULL END) AS wifi_unique_21_03
    FROM wifi_flat GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE ble_flat AS
    SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS lifelog_date,
           EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           b.address AS address, b.device_class AS device_class, b.rssi::DOUBLE AS rssi
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mBle.parquet')}'), unnest(m_ble) AS t(b);

    CREATE OR REPLACE TEMP TABLE ble AS
    SELECT subject_id, CAST(lifelog_date AS VARCHAR) AS lifelog_date,
           COUNT(*) AS ble_records,
           COUNT(DISTINCT address) AS ble_unique_addr,
           AVG(rssi) AS ble_rssi_mean,
           MAX(rssi) AS ble_rssi_max,
           SUM(CASE WHEN rssi >= -60 THEN 1 ELSE 0 END) AS ble_near_count,
           SUM(CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN 1 ELSE 0 END) AS ble_records_21_03,
           COUNT(DISTINCT CASE WHEN hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2 THEN address ELSE NULL END) AS ble_unique_21_03
    FROM ble_flat GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE amb_flat AS
    SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS lifelog_date,
           EXTRACT('hour' FROM timestamp)::INTEGER AS hour,
           lower(a[1]) AS cls, try_cast(a[2] AS DOUBLE) AS prob
    FROM read_parquet('{q(ITEM_DIR / 'ch2025_mAmbience.parquet')}'), unnest(m_ambience) AS t(a);

    CREATE OR REPLACE TEMP TABLE amb AS
    SELECT subject_id, CAST(lifelog_date AS VARCHAR) AS lifelog_date,
           COUNT(*) AS amb_records,
           AVG(CASE WHEN cls LIKE '%speech%' THEN prob ELSE 0 END) AS amb_speech_prob,
           AVG(CASE WHEN cls LIKE '%music%' THEN prob ELSE 0 END) AS amb_music_prob,
           AVG(CASE WHEN cls LIKE '%vehicle%' OR cls LIKE '%car%' OR cls LIKE '%truck%' THEN prob ELSE 0 END) AS amb_vehicle_prob,
           AVG(CASE WHEN cls LIKE '%outside%' THEN prob ELSE 0 END) AS amb_outside_prob,
           AVG(CASE WHEN cls LIKE '%inside%' THEN prob ELSE 0 END) AS amb_inside_prob,
           AVG(CASE WHEN (hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2) AND cls LIKE '%speech%' THEN prob ELSE 0 END) AS amb_speech_prob_21_03,
           AVG(CASE WHEN (hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2) AND cls LIKE '%music%' THEN prob ELSE 0 END) AS amb_music_prob_21_03,
           AVG(CASE WHEN (hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2) AND (cls LIKE '%vehicle%' OR cls LIKE '%car%' OR cls LIKE '%truck%') THEN prob ELSE 0 END) AS amb_vehicle_prob_21_03,
           AVG(CASE WHEN (hour BETWEEN 21 AND 23 OR hour BETWEEN 0 AND 2) AND cls LIKE '%outside%' THEN prob ELSE 0 END) AS amb_outside_prob_21_03
    FROM amb_flat GROUP BY 1,2;

    CREATE OR REPLACE TEMP TABLE dates AS
    SELECT subject_id, lifelog_date FROM read_parquet('{q(FEATURE_DIR / 'daily_window_features.parquet')}');

    CREATE OR REPLACE TEMP TABLE joined AS
    SELECT d.subject_id, d.lifelog_date,
           hr.* EXCLUDE(subject_id, lifelog_date), gps.* EXCLUDE(subject_id, lifelog_date),
           app.* EXCLUDE(subject_id, lifelog_date), wifi.* EXCLUDE(subject_id, lifelog_date),
           ble.* EXCLUDE(subject_id, lifelog_date), amb.* EXCLUDE(subject_id, lifelog_date)
    FROM dates d
    LEFT JOIN hr USING(subject_id, lifelog_date)
    LEFT JOIN gps USING(subject_id, lifelog_date)
    LEFT JOIN app USING(subject_id, lifelog_date)
    LEFT JOIN wifi USING(subject_id, lifelog_date)
    LEFT JOIN ble USING(subject_id, lifelog_date)
    LEFT JOIN amb USING(subject_id, lifelog_date);

    COPY joined TO '{q(out)}' (FORMAT PARQUET);
    """
    con.execute(sql)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{q(out)}')").fetchone()[0]
    c = len(con.execute(f"DESCRIBE SELECT * FROM read_parquet('{q(out)}')").fetchall())
    print(f"wrote {out} rows={n} cols={c}")


if __name__ == "__main__":
    main()
