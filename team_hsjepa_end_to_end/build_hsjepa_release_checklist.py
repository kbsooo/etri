#!/usr/bin/env python3
"""Build the final team-release checklist for the HS-JEPA package.

This is the last gate a teammate can inspect before using the package in a
paper, presentation, or submission discussion.  It checks that the independent
reports agree with each other and that the package is still role-based rather
than historical-version based.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
import sys


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"

PACKAGE_JSON = OUT / "route_conserving_s2_bridge_package.json"
VALIDATION_JSON = OUT / "route_conserving_s2_bridge_validation_report.json"
CONTRACT_JSON = OUT / "hsjepa_reproducibility_contract.json"
READINESS_JSON = OUT / "hsjepa_architecture_readiness_report.json"
MECHANISM_ABLATION_JSON = OUT / "hsjepa_mechanism_ablation_report.json"
GENERALITY_JSON = OUT / "hsjepa_generality_report.json"
BOUNDARY_AUDIT_JSON = OUT / "hsjepa_core_adapter_boundary_audit.json"
METHOD_PACKET_JSON = OUT / "hsjepa_paper_method_packet.json"
PIPELINE_JSON = OUT / "hsjepa_pipeline_manifest.json"
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
ACTION_DECODER_ABLATION_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "action_decoder_ablation_suite" / "hsjepa_action_decoder_ablation_suite.json"
CONTRASTIVE_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "listener_invariant_contrastive_probe.json"
PRIVATE_TOXICITY_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "private_safe_toxicity_probe.json"
HARDWORLD_TOXICITY_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hardworld_toxicity_factorization_probe.json"
FACTORIZED_DECODER_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout.json"
FACTORIZED_STRESS_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit.json"

CHECKLIST_JSON = OUT / "hsjepa_release_checklist.json"
CHECKLIST_MD = OUT / "hsjepa_release_checklist_ko.md"

EXPECTED_ROLES = {"competition_primary", "interpretable_s2_hub", "human_state_probe"}


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(value: object, digits: int = 6) -> str:
    if value is None:
        return "n/a"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def check(name: str, passed: bool, evidence: str, required: bool = True) -> dict[str, object]:
    return {
        "check": name,
        "status": "PASS" if passed else ("FAIL" if required else "WARN"),
        "passed": bool(passed),
        "required": bool(required),
        "evidence": evidence,
    }


def require_inputs() -> list[dict[str, object]]:
    rows = []
    for path in [
        PACKAGE_JSON,
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
        ACTION_DECODER_ABLATION_JSON,
        CONTRASTIVE_PROBE_JSON,
        PRIVATE_TOXICITY_PROBE_JSON,
        HARDWORLD_TOXICITY_PROBE_JSON,
        FACTORIZED_DECODER_JSON,
        FACTORIZED_STRESS_JSON,
        PIPELINE_JSON,
    ]:
        rows.append(check(f"exists:{path.name}", path.exists(), str(path.relative_to(ROOT))))
    return rows


def build_checklist() -> dict[str, object]:
    rows = require_inputs()
    if not all(row["passed"] for row in rows):
        required_failures = [row for row in rows if row["required"] and not row["passed"]]
        result = {
            "package": "Route-Conserving S2 Bridge HS-JEPA",
            "status": "release_blocked_missing_inputs",
            "passed_checks": sum(1 for row in rows if row["passed"]),
            "total_checks": len(rows),
            "required_failures": required_failures,
            "checks": rows,
            "release_claim": "Release is blocked because one or more required report inputs are missing.",
            "boundary": {
                "not_pure_og_only": True,
                "private_lb_not_proven": True,
                "human_state_not_standalone_assignment_solver": True,
            },
        }
        CHECKLIST_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
        CHECKLIST_MD.write_text(build_markdown(result), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return result

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
    action_decoder_ablation = read_json(ACTION_DECODER_ABLATION_JSON)
    contrastive_probe = read_json(CONTRASTIVE_PROBE_JSON)
    private_toxicity_probe = read_json(PRIVATE_TOXICITY_PROBE_JSON)
    hardworld_toxicity_probe = read_json(HARDWORLD_TOXICITY_PROBE_JSON)
    factorized_decoder = read_json(FACTORIZED_DECODER_JSON)
    factorized_stress = read_json(FACTORIZED_STRESS_JSON)
    pipeline = read_json(PIPELINE_JSON)

    packaged = package.get("packaged_submissions", {})
    role_keys = set(packaged) if isinstance(packaged, dict) else set()
    upload_results = validation.get("upload_results", {})
    public = readiness.get("public_breakthrough", {})
    human = readiness.get("human_state", {})
    mechanism = readiness.get("mechanism", {})
    primary = mechanism.get("primary", {}) if isinstance(mechanism, dict) else {}
    s2 = mechanism.get("s2_listener", {}) if isinstance(mechanism, dict) else {}
    boundary = contract.get("boundary", {})
    role_outputs = pipeline.get("role_outputs", {})
    stress_ablation = ablation.get("stress_ablation", [])
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
    action_ablation_verdict = action_decoder_ablation.get("verdict", {})
    contrastive_verdict = contrastive_probe.get("verdict", {})
    toxicity_verdict = private_toxicity_probe.get("verdict", {})
    hardworld_verdict = hardworld_toxicity_probe.get("verdict", {})
    factorized_variants = factorized_decoder.get("variants", {})
    factorized_stress_variants = factorized_stress.get("variants", {})
    factorized_supported = [
        name
        for name, item in factorized_stress_variants.items()
        if isinstance(item, dict) and item.get("verdict", {}).get("status") == "factorized_decoder_stress_supported"
    ]

    rows.extend(
        [
            check("validation_passed", bool(validation.get("passed")), f"passed={validation.get('passed')}"),
            check(
                "contract_passed",
                bool(contract.get("passed")) and int(contract.get("required_missing_count", 1)) == 0,
                f"passed={contract.get('passed')}, missing={contract.get('required_missing_count')}",
            ),
            check(
                "readiness_passed",
                readiness.get("status") == "paper_ready_with_boundary"
                and int(readiness.get("passed_gates", 0)) == int(readiness.get("total_gates", -1)),
                f"status={readiness.get('status')}, gates={readiness.get('passed_gates')}/{readiness.get('total_gates')}",
            ),
            check(
                "score_breakthrough_large_enough",
                float(public.get("current_delta_vs_pre_breakthrough", 0.0)) <= -0.005,
                f"delta={fmt(public.get('current_delta_vs_pre_breakthrough'), 10)}",
            ),
            check(
                "route_conserving_mechanism",
                float(primary.get("mean_route_energy_delta", 0.0)) < float(primary.get("null_mean_route_energy_delta", -1.0))
                and float(primary.get("mean_energy_rank_pct", 1.0)) <= 0.25,
                (
                    f"route_delta={fmt(primary.get('mean_route_energy_delta'), 5)}, "
                    f"null={fmt(primary.get('null_mean_route_energy_delta'), 5)}, "
                    f"rank={fmt(primary.get('mean_energy_rank_pct'), 3)}"
                ),
            ),
            check(
                "s2_listener_hub_mechanism",
                float(s2.get("s2_any_rate", 0.0)) >= 0.95
                and float(s2.get("mean_s2hub_rank_pct", 1.0)) <= 0.25,
                (
                    f"s2_usage={fmt(s2.get('s2_any_rate'), 3)}, "
                    f"null={fmt(s2.get('null_s2_any_rate'), 3)}, "
                    f"rank={fmt(s2.get('mean_s2hub_rank_pct'), 3)}"
                ),
            ),
            check(
                "human_state_boundary",
                float(human.get("cell_oof_auc_human_target_context", 0.0)) >= 0.70
                and float(human.get("row_oof_auc", 1.0)) < 0.60,
                (
                    f"cell_auc={fmt(human.get('cell_oof_auc_human_target_context'), 3)}, "
                    f"row_auc={fmt(human.get('row_oof_auc'), 3)}"
                ),
            ),
            check(
                "mechanism_ablation_ready",
                ablation.get("status") == "mechanism_ablation_ready"
                and int(ablation.get("public_worldviews_killed", 0)) >= 4
                and int(ablation.get("public_worldviews_survived", 0)) >= 2,
                (
                    f"status={ablation.get('status')}, "
                    f"killed={ablation.get('public_worldviews_killed')}, "
                    f"survived={ablation.get('public_worldviews_survived')}"
                ),
            ),
            check(
                "mechanism_shortcuts_rejected",
                len(stress_ablation) >= 2
                and all(str(item.get("verdict", "")).startswith("killed") for item in stress_ablation if isinstance(item, dict)),
                f"stress_verdicts={[item.get('verdict') for item in stress_ablation if isinstance(item, dict)]}",
            ),
            check(
                "generality_boundary_explicit",
                generality.get("status") == "general_architecture_separated_with_case_boundary"
                and int(generality.get("passed_checks", 0)) >= 5
                and "remaining_generality_gap" in set(generality.get("nonblocking_boundaries", [])),
                (
                    f"status={generality.get('status')}, "
                    f"checks={generality.get('passed_checks')}/{generality.get('total_checks')}, "
                    f"boundaries={generality.get('nonblocking_boundaries')}"
                ),
            ),
            check(
                "core_adapter_separation_explicit",
                core.get("status") == "core_ready_for_adapter"
                and adapter.get("status") == "adapter_ready_with_public_sensor_boundary"
                and int(core.get("passed_gates", 0)) == int(core.get("total_gates", -1)),
                (
                    f"core={core.get('status')} "
                    f"({core.get('passed_gates')}/{core.get('total_gates')}), "
                    f"adapter={adapter.get('status')}"
                ),
            ),
            check(
                "core_adapter_boundary_audit_verified",
                boundary_audit.get("status") == "core_adapter_boundary_verified"
                and int(boundary_audit.get("passed_checks", 0)) == int(boundary_audit.get("total_checks", -1)),
                (
                    f"status={boundary_audit.get('status')}, "
                    f"checks={boundary_audit.get('passed_checks')}/{boundary_audit.get('total_checks')}"
                ),
            ),
            check(
                "core_ablation_contract_present",
                core_ablation.get("status") == "ablation_contract_ready"
                and len(core_ablation.get("ablations", [])) >= 6,
                f"status={core_ablation.get('status')}, ablations={len(core_ablation.get('ablations', []))}",
            ),
            check(
                "core_reference_executable",
                core_reference.get("status") == "core_reference_ready"
                and int(core_reference.get("full_core", {}).get("summary", {}).get("released_count", 0)) >= 1
                and len(core_reference.get("ablations", {})) >= 3,
                (
                    f"status={core_reference.get('status')}, "
                    f"released={core_reference.get('full_core', {}).get('summary', {}).get('released_count')}, "
                    f"ablations={len(core_reference.get('ablations', {}))}"
                ),
            ),
            check(
                "core_module_benchmark_executable",
                core_benchmark.get("status") == "core_module_benchmark_ready"
                and float(core_benchmark.get("verdict", {}).get("full_core_mean_f1", 0.0)) >= 0.90
                and int(core_benchmark.get("verdict", {}).get("remove_action_health_false_positive_lift", 0)) >= 1,
                (
                    f"status={core_benchmark.get('status')}, "
                    f"scenarios={core_benchmark.get('scenario_count')}, "
                    f"full_f1={fmt(core_benchmark.get('verdict', {}).get('full_core_mean_f1'), 4)}, "
                    f"action_health_fp_lift={core_benchmark.get('verdict', {}).get('remove_action_health_false_positive_lift')}, "
                    f"invariant_fp_lift={core_benchmark.get('verdict', {}).get('remove_invariant_false_positive_lift')}"
                ),
            ),
            check(
                "big_bet_queue_high_ceiling",
                big_bets.get("status") == "big_bet_queue_ready"
                and len(big_bets.get("bets", [])) >= 3
                and any(float(bet.get("expected_public_lb_delta_if_true", 0.0)) <= -0.002 for bet in big_bets.get("bets", [])),
                f"status={big_bets.get('status')}, count={len(big_bets.get('bets', []))}",
            ),
            check(
                "og_only_assignment_probe_recorded",
                og_probe.get("status") == "probe_ready"
                and og_verdict.get("status") in {
                    "og_unsupervised_assignment_signal_alive",
                    "teacher_distillation_alive_but_not_portable",
                    "og_only_assignment_replacement_not_ready",
                },
                (
                    f"status={og_verdict.get('status')}, "
                    f"pure_recall={fmt(og_verdict.get('pure_og_row_cap2_mean_recall'), 4)}, "
                    f"distilled_recall={fmt(og_verdict.get('distilled_row_cap2_mean_recall'), 4)}"
                ),
            ),
            check(
                "assignment_gap_decomposition_recorded",
                assignment_gap.get("status") == "probe_ready"
                and gap_verdict.get("status") in {
                    "portable_assignment_signal_alive",
                    "row_support_is_primary_bottleneck",
                    "distilled_capacity_alive_but_not_portable",
                    "assignment_gap_not_explained_by_current_human_context",
                }
                and float(gap_verdict.get("mean_row_oracle_stage_recall", 0.0)) > float(gap_verdict.get("mean_best_portable_recall", 1.0)),
                (
                    f"status={gap_verdict.get('status')}, "
                    f"portable={fmt(gap_verdict.get('mean_best_portable_recall'), 4)}, "
                    f"row_oracle={fmt(gap_verdict.get('mean_row_oracle_stage_recall'), 4)}, "
                    f"row_gap={fmt(gap_verdict.get('mean_row_support_gap'), 4)}"
                ),
            ),
            check(
                "hidden_row_support_sensor_recorded",
                row_support_sensor.get("status") == "probe_ready"
                and row_support_verdict.get("status") in {
                    "portable_row_support_sensor_alive_partial",
                    "adapter_row_support_upper_bound_only",
                    "row_support_sensor_not_found",
                }
                and float(row_support_verdict.get("best_portable_mean_row_auc", 0.0)) >= 0.60
                and float(row_support_verdict.get("best_portable_mean_auc_z_vs_permuted_train", 0.0)) > 2.0,
                (
                    f"status={row_support_verdict.get('status')}, "
                    f"family={row_support_verdict.get('best_portable_family')}, "
                    f"row_auc={fmt(row_support_verdict.get('best_portable_mean_row_auc'), 4)}, "
                    f"cell_recall={fmt(row_support_verdict.get('best_portable_mean_cell_recall_with_stage_prior'), 4)}, "
                    f"auc_z={fmt(row_support_verdict.get('best_portable_mean_auc_z_vs_permuted_train'), 4)}"
                ),
            ),
            check(
                "masked_row_support_objective_recorded",
                masked_row_support.get("status") == "probe_ready"
                and masked_row_support_verdict.get("status") in {
                    "masked_row_support_objective_supported_with_stress_boundary",
                    "masked_row_support_objective_alive_but_fragile",
                    "masked_row_support_objective_not_supported",
                }
                and float(masked_row_support_verdict.get("full_composite_mean_row_auc", 0.0)) >= 0.70
                and float(masked_row_support_verdict.get("full_composite_mean_cell_recall", 0.0)) >= 0.25,
                (
                    f"status={masked_row_support_verdict.get('status')}, "
                    f"row_auc={fmt(masked_row_support_verdict.get('full_composite_mean_row_auc'), 4)}, "
                    f"cell_recall={fmt(masked_row_support_verdict.get('full_composite_mean_cell_recall'), 4)}, "
                    f"group_stress_auc={fmt(masked_row_support_verdict.get('group_stress_full_mean_auc'), 4)}"
                ),
            ),
            check(
                "row_support_strict_action_decoder_recorded",
                row_support_decoder.get("status") in {
                    "row_support_action_decoder_alive_with_route_tradeoff",
                    "row_support_action_decoder_too_conservative",
                    "row_support_action_decoder_not_ready",
                }
                and row_support_decoder_verdict.get("recommended_variant") in row_support_decoder.get("variants", {})
                and int(row_support_decoder_verdict.get("exploratory_changed_cells", 0)) >= 20
                and float(row_support_decoder_verdict.get("exploratory_safety_z", 0.0)) >= 2.0
                and all(
                    isinstance(item, dict) and item.get("validation", {}).get("upload_safe") is True
                    for item in row_support_decoder.get("variants", {}).values()
                ),
                (
                    f"status={row_support_decoder_verdict.get('status')}, "
                    f"recommended={row_support_decoder_verdict.get('recommended_variant')}, "
                    f"changed={row_support_decoder_verdict.get('exploratory_changed_cells')}, "
                    f"safety_z={fmt(row_support_decoder_verdict.get('exploratory_safety_z'), 2)}, "
                    f"combined_z={fmt(row_support_decoder_verdict.get('exploratory_combined_z'), 2)}"
                ),
            ),
            check(
                "route_frontier_action_decoder_recorded",
                route_frontier_decoder.get("status")
                in {
                    "route_frontier_action_decoder_alive_with_matched_boundary",
                    "route_frontier_action_decoder_not_release_ready",
                }
                and route_frontier_verdict.get("recommended_variant") in route_frontier_decoder.get("variants", {})
                and any(
                    isinstance(item, dict)
                    and int(item.get("changed_cells", 0)) >= 20
                    and float(item.get("broad_route_z", 0.0)) >= 2.0
                    and float(item.get("matched_score_z", 0.0)) >= 2.0
                    and bool(item.get("upload_safe"))
                    for item in route_frontier_verdict.get("variant_scores", [])
                )
                and all(
                    isinstance(item, dict) and item.get("validation", {}).get("upload_safe") is True
                    for item in route_frontier_decoder.get("variants", {}).values()
                ),
                (
                    f"status={route_frontier_verdict.get('status')}, "
                    f"recommended={route_frontier_verdict.get('recommended_variant')}, "
                    f"scores={route_frontier_verdict.get('variant_scores')}"
                ),
            ),
            check(
                "action_decoder_ablation_suite_recorded",
                action_decoder_ablation.get("status")
                in {
                    "action_decoder_ablation_ready_route_frontier_leads",
                    "action_decoder_ablation_ready_route_toxicity_fusion_leads",
                    "action_decoder_ablation_ready_decoder_jury_leads",
                    "action_decoder_ablation_ready_boundary_tomography_leads",
                    "action_decoder_ablation_ready_core_mediated_release_leads",
                    "action_decoder_ablation_ready_core_release_ablation_leads",
                    "action_decoder_ablation_ready_non_route_leads",
                }
                and isinstance(action_ablation_verdict.get("recommended_lb_sensor"), dict)
                and isinstance(action_ablation_verdict.get("big_bet_sensor"), dict)
                and len(action_decoder_ablation.get("ranking", [])) >= 6
                and any(
                    isinstance(item, dict)
                    and item.get("family") == "route_frontier"
                    and int(item.get("ablation_rank", 99)) <= 10
                    and bool(item.get("upload_safe"))
                    for item in action_decoder_ablation.get("ranking", [])
                ),
                (
                    f"status={action_ablation_verdict.get('status')}, "
                    f"recommended={action_ablation_verdict.get('recommended_lb_sensor')}, "
                    f"big_bet={action_ablation_verdict.get('big_bet_sensor')}"
                ),
            ),
            check(
                "route_toxicity_fusion_decoder_recorded",
                route_toxicity_fusion_decoder.get("status")
                in {
                    "route_toxicity_fusion_decoder_alive",
                    "route_toxicity_fusion_decoder_boundary",
                }
                and route_toxicity_fusion_verdict.get("recommended_variant") in route_toxicity_fusion_decoder.get("variants", {})
                and any(
                    isinstance(item, dict)
                    and int(item.get("changed_cells", 0)) >= 20
                    and float(item.get("toxicity_matched_fusion_z", 0.0)) >= 2.0
                    and bool(item.get("upload_safe"))
                    for item in route_toxicity_fusion_verdict.get("variant_scores", [])
                )
                and all(
                    isinstance(item, dict) and item.get("validation", {}).get("upload_safe") is True
                    for item in route_toxicity_fusion_decoder.get("variants", {}).values()
                ),
                (
                    f"status={route_toxicity_fusion_verdict.get('status')}, "
                    f"recommended={route_toxicity_fusion_verdict.get('recommended_variant')}, "
                    f"scores={route_toxicity_fusion_verdict.get('variant_scores')}"
                ),
            ),
            check(
                "decoder_order_jury_solver_recorded",
                decoder_order_jury.get("status")
                in {
                    "decoder_order_jury_ready",
                    "decoder_order_jury_boundary",
                }
                and isinstance(decoder_order_jury_verdict.get("recommended_lb_sensor"), dict)
                and any(
                    isinstance(item, dict)
                    and item.get("status") == "decoder_jury_alive_cross_decoder_agreement"
                    and item.get("validation", {}).get("upload_safe") is True
                    and int(item.get("validation", {}).get("changed_cells_vs_current_best", 0)) >= 10
                    for item in decoder_order_jury.get("ranking", [])
                ),
                (
                    f"status={decoder_order_jury_verdict.get('status')}, "
                    f"recommended={decoder_order_jury_verdict.get('recommended_lb_sensor')}"
                ),
            ),
            check(
                "decoder_boundary_tomography_solver_recorded",
                decoder_boundary_tomography.get("status")
                in {
                    "boundary_tomography_ready",
                    "boundary_tomography_diagnostic_only",
                }
                and isinstance(decoder_boundary_tomography_verdict.get("recommended_lb_sensor"), dict)
                and int(decoder_boundary_tomography.get("boundary_inventory", {}).get("consensus_shadow_cells", 0)) >= 1
                and any(
                    isinstance(item, dict)
                    and item.get("status") == "consensus_shadow_alive"
                    and item.get("validation", {}).get("upload_safe") is True
                    and int(item.get("validation", {}).get("changed_cells_vs_current_best", 0)) >= 20
                    for item in decoder_boundary_tomography.get("ranking", [])
                ),
                (
                    f"status={decoder_boundary_tomography_verdict.get('status')}, "
                    f"recommended={decoder_boundary_tomography_verdict.get('recommended_lb_sensor')}, "
                    f"inventory={decoder_boundary_tomography.get('boundary_inventory')}"
                ),
            ),
            check(
                "core_mediated_action_release_recorded",
                core_mediated_release.get("status") == "core_mediated_action_release_ready"
                and core_mediated_verdict.get("status") == "core_mediated_action_release_ready"
                and isinstance(core_mediated_verdict.get("recommended_lb_sensor"), dict)
                and int(core_mediated_release.get("cell_inventory", {}).get("default_core_released", 0)) >= 1
                and any(
                    isinstance(item, dict)
                    and item.get("validation", {}).get("upload_safe") is True
                    and str(item.get("status", "")).startswith("core_mediated_")
                    for item in core_mediated_release.get("ranking", [])
                ),
                (
                    f"status={core_mediated_verdict.get('status')}, "
                    f"recommended={core_mediated_verdict.get('recommended_lb_sensor')}, "
                    f"inventory={core_mediated_release.get('cell_inventory')}"
                ),
            ),
            check(
                "core_release_ablation_probe_recorded",
                core_release_ablation.get("status") == "core_release_ablation_ready"
                and core_release_ablation_verdict.get("status") == "core_release_ablation_ready"
                and isinstance(core_release_ablation_verdict.get("recommended_lb_candidate"), dict)
                and isinstance(core_release_ablation_verdict.get("recommended_architecture_sensor"), dict)
                and any(
                    isinstance(item, dict)
                    and item.get("validation", {}).get("upload_safe") is True
                    and str(item.get("status", "")).startswith(("full_core_", "no_", "invariant_only"))
                    for item in core_release_ablation.get("ranking", [])
                ),
                (
                    f"status={core_release_ablation_verdict.get('status')}, "
                    f"lb_candidate={core_release_ablation_verdict.get('recommended_lb_candidate')}, "
                    f"sensor={core_release_ablation_verdict.get('recommended_architecture_sensor')}"
                ),
            ),
            check(
                "listener_invariant_contrastive_probe_recorded",
                contrastive_probe.get("status") == "probe_ready"
                and contrastive_verdict.get("status") in {
                    "listener_invariant_decoder_promising",
                    "listener_invariant_decoder_alive_but_weak",
                    "listener_invariant_decoder_not_ready",
                },
                (
                    f"status={contrastive_verdict.get('status')}, "
                    f"rho={fmt(contrastive_verdict.get('mean_listener_route_spearman'), 4)}, "
                    f"overlap={fmt(contrastive_verdict.get('mean_contrastive_overlap_rate'), 4)}"
                ),
            ),
            check(
                "private_safe_toxicity_probe_recorded",
                private_toxicity_probe.get("status") == "probe_ready"
                and toxicity_verdict.get("status") in {
                    "private_safe_toxicity_field_promising",
                    "toxicity_field_promising_with_hardworld_gap",
                    "toxicity_field_alive_but_public_sensor_bound",
                    "private_safe_toxicity_field_not_ready",
                },
                (
                    f"status={toxicity_verdict.get('status')}, "
                    f"mean_loo_auc={fmt(toxicity_verdict.get('mean_loo_bad_anchor_auc'), 4)}, "
                    f"worst_loo_auc={fmt(toxicity_verdict.get('worst_loo_bad_anchor_auc'), 4)}, "
                    f"safety_z={fmt(toxicity_verdict.get('selected_safety_z_vs_matched_null'), 4)}"
                ),
            ),
            check(
                "hardworld_toxicity_factorization_probe_recorded",
                hardworld_toxicity_probe.get("status") == "probe_ready"
                and hardworld_verdict.get("status") in {
                    "hardworld_mixture_factorization_required",
                    "hardworld_mode_alive_but_decoder_not_validated",
                    "hardworld_factorization_not_supported",
                },
                (
                    f"status={hardworld_verdict.get('status')}, "
                    f"broad_to_h088_auc={fmt(hardworld_verdict.get('broad_predicts_hardworld_auc'), 4)}, "
                    f"rho={fmt(hardworld_verdict.get('broad_hardworld_spearman'), 4)}, "
                    f"joint_z={fmt(hardworld_verdict.get('selected_joint_safety_z'), 4)}"
                ),
            ),
            check(
                "factorized_toxicity_decoder_candidate_recorded",
                factorized_decoder.get("experiment") == "Factorized Toxicity Decoder Candidate"
                and len(factorized_variants) >= 2
                and all(
                    isinstance(item, dict) and item.get("validation", {}).get("upload_safe") is True
                    for item in factorized_variants.values()
                ),
                (
                    f"variants={sorted(factorized_variants)}, "
                    f"upload_safe={[item.get('validation', {}).get('upload_safe') for item in factorized_variants.values() if isinstance(item, dict)]}"
                ),
            ),
            check(
                "factorized_toxicity_decoder_stress_supported",
                factorized_stress.get("status") == "stress_audit_ready"
                and len(factorized_stress_variants) >= 2
                and len(factorized_supported) >= 1,
                (
                    f"status={factorized_stress.get('status')}, "
                    f"supported={factorized_supported}, "
                    f"variants={[(name, item.get('verdict', {}).get('status')) for name, item in factorized_stress_variants.items() if isinstance(item, dict)]}"
                ),
            ),
            check("roles_present", role_keys == EXPECTED_ROLES, f"roles={sorted(role_keys)}"),
            check(
                "role_based_output_names",
                set(role_outputs) == EXPECTED_ROLES
                and all(str(name).startswith("submission_team_hsjepa_") for name in role_outputs.values()),
                f"role_outputs={role_outputs}",
            ),
            check(
                "all_role_submissions_upload_safe",
                bool(upload_results)
                and all(bool(item.get("upload_safe")) for item in upload_results.values() if isinstance(item, dict)),
                f"upload_roles={sorted(upload_results)}",
            ),
            check(
                "pipeline_manifest_complete",
                pipeline.get("status") == "pipeline_ready_with_boundary"
                and int(pipeline.get("stage_count", 0)) >= 8
                and int(pipeline.get("edge_count", 0)) >= 9,
                f"status={pipeline.get('status')}, stages={pipeline.get('stage_count')}, edges={pipeline.get('edge_count')}",
            ),
            check(
                "method_packet_presentable",
                (
                    "route-conserving" in str(method.get("title", "")).lower()
                    or "route-conserving" in str(method.get("one_sentence", "")).lower()
                    or (
                        "route" in str(method.get("one_sentence", "")).lower()
                        and "bridge" in str(method.get("one_sentence", "")).lower()
                    )
                )
                and {"abstract_ko", "method_ko", "generality_ko", "algorithm_ko"}.issubset(set(method.get("paper_sections", {}))),
                f"title={method.get('title')}",
            ),
            check(
                "claim_boundary_honest",
                boundary.get("is_pure_og_only_model") is False
                and boundary.get("uses_public_lb_sensor") is True
                and boundary.get("uses_proprietary_embedding_api_in_team_runner") is False,
                (
                    f"pure_og={boundary.get('is_pure_og_only_model')}, "
                    f"public_sensor={boundary.get('uses_public_lb_sensor')}, "
                    f"proprietary_embedding={boundary.get('uses_proprietary_embedding_api_in_team_runner')}"
                ),
            ),
        ]
    )

    required_failures = [row for row in rows if row["required"] and not row["passed"]]
    result = {
        "package": "Route-Conserving S2 Bridge HS-JEPA",
        "status": "release_ready_with_boundary" if not required_failures else "release_blocked",
        "passed_checks": sum(1 for row in rows if row["passed"]),
        "total_checks": len(rows),
        "required_failures": required_failures,
        "checks": rows,
        "release_claim": (
            "This package is ready as a team-facing and paper-facing HS-JEPA release "
            "when presented with the explicit public-sensor boundary."
        ),
        "boundary": {
            "not_pure_og_only": True,
            "private_lb_not_proven": True,
            "human_state_not_standalone_assignment_solver": True,
        },
    }
    CHECKLIST_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    CHECKLIST_MD.write_text(build_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


def build_markdown(result: dict[str, object]) -> str:
    rows = ["| Check | Status | Evidence |", "| --- | --- | --- |"]
    for item in result["checks"]:
        rows.append(f"| `{item['check']}` | `{item['status']}` | {item['evidence']} |")

    failures = result.get("required_failures", [])
    failure_lines = ["- none"] if not failures else [f"- `{item['check']}`: {item['evidence']}" for item in failures]

    return "\n".join(
        [
            "# HS-JEPA Release Checklist",
            "",
            "이 문서는 현재 HS-JEPA 패키지를 팀 공유/논문 발표/대회 제출 논의용 release로 볼 수 있는지 최종 확인한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{result['status']}`",
            f"- Checks: `{result['passed_checks']}/{result['total_checks']}` passed",
            "",
            "## Required Failures",
            "",
            *failure_lines,
            "",
            "## Checks",
            "",
            *rows,
            "",
            "## Release Claim",
            "",
            result["release_claim"],
            "",
            "## Boundary",
            "",
            "- private LB safety is not proven",
            "- pure OG-only assignment is not proven",
            "- hidden row-support recovery is not solved by current portable human/social/cohort context",
            "- hidden row-support transfer is partially alive but not yet an action-grade deployment decoder",
            "- masked row-support is a valid HS-JEPA representation objective candidate but group-heldout stress is still weak",
            "- row-support strict action decoder is LB-informative but has a route-gain tradeoff against local nulls",
            "- human-state is an orientation diagnostic, not a complete row-target assignment solver",
            "- OG-only assignment replacement has a recorded probe result",
            "- Hidden row-support transfer has a recorded probe result",
            "- Masked row-support objective has a recorded stress-boundary probe result",
            "- Row-support strict action decoder has recorded upload-safe outputs and local stress",
            "- Action decoder ablation suite ranks toxicity-first/support-first/route-first decoders for submission-slot prioritization, not LB prediction",
            "- Decoder boundary tomography has recorded consensus-shadow/route-only/fusion-only probes, but their public safety is not proven",
            "- Listener-invariant contrastive decoding has a recorded probe result",
            "- Private-safe toxicity has a recorded probe result and hard-world boundary",
            "- Hard-world toxicity factorization has a recorded probe result",
            "- Factorized toxicity decoder candidates have recorded upload-safe outputs",
            "- Factorized toxicity decoder has a recorded stress audit with at least one supported variant",
            "- HS-JEPA Core is separated from the Sleep Competition Adapter",
            "- HS-JEPA Core/Adapter boundary audit is verified",
            "- the next big bet is replacing public-sensor assignment with an OG-only human-state teacher",
            "",
        ]
    )


def main() -> None:
    result = build_checklist()
    sys.exit(0 if result["status"] == "release_ready_with_boundary" else 1)


if __name__ == "__main__":
    main()
