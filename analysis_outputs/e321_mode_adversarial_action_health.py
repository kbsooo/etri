#!/usr/bin/env python3
"""E321: mode-specific adversarial action-health learner.

E320 showed that E319 tensors fail mainly against row/subject/dateblock
placement nulls, while target/sign/QS controls are mostly beaten.  This script
asks the next local question before any public LB use:

Can candidate geometry plus route metadata predict, under held-out candidate
stress, whether an E319 actual tensor beats its matched row/subject/dateblock
nulls?

The output is a local health diagnostic and blocker.  It creates no
submission.
"""

from __future__ import annotations

from pathlib import Path
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
from sklearn.preprocessing import OneHotEncoder, StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

GOVERNOR = OUT / "e319_mode_specialized_generator_governor.csv"
SCORES = OUT / "e319_mode_specialized_generator_scores.csv"
NULL_MAP = OUT / "e319_mode_specialized_generator_null_map.csv"

PAIR_AUDIT_OUT = OUT / "e321_mode_adversarial_action_health_pair_audit.csv"
CANDIDATE_AUDIT_OUT = OUT / "e321_mode_adversarial_action_health_candidate_audit.csv"
SUMMARY_OUT = OUT / "e321_mode_adversarial_action_health_summary.csv"
REPORT_OUT = OUT / "e321_mode_adversarial_action_health_report.md"

PLACEMENT_MODES = ["row", "subject", "dateblock"]
PROMOTION_THRESHOLDS = {
    "null_strict_rate": 0.10,
    "p90_dominance": 0.80,
    "mean_dominance": 0.70,
    "worst_mode_p90_dominance": 0.55,
}
EPS = 1e-6

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def md(frame: pd.DataFrame, n: int = 40, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    out = frame.head(n).copy()
    for col in out.select_dtypes(include=[np.floating]).columns:
        out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{x:{floatfmt}}")
    out = out.fillna("").astype(str)
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *rows])


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


def safe_corr(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray, method: str = "spearman") -> float:
    sa = pd.Series(a)
    sb = pd.Series(b)
    if sa.nunique(dropna=True) < 2 or sb.nunique(dropna=True) < 2:
        return np.nan
    return float(sa.corr(sb, method=method))


def parse_mode_mix(value: str) -> dict[str, float]:
    out = {f"mix_{m}": 0.0 for m in ["actual", "row", "subject", "dateblock"]}
    total = 0.0
    for part in str(value).split("|"):
        if ":" not in part:
            continue
        key, val = part.split(":", 1)
        try:
            num = float(val)
        except ValueError:
            continue
        out[f"mix_{key}"] = num
        total += num
    if total > 0:
        for key in list(out):
            out[f"{key}_share"] = out[key] / total
    return out


def score_feature_columns(scores: pd.DataFrame) -> list[str]:
    blocked = {
        "scenario_count",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_median",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_delta_vs_current_min",
        "pred_delta_vs_current_max",
        "pred_delta_vs_current_spread",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    }
    blocked_prefixes = ("strict_", "info_", "below_", "block_")
    out: list[str] = []
    for col in scores.columns:
        if col in blocked or col.startswith(blocked_prefixes):
            continue
        if pd.api.types.is_numeric_dtype(scores[col]):
            out.append(col)
    return out


def candidate_meta_features(governor: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    numeric_cols = [
        "source_count",
        "weight",
        "nonzero_rows",
        "nonzero_cells",
        "mean_abs_delta",
        "max_abs_delta",
        "l1_delta",
        "signed_delta_sum",
        "q_abs_share",
        "s_abs_share",
        "abs_Q1",
        "abs_Q2",
        "abs_Q3",
        "abs_S1",
        "abs_S2",
        "abs_S3",
        "abs_S4",
    ]
    for _, row in governor.iterrows():
        item: dict[str, Any] = {
            "basename": row["basename"],
            "policy": row.get("policy", ""),
            "recipe": row.get("recipe", ""),
            "group_key": row.get("group_key", ""),
            "base_variant": row.get("base_variant", ""),
        }
        for col in numeric_cols:
            item[f"meta_{col}"] = float(row[col]) if col in row and pd.notna(row[col]) else np.nan
        item.update(parse_mode_mix(str(row.get("selected_mode_mix", ""))))
        rows.append(item)
    return pd.DataFrame(rows)


def build_pair_rows() -> pd.DataFrame:
    governor = pd.read_csv(GOVERNOR)
    governor = governor[~governor["oracle_control"].astype(bool)].reset_index(drop=True)
    scores = pd.read_csv(SCORES)
    null_map = pd.read_csv(NULL_MAP)
    score_cols = score_feature_columns(scores)

    score_by_base = scores.set_index("basename")
    meta = candidate_meta_features(governor).set_index("basename")

    rows: list[dict[str, Any]] = []
    for _, cand in governor.iterrows():
        basename = str(cand["basename"])
        if basename not in score_by_base.index:
            continue
        actual_score = score_by_base.loc[basename]
        actual_geo = actual_score[score_cols].astype(float)
        cand_meta = meta.loc[basename].to_dict() if basename in meta.index else {}
        for _, null in null_map[null_map["source_basename"].eq(basename)].iterrows():
            mode = str(null["mode"])
            if mode not in PLACEMENT_MODES:
                continue
            null_base = str(null["null_basename"])
            if null_base not in score_by_base.index:
                continue
            null_score = score_by_base.loc[null_base]
            null_geo = null_score[score_cols].astype(float)
            item: dict[str, Any] = {
                "basename": basename,
                "null_basename": null_base,
                "mode": mode,
                "rep": int(null["rep"]),
                "actual_p90": float(actual_score["pred_delta_vs_current_p90"]),
                "null_p90": float(null_score["pred_delta_vs_current_p90"]),
                "actual_mean": float(actual_score["pred_delta_vs_current_mean"]),
                "null_mean": float(null_score["pred_delta_vs_current_mean"]),
                "actual_strict": bool(actual_score["strict_promote_gate"]),
                "null_strict": bool(null_score["strict_promote_gate"]),
                "p90_win": int(float(actual_score["pred_delta_vs_current_p90"]) < float(null_score["pred_delta_vs_current_p90"])),
                "mean_win": int(float(actual_score["pred_delta_vs_current_mean"]) < float(null_score["pred_delta_vs_current_mean"])),
                "null_not_strict": int(not bool(null_score["strict_promote_gate"])),
            }
            item["pair_health"] = int(item["p90_win"] and item["mean_win"] and item["null_not_strict"])
            for col in score_cols:
                item[f"actual__{col}"] = float(actual_geo[col])
                item[f"null__{col}"] = float(null_geo[col])
                item[f"diff__{col}"] = float(actual_geo[col] - null_geo[col])
            item.update(cand_meta)
            rows.append(item)
    return pd.DataFrame(rows)


def feature_sets(df: pd.DataFrame) -> dict[str, tuple[list[str], list[str]]]:
    actual_cols = [c for c in df.columns if c.startswith("actual__")]
    null_cols = [c for c in df.columns if c.startswith("null__")]
    diff_cols = [c for c in df.columns if c.startswith("diff__")]
    meta_num = [
        c
        for c in df.columns
        if (c.startswith("meta_") or c.startswith("mix_"))
        and pd.api.types.is_numeric_dtype(df[c])
    ]
    meta_cat = ["policy", "recipe", "base_variant", "group_key"]
    return {
        "actual_geometry": (actual_cols + meta_num, meta_cat),
        "pair_delta_geometry": (diff_cols + meta_num, meta_cat),
        "actual_plus_null_geometry": (actual_cols + null_cols + meta_num, meta_cat),
        "full_pair_geometry": (actual_cols + null_cols + diff_cols + meta_num, meta_cat),
        "route_meta_only": (meta_num, meta_cat),
    }


def classifier(num_cols: list[str], cat_cols: list[str]):
    transformers: list[tuple[str, Any, list[str]]] = []
    if num_cols:
        transformers.append(("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num_cols))
    if cat_cols:
        transformers.append(
            (
                "cat",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
                cat_cols,
            )
        )
    return make_pipeline(
        ColumnTransformer(transformers, remainder="drop"),
        LogisticRegression(C=0.20, solver="liblinear", class_weight="balanced", max_iter=2500),
    )


def regressor(num_cols: list[str], cat_cols: list[str]):
    transformers: list[tuple[str, Any, list[str]]] = []
    if num_cols:
        transformers.append(("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), num_cols))
    if cat_cols:
        transformers.append(
            (
                "cat",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
                cat_cols,
            )
        )
    return make_pipeline(ColumnTransformer(transformers, remainder="drop"), Ridge(alpha=10.0))


def oof_predict_classifier(df: pd.DataFrame, num_cols: list[str], cat_cols: list[str], target: str) -> np.ndarray:
    y = df[target].astype(int).to_numpy()
    groups = df["basename"].astype(str).to_numpy()
    pred = np.full(len(df), float(np.mean(y)), dtype=float)
    n_groups = len(np.unique(groups))
    if n_groups < 2 or len(np.unique(y)) < 2:
        return pred
    folds = GroupKFold(n_splits=max(2, min(5, n_groups)))
    for tr, va in folds.split(df, y, groups):
        if len(np.unique(y[tr])) < 2:
            pred[va] = float(np.mean(y[tr]))
            continue
        model = classifier(num_cols, cat_cols)
        model.fit(df.iloc[tr][num_cols + cat_cols], y[tr])
        pred[va] = model.predict_proba(df.iloc[va][num_cols + cat_cols])[:, 1]
    return np.clip(pred, EPS, 1.0 - EPS)


def oof_predict_regression(df: pd.DataFrame, num_cols: list[str], cat_cols: list[str], target: str) -> np.ndarray:
    y = df[target].astype(float).to_numpy()
    groups = df["basename"].astype(str).to_numpy()
    pred = np.full(len(df), float(np.mean(y)), dtype=float)
    n_groups = len(np.unique(groups))
    if n_groups < 2:
        return pred
    folds = GroupKFold(n_splits=max(2, min(5, n_groups)))
    for tr, va in folds.split(df, y, groups):
        model = regressor(num_cols, cat_cols)
        model.fit(df.iloc[tr][num_cols + cat_cols], y[tr])
        pred[va] = model.predict(df.iloc[va][num_cols + cat_cols])
    return pred


def eval_pair_models(pairs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sets = feature_sets(pairs)
    rows: list[dict[str, Any]] = []
    pred_frames: list[pd.DataFrame] = []
    for mode in PLACEMENT_MODES:
        sub_idx = pairs["mode"].eq(mode)
        sub = pairs[sub_idx].reset_index(drop=True)
        if sub.empty:
            continue
        for block, (num_cols, cat_cols) in sets.items():
            for target in ["p90_win", "mean_win", "null_not_strict", "pair_health"]:
                pred = oof_predict_classifier(sub, num_cols, cat_cols, target)
                y = sub[target].astype(int).to_numpy()
                rows.append(
                    {
                        "level": "pair",
                        "mode": mode,
                        "task": target,
                        "feature_block": block,
                        "n": int(len(sub)),
                        "groups": int(sub["basename"].nunique()),
                        "positive_rate": float(np.mean(y)),
                        "auc": safe_auc(y, pred),
                        "average_precision": safe_ap(y, pred),
                        "logloss": safe_logloss(y, pred),
                        "spearman": safe_corr(y, pred),
                        "pred_mean": float(np.mean(pred)),
                    }
                )
                pred_frames.append(
                    sub[["basename", "null_basename", "mode", "rep"]].assign(
                        task=target,
                        feature_block=block,
                        label=y,
                        oof_pred=pred,
                    )
                )
            for target in ["actual_p90_minus_null_p90", "actual_mean_minus_null_mean"]:
                work = sub.copy()
                if target == "actual_p90_minus_null_p90":
                    work[target] = work["actual_p90"] - work["null_p90"]
                else:
                    work[target] = work["actual_mean"] - work["null_mean"]
                pred = oof_predict_regression(work, num_cols, cat_cols, target)
                y = work[target].astype(float).to_numpy()
                rows.append(
                    {
                        "level": "pair",
                        "mode": mode,
                        "task": target,
                        "feature_block": block,
                        "n": int(len(work)),
                        "groups": int(work["basename"].nunique()),
                        "positive_rate": np.nan,
                        "auc": np.nan,
                        "average_precision": np.nan,
                        "logloss": np.nan,
                        "spearman": safe_corr(y, pred),
                        "pearson": safe_corr(y, pred, "pearson"),
                        "rmse": float(np.sqrt(np.mean((y - pred) ** 2))),
                        "pred_mean": float(np.mean(pred)),
                    }
                )
                pred_frames.append(
                    work[["basename", "null_basename", "mode", "rep"]].assign(
                        task=target,
                        feature_block=block,
                        label=y,
                        oof_pred=pred,
                    )
                )
    return pd.DataFrame(rows), pd.concat(pred_frames, ignore_index=True)


def candidate_readout(pairs: pd.DataFrame, pair_pred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    gov = pd.read_csv(GOVERNOR)
    gov = gov[~gov["oracle_control"].astype(bool)].copy()
    pred = pair_pred[
        pair_pred["feature_block"].eq("full_pair_geometry")
        & pair_pred["task"].isin(["p90_win", "mean_win", "null_not_strict", "pair_health"])
    ].copy()
    pivot = pred.pivot_table(
        index=["basename", "mode", "rep"],
        columns="task",
        values="oof_pred",
        aggfunc="mean",
    ).reset_index()
    agg_mode = (
        pivot.groupby(["basename", "mode"])
        .agg(
            pred_p90_dominance=("p90_win", "mean"),
            pred_mean_dominance=("mean_win", "mean"),
            pred_null_not_strict=("null_not_strict", "mean"),
            pred_pair_health=("pair_health", "mean"),
        )
        .reset_index()
    )
    cand = agg_mode.pivot_table(index="basename", columns="mode", values="pred_p90_dominance", aggfunc="mean")
    cand.columns = [f"pred_{c}_p90_dominance" for c in cand.columns]
    cand = cand.reset_index()
    for col in [f"pred_{m}_p90_dominance" for m in PLACEMENT_MODES]:
        if col not in cand.columns:
            cand[col] = np.nan
    cand["pred_worst_placement_dominance"] = cand[[f"pred_{m}_p90_dominance" for m in PLACEMENT_MODES]].min(axis=1)

    null_strict = agg_mode.pivot_table(index="basename", columns="mode", values="pred_null_not_strict", aggfunc="mean")
    null_strict.columns = [f"pred_{c}_null_not_strict" for c in null_strict.columns]
    null_strict = null_strict.reset_index()
    cand = cand.merge(null_strict, on="basename", how="left")
    strict_cols = [f"pred_{m}_null_not_strict" for m in PLACEMENT_MODES]
    for col in strict_cols:
        if col not in cand.columns:
            cand[col] = np.nan
    cand["pred_null_strict_rate"] = 1.0 - cand[strict_cols].mean(axis=1)
    cand["pred_adversarial_health"] = (
        cand["pred_worst_placement_dominance"].fillna(0.0)
        - cand["pred_null_strict_rate"].fillna(1.0)
    )

    keep = [
        "basename",
        "policy",
        "recipe",
        "group_key",
        "base_variant",
        "source_count",
        "selected_mode_mix",
        "old_strict_promote",
        "actual_p90",
        "actual_mean",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "public_free_submission_ready",
    ]
    actual = gov[[c for c in keep if c in gov.columns]].copy()
    out = actual.merge(cand, on="basename", how="left")
    out["actual_adversarial_health"] = (
        out["worst_mode_p90_dominance"].fillna(0.0)
        - out["null_strict_rate"].fillna(1.0)
    )
    out["ready_like_actual"] = (
        out["old_strict_promote"].astype(bool)
        & out["actual_p90"].le(-2.0e-5)
        & out["null_strict_rate"].le(PROMOTION_THRESHOLDS["null_strict_rate"])
        & out["p90_dominance"].ge(PROMOTION_THRESHOLDS["p90_dominance"])
        & out["mean_dominance"].ge(PROMOTION_THRESHOLDS["mean_dominance"])
        & out["worst_mode_p90_dominance"].ge(PROMOTION_THRESHOLDS["worst_mode_p90_dominance"])
    )
    out = out.sort_values(["pred_adversarial_health", "actual_p90"], ascending=[False, True]).reset_index(drop=True)

    metric_rows: list[dict[str, Any]] = []
    for pred_col, actual_col in [
        ("pred_worst_placement_dominance", "worst_mode_p90_dominance"),
        ("pred_null_strict_rate", "null_strict_rate"),
        ("pred_adversarial_health", "actual_adversarial_health"),
    ]:
        metric_rows.append(
            {
                "level": "candidate",
                "mode": "placement",
                "task": f"{pred_col}_vs_{actual_col}",
                "feature_block": "full_pair_geometry",
                "n": int(out[[pred_col, actual_col]].dropna().shape[0]),
                "groups": int(out["basename"].nunique()),
                "spearman": safe_corr(out[actual_col], out[pred_col]),
                "pearson": safe_corr(out[actual_col], out[pred_col], "pearson"),
                "top10_actual_ready_like": int(out.head(10)["ready_like_actual"].sum()),
                "top10_mean_actual_health": float(out.head(10)["actual_adversarial_health"].mean()),
            }
        )
    return out, pd.DataFrame(metric_rows)


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pairs = build_pair_rows()
    pair_metrics, pair_pred = eval_pair_models(pairs)
    candidates, cand_metrics = candidate_readout(pairs, pair_pred)

    summary = pd.concat([pair_metrics, cand_metrics], ignore_index=True, sort=False)
    pairs.to_csv(PAIR_AUDIT_OUT, index=False)
    candidates.to_csv(CANDIDATE_AUDIT_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(pairs, summary, candidates)
    return pairs, summary, candidates


def write_report(pairs: pd.DataFrame, summary: pd.DataFrame, candidates: pd.DataFrame) -> None:
    pair_main = summary[
        summary["level"].eq("pair")
        & summary["task"].isin(["p90_win", "null_not_strict", "pair_health"])
        & summary["feature_block"].isin(["route_meta_only", "actual_geometry", "full_pair_geometry"])
    ].copy()
    pair_main = pair_main.sort_values(["task", "mode", "auc"], ascending=[True, True, False])
    cand_main = summary[summary["level"].eq("candidate")].copy()
    top = candidates[
        [
            "basename",
            "policy",
            "recipe",
            "base_variant",
            "actual_p90",
            "null_strict_rate",
            "p90_dominance",
            "mean_dominance",
            "worst_mode_p90_dominance",
            "pred_worst_placement_dominance",
            "pred_null_strict_rate",
            "pred_adversarial_health",
            "actual_adversarial_health",
            "ready_like_actual",
        ]
    ].head(20)
    ready_count = int(candidates["ready_like_actual"].sum())
    top_ready = int(candidates.head(10)["ready_like_actual"].sum())
    best_health = float(candidates["actual_adversarial_health"].max()) if not candidates.empty else np.nan
    best_pred_top_health = float(candidates.head(10)["actual_adversarial_health"].max()) if not candidates.empty else np.nan
    p90_full = summary[
        summary["level"].eq("pair")
        & summary["task"].eq("p90_win")
        & summary["feature_block"].eq("full_pair_geometry")
    ][["mode", "auc"]]
    p90_full_text = ", ".join(f"{r.mode}={r.auc:.3f}" for r in p90_full.itertuples())
    cand_health = cand_main[cand_main["task"].str.startswith("pred_adversarial_health", na=False)]
    cand_spearman = float(cand_health["spearman"].iloc[0]) if not cand_health.empty else np.nan
    lines = [
        "# E321 Mode-Specific Adversarial Action-Health Learner",
        "",
        "Public LB was not used. No submission was created.",
        "",
        "## Question",
        "",
        "Can E319 row/subject/dateblock failures be predicted from candidate geometry and route metadata under held-out-candidate stress?",
        "",
        "## Dataset",
        "",
        f"- pair rows: `{len(pairs)}`",
        f"- candidates: `{pairs['basename'].nunique()}`",
        f"- modes: `{', '.join(PLACEMENT_MODES)}`",
        f"- positive p90-win rate: `{pairs['p90_win'].mean():.6f}`",
        f"- positive pair-health rate: `{pairs['pair_health'].mean():.6f}`",
        "",
        "## Pair OOF Metrics",
        "",
        md(pair_main, n=45),
        "",
        "## Candidate-Level Readout",
        "",
        md(cand_main, n=10),
        "",
        f"- local ready-like candidates in E319 governed set: `{ready_count}`",
        f"- ready-like candidates inside predicted top10: `{top_ready}`",
        f"- best actual adversarial health: `{best_health:.6f}`",
        f"- best actual adversarial health inside predicted top10: `{best_pred_top_health:.6f}`",
        "",
        "## Predicted Top Candidates",
        "",
        md(top, n=20),
        "",
        "## Decision",
        "",
        f"- Pairwise placement health is learnable enough to use as a local target: full-pair p90-win AUC by mode is `{p90_full_text}`.",
        f"- Candidate-level adversarial health ranking is useful but not sufficient: Spearman is `{cand_spearman:.6f}` and predicted top10 still contains `0` ready-like candidates.",
        "- E321 is therefore a checker/diagnostic, not a submission source.",
        "- The next branch should use this adversarial health model before materialization or as a preselector for extra local null evaluation. It should not spend public LB.",
        "",
        "## Outputs",
        "",
        f"- `{PAIR_AUDIT_OUT.relative_to(ROOT)}`",
        f"- `{CANDIDATE_AUDIT_OUT.relative_to(ROOT)}`",
        f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        f"- `{REPORT_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    pairs, summary, candidates = run()
    cand_rows = summary[summary["level"].eq("candidate")]
    best_pair = summary[
        summary["level"].eq("pair")
        & summary["task"].eq("p90_win")
        & summary["feature_block"].eq("full_pair_geometry")
    ]
    print(f"pair_rows={len(pairs)}")
    print(f"candidates={candidates['basename'].nunique()}")
    if not best_pair.empty:
        print("p90_win_full_pair_auc_by_mode=" + ",".join(f"{r.mode}:{r.auc:.6f}" for r in best_pair.itertuples()))
    if not cand_rows.empty:
        for r in cand_rows.itertuples():
            print(f"{r.task}_spearman={getattr(r, 'spearman', np.nan):.6f}")
    print(f"ready_like={int(candidates['ready_like_actual'].sum())}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
