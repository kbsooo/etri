#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import torch
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.cl_common import DATA_DIR, EXPERIMENT_DIR, FEATURE_DIR, LABELS, OUT_DIR, ensure_dirs

SEED = 42
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
CHANNELS = [
    "screen_use_sum_h", "steps_sum_h", "distance_sum_h", "mlight_mean_h", "wlight_mean_h",
    "activity_mean_h", "screen_n_h", "pedo_n_h", "mlight_n_h", "wlight_n_h", "activity_n_h",
]
Q_TARGETS = ["Q1", "Q3"]


def seed_everything(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def folds():
    return json.loads((OUT_DIR / "validation" / "folds_chrono.json").read_text())["folds"]


def load_hourly_tensor():
    con = duckdb.connect()
    tb = con.execute(f"select * from read_parquet('{FEATURE_DIR/'timebin_1h_features.parquet'}')").df()
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv")
    sample = pd.read_csv(DATA_DIR / "ch2026_submission_sample.csv")
    keys = pd.concat([
        train[["subject_id", "lifelog_date"]],
        sample[["subject_id", "lifelog_date"]],
    ], ignore_index=True).drop_duplicates().sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)

    x = np.zeros((len(keys), 24, len(CHANNELS)), dtype=np.float32)
    obs = np.zeros_like(x)
    key_to_i = {(r.subject_id, str(r.lifelog_date)): i for i, r in keys.iterrows()}
    for r in tb.itertuples(index=False):
        key = (getattr(r, "subject_id"), str(getattr(r, "lifelog_date")))
        if key not in key_to_i:
            continue
        h = int(getattr(r, "hour"))
        if h < 0 or h > 23:
            continue
        i = key_to_i[key]
        for j, c in enumerate(CHANNELS):
            v = getattr(r, c, np.nan)
            if pd.notna(v):
                x[i, h, j] = float(v)
                obs[i, h, j] = 1.0

    # Add observed-mask channels, because missingness is behavioral signal in lifelog data.
    x_full = np.concatenate([x, obs], axis=2)
    keys["lifelog_date"] = keys["lifelog_date"].astype(str)
    return keys, x_full


def standardize_tensor(x: np.ndarray):
    vals = x.reshape(-1, x.shape[-1])
    mu = vals.mean(axis=0, keepdims=True)
    sd = vals.std(axis=0, keepdims=True)
    sd[sd < 1e-6] = 1.0
    xs = ((vals - mu) / sd).reshape(x.shape).astype(np.float32)
    return xs, mu.astype(np.float32), sd.astype(np.float32)


class MaskedAE(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 48):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 192), nn.LayerNorm(192), nn.GELU(), nn.Dropout(0.10),
            nn.Linear(192, 96), nn.GELU(),
            nn.Linear(96, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 96), nn.GELU(),
            nn.Linear(96, 192), nn.GELU(),
            nn.Linear(192, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z), z


class EncoderProj(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 48, proj_dim: int = 64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 192), nn.LayerNorm(192), nn.GELU(), nn.Dropout(0.10),
            nn.Linear(192, 96), nn.GELU(),
            nn.Linear(96, latent_dim),
        )
        self.head = nn.Sequential(
            nn.Linear(latent_dim, 96), nn.GELU(),
            nn.Linear(96, proj_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        p = self.head(z)
        return z, p


def make_masked_view(x: torch.Tensor, mask_prob: float = 0.25, noise: float = 0.03):
    m = (torch.rand_like(x) > mask_prob).float()
    return x * m + noise * torch.randn_like(x)


def make_temporal_view(x: torch.Tensor):
    # DINO-like local/global views for day tokens: keep a semantic window, drop other hours.
    b, flat = x.shape
    t = x.view(b, 24, -1).clone()
    candidates = [(0, 24), (6, 12), (12, 18), (18, 24), (21, 24), (0, 6), (21, 30)]
    out = torch.zeros_like(t)
    for i in range(b):
        s, e = random.choice(candidates)
        if e <= 24:
            out[i, s:e] = t[i, s:e]
        else:
            out[i, s:24] = t[i, s:24]
            out[i, 0:e-24] = t[i, 0:e-24]
        # modality dropout: drop random original channels, keep mask channels more often.
        c = t.shape[-1]
        keep = (torch.rand(c, device=t.device) > 0.20).float()
        keep[c//2:] = (torch.rand(c//2, device=t.device) > 0.05).float()
        out[i] *= keep
    out += 0.02 * torch.randn_like(out)
    return out.reshape(b, flat)


def train_masked_ae(x_flat: np.ndarray, epochs: int = 450, latent_dim: int = 48):
    seed_everything()
    xt = torch.tensor(x_flat, dtype=torch.float32, device=DEVICE)
    loader = DataLoader(TensorDataset(xt), batch_size=min(128, len(xt)), shuffle=True)
    model = MaskedAE(x_flat.shape[1], latent_dim=latent_dim).to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=1e-4)
    best_loss = math.inf
    best_state = None
    for ep in range(epochs):
        model.train(); losses = []
        for (xb,) in loader:
            xin = make_masked_view(xb, 0.30, 0.02)
            recon, _ = model(xin)
            loss = nn.functional.smooth_l1_loss(recon, xb)
            opt.zero_grad(); loss.backward(); opt.step()
            losses.append(float(loss.detach().cpu()))
        avg = float(np.mean(losses))
        if avg < best_loss:
            best_loss = avg
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    if best_state:
        model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        _, z = model(xt)
    return z.cpu().numpy().astype(np.float32), best_loss


def dino_loss(student_logits, teacher_logits, temp_s=0.2, temp_t=0.07):
    s_logp = nn.functional.log_softmax(student_logits / temp_s, dim=1)
    t_p = nn.functional.softmax(teacher_logits / temp_t, dim=1).detach()
    return -(t_p * s_logp).sum(dim=1).mean()


def train_dino_inspired(x_flat: np.ndarray, epochs: int = 500, latent_dim: int = 48):
    seed_everything(SEED + 1)
    xt = torch.tensor(x_flat, dtype=torch.float32, device=DEVICE)
    loader = DataLoader(TensorDataset(xt), batch_size=min(128, len(xt)), shuffle=True)
    student = EncoderProj(x_flat.shape[1], latent_dim=latent_dim, proj_dim=64).to(DEVICE)
    teacher = EncoderProj(x_flat.shape[1], latent_dim=latent_dim, proj_dim=64).to(DEVICE)
    teacher.load_state_dict(student.state_dict())
    for p in teacher.parameters():
        p.requires_grad_(False)
    opt = torch.optim.AdamW(student.parameters(), lr=1e-3, weight_decay=1e-4)
    ema = 0.99
    last_loss = math.nan
    for ep in range(epochs):
        student.train(); losses=[]
        for (xb,) in loader:
            v1 = make_temporal_view(xb)
            v2 = make_temporal_view(xb)
            with torch.no_grad():
                _, tg = teacher(xb)  # teacher sees global/full day view
            _, s1 = student(v1)
            _, s2 = student(v2)
            loss = 0.5 * (dino_loss(s1, tg) + dino_loss(s2, tg))
            # small variance regularizer to discourage degenerate constant embeddings.
            z1 = nn.functional.normalize(s1, dim=1)
            z2 = nn.functional.normalize(s2, dim=1)
            loss = loss + 0.05 * (1.0 - (z1.std(dim=0).mean() + z2.std(dim=0).mean()))
            opt.zero_grad(); loss.backward(); opt.step()
            with torch.no_grad():
                for ps, pt in zip(student.parameters(), teacher.parameters()):
                    pt.data.mul_(ema).add_(ps.data, alpha=1-ema)
            losses.append(float(loss.detach().cpu()))
        last_loss = float(np.mean(losses))
    teacher.eval()
    with torch.no_grad():
        z, _ = teacher(xt)
    return z.cpu().numpy().astype(np.float32), last_loss


def evaluate_embeddings(keys: pd.DataFrame, emb: np.ndarray, method: str):
    train = pd.read_csv(DATA_DIR / "ch2026_metrics_train.csv")
    edf = keys.copy()
    for j in range(emb.shape[1]):
        edf[f"ssl_{method}_{j:02d}"] = emb[:, j]
    df = train.merge(edf, on=["subject_id", "lifelog_date"], how="left")
    cols = [c for c in edf.columns if c.startswith("ssl_")]
    rows=[]; pred_rows=[]
    for fold in folds():
        valid={(x['subject_id'], str(x['lifelog_date'])) for x in fold['valid_keys']}
        mask=df.apply(lambda r:(r['subject_id'], str(r['lifelog_date'])) in valid, axis=1).to_numpy()
        tmp=df.loc[mask,["subject_id","lifelog_date"]+Q_TARGETS].copy()
        scores={}; aucs={}; accs={}; cfg={}
        for y in Q_TARGETS:
            ytr=df.loc[~mask,y].astype(int).to_numpy(); yva=df.loc[mask,y].astype(int).to_numpy()
            best=None
            for C in [0.001,0.003,0.01,0.03,0.1,0.3,1.0]:
                pipe=Pipeline([
                    ('imp', SimpleImputer(strategy='median')),
                    ('scale', StandardScaler()),
                    ('clf', LogisticRegression(C=C, solver='liblinear', max_iter=1000, random_state=SEED)),
                ])
                pipe.fit(df.loc[~mask,cols], ytr)
                p=np.clip(pipe.predict_proba(df.loc[mask,cols])[:,1],0.05,0.95)
                loss=log_loss(yva,p,labels=[0,1])
                if best is None or loss < best[0]:
                    best=(loss,C,p,pipe)
            scores[y]=float(best[0]); cfg[y]={"C":best[1]}; tmp[f"pred_{y}"]=best[2]
            try: aucs[y]=roc_auc_score(yva,best[2])
            except Exception: aucs[y]=np.nan
            accs[y]=accuracy_score(yva,best[2]>=0.5)
        rows.append({
            "model": f"ssl_{method}_latent_logistic_q", "fold_id": fold['fold_id'],
            "mean_q_logloss": float(np.mean(list(scores.values()))),
            **{f"logloss_{k}":v for k,v in scores.items()},
            **{f"auc_{k}":v for k,v in aucs.items()},
            **{f"acc_{k}":v for k,v in accs.items()},
            "cfg": json.dumps(cfg),
        })
        pred_rows.append(tmp)
    return pd.DataFrame(rows), pd.concat(pred_rows, ignore_index=True), edf


def main():
    ensure_dirs(); seed_everything()
    print(f"device={DEVICE}")
    keys, x = load_hourly_tensor()
    xs, mu, sd = standardize_tensor(x)
    x_flat = xs.reshape(xs.shape[0], -1)
    print(f"tensor days={x.shape[0]} shape={x.shape[1:]} flat_dim={x_flat.shape[1]}")

    summary=[]
    ae_emb, ae_loss = train_masked_ae(x_flat)
    summary.append({"method":"masked_ae", "ssl_loss":ae_loss})
    dino_emb, dino_loss_last = train_dino_inspired(x_flat)
    summary.append({"method":"dino_temporal", "ssl_loss":dino_loss_last})

    all_res=[]
    for method, emb in [("masked_ae", ae_emb), ("dino_temporal", dino_emb)]:
        res, oof, edf = evaluate_embeddings(keys, emb, method)
        emb_path = FEATURE_DIR / f"ssl_hourly_{method}_embeddings.parquet"
        edf.to_parquet(emb_path, index=False)
        res.to_csv(EXPERIMENT_DIR / f"probe_ssl_hourly_{method}_q_results.csv", index=False)
        oof.to_csv(EXPERIMENT_DIR / f"probe_ssl_hourly_{method}_q_oof.csv", index=False)
        all_res.append(res)
        print("\n", method)
        print(res.to_string(index=False))
        print("target avg")
        print(res[["logloss_Q1","logloss_Q3"]].mean().to_string())

    final = pd.concat(all_res, ignore_index=True)
    final.to_csv(EXPERIMENT_DIR / "probe_ssl_hourly_q_results.csv", index=False)
    (EXPERIMENT_DIR / "probe_ssl_hourly_q_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\nOVERALL")
    print(final.groupby("model")[["mean_q_logloss","logloss_Q1","logloss_Q3","auc_Q1","auc_Q3"]].mean().sort_values("mean_q_logloss").to_string())


if __name__ == "__main__":
    main()
