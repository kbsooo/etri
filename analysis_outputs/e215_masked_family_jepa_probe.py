#!/usr/bin/env python3
"""E215: masked feature-family JEPA probe.

E208 used feature-neighbor targets in a broad latent space. E213 showed that
the surviving Q3/S4 axes are specific, while E214 showed that a generic
benefit gate does not fix the probability translation.

This probe changes the JEPA target itself. It masks one feature-family
representation at a time and predicts that held-out family representation from
the remaining families. The goal is not raw reconstruction; each family is a
PCA representation block. If this objective captures the hidden generating
state better than E208, its residual/predicted latent features should survive
the same downstream OOF, subject-half, and geometry stress.
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
import e208_feature_neighbor_jepa_probe as e208  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
SEED = 291215

TRAIN_FEATURES_OUT = OUT / "e215_masked_family_jepa_train_features.parquet"
SUB_FEATURES_OUT = OUT / "e215_masked_family_jepa_submission_features.parquet"
TRAINING_OUT = OUT / "e215_masked_family_jepa_training_summary.csv"
CONTEXT_OUT = OUT / "e215_masked_family_jepa_context_summary.csv"
GEOMETRY_HEALTH_OUT = OUT / "e215_masked_family_jepa_geometry_health_summary.csv"
SCAN_OUT = OUT / "e215_masked_family_jepa_downstream_scan_summary.csv"
DOWNSTREAM_GEOM_OUT = OUT / "e215_masked_family_jepa_downstream_geometry_summary.csv"
TARGET_OUT = OUT / "e215_masked_family_jepa_target_summary.csv"
REPORT_OUT = OUT / "e215_masked_family_jepa_report.md"
META_OUT = OUT / "e215_masked_family_jepa_meta.json"


@dataclass(frozen=True)
class FamilyBlock:
    family: str
    start: int
    end: int
    columns: int
    components: int
    explained_variance: float


@dataclass(frozen=True)
class TrainResult:
    seed: int
    train_mse: float
    val_mse: float
    copy_visible_mse: float
    mean_block_mse: float
    hidden_var_penalty: float
    pred_var_penalty: float
    hidden_cov_penalty: float
    epochs: int
    hidden_by_mask: np.ndarray
    pred_by_mask: np.ndarray


class MaskedFamilyJEPA(torch.nn.Module):
    def __init__(self, input_dim: int, family_count: int, hidden_dim: int, emb_dim: int, output_dim: int) -> None:
        super().__init__()
        self.encoder = torch.nn.Sequential(
            torch.nn.Linear(input_dim + family_count, hidden_dim),
            torch.nn.GELU(),
            torch.nn.LayerNorm(hidden_dim),
            torch.nn.Linear(hidden_dim, emb_dim),
        )
        self.predictor = torch.nn.Sequential(
            torch.nn.LayerNorm(emb_dim),
            torch.nn.Linear(emb_dim, hidden_dim),
            torch.nn.GELU(),
            torch.nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor, mask_onehot: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(torch.cat([x, mask_onehot], dim=1))
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


def build_family_context(train_feat: pd.DataFrame, sub_feat: pd.DataFrame) -> tuple[np.ndarray, list[FamilyBlock]]:
    all_feat = pd.concat([train_feat, sub_feat], axis=0, ignore_index=True)
    cols = e207.numeric_feature_cols(all_feat)
    by_family: dict[str, list[str]] = {}
    for col in cols:
        by_family.setdefault(e208.family_name(col), []).append(col)

    blocks: list[np.ndarray] = []
    families: list[FamilyBlock] = []
    start = 0
    for fam, fam_cols in sorted(by_family.items()):
        if len(fam_cols) < 12:
            continue
        x, raw_cols = e207.scaled_matrix(all_feat, fam_cols, top_cols=900)
        n_comp = int(min(10, max(3, len(fam_cols) // 35), x.shape[0] - 2, x.shape[1]))
        if n_comp < 3:
            continue
        pca = PCA(n_components=n_comp, svd_solver="randomized", random_state=SEED + len(families))
        z = pca.fit_transform(x)
        z = StandardScaler().fit_transform(z)
        z = finite(z)
        blocks.append(z)
        end = start + z.shape[1]
        families.append(
            FamilyBlock(
                family=fam,
                start=start,
                end=end,
                columns=int(raw_cols),
                components=int(z.shape[1]),
                explained_variance=float(np.sum(pca.explained_variance_ratio_)),
            )
        )
        start = end

    if not blocks:
        raise ValueError("no feature-family blocks")
    context = np.hstack(blocks)
    context = StandardScaler().fit_transform(context)
    return finite(context), families


def masked_input(context: np.ndarray, family: FamilyBlock) -> np.ndarray:
    x = context.copy()
    x[:, family.start : family.end] = 0.0
    return x


def training_samples(n_rows: int, n_families: int) -> tuple[np.ndarray, np.ndarray]:
    row_idx = np.repeat(np.arange(n_rows), n_families)
    fam_idx = np.tile(np.arange(n_families), n_rows)
    return row_idx, fam_idx


def masked_loss(pred: torch.Tensor, target: torch.Tensor, fam_idx: torch.Tensor, families: list[FamilyBlock]) -> torch.Tensor:
    losses = []
    for k, family in enumerate(families):
        sel = fam_idx == k
        if bool(sel.any()):
            losses.append(torch.nn.functional.mse_loss(pred[sel, family.start : family.end], target[sel, family.start : family.end]))
    if not losses:
        return pred.sum() * 0.0
    return torch.stack(losses).mean()


def train_masked_family_jepa(
    context: np.ndarray,
    families: list[FamilyBlock],
    seed: int,
    emb_dim: int = 32,
    epochs: int = 560,
) -> TrainResult:
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    device = torch.device("cpu")
    x_all_np = np.stack([masked_input(context, family) for family in families], axis=1)
    x_all = torch.tensor(x_all_np, dtype=torch.float32, device=device)
    t_all = torch.tensor(context, dtype=torch.float32, device=device)
    rows, fams = training_samples(len(context), len(families))
    order = rng.permutation(len(rows))
    val_size = max(80, int(round(0.20 * len(order))))
    val_sel = order[:val_size]
    tr_sel = order[val_size:]

    tr_rows = torch.tensor(rows[tr_sel], dtype=torch.long, device=device)
    tr_fams = torch.tensor(fams[tr_sel], dtype=torch.long, device=device)
    va_rows = torch.tensor(rows[val_sel], dtype=torch.long, device=device)
    va_fams = torch.tensor(fams[val_sel], dtype=torch.long, device=device)
    family_eye = torch.eye(len(families), dtype=torch.float32, device=device)

    model = MaskedFamilyJEPA(context.shape[1], len(families), hidden_dim=112, emb_dim=emb_dim, output_dim=context.shape[1]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=1.6e-3, weight_decay=1.0e-4)
    best_state: dict[str, torch.Tensor] | None = None
    best_val = float("inf")
    bad_epochs = 0
    for epoch in range(epochs):
        model.train()
        z, pred = model(x_all[tr_rows, tr_fams], family_eye[tr_fams])
        loss_pred = masked_loss(pred, t_all[tr_rows], tr_fams, families)
        loss = loss_pred + 0.025 * variance_penalty(z) + 0.010 * covariance_penalty(z) + 0.010 * variance_penalty(pred)
        opt.zero_grad()
        loss.backward()
        opt.step()

        if epoch % 10 == 0 or epoch == epochs - 1:
            model.eval()
            with torch.no_grad():
                z_val, pred_val = model(x_all[va_rows, va_fams], family_eye[va_fams])
                val_loss = masked_loss(pred_val, t_all[va_rows], va_fams, families).item()
                val_loss += 0.002 * variance_penalty(z_val).item()
            if val_loss < best_val - 1e-6:
                best_val = val_loss
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                bad_epochs = 0
            else:
                bad_epochs += 10
            if bad_epochs >= 160:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    hidden_parts: list[np.ndarray] = []
    pred_parts: list[np.ndarray] = []
    with torch.no_grad():
        for fam_i, family in enumerate(families):
            fam_vec = torch.full((len(context),), fam_i, dtype=torch.long, device=device)
            z, pred = model(x_all[:, fam_i], family_eye[fam_vec])
            hidden_parts.append(finite(z.cpu().numpy()))
            pred_parts.append(finite(pred.cpu().numpy()))
        z_tr, pred_tr = model(x_all[tr_rows, tr_fams], family_eye[tr_fams])
        z_va, pred_va = model(x_all[va_rows, va_fams], family_eye[va_fams])
        train_mse = masked_loss(pred_tr, t_all[tr_rows], tr_fams, families).item()
        val_mse = masked_loss(pred_va, t_all[va_rows], va_fams, families).item()
        hv = variance_penalty(torch.cat([torch.tensor(h, dtype=torch.float32, device=device) for h in hidden_parts], dim=0)).item()
        pv = variance_penalty(torch.cat([torch.tensor(p, dtype=torch.float32, device=device) for p in pred_parts], dim=0)).item()
        hc = covariance_penalty(torch.cat([torch.tensor(h, dtype=torch.float32, device=device) for h in hidden_parts], dim=0)).item()

    copy_losses = []
    mean_losses = []
    for family in families:
        block = context[:, family.start : family.end]
        copy_losses.append(float(np.mean(block**2)))
        mean_block = block[rows[tr_sel[fams[tr_sel] == families.index(family)]]].mean(axis=0, keepdims=True)
        mean_losses.append(float(np.mean((block - mean_block) ** 2)))
    return TrainResult(
        seed=seed,
        train_mse=float(train_mse),
        val_mse=float(val_mse),
        copy_visible_mse=float(np.mean(copy_losses)),
        mean_block_mse=float(np.mean(mean_losses)),
        hidden_var_penalty=float(hv),
        pred_var_penalty=float(pv),
        hidden_cov_penalty=float(hc),
        epochs=int(epoch + 1),
        hidden_by_mask=np.stack(hidden_parts, axis=1),
        pred_by_mask=np.stack(pred_parts, axis=1),
    )


def assemble_masked_prediction(result: TrainResult, context: np.ndarray, families: list[FamilyBlock]) -> np.ndarray:
    out = np.zeros_like(context)
    for fam_i, family in enumerate(families):
        out[:, family.start : family.end] = result.pred_by_mask[:, fam_i, family.start : family.end]
    return finite(out)


def pca_features(prefix: str, matrix: np.ndarray, max_comp: int) -> dict[str, np.ndarray]:
    n_comp = min(max_comp, matrix.shape[0] - 2, matrix.shape[1])
    if n_comp <= 0:
        return {}
    z = PCA(n_components=n_comp, svd_solver="randomized", random_state=SEED + len(prefix)).fit_transform(finite(matrix))
    z = StandardScaler().fit_transform(z)
    return {f"{prefix}{k:02d}": z[:, k] for k in range(n_comp)}


def build_feature_frame(rows: pd.DataFrame, context: np.ndarray, families: list[FamilyBlock], results: list[TrainResult]) -> tuple[pd.DataFrame, pd.DataFrame]:
    pred_stack = np.stack([assemble_masked_prediction(r, context, families) for r in results], axis=0)
    hidden_stack = np.stack([r.hidden_by_mask.mean(axis=1) for r in results], axis=0)
    pred_mean = finite(pred_stack.mean(axis=0))
    pred_std = finite(pred_stack.std(axis=0))
    hidden_mean = finite(hidden_stack.mean(axis=0))
    residual = finite(pred_mean - context)

    fmap: dict[str, np.ndarray] = {
        "e215_pred_norm": np.linalg.norm(pred_mean, axis=1),
        "e215_hidden_norm": np.linalg.norm(hidden_mean, axis=1),
        "e215_pred_seed_std": pred_std.mean(axis=1),
        "e215_resid_norm": np.linalg.norm(residual, axis=1),
        "e215_resid_abs_mean": np.abs(residual).mean(axis=1),
        "e215_pred_to_context_cos": np.sum(pred_mean * context, axis=1) / np.maximum(np.linalg.norm(pred_mean, axis=1) * np.linalg.norm(context, axis=1), 1e-9),
    }
    fmap.update(pca_features("e215_pred_pc", pred_mean, 16))
    fmap.update(pca_features("e215_resid_pc", residual, 16))
    fmap.update(pca_features("e215_hidden_z", hidden_mean, 12))

    for family in families:
        block_pred = pred_mean[:, family.start : family.end]
        block_resid = residual[:, family.start : family.end]
        fam = family.family.replace("-", "_")
        fmap[f"e215_{fam}_pred_norm"] = np.linalg.norm(block_pred, axis=1)
        fmap[f"e215_{fam}_resid_norm"] = np.linalg.norm(block_resid, axis=1)
        fmap[f"e215_{fam}_resid_abs_mean"] = np.abs(block_resid).mean(axis=1)
        for k in range(min(6, family.components)):
            fmap[f"e215_{fam}_pred_z{k:02d}"] = block_pred[:, k]
            fmap[f"e215_{fam}_resid_z{k:02d}"] = block_resid[:, k]

    feature_df = pd.concat([rows[SUB_KEY].reset_index(drop=True), pd.DataFrame(fmap)], axis=1)
    rng = np.random.default_rng(SEED + 215)
    health_rows = []
    for name, matrix in {"pred_mean": pred_mean, "hidden_mean": hidden_mean, "residual": residual}.items():
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
    cols = [c for c in df.columns if c.startswith("e215_")]
    pre = broad.prefilter(df, base, cols, TARGETS, top_n=20)
    y = train_raw[TARGETS].to_numpy(dtype=int)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.10, 0.20]:
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
    for op in scan[(scan["best_weight"] > 0) & (scan["delta_vs_base"] < -0.00025)].head(18).to_dict(orient="records"):
        enriched = dict(op)
        enriched.update(geometry_summary(train_raw, sub_raw, df, base, op))
        geom_rows.append(enriched)
    geom_df = pd.DataFrame(geom_rows)
    if not geom_df.empty:
        geom_df["passes_e215_probe"] = (
            (geom_df["delta_vs_base"] <= -0.00045)
            & (geom_df["mean_delta"] <= -0.00010)
            & (geom_df["win_rate"] >= 0.62)
            & (geom_df["geometry_delta_mean"] <= 0.0)
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
    train_diag: pd.DataFrame,
    health: pd.DataFrame,
    target_summary: pd.DataFrame,
    geom_df: pd.DataFrame,
) -> None:
    pass_count = int(geom_df["passes_e215_probe"].sum()) if "passes_e215_probe" in geom_df else 0
    lines = [
        "# E215 Masked Family JEPA Probe",
        "",
        "## Purpose",
        "",
        "Train an I-JEPA-style masked feature-family objective: context is all visible feature-family PCA blocks, target is the hidden family representation block. This tests whether changing the JEPA target representation creates broader or cleaner downstream target signal than E208's feature-neighbor target.",
        "",
        "## Data",
        "",
        f"- rows: `{len(rows)}` train+submission rows",
        f"- context families: `{len(context_meta)}`",
        "",
        "## Context Families",
        "",
        md_table(context_meta, ["family", "columns", "components", "explained_variance"], 20),
        "",
        "## JEPA Training Diagnostics",
        "",
        md_table(
            train_diag,
            [
                "seed",
                "train_mse",
                "val_mse",
                "copy_visible_mse",
                "mean_block_mse",
                "hidden_var_penalty",
                "pred_var_penalty",
                "hidden_cov_penalty",
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
            geom_df.sort_values(["passes_e215_probe", "geometry_delta_mean", "delta_vs_base"], ascending=[False, True, True])
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
                "passes_e215_probe",
            ],
            18,
        ),
        "",
        "## Decision",
        "",
        f"- materialization gate pass count: `{pass_count}`",
    ]
    if pass_count:
        lines.append("- E215 found downstream-stressed masked-family JEPA features. Compare them against E208/E211 before materialization; this objective is a representation candidate, not a direct submission yet.")
    else:
        lines.append("- E215 did not find a geometry-safe improvement. This weakens masked feature-family JEPA as the next representation target.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    torch.set_num_threads(1)
    train_raw, sub_raw, train_feat, sub_feat = stage2.build_frames()
    rows = e207.make_rows(train_raw, sub_raw)
    context, families = build_family_context(train_feat, sub_feat)
    context_meta = pd.DataFrame([family.__dict__ for family in families])

    seeds = [SEED + 3, SEED + 19, SEED + 41]
    results = [train_masked_family_jepa(context, families, seed=s) for s in seeds]
    train_diag = pd.DataFrame(
        [
            {
                "seed": r.seed,
                "train_mse": r.train_mse,
                "val_mse": r.val_mse,
                "copy_visible_mse": r.copy_visible_mse,
                "mean_block_mse": r.mean_block_mse,
                "hidden_var_penalty": r.hidden_var_penalty,
                "pred_var_penalty": r.pred_var_penalty,
                "hidden_cov_penalty": r.hidden_cov_penalty,
                "epochs": r.epochs,
                "val_vs_mean_block_ratio": r.val_mse / max(r.mean_block_mse, 1e-12),
            }
            for r in results
        ]
    )
    feature_df, health = build_feature_frame(rows, context, families, results)
    feature_df.iloc[: len(train_raw)].to_parquet(TRAIN_FEATURES_OUT, index=False)
    feature_df.iloc[len(train_raw) :].to_parquet(SUB_FEATURES_OUT, index=False)

    scan, downstream_geom, target_summary = downstream_scan(train_raw, sub_raw, feature_df)
    train_diag.to_csv(TRAINING_OUT, index=False)
    context_meta.to_csv(CONTEXT_OUT, index=False)
    health.to_csv(GEOMETRY_HEALTH_OUT, index=False)
    scan.to_csv(SCAN_OUT, index=False)
    downstream_geom.to_csv(DOWNSTREAM_GEOM_OUT, index=False)
    target_summary.to_csv(TARGET_OUT, index=False)
    META_OUT.write_text(
        json.dumps(
            {
                "train_rows": int(len(train_raw)),
                "submission_rows": int(len(sub_raw)),
                "context_dim": int(context.shape[1]),
                "family_count": int(len(families)),
                "seeds": seeds,
                "materialization_gate_pass_count": int(downstream_geom["passes_e215_probe"].sum())
                if "passes_e215_probe" in downstream_geom
                else 0,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    write_report(rows, context_meta, train_diag, health, target_summary, downstream_geom)

    print("[training]")
    print(train_diag.round(6).to_string(index=False))
    print("\n[target summary]")
    print(target_summary.round(9).to_string(index=False))
    if not downstream_geom.empty:
        cols = [
            "target",
            "feature",
            "mode",
            "best_weight",
            "delta_vs_base",
            "mean_delta",
            "win_rate",
            "geometry_delta_mean",
            "passes_e215_probe",
        ]
        print("\n[geometry]")
        print(downstream_geom.sort_values(["passes_e215_probe", "geometry_delta_mean"], ascending=[False, True])[cols].round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
