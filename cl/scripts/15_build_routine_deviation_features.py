#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ensure_dirs


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    # Use pre-routine model features as source but avoid huge hourly flattening and existing subject-normalized expansions.
    df = con.execute(f"SELECT * FROM read_parquet('{FEATURE_DIR / 'model_features_v0.parquet'}')").df()
    df['date_dt'] = pd.to_datetime(df['lifelog_date'])
    df = df.sort_values(['subject_id', 'date_dt']).reset_index(drop=True)

    out = df[['subject_id', 'lifelog_date']].copy()
    out['dow'] = df['date_dt'].dt.dayofweek
    out['is_weekend'] = (out['dow'] >= 5).astype(int)
    out['month'] = df['date_dt'].dt.month
    out['dayofmonth'] = df['date_dt'].dt.day
    out['dow_sin'] = np.sin(2 * np.pi * out['dow'] / 7)
    out['dow_cos'] = np.cos(2 * np.pi * out['dow'] / 7)

    gdate = df.groupby('subject_id')['date_dt']
    out['days_since_subject_start'] = (df['date_dt'] - gdate.transform('min')).dt.days
    out['days_until_subject_end'] = (gdate.transform('max') - df['date_dt']).dt.days
    denom = (gdate.transform('max') - gdate.transform('min')).dt.days.replace(0, np.nan)
    out['subject_time_frac'] = out['days_since_subject_start'] / denom
    out['gap_from_prev_day'] = df.groupby('subject_id')['date_dt'].diff().dt.days.fillna(0)
    out['gap_to_next_day'] = -df.groupby('subject_id')['date_dt'].diff(-1).dt.days.fillna(0)

    all_cols = [c for c in df.columns if c not in {'subject_id','lifelog_date','date_dt'}]
    # Focus on interpretable daily/semantic/sleep/state columns; skip generated subj norms and 24h flat columns.
    keys = ('screen_', 'steps_', 'distance_', 'mlight_', 'wlight_', 'activity_', 'sleep', 'quiet_', 'screenoff_', 'late_', 'dark_', 'bright_',
            'hr_', 'gps_', 'app_', 'wifi_', 'ble_', 'amb_', 'state_', 'night_')
    base_cols = []
    for c in all_cols:
        if '__subj_' in c or c.startswith('h'):
            continue
        if any(k in c for k in keys):
            s = pd.to_numeric(df[c], errors='coerce')
            if s.notna().sum() > 20 and s.nunique(dropna=True) > 2:
                base_cols.append(c)
    # Keep moderate size by preferring columns with coverage and variance.
    scored = []
    for c in base_cols:
        s = pd.to_numeric(df[c], errors='coerce')
        scored.append((s.notna().mean() * float(s.std(skipna=True) or 0), c))
    base_cols = [c for _, c in sorted(scored, reverse=True)[:160]]

    for c in base_cols:
        s = pd.to_numeric(df[c], errors='coerce')
        grp = df['subject_id']
        # day-to-day change / volatility
        prev = s.groupby(grp).shift(1)
        out[f'{c}__prev_delta'] = s - prev
        out[f'{c}__prev_abs_delta'] = (s - prev).abs()
        # trailing routine deviations, shifted to avoid using same-day in baseline
        roll3 = s.groupby(grp).transform(lambda x: x.shift(1).rolling(3, min_periods=2).mean())
        roll7 = s.groupby(grp).transform(lambda x: x.shift(1).rolling(7, min_periods=3).mean())
        out[f'{c}__dev_roll3'] = s - roll3
        out[f'{c}__dev_roll7'] = s - roll7
        # subject weekday routine deviation, transductive but label-free
        wd_mean = s.groupby([df['subject_id'], out['dow']]).transform('mean')
        subj_mean = s.groupby(grp).transform('mean')
        out[f'{c}__dev_weekday_mean'] = s - wd_mean
        out[f'{c}__weekday_vs_subject_mean'] = wd_mean - subj_mean

    out_path = FEATURE_DIR / 'routine_deviation_features_v1.parquet'
    con.register('out_df', out)
    con.execute(f"COPY out_df TO '{out_path}' (FORMAT PARQUET)")
    print(f'wrote {out_path} rows={len(out)} cols={out.shape[1]} base_cols={len(base_cols)}')

if __name__ == '__main__':
    main()
