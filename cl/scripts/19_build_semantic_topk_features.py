#!/usr/bin/env python3
from __future__ import annotations

import re, sys
from pathlib import Path
import duckdb
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import FEATURE_DIR, ITEM_DIR, ensure_dirs


def safe(s: str) -> str:
    s = str(s).lower().strip()
    s = re.sub(r'[^0-9a-z가-힣]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s[:45] or 'unknown'


def hour_window(h):
    if h in [21,22,23,0,1,2]: return '21_03'
    if h in [0,1,2,3,4,5]: return '00_06'
    if h in [6,7,8,9,10,11]: return 'morning'
    if h in [18,19,20,21,22,23]: return 'evening'
    return 'day'


def main():
    ensure_dirs(); con=duckdb.connect()
    keys = con.execute(f"select subject_id, lifelog_date from read_parquet('{FEATURE_DIR/'daily_window_features.parquet'}')").df()
    keys['lifelog_date']=keys['lifelog_date'].astype(str)
    out=keys.copy()

    # Exact top app usage features.
    app=con.execute(f"""
      SELECT subject_id, CAST(timestamp AS DATE)::VARCHAR AS lifelog_date,
             EXTRACT('hour' FROM timestamp)::INT AS hour,
             lower(a.app_name) AS app_name, a.total_time::DOUBLE AS total_time
      FROM read_parquet('{ITEM_DIR/'ch2025_mUsageStats.parquet'}'), unnest(m_usage_stats) AS t(a)
    """).df()
    if len(app):
        app['app_safe']=app['app_name'].map(safe)
        top_apps=app.groupby('app_safe')['total_time'].sum().sort_values(ascending=False).head(100).index.tolist()
        app_top=app[app.app_safe.isin(top_apps)].copy()
        for win_name, mask in {
            'all': np.ones(len(app_top), dtype=bool),
            '21_03': app_top['hour'].isin([21,22,23,0,1,2]),
            '00_06': app_top['hour'].between(0,5),
            'evening': app_top['hour'].between(18,23),
        }.items():
            piv=app_top[mask].pivot_table(index=['subject_id','lifelog_date'], columns='app_safe', values='total_time', aggfunc='sum', fill_value=0)
            piv.columns=[f'topapp_{win_name}_{c}_time' for c in piv.columns]
            piv=piv.reset_index()
            out=out.merge(piv,on=['subject_id','lifelog_date'],how='left')
        # session-ish app burst features
        agg=app.groupby(['subject_id','lifelog_date','hour']).agg(hour_app_time=('total_time','sum'), hour_app_unique=('app_name','nunique')).reset_index()
        day=agg.groupby(['subject_id','lifelog_date']).agg(
            app_hourly_time_max=('hour_app_time','max'),
            app_hourly_time_std=('hour_app_time','std'),
            app_hourly_unique_max=('hour_app_unique','max'),
            app_active_hours=('hour_app_time', lambda x: (x>0).sum()),
        ).reset_index()
        out=out.merge(day,on=['subject_id','lifelog_date'],how='left')

    # Exact ambience top labels.
    amb=con.execute(f"""
      SELECT subject_id, CAST(timestamp AS DATE)::VARCHAR AS lifelog_date,
             EXTRACT('hour' FROM timestamp)::INT AS hour,
             lower(a[1]) AS cls, try_cast(a[2] AS DOUBLE) AS prob
      FROM read_parquet('{ITEM_DIR/'ch2025_mAmbience.parquet'}'), unnest(m_ambience) AS t(a)
    """).df()
    if len(amb):
        amb['cls_safe']=amb['cls'].map(safe)
        top_cls=amb.groupby('cls_safe')['prob'].sum().sort_values(ascending=False).head(80).index.tolist()
        amb_top=amb[amb.cls_safe.isin(top_cls)].copy()
        for win_name, mask in {
            'all': np.ones(len(amb_top), dtype=bool),
            '21_03': amb_top['hour'].isin([21,22,23,0,1,2]),
            '00_06': amb_top['hour'].between(0,5),
            'evening': amb_top['hour'].between(18,23),
        }.items():
            piv=amb_top[mask].pivot_table(index=['subject_id','lifelog_date'], columns='cls_safe', values='prob', aggfunc='mean', fill_value=0)
            piv.columns=[f'topamb_{win_name}_{c}_mean' for c in piv.columns]
            out=out.merge(piv.reset_index(),on=['subject_id','lifelog_date'],how='left')

    # BLE device class composition.
    ble=con.execute(f"""
      SELECT subject_id, CAST(timestamp AS DATE)::VARCHAR AS lifelog_date,
             EXTRACT('hour' FROM timestamp)::INT AS hour,
             b.device_class AS device_class, b.rssi::DOUBLE AS rssi
      FROM read_parquet('{ITEM_DIR/'ch2025_mBle.parquet'}'), unnest(m_ble) AS t(b)
    """).df()
    if len(ble):
        top_dc=ble.groupby('device_class').size().sort_values(ascending=False).head(30).index.tolist()
        bt=ble[ble.device_class.isin(top_dc)].copy()
        piv=bt.pivot_table(index=['subject_id','lifelog_date'], columns='device_class', values='rssi', aggfunc='count', fill_value=0)
        piv.columns=[f'ble_deviceclass_{safe(c)}_count' for c in piv.columns]
        out=out.merge(piv.reset_index(),on=['subject_id','lifelog_date'],how='left')

    out=out.fillna(0)
    path=FEATURE_DIR/'semantic_topk_features_v2.parquet'
    con.register('out_df', out)
    con.execute(f"COPY out_df TO '{path}' (FORMAT PARQUET)")
    print(f'wrote {path} rows={len(out)} cols={out.shape[1]}')

if __name__=='__main__': main()
