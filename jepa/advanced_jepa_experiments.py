from __future__ import annotations

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
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from torch import nn


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q_TARGETS = ["Q1", "Q2", "Q3"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(ANALYSIS))
import broad_single_feature_residual_probe as broad  # noqa: E402
import geometry_mask_cv_experiments as geom  # noqa: E402


BASE_OOF = ANALYSIS / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
BASE_SUB = ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
WEIGHTS = np.array([0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.60])
ALPHAS = [1.0, 10.0, 100.0]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 1e-5, 1.0 - 1e-5)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], pred[:, j]) for j in range(len(TARGETS))]))


def read_data() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, pd.DataFrame]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sub = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    base = clip(np.load(BASE_OOF))
    base_sub = pd.read_csv(BASE_SUB, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    assert base_sub[SUB_KEY].equals(sub[SUB_KEY])
    return train, sub, base, base_sub


def all_rows(train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    tr = train[SUB_KEY].copy()
    tr["split"] = "train"
    tr["train_idx"] = np.arange(len(train))
    tr["sub_idx"] = -1
    su = sub[SUB_KEY].copy()
    su["split"] = "submission"
    su["train_idx"] = -1
    su["sub_idx"] = np.arange(len(sub))
    rows = pd.concat([tr, su], ignore_index=True).sort_values(KEY).reset_index(drop=True)
    rows["global_pos"] = np.arange(len(rows))
    rows["subject_pos"] = rows.groupby("subject_id", sort=False).cumcount()
    rows["subject_count"] = rows.groupby("subject_id", sort=False)["subject_id"].transform("size")
    rows["subject_phase"] = rows["subject_pos"] / np.maximum(rows["subject_count"] - 1, 1)
    rows["dow"] = rows["lifelog_date"].dt.dayofweek
    rows["is_weekend"] = (rows["dow"] >= 5).astype(float)
    return rows


def source_frame(path: Path, prefix: str, train: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame | None:
    if not path.exists():
        return None
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.copy()
    for col in ["lifelog_date", "sleep_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    keys = SUB_KEY if "sleep_date" in df.columns else KEY
    drop = set(TARGETS + ["split"])
    cols = [c for c in df.columns if c not in set(keys) | drop]
    out = df[keys + cols].copy()
    out = out.rename(columns={c: f"{prefix}__{c}" for c in cols})
    if keys == KEY:
        base_keys = pd.concat([train[KEY], sub[KEY]], ignore_index=True).sort_values(KEY).reset_index(drop=True)
    else:
        base_keys = pd.concat([train[SUB_KEY], sub[SUB_KEY]], ignore_index=True).sort_values(KEY).reset_index(drop=True)
    return base_keys.merge(out, on=keys, how="left")


def pca_components(df: pd.DataFrame, prefix: str, n_components: int) -> pd.DataFrame:
    key_cols = [c for c in SUB_KEY if c in df.columns]
    if not key_cols:
        key_cols = [c for c in KEY if c in df.columns]
    numeric_cols = []
    for col in df.columns:
        if col in key_cols:
            continue
        s = pd.to_numeric(df[col], errors="coerce")
        if s.notna().sum() >= 80 and s.nunique(dropna=True) > 1:
            numeric_cols.append(col)
    out = df[key_cols].copy()
    if len(numeric_cols) < 2:
        return out
    vals = df[numeric_cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    med = vals.median(numeric_only=True).fillna(0.0)
    x = vals.fillna(med).to_numpy(dtype=np.float32)
    x = StandardScaler().fit_transform(x).astype(np.float32)
    k = min(n_components, x.shape[0] - 1, x.shape[1])
    if k < 1:
        return out
    z = PCA(n_components=k, svd_solver="randomized", random_state=260991).fit_transform(x)
    for i in range(k):
        out[f"{prefix}_pc{i:02d}"] = z[:, i]
    out[f"{prefix}_nan_frac"] = vals.isna().mean(axis=1).to_numpy(dtype=float)
    return out


def build_row_representation(train: pd.DataFrame, sub: pd.DataFrame, base: np.ndarray, base_sub: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    rows = all_rows(train, sub)
    frame = rows[SUB_KEY + ["split", "train_idx", "sub_idx", "global_pos", "subject_pos", "subject_count", "subject_phase", "dow", "is_weekend"]].copy()
    frame["dow_sin"] = np.sin(2.0 * np.pi * frame["dow"] / 7.0)
    frame["dow_cos"] = np.cos(2.0 * np.pi * frame["dow"] / 7.0)
    base_all = np.zeros((len(rows), len(TARGETS)), dtype=float)
    train_pos = rows["split"].eq("train").to_numpy()
    sub_pos = rows["split"].eq("submission").to_numpy()
    base_all[train_pos] = base[rows.loc[train_pos, "train_idx"].to_numpy(dtype=int)]
    base_all[sub_pos] = base_sub.loc[rows.loc[sub_pos, "sub_idx"].to_numpy(dtype=int), TARGETS].to_numpy(dtype=float)
    for j, target in enumerate(TARGETS):
        frame[f"base_{target}"] = base_all[:, j]
        frame[f"base_logit_{target}"] = logit(base_all[:, j])

    sources: list[tuple[str, Path, int]] = [
        ("rhythm", ANALYSIS / "rhythm_regular_features.parquet", 14),
        ("mp", ANALYSIS / "measurement_process_features.parquet", 18),
        ("jepa", OUT / "train_jepa_features.parquet", 14),
        ("neural", OUT / "train_neural_jepa_features.parquet", 10),
        ("proxy", ANALYSIS / "sleep_interval_proxy_features.parquet", 10),
        ("quiet", ANALYSIS / "quiet_window_residual_features.parquet", 10),
        ("prectx", ANALYSIS / "presleep_temporal_context_features.parquet", 10),
    ]
    for prefix, path, k in sources:
        if prefix in {"jepa", "neural"}:
            train_path = path
            sub_path = OUT / path.name.replace("train_", "submission_")
            if not train_path.exists() or not sub_path.exists():
                continue
            df = pd.concat([pd.read_parquet(train_path), pd.read_parquet(sub_path)], ignore_index=True).sort_values(KEY).reset_index(drop=True)
        else:
            df = source_frame(path, prefix, train, sub)
            if df is None:
                continue
        comps = pca_components(df, prefix, k)
        join_keys = SUB_KEY if "sleep_date" in comps.columns else KEY
        frame = frame.merge(comps, on=join_keys, how="left")

    numeric_cols = [c for c in frame.columns if c not in set(SUB_KEY + ["split", "train_idx", "sub_idx"])]
    vals = frame[numeric_cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    med = vals.median(numeric_only=True).fillna(0.0)
    x = vals.fillna(med).to_numpy(dtype=np.float32)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    return frame, x, base_all


def train_label_matrix(rows: pd.DataFrame, train: pd.DataFrame) -> np.ndarray:
    y = np.full((len(rows), len(TARGETS)), np.nan, dtype=float)
    mask = rows["split"].eq("train").to_numpy()
    idx = rows.loc[mask, "train_idx"].to_numpy(dtype=int)
    y[mask] = train.loc[idx, TARGETS].to_numpy(dtype=float)
    return y


def submission_blocks(train: pd.DataFrame, sub: pd.DataFrame, rows: pd.DataFrame) -> list[np.ndarray]:
    blocks: list[np.ndarray] = []
    for _sid, g in rows.groupby("subject_id", sort=False):
        split = g["split"].to_numpy()
        pos = g["global_pos"].to_numpy(dtype=int)
        start = 0
        while start < len(g):
            end = start + 1
            while end < len(g) and split[end] == split[start]:
                end += 1
            if split[start] == "submission":
                blocks.append(pos[start:end])
            start = end
    return blocks


def actual_lengths_by_subject(rows: pd.DataFrame) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for sid, g in rows.groupby("subject_id", sort=False):
        lengths = []
        split = g["split"].to_numpy()
        start = 0
        while start < len(g):
            end = start + 1
            while end < len(g) and split[end] == split[start]:
                end += 1
            if split[start] == "submission":
                lengths.append(end - start)
            start = end
        out[str(sid)] = lengths or [max(1, int(round(len(g) * 0.2)))]
    return out


def contiguous_val_blocks(rows: pd.DataFrame, val_train_indices: np.ndarray) -> list[np.ndarray]:
    val_set = set(int(x) for x in val_train_indices)
    blocks: list[np.ndarray] = []
    for _sid, g in rows[rows["split"].eq("train")].groupby("subject_id", sort=False):
        train_idx = g["train_idx"].to_numpy(dtype=int)
        pos = g["global_pos"].to_numpy(dtype=int)
        is_val = np.array([idx in val_set for idx in train_idx], dtype=bool)
        i = 0
        while i < len(g):
            if not is_val[i]:
                i += 1
                continue
            j = i + 1
            while j < len(g) and is_val[j]:
                j += 1
            blocks.append(pos[i:j])
            i = j
    return blocks


def known_mask_for_train(rows: pd.DataFrame, allowed_train_indices: np.ndarray) -> np.ndarray:
    allowed = set(int(x) for x in allowed_train_indices)
    mask = np.zeros(len(rows), dtype=bool)
    tr = rows["split"].eq("train").to_numpy()
    idx = rows["train_idx"].to_numpy(dtype=int)
    mask[tr] = np.array([int(i) in allowed for i in idx[tr]], dtype=bool)
    return mask


def block_context_features(
    rows: pd.DataFrame,
    x: np.ndarray,
    y: np.ndarray,
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
    before_tail = before[-5:]
    after_head = after[:5]

    xb = x[block_pos]
    feats = [
        np.array(
            [
                len(block_pos),
                rows.iloc[block_pos]["subject_phase"].mean(),
                rows.iloc[block_pos]["is_weekend"].mean(),
                rows.iloc[block_pos]["dow"].mean() / 6.0,
                float(block_pos.min() - subject_pos.min()) / max(len(subject_pos), 1),
                float(subject_pos.max() - block_pos.max()) / max(len(subject_pos), 1),
            ],
            dtype=float,
        ),
        np.nanmean(xb, axis=0),
        np.nanstd(xb, axis=0),
    ]
    for context in [before_tail, after_head, known_subject]:
        if len(context) == 0:
            feats.append(np.zeros(x.shape[1], dtype=float))
        else:
            feats.append(np.nanmean(x[context], axis=0))
    for context in [before_tail, after_head, known_subject]:
        if len(context) == 0:
            feats.append(np.full(len(TARGETS), 0.5, dtype=float))
            feats.append(np.zeros(len(TARGETS), dtype=float))
        else:
            vals = y[context]
            feats.append(np.nanmean(vals, axis=0))
            feats.append(np.isfinite(vals).mean(axis=0))
    gaps = np.array(
        [
            float(block_pos.min() - before_tail[-1]) if len(before_tail) else 99.0,
            float(after_head[0] - block_pos.max()) if len(after_head) else 99.0,
        ],
        dtype=float,
    )
    feats.append(gaps)
    out = np.concatenate([np.nan_to_num(f, nan=0.0, posinf=0.0, neginf=0.0).ravel() for f in feats])
    return out.astype(np.float32)


def target_latent(y_block: np.ndarray) -> np.ndarray:
    rates = np.nanmean(y_block, axis=0)
    rates = np.nan_to_num(rates, nan=0.5)
    ent = -(rates * np.log(clip(rates)) + (1.0 - rates) * np.log(clip(1.0 - rates)))
    first = y_block[0]
    last = y_block[-1]
    return np.r_[rates, ent, first, last].astype(np.float32)


def make_training_blocks(
    rows: pd.DataFrame,
    y: np.ndarray,
    allowed_train_indices: np.ndarray,
    lengths_by_subject: dict[str, list[int]],
    max_blocks_per_subject: int = 160,
) -> list[np.ndarray]:
    allowed = set(int(x) for x in allowed_train_indices)
    blocks: list[np.ndarray] = []
    for sid, g in rows[rows["split"].eq("train")].groupby("subject_id", sort=False):
        train_idx = g["train_idx"].to_numpy(dtype=int)
        pos = g["global_pos"].to_numpy(dtype=int)
        ok = np.array([idx in allowed for idx in train_idx], dtype=bool)
        sid_lengths = sorted(set(max(1, min(int(l), max(1, ok.sum()))) for l in lengths_by_subject.get(str(sid), [max(1, int(ok.sum() * 0.2))])))
        sid_blocks: list[np.ndarray] = []
        for length in sid_lengths:
            stride = max(1, length // 2)
            for start in range(0, len(pos) - length + 1, stride):
                block = pos[start : start + length]
                if ok[start : start + length].all() and np.isfinite(y[block]).all():
                    sid_blocks.append(block)
        if len(sid_blocks) > max_blocks_per_subject:
            idx = np.linspace(0, len(sid_blocks) - 1, max_blocks_per_subject).round().astype(int)
            sid_blocks = [sid_blocks[i] for i in idx]
        blocks.extend(sid_blocks)
    return blocks


def fit_block_model(x_block: np.ndarray, z_target: np.ndarray, alpha: float) -> tuple[StandardScaler, Ridge]:
    scaler = StandardScaler()
    xs = scaler.fit_transform(np.asarray(x_block, dtype=np.float64))
    xs = np.nan_to_num(xs, nan=0.0, posinf=0.0, neginf=0.0)
    model = Ridge(alpha=alpha, solver="svd")
    model.fit(xs, np.asarray(z_target, dtype=np.float64))
    return scaler, model


def predict_block_rates(scaler: StandardScaler, model: Ridge, x_block: np.ndarray, n_targets: int = 7) -> np.ndarray:
    xs = scaler.transform(np.asarray(x_block, dtype=np.float64))
    xs = np.nan_to_num(xs, nan=0.0, posinf=0.0, neginf=0.0)
    pred = model.predict(xs)
    return clip(pred[:, :n_targets])


def evaluate_blockrate_jepa(train: pd.DataFrame, sub: pd.DataFrame, rows: pd.DataFrame, x: np.ndarray, y: np.ndarray, base: np.ndarray, base_all: np.ndarray) -> tuple[pd.DataFrame, dict[tuple[float, float], np.ndarray]]:
    lengths = actual_lengths_by_subject(rows)
    y_train = train[TARGETS].to_numpy(dtype=int)
    pred_store: dict[tuple[float, float], np.ndarray] = {(a, w): base.copy() for a in ALPHAS for w in WEIGHTS}
    fold_rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train, sub, n_repeats=4):
        known = known_mask_for_train(rows, tr_idx)
        train_blocks = make_training_blocks(rows, y, tr_idx, lengths)
        x_train = np.vstack([block_context_features(rows, x, y, b, known) for b in train_blocks])
        z_train = np.vstack([target_latent(y[b]) for b in train_blocks])
        val_blocks = contiguous_val_blocks(rows, val_idx)
        x_val = np.vstack([block_context_features(rows, x, y, b, known) for b in val_blocks])
        val_block_train_idx = [rows.iloc[b]["train_idx"].to_numpy(dtype=int) for b in val_blocks]
        for alpha in ALPHAS:
            scaler, model = fit_block_model(x_train, z_train, alpha)
            rate_pred = predict_block_rates(scaler, model, x_val)
            block_rate_rows = []
            for block_i, idxs in enumerate(val_block_train_idx):
                block_rate_rows.append((idxs, rate_pred[block_i]))
            for w in WEIGHTS:
                pred = pred_store[(alpha, w)]
                for idxs, rates in block_rate_rows:
                    pred[idxs] = clip((1.0 - w) * base[idxs] + w * rates)
                fold_rows.append(
                    {
                        "experiment": "blockrate_jepa",
                        "fold": fold,
                        "alpha": alpha,
                        "weight": w,
                        "train_blocks": len(train_blocks),
                        "val_blocks": len(val_blocks),
                        "base_loss": mean_loss(y_train[val_idx], base[val_idx]),
                        "candidate_loss": mean_loss(y_train[val_idx], pred[val_idx]),
                        "delta": mean_loss(y_train[val_idx], pred[val_idx]) - mean_loss(y_train[val_idx], base[val_idx]),
                    }
                )
        print(f"blockrate {fold}: train_blocks={len(train_blocks)} val_blocks={len(val_blocks)}", flush=True)
    return pd.DataFrame(fold_rows), pred_store


def fit_submit_blockrate(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    x: np.ndarray,
    y: np.ndarray,
    base_sub: pd.DataFrame,
    base_all: np.ndarray,
    alpha: float,
    weight: float,
) -> pd.DataFrame:
    lengths = actual_lengths_by_subject(rows)
    tr_idx = np.arange(len(train))
    known = known_mask_for_train(rows, tr_idx)
    train_blocks = make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=240)
    x_train = np.vstack([block_context_features(rows, x, y, b, known) for b in train_blocks])
    z_train = np.vstack([target_latent(y[b]) for b in train_blocks])
    scaler, model = fit_block_model(x_train, z_train, alpha)
    sub_blocks = submission_blocks(train, sub, rows)
    x_sub = np.vstack([block_context_features(rows, x, y, b, known) for b in sub_blocks])
    rates = predict_block_rates(scaler, model, x_sub)
    out = base_sub.copy()
    arr = out[TARGETS].to_numpy(dtype=float).copy()
    for block_i, block in enumerate(sub_blocks):
        sub_idx = rows.iloc[block]["sub_idx"].to_numpy(dtype=int)
        arr[sub_idx] = clip((1.0 - weight) * arr[sub_idx] + weight * rates[block_i])
    out[TARGETS] = arr
    return out


def summarize_block_results(folds: pd.DataFrame, prefix: str) -> pd.DataFrame:
    summary = (
        folds.groupby(["experiment", "alpha", "weight"])
        .agg(base_loss=("base_loss", "mean"), candidate_loss=("candidate_loss", "mean"), delta=("delta", "mean"), win_rate=("delta", lambda s: float((s < 0).mean())))
        .reset_index()
        .sort_values("delta")
    )
    summary.to_csv(OUT / f"{prefix}_summary.csv", index=False)
    folds.to_csv(OUT / f"{prefix}_folds.csv", index=False)
    return summary


def evaluate_qrank_count_jepa(train: pd.DataFrame, sub: pd.DataFrame, rows: pd.DataFrame, x: np.ndarray, y: np.ndarray, base: np.ndarray) -> tuple[pd.DataFrame, dict[tuple[float, float], np.ndarray]]:
    q_idx = [TARGETS.index(t) for t in Q_TARGETS]
    lengths = actual_lengths_by_subject(rows)
    y_train = train[TARGETS].to_numpy(dtype=int)
    pred_store: dict[tuple[float, float], np.ndarray] = {(a, w): base.copy() for a in ALPHAS for w in WEIGHTS}
    fold_rows = []
    for tr_idx, val_idx, fold in geom.geometry_folds(train, sub, n_repeats=4):
        known = known_mask_for_train(rows, tr_idx)
        train_blocks = make_training_blocks(rows, y, tr_idx, lengths)
        x_train = np.vstack([block_context_features(rows, x, y, b, known) for b in train_blocks])
        z_rows = []
        for b in train_blocks:
            rates = np.nanmean(y[b][:, q_idx], axis=0)
            counts = np.nansum(y[b][:, q_idx], axis=0) / max(len(b), 1)
            ent = -(rates * np.log(clip(rates)) + (1.0 - rates) * np.log(clip(1.0 - rates)))
            z_rows.append(np.r_[rates, counts, ent, y[b[0]][q_idx], y[b[-1]][q_idx]])
        z_train = np.vstack(z_rows).astype(np.float32)
        val_blocks = contiguous_val_blocks(rows, val_idx)
        x_val = np.vstack([block_context_features(rows, x, y, b, known) for b in val_blocks])
        val_block_train_idx = [rows.iloc[b]["train_idx"].to_numpy(dtype=int) for b in val_blocks]
        for alpha in ALPHAS:
            scaler, model = fit_block_model(x_train, z_train, alpha)
            q_rates = predict_block_rates(scaler, model, x_val, n_targets=len(Q_TARGETS))
            for w in WEIGHTS:
                pred = pred_store[(alpha, w)]
                for block_i, idxs in enumerate(val_block_train_idx):
                    for local_j, target_j in enumerate(q_idx):
                        pred[idxs, target_j] = clip((1.0 - w) * base[idxs, target_j] + w * q_rates[block_i, local_j])
                fold_rows.append(
                    {
                        "experiment": "qrank_count_jepa",
                        "fold": fold,
                        "alpha": alpha,
                        "weight": w,
                        "train_blocks": len(train_blocks),
                        "val_blocks": len(val_blocks),
                        "base_loss": np.mean([loss_col(y_train[val_idx, j], base[val_idx, j]) for j in q_idx]),
                        "candidate_loss": np.mean([loss_col(y_train[val_idx, j], pred[val_idx, j]) for j in q_idx]),
                        "delta": np.mean([loss_col(y_train[val_idx, j], pred[val_idx, j]) - loss_col(y_train[val_idx, j], base[val_idx, j]) for j in q_idx]),
                        "mean7_delta": mean_loss(y_train[val_idx], pred[val_idx]) - mean_loss(y_train[val_idx], base[val_idx]),
                    }
                )
        print(f"qrank {fold}: train_blocks={len(train_blocks)} val_blocks={len(val_blocks)}", flush=True)
    return pd.DataFrame(fold_rows), pred_store


def fit_submit_qrank(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    x: np.ndarray,
    y: np.ndarray,
    base_sub: pd.DataFrame,
    alpha: float,
    weight: float,
) -> pd.DataFrame:
    q_idx = [TARGETS.index(t) for t in Q_TARGETS]
    lengths = actual_lengths_by_subject(rows)
    tr_idx = np.arange(len(train))
    known = known_mask_for_train(rows, tr_idx)
    train_blocks = make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=240)
    x_train = np.vstack([block_context_features(rows, x, y, b, known) for b in train_blocks])
    z_train = []
    for b in train_blocks:
        rates = np.nanmean(y[b][:, q_idx], axis=0)
        counts = np.nansum(y[b][:, q_idx], axis=0) / max(len(b), 1)
        ent = -(rates * np.log(clip(rates)) + (1.0 - rates) * np.log(clip(1.0 - rates)))
        z_train.append(np.r_[rates, counts, ent, y[b[0]][q_idx], y[b[-1]][q_idx]])
    scaler, model = fit_block_model(x_train, np.vstack(z_train), alpha)
    sub_blocks = submission_blocks(train, sub, rows)
    x_sub = np.vstack([block_context_features(rows, x, y, b, known) for b in sub_blocks])
    q_rates = predict_block_rates(scaler, model, x_sub, n_targets=len(Q_TARGETS))
    out = base_sub.copy()
    arr = out[TARGETS].to_numpy(dtype=float).copy()
    for block_i, block in enumerate(sub_blocks):
        sub_idx = rows.iloc[block]["sub_idx"].to_numpy(dtype=int)
        for local_j, target_j in enumerate(q_idx):
            arr[sub_idx, target_j] = clip((1.0 - weight) * arr[sub_idx, target_j] + weight * q_rates[block_i, local_j])
    out[TARGETS] = arr
    return out


SENSOR_FILES = [
    ("mcharge", "ch2025_mACStatus.parquet", "m_charging"),
    ("mactivity", "ch2025_mActivity.parquet", "m_activity"),
    ("mambience", "ch2025_mAmbience.parquet", "m_ambience"),
    ("mble", "ch2025_mBle.parquet", "m_ble"),
    ("mgps", "ch2025_mGps.parquet", "m_gps"),
    ("mlight", "ch2025_mLight.parquet", "m_light"),
    ("mscreen", "ch2025_mScreenStatus.parquet", "m_screen_use"),
    ("musage", "ch2025_mUsageStats.parquet", "m_usage_stats"),
    ("mwifi", "ch2025_mWifi.parquet", "m_wifi"),
    ("whr", "ch2025_wHr.parquet", "heart_rate"),
    ("wlight", "ch2025_wLight.parquet", "w_light"),
    ("wpedo", "ch2025_wPedo.parquet", "step"),
]


def event_value(series: pd.Series, sensor_col: str, df: pd.DataFrame) -> pd.Series:
    if sensor_col in {"m_ble", "m_wifi", "m_gps", "m_usage_stats", "heart_rate"}:
        def val(x: object) -> float:
            if not isinstance(x, list) or len(x) == 0:
                return 0.0
            if sensor_col == "heart_rate":
                arr = np.asarray(x, dtype=float)
                arr = arr[np.isfinite(arr)]
                return float(arr.mean()) if arr.size else 0.0
            if sensor_col == "m_usage_stats":
                total = 0.0
                for item in x:
                    if isinstance(item, dict):
                        total += float(item.get("total_time") or 0.0)
                return total
            if sensor_col == "m_gps":
                speeds = [float(item.get("speed") or 0.0) for item in x if isinstance(item, dict)]
                return float(np.mean(speeds)) if speeds else 0.0
            return float(len(x))
        return series.map(val).astype(float)
    if sensor_col == "step" and "step" in df.columns:
        numeric = [c for c in ["step", "step_frequency", "running_step", "walking_step", "distance", "speed", "burned_calories"] if c in df.columns]
        return df[numeric].apply(pd.to_numeric, errors="coerce").fillna(0.0).sum(axis=1)
    return pd.to_numeric(series, errors="coerce").fillna(0.0).astype(float)


def add_lifelog_bin(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    hour = out["timestamp"].dt.hour
    minute = out["timestamp"].dt.minute
    base_date = out["timestamp"].dt.normalize()
    out["lifelog_date"] = pd.to_datetime(np.where(hour < 12, base_date - pd.Timedelta(days=1), base_date))
    total_min = np.where(hour < 12, (hour + 24) * 60 + minute, hour * 60 + minute)
    out["bin30"] = ((total_min - 12 * 60) // 30).astype(int)
    return out[(out["bin30"] >= 0) & (out["bin30"] < 48)].copy()


def build_raw_canvas(rows: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    cache = OUT / "raw_timeline_canvas_30m.npy"
    meta = OUT / "raw_timeline_canvas_30m_meta.csv"
    if cache.exists() and meta.exists():
        sensors = pd.read_csv(meta)["sensor"].tolist()
        return np.load(cache), sensors
    key_to_i = {(str(r.subject_id), pd.Timestamp(r.lifelog_date)): int(r.global_pos) for r in rows.itertuples(index=False)}
    sensors = [s[0] for s in SENSOR_FILES]
    canvas = np.zeros((len(rows), len(sensors), 48, 2), dtype=np.float32)
    for sensor_i, (sensor, file_name, value_col) in enumerate(SENSOR_FILES):
        df = pd.read_parquet(ITEMS / file_name)
        if value_col not in df.columns:
            continue
        df = df[["subject_id", "timestamp", value_col] + ([c for c in ["step_frequency", "running_step", "walking_step", "distance", "speed", "burned_calories"] if c in df.columns])].copy()
        df = add_lifelog_bin(df)
        df["value"] = event_value(df[value_col], value_col, df)
        grouped = df.groupby(["subject_id", "lifelog_date", "bin30"], sort=False).agg(count=("value", "size"), value=("value", "mean")).reset_index()
        for r in grouped.itertuples(index=False):
            idx = key_to_i.get((str(r.subject_id), pd.Timestamp(r.lifelog_date)))
            if idx is None:
                continue
            b = int(r.bin30)
            canvas[idx, sensor_i, b, 0] = float(r.count)
            canvas[idx, sensor_i, b, 1] = float(r.value)
        print(f"canvas sensor {sensor} rows={len(grouped)}", flush=True)
    flat = canvas.reshape(len(rows), -1)
    mean = flat.mean(axis=0, keepdims=True)
    std = flat.std(axis=0, keepdims=True)
    std[std < 1e-6] = 1.0
    canvas = ((flat - mean) / std).reshape(canvas.shape).astype(np.float32)
    np.save(cache, canvas)
    pd.DataFrame({"sensor": sensors}).to_csv(meta, index=False)
    return canvas, sensors


class PatchEncoder(nn.Module):
    def __init__(self, channels: int, patch_count: int, dim: int = 32) -> None:
        super().__init__()
        self.patch = nn.Sequential(nn.Linear(channels, dim), nn.GELU(), nn.Linear(dim, dim))
        self.pos = nn.Parameter(torch.randn(patch_count, dim) * 0.02)
        self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.norm(self.patch(x) + self.pos)


class RawIJEPA(nn.Module):
    def __init__(self, channels: int, patch_count: int, dim: int = 32) -> None:
        super().__init__()
        self.context = PatchEncoder(channels, patch_count, dim)
        self.target = PatchEncoder(channels, patch_count, dim)
        self.predictor = nn.Sequential(nn.Linear(dim * 2, dim * 2), nn.GELU(), nn.LayerNorm(dim * 2), nn.Linear(dim * 2, dim))
        for p in self.target.parameters():
            p.requires_grad_(False)
        self.update_target(0.0)

    @torch.no_grad()
    def update_target(self, momentum: float) -> None:
        for tp, cp in zip(self.target.parameters(), self.context.parameters()):
            tp.data.mul_(momentum).add_(cp.data, alpha=1.0 - momentum)


def sample_masks(batch: int, sensors: int, bins: int, device: torch.device) -> torch.Tensor:
    mask = torch.zeros((batch, sensors, bins), dtype=torch.bool, device=device)
    for i in range(batch):
        for _ in range(4):
            sh = int(np.random.randint(2, max(3, sensors // 2 + 1)))
            tw = int(np.random.randint(5, 13))
            s0 = int(np.random.randint(0, max(1, sensors - sh + 1)))
            t0 = int(np.random.randint(0, max(1, bins - tw + 1)))
            mask[i, s0 : s0 + sh, t0 : t0 + tw] = True
    return mask.reshape(batch, sensors * bins)


def train_raw_ijepa(canvas: np.ndarray, epochs: int = 220) -> tuple[np.ndarray, list[dict[str, float]]]:
    torch.manual_seed(260991)
    np.random.seed(260991)
    n, sensors, bins, channels = canvas.shape
    patches = sensors * bins
    x = torch.from_numpy(canvas.reshape(n, patches, channels))
    model = RawIJEPA(channels, patches, dim=32)
    opt = torch.optim.AdamW(model.context.parameters(), lr=1e-3, weight_decay=1e-4)
    history: list[dict[str, float]] = []
    batch_size = 128
    for epoch in range(epochs):
        order = torch.randperm(n)
        losses = []
        for start in range(0, n, batch_size):
            idx = order[start : start + batch_size]
            xb = x[idx]
            mask = sample_masks(len(idx), sensors, bins, xb.device)
            ctx_tokens = model.context(xb)
            tgt_tokens = model.target(xb).detach()
            visible = ~mask
            denom = visible.sum(dim=1, keepdim=True).clamp_min(1)
            ctx = (ctx_tokens * visible.unsqueeze(-1)).sum(dim=1) / denom
            pos = model.context.pos.unsqueeze(0).expand(len(idx), -1, -1)
            pred = model.predictor(torch.cat([ctx.unsqueeze(1).expand(-1, patches, -1), pos], dim=-1))
            loss = ((pred[mask] - tgt_tokens[mask]) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.context.parameters(), 1.0)
            opt.step()
            model.update_target(0.996 + 0.004 * (epoch / max(epochs - 1, 1)))
            losses.append(float(loss.detach()))
        if epoch in {0, 24, 49, 99, 149, epochs - 1}:
            history.append({"epoch": float(epoch + 1), "loss": float(np.mean(losses))})
    with torch.no_grad():
        z = model.target(x).mean(dim=1).numpy()
        z_std = model.target(x).std(dim=1).numpy()
    feat = np.concatenate([z, z_std], axis=1)
    return feat.astype(np.float32), history


def scan_raw_features(train: pd.DataFrame, sub: pd.DataFrame, feat_all: np.ndarray, base: np.ndarray, base_sub: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, pd.DataFrame]:
    rows = all_rows(train, sub)
    feat_cols = [f"rawijepa__z{i:02d}" for i in range(feat_all.shape[1])]
    feat_df = pd.concat([rows[SUB_KEY + ["split", "train_idx", "sub_idx"]].reset_index(drop=True), pd.DataFrame(feat_all, columns=feat_cols)], axis=1)
    train_feat = feat_df[feat_df["split"].eq("train")].sort_values("train_idx").reset_index(drop=True)
    sub_feat = feat_df[feat_df["split"].eq("submission")].sort_values("sub_idx").reset_index(drop=True)
    train_out = train[SUB_KEY + TARGETS].merge(train_feat[SUB_KEY + feat_cols], on=SUB_KEY, how="left")
    sub_out = sub[SUB_KEY].merge(sub_feat[SUB_KEY + feat_cols], on=SUB_KEY, how="left")
    train_out.to_parquet(OUT / "train_rawijepa_features.parquet", index=False)
    sub_out.to_parquet(OUT / "submission_rawijepa_features.parquet", index=False)

    cols = broad.finite_numeric_cols(train_out)
    pre = broad.prefilter(train_out, base, cols, TARGETS, top_n=8)
    pre.to_csv(OUT / "rawijepa_prefilter.csv", index=False)
    y = train[TARGETS].to_numpy(dtype=int)
    result_rows = []
    for cand in pre.itertuples(index=False):
        target = str(cand.target)
        feature = str(cand.feature)
        mode = str(cand.mode)
        j = TARGETS.index(target)
        base_loss = loss_col(y[:, j], base[:, j])
        for c_value in [0.05, 0.20]:
            corrected = broad.oof_corrected(train_out, base, target, feature, mode, c_value)
            losses = [loss_col(y[:, j], (1.0 - w) * base[:, j] + w * corrected) for w in broad.GRID]
            best_i = int(np.argmin(losses))
            row = {
                "target": target,
                "feature": feature,
                "mode": mode,
                "c_value": c_value,
                "best_weight": float(broad.GRID[best_i]),
                "base_loss": base_loss,
                "best_loss": float(losses[best_i]),
                "delta_vs_base": float(losses[best_i] - base_loss),
            }
            if row["best_weight"] > 0 and row["delta_vs_base"] < 0:
                row.update(broad.repeated_subject_guardrail(train_out, y, base, corrected, j))
            else:
                row.update({"mean_delta": 0.0, "win_rate": 0.0})
            row["passes"] = bool(row["delta_vs_base"] < -0.0003 and row["mean_delta"] < -0.0001 and row["win_rate"] >= 0.65)
            result_rows.append(row)
    result = pd.DataFrame(result_rows).sort_values(["passes", "delta_vs_base"], ascending=[False, True])
    result.to_csv(OUT / "rawijepa_scan.csv", index=False)
    ops = []
    seen = set()
    for r in result[result["passes"]].itertuples(index=False):
        if r.target in seen:
            continue
        ops.append(r)
        seen.add(r.target)
    pred = base.copy()
    sub_pred = base_sub[TARGETS].to_numpy(dtype=float).copy()
    for op in ops:
        j = TARGETS.index(str(op.target))
        corr = broad.oof_corrected(train_out, pred, str(op.target), str(op.feature), str(op.mode), float(op.c_value))
        pred[:, j] = clip((1.0 - float(op.best_weight)) * pred[:, j] + float(op.best_weight) * corr)
        corr_sub = broad.fit_corrected(train_out, sub_out, pred, sub_pred, str(op.target), str(op.feature), str(op.mode), float(op.c_value))
        sub_pred[:, j] = clip((1.0 - float(op.best_weight)) * sub_pred[:, j] + float(op.best_weight) * corr_sub)
    submission = base_sub.copy()
    submission[TARGETS] = sub_pred
    submission.to_csv(OUT / "submission_rawijepa_selected.csv", index=False)
    np.save(OUT / "rawijepa_oof.npy", pred)
    cv = []
    for j, t in enumerate(TARGETS):
        cv.append({"target": t, "base_loss": loss_col(y[:, j], base[:, j]), "candidate_loss": loss_col(y[:, j], pred[:, j]), "delta_vs_base": loss_col(y[:, j], pred[:, j]) - loss_col(y[:, j], base[:, j])})
    cv.append({"target": "mean", "base_loss": mean_loss(y, base), "candidate_loss": mean_loss(y, pred), "delta_vs_base": mean_loss(y, pred) - mean_loss(y, base)})
    cv_df = pd.DataFrame(cv)
    cv_df.to_csv(OUT / "rawijepa_cv_estimate.csv", index=False)
    return result, cv_df, pred, submission


def public_axis_for(file_name: str) -> dict[str, float]:
    try:
        anchor_path = ANALYSIS / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv"
        stage2_path = ANALYSIS / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
        ordinal_path = ANALYSIS / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv"
        cand_path = OUT / file_name
        if not cand_path.exists():
            return {"bad_axis_projection_ratio": np.nan, "good_axis_projection_ratio": np.nan}
        dfs = {
            "anchor": pd.read_csv(anchor_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True),
            "stage2": pd.read_csv(stage2_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True),
            "ordinal": pd.read_csv(ordinal_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True),
            "candidate": pd.read_csv(cand_path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True),
        }
        stage2 = logit(dfs["stage2"][TARGETS].to_numpy(dtype=float))
        good_axis = stage2 - logit(dfs["anchor"][TARGETS].to_numpy(dtype=float))
        bad_axis = logit(dfs["ordinal"][TARGETS].to_numpy(dtype=float)) - stage2
        move = logit(dfs["candidate"][TARGETS].to_numpy(dtype=float)) - stage2
        return {
            "bad_axis_projection_ratio": float(np.dot(move.reshape(-1), bad_axis.reshape(-1)) / max(np.dot(bad_axis.reshape(-1), bad_axis.reshape(-1)), 1e-12)),
            "good_axis_projection_ratio": float(np.dot(move.reshape(-1), good_axis.reshape(-1)) / max(np.dot(good_axis.reshape(-1), good_axis.reshape(-1)), 1e-12)),
        }
    except Exception:
        pass
    return {"bad_axis_projection_ratio": np.nan, "good_axis_projection_ratio": np.nan}


def write_report(parts: list[str]) -> None:
    (OUT / "advanced_jepa_experiment_report.md").write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    train, sub, base, base_sub = read_data()
    rows, x, base_all = build_row_representation(train, sub, base, base_sub)
    y = train_label_matrix(rows, train)
    pd.concat([rows[SUB_KEY + ["split"]], pd.DataFrame(x)], axis=1).to_parquet(OUT / "advanced_jepa_row_context_features.parquet", index=False)
    print(f"row context matrix {x.shape}", flush=True)

    block_folds, block_preds = evaluate_blockrate_jepa(train, sub, rows, x, y, base, base_all)
    block_summary = summarize_block_results(block_folds, "blockrate_jepa_minimal")
    best_block = block_summary.iloc[0]
    block_submission = fit_submit_blockrate(train, sub, rows, x, y, base_sub, base_all, float(best_block["alpha"]), float(best_block["weight"]))
    block_submission.to_csv(OUT / "submission_blockrate_jepa_minimal.csv", index=False)
    np.save(OUT / "blockrate_jepa_minimal_oof.npy", block_preds[(float(best_block["alpha"]), float(best_block["weight"]))])

    q_folds, q_preds = evaluate_qrank_count_jepa(train, sub, rows, x, y, base)
    q_summary = summarize_block_results(q_folds.rename(columns={"mean7_delta": "delta_mean7"}), "qrank_count_jepa")
    # Select by the actual 7-target effect when available, otherwise Q-only delta.
    q_select = (
        q_folds.groupby(["experiment", "alpha", "weight"])
        .agg(q_delta=("delta", "mean"), mean7_delta=("mean7_delta", "mean"), win_rate=("mean7_delta", lambda s: float((s < 0).mean())))
        .reset_index()
        .sort_values(["mean7_delta", "q_delta"])
    )
    q_select.to_csv(OUT / "qrank_count_jepa_selection_summary.csv", index=False)
    best_q = q_select.iloc[0]
    q_submission = fit_submit_qrank(train, sub, rows, x, y, base_sub, float(best_q["alpha"]), float(best_q["weight"]))
    q_submission.to_csv(OUT / "submission_qrank_count_jepa.csv", index=False)
    np.save(OUT / "qrank_count_jepa_oof.npy", q_preds[(float(best_q["alpha"]), float(best_q["weight"]))])

    canvas, sensors = build_raw_canvas(rows)
    raw_feat, raw_history = train_raw_ijepa(canvas)
    pd.DataFrame(raw_history).to_csv(OUT / "rawijepa_training_history.csv", index=False)
    raw_result, raw_cv, raw_oof, raw_submission = scan_raw_features(train, sub, raw_feat, base, base_sub)

    candidate_rows = []
    y_train = train[TARGETS].to_numpy(dtype=int)
    for name, pred, summary_row in [
        ("submission_blockrate_jepa_minimal.csv", block_preds[(float(best_block["alpha"]), float(best_block["weight"]))], best_block),
        ("submission_qrank_count_jepa.csv", q_preds[(float(best_q["alpha"]), float(best_q["weight"]))], best_q),
        ("submission_rawijepa_selected.csv", raw_oof, None),
    ]:
        axis = public_axis_for(name)
        candidate_rows.append(
            {
                "candidate": name,
                "oof_loss": mean_loss(y_train, pred),
                "oof_delta_vs_stage2": mean_loss(y_train, pred) - mean_loss(y_train, base),
                **axis,
            }
        )
    cand = pd.DataFrame(candidate_rows)
    cand.to_csv(OUT / "advanced_jepa_candidate_summary.csv", index=False)

    report = [
        "# Advanced JEPA Experiments",
        "",
        "## BlockRate-JEPA Minimal",
        "",
        block_summary.head(12).to_csv(index=False),
        "",
        "## Q-Rank Count JEPA",
        "",
        q_select.head(12).to_csv(index=False),
        "",
        "## Raw Timeline I-JEPA",
        "",
        pd.DataFrame(raw_history).to_csv(index=False),
        "",
        raw_cv.to_csv(index=False),
        "",
        raw_result.head(20).to_csv(index=False),
        "",
        "## Candidate Summary",
        "",
        cand.to_csv(index=False),
    ]
    write_report(report)
    print("block best")
    print(block_summary.head(5).round(9).to_string(index=False))
    print("qrank best")
    print(q_select.head(5).round(9).to_string(index=False))
    print("raw cv")
    print(raw_cv.round(9).to_string(index=False))
    print("candidate summary")
    print(cand.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
