#!/usr/bin/env python3
"""Run the full team-facing HS-JEPA package.

This is the single command a teammate should run when they do not know any
historical experiment version names.  It executes:

1. HS-JEPA core architecture manifest.
2. HS-JEPA core reference run.
3. HS-JEPA core module benchmark.
4. Route-Conserving S2 Bridge package generation.
5. Stress audit against feasible candidate nulls.
6. Claim/evidence validation.
7. Reproducibility contract.
8. Architecture readiness report.
9. Mechanism ablation report.
10. OG-only assignment teacher probe.
11. Assignment-gap decomposition probe.
12. Hidden row-support sensor transfer probe.
13. Masked row-support objective stress probe.
14. Row-support strict action decoder.
15. Route-toxicity fusion action decoder.
16. Decoder-order jury solver.
17. Decoder boundary tomography solver.
18. Core-mediated action release.
19. Core release ablation probe.
20. Core-health calibrated release.
21. Cross-listener transport decoder.
22. Counterfactual listener-dropout solver.
23. Spectral public tangent solver.
24. Negative-tangent invariant projection solver.
25. LB-conditioned responsibility solver.
26. Mixture-listener responsibility solver.
27. Public/private subset tomography solver.
28. Listener-invariant contrastive probe.
29. Private-safe toxicity probe.
30. Hard-world toxicity factorization probe.
31. Factorized toxicity decoder candidate.
32. Factorized toxicity decoder stress audit.
33. Action decoder ablation suite.
34. Generality report.
35. Sleep competition adapter report and big-bet queue.
36. Core/adapter boundary audit.
37. Paper method packet.
38. Pipeline manifest.
39. Release checklist.
40. A compact handoff report for paper and competition discussion.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json
import subprocess
import sys
import time

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"
OUT.mkdir(parents=True, exist_ok=True)

PACKAGE_JSON = OUT / "route_conserving_s2_bridge_package.json"
STRESS_CSV = OUT / "route_conserving_s2_bridge_stress_summary.csv"
VALIDATION_JSON = OUT / "route_conserving_s2_bridge_validation_report.json"
HANDOFF_MD = OUT / "route_conserving_s2_bridge_team_handoff.md"
HANDOFF_JSON = OUT / "route_conserving_s2_bridge_team_handoff.json"
RUN_LOG_JSON = OUT / "route_conserving_s2_bridge_full_run_log.json"
CONTRACT_MD = OUT / "hsjepa_reproducibility_contract.md"
CONTRACT_JSON = OUT / "hsjepa_reproducibility_contract.json"
READINESS_MD = OUT / "hsjepa_architecture_readiness_report.md"
READINESS_JSON = OUT / "hsjepa_architecture_readiness_report.json"
PAPER_PACKET_MD = OUT / "hsjepa_paper_method_packet_ko.md"
PAPER_PACKET_JSON = OUT / "hsjepa_paper_method_packet.json"
PIPELINE_MD = OUT / "hsjepa_pipeline_manifest_ko.md"
PIPELINE_JSON = OUT / "hsjepa_pipeline_manifest.json"
MECHANISM_ABLATION_MD = OUT / "hsjepa_mechanism_ablation_report_ko.md"
MECHANISM_ABLATION_JSON = OUT / "hsjepa_mechanism_ablation_report.json"
GENERALITY_MD = OUT / "hsjepa_generality_report_ko.md"
GENERALITY_JSON = OUT / "hsjepa_generality_report.json"
BOUNDARY_AUDIT_MD = OUT / "hsjepa_core_adapter_boundary_audit_ko.md"
BOUNDARY_AUDIT_JSON = OUT / "hsjepa_core_adapter_boundary_audit.json"
RELEASE_CHECKLIST_MD = OUT / "hsjepa_release_checklist_ko.md"
RELEASE_CHECKLIST_JSON = OUT / "hsjepa_release_checklist.json"
CORE_OUT = ROOT / "hsjepa_core" / "outputs"
CORE_MANIFEST_MD = CORE_OUT / "hsjepa_core_manifest_ko.md"
CORE_MANIFEST_JSON = CORE_OUT / "hsjepa_core_manifest.json"
CORE_ABLATION_MD = CORE_OUT / "hsjepa_core_ablation_contract_ko.md"
CORE_ABLATION_JSON = CORE_OUT / "hsjepa_core_ablation_contract.json"
CORE_REFERENCE_MD = CORE_OUT / "hsjepa_core_reference_run_ko.md"
CORE_REFERENCE_JSON = CORE_OUT / "hsjepa_core_reference_run.json"
CORE_BENCHMARK_MD = CORE_OUT / "hsjepa_core_module_benchmark_ko.md"
CORE_BENCHMARK_JSON = CORE_OUT / "hsjepa_core_module_benchmark.json"
CORE_BENCHMARK_CSV = CORE_OUT / "hsjepa_core_module_benchmark_cases.csv"
ADAPTER_OUT = ROOT / "sleep_competition_adapter" / "outputs"
ADAPTER_REPORT_MD = ADAPTER_OUT / "sleep_competition_adapter_report_ko.md"
ADAPTER_REPORT_JSON = ADAPTER_OUT / "sleep_competition_adapter_report.json"
BIG_BET_MD = ADAPTER_OUT / "hsjepa_big_bet_queue_ko.md"
BIG_BET_JSON = ADAPTER_OUT / "hsjepa_big_bet_queue.json"
OG_PROBE_MD = ADAPTER_OUT / "og_only_assignment_teacher_probe_ko.md"
OG_PROBE_JSON = ADAPTER_OUT / "og_only_assignment_teacher_probe.json"
ASSIGNMENT_GAP_MD = ADAPTER_OUT / "assignment_gap_decomposition_probe_ko.md"
ASSIGNMENT_GAP_JSON = ADAPTER_OUT / "assignment_gap_decomposition_probe.json"
ROW_SUPPORT_SENSOR_MD = ADAPTER_OUT / "hidden_row_support_sensor_probe_ko.md"
ROW_SUPPORT_SENSOR_JSON = ADAPTER_OUT / "hidden_row_support_sensor_probe.json"
MASKED_ROW_SUPPORT_MD = ADAPTER_OUT / "masked_row_support_objective_probe_ko.md"
MASKED_ROW_SUPPORT_JSON = ADAPTER_OUT / "masked_row_support_objective_probe.json"
ROW_SUPPORT_DECODER_MD = ADAPTER_OUT / "row_support_strict_action_decoder" / "row_support_strict_action_decoder_readout_ko.md"
ROW_SUPPORT_DECODER_JSON = ADAPTER_OUT / "row_support_strict_action_decoder" / "row_support_strict_action_decoder_readout.json"
ROUTE_FRONTIER_DECODER_MD = ADAPTER_OUT / "route_frontier_action_decoder" / "route_frontier_action_decoder_readout_ko.md"
ROUTE_FRONTIER_DECODER_JSON = ADAPTER_OUT / "route_frontier_action_decoder" / "route_frontier_action_decoder_readout.json"
ROUTE_TOXICITY_FUSION_DECODER_MD = ADAPTER_OUT / "route_toxicity_fusion_decoder" / "route_toxicity_fusion_decoder_readout_ko.md"
ROUTE_TOXICITY_FUSION_DECODER_JSON = ADAPTER_OUT / "route_toxicity_fusion_decoder" / "route_toxicity_fusion_decoder_readout.json"
DECODER_ORDER_JURY_MD = ADAPTER_OUT / "decoder_order_jury_solver" / "decoder_order_jury_solver_readout_ko.md"
DECODER_ORDER_JURY_JSON = ADAPTER_OUT / "decoder_order_jury_solver" / "decoder_order_jury_solver_readout.json"
DECODER_BOUNDARY_TOMOGRAPHY_MD = ADAPTER_OUT / "decoder_boundary_tomography_solver" / "decoder_boundary_tomography_readout_ko.md"
DECODER_BOUNDARY_TOMOGRAPHY_JSON = ADAPTER_OUT / "decoder_boundary_tomography_solver" / "decoder_boundary_tomography_readout.json"
CORE_MEDIATED_RELEASE_MD = ADAPTER_OUT / "core_mediated_action_release" / "core_mediated_action_release_readout_ko.md"
CORE_MEDIATED_RELEASE_JSON = ADAPTER_OUT / "core_mediated_action_release" / "core_mediated_action_release_readout.json"
CORE_RELEASE_ABLATION_MD = ADAPTER_OUT / "core_release_ablation_probe" / "core_release_ablation_probe_readout_ko.md"
CORE_RELEASE_ABLATION_JSON = ADAPTER_OUT / "core_release_ablation_probe" / "core_release_ablation_probe_readout.json"
CORE_HEALTH_CALIBRATED_MD = ADAPTER_OUT / "core_health_calibrated_release" / "core_health_calibrated_release_readout_ko.md"
CORE_HEALTH_CALIBRATED_JSON = ADAPTER_OUT / "core_health_calibrated_release" / "core_health_calibrated_release_readout.json"
CROSS_LISTENER_TRANSPORT_MD = ADAPTER_OUT / "cross_listener_transport_decoder" / "cross_listener_transport_readout_ko.md"
CROSS_LISTENER_TRANSPORT_JSON = ADAPTER_OUT / "cross_listener_transport_decoder" / "cross_listener_transport_readout.json"
COUNTERFACTUAL_LISTENER_DROPOUT_MD = ADAPTER_OUT / "counterfactual_listener_dropout_solver" / "counterfactual_listener_dropout_readout_ko.md"
COUNTERFACTUAL_LISTENER_DROPOUT_JSON = ADAPTER_OUT / "counterfactual_listener_dropout_solver" / "counterfactual_listener_dropout_readout.json"
SPECTRAL_PUBLIC_TANGENT_MD = ADAPTER_OUT / "spectral_public_tangent_solver" / "spectral_public_tangent_readout_ko.md"
SPECTRAL_PUBLIC_TANGENT_JSON = ADAPTER_OUT / "spectral_public_tangent_solver" / "spectral_public_tangent_readout.json"
NEGATIVE_TANGENT_INVARIANT_MD = ADAPTER_OUT / "negative_tangent_invariant_projection_solver" / "negative_tangent_invariant_projection_readout.md"
NEGATIVE_TANGENT_INVARIANT_JSON = ADAPTER_OUT / "negative_tangent_invariant_projection_solver" / "negative_tangent_invariant_projection_readout.json"
LB_CONDITIONED_RESPONSIBILITY_MD = ADAPTER_OUT / "lb_conditioned_responsibility_solver" / "lb_conditioned_responsibility_readout_ko.md"
LB_CONDITIONED_RESPONSIBILITY_JSON = ADAPTER_OUT / "lb_conditioned_responsibility_solver" / "lb_conditioned_responsibility_readout.json"
MIXTURE_LISTENER_RESPONSIBILITY_MD = ADAPTER_OUT / "mixture_listener_responsibility_solver" / "mixture_listener_responsibility_readout_ko.md"
MIXTURE_LISTENER_RESPONSIBILITY_JSON = ADAPTER_OUT / "mixture_listener_responsibility_solver" / "mixture_listener_responsibility_readout.json"
PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_MD = (
    ADAPTER_OUT / "public_private_subset_tomography_solver" / "public_private_subset_tomography_readout_ko.md"
)
PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON = (
    ADAPTER_OUT / "public_private_subset_tomography_solver" / "public_private_subset_tomography_readout.json"
)
ACTION_DECODER_ABLATION_MD = ADAPTER_OUT / "action_decoder_ablation_suite" / "hsjepa_action_decoder_ablation_suite_ko.md"
ACTION_DECODER_ABLATION_JSON = ADAPTER_OUT / "action_decoder_ablation_suite" / "hsjepa_action_decoder_ablation_suite.json"
CONTRASTIVE_PROBE_MD = ADAPTER_OUT / "listener_invariant_contrastive_probe_ko.md"
CONTRASTIVE_PROBE_JSON = ADAPTER_OUT / "listener_invariant_contrastive_probe.json"
PRIVATE_TOXICITY_PROBE_MD = ADAPTER_OUT / "private_safe_toxicity_probe_ko.md"
PRIVATE_TOXICITY_PROBE_JSON = ADAPTER_OUT / "private_safe_toxicity_probe.json"
HARDWORLD_TOXICITY_PROBE_MD = ADAPTER_OUT / "hardworld_toxicity_factorization_probe_ko.md"
HARDWORLD_TOXICITY_PROBE_JSON = ADAPTER_OUT / "hardworld_toxicity_factorization_probe.json"
FACTORIZED_DECODER_MD = ADAPTER_OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout_ko.md"
FACTORIZED_DECODER_JSON = ADAPTER_OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_readout.json"
FACTORIZED_STRESS_MD = ADAPTER_OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit_ko.md"
FACTORIZED_STRESS_JSON = ADAPTER_OUT / "factorized_toxicity_decoder_candidate" / "factorized_toxicity_decoder_stress_audit.json"


def run_command(args: list[str]) -> dict[str, object]:
    started = time.time()
    proc = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.time() - started
    record = {
        "command": args,
        "returncode": proc.returncode,
        "elapsed_sec": elapsed,
        "stdout_tail": proc.stdout[-6000:],
        "stderr_tail": proc.stderr[-6000:],
    }
    if proc.returncode != 0:
        raise RuntimeError(json.dumps(record, indent=2, ensure_ascii=False))
    return record


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_handoff(
    package: dict[str, object],
    validation: dict[str, object],
    stress: pd.DataFrame,
    readiness: dict[str, object],
    ablation: dict[str, object],
    generality: dict[str, object],
    core: dict[str, object],
    core_reference: dict[str, object],
    core_benchmark: dict[str, object],
    adapter: dict[str, object],
    big_bets: dict[str, object],
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
    action_decoder_ablation: dict[str, object],
    contrastive_probe: dict[str, object],
    private_toxicity_probe: dict[str, object],
    hardworld_toxicity_probe: dict[str, object],
    factorized_decoder: dict[str, object],
    factorized_stress: dict[str, object],
    boundary_audit: dict[str, object],
    release: dict[str, object],
) -> str:
    packaged = package["packaged_submissions"]
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
    lb_responsibility_fit = lb_conditioned_responsibility.get("fit", {})
    lb_recommended = lb_responsibility_verdict.get("recommended_variant")
    lb_recommended_variant = lb_conditioned_responsibility.get("variants", {}).get(str(lb_recommended), {})
    lb_recommended_metrics = lb_recommended_variant.get("metrics", {}) if isinstance(lb_recommended_variant, dict) else {}
    lb_recommended_submission = lb_recommended_variant.get("submission", {}) if isinstance(lb_recommended_variant, dict) else {}
    mixture_listener_verdict = mixture_listener_responsibility.get("verdict", {})
    mixture_recommended = mixture_listener_verdict.get("recommended_variant")
    mixture_recommended_variant = mixture_listener_responsibility.get("variants", {}).get(str(mixture_recommended), {})
    mixture_recommended_metrics = mixture_recommended_variant.get("metrics", {}) if isinstance(mixture_recommended_variant, dict) else {}
    mixture_recommended_submission = mixture_recommended_variant.get("submission", {}) if isinstance(mixture_recommended_variant, dict) else {}
    subset_tomography_verdict = public_private_subset_tomography.get("verdict", {})
    subset_tomography_recommended = subset_tomography_verdict.get("recommended_variant")
    subset_tomography_variant = public_private_subset_tomography.get("variants", {}).get(str(subset_tomography_recommended), {})
    subset_tomography_metrics = subset_tomography_variant.get("metrics", {}) if isinstance(subset_tomography_variant, dict) else {}
    subset_tomography_submission = subset_tomography_variant.get("submission", {}) if isinstance(subset_tomography_variant, dict) else {}
    action_ablation_verdict = action_decoder_ablation.get("verdict", {})
    contrastive_verdict = contrastive_probe.get("verdict", {})
    toxicity_verdict = private_toxicity_probe.get("verdict", {})
    hardworld_verdict = hardworld_toxicity_probe.get("verdict", {})
    factorized_variants = factorized_decoder.get("variants", {})
    factorized_stress_variants = factorized_stress.get("variants", {})
    factorized_stress_statuses = ", ".join(
        f"{name}:{item.get('verdict', {}).get('status')}"
        for name, item in sorted(factorized_stress_variants.items())
        if isinstance(item, dict)
    )

    submission_rows = ["| Role | File | Upload-safe | Changed cells |", "| --- | --- | ---: | ---: |"]
    for role in ["competition_primary", "interpretable_s2_hub", "human_state_probe"]:
        item = packaged[role]
        validation_item = item["validation"]
        submission_rows.append(
            f"| `{role}` | `{item['submission_file']}` | `{validation_item['upload_safe']}` | "
            f"`{validation_item['changed_cells_vs_current_best']}` |"
        )

    stress_rows = ["| Candidate | Route delta | Null route delta | S2 usage | Null S2 usage | Route p | S2 p |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for rec in stress.to_dict("records"):
        stress_rows.append(
            f"| `{rec['name']}` | `{rec['mean_route_energy_delta']:.5f}` | "
            f"`{rec['null_mean_route_energy_delta']:.5f}` | `{rec['s2_any_rate']:.3f}` | "
            f"`{rec['null_s2_any_rate']:.3f}` | `{rec['p_null_energy_le_actual']:.4f}` | "
            f"`{rec['p_null_s2_any_ge_actual']:.4f}` |"
        )

    return "\n".join(
        [
            "# Route-Conserving S2 Bridge HS-JEPA Team Handoff",
            "",
            "이 파일은 팀원이 과거 실험 버전명을 몰라도 현재 HS-JEPA 패키지의 실행 결과와 논문용 주장을 한 번에 이해하도록 만든 최종 핸드오프 요약이다.",
            "",
            "## One-Command Reproduction",
            "",
            "```bash",
            "python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py",
            "```",
            "",
            "전체 dependency까지 재생성하려면:",
            "",
            "```bash",
            "python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py --refresh",
            "```",
            "",
            "## Core Mechanism",
            "",
            "```text",
            "HS-JEPA Core:",
            "partial human context",
            "  -> hidden human-state representation",
            "  -> listener responsibility",
            "  -> action-health decision",
            "  -> invariant-preserving decoder",
            "  -> anti-shortcut validation",
            "",
            "Sleep Competition Adapter:",
            "public-sensitive driver action",
            "  + route-conserving bridge action",
            "  + S2 listener/hub constraint",
            "  + upload-safe sparse row-target decoder",
            "```",
            "",
            "축구 비유로 말하면, HS-JEPA Core는 `상황을 읽고, listener와 action 위험을 분리한 뒤, 궤적 불변성을 보존하는 슛 기술`이다. Sleep Adapter의 S2 bridge는 그 기술이 이번 경기장에서 구현된 case-study 궤적이다.",
            "",
            "## Core / Adapter Separation",
            "",
            f"- Core status: `{core['status']}` (`{core['passed_gates']}/{core['total_gates']}` gates)",
            f"- Core ablation contract: `{len(core.get('modules', []))}` modules, `{len(big_bets.get('bets', []))}` big-bet followups",
            f"- Core reference run: `{core_reference.get('status')}`, released actions `{core_reference.get('full_core', {}).get('summary', {}).get('released_actions')}`",
            f"- Core module benchmark: `{core_benchmark.get('status')}`, full-core F1 `{core_benchmark.get('verdict', {}).get('full_core_mean_f1')}`, action-health FP lift `{core_benchmark.get('verdict', {}).get('remove_action_health_false_positive_lift')}`",
            f"- Adapter status: `{adapter['status']}`",
            f"- Adapter score delta: `{adapter['score_evidence']['delta']}`",
            f"- OG-only assignment probe: `{og_verdict.get('status')}`",
            f"- Assignment-gap decomposition: `{gap_verdict.get('status')}`",
            f"- Hidden row-support sensor: `{row_support_verdict.get('status')}`",
            f"- Masked row-support objective: `{masked_row_support_verdict.get('status')}`",
            f"- Row-support strict action decoder: `{row_support_decoder_verdict.get('status')}`",
            f"- Route-frontier action decoder: `{route_frontier_verdict.get('status')}`",
            f"- Route-toxicity fusion decoder: `{route_toxicity_fusion_verdict.get('status')}`",
            f"- Decoder-order jury solver: `{decoder_order_jury_verdict.get('status')}`",
            f"- Decoder boundary tomography: `{decoder_boundary_tomography_verdict.get('status')}`",
            f"- Core-mediated action release: `{core_mediated_verdict.get('status')}`",
            f"- Core release ablation probe: `{core_release_ablation_verdict.get('status')}`",
            f"- Core-health calibrated release: `{core_health_calibrated_verdict.get('status')}`",
            f"- Cross-listener transport decoder: `{cross_listener_verdict.get('status')}`",
            f"- Counterfactual listener-dropout solver: `{counterfactual_listener_dropout.get('status')}`",
            f"- Spectral public tangent solver: `{spectral_public_tangent.get('status')}`",
            f"- Negative-tangent invariant projection: `{negative_projection_verdict.get('status')}`",
            f"- LB-conditioned responsibility solver: `{lb_responsibility_verdict.get('status')}`",
            f"- Mixture-listener responsibility solver: `{mixture_listener_verdict.get('status')}`",
            f"- Public/private subset tomography solver: `{subset_tomography_verdict.get('status')}`",
            f"- Action decoder ablation suite: `{action_ablation_verdict.get('status')}`",
            f"- Listener-invariant contrastive probe: `{contrastive_verdict.get('status')}`",
            f"- Private-safe toxicity probe: `{toxicity_verdict.get('status')}`",
            f"- Hard-world toxicity factorization probe: `{hardworld_verdict.get('status')}`",
            f"- Factorized toxicity decoder variants: `{len(factorized_variants)}`",
            f"- Factorized toxicity stress audit: `{factorized_stress.get('status')}`",
            f"- Core/adapter boundary audit: `{boundary_audit.get('status')}` (`{boundary_audit.get('passed_checks')}/{boundary_audit.get('total_checks')}` checks)",
            "",
            "Core 문서:",
            "",
            "```text",
            "hsjepa_core/outputs/hsjepa_core_manifest_ko.md",
            "hsjepa_core/outputs/hsjepa_core_ablation_contract_ko.md",
            "```",
            "",
            "Adapter 문서:",
            "",
            "```text",
            "sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md",
            "sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md",
            "sleep_competition_adapter/outputs/og_only_assignment_teacher_probe_ko.md",
            "sleep_competition_adapter/outputs/assignment_gap_decomposition_probe_ko.md",
            "sleep_competition_adapter/outputs/hidden_row_support_sensor_probe_ko.md",
            "sleep_competition_adapter/outputs/masked_row_support_objective_probe_ko.md",
            "sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout_ko.md",
            "sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout_ko.md",
            "sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout_ko.md",
            "sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout_ko.md",
            "sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout_ko.md",
            "sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_readout_ko.md",
            "sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_readout_ko.md",
            "sleep_competition_adapter/outputs/core_health_calibrated_release/core_health_calibrated_release_readout_ko.md",
            "sleep_competition_adapter/outputs/cross_listener_transport_decoder/cross_listener_transport_readout_ko.md",
            "sleep_competition_adapter/outputs/counterfactual_listener_dropout_solver/counterfactual_listener_dropout_readout_ko.md",
            "sleep_competition_adapter/outputs/spectral_public_tangent_solver/spectral_public_tangent_readout_ko.md",
            "sleep_competition_adapter/outputs/negative_tangent_invariant_projection_solver/negative_tangent_invariant_projection_readout.md",
            "sleep_competition_adapter/outputs/lb_conditioned_responsibility_solver/lb_conditioned_responsibility_readout_ko.md",
            "sleep_competition_adapter/outputs/mixture_listener_responsibility_solver/mixture_listener_responsibility_readout_ko.md",
            "sleep_competition_adapter/outputs/public_private_subset_tomography_solver/public_private_subset_tomography_readout_ko.md",
            "sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite_ko.md",
            "sleep_competition_adapter/outputs/listener_invariant_contrastive_probe_ko.md",
            "sleep_competition_adapter/outputs/private_safe_toxicity_probe_ko.md",
            "sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe_ko.md",
            "sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout_ko.md",
            "sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_audit_ko.md",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit_ko.md",
            "```",
            "",
            "## Generated Submission Roles",
            "",
            *submission_rows,
            "",
            "## Mechanism Evidence",
            "",
            *stress_rows,
            "",
            "자동 validator가 확인한 핵심 수치:",
            "",
            f"- Primary route z-score: `{mechanism['primary_route_z']:.2f}`",
            f"- S2 listener route z-score: `{mechanism['s2_route_z']:.2f}`",
            f"- S2 listener usage: `{mechanism['s2_listener_s2_any_rate']:.3f}` vs null `{mechanism['s2_listener_null_s2_any_rate']:.3f}`",
            f"- Package validation passed: `{validation['passed']}`",
            f"- Architecture readiness: `{readiness['status']}` (`{readiness['passed_gates']}/{readiness['total_gates']}` gates)",
            f"- Mechanism ablation: `{ablation['status']}` (`{ablation['public_worldviews_killed']}` public worldviews killed, `{ablation['public_worldviews_survived']}` survived)",
            f"- Generality boundary: `{generality['status']}` (`{generality['passed_checks']}/{generality['total_checks']}` portability checks, nonblocking boundaries: `{len(generality['nonblocking_boundaries'])}`)",
            f"- Core/adapter boundary: core `{core['status']}`, adapter `{adapter['status']}`",
            f"- OG-only assignment boundary: pure recall `{og_verdict.get('pure_og_row_cap2_mean_recall'):.4f}`, distilled recall `{og_verdict.get('distilled_row_cap2_mean_recall'):.4f}`",
            f"- Assignment gap: `{gap_verdict.get('status')}`, row-support gap `{gap_verdict.get('mean_row_support_gap'):.4f}`",
            f"- Hidden row-support sensor: `{row_support_verdict.get('best_portable_family')}`, row AUC `{row_support_verdict.get('best_portable_mean_row_auc'):.4f}`, cell recall `{row_support_verdict.get('best_portable_mean_cell_recall_with_stage_prior'):.4f}`",
            f"- Masked row-support objective: row AUC `{masked_row_support_verdict.get('full_composite_mean_row_auc'):.4f}`, cell recall `{masked_row_support_verdict.get('full_composite_mean_cell_recall'):.4f}`, group stress AUC `{masked_row_support_verdict.get('group_stress_full_mean_auc'):.4f}`",
            f"- Row-support strict decoder: recommended `{row_support_decoder_verdict.get('recommended_variant')}`, changed cells `{row_support_decoder_verdict.get('exploratory_changed_cells')}`, safety z `{row_support_decoder_verdict.get('exploratory_safety_z'):.2f}`",
            f"- Route-frontier decoder: recommended `{route_frontier_verdict.get('recommended_variant')}`, status `{route_frontier_verdict.get('status')}`",
            f"- Route-toxicity fusion decoder: recommended `{route_toxicity_fusion_verdict.get('recommended_variant')}`, status `{route_toxicity_fusion_verdict.get('status')}`",
            f"- Decoder-order jury: recommended `{decoder_order_jury_verdict.get('recommended_lb_sensor')}`, status `{decoder_order_jury_verdict.get('status')}`",
            f"- Decoder boundary tomography: recommended `{decoder_boundary_tomography_verdict.get('recommended_lb_sensor')}`, status `{decoder_boundary_tomography_verdict.get('status')}`, inventory `{decoder_boundary_tomography.get('boundary_inventory')}`",
            f"- Core-mediated action release: recommended `{core_mediated_verdict.get('recommended_lb_sensor')}`, status `{core_mediated_verdict.get('status')}`, inventory `{core_mediated_release.get('cell_inventory')}`",
            f"- Core release ablation: full-core `{core_release_ablation_verdict.get('recommended_lb_candidate')}`, sensor `{core_release_ablation_verdict.get('recommended_architecture_sensor')}`, status `{core_release_ablation_verdict.get('status')}`",
            f"- Core-health calibrated release: guarded `{core_health_calibrated_verdict.get('recommended_lb_candidate')}`, big bet `{core_health_calibrated_verdict.get('recommended_big_bet_sensor')}`, status `{core_health_calibrated_verdict.get('status')}`",
            f"- Cross-listener transport: recommended `{cross_listener_verdict.get('recommended_lb_sensor')}`, big bet `{cross_listener_verdict.get('recommended_big_bet')}`, status `{cross_listener_verdict.get('status')}`",
            f"- Counterfactual listener-dropout: information sensor `{listener_dropout_verdict.get('recommended_information_sensor', {}).get('variant')}`, status `{counterfactual_listener_dropout.get('status')}`",
            f"- Spectral public tangent: information sensor `{spectral_tangent_verdict.get('recommended_information_sensor', {}).get('variant')}`, status `{spectral_public_tangent.get('status')}`",
            f"- Negative-tangent invariant projection: recommended `{negative_projection_verdict.get('recommended_variant')}`, status `{negative_projection_verdict.get('status')}`",
            f"- LB-conditioned responsibility: recommended `{lb_recommended}`, file `{lb_recommended_submission.get('submission_file')}`, LOO corr `{lb_responsibility_fit.get('loo_corr')}`, changed cells `{lb_recommended_submission.get('changed_cells')}`",
            f"- Mixture-listener responsibility: recommended `{mixture_recommended}`, file `{mixture_recommended_submission.get('submission_file')}`, mixture LOO `{mixture_listener_responsibility.get('mixture_fit', {}).get('loo_corr')}`, scalar LOO `{mixture_listener_responsibility.get('mixture_fit', {}).get('scalar_fit', {}).get('loo_corr')}`, changed cells `{mixture_recommended_submission.get('changed_cells')}`",
            f"- Public/private subset tomography: recommended `{subset_tomography_recommended}`, file `{subset_tomography_submission.get('submission_file')}`, source LOO `{public_private_subset_tomography.get('source_fit', {}).get('loo_corr')}`, changed cells `{subset_tomography_submission.get('changed_cells')}`, predicted delta `{subset_tomography_metrics.get('sum_predicted_public_delta')}`",
            f"- Action decoder ablation: recommended `{action_ablation_verdict.get('recommended_lb_sensor')}`, big bet `{action_ablation_verdict.get('big_bet_sensor')}`",
            f"- Listener-invariant boundary: listener-route rho `{contrastive_verdict.get('mean_listener_route_spearman'):.4f}`, contrastive overlap `{contrastive_verdict.get('mean_contrastive_overlap_rate'):.4f}`",
            f"- Private-safe toxicity boundary: mean LOO AUC `{toxicity_verdict.get('mean_loo_bad_anchor_auc'):.4f}`, worst LOO AUC `{toxicity_verdict.get('worst_loo_bad_anchor_auc'):.4f}`",
            f"- Hard-world factorization: broad->H088 AUC `{hardworld_verdict.get('broad_predicts_hardworld_auc'):.4f}`, broad/H088 rho `{hardworld_verdict.get('broad_hardworld_spearman'):.4f}`",
            f"- Factorized decoder candidates: `{', '.join(sorted(factorized_variants))}`",
            f"- Factorized decoder stress: `{factorized_stress_statuses}`",
            f"- Boundary tomography inventory: `{decoder_boundary_tomography.get('boundary_inventory')}`",
            f"- Core-mediated release inventory: `{core_mediated_release.get('cell_inventory')}`",
            f"- Core/adapter boundary audit: `{boundary_audit.get('status')}`",
            f"- Release checklist: `{release['status']}` (`{release['passed_checks']}/{release['total_checks']}` checks)",
            "",
            "## Paper Claim",
            "",
            "강하게 주장할 수 있는 내용:",
            "",
            "```text",
            "HS-JEPA is a core architecture for human-understanding prediction.",
            "It predicts hidden human-state, listener responsibility, action-health, and invariant-preserving action representations.",
            "The sleep competition adapter instantiates the invariant as Q/S route energy and the listener bridge as S2.",
            "The current LB breakthrough is evidence for this adapter, while the reusable claim is the core/action separation.",
            "```",
            "",
            "## Big-Bet Queue",
            "",
            "다음 큰 실험은 단순 alpha 조정이 아니라 core/adaptor 경계를 바꾸는 실험이다.",
            "",
            *[
                f"- `{bet['name']}`: {bet['worldview']} Expected LB delta if true `{bet['expected_public_lb_delta_if_true']}`."
                for bet in big_bets.get("bets", [])
            ],
            "",
            "## Competition Use",
            "",
            "제출 슬롯이 있다면 우선순위는 다음이다.",
            "",
            "1. `competition_primary`: 성능 중심 Route-Conserving Objective Bridge",
            "2. `interpretable_s2_hub`: 논문 설명력이 가장 강한 S2 Listener Bridge",
            "3. `human_state_probe`: OG human-state orientation diagnostic",
            "",
            "## Reproducibility Contract",
            "",
            "이 패키지는 입력을 다음처럼 분리해서 기록한다.",
            "",
            "```text",
            "OG raw data != public-LB sensor != generated action artifact",
            "```",
            "",
            "계약 문서:",
            "",
            "```text",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.md",
            "```",
            "",
            "## Boundary",
            "",
            "이 패키지가 증명하지 않는 것:",
            "",
            "- private leaderboard safety",
            "- OG human-state encoder 단독으로 row-target assignment 해결",
            "- S2가 모든 수면 생리학적 factor의 중심이라는 주장",
            "",
            "정확한 결론은 더 좁고 강하다.",
            "",
            "```text",
            "Given a public-sensitive action field, route conservation plus S2 listener usage selects a statistically unusual and interpretable correction path.",
            "```",
            "",
            "## Architecture Readiness Report",
            "",
            "논문/팀 공유용 gate 판정:",
            "",
            "```text",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.md",
            "```",
            "",
            "## Paper Method Packet",
            "",
            "논문 초안/발표에 바로 옮길 수 있는 method packet:",
            "",
            "```text",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet_ko.md",
            "```",
            "",
            "## Mechanism Ablation Report",
            "",
            "대체 세계관 중 무엇이 public sensor/stress audit에서 죽었고 무엇이 살아남았는지 정리한 knockout report:",
            "",
            "```text",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report_ko.md",
            "```",
            "",
            "## Generality Report",
            "",
            "HS-JEPA의 범용 아키텍처와 이번 대회의 Route-Conserving S2 Bridge case study를 분리한 portability report:",
            "",
            "```text",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report_ko.md",
            "```",
            "",
            "## Pipeline Manifest",
            "",
            "OG 데이터에서 public sensor, latent/context, route decoder, submission, paper packet까지 이어지는 역할 기반 pipeline:",
            "",
            "```text",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest_ko.md",
            "```",
            "",
            "## Release Checklist",
            "",
            "팀 공유/논문 발표/제출 논의용 최종 release gate:",
            "",
            "```text",
            "team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_release_checklist_ko.md",
            "```",
            "",
        ]
    )


def run(refresh: bool = False) -> dict[str, object]:
    commands = [
        [sys.executable, str(ROOT / "hsjepa_core" / "build_core_architecture_manifest.py")],
        [sys.executable, str(ROOT / "hsjepa_core" / "run_core_reference_demo.py")],
        [sys.executable, str(ROOT / "hsjepa_core" / "run_core_module_benchmark.py")],
        [sys.executable, str(HERE / "run_route_conserving_s2_bridge.py")],
        [sys.executable, str(HERE / "audit_route_conserving_s2_bridge.py")],
        [sys.executable, str(HERE / "validate_route_conserving_s2_bridge_package.py")],
        [sys.executable, str(HERE / "inspect_hsjepa_reproducibility_contract.py")],
        [sys.executable, str(HERE / "build_hsjepa_architecture_readiness_report.py")],
        [sys.executable, str(HERE / "build_hsjepa_mechanism_ablation_report.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "og_only_assignment_teacher_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "assignment_gap_decomposition_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "hidden_row_support_sensor_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "masked_row_support_objective_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "row_support_strict_action_decoder.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "route_frontier_action_decoder.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "route_toxicity_fusion_decoder.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "decoder_order_jury_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "decoder_boundary_tomography_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "core_mediated_action_release.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "core_release_ablation_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "core_health_calibrated_release.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "cross_listener_transport_decoder.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "counterfactual_listener_dropout_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "spectral_public_tangent_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "negative_tangent_invariant_projection_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "lb_conditioned_responsibility_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "mixture_listener_responsibility_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "public_private_subset_tomography_solver.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "listener_invariant_contrastive_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "private_safe_toxicity_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "hardworld_toxicity_factorization_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "factorized_toxicity_decoder_candidate.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "factorized_toxicity_decoder_stress_audit.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "action_decoder_ablation_suite.py")],
        [sys.executable, str(HERE / "inspect_hsjepa_reproducibility_contract.py")],
        [sys.executable, str(HERE / "build_hsjepa_generality_report.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "build_sleep_competition_adapter_report.py")],
        [sys.executable, str(HERE / "audit_hsjepa_core_adapter_boundary.py")],
        [sys.executable, str(HERE / "build_hsjepa_paper_method_packet.py")],
        [sys.executable, str(HERE / "build_hsjepa_pipeline_manifest.py")],
        [sys.executable, str(HERE / "build_hsjepa_release_checklist.py")],
    ]
    if refresh:
        commands[1].append("--refresh")

    command_records = []
    for args in commands:
        command_records.append(run_command(args))

    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    readiness = read_json(READINESS_JSON)
    ablation = read_json(MECHANISM_ABLATION_JSON)
    generality = read_json(GENERALITY_JSON)
    core = read_json(CORE_MANIFEST_JSON)
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
    action_decoder_ablation = read_json(ACTION_DECODER_ABLATION_JSON)
    contrastive_probe = read_json(CONTRASTIVE_PROBE_JSON)
    private_toxicity_probe = read_json(PRIVATE_TOXICITY_PROBE_JSON)
    hardworld_toxicity_probe = read_json(HARDWORLD_TOXICITY_PROBE_JSON)
    factorized_decoder = read_json(FACTORIZED_DECODER_JSON)
    factorized_stress = read_json(FACTORIZED_STRESS_JSON)
    boundary_audit = read_json(BOUNDARY_AUDIT_JSON)
    release = read_json(RELEASE_CHECKLIST_JSON)
    stress = pd.read_csv(STRESS_CSV)
    handoff_md = build_handoff(
        package,
        validation,
        stress,
        readiness,
        ablation,
        generality,
        core,
        core_reference,
        core_benchmark,
        adapter,
        big_bets,
        og_probe,
        assignment_gap,
        row_support_sensor,
        masked_row_support,
        row_support_decoder,
        route_frontier_decoder,
        route_toxicity_fusion_decoder,
        decoder_order_jury,
        decoder_boundary_tomography,
        core_mediated_release,
        core_release_ablation,
        core_health_calibrated,
        cross_listener_transport,
        counterfactual_listener_dropout,
        spectral_public_tangent,
        negative_tangent_invariant,
        lb_conditioned_responsibility,
        mixture_listener_responsibility,
        public_private_subset_tomography,
        action_decoder_ablation,
        contrastive_probe,
        private_toxicity_probe,
        hardworld_toxicity_probe,
        factorized_decoder,
        factorized_stress,
        boundary_audit,
        release,
    )

    listener_dropout_verdict = counterfactual_listener_dropout.get("verdict", {})
    spectral_tangent_verdict = spectral_public_tangent.get("verdict", {})
    negative_projection_verdict = negative_tangent_invariant.get("verdict", {})
    lb_responsibility_verdict = lb_conditioned_responsibility.get("verdict", {})
    lb_responsibility_fit = lb_conditioned_responsibility.get("fit", {})
    lb_recommended = lb_responsibility_verdict.get("recommended_variant")
    lb_recommended_variant = lb_conditioned_responsibility.get("variants", {}).get(str(lb_recommended), {})
    lb_recommended_metrics = lb_recommended_variant.get("metrics", {}) if isinstance(lb_recommended_variant, dict) else {}
    lb_recommended_submission = lb_recommended_variant.get("submission", {}) if isinstance(lb_recommended_variant, dict) else {}
    mixture_listener_verdict = mixture_listener_responsibility.get("verdict", {})
    mixture_recommended = mixture_listener_verdict.get("recommended_variant")
    mixture_recommended_variant = mixture_listener_responsibility.get("variants", {}).get(str(mixture_recommended), {})
    mixture_recommended_metrics = mixture_recommended_variant.get("metrics", {}) if isinstance(mixture_recommended_variant, dict) else {}
    mixture_recommended_submission = mixture_recommended_variant.get("submission", {}) if isinstance(mixture_recommended_variant, dict) else {}
    subset_tomography_verdict = public_private_subset_tomography.get("verdict", {})
    subset_tomography_recommended = subset_tomography_verdict.get("recommended_variant")
    subset_tomography_variant = public_private_subset_tomography.get("variants", {}).get(str(subset_tomography_recommended), {})
    subset_tomography_metrics = subset_tomography_variant.get("metrics", {}) if isinstance(subset_tomography_variant, dict) else {}
    subset_tomography_submission = subset_tomography_variant.get("submission", {}) if isinstance(subset_tomography_variant, dict) else {}

    handoff = {
        "package": "Route-Conserving S2 Bridge HS-JEPA",
        "refresh": refresh,
        "commands": command_records,
        "package_json": str(PACKAGE_JSON.resolve()),
        "stress_csv": str(STRESS_CSV.resolve()),
        "validation_json": str(VALIDATION_JSON.resolve()),
        "handoff_md": str(HANDOFF_MD.resolve()),
        "reproducibility_contract_md": str(CONTRACT_MD.resolve()),
        "reproducibility_contract_json": str(CONTRACT_JSON.resolve()),
        "architecture_readiness_md": str(READINESS_MD.resolve()),
        "architecture_readiness_json": str(READINESS_JSON.resolve()),
        "paper_method_packet_md": str(PAPER_PACKET_MD.resolve()),
        "paper_method_packet_json": str(PAPER_PACKET_JSON.resolve()),
        "mechanism_ablation_md": str(MECHANISM_ABLATION_MD.resolve()),
        "mechanism_ablation_json": str(MECHANISM_ABLATION_JSON.resolve()),
        "generality_report_md": str(GENERALITY_MD.resolve()),
        "generality_report_json": str(GENERALITY_JSON.resolve()),
        "core_adapter_boundary_audit_md": str(BOUNDARY_AUDIT_MD.resolve()),
        "core_adapter_boundary_audit_json": str(BOUNDARY_AUDIT_JSON.resolve()),
        "core_manifest_md": str(CORE_MANIFEST_MD.resolve()),
        "core_manifest_json": str(CORE_MANIFEST_JSON.resolve()),
        "core_ablation_md": str(CORE_ABLATION_MD.resolve()),
        "core_ablation_json": str(CORE_ABLATION_JSON.resolve()),
        "core_reference_md": str(CORE_REFERENCE_MD.resolve()),
        "core_reference_json": str(CORE_REFERENCE_JSON.resolve()),
        "core_module_benchmark_md": str(CORE_BENCHMARK_MD.resolve()),
        "core_module_benchmark_json": str(CORE_BENCHMARK_JSON.resolve()),
        "core_module_benchmark_csv": str(CORE_BENCHMARK_CSV.resolve()),
        "adapter_report_md": str(ADAPTER_REPORT_MD.resolve()),
        "adapter_report_json": str(ADAPTER_REPORT_JSON.resolve()),
        "big_bet_queue_md": str(BIG_BET_MD.resolve()),
        "big_bet_queue_json": str(BIG_BET_JSON.resolve()),
        "og_only_assignment_teacher_probe_md": str(OG_PROBE_MD.resolve()),
        "og_only_assignment_teacher_probe_json": str(OG_PROBE_JSON.resolve()),
        "assignment_gap_decomposition_probe_md": str(ASSIGNMENT_GAP_MD.resolve()),
        "assignment_gap_decomposition_probe_json": str(ASSIGNMENT_GAP_JSON.resolve()),
        "hidden_row_support_sensor_probe_md": str(ROW_SUPPORT_SENSOR_MD.resolve()),
        "hidden_row_support_sensor_probe_json": str(ROW_SUPPORT_SENSOR_JSON.resolve()),
        "masked_row_support_objective_probe_md": str(MASKED_ROW_SUPPORT_MD.resolve()),
        "masked_row_support_objective_probe_json": str(MASKED_ROW_SUPPORT_JSON.resolve()),
        "row_support_strict_action_decoder_md": str(ROW_SUPPORT_DECODER_MD.resolve()),
        "row_support_strict_action_decoder_json": str(ROW_SUPPORT_DECODER_JSON.resolve()),
        "route_frontier_action_decoder_md": str(ROUTE_FRONTIER_DECODER_MD.resolve()),
        "route_frontier_action_decoder_json": str(ROUTE_FRONTIER_DECODER_JSON.resolve()),
        "route_toxicity_fusion_decoder_md": str(ROUTE_TOXICITY_FUSION_DECODER_MD.resolve()),
        "route_toxicity_fusion_decoder_json": str(ROUTE_TOXICITY_FUSION_DECODER_JSON.resolve()),
        "decoder_order_jury_solver_md": str(DECODER_ORDER_JURY_MD.resolve()),
        "decoder_order_jury_solver_json": str(DECODER_ORDER_JURY_JSON.resolve()),
        "decoder_boundary_tomography_md": str(DECODER_BOUNDARY_TOMOGRAPHY_MD.resolve()),
        "decoder_boundary_tomography_json": str(DECODER_BOUNDARY_TOMOGRAPHY_JSON.resolve()),
        "core_mediated_action_release_md": str(CORE_MEDIATED_RELEASE_MD.resolve()),
        "core_mediated_action_release_json": str(CORE_MEDIATED_RELEASE_JSON.resolve()),
        "core_release_ablation_probe_md": str(CORE_RELEASE_ABLATION_MD.resolve()),
        "core_release_ablation_probe_json": str(CORE_RELEASE_ABLATION_JSON.resolve()),
        "core_health_calibrated_release_md": str(CORE_HEALTH_CALIBRATED_MD.resolve()),
        "core_health_calibrated_release_json": str(CORE_HEALTH_CALIBRATED_JSON.resolve()),
        "cross_listener_transport_decoder_md": str(CROSS_LISTENER_TRANSPORT_MD.resolve()),
        "cross_listener_transport_decoder_json": str(CROSS_LISTENER_TRANSPORT_JSON.resolve()),
        "action_decoder_ablation_suite_md": str(ACTION_DECODER_ABLATION_MD.resolve()),
        "action_decoder_ablation_suite_json": str(ACTION_DECODER_ABLATION_JSON.resolve()),
        "listener_invariant_contrastive_probe_md": str(CONTRASTIVE_PROBE_MD.resolve()),
        "listener_invariant_contrastive_probe_json": str(CONTRASTIVE_PROBE_JSON.resolve()),
        "private_safe_toxicity_probe_md": str(PRIVATE_TOXICITY_PROBE_MD.resolve()),
        "private_safe_toxicity_probe_json": str(PRIVATE_TOXICITY_PROBE_JSON.resolve()),
        "hardworld_toxicity_factorization_probe_md": str(HARDWORLD_TOXICITY_PROBE_MD.resolve()),
        "hardworld_toxicity_factorization_probe_json": str(HARDWORLD_TOXICITY_PROBE_JSON.resolve()),
        "factorized_toxicity_decoder_md": str(FACTORIZED_DECODER_MD.resolve()),
        "factorized_toxicity_decoder_json": str(FACTORIZED_DECODER_JSON.resolve()),
        "factorized_toxicity_decoder_stress_md": str(FACTORIZED_STRESS_MD.resolve()),
        "factorized_toxicity_decoder_stress_json": str(FACTORIZED_STRESS_JSON.resolve()),
        "pipeline_manifest_md": str(PIPELINE_MD.resolve()),
        "pipeline_manifest_json": str(PIPELINE_JSON.resolve()),
        "release_checklist_md": str(RELEASE_CHECKLIST_MD.resolve()),
        "release_checklist_json": str(RELEASE_CHECKLIST_JSON.resolve()),
        "validation_passed": bool(validation["passed"]),
        "architecture_readiness_status": str(readiness["status"]),
        "architecture_readiness_gates": f"{readiness['passed_gates']}/{readiness['total_gates']}",
        "mechanism_ablation_status": str(ablation["status"]),
        "generality_status": str(generality["status"]),
        "core_status": str(core["status"]),
        "core_reference_status": str(core_reference["status"]),
        "core_module_benchmark_status": str(core_benchmark["status"]),
        "core_module_benchmark_full_core_f1": float(core_benchmark["verdict"]["full_core_mean_f1"]),
        "core_module_benchmark_action_health_fp_lift": int(core_benchmark["verdict"]["remove_action_health_false_positive_lift"]),
        "core_module_benchmark_invariant_fp_lift": int(core_benchmark["verdict"]["remove_invariant_false_positive_lift"]),
        "adapter_status": str(adapter["status"]),
        "big_bet_count": int(big_bets["count"]),
        "og_only_assignment_teacher_probe_status": str(og_probe["verdict"]["status"]),
        "assignment_gap_decomposition_probe_status": str(assignment_gap["verdict"]["status"]),
        "assignment_gap_mean_row_support_gap": float(assignment_gap["verdict"]["mean_row_support_gap"]),
        "hidden_row_support_sensor_probe_status": str(row_support_sensor["verdict"]["status"]),
        "hidden_row_support_best_family": str(row_support_sensor["verdict"]["best_portable_family"]),
        "hidden_row_support_mean_row_auc": float(row_support_sensor["verdict"]["best_portable_mean_row_auc"]),
        "hidden_row_support_mean_cell_recall": float(row_support_sensor["verdict"]["best_portable_mean_cell_recall_with_stage_prior"]),
        "masked_row_support_objective_probe_status": str(masked_row_support["verdict"]["status"]),
        "masked_row_support_full_row_auc": float(masked_row_support["verdict"]["full_composite_mean_row_auc"]),
        "masked_row_support_full_cell_recall": float(masked_row_support["verdict"]["full_composite_mean_cell_recall"]),
        "masked_row_support_group_stress_auc": float(masked_row_support["verdict"]["group_stress_full_mean_auc"]),
        "row_support_strict_action_decoder_status": str(row_support_decoder["verdict"]["status"]),
        "row_support_strict_action_decoder_recommended": str(row_support_decoder["verdict"]["recommended_variant"]),
        "row_support_strict_action_decoder_changed_cells": int(row_support_decoder["verdict"]["exploratory_changed_cells"]),
        "row_support_strict_action_decoder_safety_z": float(row_support_decoder["verdict"]["exploratory_safety_z"]),
        "route_frontier_action_decoder_status": str(route_frontier_decoder["verdict"]["status"]),
        "route_frontier_action_decoder_recommended": str(route_frontier_decoder["verdict"]["recommended_variant"]),
        "route_frontier_action_decoder_variant_scores": route_frontier_decoder["verdict"]["variant_scores"],
        "route_toxicity_fusion_decoder_status": str(route_toxicity_fusion_decoder["verdict"]["status"]),
        "route_toxicity_fusion_decoder_recommended": str(route_toxicity_fusion_decoder["verdict"]["recommended_variant"]),
        "route_toxicity_fusion_decoder_variant_scores": route_toxicity_fusion_decoder["verdict"]["variant_scores"],
        "decoder_order_jury_solver_status": str(decoder_order_jury["verdict"]["status"]),
        "decoder_order_jury_solver_recommended_lb_sensor": decoder_order_jury["verdict"]["recommended_lb_sensor"],
        "decoder_boundary_tomography_status": str(decoder_boundary_tomography["verdict"]["status"]),
        "decoder_boundary_tomography_recommended_lb_sensor": decoder_boundary_tomography["verdict"]["recommended_lb_sensor"],
        "decoder_boundary_tomography_inventory": decoder_boundary_tomography["boundary_inventory"],
        "core_mediated_action_release_status": str(core_mediated_release["verdict"]["status"]),
        "core_mediated_action_release_recommended_lb_sensor": core_mediated_release["verdict"]["recommended_lb_sensor"],
        "core_mediated_action_release_inventory": core_mediated_release["cell_inventory"],
        "core_release_ablation_probe_status": str(core_release_ablation["verdict"]["status"]),
        "core_release_ablation_recommended_lb_candidate": core_release_ablation["verdict"]["recommended_lb_candidate"],
        "core_release_ablation_recommended_architecture_sensor": core_release_ablation["verdict"]["recommended_architecture_sensor"],
        "core_release_ablation_recommended_negative_control": core_release_ablation["verdict"]["recommended_negative_control"],
        "core_health_calibrated_release_status": str(core_health_calibrated["verdict"]["status"]),
        "core_health_calibrated_recommended_lb_candidate": core_health_calibrated["verdict"]["recommended_lb_candidate"],
        "core_health_calibrated_recommended_big_bet_sensor": core_health_calibrated["verdict"]["recommended_big_bet_sensor"],
        "core_health_calibrated_recommended_pressure_sensor": core_health_calibrated["verdict"]["recommended_pressure_sensor"],
        "cross_listener_transport_status": str(cross_listener_transport["verdict"]["status"]),
        "cross_listener_transport_recommended_lb_sensor": cross_listener_transport["verdict"]["recommended_lb_sensor"],
        "cross_listener_transport_recommended_big_bet": cross_listener_transport["verdict"]["recommended_big_bet"],
        "counterfactual_listener_dropout_md": str(COUNTERFACTUAL_LISTENER_DROPOUT_MD.resolve()),
        "counterfactual_listener_dropout_json": str(COUNTERFACTUAL_LISTENER_DROPOUT_JSON.resolve()),
        "counterfactual_listener_dropout_status": str(counterfactual_listener_dropout.get("status")),
        "counterfactual_listener_dropout_recommended_information_sensor": listener_dropout_verdict.get("recommended_information_sensor"),
        "spectral_public_tangent_md": str(SPECTRAL_PUBLIC_TANGENT_MD.resolve()),
        "spectral_public_tangent_json": str(SPECTRAL_PUBLIC_TANGENT_JSON.resolve()),
        "spectral_public_tangent_status": str(spectral_public_tangent.get("status")),
        "spectral_public_tangent_recommended_information_sensor": spectral_tangent_verdict.get("recommended_information_sensor"),
        "negative_tangent_invariant_projection_md": str(NEGATIVE_TANGENT_INVARIANT_MD.resolve()),
        "negative_tangent_invariant_projection_json": str(NEGATIVE_TANGENT_INVARIANT_JSON.resolve()),
        "negative_tangent_invariant_projection_status": str(negative_projection_verdict.get("status")),
        "negative_tangent_invariant_projection_recommended": negative_projection_verdict.get("recommended_variant"),
        "lb_conditioned_responsibility_md": str(LB_CONDITIONED_RESPONSIBILITY_MD.resolve()),
        "lb_conditioned_responsibility_json": str(LB_CONDITIONED_RESPONSIBILITY_JSON.resolve()),
        "lb_conditioned_responsibility_status": str(lb_responsibility_verdict.get("status")),
        "lb_conditioned_responsibility_recommended": lb_recommended,
        "lb_conditioned_responsibility_recommended_file": lb_recommended_submission.get("submission_file"),
        "lb_conditioned_responsibility_loo_corr": lb_responsibility_fit.get("loo_corr"),
        "lb_conditioned_responsibility_changed_cells": lb_recommended_submission.get("changed_cells"),
        "lb_conditioned_responsibility_predicted_loss_delta": lb_recommended_metrics.get("sum_predicted_loss_delta"),
        "mixture_listener_responsibility_md": str(MIXTURE_LISTENER_RESPONSIBILITY_MD.resolve()),
        "mixture_listener_responsibility_json": str(MIXTURE_LISTENER_RESPONSIBILITY_JSON.resolve()),
        "public_private_subset_tomography_md": str(PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_MD.resolve()),
        "public_private_subset_tomography_json": str(PUBLIC_PRIVATE_SUBSET_TOMOGRAPHY_JSON.resolve()),
        "mixture_listener_responsibility_status": str(mixture_listener_verdict.get("status")),
        "mixture_listener_responsibility_recommended": mixture_recommended,
        "mixture_listener_responsibility_recommended_file": mixture_recommended_submission.get("submission_file"),
        "mixture_listener_responsibility_loo_corr": mixture_listener_responsibility.get("mixture_fit", {}).get("loo_corr"),
        "mixture_listener_responsibility_scalar_loo_corr": mixture_listener_responsibility.get("mixture_fit", {}).get("scalar_fit", {}).get("loo_corr"),
        "mixture_listener_responsibility_changed_cells": mixture_recommended_submission.get("changed_cells"),
        "mixture_listener_responsibility_scalar_delta": mixture_recommended_metrics.get("sum_predicted_scalar_delta"),
        "mixture_listener_responsibility_mode_delta": mixture_recommended_metrics.get("sum_predicted_total_mode_delta"),
        "public_private_subset_tomography_status": str(subset_tomography_verdict.get("status")),
        "public_private_subset_tomography_recommended": subset_tomography_recommended,
        "public_private_subset_tomography_recommended_file": subset_tomography_submission.get("submission_file"),
        "public_private_subset_tomography_source_loo_corr": public_private_subset_tomography.get("source_fit", {}).get("loo_corr"),
        "public_private_subset_tomography_changed_cells": subset_tomography_submission.get("changed_cells"),
        "public_private_subset_tomography_predicted_loss_delta": subset_tomography_metrics.get("sum_predicted_public_delta"),
        "action_decoder_ablation_suite_status": str(action_decoder_ablation["verdict"]["status"]),
        "action_decoder_ablation_suite_recommended_lb_sensor": action_decoder_ablation["verdict"]["recommended_lb_sensor"],
        "action_decoder_ablation_suite_big_bet_sensor": action_decoder_ablation["verdict"]["big_bet_sensor"],
        "listener_invariant_contrastive_probe_status": str(contrastive_probe["verdict"]["status"]),
        "private_safe_toxicity_probe_status": str(private_toxicity_probe["verdict"]["status"]),
        "hardworld_toxicity_factorization_probe_status": str(hardworld_toxicity_probe["verdict"]["status"]),
        "factorized_toxicity_decoder_variant_count": int(len(factorized_decoder.get("variants", {}))),
        "factorized_toxicity_decoder_stress_status": str(factorized_stress.get("status")),
        "factorized_toxicity_decoder_supported_variants": [
            name
            for name, item in factorized_stress.get("variants", {}).items()
            if isinstance(item, dict) and item.get("verdict", {}).get("status") == "factorized_decoder_stress_supported"
        ],
        "core_adapter_boundary_status": str(boundary_audit.get("status")),
        "core_adapter_boundary_checks": f"{boundary_audit.get('passed_checks')}/{boundary_audit.get('total_checks')}",
        "release_status": str(release["status"]),
        "release_checks": f"{release['passed_checks']}/{release['total_checks']}",
        "mechanism_evidence": validation["mechanism_evidence"],
        "submission_files": {
            role: item["submission_file"]
            for role, item in package["packaged_submissions"].items()
        },
    }
    HANDOFF_MD.write_text(handoff_md, encoding="utf-8")
    HANDOFF_JSON.write_text(json.dumps(handoff, indent=2, ensure_ascii=False), encoding="utf-8")
    RUN_LOG_JSON.write_text(json.dumps(command_records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(handoff, indent=2, ensure_ascii=False))
    return handoff


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="rerun dependency modules before package/audit/validation")
    args = parser.parse_args()
    run(refresh=args.refresh)


if __name__ == "__main__":
    main()
