#!/usr/bin/env python3
"""Deep-learning golf for tiny lifelog labels.

Goal: test whether the engineered feature space can benefit from very small
latent neural heads or micro-MoE heads, starting from the fewest parameters.

This is intentionally not a big supervised model. It uses the existing
feature-family selectors, SelectK, fold-local scaling, tiny PyTorch heads, and
strict validation summaries across chrono/testpattern/tail splits.
"""
from __future__ import annotations
import json, math, random, warnings
from pathlib import Path
import importlib.util
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ts', ROOT/'scripts/50_eval_temporal_state_smoothing.py')
ts=importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
LABELS=ts.LABELS; EXP=ROOT/'experiments'; OUT=ROOT/'outputs'
DEVICE='mps' if torch.backends.mps.is_available() else 'cpu'
SEED=42

# Use smaller S4 K for neural heads to avoid too many params. Logistic baseline still uses same input K here.
K_CFG={'Q1':50,'Q2':20,'Q3':10,'S1':20,'S2':20,'S3':20,'S4':60}
C_CFG={'Q1':0.03,'Q2':0.01,'Q3':0.3,'S1':0.1,'S2':0.001,'S3':0.01,'S4':0.003}
SUBSET={y:ts.BASE_CFG[y][0] for y in LABELS}

class LinearHead(nn.Module):
    def __init__(self,d): super().__init__(); self.fc=nn.Linear(d,1)
    def forward(self,x): return self.fc(x).squeeze(-1)

class BottleneckHead(nn.Module):
    def __init__(self,d,z=2,drop=0.05):
        super().__init__(); self.net=nn.Sequential(nn.Linear(d,z),nn.Tanh(),nn.Dropout(drop),nn.Linear(z,1))
    def forward(self,x): return self.net(x).squeeze(-1)

class MicroMoE(nn.Module):
    def __init__(self,d,z=4,e=2,drop=0.05):
        super().__init__(); self.enc=nn.Sequential(nn.Linear(d,z),nn.Tanh(),nn.Dropout(drop)); self.gate=nn.Linear(z,e); self.experts=nn.ModuleList([nn.Linear(z,1) for _ in range(e)])
    def forward(self,x):
        z=self.enc(x); g=torch.softmax(self.gate(z),dim=1); outs=torch.cat([ex(z) for ex in self.experts],dim=1); return (g*outs).sum(dim=1)

def seed_all(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)

def prep_xy(df, known_mask, val_mask, y):
    all_cols=[c for c in df.columns if c not in ts.DROP]
    cols=ts.valid_cols(df, ts.base_subset(all_cols,SUBSET[y]), known_mask)
    k=min(K_CFG[y],len(cols))
    selector=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=k)),('scale',StandardScaler())])
    Xtr=selector.fit_transform(df.loc[known_mask,cols], df.loc[known_mask,y].astype(int).to_numpy()).astype(np.float32)
    Xva=selector.transform(df.loc[val_mask,cols]).astype(np.float32)
    ytr=df.loc[known_mask,y].astype(np.float32).to_numpy(); yva=df.loc[val_mask,y].astype(int).to_numpy()
    return Xtr,ytr,Xva,yva,k,len(cols)

def logistic_baseline(Xtr,ytr,Xva,yva,C):
    clf=LogisticRegression(C=C,solver='liblinear',max_iter=1000,random_state=42)
    clf.fit(Xtr,ytr.astype(int)); p=np.clip(clf.predict_proba(Xva)[:,1],0.02,0.98)
    return log_loss(yva,p,labels=[0,1]),p

def train_torch_model(model_ctor, Xtr,ytr,Xva,yva, seed=0, epochs=280, lr=2e-3, wd=1e-3):
    seed_all(SEED+seed)
    n=len(Xtr); idx=np.arange(n); np.random.shuffle(idx)
    # internal early stopping split; ensure both classes if possible
    nval=max(12,int(0.22*n)); tr_idx=idx[nval:]; es_idx=idx[:nval]
    if len(np.unique(ytr[es_idx]))<2 or len(np.unique(ytr[tr_idx]))<2:
        tr_idx=idx; es_idx=idx
    xt=torch.tensor(Xtr[tr_idx],device=DEVICE); yt=torch.tensor(ytr[tr_idx],device=DEVICE)
    xe=torch.tensor(Xtr[es_idx],device=DEVICE); ye=torch.tensor(ytr[es_idx],device=DEVICE)
    xv=torch.tensor(Xva,device=DEVICE)
    model=model_ctor(Xtr.shape[1]).to(DEVICE)
    # pos_weight stabilizes imbalanced S labels but keep modest.
    pos=max(1.0,float(yt.sum().item())); neg=max(1.0,float(len(yt)-yt.sum().item())); pw=torch.tensor(min(3.0,max(0.33,neg/pos)),device=DEVICE)
    loss_fn=nn.BCEWithLogitsLoss(pos_weight=pw)
    opt=torch.optim.AdamW(model.parameters(),lr=lr,weight_decay=wd)
    best=None; best_loss=math.inf; patience=35; stale=0
    for ep in range(epochs):
        model.train(); opt.zero_grad(); logits=model(xt); loss=loss_fn(logits,yt); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            eloss=nn.functional.binary_cross_entropy_with_logits(model(xe),ye).item()
        if eloss < best_loss-1e-4:
            best_loss=eloss; best={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}; stale=0
        else:
            stale+=1
            if stale>=patience: break
    if best is not None: model.load_state_dict(best)
    model.eval()
    with torch.no_grad():
        p=torch.sigmoid(model(xv)).detach().cpu().numpy()
    p=np.clip(p,0.02,0.98)
    return log_loss(yva,p,labels=[0,1]),p,sum(p.numel() for p in model.parameters())

def get_splits(train, sample):
    splits=[]
    # chrono folds from official local validation
    fpath=OUT/'validation/folds_chrono.json'
    if fpath.exists():
        folds=json.loads(fpath.read_text())['folds']
        for fold in folds:
            valid={(x['subject_id'],str(x['lifelog_date'])[:10]) for x in fold['valid_keys']}
            val_mask=train.apply(lambda r:(r.subject_id,pd.Timestamp(r.lifelog_date).strftime('%Y-%m-%d')) in valid,axis=1).to_numpy()
            if val_mask.sum() > 0:
                splits.append((fold['fold_id'],val_mask))
    for seed in range(3):
        splits.append((f'testpattern_{seed}',ts.make_testpattern_mask(train,sample,seed)))
    splits.append(('tail',ts.make_tail_mask(train)))
    return splits

def run():
    EXP.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    df=ts.load_all(); train=df[df.is_train.eq(1)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True); sample=df[df.is_train.eq(0)].copy().sort_values(['subject_id','sleep_date']).reset_index(drop=True)
    splits=get_splits(train,sample)
    rows=[]; pred_store={}
    model_defs=[
        ('torch_linear', lambda d: LinearHead(d)),
        ('bottleneck_z2', lambda d: BottleneckHead(d,z=2,drop=0.05)),
        ('bottleneck_z4', lambda d: BottleneckHead(d,z=4,drop=0.07)),
        ('bottleneck_z8', lambda d: BottleneckHead(d,z=8,drop=0.10)),
        ('micro_moe_z2_e2', lambda d: MicroMoE(d,z=2,e=2,drop=0.05)),
        ('micro_moe_z4_e2', lambda d: MicroMoE(d,z=4,e=2,drop=0.07)),
        ('micro_moe_z4_e3', lambda d: MicroMoE(d,z=4,e=3,drop=0.07)),
    ]
    for split_id,val_mask in splits:
        known_mask=~val_mask
        for y in LABELS:
            Xtr,ytr,Xva,yva,k,ncols=prep_xy(train,known_mask,val_mask,y)
            bl,pb=logistic_baseline(Xtr,ytr,Xva,yva,C_CFG[y])
            rows.append({'split':split_id,'target':y,'model':'sk_logistic_sameK','seed':-1,'params':k+1,'k':k,'ncols':ncols,'logloss':bl,'base_logloss':bl})
            for mname,ctor in model_defs:
                # two seeds, average later; tiny labels have high variance.
                for seed in [0,1]:
                    try:
                        loss,p,params=train_torch_model(ctor,Xtr,ytr,Xva,yva,seed=seed)
                    except Exception as e:
                        print('ERR',split_id,y,mname,seed,e); continue
                    rows.append({'split':split_id,'target':y,'model':mname,'seed':seed,'params':params,'k':k,'ncols':ncols,'logloss':loss,'base_logloss':bl})
    res=pd.DataFrame(rows)
    res.to_csv(EXP/'tiny_dl_golf_results.csv',index=False)
    print('wrote',EXP/'tiny_dl_golf_results.csv')
    summarize(res)
    make_candidates(train,sample,res)

def summarize(res):
    for group_name,mask in [('chrono',res.split.str.startswith('chrono')),('testpattern',res.split.str.startswith('testpattern')),('tail',res.split.eq('tail')),('all',res.split.notna())]:
        sub=res[mask]
        if len(sub)==0: continue
        print('\n###',group_name)
        summ=sub.groupby(['target','model'])[['logloss','base_logloss','params']].mean().reset_index()
        rows=[]
        for y,g in summ.groupby('target'):
            b=g[g.model.eq('sk_logistic_sameK')].logloss.mean()
            best=g.sort_values('logloss').iloc[0]
            rows.append({'target':y,'best_model':best.model,'loss':best.logloss,'logistic_sameK':b,'delta':best.logloss-b,'params':best.params})
        print(pd.DataFrame(rows).to_string(index=False))

def fit_predict_full(train,sample,y,model_name):
    full=pd.concat([train,sample],ignore_index=True)
    known=np.r_[np.ones(len(train),bool),np.zeros(len(sample),bool)]; query=~known
    Xtr,ytr,Xte,_,k,ncols=prep_xy(full,known,query,y)
    # dummy y true not used returned okay? prep expects y in sample nan -> yva not int fails. implement manually below not use.

def make_candidates(train,sample,res):
    # Select DL model per target only if it beats logistic on testpattern and is not worse on chrono/tail by >0.003.
    # Then generate two candidates: conservative hard-target only and all-selected.
    selected={}
    for y in LABELS:
        candidates=[]
        for m in res.model.unique():
            if m=='sk_logistic_sameK': continue
            vals={}
            for grp,mask in {'tp':res.split.str.startswith('testpattern'),'chrono':res.split.str.startswith('chrono'),'tail':res.split.eq('tail')}.items():
                sub=res[mask & res.target.eq(y)]
                if len(sub)==0: vals[grp]=0; continue
                bm=sub[sub.model.eq('sk_logistic_sameK')].logloss.mean()
                lm=sub[sub.model.eq(m)].logloss.mean()
                vals[grp]=lm-bm
            if vals['tp'] < -0.003 and vals['chrono'] <= 0.006 and vals['tail'] <= 0.006:
                candidates.append((vals['tp']+max(vals['chrono'],0)+max(vals['tail'],0),m,vals))
        if candidates:
            selected[y]=sorted(candidates)[0]
    print('\n### selected for submission gate')
    print(json.dumps({y:{'model':v[1],'deltas':v[2]} for y,v in selected.items()},indent=2))
    # If nothing passes, still write selection json and no-op candidate for audit.
    (EXP/'tiny_dl_golf_selected.json').write_text(json.dumps({y:{'model':v[1],'deltas':v[2]} for y,v in selected.items()},indent=2),encoding='utf-8')
    # Generate predictions for selected models by training on all train. Otherwise base_v4 replicate values.
    base=pd.read_csv(OUT/'submission_base_v4_replicate_prob.csv')
    model_map={
        'torch_linear': lambda d: LinearHead(d),
        'bottleneck_z2': lambda d: BottleneckHead(d,z=2,drop=0.05),
        'bottleneck_z4': lambda d: BottleneckHead(d,z=4,drop=0.07),
        'bottleneck_z8': lambda d: BottleneckHead(d,z=8,drop=0.10),
        'micro_moe_z2_e2': lambda d: MicroMoE(d,z=2,e=2,drop=0.05),
        'micro_moe_z4_e2': lambda d: MicroMoE(d,z=4,e=2,drop=0.07),
        'micro_moe_z4_e3': lambda d: MicroMoE(d,z=4,e=3,drop=0.07),
    }
    # Helper prepare full train/test features without labels in sample
    def transform_full(y):
        full=pd.concat([train,sample],ignore_index=True)
        all_cols=[c for c in full.columns if c not in ts.DROP]
        known=np.r_[np.ones(len(train),bool),np.zeros(len(sample),bool)]; query=~known
        cols=ts.valid_cols(full, ts.base_subset(all_cols,SUBSET[y]), known)
        k=min(K_CFG[y],len(cols)); pipe=Pipeline([('imp',SimpleImputer(strategy='median')),('sel',SelectKBest(f_classif,k=k)),('scale',StandardScaler())])
        Xtr=pipe.fit_transform(full.loc[known,cols], full.loc[known,y].astype(int).to_numpy()).astype(np.float32)
        Xte=pipe.transform(full.loc[query,cols]).astype(np.float32)
        ytr=full.loc[known,y].astype(np.float32).to_numpy()
        return Xtr,ytr,Xte
    sub_all=base.copy(); sub_hard=base.copy(); shifts=[]
    for y,(score,m,vals) in selected.items():
        Xtr,ytr,Xte=transform_full(y)
        preds=[]
        for seed in [0,1,2]:
            seed_all(SEED+seed)
            ctor=model_map[m]
            # Use train as early stop too on full fit; simpler but low-risk by averaging.
            dummy_y=np.zeros(len(Xte),int)
            _,p,_=train_torch_model(ctor,Xtr,ytr,Xte,dummy_y,seed=seed,epochs=320)
            preds.append(p)
        p=np.mean(preds,axis=0)
        sub_all[y]=p
        if y in ['Q1','Q2','S4']:
            sub_hard[y]=p
    for name,sub in [('submission_tiny_dl_golf_selected_prob',sub_all),('submission_tiny_dl_golf_hardtargets_prob',sub_hard)]:
        sub.to_csv(OUT/f'{name}.csv',index=False)
        sh=[]
        for y in LABELS:
            d=np.abs(sub[y].to_numpy()-base[y].to_numpy())
            sh.append({'target':y,'changed_rows':int((d>1e-12).sum()),'mean_abs_delta':float(d.mean()),'max_abs_delta':float(d.max()),'corr_vs_base':float(np.corrcoef(sub[y],base[y])[0,1]) if d.max()>0 else 1.0})
        pd.DataFrame(sh).to_csv(EXP/f'{name}_shift.csv',index=False)
        print('\n### wrote',name)
        print(pd.DataFrame(sh).to_string(index=False))

if __name__=='__main__': run()
