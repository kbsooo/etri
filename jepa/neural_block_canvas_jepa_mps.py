from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
import torch
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


def safe_label(x: float) -> str:
    return str(x).replace("-", "m").replace(".", "p")


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def block_label_stats(y: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = y[block]
    rates = np.nanmean(vals, axis=0)
    rates = np.nan_to_num(rates, nan=0.5)
    ent = -(rates * np.log(adv.clip(rates)) + (1.0 - rates) * np.log(adv.clip(1.0 - rates)))
    first = vals[0]
    last = vals[-1]
    change = last - first
    return np.r_[rates, ent, first, last, change].astype(np.float32)


class DualHeadJEPA(nn.Module):
    def __init__(self, in_dim: int, raw_dim: int, label_dim: int, hidden: int = 384, dropout: float = 0.06):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.LayerNorm(hidden),
            nn.SiLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden),
            nn.LayerNorm(hidden),
            nn.SiLU(),
            nn.Dropout(dropout),
        )
        self.raw_head = nn.Linear(hidden, raw_dim)
        self.label_head = nn.Linear(hidden, label_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.backbone(x)
        return self.raw_head(h), self.label_head(h)


def fit_predict_dual_head(
    x_train: np.ndarray,
    raw_target: np.ndarray,
    label_target: np.ndarray,
    x_pred: np.ndarray,
    seed: int,
    epochs: int = 220,
    label_weight: float = 0.65,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    dev = device()
    sx = StandardScaler()
    sr = StandardScaler()
    sl = StandardScaler()
    x = sx.fit_transform(finite(x_train)).astype(np.float32)
    xp = sx.transform(finite(x_pred)).astype(np.float32)
    yr = sr.fit_transform(finite(raw_target)).astype(np.float32)
    yl = sl.fit_transform(finite(label_target)).astype(np.float32)

    xt = torch.from_numpy(x).to(dev)
    rt = torch.from_numpy(yr).to(dev)
    lt = torch.from_numpy(yl).to(dev)
    model = DualHeadJEPA(x.shape[1], yr.shape[1], yl.shape[1]).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=2.5e-3, weight_decay=1.0e-3)
    batch = min(256, len(x))
    for epoch in range(epochs):
        model.train()
        order = rng.permutation(len(x))
        for start in range(0, len(x), batch):
            idx_np = order[start : start + batch]
            idx = torch.from_numpy(idx_np).to(dev)
            pr, pl = model(xt.index_select(0, idx))
            loss_raw = torch.mean((pr - rt.index_select(0, idx)) ** 2)
            loss_label = torch.mean((pl - lt.index_select(0, idx)) ** 2)
            loss = loss_raw + label_weight * loss_label
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
        if epoch in {140, 185}:
            for group in opt.param_groups:
                group["lr"] *= 0.45

    model.eval()
    with torch.no_grad():
        xp_t = torch.from_numpy(xp).to(dev)
        raw_pred, label_pred = model(xp_t)
    raw_np = sr.inverse_transform(raw_pred.detach().cpu().numpy()).astype(np.float32)
    label_np = sl.inverse_transform(label_pred.detach().cpu().numpy()).astype(np.float32)
    return raw_np, label_np


def predict_blocks(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    train_indices: np.ndarray,
    pred_blocks: list[np.ndarray],
    lengths: dict[str, list[int]],
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    known = adv.known_mask_for_train(rows, train_indices)
    train_blocks = adv.make_training_blocks(rows, y, train_indices, lengths, max_blocks_per_subject=240)
    if not train_blocks or not pred_blocks:
        return (
            np.full((len(pred_blocks), bcj.summary_dim(z.shape[1])), np.nan, dtype=np.float32),
            np.full((len(pred_blocks), len(TARGETS) * 5), np.nan, dtype=np.float32),
        )
    x_train = np.vstack([bcj.context_for_block(rows, z, y, base_all, b, known) for b in train_blocks])
    raw_target = np.vstack([bcj.summarize_z(z, b) for b in train_blocks])
    label_target = np.vstack([block_label_stats(y, b) for b in train_blocks])
    x_pred = np.vstack([bcj.context_for_block(rows, z, y, base_all, b, known) for b in pred_blocks])
    return fit_predict_dual_head(x_train, raw_target, label_target, x_pred, seed=seed)


def ensure_store(store: dict[str, np.ndarray], name: str, n_rows: int) -> np.ndarray:
    if name not in store:
        store[name] = np.full(n_rows, np.nan, dtype=np.float32)
    return store[name]


def assign_features(
    store: dict[str, np.ndarray],
    n_rows: int,
    prefix: str,
    z: np.ndarray,
    blocks: list[np.ndarray],
    row_indices: list[np.ndarray],
    raw_pred: np.ndarray,
    label_pred: np.ndarray,
    max_latent: int = 22,
) -> None:
    z_dim = z.shape[1]
    for block_i, block in enumerate(blocks):
        actual = bcj.summarize_z(z, block)
        pred = raw_pred[block_i]
        resid = actual - pred
        pred_mean = pred[:z_dim]
        actual_mean = actual[:z_dim]
        resid_mean = resid[:z_dim]
        label = label_pred[block_i]
        idxs = np.asarray(row_indices[block_i], dtype=int)
        rel = np.linspace(0.0, 1.0, len(idxs)) if len(idxs) > 1 else np.zeros(len(idxs))
        for local, row_i in enumerate(idxs):
            row_z = z[block[local]]
            ensure_store(store, f"{prefix}_pos", n_rows)[row_i] = rel[local]
            ensure_store(store, f"{prefix}_len", n_rows)[row_i] = len(idxs)
            ensure_store(store, f"{prefix}_resid_norm", n_rows)[row_i] = float(np.linalg.norm(resid_mean))
            ensure_store(store, f"{prefix}_row_resid_norm", n_rows)[row_i] = float(np.linalg.norm(row_z - pred_mean))
            ensure_store(store, f"{prefix}_actual_norm", n_rows)[row_i] = float(np.linalg.norm(actual_mean))
            ensure_store(store, f"{prefix}_pred_norm", n_rows)[row_i] = float(np.linalg.norm(pred_mean))
            denom = float(np.linalg.norm(actual_mean) * np.linalg.norm(pred_mean))
            ensure_store(store, f"{prefix}_cos", n_rows)[row_i] = float(np.dot(actual_mean, pred_mean) / max(denom, 1e-9))
            for k in range(min(max_latent, z_dim)):
                ensure_store(store, f"{prefix}_pred_{k:02d}", n_rows)[row_i] = pred_mean[k]
                ensure_store(store, f"{prefix}_resid_{k:02d}", n_rows)[row_i] = resid_mean[k]
                ensure_store(store, f"{prefix}_absresid_{k:02d}", n_rows)[row_i] = abs(resid_mean[k])
                ensure_store(store, f"{prefix}_row_resid_{k:02d}", n_rows)[row_i] = row_z[k] - pred_mean[k]
            for j, target in enumerate(TARGETS):
                ensure_store(store, f"{prefix}_label_rate_{target}", n_rows)[row_i] = np.clip(label[j], 1e-4, 1.0 - 1e-4)
                ensure_store(store, f"{prefix}_label_entropy_{target}", n_rows)[row_i] = label[7 + j]
                ensure_store(store, f"{prefix}_label_first_{target}", n_rows)[row_i] = np.clip(label[14 + j], 1e-4, 1.0 - 1e-4)
                ensure_store(store, f"{prefix}_label_last_{target}", n_rows)[row_i] = np.clip(label[21 + j], 1e-4, 1.0 - 1e-4)
                ensure_store(store, f"{prefix}_label_change_{target}", n_rows)[row_i] = label[28 + j]


def build_features(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    repeats: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    lengths = adv.actual_lengths_by_subject(rows)
    train_feat = train[SUB_KEY + TARGETS].copy()
    sub_feat = sub[SUB_KEY].copy()
    prefix = "nbcj_mps"
    train_data: dict[str, np.ndarray] = {}
    cover = np.zeros(len(train), dtype=int)
    for fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=293501)):
        val_blocks = adv.contiguous_val_blocks(rows, val_idx)
        if not val_blocks:
            continue
        raw_pred, label_pred = predict_blocks(rows, z, y, base_all, tr_idx, val_blocks, lengths, seed=293900 + fold_i)
        row_indices = [rows.iloc[b]["train_idx"].to_numpy(dtype=int) for b in val_blocks]
        assign_features(train_data, len(train), prefix, z, val_blocks, row_indices, raw_pred, label_pred)
        for idxs in row_indices:
            cover[idxs] += 1
        print(f"neural-block-canvas {fold}: val_blocks={len(val_blocks)} covered={int((cover > 0).sum())}", flush=True)
    train_feat = pd.concat([train_feat, pd.DataFrame(train_data, index=np.arange(len(train)))], axis=1)

    sub_blocks = adv.submission_blocks(train, sub, rows)
    raw_sub, label_sub = predict_blocks(rows, z, y, base_all, np.arange(len(train)), sub_blocks, lengths, seed=294999)
    sub_indices = [rows.iloc[b]["sub_idx"].to_numpy(dtype=int) for b in sub_blocks]
    sub_data: dict[str, np.ndarray] = {}
    assign_features(sub_data, len(sub), prefix, z, sub_blocks, sub_indices, raw_sub, label_sub)
    sub_feat = pd.concat([sub_feat, pd.DataFrame(sub_data, index=np.arange(len(sub)))], axis=1)
    return train_feat.copy(), sub_feat.copy()


def axis_stats(file_name: str) -> dict[str, float]:
    try:
        base_sub = pd.read_csv(adv.BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        cand = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        base_logit = adv.logit(base_sub[TARGETS].to_numpy(dtype=float))
        move = adv.logit(cand[TARGETS].to_numpy(dtype=float)) - base_logit
        bad_parts = []
        weights = []
        for bad_name, score in [
            ("submission_jepa_latent_residual_probe.csv", 0.5812273278),
            ("submission_jepa_latent_q2_w0p45.csv", 0.5798012862),
        ]:
            bad = pd.read_csv(OUT / bad_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
            bad_parts.append(adv.logit(bad[TARGETS].to_numpy(dtype=float)) - base_logit)
            weights.append(max(score - STAGE2_PUBLIC, 1e-9))
        bad_axis = np.average(np.stack(bad_parts), axis=0, weights=np.asarray(weights))
        good = pd.read_csv(OUT / "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        good_axis = adv.logit(good[TARGETS].to_numpy(dtype=float)) - base_logit
        out = {}
        for name, axis in [("jepa_bad", bad_axis), ("raw_good", good_axis)]:
            m = move.reshape(-1)
            a = axis.reshape(-1)
            out[f"{name}_ratio"] = float(np.dot(m, a) / max(float(np.dot(a, a)), 1e-12))
            out[f"{name}_cos"] = float(np.dot(m, a) / max(float(np.linalg.norm(m) * np.linalg.norm(a)), 1e-12))
        return out
    except Exception:
        return {"jepa_bad_ratio": np.nan, "jepa_bad_cos": np.nan, "raw_good_ratio": np.nan, "raw_good_cos": np.nan}


def scan_and_submit(train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base: np.ndarray, base_sub: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train_feat[TARGETS].to_numpy(dtype=int)
    cols = broad.finite_numeric_cols(train_feat)
    pre = broad.prefilter(train_feat, base, cols, TARGETS, top_n=60)
    pre.to_csv(OUT / "neural_block_canvas_jepa_mps_prefilter.csv", index=False)
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
                "base_loss": base_loss,
                "corrected_loss": broad.loss_col(y[:, j], corrected),
                "best_weight": float(broad.GRID[best_i]),
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(train_feat, y, base, corrected, j))
            else:
                row.update({"mean_delta": 0.0, "median_delta": 0.0, "p25_delta": 0.0, "p75_delta": 0.0, "win_rate": 0.0, "mean_selected_weight": 0.0, "zero_weight_rate": 1.0})
            row["passes_strict"] = bool(row["delta_vs_base"] <= -0.00035 and row["mean_delta"] <= -0.00005 and row["win_rate"] >= 0.62)
            row["passes_loose"] = bool(row["delta_vs_base"] <= -0.00015 and row["mean_delta"] < 0.0 and row["win_rate"] >= 0.56)
            rows.append(row)
    scan = pd.DataFrame(rows).sort_values(["passes_strict", "passes_loose", "delta_vs_base"], ascending=[False, False, True])
    scan.to_csv(OUT / "neural_block_canvas_jepa_mps_scan.csv", index=False)

    def apply_ops(ops: pd.DataFrame, file_name: str, scale: float) -> tuple[np.ndarray, pd.DataFrame]:
        pred = base.copy()
        sub_pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
        used = []
        for op in ops.itertuples(index=False):
            target = str(op.target)
            if target in {u["target"] for u in used}:
                continue
            j = TARGETS.index(target)
            w = float(op.best_weight) * scale
            corrected = broad.oof_corrected(train_feat, pred, target, str(op.feature), str(op.mode), float(op.c_value))
            pred[:, j] = adv.clip((1.0 - w) * pred[:, j] + w * corrected)
            sub_corr = broad.fit_corrected(train_feat, sub_feat, pred, sub_pred, target, str(op.feature), str(op.mode), float(op.c_value))
            sub_pred[:, j] = adv.clip((1.0 - w) * sub_pred[:, j] + w * sub_corr)
            used.append({"target": target, "feature": str(op.feature), "mode": str(op.mode), "c_value": float(op.c_value), "base_weight": float(op.best_weight), "scaled_weight": w, "delta_vs_base": float(op.delta_vs_base), "mean_delta": float(op.mean_delta), "win_rate": float(op.win_rate)})
        out = base_sub.copy()
        out[TARGETS] = sub_pred
        out.to_csv(OUT / file_name, index=False)
        pd.DataFrame(used).to_csv(OUT / file_name.replace("submission_", "").replace(".csv", "_ops.csv"), index=False)
        return pred, pd.DataFrame(used)

    strict = scan[(scan["passes_strict"]) & (scan["best_weight"] > 0)].sort_values("delta_vs_base")
    strict_noq2 = strict[~strict["target"].eq("Q2")]
    top = scan[scan["best_weight"] > 0].sort_values("delta_vs_base").groupby("target", group_keys=False).head(1)
    specs = []
    for label, ops in [("strict", strict), ("strict_noq2", strict_noq2), ("top_probe", top)]:
        for scale in [0.35, 0.5, 0.75, 1.0]:
            specs.append((label, ops, scale))
    base_loss = adv.mean_loss(y, base)
    summary_rows = []
    for label, ops, scale in specs:
        file_name = f"submission_neural_block_canvas_jepa_mps_{label}_scale{safe_label(scale)}.csv"
        pred, used = apply_ops(ops, file_name, scale)
        loss = adv.mean_loss(y, pred)
        summary_rows.append({"candidate": file_name, "class": label, "scale": scale, "ops": int(len(used)), "oof_loss": loss, "oof_delta_vs_stage2": loss - base_loss, **axis_stats(file_name)})
    summary = pd.DataFrame(summary_rows).sort_values(["jepa_bad_ratio", "oof_delta_vs_stage2"]).reset_index(drop=True)
    summary.to_csv(OUT / "neural_block_canvas_jepa_mps_candidate_summary.csv", index=False)
    return scan, summary


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, names = bcj.build_day_latent(rows, canvas)
    pd.DataFrame({"latent": names}).to_csv(OUT / "neural_block_canvas_jepa_mps_latent_meta.csv", index=False)
    print(f"neural-block-canvas device={device()} z_dim={z.shape[1]}", flush=True)
    train_feat, sub_feat = build_features(train, sub, rows, z, y, base_all)
    train_feat.to_parquet(OUT / "neural_block_canvas_jepa_mps_train_features.parquet", index=False)
    sub_feat.to_parquet(OUT / "neural_block_canvas_jepa_mps_submission_features.parquet", index=False)
    scan, summary = scan_and_submit(train_feat, sub_feat, base, base_sub)
    report = [
        "# Neural Block-Canvas JEPA MPS",
        "",
        "A PyTorch dual-head predictor uses the observed block/context canvas to predict both the hidden block raw latent and the hidden block label-rate latent. The neural JEPA latent is used only as residual/probe features, then filtered by OOF logloss and subject guardrails.",
        "",
        f"Device: `{device()}`",
        "",
        "## Candidate Summary",
        "",
        summary.to_csv(index=False),
        "",
        "## Best Scan Rows",
        "",
        scan.head(60).to_csv(index=False),
    ]
    (OUT / "neural_block_canvas_jepa_mps_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(20).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
