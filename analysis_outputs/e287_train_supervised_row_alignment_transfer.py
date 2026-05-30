#!/usr/bin/env python3
"""E287: train-supervised row-alignment transfer audit.

E286 rejected test-side E247 pseudo-cell identity as a breakthrough target.
This experiment grounds the next human/social JEPA target in train labels:

    context -> "will this q-sleep diary action improve this row/target?"

The target is defined from OOF train residual benefit, not from current test
submission membership.  A candidate can only be considered if the learned
row-action gate improves train OOF row placement versus matched shuffles and
then beats E247-current matched row/subject/dateblock nulls on the test tensor.

No public LB is used.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e287_train_supervised_row_alignment_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    evaluate_models,
    score_candidates,
)
from e274_target_specific_diary_energy_audit import (  # noqa: E402
    FEATURE_PATH,
    TARGETS,
    clip_prob,
    robust_z,
    sigmoid,
)
from e276_q_sleep_story_ablation_placebo_audit import q_axes_top12  # noqa: E402
from e278_train_row_alignment_null_audit import oof_baseline, q_mean_logloss  # noqa: E402
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    feature_row,
    load_sub,
    logit,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

RNG_SEED = 20260531 + 287
Q_TARGETS = ["Q1", "Q2", "Q3"]
N_TRAIN_NULL_REPS = 60
N_TEST_NULL_REPS = 7

APP_STATE_IN = OUT / "e282_appentropy_story_state.csv"

LATENT_OUT = OUT / "e287_train_supervised_row_alignment_latent_summary.csv"
POLICY_OUT = OUT / "e287_train_supervised_row_alignment_policy_summary.csv"
TRANSFER_OUT = OUT / "e287_train_supervised_row_alignment_transfer_summary.csv"
CANDIDATE_OUT = OUT / "e287_train_supervised_row_alignment_candidate_summary.csv"
GOVERNOR_OUT = OUT / "e287_train_supervised_row_alignment_governor_summary.csv"
SCORE_OUT = OUT / "e287_train_supervised_row_alignment_scores.csv"
NULLS_OUT = OUT / "e287_train_supervised_row_alignment_nulls.csv"
REPORT_OUT = OUT / "e287_train_supervised_row_alignment_report.md"


@dataclass(frozen=True)
class PolicySpec:
    policy_id: str
    axes: pd.DataFrame
    note: str


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 72) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def cell_nll(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    p = clip_prob(p)
    y = np.asarray(y, dtype=np.float64)
    return -(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))


def prep_dates(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in ["sleep_date", "lifelog_date"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out


def key_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return prep_dates(frame[KEYS]).reset_index(drop=True)


def load_features() -> pd.DataFrame:
    features = prep_dates(pd.read_parquet(FEATURE_PATH)).sort_values(KEYS).reset_index(drop=True)
    app = prep_dates(pd.read_csv(APP_STATE_IN)).sort_values(KEYS).reset_index(drop=True)
    if not key_frame(features).equals(key_frame(app)):
        raise RuntimeError("E287 app-entropy state does not align with diary features")
    app_cols = [
        c
        for c in ["story_score_actual", "state_subject_z", "state_dateblock_z", "state_avg_z"]
        if c in app.columns
    ]
    for col in app_cols:
        features[f"appentropy_{col}"] = pd.to_numeric(app[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    return features


def feature_columns(features: pd.DataFrame) -> list[str]:
    excluded = set(KEYS + TARGETS + ["split", "dateblock_group"])
    cols: list[str] = []
    for col in features.columns:
        if col in excluded:
            continue
        if pd.api.types.is_numeric_dtype(features[col]):
            cols.append(col)
    return cols


def policy_specs() -> list[PolicySpec]:
    axes = q_axes_top12()
    axes = axes.sort_values("local_axis_score", ascending=False).reset_index(drop=True)
    specs = [
        PolicySpec("full_qsleep", axes, "all q-sleep Q1/Q2/Q3 axes"),
        PolicySpec("q3_only", axes[axes["target"].eq("Q3")].copy(), "Q3-only subjective sleep row action"),
        PolicySpec("jepa_only", axes[axes["axis_kind"].astype(str).str.startswith("jepa")].copy(), "JEPA-derived diary axes only"),
        PolicySpec(
            "mobility_q3",
            axes[axes["target"].eq("Q3") & axes["story_family"].eq("mobility_context")].copy(),
            "Q3 mobility/context state only",
        ),
        PolicySpec(
            "bedtime_q3",
            axes[axes["target"].eq("Q3") & axes["story_family"].eq("bedtime_phone")].copy(),
            "Q3 bedtime-phone state only",
        ),
        PolicySpec(
            "attention_money_q3",
            axes[axes["target"].eq("Q3") & axes["story_family"].isin(["cognitive_money", "routine_calendar", "diary_global"])].copy(),
            "Q3 cognitive-money/routine/global attention state",
        ),
    ]
    return [spec for spec in specs if not spec.axes.empty]


def apply_policy_moves(
    frame: pd.DataFrame,
    train_ref: pd.DataFrame,
    base_logits: np.ndarray,
    target_names: list[str],
    spec: PolicySpec,
    *,
    amp: float = 0.045 * 1.60,
    cap: float = 0.090,
    top_each: int = 12,
) -> tuple[np.ndarray, pd.DataFrame]:
    logits = np.asarray(base_logits, dtype=np.float64).copy()
    original = np.asarray(base_logits, dtype=np.float64).copy()
    rows: list[dict[str, Any]] = []

    for _, axis in spec.axes.sort_values("local_axis_score", ascending=False).iterrows():
        target = str(axis["target"])
        if target not in target_names:
            continue
        target_idx = target_names.index(target)
        feature = str(axis["feature"])
        if feature not in frame.columns or feature not in train_ref.columns:
            continue
        direction = int(axis["direction"])
        if direction == 0:
            continue
        z_vals, _, _ = robust_z(train_ref[feature], frame[feature])
        effect = direction * z_vals
        if not np.isfinite(effect).any():
            continue
        order_hi = np.argsort(effect)[::-1]
        order_lo = np.argsort(effect)
        chosen = np.zeros(len(frame), dtype=bool)
        chosen[order_hi[:top_each]] = True
        chosen[order_lo[:top_each]] = True
        scale = np.clip(float(axis["abs_label_lift"]) / 0.20, 0.45, 1.60)
        raw_delta = amp * scale * np.clip(effect / 2.5, -1.0, 1.0)
        delta = np.where(chosen, raw_delta, 0.0)
        before = logits[:, target_idx].copy()
        logits[:, target_idx] = np.clip(logits[:, target_idx] + delta, original[:, target_idx] - cap, original[:, target_idx] + cap)
        applied = logits[:, target_idx] - before
        for row_idx in np.where(np.abs(applied) > 1.0e-12)[0]:
            rows.append(
                {
                    "row_idx": int(row_idx),
                    "policy_id": spec.policy_id,
                    "target": target,
                    "feature": feature,
                    "story_family": axis.get("story_family", ""),
                    "axis_kind": axis.get("axis_kind", ""),
                    "feature_effect": float(effect[row_idx]),
                    "abs_feature_effect": float(abs(effect[row_idx])),
                    "logit_delta": float(applied[row_idx]),
                    "abs_logit_delta": float(abs(applied[row_idx])),
                    "axis_abs_label_lift": float(axis["abs_label_lift"]),
                    "axis_subject_delta": float(axis["subject_delta"]),
                    "axis_dateblock_delta": float(axis["dateblock_delta"]),
                    "axis_boundary_signal": float(axis["boundary_signal"]),
                    "axis_local_score": float(axis["local_axis_score"]),
                }
            )
    return logits - original, pd.DataFrame(rows)


def train_cell_frame(
    features: pd.DataFrame,
    train: pd.DataFrame,
    base_prob: np.ndarray,
    base_logits: np.ndarray,
    split_name: str,
    spec: PolicySpec,
) -> tuple[pd.DataFrame, np.ndarray]:
    delta, cells = apply_policy_moves(train, train, base_logits, Q_TARGETS, spec)
    if cells.empty:
        return cells, delta
    y = train[Q_TARGETS].to_numpy(dtype=int)
    target_idx = cells["target"].map({target: i for i, target in enumerate(Q_TARGETS)}).to_numpy(dtype=int)
    row_idx = cells["row_idx"].to_numpy(dtype=int)
    before = base_prob[row_idx, target_idx]
    after = sigmoid(base_logits[row_idx, target_idx] + cells["logit_delta"].to_numpy(dtype=np.float64))
    labels = y[row_idx, target_idx]
    benefit = cell_nll(labels, after) - cell_nll(labels, before)

    out = cells.copy()
    out["split_name"] = split_name
    out["label"] = labels
    out["base_prob"] = before
    out["base_logit"] = base_logits[row_idx, target_idx]
    out["benefit_delta"] = benefit
    out["benefit_good"] = benefit < 0.0
    out["benefit_strong_good"] = benefit <= np.quantile(benefit, 0.35)
    out["subject_id"] = train.iloc[row_idx]["subject_id"].astype(str).to_numpy()
    out["dateblock_group"] = train.iloc[row_idx]["dateblock_group"].astype(str).to_numpy()
    return out.reset_index(drop=True), delta


def test_cell_frame(
    features: pd.DataFrame,
    test: pd.DataFrame,
    base: pd.DataFrame,
    spec: PolicySpec,
) -> tuple[pd.DataFrame, np.ndarray]:
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    train_ref = features[features["split"].eq("train")].reset_index(drop=True)
    delta, cells = apply_policy_moves(test, train_ref, base_logits, TARGETS, spec)
    if cells.empty:
        return cells, delta
    target_idx = cells["target"].map({target: i for i, target in enumerate(TARGETS)}).to_numpy(dtype=int)
    row_idx = cells["row_idx"].to_numpy(dtype=int)
    out = cells.copy()
    out["subject_id"] = test.iloc[row_idx]["subject_id"].astype(str).to_numpy()
    out["dateblock_group"] = test.iloc[row_idx]["dateblock_group"].astype(str).to_numpy()
    out["base_prob"] = base[TARGETS].to_numpy(dtype=np.float64)[row_idx, target_idx]
    out["base_logit"] = base_logits[row_idx, target_idx]
    return out.reset_index(drop=True), delta


def build_cell_features(row_features: pd.DataFrame, cells: pd.DataFrame, row_feature_cols: list[str]) -> pd.DataFrame:
    row_idx = cells["row_idx"].to_numpy(dtype=int)
    x = row_features.iloc[row_idx][row_feature_cols].reset_index(drop=True).copy()
    x = x.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    for col in [
        "feature_effect",
        "abs_feature_effect",
        "logit_delta",
        "abs_logit_delta",
        "axis_abs_label_lift",
        "axis_subject_delta",
        "axis_dateblock_delta",
        "axis_boundary_signal",
        "axis_local_score",
        "base_prob",
        "base_logit",
    ]:
        x[f"cell_{col}"] = pd.to_numeric(cells[col], errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    dummies = pd.get_dummies(
        cells[["target", "story_family", "axis_kind", "feature"]].astype(str),
        prefix=["target", "family", "kind", "feature"],
        dtype=float,
    ).reset_index(drop=True)
    return pd.concat([x.reset_index(drop=True), dummies], axis=1).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def make_model(model_name: str):
    if model_name == "lr_l2":
        return Pipeline(
            [
                ("impute", SimpleImputer(strategy="median")),
                ("scale", StandardScaler()),
                (
                    "clf",
                    LogisticRegression(
                        C=0.35,
                        solver="lbfgs",
                        class_weight="balanced",
                        max_iter=2000,
                        random_state=RNG_SEED,
                    ),
                ),
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
                        C=0.18,
                        solver="liblinear",
                        penalty="l1",
                        class_weight="balanced",
                        max_iter=2000,
                        random_state=RNG_SEED,
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
                        min_samples_leaf=10,
                        l2_regularization=0.08,
                        max_iter=120,
                        random_state=RNG_SEED,
                    ),
                ),
            ]
        )
    raise ValueError(model_name)


def group_folds(groups: pd.Series) -> list[tuple[np.ndarray, np.ndarray]]:
    n_groups = int(groups.nunique())
    if n_groups < 2:
        return []
    return list(GroupKFold(n_splits=min(5, n_groups)).split(np.zeros(len(groups)), groups=groups.astype(str).to_numpy()))


def crossfit_scores(x: pd.DataFrame, y: np.ndarray, groups: pd.Series, model_name: str) -> np.ndarray:
    scores = np.full(len(y), np.nan, dtype=np.float64)
    for tr_idx, va_idx in group_folds(groups):
        y_tr = y[tr_idx]
        if len(np.unique(y_tr)) < 2:
            scores[va_idx] = float(np.mean(y_tr))
            continue
        model = make_model(model_name)
        model.fit(x.iloc[tr_idx], y_tr)
        scores[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return np.nan_to_num(scores, nan=float(np.mean(y)))


def metric_row(y: np.ndarray, score: np.ndarray) -> dict[str, float]:
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=np.float64)
    prevalence = float(np.mean(y))
    out = {"prevalence": prevalence}
    if len(np.unique(y)) < 2:
        out.update({"auc": np.nan, "ap": np.nan, "ap_lift": np.nan})
    else:
        ap = float(average_precision_score(y, score))
        out.update({"auc": float(roc_auc_score(y, score)), "ap": ap, "ap_lift": ap - prevalence})
    return out


def evaluate_gated_train(
    cells: pd.DataFrame,
    delta: np.ndarray,
    base_logits: np.ndarray,
    base_prob: np.ndarray,
    train: pd.DataFrame,
    score: np.ndarray,
    top_frac: float,
    rng: np.random.Generator,
) -> dict[str, float]:
    if cells.empty:
        return {}
    y = train[Q_TARGETS].to_numpy(dtype=int)
    n_select = max(1, int(round(len(cells) * float(top_frac))))
    order = np.argsort(score)[::-1]
    selected_cell_pos = order[:n_select]
    selected_delta = np.zeros_like(delta)
    for pos in selected_cell_pos:
        row_idx = int(cells.iloc[pos]["row_idx"])
        target_idx = Q_TARGETS.index(str(cells.iloc[pos]["target"]))
        selected_delta[row_idx, target_idx] += float(cells.iloc[pos]["logit_delta"])
    actual_prob = clip_prob(sigmoid(base_logits + selected_delta))
    base_loss = q_mean_logloss(y, base_prob)
    actual_delta = q_mean_logloss(y, actual_prob) - base_loss

    modes = {
        "row": None,
        "subject": cells["subject_id"].astype(str).reset_index(drop=True),
        "dateblock": cells["dateblock_group"].astype(str).reset_index(drop=True),
    }
    null_rows: list[dict[str, float | str]] = []
    for mode, groups in modes.items():
        for rep in range(N_TRAIN_NULL_REPS):
            shuffled_score = np.asarray(score, dtype=np.float64).copy()
            if groups is None:
                shuffled_score = shuffled_score[rng.permutation(len(shuffled_score))]
            else:
                for _, idx in groups.groupby(groups).indices.items():
                    idx_arr = np.asarray(idx, dtype=int)
                    shuffled_score[idx_arr] = shuffled_score[idx_arr][rng.permutation(len(idx_arr))]
            sel = np.argsort(shuffled_score)[::-1][:n_select]
            null_delta = np.zeros_like(delta)
            for pos in sel:
                row_idx = int(cells.iloc[pos]["row_idx"])
                target_idx = Q_TARGETS.index(str(cells.iloc[pos]["target"]))
                null_delta[row_idx, target_idx] += float(cells.iloc[pos]["logit_delta"])
            prob = clip_prob(sigmoid(base_logits + null_delta))
            null_rows.append({"mode": mode, "delta": q_mean_logloss(y, prob) - base_loss})
    null = pd.DataFrame(null_rows)
    all_null = null["delta"].to_numpy(dtype=np.float64)
    out: dict[str, float] = {
        "top_frac": float(top_frac),
        "selected_cells": float(n_select),
        "actual_delta": float(actual_delta),
        "null_q20": float(np.quantile(all_null, 0.20)),
        "null_median": float(np.median(all_null)),
        "null_best": float(np.min(all_null)),
        "dominance": float(np.mean(actual_delta < all_null)),
        "placebo_adjusted_vs_median": float(actual_delta - np.median(all_null)),
        "placebo_adjusted_vs_best": float(actual_delta - np.min(all_null)),
    }
    for mode in modes:
        vals = null.loc[null["mode"].eq(mode), "delta"].to_numpy(dtype=np.float64)
        out[f"{mode}_dominance"] = float(np.mean(actual_delta < vals))
        out[f"{mode}_null_q20"] = float(np.quantile(vals, 0.20))
        out[f"{mode}_null_best"] = float(np.min(vals))
    out["train_gate"] = float(
        actual_delta < 0.0
        and out["dominance"] >= 0.78
        and min(out["row_dominance"], out["subject_dominance"], out["dateblock_dominance"]) >= 0.58
        and actual_delta <= out["null_q20"] - 1.0e-5
    )
    return out


def run_latent_audit(features: pd.DataFrame, specs: list[PolicySpec]) -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[str, str], dict[str, Any]]]:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    row_cols = feature_columns(features)
    latent_rows: list[dict[str, Any]] = []
    policy_rows: list[dict[str, Any]] = []
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    rng = np.random.default_rng(RNG_SEED)

    for split_name, group_col in [("subject_oof", "subject_id"), ("dateblock_oof", "dateblock_group")]:
        base_prob = oof_baseline(train, group_col)
        base_logits = logit(base_prob)
        for spec in specs:
            cells, delta = train_cell_frame(features, train, base_prob, base_logits, split_name, spec)
            if len(cells) < 16 or cells["benefit_good"].nunique() < 2:
                continue
            x = build_cell_features(train, cells, row_cols)
            y = cells["benefit_good"].astype(int).to_numpy()
            groups = cells["subject_id"] if split_name == "subject_oof" else cells["dateblock_group"]
            for model_name in ["lr_l2", "lr_l1", "hgb_shallow"]:
                score = crossfit_scores(x, y, groups, model_name)
                m = metric_row(y, score)
                rec: dict[str, Any] = {
                    "policy_id": spec.policy_id,
                    "policy_note": spec.note,
                    "split": split_name,
                    "model": model_name,
                    "n_cells": int(len(cells)),
                    "n_rows": int(cells["row_idx"].nunique()),
                    "n_good": int(y.sum()),
                    "mean_benefit_delta": float(cells["benefit_delta"].mean()),
                    "median_benefit_delta": float(cells["benefit_delta"].median()),
                    **m,
                }
                latent_rows.append(rec)
                for top_frac in [0.20, 0.35, 0.50, 0.70, 1.00]:
                    gate = evaluate_gated_train(cells, delta, base_logits, base_prob, train, score, top_frac, rng)
                    if not gate:
                        continue
                    policy_rows.append({**rec, **gate, "train_gate_bool": bool(gate["train_gate"])})
                cache[(spec.policy_id, split_name)] = {
                    "cells": cells,
                    "delta": delta,
                    "x": x,
                    "y": y,
                    "row_cols": row_cols,
                }
    latent = pd.DataFrame(latent_rows).sort_values(["auc", "ap_lift"], ascending=[False, False])
    policies = pd.DataFrame(policy_rows)
    if not policies.empty:
        policies = policies.sort_values(
            ["train_gate_bool", "dominance", "actual_delta"],
            ascending=[False, False, True],
        ).reset_index(drop=True)
    return latent.reset_index(drop=True), policies, cache


def align_columns(x_train: pd.DataFrame, x_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = sorted(set(x_train.columns) | set(x_test.columns))
    return x_train.reindex(columns=cols, fill_value=0.0), x_test.reindex(columns=cols, fill_value=0.0)


def train_final_scores(
    features: pd.DataFrame,
    spec: PolicySpec,
    split_name: str,
    model_name: str,
    test_cells: pd.DataFrame,
    train_base_group_col: str,
) -> np.ndarray:
    train = features[features["split"].eq("train")].reset_index(drop=True)
    test = features[features["split"].eq("test")].reset_index(drop=True)
    base_prob = oof_baseline(train, train_base_group_col)
    base_logits = logit(base_prob)
    train_cells, _ = train_cell_frame(features, train, base_prob, base_logits, split_name, spec)
    if train_cells.empty or train_cells["benefit_good"].nunique() < 2 or test_cells.empty:
        return np.zeros(len(test_cells), dtype=np.float64)
    row_cols = feature_columns(features)
    x_train = build_cell_features(train, train_cells, row_cols)
    x_test = build_cell_features(test, test_cells, row_cols)
    x_train, x_test = align_columns(x_train, x_test)
    y = train_cells["benefit_good"].astype(int).to_numpy()
    model = make_model(model_name)
    model.fit(x_train, y)
    return model.predict_proba(x_test)[:, 1]


def write_candidate(base: pd.DataFrame, delta: np.ndarray, cells: pd.DataFrame, score: np.ndarray, top_frac: float, candidate_id: str) -> tuple[Path, pd.DataFrame]:
    n_select = max(1, int(round(len(cells) * float(top_frac))))
    order = np.argsort(score)[::-1][:n_select]
    selected_delta = np.zeros_like(delta)
    selected = cells.iloc[order].copy().reset_index(drop=True)
    selected["rowalign_score"] = score[order]
    for _, row in selected.iterrows():
        row_idx = int(row["row_idx"])
        target_idx = TARGETS.index(str(row["target"]))
        selected_delta[row_idx, target_idx] += float(row["logit_delta"])
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logit(base[TARGETS].to_numpy(dtype=np.float64)) + selected_delta))
    path = OUT / f"submission_e287_rowalign_{safe_id(candidate_id, 92)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    selected["candidate_id"] = candidate_id
    selected["submission_file"] = path.name
    return path, selected


def write_null_candidate(base: pd.DataFrame, delta: np.ndarray, meta: pd.DataFrame, source_path: Path, mode: str, rep: int, seed: int) -> Path:
    rng = np.random.default_rng(seed)
    shuffled = np.zeros_like(delta)
    for target_idx in range(delta.shape[1]):
        values = delta[:, target_idx].copy()
        if mode == "row":
            shuffled[:, target_idx] = values[rng.permutation(len(values))]
        elif mode == "subject":
            for _, idx in meta.groupby("subject_id").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        elif mode == "dateblock":
            for _, idx in meta.groupby("dateblock_group").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        else:
            raise ValueError(mode)
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logit(base[TARGETS].to_numpy(dtype=np.float64)) + shuffled))
    path = NULL_DIR / f"submission_e287null_{source_path.stem[:72]}_{mode}_r{rep}_{short_hash(out)}.csv"
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


def materialize_and_govern(features: pd.DataFrame, specs: list[PolicySpec], policy_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if policy_summary.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    ready_train = policy_summary[policy_summary["train_gate_bool"].astype(bool)].copy()
    if ready_train.empty:
        ready_train = policy_summary.head(8).copy()
    else:
        ready_train = ready_train.head(16).copy()

    base = load_sub(CURRENT).sort_values(KEYS).reset_index(drop=True)
    sample = base[KEYS].copy()
    test = features[features["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    if not key_frame(test).equals(key_frame(base)):
        raise RuntimeError("E287 test diary features do not align with current submission")
    meta = test[KEYS + ["dateblock_group"]].copy()
    meta["subject_id"] = meta["subject_id"].astype(str)
    NULL_DIR.mkdir(exist_ok=True)

    candidate_paths: list[Path] = []
    candidate_rows: list[dict[str, Any]] = []
    selected_cell_rows: list[pd.DataFrame] = []
    null_map_rows: list[dict[str, Any]] = []
    spec_map = {spec.policy_id: spec for spec in specs}

    for idx, row in ready_train.iterrows():
        spec = spec_map[str(row["policy_id"])]
        test_cells, full_delta = test_cell_frame(features, test, base, spec)
        if test_cells.empty:
            continue
        split_name = str(row["split"])
        model_name = str(row["model"])
        group_col = "subject_id" if split_name == "subject_oof" else "dateblock_group"
        score = train_final_scores(features, spec, split_name, model_name, test_cells, group_col)
        top_frac = float(row["top_frac"])
        candidate_id = f"{spec.policy_id}_{split_name}_{model_name}_tf{int(top_frac * 100):02d}"
        path, selected = write_candidate(base, full_delta, test_cells, score, top_frac, candidate_id)
        candidate_paths.append(path)
        selected_cell_rows.append(selected)
        candidate_delta = logit(load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)) - logit(base[TARGETS].to_numpy(dtype=np.float64))
        candidate_rows.append(
            {
                "candidate_id": candidate_id,
                "basename": path.name,
                "source_path": rel(path),
                "policy_id": spec.policy_id,
                "split": split_name,
                "model": model_name,
                "top_frac": top_frac,
                "train_actual_delta": float(row["actual_delta"]),
                "train_dominance": float(row["dominance"]),
                "train_min_mode_dominance": float(min(row["row_dominance"], row["subject_dominance"], row["dateblock_dominance"])),
                "test_available_cells": int(len(test_cells)),
                "test_selected_cells": int(len(selected)),
                "changed_cells_vs_current": int(np.count_nonzero(np.abs(candidate_delta) > 1.0e-12)),
                "l1_logit_delta_vs_current": float(np.sum(np.abs(candidate_delta))),
                "max_abs_logit_delta_vs_current": float(np.max(np.abs(candidate_delta))),
            }
        )
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_TEST_NULL_REPS):
                seed = RNG_SEED + int(idx) * 1009 + rep * 97 + {"row": 0, "subject": 1, "dateblock": 2}[mode]
                null_path = write_null_candidate(base, candidate_delta, meta, path, mode, rep, seed)
                null_map_rows.append(
                    {
                        "source_path": rel(path),
                        "source_basename": path.name,
                        "null_path": rel(null_path),
                        "null_basename": null_path.name,
                        "mode": mode,
                        "rep": rep,
                    }
                )
    candidate_meta = pd.DataFrame(candidate_rows)
    null_map = pd.DataFrame(null_map_rows)
    selected_cells = pd.concat(selected_cell_rows, ignore_index=True) if selected_cell_rows else pd.DataFrame()
    if not candidate_paths:
        return candidate_meta, null_map, pd.DataFrame(), selected_cells

    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    all_paths = [OUT / CURRENT, *candidate_paths, *[ROOT / p for p in []]]
    null_paths = [ROOT / p if not Path(p).is_absolute() else Path(p) for p in null_map["null_path"].tolist()] if not null_map.empty else []
    # rel(null_path) is relative to ROOT, so ROOT / rel resolves correctly.
    score_features = feature_rows([*all_paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, score_features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULLS_OUT, index=False)

    candidate_score = scores[scores["basename"].isin(candidate_meta["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"] if not null_map.empty else [])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidate_meta.iterrows():
        basename = str(cand["basename"])
        actual = candidate_score[candidate_score["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        these_null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these_null = null_scores[null_scores["basename"].isin(these_null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        p90 = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90)) if len(p90) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean)) if len(mean) else 0.0
        worst_mode = 0.0
        if len(these_null):
            mode_vals = []
            for mode, part in these_null.groupby("mode"):
                vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
                mode_vals.append(float(np.mean(float(a["pred_delta_vs_current_p90"]) < vals)))
            worst_mode = float(min(mode_vals)) if mode_vals else 0.0
        ready = bool(old_strict and null_strict_rate <= 0.10 and p90_dominance >= 0.80 and mean_dominance >= 0.70 and worst_mode >= 0.55)
        final_decision = "public_free_submission_ready" if ready else (
            "blocked_by_matched_nulls" if old_strict else str(a.get("promotion_decision", "hold"))
        )
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
                "final_decision": final_decision,
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "actual_p90", "p90_dominance"],
            ascending=[False, False, True, False],
        ).reset_index(drop=True)
    return candidate_meta, null_map, governor, selected_cells


def write_report(latent: pd.DataFrame, policy: pd.DataFrame, transfer: pd.DataFrame, candidates: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    train_ready = policy[policy["train_gate_bool"].astype(bool)] if not policy.empty else pd.DataFrame()
    lines = [
        "# E287 Train-Supervised Row-Alignment Transfer Audit",
        "",
        "## Question",
        "",
        "Can human/social diary context learn a label-grounded row-action benefit target, and can that learned gate transfer to an E247-current tensor without public LB?",
        "",
        "## Train Latent Health",
        "",
        f"- latent rows: `{len(latent)}`",
        f"- train-gated policy rows: `{len(train_ready)}`",
        "",
        md_table(latent, ["policy_id", "split", "model", "n_cells", "n_good", "prevalence", "auc", "ap", "ap_lift", "mean_benefit_delta"], n=30),
        "",
        "## Train Row-Placement Policy Stress",
        "",
        md_table(
            policy,
            [
                "policy_id",
                "split",
                "model",
                "top_frac",
                "selected_cells",
                "actual_delta",
                "null_q20",
                "dominance",
                "row_dominance",
                "subject_dominance",
                "dateblock_dominance",
                "train_gate_bool",
            ],
            n=40,
        ),
        "",
        "## Test Transfer Candidates",
        "",
        f"- materialized candidates: `{len(candidates)}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor,
            [
                "basename",
                "policy_id",
                "split",
                "model",
                "top_frac",
                "test_selected_cells",
                "old_promotion_decision",
                "actual_mean",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "worst_mode_p90_dominance",
                "final_decision",
            ],
            n=40,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("At least one E287 row-alignment transfer candidate is public-free ready. Submit only the top ready row, because this is a scarce-LB hypothesis test.")
    else:
        lines.append("No E287 candidate is public-free ready. The train row-action latent is useful only if it can beat test matched nulls; otherwise keep it diagnostic.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This experiment distinguishes three states: train-label row-action learnability, train matched-null row placement, and test tensor transfer. A high train AUC without matched-null dominance is not enough. A train-gated row without E247-current null dominance is also not enough.",
            "",
            "## Files",
            "",
            f"- `{LATENT_OUT.name}`",
            f"- `{POLICY_OUT.name}`",
            f"- `{TRANSFER_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    features = load_features()
    specs = policy_specs()
    latent, policy, _cache = run_latent_audit(features, specs)
    candidate_meta, null_map, governor, selected_cells = materialize_and_govern(features, specs, policy)

    latent.to_csv(LATENT_OUT, index=False)
    policy.to_csv(POLICY_OUT, index=False)
    candidate_meta.to_csv(CANDIDATE_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    selected_cells.to_csv(TRANSFER_OUT, index=False)
    write_report(latent, policy, selected_cells, candidate_meta, governor)
    print(f"latent_rows={len(latent)}")
    print(f"train_policy_rows={len(policy)}")
    print(f"train_gated_rows={int(policy['train_gate_bool'].sum()) if not policy.empty else 0}")
    print(f"candidates={len(candidate_meta)}")
    print(f"nulls={len(null_map)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
