from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

STAGE2_PUBLIC = 0.5779449757
PUBLIC_KNOWN = {
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv": 0.5775263072,
    "submission_jepa_latent_residual_probe.csv": 0.5812273278,
    "submission_jepa_latent_q2_w0p45.csv": 0.5798012862,
}

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def pca_fit_transform(x: np.ndarray, n_components: int, seed: int) -> np.ndarray:
    xs = StandardScaler().fit_transform(finite(x))
    k = min(n_components, xs.shape[0] - 1, xs.shape[1])
    return PCA(n_components=k, random_state=seed, svd_solver="randomized").fit_transform(xs).astype(np.float32)


def build_day_latent(rows: pd.DataFrame, canvas: np.ndarray) -> tuple[np.ndarray, list[str]]:
    flat = canvas.reshape(len(rows), -1)
    z_full = pca_fit_transform(flat, 32, 280101)
    mobile = canvas[:, :9, :, :].reshape(len(rows), -1)
    wear = canvas[:, 9:, :, :].reshape(len(rows), -1)
    z_mobile = pca_fit_transform(mobile, 18, 280102)
    z_wear = pca_fit_transform(wear, 14, 280103)
    windows = {
        "day": slice(0, 12),
        "evening": slice(12, 24),
        "night": slice(24, 40),
        "morning": slice(40, 48),
    }
    z_windows = []
    names = []
    for name, sl in windows.items():
        xw = canvas[:, :, sl, :]
        stats = np.concatenate(
            [
                xw.mean(axis=2),
                xw.std(axis=2),
                xw.max(axis=2),
                xw.min(axis=2),
                np.sqrt((xw**2).mean(axis=2)),
            ],
            axis=1,
        ).reshape(len(rows), -1)
        zw = pca_fit_transform(stats, 10, 280200 + len(name))
        z_windows.append(zw)
        names.extend([f"{name}_pc{i:02d}" for i in range(zw.shape[1])])
    z = np.hstack([z_full, z_mobile, z_wear] + z_windows).astype(np.float32)
    names = [f"full_pc{i:02d}" for i in range(z_full.shape[1])] + [f"mobile_pc{i:02d}" for i in range(z_mobile.shape[1])] + [f"wear_pc{i:02d}" for i in range(z_wear.shape[1])] + names
    return z, names


def slope_of(mat: np.ndarray) -> np.ndarray:
    if len(mat) <= 1:
        return np.zeros(mat.shape[1], dtype=float)
    x = np.linspace(-0.5, 0.5, len(mat), dtype=float)
    denom = float(np.sum(x * x))
    return (x[:, None] * mat).sum(axis=0) / max(denom, 1e-9)


def summarize_z(z: np.ndarray, pos: np.ndarray) -> np.ndarray:
    mat = z[np.asarray(pos, dtype=int)]
    return np.r_[
        mat.mean(axis=0),
        mat.std(axis=0),
        mat[0],
        mat[-1],
        mat[-1] - mat[0],
        slope_of(mat),
        np.linalg.norm(mat, axis=1).mean(),
        np.linalg.norm(mat, axis=1).std(),
    ].astype(np.float32)


def summary_dim(z_dim: int) -> int:
    return z_dim * 6 + 2


def context_for_block(rows: pd.DataFrame, z: np.ndarray, y: np.ndarray, base_all: np.ndarray, block_pos: np.ndarray, known_label_mask: np.ndarray) -> np.ndarray:
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
    contexts = [before_tail, after_head, known_subject]
    feats = [
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
            ],
            dtype=float,
        )
    ]
    for ctx in contexts:
        if len(ctx) == 0:
            feats.extend([np.zeros(z.shape[1]), np.zeros(z.shape[1]), np.zeros(z.shape[1])])
        else:
            feats.extend([z[ctx].mean(axis=0), z[ctx].std(axis=0), slope_of(z[ctx])])
    for ctx in [before_tail, after_head, known_subject]:
        if len(ctx) == 0:
            feats.extend([np.full(len(TARGETS), 0.5), np.zeros(len(TARGETS)), np.full(len(TARGETS), 0.5), np.zeros(len(TARGETS))])
        else:
            vals = y[ctx]
            feats.extend([np.nanmean(vals, axis=0), np.isfinite(vals).mean(axis=0), base_all[ctx].mean(axis=0), base_all[ctx].std(axis=0)])
    block_base = base_all[block_pos]
    feats.extend([block_base.mean(axis=0), block_base.std(axis=0), z[block_pos].mean(axis=0), z[block_pos].std(axis=0)])
    return np.concatenate([np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0).ravel() for f in feats]).astype(np.float32)


def fit_block_canvas_model(x_context: np.ndarray, z_target: np.ndarray, alpha: float) -> tuple[StandardScaler, Ridge]:
    scaler = StandardScaler()
    xs = scaler.fit_transform(finite(x_context))
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(xs, finite(z_target))
    return scaler, model


def predict_block_summary(rows: pd.DataFrame, z: np.ndarray, y: np.ndarray, base_all: np.ndarray, train_indices: np.ndarray, pred_blocks: list[np.ndarray], lengths: dict[str, list[int]], alpha: float) -> np.ndarray:
    known = adv.known_mask_for_train(rows, train_indices)
    train_blocks = adv.make_training_blocks(rows, y, train_indices, lengths, max_blocks_per_subject=220)
    if not train_blocks or not pred_blocks:
        return np.full((len(pred_blocks), summary_dim(z.shape[1])), np.nan, dtype=float)
    x_train = np.vstack([context_for_block(rows, z, y, base_all, b, known) for b in train_blocks])
    z_train = np.vstack([summarize_z(z, b) for b in train_blocks])
    scaler, model = fit_block_canvas_model(x_train, z_train, alpha)
    x_pred = np.vstack([context_for_block(rows, z, y, base_all, b, known) for b in pred_blocks])
    return model.predict(scaler.transform(finite(x_pred)))


def add_block_features(out: pd.DataFrame, prefix: str, z: np.ndarray, block_rows: list[np.ndarray], pred_summary: np.ndarray, row_indices: list[np.ndarray], max_latent: int = 28) -> None:
    z_dim = z.shape[1]
    for block_i, block in enumerate(block_rows):
        actual = summarize_z(z, block)
        pred = pred_summary[block_i]
        resid = actual - pred
        pred_mean = pred[:z_dim]
        actual_mean = actual[:z_dim]
        resid_mean = resid[:z_dim]
        idxs = row_indices[block_i]
        rel = np.linspace(0.0, 1.0, len(idxs)) if len(idxs) > 1 else np.zeros(len(idxs))
        for local, row_i in enumerate(idxs):
            row_z = z[block[local]]
            out.loc[row_i, f"{prefix}_pos"] = rel[local]
            out.loc[row_i, f"{prefix}_len"] = len(idxs)
            out.loc[row_i, f"{prefix}_resid_norm"] = float(np.linalg.norm(resid_mean))
            out.loc[row_i, f"{prefix}_row_resid_norm"] = float(np.linalg.norm(row_z - pred_mean))
            out.loc[row_i, f"{prefix}_actual_norm"] = float(np.linalg.norm(actual_mean))
            out.loc[row_i, f"{prefix}_pred_norm"] = float(np.linalg.norm(pred_mean))
            denom = np.linalg.norm(actual_mean) * np.linalg.norm(pred_mean)
            out.loc[row_i, f"{prefix}_block_cos"] = float(np.dot(actual_mean, pred_mean) / max(denom, 1e-9))
            for k in range(min(max_latent, z_dim)):
                out.loc[row_i, f"{prefix}_pred_{k:02d}"] = pred_mean[k]
                out.loc[row_i, f"{prefix}_resid_{k:02d}"] = resid_mean[k]
                out.loc[row_i, f"{prefix}_absresid_{k:02d}"] = abs(resid_mean[k])
                out.loc[row_i, f"{prefix}_row_resid_{k:02d}"] = row_z[k] - pred_mean[k]
                out.loc[row_i, f"{prefix}_row_absresid_{k:02d}"] = abs(row_z[k] - pred_mean[k])


def build_block_canvas_features(train: pd.DataFrame, sub: pd.DataFrame, rows: pd.DataFrame, z: np.ndarray, y: np.ndarray, base_all: np.ndarray, base_sub: pd.DataFrame, repeats: int = 18) -> tuple[pd.DataFrame, pd.DataFrame]:
    lengths = adv.actual_lengths_by_subject(rows)
    train_feat = train[SUB_KEY + TARGETS].copy()
    sub_feat = sub[SUB_KEY].copy()
    for alpha in [10.0, 50.0, 150.0]:
        prefix = f"bcj_a{str(alpha).replace('.', 'p')}"
        train_block_feature = pd.DataFrame(index=np.arange(len(train)))
        acc_cover = np.zeros(len(train), dtype=int)
        for fold_i, (tr_idx, val_idx, fold) in enumerate(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=281000 + int(alpha))):
            val_blocks = adv.contiguous_val_blocks(rows, val_idx)
            if not val_blocks:
                continue
            pred = predict_block_summary(rows, z, y, base_all, tr_idx, val_blocks, lengths, alpha)
            row_indices = [rows.iloc[b]["train_idx"].to_numpy(dtype=int) for b in val_blocks]
            add_block_features(train_block_feature, prefix, z, val_blocks, pred, row_indices)
            for idx in row_indices:
                acc_cover[idx] += 1
            print(f"block-canvas alpha={alpha:g} {fold}: val_blocks={len(val_blocks)} covered={int((acc_cover > 0).sum())}", flush=True)
        train_feat = pd.concat([train_feat, train_block_feature.add_suffix("")], axis=1)

        sub_blocks = adv.submission_blocks(train, sub, rows)
        pred_sub = predict_block_summary(rows, z, y, base_all, np.arange(len(train)), sub_blocks, lengths, alpha)
        sub_block_feature = pd.DataFrame(index=np.arange(len(sub)))
        sub_row_indices = [rows.iloc[b]["sub_idx"].to_numpy(dtype=int) for b in sub_blocks]
        add_block_features(sub_block_feature, prefix, z, sub_blocks, pred_sub, sub_row_indices)
        sub_feat = pd.concat([sub_feat, sub_block_feature], axis=1)
    return train_feat.copy(), sub_feat.copy()


def axis_against(file_name: str) -> dict[str, float]:
    try:
        stage2 = pd.read_csv(adv.BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        cand = pd.read_csv(OUT / file_name, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
        s = adv.logit(stage2[TARGETS].to_numpy(float))
        move = adv.logit(cand[TARGETS].to_numpy(float)) - s

        def axis(files: list[str], weights: list[float] | None = None) -> np.ndarray:
            arr = []
            for f in files:
                df = pd.read_csv(OUT / f, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
                arr.append(adv.logit(df[TARGETS].to_numpy(float)) - s)
            if weights is None:
                return np.mean(np.stack(arr), axis=0)
            return np.average(np.stack(arr), axis=0, weights=np.asarray(weights))

        bad = axis(["submission_jepa_latent_residual_probe.csv", "submission_jepa_latent_q2_w0p45.csv"], [PUBLIC_KNOWN["submission_jepa_latent_residual_probe.csv"] - STAGE2_PUBLIC, PUBLIC_KNOWN["submission_jepa_latent_q2_w0p45.csv"] - STAGE2_PUBLIC])
        good = axis(["submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"])
        out = {}
        for name, ax in [("jepa_bad", bad), ("raw_good", good)]:
            m = move.reshape(-1)
            a = ax.reshape(-1)
            out[f"{name}_ratio"] = float(np.dot(m, a) / max(float(np.dot(a, a)), 1e-12))
            out[f"{name}_cos"] = float(np.dot(m, a) / max(float(np.linalg.norm(m) * np.linalg.norm(a)), 1e-12))
        out.update(adv.public_axis_for(file_name))
        return out
    except Exception:
        return {"jepa_bad_ratio": np.nan, "jepa_bad_cos": np.nan, "raw_good_ratio": np.nan, "raw_good_cos": np.nan}


def scan_and_submit(train_feat: pd.DataFrame, sub_feat: pd.DataFrame, base: np.ndarray, base_sub: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    y = train_feat[TARGETS].to_numpy(int)
    cols = broad.finite_numeric_cols(train_feat)
    pre = broad.prefilter(train_feat, base, cols, TARGETS, top_n=65)
    pre.to_csv(OUT / "block_canvas_jepa_prefilter.csv", index=False)
    rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = broad.loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.10, 0.20, 0.50]:
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
    scan.to_csv(OUT / "block_canvas_jepa_scan.csv", index=False)

    def apply_ops(ops: pd.DataFrame, name: str, scale: float = 1.0) -> tuple[np.ndarray, pd.DataFrame]:
        pred = base.copy()
        sub_pred = base_sub[TARGETS].to_numpy(float).copy()
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
        out.to_csv(OUT / name, index=False)
        pd.DataFrame(used).to_csv(OUT / name.replace("submission_", "").replace(".csv", "_ops.csv"), index=False)
        return pred, pd.DataFrame(used)

    strict = scan[(scan["passes_strict"]) & (scan["best_weight"] > 0)].sort_values("delta_vs_base")
    no_q2 = strict[~strict["target"].eq("Q2")]
    top = scan[scan["best_weight"] > 0].sort_values("delta_vs_base").groupby("target", group_keys=False).head(1)
    specs = []
    for label, ops in [("strict", strict), ("strict_noq2", no_q2), ("top_probe", top)]:
        for scale in [0.35, 0.5, 0.75, 1.0]:
            specs.append((label, ops, scale))
    summary_rows = []
    for label, ops, scale in specs:
        scale_label = str(scale).replace(".", "p")
        file_name = f"submission_block_canvas_jepa_{label}_scale{scale_label}.csv"
        pred, used = apply_ops(ops, file_name, scale)
        mloss = adv.mean_loss(y, pred)
        summary_rows.append({"candidate": file_name, "class": label, "scale": scale, "ops": int(len(used)), "oof_loss": mloss, "oof_delta_vs_stage2": mloss - adv.mean_loss(y, base), **axis_against(file_name)})
    summary = pd.DataFrame(summary_rows).sort_values(["class", "oof_delta_vs_stage2"])
    summary.to_csv(OUT / "block_canvas_jepa_candidate_summary.csv", index=False)
    return scan, summary


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, sensors = adv.build_raw_canvas(rows)
    z, names = build_day_latent(rows, canvas)
    pd.DataFrame({"latent": names}).to_csv(OUT / "block_canvas_jepa_latent_meta.csv", index=False)
    train_feat, sub_feat = build_block_canvas_features(train, sub, rows, z, y, base_all, base_sub)
    train_feat.to_parquet(OUT / "block_canvas_jepa_train_features.parquet", index=False)
    sub_feat.to_parquet(OUT / "block_canvas_jepa_submission_features.parquet", index=False)
    scan, summary = scan_and_submit(train_feat, sub_feat, base, base_sub)
    report = [
        "# Block-Canvas JEPA",
        "",
        "Target object is a real submission-like hidden block raw canvas. Context is surrounding same-subject train raw/label/base state. Features are block-level actual-vs-predicted raw latent residuals assigned back to rows.",
        "",
        "## Candidate Summary",
        "",
        summary.to_csv(index=False),
        "",
        "## Best Scan Rows",
        "",
        scan.head(50).to_csv(index=False),
        "",
        "## Public Feedback",
        "",
        pd.DataFrame([{"candidate": k, "public_lb": v, "delta_vs_stage2": v - STAGE2_PUBLIC} for k, v in PUBLIC_KNOWN.items()]).to_csv(index=False),
    ]
    (OUT / "block_canvas_jepa_report.md").write_text("\n".join(report), encoding="utf-8")
    print(summary.head(20).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
