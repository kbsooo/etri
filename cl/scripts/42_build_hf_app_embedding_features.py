#!/usr/bin/env python3
from __future__ import annotations
import re, sys
from pathlib import Path
import duckdb, numpy as np, pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, FEATURE_DIR, ITEM_DIR, ensure_dirs

MODEL_NAME='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
PROTOTYPES={
 'social_chat':'카카오톡 메신저 채팅 문자 DM telegram line discord instagram facebook social message',
 'browser_search_news':'네이버 chrome browser google daum web internet search news reddit information',
 'video_music_entertainment':'youtube netflix tiktok music spotify melon video streaming game entertainment',
 'finance_shopping':'토스 toss banking bank card payment finance shopping coupang market pay',
 'phone_system':'전화 통화 contacts settings samsung system launcher keyboard camera gallery utilities',
 'study_work_productivity':'calendar notion docs office pdf email gmail zoom teams slack study book work',
 'health_fitness':'health fitbit samsung health walk pedometer exercise sleep meditation workout',
 'transport_map':'map navigation kakao metro bus taxi tmap uber travel gps transport',
}
WINDOWS={'all':(0,24),'night':(0,6),'morning':(6,12),'day':(12,18),'evening':(18,24),'late':(21,24),'sleepwin':(21,30)}

def clean(x):
    x=str(x or '').strip().lower().replace('\xa0',' ')
    return re.sub(r'\s+',' ',x)

def entropy(arr):
    arr=np.asarray(arr,dtype=float); s=arr.sum()
    if s<=0: return 0.0
    p=arr[arr>0]/s
    return float(-(p*np.log(p)).sum())

def explode_usage():
    con=duckdb.connect()
    usage=con.execute(f"select * from read_parquet('{ITEM_DIR/'ch2025_mUsageStats.parquet'}')").df()
    rows=[]
    for sid,ts,stats in usage[['subject_id','timestamp','m_usage_stats']].itertuples(index=False):
        if stats is None: continue
        for item in stats:
            if not isinstance(item,dict): continue
            app=clean(item.get('app_name',''))
            try: total=float(item.get('total_time',0) or 0)
            except Exception: total=0.0
            if app and total>0: rows.append((sid,pd.Timestamp(ts),app,total))
    return pd.DataFrame(rows,columns=['subject_id','timestamp','app_name','total_time'])

def main():
    ensure_dirs()
    train=pd.read_csv(DATA_DIR/'ch2026_metrics_train.csv'); test=pd.read_csv(DATA_DIR/'ch2026_submission_sample.csv')
    keys=pd.concat([train[['subject_id','lifelog_date']],test[['subject_id','lifelog_date']]],ignore_index=True).drop_duplicates()
    keys['lifelog_date']=keys['lifelog_date'].astype(str)
    app=explode_usage(); app['lifelog_date']=app.timestamp.dt.strftime('%Y-%m-%d'); app['hour']=app.timestamp.dt.hour
    apps=sorted(app.app_name.unique())
    model=SentenceTransformer(MODEL_NAME, device='cpu')
    texts=apps+list(PROTOTYPES.values())
    Z=model.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)
    app_Z=np.asarray(Z[:len(apps)],dtype=float); proto_Z=np.asarray(Z[len(apps):],dtype=float)
    proto_names=list(PROTOTYPES.keys())
    dist=pairwise_distances(app_Z, proto_Z, metric='cosine')
    amap=pd.DataFrame({'app_name':apps,'hf_proto':[proto_names[i] for i in dist.argmin(axis=1)],'hf_proto_dist':dist.min(axis=1)})
    for k in [8,16,32,48]:
        kk=min(k,len(apps))
        amap[f'hf_k{k}']=KMeans(n_clusters=kk,random_state=42,n_init=20).fit_predict(app_Z)
    app=app.merge(amap,on='app_name',how='left')
    rows=[]
    for (sid,d),g0 in app.groupby(['subject_id','lifelog_date'],sort=False):
        rec={'subject_id':sid,'lifelog_date':d}
        for w,(lo,hi) in WINDOWS.items():
            if hi<=24: g=g0[(g0.hour>=lo)&(g0.hour<hi)]
            else: g=g0[(g0.hour>=lo)|(g0.hour<(hi-24))]
            total=float(g.total_time.sum())
            rec[f'ext_hfapp_{w}_total_time']=total
            rec[f'ext_hfapp_{w}_unique_apps']=float(g.app_name.nunique())
            rec[f'ext_hfapp_{w}_event_count']=float(len(g))
            rec[f'ext_hfapp_{w}_app_entropy']=entropy(g.groupby('app_name').total_time.sum().values) if len(g) else 0.0
            rec[f'ext_hfapp_{w}_proto_entropy']=entropy(g.groupby('hf_proto').total_time.sum().values) if len(g) else 0.0
            rec[f'ext_hfapp_{w}_mean_proto_dist']=float(np.average(g.hf_proto_dist,weights=g.total_time)) if total>0 else 0.0
            if len(g):
                # weighted average of neural app-name embedding dims, compact first 16 dims
                weights=g.total_time.to_numpy(); ix=[apps.index(a) for a in g.app_name]
                emb=np.average(app_Z[ix,:16],axis=0,weights=weights)
            else: emb=np.zeros(16)
            for j,v in enumerate(emb): rec[f'ext_hfapp_{w}_emb{j:02d}']=float(v)
            for pn in proto_names:
                val=float(g.loc[g.hf_proto==pn,'total_time'].sum()) if len(g) else 0.0
                rec[f'ext_hfapp_{w}_proto_{pn}_time']=val
                rec[f'ext_hfapp_{w}_proto_{pn}_share']=val/total if total>0 else 0.0
            for k in [8,16,32,48]:
                counts=g.groupby(f'hf_k{k}').total_time.sum() if len(g) else pd.Series(dtype=float)
                rec[f'ext_hfapp_{w}_k{k}_entropy']=entropy(counts.values) if len(counts) else 0.0
                rec[f'ext_hfapp_{w}_k{k}_dominance']=float(counts.max()/total) if total>0 and len(counts) else 0.0
        rows.append(rec)
    feat=keys.merge(pd.DataFrame(rows),on=['subject_id','lifelog_date'],how='left').fillna(0.0)
    base_cols=[c for c in feat.columns if c not in ['subject_id','lifelog_date']]
    for c in list(base_cols):
        vals=pd.to_numeric(feat[c],errors='coerce')
        if vals.nunique(dropna=True)>1:
            mu=feat.groupby('subject_id')[c].transform('mean')
            sd=feat.groupby('subject_id')[c].transform('std').replace(0,np.nan)
            feat[f'{c}__subj_delta']=vals-mu
            feat[f'{c}__subj_z']=((vals-mu)/sd).fillna(0.0)
    feat.to_parquet(FEATURE_DIR/'external_hf_app_embedding_features_v1.parquet',index=False)
    amap.to_csv(FEATURE_DIR/'external_hf_app_embedding_app_map_v1.csv',index=False)
    print('wrote', FEATURE_DIR/'external_hf_app_embedding_features_v1.parquet', feat.shape, 'apps', len(apps), 'model', MODEL_NAME)

if __name__=='__main__': main()
