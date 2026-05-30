#!/usr/bin/env python3
"""E213: audit whether the live E208/E211 JEPA axes are specific.

E208/E209/E211 found a narrow JEPA-derived path:

- Q3: e208_resid_self_pc10
- S4: e208_pred_pc14

This script asks whether those axes are special or whether they are likely
cherry-picked from many latent coordinates. It does not create a submission.
It compares the live axes against:

- global row permutations of the same feature;
- within-subject permutations of the same feature;
- neighboring coordinates from the same JEPA embedding family;
- the original E208 downstream scan rank.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import broad_single_feature_residual_probe as broad  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
SUB_KEY = ["subject_id", "sleep_date", "lifelog_date"]
KEY = ["subject_id", "lifelog_date"]
BASE_OOF = OUT / "final_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4_oof.npy"
TRAIN_FEATURES = OUT / "e208_feature_neighbor_jepa_train_features.parquet"
SCAN_SUMMARY = OUT / "e208_feature_neighbor_jepa_downstream_scan_summary.csv"
GEOM_SUMMARY = OUT / "e208_feature_neighbor_jepa_downstream_geometry_summary.csv"

SUMMARY_OUT = OUT / "e213_jepa_axis_specificity_audit_summary.csv"
NULL_OUT = OUT / "e213_jepa_axis_specificity_audit_nulls.csv"
POOL_OUT = OUT / "e213_jepa_axis_specificity_audit_pool.csv"
REPORT_OUT = OUT / "e213_jepa_axis_specificity_audit_report.md"

SEED = 321213
N_PERM = 48
N_HALF = 120


@dataclass(frozen=True)
class Axis:
    axis_id: str
    target: str
    feature: str
    mode: str
    c_value: float
    weight: float
    family_pattern: str


AXES = [
    Axis("q3_resid_self_pc10", "Q3", "e208_resid_self_pc10", "subject_center", 0.10, 0.45, r"^e208_resid_self_pc\d+$"),
    Axis("s4_pred_pc14", "S4", "e208_pred_pc14", "subject_rank", 0.20, 0.45, r"^e208_pred_pc\d+$"),
]


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=float), 1e-5, 1.0 - 1e-5)


def loss_col(y: np.ndarray, p: np.ndarray) -> float:
    yy = y.astype(float)
    pp = clip(p)
    return float(-(yy * np.log(pp) + (1.0 - yy) * np.log(1.0 - pp)).mean())


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()

    def render(v: Any) -> str:
        if isinstance(v, (float, np.floating)):
            return f"{float(v):.12g}"
        if isinstance(v, (int, np.integer)):
            return str(int(v))
        return str(v)

    def clean(s: str) -> str:
        return s.replace("\n", " ").replace("|", "\\|")

    lines = [
        "| " + " | ".join(clean(str(c)) for c in view.columns) + " |",
        "| " + " | ".join("---" for _ in view.columns) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(clean(render(row[c])) for c in view.columns) + " |")
    return "\n".join(lines)


def build_frame() -> tuple[pd.DataFrame, np.ndarray]:
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    features = pd.read_parquet(TRAIN_FEATURES)
    merged = train[SUB_KEY + TARGETS].merge(features, on=SUB_KEY, how="left", validate="one_to_one")
    if len(merged) != len(train):
        raise ValueError("feature merge changed row count")
    missing = merged.filter(like="e208_").isna().sum().sum()
    if missing:
        raise ValueError(f"missing e208 feature cells: {missing}")
    base = clip(np.load(BASE_OOF))
    if base.shape != (len(train), len(TARGETS)):
        raise ValueError(f"bad base shape {base.shape}")
    return merged.sort_values(KEY).reset_index(drop=True), base


def subject_half_delta(
    df: pd.DataFrame,
    y_col: np.ndarray,
    base_col: np.ndarray,
    cand_col: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, float]:
    subjects = np.array(sorted(df["subject_id"].astype(str).unique()))
    deltas: list[float] = []
    for _ in range(N_HALF):
        picked = set(rng.choice(subjects, size=max(1, len(subjects) // 2), replace=False))
        hold = ~df["subject_id"].astype(str).isin(picked).to_numpy()
        deltas.append(loss_col(y_col[hold], cand_col[hold]) - loss_col(y_col[hold], base_col[hold]))
    arr = np.asarray(deltas, dtype=float)
    return {
        "half_mean_delta": float(arr.mean()),
        "half_median_delta": float(np.median(arr)),
        "half_p25_delta": float(np.quantile(arr, 0.25)),
        "half_p75_delta": float(np.quantile(arr, 0.75)),
        "half_win_rate": float((arr < 0.0).mean()),
    }


def evaluate_axis_feature(
    df: pd.DataFrame,
    base: np.ndarray,
    axis: Axis,
    feature: str,
    rng: np.random.Generator,
) -> dict[str, float]:
    j = TARGETS.index(axis.target)
    corrected = broad.oof_corrected(df, base, axis.target, feature, axis.mode, axis.c_value)
    cand = clip((1.0 - axis.weight) * base[:, j] + axis.weight * corrected)
    y_col = df[axis.target].to_numpy(dtype=int)
    base_col = base[:, j]
    out = {
        "base_loss": loss_col(y_col, base_col),
        "candidate_loss": loss_col(y_col, cand),
        "delta": loss_col(y_col, cand) - loss_col(y_col, base_col),
        "corrected_loss": loss_col(y_col, corrected),
    }
    out.update(subject_half_delta(df, y_col, base_col, cand, rng))
    return out


def permute_global(values: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    return values[rng.permutation(len(values))]


def permute_subject(df: pd.DataFrame, values: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = values.copy()
    subjects = df["subject_id"].astype(str).to_numpy()
    for sid in np.unique(subjects):
        idx = np.where(subjects == sid)[0]
        if len(idx) > 1:
            out[idx] = out[idx][rng.permutation(len(idx))]
    return out


def scan_rank(axis: Axis) -> dict[str, float]:
    scan = pd.read_csv(SCAN_SUMMARY)
    sub = scan.loc[scan["target"].eq(axis.target)].copy()
    sub["rank_delta"] = sub["delta_vs_base"].rank(method="min", ascending=True)
    feature_rows = sub.loc[sub["feature"].eq(axis.feature)].copy()
    exact = feature_rows.loc[
        feature_rows["mode"].eq(axis.mode) & np.isclose(feature_rows["c_value"].astype(float), axis.c_value)
    ]
    best_feature = feature_rows.sort_values("delta_vs_base").head(1)
    if exact.empty:
        return {
            "scan_target_rows": float(len(sub)),
            "scan_exact_rank": np.nan,
            "scan_exact_percentile": np.nan,
            "scan_feature_best_rank": float(best_feature["rank_delta"].iloc[0]) if not best_feature.empty else np.nan,
            "scan_feature_best_delta": float(best_feature["delta_vs_base"].iloc[0]) if not best_feature.empty else np.nan,
        }
    rec = exact.sort_values("delta_vs_base").iloc[0]
    return {
        "scan_target_rows": float(len(sub)),
        "scan_exact_rank": float(rec["rank_delta"]),
        "scan_exact_percentile": float(1.0 - (rec["rank_delta"] - 1.0) / max(len(sub) - 1, 1)),
        "scan_feature_best_rank": float(best_feature["rank_delta"].iloc[0]) if not best_feature.empty else float(rec["rank_delta"]),
        "scan_feature_best_delta": float(best_feature["delta_vs_base"].iloc[0]) if not best_feature.empty else float(rec["delta_vs_base"]),
    }


def geometry_lookup(axis: Axis) -> dict[str, float]:
    geom = pd.read_csv(GEOM_SUMMARY)
    exact = geom.loc[
        geom["target"].eq(axis.target)
        & geom["feature"].eq(axis.feature)
        & geom["mode"].eq(axis.mode)
        & np.isclose(geom["c_value"].astype(float), axis.c_value)
    ]
    if exact.empty:
        return {"geometry_delta_mean": np.nan, "geometry_win_rate": np.nan, "passes_e208_probe": np.nan}
    row = exact.sort_values("delta_vs_base").iloc[0]
    return {
        "geometry_delta_mean": float(row["geometry_delta_mean"]),
        "geometry_win_rate": float(row["geometry_win_rate"]),
        "passes_e208_probe": float(bool(row["passes_e208_probe"])),
    }


def empirical_p(null_values: pd.Series, actual: float, lower_is_better: bool = True) -> float:
    vals = null_values.dropna().to_numpy(dtype=float)
    if vals.size == 0:
        return np.nan
    if lower_is_better:
        return float((np.sum(vals <= actual) + 1.0) / (len(vals) + 1.0))
    return float((np.sum(vals >= actual) + 1.0) / (len(vals) + 1.0))


def main() -> None:
    df, base = build_frame()
    rng = np.random.default_rng(SEED)
    null_rows: list[dict[str, Any]] = []
    pool_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for axis in AXES:
        actual_rng = np.random.default_rng(SEED + len(summary_rows) * 101 + 7)
        actual = evaluate_axis_feature(df, base, axis, axis.feature, actual_rng)
        actual.update(scan_rank(axis))
        actual.update(geometry_lookup(axis))

        values = pd.to_numeric(df[axis.feature], errors="coerce").to_numpy(dtype=float)
        for kind in ["global_perm", "subject_perm"]:
            for rep in range(N_PERM):
                temp_col = f"e213_null_{axis.axis_id}_{kind}_{rep:03d}"
                if kind == "global_perm":
                    df[temp_col] = permute_global(values, rng)
                else:
                    df[temp_col] = permute_subject(df, values, rng)
                rec = evaluate_axis_feature(df, base, axis, temp_col, rng)
                rec.update({"axis_id": axis.axis_id, "target": axis.target, "feature": axis.feature, "null_kind": kind, "rep": rep})
                null_rows.append(rec)
                df.drop(columns=[temp_col], inplace=True)

        pool_cols = [
            c for c in df.columns
            if re.match(axis.family_pattern, c) and c != axis.feature
        ]
        for feature in sorted(pool_cols):
            rec = evaluate_axis_feature(df, base, axis, feature, rng)
            rec.update({"axis_id": axis.axis_id, "target": axis.target, "axis_feature": axis.feature, "pool_feature": feature})
            pool_rows.append(rec)

        null_df_axis = pd.DataFrame([r for r in null_rows if r["axis_id"] == axis.axis_id])
        pool_df_axis = pd.DataFrame([r for r in pool_rows if r["axis_id"] == axis.axis_id])
        row = {
            "axis_id": axis.axis_id,
            "target": axis.target,
            "feature": axis.feature,
            "mode": axis.mode,
            "c_value": axis.c_value,
            "weight": axis.weight,
            **actual,
            "global_perm_p_delta": empirical_p(null_df_axis.loc[null_df_axis["null_kind"].eq("global_perm"), "delta"], actual["delta"], True),
            "subject_perm_p_delta": empirical_p(null_df_axis.loc[null_df_axis["null_kind"].eq("subject_perm"), "delta"], actual["delta"], True),
            "global_perm_p_half": empirical_p(null_df_axis.loc[null_df_axis["null_kind"].eq("global_perm"), "half_mean_delta"], actual["half_mean_delta"], True),
            "subject_perm_p_half": empirical_p(null_df_axis.loc[null_df_axis["null_kind"].eq("subject_perm"), "half_mean_delta"], actual["half_mean_delta"], True),
            "pool_size": int(len(pool_df_axis)),
            "pool_rank_delta": float(1 + np.sum(pool_df_axis["delta"].to_numpy(dtype=float) < actual["delta"])) if not pool_df_axis.empty else np.nan,
            "pool_p_delta": empirical_p(pool_df_axis["delta"], actual["delta"], True),
            "pool_best_delta": float(pool_df_axis["delta"].min()) if not pool_df_axis.empty else np.nan,
            "pool_best_feature": str(pool_df_axis.sort_values("delta").iloc[0]["pool_feature"]) if not pool_df_axis.empty else "",
        }
        row["axis_specificity_decision"] = (
            "specific"
            if (
                row["global_perm_p_delta"] <= 0.05
                and row["subject_perm_p_delta"] <= 0.10
                and row["pool_rank_delta"] <= max(2, 0.15 * max(row["pool_size"], 1))
                and actual["half_win_rate"] >= 0.60
                and actual["geometry_delta_mean"] <= 0.0
            )
            else "weak_or_underidentified"
        )
        summary_rows.append(row)

    null_df = pd.DataFrame(null_rows)
    pool_df = pd.DataFrame(pool_rows)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_OUT, index=False)
    null_df.to_csv(NULL_OUT, index=False)
    pool_df.to_csv(POOL_OUT, index=False)

    lines = [
        "# E213 JEPA Axis Specificity Audit",
        "",
        "## Purpose",
        "",
        "Test whether the live E208/E211 JEPA axes are specific representation signals or likely latent-axis cherry-picks. This creates no submission.",
        "",
        "## Summary",
        "",
        md_table(
            summary,
            [
                "axis_id",
                "target",
                "feature",
                "delta",
                "half_mean_delta",
                "half_win_rate",
                "geometry_delta_mean",
                "geometry_win_rate",
                "scan_exact_rank",
                "scan_exact_percentile",
                "global_perm_p_delta",
                "subject_perm_p_delta",
                "pool_rank_delta",
                "pool_p_delta",
                "pool_best_feature",
                "pool_best_delta",
                "axis_specificity_decision",
            ],
        ),
        "",
        "## Null Distribution Snapshot",
        "",
        md_table(
            null_df.groupby(["axis_id", "null_kind"]).agg(
                n=("delta", "size"),
                delta_min=("delta", "min"),
                delta_p05=("delta", lambda x: float(np.quantile(x, 0.05))),
                delta_median=("delta", "median"),
                half_mean_min=("half_mean_delta", "min"),
                half_mean_median=("half_mean_delta", "median"),
            ).reset_index(),
            n=20,
        ),
        "",
        "## Same-Family Pool Top Rows",
        "",
        md_table(
            pool_df.sort_values(["axis_id", "delta"]),
            ["axis_id", "pool_feature", "delta", "half_mean_delta", "half_win_rate"],
            n=30,
        ),
        "",
        "## Decision",
        "",
        "- `specific` means the axis beats permutation nulls, is near the top of its same-family coordinate pool, keeps subject-half support, and had nonpositive E208 geometry.",
        "- `weak_or_underidentified` means the current axis may still be useful, but it should be treated as a fragile probability translator rather than a representation law.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(summary.round(9).to_string(index=False))


if __name__ == "__main__":
    main()
