#!/usr/bin/env python3
"""Run the full team-facing HS-JEPA package.

This is the single command a teammate should run when they do not know any
historical experiment version names.  It executes:

1. Route-Conserving S2 Bridge package generation.
2. Stress audit against feasible candidate nulls.
3. Claim/evidence validation.
4. Reproducibility contract.
5. Architecture readiness report.
6. Paper method packet.
7. A compact handoff report for paper and competition discussion.
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
) -> str:
    packaged = package["packaged_submissions"]
    mechanism = validation["mechanism_evidence"]

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
            "public-sensitive driver action",
            "  + route-conserving bridge action",
            "  + S2 listener/hub constraint",
            "  + human-state orientation diagnostic",
            "```",
            "",
            "축구 비유로 말하면, 이 패키지의 무회전 슛은 `target correction은 route manifold를 보존해야 한다`는 규칙이다. 세부 셀을 외운 것이 아니라, 가능한 action space에서 route를 깨지 않는 driver/bridge 궤적을 고른다.",
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
            "",
            "## Paper Claim",
            "",
            "강하게 주장할 수 있는 내용:",
            "",
            "```text",
            "HS-JEPA reframes multi-label sleep prediction as sparse row-target action decoding.",
            "For objective sleep-stage targets, the decoder should not move targets independently.",
            "It should pair public-sensitive driver actions with route-conserving bridge actions.",
            "S2 emerges as the listener/hub in this route-conserving decoder.",
            "Human-state representation is useful as an orientation diagnostic, not as a complete row-assignment solver.",
            "```",
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
        ]
    )


def run(refresh: bool = False) -> dict[str, object]:
    commands = [
        [sys.executable, str(HERE / "run_route_conserving_s2_bridge.py")],
        [sys.executable, str(HERE / "audit_route_conserving_s2_bridge.py")],
        [sys.executable, str(HERE / "validate_route_conserving_s2_bridge_package.py")],
        [sys.executable, str(HERE / "inspect_hsjepa_reproducibility_contract.py")],
        [sys.executable, str(HERE / "build_hsjepa_architecture_readiness_report.py")],
        [sys.executable, str(HERE / "build_hsjepa_paper_method_packet.py")],
    ]
    if refresh:
        commands[0].append("--refresh")

    command_records = []
    for args in commands:
        command_records.append(run_command(args))

    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    readiness = read_json(READINESS_JSON)
    stress = pd.read_csv(STRESS_CSV)
    handoff_md = build_handoff(package, validation, stress, readiness)

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
        "validation_passed": bool(validation["passed"]),
        "architecture_readiness_status": str(readiness["status"]),
        "architecture_readiness_gates": f"{readiness['passed_gates']}/{readiness['total_gates']}",
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
