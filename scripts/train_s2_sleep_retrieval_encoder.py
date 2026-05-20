from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EPS = 1e-5
SEED = 2026


@dataclass(frozen=True)
class FoldPack:
    train_idx: np.ndarray
    val_idx: np.ndarray


@dataclass(frozen=True)
class SourceResult:
    name: str
    oof_pred: np.ndarray
    sample_pred: np.ndarray
    score: float


def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in KEY_COLUMNS:
        out[col] = out[col].astype(str)
    return out


def safe_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values, EPS, 1.0 - EPS)
    return np.log(values / (1.0 - values))


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -50.0, 50.0)))


def target_loss(y: np.ndarray, pred: np.ndarray) -> float:
    return float(log_loss(y.astype(int), np.clip(pred, EPS, 1.0 - EPS), labels=[0, 1]))


def make_subject_time_folds(frame: pd.DataFrame, n_folds: int) -> list[FoldPack]:
    ordered = frame.reset_index(names="_idx").sort_values(["subject_id", "lifelog_date", "sleep_date"])
    val_parts: list[list[int]] = [[] for _ in range(n_folds)]
    for _, group in ordered.groupby("subject_id", sort=False):
        chunks = np.array_split(group["_idx"].to_numpy(int), n_folds)
        for fold, chunk in enumerate(chunks):
            val_parts[fold].extend(chunk.tolist())
    all_idx = np.arange(len(frame), dtype=int)
    packs = []
    for part in val_parts:
        val_idx = np.array(sorted(part), dtype=int)
        packs.append(FoldPack(train_idx=np.setdiff1d(all_idx, val_idx), val_idx=val_idx))
    return packs


def load_base_predictions(train: pd.DataFrame, sample: pd.DataFrame, base_oof: Path, base_submission: Path) -> tuple[np.ndarray, np.ndarray]:
    oof = normalize_keys(pd.read_csv(base_oof))
    submission = normalize_keys(pd.read_csv(base_submission))
    if not oof[KEY_COLUMNS].equals(train[KEY_COLUMNS]):
        raise ValueError("Base OOF keys do not match train keys.")
    if not submission[KEY_COLUMNS].equals(sample[KEY_COLUMNS]):
        raise ValueError("Base submission keys do not match sample keys.")
    base_train = np.clip(np.column_stack([oof[f"pred_{target}"].to_numpy(float) for target in TARGET_COLUMNS]), EPS, 1 - EPS)
    base_sample = np.clip(submission[TARGET_COLUMNS].to_numpy(float), EPS, 1 - EPS)
    return base_train, base_sample


def signed_log1p(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.astype(float).copy()
    for col in out.columns:
        values = out[col].to_numpy(float)
        finite = values[np.isfinite(values)]
        if len(finite) and np.nanpercentile(np.abs(finite), 95) > 1000:
            out[col] = np.sign(values) * np.log1p(np.abs(values))
    out = out.replace([np.inf, -np.inf], np.nan)
    return out


def columns_matching(columns: list[str], any_tokens: list[str], all_tokens: list[str] | None = None) -> list[str]:
    all_tokens = all_tokens or []
    selected = []
    for col in columns:
        lower = col.lower()
        if any(token in lower for token in any_tokens) and all(token in lower for token in all_tokens):
            selected.append(col)
    return selected


def row_digest(frame: pd.DataFrame, columns: list[str], prefix: str) -> pd.DataFrame:
    if not columns:
        return pd.DataFrame(index=frame.index)
    values = frame[columns].to_numpy(float)
    finite = np.isfinite(values)
    valid_count = finite.sum(axis=1).astype(float)
    safe = np.where(finite, values, np.nan)
    abs_safe = np.abs(safe)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = pd.DataFrame(
            {
                f"{prefix}mean": np.nanmean(safe, axis=1),
                f"{prefix}std": np.nanstd(safe, axis=1),
                f"{prefix}abs_mean": np.nanmean(abs_safe, axis=1),
                f"{prefix}p90": np.nanpercentile(safe, 90, axis=1),
                f"{prefix}max": np.nanmax(safe, axis=1),
                f"{prefix}coverage": valid_count / max(1, len(columns)),
            },
            index=frame.index,
        )
    return out.replace([np.inf, -np.inf], np.nan)


def add_temporal_deviation_features(digest: pd.DataFrame, keys: pd.DataFrame) -> pd.DataFrame:
    temporal_cols = [col for col in digest.columns if col.startswith("eng__")]
    if not temporal_cols:
        return pd.DataFrame(index=digest.index)
    ordered = pd.concat(
        [
            keys[KEY_COLUMNS].reset_index(drop=True),
            digest[temporal_cols].reset_index(drop=True),
        ],
        axis=1,
    )
    ordered["_orig_idx"] = np.arange(len(ordered))
    ordered["_date"] = pd.to_datetime(ordered["lifelog_date"])
    ordered = ordered.sort_values(["subject_id", "_date", "sleep_date"]).reset_index(drop=True)
    temporal_parts: list[pd.DataFrame] = []
    current = ordered[temporal_cols]
    grouped = ordered.groupby("subject_id", sort=False)

    prev = grouped[temporal_cols].shift(1)
    prev2 = grouped[temporal_cols].shift(2)
    prev_delta = current - prev
    temporal_parts.append(prev_delta.add_prefix("tmp__prev1_delta__"))
    temporal_parts.append(prev_delta.abs().add_prefix("tmp__prev1_abs_delta__"))
    prev2_delta = current - prev2
    acceleration = current - (2.0 * prev) + prev2
    temporal_parts.append(prev2_delta.add_prefix("tmp__prev2_delta__"))
    temporal_parts.append(prev2_delta.abs().add_prefix("tmp__prev2_abs_delta__"))
    temporal_parts.append(acceleration.add_prefix("tmp__accel__"))
    temporal_parts.append(acceleration.abs().add_prefix("tmp__accel_abs__"))

    roll_means: dict[int, pd.DataFrame] = {}
    roll_stds: dict[int, pd.DataFrame] = {}
    roll_z: dict[int, pd.DataFrame] = {}

    for window in (3, 7):
        roll_mean = grouped[temporal_cols].transform(
            lambda values: values.shift(1).rolling(window=window, min_periods=1).mean()
        )
        roll_means[window] = roll_mean
        roll_std = grouped[temporal_cols].transform(
            lambda values: values.shift(1).rolling(window=window, min_periods=2).std()
        )
        roll_stds[window] = roll_std
        delta = current - roll_mean
        z = delta / roll_std.replace(0, np.nan)
        roll_z[window] = z
        temporal_parts.append(delta.add_prefix(f"tmp__roll{window}_delta__"))
        temporal_parts.append(delta.abs().add_prefix(f"tmp__roll{window}_abs_delta__"))
        temporal_parts.append(z.add_prefix(f"tmp__roll{window}_z__"))

    if 7 in roll_z:
        abs_z7 = roll_z[7].abs()
        pos_z7 = roll_z[7].clip(lower=0.0)
        neg_z7 = (-roll_z[7]).clip(lower=0.0)
        shock_gt1 = (abs_z7 > 1.0).astype(float).where(abs_z7.notna())
        shock_gt15 = (abs_z7 > 1.5).astype(float).where(abs_z7.notna())
        temporal_parts.append(shock_gt1.add_prefix("tmp__shock_gt1_roll7__"))
        temporal_parts.append(shock_gt15.add_prefix("tmp__shock_gt15_roll7__"))
        for window in (3, 7):
            burden = abs_z7.groupby(ordered["subject_id"], sort=False).transform(
                lambda values: values.rolling(window=window, min_periods=1).sum()
            )
            pos_burden = pos_z7.groupby(ordered["subject_id"], sort=False).transform(
                lambda values: values.rolling(window=window, min_periods=1).sum()
            )
            neg_burden = neg_z7.groupby(ordered["subject_id"], sort=False).transform(
                lambda values: values.rolling(window=window, min_periods=1).sum()
            )
            shock_count = shock_gt1.groupby(ordered["subject_id"], sort=False).transform(
                lambda values: values.rolling(window=window, min_periods=1).sum()
            )
            temporal_parts.append(burden.add_prefix(f"tmp__burden_absz7_roll{window}__"))
            temporal_parts.append(pos_burden.add_prefix(f"tmp__signed_burden_posz7_roll{window}__"))
            temporal_parts.append(neg_burden.add_prefix(f"tmp__signed_burden_negz7_roll{window}__"))
            temporal_parts.append((pos_burden - neg_burden).add_prefix(f"tmp__signed_burden_balance_roll{window}__"))
            temporal_parts.append(shock_count.add_prefix(f"tmp__shock_count_gt1_roll{window}__"))

        for alpha_name, alpha in (("a03", 0.3), ("a06", 0.6)):
            ema_abs = abs_z7.groupby(ordered["subject_id"], sort=False).transform(
                lambda values: values.ewm(alpha=alpha, adjust=False, min_periods=1).mean()
            )
            ema_pos = pos_z7.groupby(ordered["subject_id"], sort=False).transform(
                lambda values: values.ewm(alpha=alpha, adjust=False, min_periods=1).mean()
            )
            ema_neg = neg_z7.groupby(ordered["subject_id"], sort=False).transform(
                lambda values: values.ewm(alpha=alpha, adjust=False, min_periods=1).mean()
            )
            temporal_parts.append(ema_abs.add_prefix(f"tmp__decay_absz7_{alpha_name}__"))
            temporal_parts.append(ema_pos.add_prefix(f"tmp__decay_posz7_{alpha_name}__"))
            temporal_parts.append(ema_neg.add_prefix(f"tmp__decay_negz7_{alpha_name}__"))

        for threshold, shock_frame in (("gt1", shock_gt1), ("gt15", shock_gt15)):
            streak_values = np.full((len(ordered), len(temporal_cols)), np.nan, dtype=np.float32)
            age_values = np.full((len(ordered), len(temporal_cols)), np.nan, dtype=np.float32)
            for _, group in ordered.groupby("subject_id", sort=False):
                row_pos = group.index.to_numpy()
                values = shock_frame.loc[row_pos, temporal_cols].to_numpy(float)
                streak = np.zeros(values.shape[1], dtype=np.float32)
                age = np.full(values.shape[1], np.nan, dtype=np.float32)
                for local_i, global_i in enumerate(row_pos):
                    row = values[local_i]
                    finite = np.isfinite(row)
                    active = finite & (row > 0.5)
                    streak[active] += 1.0
                    streak[finite & ~active] = 0.0
                    streak[~finite] = np.nan
                    age[finite] = np.where(np.isnan(age[finite]), np.nan, age[finite] + 1.0)
                    age[active] = 0.0
                    age[~finite] = np.nan
                    streak_values[global_i] = streak
                    age_values[global_i] = age
                    streak = np.nan_to_num(streak, nan=0.0)
                    age = np.where(np.isfinite(age), age, np.nan)
            streak_frame = pd.DataFrame(streak_values, columns=temporal_cols, index=ordered.index)
            age_frame = pd.DataFrame(age_values, columns=temporal_cols, index=ordered.index)
            temporal_parts.append(streak_frame.add_prefix(f"tmp__shock_streak_{threshold}_roll7__"))
            temporal_parts.append(age_frame.add_prefix(f"tmp__shock_age_{threshold}_roll7__"))

        sync_specs = {
            "phone": ["eng__phone"],
            "social": ["eng__social"],
            "body": ["eng__physio", "eng__body"],
            "mobility": ["eng__mobility"],
            "volatility": ["eng__volatility"],
            "missing": ["eng__coverage_missing"],
            "sleep": ["eng__sleep_proxy"],
        }

        def sync_columns(tokens: list[str]) -> list[str]:
            return [col for col in temporal_cols if any(token in col for token in tokens)]

        sync_parts = {}
        for name, tokens in sync_specs.items():
            cols = sync_columns(tokens)
            if not cols:
                continue
            sync_parts[f"tmp__sync_absz7__{name}"] = abs_z7[cols].mean(axis=1)
            sync_parts[f"tmp__sync_posz7__{name}"] = pos_z7[cols].mean(axis=1)
            sync_parts[f"tmp__sync_negz7__{name}"] = neg_z7[cols].mean(axis=1)
            sync_parts[f"tmp__sync_shockrate__{name}"] = shock_gt1[cols].mean(axis=1)

        sync_frame = pd.DataFrame(sync_parts, index=ordered.index).replace([np.inf, -np.inf], np.nan)
        if not sync_frame.empty:
            abs_cols = [col for col in sync_frame.columns if col.startswith("tmp__sync_absz7__")]
            shock_cols = [col for col in sync_frame.columns if col.startswith("tmp__sync_shockrate__")]
            pos_cols = [col for col in sync_frame.columns if col.startswith("tmp__sync_posz7__")]
            neg_cols = [col for col in sync_frame.columns if col.startswith("tmp__sync_negz7__")]
            sync_frame["tmp__sync_absz7__mean"] = sync_frame[abs_cols].mean(axis=1)
            sync_frame["tmp__sync_absz7__std"] = sync_frame[abs_cols].std(axis=1)
            sync_frame["tmp__sync_absz7__max"] = sync_frame[abs_cols].max(axis=1)
            sync_frame["tmp__sync_absz7__breadth_gt1"] = (sync_frame[abs_cols] > 1.0).sum(axis=1)
            sync_frame["tmp__sync_shockrate__mean"] = sync_frame[shock_cols].mean(axis=1)
            sync_frame["tmp__sync_shockrate__breadth"] = (sync_frame[shock_cols] > 0.0).sum(axis=1)
            sync_frame["tmp__sync_signed_balance__mean"] = sync_frame[pos_cols].mean(axis=1) - sync_frame[neg_cols].mean(axis=1)
            for left, right in (("body", "phone"), ("social", "phone"), ("mobility", "social"), ("sleep", "body")):
                left_col = f"tmp__sync_absz7__{left}"
                right_col = f"tmp__sync_absz7__{right}"
                if left_col in sync_frame and right_col in sync_frame:
                    sync_frame[f"tmp__sync_absz7_gap__{left}_minus_{right}"] = sync_frame[left_col] - sync_frame[right_col]
                    sync_frame[f"tmp__sync_absz7_abs_gap__{left}_minus_{right}"] = (sync_frame[left_col] - sync_frame[right_col]).abs()
            temporal_parts.append(sync_frame)

            leadlag_parts = {}
            leadlag_pairs = (
                ("phone", "body"),
                ("phone", "sleep"),
                ("phone", "social"),
                ("social", "body"),
                ("social", "sleep"),
                ("social", "phone"),
                ("mobility", "body"),
                ("mobility", "sleep"),
                ("mobility", "social"),
                ("missing", "sleep"),
                ("missing", "body"),
                ("sleep", "body"),
            )
            for lag in (1, 2):
                shifted = sync_frame.groupby(ordered["subject_id"], sort=False).shift(lag)
                for left, right in leadlag_pairs:
                    left_abs = f"tmp__sync_absz7__{left}"
                    left_pos = f"tmp__sync_posz7__{left}"
                    left_neg = f"tmp__sync_negz7__{left}"
                    left_shock = f"tmp__sync_shockrate__{left}"
                    right_abs = f"tmp__sync_absz7__{right}"
                    right_pos = f"tmp__sync_posz7__{right}"
                    right_neg = f"tmp__sync_negz7__{right}"
                    right_shock = f"tmp__sync_shockrate__{right}"
                    if left_abs not in shifted or right_abs not in sync_frame:
                        continue
                    prefix = f"tmp__leadlag_lag{lag}__{left}_to_{right}"
                    leadlag_parts[f"{prefix}__abs_product"] = shifted[left_abs] * sync_frame[right_abs]
                    leadlag_parts[f"{prefix}__abs_delta"] = sync_frame[right_abs] - shifted[left_abs]
                    if left_shock in shifted and right_shock in sync_frame:
                        leadlag_parts[f"{prefix}__shock_product"] = shifted[left_shock] * sync_frame[right_shock]
                    if left_pos in shifted and left_neg in shifted and right_pos in sync_frame and right_neg in sync_frame:
                        same_direction = (shifted[left_pos] * sync_frame[right_pos]) + (shifted[left_neg] * sync_frame[right_neg])
                        opposite_direction = (shifted[left_pos] * sync_frame[right_neg]) + (shifted[left_neg] * sync_frame[right_pos])
                        leadlag_parts[f"{prefix}__same_direction"] = same_direction
                        leadlag_parts[f"{prefix}__opposite_direction"] = opposite_direction
                        leadlag_parts[f"{prefix}__direction_balance"] = same_direction - opposite_direction
            if leadlag_parts:
                temporal_parts.append(pd.DataFrame(leadlag_parts, index=ordered.index).replace([np.inf, -np.inf], np.nan))

            motif_parts = {}
            motif_base_cols = [
                col
                for col in sync_frame.columns
                if col.startswith(("tmp__sync_absz7__", "tmp__sync_posz7__", "tmp__sync_negz7__", "tmp__sync_shockrate__"))
                and not any(token in col for token in ("mean", "std", "max", "breadth", "balance", "gap"))
            ]
            for col in motif_base_cols:
                short = col.removeprefix("tmp__sync_")
                lag1 = sync_frame.groupby(ordered["subject_id"], sort=False)[col].shift(1)
                lag2 = sync_frame.groupby(ordered["subject_id"], sort=False)[col].shift(2)
                delta1 = sync_frame[col] - lag1
                delta2 = sync_frame[col] - lag2
                motif_parts[f"tmp__motif__{short}__lag1"] = lag1
                motif_parts[f"tmp__motif__{short}__lag2"] = lag2
                motif_parts[f"tmp__motif__{short}__delta1"] = delta1
                motif_parts[f"tmp__motif__{short}__delta2"] = delta2
                motif_parts[f"tmp__motif__{short}__reversal"] = -(delta1 * (lag1 - lag2))
                for window in (3, 5):
                    roll = sync_frame.groupby(ordered["subject_id"], sort=False)[col].transform(
                        lambda values: values.rolling(window=window, min_periods=1).mean()
                    )
                    roll_std = sync_frame.groupby(ordered["subject_id"], sort=False)[col].transform(
                        lambda values: values.rolling(window=window, min_periods=2).std()
                    )
                    lag_window = sync_frame.groupby(ordered["subject_id"], sort=False)[col].shift(window - 1)
                    motif_parts[f"tmp__motif__{short}__roll{window}_mean"] = roll
                    motif_parts[f"tmp__motif__{short}__roll{window}_std"] = roll_std
                    motif_parts[f"tmp__motif__{short}__roll{window}_slope"] = (sync_frame[col] - lag_window) / float(window - 1)

            if motif_parts:
                motif_frame = pd.DataFrame(motif_parts, index=ordered.index).replace([np.inf, -np.inf], np.nan)
                delta_cols = [col for col in motif_frame.columns if col.endswith("__delta1")]
                reversal_cols = [col for col in motif_frame.columns if col.endswith("__reversal")]
                slope_cols = [col for col in motif_frame.columns if col.endswith("__roll3_slope")]
                if delta_cols:
                    motif_frame["tmp__motif_summary__delta1_abs_mean"] = motif_frame[delta_cols].abs().mean(axis=1)
                    motif_frame["tmp__motif_summary__delta1_pos_breadth"] = (motif_frame[delta_cols] > 0.0).sum(axis=1)
                    motif_frame["tmp__motif_summary__delta1_neg_breadth"] = (motif_frame[delta_cols] < 0.0).sum(axis=1)
                if reversal_cols:
                    motif_frame["tmp__motif_summary__reversal_mean"] = motif_frame[reversal_cols].mean(axis=1)
                    motif_frame["tmp__motif_summary__reversal_abs_mean"] = motif_frame[reversal_cols].abs().mean(axis=1)
                if slope_cols:
                    motif_frame["tmp__motif_summary__slope_abs_mean"] = motif_frame[slope_cols].abs().mean(axis=1)
                    motif_frame["tmp__motif_summary__slope_pos_breadth"] = (motif_frame[slope_cols] > 0.0).sum(axis=1)
                temporal_parts.append(motif_frame)

            state_parts = {}
            state_abs_cols = [col for col in sync_frame.columns if col.startswith("tmp__sync_absz7__") and "__" in col]
            state_abs_cols = [
                col
                for col in state_abs_cols
                if not any(token in col for token in ("mean", "std", "max", "breadth", "gap", "balance"))
            ]
            if state_abs_cols:
                current_state = sync_frame[state_abs_cols]
                lag1_state = current_state.groupby(ordered["subject_id"], sort=False).shift(1)
                lag2_state = current_state.groupby(ordered["subject_id"], sort=False).shift(2)
                delta1_state = current_state - lag1_state
                delta2_state = current_state - lag2_state
                eps = 1e-6
                cur_norm = np.sqrt((current_state * current_state).sum(axis=1))
                lag1_norm = np.sqrt((lag1_state * lag1_state).sum(axis=1))
                delta1_norm = np.sqrt((delta1_state * delta1_state).sum(axis=1))
                delta2_norm = np.sqrt((delta2_state * delta2_state).sum(axis=1))
                dot_lag1 = (current_state * lag1_state).sum(axis=1)
                dot_delta = (delta1_state * (lag1_state - lag2_state)).sum(axis=1)
                cur_sum = current_state.sum(axis=1)
                lag_sum = lag1_state.sum(axis=1)
                cur_share = current_state.div(cur_sum.replace(0, np.nan), axis=0)
                lag_share = lag1_state.div(lag_sum.replace(0, np.nan), axis=0)
                share_delta = cur_share - lag_share
                entropy = -(cur_share * np.log(cur_share.clip(lower=eps))).sum(axis=1)
                lag_entropy = -(lag_share * np.log(lag_share.clip(lower=eps))).sum(axis=1)
                state_parts["tmp__state_transition__cur_norm"] = cur_norm
                state_parts["tmp__state_transition__lag1_norm"] = lag1_norm
                state_parts["tmp__state_transition__delta1_norm"] = delta1_norm
                state_parts["tmp__state_transition__delta2_norm"] = delta2_norm
                state_parts["tmp__state_transition__cosine_lag1"] = dot_lag1 / (cur_norm * lag1_norm + eps)
                state_parts["tmp__state_transition__speed_ratio"] = delta1_norm / (lag1_norm + eps)
                state_parts["tmp__state_transition__accel_ratio"] = delta1_norm / (delta2_norm + eps)
                state_parts["tmp__state_transition__direction_persistence"] = dot_delta / (delta1_norm * np.sqrt(((lag1_state - lag2_state) ** 2).sum(axis=1)) + eps)
                state_parts["tmp__state_transition__entropy"] = entropy
                state_parts["tmp__state_transition__entropy_delta"] = entropy - lag_entropy
                state_parts["tmp__state_transition__dominance"] = cur_share.max(axis=1)
                state_parts["tmp__state_transition__dominance_delta"] = cur_share.max(axis=1) - lag_share.max(axis=1)
                state_parts["tmp__state_transition__share_shift_l1"] = share_delta.abs().sum(axis=1)
                state_parts["tmp__state_transition__share_shift_l2"] = np.sqrt((share_delta * share_delta).sum(axis=1))
                for col in state_abs_cols:
                    name = col.removeprefix("tmp__sync_absz7__")
                    state_parts[f"tmp__state_transition_component__{name}__share"] = cur_share[col]
                    state_parts[f"tmp__state_transition_component__{name}__share_delta"] = share_delta[col]
                    state_parts[f"tmp__state_transition_component__{name}__velocity"] = delta1_state[col]
                temporal_parts.append(pd.DataFrame(state_parts, index=ordered.index).replace([np.inf, -np.inf], np.nan))

                recurrence_values: dict[str, np.ndarray] = {}
                recurrence_metrics = ("min_l2", "mean_l2", "knn3_l2", "max_cos", "mean_cos", "centroid_l2")
                for window_name in ("w7", "w14", "w28", "all"):
                    for metric in recurrence_metrics:
                        recurrence_values[f"tmp__state_recurrence__{window_name}__{metric}"] = np.full(len(ordered), np.nan, dtype=np.float32)

                state_matrix = current_state.to_numpy(float)
                for _, group in ordered.groupby("subject_id", sort=False):
                    row_pos = group.index.to_numpy()
                    values = state_matrix[row_pos]
                    for local_i, global_i in enumerate(row_pos):
                        cur = values[local_i]
                        if not np.isfinite(cur).any():
                            continue
                        for window_name, window in (("w7", 7), ("w14", 14), ("w28", 28), ("all", None)):
                            start = 0 if window is None else max(0, local_i - window)
                            prior = values[start:local_i]
                            if len(prior) == 0:
                                continue
                            finite = np.isfinite(prior) & np.isfinite(cur)[None, :]
                            valid_counts = finite.sum(axis=1)
                            usable = valid_counts > 0
                            if not usable.any():
                                continue
                            diff = np.where(finite, prior - cur[None, :], 0.0)
                            l2 = np.sqrt((diff * diff).sum(axis=1) / np.maximum(valid_counts, 1))
                            l2 = l2[usable]
                            prior_usable = np.where(finite[usable], prior[usable], 0.0)
                            cur_masked = np.where(np.isfinite(cur), cur, 0.0)
                            dot = (prior_usable * cur_masked[None, :]).sum(axis=1)
                            prior_norm = np.sqrt((prior_usable * prior_usable).sum(axis=1))
                            cur_norm_scalar = np.sqrt((cur_masked * cur_masked).sum())
                            cosine = dot / (prior_norm * cur_norm_scalar + 1e-6)
                            centroid = np.nanmean(prior, axis=0)
                            centroid_diff = cur - centroid
                            centroid_l2 = np.sqrt(np.nanmean(centroid_diff * centroid_diff))
                            recurrence_values[f"tmp__state_recurrence__{window_name}__min_l2"][global_i] = np.nanmin(l2)
                            recurrence_values[f"tmp__state_recurrence__{window_name}__mean_l2"][global_i] = np.nanmean(l2)
                            recurrence_values[f"tmp__state_recurrence__{window_name}__knn3_l2"][global_i] = np.nanmean(np.sort(l2)[: min(3, len(l2))])
                            recurrence_values[f"tmp__state_recurrence__{window_name}__max_cos"][global_i] = np.nanmax(cosine)
                            recurrence_values[f"tmp__state_recurrence__{window_name}__mean_cos"][global_i] = np.nanmean(cosine)
                            recurrence_values[f"tmp__state_recurrence__{window_name}__centroid_l2"][global_i] = centroid_l2
                recurrence_frame = pd.DataFrame(recurrence_values, index=ordered.index).replace([np.inf, -np.inf], np.nan)
                if not recurrence_frame.empty:
                    if "tmp__state_recurrence__w7__min_l2" in recurrence_frame and "tmp__state_recurrence__w28__min_l2" in recurrence_frame:
                        recurrence_frame["tmp__state_recurrence__w7_vs_w28_min_l2"] = (
                            recurrence_frame["tmp__state_recurrence__w7__min_l2"]
                            - recurrence_frame["tmp__state_recurrence__w28__min_l2"]
                        )
                    if "tmp__state_recurrence__w7__centroid_l2" in recurrence_frame and "tmp__state_recurrence__w28__centroid_l2" in recurrence_frame:
                        recurrence_frame["tmp__state_recurrence__w7_vs_w28_centroid_l2"] = (
                            recurrence_frame["tmp__state_recurrence__w7__centroid_l2"]
                            - recurrence_frame["tmp__state_recurrence__w28__centroid_l2"]
                        )
                    temporal_parts.append(recurrence_frame)

                    novelty_cols = [
                        col
                        for col in recurrence_frame.columns
                        if col.startswith("tmp__state_recurrence__")
                        and any(token in col for token in ("min_l2", "knn3_l2", "centroid_l2", "max_cos"))
                    ]
                    novelty_parts = {}
                    grouped_recur = recurrence_frame.groupby(ordered["subject_id"], sort=False)
                    for col in novelty_cols:
                        short = col.removeprefix("tmp__state_recurrence__")
                        current_metric = recurrence_frame[col]
                        prior_mean = grouped_recur[col].transform(lambda values: values.shift(1).expanding(min_periods=2).mean())
                        prior_std = grouped_recur[col].transform(lambda values: values.shift(1).expanding(min_periods=3).std())
                        z = (current_metric - prior_mean) / prior_std.replace(0, np.nan)
                        if col.endswith("max_cos"):
                            z = -z
                        shock = (z > 1.0).astype(float).where(z.notna())
                        novelty_parts[f"tmp__state_novelty__{short}__z"] = z
                        novelty_parts[f"tmp__state_novelty__{short}__shock_gt1"] = shock
                        for window in (3, 7):
                            roll_mean = grouped_recur[col].transform(lambda values: values.rolling(window=window, min_periods=1).mean())
                            roll_std = grouped_recur[col].transform(lambda values: values.rolling(window=window, min_periods=2).std())
                            shock_count = shock.groupby(ordered["subject_id"], sort=False).transform(
                                lambda values: values.rolling(window=window, min_periods=1).sum()
                            )
                            novelty_parts[f"tmp__state_novelty__{short}__roll{window}_mean"] = roll_mean
                            novelty_parts[f"tmp__state_novelty__{short}__roll{window}_std"] = roll_std
                            novelty_parts[f"tmp__state_novelty__{short}__shock_count_roll{window}"] = shock_count

                    novelty_frame = pd.DataFrame(novelty_parts, index=ordered.index).replace([np.inf, -np.inf], np.nan)
                    if not novelty_frame.empty:
                        shock_cols_novelty = [col for col in novelty_frame.columns if col.endswith("__shock_gt1")]
                        z_cols_novelty = [col for col in novelty_frame.columns if col.endswith("__z")]
                        if shock_cols_novelty:
                            novelty_frame["tmp__state_novelty_summary__shock_breadth"] = novelty_frame[shock_cols_novelty].sum(axis=1)
                        if z_cols_novelty:
                            novelty_frame["tmp__state_novelty_summary__z_mean"] = novelty_frame[z_cols_novelty].mean(axis=1)
                            novelty_frame["tmp__state_novelty_summary__z_max"] = novelty_frame[z_cols_novelty].max(axis=1)
                            novelty_frame["tmp__state_novelty_summary__z_pos_breadth"] = (novelty_frame[z_cols_novelty] > 1.0).sum(axis=1)
                        temporal_parts.append(novelty_frame)

                        recovery_parts = {}
                        grouped_novelty = novelty_frame.groupby(ordered["subject_id"], sort=False)
                        recovery_base_cols = [
                            col
                            for col in novelty_frame.columns
                            if col.endswith("__z")
                            or col.endswith("__shock_gt1")
                            or col.endswith("__shock_count_roll3")
                            or col.endswith("__shock_count_roll7")
                            or col.startswith("tmp__state_novelty_summary__")
                        ]
                        for col in recovery_base_cols:
                            short = col.removeprefix("tmp__state_novelty__").removeprefix("tmp__state_novelty_summary__")
                            current_metric = novelty_frame[col]
                            lag1 = grouped_novelty[col].shift(1)
                            delta = current_metric - lag1
                            roll3 = grouped_novelty[col].transform(lambda values: values.rolling(window=3, min_periods=1).mean())
                            roll7 = grouped_novelty[col].transform(lambda values: values.rolling(window=7, min_periods=1).mean())
                            recovery = lag1.abs() - current_metric.abs()
                            recovery_parts[f"tmp__state_novelty_recovery__{short}__delta1"] = delta
                            recovery_parts[f"tmp__state_novelty_recovery__{short}__abs_delta1"] = delta.abs()
                            recovery_parts[f"tmp__state_novelty_recovery__{short}__roll3_minus_roll7"] = roll3 - roll7
                            recovery_parts[f"tmp__state_novelty_recovery__{short}__recovery"] = recovery
                            recovery_parts[f"tmp__state_novelty_recovery__{short}__worsening"] = (-recovery).clip(lower=0.0)
                        recovery_frame = pd.DataFrame(recovery_parts, index=ordered.index).replace([np.inf, -np.inf], np.nan)
                        if not recovery_frame.empty:
                            worsening_cols = [col for col in recovery_frame.columns if col.endswith("__worsening")]
                            recovery_cols = [col for col in recovery_frame.columns if col.endswith("__recovery")]
                            delta_cols = [col for col in recovery_frame.columns if col.endswith("__delta1")]
                            if worsening_cols:
                                recovery_frame["tmp__state_novelty_recovery_summary__worsening_mean"] = recovery_frame[worsening_cols].mean(axis=1)
                                recovery_frame["tmp__state_novelty_recovery_summary__worsening_breadth"] = (recovery_frame[worsening_cols] > 0.0).sum(axis=1)
                            if recovery_cols:
                                recovery_frame["tmp__state_novelty_recovery_summary__recovery_mean"] = recovery_frame[recovery_cols].mean(axis=1)
                                recovery_frame["tmp__state_novelty_recovery_summary__recovery_breadth"] = (recovery_frame[recovery_cols] > 0.0).sum(axis=1)
                            if delta_cols:
                                recovery_frame["tmp__state_novelty_recovery_summary__delta_abs_mean"] = recovery_frame[delta_cols].abs().mean(axis=1)
                            temporal_parts.append(recovery_frame)

    if 3 in roll_means and 7 in roll_means:
        momentum = roll_means[3] - roll_means[7]
        temporal_parts.append(momentum.add_prefix("tmp__roll3_minus_roll7__"))
        temporal_parts.append(momentum.abs().add_prefix("tmp__roll3_minus_roll7_abs__"))
    if 3 in roll_stds and 7 in roll_stds:
        volatility_regime = roll_stds[3] / roll_stds[7].replace(0, np.nan)
        temporal_parts.append(volatility_regime.add_prefix("tmp__volregime3v7__"))
        temporal_parts.append(np.log1p(volatility_regime).add_prefix("tmp__volregime3v7_log__"))

    if 7 in roll_means:
        roll7_delta = current - roll_means[7]
        prev_roll7_delta = prev - roll_means[7]
        same_direction = np.sign(roll7_delta) * np.sign(prev_roll7_delta)
        persistence = roll7_delta * prev_roll7_delta
        recovery = prev_roll7_delta.abs() - roll7_delta.abs()
        temporal_parts.append(same_direction.add_prefix("tmp__persist_sign_roll7__"))
        temporal_parts.append(persistence.add_prefix("tmp__persist_product_roll7__"))
        temporal_parts.append(recovery.add_prefix("tmp__recovery_to_roll7__"))
        temporal_parts.append(recovery.abs().add_prefix("tmp__recovery_to_roll7_abs__"))

    for window in (7, 14):
        rank_values = np.full((len(ordered), len(temporal_cols)), np.nan, dtype=np.float32)
        for _, group in ordered.groupby("subject_id", sort=False):
            row_pos = group.index.to_numpy()
            values = group[temporal_cols].to_numpy(float)
            for local_i, global_i in enumerate(row_pos):
                start = max(0, local_i - window)
                prior = values[start:local_i]
                if len(prior) == 0:
                    continue
                current_row = values[local_i]
                finite = np.isfinite(prior) & np.isfinite(current_row)[None, :]
                counts = finite.sum(axis=0)
                less_equal = ((prior <= current_row[None, :]) & finite).sum(axis=0)
                rank_values[global_i] = np.where(counts > 0, less_equal / np.maximum(counts, 1), np.nan)
        rank_frame = pd.DataFrame(rank_values, columns=temporal_cols, index=ordered.index)
        temporal_parts.append(rank_frame.add_prefix(f"tmp__roll{window}_rank__"))
        temporal_parts.append((rank_frame - 0.5).abs().add_prefix(f"tmp__roll{window}_rank_extreme__"))

    out = pd.concat(temporal_parts, axis=1).replace([np.inf, -np.inf], np.nan)
    out["_orig_idx"] = ordered["_orig_idx"].to_numpy()
    out = out.sort_values("_orig_idx").drop(columns=["_orig_idx"]).reset_index(drop=True)
    return out


def add_engineered_digest_features(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    train_keys: pd.DataFrame,
    sample_keys: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Add label-free daily digest features that make retrieval latents less column-fragmented."""
    combined = pd.concat([train_x, sample_x], ignore_index=True)
    combined_keys = pd.concat([train_keys[KEY_COLUMNS], sample_keys[KEY_COLUMNS]], ignore_index=True)
    columns = combined.columns.tolist()
    subset_specs = {
        "eng__phone_all__": columns_matching(columns, ["screen", "usage", "app_", "app_hash", "charging"]),
        "eng__phone_night__": columns_matching(
            columns,
            ["screen", "usage", "app_", "app_hash", "charging"],
            ["night"],
        )
        + columns_matching(columns, ["screen", "usage", "app_", "app_hash", "charging"], ["earlyam"])
        + columns_matching(columns, ["screen", "usage", "app_", "app_hash", "charging"], ["late_night"]),
        "eng__social_all__": columns_matching(
            columns,
            ["amb", "speech", "music", "vehicle", "silence", "wifi", "ble", "home", "work", "elsewhere", "unique"],
        ),
        "eng__social_night__": columns_matching(
            columns,
            ["amb", "speech", "music", "vehicle", "silence", "wifi", "ble", "home", "work", "elsewhere", "unique"],
            ["night"],
        )
        + columns_matching(
            columns,
            ["amb", "speech", "music", "vehicle", "silence", "wifi", "ble", "home", "work", "elsewhere", "unique"],
            ["earlyam"],
        )
        + columns_matching(
            columns,
            ["amb", "speech", "music", "vehicle", "silence", "wifi", "ble", "home", "work", "elsewhere", "unique"],
            ["late_night"],
        ),
        "eng__physio_all__": columns_matching(columns, ["hr", "step", "pedo", "light", "still", "activity"]),
        "eng__physio_night__": columns_matching(columns, ["hr", "step", "pedo", "light", "still", "activity"], ["night"])
        + columns_matching(columns, ["hr", "step", "pedo", "light", "still", "activity"], ["earlyam"])
        + columns_matching(columns, ["hr", "step", "pedo", "light", "still", "activity"], ["late_night"]),
        "eng__mobility_all__": columns_matching(columns, ["gps", "speed", "stationary", "moving", "place", "home", "work", "elsewhere"]),
        "eng__mobility_night__": columns_matching(columns, ["gps", "speed", "stationary", "moving", "place", "home", "work", "elsewhere"], ["night"])
        + columns_matching(columns, ["gps", "speed", "stationary", "moving", "place", "home", "work", "elsewhere"], ["earlyam"])
        + columns_matching(columns, ["gps", "speed", "stationary", "moving", "place", "home", "work", "elsewhere"], ["late_night"]),
        "eng__volatility__": columns_matching(
            columns,
            ["abs_delta", "delta_std", "delta_abs", "gap_max", "gap_mean", "novel", "novelty", "entropy", "event_abs_delta"],
        ),
        "eng__coverage_missing__": columns_matching(columns, ["gap", "row_count", "coverage", "cov__", "normcov", "zero_rate", "missing"]),
        "eng__sleep_proxy__": columns_matching(columns, ["sleep_proxy", "sleep_interrupt", "night_hr", "night_screen", "night_step", "night_charging"]),
    }
    digest_parts = [row_digest(combined, sorted(set(cols)), prefix) for prefix, cols in subset_specs.items()]
    digest = pd.concat(digest_parts, axis=1)

    def add_difference(left: str, right: str, name: str) -> None:
        left_cols = [c for c in digest.columns if c.startswith(left)]
        for left_col in left_cols:
            suffix = left_col.removeprefix(left)
            right_col = f"{right}{suffix}"
            if right_col in digest:
                digest[f"{name}{suffix}"] = digest[left_col] - digest[right_col]
                digest[f"{name}abs_{suffix}"] = np.abs(digest[left_col] - digest[right_col])

    add_difference("eng__phone_night__", "eng__phone_all__", "eng__phone_recovery__")
    add_difference("eng__social_night__", "eng__social_all__", "eng__social_rhythm__")
    add_difference("eng__physio_night__", "eng__physio_all__", "eng__body_recovery__")
    add_difference("eng__mobility_night__", "eng__mobility_all__", "eng__mobility_rhythm__")
    add_difference("eng__social_all__", "eng__phone_all__", "eng__social_phone_mismatch__")
    add_difference("eng__physio_all__", "eng__phone_all__", "eng__body_phone_mismatch__")
    add_difference("eng__mobility_all__", "eng__social_all__", "eng__mobility_social_mismatch__")
    add_difference("eng__volatility__", "eng__coverage_missing__", "eng__volatility_missing_mismatch__")

    temporal = add_temporal_deviation_features(digest.replace([np.inf, -np.inf], np.nan), combined_keys)
    digest = pd.concat([digest, temporal], axis=1).replace([np.inf, -np.inf], np.nan)
    train_digest = digest.iloc[: len(train_x)].reset_index(drop=True)
    sample_digest = digest.iloc[len(train_x) :].reset_index(drop=True)
    return (
        pd.concat([train_x.reset_index(drop=True), train_digest], axis=1),
        pd.concat([sample_x.reset_index(drop=True), sample_digest], axis=1),
    )


def merge_feature_tables(train: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = normalize_keys(pd.read_parquet("outputs/encoder_day_pyramid/day_summary_features.parquet"))
    master = normalize_keys(pd.read_parquet("artifacts/10_master_daily.parquet"))
    drop = set(KEY_COLUMNS + TARGET_COLUMNS + ["split", "is_labeled", "role", "date", "sleep_onset", "wake_time"])

    def prepared(table: pd.DataFrame, prefix: str) -> pd.DataFrame:
        numeric_cols = [c for c in table.select_dtypes(include=[np.number]).columns if c not in drop]
        return table[KEY_COLUMNS + numeric_cols].rename(columns={c: f"{prefix}{c}" for c in numeric_cols})

    summary = prepared(summary, "sum__")
    master = prepared(master, "mst__")
    train_x = train[KEY_COLUMNS].merge(summary, on=KEY_COLUMNS, how="left", validate="one_to_one")
    train_x = train_x.merge(master, on=KEY_COLUMNS, how="left", validate="one_to_one")
    sample_x = sample[KEY_COLUMNS].merge(summary, on=KEY_COLUMNS, how="left", validate="one_to_one")
    sample_x = sample_x.merge(master, on=KEY_COLUMNS, how="left", validate="one_to_one")
    feature_cols = [c for c in train_x.columns if c not in KEY_COLUMNS]
    train_features = signed_log1p(train_x[feature_cols])
    sample_features = signed_log1p(sample_x[feature_cols])
    return add_engineered_digest_features(train_features, sample_features, train[KEY_COLUMNS], sample[KEY_COLUMNS])


def select_group_columns(columns: list[str], group: str) -> list[str]:
    groups = {
        "sleep_missing": [
            "sleep",
            "night",
            "latenight",
            "late_night",
            "earlyam",
            "missing",
            "gap",
            "row_count",
            "charging",
            "screen",
            "light",
            "hr",
            "step",
            "still",
        ],
        "connectivity_context": [
            "wifi",
            "ble",
            "gps",
            "amb",
            "ambience",
            "usage",
            "screen",
            "charging",
            "missing",
            "gap",
        ],
        "night_events": [
            "event",
            "proto",
            "sleep_proxy",
            "missingness",
            "phone_night",
            "physio_night",
            "mobility_night",
            "mod_night",
            "mod_late_night",
            "z_night",
            "z_latenight",
            "z_earlyam",
        ],
        "s2_broad": [
            "sleep",
            "night",
            "earlyam",
            "late_night",
            "missing",
            "gap",
            "row_count",
            "screen",
            "charging",
            "light",
            "hr",
            "step",
            "still",
            "gps",
            "wifi",
            "ble",
            "amb",
            "usage",
            "proto",
            "event",
        ],
        "volatility_shift": [
            "abs_delta",
            "delta_std",
            "delta_max",
            "delta_abs",
            "gap_max",
            "gap_mean",
            "normcov",
            "zero_rate",
            "novel",
            "novelty",
            "entropy",
        ],
        "circadian_disruption": [
            "late_night",
            "night",
            "earlyam",
            "z_abs",
            "screen",
            "charging",
            "light",
            "hr",
            "step",
            "gps_speed",
            "still",
            "sleep_proxy",
            "missingness",
        ],
        "social_environment": [
            "amb",
            "ambience",
            "speech",
            "music",
            "vehicle",
            "silence",
            "wifi",
            "ble",
            "gps",
            "home",
            "work",
            "elsewhere",
            "transient",
            "usage",
            "unique",
            "app_hash",
        ],
        "q1_s2_residual": [
            "abs_delta",
            "gap",
            "normcov",
            "proto",
            "event",
            "late_night",
            "night",
            "screen",
            "usage",
            "amb",
            "wifi",
            "ble",
            "gps",
            "hr",
            "light",
            "charging",
            "panel",
            "weekday",
        ],
        "phone_recovery": [
            "eng__phone",
            "eng__phone_recovery",
            "eng__body_phone_mismatch",
            "screen",
            "usage",
            "app_",
            "charging",
            "night",
            "earlyam",
            "late_night",
            "sleep_proxy",
        ],
        "social_rhythm": [
            "eng__social",
            "eng__social_rhythm",
            "eng__social_phone_mismatch",
            "eng__mobility_social_mismatch",
            "amb",
            "wifi",
            "ble",
            "speech",
            "music",
            "vehicle",
            "silence",
            "home",
            "work",
            "elsewhere",
            "unique",
            "novel",
        ],
        "body_recovery": [
            "eng__physio",
            "eng__body_recovery",
            "eng__body_phone_mismatch",
            "hr",
            "step",
            "pedo",
            "light",
            "still",
            "activity",
            "night",
            "earlyam",
            "late_night",
            "sleep_proxy",
        ],
        "modality_desync": [
            "eng__",
            "mismatch",
            "recovery",
            "rhythm",
            "volatility",
            "coverage_missing",
            "normcov",
            "abs_delta",
            "gap",
            "proto",
            "event",
        ],
        "temporal_deviation": [
            "tmp__prev1_delta__",
            "tmp__prev1_abs_delta__",
            "tmp__roll3_delta__",
            "tmp__roll3_abs_delta__",
            "tmp__roll3_z__",
            "tmp__roll7_delta__",
            "tmp__roll7_abs_delta__",
            "tmp__roll7_z__",
        ],
        "temporal_recovery": [
            "tmp__prev1_delta__eng__phone_recovery",
            "tmp__prev1_delta__eng__social_rhythm",
            "tmp__prev1_delta__eng__body_recovery",
            "tmp__prev1_delta__eng__mobility_rhythm",
            "tmp__roll3_delta__eng__phone_recovery",
            "tmp__roll3_delta__eng__social_rhythm",
            "tmp__roll3_delta__eng__body_recovery",
            "tmp__roll3_delta__eng__mobility_rhythm",
            "tmp__roll7_delta__eng__phone_recovery",
            "tmp__roll7_delta__eng__social_rhythm",
            "tmp__roll7_delta__eng__body_recovery",
            "tmp__roll7_delta__eng__mobility_rhythm",
        ],
        "temporal_acceleration": [
            "tmp__prev2_delta__",
            "tmp__prev2_abs_delta__",
            "tmp__accel__",
            "tmp__accel_abs__",
        ],
        "temporal_momentum": [
            "tmp__roll3_minus_roll7__",
            "tmp__roll3_minus_roll7_abs__",
        ],
        "temporal_extreme": [
            "tmp__roll7_rank__",
            "tmp__roll7_rank_extreme__",
            "tmp__roll14_rank__",
            "tmp__roll14_rank_extreme__",
        ],
        "temporal_persistence": [
            "tmp__persist_sign_roll7__",
            "tmp__persist_product_roll7__",
            "tmp__recovery_to_roll7__",
            "tmp__recovery_to_roll7_abs__",
        ],
        "temporal_regime": [
            "tmp__volregime3v7__",
            "tmp__volregime3v7_log__",
        ],
        "temporal_burden": [
            "tmp__shock_gt1_roll7__",
            "tmp__shock_gt15_roll7__",
            "tmp__burden_absz7_roll3__",
            "tmp__burden_absz7_roll7__",
            "tmp__shock_count_gt1_roll3__",
            "tmp__shock_count_gt1_roll7__",
            "tmp__shock_streak_gt1_roll7__",
            "tmp__shock_streak_gt15_roll7__",
        ],
        "temporal_signed_burden": [
            "tmp__signed_burden_posz7_roll3__",
            "tmp__signed_burden_posz7_roll7__",
            "tmp__signed_burden_negz7_roll3__",
            "tmp__signed_burden_negz7_roll7__",
            "tmp__signed_burden_balance_roll3__",
            "tmp__signed_burden_balance_roll7__",
        ],
        "temporal_decay": [
            "tmp__decay_absz7_a03__",
            "tmp__decay_posz7_a03__",
            "tmp__decay_negz7_a03__",
            "tmp__decay_absz7_a06__",
            "tmp__decay_posz7_a06__",
            "tmp__decay_negz7_a06__",
            "tmp__shock_age_gt1_roll7__",
            "tmp__shock_age_gt15_roll7__",
        ],
        "temporal_synchrony": [
            "tmp__sync_",
        ],
        "temporal_leadlag": [
            "tmp__leadlag_",
        ],
        "temporal_motif": [
            "tmp__motif_",
        ],
        "temporal_state_transition": [
            "tmp__state_transition",
        ],
        "temporal_state_recurrence": [
            "tmp__state_recurrence",
        ],
        "temporal_state_novelty": [
            "tmp__state_novelty",
        ],
        "temporal_state_novelty_recovery": [
            "tmp__state_novelty_recovery",
        ],
        "temporal_all": [
            "tmp__",
        ],
    }
    needles = groups[group]
    selected = [col for col in columns if any(needle in col.lower() for needle in needles)]
    if not selected:
        raise ValueError(f"No columns selected for group {group}")
    return selected


def add_fold_safe_subject_deviation(
    train_x: pd.DataFrame,
    sample_x: pd.DataFrame,
    train_keys: pd.DataFrame,
    sample_keys: pd.DataFrame,
    fit_idx: np.ndarray,
    apply_idx: np.ndarray | None,
) -> tuple[pd.DataFrame, pd.DataFrame | None, pd.DataFrame]:
    fit = train_x.iloc[fit_idx].reset_index(drop=True)
    global_mean = fit.mean(axis=0, skipna=True)
    global_std = fit.std(axis=0, skipna=True).replace(0, np.nan)
    fit_subjects = train_keys.iloc[fit_idx]["subject_id"].reset_index(drop=True)
    fit_with_subject = fit.assign(subject_id=fit_subjects)
    subject_mean = fit_with_subject.groupby("subject_id").mean(numeric_only=True)
    subject_std = fit_with_subject.groupby("subject_id").std(numeric_only=True).replace(0, np.nan)

    def transform(frame: pd.DataFrame, keys: pd.DataFrame) -> pd.DataFrame:
        means = keys["subject_id"].map(lambda sid: subject_mean.loc[sid] if sid in subject_mean.index else global_mean)
        stds = keys["subject_id"].map(lambda sid: subject_std.loc[sid] if sid in subject_std.index else global_std)
        mean_values = np.vstack([row.to_numpy(float) for row in means])
        std_values = np.vstack([row.to_numpy(float) for row in stds])
        std_values = np.where(np.isfinite(std_values) & (std_values > 1e-6), std_values, global_std.to_numpy(float))
        dev = (frame.to_numpy(float) - mean_values) / np.where(np.abs(std_values) > 1e-6, std_values, 1.0)
        dev = pd.DataFrame(dev, columns=[f"subjdev__{c}" for c in frame.columns], index=frame.index)
        return pd.concat([frame.reset_index(drop=True), dev.reset_index(drop=True)], axis=1)

    train_aug = transform(train_x, train_keys)
    sample_aug = transform(sample_x, sample_keys)
    val_aug = None if apply_idx is None else train_aug.iloc[apply_idx].reset_index(drop=True)
    return train_aug.iloc[fit_idx].reset_index(drop=True), val_aug, sample_aug.reset_index(drop=True)


def preprocess_matrices(
    x_fit: pd.DataFrame,
    y_fit: np.ndarray,
    x_apply: pd.DataFrame,
    x_sample: pd.DataFrame,
    k_best: int,
    pca_dim: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    missing = x_fit.isna().mean(axis=0)
    unique = x_fit.nunique(dropna=True)
    keep = x_fit.columns[(missing <= 0.75) & (unique > 1)].tolist()
    x_fit = x_fit[keep]
    x_apply = x_apply[keep]
    x_sample = x_sample[keep]

    steps: list[object] = [SimpleImputer(strategy="median", keep_empty_features=True), StandardScaler()]
    if k_best > 0 and len(keep) > k_best and len(np.unique(y_fit)) > 1:
        steps.append(SelectKBest(f_classif, k=k_best))
    if pca_dim > 0:
        dim = min(pca_dim, len(x_fit) - 1, k_best if k_best > 0 else len(keep))
        if dim >= 2:
            steps.append(PCA(n_components=dim, random_state=SEED))
            steps.append(StandardScaler())
    pipe = make_pipeline(*steps)
    fit_z = pipe.fit_transform(x_fit, y_fit).astype(np.float32)
    apply_z = pipe.transform(x_apply).astype(np.float32)
    sample_z = pipe.transform(x_sample).astype(np.float32)
    fit_z = np.nan_to_num(fit_z, nan=0.0, posinf=8.0, neginf=-8.0)
    apply_z = np.nan_to_num(apply_z, nan=0.0, posinf=8.0, neginf=-8.0)
    sample_z = np.nan_to_num(sample_z, nan=0.0, posinf=8.0, neginf=-8.0)
    fit_z = np.clip(fit_z, -8.0, 8.0)
    apply_z = np.clip(apply_z, -8.0, 8.0)
    sample_z = np.clip(sample_z, -8.0, 8.0)
    return fit_z, apply_z, sample_z


def weighted_knn_probability(
    ref_z: np.ndarray,
    query_z: np.ndarray,
    ref_y: np.ndarray,
    ref_base: np.ndarray,
    query_base: np.ndarray,
    k: int,
    temp: float,
    mode: str,
) -> np.ndarray:
    d2 = ((query_z[:, None, :] - ref_z[None, :, :]) ** 2).mean(axis=2)
    kk = min(k, ref_z.shape[0])
    idx = np.argpartition(d2, kk - 1, axis=1)[:, :kk]
    chosen = np.take_along_axis(d2, idx, axis=1)
    scale = np.maximum(np.median(chosen, axis=1, keepdims=True), 1e-6) * temp
    weights = np.exp(-chosen / scale)
    weights = weights / np.maximum(weights.sum(axis=1, keepdims=True), 1e-12)
    if mode == "label":
        pred = (weights * ref_y[idx]).sum(axis=1)
    elif mode == "residual":
        residual = ref_y - ref_base
        pred = query_base + (weights * residual[idx]).sum(axis=1)
    elif mode == "logit_residual":
        y_smooth = ref_y * 0.98 + 0.01
        residual = safe_logit(y_smooth) - safe_logit(ref_base)
        pred = sigmoid(safe_logit(query_base) + (weights * residual[idx]).sum(axis=1))
    else:
        raise ValueError(f"Unknown KNN mode: {mode}")
    return np.clip(pred, EPS, 1 - EPS)


def prototype_probability(ref_z: np.ndarray, query_z: np.ndarray, ref_y: np.ndarray) -> np.ndarray:
    if len(np.unique(ref_y)) < 2:
        return np.full(len(query_z), float(ref_y.mean()))
    pos = ref_z[ref_y == 1].mean(axis=0)
    neg = ref_z[ref_y == 0].mean(axis=0)
    d_pos = ((query_z - pos) ** 2).mean(axis=1)
    d_neg = ((query_z - neg) ** 2).mean(axis=1)
    raw = d_neg - d_pos
    scale = np.std(raw) if np.std(raw) > 1e-6 else 1.0
    prior = np.clip(ref_y.mean(), EPS, 1 - EPS)
    return np.clip(sigmoid(safe_logit(np.full(len(query_z), prior)) + raw / scale), EPS, 1 - EPS)


def fit_model_probability(name: str, fit_z: np.ndarray, y_fit: np.ndarray, apply_z: np.ndarray, sample_z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    fit_z = np.clip(np.nan_to_num(fit_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    apply_z = np.clip(np.nan_to_num(apply_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    sample_z = np.clip(np.nan_to_num(sample_z, nan=0.0, posinf=8.0, neginf=-8.0), -8.0, 8.0)
    if name == "hgb":
        model = HistGradientBoostingClassifier(
            learning_rate=0.035,
            max_iter=80,
            max_leaf_nodes=7,
            l2_regularization=0.4,
            min_samples_leaf=15,
            random_state=SEED,
        )
    elif name == "extra":
        model = ExtraTreesClassifier(
            n_estimators=400,
            max_depth=3,
            min_samples_leaf=12,
            max_features=0.5,
            class_weight="balanced_subsample",
            random_state=SEED,
            n_jobs=-1,
        )
    elif name == "logreg":
        model = LogisticRegression(C=0.12, class_weight="balanced", max_iter=2000, solver="liblinear", random_state=SEED)
    elif name == "ridge":
        model = RidgeClassifier(alpha=12.0, class_weight="balanced")
    else:
        raise ValueError(name)
    model.fit(fit_z, y_fit)
    if hasattr(model, "predict_proba"):
        return model.predict_proba(apply_z)[:, 1], model.predict_proba(sample_z)[:, 1]
    apply_score = model.decision_function(apply_z)
    sample_score = model.decision_function(sample_z)
    return sigmoid(apply_score), sigmoid(sample_score)


def write_source(
    output_dir: Path,
    name: str,
    target: str,
    train: pd.DataFrame,
    sample: pd.DataFrame,
    base_train: np.ndarray,
    base_sample: np.ndarray,
    target_oof: np.ndarray,
    target_sample: np.ndarray,
) -> tuple[Path, Path]:
    train_pred = base_train.copy()
    sample_pred = base_sample.copy()
    target_i = TARGET_COLUMNS.index(target)
    train_pred[:, target_i] = np.clip(target_oof, EPS, 1 - EPS)
    sample_pred[:, target_i] = np.clip(target_sample, EPS, 1 - EPS)
    oof = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    submission = sample[KEY_COLUMNS].copy()
    for i, target in enumerate(TARGET_COLUMNS):
        oof[f"pred_{target}"] = train_pred[:, i]
        submission[target] = sample_pred[:, i]
    oof_path = output_dir / f"oof_{name}.csv"
    sub_path = output_dir / f"submission_{name}.csv"
    oof.to_csv(oof_path, index=False)
    submission.to_csv(sub_path, index=False)
    return oof_path, sub_path


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.6f}")
        else:
            display[col] = display[col].map(lambda value: "" if pd.isna(value) else str(value))
    lines = [
        "| " + " | ".join(display.columns) + " |",
        "| " + " | ".join(["---"] * len(display.columns)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in display.astype(str).to_numpy())
    return "\n".join(lines)


def train_sources(args: argparse.Namespace) -> None:
    train = normalize_keys(pd.read_csv(args.train_path))
    sample = normalize_keys(pd.read_csv(args.sample_path))
    target = args.target.upper()
    if target not in TARGET_COLUMNS:
        raise ValueError(f"--target must be one of {TARGET_COLUMNS}, got {args.target}")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_train, base_sample = load_base_predictions(train, sample, Path(args.base_oof), Path(args.base_submission))
    raw_train_x, raw_sample_x = merge_feature_tables(train, sample)
    all_columns = raw_train_x.columns.tolist()
    y = train[target].to_numpy(int)
    base_target = base_train[:, TARGET_COLUMNS.index(target)]
    base_sample_target = base_sample[:, TARGET_COLUMNS.index(target)]
    folds = make_subject_time_folds(train, args.n_folds)

    results: list[SourceResult] = []
    source_paths: list[dict[str, str]] = []
    latent_parts_train: list[pd.DataFrame] = []
    latent_parts_sample: list[pd.DataFrame] = []

    for group in args.groups.split(","):
        group = group.strip()
        cols = select_group_columns(all_columns, group)
        group_train_x = raw_train_x[cols]
        group_sample_x = raw_sample_x[cols]
        configs = [
            ("knn_label", 160, 32),
            ("knn_resid", 220, 48),
            ("knn_logitresid", 220, 48),
            ("proto", 160, 32),
            ("logreg", 220, 48),
            ("hgb", 260, 0),
            ("extra", 260, 0),
        ]
        for method, k_best, pca_dim in configs:
            oof_pred = np.full(len(train), np.nan, dtype=float)
            sample_fold_preds: list[np.ndarray] = []
            fold_scores = []
            for fold_id, fold in enumerate(folds):
                fit_x, val_x, sample_x = add_fold_safe_subject_deviation(
                    group_train_x,
                    group_sample_x,
                    train[KEY_COLUMNS],
                    sample[KEY_COLUMNS],
                    fold.train_idx,
                    fold.val_idx,
                )
                assert val_x is not None
                fit_z, val_z, sample_z = preprocess_matrices(
                    fit_x,
                    y[fold.train_idx],
                    val_x,
                    sample_x,
                    min(k_best, max(2, len(fold.train_idx) - 2)),
                    pca_dim,
                )
                if method.startswith("knn"):
                    mode = {"knn_label": "label", "knn_resid": "residual", "knn_logitresid": "logit_residual"}[method]
                    val_pred = weighted_knn_probability(
                        fit_z,
                        val_z,
                        y[fold.train_idx],
                    base_target[fold.train_idx],
                    base_target[fold.val_idx],
                        args.knn_k,
                        args.knn_temp,
                        mode,
                    )
                    sample_pred = weighted_knn_probability(
                        fit_z,
                        sample_z,
                        y[fold.train_idx],
                    base_target[fold.train_idx],
                    base_sample_target,
                        args.knn_k,
                        args.knn_temp,
                        mode,
                    )
                elif method == "proto":
                    val_pred = prototype_probability(fit_z, val_z, y[fold.train_idx])
                    sample_pred = prototype_probability(fit_z, sample_z, y[fold.train_idx])
                else:
                    val_pred, sample_pred = fit_model_probability(method, fit_z, y[fold.train_idx], val_z, sample_z)
                oof_pred[fold.val_idx] = val_pred
                sample_fold_preds.append(sample_pred)
                fold_scores.append(target_loss(y[fold.val_idx], val_pred))
            if np.isnan(oof_pred).any():
                raise RuntimeError(f"OOF contains NaN for {group}_{method}")
            sample_pred = np.mean(sample_fold_preds, axis=0)
            score = target_loss(y, oof_pred)
            source_name = f"{target.lower()}_{group}_{method}"
            oof_path, sub_path = write_source(output_dir, source_name, target, train, sample, base_train, base_sample, oof_pred, sample_pred)
            results.append(SourceResult(source_name, oof_pred, sample_pred, score))
            source_paths.append({"name": source_name, "oof": str(oof_path), "submission": str(sub_path), f"{target}_log_loss": score, "fold_log_loss": fold_scores})
            latent_parts_train.append(pd.DataFrame({f"latent__{source_name}": safe_logit(oof_pred) - safe_logit(base_target)}))
            latent_parts_sample.append(pd.DataFrame({f"latent__{source_name}": safe_logit(sample_pred) - safe_logit(base_sample_target)}))
            print(f"{source_name}: {target}={score:.6f} folds={[round(v, 6) for v in fold_scores]}")

    # A compact meta latent is intentionally fit fold-safely on the source logits.
    stack_oof = np.column_stack([safe_logit(r.oof_pred) - safe_logit(base_target) for r in results])
    stack_sample_members = np.column_stack([safe_logit(r.sample_pred) - safe_logit(base_sample_target) for r in results])
    meta_oof = np.full(len(train), np.nan, dtype=float)
    meta_sample_folds: list[np.ndarray] = []
    for fold in folds:
        model = LogisticRegression(C=0.08, class_weight="balanced", max_iter=2000, solver="liblinear", random_state=SEED)
        scaler = StandardScaler()
        x_fit = scaler.fit_transform(stack_oof[fold.train_idx])
        x_val = scaler.transform(stack_oof[fold.val_idx])
        x_sample = scaler.transform(stack_sample_members)
        model.fit(x_fit, y[fold.train_idx])
        meta_oof[fold.val_idx] = model.predict_proba(x_val)[:, 1]
        meta_sample_folds.append(model.predict_proba(x_sample)[:, 1])
    meta_sample = np.mean(meta_sample_folds, axis=0)
    meta_score = target_loss(y, meta_oof)
    meta_name = f"{target.lower()}_sleep_retrieval_meta"
    oof_path, sub_path = write_source(output_dir, meta_name, target, train, sample, base_train, base_sample, meta_oof, meta_sample)
    source_paths.append({"name": meta_name, "oof": str(oof_path), "submission": str(sub_path), f"{target}_log_loss": meta_score})
    latent_parts_train.append(pd.DataFrame({f"latent__{meta_name}": safe_logit(meta_oof) - safe_logit(base_target)}))
    latent_parts_sample.append(pd.DataFrame({f"latent__{meta_name}": safe_logit(meta_sample) - safe_logit(base_sample_target)}))
    print(f"{meta_name}: {target}={meta_score:.6f}")

    latent_train = pd.concat([train[KEY_COLUMNS].reset_index(drop=True), *latent_parts_train], axis=1)
    latent_sample = pd.concat([sample[KEY_COLUMNS].reset_index(drop=True), *latent_parts_sample], axis=1)
    latent_train.to_parquet(output_dir / f"{target.lower()}_retrieval_latents_train.parquet", index=False)
    latent_sample.to_parquet(output_dir / f"{target.lower()}_retrieval_latents_sample.parquet", index=False)

    metric_key = f"{target}_log_loss"
    base_score = target_loss(y, base_target)
    report = {
        "target": target,
        "base_log_loss": base_score,
        "best_source_log_loss": min(item[metric_key] for item in source_paths),
        "sources": sorted(source_paths, key=lambda item: item[metric_key]),
        "args": vars(args),
        "feature_groups": {group: len(select_group_columns(all_columns, group.strip())) for group in args.groups.split(",") if group.strip()},
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        f"# {target} sleep/missingness retrieval encoder",
        "",
        f"- Base {target} OOF: `{base_score:.6f}`",
        f"- Best source {target} OOF: `{report['best_source_log_loss']:.6f}`",
        "",
        "## Sources",
        "",
        dataframe_to_markdown(pd.DataFrame(report["sources"])[["name", metric_key, "oof", "submission"]]),
        "",
        "## Feature Groups",
        "",
        dataframe_to_markdown(
            pd.Series(report["feature_groups"], name="n_features")
            .reset_index()
            .rename(columns={"index": "group"})
        ),
    ]
    (output_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved: {output_dir / 'report.md'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build target-specific sleep/missingness retrieval latent sources.")
    parser.add_argument("--train-path", default="data/ch2026_metrics_train.csv")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument("--base-oof", default="outputs/conditional_latent_routing_v10_all_focused_sources/oof_conditional_latent_routing.csv")
    parser.add_argument("--base-submission", default="outputs/conditional_latent_routing_v10_all_focused_sources/submission_conditional_latent_routing.csv")
    parser.add_argument("--output-dir", default="outputs/s2_sleep_retrieval_encoder_v1")
    parser.add_argument("--target", default="S2")
    parser.add_argument("--groups", default="sleep_missing,connectivity_context,night_events,s2_broad")
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--knn-k", type=int, default=17)
    parser.add_argument("--knn-temp", type=float, default=1.2)
    return parser.parse_args()


def main() -> None:
    train_sources(parse_args())


if __name__ == "__main__":
    main()
