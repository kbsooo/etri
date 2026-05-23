#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ITEM_DIR, ensure_dirs


def safe_mean(xs):
    xs = [float(x) for x in xs if pd.notna(x)]
    return float(np.mean(xs)) if xs else np.nan


def safe_std(xs):
    xs = [float(x) for x in xs if pd.notna(x)]
    return float(np.std(xs)) if xs else np.nan


def safe_max(xs):
    xs = [float(x) for x in xs if pd.notna(x)]
    return float(np.max(xs)) if xs else np.nan


def transitions(flags):
    return sum(int(a != b) for a, b in zip(flags, flags[1:]))


def q(path: Path) -> str:
    return str(path).replace("'", "''")


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()

    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv")[["subject_id", "sleep_date", "lifelog_date"]]
    test = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv")[["subject_id", "sleep_date", "lifelog_date"]]
    keys = pd.concat([train, test], ignore_index=True).drop_duplicates()
    keys["lifelog_date"] = pd.to_datetime(keys["lifelog_date"])
    keys["sleep_date"] = pd.to_datetime(keys["sleep_date"])

    # TimesFM-inspired practical abstraction for this tiny-label task:
    # build compact hourly "patch token" channels, then use direct chunk/window
    # summaries and per-series normalization instead of a large supervised Transformer.
    hourly = con.execute(f"""
    WITH screen_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             SUM(m_screen_use)::DOUBLE screen, AVG(m_screen_use)::DOUBLE screen_mean, COUNT(*)::DOUBLE screen_n
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mScreenStatus.parquet')}') GROUP BY 1,2,3
    ), pedo_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             SUM(step)::DOUBLE steps, SUM(distance)::DOUBLE distance, SUM(burned_calories)::DOUBLE calories,
             AVG(speed)::DOUBLE speed, MAX(speed)::DOUBLE speed_max
      FROM read_parquet('{q(ITEM_DIR/'ch2025_wPedo.parquet')}') GROUP BY 1,2,3
    ), mlight_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             AVG(m_light)::DOUBLE mlight, MAX(m_light)::DOUBLE mlight_max
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mLight.parquet')}') GROUP BY 1,2,3
    ), wlight_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             AVG(w_light)::DOUBLE wlight, MAX(w_light)::DOUBLE wlight_max
      FROM read_parquet('{q(ITEM_DIR/'ch2025_wLight.parquet')}') GROUP BY 1,2,3
    ), act_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             AVG(m_activity)::DOUBLE activity, MAX(m_activity)::DOUBLE activity_max
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mActivity.parquet')}') GROUP BY 1,2,3
    ), ac_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             AVG(m_charging)::DOUBLE charging
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mACStatus.parquet')}') GROUP BY 1,2,3
    ), hr_flat AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, x::DOUBLE hr
      FROM read_parquet('{q(ITEM_DIR/'ch2025_wHr.parquet')}'), unnest(heart_rate) AS t(x)
    ), hr_h AS (
      SELECT subject_id,date,hour, AVG(hr)::DOUBLE hr, MAX(hr)::DOUBLE hr_max, MIN(hr)::DOUBLE hr_min,
             STDDEV_POP(hr)::DOUBLE hr_std, quantile_cont(hr,0.9)::DOUBLE hr_p90
      FROM hr_flat GROUP BY 1,2,3
    ), app_flat AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             lower(a.app_name) app_name, a.total_time::DOUBLE total_time
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mUsageStats.parquet')}'), unnest(m_usage_stats) AS t(a)
    ), app_h AS (
      SELECT subject_id,date,hour,
             SUM(total_time)::DOUBLE app_time,
             COUNT(*)::DOUBLE app_records,
             COUNT(DISTINCT app_name)::DOUBLE app_unique,
             MAX(total_time)::DOUBLE app_top_time,
             SUM(CASE WHEN app_name LIKE '%kakao%' OR app_name LIKE '%카카오%' OR app_name LIKE '%instagram%' OR app_name LIKE '%facebook%' OR app_name LIKE '%discord%' OR app_name LIKE '%telegram%' THEN total_time ELSE 0 END)::DOUBLE app_social,
             SUM(CASE WHEN app_name LIKE '%youtube%' OR app_name LIKE '%유튜브%' OR app_name LIKE '%netflix%' OR app_name LIKE '%music%' OR app_name LIKE '%뮤직%' THEN total_time ELSE 0 END)::DOUBLE app_media,
             SUM(CASE WHEN app_name LIKE '%naver%' OR app_name LIKE '%chrome%' OR app_name LIKE '%safari%' OR app_name LIKE '%google%' THEN total_time ELSE 0 END)::DOUBLE app_browser,
             SUM(CASE WHEN app_name LIKE '%game%' OR app_name LIKE '%게임%' THEN total_time ELSE 0 END)::DOUBLE app_game,
             SUM(CASE WHEN app_name LIKE '%study%' OR app_name LIKE '%class%' OR app_name LIKE '%학교%' OR app_name LIKE '%notion%' THEN total_time ELSE 0 END)::DOUBLE app_work
      FROM app_flat GROUP BY 1,2,3
    ), amb_flat AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             lower(a[1]) cls, try_cast(a[2] AS DOUBLE) prob
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mAmbience.parquet')}'), unnest(m_ambience) AS t(a)
    ), amb_h AS (
      SELECT subject_id,date,hour,
             AVG(CASE WHEN cls LIKE '%speech%' THEN prob ELSE 0 END)::DOUBLE amb_speech,
             AVG(CASE WHEN cls LIKE '%music%' THEN prob ELSE 0 END)::DOUBLE amb_music,
             AVG(CASE WHEN cls LIKE '%vehicle%' OR cls LIKE '%car%' OR cls LIKE '%truck%' THEN prob ELSE 0 END)::DOUBLE amb_vehicle,
             AVG(CASE WHEN cls LIKE '%outside%' THEN prob ELSE 0 END)::DOUBLE amb_outside,
             AVG(CASE WHEN cls LIKE '%inside%' THEN prob ELSE 0 END)::DOUBLE amb_inside,
             AVG(CASE WHEN cls LIKE '%silence%' OR cls LIKE '%quiet%' THEN prob ELSE 0 END)::DOUBLE amb_quiet
      FROM amb_flat GROUP BY 1,2,3
    ), gps_flat AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             g.speed::DOUBLE speed, g.latitude::DOUBLE lat, g.longitude::DOUBLE lon
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mGps.parquet')}'), unnest(m_gps) AS t(g)
    ), gps_h AS (
      SELECT subject_id,date,hour, AVG(speed)::DOUBLE gps_speed, MAX(speed)::DOUBLE gps_speed_max,
             SUM(CASE WHEN speed > 0.5 THEN 1 ELSE 0 END)::DOUBLE gps_moving,
             COUNT(DISTINCT ROUND(lat,4) || '_' || ROUND(lon,4))::DOUBLE gps_grid_unique
      FROM gps_flat GROUP BY 1,2,3
    ), wifi_flat AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             w.bssid bssid, w.rssi::DOUBLE rssi
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mWifi.parquet')}'), unnest(m_wifi) AS t(w)
    ), wifi_h AS (
      SELECT subject_id,date,hour, COUNT(*)::DOUBLE wifi_records, COUNT(DISTINCT bssid)::DOUBLE wifi_unique,
             AVG(rssi)::DOUBLE wifi_rssi, MAX(rssi)::DOUBLE wifi_rssi_max
      FROM wifi_flat GROUP BY 1,2,3
    ), ble_flat AS (
      SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             b.address address, b.device_class device_class, b.rssi::DOUBLE rssi
      FROM read_parquet('{q(ITEM_DIR/'ch2025_mBle.parquet')}'), unnest(m_ble) AS t(b)
    ), ble_h AS (
      SELECT subject_id,date,hour, COUNT(*)::DOUBLE ble_records, COUNT(DISTINCT address)::DOUBLE ble_unique,
             SUM(CASE WHEN rssi >= -60 THEN 1 ELSE 0 END)::DOUBLE ble_near,
             AVG(rssi)::DOUBLE ble_rssi, MAX(rssi)::DOUBLE ble_rssi_max
      FROM ble_flat GROUP BY 1,2,3
    ), base AS (
      SELECT subject_id,date,hour FROM screen_h UNION SELECT subject_id,date,hour FROM pedo_h
      UNION SELECT subject_id,date,hour FROM mlight_h UNION SELECT subject_id,date,hour FROM wlight_h
      UNION SELECT subject_id,date,hour FROM act_h UNION SELECT subject_id,date,hour FROM ac_h
      UNION SELECT subject_id,date,hour FROM hr_h UNION SELECT subject_id,date,hour FROM app_h
      UNION SELECT subject_id,date,hour FROM amb_h UNION SELECT subject_id,date,hour FROM gps_h
      UNION SELECT subject_id,date,hour FROM wifi_h UNION SELECT subject_id,date,hour FROM ble_h
    )
    SELECT b.subject_id, CAST(b.date AS VARCHAR) date, b.hour,
           screen_h.* EXCLUDE(subject_id,date,hour), pedo_h.* EXCLUDE(subject_id,date,hour),
           mlight_h.* EXCLUDE(subject_id,date,hour), wlight_h.* EXCLUDE(subject_id,date,hour),
           act_h.* EXCLUDE(subject_id,date,hour), ac_h.* EXCLUDE(subject_id,date,hour),
           hr_h.* EXCLUDE(subject_id,date,hour), app_h.* EXCLUDE(subject_id,date,hour),
           amb_h.* EXCLUDE(subject_id,date,hour), gps_h.* EXCLUDE(subject_id,date,hour),
           wifi_h.* EXCLUDE(subject_id,date,hour), ble_h.* EXCLUDE(subject_id,date,hour)
    FROM base b
    LEFT JOIN screen_h USING(subject_id,date,hour) LEFT JOIN pedo_h USING(subject_id,date,hour)
    LEFT JOIN mlight_h USING(subject_id,date,hour) LEFT JOIN wlight_h USING(subject_id,date,hour)
    LEFT JOIN act_h USING(subject_id,date,hour) LEFT JOIN ac_h USING(subject_id,date,hour)
    LEFT JOIN hr_h USING(subject_id,date,hour) LEFT JOIN app_h USING(subject_id,date,hour)
    LEFT JOIN amb_h USING(subject_id,date,hour) LEFT JOIN gps_h USING(subject_id,date,hour)
    LEFT JOIN wifi_h USING(subject_id,date,hour) LEFT JOIN ble_h USING(subject_id,date,hour)
    """).df()
    hourly["date"] = pd.to_datetime(hourly["date"])
    for c in hourly.columns:
        if c not in ["subject_id", "date", "hour"]:
            hourly[c] = pd.to_numeric(hourly[c], errors="coerce").fillna(0.0)

    idx = {(r.subject_id, r.date.date(), int(r.hour)): r for r in hourly.itertuples(index=False)}
    subj_stats = hourly.groupby("subject_id").agg(
        subj_hr_mean=("hr", "mean"), subj_hr_std=("hr", "std"), subj_screen_mean=("screen", "mean"),
        subj_app_mean=("app_time", "mean"), subj_steps_mean=("steps", "mean"), subj_amb_speech=("amb_speech", "mean"),
        subj_amb_music=("amb_music", "mean"), subj_gps_moving=("gps_moving", "mean")
    ).fillna(0.0)

    vars_for_patch = ["hr", "hr_max", "hr_std", "screen", "steps", "activity", "mlight", "wlight", "charging", "app_time", "app_social", "app_media", "app_browser", "amb_speech", "amb_music", "amb_vehicle", "amb_outside", "gps_moving", "wifi_unique", "ble_near"]

    def get(sid, date, hour):
        return idx.get((sid, date, hour))

    def val(r, name, default=0.0):
        if r is None:
            return default
        x = getattr(r, name)
        return float(x) if pd.notna(x) else default

    def rows_for(sid, date, hours):
        return [get(sid, date, h) for h in hours]

    def agg(rs, prefix):
        hs = [r for r in rs if r is not None]
        out = {}
        for c in ["hr", "hr_max", "hr_std", "screen", "steps", "calories", "distance", "speed", "activity", "mlight", "wlight", "charging", "app_time", "app_social", "app_media", "app_browser", "app_game", "app_work", "amb_speech", "amb_music", "amb_vehicle", "amb_outside", "amb_inside", "amb_quiet", "gps_speed", "gps_moving", "wifi_unique", "ble_unique", "ble_near"]:
            xs = [val(r, c, np.nan if c.startswith('hr') else 0.0) for r in hs]
            out[f"{prefix}_{c}_mean"] = safe_mean(xs)
            out[f"{prefix}_{c}_sum"] = float(np.nansum(xs)) if xs else 0.0
            out[f"{prefix}_{c}_max"] = safe_max(xs)
        out[f"{prefix}_screen_active_hours"] = sum(val(r, "screen") > 0 for r in hs)
        out[f"{prefix}_active_hours"] = sum((val(r, "steps") > 20) or (val(r, "activity") > 1.2) for r in hs)
        out[f"{prefix}_social_audio_hours"] = sum((val(r, "amb_speech") + val(r, "amb_music") > 0.05) for r in hs)
        out[f"{prefix}_mobility_hours"] = sum((val(r, "gps_moving") > 0) or (val(r, "steps") > 50) for r in hs)
        return out

    rows = []
    for rec in keys.itertuples(index=False):
        sid = rec.subject_id
        d = rec.lifelog_date.date()
        sd = rec.sleep_date.date()
        sb = subj_stats.loc[sid] if sid in subj_stats.index else pd.Series(dtype=float)
        row = {"subject_id": sid, "lifelog_date": str(d)}

        day = rows_for(sid, d, range(6, 18))
        eve = rows_for(sid, d, range(18, 21))
        late = rows_for(sid, d, range(21, 24))
        after_mid = rows_for(sid, sd, range(0, 4))
        morning = rows_for(sid, sd, range(5, 12))
        qlate = late + after_mid
        full = day + eve + qlate + morning

        row.update(agg(day, "q3x_day"))
        row.update(agg(eve, "q3x_evening"))
        row.update(agg(late, "q3x_late21_24"))
        row.update(agg(qlate, "q3x_late21_04"))
        row.update(agg(morning, "q1x_morning"))

        day_hr = row["q3x_day_hr_mean"]
        late_hr = row["q3x_late21_04_hr_mean"]
        subj_hr = float(sb.get("subj_hr_mean", 0.0))
        subj_hr_std = float(sb.get("subj_hr_std", 0.0)) or 1.0
        row["q3x_late_hr_minus_day"] = late_hr - day_hr if pd.notna(late_hr) and pd.notna(day_hr) else np.nan
        row["q3x_late_hr_z_subj"] = (late_hr - subj_hr) / subj_hr_std if pd.notna(late_hr) else np.nan
        row["q3x_evening_hr_minus_day"] = row["q3x_evening_hr_mean"] - day_hr if pd.notna(row["q3x_evening_hr_mean"]) and pd.notna(day_hr) else np.nan
        row["q3x_late_hrmax_minus_day"] = row["q3x_late21_04_hr_max_max"] - row["q3x_day_hr_max_max"] if pd.notna(row["q3x_late21_04_hr_max_max"]) else np.nan
        row["q3x_late_lowmove_highhr"] = max(row.get("q3x_late_hr_z_subj", 0) if pd.notna(row.get("q3x_late_hr_z_subj")) else 0, 0) * math.log1p(row["q3x_late21_04_screen_sum"]) / math.log1p(row["q3x_late21_04_steps_sum"] + 1)
        row["q3x_social_arousal_score"] = math.log1p(row["q3x_late21_04_app_social_sum"] + row["q3x_late21_04_app_media_sum"] + row["q3x_late21_04_app_browser_sum"]) * (1 + max(row.get("q3x_late_hr_z_subj", 0) if pd.notna(row.get("q3x_late_hr_z_subj")) else 0, 0))
        row["q3x_audio_context_score"] = row["q3x_late21_04_amb_speech_mean"] + row["q3x_late21_04_amb_music_mean"] + row["q3x_late21_04_amb_vehicle_mean"] + row["q3x_late21_04_amb_outside_mean"]
        row["q3x_screen_in_dark_score"] = math.log1p(row["q3x_late21_04_screen_sum"]) * math.log1p(row["q3x_late21_04_mlight_max"] + row["q3x_late21_04_wlight_max"])
        row["q3x_day_overstim_to_late_arousal"] = (math.log1p(row["q3x_day_app_time_sum"] + row["q3x_day_amb_speech_sum"]*100 + row["q3x_day_amb_music_sum"]*100) * (1 + max(row.get("q3x_late_hr_z_subj", 0) if pd.notna(row.get("q3x_late_hr_z_subj")) else 0, 0)))

        # Hourly patch/channel summaries: direct chunky windows + normalized late-vs-day distances.
        patch_hours = [(d,h) for h in range(6,24)] + [(sd,h) for h in range(0,4)]
        token_vectors = []
        for rel, (date, h) in enumerate(patch_hours):
            r = get(sid, date, h)
            vec = np.array([val(r, c, np.nan if c.startswith('hr') else 0.0) for c in vars_for_patch], dtype=float)
            token_vectors.append(vec)
            for c, x in zip(vars_for_patch, vec):
                if False:  # raw hourly patch values were too wide/noisy; keep only normalized patch summaries below.
                    row[f"qpatch_h{rel}_{c}"] = float(0.0 if pd.isna(x) else x)
        mat = np.vstack(token_vectors)
        day_mat = mat[:12]
        late_mat = mat[15:]  # 21-03 chunk
        mu = np.nanmean(day_mat, axis=0)
        sig = np.nanstd(day_mat, axis=0); sig[sig == 0] = 1.0
        zlate = (late_mat - mu) / sig
        for i, c in enumerate(vars_for_patch):
            row[f"qpatch_late_{c}_zmean"] = float(np.nanmean(zlate[:, i]))
            row[f"qpatch_late_{c}_zmax"] = float(np.nanmax(zlate[:, i]))
            row[f"qpatch_late_{c}_slope"] = float(np.nan_to_num(late_mat[-1, i]) - np.nan_to_num(late_mat[0, i]))
        row["qpatch_late_vector_dist_mean"] = float(np.nanmean(np.sqrt(np.nansum(np.nan_to_num(zlate) ** 2, axis=1))))
        row["qpatch_late_vector_dist_max"] = float(np.nanmax(np.sqrt(np.nansum(np.nan_to_num(zlate) ** 2, axis=1))))
        screen_flags = [v > 0 for v in mat[:, vars_for_patch.index("screen")]]
        active_flags = [(mat[i, vars_for_patch.index("steps")] > 20) or (mat[i, vars_for_patch.index("activity")] > 1.2) for i in range(mat.shape[0])]
        social_flags = [(mat[i, vars_for_patch.index("app_social")] + mat[i, vars_for_patch.index("amb_speech")] + mat[i, vars_for_patch.index("amb_music")]) > 0.05 for i in range(mat.shape[0])]
        row["qpatch_screen_transitions"] = transitions(screen_flags)
        row["qpatch_active_transitions"] = transitions(active_flags)
        row["qpatch_social_audio_transitions"] = transitions(social_flags)
        row["qpatch_late_screen_transitions"] = transitions(screen_flags[15:])
        row["qpatch_late_active_transitions"] = transitions(active_flags[15:])

        # Q1 subjective sleep-quality proxies: sleep carry-over plus post-wake recovery.
        row["q1x_morning_hr_minus_late_hr"] = row["q1x_morning_hr_mean"] - late_hr if pd.notna(row["q1x_morning_hr_mean"]) and pd.notna(late_hr) else np.nan
        row["q1x_morning_hr_z_subj"] = (row["q1x_morning_hr_mean"] - subj_hr) / subj_hr_std if pd.notna(row["q1x_morning_hr_mean"]) else np.nan
        row["q1x_morning_screen_after_badnight"] = math.log1p(row["q1x_morning_screen_sum"]) * (1 + max(row.get("q3x_late_hr_z_subj", 0) if pd.notna(row.get("q3x_late_hr_z_subj")) else 0, 0))
        row["q1x_recovery_failure_score"] = (row["q1x_morning_hr_z_subj"] if pd.notna(row["q1x_morning_hr_z_subj"]) else 0) + 0.05 * row["q1x_morning_active_hours"] + 0.001 * row["q1x_morning_screen_sum"]

        rows.append(row)

    out = pd.DataFrame(rows).sort_values(["subject_id", "lifelog_date"])

    # Keep compact, mechanism-shaped columns. The full aggregate expansion is noisy and
    # also makes model_features_v0 subject-normalization very wide.
    keep = ["subject_id", "lifelog_date"]
    selected_suffixes = (
        "_hr_mean", "_hr_max", "_hr_std_mean", "_screen_sum", "_steps_sum", "_activity_mean",
        "_mlight_max", "_wlight_max", "_app_time_sum", "_app_social_sum", "_app_media_sum",
        "_app_browser_sum", "_app_game_sum", "_app_work_sum", "_amb_speech_mean", "_amb_music_mean",
        "_amb_vehicle_mean", "_amb_outside_mean", "_amb_inside_mean", "_amb_quiet_mean",
        "_gps_moving_sum", "_gps_speed_mean", "_wifi_unique_sum", "_ble_near_sum",
        "_screen_active_hours", "_active_hours", "_social_audio_hours", "_mobility_hours",
    )
    engineered_names = {
        "q3x_late_hr_minus_day", "q3x_late_hr_z_subj", "q3x_evening_hr_minus_day",
        "q3x_late_hrmax_minus_day", "q3x_late_lowmove_highhr", "q3x_social_arousal_score",
        "q3x_audio_context_score", "q3x_screen_in_dark_score", "q3x_day_overstim_to_late_arousal",
        "q1x_morning_hr_minus_late_hr", "q1x_morning_hr_z_subj", "q1x_morning_screen_after_badnight",
        "q1x_recovery_failure_score", "qpatch_late_vector_dist_mean", "qpatch_late_vector_dist_max",
        "qpatch_screen_transitions", "qpatch_active_transitions", "qpatch_social_audio_transitions",
        "qpatch_late_screen_transitions", "qpatch_late_active_transitions",
    }
    for c in out.columns:
        if c in keep:
            continue
        if c in engineered_names or c.startswith("qpatch_late_") or c.endswith(selected_suffixes):
            keep.append(c)
    out = out.loc[:, keep].copy()

    # Previous subjective-state carry-over for only the compact engineered columns.
    lag_cols = [c for c in out.columns if c in engineered_names or c in {"qpatch_late_vector_dist_mean", "qpatch_late_vector_dist_max"}]
    for c in lag_cols:
        out[f"qcarry_prev_{c}"] = out.groupby("subject_id")[c].shift(1)

    path = FEATURE_DIR / "stress_arousal_q_features_v1.parquet"
    con.register("outdf", out)
    con.execute(f"COPY outdf TO '{q(path)}' (FORMAT PARQUET)")
    print(f"wrote {path} rows={len(out)} cols={out.shape[1]}")


if __name__ == "__main__":
    main()
