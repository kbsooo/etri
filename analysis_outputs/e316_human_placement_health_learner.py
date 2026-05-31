#!/usr/bin/env python3
"""E316: human placement-health learner.

E315 showed a sharper bottleneck:

    human/social compositions create strong target movement, but they fail
    row/subject/dateblock placement controls.

This script treats placement itself as the JEPA-style latent target.  It asks
whether raw human diary signatures can identify the intended placement among
matched null placements, and whether that identity signal aligns with local
action health.  No public LB is used and no submission is created.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any
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

from e313_human_action_signature import (  # noqa: E402
    CURRENT_PATH,
    TARGETS,
    delta_signature,
    load_human_matrix,
    logit,
    md,
)


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

GOVERNOR = OUT / "e315_human_ready_composition_governor.csv"
NULL_MAP = OUT / "e315_human_ready_composition_null_map.csv"
SCORES = OUT / "e315_human_ready_composition_scores.csv"

FEATURE_OUT = OUT / "e316_human_placement_health_features.csv"
METRICS_OUT = OUT / "e316_human_placement_health_metrics.csv"
OOF_OUT = OUT / "e316_human_placement_health_oof.csv"
SOURCE_OUT = OUT / "e316_human_placement_health_source_readout.csv"
TOP_FEATURE_OUT = OUT / "e316_human_placement_health_top_features.csv"
REPORT_OUT = OUT / "e316_human_placement_health_report.md"

PLACEMENT_MODES = {"row", "subject", "dateblock"}
MAX_HUMAN_COLS = 520
EPS = 1e-6


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def path_from_rel(value: str) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return ROOT / path


def load_score_table() -> pd.DataFrame:
    scores = pd.read_csv(SCORES)
    keep = [
        "basename",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "strict_promote_gate",
        "info_sensor_gate",
        "promotion_decision",
    ]
    return scores[[c for c in keep if c in scores.columns]].drop_duplicates("basename")


def build_placement_rows() -> pd.DataFrame:
    governor = pd.read_csv(GOVERNOR)
    null_map = pd.read_csv(NULL_MAP)
    scores = load_score_table()

    current = pd.read_csv(CURRENT_PATH)
    current_logit = logit(current[TARGETS].to_numpy(dtype=float))
    human, human_cols = load_human_matrix(current)

    rows: list[dict[str, Any]] = []
    items: list[dict[str, Any]] = []
    for _, rec in governor.iterrows():
        basename = str(rec["basename"])
        items.append(
            {
                "basename": basename,
                "source_basename": basename,
                "placement_mode": "actual",
                "rep": -1,
                "is_actual": 1,
                "path": path_from_rel(str(rec["source_path"])),
            }
        )
    for _, rec in null_map.iterrows():
        items.append(
            {
                "basename": str(rec["null_basename"]),
                "source_basename": str(rec["source_basename"]),
                "placement_mode": str(rec["mode"]),
                "rep": int(rec["rep"]),
                "is_actual": 0,
                "path": path_from_rel(str(rec["null_path"])),
            }
        )

    governor_meta = governor.drop(columns=[c for c in ["source_path"] if c in governor.columns]).copy()
    prefix_cols = {
        c: f"source__{c}"
        for c in governor_meta.columns
        if c not in {"basename"}
    }
    governor_meta = governor_meta.rename(columns=prefix_cols).rename(columns={"basename": "source_basename"})

    for item in items:
        shape, sig = delta_signature(item["path"], current_logit, human, human_cols)
        row: dict[str, Any] = {
            k: v
            for k, v in item.items()
            if k != "path"
        }
        row["path"] = rel(item["path"])
        row.update({f"shape__{k}": v for k, v in shape.items()})
        row.update(sig)
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.merge(scores, on="basename", how="left")
    df = df.merge(governor_meta, on="source_basename", how="left")
    if "source__recipe" in df.columns:
        df["recipe"] = df["source__recipe"].astype(str)
    else:
        df["recipe"] = ""

    df["placement_null"] = df["placement_mode"].isin(PLACEMENT_MODES).astype(int)
    df["actual_or_placement_null"] = ((df["is_actual"].eq(1)) | (df["placement_null"].eq(1))).astype(int)
    df["score_visible"] = df["strict_promote_gate"].fillna(False).astype(bool).astype(int)
    df["score_p90_good"] = df["pred_delta_vs_current_p90"].fillna(1.0).lt(-2.0e-5).astype(int)
    df["score_mean_good"] = df["pred_delta_vs_current_mean"].fillna(1.0).lt(-2.0e-5).astype(int)
    df["score_health_proxy"] = (
        df["score_visible"].astype(float)
        + df["score_p90_good"].astype(float)
        + df["score_mean_good"].astype(float)
    )

    human_cols_out = [c for c in df.columns if c.startswith("human_")]
    if len(human_cols_out) > MAX_HUMAN_COLS:
        std = df[human_cols_out].std(axis=0, ddof=0).fillna(0.0).sort_values(ascending=False)
        keep = set(std.head(MAX_HUMAN_COLS).index)
        drop = [c for c in human_cols_out if c not in keep]
        df = df.drop(columns=drop)

    return df


def feature_blocks(df: pd.DataFrame) -> dict[str, list[str]]:
    human_cols = [c for c in df.columns if c.startswith("human_")]
    shape_cols = [c for c in df.columns if c.startswith("shape__")]
    score_shape_cols = [
        "shape__changed_cells",
        "shape__changed_rows",
        "shape__abs_logit_l1",
        "shape__max_abs_logit",
        "shape__row_l1_top1_share",
        "shape__row_l1_top5_share",
        "shape__q_abs_share",
        "shape__s_abs_share",
        "shape__signed_logit_sum",
        "source__seed_count",
        "source__nonzero_rows",
        "source__nonzero_cells",
        "source__l1_delta",
        "source__q_abs_share",
        "source__s_abs_share",
        "source__abs_Q1",
        "source__abs_Q2",
        "source__abs_Q3",
        "source__abs_S1",
        "source__abs_S2",
        "source__abs_S3",
        "source__abs_S4",
    ]
    score_shape_cols = [c for c in score_shape_cols if c in df.columns]
    return {
        "human_signature": human_cols,
        "shape_signature": shape_cols,
        "action_shape": score_shape_cols,
        "human_plus_shape": list(dict.fromkeys(human_cols + score_shape_cols)),
    }


def logistic_pipeline(cols: list[str]):
    return make_pipeline(
        ColumnTransformer(
            [("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), cols)],
            remainder="drop",
        ),
        LogisticRegression(C=0.18, solver="liblinear", class_weight="balanced", max_iter=2500),
    )


def ridge_pipeline(cols: list[str]):
    return make_pipeline(
        ColumnTransformer(
            [("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), cols)],
            remainder="drop",
        ),
        Ridge(alpha=10.0),
    )


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


def group_folds(groups: pd.Series, n_splits: int = 5) -> GroupKFold:
    n_groups = int(groups.nunique())
    return GroupKFold(n_splits=max(2, min(n_splits, n_groups)))


def eval_binary_task(df: pd.DataFrame, task: str, mask: pd.Series, label_col: str, blocks: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    sub = df.loc[mask].reset_index(drop=True).copy()
    rows: list[dict[str, Any]] = []
    oof_rows: list[pd.DataFrame] = []
    if sub.empty or sub[label_col].nunique() < 2:
        return pd.DataFrame(), pd.DataFrame()
    groups = sub["source_basename"].astype(str)
    folds = group_folds(groups)
    y = sub[label_col].astype(int).to_numpy()

    for block_name, cols in blocks.items():
        if not cols:
            continue
        pred = np.zeros(len(sub), dtype=float)
        for tr, va in folds.split(sub, y, groups):
            model = logistic_pipeline(cols)
            model.fit(sub.iloc[tr][cols], y[tr])
            pred[va] = model.predict_proba(sub.iloc[va][cols])[:, 1]
        rows.append(
            {
                "task": task,
                "feature_block": block_name,
                "n": int(len(sub)),
                "positive_rate": float(y.mean()),
                "auc": safe_auc(y, pred),
                "average_precision": safe_ap(y, pred),
                "logloss": safe_logloss(y, pred),
                "pred_mean": float(pred.mean()),
            }
        )
        part = sub[["basename", "source_basename", "placement_mode", "is_actual", "recipe", "source__actual_p90", "source__null_strict_rate"]].copy()
        part["task"] = task
        part["feature_block"] = block_name
        part["label"] = y
        part["oof_pred"] = pred
        oof_rows.append(part)
    return pd.DataFrame(rows), pd.concat(oof_rows, ignore_index=True) if oof_rows else pd.DataFrame()


def eval_regression_task(df: pd.DataFrame, task: str, mask: pd.Series, target_col: str, blocks: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    sub = df.loc[mask].reset_index(drop=True).copy()
    rows: list[dict[str, Any]] = []
    oof_rows: list[pd.DataFrame] = []
    if sub.empty or sub[target_col].notna().sum() < 20:
        return pd.DataFrame(), pd.DataFrame()
    sub = sub[sub[target_col].notna()].reset_index(drop=True)
    y = sub[target_col].astype(float).to_numpy()
    groups = sub["source_basename"].astype(str)
    folds = group_folds(groups)
    for block_name, cols in blocks.items():
        if not cols:
            continue
        pred = np.zeros(len(sub), dtype=float)
        for tr, va in folds.split(sub, y, groups):
            model = ridge_pipeline(cols)
            model.fit(sub.iloc[tr][cols], y[tr])
            pred[va] = model.predict(sub.iloc[va][cols])
        spearman = float(pd.Series(y).corr(pd.Series(pred), method="spearman"))
        pearson = float(pd.Series(y).corr(pd.Series(pred), method="pearson"))
        rows.append(
            {
                "task": task,
                "feature_block": block_name,
                "n": int(len(sub)),
                "target_mean": float(np.mean(y)),
                "spearman": spearman,
                "pearson": pearson,
                "rmse": float(np.sqrt(np.mean((pred - y) ** 2))),
            }
        )
        part = sub[["basename", "source_basename", "placement_mode", "is_actual", "recipe", "source__actual_p90", "source__null_strict_rate"]].copy()
        part["task"] = task
        part["feature_block"] = block_name
        part["label"] = y
        part["oof_pred"] = pred
        oof_rows.append(part)
    return pd.DataFrame(rows), pd.concat(oof_rows, ignore_index=True) if oof_rows else pd.DataFrame()


def source_readout(df: pd.DataFrame, oof: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    task = "actual_vs_placement_null"
    for block_name, part in oof[oof["task"].eq(task)].groupby("feature_block"):
        for source, g in part.groupby("source_basename"):
            actual = g[g["is_actual"].eq(1)]
            nulls = g[g["is_actual"].eq(0)]
            if actual.empty or nulls.empty:
                continue
            apred = float(actual["oof_pred"].iloc[0])
            null_pred = nulls["oof_pred"].to_numpy(dtype=float)
            meta = df[df["source_basename"].eq(source) & df["is_actual"].eq(1)].iloc[0]
            rows.append(
                {
                    "source_basename": source,
                    "feature_block": block_name,
                    "actual_identity_pred": apred,
                    "null_pred_mean": float(np.mean(null_pred)),
                    "actual_rank_vs_placement_null": float(np.mean(apred > null_pred)),
                    "placement_null_count": int(len(nulls)),
                    "recipe": meta.get("recipe", ""),
                    "source_actual_p90": float(meta.get("source__actual_p90", np.nan)),
                    "source_null_strict_rate": float(meta.get("source__null_strict_rate", np.nan)),
                    "source_p90_dominance": float(meta.get("source__p90_dominance", np.nan)),
                    "source_mean_dominance": float(meta.get("source__mean_dominance", np.nan)),
                    "source_worst_mode_p90_dominance": float(meta.get("source__worst_mode_p90_dominance", np.nan)),
                    "source_row_p90_dominance": float(meta.get("source__row_p90_dominance", np.nan)),
                    "source_subject_p90_dominance": float(meta.get("source__subject_p90_dominance", np.nan)),
                    "source_dateblock_p90_dominance": float(meta.get("source__dateblock_p90_dominance", np.nan)),
                    "source_final_decision": meta.get("source__final_decision", ""),
                }
            )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["identity_health_gap"] = out["actual_rank_vs_placement_null"] - out["source_worst_mode_p90_dominance"].fillna(0.0)
    return out.sort_values(["feature_block", "actual_rank_vs_placement_null"], ascending=[True, False]).reset_index(drop=True)


def top_coefficients(df: pd.DataFrame, blocks: dict[str, list[str]]) -> pd.DataFrame:
    mask = df["actual_or_placement_null"].eq(1)
    sub = df.loc[mask].reset_index(drop=True)
    y = sub["is_actual"].astype(int).to_numpy()
    rows: list[dict[str, Any]] = []
    for block_name in ["human_signature", "human_plus_shape"]:
        cols = blocks.get(block_name, [])
        if not cols or len(np.unique(y)) < 2:
            continue
        model = logistic_pipeline(cols)
        model.fit(sub[cols], y)
        lr = model.named_steps["logisticregression"]
        coef = lr.coef_[0]
        for col, value in zip(cols, coef, strict=False):
            rows.append({"feature_block": block_name, "feature": col, "coef_actual_identity": float(value), "abs_coef": float(abs(value))})
    return pd.DataFrame(rows).sort_values("abs_coef", ascending=False).head(100).reset_index(drop=True) if rows else pd.DataFrame()


def summarize_correlations(source: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if source.empty:
        return pd.DataFrame()
    for block, part in source.groupby("feature_block"):
        identity = part["actual_rank_vs_placement_null"]
        for col in [
            "source_null_strict_rate",
            "source_p90_dominance",
            "source_mean_dominance",
            "source_worst_mode_p90_dominance",
            "source_row_p90_dominance",
            "source_subject_p90_dominance",
            "source_dateblock_p90_dominance",
        ]:
            if col not in part.columns or part[col].notna().sum() < 5:
                continue
            target = part[col]
            valid = identity.notna() & target.notna()
            if identity[valid].nunique() < 2 or target[valid].nunique() < 2:
                spearman = np.nan
                pearson = np.nan
            else:
                spearman = float(identity[valid].corr(target[valid], method="spearman"))
                pearson = float(identity[valid].corr(target[valid], method="pearson"))
            rows.append(
                {
                    "feature_block": block,
                    "identity_rank_vs": col,
                    "spearman": spearman,
                    "pearson": pearson,
                    "n": int(valid.sum()),
                }
            )
    return pd.DataFrame(rows)


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = build_placement_rows()
    blocks = feature_blocks(df)
    metric_frames: list[pd.DataFrame] = []
    oof_frames: list[pd.DataFrame] = []

    for task, mask, label in [
        ("actual_vs_all_null", df["is_actual"].isin([0, 1]), "is_actual"),
        ("actual_vs_placement_null", df["actual_or_placement_null"].eq(1), "is_actual"),
    ]:
        metrics, oof = eval_binary_task(df, task, mask, label, blocks)
        metric_frames.append(metrics)
        oof_frames.append(oof)

    for task, target in [
        ("predict_local_p90", "pred_delta_vs_current_p90"),
        ("predict_local_mean", "pred_delta_vs_current_mean"),
    ]:
        metrics, oof = eval_regression_task(df, task, df["actual_or_placement_null"].eq(1), target, blocks)
        metric_frames.append(metrics)
        oof_frames.append(oof)

    metrics_all = pd.concat([m for m in metric_frames if not m.empty], ignore_index=True)
    oof_all = pd.concat([o for o in oof_frames if not o.empty], ignore_index=True)
    source = source_readout(df, oof_all)
    tops = top_coefficients(df, blocks)
    corr = summarize_correlations(source)

    df.to_csv(FEATURE_OUT, index=False)
    metrics_all.to_csv(METRICS_OUT, index=False)
    oof_all.to_csv(OOF_OUT, index=False)
    source.to_csv(SOURCE_OUT, index=False)
    tops.to_csv(TOP_FEATURE_OUT, index=False)
    write_report(df, metrics_all, source, tops, corr)
    return df, metrics_all, source, tops, corr


def write_report(df: pd.DataFrame, metrics: pd.DataFrame, source: pd.DataFrame, tops: pd.DataFrame, corr: pd.DataFrame) -> None:
    placement_metrics = metrics[metrics["task"].eq("actual_vs_placement_null")].sort_values("auc", ascending=False)
    p90_metrics = metrics[metrics["task"].eq("predict_local_p90")].sort_values("spearman", ascending=False)
    source_summary = (
        source.groupby("feature_block")
        .agg(
            sources=("source_basename", "count"),
            mean_actual_rank=("actual_rank_vs_placement_null", "mean"),
            median_actual_rank=("actual_rank_vs_placement_null", "median"),
            top_quartile_rate=("actual_rank_vs_placement_null", lambda s: float(np.mean(np.asarray(s) >= 0.75))),
            mean_identity_health_gap=("identity_health_gap", "mean"),
        )
        .reset_index()
        .sort_values("mean_actual_rank", ascending=False)
        if not source.empty
        else pd.DataFrame()
    )
    near = (
        source.sort_values(["actual_rank_vs_placement_null", "source_worst_mode_p90_dominance"], ascending=[False, True])
        .head(20)
        if not source.empty
        else pd.DataFrame()
    )
    lines = [
        "# E316 Human Placement-Health Learner",
        "",
        "Public LB는 사용하지 않았다. E315의 actual/null placement들을 하나의 mini-world로 보고, raw human diary signature가 실제 placement와 건강한 placement를 구분하는지 검증했다.",
        "",
        "## Dataset",
        "",
        f"- placement rows: `{len(df)}`",
        f"- sources: `{df['source_basename'].nunique()}`",
        f"- actual rows: `{int(df['is_actual'].sum())}`",
        f"- placement null rows: `{int(df['placement_null'].sum())}`",
        f"- all null rows: `{int((df['is_actual'] == 0).sum())}`",
        "",
        "## Actual vs Placement Null",
        "",
        md(placement_metrics, n=20),
        "",
        "## Local Score Regression",
        "",
        md(p90_metrics, n=20),
        "",
        "## Source-Level Identity Readout",
        "",
        md(source_summary, n=20),
        "",
        "## Identity vs Health Correlation",
        "",
        md(corr.sort_values(["feature_block", "identity_rank_vs"]) if not corr.empty else corr, n=40),
        "",
        "## Near-Miss Anatomy",
        "",
        md(
            near[
                [
                    "feature_block",
                    "source_basename",
                    "recipe",
                    "actual_rank_vs_placement_null",
                    "source_actual_p90",
                    "source_null_strict_rate",
                    "source_worst_mode_p90_dominance",
                    "source_row_p90_dominance",
                    "source_subject_p90_dominance",
                    "source_dateblock_p90_dominance",
                    "source_final_decision",
                ]
            ]
            if not near.empty
            else near,
            n=20,
        ),
        "",
        "## Top Human Coefficients",
        "",
        md(tops.head(40) if not tops.empty else tops, n=40),
        "",
        "## Decision",
        "",
    ]
    best_human = placement_metrics[placement_metrics["feature_block"].eq("human_signature")]
    best_auc = float(best_human["auc"].iloc[0]) if not best_human.empty else np.nan
    best_source = source_summary[source_summary["feature_block"].eq("human_signature")]
    mean_rank = float(best_source["mean_actual_rank"].iloc[0]) if not best_source.empty else np.nan
    if np.isfinite(best_auc) and best_auc >= 0.70 and np.isfinite(mean_rank) and mean_rank >= 0.60:
        lines.extend(
            [
                "- Human diary signatures can identify intended placement above chance, so hidden placement is partially learnable.",
                "- However this is not enough for submission unless the identity rank correlates with subject/dateblock/worst-mode health.",
                "- Next action: train a placement-health target, not just an actual-vs-null identity target.",
            ]
        )
    else:
        lines.extend(
            [
                "- Human diary signatures do not robustly identify intended placement against row/subject/dateblock nulls.",
                "- The E315 failure is therefore not just a bad materializer; the available human diary representation is missing the placement invariant.",
                "- Next action: create a richer subject/dateblock world target before more probability editing.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{FEATURE_OUT.relative_to(ROOT)}`",
            f"- `{METRICS_OUT.relative_to(ROOT)}`",
            f"- `{OOF_OUT.relative_to(ROOT)}`",
            f"- `{SOURCE_OUT.relative_to(ROOT)}`",
            f"- `{TOP_FEATURE_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df, metrics, source, _, _ = run()
    print(f"placement_rows={len(df)}")
    print(f"sources={df['source_basename'].nunique()}")
    print(f"actual_rows={int(df['is_actual'].sum())}")
    print(f"placement_null_rows={int(df['placement_null'].sum())}")
    metric = metrics[(metrics["task"].eq("actual_vs_placement_null")) & (metrics["feature_block"].eq("human_signature"))]
    if not metric.empty:
        print(f"human_actual_vs_placement_auc={metric['auc'].iloc[0]:.6f}")
        print(f"human_actual_vs_placement_ap={metric['average_precision'].iloc[0]:.6f}")
    read = source[source["feature_block"].eq("human_signature")]
    if not read.empty:
        print(f"human_mean_actual_rank={read['actual_rank_vs_placement_null'].mean():.6f}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
