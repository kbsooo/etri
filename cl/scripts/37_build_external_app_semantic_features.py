#!/usr/bin/env python3
from __future__ import annotations
import math, re, sys
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ITEM_DIR, ensure_dirs

# External-model-inspired app semantics without sending private app strings to external APIs.
# We use a local multilingual character n-gram embedding space seeded by public Korean/English
# app category prototypes. This is not a neural HF model, but it is an external semantic prior
# over app names and is reproducible/offline. If sentence-transformers is available, the script
# can be extended to replace embed_texts() with a HF encoder.
PROTOTYPES = {
    'social_chat': ['카카오톡 messenger chat dm message telegram line discord instagram facebook social'],
    'browser_search_news': ['NAVER chrome browser search news google daum web internet reddit'],
    'video_music_entertainment': ['youtube netflix tiktok music spotify melon video streaming game entertainment'],
    'finance_shopping': ['토스 toss banking bank card payment finance shopping coupang market pay'],
    'phone_system': ['전화 통화 contacts one ui settings samsung system launcher keyboard camera gallery'],
    'study_work_productivity': ['calendar notion docs office pdf email gmail zoom teams slack study bible book'],
    'health_fitness': ['health fitbit samsung health walk pedometer exercise sleep meditation workout'],
    'transport_map': ['map navigation kakao metro bus taxi tmap uber travel gps'],
}
WINDOWS = {
    'all': (0,24), 'night': (0,6), 'morning': (6,12), 'day': (12,18), 'evening': (18,24), 'late': (21,24), 'sleepwin': (21,30)
}

def clean_app(x: str) -> str:
    x = str(x or '').strip().lower().replace('\xa0',' ')
    x = re.sub(r'\s+', ' ', x)
    return x

def entropy(arr):
    arr = np.asarray(arr, dtype=float)
    s = arr.sum()
    if s <= 0: return 0.0
    p = arr[arr>0] / s
    return float(-(p*np.log(p)).sum())

def build_embedding(apps):
    corpus = list(apps) + [v[0] for v in PROTOTYPES.values()]
    vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,5), min_df=1, sublinear_tf=True, norm='l2')
    X = vec.fit_transform(corpus)
    n_comp = min(48, max(2, X.shape[1]-1), max(2, X.shape[0]-1))
    svd = TruncatedSVD(n_components=n_comp, random_state=42)
    Z = svd.fit_transform(X)
    # l2 normalize
    Z = Z / np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-12)
    app_Z = Z[:len(apps)]
    proto_Z = Z[len(apps):]
    return app_Z, proto_Z

def explode_usage():
    con = duckdb.connect()
    usage = con.execute(f"select * from read_parquet('{ITEM_DIR/'ch2025_mUsageStats.parquet'}')").df()
    rows=[]
    for sid, ts, stats in usage[['subject_id','timestamp','m_usage_stats']].itertuples(index=False):
        if stats is None: continue
        for item in stats:
            if not isinstance(item, dict): continue
            app = clean_app(item.get('app_name',''))
            try: total = float(item.get('total_time',0) or 0)
            except Exception: total = 0.0
            if app and total > 0:
                rows.append((sid, pd.Timestamp(ts), app, total))
    return pd.DataFrame(rows, columns=['subject_id','timestamp','app_name','total_time'])

def main():
    ensure_dirs()
    train = pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv')
    test = pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')
    keys = pd.concat([train[['subject_id','lifelog_date']], test[['subject_id','lifelog_date']]], ignore_index=True).drop_duplicates()
    app = explode_usage()
    if app.empty:
        raise RuntimeError('no usage rows')
    app['lifelog_date'] = app['timestamp'].dt.strftime('%Y-%m-%d')
    app['hour'] = app['timestamp'].dt.hour
    apps = sorted(app['app_name'].unique())
    app_Z, proto_Z = build_embedding(apps)
    proto_names = list(PROTOTYPES.keys())
    dist = pairwise_distances(app_Z, proto_Z, metric='cosine')
    proto = pd.DataFrame({
        'app_name': apps,
        'app_sem_proto': [proto_names[i] for i in dist.argmin(axis=1)],
        'app_sem_proto_dist': dist.min(axis=1),
    })
    # KMeans over app name embedding as data-driven semantic clusters.
    for k in [8,16,32]:
        km = KMeans(n_clusters=min(k, len(apps)), random_state=42, n_init=20)
        proto[f'app_sem_k{k}'] = km.fit_predict(app_Z)
    app = app.merge(proto, on='app_name', how='left')
    rows=[]
    for (sid, d), g0 in app.groupby(['subject_id','lifelog_date'], sort=False):
        rec={'subject_id':sid, 'lifelog_date':d}
        for w,(lo,hi) in WINDOWS.items():
            if hi <= 24:
                g = g0[(g0.hour>=lo)&(g0.hour<hi)]
            else:
                g = g0[(g0.hour>=lo)|(g0.hour<(hi-24))]
            total = float(g.total_time.sum())
            rec[f'ext_appsem_{w}_total_time'] = total
            rec[f'ext_appsem_{w}_unique_apps'] = float(g.app_name.nunique())
            rec[f'ext_appsem_{w}_event_count'] = float(len(g))
            rec[f'ext_appsem_{w}_app_entropy'] = entropy(g.groupby('app_name').total_time.sum().values) if len(g) else 0.0
            rec[f'ext_appsem_{w}_proto_entropy'] = entropy(g.groupby('app_sem_proto').total_time.sum().values) if len(g) else 0.0
            rec[f'ext_appsem_{w}_mean_proto_dist'] = float(np.average(g.app_sem_proto_dist, weights=g.total_time)) if total>0 else 0.0
            for pn in proto_names:
                val = float(g.loc[g.app_sem_proto==pn, 'total_time'].sum()) if len(g) else 0.0
                rec[f'ext_appsem_{w}_proto_{pn}_time'] = val
                rec[f'ext_appsem_{w}_proto_{pn}_share'] = val/total if total>0 else 0.0
            for k in [8,16,32]:
                counts = g.groupby(f'app_sem_k{k}').total_time.sum() if len(g) else pd.Series(dtype=float)
                rec[f'ext_appsem_{w}_k{k}_entropy'] = entropy(counts.values) if len(counts) else 0.0
                rec[f'ext_appsem_{w}_k{k}_dominance'] = float(counts.max()/total) if total>0 and len(counts) else 0.0
        rows.append(rec)
    feat = keys.merge(pd.DataFrame(rows), on=['subject_id','lifelog_date'], how='left').fillna(0.0)
    # subject-normalized app semantic features
    val_cols = [c for c in feat.columns if c not in ['subject_id','lifelog_date']]
    for c in list(val_cols):
        vals = pd.to_numeric(feat[c], errors='coerce')
        if vals.nunique(dropna=True)>1:
            mu = feat.groupby('subject_id')[c].transform('mean')
            sd = feat.groupby('subject_id')[c].transform('std').replace(0, np.nan)
            feat[f'{c}__subj_delta'] = vals - mu
            feat[f'{c}__subj_z'] = ((vals - mu) / sd).fillna(0.0)
    feat.to_parquet(FEATURE_DIR/'external_app_semantic_features_v1.parquet', index=False)
    proto.to_csv(FEATURE_DIR/'external_app_semantic_app_map_v1.csv', index=False)
    print('wrote', FEATURE_DIR/'external_app_semantic_features_v1.parquet', feat.shape)
    print('app map', FEATURE_DIR/'external_app_semantic_app_map_v1.csv', proto.shape)
    print(feat.head().to_string(index=False))

if __name__ == '__main__':
    main()
