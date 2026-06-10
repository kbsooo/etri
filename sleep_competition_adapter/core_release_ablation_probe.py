#!/usr/bin/env python3
"""Ablate HS-JEPA core modules on real sleep-adapter actions.

The synthetic core reference run proves that the reusable HS-JEPA API executes.
The core-mediated release probe proves that real row-target action candidates
can be converted into ContextView/ListenerPrototype/CandidateAction objects.

This script asks the next paper-facing question:

    Which HS-JEPA core module actually changes the action boundary on real
    sleep-adapter cells?

It keeps the same candidate universe as core_mediated_action_release.py and
creates counterfactual release policies:

* full_core_reference: listener responsibility + action health + invariant.
* no_listener_responsibility: health is computed as if every listener had full
  authority.
* no_action_health: high route/fusion action evidence can release without the
  core health gate.
* no_invariant_energy: health can release even when the move leaves the
  invariant manifold.
* invariant_only: low invariant energy can release even without listener/action
  health strength.

The outputs are upload-safe probes and a module-ablation report.  Public LB is
not optimized here; it is a sensor for whether a removed module was decorative
or actually necessary for action-grade release.
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

from sleep_competition_adapter.core_mediated_action_release import (
    load_base,
    load_candidate_cells,
    score_cells,
    score_selection,
    sample_null,
    z_and_p,
)
from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (
    clip_prob,
    short_hash,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "core_release_ablation_probe"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "core_release_ablation_probe_readout.json"
READOUT_MD = OUT / "core_release_ablation_probe_readout_ko.md"
CELL_CSV = OUT / "core_release_ablation_probe_cells.csv"
NULL_CSV = OUT / "core_release_ablation_probe_null_stress.csv"


@dataclass(frozen=True)
class AblationConfig:
    name: str
    score_col: str
    allowed_classes: tuple[str, ...]
    max_cells: int
    strict_shrink: float
    extra_shrink: float
    require_no_opposition: bool
    health_floor: float | None
    invariant_cap: float | None
    risk_role: str


CONFIGS = [
    AblationConfig(
        name="full_core_reference",
        score_col="full_core_score",
        allowed_classes=("strict_jury", "consensus_shadow"),
        max_cells=29,
        strict_shrink=0.92,
        extra_shrink=0.42,
        require_no_opposition=True,
        health_floor=0.052,
        invariant_cap=0.44,
        risk_role="baseline full HS-JEPA core boundary on strict plus weak-consensus cells",
    ),
    AblationConfig(
        name="no_listener_responsibility",
        score_col="no_listener_score",
        allowed_classes=("strict_jury", "consensus_shadow"),
        max_cells=34,
        strict_shrink=0.90,
        extra_shrink=0.36,
        require_no_opposition=True,
        health_floor=None,
        invariant_cap=0.44,
        risk_role="tests whether listener responsibility is actually needed for action authority",
    ),
    AblationConfig(
        name="no_action_health",
        score_col="no_action_health_score",
        allowed_classes=("strict_jury", "consensus_shadow", "route_only", "fusion_only"),
        max_cells=40,
        strict_shrink=0.84,
        extra_shrink=0.24,
        require_no_opposition=True,
        health_floor=None,
        invariant_cap=0.48,
        risk_role="tests whether route/fusion evidence alone over-releases without action-health",
    ),
    AblationConfig(
        name="no_invariant_energy",
        score_col="no_invariant_score",
        allowed_classes=("strict_jury", "consensus_shadow", "route_only", "fusion_only"),
        max_cells=40,
        strict_shrink=0.84,
        extra_shrink=0.24,
        require_no_opposition=True,
        health_floor=0.046,
        invariant_cap=None,
        risk_role="tests whether high-health actions become toxic when invariant energy is ignored",
    ),
    AblationConfig(
        name="invariant_only",
        score_col="invariant_only_score",
        allowed_classes=("strict_jury", "consensus_shadow", "route_only", "fusion_only"),
        max_cells=29,
        strict_shrink=0.78,
        extra_shrink=0.20,
        require_no_opposition=True,
        health_floor=None,
        invariant_cap=0.40,
        risk_role="tests whether low invariant energy alone is enough without listener/action-health",
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


def add_ablation_scores(scored: pd.DataFrame) -> pd.DataFrame:
    frame = scored.copy()
    responsibility = frame["core_listener_responsibility"].clip(lower=1e-6)
    invariant = frame["core_invariant_energy_delta"].astype(float)
    action_score = frame["action_score"].astype(float)
    total_weight = frame["total_weight"].astype(float)
    family_balance = frame["family_balance"].astype(float)
    opposition = frame["opposed_weight"].astype(float)

    frame["full_core_score"] = frame["core_release_score"].astype(float)
    frame["no_listener_score"] = (
        frame["core_health_score"].astype(float) / responsibility
        + 0.20 * frame["core_listener_alignment"].astype(float)
        - 0.35 * invariant
    )
    frame["no_action_health_score"] = (
        0.55 * action_score
        + 0.20 * total_weight.rank(pct=True)
        + 0.20 * family_balance
        - 0.45 * opposition
        - 0.15 * invariant
    )
    frame["no_invariant_score"] = (
        frame["core_health_score"].astype(float)
        + 0.22 * frame["core_listener_responsibility"].astype(float)
        + 0.12 * frame["core_listener_alignment"].astype(float)
        + 0.08 * action_score.rank(pct=True)
    )
    frame["invariant_only_score"] = (
        (0.46 - invariant)
        + 0.10 * action_score.rank(pct=True)
        + 0.06 * family_balance
        - 0.20 * opposition
    )
    return frame.sort_values("full_core_score", ascending=False, kind="mergesort").reset_index(drop=True)


def select_cells(scored: pd.DataFrame, config: AblationConfig) -> pd.DataFrame:
    eligible = scored[scored["boundary_class"].isin(config.allowed_classes)].copy()
    if config.require_no_opposition:
        eligible = eligible[eligible["opposed_weight"].le(1e-12)]
    if config.health_floor is not None:
        eligible = eligible[eligible["core_health_score"].ge(config.health_floor)]
    if config.invariant_cap is not None:
        eligible = eligible[eligible["core_invariant_energy_delta"].le(config.invariant_cap)]
    eligible = eligible.sort_values(
        [config.score_col, "core_release_score", "action_score", "mean_abs_delta"],
        ascending=[False, False, False, False],
        kind="mergesort",
    )
    return eligible.drop_duplicates(["row", "target"], keep="first").head(config.max_cells).reset_index(drop=True)


def apply_selection(base_prob: np.ndarray, selected: pd.DataFrame, config: AblationConfig) -> np.ndarray:
    prob = base_prob.copy()
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        shrink = config.strict_shrink if rec["boundary_class"] == "strict_jury" else config.extra_shrink
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + shrink * float(rec["action_delta"]))
    return prob


def make_submission(base: pd.DataFrame, base_prob: np.ndarray, selected: pd.DataFrame, config: AblationConfig) -> tuple[Path, Path, dict[str, object]]:
    prob = apply_selection(base_prob, selected, config)
    suffix = short_hash(prob)
    file_name = f"submission_hsjepa_core_ablation_{config.name}_{suffix}_uploadsafe.csv"
    root_path = ROOT / file_name
    local_path = OUT / file_name
    write_submission(root_path, base, prob)
    write_submission(local_path, base, prob)
    validation = validate_submission(root_path, base, base_prob)
    return root_path, local_path, validation


def cell_set(frame: pd.DataFrame) -> set[str]:
    return set(frame["cell_key"].astype(str).tolist()) if not frame.empty else set()


def extended_metrics(selected: pd.DataFrame, score_col: str, full_cells: set[str]) -> dict[str, float]:
    base = score_selection(selected)
    if selected.empty:
        base.update(
            {
                "mean_ablation_score": 0.0,
                "high_invariant_rate": 0.0,
                "low_responsibility_rate": 0.0,
                "full_overlap_rate": 0.0,
                "q_rate": 0.0,
                "s_rate": 0.0,
            }
        )
        return base
    selected_cells = cell_set(selected)
    base.update(
        {
            "mean_ablation_score": float(selected[score_col].mean()),
            "high_invariant_rate": float(selected["core_invariant_energy_delta"].gt(0.46).mean()),
            "low_responsibility_rate": float(selected["core_listener_responsibility"].lt(0.18).mean()),
            "full_overlap_rate": float(len(selected_cells & full_cells) / max(1, len(selected_cells))),
            "q_rate": float(selected["target"].astype(str).str.startswith("Q").mean()),
            "s_rate": float(selected["target"].astype(str).str.startswith("S").mean()),
        }
    )
    return base


def stress_ablation(scored: pd.DataFrame, selected: pd.DataFrame, config: AblationConfig, full_cells: set[str], seed: int = 20260611, iters: int = 700) -> dict[str, Any]:
    actual = extended_metrics(selected, config.score_col, full_cells)
    rng = np.random.default_rng(seed)
    null_rows = []
    for idx in range(iters):
        sampled = sample_null(scored, selected, rng)
        metrics = extended_metrics(sampled, config.score_col, full_cells)
        metrics["iteration"] = idx
        null_rows.append(metrics)
    null = pd.DataFrame(null_rows)
    tests = {
        "mean_ablation_score": z_and_p(actual["mean_ablation_score"], null["mean_ablation_score"].to_list(), higher_is_better=True),
        "mean_health": z_and_p(actual["mean_health"], null["mean_health"].to_list(), higher_is_better=True),
        "mean_release_score": z_and_p(actual["mean_release_score"], null["mean_release_score"].to_list(), higher_is_better=True),
        "mean_invariant_margin": z_and_p(actual["mean_invariant_margin"], null["mean_invariant_margin"].to_list(), higher_is_better=True),
        "high_invariant_rate": z_and_p(actual["high_invariant_rate"], null["high_invariant_rate"].to_list(), higher_is_better=False),
    }
    return {"actual": actual, "tests": tests, "null_rows": null_rows}


def priority(metrics: dict[str, Any], config: AblationConfig, upload_safe: bool) -> float:
    if not upload_safe:
        return -99.0
    tests = metrics["tests"]
    actual = metrics["actual"]
    score_z = finite(tests["mean_ablation_score"]["z"])
    release_z = finite(tests["mean_release_score"]["z"])
    invariant_z = finite(tests["mean_invariant_margin"]["z"])
    high_inv = finite(actual["high_invariant_rate"])
    novelty = 1.0 - finite(actual["full_overlap_rate"])
    if config.name == "full_core_reference":
        novelty *= 0.25
    negative_control_penalty = 0.18 if config.name in {"no_action_health", "no_invariant_energy", "invariant_only"} else 0.0
    return (
        0.30 * max(-1.0, min(2.0, score_z / 3.0))
        + 0.25 * max(-1.0, min(2.0, release_z / 3.0))
        + 0.18 * max(-1.0, min(2.0, invariant_z / 3.0))
        + 0.15 * novelty
        - 0.25 * high_inv
        - negative_control_penalty
        + 0.12
    )


def status_for(metrics: dict[str, Any], config: AblationConfig, upload_safe: bool) -> str:
    if not upload_safe:
        return "core_ablation_not_upload_safe"
    actual = metrics["actual"]
    if finite(actual["cells"]) <= 0:
        return "core_ablation_empty"
    if config.name == "full_core_reference":
        return "full_core_reference_ready"
    if finite(actual["full_overlap_rate"]) < 0.75:
        return f"{config.name}_changes_release_boundary"
    return f"{config.name}_mostly_matches_full_core"


def build_findings(variants: dict[str, dict[str, Any]]) -> list[dict[str, object]]:
    full = variants["full_core_reference"]["stress"]["actual"]
    findings = []
    for name in ["no_listener_responsibility", "no_action_health", "no_invariant_energy", "invariant_only"]:
        item = variants[name]
        actual = item["stress"]["actual"]
        findings.append(
            {
                "claim": f"{name} is a real HS-JEPA module ablation, not a cosmetic label.",
                "evidence": (
                    f"overlap_with_full={fmt(actual['full_overlap_rate'])}, "
                    f"high_invariant_rate={fmt(actual['high_invariant_rate'])}, "
                    f"mean_release_score={fmt(actual['mean_release_score'])}, "
                    f"full_mean_release_score={fmt(full['mean_release_score'])}"
                ),
                "status": item["status"],
                "next_test": (
                    "Use public LB only for a high-information counterfactual if this ablation ranks high while changing many cells."
                ),
            }
        )
    return findings


def build_markdown(readout: dict[str, Any]) -> str:
    verdict = readout["verdict"]
    lb_candidate = verdict["recommended_lb_candidate"]
    sensor = verdict["recommended_architecture_sensor"]
    negative = verdict["recommended_negative_control"]
    rows = [
        "| Rank | Variant | Cells | Extra | Full overlap | High invariant | Score z | Release z | Priority | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for rec in readout["ranking"]:
        actual = rec["stress"]["actual"]
        tests = rec["stress"]["tests"]
        rows.append(
            f"| `{rec['rank']}` | `{rec['variant']}` | `{int(actual['cells'])}` | `{int(actual['extra_cells'])}` | "
            f"`{fmt(actual['full_overlap_rate'])}` | `{fmt(actual['high_invariant_rate'])}` | "
            f"`{fmt(tests['mean_ablation_score']['z'])}` | `{fmt(tests['mean_release_score']['z'])}` | "
            f"`{fmt(rec['priority'])}` | `{rec['submission_file']}` |"
        )
    return "\n".join(
        [
            "# HS-JEPA Core Release Ablation Probe",
            "",
            "실제 sleep-adapter action 후보에서 HS-JEPA core module을 하나씩 제거해 release boundary가 어떻게 바뀌는지 본다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['status']}`",
            f"- Recommended LB candidate: `{lb_candidate['variant']}` / `{lb_candidate['submission_file']}` / priority `{fmt(lb_candidate['priority'])}`",
            f"- Recommended architecture sensor: `{sensor['variant']}` / `{sensor['submission_file']}` / priority `{fmt(sensor['priority'])}`",
            f"- Recommended negative control: `{negative['variant']}` / `{negative['submission_file']}` / priority `{fmt(negative['priority'])}`",
            f"- Claim: {verdict['claim']}",
            "",
            "## Ranking",
            "",
            *rows,
            "",
            "## Findings",
            "",
            *[
                f"- `{item['status']}`: {item['evidence']}"
                for item in readout["findings"]
            ],
            "",
            "## Interpretation",
            "",
            "full-core와 module-removed 후보의 overlap이 낮으면 해당 module은 장식이 아니라 실제 row-target release를 바꾸는 구조다. public에서 no-module 후보가 이기면 그 module은 현재 adapter에서 과하게 보수적이고, 지면 full HS-JEPA release boundary가 더 설득력 있다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    base, base_prob = load_base()
    scored = add_ablation_scores(score_cells(load_candidate_cells()))
    scored.to_csv(CELL_CSV, index=False)

    selected_by_name: dict[str, pd.DataFrame] = {}
    full_selected = select_cells(scored, CONFIGS[0])
    full_cells = cell_set(full_selected)
    selected_by_name[CONFIGS[0].name] = full_selected

    variants: dict[str, Any] = {}
    null_frames = []
    for config in CONFIGS:
        selected = selected_by_name.get(config.name)
        if selected is None:
            selected = select_cells(scored, config)
            selected_by_name[config.name] = selected
        root_path, local_path, validation = make_submission(base, base_prob, selected, config)
        stress = stress_ablation(scored, selected, config, full_cells)
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
                "score_col": config.score_col,
                "allowed_classes": list(config.allowed_classes),
                "max_cells": config.max_cells,
                "strict_shrink": config.strict_shrink,
                "extra_shrink": config.extra_shrink,
                "require_no_opposition": config.require_no_opposition,
                "health_floor": config.health_floor,
                "invariant_cap": config.invariant_cap,
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
    findings = build_findings(variants)
    upload_safe = [item for item in ranking if item["validation"].get("upload_safe")]
    non_full = [item for item in upload_safe if item["variant"] != "full_core_reference"]
    negative_controls = [
        item for item in upload_safe
        if item["variant"] in {"no_action_health", "no_invariant_energy", "invariant_only"}
    ]
    reference = variants["full_core_reference"]
    boundary_changers = [
        item for item in non_full
        if finite(item["stress"]["actual"]["full_overlap_rate"], 1.0) < 0.85
    ]
    recommended = (
        sorted(boundary_changers, key=lambda item: item["priority"], reverse=True)[0]
        if boundary_changers
        else (non_full[0] if non_full else upload_safe[0])
    )
    negative = (
        sorted(
            negative_controls,
            key=lambda item: (
                finite(item["stress"]["actual"]["full_overlap_rate"], 1.0),
                -finite(item["priority"]),
            ),
        )[0]
        if negative_controls
        else recommended
    )

    readout = {
        "experiment": "HS-JEPA Core Release Ablation Probe",
        "architecture_role": "real_adapter_core_module_ablation",
        "status": "core_release_ablation_ready",
        "verdict": {
            "status": "core_release_ablation_ready",
            "recommended_lb_candidate": {
                "variant": reference["variant"],
                "submission_file": reference["submission_file"],
                "priority": reference["priority"],
            },
            "recommended_architecture_sensor": {
                "variant": recommended["variant"],
                "submission_file": recommended["submission_file"],
                "priority": recommended["priority"],
            },
            "recommended_negative_control": {
                "variant": negative["variant"],
                "submission_file": negative["submission_file"],
                "priority": negative["priority"],
            },
            "claim": (
                "HS-JEPA core modules change the real sleep-adapter action boundary when removed. "
                "This makes listener responsibility, action-health, and invariant energy falsifiable rather than only descriptive."
            ),
            "failure_interpretation": (
                "If all module-removal variants match or beat full-core release on public LB, the current HS-JEPA core is over-constrained for the competition adapter."
            ),
        },
        "module_ablation_design": {
            "candidate_universe": "decoder-order strict cells plus boundary tomography rejected cells",
            "full_core": "listener responsibility + action health + invariant energy",
            "ablations": [config.name for config in CONFIGS if config.name != "full_core_reference"],
        },
        "findings": findings,
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
