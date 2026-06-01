#!/usr/bin/env python3
"""H007: turn the H005/H006 S4 mobility signal into an internal latent feature.

H006 found a real-looking but too-small postprocess: high human mobility rows
prefer S4-up, and the opposite direction is worse.  H007 tests whether the same
signal becomes stronger when treated as a hidden lifestyle state inside the S4
model instead of as a direct logit edit.

JEPA translation used here:
    teacher target representation = H005 mobility route consensus
    context = calendar/subject + non-vehicle episode states
    latent health = teacher prediction, residual, and low-energy agreement
    downstream = S4 classifier with/without this latent block

No public LB is used.  Candidate files are scored only by the existing
public-free selector.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H007 = HITL / "h007_s4_mobility_latent_model"
H007.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import h005_all_human_route_hypotheses as h005  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    KEYS,
    TARGETS,
    base_label_matrix,
    clip_prob,
    folds_for,
    groups_for,
    load_frames,
    md_table,
)
from e295_episode_state_jepa_audit import build_episode_matrix  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260601 + 7
EPS = 1.0e-12
TARGET = "S4"
TIDX = TARGETS.index(TARGET)

H005_TEST = HITL / "h005_all_human_route_hypotheses" / "h005_all_route_tests.csv"
E247 = OUT / CURRENT
H003_TINY = HITL / "h003_hs_jepa_prototype" / "submission_h003_semantic_tiny_11e7aa3b.csv"

LATENT_OUT = H007 / "h007_s4_mobility_latent_features.parquet"
FEATURE_META_OUT = H007 / "h007_feature_meta.csv"
ABLATION_OUT = H007 / "h007_s4_feature_ablation.csv"
NULL_OUT = H007 / "h007_s4_feature_nulls.csv"
CANDIDATE_OUT = H007 / "h007_candidates.csv"
SCORE_OUT = H007 / "h007_selector_scores.csv"
ANATOMY_OUT = H007 / "h007_candidate_anatomy.csv"
GATE_OUT = H007 / "h007_gate_scores.csv"
SELECTION_OUT = H007 / "h007_selection.csv"
REPORT_OUT = H007 / "h007_report.md"


MOBILITY_IDS = ["H0704", "H0774", "H0646"]
SUPPORT_IDS = ["H0568", "H0562", "H0094"]
ALL_STATE_IDS = MOBILITY_IDS + SUPPORT_IDS
CS = [0.05, 0.12, 0.35, 0.80]
NULL_REPS = 4


FEATURE_SETS: dict[str, list[str]] = {
    "mobility_teacher": [
        "h005_mobility_teacher_z",
        "h005_mobility_teacher_rank",
        "h005_mobility_high",
    ],
    "mobility_hypotheses": [
        "h005_H0704_z",
        "h005_H0774_z",
        "h005_H0646_z",
        "h005_mobility_teacher_z",
        "h005_mobility_teacher_rank",
    ],
    "mobility_jepa": [
        "h005_mobility_teacher_z",
        "jepa_mobility_pred_z",
        "jepa_mobility_residual_z",
        "jepa_mobility_energy",
        "jepa_mobility_low_energy",
        "jepa_mobility_agreement",
    ],
    "mobility_interactions": [
        "h005_mobility_teacher_z",
        "h005_mobility_teacher_rank",
        "jepa_mobility_pred_z",
        "jepa_mobility_residual_z",
        "jepa_mobility_low_energy",
        "mobility_x_weekend",
        "mobility_x_weekday",
        "mobility_x_badnight",
        "mobility_x_sensor",
        "mobility_x_routine_fragment",
    ],
    "mobility_routebook": [
        "h005_H0704_z",
        "h005_H0774_z",
        "h005_H0646_z",
        "h005_H0568_z",
        "h005_H0562_z",
        "h005_H0094_z",
        "h005_mobility_teacher_z",
        "h005_support_teacher_z",
        "jepa_mobility_low_energy",
        "mobility_x_sensor",
    ],
}


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def rank01(values: np.ndarray | pd.Series, ref_mask: np.ndarray | None = None) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if ref_mask is None:
        ref = s
    else:
        ref = s.iloc[np.asarray(ref_mask, dtype=bool)]
    if ref.nunique(dropna=False) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    return pd.concat([ref, s], ignore_index=True).rank(method="average", pct=True).iloc[len(ref) :].to_numpy(dtype=np.float64)


def robust_z(values: np.ndarray | pd.Series, train_mask: np.ndarray) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    ref = s.iloc[train_mask]
    med = float(ref.median())
    q25 = float(ref.quantile(0.25))
    q75 = float(ref.quantile(0.75))
    scale = (q75 - q25) / 1.349
    if not np.isfinite(scale) or scale < 1.0e-9:
        scale = float(ref.std(ddof=0))
    if not np.isfinite(scale) or scale < 1.0e-9:
        return np.zeros(len(s), dtype=np.float64)
    return ((s - med) / scale).clip(-8.0, 8.0).to_numpy(dtype=np.float64)


def normalize_sample_keys(sample: pd.DataFrame) -> pd.DataFrame:
    out = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    return out.reset_index(drop=True)


def h005_state_score(
    hyp_id: str,
    h005_results: pd.DataFrame,
    base: pd.DataFrame,
    z_features: pd.DataFrame,
    episodes: pd.DataFrame,
    pool: dict[str, tuple[str, str]],
    train_mask: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    rows = h005_results[h005_results["hypothesis_id"].astype(str).eq(str(hyp_id))]
    if rows.empty:
        raise KeyError(f"missing H005 hypothesis id: {hyp_id}")
    hyp = rows.iloc[0]
    score, meta = h005.make_hypothesis_score(hyp, z_features, episodes, pool, train_mask)
    gate, gate_tags, gate_relaxed = h005.condition_gate(hyp, base, episodes, z_features, train_mask)
    meta.update(
        {
            "hypothesis_id": hyp_id,
            "hidden_human_state": hyp["hidden_human_state"],
            "route_key": hyp["route_key"],
            "gate_tags": gate_tags,
            "gate_relaxed": gate_relaxed,
            "h005_avg_delta": float(hyp.get("avg_delta", np.nan)),
            "h005_worst_delta": float(hyp.get("worst_delta", np.nan)),
            "train_gate_rows": int((gate & train_mask).sum()),
            "test_gate_rows": int((gate & ~train_mask).sum()),
        }
    )
    return np.asarray(score, dtype=np.float64), meta


def oof_ridge_state(context: pd.DataFrame, teacher: np.ndarray, base: pd.DataFrame, train_mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    train = base.loc[train_mask].reset_index(drop=True)
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    full_test_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
    x_train = context.iloc[train_mask].reset_index(drop=True)
    x_test = context.iloc[full_test_idx].reset_index(drop=True)
    y = np.asarray(teacher, dtype=np.float64)[train_mask]
    pred_train = np.zeros(len(train), dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups_for(train, "subject5").reset_index(drop=True)):
        model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=12.0))
        model.fit(x_train.iloc[tr_idx], y[tr_idx])
        pred_train[va_idx] = model.predict(x_train.iloc[va_idx])
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=12.0))
    model.fit(x_train, y)
    pred_test = np.asarray(model.predict(x_test), dtype=np.float64)
    return pred_train, pred_test


def build_latent_features() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not H005_TEST.exists():
        raise FileNotFoundError(f"run H005 first: {H005_TEST}")
    h005_results = pd.read_csv(H005_TEST)
    base, _, _, feature_frames = load_frames()
    episodes, episode_defs = build_episode_matrix(base, feature_frames)
    train_mask = base["split"].eq("train").to_numpy()
    pool = h005.build_feature_pool(feature_frames)
    z_features = h005.build_z_feature_matrix(base, feature_frames, pool, train_mask)

    state_cols: dict[str, np.ndarray] = {}
    meta_rows: list[dict[str, Any]] = []
    for hyp_id in ALL_STATE_IDS:
        score, meta = h005_state_score(hyp_id, h005_results, base, z_features, episodes, pool, train_mask)
        state_cols[f"h005_{hyp_id}_z"] = robust_z(score, train_mask)
        state_cols[f"h005_{hyp_id}_rank"] = rank01(score, train_mask)
        meta_rows.append(meta)

    mobility_stack = np.vstack([state_cols[f"h005_{hyp_id}_z"] for hyp_id in MOBILITY_IDS])
    support_stack = np.vstack([state_cols[f"h005_{hyp_id}_z"] for hyp_id in SUPPORT_IDS])
    teacher = robust_z(np.mean(mobility_stack, axis=0), train_mask)
    support_teacher = robust_z(np.mean(support_stack, axis=0), train_mask)
    state_cols["h005_mobility_teacher_z"] = teacher
    state_cols["h005_mobility_teacher_rank"] = rank01(teacher, train_mask)
    state_cols["h005_support_teacher_z"] = support_teacher
    state_cols["h005_support_teacher_rank"] = rank01(support_teacher, train_mask)
    state_cols["h005_mobility_high"] = (state_cols["h005_mobility_teacher_rank"] >= 0.82).astype(float)

    context_episode_cols = [
        "bedtime_arousal",
        "routine_fragmentation",
        "routine_anchor_recovery",
        "home_recovery",
        "badnight_aftereffect",
        "measurement_wear_confidence",
        "physiology_strain",
        "cashflow_stress",
        "cashflow_relief_spend",
    ]
    context = pd.concat(
        [
            base_label_matrix(base).reset_index(drop=True),
            episodes[[c for c in context_episode_cols if c in episodes.columns]].reset_index(drop=True).add_prefix("ctx_episode_"),
        ],
        axis=1,
    )
    pred_train, pred_test = oof_ridge_state(context, teacher, base, train_mask)
    full_pred = np.zeros(len(base), dtype=np.float64)
    full_pred[train_mask] = pred_train
    test_sorted_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
    full_pred[test_sorted_idx] = pred_test
    energy = np.abs(teacher - full_pred)
    state_cols["jepa_mobility_pred_z"] = robust_z(full_pred, train_mask)
    state_cols["jepa_mobility_residual_z"] = robust_z(teacher - full_pred, train_mask)
    state_cols["jepa_mobility_energy"] = robust_z(energy, train_mask)
    low_energy = state_cols["h005_mobility_teacher_rank"] * (1.0 - rank01(energy, train_mask))
    state_cols["jepa_mobility_low_energy"] = robust_z(low_energy, train_mask)
    agree = teacher * full_pred
    state_cols["jepa_mobility_agreement"] = robust_z(agree, train_mask)

    for episode in ["badnight_aftereffect", "measurement_wear_confidence", "routine_fragmentation"]:
        if episode in episodes.columns:
            state_cols[f"episode_{episode}_z"] = robust_z(episodes[episode].to_numpy(dtype=np.float64), train_mask)

    is_weekend = base["is_weekend"].to_numpy(dtype=float)
    state_cols["mobility_x_weekend"] = robust_z(teacher * is_weekend, train_mask)
    state_cols["mobility_x_weekday"] = robust_z(teacher * (1.0 - is_weekend), train_mask)
    state_cols["mobility_x_badnight"] = robust_z(teacher * episodes["badnight_aftereffect"].to_numpy(dtype=np.float64), train_mask)
    state_cols["mobility_x_sensor"] = robust_z(teacher * episodes["measurement_wear_confidence"].to_numpy(dtype=np.float64), train_mask)
    state_cols["mobility_x_routine_fragment"] = robust_z(teacher * episodes["routine_fragmentation"].to_numpy(dtype=np.float64), train_mask)

    latent = pd.concat([base[KEYS + ["split", "dateblock_group", "weekday", "is_weekend"] + TARGETS].reset_index(drop=True), pd.DataFrame(state_cols)], axis=1)
    latent.to_parquet(LATENT_OUT, index=False)
    pd.DataFrame(meta_rows).to_csv(FEATURE_META_OUT, index=False)
    return base, latent, episodes, pd.DataFrame(meta_rows)


def oof_predict_binary(x: pd.DataFrame, y: np.ndarray, groups: pd.Series, c_value: float) -> np.ndarray:
    pred = np.zeros(len(y), dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        y_tr = y[tr_idx]
        if len(np.unique(y_tr)) < 2:
            pred[va_idx] = float(np.mean(y_tr))
            continue
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=float(c_value), max_iter=1800, solver="lbfgs"),
        )
        model.fit(x.iloc[tr_idx], y_tr)
        pred[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return clip_prob(pred)


def full_predict_binary(x_train: pd.DataFrame, y: np.ndarray, x_test: pd.DataFrame, c_value: float) -> np.ndarray:
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=float(c_value), max_iter=1800, solver="lbfgs"),
    )
    model.fit(x_train, y)
    return clip_prob(model.predict_proba(x_test)[:, 1])


def shuffle_added(add: pd.DataFrame, train: pd.DataFrame, mode: str, rng: np.random.Generator) -> pd.DataFrame:
    out = add.copy().reset_index(drop=True)
    if mode == "row":
        return out.iloc[rng.permutation(len(out))].reset_index(drop=True)
    group_col = "subject_id" if mode == "subject" else "dateblock_group"
    pieces = []
    for _, idx in train.reset_index().groupby(group_col)["index"]:
        idx_arr = idx.to_numpy(dtype=int)
        vals = out.iloc[idx_arr].copy()
        if len(vals) > 1:
            vals.iloc[:, :] = vals.iloc[rng.permutation(len(vals))].to_numpy()
        pieces.append(vals)
    return pd.concat(pieces).sort_index().reset_index(drop=True)


def evaluate_feature_sets(base: pd.DataFrame, latent: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    train = base[base["split"].eq("train")].reset_index(drop=True)
    train_mask = base["split"].eq("train").to_numpy()
    y = train[TARGET].to_numpy(dtype=int)
    base_x = base_label_matrix(train).reset_index(drop=True)
    latent_train = latent.loc[train_mask].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    pred_cache: dict[str, np.ndarray] = {}
    rng = np.random.default_rng(RNG_SEED)

    for feature_set, cols in FEATURE_SETS.items():
        add = latent_train[cols].astype(float).reset_index(drop=True)
        for c_value in CS:
            for split_name in ["subject5", "dateblock5"]:
                groups = groups_for(train, split_name).reset_index(drop=True)
                base_pred = oof_predict_binary(base_x, y, groups, c_value)
                plus_x = pd.concat([base_x, add], axis=1)
                plus_pred = oof_predict_binary(plus_x, y, groups, c_value)
                base_loss = float(log_loss(y, base_pred, labels=[0, 1]))
                plus_loss = float(log_loss(y, plus_pred, labels=[0, 1]))
                delta = plus_loss - base_loss
                key = f"{feature_set}|C{c_value:g}|{split_name}|plus"
                pred_cache[key] = plus_pred
                pred_cache[f"{feature_set}|C{c_value:g}|{split_name}|base"] = base_pred

                null_deltas: list[float] = []
                for mode in ["row", "subject", "dateblock"]:
                    for rep in range(NULL_REPS):
                        shuf = shuffle_added(add, train, mode, rng)
                        null_x = pd.concat([base_x, shuf], axis=1)
                        null_pred = oof_predict_binary(null_x, y, groups, c_value)
                        null_loss = float(log_loss(y, null_pred, labels=[0, 1]))
                        ndelta = null_loss - base_loss
                        null_deltas.append(ndelta)
                        null_rows.append(
                            {
                                "feature_set": feature_set,
                                "C": c_value,
                                "split": split_name,
                                "mode": mode,
                                "rep": rep,
                                "base_loss": base_loss,
                                "null_loss": null_loss,
                                "null_delta": ndelta,
                            }
                        )
                null_arr = np.asarray(null_deltas, dtype=np.float64)
                rows.append(
                    {
                        "feature_set": feature_set,
                        "C": c_value,
                        "split": split_name,
                        "n_added_features": len(cols),
                        "base_loss": base_loss,
                        "plus_loss": plus_loss,
                        "delta_logloss": delta,
                        "null_median_delta": float(np.median(null_arr)),
                        "null_p10_delta": float(np.quantile(null_arr, 0.10)),
                        "null_dominance": float(np.mean(delta < null_arr)),
                        "beats_base": bool(delta < 0.0),
                    }
                )
    ablation = pd.DataFrame(rows)
    summary = (
        ablation.groupby(["feature_set", "C"])
        .agg(
            splits=("split", "count"),
            mean_delta=("delta_logloss", "mean"),
            worst_delta=("delta_logloss", "max"),
            subject5_delta=("delta_logloss", lambda s: float(s.iloc[0])),
            dateblock5_delta=("delta_logloss", lambda s: float(s.iloc[1]) if len(s) > 1 else np.nan),
            min_null_dominance=("null_dominance", "min"),
            mean_null_dominance=("null_dominance", "mean"),
        )
        .reset_index()
    )
    ablation = ablation.merge(summary, on=["feature_set", "C"], how="left", suffixes=("", "_summary"))
    ablation = ablation.sort_values(["worst_delta", "mean_delta", "min_null_dominance"], ascending=[True, True, False]).reset_index(drop=True)
    nulls = pd.DataFrame(null_rows)
    ablation.to_csv(ABLATION_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    return ablation, nulls, pred_cache


def choose_model(ablation: pd.DataFrame) -> dict[str, Any]:
    summary_cols = ["feature_set", "C", "mean_delta", "worst_delta", "min_null_dominance", "mean_null_dominance"]
    summary = ablation[summary_cols].drop_duplicates().copy()
    robust = summary[(summary["worst_delta"] < 0.0) & (summary["min_null_dominance"] >= 0.55)]
    if robust.empty:
        robust = summary[(summary["mean_delta"] < 0.0) & (summary["mean_null_dominance"] >= 0.55)]
    if robust.empty:
        robust = summary
    row = robust.sort_values(["worst_delta", "mean_delta", "min_null_dominance"], ascending=[True, True, False]).iloc[0]
    return {"feature_set": str(row["feature_set"]), "C": float(row["C"])}


def build_test_delta(base: pd.DataFrame, latent: pd.DataFrame, chosen: dict[str, Any]) -> tuple[np.ndarray, pd.DataFrame]:
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    test_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
    y = train[TARGET].to_numpy(dtype=int)
    base_x_train = base_label_matrix(train).reset_index(drop=True)
    base_x_test = base_label_matrix(test).reset_index(drop=True)
    cols = FEATURE_SETS[str(chosen["feature_set"])]
    add_train = latent.loc[train_mask, cols].astype(float).reset_index(drop=True)
    add_test = latent.loc[test_idx, cols].astype(float).reset_index(drop=True)
    c_value = float(chosen["C"])
    base_pred = full_predict_binary(base_x_train, y, base_x_test, c_value)
    plus_pred = full_predict_binary(pd.concat([base_x_train, add_train], axis=1), y, pd.concat([base_x_test, add_test], axis=1), c_value)
    delta = logit(plus_pred) - logit(base_pred)
    test_state = latent.loc[test_idx, KEYS + [
        "h005_mobility_teacher_z",
        "h005_mobility_teacher_rank",
        "jepa_mobility_pred_z",
        "jepa_mobility_energy",
        "jepa_mobility_low_energy",
    ]].reset_index(drop=True)
    test_state["model_delta_logit"] = delta
    test_state["model_delta_rank"] = rank01(delta)
    test_state["positive_delta"] = np.maximum(delta, 0.0)
    return delta, test_state


def candidate_specs() -> list[dict[str, Any]]:
    return [
        {"candidate_id": "s4latent_pos_top20_a018_cap008", "mode": "pos", "top_k": 20, "alpha": 0.18, "cap": 0.0080, "rank": "consensus"},
        {"candidate_id": "s4latent_pos_top36_a015_cap006", "mode": "pos", "top_k": 36, "alpha": 0.15, "cap": 0.0060, "rank": "consensus"},
        {"candidate_id": "s4latent_pos_top50_a012_cap005", "mode": "pos", "top_k": 50, "alpha": 0.12, "cap": 0.0050, "rank": "consensus"},
        {"candidate_id": "s4latent_pos_top50_a024_cap010", "mode": "pos", "top_k": 50, "alpha": 0.24, "cap": 0.0100, "rank": "consensus"},
        {"candidate_id": "s4latent_pos_top80_a014_cap006", "mode": "pos", "top_k": 80, "alpha": 0.14, "cap": 0.0060, "rank": "consensus"},
        {"candidate_id": "s4latent_pos_top80_a020_cap008", "mode": "pos", "top_k": 80, "alpha": 0.20, "cap": 0.0080, "rank": "consensus"},
        {"candidate_id": "s4latent_lowenergy_top28_a016_cap006", "mode": "pos", "top_k": 28, "alpha": 0.16, "cap": 0.0060, "rank": "lowenergy"},
        {"candidate_id": "s4latent_lowenergy_top60_a018_cap008", "mode": "pos", "top_k": 60, "alpha": 0.18, "cap": 0.0080, "rank": "lowenergy"},
        {"candidate_id": "s4latent_signed_top40_a008_cap004", "mode": "signed", "top_k": 40, "alpha": 0.08, "cap": 0.0040, "rank": "absdelta"},
        {"candidate_id": "s4latent_signed_top80_a010_cap006", "mode": "signed", "top_k": 80, "alpha": 0.10, "cap": 0.0060, "rank": "absdelta"},
        {"candidate_id": "s4latent_down_control_top28_a016_cap006", "mode": "down_control", "top_k": 28, "alpha": 0.16, "cap": 0.0060, "rank": "lowenergy"},
    ]


def select_rows(test_state: pd.DataFrame, spec: dict[str, Any]) -> np.ndarray:
    if spec["rank"] == "lowenergy":
        score = rank01(test_state["jepa_mobility_low_energy"]) + 0.35 * rank01(test_state["positive_delta"])
    elif spec["rank"] == "absdelta":
        score = rank01(np.abs(test_state["model_delta_logit"]))
    else:
        score = 0.55 * rank01(test_state["h005_mobility_teacher_rank"]) + 0.45 * rank01(test_state["positive_delta"])
    k = int(min(max(int(spec["top_k"]), 1), len(score)))
    order = np.argsort(score)
    selected = np.zeros(len(score), dtype=bool)
    selected[order[-k:]] = True
    return selected


def write_candidate(base_sub: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base_sub[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = H007 / f"submission_h007_{safe_id(candidate_id, 90)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(base: pd.DataFrame, test_delta: np.ndarray, test_state: pd.DataFrame) -> tuple[pd.DataFrame, list[Path]]:
    train_mask = base["split"].eq("train").to_numpy()
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    sample = normalize_sample_keys(test[KEYS])
    base_sub = load_anchor_sub(E247, sample)
    base_prob = base_sub[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)

    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in candidate_specs():
        selected = select_rows(test_state, spec)
        move_s4 = np.zeros(len(test_state), dtype=np.float64)
        raw = np.asarray(test_delta, dtype=np.float64)
        if spec["mode"] == "pos":
            move_s4[selected] = np.clip(float(spec["alpha"]) * np.maximum(raw[selected], 0.0), 0.0, float(spec["cap"]))
        elif spec["mode"] == "signed":
            move_s4[selected] = np.clip(float(spec["alpha"]) * raw[selected], -float(spec["cap"]), float(spec["cap"]))
        elif spec["mode"] == "down_control":
            move_s4[selected] = -np.clip(float(spec["alpha"]) * np.maximum(raw[selected], 0.0), 0.0, float(spec["cap"]))
        else:
            raise ValueError(str(spec["mode"]))
        logits = base_logit.copy()
        logits[:, TIDX] += move_s4
        path = write_candidate(base_sub, logits, str(spec["candidate_id"]))
        paths.append(path)
        rows.append(
            {
                "candidate_id": spec["candidate_id"],
                "file": rel(path),
                "basename": path.name,
                "mode": spec["mode"],
                "rank": spec["rank"],
                "top_k": int(spec["top_k"]),
                "alpha": float(spec["alpha"]),
                "cap": float(spec["cap"]),
                "changed_rows": int((np.abs(move_s4) > EPS).sum()),
                "changed_cells": int((np.abs(move_s4) > EPS).sum()),
                "mean_abs_logit_move": float(np.mean(np.abs(move_s4))),
                "l1_logit_move": float(np.sum(np.abs(move_s4))),
                "max_abs_logit_move": float(np.max(np.abs(move_s4))),
                "max_abs_prob_delta": float(np.max(np.abs(sigmoid(logits)[:, TIDX] - base_prob[:, TIDX]))),
                "selected_delta_mean": float(np.mean(raw[selected])) if int(selected.sum()) else np.nan,
                "selected_mobility_rank_mean": float(test_state.loc[selected, "h005_mobility_teacher_rank"].mean()) if int(selected.sum()) else np.nan,
            }
        )
    candidates = pd.DataFrame(rows)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths


def score_new_candidates(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [str(path.resolve()) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    base = load_anchor_sub(E247, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    h003_move = None
    if H003_TINY.exists():
        h003 = load_anchor_sub(H003_TINY, sample)
        h003_move = logit(h003[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_anchor_sub(path, sample)
        prob = cand[TARGETS].to_numpy(dtype=np.float64)
        move = logit(prob) - base_logit
        rec: dict[str, Any] = {
            "file": rel(path),
            "basename": path.name,
            "changed_rows_vs_current": int((np.abs(move).max(axis=1) > EPS).sum()),
            "changed_cells_vs_current": int((np.abs(move) > EPS).sum()),
            "mean_abs_logit_delta_vs_current": float(np.mean(np.abs(move))),
            "l1_logit_delta_vs_current": float(np.sum(np.abs(move))),
            "max_abs_logit_delta_vs_current": float(np.max(np.abs(move))),
            "max_abs_prob_delta_vs_current": float(np.max(np.abs(prob - base_prob))),
        }
        for ti, target in enumerate(TARGETS):
            rec[f"changed_{target}"] = int((np.abs(move[:, ti]) > EPS).sum())
        if h003_move is not None:
            denom = float(np.linalg.norm(move) * np.linalg.norm(h003_move) + EPS)
            rec["cos_delta_with_h003_tiny"] = float(np.sum(move * h003_move) / denom)
            rec["l1_ratio_to_h003_tiny"] = float(np.sum(np.abs(move)) / (np.sum(np.abs(h003_move)) + EPS))
        rows.append(rec)
    anatomy = pd.DataFrame(rows).sort_values(["l1_logit_delta_vs_current", "basename"]).reset_index(drop=True)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return anatomy


def build_gate_scores(candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame) -> pd.DataFrame:
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "strict_promote_gate",
        "info_sensor_gate",
        "below_resolution_gate",
        "block_gate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
    ]
    present_score_cols = [col for col in score_cols if col in scores.columns]
    merged = candidates.merge(scores[present_score_cols], on="basename", how="left")
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    present_anatomy_cols = [col for col in anatomy_cols if col in anatomy.columns]
    merged = merged.merge(anatomy[present_anatomy_cols], on="basename", how="left")
    ratio = merged.get("l1_ratio_to_h003_tiny", pd.Series(0.0, index=merged.index)).fillna(0.0)
    merged["shape_gate"] = (
        (merged["changed_cells"] <= 70)
        & (merged["max_abs_prob_delta"] <= 0.0020)
        & (ratio <= 0.25)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.020)
    )
    merged["h007_strict_upload_gate"] = merged["shape_gate"] & merged["strict_promote_gate"].fillna(False).astype(bool)
    merged["h007_info_gate"] = merged["shape_gate"] & (
        merged["info_sensor_gate"].fillna(False).astype(bool)
        | (
            (merged["pred_delta_vs_current_mean"] < 0.0)
            & (merged["pred_beats_current_rate"] >= 0.55)
            & (merged["incremental_bad_axis_vs_current"].abs() <= 0.025)
        )
    )
    merged["h007_decision"] = np.select(
        [
            merged["h007_strict_upload_gate"],
            merged["h007_info_gate"] & ~merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["h007_info_gate"] & merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["shape_gate"],
        ],
        [
            "uploadsafe_candidate",
            "diagnostic_public_sensor_only",
            "too_small_to_submit",
            "shape_ok_but_selector_rejects",
        ],
        default="reject_shape_or_bad_axis",
    )
    gate = merged.sort_values(
        ["h007_strict_upload_gate", "h007_info_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)
    gate.to_csv(GATE_OUT, index=False)
    return gate


def write_uploadsafe_files(gate_scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in gate_scores[gate_scores["h007_strict_upload_gate"].astype(bool)].to_dict("records"):
        src = ROOT / str(rec["file"])
        if not src.exists():
            src = H007 / str(rec["basename"])
        dst = H007 / src.name.replace(".csv", "_uploadsafe.csv")
        shutil.copyfile(src, dst)
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "basename": dst.name,
                "file": rel(dst),
                "reason": "passed H007 strict selector + movement-shape gate",
            }
        )
    selection = pd.DataFrame(rows)
    selection.to_csv(SELECTION_OUT, index=False)
    return selection


def write_report(
    feature_meta: pd.DataFrame,
    ablation: pd.DataFrame,
    nulls: pd.DataFrame,
    chosen: dict[str, Any],
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
    gate_scores: pd.DataFrame,
    selection: pd.DataFrame,
) -> None:
    summary_cols = [
        "feature_set",
        "C",
        "split",
        "n_added_features",
        "base_loss",
        "plus_loss",
        "delta_logloss",
        "null_median_delta",
        "null_dominance",
        "mean_delta",
        "worst_delta",
        "min_null_dominance",
    ]
    gate_cols = [
        "candidate_id",
        "h007_decision",
        "mode",
        "rank",
        "changed_cells",
        "max_abs_prob_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "shape_gate",
        "h007_strict_upload_gate",
        "h007_info_gate",
        "basename",
    ]
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    meta_cols = [
        "hypothesis_id",
        "hidden_human_state",
        "route_key",
        "h005_avg_delta",
        "h005_worst_delta",
        "matched_feature_count",
        "fallback_episodes",
    ]
    strict_n = int(gate_scores["h007_strict_upload_gate"].sum())
    info_n = int(gate_scores["h007_info_gate"].sum())
    robust_rows = ablation[["feature_set", "C", "mean_delta", "worst_delta", "min_null_dominance"]].drop_duplicates()
    robust_pass = robust_rows[(robust_rows["worst_delta"] < 0.0) & (robust_rows["min_null_dominance"] >= 0.55)]
    lines = [
        "# H007 S4 Mobility Latent Model",
        "",
        "## Question",
        "",
        "Does the H006 S4 mobility signal become useful when used as an internal HS-JEPA latent feature rather than a direct postprocess?",
        "",
        "## Chosen Downstream Model",
        "",
        f"- feature_set: `{chosen['feature_set']}`",
        f"- C: `{chosen['C']}`",
        f"- robust feature-set passes: `{len(robust_pass)}`",
        "",
        "## S4 Feature Ablation",
        "",
        md_table(ablation[[col for col in summary_cols if col in ablation.columns]], n=50, floatfmt=".9f"),
        "",
        "## Feature Sources",
        "",
        md_table(feature_meta[[col for col in meta_cols if col in feature_meta.columns]], n=20, floatfmt=".9f"),
        "",
        "## Candidate Gate",
        "",
        md_table(gate_scores[[col for col in gate_cols if col in gate_scores.columns]], n=30, floatfmt=".9f"),
        "",
        "## Selector Scores",
        "",
        md_table(scores[[col for col in score_cols if col in scores.columns]], n=30, floatfmt=".9f"),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[[col for col in anatomy_cols if col in anatomy.columns]], n=30, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=20, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    if len(robust_pass):
        best = robust_pass.sort_values(["worst_delta", "mean_delta"], ascending=[True, True]).iloc[0]
        lines.append(
            f"The mobility latent is locally real for S4: best robust feature set `{best['feature_set']}` improves both splits with worst delta `{float(best['worst_delta']):.9f}`."
        )
    else:
        lines.append(
            "The mobility latent did not pass the strict both-split/null gate as a supervised S4 feature. It remains a weak direction sensor, not a robust model input."
        )
    if strict_n:
        best = gate_scores[gate_scores["h007_strict_upload_gate"].astype(bool)].iloc[0]
        lines.append(f"`{strict_n}` candidate(s) passed strict upload gate. Best file: `{best['basename']}`.")
    elif info_n:
        best = gate_scores[gate_scores["h007_info_gate"].astype(bool)].iloc[0]
        lines.append(f"No strict upload candidate. Best diagnostic sensor: `{best['basename']}`.")
    else:
        lines.append("No candidate passed the H007 info gate. Do not submit these without a new reason.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(LATENT_OUT)}`",
            f"- `{rel(FEATURE_META_OUT)}`",
            f"- `{rel(ABLATION_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(ANATOMY_OUT)}`",
            f"- `{rel(GATE_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, latent, _, feature_meta = build_latent_features()
    ablation, nulls, _ = evaluate_feature_sets(base, latent)
    chosen = choose_model(ablation)
    test_delta, test_state = build_test_delta(base, latent, chosen)
    candidates, paths = materialize_candidates(base, test_delta, test_state)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths)
    gate_scores = build_gate_scores(candidates, scores, anatomy)
    selection = write_uploadsafe_files(gate_scores)
    write_report(feature_meta, ablation, nulls, chosen, candidates, scores, anatomy, gate_scores, selection)

    print(f"report={rel(REPORT_OUT)}")
    print("[chosen]", chosen)
    print("[best ablation]")
    print(
        ablation[
            [
                "feature_set",
                "C",
                "split",
                "delta_logloss",
                "null_median_delta",
                "null_dominance",
                "mean_delta",
                "worst_delta",
                "min_null_dominance",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )
    print("[h007 gate]")
    print(
        gate_scores[
            [
                "candidate_id",
                "h007_decision",
                "changed_cells",
                "max_abs_prob_delta",
                "pred_delta_vs_current_mean",
                "pred_delta_vs_current_p90",
                "pred_beats_current_rate",
                "incremental_bad_axis_vs_current",
                "basename",
            ]
        ]
        .round(9)
        .to_string(index=False)
    )
    if not selection.empty:
        print("[uploadsafe]")
        print(selection.to_string(index=False))


if __name__ == "__main__":
    main()
