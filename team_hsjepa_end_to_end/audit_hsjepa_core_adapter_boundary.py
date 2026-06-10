#!/usr/bin/env python3
"""Audit the HS-JEPA core/adapter boundary.

The project now makes two distinct claims:

1. HS-JEPA Core is a reusable human-understanding architecture.
2. The sleep competition adapter is a case-study instantiation that is allowed
   to use Q/S target names, public-LB sensors, and upload-safe submissions.

This audit turns that separation into a reproducible gate.  It intentionally
does not forbid explanatory boundary text in the core docs.  Instead it checks
the operational boundary: imports, manifest fields, runner order, and adapter
dependencies.
"""

from __future__ import annotations

from pathlib import Path
import ast
import json
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_conserving_s2_bridge"
OUT.mkdir(parents=True, exist_ok=True)

CORE_ROOT = ROOT / "hsjepa_core"
ADAPTER_ROOT = ROOT / "sleep_competition_adapter"
TEAM_ROOT = ROOT / "team_hsjepa_end_to_end"

CORE_MANIFEST_JSON = CORE_ROOT / "outputs" / "hsjepa_core_manifest.json"
CORE_ABLATION_JSON = CORE_ROOT / "outputs" / "hsjepa_core_ablation_contract.json"
ADAPTER_REPORT_JSON = ADAPTER_ROOT / "outputs" / "sleep_competition_adapter_report.json"
RUNNER = TEAM_ROOT / "run_full_team_hsjepa_package.py"

AUDIT_JSON = OUT / "hsjepa_core_adapter_boundary_audit.json"
AUDIT_MD = OUT / "hsjepa_core_adapter_boundary_audit_ko.md"

CORE_REQUIRED_MODULES = {
    "context_encoder",
    "masked_state_predictor",
    "listener_responsibility",
    "action_health_decoder",
    "invariant_energy",
    "anti_shortcut_validation",
}

CORE_FORBIDDEN_IMPORT_PREFIXES = {
    "sleep_competition_adapter",
    "team_hsjepa_end_to_end",
    "paper_hsjepa_core",
    "hitl",
    "final_hsjepa_candidates",
    "final_hsjepa_prototypes",
    "data_analytics",
}

CORE_FORBIDDEN_PATH_TOKENS = {
    "ch2026",
    "ch2025_data_items",
    "submission_",
    "public_lb",
    "hsjepa_public_score_ledger",
}

DATASET_TARGET_RE = re.compile(r"\b(?:Q[123]|S[1234])\b")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def py_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def extract_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def extract_string_constants(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)
    return values


def flatten_json(value: Any, path: str = "") -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = [(path, value)]
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            rows.extend(flatten_json(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            child_path = f"{path}[{idx}]"
            rows.extend(flatten_json(child, child_path))
    return rows


def check(name: str, passed: bool, evidence: str, required: bool = True) -> dict[str, Any]:
    return {
        "check": name,
        "status": "PASS" if passed else ("FAIL" if required else "WARN"),
        "passed": bool(passed),
        "required": bool(required),
        "evidence": evidence,
    }


def core_import_audit() -> tuple[bool, list[dict[str, str]]]:
    violations: list[dict[str, str]] = []
    for path in py_files(CORE_ROOT):
        for module in extract_imports(path):
            if any(module == prefix or module.startswith(prefix + ".") for prefix in CORE_FORBIDDEN_IMPORT_PREFIXES):
                violations.append(
                    {
                        "file": str(path.relative_to(ROOT)),
                        "import": module,
                        "reason": "core must not import competition adapter, team package, or historical experiment code",
                    }
                )
    return len(violations) == 0, violations


def core_string_audit() -> tuple[bool, list[dict[str, str]], list[dict[str, str]]]:
    hard_violations: list[dict[str, str]] = []
    boundary_mentions: list[dict[str, str]] = []
    for path in py_files(CORE_ROOT):
        for value in extract_string_constants(path):
            lowered = value.lower()
            matched = sorted(token for token in CORE_FORBIDDEN_PATH_TOKENS if token in lowered)
            if not matched:
                continue
            entry = {
                "file": str(path.relative_to(ROOT)),
                "tokens": ", ".join(matched),
                "text": value[:160].replace("\n", " "),
            }
            if "forbidden" in lowered or "not require" in lowered or "core must not" in lowered:
                boundary_mentions.append(entry)
            else:
                hard_violations.append(entry)
    return len(hard_violations) == 0, hard_violations, boundary_mentions


def core_manifest_audit(core: dict[str, Any], core_ablation: dict[str, Any]) -> tuple[bool, list[dict[str, str]]]:
    violations: list[dict[str, str]] = []
    module_ids = {str(item.get("id")) for item in core.get("modules", []) if isinstance(item, dict)}
    missing_modules = sorted(CORE_REQUIRED_MODULES - module_ids)
    if missing_modules:
        violations.append({"field": "modules", "reason": f"missing core modules: {missing_modules}"})

    forbidden_paths = {"forbidden_core_dependencies", "portability_gates"}
    for path, value in flatten_json(core):
        if any(path.startswith(skip) for skip in forbidden_paths):
            continue
        if isinstance(value, str) and DATASET_TARGET_RE.search(value):
            violations.append({"field": path, "reason": f"dataset target token found: {value[:120]}"})
        if isinstance(value, str) and "public lb" in value.lower():
            violations.append({"field": path, "reason": f"public-LB token found: {value[:120]}"})
        if isinstance(value, str) and "submission" in value.lower():
            violations.append({"field": path, "reason": f"submission token found: {value[:120]}"})

    if core.get("status") != "core_ready_for_adapter":
        violations.append({"field": "status", "reason": f"unexpected core status {core.get('status')}"})
    if core.get("passed_gates") != core.get("total_gates"):
        violations.append(
            {
                "field": "portability_gates",
                "reason": f"passed {core.get('passed_gates')}/{core.get('total_gates')}",
            }
        )
    if core_ablation.get("status") != "ablation_contract_ready":
        violations.append({"field": "core_ablation.status", "reason": str(core_ablation.get("status"))})
    return len(violations) == 0, violations


def adapter_dependency_audit(adapter: dict[str, Any]) -> tuple[bool, list[str]]:
    required_refs = [
        "CORE_MANIFEST_JSON",
        "CORE_ABLATION_JSON",
        "core_status",
        "core_ablation_status",
        "adapter_mapping",
    ]
    report_source = (ADAPTER_ROOT / "build_sleep_competition_adapter_report.py").read_text(encoding="utf-8")
    missing = [ref for ref in required_refs if ref not in report_source and ref not in adapter]
    if adapter.get("core_status") != "core_ready_for_adapter":
        missing.append(f"adapter.core_status={adapter.get('core_status')}")
    if adapter.get("core_ablation_status") != "ablation_contract_ready":
        missing.append(f"adapter.core_ablation_status={adapter.get('core_ablation_status')}")
    if len(adapter.get("adapter_mapping", [])) < len(CORE_REQUIRED_MODULES):
        missing.append(f"adapter_mapping_count={len(adapter.get('adapter_mapping', []))}")
    return len(missing) == 0, missing


def runner_order_audit() -> tuple[bool, dict[str, int | None]]:
    text = RUNNER.read_text(encoding="utf-8")
    needles = {
        "core_manifest": "hsjepa_core\" / \"build_core_architecture_manifest.py",
        "core_reference": "hsjepa_core\" / \"run_core_reference_demo.py",
        "sleep_adapter_report": "sleep_competition_adapter\" / \"build_sleep_competition_adapter_report.py",
        "boundary_audit": "audit_hsjepa_core_adapter_boundary.py",
        "paper_packet": "build_hsjepa_paper_method_packet.py",
        "release_checklist": "build_hsjepa_release_checklist.py",
    }
    positions: dict[str, int | None] = {
        key: (text.find(needle) if text.find(needle) >= 0 else None)
        for key, needle in needles.items()
    }
    required_order = [
        positions["core_manifest"],
        positions["core_reference"],
        positions["sleep_adapter_report"],
        positions["boundary_audit"],
        positions["paper_packet"],
        positions["release_checklist"],
    ]
    passed = all(pos is not None for pos in required_order) and required_order == sorted(required_order)
    return bool(passed), positions


def build_markdown(result: dict[str, Any]) -> str:
    rows = ["| Check | Status | Evidence |", "| --- | --- | --- |"]
    for item in result["checks"]:
        rows.append(f"| `{item['check']}` | `{item['status']}` | {item['evidence']} |")

    import_lines = ["- none"] if not result["core_import_violations"] else [
        f"- `{item['file']}` imports `{item['import']}`: {item['reason']}"
        for item in result["core_import_violations"]
    ]
    string_lines = ["- none"] if not result["core_string_violations"] else [
        f"- `{item['file']}` contains `{item['tokens']}`: {item['text']}"
        for item in result["core_string_violations"]
    ]
    boundary_lines = ["- none"] if not result["core_boundary_mentions"] else [
        f"- `{item['file']}` mentions `{item['tokens']}` only as boundary text: {item['text']}"
        for item in result["core_boundary_mentions"]
    ]

    return "\n".join(
        [
            "# HS-JEPA Core/Adapter Boundary Audit",
            "",
            "이 문서는 HS-JEPA가 범용 core architecture와 sleep competition adapter를 코드/문서에서 실제로 분리하고 있는지 검사한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{result['status']}`",
            f"- Checks: `{result['passed_checks']}/{result['total_checks']}` passed",
            "",
            "## Checks",
            "",
            *rows,
            "",
            "## Core Import Violations",
            "",
            *import_lines,
            "",
            "## Core String Violations",
            "",
            *string_lines,
            "",
            "## Allowed Boundary Mentions",
            "",
            *boundary_lines,
            "",
            "## Interpretation",
            "",
            "통과하면 core는 일반 human-state/listener/action-health/invariant interface만 정의하고, Q/S target, public sensor, submission packaging은 adapter가 책임진다고 말할 수 있다.",
            "실패하면 HS-JEPA가 architecture가 아니라 sleep competition 전용 코드 묶음이라는 비판을 피하기 어렵다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    required_paths = [CORE_MANIFEST_JSON, CORE_ABLATION_JSON, ADAPTER_REPORT_JSON, RUNNER]
    missing_paths = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing_paths:
        result = {
            "package": "HS-JEPA Core/Adapter Boundary Audit",
            "status": "boundary_audit_blocked_missing_inputs",
            "missing_inputs": missing_paths,
            "checks": [check("required_inputs_exist", False, f"missing={missing_paths}")],
            "passed_checks": 0,
            "total_checks": 1,
            "core_import_violations": [],
            "core_string_violations": [],
            "core_boundary_mentions": [],
        }
        AUDIT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
        AUDIT_MD.write_text(build_markdown(result), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return result

    core = read_json(CORE_MANIFEST_JSON)
    core_ablation = read_json(CORE_ABLATION_JSON)
    adapter = read_json(ADAPTER_REPORT_JSON)

    imports_ok, import_violations = core_import_audit()
    strings_ok, string_violations, boundary_mentions = core_string_audit()
    manifest_ok, manifest_violations = core_manifest_audit(core, core_ablation)
    adapter_ok, adapter_missing = adapter_dependency_audit(adapter)
    runner_ok, runner_positions = runner_order_audit()

    rows = [
        check("required_inputs_exist", True, "core manifest, core ablation, adapter report, and runner exist"),
        check("core_has_no_forbidden_imports", imports_ok, f"violations={len(import_violations)}"),
        check("core_has_no_operational_competition_paths", strings_ok, f"violations={len(string_violations)}, boundary_mentions={len(boundary_mentions)}"),
        check("core_manifest_is_dataset_agnostic", manifest_ok, f"violations={manifest_violations}"),
        check("adapter_declares_core_dependency", adapter_ok, f"missing_or_bad={adapter_missing}"),
        check("runner_orders_core_before_adapter_before_release", runner_ok, f"positions={runner_positions}"),
    ]

    required_failures = [item for item in rows if item["required"] and not item["passed"]]
    result = {
        "package": "HS-JEPA Core/Adapter Boundary Audit",
        "status": "core_adapter_boundary_verified" if not required_failures else "core_adapter_boundary_failed",
        "passed_checks": sum(1 for item in rows if item["passed"]),
        "total_checks": len(rows),
        "required_failures": required_failures,
        "checks": rows,
        "core_import_violations": import_violations,
        "core_string_violations": string_violations,
        "core_boundary_mentions": boundary_mentions,
        "core_manifest_violations": manifest_violations,
        "adapter_missing_or_bad": adapter_missing,
        "runner_positions": runner_positions,
        "boundary_claim": (
            "HS-JEPA Core is competition-agnostic at the operational dependency layer; "
            "the sleep adapter owns public sensors, Q/S listeners, and submission packaging."
        ),
    }
    AUDIT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    AUDIT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    audit = run()
    raise SystemExit(0 if audit["status"] == "core_adapter_boundary_verified" else 1)
