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
        for path in [PACKAGE_JSON, STRESS_CSV, EVIDENCE_CSV, VALIDATION_JSON, CONTRACT_JSON, READINESS_JSON]
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
    stress = pd.read_csv(STRESS_CSV)
    evidence = pd.read_csv(EVIDENCE_CSV)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    primary = readiness["mechanism"]["primary"]
    s2 = readiness["mechanism"]["s2_listener"]
    boundary = contract["boundary"]

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
        "title": "Human-State JEPA with Route-Conserving S2 Bridge Decoder",
        "short_name": "HS-JEPA Route-Conserving S2 Bridge",
        "status": readiness["status"],
        "one_sentence": (
            "HS-JEPA treats sleep-log prediction as hidden human-state oriented sparse "
            "row-target action decoding, then constrains objective-stage corrections "
            "to preserve the learned Q/S route manifold through an S2 listener bridge."
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
            "role": "orientation diagnostic, not complete row-target assignment solver",
        },
        "roles": roles,
        "boundary": boundary,
        "outputs": {
            "method_packet_md": str(PACKET_MD.resolve()),
            "method_packet_json": str(PACKET_JSON.resolve()),
            "readiness_report": str(READINESS_JSON.resolve()),
            "reproducibility_contract": str(CONTRACT_JSON.resolve()),
            "one_command": "python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py",
        },
        "paper_sections": {
            "abstract_ko": build_abstract(public, primary, s2, human),
            "method_ko": build_method_text(),
            "algorithm_ko": build_algorithm_text(),
            "limitations_ko": build_limitations_text(boundary),
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
        "우리는 수면 기반 생활 로그 예측을 독립적인 7개 label 분류 문제가 아니라, "
        "숨은 인간 생활 상태가 만드는 sparse row-target action decoding 문제로 재정의한다. "
        "제안하는 HS-JEPA는 raw label을 직접 복원하지 않고 human-state, target-listener, "
        "row-target action, route-consistency energy를 분리한다. 특히 objective sleep-stage "
        "target에서는 public-sensitive driver action을 단독으로 적용하지 않고, train label에서 "
        "학습한 Q/S route manifold를 보존하는 bridge action을 함께 선택한다. 실험적으로 이 "
        "route-conserving decoder는 기존 public-equation 이전 최고 public LB "
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


def build_method_text() -> str:
    return "\n".join(
        [
            "HS-JEPA는 다음 네 계층으로 구성된다.",
            "",
            "1. Human-State Encoder: OG 생활 로그, 개인/코호트 상태, 수면 상태의 deviation을 latent context로 변환한다.",
            "2. Target Listener Representation: 각 target이 현재 hidden state와 어떤 방향으로 반응하는지 cell-level orientation을 예측한다.",
            "3. Row-Target Assignment Solver: 실제로 움직일 sparse row-target support를 찾는다. 이 단계는 competition-specific public sensor를 사용하므로 논문 claim에서 분리한다.",
            "4. Route-Conserving S2 Bridge Decoder: driver target을 단독 이동하지 않고, Q/S route energy를 낮추는 bridge target을 함께 선택한다.",
            "",
            "핵심은 label probability를 크게 만드는 것이 아니라, action 이후의 7-target vector가 train label의 공동 구조를 덜 위반하도록 만드는 것이다.",
        ]
    )


def build_algorithm_text() -> str:
    return "\n".join(
        [
            "Algorithm: Route-Conserving S2 Bridge HS-JEPA",
            "",
            "Input: OG lifestyle logs, train labels, public-sensor action anchors, current best prediction.",
            "Output: sparse row-target correction field and upload-safe submission.",
            "",
            "1. Learn a Q/S route energy model from train labels.",
            "2. Build human-state and target-listener representations from OG/context artifacts.",
            "3. Identify public-sensitive driver cells from the action anchor field.",
            "4. For each driver cell, enumerate same-row objective-stage bridge candidates.",
            "5. Score each driver/bridge bundle by public utility, route-energy gain, S2 listener usage, and toxicity stress.",
            "6. Select sparse non-overlapping bundles under target/row budget constraints.",
            "7. Apply bounded logit-space corrections and validate upload safety.",
            "8. Stress-audit the selected bundles against random feasible bundle nulls.",
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
            "",
            "## Role-Based Outputs",
            "",
            *role_rows,
            "",
            "## Stress Evidence",
            "",
            *stress_rows,
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
            "",
        ]
    )


def main() -> None:
    build_packet()


if __name__ == "__main__":
    main()
