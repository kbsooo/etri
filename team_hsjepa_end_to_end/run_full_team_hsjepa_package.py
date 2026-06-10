#!/usr/bin/env python3
"""Run the full team-facing HS-JEPA package.

This is the single command a teammate should run when they do not know any
historical experiment version names.  It executes:

1. HS-JEPA core architecture manifest.
2. Route-Conserving S2 Bridge package generation.
3. Stress audit against feasible candidate nulls.
4. Claim/evidence validation.
5. Reproducibility contract.
6. Architecture readiness report.
7. Mechanism ablation report.
8. OG-only assignment teacher probe.
9. Assignment-gap decomposition probe.
10. Hidden row-support sensor transfer probe.
11. Masked row-support objective stress probe.
12. Listener-invariant contrastive probe.
13. Private-safe toxicity probe.
14. Hard-world toxicity factorization probe.
15. Factorized toxicity decoder candidate.
16. Factorized toxicity decoder stress audit.
17. Generality report.
18. Sleep competition adapter report and big-bet queue.
19. Core/adapter boundary audit.
20. Paper method packet.
21. Pipeline manifest.
22. Release checklist.
23. A compact handoff report for paper and competition discussion.
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
    adapter: dict[str, object],
    big_bets: dict[str, object],
    og_probe: dict[str, object],
    assignment_gap: dict[str, object],
    row_support_sensor: dict[str, object],
    masked_row_support: dict[str, object],
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
            f"- Adapter status: `{adapter['status']}`",
            f"- Adapter score delta: `{adapter['score_evidence']['delta']}`",
            f"- OG-only assignment probe: `{og_verdict.get('status')}`",
            f"- Assignment-gap decomposition: `{gap_verdict.get('status')}`",
            f"- Hidden row-support sensor: `{row_support_verdict.get('status')}`",
            f"- Masked row-support objective: `{masked_row_support_verdict.get('status')}`",
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
            f"- Listener-invariant boundary: listener-route rho `{contrastive_verdict.get('mean_listener_route_spearman'):.4f}`, contrastive overlap `{contrastive_verdict.get('mean_contrastive_overlap_rate'):.4f}`",
            f"- Private-safe toxicity boundary: mean LOO AUC `{toxicity_verdict.get('mean_loo_bad_anchor_auc'):.4f}`, worst LOO AUC `{toxicity_verdict.get('worst_loo_bad_anchor_auc'):.4f}`",
            f"- Hard-world factorization: broad->H088 AUC `{hardworld_verdict.get('broad_predicts_hardworld_auc'):.4f}`, broad/H088 rho `{hardworld_verdict.get('broad_hardworld_spearman'):.4f}`",
            f"- Factorized decoder candidates: `{', '.join(sorted(factorized_variants))}`",
            f"- Factorized decoder stress: `{factorized_stress_statuses}`",
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
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "listener_invariant_contrastive_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "private_safe_toxicity_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "hardworld_toxicity_factorization_probe.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "factorized_toxicity_decoder_candidate.py")],
        [sys.executable, str(ROOT / "sleep_competition_adapter" / "factorized_toxicity_decoder_stress_audit.py")],
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
    adapter = read_json(ADAPTER_REPORT_JSON)
    big_bets = read_json(BIG_BET_JSON)
    og_probe = read_json(OG_PROBE_JSON)
    assignment_gap = read_json(ASSIGNMENT_GAP_JSON)
    row_support_sensor = read_json(ROW_SUPPORT_SENSOR_JSON)
    masked_row_support = read_json(MASKED_ROW_SUPPORT_JSON)
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
        adapter,
        big_bets,
        og_probe,
        assignment_gap,
        row_support_sensor,
        masked_row_support,
        contrastive_probe,
        private_toxicity_probe,
        hardworld_toxicity_probe,
        factorized_decoder,
        factorized_stress,
        boundary_audit,
        release,
    )

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
