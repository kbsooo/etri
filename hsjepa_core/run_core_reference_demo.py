#!/usr/bin/env python3
"""Run a tiny dataset-free HS-JEPA core demonstration."""

from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.core import CandidateAction, ContextView, HSJEPACore, ListenerPrototype  # noqa: E402


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

REFERENCE_JSON = OUT / "hsjepa_core_reference_run.json"
REFERENCE_MD = OUT / "hsjepa_core_reference_run_ko.md"


def build_fixture() -> tuple[list[ContextView], list[ListenerPrototype], list[CandidateAction], list[tuple[float, ...]]]:
    contexts = [
        ContextView("personal_baseline", (0.82, 0.12, 0.05, 0.01), coverage=0.95, uncertainty=0.05),
        ContextView("cohort_relative_context", (0.76, 0.18, 0.04, 0.02), coverage=0.90, uncertainty=0.08),
        ContextView("temporal_routine_context", (0.70, 0.22, 0.06, 0.02), coverage=0.85, uncertainty=0.12),
        ContextView("sensor_reliability_context", (0.80, 0.12, 0.04, 0.04), coverage=0.80, uncertainty=0.15),
    ]
    listeners = [
        ListenerPrototype("survey_listener", (0.75, 0.20, 0.05, 0.00), sensitivity=1.00),
        ListenerPrototype("sensor_listener", (0.10, 0.20, 0.65, 0.05), sensitivity=0.95),
        ListenerPrototype("recovery_listener", (0.15, 0.10, 0.05, 0.70), sensitivity=0.90),
    ]
    actions = [
        CandidateAction("survey_small_shift", "survey_listener", (0.08, 0.03, -0.01, 0.00), amplitude=0.30, support=0.95),
        CandidateAction("sensor_route_shift", "sensor_listener", (-0.02, 0.01, 0.10, 0.00), amplitude=0.35, support=0.88),
        CandidateAction("recovery_minor_shift", "recovery_listener", (0.00, 0.00, 0.02, 0.08), amplitude=0.20, support=0.72),
        CandidateAction("unsupported_large_shortcut", "survey_listener", (0.60, -0.50, 0.00, 0.00), amplitude=0.80, support=0.12),
    ]
    anchors = [
        (0.82, 0.12, 0.05, 0.01),
        (0.76, 0.18, 0.04, 0.02),
        (0.70, 0.22, 0.06, 0.02),
    ]
    return contexts, listeners, actions, anchors


def summarize_decisions(decisions: list[dict[str, object]]) -> dict[str, object]:
    released = [item for item in decisions if item.get("released")]
    rejected = [item for item in decisions if not item.get("released")]
    return {
        "released_count": len(released),
        "rejected_count": len(rejected),
        "released_actions": [item["action"]["name"] for item in released],
        "rejected_actions": [item["action"]["name"] for item in rejected],
    }


def build_markdown(result: dict[str, object]) -> str:
    full = result["full_core"]
    ablations = result["ablations"]
    rows = ["| Case | Released | Rejected | Released actions |", "| --- | ---: | ---: | --- |"]
    rows.append(
        "| `full_core` | "
        f"`{full['summary']['released_count']}` | `{full['summary']['rejected_count']}` | "
        f"`{', '.join(full['summary']['released_actions'])}` |"
    )
    for name, item in ablations.items():
        rows.append(
            f"| `{name}` | `{item['released_count']}` | `{item['rejected_count']}` | "
            f"`{', '.join(item['released_actions'])}` |"
        )

    return "\n".join(
        [
            "# HS-JEPA Core Reference Run",
            "",
            "이 파일은 특정 데이터셋 adapter 없이 HS-JEPA core가 실행 가능하다는 것을 보여주는 synthetic reference run이다.",
            "",
            "## Claim",
            "",
            str(result["claim"]),
            "",
            "## Release Summary",
            "",
            *rows,
            "",
            "## Responsibilities",
            "",
            "```json",
            json.dumps(full["responsibilities"], indent=2, ensure_ascii=False, allow_nan=False),
            "```",
            "",
            "## Interpretation",
            "",
            "- listener responsibility는 같은 hidden state가 어느 listener로 번역될지 정한다.",
            "- action-health는 좋아 보이는 latent move가 곧바로 output action이 되는 것을 막는다.",
            "- invariant energy는 adapter가 제공한 human-state manifold 밖으로 나가는 action을 제한한다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    contexts, listeners, actions, anchors = build_fixture()
    core = HSJEPACore(
        responsibility_temperature=0.35,
        health_release_threshold=0.055,
        invariant_release_threshold=0.38,
    )
    full = core.release_actions(contexts, listeners, actions, anchors)

    no_listener_core = HSJEPACore(
        responsibility_temperature=999.0,
        health_release_threshold=0.055,
        invariant_release_threshold=0.38,
    )
    no_listener = no_listener_core.release_actions(contexts, listeners, actions, anchors)

    no_action_health_core = HSJEPACore(
        responsibility_temperature=0.35,
        health_release_threshold=0.0,
        invariant_release_threshold=0.38,
    )
    no_action_health = no_action_health_core.release_actions(contexts, listeners, actions, anchors)

    no_invariant_core = HSJEPACore(
        responsibility_temperature=0.35,
        health_release_threshold=0.055,
        invariant_release_threshold=999.0,
    )
    no_invariant = no_invariant_core.release_actions(contexts, listeners, actions, None)

    result = {
        "package": "HS-JEPA Core Reference Run",
        "status": "core_reference_ready",
        "claim": "The HS-JEPA mechanism executes without a domain adapter and exposes falsifiable module-removal behavior.",
        "full_core": {
            "summary": summarize_decisions(full["decisions"]),
            "hidden": full["hidden"],
            "responsibilities": full["responsibilities"],
            "decisions": full["decisions"],
        },
        "ablations": {
            "remove_listener_responsibility": summarize_decisions(no_listener["decisions"]),
            "remove_action_health": summarize_decisions(no_action_health["decisions"]),
            "remove_invariant_energy": summarize_decisions(no_invariant["decisions"]),
        },
        "interpretation": {
            "listener_responsibility": "Changes which listener receives action authority.",
            "action_health": "Prevents every aligned latent move from becoming an output action.",
            "invariant_energy": "Keeps action release close to the hidden-state manifold supplied by the adapter.",
        },
    }
    REFERENCE_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REFERENCE_MD.write_text(build_markdown(result), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
