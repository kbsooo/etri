#!/usr/bin/env python3
"""Boundary tomography solver for HS-JEPA sleep adapter.

This module asks what the decoder-order jury is throwing away.

It is adapter code, not HS-JEPA core code.  The reusable architecture says that
hidden human-state should pass through listener responsibility, action-health,
and invariant-energy decoders before release.  This competition adapter turns
that idea into a concrete question:

    Are cells rejected by strict cross-decoder consensus toxic, or merely weak?

The solver creates upload-safe sensor submissions for three boundary worlds:

1. consensus_shadow_plus: route and fusion agree, but strict jury was too
   conservative.
2. route_only_rescue: invariant route says act, while action-health is silent.
3. fusion_only_probe: action-health says act, while route invariant is silent.

These are not safe defaults.  They are high-information public-LB sensors for
the next HS-JEPA action-decoder ablation.
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

from sleep_competition_adapter.decoder_order_jury_solver import (
    FUSION_FILES,
    ROUTE_FILES,
    collect_changes,
    finite,
    load_base,
    load_suite_weights,
    z_and_p,
)
from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (
    TARGETS,
    clip_prob,
    short_hash,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "decoder_boundary_tomography_solver"
OUT.mkdir(parents=True, exist_ok=True)

STRICT_JURY_CELLS = HERE / "outputs" / "decoder_order_jury_solver" / "decoder_order_jury_cells.csv"

READOUT_JSON = OUT / "decoder_boundary_tomography_readout.json"
READOUT_MD = OUT / "decoder_boundary_tomography_readout_ko.md"
CELL_CSV = OUT / "decoder_boundary_tomography_cells.csv"
NULL_CSV = OUT / "decoder_boundary_tomography_null_stress.csv"


@dataclass(frozen=True)
class BoundaryConfig:
    name: str
    include_classes: tuple[str, ...]
    max_extra_cells: int
    extra_shrink: float
    strict_shrink: float
    risk_role: str


CONFIGS = [
    BoundaryConfig(
        name="consensus_shadow_plus",
        include_classes=("consensus_shadow",),
        max_extra_cells=8,
        extra_shrink=0.45,
        strict_shrink=1.00,
        risk_role="tests whether strict jury is too conservative",
    ),
    BoundaryConfig(
        name="consensus_shadow_all_soft",
        include_classes=("consensus_shadow",),
        max_extra_cells=18,
        extra_shrink=0.32,
        strict_shrink=1.00,
        risk_role="tests whether all weak cross-decoder consensus cells are useful when softened",
    ),
    BoundaryConfig(
        name="route_only_rescue",
        include_classes=("route_only",),
        max_extra_cells=4,
        extra_shrink=0.36,
        strict_shrink=1.00,
        risk_role="tests whether action-health gate is over-vetoing invariant route actions",
    ),
    BoundaryConfig(
        name="fusion_only_probe",
        include_classes=("fusion_only",),
        max_extra_cells=4,
        extra_shrink=0.34,
        strict_shrink=1.00,
        risk_role="tests whether action-health alone can safely add cells without route support",
    ),
    BoundaryConfig(
        name="boundary_dual_probe",
        include_classes=("route_only", "fusion_only"),
        max_extra_cells=6,
        extra_shrink=0.26,
        strict_shrink=1.00,
        risk_role="tests whether disagreement cells contain complementary upside instead of toxicity",
    ),
]


def fmt(value: Any, digits: int = 4) -> str:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return "n/a"
    return f"{out:.{digits}f}" if math.isfinite(out) else "n/a"


def load_strict_jury_cells() -> pd.DataFrame:
    if not STRICT_JURY_CELLS.exists():
        raise FileNotFoundError(STRICT_JURY_CELLS)
    cells = pd.read_csv(STRICT_JURY_CELLS)
    cells = cells[cells["config"].eq("family_supermajority")].copy()
    if cells.empty:
        raise ValueError("family_supermajority cells are missing from decoder_order_jury_cells.csv")
    return cells


def cell_stats(changes: pd.DataFrame, strict_cells: pd.DataFrame) -> pd.DataFrame:
    strict_keys = set(strict_cells["cell_key"].astype(str))
    rows: list[dict[str, Any]] = []
    for cell_key, group in changes.groupby("cell_key", sort=False):
        route = group[group["file"].isin(ROUTE_FILES)]
        fusion = group[group["file"].isin(FUSION_FILES)]
        pos_weight = float(group.loc[group["sign"].eq(1), "priority"].sum())
        neg_weight = float(group.loc[group["sign"].eq(-1), "priority"].sum())
        direction = 1 if pos_weight >= neg_weight else -1
        opposed_weight = neg_weight if direction == 1 else pos_weight
        agreed = group[group["sign"].eq(direction)].copy()
        route_agreed = route[route["sign"].eq(direction)]
        fusion_agreed = fusion[fusion["sign"].eq(direction)]
        if agreed.empty:
            continue

        route_weight = float(route_agreed["priority"].sum())
        fusion_weight = float(fusion_agreed["priority"].sum())
        total_weight = float(agreed["priority"].sum())
        route_votes = int(len(route_agreed))
        fusion_votes = int(len(fusion_agreed))
        total_votes = int(len(agreed))
        balance = 2.0 * min(route_weight, fusion_weight) / max(route_weight + fusion_weight, 1e-12)
        vote_coverage = 0.5 * (route_votes / len(ROUTE_FILES) + fusion_votes / len(FUSION_FILES))
        weighted_delta = float(np.average(agreed["delta"].to_numpy(dtype=np.float64), weights=agreed["priority"].to_numpy(dtype=np.float64)))
        mean_abs_delta = float(agreed["abs_delta"].mean())

        if route_votes and fusion_votes and opposed_weight <= 1e-12:
            boundary_class = "strict_jury" if cell_key in strict_keys else "consensus_shadow"
        elif route_votes and not fusion_votes:
            boundary_class = "route_only"
        elif fusion_votes and not route_votes:
            boundary_class = "fusion_only"
        else:
            boundary_class = "conflict"

        score = total_weight * (0.35 + 0.65 * balance) * (0.35 + 0.65 * vote_coverage) * (0.75 + mean_abs_delta)
        first = group.iloc[0]
        rows.append(
            {
                "row": int(first["row"]),
                "target": str(first["target"]),
                "target_idx": int(first["target_idx"]),
                "cell_key": str(cell_key),
                "boundary_class": boundary_class,
                "direction": int(direction),
                "opposed_weight": float(opposed_weight),
                "route_votes": route_votes,
                "fusion_votes": fusion_votes,
                "total_votes": total_votes,
                "route_weight": route_weight,
                "fusion_weight": fusion_weight,
                "total_weight": total_weight,
                "family_balance": float(balance),
                "vote_coverage": float(vote_coverage),
                "mean_abs_delta": mean_abs_delta,
                "weighted_delta": weighted_delta,
                "boundary_score": float(score),
                "files": ",".join(sorted(agreed["file"].unique())),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out.sort_values(
        ["boundary_class", "boundary_score", "total_votes", "mean_abs_delta"],
        ascending=[True, False, False, False],
        kind="mergesort",
    ).reset_index(drop=True)


def choose_extra_cells(stats: pd.DataFrame, config: BoundaryConfig) -> pd.DataFrame:
    extra = stats[stats["boundary_class"].isin(config.include_classes)].copy()
    extra = extra[extra["opposed_weight"].le(1e-12)]
    if extra.empty:
        return extra
    if set(config.include_classes) == {"route_only", "fusion_only"}:
        parts = []
        per_class = max(1, config.max_extra_cells // 2)
        for cls in config.include_classes:
            parts.append(
                extra[extra["boundary_class"].eq(cls)].sort_values(
                    ["boundary_score", "mean_abs_delta"], ascending=[False, False], kind="mergesort"
                ).head(per_class)
            )
        extra = pd.concat(parts, ignore_index=True)
    else:
        extra = extra.sort_values(["boundary_score", "mean_abs_delta"], ascending=[False, False], kind="mergesort")
    return extra.head(config.max_extra_cells).reset_index(drop=True)


def apply_cells(
    base_prob: np.ndarray,
    strict_cells: pd.DataFrame,
    extra_cells: pd.DataFrame,
    config: BoundaryConfig,
) -> np.ndarray:
    prob = base_prob.copy()
    for rec in strict_cells.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + config.strict_shrink * float(rec["released_delta"]))
    for rec in extra_cells.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + config.extra_shrink * float(rec["weighted_delta"]))
    return prob


def score_selection(extra: pd.DataFrame) -> dict[str, float]:
    if extra.empty:
        return {
            "extra_cells": 0,
            "extra_rows": 0,
            "mean_boundary_score": 0.0,
            "mean_total_weight": 0.0,
            "mean_route_weight": 0.0,
            "mean_fusion_weight": 0.0,
            "mean_family_balance": 0.0,
            "mean_vote_coverage": 0.0,
            "mean_abs_delta": 0.0,
            "route_only_rate": 0.0,
            "fusion_only_rate": 0.0,
            "consensus_shadow_rate": 0.0,
        }
    return {
        "extra_cells": int(len(extra)),
        "extra_rows": int(extra["row"].nunique()),
        "mean_boundary_score": float(extra["boundary_score"].mean()),
        "mean_total_weight": float(extra["total_weight"].mean()),
        "mean_route_weight": float(extra["route_weight"].mean()),
        "mean_fusion_weight": float(extra["fusion_weight"].mean()),
        "mean_family_balance": float(extra["family_balance"].mean()),
        "mean_vote_coverage": float(extra["vote_coverage"].mean()),
        "mean_abs_delta": float(extra["mean_abs_delta"].mean()),
        "route_only_rate": float(extra["boundary_class"].eq("route_only").mean()),
        "fusion_only_rate": float(extra["boundary_class"].eq("fusion_only").mean()),
        "consensus_shadow_rate": float(extra["boundary_class"].eq("consensus_shadow").mean()),
    }


def sample_null(stats: pd.DataFrame, selected: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    if selected.empty:
        return selected
    rows = []
    for cls, count in selected["boundary_class"].value_counts().to_dict().items():
        pool = stats[stats["boundary_class"].eq(cls)]
        if pool.empty:
            pool = stats
        target_counts = selected[selected["boundary_class"].eq(cls)]["target"].value_counts().to_dict()
        for target, target_count in target_counts.items():
            target_pool = pool[pool["target"].eq(target)]
            if target_pool.empty:
                target_pool = pool
            rows.append(
                target_pool.sample(
                    n=int(target_count),
                    replace=len(target_pool) < int(target_count),
                    random_state=int(rng.integers(0, 2**31 - 1)),
                )
            )
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def stress_selection(stats: pd.DataFrame, selected: pd.DataFrame, seed: int = 20260610, iters: int = 700) -> dict[str, Any]:
    actual = score_selection(selected)
    rng = np.random.default_rng(seed)
    null_rows = []
    pool = stats[stats["boundary_class"].isin(["consensus_shadow", "route_only", "fusion_only"])]
    for idx in range(iters):
        sampled = sample_null(pool, selected, rng)
        metrics = score_selection(sampled)
        metrics["iteration"] = idx
        null_rows.append(metrics)
    null = pd.DataFrame(null_rows)
    tests = {}
    if not null.empty:
        for key in [
            "mean_boundary_score",
            "mean_total_weight",
            "mean_family_balance",
            "mean_vote_coverage",
            "mean_abs_delta",
        ]:
            tests[key] = z_and_p(actual[key], null[key].to_list(), higher_is_better=True)
    return {"actual": actual, "tests": tests, "null_rows": null_rows}


def make_submission(base: pd.DataFrame, base_prob: np.ndarray, strict_cells: pd.DataFrame, extra: pd.DataFrame, config: BoundaryConfig) -> tuple[Path, Path, dict[str, object]]:
    prob = apply_cells(base_prob, strict_cells, extra, config)
    suffix = short_hash(prob)
    file_name = f"submission_hsjepa_boundary_tomography_{config.name}_{suffix}_uploadsafe.csv"
    root_path = ROOT / file_name
    local_path = OUT / file_name
    write_submission(root_path, base, prob)
    write_submission(local_path, base, prob)
    validation = validate_submission(root_path, base, base_prob)
    return root_path, local_path, validation


def priority(metrics: dict[str, Any], config: BoundaryConfig, upload_safe: bool) -> float:
    if not upload_safe:
        return -99.0
    tests = metrics.get("tests", {})
    actual = metrics.get("actual", {})
    boundary_z = finite(tests.get("mean_boundary_score", {}).get("z"))
    weight_z = finite(tests.get("mean_total_weight", {}).get("z"))
    balance_z = finite(tests.get("mean_family_balance", {}).get("z"))
    cells = finite(actual.get("extra_cells"))
    if "consensus_shadow" in config.include_classes:
        risk_bonus = 0.20
    elif "route_only" in config.include_classes and "fusion_only" not in config.include_classes:
        risk_bonus = 0.08
    else:
        risk_bonus = -0.02
    return (
        0.35 * max(-1.0, min(2.0, boundary_z / 3.0))
        + 0.25 * max(-1.0, min(2.0, weight_z / 3.0))
        + 0.14 * max(-1.0, min(1.5, balance_z / 3.0))
        + 0.16 * min(cells, 12.0) / 12.0
        + risk_bonus
    )


def status_for(metrics: dict[str, Any], config: BoundaryConfig, upload_safe: bool) -> str:
    if not upload_safe:
        return "boundary_tomography_not_upload_safe"
    actual = metrics.get("actual", {})
    tests = metrics.get("tests", {})
    if finite(actual.get("extra_cells")) <= 0:
        return "boundary_tomography_empty"
    boundary_z = finite(tests.get("mean_boundary_score", {}).get("z"))
    if "consensus_shadow" in config.include_classes and boundary_z >= 1.5:
        return "consensus_shadow_alive"
    if "route_only" in config.include_classes and "fusion_only" not in config.include_classes:
        return "route_only_high_information"
    if "fusion_only" in config.include_classes and "route_only" not in config.include_classes:
        return "fusion_only_negative_control"
    return "boundary_disagreement_probe"


def build_markdown(readout: dict[str, Any]) -> str:
    rows = [
        "| Rank | Variant | Extra cells | Classes | Boundary z | Weight z | Priority | File |",
        "| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for rec in readout["ranking"]:
        tests = rec["stress"]["tests"]
        actual = rec["stress"]["actual"]
        rows.append(
            f"| `{rec['rank']}` | `{rec['variant']}` | `{actual['extra_cells']}` | `{','.join(rec['config']['include_classes'])}` | "
            f"`{fmt(tests.get('mean_boundary_score', {}).get('z'))}` | `{fmt(tests.get('mean_total_weight', {}).get('z'))}` | "
            f"`{fmt(rec['priority'])}` | `{rec['submission_file']}` |"
        )
    verdict = readout["verdict"]
    sensor = verdict["recommended_lb_sensor"]
    return "\n".join(
        [
            "# HS-JEPA Decoder Boundary Tomography Solver",
            "",
            "이 실험은 strict decoder-order jury가 버린 셀을 세 부류로 나누어 본다.",
            "",
            "- `consensus_shadow`: route와 fusion이 같은 방향으로 동의했지만 strict vote 기준을 못 넘긴 셀",
            "- `route_only`: route invariant만 action을 제안한 셀",
            "- `fusion_only`: action-health/fusion만 action을 제안한 셀",
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
            "## Why This Matters",
            "",
            "strict jury가 public에서 좋으면 안전한 consensus가 맞다. 하지만 그 다음 병목은 too-conservative release일 수 있다.",
            "이 solver는 그 보수성을 구조적으로 찌르는 다음 실험 후보를 만든다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    base, base_prob = load_base()
    weights = load_suite_weights()
    changes = collect_changes(base_prob, weights)
    strict = load_strict_jury_cells()
    stats = cell_stats(changes, strict)
    stats.to_csv(CELL_CSV, index=False)

    variants: dict[str, Any] = {}
    null_frames = []
    for config in CONFIGS:
        extra = choose_extra_cells(stats, config)
        root_path, local_path, validation = make_submission(base, base_prob, strict, extra, config)
        stress = stress_selection(stats, extra)
        if stress["null_rows"]:
            null_frame = pd.DataFrame(stress["null_rows"])
            null_frame["variant"] = config.name
            null_frames.append(null_frame)
        p = priority(stress, config, bool(validation.get("upload_safe")))
        variants[config.name] = {
            "variant": config.name,
            "status": status_for(stress, config, bool(validation.get("upload_safe"))),
            "submission_file": root_path.name,
            "root_path": str(root_path.resolve()),
            "local_path": str(local_path.resolve()),
            "validation": validation,
            "selected_extra_cells": extra.to_dict("records"),
            "stress": {"actual": stress["actual"], "tests": stress["tests"]},
            "priority": p,
            "config": {
                "name": config.name,
                "include_classes": list(config.include_classes),
                "max_extra_cells": config.max_extra_cells,
                "extra_shrink": config.extra_shrink,
                "strict_shrink": config.strict_shrink,
                "risk_role": config.risk_role,
            },
        }

    if null_frames:
        pd.concat(null_frames, ignore_index=True).to_csv(NULL_CSV, index=False)
    else:
        pd.DataFrame().to_csv(NULL_CSV, index=False)

    ranking = sorted(variants.values(), key=lambda item: item["priority"], reverse=True)
    for idx, item in enumerate(ranking, 1):
        item["rank"] = idx

    recommended = next((item for item in ranking if item["validation"].get("upload_safe")), ranking[0])
    status = "boundary_tomography_ready"
    if recommended["status"] not in {"consensus_shadow_alive", "route_only_high_information"}:
        status = "boundary_tomography_diagnostic_only"

    readout = {
        "experiment": "HS-JEPA Decoder Boundary Tomography Solver",
        "architecture_role": "sleep_competition_adapter_boundary_disagreement_probe",
        "core_boundary": "This is a competition adapter module; it reads submission-derived action decoders.",
        "status": status,
        "verdict": {
            "status": status,
            "recommended_lb_sensor": {
                "variant": recommended["variant"],
                "submission_file": recommended["submission_file"],
                "priority": recommended["priority"],
            },
            "claim": (
                "The next action-decoder bottleneck is whether strict cross-decoder jury is too conservative; "
                "weak consensus and route-only cells are separate hidden worlds and must be tested separately."
            ),
            "failure_interpretation": (
                "If every boundary probe worsens public LB, the safe frontier is strict cross-decoder consensus. "
                "If consensus_shadow wins, the jury was too conservative. If route_only wins, action-health is over-vetoing route signal."
            ),
        },
        "boundary_inventory": {
            "strict_jury_cells": int(stats["boundary_class"].eq("strict_jury").sum()),
            "consensus_shadow_cells": int(stats["boundary_class"].eq("consensus_shadow").sum()),
            "route_only_cells": int(stats["boundary_class"].eq("route_only").sum()),
            "fusion_only_cells": int(stats["boundary_class"].eq("fusion_only").sum()),
            "conflict_cells": int(stats["boundary_class"].eq("conflict").sum()),
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
    print(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False))
    return readout


if __name__ == "__main__":
    run()
