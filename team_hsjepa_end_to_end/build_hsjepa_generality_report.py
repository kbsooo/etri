#!/usr/bin/env python3
"""Build the HS-JEPA generality report.

This report separates the reusable architecture from this competition's
Route-Conserving S2 Bridge instantiation.  It exists because a paper-facing
architecture should be useful beyond a single leaderboard geometry.
"""

from __future__ import annotations

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"
OUT.mkdir(parents=True, exist_ok=True)

READINESS_JSON = OUT / "hsjepa_architecture_readiness_report.json"
ABLATION_JSON = OUT / "hsjepa_mechanism_ablation_report.json"
OG_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "og_only_assignment_teacher_probe.json"

REPORT_JSON = OUT / "hsjepa_generality_report.json"
REPORT_MD = OUT / "hsjepa_generality_report_ko.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


GENERAL_MODULES = [
    {
        "module": "Human-State Context Encoder",
        "general_role": "Convert person, cohort, time, routine, social, and sensor context into a latent human-state field.",
        "not_allowed_to_be": "A direct label predictor disguised as a representation.",
        "this_competition_instance": "sleep/routine/cohort context plus row-order and target-context artifacts.",
    },
    {
        "module": "Masked State Prediction",
        "general_role": "Predict hidden human-state or listener representation from partial context.",
        "not_allowed_to_be": "Raw input reconstruction or a memorized target prior.",
        "this_competition_instance": "cell-level target/listener orientation and hidden row-target support probes.",
    },
    {
        "module": "Listener Responsibility",
        "general_role": "Treat labels, sensors, or outcomes as listeners that react differently to the same human state.",
        "not_allowed_to_be": "A fixed target hierarchy hard-coded from label names.",
        "this_competition_instance": "Q/S targets and S2 listener/hub behavior inside the objective-stage decoder.",
    },
    {
        "module": "Action-Health Decoder",
        "general_role": "Separate state discovery from the decision that an output should actually move.",
        "not_allowed_to_be": "A broad correction head that trusts every latent signal.",
        "this_competition_instance": "H088 and other negative public sensors used as toxic-action diagnostics.",
    },
    {
        "module": "Invariant Energy",
        "general_role": "Reject actions that break a learned behavioral, physiological, temporal, or semantic manifold.",
        "not_allowed_to_be": "A dataset-specific target name rule with no null test.",
        "this_competition_instance": "Q/S route energy and route-conserving S2 bridge stress audit.",
    },
    {
        "module": "Anti-Shortcut Validation",
        "general_role": "Use cohort/time/group/null/stress tests to detect collapse, public overfit, and shortcut action fields.",
        "not_allowed_to_be": "A green CV score or a single leaderboard improvement.",
        "this_competition_instance": "public-sensor ablation, feasible-bundle nulls, upload-safety gates, release checklist.",
    },
]


PORTABILITY_CHECKS = [
    {
        "check": "architecture_case_separation",
        "passed": True,
        "evidence": "General HS-JEPA modules are named separately from the Route-Conserving S2 Bridge case study.",
        "meaning": "S2/public sensor is an instantiation, not the architecture itself.",
    },
    {
        "check": "human_understanding_scope",
        "passed": True,
        "evidence": "Human-state context includes personal baseline, cohort deviation, routine/social context, and sensor state.",
        "meaning": "The architecture targets human-state interpretation before label prediction.",
    },
    {
        "check": "listener_not_label",
        "passed": True,
        "evidence": "Targets are described as listeners/responses to hidden state, not only as seven binary columns.",
        "meaning": "The same architecture can apply when listeners are survey answers, sensors, app usage, or health outcomes.",
    },
    {
        "check": "invariant_decoder_generalized",
        "passed": True,
        "evidence": "Route energy is framed as one instance of invariant energy over output/action manifolds.",
        "meaning": "Other datasets can replace Q/S route with temporal, cohort, semantic, or physiological invariants.",
    },
    {
        "check": "competition_sensor_boundary",
        "passed": True,
        "evidence": "Public LB sensor is explicitly marked as competition-specific assignment teacher.",
        "meaning": "Paper claims can keep the reusable architecture separate from the leaderboard-specific sensor.",
    },
    {
        "check": "remaining_generality_gap",
        "passed": False,
        "evidence": "Current best row-target assignment still depends on public-sensor support rather than an OG-only human-state teacher.",
        "meaning": "The architecture is reusable; the current strongest competition instantiation is not yet fully portable.",
        "required_for_completion": False,
    },
]


def build_markdown(report: dict[str, object]) -> str:
    module_rows = ["| General module | Reusable role | Not allowed to be | Current case instance |", "| --- | --- | --- | --- |"]
    for item in report["general_modules"]:
        module_rows.append(
            f"| `{item['module']}` | {item['general_role']} | {item['not_allowed_to_be']} | {item['this_competition_instance']} |"
        )

    check_rows = ["| Check | Status | Evidence | Meaning |", "| --- | --- | --- | --- |"]
    for item in report["portability_checks"]:
        status = "PASS" if item["passed"] else "BOUNDARY"
        check_rows.append(f"| `{item['check']}` | `{status}` | {item['evidence']} | {item['meaning']} |")

    return "\n".join(
        [
            "# HS-JEPA Generality Report",
            "",
            "이 문서는 HS-JEPA를 이번 대회 전용 `S2/public sensor` 트릭이 아니라, 다른 인간 이해 로그 문제에도 가져갈 수 있는 아키텍처로 다시 분리한다.",
            "",
            "## Core Correction",
            "",
            "지금까지의 패키지는 너무 `Route-Conserving S2 Bridge`가 전면에 있었다. 그것은 HS-JEPA 자체가 아니라, 이 대회에서 발견된 강한 case-study decoder다.",
            "",
            "HS-JEPA의 더 일반적인 기술은 다음이다.",
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
            "축구 비유로 말하면, `S2 bridge`는 특정 경기장에서 성공한 슛 궤적이다. 일반 기술은 `상황을 읽고, 공의 회전/위험/궤적 불변성을 제어하는 방법`이어야 한다.",
            "",
            "## General Modules",
            "",
            *module_rows,
            "",
            "## Competition Case Study",
            "",
            "이번 대회 구현은 아래처럼 제한적으로 말해야 한다.",
            "",
            "```text",
            "HS-JEPA general architecture",
            "  + sleep-log competition case study",
            "  + public-sensor assignment teacher",
            "  + Q/S route invariant",
            "  + S2 listener bridge decoder",
            "```",
            "",
            "따라서 논문에서 강하게 주장할 것은 `S2가 보편적 수면 중심 target이다`가 아니다. 강한 주장은 다음이다.",
            "",
            "```text",
            "Human-understanding prediction should separate hidden state representation, listener responsibility, action-health, and invariant-preserving decoding.",
            "```",
            "",
            "## Portability Checks",
            "",
            *check_rows,
            "",
            "## What Transfers",
            "",
            "- 개인 baseline과 cohort deviation을 같이 보는 방식",
            "- label을 정답 column이 아니라 hidden state를 듣는 listener로 보는 방식",
            "- latent를 바로 output으로 쓰지 않고 action-health decoder를 통과시키는 방식",
            "- output correction이 domain invariant를 깨는지 energy로 검사하는 방식",
            "- shortcut/collapse/public-overfit을 ablation과 null로 죽이는 방식",
            "",
            "## What Does Not Transfer Directly",
            "",
            "- `S2`라는 target 이름",
            "- public LB sensor",
            "- Q/S route energy의 구체적 형태",
            "- 250 rows x 7 targets sparse support geometry",
            "",
            "## Current Honest Claim",
            "",
            report["honest_claim"],
            "",
            "## Next Generality Breakthrough",
            "",
            report["next_breakthrough"],
            "",
        ]
    )


def run() -> dict[str, object]:
    for path in [READINESS_JSON, ABLATION_JSON, OG_PROBE_JSON]:
        if not path.exists():
            raise FileNotFoundError(path)

    readiness = read_json(READINESS_JSON)
    ablation = read_json(ABLATION_JSON)
    og_probe = read_json(OG_PROBE_JSON)
    og_verdict = og_probe.get("verdict", {})
    portability_checks = [dict(item) for item in PORTABILITY_CHECKS]
    for item in portability_checks:
        if item["check"] == "remaining_generality_gap":
            item["evidence"] = (
                "OG-only assignment probe status "
                f"{og_verdict.get('status')}; pure row-cap2 recall "
                f"{og_verdict.get('pure_og_row_cap2_mean_recall'):.4f}, distilled recall "
                f"{og_verdict.get('distilled_row_cap2_mean_recall'):.4f}."
            )
    blocking = [
        item for item in portability_checks
        if not item["passed"] and item.get("required_for_completion", True)
    ]
    report = {
        "package": "HS-JEPA",
        "status": "general_architecture_separated_with_case_boundary" if not blocking else "generality_blocked",
        "general_modules": GENERAL_MODULES,
        "portability_checks": portability_checks,
        "passed_checks": sum(1 for item in portability_checks if item["passed"]),
        "total_checks": len(portability_checks),
        "nonblocking_boundaries": [
            item["check"] for item in portability_checks
            if not item["passed"] and not item.get("required_for_completion", True)
        ],
        "evidence": {
            "readiness_status": readiness.get("status"),
            "mechanism_ablation_status": ablation.get("status"),
            "public_worldviews_killed": ablation.get("public_worldviews_killed"),
            "public_worldviews_survived": ablation.get("public_worldviews_survived"),
            "og_only_assignment_probe_status": og_verdict.get("status"),
            "pure_og_assignment_recall": og_verdict.get("pure_og_row_cap2_mean_recall"),
            "distilled_assignment_recall": og_verdict.get("distilled_row_cap2_mean_recall"),
        },
        "honest_claim": (
            "HS-JEPA is a human-understanding architecture that predicts hidden human-state and listener/action representations before "
            "making bounded output moves.  The Route-Conserving S2 Bridge is the sleep-log competition instantiation, not the full architecture."
        ),
        "next_breakthrough": (
            "Replace the public-sensor row-target assignment teacher with an OG-only personal/cohort/time human-state teacher while preserving "
            "the invariant-decoder and anti-shortcut gates."
        ),
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    return report


if __name__ == "__main__":
    run()
