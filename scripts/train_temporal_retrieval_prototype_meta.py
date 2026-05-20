from __future__ import annotations

import json
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import log_loss
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5
SEED = 2026


@dataclass(frozen=True)
class Candidate:
    name: str
    oof_path: Path
    submission_path: Path


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50.0, 50.0)))


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, EPS, 1.0 - EPS)
    return np.log(p / (1.0 - p))


def signed_log1p(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.astype(float).copy()
    for col in out.columns:
        values = out[col].to_numpy(dtype=float)
        finite = values[np.isfinite(values)]
        if len(finite) and np.nanpercentile(np.abs(finite), 95) > 1000:
            out[col] = np.sign(values) * np.log1p(np.abs(values))
    return out


def default_candidates() -> list[Candidate]:
    return [
        Candidate(
            "oldbalanced",
            Path("outputs/sample_oldbalanced_plus_q1fastmid_vs_multi_signal/oof_sample_support_target_blend.csv"),
            Path("outputs/sample_oldbalanced_plus_q1fastmid_vs_multi_signal/submission_sample_support_target_blend.csv"),
        ),
        Candidate(
            "recovery15",
            Path("outputs/lb_feedback_recovery_uploads/oof_15_v18_old15_prob_blend.csv"),
            Path("outputs/lb_feedback_recovery_uploads/submission_15_v18_old15_prob_blend.csv"),
        ),
        Candidate(
            "v18_q3tail",
            Path("outputs/sample_portfolio_v18_q3tail_w100/oof_sample_support_target_blend.csv"),
            Path("outputs/sample_portfolio_v18_q3tail_w100/submission_sample_support_target_blend.csv"),
        ),
        Candidate(
            "v17_robust",
            Path("outputs/sample_weighted_targetwise_portfolio_v17_robust/oof_sample_weighted_targetwise_blend.csv"),
            Path("outputs/sample_weighted_targetwise_portfolio_v17_robust/submission_sample_weighted_targetwise_blend.csv"),
        ),
        Candidate(
            "v35e",
            Path("outputs/sample_portfolio_v35e_v35b_plus_stack_q2mid_w050_prob/oof_sample_support_target_blend.csv"),
            Path("outputs/sample_portfolio_v35e_v35b_plus_stack_q2mid_w050_prob/submission_sample_support_target_blend.csv"),
        ),
        Candidate(
            "multi_signal",
            Path("outputs/multi_signal_qcount_blend_w015_020_015_015/oof_multi_signal_qcount_blend.csv"),
            Path("outputs/multi_signal_qcount_blend_w015_020_015_015/submission_multi_signal_qcount_blend.csv"),
        ),
        Candidate(
            "latent_temporal",
            Path("outputs/latent_decoder/oof_targetwise_temporal_blend.csv"),
            Path("outputs/latent_decoder/submission_latent_decoder_targetwise_temporal.csv"),
        ),
        Candidate(
            "diverse_lgbm_latent_rankdev",
            Path("outputs/diverse_tabular_decoder/oof_lgbm_latent_rankdev.csv"),
            Path("outputs/diverse_tabular_decoder/submission_lgbm_latent_rankdev.csv"),
        ),
        Candidate(
            "diverse_xgb_latent_rankdev",
            Path("outputs/diverse_tabular_decoder/oof_xgb_latent_rankdev.csv"),
            Path("outputs/diverse_tabular_decoder/submission_xgb_latent_rankdev.csv"),
        ),
        Candidate(
            "hourly_fused",
            Path("outputs/hourly_fused_sequence_decoder_on_v14/oof_fused_hgb_k260_l2_15_sample.csv"),
            Path("outputs/hourly_fused_sequence_decoder_on_v14/submission_fused_hgb_k260_l2_15_sample.csv"),
        ),
    ]


def prediction_matrix(oof: pd.DataFrame) -> np.ndarray:
    return np.clip(
        np.column_stack([oof[f"pred_{target}"].to_numpy(dtype=float) for target in TARGET_COLUMNS]),
        EPS,
        1.0 - EPS,
    )


def submission_matrix(submission: pd.DataFrame) -> np.ndarray:
    return np.clip(submission[TARGET_COLUMNS].to_numpy(dtype=float), EPS, 1.0 - EPS)


def load_prediction_bank(
    train: pd.DataFrame,
    sample: pd.DataFrame,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    names: list[str] = []
    oof_blocks: list[np.ndarray] = []
    sub_blocks: list[np.ndarray] = []
    for candidate in default_candidates():
        if not candidate.oof_path.exists() or not candidate.submission_path.exists():
            continue
        oof = normalize_keys(pd.read_csv(candidate.oof_path))
        submission = normalize_keys(pd.read_csv(candidate.submission_path))
        if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
            continue
        if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
            continue
        names.append(candidate.name)
        oof_blocks.append(prediction_matrix(oof))
        sub_blocks.append(submission_matrix(submission))
    if not oof_blocks:
        raise RuntimeError("No compatible anchor prediction files were found.")
    return names, np.stack(oof_blocks, axis=1), np.stack(sub_blocks, axis=1)


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int = 5) -> list[tuple[np.ndarray, np.ndarray]]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_parts: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(dtype=int), n_folds)
        for fold, chunk in enumerate(chunks):
            val_parts[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame), dtype=int)
    folds = []
    for val in val_parts:
        val_idx = np.array(sorted(val), dtype=int)
        folds.append((np.setdiff1d(all_idx, val_idx), val_idx))
    return folds


def add_panel_features(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_rows = pd.concat(
        [
            train[KEY_COLUMNS].assign(_split="train", _row=np.arange(len(train))),
            sample[KEY_COLUMNS].assign(_split="sample", _row=np.arange(len(sample))),
        ],
        ignore_index=True,
    )
    all_rows = all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).copy()
    all_rows["panel_index"] = all_rows.groupby("subject_id").cumcount().astype(float)
    denom = all_rows.groupby("subject_id")["panel_index"].transform("max").replace(0, 1)
    all_rows["panel_position"] = all_rows["panel_index"] / denom
    dates = pd.to_datetime(all_rows["lifelog_date"])
    all_rows["weekday"] = dates.dt.weekday.astype(float)
    all_rows["weekday_sin"] = np.sin(2 * np.pi * all_rows["weekday"] / 7.0)
    all_rows["weekday_cos"] = np.cos(2 * np.pi * all_rows["weekday"] / 7.0)
    out = all_rows.sort_index()
    train_panel = out[out["_split"].eq("train")].sort_values("_row").reset_index(drop=True)
    sample_panel = out[out["_split"].eq("sample")].sort_values("_row").reset_index(drop=True)
    return train_panel, sample_panel


def load_master_matrix(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    master = normalize_keys(pd.read_parquet("artifacts/10_master_daily.parquet"))
    train_keys = train[KEY_COLUMNS].copy()
    sample_keys = sample[KEY_COLUMNS].copy()
    train_m = train_keys.merge(master, on=KEY_COLUMNS, how="left", validate="one_to_one")
    sample_m = sample_keys.merge(master, on=KEY_COLUMNS, how="left", validate="one_to_one")
    if train_m.isna().all(axis=1).any() or sample_m.isna().all(axis=1).any():
        raise ValueError("Master daily feature merge produced empty rows.")

    exclude = set(KEY_COLUMNS + TARGET_COLUMNS + ["role", "date", "sleep_onset", "wake_time"])
    numeric_cols = [c for c in train_m.select_dtypes(include=[np.number]).columns if c not in exclude]
    keep_cols = []
    both = pd.concat([train_m[numeric_cols], sample_m[numeric_cols]], ignore_index=True)
    for col in numeric_cols:
        missing = both[col].isna().mean()
        unique = both[col].nunique(dropna=True)
        if missing <= 0.55 and unique > 1:
            keep_cols.append(col)

    train_x = signed_log1p(train_m[keep_cols])
    sample_x = signed_log1p(sample_m[keep_cols])
    return train_x, sample_x, keep_cols


def merge_latents(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    latent_specs = [
        ("diff64", Path("outputs/diffusion_encoder/day_latents.parquet")),
        ("tc96", Path("outputs/temporal_contrastive_encoder_zero_v1/day_latents.parquet")),
        ("denoise64", Path("outputs/temporal_contrastive_encoder_zero_denoise64_v1/day_latents.parquet")),
    ]
    train_parts: list[pd.DataFrame] = []
    sample_parts: list[pd.DataFrame] = []
    names: list[str] = []
    for prefix, path in latent_specs:
        if not path.exists():
            continue
        lat = normalize_keys(pd.read_parquet(path))
        z_cols = [c for c in lat.columns if c.startswith("z_")]
        renamed = lat[KEY_COLUMNS + z_cols].rename(columns={c: f"{prefix}_{c}" for c in z_cols})
        train_join = train[KEY_COLUMNS].merge(renamed, on=KEY_COLUMNS, how="left", validate="one_to_one")
        sample_join = sample[KEY_COLUMNS].merge(renamed, on=KEY_COLUMNS, how="left", validate="one_to_one")
        cols = [f"{prefix}_{c}" for c in z_cols]
        train_parts.append(train_join[cols])
        sample_parts.append(sample_join[cols])
        names.extend(cols)
    if not train_parts:
        return pd.DataFrame(index=train.index), pd.DataFrame(index=sample.index), []
    return pd.concat(train_parts, axis=1), pd.concat(sample_parts, axis=1), names


def feature_groups(columns: list[str]) -> dict[str, list[int]]:
    patterns = {
        "sleep": ["sleep", "tst", "awak", "sol", "night", "prebed"],
        "mobility": ["gps", "place", "home", "work", "moving", "mob_", "outing", "stationary", "transient", "wifi", "ble"],
        "phone": ["screen", "app_", "prebed", "charge", "call", "browser", "sns", "video", "messenger", "music"],
        "physiology": ["hr", "rmssd", "sdnn", "pnn50", "pedo", "step", "cal_", "light"],
        "ambience": ["amb_", "mlight", "wlight"],
    }
    groups: dict[str, list[int]] = {}
    for name, pats in patterns.items():
        idx = [i for i, col in enumerate(columns) if any(p in col.lower() for p in pats)]
        if idx:
            groups[name] = idx
    groups["all"] = list(range(len(columns)))
    return groups


def fit_numeric_transform(train_x: pd.DataFrame, sample_x: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    imputer = SimpleImputer(strategy="median", keep_empty_features=True)
    scaler = StandardScaler()
    train_imp = imputer.fit_transform(train_x)
    sample_imp = imputer.transform(sample_x)
    train_scaled = scaler.fit_transform(train_imp)
    sample_scaled = scaler.transform(sample_imp)
    return train_scaled.astype(np.float32), sample_scaled.astype(np.float32)


def pca_features(train_blocks: list[np.ndarray], sample_blocks: list[np.ndarray], n_components: int = 32) -> tuple[np.ndarray, np.ndarray]:
    train_x = np.column_stack(train_blocks)
    sample_x = np.column_stack(sample_blocks)
    n_components = min(n_components, train_x.shape[0] - 1, train_x.shape[1])
    pca = PCA(n_components=n_components, random_state=SEED)
    train_p = pca.fit_transform(train_x)
    sample_p = pca.transform(sample_x)
    return train_p.astype(np.float32), sample_p.astype(np.float32)


def chronological_frame(train: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    train_panel, sample_panel = add_panel_features(train, sample)
    train_rows = train[KEY_COLUMNS].copy()
    sample_rows = sample[KEY_COLUMNS].copy()
    train_rows["_split"] = "train"
    sample_rows["_split"] = "sample"
    train_rows["_row"] = np.arange(len(train))
    sample_rows["_row"] = np.arange(len(sample))
    all_rows = pd.concat([train_rows, sample_rows], ignore_index=True)
    panel = pd.concat(
        [
            train_panel[["panel_index", "panel_position", "weekday_sin", "weekday_cos"]],
            sample_panel[["panel_index", "panel_position", "weekday_sin", "weekday_cos"]],
        ],
        ignore_index=True,
    )
    all_rows[["panel_index", "panel_position", "weekday_sin", "weekday_cos"]] = panel
    return all_rows.sort_values(["subject_id", "lifelog_date", "sleep_date"]).reset_index(drop=True)


def temporal_deviation_features(
    all_rows: pd.DataFrame,
    feature_all: np.ndarray,
    groups: dict[str, list[int]],
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    rows = []
    names: list[str] = []
    for group_name in groups:
        if group_name == "all":
            continue
        for window in [7, 14, 28]:
            for metric in ["mean_abs", "l2", "cosine", "max_abs"]:
                names.append(f"td_{group_name}_w{window}_{metric}")
        names.extend([f"td_{group_name}_prev1_l2", f"td_{group_name}_prev3_l2"])

    out = np.zeros((len(all_rows), len(names)), dtype=np.float32)
    name_pos = {name: i for i, name in enumerate(names)}
    for _, subject_rows in all_rows.groupby("subject_id", sort=False):
        idx = subject_rows.index.to_numpy(dtype=int)
        for local_pos, row_idx in enumerate(idx):
            for group_name, group_idx in groups.items():
                if group_name == "all":
                    continue
                cur = feature_all[row_idx, group_idx]
                for window in [7, 14, 28]:
                    lo = max(0, local_pos - window)
                    prev_idx = idx[lo:local_pos]
                    if len(prev_idx) == 0:
                        prev = np.zeros_like(cur)
                    else:
                        prev = feature_all[prev_idx][:, group_idx].mean(axis=0)
                    diff = cur - prev
                    denom = (np.linalg.norm(cur) * np.linalg.norm(prev)) + 1e-8
                    cosine = 1.0 - float(np.dot(cur, prev) / denom) if len(prev) else 0.0
                    values = {
                        "mean_abs": float(np.mean(np.abs(diff))),
                        "l2": float(np.linalg.norm(diff) / np.sqrt(max(len(diff), 1))),
                        "cosine": cosine,
                        "max_abs": float(np.max(np.abs(diff))) if len(diff) else 0.0,
                    }
                    for metric, value in values.items():
                        out[row_idx, name_pos[f"td_{group_name}_w{window}_{metric}"]] = value

                prev1_idx = idx[max(0, local_pos - 1) : local_pos]
                prev3_idx = idx[max(0, local_pos - 3) : local_pos]
                prev1 = feature_all[prev1_idx][:, group_idx].mean(axis=0) if len(prev1_idx) else np.zeros_like(cur)
                prev3 = feature_all[prev3_idx][:, group_idx].mean(axis=0) if len(prev3_idx) else np.zeros_like(cur)
                out[row_idx, name_pos[f"td_{group_name}_prev1_l2"]] = float(
                    np.linalg.norm(cur - prev1) / np.sqrt(max(len(cur), 1))
                )
                out[row_idx, name_pos[f"td_{group_name}_prev3_l2"]] = float(
                    np.linalg.norm(cur - prev3) / np.sqrt(max(len(cur), 1))
                )

    train_mask = all_rows["_split"].eq("train").to_numpy()
    sample_mask = all_rows["_split"].eq("sample").to_numpy()
    train_order = all_rows.loc[train_mask].sort_values("_row").index.to_numpy(dtype=int)
    sample_order = all_rows.loc[sample_mask].sort_values("_row").index.to_numpy(dtype=int)
    return out[train_order], out[sample_order], names


def rbf_topk_label_average(
    query: np.ndarray,
    cand_x: np.ndarray,
    cand_y: np.ndarray,
    k: int,
    fallback: np.ndarray,
) -> tuple[np.ndarray, float]:
    if len(cand_x) == 0:
        return fallback.copy(), 0.0
    diff = cand_x - query[None, :]
    dist = np.sqrt(np.mean(diff * diff, axis=1))
    k = min(k, len(dist))
    top = np.argpartition(dist, k - 1)[:k]
    top_dist = dist[top]
    bandwidth = float(np.median(top_dist) + 1e-6)
    weights = np.exp(-top_dist / bandwidth)
    if weights.sum() <= 0:
        weights = np.ones_like(weights)
    pred = np.average(cand_y[top], axis=0, weights=weights)
    return np.clip(pred, EPS, 1.0 - EPS), float(weights.max() / weights.sum())


def retrieval_features(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    feature_train: np.ndarray,
    feature_sample: np.ndarray,
    groups: dict[str, list[int]],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray, list[str], np.ndarray, np.ndarray]:
    y = train[TARGET_COLUMNS].to_numpy(dtype=float)
    subjects_train = train["subject_id"].to_numpy()
    subjects_sample = sample["subject_id"].to_numpy()
    dates_train = pd.to_datetime(train["lifelog_date"]).to_numpy()
    dates_sample = pd.to_datetime(sample["lifelog_date"]).to_numpy()
    use_groups = [name for name in ["sleep", "mobility", "phone", "physiology", "all"] if name in groups]
    modes = ["same_past", "cross_norm"]
    names = []
    for group_name in use_groups:
        for mode in modes:
            for target in TARGET_COLUMNS:
                names.append(f"retr_{group_name}_{mode}_{target}")
            names.append(f"retr_{group_name}_{mode}_top_weight")
    train_feat = np.zeros((len(train), len(names)), dtype=np.float32)
    sample_feat = np.zeros((len(sample), len(names)), dtype=np.float32)
    name_pos = {name: i for i, name in enumerate(names)}
    retrieval_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=np.float32)
    retrieval_test_parts = []

    for fold_train_idx, val_idx in folds:
        fallback = np.clip(y[fold_train_idx].mean(axis=0), EPS, 1.0 - EPS)
        fold_retrieval_accum = np.zeros((len(val_idx), len(TARGET_COLUMNS)), dtype=float)
        fold_retrieval_count = 0
        for group_name in use_groups:
            idx_cols = groups[group_name]
            x_train_group = feature_train[:, idx_cols]
            for local_i, row_idx in enumerate(val_idx):
                subject = subjects_train[row_idx]
                date = dates_train[row_idx]
                same_mask = (
                    np.isin(np.arange(len(train)), fold_train_idx)
                    & (subjects_train == subject)
                    & (dates_train < date)
                )
                cross_mask = np.isin(np.arange(len(train)), fold_train_idx) & (subjects_train != subject)
                specs = [("same_past", same_mask, 5), ("cross_norm", cross_mask, 12)]
                for mode, mask, k in specs:
                    pred, weight = rbf_topk_label_average(
                        x_train_group[row_idx],
                        x_train_group[mask],
                        y[mask],
                        k,
                        fallback,
                    )
                    for target_i, target in enumerate(TARGET_COLUMNS):
                        train_feat[row_idx, name_pos[f"retr_{group_name}_{mode}_{target}"]] = pred[target_i]
                    train_feat[row_idx, name_pos[f"retr_{group_name}_{mode}_top_weight"]] = weight
                    fold_retrieval_accum[local_i] += pred
                    fold_retrieval_count += 1
        retrieval_oof[val_idx] = np.clip(fold_retrieval_accum / max(fold_retrieval_count / len(val_idx), 1), EPS, 1.0 - EPS)

    full_fallback = np.clip(y.mean(axis=0), EPS, 1.0 - EPS)
    retrieval_test = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    retrieval_test_count = 0
    for group_name in use_groups:
        idx_cols = groups[group_name]
        x_train_group = feature_train[:, idx_cols]
        x_sample_group = feature_sample[:, idx_cols]
        for row_idx in range(len(sample)):
            subject = subjects_sample[row_idx]
            date = dates_sample[row_idx]
            same_mask = (subjects_train == subject) & (dates_train < date)
            cross_mask = subjects_train != subject
            specs = [("same_past", same_mask, 5), ("cross_norm", cross_mask, 12)]
            for mode, mask, k in specs:
                pred, weight = rbf_topk_label_average(
                    x_sample_group[row_idx],
                    x_train_group[mask],
                    y[mask],
                    k,
                    full_fallback,
                )
                for target_i, target in enumerate(TARGET_COLUMNS):
                    sample_feat[row_idx, name_pos[f"retr_{group_name}_{mode}_{target}"]] = pred[target_i]
                sample_feat[row_idx, name_pos[f"retr_{group_name}_{mode}_top_weight"]] = weight
                retrieval_test[row_idx] += pred
                retrieval_test_count += 1
    retrieval_test = np.clip(retrieval_test / max(retrieval_test_count / len(sample), 1), EPS, 1.0 - EPS)
    return train_feat, sample_feat, names, retrieval_oof, retrieval_test


def prototype_features(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    feature_train: np.ndarray,
    feature_sample: np.ndarray,
    groups: dict[str, list[int]],
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> tuple[np.ndarray, np.ndarray, list[str], np.ndarray, np.ndarray]:
    y = train[TARGET_COLUMNS].to_numpy(dtype=float)
    subjects = sorted(train["subject_id"].unique().tolist())
    subject_to_i = {subject: i for i, subject in enumerate(subjects)}
    train_subjects = train["subject_id"].to_numpy()
    sample_subjects = sample["subject_id"].to_numpy()
    use_groups = [name for name in ["sleep", "mobility", "phone", "physiology", "all"] if name in groups]
    names = []
    for group_name in use_groups:
        for subject in subjects:
            names.append(f"proto_{group_name}_w_{subject}")
        for target in TARGET_COLUMNS:
            names.append(f"proto_{group_name}_pred_{target}")
    train_feat = np.zeros((len(train), len(names)), dtype=np.float32)
    sample_feat = np.zeros((len(sample), len(names)), dtype=np.float32)
    name_pos = {name: i for i, name in enumerate(names)}
    proto_oof = np.zeros((len(train), len(TARGET_COLUMNS)), dtype=np.float32)

    def compute_fold(row_x: np.ndarray, group_idx: list[int], train_idx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        prototypes = []
        priors = []
        global_prior = np.clip(y[train_idx].mean(axis=0), EPS, 1.0 - EPS)
        for subject in subjects:
            mask = train_idx[train_subjects[train_idx] == subject]
            if len(mask) == 0:
                prototypes.append(np.zeros(len(group_idx), dtype=float))
                priors.append(global_prior)
            else:
                prototypes.append(feature_train[mask][:, group_idx].mean(axis=0))
                priors.append(np.clip(y[mask].mean(axis=0), EPS, 1.0 - EPS))
        proto = np.vstack(prototypes)
        prior = np.vstack(priors)
        dist = np.sqrt(np.mean((proto - row_x[group_idx][None, :]) ** 2, axis=1))
        temp = float(np.median(dist) + 1e-6)
        weights = np.exp(-dist / temp)
        weights = weights / max(weights.sum(), 1e-12)
        pred = weights @ prior
        return weights, np.clip(pred, EPS, 1.0 - EPS)

    for fold_train_idx, val_idx in folds:
        accum = np.zeros((len(val_idx), len(TARGET_COLUMNS)), dtype=float)
        for group_name in use_groups:
            group_idx = groups[group_name]
            for local_i, row_idx in enumerate(val_idx):
                weights, pred = compute_fold(feature_train[row_idx], group_idx, fold_train_idx)
                for subject, weight in zip(subjects, weights):
                    train_feat[row_idx, name_pos[f"proto_{group_name}_w_{subject}"]] = weight
                for target_i, target in enumerate(TARGET_COLUMNS):
                    train_feat[row_idx, name_pos[f"proto_{group_name}_pred_{target}"]] = pred[target_i]
                accum[local_i] += pred
        proto_oof[val_idx] = np.clip(accum / len(use_groups), EPS, 1.0 - EPS)

    full_idx = np.arange(len(train), dtype=int)
    proto_test = np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=float)
    for group_name in use_groups:
        group_idx = groups[group_name]
        for row_idx in range(len(sample)):
            weights, pred = compute_fold(feature_sample[row_idx], group_idx, full_idx)
            for subject, weight in zip(subjects, weights):
                sample_feat[row_idx, name_pos[f"proto_{group_name}_w_{subject}"]] = weight
            for target_i, target in enumerate(TARGET_COLUMNS):
                sample_feat[row_idx, name_pos[f"proto_{group_name}_pred_{target}"]] = pred[target_i]
            proto_test[row_idx] += pred
    proto_test = np.clip(proto_test / len(use_groups), EPS, 1.0 - EPS)
    return train_feat, sample_feat, names, proto_oof, proto_test


def anchor_features(pred_bank: np.ndarray, target_i: int) -> np.ndarray:
    logits = logit(pred_bank)
    same_l = logits[:, :, target_i]
    same_p = pred_bank[:, :, target_i]
    all_mean = logits.mean(axis=1)
    return np.column_stack(
        [
            same_l,
            same_p,
            same_l.mean(axis=1),
            same_l.std(axis=1),
            same_l.min(axis=1),
            same_l.max(axis=1),
            same_p.mean(axis=1),
            same_p.std(axis=1),
            all_mean,
        ]
    )


def fit_lgbm(x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray, seed: int) -> np.ndarray:
    if len(np.unique(y_train)) < 2:
        return np.full(len(x_eval), float(y_train[0]), dtype=float)
    model = LGBMClassifier(
        n_estimators=550,
        learning_rate=0.025,
        num_leaves=15,
        max_depth=4,
        min_child_samples=7,
        subsample=0.85,
        colsample_bytree=0.70,
        reg_alpha=0.05,
        reg_lambda=2.0,
        objective="binary",
        random_state=seed,
        verbosity=-1,
    )
    model.fit(x_train, y_train)
    return model.predict_proba(x_eval)[:, 1]


def fit_xgb(x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray, seed: int) -> np.ndarray:
    if len(np.unique(y_train)) < 2:
        return np.full(len(x_eval), float(y_train[0]), dtype=float)
    model = XGBClassifier(
        n_estimators=420,
        learning_rate=0.025,
        max_depth=2,
        min_child_weight=2.0,
        subsample=0.85,
        colsample_bytree=0.75,
        reg_lambda=4.0,
        reg_alpha=0.1,
        objective="binary:logistic",
        eval_metric="logloss",
        tree_method="hist",
        random_state=seed,
        verbosity=0,
    )
    model.fit(x_train, y_train)
    return model.predict_proba(x_eval)[:, 1]


def fit_meta_models(
    train: pd.DataFrame,
    sample: pd.DataFrame,
    pred_bank: np.ndarray,
    sub_bank: np.ndarray,
    common_train: np.ndarray,
    common_sample: np.ndarray,
    folds: list[tuple[np.ndarray, np.ndarray]],
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    y = train[TARGET_COLUMNS].to_numpy(dtype=int)
    outputs = {
        "lgbm_temporal_retrieval_prototype_meta": (
            np.zeros((len(train), len(TARGET_COLUMNS)), dtype=np.float32),
            np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=np.float32),
        ),
        "xgb_temporal_retrieval_prototype_meta": (
            np.zeros((len(train), len(TARGET_COLUMNS)), dtype=np.float32),
            np.zeros((len(sample), len(TARGET_COLUMNS)), dtype=np.float32),
        ),
    }
    for target_i, target in enumerate(TARGET_COLUMNS):
        x_anchor = anchor_features(pred_bank, target_i)
        x_anchor_test = anchor_features(sub_bank, target_i)
        x_all = np.column_stack([x_anchor, common_train]).astype(np.float32)
        x_test = np.column_stack([x_anchor_test, common_sample]).astype(np.float32)
        lgb_oof, lgb_test = outputs["lgbm_temporal_retrieval_prototype_meta"]
        xgb_oof, xgb_test = outputs["xgb_temporal_retrieval_prototype_meta"]
        test_lgb_parts = []
        test_xgb_parts = []
        for fold_i, (train_idx, val_idx) in enumerate(folds):
            lgb_oof[val_idx, target_i] = fit_lgbm(x_all[train_idx], y[train_idx, target_i], x_all[val_idx], SEED + fold_i)
            xgb_oof[val_idx, target_i] = fit_xgb(x_all[train_idx], y[train_idx, target_i], x_all[val_idx], SEED + 100 + fold_i)
        for seed_offset in [0, 1, 2]:
            test_lgb_parts.append(fit_lgbm(x_all, y[:, target_i], x_test, SEED + 10 * seed_offset + target_i))
            test_xgb_parts.append(fit_xgb(x_all, y[:, target_i], x_test, SEED + 200 + 10 * seed_offset + target_i))
        lgb_test[:, target_i] = np.mean(test_lgb_parts, axis=0)
        xgb_test[:, target_i] = np.mean(test_xgb_parts, axis=0)
    return {
        name: (np.clip(oof, EPS, 1.0 - EPS), np.clip(test, EPS, 1.0 - EPS))
        for name, (oof, test) in outputs.items()
    }


def avg_logloss(y: pd.DataFrame, pred: np.ndarray, weights: np.ndarray | None = None) -> float:
    scores = []
    for target_i, target in enumerate(TARGET_COLUMNS):
        scores.append(
            float(
                log_loss(
                    y[target].to_numpy(),
                    np.clip(pred[:, target_i], EPS, 1.0 - EPS),
                    labels=[0, 1],
                    sample_weight=weights,
                )
            )
        )
    return float(np.mean(scores))


def sample_position_weights(train: pd.DataFrame, sample: pd.DataFrame) -> np.ndarray:
    train_panel, sample_panel = add_panel_features(train, sample)
    bins = np.asarray([0.0, 1 / 3, 2 / 3, 0.8, 1.000001])
    train_bin = np.digitize(train_panel["panel_position"].to_numpy(float), bins) - 1
    sample_bin = np.digitize(sample_panel["panel_position"].to_numpy(float), bins) - 1
    train_frac = np.bincount(train_bin, minlength=len(bins) - 1).astype(float) / len(train_bin)
    sample_frac = np.bincount(sample_bin, minlength=len(bins) - 1).astype(float) / len(sample_bin)
    ratio = np.divide(sample_frac, train_frac, out=np.zeros_like(train_frac), where=train_frac > 0)
    weights = ratio[train_bin]
    return weights / weights.mean()


def submission_stats(pred: np.ndarray) -> dict[str, float]:
    values = np.clip(pred, EPS, 1.0 - EPS)
    return {
        "sub_min": float(values.min()),
        "sub_p01": float(np.quantile(values, 0.01)),
        "sub_p05": float(np.quantile(values, 0.05)),
        "sub_mean": float(values.mean()),
        "sub_p95": float(np.quantile(values, 0.95)),
        "sub_p99": float(np.quantile(values, 0.99)),
        "sub_max": float(values.max()),
        "sub_abs_logit_mean": float(np.abs(logit(values)).mean()),
        "sub_extreme_005_995": float(((values < 0.005) | (values > 0.995)).mean()),
    }


def write_prediction_files(
    output_dir: Path,
    name: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    oof: np.ndarray,
    submission: np.ndarray,
) -> tuple[Path, Path]:
    oof_frame = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    sub_frame = sample[KEY_COLUMNS].copy()
    for target_i, target in enumerate(TARGET_COLUMNS):
        oof_frame[f"pred_{target}"] = np.clip(oof[:, target_i], EPS, 1.0 - EPS)
        sub_frame[target] = np.clip(submission[:, target_i], EPS, 1.0 - EPS)
    oof_path = output_dir / f"oof_{name}.csv"
    sub_path = output_dir / f"submission_{name}.csv"
    oof_frame.to_csv(oof_path, index=False)
    sub_frame.to_csv(sub_path, index=False)
    return oof_path, sub_path


def targetwise_best(base: np.ndarray, candidates: dict[str, tuple[np.ndarray, np.ndarray]], y: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    best_oof = base.copy()
    best_sub = None
    rows = []
    base_score_by_target = [
        log_loss(y[target], np.clip(base[:, i], EPS, 1.0 - EPS), labels=[0, 1]) for i, target in enumerate(TARGET_COLUMNS)
    ]
    for i, target in enumerate(TARGET_COLUMNS):
        best_name = "base_recovery15"
        best_score = base_score_by_target[i]
        for name, (oof, sub) in candidates.items():
            score = log_loss(y[target], np.clip(oof[:, i], EPS, 1.0 - EPS), labels=[0, 1])
            if score < best_score:
                best_score = score
                best_name = name
        rows.append({"target": target, "selected": best_name, "score": float(best_score), "base_score": float(base_score_by_target[i])})
    return best_oof, best_sub, rows


def main() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    output_dir = Path("outputs/temporal_retrieval_prototype_meta")
    output_dir.mkdir(parents=True, exist_ok=True)

    train = normalize_keys(pd.read_csv("data/ch2026_metrics_train.csv"))
    sample = normalize_keys(pd.read_csv("data/ch2026_submission_sample.csv"))
    folds = make_subject_time_folds(train)
    weights = sample_position_weights(train, sample)
    y = train[TARGET_COLUMNS]

    anchor_names, pred_bank, sub_bank = load_prediction_bank(train, sample)
    master_train_df, master_sample_df, master_cols = load_master_matrix(train, sample)
    latent_train_df, latent_sample_df, latent_cols = merge_latents(train, sample)
    raw_train_df = pd.concat([master_train_df, latent_train_df], axis=1)
    raw_sample_df = pd.concat([master_sample_df, latent_sample_df], axis=1)
    raw_cols = master_cols + latent_cols
    feature_train, feature_sample = fit_numeric_transform(raw_train_df, raw_sample_df)
    groups = feature_groups(raw_cols)
    all_rows = chronological_frame(train, sample)
    feature_all = np.vstack([feature_train, feature_sample])
    # chronological_frame preserves train rows followed by sample rows through _row, so build aligned feature matrix.
    aligned_all = np.zeros((len(all_rows), feature_all.shape[1]), dtype=np.float32)
    for pos, row in all_rows.iterrows():
        source_offset = int(row["_row"]) if row["_split"] == "train" else len(train) + int(row["_row"])
        aligned_all[pos] = feature_all[source_offset]

    td_train, td_sample, td_names = temporal_deviation_features(all_rows, aligned_all, groups)
    retr_train, retr_sample, retr_names, retr_oof, retr_test = retrieval_features(
        train, sample, feature_train, feature_sample, groups, folds
    )
    proto_train, proto_sample, proto_names, proto_oof, proto_test = prototype_features(
        train, sample, feature_train, feature_sample, groups, folds
    )
    pca_train, pca_sample = pca_features([feature_train], [feature_sample], n_components=32)
    panel_train, panel_sample = add_panel_features(train, sample)
    subject_train = pd.get_dummies(train["subject_id"], prefix="subject", dtype=float)
    subject_sample = pd.get_dummies(sample["subject_id"], prefix="subject", dtype=float).reindex(columns=subject_train.columns, fill_value=0.0)
    panel_cols = ["panel_index", "panel_position", "weekday_sin", "weekday_cos"]
    common_train = np.column_stack(
        [
            td_train,
            retr_train,
            proto_train,
            logit(retr_oof),
            logit(proto_oof),
            pca_train,
            panel_train[panel_cols].to_numpy(float),
            subject_train.to_numpy(float),
        ]
    ).astype(np.float32)
    common_sample = np.column_stack(
        [
            td_sample,
            retr_sample,
            proto_sample,
            logit(retr_test),
            logit(proto_test),
            pca_sample,
            panel_sample[panel_cols].to_numpy(float),
            subject_sample.to_numpy(float),
        ]
    ).astype(np.float32)

    feature_manifest = {
        "anchor_names": anchor_names,
        "master_feature_count": len(master_cols),
        "latent_feature_count": len(latent_cols),
        "temporal_deviation_features": td_names,
        "retrieval_features": retr_names,
        "prototype_features": proto_names,
        "groups": {name: [raw_cols[i] for i in idx[:20]] for name, idx in groups.items()},
        "common_feature_shape": {"train": list(common_train.shape), "sample": list(common_sample.shape)},
    }
    (output_dir / "feature_manifest.json").write_text(json.dumps(feature_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(td_train, columns=td_names).assign(**train[KEY_COLUMNS]).to_parquet(output_dir / "temporal_deviation_train.parquet", index=False)
    pd.DataFrame(retr_train, columns=retr_names).assign(**train[KEY_COLUMNS]).to_parquet(output_dir / "retrieval_train.parquet", index=False)
    pd.DataFrame(proto_train, columns=proto_names).assign(**train[KEY_COLUMNS]).to_parquet(output_dir / "prototype_train.parquet", index=False)

    model_outputs = fit_meta_models(train, sample, pred_bank, sub_bank, common_train, common_sample, folds)
    model_outputs["retrieval_source"] = (retr_oof, retr_test)
    model_outputs["prototype_source"] = (proto_oof, proto_test)
    lgb_oof, lgb_test = model_outputs["lgbm_temporal_retrieval_prototype_meta"]
    xgb_oof, xgb_test = model_outputs["xgb_temporal_retrieval_prototype_meta"]
    model_outputs["lgbm_xgb_7030_meta"] = (
        np.clip(0.7 * lgb_oof + 0.3 * xgb_oof, EPS, 1.0 - EPS),
        np.clip(0.7 * lgb_test + 0.3 * xgb_test, EPS, 1.0 - EPS),
    )
    model_outputs["lgbm_xgb_5050_meta"] = (
        np.clip(0.5 * lgb_oof + 0.5 * xgb_oof, EPS, 1.0 - EPS),
        np.clip(0.5 * lgb_test + 0.5 * xgb_test, EPS, 1.0 - EPS),
    )

    recovery_idx = anchor_names.index("recovery15") if "recovery15" in anchor_names else 0
    recovery_oof = pred_bank[:, recovery_idx, :]
    recovery_test = sub_bank[:, recovery_idx, :]
    for alpha in [0.35, 0.50, 0.70]:
        for base_name in ["lgbm_xgb_7030_meta", "lgbm_xgb_5050_meta"]:
            oof, test = model_outputs[base_name]
            name = f"{base_name}_logitblend_recovery15_a{alpha:.2f}".replace(".", "p")
            model_outputs[name] = (
                sigmoid((1.0 - alpha) * logit(recovery_oof) + alpha * logit(oof)),
                sigmoid((1.0 - alpha) * logit(recovery_test) + alpha * logit(test)),
            )

    rows = []
    for name, (oof, submission) in model_outputs.items():
        oof_path, sub_path = write_prediction_files(output_dir, name, train, sample, oof, submission)
        rows.append(
            {
                "name": name,
                "uniform_oof_cv": avg_logloss(y, oof),
                "sample_weighted_oof_cv": avg_logloss(y, oof, weights),
                "oof_path": str(oof_path),
                "submission_path": str(sub_path),
                **submission_stats(submission),
            }
        )
    report = pd.DataFrame(rows).sort_values(["uniform_oof_cv", "sample_weighted_oof_cv"]).reset_index(drop=True)
    report.to_csv(output_dir / "meta_experiment_report.csv", index=False)
    (output_dir / "meta_experiment_report.json").write_text(
        json.dumps(report.to_dict(orient="records"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
