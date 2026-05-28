from __future__ import annotations

import sys
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import StandardScaler
from torch import nn


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(ANALYSIS))
import broad_single_feature_residual_probe as broad  # noqa: E402


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    pp = clip(p)
    yy = y.astype(float)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


class MaskedGridJEPA(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 24) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 96),
            nn.GELU(),
            nn.LayerNorm(96),
            nn.Linear(96, latent_dim),
            nn.Tanh(),
        )
        self.predictor = nn.Sequential(
            nn.Linear(latent_dim, 96),
            nn.GELU(),
            nn.LayerNorm(96),
            nn.Linear(96, input_dim),
        )

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        z = self.encoder(x)
        return z, self.predictor(z)


@dataclass(frozen=True)
class Op:
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float


def cell_tokens(col: str) -> tuple[str, str]:
    body = col.removeprefix("jepa_grid__").removesuffix("__value")
    sensor, time = body.rsplit("__", 1)
    return sensor, time


def load_grid() -> tuple[pd.DataFrame, pd.DataFrame, list[str], np.ndarray]:
    jtr = pd.read_parquet(OUT / "train_jepa_features.parquet")
    jsu = pd.read_parquet(OUT / "submission_jepa_features.parquet")
    grid_cols = [c for c in jtr.columns if c.startswith("jepa_grid__") and c.endswith("__value")]
    if len(grid_cols) < 20:
        raise RuntimeError(f"too few grid value columns: {len(grid_cols)}")
    all_grid = pd.concat([jtr[grid_cols], jsu[grid_cols]], axis=0, ignore_index=True)
    med = all_grid.median(numeric_only=True).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    vals = all_grid.replace([np.inf, -np.inf], np.nan).fillna(med).to_numpy(dtype=float)
    x = StandardScaler().fit_transform(vals)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    return jtr[SUB_KEY].copy(), jsu[SUB_KEY].copy(), grid_cols, x


def train_masked_model(x: np.ndarray, seed: int = 260991, epochs: int = 360) -> tuple[MaskedGridJEPA, list[dict[str, float]]]:
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = MaskedGridJEPA(x.shape[1])
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    xt = torch.from_numpy(x)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        mask = torch.rand_like(xt) < 0.35
        masked = xt.masked_fill(mask, 0.0)
        _, pred = model(masked)
        masked_loss = torch.mean((pred[mask] - xt[mask]) ** 2)
        context_loss = torch.mean((pred[~mask] - xt[~mask]) ** 2)
        loss = masked_loss + 0.05 * context_loss
        opt.zero_grad()
        loss.backward()
        opt.step()
        if epoch in {0, 49, 99, 179, epochs - 1}:
            history.append({"epoch": float(epoch + 1), "loss": float(loss.detach()), "masked_loss": float(masked_loss.detach())})
    return model.eval(), history


def group_indices(grid_cols: list[str]) -> dict[str, list[int]]:
    groups: dict[str, list[int]] = {}
    for idx, col in enumerate(grid_cols):
        sensor, time = cell_tokens(col)
        groups.setdefault(f"time__{time}", []).append(idx)
        groups.setdefault(f"sensor__{sensor}", []).append(idx)
    return {k: v for k, v in groups.items() if len(v) >= 4}


def add_block_prediction_features(model: MaskedGridJEPA, x: np.ndarray, grid_cols: list[str]) -> dict[str, np.ndarray]:
    xt = torch.from_numpy(x)
    features: dict[str, np.ndarray] = {}
    with torch.no_grad():
        z, full_pred = model(xt)
    z_np = z.numpy()
    full_resid = x - full_pred.numpy()
    for k in range(z_np.shape[1]):
        features[f"neural_jepa__full_z{k:02d}"] = z_np[:, k]
    features["neural_jepa__full_resid_norm"] = np.linalg.norm(full_resid, axis=1)
    features["neural_jepa__full_resid_abs_mean"] = np.mean(np.abs(full_resid), axis=1)

    for name, idxs in group_indices(grid_cols).items():
        masked = xt.clone()
        masked[:, idxs] = 0.0
        with torch.no_grad():
            z_ctx, pred = model(masked)
        target = x[:, idxs]
        pred_np = pred.numpy()[:, idxs]
        resid = target - pred_np
        target_norm = np.linalg.norm(target, axis=1)
        pred_norm = np.linalg.norm(pred_np, axis=1)
        resid_norm = np.linalg.norm(resid, axis=1)
        cos = np.sum(target * pred_np, axis=1) / np.maximum(target_norm * pred_norm, 1e-9)
        safe = name.replace("/", "_")
        features[f"neural_jepa_mask__{safe}__target_norm"] = target_norm
        features[f"neural_jepa_mask__{safe}__pred_norm"] = pred_norm
        features[f"neural_jepa_mask__{safe}__resid_norm"] = resid_norm
        features[f"neural_jepa_mask__{safe}__resid_abs_mean"] = np.mean(np.abs(resid), axis=1)
        features[f"neural_jepa_mask__{safe}__resid_mean"] = np.mean(resid, axis=1)
        features[f"neural_jepa_mask__{safe}__cos"] = cos
        # Context embedding movement: whether this block is structurally important for the full latent state.
        z_diff = z_np - z_ctx.numpy()
        features[f"neural_jepa_mask__{safe}__latent_shift_norm"] = np.linalg.norm(z_diff, axis=1)
    return features


def scan(train: pd.DataFrame, neural_train: pd.DataFrame, base: np.ndarray, top_n: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = train[SUB_KEY + TARGETS].merge(neural_train, on=SUB_KEY, how="left")
    cols = broad.finite_numeric_cols(df)
    y = df[TARGETS].to_numpy(dtype=int)
    pre = broad.prefilter(df, base, cols, TARGETS, top_n=top_n)
    pre.to_csv(OUT / "neural_jepa_prefilter.csv", index=False)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.20]:
            corrected = broad.oof_corrected(df, base, target, feature, mode, c_value)
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "corr": float(cand.corr),
                "c_value": c_value,
                "base_loss": base_loss,
                "best_weight": float(broad.GRID[best_i]),
                "best_blend_loss": float(losses[best_i]),
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
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.58)
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.0004 and row["mean_delta"] <= -0.00015 and row["win_rate"] >= 0.65)
            rows.append(row)
    result = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    result.to_csv(OUT / "neural_jepa_scan.csv", index=False)
    result.groupby("target", group_keys=False).head(10).to_csv(OUT / "neural_jepa_top.csv", index=False)
    result[result["passes_loose"]].to_csv(OUT / "neural_jepa_selected_features.csv", index=False)
    return df, result


def choose_ops(result: pd.DataFrame) -> list[Op]:
    selected = result[result["passes_strict"]].copy()
    if selected.empty:
        selected = result[result["passes_loose"]].copy()
    if selected.empty:
        return []
    selected = selected.sort_values(["passes_strict", "passes_loose", "mean_delta", "delta_vs_base"], ascending=[False, False, True, True])
    ops: list[Op] = []
    seen: set[str] = set()
    for row in selected.itertuples(index=False):
        target = str(row.target)
        if target in seen:
            continue
        ops.append(Op(target, str(row.feature), str(row.mode), float(row.c_value), float(row.best_weight)))
        seen.add(target)
    return ops


def apply_ops_oof(df: pd.DataFrame, base: np.ndarray, ops: list[Op]) -> np.ndarray:
    out = base.copy()
    for op in ops:
        j = TARGETS.index(op.target)
        corrected = broad.oof_corrected(df, out, op.target, op.feature, op.mode, op.c_value)
        out[:, j] = clip((1.0 - op.weight) * out[:, j] + op.weight * corrected)
    return out


def apply_ops_submission(train_df: pd.DataFrame, sub_df: pd.DataFrame, base_oof: np.ndarray, base_sub: pd.DataFrame, ops: list[Op]) -> pd.DataFrame:
    pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
    ref = base_oof.copy()
    for op in ops:
        j = TARGETS.index(op.target)
        corrected_sub = broad.fit_corrected(train_df, sub_df, ref, pred, op.target, op.feature, op.mode, op.c_value)
        pred[:, j] = clip((1.0 - op.weight) * pred[:, j] + op.weight * corrected_sub)
        corrected_ref = broad.fit_corrected(train_df, train_df, ref, ref, op.target, op.feature, op.mode, op.c_value)
        ref[:, j] = clip((1.0 - op.weight) * ref[:, j] + op.weight * corrected_ref)
    out = base_sub.copy()
    out[TARGETS] = clip(pred)
    return out


def write_report(meta: dict[str, object], result: pd.DataFrame, ops: list[Op], cv: pd.DataFrame) -> None:
    lines = [
        "# Neural Grid JEPA Probe",
        "",
        "Masked sensor-time grid prediction trained on train+submission features without labels.",
        "",
        f"- grid cells: `{meta['grid_cells']}`",
        f"- generated features: `{meta['feature_count']}`",
        f"- selected ops: `{len(ops)}`",
        "",
        "## Training",
        "",
        pd.DataFrame(meta["train_history"]).to_csv(index=False),
        "",
        "## Top Scan Rows",
        "",
        result.head(20).to_csv(index=False),
        "",
        "## CV Estimate",
        "",
        cv.to_csv(index=False),
    ]
    (OUT / "neural_jepa_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base = clip(np.load(ANALYSIS / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"))
    base_sub = pd.read_csv(ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].equals(sub[SUB_KEY])

    train_keys, sub_keys, grid_cols, x = load_grid()
    model, history = train_masked_model(x)
    feature_map = add_block_prediction_features(model, x, grid_cols)
    all_features = pd.concat([pd.concat([train_keys, sub_keys], axis=0, ignore_index=True), pd.DataFrame(feature_map)], axis=1)
    neural_train = train_keys.merge(all_features, on=SUB_KEY, how="left")
    neural_sub = sub_keys.merge(all_features, on=SUB_KEY, how="left")
    neural_train.to_parquet(OUT / "train_neural_jepa_features.parquet", index=False)
    neural_sub.to_parquet(OUT / "submission_neural_jepa_features.parquet", index=False)

    scan_df, result = scan(train, neural_train, base)
    ops = choose_ops(result)
    pred = apply_ops_oof(scan_df, base, ops) if ops else base.copy()
    y = train[TARGETS].to_numpy(dtype=int)
    cv_rows = []
    for j, target in enumerate(TARGETS):
        cv_rows.append(
            {
                "target": target,
                "base_loss": loss_col(y[:, j], base[:, j]),
                "candidate_loss": loss_col(y[:, j], pred[:, j]),
                "delta_vs_base": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base[:, j]),
            }
        )
    cv_rows.append({"target": "mean", "base_loss": mean_loss(y, base), "candidate_loss": mean_loss(y, pred), "delta_vs_base": mean_loss(y, pred) - mean_loss(y, base)})
    cv = pd.DataFrame(cv_rows)
    cv.to_csv(OUT / "neural_jepa_cv_estimate.csv", index=False)
    np.save(OUT / "neural_jepa_oof.npy", pred)
    train_df = train[SUB_KEY + TARGETS].merge(neural_train, on=SUB_KEY, how="left")
    sub_df = sub[SUB_KEY].merge(neural_sub, on=SUB_KEY, how="left")
    submission = apply_ops_submission(train_df, sub_df, base, base_sub, ops) if ops else base_sub.copy()
    submission.to_csv(OUT / "submission_neural_jepa_selected.csv", index=False)
    pd.DataFrame([op.__dict__ for op in ops]).to_csv(OUT / "neural_jepa_selected_ops.csv", index=False)

    meta = {"grid_cells": len(grid_cols), "feature_count": len(feature_map), "train_history": history}
    write_report(meta, result, ops, cv)
    print(pd.DataFrame(history).round(9).to_string(index=False))
    print(cv.round(9).to_string(index=False))
    print(result.head(15).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
