#!/usr/bin/env python3
"""Build the HS-JEPA reproducibility contract.

The team package intentionally uses two kinds of evidence:

1. Original competition data and generated lifestyle/state artifacts.
2. Public-LB sensor observations accumulated during the competition.

For a paper or team handoff, these must not be blurred together.  This script
classifies required inputs and generated outputs so a teammate can see exactly
what is OG data, what is a public sensor, and what is a derived artifact.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"
OUT.mkdir(parents=True, exist_ok=True)

CONTRACT_JSON = OUT / "hsjepa_reproducibility_contract.json"
CONTRACT_MD = OUT / "hsjepa_reproducibility_contract.md"

CRITICAL_SUBMISSIONS = [
    ("current_best_anchor", "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"),
    ("toxicity_negative_sensor", "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"),
    ("local_semantic_source_consensus", "submission_h154_local_semantic_source_consensus_36eeef08_uploadsafe.csv"),
    ("posterior_support_anchor", "submission_h155_h061_all_cap1.0_k150_a1.15_0f87a1af_uploadsafe.csv"),
    ("sparse_lossnull_anchor", "submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160_c7b38d35_uploadsafe.csv"),
    ("competition_primary_output", "submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv"),
    ("interpretable_s2_output", "submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv"),
    ("human_state_probe_output", "submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv"),
]

SOURCE_ACTION_SUBMISSIONS = [
    "submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv",
    "submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv",
    "submission_h074_antishortcut_inversion_816703df_uploadsafe.csv",
    "submission_h075_antibad_transport_f6863945_uploadsafe.csv",
    "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv",
    "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv",
    "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv",
    "submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv",
    "submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv",
    "submission_bigbet1_public_listener_tomography_2687b6b6_uploadsafe.csv",
    "submission_h085_aug_public_equation_f154e2bb_uploadsafe.csv",
]

PUBLIC_LOSS_SENSOR_SUBMISSIONS = [
    "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
    "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
    "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
    "submission_h010_objective_s1s4_v2_uploadsafe.csv",
    "submission_e323_5508f966_uploadsafe.csv",
    "submission_h145_q3repair_2d818e46_uploadsafe.csv",
]

MODULES = [
    "final_hsjepa_candidates/candidate_1_public_loss_sparse_tomography.py",
    "hsjepa_jackpot/h154_local_semantic_source_consensus.py",
    "hsjepa_jackpot/h155_h158_posterior_lossnull_jackpot.py",
    "paper_hsjepa_core/stage_bridge_conservation_solver.py",
    "paper_hsjepa_core/s2hub_bridge_solver.py",
    "paper_hsjepa_core/s2hub_human_state_distillation.py",
    "team_hsjepa_end_to_end/run_route_conserving_s2_bridge.py",
    "team_hsjepa_end_to_end/audit_route_conserving_s2_bridge.py",
    "team_hsjepa_end_to_end/validate_route_conserving_s2_bridge_package.py",
    "team_hsjepa_end_to_end/run_full_team_hsjepa_package.py",
    "team_hsjepa_end_to_end/build_hsjepa_architecture_readiness_report.py",
    "team_hsjepa_end_to_end/build_hsjepa_mechanism_ablation_report.py",
    "team_hsjepa_end_to_end/build_hsjepa_generality_report.py",
    "team_hsjepa_end_to_end/audit_hsjepa_core_adapter_boundary.py",
    "team_hsjepa_end_to_end/build_hsjepa_paper_method_packet.py",
    "team_hsjepa_end_to_end/build_hsjepa_pipeline_manifest.py",
    "team_hsjepa_end_to_end/build_hsjepa_release_checklist.py",
    "hsjepa_core/core.py",
    "hsjepa_core/build_core_architecture_manifest.py",
    "hsjepa_core/run_core_reference_demo.py",
    "sleep_competition_adapter/og_only_assignment_teacher_probe.py",
    "sleep_competition_adapter/assignment_gap_decomposition_probe.py",
    "sleep_competition_adapter/hidden_row_support_sensor_probe.py",
    "sleep_competition_adapter/masked_row_support_objective_probe.py",
    "sleep_competition_adapter/listener_invariant_contrastive_probe.py",
    "sleep_competition_adapter/private_safe_toxicity_probe.py",
    "sleep_competition_adapter/hardworld_toxicity_factorization_probe.py",
    "sleep_competition_adapter/factorized_toxicity_decoder_candidate.py",
    "sleep_competition_adapter/factorized_toxicity_decoder_stress_audit.py",
    "sleep_competition_adapter/row_support_strict_action_decoder.py",
    "sleep_competition_adapter/route_frontier_action_decoder.py",
    "sleep_competition_adapter/route_toxicity_fusion_decoder.py",
    "sleep_competition_adapter/decoder_order_jury_solver.py",
    "sleep_competition_adapter/decoder_boundary_tomography_solver.py",
    "sleep_competition_adapter/action_decoder_ablation_suite.py",
    "sleep_competition_adapter/build_sleep_competition_adapter_report.py",
]

GENERATED_OUTPUTS = [
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_package.json", True),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_evidence_table.csv", True),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_stress_audit.json", True),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_stress_summary.csv", True),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_validation_report.json", True),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_validation_report.md", True),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_team_handoff.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_team_handoff.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_full_run_log.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report_ko.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report_ko.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit_ko.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet_ko.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest_ko.md", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_release_checklist.json", False),
    ("team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_release_checklist_ko.md", False),
    ("hsjepa_core/outputs/hsjepa_core_manifest.json", False),
    ("hsjepa_core/outputs/hsjepa_core_manifest_ko.md", False),
    ("hsjepa_core/outputs/hsjepa_core_ablation_contract.json", False),
    ("hsjepa_core/outputs/hsjepa_core_ablation_contract_ko.md", False),
    ("hsjepa_core/outputs/hsjepa_core_reference_run.json", False),
    ("hsjepa_core/outputs/hsjepa_core_reference_run_ko.md", False),
    ("sleep_competition_adapter/outputs/sleep_competition_adapter_report.json", False),
    ("sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md", False),
    ("sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json", False),
    ("sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md", False),
    ("sleep_competition_adapter/outputs/og_only_assignment_teacher_probe.json", False),
    ("sleep_competition_adapter/outputs/og_only_assignment_teacher_probe_ko.md", False),
    ("sleep_competition_adapter/outputs/og_only_assignment_teacher_ranked_cells.csv", False),
    ("sleep_competition_adapter/outputs/assignment_gap_decomposition_probe.json", False),
    ("sleep_competition_adapter/outputs/assignment_gap_decomposition_probe_ko.md", False),
    ("sleep_competition_adapter/outputs/assignment_gap_decomposition_summary.csv", False),
    ("sleep_competition_adapter/outputs/hidden_row_support_sensor_probe.json", False),
    ("sleep_competition_adapter/outputs/hidden_row_support_sensor_probe_ko.md", False),
    ("sleep_competition_adapter/outputs/hidden_row_support_sensor_transfer_metrics.csv", False),
    ("sleep_competition_adapter/outputs/masked_row_support_objective_probe.json", False),
    ("sleep_competition_adapter/outputs/masked_row_support_objective_probe_ko.md", False),
    ("sleep_competition_adapter/outputs/masked_row_support_objective_transfer_metrics.csv", False),
    ("sleep_competition_adapter/outputs/masked_row_support_objective_group_stress.csv", False),
    ("sleep_competition_adapter/outputs/listener_invariant_contrastive_probe.json", False),
    ("sleep_competition_adapter/outputs/listener_invariant_contrastive_probe_ko.md", False),
    ("sleep_competition_adapter/outputs/listener_invariant_contrastive_scored_bundles.csv", False),
    ("sleep_competition_adapter/outputs/private_safe_toxicity_probe.json", False),
    ("sleep_competition_adapter/outputs/private_safe_toxicity_probe_ko.md", False),
    ("sleep_competition_adapter/outputs/private_safe_toxicity_scored_cells.csv", False),
    ("sleep_competition_adapter/outputs/private_safe_toxicity_loo_anchor_metrics.csv", False),
    ("sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe.json", False),
    ("sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe_ko.md", False),
    ("sleep_competition_adapter/outputs/hardworld_toxicity_factorization_sectors.csv", False),
    ("sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout.json", False),
    ("sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout_ko.md", False),
    ("sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_audit.json", False),
    ("sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_audit_ko.md", False),
    ("sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_summary.csv", False),
    ("sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout.json", False),
    ("sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout_ko.md", False),
    ("sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_audit.csv", False),
    ("sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_null_stress.csv", False),
    ("sleep_competition_adapter/outputs/row_support_strict_action_decoder/submission_hsjepa_row_support_strict_route_support_gate_5ae5c515_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/row_support_strict_action_decoder/submission_hsjepa_row_support_exploratory_route_support_gate_97a2f8f5_uploadsafe.csv", False),
    ("submission_hsjepa_row_support_strict_route_support_gate_5ae5c515_uploadsafe.csv", False),
    ("submission_hsjepa_row_support_exploratory_route_support_gate_97a2f8f5_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout.json", False),
    ("sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout_ko.md", False),
    ("sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_audit.csv", False),
    ("sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_null_stress.csv", False),
    ("sleep_competition_adapter/outputs/route_frontier_action_decoder/submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_frontier_action_decoder/submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_frontier_action_decoder/submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv", False),
    ("submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv", False),
    ("submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv", False),
    ("submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout.json", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout_ko.md", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_audit.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_null_stress.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_s2_route_toxicity_fusion_5ac75e44_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_seed_route_toxicity_fusion_ec01d56a_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_open_route_toxicity_fusion_bb0ca49f_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv", False),
    ("submission_hsjepa_s2_route_toxicity_fusion_5ac75e44_uploadsafe.csv", False),
    ("submission_hsjepa_seed_route_toxicity_fusion_ec01d56a_uploadsafe.csv", False),
    ("submission_hsjepa_open_route_toxicity_fusion_bb0ca49f_uploadsafe.csv", False),
    ("submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv", False),
    ("submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv", False),
    ("submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout.json", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout_ko.md", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_cells.csv", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_null_stress.csv", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_route_majority_fusion_confirmed_1caf57fb_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_s2_pair_consensus_a71de0a7_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_seed_pair_consensus_e8a7ce4c_uploadsafe.csv", False),
    ("submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv", False),
    ("submission_hsjepa_decoder_jury_route_majority_fusion_confirmed_1caf57fb_uploadsafe.csv", False),
    ("submission_hsjepa_decoder_jury_s2_pair_consensus_a71de0a7_uploadsafe.csv", False),
    ("submission_hsjepa_decoder_jury_seed_pair_consensus_e8a7ce4c_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout.json", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout_ko.md", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_cells.csv", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_null_stress.csv", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_boundary_dual_probe_528728bd_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_route_only_rescue_6c0f15eb_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_fusion_only_probe_8ce162dc_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_consensus_shadow_all_soft_80850159_uploadsafe.csv", False),
    ("submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv", False),
    ("submission_hsjepa_boundary_tomography_boundary_dual_probe_528728bd_uploadsafe.csv", False),
    ("submission_hsjepa_boundary_tomography_route_only_rescue_6c0f15eb_uploadsafe.csv", False),
    ("submission_hsjepa_boundary_tomography_fusion_only_probe_8ce162dc_uploadsafe.csv", False),
    ("submission_hsjepa_boundary_tomography_consensus_shadow_all_soft_80850159_uploadsafe.csv", False),
    ("sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite.json", False),
    ("sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite_ko.md", False),
    ("sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite.csv", False),
]


def sha1_file(path: Path, max_full_bytes: int = 64 * 1024 * 1024) -> dict[str, object]:
    size = path.stat().st_size
    h = hashlib.sha1()
    mode = "full"
    if size <= max_full_bytes:
        h.update(path.read_bytes())
    else:
        mode = "head_tail_1mb"
        with path.open("rb") as fh:
            h.update(fh.read(1024 * 1024))
            if size > 1024 * 1024:
                fh.seek(max(0, size - 1024 * 1024))
                h.update(fh.read(1024 * 1024))
    return {"sha1": h.hexdigest(), "hash_mode": mode, "size_bytes": int(size)}


def resolve_file(name: str | Path) -> Path | None:
    path = Path(name)
    if path.is_absolute() and path.exists():
        return path
    direct = ROOT / str(name)
    if direct.exists():
        return direct
    matches = list(ROOT.rglob(str(name)))
    return matches[0] if matches else None


def file_record(category: str, role: str, name: str | Path, required: bool, reason: str) -> dict[str, object]:
    path = resolve_file(name)
    rec: dict[str, object] = {
        "category": category,
        "role": role,
        "name": str(name),
        "required": required,
        "reason": reason,
        "exists": path is not None,
        "path": str(path.resolve()) if path else None,
    }
    if path and path.is_file():
        rec.update(sha1_file(path))
    return rec


def directory_record(category: str, role: str, path: Path, pattern: str, required: bool, reason: str) -> dict[str, object]:
    files = sorted(path.glob(pattern)) if path.exists() else []
    total = sum(p.stat().st_size for p in files if p.is_file())
    sample = [str(p.relative_to(ROOT)) for p in files[:12]]
    return {
        "category": category,
        "role": role,
        "name": str(path.relative_to(ROOT)),
        "required": required,
        "reason": reason,
        "exists": path.exists(),
        "path": str(path.resolve()) if path.exists() else None,
        "pattern": pattern,
        "file_count": len(files),
        "total_size_bytes": int(total),
        "sample_files": sample,
    }


def summarize_public_ledger(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"exists": False}
    ledger = pd.read_csv(path)
    out = {
        "exists": True,
        "rows": int(len(ledger)),
        "columns": list(ledger.columns),
    }
    if "public_lb" in ledger:
        out["best_public_lb"] = float(ledger["public_lb"].min())
        out["worst_public_lb"] = float(ledger["public_lb"].max())
    if "file" in ledger:
        out["unique_files"] = int(ledger["file"].nunique())
    return out


def build_markdown(contract: dict[str, object]) -> str:
    records = contract["records"]
    by_category: dict[str, list[dict[str, object]]] = {}
    for rec in records:
        by_category.setdefault(str(rec["category"]), []).append(rec)

    lines = [
        "# HS-JEPA Reproducibility Contract",
        "",
        "이 문서는 Route-Conserving S2 Bridge HS-JEPA가 어떤 입력을 쓰는지 명확히 분리한다.",
        "",
        "핵심은 다음이다.",
        "",
        "```text",
        "OG raw data != public-LB sensor != generated action artifact",
        "```",
        "",
        "이 구분을 해야 논문에서 HS-JEPA의 representation claim과 competition-specific decoder claim을 과장하지 않을 수 있다.",
        "",
        "## Status",
        "",
        f"- Contract passed: `{contract['passed']}`",
        f"- Required missing records: `{contract['required_missing_count']}`",
        f"- Public ledger rows: `{contract['public_ledger_summary'].get('rows')}`",
        f"- Public ledger best LB: `{contract['public_ledger_summary'].get('best_public_lb')}`",
        "",
        "## Category Summary",
        "",
        "| Category | Records | Missing required | Meaning |",
        "| --- | ---: | ---: | --- |",
    ]
    meanings = {
        "og_raw": "대회 원본 데이터 또는 원본 raw lifelog 묶음",
        "public_sensor": "public LB 관측을 센서로 사용한 자산",
        "competition_anchor": "현재 frontier와 listener/source action anchor",
        "derived_module": "재생성 가능한 코드 모듈",
        "generated_output": "one-command runner가 만든 산출물",
    }
    for category, rows in sorted(by_category.items()):
        missing = sum(1 for row in rows if row["required"] and not row["exists"])
        lines.append(f"| `{category}` | `{len(rows)}` | `{missing}` | {meanings.get(category, '')} |")

    for category, rows in sorted(by_category.items()):
        lines.extend(["", f"## {category}", "", "| Role | Exists | Required | Name | Reason |", "| --- | ---: | ---: | --- | --- |"])
        for row in rows:
            lines.append(
                f"| `{row['role']}` | `{row['exists']}` | `{row['required']}` | `{row['name']}` | {row['reason']} |"
            )

    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "강하게 말할 수 있는 것:",
            "",
            "```text",
            "The package is end-to-end reproducible from the listed local OG data, public sensor ledger, and generated action anchors.",
            "The decoder mechanism is tested by route-conservation and S2-hub stress audits.",
            "```",
            "",
            "조심해야 하는 것:",
            "",
            "```text",
            "This is not a pure OG-only model.",
            "The competition decoder uses public-LB sensor observations.",
            "The paper claim should separate human-state representation from competition-specific row-target assignment.",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict[str, object]:
    records: list[dict[str, object]] = []

    records.append(file_record("og_raw", "train_metrics", "data/ch2026_metrics_train.csv", True, "original train labels/metrics"))
    records.append(file_record("og_raw", "submission_sample", "data/ch2026_submission_sample.csv", True, "original submission key/order contract"))
    records.append(directory_record("og_raw", "raw_lifelog_items", ROOT / "data" / "ch2025_data_items", "*.parquet", True, "original raw lifelog feature items"))

    records.append(file_record("public_sensor", "public_score_ledger", "data_analytics/hsjepa_public_score_ledger.csv", True, "known public LB observations used as sensor"))
    for name in PUBLIC_LOSS_SENSOR_SUBMISSIONS:
        records.append(file_record("public_sensor", "public_loss_sensor_submission", name, False, "submission used to infer public loss/action toxicity when available"))

    for role, name in CRITICAL_SUBMISSIONS:
        records.append(file_record("competition_anchor", role, name, True, "frontier/source/output action anchor used by the packaged decoder"))
    for name in SOURCE_ACTION_SUBMISSIONS:
        records.append(file_record("competition_anchor", "source_action_submission", name, False, "source/listener action proposal used by local semantic consensus if present"))

    records.append(file_record("competition_anchor", "h154_cell_candidates", "hsjepa_jackpot/outputs/h154_cell_candidates.csv", True, "local semantic source-consensus cell table"))
    records.append(file_record("competition_anchor", "h061_cell_posterior", "hitl/h061_h057_feedback_support_translator_jepa/h061_cell_posterior.csv", False, "posterior support feature for h155/h158 when available"))

    for name in MODULES:
        records.append(file_record("derived_module", "python_module", name, True, "reproducible module in the role-based HS-JEPA package"))
    for name, required in GENERATED_OUTPUTS:
        records.append(
            file_record(
                "generated_output",
                "team_package_output",
                name,
                required,
                "generated by run_full_team_hsjepa_package.py",
            )
        )

    required_missing = [rec for rec in records if rec["required"] and not rec["exists"]]
    public_ledger = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"
    contract = {
        "package": "Route-Conserving S2 Bridge HS-JEPA",
        "contract": "HS-JEPA reproducibility contract",
        "passed": len(required_missing) == 0,
        "required_missing_count": len(required_missing),
        "required_missing": required_missing,
        "public_ledger_summary": summarize_public_ledger(public_ledger),
        "records": records,
        "boundary": {
            "is_pure_og_only_model": False,
            "uses_public_lb_sensor": True,
            "uses_proprietary_embedding_api_in_team_runner": False,
            "human_state_role": "orientation diagnostic, not complete row-target assignment solver",
            "competition_decoder_role": "public-sensitive row-target action solver with route-conserving S2 bridge",
        },
    }
    CONTRACT_JSON.write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding="utf-8")
    CONTRACT_MD.write_text(build_markdown(contract), encoding="utf-8")
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return contract


if __name__ == "__main__":
    result = run()
    raise SystemExit(0 if result["passed"] else 1)
