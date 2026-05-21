from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def source_family(source: str) -> str:
    if source.startswith("db_prebed"):
        return "digital_boundary_prebed"
    if source.startswith("db_sleep_phone"):
        return "digital_boundary_sleep_phone"
    if source.startswith("db_postwake"):
        return "digital_boundary_postwake"
    if source.startswith("db_app_stim"):
        return "digital_boundary_app_stim"
    if source.startswith("db_core"):
        return "digital_boundary_core"
    if source.startswith("best_plus_digital_boundary") or source.startswith("digital_boundary"):
        return "digital_boundary"
    if source.startswith("best_plus_mobility_constriction") or source.startswith("mobility_constriction"):
        return "mobility_constriction"
    if source.startswith("best_plus_fatigue_carryover") or source.startswith("fatigue_carryover"):
        return "fatigue_carryover"
    if source.startswith("best_plus_routine_digital"):
        return "routine_digital"
    if source.startswith("best_plus_digital_sleep") or source.startswith("digital_sleep"):
        return "digital_sleep"
    if source.startswith("best_plus_routine_regularity") or source.startswith("routine_regularity"):
        return "routine_regularity"
    if source.startswith("best_plus_sleep_intrusion") or source.startswith("sleep_intrusion"):
        return "sleep_intrusion"
    if source.startswith("best_plus_trajectory_proto") or source.startswith("trajectory_proto"):
        return "trajectory_proto"
    if source.startswith("best_plus_event_rhythm") or source.startswith("event_rhythm"):
        return "event_rhythm"
    if source.startswith("td_future"):
        return "future"
    if source.startswith("td_past_recovery"):
        return "past_recovery"
    if source.startswith("td_recovery"):
        return "recovery"
    if source.startswith("td_trajectory"):
        return "trajectory"
    if source.startswith("td_past"):
        return "past"
    if source.startswith("best"):
        return "best_late_fusion"
    return "other"


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    fold_losses = pd.read_csv(args.fold_losses)
    fold_losses = fold_losses[fold_losses["target"].isin(TARGET_COLUMNS)].copy()
    if args.source_prefix:
        mask = np.zeros(len(fold_losses), dtype=bool)
        for prefix in args.source_prefix:
            mask |= fold_losses["source"].astype(str).str.startswith(prefix).to_numpy()
        fold_losses = fold_losses[mask].copy()
    if fold_losses.empty:
        raise ValueError("No fold losses remain after filtering")

    folds = sorted(fold_losses["fold"].unique().tolist())
    base_source = args.base_source
    if base_source not in set(fold_losses["source"]):
        raise ValueError(f"Base source not present after filtering: {base_source}")

    selected_rows = []
    candidate_rows = []
    for held_fold in folds:
        train_part = fold_losses[fold_losses["fold"] != held_fold]
        held_part = fold_losses[fold_losses["fold"] == held_fold]
        for target in TARGET_COLUMNS:
            train_target = train_part[train_part["target"] == target]
            held_target = held_part[held_part["target"] == target]
            train_scores = (
                train_target.groupby("source", as_index=False)["loss"]
                .mean()
                .rename(columns={"loss": "selector_loss"})
                .sort_values(["selector_loss", "source"], ascending=[True, True])
            )
            raw_best_source = str(train_scores.iloc[0]["source"])
            raw_best_selector_loss = float(train_scores.iloc[0]["selector_loss"])
            train_base_loss = float(train_scores.loc[train_scores["source"] == base_source, "selector_loss"].iloc[0])
            if raw_best_selector_loss < train_base_loss - args.min_train_delta:
                best_source = raw_best_source
                selector_loss = raw_best_selector_loss
                selection_action = "switch"
            else:
                best_source = base_source
                selector_loss = train_base_loss
                selection_action = "base"
            held_loss = float(held_target.loc[held_target["source"] == best_source, "loss"].iloc[0])
            base_loss = float(held_target.loc[held_target["source"] == base_source, "loss"].iloc[0])
            selected_rows.append(
                {
                    "held_fold": int(held_fold),
                    "target": target,
                    "selected_source": best_source,
                    "source_family": source_family(best_source),
                    "raw_best_source": raw_best_source,
                    "raw_best_selector_loss": raw_best_selector_loss,
                    "train_base_loss": train_base_loss,
                    "selector_loss": selector_loss,
                    "selection_action": selection_action,
                    "held_loss": held_loss,
                    "base_loss": base_loss,
                    "delta_vs_base": held_loss - base_loss,
                }
            )
            for _, row in train_scores.head(args.top_k).iterrows():
                source = str(row["source"])
                candidate_rows.append(
                    {
                        "held_fold": int(held_fold),
                        "target": target,
                        "rank": len([r for r in candidate_rows if r["held_fold"] == int(held_fold) and r["target"] == target]) + 1,
                        "source": source,
                        "source_family": source_family(source),
                        "selector_loss": float(row["selector_loss"]),
                        "held_loss": float(held_target.loc[held_target["source"] == source, "loss"].iloc[0]),
                    }
                )

    selected = pd.DataFrame(selected_rows)
    candidates = pd.DataFrame(candidate_rows)
    target_summary = (
        selected.groupby(["target"], as_index=False)
        .agg(
            selected_loss=("held_loss", "mean"),
            base_loss=("base_loss", "mean"),
            delta_vs_base=("delta_vs_base", "mean"),
            most_common_family=("source_family", lambda s: s.value_counts().index[0]),
        )
        .sort_values("target")
    )
    family_counts = (
        selected.groupby(["target", "source_family"], as_index=False)
        .size()
        .sort_values(["target", "size"], ascending=[True, False])
    )
    overall = {
        "base_avg": float(target_summary["base_loss"].mean()),
        "nested_selected_avg": float(target_summary["selected_loss"].mean()),
        "delta_vs_base": float(target_summary["delta_vs_base"].mean()),
        "n_folds": int(len(folds)),
        "base_source": base_source,
        "min_train_delta": float(args.min_train_delta),
    }

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    selected.to_csv(output_dir / "nested_selected_fold_losses.csv", index=False)
    candidates.to_csv(output_dir / "nested_candidate_fold_losses.csv", index=False)
    target_summary.to_csv(output_dir / "target_summary.csv", index=False)
    family_counts.to_csv(output_dir / "family_counts.csv", index=False)
    report = {
        "fold_losses": args.fold_losses,
        "overall": overall,
        "target_summary": target_summary.to_dict(orient="records"),
        "family_counts": family_counts.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# Nested Source Selection Diagnostics",
        "",
        "## Purpose",
        "",
        "Estimate whether target-specific temporal-deviation source selection survives fold-safe selection.",
        "",
        "## Overall",
        "",
        f"- Base source: `{base_source}`",
        f"- Base avg fold loss: `{overall['base_avg']:.6f}`",
        f"- Nested selected avg fold loss: `{overall['nested_selected_avg']:.6f}`",
        f"- Delta vs base: `{overall['delta_vs_base']:.6f}`",
        f"- Minimum train-fold improvement needed to switch: `{overall['min_train_delta']:.6f}`",
        "",
        "## Target Summary",
        "",
        dataframe_to_markdown(target_summary),
        "",
        "## Selected Family Counts",
        "",
        dataframe_to_markdown(family_counts),
        "",
        "## Read",
        "",
        "A negative delta means the family choice still helps after the held fold is hidden during source selection.",
        "A positive delta means the apparent target-specific gain is likely selection noise or too unstable for a decoder.",
    ]
    (output_dir / "report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Nested fold-safe source selection diagnostics from fold target losses.")
    parser.add_argument("--fold-losses", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--base-source", default="best__absolute_plus_deviation__c0.3_b0.2")
    parser.add_argument("--source-prefix", nargs="*", default=["best", "td_future", "td_trajectory", "td_recovery", "td_past"])
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--min-train-delta", type=float, default=0.0)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
