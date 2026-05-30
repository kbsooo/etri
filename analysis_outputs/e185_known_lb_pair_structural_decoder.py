#!/usr/bin/env python3
"""E185: known-LB pair structural decoder stress.

E184 asked whether shallow known-public cell metadata can select pressure-world
branches. It failed. The next smaller question is not another cell classifier:

    If all currently known public-LB submissions are turned into pairwise
    movement claims, does candidate movement anatomy itself generalize to an
    unseen submission, especially at the E95/E101/mixmin frontier scale?

This is a decoder audit, not a submission generator. A usable selector must
survive leave-one-file-out and frontier-scale stress before its pressure-branch
scores can influence submission choice.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import TARGETS, known_public_table  # noqa: E402
import e179_e176_critical_cell_visibility_audit as e179  # noqa: E402


PAIR_FEATURES_OUT = OUT / "e185_known_lb_pair_structural_decoder_features.csv"
FILE_LOO_OUT = OUT / "e185_known_lb_pair_structural_decoder_file_loo.csv"
PAIR_LOO_OUT = OUT / "e185_known_lb_pair_structural_decoder_pair_loo.csv"
SUMMARY_OUT = OUT / "e185_known_lb_pair_structural_decoder_summary.csv"
BRANCH_OUT = OUT / "e185_known_lb_pair_structural_decoder_pressure_branches.csv"
REPORT_OUT = OUT / "e185_known_lb_pair_structural_decoder_report.md"

PRESSURE_CELLS_IN = OUT / "e183_pressure_world_branch_anatomy_cells.csv"

EPS = 1.0e-12
FRONTIER_CUTOFF = 0.5776
MICRO_DELTA = 0.0002
E95_EDGE = 0.5763066405 - 0.5762913298

PRIORS = (
    "global",
    "subject",
    "nearest_hard085",
    "focus_mean",
    "flank_mean",
    "visible_mean",
)

SETS = (
    "all",
    "top1",
    "top4",
    "top16",
    "top33",
    "between",
    "not_e72",
    "between_not_e72",
)


@dataclass(frozen=True)
class FeatureSet:
    name: str
    include_prefixes: tuple[str, ...]


FEATURE_SETS = (
    FeatureSet(
        "shape_only",
        (
            "shape_",
            "target_",
            "ctx_",
        ),
    ),
    FeatureSet(
        "shape_support",
        (
            "shape_",
            "target_",
            "ctx_",
            "sup_",
        ),
    ),
    FeatureSet(
        "shape_support_public_axis",
        (
            "shape_",
            "target_",
            "ctx_",
            "sup_",
            "axis_",
        ),
    ),
)


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    rendered = view.copy()
    for col in rendered.columns:
        if pd.api.types.is_float_dtype(rendered[col]):
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else f"{x:.9f}")
        else:
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(rendered.columns.astype(str)) + " |"
    sep = "| " + " | ".join(["---"] * len(rendered.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in rendered.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def safe_bool(frame: pd.DataFrame, col: str, default: bool = False) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=bool)
    return frame[col].fillna(default).astype(bool)


def safe_num(frame: pd.DataFrame, col: str, default: float = 0.0) -> pd.Series:
    if col not in frame.columns:
        return pd.Series(default, index=frame.index, dtype=float)
    return pd.to_numeric(frame[col], errors="coerce").fillna(default)


def support_probability(cells: pd.DataFrame, prior: str, reverse: bool) -> np.ndarray:
    col = f"support_probability_{prior}"
    if col not in cells.columns:
        raise KeyError(col)
    p = cells[col].to_numpy(dtype=np.float64)
    return 1.0 - p if reverse else p


def oriented_support_label(cells: pd.DataFrame, reverse: bool) -> np.ndarray:
    label = cells["support_label"].to_numpy(dtype=np.float64)
    return 1.0 - label if reverse else label


def mask_for(cells: pd.DataFrame, set_name: str) -> np.ndarray:
    n = len(cells)
    if set_name == "all":
        return np.ones(n, dtype=bool)
    if set_name == "top1":
        return cells["swing_rank"].le(1).to_numpy(dtype=bool)
    if set_name == "top4":
        return cells["swing_rank"].le(4).to_numpy(dtype=bool)
    if set_name == "top16":
        return cells["swing_rank"].le(16).to_numpy(dtype=bool)
    if set_name == "top33":
        return cells["swing_rank"].le(33).to_numpy(dtype=bool)
    if set_name == "between":
        return safe_bool(cells, "between_train_runs").to_numpy(dtype=bool)
    if set_name == "not_e72":
        return ~safe_bool(cells, "e72_active").to_numpy(dtype=bool)
    if set_name == "between_not_e72":
        return safe_bool(cells, "between_train_runs").to_numpy(dtype=bool) & ~safe_bool(
            cells, "e72_active"
        ).to_numpy(dtype=bool)
    raise ValueError(set_name)


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    if len(values) == 0:
        return np.nan
    denom = float(np.sum(weights))
    if denom <= EPS:
        return float(np.mean(values))
    return float(np.average(values, weights=weights))


def add_set_features(rec: dict[str, Any], cells: pd.DataFrame, set_name: str, reverse: bool) -> None:
    mask = mask_for(cells, set_name)
    part = cells.loc[mask].copy()
    prefix = f"{set_name}_"
    if part.empty:
        rec[f"shape_{prefix}n_cells"] = 0.0
        rec[f"shape_{prefix}swing_sum"] = 0.0
        return

    swing = part["swing"].to_numpy(dtype=np.float64)
    support_label = oriented_support_label(part, reverse)
    rec[f"shape_{prefix}n_cells"] = float(len(part))
    rec[f"shape_{prefix}n_rows"] = float(part["sub_idx"].nunique())
    rec[f"shape_{prefix}swing_sum"] = float(np.sum(swing))
    rec[f"shape_{prefix}swing_max"] = float(np.max(swing))
    rec[f"shape_{prefix}swing_top_share"] = float(np.max(swing) / max(np.sum(swing), EPS))
    rec[f"shape_{prefix}support_label_mean"] = float(np.mean(support_label))
    rec[f"shape_{prefix}support_label_swing"] = weighted_mean(support_label, swing)

    q_mask = part["target_group"].eq("Q").to_numpy(dtype=bool)
    rec[f"target_{prefix}q_cell_share"] = float(np.mean(q_mask))
    rec[f"target_{prefix}q_swing_share"] = float(np.sum(swing[q_mask]) / max(np.sum(swing), EPS))
    for target in TARGETS:
        tmask = part["target"].eq(target).to_numpy(dtype=bool)
        rec[f"target_{prefix}{target}_cell_share"] = float(np.mean(tmask))
        rec[f"target_{prefix}{target}_swing_share"] = float(np.sum(swing[tmask]) / max(np.sum(swing), EPS))
        if np.any(tmask):
            rec[f"target_{prefix}{target}_support_swing"] = weighted_mean(support_label[tmask], swing[tmask])
        else:
            rec[f"target_{prefix}{target}_support_swing"] = 0.0

    rec[f"ctx_{prefix}between_rate"] = float(safe_bool(part, "between_train_runs").mean())
    rec[f"ctx_{prefix}edge_like_rate"] = float(safe_bool(part, "edge_like").mean())
    rec[f"ctx_{prefix}context_high_rate"] = float(safe_bool(part, "context_high").mean())
    rec[f"ctx_{prefix}flank_conflict_rate"] = float(safe_bool(part, "flank_conflict").mean())
    rec[f"ctx_{prefix}both_flanks_rate"] = float(safe_bool(part, "both_flanks").mean())

    rec[f"axis_{prefix}e72_active_rate"] = float(safe_bool(part, "e72_active").mean())
    rec[f"axis_{prefix}e101_active_rate"] = float(safe_bool(part, "e101_active").mean())
    rec[f"axis_{prefix}all_veto_null_rate"] = float(safe_bool(part, "all_veto_null").mean())
    rec[f"axis_{prefix}all_safe_density_mean"] = float(safe_num(part, "all_safe_density").mean())
    rec[f"axis_{prefix}broad_low_alpha_mass_mean"] = float(safe_num(part, "broad_low_alpha_mass").mean())
    rec[f"axis_{prefix}e101_plausible_mass_mean"] = float(safe_num(part, "e101_plausible_mass").mean())

    for prior in PRIORS:
        p = support_probability(part, prior, reverse)
        rec[f"sup_{prefix}{prior}_mean"] = float(np.mean(p))
        rec[f"sup_{prefix}{prior}_swing"] = weighted_mean(p, swing)
        rec[f"sup_{prefix}{prior}_hard_rate"] = float(np.mean(p >= 0.5))
    support_stack = np.column_stack([support_probability(part, prior, reverse) for prior in PRIORS])
    rec[f"sup_{prefix}range_mean"] = float(np.mean(np.max(support_stack, axis=1) - np.min(support_stack, axis=1)))
    rec[f"sup_{prefix}all_prior_support_rate"] = float(np.mean(np.min(support_stack, axis=1) >= 0.5))
    rec[f"sup_{prefix}all_prior_adverse_rate"] = float(np.mean(np.max(support_stack, axis=1) < 0.5))
    rec[f"sup_{prefix}prior_split_rate"] = float(
        np.mean((np.min(support_stack, axis=1) < 0.5) & (np.max(support_stack, axis=1) >= 0.5))
    )


def aggregate_pair(
    cells: pd.DataFrame,
    pair_id: str,
    new_file: str,
    base_file: str,
    new_score: float,
    base_score: float,
    reverse: bool,
) -> dict[str, Any]:
    actual_delta = float(new_score - base_score)
    rec: dict[str, Any] = {
        "pair_id": pair_id,
        "new_file": new_file,
        "base_file": base_file,
        "new_score": float(new_score),
        "base_score": float(base_score),
        "actual_delta": actual_delta,
        "actual_new_better": int(actual_delta < 0.0),
        "abs_actual_delta": abs(actual_delta),
        "frontier_pair": bool(max(new_score, base_score) <= FRONTIER_CUTOFF),
        "micro_pair": bool(abs(actual_delta) <= MICRO_DELTA),
        "e95_edge_pair": bool(abs(actual_delta) <= E95_EDGE * 8.0),
        "orientation_reverse": bool(reverse),
    }
    for set_name in SETS:
        add_set_features(rec, cells, set_name, reverse)
    return rec


def load_known_scores() -> pd.DataFrame:
    known = known_public_table().copy()
    known = known.sort_values("public_lb").reset_index(drop=True)
    known = known.drop_duplicates("file", keep="first").reset_index(drop=True)
    return known


def build_oriented_pair_features(known: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    records = known.to_dict("records")
    for i, left in enumerate(records):
        for j in range(i + 1, len(records)):
            right = records[j]
            left_file = str(left["file"])
            right_file = str(right["file"])
            pair_id = f"{left_file}__vs__{right_file}"
            cells = e179.build_pair_cells(pair_id, left_file, right_file)
            rows.append(
                aggregate_pair(
                    cells,
                    pair_id,
                    left_file,
                    right_file,
                    float(left["public_lb"]),
                    float(right["public_lb"]),
                    reverse=False,
                )
            )
            rows.append(
                aggregate_pair(
                    cells,
                    pair_id,
                    right_file,
                    left_file,
                    float(right["public_lb"]),
                    float(left["public_lb"]),
                    reverse=True,
                )
            )
    return pd.DataFrame(rows)


def feature_columns(frame: pd.DataFrame, fs: FeatureSet) -> list[str]:
    cols = [
        c
        for c in frame.columns
        if any(c.startswith(prefix) for prefix in fs.include_prefixes)
        and pd.api.types.is_numeric_dtype(frame[c])
    ]
    return sorted(cols)


def make_model() -> Pipeline:
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=5000, C=0.25, solver="lbfgs")),
        ]
    )


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(roc_auc_score(y, p))


def evaluate_predictions(rows: list[dict[str, Any]], group_col: str, feature_set: str) -> dict[str, Any]:
    pred = pd.DataFrame(rows)
    y = pred["actual_new_better"].to_numpy(dtype=int)
    p = pred["prob_new_better"].to_numpy(dtype=np.float64)
    reciprocity_rows = []
    for _, part in pred.groupby(["heldout", "pair_id"]):
        if len(part) != 2:
            continue
        reciprocity_rows.append(
            {
                "abs_sum_error": abs(float(part["prob_new_better"].sum()) - 1.0),
                "frontier_pair": bool(part["frontier_pair"].any()),
                "micro_pair": bool(part["micro_pair"].any()),
                "e95_edge_pair": bool(part["e95_edge_pair"].any()),
            }
        )
    reciprocity = pd.DataFrame(reciprocity_rows)
    out: dict[str, Any] = {
        "feature_set": feature_set,
        "group_col": group_col,
        "n_rows": int(len(pred)),
        "n_groups": int(pred["heldout"].nunique()),
        "accuracy": float(np.mean((p >= 0.5) == y)),
        "auc": safe_auc(y, p),
        "logloss": float(log_loss(y, np.clip(p, EPS, 1.0 - EPS), labels=[0, 1])),
        "brier": float(brier_score_loss(y, np.clip(p, EPS, 1.0 - EPS))),
        "frontier_accuracy": np.nan,
        "frontier_auc": np.nan,
        "micro_accuracy": np.nan,
        "e95_edge_accuracy": np.nan,
        "reciprocity_mae": float(reciprocity["abs_sum_error"].mean()) if not reciprocity.empty else np.nan,
        "frontier_reciprocity_mae": np.nan,
        "micro_reciprocity_mae": np.nan,
        "e95_edge_reciprocity_mae": np.nan,
    }
    for flag, name in [
        ("frontier_pair", "frontier"),
        ("micro_pair", "micro"),
        ("e95_edge_pair", "e95_edge"),
    ]:
        if flag in pred.columns and pred[flag].any():
            yy = pred.loc[pred[flag], "actual_new_better"].to_numpy(dtype=int)
            pp = pred.loc[pred[flag], "prob_new_better"].to_numpy(dtype=np.float64)
            out[f"{name}_n"] = int(len(yy))
            out[f"{name}_accuracy"] = float(np.mean((pp >= 0.5) == yy))
            out[f"{name}_auc"] = safe_auc(yy, pp)
            out[f"{name}_logloss"] = float(log_loss(yy, np.clip(pp, EPS, 1.0 - EPS), labels=[0, 1]))
            if not reciprocity.empty and reciprocity[flag].any():
                out[f"{name}_reciprocity_mae"] = float(
                    reciprocity.loc[reciprocity[flag], "abs_sum_error"].mean()
                )
        else:
            out[f"{name}_n"] = 0
    return out


def file_loo(features: pd.DataFrame, fs: FeatureSet) -> tuple[pd.DataFrame, dict[str, Any]]:
    cols = feature_columns(features, fs)
    rows: list[dict[str, Any]] = []
    for held_file in sorted(set(features["new_file"]).union(set(features["base_file"]))):
        test_mask = features["new_file"].eq(held_file) | features["base_file"].eq(held_file)
        train = features.loc[~test_mask].copy()
        test = features.loc[test_mask].copy()
        if train["actual_new_better"].nunique() < 2 or test.empty:
            continue
        model = make_model()
        model.fit(train[cols], train["actual_new_better"])
        prob = model.predict_proba(test[cols])[:, 1]
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "feature_set": fs.name,
                    "heldout": held_file,
                    "pair_id": rec["pair_id"],
                    "new_file": rec["new_file"],
                    "base_file": rec["base_file"],
                    "actual_delta": rec["actual_delta"],
                    "abs_actual_delta": rec["abs_actual_delta"],
                    "actual_new_better": rec["actual_new_better"],
                    "prob_new_better": float(p),
                    "correct": bool((p >= 0.5) == bool(rec["actual_new_better"])),
                    "frontier_pair": bool(rec["frontier_pair"]),
                    "micro_pair": bool(rec["micro_pair"]),
                    "e95_edge_pair": bool(rec["e95_edge_pair"]),
                }
            )
    return pd.DataFrame(rows), evaluate_predictions(rows, "file", fs.name)


def pair_loo(features: pd.DataFrame, fs: FeatureSet) -> tuple[pd.DataFrame, dict[str, Any]]:
    cols = feature_columns(features, fs)
    rows: list[dict[str, Any]] = []
    for pair_id in sorted(features["pair_id"].unique()):
        test_mask = features["pair_id"].eq(pair_id)
        train = features.loc[~test_mask].copy()
        test = features.loc[test_mask].copy()
        if train["actual_new_better"].nunique() < 2 or test.empty:
            continue
        model = make_model()
        model.fit(train[cols], train["actual_new_better"])
        prob = model.predict_proba(test[cols])[:, 1]
        for rec, p in zip(test.to_dict("records"), prob):
            rows.append(
                {
                    "feature_set": fs.name,
                    "heldout": pair_id,
                    "pair_id": rec["pair_id"],
                    "new_file": rec["new_file"],
                    "base_file": rec["base_file"],
                    "actual_delta": rec["actual_delta"],
                    "abs_actual_delta": rec["abs_actual_delta"],
                    "actual_new_better": rec["actual_new_better"],
                    "prob_new_better": float(p),
                    "correct": bool((p >= 0.5) == bool(rec["actual_new_better"])),
                    "frontier_pair": bool(rec["frontier_pair"]),
                    "micro_pair": bool(rec["micro_pair"]),
                    "e95_edge_pair": bool(rec["e95_edge_pair"]),
                }
            )
    return pd.DataFrame(rows), evaluate_predictions(rows, "pair", fs.name)


def pressure_branch_frame() -> pd.DataFrame:
    raw = pd.read_csv(PRESSURE_CELLS_IN, low_memory=False)
    cells = raw.copy()
    cells["swing"] = pd.to_numeric(cells["range_contribution"], errors="coerce").fillna(
        pd.to_numeric(cells["coeff_abs"], errors="coerce").fillna(0.0)
    )
    cells["support_label"] = pd.to_numeric(cells["min_label"], errors="coerce").fillna(0).astype(int)
    cells["swing_rank"] = cells.groupby(["candidate", "scenario"])["swing"].rank(
        method="first", ascending=False
    )
    for prior in PRIORS:
        src = f"min_label_prob_{prior}"
        if src not in cells.columns:
            raise KeyError(src)
        cells[f"support_probability_{prior}"] = pd.to_numeric(cells[src], errors="coerce")
    return cells


def score_pressure_branches(features: pd.DataFrame, fs: FeatureSet) -> pd.DataFrame:
    cols = feature_columns(features, fs)
    model = make_model()
    model.fit(features[cols], features["actual_new_better"])
    cells = pressure_branch_frame()
    rows: list[dict[str, Any]] = []
    for (candidate, scenario), part in cells.groupby(["candidate", "scenario"]):
        rec = {
            "pair_id": f"{candidate}_{scenario}_min_vs_max",
            "new_file": f"{candidate}_pressure_min",
            "base_file": f"{candidate}_pressure_max",
            "new_score": np.nan,
            "base_score": np.nan,
            "actual_delta": np.nan,
            "actual_new_better": np.nan,
            "abs_actual_delta": np.nan,
            "frontier_pair": False,
            "micro_pair": False,
            "e95_edge_pair": False,
            "orientation_reverse": False,
        }
        for set_name in SETS:
            add_set_features(rec, part.copy(), set_name, reverse=False)
        branch = pd.DataFrame([rec])
        prob = float(model.predict_proba(branch[cols])[:, 1][0])
        rows.append(
            {
                "feature_set": fs.name,
                "candidate": candidate,
                "scenario": scenario,
                "prob_pressure_min_public_better": prob,
                "prefers_favorable_min": bool(prob >= 0.5),
                "n_diff_cells": int(len(part)),
                "top_targets": ",".join(part.sort_values("swing", ascending=False)["target"].head(4).tolist()),
                "between_rate": float(safe_bool(part, "between_train_runs").mean()),
                "e72_active_rate": float(safe_bool(part, "e72_active").mean()),
                "e101_active_rate": float(safe_bool(part, "e101_active").mean()),
            }
        )
    return pd.DataFrame(rows)


def summarize_branch_scores(branches: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (fs, candidate), part in branches.groupby(["feature_set", "candidate"]):
        rows.append(
            {
                "feature_set": fs,
                "candidate": candidate,
                "scenario_count": int(len(part)),
                "prefers_favorable_min_rate": float(part["prefers_favorable_min"].mean()),
                "prob_mean": float(part["prob_pressure_min_public_better"].mean()),
                "prob_min": float(part["prob_pressure_min_public_better"].min()),
                "prob_max": float(part["prob_pressure_min_public_better"].max()),
            }
        )
    return pd.DataFrame(rows)


def write_report(
    known: pd.DataFrame,
    features: pd.DataFrame,
    summary: pd.DataFrame,
    file_pred: pd.DataFrame,
    pair_pred: pd.DataFrame,
    branches: pd.DataFrame,
) -> None:
    best_file = summary[summary["group_col"].eq("file")].sort_values(
        ["e95_edge_accuracy", "frontier_accuracy", "accuracy", "auc"], ascending=False
    ).iloc[0]
    best_pair = summary[summary["group_col"].eq("pair")].sort_values(
        ["e95_edge_accuracy", "frontier_accuracy", "accuracy", "auc"], ascending=False
    ).iloc[0]
    branch_summary = summarize_branch_scores(branches)

    cols_summary = [
        "feature_set",
        "group_col",
        "n_rows",
        "n_groups",
        "accuracy",
        "auc",
        "logloss",
        "frontier_n",
        "frontier_accuracy",
        "frontier_auc",
        "micro_n",
        "micro_accuracy",
        "e95_edge_n",
        "e95_edge_accuracy",
        "reciprocity_mae",
        "frontier_reciprocity_mae",
        "micro_reciprocity_mae",
        "e95_edge_reciprocity_mae",
    ]
    cols_known = ["file", "public_lb", "note"]
    cols_branch = [
        "feature_set",
        "candidate",
        "scenario_count",
        "prefers_favorable_min_rate",
        "prob_mean",
        "prob_min",
        "prob_max",
    ]
    cols_branch_detail = [
        "feature_set",
        "candidate",
        "scenario",
        "prob_pressure_min_public_better",
        "prefers_favorable_min",
        "n_diff_cells",
        "top_targets",
        "between_rate",
        "e72_active_rate",
        "e101_active_rate",
    ]
    hard_file = file_pred[file_pred["e95_edge_pair"]].copy()
    hard_pair = pair_pred[pair_pred["e95_edge_pair"]].copy()
    cols_pred = [
        "feature_set",
        "heldout",
        "new_file",
        "base_file",
        "actual_delta",
        "prob_new_better",
        "correct",
        "frontier_pair",
        "micro_pair",
        "e95_edge_pair",
    ]

    report = f"""# E185 Known-LB Pair Structural Decoder

## Question

E184 showed that a shallow cell-level public-anchor motif is not a reliable
pressure-branch selector. E185 asks whether a broader pair-level movement
representation, trained on all known public-LB submission pairs, can generalize
to an unseen submission and especially to frontier-scale pairs.

## Result In One Sentence

The best leave-one-file decoder is `{best_file['feature_set']}` with overall
accuracy `{float(best_file['accuracy']):.3f}`, frontier accuracy
`{float(best_file['frontier_accuracy']):.3f}`, and E95-edge-band accuracy
`{float(best_file['e95_edge_accuracy']):.3f}`, but its E95-edge reciprocity MAE
is `{float(best_file['e95_edge_reciprocity_mae']):.3f}`. The best
leave-one-pair decoder is `{best_pair['feature_set']}` with E95-edge-band
accuracy `{float(best_pair['e95_edge_accuracy']):.3f}` and reciprocity MAE
`{float(best_pair['e95_edge_reciprocity_mae']):.3f}`. Treat pressure-branch
scores below as diagnostic unless file-LOO, edge-band stress, and reciprocal
orientation sanity are all strong.

## Known Public Files

{md(known, cols_known, n=30)}

## Decoder Stress Summary

{md(summary.sort_values(["group_col", "e95_edge_accuracy", "frontier_accuracy", "accuracy"], ascending=[True, False, False, False]), cols_summary, n=20)}

## E95-Edge-Band File-LOO Predictions

{md(hard_file.sort_values(["feature_set", "abs_actual_delta"]), cols_pred, n=80)}

## E95-Edge-Band Pair-LOO Predictions

{md(hard_pair.sort_values(["feature_set", "abs_actual_delta"]), cols_pred, n=80)}

## Pressure-Branch Scores

{md(branch_summary.sort_values(["feature_set", "candidate"]), cols_branch, n=40)}

## Pressure-Branch Detail

{md(branches.sort_values(["feature_set", "candidate", "scenario"]), cols_branch_detail, n=80)}

## Interpretation

- Leave-one-file is the meaningful stress: a decoder that merely memorizes known
  file quality does not solve the next-submission problem.
- Frontier and E95-edge-band rows are the plateau regime. A model can look good
  on broad bad-vs-good public pairs and still be useless for E95/E101/mixmin
  branch choice.
- Reciprocal sanity matters: for one unordered pair, `P(A beats B) + P(B beats
  A)` should be close to `1`. Large errors are representation collapse, even
  when threshold accuracy looks acceptable.
- If branch preferences flip across feature sets, that is LeJEPA-style
  shortcut/collapse evidence, not a submission ranking signal.

## Decision

No submission is created. Use this audit to decide whether pair-level structural
movement is a real selector or only a coarse public-quality classifier.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def run() -> None:
    known = load_known_scores()
    features = build_oriented_pair_features(known)
    features.to_csv(PAIR_FEATURES_OUT, index=False)

    file_rows: list[pd.DataFrame] = []
    pair_rows: list[pd.DataFrame] = []
    summaries: list[dict[str, Any]] = []
    branches: list[pd.DataFrame] = []

    for fs in FEATURE_SETS:
        f_pred, f_summary = file_loo(features, fs)
        p_pred, p_summary = pair_loo(features, fs)
        file_rows.append(f_pred)
        pair_rows.append(p_pred)
        summaries.extend([f_summary, p_summary])
        branches.append(score_pressure_branches(features, fs))

    file_pred = pd.concat(file_rows, ignore_index=True)
    pair_pred = pd.concat(pair_rows, ignore_index=True)
    summary = pd.DataFrame(summaries)
    branch_scores = pd.concat(branches, ignore_index=True)

    file_pred.to_csv(FILE_LOO_OUT, index=False)
    pair_pred.to_csv(PAIR_LOO_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    branch_scores.to_csv(BRANCH_OUT, index=False)
    write_report(known, features, summary, file_pred, pair_pred, branch_scores)

    print(PAIR_FEATURES_OUT)
    print(FILE_LOO_OUT)
    print(PAIR_LOO_OUT)
    print(SUMMARY_OUT)
    print(BRANCH_OUT)
    print(REPORT_OUT)


if __name__ == "__main__":
    run()
