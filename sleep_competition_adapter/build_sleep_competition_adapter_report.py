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
        METHOD_PACKET_JSON,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing sleep adapter inputs: {missing}")


def build_big_bets() -> list[dict[str, object]]:
    return [
        {
            "id": "og_only_assignment_teacher",
            "name": "OG-only Human-State Assignment Teacher",
            "worldview": "The public-sensor teacher can be replaced by personal/cohort/time human-state consistency.",
            "core_modules_exercised": ["context_encoder", "masked_state_predictor", "listener_responsibility", "anti_shortcut_validation"],
            "adapter_move": "Train a row-target support teacher from OG personal/cohort/time masks, then feed it into the existing invariant decoder.",
            "why_big": "If it works, HS-JEPA becomes a portable architecture rather than a public-sensor case study.",
            "expected_public_lb_delta_if_true": -0.003,
            "kill_criterion": "Cell orientation remains high but row assignment stays near random under subject/time stress.",
        },
        {
            "id": "listener_invariant_contrastive_decoder",
            "name": "Listener-Invariant Contrastive Decoder",
            "worldview": "A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone.",
            "core_modules_exercised": ["listener_responsibility", "action_health_decoder", "invariant_energy"],
            "adapter_move": "Score candidate row-target actions by listener gain minus route-energy toxicity under random feasible nulls.",
            "why_big": "This could move beyond the current S2 bridge into a general action-health decoder.",
            "expected_public_lb_delta_if_true": -0.002,
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
            "kill_criterion": "Toxicity score only recovers known public failures and does not separate local nulls.",
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
    method = read_json(METHOD_PACKET_JSON)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    mechanism = validation["mechanism_evidence"]

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
        "role_outputs": {
            role: item["submission_file"]
            for role, item in package["packaged_submissions"].items()
        },
        "what_the_adapter_proves": [
            "HS-JEPA-style listener/action/invariant separation can explain the 0.567 public-LB breakthrough case study.",
            "Route-conserving action selection is statistically non-random against feasible null bundles.",
            "Human-state latent explains target/cell orientation but not enough row assignment on its own.",
        ],
        "what_the_adapter_does_not_prove": [
            "pure OG-only assignment",
            "private leaderboard safety",
            "S2 as a universal human-sleep factor",
            "that public LB sensors can be used outside this competition",
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
        "| Big bet | Worldview | Adapter move | Expected LB delta if true | Kill criterion |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for bet in bets:
        rows.append(
            f"| `{bet['name']}` | {bet['worldview']} | {bet['adapter_move']} | `{bet['expected_public_lb_delta_if_true']}` | {bet['kill_criterion']} |"
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
            "2. `Listener-Invariant Contrastive Decoder`: 현재 S2 bridge를 일반 action-health decoder로 확장한다.",
            "3. `Private-Safe Toxicity Field`: public-specific gain의 private risk를 줄이는 방향이다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    report = build_report()
    bets = build_big_bets()
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
