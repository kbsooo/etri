#!/usr/bin/env python3
"""Compare augmentation ideas for CoLa-inspired SSL day latents.

No submission is generated.

We compare several tiny self-supervised augmentation recipes on 700 day rows:
- gaussian denoising only
- feature dropout
- time-block masking on hourly features
- small hour jitter on hourly features
- multi-view consistency between two corrupted views

Output: fold-level anchor+latent probe deltas and a short verdict. Negative delta
means the augmented latent helped over subject/day anchor.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEATURES = ROOT / "features"
EXP = ROOT / "experiments"
OUT = ROOT / "outputs"
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
SEED = 20260525
DEVICE = "cpu"


def seed_all(seed=SEED):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


class TinyAE(nn.Module):
    def __init__(self, d, z=8, h=64, drop=0.05):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(d, h), nn.GELU(), nn.Dropout(drop), nn.Linear(h, z))
        self.dec = nn.Sequential(nn.Linear(z, h), nn.GELU(), nn.Dropout(drop), nn.Linear(h, d))
    def forward(self, x):
        z = self.enc(x); return self.dec(z), z


def load_data():
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    for df in (train, test):
        df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
        df["sleep_date"] = pd.to_datetime(df["sleep_date"])
    return train.sort_values(["subject_id","lifelog_date"]).reset_index(drop=True), test.sort_values(["subject_id","lifelog_date"]).reset_index(drop=True)


def load_matrix():
    # Keep hourly flat first so we can apply structured time augmentations.
    paths = [
        "timebin_1h_flat_features.parquet",
        "deep_raw_modality_daily_features.parquet",
        "ssl_hourly_masked_ae_embeddings.parquet",
        "ssl_hourly_dino_temporal_embeddings.parquet",
    ]
    parts=[]
    for name in paths:
        p=FEATURES/name
        if p.exists():
            df=pd.read_parquet(p); df["lifelog_date"]=pd.to_datetime(df["lifelog_date"]); parts.append(df)
    day=parts[0]
    for df in parts[1:]: day=day.merge(df,on=["subject_id","lifelog_date"],how="outer")
    id_cols=["subject_id","lifelog_date"]
    num_cols=[c for c in day.columns if c not in id_cols]
    hourly_cols=[c for c in num_cols if c.startswith("h") and len(c)>3 and c[1:3].isdigit()]
    return day.sort_values(id_cols).reset_index(drop=True), num_cols, hourly_cols


def hourly_groups(num_cols, hourly_cols):
    idx_by_hour={h:[] for h in range(24)}
    col_index={c:i for i,c in enumerate(num_cols)}
    for c in hourly_cols:
        h=int(c[1:3]); idx_by_hour[h].append(col_index[c])
    return idx_by_hour


def corrupt(x: torch.Tensor, cfg: Dict, idx_by_hour: Dict[int, List[int]]):
    y=x.clone()
    sigma=cfg.get("sigma",0.15)
    if sigma>0:
        y = y + sigma*torch.randn_like(y)
    feat_drop=cfg.get("feature_dropout",0.0)
    if feat_drop>0:
        y = y * (torch.rand_like(y)>feat_drop).float()
    # time-block mask: same hours across batch but this is okay for tiny SSL.
    block=cfg.get("time_block",0)
    if block>0 and idx_by_hour:
        starts=torch.randint(0,24,(x.shape[0],),device=x.device)
        for i,s in enumerate(starts.tolist()):
            ids=[]
            for dh in range(block): ids.extend(idx_by_hour[(s+dh)%24])
            if ids: y[i, ids]=0.0
    # hour jitter: roll hourly feature groups by -1/0/+1 for each row.
    if cfg.get("hour_jitter",False) and idx_by_hour:
        y2=y.clone()
        shifts=torch.randint(-1,2,(x.shape[0],),device=x.device).tolist()
        for i,sh in enumerate(shifts):
            if sh==0: continue
            for h in range(24):
                src=idx_by_hour[h]; dst=idx_by_hour[(h+sh)%24]
                if src and dst and len(src)==len(dst): y2[i,dst]=y[i,src]
        y=y2
    return y


def train_latent(day, num_cols, hourly_cols, name, cfg):
    Xraw=day[num_cols].replace([np.inf,-np.inf],np.nan).astype(float)
    prep=Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    X=prep.fit_transform(Xraw).astype(np.float32)
    idx_by_hour=hourly_groups(num_cols,hourly_cols)
    seed_all(SEED + abs(hash(name))%10000)
    model=TinyAE(X.shape[1],z=8,h=64,drop=0.05).to(DEVICE)
    opt=torch.optim.AdamW(model.parameters(),lr=2e-3,weight_decay=2e-4)
    xt=torch.tensor(X,device=DEVICE)
    best=None; best_loss=1e9; stale=0
    consistency=cfg.get("consistency",0.0)
    for ep in range(650):
        model.train(); opt.zero_grad()
        x1=corrupt(xt,cfg,idx_by_hour)
        rec1,z1=model(x1)
        loss=nn.functional.mse_loss(rec1,xt) + 1e-3*z1.pow(2).mean()
        if consistency>0:
            x2=corrupt(xt,cfg,idx_by_hour)
            rec2,z2=model(x2)
            zn1=(z1-z1.mean(0))/(z1.std(0)+1e-6); zn2=(z2-z2.mean(0))/(z2.std(0)+1e-6)
            loss = loss + consistency*nn.functional.mse_loss(zn1,zn2) + 0.25*nn.functional.mse_loss(rec2,xt)
        loss.backward(); opt.step()
        with torch.no_grad():
            model.eval(); rec,z=model(xt); clean_loss=nn.functional.mse_loss(rec,xt).item()
        if clean_loss < best_loss-1e-5:
            best_loss=clean_loss; best={k:v.detach().cpu().clone() for k,v in model.state_dict().items()}; stale=0
        else:
            stale+=1
            if ep>250 and stale>100: break
    if best: model.load_state_dict(best)
    model.eval()
    with torch.no_grad():
        rec,z=model(xt); rec=rec.cpu().numpy(); z=z.cpu().numpy()
    err=(rec-X)**2
    out=day[["subject_id","lifelog_date"]].copy()
    prefix=f"aug_{name}"
    for j in range(z.shape[1]): out[f"{prefix}_z{j:02d}"]=z[:,j]
    out[f"{prefix}_recon_mse"]=err.mean(1)
    out[f"{prefix}_recon_p90_abs"]=np.quantile(np.abs(rec-X),0.90,axis=1)
    for c in [c for c in out.columns if c.startswith(prefix)]:
        mu=out.groupby("subject_id")[c].transform("mean"); sd=out.groupby("subject_id")[c].transform("std").replace(0,np.nan)
        out[c+"__subj_z"]=((out[c]-mu)/sd).fillna(0.0)
    return out, {"config":name,"best_recon_mse":float(best_loss),"n_features":int(X.shape[1])}


def make_splits(train):
    splits=[]
    fpath=OUT/"validation/folds_chrono.json"
    if fpath.exists():
        folds=json.loads(fpath.read_text())["folds"]
        for fold in folds:
            valid={(x["subject_id"],str(x["lifelog_date"])[:10]) for x in fold["valid_keys"]}
            val=train.apply(lambda r:(r.subject_id,pd.Timestamp(r.lifelog_date).strftime("%Y-%m-%d")) in valid,axis=1).to_numpy()
            if val.sum(): splits.append((str(fold["fold_id"]),val))
    for offset in [0,2,4]:
        val=np.zeros(len(train),bool)
        for _,idx in train.groupby("subject_id").groups.items():
            for k,i in enumerate(list(idx)):
                if (k+offset)%7==0 or (k+2*offset)%11==0: val[i]=True
        splits.append((f"pattern_{offset}",val))
    val=np.zeros(len(train),bool)
    for _,idx in train.groupby("subject_id").groups.items():
        ordered=list(idx); val[ordered[-max(3,len(ordered)//8):]]=True
    splits.append(("tail",val))
    return splits


def anchor_frame(df):
    out=df[["subject_id","lifelog_date"]].copy()
    out["dow"]=pd.to_datetime(out.lifelog_date).dt.dayofweek.astype(str)
    out["day_rank_subj"]=df.groupby("subject_id")["lifelog_date"].rank(method="first")
    out["day_rank_subj_z"]=out.groupby(df.subject_id)["day_rank_subj"].transform(lambda s:(s-s.mean())/(s.std() or 1.0)).fillna(0)
    return out


def eval_one(train, latent, config):
    df=train.merge(latent,on=["subject_id","lifelog_date"],how="left")
    anc=anchor_frame(df)
    lcols=[c for c in latent.columns if c.startswith(f"aug_{config}")]
    rows=[]
    for split,val_mask in make_splits(train):
        tr=~val_mask
        X_anchor=pd.get_dummies(anc[["subject_id","dow","day_rank_subj_z"]],columns=["subject_id","dow"])
        X_lat=pd.concat([anc[["subject_id","dow","day_rank_subj_z"]],df[lcols]],axis=1)
        X_lat=pd.get_dummies(X_lat,columns=["subject_id","dow"])
        for y in LABELS:
            ytr=df.loc[tr,y].astype(int).to_numpy(); yva=df.loc[val_mask,y].astype(int).to_numpy()
            if len(np.unique(ytr))<2 or len(np.unique(yva))<2: continue
            losses={}
            for mname,X in [("anchor",X_anchor),("aug",X_lat)]:
                pipe=Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler(with_mean=False)),("clf",LogisticRegression(C=0.03,solver="liblinear",max_iter=1000,random_state=SEED))])
                pipe.fit(X.loc[tr],ytr)
                p=np.clip(pipe.predict_proba(X.loc[val_mask])[:,1],0.02,0.98)
                losses[mname]=log_loss(yva,p,labels=[0,1])
            rows.append({"config":config,"split":split,"target":y,"anchor_loss":losses["anchor"],"aug_loss":losses["aug"],"delta_aug_minus_anchor":losses["aug"]-losses["anchor"]})
    return pd.DataFrame(rows)


def write_report(ev, infos):
    summary=ev.groupby(["config","target"])["delta_aug_minus_anchor"].agg(["mean","median","min","max","count"]).reset_index()
    overall=ev.groupby("config")["delta_aug_minus_anchor"].agg(["mean","median","min","max","count"]).reset_index().sort_values("mean")
    s4=summary[summary.target.eq("S4")].sort_values("mean")
    s2=summary[summary.target.eq("S2")].sort_values("mean")
    lines=[]
    lines.append("# Augmented CoLa SSL signal hunt\n")
    lines.append("No submission files were created. Negative delta means anchor+augmented latent beat subject/day anchor.\n")
    lines.append("## Config reconstruction info\n")
    lines.append(pd.DataFrame(infos).to_markdown(index=False,floatfmt=".4f"))
    lines.append("\n## Overall deltas\n")
    lines.append(overall.to_markdown(index=False,floatfmt=".4f"))
    lines.append("\n## S4 ranking\n")
    lines.append(s4.to_markdown(index=False,floatfmt=".4f"))
    lines.append("\n## S2 ranking\n")
    lines.append(s2.to_markdown(index=False,floatfmt=".4f"))
    lines.append("\n## All target/config deltas\n")
    lines.append(summary.sort_values(["target","mean"]).to_markdown(index=False,floatfmt=".4f"))
    best_s4=s4.iloc[0]
    lines.append("\n## Verdict\n")
    lines.append(f"- Best S4 config: `{best_s4.config}` with mean delta `{best_s4['mean']:.4f}`.")
    if best_s4['mean'] < -0.006:
        lines.append("- S4 augmentation signal strengthened vs the previous plain CoLa run; next step is row-shift diagnostic for this best config.")
    elif best_s4['mean'] < -0.002:
        lines.append("- S4 remains weakly alive, but not enough for broad trust; use only as row-level microscope.")
    else:
        lines.append("- Augmentation did not produce a useful S4 latent; do not pursue diffusion/SSL further without new raw sequence features.")
    (EXP/"augmented_cola_ssl_signal_hunt_report.md").write_text("\n".join(lines))


def main():
    EXP.mkdir(exist_ok=True); FEATURES.mkdir(exist_ok=True)
    train,_=load_data(); day,num_cols,hourly_cols=load_matrix()
    configs={
        "gauss": {"sigma":0.20},
        "dropout": {"sigma":0.10,"feature_dropout":0.12},
        "timeblock": {"sigma":0.10,"time_block":3},
        "jitter": {"sigma":0.08,"hour_jitter":True},
        "multiview": {"sigma":0.12,"feature_dropout":0.08,"time_block":2,"consistency":0.35},
        "heavy_multiview": {"sigma":0.20,"feature_dropout":0.15,"time_block":4,"hour_jitter":True,"consistency":0.50},
    }
    all_ev=[]; infos=[]
    for name,cfg in configs.items():
        print("training",name,cfg,flush=True)
        latent,info=train_latent(day,num_cols,hourly_cols,name,cfg)
        latent.to_parquet(FEATURES/f"augmented_cola_{name}_latent_v1.parquet",index=False)
        ev=eval_one(train,latent,name)
        ev.to_csv(EXP/f"augmented_cola_{name}_eval.csv",index=False)
        all_ev.append(ev); infos.append(info)
        print(ev.groupby("target")["delta_aug_minus_anchor"].mean().sort_values().to_string(),flush=True)
    ev=pd.concat(all_ev,ignore_index=True)
    ev.to_csv(EXP/"augmented_cola_ssl_signal_eval_all.csv",index=False)
    write_report(ev,infos)
    print("wrote",EXP/"augmented_cola_ssl_signal_hunt_report.md")
    print(ev.groupby(["config","target"])["delta_aug_minus_anchor"].mean().reset_index().sort_values(["target","delta_aug_minus_anchor"]).to_string(index=False))

if __name__ == "__main__":
    main()
