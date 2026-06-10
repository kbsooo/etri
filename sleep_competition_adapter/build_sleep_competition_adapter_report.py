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
DECODER_BOUNDARY_TOMOGRAPHY_JSON = OUT / "decoder_boundary_tomography_solver" / "decoder_boundary_tomography_readout.json"
CORE_MEDIATED_RELEASE_JSON = OUT / "core_mediated_action_release" / "core_mediated_action_release_readout.json"
CORE_RELEASE_ABLATION_JSON = OUT / "core_release_ablation_probe" / "core_release_ablation_probe_readout.json"
CORE_HEALTH_CALIBRATED_JSON = OUT / "core_health_calibrated_release" / "core_health_calibrated_release_readout.json"
CROSS_LISTENER_TRANSPORT_JSON = OUT / "cross_listener_transport_decoder" / "cross_listener_transport_readout.json"
COUNTERFACTUAL_LISTENER_DROPOUT_JSON = (
    OUT / "counterfactual_listener_dropout_solver" / "counterfactual_listener_dropout_readout.json"
)
SPECTRAL_PUBLIC_TANGENT_JSON = (
    OUT / "spectral_public_tangent_solver" / "spectral_public_tangent_readout.json"
)
NEGATIVE_TANGENT_INVARIANT_JSON = (
    OUT
    / "negative_tangent_invariant_projection_solver"
    / "negative_tangent_invariant_projection_readout.json"
)
LB_CONDITIONED_RESPONSIBILITY_JSON = (
    OUT
    / "lb_conditioned_responsibility_solver"
    / "lb_conditioned_responsibility_readout.json"
)
MIXTURE_LISTENER_RESPONSIBILITY_JSON = (
    OUT
    / "mixture_listener_responsibility_solver"
    / "mixture_listener_responsibility_readout.json"
)
PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON = (
    OUT
    / "public_private_subset_tomography_solver"
    / "public_private_subset_tomography_readout.json"
)
ANTI_LISTENER_TOXICITY_JSON = (
    OUT
    / "anti_listener_toxicity_equation_solver"
    / "anti_listener_toxicity_equation_readout.json"
)
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
    decoder_boundary_tomography: dict[str, object],
    core_mediated_release: dict[str, object],
    core_release_ablation: dict[str, object],
    core_health_calibrated: dict[str, object],
    cross_listener_transport: dict[str, object],
    counterfactual_listener_dropout: dict[str, object],
    spectral_public_tangent: dict[str, object],
    negative_tangent_invariant: dict[str, object],
    lb_conditioned_responsibility: dict[str, object],
    mixture_listener_responsibility: dict[str, object],
    public_private_subset_tomography: dict[str, object],
    anti_listener_toxicity: dict[str, object],
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
    decoder_boundary_tomography_verdict = (
        decoder_boundary_tomography.get("verdict", {})
        if isinstance(decoder_boundary_tomography.get("verdict"), dict)
        else {}
    )
    core_mediated_verdict = (
        core_mediated_release.get("verdict", {})
        if isinstance(core_mediated_release.get("verdict"), dict)
        else {}
    )
    core_release_ablation_verdict = (
        core_release_ablation.get("verdict", {})
        if isinstance(core_release_ablation.get("verdict"), dict)
        else {}
    )
    core_health_calibrated_verdict = (
        core_health_calibrated.get("verdict", {})
        if isinstance(core_health_calibrated.get("verdict"), dict)
        else {}
    )
    cross_listener_verdict = (
        cross_listener_transport.get("verdict", {})
        if isinstance(cross_listener_transport.get("verdict"), dict)
        else {}
    )
    listener_dropout_verdict = (
        counterfactual_listener_dropout.get("verdict", {})
        if isinstance(counterfactual_listener_dropout.get("verdict"), dict)
        else {}
    )
    spectral_tangent_verdict = (
        spectral_public_tangent.get("verdict", {})
        if isinstance(spectral_public_tangent.get("verdict"), dict)
        else {}
    )
    negative_projection_verdict = (
        negative_tangent_invariant.get("verdict", {})
        if isinstance(negative_tangent_invariant.get("verdict"), dict)
        else {}
    )
    lb_responsibility_verdict = (
        lb_conditioned_responsibility.get("verdict", {})
        if isinstance(lb_conditioned_responsibility.get("verdict"), dict)
        else {}
    )
    mixture_listener_verdict = (
        mixture_listener_responsibility.get("verdict", {})
        if isinstance(mixture_listener_responsibility.get("verdict"), dict)
        else {}
    )
    subset_tomography_verdict = (
        public_private_subset_tomography.get("verdict", {})
        if isinstance(public_private_subset_tomography.get("verdict"), dict)
        else {}
    )
    anti_listener_verdict = (
        anti_listener_toxicity.get("verdict", {})
        if isinstance(anti_listener_toxicity.get("verdict"), dict)
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
    bets = [
        {
            "id": "anti_listener_toxicity_equation_solver",
            "name": "Anti-Listener Toxicity Equation Solver",
            "worldview": "Listener responsibility is not an action generator; failed listener releases define a toxic direction that must be inverted or vetoed by action-health.",
            "core_modules_exercised": [
                "listener_responsibility",
                "action_health_decoder",
                "external_listener_tomography",
                "public_private_equation",
                "anti_shortcut_validation",
            ],
            "adapter_move": "Use CrossListener, target-listener lift, H088 hard-world, and other public-bad anchors as toxic teachers, then release inverse row-target moves that also satisfy private-safety and route/subject invariants.",
            "why_big": "If this wins LB, HS-JEPA gains a stronger paper thesis: a listener can be informative precisely because it failed as a generator, and action-health must learn anti-listener equations.",
            "expected_public_lb_delta_if_true": -0.014,
            "latest_probe_status": anti_listener_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": anti_listener_verdict.get("recommended_variant"),
                "ranking": anti_listener_verdict.get("ranking"),
                "source_fit": anti_listener_toxicity.get("source_fit"),
                "cell_count": anti_listener_toxicity.get("cell_count"),
            },
            "kill_criterion": "Inverse, private-safe, Q2/S2, subset-veto, and boundary-probe variants all fail public LB, meaning listener failures are diagnostic but not invertible action-health equations.",
        },
        {
            "id": "public_private_subset_tomography_solver",
            "name": "Public/Private Subset Tomography Solver",
            "worldview": "Scalar public feedback is generated by public subset inclusion times hidden label direction, while private action-health decides whether the move is safe outside that listener.",
            "core_modules_exercised": [
                "listener_responsibility",
                "external_listener_tomography",
                "action_health_decoder",
                "public_private_equation",
                "target_route_decoder",
            ],
            "adapter_move": "Decompose LB-conditioned responsibility into public-inclusion, label-direction, private-safety, and toxicity fields, then release row-target actions under several hidden-world assumptions.",
            "why_big": "If this wins LB, HS-JEPA gains a paper-level contribution: external scalar feedback can be factorized into subset membership and hidden label direction before action release.",
            "expected_public_lb_delta_if_true": -0.012,
            "latest_probe_status": subset_tomography_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": subset_tomography_verdict.get("recommended_variant"),
                "ranking": subset_tomography_verdict.get("ranking"),
                "source_fit": public_private_subset_tomography.get("source_fit"),
                "cell_count": public_private_subset_tomography.get("cell_count"),
            },
            "kill_criterion": "Public-first, private-safe, boundary-probe, Q/S split, and orthogonal-private variants all fail public LB, meaning scalar public feedback is descriptive but not enough to identify an action-grade public/private subset equation.",
        },
        {
            "id": "mixture_listener_responsibility_solver",
            "name": "Mixture-Listener Responsibility Solver",
            "worldview": "The public LB is not one listener; it is a scalar readout of multiple latent listener heads, and Q/S actions may need different heads.",
            "core_modules_exercised": [
                "listener_responsibility",
                "latent_listener_factorization",
                "target_route_decoder",
                "action_health_decoder",
                "public_private_equation",
            ],
            "adapter_move": "Factor previous public-score action deltas into spectral listener heads, then release row-target actions by consensus, conflict, or target-specific Q/S listener routing.",
            "why_big": "If this wins LB, HS-JEPA gains a stronger paper contribution than scalar responsibility: human-state actions should be decoded through latent listener mixtures, not a single public response gradient.",
            "expected_public_lb_delta_if_true": -0.010,
            "latest_probe_status": mixture_listener_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": mixture_listener_verdict.get("recommended_variant"),
                "ranking": mixture_listener_verdict.get("ranking"),
                "mixture_fit": mixture_listener_responsibility.get("mixture_fit"),
                "cell_count": mixture_listener_responsibility.get("cell_count"),
            },
            "kill_criterion": "Target-split, consensus, and residual-conflict variants all fail public LB, meaning public LB anchors are too scalar/noisy to identify action-grade latent listeners.",
        },
        {
            "id": "lb_conditioned_responsibility_solver",
            "name": "LB-Conditioned Responsibility Solver",
            "worldview": "The public LB can be treated as an external listener whose scalar observations reveal row-target action responsibility.",
            "core_modules_exercised": [
                "listener_responsibility",
                "action_health_decoder",
                "invariant_energy",
                "public_private_equation",
            ],
            "adapter_move": "Fit a ridge/LOO responsibility equation from public-score action deltas, invert harmful row-target directions, and release only upload-safe invariant-valid actions.",
            "why_big": "If this wins LB, HS-JEPA gains a paper-level contribution: listener responsibility can be inferred from scalar outcomes, not only explicit labels or target heads.",
            "expected_public_lb_delta_if_true": -0.008,
            "latest_probe_status": lb_responsibility_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": lb_responsibility_verdict.get("recommended_variant"),
                "ranking": lb_responsibility_verdict.get("ranking"),
                "fit": lb_conditioned_responsibility.get("fit"),
                "responsibility_cells": lb_conditioned_responsibility.get("responsibility_cells"),
            },
            "kill_criterion": "Pure-gradient and invariant-safe variants both fail public LB, meaning scalar public listener responsibility is descriptive but not enough without a hidden public/private row-support assignment.",
        },
        {
            "id": "negative_tangent_invariant_projection_solver",
            "name": "Negative Tangent Invariant Projection Solver",
            "worldview": "A negative public representation is useful only when its inverse can be projected onto label-valid human-state invariants.",
            "core_modules_exercised": [
                "action_health_decoder",
                "invariant_energy",
                "listener_responsibility",
                "anti_shortcut_validation",
            ],
            "adapter_move": "Take the low-rank public-bad tangent, choose anti-bad row-target actions, and greedily release only cells that preserve train target-route and subject-prior energy.",
            "why_big": "If this wins LB, HS-JEPA gains a general contribution: failed actions define negative representations, but action-grade decoding requires invariant projection.",
            "expected_public_lb_delta_if_true": -0.006,
            "latest_probe_status": negative_projection_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_variant": negative_projection_verdict.get("recommended_variant"),
                "ranking": negative_projection_verdict.get("ranking"),
                "spectral": negative_tangent_invariant.get("spectral"),
                "projected_cells": negative_tangent_invariant.get("projected_cells"),
            },
            "kill_criterion": "Projection candidates worsen public LB like naive anti-tangent probes, meaning public-bad geometry is diagnostic but not yet an invertible action equation even under target/subject invariants.",
        },
        {
            "id": "spectral_public_tangent_solver",
            "name": "Spectral Public-Tangent Solver",
            "worldview": "Known post-H057 public failures are not independent mistakes; they collapse onto a low-rank public-bad action tangent.",
            "core_modules_exercised": [
                "action_health_decoder",
                "anti_shortcut_validation",
                "listener_responsibility",
                "public_private_equation",
            ],
            "adapter_move": "Infer the dominant bad public-loss tangent from failed submissions, then release anti-tangent or orthogonal private-residual row-target actions.",
            "why_big": "If anti-tangent pressure improves LB, HS-JEPA gains a falsifiable action-equation thesis: failures define a negative representation that can be inverted or avoided.",
            "expected_public_lb_delta_if_true": -0.004,
            "latest_probe_status": spectral_public_tangent.get("status"),
            "latest_probe_evidence": {
                "first_mode_variance": spectral_public_tangent.get("spectral", {}).get("first_mode_variance"),
                "top5_cumulative_variance": spectral_public_tangent.get("spectral", {}).get("top5_cumulative_variance"),
                "recommended_information_sensor": spectral_tangent_verdict.get("recommended_information_sensor"),
                "recommended_counter_sensor": spectral_tangent_verdict.get("recommended_counter_sensor"),
                "pool": spectral_public_tangent.get("pool"),
            },
            "kill_criterion": "Anti-tangent and orthogonal residual sensors both worsen public LB, meaning the low-rank tangent is descriptive but not an invertible action equation.",
        },
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
            "id": "decoder_boundary_tomography_solver",
            "name": "Decoder Boundary Tomography Solver",
            "worldview": "The strict cross-decoder jury may be correct but too conservative; rejected cells split into weak consensus, route-only, and fusion-only worlds.",
            "core_modules_exercised": ["invariant_energy", "action_health_decoder", "anti_shortcut_validation"],
            "adapter_move": "Keep the strict jury base, then add only boundary cells by class to see which action-release frontier public LB accepts.",
            "why_big": "If consensus-shadow cells improve LB, HS-JEPA gets a sharper release rule: weak agreement can be released when disagreement is zero.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": decoder_boundary_tomography_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_lb_sensor": decoder_boundary_tomography_verdict.get("recommended_lb_sensor"),
                "claim": decoder_boundary_tomography_verdict.get("claim"),
                "inventory": decoder_boundary_tomography.get("boundary_inventory"),
            },
            "kill_criterion": "All boundary probes worsen public LB, meaning strict cross-decoder consensus is the current safe frontier.",
        },
        {
            "id": "core_mediated_action_release",
            "name": "Core-Mediated Action Release",
            "worldview": "A reusable HS-JEPA core should mediate real row-target actions before the sleep adapter releases them.",
            "core_modules_exercised": [
                "context_encoder",
                "listener_responsibility",
                "action_health_decoder",
                "invariant_energy",
                "anti_shortcut_validation",
            ],
            "adapter_move": "Convert decoder-order and boundary-tomography cells into ContextView/ListenerPrototype/CandidateAction objects, then let HSJEPACore release or veto them.",
            "why_big": "If this beats the strict jury, HS-JEPA is no longer only an explanatory wrapper; its generic core release equation is action-grade for the adapter.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": core_mediated_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_lb_sensor": core_mediated_verdict.get("recommended_lb_sensor"),
                "claim": core_mediated_verdict.get("claim"),
                "inventory": core_mediated_release.get("cell_inventory"),
            },
            "kill_criterion": "Core-mediated candidates underperform the strict jury and boundary tomography, meaning generic core release is diagnostic but not yet the competition action equation.",
        },
        {
            "id": "core_release_ablation_probe",
            "name": "Core Release Ablation Probe",
            "worldview": "A real HS-JEPA architecture must expose which core module over-constrains or protects row-target action release.",
            "core_modules_exercised": ["listener_responsibility", "action_health_decoder", "invariant_energy"],
            "adapter_move": "Run the same real adapter cells through full-core, no-listener, no-action-health, no-invariant, and invariant-only release policies.",
            "why_big": "If a removed-module policy beats full-core on public LB, the architecture learns which JEPA constraint is too conservative; if it loses, full-core has action-grade evidence.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": core_release_ablation_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_lb_candidate": core_release_ablation_verdict.get("recommended_lb_candidate"),
                "recommended_architecture_sensor": core_release_ablation_verdict.get("recommended_architecture_sensor"),
                "recommended_negative_control": core_release_ablation_verdict.get("recommended_negative_control"),
                "claim": core_release_ablation_verdict.get("claim"),
            },
            "kill_criterion": "All module-removal probes match full-core and public LB cannot distinguish them, meaning this ablation axis is not the current bottleneck.",
        },
        {
            "id": "core_health_calibrated_release",
            "name": "Core-Health Calibrated Release",
            "worldview": "Dataset-free HS-JEPA action-health failure modes should calibrate the real sleep-adapter action boundary.",
            "core_modules_exercised": [
                "context_encoder",
                "listener_responsibility",
                "action_health_decoder",
                "invariant_energy",
                "core_benchmark_fp_calibration",
            ],
            "adapter_move": "Use the core module benchmark's action-health false-positive lift as a release prior for real row-target cells.",
            "why_big": "If guarded release survives LB, HS-JEPA gains a portable mechanism-to-adapter bridge instead of only a competition-specific decoder.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": core_health_calibrated_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_lb_candidate": core_health_calibrated_verdict.get("recommended_lb_candidate"),
                "recommended_big_bet_sensor": core_health_calibrated_verdict.get("recommended_big_bet_sensor"),
                "recommended_pressure_sensor": core_health_calibrated_verdict.get("recommended_pressure_sensor"),
                "top_ranked_upload_safe": core_health_calibrated_verdict.get("top_ranked_upload_safe"),
                "benchmark_calibration": core_health_calibrated.get("benchmark_calibration"),
            },
            "kill_criterion": "Guarded release loses to relaxed pressure or to strict jury, meaning the current generic action-health prior is useful diagnostically but not action-grade for this adapter.",
        },
        {
            "id": "cross_listener_transport_decoder",
            "name": "Cross-Listener Transport Decoder",
            "worldview": "Target-listener posterior is not an action generator; it is a transport calibrator over route/fusion/core-safe actions.",
            "core_modules_exercised": ["listener_responsibility", "action_health_decoder", "invariant_energy"],
            "adapter_move": "Reuse the failed target-listener lift as a boundary prior, then only move S-stage cells that route/fusion/core decoders already expose.",
            "why_big": "If this survives LB, HS-JEPA gains a reusable listener-as-calibrator rule instead of treating failed listener routes as dead features.",
            "expected_public_lb_delta_if_true": -0.002,
            "latest_probe_status": cross_listener_verdict.get("status"),
            "latest_probe_evidence": {
                "recommended_lb_sensor": cross_listener_verdict.get("recommended_lb_sensor"),
                "recommended_big_bet": cross_listener_verdict.get("recommended_big_bet"),
                "negative_sensor": cross_listener_transport.get("negative_sensor"),
                "claim": cross_listener_verdict.get("claim"),
            },
            "kill_criterion": "Public LB says listener-confirmed transport underperforms strict jury/core-health, meaning listener posterior remains diagnostic and not action-boundary evidence.",
        },
        {
            "id": "counterfactual_listener_dropout_solver",
            "name": "Counterfactual Listener-Dropout Solver",
            "worldview": "A healthy HS-JEPA action should survive when one listener is masked, while failed public sensors become action-toxicity evidence rather than discarded submissions.",
            "core_modules_exercised": [
                "listener_responsibility",
                "action_health_decoder",
                "invariant_energy",
                "anti_shortcut_validation",
            ],
            "adapter_move": "Score route/fusion/listener actions under counterfactual listener dropout, then compare aggressive same-direction release against toxic-direction inversion.",
            "why_big": "This turns HS-JEPA from a set of empirical adapters into a falsifiable architecture claim: robust action health is listener-invariant, not single-head score chasing.",
            "expected_public_lb_delta_if_true": -0.003,
            "latest_probe_status": counterfactual_listener_dropout.get("status"),
            "latest_probe_evidence": {
                "recommended_information_sensor": listener_dropout_verdict.get("recommended_information_sensor"),
                "recommended_thesis_sensor": listener_dropout_verdict.get("recommended_thesis_sensor"),
                "claim": listener_dropout_verdict.get("claim"),
                "top_ranked": counterfactual_listener_dropout.get("ranking", [])[:2],
            },
            "kill_criterion": "Aggressive listener-dropout and inversion both fail public LB, meaning listener-dropout geometry is not enough to solve the public/private row-target equation.",
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
    ]
    priority_order = {
        "anti_listener_toxicity_equation_solver": 0,
        "public_private_subset_tomography_solver": 1,
        "mixture_listener_responsibility_solver": 2,
        "lb_conditioned_responsibility_solver": 3,
        "negative_tangent_invariant_projection_solver": 4,
        "spectral_public_tangent_solver": 5,
        "counterfactual_listener_dropout_solver": 6,
        "action_decoder_ablation_suite": 7,
        "og_only_assignment_teacher": 8,
    }
    return sorted(
        bets,
        key=lambda bet: (
            priority_order.get(str(bet["id"]), 100),
            float(bet.get("expected_public_lb_delta_if_true") or 0.0),
        ),
    )


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
    decoder_boundary_tomography_verdict = decoder_boundary_tomography.get("verdict", {})
    core_mediated_verdict = core_mediated_release.get("verdict", {})
    core_release_ablation_verdict = core_release_ablation.get("verdict", {})
    core_health_calibrated_verdict = core_health_calibrated.get("verdict", {})
    cross_listener_verdict = cross_listener_transport.get("verdict", {})
    listener_dropout_verdict = counterfactual_listener_dropout.get("verdict", {})
    spectral_tangent_verdict = spectral_public_tangent.get("verdict", {})
    negative_projection_verdict = negative_tangent_invariant.get("verdict", {})
    lb_responsibility_verdict = lb_conditioned_responsibility.get("verdict", {})
    mixture_listener_verdict = mixture_listener_responsibility.get("verdict", {})
    subset_tomography_verdict = public_private_subset_tomography.get("verdict", {})
    anti_listener_verdict = anti_listener_toxicity.get("verdict", {})
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
        "decoder_boundary_tomography_solver": {
            "status": decoder_boundary_tomography_verdict.get("status"),
            "recommended_lb_sensor": decoder_boundary_tomography_verdict.get("recommended_lb_sensor"),
            "claim": decoder_boundary_tomography_verdict.get("claim"),
            "failure_interpretation": decoder_boundary_tomography_verdict.get("failure_interpretation"),
            "boundary_inventory": decoder_boundary_tomography.get("boundary_inventory"),
            "top_ranked": decoder_boundary_tomography.get("ranking", [])[:3],
        },
        "core_mediated_action_release": {
            "status": core_mediated_verdict.get("status"),
            "recommended_lb_sensor": core_mediated_verdict.get("recommended_lb_sensor"),
            "claim": core_mediated_verdict.get("claim"),
            "failure_interpretation": core_mediated_verdict.get("failure_interpretation"),
            "cell_inventory": core_mediated_release.get("cell_inventory"),
            "top_ranked": core_mediated_release.get("ranking", [])[:3],
        },
        "core_release_ablation_probe": {
            "status": core_release_ablation_verdict.get("status"),
            "recommended_lb_candidate": core_release_ablation_verdict.get("recommended_lb_candidate"),
            "recommended_architecture_sensor": core_release_ablation_verdict.get("recommended_architecture_sensor"),
            "recommended_negative_control": core_release_ablation_verdict.get("recommended_negative_control"),
            "claim": core_release_ablation_verdict.get("claim"),
            "failure_interpretation": core_release_ablation_verdict.get("failure_interpretation"),
            "top_ranked": core_release_ablation.get("ranking", [])[:3],
            "findings": core_release_ablation.get("findings", []),
        },
        "core_health_calibrated_release": {
            "status": core_health_calibrated_verdict.get("status"),
            "recommended_lb_candidate": core_health_calibrated_verdict.get("recommended_lb_candidate"),
            "recommended_big_bet_sensor": core_health_calibrated_verdict.get("recommended_big_bet_sensor"),
            "recommended_pressure_sensor": core_health_calibrated_verdict.get("recommended_pressure_sensor"),
            "top_ranked_upload_safe": core_health_calibrated_verdict.get("top_ranked_upload_safe"),
            "claim": core_health_calibrated_verdict.get("claim"),
            "failure_interpretation": core_health_calibrated_verdict.get("failure_interpretation"),
            "benchmark_calibration": core_health_calibrated.get("benchmark_calibration"),
            "top_ranked": core_health_calibrated.get("ranking", [])[:3],
        },
        "cross_listener_transport_decoder": {
            "status": cross_listener_verdict.get("status"),
            "recommended_lb_sensor": cross_listener_verdict.get("recommended_lb_sensor"),
            "recommended_big_bet": cross_listener_verdict.get("recommended_big_bet"),
            "negative_sensor": cross_listener_transport.get("negative_sensor"),
            "claim": cross_listener_verdict.get("claim"),
            "failure_interpretation": cross_listener_verdict.get("failure_interpretation"),
            "top_ranked": cross_listener_transport.get("ranking", [])[:3],
        },
        "counterfactual_listener_dropout_solver": {
            "status": counterfactual_listener_dropout.get("status"),
            "recommended_information_sensor": listener_dropout_verdict.get("recommended_information_sensor"),
            "recommended_thesis_sensor": listener_dropout_verdict.get("recommended_thesis_sensor"),
            "claim": listener_dropout_verdict.get("claim"),
            "failure_interpretation": listener_dropout_verdict.get("failure_interpretation"),
            "negative_sensor_files": counterfactual_listener_dropout.get("negative_sensor_files"),
            "positive_source_files": counterfactual_listener_dropout.get("positive_source_files"),
            "top_ranked": counterfactual_listener_dropout.get("ranking", [])[:3],
        },
        "spectral_public_tangent_solver": {
            "status": spectral_public_tangent.get("status"),
            "claim": spectral_tangent_verdict.get("claim") or spectral_public_tangent.get("claim"),
            "recommended_information_sensor": spectral_tangent_verdict.get("recommended_information_sensor"),
            "recommended_counter_sensor": spectral_tangent_verdict.get("recommended_counter_sensor"),
            "failure_interpretation": spectral_tangent_verdict.get("failure_interpretation"),
            "spectral": spectral_public_tangent.get("spectral"),
            "pool": spectral_public_tangent.get("pool"),
            "top_ranked": spectral_public_tangent.get("ranking", [])[:3],
        },
        "negative_tangent_invariant_projection_solver": {
            "experiment": negative_tangent_invariant.get("experiment"),
            "architecture_role": negative_tangent_invariant.get("architecture_role"),
            "core_claim": negative_tangent_invariant.get("core_claim"),
            "status": negative_projection_verdict.get("status"),
            "recommended_variant": negative_projection_verdict.get("recommended_variant"),
            "reason": negative_projection_verdict.get("reason"),
            "spectral": negative_tangent_invariant.get("spectral"),
            "projected_cells": negative_tangent_invariant.get("projected_cells"),
            "ranking": negative_projection_verdict.get("ranking"),
            "variants": {
                name: {
                    "submission_file": item.get("submission", {}).get("submission_file"),
                    "changed_cells": item.get("submission", {}).get("changed_cells"),
                    "selected_rows": item.get("submission", {}).get("selected_rows"),
                    "bad_tangent_cosine": item.get("metrics", {}).get("bad_tangent_cosine"),
                    "mean_incremental_energy_delta": item.get("metrics", {}).get("mean_incremental_energy_delta"),
                    "mean_subject_energy_delta": item.get("metrics", {}).get("mean_subject_energy_delta"),
                    "upload_safe": item.get("submission", {}).get("validation", {}).get("upload_safe"),
                }
                for name, item in negative_tangent_invariant.get("variants", {}).items()
                if isinstance(item, dict)
            },
        },
        "lb_conditioned_responsibility_solver": {
            "experiment": lb_conditioned_responsibility.get("experiment"),
            "architecture_role": lb_conditioned_responsibility.get("architecture_role"),
            "core_claim": lb_conditioned_responsibility.get("core_claim"),
            "status": lb_responsibility_verdict.get("status"),
            "recommended_variant": lb_responsibility_verdict.get("recommended_variant"),
            "reason": lb_responsibility_verdict.get("reason"),
            "spectral": lb_conditioned_responsibility.get("spectral"),
            "fit": lb_conditioned_responsibility.get("fit"),
            "responsibility_cells": lb_conditioned_responsibility.get("responsibility_cells"),
            "ranking": lb_responsibility_verdict.get("ranking"),
            "variants": {
                name: {
                    "submission_file": item.get("submission", {}).get("submission_file"),
                    "changed_cells": item.get("submission", {}).get("changed_cells"),
                    "selected_rows": item.get("submission", {}).get("selected_rows"),
                    "sum_predicted_loss_delta": item.get("metrics", {}).get("sum_predicted_loss_delta"),
                    "mean_sign_stability": item.get("metrics", {}).get("mean_sign_stability"),
                    "mean_incremental_energy_delta": item.get("metrics", {}).get("mean_incremental_energy_delta"),
                    "bad_tangent_cosine": item.get("metrics", {}).get("bad_tangent_cosine"),
                    "upload_safe": item.get("submission", {}).get("validation", {}).get("upload_safe"),
                }
                for name, item in lb_conditioned_responsibility.get("variants", {}).items()
                if isinstance(item, dict)
            },
        },
        "mixture_listener_responsibility_solver": {
            "experiment": mixture_listener_responsibility.get("experiment"),
            "architecture_role": mixture_listener_responsibility.get("architecture_role"),
            "core_claim": mixture_listener_responsibility.get("core_claim"),
            "status": mixture_listener_verdict.get("status"),
            "recommended_variant": mixture_listener_verdict.get("recommended_variant"),
            "reason": mixture_listener_verdict.get("reason"),
            "anchor_count": mixture_listener_responsibility.get("anchor_count"),
            "cell_count": mixture_listener_responsibility.get("cell_count"),
            "spectral": mixture_listener_responsibility.get("spectral"),
            "mixture_fit": mixture_listener_responsibility.get("mixture_fit"),
            "ranking": mixture_listener_verdict.get("ranking"),
            "variants": {
                name: {
                    "submission_file": item.get("submission", {}).get("submission_file"),
                    "changed_cells": item.get("submission", {}).get("changed_cells"),
                    "selected_rows": item.get("submission", {}).get("selected_rows"),
                    "sum_predicted_scalar_delta": item.get("metrics", {}).get("sum_predicted_scalar_delta"),
                    "sum_predicted_total_mode_delta": item.get("metrics", {}).get("sum_predicted_total_mode_delta"),
                    "mean_conflict_score": item.get("metrics", {}).get("mean_conflict_score"),
                    "mean_mode_confidence": item.get("metrics", {}).get("mean_mode_confidence"),
                    "bad_tangent_cosine": item.get("metrics", {}).get("bad_tangent_cosine"),
                    "upload_safe": item.get("submission", {}).get("validation", {}).get("upload_safe"),
                }
                for name, item in mixture_listener_responsibility.get("variants", {}).items()
                if isinstance(item, dict)
            },
        },
        "public_private_subset_tomography_solver": {
            "experiment": public_private_subset_tomography.get("experiment"),
            "architecture_role": public_private_subset_tomography.get("architecture_role"),
            "core_claim": public_private_subset_tomography.get("core_claim"),
            "status": subset_tomography_verdict.get("status"),
            "recommended_variant": subset_tomography_verdict.get("recommended_variant"),
            "reason": subset_tomography_verdict.get("reason"),
            "anchor_count": public_private_subset_tomography.get("anchor_count"),
            "cell_count": public_private_subset_tomography.get("cell_count"),
            "source_fit": public_private_subset_tomography.get("source_fit"),
            "ranking": subset_tomography_verdict.get("ranking"),
            "variants": {
                name: {
                    "submission_file": item.get("submission", {}).get("submission_file"),
                    "changed_cells": item.get("submission", {}).get("changed_cells"),
                    "selected_rows": item.get("submission", {}).get("selected_rows"),
                    "mean_public_inclusion": item.get("metrics", {}).get("mean_public_inclusion"),
                    "mean_label_confidence": item.get("metrics", {}).get("mean_label_confidence"),
                    "mean_private_safety": item.get("metrics", {}).get("mean_private_safety"),
                    "mean_toxicity": item.get("metrics", {}).get("mean_toxicity"),
                    "sum_predicted_public_delta": item.get("metrics", {}).get("sum_predicted_public_delta"),
                    "bad_tangent_cosine": item.get("metrics", {}).get("bad_tangent_cosine"),
                    "upload_safe": item.get("submission", {}).get("validation", {}).get("upload_safe"),
                }
                for name, item in public_private_subset_tomography.get("variants", {}).items()
                if isinstance(item, dict)
            },
        },
        "anti_listener_toxicity_equation_solver": {
            "experiment": anti_listener_toxicity.get("experiment"),
            "architecture_role": anti_listener_toxicity.get("architecture_role"),
            "thesis": anti_listener_toxicity.get("thesis"),
            "status": anti_listener_verdict.get("status"),
            "recommended_variant": anti_listener_verdict.get("recommended_variant"),
            "interpretation": anti_listener_verdict.get("interpretation"),
            "toxic_anchor_count": sum(
                1 for item in anti_listener_toxicity.get("toxic_anchors", []) if item.get("available")
            ),
            "cell_count": anti_listener_toxicity.get("cell_count"),
            "source_fit": anti_listener_toxicity.get("source_fit"),
            "ranking": anti_listener_verdict.get("ranking"),
            "variants": {
                name: {
                    "submission_file": item.get("submission", {}).get("submission_file"),
                    "changed_cells": item.get("submission", {}).get("changed_cells"),
                    "mean_listener_inverse": item.get("metrics", {}).get("mean_listener_inverse"),
                    "mean_listener_safety": item.get("metrics", {}).get("mean_listener_safety"),
                    "mean_private_safety": item.get("metrics", {}).get("mean_private_safety"),
                    "mean_hardworld_toxicity": item.get("metrics", {}).get("mean_hardworld_toxicity"),
                    "mean_broad_toxicity": item.get("metrics", {}).get("mean_broad_toxicity"),
                    "sum_predicted_public_delta": item.get("metrics", {}).get("sum_predicted_public_delta"),
                    "upload_safe": item.get("submission", {}).get("validation", {}).get("upload_safe"),
                }
                for name, item in anti_listener_toxicity.get("variants", {}).items()
                if isinstance(item, dict)
            },
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
            "Decoder boundary tomography separates strict-jury rejects into consensus-shadow, route-only, and fusion-only cells; consensus-shadow is the safest next too-conservative-jury sensor.",
            "The action-decoder ablation suite now ranks toxicity-first, support-first, route-first, and route-toxicity fusion decoders under one table; route-first currently leads the LB-sensor priority.",
            "A naive listener-invariant contrastive decoder is not ready yet; listener responsibility and route safety are weakly anti-aligned in current candidates.",
            "The toxicity field generalizes across many bad public anchors and beats matched nulls, but still misses a hard-world toxicity mode.",
            "Hard-world toxicity is anti-correlated with broad toxicity, so HS-JEPA action-health should be a factorized mixture rather than a scalar veto.",
            "The factorized toxicity decoder now produces upload-safe candidates that remove H088 top-toxic and broad-safe/H088-toxic selected cells in local diagnostics.",
            "The dual-safe expansion variant survives target-only and source-matched null stress, while the teacher-only variant is intentionally marked weaker under source-matched stress.",
            "Core release ablation now makes listener responsibility, action-health, and invariant energy falsifiable on real sleep-adapter actions rather than only synthetic core examples.",
            "Core-health calibrated release now uses dataset-free action-health false-positive lift as a real adapter release prior, connecting architecture benchmark behavior to submission candidates.",
            "Cross-listener transport now converts the failed target-listener route-lift into a safer rule: listener posterior calibrates route/fusion/core-proposed actions instead of generating actions directly.",
            "Counterfactual listener-dropout turns public failures into toxicity labels and exposes a strong A/B sensor: either high-survival route/fusion actions were good cells mixed into bad submissions, or the public/private equation requires inverting those toxic directions.",
            "Spectral public-tangent decomposition shows that post-H057 public failures are highly low-rank; HS-JEPA can now treat failed submissions as a negative representation space rather than isolated bad scores.",
            "Negative tangent invariant projection turns that negative representation into an action-grade test: only anti-public-bad moves that preserve target-route and subject-prior energy are released.",
            "LB-conditioned responsibility now treats public LB as an external listener and estimates which row-target actions carried scalar loss responsibility under leave-one-anchor stress.",
            "Mixture-listener responsibility shows that scalar public response is better explained by latent listener heads, and raises a new Q/S target-routing hypothesis through `target_listener_split_qs`.",
        ],
        "what_the_adapter_does_not_prove": [
            "pure OG-only assignment",
            "action-grade portable hidden row-support recovery",
            "that masked row-support is already a deployment-grade action decoder",
            "that the row-support strict action decoder is safe without public/private LB observation",
            "that route-frontier action decoding is private-safe without public LB observation",
            "that route-toxicity fusion will beat plain route-frontier on public/private LB",
            "that consensus-shadow boundary cells are safe before public LB observes them",
            "that removing a core module is beneficial before public LB observes the full-core vs ablated-core counterfactual",
            "that dataset-free action-health calibration will beat the strict decoder jury before public LB observes the guarded/pressure counterfactual",
            "that cross-listener transport will beat the strict decoder jury before public LB observes the listener-calibrated counterfactual",
            "that listener-dropout health alone is public-safe before public LB observes the aggressive-vs-inverted counterfactual",
            "that the public-bad spectral tangent is invertible before public LB observes anti-tangent and orthogonal residual sensors",
            "that invariant-projected anti-tangent actions improve LB before public LB observes the generated projection candidates",
            "that scalar public-listener responsibility is portable or private-safe before public LB observes the LB-conditioned responsibility candidates",
            "that mixture-listener responsibility is action-grade before public LB observes target-split, consensus, and residual-conflict candidates",
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

    negative_projection_rows = [
        "| Variant | Output | Changed cells | Bad cosine | Energy delta | Subject delta | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["negative_tangent_invariant_projection_solver"]["variants"].items():
        negative_projection_rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{item['changed_cells']}` | "
            f"`{fmt(item['bad_tangent_cosine'], 4)}` | `{fmt(item['mean_incremental_energy_delta'], 5)}` | "
            f"`{fmt(item['mean_subject_energy_delta'], 5)}` | `{item['upload_safe']}` |"
        )

    lb_responsibility_rows = [
        "| Variant | Output | Changed cells | Predicted loss delta | Sign stability | Energy delta | Bad cosine | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["lb_conditioned_responsibility_solver"]["variants"].items():
        lb_responsibility_rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{item['changed_cells']}` | "
            f"`{fmt(item['sum_predicted_loss_delta'], 5)}` | `{fmt(item['mean_sign_stability'], 4)}` | "
            f"`{fmt(item['mean_incremental_energy_delta'], 5)}` | `{fmt(item['bad_tangent_cosine'], 4)}` | "
            f"`{item['upload_safe']}` |"
        )

    mixture_listener_rows = [
        "| Variant | Output | Changed cells | Scalar delta | Mode delta | Conflict | Confidence | Bad cosine | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["mixture_listener_responsibility_solver"]["variants"].items():
        mixture_listener_rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{item['changed_cells']}` | "
            f"`{fmt(item['sum_predicted_scalar_delta'], 5)}` | "
            f"`{fmt(item['sum_predicted_total_mode_delta'], 5)}` | "
            f"`{fmt(item['mean_conflict_score'], 4)}` | "
            f"`{fmt(item['mean_mode_confidence'], 4)}` | "
            f"`{fmt(item['bad_tangent_cosine'], 4)}` | `{item['upload_safe']}` |"
        )

    subset_tomography_rows = [
        "| Variant | Output | Changed cells | Public incl. | Label conf. | Private safe | Toxicity | Pred delta | Bad cosine | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["public_private_subset_tomography_solver"]["variants"].items():
        subset_tomography_rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{item['changed_cells']}` | "
            f"`{fmt(item['mean_public_inclusion'], 4)}` | "
            f"`{fmt(item['mean_label_confidence'], 4)}` | "
            f"`{fmt(item['mean_private_safety'], 4)}` | "
            f"`{fmt(item['mean_toxicity'], 4)}` | "
            f"`{fmt(item['sum_predicted_public_delta'], 5)}` | "
            f"`{fmt(item['bad_tangent_cosine'], 4)}` | `{item['upload_safe']}` |"
        )

    anti_listener_rows = [
        "| Variant | Output | Changed cells | Listener inverse | Listener safety | Private safe | Hard tox | Broad tox | Pred delta | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for variant, item in report["anti_listener_toxicity_equation_solver"]["variants"].items():
        anti_listener_rows.append(
            f"| `{variant}` | `{item['submission_file']}` | `{item['changed_cells']}` | "
            f"`{fmt(item['mean_listener_inverse'], 4)}` | "
            f"`{fmt(item['mean_listener_safety'], 4)}` | "
            f"`{fmt(item['mean_private_safety'], 4)}` | "
            f"`{fmt(item['mean_hardworld_toxicity'], 4)}` | "
            f"`{fmt(item['mean_broad_toxicity'], 4)}` | "
            f"`{fmt(item['sum_predicted_public_delta'], 5)}` | `{item['upload_safe']}` |"
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
            "## Decoder Boundary Tomography Solver",
            "",
            f"- Status: `{report['decoder_boundary_tomography_solver']['status']}`",
            f"- Recommended LB sensor: `{report['decoder_boundary_tomography_solver']['recommended_lb_sensor']}`",
            f"- Boundary inventory: `{report['decoder_boundary_tomography_solver']['boundary_inventory']}`",
            "",
            report["decoder_boundary_tomography_solver"]["claim"],
            "",
            "이 실험은 strict jury가 버린 셀을 `consensus_shadow`, `route_only`, `fusion_only`로 분리한다. public에서 consensus-shadow가 살아나면 HS-JEPA decoder의 병목은 안전한 latent가 아니라 너무 보수적인 action release였다는 뜻이다.",
            "",
            "## Core-Mediated Action Release",
            "",
            f"- Status: `{report['core_mediated_action_release']['status']}`",
            f"- Recommended LB sensor: `{report['core_mediated_action_release']['recommended_lb_sensor']}`",
            f"- Cell inventory: `{report['core_mediated_action_release']['cell_inventory']}`",
            "",
            report["core_mediated_action_release"]["claim"],
            "",
            "이 실험은 실제 sleep-adapter row-target action을 HS-JEPA Core의 `ContextView`, `ListenerPrototype`, `CandidateAction` 인터페이스로 변환한 뒤 core release equation을 통과시킨다. public에서 살아나면 HS-JEPA Core가 논문용 설명 구조를 넘어 action-grade decoder가 됐다는 신호다.",
            "",
            "## Core Release Ablation Probe",
            "",
            f"- Status: `{report['core_release_ablation_probe']['status']}`",
            f"- Recommended LB candidate: `{report['core_release_ablation_probe']['recommended_lb_candidate']}`",
            f"- Recommended architecture sensor: `{report['core_release_ablation_probe']['recommended_architecture_sensor']}`",
            f"- Recommended negative control: `{report['core_release_ablation_probe']['recommended_negative_control']}`",
            "",
            report["core_release_ablation_probe"]["claim"],
            "",
            "이 실험은 같은 real adapter cell을 full-core, no-listener, no-action-health, no-invariant, invariant-only release equation으로 다시 풀어본다. public에서 no-action-health가 full-core를 이기면 action-health가 현재 adapter를 과하게 막고 있다는 뜻이고, 지면 full HS-JEPA release boundary가 더 설득력 있다.",
            "",
            "## Core-Health Calibrated Release",
            "",
            f"- Status: `{report['core_health_calibrated_release']['status']}`",
            f"- Recommended LB candidate: `{report['core_health_calibrated_release']['recommended_lb_candidate']}`",
            f"- Recommended big-bet sensor: `{report['core_health_calibrated_release']['recommended_big_bet_sensor']}`",
            f"- Recommended pressure sensor: `{report['core_health_calibrated_release']['recommended_pressure_sensor']}`",
            f"- Benchmark calibration: `{report['core_health_calibrated_release']['benchmark_calibration']}`",
            "",
            report["core_health_calibrated_release"]["claim"],
            "",
            "이 실험은 dataset-free core benchmark에서 action-health 제거가 false positive를 크게 만든다는 사실을 실제 sleep-adapter row-target release prior로 사용한다. guarded 후보가 public에서 살아나면 HS-JEPA core의 일반적인 action-health 실패 모드가 대회 adapter에도 전이된다는 강한 증거가 된다.",
            "",
            "## Cross-Listener Transport Decoder",
            "",
            f"- Status: `{report['cross_listener_transport_decoder']['status']}`",
            f"- Recommended LB sensor: `{report['cross_listener_transport_decoder']['recommended_lb_sensor']}`",
            f"- Recommended big bet: `{report['cross_listener_transport_decoder']['recommended_big_bet']}`",
            f"- Negative sensor: `{report['cross_listener_transport_decoder']['negative_sensor']}`",
            "",
            report["cross_listener_transport_decoder"]["claim"],
            "",
            "이 실험은 target-listener route-lift가 public에서 실패한 사실을 버리지 않고, listener posterior의 역할을 `action generator`에서 `transport calibrator`로 바꾼다. public에서 살아나면 HS-JEPA의 listener responsibility가 직접 예측값을 만드는 장치가 아니라 action boundary를 보정하는 장치라는 더 일반적인 주장이 강해진다.",
            "",
            "## Counterfactual Listener-Dropout Solver",
            "",
            f"- Status: `{report['counterfactual_listener_dropout_solver']['status']}`",
            f"- Recommended information sensor: `{report['counterfactual_listener_dropout_solver']['recommended_information_sensor']}`",
            f"- Recommended thesis sensor: `{report['counterfactual_listener_dropout_solver']['recommended_thesis_sensor']}`",
            "",
            report["counterfactual_listener_dropout_solver"]["claim"],
            "",
            "이 실험은 route/fusion/target-listener/anti-shortcut을 서로 다른 listener로 보고, 한 listener를 가려도 살아남는 action만 healthy action으로 본다. 특히 `dropout_fullfield_aggressive`와 `toxic_direction_inversion`은 같은 high-survival cell을 같은 방향으로 믿을지, public-negative sensor가 말한 반대 방향으로 뒤집을지를 가르는 A/B 센서다.",
            "",
            "## Spectral Public-Tangent Solver",
            "",
            f"- Status: `{report['spectral_public_tangent_solver']['status']}`",
            f"- First bad-mode variance: `{fmt(report['spectral_public_tangent_solver']['spectral'].get('first_mode_variance'), 4)}`",
            f"- Top-5 cumulative variance: `{fmt(report['spectral_public_tangent_solver']['spectral'].get('top5_cumulative_variance'), 4)}`",
            f"- Candidate pool: `{report['spectral_public_tangent_solver']['pool']}`",
            f"- Recommended information sensor: `{report['spectral_public_tangent_solver']['recommended_information_sensor']}`",
            f"- Recommended counter sensor: `{report['spectral_public_tangent_solver']['recommended_counter_sensor']}`",
            "",
            report["spectral_public_tangent_solver"]["claim"],
            "",
            "이 실험은 H057 이후 public에서 실패한 제출들을 독립 실패로 보지 않고 하나의 negative representation space로 본다. 첫 번째 spectral mode가 지배적이면, 다음 큰 질문은 `나쁜 방향의 반대로 가면 좋은가`, 아니면 `나쁜 방향과 직교한 private-safe 잔차만 살아남는가`이다.",
            "",
            "## Negative Tangent Invariant Projection Solver",
            "",
            f"- Status: `{report['negative_tangent_invariant_projection_solver']['status']}`",
            f"- Recommended variant: `{report['negative_tangent_invariant_projection_solver']['recommended_variant']}`",
            f"- Projected cells: `{report['negative_tangent_invariant_projection_solver']['projected_cells']}`",
            "",
            report["negative_tangent_invariant_projection_solver"]["core_claim"],
            "",
            *negative_projection_rows,
            "",
            "이 실험은 spectral solver의 후속이다. 단순히 public-bad tangent 반대로 움직이는 것이 아니라, train label covariance와 subject prior로 정의한 invariant manifold를 깨지 않는 anti-bad action만 release한다. public에서 살아나면 HS-JEPA의 핵심 decoder가 `negative representation + invariant projection`이라는 논문 주장으로 올라간다.",
            "",
            "## LB-Conditioned Responsibility Solver",
            "",
            f"- Status: `{report['lb_conditioned_responsibility_solver']['status']}`",
            f"- Recommended variant: `{report['lb_conditioned_responsibility_solver']['recommended_variant']}`",
            f"- Anchor count: `{report['lb_conditioned_responsibility_solver']['fit'].get('anchor_count')}`",
            f"- LOO correlation: `{fmt(report['lb_conditioned_responsibility_solver']['fit'].get('loo_corr'), 4)}`",
            f"- Responsibility cells: `{report['lb_conditioned_responsibility_solver']['responsibility_cells']}`",
            "",
            report["lb_conditioned_responsibility_solver"]["core_claim"],
            "",
            *lb_responsibility_rows,
            "",
            "이 실험은 public LB를 하나의 외부 listener로 보고, 여러 제출 action delta와 scalar loss 변화를 이용해 row-target responsibility를 역추정한다. 추천 `pure_lb_gradient_jackpot`은 predicted public-listener 개선과 route energy는 강하지만 spectral bad tangent와 일부 같은 방향이다. 그래서 public에서 좋아지면 scalar listener equation이 spectral anti-tangent보다 더 action-grade라는 뜻이고, 나빠지면 LB-conditioned responsibility는 아직 diagnostic에 가깝다는 뜻이다.",
            "",
            "## Mixture-Listener Responsibility Solver",
            "",
            f"- Status: `{report['mixture_listener_responsibility_solver']['status']}`",
            f"- Recommended variant: `{report['mixture_listener_responsibility_solver']['recommended_variant']}`",
            f"- Anchor count: `{report['mixture_listener_responsibility_solver']['anchor_count']}`",
            f"- Cell count: `{report['mixture_listener_responsibility_solver']['cell_count']}`",
            f"- Mixture LOO correlation: `{fmt(report['mixture_listener_responsibility_solver']['mixture_fit'].get('loo_corr'), 4)}`",
            f"- Scalar LOO correlation: `{fmt(report['mixture_listener_responsibility_solver']['mixture_fit'].get('scalar_fit', {}).get('loo_corr'), 4)}`",
            "",
            report["mixture_listener_responsibility_solver"]["core_claim"],
            "",
            *mixture_listener_rows,
            "",
            "이 실험은 public LB를 단일 listener가 아니라 여러 latent listener head의 scalar readout으로 본다. 추천 `target_listener_split_qs`는 Q target은 residual listener, S target은 scalar/public consensus 쪽을 듣는다는 가설을 건다. public에서 좋아지면 HS-JEPA의 논문 기여는 `listener responsibility`에서 `latent listener mixture routing`으로 확장된다.",
            "",
            "## Public/Private Subset Tomography Solver",
            "",
            f"- Status: `{report['public_private_subset_tomography_solver']['status']}`",
            f"- Recommended variant: `{report['public_private_subset_tomography_solver']['recommended_variant']}`",
            f"- Anchor count: `{report['public_private_subset_tomography_solver']['anchor_count']}`",
            f"- Cell count: `{report['public_private_subset_tomography_solver']['cell_count']}`",
            f"- Source responsibility LOO correlation: `{fmt(report['public_private_subset_tomography_solver']['source_fit'].get('loo_corr'), 4)}`",
            "",
            report["public_private_subset_tomography_solver"]["core_claim"],
            "",
            *subset_tomography_rows,
            "",
            "이 실험은 scalar public feedback을 그대로 action truth로 쓰지 않고, public subset inclusion, hidden label direction, private-safety, toxicity를 분리한다. 추천 `subset_label_direction_jackpot`이 좋아지면 public subset과 label direction 분해가 action-grade라는 뜻이고, `qs_dual_subset_route`가 상대적으로 낫다면 Q/S listener route 분리가 더 중요한 병목이라는 뜻이다.",
            "",
            "## Anti-Listener Toxicity Equation Solver",
            "",
            f"- Status: `{report['anti_listener_toxicity_equation_solver']['status']}`",
            f"- Recommended variant: `{report['anti_listener_toxicity_equation_solver']['recommended_variant']}`",
            f"- Toxic anchors: `{report['anti_listener_toxicity_equation_solver']['toxic_anchor_count']}`",
            f"- Cell count: `{report['anti_listener_toxicity_equation_solver']['cell_count']}`",
            f"- Source responsibility LOO correlation: `{fmt(report['anti_listener_toxicity_equation_solver']['source_fit'].get('loo_corr'), 4)}`",
            "",
            report["anti_listener_toxicity_equation_solver"]["thesis"],
            "",
            *anti_listener_rows,
            "",
            "이 실험은 CrossListener/H088/target-listener 실패를 단순 폐기하지 않고, 실패한 listener action을 독성 teacher로 사용한다. 추천 `private_safe_anti_listener_bridge`가 public에서 살아나면 HS-JEPA의 action-health 모듈은 listener를 더 믿는 장치가 아니라, listener가 틀린 방향을 말할 때 그 반대 방향을 안전하게 release하는 장치라는 논문 주장이 강해진다.",
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
            "1. `Anti-Listener Toxicity Equation Solver`: 실패한 listener release를 독성 teacher로 뒤집을 수 있는지 검증한다.",
            "2. `Public/Private Subset Tomography Solver`: scalar public feedback을 subset inclusion과 hidden label direction으로 분해한다.",
            "3. `Mixture-Listener Responsibility Solver`: public response가 여러 latent listener head의 합성인지 검증한다.",
            "4. `LB-Conditioned Responsibility Solver`: public scalar listener equation이 action-grade인지 검증한다.",
            "5. `Negative Tangent Invariant Projection Solver`: negative representation이 실제 action-grade가 되려면 invariant projection이 필요한지 검증한다.",
            "6. `Spectral Public-Tangent Solver`: H057 이후 실패들이 공유하는 저차원 public-bad direction이 invertible action equation인지 검증한다.",
            "7. `Counterfactual Listener-Dropout Solver`: 같은 high-survival action을 믿을지 뒤집을지 가르는 A/B 센서다.",
            "8. `Action Decoder Ablation Suite`: action decoder order가 public sensor와 맞는지 큰 구조로 검증한다.",
            "9. `OG-only Human-State Assignment Teacher`: 성공하면 HS-JEPA의 범용성이 가장 크게 올라간다.",
            "10. `Hard-World Mixture Toxicity Decoder`: H088류 hard-world 독성을 broad toxicity와 분리한다.",
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
        read_json(DECODER_BOUNDARY_TOMOGRAPHY_JSON),
        read_json(CORE_MEDIATED_RELEASE_JSON),
        read_json(CORE_RELEASE_ABLATION_JSON),
        read_json(CORE_HEALTH_CALIBRATED_JSON),
        read_json(CROSS_LISTENER_TRANSPORT_JSON),
        read_json(COUNTERFACTUAL_LISTENER_DROPOUT_JSON),
        read_json(SPECTRAL_PUBLIC_TANGENT_JSON),
        read_json(NEGATIVE_TANGENT_INVARIANT_JSON),
        read_json(LB_CONDITIONED_RESPONSIBILITY_JSON),
        read_json(MIXTURE_LISTENER_RESPONSIBILITY_JSON),
        read_json(PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON),
        read_json(ANTI_LISTENER_TOXICITY_JSON),
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
