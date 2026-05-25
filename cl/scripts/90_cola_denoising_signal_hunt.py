#!/usr/bin/env python3
"""CoLa-inspired continuous latent denoising signal hunt.

No submission is generated.

Use diffusion/continuous-latent ideas safely for this tiny lifelog problem:
- train an unsupervised denoising bottleneck on all day-level hourly sensor features;
- treat the bottleneck as a *signal microscope*, not as a final supervised model;
- test whether denoising latent/reconstruction-error features add fold-robust signal
  beyond simple subject/day anchors for freeze-ish targets.

This is intentionally closer to CoLa's "continuous latent prior / denoising path"
intuition than to a full diffusion model: with only 700 day rows, full diffusion is
mostly parameter theater. The useful object is the learned continuous day manifold
and its denoising difficulty/anomaly geometry.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEATURES = ROOT / "features"
EXP = ROOT / "experiments"
OUT = ROOT / "outputs"
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
FREEZE_FOCUS = ["Q1", "S1", "S2", "S3"]
SEED = 20260525
DEVICE = "cpu"  # CPU is faster/more stable for this tiny matrix than MPS startup overhead.


def seed_all(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


class DenoisingBottleneckAE(nn.Module):
    def __init__(self, d: int, z: int = 8, h: int = 64, dropout: float = 0.05):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Linear(d, h), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(h, z),
        )
        self.dec = nn.Sequential(
            nn.Linear(z, h), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(h, d),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        z = self.enc(x)
        rec = self.dec(z)
        return rec, z


def load_labels() -> Tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    test = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    for df in (train, test):
        df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
        df["sleep_date"] = pd.to_datetime(df["sleep_date"])
    return train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True), test.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)


def load_day_matrix() -> pd.DataFrame:
    """Hourly features + existing SSL embeddings as day-level continuous state."""
    parts = []
    for name in [
        "timebin_1h_flat_features.parquet",
        "deep_raw_modality_daily_features.parquet",
        "ssl_hourly_masked_ae_embeddings.parquet",
        "ssl_hourly_dino_temporal_embeddings.parquet",
    ]:
        p = FEATURES / name
        if p.exists():
            df = pd.read_parquet(p)
            df["lifelog_date"] = pd.to_datetime(df["lifelog_date"])
            parts.append(df)
    base = parts[0]
    for df in parts[1:]:
        base = base.merge(df, on=["subject_id", "lifelog_date"], how="outer")
    return base.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)


def train_denoiser(day: pd.DataFrame, zdim: int = 8) -> Tuple[pd.DataFrame, Dict[str, float]]:
    id_cols = ["subject_id", "lifelog_date"]
    num_cols = [c for c in day.columns if c not in id_cols]
    X_raw = day[num_cols].replace([np.inf, -np.inf], np.nan).astype(float)
    prep = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    X = prep.fit_transform(X_raw).astype(np.float32)
    seed_all()
    model = DenoisingBottleneckAE(X.shape[1], z=zdim, h=64, dropout=0.05).to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=2e-4)
    xt = torch.tensor(X, device=DEVICE)
    best = None
    best_loss = float("inf")
    stale = 0
    # Multi-noise denoising approximates a tiny diffusion/score path without fitting a full sampler.
    for ep in range(900):
        model.train()
        opt.zero_grad()
        sigma = float(np.random.choice([0.05, 0.10, 0.20, 0.35, 0.50]))
        mask_keep = (torch.rand_like(xt) > 0.08).float()
        noisy = xt * mask_keep + sigma * torch.randn_like(xt)
        rec, z = model(noisy)
        loss_rec = nn.functional.mse_loss(rec, xt)
        # Mild isotropic regularizer: avoid pure subject-id memorization geometry exploding.
        loss_reg = 1e-3 * (z.pow(2).mean())
        loss = loss_rec + loss_reg
        loss.backward()
        opt.step()
        if loss_rec.item() < best_loss - 1e-5:
            best_loss = loss_rec.item()
            best = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if ep > 250 and stale > 120:
                break
    if best:
        model.load_state_dict(best)
    model.eval()
    with torch.no_grad():
        clean = torch.tensor(X, device=DEVICE)
        rec, z = model(clean)
        rec_np = rec.cpu().numpy()
        z_np = z.cpu().numpy()
    err = ((rec_np - X) ** 2)
    out = day[id_cols].copy()
    for j in range(z_np.shape[1]):
        out[f"cola_z{j:02d}"] = z_np[:, j]
    out["cola_recon_mse"] = err.mean(axis=1)
    out["cola_recon_p90_abs"] = np.quantile(np.abs(rec_np - X), 0.90, axis=1)
    # Subject-normalized manifold deviation.
    for col in [c for c in out.columns if c.startswith("cola_z") or c.startswith("cola_recon")]:
        mu = out.groupby("subject_id")[col].transform("mean")
        sd = out.groupby("subject_id")[col].transform("std").replace(0, np.nan)
        out[col + "__subj_z"] = ((out[col] - mu) / sd).fillna(0.0)
    info = {"n_days": int(len(day)), "n_input_features": int(X.shape[1]), "zdim": int(zdim), "best_recon_mse": float(best_loss)}
    return out, info


def make_splits(train: pd.DataFrame, test: pd.DataFrame) -> List[Tuple[str, np.ndarray]]:
    splits: List[Tuple[str, np.ndarray]] = []
    fpath = OUT / "validation/folds_chrono.json"
    if fpath.exists():
        folds = json.loads(fpath.read_text())["folds"]
        for fold in folds:
            valid = {(x["subject_id"], str(x["lifelog_date"])[:10]) for x in fold["valid_keys"]}
            val = train.apply(lambda r: (r.subject_id, pd.Timestamp(r.lifelog_date).strftime("%Y-%m-%d")) in valid, axis=1).to_numpy()
            if val.sum():
                splits.append((str(fold["fold_id"]), val))
    # Deterministic test-pattern-like holes: every 7th/11th day per subject with offsets.
    for offset in [0, 2, 4]:
        val = np.zeros(len(train), dtype=bool)
        for _, idx in train.groupby("subject_id").groups.items():
            ordered = list(idx)
            for k, i in enumerate(ordered):
                if (k + offset) % 7 == 0 or (k + 2 * offset) % 11 == 0:
                    val[i] = True
        splits.append((f"pattern_{offset}", val))
    # Tail by subject.
    val = np.zeros(len(train), dtype=bool)
    for _, idx in train.groupby("subject_id").groups.items():
        ordered = list(idx)
        val[ordered[-max(3, len(ordered)//8):]] = True
    splits.append(("tail", val))
    return splits


def anchor_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["subject_id", "lifelog_date"]].copy()
    out["dow"] = pd.to_datetime(out["lifelog_date"]).dt.dayofweek.astype(str)
    # Within-subject relative time helps interpolate regime without label leakage.
    out["day_rank_subj"] = df.groupby("subject_id")["lifelog_date"].rank(method="first")
    out["day_rank_subj_z"] = out.groupby(df["subject_id"])["day_rank_subj"].transform(lambda s: (s - s.mean()) / (s.std() or 1.0)).fillna(0)
    return out


def eval_latent(train: pd.DataFrame, latent: pd.DataFrame) -> pd.DataFrame:
    df = train.merge(latent, on=["subject_id", "lifelog_date"], how="left")
    anc = anchor_features(df)
    latent_cols = [c for c in latent.columns if c.startswith("cola_")]
    rows = []
    splits = make_splits(train, pd.DataFrame())
    for split, val_mask in splits:
        tr_mask = ~val_mask
        for y in LABELS:
            ytr = df.loc[tr_mask, y].astype(int).to_numpy()
            yva = df.loc[val_mask, y].astype(int).to_numpy()
            if len(np.unique(ytr)) < 2 or len(np.unique(yva)) < 2:
                continue
            # Anchor: subject + dow + relative date. Keep day_rank as numeric;
            # dummy only subject/dow so the comparison is not an artifact of OHE'ing
            # every unique date rank.
            X_anchor = anc[["subject_id", "dow", "day_rank_subj_z"]].copy()
            Xa_df = pd.get_dummies(X_anchor, columns=["subject_id", "dow"], dummy_na=False)
            Xa = Xa_df.loc[tr_mask, Xa_df.columns]
            Xav = Xa_df.loc[val_mask, Xa_df.columns]
            # Anchor+latent.
            X_lat = pd.concat([X_anchor, df[latent_cols]], axis=1)
            Xl = pd.get_dummies(X_lat, columns=["subject_id", "dow"], dummy_na=False)
            tr_cols = Xl.columns
            Xltr = Xl.loc[tr_mask, tr_cols]
            Xlva = Xl.loc[val_mask, tr_cols]
            models = {
                "anchor_subject_dow": (Xa, Xav),
                "anchor_plus_cola_latent": (Xltr, Xlva),
            }
            losses = {}
            aucs = {}
            for name, (Xtr, Xva) in models.items():
                pipe = Pipeline([
                    ("imp", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler(with_mean=False)),
                    ("clf", LogisticRegression(C=0.03, solver="liblinear", max_iter=1000, random_state=SEED)),
                ])
                pipe.fit(Xtr, ytr)
                p = np.clip(pipe.predict_proba(Xva)[:, 1], 0.02, 0.98)
                losses[name] = log_loss(yva, p, labels=[0, 1])
                try:
                    aucs[name] = roc_auc_score(yva, p)
                except Exception:
                    aucs[name] = np.nan
            rows.append({
                "split": split,
                "target": y,
                "focus_target": y in FREEZE_FOCUS,
                "n_val": int(val_mask.sum()),
                "anchor_loss": losses["anchor_subject_dow"],
                "cola_loss": losses["anchor_plus_cola_latent"],
                "delta_cola_minus_anchor": losses["anchor_plus_cola_latent"] - losses["anchor_subject_dow"],
                "anchor_auc": aucs["anchor_subject_dow"],
                "cola_auc": aucs["anchor_plus_cola_latent"],
            })
    return pd.DataFrame(rows)


def nearest_neighbor_purity(train: pd.DataFrame, latent: pd.DataFrame, k: int = 3) -> pd.DataFrame:
    df = train.merge(latent, on=["subject_id", "lifelog_date"], how="left")
    zcols = [c for c in latent.columns if c.startswith("cola_z") and not c.endswith("__subj_z")]
    rows = []
    for sid, g in df.groupby("subject_id"):
        Z = g[zcols].to_numpy(float)
        if len(g) <= k:
            continue
        # z-score inside subject before neighbor search.
        Z = (Z - np.nanmean(Z, axis=0)) / (np.nanstd(Z, axis=0) + 1e-6)
        D = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(axis=2)
        np.fill_diagonal(D, np.inf)
        nn = np.argsort(D, axis=1)[:, :k]
        for y in LABELS:
            vals = g[y].astype(int).to_numpy()
            maj = []
            agree = []
            for i in range(len(g)):
                neigh = vals[nn[i]]
                pred = int(neigh.mean() >= 0.5)
                maj.append(pred)
                agree.append(float(pred == vals[i]))
            base = max(vals.mean(), 1 - vals.mean())
            rows.append({"subject_id": sid, "target": y, "nn_acc": float(np.mean(agree)), "subject_majority_acc": float(base), "lift": float(np.mean(agree) - base)})
    return pd.DataFrame(rows)


def write_report(info: Dict[str, float], ev: pd.DataFrame, nn: pd.DataFrame) -> None:
    EXP.mkdir(exist_ok=True)
    focus = ev[ev.focus_target]
    overall = ev.groupby("target")["delta_cola_minus_anchor"].agg(["mean", "median", "min", "max", "count"]).reset_index()
    split = ev.groupby(["target", "split"])["delta_cola_minus_anchor"].mean().reset_index()
    nn_s = nn.groupby("target")[["nn_acc", "subject_majority_acc", "lift"]].mean().reset_index()
    lines = []
    lines.append("# CoLa-inspired denoising latent signal hunt\n")
    lines.append("No submission files were created. Negative delta means the continuous denoising latent helped over a subject/day anchor.\n")
    lines.append("## Setup\n")
    for k, v in info.items():
        lines.append(f"- {k}: `{v}`")
    lines.append("\n## Target-level delta: anchor+CoLa latent minus anchor\n")
    lines.append(overall.to_markdown(index=False, floatfmt=".4f"))
    lines.append("\n## Split-level deltas\n")
    lines.append(split.to_markdown(index=False, floatfmt=".4f"))
    lines.append("\n## Subject-local latent nearest-neighbor label purity\n")
    lines.append(nn_s.to_markdown(index=False, floatfmt=".4f"))
    lines.append("\n## Interpretation\n")
    good = overall[overall["mean"] < -0.003].target.tolist()
    bad = overall[overall["mean"] > 0.003].target.tolist()
    lines.append(f"- Potentially useful targets by mean delta < -0.003: `{good}`")
    lines.append(f"- Likely unsafe/noisy targets by mean delta > +0.003: `{bad}`")
    lines.append("- Treat this as a microscope. A full diffusion sampler is not justified unless these latent/anomaly features show stable target-local signal.")
    lines.append("- If signal exists, next step is not immediate submission; inspect row-level high-shift cases against `test_regime_map.csv` and public-LB constraints.")
    (EXP / "cola_denoising_signal_hunt_report.md").write_text("\n".join(lines))


def write_paper_notes() -> None:
    note = """# CoLa / continuous latent diffusion idea — competition adaptation\n\nSource inspected: `/Users/kbsoo/Downloads/cola.pdf` (`Continuous Latent Diffusion Language Model`, arXiv 2605.06548).\n\n## Paper idea in one line\nCoLa separates generation into: discrete observation -> stable continuous latent -> diffusion/flow prior in latent space -> conditional decoder. The important part for us is not language generation, but the hierarchy: local noisy observations are compressed into a global continuous semantic state, then a prior/denoising path models that state.\n\n## Why directly copying it is wrong here\n- CoLa has massive text data and a generative objective; this competition has about 700 day rows and 450 labeled rows.\n- A real diffusion prior over 700 day latents would mostly learn subject/date artifacts.\n- Token-level decoding has no analogue unless we reconstruct raw sensor streams, which is expensive and probably not submission-relevant.\n\n## Safe adaptation\nUse a tiny continuous denoising bottleneck as a *day-state microscope*:\n1. build day/hour sensor vector;\n2. corrupt it with noise/masking at several sigma levels;\n3. train encoder-decoder to recover clean day vector;\n4. use bottleneck z and denoising error as row-level signals;\n5. validate whether those signals explain freeze-target flips beyond subject/day anchors.\n\nThis is diffusion-inspired but deliberately not a full sampler. It tests the part of CoLa that is plausibly useful: continuous semantic/state compression and denoising difficulty.\n\n## If this works\nOnly then consider a second spike: a small latent-prior model over subject time, e.g. predict/denoise z_t from neighboring days z_{t-1}, z_{t+1}, then use residuals as anomaly features.\n"""
    (EXP / "cola_continuous_latent_diffusion_notes.md").write_text(note)


def main() -> None:
    EXP.mkdir(exist_ok=True)
    FEATURES.mkdir(exist_ok=True)
    train, test = load_labels()
    day = load_day_matrix()
    latent, info = train_denoiser(day, zdim=8)
    latent_path = FEATURES / "cola_denoising_latent_v1.parquet"
    latent.to_parquet(latent_path, index=False)
    ev = eval_latent(train, latent)
    ev_path = EXP / "cola_denoising_signal_eval.csv"
    ev.to_csv(ev_path, index=False)
    nn = nearest_neighbor_purity(train, latent, k=3)
    nn_path = EXP / "cola_denoising_nn_purity.csv"
    nn.to_csv(nn_path, index=False)
    write_report(info, ev, nn)
    write_paper_notes()
    print("wrote", latent_path)
    print("wrote", ev_path)
    print("wrote", nn_path)
    print("wrote", EXP / "cola_denoising_signal_hunt_report.md")
    print(ev.groupby("target")["delta_cola_minus_anchor"].mean().sort_values().to_string())


if __name__ == "__main__":
    main()
