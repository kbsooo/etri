#!/usr/bin/env python3
"""E308: governed action-outcome atlas.

E279-E307 produced many human/social/JEPA latent states and many materialized
submission candidates. Most failures now have the same shape:

    selector-visible candidate -> matched nulls reproduce it

This script treats those governed candidates as the supervision signal. It
aggregates all available matched-null governors, recomputes outcome quadrants,
and asks whether selector visibility and null rarity are predictable under
leave-experiment-out stress.

No public LB is used. No submission is created.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, mean_absolute_error, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e298_materialization_outcome_atlas import normalize, to_bool  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

GOVERNOR_FILES = [
    OUT / "e279_public_free_governor_summary.csv",
    OUT / "e284_appentropy_decisive_cell_jepa_governor_summary.csv",
    OUT / "e285_e247_residual_human_state_governor_summary.csv",
    OUT / "e286_e247_preserve_avoid_governor_summary.csv",
    OUT / "e287_train_supervised_row_alignment_governor_summary.csv",
    OUT / "e289_target_specific_lifestyle_slice_governor_summary.csv",
    OUT / "e290_lifestyle_row_placement_governor_summary.csv",
    OUT / "e291_lifestyle_block_state_governor_summary.csv",
    OUT / "e292_contrastive_lifestyle_governor_summary.csv",
    OUT / "e293_s4_lownull_governor_summary.csv",
    OUT / "e297_episode_state_materializer_governor.csv",
    OUT / "e299_visibility_null_bridge_governor.csv",
    OUT / "e300_s4_mean_dominance_governor.csv",
    OUT / "e301_s4_ready_strict_governor.csv",
    OUT / "e303_s4_mean_prior_governor.csv",
    OUT / "e305_block_prior_s4_governor.csv",
    OUT / "e306_within_block_s4_governor.csv",
    OUT / "e307_s4_latent_censor_governor.csv",
]

ALL_OUT = OUT / "e308_action_outcome_all.csv"
GROUP_OUT = OUT / "e308_action_outcome_group_summary.csv"
MODEL_OOF_OUT = OUT / "e308_action_outcome_model_oof.csv"
MODEL_SUMMARY_OUT = OUT / "e308_action_outcome_model_summary.csv"
IMPORTANCE_OUT = OUT / "e308_action_outcome_feature_importance.csv"
REPORT_OUT = OUT / "e308_action_outcome_report.md"


OUTCOME_SUBSTRINGS = [
    "null",
    "dominance",
    "ready",
    "decision",
    "outcome",
    "failure",
    "readiness",
    "public_free",
    "placebo",
]
OUTCOME_EXACT = {
    "old_ready_rule",
    "selector_visible",
    "selector_visible_strict",
    "selector_visible_soft",
    "null_rare",
    "null_common",
    "p90_ok",
    "mean_ok",
    "worst_mode_ok",
    "edge_ok",
    "matched_placebo_gate",
    "public_lb_if_known",
    "public_delta_vs_current",
    "known_public_worse_than_current",
}
SAFE_ACTUAL_COLS = {
    "actual_mean",
    "actual_p10",
    "actual_p90",
    "actual_beats_current_rate",
    "incremental_bad_axis_vs_current",
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def as_bool_series(df: pd.DataFrame, col: str) -> pd.Series:
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    return df[col].map(to_bool).astype(bool)


def md(frame: pd.DataFrame, columns: list[str] | None = None, n: int = 25) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if columns is None else frame.loc[:, [c for c in columns if c in frame.columns]]
    out = view.head(n).copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    out = out.fillna("").astype(str)
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *rows])


def experiment_num(exp: str) -> int:
    match = re.search(r"(\d+)", str(exp))
    return int(match.group(1)) if match else -1


def load_all() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in GOVERNOR_FILES:
        if not path.exists():
            continue
        frame = normalize(path)
        frame["loaded_from"] = rel(path)
        frames.append(frame)
    if not frames:
        raise SystemExit("No governor files found")
    all_df = pd.concat(frames, ignore_index=True, sort=False).copy()
    for col in ["actual_mean", "actual_p90", "null_strict_rate", "p90_dominance", "mean_dominance", "worst_mode_p90_dominance"]:
        if col in all_df.columns:
            all_df[col] = pd.to_numeric(all_df[col], errors="coerce")
    all_df["experiment_num"] = all_df["experiment"].map(experiment_num)
    all_df["post_s4_handbuilt"] = all_df["experiment_num"].ge(299)
    all_df["post_e303_s4_handbuilt"] = all_df["experiment_num"].ge(303)
    all_df["visible_null_rare"] = all_df["selector_visible"] & all_df["null_rare"]
    all_df["visible_null_common"] = all_df["selector_visible"] & all_df["null_common"]
    all_df["strict_large_null_ready"] = (
        all_df["selector_visible"]
        & all_df["null_rare"]
        & all_df["p90_ok"]
        & all_df["mean_ok"]
        & all_df["worst_mode_ok"]
        & all_df["edge_ok"]
    )
    # E300 had a small-governor ready row that E301 later rejected; keep the
    # raw label visible but do not count it as certified-ready.
    all_df["known_superseded_ready"] = all_df["basename"].astype(str).str.contains(
        "submission_e300_s4mean_drop_dateblock_id07_b9", regex=False, na=False
    )
    all_df["certified_public_free_ready"] = all_df["strict_large_null_ready"] & ~all_df["known_superseded_ready"]
    return all_df


def group_summary(all_df: pd.DataFrame) -> pd.DataFrame:
    grp = (
        all_df.groupby(["experiment", "target_norm", "family", "outcome_quadrant"], dropna=False)
        .agg(
            n=("basename", "count"),
            selector_visible=("selector_visible", "sum"),
            null_rare=("null_rare", "sum"),
            visible_null_rare=("visible_null_rare", "sum"),
            visible_null_common=("visible_null_common", "sum"),
            certified_ready=("certified_public_free_ready", "sum"),
            best_actual_p90=("actual_p90", "min"),
            best_actual_mean=("actual_mean", "min"),
            median_null_strict=("null_strict_rate", "median"),
            best_null_strict=("null_strict_rate", "min"),
            best_p90_dominance=("p90_dominance", "max"),
            best_mean_dominance=("mean_dominance", "max"),
            best_worst_mode=("worst_mode_p90_dominance", "max"),
        )
        .reset_index()
        .sort_values(["certified_ready", "visible_null_rare", "selector_visible", "best_actual_p90"], ascending=[False, False, False, True])
    )
    return grp


def usable_feature_columns(all_df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric_cols: list[str] = []
    cat_cols: list[str] = []
    for col in all_df.columns:
        if col in OUTCOME_EXACT:
            continue
        if any(part in col.lower() for part in OUTCOME_SUBSTRINGS) and col not in SAFE_ACTUAL_COLS:
            continue
        if col in {"basename", "source_path", "loaded_from", "source_governor_file"}:
            continue
        if pd.api.types.is_numeric_dtype(all_df[col]):
            numeric_cols.append(col)
        elif all_df[col].dtype == object or str(all_df[col].dtype) == "category":
            if all_df[col].nunique(dropna=True) <= 80:
                cat_cols.append(col)
    # Keep the core old-selector/current-anchor features even though they contain
    # "actual"; those are known before null-governor evaluation.
    numeric_cols = list(dict.fromkeys([c for c in numeric_cols if c not in OUTCOME_EXACT]))
    cat_cols = list(dict.fromkeys(cat_cols))
    return numeric_cols, cat_cols


def make_preprocessor(numeric_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    try:
        encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=True, min_frequency=2)
    except TypeError:
        encoder = OneHotEncoder(handle_unknown="ignore")
    return ColumnTransformer(
        [
            ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler(with_mean=False)), numeric_cols),
            ("cat", make_pipeline(SimpleImputer(strategy="most_frequent"), encoder), cat_cols),
        ],
        sparse_threshold=0.30,
    )


def metric_auc(y: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    if len(np.unique(y)) < 2:
        return np.nan, np.nan
    return float(roc_auc_score(y, pred)), float(average_precision_score(y, pred))


def leave_experiment_out_models(all_df: pd.DataFrame, numeric_cols: list[str], cat_cols: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = all_df[numeric_cols + cat_cols].copy()
    groups = all_df["experiment"].astype(str).to_numpy()
    targets = {
        "selector_visible": all_df["selector_visible"].astype(int).to_numpy(),
        "null_rare": all_df["null_rare"].astype(int).to_numpy(),
        "null_common": all_df["null_common"].astype(int).to_numpy(),
        "visible_null_common": all_df["visible_null_common"].astype(int).to_numpy(),
        "edge_ok": all_df["edge_ok"].astype(int).to_numpy(),
    }
    regression_targets = {
        "null_strict_rate": all_df["null_strict_rate"].fillna(1.0).to_numpy(dtype=np.float64),
        "actual_p90": all_df["actual_p90"].fillna(0.01).to_numpy(dtype=np.float64),
    }
    oof_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    for target_name, y in targets.items():
        pred = np.full(len(all_df), np.nan, dtype=np.float64)
        for exp in sorted(set(groups), key=experiment_num):
            va = groups == exp
            tr = ~va
            if len(np.unique(y[tr])) < 2:
                continue
            model = make_pipeline(
                make_preprocessor(numeric_cols, cat_cols),
                LogisticRegression(C=0.25, max_iter=2000, solver="lbfgs", class_weight="balanced"),
            )
            model.fit(x.loc[tr], y[tr])
            pred[va] = model.predict_proba(x.loc[va])[:, 1]
            auc, ap = metric_auc(y[va], pred[va])
            metric_rows.append(
                {
                    "task": target_name,
                    "heldout_experiment": exp,
                    "n_valid": int(va.sum()),
                    "positive_rate": float(np.mean(y[va])),
                    "auc": auc,
                    "average_precision": ap,
                    "pred_mean": float(np.nanmean(pred[va])),
                }
            )
        mask = np.isfinite(pred)
        auc, ap = metric_auc(y[mask], pred[mask])
        metric_rows.append(
            {
                "task": target_name,
                "heldout_experiment": "__global_oof__",
                "n_valid": int(mask.sum()),
                "positive_rate": float(np.mean(y[mask])) if mask.any() else np.nan,
                "auc": auc,
                "average_precision": ap,
                "pred_mean": float(np.nanmean(pred[mask])) if mask.any() else np.nan,
            }
        )
        for idx, val in enumerate(pred):
            if np.isfinite(val):
                oof_rows.append({"row_idx": idx, "task": target_name, "oof_pred": float(val), "label": int(y[idx])})

    for target_name, y in regression_targets.items():
        pred = np.full(len(all_df), np.nan, dtype=np.float64)
        for exp in sorted(set(groups), key=experiment_num):
            va = groups == exp
            tr = ~va
            model = make_pipeline(make_preprocessor(numeric_cols, cat_cols), Ridge(alpha=35.0))
            model.fit(x.loc[tr], y[tr])
            pred[va] = model.predict(x.loc[va])
            corr = spearmanr(y[va], pred[va]).correlation if len(np.unique(np.round(y[va], 10))) > 1 else np.nan
            metric_rows.append(
                {
                    "task": target_name,
                    "heldout_experiment": exp,
                    "n_valid": int(va.sum()),
                    "positive_rate": np.nan,
                    "auc": np.nan,
                    "average_precision": np.nan,
                    "mae": float(mean_absolute_error(y[va], pred[va])),
                    "spearman": float(corr) if np.isfinite(corr) else np.nan,
                    "pred_mean": float(np.nanmean(pred[va])),
                }
            )
        mask = np.isfinite(pred)
        corr = spearmanr(y[mask], pred[mask]).correlation if len(np.unique(np.round(y[mask], 10))) > 1 else np.nan
        metric_rows.append(
            {
                "task": target_name,
                "heldout_experiment": "__global_oof__",
                "n_valid": int(mask.sum()),
                "positive_rate": np.nan,
                "auc": np.nan,
                "average_precision": np.nan,
                "mae": float(mean_absolute_error(y[mask], pred[mask])),
                "spearman": float(corr) if np.isfinite(corr) else np.nan,
                "pred_mean": float(np.nanmean(pred[mask])),
            }
        )
        for idx, val in enumerate(pred):
            if np.isfinite(val):
                oof_rows.append({"row_idx": idx, "task": target_name, "oof_pred": float(val), "label": float(y[idx])})

    return pd.DataFrame(oof_rows), pd.DataFrame(metric_rows)


def feature_importance(all_df: pd.DataFrame, numeric_cols: list[str], cat_cols: list[str]) -> pd.DataFrame:
    x = all_df[numeric_cols + cat_cols].copy()
    y = all_df["null_common"].astype(int).to_numpy()
    if len(np.unique(y)) < 2:
        return pd.DataFrame()
    prep = make_preprocessor(numeric_cols, cat_cols)
    clf = LogisticRegression(C=0.25, max_iter=2000, solver="lbfgs", class_weight="balanced")
    model = make_pipeline(prep, clf)
    model.fit(x, y)
    try:
        names = model.named_steps["columntransformer"].get_feature_names_out()
    except Exception:
        names = np.array([f"f{i}" for i in range(model.named_steps["logisticregression"].coef_.shape[1])])
    coef = model.named_steps["logisticregression"].coef_[0]
    out = pd.DataFrame({"feature": names, "coef_null_common": coef, "abs_coef": np.abs(coef)})
    return out.sort_values("abs_coef", ascending=False).reset_index(drop=True)


def write_report(all_df: pd.DataFrame, group: pd.DataFrame, model_summary: pd.DataFrame, importance: pd.DataFrame, numeric_cols: list[str], cat_cols: list[str]) -> None:
    global_metrics = model_summary[model_summary["heldout_experiment"].eq("__global_oof__")].copy()
    post_s4 = all_df[all_df["post_s4_handbuilt"]].copy()
    post_e303 = all_df[all_df["post_e303_s4_handbuilt"]].copy()
    near = all_df.sort_values(["certified_public_free_ready", "visible_null_rare", "readiness_distance", "actual_p90"], ascending=[False, False, True, True]).head(30)
    lines = [
        "# E308 Governed Action-Outcome Atlas",
        "",
        "Public LB는 사용하지 않았다. E279-E307 matched-null governor 결과를 하나의 supervision table로 묶고, action outcome이 leave-experiment-out으로 예측 가능한지 확인했다.",
        "",
        "## Dataset",
        "",
        f"- governed candidate rows: `{len(all_df)}`",
        f"- experiments loaded: `{all_df['experiment'].nunique()}`",
        f"- numeric features for outcome model: `{len(numeric_cols)}`",
        f"- categorical features for outcome model: `{len(cat_cols)}`",
        "",
        "## Counts",
        "",
        f"- selector_visible: `{int(all_df['selector_visible'].sum())}`",
        f"- null_rare: `{int(all_df['null_rare'].sum())}`",
        f"- visible_null_rare: `{int(all_df['visible_null_rare'].sum())}`",
        f"- strict_large_null_ready raw: `{int(all_df['strict_large_null_ready'].sum())}`",
        f"- certified_public_free_ready after E301 supersession: `{int(all_df['certified_public_free_ready'].sum())}`",
        f"- post-S4-handbuilt rows E299-E307: `{len(post_s4)}`, visible_null_rare `{int(post_s4['visible_null_rare'].sum())}`",
        f"- post-E303 S4 rows: `{len(post_e303)}`, visible_null_rare `{int(post_e303['visible_null_rare'].sum())}`, null_rare `{int(post_e303['null_rare'].sum())}`",
        "",
        "## Leave-Experiment-Out Outcome Models",
        "",
        md(global_metrics, ["task", "n_valid", "positive_rate", "auc", "average_precision", "mae", "spearman", "pred_mean"], n=20),
        "",
        "## Group Summary",
        "",
        md(
            group,
            [
                "experiment",
                "target_norm",
                "family",
                "outcome_quadrant",
                "n",
                "selector_visible",
                "null_rare",
                "visible_null_rare",
                "visible_null_common",
                "best_actual_p90",
                "best_null_strict",
                "best_mean_dominance",
            ],
            n=35,
        ),
        "",
        "## Nearest Rows",
        "",
        md(
            near,
            [
                "experiment",
                "target_norm",
                "family",
                "outcome_quadrant",
                "failure_mode",
                "selector_visible",
                "null_rare",
                "visible_null_rare",
                "actual_p90",
                "null_strict_rate",
                "mean_dominance",
                "basename",
            ],
            n=30,
        ),
        "",
        "## Null-Common Model Top Coefficients",
        "",
        md(importance, ["feature", "coef_null_common", "abs_coef"], n=25),
        "",
        "## Decision",
        "",
    ]
    if int(all_df["certified_public_free_ready"].sum()) > 0:
        lines.append("- A certified public-free candidate exists. It should receive independent confirmation before public LB.")
    else:
        lines.extend(
            [
                "- No certified public-free candidate exists in the governed archive.",
                "- The two visible/null-rare S4 rows before E303 were not enough: one is the E300 small-governor row superseded by E301, and post-E303 S4 action families have `0` null-rare rows.",
                "- The learned outcome table is useful as a diagnostic, but positive labels for `visible_null_rare` are too sparse to generate submissions directly.",
                "- Next high-value experiment should pivot from hand-built S4 deltas to a different target interaction or create synthetic/action-health training labels with explicit controls.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{rel(ALL_OUT)}`",
            f"- `{rel(GROUP_OUT)}`",
            f"- `{rel(MODEL_OOF_OUT)}`",
            f"- `{rel(MODEL_SUMMARY_OUT)}`",
            f"- `{rel(IMPORTANCE_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    all_df = load_all()
    group = group_summary(all_df)
    numeric_cols, cat_cols = usable_feature_columns(all_df)
    oof, model_summary = leave_experiment_out_models(all_df, numeric_cols, cat_cols)
    importance = feature_importance(all_df, numeric_cols, cat_cols)
    all_df.to_csv(ALL_OUT, index=False)
    group.to_csv(GROUP_OUT, index=False)
    oof.to_csv(MODEL_OOF_OUT, index=False)
    model_summary.to_csv(MODEL_SUMMARY_OUT, index=False)
    importance.to_csv(IMPORTANCE_OUT, index=False)
    write_report(all_df, group, model_summary, importance, numeric_cols, cat_cols)
    print(
        "rows={} experiments={} certified_ready={} visible_null_rare={} post_e303_null_rare={}".format(
            len(all_df),
            all_df["experiment"].nunique(),
            int(all_df["certified_public_free_ready"].sum()),
            int(all_df["visible_null_rare"].sum()),
            int(all_df.loc[all_df["post_e303_s4_handbuilt"], "null_rare"].sum()),
        )
    )
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
