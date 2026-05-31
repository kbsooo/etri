#!/usr/bin/env python3
"""E312: action-health world model.

E310/E311 established a sharper bottleneck:

    human/social representations can be real, but visible probability actions
    often become matched-null common.

E312 treats that failure mode as the target representation. The question is not
"which story sounds plausible?" but:

    Can the archive predict whether an action will be selector-visible,
    null-common, or near public-free health before public LB is used?

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
from scipy.stats import ConstantInputWarning, spearmanr
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

from e298_materialization_outcome_atlas import normalize  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=ConstantInputWarning)

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
    OUT / "e310_pair_interaction_governor.csv",
    OUT / "e311_pair_micro_governor.csv",
]

ALL_OUT = OUT / "e312_action_health_all.csv"
METRICS_OUT = OUT / "e312_action_health_metrics.csv"
OOF_OUT = OUT / "e312_action_health_oof.csv"
RISK_OUT = OUT / "e312_action_health_risk_readout.csv"
BLOCK_OUT = OUT / "e312_action_health_feature_blocks.csv"
REPORT_OUT = OUT / "e312_action_health_world_model_report.md"

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
DERIVED_LABELS = {
    "selector_visible",
    "selector_visible_strict",
    "selector_visible_soft",
    "null_rare",
    "null_common",
    "p90_ok",
    "mean_ok",
    "worst_mode_ok",
    "edge_ok",
    "old_ready_rule",
    "visible_null_rare",
    "visible_null_common",
    "strict_large_null_ready",
    "certified_public_free_ready",
    "action_cliff",
    "safe_invisible",
    "edge_and_safe_invisible",
    "strict_health",
    "health_margin",
}
SAFE_NUMERIC_OUTCOME_COLS = {
    "actual_mean",
    "actual_p10",
    "actual_p90",
    "actual_beats_current_rate",
    "incremental_bad_axis_vs_current",
}
ALWAYS_EXCLUDE = {
    "basename",
    "source_path",
    "source_governor_file",
    "loaded_from",
    "final_decision",
    "promotion_decision",
    "old_promotion_decision",
    "experiment_num",
    "public_lb_if_known",
    "public_delta_vs_current",
    "known_public_worse_than_current",
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def md(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".6f") -> str:
    if frame is None or frame.empty:
        return "_empty_"
    out = frame.head(n).copy()
    for col in out.select_dtypes(include=[np.floating]).columns:
        out[col] = out[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
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
        if path.exists():
            frame = normalize(path)
            frame["loaded_from"] = rel(path)
            frames.append(frame)
    if not frames:
        raise SystemExit("no governor files found")
    df = pd.concat(frames, ignore_index=True, sort=False).copy()
    for col in [
        "actual_mean",
        "actual_p10",
        "actual_p90",
        "actual_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "null_count",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "readiness_distance",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["experiment_num"] = df["experiment"].map(experiment_num)
    df["visible_null_rare"] = df["selector_visible"].astype(bool) & df["null_rare"].astype(bool)
    df["visible_null_common"] = df["selector_visible"].astype(bool) & df["null_common"].astype(bool)
    df["action_cliff"] = df["selector_visible"].astype(bool) & ~df["null_rare"].astype(bool)
    df["safe_invisible"] = ~df["selector_visible"].astype(bool) & df["null_rare"].astype(bool)
    df["edge_and_safe_invisible"] = df["safe_invisible"] & df["edge_ok"].astype(bool)
    df["strict_health"] = (
        df["selector_visible"].astype(bool)
        & df["null_rare"].astype(bool)
        & df["p90_ok"].astype(bool)
        & df["mean_ok"].astype(bool)
        & df["worst_mode_ok"].astype(bool)
        & df["edge_ok"].astype(bool)
    )
    df["health_margin"] = -df["readiness_distance"].fillna(10.0)
    return df


def semantic_col(col: str) -> bool:
    text = col.lower()
    keys = [
        "target",
        "family",
        "story",
        "episode",
        "pair",
        "source_family",
        "affected_targets",
        "episodes",
        "pairs",
    ]
    return any(k in text for k in keys)


def geometry_cat_col(col: str) -> bool:
    return col in {"rule", "recipe", "split", "view_id", "delta_mode", "action", "policy", "rules"}


def is_outcome_col(col: str) -> bool:
    if col in DERIVED_LABELS:
        return True
    if col in SAFE_NUMERIC_OUTCOME_COLS:
        return False
    text = col.lower()
    return any(part in text for part in OUTCOME_SUBSTRINGS)


def feature_blocks(df: pd.DataFrame) -> dict[str, tuple[list[str], list[str]]]:
    numeric_safe: list[str] = []
    cat_safe: list[str] = []
    for col in df.columns:
        if col in ALWAYS_EXCLUDE or is_outcome_col(col):
            continue
        if pd.api.types.is_bool_dtype(df[col]):
            numeric_safe.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_safe.append(col)
        elif df[col].dtype == object or str(df[col].dtype) == "category" or pd.api.types.is_string_dtype(df[col]):
            if df[col].nunique(dropna=True) <= 120:
                cat_safe.append(col)

    semantic_cats = [c for c in cat_safe if semantic_col(c)]
    semantic_nums = [c for c in numeric_safe if semantic_col(c)]
    geometry_nums = [c for c in numeric_safe if not semantic_col(c)]
    # Include low-card action syntax in geometry because it describes the
    # materializer, not the human story itself.
    geometry_cats = [
        c
        for c in cat_safe
        if geometry_cat_col(c)
    ]
    blocks = {
        "semantic_only": (semantic_nums, semantic_cats),
        "geometry_only": (geometry_nums, geometry_cats),
        "full_safe": (list(dict.fromkeys(numeric_safe)), list(dict.fromkeys(cat_safe))),
    }
    return blocks


def preprocessor(num_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    try:
        enc = OneHotEncoder(handle_unknown="ignore", min_frequency=2, sparse_output=True)
    except TypeError:
        enc = OneHotEncoder(handle_unknown="ignore")
    return ColumnTransformer(
        [
            ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler(with_mean=False)), num_cols),
            ("cat", make_pipeline(SimpleImputer(strategy="most_frequent"), enc), cat_cols),
        ],
        sparse_threshold=0.30,
    )


def auc_ap(y: np.ndarray, pred: np.ndarray) -> tuple[float, float]:
    if len(np.unique(y)) < 2:
        return np.nan, np.nan
    return float(roc_auc_score(y, pred)), float(average_precision_score(y, pred))


def leave_experiment_out(
    df: pd.DataFrame,
    block_name: str,
    num_cols: list[str],
    cat_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = df[num_cols + cat_cols].copy()
    groups = df["experiment"].astype(str).to_numpy()
    class_targets = {
        "null_common": df["null_common"].astype(int).to_numpy(),
        "null_rare": df["null_rare"].astype(int).to_numpy(),
        "visible_null_common": df["visible_null_common"].astype(int).to_numpy(),
        "action_cliff": df["action_cliff"].astype(int).to_numpy(),
        "safe_invisible": df["safe_invisible"].astype(int).to_numpy(),
        "strict_health": df["strict_health"].astype(int).to_numpy(),
    }
    regression_targets = {
        "null_strict_rate": df["null_strict_rate"].fillna(1.0).to_numpy(dtype=np.float64),
        "readiness_distance": df["readiness_distance"].fillna(10.0).to_numpy(dtype=np.float64),
        "actual_p90": df["actual_p90"].fillna(0.01).to_numpy(dtype=np.float64),
    }
    oof_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    for task, y in class_targets.items():
        pred = np.full(len(df), np.nan, dtype=np.float64)
        for exp in sorted(set(groups), key=experiment_num):
            va = groups == exp
            tr = ~va
            if len(np.unique(y[tr])) < 2:
                continue
            model = make_pipeline(
                preprocessor(num_cols, cat_cols),
                LogisticRegression(C=0.35, max_iter=2500, solver="lbfgs", class_weight="balanced"),
            )
            model.fit(x.loc[tr], y[tr])
            pred[va] = model.predict_proba(x.loc[va])[:, 1]
            auc, ap = auc_ap(y[va], pred[va])
            metric_rows.append(
                {
                    "feature_block": block_name,
                    "task": task,
                    "heldout_experiment": exp,
                    "n_valid": int(va.sum()),
                    "positive_rate": float(np.mean(y[va])),
                    "auc": auc,
                    "average_precision": ap,
                    "pred_mean": float(np.nanmean(pred[va])),
                }
            )
        mask = np.isfinite(pred)
        auc, ap = auc_ap(y[mask], pred[mask])
        metric_rows.append(
            {
                "feature_block": block_name,
                "task": task,
                "heldout_experiment": "__global_oof__",
                "n_valid": int(mask.sum()),
                "positive_rate": float(np.mean(y[mask])) if mask.any() else np.nan,
                "auc": auc,
                "average_precision": ap,
                "pred_mean": float(np.nanmean(pred[mask])) if mask.any() else np.nan,
            }
        )
        for idx, value in enumerate(pred):
            if np.isfinite(value):
                oof_rows.append(
                    {
                        "row_idx": idx,
                        "feature_block": block_name,
                        "task": task,
                        "oof_pred": float(value),
                        "label": int(y[idx]),
                    }
                )

    for task, y in regression_targets.items():
        pred = np.full(len(df), np.nan, dtype=np.float64)
        for exp in sorted(set(groups), key=experiment_num):
            va = groups == exp
            tr = ~va
            model = make_pipeline(preprocessor(num_cols, cat_cols), Ridge(alpha=45.0))
            model.fit(x.loc[tr], y[tr])
            pred[va] = model.predict(x.loc[va])
            corr = spearmanr(y[va], pred[va]).correlation if len(np.unique(np.round(y[va], 10))) > 1 else np.nan
            metric_rows.append(
                {
                    "feature_block": block_name,
                    "task": task,
                    "heldout_experiment": exp,
                    "n_valid": int(va.sum()),
                    "mae": float(mean_absolute_error(y[va], pred[va])),
                    "spearman": float(corr) if np.isfinite(corr) else np.nan,
                    "pred_mean": float(np.nanmean(pred[va])),
                }
            )
        mask = np.isfinite(pred)
        corr = spearmanr(y[mask], pred[mask]).correlation if len(np.unique(np.round(y[mask], 10))) > 1 else np.nan
        metric_rows.append(
            {
                "feature_block": block_name,
                "task": task,
                "heldout_experiment": "__global_oof__",
                "n_valid": int(mask.sum()),
                "mae": float(mean_absolute_error(y[mask], pred[mask])),
                "spearman": float(corr) if np.isfinite(corr) else np.nan,
                "pred_mean": float(np.nanmean(pred[mask])),
            }
        )
        for idx, value in enumerate(pred):
            if np.isfinite(value):
                oof_rows.append(
                    {
                        "row_idx": idx,
                        "feature_block": block_name,
                        "task": task,
                        "oof_pred": float(value),
                        "label": float(y[idx]),
                    }
                )
    return pd.DataFrame(oof_rows), pd.DataFrame(metric_rows)


def build_risk_readout(df: pd.DataFrame, oof: pd.DataFrame) -> pd.DataFrame:
    pivot = oof.pivot_table(index=["row_idx", "feature_block"], columns="task", values="oof_pred", aggfunc="first").reset_index()
    pivot = pivot.rename(columns={c: f"pred_{c}" for c in pivot.columns if c not in {"row_idx", "feature_block"}})
    meta_cols = [
        "experiment",
        "basename",
        "family",
        "target_norm",
        "selector_visible",
        "null_rare",
        "null_common",
        "visible_null_common",
        "strict_health",
        "actual_p90",
        "null_strict_rate",
        "readiness_distance",
        "failure_mode",
    ]
    meta = df[[c for c in meta_cols if c in df.columns]].reset_index().rename(columns={"index": "row_idx"})
    out = pivot.merge(meta, on="row_idx", how="left")
    if "pred_readiness_distance" in out.columns:
        out["pred_health_rank"] = -out["pred_readiness_distance"].rank(method="average")
    if {"pred_null_rare", "pred_null_common", "actual_p90"}.issubset(out.columns):
        out["pred_submission_hope"] = (
            out["pred_null_rare"].astype(float)
            * (1.0 - out["pred_null_common"].astype(float))
            * np.maximum(0.0, -out["actual_p90"].fillna(0.0).astype(float) / 0.001)
        )
    else:
        out["pred_submission_hope"] = 0.0
    return out.sort_values(
        ["feature_block", "pred_submission_hope", "actual_p90"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def block_summary(blocks: dict[str, tuple[list[str], list[str]]]) -> pd.DataFrame:
    rows = []
    for name, (num_cols, cat_cols) in blocks.items():
        rows.append(
            {
                "feature_block": name,
                "numeric_cols": len(num_cols),
                "categorical_cols": len(cat_cols),
                "sample_numeric": ", ".join(num_cols[:8]),
                "sample_categorical": ", ".join(cat_cols[:8]),
            }
        )
    return pd.DataFrame(rows)


def write_report(df: pd.DataFrame, metrics: pd.DataFrame, risk: pd.DataFrame, block_df: pd.DataFrame) -> None:
    global_metrics = metrics[metrics["heldout_experiment"].eq("__global_oof__")].copy()
    task_order = ["null_common", "null_rare", "visible_null_common", "action_cliff", "safe_invisible", "strict_health", "null_strict_rate", "readiness_distance"]
    global_metrics["task_order"] = global_metrics["task"].map({t: i for i, t in enumerate(task_order)}).fillna(99)
    global_metrics = global_metrics.sort_values(["task_order", "feature_block"])
    e310_e311 = risk[risk["experiment"].isin(["e310", "e311"]) & risk["feature_block"].eq("full_safe")].copy()
    top_hope = e310_e311.sort_values(["pred_submission_hope", "actual_p90"], ascending=[False, True]).head(20)
    by_exp = (
        df.groupby("experiment", dropna=False)
        .agg(
            rows=("basename", "count"),
            selector_visible=("selector_visible", "sum"),
            null_rare=("null_rare", "sum"),
            visible_null_rare=("visible_null_rare", "sum"),
            visible_null_common=("visible_null_common", "sum"),
            strict_health=("strict_health", "sum"),
            best_p90=("actual_p90", "min"),
            best_null_strict=("null_strict_rate", "min"),
        )
        .reset_index()
        .sort_values("experiment", key=lambda s: s.map(experiment_num))
    )
    lines = [
        "# E312 Action-Health World Model",
        "",
        "Public LB는 사용하지 않았다. E310/E311 이후 병목을 `human story -> target delta`가 아니라 `candidate action -> visible/null-rare health`로 재정의해 검증했다.",
        "",
        "## Data",
        "",
        f"- governed rows: `{len(df)}`",
        f"- experiments: `{df['experiment'].nunique()}`",
        f"- selector_visible: `{int(df['selector_visible'].sum())}`",
        f"- null_rare: `{int(df['null_rare'].sum())}`",
        f"- visible_null_rare: `{int(df['visible_null_rare'].sum())}`",
        f"- strict_health: `{int(df['strict_health'].sum())}`",
        "",
        md(by_exp, n=40),
        "",
        "## Feature Blocks",
        "",
        md(block_df, n=10),
        "",
        "## Leave-Experiment-Out Metrics",
        "",
        md(
            global_metrics[
                [
                    "feature_block",
                    "task",
                    "n_valid",
                    "positive_rate",
                    "auc",
                    "average_precision",
                    "mae",
                    "spearman",
                    "pred_mean",
                ]
            ],
            n=80,
        ),
        "",
        "## E310/E311 Held-Out Risk Readout",
        "",
        md(
            top_hope[
                [
                    "experiment",
                    "basename",
                    "family",
                    "target_norm",
                    "selector_visible",
                    "null_rare",
                    "null_common",
                    "actual_p90",
                    "null_strict_rate",
                    "pred_submission_hope",
                    "failure_mode",
                ]
            ],
            n=20,
        ),
        "",
        "## Decision",
        "",
    ]
    full = global_metrics[global_metrics["feature_block"].eq("full_safe")]
    geom = global_metrics[global_metrics["feature_block"].eq("geometry_only")]
    semantic = global_metrics[global_metrics["feature_block"].eq("semantic_only")]
    def metric_value(frame: pd.DataFrame, task: str, col: str) -> float:
        vals = frame.loc[frame["task"].eq(task), col]
        return float(vals.iloc[0]) if len(vals) and pd.notna(vals.iloc[0]) else np.nan

    full_null_common_auc = metric_value(full, "null_common", "auc")
    geom_null_common_auc = metric_value(geom, "null_common", "auc")
    sem_null_common_auc = metric_value(semantic, "null_common", "auc")
    full_dist_spearman = metric_value(full, "readiness_distance", "spearman")
    lines.extend(
        [
            f"- full_safe null_common OOF AUC: `{full_null_common_auc:.6f}`",
            f"- geometry_only null_common OOF AUC: `{geom_null_common_auc:.6f}`",
            f"- semantic_only null_common OOF AUC: `{sem_null_common_auc:.6f}`",
            f"- full_safe readiness_distance OOF Spearman: `{full_dist_spearman:.6f}`",
            "- If geometry is close to full and semantic is weaker, the current bottleneck is action geometry rather than lack of social stories.",
            "- If E310/E311 top predicted hope rows are still actual null-common or too-small, outcome modeling is currently a blocker/gate, not a submission generator.",
            "- Next useful experiment should generate a new action class with different geometry, or learn local row/block action health from richer synthetic controls before materialization.",
        ]
    )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{ALL_OUT.relative_to(ROOT)}`",
            f"- `{METRICS_OUT.relative_to(ROOT)}`",
            f"- `{OOF_OUT.relative_to(ROOT)}`",
            f"- `{RISK_OUT.relative_to(ROOT)}`",
            f"- `{BLOCK_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = load_all()
    blocks = feature_blocks(df)
    block_df = block_summary(blocks)
    oof_frames: list[pd.DataFrame] = []
    metric_frames: list[pd.DataFrame] = []
    for name, (num_cols, cat_cols) in blocks.items():
        if not num_cols and not cat_cols:
            continue
        oof, metrics = leave_experiment_out(df, name, num_cols, cat_cols)
        oof_frames.append(oof)
        metric_frames.append(metrics)
    oof_all = pd.concat(oof_frames, ignore_index=True)
    metrics_all = pd.concat(metric_frames, ignore_index=True)
    risk = build_risk_readout(df, oof_all)

    df.to_csv(ALL_OUT, index=False)
    metrics_all.to_csv(METRICS_OUT, index=False)
    oof_all.to_csv(OOF_OUT, index=False)
    risk.to_csv(RISK_OUT, index=False)
    block_df.to_csv(BLOCK_OUT, index=False)
    write_report(df, metrics_all, risk, block_df)

    global_metrics = metrics_all[metrics_all["heldout_experiment"].eq("__global_oof__")]
    def val(block: str, task: str, col: str) -> float:
        vals = global_metrics.loc[
            global_metrics["feature_block"].eq(block) & global_metrics["task"].eq(task),
            col,
        ]
        return float(vals.iloc[0]) if len(vals) and pd.notna(vals.iloc[0]) else np.nan

    print(f"rows={len(df)} experiments={df['experiment'].nunique()}")
    print(f"visible_null_rare={int(df['visible_null_rare'].sum())} strict_health={int(df['strict_health'].sum())}")
    print(f"full_null_common_auc={val('full_safe','null_common','auc'):.6f}")
    print(f"geometry_null_common_auc={val('geometry_only','null_common','auc'):.6f}")
    print(f"semantic_null_common_auc={val('semantic_only','null_common','auc'):.6f}")
    print(f"full_readiness_spearman={val('full_safe','readiness_distance','spearman'):.6f}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
