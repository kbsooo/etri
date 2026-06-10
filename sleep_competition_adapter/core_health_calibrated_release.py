#!/usr/bin/env python3
"""Benchmark-calibrated HS-JEPA action release for the sleep adapter.

The dataset-free core benchmark exposed the strongest generic failure mode:
removing action-health creates many false-positive releases.  This adapter
experiment uses that result as a calibration prior instead of treating it as a
paper-only sanity check.

Question tested:

    Can the sleep adapter open a larger row-target boundary while preserving
    the generic HS-JEPA action-health guard?

If the guarded variants win public LB, HS-JEPA has a concrete architecture
story: dataset-free action-health failures predict which competition actions
should be vetoed.  If the relaxed pressure sensor wins instead, the current
core is over-constraining this adapter and the action-health module needs a
less conservative decoder.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import math
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.core_mediated_action_release import (  # noqa: E402
    load_base,
    load_candidate_cells,
    sample_null,
    score_cells,
    score_selection,
    z_and_p,
)
from sleep_competition_adapter.core_release_ablation_probe import (  # noqa: E402
    CONFIGS as CORE_ABLATION_CONFIGS,
    add_ablation_scores,
    select_cells as select_ablation_cells,
)
from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (  # noqa: E402
    clip_prob,
    short_hash,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "core_health_calibrated_release"
OUT.mkdir(parents=True, exist_ok=True)

CORE_BENCHMARK_JSON = ROOT / "hsjepa_core" / "outputs" / "hsjepa_core_module_benchmark.json"

READOUT_JSON = OUT / "core_health_calibrated_release_readout.json"
READOUT_MD = OUT / "core_health_calibrated_release_readout_ko.md"
CELL_CSV = OUT / "core_health_calibrated_release_cells.csv"
NULL_CSV = OUT / "core_health_calibrated_release_null_stress.csv"


@dataclass(frozen=True)
class HealthCalibratedConfig:
    name: str
    allowed_classes: tuple[str, ...]
    max_cells: int
    max_extra_cells: int
    strict_shrink: float
    extra_shrink: float
    health_floor: float | None
    responsibility_floor: float | None
    invariant_cap: float | None
    pressure_floor: float | None
    require_no_opposition: bool
    include_full_seed: bool
    risk_role: str


CONFIGS = [
    HealthCalibratedConfig(
        name="benchmark_guarded_full_plus",
        allowed_classes=("consensus_shadow", "route_only"),
        max_cells=36,
        max_extra_cells=7,
        strict_shrink=0.92,
        extra_shrink=0.34,
        health_floor=0.060,
        responsibility_floor=0.24,
        invariant_cap=0.40,
        pressure_floor=0.18,
        require_no_opposition=True,
        include_full_seed=True,
        risk_role="LB candidate: full-core reference plus benchmark-safe high-pressure boundary cells",
    ),
    HealthCalibratedConfig(
        name="route_pressure_boundary_probe",
        allowed_classes=("consensus_shadow", "route_only", "fusion_only"),
        max_cells=44,
        max_extra_cells=25,
        strict_shrink=0.88,
        extra_shrink=0.16,
        health_floor=0.015,
        responsibility_floor=0.48,
        invariant_cap=0.22,
        pressure_floor=None,
        require_no_opposition=True,
        include_full_seed=True,
        risk_role="Big-bet sensor: tests whether high-responsibility route-only cells are over-vetoed by action-health",
    ),
    HealthCalibratedConfig(
        name="health_relaxed_pressure_sensor",
        allowed_classes=("consensus_shadow", "route_only", "fusion_only"),
        max_cells=42,
        max_extra_cells=26,
        strict_shrink=0.82,
        extra_shrink=0.18,
        health_floor=0.036,
        responsibility_floor=0.12,
        invariant_cap=0.48,
        pressure_floor=0.24,
        require_no_opposition=True,
        include_full_seed=False,
        risk_role="Architecture sensor: tests whether action-health is too conservative despite benchmark FP risk",
    ),
]


def finite(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def fmt(value: Any, digits: int = 4) -> str:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{out:.{digits}f}" if math.isfinite(out) else "n/a"


def rank01(series: pd.Series, higher: bool = True) -> pd.Series:
    if series.notna().sum() <= 1:
        return pd.Series([0.5] * len(series), index=series.index)
    return series.rank(pct=True, method="average", ascending=not higher).fillna(0.0)


def load_core_benchmark() -> dict[str, Any]:
    if not CORE_BENCHMARK_JSON.exists():
        raise FileNotFoundError(CORE_BENCHMARK_JSON)
    return json.loads(CORE_BENCHMARK_JSON.read_text(encoding="utf-8"))


def benchmark_fp_lifts(benchmark: dict[str, Any]) -> dict[str, float]:
    summary = {
        str(item.get("policy")): finite(item.get("false_positive_count"))
        for item in benchmark.get("policy_summary", [])
        if isinstance(item, dict)
    }
    full = summary.get("full_core", 0.0)
    return {
        "remove_listener_responsibility": max(0.0, summary.get("remove_listener_responsibility", 0.0) - full),
        "remove_action_health": max(0.0, summary.get("remove_action_health", 0.0) - full),
        "remove_invariant_energy": max(0.0, summary.get("remove_invariant_energy", 0.0) - full),
        "invariant_only": max(0.0, summary.get("invariant_only", 0.0) - full),
    }


def add_calibrated_scores(scored: pd.DataFrame, benchmark: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, float]]:
    frame = add_ablation_scores(scored)
    lifts = benchmark_fp_lifts(benchmark)
    action_fp_lift = lifts["remove_action_health"]
    invariant_fp_lift = lifts["remove_invariant_energy"]
    listener_fp_lift = lifts["remove_listener_responsibility"]
    scenario_count = max(1.0, finite(benchmark.get("scenario_count"), 1.0))

    health = frame["core_health_score"].astype(float)
    responsibility = frame["core_listener_responsibility"].astype(float)
    invariant = frame["core_invariant_energy_delta"].astype(float)
    pressure = frame["no_action_health_score"].astype(float) - frame["full_core_score"].astype(float)
    health_rank = rank01(health, higher=True)
    resp_rank = rank01(responsibility, higher=True)
    invariant_rank = rank01(invariant, higher=False)
    pressure_rank = rank01(pressure, higher=True)
    action_rank = rank01(frame["action_score"].astype(float), higher=True)

    action_fp_weight = action_fp_lift / (action_fp_lift + scenario_count)
    invariant_fp_weight = invariant_fp_lift / (invariant_fp_lift + scenario_count)
    listener_fp_weight = listener_fp_lift / (listener_fp_lift + scenario_count)

    health_shortfall = (0.060 - health).clip(lower=0.0) / 0.060
    resp_shortfall = (0.22 - responsibility).clip(lower=0.0) / 0.22
    invariant_excess = (invariant - 0.42).clip(lower=0.0) / 0.42

    frame["no_action_pressure"] = pressure
    frame["action_health_risk"] = (
        action_fp_weight * (0.50 * health_shortfall + 0.20 * (1.0 - health_rank))
        + listener_fp_weight * (0.20 * resp_shortfall + 0.10 * (1.0 - resp_rank))
        + invariant_fp_weight * (0.25 * invariant_excess + 0.05 * (1.0 - invariant_rank))
    )
    frame["benchmark_calibrated_score"] = (
        frame["full_core_score"].astype(float)
        + 0.28 * pressure_rank
        + 0.16 * action_rank
        + 0.12 * frame["family_balance"].astype(float)
        + 0.10 * frame["vote_coverage"].astype(float)
        - 0.85 * frame["action_health_risk"].astype(float)
    )
    frame["health_risk_margin"] = 1.0 - frame["action_health_risk"].astype(float)
    frame = frame.sort_values(
        ["benchmark_calibrated_score", "core_release_score", "action_score", "mean_abs_delta"],
        ascending=[False, False, False, False],
        kind="mergesort",
    ).reset_index(drop=True)
    return frame, {
        "action_health_fp_lift": action_fp_lift,
        "invariant_fp_lift": invariant_fp_lift,
        "listener_fp_lift": listener_fp_lift,
        "scenario_count": scenario_count,
        "action_fp_weight": action_fp_weight,
        "invariant_fp_weight": invariant_fp_weight,
        "listener_fp_weight": listener_fp_weight,
    }


def cell_set(frame: pd.DataFrame) -> set[str]:
    return set(frame["cell_key"].astype(str).tolist()) if not frame.empty else set()


def select_cells(scored: pd.DataFrame, config: HealthCalibratedConfig, full_selected: pd.DataFrame) -> pd.DataFrame:
    full_cells = cell_set(full_selected)
    extras = scored[scored["boundary_class"].isin(config.allowed_classes)].copy()
    extras = extras[~extras["cell_key"].astype(str).isin(full_cells)]
    if config.require_no_opposition:
        extras = extras[extras["opposed_weight"].le(1e-12)]
    if config.health_floor is not None:
        extras = extras[extras["core_health_score"].ge(config.health_floor)]
    if config.responsibility_floor is not None:
        extras = extras[extras["core_listener_responsibility"].ge(config.responsibility_floor)]
    if config.invariant_cap is not None:
        extras = extras[extras["core_invariant_energy_delta"].le(config.invariant_cap)]
    if config.pressure_floor is not None:
        extras = extras[extras["no_action_pressure"].ge(config.pressure_floor)]
    extras = extras.sort_values(
        ["benchmark_calibrated_score", "no_action_pressure", "core_release_score", "mean_abs_delta"],
        ascending=[False, False, False, False],
        kind="mergesort",
    ).drop_duplicates(["row", "target"], keep="first").head(config.max_extra_cells)

    if config.include_full_seed:
        selected = pd.concat([full_selected, extras], ignore_index=True)
    else:
        selected = extras
        if len(selected) < min(config.max_cells, 18):
            strict = scored[scored["boundary_class"].eq("strict_jury")].copy()
            strict = strict[
                strict["core_health_score"].ge(config.health_floor or 0.0)
                & strict["core_invariant_energy_delta"].le(config.invariant_cap or 1.0)
            ].sort_values(
                ["no_action_pressure", "benchmark_calibrated_score", "action_score"],
                ascending=[False, False, False],
                kind="mergesort",
            )
            selected = pd.concat([selected, strict], ignore_index=True)

    return (
        selected.drop_duplicates(["row", "target"], keep="first")
        .sort_values(
            ["benchmark_calibrated_score", "core_release_score", "action_score"],
            ascending=[False, False, False],
            kind="mergesort",
        )
        .head(config.max_cells)
        .reset_index(drop=True)
    )


def apply_selection(base_prob: np.ndarray, selected: pd.DataFrame, config: HealthCalibratedConfig) -> np.ndarray:
    prob = base_prob.copy()
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        shrink = config.strict_shrink if rec["boundary_class"] == "strict_jury" else config.extra_shrink
        risk_margin = max(0.50, min(1.05, finite(rec.get("health_risk_margin"), 1.0)))
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + shrink * risk_margin * float(rec["action_delta"]))
    return prob


def make_submission(
    base: pd.DataFrame,
    base_prob: np.ndarray,
    selected: pd.DataFrame,
    config: HealthCalibratedConfig,
) -> tuple[Path, Path, dict[str, object]]:
    prob = apply_selection(base_prob, selected, config)
    suffix = short_hash(prob)
    file_name = f"submission_hsjepa_core_health_{config.name}_{suffix}_uploadsafe.csv"
    root_path = ROOT / file_name
    local_path = OUT / file_name
    write_submission(root_path, base, prob)
    write_submission(local_path, base, prob)
    validation = validate_submission(root_path, base, base_prob)
    return root_path, local_path, validation


def extended_metrics(selected: pd.DataFrame, full_cells: set[str]) -> dict[str, float]:
    base = score_selection(selected)
    if selected.empty:
        base.update(
            {
                "mean_calibrated_score": 0.0,
                "mean_no_action_pressure": 0.0,
                "mean_action_health_risk": 0.0,
                "mean_health_risk_margin": 0.0,
                "full_overlap_rate": 0.0,
                "high_pressure_rate": 0.0,
                "high_risk_rate": 0.0,
                "q_rate": 0.0,
                "s_rate": 0.0,
            }
        )
        return base
    selected_cells = cell_set(selected)
    base.update(
        {
            "mean_calibrated_score": float(selected["benchmark_calibrated_score"].mean()),
            "mean_no_action_pressure": float(selected["no_action_pressure"].mean()),
            "mean_action_health_risk": float(selected["action_health_risk"].mean()),
            "mean_health_risk_margin": float(selected["health_risk_margin"].mean()),
            "full_overlap_rate": float(len(selected_cells & full_cells) / max(1, len(selected_cells))),
            "high_pressure_rate": float(selected["no_action_pressure"].ge(0.20).mean()),
            "high_risk_rate": float(selected["action_health_risk"].ge(0.25).mean()),
            "q_rate": float(selected["target"].astype(str).str.startswith("Q").mean()),
            "s_rate": float(selected["target"].astype(str).str.startswith("S").mean()),
        }
    )
    return base


def stress_selection(
    scored: pd.DataFrame,
    selected: pd.DataFrame,
    full_cells: set[str],
    seed: int = 20260611,
    iters: int = 700,
) -> dict[str, Any]:
    actual = extended_metrics(selected, full_cells)
    rng = np.random.default_rng(seed)
    null_rows = []
    for idx in range(iters):
        sampled = sample_null(scored, selected, rng)
        metrics = extended_metrics(sampled, full_cells)
        metrics["iteration"] = idx
        null_rows.append(metrics)
    null = pd.DataFrame(null_rows)
    tests = {
        "mean_calibrated_score": z_and_p(actual["mean_calibrated_score"], null["mean_calibrated_score"].to_list(), higher_is_better=True),
        "mean_no_action_pressure": z_and_p(actual["mean_no_action_pressure"], null["mean_no_action_pressure"].to_list(), higher_is_better=True),
        "mean_health": z_and_p(actual["mean_health"], null["mean_health"].to_list(), higher_is_better=True),
        "mean_release_score": z_and_p(actual["mean_release_score"], null["mean_release_score"].to_list(), higher_is_better=True),
        "mean_health_risk_margin": z_and_p(actual["mean_health_risk_margin"], null["mean_health_risk_margin"].to_list(), higher_is_better=True),
        "mean_action_health_risk": z_and_p(actual["mean_action_health_risk"], null["mean_action_health_risk"].to_list(), higher_is_better=False),
        "high_risk_rate": z_and_p(actual["high_risk_rate"], null["high_risk_rate"].to_list(), higher_is_better=False),
    }
    return {"actual": actual, "tests": tests, "null_rows": null_rows}


def priority(metrics: dict[str, Any], config: HealthCalibratedConfig, upload_safe: bool) -> float:
    if not upload_safe:
        return -99.0
    tests = metrics["tests"]
    actual = metrics["actual"]
    calibrated_z = finite(tests["mean_calibrated_score"]["z"])
    pressure_z = finite(tests["mean_no_action_pressure"]["z"])
    health_z = finite(tests["mean_health"]["z"])
    margin_z = finite(tests["mean_health_risk_margin"]["z"])
    high_risk = finite(actual["high_risk_rate"])
    novelty = 1.0 - finite(actual["full_overlap_rate"], 1.0)
    sensor_penalty = 0.22 if config.name == "health_relaxed_pressure_sensor" else 0.0
    return (
        0.30 * max(-1.0, min(2.0, calibrated_z / 3.0))
        + 0.20 * max(-1.0, min(2.0, pressure_z / 3.0))
        + 0.20 * max(-1.0, min(2.0, health_z / 3.0))
        + 0.15 * max(-1.0, min(2.0, margin_z / 3.0))
        + 0.13 * novelty
        - 0.35 * high_risk
        - sensor_penalty
        + 0.10
    )


def status_for(metrics: dict[str, Any], config: HealthCalibratedConfig, upload_safe: bool) -> str:
    if not upload_safe:
        return "core_health_calibrated_not_upload_safe"
    actual = metrics["actual"]
    if finite(actual["cells"]) <= 0:
        return "core_health_calibrated_empty"
    if config.name == "benchmark_guarded_full_plus" and finite(actual["extra_cells"]) > 0:
        return "benchmark_guarded_full_plus_ready"
    if config.name == "route_pressure_boundary_probe":
        return "route_pressure_boundary_probe_ready"
    return "health_relaxed_pressure_sensor_ready"


def build_markdown(readout: dict[str, Any]) -> str:
    verdict = readout["verdict"]
    lb = verdict["recommended_lb_candidate"]
    big = verdict["recommended_big_bet_sensor"]
    pressure = verdict["recommended_pressure_sensor"]
    rows = [
        "| Rank | Variant | Cells | Extra | Full overlap | Pressure z | Health z | Risk margin z | High risk | Priority | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for rec in readout["ranking"]:
        actual = rec["stress"]["actual"]
        tests = rec["stress"]["tests"]
        rows.append(
            f"| `{rec['rank']}` | `{rec['variant']}` | `{int(actual['cells'])}` | `{int(actual['extra_cells'])}` | "
            f"`{fmt(actual['full_overlap_rate'])}` | `{fmt(tests['mean_no_action_pressure']['z'])}` | "
            f"`{fmt(tests['mean_health']['z'])}` | `{fmt(tests['mean_health_risk_margin']['z'])}` | "
            f"`{fmt(actual['high_risk_rate'])}` | `{fmt(rec['priority'])}` | `{rec['submission_file']}` |"
        )
    return "\n".join(
        [
            "# HS-JEPA Core-Health Calibrated Release",
            "",
            "dataset-free core benchmark에서 action-health 제거가 false positive를 크게 만든다는 결론을 실제 sleep adapter release rule에 넣은 실험이다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['status']}`",
            f"- Recommended LB candidate: `{lb['variant']}` / `{lb['submission_file']}` / priority `{fmt(lb['priority'])}`",
            f"- Recommended big-bet sensor: `{big['variant']}` / `{big['submission_file']}` / priority `{fmt(big['priority'])}`",
            f"- Recommended pressure sensor: `{pressure['variant']}` / `{pressure['submission_file']}` / priority `{fmt(pressure['priority'])}`",
            f"- Core benchmark action-health FP lift: `{readout['benchmark_calibration']['action_health_fp_lift']}`",
            "",
            "## Ranking",
            "",
            *rows,
            "",
            "## Interpretation",
            "",
            "- `benchmark_guarded_full_plus`가 public에서 좋으면 action-health guard가 leaderboard action에도 유효하다는 주장에 힘이 실린다.",
            "- `route_pressure_boundary_probe`가 좋으면 route-only high-responsibility cells가 action-health에 의해 과하게 막혔다는 뜻이다.",
            "- `health_relaxed_pressure_sensor`가 이기면 generic benchmark와 sleep adapter가 충돌한다. 그 경우 action-health는 버릴 모듈이 아니라 adapter-specific decoder를 다시 배워야 하는 모듈이다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    base, base_prob = load_base()
    benchmark = load_core_benchmark()
    scored, calibration = add_calibrated_scores(score_cells(load_candidate_cells()), benchmark)
    scored.to_csv(CELL_CSV, index=False)

    full_selected = select_ablation_cells(scored, CORE_ABLATION_CONFIGS[0])
    full_cells = cell_set(full_selected)

    variants: dict[str, Any] = {}
    null_frames = []
    for config in CONFIGS:
        selected = select_cells(scored, config, full_selected)
        root_path, local_path, validation = make_submission(base, base_prob, selected, config)
        stress = stress_selection(scored, selected, full_cells)
        if stress["null_rows"]:
            null_frame = pd.DataFrame(stress["null_rows"])
            null_frame["variant"] = config.name
            null_frames.append(null_frame)
        variants[config.name] = {
            "variant": config.name,
            "status": status_for(stress, config, bool(validation.get("upload_safe"))),
            "submission_file": root_path.name,
            "root_path": str(root_path.resolve()),
            "local_path": str(local_path.resolve()),
            "validation": validation,
            "selected_cells": selected.to_dict("records"),
            "stress": {"actual": stress["actual"], "tests": stress["tests"]},
            "priority": priority(stress, config, bool(validation.get("upload_safe"))),
            "config": {
                "name": config.name,
                "allowed_classes": list(config.allowed_classes),
                "max_cells": config.max_cells,
                "max_extra_cells": config.max_extra_cells,
                "strict_shrink": config.strict_shrink,
                "extra_shrink": config.extra_shrink,
                "health_floor": config.health_floor,
                "responsibility_floor": config.responsibility_floor,
                "invariant_cap": config.invariant_cap,
                "pressure_floor": config.pressure_floor,
                "require_no_opposition": config.require_no_opposition,
                "include_full_seed": config.include_full_seed,
                "risk_role": config.risk_role,
            },
        }

    if null_frames:
        pd.concat(null_frames, ignore_index=True).to_csv(NULL_CSV, index=False)
    else:
        pd.DataFrame().to_csv(NULL_CSV, index=False)

    ranking = sorted(variants.values(), key=lambda item: item["priority"], reverse=True)
    for rank, item in enumerate(ranking, 1):
        item["rank"] = rank
    upload_safe = [item for item in ranking if item["validation"].get("upload_safe")]
    guarded = variants["benchmark_guarded_full_plus"]
    big = variants["route_pressure_boundary_probe"]
    pressure = variants["health_relaxed_pressure_sensor"]
    readout = {
        "experiment": "HS-JEPA Core-Health Calibrated Release",
        "architecture_role": "dataset_free_core_benchmark_to_sleep_adapter_release",
        "status": "core_health_calibrated_release_ready",
        "verdict": {
            "status": "core_health_calibrated_release_ready",
            "recommended_lb_candidate": {
                "variant": guarded["variant"],
                "submission_file": guarded["submission_file"],
                "priority": guarded["priority"],
            },
            "recommended_big_bet_sensor": {
                "variant": big["variant"],
                "submission_file": big["submission_file"],
                "priority": big["priority"],
            },
            "recommended_pressure_sensor": {
                "variant": pressure["variant"],
                "submission_file": pressure["submission_file"],
                "priority": pressure["priority"],
            },
            "top_ranked_upload_safe": {
                "variant": upload_safe[0]["variant"],
                "submission_file": upload_safe[0]["submission_file"],
                "priority": upload_safe[0]["priority"],
            } if upload_safe else None,
            "claim": (
                "Dataset-free HS-JEPA action-health failures can calibrate the real sleep-adapter row-target release boundary."
            ),
            "failure_interpretation": (
                "If relaxed pressure beats guarded release on public LB, action-health is still a useful module but the adapter needs a less conservative action decoder."
            ),
        },
        "benchmark_calibration": calibration,
        "ranking": ranking,
        "outputs": {
            "json": str(READOUT_JSON.resolve()),
            "markdown": str(READOUT_MD.resolve()),
            "cells": str(CELL_CSV.resolve()),
            "null_stress": str(NULL_CSV.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps(readout["verdict"], indent=2, ensure_ascii=False, allow_nan=False))
    return readout


if __name__ == "__main__":
    run()
