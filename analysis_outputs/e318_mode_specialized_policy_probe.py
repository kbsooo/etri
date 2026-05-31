#!/usr/bin/env python3
"""E318: mode-specialized placement policy probe.

E317 found a split:

* human diary context helps choose plausible placement regime/source neighborhood;
* action geometry is stronger inside a fixed regime.

E318 asks whether that can already select healthier placements from the
E315 actual/null mini-world without public LB.  It does not create a
submission.  The output is a routebook for the next generator: if a policy
cannot pick better placements locally from existing controls, materializing
new probabilities from it is premature.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e313_human_action_signature import md  # noqa: E402
from e317_human_placement_outcome_learner import load_feature_rows  # noqa: E402


E317_OOF = OUT / "e317_human_placement_outcome_oof.csv"
SCORES_OUT = OUT / "e318_mode_specialized_policy_scores.csv"
SELECTED_OUT = OUT / "e318_mode_specialized_policy_selected.csv"
SUMMARY_OUT = OUT / "e318_mode_specialized_policy_summary.csv"
REPORT_OUT = OUT / "e318_mode_specialized_policy_report.md"


POLICY_SPECS = {
    "human_p90_rank": [("predict_p90_rank", "human_signature", 1.0)],
    "human_action_p90_rank": [("predict_p90_rank", "human_plus_action", 1.0)],
    "human_identity_action_p90_rank": [("predict_p90_rank", "human_plus_identity_action", 1.0)],
    "health_human_action": [("predict_health_score", "human_plus_action", 1.0)],
    "health_human_identity_action": [("predict_health_score", "human_plus_identity_action", 1.0)],
    "joint_shape_identity": [("classify_joint_health", "shape_plus_identity", 1.0)],
    "joint_human_action": [("classify_joint_health", "human_plus_action", 1.0)],
    "regime_then_geometry": [
        ("predict_p90_rank", "human_plus_identity_action", 0.55),
        ("classify_joint_health", "shape_plus_identity", 0.30),
        ("predict_health_score", "human_plus_action", 0.15),
    ],
    "human_regime_only": [
        ("predict_p90_rank", "human_signature", 0.55),
        ("predict_health_score", "human_signature", 0.25),
        ("classify_joint_health", "human_signature", 0.20),
    ],
    "geometry_health_only": [
        ("predict_p90_rank", "shape_plus_identity", 0.45),
        ("classify_joint_health", "shape_plus_identity", 0.35),
        ("predict_health_score", "shape_plus_identity", 0.20),
    ],
}


def zscore_by_source(df: pd.DataFrame, col: str) -> pd.Series:
    def z(s: pd.Series) -> pd.Series:
        std = float(s.std(ddof=0))
        if not np.isfinite(std) or std < 1e-12:
            return pd.Series(np.zeros(len(s)), index=s.index)
        return (s - float(s.mean())) / std

    return df.groupby("source_basename")[col].transform(z)


def load_rows_with_oof() -> pd.DataFrame:
    df = load_feature_rows()
    df["true_p90_rank_health"] = 1.0 - df["target_p90_rank_pct"].astype(float)
    df["true_mean_rank_health"] = 1.0 - df["target_mean_rank_pct"].astype(float)
    df["true_joint_health"] = df["target_joint_health"].astype(int)
    df["true_visible"] = df["target_visible"].astype(int)

    oof = pd.read_csv(E317_OOF)
    keep_tasks = {
        "predict_p90_rank",
        "predict_health_score",
        "classify_joint_health",
    }
    oof = oof[oof["split"].eq("source_group") & oof["task"].isin(keep_tasks)].copy()
    pred = oof.pivot_table(
        index=["basename", "source_basename", "placement_mode"],
        columns=["task", "feature_block"],
        values="oof_pred",
        aggfunc="mean",
    )
    pred.columns = [f"pred__{task}__{block}" for task, block in pred.columns]
    pred = pred.reset_index()
    df = df.merge(pred, on=["basename", "source_basename", "placement_mode"], how="left")

    for policy, specs in POLICY_SPECS.items():
        score = pd.Series(0.0, index=df.index)
        weight_sum = 0.0
        for task, block, weight in specs:
            col = f"pred__{task}__{block}"
            if col not in df.columns:
                continue
            zcol = f"z__{task}__{block}"
            if zcol not in df.columns:
                df[zcol] = zscore_by_source(df, col)
            score = score + weight * df[zcol].fillna(0.0)
            weight_sum += abs(weight)
        df[f"policy__{policy}"] = score / weight_sum if weight_sum else 0.0
    return df


def selected_by_policy(df: pd.DataFrame, policy: str) -> pd.DataFrame:
    score_col = f"policy__{policy}"
    idx = df.groupby("source_basename")[score_col].idxmax()
    out = df.loc[idx].copy()
    out["policy"] = policy
    out["selected_score"] = out[score_col]
    return out.reset_index(drop=True)


def actual_baseline(df: pd.DataFrame) -> pd.DataFrame:
    out = df[df["placement_mode"].eq("actual")].copy()
    out["policy"] = "actual_baseline"
    out["selected_score"] = np.nan
    return out.reset_index(drop=True)


def oracle_baseline(df: pd.DataFrame, target: str, name: str) -> pd.DataFrame:
    idx = df.groupby("source_basename")[target].idxmax()
    out = df.loc[idx].copy()
    out["policy"] = name
    out["selected_score"] = out[target]
    return out.reset_index(drop=True)


def summarize_selection(sel: pd.DataFrame, df: pd.DataFrame) -> dict[str, Any]:
    true_top = df.loc[df.groupby("source_basename")["true_p90_rank_health"].idxmax(), ["source_basename", "placement_mode"]]
    true_top = true_top.rename(columns={"placement_mode": "oracle_p90_mode"})
    part = sel.merge(true_top, on="source_basename", how="left")
    actual = actual_baseline(df)[
        [
            "source_basename",
            "target_p90",
            "target_mean",
            "true_p90_rank_health",
            "true_mean_rank_health",
            "true_joint_health",
            "true_visible",
            "target_health_score",
        ]
    ].rename(
        columns={
            "target_p90": "actual_target_p90",
            "target_mean": "actual_target_mean",
            "true_p90_rank_health": "actual_p90_rank_health",
            "true_mean_rank_health": "actual_mean_rank_health",
            "true_joint_health": "actual_joint_health",
            "true_visible": "actual_visible",
            "target_health_score": "actual_health_score",
        }
    )
    part = part.merge(actual, on="source_basename", how="left")
    return {
        "policy": str(part["policy"].iloc[0]),
        "sources": int(len(part)),
        "selected_actual_rate": float(part["placement_mode"].eq("actual").mean()),
        "selected_row_rate": float(part["placement_mode"].eq("row").mean()),
        "selected_subject_rate": float(part["placement_mode"].eq("subject").mean()),
        "selected_dateblock_rate": float(part["placement_mode"].eq("dateblock").mean()),
        "oracle_mode_accuracy": float(part["placement_mode"].eq(part["oracle_p90_mode"]).mean()),
        "visible_rate": float(part["true_visible"].mean()),
        "joint_health_rate": float(part["true_joint_health"].mean()),
        "p90_rank_health_mean": float(part["true_p90_rank_health"].mean()),
        "mean_rank_health_mean": float(part["true_mean_rank_health"].mean()),
        "health_score_mean": float(part["target_health_score"].mean()),
        "target_p90_mean": float(part["target_p90"].mean()),
        "target_mean_mean": float(part["target_mean"].mean()),
        "delta_p90_vs_actual": float((part["target_p90"] - part["actual_target_p90"]).mean()),
        "delta_mean_vs_actual": float((part["target_mean"] - part["actual_target_mean"]).mean()),
        "delta_rank_vs_actual": float((part["true_p90_rank_health"] - part["actual_p90_rank_health"]).mean()),
        "delta_health_score_vs_actual": float((part["target_health_score"] - part["actual_health_score"]).mean()),
        "selected_paths_found": int(part["path"].notna().sum()),
    }


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = load_rows_with_oof()
    selected_frames = [actual_baseline(df)]
    selected_frames.extend(
        [
            oracle_baseline(df, "true_p90_rank_health", "oracle_p90_rank"),
            oracle_baseline(df, "target_health_score", "oracle_health_score"),
        ]
    )
    for policy in POLICY_SPECS:
        selected_frames.append(selected_by_policy(df, policy))
    selected = pd.concat(selected_frames, ignore_index=True)
    summaries = [summarize_selection(part, df) for _, part in selected.groupby("policy", sort=False)]
    summary = pd.DataFrame(summaries).sort_values(
        ["delta_rank_vs_actual", "p90_rank_health_mean"],
        ascending=[False, False],
    )

    score_cols = [
        "basename",
        "source_basename",
        "placement_mode",
        "rep",
        "is_actual",
        "path",
        "recipe",
        "target_p90",
        "target_mean",
        "true_p90_rank_health",
        "true_mean_rank_health",
        "true_joint_health",
        "true_visible",
        "target_health_score",
    ]
    score_cols += [c for c in df.columns if c.startswith("pred__") or c.startswith("policy__")]
    selected_cols = ["policy", "selected_score"] + score_cols
    df[[c for c in score_cols if c in df.columns]].to_csv(SCORES_OUT, index=False)
    selected[[c for c in selected_cols if c in selected.columns]].to_csv(SELECTED_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(df, selected, summary)
    return df, selected, summary


def write_report(df: pd.DataFrame, selected: pd.DataFrame, summary: pd.DataFrame) -> None:
    non_oracle = summary[~summary["policy"].str.startswith("oracle") & ~summary["policy"].eq("actual_baseline")]
    best = non_oracle.head(1)
    top_selected = (
        selected[selected["policy"].isin(non_oracle.head(3)["policy"])]
        .sort_values(["policy", "true_p90_rank_health", "target_health_score"], ascending=[True, False, False])
        .head(30)
    )
    mode_counts = (
        selected[~selected["policy"].str.startswith("oracle")]
        .pivot_table(index="policy", columns="placement_mode", values="basename", aggfunc="count", fill_value=0)
        .reset_index()
    )
    lines = [
        "# E318 Mode-Specialized Placement Policy Probe",
        "",
        "Public LB는 사용하지 않았다. E317 OOF predictions로 E315 actual/null placement pool 안에서 더 건강한 placement를 고를 수 있는지 확인했다.",
        "",
        "## Dataset",
        "",
        f"- rows: `{len(df)}`",
        f"- sources: `{df['source_basename'].nunique()}`",
        f"- policies: `{len(POLICY_SPECS)}`",
        "",
        "## Policy Summary",
        "",
        md(summary, n=20),
        "",
        "## Mode Counts",
        "",
        md(mode_counts, n=20),
        "",
        "## Top Selected Rows From Best Non-Oracle Policies",
        "",
        md(
            top_selected[
                [
                    "policy",
                    "source_basename",
                    "basename",
                    "placement_mode",
                    "recipe",
                    "true_p90_rank_health",
                    "true_mean_rank_health",
                    "true_joint_health",
                    "true_visible",
                    "target_p90",
                    "target_mean",
                    "selected_score",
                    "path",
                ]
            ],
            n=30,
        ),
        "",
        "## Decision",
        "",
    ]
    if not best.empty:
        rec = best.iloc[0]
        lines.append(
            f"- Best non-oracle policy is `{rec['policy']}` with delta p90-rank vs actual `{rec['delta_rank_vs_actual']:.6f}` and oracle-mode accuracy `{rec['oracle_mode_accuracy']:.6f}`."
        )
        if rec["delta_rank_vs_actual"] > 0.05 and rec["oracle_mode_accuracy"] > 0.30:
            lines.append("- This supports the next mode-specialized generator: selecting placement regime locally has measurable value.")
        else:
            lines.append("- This is not strong enough to justify a generator yet; selection is below the threshold for local promotion.")
        if rec["selected_actual_rate"] < 0.50:
            lines.append("- The policy often selects row/subject/dateblock control placements, which means the current actual materializer is frequently placing human/social deltas in the wrong regime.")
    lines.extend(
        [
            "- No submission is created. Existing null-placement files are controls, not public candidates, unless regenerated and governed with fresh row/subject/dateblock/sign/target nulls.",
            "- Next action if this branch continues: build a generator that explicitly chooses mode first, then uses within-mode geometry to construct a new action and rerun direct null governance.",
            "",
            "## Outputs",
            "",
            f"- `{SCORES_OUT.relative_to(ROOT)}`",
            f"- `{SELECTED_OUT.relative_to(ROOT)}`",
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df, _, summary = run()
    print(f"rows={len(df)}")
    print(f"sources={df['source_basename'].nunique()}")
    best = summary[
        ~summary["policy"].str.startswith("oracle")
        & ~summary["policy"].eq("actual_baseline")
    ].head(1)
    if not best.empty:
        rec = best.iloc[0]
        print(f"best_policy={rec['policy']}")
        print(f"best_delta_rank_vs_actual={rec['delta_rank_vs_actual']:.6f}")
        print(f"best_oracle_mode_accuracy={rec['oracle_mode_accuracy']:.6f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
