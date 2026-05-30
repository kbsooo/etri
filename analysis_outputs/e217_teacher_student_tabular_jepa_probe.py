#!/usr/bin/env python3
"""E217: teacher-student tabular JEPA probe.

E215 used a masked-family predictor, but its target was still a fixed PCA
block. This experiment moves closer to I-JEPA/LeJEPA mechanics:

- the context encoder sees masked feature-family blocks plus same-subject row
  neighborhood context;
- the target encoder is an EMA teacher that sees only the full current row
  representation;
- the predictor matches the teacher latent, not raw feature values;
- downstream use is still conservative: frozen latents are only tested as
  calibrated residual/gate features against the stage2 OOF baseline.

The question is not "can a neural net classify the labels", but whether a
teacher-student hidden-state objective creates a new stable signal beyond the
E208/E215 JEPA probes.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import broad_feature_addon_builder as stage2  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402
import e207_lejepa_identifiability_conditions_audit as e207  # noqa: E402
import e215_masked_family_jepa_probe as e215  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
SEED = 291217

TRAIN_FEATURES_OUT = OUT / "e217_teacher_student_tabular_jepa_train_features.parquet"
SUB_FEATURES_OUT = OUT / "e217_teacher_student_tabular_jepa_submission_features.parquet"
TRAINING_OUT = OUT / "e217_teacher_student_tabular_jepa_training_summary.csv"
CONTEXT_OUT = OUT / "e217_teacher_student_tabular_jepa_context_summary.csv"
MASK_OUT = OUT / "e217_teacher_student_tabular_jepa_mask_summary.csv"
GEOMETRY_HEALTH_OUT = OUT / "e217_teacher_student_tabular_jepa_geometry_health_summary.csv"
SCAN_OUT = OUT / "e217_teacher_student_tabular_jepa_downstream_scan_summary.csv"
DOWNSTREAM_GEOM_OUT = OUT / "e217_teacher_student_tabular_jepa_downstream_geometry_summary.csv"
TARGET_OUT = OUT / "e217_teacher_student_tabular_jepa_target_summary.csv"
REPORT_OUT = OUT / "e217_teacher_student_tabular_jepa_report.md"
META_OUT = OUT / "e217_teacher_student_tabular_jepa_meta.json"


@dataclass(frozen=True)
class MaskSpec:
    name: str
    family_indices: tuple[int, ...]


@dataclass(frozen=True)
class TrainResult:
    seed: int
    train_loss: float
    val_loss: float
    mean_teacher_loss: float
    shuffled_teacher_loss: float
    context_var_penalty: float
    pred_var_penalty: float
    target_var_penalty: float
    context_cov_penalty: float
    target_cov_penalty: float
    epochs: int
    target_z: np.ndarray
    context_z_by_mask: np.ndarray
    pred_by_mask: np.ndarray


class Encoder(torch.nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, emb_dim: int) -> None:
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.Linear(hidden_dim, emb_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class TeacherStudentJEPA(torch.nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, emb_dim: int) -> None:
        super().__init__()
        self.context_encoder = Encoder(input_dim, hidden_dim, emb_dim)
        self.predictor = torch.nn.Sequential(
            torch.nn.LayerNorm(emb_dim),
            torch.nn.Linear(emb_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim, emb_dim),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.context_encoder(x)
        pred = self.predictor(z)
        return z, pred


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def variance_penalty(x: torch.Tensor, eps: float = 1e-4) -> torch.Tensor:
    std = torch.sqrt(x.var(dim=0, unbiased=False) + eps)
    return torch.relu(1.0 - std).mean()


def covariance_penalty(x: torch.Tensor) -> torch.Tensor:
    if x.shape[0] < 2:
        return x.sum() * 0.0
    xc = x - x.mean(dim=0, keepdim=True)
    cov = (xc.T @ xc) / max(x.shape[0] - 1, 1)
    off = cov - torch.diag(torch.diag(cov))
    return (off**2).sum() / x.shape[1]


def normalized_mse(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    pp = torch.nn.functional.normalize(pred, dim=1)
    tt = torch.nn.functional.normalize(target.detach(), dim=1)
    return torch.nn.functional.mse_loss(pp, tt)


def update_ema(teacher: torch.nn.Module, online: torch.nn.Module, momentum: float) -> None:
    with torch.no_grad():
        for tp, op in zip(teacher.parameters(), online.parameters()):
            tp.data.mul_(momentum).add_(op.data, alpha=1.0 - momentum)


def make_mask_specs(families: list[e215.FamilyBlock]) -> list[MaskSpec]:
    k = len(families)
    specs: list[MaskSpec] = []
    for i, fam in enumerate(families):
        specs.append(MaskSpec(f"single_{fam.family}", (i,)))
    for i in range(k):
        specs.append(MaskSpec(f"pair_{families[i].family}_{families[(i + 1) % k].family}", (i, (i + 1) % k)))
    if k >= 3:
        specs.extend(
            [
                MaskSpec("triple_lowfreq", tuple(range(min(3, k)))),
                MaskSpec("triple_highfreq", tuple(range(max(0, k - 3), k))),
            ]
        )
    # Deduplicate cyclic pair collisions when there are few families.
    seen: set[tuple[int, ...]] = set()
    out: list[MaskSpec] = []
    for spec in specs:
        key = tuple(sorted(set(spec.family_indices)))
        if key in seen:
            continue
        seen.add(key)
        out.append(MaskSpec(spec.name, key))
    return out


def same_subject_neighbor_context(rows: pd.DataFrame, context: np.ndarray) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    n, d = context.shape
    mean_ctx = np.zeros((n, d), dtype=np.float64)
    delta_ctx = np.zeros((n, d), dtype=np.float64)
    meta = np.zeros((n, 5), dtype=np.float64)
    frame = rows.reset_index().rename(columns={"index": "global_index"}).sort_values(["subject_id", "lifelog_date", "sleep_date"])
    for _, g in frame.groupby("subject_id", sort=False):
        idx = g["global_index"].to_numpy(dtype=int)
        dates = pd.to_datetime(g["lifelog_date"]).to_numpy()
        m = len(idx)
        for pos, row_idx in enumerate(idx):
            before_parts: list[np.ndarray] = []
            before_w: list[float] = []
            after_parts: list[np.ndarray] = []
            after_w: list[float] = []
            for lag in [1, 2]:
                if pos - lag >= 0:
                    gap = max(int((dates[pos] - dates[pos - lag]) / np.timedelta64(1, "D")), 1)
                    before_parts.append(context[idx[pos - lag]])
                    before_w.append(float(np.exp(-gap / 7.0) / lag))
                if pos + lag < m:
                    gap = max(int((dates[pos + lag] - dates[pos]) / np.timedelta64(1, "D")), 1)
                    after_parts.append(context[idx[pos + lag]])
                    after_w.append(float(np.exp(-gap / 7.0) / lag))
            pieces = before_parts + after_parts
            weights = before_w + after_w
            if pieces:
                ww = np.asarray(weights, dtype=np.float64)
                mean_ctx[row_idx] = np.average(np.vstack(pieces), axis=0, weights=ww)
            if before_parts:
                b = np.average(np.vstack(before_parts), axis=0, weights=np.asarray(before_w, dtype=np.float64))
            else:
                b = np.zeros(d, dtype=np.float64)
            if after_parts:
                a = np.average(np.vstack(after_parts), axis=0, weights=np.asarray(after_w, dtype=np.float64))
            else:
                a = np.zeros(d, dtype=np.float64)
            delta_ctx[row_idx] = a - b
            meta[row_idx] = [
                len(before_parts),
                len(after_parts),
                len(pieces),
                pos / max(m - 1, 1),
                min(pos, max(m - 1 - pos, 0)),
            ]
    meta[:, :3] /= 4.0
    meta[:, 4] = np.log1p(meta[:, 4])
    meta = StandardScaler().fit_transform(meta)
    meta = finite(meta)
    summary = pd.DataFrame(
        {
            "metric": ["mean_neighbor_norm", "mean_delta_norm", "rows_with_neighbor", "meta_columns"],
            "value": [
                float(np.linalg.norm(mean_ctx, axis=1).mean()),
                float(np.linalg.norm(delta_ctx, axis=1).mean()),
                float((np.abs(mean_ctx).sum(axis=1) > 0).mean()),
                float(meta.shape[1]),
            ],
        }
    )
    return finite(mean_ctx), finite(delta_ctx), summary


def input_for_mask(
    context: np.ndarray,
    neighbor_mean: np.ndarray,
    neighbor_delta: np.ndarray,
    row_meta: np.ndarray,
    families: list[e215.FamilyBlock],
    spec: MaskSpec,
) -> np.ndarray:
    masked = context.copy()
    mask_vec = np.zeros((len(context), len(families)), dtype=np.float64)
    for fam_i in spec.family_indices:
        family = families[fam_i]
        masked[:, family.start : family.end] = 0.0
        mask_vec[:, fam_i] = 1.0
    return finite(np.hstack([masked, neighbor_mean, neighbor_delta, row_meta, mask_vec]))


def target_input(context: np.ndarray, neighbor_mean: np.ndarray, row_meta: np.ndarray, families: list[e215.FamilyBlock]) -> np.ndarray:
    zeros_neighbor = np.zeros_like(neighbor_mean)
    zeros_delta = np.zeros_like(neighbor_mean)
    zeros_meta = np.zeros_like(row_meta)
    zeros_mask = np.zeros((len(context), len(families)), dtype=np.float64)
    return finite(np.hstack([context, zeros_neighbor, zeros_delta, zeros_meta, zeros_mask]))


def train_teacher_student_jepa(
    context: np.ndarray,
    neighbor_mean: np.ndarray,
    neighbor_delta: np.ndarray,
    row_meta: np.ndarray,
    families: list[e215.FamilyBlock],
    specs: list[MaskSpec],
    seed: int,
    emb_dim: int = 32,
    epochs: int = 720,
) -> TrainResult:
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    device = torch.device("cpu")

    x_by_mask_np = np.stack(
        [input_for_mask(context, neighbor_mean, neighbor_delta, row_meta, families, spec) for spec in specs],
        axis=1,
    )
    target_np = target_input(context, neighbor_mean, row_meta, families)
    x_all = torch.tensor(x_by_mask_np, dtype=torch.float32, device=device)
    target_all = torch.tensor(target_np, dtype=torch.float32, device=device)

    rows = np.repeat(np.arange(len(context)), len(specs))
    masks = np.tile(np.arange(len(specs)), len(context))
    order = rng.permutation(len(rows))
    val_size = max(96, int(round(0.20 * len(order))))
    val_sel = order[:val_size]
    tr_sel = order[val_size:]
    tr_rows = torch.tensor(rows[tr_sel], dtype=torch.long, device=device)
    tr_masks = torch.tensor(masks[tr_sel], dtype=torch.long, device=device)
    va_rows = torch.tensor(rows[val_sel], dtype=torch.long, device=device)
    va_masks = torch.tensor(masks[val_sel], dtype=torch.long, device=device)

    model = TeacherStudentJEPA(x_by_mask_np.shape[2], hidden_dim=128, emb_dim=emb_dim).to(device)
    teacher = Encoder(x_by_mask_np.shape[2], hidden_dim=128, emb_dim=emb_dim).to(device)
    teacher.load_state_dict(model.context_encoder.state_dict())
    for p in teacher.parameters():
        p.requires_grad_(False)

    opt = torch.optim.AdamW(model.parameters(), lr=1.2e-3, weight_decay=1.0e-4)
    best_state: dict[str, Any] | None = None
    best_val = float("inf")
    bad_epochs = 0

    for epoch in range(epochs):
        model.train()
        with torch.no_grad():
            target_z = teacher(target_all[tr_rows])
        z, pred = model(x_all[tr_rows, tr_masks])
        loss_pred = normalized_mse(pred, target_z)
        loss = loss_pred + 0.040 * variance_penalty(z) + 0.015 * covariance_penalty(z) + 0.025 * variance_penalty(pred)
        opt.zero_grad()
        loss.backward()
        opt.step()
        update_ema(teacher, model.context_encoder, momentum=0.992)

        if epoch % 10 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                target_val = teacher(target_all[va_rows])
                z_val, pred_val = model(x_all[va_rows, va_masks])
                val_loss = normalized_mse(pred_val, target_val).item()
                val_loss += 0.003 * variance_penalty(z_val).item()
            if val_loss < best_val - 1e-7:
                best_val = val_loss
                best_state = {
                    "model": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
                    "teacher": {k: v.detach().cpu().clone() for k, v in teacher.state_dict().items()},
                }
                bad_epochs = 0
            else:
                bad_epochs += 10
            if bad_epochs >= 180:
                break

    if best_state is not None:
        model.load_state_dict(best_state["model"])
        teacher.load_state_dict(best_state["teacher"])
    model.eval()
    teacher.eval()
    with torch.no_grad():
        target_z_all = teacher(target_all)
        z_parts: list[np.ndarray] = []
        pred_parts: list[np.ndarray] = []
        for spec_i in range(len(specs)):
            z_part, pred_part = model(x_all[:, spec_i])
            z_parts.append(finite(z_part.cpu().numpy()))
            pred_parts.append(finite(pred_part.cpu().numpy()))
        train_target = teacher(target_all[tr_rows])
        val_target = teacher(target_all[va_rows])
        tr_z, tr_pred = model(x_all[tr_rows, tr_masks])
        va_z, va_pred = model(x_all[va_rows, va_masks])
        train_loss = normalized_mse(tr_pred, train_target).item()
        val_loss = normalized_mse(va_pred, val_target).item()
        ctx_var = variance_penalty(torch.cat([torch.tensor(z, dtype=torch.float32, device=device) for z in z_parts], dim=0)).item()
        pred_var = variance_penalty(torch.cat([torch.tensor(p, dtype=torch.float32, device=device) for p in pred_parts], dim=0)).item()
        target_var = variance_penalty(target_z_all).item()
        ctx_cov = covariance_penalty(torch.cat([torch.tensor(z, dtype=torch.float32, device=device) for z in z_parts], dim=0)).item()
        target_cov = covariance_penalty(target_z_all).item()

        normalized_val_target = torch.nn.functional.normalize(val_target, dim=1)
        mean_teacher = torch.nn.functional.normalize(train_target.mean(dim=0, keepdim=True), dim=1).repeat(len(va_rows), 1)
        mean_teacher_loss = torch.nn.functional.mse_loss(mean_teacher, normalized_val_target).item()
        shuffled_idx = torch.tensor(rng.choice(len(context), size=len(va_rows), replace=True), dtype=torch.long, device=device)
        shuffled_teacher = torch.nn.functional.normalize(teacher(target_all[shuffled_idx]), dim=1)
        shuffled_teacher_loss = torch.nn.functional.mse_loss(shuffled_teacher, normalized_val_target).item()

    return TrainResult(
        seed=seed,
        train_loss=float(train_loss),
        val_loss=float(val_loss),
        mean_teacher_loss=float(mean_teacher_loss),
        shuffled_teacher_loss=float(shuffled_teacher_loss),
        context_var_penalty=float(ctx_var),
        pred_var_penalty=float(pred_var),
        target_var_penalty=float(target_var),
        context_cov_penalty=float(ctx_cov),
        target_cov_penalty=float(target_cov),
        epochs=int(epoch + 1),
        target_z=finite(target_z_all.cpu().numpy()),
        context_z_by_mask=np.stack(z_parts, axis=1),
        pred_by_mask=np.stack(pred_parts, axis=1),
    )


def pca_features(prefix: str, matrix: np.ndarray, max_comp: int) -> dict[str, np.ndarray]:
    n_comp = min(max_comp, matrix.shape[0] - 2, matrix.shape[1])
    if n_comp <= 0:
        return {}
    z = PCA(n_components=n_comp, svd_solver="randomized", random_state=SEED + len(prefix)).fit_transform(finite(matrix))
    z = StandardScaler().fit_transform(z)
    return {f"{prefix}{k:02d}": finite(z[:, k]) for k in range(n_comp)}


def build_feature_frame(
    rows: pd.DataFrame,
    results: list[TrainResult],
    specs: list[MaskSpec],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pred_stack = np.stack([r.pred_by_mask for r in results], axis=0)
    ctx_stack = np.stack([r.context_z_by_mask for r in results], axis=0)
    teacher_stack = np.stack([r.target_z for r in results], axis=0)

    pred_mean = finite(pred_stack.mean(axis=(0, 2)))
    pred_std = finite(pred_stack.std(axis=(0, 2)))
    ctx_mean = finite(ctx_stack.mean(axis=(0, 2)))
    teacher_mean = finite(teacher_stack.mean(axis=0))
    residual = finite(pred_mean - teacher_mean)
    ctx_residual = finite(ctx_mean - teacher_mean)

    single_idx = [i for i, spec in enumerate(specs) if len(spec.family_indices) == 1]
    hard_idx = [i for i, spec in enumerate(specs) if len(spec.family_indices) >= 2]
    if single_idx:
        single_pred = finite(pred_stack[:, :, single_idx, :].mean(axis=(0, 2)))
    else:
        single_pred = pred_mean
    if hard_idx:
        hard_pred = finite(pred_stack[:, :, hard_idx, :].mean(axis=(0, 2)))
    else:
        hard_pred = pred_mean

    pred_norm = np.linalg.norm(pred_mean, axis=1)
    teacher_norm = np.linalg.norm(teacher_mean, axis=1)
    denom = np.maximum(pred_norm * teacher_norm, 1e-9)
    pred_teacher_cos = np.sum(pred_mean * teacher_mean, axis=1) / denom
    ctx_teacher_cos = np.sum(ctx_mean * teacher_mean, axis=1) / np.maximum(
        np.linalg.norm(ctx_mean, axis=1) * teacher_norm, 1e-9
    )

    fmap: dict[str, np.ndarray] = {
        "e217_pred_norm": pred_norm,
        "e217_context_norm": np.linalg.norm(ctx_mean, axis=1),
        "e217_teacher_norm": teacher_norm,
        "e217_pred_mask_std": pred_std.mean(axis=1),
        "e217_resid_norm": np.linalg.norm(residual, axis=1),
        "e217_resid_abs_mean": np.abs(residual).mean(axis=1),
        "e217_context_resid_norm": np.linalg.norm(ctx_residual, axis=1),
        "e217_pred_teacher_cos": pred_teacher_cos,
        "e217_context_teacher_cos": ctx_teacher_cos,
        "e217_single_resid_norm": np.linalg.norm(single_pred - teacher_mean, axis=1),
        "e217_hard_resid_norm": np.linalg.norm(hard_pred - teacher_mean, axis=1),
        "e217_hard_minus_single_norm": np.linalg.norm(hard_pred - single_pred, axis=1),
    }
    fmap.update(pca_features("e217_pred_pc", pred_mean, 16))
    fmap.update(pca_features("e217_teacher_pc", teacher_mean, 16))
    fmap.update(pca_features("e217_context_pc", ctx_mean, 16))
    fmap.update(pca_features("e217_resid_pc", residual, 16))
    fmap.update(pca_features("e217_hard_resid_pc", hard_pred - teacher_mean, 12))

    feature_df = pd.concat([rows[SUB_KEY].reset_index(drop=True), pd.DataFrame(fmap)], axis=1)
    rng = np.random.default_rng(SEED + 217)
    health_rows = []
    for name, matrix in {
        "teacher_mean": teacher_mean,
        "pred_mean": pred_mean,
        "context_mean": ctx_mean,
        "residual": residual,
        "hard_residual": hard_pred - teacher_mean,
    }.items():
        health_rows.append({"embedding": name, **e207.projection_moments(matrix, rng), **e207.covariance_health(matrix)})
    return feature_df, pd.DataFrame(health_rows)


def fit_corrected(
    train_rows: pd.DataFrame,
    pred_rows: pd.DataFrame,
    train_base: np.ndarray,
    pred_base: np.ndarray,
    target: str,
    feature: str,
    mode: str,
    c_value: float,
) -> np.ndarray:
    j = TARGETS.index(target)
    z_tr, z_pr = broad.transform_pair(train_rows, pred_rows, feature, mode)
    x_tr = np.column_stack([logit(train_base[:, j]), z_tr])
    x_pr = np.column_stack([logit(pred_base[:, j]), z_pr])
    y = train_rows[target].to_numpy(dtype=int)
    if y.min() == y.max():
        return np.full(len(pred_rows), float(y.mean()))
    clf = LogisticRegression(C=float(c_value), solver="lbfgs", max_iter=700)
    clf.fit(x_tr, y)
    return clip(clf.predict_proba(x_pr)[:, 1])


def geometry_summary(train_raw: pd.DataFrame, sub_raw: pd.DataFrame, df: pd.DataFrame, base: np.ndarray, op: dict[str, object]) -> dict[str, float]:
    y = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    target = str(op["target"])
    feature = str(op["feature"])
    mode = str(op["mode"])
    c_value = float(op["c_value"])
    weight = float(op["best_weight"])
    j = TARGETS.index(target)
    for tr_idx, val_idx, fold in geom.geometry_folds(train_raw, sub_raw, n_repeats=8, seed=SEED):
        ref = df.iloc[tr_idx].reset_index(drop=True)
        val = df.iloc[val_idx].reset_index(drop=True)
        val_pred = base[val_idx].copy()
        corrected = fit_corrected(ref, val, base[tr_idx].copy(), val_pred, target, feature, mode, c_value)
        val_pred[:, j] = clip((1.0 - weight) * val_pred[:, j] + weight * corrected)
        rows.append(
            {
                "fold": fold,
                "delta_mean": mean_loss(y[val_idx], val_pred) - mean_loss(y[val_idx], base[val_idx]),
                "delta_target": loss_col(y[val_idx, j], val_pred[:, j]) - loss_col(y[val_idx, j], base[val_idx, j]),
            }
        )
    g = pd.DataFrame(rows)
    return {
        "geometry_delta_mean": float(g["delta_mean"].mean()),
        "geometry_win_rate": float((g["delta_mean"] < 0).mean()),
        "geometry_target_delta": float(g["delta_target"].mean()),
        "geometry_target_win_rate": float((g["delta_target"] < 0).mean()),
    }


def downstream_scan(train_raw: pd.DataFrame, sub_raw: pd.DataFrame, feature_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = clip(np.load(OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    df = train_raw[SUB_KEY + TARGETS].merge(feature_df, on=SUB_KEY, how="left")
    cols = [c for c in df.columns if c.startswith("e217_")]
    pre = broad.prefilter(df, base, cols, TARGETS, top_n=22)
    y = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.03, 0.05, 0.10, 0.20]:
            corrected = broad.oof_corrected(df, base, target, feature, mode, c_value)
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": float(c_value),
                "base_loss": base_loss,
                "corrected_loss": loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(df, y, base, corrected, j))
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
            rows.append(row)

    scan = pd.DataFrame(rows).sort_values(["delta_vs_base", "mean_delta"], ascending=[True, True])
    geom_rows = []
    for op in scan[(scan["best_weight"] > 0) & (scan["delta_vs_base"] < -0.00025)].head(24).to_dict(orient="records"):
        enriched = dict(op)
        enriched.update(geometry_summary(train_raw, sub_raw, df, base, op))
        geom_rows.append(enriched)
    geom_df = pd.DataFrame(geom_rows)
    if not geom_df.empty:
        geom_df["passes_e217_probe"] = (
            (geom_df["delta_vs_base"] <= -0.00045)
            & (geom_df["mean_delta"] <= -0.00010)
            & (geom_df["win_rate"] >= 0.62)
            & (geom_df["geometry_delta_mean"] <= 0.0)
            & (geom_df["geometry_win_rate"] >= 0.50)
        )

    target_rows = []
    for target, group in scan.groupby("target", sort=False):
        best = group.iloc[0]
        target_rows.append(
            {
                "target": target,
                "best_feature": best["feature"],
                "best_mode": best["mode"],
                "best_c_value": float(best["c_value"]),
                "best_weight": float(best["best_weight"]),
                "best_delta_vs_base": float(best["delta_vs_base"]),
                "best_mean_delta": float(best["mean_delta"]),
                "best_win_rate": float(best["win_rate"]),
            }
        )
    return scan, geom_df, pd.DataFrame(target_rows)


def md_table(frame: pd.DataFrame, cols: list[str], max_rows: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.head(max_rows)[cols].iterrows():
        vals = []
        for col in cols:
            val = row[col]
            vals.append(f"{val:.6g}" if isinstance(val, float) else str(val))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(
    rows: pd.DataFrame,
    context_meta: pd.DataFrame,
    mask_meta: pd.DataFrame,
    neighbor_meta: pd.DataFrame,
    train_diag: pd.DataFrame,
    health: pd.DataFrame,
    target_summary: pd.DataFrame,
    geom_df: pd.DataFrame,
) -> None:
    pass_count = int(geom_df["passes_e217_probe"].sum()) if "passes_e217_probe" in geom_df else 0
    best_target = target_summary.sort_values("best_delta_vs_base").head(1)
    lines = [
        "# E217 Teacher-Student Tabular JEPA Probe",
        "",
        "## Purpose",
        "",
        "Train a teacher-student JEPA closer to the paper mechanics than E215: the context encoder sees masked feature-family blocks plus same-subject row-neighborhood context, while an EMA teacher sees the full current row representation. The learned latent is frozen and tested only as a downstream calibration/gate signal.",
        "",
        "## Data",
        "",
        f"- rows: `{len(rows)}` train+submission rows",
        f"- context families: `{len(context_meta)}`",
        f"- mask specs: `{len(mask_meta)}`",
        "",
        "## Context Families",
        "",
        md_table(context_meta, ["family", "columns", "components", "explained_variance"], 20),
        "",
        "## Mask Specs",
        "",
        md_table(mask_meta, ["name", "families", "n_families"], 20),
        "",
        "## Same-Subject Neighborhood Context",
        "",
        md_table(neighbor_meta, ["metric", "value"], 10),
        "",
        "## JEPA Training Diagnostics",
        "",
        md_table(
            train_diag,
            [
                "seed",
                "train_loss",
                "val_loss",
                "mean_teacher_loss",
                "shuffled_teacher_loss",
                "context_var_penalty",
                "pred_var_penalty",
                "target_var_penalty",
                "epochs",
            ],
        ),
        "",
        "## Embedding Geometry",
        "",
        md_table(health, ["embedding", "skew_abs", "excess_kurt_abs", "effective_rank", "rank_fraction", "cov_eig_cv", "cov_condition"], 10),
        "",
        "## Downstream Target Summary",
        "",
        md_table(target_summary, ["target", "best_feature", "best_mode", "best_c_value", "best_weight", "best_delta_vs_base", "best_mean_delta", "best_win_rate"], 10),
        "",
        "## Geometry-Stressed Candidates",
        "",
        md_table(
            geom_df.sort_values(["passes_e217_probe", "geometry_delta_mean", "delta_vs_base"], ascending=[False, True, True])
            if not geom_df.empty
            else geom_df,
            [
                "target",
                "feature",
                "mode",
                "c_value",
                "best_weight",
                "delta_vs_base",
                "mean_delta",
                "win_rate",
                "geometry_delta_mean",
                "geometry_win_rate",
                "passes_e217_probe",
            ],
            24,
        ),
        "",
        "## Decision",
        "",
        f"- materialization gate pass count: `{pass_count}`",
    ]
    if pass_count:
        best = geom_df[geom_df["passes_e217_probe"]].sort_values(["geometry_delta_mean", "delta_vs_base"]).iloc[0]
        lines.append(
            f"- E217 produced a geometry-safe teacher-student JEPA signal: `{best['feature']}` for `{best['target']}`. Next step is frontier materialization against E95/E154 hard-tail stress."
        )
    else:
        if not best_target.empty:
            row = best_target.iloc[0]
            lines.append(
                f"- E217 has local signal (`{row['target']}` via `{row['best_feature']}`, delta `{row['best_delta_vs_base']:.6g}`) but no geometry-safe materialization gate yet."
            )
        lines.append("- This would weaken full teacher-student JEPA as an immediate submission source, while still keeping its energy features as diagnostics.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    torch.set_num_threads(1)
    train_raw, sub_raw, train_feat, sub_feat = stage2.build_frames()
    rows = e207.make_rows(train_raw, sub_raw)
    context, families = e215.build_family_context(train_feat, sub_feat)
    neighbor_mean, neighbor_delta, neighbor_summary = same_subject_neighbor_context(rows, context)
    # Meta columns are intentionally not placed in the teacher target input; they are context-only clues.
    row_meta = StandardScaler().fit_transform(
        np.column_stack(
            [
                np.linalg.norm(neighbor_mean, axis=1),
                np.linalg.norm(neighbor_delta, axis=1),
                np.sum(np.abs(neighbor_mean) > 1.0e-12, axis=1),
            ]
        )
    )
    row_meta = finite(row_meta)
    specs = make_mask_specs(families)

    context_meta = pd.DataFrame([family.__dict__ for family in families])
    mask_meta = pd.DataFrame(
        [
            {
                "name": spec.name,
                "families": ",".join(families[i].family for i in spec.family_indices),
                "n_families": len(spec.family_indices),
            }
            for spec in specs
        ]
    )

    seeds = [SEED + 11, SEED + 29, SEED + 47]
    results = [
        train_teacher_student_jepa(context, neighbor_mean, neighbor_delta, row_meta, families, specs, seed=s)
        for s in seeds
    ]
    train_diag = pd.DataFrame(
        [
            {
                "seed": r.seed,
                "train_loss": r.train_loss,
                "val_loss": r.val_loss,
                "mean_teacher_loss": r.mean_teacher_loss,
                "shuffled_teacher_loss": r.shuffled_teacher_loss,
                "val_vs_mean_teacher_ratio": r.val_loss / max(r.mean_teacher_loss, 1e-12),
                "val_vs_shuffled_teacher_ratio": r.val_loss / max(r.shuffled_teacher_loss, 1e-12),
                "context_var_penalty": r.context_var_penalty,
                "pred_var_penalty": r.pred_var_penalty,
                "target_var_penalty": r.target_var_penalty,
                "context_cov_penalty": r.context_cov_penalty,
                "target_cov_penalty": r.target_cov_penalty,
                "epochs": r.epochs,
            }
            for r in results
        ]
    )
    feature_df, health = build_feature_frame(rows, results, specs)
    feature_df.iloc[: len(train_raw)].to_parquet(TRAIN_FEATURES_OUT, index=False)
    feature_df.iloc[len(train_raw) :].to_parquet(SUB_FEATURES_OUT, index=False)

    scan, geom_df, target_summary = downstream_scan(train_raw, sub_raw, feature_df.iloc[: len(train_raw)].reset_index(drop=True))

    context_meta.to_csv(CONTEXT_OUT, index=False)
    mask_meta.to_csv(MASK_OUT, index=False)
    train_diag.to_csv(TRAINING_OUT, index=False)
    health.to_csv(GEOMETRY_HEALTH_OUT, index=False)
    scan.to_csv(SCAN_OUT, index=False)
    geom_df.to_csv(DOWNSTREAM_GEOM_OUT, index=False)
    target_summary.to_csv(TARGET_OUT, index=False)
    META_OUT.write_text(
        json.dumps(
            {
                "seeds": seeds,
                "n_rows": int(len(rows)),
                "n_train": int(len(train_raw)),
                "n_submission": int(len(sub_raw)),
                "context_dim": int(context.shape[1]),
                "input_dim": int(context.shape[1] * 3 + row_meta.shape[1] + len(families)),
                "n_families": int(len(families)),
                "n_masks": int(len(specs)),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(rows, context_meta, mask_meta, neighbor_summary, train_diag, health, target_summary, geom_df)

    print("[training]")
    print(train_diag.round(9).to_string(index=False))
    print("\n[target summary]")
    print(target_summary.round(9).to_string(index=False))
    print("\n[geometry top]")
    if geom_df.empty:
        print("empty")
    else:
        cols = [
            "target",
            "feature",
            "mode",
            "c_value",
            "best_weight",
            "delta_vs_base",
            "mean_delta",
            "win_rate",
            "geometry_delta_mean",
            "geometry_win_rate",
            "passes_e217_probe",
        ]
        print(
            geom_df.sort_values(["passes_e217_probe", "geometry_delta_mean", "delta_vs_base"], ascending=[False, True, True])[
                cols
            ]
            .head(24)
            .round(9)
            .to_string(index=False)
        )
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
