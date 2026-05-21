from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def source_family(source: str) -> str:
    if source.startswith("boundary_target_map"):
        return "boundary_target_map"
    if source.startswith("best_plus_rr_"):
        return source.split("__", maxsplit=1)[0]
    if source.startswith("rr_"):
        return source.split("__", maxsplit=1)[0]
    if source.startswith("best_plus_scs_pca"):
        return "best_plus_sleep_consensus_stability_pca"
    if source.startswith("scs_pca"):
        return "sleep_consensus_stability_pca"
    if source.startswith("best_plus_s4_routine_fragment"):
        return "best_plus_s4_routine_fragment"
    if source.startswith("s4_routine_fragment"):
        return "s4_routine_fragment"
    if source.startswith("best_plus_scc_core"):
        return "best_plus_sleep_consensus_compact_core"
    if source.startswith("best_plus_scc_subject_relative"):
        return "best_plus_sleep_consensus_compact_subject_relative"
    if source.startswith("best_plus_scc_rolling"):
        return "best_plus_sleep_consensus_compact_rolling"
    if source.startswith("best_plus_scc_all"):
        return "best_plus_sleep_consensus_compact_all"
    if source.startswith("scc_core"):
        return "sleep_consensus_compact_core"
    if source.startswith("scc_subject_relative"):
        return "sleep_consensus_compact_subject_relative"
    if source.startswith("scc_rolling"):
        return "sleep_consensus_compact_rolling"
    if source.startswith("scc_all"):
        return "sleep_consensus_compact_all"
    if source.startswith("best_plus_scp_consensus_purity"):
        return "best_plus_sleep_consensus_purity"
    if source.startswith("best_plus_scp_micro_awakenings"):
        return "best_plus_sleep_consensus_micro_awakenings"
    if source.startswith("best_plus_scp_missingness_semantics"):
        return "best_plus_sleep_consensus_missingness"
    if source.startswith("best_plus_scp_final_sleep_quality"):
        return "best_plus_sleep_consensus_final_quality"
    if source.startswith("best_plus_scp_prebed_conflict"):
        return "best_plus_sleep_consensus_prebed_conflict"
    if source.startswith("best_plus_scp_sleep_metric_interaction"):
        return "best_plus_sleep_consensus_metric_interaction"
    if source.startswith("best_plus_scp_subject_relative_only"):
        return "best_plus_sleep_consensus_subject_relative"
    if source.startswith("best_plus_scp_rolling_context_only"):
        return "best_plus_sleep_consensus_rolling_context"
    if source.startswith("best_plus_scp_base_values_only"):
        return "best_plus_sleep_consensus_base_values"
    if source.startswith("scp_consensus_purity"):
        return "sleep_consensus_purity"
    if source.startswith("scp_micro_awakenings"):
        return "sleep_consensus_micro_awakenings"
    if source.startswith("scp_missingness_semantics"):
        return "sleep_consensus_missingness"
    if source.startswith("scp_final_sleep_quality"):
        return "sleep_consensus_final_quality"
    if source.startswith("scp_prebed_conflict"):
        return "sleep_consensus_prebed_conflict"
    if source.startswith("scp_sleep_metric_interaction"):
        return "sleep_consensus_metric_interaction"
    if source.startswith("scp_subject_relative_only"):
        return "sleep_consensus_subject_relative"
    if source.startswith("scp_rolling_context_only"):
        return "sleep_consensus_rolling_context"
    if source.startswith("scp_base_values_only"):
        return "sleep_consensus_base_values"
    if source.startswith("sleep_consensus_purity"):
        return "sleep_consensus_purity"
    if source.startswith("best_plus_wai_activation_latency"):
        return "best_plus_wake_activation_latency"
    if source.startswith("best_plus_wai_activation_slope"):
        return "best_plus_wake_activation_slope"
    if source.startswith("best_plus_wai_phone_inertia"):
        return "best_plus_wake_phone_inertia"
    if source.startswith("best_plus_wai_light_hr_entrainment"):
        return "best_plus_wake_light_hr_entrainment"
    if source.startswith("best_plus_wai_sleep_recovery_interaction"):
        return "best_plus_wake_sleep_recovery_interaction"
    if source.startswith("best_plus_wai_subject_relative_only"):
        return "best_plus_wake_subject_relative"
    if source.startswith("best_plus_wai_rolling_context_only"):
        return "best_plus_wake_rolling_context"
    if source.startswith("best_plus_wai_base_values_only"):
        return "best_plus_wake_base_values"
    if source.startswith("wai_activation_latency"):
        return "wake_activation_latency"
    if source.startswith("wai_activation_slope"):
        return "wake_activation_slope"
    if source.startswith("wai_phone_inertia"):
        return "wake_phone_inertia"
    if source.startswith("wai_light_hr_entrainment"):
        return "wake_light_hr_entrainment"
    if source.startswith("wai_sleep_recovery_interaction"):
        return "wake_sleep_recovery_interaction"
    if source.startswith("wai_subject_relative_only"):
        return "wake_subject_relative"
    if source.startswith("wai_rolling_context_only"):
        return "wake_rolling_context"
    if source.startswith("wai_base_values_only"):
        return "wake_base_values"
    if source.startswith("wake_activation_inertia"):
        return "wake_activation_inertia"
    if source.startswith("best_plus_sot_micro_charging_timing"):
        return "best_plus_sleep_onset_micro_charging_timing"
    if source.startswith("best_plus_sot_micro_charging_windows"):
        return "best_plus_sleep_onset_micro_charging_windows"
    if source.startswith("best_plus_sot_micro_settled_no_phone"):
        return "best_plus_sleep_onset_micro_settled_no_phone"
    if source.startswith("best_plus_sot_micro_settled_charging"):
        return "best_plus_sleep_onset_micro_settled_charging"
    if source.startswith("best_plus_sot_micro_phone_charging_conflict"):
        return "best_plus_sleep_onset_micro_phone_charging_conflict"
    if source.startswith("best_plus_sot_micro_readiness_rolling"):
        return "best_plus_sleep_onset_micro_readiness_rolling"
    if source.startswith("best_plus_sot_micro_pre30m_settle"):
        return "best_plus_sleep_onset_micro_pre30m_settle"
    if source.startswith("best_plus_sot_micro_pre1h_settle"):
        return "best_plus_sleep_onset_micro_pre1h_settle"
    if source.startswith("best_plus_sot_micro_base_values_only"):
        return "best_plus_sleep_onset_micro_base_values"
    if source.startswith("best_plus_sot_micro_subject_relative_only"):
        return "best_plus_sleep_onset_micro_subject_relative"
    if source.startswith("best_plus_sot_micro_rolling_context_only"):
        return "best_plus_sleep_onset_micro_rolling_context"
    if source.startswith("best_plus_sot_micro_s3_core_timing_settle_conflict"):
        return "best_plus_sleep_onset_micro_s3_core"
    if source.startswith("best_plus_sot_micro_s3_final_hour_core"):
        return "best_plus_sleep_onset_micro_s3_final_hour"
    if source.startswith("sot_micro_charging_timing"):
        return "sleep_onset_micro_charging_timing"
    if source.startswith("sot_micro_charging_windows"):
        return "sleep_onset_micro_charging_windows"
    if source.startswith("sot_micro_settled_no_phone"):
        return "sleep_onset_micro_settled_no_phone"
    if source.startswith("sot_micro_settled_charging"):
        return "sleep_onset_micro_settled_charging"
    if source.startswith("sot_micro_phone_charging_conflict"):
        return "sleep_onset_micro_phone_charging_conflict"
    if source.startswith("sot_micro_readiness_rolling"):
        return "sleep_onset_micro_readiness_rolling"
    if source.startswith("sot_micro_pre30m_settle"):
        return "sleep_onset_micro_pre30m_settle"
    if source.startswith("sot_micro_pre1h_settle"):
        return "sleep_onset_micro_pre1h_settle"
    if source.startswith("sot_micro_base_values_only"):
        return "sleep_onset_micro_base_values"
    if source.startswith("sot_micro_subject_relative_only"):
        return "sleep_onset_micro_subject_relative"
    if source.startswith("sot_micro_rolling_context_only"):
        return "sleep_onset_micro_rolling_context"
    if source.startswith("sot_micro_s3_core_timing_settle_conflict"):
        return "sleep_onset_micro_s3_core"
    if source.startswith("sot_micro_s3_final_hour_core"):
        return "sleep_onset_micro_s3_final_hour"
    if source.startswith("best_plus_sot_last_event_latency"):
        return "best_plus_sleep_onset_latency"
    if source.startswith("best_plus_sot_shutdown_slope"):
        return "best_plus_sleep_onset_shutdown"
    if source.startswith("best_plus_sot_prebed_fragmentation"):
        return "best_plus_sleep_onset_fragmentation"
    if source.startswith("best_plus_sot_light_environment_transition"):
        return "best_plus_sleep_onset_environment"
    if source.startswith("best_plus_sot_charging_settle"):
        return "best_plus_sleep_onset_charging"
    if source.startswith("best_plus_sot_onset_consensus"):
        return "best_plus_sleep_onset_consensus"
    if source.startswith("best_plus_sot_full"):
        return "best_plus_sleep_onset_transition"
    if source.startswith("sot_last_event_latency"):
        return "sleep_onset_latency"
    if source.startswith("sot_shutdown_slope"):
        return "sleep_onset_shutdown"
    if source.startswith("sot_prebed_fragmentation"):
        return "sleep_onset_fragmentation"
    if source.startswith("sot_light_environment_transition"):
        return "sleep_onset_environment"
    if source.startswith("sot_charging_settle"):
        return "sleep_onset_charging"
    if source.startswith("sot_onset_consensus"):
        return "sleep_onset_consensus"
    if source.startswith("sleep_onset_transition"):
        return "sleep_onset_transition"
    if source.startswith("best_plus_cc_load"):
        return "best_plus_causal_chain_load"
    if source.startswith("best_plus_cc_arousal"):
        return "best_plus_causal_chain_arousal"
    if source.startswith("best_plus_cc_opportunity"):
        return "best_plus_causal_chain_opportunity"
    if source.startswith("best_plus_cc_continuity"):
        return "best_plus_causal_chain_continuity"
    if source.startswith("best_plus_cc_recovery"):
        return "best_plus_causal_chain_recovery"
    if source.startswith("best_plus_cc_chain_interactions"):
        return "best_plus_causal_chain_interactions"
    if source.startswith("cc_load"):
        return "causal_chain_load"
    if source.startswith("cc_arousal"):
        return "causal_chain_arousal"
    if source.startswith("cc_opportunity"):
        return "causal_chain_opportunity"
    if source.startswith("cc_continuity"):
        return "causal_chain_continuity"
    if source.startswith("cc_recovery"):
        return "causal_chain_recovery"
    if source.startswith("cc_chain_interactions"):
        return "causal_chain_interactions"
    if source.startswith("causal_chain"):
        return "causal_chain"
    if source.startswith("best_plus_di_social_isolation"):
        return "best_plus_digital_isolation_social"
    if source.startswith("best_plus_di_app_diversity_shift"):
        return "best_plus_digital_isolation_app_diversity"
    if source.startswith("best_plus_di_phone_fragmentation"):
        return "best_plus_digital_isolation_phone_fragmentation"
    if source.startswith("best_plus_di_prebed_consumption"):
        return "best_plus_digital_isolation_prebed"
    if source.startswith("best_plus_di_digital_rhythm"):
        return "best_plus_digital_isolation_rhythm"
    if source.startswith("di_social_isolation"):
        return "digital_isolation_social"
    if source.startswith("di_app_diversity_shift"):
        return "digital_isolation_app_diversity"
    if source.startswith("di_phone_fragmentation"):
        return "digital_isolation_phone_fragmentation"
    if source.startswith("di_prebed_consumption"):
        return "digital_isolation_prebed"
    if source.startswith("di_digital_rhythm"):
        return "digital_isolation_rhythm"
    if source.startswith("digital_isolation"):
        return "digital_isolation"
    if source.startswith("acm_ambient_light"):
        return "ambient_light"
    if source.startswith("acm_coverage_no_wear"):
        return "coverage_no_wear"
    if source.startswith("acm_motif_distance"):
        return "day_state_motif"
    if source.startswith("acm_night_environment"):
        return "night_environment"
    if source.startswith("acm_coverage_rhythm"):
        return "coverage_rhythm"
    if source.startswith("ambient_coverage_motif"):
        return "ambient_coverage_motif"
    if source.startswith("ef_energy_phase"):
        return "energy_phase"
    if source.startswith("ef_daytime_fragmentation"):
        return "daytime_fragmentation"
    if source.startswith("ef_commute_stress"):
        return "commute_stress"
    if source.startswith("ef_recovery_slope"):
        return "energy_recovery_slope"
    if source.startswith("ef_digital_energy_coupling"):
        return "digital_energy_coupling"
    if source.startswith("energy_fragmentation"):
        return "energy_fragmentation"
    if source.startswith("cs_sleep_to_sleep"):
        return "chronotype_sleep_to_sleep"
    if source.startswith("cs_phase_social_jetlag"):
        return "chronotype_phase_social_jetlag"
    if source.startswith("cs_debt_ledger"):
        return "chronotype_debt_ledger"
    if source.startswith("cs_postwake_energy"):
        return "chronotype_postwake_energy"
    if source.startswith("cs_postwake_digital"):
        return "chronotype_postwake_digital"
    if source.startswith("cs_prebed_arousal"):
        return "chronotype_prebed_arousal"
    if source.startswith("chronotype_sleep_debt"):
        return "chronotype_sleep_debt"
    if source.startswith("sfr_sleep_wake_digital"):
        return "sleep_fragment_recovery_sleep_wake_digital"
    if source.startswith("sfr_postwake_digital"):
        return "sleep_fragment_recovery_postwake_digital"
    if source.startswith("sfr_sleep_digital"):
        return "sleep_fragment_recovery_sleep_digital"
    if source.startswith("sfr_sleep_sensor"):
        return "sleep_fragment_recovery_sleep_sensor"
    if source.startswith("sfr_awakening"):
        return "sleep_fragment_recovery_awakening"
    if source.startswith("sfr_postwake_recovery"):
        return "sleep_fragment_recovery_postwake"
    if source.startswith("sfr_fragment_core"):
        return "sleep_fragment_recovery_core"
    if source.startswith("best_plus_sleep_fragment_recovery") or source.startswith("sleep_fragment_recovery"):
        return "sleep_fragment_recovery"
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
