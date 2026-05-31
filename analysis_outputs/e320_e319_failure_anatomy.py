#!/usr/bin/env python3
"""E320: failure anatomy for E319 mode-specialized tensors.

E319 generated many selector-visible tensors but none passed public-free null
governance.  This script identifies which gates killed the candidates so the
next branch does not repeat a larger average-consensus search.

No public LB is used and no submission is created.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

GOVERNOR = OUT / "e319_mode_specialized_generator_governor.csv"
SUMMARY_OUT = OUT / "e320_e319_failure_anatomy_summary.csv"
NEAR_OUT = OUT / "e320_e319_failure_anatomy_near_misses.csv"
REPORT_OUT = OUT / "e320_e319_failure_anatomy_report.md"

PROMOTION_THRESHOLDS = {
    "null_strict_rate": 0.10,
    "p90_dominance": 0.80,
    "mean_dominance": 0.70,
    "worst_mode_p90_dominance": 0.55,
}


def md(frame: pd.DataFrame, n: int = 40, floatfmt: str = ".9f") -> str:
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


def dominance_columns(df: pd.DataFrame) -> list[str]:
    return [
        c
        for c in df.columns
        if c.endswith("_p90_dominance") and c != "worst_mode_p90_dominance"
    ]


def annotate(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    mode_cols = dominance_columns(out)
    out["killer_mode"] = out[mode_cols].idxmin(axis=1).str.replace("_p90_dominance", "", regex=False)
    out["pass_null"] = out["null_strict_rate"].le(PROMOTION_THRESHOLDS["null_strict_rate"])
    out["pass_p90_dom"] = out["p90_dominance"].ge(PROMOTION_THRESHOLDS["p90_dominance"])
    out["pass_mean_dom"] = out["mean_dominance"].ge(PROMOTION_THRESHOLDS["mean_dominance"])
    out["pass_worst_dom"] = out["worst_mode_p90_dominance"].ge(PROMOTION_THRESHOLDS["worst_mode_p90_dominance"])
    out["def_null"] = np.maximum(0.0, out["null_strict_rate"] - PROMOTION_THRESHOLDS["null_strict_rate"]) / (
        1.0 - PROMOTION_THRESHOLDS["null_strict_rate"]
    )
    out["def_p90"] = np.maximum(0.0, PROMOTION_THRESHOLDS["p90_dominance"] - out["p90_dominance"]) / PROMOTION_THRESHOLDS[
        "p90_dominance"
    ]
    out["def_mean"] = np.maximum(0.0, PROMOTION_THRESHOLDS["mean_dominance"] - out["mean_dominance"]) / PROMOTION_THRESHOLDS[
        "mean_dominance"
    ]
    out["def_worst"] = np.maximum(
        0.0,
        PROMOTION_THRESHOLDS["worst_mode_p90_dominance"] - out["worst_mode_p90_dominance"],
    ) / PROMOTION_THRESHOLDS["worst_mode_p90_dominance"]
    out["def_old_strict"] = (~out["old_strict_promote"].astype(bool)).astype(float) * 2.0
    out["def_total"] = out[["def_old_strict", "def_null", "def_p90", "def_mean", "def_worst"]].sum(axis=1)
    return out


def relaxed_gate_table(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for null_thr in [0.0, 0.05, 0.10, 0.20, 0.35, 0.50]:
        base = df["old_strict_promote"].astype(bool) & df["actual_p90"].le(-2.0e-5) & df["null_strict_rate"].le(null_thr)
        rows.append(
            {
                "null_threshold": null_thr,
                "base_count": int(base.sum()),
                "pass_p90_dom": int((base & df["pass_p90_dom"]).sum()),
                "pass_mean_dom": int((base & df["pass_mean_dom"]).sum()),
                "pass_worst_dom": int((base & df["pass_worst_dom"]).sum()),
                "all_promotion_except_null_threshold": int(
                    (
                        base
                        & df["pass_p90_dom"]
                        & df["pass_mean_dom"]
                        & df["pass_worst_dom"]
                    ).sum()
                ),
            }
        )
    return pd.DataFrame(rows)


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(GOVERNOR)
    non_oracle = annotate(df[~df["oracle_control"].astype(bool)].reset_index(drop=True))
    mode_cols = dominance_columns(non_oracle)

    mode_summary = []
    for col in mode_cols:
        mode_summary.append(
            {
                "mode": col.replace("_p90_dominance", ""),
                "mean_dominance": float(non_oracle[col].mean()),
                "min_dominance": float(non_oracle[col].min()),
                "p25_dominance": float(non_oracle[col].quantile(0.25)),
                "pass_0p8_count": int(non_oracle[col].ge(0.80).sum()),
                "pass_0p8_rate": float(non_oracle[col].ge(0.80).mean()),
            }
        )
    mode_summary = pd.DataFrame(mode_summary).sort_values("mean_dominance")

    killer_counts = (
        non_oracle["killer_mode"].value_counts().rename_axis("killer_mode").reset_index(name="count")
    )
    relaxed = relaxed_gate_table(non_oracle)

    near_cols = [
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
        "killer_mode",
        "def_null",
        "def_p90",
        "def_mean",
        "def_worst",
        "def_total",
    ]
    near = non_oracle.sort_values(["def_total", "actual_p90"])[near_cols].head(30)

    summary = pd.concat(
        [
            mode_summary.assign(section="mode_dominance"),
            killer_counts.assign(section="killer_counts"),
            relaxed.assign(section="relaxed_gates"),
        ],
        ignore_index=True,
        sort=False,
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    near.to_csv(NEAR_OUT, index=False)
    write_report(non_oracle, mode_summary, killer_counts, relaxed, near)
    return mode_summary, killer_counts, relaxed


def write_report(
    df: pd.DataFrame,
    mode_summary: pd.DataFrame,
    killer_counts: pd.DataFrame,
    relaxed: pd.DataFrame,
    near: pd.DataFrame,
) -> None:
    target_like_modes = ["target_perm_p90_dominance", "sign_flip_p90_dominance", "q_s_swap_p90_dominance"]
    target_like = {
        col.replace("_p90_dominance", ""): float(df[col].mean())
        for col in target_like_modes
        if col in df.columns
    }
    lines = [
        "# E320 E319 Failure Anatomy",
        "",
        "Public LB was not used. This analyzes why E319 generated many locally visible tensors but no public-free ready candidate.",
        "",
        "## Main Read",
        "",
        f"- non-oracle governed candidates: `{len(df)}`",
        f"- old-strict candidates inside governor: `{int(df['old_strict_promote'].sum())}`",
        f"- public-free ready candidates: `{int(df['public_free_submission_ready'].sum())}`",
        f"- target/sign/QS mean dominance: `{target_like}`",
        "",
        "The failure is not primarily target permutation, sign, or Q/S swap. Those controls are mostly beaten. The blocker is row/subject/dateblock placement ambiguity.",
        "",
        "## Mode Dominance",
        "",
        md(mode_summary, n=20),
        "",
        "## Killer Modes",
        "",
        md(killer_counts, n=20),
        "",
        "## Relaxed Promotion Gates",
        "",
        md(relaxed, n=20),
        "",
        "## Closest Near Misses",
        "",
        md(near, n=30),
        "",
        "## Decision",
        "",
        "- E319 average-consensus generation should not be scaled or public-tested.",
        "- The next generator needs explicit adversarial row/subject/dateblock geometry, not broader averaging of selected placements.",
        "- The most useful next target is mode-specific action health: for a chosen regime, learn which delta shapes beat same-regime nulls before old-selector visibility is considered.",
        "",
        "## Outputs",
        "",
        f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
        f"- `{NEAR_OUT.relative_to(ROOT)}`",
        f"- `{REPORT_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    mode_summary, killer_counts, relaxed = run()
    print(f"mode_rows={len(mode_summary)}")
    print("killer_modes=" + ",".join(f"{r.killer_mode}:{r.count}" for r in killer_counts.itertuples()))
    print("best_relaxed_all=" + str(int(relaxed["all_promotion_except_null_threshold"].max())))
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
