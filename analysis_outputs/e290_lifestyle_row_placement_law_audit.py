#!/usr/bin/env python3
"""E290: lifestyle row-placement law audit.

E289 showed that Q3/S4 lifestyle slices are real on train, but direct
materialization fails because matched row/subject/dateblock shuffles look just
as good. This experiment changes the target:

    lifestyle slice -> "which rows should receive this slice?"

The placement target is defined from train OOF row benefit. A candidate is
allowed to move E247 only if its placement law beats train matched nulls and
then beats E247-current matched null submissions.

No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e290_lifestyle_row_placement_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    build_context_views,
    build_story_matrix,
    clip_prob,
    fit_predict_test,
    groups_for,
    load_frames,
    make_latent,
    md_table,
    oof_multi_ridge,
    stable_seed,
)
from e289_target_specific_lifestyle_slice_audit import (  # noqa: E402
    CAP,
    SLICE_OUT,
    base_label_matrix_all,
    cluster6,
    normalize_keys,
    prep_test_meta,
    rep_frames,
)
from public_anchor_bottleneck_decomposition import KEYS, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", message="Inconsistent values: penalty=l1.*", category=UserWarning)

RNG_SEED = 20260531 + 290
N_TRAIN_NULL_REPS = 32
N_TEST_NULL_REPS = 5
MAX_POLICIES = 12
TOP_FRACS = [0.15, 0.25, 0.35, 0.50, 0.70]
SCALES = [0.25, 0.50]
DELTA_MODES = ["raw", "centered"]

PLACEMENT_OUT = OUT / "e290_lifestyle_row_placement_train_summary.csv"
CANDIDATE_OUT = OUT / "e290_lifestyle_row_placement_candidate_summary.csv"
GOVERNOR_OUT = OUT / "e290_lifestyle_row_placement_governor_summary.csv"
SCORE_OUT = OUT / "e290_lifestyle_row_placement_scores.csv"
NULL_MAP_OUT = OUT / "e290_lifestyle_row_placement_null_map.csv"
REPORT_OUT = OUT / "e290_lifestyle_row_placement_report.md"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_id(text: str, limit: int = 92) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def cell_nll(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    p = clip_prob(p)
    y = np.asarray(y, dtype=np.float64)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def folds_for(groups: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    n_splits = min(5, int(groups.nunique()))
    if n_splits < 2:
        return []
    return list(GroupKFold(n_splits=n_splits).split(np.zeros(len(groups)), groups=groups.astype(str).to_numpy()))


def prob_model() -> Pipeline:
    return make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.35, max_iter=1200, solver="lbfgs"),
    )


def oof_prob(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> np.ndarray:
    pred = np.full(len(y), np.nan, dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        y_tr = y[tr_idx]
        if len(np.unique(y_tr)) < 2:
            pred[va_idx] = float(np.mean(y_tr))
            continue
        model = prob_model()
        model.fit(x.iloc[tr_idx], y_tr)
        pred[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return clip_prob(np.nan_to_num(pred, nan=float(np.mean(y))))


def fit_predict_prob(x_train: pd.DataFrame, y_train: np.ndarray, x_test: pd.DataFrame) -> np.ndarray:
    x_train, x_test = align_columns(x_train, x_test)
    model = prob_model()
    model.fit(x_train, y_train)
    return clip_prob(model.predict_proba(x_test)[:, 1])


def align_columns(x_train: pd.DataFrame, x_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = sorted(set(x_train.columns) | set(x_test.columns))
    return x_train.reindex(columns=cols, fill_value=0.0), x_test.reindex(columns=cols, fill_value=0.0)


def make_gate_model(model_name: str):
    if model_name == "lr_l2":
        return Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                ("clf", LogisticRegression(C=0.35, max_iter=1600, solver="lbfgs", class_weight="balanced")),
            ]
        )
    if model_name == "lr_l1":
        return Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.14,
                        max_iter=1600,
                        solver="liblinear",
                        penalty="l1",
                        class_weight="balanced",
                    ),
                ),
            ]
        )
    if model_name == "hgb_shallow":
        return Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                (
                    "clf",
                    HistGradientBoostingClassifier(
                        learning_rate=0.045,
                        max_leaf_nodes=9,
                        min_samples_leaf=12,
                        l2_regularization=0.08,
                        max_iter=120,
                        random_state=RNG_SEED,
                    ),
                ),
            ]
        )
    raise ValueError(model_name)


def crossfit_gate_score(x: pd.DataFrame, y: np.ndarray, groups: pd.Series, model_name: str) -> np.ndarray:
    score = np.full(len(y), np.nan, dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        y_tr = y[tr_idx]
        if len(np.unique(y_tr)) < 2:
            score[va_idx] = float(np.mean(y_tr))
            continue
        model = make_gate_model(model_name)
        model.fit(x.iloc[tr_idx], y_tr)
        score[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return np.nan_to_num(score, nan=float(np.mean(y)))


def score_metrics(y: np.ndarray, score: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=int)
    prev = float(np.mean(y))
    if len(np.unique(y)) < 2:
        return {"prevalence": prev, "auc": np.nan, "ap": np.nan, "ap_lift": np.nan}
    ap = float(average_precision_score(y, score))
    return {"prevalence": prev, "auc": float(roc_auc_score(y, score)), "ap": ap, "ap_lift": ap - prev}


def add_rank_features(x: pd.DataFrame, groups: pd.Series, cols: list[str], prefix: str) -> pd.DataFrame:
    out = x.copy()
    g = groups.astype(str).reset_index(drop=True)
    for col in cols:
        vals = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
        out[f"{prefix}_{col}_rank"] = vals.groupby(g).rank(pct=True).fillna(0.5).to_numpy(dtype=np.float64)
    return out


def row_features(
    row_base: pd.DataFrame,
    rep: pd.DataFrame,
    target: str,
    base_prob: np.ndarray,
    aug_prob: np.ndarray,
    frame: pd.DataFrame,
) -> pd.DataFrame:
    base = row_base.reset_index(drop=True).copy()
    rep_x = rep.reset_index(drop=True).add_prefix("life_")
    delta = np.clip(logit(aug_prob) - logit(base_prob), -CAP, CAP)
    x = pd.concat([base, rep_x], axis=1)
    x["model_base_prob"] = base_prob
    x["model_aug_prob"] = aug_prob
    x["model_delta"] = delta
    x["model_abs_delta"] = np.abs(delta)
    x["model_delta_pos"] = np.maximum(delta, 0.0)
    x["model_delta_neg"] = np.maximum(-delta, 0.0)
    for col in ["weekday", "is_weekend", "subject_order", "lifelog_dom", "lifelog_month"]:
        if col in frame.columns and pd.api.types.is_numeric_dtype(frame[col]):
            x[f"meta_{col}"] = pd.to_numeric(frame[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    x["target_is_q"] = float(str(target).startswith("Q"))
    x["target_is_s"] = float(str(target).startswith("S"))
    x[f"target_{target}"] = 1.0
    x = add_rank_features(x, frame["subject_id"], ["model_base_prob", "model_aug_prob", "model_delta", "model_abs_delta"], "subj")
    x = add_rank_features(x, frame["dateblock_group"], ["model_base_prob", "model_aug_prob", "model_delta", "model_abs_delta"], "dateblock")
    return x.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def shuffle_scores(score: np.ndarray, mode: str, groups: pd.Series, rng: np.random.Generator) -> np.ndarray:
    values = np.asarray(score, dtype=np.float64)
    if mode == "row":
        return values[rng.permutation(len(values))]
    out = values.copy()
    for _, idx in groups.astype(str).groupby(groups.astype(str)).indices.items():
        idx_arr = np.asarray(idx, dtype=int)
        if len(idx_arr) > 1:
            out[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
    return out


def gated_target_delta(
    y: np.ndarray,
    base_prob: np.ndarray,
    aug_prob: np.ndarray,
    score: np.ndarray,
    top_frac: float,
    score_threshold: float | None = None,
) -> tuple[float, np.ndarray]:
    n_select = max(1, int(round(len(score) * float(top_frac))))
    selected = np.zeros(len(score), dtype=bool)
    order = np.argsort(score)[::-1]
    selected[order[:n_select]] = True
    if score_threshold is not None:
        selected &= np.asarray(score) >= score_threshold
    pred = np.asarray(base_prob, dtype=np.float64).copy()
    pred[selected] = aug_prob[selected]
    delta = float(log_loss(y, clip_prob(pred), labels=[0, 1]) - log_loss(y, clip_prob(base_prob), labels=[0, 1]))
    return delta, selected


def train_placement_stress(
    y: np.ndarray,
    base_prob: np.ndarray,
    aug_prob: np.ndarray,
    benefit: np.ndarray,
    score: np.ndarray,
    train_df: pd.DataFrame,
    top_frac: float,
    rng: np.random.Generator,
) -> dict[str, float]:
    actual_delta, selected = gated_target_delta(y, base_prob, aug_prob, score, top_frac)
    null_rows = []
    groups = {
        "row": train_df["subject_id"].astype(str),
        "subject": train_df["subject_id"].astype(str),
        "dateblock": train_df["dateblock_group"].astype(str),
    }
    for mode, group in groups.items():
        for rep in range(N_TRAIN_NULL_REPS):
            shuffled = shuffle_scores(score, mode, group, rng)
            null_delta, _ = gated_target_delta(y, base_prob, aug_prob, shuffled, top_frac)
            null_rows.append({"mode": mode, "delta": null_delta})
    null = pd.DataFrame(null_rows)
    null_vals = null["delta"].to_numpy(dtype=np.float64)
    benefit_selected = np.asarray(benefit, dtype=np.float64)[selected]
    out: dict[str, float] = {
        "top_frac": float(top_frac),
        "selected_rows": float(np.count_nonzero(selected)),
        "actual_delta": float(actual_delta),
        "selected_benefit_mean": float(np.mean(benefit_selected)) if len(benefit_selected) else np.nan,
        "selected_good_rate": float(np.mean(benefit_selected < 0.0)) if len(benefit_selected) else np.nan,
        "null_q20": float(np.quantile(null_vals, 0.20)),
        "null_median": float(np.median(null_vals)),
        "null_best": float(np.min(null_vals)),
        "dominance": float(np.mean(actual_delta < null_vals)),
        "placebo_adjusted_vs_median": float(actual_delta - np.median(null_vals)),
    }
    for mode in ["row", "subject", "dateblock"]:
        vals = null.loc[null["mode"].eq(mode), "delta"].to_numpy(dtype=np.float64)
        out[f"{mode}_dominance"] = float(np.mean(actual_delta < vals))
        out[f"{mode}_null_best"] = float(np.min(vals))
    out["train_gate"] = float(
        actual_delta < -0.00020
        and out["dominance"] >= 0.78
        and min(out["row_dominance"], out["subject_dominance"], out["dateblock_dominance"]) >= 0.58
        and actual_delta <= out["null_q20"] - 1.0e-5
    )
    return out


def build_lifestyle_cache() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[tuple[str, str], dict[str, Any]]]:
    base_features, raw, stories, feature_frames = load_frames()
    story_matrix, _story_meta = build_story_matrix(base_features, stories, feature_frames)
    views = build_context_views(base_features, raw)
    train_mask = base_features["split"].eq("train").to_numpy()
    train_df = base_features.loc[train_mask].reset_index(drop=True)
    test_df = base_features.loc[~train_mask].reset_index(drop=True)
    y_story = story_matrix.loc[train_mask].reset_index(drop=True)
    base_train, base_test = base_label_matrix_all(train_df, test_df)
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    for view_id, context in views.items():
        x_train = context.loc[train_mask].reset_index(drop=True)
        x_test = context.loc[~train_mask].reset_index(drop=True)
        for split_name in ["subject5", "dateblock5"]:
            groups = groups_for(train_df, split_name).reset_index(drop=True)
            pred_train = oof_multi_ridge(x_train, y_story, groups)
            pred_test = fit_predict_test(x_train, y_story, x_test)
            train_lat, test_lat, _diag = make_latent(pred_train, pred_test)
            tr_cluster, te_cluster, _cdiag = cluster6(train_lat, test_lat, train_df["subject_id"], view_id, split_name)
            reps = rep_frames(train_lat, test_lat, tr_cluster, te_cluster)
            cache[(view_id, split_name)] = {"reps": reps, "tr_cluster": tr_cluster, "te_cluster": te_cluster}
    return train_df, test_df, base_train, base_test, cache


def selected_slices() -> pd.DataFrame:
    if not SLICE_OUT.exists():
        raise FileNotFoundError(SLICE_OUT)
    slices = pd.read_csv(SLICE_OUT)
    gated = slices[slices["target_gate"].astype(bool)].copy()
    if gated.empty:
        gated = slices.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(8).copy()
    return gated.sort_values(["actual_delta", "dominance"], ascending=[True, False]).reset_index(drop=True)


def train_slice_policy_rows(
    slices: pd.DataFrame,
    train_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    cache: dict[tuple[str, str], dict[str, Any]],
) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    policy_cache: dict[str, dict[str, Any]] = {}
    rng = np.random.default_rng(RNG_SEED)
    for _, sl in slices.iterrows():
        target = str(sl["target"])
        view_id = str(sl["view_id"])
        split_name = str(sl["split"])
        rep_id = str(sl["rep"])
        key = (view_id, split_name)
        rep_train, rep_test = cache[key]["reps"][rep_id]
        groups = groups_for(train_df, split_name).reset_index(drop=True)
        y = train_df[target].to_numpy(dtype=int)
        x_base_tr = base_train.reset_index(drop=True)
        x_aug_tr = pd.concat([x_base_tr, rep_train.reset_index(drop=True)], axis=1)
        x_base_aligned, x_aug_aligned = align_columns(x_base_tr, x_aug_tr)
        base_oof = oof_prob(x_base_aligned, y, groups)
        aug_oof = oof_prob(x_aug_aligned, y, groups)
        benefit = cell_nll(y, aug_oof) - cell_nll(y, base_oof)
        label_defs = {
            "good": benefit < 0.0,
            "strong35": benefit <= float(np.quantile(benefit, 0.35)),
        }
        x_gate = row_features(base_train, rep_train, target, base_oof, aug_oof, train_df)
        for label_name, labels_bool in label_defs.items():
            labels = labels_bool.astype(int)
            if len(np.unique(labels)) < 2:
                continue
            for gate_group in ["subject5", "dateblock5"]:
                gate_groups = groups_for(train_df, gate_group).reset_index(drop=True)
                for model_name in ["lr_l2", "lr_l1", "hgb_shallow"]:
                    score = crossfit_gate_score(x_gate, labels, gate_groups, model_name)
                    metrics = score_metrics(labels, score)
                    base_rec: dict[str, Any] = {
                        "policy_id": f"{target}_{view_id}_{split_name}_{rep_id}_{label_name}_{gate_group}_{model_name}",
                        "slice_id": sl["slice_id"],
                        "target": target,
                        "view_id": view_id,
                        "split": split_name,
                        "rep": rep_id,
                        "label_mode": label_name,
                        "gate_group": gate_group,
                        "model": model_name,
                        "n_rows": int(len(y)),
                        "n_good": int(labels.sum()),
                        "base_loss": float(log_loss(y, base_oof, labels=[0, 1])),
                        "aug_loss": float(log_loss(y, aug_oof, labels=[0, 1])),
                        "full_aug_delta": float(log_loss(y, aug_oof, labels=[0, 1]) - log_loss(y, base_oof, labels=[0, 1])),
                        "benefit_mean": float(np.mean(benefit)),
                        "benefit_good_rate": float(np.mean(benefit < 0.0)),
                        "slice_train_delta": float(sl["actual_delta"]),
                        "slice_train_dominance": float(sl["dominance"]),
                        **metrics,
                    }
                    for top_frac in TOP_FRACS:
                        stress = train_placement_stress(y, base_oof, aug_oof, benefit, score, train_df, top_frac, rng)
                        rows.append({**base_rec, **stress, "train_gate_bool": bool(stress["train_gate"])})
                    policy_cache[base_rec["policy_id"]] = {
                        "target": target,
                        "rep_train": rep_train,
                        "rep_test": rep_test,
                        "base_oof": base_oof,
                        "aug_oof": aug_oof,
                        "benefit": benefit,
                        "x_gate": x_gate,
                        "labels": labels,
                        "model_name": model_name,
                        "gate_group": gate_group,
                        "label_mode": label_name,
                        "slice": sl.to_dict(),
                    }
    summary = pd.DataFrame(rows)
    if not summary.empty:
        summary = summary.sort_values(
            ["train_gate_bool", "actual_delta", "dominance", "auc"],
            ascending=[False, True, False, False],
        ).reset_index(drop=True)
    return summary, policy_cache


def final_test_components(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    policy: dict[str, Any],
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    target = str(policy["target"])
    rep_train = policy["rep_train"]
    rep_test = policy["rep_test"]
    y = train_df[target].to_numpy(dtype=int)
    x_base_tr = base_train.reset_index(drop=True)
    x_base_te = base_test.reset_index(drop=True)
    x_aug_tr = pd.concat([x_base_tr, rep_train.reset_index(drop=True)], axis=1)
    x_aug_te = pd.concat([x_base_te, rep_test.reset_index(drop=True)], axis=1)
    base_test_prob = fit_predict_prob(x_base_tr, y, x_base_te)
    aug_test_prob = fit_predict_prob(x_aug_tr, y, x_aug_te)
    train_x = policy["x_gate"]
    test_x = row_features(base_test, rep_test, target, base_test_prob, aug_test_prob, test_df)
    train_x, test_x = align_columns(train_x, test_x)
    labels = policy["labels"].astype(int)
    model = make_gate_model(str(policy["model_name"]))
    model.fit(train_x, labels)
    test_score = model.predict_proba(test_x)[:, 1]
    raw_delta = np.clip(logit(aug_test_prob) - logit(base_test_prob), -CAP, CAP)
    centered_delta = np.clip(raw_delta - float(np.median(raw_delta)), -CAP, CAP)
    return test_x, test_score, raw_delta, centered_delta, base_test_prob


def write_candidate(base: pd.DataFrame, target: str, delta: np.ndarray, score: np.ndarray, top_frac: float, scale: float, candidate_id: str) -> tuple[Path, np.ndarray]:
    n_select = max(1, int(round(len(score) * float(top_frac))))
    selected = np.zeros(len(score), dtype=bool)
    selected[np.argsort(score)[::-1][:n_select]] = True
    selected_delta = np.where(selected, scale * np.asarray(delta, dtype=np.float64), 0.0)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += selected_delta
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e290_lifeplace_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, selected_delta


def write_null_candidate(base: pd.DataFrame, target: str, selected_delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(stable_seed("e290null", source_path.name, mode, rep))
    values = np.asarray(selected_delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values))]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
    else:
        raise ValueError(mode)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += shuffled
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e290null_{source_path.stem[:72]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel(path)
        row["source_path"] = rel(path)
        row["basename"] = path.name
        rows.append(row)
    return pd.DataFrame(rows)


def materialize(
    placement: pd.DataFrame,
    policy_cache: dict[str, dict[str, Any]],
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    current: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    selected = placement[placement["train_gate_bool"].astype(bool)].copy()
    if selected.empty:
        selected = placement.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_POLICIES).copy()
    else:
        selected = selected.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_POLICIES).copy()
    meta = prep_test_meta(test_df)
    candidate_paths: list[Path] = []
    candidate_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    component_cache: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}

    for _, row in selected.iterrows():
        policy_id = str(row["policy_id"])
        policy = policy_cache[policy_id]
        if policy_id not in component_cache:
            _test_x, score, raw_delta, centered_delta, _base_test_prob = final_test_components(
                train_df, test_df, base_train, base_test, policy
            )
            component_cache[policy_id] = (score, raw_delta, centered_delta)
        score, raw_delta, centered_delta = component_cache[policy_id]
        for delta_mode, delta in [("raw", raw_delta), ("centered", centered_delta)]:
            if delta_mode not in DELTA_MODES:
                continue
            for scale in SCALES:
                candidate_id = f"{policy_id}_tf{int(float(row['top_frac'])*100):02d}_{delta_mode}_s{int(scale*100):03d}"
                path, selected_delta = write_candidate(
                    current,
                    str(row["target"]),
                    delta,
                    score,
                    float(row["top_frac"]),
                    scale,
                    candidate_id,
                )
                candidate_paths.append(path)
                candidate_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "basename": path.name,
                        "source_path": rel(path),
                        "policy_id": policy_id,
                        "target": row["target"],
                        "view_id": row["view_id"],
                        "split": row["split"],
                        "rep": row["rep"],
                        "label_mode": row["label_mode"],
                        "gate_group": row["gate_group"],
                        "model": row["model"],
                        "top_frac": float(row["top_frac"]),
                        "delta_mode": delta_mode,
                        "scale": scale,
                        "train_actual_delta": float(row["actual_delta"]),
                        "train_dominance": float(row["dominance"]),
                        "train_min_mode_dominance": float(min(row["row_dominance"], row["subject_dominance"], row["dateblock_dominance"])),
                        "test_selected_rows": int(np.count_nonzero(np.abs(selected_delta) > 1.0e-12)),
                        "test_delta_mean": float(np.mean(selected_delta)),
                        "test_delta_p90_abs": float(np.quantile(np.abs(selected_delta), 0.90)),
                        "test_delta_l1": float(np.sum(np.abs(selected_delta))),
                    }
                )
                for null_mode in ["row", "subject", "dateblock"]:
                    for rep in range(N_TEST_NULL_REPS):
                        null_path = write_null_candidate(current, str(row["target"]), selected_delta, path, meta, null_mode, rep)
                        null_rows.append(
                            {
                                "source_basename": path.name,
                                "null_basename": null_path.name,
                                "null_path": rel(null_path),
                                "mode": null_mode,
                                "rep": rep,
                            }
                        )

    candidate_meta = pd.DataFrame(candidate_rows)
    null_map = pd.DataFrame(null_rows)
    if candidate_meta.empty:
        return candidate_meta, null_map, pd.DataFrame()

    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_paths = [ROOT / p for p in null_map["null_path"].tolist()]
    score_features = feature_rows([OUT / CURRENT, *candidate_paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, score_features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    candidate_score = scores[scores["basename"].isin(candidate_meta["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidate_meta.iterrows():
        basename = str(cand["basename"])
        actual = candidate_score[candidate_score["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these_null = null_scores[null_scores["basename"].isin(null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].mean()) if len(these_null) else 1.0
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = []
        for _, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms.append(float(np.mean(float(a["pred_delta_vs_current_p90"]) < vals)))
        worst_mode = float(min(mode_doms)) if mode_doms else 0.0
        ready = bool(old_strict and null_strict_rate <= 0.10 and p90_dominance >= 0.80 and mean_dominance >= 0.70 and worst_mode >= 0.55)
        rows.append(
            {
                **cand.to_dict(),
                "old_promotion_decision": a.get("promotion_decision", ""),
                "old_strict_promote": old_strict,
                "actual_mean": float(a["pred_delta_vs_current_mean"]),
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": float(a["pred_delta_vs_current_p90"]),
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these_null)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode,
                "public_free_submission_ready": ready,
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_matched_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "actual_p90", "p90_dominance"],
            ascending=[False, False, True, False],
        ).reset_index(drop=True)
    return candidate_meta, null_map, governor


def write_report(placement: pd.DataFrame, candidates: pd.DataFrame, governor: pd.DataFrame) -> None:
    gates = placement[placement["train_gate_bool"].astype(bool)] if not placement.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    lines = [
        "# E290 Lifestyle Row-Placement Law Audit",
        "",
        "## Question",
        "",
        "Can the Q3/S4 lifestyle slices from E289 learn where they should be applied, rather than being applied as a global target shift?",
        "",
        "## Train Placement Stress",
        "",
        f"- placement rows: `{len(placement)}`",
        f"- train placement gates: `{len(gates)}`",
        "",
        md_table(
            placement[
                [
                    "policy_id",
                    "target",
                    "label_mode",
                    "gate_group",
                    "model",
                    "top_frac",
                    "full_aug_delta",
                    "actual_delta",
                    "null_median",
                    "dominance",
                    "row_dominance",
                    "subject_dominance",
                    "dateblock_dominance",
                    "train_gate_bool",
                ]
            ] if not placement.empty else placement,
            n=40,
        ),
        "",
        "## Materialization Governor",
        "",
        f"- candidates: `{len(candidates)}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor[
                [
                    "basename",
                    "target",
                    "label_mode",
                    "gate_group",
                    "model",
                    "top_frac",
                    "delta_mode",
                    "scale",
                    "old_promotion_decision",
                    "actual_mean",
                    "actual_p90",
                    "null_strict_rate",
                    "p90_dominance",
                    "worst_mode_p90_dominance",
                    "final_decision",
                ]
            ] if not governor.empty else governor,
            n=60,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("At least one E290 candidate is public-free ready. Submit only the top ready candidate as the next scarce-LB test.")
    else:
        lines.append("No E290 candidate is public-free ready. Lifestyle row-placement remains a diagnostic target, not a submission translator.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit asks whether the E289 signal failed because placement was unknown. A train placement gate is necessary but not sufficient: it must also produce an E247-current movement that beats matched test nulls.",
            "",
            "## Files",
            "",
            f"- `{PLACEMENT_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train_df, test_df, base_train, base_test, cache = build_lifestyle_cache()
    slices = selected_slices()
    placement, policy_cache = train_slice_policy_rows(slices, train_df, base_train, base_test, cache)

    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    if not prep_test_meta(test_df)[KEYS].equals(normalize_keys(current[KEYS])):
        raise RuntimeError("E290 test features do not align with current submission")
    candidates, null_map, governor = materialize(placement, policy_cache, train_df, test_df, base_train, base_test, current)

    placement.to_csv(PLACEMENT_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(placement, candidates, governor)

    print(f"placement_rows={len(placement)}")
    print(f"train_gates={int(placement['train_gate_bool'].sum()) if not placement.empty else 0}")
    print(f"candidates={len(candidates)}")
    print(f"nulls={len(null_map)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    print(f"best_train_delta={placement['actual_delta'].min():.9f}" if not placement.empty else "best_train_delta=nan")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
