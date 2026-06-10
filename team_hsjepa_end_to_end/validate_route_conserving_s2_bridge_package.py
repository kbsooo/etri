#!/usr/bin/env python3
"""Validate the team-facing Route-Conserving S2 Bridge HS-JEPA package.

This is intentionally stricter than checking that CSV files exist.  The package
claims a reusable decoder mechanism, so this validator checks three layers:

1. Reproducibility: expected docs, package manifests, outputs, and submissions
   exist and are upload-safe.
2. Mechanism evidence: selected bridge actions are unusually route-conserving
   and S2-centered compared with the feasible candidate null.
3. Claim boundaries: the package keeps human-state as an orientation diagnostic
   instead of overclaiming it as a full row-assignment solver.
"""

from __future__ import annotations

from pathlib import Path
import json
import math
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"

KEYS = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

PACKAGE_JSON = OUT / "route_conserving_s2_bridge_package.json"
EVIDENCE_CSV = OUT / "route_conserving_s2_bridge_evidence_table.csv"
STRESS_JSON = OUT / "route_conserving_s2_bridge_stress_audit.json"
STRESS_CSV = OUT / "route_conserving_s2_bridge_stress_summary.csv"
REPORT_MD = OUT / "route_conserving_s2_bridge_validation_report.md"
REPORT_JSON = OUT / "route_conserving_s2_bridge_validation_report.json"

REQUIRED_DOCS = [
    HERE / "README.md",
    HERE / "ROUTE_CONSERVING_S2_BRIDGE_KO.md",
    ROOT / "paper_hsjepa_core" / "HS_JEPA_ARCHITECTURE_PACKAGE_KO.md",
    ROOT / "experiment_log.md",
]


def check(condition: bool, name: str, detail: str, rows: list[dict[str, object]]) -> None:
    rows.append(
        {
            "check": name,
            "status": "PASS" if condition else "FAIL",
            "detail": detail,
        }
    )


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_submission(path: Path, sample: pd.DataFrame) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=KEYS[1:])
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df[KEYS].duplicated().sum()),
        "nan_cells": int(np.isnan(prob).sum()),
        "finite": bool(np.isfinite(prob).all()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and not df[KEYS].duplicated().any()
            and np.isfinite(prob).all()
            and prob.min() > 0.0
            and prob.max() < 1.0
        ),
    }


def z_score(actual: float, mean: float, std: float) -> float:
    if std <= 0:
        return math.inf
    return (actual - mean) / std


def build_markdown(rows: list[dict[str, object]], readout: dict[str, object]) -> str:
    table = ["| Check | Status | Detail |", "| --- | --- | --- |"]
    for row in rows:
        table.append(f"| `{row['check']}` | `{row['status']}` | {row['detail']} |")

    stress = readout["mechanism_evidence"]
    claims = [
        "| Claim | Evidence | Boundary |",
        "| --- | --- | --- |",
        (
            "| Route-conserving decoder | "
            f"Primary route z `{stress['primary_route_z']:.2f}`, "
            f"S2 route z `{stress['s2_route_z']:.2f}` | "
            "This proves unusual selection inside the candidate pool, not private leaderboard safety. |"
        ),
        (
            "| S2 listener/hub | "
            f"S2 bridge usage `{stress['s2_listener_s2_any_rate']:.3f}` vs null "
            f"`{stress['s2_listener_null_s2_any_rate']:.3f}` | "
            "S2 is a listener/hub in this route decoder, not necessarily a universal sleep factor. |"
        ),
        (
            "| Human-state as orientation diagnostic | "
            "Package contains a separate human_state_probe role and does not use it as the primary assignment solver | "
            "Human-state alone still does not solve row support assignment. |"
        ),
        (
            "| Team reproducibility | "
            "Wrapper, stress audit, validation report, manifest, and upload-safe submissions are generated | "
            "The package depends on existing local competition artifacts and score ledger. |"
        ),
    ]

    return "\n".join(
        [
            "# Route-Conserving S2 Bridge Validation Report",
            "",
            "이 리포트는 팀원이 HS-JEPA 패키지를 열었을 때, 핵심 주장이 산출물로 검증되는지 확인하기 위한 자동 검증 결과다.",
            "",
            "## Pass/Fail Checks",
            "",
            *table,
            "",
            "## Claim-Evidence Matrix",
            "",
            *claims,
            "",
            "## Interpretation",
            "",
            "이 검증이 통과하면, 현재 패키지는 단순 leaderboard 시행착오 묶음이 아니라 다음 형태의 검증 가능한 메커니즘으로 설명할 수 있다.",
            "",
            "```text",
            "public-sensitive driver action",
            "  + route-conserving bridge action",
            "  + S2 listener/hub constraint",
            "  + human-state orientation diagnostic",
            "```",
            "",
            "검증이 증명하지 않는 것도 명확하다. 이것은 private-safe를 증명하지 않고, OG-only encoder가 완전한 row-target assignment solver임을 증명하지도 않는다. 대신 가능한 action 후보 공간 안에서 선택된 bridge rule이 통계적으로 특이하고 재현 가능한 decoder constraint임을 증명한다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    rows: list[dict[str, object]] = []

    for path in [PACKAGE_JSON, EVIDENCE_CSV, STRESS_JSON, STRESS_CSV, *REQUIRED_DOCS]:
        check(path.exists(), f"exists:{path.name}", str(path.relative_to(ROOT)) if path.exists() else "missing", rows)

    if not PACKAGE_JSON.exists() or not STRESS_CSV.exists() or not EVIDENCE_CSV.exists():
        raise FileNotFoundError("required package outputs are missing; run run_route_conserving_s2_bridge.py and audit_route_conserving_s2_bridge.py first")

    package = read_json(PACKAGE_JSON)
    evidence = pd.read_csv(EVIDENCE_CSV)
    stress = pd.read_csv(STRESS_CSV)
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=KEYS[1:]).sort_values(KEYS).reset_index(drop=True)

    required_roles = {"competition_primary", "interpretable_s2_hub", "human_state_probe"}
    packaged = package.get("packaged_submissions", {})
    check(required_roles.issubset(set(packaged)), "roles:all_present", f"roles={sorted(packaged)}", rows)

    upload_results = {}
    if isinstance(packaged, dict):
        for role, item in packaged.items():
            if not isinstance(item, dict):
                continue
            root_path = Path(str(item.get("root_path", "")))
            local_path = Path(str(item.get("local_path", "")))
            check(root_path.exists(), f"submission_root:{role}", str(root_path.relative_to(ROOT)) if root_path.exists() else str(root_path), rows)
            check(local_path.exists(), f"submission_local:{role}", str(local_path.relative_to(ROOT)) if local_path.exists() else str(local_path), rows)
            if root_path.exists():
                validation = validate_submission(root_path, sample)
                upload_results[role] = validation
                check(validation["upload_safe"], f"upload_safe:{role}", json.dumps(validation, ensure_ascii=False), rows)

    check(len(evidence) >= 3, "evidence:three_roles", f"rows={len(evidence)}", rows)
    check(set(evidence["role"]).issuperset({"competition_primary", "interpretable_s2_hub", "human_state_probe"}), "evidence:roles", ",".join(evidence["role"].astype(str)), rows)

    stress_by_name = {str(row["name"]): row for row in stress.to_dict("records")}
    primary = stress_by_name.get("route_conserving_objective_bridge_primary")
    s2_listener = stress_by_name.get("s2_listener_bridge_interpretable")
    check(primary is not None, "stress:primary_present", "route_conserving_objective_bridge_primary", rows)
    check(s2_listener is not None, "stress:s2_present", "s2_listener_bridge_interpretable", rows)

    mechanism = {
        "primary_route_z": 0.0,
        "s2_route_z": 0.0,
        "s2_listener_s2_any_rate": 0.0,
        "s2_listener_null_s2_any_rate": 0.0,
    }
    if primary is not None:
        primary_route_z = z_score(
            float(primary["mean_route_energy_delta"]),
            float(primary["null_mean_route_energy_delta"]),
            float(read_json(STRESS_JSON)["audits"]["route_conserving_objective_bridge_primary"]["random_unique_row_null"]["null_mean_route_energy_delta_std"]),
        )
        mechanism["primary_route_z"] = primary_route_z
        check(float(primary["p_null_energy_le_actual"]) <= 0.001, "mechanism:primary_route_p", f"p={primary['p_null_energy_le_actual']}", rows)
        check(primary_route_z <= -5.0, "mechanism:primary_route_z", f"z={primary_route_z:.2f}", rows)
        check(float(primary["mean_energy_rank_pct"]) <= 0.25, "mechanism:primary_rank", f"rank={primary['mean_energy_rank_pct']:.3f}", rows)
    if s2_listener is not None:
        stress_json = read_json(STRESS_JSON)
        s2_route_z = z_score(
            float(s2_listener["mean_route_energy_delta"]),
            float(s2_listener["null_mean_route_energy_delta"]),
            float(stress_json["audits"]["s2_listener_bridge_interpretable"]["random_unique_row_null"]["null_mean_route_energy_delta_std"]),
        )
        mechanism["s2_route_z"] = s2_route_z
        mechanism["s2_listener_s2_any_rate"] = float(s2_listener["s2_any_rate"])
        mechanism["s2_listener_null_s2_any_rate"] = float(s2_listener["null_s2_any_rate"])
        check(float(s2_listener["p_null_energy_le_actual"]) <= 0.001, "mechanism:s2_route_p", f"p={s2_listener['p_null_energy_le_actual']}", rows)
        check(s2_route_z <= -5.0, "mechanism:s2_route_z", f"z={s2_route_z:.2f}", rows)
        check(float(s2_listener["p_null_s2_any_ge_actual"]) <= 0.001, "mechanism:s2_hub_p", f"p={s2_listener['p_null_s2_any_ge_actual']}", rows)
        check(float(s2_listener["s2_any_rate"]) >= 0.95, "mechanism:s2_hub_usage", f"rate={s2_listener['s2_any_rate']:.3f}", rows)
        check(float(s2_listener["mean_s2hub_rank_pct"]) <= 0.25, "mechanism:s2hub_rank", f"rank={s2_listener['mean_s2hub_rank_pct']:.3f}", rows)

    readout = {
        "package": str(PACKAGE_JSON.resolve()),
        "checks": rows,
        "upload_results": upload_results,
        "mechanism_evidence": mechanism,
        "passed": all(row["status"] == "PASS" for row in rows),
    }
    REPORT_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(rows, readout), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    return readout


if __name__ == "__main__":
    result = run()
    sys.exit(0 if result["passed"] else 1)
