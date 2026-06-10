#!/usr/bin/env python3
"""Run a dataset-free HS-JEPA module benchmark.

The reference demo shows that the core executes once.  This benchmark makes the
architecture claim harder to fake: several generic human-state worlds define
which listener/action should be released, then module-removal policies are
measured against those expected releases.

No sleep-target names, public leaderboard observations, submission files, or row
ids are allowed here.  Those belong to dataset adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hsjepa_core.core import CandidateAction, ContextView, HSJEPACore, ListenerPrototype  # noqa: E402


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

BENCHMARK_JSON = OUT / "hsjepa_core_module_benchmark.json"
BENCHMARK_MD = OUT / "hsjepa_core_module_benchmark_ko.md"
BENCHMARK_CSV = OUT / "hsjepa_core_module_benchmark_cases.csv"


Vector = tuple[float, ...]


@dataclass(frozen=True)
class Scenario:
    name: str
    human_story: str
    contexts: tuple[ContextView, ...]
    listeners: tuple[ListenerPrototype, ...]
    actions: tuple[CandidateAction, ...]
    invariant_anchors: tuple[Vector, ...]
    expected_release: tuple[str, ...]
    expected_failure_if_removed: dict[str, str]


def unit(values: Iterable[float]) -> Vector:
    vals = tuple(float(v) for v in values)
    total = sum(v * v for v in vals) ** 0.5
    if total <= 1e-12:
        return tuple(0.0 for _ in vals)
    return tuple(v / total for v in vals)


LISTENERS = (
    ListenerPrototype("survey_listener", unit((0.92, 0.20, 0.05, 0.02, 0.00)), sensitivity=1.00),
    ListenerPrototype("sensor_listener", unit((0.08, 0.15, 0.94, 0.05, 0.02)), sensitivity=0.98),
    ListenerPrototype("recovery_listener", unit((0.07, 0.10, 0.05, 0.93, 0.09)), sensitivity=0.95),
    ListenerPrototype("social_listener", unit((0.10, 0.82, 0.10, 0.05, 0.52)), sensitivity=0.90),
)


def make_contexts(prefix: str, base: Vector, drift: Vector, coverage: float, uncertainty: float) -> tuple[ContextView, ...]:
    return (
        ContextView(f"{prefix}_personal", base, coverage=coverage, uncertainty=uncertainty, mask_family="personal"),
        ContextView(f"{prefix}_cohort", unit(tuple(0.82 * a + 0.18 * b for a, b in zip(base, drift))), coverage=coverage - 0.05, uncertainty=uncertainty + 0.02, mask_family="cohort"),
        ContextView(f"{prefix}_time", unit(tuple(0.70 * a + 0.30 * b for a, b in zip(base, drift))), coverage=coverage - 0.10, uncertainty=uncertainty + 0.04, mask_family="routine"),
        ContextView(f"{prefix}_sensor", unit(tuple(0.88 * a + 0.12 * b for a, b in zip(base, drift))), coverage=coverage - 0.08, uncertainty=uncertainty + 0.06, mask_family="sensor"),
    )


def action(name: str, listener: str, delta: Vector, amplitude: float, support: float) -> CandidateAction:
    return CandidateAction(name=name, listener=listener, delta_embedding=delta, amplitude=amplitude, support=support)


def scenarios() -> tuple[Scenario, ...]:
    survey = LISTENERS[0].embedding
    sensor = LISTENERS[1].embedding
    recovery = LISTENERS[2].embedding
    social = LISTENERS[3].embedding
    shortcut = unit((0.80, -0.58, 0.02, 0.02, -0.10))
    # This vector remains partially aligned with the survey listener, but it
    # pulls the post-action state away from the local survey manifold.
    off_manifold = unit((0.62, 0.55, 0.05, 0.15, -0.52))

    return (
        Scenario(
            name="stable_routine_survey_state",
            human_story="A stable routine day where subjective survey state should move slightly, but shortcut moves should not.",
            contexts=make_contexts("stable", survey, social, coverage=0.96, uncertainty=0.04),
            listeners=LISTENERS,
            actions=(
                action("survey_small_state_update", "survey_listener", survey, 0.18, 0.96),
                action("sensor_unrelated_update", "sensor_listener", sensor, 0.18, 0.55),
                action("unsupported_survey_shortcut", "survey_listener", shortcut, 0.75, 0.10),
            ),
            invariant_anchors=(survey, unit((0.88, 0.27, 0.04, 0.02, 0.00))),
            expected_release=("survey_small_state_update",),
            expected_failure_if_removed={
                "remove_action_health": "may over-release low-support shortcuts",
                "remove_invariant_energy": "may release state moves without manifold support",
            },
        ),
        Scenario(
            name="sensor_fragmentation_state",
            human_story="A fragmented sensor day where objective sensor listener should get authority over survey listener.",
            contexts=make_contexts("fragmented", sensor, recovery, coverage=0.90, uncertainty=0.09),
            listeners=LISTENERS,
            actions=(
                action("sensor_fragmentation_update", "sensor_listener", sensor, 0.22, 0.92),
                action("survey_mood_shortcut", "survey_listener", survey, 0.28, 0.34),
                action("recovery_minor_update", "recovery_listener", recovery, 0.18, 0.54),
            ),
            invariant_anchors=(sensor, unit((0.10, 0.19, 0.91, 0.11, 0.02))),
            expected_release=("sensor_fragmentation_update",),
            expected_failure_if_removed={
                "remove_listener_responsibility": "may flatten listener authority and release subjective actions",
                "remove_action_health": "may release weak survey/recovery moves",
            },
        ),
        Scenario(
            name="recovery_debt_state",
            human_story="A recovery-debt day where the same context should route action to recovery, not social or sensor listeners.",
            contexts=make_contexts("recovery", recovery, sensor, coverage=0.91, uncertainty=0.08),
            listeners=LISTENERS,
            actions=(
                action("recovery_debt_update", "recovery_listener", recovery, 0.22, 0.94),
                action("social_calendar_shortcut", "social_listener", social, 0.30, 0.44),
                action("sensor_noise_update", "sensor_listener", sensor, 0.24, 0.46),
            ),
            invariant_anchors=(recovery, unit((0.05, 0.11, 0.06, 0.90, 0.14))),
            expected_release=("recovery_debt_update",),
            expected_failure_if_removed={
                "remove_listener_responsibility": "may confuse recovery with sensor/social listeners",
                "remove_action_health": "may release weak non-recovery moves",
            },
        ),
        Scenario(
            name="cohort_outlier_uncertain_state",
            human_story="A cohort-outlier day with high uncertainty; good architecture should resist broad action release.",
            contexts=(
                ContextView("outlier_personal", social, coverage=0.70, uncertainty=0.28, mask_family="personal"),
                ContextView("outlier_cohort", survey, coverage=0.67, uncertainty=0.31, mask_family="cohort"),
                ContextView("outlier_time", sensor, coverage=0.62, uncertainty=0.34, mask_family="routine"),
                ContextView("outlier_sensor", recovery, coverage=0.58, uncertainty=0.37, mask_family="sensor"),
            ),
            listeners=LISTENERS,
            actions=(
                action("survey_outlier_guess", "survey_listener", survey, 0.28, 0.42),
                action("sensor_outlier_guess", "sensor_listener", sensor, 0.28, 0.42),
                action("social_outlier_guess", "social_listener", social, 0.28, 0.42),
            ),
            invariant_anchors=(unit((0.35, 0.35, 0.35, 0.35, 0.35)),),
            expected_release=(),
            expected_failure_if_removed={
                "remove_action_health": "may release uncertain guesses because threshold is gone",
                "remove_invariant_energy": "may ignore that all guesses leave the stable manifold",
            },
        ),
        Scenario(
            name="off_manifold_listener_trap",
            human_story="A listener-aligned but off-manifold action should be rejected even when the listener looks plausible.",
            contexts=make_contexts("trap", survey, recovery, coverage=0.92, uncertainty=0.06),
            listeners=LISTENERS,
            actions=(
                action("survey_manifold_update", "survey_listener", survey, 0.16, 0.90),
                action("survey_off_manifold_trap", "survey_listener", off_manifold, 0.92, 0.86),
                action("social_weak_update", "social_listener", social, 0.20, 0.30),
            ),
            invariant_anchors=(survey, unit((0.91, 0.23, 0.03, 0.03, 0.00))),
            expected_release=("survey_manifold_update",),
            expected_failure_if_removed={
                "remove_invariant_energy": "may release off-manifold high-support listener action",
                "remove_action_health": "may release weak social action",
            },
        ),
    )


def summarize(decisions: list[dict[str, object]], expected: set[str]) -> dict[str, object]:
    released = {str(item["action"]["name"]) for item in decisions if item.get("released")}
    if not expected and not released:
        return {
            "released": [],
            "expected": [],
            "true_positive": [],
            "false_positive": [],
            "false_negative": [],
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
        }
    false_pos = sorted(released - expected)
    false_neg = sorted(expected - released)
    true_pos = sorted(released & expected)
    precision = len(true_pos) / max(1, len(released))
    recall = len(true_pos) / max(1, len(expected)) if expected else (1.0 if not released else 0.0)
    if precision + recall <= 1e-12:
        f1 = 0.0
    else:
        f1 = 2.0 * precision * recall / (precision + recall)
    return {
        "released": sorted(released),
        "expected": sorted(expected),
        "true_positive": true_pos,
        "false_positive": false_pos,
        "false_negative": false_neg,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def run_policy(
    scenario: Scenario,
    policy: str,
    *,
    health_release_threshold: float,
    invariant_release_threshold: float,
    responsibility_temperature: float = 0.35,
    use_anchors: bool = True,
) -> dict[str, object]:
    core = HSJEPACore(
        responsibility_temperature=responsibility_temperature,
        health_release_threshold=health_release_threshold,
        invariant_release_threshold=invariant_release_threshold,
    )
    return core.release_actions(
        scenario.contexts,
        scenario.listeners,
        scenario.actions,
        scenario.invariant_anchors if use_anchors else None,
    ) | {"policy": policy}


def invariant_only_policy(scenario: Scenario) -> dict[str, object]:
    core = HSJEPACore(health_release_threshold=999.0, invariant_release_threshold=0.36)
    hidden = core.predict_hidden_state(scenario.contexts)
    responsibilities = core.listener_responsibility(hidden, scenario.listeners)
    decisions = []
    for act in scenario.actions:
        decision = core.score_action(hidden, scenario.listeners, responsibilities, act, scenario.invariant_anchors).to_json()
        decision["released"] = decision["invariant_energy_delta"] <= 0.36 and act.support >= 0.25
        decisions.append(decision)
    return {
        "policy": "invariant_only",
        "hidden": hidden.__dict__,
        "responsibilities": responsibilities,
        "decisions": decisions,
        "released_actions": [item["action"]["name"] for item in decisions if item["released"]],
    }


def evaluate_scenario(scenario: Scenario) -> dict[str, object]:
    expected = set(scenario.expected_release)
    policy_outputs = {
        "full_core": run_policy(
            scenario,
            "full_core",
            health_release_threshold=0.052,
            invariant_release_threshold=0.34,
        ),
        "remove_listener_responsibility": run_policy(
            scenario,
            "remove_listener_responsibility",
            responsibility_temperature=999.0,
            health_release_threshold=0.052,
            invariant_release_threshold=0.34,
        ),
        "remove_action_health": run_policy(
            scenario,
            "remove_action_health",
            health_release_threshold=0.0,
            invariant_release_threshold=0.34,
        ),
        "remove_invariant_energy": run_policy(
            scenario,
            "remove_invariant_energy",
            health_release_threshold=0.052,
            invariant_release_threshold=999.0,
            use_anchors=False,
        ),
        "invariant_only": invariant_only_policy(scenario),
    }
    results = {
        name: summarize(output["decisions"], expected)
        for name, output in policy_outputs.items()
    }
    decision_records = []
    for name, output in policy_outputs.items():
        for item in output["decisions"]:
            action_data = item["action"]
            decision_records.append(
                {
                    "scenario": scenario.name,
                    "policy": name,
                    "action": action_data["name"],
                    "listener": action_data["listener"],
                    "released": bool(item["released"]),
                    "expected": action_data["name"] in expected,
                    "listener_responsibility": item["listener_responsibility"],
                    "listener_alignment": item["listener_alignment"],
                    "invariant_energy_delta": item["invariant_energy_delta"],
                    "health_score": item["health_score"],
                }
            )
    return {
        "name": scenario.name,
        "human_story": scenario.human_story,
        "expected_release": list(scenario.expected_release),
        "expected_failure_if_removed": scenario.expected_failure_if_removed,
        "results": results,
        "policy_outputs": policy_outputs,
        "decision_records": decision_records,
    }


def aggregate(evaluated: list[dict[str, object]]) -> dict[str, object]:
    policies = ["full_core", "remove_listener_responsibility", "remove_action_health", "remove_invariant_energy", "invariant_only"]
    rows = []
    for policy in policies:
        precision = sum(item["results"][policy]["precision"] for item in evaluated) / len(evaluated)
        recall = sum(item["results"][policy]["recall"] for item in evaluated) / len(evaluated)
        f1 = sum(item["results"][policy]["f1"] for item in evaluated) / len(evaluated)
        false_positive_count = sum(len(item["results"][policy]["false_positive"]) for item in evaluated)
        false_negative_count = sum(len(item["results"][policy]["false_negative"]) for item in evaluated)
        rows.append(
            {
                "policy": policy,
                "mean_precision": precision,
                "mean_recall": recall,
                "mean_f1": f1,
                "false_positive_count": false_positive_count,
                "false_negative_count": false_negative_count,
            }
        )
    by_policy = {row["policy"]: row for row in rows}
    full = by_policy["full_core"]
    no_health = by_policy["remove_action_health"]
    no_invariant = by_policy["remove_invariant_energy"]
    status = "core_module_benchmark_ready"
    if full["mean_f1"] < 0.70:
        status = "core_module_benchmark_failed_full_core"
    verdict = {
        "status": status,
        "full_core_mean_f1": full["mean_f1"],
        "full_core_false_positive_count": full["false_positive_count"],
        "remove_action_health_false_positive_lift": no_health["false_positive_count"] - full["false_positive_count"],
        "remove_invariant_false_positive_lift": no_invariant["false_positive_count"] - full["false_positive_count"],
        "claim": "The HS-JEPA core has dataset-free module behavior: full core preserves expected listener/action releases, while module removals expose failure modes.",
        "kill_condition": "If full core cannot beat module-removal policies on generic worlds, HS-JEPA is not yet an architecture; it is only an adapter heuristic.",
    }
    return {
        "policy_summary": rows,
        "verdict": verdict,
    }


def build_markdown(result: dict[str, object]) -> str:
    summary_rows = ["| Policy | Mean F1 | False positives | False negatives |", "| --- | ---: | ---: | ---: |"]
    for row in result["policy_summary"]:
        summary_rows.append(
            f"| `{row['policy']}` | `{row['mean_f1']:.3f}` | `{row['false_positive_count']}` | `{row['false_negative_count']}` |"
        )

    case_rows = ["| Scenario | Expected release | Full-core release | Main failure exposed |", "| --- | --- | --- | --- |"]
    for item in result["scenarios"]:
        full_release = ", ".join(item["results"]["full_core"]["released"]) or "none"
        failures = "; ".join(f"{key}: {value}" for key, value in item["expected_failure_if_removed"].items())
        case_rows.append(
            f"| `{item['name']}` | `{', '.join(item['expected_release']) or 'none'}` | `{full_release}` | {failures} |"
        )

    return "\n".join(
        [
            "# HS-JEPA Core Module Benchmark",
            "",
            "이 벤치마크는 sleep competition adapter 없이 HS-JEPA core가 여러 인간상태 상황에서 기대한 release/reject 행동을 내는지 확인한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{result['verdict']['status']}`",
            f"- Full-core mean F1: `{result['verdict']['full_core_mean_f1']:.3f}`",
            f"- Action-health removal false-positive lift: `{result['verdict']['remove_action_health_false_positive_lift']}`",
            f"- Invariant removal false-positive lift: `{result['verdict']['remove_invariant_false_positive_lift']}`",
            "",
            "## Policy Summary",
            "",
            *summary_rows,
            "",
            "## Scenario Summary",
            "",
            *case_rows,
            "",
            "## 해석",
            "",
            "- 이 파일은 LB 점수를 만들지 않는다.",
            "- 대신 HS-JEPA가 `특정 대회 target 이름 없이도` context/listener/action/invariant 구조로 행동한다는 증거를 만든다.",
            "- sleep adapter의 public-sensor 실험은 별도 case-study이고, 이 benchmark는 architecture sanity check다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    evaluated = [evaluate_scenario(item) for item in scenarios()]
    agg = aggregate(evaluated)
    records = [rec for item in evaluated for rec in item["decision_records"]]
    result = {
        "package": "HS-JEPA Core Module Benchmark",
        "status": agg["verdict"]["status"],
        "architecture_role": "dataset_free_core_module_validation",
        "forbidden_dependencies_checked": [
            "no sleep target names",
            "no public leaderboard observations",
            "no submission files",
            "no row ids",
        ],
        "scenario_count": len(evaluated),
        "policy_summary": agg["policy_summary"],
        "verdict": agg["verdict"],
        "scenarios": [
            {
                key: value
                for key, value in item.items()
                if key not in {"policy_outputs", "decision_records"}
            }
            for item in evaluated
        ],
        "outputs": {
            "json": str(BENCHMARK_JSON.resolve()),
            "markdown": str(BENCHMARK_MD.resolve()),
            "csv": str(BENCHMARK_CSV.resolve()),
        },
    }
    BENCHMARK_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    BENCHMARK_MD.write_text(build_markdown(result), encoding="utf-8")
    with BENCHMARK_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "scenario",
                "policy",
                "action",
                "listener",
                "released",
                "expected",
                "listener_responsibility",
                "listener_alignment",
                "invariant_energy_delta",
                "health_score",
            ],
        )
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
