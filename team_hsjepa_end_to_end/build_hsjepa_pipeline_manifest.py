#!/usr/bin/env python3
"""Build an end-to-end pipeline manifest for the team HS-JEPA package.

The reproducibility contract lists files.  The method packet explains the idea.
This manifest connects them as a role-based pipeline from raw data and public
sensor observations to submissions and paper artifacts.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"

PACKAGE_JSON = OUT / "route_conserving_s2_bridge_package.json"
EVIDENCE_CSV = OUT / "route_conserving_s2_bridge_evidence_table.csv"
STRESS_CSV = OUT / "route_conserving_s2_bridge_stress_summary.csv"
VALIDATION_JSON = OUT / "route_conserving_s2_bridge_validation_report.json"
CONTRACT_JSON = OUT / "hsjepa_reproducibility_contract.json"
READINESS_JSON = OUT / "hsjepa_architecture_readiness_report.json"
MECHANISM_ABLATION_JSON = OUT / "hsjepa_mechanism_ablation_report.json"
GENERALITY_JSON = OUT / "hsjepa_generality_report.json"
BOUNDARY_AUDIT_JSON = OUT / "hsjepa_core_adapter_boundary_audit.json"
METHOD_PACKET_JSON = OUT / "hsjepa_paper_method_packet.json"
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
ACTION_DECODER_ABLATION_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "action_decoder_ablation_suite" / "hsjepa_action_decoder_ablation_suite.json"
CONTRASTIVE_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "listener_invariant_contrastive_probe.json"
PRIVATE_TOXICITY_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "private_safe_toxicity_probe.json"
HARDWORLD_TOXICITY_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hardworld_toxicity_factorization_probe.json"
FACTORIZED_DECODER_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout.json"
FACTORIZED_STRESS_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit.json"

MANIFEST_JSON = OUT / "hsjepa_pipeline_manifest.json"
MANIFEST_MD = OUT / "hsjepa_pipeline_manifest_ko.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(x: object, digits: int = 6) -> str:
    if x is None:
        return "n/a"
    try:
        val = float(x)
    except (TypeError, ValueError):
        return str(x)
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def require_inputs() -> None:
    required = [
        PACKAGE_JSON,
        EVIDENCE_CSV,
        STRESS_CSV,
        VALIDATION_JSON,
        CONTRACT_JSON,
        READINESS_JSON,
        MECHANISM_ABLATION_JSON,
        GENERALITY_JSON,
        BOUNDARY_AUDIT_JSON,
        METHOD_PACKET_JSON,
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
        ACTION_DECODER_ABLATION_JSON,
        CONTRASTIVE_PROBE_JSON,
        PRIVATE_TOXICITY_PROBE_JSON,
        HARDWORLD_TOXICITY_PROBE_JSON,
        FACTORIZED_DECODER_JSON,
        FACTORIZED_STRESS_JSON,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing pipeline manifest inputs: {missing}")


def contract_category_summary(contract: dict[str, object]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for rec in contract.get("records", []):
        if not isinstance(rec, dict):
            continue
        category = str(rec.get("category"))
        bucket = summary.setdefault(category, {"records": 0, "required": 0, "missing_required": 0})
        bucket["records"] += 1
        if rec.get("required"):
            bucket["required"] += 1
            if not rec.get("exists"):
                bucket["missing_required"] += 1
    return summary


def stage(
    stage_id: str,
    name: str,
    role: str,
    inputs: list[str],
    outputs: list[str],
    evidence: list[str],
    boundary: str,
) -> dict[str, object]:
    return {
        "id": stage_id,
        "name": name,
        "role": role,
        "inputs": inputs,
        "outputs": outputs,
        "evidence": evidence,
        "boundary": boundary,
    }


def build_manifest() -> dict[str, object]:
    require_inputs()
    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    contract = read_json(CONTRACT_JSON)
    readiness = read_json(READINESS_JSON)
    ablation = read_json(MECHANISM_ABLATION_JSON)
    generality = read_json(GENERALITY_JSON)
    boundary_audit = read_json(BOUNDARY_AUDIT_JSON)
    method = read_json(METHOD_PACKET_JSON)
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
    action_decoder_ablation = read_json(ACTION_DECODER_ABLATION_JSON)
    contrastive_probe = read_json(CONTRASTIVE_PROBE_JSON)
    private_toxicity_probe = read_json(PRIVATE_TOXICITY_PROBE_JSON)
    hardworld_toxicity_probe = read_json(HARDWORLD_TOXICITY_PROBE_JSON)
    factorized_decoder = read_json(FACTORIZED_DECODER_JSON)
    factorized_stress = read_json(FACTORIZED_STRESS_JSON)
    evidence = pd.read_csv(EVIDENCE_CSV)
    stress = pd.read_csv(STRESS_CSV)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    mechanism = validation["mechanism_evidence"]
    og_verdict = og_probe["verdict"]
    gap_verdict = assignment_gap["verdict"]
    row_support_verdict = row_support_sensor["verdict"]
    masked_row_support_verdict = masked_row_support["verdict"]
    row_support_decoder_verdict = row_support_decoder["verdict"]
    route_frontier_verdict = route_frontier_decoder["verdict"]
    route_toxicity_fusion_verdict = route_toxicity_fusion_decoder["verdict"]
    decoder_order_jury_verdict = decoder_order_jury["verdict"]
    decoder_boundary_tomography_verdict = decoder_boundary_tomography["verdict"]
    core_mediated_verdict = core_mediated_release["verdict"]
    core_release_ablation_verdict = core_release_ablation["verdict"]
    core_health_calibrated_verdict = core_health_calibrated["verdict"]
    cross_listener_verdict = cross_listener_transport["verdict"]
    listener_dropout_verdict = counterfactual_listener_dropout["verdict"]
    spectral_tangent_verdict = spectral_public_tangent["verdict"]
    negative_projection_verdict = negative_tangent_invariant["verdict"]
    lb_responsibility_verdict = lb_conditioned_responsibility["verdict"]
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
    category_summary = contract_category_summary(contract)
    packaged = package["packaged_submissions"]

    role_outputs = {
        role: item["submission_file"]
        for role, item in packaged.items()
        if isinstance(item, dict) and "submission_file" in item
    }

    stress_by_name = {str(row["name"]): row for row in stress.to_dict("records")}
    primary = stress_by_name["route_conserving_objective_bridge_primary"]
    s2 = stress_by_name["s2_listener_bridge_interpretable"]

    stages = [
        stage(
            "hsjepa_core_architecture",
            "HS-JEPA Core Architecture",
            "Defines the reusable human-understanding mechanism before any sleep-competition target names are introduced.",
            ["partial human context", "generic listener/outcome set", "domain invariant interface"],
            ["hsjepa_core_manifest_ko.md", "hsjepa_core_ablation_contract_ko.md"],
            [
                f"Core status: {core['status']}",
                f"Core gates: {core['passed_gates']}/{core['total_gates']}",
                f"Ablation status: {core_ablation['status']}",
                f"Reference run: {core_reference['status']}",
                f"Module benchmark: {core_benchmark['status']}",
            ],
            "The core must not depend on S2, public LB sensors, submission files, or manual row ids.",
        ),
        stage(
            "hsjepa_core_reference_run",
            "HS-JEPA Core Reference Run",
            "Executes the dataset-free core on synthetic context/listener/action inputs to prove the architecture is not only a report.",
            ["hsjepa_core/core.py", "synthetic context views", "synthetic listener prototypes", "synthetic candidate actions"],
            ["hsjepa_core_reference_run_ko.md"],
            [
                f"Status: {core_reference['status']}",
                f"Released actions: {core_reference['full_core']['summary']['released_actions']}",
                f"Ablations: {list(core_reference['ablations'].keys())}",
            ],
            "This stage is architecture-only; it must not read competition data or sensor observations.",
        ),
        stage(
            "hsjepa_core_module_benchmark",
            "HS-JEPA Core Module Benchmark",
            "Tests the reusable core across generic human-state worlds and compares full core against module-removal policies.",
            ["hsjepa_core/core.py", "generic human-state scenarios", "listener/action/invariant expectations"],
            ["hsjepa_core_module_benchmark_ko.md", "hsjepa_core_module_benchmark_cases.csv"],
            [
                f"Status: {core_benchmark['status']}",
                f"Scenarios: {core_benchmark['scenario_count']}",
                f"Full-core F1: {fmt(core_benchmark['verdict']['full_core_mean_f1'], 4)}",
                f"Action-health FP lift: {core_benchmark['verdict']['remove_action_health_false_positive_lift']}",
                f"Invariant FP lift: {core_benchmark['verdict']['remove_invariant_false_positive_lift']}",
            ],
            "This stage is core-only; it proves architecture behavior without sleep labels or public sensors.",
        ),
        stage(
            "og_raw_lifestyle_context",
            "OG Raw Lifestyle Context",
            "Provides train labels, submission key contract, and raw lifelog items.",
            ["data/ch2026_metrics_train.csv", "data/ch2026_submission_sample.csv", "data/ch2025_data_items/*.parquet"],
            ["raw/context feature artifacts used by upstream HS-JEPA modules"],
            [
                f"OG records in contract: {category_summary.get('og_raw', {}).get('records', 0)}",
                f"Required missing: {contract.get('required_missing_count')}",
            ],
            "This stage is competition data, not external/private data.",
        ),
        stage(
            "public_lb_sensor",
            "Public LB Sensor Ledger",
            "Uses public submission observations as a sensor for hidden row-target action response.",
            ["data_analytics/hsjepa_public_score_ledger.csv"],
            ["public-sensitive action anchors", "negative toxicity anchors"],
            [
                f"Ledger rows: {contract.get('public_ledger_summary', {}).get('rows')}",
                f"Pre-public-equation best: {fmt(public['pre_public_equation_best_public_lb'], 10)}",
                f"Current best: {fmt(public['current_best_public_lb'], 10)}",
            ],
            "This is not an OG-only claim; it is the competition-specific sensor path.",
        ),
        stage(
            "human_state_listener_context",
            "Human-State Listener Context",
            "Turns lifestyle/cohort context into target/cell orientation diagnostics.",
            ["OG lifestyle/context artifacts", "s2hub_human_state_distillation_readout.json"],
            ["cell orientation scores", "human_state_probe submission"],
            [
                f"Cell OOF AUC: {fmt(human['cell_oof_auc_human_target_context'], 3)}",
                f"Row OOF AUC: {fmt(human['row_oof_auc'], 3)}",
            ],
            "Human-state is an orientation diagnostic, not a standalone row selector.",
        ),
        stage(
            "og_only_assignment_probe",
            "OG-only Assignment Teacher Probe",
            "Tests whether human-state geometry can replace the public-sensor row-target assignment teacher.",
            ["s2hub_jackpot_cell_student_frame.csv", "stagebridge_jackpot_cell_student_frame.csv"],
            ["og_only_assignment_teacher_probe_ko.md", "og_only_assignment_teacher_ranked_cells.csv"],
            [
                f"Probe status: {og_verdict['status']}",
                f"Pure OG row-cap2 recall: {fmt(og_verdict['pure_og_row_cap2_mean_recall'], 4)}",
                f"Distilled row-cap2 recall: {fmt(og_verdict['distilled_row_cap2_mean_recall'], 4)}",
            ],
            "The probe currently measures the gap; it does not prove pure OG-only deployment.",
        ),
        stage(
            "assignment_gap_decomposition",
            "Assignment Gap Decomposition",
            "Decomposes public-sensitive row-target assignment into target-route information and hidden row-support information.",
            ["og_only_assignment_teacher_ranked_cells.csv"],
            ["assignment_gap_decomposition_probe_ko.md", "assignment_gap_decomposition_summary.csv"],
            [
                f"Gap status: {gap_verdict['status']}",
                f"Best portable recall: {fmt(gap_verdict['mean_best_portable_recall'], 4)}",
                f"Row oracle + stage recall: {fmt(gap_verdict['mean_row_oracle_stage_recall'], 4)}",
                f"Row-support gap: {fmt(gap_verdict['mean_row_support_gap'], 4)}",
            ],
            "This is a bottleneck decomposition, not a deployable row-support sensor.",
        ),
        stage(
            "hidden_row_support_sensor",
            "Hidden Row-Support Sensor Transfer Probe",
            "Learns row-support from one public-sensitive teacher world and tests transfer to another teacher world.",
            ["og_only_assignment_teacher_ranked_cells.csv", "assignment_gap_decomposition_probe.json"],
            ["hidden_row_support_sensor_probe_ko.md", "hidden_row_support_sensor_transfer_metrics.csv"],
            [
                f"Probe status: {row_support_verdict['status']}",
                f"Best portable family: {row_support_verdict['best_portable_family']}",
                f"Mean row AUC: {fmt(row_support_verdict['best_portable_mean_row_auc'], 4)}",
                f"Mean cell recall with stage prior: {fmt(row_support_verdict['best_portable_mean_cell_recall_with_stage_prior'], 4)}",
                f"AUC z vs permuted train: {fmt(row_support_verdict['best_portable_mean_auc_z_vs_permuted_train'], 4)}",
            ],
            "This is transfer evidence for a row-support sensor, not yet an action-grade deployment decoder.",
        ),
        stage(
            "masked_row_support_objective",
            "Masked Row-Support Objective Probe",
            "Tests whether hidden row-support can serve as a JEPA target representation predicted from masked human/context views.",
            ["hidden_row_support_sensor_probe.json", "og_only_assignment_teacher_ranked_cells.csv"],
            ["masked_row_support_objective_probe_ko.md", "masked_row_support_objective_transfer_metrics.csv"],
            [
                f"Objective status: {masked_row_support_verdict['status']}",
                f"Full row AUC: {fmt(masked_row_support_verdict['full_composite_mean_row_auc'], 4)}",
                f"Full cell recall: {fmt(masked_row_support_verdict['full_composite_mean_cell_recall'], 4)}",
                f"Human-only cell recall: {fmt(masked_row_support_verdict['human_only_mean_cell_recall'], 4)}",
                f"Group stress row AUC: {fmt(masked_row_support_verdict['group_stress_full_mean_auc'], 4)}",
            ],
            "This supports HS-JEPA representation learning, but weak group-heldout stress blocks direct deployment as an action decoder.",
        ),
        stage(
            "row_support_strict_action_decoder",
            "Row-Support Strict Action Decoder",
            "Translates masked row-support into route-conserving, toxicity-filtered row-target action candidates.",
            ["masked_row_support_objective_probe.json", "hardworld_toxicity_factorization_sectors.csv", "route bridge selected bundles"],
            ["row_support_strict_action_decoder_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in row_support_decoder.get("variants", {}).values()
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Decoder status: {row_support_decoder_verdict['status']}",
                f"Recommended variant: {row_support_decoder_verdict['recommended_variant']}",
                f"Exploratory changed cells: {row_support_decoder_verdict['exploratory_changed_cells']}",
                f"Exploratory safety z: {fmt(row_support_decoder_verdict['exploratory_safety_z'], 2)}",
                f"Exploratory combined z: {fmt(row_support_decoder_verdict['exploratory_combined_z'], 2)}",
            ],
            "This is an LB-informative big bet with a route-gain tradeoff, not a safe default submission.",
        ),
        stage(
            "route_frontier_action_decoder",
            "Route-Frontier Action Decoder",
            "Selects route-manifold frontier actions before trusting row-support and toxicity gates.",
            ["row_support_strict_action_decoder_readout.json", "route bridge candidates", "hardworld toxicity sectors"],
            ["route_frontier_action_decoder_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in route_frontier_decoder.get("variants", {}).values()
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Decoder status: {route_frontier_verdict['status']}",
                f"Recommended variant: {route_frontier_verdict['recommended_variant']}",
                f"Variant scores: {route_frontier_verdict['variant_scores']}",
            ],
            "This tests whether action-grade decoding should start from route-frontier selection rather than support-first selection.",
        ),
        stage(
            "route_toxicity_fusion_decoder",
            "Route-Toxicity Fusion Decoder",
            "Composes route-frontier action ordering with factorized broad-public and hard-world action-health gating.",
            ["route_frontier_action_decoder_readout.json", "hardworld_toxicity_factorization_sectors.csv", "row-support scores"],
            ["route_toxicity_fusion_decoder_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in route_toxicity_fusion_decoder.get("variants", {}).values()
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Decoder status: {route_toxicity_fusion_verdict['status']}",
                f"Recommended variant: {route_toxicity_fusion_verdict['recommended_variant']}",
                f"Variant scores: {route_toxicity_fusion_verdict['variant_scores']}",
            ],
            "This is a competition-adapter action solver; it does not prove private-LB safety or pure OG-only assignment.",
        ),
        stage(
            "decoder_order_jury_solver",
            "Decoder-Order Jury Solver",
            "Releases only row-target actions independently selected by route-frontier and route-toxicity fusion decoders.",
            ["route_frontier_action_decoder_readout.json", "route_toxicity_fusion_decoder_readout.json", "action_decoder_ablation_suite.csv"],
            ["decoder_order_jury_solver_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in decoder_order_jury.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Solver status: {decoder_order_jury_verdict['status']}",
                f"Recommended LB sensor: {decoder_order_jury_verdict['recommended_lb_sensor']}",
            ],
            "This tests whether HS-JEPA action decoding should be a cross-decoder listener jury rather than a single route or toxicity score.",
        ),
        stage(
            "decoder_boundary_tomography_solver",
            "Decoder Boundary Tomography Solver",
            "Splits cells rejected by strict cross-decoder jury into weak-consensus, route-only, and fusion-only action worlds.",
            ["decoder_order_jury_solver_readout.json", "route_frontier_action_decoder_readout.json", "route_toxicity_fusion_decoder_readout.json"],
            ["decoder_boundary_tomography_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in decoder_boundary_tomography.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Tomography status: {decoder_boundary_tomography_verdict['status']}",
                f"Recommended LB sensor: {decoder_boundary_tomography_verdict['recommended_lb_sensor']}",
                f"Boundary inventory: {decoder_boundary_tomography.get('boundary_inventory')}",
            ],
            "This is the too-conservative-jury diagnostic; consensus-shadow cells are not safe until public LB observes them.",
        ),
        stage(
            "core_mediated_action_release",
            "Core-Mediated Action Release",
            "Converts real sleep-adapter row-target actions into the generic HS-JEPA core API before release.",
            [
                "hsjepa_core_reference_run.json",
                "decoder_order_jury_solver_readout.json",
                "decoder_boundary_tomography_readout.json",
            ],
            ["core_mediated_action_release_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in core_mediated_release.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Core-mediated status: {core_mediated_verdict['status']}",
                f"Recommended LB sensor: {core_mediated_verdict['recommended_lb_sensor']}",
                f"Cell inventory: {core_mediated_release.get('cell_inventory')}",
            ],
            "This proves the core API can drive adapter actions mechanically; public LB still decides whether that core release equation is action-grade.",
        ),
        stage(
            "core_release_ablation_probe",
            "Core Release Ablation Probe",
            "Removes listener responsibility, action-health, or invariant energy from the real adapter release equation to make HS-JEPA core constraints falsifiable.",
            ["core_mediated_action_release_readout.json", "decoder_order_jury_solver_readout.json", "decoder_boundary_tomography_readout.json"],
            ["core_release_ablation_probe_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in core_release_ablation.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Ablation status: {core_release_ablation_verdict['status']}",
                f"Full-core LB candidate: {core_release_ablation_verdict['recommended_lb_candidate']}",
                f"Architecture sensor: {core_release_ablation_verdict['recommended_architecture_sensor']}",
            ],
            "This is an architecture falsification probe; module-removal public LB is needed before claiming a removed module improves the adapter.",
        ),
        stage(
            "core_health_calibrated_release",
            "Core-Health Calibrated Release",
            "Uses dataset-free action-health false-positive lift as a release prior for real sleep-adapter row-target actions.",
            ["hsjepa_core_module_benchmark.json", "core_release_ablation_probe_readout.json", "core_mediated_action_release_readout.json"],
            ["core_health_calibrated_release_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in core_health_calibrated.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Calibrated status: {core_health_calibrated_verdict['status']}",
                f"Guarded LB candidate: {core_health_calibrated_verdict['recommended_lb_candidate']}",
                f"Route pressure sensor: {core_health_calibrated_verdict['recommended_big_bet_sensor']}",
                f"Benchmark calibration: {core_health_calibrated.get('benchmark_calibration')}",
            ],
            "This is the direct bridge from generic core behavior to adapter release; public LB must still decide whether the guard is too conservative.",
        ),
        stage(
            "cross_listener_transport_decoder",
            "Cross-Listener Transport Decoder",
            "Uses target-listener posterior as a transport calibrator over route/fusion/core-safe action cells instead of directly generating actions.",
            [
                "decoder_order_jury_solver_readout.json",
                "decoder_boundary_tomography_readout.json",
                "target_listener_route_lift_action_audit.csv",
                "core_health_calibrated_release_readout.json",
            ],
            ["cross_listener_transport_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in cross_listener_transport.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Transport status: {cross_listener_verdict['status']}",
                f"Recommended LB sensor: {cross_listener_verdict['recommended_lb_sensor']}",
                f"Recommended big bet: {cross_listener_verdict['recommended_big_bet']}",
                f"Negative sensor: {cross_listener_transport.get('negative_sensor')}",
            ],
            "This stage does not claim listener posterior is a direct action head; it tests whether it can safely calibrate already supported actions.",
        ),
        stage(
            "counterfactual_listener_dropout_solver",
            "Counterfactual Listener-Dropout Solver",
            "Treats each listener as a removable view and releases only row-target action fields that remain coherent under listener dropout, while using failed public sensors as toxicity evidence.",
            [
                "decoder_order_jury_solver_readout.json",
                "decoder_boundary_tomography_readout.json",
                "cross_listener_transport_readout.json",
                "public_score_ledger.csv",
                "failed public sensor submissions",
            ],
            ["counterfactual_listener_dropout_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in counterfactual_listener_dropout.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Dropout status: {counterfactual_listener_dropout['status']}",
                f"Information sensor: {listener_dropout_verdict['recommended_information_sensor']}",
                f"Thesis sensor: {listener_dropout_verdict['recommended_thesis_sensor']}",
                f"Claim: {listener_dropout_verdict['claim']}",
            ],
            "This is a high-information public/private equation sensor; it can validate listener-invariant action health or kill that release geometry.",
        ),
        stage(
            "spectral_public_tangent_solver",
            "Spectral Public-Tangent Solver",
            "Treats post-H057 public failures as a low-rank negative representation and tests anti-tangent versus orthogonal residual action release.",
            [
                "public_score_ledger.csv",
                "current best submission",
                "counterfactual_listener_dropout_cells.csv",
                "public_loss_sparse_tomography cells",
                "route_frontier_action_decoder_audit.csv",
                "route_toxicity_fusion_decoder_audit.csv",
            ],
            ["spectral_public_tangent_readout_ko.md", *[
                str(item.get("submission_file"))
                for item in spectral_public_tangent.get("ranking", [])
                if isinstance(item, dict) and item.get("submission_file")
            ]],
            [
                f"Spectral status: {spectral_public_tangent['status']}",
                f"First bad-mode variance: {fmt(spectral_public_tangent['spectral']['first_mode_variance'], 4)}",
                f"Top-5 variance: {fmt(spectral_public_tangent['spectral']['top5_cumulative_variance'], 4)}",
                f"Information sensor: {spectral_tangent_verdict['recommended_information_sensor']}",
                f"Counter sensor: {spectral_tangent_verdict['recommended_counter_sensor']}",
            ],
            "This stage proves a negative representation geometry, not that the inverse direction is label-valid before public LB observes it.",
        ),
        stage(
            "negative_tangent_invariant_projection_solver",
            "Negative Tangent Invariant Projection Solver",
            "Projects the low-rank public-bad negative representation onto train target-route and subject-prior invariant coordinates before releasing row-target actions.",
            [
                "spectral_public_tangent_readout.json",
                "spectral_public_tangent_cells.csv",
                "ch2026_metrics_train.csv",
                "current best submission",
            ],
            ["negative_tangent_invariant_projection_readout.md", *[
                str(item.get("submission", {}).get("submission_file"))
                for item in negative_tangent_invariant.get("variants", {}).values()
                if isinstance(item, dict) and item.get("submission", {}).get("submission_file")
            ]],
            [
                f"Projection status: {negative_projection_verdict['status']}",
                f"Recommended variant: {negative_projection_verdict['recommended_variant']}",
                f"Projected cells: {negative_tangent_invariant['projected_cells']}",
                f"Core claim: {negative_tangent_invariant['core_claim']}",
            ],
            "This stage tests whether a negative representation is action-grade only after invariant projection; public LB must still validate the generated action field.",
        ),
        stage(
            "lb_conditioned_responsibility_solver",
            "LB-Conditioned Responsibility Solver",
            "Treats public LB as an external scalar listener and estimates row-target action responsibility from observed submission loss deltas.",
            [
                "public_score_ledger.csv",
                "spectral_public_tangent_readout.json",
                "negative_tangent_invariant_projection_readout.json",
                "route energy and subject-prior invariants",
                "current best submission",
            ],
            ["lb_conditioned_responsibility_readout_ko.md", *[
                str(item.get("submission", {}).get("submission_file"))
                for item in lb_conditioned_responsibility.get("variants", {}).values()
                if isinstance(item, dict) and item.get("submission", {}).get("submission_file")
            ]],
            [
                f"Responsibility status: {lb_responsibility_verdict['status']}",
                f"Recommended variant: {lb_responsibility_verdict['recommended_variant']}",
                f"LOO corr: {fmt(lb_conditioned_responsibility['fit']['loo_corr'], 4)}",
                f"Responsibility cells: {lb_conditioned_responsibility['responsibility_cells']}",
            ],
            "This is a scalar-listener inversion sensor; if public LB rejects it, responsibility is diagnostic but not yet a portable action equation.",
        ),
        stage(
            "action_decoder_ablation_suite",
            "Action Decoder Ablation Suite",
            "Ranks toxicity-first, support-first, route-first, route-toxicity fusion, decoder-jury, boundary-tomography, core-mediated, core-release-ablation, core-health-calibrated, cross-listener transport, listener-dropout, spectral, invariant-projection, and LB-conditioned responsibility alternatives as HS-JEPA module ablations.",
            [
                "row_support_strict_action_decoder_readout.json",
                "route_frontier_action_decoder_readout.json",
                "route_toxicity_fusion_decoder_readout.json",
                "decoder_order_jury_solver_readout.json",
                "decoder_boundary_tomography_readout.json",
                "core_mediated_action_release_readout.json",
                "core_release_ablation_probe_readout.json",
                "core_health_calibrated_release_readout.json",
                "cross_listener_transport_readout.json",
                "counterfactual_listener_dropout_readout.json",
                "spectral_public_tangent_readout.json",
                "negative_tangent_invariant_projection_readout.json",
                "lb_conditioned_responsibility_readout.json",
                "factorized_toxicity_decoder_stress_audit.json",
            ],
            ["hsjepa_action_decoder_ablation_suite_ko.md", "hsjepa_action_decoder_ablation_suite.csv"],
            [
                f"Suite status: {action_ablation_verdict['status']}",
                f"Recommended LB sensor: {action_ablation_verdict['recommended_lb_sensor']}",
                f"Open big-bet sensor: {action_ablation_verdict['big_bet_sensor']}",
            ],
            "This prioritizes public-sensor experiments; it is not a calibrated LB predictor.",
        ),
        stage(
            "route_energy_model",
            "Q/S Route Energy Model",
            "Learns a target-route manifold from train labels and scores whether an action breaks it.",
            ["train Q/S labels", "candidate corrected prediction vectors"],
            ["route energy", "route-conservation veto"],
            [
                f"Primary route z-score: {fmt(mechanism['primary_route_z'], 2)}",
                f"S2 route z-score: {fmt(mechanism['s2_route_z'], 2)}",
            ],
            "Route energy proves candidate-pool structure, not private leaderboard safety.",
        ),
        stage(
            "listener_invariant_contrastive_probe",
            "Listener-Invariant Contrastive Probe",
            "Tests whether listener responsibility and route-invariant action health select the same bundles.",
            ["listener_responsibility_ranked_cells.csv", "stagebridge/s2hub candidate bundles"],
            ["listener_invariant_contrastive_probe_ko.md", "listener_invariant_contrastive_scored_bundles.csv"],
            [
                f"Probe status: {contrastive_verdict['status']}",
                f"Listener-route rho: {fmt(contrastive_verdict['mean_listener_route_spearman'], 4)}",
                f"Contrastive overlap: {fmt(contrastive_verdict['mean_contrastive_overlap_rate'], 4)}",
            ],
            "This stage is a diagnostic; it does not create a new submission.",
        ),
        stage(
            "private_safe_toxicity_probe",
            "Private-Safe Toxicity Probe",
            "Tests whether toxicity head generalizes across bad public anchors and selects safer cells than matched nulls.",
            ["toxicity_candidate_cell_table.csv", "toxicity_action_audit.csv", "toxicity_anchor_ledger.csv"],
            ["private_safe_toxicity_probe_ko.md", "private_safe_toxicity_loo_anchor_metrics.csv"],
            [
                f"Probe status: {toxicity_verdict['status']}",
                f"Mean LOO bad-anchor AUC: {fmt(toxicity_verdict['mean_loo_bad_anchor_auc'], 4)}",
                f"Worst LOO bad-anchor AUC: {fmt(toxicity_verdict['worst_loo_bad_anchor_auc'], 4)}",
                f"Safety z vs matched null: {fmt(toxicity_verdict['selected_safety_z_vs_matched_null'], 4)}",
            ],
            "This stage supports toxicity diagnostics, not a private-LB safety guarantee.",
        ),
        stage(
            "hardworld_toxicity_factorization_probe",
            "Hard-World Toxicity Factorization Probe",
            "Tests whether the H088 hard-world toxicity mode is anti-correlated with broad public-bad toxicity.",
            ["private_safe_toxicity_probe.json", "toxicity_candidate_cell_table.csv", "toxicity_anchor_ledger.csv"],
            ["hardworld_toxicity_factorization_probe_ko.md", "hardworld_toxicity_factorization_sectors.csv"],
            [
                f"Probe status: {hardworld_verdict['status']}",
                f"Broad->H088 AUC: {fmt(hardworld_verdict['broad_predicts_hardworld_auc'], 4)}",
                f"Broad/H088 rho: {fmt(hardworld_verdict['broad_hardworld_spearman'], 4)}",
                f"Joint safety z: {fmt(hardworld_verdict['selected_joint_safety_z'], 4)}",
            ],
            "This diagnostic stage says action-health should be factorized; the following decoder stage is the submission translation.",
        ),
        stage(
            "factorized_toxicity_decoder_candidate",
            "Factorized Toxicity Decoder Candidate",
            "Translates broad-public and hard-world toxicity heads into upload-safe row-target action candidates.",
            ["hardworld_toxicity_factorization_sectors.csv", "current best prediction", "public-sensitive teacher support"],
            [
                "factorized_toxicity_decoder_readout_ko.md",
                *[
                    str(item.get("submission_file"))
                    for item in factorized_variants.values()
                    if isinstance(item, dict) and item.get("submission_file")
                ],
            ],
            [
                f"Decoder variants: {', '.join(sorted(factorized_variants))}",
                f"Upload-safe variants: {sum(1 for item in factorized_variants.values() if isinstance(item, dict) and item.get('validation', {}).get('upload_safe'))}/{len(factorized_variants)}",
            ],
            "This creates competition submissions, but their public/private score impact remains unverified until external submission.",
        ),
        stage(
            "factorized_toxicity_decoder_stress_audit",
            "Factorized Toxicity Decoder Stress Audit",
            "Compares factorized decoder variants against target-only and source-matched feasible null action fields.",
            ["factorized_toxicity_decoder_readout.json", "hardworld_toxicity_factorization_sectors.csv"],
            ["factorized_toxicity_decoder_stress_audit_ko.md", "factorized_toxicity_decoder_stress_summary.csv"],
            [
                f"Stress status: {factorized_stress['status']}",
                f"Supported variants: {', '.join(factorized_supported) if factorized_supported else 'none'}",
                f"Iterations: {factorized_stress['iterations']}",
            ],
            "This is local action-health evidence; external public/private LB remains a separate sensor.",
        ),
        stage(
            "driver_action_field",
            "Public-Sensitive Driver Action Field",
            "Selects sparse row-target cells that public sensor evidence says are worth moving.",
            ["public action anchors", "current best prediction"],
            ["driver candidate pool"],
            [
                f"Score breakthrough delta: {fmt(public['current_delta_vs_pre_breakthrough'], 10)}",
                f"Evidence roles: {', '.join(evidence['role'].astype(str))}",
            ],
            "This stage is deliberately separated from the OG human-state representation claim.",
        ),
        stage(
            "route_conserving_s2_bridge_decoder",
            "Route-Conserving S2 Bridge Decoder",
            "Pairs driver cells with same-row bridge cells that lower route energy and repeatedly use S2 as listener/hub.",
            ["driver candidate pool", "route energy", "S2 listener score"],
            ["sparse row-target correction field"],
            [
                f"Primary route delta vs null: {fmt(primary['mean_route_energy_delta'], 5)} vs {fmt(primary['null_mean_route_energy_delta'], 5)}",
                f"S2 usage vs null: {fmt(s2['s2_any_rate'], 3)} vs {fmt(s2['null_s2_any_rate'], 3)}",
            ],
            "S2 is a decoder listener/hub in this action space, not a universal sleep physiology claim.",
        ),
        stage(
            "submission_packager",
            "Role-Based Submission Packager",
            "Packages three role-based outputs without requiring historical version names.",
            ["sparse correction field", "submission sample key contract"],
            list(role_outputs.values()),
            [
                f"Upload-safe roles: {', '.join(sorted(validation['upload_results']))}",
                f"Validation passed: {validation['passed']}",
            ],
            "Upload safety is a format guarantee, not a score guarantee.",
        ),
        stage(
            "mechanism_ablation_knockout",
            "Mechanism Ablation Knockout",
            "Records which alternative worldviews public sensors and local stress audits killed or preserved.",
            ["public score ledger", "route-conserving stress audit", "architecture readiness report"],
            ["hsjepa_mechanism_ablation_report_ko.md"],
            [
                f"Public worldviews killed: {ablation['public_worldviews_killed']}",
                f"Public worldviews survived: {ablation['public_worldviews_survived']}",
                f"Ablation status: {ablation['status']}",
            ],
            "This explains mechanism evidence; it is not a new private-score guarantee.",
        ),
        stage(
            "general_architecture_boundary",
            "General Architecture Boundary",
            "Separates reusable HS-JEPA modules from the sleep-competition S2/public-sensor instantiation.",
            ["architecture readiness report", "mechanism ablation report"],
            ["hsjepa_generality_report_ko.md"],
            [
                f"Generality status: {generality['status']}",
                f"Portability checks: {generality['passed_checks']}/{generality['total_checks']}",
                f"Nonblocking boundaries: {', '.join(generality['nonblocking_boundaries'])}",
            ],
            "The current strongest case study still uses a public-sensor assignment teacher.",
        ),
        stage(
            "sleep_competition_adapter",
            "Sleep Competition Adapter",
            "Maps HS-JEPA Core into Q/S listeners, route energy, public-sensor action evidence, and upload-safe sparse row-target outputs.",
            ["HS-JEPA core manifest", "OG data", "public sensor ledger", "route-conserving package"],
            ["sleep_competition_adapter_report_ko.md", "hsjepa_big_bet_queue_ko.md"],
            [
                f"Adapter status: {adapter['status']}",
                f"Adapter score delta: {fmt(adapter['score_evidence']['delta'], 10)}",
                f"Big-bet count: {big_bets['count']}",
            ],
            "This adapter is a competition case study; it is not the general HS-JEPA architecture.",
        ),
        stage(
            "core_adapter_boundary_audit",
            "Core/Adapter Boundary Audit",
            "Statically verifies that HS-JEPA Core has no operational dependency on competition adapters and that the adapter depends on the core contract.",
            ["hsjepa_core_manifest.json", "hsjepa_core_ablation_contract.json", "sleep_competition_adapter_report.json", "run_full_team_hsjepa_package.py"],
            ["hsjepa_core_adapter_boundary_audit_ko.md", "hsjepa_core_adapter_boundary_audit.json"],
            [
                f"Boundary audit status: {boundary_audit['status']}",
                f"Boundary audit checks: {boundary_audit['passed_checks']}/{boundary_audit['total_checks']}",
                f"Core import violations: {len(boundary_audit.get('core_import_violations', []))}",
            ],
            "This verifies architecture separation; it does not create a new prediction or score guarantee.",
        ),
        stage(
            "claim_readiness_and_paper_packet",
            "Claim Readiness and Paper Packet",
            "Converts the runnable package into paper/team-facing evidence and method text.",
            ["core manifest", "sleep adapter report", "core/adapter boundary audit", "package outputs", "stress audit", "reproducibility contract", "mechanism ablation report", "generality report"],
            [
                "hsjepa_core_manifest_ko.md",
                "sleep_competition_adapter_report_ko.md",
                "hsjepa_architecture_readiness_report.md",
                "hsjepa_paper_method_packet_ko.md",
                "hsjepa_mechanism_ablation_report_ko.md",
                "hsjepa_generality_report_ko.md",
                "hsjepa_core_adapter_boundary_audit_ko.md",
            ],
            [
                f"Readiness status: {readiness['status']}",
                f"Readiness gates: {readiness['passed_gates']}/{readiness['total_gates']}",
                f"Method title: {method['title']}",
            ],
            "Paper claims must keep representation, public sensor, and action decoder separated.",
        ),
    ]

    edges = [
        ["hsjepa_core_architecture", "hsjepa_core_reference_run"],
        ["hsjepa_core_architecture", "hsjepa_core_module_benchmark"],
        ["hsjepa_core_reference_run", "hsjepa_core_module_benchmark"],
        ["hsjepa_core_module_benchmark", "general_architecture_boundary"],
        ["hsjepa_core_module_benchmark", "claim_readiness_and_paper_packet"],
        ["hsjepa_core_reference_run", "sleep_competition_adapter"],
        ["hsjepa_core_reference_run", "core_adapter_boundary_audit"],
        ["hsjepa_core_reference_run", "claim_readiness_and_paper_packet"],
        ["hsjepa_core_architecture", "og_raw_lifestyle_context"],
        ["hsjepa_core_architecture", "human_state_listener_context"],
        ["hsjepa_core_architecture", "route_energy_model"],
        ["og_raw_lifestyle_context", "human_state_listener_context"],
        ["og_raw_lifestyle_context", "route_energy_model"],
        ["human_state_listener_context", "og_only_assignment_probe"],
        ["og_only_assignment_probe", "general_architecture_boundary"],
        ["og_only_assignment_probe", "assignment_gap_decomposition"],
        ["assignment_gap_decomposition", "general_architecture_boundary"],
        ["assignment_gap_decomposition", "hidden_row_support_sensor"],
        ["hidden_row_support_sensor", "general_architecture_boundary"],
        ["hidden_row_support_sensor", "sleep_competition_adapter"],
        ["hidden_row_support_sensor", "masked_row_support_objective"],
        ["masked_row_support_objective", "general_architecture_boundary"],
        ["masked_row_support_objective", "sleep_competition_adapter"],
        ["masked_row_support_objective", "row_support_strict_action_decoder"],
        ["row_support_strict_action_decoder", "sleep_competition_adapter"],
        ["row_support_strict_action_decoder", "claim_readiness_and_paper_packet"],
        ["row_support_strict_action_decoder", "route_frontier_action_decoder"],
        ["route_frontier_action_decoder", "sleep_competition_adapter"],
        ["route_frontier_action_decoder", "claim_readiness_and_paper_packet"],
        ["row_support_strict_action_decoder", "action_decoder_ablation_suite"],
        ["route_frontier_action_decoder", "action_decoder_ablation_suite"],
        ["route_frontier_action_decoder", "route_toxicity_fusion_decoder"],
        ["hardworld_toxicity_factorization_probe", "route_toxicity_fusion_decoder"],
        ["route_frontier_action_decoder", "decoder_order_jury_solver"],
        ["route_toxicity_fusion_decoder", "decoder_order_jury_solver"],
        ["decoder_order_jury_solver", "action_decoder_ablation_suite"],
        ["decoder_order_jury_solver", "sleep_competition_adapter"],
        ["decoder_order_jury_solver", "claim_readiness_and_paper_packet"],
        ["decoder_order_jury_solver", "decoder_boundary_tomography_solver"],
        ["decoder_boundary_tomography_solver", "action_decoder_ablation_suite"],
        ["decoder_boundary_tomography_solver", "sleep_competition_adapter"],
        ["decoder_boundary_tomography_solver", "claim_readiness_and_paper_packet"],
        ["hsjepa_core_architecture", "core_mediated_action_release"],
        ["decoder_order_jury_solver", "core_mediated_action_release"],
        ["decoder_boundary_tomography_solver", "core_mediated_action_release"],
        ["core_mediated_action_release", "action_decoder_ablation_suite"],
        ["core_mediated_action_release", "sleep_competition_adapter"],
        ["core_mediated_action_release", "claim_readiness_and_paper_packet"],
        ["core_mediated_action_release", "core_release_ablation_probe"],
        ["hsjepa_core_module_benchmark", "core_health_calibrated_release"],
        ["core_mediated_action_release", "core_health_calibrated_release"],
        ["core_release_ablation_probe", "action_decoder_ablation_suite"],
        ["core_release_ablation_probe", "sleep_competition_adapter"],
        ["core_release_ablation_probe", "claim_readiness_and_paper_packet"],
        ["core_release_ablation_probe", "core_health_calibrated_release"],
        ["core_health_calibrated_release", "action_decoder_ablation_suite"],
        ["core_health_calibrated_release", "sleep_competition_adapter"],
        ["core_health_calibrated_release", "claim_readiness_and_paper_packet"],
        ["decoder_order_jury_solver", "cross_listener_transport_decoder"],
        ["decoder_boundary_tomography_solver", "cross_listener_transport_decoder"],
        ["core_health_calibrated_release", "cross_listener_transport_decoder"],
        ["cross_listener_transport_decoder", "action_decoder_ablation_suite"],
        ["cross_listener_transport_decoder", "sleep_competition_adapter"],
        ["cross_listener_transport_decoder", "claim_readiness_and_paper_packet"],
        ["cross_listener_transport_decoder", "counterfactual_listener_dropout_solver"],
        ["decoder_order_jury_solver", "counterfactual_listener_dropout_solver"],
        ["decoder_boundary_tomography_solver", "counterfactual_listener_dropout_solver"],
        ["public_lb_sensor", "counterfactual_listener_dropout_solver"],
        ["counterfactual_listener_dropout_solver", "spectral_public_tangent_solver"],
        ["public_lb_sensor", "spectral_public_tangent_solver"],
        ["spectral_public_tangent_solver", "negative_tangent_invariant_projection_solver"],
        ["route_energy_model", "negative_tangent_invariant_projection_solver"],
        ["human_state_listener_context", "negative_tangent_invariant_projection_solver"],
        ["public_lb_sensor", "lb_conditioned_responsibility_solver"],
        ["spectral_public_tangent_solver", "lb_conditioned_responsibility_solver"],
        ["negative_tangent_invariant_projection_solver", "lb_conditioned_responsibility_solver"],
        ["route_energy_model", "lb_conditioned_responsibility_solver"],
        ["human_state_listener_context", "lb_conditioned_responsibility_solver"],
        ["lb_conditioned_responsibility_solver", "action_decoder_ablation_suite"],
        ["lb_conditioned_responsibility_solver", "sleep_competition_adapter"],
        ["lb_conditioned_responsibility_solver", "claim_readiness_and_paper_packet"],
        ["negative_tangent_invariant_projection_solver", "action_decoder_ablation_suite"],
        ["negative_tangent_invariant_projection_solver", "sleep_competition_adapter"],
        ["negative_tangent_invariant_projection_solver", "claim_readiness_and_paper_packet"],
        ["spectral_public_tangent_solver", "action_decoder_ablation_suite"],
        ["spectral_public_tangent_solver", "sleep_competition_adapter"],
        ["spectral_public_tangent_solver", "claim_readiness_and_paper_packet"],
        ["counterfactual_listener_dropout_solver", "action_decoder_ablation_suite"],
        ["counterfactual_listener_dropout_solver", "sleep_competition_adapter"],
        ["counterfactual_listener_dropout_solver", "claim_readiness_and_paper_packet"],
        ["route_toxicity_fusion_decoder", "action_decoder_ablation_suite"],
        ["route_toxicity_fusion_decoder", "sleep_competition_adapter"],
        ["route_toxicity_fusion_decoder", "claim_readiness_and_paper_packet"],
        ["factorized_toxicity_decoder_stress_audit", "action_decoder_ablation_suite"],
        ["action_decoder_ablation_suite", "sleep_competition_adapter"],
        ["action_decoder_ablation_suite", "claim_readiness_and_paper_packet"],
        ["public_lb_sensor", "driver_action_field"],
        ["human_state_listener_context", "driver_action_field"],
        ["route_energy_model", "route_conserving_s2_bridge_decoder"],
        ["human_state_listener_context", "listener_invariant_contrastive_probe"],
        ["route_energy_model", "listener_invariant_contrastive_probe"],
        ["listener_invariant_contrastive_probe", "sleep_competition_adapter"],
        ["public_lb_sensor", "private_safe_toxicity_probe"],
        ["driver_action_field", "private_safe_toxicity_probe"],
        ["private_safe_toxicity_probe", "hardworld_toxicity_factorization_probe"],
        ["hardworld_toxicity_factorization_probe", "factorized_toxicity_decoder_candidate"],
        ["factorized_toxicity_decoder_candidate", "factorized_toxicity_decoder_stress_audit"],
        ["factorized_toxicity_decoder_stress_audit", "sleep_competition_adapter"],
        ["driver_action_field", "route_conserving_s2_bridge_decoder"],
        ["route_conserving_s2_bridge_decoder", "submission_packager"],
        ["hsjepa_core_architecture", "sleep_competition_adapter"],
        ["submission_packager", "sleep_competition_adapter"],
        ["public_lb_sensor", "sleep_competition_adapter"],
        ["public_lb_sensor", "mechanism_ablation_knockout"],
        ["route_conserving_s2_bridge_decoder", "mechanism_ablation_knockout"],
        ["mechanism_ablation_knockout", "claim_readiness_and_paper_packet"],
        ["mechanism_ablation_knockout", "general_architecture_boundary"],
        ["general_architecture_boundary", "claim_readiness_and_paper_packet"],
        ["sleep_competition_adapter", "core_adapter_boundary_audit"],
        ["hsjepa_core_architecture", "core_adapter_boundary_audit"],
        ["core_adapter_boundary_audit", "claim_readiness_and_paper_packet"],
        ["sleep_competition_adapter", "claim_readiness_and_paper_packet"],
        ["hsjepa_core_architecture", "claim_readiness_and_paper_packet"],
        ["submission_packager", "claim_readiness_and_paper_packet"],
        ["route_conserving_s2_bridge_decoder", "claim_readiness_and_paper_packet"],
    ]

    manifest = {
        "package": "Route-Conserving S2 Bridge HS-JEPA",
        "status": "pipeline_ready_with_boundary",
        "one_command": "python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py",
        "stage_count": len(stages),
        "edge_count": len(edges),
        "stages": stages,
        "edges": edges,
        "role_outputs": role_outputs,
        "boundary": {
            "is_pure_og_only_model": contract["boundary"]["is_pure_og_only_model"],
            "uses_public_lb_sensor": contract["boundary"]["uses_public_lb_sensor"],
            "human_state_role": contract["boundary"]["human_state_role"],
            "competition_decoder_role": contract["boundary"]["competition_decoder_role"],
        },
        "score_and_mechanism_summary": {
            "current_best_public_lb": public["current_best_public_lb"],
            "current_delta_vs_pre_public_equation": public["current_delta_vs_pre_breakthrough"],
            "primary_route_delta": primary["mean_route_energy_delta"],
            "primary_null_route_delta": primary["null_mean_route_energy_delta"],
            "s2_usage": s2["s2_any_rate"],
            "s2_null_usage": s2["null_s2_any_rate"],
            "human_state_cell_auc": human["cell_oof_auc_human_target_context"],
            "human_state_row_auc": human["row_oof_auc"],
            "public_worldviews_killed": ablation["public_worldviews_killed"],
            "public_worldviews_survived": ablation["public_worldviews_survived"],
            "generality_status": generality["status"],
            "generality_nonblocking_boundaries": generality["nonblocking_boundaries"],
            "core_status": core["status"],
            "core_module_benchmark_status": core_benchmark["status"],
            "core_module_benchmark_full_core_f1": core_benchmark["verdict"]["full_core_mean_f1"],
            "core_module_benchmark_action_health_fp_lift": core_benchmark["verdict"]["remove_action_health_false_positive_lift"],
            "core_module_benchmark_invariant_fp_lift": core_benchmark["verdict"]["remove_invariant_false_positive_lift"],
            "adapter_status": adapter["status"],
            "core_adapter_boundary_status": boundary_audit["status"],
            "big_bet_count": big_bets["count"],
            "og_only_assignment_probe_status": og_verdict["status"],
            "assignment_gap_decomposition_status": gap_verdict["status"],
            "assignment_gap_mean_row_support_gap": gap_verdict["mean_row_support_gap"],
            "hidden_row_support_sensor_status": row_support_verdict["status"],
            "hidden_row_support_best_family": row_support_verdict["best_portable_family"],
            "hidden_row_support_mean_row_auc": row_support_verdict["best_portable_mean_row_auc"],
            "hidden_row_support_mean_cell_recall": row_support_verdict["best_portable_mean_cell_recall_with_stage_prior"],
            "masked_row_support_objective_status": masked_row_support_verdict["status"],
            "masked_row_support_full_row_auc": masked_row_support_verdict["full_composite_mean_row_auc"],
            "masked_row_support_full_cell_recall": masked_row_support_verdict["full_composite_mean_cell_recall"],
            "masked_row_support_group_stress_auc": masked_row_support_verdict["group_stress_full_mean_auc"],
            "row_support_strict_action_decoder_status": row_support_decoder_verdict["status"],
            "row_support_strict_action_decoder_recommended": row_support_decoder_verdict["recommended_variant"],
            "row_support_strict_action_decoder_changed_cells": row_support_decoder_verdict["exploratory_changed_cells"],
            "row_support_strict_action_decoder_safety_z": row_support_decoder_verdict["exploratory_safety_z"],
            "route_frontier_action_decoder_status": route_frontier_verdict["status"],
            "route_frontier_action_decoder_recommended": route_frontier_verdict["recommended_variant"],
            "route_frontier_action_decoder_variant_scores": route_frontier_verdict["variant_scores"],
            "decoder_order_jury_solver_status": decoder_order_jury_verdict["status"],
            "decoder_order_jury_solver_recommended_lb_sensor": decoder_order_jury_verdict["recommended_lb_sensor"],
            "decoder_boundary_tomography_status": decoder_boundary_tomography_verdict["status"],
            "decoder_boundary_tomography_recommended_lb_sensor": decoder_boundary_tomography_verdict["recommended_lb_sensor"],
            "decoder_boundary_tomography_inventory": decoder_boundary_tomography.get("boundary_inventory"),
            "core_mediated_action_release_status": core_mediated_verdict["status"],
            "core_mediated_action_release_recommended_lb_sensor": core_mediated_verdict["recommended_lb_sensor"],
            "core_mediated_action_release_inventory": core_mediated_release.get("cell_inventory"),
            "core_release_ablation_probe_status": core_release_ablation_verdict["status"],
            "core_release_ablation_recommended_lb_candidate": core_release_ablation_verdict["recommended_lb_candidate"],
            "core_release_ablation_recommended_architecture_sensor": core_release_ablation_verdict["recommended_architecture_sensor"],
            "core_health_calibrated_release_status": core_health_calibrated_verdict["status"],
            "core_health_calibrated_recommended_lb_candidate": core_health_calibrated_verdict["recommended_lb_candidate"],
            "core_health_calibrated_recommended_big_bet_sensor": core_health_calibrated_verdict["recommended_big_bet_sensor"],
            "core_health_calibrated_recommended_pressure_sensor": core_health_calibrated_verdict["recommended_pressure_sensor"],
            "cross_listener_transport_status": cross_listener_verdict["status"],
            "cross_listener_transport_recommended_lb_sensor": cross_listener_verdict["recommended_lb_sensor"],
            "cross_listener_transport_recommended_big_bet": cross_listener_verdict["recommended_big_bet"],
            "cross_listener_transport_negative_sensor": cross_listener_transport.get("negative_sensor"),
            "counterfactual_listener_dropout_status": counterfactual_listener_dropout["status"],
            "counterfactual_listener_dropout_recommended_information_sensor": listener_dropout_verdict["recommended_information_sensor"],
            "counterfactual_listener_dropout_recommended_thesis_sensor": listener_dropout_verdict["recommended_thesis_sensor"],
            "counterfactual_listener_dropout_top_variants": counterfactual_listener_dropout.get("ranking", [])[:2],
            "spectral_public_tangent_status": spectral_public_tangent["status"],
            "spectral_public_tangent_first_mode_variance": spectral_public_tangent["spectral"]["first_mode_variance"],
            "spectral_public_tangent_top5_variance": spectral_public_tangent["spectral"]["top5_cumulative_variance"],
            "spectral_public_tangent_recommended_information_sensor": spectral_tangent_verdict["recommended_information_sensor"],
            "spectral_public_tangent_recommended_counter_sensor": spectral_tangent_verdict["recommended_counter_sensor"],
            "negative_tangent_invariant_projection_status": negative_projection_verdict["status"],
            "negative_tangent_invariant_projection_recommended": negative_projection_verdict["recommended_variant"],
            "negative_tangent_invariant_projection_projected_cells": negative_tangent_invariant["projected_cells"],
            "negative_tangent_invariant_projection_top_ranked": negative_projection_verdict["ranking"][:2],
            "lb_conditioned_responsibility_status": lb_responsibility_verdict["status"],
            "lb_conditioned_responsibility_recommended": lb_responsibility_verdict["recommended_variant"],
            "lb_conditioned_responsibility_loo_corr": lb_conditioned_responsibility["fit"]["loo_corr"],
            "lb_conditioned_responsibility_cells": lb_conditioned_responsibility["responsibility_cells"],
            "lb_conditioned_responsibility_top_ranked": lb_responsibility_verdict["ranking"][:2],
            "action_decoder_ablation_suite_status": action_ablation_verdict["status"],
            "action_decoder_ablation_suite_recommended_lb_sensor": action_ablation_verdict["recommended_lb_sensor"],
            "action_decoder_ablation_suite_big_bet_sensor": action_ablation_verdict["big_bet_sensor"],
            "listener_invariant_contrastive_probe_status": contrastive_verdict["status"],
            "private_safe_toxicity_probe_status": toxicity_verdict["status"],
            "hardworld_toxicity_factorization_probe_status": hardworld_verdict["status"],
            "factorized_toxicity_decoder_variant_count": len(factorized_variants),
            "factorized_toxicity_decoder_supported_variants": factorized_supported,
        },
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    MANIFEST_MD.write_text(build_markdown(manifest), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False))
    return manifest


def build_markdown(manifest: dict[str, object]) -> str:
    stage_rows = ["| Stage | Role | Key Evidence | Boundary |", "| --- | --- | --- | --- |"]
    for item in manifest["stages"]:
        evidence = "<br>".join(str(x) for x in item["evidence"])
        stage_rows.append(f"| `{item['id']}` | {item['role']} | {evidence} | {item['boundary']} |")

    role_rows = ["| Role | Output file |", "| --- | --- |"]
    for role, output in sorted(manifest["role_outputs"].items()):
        role_rows.append(f"| `{role}` | `{output}` |")

    return "\n".join(
        [
            "# HS-JEPA Pipeline Manifest",
            "",
            "이 문서는 팀원이 OG 데이터에서 최종 제출/논문 산출물까지 어떤 경로로 이어지는지 한눈에 추적하도록 만든 역할 기반 pipeline manifest다.",
            "",
            "## One-Command Entry",
            "",
            "```bash",
            manifest["one_command"],
            "```",
            "",
            "## Pipeline Diagram",
            "",
            "```mermaid",
            "flowchart TD",
            '    CORE["HS-JEPA core architecture"] --> A["OG raw lifestyle context"]',
            '    CORE --> C["Human-state listener context"]',
            '    CORE --> D["Q/S route energy model"]',
            '    A["OG raw lifestyle context"] --> C["Human-state listener context"]',
            '    A --> D["Q/S route energy model"]',
            '    C --> P1["OG-only assignment probe"]',
            '    P1 --> GAP["Assignment gap decomposition"]',
            '    GAP --> RSP["Hidden row-support sensor"]',
            '    RSP --> MRO["Masked row-support objective"]',
            '    MRO --> RSA["Row-support strict action decoder"]',
            '    RSA --> RFA["Route-frontier action decoder"]',
            '    RFA --> ADA["Action decoder ablation suite"]',
            '    MRO --> GEN["General architecture boundary"]',
            '    B["Public LB sensor ledger"] --> E["Public-sensitive driver action field"]',
            '    C --> E',
            '    D --> F["Route-conserving S2 bridge decoder"]',
            '    C --> P2["Listener-invariant contrastive probe"]',
            '    D --> P2',
            '    B --> P3["Private-safe toxicity probe"]',
            '    E --> P3',
            '    P3 --> P4["Hard-world toxicity factorization probe"]',
            '    P4 --> P5["Factorized toxicity decoder candidate"]',
            '    P5 --> P6["Factorized toxicity decoder stress audit"]',
            '    P6 --> ADA',
            '    RSA --> ADA',
            '    CORE --> CMA["Core-mediated action release"]',
            '    CMA --> CRA["Core release ablation probe"]',
            '    CRA --> ADA',
            '    CRA --> ADAPT',
            '    RFA --> CLT["Cross-listener transport decoder"]',
            '    CLT --> CLD["Counterfactual listener-dropout solver"]',
            '    B --> CLD',
            '    CLD --> SPT["Spectral public-tangent solver"]',
            '    B --> SPT',
            '    SPT --> ADA',
            '    SPT --> ADAPT',
            '    SPT --> LBR["LB-conditioned responsibility solver"]',
            '    NTP["Negative tangent invariant projection"] --> LBR',
            '    B --> LBR',
            '    LBR --> ADA',
            '    LBR --> ADAPT',
            '    CLD --> ADA',
            '    CLD --> ADAPT',
            '    E --> F',
            '    F --> G["Role-based submission packager"]',
            '    G --> ADAPT["Sleep competition adapter"]',
            '    CORE --> ADAPT',
            '    B --> ADAPT',
            '    P2 --> ADAPT',
            '    P3 --> ADAPT',
            '    P4 --> ADAPT',
            '    P6 --> ADAPT',
            '    RSP --> ADAPT',
            '    MRO --> ADAPT',
            '    RSA --> ADAPT',
            '    RFA --> ADAPT',
            '    ADA --> ADAPT',
            '    ADAPT --> BAUD["Core/adapter boundary audit"]',
            '    CORE --> BAUD',
            '    GEN --> H["Claim readiness and paper packet"]',
            '    BAUD --> H',
            '    ADAPT --> H["Claim readiness and paper packet"]',
            '    G --> H["Claim readiness and paper packet"]',
            '    F --> H',
            '    ADA --> H',
            "```",
            "",
            "## Stage Table",
            "",
            *stage_rows,
            "",
            "## Role-Based Outputs",
            "",
            *role_rows,
            "",
            "## Boundary",
            "",
            f"- Pure OG-only model: `{manifest['boundary']['is_pure_og_only_model']}`",
            f"- Uses public LB sensor: `{manifest['boundary']['uses_public_lb_sensor']}`",
            f"- Human-state role: `{manifest['boundary']['human_state_role']}`",
            f"- Competition decoder role: `{manifest['boundary']['competition_decoder_role']}`",
            "",
            "## Summary",
            "",
            "```text",
            "The reusable mechanism is HS-JEPA Core: hidden state -> listener -> action-health -> invariant decoder.",
            "The sleep competition adapter supplies Q/S listeners, public-sensor actions, route energy, and upload format.",
            "The boundary audit verifies that this is a real dependency split, not only a naming convention.",
            "The current LB breakthrough is adapter evidence; the paper claim must remain core-first.",
            "The next jackpot is either a better public/private action-health factorization or evidence that one HS-JEPA core constraint over-constrains real row-target release.",
            "```",
            "",
        ]
    )


def main() -> None:
    build_manifest()


if __name__ == "__main__":
    main()
