#!/usr/bin/env python3
"""Decoder-order jury solver for the sleep competition adapter.

This is not HS-JEPA core code.  It is a competition-adapter big bet.

The action-decoder ablation currently says route-first decoding is the
strongest local LB sensor, while route-toxicity fusion says factorized
action-health is a useful but weaker guard.  This solver asks a sharper
question:

    Which row-target actions are independently selected by both decoder
    orders, in the same direction?

If this works on public LB, the action decoder is not a single scoring rule.
It is a jury: route invariant proposes the move, action-health confirms it,
and only cross-decoder agreement is released.
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

from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (  # noqa: E402
    KEYS,
    TARGETS,
    TOL,
    clip_prob,
    short_hash,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "decoder_order_jury_solver"
OUT.mkdir(parents=True, exist_ok=True)

BASE_SUBMISSION = ROOT / "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
ACTION_SUITE_CSV = HERE / "outputs" / "action_decoder_ablation_suite" / "hsjepa_action_decoder_ablation_suite.csv"

READOUT_JSON = OUT / "decoder_order_jury_solver_readout.json"
READOUT_MD = OUT / "decoder_order_jury_solver_readout_ko.md"
CELL_CSV = OUT / "decoder_order_jury_cells.csv"
NULL_CSV = OUT / "decoder_order_jury_null_stress.csv"

ROUTE_S2 = "submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv"
ROUTE_SEED = "submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv"
ROUTE_OPEN = "submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv"
FUSION_S2 = "submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv"
FUSION_SEED = "submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv"
FUSION_OPEN = "submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv"


@dataclass(frozen=True)
class JuryConfig:
    name: str
    route_files: tuple[str, ...]
    fusion_files: tuple[str, ...]
    min_route_votes: int
    min_fusion_votes: int
    min_total_votes: int
    max_cells: int
    shrink: float


CONFIGS = [
    JuryConfig(
        name="s2_pair_consensus",
        route_files=(ROUTE_S2,),
        fusion_files=(FUSION_S2,),
        min_route_votes=1,
        min_fusion_votes=1,
        min_total_votes=2,
        max_cells=24,
        shrink=0.92,
    ),
    JuryConfig(
        name="seed_pair_consensus",
        route_files=(ROUTE_SEED,),
        fusion_files=(FUSION_SEED,),
        min_route_votes=1,
        min_fusion_votes=1,
        min_total_votes=2,
        max_cells=24,
        shrink=0.92,
    ),
    JuryConfig(
        name="family_supermajority",
        route_files=(ROUTE_S2, ROUTE_SEED, ROUTE_OPEN),
        fusion_files=(FUSION_S2, FUSION_SEED, FUSION_OPEN),
        min_route_votes=1,
        min_fusion_votes=1,
        min_total_votes=3,
        max_cells=28,
        shrink=0.86,
    ),
    JuryConfig(
        name="route_majority_fusion_confirmed",
        route_files=(ROUTE_S2, ROUTE_SEED, ROUTE_OPEN),
        fusion_files=(FUSION_S2, FUSION_SEED, FUSION_OPEN),
        min_route_votes=2,
        min_fusion_votes=1,
        min_total_votes=3,
        max_cells=24,
        shrink=0.88,
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
    if not math.isfinite(out):
        return "n/a"
    return f"{out:.{digits}f}"


def z_and_p(actual: float, nulls: list[float], higher_is_better: bool = True) -> dict[str, float | None]:
    if not nulls:
        return {"actual": float(actual), "null_mean": None, "null_std": None, "z": None, "p": None}
    arr = np.asarray(nulls, dtype=np.float64)
    mean = float(arr.mean())
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    z = (float(actual) - mean) / std if std > 0 else 0.0
    if higher_is_better:
        p = float((arr >= actual).mean())
    else:
        p = float((arr <= actual).mean())
    return {"actual": float(actual), "null_mean": mean, "null_std": std, "z": float(z), "p": p}


def load_base() -> tuple[pd.DataFrame, np.ndarray]:
    base = pd.read_csv(BASE_SUBMISSION, parse_dates=KEYS[1:])
    return base, base[TARGETS].to_numpy(dtype=np.float64)


def load_suite_weights() -> dict[str, dict[str, Any]]:
    if not ACTION_SUITE_CSV.exists():
        return {}
    suite = pd.read_csv(ACTION_SUITE_CSV)
    weights: dict[str, dict[str, Any]] = {}
    for rec in suite.to_dict("records"):
        file_name = str(rec.get("submission_file", ""))
        if not file_name or file_name == "nan":
            continue
        weights[file_name] = {
            "family": str(rec.get("family", "")),
            "variant": str(rec.get("variant", "")),
            "priority": max(0.05, finite(rec.get("lb_sensor_priority"), 0.05)),
        }
    return weights


def collect_changes(base_prob: np.ndarray, weights: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    all_files = sorted({*ROUTE_FILES, *FUSION_FILES})
    for file_name in all_files:
        path = ROOT / file_name
        if not path.exists():
            raise FileNotFoundError(path)
        pred = pd.read_csv(path, parse_dates=KEYS[1:])[TARGETS].to_numpy(dtype=np.float64)
        meta = weights.get(file_name, {})
        family = str(meta.get("family", "route_frontier" if "route_frontier" in file_name else "route_toxicity_fusion"))
        variant = str(meta.get("variant", file_name.replace("submission_hsjepa_", "").replace("_uploadsafe.csv", "")))
        priority = finite(meta.get("priority"), 0.50)
        for row_idx in range(pred.shape[0]):
            for target_idx, target in enumerate(TARGETS):
                delta = float(pred[row_idx, target_idx] - base_prob[row_idx, target_idx])
                if abs(delta) <= TOL:
                    continue
                rows.append(
                    {
                        "row": int(row_idx),
                        "target": target,
                        "target_idx": int(target_idx),
                        "cell_key": f"{row_idx}:{target}",
                        "file": file_name,
                        "family": family,
                        "variant": variant,
                        "priority": float(priority),
                        "delta": delta,
                        "sign": 1 if delta > 0 else -1,
                        "abs_delta": abs(delta),
                    }
                )
    return pd.DataFrame(rows)


ROUTE_FILES = (ROUTE_S2, ROUTE_SEED, ROUTE_OPEN)
FUSION_FILES = (FUSION_S2, FUSION_SEED, FUSION_OPEN)


def score_cell(group: pd.DataFrame, config: JuryConfig) -> dict[str, Any] | None:
    allowed = group[group["file"].isin((*config.route_files, *config.fusion_files))].copy()
    if allowed.empty:
        return None

    route = allowed[allowed["file"].isin(config.route_files)]
    fusion = allowed[allowed["file"].isin(config.fusion_files)]
    if route.empty or fusion.empty:
        return None

    pos_weight = float(allowed.loc[allowed["sign"].eq(1), "priority"].sum())
    neg_weight = float(allowed.loc[allowed["sign"].eq(-1), "priority"].sum())
    direction = 1 if pos_weight >= neg_weight else -1
    opposed_weight = neg_weight if direction == 1 else pos_weight
    agreed = allowed[allowed["sign"].eq(direction)].copy()
    route_agreed = route[route["sign"].eq(direction)]
    fusion_agreed = fusion[fusion["sign"].eq(direction)]

    if len(route_agreed) < config.min_route_votes:
        return None
    if len(fusion_agreed) < config.min_fusion_votes:
        return None
    if len(agreed) < config.min_total_votes:
        return None
    if opposed_weight > 1e-9:
        return None

    total_weight = float(agreed["priority"].sum())
    route_weight = float(route_agreed["priority"].sum())
    fusion_weight = float(fusion_agreed["priority"].sum())
    balance = 2.0 * min(route_weight, fusion_weight) / max(route_weight + fusion_weight, 1e-12)
    vote_coverage = 0.5 * (len(route_agreed) / len(config.route_files) + len(fusion_agreed) / len(config.fusion_files))
    weighted_delta = float(np.average(agreed["delta"].to_numpy(dtype=np.float64), weights=agreed["priority"].to_numpy(dtype=np.float64)))
    consensus_score = total_weight * (0.50 + 0.50 * balance) * (0.50 + 0.50 * vote_coverage)
    row = allowed.iloc[0]
    return {
        "config": config.name,
        "row": int(row["row"]),
        "target": str(row["target"]),
        "target_idx": int(row["target_idx"]),
        "cell_key": str(row["cell_key"]),
        "direction": int(direction),
        "route_votes": int(len(route_agreed)),
        "fusion_votes": int(len(fusion_agreed)),
        "total_votes": int(len(agreed)),
        "route_weight": route_weight,
        "fusion_weight": fusion_weight,
        "total_weight": total_weight,
        "family_balance": float(balance),
        "vote_coverage": float(vote_coverage),
        "mean_abs_delta": float(agreed["abs_delta"].mean()),
        "weighted_delta": weighted_delta,
        "released_delta": float(config.shrink * weighted_delta),
        "consensus_score": float(consensus_score),
        "files": ",".join(sorted(agreed["file"].unique())),
    }


def select_cells(changes: pd.DataFrame, config: JuryConfig) -> pd.DataFrame:
    rows = []
    for _, group in changes.groupby("cell_key", sort=False):
        scored = score_cell(group, config)
        if scored is not None:
            rows.append(scored)
    if not rows:
        return pd.DataFrame()
    selected = pd.DataFrame(rows)
    selected = selected.sort_values(
        ["consensus_score", "total_votes", "family_balance", "vote_coverage", "mean_abs_delta"],
        ascending=[False, False, False, False, False],
        kind="mergesort",
    ).head(config.max_cells)
    return selected.reset_index(drop=True)


def score_cells(frame: pd.DataFrame) -> dict[str, float]:
    if frame.empty:
        return {
            "changed_cells": 0,
            "changed_rows": 0,
            "mean_consensus_score": 0.0,
            "mean_total_weight": 0.0,
            "mean_cross_family_weight": 0.0,
            "mean_family_balance": 0.0,
            "mean_vote_coverage": 0.0,
            "same_direction_rate": 0.0,
        }
    return {
        "changed_cells": int(len(frame)),
        "changed_rows": int(frame["row"].nunique()),
        "mean_consensus_score": float(frame["consensus_score"].mean()),
        "mean_total_weight": float(frame["total_weight"].mean()),
        "mean_cross_family_weight": float(np.minimum(frame["route_weight"], frame["fusion_weight"]).mean()),
        "mean_family_balance": float(frame["family_balance"].mean()),
        "mean_vote_coverage": float(frame["vote_coverage"].mean()),
        "same_direction_rate": 1.0,
    }


def sample_null(changes: pd.DataFrame, selected: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    if selected.empty:
        return selected
    rows: list[pd.DataFrame] = []
    target_counts = selected["target"].value_counts().to_dict()
    unique_cells = selected[["cell_key", "target"]].drop_duplicates()
    all_cells = changes[["cell_key", "row", "target", "target_idx"]].drop_duplicates()
    for target, count in target_counts.items():
        pool = all_cells[all_cells["target"].eq(target)]
        if pool.empty:
            pool = all_cells
        rows.append(pool.sample(n=int(count), replace=len(pool) < int(count), random_state=int(rng.integers(0, 2**31 - 1))))
    sampled_keys = pd.concat(rows, ignore_index=True)["cell_key"].tolist()
    sampled = []
    for key in sampled_keys:
        group = changes[changes["cell_key"].eq(key)]
        route = group[group["family"].eq("route_frontier")]
        fusion = group[group["family"].eq("route_toxicity_fusion")]
        if group.empty:
            continue
        pos_weight = float(group.loc[group["sign"].eq(1), "priority"].sum())
        neg_weight = float(group.loc[group["sign"].eq(-1), "priority"].sum())
        direction = 1 if pos_weight >= neg_weight else -1
        agreed = group[group["sign"].eq(direction)]
        route_agreed = route[route["sign"].eq(direction)]
        fusion_agreed = fusion[fusion["sign"].eq(direction)]
        row = group.iloc[0]
        route_weight = float(route_agreed["priority"].sum())
        fusion_weight = float(fusion_agreed["priority"].sum())
        total_weight = float(agreed["priority"].sum())
        balance = 2.0 * min(route_weight, fusion_weight) / max(route_weight + fusion_weight, 1e-12)
        vote_coverage = 0.5 * (len(route_agreed) / len(ROUTE_FILES) + len(fusion_agreed) / len(FUSION_FILES))
        consensus_score = total_weight * (0.50 + 0.50 * balance) * (0.50 + 0.50 * vote_coverage)
        sampled.append(
            {
                "row": int(row["row"]),
                "target": str(row["target"]),
                "target_idx": int(row["target_idx"]),
                "cell_key": str(key),
                "route_weight": route_weight,
                "fusion_weight": fusion_weight,
                "total_weight": total_weight,
                "family_balance": float(balance),
                "vote_coverage": float(vote_coverage),
                "consensus_score": float(consensus_score),
            }
        )
    return pd.DataFrame(sampled)


def stress_against_null(changes: pd.DataFrame, selected: pd.DataFrame, seed: int = 20260610, iters: int = 500) -> dict[str, Any]:
    actual = score_cells(selected)
    null_rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(seed)
    for idx in range(iters):
        sampled = sample_null(changes, selected, rng)
        metrics = score_cells(sampled)
        metrics["iteration"] = idx
        null_rows.append(metrics)
    null = pd.DataFrame(null_rows)
    if null.empty:
        return {"actual": actual, "tests": {}, "null_rows": []}
    tests = {
        key: z_and_p(actual[key], null[key].to_list(), higher_is_better=True)
        for key in [
            "mean_consensus_score",
            "mean_total_weight",
            "mean_cross_family_weight",
            "mean_family_balance",
            "mean_vote_coverage",
        ]
    }
    return {"actual": actual, "tests": tests, "null_rows": null_rows}


def make_submission(base: pd.DataFrame, base_prob: np.ndarray, selected: pd.DataFrame, name: str) -> tuple[Path, Path, dict[str, object]]:
    prob = base_prob.copy()
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + float(rec["released_delta"]))
    suffix = short_hash(prob)
    file_name = f"submission_hsjepa_decoder_jury_{name}_{suffix}_uploadsafe.csv"
    root_path = ROOT / file_name
    local_path = OUT / file_name
    write_submission(root_path, base, prob)
    write_submission(local_path, base, prob)
    validation = validate_submission(root_path, base, base_prob)
    return root_path, local_path, validation


def variant_priority(metrics: dict[str, Any]) -> float:
    tests = metrics.get("tests", {})
    actual = metrics.get("actual", {})
    consensus_z = finite(tests.get("mean_consensus_score", {}).get("z"))
    cross_z = finite(tests.get("mean_cross_family_weight", {}).get("z"))
    balance_z = finite(tests.get("mean_family_balance", {}).get("z"))
    cells = finite(actual.get("changed_cells"))
    rows = finite(actual.get("changed_rows"))
    return (
        0.32 * max(-1.0, min(2.0, consensus_z / 3.0))
        + 0.28 * max(-1.0, min(2.0, cross_z / 3.0))
        + 0.16 * max(-1.0, min(1.5, balance_z / 3.0))
        + 0.14 * min(cells, 28.0) / 28.0
        + 0.10 * min(rows, 28.0) / 28.0
    )


def status_for(metrics: dict[str, Any], upload_safe: bool) -> str:
    if not upload_safe:
        return "decoder_jury_not_upload_safe"
    actual = metrics.get("actual", {})
    tests = metrics.get("tests", {})
    if finite(actual.get("changed_cells")) < 4:
        return "decoder_jury_too_sparse"
    consensus_z = finite(tests.get("mean_consensus_score", {}).get("z"))
    cross_z = finite(tests.get("mean_cross_family_weight", {}).get("z"))
    if consensus_z >= 2.0 and cross_z >= 2.0:
        return "decoder_jury_alive_cross_decoder_agreement"
    if consensus_z >= 1.0 or cross_z >= 1.0:
        return "decoder_jury_boundary"
    return "decoder_jury_weak"


def build_markdown(readout: dict[str, Any]) -> str:
    rows = [
        "| Rank | Variant | Changed | Rows | Consensus z | Cross-family z | Priority | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for rec in readout["ranking"]:
        tests = rec["stress"]["tests"]
        actual = rec["stress"]["actual"]
        rows.append(
            f"| `{rec['rank']}` | `{rec['variant']}` | `{actual['changed_cells']}` | `{actual['changed_rows']}` | "
            f"`{fmt(tests['mean_consensus_score']['z'])}` | `{fmt(tests['mean_cross_family_weight']['z'])}` | "
            f"`{fmt(rec['priority'])}` | `{rec['submission_file']}` |"
        )

    verdict = readout["verdict"]
    rec = verdict["recommended_lb_sensor"]
    return "\n".join(
        [
            "# HS-JEPA Decoder-Order Jury Solver",
            "",
            "이 실험은 route-first decoder와 route-toxicity fusion decoder가 같은 row-target action을 같은 방향으로 고르는지 본다.",
            "단일 decoder 점수를 더 믿는 대신, 여러 decoder가 독립적으로 동의한 action만 release한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{verdict['status']}`",
            f"- Recommended LB sensor: `{rec['variant']}` -> `{rec['submission_file']}`",
            f"- Claim: {verdict['claim']}",
            f"- Failure interpretation: {verdict['failure_interpretation']}",
            "",
            "## Ranking",
            "",
            *rows,
            "",
            "## Interpretation",
            "",
            "- 이 후보가 public에서 route-frontier보다 좋으면, HS-JEPA action decoder는 route-first 단독이 아니라 cross-decoder listener jury가 맞다는 뜻이다.",
            "- 나쁘면, consensus가 너무 보수적이거나 action-health gate가 route signal을 과하게 깎았다는 뜻이다.",
            "- 이 모듈은 HS-JEPA core가 아니라 sleep competition adapter의 row-target assignment solver다.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    base, base_prob = load_base()
    weights = load_suite_weights()
    changes = collect_changes(base_prob, weights)

    variants: dict[str, Any] = {}
    all_cells: list[pd.DataFrame] = []
    all_nulls: list[pd.DataFrame] = []
    for config in CONFIGS:
        selected = select_cells(changes, config)
        if not selected.empty:
            root_path, local_path, validation = make_submission(base, base_prob, selected, config.name)
        else:
            root_path = local_path = Path("")
            validation = {"upload_safe": False, "changed_cells_vs_current_best": 0}
        stress = stress_against_null(changes, selected)
        priority = variant_priority(stress)
        status = status_for(stress, bool(validation.get("upload_safe")))
        selected = selected.copy()
        selected["variant"] = config.name
        all_cells.append(selected)
        null_frame = pd.DataFrame(stress.get("null_rows", []))
        if not null_frame.empty:
            null_frame["variant"] = config.name
            all_nulls.append(null_frame)
        variants[config.name] = {
            "variant": config.name,
            "status": status,
            "submission_file": root_path.name if root_path.name else None,
            "root_path": str(root_path.resolve()) if root_path.name else None,
            "local_path": str(local_path.resolve()) if local_path.name else None,
            "validation": validation,
            "stress": {
                "actual": stress["actual"],
                "tests": stress["tests"],
            },
            "priority": priority,
            "config": config.__dict__,
        }

    if all_cells:
        pd.concat(all_cells, ignore_index=True).to_csv(CELL_CSV, index=False)
    else:
        pd.DataFrame().to_csv(CELL_CSV, index=False)
    if all_nulls:
        pd.concat(all_nulls, ignore_index=True).to_csv(NULL_CSV, index=False)
    else:
        pd.DataFrame().to_csv(NULL_CSV, index=False)

    ranking = sorted(variants.values(), key=lambda item: item["priority"], reverse=True)
    for idx, item in enumerate(ranking, 1):
        item["rank"] = idx
    recommended = next((item for item in ranking if item["validation"].get("upload_safe")), ranking[0])
    status = "decoder_order_jury_ready"
    if recommended["status"] != "decoder_jury_alive_cross_decoder_agreement":
        status = "decoder_order_jury_boundary"

    readout = {
        "experiment": "HS-JEPA Decoder-Order Jury Solver",
        "architecture_role": "sleep_competition_adapter_cross_decoder_action_jury",
        "core_boundary": "This module reads adapter submissions and must not be imported by HS-JEPA core.",
        "status": status,
        "verdict": {
            "status": status,
            "recommended_lb_sensor": {
                "variant": recommended["variant"],
                "submission_file": recommended["submission_file"],
                "priority": recommended["priority"],
            },
            "claim": (
                "Safe row-target assignment is a cross-decoder jury: route invariant proposes the action, "
                "factorized action-health confirms it, and only same-direction consensus is released."
            ),
            "failure_interpretation": (
                "If public LB worsens, consensus is too conservative or action-health removes useful route-frontier signal."
            ),
        },
        "ranking": ranking,
        "inputs": {
            "base_submission": str(BASE_SUBMISSION.resolve()),
            "action_suite": str(ACTION_SUITE_CSV.resolve()),
            "route_files": list(ROUTE_FILES),
            "fusion_files": list(FUSION_FILES),
        },
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
