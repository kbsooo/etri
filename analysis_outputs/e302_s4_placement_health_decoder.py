#!/usr/bin/env python3
"""E302: decode S4 placement health from human diary state.

E301 showed that the S4 direction itself is not random, but subject/dateblock
null placements can reproduce the mean edge. This script treats the E301 actual
and null submissions as a small "placement world" laboratory:

    placement tensor -> human/social/dateblock aggregate features -> selector health

The purpose is not to submit a null placement. It asks whether raw human diary
context can explain which S4 placements are healthy enough to deserve a future
candidate generator.

No public LB is used.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e288_lifestyle_bundle_jepa_audit import TARGETS, build_story_matrix, load_frames, md_table  # noqa: E402
from e295_episode_state_jepa_audit import build_episode_matrix  # noqa: E402
from e300_s4_mean_dominance_rescue import as_bool, load_current_and_meta, rel  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

ACTUAL = OUT / "submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv"
E301_SCORE = OUT / "e301_s4_ready_strict_scores.csv"
E301_NULL_MAP = OUT / "e301_s4_ready_strict_null_map.csv"

SUMMARY_OUT = OUT / "e302_s4_placement_health_summary.csv"
CV_OUT = OUT / "e302_s4_placement_health_cv.csv"
PRED_OUT = OUT / "e302_s4_placement_health_predictions.csv"
FEATURE_OUT = OUT / "e302_s4_placement_health_feature_weights.csv"
BEST_NULL_OUT = OUT / "e302_s4_placement_health_best_nulls.csv"
REPORT_OUT = OUT / "e302_s4_placement_health_report.md"

S4_IDX = TARGETS.index("S4")
RNG_SEED = 20260531 + 302
ALPHA = 25.0


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except Exception:  # noqa: BLE001
        return default
    return out if np.isfinite(out) else default


def md(frame: pd.DataFrame, columns: list[str] | None = None, n: int = 25) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if columns is None else frame.loc[:, [c for c in columns if c in frame.columns]]
    return md_table(view, n=n)


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    keys = frame[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        keys[col] = pd.to_datetime(keys[col]).dt.strftime("%Y-%m-%d")
    keys["subject_id"] = keys["subject_id"].astype(str)
    return keys.reset_index(drop=True)


def load_placement_table() -> pd.DataFrame:
    scores = pd.read_csv(E301_SCORE)
    null_map = pd.read_csv(E301_NULL_MAP)
    mode_map = null_map.set_index("null_basename")["mode"].to_dict()
    keep = scores[scores["basename"].isin([ACTUAL.name, *mode_map.keys()])].copy()
    keep["placement_mode"] = keep["basename"].map(mode_map).fillna("actual")
    keep["is_actual"] = keep["basename"].eq(ACTUAL.name)
    keep["strict_bool"] = keep["strict_promote_gate"].map(as_bool)
    keep["source_path"] = keep["source_path"].astype(str)
    keep.loc[keep["is_actual"], "source_path"] = rel(ACTUAL)
    return keep.reset_index(drop=True)


def test_human_features(current: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base, _raw, stories, feature_frames = load_frames()
    story_matrix, story_meta = build_story_matrix(base, stories, feature_frames)
    episode_matrix, episode_meta = build_episode_matrix(base, feature_frames)

    test_mask = base["split"].eq("test").to_numpy()
    test_base = base.loc[test_mask].sort_values(KEYS).reset_index(drop=True)
    story_test = story_matrix.loc[test_mask].reset_index(drop=True).loc[test_base.index]
    episode_test = episode_matrix.loc[test_mask].reset_index(drop=True).loc[test_base.index]

    if not normalize_keys(test_base).equals(normalize_keys(current)):
        # Sorting after matrix slicing keeps the common E288 layout aligned in
        # current data, but fail closed if this assumption changes.
        merged_order = normalize_keys(current).reset_index().merge(
            normalize_keys(base.loc[test_mask].reset_index(drop=True)).reset_index(),
            on=KEYS,
            how="left",
            suffixes=("_current", "_base"),
            validate="one_to_one",
        )
        if merged_order["index_base"].isna().any():
            raise RuntimeError("Could not align human feature rows to current submission keys")
        order = merged_order["index_base"].astype(int).to_numpy()
        test_base = base.loc[test_mask].reset_index(drop=True).iloc[order].reset_index(drop=True)
        story_test = story_matrix.loc[test_mask].reset_index(drop=True).iloc[order].reset_index(drop=True)
        episode_test = episode_matrix.loc[test_mask].reset_index(drop=True).iloc[order].reset_index(drop=True)
        if not normalize_keys(test_base).equals(normalize_keys(current)):
            raise RuntimeError("Human feature alignment failed")

    blocked = set(KEYS + TARGETS + ["split", "dateblock_group", "subject_id"])
    diary_cols = [
        c
        for c in test_base.columns
        if c not in blocked and pd.api.types.is_numeric_dtype(test_base[c])
    ]
    diary = test_base[diary_cols].copy().add_prefix("diary__")
    story = story_test.add_prefix("story__")
    episode = episode_test.add_prefix("episode__")
    features = pd.concat([diary, story, episode], axis=1)
    features = features.replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)

    meta_rows: list[dict[str, str]] = []
    for col in diary.columns:
        raw = col.replace("diary__", "")
        if raw.startswith("jepa_"):
            family = raw.split("_")[-1]
            text = f"JEPA residual/prednorm diary signal for {family}"
        elif raw.startswith("diary_state"):
            text = "learned day-level diary state geometry"
        else:
            text = raw.replace("_", " ")
        meta_rows.append({"feature": col, "source": "diary", "human_story": text})
    for row in story_meta.to_dict("records"):
        meta_rows.append(
            {
                "feature": f"story__{row['story']}",
                "source": str(row["source"]),
                "human_story": str(row["human_story"]),
            }
        )
    for row in episode_meta.drop_duplicates("episode").to_dict("records"):
        meta_rows.append(
            {
                "feature": f"episode__{row['episode']}",
                "source": "episode",
                "human_story": str(row["human_story"]),
            }
        )
    meta = pd.DataFrame(meta_rows).drop_duplicates("feature")
    return features, meta


def s4_delta_for(path: Path, current: pd.DataFrame) -> np.ndarray:
    pred = load_sub(path, current).sort_values(KEYS).reset_index(drop=True)
    return (
        logit(pred[TARGETS].to_numpy(dtype=np.float64))
        - logit(current[TARGETS].to_numpy(dtype=np.float64))
    )[:, S4_IDX]


def entropy(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=np.float64)
    x = x[x > 0]
    if len(x) == 0:
        return 0.0
    p = x / x.sum()
    return float(-(p * np.log(p + 1.0e-12)).sum() / math.log(len(values) + 1.0e-12))


def aggregate_placement(delta: np.ndarray, row_features: pd.DataFrame, meta: pd.DataFrame) -> dict[str, float]:
    active = np.abs(delta) > 1.0e-12
    pos = delta > 1.0e-12
    neg = delta < -1.0e-12
    abs_w = np.abs(delta)
    abs_sum = float(abs_w.sum())
    signed_sum = float(delta.sum())
    pos_sum = float(delta[pos].sum()) if pos.any() else 0.0
    neg_sum = float(abs_w[neg].sum()) if neg.any() else 0.0
    rec: dict[str, float] = {
        "top__nonzero_rows": float(active.sum()),
        "top__pos_rows": float(pos.sum()),
        "top__neg_rows": float(neg.sum()),
        "top__abs_sum": abs_sum,
        "top__signed_sum": signed_sum,
        "top__pos_abs_sum": pos_sum,
        "top__neg_abs_sum": neg_sum,
        "top__mean_abs_delta_active": float(abs_w[active].mean()) if active.any() else 0.0,
        "top__max_abs_delta": float(abs_w.max()) if len(abs_w) else 0.0,
    }

    for subject, vals in meta.assign(abs_w=abs_w, signed=delta).groupby("subject_id"):
        key = str(subject)
        rec[f"top__subject_abs_share_{key}"] = float(vals["abs_w"].sum() / max(abs_sum, 1.0e-12))
        rec[f"top__subject_signed_share_{key}"] = float(vals["signed"].sum() / max(abs_sum, 1.0e-12))
    date_abs = meta.assign(abs_w=abs_w).groupby("dateblock_group")["abs_w"].sum().to_numpy(dtype=np.float64)
    rec["top__dateblock_abs_entropy"] = entropy(date_abs)
    rec["top__subject_abs_entropy"] = entropy(
        meta.assign(abs_w=abs_w).groupby("subject_id")["abs_w"].sum().to_numpy(dtype=np.float64)
    )

    x = row_features.to_numpy(dtype=np.float64)
    cols = row_features.columns.tolist()
    active_x = x[active]
    pos_x = x[pos]
    neg_x = x[neg]
    for i, col in enumerate(cols):
        vals = x[:, i]
        if abs_sum > 1.0e-12:
            rec[f"human_signed__{col}"] = float(np.dot(delta, vals) / abs_sum)
            rec[f"human_abs__{col}"] = float(np.dot(abs_w, vals) / abs_sum)
        else:
            rec[f"human_signed__{col}"] = 0.0
            rec[f"human_abs__{col}"] = 0.0
        rec[f"human_active_mean__{col}"] = float(active_x[:, i].mean()) if len(active_x) else 0.0
        pmean = float(pos_x[:, i].mean()) if len(pos_x) else 0.0
        nmean = float(neg_x[:, i].mean()) if len(neg_x) else 0.0
        rec[f"human_pos_minus_neg__{col}"] = pmean - nmean
    return rec


def feature_sets(frame: pd.DataFrame) -> dict[str, list[str]]:
    topology = [c for c in frame.columns if c.startswith("top__")]
    story_episode = [
        c
        for c in frame.columns
        if c.startswith("human_") and ("story__" in c or "episode__" in c)
    ]
    human_all = [c for c in frame.columns if c.startswith("human_")]
    return {
        "topology": topology,
        "story_episode": story_episode,
        "human_all": human_all,
        "human_all_plus_topology": [*topology, *human_all],
    }


def spearman_safe(y: np.ndarray, pred: np.ndarray) -> float:
    if len(np.unique(np.round(y, 12))) < 2 or len(np.unique(np.round(pred, 12))) < 2:
        return 0.0
    val = spearmanr(y, pred).correlation
    return float(val) if np.isfinite(val) else 0.0


def ridge_predict(train_x: pd.DataFrame, train_y: np.ndarray, test_x: pd.DataFrame) -> np.ndarray:
    model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=ALPHA))
    model.fit(train_x, train_y)
    return np.asarray(model.predict(test_x), dtype=np.float64)


def logit_predict(train_x: pd.DataFrame, train_y: np.ndarray, test_x: pd.DataFrame) -> np.ndarray:
    if len(np.unique(train_y)) < 2:
        return np.full(len(test_x), float(np.mean(train_y)), dtype=np.float64)
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.25, max_iter=1000, solver="lbfgs"),
    )
    model.fit(train_x, train_y)
    return np.asarray(model.predict_proba(test_x)[:, 1], dtype=np.float64)


def evaluate_feature_sets(frame: pd.DataFrame, sets: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    nulls = frame[~frame["is_actual"]].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    pred_rows: list[pd.DataFrame] = []
    y_mean = nulls["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
    y_p90 = nulls["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
    y_strict = nulls["strict_bool"].astype(int).to_numpy()

    for set_name, cols in sets.items():
        if not cols:
            continue

        for hold_mode in sorted(nulls["placement_mode"].unique()):
            train_mask = ~nulls["placement_mode"].eq(hold_mode).to_numpy()
            test_mask = ~train_mask
            if train_mask.sum() < 10 or test_mask.sum() < 5:
                continue
            x_train = nulls.loc[train_mask, cols]
            x_test = nulls.loc[test_mask, cols]
            mean_pred = ridge_predict(x_train, y_mean[train_mask], x_test)
            p90_pred = ridge_predict(x_train, y_p90[train_mask], x_test)
            strict_pred = logit_predict(x_train, y_strict[train_mask], x_test)
            test_strict = y_strict[test_mask]
            auc = (
                float(roc_auc_score(test_strict, strict_pred))
                if len(np.unique(test_strict)) == 2
                else np.nan
            )
            rows.append(
                {
                    "feature_set": set_name,
                    "cv_type": "leave_mode_out",
                    "holdout": hold_mode,
                    "n_features": len(cols),
                    "n_train": int(train_mask.sum()),
                    "n_test": int(test_mask.sum()),
                    "mean_mae": float(mean_absolute_error(y_mean[test_mask], mean_pred)),
                    "mean_spearman": spearman_safe(y_mean[test_mask], mean_pred),
                    "p90_mae": float(mean_absolute_error(y_p90[test_mask], p90_pred)),
                    "p90_spearman": spearman_safe(y_p90[test_mask], p90_pred),
                    "strict_auc": auc,
                }
            )
            pred_part = nulls.loc[test_mask, ["basename", "placement_mode", "strict_bool", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90"]].copy()
            pred_part["feature_set"] = set_name
            pred_part["cv_type"] = "leave_mode_out"
            pred_part["mean_pred"] = mean_pred
            pred_part["p90_pred"] = p90_pred
            pred_part["strict_pred"] = strict_pred
            pred_rows.append(pred_part)

        kf = KFold(n_splits=5, shuffle=True, random_state=RNG_SEED)
        for fold, (tr, va) in enumerate(kf.split(nulls), start=1):
            mean_pred = ridge_predict(nulls.iloc[tr][cols], y_mean[tr], nulls.iloc[va][cols])
            p90_pred = ridge_predict(nulls.iloc[tr][cols], y_p90[tr], nulls.iloc[va][cols])
            strict_pred = logit_predict(nulls.iloc[tr][cols], y_strict[tr], nulls.iloc[va][cols])
            test_strict = y_strict[va]
            auc = (
                float(roc_auc_score(test_strict, strict_pred))
                if len(np.unique(test_strict)) == 2
                else np.nan
            )
            rows.append(
                {
                    "feature_set": set_name,
                    "cv_type": "random5",
                    "holdout": f"fold{fold}",
                    "n_features": len(cols),
                    "n_train": int(len(tr)),
                    "n_test": int(len(va)),
                    "mean_mae": float(mean_absolute_error(y_mean[va], mean_pred)),
                    "mean_spearman": spearman_safe(y_mean[va], mean_pred),
                    "p90_mae": float(mean_absolute_error(y_p90[va], p90_pred)),
                    "p90_spearman": spearman_safe(y_p90[va], p90_pred),
                    "strict_auc": auc,
                }
            )

    return pd.DataFrame(rows), pd.concat(pred_rows, ignore_index=True) if pred_rows else pd.DataFrame()


def fit_full_predictions(frame: pd.DataFrame, sets: dict[str, list[str]]) -> pd.DataFrame:
    nulls = frame[~frame["is_actual"]].reset_index(drop=True)
    actual = frame[frame["is_actual"]].reset_index(drop=True)
    out_rows = []
    for set_name, cols in sets.items():
        if not cols:
            continue
        mean_model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=ALPHA))
        p90_model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=ALPHA))
        strict_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=0.25, max_iter=1000, solver="lbfgs"),
        )
        mean_model.fit(nulls[cols], nulls["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64))
        p90_model.fit(nulls[cols], nulls["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64))
        y_strict = nulls["strict_bool"].astype(int).to_numpy()
        if len(np.unique(y_strict)) >= 2:
            strict_model.fit(nulls[cols], y_strict)
            strict_pred_all = strict_model.predict_proba(frame[cols])[:, 1]
        else:
            strict_pred_all = np.full(len(frame), float(y_strict.mean()), dtype=np.float64)

        mean_pred_all = mean_model.predict(frame[cols])
        p90_pred_all = p90_model.predict(frame[cols])
        null_mean_pred = mean_pred_all[~frame["is_actual"].to_numpy()]
        null_p90_pred = p90_pred_all[~frame["is_actual"].to_numpy()]
        actual_mean_pred = float(mean_pred_all[frame["is_actual"].to_numpy()][0])
        actual_p90_pred = float(p90_pred_all[frame["is_actual"].to_numpy()][0])
        for i, row in frame.iterrows():
            out_rows.append(
                {
                    "feature_set": set_name,
                    "basename": row["basename"],
                    "placement_mode": row["placement_mode"],
                    "is_actual": bool(row["is_actual"]),
                    "actual_mean": float(row["pred_delta_vs_current_mean"]),
                    "actual_p90": float(row["pred_delta_vs_current_p90"]),
                    "actual_strict": bool(row["strict_bool"]),
                    "mean_pred_full": float(mean_pred_all[i]),
                    "p90_pred_full": float(p90_pred_all[i]),
                    "strict_pred_full": float(strict_pred_all[i]),
                    "actual_mean_pred_rank_pct": float(np.mean(actual_mean_pred > null_mean_pred)) if bool(row["is_actual"]) else np.nan,
                    "actual_p90_pred_rank_pct": float(np.mean(actual_p90_pred > null_p90_pred)) if bool(row["is_actual"]) else np.nan,
                }
            )
    return pd.DataFrame(out_rows)


def feature_weights(frame: pd.DataFrame, sets: dict[str, list[str]], feature_meta: pd.DataFrame) -> pd.DataFrame:
    nulls = frame[~frame["is_actual"]].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    meta = feature_meta.set_index("feature").to_dict("index")
    for set_name, cols in sets.items():
        if not cols:
            continue
        pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=ALPHA))
        pipe.fit(nulls[cols], nulls["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64))
        coef = pipe.named_steps["ridge"].coef_
        for col, weight in zip(cols, coef, strict=False):
            base_feature = col
            for prefix in ["human_signed__", "human_abs__", "human_active_mean__", "human_pos_minus_neg__"]:
                if col.startswith(prefix):
                    base_feature = col.replace(prefix, "")
                    break
            info = meta.get(base_feature, {})
            rows.append(
                {
                    "feature_set": set_name,
                    "aggregate_feature": col,
                    "base_feature": base_feature,
                    "weight_for_lower_mean_is_negative": float(weight),
                    "abs_weight": float(abs(weight)),
                    "source": info.get("source", "topology"),
                    "human_story": info.get("human_story", base_feature.replace("_", " ")),
                }
            )
    return pd.DataFrame(rows).sort_values(["feature_set", "abs_weight"], ascending=[True, False]).reset_index(drop=True)


def write_report(summary: pd.DataFrame, cv: pd.DataFrame, preds: pd.DataFrame, weights: pd.DataFrame, best_nulls: pd.DataFrame) -> None:
    actual_preds = preds[preds["is_actual"]].copy()
    lmo = cv[cv["cv_type"].eq("leave_mode_out")].copy()
    lmo_summary = (
        lmo.groupby("feature_set")
        .agg(
            mean_mae=("mean_mae", "mean"),
            mean_spearman=("mean_spearman", "mean"),
            p90_mae=("p90_mae", "mean"),
            p90_spearman=("p90_spearman", "mean"),
            strict_auc=("strict_auc", "mean"),
        )
        .reset_index()
        .sort_values(["mean_spearman", "strict_auc"], ascending=[False, False])
    )
    top_neg = weights[weights["feature_set"].eq("human_all_plus_topology")].sort_values("weight_for_lower_mean_is_negative").head(15)
    top_pos = weights[weights["feature_set"].eq("human_all_plus_topology")].sort_values("weight_for_lower_mean_is_negative", ascending=False).head(15)
    lines = [
        "# E302 S4 Placement-Health Decoder",
        "",
        "Public LB는 사용하지 않았다. E301 actual/null placement 세계에서 S4 placement health가 human diary representation으로 예측되는지 검사했다.",
        "",
        "## Question",
        "",
        "E301의 실패가 단순한 S4 방향 문제가 아니라 subject/dateblock placement 문제라면, 좋은 placement는 raw human/social/day state aggregate에서 설명되어야 한다.",
        "",
        "## Summary",
        "",
        md(summary, list(summary.columns), n=20),
        "",
        "## Leave-Mode-Out CV",
        "",
        md(lmo_summary, list(lmo_summary.columns), n=10),
        "",
        "## Actual Candidate Predicted Rank",
        "",
        md(
            actual_preds[
                [
                    "feature_set",
                    "actual_mean",
                    "actual_p90",
                    "actual_strict",
                    "mean_pred_full",
                    "p90_pred_full",
                    "strict_pred_full",
                    "actual_mean_pred_rank_pct",
                    "actual_p90_pred_rank_pct",
                ]
            ],
            n=10,
        ),
        "",
        "Interpretation of rank columns: lower predicted mean/p90 is better. A high rank_pct means the model predicts the actual candidate as worse than many null placements.",
        "",
        "## Best Actual Null Placements",
        "",
        md(
            best_nulls[
                [
                    "basename",
                    "placement_mode",
                    "pred_delta_vs_current_mean",
                    "pred_delta_vs_current_p90",
                    "strict_bool",
                ]
            ],
            n=15,
        ),
        "",
        "## Features Associated With Better Mean Edge",
        "",
        md(
            top_neg[
                [
                    "aggregate_feature",
                    "weight_for_lower_mean_is_negative",
                    "source",
                    "human_story",
                ]
            ],
            n=15,
        ),
        "",
        "## Features Associated With Worse Mean Edge",
        "",
        md(
            top_pos[
                [
                    "aggregate_feature",
                    "weight_for_lower_mean_is_negative",
                    "source",
                    "human_story",
                ]
            ],
            n=15,
        ),
        "",
        "## Decision",
        "",
    ]
    best_lmo = lmo_summary.iloc[0] if not lmo_summary.empty else None
    actual_human = actual_preds[actual_preds["feature_set"].eq("human_all_plus_topology")]
    if best_lmo is not None and safe_float(best_lmo["mean_spearman"]) >= 0.25:
        lines.append("- Placement health has some learnable structure, but this is not yet a submission rule.")
    else:
        lines.append("- Placement health is not reliably decoded by the current human diary features under leave-mode-out stress.")
    if not actual_human.empty:
        rec = actual_human.iloc[0]
        lines.append(
            f"- The E300 actual candidate predicted mean rank pct is `{float(rec['actual_mean_pred_rank_pct']):.6f}` under human_all_plus_topology."
        )
    lines += [
        "- Do not submit E300 or any E301 null placement.",
        "- Next useful step: if any feature family has stable leave-mode-out signal, turn it into a constrained subject/dateblock placement prior; otherwise stop S4 mask surgery and return to broader episode/block-state targets.",
        "",
        "## Outputs",
        "",
        f"- `{rel(SUMMARY_OUT)}`",
        f"- `{rel(CV_OUT)}`",
        f"- `{rel(PRED_OUT)}`",
        f"- `{rel(FEATURE_OUT)}`",
        f"- `{rel(BEST_NULL_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    current, meta = load_current_and_meta()
    placements = load_placement_table()
    row_features, feature_meta = test_human_features(current)

    rows = []
    for rec in placements.to_dict("records"):
        path = Path(str(rec["source_path"]))
        if not path.is_absolute():
            path = ROOT / path
        delta = s4_delta_for(path, current)
        agg = aggregate_placement(delta, row_features, meta)
        rows.append({**rec, **agg})
    frame = pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    sets = feature_sets(frame)
    cv, cv_preds = evaluate_feature_sets(frame, sets)
    full_preds = fit_full_predictions(frame, sets)
    weights = feature_weights(frame, sets, feature_meta)
    best_nulls = frame[~frame["is_actual"]].sort_values(
        ["pred_delta_vs_current_mean", "pred_delta_vs_current_p90"]
    ).head(25)

    summary_rows = []
    for mode, part in frame.groupby("placement_mode"):
        summary_rows.append(
            {
                "placement_mode": mode,
                "n": len(part),
                "strict_rate": float(part["strict_bool"].mean()),
                "mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "p90_best": float(part["pred_delta_vs_current_p90"].min()),
            }
        )
    summary = pd.DataFrame(summary_rows).sort_values(["placement_mode"]).reset_index(drop=True)

    summary.to_csv(SUMMARY_OUT, index=False)
    cv.to_csv(CV_OUT, index=False)
    full_preds.to_csv(PRED_OUT, index=False)
    weights.to_csv(FEATURE_OUT, index=False)
    best_nulls.to_csv(BEST_NULL_OUT, index=False)
    write_report(summary, cv, full_preds, weights, best_nulls)

    print(f"placements={len(frame)} nulls={int((~frame['is_actual']).sum())}")
    print(f"feature_sets={','.join(sets.keys())}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
