#!/usr/bin/env python3
"""Build the competition-agnostic HS-JEPA core manifest.

The core manifest is intentionally free of sleep-target names, public
leaderboard sensors, and submission files.  It defines the reusable mechanism
that a competition adapter can instantiate for a specific dataset.
"""

from __future__ import annotations

from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

MANIFEST_JSON = OUT / "hsjepa_core_manifest.json"
MANIFEST_MD = OUT / "hsjepa_core_manifest_ko.md"
ABLATION_JSON = OUT / "hsjepa_core_ablation_contract.json"
ABLATION_MD = OUT / "hsjepa_core_ablation_contract_ko.md"
REFERENCE_JSON = OUT / "hsjepa_core_reference_run.json"
REFERENCE_MD = OUT / "hsjepa_core_reference_run_ko.md"


CORE_MODULES = [
    {
        "id": "context_encoder",
        "name": "Human-State Context Encoder",
        "purpose": "Encode partial person, cohort, time, routine, social, and sensor context into a hidden human-state field.",
        "input_contract": ["personal baseline", "cohort-relative context", "temporal/routine context", "sensor reliability context"],
        "output_contract": ["hidden human-state embedding", "state uncertainty", "context coverage mask"],
        "failure_if_removed": "The model collapses into direct label prior fitting or local feature heuristics.",
    },
    {
        "id": "masked_state_predictor",
        "name": "Masked State Predictor",
        "purpose": "Predict unobserved state/listener representations from visible context without reconstructing raw inputs.",
        "input_contract": ["visible context view", "semantic mask definition"],
        "output_contract": ["predicted hidden state", "prediction energy"],
        "failure_if_removed": "The representation no longer proves that it understands hidden human structure.",
    },
    {
        "id": "listener_responsibility",
        "name": "Listener Responsibility",
        "purpose": "Treat labels, sensors, surveys, or outcomes as listeners that react differently to the same human state.",
        "input_contract": ["hidden human-state embedding", "candidate listener set"],
        "output_contract": ["listener responsibility distribution", "listener-specific uncertainty"],
        "failure_if_removed": "The architecture becomes a flat multi-label classifier with no explanation of which outcome should react.",
    },
    {
        "id": "action_health_decoder",
        "name": "Action-Health Decoder",
        "purpose": "Decide whether a latent signal is healthy enough to translate into an output action.",
        "input_contract": ["hidden state", "listener responsibility", "candidate action"],
        "output_contract": ["action-health score", "toxicity/risk flag", "bounded action amplitude"],
        "failure_if_removed": "Good-looking latent signals become unsafe output moves and overfit shortcut regions.",
    },
    {
        "id": "invariant_energy",
        "name": "Invariant Energy",
        "purpose": "Score whether an action preserves the behavioral, physiological, temporal, or semantic manifold of the domain.",
        "input_contract": ["pre-action representation", "post-action representation", "domain invariant definition"],
        "output_contract": ["invariant energy delta", "veto decision"],
        "failure_if_removed": "The model can improve a local listener while breaking the global human-state manifold.",
    },
    {
        "id": "anti_shortcut_validation",
        "name": "Anti-Shortcut Validation",
        "purpose": "Stress-test the representation and action field against nulls, cohort shifts, time shifts, and shortcut sensors.",
        "input_contract": ["candidate action field", "null generator", "stress split definitions"],
        "output_contract": ["shortcut verdict", "collapse verdict", "portability warning"],
        "failure_if_removed": "A lucky split or public-only shortcut can be mistaken for human-state understanding.",
    },
]


CORE_PORTABILITY_GATES = [
    {
        "gate": "no_competition_target_names",
        "passed": True,
        "evidence": "Core contracts use generic listeners/outcomes instead of dataset-specific target names.",
    },
    {
        "gate": "no_public_sensor_dependency",
        "passed": True,
        "evidence": "Core contracts do not require leaderboard observations or submission files.",
    },
    {
        "gate": "adapter_boundary_required",
        "passed": True,
        "evidence": "Dataset-specific invariants and output schema must be supplied by an adapter.",
    },
    {
        "gate": "ablation_contract_defined",
        "passed": True,
        "evidence": "Each core module has a removal test and expected failure mode.",
    },
    {
        "gate": "human_understanding_scope",
        "passed": True,
        "evidence": "The core predicts hidden state/listener/action representations before final labels.",
    },
]


ABLATIONS = [
    {
        "ablation": "remove_context_encoder",
        "removed_module": "context_encoder",
        "expected_failure": "listener responsibility becomes prior-heavy and cohort/time generalization weakens.",
        "measurement": "drop in listener orientation, worse stress performance under cohort/time split.",
    },
    {
        "ablation": "remove_masked_state_prediction",
        "removed_module": "masked_state_predictor",
        "expected_failure": "representation can no longer predict hidden state under semantic masks.",
        "measurement": "masked representation prediction energy loses separation from null.",
    },
    {
        "ablation": "remove_listener_responsibility",
        "removed_module": "listener_responsibility",
        "expected_failure": "the same latent move is applied to wrong outcomes/listeners.",
        "measurement": "target/listener action precision drops while aggregate score may look locally stable.",
    },
    {
        "ablation": "remove_action_health",
        "removed_module": "action_health_decoder",
        "expected_failure": "unsafe latent signals are translated into overbroad output moves.",
        "measurement": "toxicity or negative-sensor alignment rises; high-energy tails worsen.",
    },
    {
        "ablation": "remove_invariant_energy",
        "removed_module": "invariant_energy",
        "expected_failure": "local action gains break the domain manifold.",
        "measurement": "selected actions lose energy advantage versus feasible null bundles.",
    },
    {
        "ablation": "remove_anti_shortcut_validation",
        "removed_module": "anti_shortcut_validation",
        "expected_failure": "collapse, split shortcut, or public-only behavior is overclaimed as architecture.",
        "measurement": "green score without null/stress survival is marked non-releasable.",
    },
]


def build_manifest() -> dict[str, object]:
    return {
        "package": "HS-JEPA Core",
        "status": "core_ready_for_adapter",
        "claim": (
            "HS-JEPA is a general architecture for human-understanding prediction: "
            "predict hidden human-state, listener responsibility, action-health, "
            "and invariant-preserving action representations before making bounded outputs."
        ),
        "core_equation": (
            "partial_human_context -> hidden_human_state -> listener_responsibility "
            "-> action_health -> invariant_preserving_decoder -> anti_shortcut_validation"
        ),
        "modules": CORE_MODULES,
        "portability_gates": CORE_PORTABILITY_GATES,
        "passed_gates": sum(1 for gate in CORE_PORTABILITY_GATES if gate["passed"]),
        "total_gates": len(CORE_PORTABILITY_GATES),
        "requires_adapter_for": [
            "dataset schema",
            "domain invariant definition",
            "listener/output names",
            "deployment metric",
            "output or serving format",
        ],
        "reference_implementation": {
            "core_module": "hsjepa_core/core.py",
            "reference_runner": "hsjepa_core/run_core_reference_demo.py",
            "reference_outputs": [
                str(REFERENCE_JSON.relative_to(HERE.parent)),
                str(REFERENCE_MD.relative_to(HERE.parent)),
            ],
            "claim": "The core can execute on synthetic context/listener/action inputs before any domain adapter is attached.",
        },
        "forbidden_core_dependencies": [
            "public leaderboard observations",
            "dataset-specific target names",
            "submission file names",
            "manual row ids",
            "private labels",
        ],
    }


def build_ablation_contract() -> dict[str, object]:
    return {
        "package": "HS-JEPA Core",
        "status": "ablation_contract_ready",
        "purpose": "Make the HS-JEPA mechanism falsifiable instead of only descriptive.",
        "ablations": ABLATIONS,
        "minimum_publishable_evidence": [
            "core module removal changes downstream behavior",
            "invariant-energy removal loses null separation",
            "action-health removal increases toxic action rate",
            "listener removal hurts target/outcome routing",
            "anti-shortcut validation rejects at least one tempting but false shortcut",
        ],
    }


def build_manifest_markdown(manifest: dict[str, object]) -> str:
    module_rows = [
        "| Module | Purpose | Output | Failure if removed |",
        "| --- | --- | --- | --- |",
    ]
    for item in manifest["modules"]:
        module_rows.append(
            f"| `{item['name']}` | {item['purpose']} | {', '.join(item['output_contract'])} | {item['failure_if_removed']} |"
        )

    gate_rows = ["| Gate | Status | Evidence |", "| --- | --- | --- |"]
    for gate in manifest["portability_gates"]:
        gate_rows.append(f"| `{gate['gate']}` | `{'PASS' if gate['passed'] else 'FAIL'}` | {gate['evidence']} |")

    return "\n".join(
        [
            "# HS-JEPA Core Architecture Manifest",
            "",
            "이 문서는 HS-JEPA의 재사용 가능한 core를 정의한다. 여기에는 특정 대회 target 이름, public LB, submission 파일명이 들어가지 않는다.",
            "",
            "## Core Claim",
            "",
            manifest["claim"],
            "",
            "## Core Equation",
            "",
            "```text",
            manifest["core_equation"],
            "```",
            "",
            "## Modules",
            "",
            *module_rows,
            "",
            "## Portability Gates",
            "",
            *gate_rows,
            "",
            "## Adapter가 책임지는 것",
            "",
            *[f"- {item}" for item in manifest["requires_adapter_for"]],
            "",
            "## Reference Implementation",
            "",
            f"- Core module: `{manifest['reference_implementation']['core_module']}`",
            f"- Reference runner: `{manifest['reference_implementation']['reference_runner']}`",
            f"- Claim: {manifest['reference_implementation']['claim']}",
            "",
            "## Core에 들어오면 안 되는 것",
            "",
            *[f"- {item}" for item in manifest["forbidden_core_dependencies"]],
            "",
        ]
    )


def build_ablation_markdown(contract: dict[str, object]) -> str:
    rows = ["| Ablation | Removed module | Expected failure | Measurement |", "| --- | --- | --- | --- |"]
    for item in contract["ablations"]:
        rows.append(
            f"| `{item['ablation']}` | `{item['removed_module']}` | {item['expected_failure']} | {item['measurement']} |"
        )

    return "\n".join(
        [
            "# HS-JEPA Core Ablation Contract",
            "",
            "이 문서는 HS-JEPA를 논문/발표용 아키텍처로 주장하기 위해 반드시 죽여봐야 할 제거 실험을 정의한다.",
            "",
            "## Purpose",
            "",
            contract["purpose"],
            "",
            "## Ablations",
            "",
            *rows,
            "",
            "## Minimum Publishable Evidence",
            "",
            *[f"- {item}" for item in contract["minimum_publishable_evidence"]],
            "",
        ]
    )


def run() -> dict[str, object]:
    manifest = build_manifest()
    ablation = build_ablation_contract()
    MANIFEST_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    MANIFEST_MD.write_text(build_manifest_markdown(manifest), encoding="utf-8")
    ABLATION_JSON.write_text(json.dumps(ablation, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    ABLATION_MD.write_text(build_ablation_markdown(ablation), encoding="utf-8")
    result = {
        "manifest_json": str(MANIFEST_JSON.resolve()),
        "manifest_md": str(MANIFEST_MD.resolve()),
        "ablation_json": str(ABLATION_JSON.resolve()),
        "ablation_md": str(ABLATION_MD.resolve()),
        "status": manifest["status"],
        "ablation_status": ablation["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
