#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ensure_dirs


def robust_z(s: pd.Series, ref_mask: pd.Series) -> pd.Series:
    v = pd.to_numeric(s, errors='coerce')
    ref = v[ref_mask]
    med = float(ref.median()) if ref.notna().any() else 0.0
    q75 = float(ref.quantile(.75)) if ref.notna().any() else 1.0
    q25 = float(ref.quantile(.25)) if ref.notna().any() else 0.0
    scale = q75 - q25
    if not np.isfinite(scale) or scale < 1e-6:
        scale = float(ref.std()) if ref.notna().sum() > 1 else 1.0
    if not np.isfinite(scale) or scale < 1e-6:
        scale = 1.0
    return ((v.fillna(med) - med) / scale).clip(-5, 5)


def main() -> None:
    ensure_dirs()
    con = duckdb.connect()
    psw = con.execute(f"select * from read_parquet('{FEATURE_DIR / 'prior_sleep_window_features_v1.parquet'}')").df()
    train_keys = pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')[['subject_id','lifelog_date']].assign(is_train=1)
    df = psw.merge(train_keys, on=['subject_id','lifelog_date'], how='left')
    df['is_train'] = df['is_train'].fillna(0).astype(int)
    ref = df['is_train'].eq(1)
    z = lambda c: robust_z(df[c] if c in df.columns else pd.Series(0,index=df.index), ref)

    # Cross-window contrasts: safer than raw level for personal behavioral shifts.
    pairs = [
        ('pedo_step_sum'), ('screen_use_sum'), ('act_mean'), ('act_nonzero_n'),
        ('mlight_mean'), ('mlight_max'), ('wlight_mean'), ('hr_mean'), ('hr_std'), ('charge_mean')
    ]
    for metric in pairs:
        for a,b in [('overnight','evening'),('presleep','evening'),('morning','overnight'),('fullctx','evening')]:
            ca=f'psw_sw_{a}_{metric}'; cb=f'psw_sw_{b}_{metric}'
            if ca in df.columns and cb in df.columns:
                df[f'pswp_{a}_minus_{b}_{metric}'] = pd.to_numeric(df[ca],errors='coerce') - pd.to_numeric(df[cb],errors='coerce')
                df[f'pswp_{a}_ratio_{b}_{metric}'] = pd.to_numeric(df[ca],errors='coerce') / (pd.to_numeric(df[cb],errors='coerce').abs() + 1e-3)

    df['pswp_rest_duration'] = (
        -0.24*z('psw_sw_fullctx_act_mean')
        -0.20*z('psw_sw_fullctx_pedo_step_sum')
        -0.18*z('psw_sw_fullctx_screen_use_sum')
        -0.14*z('psw_sw_fullctx_mlight_mean')
        -0.10*z('psw_sw_fullctx_wlight_mean')
        +0.14*z('psw_sw_overnight_charge_mean')
    )
    df['pswp_sleep_efficiency'] = (
        -0.28*z('psw_sw_overnight_act_mean')
        -0.24*z('psw_sw_overnight_screen_use_sum')
        -0.20*z('psw_sw_overnight_pedo_step_sum')
        -0.14*z('psw_sw_overnight_mlight_mean')
        -0.08*z('psw_sw_overnight_wlight_mean')
        -0.06*z('psw_sw_overnight_hr_std')
    )
    df['pswp_sleep_latency_bad'] = (
        +0.28*z('psw_sw_presleep_screen_use_sum')
        +0.22*z('psw_sw_presleep_mlight_mean')
        +0.18*z('psw_sw_presleep_act_mean')
        +0.12*z('psw_sw_presleep_pedo_step_sum')
        +0.10*z('psw_sw_presleep_hr_mean')
        -0.10*z('psw_sw_presleep_charge_mean')
    )
    df['pswp_waso_bad'] = (
        +0.24*z('psw_sw_overnight_screen_use_sum')
        +0.22*z('psw_sw_overnight_act_max')
        +0.18*z('psw_sw_overnight_pedo_step_sum')
        +0.16*z('psw_sw_overnight_mlight_max')
        +0.10*z('psw_sw_overnight_hr_std')
        +0.10*z('psw_sw_morning_screen_use_sum')
    )
    df['pswp_sleep_quality'] = (
        +0.38*df['pswp_sleep_efficiency']
        +0.28*df['pswp_rest_duration']
        -0.18*df['pswp_sleep_latency_bad']
        -0.16*df['pswp_waso_bad']
    )
    df['pswp_fatigue_stress'] = (
        +0.24*z('psw_sw_presleep_screen_use_sum')
        +0.20*z('psw_sw_presleep_hr_mean')
        +0.18*z('psw_sw_fullctx_hr_std')
        +0.16*z('psw_sw_morning_act_mean')
        +0.12*z('psw_sw_morning_pedo_step_sum')
        +0.10*z('psw_sw_presleep_mlight_mean')
    )
    keep = ['subject_id','sleep_date','lifelog_date'] + [c for c in df.columns if c.startswith('pswp_')]
    out = FEATURE_DIR/'prior_sleep_proxy_features_v1.parquet'
    df[keep].to_parquet(out, index=False)
    print(f'wrote {out} rows={len(df)} cols={len(keep)}')

if __name__=='__main__': main()
