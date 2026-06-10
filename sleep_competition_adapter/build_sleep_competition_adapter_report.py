#!/usr/bin/env python3
"""Build the sleep-competition adapter report for HS-JEPA.

This adapter maps the competition-agnostic HS-JEPA core into the current sleep
lifestyle-log competition.  It is allowed to mention Q/S targets, S2, public
LB sensors, and upload-safe submissions because those are adapter concerns.
"""

from __future__ import annotations

from pathlib import Path
import json
import math


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

CORE_MANIFEST_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_manifest.json"
CORE_ABLATION_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_ablation_contract.json"
TEAM_OUT = ROOT / "team_hsjepa_end_to_end" / "outputs" / "route_conserving_s2_bridge"

PACKAGE_JSON = TEAM_OUT / "route_conserving_s2_bridge_package.json"
VALIDATION_JSON = TEAM_OUT / "route_conserving_s2_bridge_validation_report.json"
READINESS_JSON = TEAM_OUT / "hsjepa_architecture_readiness_report.json"
GENERALITY_JSON = TEAM_OUT / "hsjepa_generality_report.json"
METHOD_PACKET_JSON = TEAM_OUT / "hsjepa_paper_method_packet.json"
OG_PROBE_JSON = OUT / "og_only_assignment_teacher_probe.json"
ASSIGNMENT_GAP_JSON = OUT / "assignment_gap_decomposition_probe.json"
ROW_SUPPORT_SENSOR_JSON = OUT / "hidden_row_support_sensor_probe.json"
MASKED_ROW_SUPPORT_JSON = OUT / "masked_row_support_objective_probe.json"
ROW_SUPPORT_DECODER_JSON = OUT / "row_support_strict_action_decoder" / "row_support_strict_action_decoder_readout.json"
ROUTE_FRONTIER_DECODER_JSON = OUT / "route_frontier_action_decoder" / "route_frontier_action_decoder_readout.json"
ROUTE_TOXICITY_FUSION_DECODER_JSON = OUT / "route_toxicity_fusion_decoder" / "route_toxicity_fusion_decoder_readout.json"
DECODER_ORDER_JURY_JSON = OUT / "decoder_order_jury_solver" / "decoder_order_jury_solver_readout.json"
ACTION_DECODER_ABLATION_JSON = OUT / "action_decoder_ablation_suite" / "hsjepa_action_decoder_ablation_suite.json"
CONTRASTIVE_PROBE_JSON = OUT / "listener_invariant_contrastive_probe.json"
PRIVATE_TOXICITY_PROBE_JSON = OUT / "private_safe_toxicity_probe.json"
HARDWORLD_TOXICITY_PROBE_JSON = OUT / "hardworld_toxicity_factorization_probe.json"
FACTORIZED_DECODER_JSON = OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout.json"
FACTORIZED_STRESS_JSON = OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit.json"

REPORT_JSON = OUT / "sleep_competition_adapter_report.json"
REPORT_MD = OUT / "sleep_competition_adapter_report_ko.md"
BIG_BET_JSON = OUT / "hsjepa_big_bet_queue.json"
BIG_BET_MD = OUT / "hsjepa_big_bet_queue_ko.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: object, digits: int = 6) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def require_inputs() -> None:
    required = [
        CORE_MANIFEST_JSON,
        CORE_ABLATION_JSON,
        PACKAGE_JSON,
        VALIDATION_JSON,
        READINESS_JSON,
        GENERALITY_JSON,
        OG_PROBE_JSON,
        ASSIGNMENT_GAP_JSON,
        ROW_SUPPORT_SENSOR_JSON,
        MASKED_ROW_SUPPORT_JSON,
        ROW_SUPPORT_DECODER_JSON,
        ROUTE_FRONTIER_DECODER_JSON,
        ROUTE_TOXICITY_FUSION_DECODER_JSON,
        DECODER_ORDER_JURY_JSON,
        ACTION_DECODER_ABLATION_JSON,
        CONTRASTIVE_PROBE_JSON,
        PRIVATE_TOXICITY_PROBE_JSON,
        HARDWORLD_TOXICITY_PROBE_JSON,
        FACTORIZED_DECODER_JSON,
        FACTORIZED_STRESS_JSON,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing sleep adapter inputs: {missing}")


def build_big_bets(
    og_probe: dict[str, object],
    assignment_gap: dict[str, object],
    row_support_sensor: dict[str, object],
    masked_row_support: dict[str, object],
    row_support_decoder: dict[str, object],
    route_frontier_decoder: dict[str, object],
    route_toxicity_fusion_decoder: dict[str, object],
    decoder_order_jury: dict[str, object],
    action_decoder_ablation: dict[str, object],
    contrastive_probe: dict[str, object],
    private_toxicity_probe: dict[str, object],
    hardworld_toxicity_probe: dict[str, object],
) -> list[dict[str, object]]:
    og_verdict = og_probe.get("verdict", {}) if isinstance(og_probe.get("verdict"), dict) else {}
    gap_verdict = assignment_gap.get("verdict", {}) if isinstance(assignment_gap.get("verdict"), dict) else {}
    row_support_verdict = (
        row_support_sensor.get("verdict", {})
        if isinstance(row_support_sensor.get("verdict"), dict)
        else {}
    )
    masked_row_support_verdict = (
        masked_row_support.get("verdict", {})
        if isinstance(masked_row_support.get("verdict"), dict)
        else {}
    )
    row_support_decoder_verdict = (
        row_support_decoder.get("verdict", {})
        if isinstance(row_support_decoder.get("verdict"), dict)
        else {}
    )
    route_frontier_verdict = (
        route_frontier_decoder.get("verdict", {})
        if isinstance(route_frontier_decoder.get("verdict"), dict)
        else {}
    )
    route_toxicity_fusion_verdict = (
        route_toxicity_fusion_decoder.get("verdict", {})
        if isinstance(route_toxicity_fusion_decoder.get("verdict"), dict)
        else {}
    )
    decoder_order_jury_verdict = (
        decoder_order_jury.get("verdict", {})
        if isinstance(decoder_order_jury.get("verdict"), dict)
        else {}
    )
    action_ablation_verdict = (
        action_decoder_ablation.get("verdict", {})
        if isinstance(action_decoder_ablation.get("verdict"), dict)
        else {}
    )
    contrastive_verdict = (
        contrastive_probe.get("verdict", {})
        if isinstance(contrastive_probe.get("verdict"), dict)
        else {}
    )
    toxicity_verdict = (
        private_toxicity_probe.get("verdict", {})
        if isinstance(private_toxicity_probe.get("verdict"), dict)
        else {}
    )
    hardworld_verdict = (
        hardworld_toxicity_probe.get("verdict", {})
        if isinstance(hardworld_toxicity_probe.get("verdict"), dict)
        else {}
    )
    return [
        {
            "id": "action_decoder_ablation_suite",
            "name": "Action Decoder Ablation Suite",
            "worldview": "The next breakthrough comes from choosing the correct action-decoder order, not from adding more latent features.",
            "core_modules_exercised": ["action_health_decoder", "invariant_energy", "anti_shortcut_validation"],
            "adapter_move": "Compare toxicity-first, support-first, and route-first decoders under one LB-sensor priority table.",
            "why_big": "If the suite ranking matches public LB, HS-JEPA gains a falsifiable action-decoder selection rule.",
            "expected_public_lb_delta_if_true": -0.0025,
            "latest_probe_status": action_ablation_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_lb_sensor": action_ablation_verdict.get("recommended_lb_sensor"),
                "big_bet_sensor": action_ablation_verdict.get("big_bet_sensor"),
            },
            "kill_criterion": "Public LB contradicts the top-ranked decoder order, or route-first gains vanish under stronger null matching.",
        },
        {
            "id": "og_only_assignment_teacher",
            "name": "OG-only Human-State Assignment Teacher",
            "worldview": "The public-sensor teacher can be replaced by personal/cohort/time human-state consistency.",
            "core_modules_exercised": ["context_encoder", "masked_state_predictor", "listener_responsibility", "anti_shortcut_validation"],
            "adapter_move": "Train a row-target support teacher from OG personal/cohort/time masks, then feed it into the existing invariant decoder.",
            "why_big": "If it works, HS-JEPA becomes a portable architecture rather than a public-sensor case study.",
            "expected_public_lb_delta_if_true": -0.003,
            "latest_probe_status": row_support_verdict.get("status") or gap_verdict.get("status") or og_verdict.get("status"),
            "latest_probe_evidence": {
                "pure_og_row_cap2_mean_recall": og_verdict.get("pure_og_row_cap2_mean_recall"),
                "distilled_row_cap2_mean_recall": og_verdict.get("distilled_row_cap2_mean_recall"),
                "listener_upper_bound_row_cap2_mean_recall": og_verdict.get("listener_upper_bound_row_cap2_mean_recall"),
                "mean_best_portable_recall": gap_verdict.get("mean_best_portable_recall"),
                "mean_row_oracle_stage_recall": gap_verdict.get("mean_row_oracle_stage_recall"),
                "mean_row_support_gap": gap_verdict.get("mean_row_support_gap"),
                "best_row_support_family": row_support_verdict.get("best_portable_family"),
                "best_row_support_mean_auc": row_support_verdict.get("best_portable_mean_row_auc"),
                "best_row_support_mean_cell_recall": row_support_verdict.get("best_portable_mean_cell_recall_with_stage_prior"),
                "best_row_support_auc_z": row_support_verdict.get("best_portable_mean_auc_z_vs_permuted_train"),
                "masked_objective_status": masked_row_support_verdict.get("status"),
                "masked_objective_full_row_auc": masked_row_support_verdict.get("full_composite_mean_row_auc"),
                "masked_objective_full_cell_recall": masked_row_support_verdict.get("full_composite_mean_cell_recall"),
                "masked_objective_human_cell_recall": masked_row_support_verdict.get("human_only_mean_cell_recall"),
                "masked_objective_prediction_cell_recall": masked_row_support_verdict.get("prediction_only_mean_cell_recall"),
                "masked_objective_route_mask_cell_recall": masked_row_support_verdict.get("route_mask_mean_cell_recall"),
                "masked_objective_group_stress_auc": masked_row_support_verdict.get("group_stress_full_mean_auc"),
                "row_support_decoder_status": row_support_decoder_verdict.get("status"),
                "row_support_decoder_recommended_variant": row_support_decoder_verdict.get("recommended_variant"),
                "row_support_decoder_exploratory_changed_cells": row_support_decoder_verdict.get("exploratory_changed_cells"),
                "row_support_decoder_exploratory_safety_z": row_support_decoder_verdict.get("exploratory_safety_z"),
                "row_support_decoder_exploratory_combined_z": row_support_decoder_verdict.get("exploratory_combined_z"),
            },
            "kill_criterion": "Masked row-support keeps failing subject/date/order stress or cannot be converted into safe row-target actions.",
        },
        {
            "id": "masked_row_support_action_decoder",
            "name": "Masked Row-Support Action Decoder",
            "worldview": "The masked row-support representation can choose which route-conserving S2/stage bundles are safe enough to move.",
            "core_modules_exercised": ["masked_state_predictor", "action_health_decoder", "invariant_energy", "anti_shortcut_validation"],
            "adapter_move": "Gate route-conserving bridge bundles by transferred row-support and factorized broad/hard-world toxicity.",
            "why_big": "If this survives LB, HS-JEPA has a concrete path from hidden representation to action-grade row-target decoding.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": row_support_decoder_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": row_support_decoder_verdict.get("recommended_variant"),
                "exploratory_changed_cells": row_support_decoder_verdict.get("exploratory_changed_cells"),
                "exploratory_safety_z": row_support_decoder_verdict.get("exploratory_safety_z"),
                "exploratory_combined_z": row_support_decoder_verdict.get("exploratory_combined_z"),
                "exploratory_mean_route_gain": row_support_decoder_verdict.get("exploratory_mean_route_gain"),
            },
            "kill_criterion": "Public LB worsens or route/null stress remains weak after increasing row-support selectivity.",
        },
        {
            "id": "route_frontier_action_decoder",
            "name": "Route-Frontier Action Decoder",
            "worldview": "The action decoder should select route-manifold frontier moves first, then check row-support and toxicity.",
            "core_modules_exercised": ["action_health_decoder", "invariant_energy", "anti_shortcut_validation"],
            "adapter_move": "Choose public-selected and open-candidate route-frontier bundles that beat broad and matched nulls.",
            "why_big": "If it survives LB, HS-JEPA gains a concrete action translation rule instead of a hand-tuned support gate.",
            "expected_public_lb_delta_if_true": -0.0025,
            "latest_probe_status": route_frontier_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": route_frontier_verdict.get("recommended_variant"),
                "variant_scores": route_frontier_verdict.get("variant_scores"),
            },
            "kill_criterion": "Public LB worsens or matched-null frontier score fails after larger candidate pools are used.",
        },
        {
            "id": "route_toxicity_fusion_decoder",
            "name": "Route-Toxicity Fusion Decoder",
            "worldview": "Route-frontier action ordering and factorized action-health are not alternatives; safe actions need both.",
            "core_modules_exercised": ["invariant_energy", "action_health_decoder", "anti_shortcut_validation"],
            "adapter_move": "Select route-frontier bundles first, then filter driver actions through hard-world/broad-public toxicity and use bridge actions as soft route support.",
            "why_big": "If this wins LB over plain route-frontier, HS-JEPA gains a more general action-grade decoder order.",
            "expected_public_lb_delta_if_true": -0.0025,
            "latest_probe_status": route_toxicity_fusion_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": route_toxicity_fusion_verdict.get("recommended_variant"),
                "variant_scores": route_toxicity_fusion_verdict.get("variant_scores"),
            },
            "kill_criterion": "Public LB says plain route-frontier wins, or fusion only improves local toxicity while harming route/action response.",
        },
        {
            "id": "decoder_order_jury_solver",
            "name": "Decoder-Order Jury Solver",
            "worldview": "Safe row-target assignment is a cross-decoder jury, not a single route or toxicity score.",
            "core_modules_exercised": ["invariant_energy", "action_health_decoder", "anti_shortcut_validation"],
            "adapter_move": "Release only row-target cells independently selected by route-frontier and route-toxicity fusion decoders in the same direction.",
            "why_big": "If this beats route-frontier, HS-JEPA gains an action-grade listener responsibility rule rather than another tuned decoder.",
            "expected_public_lb_delta_if_true": -0.0025,
            "latest_probe_status": decoder_order_jury_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_lb_sensor": decoder_order_jury_verdict.get("recommended_lb_sensor"),
                "claim": decoder_order_jury_verdict.get("claim"),
            },
            "kill_criterion": "Public LB worsens or underperforms route-frontier, meaning consensus is too conservative or action-health removes useful route signal.",
        },
        {
            "id": "listener_invariant_contrastive_decoder",
            "name": "Listener-Invariant Contrastive Decoder",
            "worldview": "A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone.",
            "core_modules_exercised": ["listener_responsibility", "action_health_decoder", "invariant_energy"],
            "adapter_move": "Score candidate row-target actions by listener gain minus route-energy toxicity under random feasible nulls.",
            "why_big": "This could move beyond the current S2 bridge into a general action-health decoder.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": contrastive_verdict.get("status"),
            "latest_probe_evidence": {
                "mean_listener_route_spearman": contrastive_verdict.get("mean_listener_route_spearman"),
                "mean_contrastive_overlap_rate": contrastive_verdict.get("mean_contrastive_overlap_rate"),
                "mean_high_listener_low_route_rate": contrastive_verdict.get("mean_high_listener_low_route_rate"),
            },
            "kill_criterion": "Listener gain and invariant energy remain anti-correlated on strong candidates.",
        },
        {
            "id": "private_safe_toxicity_field",
            "name": "Private-Safe Toxicity Field",
            "worldview": "The plateau comes from actions that help public-like rows but poison private-like rows.",
            "core_modules_exercised": ["action_health_decoder", "anti_shortcut_validation"],
            "adapter_move": "Use failed public sensors, null bundles, and cohort/time stress to learn a toxicity veto before submission packaging.",
            "why_big": "A true toxicity field can preserve the 0.567 gain while reducing private-risk and maybe exposing larger safe moves.",
            "expected_public_lb_delta_if_true": -0.0015,
            "latest_probe_status": toxicity_verdict.get("status"),
            "latest_probe_evidence": {
                "mean_loo_bad_anchor_auc": toxicity_verdict.get("mean_loo_bad_anchor_auc"),
                "worst_loo_bad_anchor_auc": toxicity_verdict.get("worst_loo_bad_anchor_auc"),
                "selected_safety_z_vs_matched_null": toxicity_verdict.get("selected_safety_z_vs_matched_null"),
            },
            "kill_criterion": "Toxicity score only recovers known public failures, fails hard-world anchors, or does not separate matched local nulls.",
        },
        {
            "id": "hardworld_mixture_toxicity_decoder",
            "name": "Hard-World Mixture Toxicity Decoder",
            "worldview": "H088-like hard-world toxicity is anti-correlated with broad public-bad toxicity, so action-health must be factorized.",
            "core_modules_exercised": ["action_health_decoder", "anti_shortcut_validation", "listener_responsibility"],
            "adapter_move": "Replace scalar toxicity with a two-head broad-public/hard-world safety gate before row-target assignment.",
            "why_big": "This directly targets the observed gap where broad toxicity generalizes but misses the H088 hard-world mode.",
            "expected_public_lb_delta_if_true": -0.0025,
            "latest_probe_status": hardworld_verdict.get("status"),
            "latest_probe_evidence": {
                "broad_predicts_hardworld_auc": hardworld_verdict.get("broad_predicts_hardworld_auc"),
                "broad_hardworld_spearman": hardworld_verdict.get("broad_hardworld_spearman"),
                "selected_joint_safety_z": hardworld_verdict.get("selected_joint_safety_z"),
            },
            "kill_criterion": "Broad toxicity predicts H088 well, or mixture safety does not beat matched null after target/source matching.",
        },
        {
            "id": "cross_listener_state_transport",
            "name": "Cross-Listener Human-State Transport",
            "worldview": "Subjective Q and objective S labels are different listeners of one human state, not separate tasks.",
            "core_modules_exercised": ["context_encoder", "listener_responsibility", "invariant_energy"],
            "adapter_move": "Move actions only when Q-listener and S-listener state transitions are mutually consistent.",
            "why_big": "This attacks the current weakness that Q and S decoders are mostly separated.",
            "expected_public_lb_delta_if_true": -0.001,
            "kill_criterion": "Q-S bridge actions fail null tests or replicate the already-killed subjective-shadow bridge.",
        },
    ]


def build_report() -> dict[str, object]:
    require_inputs()
    core = read_json(CORE_MANIFEST_JSON)
    core_ablation = read_json(CORE_ABLATION_JSON)
    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    readiness = read_json(READINESS_JSON)
    generality = read_json(GENERALITY_JSON)
    method = read_json(METHOD_PACKET_JSON) if METHOD_PACKET_JSON.exists() else {"title": "HS-JEPA Method Packet Pending"}
    og_probe = read_json(OG_PROBE_JSON)
    assignment_gap = read_json(ASSIGNMENT_GAP_JSON)
    row_support_sensor = read_json(ROW_SUPPORT_SENSOR_JSON)
    masked_row_support = read_json(MASKED_ROW_SUPPORT_JSON)
    row_support_decoder = read_json(ROW_SUPPORT_DECODER_JSON)
    route_frontier_decoder = read_json(ROUTE_FRONTIER_DECODER_JSON)
    route_toxicity_fusion_decoder = read_json(ROUTE_TOXICITY_FUSION_DECODER_JSON)
    decoder_order_jury = read_json(DECODER_ORDER_JURY_JSON)
    action_decoder_ablation = read_json(ACTION_DECODER_ABLATION_JSON)
    contrastive_probe = read_json(CONTRASTIVE_PROBE_JSON)
    private_toxicity_probe = read_json(PRIVATE_TOXICITY_PROBE_JSON)
    hardworld_toxicity_probe = read_json(HARDWORLD_TOXICITY_PROBE_JSON)
    factorized_decoder = read_json(FACTORIZED_DECODER_JSON)
    factorized_stress = read_json(FACTORIZED_STRESS_JSON)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    mechanism = validation["mechanism_evidence"]
    og_verdict = og_probe.get("verdict", {})
    gap_verdict = assignment_gap.get("verdict", {})
    row_support_verdict = row_support_sensor.get("verdict", {})
    masked_row_support_verdict = masked_row_support.get("verdict", {})
    row_support_decoder_verdict = row_support_decoder.get("verdict", {})
    route_frontier_verdict = route_frontier_decoder.get("verdict", {})
    route_toxicity_fusion_verdict = route_toxicity_fusion_decoder.get("verdict", {})
    decoder_order_jury_verdict = decoder_order_jury.get("verdict", {})
    action_decoder_ablation_verdict = action_decoder_ablation.get("verdict", {})
    contrastive_verdict = contrastive_probe.get("verdict", {})
    toxicity_verdict = private_toxicity_probe.get("verdict", {})
    hardworld_verdict = hardworld_toxicity_probe.get("verdict", {})
    factorized_variants = factorized_decoder.get("variants", {})
    factorized_stress_variants = factorized_stress.get("variants", {})

    adapter_mapping = [
        {
            "core_module": "context_encoder",
            "competition_adapter": "raw lifestyle, subject/cohort, row-order, and sleep-state context features",
            "evidence": f"cell-level human-state orientation AUC {fmt(human['cell_oof_auc_human_target_context'], 3)}",
            "boundary": f"row-level assignment AUC {fmt(human['row_oof_auc'], 3)} is not enough for standalone assignment.",
        },
        {
            "core_module": "masked_state_predictor",
            "competition_adapter": "teacher/student probes for hidden S2-hub and row-target support orientation",
            "evidence": "human-state probe exists as a role-based output",
            "boundary": "current strongest teacher still uses public-sensitive action support.",
        },
        {
            "core_module": "listener_responsibility",
            "competition_adapter": "Q/S targets are treated as listeners; S2 emerges as an objective-stage hub",
            "evidence": f"S2 listener usage {fmt(mechanism['s2_listener_s2_any_rate'], 3)} vs null {fmt(mechanism['s2_listener_null_s2_any_rate'], 3)}",
            "boundary": "S2 hub is a sleep competition case-study claim, not a universal physiology claim.",
        },
        {
            "core_module": "action_health_decoder",
            "competition_adapter": "public-positive and public-negative sensors define toxic action diagnostics",
            "evidence": "mechanism ablation kills broad/toxic alternatives before release",
            "boundary": "public LB sensor is not portable and must be replaced for non-competition deployments.",
        },
        {
            "core_module": "invariant_energy",
            "competition_adapter": "Q/S route energy and route-conserving S2 bridge",
            "evidence": f"route z-scores primary={fmt(mechanism['primary_route_z'], 2)}, s2={fmt(mechanism['s2_route_z'], 2)}",
            "boundary": "other domains need their own temporal, physiological, semantic, or cohort invariant.",
        },
        {
            "core_module": "anti_shortcut_validation",
            "competition_adapter": "upload safety, feasible-bundle nulls, mechanism knockout, and release checklist",
            "evidence": f"generality checks {generality['passed_checks']}/{generality['total_checks']}",
            "boundary": "private LB safety is not proven.",
        },
    ]

    report = {
        "package": "Sleep Competition Adapter for HS-JEPA",
        "status": "adapter_ready_with_public_sensor_boundary",
        "core_status": core["status"],
        "core_ablation_status": core_ablation["status"],
        "adapter_claim": (
            "This adapter converts HS-JEPA Core into a sleep-log competition system by supplying "
            "Q/S listeners, a route invariant, public-sensor action evidence, and upload-safe sparse row-target decoding."
        ),
        "score_evidence": {
            "pre_public_equation_best_public_lb": public["pre_public_equation_best_public_lb"],
            "current_best_public_lb": public["current_best_public_lb"],
            "delta": public["current_delta_vs_pre_breakthrough"],
            "current_best_file": public["current_best_file"],
        },
        "adapter_mapping": adapter_mapping,
        "og_assignment_teacher_probe": {
            "status": og_verdict.get("status"),
            "pure_og_row_cap2_mean_recall": og_verdict.get("pure_og_row_cap2_mean_recall"),
            "pure_og_row_cap2_mean_precision_lift": og_verdict.get("pure_og_row_cap2_mean_precision_lift"),
            "distilled_row_cap2_mean_recall": og_verdict.get("distilled_row_cap2_mean_recall"),
            "distilled_row_cap2_mean_precision": og_verdict.get("distilled_row_cap2_mean_precision"),
            "listener_upper_bound_row_cap2_mean_recall": og_verdict.get("listener_upper_bound_row_cap2_mean_recall"),
            "interpretation": og_verdict.get("interpretation"),
        },
        "assignment_gap_decomposition_probe": {
            "status": gap_verdict.get("status"),
            "mean_best_portable_recall": gap_verdict.get("mean_best_portable_recall"),
            "mean_distilled_row_gated_recall": gap_verdict.get("mean_distilled_row_gated_recall"),
            "mean_target_oracle_recall": gap_verdict.get("mean_target_oracle_recall"),
            "mean_row_oracle_stage_recall": gap_verdict.get("mean_row_oracle_stage_recall"),
            "mean_row_support_gap": gap_verdict.get("mean_row_support_gap"),
            "next_action": gap_verdict.get("next_action"),
            "interpretation": gap_verdict.get("interpretation"),
        },
        "hidden_row_support_sensor_probe": {
            "status": row_support_verdict.get("status"),
            "best_portable_family": row_support_verdict.get("best_portable_family"),
            "best_portable_mean_row_auc": row_support_verdict.get("best_portable_mean_row_auc"),
            "best_portable_mean_row_recall_at_k": row_support_verdict.get("best_portable_mean_row_recall_at_k"),
            "best_portable_mean_cell_recall_with_stage_prior": row_support_verdict.get("best_portable_mean_cell_recall_with_stage_prior"),
            "best_portable_mean_auc_z_vs_permuted_train": row_support_verdict.get("best_portable_mean_auc_z_vs_permuted_train"),
            "adapter_minus_portable_cell_recall_gap": row_support_verdict.get("adapter_minus_portable_cell_recall_gap"),
            "next_action": row_support_verdict.get("next_action"),
            "interpretation": row_support_verdict.get("interpretation"),
        },
        "masked_row_support_objective_probe": {
            "status": masked_row_support_verdict.get("status"),
            "full_composite_mean_row_auc": masked_row_support_verdict.get("full_composite_mean_row_auc"),
            "full_composite_mean_row_recall_at_k": masked_row_support_verdict.get("full_composite_mean_row_recall_at_k"),
            "full_composite_mean_cell_recall": masked_row_support_verdict.get("full_composite_mean_cell_recall"),
            "human_only_mean_cell_recall": masked_row_support_verdict.get("human_only_mean_cell_recall"),
            "prediction_only_mean_cell_recall": masked_row_support_verdict.get("prediction_only_mean_cell_recall"),
            "route_mask_mean_cell_recall": masked_row_support_verdict.get("route_mask_mean_cell_recall"),
            "robust_mask_count": masked_row_support_verdict.get("robust_mask_count"),
            "group_stress_full_mean_auc": masked_row_support_verdict.get("group_stress_full_mean_auc"),
            "group_stress_full_mean_recall_at_k": masked_row_support_verdict.get("group_stress_full_mean_recall_at_k"),
            "next_action": masked_row_support_verdict.get("next_action"),
            "interpretation": masked_row_support_verdict.get("interpretation"),
        },
        "row_support_strict_action_decoder": {
            "status": row_support_decoder_verdict.get("status"),
            "recommended_variant": row_support_decoder_verdict.get("recommended_variant"),
            "reason": row_support_decoder_verdict.get("reason"),
            "exploratory_changed_cells": row_support_decoder_verdict.get("exploratory_changed_cells"),
            "exploratory_safety_z": row_support_decoder_verdict.get("exploratory_safety_z"),
            "exploratory_combined_z": row_support_decoder_verdict.get("exploratory_combined_z"),
            "exploratory_mean_route_gain": row_support_decoder_verdict.get("exploratory_mean_route_gain"),
            "strict_changed_cells": row_support_decoder_verdict.get("strict_changed_cells"),
            "variants": {
                name: {
                    "submission_file": item.get("submission_file"),
                    "changed_cells": item.get("decode_diagnostics", {}).get("changed_cells"),
                    "changed_rows": item.get("decode_diagnostics", {}).get("changed_rows"),
                    "selected_bundles": item.get("decode_diagnostics", {}).get("selected_bundles"),
                    "upload_safe": item.get("validation", {}).get("upload_safe"),
                }
                for name, item in row_support_decoder.get("variants", {}).items()
                if isinstance(item, dict)
            },
        },
        "route_frontier_action_decoder": {
            "status": route_frontier_verdict.get("status"),
            "recommended_variant": route_frontier_verdict.get("recommended_variant"),
            "reason": route_frontier_verdict.get("reason"),
            "variant_scores": route_frontier_verdict.get("variant_scores"),
            "variants": {
                name: {
                    "submission_file": item.get("submission_file"),
                    "changed_cells": item.get("decode_diagnostics", {}).get("changed_cells"),
                    "changed_rows": item.get("decode_diagnostics", {}).get("changed_rows"),
                    "selected_bundles": item.get("decode_diagnostics", {}).get("selected_bundles"),
                    "upload_safe": item.get("validation", {}).get("upload_safe"),
                }
                for name, item in route_frontier_decoder.get("variants", {}).items()
                if isinstance(item, dict)
            },
        },
        "route_toxicity_fusion_decoder": {
            "status": route_toxicity_fusion_verdict.get("status"),
            "recommended_variant": route_toxicity_fusion_verdict.get("recommended_variant"),
            "reason": route_toxicity_fusion_verdict.get("reason"),
            "variant_scores": route_toxicity_fusion_verdict.get("variant_scores"),
            "variants": {
                name: {
                    "submission_file": item.get("submission_file"),
                    "changed_cells": item.get("decode_diagnostics", {}).get("changed_cells"),
                    "changed_rows": item.get("decode_diagnostics", {}).get("changed_rows"),
                    "selected_bundles": item.get("decode_diagnostics", {}).get("selected_bundles"),
                    "upload_safe": item.get("validation", {}).get("upload_safe"),
                }
                for name, item in route_toxicity_fusion_decoder.get("variants", {}).items()
                if isinstance(item, dict)
            },
        },
        "decoder_order_jury_solver": {
            "status": decoder_order_jury_verdict.get("status"),
            "recommended_lb_sensor": decoder_order_jury_verdict.get("recommended_lb_sensor"),
            "claim": decoder_order_jury_verdict.get("claim"),
            "failure_interpretation": decoder_order_jury_verdict.get("failure_interpretation"),
            "top_ranked": decoder_order_jury.get("ranking", [])[:3],
        },
        "action_decoder_ablation_suite": {
            "status": action_decoder_ablation_verdict.get("status"),
            "recommended_lb_sensor": action_decoder_ablation_verdict.get("recommended_lb_sensor"),
            "big_bet_sensor": action_decoder_ablation_verdict.get("big_bet_sensor"),
            "reason": action_decoder_ablation_verdict.get("reason"),
            "top_ranked": action_decoder_ablation.get("ranking", [])[:3],
            "findings": action_decoder_ablation.get("findings", []),
        },
        "listener_invariant_contrastive_probe": {
            "status": contrastive_verdict.get("status"),
            "mean_listener_route_spearman": contrastive_verdict.get("mean_listener_route_spearman"),
            "mean_contrastive_overlap_rate": contrastive_verdict.get("mean_contrastive_overlap_rate"),
            "mean_high_listener_low_route_rate": contrastive_verdict.get("mean_high_listener_low_route_rate"),
            "interpretation": contrastive_verdict.get("interpretation"),
        },
        "private_safe_toxicity_probe": {
            "status": toxicity_verdict.get("status"),
            "mean_loo_bad_anchor_auc": toxicity_verdict.get("mean_loo_bad_anchor_auc"),
            "worst_loo_bad_anchor_auc": toxicity_verdict.get("worst_loo_bad_anchor_auc"),
            "anchors_below_0p6_auc": toxicity_verdict.get("anchors_below_0p6_auc"),
            "selected_safety_z_vs_matched_null": toxicity_verdict.get("selected_safety_z_vs_matched_null"),
            "p_null_safety_ge_selected": toxicity_verdict.get("p_null_safety_ge_selected"),
            "interpretation": toxicity_verdict.get("interpretation"),
        },
        "hardworld_toxicity_factorization_probe": {
            "status": hardworld_verdict.get("status"),
            "broad_predicts_hardworld_auc": hardworld_verdict.get("broad_predicts_hardworld_auc"),
            "broad_hardworld_spearman": hardworld_verdict.get("broad_hardworld_spearman"),
            "broad_safe_hardworld_toxic_cells": hardworld_verdict.get("broad_safe_hardworld_toxic_cells"),
            "selected_joint_safety_z": hardworld_verdict.get("selected_joint_safety_z"),
            "selected_hardworld_top_toxic_rate": hardworld_verdict.get("selected_hardworld_top_toxic_rate"),
            "null_hardworld_top_toxic_rate": hardworld_verdict.get("null_hardworld_top_toxic_rate"),
            "interpretation": hardworld_verdict.get("interpretation"),
        },
        "factorized_toxicity_decoder_candidate": {
            "experiment": factorized_decoder.get("experiment"),
            "architecture_role": factorized_decoder.get("architecture_role"),
            "core_boundary": factorized_decoder.get("core_boundary"),
            "variants": {
                name: {
                    "submission_file": item.get("submission_file"),
                    "changed_cells": item.get("decode_diagnostics", {}).get("changed_cells"),
                    "changed_rows": item.get("decode_diagnostics", {}).get("changed_rows"),
                    "joint_safety_mean": item.get("decode_diagnostics", {}).get("selected_safety", {}).get("joint_safety_mean"),
                    "hardworld_top_toxic_rate": item.get("decode_diagnostics", {}).get("selected_safety", {}).get("hardworld_top_toxic_rate"),
                    "broad_safe_hardworld_toxic_rate": item.get("decode_diagnostics", {}).get("selected_safety", {}).get("broad_safe_hardworld_toxic_rate"),
                    "upload_safe": item.get("validation", {}).get("upload_safe"),
                }
                for name, item in factorized_variants.items()
                if isinstance(item, dict)
            },
        },
        "factorized_toxicity_decoder_stress_audit": {
            "status": factorized_stress.get("status"),
            "iterations": factorized_stress.get("iterations"),
            "variants": {
                name: {
                    "submission_file": item.get("submission_file"),
                    "verdict": item.get("verdict", {}).get("status"),
                    "target_null_joint_safety_z": item.get("verdict", {}).get("target_null_joint_safety_z"),
                    "source_null_conflict_p": item.get("verdict", {}).get("source_null_conflict_p"),
                    "hardworld_top_toxic_exposure": item.get("actual", {}).get("hardworld_top_toxic_exposure"),
                    "broad_safe_hardworld_toxic_exposure": item.get("actual", {}).get("broad_safe_hardworld_toxic_exposure"),
                }
                for name, item in factorized_stress_variants.items()
                if isinstance(item, dict)
            },
        },
        "role_outputs": {
            role: item["submission_file"]
            for role, item in package["packaged_submissions"].items()
        },
        "what_the_adapter_proves": [
            "HS-JEPA-style listener/action/invariant separation can explain the 0.567 public-LB breakthrough case study.",
            "Route-conserving action selection is statistically non-random against feasible null bundles.",
            "Human-state latent explains target/cell orientation but not enough row assignment on its own.",
            "A pure OG-only assignment teacher is not ready yet; this is now a measured architecture boundary, not an informal caveat.",
            "The assignment gap decomposes into a row-support bottleneck: target route is relatively easy, but current human/social/cohort context does not find the right support rows.",
            "A teacher-transfer hidden row-support sensor is partially alive; portable row-support composite context transfers across teacher worlds better than the listener upper bound in this local diagnostic.",
            "Masked row-support behaves like a real HS-JEPA representation target under teacher-transfer and feature-family masks, but subject/date/order held-out stress remains weak.",
            "A row-support action decoder can produce upload-safe route/S2 bundle candidates with strong local toxicity safety, but route-gain remains a tradeoff.",
            "A route-frontier action decoder now beats broad route nulls and matched frontier-score nulls while staying upload-safe, so the next LB sensor can test action-grade route translation directly.",
            "A route-toxicity fusion decoder now composes route-first selection with factorized broad-public/hard-world action-health; it is alive locally but still ranks below plain route-frontier as an LB sensor.",
            "The action-decoder ablation suite now ranks toxicity-first, support-first, route-first, and route-toxicity fusion decoders under one table; route-first currently leads the LB-sensor priority.",
            "A naive listener-invariant contrastive decoder is not ready yet; listener responsibility and route safety are weakly anti-aligned in current candidates.",
            "The toxicity field generalizes across many bad public anchors and beats matched nulls, but still misses a hard-world toxicity mode.",
            "Hard-world toxicity is anti-correlated with broad toxicity, so HS-JEPA action-health should be a factorized mixture rather than a scalar veto.",
            "The factorized toxicity decoder now produces upload-safe candidates that remove H088 top-toxic and broad-safe/H088-toxic selected cells in local diagnostics.",
            "The dual-safe expansion variant survives target-only and source-matched null stress, while the teacher-only variant is intentionally marked weaker under source-matched stress.",
        ],
        "what_the_adapter_does_not_prove": [
            "pure OG-only assignment",
            "action-grade portable hidden row-support recovery",
            "that masked row-support is already a deployment-grade action decoder",
            "that the row-support strict action decoder is safe without public/private LB observation",
            "that route-frontier action decoding is private-safe without public LB observation",
            "that route-toxicity fusion will beat plain route-frontier on public/private LB",
            "that the action-decoder ablation suite predicts public LB instead of prioritizing public-sensor experiments",
            "private leaderboard safety",
            "S2 as a universal human-sleep factor",
            "that public LB sensors can be used outside this competition",
            "that listener responsibility alone is an action-grade decoder",
            "that toxicity diagnostics prove private leaderboard safety",
            "that a hard-world mixture decoder will improve public/private LB before it is externally submitted",
        ],
        "paper_method_title": method["title"],
    }
    return report


def build_report_markdown(report: dict[str, object]) -> str:
    mapping_rows = ["| Core module | Sleep adapter instantiation | Evidence | Boundary |", "| --- | --- | --- | --- |"]
    for item in report["adapter_mapping"]:
        mapping_rows.append(
            f"| `{item['core_module']}` | {item['competition_adapter']} | {item['evidence']} | {item['boundary']} |"
        )

    roles = ["| Role | Output |", "| --- | --- |"]
    for role, name in report["role_outputs"].items():
        roles.append(f"| `{role}` | `{name}` |")

    factorized_rows = [
        "| Variant | Output | Changed cells | Joint safety | H088 top-toxic | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["factorized_toxicity_decoder_candidate"]["variants"].items():
        factorized_rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{item['changed_cells']}` | "
            f"`{fmt(item['joint_safety_mean'], 4)}` | `{fmt(item['hardworld_top_toxic_rate'], 4)}` | "
            f"`{item['upload_safe']}` |"
        )

    factorized_stress_rows = [
        "| Variant | Stress verdict | Target-null joint z | Source-null conflict p | Hard-toxic exposure | Conflict exposure |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["factorized_toxicity_decoder_stress_audit"]["variants"].items():
        factorized_stress_rows.append(
            f"| `{variant}` | `{item['verdict']}` | `{fmt(item['target_null_joint_safety_z'], 2)}` | "
            f"`{fmt(item['source_null_conflict_p'], 4)}` | `{fmt(item['hardworld_top_toxic_exposure'], 4)}` | "
            f"`{fmt(item['broad_safe_hardworld_toxic_exposure'], 4)}` |"
        )

    return "\n".join(
        [
            "# Sleep Competition Adapter Report",
            "",
            "이 문서는 HS-JEPA Core를 수면 생활습관 로그 대회에 적용하는 adapter를 설명한다.",
            "",
            "## Adapter Claim",
            "",
            report["adapter_claim"],
            "",
            "## Score Evidence",
            "",
            f"- Pre-public-equation best public LB: `{report['score_evidence']['pre_public_equation_best_public_lb']}`",
            f"- Current best public LB: `{report['score_evidence']['current_best_public_lb']}`",
            f"- Delta: `{report['score_evidence']['delta']}`",
            f"- Current best file: `{report['score_evidence']['current_best_file']}`",
            "",
            "## Core to Adapter Mapping",
            "",
            *mapping_rows,
            "",
            "## OG-only Assignment Probe",
            "",
            f"- Status: `{report['og_assignment_teacher_probe']['status']}`",
            f"- Pure OG row-cap2 recall: `{fmt(report['og_assignment_teacher_probe']['pure_og_row_cap2_mean_recall'], 4)}`",
            f"- Distilled row-cap2 recall: `{fmt(report['og_assignment_teacher_probe']['distilled_row_cap2_mean_recall'], 4)}`",
            f"- Listener/source upper-bound row-cap2 recall: `{fmt(report['og_assignment_teacher_probe']['listener_upper_bound_row_cap2_mean_recall'], 4)}`",
            "",
            report["og_assignment_teacher_probe"]["interpretation"],
            "",
            "## Assignment Gap Decomposition Probe",
            "",
            f"- Status: `{report['assignment_gap_decomposition_probe']['status']}`",
            f"- Mean best portable recall: `{fmt(report['assignment_gap_decomposition_probe']['mean_best_portable_recall'], 4)}`",
            f"- Mean target oracle recall: `{fmt(report['assignment_gap_decomposition_probe']['mean_target_oracle_recall'], 4)}`",
            f"- Mean row oracle + stage prior recall: `{fmt(report['assignment_gap_decomposition_probe']['mean_row_oracle_stage_recall'], 4)}`",
            f"- Mean row support gap: `{fmt(report['assignment_gap_decomposition_probe']['mean_row_support_gap'], 4)}`",
            "",
            report["assignment_gap_decomposition_probe"]["interpretation"],
            "",
            f"Next action: {report['assignment_gap_decomposition_probe']['next_action']}",
            "",
            "## Hidden Row-Support Sensor Probe",
            "",
            f"- Status: `{report['hidden_row_support_sensor_probe']['status']}`",
            f"- Best portable family: `{report['hidden_row_support_sensor_probe']['best_portable_family']}`",
            f"- Mean row AUC: `{fmt(report['hidden_row_support_sensor_probe']['best_portable_mean_row_auc'], 4)}`",
            f"- Mean row recall@K: `{fmt(report['hidden_row_support_sensor_probe']['best_portable_mean_row_recall_at_k'], 4)}`",
            f"- Mean cell recall with stage prior: `{fmt(report['hidden_row_support_sensor_probe']['best_portable_mean_cell_recall_with_stage_prior'], 4)}`",
            f"- Mean AUC z vs permuted train: `{fmt(report['hidden_row_support_sensor_probe']['best_portable_mean_auc_z_vs_permuted_train'], 4)}`",
            f"- Adapter minus portable cell-recall gap: `{fmt(report['hidden_row_support_sensor_probe']['adapter_minus_portable_cell_recall_gap'], 4)}`",
            "",
            report["hidden_row_support_sensor_probe"]["interpretation"],
            "",
            f"Next action: {report['hidden_row_support_sensor_probe']['next_action']}",
            "",
            "## Masked Row-Support Objective Probe",
            "",
            f"- Status: `{report['masked_row_support_objective_probe']['status']}`",
            f"- Full composite row AUC: `{fmt(report['masked_row_support_objective_probe']['full_composite_mean_row_auc'], 4)}`",
            f"- Full composite row recall@K: `{fmt(report['masked_row_support_objective_probe']['full_composite_mean_row_recall_at_k'], 4)}`",
            f"- Full composite cell recall: `{fmt(report['masked_row_support_objective_probe']['full_composite_mean_cell_recall'], 4)}`",
            f"- Human-only cell recall: `{fmt(report['masked_row_support_objective_probe']['human_only_mean_cell_recall'], 4)}`",
            f"- Prediction-only cell recall: `{fmt(report['masked_row_support_objective_probe']['prediction_only_mean_cell_recall'], 4)}`",
            f"- Route-masked cell recall: `{fmt(report['masked_row_support_objective_probe']['route_mask_mean_cell_recall'], 4)}`",
            f"- Group-heldout full row AUC: `{fmt(report['masked_row_support_objective_probe']['group_stress_full_mean_auc'], 4)}`",
            "",
            report["masked_row_support_objective_probe"]["interpretation"],
            "",
            f"Next action: {report['masked_row_support_objective_probe']['next_action']}",
            "",
            "## Row-Support Strict Action Decoder",
            "",
            f"- Status: `{report['row_support_strict_action_decoder']['status']}`",
            f"- Recommended variant: `{report['row_support_strict_action_decoder']['recommended_variant']}`",
            f"- Exploratory changed cells: `{report['row_support_strict_action_decoder']['exploratory_changed_cells']}`",
            f"- Exploratory safety z: `{fmt(report['row_support_strict_action_decoder']['exploratory_safety_z'], 2)}`",
            f"- Exploratory combined z: `{fmt(report['row_support_strict_action_decoder']['exploratory_combined_z'], 2)}`",
            f"- Exploratory mean route gain: `{fmt(report['row_support_strict_action_decoder']['exploratory_mean_route_gain'], 5)}`",
            "",
            report["row_support_strict_action_decoder"]["reason"],
            "",
            "## Route-Frontier Action Decoder",
            "",
            f"- Status: `{report['route_frontier_action_decoder']['status']}`",
            f"- Recommended variant: `{report['route_frontier_action_decoder']['recommended_variant']}`",
            "",
            report["route_frontier_action_decoder"]["reason"],
            "",
            "## Route-Toxicity Fusion Decoder",
            "",
            f"- Status: `{report['route_toxicity_fusion_decoder']['status']}`",
            f"- Recommended variant: `{report['route_toxicity_fusion_decoder']['recommended_variant']}`",
            "",
            report["route_toxicity_fusion_decoder"]["reason"],
            "",
            "## Decoder-Order Jury Solver",
            "",
            f"- Status: `{report['decoder_order_jury_solver']['status']}`",
            f"- Recommended LB sensor: `{report['decoder_order_jury_solver']['recommended_lb_sensor']}`",
            "",
            report["decoder_order_jury_solver"]["claim"],
            "",
            "## Action Decoder Ablation Suite",
            "",
            f"- Status: `{report['action_decoder_ablation_suite']['status']}`",
            f"- Recommended LB sensor: `{report['action_decoder_ablation_suite']['recommended_lb_sensor']}`",
            f"- Open big-bet sensor: `{report['action_decoder_ablation_suite']['big_bet_sensor']}`",
            "",
            report["action_decoder_ablation_suite"]["reason"],
            "",
            "## Listener-Invariant Contrastive Probe",
            "",
            f"- Status: `{report['listener_invariant_contrastive_probe']['status']}`",
            f"- Mean listener-route Spearman: `{fmt(report['listener_invariant_contrastive_probe']['mean_listener_route_spearman'], 4)}`",
            f"- Mean contrastive overlap: `{fmt(report['listener_invariant_contrastive_probe']['mean_contrastive_overlap_rate'], 4)}`",
            f"- Mean conflict rate: `{fmt(report['listener_invariant_contrastive_probe']['mean_high_listener_low_route_rate'], 4)}`",
            "",
            report["listener_invariant_contrastive_probe"]["interpretation"],
            "",
            "## Private-Safe Toxicity Probe",
            "",
            f"- Status: `{report['private_safe_toxicity_probe']['status']}`",
            f"- Mean leave-one-bad-anchor AUC: `{fmt(report['private_safe_toxicity_probe']['mean_loo_bad_anchor_auc'], 4)}`",
            f"- Worst leave-one-bad-anchor AUC: `{fmt(report['private_safe_toxicity_probe']['worst_loo_bad_anchor_auc'], 4)}`",
            f"- Selected safety z vs matched null: `{fmt(report['private_safe_toxicity_probe']['selected_safety_z_vs_matched_null'], 4)}`",
            "",
            report["private_safe_toxicity_probe"]["interpretation"],
            "",
            "## Hard-World Toxicity Factorization Probe",
            "",
            f"- Status: `{report['hardworld_toxicity_factorization_probe']['status']}`",
            f"- Broad toxicity -> H088 AUC: `{fmt(report['hardworld_toxicity_factorization_probe']['broad_predicts_hardworld_auc'], 4)}`",
            f"- Broad/H088 Spearman: `{fmt(report['hardworld_toxicity_factorization_probe']['broad_hardworld_spearman'], 4)}`",
            f"- Broad-safe but H088-toxic cells: `{report['hardworld_toxicity_factorization_probe']['broad_safe_hardworld_toxic_cells']}`",
            f"- Selected joint safety z: `{fmt(report['hardworld_toxicity_factorization_probe']['selected_joint_safety_z'], 4)}`",
            f"- Selected H088 top-toxic rate: `{fmt(report['hardworld_toxicity_factorization_probe']['selected_hardworld_top_toxic_rate'], 4)}` vs null `{fmt(report['hardworld_toxicity_factorization_probe']['null_hardworld_top_toxic_rate'], 4)}`",
            "",
            report["hardworld_toxicity_factorization_probe"]["interpretation"],
            "",
            "## Factorized Toxicity Decoder Candidate",
            "",
            f"- Architecture role: `{report['factorized_toxicity_decoder_candidate']['architecture_role']}`",
            f"- Core boundary: {report['factorized_toxicity_decoder_candidate']['core_boundary']}",
            "",
            *factorized_rows,
            "",
            "이 후보는 broad-public safety와 hard-world safety를 동시에 통과한 row-target action만 믿는 adapter-side decoder다. public 결과가 좋아지면 factorized action-health가 맞다는 신호이고, 나빠지면 factorization은 diagnostic으로는 유효하지만 아직 action-grade decoder는 아니라는 뜻이다.",
            "",
            "## Factorized Toxicity Decoder Stress Audit",
            "",
            f"- Status: `{report['factorized_toxicity_decoder_stress_audit']['status']}`",
            f"- Iterations: `{report['factorized_toxicity_decoder_stress_audit']['iterations']}`",
            "",
            *factorized_stress_rows,
            "",
            "`dual_safe_expansion`은 source-matched null까지 통과한 strict supported 후보이고, `teacher_dual_head`는 target-null에서는 강하지만 source-matched null이 약한 diagnostic 후보로 남긴다.",
            "",
            "## Role Outputs",
            "",
            *roles,
            "",
            "## 이 adapter가 증명하는 것",
            "",
            *[f"- {item}" for item in report["what_the_adapter_proves"]],
            "",
            "## 이 adapter가 아직 증명하지 못한 것",
            "",
            *[f"- {item}" for item in report["what_the_adapter_does_not_prove"]],
            "",
        ]
    )


def build_big_bet_markdown(bets: list[dict[str, object]]) -> str:
    rows = [
        "| Big bet | Worldview | Adapter move | Latest probe | Expected LB delta if true | Kill criterion |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for bet in bets:
        latest_probe = bet.get("latest_probe_status", "not_run")
        rows.append(
            f"| `{bet['name']}` | {bet['worldview']} | {bet['adapter_move']} | `{latest_probe}` | `{bet['expected_public_lb_delta_if_true']}` | {bet['kill_criterion']} |"
        )

    return "\n".join(
        [
            "# HS-JEPA Big-Bet Queue",
            "",
            "이 문서는 0.0001 개선용 조정이 아니라 HS-JEPA의 core/adaptor 구조를 바꿀 수 있는 큰 실험만 남긴다.",
            "",
            *rows,
            "",
            "## 우선순위",
            "",
            "1. `OG-only Human-State Assignment Teacher`: 성공하면 HS-JEPA의 범용성이 가장 크게 올라간다.",
            "2. `Hard-World Mixture Toxicity Decoder`: H088류 hard-world 독성을 broad toxicity와 분리한다.",
            "3. `Listener-Invariant Contrastive Decoder`: 현재 S2 bridge를 일반 action-health decoder로 확장한다.",
            "4. `Private-Safe Toxicity Field`: public-specific gain의 private risk를 줄이는 방향이다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    report = build_report()
    bets = build_big_bets(
        read_json(OG_PROBE_JSON),
        read_json(ASSIGNMENT_GAP_JSON),
        read_json(ROW_SUPPORT_SENSOR_JSON),
        read_json(MASKED_ROW_SUPPORT_JSON),
        read_json(ROW_SUPPORT_DECODER_JSON),
        read_json(ROUTE_FRONTIER_DECODER_JSON),
        read_json(ROUTE_TOXICITY_FUSION_DECODER_JSON),
        read_json(DECODER_ORDER_JURY_JSON),
        read_json(ACTION_DECODER_ABLATION_JSON),
        read_json(CONTRASTIVE_PROBE_JSON),
        read_json(PRIVATE_TOXICITY_PROBE_JSON),
        read_json(HARDWORLD_TOXICITY_PROBE_JSON),
    )
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_report_markdown(report), encoding="utf-8")
    BIG_BET_JSON.write_text(
        json.dumps(
            {
                "package": "HS-JEPA Big-Bet Queue",
                "status": "big_bet_queue_ready",
                "bets": bets,
                "count": len(bets),
            },
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        ),
        encoding="utf-8",
    )
    BIG_BET_MD.write_text(build_big_bet_markdown(bets), encoding="utf-8")
    result = {
        "adapter_report_json": str(REPORT_JSON.resolve()),
        "adapter_report_md": str(REPORT_MD.resolve()),
        "big_bet_json": str(BIG_BET_JSON.resolve()),
        "big_bet_md": str(BIG_BET_MD.resolve()),
        "status": report["status"],
        "big_bet_count": len(bets),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
