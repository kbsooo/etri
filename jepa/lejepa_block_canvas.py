from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from torch import nn


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
STAGE2_PUBLIC = 0.5779449757

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import block_canvas_jepa as bcj  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def finite(x: np.ndarray, dtype=np.float32) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=dtype), nan=0.0, posinf=0.0, neginf=0.0)


def safe_label(x: float) -> str:
    return str(x).replace("-", "m").replace(".", "p")


def sigmoid_from_logit(x: np.ndarray) -> np.ndarray:
    return adv.clip(1.0 / (1.0 + np.exp(-x)))


def context_only_for_block(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    block_pos: np.ndarray,
    known_label_mask: np.ndarray,
) -> np.ndarray:
    block_pos = np.asarray(block_pos, dtype=int)
    sid = str(rows.iloc[int(block_pos[0])]["subject_id"])
    subject_idx = rows["subject_id"].astype(str).eq(sid).to_numpy()
    subject_pos = np.where(subject_idx)[0]
    block_set = set(int(p) for p in block_pos)
    known_subject = np.array([p for p in subject_pos if known_label_mask[p] and p not in block_set], dtype=int)
    before = known_subject[known_subject < block_pos.min()]
    after = known_subject[known_subject > block_pos.max()]
    before_tail = before[-14:]
    after_head = after[:14]

    feats: list[np.ndarray] = [
        np.array(
            [
                len(block_pos),
                rows.iloc[block_pos]["subject_phase"].mean(),
                rows.iloc[block_pos]["is_weekend"].mean(),
                rows.iloc[block_pos]["dow"].mean() / 6.0,
                float(block_pos.min() - subject_pos.min()) / max(len(subject_pos), 1),
                float(subject_pos.max() - block_pos.max()) / max(len(subject_pos), 1),
                float(block_pos.min() - before_tail[-1]) if len(before_tail) else 99.0,
                float(after_head[0] - block_pos.max()) if len(after_head) else 99.0,
                float(len(before_tail)),
                float(len(after_head)),
                float(len(known_subject)) / max(len(subject_pos), 1),
            ],
            dtype=float,
        )
    ]

    for ctx in [before_tail, after_head, known_subject]:
        if len(ctx) == 0:
            feats.extend([np.zeros(z.shape[1]), np.zeros(z.shape[1]), np.zeros(z.shape[1])])
        else:
            feats.extend([z[ctx].mean(axis=0), z[ctx].std(axis=0), bcj.slope_of(z[ctx])])

    for ctx in [before_tail, after_head, known_subject]:
        if len(ctx) == 0:
            feats.extend(
                [
                    np.full(len(TARGETS), 0.5),
                    np.zeros(len(TARGETS)),
                    np.full(len(TARGETS), 0.5),
                    np.zeros(len(TARGETS)),
                ]
            )
        else:
            vals = y[ctx]
            feats.extend(
                [
                    np.nanmean(vals, axis=0),
                    np.isfinite(vals).mean(axis=0),
                    base_all[ctx].mean(axis=0),
                    base_all[ctx].std(axis=0),
                ]
            )

    return np.concatenate([np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0).ravel() for f in feats]).astype(
        np.float32
    )


def target_rate(y_block: np.ndarray) -> np.ndarray:
    rates = np.nanmean(y_block, axis=0)
    return np.nan_to_num(rates, nan=0.5).astype(np.float32)


class MLP(nn.Module):
    def __init__(self, in_dim: int, out_dim: int, hidden: int, dropout: float) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.LayerNorm(hidden),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden),
            nn.LayerNorm(hidden),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class LeJEPABlock(nn.Module):
    def __init__(self, context_dim: int, target_dim: int, emb_dim: int, hidden: int, dropout: float) -> None:
        super().__init__()
        self.context_encoder = MLP(context_dim, emb_dim, hidden, dropout)
        self.target_encoder = MLP(target_dim, emb_dim, hidden, dropout)
        self.predictor = MLP(emb_dim, emb_dim, max(hidden // 2, emb_dim * 2), dropout)

    def forward(self, x_context: torch.Tensor, x_target: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        c = self.context_encoder(x_context)
        t = self.target_encoder(x_target)
        p = self.predictor(c)
        return c, t, p


def sigreg_loss(z: torch.Tensor, num_slices: int = 96) -> torch.Tensor:
    if z.shape[0] < 4:
        return z.square().mean() * 0.0
    a = torch.randn((z.shape[1], num_slices), dtype=z.dtype, device=z.device)
    a = a / a.norm(dim=0, keepdim=True).clamp_min(1e-6)
    proj = z @ a
    t = torch.linspace(-5.0, 5.0, 17, dtype=z.dtype, device=z.device)
    xt = proj.unsqueeze(-1) * t.view(1, 1, -1)
    real = torch.cos(xt).mean(dim=0)
    imag = torch.sin(xt).mean(dim=0)
    target = torch.exp(-0.5 * t.square()).view(1, -1)
    err = ((real - target).square() + imag.square()) * target
    return err.mean()


@dataclass
class FittedLeJEPA:
    model: LeJEPABlock
    context_scaler: StandardScaler
    target_scaler: StandardScaler
    device: torch.device
    train_loss: float
    pred_loss: float
    sig_loss: float


def fit_lejepa(
    x_context: np.ndarray,
    x_target: np.ndarray,
    *,
    emb_dim: int,
    hidden: int,
    dropout: float,
    sig_lambda: float,
    epochs: int,
    seed: int,
) -> FittedLeJEPA:
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    dev = device()
    sx = StandardScaler()
    sy = StandardScaler()
    xc = sx.fit_transform(finite(x_context)).astype(np.float32)
    yt = sy.fit_transform(finite(x_target)).astype(np.float32)
    x_tensor = torch.from_numpy(xc).to(dev)
    y_tensor = torch.from_numpy(yt).to(dev)
    model = LeJEPABlock(xc.shape[1], yt.shape[1], emb_dim, hidden, dropout).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1.5e-3, weight_decay=1.0e-3)
    batch = min(256, len(xc))
    last = {"loss": np.nan, "pred": np.nan, "sig": np.nan}
    for epoch in range(epochs):
        order = rng.permutation(len(xc))
        losses: list[float] = []
        pred_losses: list[float] = []
        sig_losses: list[float] = []
        model.train()
        for start in range(0, len(xc), batch):
            idx_np = order[start : start + batch]
            idx = torch.from_numpy(idx_np).to(dev)
            c, t, p = model(x_tensor.index_select(0, idx), y_tensor.index_select(0, idx))
            pred_loss = (p - t).square().mean()
            sig = (sigreg_loss(c) + sigreg_loss(t) + sigreg_loss(p)) / 3.0
            loss = (1.0 - sig_lambda) * pred_loss + sig_lambda * sig
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            opt.step()
            losses.append(float(loss.detach().cpu()))
            pred_losses.append(float(pred_loss.detach().cpu()))
            sig_losses.append(float(sig.detach().cpu()))
        last = {"loss": float(np.mean(losses)), "pred": float(np.mean(pred_losses)), "sig": float(np.mean(sig_losses))}
        if epoch in {max(1, epochs // 2), max(1, int(epochs * 0.75))}:
            for group in opt.param_groups:
                group["lr"] *= 0.45
    model.eval()
    return FittedLeJEPA(model, sx, sy, dev, last["loss"], last["pred"], last["sig"])


def encode_blocks(fit: FittedLeJEPA, x_context: np.ndarray, x_target: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    xc = fit.context_scaler.transform(finite(x_context)).astype(np.float32)
    yt = fit.target_scaler.transform(finite(x_target)).astype(np.float32)
    with torch.no_grad():
        c, t, p = fit.model(torch.from_numpy(xc).to(fit.device), torch.from_numpy(yt).to(fit.device))
    return (
        c.detach().cpu().numpy().astype(np.float32),
        t.detach().cpu().numpy().astype(np.float32),
        p.detach().cpu().numpy().astype(np.float32),
    )


def fit_rate_decoders(
    pred_emb: np.ndarray,
    target_emb: np.ndarray,
    rates: np.ndarray,
    alpha: float = 10.0,
) -> tuple[StandardScaler, Ridge, StandardScaler, Ridge]:
    x_pred = finite(pred_emb)
    x_both = finite(np.hstack([pred_emb, target_emb, target_emb - pred_emb, np.abs(target_emb - pred_emb)]))
    sp = StandardScaler()
    sb = StandardScaler()
    mp = Ridge(alpha=alpha, solver="svd")
    mb = Ridge(alpha=alpha, solver="svd")
    mp.fit(sp.fit_transform(x_pred), finite(rates))
    mb.fit(sb.fit_transform(x_both), finite(rates))
    return sp, mp, sb, mb


def predict_rates(
    decoders: tuple[StandardScaler, Ridge, StandardScaler, Ridge],
    pred_emb: np.ndarray,
    target_emb: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    sp, mp, sb, mb = decoders
    x_pred = finite(pred_emb)
    x_both = finite(np.hstack([pred_emb, target_emb, target_emb - pred_emb, np.abs(target_emb - pred_emb)]))
    return adv.clip(mp.predict(sp.transform(x_pred))), adv.clip(mb.predict(sb.transform(x_both)))


class FeatureAccumulator:
    def __init__(self, n_rows: int) -> None:
        self.n_rows = n_rows
        self.sum: dict[str, np.ndarray] = {}
        self.count: dict[str, np.ndarray] = {}

    def add(self, row_i: int, name: str, value: float) -> None:
        if name not in self.sum:
            self.sum[name] = np.zeros(self.n_rows, dtype=np.float64)
            self.count[name] = np.zeros(self.n_rows, dtype=np.float64)
        if np.isfinite(value):
            self.sum[name][row_i] += float(value)
            self.count[name][row_i] += 1.0

    def frame(self) -> pd.DataFrame:
        out = {}
        for name, values in self.sum.items():
            cnt = self.count[name]
            arr = np.full(self.n_rows, np.nan, dtype=np.float32)
            ok = cnt > 0
            arr[ok] = (values[ok] / cnt[ok]).astype(np.float32)
            out[name] = arr
        return pd.DataFrame(out, index=np.arange(self.n_rows))


def add_block_features(
    acc: FeatureAccumulator,
    prefix: str,
    blocks: list[np.ndarray],
    row_indices: list[np.ndarray],
    target_emb: np.ndarray,
    pred_emb: np.ndarray,
    pred_rates: np.ndarray,
    both_rates: np.ndarray,
    max_emb: int,
) -> None:
    for block_i, _block in enumerate(blocks):
        t = target_emb[block_i]
        p = pred_emb[block_i]
        r = t - p
        abs_r = np.abs(r)
        denom = float(np.linalg.norm(t) * np.linalg.norm(p))
        cos = float(np.dot(t, p) / max(denom, 1e-9))
        idxs = np.asarray(row_indices[block_i], dtype=int)
        rel = np.linspace(0.0, 1.0, len(idxs)) if len(idxs) > 1 else np.zeros(len(idxs))
        for local, row_i in enumerate(idxs):
            acc.add(row_i, f"{prefix}_pos", rel[local])
            acc.add(row_i, f"{prefix}_len", len(idxs))
            acc.add(row_i, f"{prefix}_target_norm", float(np.linalg.norm(t)))
            acc.add(row_i, f"{prefix}_pred_norm", float(np.linalg.norm(p)))
            acc.add(row_i, f"{prefix}_resid_norm", float(np.linalg.norm(r)))
            acc.add(row_i, f"{prefix}_absresid_mean", float(abs_r.mean()))
            acc.add(row_i, f"{prefix}_cos", cos)
            for k in range(min(max_emb, len(t))):
                acc.add(row_i, f"{prefix}_target_emb_{k:02d}", t[k])
                acc.add(row_i, f"{prefix}_pred_emb_{k:02d}", p[k])
                acc.add(row_i, f"{prefix}_resid_emb_{k:02d}", r[k])
                acc.add(row_i, f"{prefix}_absresid_emb_{k:02d}", abs_r[k])
            for j, target in enumerate(TARGETS):
                acc.add(row_i, f"{prefix}_pred_rate_{target}", pred_rates[block_i, j])
                acc.add(row_i, f"{prefix}_both_rate_{target}", both_rates[block_i, j])
                acc.add(row_i, f"{prefix}_rate_gap_{target}", both_rates[block_i, j] - pred_rates[block_i, j])


def latent_health(z: np.ndarray, prefix: str, seed: int = 42017) -> dict[str, float | str]:
    z = finite(z, dtype=np.float64)
    zc = z - z.mean(axis=0, keepdims=True)
    dim_std = zc.std(axis=0)
    global_scale = float(np.sqrt(np.mean(zc**2)))
    zg = zc / max(global_scale, 1e-12)
    cov = np.cov(zg, rowvar=False)
    cov = np.atleast_2d(cov)
    eig = np.clip(np.linalg.eigvalsh(cov), 0.0, None)
    eig_sum = float(eig.sum())
    p = eig / max(eig_sum, 1e-12)
    entropy = float(-(p[p > 0] * np.log(p[p > 0])).sum())
    eff_rank = float(np.exp(entropy))
    part_ratio = float(eig_sum**2 / max(float((eig**2).sum()), 1e-12))
    rng = np.random.default_rng(seed)
    sig = epps_pulley_sigreg(zg, rng, num_slices=192)
    return {
        "latent": prefix,
        "n": float(z.shape[0]),
        "dim": float(z.shape[1]),
        "global_scale": global_scale,
        "min_dim_std": float(dim_std.min()) if len(dim_std) else np.nan,
        "max_dim_std": float(dim_std.max()) if len(dim_std) else np.nan,
        "cov_eig_min": float(eig.min()) if len(eig) else np.nan,
        "cov_eig_max": float(eig.max()) if len(eig) else np.nan,
        "cov_eig_cv": float(eig.std() / max(float(eig.mean()), 1e-12)) if len(eig) else np.nan,
        "cov_condition": float(eig.max() / max(float(eig.min()), 1e-12)) if len(eig) else np.nan,
        "effective_rank": eff_rank,
        "participation_ratio": part_ratio,
        "sigreg_ep": sig,
    }


def epps_pulley_sigreg(z: np.ndarray, rng: np.random.Generator, num_slices: int = 192) -> float:
    if z.shape[0] < 4 or z.shape[1] == 0:
        return np.nan
    a = rng.normal(size=(z.shape[1], num_slices))
    a /= np.maximum(np.linalg.norm(a, axis=0, keepdims=True), 1e-12)
    proj = z @ a
    t = np.linspace(-5.0, 5.0, 17)
    target = np.exp(-0.5 * t**2)
    real = np.cos(proj[:, :, None] * t.reshape(1, 1, -1)).mean(axis=0)
    imag = np.sin(proj[:, :, None] * t.reshape(1, 1, -1)).mean(axis=0)
    err = ((real - target.reshape(1, -1)) ** 2 + imag**2) * target.reshape(1, -1)
    return float(np.trapezoid(err, t, axis=1).mean())


def build_features(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    *,
    repeats: int,
    epochs: int,
    sig_lambda: float,
    emb_dim: int,
    hidden: int,
    dropout: float,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    lengths = adv.actual_lengths_by_subject(rows)
    prefix = f"lebcj_l{safe_label(sig_lambda)}_e{emb_dim}"
    train_acc = FeatureAccumulator(len(train))
    health_rows: list[dict[str, float | str]] = []
    fold_rows: list[dict[str, float | str]] = []
    cover = np.zeros(len(train), dtype=int)

    for fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=312001)):
        known = adv.known_mask_for_train(rows, tr_idx)
        train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=240)
        val_blocks = adv.contiguous_val_blocks(rows, val_idx)
        if not train_blocks or not val_blocks:
            continue
        x_train = np.vstack([context_only_for_block(rows, z, y, base_all, b, known) for b in train_blocks])
        t_train = np.vstack([bcj.summarize_z(z, b) for b in train_blocks])
        r_train = np.vstack([target_rate(y[b]) for b in train_blocks])
        fit = fit_lejepa(
            x_train,
            t_train,
            emb_dim=emb_dim,
            hidden=hidden,
            dropout=dropout,
            sig_lambda=sig_lambda,
            epochs=epochs,
            seed=312500 + fold_i,
        )
        c_train, te_train, pe_train = encode_blocks(fit, x_train, t_train)
        decoders = fit_rate_decoders(pe_train, te_train, r_train)
        x_val = np.vstack([context_only_for_block(rows, z, y, base_all, b, known) for b in val_blocks])
        t_val = np.vstack([bcj.summarize_z(z, b) for b in val_blocks])
        _c_val, te_val, pe_val = encode_blocks(fit, x_val, t_val)
        pred_rate, both_rate = predict_rates(decoders, pe_val, te_val)
        row_indices = [rows.iloc[b]["train_idx"].to_numpy(dtype=int) for b in val_blocks]
        add_block_features(train_acc, prefix, val_blocks, row_indices, te_val, pe_val, pred_rate, both_rate, max_emb=min(24, emb_dim))
        for idxs in row_indices:
            cover[idxs] += 1
        health_rows.extend(
            [
                {**latent_health(c_train, f"{fold}_context", 43000 + fold_i), "fold": fold},
                {**latent_health(te_train, f"{fold}_target", 44000 + fold_i), "fold": fold},
                {**latent_health(pe_train, f"{fold}_pred", 45000 + fold_i), "fold": fold},
            ]
        )
        fold_rows.append(
            {
                "fold": fold,
                "train_blocks": int(len(train_blocks)),
                "val_blocks": int(len(val_blocks)),
                "covered_rows": int((cover > 0).sum()),
                "train_loss": fit.train_loss,
                "pred_loss": fit.pred_loss,
                "sig_loss": fit.sig_loss,
            }
        )
        print(
            f"LeJEPA {fold}: train_blocks={len(train_blocks)} val_blocks={len(val_blocks)} "
            f"covered={int((cover > 0).sum())} loss={fit.train_loss:.5f}",
            flush=True,
        )

    train_feat = pd.concat([train[SUB_KEY + TARGETS].copy(), train_acc.frame()], axis=1)

    known = adv.known_mask_for_train(rows, np.arange(len(train)))
    train_blocks = adv.make_training_blocks(rows, y, np.arange(len(train)), lengths, max_blocks_per_subject=280)
    sub_blocks = adv.submission_blocks(train, sub, rows)
    x_train = np.vstack([context_only_for_block(rows, z, y, base_all, b, known) for b in train_blocks])
    t_train = np.vstack([bcj.summarize_z(z, b) for b in train_blocks])
    r_train = np.vstack([target_rate(y[b]) for b in train_blocks])
    fit = fit_lejepa(
        x_train,
        t_train,
        emb_dim=emb_dim,
        hidden=hidden,
        dropout=dropout,
        sig_lambda=sig_lambda,
        epochs=max(epochs, int(epochs * 1.15)),
        seed=313999,
    )
    c_train, te_train, pe_train = encode_blocks(fit, x_train, t_train)
    decoders = fit_rate_decoders(pe_train, te_train, r_train)
    x_sub = np.vstack([context_only_for_block(rows, z, y, base_all, b, known) for b in sub_blocks])
    t_sub = np.vstack([bcj.summarize_z(z, b) for b in sub_blocks])
    _c_sub, te_sub, pe_sub = encode_blocks(fit, x_sub, t_sub)
    pred_rate, both_rate = predict_rates(decoders, pe_sub, te_sub)
    sub_acc = FeatureAccumulator(len(sub))
    sub_indices = [rows.iloc[b]["sub_idx"].to_numpy(dtype=int) for b in sub_blocks]
    add_block_features(sub_acc, prefix, sub_blocks, sub_indices, te_sub, pe_sub, pred_rate, both_rate, max_emb=min(24, emb_dim))
    sub_feat = pd.concat([sub[SUB_KEY].copy(), sub_acc.frame()], axis=1)
    health_rows.extend(
        [
            {**latent_health(c_train, "full_context", 46001), "fold": "full"},
            {**latent_health(te_train, "full_target", 46002), "fold": "full"},
            {**latent_health(pe_train, "full_pred", 46003), "fold": "full"},
        ]
    )
    return train_feat, sub_feat, pd.DataFrame(fold_rows), pd.DataFrame(health_rows)


def axis_against(file_name: str) -> dict[str, float]:
    try:
        stage2 = pd.read_csv(adv.BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        cand = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        s = adv.logit(stage2[TARGETS].to_numpy(float))
        move = adv.logit(cand[TARGETS].to_numpy(float)) - s

        def read_move(name: str) -> np.ndarray:
            df = pd.read_csv(OUT / name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
            return adv.logit(df[TARGETS].to_numpy(float)) - s

        bad_parts = []
        weights = []
        for bad_name, score in [
            ("submission_jepa_latent_residual_probe.csv", 0.5812273278),
            ("submission_jepa_latent_q2_w0p45.csv", 0.5798012862),
        ]:
            path = OUT / bad_name
            if path.exists():
                bad_parts.append(read_move(bad_name))
                weights.append(max(score - STAGE2_PUBLIC, 1e-9))
        out: dict[str, float] = {}
        if bad_parts:
            bad = np.average(np.stack(bad_parts), axis=0, weights=np.asarray(weights))
            out["jepa_bad_ratio"] = float(np.dot(move.reshape(-1), bad.reshape(-1)) / max(float(np.dot(bad.reshape(-1), bad.reshape(-1))), 1e-12))
            out["jepa_bad_cos"] = float(np.dot(move.reshape(-1), bad.reshape(-1)) / max(float(np.linalg.norm(move) * np.linalg.norm(bad)), 1e-12))
        if (OUT / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv").exists():
            good = read_move("submission_raw_timeline_jepa_rescue_strict_scale0p5.csv")
            out["raw_good_ratio"] = float(np.dot(move.reshape(-1), good.reshape(-1)) / max(float(np.dot(good.reshape(-1), good.reshape(-1))), 1e-12))
            out["raw_good_cos"] = float(np.dot(move.reshape(-1), good.reshape(-1)) / max(float(np.linalg.norm(move) * np.linalg.norm(good)), 1e-12))
        out.update(adv.public_axis_for(file_name))
        return out
    except Exception:
        return {
            "jepa_bad_ratio": np.nan,
            "jepa_bad_cos": np.nan,
            "raw_good_ratio": np.nan,
            "raw_good_cos": np.nan,
            "bad_axis_projection_ratio": np.nan,
            "good_axis_projection_ratio": np.nan,
        }


def scan_and_submit(
    train_feat: pd.DataFrame,
    sub_feat: pd.DataFrame,
    base: np.ndarray,
    base_sub: pd.DataFrame,
    *,
    prefix: str,
    top_n: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train_feat[TARGETS].to_numpy(dtype=int)
    cols = broad.finite_numeric_cols(train_feat)
    pre = broad.prefilter(train_feat, base, cols, TARGETS, top_n=top_n)
    pre.to_csv(OUT / f"{prefix}_prefilter.csv", index=False)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = broad.loss_col(y[:, j], base[:, j])
        for c_value in [0.02, 0.05, 0.10, 0.20]:
            corrected = broad.oof_corrected(train_feat, base, target, feature, mode, c_value)
            losses = [broad.loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": float(c_value),
                "base_loss": float(base_loss),
                "corrected_loss": broad.loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(train_feat, y, base, corrected, j))
            else:
                row.update(
                    {
                        "mean_delta": 0.0,
                        "median_delta": 0.0,
                        "p25_delta": 0.0,
                        "p75_delta": 0.0,
                        "win_rate": 0.0,
                        "mean_selected_weight": 0.0,
                        "zero_weight_rate": 1.0,
                    }
                )
            row["feature_family"] = (
                "rate"
                if "_rate_" in feature
                else "pred_emb"
                if "_pred_emb_" in feature
                else "target_emb"
                if "_target_emb_" in feature
                else "resid_emb"
                if "_resid_emb_" in feature or "_absresid" in feature
                else "geometry"
            )
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.00035 and row["mean_delta"] <= -0.00005 and row["win_rate"] >= 0.62)
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.56)
            rows.append(row)
    scan = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    scan.to_csv(OUT / f"{prefix}_scan.csv", index=False)

    def apply_ops(ops: pd.DataFrame, file_name: str, scale: float) -> tuple[np.ndarray, pd.DataFrame]:
        pred = base.copy()
        sub_pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
        used = []
        used_targets: set[str] = set()
        for op in ops.itertuples(index=False):
            target = str(op.target)
            if target in used_targets:
                continue
            j = TARGETS.index(target)
            w = float(op.best_weight) * scale
            corrected = broad.oof_corrected(train_feat, pred, target, str(op.feature), str(op.mode), float(op.c_value))
            pred[:, j] = adv.clip((1.0 - w) * pred[:, j] + w * corrected)
            sub_corr = broad.fit_corrected(train_feat, sub_feat, pred, sub_pred, target, str(op.feature), str(op.mode), float(op.c_value))
            sub_pred[:, j] = adv.clip((1.0 - w) * sub_pred[:, j] + w * sub_corr)
            used_targets.add(target)
            used.append(
                {
                    "target": target,
                    "feature": str(op.feature),
                    "mode": str(op.mode),
                    "c_value": float(op.c_value),
                    "base_weight": float(op.best_weight),
                    "scaled_weight": w,
                    "delta_vs_base": float(op.delta_vs_base),
                    "mean_delta": float(op.mean_delta),
                    "win_rate": float(op.win_rate),
                    "feature_family": str(op.feature_family),
                }
            )
        out = base_sub.copy()
        out[TARGETS] = sub_pred
        out.to_csv(OUT / file_name, index=False)
        pd.DataFrame(used).to_csv(OUT / file_name.replace("submission_", "").replace(".csv", "_ops.csv"), index=False)
        return pred, pd.DataFrame(used)

    strict = scan[(scan["passes_strict"]) & (scan["best_weight"] > 0)].sort_values("delta_vs_base")
    loose = scan[((scan["passes_strict"] | scan["passes_loose"]) & (scan["best_weight"] > 0))].sort_values(
        ["passes_strict", "delta_vs_base"], ascending=[False, True]
    )
    top = scan[scan["best_weight"] > 0].sort_values("delta_vs_base").groupby("target", group_keys=False).head(1)
    rate_top = (
        scan[(scan["best_weight"] > 0) & (scan["feature_family"].eq("rate"))]
        .sort_values("delta_vs_base")
        .groupby("target", group_keys=False)
        .head(1)
    )

    specs = [
        ("strict", strict),
        ("strict_noq2", strict[~strict["target"].eq("Q2")]),
        ("loose", loose),
        ("top", top),
        ("rate_top", rate_top),
    ]
    summary_rows = []
    for label, ops in specs:
        for scale in [0.35, 0.50, 0.75, 1.0]:
            scale_label = safe_label(scale)
            file_name = f"submission_{prefix}_{label}_scale{scale_label}.csv"
            pred, used = apply_ops(ops, file_name, scale)
            mloss = adv.mean_loss(y, pred)
            summary_rows.append(
                {
                    "candidate": file_name,
                    "class": label,
                    "scale": scale,
                    "ops": int(len(used)),
                    "oof_loss": mloss,
                    "oof_delta_vs_stage2": mloss - adv.mean_loss(y, base),
                    **axis_against(file_name),
                }
            )
    summary = pd.DataFrame(summary_rows).sort_values(["oof_delta_vs_stage2", "ops"])
    summary.to_csv(OUT / f"{prefix}_candidate_summary.csv", index=False)
    return scan, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--repeats", type=int, default=6)
    parser.add_argument("--sig-lambda", type=float, default=0.05)
    parser.add_argument("--emb-dim", type=int, default=32)
    parser.add_argument("--hidden", type=int, default=256)
    parser.add_argument("--dropout", type=float, default=0.04)
    parser.add_argument("--top-n", type=int, default=55)
    args = parser.parse_args()

    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, names = bcj.build_day_latent(rows, canvas)
    prefix = f"lejepa_block_canvas_l{safe_label(args.sig_lambda)}_d{args.emb_dim}"
    pd.DataFrame({"latent": names}).to_csv(OUT / f"{prefix}_day_latent_meta.csv", index=False)
    train_feat, sub_feat, folds, health = build_features(
        train,
        sub,
        rows,
        z,
        y,
        base_all,
        repeats=args.repeats,
        epochs=args.epochs,
        sig_lambda=args.sig_lambda,
        emb_dim=args.emb_dim,
        hidden=args.hidden,
        dropout=args.dropout,
    )
    train_feat.to_parquet(OUT / f"{prefix}_train_features.parquet", index=False)
    sub_feat.to_parquet(OUT / f"{prefix}_submission_features.parquet", index=False)
    folds.to_csv(OUT / f"{prefix}_fold_training.csv", index=False)
    health.to_csv(OUT / f"{prefix}_latent_health.csv", index=False)
    scan, summary = scan_and_submit(train_feat, sub_feat, base, base_sub, prefix=prefix, top_n=args.top_n)

    report = [
        "# LeJEPA Block-Canvas",
        "",
        "This run removes target-block raw/base information from the context predictor. The predictor sees only surrounding same-subject context, calendar/block-position tokens, outside-block known labels, and outside-block base predictions.",
        "",
        "Target latent is produced by a learned target encoder over hidden-block raw-canvas summaries. Training uses prediction loss plus SIGReg on context, target, and predicted latents.",
        "",
        "Downstream features may use target latent and residual because raw sensor logs for submission blocks are available at inference; this is reported separately from the context-only predictor.",
        "",
        "## Config",
        "",
        pd.DataFrame([vars(args)]).to_csv(index=False),
        "",
        "## Training Folds",
        "",
        folds.to_csv(index=False),
        "",
        "## Latent Health",
        "",
        health.to_csv(index=False),
        "",
        "## Candidate Summary",
        "",
        summary.to_csv(index=False),
        "",
        "## Best Scan Rows",
        "",
        scan.head(80).to_csv(index=False),
    ]
    (OUT / f"{prefix}_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(20).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
