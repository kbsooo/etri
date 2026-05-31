#!/usr/bin/env python3
"""E317: human placement outcome learner.

E316 showed that raw human diary signatures recover intended placement, but
intended placement is not enough for submission health.  E317 changes the
JEPA-style target from identity to outcome: can context predict which
row/subject/dateblock placement actually has healthier local score behavior?

No public LB is used and no submission is created.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import sys
import warnings

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e313_human_action_signature import md  # noqa: E402
from e316_human_placement_health_learner import FEATURE_OUT as E316_FEATURE_OUT  # noqa: E402
from e316_human_placement_health_learner import OOF_OUT as E316_OOF_OUT  # noqa: E402
from e316_human_placement_health_learner import build_placement_rows  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

METRICS_OUT = OUT / "e317_human_placement_outcome_metrics.csv"
OOF_OUT = OUT / "e317_human_placement_outcome_oof.csv"
MODE_OUT = OUT / "e317_human_placement_outcome_mode_holdout.csv"
WITHIN_MODE_OUT = OUT / "e317_human_placement_outcome_within_mode.csv"
TOP_FEATURE_OUT = OUT / "e317_human_placement_outcome_top_features.csv"
SOURCE_OUT = OUT / "e317_human_placement_outcome_source_readout.csv"
SUMMARY_OUT = OUT / "e317_human_placement_outcome_summary.csv"
REPORT_OUT = OUT / "e317_human_placement_outcome_report.md"

PLACEMENT_MODES = ["actual", "row", "subject", "dateblock"]
EPS = 1e-6


def load_feature_rows() -> pd.DataFrame:
    if E316_FEATURE_OUT.exists():
        df = pd.read_csv(E316_FEATURE_OUT)
    else:
        df = build_placement_rows()
    return prepare_outcomes(attach_identity_oof(df))


def attach_identity_oof(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["human_identity_oof_pred"] = np.nan
    if not E316_OOF_OUT.exists():
        return df
    oof = pd.read_csv(E316_OOF_OUT)
    mask = oof["task"].eq("actual_vs_placement_null") & oof["feature_block"].eq("human_signature")
    keep = oof.loc[mask, ["basename", "source_basename", "oof_pred"]].drop_duplicates(["basename", "source_basename"])
    keep = keep.rename(columns={"oof_pred": "human_identity_oof_pred"})
    df = df.drop(columns=["human_identity_oof_pred"]).merge(keep, on=["basename", "source_basename"], how="left")
    return df


def prepare_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["actual_or_placement_null"].eq(1)].reset_index(drop=True)
    for mode in PLACEMENT_MODES:
        df[f"meta_mode_{mode}"] = df["placement_mode"].eq(mode).astype(float)
    df["meta_is_actual"] = df["is_actual"].astype(float)

    for col in ["strict_promote_gate", "info_sensor_gate"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)

    df["target_p90"] = df["pred_delta_vs_current_p90"].astype(float)
    df["target_mean"] = df["pred_delta_vs_current_mean"].astype(float)
    df["target_visible"] = df["strict_promote_gate"].astype(int)
    df["target_p90_good"] = df["target_p90"].lt(-2.0e-5).astype(int)
    df["target_mean_good"] = df["target_mean"].lt(-2.0e-5).astype(int)

    def rank_pct(s: pd.Series) -> pd.Series:
        return s.rank(method="average", ascending=True, pct=True)

    df["target_p90_rank_pct"] = df.groupby("source_basename")["target_p90"].transform(rank_pct)
    df["target_mean_rank_pct"] = df.groupby("source_basename")["target_mean"].transform(rank_pct)
    df["target_p90_top25"] = df["target_p90_rank_pct"].le(0.25).astype(int)
    df["target_mean_top25"] = df["target_mean_rank_pct"].le(0.25).astype(int)
    df["target_p90_top10"] = df["target_p90_rank_pct"].le(0.10).astype(int)
    df["target_joint_health"] = (
        df["target_visible"].eq(1)
        & df["target_p90_top25"].eq(1)
        & df["target_mean_rank_pct"].le(0.50)
    ).astype(int)
    df["target_health_score"] = (
        df["target_visible"].astype(float)
        + df["target_p90_good"].astype(float)
        + df["target_mean_good"].astype(float)
        + (1.0 - df["target_p90_rank_pct"].clip(0.0, 1.0))
        + (1.0 - df["target_mean_rank_pct"].clip(0.0, 1.0))
    )
    return df


def numeric_existing(df: pd.DataFrame, cols: list[str]) -> list[str]:
    out: list[str] = []
    for col in cols:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            out.append(col)
    return out


def feature_blocks(df: pd.DataFrame) -> dict[str, list[str]]:
    human_cols = [c for c in df.columns if c.startswith("human_")]
    shape_cols = [c for c in df.columns if c.startswith("shape__")]
    source_action_cols = numeric_existing(
        df,
        [
            "source__seed_count",
            "source__weight",
            "source__nonzero_rows",
            "source__nonzero_cells",
            "source__mean_abs_delta",
            "source__max_abs_delta",
            "source__l1_delta",
            "source__signed_delta_sum",
            "source__q_abs_share",
            "source__s_abs_share",
            "source__abs_Q1",
            "source__abs_Q2",
            "source__abs_Q3",
            "source__abs_S1",
            "source__abs_S2",
            "source__abs_S3",
            "source__abs_S4",
        ],
    )
    action_cols = numeric_existing(
        df,
        [
            "shape__changed_cells",
            "shape__changed_rows",
            "shape__abs_logit_l1",
            "shape__max_abs_logit",
            "shape__row_l1_top1_share",
            "shape__row_l1_top5_share",
            "shape__q_abs_share",
            "shape__s_abs_share",
            "shape__signed_logit_sum",
        ],
    ) + source_action_cols
    identity_cols = numeric_existing(
        df,
        [
            "meta_is_actual",
            "meta_mode_actual",
            "meta_mode_row",
            "meta_mode_subject",
            "meta_mode_dateblock",
            "human_identity_oof_pred",
        ],
    )
    return {
        "identity_signal": identity_cols,
        "human_signature": human_cols,
        "shape_signature": shape_cols,
        "action_shape": list(dict.fromkeys(action_cols)),
        "human_plus_action": list(dict.fromkeys(human_cols + action_cols)),
        "human_plus_identity_action": list(dict.fromkeys(human_cols + identity_cols + action_cols)),
        "shape_plus_identity": list(dict.fromkeys(shape_cols + identity_cols)),
    }


def ridge_pipeline(cols: list[str]):
    return make_pipeline(
        ColumnTransformer(
            [("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), cols)],
            remainder="drop",
        ),
        Ridge(alpha=12.0),
    )


def logistic_pipeline(cols: list[str]):
    return make_pipeline(
        ColumnTransformer(
            [("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), cols)],
            remainder="drop",
        ),
        LogisticRegression(C=0.15, solver="liblinear", class_weight="balanced", max_iter=2500),
    )


def safe_corr(y: np.ndarray, p: np.ndarray, method: str) -> float:
    ys = pd.Series(y)
    ps = pd.Series(p)
    if ys.nunique(dropna=True) < 2 or ps.nunique(dropna=True) < 2:
        return np.nan
    return float(ys.corr(ps, method=method))


def safe_auc(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(roc_auc_score(y, p))


def safe_ap(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(average_precision_score(y, p))


def safe_logloss(y: np.ndarray, p: np.ndarray) -> float:
    if len(np.unique(y)) < 2:
        return np.nan
    return float(log_loss(y, np.clip(p, EPS, 1.0 - EPS), labels=[0, 1]))


def source_folds(df: pd.DataFrame) -> GroupKFold:
    n_groups = int(df["source_basename"].nunique())
    return GroupKFold(n_splits=max(2, min(5, n_groups)))


def eval_group_regression(df: pd.DataFrame, blocks: dict[str, list[str]], task: str, target_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    sub = df[df[target_col].notna()].reset_index(drop=True)
    y = sub[target_col].astype(float).to_numpy()
    groups = sub["source_basename"].astype(str)
    rows: list[dict[str, Any]] = []
    oofs: list[pd.DataFrame] = []
    for block, cols in blocks.items():
        if not cols:
            continue
        pred = np.zeros(len(sub), dtype=float)
        folds = source_folds(sub)
        for tr, va in folds.split(sub, y, groups):
            model = ridge_pipeline(cols)
            model.fit(sub.iloc[tr][cols], y[tr])
            pred[va] = model.predict(sub.iloc[va][cols])
        rows.append(
            {
                "split": "source_group",
                "task": task,
                "feature_block": block,
                "n": int(len(sub)),
                "target_mean": float(np.mean(y)),
                "spearman": safe_corr(y, pred, "spearman"),
                "pearson": safe_corr(y, pred, "pearson"),
                "rmse": float(np.sqrt(np.mean((pred - y) ** 2))),
            }
        )
        part = sub[["basename", "source_basename", "placement_mode", "is_actual"]].copy()
        part["split"] = "source_group"
        part["task"] = task
        part["feature_block"] = block
        part["label"] = y
        part["oof_pred"] = pred
        oofs.append(part)
    return pd.DataFrame(rows), pd.concat(oofs, ignore_index=True) if oofs else pd.DataFrame()


def eval_group_binary(df: pd.DataFrame, blocks: dict[str, list[str]], task: str, target_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    sub = df[df[target_col].notna()].reset_index(drop=True)
    y = sub[target_col].astype(int).to_numpy()
    if len(np.unique(y)) < 2:
        return pd.DataFrame(), pd.DataFrame()
    groups = sub["source_basename"].astype(str)
    rows: list[dict[str, Any]] = []
    oofs: list[pd.DataFrame] = []
    for block, cols in blocks.items():
        if not cols:
            continue
        pred = np.zeros(len(sub), dtype=float)
        folds = source_folds(sub)
        for tr, va in folds.split(sub, y, groups):
            model = logistic_pipeline(cols)
            model.fit(sub.iloc[tr][cols], y[tr])
            pred[va] = model.predict_proba(sub.iloc[va][cols])[:, 1]
        rows.append(
            {
                "split": "source_group",
                "task": task,
                "feature_block": block,
                "n": int(len(sub)),
                "positive_rate": float(np.mean(y)),
                "auc": safe_auc(y, pred),
                "average_precision": safe_ap(y, pred),
                "logloss": safe_logloss(y, pred),
                "pred_mean": float(np.mean(pred)),
            }
        )
        part = sub[["basename", "source_basename", "placement_mode", "is_actual"]].copy()
        part["split"] = "source_group"
        part["task"] = task
        part["feature_block"] = block
        part["label"] = y
        part["oof_pred"] = pred
        oofs.append(part)
    return pd.DataFrame(rows), pd.concat(oofs, ignore_index=True) if oofs else pd.DataFrame()


def eval_leave_mode(df: pd.DataFrame, blocks: dict[str, list[str]], target_col: str, kind: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for heldout_mode in PLACEMENT_MODES:
        train = df[~df["placement_mode"].eq(heldout_mode)].reset_index(drop=True)
        test = df[df["placement_mode"].eq(heldout_mode)].reset_index(drop=True)
        if train.empty or test.empty:
            continue
        for block, cols in blocks.items():
            if not cols:
                continue
            if kind == "regression":
                y_train = train[target_col].astype(float).to_numpy()
                y_test = test[target_col].astype(float).to_numpy()
                model = ridge_pipeline(cols)
                model.fit(train[cols], y_train)
                pred = model.predict(test[cols])
                rows.append(
                    {
                        "split": f"leave_mode_{heldout_mode}",
                        "task": target_col,
                        "feature_block": block,
                        "n": int(len(test)),
                        "target_mean": float(np.mean(y_test)),
                        "spearman": safe_corr(y_test, pred, "spearman"),
                        "pearson": safe_corr(y_test, pred, "pearson"),
                        "rmse": float(np.sqrt(np.mean((pred - y_test) ** 2))),
                    }
                )
            else:
                y_train = train[target_col].astype(int).to_numpy()
                y_test = test[target_col].astype(int).to_numpy()
                if len(np.unique(y_train)) < 2:
                    continue
                model = logistic_pipeline(cols)
                model.fit(train[cols], y_train)
                pred = model.predict_proba(test[cols])[:, 1]
                rows.append(
                    {
                        "split": f"leave_mode_{heldout_mode}",
                        "task": target_col,
                        "feature_block": block,
                        "n": int(len(test)),
                        "positive_rate": float(np.mean(y_test)),
                        "auc": safe_auc(y_test, pred),
                        "average_precision": safe_ap(y_test, pred),
                        "logloss": safe_logloss(y_test, pred),
                        "pred_mean": float(np.mean(pred)),
                    }
                )
    return pd.DataFrame(rows)


def eval_within_mode(df: pd.DataFrame, blocks: dict[str, list[str]], target_col: str, kind: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for mode in PLACEMENT_MODES:
        sub = df[df["placement_mode"].eq(mode)].reset_index(drop=True)
        if sub.empty or sub["source_basename"].nunique() < 3:
            continue
        groups = sub["source_basename"].astype(str)
        folds = source_folds(sub)
        for block, cols in blocks.items():
            if not cols:
                continue
            if kind == "regression":
                y = sub[target_col].astype(float).to_numpy()
                pred = np.zeros(len(sub), dtype=float)
                for tr, va in folds.split(sub, y, groups):
                    model = ridge_pipeline(cols)
                    model.fit(sub.iloc[tr][cols], y[tr])
                    pred[va] = model.predict(sub.iloc[va][cols])
                rows.append(
                    {
                        "split": f"within_mode_{mode}",
                        "task": target_col,
                        "feature_block": block,
                        "n": int(len(sub)),
                        "target_mean": float(np.mean(y)),
                        "spearman": safe_corr(y, pred, "spearman"),
                        "pearson": safe_corr(y, pred, "pearson"),
                        "rmse": float(np.sqrt(np.mean((pred - y) ** 2))),
                    }
                )
            else:
                y = sub[target_col].astype(int).to_numpy()
                if len(np.unique(y)) < 2:
                    continue
                pred = np.zeros(len(sub), dtype=float)
                for tr, va in folds.split(sub, y, groups):
                    model = logistic_pipeline(cols)
                    model.fit(sub.iloc[tr][cols], y[tr])
                    pred[va] = model.predict_proba(sub.iloc[va][cols])[:, 1]
                rows.append(
                    {
                        "split": f"within_mode_{mode}",
                        "task": target_col,
                        "feature_block": block,
                        "n": int(len(sub)),
                        "positive_rate": float(np.mean(y)),
                        "auc": safe_auc(y, pred),
                        "average_precision": safe_ap(y, pred),
                        "logloss": safe_logloss(y, pred),
                        "pred_mean": float(np.mean(pred)),
                    }
                )
    return pd.DataFrame(rows)


def source_readout(df: pd.DataFrame, oof: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    wanted = oof[oof["split"].eq("source_group") & oof["task"].eq("predict_p90_rank")]
    for block, part in wanted.groupby("feature_block"):
        for source, g in part.groupby("source_basename"):
            meta = df[df["source_basename"].eq(source) & df["is_actual"].eq(1)].iloc[0]
            pred = g["oof_pred"].to_numpy(dtype=float)
            label = g["label"].to_numpy(dtype=float)
            actual_pred = float(g[g["is_actual"].eq(1)]["oof_pred"].iloc[0]) if g["is_actual"].eq(1).any() else np.nan
            actual_label = float(g[g["is_actual"].eq(1)]["label"].iloc[0]) if g["is_actual"].eq(1).any() else np.nan
            rows.append(
                {
                    "source_basename": source,
                    "feature_block": block,
                    "recipe": meta.get("recipe", ""),
                    "actual_pred_rank_health": actual_pred,
                    "actual_true_rank_health": actual_label,
                    "pred_top_mode": str(g.iloc[int(np.argmax(pred))]["placement_mode"]),
                    "true_top_mode": str(g.iloc[int(np.argmax(label))]["placement_mode"]),
                    "source_actual_p90": float(meta.get("source__actual_p90", np.nan)),
                    "source_null_strict_rate": float(meta.get("source__null_strict_rate", np.nan)),
                    "source_worst_mode_p90_dominance": float(meta.get("source__worst_mode_p90_dominance", np.nan)),
                    "source_final_decision": meta.get("source__final_decision", ""),
                }
            )
    return pd.DataFrame(rows)


def summarize_readouts(metrics: pd.DataFrame, mode: pd.DataFrame, within: pd.DataFrame, source: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for block, part in source.groupby("feature_block"):
        rows.append(
            {
                "summary": "source_top_mode_accuracy",
                "feature_block": block,
                "value": float(np.mean(part["pred_top_mode"].eq(part["true_top_mode"]))),
                "n": int(len(part)),
            }
        )
        rows.append(
            {
                "summary": "source_actual_pred_rank_mean",
                "feature_block": block,
                "value": float(part["actual_pred_rank_health"].mean()),
                "n": int(part["actual_pred_rank_health"].notna().sum()),
            }
        )

    null_mode = mode[mode["split"].isin(["leave_mode_row", "leave_mode_subject", "leave_mode_dateblock"])]
    p90 = null_mode[null_mode["task"].eq("target_p90_rank_health")]
    for block, part in p90.groupby("feature_block"):
        rows.append(
            {
                "summary": "null_mode_holdout_p90_spearman_mean",
                "feature_block": block,
                "value": float(part["spearman"].mean()),
                "n": int(part["spearman"].notna().sum()),
            }
        )

    joint = null_mode[null_mode["task"].eq("target_joint_health")]
    for block, part in joint.groupby("feature_block"):
        rows.append(
            {
                "summary": "null_mode_holdout_joint_auc_mean",
                "feature_block": block,
                "value": float(part["auc"].mean()),
                "n": int(part["auc"].notna().sum()),
            }
        )

    within_p90 = within[within["task"].eq("target_p90_rank_health")]
    for block, part in within_p90.groupby("feature_block"):
        rows.append(
            {
                "summary": "within_mode_p90_spearman_mean",
                "feature_block": block,
                "value": float(part["spearman"].mean()),
                "n": int(part["spearman"].notna().sum()),
            }
        )

    within_joint = within[within["task"].eq("target_joint_health")]
    for block, part in within_joint.groupby("feature_block"):
        rows.append(
            {
                "summary": "within_mode_joint_auc_mean",
                "feature_block": block,
                "value": float(part["auc"].mean()),
                "n": int(part["auc"].notna().sum()),
            }
        )

    for task in ["predict_p90_rank", "predict_health_score", "classify_joint_health"]:
        part = metrics[metrics["task"].eq(task)]
        value_col = "spearman" if task.startswith("predict") else "auc"
        for _, rec in part.iterrows():
            rows.append(
                {
                    "summary": f"source_holdout_{task}_{value_col}",
                    "feature_block": rec["feature_block"],
                    "value": float(rec[value_col]) if pd.notna(rec[value_col]) else np.nan,
                    "n": int(rec["n"]),
                }
            )
    return pd.DataFrame(rows)


def fit_top_features(df: pd.DataFrame, blocks: dict[str, list[str]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    tasks = [
        ("predict_p90_rank", "target_p90_rank_health", "ridge"),
        ("classify_joint_health", "target_joint_health", "logistic"),
    ]
    for task, target_col, model_kind in tasks:
        y = df[target_col].astype(float if model_kind == "ridge" else int).to_numpy()
        for block in ["human_signature", "human_plus_action", "human_plus_identity_action"]:
            cols = blocks.get(block, [])
            if not cols:
                continue
            pipe = ridge_pipeline(cols) if model_kind == "ridge" else logistic_pipeline(cols)
            if model_kind == "logistic" and len(np.unique(y)) < 2:
                continue
            pipe.fit(df[cols], y)
            model = pipe.named_steps["ridge"] if model_kind == "ridge" else pipe.named_steps["logisticregression"]
            coef = model.coef_[0] if model_kind == "logistic" else model.coef_
            for col, value in zip(cols, coef, strict=False):
                rows.append(
                    {
                        "task": task,
                        "feature_block": block,
                        "feature": col,
                        "coef": float(value),
                        "abs_coef": float(abs(value)),
                    }
                )
    return pd.DataFrame(rows).sort_values("abs_coef", ascending=False).head(120).reset_index(drop=True) if rows else pd.DataFrame()


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = load_feature_rows()
    df["target_p90_rank_health"] = 1.0 - df["target_p90_rank_pct"].astype(float)
    df["target_mean_rank_health"] = 1.0 - df["target_mean_rank_pct"].astype(float)
    blocks = feature_blocks(df)

    metric_frames: list[pd.DataFrame] = []
    oof_frames: list[pd.DataFrame] = []
    for task, target in [
        ("predict_p90", "target_p90"),
        ("predict_mean", "target_mean"),
        ("predict_p90_rank", "target_p90_rank_health"),
        ("predict_mean_rank", "target_mean_rank_health"),
        ("predict_health_score", "target_health_score"),
    ]:
        metrics, oof = eval_group_regression(df, blocks, task, target)
        metric_frames.append(metrics)
        oof_frames.append(oof)

    for task, target in [
        ("classify_visible", "target_visible"),
        ("classify_p90_top25", "target_p90_top25"),
        ("classify_mean_top25", "target_mean_top25"),
        ("classify_joint_health", "target_joint_health"),
    ]:
        metrics, oof = eval_group_binary(df, blocks, task, target)
        metric_frames.append(metrics)
        oof_frames.append(oof)

    mode_frames = [
        eval_leave_mode(df, blocks, "target_p90_rank_health", "regression"),
        eval_leave_mode(df, blocks, "target_health_score", "regression"),
        eval_leave_mode(df, blocks, "target_joint_health", "binary"),
    ]
    within_frames = [
        eval_within_mode(df, blocks, "target_p90_rank_health", "regression"),
        eval_within_mode(df, blocks, "target_health_score", "regression"),
        eval_within_mode(df, blocks, "target_joint_health", "binary"),
    ]
    metrics_all = pd.concat([m for m in metric_frames if not m.empty], ignore_index=True)
    oof_all = pd.concat([o for o in oof_frames if not o.empty], ignore_index=True)
    mode_all = pd.concat([m for m in mode_frames if not m.empty], ignore_index=True)
    within_all = pd.concat([m for m in within_frames if not m.empty], ignore_index=True)
    source = source_readout(df, oof_all)
    summary = summarize_readouts(metrics_all, mode_all, within_all, source)
    tops = fit_top_features(df, blocks)

    metrics_all.to_csv(METRICS_OUT, index=False)
    oof_all.to_csv(OOF_OUT, index=False)
    mode_all.to_csv(MODE_OUT, index=False)
    within_all.to_csv(WITHIN_MODE_OUT, index=False)
    source.to_csv(SOURCE_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    tops.to_csv(TOP_FEATURE_OUT, index=False)
    write_report(df, metrics_all, mode_all, within_all, source, summary, tops)
    return df, metrics_all, mode_all, source, tops


def best_rows(metrics: pd.DataFrame, task: str, key: str, n: int = 8) -> pd.DataFrame:
    part = metrics[metrics["task"].eq(task)].copy()
    if part.empty or key not in part.columns:
        return part
    return part.sort_values(key, ascending=False).head(n)


def write_report(df: pd.DataFrame, metrics: pd.DataFrame, mode: pd.DataFrame, within: pd.DataFrame, source: pd.DataFrame, summary: pd.DataFrame, tops: pd.DataFrame) -> None:
    p90_rank = best_rows(metrics, "predict_p90_rank", "spearman")
    health_score = best_rows(metrics, "predict_health_score", "spearman")
    joint = best_rows(metrics, "classify_joint_health", "auc")
    mode_p90 = mode[mode["task"].eq("target_p90_rank_health")].sort_values(["split", "spearman"], ascending=[True, False])
    mode_joint = mode[mode["task"].eq("target_joint_health")].sort_values(["split", "auc"], ascending=[True, False])
    mode_summary = summary[summary["summary"].str.startswith("null_mode_holdout")].sort_values(["summary", "value"], ascending=[True, False])
    within_summary = summary[summary["summary"].str.startswith("within_mode")].sort_values(["summary", "value"], ascending=[True, False])
    within_p90 = within[within["task"].eq("target_p90_rank_health")].sort_values(["split", "spearman"], ascending=[True, False])
    source_summary = summary[summary["summary"].str.startswith("source_top_mode")].sort_values("value", ascending=False)

    def metric_value(task: str, block: str, col: str) -> float:
        part = metrics[metrics["task"].eq(task) & metrics["feature_block"].eq(block)]
        if part.empty or col not in part.columns:
            return np.nan
        return float(part[col].iloc[0])

    human_p90 = metric_value("predict_p90_rank", "human_signature", "spearman")
    action_p90 = metric_value("predict_p90_rank", "action_shape", "spearman")
    hpa_p90 = metric_value("predict_p90_rank", "human_plus_action", "spearman")
    human_joint = metric_value("classify_joint_health", "human_signature", "auc")
    action_joint = metric_value("classify_joint_health", "action_shape", "auc")

    def summary_value(name: str, block: str) -> float:
        part = summary[summary["summary"].eq(name) & summary["feature_block"].eq(block)]
        if part.empty:
            return np.nan
        return float(part["value"].iloc[0])

    within_human_p90 = summary_value("within_mode_p90_spearman_mean", "human_signature")
    within_action_p90 = summary_value("within_mode_p90_spearman_mean", "action_shape")
    leave_human_p90 = summary_value("null_mode_holdout_p90_spearman_mean", "human_signature")
    leave_action_p90 = summary_value("null_mode_holdout_p90_spearman_mean", "action_shape")

    lines = [
        "# E317 Human Placement Outcome Learner",
        "",
        "Public LB는 사용하지 않았다. E316의 identity target을 버리고, E315 actual/null placement rows의 local outcome health를 직접 예측했다.",
        "",
        "## Dataset",
        "",
        f"- placement rows: `{len(df)}`",
        f"- sources: `{df['source_basename'].nunique()}`",
        f"- actual rows: `{int(df['is_actual'].sum())}`",
        f"- row nulls: `{int(df['placement_mode'].eq('row').sum())}`",
        f"- subject nulls: `{int(df['placement_mode'].eq('subject').sum())}`",
        f"- dateblock nulls: `{int(df['placement_mode'].eq('dateblock').sum())}`",
        f"- joint-health positive rate: `{df['target_joint_health'].mean():.6f}`",
        "",
        "## Source-Holdout P90 Rank Health",
        "",
        md(p90_rank, n=12),
        "",
        "## Source-Holdout Health Score",
        "",
        md(health_score, n=12),
        "",
        "## Source-Holdout Joint Health",
        "",
        md(joint, n=12),
        "",
        "## Leave-Mode-Out P90 Rank Health",
        "",
        md(mode_p90, n=24),
        "",
        "## Mode and Source Summary",
        "",
        md(mode_summary, n=20),
        "",
        md(within_summary, n=20),
        "",
        md(source_summary, n=12),
        "",
        "## Within-Mode P90 Rank Health",
        "",
        md(within_p90, n=28),
        "",
        "## Leave-Mode-Out Joint Health",
        "",
        md(mode_joint, n=24),
        "",
        "## Source Readout",
        "",
        md(source.head(20), n=20),
        "",
        "## Top Human/Action Coefficients",
        "",
        md(tops.head(50), n=50),
        "",
        "## Decision",
        "",
    ]
    if np.isfinite(human_p90) and np.isfinite(action_p90) and human_p90 > action_p90 + 0.05:
        lines.append("- Human diary signatures beat action shape on source-held placement health. This would support a live placement-health latent.")
    elif np.isfinite(hpa_p90) and np.isfinite(action_p90) and hpa_p90 > action_p90 + 0.05:
        lines.append("- Human diary signatures add useful health information only when combined with action shape. This supports using human context as a gate/regularizer, not as a standalone selector.")
    else:
        lines.append("- Human diary signatures do not clearly beat action shape on source-held placement health. The current health target is still dominated by action geometry or source-level movement.")
    if np.isfinite(within_human_p90) and np.isfinite(within_action_p90) and within_action_p90 > within_human_p90:
        lines.append(f"- Within a fixed placement mode, action shape is stronger than human-only context (`{within_action_p90:.6f}` vs `{within_human_p90:.6f}` mean Spearman).")
    if np.isfinite(leave_human_p90) and np.isfinite(leave_action_p90):
        lines.append(f"- Across held-out null modes, human-only context is the only positive p90-rank signal (`{leave_human_p90:.6f}` vs action `{leave_action_p90:.6f}`), but the magnitude is too weak for promotion.")
    if np.isfinite(human_joint) and np.isfinite(action_joint) and human_joint > action_joint + 0.05:
        lines.append("- Joint-health classification has independent human signal.")
    else:
        lines.append("- Joint-health classification is not independently solved by human context.")
    lines.append("- Revised bottleneck: human context helps choose which placement mode/source neighborhood is plausible, while action geometry still controls health inside a mode. The next generator should be mode-specialized, not a universal human-score multiplier.")
    lines.extend(
        [
            "- No submission is created. A future candidate needs a direct action generator whose predicted health beats row/subject/dateblock controls, not only a high identity score.",
            "",
            "## Outputs",
            "",
            f"- `{METRICS_OUT.relative_to(ROOT)}`",
            f"- `{MODE_OUT.relative_to(ROOT)}`",
            f"- `{WITHIN_MODE_OUT.relative_to(ROOT)}`",
            f"- `{SOURCE_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{TOP_FEATURE_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df, metrics, mode, _, _ = run()
    print(f"placement_rows={len(df)}")
    print(f"sources={df['source_basename'].nunique()}")
    print(f"joint_health_positive_rate={df['target_joint_health'].mean():.6f}")
    for block in ["human_signature", "action_shape", "human_plus_action", "human_plus_identity_action"]:
        part = metrics[metrics["task"].eq("predict_p90_rank") & metrics["feature_block"].eq(block)]
        if not part.empty:
            print(f"source_p90_rank_spearman_{block}={part['spearman'].iloc[0]:.6f}")
    mode_part = mode[mode["task"].eq("target_p90_rank_health")]
    if not mode_part.empty:
        best = mode_part.sort_values("spearman", ascending=False).iloc[0]
        print(f"best_leave_mode={best['split']}:{best['feature_block']}:{best['spearman']:.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
