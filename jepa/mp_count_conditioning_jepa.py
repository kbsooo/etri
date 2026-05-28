from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "jepa"
ANALYSIS = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "lifelog_date"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(ANALYSIS))
import advanced_jepa_experiments as adv  # noqa: E402
import broad_single_feature_residual_probe as broad  # noqa: E402


GROUPS: dict[str, list[str]] = {
    "all": TARGETS,
    "q_only": ["Q1", "Q2", "Q3"],
    "q13_s23": ["Q1", "Q3", "S2", "S3"],
    "oracle_gap_core": ["Q1", "Q2", "Q3", "S2", "S3"],
    "stage_only": ["S1", "S2", "S3", "S4"],
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "s23_only": ["S2", "S3"],
}
STRENGTHS = [0.20, 0.35, 0.50, 0.70, 0.90]
SCALES = [0.50, 0.75, 1.00]
CONCENTRATIONS = [2.0, 4.0, 8.0, 20.0]
BASE_MIXES = [0.0, 0.35]
EPS = 1e-5
_COUNT_BASIS_CACHE: dict[tuple[int, int, tuple[int, ...], int], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}


@dataclass
class BlockRecord:
    indices: np.ndarray
    rates: dict[str, np.ndarray]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    return np.log(pp / (1.0 - pp))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=float)))


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def mean_loss(y: np.ndarray, p: np.ndarray) -> float:
    return float(np.mean([loss_col(y[:, j], p[:, j]) for j in range(len(TARGETS))]))


def finite(x: np.ndarray) -> np.ndarray:
    return np.nan_to_num(np.asarray(x, dtype=np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def normalize_file_name(name: str) -> str:
    return Path(str(name)).name


def collect_signal_feature_names(limit_per_source: int = 120) -> dict[str, list[str]]:
    feature_map: dict[str, list[str]] = {}
    sources = [
        ANALYSIS / "data_dissection_feature_residual_top.csv",
        ANALYSIS / "data_dissection_feature_label_top.csv",
        ANALYSIS / "data_dissection_feature_shift_top.csv",
        ANALYSIS / "data_dissection_rank_threshold_feature_candidates.csv",
    ]
    for path in sources:
        if not path.exists():
            continue
        df = pd.read_csv(path)
        if "feature_file" not in df.columns or "feature" not in df.columns:
            continue
        if "abs_corr" in df.columns:
            df = df.sort_values("abs_corr", ascending=False)
        elif "abs_shift" in df.columns:
            df = df.sort_values("abs_shift", ascending=False)
        for row in df.head(limit_per_source).itertuples(index=False):
            file_name = normalize_file_name(getattr(row, "feature_file"))
            feature = str(getattr(row, "feature"))
            feature_map.setdefault(file_name, [])
            if feature not in feature_map[file_name]:
                feature_map[file_name].append(feature)
    return feature_map


def selected_feature_paths() -> dict[str, Path]:
    return {
        "measurement_process_features.parquet": ANALYSIS / "measurement_process_features.parquet",
        "rhythm_regular_features.parquet": ANALYSIS / "rhythm_regular_features.parquet",
        "presleep_temporal_context_features.parquet": ANALYSIS / "presleep_temporal_context_features.parquet",
        "quiet_window_residual_features.parquet": ANALYSIS / "quiet_window_residual_features.parquet",
        "sleep_interval_proxy_features.parquet": ANALYSIS / "sleep_interval_proxy_features.parquet",
        "pre_sleep_relative_features.parquet": ANALYSIS / "pre_sleep_relative_features.parquet",
    }


def read_feature_file(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path)
    df = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    return df


def add_subject_variants(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    generated: dict[str, np.ndarray] = {}
    subj = frame["subject_id"].astype(str)
    for col in cols:
        vals = pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if vals.notna().sum() < 70 or vals.nunique(dropna=True) < 2:
            continue
        med = float(vals.median()) if vals.notna().any() else 0.0
        raw = vals.fillna(med).astype(float)
        subj_mean = raw.groupby(subj).transform("mean")
        subj_std = raw.groupby(subj).transform("std").replace(0.0, np.nan).fillna(1.0)
        rank = raw.groupby(subj).rank(pct=True).fillna(0.5)
        safe = col.replace("/", "_").replace(" ", "_")
        generated[f"{safe}__raw"] = raw.to_numpy(dtype=np.float32)
        generated[f"{safe}__subj_z"] = ((raw - subj_mean) / subj_std).to_numpy(dtype=np.float32)
        generated[f"{safe}__subj_rank"] = rank.to_numpy(dtype=np.float32)
    if not generated:
        return frame[SUB_KEY].copy()
    return pd.concat([frame[SUB_KEY].reset_index(drop=True), pd.DataFrame(generated)], axis=1)


def build_signal_matrix(train: pd.DataFrame, sub: pd.DataFrame, rows: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    cache = OUT / "mp_count_signal_matrix.parquet"
    if cache.exists():
        cached = pd.read_parquet(cache)
        cols = [c for c in cached.columns if c not in SUB_KEY]
        merged = rows[SUB_KEY].merge(cached, on=SUB_KEY, how="left")
        vals = merged[cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
        return vals.fillna(vals.median(numeric_only=True).fillna(0.0)).to_numpy(dtype=np.float32), cols

    feature_map = collect_signal_feature_names()
    paths = selected_feature_paths()
    base_keys = pd.concat([train[SUB_KEY], sub[SUB_KEY]], ignore_index=True).sort_values(KEY).reset_index(drop=True)
    pieces = [base_keys.copy()]
    for file_name, features in feature_map.items():
        path = paths.get(file_name)
        if path is None:
            continue
        df = read_feature_file(path)
        if df is None:
            continue
        keys = SUB_KEY if "sleep_date" in df.columns else KEY
        available = [f for f in features if f in df.columns]
        if not available:
            continue
        part = df[keys + available].copy()
        if keys == KEY:
            merged = base_keys.merge(part, on=KEY, how="left")
        else:
            merged = base_keys.merge(part, on=SUB_KEY, how="left")
        prefix = Path(file_name).stem
        rename = {c: f"{prefix}__{c}" for c in available}
        merged = merged.rename(columns=rename)
        variant_cols = [rename[c] for c in available]
        pieces.append(add_subject_variants(merged[SUB_KEY + variant_cols], variant_cols))
        print(f"signal features {file_name}: raw={len(available)} variants={len(variant_cols) * 3}", flush=True)

    out = base_keys.copy()
    for piece in pieces[1:]:
        out = out.merge(piece, on=SUB_KEY, how="left")
    cols = [c for c in out.columns if c not in SUB_KEY]
    vals = out[cols].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    vals = vals.loc[:, vals.nunique(dropna=True) > 1]
    cols = vals.columns.tolist()
    vals = vals.fillna(vals.median(numeric_only=True).fillna(0.0))
    out = pd.concat([out[SUB_KEY], vals], axis=1)
    out.to_parquet(cache, index=False)
    merged = rows[SUB_KEY].merge(out, on=SUB_KEY, how="left")
    return merged[cols].fillna(0.0).to_numpy(dtype=np.float32), cols


def reduce_row_latent(x: np.ndarray, seed: int = 372001, budget: int = 112) -> np.ndarray:
    scaler = StandardScaler()
    xs = scaler.fit_transform(finite(x))
    k = min(int(budget), xs.shape[0] - 2, xs.shape[1])
    if k < 2:
        return xs.astype(np.float32)
    pca = PCA(n_components=k, random_state=seed, svd_solver="randomized")
    z = pca.fit_transform(xs)
    return z.astype(np.float32)


def slope_of(mat: np.ndarray) -> np.ndarray:
    if len(mat) <= 1:
        return np.zeros(mat.shape[1], dtype=float)
    x = np.linspace(-0.5, 0.5, len(mat), dtype=float)
    denom = float(np.sum(x * x))
    return (x[:, None] * mat).sum(axis=0) / max(denom, 1e-9)


def summarize_z(z: np.ndarray, block: np.ndarray) -> np.ndarray:
    mat = z[np.asarray(block, dtype=int)]
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


def block_meta(rows: pd.DataFrame, block: np.ndarray) -> np.ndarray:
    block = np.asarray(block, dtype=int)
    part = rows.iloc[block]
    sid = str(part.iloc[0]["subject_id"])
    subj = rows["subject_id"].astype(str).eq(sid).to_numpy()
    subj_pos = np.where(subj)[0]
    return np.array(
        [
            len(block),
            part["subject_phase"].mean(),
            part["is_weekend"].mean(),
            part["dow"].mean() / 6.0,
            np.sin(2.0 * np.pi * part["dow"].mean() / 7.0),
            np.cos(2.0 * np.pi * part["dow"].mean() / 7.0),
            float(block.min() - subj_pos.min()) / max(len(subj_pos), 1),
            float(subj_pos.max() - block.max()) / max(len(subj_pos), 1),
        ],
        dtype=np.float32,
    )


def label_summary(y: np.ndarray, base_all: np.ndarray, idx: np.ndarray) -> np.ndarray:
    if len(idx) == 0:
        return np.r_[np.full(len(TARGETS), 0.5), np.zeros(len(TARGETS)), np.full(len(TARGETS), 0.5), np.zeros(len(TARGETS))].astype(np.float32)
    vals = y[np.asarray(idx, dtype=int)]
    base = base_all[np.asarray(idx, dtype=int)]
    return np.r_[np.nanmean(vals, axis=0), np.isfinite(vals).mean(axis=0), base.mean(axis=0), base.std(axis=0)].astype(np.float32)


def context_indices(rows: pd.DataFrame, block: np.ndarray, known: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    block = np.asarray(block, dtype=int)
    sid = str(rows.iloc[int(block[0])]["subject_id"])
    subj_idx = rows["subject_id"].astype(str).eq(sid).to_numpy()
    subj_pos = np.where(subj_idx)[0]
    block_set = set(int(p) for p in block)
    known_subject = np.array([p for p in subj_pos if known[p] and p not in block_set], dtype=int)
    past = known_subject[known_subject < block.min()][-14:]
    future = known_subject[known_subject > block.max()][:14]
    return past, future, known_subject


def summarize_context_z(z: np.ndarray, idx: np.ndarray) -> np.ndarray:
    if len(idx) == 0:
        return np.zeros(z.shape[1] * 3, dtype=np.float32)
    vals = z[np.asarray(idx, dtype=int)]
    return np.r_[vals.mean(axis=0), vals.std(axis=0), slope_of(vals)].astype(np.float32)


def context_only_features(rows: pd.DataFrame, z: np.ndarray, y: np.ndarray, base_all: np.ndarray, block: np.ndarray, known: np.ndarray) -> np.ndarray:
    past, future, prior = context_indices(rows, block, known)
    gap = np.array(
        [
            float(np.asarray(block).min() - past[-1]) if len(past) else 99.0,
            float(future[0] - np.asarray(block).max()) if len(future) else 99.0,
            len(past),
            len(future),
            len(prior),
        ],
        dtype=np.float32,
    )
    parts = [
        block_meta(rows, block),
        gap,
        summarize_context_z(z, past),
        summarize_context_z(z, future),
        summarize_context_z(z, prior),
        label_summary(y, base_all, past),
        label_summary(y, base_all, future),
        label_summary(y, base_all, prior),
        base_all[np.asarray(block, dtype=int)].mean(axis=0),
        base_all[np.asarray(block, dtype=int)].std(axis=0),
    ]
    return np.concatenate([np.nan_to_num(p, nan=0.0, posinf=0.0, neginf=0.0).ravel() for p in parts]).astype(np.float32)


def fit_context_to_target(train_context: np.ndarray, train_summary: np.ndarray, seed: int) -> tuple[StandardScaler, PCA | None, Ridge]:
    scaler = StandardScaler()
    xs = scaler.fit_transform(finite(train_context))
    k = min(96, xs.shape[0] - 2, xs.shape[1])
    pca: PCA | None = None
    if k >= 12 and k < xs.shape[1]:
        pca = PCA(n_components=k, random_state=seed, svd_solver="randomized")
        xs = pca.fit_transform(xs)
    model = Ridge(alpha=80.0, solver="svd")
    model.fit(xs, finite(train_summary))
    return scaler, pca, model


def predict_context_target(model_pack: tuple[StandardScaler, PCA | None, Ridge], context: np.ndarray) -> np.ndarray:
    scaler, pca, model = model_pack
    xs = scaler.transform(finite(context))
    if pca is not None:
        xs = pca.transform(xs)
    return model.predict(xs).astype(np.float32)


def count_model_features(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    blocks: list[np.ndarray],
    known: np.ndarray,
    pred_summary: np.ndarray,
    max_latent: int = 42,
) -> np.ndarray:
    feats = []
    z_dim = z.shape[1]
    keep = min(max_latent, z_dim)
    for i, block in enumerate(blocks):
        block = np.asarray(block, dtype=int)
        ctx = context_only_features(rows, z, y, base_all, block, known)
        actual = summarize_z(z, block)
        pred = pred_summary[i]
        resid = actual - pred
        actual_mean = actual[:z_dim][:keep]
        pred_mean = pred[:z_dim][:keep]
        resid_mean = resid[:z_dim][:keep]
        row_pos = np.linspace(0.0, 1.0, len(block)) if len(block) > 1 else np.zeros(len(block))
        base = base_all[block]
        extra = np.r_[
            actual_mean,
            pred_mean,
            resid_mean,
            np.abs(resid_mean),
            np.linalg.norm(resid_mean),
            np.linalg.norm(actual_mean),
            np.linalg.norm(pred_mean),
            float(np.dot(actual_mean, pred_mean) / max(np.linalg.norm(actual_mean) * np.linalg.norm(pred_mean), 1e-9)),
            row_pos.mean(),
            row_pos.std(),
            base.mean(axis=0),
            base.std(axis=0),
            base[0],
            base[-1],
            base[-1] - base[0],
        ]
        feats.append(np.r_[ctx, extra].astype(np.float32))
    return np.vstack(feats).astype(np.float32)


def block_rates(y: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    return np.vstack([np.nanmean(y[np.asarray(b, dtype=int)], axis=0) for b in blocks]).astype(np.float32)


def block_base_rates(base_all: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    return np.vstack([base_all[np.asarray(b, dtype=int)].mean(axis=0) for b in blocks]).astype(np.float32)


def reduce_fit_predict(train_x: np.ndarray, query_x: np.ndarray, seed: int, budget: int = 80) -> tuple[np.ndarray, np.ndarray]:
    scaler = StandardScaler()
    tr = scaler.fit_transform(finite(train_x))
    qu = scaler.transform(finite(query_x))
    k = min(budget, tr.shape[0] - 2, tr.shape[1])
    if k >= 12 and k < tr.shape[1]:
        pca = PCA(n_components=k, random_state=seed, svd_solver="randomized")
        tr = pca.fit_transform(tr)
        qu = pca.transform(qu)
    return tr.astype(np.float32), qu.astype(np.float32)


def fit_rate_methods(train_x: np.ndarray, query_x: np.ndarray, train_rate: np.ndarray, train_base: np.ndarray, query_base: np.ndarray, seed: int) -> dict[str, np.ndarray]:
    tr, qu = reduce_fit_predict(train_x, query_x, seed=seed, budget=86)
    methods: dict[str, np.ndarray] = {}

    ridge_rate = Ridge(alpha=18.0, solver="svd")
    ridge_rate.fit(tr, train_rate)
    methods["mpj_ridge_rate"] = clip(ridge_rate.predict(qu))

    ridge_resid = Ridge(alpha=35.0, solver="svd")
    ridge_resid.fit(tr, train_rate - train_base)
    methods["mpj_ridge_resid"] = clip(query_base + ridge_resid.predict(qu))

    ridge_heavy = Ridge(alpha=120.0, solver="svd")
    ridge_heavy.fit(tr, train_rate - train_base)
    methods["mpj_ridge_resid_heavy"] = clip(query_base + ridge_heavy.predict(qu))

    n_neighbors = min(18, max(3, len(train_rate) // 8))
    knn = KNeighborsRegressor(n_neighbors=n_neighbors, weights="distance", metric="euclidean")
    knn.fit(tr, train_rate)
    methods[f"mpj_knn{n_neighbors}"] = clip(knn.predict(qu))

    forest = ExtraTreesRegressor(
        n_estimators=160,
        max_depth=5,
        min_samples_leaf=5,
        max_features=0.65,
        random_state=seed + 17,
        n_jobs=1,
    )
    forest.fit(tr, train_rate - train_base)
    methods["mpj_xt_resid"] = clip(query_base + forest.predict(qu))

    methods["mpj_blend_resid_knn"] = clip(0.55 * methods["mpj_ridge_resid"] + 0.45 * methods[f"mpj_knn{n_neighbors}"])
    methods["mpj_blend_xt_ridge"] = clip(0.50 * methods["mpj_xt_resid"] + 0.50 * methods["mpj_ridge_resid_heavy"])
    methods["mpj_base_anchor"] = clip(query_base)
    return methods


def fit_predict_block_rates(
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    train_indices: np.ndarray,
    train_blocks: list[np.ndarray],
    query_blocks: list[np.ndarray],
    seed: int,
) -> dict[str, np.ndarray]:
    known = adv.known_mask_for_train(rows, train_indices)
    train_context = np.vstack([context_only_features(rows, z, y, base_all, b, known) for b in train_blocks])
    train_summary = np.vstack([summarize_z(z, b) for b in train_blocks])
    model_pack = fit_context_to_target(train_context, train_summary, seed=seed + 201)
    query_context = np.vstack([context_only_features(rows, z, y, base_all, b, known) for b in query_blocks])
    pred_train_summary = predict_context_target(model_pack, train_context)
    pred_query_summary = predict_context_target(model_pack, query_context)
    train_x = count_model_features(rows, z, y, base_all, train_blocks, known, pred_train_summary)
    query_x = count_model_features(rows, z, y, base_all, query_blocks, known, pred_query_summary)
    train_rate = block_rates(y, train_blocks)
    train_base = block_base_rates(base_all, train_blocks)
    query_base = block_base_rates(base_all, query_blocks)
    methods = fit_rate_methods(train_x, query_x, train_rate, train_base, query_base, seed=seed + 311)
    return methods


def build_oof_records(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
    cv_mode: str,
    repeats: int,
) -> list[BlockRecord]:
    lengths = adv.actual_lengths_by_subject(rows)
    if cv_mode == "subject_chunk":
        folds = [(tr, va, f"subject_chunk_{i:02d}") for i, (tr, va) in enumerate(broad.qlp.make_subject_blocks(train))]
    elif cv_mode == "geometry":
        folds = list(adv.geom.geometry_folds(train, sub, n_repeats=repeats, seed=372500))
    else:
        raise ValueError(cv_mode)
    records: list[BlockRecord] = []
    for fold_i, (tr_idx, val_idx, fold) in enumerate(folds):
        train_blocks = adv.make_training_blocks(rows, y, tr_idx, lengths, max_blocks_per_subject=300)
        query_blocks = adv.contiguous_val_blocks(rows, val_idx)
        if not train_blocks or not query_blocks:
            continue
        rates = fit_predict_block_rates(rows, z, y, base_all, tr_idx, train_blocks, query_blocks, seed=372700 + fold_i * 101)
        for block_i, block in enumerate(query_blocks):
            idx = rows.iloc[block]["train_idx"].to_numpy(dtype=int)
            records.append(BlockRecord(indices=idx, rates={name: val[block_i] for name, val in rates.items()}))
        covered = len(set(np.concatenate([r.indices for r in records]))) if records else 0
        print(f"mp-count {cv_mode} {fold}: train_blocks={len(train_blocks)} val_blocks={len(query_blocks)} covered={covered}", flush=True)
    return records


def build_submission_records(
    train: pd.DataFrame,
    sub: pd.DataFrame,
    rows: pd.DataFrame,
    z: np.ndarray,
    y: np.ndarray,
    base_all: np.ndarray,
) -> list[BlockRecord]:
    lengths = adv.actual_lengths_by_subject(rows)
    train_indices = np.arange(len(train))
    train_blocks = adv.make_training_blocks(rows, y, train_indices, lengths, max_blocks_per_subject=360)
    query_blocks = adv.submission_blocks(train, sub, rows)
    rates = fit_predict_block_rates(rows, z, y, base_all, train_indices, train_blocks, query_blocks, seed=389001)
    records = []
    for block_i, block in enumerate(query_blocks):
        idx = rows.iloc[block]["sub_idx"].to_numpy(dtype=int)
        records.append(BlockRecord(indices=idx, rates={name: val[block_i] for name, val in rates.items()}))
    return records


def poisson_binomial_distribution(p: np.ndarray) -> np.ndarray:
    pp = clip(p)
    n = len(pp)
    dist = np.zeros(n + 1, dtype=float)
    dist[0] = 1.0
    for prob in pp:
        new = np.zeros_like(dist)
        new[:-1] += dist[:-1] * (1.0 - prob)
        new[1:] += dist[:-1] * prob
        dist = new
    s = dist.sum()
    return dist / max(s, 1e-15)


def beta_binomial_distribution(n: int, mean: float, concentration: float) -> np.ndarray:
    mean = float(np.clip(mean, EPS, 1.0 - EPS))
    conc = max(float(concentration), 1e-3)
    a = mean * conc
    b = (1.0 - mean) * conc
    log_norm = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    vals = []
    for k in range(n + 1):
        log_comb = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
        log_p = log_comb + math.lgamma(k + a) + math.lgamma(n - k + b) - math.lgamma(n + a + b) + log_norm
        vals.append(log_p)
    arr = np.exp(np.asarray(vals) - np.max(vals))
    return arr / max(float(arr.sum()), 1e-15)


def condition_bernoulli_on_count(p: np.ndarray, q_count: np.ndarray) -> np.ndarray:
    pp = clip(p)
    n = len(pp)
    q = np.asarray(q_count, dtype=float)
    if len(q) != n + 1:
        raise ValueError("q_count length must be n + 1")
    q = np.clip(q, 0.0, None)
    q = q / max(float(q.sum()), 1e-15)

    f = np.zeros((n + 1, n + 1), dtype=float)
    b = np.zeros((n + 1, n + 1), dtype=float)
    f[0, 0] = 1.0
    for i, prob in enumerate(pp):
        f[i + 1, : i + 1] += f[i, : i + 1] * (1.0 - prob)
        f[i + 1, 1 : i + 2] += f[i, : i + 1] * prob
    b[n, 0] = 1.0
    for i in range(n - 1, -1, -1):
        prob = pp[i]
        max_s = n - i - 1
        b[i, : max_s + 1] += b[i + 1, : max_s + 1] * (1.0 - prob)
        b[i, 1 : max_s + 2] += b[i + 1, : max_s + 1] * prob

    denom = np.clip(f[n], 1e-18, None)
    out = np.zeros(n, dtype=float)
    for i, prob in enumerate(pp):
        numer_by_k = np.zeros(n + 1, dtype=float)
        for k in range(1, n + 1):
            total = 0.0
            lo = max(0, k - 1 - (n - i - 1))
            hi = min(i, k - 1)
            for a in range(lo, hi + 1):
                total += f[i, a] * b[i + 1, k - 1 - a]
            numer_by_k[k] = prob * total
        cond = numer_by_k / denom
        out[i] = float(np.sum(q * cond))
    return clip(out)


def count_condition_basis(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pp = clip(p)
    n = len(pp)
    f = np.zeros((n + 1, n + 1), dtype=float)
    b = np.zeros((n + 1, n + 1), dtype=float)
    f[0, 0] = 1.0
    for i, prob in enumerate(pp):
        f[i + 1, : i + 1] += f[i, : i + 1] * (1.0 - prob)
        f[i + 1, 1 : i + 2] += f[i, : i + 1] * prob
    b[n, 0] = 1.0
    for i in range(n - 1, -1, -1):
        prob = pp[i]
        max_s = n - i - 1
        b[i, : max_s + 1] += b[i + 1, : max_s + 1] * (1.0 - prob)
        b[i, 1 : max_s + 2] += b[i + 1, : max_s + 1] * prob

    denom = np.clip(f[n], 1e-18, None)
    basis = np.zeros((n + 1, n), dtype=float)
    for i, prob in enumerate(pp):
        for k in range(1, n + 1):
            total = 0.0
            lo = max(0, k - 1 - (n - i - 1))
            hi = min(i, k - 1)
            for a in range(lo, hi + 1):
                total += f[i, a] * b[i + 1, k - 1 - a]
            basis[k, i] = prob * total / denom[k]
    count_dist = f[n] / max(float(f[n].sum()), 1e-15)
    return basis, count_dist


def cached_count_basis(base: np.ndarray, idx: np.ndarray, target_j: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    idx = np.asarray(idx, dtype=int)
    p0 = clip(base[idx, target_j])
    key = (len(base), int(target_j), tuple(int(i) for i in idx), hash(p0.tobytes()))
    cached = _COUNT_BASIS_CACHE.get(key)
    if cached is not None:
        return cached
    basis, count_dist = count_condition_basis(p0)
    cached = (p0, basis, count_dist)
    _COUNT_BASIS_CACHE[key] = cached
    return cached


def conditioned_block_probs_from_basis(
    p0: np.ndarray,
    basis: np.ndarray,
    q_base: np.ndarray,
    target_rate: float,
    concentration: float,
    base_mix: float,
    scale: float,
) -> np.ndarray:
    n = len(p0)
    rate = float(np.clip(target_rate, EPS, 1.0 - EPS))
    q_model = beta_binomial_distribution(n, rate, concentration)
    if base_mix > 0.0:
        q = (1.0 - base_mix) * q_model + base_mix * q_base
    else:
        q = q_model
    cond = clip(q @ basis)
    move = logit(cond) - logit(p0)
    return clip(sigmoid(logit(p0) + float(scale) * move))


def apply_solver(
    base: np.ndarray,
    records: list[BlockRecord],
    method: str,
    group: str,
    strength: float,
    concentration: float,
    base_mix: float,
    scale: float,
) -> np.ndarray:
    out_sum = np.zeros_like(base, dtype=float)
    out_count = np.zeros_like(base, dtype=float)
    target_set = set(GROUPS[group])
    for rec in records:
        if method not in rec.rates:
            continue
        idx = np.asarray(rec.indices, dtype=int)
        rate = rec.rates[method]
        for j, target in enumerate(TARGETS):
            if target not in target_set:
                continue
            p0, basis, q_base = cached_count_basis(base, idx, j)
            base_mean = float(np.mean(p0))
            target_rate = (1.0 - strength) * base_mean + strength * float(rate[j])
            new_p = conditioned_block_probs_from_basis(p0, basis, q_base, target_rate, concentration=concentration, base_mix=base_mix, scale=scale)
            out_sum[idx, j] += new_p
            out_count[idx, j] += 1.0
    pred = base.copy()
    mask = out_count > 0
    pred[mask] = out_sum[mask] / out_count[mask]
    return clip(pred)


def candidate_key(row: pd.Series | object) -> tuple[str, str, float, float, float, float]:
    if isinstance(row, pd.Series):
        return (
            str(row["method"]),
            str(row["group"]),
            float(row["strength"]),
            float(row["concentration"]),
            float(row["base_mix"]),
            float(row["scale"]),
        )
    return (
        str(getattr(row, "method")),
        str(getattr(row, "group")),
        float(getattr(row, "strength")),
        float(getattr(row, "concentration")),
        float(getattr(row, "base_mix")),
        float(getattr(row, "scale")),
    )


def scan_records(records: list[BlockRecord], base: np.ndarray, y: np.ndarray, cv_mode: str) -> pd.DataFrame:
    methods = sorted(records[0].rates.keys()) if records else []
    base_loss = mean_loss(y, base)
    rows = []
    total = len(methods) * len(GROUPS) * len(STRENGTHS) * len(CONCENTRATIONS) * len(BASE_MIXES) * len(SCALES)
    done = 0
    for method in methods:
        for group in GROUPS:
            for strength in STRENGTHS:
                for concentration in CONCENTRATIONS:
                    for base_mix in BASE_MIXES:
                        for scale in SCALES:
                            pred = apply_solver(base, records, method, group, strength, concentration, base_mix, scale)
                            row = {
                                "cv_mode": cv_mode,
                                "method": method,
                                "group": group,
                                "strength": strength,
                                "concentration": concentration,
                                "base_mix": base_mix,
                                "scale": scale,
                                "base_loss": base_loss,
                                "oof_loss": mean_loss(y, pred),
                            }
                            row["oof_delta_vs_stage2"] = row["oof_loss"] - base_loss
                            for j, target in enumerate(TARGETS):
                                row[f"loss_{target}"] = loss_col(y[:, j], pred[:, j])
                            rows.append(row)
                            done += 1
        print(f"mp-count scan {cv_mode}: method={method} done={done}/{total}", flush=True)
    return pd.DataFrame(rows).sort_values(["oof_loss", "oof_delta_vs_stage2"]).reset_index(drop=True)


def remap_geometry_records(records: list[BlockRecord], y_train: np.ndarray, base: np.ndarray) -> tuple[list[BlockRecord], np.ndarray, np.ndarray]:
    covered = sorted(set(np.concatenate([r.indices for r in records]))) if records else []
    pos_map = {idx: pos for pos, idx in enumerate(covered)}
    remapped = [
        BlockRecord(indices=np.array([pos_map[int(i)] for i in rec.indices], dtype=int), rates=rec.rates)
        for rec in records
    ]
    return remapped, base[covered], y_train[covered]


def emit_submissions(scan: pd.DataFrame, sub_records: list[BlockRecord], base_sub_df: pd.DataFrame, top_n: int = 24) -> pd.DataFrame:
    base_sub = base_sub_df[TARGETS].to_numpy(dtype=float)
    emitted = []
    seen: set[tuple[str, str, float, float, float, float]] = set()
    def fmt(x: float) -> str:
        return f"{float(x):g}".replace(".", "p")

    for row in scan.itertuples(index=False):
        key = candidate_key(row)
        if key in seen:
            continue
        seen.add(key)
        if len(emitted) >= top_n:
            break
        method, group, strength, concentration, base_mix, scale = key
        pred = apply_solver(base_sub, sub_records, method, group, strength, concentration, base_mix, scale)
        file_stem = (
            "submission_mp_count_conditioning_jepa"
            f"_{str(getattr(row, 'cv_mode'))}"
            f"_{method}_{group}"
            f"_st{fmt(strength)}_c{fmt(concentration)}_bm{fmt(base_mix)}_sc{fmt(scale)}"
        )
        file_name = f"{file_stem}.csv"
        out = base_sub_df.copy()
        out[TARGETS] = pred
        out.to_csv(OUT / file_name, index=False)
        emitted.append(
            {
                "candidate": file_name,
                "cv_mode": str(getattr(row, "cv_mode")),
                "method": method,
                "group": group,
                "strength": strength,
                "concentration": concentration,
                "base_mix": base_mix,
                "scale": scale,
                "oof_loss": float(getattr(row, "oof_loss")),
                "oof_delta_vs_stage2": float(getattr(row, "oof_delta_vs_stage2")),
                **adv.public_axis_for(file_name),
            }
        )
    return pd.DataFrame(emitted)


def validate_submission(path: Path, sample: pd.DataFrame) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    sample_sorted = sample.sort_values(KEY).reset_index(drop=True)
    return {
        "file": path.name,
        "rows": len(df),
        "key_ok": bool(df[SUB_KEY].equals(sample_sorted[SUB_KEY])),
        "min_prob": float(df[TARGETS].min().min()),
        "max_prob": float(df[TARGETS].max().max()),
        "range_ok": bool(((df[TARGETS] > 0.0) & (df[TARGETS] < 1.0)).all().all()),
    }


def write_report(chunk_scan: pd.DataFrame, geom_scan: pd.DataFrame, candidates: pd.DataFrame, validations: pd.DataFrame) -> None:
    lines = [
        "# Measurement-Process Count Conditioning JEPA",
        "",
        "This experiment uses the earlier data dissection result directly: measurement process and sensor coverage are treated as the visible target-block state, while labels are hidden.",
        "",
        "Pipeline:",
        "1. Build a row latent from stage2 base probabilities, measurement-process features, rhythm regularity, quiet windows, pre-sleep context, and selected forensics features.",
        "2. For each hidden-like block, predict the target block latent from surrounding context only. The actual minus predicted latent is the JEPA residual.",
        "3. Predict each block's 7-label rate/count latent from actual latent, context-predicted latent, JEPA residual, context labels, and base block probabilities.",
        "4. Convert the predicted rate into a beta-binomial count distribution and exactly condition the row-level Bernoulli probabilities on that count distribution.",
        "",
        "## Subject-Chunk Top",
        "",
        chunk_scan.head(40).to_csv(index=False),
        "",
        "## Geometry Top",
        "",
        geom_scan.head(40).to_csv(index=False) if not geom_scan.empty else "No geometry rows.",
        "",
        "## Emitted Candidates",
        "",
        candidates.to_csv(index=False),
        "",
        "## Submission Validation",
        "",
        validations.to_csv(index=False),
    ]
    (OUT / "mp_count_conditioning_jepa_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    repeats = int(os.environ.get("MPCOUNT_GEOM_REPEATS", "5"))
    top_n = int(os.environ.get("MPCOUNT_TOP_N", "24"))

    train, sub, base, base_sub = adv.read_data()
    rows, x_adv, base_all = adv.build_row_representation(train, sub, base, base_sub)
    y_full = adv.train_label_matrix(rows, train)
    y_train = train[TARGETS].to_numpy(dtype=int)
    signal_x, signal_cols = build_signal_matrix(train, sub, rows)
    z = reduce_row_latent(np.hstack([x_adv, signal_x]), budget=112)
    pd.DataFrame({"n_signal_cols": [len(signal_cols)], "row_latent_dim": [z.shape[1]]}).to_csv(
        OUT / "mp_count_conditioning_jepa_latent_meta.csv", index=False
    )
    print(f"mp-count latent: adv={x_adv.shape} signal={signal_x.shape} z={z.shape}", flush=True)

    chunk_records = build_oof_records(train, sub, rows, z, y_full, base_all, "subject_chunk", repeats=repeats)
    chunk_scan = scan_records(chunk_records, base, y_train, "subject_chunk")
    chunk_scan.to_csv(OUT / "mp_count_conditioning_jepa_subject_chunk_scan.csv", index=False)

    geom_records = build_oof_records(train, sub, rows, z, y_full, base_all, "geometry", repeats=repeats)
    if geom_records:
        remapped, geom_base, geom_y = remap_geometry_records(geom_records, y_train, base)
        geom_scan = scan_records(remapped, geom_base, geom_y, "geometry")
    else:
        geom_scan = pd.DataFrame()
    geom_scan.to_csv(OUT / "mp_count_conditioning_jepa_geometry_scan.csv", index=False)

    combined = pd.concat([chunk_scan.head(16), geom_scan.head(12)], ignore_index=True)
    combined = combined.drop_duplicates(["cv_mode", "method", "group", "strength", "concentration", "base_mix", "scale"])
    sub_records = build_submission_records(train, sub, rows, z, y_full, base_all)
    candidates = emit_submissions(combined, sub_records, base_sub, top_n=top_n)
    candidates.to_csv(OUT / "mp_count_conditioning_jepa_candidate_summary.csv", index=False)
    validations = pd.DataFrame([validate_submission(OUT / name, sub) for name in candidates["candidate"]])
    validations.to_csv(OUT / "mp_count_conditioning_jepa_submission_validation.csv", index=False)
    write_report(chunk_scan, geom_scan, candidates, validations)

    print("MP-COUNT candidates")
    print(candidates.to_string(index=False), flush=True)
    print("MP-COUNT subject_chunk top")
    print(chunk_scan.head(20).to_string(index=False), flush=True)
    if not geom_scan.empty:
        print("MP-COUNT geometry top")
        print(geom_scan.head(20).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
