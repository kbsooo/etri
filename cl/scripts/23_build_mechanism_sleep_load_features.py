#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from collections import defaultdict
import math

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ITEM_DIR, ensure_dirs


def longest_true_run(flags):
    best = (0, -1, -1); cur_len = 0; cur_start = -1
    for i, f in enumerate(flags):
        if f:
            if cur_len == 0: cur_start = i
            cur_len += 1
            if cur_len > best[0]: best = (cur_len, cur_start, i)
        else:
            cur_len = 0
    return best


def transitions(flags):
    return sum(int(a != b) for a, b in zip(flags, flags[1:]))


def safe_mean(xs):
    xs = [x for x in xs if pd.notna(x)]
    return float(np.mean(xs)) if xs else np.nan


def main():
    ensure_dirs()
    con = duckdb.connect()
    train = pd.read_csv(DATA_DIR / 'ch2026_metrics_train.csv')[['subject_id','sleep_date','lifelog_date']]
    test = pd.read_csv(DATA_DIR / 'ch2026_submission_sample.csv')[['subject_id','sleep_date','lifelog_date']]
    keys = pd.concat([train, test], ignore_index=True).drop_duplicates()
    keys['lifelog_date'] = pd.to_datetime(keys['lifelog_date'])
    keys['sleep_date'] = pd.to_datetime(keys['sleep_date'])

    # Hourly sensor table with the extra streams omitted by the previous timebin builder.
    hourly = con.execute(f"""
    WITH screen_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS screen_n, SUM(m_screen_use) AS screen_sum, AVG(m_screen_use) AS screen_mean
      FROM read_parquet('{ITEM_DIR/'ch2025_mScreenStatus.parquet'}') GROUP BY 1,2,3
    ), pedo_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS pedo_n, SUM(step) AS steps, SUM(distance) AS distance, SUM(burned_calories) AS calories,
             AVG(speed) AS speed_mean, MAX(speed) AS speed_max
      FROM read_parquet('{ITEM_DIR/'ch2025_wPedo.parquet'}') GROUP BY 1,2,3
    ), mlight_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS mlight_n, AVG(m_light) AS mlight_mean, MAX(m_light) AS mlight_max
      FROM read_parquet('{ITEM_DIR/'ch2025_mLight.parquet'}') GROUP BY 1,2,3
    ), wlight_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS wlight_n, AVG(w_light) AS wlight_mean, MAX(w_light) AS wlight_max
      FROM read_parquet('{ITEM_DIR/'ch2025_wLight.parquet'}') GROUP BY 1,2,3
    ), activity_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS activity_n, AVG(m_activity) AS activity_mean, MAX(m_activity) AS activity_max
      FROM read_parquet('{ITEM_DIR/'ch2025_mActivity.parquet'}') GROUP BY 1,2,3
    ), ac_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS ac_n, AVG(m_charging) AS charging_mean, MAX(m_charging) AS charging_any
      FROM read_parquet('{ITEM_DIR/'ch2025_mACStatus.parquet'}') GROUP BY 1,2,3
    ), hr_flat AS (
      SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             x::DOUBLE AS hr
      FROM read_parquet('{ITEM_DIR/'ch2025_wHr.parquet'}'), unnest(heart_rate) AS t(x)
    ), hr_h AS (
      SELECT subject_id, date, hour, COUNT(*) AS hr_n, AVG(hr) AS hr_mean, STDDEV_POP(hr) AS hr_std,
             MIN(hr) AS hr_min, MAX(hr) AS hr_max, quantile_cont(hr,0.9) AS hr_p90
      FROM hr_flat GROUP BY 1,2,3
    ), base AS (
      SELECT subject_id,date,hour FROM screen_h UNION SELECT subject_id,date,hour FROM pedo_h
      UNION SELECT subject_id,date,hour FROM mlight_h UNION SELECT subject_id,date,hour FROM wlight_h
      UNION SELECT subject_id,date,hour FROM activity_h UNION SELECT subject_id,date,hour FROM ac_h
      UNION SELECT subject_id,date,hour FROM hr_h
    )
    SELECT b.subject_id, CAST(b.date AS VARCHAR) AS date, b.hour,
           screen_h.* EXCLUDE(subject_id,date,hour), pedo_h.* EXCLUDE(subject_id,date,hour),
           mlight_h.* EXCLUDE(subject_id,date,hour), wlight_h.* EXCLUDE(subject_id,date,hour),
           activity_h.* EXCLUDE(subject_id,date,hour), ac_h.* EXCLUDE(subject_id,date,hour),
           hr_h.* EXCLUDE(subject_id,date,hour)
    FROM base b
    LEFT JOIN screen_h USING(subject_id,date,hour)
    LEFT JOIN pedo_h USING(subject_id,date,hour)
    LEFT JOIN mlight_h USING(subject_id,date,hour)
    LEFT JOIN wlight_h USING(subject_id,date,hour)
    LEFT JOIN activity_h USING(subject_id,date,hour)
    LEFT JOIN ac_h USING(subject_id,date,hour)
    LEFT JOIN hr_h USING(subject_id,date,hour)
    """).df()
    hourly['date'] = pd.to_datetime(hourly['date'])
    for c in hourly.columns:
        if c not in ['subject_id','date','hour']:
            hourly[c] = pd.to_numeric(hourly[c], errors='coerce')
    num_cols = [c for c in hourly.columns if c not in ['subject_id','date','hour']]
    hourly[num_cols] = hourly[num_cols].fillna(0)
    idx = {(r.subject_id, r.date.date(), int(r.hour)): r for r in hourly.itertuples(index=False)}

    # subject baselines from daytime/evening HR/activity for relative load.
    subj_base = hourly.groupby('subject_id').agg(
        subj_hr_mean=('hr_mean','mean'), subj_hr_std=('hr_mean','std'), subj_steps_hour_mean=('steps','mean'),
        subj_cal_hour_mean=('calories','mean'), subj_screen_hour_mean=('screen_sum','mean')
    ).fillna(0)

    rows = []
    for rec in keys.itertuples(index=False):
        sid = rec.subject_id; d = rec.lifelog_date.date(); sd = rec.sleep_date.date()
        # Cross-night sequence: evening of lifelog_date + morning of sleep_date.
        seq = []
        for h in range(18, 24):
            seq.append((h, idx.get((sid, d, h))))
        for h in range(0, 13):
            seq.append((24 + h, idx.get((sid, sd, h))))
        vals = []
        for rel_h, r in seq:
            if r is None:
                vals.append({'rel_h':rel_h,'screen':0,'steps':0,'activity':0,'mlight':0,'wlight':0,'lightmax':0,'charging':0,'hr':np.nan,'hrmax':np.nan,'calories':0,'distance':0})
            else:
                vals.append({
                    'rel_h': rel_h, 'screen': float(r.screen_sum), 'steps': float(r.steps),
                    'activity': float(r.activity_mean), 'mlight': float(r.mlight_mean), 'wlight': float(r.wlight_mean),
                    'lightmax': max(float(r.mlight_max), float(r.wlight_max)), 'charging': float(r.charging_mean),
                    'hr': float(r.hr_mean) if r.hr_mean else np.nan, 'hrmax': float(r.hr_max) if r.hr_max else np.nan,
                    'calories': float(r.calories), 'distance': float(r.distance)
                })
        # Quiet/sleep flags. Allow dark missing as quiet but penalize screen/steps/activity.
        quiet = [(v['screen'] <= 0 and v['steps'] <= 3 and v['activity'] <= 1.0 and v['lightmax'] <= 80) for v in vals]
        screenoff = [v['screen'] <= 0 for v in vals]
        inactive = [(v['steps'] <= 3 and v['activity'] <= 1.0) for v in vals]
        dark = [v['lightmax'] <= 30 for v in vals]
        q_len, q_s, q_e = longest_true_run(quiet)
        so_len, so_s, so_e = longest_true_run(screenoff)
        # primary block: longest quiet if >=2h, else longest screenoff/inactive intersection.
        block_s, block_e = q_s, q_e
        if q_len < 2:
            alt_flags = [a and b for a,b in zip(screenoff,inactive)]
            _, block_s, block_e = longest_true_run(alt_flags)
        if block_s < 0:
            block_s, block_e = 0, len(vals)-1
        block = vals[block_s:block_e+1]
        pre = vals[:block_s]; post = vals[block_e+1:]
        block_len = len(block)
        intr_screen = sum(v['screen'] > 0 for v in block)
        intr_steps = sum(v['steps'] > 3 or v['activity'] > 1.0 for v in block)
        intr_light = sum(v['lightmax'] > 80 for v in block)
        intr_any = sum((v['screen'] > 0) or (v['steps'] > 3) or (v['activity'] > 1.0) or (v['lightmax'] > 80) for v in block)
        hr_vals = [v['hr'] for v in block if pd.notna(v['hr'])]
        hr_mean = safe_mean(hr_vals)
        hr_spike = 0
        if hr_vals and pd.notna(hr_mean):
            hr_spike = sum((v['hr'] if pd.notna(v['hr']) else hr_mean) > hr_mean + 8 for v in block)
        row = {
            'subject_id': sid, 'lifelog_date': str(rec.lifelog_date.date()),
            's4x_cross_quiet_longest_h': q_len,
            's4x_cross_screenoff_longest_h': so_len,
            's4x_sleep_block_len_h': block_len,
            's4x_sleep_onset_rel_hour': vals[block_s]['rel_h'],
            's4x_wake_rel_hour': vals[block_e]['rel_h'] + 1,
            's4x_sleep_midpoint_rel_hour': (vals[block_s]['rel_h'] + vals[block_e]['rel_h'] + 1) / 2,
            's4x_quiet_fragmentation': transitions(quiet),
            's4x_screenoff_fragmentation': transitions(screenoff),
            's4x_inactive_fragmentation': transitions(inactive),
            's4x_dark_fragmentation': transitions(dark),
            's4x_block_screen_interrupt_h': intr_screen,
            's4x_block_step_interrupt_h': intr_steps,
            's4x_block_light_interrupt_h': intr_light,
            's4x_block_any_interrupt_h': intr_any,
            's4x_block_interrupt_rate': intr_any / max(block_len,1),
            's4x_block_steps_sum': sum(v['steps'] for v in block),
            's4x_block_screen_sum': sum(v['screen'] for v in block),
            's4x_block_light_max': max([v['lightmax'] for v in block] or [0]),
            's4x_block_hr_mean': hr_mean,
            's4x_block_hr_max': max([v['hrmax'] for v in block if pd.notna(v['hrmax'])] or [np.nan]),
            's4x_block_hr_spike_hours': hr_spike,
            's4x_pre_sleep_screen_sum': sum(v['screen'] for v in pre[-4:]),
            's4x_pre_sleep_steps_sum': sum(v['steps'] for v in pre[-4:]),
            's4x_post_wake_screen_sum': sum(v['screen'] for v in post[:4]),
            's4x_post_wake_steps_sum': sum(v['steps'] for v in post[:4]),
            's4x_charging_mean_block': safe_mean([v['charging'] for v in block]),
            's4x_dark_hours_crossnight': sum(dark),
            's4x_activity_hours_crossnight': sum((v['steps']>3 or v['activity']>1.0) for v in vals),
        }

        # Q2 daytime load / evening recovery on lifelog_date plus late pre-sleep window.
        day_hours = [idx.get((sid, d, h)) for h in range(6, 18)]
        eve_hours = [idx.get((sid, d, h)) for h in range(18, 24)]
        late_hours = [idx.get((sid, d, h)) for h in range(21, 24)] + [idx.get((sid, sd, h)) for h in range(0, 3)]
        def agg(hours, prefix):
            hs=[h for h in hours if h is not None]
            out={}
            for col in ['steps','distance','calories','screen_sum']:
                out[f'{prefix}_{col}_sum'] = sum(float(getattr(h,col)) for h in hs)
                out[f'{prefix}_{col}_maxh'] = max([float(getattr(h,col)) for h in hs] or [0])
            out[f'{prefix}_hr_mean'] = safe_mean([float(h.hr_mean) for h in hs if h.hr_mean])
            out[f'{prefix}_hr_max'] = max([float(h.hr_max) for h in hs if h.hr_max] or [np.nan])
            out[f'{prefix}_hr_std_hours'] = float(np.nanstd([float(h.hr_mean) if h.hr_mean else np.nan for h in hs])) if hs else np.nan
            out[f'{prefix}_active_hours'] = sum((float(h.steps)>20 or float(h.activity_mean)>1.2) for h in hs)
            out[f'{prefix}_screen_active_hours'] = sum(float(h.screen_sum)>0 for h in hs)
            return out
        q2 = {}
        q2.update(agg(day_hours, 'q2x_day'))
        q2.update(agg(eve_hours, 'q2x_evening'))
        q2.update(agg(late_hours, 'q2x_late'))
        sb = subj_base.loc[sid] if sid in subj_base.index else pd.Series(dtype=float)
        q2['q2x_day_steps_vs_subj_hour_mean'] = q2['q2x_day_steps_sum']/12 - float(sb.get('subj_steps_hour_mean',0))
        q2['q2x_day_cal_vs_subj_hour_mean'] = q2['q2x_day_calories_sum']/12 - float(sb.get('subj_cal_hour_mean',0))
        q2['q2x_evening_hr_minus_day_hr'] = q2['q2x_evening_hr_mean'] - q2['q2x_day_hr_mean']
        q2['q2x_late_hr_minus_day_hr'] = q2['q2x_late_hr_mean'] - q2['q2x_day_hr_mean']
        q2['q2x_late_screen_after_high_load'] = q2['q2x_late_screen_sum_sum'] * math.log1p(max(q2['q2x_day_steps_sum'],0))
        q2['q2x_recovery_failure_score'] = (q2['q2x_late_hr_minus_day_hr'] if pd.notna(q2['q2x_late_hr_minus_day_hr']) else 0) + 0.001*q2['q2x_late_screen_sum_sum'] - 0.001*q2['q2x_late_steps_sum']
        row.update(q2)
        rows.append(row)

    out = pd.DataFrame(rows)
    # Add previous-night carry-over for Q2/S labels.
    out['lifelog_dt'] = pd.to_datetime(out['lifelog_date'])
    out = out.sort_values(['subject_id','lifelog_dt'])
    lag_cols = [c for c in out.columns if c.startswith('s4x_') and c not in {'subject_id','lifelog_date'}]
    for c in lag_cols:
        out[f'q2x_prevnight_{c}'] = out.groupby('subject_id')[c].shift(1)
    out = out.drop(columns=['lifelog_dt'])
    path = FEATURE_DIR / 'mechanism_sleep_load_features_v2.parquet'
    con.register('mech', out)
    con.execute(f"COPY mech TO '{path}' (FORMAT PARQUET)")
    print(f'wrote {path} rows={len(out)} cols={out.shape[1]}')

if __name__ == '__main__':
    main()
