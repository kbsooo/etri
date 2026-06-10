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
ADAPTER_REPORT_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "sleep_competition_adapter_report.json"
BIG_BET_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hsjepa_big_bet_queue.json"
OG_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "og_only_assignment_teacher_probe.json"
ASSIGNMENT_GAP_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "assignment_gap_decomposition_probe.json"
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
            ADAPTER_REPORT_JSON,
            BIG_BET_JSON,
            OG_PROBE_JSON,
            ASSIGNMENT_GAP_JSON,
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
    adapter = read_json(ADAPTER_REPORT_JSON)
    big_bets = read_json(BIG_BET_JSON)
    og_probe = read_json(OG_PROBE_JSON)
    assignment_gap = read_json(ASSIGNMENT_GAP_JSON)
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
            "core_adapter_boundary_audit": str(BOUNDARY_AUDIT_JSON.resolve()),
            "sleep_adapter_report": str(ADAPTER_REPORT_JSON.resolve()),
            "big_bet_queue": str(BIG_BET_JSON.resolve()),
            "og_only_assignment_teacher_probe": str(OG_PROBE_JSON.resolve()),
            "assignment_gap_decomposition_probe": str(ASSIGNMENT_GAP_JSON.resolve()),
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
            "generality_ko": build_generality_text(generality, og_verdict, gap_verdict, contrastive_verdict, toxicity_verdict, hardworld_verdict),
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
            "이번 수면 대회에서는 listener가 Q1/Q2/Q3/S1/S2/S3/S4로, invariant가 Q/S route energy로, action-health가 public/private toxicity 및 feasible-bundle stress로 구현되었다. 새 hard-world probe는 broad toxicity와 H088 toxicity가 역상관될 수 있음을 보여주므로, action-health는 단일 위험 점수가 아니라 factorized energy head로 다루어야 한다. 핵심은 `S2` 자체가 아니라, hidden state를 직접 label로 쓰지 않고 core의 listener/action/invariant 경로를 adapter가 안전한 sparse row-target action으로 번역한다는 점이다.",
        ]
    )


def build_generality_text(
    generality: dict[str, object],
    og_verdict: dict[str, object],
    gap_verdict: dict[str, object],
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
        f"- Listener-invariant probe: `{contrastive_verdict['status']}`",
        f"- Listener-route Spearman: `{fmt(contrastive_verdict['mean_listener_route_spearman'], 4)}`",
        f"- Private-safe toxicity probe: `{toxicity_verdict['status']}`",
        f"- Toxicity mean LOO AUC: `{fmt(toxicity_verdict['mean_loo_bad_anchor_auc'], 4)}`",
        f"- Toxicity worst LOO AUC: `{fmt(toxicity_verdict['worst_loo_bad_anchor_auc'], 4)}`",
        f"- Hard-world factorization probe: `{hardworld_verdict['status']}`",
        f"- Broad toxicity -> H088 AUC: `{fmt(hardworld_verdict['broad_predicts_hardworld_auc'], 4)}`",
        f"- Broad/H088 Spearman: `{fmt(hardworld_verdict['broad_hardworld_spearman'], 4)}`",
        "",
        "가장 중요한 남은 과제는 target route가 아니라 hidden row-support sensor다. 현재 calendar/cohort/latent/peer-route context는 portable assignment teacher로 부족하며, public-sensor row-target assignment teacher를 OG-only personal/cohort/time human-state teacher로 교체하려면 row-support를 복원하는 새 context objective가 필요하다. 동시에 이미 생성된 broad-public/hard-world factorized decoder 후보가 실제 public/private score에서 action-grade decoder인지 검증해야 한다.",
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
            "3. Estimate listener responsibility: which outcomes should react to the hidden state.",
            "4. Estimate action-health: whether the latent signal is safe to translate into output movement.",
            "5. Factorize action-health when shortcut modes are anti-correlated rather than scalar.",
            "6. Learn an invariant energy over valid output/action manifolds.",
            "7. Decode bounded actions that improve listener fit while preserving the invariant.",
            "8. Reject shortcuts with cohort/time/group/null stress tests.",
            "9. In the sleep-log case study, instantiate the invariant as Q/S route energy and the decoder as the S2 bridge.",
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
            f"- `{packet['outputs']['core_adapter_boundary_audit']}`",
            f"- `{packet['outputs']['sleep_adapter_report']}`",
            f"- `{packet['outputs']['big_bet_queue']}`",
            f"- `{packet['outputs']['assignment_gap_decomposition_probe']}`",
            "",
        ]
    )


def main() -> None:
    build_packet()


if __name__ == "__main__":
    main()
