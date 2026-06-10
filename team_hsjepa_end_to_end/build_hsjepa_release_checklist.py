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
METHOD_PACKET_JSON = OUT / "hsjepa_paper_method_packet.json"
PIPELINE_JSON = OUT / "hsjepa_pipeline_manifest.json"
CORE_MANIFEST_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_manifest.json"
CORE_ABLATION_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_ablation_contract.json"
ADAPTER_REPORT_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "sleep_competition_adapter_report.json"
BIG_BET_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hsjepa_big_bet_queue.json"

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
        METHOD_PACKET_JSON,
        CORE_MANIFEST_JSON,
        CORE_ABLATION_JSON,
        ADAPTER_REPORT_JSON,
        BIG_BET_JSON,
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
    method = read_json(METHOD_PACKET_JSON)
    core = read_json(CORE_MANIFEST_JSON)
    core_ablation = read_json(CORE_ABLATION_JSON)
    adapter = read_json(ADAPTER_REPORT_JSON)
    big_bets = read_json(BIG_BET_JSON)
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
                "core_ablation_contract_present",
                core_ablation.get("status") == "ablation_contract_ready"
                and len(core_ablation.get("ablations", [])) >= 6,
                f"status={core_ablation.get('status')}, ablations={len(core_ablation.get('ablations', []))}",
            ),
            check(
                "big_bet_queue_high_ceiling",
                big_bets.get("status") == "big_bet_queue_ready"
                and len(big_bets.get("bets", [])) >= 3
                and any(float(bet.get("expected_public_lb_delta_if_true", 0.0)) <= -0.002 for bet in big_bets.get("bets", [])),
                f"status={big_bets.get('status')}, count={len(big_bets.get('bets', []))}",
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
            "- human-state is an orientation diagnostic, not a complete row-target assignment solver",
            "- HS-JEPA Core is separated from the Sleep Competition Adapter",
            "- the next big bet is replacing public-sensor assignment with an OG-only human-state teacher",
            "",
        ]
    )


def main() -> None:
    result = build_checklist()
    sys.exit(0 if result["status"] == "release_ready_with_boundary" else 1)


if __name__ == "__main__":
    main()
