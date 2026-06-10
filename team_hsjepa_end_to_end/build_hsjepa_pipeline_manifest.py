#!/usr/bin/env python3
"""Build an end-to-end pipeline manifest for the team HS-JEPA package.

The reproducibility contract lists files.  The method packet explains the idea.
This manifest connects them as a role-based pipeline from raw data and public
sensor observations to submissions and paper artifacts.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"

PACKAGE_JSON = OUT / "route_conserving_s2_bridge_package.json"
EVIDENCE_CSV = OUT / "route_conserving_s2_bridge_evidence_table.csv"
STRESS_CSV = OUT / "route_conserving_s2_bridge_stress_summary.csv"
VALIDATION_JSON = OUT / "route_conserving_s2_bridge_validation_report.json"
CONTRACT_JSON = OUT / "hsjepa_reproducibility_contract.json"
READINESS_JSON = OUT / "hsjepa_architecture_readiness_report.json"
METHOD_PACKET_JSON = OUT / "hsjepa_paper_method_packet.json"

MANIFEST_JSON = OUT / "hsjepa_pipeline_manifest.json"
MANIFEST_MD = OUT / "hsjepa_pipeline_manifest_ko.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def fmt(x: object, digits: int = 6) -> str:
    if x is None:
        return "n/a"
    try:
        val = float(x)
    except (TypeError, ValueError):
        return str(x)
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def require_inputs() -> None:
    required = [PACKAGE_JSON, EVIDENCE_CSV, STRESS_CSV, VALIDATION_JSON, CONTRACT_JSON, READINESS_JSON, METHOD_PACKET_JSON]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing pipeline manifest inputs: {missing}")


def contract_category_summary(contract: dict[str, object]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for rec in contract.get("records", []):
        if not isinstance(rec, dict):
            continue
        category = str(rec.get("category"))
        bucket = summary.setdefault(category, {"records": 0, "required": 0, "missing_required": 0})
        bucket["records"] += 1
        if rec.get("required"):
            bucket["required"] += 1
            if not rec.get("exists"):
                bucket["missing_required"] += 1
    return summary


def stage(
    stage_id: str,
    name: str,
    role: str,
    inputs: list[str],
    outputs: list[str],
    evidence: list[str],
    boundary: str,
) -> dict[str, object]:
    return {
        "id": stage_id,
        "name": name,
        "role": role,
        "inputs": inputs,
        "outputs": outputs,
        "evidence": evidence,
        "boundary": boundary,
    }


def build_manifest() -> dict[str, object]:
    require_inputs()
    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    contract = read_json(CONTRACT_JSON)
    readiness = read_json(READINESS_JSON)
    method = read_json(METHOD_PACKET_JSON)
    evidence = pd.read_csv(EVIDENCE_CSV)
    stress = pd.read_csv(STRESS_CSV)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    mechanism = validation["mechanism_evidence"]
    category_summary = contract_category_summary(contract)
    packaged = package["packaged_submissions"]

    role_outputs = {
        role: item["submission_file"]
        for role, item in packaged.items()
        if isinstance(item, dict) and "submission_file" in item
    }

    stress_by_name = {str(row["name"]): row for row in stress.to_dict("records")}
    primary = stress_by_name["route_conserving_objective_bridge_primary"]
    s2 = stress_by_name["s2_listener_bridge_interpretable"]

    stages = [
        stage(
            "og_raw_lifestyle_context",
            "OG Raw Lifestyle Context",
            "Provides train labels, submission key contract, and raw lifelog items.",
            ["data/ch2026_metrics_train.csv", "data/ch2026_submission_sample.csv", "data/ch2025_data_items/*.parquet"],
            ["raw/context feature artifacts used by upstream HS-JEPA modules"],
            [
                f"OG records in contract: {category_summary.get('og_raw', {}).get('records', 0)}",
                f"Required missing: {contract.get('required_missing_count')}",
            ],
            "This stage is competition data, not external/private data.",
        ),
        stage(
            "public_lb_sensor",
            "Public LB Sensor Ledger",
            "Uses public submission observations as a sensor for hidden row-target action response.",
            ["data_analytics/hsjepa_public_score_ledger.csv"],
            ["public-sensitive action anchors", "negative toxicity anchors"],
            [
                f"Ledger rows: {contract.get('public_ledger_summary', {}).get('rows')}",
                f"Pre-public-equation best: {fmt(public['pre_public_equation_best_public_lb'], 10)}",
                f"Current best: {fmt(public['current_best_public_lb'], 10)}",
            ],
            "This is not an OG-only claim; it is the competition-specific sensor path.",
        ),
        stage(
            "human_state_listener_context",
            "Human-State Listener Context",
            "Turns lifestyle/cohort context into target/cell orientation diagnostics.",
            ["OG lifestyle/context artifacts", "s2hub_human_state_distillation_readout.json"],
            ["cell orientation scores", "human_state_probe submission"],
            [
                f"Cell OOF AUC: {fmt(human['cell_oof_auc_human_target_context'], 3)}",
                f"Row OOF AUC: {fmt(human['row_oof_auc'], 3)}",
            ],
            "Human-state is an orientation diagnostic, not a standalone row selector.",
        ),
        stage(
            "route_energy_model",
            "Q/S Route Energy Model",
            "Learns a target-route manifold from train labels and scores whether an action breaks it.",
            ["train Q/S labels", "candidate corrected prediction vectors"],
            ["route energy", "route-conservation veto"],
            [
                f"Primary route z-score: {fmt(mechanism['primary_route_z'], 2)}",
                f"S2 route z-score: {fmt(mechanism['s2_route_z'], 2)}",
            ],
            "Route energy proves candidate-pool structure, not private leaderboard safety.",
        ),
        stage(
            "driver_action_field",
            "Public-Sensitive Driver Action Field",
            "Selects sparse row-target cells that public sensor evidence says are worth moving.",
            ["public action anchors", "current best prediction"],
            ["driver candidate pool"],
            [
                f"Score breakthrough delta: {fmt(public['current_delta_vs_pre_breakthrough'], 10)}",
                f"Evidence roles: {', '.join(evidence['role'].astype(str))}",
            ],
            "This stage is deliberately separated from the OG human-state representation claim.",
        ),
        stage(
            "route_conserving_s2_bridge_decoder",
            "Route-Conserving S2 Bridge Decoder",
            "Pairs driver cells with same-row bridge cells that lower route energy and repeatedly use S2 as listener/hub.",
            ["driver candidate pool", "route energy", "S2 listener score"],
            ["sparse row-target correction field"],
            [
                f"Primary route delta vs null: {fmt(primary['mean_route_energy_delta'], 5)} vs {fmt(primary['null_mean_route_energy_delta'], 5)}",
                f"S2 usage vs null: {fmt(s2['s2_any_rate'], 3)} vs {fmt(s2['null_s2_any_rate'], 3)}",
            ],
            "S2 is a decoder listener/hub in this action space, not a universal sleep physiology claim.",
        ),
        stage(
            "submission_packager",
            "Role-Based Submission Packager",
            "Packages three role-based outputs without requiring historical version names.",
            ["sparse correction field", "submission sample key contract"],
            list(role_outputs.values()),
            [
                f"Upload-safe roles: {', '.join(sorted(validation['upload_results']))}",
                f"Validation passed: {validation['passed']}",
            ],
            "Upload safety is a format guarantee, not a score guarantee.",
        ),
        stage(
            "claim_readiness_and_paper_packet",
            "Claim Readiness and Paper Packet",
            "Converts the runnable package into paper/team-facing evidence and method text.",
            ["package outputs", "stress audit", "reproducibility contract"],
            ["hsjepa_architecture_readiness_report.md", "hsjepa_paper_method_packet_ko.md"],
            [
                f"Readiness status: {readiness['status']}",
                f"Readiness gates: {readiness['passed_gates']}/{readiness['total_gates']}",
                f"Method title: {method['title']}",
            ],
            "Paper claims must keep representation, public sensor, and action decoder separated.",
        ),
    ]

    edges = [
        ["og_raw_lifestyle_context", "human_state_listener_context"],
        ["og_raw_lifestyle_context", "route_energy_model"],
        ["public_lb_sensor", "driver_action_field"],
        ["human_state_listener_context", "driver_action_field"],
        ["route_energy_model", "route_conserving_s2_bridge_decoder"],
        ["driver_action_field", "route_conserving_s2_bridge_decoder"],
        ["route_conserving_s2_bridge_decoder", "submission_packager"],
        ["submission_packager", "claim_readiness_and_paper_packet"],
        ["route_conserving_s2_bridge_decoder", "claim_readiness_and_paper_packet"],
    ]

    manifest = {
        "package": "Route-Conserving S2 Bridge HS-JEPA",
        "status": "pipeline_ready_with_boundary",
        "one_command": "python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py",
        "stage_count": len(stages),
        "edge_count": len(edges),
        "stages": stages,
        "edges": edges,
        "role_outputs": role_outputs,
        "boundary": {
            "is_pure_og_only_model": contract["boundary"]["is_pure_og_only_model"],
            "uses_public_lb_sensor": contract["boundary"]["uses_public_lb_sensor"],
            "human_state_role": contract["boundary"]["human_state_role"],
            "competition_decoder_role": contract["boundary"]["competition_decoder_role"],
        },
        "score_and_mechanism_summary": {
            "current_best_public_lb": public["current_best_public_lb"],
            "current_delta_vs_pre_public_equation": public["current_delta_vs_pre_breakthrough"],
            "primary_route_delta": primary["mean_route_energy_delta"],
            "primary_null_route_delta": primary["null_mean_route_energy_delta"],
            "s2_usage": s2["s2_any_rate"],
            "s2_null_usage": s2["null_s2_any_rate"],
            "human_state_cell_auc": human["cell_oof_auc_human_target_context"],
            "human_state_row_auc": human["row_oof_auc"],
        },
    }
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    MANIFEST_MD.write_text(build_markdown(manifest), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False))
    return manifest


def build_markdown(manifest: dict[str, object]) -> str:
    stage_rows = ["| Stage | Role | Key Evidence | Boundary |", "| --- | --- | --- | --- |"]
    for item in manifest["stages"]:
        evidence = "<br>".join(str(x) for x in item["evidence"])
        stage_rows.append(f"| `{item['id']}` | {item['role']} | {evidence} | {item['boundary']} |")

    role_rows = ["| Role | Output file |", "| --- | --- |"]
    for role, output in sorted(manifest["role_outputs"].items()):
        role_rows.append(f"| `{role}` | `{output}` |")

    return "\n".join(
        [
            "# HS-JEPA Pipeline Manifest",
            "",
            "이 문서는 팀원이 OG 데이터에서 최종 제출/논문 산출물까지 어떤 경로로 이어지는지 한눈에 추적하도록 만든 역할 기반 pipeline manifest다.",
            "",
            "## One-Command Entry",
            "",
            "```bash",
            manifest["one_command"],
            "```",
            "",
            "## Pipeline Diagram",
            "",
            "```mermaid",
            "flowchart TD",
            '    A["OG raw lifestyle context"] --> C["Human-state listener context"]',
            '    A --> D["Q/S route energy model"]',
            '    B["Public LB sensor ledger"] --> E["Public-sensitive driver action field"]',
            '    C --> E',
            '    D --> F["Route-conserving S2 bridge decoder"]',
            '    E --> F',
            '    F --> G["Role-based submission packager"]',
            '    G --> H["Claim readiness and paper packet"]',
            '    F --> H',
            "```",
            "",
            "## Stage Table",
            "",
            *stage_rows,
            "",
            "## Role-Based Outputs",
            "",
            *role_rows,
            "",
            "## Boundary",
            "",
            f"- Pure OG-only model: `{manifest['boundary']['is_pure_og_only_model']}`",
            f"- Uses public LB sensor: `{manifest['boundary']['uses_public_lb_sensor']}`",
            f"- Human-state role: `{manifest['boundary']['human_state_role']}`",
            f"- Competition decoder role: `{manifest['boundary']['competition_decoder_role']}`",
            "",
            "## Summary",
            "",
            "```text",
            "The reusable mechanism is the route-conserving S2 bridge decoder.",
            "The competition-specific sensor supplies sparse driver actions.",
            "The OG human-state representation supplies orientation diagnostics.",
            "The paper claim is valid only when these roles are kept separate.",
            "```",
            "",
        ]
    )


def main() -> None:
    build_manifest()


if __name__ == "__main__":
    main()
