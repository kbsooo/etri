from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import block_canvas_jepa as bcj  # noqa: E402
import jepa_ready_data_audit as audit  # noqa: E402


BLOCK_MODES = ["submission_like", "fixed_2", "fixed_4", "fixed_6", "fixed_8"]
TARGET_FAMILIES = [
    "time_meta",
    "raw_mean",
    "raw_trend",
    "window_state",
    "modality_state",
    "canvas_process",
    "hybrid_raw",
    "label_rate",
    "label_state",
    "teacher_hybrid",
]
CONTEXT_VARIANTS = [
    "meta_only",
    "past_raw",
    "future_raw",
    "bidir_raw",
    "prior_raw",
    "past_label",
    "future_label",
    "bidir_label",
    "prior_label",
    "bidir_all",
    "prior_all",
    "full_strict",
]
PROTO_KS = [4, 8, 10]
PCA_BUDGET = 24


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float32), nan=0.0, posinf=0.0, neginf=0.0)


def label_rate(y: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = y[np.asarray(block, dtype=int)]
    rates = np.nanmean(vals, axis=0)
    return np.nan_to_num(rates, nan=0.5).astype(np.float32)


def block_label_state(y: np.ndarray, block: np.ndarray) -> np.ndarray:
    vals = y[np.asarray(block, dtype=int)]
    rates = label_rate(y, block)
    ent = -(rates * np.log(adv.clip(rates)) + (1.0 - rates) * np.log(adv.clip(1.0 - rates)))
    return np.r_[rates, ent, vals[0], vals[-1], vals[-1] - vals[0]].astype(np.float32)


def block_meta(rows: pd.DataFrame, block: np.ndarray) -> np.ndarray:
    part = rows.iloc[np.asarray(block, dtype=int)]
    return np.array(
        [
            len(block),
            part["subject_phase"].mean(),
            part["is_weekend"].mean(),
            part["dow"].mean() / 6.0,
            np.sin(2.0 * np.pi * part["dow"].mean() / 7.0),
            np.cos(2.0 * np.pi * part["dow"].mean() / 7.0),
        ],
        dtype=np.float32,
    )


def slope_of(mat: np.ndarray) -> np.ndarray:
    return audit.slope_of(finite(mat))


def summarize_z(z: np.ndarray, indices: np.ndarray) -> np.ndarray:
    if len(indices) == 0:
        return np.zeros(z.shape[1] * 3, dtype=np.float32)
    vals = z[np.asarray(indices, dtype=int)]
    return np.r_[vals.mean(axis=0), vals.std(axis=0), slope_of(vals)].astype(np.float32)


def summarize_labels(y: np.ndarray, base_all: np.ndarray, indices: np.ndarray) -> np.ndarray:
    if len(indices) == 0:
        return np.r_[
            np.full(len(TARGETS), 0.5),
            np.zeros(len(TARGETS)),
            np.full(len(TARGETS), 0.5),
            np.zeros(len(TARGETS)),
        ].astype(np.float32)
    vals = y[np.asarray(indices, dtype=int)]
    base = base_all[np.asarray(indices, dtype=int)]
    return np.r_[
        np.nanmean(vals, axis=0),
        np.isfinite(vals).mean(axis=0),
        base.mean(axis=0),
        base.std(axis=0),
    ].astype(np.float32)


def rich_context_parts(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    block: np.ndarray,
    known_label_mask: np.ndarray,
) -> dict[str, np.ndarray]:
    block = np.asarray(block, dtype=int)
    sid = str(rows.iloc[int(block[0])]["subject_id"])
    subject_idx = rows["subject_id"].astype(str).eq(sid).to_numpy()
    subject_pos = np.where(subject_idx)[0]
    block_set = set(int(p) for p in block)
    known_subject = np.array([p for p in subject_pos if known_label_mask[p] and p not in block_set], dtype=int)
    past = known_subject[known_subject < block.min()]
    future = known_subject[known_subject > block.max()]
    past_tail = past[-14:]
    future_head = future[:14]
    meta = np.r_[
        block_meta(rows, block),
        float(block.min() - subject_pos.min()) / max(len(subject_pos), 1),
        float(subject_pos.max() - block.max()) / max(len(subject_pos), 1),
        float(block.min() - past_tail[-1]) if len(past_tail) else 99.0,
        float(future_head[0] - block.max()) if len(future_head) else 99.0,
        len(past_tail),
        len(future_head),
        len(known_subject),
    ].astype(np.float32)
    return {
        "meta": meta,
        "past_z": summarize_z(z, past_tail),
        "future_z": summarize_z(z, future_head),
        "prior_z": summarize_z(z, known_subject),
        "past_label": summarize_labels(y, base_all, past_tail),
        "future_label": summarize_labels(y, base_all, future_head),
        "prior_label": summarize_labels(y, base_all, known_subject),
    }


def build_context(parts: dict[str, np.ndarray], variant: str) -> np.ndarray:
    mapping = {
        "meta_only": ["meta"],
        "past_raw": ["meta", "past_z"],
        "future_raw": ["meta", "future_z"],
        "bidir_raw": ["meta", "past_z", "future_z"],
        "prior_raw": ["meta", "prior_z"],
        "past_label": ["meta", "past_label"],
        "future_label": ["meta", "future_label"],
        "bidir_label": ["meta", "past_label", "future_label"],
        "prior_label": ["meta", "prior_label"],
        "bidir_all": ["meta", "past_z", "future_z", "past_label", "future_label"],
        "prior_all": ["meta", "prior_z", "prior_label"],
        "full_strict": ["meta", "past_z", "future_z", "prior_z", "past_label", "future_label", "prior_label"],
    }
    if variant not in mapping:
        raise ValueError(variant)
    return np.concatenate([parts[name] for name in mapping[variant]]).astype(np.float32)


def canvas_process_summary(canvas: np.ndarray, block: np.ndarray) -> np.ndarray:
    mat = canvas[np.asarray(block, dtype=int)]
    abs_mat = np.abs(mat)
    sensor_mean = mat.mean(axis=(0, 2))
    sensor_std = mat.std(axis=(0, 2))
    time_profile = abs_mat.mean(axis=(0, 1, 3))
    windows = [slice(0, 12), slice(12, 24), slice(24, 40), slice(40, 48)]
    win_stats = []
    for sl in windows:
        part = abs_mat[:, :, sl, :]
        win_stats.extend([part.mean(), part.std(), part.max()])
    sensor_mag = abs_mat.mean(axis=(0, 2, 3))
    return np.r_[sensor_mean.ravel(), sensor_std.ravel(), time_profile, win_stats, sensor_mag].astype(np.float32)


def target_feature(family: str, rows: pd.DataFrame, z: np.ndarray, canvas: np.ndarray, y: np.ndarray, block: np.ndarray) -> np.ndarray:
    if family == "time_meta":
        return block_meta(rows, block)
    if family == "raw_mean":
        return np.r_[audit.mean_latent(z, block), block_meta(rows, block)].astype(np.float32)
    if family == "raw_trend":
        mat = z[np.asarray(block, dtype=int)]
        return np.r_[mat.mean(axis=0), mat.std(axis=0), slope_of(mat), block_meta(rows, block)].astype(np.float32)
    if family == "window_state":
        return np.r_[audit.window_state(z, block), block_meta(rows, block)].astype(np.float32)
    if family == "modality_state":
        return np.r_[audit.modality_state(z, block), block_meta(rows, block)].astype(np.float32)
    if family == "canvas_process":
        return np.r_[canvas_process_summary(canvas, block), block_meta(rows, block)].astype(np.float32)
    if family == "hybrid_raw":
        return np.r_[
            audit.window_state(z, block),
            audit.modality_state(z, block),
            canvas_process_summary(canvas, block),
            block_meta(rows, block),
        ].astype(np.float32)
    if family == "label_rate":
        return label_rate(y, block)
    if family == "label_state":
        return block_label_state(y, block)
    if family == "teacher_hybrid":
        return np.r_[block_label_state(y, block), audit.window_state(z, block), audit.modality_state(z, block), block_meta(rows, block)].astype(np.float32)
    raise ValueError(family)


def build_target_matrix(
    family: str,
    rows: pd.DataFrame,
    z: np.ndarray,
    canvas: np.ndarray,
    y: np.ndarray,
    blocks: list[np.ndarray],
) -> np.ndarray:
    return np.vstack([target_feature(family, rows, z, canvas, y, b) for b in blocks]).astype(np.float32)


def fixed_blocks(
    rows: pd.DataFrame,
    y: np.ndarray,
    allowed_train_indices: np.ndarray,
    length: int,
    max_blocks_per_subject: int,
) -> list[np.ndarray]:
    allowed = set(int(x) for x in allowed_train_indices)
    blocks: list[np.ndarray] = []
    stride = max(1, length // 2)
    for _sid, g in rows[rows["split"].eq("train")].groupby("subject_id", sort=False):
        train_idx = g["train_idx"].to_numpy(dtype=int)
        pos = g["global_pos"].to_numpy(dtype=int)
        ok = np.array([idx in allowed for idx in train_idx], dtype=bool)
        sid_blocks = []
        for start in range(0, len(pos) - length + 1, stride):
            block = pos[start : start + length]
            if ok[start : start + length].all() and np.isfinite(y[block]).all():
                sid_blocks.append(block)
        if len(sid_blocks) > max_blocks_per_subject:
            idx = np.linspace(0, len(sid_blocks) - 1, max_blocks_per_subject).round().astype(int)
            sid_blocks = [sid_blocks[i] for i in idx]
        blocks.extend(sid_blocks)
    return blocks


def blocks_for_mode(
    mode: str,
    rows: pd.DataFrame,
    y: np.ndarray,
    train_indices: np.ndarray,
    val_indices: np.ndarray,
    lengths: dict[str, list[int]],
) -> tuple[list[np.ndarray], list[np.ndarray]]:
    if mode == "submission_like":
        return (
            adv.make_training_blocks(rows, y, train_indices, lengths, max_blocks_per_subject=160),
            adv.contiguous_val_blocks(rows, val_indices),
        )
    length = int(mode.split("_")[1])
    return (
        fixed_blocks(rows, y, train_indices, length, max_blocks_per_subject=120),
        fixed_blocks(rows, y, val_indices, length, max_blocks_per_subject=80),
    )


def transform_features(train_x: np.ndarray, val_x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_x))
    va = scaler.transform(finite(val_x))
    k = min(PCA_BUDGET, tr.shape[0] - 1, tr.shape[1])
    if 1 < k < tr.shape[1]:
        pca = PCA(n_components=k, svd_solver="randomized", random_state=297701)
        tr = pca.fit_transform(tr)
        va = pca.transform(va)
    return tr.astype(np.float32), va.astype(np.float32)


def rate_metrics(true: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    true = finite(true)
    pred = finite(pred)
    sse = float(np.sum((true - pred) ** 2))
    mean = true.mean(axis=0, keepdims=True)
    sst = float(np.sum((true - mean) ** 2))
    denom = np.linalg.norm(true, axis=1) * np.linalg.norm(pred, axis=1)
    return {
        "r2": 1.0 - sse / max(sst, 1e-12),
        "rmse": float(np.sqrt(np.mean((true - pred) ** 2))),
        "cos": float(np.mean(np.sum(true * pred, axis=1) / np.maximum(denom, 1e-12))),
    }


def safe_logloss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    y_prob = np.clip(y_prob, 1e-6, 1.0)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True)
    return float(log_loss(y_true, y_prob, labels=np.arange(y_prob.shape[1])))


def predict_proto_probs(train_ctx: np.ndarray, train_proto: np.ndarray, val_ctx: np.ndarray, k: int) -> np.ndarray | None:
    if np.unique(train_proto).size < 2:
        return None
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_ctx))
    va = scaler.transform(finite(val_ctx))
    clf = LogisticRegression(C=0.75, max_iter=800, solver="lbfgs", random_state=298001)
    clf.fit(tr, train_proto)
    raw_prob = clf.predict_proba(va).astype(np.float32)
    prob = np.full((len(val_ctx), k), 1e-6, dtype=np.float32)
    for col_i, cls in enumerate(clf.classes_):
        prob[:, int(cls)] = raw_prob[:, col_i]
    prob = prob / prob.sum(axis=1, keepdims=True)
    return prob


def entropy_norm(counts: np.ndarray) -> float:
    p = counts.astype(np.float64) / max(float(counts.sum()), 1.0)
    ent = float(-(p * np.log(np.clip(p, 1e-12, 1.0))).sum())
    return ent / max(np.log(len(counts)), 1e-12)


def is_pareto(df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    values = df[cols].to_numpy(dtype=float)
    keep = np.ones(len(df), dtype=bool)
    for i in range(len(df)):
        if not keep[i]:
            continue
        dominated = np.all(values >= values[i], axis=1) & np.any(values > values[i], axis=1)
        if dominated.any():
            keep[i] = False
    return keep


def main() -> None:
    train, sub, base, base_sub = adv.read_data()
    rows, _x, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y = adv.train_label_matrix(rows, train)
    canvas, _sensors = adv.build_raw_canvas(rows)
    z, _names = bcj.build_day_latent(rows, canvas)
    lengths = adv.actual_lengths_by_subject(rows)

    fold_rows = []
    profile_rows = []
    for tr_idx, val_idx, fold in adv.geom.geometry_folds(train, sub, n_repeats=4, seed=298000):
        known = adv.known_mask_for_train(rows, tr_idx)
        for block_mode in BLOCK_MODES:
            train_blocks, val_blocks = blocks_for_mode(block_mode, rows, y, tr_idx, val_idx, lengths)
            if len(train_blocks) < 40 or len(val_blocks) < 6:
                continue
            print(f"atlas {fold} {block_mode}: train_blocks={len(train_blocks)} val_blocks={len(val_blocks)}", flush=True)
            train_parts = [rich_context_parts(rows, z, y, base_all, b, known) for b in train_blocks]
            val_parts = [rich_context_parts(rows, z, y, base_all, b, known) for b in val_blocks]
            train_rate = np.vstack([label_rate(y, b) for b in train_blocks]).astype(np.float32)
            val_rate = np.vstack([label_rate(y, b) for b in val_blocks]).astype(np.float32)
            train_contexts = {
                ctx: np.vstack([build_context(p, ctx) for p in train_parts]).astype(np.float32)
                for ctx in CONTEXT_VARIANTS
            }
            val_contexts = {
                ctx: np.vstack([build_context(p, ctx) for p in val_parts]).astype(np.float32)
                for ctx in CONTEXT_VARIANTS
            }
            for family in TARGET_FAMILIES:
                train_target = build_target_matrix(family, rows, z, canvas, y, train_blocks)
                val_target = build_target_matrix(family, rows, z, canvas, y, val_blocks)
                train_feat, val_feat = transform_features(train_target, val_target)
                for k in PROTO_KS:
                    if len(train_feat) <= k * 4:
                        continue
                    km = MiniBatchKMeans(n_clusters=k, random_state=298100 + k, batch_size=256, n_init=10)
                    train_proto = km.fit_predict(train_feat).astype(int)
                    val_proto = km.predict(val_feat).astype(int)
                    proto_count = np.bincount(train_proto, minlength=k).astype(np.float32)
                    if proto_count.min() < 2:
                        continue
                    proto_rate = np.zeros((k, len(TARGETS)), dtype=np.float32)
                    for cid in range(k):
                        proto_rate[cid] = train_rate[train_proto == cid].mean(axis=0)
                        profile_rows.append(
                            {
                                "fold": fold,
                                "block_mode": block_mode,
                                "family": family,
                                "k": k,
                                "proto": cid,
                                "count": int(proto_count[cid]),
                                **{f"rate_{t}": float(proto_rate[cid, j]) for j, t in enumerate(TARGETS)},
                            }
                        )
                    oracle_rate = proto_rate[val_proto]
                    oracle_stats = rate_metrics(val_rate, oracle_rate)
                    balance = entropy_norm(proto_count)
                    for ctx in CONTEXT_VARIANTS:
                        prob = predict_proto_probs(train_contexts[ctx], train_proto, val_contexts[ctx], k)
                        if prob is None:
                            continue
                        pred_proto = prob.argmax(axis=1)
                        pred_rate = prob @ proto_rate
                        pred_stats = rate_metrics(val_rate, pred_rate)
                        random_logloss = np.log(k)
                        predictability = 1.0 - safe_logloss(val_proto, prob) / max(random_logloss, 1e-12)
                        fold_rows.append(
                            {
                                "fold": fold,
                                "block_mode": block_mode,
                                "family": family,
                                "k": k,
                                "context_variant": ctx,
                                "train_blocks": len(train_blocks),
                                "val_blocks": len(val_blocks),
                                "mean_val_len": float(np.mean([len(b) for b in val_blocks])),
                                "proto_logloss": safe_logloss(val_proto, prob),
                                "proto_acc": float(accuracy_score(val_proto, pred_proto)),
                                "proto_predictability": float(predictability),
                                "balance_entropy_norm": balance,
                                "oracle_rate_r2": oracle_stats["r2"],
                                "oracle_rate_rmse": oracle_stats["rmse"],
                                "oracle_rate_cos": oracle_stats["cos"],
                                "pred_rate_r2": pred_stats["r2"],
                                "pred_rate_rmse": pred_stats["rmse"],
                                "pred_rate_cos": pred_stats["cos"],
                            }
                        )

    folds = pd.DataFrame(fold_rows)
    profiles = pd.DataFrame(profile_rows)
    folds.to_csv(OUT / "jepa_friendly_atlas_folds.csv", index=False)
    profiles.to_csv(OUT / "jepa_friendly_atlas_prototype_profiles.csv", index=False)

    summary = (
        folds.groupby(["block_mode", "family", "k", "context_variant"], as_index=False)
        .agg(
            folds=("fold", "nunique"),
            train_blocks=("train_blocks", "mean"),
            val_blocks=("val_blocks", "mean"),
            mean_val_len=("mean_val_len", "mean"),
            proto_logloss=("proto_logloss", "mean"),
            proto_acc=("proto_acc", "mean"),
            proto_predictability=("proto_predictability", "mean"),
            balance_entropy_norm=("balance_entropy_norm", "mean"),
            oracle_rate_r2=("oracle_rate_r2", "mean"),
            oracle_rate_cos=("oracle_rate_cos", "mean"),
            pred_rate_r2=("pred_rate_r2", "mean"),
            pred_rate_cos=("pred_rate_cos", "mean"),
        )
    )
    summary["jepa_friendly_score"] = (
        0.35 * summary["proto_predictability"]
        + 0.20 * summary["proto_acc"]
        + 0.20 * summary["pred_rate_r2"]
        + 0.15 * summary["oracle_rate_r2"]
        + 0.10 * summary["balance_entropy_norm"]
    )
    summary = summary.sort_values("jepa_friendly_score", ascending=False).reset_index(drop=True)
    summary.to_csv(OUT / "jepa_friendly_atlas_summary.csv", index=False)

    pareto_cols = ["proto_predictability", "proto_acc", "pred_rate_r2", "oracle_rate_r2", "balance_entropy_norm"]
    pareto = summary[is_pareto(summary, pareto_cols)].sort_values("jepa_friendly_score", ascending=False)
    pareto.to_csv(OUT / "jepa_friendly_atlas_pareto.csv", index=False)

    context_summary = (
        summary.groupby("context_variant", as_index=False)
        .agg(
            best_score=("jepa_friendly_score", "max"),
            mean_score=("jepa_friendly_score", "mean"),
            best_predictability=("proto_predictability", "max"),
            best_pred_rate_r2=("pred_rate_r2", "max"),
            best_oracle_rate_r2=("oracle_rate_r2", "max"),
        )
        .sort_values("best_score", ascending=False)
    )
    context_summary.to_csv(OUT / "jepa_friendly_atlas_context_summary.csv", index=False)

    block_summary = (
        summary.groupby("block_mode", as_index=False)
        .agg(
            best_score=("jepa_friendly_score", "max"),
            mean_score=("jepa_friendly_score", "mean"),
            best_predictability=("proto_predictability", "max"),
            best_pred_rate_r2=("pred_rate_r2", "max"),
            best_oracle_rate_r2=("oracle_rate_r2", "max"),
            mean_val_len=("mean_val_len", "mean"),
        )
        .sort_values("best_score", ascending=False)
    )
    block_summary.to_csv(OUT / "jepa_friendly_atlas_block_summary.csv", index=False)

    family_summary = (
        summary.groupby("family", as_index=False)
        .agg(
            best_score=("jepa_friendly_score", "max"),
            mean_score=("jepa_friendly_score", "mean"),
            best_predictability=("proto_predictability", "max"),
            best_pred_rate_r2=("pred_rate_r2", "max"),
            best_oracle_rate_r2=("oracle_rate_r2", "max"),
        )
        .sort_values("best_score", ascending=False)
    )
    family_summary.to_csv(OUT / "jepa_friendly_atlas_family_summary.csv", index=False)

    report = [
        "# JEPA-Friendly Atlas",
        "",
        "Objective: move the original exhaustive data-mining mindset from direct Log Loss improvement to JEPA-friendly data design.",
        "",
        "A candidate is JEPA-friendly when it is predictable from strict non-target context, keeps enough semantic information about Q1/Q2/Q3/S1-S4, avoids code collapse, and works under fold-safe hidden-block geometry.",
        "",
        "## Top JEPA-Friendly Candidates",
        "",
        summary.head(25).to_csv(index=False),
        "",
        "## Pareto Frontier",
        "",
        pareto.head(25).to_csv(index=False),
        "",
        "## Context Summary",
        "",
        context_summary.to_csv(index=False),
        "",
        "## Block Geometry Summary",
        "",
        block_summary.to_csv(index=False),
        "",
        "## Target Family Summary",
        "",
        family_summary.to_csv(index=False),
        "",
        "## Files",
        "",
        "- `jepa_friendly_atlas_folds.csv`",
        "- `jepa_friendly_atlas_summary.csv`",
        "- `jepa_friendly_atlas_pareto.csv`",
        "- `jepa_friendly_atlas_context_summary.csv`",
        "- `jepa_friendly_atlas_block_summary.csv`",
        "- `jepa_friendly_atlas_family_summary.csv`",
        "- `jepa_friendly_atlas_prototype_profiles.csv`",
    ]
    (OUT / "jepa_friendly_atlas_report.md").write_text("\n".join(report), encoding="utf-8")

    print("TOP JEPA-FRIENDLY")
    print(summary.head(25).to_string(index=False), flush=True)
    print("\nCONTEXT")
    print(context_summary.to_string(index=False), flush=True)
    print("\nBLOCKS")
    print(block_summary.to_string(index=False), flush=True)
    print("\nFAMILIES")
    print(family_summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
