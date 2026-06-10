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
MECHANISM_ABLATION_JSON = OUT / "hsjepa_mechanism_ablation_report.json"
GENERALITY_JSON = OUT / "hsjepa_generality_report.json"
METHOD_PACKET_JSON = OUT / "hsjepa_paper_method_packet.json"
CORE_MANIFEST_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_manifest.json"
CORE_ABLATION_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_ablation_contract.json"
ADAPTER_REPORT_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "sleep_competition_adapter_report.json"
BIG_BET_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "hsjepa_big_bet_queue.json"
OG_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "og_only_assignment_teacher_probe.json"
CONTRASTIVE_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "listener_invariant_contrastive_probe.json"
PRIVATE_TOXICITY_PROBE_JSON = ROOT / "sleep_competition_adapter" / "outputs" / "private_safe_toxicity_probe.json"

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
    required = [
        PACKAGE_JSON,
        EVIDENCE_CSV,
        STRESS_CSV,
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
        OG_PROBE_JSON,
        CONTRASTIVE_PROBE_JSON,
        PRIVATE_TOXICITY_PROBE_JSON,
    ]
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
    ablation = read_json(MECHANISM_ABLATION_JSON)
    generality = read_json(GENERALITY_JSON)
    method = read_json(METHOD_PACKET_JSON)
    core = read_json(CORE_MANIFEST_JSON)
    core_ablation = read_json(CORE_ABLATION_JSON)
    adapter = read_json(ADAPTER_REPORT_JSON)
    big_bets = read_json(BIG_BET_JSON)
    og_probe = read_json(OG_PROBE_JSON)
    contrastive_probe = read_json(CONTRASTIVE_PROBE_JSON)
    private_toxicity_probe = read_json(PRIVATE_TOXICITY_PROBE_JSON)
    evidence = pd.read_csv(EVIDENCE_CSV)
    stress = pd.read_csv(STRESS_CSV)

    public = readiness["public_breakthrough"]
    human = readiness["human_state"]
    mechanism = validation["mechanism_evidence"]
    og_verdict = og_probe["verdict"]
    contrastive_verdict = contrastive_probe["verdict"]
    toxicity_verdict = private_toxicity_probe["verdict"]
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
            "hsjepa_core_architecture",
            "HS-JEPA Core Architecture",
            "Defines the reusable human-understanding mechanism before any sleep-competition target names are introduced.",
            ["partial human context", "generic listener/outcome set", "domain invariant interface"],
            ["hsjepa_core_manifest_ko.md", "hsjepa_core_ablation_contract_ko.md"],
            [
                f"Core status: {core['status']}",
                f"Core gates: {core['passed_gates']}/{core['total_gates']}",
                f"Ablation status: {core_ablation['status']}",
            ],
            "The core must not depend on S2, public LB sensors, submission files, or manual row ids.",
        ),
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
            "og_only_assignment_probe",
            "OG-only Assignment Teacher Probe",
            "Tests whether human-state geometry can replace the public-sensor row-target assignment teacher.",
            ["s2hub_jackpot_cell_student_frame.csv", "stagebridge_jackpot_cell_student_frame.csv"],
            ["og_only_assignment_teacher_probe_ko.md", "og_only_assignment_teacher_ranked_cells.csv"],
            [
                f"Probe status: {og_verdict['status']}",
                f"Pure OG row-cap2 recall: {fmt(og_verdict['pure_og_row_cap2_mean_recall'], 4)}",
                f"Distilled row-cap2 recall: {fmt(og_verdict['distilled_row_cap2_mean_recall'], 4)}",
            ],
            "The probe currently measures the gap; it does not prove pure OG-only deployment.",
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
            "listener_invariant_contrastive_probe",
            "Listener-Invariant Contrastive Probe",
            "Tests whether listener responsibility and route-invariant action health select the same bundles.",
            ["listener_responsibility_ranked_cells.csv", "stagebridge/s2hub candidate bundles"],
            ["listener_invariant_contrastive_probe_ko.md", "listener_invariant_contrastive_scored_bundles.csv"],
            [
                f"Probe status: {contrastive_verdict['status']}",
                f"Listener-route rho: {fmt(contrastive_verdict['mean_listener_route_spearman'], 4)}",
                f"Contrastive overlap: {fmt(contrastive_verdict['mean_contrastive_overlap_rate'], 4)}",
            ],
            "This stage is a diagnostic; it does not create a new submission.",
        ),
        stage(
            "private_safe_toxicity_probe",
            "Private-Safe Toxicity Probe",
            "Tests whether toxicity head generalizes across bad public anchors and selects safer cells than matched nulls.",
            ["toxicity_candidate_cell_table.csv", "toxicity_action_audit.csv", "toxicity_anchor_ledger.csv"],
            ["private_safe_toxicity_probe_ko.md", "private_safe_toxicity_loo_anchor_metrics.csv"],
            [
                f"Probe status: {toxicity_verdict['status']}",
                f"Mean LOO bad-anchor AUC: {fmt(toxicity_verdict['mean_loo_bad_anchor_auc'], 4)}",
                f"Worst LOO bad-anchor AUC: {fmt(toxicity_verdict['worst_loo_bad_anchor_auc'], 4)}",
                f"Safety z vs matched null: {fmt(toxicity_verdict['selected_safety_z_vs_matched_null'], 4)}",
            ],
            "This stage supports toxicity diagnostics, not a private-LB safety guarantee.",
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
            "mechanism_ablation_knockout",
            "Mechanism Ablation Knockout",
            "Records which alternative worldviews public sensors and local stress audits killed or preserved.",
            ["public score ledger", "route-conserving stress audit", "architecture readiness report"],
            ["hsjepa_mechanism_ablation_report_ko.md"],
            [
                f"Public worldviews killed: {ablation['public_worldviews_killed']}",
                f"Public worldviews survived: {ablation['public_worldviews_survived']}",
                f"Ablation status: {ablation['status']}",
            ],
            "This explains mechanism evidence; it is not a new private-score guarantee.",
        ),
        stage(
            "general_architecture_boundary",
            "General Architecture Boundary",
            "Separates reusable HS-JEPA modules from the sleep-competition S2/public-sensor instantiation.",
            ["architecture readiness report", "mechanism ablation report"],
            ["hsjepa_generality_report_ko.md"],
            [
                f"Generality status: {generality['status']}",
                f"Portability checks: {generality['passed_checks']}/{generality['total_checks']}",
                f"Nonblocking boundaries: {', '.join(generality['nonblocking_boundaries'])}",
            ],
            "The current strongest case study still uses a public-sensor assignment teacher.",
        ),
        stage(
            "sleep_competition_adapter",
            "Sleep Competition Adapter",
            "Maps HS-JEPA Core into Q/S listeners, route energy, public-sensor action evidence, and upload-safe sparse row-target outputs.",
            ["HS-JEPA core manifest", "OG data", "public sensor ledger", "route-conserving package"],
            ["sleep_competition_adapter_report_ko.md", "hsjepa_big_bet_queue_ko.md"],
            [
                f"Adapter status: {adapter['status']}",
                f"Adapter score delta: {fmt(adapter['score_evidence']['delta'], 10)}",
                f"Big-bet count: {big_bets['count']}",
            ],
            "This adapter is a competition case study; it is not the general HS-JEPA architecture.",
        ),
        stage(
            "claim_readiness_and_paper_packet",
            "Claim Readiness and Paper Packet",
            "Converts the runnable package into paper/team-facing evidence and method text.",
            ["core manifest", "sleep adapter report", "package outputs", "stress audit", "reproducibility contract", "mechanism ablation report", "generality report"],
            [
                "hsjepa_core_manifest_ko.md",
                "sleep_competition_adapter_report_ko.md",
                "hsjepa_architecture_readiness_report.md",
                "hsjepa_paper_method_packet_ko.md",
                "hsjepa_mechanism_ablation_report_ko.md",
                "hsjepa_generality_report_ko.md",
            ],
            [
                f"Readiness status: {readiness['status']}",
                f"Readiness gates: {readiness['passed_gates']}/{readiness['total_gates']}",
                f"Method title: {method['title']}",
            ],
            "Paper claims must keep representation, public sensor, and action decoder separated.",
        ),
    ]

    edges = [
        ["hsjepa_core_architecture", "og_raw_lifestyle_context"],
        ["hsjepa_core_architecture", "human_state_listener_context"],
        ["hsjepa_core_architecture", "route_energy_model"],
        ["og_raw_lifestyle_context", "human_state_listener_context"],
        ["og_raw_lifestyle_context", "route_energy_model"],
        ["human_state_listener_context", "og_only_assignment_probe"],
        ["og_only_assignment_probe", "general_architecture_boundary"],
        ["public_lb_sensor", "driver_action_field"],
        ["human_state_listener_context", "driver_action_field"],
        ["route_energy_model", "route_conserving_s2_bridge_decoder"],
        ["human_state_listener_context", "listener_invariant_contrastive_probe"],
        ["route_energy_model", "listener_invariant_contrastive_probe"],
        ["listener_invariant_contrastive_probe", "sleep_competition_adapter"],
        ["public_lb_sensor", "private_safe_toxicity_probe"],
        ["driver_action_field", "private_safe_toxicity_probe"],
        ["private_safe_toxicity_probe", "sleep_competition_adapter"],
        ["driver_action_field", "route_conserving_s2_bridge_decoder"],
        ["route_conserving_s2_bridge_decoder", "submission_packager"],
        ["hsjepa_core_architecture", "sleep_competition_adapter"],
        ["submission_packager", "sleep_competition_adapter"],
        ["public_lb_sensor", "sleep_competition_adapter"],
        ["public_lb_sensor", "mechanism_ablation_knockout"],
        ["route_conserving_s2_bridge_decoder", "mechanism_ablation_knockout"],
        ["mechanism_ablation_knockout", "claim_readiness_and_paper_packet"],
        ["mechanism_ablation_knockout", "general_architecture_boundary"],
        ["general_architecture_boundary", "claim_readiness_and_paper_packet"],
        ["sleep_competition_adapter", "claim_readiness_and_paper_packet"],
        ["hsjepa_core_architecture", "claim_readiness_and_paper_packet"],
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
            "public_worldviews_killed": ablation["public_worldviews_killed"],
            "public_worldviews_survived": ablation["public_worldviews_survived"],
            "generality_status": generality["status"],
            "generality_nonblocking_boundaries": generality["nonblocking_boundaries"],
            "core_status": core["status"],
            "adapter_status": adapter["status"],
            "big_bet_count": big_bets["count"],
            "og_only_assignment_probe_status": og_verdict["status"],
            "listener_invariant_contrastive_probe_status": contrastive_verdict["status"],
            "private_safe_toxicity_probe_status": toxicity_verdict["status"],
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
            '    CORE["HS-JEPA core architecture"] --> A["OG raw lifestyle context"]',
            '    CORE --> C["Human-state listener context"]',
            '    CORE --> D["Q/S route energy model"]',
            '    A["OG raw lifestyle context"] --> C["Human-state listener context"]',
            '    A --> D["Q/S route energy model"]',
            '    C --> P1["OG-only assignment probe"]',
            '    P1 --> GEN["General architecture boundary"]',
            '    B["Public LB sensor ledger"] --> E["Public-sensitive driver action field"]',
            '    C --> E',
            '    D --> F["Route-conserving S2 bridge decoder"]',
            '    C --> P2["Listener-invariant contrastive probe"]',
            '    D --> P2',
            '    B --> P3["Private-safe toxicity probe"]',
            '    E --> P3',
            '    E --> F',
            '    F --> G["Role-based submission packager"]',
            '    G --> ADAPT["Sleep competition adapter"]',
            '    CORE --> ADAPT',
            '    B --> ADAPT',
            '    P2 --> ADAPT',
            '    P3 --> ADAPT',
            '    GEN --> H["Claim readiness and paper packet"]',
            '    ADAPT --> H["Claim readiness and paper packet"]',
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
            "The reusable mechanism is HS-JEPA Core: hidden state -> listener -> action-health -> invariant decoder.",
            "The sleep competition adapter supplies Q/S listeners, public-sensor actions, route energy, and upload format.",
            "The current LB breakthrough is adapter evidence; the paper claim must remain core-first.",
            "The next jackpot is replacing public-sensor assignment with an OG-only human-state teacher.",
            "```",
            "",
        ]
    )


def main() -> None:
    build_manifest()


if __name__ == "__main__":
    main()
