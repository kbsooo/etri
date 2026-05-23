#!/usr/bin/env python3
from __future__ import annotations
import json, math, warnings, sys
from pathlib import Path
from collections import Counter
import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, ITEM_DIR, FEATURE_DIR, EXPERIMENT_DIR, OUT_DIR, LABELS, ID_COLS, ensure_dirs
warnings.filterwarnings('ignore')
KEYS=['subject_id','lifelog_date']
DROP=set(ID_COLS+LABELS+['is_train'])
BASE_CFG={
    'Q1':('semantic_only',50,0.03),
    'Q2':('day_flat',20,0.01),
    'Q3':('dino_k4_cluster',10,0.30),
    'S1':('no_flat_hourly',20,0.10),
    'S2':('no_flat_hourly',20,0.001),
    'S3':('semantic_only',20,0.01),
    'S4':('sleep_plus_s4x',200,0.003),
}


def folds():
    return json.loads((OUT_DIR/'validation'/'folds_chrono.json').read_text())['folds']

def safe_mean(xs):
    xs=[float(x) for x in xs if pd.notna(x)]
    return float(np.mean(xs)) if xs else np.nan

def safe_std(xs):
    xs=[float(x) for x in xs if pd.notna(x)]
    return float(np.std(xs)) if xs else np.nan

def longest_run(flags):
    best=(0,-1,-1); cur=0; start=-1
    for i,f in enumerate(flags):
        if bool(f):
            if cur==0: start=i
            cur+=1
            if cur>best[0]: best=(cur,start,i)
        else:
            cur=0
    return best

def transitions(flags):
    return sum(int(a!=b) for a,b in zip(flags,flags[1:]))

def entropy(vals):
    vals=[v for v in vals if pd.notna(v)]
    if not vals: return 0.0
    c=Counter(vals); n=sum(c.values())
    return float(-sum((v/n)*math.log((v/n)+1e-12) for v in c.values()))

def build_hourly():
    con=duckdb.connect()
    # Sensor hourly aggregation. Keep intentionally compact but richer than old builders.
    q=f"""
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
             COUNT(*) AS activity_n, AVG(m_activity) AS activity_mean, MAX(m_activity) AS activity_max,
             SUM(CASE WHEN m_activity > 1 THEN 1 ELSE 0 END) AS activity_active_n
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
             MIN(hr) AS hr_min, MAX(hr) AS hr_max, quantile_cont(hr,0.9) AS hr_p90, quantile_cont(hr,0.95) AS hr_p95
      FROM hr_flat GROUP BY 1,2,3
    ), usage_flat AS (
      SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             lower(x.app_name) AS app_name, x.total_time::DOUBLE AS total_time
      FROM read_parquet('{ITEM_DIR/'ch2025_mUsageStats.parquet'}'), unnest(m_usage_stats) AS t(x)
    ), usage_h AS (
      SELECT subject_id, date, hour, COUNT(*) AS app_n, COUNT(DISTINCT app_name) AS app_unique,
             SUM(total_time) AS app_total_time,
             SUM(CASE WHEN app_name LIKE '%카카오%' OR app_name LIKE '%통화%' OR app_name LIKE '%전화%' OR app_name LIKE '%instagram%' OR app_name LIKE '%facebook%' OR app_name LIKE '%discord%' THEN total_time ELSE 0 END) AS app_social_time,
             SUM(CASE WHEN app_name LIKE '%youtube%' OR app_name LIKE '%netflix%' OR app_name LIKE '%music%' OR app_name LIKE '%뮤직%' THEN total_time ELSE 0 END) AS app_media_time
      FROM usage_flat GROUP BY 1,2,3
    ), gps_flat AS (
      SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             x.speed::DOUBLE AS speed, x.latitude::DOUBLE AS lat, x.longitude::DOUBLE AS lon
      FROM read_parquet('{ITEM_DIR/'ch2025_mGps.parquet'}'), unnest(m_gps) AS t(x)
    ), gps_h AS (
      SELECT subject_id, date, hour, COUNT(*) AS gps_n, AVG(speed) AS gps_speed_mean, MAX(speed) AS gps_speed_max,
             STDDEV_POP(speed) AS gps_speed_std, COUNT(DISTINCT round(lat,4)||','||round(lon,4)) AS gps_place_bins
      FROM gps_flat GROUP BY 1,2,3
    ), wifi_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS wifi_scan_n, SUM(array_length(m_wifi)) AS wifi_device_n
      FROM read_parquet('{ITEM_DIR/'ch2025_mWifi.parquet'}') GROUP BY 1,2,3
    ), ble_h AS (
      SELECT subject_id, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             COUNT(*) AS ble_scan_n, SUM(array_length(m_ble)) AS ble_device_n
      FROM read_parquet('{ITEM_DIR/'ch2025_mBle.parquet'}') GROUP BY 1,2,3
    ), amb_flat AS (
      SELECT subject_id, timestamp, CAST(timestamp AS DATE) AS date, EXTRACT('hour' FROM timestamp)::INT AS hour,
             lower(x[1]) AS amb_name, try_cast(x[2] AS DOUBLE) AS amb_prob
      FROM read_parquet('{ITEM_DIR/'ch2025_mAmbience.parquet'}'), unnest(m_ambience) AS t(x)
    ), amb_h AS (
      SELECT subject_id, date, hour, COUNT(*) AS amb_n,
             SUM(CASE WHEN amb_name LIKE '%speech%' THEN amb_prob ELSE 0 END) AS amb_speech_prob,
             SUM(CASE WHEN amb_name LIKE '%vehicle%' OR amb_name LIKE '%car%' THEN amb_prob ELSE 0 END) AS amb_vehicle_prob,
             SUM(CASE WHEN amb_name LIKE '%music%' THEN amb_prob ELSE 0 END) AS amb_music_prob,
             SUM(CASE WHEN amb_name LIKE '%outside%' THEN amb_prob ELSE 0 END) AS amb_outside_prob
      FROM amb_flat GROUP BY 1,2,3
    ), base AS (
      SELECT subject_id,date,hour FROM screen_h UNION SELECT subject_id,date,hour FROM pedo_h
      UNION SELECT subject_id,date,hour FROM mlight_h UNION SELECT subject_id,date,hour FROM wlight_h
      UNION SELECT subject_id,date,hour FROM activity_h UNION SELECT subject_id,date,hour FROM ac_h
      UNION SELECT subject_id,date,hour FROM hr_h UNION SELECT subject_id,date,hour FROM usage_h
      UNION SELECT subject_id,date,hour FROM gps_h UNION SELECT subject_id,date,hour FROM wifi_h
      UNION SELECT subject_id,date,hour FROM ble_h UNION SELECT subject_id,date,hour FROM amb_h
    )
    SELECT b.subject_id, CAST(b.date AS VARCHAR) AS date, b.hour,
           screen_h.* EXCLUDE(subject_id,date,hour), pedo_h.* EXCLUDE(subject_id,date,hour),
           mlight_h.* EXCLUDE(subject_id,date,hour), wlight_h.* EXCLUDE(subject_id,date,hour),
           activity_h.* EXCLUDE(subject_id,date,hour), ac_h.* EXCLUDE(subject_id,date,hour),
           hr_h.* EXCLUDE(subject_id,date,hour), usage_h.* EXCLUDE(subject_id,date,hour),
           gps_h.* EXCLUDE(subject_id,date,hour), wifi_h.* EXCLUDE(subject_id,date,hour),
           ble_h.* EXCLUDE(subject_id,date,hour), amb_h.* EXCLUDE(subject_id,date,hour)
    FROM base b
    LEFT JOIN screen_h USING(subject_id,date,hour)
    LEFT JOIN pedo_h USING(subject_id,date,hour)
    LEFT JOIN mlight_h USING(subject_id,date,hour)
    LEFT JOIN wlight_h USING(subject_id,date,hour)
    LEFT JOIN activity_h USING(subject_id,date,hour)
    LEFT JOIN ac_h USING(subject_id,date,hour)
    LEFT JOIN hr_h USING(subject_id,date,hour)
    LEFT JOIN usage_h USING(subject_id,date,hour)
    LEFT JOIN gps_h USING(subject_id,date,hour)
    LEFT JOIN wifi_h USING(subject_id,date,hour)
    LEFT JOIN ble_h USING(subject_id,date,hour)
    LEFT JOIN amb_h USING(subject_id,date,hour)
    """
    hourly=con.execute(q).df()
    hourly['date']=pd.to_datetime(hourly['date'])
    for c in hourly.columns:
        if c not in ['subject_id','date','hour']:
            hourly[c]=pd.to_numeric(hourly[c], errors='coerce')
    num=[c for c in hourly.columns if c not in ['subject_id','date','hour']]
    hourly[num]=hourly[num].fillna(0)
    return hourly

def build_followup_features():
    ensure_dirs(); con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')[ID_COLS]
    test=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')[ID_COLS]
    keys=pd.concat([train,test],ignore_index=True).drop_duplicates().copy()
    keys['lifelog_date']=pd.to_datetime(keys['lifelog_date']); keys['sleep_date']=pd.to_datetime(keys['sleep_date'])
    hourly=build_hourly()
    idx={(r.subject_id,r.date.date(),int(r.hour)):r for r in hourly.itertuples(index=False)}
    # subject baselines for relative signals
    subj=hourly.groupby('subject_id').agg(
        hr_mean=('hr_mean','mean'), hr_std=('hr_mean','std'), steps_h=('steps','mean'), cal_h=('calories','mean'),
        screen_h=('screen_sum','mean'), app_h=('app_total_time','mean'), gps_h=('gps_speed_mean','mean')
    ).fillna(0)

    rows=[]; cn_seq=[]; day_seq=[]
    for rec in keys.itertuples(index=False):
        sid=rec.subject_id; d=rec.lifelog_date.date(); sd=rec.sleep_date.date(); sb=subj.loc[sid]
        def get(date,h): return idx.get((sid,date,h))
        def val(r,c,default=0.0): return float(getattr(r,c)) if r is not None and pd.notna(getattr(r,c)) else default
        # cross-night sequence 18..23 + 0..12
        seq=[]
        for h in range(18,24): seq.append((h,get(d,h)))
        for h in range(0,13): seq.append((24+h,get(sd,h)))
        V=[]
        for rel,r in seq:
            lightmax=max(val(r,'mlight_max'), val(r,'wlight_max'))
            hr=val(r,'hr_mean',np.nan); hrmax=val(r,'hr_max',np.nan)
            V.append(dict(rel=rel, screen=val(r,'screen_sum'), steps=val(r,'steps'), act=val(r,'activity_mean'), actn=val(r,'activity_active_n'),
                          light=lightmax, charging=val(r,'charging_mean'), hr=hr if hr>0 else np.nan, hrmax=hrmax if hrmax>0 else np.nan,
                          app=val(r,'app_total_time'), social=val(r,'app_social_time'), gps=val(r,'gps_speed_mean'), missing=int(r is None)))
        quiet=[v['screen']<=0 and v['steps']<=3 and v['act']<=1.0 and v['light']<=80 for v in V]
        screenoff=[v['screen']<=0 for v in V]
        inactive=[v['steps']<=3 and v['act']<=1.0 for v in V]
        dark=[v['light']<=30 for v in V]
        q_len,q_s,q_e=longest_run(quiet)
        if q_len<2:
            _,q_s,q_e=longest_run([a and b for a,b in zip(screenoff,inactive)])
        if q_s<0: q_s,q_e=0,len(V)-1
        block=V[q_s:q_e+1]; pre=V[:q_s]; post=V[q_e+1:]
        bl=max(len(block),1)
        hr_block=[v['hr'] for v in block if pd.notna(v['hr'])]
        hr_pre=[v['hr'] for v in pre[-4:] if pd.notna(v['hr'])]
        hr_post=[v['hr'] for v in post[:4] if pd.notna(v['hr'])]
        bh=safe_mean(hr_block); ph=safe_mean(hr_pre); poh=safe_mean(hr_post)
        hr_spikes=sum((v['hr'] if pd.notna(v['hr']) else bh) > (bh+8 if pd.notna(bh) else 999) for v in block)
        any_intr=[(v['screen']>0) or (v['steps']>3) or (v['act']>1.0) or (v['light']>80) for v in block]
        first=block[:max(1,bl//2)]; second=block[max(1,bl//2):]
        row={'subject_id':sid,'lifelog_date':str(d)}
        # Q1 compact sleep quality index
        row.update({
            'q1qual_block_len_h': bl,
            'q1qual_onset_rel': V[q_s]['rel'], 'q1qual_wake_rel': V[q_e]['rel']+1,
            'q1qual_midpoint_rel': (V[q_s]['rel']+V[q_e]['rel']+1)/2,
            'q1qual_quiet_longest_h': q_len,
            'q1qual_interrupt_rate': sum(any_intr)/bl,
            'q1qual_screen_interrupt_h': sum(v['screen']>0 for v in block),
            'q1qual_step_interrupt_h': sum(v['steps']>3 or v['act']>1.0 for v in block),
            'q1qual_light_interrupt_h': sum(v['light']>80 for v in block),
            'q1qual_hr_spike_h': hr_spikes,
            'q1qual_hr_evening_minus_block': (ph-bh) if pd.notna(ph) and pd.notna(bh) else np.nan,
            'q1qual_hr_morning_minus_block': (poh-bh) if pd.notna(poh) and pd.notna(bh) else np.nan,
            'q1qual_dark_consistency': sum(dark[q_s:q_e+1])/bl,
            'q1qual_charge_consistency': safe_mean([v['charging'] for v in block]),
            'q1qual_morning_screen_4h': sum(v['screen'] for v in post[:4]),
            'q1qual_morning_steps_4h': sum(v['steps'] for v in post[:4]),
            'q1qual_missing_h': sum(v['missing'] for v in V),
            'q1qual_episode_confidence': q_len/(sum(v['missing']==0 for v in V)+1e-6) - transitions(quiet)/20.0,
        })
        # S4 event-level hourly WASO proxy
        row.update({
            's4evt_episode_len_h': bl,
            's4evt_any_interrupt_h': sum(any_intr),
            's4evt_any_interrupt_rate': sum(any_intr)/bl,
            's4evt_screen_burst_h': sum(v['screen']>0 for v in block),
            's4evt_step_burst_h': sum(v['steps']>3 for v in block),
            's4evt_activity_burst_h': sum(v['act']>1.0 for v in block),
            's4evt_light_spike_h': sum(v['light']>80 for v in block),
            's4evt_hr_spike_h': hr_spikes,
            's4evt_first_half_interrupt_h': sum((v['screen']>0) or (v['steps']>3) or (v['light']>80) for v in first),
            's4evt_second_half_interrupt_h': sum((v['screen']>0) or (v['steps']>3) or (v['light']>80) for v in second),
            's4evt_late_interrupt_balance': sum((v['screen']>0) or (v['steps']>3) or (v['light']>80) for v in second)-sum((v['screen']>0) or (v['steps']>3) or (v['light']>80) for v in first),
            's4evt_interrupt_clusters': transitions([not x for x in any_intr]),
            's4evt_longest_uninterrupted_h': longest_run([not x for x in any_intr])[0],
            's4evt_block_screen_sum': sum(v['screen'] for v in block),
            's4evt_block_steps_sum': sum(v['steps'] for v in block),
            's4evt_block_light_max': max([v['light'] for v in block] or [0]),
            's4evt_block_hr_max_minus_mean': (max([v['hrmax'] for v in block if pd.notna(v['hrmax'])] or [np.nan])-bh) if pd.notna(bh) else np.nan,
            's4evt_episode_confidence': row['q1qual_episode_confidence'],
        })
        # Daytime Q2 load/recovery features
        def hours(date,hs): return [get(date,h) for h in hs]
        def agg(rs,prefix):
            hs=[r for r in rs if r is not None]
            out={}
            for c in ['steps','distance','calories','screen_sum','app_total_time','app_social_time','app_media_time','gps_speed_mean','wifi_device_n','ble_device_n','amb_speech_prob','amb_vehicle_prob','amb_music_prob','amb_outside_prob']:
                vals=[val(r,c) for r in hs]
                out[f'{prefix}_{c}_sum']=float(np.sum(vals)) if vals else 0.0
                out[f'{prefix}_{c}_max']=float(np.max(vals)) if vals else 0.0
                out[f'{prefix}_{c}_mean']=float(np.mean(vals)) if vals else 0.0
            hrv=[val(r,'hr_mean',np.nan) for r in hs]; hrv=[x for x in hrv if pd.notna(x) and x>0]
            out[f'{prefix}_hr_mean']=safe_mean(hrv); out[f'{prefix}_hr_p90_hour']=float(np.nanpercentile(hrv,90)) if hrv else np.nan
            out[f'{prefix}_high_hr_hours']=sum(x > (float(sb.hr_mean)+0.5*float(sb.hr_std)) for x in hrv) if hrv else 0
            out[f'{prefix}_active_hours']=sum(val(r,'steps')>20 or val(r,'activity_mean')>1.2 for r in hs)
            out[f'{prefix}_screen_hours']=sum(val(r,'screen_sum')>0 for r in hs)
            out[f'{prefix}_context_entropy']=entropy([round(val(r,'wifi_device_n')/10) for r in hs] + [round(val(r,'ble_device_n')/10) for r in hs])
            return out
        q2={}
        for end in [12,15,18,21]:
            q2.update(agg(hours(d, range(6,end)), f'q2lr_day06_{end}'))
        q2.update(agg(hours(d, range(18,24)), 'q2lr_evening'))
        q2.update(agg(hours(d, range(21,24))+hours(sd,range(0,3)), 'q2lr_late'))
        q2['q2lr_evening_hr_minus_day']=q2['q2lr_evening_hr_mean']-q2['q2lr_day06_18_hr_mean']
        q2['q2lr_late_hr_minus_day']=q2['q2lr_late_hr_mean']-q2['q2lr_day06_18_hr_mean']
        q2['q2lr_activity_drop_18_to_evening']=q2['q2lr_day06_18_steps_mean']-q2['q2lr_evening_steps_mean']
        q2['q2lr_late_screen_after_load']=math.log1p(max(q2['q2lr_day06_18_steps_sum'],0))*math.log1p(max(q2['q2lr_late_screen_sum_sum'],0))
        q2['q2lr_load_score']=0.001*q2['q2lr_day06_18_steps_sum']+0.001*q2['q2lr_day06_18_calories_sum']+0.01*q2['q2lr_day06_18_high_hr_hours']+0.00001*q2['q2lr_day06_18_app_total_time_sum']
        q2['q2lr_recovery_failure']=np.nan_to_num(q2['q2lr_late_hr_minus_day']) + 0.001*q2['q2lr_late_screen_sum_sum'] - 0.001*q2['q2lr_late_steps_sum']
        row.update(q2)
        rows.append(row)
        # sequences for prototype features
        cn_vec=[]
        for v in V:
            cn_vec.extend([v['screen'], v['steps'], v['act'], v['light'], v['charging'], np.nan_to_num(v['hr'], nan=float(sb.hr_mean)), v['missing']])
        cn_seq.append(cn_vec)
        day_vec=[]
        for r in hours(d, range(6,24)):
            day_vec.extend([val(r,'steps'), val(r,'screen_sum'), val(r,'app_total_time'), val(r,'gps_speed_mean'), val(r,'wifi_device_n'), val(r,'ble_device_n'), val(r,'hr_mean',float(sb.hr_mean))])
        day_seq.append(day_vec)

    out=pd.DataFrame(rows)
    # add global prototype clusters (unsupervised). Compact features only.
    for prefix,mat,ks in [('cnproto',np.array(cn_seq,dtype=float),[3,4,6,8]),('q2proto',np.array(day_seq,dtype=float),[3,4,6,8])]:
        mat=np.nan_to_num(mat, nan=0.0, posinf=0.0, neginf=0.0)
        mat=StandardScaler().fit_transform(mat)
        for k in ks:
            km=KMeans(n_clusters=k, random_state=42, n_init=20)
            lab=km.fit_predict(mat)
            dist=km.transform(mat)
            out[f'{prefix}_k{k}_label']=lab
            out[f'{prefix}_k{k}_dist_min']=dist.min(axis=1)
            out[f'{prefix}_k{k}_dist_entropy']=-np.sum((1/(dist+1e-6)/(1/(dist+1e-6)).sum(axis=1,keepdims=True))*np.log((1/(dist+1e-6)/(1/(dist+1e-6)).sum(axis=1,keepdims=True))+1e-12),axis=1)
            for j in range(k): out[f'{prefix}_k{k}_is{j}']=(lab==j).astype(int)
    path=FEATURE_DIR/'public_failure_followup_features_v1.parquet'
    con.register('follow',out)
    con.execute(f"COPY follow TO '{path}' (FORMAT PARQUET)")
    print(f'wrote {path} rows={len(out)} cols={out.shape[1]}')
    return out

def load_all():
    con=duckdb.connect()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv').assign(is_train=1)
    sample=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv').assign(is_train=0)
    for y in LABELS: sample[y]=np.nan
    df=pd.concat([train,sample],ignore_index=True)
    paths=[FEATURE_DIR/'model_features_v0.parquet', FEATURE_DIR/'ssl_semantic_cluster_features.parquet', FEATURE_DIR/'public_failure_followup_features_v1.parquet']
    for p in paths:
        if p.exists():
            feat=con.execute(f"select * from read_parquet('{p}')").df()
            dup=[c for c in feat.columns if c in df.columns and c not in KEYS]
            if dup: feat=feat.rename(columns={c:f'{c}__{p.stem}' for c in dup})
            df=df.merge(feat,on=KEYS,how='left')
    return df

def base_subset(all_cols, subset):
    if subset=='semantic_only':
        return [c for c in all_cols if any(k in c for k in ('hr_','gps_','app_','wifi_','ble_','amb_')) and not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','q2lr_','q1qual_','s4evt_','cnproto_','q2proto_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='no_flat_hourly':
        return [c for c in all_cols if not c.startswith(('h','topapp_','topamb_','q2x_','s4x_','q2lr_','q1qual_','s4evt_','cnproto_','q2proto_','cn_h','day_h','q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_')) and '__dev_' not in c and '__prev_' not in c and '__weekday' not in c]
    if subset=='sleep_plus_s4x':
        return [c for c in all_cols if (c.startswith('s4x_') or any(k in c for k in ('sleep','quiet_','screenoff_','late_','dark_','bright_'))) and not c.startswith(('q3x_','q1x_','qpatch_','qcarry_','sslcl_','ext_','psw_','pswp_','q1qual_','q2lr_','s4evt_','cnproto_','q2proto_'))]
    if subset=='day_flat': return [c for c in all_cols if c.startswith('day_h')]
    if subset=='dino_k4_cluster': return [c for c in all_cols if c.startswith('sslcl_dino_temporal_k4_')]
    if subset=='q1qual': return [c for c in all_cols if c.startswith('q1qual_')]
    if subset=='q1qual+semantic': return base_subset(all_cols,'q1qual')+base_subset(all_cols,'semantic_only')
    if subset=='q1qual+cnproto': return base_subset(all_cols,'q1qual')+[c for c in all_cols if c.startswith('cnproto_')]
    if subset=='q1qual+semantic+cnproto': return base_subset(all_cols,'q1qual')+base_subset(all_cols,'semantic_only')+[c for c in all_cols if c.startswith('cnproto_')]
    if subset=='q2lr': return [c for c in all_cols if c.startswith('q2lr_')]
    if subset=='q2lr+day_flat': return base_subset(all_cols,'q2lr')+base_subset(all_cols,'day_flat')
    if subset=='q2lr+q2proto': return base_subset(all_cols,'q2lr')+[c for c in all_cols if c.startswith('q2proto_')]
    if subset=='q2lr+day_flat+q2proto': return base_subset(all_cols,'q2lr')+base_subset(all_cols,'day_flat')+[c for c in all_cols if c.startswith('q2proto_')]
    if subset=='s4evt': return [c for c in all_cols if c.startswith('s4evt_')]
    if subset=='s4evt+sleep': return base_subset(all_cols,'s4evt')+base_subset(all_cols,'sleep_plus_s4x')
    if subset=='s4evt+cnproto': return base_subset(all_cols,'s4evt')+[c for c in all_cols if c.startswith('cnproto_')]
    if subset=='s4evt+sleep+cnproto': return base_subset(all_cols,'s4evt')+base_subset(all_cols,'sleep_plus_s4x')+[c for c in all_cols if c.startswith('cnproto_')]
    raise ValueError(subset)

def valid_cols(df, cols):
    out=[]; train=df['is_train'].eq(1)
    seen=set()
    for c in cols:
        if c in seen or c not in df.columns: continue
        seen.add(c)
        s=pd.to_numeric(df.loc[train,c], errors='coerce')
        if s.notna().sum()>20 and s.nunique(dropna=True)>1: out.append(c)
    return out

def make_pipe(k,C,ncols):
    return Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=min(k,ncols))),('scale',RobustScaler()),('clf',LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42))])

def eval_config(df, cfg, name, write_oof=True):
    all_cols=[c for c in df.columns if c not in DROP]
    col_cache={}
    rows=[]; oofs=[]; selected={}
    for fold in folds():
        valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
        valid_mask=(df['is_train'].eq(1) & df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1)).to_numpy()
        train_mask=(df['is_train'].eq(1) & ~valid_mask).to_numpy()
        tmp=df.loc[valid_mask,['subject_id','lifelog_date']+LABELS].copy()
        scores={}
        for y,(subset,k,C) in cfg.items():
            if subset not in col_cache: col_cache[subset]=valid_cols(df,base_subset(all_cols,subset))
            cols=col_cache[subset]
            pipe=make_pipe(k,C,len(cols))
            pipe.fit(df.loc[train_mask,cols], df.loc[train_mask,y].astype(int).to_numpy())
            p=np.clip(pipe.predict_proba(df.loc[valid_mask,cols])[:,1],0.05,0.95)
            scores[y]=log_loss(df.loc[valid_mask,y].astype(int).to_numpy(),p,labels=[0,1])
            tmp[f'pred_{y}']=p
            if fold['fold_id']==folds()[0]['fold_id']:
                try:
                    sel=pipe.named_steps['sel'].get_support(indices=True)
                    selected[y]=[cols[i] for i in sel[:min(len(sel),30)]]
                except Exception: pass
        rows.append({'model':name,'fold_id':fold['fold_id'],'mean_logloss':float(np.mean(list(scores.values()))),**{f'logloss_{y}':scores[y] for y in LABELS}})
        oofs.append(tmp)
    res=pd.DataFrame(rows)
    res.to_csv(EXPERIMENT_DIR/f'{name}_results.csv',index=False)
    if write_oof: pd.concat(oofs).to_csv(EXPERIMENT_DIR/f'{name}_oof.csv',index=False)
    (EXPERIMENT_DIR/f'{name}_selected_features.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
    return res

def sweep_targets(df):
    all_cols=[c for c in df.columns if c not in DROP]
    candidates={
        'Q1':['semantic_only','q1qual','q1qual+semantic','q1qual+cnproto','q1qual+semantic+cnproto'],
        'Q2':['day_flat','q2lr','q2lr+day_flat','q2lr+q2proto','q2lr+day_flat+q2proto'],
        'S4':['sleep_plus_s4x','s4evt','s4evt+sleep','s4evt+cnproto','s4evt+sleep+cnproto'],
    }
    grids={'Q1':[(10,0.001),(10,0.003),(15,0.003),(20,0.01),(30,0.01),(50,0.03)],
           'Q2':[(10,0.001),(20,0.003),(20,0.01),(40,0.01),(60,0.03),(100,0.01)],
           'S4':[(10,0.001),(20,0.003),(40,0.003),(80,0.003),(120,0.001),(200,0.003)]}
    out=[]
    for y,subs in candidates.items():
        for subset in subs:
            cols=valid_cols(df,base_subset(all_cols,subset))
            if not cols: continue
            for k,C in grids[y]:
                fold_scores=[]; test_shift=[]
                for fold in folds():
                    valid={(x['subject_id'],x['lifelog_date']) for x in fold['valid_keys']}
                    valid_mask=(df['is_train'].eq(1) & df.apply(lambda r:(r['subject_id'],r['lifelog_date']) in valid, axis=1)).to_numpy()
                    train_mask=(df['is_train'].eq(1) & ~valid_mask).to_numpy()
                    pipe=make_pipe(k,C,len(cols))
                    pipe.fit(df.loc[train_mask,cols], df.loc[train_mask,y].astype(int).to_numpy())
                    p=np.clip(pipe.predict_proba(df.loc[valid_mask,cols])[:,1],0.05,0.95)
                    fold_scores.append(log_loss(df.loc[valid_mask,y].astype(int).to_numpy(),p,labels=[0,1]))
                out.append({'target':y,'subset':subset,'k':k,'C':C,'ncols':len(cols),'mean':float(np.mean(fold_scores)),'std':float(np.std(fold_scores)),**{f'fold{i}':v for i,v in enumerate(fold_scores)}})
    res=pd.DataFrame(out).sort_values(['target','mean'])
    res.to_csv(EXPERIMENT_DIR/'followup_target_sweep_results.csv',index=False)
    print('target sweep best')
    print(res.groupby('target').head(10).to_string(index=False))
    return res

def predict_submission(df,cfg,name):
    all_cols=[c for c in df.columns if c not in DROP]
    train=df['is_train'].eq(1); test=~train
    sub=df.loc[test,ID_COLS].copy().reset_index(drop=True)
    used={}
    for y,(subset,k,C) in cfg.items():
        cols=valid_cols(df,base_subset(all_cols,subset)); used[y]={'subset':subset,'k':k,'C':C,'ncols':len(cols)}
        pipe=make_pipe(k,C,len(cols)); pipe.fit(df.loc[train,cols], df.loc[train,y].astype(int).to_numpy())
        sub[y]=np.clip(pipe.predict_proba(df.loc[test,cols])[:,1],0.05,0.95)
    path=OUT_DIR/f'{name}.csv'; sub.to_csv(path,index=False)
    (EXPERIMENT_DIR/f'{name}_used_features.json').write_text(json.dumps(used,indent=2),encoding='utf-8')
    print('wrote',path,sub.shape)
    return path

def robustness_gate(base_res, cand_res, name):
    rows=[]
    for y in LABELS:
        b=base_res[f'logloss_{y}'].to_numpy(); c=cand_res[f'logloss_{y}'].to_numpy(); d=c-b
        rows.append({'target':y,'base_mean':float(b.mean()),'cand_mean':float(c.mean()),'delta':float(d.mean()),'delta_std':float(d.std()),'wins':int((d<0).sum()),'max_worse':float(d.max()),'pass': bool((d.mean()<0) and (d.max()<=0.01))})
    gate=pd.DataFrame(rows)
    gate.to_csv(EXPERIMENT_DIR/f'{name}_robustness_gate.csv',index=False)
    return gate

def main():
    ensure_dirs()
    build_followup_features()
    df=load_all()
    base_res=eval_config(df,BASE_CFG,'followup_base_v4_recheck')
    sweep=sweep_targets(df)
    # Build a conservative followup config: replace only targets that beat base mean, win >=2 folds, max_worse <=0.01
    cfg=dict(BASE_CFG); chosen={}
    for y in ['Q1','Q2','S4']:
        bmean=base_res[f'logloss_{y}'].mean()
        sub=sweep[sweep.target==y].copy()
        ok=[]
        for _,r in sub.iterrows():
            foldscores=np.array([r['fold0'],r['fold1'],r['fold2']])
            # align base fold order
            basefold=base_res[f'logloss_{y}'].to_numpy()
            delta=foldscores-basefold
            if r['mean'] < bmean and (delta<0).sum()>=2 and delta.max()<=0.01:
                ok.append((r['mean']+0.5*r['std'],r,delta))
        if ok:
            _,r,delta=sorted(ok,key=lambda x:x[0])[0]
            cfg[y]=(r['subset'],int(r['k']),float(r['C']))
            chosen[y]={'subset':r['subset'],'k':int(r['k']),'C':float(r['C']),'mean':float(r['mean']),'delta':delta.tolist()}
    cand_res=eval_config(df,cfg,'followup_stability_selected')
    gate=robustness_gate(base_res,cand_res,'followup_stability_selected')
    predict_submission(df,cfg,'submission_followup_stability_selected_prob')
    report={
        'base_mean':float(base_res['mean_logloss'].mean()),
        'candidate_mean':float(cand_res['mean_logloss'].mean()),
        'chosen':chosen,
        'gate':gate.to_dict(orient='records'),
    }
    (EXPERIMENT_DIR/'followup_public_failure_summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
