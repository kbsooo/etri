#!/usr/bin/env python3
"""Core-mediated action release for the sleep competition adapter.

This is the first adapter module that explicitly routes real row-target action
candidates through the reusable HS-JEPA core API.  The core stays generic; this
adapter converts route/fusion/boundary statistics into context views, listener
prototypes, and candidate actions.

Question tested:

    Does the generic HS-JEPA release rule agree with, sharpen, or contradict
    the competition-specific decoder-order jury?

If this works on public LB, HS-JEPA is not only a report structure.  The core
release mechanism itself is useful for deciding which sleep-adapter actions
should be allowed through.
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

from hsjepa_core.core import CandidateAction, ContextView, HSJEPACore, ListenerPrototype  # noqa: E402
from sleep_competition_adapter.decoder_order_jury_solver import load_base, z_and_p  # noqa: E402
from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (  # noqa: E402
    TARGETS,
    clip_prob,
    short_hash,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "core_mediated_action_release"
OUT.mkdir(parents=True, exist_ok=True)

STRICT_CELLS = HERE / "outputs" / "decoder_order_jury_solver" / "decoder_order_jury_cells.csv"
BOUNDARY_CELLS = HERE / "outputs" / "decoder_boundary_tomography_solver" / "decoder_boundary_tomography_cells.csv"

READOUT_JSON = OUT / "core_mediated_action_release_readout.json"
READOUT_MD = OUT / "core_mediated_action_release_readout_ko.md"
CELL_CSV = OUT / "core_mediated_action_release_cells.csv"
NULL_CSV = OUT / "core_mediated_action_release_null_stress.csv"


@dataclass(frozen=True)
class CoreReleaseConfig:
    name: str
    include_boundary_classes: tuple[str, ...]
    max_strict_cells: int
    max_extra_cells: int
    strict_shrink: float
    extra_shrink: float
    health_threshold: float
    invariant_threshold: float
    risk_role: str


CONFIGS = [
    CoreReleaseConfig(
        name="core_jury_veto",
        include_boundary_classes=(),
        max_strict_cells=24,
        max_extra_cells=0,
        strict_shrink=0.92,
        extra_shrink=0.00,
        health_threshold=0.060,
        invariant_threshold=0.42,
        risk_role="tests whether generic core vetoes any strict jury cells",
    ),
    CoreReleaseConfig(
        name="core_consensus_shadow_plus",
        include_boundary_classes=("consensus_shadow",),
        max_strict_cells=24,
        max_extra_cells=10,
        strict_shrink=0.92,
        extra_shrink=0.42,
        health_threshold=0.052,
        invariant_threshold=0.44,
        risk_role="tests whether generic core can safely release weak cross-decoder consensus",
    ),
    CoreReleaseConfig(
        name="core_route_rescue",
        include_boundary_classes=("route_only",),
        max_strict_cells=24,
        max_extra_cells=5,
        strict_shrink=0.92,
        extra_shrink=0.34,
        health_threshold=0.048,
        invariant_threshold=0.46,
        risk_role="tests whether generic core rescues route-only cells vetoed by action-health",
    ),
    CoreReleaseConfig(
        name="core_boundary_balanced",
        include_boundary_classes=("consensus_shadow", "route_only", "fusion_only"),
        max_strict_cells=24,
        max_extra_cells=12,
        strict_shrink=0.90,
        extra_shrink=0.28,
        health_threshold=0.050,
        invariant_threshold=0.45,
        risk_role="tests whether generic core can arbitrate all boundary classes together",
    ),
]


LISTENERS = [
    ListenerPrototype("subjective_listener", (0.76, 0.22, 0.04, 0.02), sensitivity=1.00),
    ListenerPrototype("objective_listener", (0.12, 0.24, 0.58, 0.06), sensitivity=0.96),
    ListenerPrototype("boundary_listener", (0.34, 0.34, 0.20, 0.12), sensitivity=0.82),
]


CLASS_PRIOR = {
    "strict_jury": 1.00,
    "consensus_shadow": 0.74,
    "route_only": 0.52,
    "fusion_only": 0.40,
    "conflict": 0.10,
}

CLASS_UNCERTAINTY = {
    "strict_jury": 0.05,
    "consensus_shadow": 0.13,
    "route_only": 0.24,
    "fusion_only": 0.30,
    "conflict": 0.55,
}


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


def normalize01(value: float, max_value: float) -> float:
    if max_value <= 1e-12:
        return 0.0
    return max(0.0, min(1.0, value / max_value))


def listener_for_target(target: str) -> str:
    return "subjective_listener" if target.startswith("Q") else "objective_listener"


def target_group_scalar(target: str) -> float:
    return 0.25 if target.startswith("Q") else 0.75


def load_candidate_cells() -> pd.DataFrame:
    if not STRICT_CELLS.exists():
        raise FileNotFoundError(STRICT_CELLS)
    if not BOUNDARY_CELLS.exists():
        raise FileNotFoundError(BOUNDARY_CELLS)

    strict = pd.read_csv(STRICT_CELLS)
    strict = strict[strict["config"].eq("family_supermajority")].copy()
    strict["boundary_class"] = "strict_jury"
    strict["opposed_weight"] = 0.0
    strict["source_table"] = "decoder_order_jury"
    strict["action_delta"] = strict["released_delta"].astype(float)
    strict["action_score"] = strict["consensus_score"].astype(float)

    boundary = pd.read_csv(BOUNDARY_CELLS).copy()
    boundary = boundary[boundary["boundary_class"].isin(["consensus_shadow", "route_only", "fusion_only", "conflict"])].copy()
    boundary["source_table"] = "decoder_boundary_tomography"
    boundary["action_delta"] = boundary["weighted_delta"].astype(float)
    boundary["action_score"] = boundary["boundary_score"].astype(float)

    cols = [
        "row",
        "target",
        "target_idx",
        "cell_key",
        "boundary_class",
        "direction",
        "opposed_weight",
        "route_votes",
        "fusion_votes",
        "total_votes",
        "route_weight",
        "fusion_weight",
        "total_weight",
        "family_balance",
        "vote_coverage",
        "mean_abs_delta",
        "weighted_delta",
        "action_delta",
        "action_score",
        "files",
        "source_table",
    ]
    cells = pd.concat([strict[cols], boundary[cols]], ignore_index=True)
    cells = cells.drop_duplicates(["cell_key", "boundary_class"], keep="first")
    return cells.reset_index(drop=True)


def contexts_for_cell(row: pd.Series, maxes: dict[str, float]) -> list[ContextView]:
    boundary_class = str(row["boundary_class"])
    prior = CLASS_PRIOR.get(boundary_class, 0.20)
    uncertainty = CLASS_UNCERTAINTY.get(boundary_class, 0.40)
    route_strength = normalize01(finite(row["route_weight"]), maxes["route_weight"])
    fusion_strength = normalize01(finite(row["fusion_weight"]), maxes["fusion_weight"])
    total_strength = normalize01(finite(row["total_weight"]), maxes["total_weight"])
    abs_strength = normalize01(finite(row["mean_abs_delta"]), maxes["mean_abs_delta"])
    no_conflict = 1.0 if finite(row["opposed_weight"]) <= 1e-12 else 0.0
    balance = max(0.0, min(1.0, finite(row["family_balance"])))
    coverage = max(0.0, min(1.0, finite(row["vote_coverage"])))
    group = target_group_scalar(str(row["target"]))
    return [
        ContextView(
            "route_invariant_context",
            (route_strength, coverage, abs_strength, group),
            coverage=coverage,
            uncertainty=uncertainty,
        ),
        ContextView(
            "action_health_context",
            (fusion_strength, balance, no_conflict, prior),
            coverage=0.50 + 0.50 * balance,
            uncertainty=uncertainty + 0.10 * (1.0 - no_conflict),
        ),
        ContextView(
            "boundary_consensus_context",
            (total_strength, prior, no_conflict, 1.0 - uncertainty),
            coverage=0.50 + 0.50 * total_strength,
            uncertainty=0.5 * uncertainty,
        ),
    ]


def action_for_cell(row: pd.Series, maxes: dict[str, float]) -> CandidateAction:
    target = str(row["target"])
    listener = listener_for_target(target)
    abs_strength = normalize01(finite(row["mean_abs_delta"]), maxes["mean_abs_delta"])
    total_strength = normalize01(finite(row["total_weight"]), maxes["total_weight"])
    route_strength = normalize01(finite(row["route_weight"]), maxes["route_weight"])
    fusion_strength = normalize01(finite(row["fusion_weight"]), maxes["fusion_weight"])
    if listener == "subjective_listener":
        embedding = (0.78, 0.20, 0.04 + 0.10 * abs_strength, 0.02)
    else:
        embedding = (0.10 + 0.10 * route_strength, 0.22, 0.58, 0.10 + 0.05 * fusion_strength)
    support = max(0.02, total_strength * (0.55 + 0.45 * finite(row["family_balance"])))
    amplitude = max(0.05, min(1.20, abs(finite(row["action_delta"])) / max(maxes["mean_abs_delta"], 1e-12)))
    return CandidateAction(
        name=str(row["cell_key"]),
        listener=listener,
        delta_embedding=embedding,
        amplitude=amplitude,
        support=support,
    )


def score_cells(cells: pd.DataFrame) -> pd.DataFrame:
    maxes = {
        "route_weight": max(float(cells["route_weight"].max()), 1e-12),
        "fusion_weight": max(float(cells["fusion_weight"].max()), 1e-12),
        "total_weight": max(float(cells["total_weight"].max()), 1e-12),
        "mean_abs_delta": max(float(cells["mean_abs_delta"].max()), 1e-12),
    }
    core = HSJEPACore(
        responsibility_temperature=0.38,
        health_release_threshold=0.050,
        invariant_release_threshold=0.46,
    )
    scored = []
    for rec in cells.to_dict("records"):
        row = pd.Series(rec)
        contexts = contexts_for_cell(row, maxes)
        action = action_for_cell(row, maxes)
        hidden = core.predict_hidden_state(contexts)
        responsibilities = core.listener_responsibility(hidden, LISTENERS)
        decision = core.score_action(hidden, LISTENERS, responsibilities, action, [ctx.embedding for ctx in contexts])
        out = dict(rec)
        out.update(
            {
                "core_listener": action.listener,
                "core_prediction_energy": hidden.prediction_energy,
                "core_context_coverage": hidden.context_coverage,
                "core_context_disagreement": hidden.context_disagreement,
                "core_listener_responsibility": decision.listener_responsibility,
                "core_listener_alignment": decision.listener_alignment,
                "core_invariant_energy_delta": decision.invariant_energy_delta,
                "core_health_score": decision.health_score,
                "core_default_released": bool(decision.released),
                "core_release_score": (
                    decision.health_score
                    + 0.25 * decision.listener_responsibility
                    + 0.15 * decision.listener_alignment
                    - 0.40 * decision.invariant_energy_delta
                    - 0.20 * hidden.prediction_energy
                ),
            }
        )
        scored.append(out)
    frame = pd.DataFrame(scored)
    frame = frame.sort_values(
        ["core_release_score", "core_health_score", "action_score", "mean_abs_delta"],
        ascending=[False, False, False, False],
        kind="mergesort",
    ).reset_index(drop=True)
    return frame


def selected_for_config(scored: pd.DataFrame, config: CoreReleaseConfig) -> pd.DataFrame:
    strict = scored[scored["boundary_class"].eq("strict_jury")].copy()
    strict = strict[
        strict["core_health_score"].ge(config.health_threshold * 0.82)
        & strict["core_invariant_energy_delta"].le(config.invariant_threshold)
    ].head(config.max_strict_cells)

    if not config.include_boundary_classes or config.max_extra_cells <= 0:
        selected = strict
    else:
        extra = scored[scored["boundary_class"].isin(config.include_boundary_classes)].copy()
        extra = extra[
            extra["core_health_score"].ge(config.health_threshold)
            & extra["core_invariant_energy_delta"].le(config.invariant_threshold)
            & extra["opposed_weight"].le(1e-12)
        ].head(config.max_extra_cells)
        selected = pd.concat([strict, extra], ignore_index=True)
    return selected.drop_duplicates(["row", "target"], keep="first").reset_index(drop=True)


def apply_selection(base_prob: np.ndarray, selected: pd.DataFrame, config: CoreReleaseConfig) -> np.ndarray:
    prob = base_prob.copy()
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        shrink = config.strict_shrink if rec["boundary_class"] == "strict_jury" else config.extra_shrink
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + shrink * float(rec["action_delta"]))
    return prob


def score_selection(selected: pd.DataFrame) -> dict[str, float]:
    if selected.empty:
        return {
            "cells": 0.0,
            "rows": 0.0,
            "extra_cells": 0.0,
            "mean_health": 0.0,
            "mean_responsibility": 0.0,
            "mean_release_score": 0.0,
            "mean_invariant_margin": 0.0,
            "strict_rate": 0.0,
            "shadow_rate": 0.0,
            "route_only_rate": 0.0,
            "fusion_only_rate": 0.0,
        }
    return {
        "cells": float(len(selected)),
        "rows": float(selected["row"].nunique()),
        "extra_cells": float((~selected["boundary_class"].eq("strict_jury")).sum()),
        "mean_health": float(selected["core_health_score"].mean()),
        "mean_responsibility": float(selected["core_listener_responsibility"].mean()),
        "mean_release_score": float(selected["core_release_score"].mean()),
        "mean_invariant_margin": float((0.46 - selected["core_invariant_energy_delta"]).mean()),
        "strict_rate": float(selected["boundary_class"].eq("strict_jury").mean()),
        "shadow_rate": float(selected["boundary_class"].eq("consensus_shadow").mean()),
        "route_only_rate": float(selected["boundary_class"].eq("route_only").mean()),
        "fusion_only_rate": float(selected["boundary_class"].eq("fusion_only").mean()),
    }


def sample_null(scored: pd.DataFrame, selected: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    if selected.empty:
        return selected
    rows = []
    for cls, cls_df in selected.groupby("boundary_class", sort=False):
        pool = scored[scored["boundary_class"].eq(cls)]
        if pool.empty:
            pool = scored
        for target, count in cls_df["target"].value_counts().to_dict().items():
            target_pool = pool[pool["target"].eq(target)]
            if target_pool.empty:
                target_pool = pool
            rows.append(
                target_pool.sample(
                    n=int(count),
                    replace=len(target_pool) < int(count),
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )
            )
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def stress_selection(scored: pd.DataFrame, selected: pd.DataFrame, seed: int = 20260610, iters: int = 700) -> dict[str, Any]:
    actual = score_selection(selected)
    rng = np.random.default_rng(seed)
    null_rows = []
    for idx in range(iters):
        sampled = sample_null(scored, selected, rng)
        metrics = score_selection(sampled)
        metrics["iteration"] = idx
        null_rows.append(metrics)
    null = pd.DataFrame(null_rows)
    tests = {}
    for key in ["mean_health", "mean_responsibility", "mean_release_score", "mean_invariant_margin"]:
        tests[key] = z_and_p(actual[key], null[key].to_list(), higher_is_better=True)
    return {"actual": actual, "tests": tests, "null_rows": null_rows}


def make_submission(base: pd.DataFrame, base_prob: np.ndarray, selected: pd.DataFrame, config: CoreReleaseConfig) -> tuple[Path, Path, dict[str, object]]:
    prob = apply_selection(base_prob, selected, config)
    suffix = short_hash(prob)
    file_name = f"submission_hsjepa_core_mediated_{config.name}_{suffix}_uploadsafe.csv"
    root_path = ROOT / file_name
    local_path = OUT / file_name
    write_submission(root_path, base, prob)
    write_submission(local_path, base, prob)
    validation = validate_submission(root_path, base, base_prob)
    return root_path, local_path, validation


def priority(metrics: dict[str, Any], config: CoreReleaseConfig, upload_safe: bool) -> float:
    if not upload_safe:
        return -99.0
    tests = metrics["tests"]
    actual = metrics["actual"]
    health_z = finite(tests["mean_health"]["z"])
    release_z = finite(tests["mean_release_score"]["z"])
    invariant_z = finite(tests["mean_invariant_margin"]["z"])
    extra_cells = finite(actual["extra_cells"])
    extra_bonus = min(extra_cells, 10.0) / 10.0
    risk_bonus = 0.18 if config.include_boundary_classes == ("consensus_shadow",) else 0.08 if not config.include_boundary_classes else 0.02
    return (
        0.32 * max(-1.0, min(2.0, release_z / 3.0))
        + 0.24 * max(-1.0, min(2.0, health_z / 3.0))
        + 0.18 * max(-1.0, min(2.0, invariant_z / 3.0))
        + 0.14 * extra_bonus
        + 0.12
        + risk_bonus
    )


def status_for(metrics: dict[str, Any], config: CoreReleaseConfig, upload_safe: bool) -> str:
    if not upload_safe:
        return "core_mediated_release_not_upload_safe"
    actual = metrics["actual"]
    tests = metrics["tests"]
    if finite(actual["cells"]) <= 0:
        return "core_mediated_release_empty"
    release_z = finite(tests["mean_release_score"]["z"])
    if config.include_boundary_classes == ("consensus_shadow",) and finite(actual["extra_cells"]) > 0 and release_z >= 1.0:
        return "core_mediated_shadow_release_alive"
    if not config.include_boundary_classes and release_z >= 1.0:
        return "core_mediated_jury_veto_alive"
    if "route_only" in config.include_boundary_classes and finite(actual["extra_cells"]) > 0:
        return "core_mediated_route_rescue_sensor"
    return "core_mediated_boundary_diagnostic"


def build_markdown(readout: dict[str, Any]) -> str:
    rows = [
        "| Rank | Variant | Cells | Extra | Health z | Release z | Invariant z | Priority | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for rec in readout["ranking"]:
        tests = rec["stress"]["tests"]
        actual = rec["stress"]["actual"]
        rows.append(
            f"| `{rec['rank']}` | `{rec['variant']}` | `{int(actual['cells'])}` | `{int(actual['extra_cells'])}` | "
            f"`{fmt(tests['mean_health']['z'])}` | `{fmt(tests['mean_release_score']['z'])}` | "
            f"`{fmt(tests['mean_invariant_margin']['z'])}` | `{fmt(rec['priority'])}` | `{rec['submission_file']}` |"
        )
    verdict = readout["verdict"]
    sensor = verdict["recommended_lb_sensor"]
    return "\n".join(
        [
            "# HS-JEPA Core-Mediated Action Release",
            "",
            "이 실험은 실제 sleep adapter의 row-target action 후보를 HS-JEPA core API로 변환해 release/veto를 받는다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{verdict['status']}`",
            f"- Recommended LB sensor: `{sensor['variant']}` -> `{sensor['submission_file']}`",
            f"- Claim: {verdict['claim']}",
            f"- Failure interpretation: {verdict['failure_interpretation']}",
            "",
            "## Ranking",
            "",
            *rows,
            "",
            "## Architecture Meaning",
            "",
            "이 probe가 public에서 살아나면 HS-JEPA core의 listener/action-health/invariant release rule이 실제 대회 adapter의 action boundary에도 유효하다는 뜻이다.",
            "반대로 죽으면 현재 core reference는 설명용 구조로는 유효하지만, sleep adapter의 최고 LB decoder는 아직 더 특수한 release equation을 필요로 한다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    base, base_prob = load_base()
    cells = load_candidate_cells()
    scored = score_cells(cells)
    scored.to_csv(CELL_CSV, index=False)

    variants: dict[str, Any] = {}
    null_frames = []
    for config in CONFIGS:
        selected = selected_for_config(scored, config)
        root_path, local_path, validation = make_submission(base, base_prob, selected, config)
        stress = stress_selection(scored, selected)
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
                "include_boundary_classes": list(config.include_boundary_classes),
                "max_strict_cells": config.max_strict_cells,
                "max_extra_cells": config.max_extra_cells,
                "strict_shrink": config.strict_shrink,
                "extra_shrink": config.extra_shrink,
                "health_threshold": config.health_threshold,
                "invariant_threshold": config.invariant_threshold,
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

    recommended = next((item for item in ranking if item["validation"].get("upload_safe")), ranking[0])
    status = "core_mediated_action_release_ready"
    readout = {
        "experiment": "HS-JEPA Core-Mediated Action Release",
        "architecture_role": "sleep_adapter_to_hsjepa_core_api_probe",
        "core_api_used": {
            "ContextView": "route/action-health/boundary contexts",
            "ListenerPrototype": "subjective/objective/boundary listeners",
            "CandidateAction": "row-target probability move as bounded action",
            "HSJEPACore": "listener responsibility, action-health, invariant release",
        },
        "status": status,
        "verdict": {
            "status": status,
            "recommended_lb_sensor": {
                "variant": recommended["variant"],
                "submission_file": recommended["submission_file"],
                "priority": recommended["priority"],
            },
            "claim": (
                "Real sleep-adapter row-target actions can be routed through the generic HS-JEPA core. "
                "The public sensor should reveal whether generic core release sharpens the strict decoder jury."
            ),
            "failure_interpretation": (
                "If core-mediated candidates underperform, the current HS-JEPA core is architecturally useful but "
                "not yet the action-grade release equation for this competition adapter."
            ),
        },
        "cell_inventory": {
            "candidate_cells": int(len(scored)),
            "strict_cells": int(scored["boundary_class"].eq("strict_jury").sum()),
            "consensus_shadow_cells": int(scored["boundary_class"].eq("consensus_shadow").sum()),
            "route_only_cells": int(scored["boundary_class"].eq("route_only").sum()),
            "fusion_only_cells": int(scored["boundary_class"].eq("fusion_only").sum()),
            "default_core_released": int(scored["core_default_released"].sum()),
        },
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
