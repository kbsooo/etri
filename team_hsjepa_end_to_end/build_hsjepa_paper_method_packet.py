#!/usr/bin/env python3
"""Build a paper/team method packet for HS-JEPA.

This file is deliberately not another modeling experiment.  It turns the
validated package outputs into a paper-facing method description that a teammate
can read without knowing historical experiment version names.
"""

from __future__ import annotations

from pathlib import Path
import json
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"

PACKAGE_JSON = OUT / "route_conserving_s2_bridge_package.json"
STRESS_CSV = OUT / "route_conserving_s2_bridge_stress_summary.csv"
EVIDENCE_CSV = OUT / "route_conserving_s2_bridge_evidence_table.csv"
VALIDATION_JSON = OUT / "route_conserving_s2_bridge_validation_report.json"
CONTRACT_JSON = OUT / "hsjepa_reproducibility_contract.json"
READINESS_JSON = OUT / "hsjepa_architecture_readiness_report.json"
GENERALITY_JSON = OUT / "hsjepa_generality_report.json"
BOUNDARY_AUDIT_JSON = OUT / "hsjepa_core_adapter_boundary_audit.json"
CORE_MANIFEST_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_manifest.json"
CORE_ABLATION_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_ablation_contract.json"
CORE_REFERENCE_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_reference_run.json"
CORE_BENCHMARK_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_module_benchmark.json"
ADAPTER_REPORT_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "sleep_competition_adapter_report.json"
BIG_BET_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hsjepa_big_bet_queue.json"
OG_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "og_only_assignment_teacher_probe.json"
ASSIGNMENT_GAP_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "assignment_gap_decomposition_probe.json"
ROW_SUPPORT_SENSOR_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hidden_row_support_sensor_probe.json"
MASKED_ROW_SUPPORT_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "masked_row_support_objective_probe.json"
ROW_SUPPORT_DECODER_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "row_support_strict_action_decoder" / "row_support_strict_action_decoder_readout.json"
ROUTE_FRONTIER_DECODER_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "route_frontier_action_decoder" / "route_frontier_action_decoder_readout.json"
ROUTE_TOXICITY_FUSION_DECODER_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "route_toxicity_fusion_decoder" / "route_toxicity_fusion_decoder_readout.json"
DECODER_ORDER_JURY_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "decoder_order_jury_solver" / "decoder_order_jury_solver_readout.json"
DECODER_BOUNDARY_TOMOGRAPHY_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "decoder_boundary_tomography_solver" / "decoder_boundary_tomography_readout.json"
CORE_MEDIATED_RELEASE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "core_mediated_action_release" / "core_mediated_action_release_readout.json"
CORE_RELEASE_ABLATION_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "core_release_ablation_probe" / "core_release_ablation_probe_readout.json"
CORE_HEALTH_CALIBRATED_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "core_health_calibrated_release" / "core_health_calibrated_release_readout.json"
CROSS_LISTENER_TRANSPORT_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "cross_listener_transport_decoder" / "cross_listener_transport_readout.json"
COUNTERFACTUAL_LISTENER_DROPOUT_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "counterfactual_listener_dropout_solver"
    / "counterfactual_listener_dropout_readout.json"
)
SPECTRAL_PUBLIC_TANGENT_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "spectral_public_tangent_solver"
    / "spectral_public_tangent_readout.json"
)
NEGATIVE_TANGENT_INVARIANT_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "negative_tangent_invariant_projection_solver"
    / "negative_tangent_invariant_projection_readout.json"
)
LB_CONDITIONED_RESPONSIBILITY_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "lb_conditioned_responsibility_solver"
    / "lb_conditioned_responsibility_readout.json"
)
MIXTURE_LISTENER_RESPONSIBILITY_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "mixture_listener_responsibility_solver"
    / "mixture_listener_responsibility_readout.json"
)
PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "public_private_subset_tomography_solver"
    / "public_private_subset_tomography_readout.json"
)
ANTI_LISTENER_TOXICITY_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "anti_listener_toxicity_equation_solver"
    / "anti_listener_toxicity_equation_readout.json"
)
FRONTIER_TRAJECTORY_SILENCE_JSON = (
    ROOT
    / "sleep_competition_adapter"
    / "outputs"
    / "frontier_trajectory_silence_solver"
    / "frontier_trajectory_silence_readout.json"
)
ACTION_DECODER_ABLATION_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "action_decoder_ablation_suite" / "hsjepa_action_decoder_ablation_suite.json"
CONTRASTIVE_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "listener_invariant_contrastive_probe.json"
PRIVATE_TOXICITY_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "private_safe_toxicity_probe.json"
HARDWORLD_TOXICITY_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hardworld_toxicity_factorization_probe.json"
FACTORIZED_DECODER_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout.json"
FACTORIZED_STRESS_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit.json"

PACKET_JSON = OUT / "hsjepa_paper_method_packet.json"
PACKET_MD = OUT / "hsjepa_paper_method_packet_ko.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(x: object, digits: int = 6) -> str:
    if x is None:
        return "n/a"
    try:
        return f"{float(x):.{digits}f}"
    except (TypeError, ValueError):
        return str(x)


def require_inputs() -> None:
    missing = [
        str(path.relative_to(ROOT))
        for path in [
            PACKAGE_JSON,
            STRESS_CSV,
            EVIDENCE_CSV,
            VALIDATION_JSON,
            CONTRACT_JSON,
            READINESS_JSON,
            GENERALITY_JSON,
            BOUNDARY_AUDIT_JSON,
            CORE_MANIFEST_JSON,
            CORE_ABLATION_JSON,
            CORE_REFERENCE_JSON,
            CORE_BENCHMARK_JSON,
            ADAPTER_REPORT_JSON,
            BIG_BET_JSON,
            OG_PROBE_JSON,
            ASSIGNMENT_GAP_JSON,
            ROW_SUPPORT_SENSOR_JSON,
            MASKED_ROW_SUPPORT_JSON,
            ROW_SUPPORT_DECODER_JSON,
            ROUTE_FRONTIER_DECODER_JSON,
            ROUTE_TOXICITY_FUSION_DECODER_JSON,
            DECODER_ORDER_JURY_JSON,
            DECODER_BOUNDARY_TOMOGRAPHY_JSON,
            CORE_MEDIATED_RELEASE_JSON,
            CORE_RELEASE_ABLATION_JSON,
            CORE_HEALTH_CALIBRATED_JSON,
            CROSS_LISTENER_TRANSPORT_JSON,
            COUNTERFACTUAL_LISTENER_DROPOUT_JSON,
            SPECTRAL_PUBLIC_TANGENT_JSON,
            NEGATIVE_TANGENT_INVARIANT_JSON,
            LB_CONDITIONED_RESPONSIBILITY_JSON,
            MIXTURE_LISTENER_RESPONSIBILITY_JSON,
            PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON,
            ANTI_LISTENER_TOXICITY_JSON,
            FRONTIER_TRAJECTORY_SILENCE_JSON,
            ACTION_DECODER_ABLATION_JSON,
            CONTRASTIVE_PROBE_JSON,
            PRIVATE_TOXICITY_PROBE_JSON,
            HARDWORLD_TOXICITY_PROBE_JSON,
            FACTORIZED_DECODER_JSON,
            FACTORIZED_STRESS_JSON,
        ]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing paper packet inputs: {missing}")


def build_packet() -> dict[str, object]:
    require_inputs()
    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    contract = read_json(CONTRACT_JSON)
    readiness = read_json(READINESS_JSON)
    generality = read_json(GENERALITY_JSON)
    boundary_audit = read_json(BOUNDARY_AUDIT_JSON)
    core = read_json(CORE_MANIFEST_JSON)
    core_ablation = read_json(CORE_ABLATION_JSON)
    core_reference = read_json(CORE_REFERENCE_JSON)
    core_benchmark = read_json(CORE_BENCHMARK_JSON)
    adapter = read_json(ADAPTER_REPORT_JSON)
    big_bets = read_json(BIG_BET_JSON)
    og_probe = read_json(OG_PROBE_JSON)
    assignment_gap = read_json(ASSIGNMENT_GAP_JSON)
    row_support_sensor = read_json(ROW_SUPPORT_SENSOR_JSON)
    masked_row_support = read_json(MASKED_ROW_SUPPORT_JSON)
    row_support_decoder = read_json(ROW_SUPPORT_DECODER_JSON)
    route_frontier_decoder = read_json(ROUTE_FRONTIER_DECODER_JSON)
    route_toxicity_fusion_decoder = read_json(ROUTE_TOXICITY_FUSION_DECODER_JSON)
    decoder_order_jury = read_json(DECODER_ORDER_JURY_JSON)
    decoder_boundary_tomography = read_json(DECODER_BOUNDARY_TOMOGRAPHY_JSON)
    core_mediated_release = read_json(CORE_MEDIATED_RELEASE_JSON)
    core_release_ablation = read_json(CORE_RELEASE_ABLATION_JSON)
    core_health_calibrated = read_json(CORE_HEALTH_CALIBRATED_JSON)
    cross_listener_transport = read_json(CROSS_LISTENER_TRANSPORT_JSON)
    counterfactual_listener_dropout = read_json(COUNTERFACTUAL_LISTENER_DROPOUT_JSON)
    spectral_public_tangent = read_json(SPECTRAL_PUBLIC_TANGENT_JSON)
    negative_tangent_invariant = read_json(NEGATIVE_TANGENT_INVARIANT_JSON)
    lb_conditioned_responsibility = read_json(LB_CONDITIONED_RESPONSIBILITY_JSON)
    mixture_listener_responsibility = read_json(MIXTURE_LISTENER_RESPONSIBILITY_JSON)
    public_private_subset_tomography = read_json(PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON)
    anti_listener_toxicity = read_json(ANTI_LISTENER_TOXICITY_JSON)
    frontier_trajectory_silence = read_json(FRONTIER_TRAJECTORY_SILENCE_JSON)
    action_decoder_ablation = read_json(ACTION_DECODER_ABLATION_JSON)
    contrastive_probe = read_json(CONTRASTIVE_PROBE_JSON)
    private_toxicity_probe = read_json(PRIVATE_TOXICITY_PROBE_JSON)
    hardworld_toxicity_probe = read_json(HARDWORLD_TOXICITY_PROBE_JSON)
    factorized_decoder = read_json(FACTORIZED_DECODER_JSON)
    factorized_stress = read_json(FACTORIZED_STRESS_JSON)
    stress = pd.read_csv(STRESS_CSV)
    evidence = pd.read_csv(EVIDENCE_CSV)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    primary = readiness["mechanism"]["primary"]
    s2 = readiness["mechanism"]["s2_listener"]
    boundary = contract["boundary"]
    og_verdict = og_probe["verdict"]
    gap_verdict = assignment_gap["verdict"]
    row_support_verdict = row_support_sensor["verdict"]
    masked_row_support_verdict = masked_row_support["verdict"]
    row_support_decoder_verdict = row_support_decoder["verdict"]
    route_frontier_verdict = route_frontier_decoder["verdict"]
    route_toxicity_fusion_verdict = route_toxicity_fusion_decoder["verdict"]
    decoder_order_jury_verdict = decoder_order_jury["verdict"]
    decoder_order_jury_sensor = decoder_order_jury_verdict["recommended_lb_sensor"]
    decoder_boundary_tomography_verdict = decoder_boundary_tomography["verdict"]
    decoder_boundary_tomography_sensor = decoder_boundary_tomography_verdict["recommended_lb_sensor"]
    core_mediated_verdict = core_mediated_release["verdict"]
    core_mediated_sensor = core_mediated_verdict["recommended_lb_sensor"]
    core_release_ablation_verdict = core_release_ablation["verdict"]
    core_release_lb_candidate = core_release_ablation_verdict["recommended_lb_candidate"]
    core_release_sensor = core_release_ablation_verdict["recommended_architecture_sensor"]
    core_health_calibrated_verdict = core_health_calibrated["verdict"]
    core_health_lb_candidate = core_health_calibrated_verdict["recommended_lb_candidate"]
    core_health_big_bet = core_health_calibrated_verdict["recommended_big_bet_sensor"]
    core_health_pressure = core_health_calibrated_verdict["recommended_pressure_sensor"]
    cross_listener_verdict = cross_listener_transport["verdict"]
    cross_listener_sensor = cross_listener_verdict["recommended_lb_sensor"]
    cross_listener_big_bet = cross_listener_verdict["recommended_big_bet"]
    listener_dropout_verdict = counterfactual_listener_dropout["verdict"]
    listener_dropout_information_sensor = listener_dropout_verdict["recommended_information_sensor"]
    listener_dropout_thesis_sensor = listener_dropout_verdict["recommended_thesis_sensor"]
    spectral_tangent_verdict = spectral_public_tangent["verdict"]
    spectral_information_sensor = spectral_tangent_verdict["recommended_information_sensor"]
    spectral_counter_sensor = spectral_tangent_verdict["recommended_counter_sensor"]
    negative_projection_verdict = negative_tangent_invariant["verdict"]
    negative_projection_recommended = negative_projection_verdict["recommended_variant"]
    negative_projection_item = negative_tangent_invariant["variants"][negative_projection_recommended]
    negative_projection_submission = negative_projection_item["submission"]
    lb_responsibility_verdict = lb_conditioned_responsibility["verdict"]
    lb_responsibility_recommended = lb_responsibility_verdict["recommended_variant"]
    lb_responsibility_item = lb_conditioned_responsibility["variants"][lb_responsibility_recommended]
    lb_responsibility_submission = lb_responsibility_item["submission"]
    mixture_listener_verdict = mixture_listener_responsibility["verdict"]
    mixture_listener_recommended = mixture_listener_verdict["recommended_variant"]
    mixture_listener_item = mixture_listener_responsibility["variants"][mixture_listener_recommended]
    mixture_listener_submission = mixture_listener_item["submission"]
    subset_tomography_verdict = public_private_subset_tomography["verdict"]
    subset_tomography_recommended = subset_tomography_verdict["recommended_variant"]
    subset_tomography_item = public_private_subset_tomography["variants"][subset_tomography_recommended]
    subset_tomography_submission = subset_tomography_item["submission"]
    anti_listener_verdict = anti_listener_toxicity["verdict"]
    anti_listener_recommended = anti_listener_verdict["recommended_variant"]
    anti_listener_item = anti_listener_toxicity["variants"][anti_listener_recommended]
    anti_listener_submission = anti_listener_item["submission"]
    frontier_silence_verdict = frontier_trajectory_silence["verdict"]
    frontier_silence_recommended = frontier_silence_verdict["recommended_variant"]
    frontier_silence_item = frontier_trajectory_silence["variants"][frontier_silence_recommended]
    frontier_silence_submission = frontier_silence_item["submission"]
    frontier_silence_changed_cells = frontier_silence_submission.get(
        "changed_cells",
        frontier_silence_submission.get("validation", {}).get("changed_cells_vs_current_best"),
    )
    action_ablation_verdict = action_decoder_ablation["verdict"]
    contrastive_verdict = contrastive_probe["verdict"]
    toxicity_verdict = private_toxicity_probe["verdict"]
    hardworld_verdict = hardworld_toxicity_probe["verdict"]
    factorized_variants = factorized_decoder.get("variants", {})
    factorized_stress_variants = factorized_stress.get("variants", {})
    factorized_supported = [
        name
        for name, item in factorized_stress_variants.items()
        if isinstance(item, dict) and item.get("verdict", {}).get("status") == "factorized_decoder_stress_supported"
    ]

    roles = []
    for row in evidence.to_dict("records"):
        roles.append(
            {
                "role": str(row["role"]),
                "component": str(row["component"]),
                "submission_file": str(row["submission_file"]),
                "changed_cells": int(row["submission_changed_cells_vs_current_best"]),
                "changed_rows": int(row["changed_rows"]),
                "claim": str(row["claim"]),
            }
        )

    packet = {
        "title": "Human-State JEPA: General Architecture with a Route-Conserving S2 Bridge Case Study",
        "short_name": "HS-JEPA General Architecture",
        "status": readiness["status"],
        "one_sentence": (
            "HS-JEPA Core is a human-understanding architecture that predicts hidden human-state, "
            "listener responsibility, action-health, and invariant-preserving action representations "
            "before producing bounded predictions; the Sleep Competition Adapter instantiates that core "
            "as a Route-Conserving S2 Bridge case study."
        ),
        "score_evidence": {
            "pre_public_equation_best_public_lb": public["pre_public_equation_best_public_lb"],
            "public_equation_breakthrough_public_lb": public["public_equation_breakthrough_public_lb"],
            "current_best_public_lb": public["current_best_public_lb"],
            "current_delta_vs_pre_public_equation": public["current_delta_vs_pre_breakthrough"],
            "current_best_role": public["current_best_role_name"],
            "current_best_file": public["current_best_file"],
        },
        "mechanism_evidence": {
            "primary_route_delta": primary["mean_route_energy_delta"],
            "primary_null_route_delta": primary["null_mean_route_energy_delta"],
            "primary_energy_rank_pct": primary["mean_energy_rank_pct"],
            "s2_usage": s2["s2_any_rate"],
            "s2_null_usage": s2["null_s2_any_rate"],
            "s2hub_rank_pct": s2["mean_s2hub_rank_pct"],
            "validation_passed": validation["passed"],
            "readiness_gates": f"{readiness['passed_gates']}/{readiness['total_gates']}",
        },
        "human_state_evidence": {
            "cell_oof_auc": human["cell_oof_auc_human_target_context"],
            "row_oof_auc": human["row_oof_auc"],
            "og_only_assignment_probe_status": og_verdict["status"],
            "pure_og_row_cap2_mean_recall": og_verdict["pure_og_row_cap2_mean_recall"],
            "distilled_row_cap2_mean_recall": og_verdict["distilled_row_cap2_mean_recall"],
            "assignment_gap_status": gap_verdict["status"],
            "assignment_gap_best_portable_recall": gap_verdict["mean_best_portable_recall"],
            "assignment_gap_row_oracle_stage_recall": gap_verdict["mean_row_oracle_stage_recall"],
            "assignment_gap_row_support_gap": gap_verdict["mean_row_support_gap"],
            "hidden_row_support_sensor_status": row_support_verdict["status"],
            "hidden_row_support_best_family": row_support_verdict["best_portable_family"],
            "hidden_row_support_mean_row_auc": row_support_verdict["best_portable_mean_row_auc"],
            "hidden_row_support_mean_row_recall_at_k": row_support_verdict["best_portable_mean_row_recall_at_k"],
            "hidden_row_support_mean_cell_recall": row_support_verdict["best_portable_mean_cell_recall_with_stage_prior"],
            "hidden_row_support_auc_z": row_support_verdict["best_portable_mean_auc_z_vs_permuted_train"],
            "masked_row_support_objective_status": masked_row_support_verdict["status"],
            "masked_row_support_full_row_auc": masked_row_support_verdict["full_composite_mean_row_auc"],
            "masked_row_support_full_cell_recall": masked_row_support_verdict["full_composite_mean_cell_recall"],
            "masked_row_support_human_cell_recall": masked_row_support_verdict["human_only_mean_cell_recall"],
            "masked_row_support_prediction_cell_recall": masked_row_support_verdict["prediction_only_mean_cell_recall"],
            "masked_row_support_route_mask_cell_recall": masked_row_support_verdict["route_mask_mean_cell_recall"],
            "masked_row_support_group_stress_auc": masked_row_support_verdict["group_stress_full_mean_auc"],
            "row_support_action_decoder_status": row_support_decoder_verdict["status"],
            "row_support_action_decoder_recommended": row_support_decoder_verdict["recommended_variant"],
            "row_support_action_decoder_changed_cells": row_support_decoder_verdict["exploratory_changed_cells"],
            "row_support_action_decoder_safety_z": row_support_decoder_verdict["exploratory_safety_z"],
            "row_support_action_decoder_combined_z": row_support_decoder_verdict["exploratory_combined_z"],
            "row_support_action_decoder_mean_route_gain": row_support_decoder_verdict["exploratory_mean_route_gain"],
            "route_frontier_action_decoder_status": route_frontier_verdict["status"],
            "route_frontier_action_decoder_recommended": route_frontier_verdict["recommended_variant"],
            "route_frontier_action_decoder_variant_scores": route_frontier_verdict["variant_scores"],
            "route_toxicity_fusion_decoder_status": route_toxicity_fusion_verdict["status"],
            "route_toxicity_fusion_decoder_recommended": route_toxicity_fusion_verdict["recommended_variant"],
            "route_toxicity_fusion_decoder_variant_scores": route_toxicity_fusion_verdict["variant_scores"],
            "decoder_order_jury_solver_status": decoder_order_jury_verdict["status"],
            "decoder_order_jury_solver_recommended": decoder_order_jury_sensor,
            "decoder_order_jury_solver_file": decoder_order_jury_sensor["submission_file"],
            "decoder_order_jury_solver_priority": decoder_order_jury_sensor["priority"],
            "decoder_boundary_tomography_status": decoder_boundary_tomography_verdict["status"],
            "decoder_boundary_tomography_recommended": decoder_boundary_tomography_sensor,
            "decoder_boundary_tomography_file": decoder_boundary_tomography_sensor["submission_file"],
            "decoder_boundary_tomography_priority": decoder_boundary_tomography_sensor["priority"],
            "decoder_boundary_tomography_inventory": decoder_boundary_tomography["boundary_inventory"],
            "core_mediated_action_release_status": core_mediated_verdict["status"],
            "core_mediated_action_release_recommended": core_mediated_sensor,
            "core_mediated_action_release_file": core_mediated_sensor["submission_file"],
            "core_mediated_action_release_priority": core_mediated_sensor["priority"],
            "core_mediated_action_release_inventory": core_mediated_release["cell_inventory"],
            "core_release_ablation_status": core_release_ablation_verdict["status"],
            "core_release_ablation_lb_candidate": core_release_lb_candidate,
            "core_release_ablation_lb_candidate_file": core_release_lb_candidate["submission_file"],
            "core_release_ablation_lb_candidate_priority": core_release_lb_candidate["priority"],
            "core_release_ablation_sensor": core_release_sensor,
            "core_release_ablation_sensor_file": core_release_sensor["submission_file"],
            "core_release_ablation_sensor_priority": core_release_sensor["priority"],
            "core_health_calibrated_status": core_health_calibrated_verdict["status"],
            "core_health_calibrated_lb_candidate": core_health_lb_candidate,
            "core_health_calibrated_lb_candidate_file": core_health_lb_candidate["submission_file"],
            "core_health_calibrated_lb_candidate_priority": core_health_lb_candidate["priority"],
            "core_health_calibrated_big_bet": core_health_big_bet,
            "core_health_calibrated_big_bet_file": core_health_big_bet["submission_file"],
            "core_health_calibrated_big_bet_priority": core_health_big_bet["priority"],
            "core_health_calibrated_pressure": core_health_pressure,
            "core_health_calibrated_pressure_file": core_health_pressure["submission_file"],
            "core_health_calibrated_pressure_priority": core_health_pressure["priority"],
            "core_health_calibrated_benchmark_calibration": core_health_calibrated["benchmark_calibration"],
            "cross_listener_transport_status": cross_listener_verdict["status"],
            "cross_listener_transport_recommended": cross_listener_sensor,
            "cross_listener_transport_file": cross_listener_sensor["submission_file"],
            "cross_listener_transport_priority": cross_listener_sensor["priority"],
            "cross_listener_transport_big_bet": cross_listener_big_bet,
            "cross_listener_transport_big_bet_file": cross_listener_big_bet["submission_file"],
            "cross_listener_transport_big_bet_priority": cross_listener_big_bet["priority"],
            "cross_listener_transport_negative_sensor": cross_listener_transport["negative_sensor"],
            "counterfactual_listener_dropout_status": counterfactual_listener_dropout["status"],
            "counterfactual_listener_dropout_information_sensor": listener_dropout_information_sensor,
            "counterfactual_listener_dropout_information_sensor_file": listener_dropout_information_sensor["submission_file"],
            "counterfactual_listener_dropout_information_sensor_priority": listener_dropout_information_sensor["priority"],
            "counterfactual_listener_dropout_thesis_sensor": listener_dropout_thesis_sensor,
            "counterfactual_listener_dropout_thesis_sensor_file": listener_dropout_thesis_sensor["submission_file"],
            "counterfactual_listener_dropout_thesis_sensor_priority": listener_dropout_thesis_sensor["priority"],
            "counterfactual_listener_dropout_top_ranked": counterfactual_listener_dropout.get("ranking", [])[:2],
            "spectral_public_tangent_status": spectral_public_tangent["status"],
            "spectral_public_tangent_first_mode_variance": spectral_public_tangent["spectral"]["first_mode_variance"],
            "spectral_public_tangent_top5_variance": spectral_public_tangent["spectral"]["top5_cumulative_variance"],
            "spectral_public_tangent_pool": spectral_public_tangent["pool"],
            "spectral_public_tangent_information_sensor": spectral_information_sensor,
            "spectral_public_tangent_information_sensor_file": spectral_information_sensor["submission_file"],
            "spectral_public_tangent_information_sensor_priority": spectral_information_sensor["priority"],
            "spectral_public_tangent_counter_sensor": spectral_counter_sensor,
            "spectral_public_tangent_counter_sensor_file": spectral_counter_sensor["submission_file"],
            "negative_tangent_invariant_status": negative_projection_verdict["status"],
            "negative_tangent_invariant_recommended": negative_projection_recommended,
            "negative_tangent_invariant_file": negative_projection_submission["submission_file"],
            "negative_tangent_invariant_projected_cells": negative_tangent_invariant["projected_cells"],
            "negative_tangent_invariant_bad_cosine": negative_projection_item["metrics"]["bad_tangent_cosine"],
            "negative_tangent_invariant_energy_delta": negative_projection_item["metrics"]["mean_incremental_energy_delta"],
            "negative_tangent_invariant_subject_delta": negative_projection_item["metrics"]["mean_subject_energy_delta"],
            "lb_conditioned_responsibility_status": lb_responsibility_verdict["status"],
            "lb_conditioned_responsibility_recommended": lb_responsibility_recommended,
            "lb_conditioned_responsibility_file": lb_responsibility_submission["submission_file"],
            "lb_conditioned_responsibility_anchor_count": lb_conditioned_responsibility["fit"]["anchor_count"],
            "lb_conditioned_responsibility_loo_corr": lb_conditioned_responsibility["fit"]["loo_corr"],
            "lb_conditioned_responsibility_cells": lb_conditioned_responsibility["responsibility_cells"],
            "lb_conditioned_responsibility_changed_cells": lb_responsibility_submission["changed_cells"],
            "lb_conditioned_responsibility_predicted_delta": lb_responsibility_item["metrics"]["sum_predicted_loss_delta"],
            "lb_conditioned_responsibility_energy_delta": lb_responsibility_item["metrics"]["mean_incremental_energy_delta"],
            "lb_conditioned_responsibility_bad_cosine": lb_responsibility_item["metrics"]["bad_tangent_cosine"],
            "mixture_listener_responsibility_status": mixture_listener_verdict["status"],
            "mixture_listener_responsibility_recommended": mixture_listener_recommended,
            "mixture_listener_responsibility_file": mixture_listener_submission["submission_file"],
            "mixture_listener_anchor_count": mixture_listener_responsibility["anchor_count"],
            "mixture_listener_cell_count": mixture_listener_responsibility["cell_count"],
            "mixture_listener_loo_corr": mixture_listener_responsibility["mixture_fit"]["loo_corr"],
            "mixture_listener_scalar_loo_corr": mixture_listener_responsibility["mixture_fit"]["scalar_fit"]["loo_corr"],
            "mixture_listener_changed_cells": mixture_listener_submission["changed_cells"],
            "mixture_listener_scalar_delta": mixture_listener_item["metrics"]["sum_predicted_scalar_delta"],
            "mixture_listener_mode_delta": mixture_listener_item["metrics"]["sum_predicted_total_mode_delta"],
            "mixture_listener_conflict_score": mixture_listener_item["metrics"]["mean_conflict_score"],
            "mixture_listener_bad_cosine": mixture_listener_item["metrics"]["bad_tangent_cosine"],
            "public_private_subset_tomography_status": subset_tomography_verdict["status"],
            "public_private_subset_tomography_recommended": subset_tomography_recommended,
            "public_private_subset_tomography_file": subset_tomography_submission["submission_file"],
            "public_private_subset_tomography_source_loo_corr": public_private_subset_tomography["source_fit"]["loo_corr"],
            "public_private_subset_tomography_cell_count": public_private_subset_tomography["cell_count"],
            "public_private_subset_tomography_changed_cells": subset_tomography_submission["changed_cells"],
            "public_private_subset_tomography_predicted_delta": subset_tomography_item["metrics"]["sum_predicted_public_delta"],
            "public_private_subset_tomography_mean_inclusion": subset_tomography_item["metrics"]["mean_public_inclusion"],
            "public_private_subset_tomography_mean_label_confidence": subset_tomography_item["metrics"]["mean_label_confidence"],
            "public_private_subset_tomography_private_safety": subset_tomography_item["metrics"]["mean_private_safety"],
            "public_private_subset_tomography_toxicity": subset_tomography_item["metrics"]["mean_toxicity"],
            "anti_listener_toxicity_status": anti_listener_verdict["status"],
            "anti_listener_toxicity_recommended": anti_listener_recommended,
            "anti_listener_toxicity_file": anti_listener_submission["submission_file"],
            "anti_listener_toxicity_source_loo_corr": anti_listener_toxicity["source_fit"]["loo_corr"],
            "anti_listener_toxicity_cell_count": anti_listener_toxicity["cell_count"],
            "anti_listener_toxicity_changed_cells": anti_listener_submission["changed_cells"],
            "anti_listener_toxicity_predicted_delta": anti_listener_item["metrics"]["sum_predicted_public_delta"],
            "anti_listener_toxicity_listener_inverse": anti_listener_item["metrics"]["mean_listener_inverse"],
            "anti_listener_toxicity_private_safety": anti_listener_item["metrics"]["mean_private_safety"],
            "anti_listener_toxicity_hardworld_toxicity": anti_listener_item["metrics"]["mean_hardworld_toxicity"],
            "anti_listener_toxicity_broad_toxicity": anti_listener_item["metrics"]["mean_broad_toxicity"],
            "frontier_trajectory_silence_status": frontier_silence_verdict["status"],
            "frontier_trajectory_silence_recommended": frontier_silence_recommended,
            "frontier_trajectory_silence_file": frontier_silence_submission["submission_file"],
            "frontier_trajectory_silence_cell_count": frontier_trajectory_silence["cell_count"],
            "frontier_trajectory_silence_changed_cells": frontier_silence_changed_cells,
            "frontier_trajectory_silence_first_bad_mode_variance": frontier_trajectory_silence["negative_tangent"]["first_mode_variance"],
            "frontier_trajectory_silence_frontier_cosine": frontier_silence_item["metrics"]["frontier_cosine"],
            "frontier_trajectory_silence_bad_tangent_cosine": frontier_silence_item["metrics"]["bad_tangent_cosine"],
            "frontier_trajectory_silence_mean_silence_pressure": frontier_silence_item["metrics"]["mean_silence_pressure"],
            "action_decoder_ablation_status": action_ablation_verdict["status"],
            "action_decoder_ablation_recommended_lb_sensor": action_ablation_verdict["recommended_lb_sensor"],
            "action_decoder_ablation_big_bet_sensor": action_ablation_verdict["big_bet_sensor"],
            "listener_invariant_probe_status": contrastive_verdict["status"],
            "listener_route_spearman": contrastive_verdict["mean_listener_route_spearman"],
            "contrastive_overlap_rate": contrastive_verdict["mean_contrastive_overlap_rate"],
            "private_safe_toxicity_probe_status": toxicity_verdict["status"],
            "toxicity_mean_loo_auc": toxicity_verdict["mean_loo_bad_anchor_auc"],
            "toxicity_worst_loo_auc": toxicity_verdict["worst_loo_bad_anchor_auc"],
            "toxicity_selected_safety_z": toxicity_verdict["selected_safety_z_vs_matched_null"],
            "hardworld_factorization_probe_status": hardworld_verdict["status"],
            "hardworld_broad_to_h088_auc": hardworld_verdict["broad_predicts_hardworld_auc"],
            "hardworld_broad_h088_spearman": hardworld_verdict["broad_hardworld_spearman"],
            "hardworld_joint_safety_z": hardworld_verdict["selected_joint_safety_z"],
            "factorized_decoder_variant_count": len(factorized_variants),
            "factorized_decoder_upload_safe_count": sum(
                1
                for item in factorized_variants.values()
                if isinstance(item, dict) and item.get("validation", {}).get("upload_safe")
            ),
            "factorized_decoder_stress_status": factorized_stress.get("status"),
            "factorized_decoder_stress_supported_variants": factorized_supported,
            "role": "orientation diagnostic, not complete row-target assignment solver",
        },
        "roles": roles,
        "boundary": boundary,
        "core": {
            "status": core["status"],
            "claim": core["claim"],
            "core_equation": core["core_equation"],
            "passed_gates": core["passed_gates"],
            "total_gates": core["total_gates"],
            "ablation_status": core_ablation["status"],
            "ablation_count": len(core_ablation["ablations"]),
            "reference_status": core_reference["status"],
            "reference_released_actions": core_reference["full_core"]["summary"]["released_actions"],
            "reference_ablation_count": len(core_reference["ablations"]),
            "module_benchmark_status": core_benchmark["status"],
            "module_benchmark_scenario_count": core_benchmark["scenario_count"],
            "module_benchmark_full_core_f1": core_benchmark["verdict"]["full_core_mean_f1"],
            "module_benchmark_action_health_fp_lift": core_benchmark["verdict"]["remove_action_health_false_positive_lift"],
            "module_benchmark_invariant_fp_lift": core_benchmark["verdict"]["remove_invariant_false_positive_lift"],
        },
        "boundary_audit": {
            "status": boundary_audit["status"],
            "passed_checks": boundary_audit["passed_checks"],
            "total_checks": boundary_audit["total_checks"],
            "core_import_violations": len(boundary_audit.get("core_import_violations", [])),
            "core_string_violations": len(boundary_audit.get("core_string_violations", [])),
            "boundary_claim": boundary_audit.get("boundary_claim"),
        },
        "adapter": {
            "status": adapter["status"],
            "claim": adapter["adapter_claim"],
            "mapping_count": len(adapter["adapter_mapping"]),
            "big_bet_status": big_bets["status"],
            "big_bet_count": big_bets["count"],
        },
        "generality": {
            "status": generality["status"],
            "passed_checks": generality["passed_checks"],
            "total_checks": generality["total_checks"],
            "nonblocking_boundaries": generality["nonblocking_boundaries"],
            "honest_claim": generality["honest_claim"],
            "next_breakthrough": generality["next_breakthrough"],
        },
        "outputs": {
            "method_packet_md": str(PACKET_MD.resolve()),
            "method_packet_json": str(PACKET_JSON.resolve()),
            "readiness_report": str(READINESS_JSON.resolve()),
            "reproducibility_contract": str(CONTRACT_JSON.resolve()),
            "core_manifest": str(CORE_MANIFEST_JSON.resolve()),
            "core_ablation_contract": str(CORE_ABLATION_JSON.resolve()),
            "core_reference_run": str(CORE_REFERENCE_JSON.resolve()),
            "core_module_benchmark": str(CORE_BENCHMARK_JSON.resolve()),
            "core_adapter_boundary_audit": str(BOUNDARY_AUDIT_JSON.resolve()),
            "sleep_adapter_report": str(ADAPTER_REPORT_JSON.resolve()),
            "big_bet_queue": str(BIG_BET_JSON.resolve()),
            "og_only_assignment_teacher_probe": str(OG_PROBE_JSON.resolve()),
            "assignment_gap_decomposition_probe": str(ASSIGNMENT_GAP_JSON.resolve()),
            "hidden_row_support_sensor_probe": str(ROW_SUPPORT_SENSOR_JSON.resolve()),
            "masked_row_support_objective_probe": str(MASKED_ROW_SUPPORT_JSON.resolve()),
            "row_support_strict_action_decoder": str(ROW_SUPPORT_DECODER_JSON.resolve()),
            "route_frontier_action_decoder": str(ROUTE_FRONTIER_DECODER_JSON.resolve()),
            "route_toxicity_fusion_decoder": str(ROUTE_TOXICITY_FUSION_DECODER_JSON.resolve()),
            "decoder_order_jury_solver": str(DECODER_ORDER_JURY_JSON.resolve()),
            "decoder_boundary_tomography_solver": str(DECODER_BOUNDARY_TOMOGRAPHY_JSON.resolve()),
            "core_mediated_action_release": str(CORE_MEDIATED_RELEASE_JSON.resolve()),
            "core_release_ablation_probe": str(CORE_RELEASE_ABLATION_JSON.resolve()),
            "core_health_calibrated_release": str(CORE_HEALTH_CALIBRATED_JSON.resolve()),
            "cross_listener_transport_decoder": str(CROSS_LISTENER_TRANSPORT_JSON.resolve()),
            "counterfactual_listener_dropout_solver": str(COUNTERFACTUAL_LISTENER_DROPOUT_JSON.resolve()),
            "spectral_public_tangent_solver": str(SPECTRAL_PUBLIC_TANGENT_JSON.resolve()),
            "negative_tangent_invariant_projection_solver": str(NEGATIVE_TANGENT_INVARIANT_JSON.resolve()),
            "lb_conditioned_responsibility_solver": str(LB_CONDITIONED_RESPONSIBILITY_JSON.resolve()),
            "mixture_listener_responsibility_solver": str(MIXTURE_LISTENER_RESPONSIBILITY_JSON.resolve()),
            "public_private_subset_tomography_solver": str(PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON.resolve()),
            "anti_listener_toxicity_equation_solver": str(ANTI_LISTENER_TOXICITY_JSON.resolve()),
            "frontier_trajectory_silence_solver": str(FRONTIER_TRAJECTORY_SILENCE_JSON.resolve()),
            "action_decoder_ablation_suite": str(ACTION_DECODER_ABLATION_JSON.resolve()),
            "listener_invariant_contrastive_probe": str(CONTRASTIVE_PROBE_JSON.resolve()),
            "private_safe_toxicity_probe": str(PRIVATE_TOXICITY_PROBE_JSON.resolve()),
            "hardworld_toxicity_factorization_probe": str(HARDWORLD_TOXICITY_PROBE_JSON.resolve()),
            "factorized_toxicity_decoder": str(FACTORIZED_DECODER_JSON.resolve()),
            "factorized_toxicity_decoder_stress_audit": str(FACTORIZED_STRESS_JSON.resolve()),
            "one_command": "python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py",
        },
        "paper_sections": {
            "abstract_ko": build_abstract(public, primary, s2, human),
            "method_ko": build_method_text(core, adapter),
            "generality_ko": build_generality_text(
                generality,
                og_verdict,
                gap_verdict,
                row_support_verdict,
                masked_row_support_verdict,
                row_support_decoder_verdict,
                route_frontier_verdict,
                route_toxicity_fusion_verdict,
                decoder_order_jury_verdict,
                decoder_boundary_tomography_verdict,
                decoder_boundary_tomography,
                core_mediated_verdict,
                core_mediated_release,
                core_release_ablation_verdict,
                core_health_calibrated_verdict,
                cross_listener_verdict,
                cross_listener_transport,
                listener_dropout_verdict,
                counterfactual_listener_dropout,
                spectral_tangent_verdict,
                spectral_public_tangent,
                lb_responsibility_verdict,
                lb_conditioned_responsibility,
                subset_tomography_verdict,
                public_private_subset_tomography,
                anti_listener_verdict,
                anti_listener_toxicity,
                frontier_silence_verdict,
                frontier_trajectory_silence,
                contrastive_verdict,
                toxicity_verdict,
                hardworld_verdict,
            ),
            "algorithm_ko": build_algorithm_text(),
            "limitations_ko": build_limitations_text(boundary),
            "big_bets_ko": build_big_bet_text(big_bets),
        },
    }
    PACKET_JSON.write_text(json.dumps(packet, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    PACKET_MD.write_text(build_markdown(packet, stress), encoding="utf-8")
    print(json.dumps(packet, indent=2, ensure_ascii=False, allow_nan=False))
    return packet


def build_abstract(
    public: dict[str, object],
    primary: dict[str, object],
    s2: dict[str, object],
    human: dict[str, object],
) -> str:
    return (
        "우리는 인간 생활 로그 예측을 label column에 대한 직접 분류 문제가 아니라, "
        "숨은 인간 생활 상태가 여러 listener와 action으로 드러나는 representation prediction 문제로 재정의한다. "
        "제안하는 HS-JEPA는 raw label을 직접 복원하지 않고 human-state, listener responsibility, "
        "action-health, invariant energy를 분리한다. 수면 로그 대회 case study에서는 이 일반 구조가 "
        "sparse row-target action decoding으로 구현되며, objective sleep-stage target에서는 "
        "public-sensitive driver action을 단독으로 적용하지 않고 train label에서 학습한 Q/S route "
        "manifold를 보존하는 bridge action을 함께 선택한다. 실험적으로 이 case-study decoder는 "
        "기존 public-equation 이전 최고 public LB "
        f"{fmt(public['pre_public_equation_best_public_lb'], 10)}에서 현재 최고 "
        f"{fmt(public['current_best_public_lb'], 10)}까지 {fmt(public['current_delta_vs_pre_breakthrough'], 10)} "
        "개선된 signal을 설명하며, 선택된 bridge는 random feasible bundle 대비 route energy를 "
        f"{fmt(primary['mean_route_energy_delta'], 5)} vs {fmt(primary['null_mean_route_energy_delta'], 5)}로 "
        "낮춘다. 또한 S2는 listener/hub로 반복 등장한다 "
        f"({fmt(s2['s2_any_rate'], 3)} vs null {fmt(s2['null_s2_any_rate'], 3)}). "
        f"Human-state latent는 cell-level orientation AUC {fmt(human['cell_oof_auc_human_target_context'], 3)}를 "
        f"보이지만 row assignment AUC는 {fmt(human['row_oof_auc'], 3)}에 그쳐, encoder와 assignment decoder를 "
        "분리해야 함을 보여준다."
    )


def build_method_text(core: dict[str, object], adapter: dict[str, object]) -> str:
    return "\n".join(
        [
            "HS-JEPA는 core와 adapter를 분리한다.",
            "",
            "Core equation:",
            "",
            "```text",
            str(core["core_equation"]),
            "```",
            "",
            "Core modules:",
            "",
            *[f"{idx}. {item['name']}: {item['purpose']}" for idx, item in enumerate(core["modules"], start=1)],
            "",
            "Sleep competition adapter:",
            "",
            adapter["adapter_claim"],
            "",
            "이번 수면 대회에서는 listener가 Q1/Q2/Q3/S1/S2/S3/S4로, invariant가 Q/S route energy로, action-health가 public/private toxicity 및 feasible-bundle stress로 구현되었다. 새 hard-world probe는 broad toxicity와 H088 toxicity가 역상관될 수 있음을 보여주므로, action-health는 단일 위험 점수가 아니라 factorized energy head로 다루어야 한다. 이후 core-health calibrated release는 dataset-free core benchmark에서 action-health를 제거했을 때 false positive가 늘어난다는 실패 패턴을 실제 adapter release prior로 사용한다. cross-listener transport는 target-listener lift가 direct action generator로는 실패했다는 negative sensor를 보존하고, listener posterior를 route/fusion/core-safe action의 transport calibrator로만 사용한다. counterfactual listener-dropout은 listener 하나를 가려도 같은 row-target action이 살아남는지 묻고, 실패한 public sensor들을 버리는 대신 action-toxicity label로 사용한다. spectral public-tangent solver는 실패한 public action들을 저차원 negative representation으로 압축한 뒤 anti-tangent와 orthogonal residual release를 비교한다. negative tangent invariant projection은 여기서 한 단계 더 나아가, 그 반대 방향 action을 target-route/subject-prior invariant 위로 투영해야만 action-grade가 된다는 주장을 테스트한다. LB-conditioned responsibility solver는 public LB라는 scalar 외부 listener가 흘린 관측값에서 row-target action responsibility를 역추정한다. public/private subset tomography는 scalar feedback을 한 번 더 분해해 `public subset inclusion × hidden label direction`으로 해석하고, private-safety/toxicity head가 그 action을 외부 listener 밖에서도 보존할 수 있는지 묻는다. anti-listener toxicity equation은 여기서 다시 한 단계 나아가, public에서 실패한 listener-derived action을 negative teacher로 보며 그 반대 방향도 private-safety와 hard-world/broad toxicity veto를 통과할 때만 release한다. frontier-trajectory active-silence는 H012→H057의 성공 trajectory를 positive representation으로, 이후 실패 trajectory를 silence/action-health representation으로 두어 `계속 밀 action`과 `침묵시킬 action`을 동시에 예측한다. 핵심은 `S2` 자체가 아니라, hidden state를 직접 label로 쓰지 않고 core의 listener/action/invariant/anti-shortcut/negative-representation/responsibility/subset-tomography/anti-listener/active-silence 경로를 adapter가 안전한 sparse row-target action으로 번역한다는 점이다.",
        ]
    )


def build_generality_text(
    generality: dict[str, object],
    og_verdict: dict[str, object],
    gap_verdict: dict[str, object],
    row_support_verdict: dict[str, object],
    masked_row_support_verdict: dict[str, object],
    row_support_decoder_verdict: dict[str, object],
    route_frontier_verdict: dict[str, object],
    route_toxicity_fusion_verdict: dict[str, object],
    decoder_order_jury_verdict: dict[str, object],
    decoder_boundary_tomography_verdict: dict[str, object],
    decoder_boundary_tomography: dict[str, object],
    core_mediated_verdict: dict[str, object],
    core_mediated_release: dict[str, object],
    core_release_ablation_verdict: dict[str, object],
    core_health_calibrated_verdict: dict[str, object],
    cross_listener_verdict: dict[str, object],
    cross_listener_transport: dict[str, object],
    listener_dropout_verdict: dict[str, object],
    counterfactual_listener_dropout: dict[str, object],
    spectral_tangent_verdict: dict[str, object],
    spectral_public_tangent: dict[str, object],
    lb_responsibility_verdict: dict[str, object],
    lb_conditioned_responsibility: dict[str, object],
    subset_tomography_verdict: dict[str, object],
    public_private_subset_tomography: dict[str, object],
    anti_listener_verdict: dict[str, object],
    anti_listener_toxicity: dict[str, object],
    frontier_silence_verdict: dict[str, object],
    frontier_trajectory_silence: dict[str, object],
    contrastive_verdict: dict[str, object],
    toxicity_verdict: dict[str, object],
    hardworld_verdict: dict[str, object],
) -> str:
    rows = [
        "HS-JEPA general architecture != Route-Conserving S2 Bridge competition case study",
        "",
        "일반 HS-JEPA에서 재사용되는 것은 다음 구조다.",
        "",
        "```text",
        "partial human context",
        "  -> hidden human-state representation",
        "  -> listener responsibility",
        "  -> action-health decision",
        "  -> invariant-preserving decoder",
        "  -> anti-shortcut validation",
        "```",
        "",
        "이번 대회의 S2/public-sensor 구조는 이 일반 구조의 case study다.",
        "",
        f"- Generality status: `{generality['status']}`",
        f"- Portability checks: `{generality['passed_checks']}/{generality['total_checks']}`",
        f"- Nonblocking boundaries: `{', '.join(generality['nonblocking_boundaries'])}`",
        f"- OG-only assignment probe: `{og_verdict['status']}`",
        f"- Pure OG row-cap2 recall: `{fmt(og_verdict['pure_og_row_cap2_mean_recall'], 4)}`",
        f"- Distilled row-cap2 recall: `{fmt(og_verdict['distilled_row_cap2_mean_recall'], 4)}`",
        f"- Assignment gap decomposition: `{gap_verdict['status']}`",
        f"- Best portable recall: `{fmt(gap_verdict['mean_best_portable_recall'], 4)}`",
        f"- Row oracle + stage prior recall: `{fmt(gap_verdict['mean_row_oracle_stage_recall'], 4)}`",
        f"- Row-support gap: `{fmt(gap_verdict['mean_row_support_gap'], 4)}`",
        f"- Hidden row-support transfer: `{row_support_verdict['status']}`",
        f"- Best row-support family: `{row_support_verdict['best_portable_family']}`",
        f"- Row-support row AUC: `{fmt(row_support_verdict['best_portable_mean_row_auc'], 4)}`",
        f"- Row-support cell recall: `{fmt(row_support_verdict['best_portable_mean_cell_recall_with_stage_prior'], 4)}`",
        f"- Row-support AUC z: `{fmt(row_support_verdict['best_portable_mean_auc_z_vs_permuted_train'], 4)}`",
        f"- Masked row-support objective: `{masked_row_support_verdict['status']}`",
        f"- Masked full row AUC: `{fmt(masked_row_support_verdict['full_composite_mean_row_auc'], 4)}`",
        f"- Masked full cell recall: `{fmt(masked_row_support_verdict['full_composite_mean_cell_recall'], 4)}`",
        f"- Masked human-only cell recall: `{fmt(masked_row_support_verdict['human_only_mean_cell_recall'], 4)}`",
        f"- Masked group stress AUC: `{fmt(masked_row_support_verdict['group_stress_full_mean_auc'], 4)}`",
        f"- Row-support strict action decoder: `{row_support_decoder_verdict['status']}`",
        f"- Recommended action variant: `{row_support_decoder_verdict['recommended_variant']}`",
        f"- Decoder changed cells: `{row_support_decoder_verdict['exploratory_changed_cells']}`",
        f"- Decoder safety z / combined z: `{fmt(row_support_decoder_verdict['exploratory_safety_z'], 4)}` / `{fmt(row_support_decoder_verdict['exploratory_combined_z'], 4)}`",
        f"- Decoder mean route gain: `{fmt(row_support_decoder_verdict['exploratory_mean_route_gain'], 5)}`",
        f"- Route-frontier action decoder: `{route_frontier_verdict['status']}`",
        f"- Route-frontier recommended variant: `{route_frontier_verdict['recommended_variant']}`",
        f"- Route-frontier variant scores: `{route_frontier_verdict['variant_scores']}`",
        f"- Route-toxicity fusion decoder: `{route_toxicity_fusion_verdict['status']}`",
        f"- Route-toxicity fusion recommended variant: `{route_toxicity_fusion_verdict['recommended_variant']}`",
        f"- Route-toxicity fusion variant scores: `{route_toxicity_fusion_verdict['variant_scores']}`",
        f"- Decoder-order jury solver: `{decoder_order_jury_verdict['status']}`",
        f"- Decoder-order jury recommended LB sensor: `{decoder_order_jury_verdict['recommended_lb_sensor']}`",
        f"- Decoder boundary tomography: `{decoder_boundary_tomography_verdict['status']}`",
        f"- Boundary tomography recommended LB sensor: `{decoder_boundary_tomography_verdict['recommended_lb_sensor']}`",
        f"- Boundary inventory: `{decoder_boundary_tomography.get('boundary_inventory')}`",
        f"- Core-mediated action release: `{core_mediated_verdict['status']}`",
        f"- Core-mediated recommended LB sensor: `{core_mediated_verdict['recommended_lb_sensor']}`",
        f"- Core-mediated inventory: `{core_mediated_release.get('cell_inventory')}`",
        f"- Core release ablation: `{core_release_ablation_verdict['status']}`",
        f"- Core release full-core LB candidate: `{core_release_ablation_verdict['recommended_lb_candidate']}`",
        f"- Core release architecture sensor: `{core_release_ablation_verdict['recommended_architecture_sensor']}`",
        f"- Core-health calibrated release: `{core_health_calibrated_verdict['status']}`",
        f"- Core-health guarded LB candidate: `{core_health_calibrated_verdict['recommended_lb_candidate']}`",
        f"- Core-health big-bet sensor: `{core_health_calibrated_verdict['recommended_big_bet_sensor']}`",
        f"- Core-health pressure sensor: `{core_health_calibrated_verdict['recommended_pressure_sensor']}`",
        f"- Cross-listener transport: `{cross_listener_verdict['status']}`",
        f"- Cross-listener recommended LB sensor: `{cross_listener_verdict['recommended_lb_sensor']}`",
        f"- Cross-listener negative sensor: `{cross_listener_transport.get('negative_sensor')}`",
        f"- Counterfactual listener-dropout: `{counterfactual_listener_dropout['status']}`",
        f"- Listener-dropout information sensor: `{listener_dropout_verdict['recommended_information_sensor']}`",
        f"- Listener-dropout thesis sensor: `{listener_dropout_verdict['recommended_thesis_sensor']}`",
        f"- Spectral public-tangent solver: `{spectral_public_tangent['status']}`",
        f"- Spectral first bad-mode variance: `{fmt(spectral_public_tangent['spectral']['first_mode_variance'], 4)}`",
        f"- Spectral top-5 variance: `{fmt(spectral_public_tangent['spectral']['top5_cumulative_variance'], 4)}`",
        f"- Spectral information sensor: `{spectral_tangent_verdict['recommended_information_sensor']}`",
        f"- Spectral counter sensor: `{spectral_tangent_verdict['recommended_counter_sensor']}`",
        f"- LB-conditioned responsibility solver: `{lb_responsibility_verdict['status']}`",
        f"- LB responsibility recommended variant: `{lb_responsibility_verdict['recommended_variant']}`",
        f"- LB responsibility LOO corr: `{fmt(lb_conditioned_responsibility['fit']['loo_corr'], 4)}`",
        f"- LB responsibility cells: `{lb_conditioned_responsibility['responsibility_cells']}`",
        f"- Public/private subset tomography: `{subset_tomography_verdict['status']}`",
        f"- Subset tomography recommended variant: `{subset_tomography_verdict['recommended_variant']}`",
        f"- Subset tomography source LOO corr: `{fmt(public_private_subset_tomography['source_fit']['loo_corr'], 4)}`",
        f"- Subset tomography cells: `{public_private_subset_tomography['cell_count']}`",
        f"- Anti-listener toxicity equation: `{anti_listener_verdict['status']}`",
        f"- Anti-listener recommended variant: `{anti_listener_verdict['recommended_variant']}`",
        f"- Anti-listener source LOO corr: `{fmt(anti_listener_toxicity['source_fit']['loo_corr'], 4)}`",
        f"- Anti-listener candidate cells: `{anti_listener_toxicity['cell_count']}`",
        f"- Frontier active-silence solver: `{frontier_silence_verdict['status']}`",
        f"- Frontier active-silence recommended variant: `{frontier_silence_verdict['recommended_variant']}`",
        f"- Frontier bad first-mode variance: `{fmt(frontier_trajectory_silence['negative_tangent']['first_mode_variance'], 4)}`",
        f"- Frontier active-silence cells: `{frontier_trajectory_silence['cell_count']}`",
        f"- Listener-invariant probe: `{contrastive_verdict['status']}`",
        f"- Listener-route Spearman: `{fmt(contrastive_verdict['mean_listener_route_spearman'], 4)}`",
        f"- Private-safe toxicity probe: `{toxicity_verdict['status']}`",
        f"- Toxicity mean LOO AUC: `{fmt(toxicity_verdict['mean_loo_bad_anchor_auc'], 4)}`",
        f"- Toxicity worst LOO AUC: `{fmt(toxicity_verdict['worst_loo_bad_anchor_auc'], 4)}`",
        f"- Hard-world factorization probe: `{hardworld_verdict['status']}`",
        f"- Broad toxicity -> H088 AUC: `{fmt(hardworld_verdict['broad_predicts_hardworld_auc'], 4)}`",
        f"- Broad/H088 Spearman: `{fmt(hardworld_verdict['broad_hardworld_spearman'], 4)}`",
        "",
        "가장 중요한 남은 과제는 target route가 아니라 hidden row-support sensor를 안전한 row-target action으로 번역하는 것이다. 이제 row-support는 완전히 죽은 가설이 아니라 teacher-transfer와 masked-family objective에서 부분적으로 살아있는 가설로 바뀌었다. 특히 seven-target prediction landscape와 human/cohort context를 합친 portable composite가 row-support를 상당 부분 복원하고, human-only/prediction-only/masked-route view도 신호를 유지한다. 첫 strict action decoder는 null 대비 safety는 강하지만 route-gain 우위가 약했다. 새 route-frontier decoder는 반대로 route manifold frontier를 먼저 고르고 support/toxicity를 통과시키며, local broad/matched null은 이겼다. route-toxicity fusion decoder는 여기서 한 단계 더 나아가 route-first와 factorized action-health를 조합한다. decoder-order jury solver는 이 둘이 같은 row-target과 방향에 합의할 때만 action을 방출한다. boundary tomography는 그 strict jury가 너무 보수적인지 보기 위해 rejected cells를 weak-consensus, route-only, fusion-only로 쪼갠다. core-mediated release는 이 후보들을 다시 HS-JEPA Core의 context/listener/action-health/invariant 인터페이스로 통과시켜, core 자체가 action-grade release equation이 될 수 있는지 시험한다. core release ablation은 같은 cell에서 listener/action-health/invariant를 하나씩 제거해 module이 실제 release boundary를 바꾸는지 확인한다. core-health calibrated release는 dataset-free core benchmark에서 관측된 action-health false-positive lift를 adapter release prior로 사용해, generic core test가 실제 competition action boundary를 조절하는지 묻는다. cross-listener transport는 실패한 direct listener action을 버리지 않고, listener posterior를 route/fusion/core-safe action의 운송 보정자로만 써서 listener responsibility의 더 일반적인 역할을 시험한다. counterfactual listener-dropout은 어떤 listener를 빼도 살아남는 action과 실패한 public sensor에 공선적인 action을 분리한다. spectral public-tangent solver는 여기서 한 단계 더 나아가, 실패한 public action들을 하나의 negative representation space로 모으고 그 반대/직교 방향이 release 가능한 action equation인지 묻는다. negative tangent invariant projection은 그 질문을 더 강하게 바꿔, 반대 방향 action도 target-route/subject-prior invariant를 통과하지 못하면 release하지 않는다. 다만 이것들도 아직 sleep adapter의 LB sensor이지 private-safe release claim은 아니다.",
    ]
    return "\n".join(rows)


def build_algorithm_text() -> str:
    return "\n".join(
        [
            "Algorithm: HS-JEPA General Pattern with Sleep-Log Case Decoder",
            "",
            "Input: human lifestyle/context logs, listener labels or sensor outcomes, optional deployment sensor, current prediction.",
            "Output: bounded prediction/action field with invariant and shortcut checks.",
            "",
            "1. Encode personal, cohort, time, routine, social, and sensor context into a human-state representation.",
            "2. Predict masked listener/action representations from partial human context.",
            "2a. Treat row-support as a hidden target representation and stress it under masked human/prediction/route views.",
            "3. Estimate listener responsibility: which outcomes should react to the hidden state.",
            "4. Estimate action-health: whether the latent signal is safe to translate into output movement.",
            "5. Factorize action-health when shortcut modes are anti-correlated rather than scalar.",
            "6. Translate row-support through a strict route-support action gate before changing outputs.",
            "7. Prefer route-frontier actions when support-first decoding fails route/null stress.",
            "8. Learn an invariant energy over valid output/action manifolds.",
            "9. Release actions through a cross-decoder jury when route-first and action-health-first decoders agree.",
            "10. Run boundary tomography on rejected cells to test whether the release rule is too conservative.",
            "11. Calibrate adapter release with dataset-free core benchmark failure modes.",
            "12. Use cross-listener posterior as a transport calibrator only after route/fusion/core action support exists.",
            "13. Drop one listener view at a time and keep only actions whose health survives listener masking.",
            "14. Treat failed public sensors as toxicity evidence and test same-direction release against direction inversion.",
            "15. Decompose failed action fields into a spectral negative representation and test anti-tangent versus orthogonal residual release.",
            "16. Project negative-representation actions onto target-route and subject-prior invariants before release.",
            "17. Estimate scalar-listener responsibility from external outcome observations when explicit row-target labels are unavailable.",
            "18. Factor scalar feedback into public subset inclusion and hidden label direction when the external listener is only partially observed.",
            "19. Treat failed listener-derived actions as negative teachers and release inverse moves only after private-safety and toxicity veto.",
            "20. Learn an active-silence field from frontier trajectories: continue positive paths and veto toxic branches.",
            "21. Decode bounded actions that improve listener fit while preserving the invariant.",
            "22. Reject shortcuts with cohort/time/group/null stress tests.",
            "23. In the sleep-log case study, instantiate the invariant as Q/S route energy and the decoder as the S2 bridge.",
        ]
    )


def build_big_bet_text(big_bets: dict[str, object]) -> str:
    rows = []
    for bet in big_bets["bets"]:
        rows.append(
            f"- `{bet['name']}`: {bet['worldview']} Expected LB delta if true `{bet['expected_public_lb_delta_if_true']}`. Kill: {bet['kill_criterion']}"
        )
    return "\n".join(
        [
            "다음 큰 실험은 HS-JEPA core/adaptor 경계를 바꾸는 실험이어야 한다.",
            "",
            *rows,
        ]
    )


def build_limitations_text(boundary: dict[str, object]) -> str:
    return "\n".join(
        [
            "현재 패키지는 다음 경계를 명시한다.",
            "",
            f"- Pure OG-only model: `{boundary['is_pure_og_only_model']}`",
            f"- Uses public LB sensor: `{boundary['uses_public_lb_sensor']}`",
            f"- Uses proprietary embedding API in team runner: `{boundary['uses_proprietary_embedding_api_in_team_runner']}`",
            f"- Human-state role: `{boundary['human_state_role']}`",
            f"- Competition decoder role: `{boundary['competition_decoder_role']}`",
            "",
            "따라서 논문에서는 HS-JEPA의 representation idea와 competition-specific action decoder를 분리해서 주장해야 한다.",
        ]
    )


def build_markdown(packet: dict[str, object], stress: pd.DataFrame) -> str:
    score = packet["score_evidence"]
    mechanism = packet["mechanism_evidence"]
    human = packet["human_state_evidence"]

    role_rows = ["| Role | Component | Changed cells | Changed rows | Claim |", "| --- | --- | ---: | ---: | --- |"]
    for role in packet["roles"]:
        role_rows.append(
            f"| `{role['role']}` | {role['component']} | `{role['changed_cells']}` | "
            f"`{role['changed_rows']}` | {role['claim']} |"
        )

    stress_rows = ["| Candidate | Route delta | Null route delta | S2 usage | Null S2 usage |", "| --- | ---: | ---: | ---: | ---: |"]
    for row in stress.to_dict("records"):
        stress_rows.append(
            f"| `{row['name']}` | `{fmt(row['mean_route_energy_delta'], 5)}` | "
            f"`{fmt(row['null_mean_route_energy_delta'], 5)}` | `{fmt(row['s2_any_rate'], 3)}` | "
            f"`{fmt(row['null_s2_any_rate'], 3)}` |"
        )

    return "\n".join(
        [
            "# HS-JEPA Paper Method Packet",
            "",
            "이 문서는 팀원이 과거 제출 버전명을 몰라도 HS-JEPA를 논문/발표 아이디어로 설명할 수 있도록 만든 method packet이다.",
            "",
            "## One-Sentence Contribution",
            "",
            str(packet["one_sentence"]),
            "",
            "## Abstract Draft",
            "",
            packet["paper_sections"]["abstract_ko"],
            "",
            "## Method",
            "",
            packet["paper_sections"]["method_ko"],
            "",
            "## Core / Adapter Evidence",
            "",
            f"- Core status: `{packet['core']['status']}` (`{packet['core']['passed_gates']}/{packet['core']['total_gates']}` gates)",
            f"- Core ablation contract: `{packet['core']['ablation_status']}` (`{packet['core']['ablation_count']}` ablations)",
            f"- Core reference run: `{packet['core']['reference_status']}`, released `{packet['core']['reference_released_actions']}`, ablations `{packet['core']['reference_ablation_count']}`",
            f"- Core module benchmark: `{packet['core']['module_benchmark_status']}`, scenarios `{packet['core']['module_benchmark_scenario_count']}`, full-core F1 `{fmt(packet['core']['module_benchmark_full_core_f1'], 3)}`, action-health FP lift `{packet['core']['module_benchmark_action_health_fp_lift']}`, invariant FP lift `{packet['core']['module_benchmark_invariant_fp_lift']}`",
            f"- Core/adapter boundary audit: `{packet['boundary_audit']['status']}` (`{packet['boundary_audit']['passed_checks']}/{packet['boundary_audit']['total_checks']}` checks)",
            f"- Core operational violations: imports `{packet['boundary_audit']['core_import_violations']}`, strings `{packet['boundary_audit']['core_string_violations']}`",
            f"- Adapter status: `{packet['adapter']['status']}`",
            f"- Big-bet queue: `{packet['adapter']['big_bet_status']}` (`{packet['adapter']['big_bet_count']}` bets)",
            "",
            "## Generality",
            "",
            packet["paper_sections"]["generality_ko"],
            "",
            "## Algorithm",
            "",
            "```text",
            packet["paper_sections"]["algorithm_ko"],
            "```",
            "",
            "## Evidence Snapshot",
            "",
            f"- Status: `{packet['status']}`",
            f"- Readiness gates: `{mechanism['readiness_gates']}`",
            f"- Pre-public-equation best public LB: `{fmt(score['pre_public_equation_best_public_lb'], 10)}`",
            f"- Current best public LB: `{fmt(score['current_best_public_lb'], 10)}`",
            f"- Delta: `{fmt(score['current_delta_vs_pre_public_equation'], 10)}`",
            f"- Route delta vs null: `{fmt(mechanism['primary_route_delta'], 5)}` vs `{fmt(mechanism['primary_null_route_delta'], 5)}`",
            f"- S2 usage vs null: `{fmt(mechanism['s2_usage'], 3)}` vs `{fmt(mechanism['s2_null_usage'], 3)}`",
            f"- Human-state cell AUC / row AUC: `{fmt(human['cell_oof_auc'], 3)}` / `{fmt(human['row_oof_auc'], 3)}`",
            f"- Assignment gap: `{human['assignment_gap_status']}`, row-support gap `{fmt(human['assignment_gap_row_support_gap'], 4)}`",
            f"- Hidden row-support sensor: `{human['hidden_row_support_sensor_status']}`, family `{human['hidden_row_support_best_family']}`, row AUC `{fmt(human['hidden_row_support_mean_row_auc'], 4)}`, cell recall `{fmt(human['hidden_row_support_mean_cell_recall'], 4)}`",
            f"- Masked row-support objective: `{human['masked_row_support_objective_status']}`, row AUC `{fmt(human['masked_row_support_full_row_auc'], 4)}`, cell recall `{fmt(human['masked_row_support_full_cell_recall'], 4)}`, group stress AUC `{fmt(human['masked_row_support_group_stress_auc'], 4)}`",
            f"- Row-support action decoder: `{human['row_support_action_decoder_status']}`, recommended `{human['row_support_action_decoder_recommended']}`, changed cells `{human['row_support_action_decoder_changed_cells']}`, safety z `{fmt(human['row_support_action_decoder_safety_z'], 4)}`, combined z `{fmt(human['row_support_action_decoder_combined_z'], 4)}`",
            f"- Route-frontier action decoder: `{human['route_frontier_action_decoder_status']}`, recommended `{human['route_frontier_action_decoder_recommended']}`, scores `{human['route_frontier_action_decoder_variant_scores']}`",
            f"- Route-toxicity fusion decoder: `{human['route_toxicity_fusion_decoder_status']}`, recommended `{human['route_toxicity_fusion_decoder_recommended']}`, scores `{human['route_toxicity_fusion_decoder_variant_scores']}`",
            f"- Decoder-order jury solver: `{human['decoder_order_jury_solver_status']}`, recommended `{human['decoder_order_jury_solver_recommended']}`, file `{human['decoder_order_jury_solver_file']}`, priority `{fmt(human['decoder_order_jury_solver_priority'], 4)}`",
            f"- Decoder boundary tomography: `{human['decoder_boundary_tomography_status']}`, recommended `{human['decoder_boundary_tomography_recommended']}`, file `{human['decoder_boundary_tomography_file']}`, priority `{fmt(human['decoder_boundary_tomography_priority'], 4)}`, inventory `{human['decoder_boundary_tomography_inventory']}`",
            f"- Core-mediated action release: `{human['core_mediated_action_release_status']}`, recommended `{human['core_mediated_action_release_recommended']}`, file `{human['core_mediated_action_release_file']}`, priority `{fmt(human['core_mediated_action_release_priority'], 4)}`, inventory `{human['core_mediated_action_release_inventory']}`",
            f"- Core release ablation: `{human['core_release_ablation_status']}`, full-core `{human['core_release_ablation_lb_candidate']}`, file `{human['core_release_ablation_lb_candidate_file']}`, priority `{fmt(human['core_release_ablation_lb_candidate_priority'], 4)}`",
            f"- Core release architecture sensor: `{human['core_release_ablation_sensor']}`, file `{human['core_release_ablation_sensor_file']}`, priority `{fmt(human['core_release_ablation_sensor_priority'], 4)}`",
            f"- Core-health calibrated release: `{human['core_health_calibrated_status']}`, guarded `{human['core_health_calibrated_lb_candidate']}`, file `{human['core_health_calibrated_lb_candidate_file']}`, priority `{fmt(human['core_health_calibrated_lb_candidate_priority'], 4)}`",
            f"- Core-health big-bet sensor: `{human['core_health_calibrated_big_bet']}`, file `{human['core_health_calibrated_big_bet_file']}`, priority `{fmt(human['core_health_calibrated_big_bet_priority'], 4)}`",
            f"- Core-health benchmark calibration: `{human['core_health_calibrated_benchmark_calibration']}`",
            f"- Cross-listener transport: `{human['cross_listener_transport_status']}`, recommended `{human['cross_listener_transport_recommended']}`, file `{human['cross_listener_transport_file']}`, priority `{fmt(human['cross_listener_transport_priority'], 4)}`",
            f"- Cross-listener negative sensor: `{human['cross_listener_transport_negative_sensor']}`",
            f"- Counterfactual listener-dropout: `{human['counterfactual_listener_dropout_status']}`, information sensor `{human['counterfactual_listener_dropout_information_sensor']}`, file `{human['counterfactual_listener_dropout_information_sensor_file']}`, priority `{fmt(human['counterfactual_listener_dropout_information_sensor_priority'], 4)}`",
            f"- Listener-dropout thesis sensor: `{human['counterfactual_listener_dropout_thesis_sensor']}`, file `{human['counterfactual_listener_dropout_thesis_sensor_file']}`, priority `{fmt(human['counterfactual_listener_dropout_thesis_sensor_priority'], 4)}`",
            f"- Spectral public-tangent solver: `{human['spectral_public_tangent_status']}`, first-mode variance `{fmt(human['spectral_public_tangent_first_mode_variance'], 4)}`, top-5 variance `{fmt(human['spectral_public_tangent_top5_variance'], 4)}`",
            f"- Spectral information sensor: `{human['spectral_public_tangent_information_sensor']}`, file `{human['spectral_public_tangent_information_sensor_file']}`, priority `{fmt(human['spectral_public_tangent_information_sensor_priority'], 4)}`",
            f"- Spectral counter sensor: `{human['spectral_public_tangent_counter_sensor']}`, file `{human['spectral_public_tangent_counter_sensor_file']}`",
            f"- Negative tangent invariant projection: `{human['negative_tangent_invariant_status']}`, recommended `{human['negative_tangent_invariant_recommended']}`, file `{human['negative_tangent_invariant_file']}`, bad cosine `{fmt(human['negative_tangent_invariant_bad_cosine'], 4)}`, energy delta `{fmt(human['negative_tangent_invariant_energy_delta'], 5)}`, subject delta `{fmt(human['negative_tangent_invariant_subject_delta'], 5)}`",
            f"- LB-conditioned responsibility: `{human['lb_conditioned_responsibility_status']}`, recommended `{human['lb_conditioned_responsibility_recommended']}`, file `{human['lb_conditioned_responsibility_file']}`, LOO corr `{fmt(human['lb_conditioned_responsibility_loo_corr'], 4)}`, changed cells `{human['lb_conditioned_responsibility_changed_cells']}`, predicted delta `{fmt(human['lb_conditioned_responsibility_predicted_delta'], 5)}`, energy delta `{fmt(human['lb_conditioned_responsibility_energy_delta'], 5)}`, bad cosine `{fmt(human['lb_conditioned_responsibility_bad_cosine'], 4)}`",
            f"- Mixture-listener responsibility: `{human['mixture_listener_responsibility_status']}`, recommended `{human['mixture_listener_responsibility_recommended']}`, file `{human['mixture_listener_responsibility_file']}`, mixture LOO corr `{fmt(human['mixture_listener_loo_corr'], 4)}` vs scalar `{fmt(human['mixture_listener_scalar_loo_corr'], 4)}`, changed cells `{human['mixture_listener_changed_cells']}`, scalar delta `{fmt(human['mixture_listener_scalar_delta'], 5)}`, mode delta `{fmt(human['mixture_listener_mode_delta'], 5)}`, conflict `{fmt(human['mixture_listener_conflict_score'], 4)}`, bad cosine `{fmt(human['mixture_listener_bad_cosine'], 4)}`",
            f"- Public/private subset tomography: `{human['public_private_subset_tomography_status']}`, recommended `{human['public_private_subset_tomography_recommended']}`, file `{human['public_private_subset_tomography_file']}`, source LOO corr `{fmt(human['public_private_subset_tomography_source_loo_corr'], 4)}`, cells `{human['public_private_subset_tomography_cell_count']}`, changed cells `{human['public_private_subset_tomography_changed_cells']}`, predicted delta `{fmt(human['public_private_subset_tomography_predicted_delta'], 5)}`, inclusion `{fmt(human['public_private_subset_tomography_mean_inclusion'], 4)}`, label confidence `{fmt(human['public_private_subset_tomography_mean_label_confidence'], 4)}`, private safety `{fmt(human['public_private_subset_tomography_private_safety'], 4)}`, toxicity `{fmt(human['public_private_subset_tomography_toxicity'], 4)}`",
            f"- Anti-listener toxicity equation: `{human['anti_listener_toxicity_status']}`, recommended `{human['anti_listener_toxicity_recommended']}`, file `{human['anti_listener_toxicity_file']}`, source LOO corr `{fmt(human['anti_listener_toxicity_source_loo_corr'], 4)}`, candidate cells `{human['anti_listener_toxicity_cell_count']}`, changed cells `{human['anti_listener_toxicity_changed_cells']}`, predicted delta `{fmt(human['anti_listener_toxicity_predicted_delta'], 5)}`, listener inverse `{fmt(human['anti_listener_toxicity_listener_inverse'], 4)}`, private safety `{fmt(human['anti_listener_toxicity_private_safety'], 4)}`, hard-world toxicity `{fmt(human['anti_listener_toxicity_hardworld_toxicity'], 4)}`, broad toxicity `{fmt(human['anti_listener_toxicity_broad_toxicity'], 4)}`",
            f"- Frontier active-silence: `{human['frontier_trajectory_silence_status']}`, recommended `{human['frontier_trajectory_silence_recommended']}`, file `{human['frontier_trajectory_silence_file']}`, cells `{human['frontier_trajectory_silence_cell_count']}`, changed cells `{human['frontier_trajectory_silence_changed_cells']}`, first bad-mode variance `{fmt(human['frontier_trajectory_silence_first_bad_mode_variance'], 4)}`, frontier cosine `{fmt(human['frontier_trajectory_silence_frontier_cosine'], 4)}`, bad-tangent cosine `{fmt(human['frontier_trajectory_silence_bad_tangent_cosine'], 4)}`, silence `{fmt(human['frontier_trajectory_silence_mean_silence_pressure'], 4)}`",
            f"- Action decoder ablation: `{human['action_decoder_ablation_status']}`, recommended `{human['action_decoder_ablation_recommended_lb_sensor']}`, big bet `{human['action_decoder_ablation_big_bet_sensor']}`",
            "",
            "## Role-Based Outputs",
            "",
            *role_rows,
            "",
            "## Stress Evidence",
            "",
            *stress_rows,
            "",
            "## Big-Bet Queue",
            "",
            packet["paper_sections"]["big_bets_ko"],
            "",
            "## Boundaries",
            "",
            packet["paper_sections"]["limitations_ko"],
            "",
            "## Team Reproduction",
            "",
            "```bash",
            packet["outputs"]["one_command"],
            "```",
            "",
            "Generated supporting reports:",
            "",
            f"- `{packet['outputs']['readiness_report']}`",
            f"- `{packet['outputs']['reproducibility_contract']}`",
            f"- `{packet['outputs']['core_manifest']}`",
            f"- `{packet['outputs']['core_ablation_contract']}`",
            f"- `{packet['outputs']['core_reference_run']}`",
            f"- `{packet['outputs']['core_module_benchmark']}`",
            f"- `{packet['outputs']['core_adapter_boundary_audit']}`",
            f"- `{packet['outputs']['sleep_adapter_report']}`",
            f"- `{packet['outputs']['big_bet_queue']}`",
            f"- `{packet['outputs']['assignment_gap_decomposition_probe']}`",
            f"- `{packet['outputs']['hidden_row_support_sensor_probe']}`",
            f"- `{packet['outputs']['masked_row_support_objective_probe']}`",
            f"- `{packet['outputs']['row_support_strict_action_decoder']}`",
            f"- `{packet['outputs']['route_frontier_action_decoder']}`",
            f"- `{packet['outputs']['route_toxicity_fusion_decoder']}`",
            f"- `{packet['outputs']['decoder_order_jury_solver']}`",
            f"- `{packet['outputs']['decoder_boundary_tomography_solver']}`",
            f"- `{packet['outputs']['core_mediated_action_release']}`",
            f"- `{packet['outputs']['core_release_ablation_probe']}`",
            f"- `{packet['outputs']['core_health_calibrated_release']}`",
            f"- `{packet['outputs']['cross_listener_transport_decoder']}`",
            f"- `{packet['outputs']['counterfactual_listener_dropout_solver']}`",
            f"- `{packet['outputs']['spectral_public_tangent_solver']}`",
            f"- `{packet['outputs']['negative_tangent_invariant_projection_solver']}`",
            f"- `{packet['outputs']['lb_conditioned_responsibility_solver']}`",
            f"- `{packet['outputs']['mixture_listener_responsibility_solver']}`",
            f"- `{packet['outputs']['public_private_subset_tomography_solver']}`",
            f"- `{packet['outputs']['anti_listener_toxicity_equation_solver']}`",
            f"- `{packet['outputs']['frontier_trajectory_silence_solver']}`",
            f"- `{packet['outputs']['action_decoder_ablation_suite']}`",
            "",
        ]
    )


def main() -> None:
    build_packet()


if __name__ == "__main__":
    main()
