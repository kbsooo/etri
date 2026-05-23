#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
import duckdb, pandas as pd, numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ITEM_DIR, ensure_dirs

def main():
 ensure_dirs(); con=duckdb.connect()
 keys=pd.concat([
  pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')[['subject_id','sleep_date','lifelog_date']],
  pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')[['subject_id','sleep_date','lifelog_date']]
 ]).drop_duplicates()
 keys['lifelog_date']=pd.to_datetime(keys.lifelog_date); keys['sleep_date']=pd.to_datetime(keys.sleep_date)
 hourly=con.execute(f"""
 WITH screen_h AS (SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, SUM(m_screen_use) screen, COUNT(*) screen_n FROM read_parquet('{ITEM_DIR/'ch2025_mScreenStatus.parquet'}') GROUP BY 1,2,3),
 pedo_h AS (SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, SUM(step) steps, SUM(distance) distance, SUM(burned_calories) calories, AVG(speed) speed FROM read_parquet('{ITEM_DIR/'ch2025_wPedo.parquet'}') GROUP BY 1,2,3),
 ml_h AS (SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, AVG(m_light) mlight, MAX(m_light) mlight_max FROM read_parquet('{ITEM_DIR/'ch2025_mLight.parquet'}') GROUP BY 1,2,3),
 wl_h AS (SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, AVG(w_light) wlight, MAX(w_light) wlight_max FROM read_parquet('{ITEM_DIR/'ch2025_wLight.parquet'}') GROUP BY 1,2,3),
 act_h AS (SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, AVG(m_activity) activity, MAX(m_activity) activity_max FROM read_parquet('{ITEM_DIR/'ch2025_mActivity.parquet'}') GROUP BY 1,2,3),
 ac_h AS (SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, AVG(m_charging) charging FROM read_parquet('{ITEM_DIR/'ch2025_mACStatus.parquet'}') GROUP BY 1,2,3),
 hr_flat AS (SELECT subject_id, CAST(timestamp AS DATE) date, EXTRACT('hour' FROM timestamp)::INT AS hour, x::DOUBLE hr FROM read_parquet('{ITEM_DIR/'ch2025_wHr.parquet'}'), unnest(heart_rate) AS t(x)),
 hr_h AS (SELECT subject_id,date,hour, AVG(hr) hr, MAX(hr) hr_max, STDDEV_POP(hr) hr_std FROM hr_flat GROUP BY 1,2,3),
 base AS (SELECT subject_id,date,hour FROM screen_h UNION SELECT subject_id,date,hour FROM pedo_h UNION SELECT subject_id,date,hour FROM ml_h UNION SELECT subject_id,date,hour FROM wl_h UNION SELECT subject_id,date,hour FROM act_h UNION SELECT subject_id,date,hour FROM ac_h UNION SELECT subject_id,date,hour FROM hr_h)
 SELECT b.subject_id, CAST(b.date AS VARCHAR) date, b.hour,
        screen_h.* EXCLUDE(subject_id,date,hour), pedo_h.* EXCLUDE(subject_id,date,hour), ml_h.* EXCLUDE(subject_id,date,hour), wl_h.* EXCLUDE(subject_id,date,hour), act_h.* EXCLUDE(subject_id,date,hour), ac_h.* EXCLUDE(subject_id,date,hour), hr_h.* EXCLUDE(subject_id,date,hour)
 FROM base b LEFT JOIN screen_h USING(subject_id,date,hour) LEFT JOIN pedo_h USING(subject_id,date,hour) LEFT JOIN ml_h USING(subject_id,date,hour) LEFT JOIN wl_h USING(subject_id,date,hour) LEFT JOIN act_h USING(subject_id,date,hour) LEFT JOIN ac_h USING(subject_id,date,hour) LEFT JOIN hr_h USING(subject_id,date,hour)
 """).df()
 hourly['date']=pd.to_datetime(hourly.date)
 for c in hourly.columns:
  if c not in ['subject_id','date','hour']: hourly[c]=pd.to_numeric(hourly[c],errors='coerce').fillna(0)
 idx={(r.subject_id,r.date.date(),int(r.hour)):r for r in hourly.itertuples(index=False)}
 vars=[c for c in hourly.columns if c not in ['subject_id','date','hour']]
 rows=[]
 for rec in keys.itertuples(index=False):
  sid=rec.subject_id; d=rec.lifelog_date.date(); sd=rec.sleep_date.date(); row={'subject_id':sid,'lifelog_date':str(d)}
  # Cross-night hourly shape preserving features.
  seq=[]
  for h in range(18,24): seq.append((h, idx.get((sid,d,h))))
  for h in range(0,13): seq.append((24+h, idx.get((sid,sd,h))))
  for rel,r in seq:
   for v in vars:
    row[f'cn_h{rel}_{v}']=float(getattr(r,v)) if r is not None else 0.0
  # Daytime-to-evening flat for fatigue.
  for h in range(6,24):
   r=idx.get((sid,d,h))
   for v in ['steps','calories','distance','screen','hr','hr_max','activity','speed']:
    row[f'day_h{h}_{v}']=float(getattr(r,v)) if r is not None else 0.0
  rows.append(row)
 out=pd.DataFrame(rows)
 path=FEATURE_DIR/'crossnight_day_flat_features_v2.parquet'
 con.register('outdf',out); con.execute(f"COPY outdf TO '{path}' (FORMAT PARQUET)")
 print(f'wrote {path} rows={len(out)} cols={out.shape[1]}')
if __name__=='__main__': main()
