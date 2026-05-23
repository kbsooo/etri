#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, ensure_dirs

PROFILE_COLS = [
    'screen_use_sum_h','steps_sum_h','distance_sum_h','mlight_mean_h','wlight_mean_h','activity_mean_h',
    'screen_n_h','pedo_n_h','mlight_n_h','wlight_n_h','activity_n_h'
]
WINDOWS = {
    'all': list(range(24)),
    'morning_06_12': list(range(6,12)),
    'day_12_18': list(range(12,18)),
    'evening_18_24': list(range(18,24)),
    'night_00_06': list(range(0,6)),
    'late_21_03': [21,22,23,0,1,2],
}

def main():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    sample=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')
    tb=con.execute(f"select * from read_parquet('{FEATURE_DIR/'timebin_1h_features.parquet'}')").df()
    cl=con.execute(f"select subject_id,lifelog_date,sslcl_dino_temporal_k4_cluster from read_parquet('{FEATURE_DIR/'ssl_semantic_cluster_features.parquet'}')").df()
    cl['lifelog_date']=cl['lifelog_date'].astype(str)
    tb['lifelog_date']=tb['lifelog_date'].astype(str)
    long=tb.merge(cl,on=['subject_id','lifelog_date'],how='inner')
    rows=[]
    for cid, g in long.groupby('sslcl_dino_temporal_k4_cluster'):
        row={'cluster':int(cid),'hour_rows':len(g),'days':g[['subject_id','lifelog_date']].drop_duplicates().shape[0]}
        for wname, hours in WINDOWS.items():
            gg=g[g.hour.isin(hours)]
            for c in PROFILE_COLS:
                if c in gg.columns:
                    row[f'{wname}_{c}_mean']=float(pd.to_numeric(gg[c],errors='coerce').mean())
        rows.append(row)
    prof=pd.DataFrame(rows).sort_values('cluster')
    # label rates for train days only
    train2=train.copy(); train2['lifelog_date']=train2['lifelog_date'].astype(str)
    lab=train2.merge(cl,on=['subject_id','lifelog_date'],how='left')
    lr=[]
    for cid,g in lab.groupby('sslcl_dino_temporal_k4_cluster'):
        lr.append({'cluster':int(cid),'train_days':len(g),'Q1_rate':g.Q1.mean(),'Q3_rate':g.Q3.mean(),'Q2_rate':g.Q2.mean(),'S4_rate':g.S4.mean()})
    labprof=pd.DataFrame(lr).sort_values('cluster')
    out=prof.merge(labprof,on='cluster',how='left')
    out.to_csv(EXPERIMENT_DIR/'ssl_dino_k4_cluster_profile.csv',index=False)

    # compact z-profile against global mean for interpretation
    numeric=[c for c in out.columns if c not in {'cluster'}]
    interp=out[['cluster','days','train_days','Q1_rate','Q3_rate']].copy()
    for key in ['late_21_03_screen_use_sum_h_mean','night_00_06_steps_sum_h_mean','evening_18_24_steps_sum_h_mean','late_21_03_activity_mean_h_mean','late_21_03_mlight_mean_h_mean','morning_06_12_steps_sum_h_mean','day_12_18_steps_sum_h_mean']:
        if key in out.columns:
            vals=out[key].astype(float)
            sd=vals.std() if vals.std()>1e-9 else 1.0
            interp[key+'_z']=(vals-vals.mean())/sd
    interp.to_csv(EXPERIMENT_DIR/'ssl_dino_k4_cluster_profile_compact.csv',index=False)
    print('wrote', EXPERIMENT_DIR/'ssl_dino_k4_cluster_profile.csv')
    print('wrote', EXPERIMENT_DIR/'ssl_dino_k4_cluster_profile_compact.csv')
    print(interp.to_string(index=False))

if __name__=='__main__': main()
