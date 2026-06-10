#!/usr/bin/env python3
"""Build a paper/team readiness report for the HS-JEPA package.

The ordinary validator checks whether the generated artifacts are present and
upload-safe.  This report answers a different question:

    Can we present the current HS-JEPA package as a reusable architecture
    rather than as a list of leaderboard tweaks?

The report intentionally separates score evidence, mechanism evidence,
human-state evidence, reproducibility, and claim boundaries.
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
STRESS_CSV = OUT / "route_conserving_s2_bridge_stress_summary.csv"
VALIDATION_JSON = OUT / "route_conserving_s2_bridge_validation_report.json"
CONTRACT_JSON = OUT / "hsjepa_reproducibility_contract.json"
LEDGER_CSV = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"

REPORT_JSON = OUT / "hsjepa_architecture_readiness_report.json"
REPORT_MD = OUT / "hsjepa_architecture_readiness_report.md"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def maybe_read_json(path: str | Path | None) -> dict[str, object]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    return read_json(p)


def gate(name: str, passed: bool, evidence: str, boundary: str) -> dict[str, object]:
    return {
        "gate": name,
        "status": "PASS" if passed else "WARN",
        "passed": bool(passed),
        "evidence": evidence,
        "boundary": boundary,
    }


def fmt(x: float, digits: int = 6) -> str:
    if x is None or not math.isfinite(float(x)):
        return "n/a"
    return f"{float(x):.{digits}f}"


def json_safe(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


def public_breakthrough_readout(ledger: pd.DataFrame) -> dict[str, object]:
    ledger = ledger.sort_values("sequence").reset_index(drop=True)
    breakthrough_rows = ledger[ledger["observed_stage"].astype(str).eq("H012")]
    if breakthrough_rows.empty:
        pre_breakthrough_best = float(ledger["public_lb"].min())
        breakthrough_lb = math.nan
        breakthrough_file = ""
    else:
        breakthrough = breakthrough_rows.iloc[0]
        pre_breakthrough = ledger[ledger["sequence"] < int(breakthrough["sequence"])]
        pre_breakthrough_best = float(pre_breakthrough["public_lb"].min())
        breakthrough_lb = float(breakthrough["public_lb"])
        breakthrough_file = str(breakthrough["file"])

    current_best_row = ledger.loc[ledger["public_lb"].idxmin()]
    current_best = float(current_best_row["public_lb"])
    return {
        "ledger_rows": int(len(ledger)),
        "pre_public_equation_best_public_lb": pre_breakthrough_best,
        "public_equation_breakthrough_public_lb": breakthrough_lb,
        "public_equation_breakthrough_file": breakthrough_file,
        "current_best_public_lb": current_best,
        "current_best_file": str(current_best_row["file"]),
        "current_best_role_name": "row_state_decoder_best",
        "public_equation_delta_vs_pre_breakthrough": (
            float(breakthrough_lb - pre_breakthrough_best) if math.isfinite(breakthrough_lb) else math.nan
        ),
        "current_delta_vs_pre_breakthrough": float(current_best - pre_breakthrough_best),
    }


def human_state_readout(package: dict[str, object]) -> dict[str, object]:
    source = package.get("source_readouts", {})
    if not isinstance(source, dict):
        return {}
    distill = maybe_read_json(source.get("s2_distillation"))
    outputs = distill.get("outputs", {}) if isinstance(distill, dict) else {}
    candidate = outputs.get("s2hub_jackpot", {}) if isinstance(outputs, dict) else {}
    cell_oof = candidate.get("cell_oof", {}) if isinstance(candidate, dict) else {}
    row_oof = candidate.get("row_oof", {}) if isinstance(candidate, dict) else {}
    human_target = cell_oof.get("human_target_context", {}) if isinstance(cell_oof, dict) else {}
    human_row = cell_oof.get("human_row_context_only", {}) if isinstance(cell_oof, dict) else {}
    return {
        "cell_oof_auc_human_target_context": float(human_target.get("subject_group_oof_auc", math.nan)),
        "cell_oof_ap_human_target_context": float(human_target.get("subject_group_oof_ap", math.nan)),
        "cell_oof_auc_human_row_context_only": float(human_row.get("subject_group_oof_auc", math.nan)),
        "row_oof_auc": float(row_oof.get("subject_group_oof_auc", math.nan)),
        "row_oof_ap": float(row_oof.get("subject_group_oof_ap", math.nan)),
        "teacher_changed_cells": int(candidate.get("teacher_changed_cells", 0)) if isinstance(candidate, dict) else 0,
        "teacher_changed_rows": int(candidate.get("teacher_changed_rows", 0)) if isinstance(candidate, dict) else 0,
    }


def build_report() -> dict[str, object]:
    missing = [
        str(path.relative_to(ROOT))
        for path in [PACKAGE_JSON, STRESS_CSV, VALIDATION_JSON, CONTRACT_JSON, LEDGER_CSV]
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing required readiness inputs: {missing}")

    package = read_json(PACKAGE_JSON)
    validation = read_json(VALIDATION_JSON)
    contract = read_json(CONTRACT_JSON)
    stress = pd.read_csv(STRESS_CSV)
    ledger = pd.read_csv(LEDGER_CSV)

    public_readout = public_breakthrough_readout(ledger)
    human_readout = human_state_readout(package)
    stress_by_name = {str(row["name"]): row for row in stress.to_dict("records")}
    primary = stress_by_name.get("route_conserving_objective_bridge_primary", {})
    s2 = stress_by_name.get("s2_listener_bridge_interpretable", {})
    boundary = contract.get("boundary", {})

    upload_results = validation.get("upload_results", {})
    upload_safe_all = bool(upload_results) and all(
        bool(item.get("upload_safe", False))
        for item in upload_results.values()
        if isinstance(item, dict)
    )

    gates = [
        gate(
            "score_breakthrough",
            public_readout["current_delta_vs_pre_breakthrough"] <= -0.005,
            (
                f"pre-public-equation baseline {fmt(public_readout['pre_public_equation_best_public_lb'], 10)} "
                f"-> current best {fmt(public_readout['current_best_public_lb'], 10)} "
                f"(delta {fmt(public_readout['current_delta_vs_pre_breakthrough'], 10)})"
            ),
            "This proves a competition-relevant public signal, not private leaderboard safety.",
        ),
        gate(
            "route_conserving_mechanism",
            bool(primary) and float(primary["p_null_energy_le_actual"]) <= 0.001 and float(primary["mean_energy_rank_pct"]) <= 0.25,
            (
                f"selected route delta {fmt(float(primary.get('mean_route_energy_delta', math.nan)), 5)} "
                f"vs null {fmt(float(primary.get('null_mean_route_energy_delta', math.nan)), 5)}, "
                f"rank pct {fmt(float(primary.get('mean_energy_rank_pct', math.nan)), 3)}"
            ),
            "This proves unusual bridge selection inside the candidate pool, not that every future dataset shares the same route.",
        ),
        gate(
            "s2_listener_hub",
            bool(s2) and float(s2["p_null_s2_any_ge_actual"]) <= 0.001 and float(s2["s2_any_rate"]) >= 0.95,
            (
                f"S2 usage {fmt(float(s2.get('s2_any_rate', math.nan)), 3)} "
                f"vs null {fmt(float(s2.get('null_s2_any_rate', math.nan)), 3)}, "
                f"S2-hub rank pct {fmt(float(s2.get('mean_s2hub_rank_pct', math.nan)), 3)}"
            ),
            "S2 is a listener/hub for this decoder, not a universal claim about sleep physiology.",
        ),
        gate(
            "human_state_orientation",
            human_readout.get("cell_oof_auc_human_target_context", 0.0) >= 0.70
            and human_readout.get("row_oof_auc", 1.0) < 0.60,
            (
                f"cell AUC {fmt(human_readout.get('cell_oof_auc_human_target_context', math.nan), 3)}, "
                f"row AUC {fmt(human_readout.get('row_oof_auc', math.nan), 3)}"
            ),
            "Human-state explains target/cell orientation, but it is not a complete row-assignment solver.",
        ),
        gate(
            "reproducibility_contract",
            bool(contract.get("passed")) and int(contract.get("required_missing_count", 1)) == 0,
            (
                f"required missing {contract.get('required_missing_count')}, "
                f"public ledger rows {contract.get('public_ledger_summary', {}).get('rows')}, "
                f"raw/source records {len(contract.get('records', []))}"
            ),
            "The team runner is reproducible from local artifacts, but it explicitly uses a public-LB sensor.",
        ),
        gate(
            "upload_safe_team_outputs",
            upload_safe_all and bool(validation.get("passed")),
            f"validation passed {validation.get('passed')}, upload-safe roles {sorted(upload_results)}",
            "Upload safety is a format/integrity guarantee, not a score guarantee.",
        ),
        gate(
            "claim_boundary_honesty",
            boundary.get("is_pure_og_only_model") is False
            and boundary.get("uses_public_lb_sensor") is True
            and boundary.get("uses_proprietary_embedding_api_in_team_runner") is False,
            (
                f"pure OG-only={boundary.get('is_pure_og_only_model')}, "
                f"public sensor={boundary.get('uses_public_lb_sensor')}, "
                f"proprietary embedding={boundary.get('uses_proprietary_embedding_api_in_team_runner')}"
            ),
            "Paper claims should separate OG human-state representation from the competition-specific action decoder.",
        ),
    ]

    passed = sum(1 for item in gates if item["passed"])
    status = "paper_ready_with_boundary" if passed == len(gates) else "needs_more_evidence"
    report = {
        "package": "Route-Conserving S2 Bridge HS-JEPA",
        "status": status,
        "passed_gates": passed,
        "total_gates": len(gates),
        "gates": gates,
        "public_breakthrough": public_readout,
        "mechanism": {
            "primary": dict(primary),
            "s2_listener": dict(s2),
        },
        "human_state": human_readout,
        "boundary": boundary,
        "interpretation": {
            "knuckleball_mechanism": "public-sensitive driver + route-conserving bridge + S2 listener/hub",
            "strong_claim": "Sparse row-target correction should preserve the learned Q/S route manifold.",
            "do_not_overclaim": [
                "This is not a pure OG-only model.",
                "This does not prove private leaderboard safety.",
                "Human-state is an orientation diagnostic, not a standalone assignment solver.",
            ],
        },
    }
    report = json_safe(report)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False))
    return report


def build_markdown(report: dict[str, object]) -> str:
    public = report["public_breakthrough"]
    human = report["human_state"]
    gates = report["gates"]

    gate_rows = ["| Gate | Status | Evidence | Boundary |", "| --- | --- | --- | --- |"]
    for item in gates:
        gate_rows.append(
            f"| `{item['gate']}` | `{item['status']}` | {item['evidence']} | {item['boundary']} |"
        )

    return "\n".join(
        [
            "# HS-JEPA Architecture Readiness Report",
            "",
            "이 리포트는 현재 HS-JEPA 패키지가 단순 leaderboard 암묵지 묶음이 아니라, 팀 공유/논문 발표용 아키텍처 주장으로 설명 가능한지 자동 판정한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{report['status']}`",
            f"- Gates: `{report['passed_gates']}/{report['total_gates']}` passed",
            "",
            "## Knuckleball Mechanism",
            "",
            "```text",
            "public-sensitive driver action",
            "  + route-conserving bridge action",
            "  + S2 listener/hub constraint",
            "  + human-state orientation diagnostic",
            "```",
            "",
            "축구 비유로 말하면, 이 패키지의 무회전 슛은 특정 제출 파일을 외우는 것이 아니라 다음 제약을 반복 가능하게 적용하는 것이다.",
            "",
            "```text",
            "Sparse row-target correction should preserve the learned Q/S route manifold.",
            "```",
            "",
            "## Gate Results",
            "",
            *gate_rows,
            "",
            "## Score Evidence",
            "",
            f"- Public ledger rows: `{public['ledger_rows']}`",
            f"- Pre-public-equation best public LB: `{fmt(public['pre_public_equation_best_public_lb'], 10)}`",
            f"- Public-equation breakthrough LB: `{fmt(public['public_equation_breakthrough_public_lb'], 10)}`",
            f"- Current best public LB: `{fmt(public['current_best_public_lb'], 10)}`",
            f"- Current best role: `{public['current_best_role_name']}`",
            f"- Current best file: `{public['current_best_file']}`",
            f"- Current delta vs pre-public-equation best: `{fmt(public['current_delta_vs_pre_breakthrough'], 10)}`",
            "",
            "해석: HS-JEPA 계열의 public-equation/row-state 관점은 기존 feature/model frontier 대비 약 `0.0084` Log Loss 단위의 큰 이동을 만들었다. 이것은 0.0001 단위 미세조정이 아니라 데이터 생성 구조를 다르게 본 결과다.",
            "",
            "## Human-State Evidence",
            "",
            f"- Cell-level human-target context OOF AUC: `{fmt(human.get('cell_oof_auc_human_target_context', math.nan), 3)}`",
            f"- Row-level OOF AUC: `{fmt(human.get('row_oof_auc', math.nan), 3)}`",
            f"- Teacher changed cells: `{human.get('teacher_changed_cells')}`",
            f"- Teacher changed rows: `{human.get('teacher_changed_rows')}`",
            "",
            "해석: human-state latent는 어떤 target/cell 방향이 말이 되는지 설명하는 데 강하지만, 어느 row를 움직일지 단독으로 고르는 데는 약하다. 따라서 논문 구조는 `encoder -> listener/orientation`과 `assignment/decoder`를 분리해야 한다.",
            "",
            "## Paper-Safe Claim",
            "",
            "강하게 말할 수 있는 주장:",
            "",
            "```text",
            "HS-JEPA reframes sleep log prediction as latent human-state oriented row-target action decoding. The reusable mechanism is not a larger classifier, but a route-conserving decoder that pairs public-sensitive driver actions with bridge actions on the learned Q/S manifold. S2 emerges as a listener/hub for objective-stage correction, while human-state representations explain action orientation rather than complete row assignment.",
            "```",
            "",
            "말하면 안 되는 과장:",
            "",
            "- pure OG-only 모델이라고 주장하지 않는다.",
            "- private leaderboard safety를 증명했다고 주장하지 않는다.",
            "- S2가 보편적인 수면 생리학 중심 factor라고 주장하지 않는다.",
            "- human-state encoder 하나로 row-target assignment를 해결했다고 주장하지 않는다.",
            "",
            "## Next Big-Bet Direction",
            "",
            "다음 큰 실험은 새 blend가 아니라 이 readiness report에서 아직 competition-specific인 부분을 줄이는 것이다.",
            "",
            "```text",
            "Can the public-sensitive assignment solver be replaced or distilled by an OG-only cohort/personal human-state listener without losing the route-conserving S2 bridge property?",
            "```",
            "",
            "이 질문이 풀리면 HS-JEPA는 대회용 decoder를 넘어 더 일반적인 human-state architecture로 강해진다.",
            "",
        ]
    )


def main() -> None:
    result = build_report()
    sys.exit(0 if result["status"] == "paper_ready_with_boundary" else 1)


if __name__ == "__main__":
    main()
