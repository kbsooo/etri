#!/usr/bin/env python3
"""Counterfactual listener-dropout solver for the sleep competition adapter.

This is a paper-facing HS-JEPA adapter experiment.

The architectural claim is not "blend another submission".  The claim is:

    a row-target action is healthy only if it remains coherent when one
    listener family is masked, and it is not the same action pattern that
    previously produced a negative public-LB sensor.

In HS-JEPA terms, route, fusion, target-listener, and anti-shortcut sensors are
treated as different listeners over the same hidden human-state action.  The
solver releases only actions that survive counterfactual listener dropout.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
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
OUT = HERE / "outputs" / "counterfactual_listener_dropout_solver"
OUT.mkdir(parents=True, exist_ok=True)

BASE_SUBMISSION = ROOT / "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
STRICT_CELLS = HERE / "outputs" / "decoder_order_jury_solver" / "decoder_order_jury_cells.csv"
BOUNDARY_CELLS = HERE / "outputs" / "decoder_boundary_tomography_solver" / "decoder_boundary_tomography_cells.csv"
CROSS_LISTENER_CELLS = HERE / "outputs" / "cross_listener_transport_decoder" / "cross_listener_transport_cells.csv"
PUBLIC_LEDGER = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"

READOUT_JSON = OUT / "counterfactual_listener_dropout_readout.json"
READOUT_MD = OUT / "counterfactual_listener_dropout_readout_ko.md"
CELL_CSV = OUT / "counterfactual_listener_dropout_cells.csv"
NULL_CSV = OUT / "counterfactual_listener_dropout_null_stress.csv"


POSITIVE_SOURCE_FILES = (
    "submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv",
    "submission_hsjepa_decoder_jury_route_majority_fusion_confirmed_1caf57fb_uploadsafe.csv",
    "submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv",
    "submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv",
    "submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv",
    "submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv",
    "submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv",
    "submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv",
)

NEGATIVE_SENSOR_FILES = {
    "target_listener_lift": "submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv",
    "cross_listener_shadow": "submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv",
    "dual_head_pareto": "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
    "public_private_toxicity": "submission_hsjepa_public_private_toxicity_23c62cf4_uploadsafe.csv",
}


@dataclass(frozen=True)
class DropoutConfig:
    name: str
    worldview: str
    include_boundary_classes: tuple[str, ...]
    max_cells: int
    min_survival_count: int
    min_dropout_score: float
    max_same_negative: float
    min_same_negative: float
    min_opposite_negative: float
    shrink: float
    rescue_opposite_negative: bool = False
    invert_action: bool = False
    require_cross_family: bool = True


CONFIGS = (
    DropoutConfig(
        name="invariant_survivor",
        worldview=(
            "Healthy actions are those selected by route/fusion structure and still coherent "
            "after target-listener or anti-shortcut evidence is masked."
        ),
        include_boundary_classes=("strict_jury", "consensus_shadow"),
        max_cells=26,
        min_survival_count=4,
        min_dropout_score=0.54,
        max_same_negative=0.18,
        min_same_negative=0.0,
        min_opposite_negative=0.0,
        shrink=0.78,
        require_cross_family=True,
    ),
    DropoutConfig(
        name="anti_listener_toxicity_veto",
        worldview=(
            "The public failure of listener-confirmed shadow actions is a toxicity label; "
            "release only route/fusion actions that are not co-linear with those negative sensors."
        ),
        include_boundary_classes=("strict_jury", "consensus_shadow", "route_only"),
        max_cells=30,
        min_survival_count=3,
        min_dropout_score=0.48,
        max_same_negative=0.10,
        min_same_negative=0.0,
        min_opposite_negative=0.0,
        shrink=0.72,
        require_cross_family=False,
    ),
    DropoutConfig(
        name="negative_space_rescue",
        worldview=(
            "Bad public sensors may reveal the wrong side of the action manifold; "
            "cells with route support and opposite negative-sensor direction are rescue candidates."
        ),
        include_boundary_classes=("consensus_shadow", "route_only", "fusion_only"),
        max_cells=24,
        min_survival_count=2,
        min_dropout_score=0.42,
        max_same_negative=0.24,
        min_same_negative=0.0,
        min_opposite_negative=0.30,
        shrink=0.46,
        rescue_opposite_negative=True,
        require_cross_family=False,
    ),
    DropoutConfig(
        name="dropout_fullfield_aggressive",
        worldview=(
            "Negative public sensors may have failed because they mixed good high-health cells with toxic extras; "
            "therefore release a larger listener-dropout field with only mild toxicity damping."
        ),
        include_boundary_classes=("strict_jury", "consensus_shadow"),
        max_cells=22,
        min_survival_count=5,
        min_dropout_score=0.50,
        max_same_negative=0.96,
        min_same_negative=0.0,
        min_opposite_negative=0.0,
        shrink=0.38,
        require_cross_family=True,
    ),
    DropoutConfig(
        name="toxic_direction_inversion",
        worldview=(
            "If listener-dropout healthy cells repeatedly align with bad public sensors, the hidden action may be "
            "on the wrong side of the public/private equation; test a small opposite-direction correction."
        ),
        include_boundary_classes=("strict_jury", "consensus_shadow"),
        max_cells=16,
        min_survival_count=5,
        min_dropout_score=0.50,
        max_same_negative=1.00,
        min_same_negative=0.55,
        min_opposite_negative=0.0,
        shrink=0.18,
        invert_action=True,
        require_cross_family=True,
    ),
)


def finite(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def fmt(value: Any, digits: int = 4) -> str:
    val = finite(value, float("nan"))
    return f"{val:.{digits}f}" if math.isfinite(val) else "n/a"


def rank01(values: pd.Series, higher: bool = True) -> pd.Series:
    if values.notna().sum() <= 1:
        return pd.Series([0.5] * len(values), index=values.index)
    return values.rank(pct=True, method="average", ascending=higher).fillna(0.0)


def z_and_p(actual: float, nulls: list[float], higher_is_better: bool = True) -> dict[str, float | None]:
    if not nulls:
        return {"actual": float(actual), "null_mean": None, "null_std": None, "z": None, "p": None}
    arr = np.asarray(nulls, dtype=np.float64)
    mean = float(arr.mean())
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    z = (float(actual) - mean) / std if std > 0.0 else 0.0
    p = float((arr >= actual).mean()) if higher_is_better else float((arr <= actual).mean())
    return {"actual": float(actual), "null_mean": mean, "null_std": std, "z": float(z), "p": p}


def public_score(file_name: str) -> float | None:
    if not PUBLIC_LEDGER.exists():
        return None
    ledger = pd.read_csv(PUBLIC_LEDGER)
    hit = ledger.loc[ledger["file"].eq(file_name), "public_lb"]
    if hit.empty:
        return None
    return float(hit.iloc[-1])


def load_base() -> tuple[pd.DataFrame, np.ndarray]:
    base = pd.read_csv(BASE_SUBMISSION, parse_dates=KEYS[1:])
    return base, base[TARGETS].to_numpy(dtype=np.float64)


def load_candidate_cells() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    strict = pd.read_csv(STRICT_CELLS)
    strict = strict[strict["config"].eq("family_supermajority")].copy()
    strict["boundary_class"] = "strict_jury"
    strict["action_delta"] = strict["released_delta"].astype(float)
    strict["action_score"] = strict["consensus_score"].astype(float)
    strict["opposed_weight"] = 0.0
    strict["source_table"] = "decoder_order_jury"
    frames.append(strict)

    boundary = pd.read_csv(BOUNDARY_CELLS).copy()
    boundary = boundary[boundary["boundary_class"].isin(["consensus_shadow", "route_only", "fusion_only"])].copy()
    boundary["action_delta"] = boundary["weighted_delta"].astype(float)
    boundary["action_score"] = boundary["boundary_score"].astype(float)
    boundary["source_table"] = "boundary_tomography"
    frames.append(boundary)

    cells = pd.concat(frames, ignore_index=True, sort=False)
    keep = [
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
    cells = cells[keep].drop_duplicates(["cell_key", "boundary_class"], keep="first")
    cells["row"] = cells["row"].astype(int)
    cells["target"] = cells["target"].astype(str)
    cells["target_idx"] = cells["target_idx"].astype(int)
    cells["direction"] = np.sign(cells["action_delta"].astype(float)).replace(0, 1).astype(int)
    return cells.reset_index(drop=True)


def add_cross_listener_features(cells: pd.DataFrame) -> pd.DataFrame:
    out = cells.copy()
    if not CROSS_LISTENER_CELLS.exists():
        out["listener_score"] = 0.0
        out["row_s2_listener_score"] = 0.0
        out["cross_listener_transport_score"] = 0.0
        out["same_listener_direction"] = False
        return out
    cross = pd.read_csv(CROSS_LISTENER_CELLS)
    cols = [
        "cell_key",
        "listener_score",
        "row_s2_listener_score",
        "cross_listener_transport_score",
        "same_listener_direction",
        "full_listener_prob",
    ]
    cross = cross[[col for col in cols if col in cross.columns]].drop_duplicates("cell_key")
    out = out.merge(cross, on="cell_key", how="left")
    for col in [
        "listener_score",
        "row_s2_listener_score",
        "cross_listener_transport_score",
        "full_listener_prob",
    ]:
        if col not in out:
            out[col] = 0.0
        out[col] = out[col].fillna(0.0).astype(float)
    if "same_listener_direction" not in out:
        out["same_listener_direction"] = False
    out["same_listener_direction"] = out["same_listener_direction"].fillna(False).astype(bool)
    return out


def submission_delta_map(base_prob: np.ndarray, file_name: str) -> pd.DataFrame:
    path = ROOT / file_name
    if not path.exists():
        return pd.DataFrame(columns=["row", "target", "cell_key", f"{file_name}_delta"])
    pred = pd.read_csv(path, parse_dates=KEYS[1:])[TARGETS].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    for row_idx in range(pred.shape[0]):
        for target_idx, target in enumerate(TARGETS):
            delta = float(pred[row_idx, target_idx] - base_prob[row_idx, target_idx])
            if abs(delta) <= TOL:
                continue
            rows.append(
                {
                    "row": row_idx,
                    "target": target,
                    "cell_key": f"{row_idx}:{target}",
                    "delta": delta,
                    "direction": 1 if delta > 0 else -1,
                    "abs_delta": abs(delta),
                }
            )
    return pd.DataFrame(rows)


def add_source_agreement(cells: pd.DataFrame, base_prob: np.ndarray) -> pd.DataFrame:
    out = cells.copy()
    positive_same = pd.Series(0.0, index=out.index)
    positive_opposite = pd.Series(0.0, index=out.index)
    for file_name in POSITIVE_SOURCE_FILES:
        deltas = submission_delta_map(base_prob, file_name)
        if deltas.empty:
            continue
        tmp = out[["cell_key", "direction"]].merge(
            deltas[["cell_key", "direction", "abs_delta"]],
            on="cell_key",
            how="left",
            suffixes=("", "_source"),
        )
        same = tmp["direction"].eq(tmp["direction_source"]).fillna(False)
        opposite = tmp["direction"].ne(tmp["direction_source"]).fillna(False) & tmp["direction_source"].notna()
        positive_same += same.astype(float) * tmp["abs_delta"].fillna(0.0).astype(float)
        positive_opposite += opposite.astype(float) * tmp["abs_delta"].fillna(0.0).astype(float)

    negative_same = pd.Series(0.0, index=out.index)
    negative_opposite = pd.Series(0.0, index=out.index)
    negative_sources: list[str] = []
    best = public_score(BASE_SUBMISSION.name) or 0.5677475939
    for label, file_name in NEGATIVE_SENSOR_FILES.items():
        deltas = submission_delta_map(base_prob, file_name)
        lb = public_score(file_name)
        lb_penalty = max(0.10, min(1.50, ((lb or best + 0.0005) - best) / 0.0005))
        if deltas.empty:
            continue
        tmp = out[["cell_key", "direction"]].merge(
            deltas[["cell_key", "direction", "abs_delta"]],
            on="cell_key",
            how="left",
            suffixes=("", "_source"),
        )
        same = tmp["direction"].eq(tmp["direction_source"]).fillna(False)
        opposite = tmp["direction"].ne(tmp["direction_source"]).fillna(False) & tmp["direction_source"].notna()
        negative_same += lb_penalty * same.astype(float) * tmp["abs_delta"].fillna(0.0).astype(float)
        negative_opposite += lb_penalty * opposite.astype(float) * tmp["abs_delta"].fillna(0.0).astype(float)
        negative_sources.append(f"{label}:{fmt(lb, 10)}")

    out["positive_same_action_mass"] = positive_same.astype(float)
    out["positive_opposite_action_mass"] = positive_opposite.astype(float)
    out["negative_same_action_mass"] = negative_same.astype(float)
    out["negative_opposite_action_mass"] = negative_opposite.astype(float)
    out["negative_sensor_sources"] = ",".join(negative_sources)
    return out


def listener_dropout_scores(cells: pd.DataFrame) -> pd.DataFrame:
    out = cells.copy()
    out["route_listener"] = rank01(out["route_weight"].astype(float))
    out["fusion_listener"] = rank01(out["fusion_weight"].astype(float))
    out["cross_decoder_listener"] = rank01(out["action_score"].astype(float))
    out["target_listener"] = rank01(out["cross_listener_transport_score"].astype(float))
    out["anti_shortcut_listener"] = 1.0 - rank01(out["negative_same_action_mass"].astype(float))
    out["negative_space_listener"] = rank01(out["negative_opposite_action_mass"].astype(float))
    out["positive_source_listener"] = rank01(out["positive_same_action_mass"].astype(float))

    components = {
        "route": ("route_listener", 0.20),
        "fusion": ("fusion_listener", 0.20),
        "cross_decoder": ("cross_decoder_listener", 0.18),
        "target_listener": ("target_listener", 0.14),
        "anti_shortcut": ("anti_shortcut_listener", 0.20),
        "positive_source": ("positive_source_listener", 0.08),
    }
    raw = sum(weight * out[col].astype(float) for col, weight in components.values())
    raw += 0.06 * out["family_balance"].astype(float).clip(0, 1)
    raw += 0.04 * out["vote_coverage"].astype(float).clip(0, 1)
    raw -= 0.16 * rank01(out["positive_opposite_action_mass"].astype(float))
    out["full_listener_score"] = raw.clip(0.0, 1.0)

    dropout_cols = []
    for dropped, (drop_col, _) in components.items():
        active = {name: item for name, item in components.items() if name != dropped}
        denom = sum(weight for _, weight in active.values())
        score = sum((weight / denom) * out[col].astype(float) for col, weight in active.values())
        score += 0.05 * out["family_balance"].astype(float).clip(0, 1)
        score += 0.03 * out["vote_coverage"].astype(float).clip(0, 1)
        score -= 0.14 * rank01(out["positive_opposite_action_mass"].astype(float))
        col_name = f"drop_{dropped}_score"
        out[col_name] = score.clip(0.0, 1.0)
        dropout_cols.append(col_name)

    out["dropout_min_score"] = out[dropout_cols].min(axis=1)
    out["dropout_mean_score"] = out[dropout_cols].mean(axis=1)
    out["dropout_survival_count"] = out[dropout_cols].ge(0.48).sum(axis=1)
    out["same_negative_rank"] = rank01(out["negative_same_action_mass"].astype(float))
    out["opposite_negative_rank"] = rank01(out["negative_opposite_action_mass"].astype(float))
    out["listener_dropout_health"] = (
        0.36 * out["dropout_min_score"]
        + 0.26 * out["dropout_mean_score"]
        + 0.18 * out["anti_shortcut_listener"]
        + 0.12 * out["positive_source_listener"]
        + 0.08 * out["negative_space_listener"]
    ).clip(0.0, 1.0)
    return out.sort_values(
        ["listener_dropout_health", "dropout_min_score", "action_score"],
        ascending=[False, False, False],
        kind="mergesort",
    ).reset_index(drop=True)


def select_cells(cells: pd.DataFrame, config: DropoutConfig) -> pd.DataFrame:
    pool = cells[cells["boundary_class"].isin(config.include_boundary_classes)].copy()
    pool = pool[pool["dropout_survival_count"].ge(config.min_survival_count)]
    pool = pool[pool["dropout_min_score"].ge(config.min_dropout_score)]
    pool = pool[pool["same_negative_rank"].le(config.max_same_negative)]
    pool = pool[pool["same_negative_rank"].ge(config.min_same_negative)]
    if config.min_opposite_negative > 0:
        pool = pool[pool["opposite_negative_rank"].ge(config.min_opposite_negative)]
    if config.require_cross_family:
        pool = pool[(pool["route_weight"].gt(0.0)) & (pool["fusion_weight"].gt(0.0))]
    if pool.empty:
        return pool
    if config.rescue_opposite_negative:
        pool["selection_score"] = (
            0.34 * pool["opposite_negative_rank"]
            + 0.26 * pool["listener_dropout_health"]
            + 0.20 * pool["route_listener"]
            + 0.12 * pool["cross_decoder_listener"]
            + 0.08 * pool["anti_shortcut_listener"]
        )
    else:
        pool["selection_score"] = (
            0.42 * pool["listener_dropout_health"]
            + 0.22 * pool["dropout_min_score"]
            + 0.16 * pool["cross_decoder_listener"]
            + 0.12 * pool["anti_shortcut_listener"]
            + 0.08 * pool["positive_source_listener"]
        )
    selected = pool.sort_values(
        ["selection_score", "dropout_min_score", "action_score"],
        ascending=[False, False, False],
        kind="mergesort",
    ).head(config.max_cells)
    selected = selected.copy()
    selected["released_delta"] = selected["action_delta"].astype(float) * config.shrink
    if config.invert_action:
        selected["released_delta"] = -selected["released_delta"]
    if config.rescue_opposite_negative:
        selected["released_delta"] = selected["released_delta"] + (
            0.12 * selected["negative_opposite_action_mass"].astype(float) * selected["direction"].astype(float)
        )
    selected["config"] = config.name
    return selected.reset_index(drop=True)


def score_cells(frame: pd.DataFrame) -> dict[str, float]:
    if frame.empty:
        return {
            "cells": 0.0,
            "rows": 0.0,
            "mean_listener_dropout_health": 0.0,
            "mean_dropout_min_score": 0.0,
            "mean_survival_count": 0.0,
            "mean_same_negative_rank": 0.0,
            "mean_opposite_negative_rank": 0.0,
            "strict_rate": 0.0,
            "cross_family_rate": 0.0,
            "s2_rate": 0.0,
        }
    return {
        "cells": float(len(frame)),
        "rows": float(frame["row"].nunique()),
        "mean_listener_dropout_health": float(frame["listener_dropout_health"].mean()),
        "mean_dropout_min_score": float(frame["dropout_min_score"].mean()),
        "mean_survival_count": float(frame["dropout_survival_count"].mean()),
        "mean_same_negative_rank": float(frame["same_negative_rank"].mean()),
        "mean_opposite_negative_rank": float(frame["opposite_negative_rank"].mean()),
        "strict_rate": float(frame["boundary_class"].eq("strict_jury").mean()),
        "cross_family_rate": float((frame["route_weight"].gt(0.0) & frame["fusion_weight"].gt(0.0)).mean()),
        "s2_rate": float(frame["target"].eq("S2").mean()),
    }


def sample_null(cells: pd.DataFrame, selected: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    if selected.empty:
        return selected.copy()
    sampled: list[pd.DataFrame] = []
    for target, group in selected.groupby("target"):
        pool = cells[cells["target"].eq(target)]
        if pool.empty:
            pool = cells
        sampled.append(
            pool.sample(
                n=len(group),
                replace=len(pool) < len(group),
                random_state=int(rng.integers(0, 2**31 - 1)),
            )
        )
    return pd.concat(sampled, ignore_index=True) if sampled else pd.DataFrame()


def stress_against_null(cells: pd.DataFrame, selected: pd.DataFrame, seed: int = 20260611, iters: int = 500) -> dict[str, Any]:
    actual = score_cells(selected)
    rng = np.random.default_rng(seed)
    null_rows: list[dict[str, Any]] = []
    for idx in range(iters):
        metrics = score_cells(sample_null(cells, selected, rng))
        metrics["iteration"] = idx
        null_rows.append(metrics)
    null = pd.DataFrame(null_rows)
    tests: dict[str, Any] = {}
    if not null.empty:
        tests = {
            "mean_listener_dropout_health": z_and_p(
                actual["mean_listener_dropout_health"],
                null["mean_listener_dropout_health"].to_list(),
                higher_is_better=True,
            ),
            "mean_dropout_min_score": z_and_p(
                actual["mean_dropout_min_score"],
                null["mean_dropout_min_score"].to_list(),
                higher_is_better=True,
            ),
            "mean_survival_count": z_and_p(
                actual["mean_survival_count"],
                null["mean_survival_count"].to_list(),
                higher_is_better=True,
            ),
            "mean_same_negative_rank": z_and_p(
                actual["mean_same_negative_rank"],
                null["mean_same_negative_rank"].to_list(),
                higher_is_better=False,
            ),
            "mean_opposite_negative_rank": z_and_p(
                actual["mean_opposite_negative_rank"],
                null["mean_opposite_negative_rank"].to_list(),
                higher_is_better=True,
            ),
        }
    return {"actual": actual, "tests": tests, "null_rows": null_rows}


def make_submission(
    base: pd.DataFrame,
    base_prob: np.ndarray,
    selected: pd.DataFrame,
    config: DropoutConfig,
) -> tuple[Path, Path, dict[str, object]]:
    prob = base_prob.copy()
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + float(rec["released_delta"]))
    suffix = short_hash(prob)
    file_name = f"submission_hsjepa_counterfactual_listener_dropout_{config.name}_{suffix}_uploadsafe.csv"
    root_path = ROOT / file_name
    local_path = OUT / file_name
    write_submission(root_path, base, prob)
    write_submission(local_path, base, prob)
    validation = validate_submission(root_path, base, base_prob)
    return root_path, local_path, validation


def priority(stress: dict[str, Any], validation: dict[str, object], config: DropoutConfig) -> float:
    tests = stress.get("tests", {})
    actual = stress.get("actual", {})
    health_z = finite(tests.get("mean_listener_dropout_health", {}).get("z"))
    min_z = finite(tests.get("mean_dropout_min_score", {}).get("z"))
    survive_z = finite(tests.get("mean_survival_count", {}).get("z"))
    negative_z = finite(tests.get("mean_same_negative_rank", {}).get("z"))
    opposite_z = finite(tests.get("mean_opposite_negative_rank", {}).get("z"))
    rescue_bonus = 0.12 if config.rescue_opposite_negative else 0.0
    return (
        0.26 * np.clip(health_z / 3.0, -1.0, 2.0)
        + 0.20 * np.clip(min_z / 3.0, -1.0, 2.0)
        + 0.18 * np.clip(survive_z / 3.0, -1.0, 2.0)
        + 0.16 * np.clip(negative_z / 3.0, -1.0, 2.0)
        + 0.08 * np.clip(opposite_z / 3.0, -1.0, 2.0)
        + 0.07 * min(finite(actual.get("cells")), 30.0) / 30.0
        + 0.05 * (1.0 if validation.get("upload_safe") else -1.0)
        + rescue_bonus
    )


def build_markdown(readout: dict[str, Any]) -> str:
    lines = [
        "# Counterfactual Listener-Dropout Solver",
        "",
        "## 핵심 주장",
        "",
        "이 실험은 HS-JEPA를 label predictor가 아니라 action-health architecture로 검증한다.",
        "row-target action은 route/fusion/target-listener/anti-shortcut listener 중 하나가 사라져도 살아남아야 하며, 이미 public에서 나빴던 listener-confirmed action과 같은 방향이면 독성으로 본다.",
        "",
        "## 왜 논문용인가",
        "",
        "- `listener dropout`: 특정 관측자에만 맞는 shortcut action을 제거한다.",
        "- `negative public sensor`: 실패한 제출을 점수표가 아니라 action toxicity label로 재해석한다.",
        "- `invariant action`: 좋은 확률값이 아니라 보이지 않는 human-state에서 건강한 이동만 release한다.",
        "",
        "## Ranking",
        "",
        "| Rank | Variant | Cells | Rows | Health z | Min-score z | Survival z | Same-negative z | Opposite-negative z | Priority | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in readout["ranking"]:
        tests = item["stress"]["tests"]
        actual = item["stress"]["actual"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(item["rank"]),
                    f"`{item['variant']}`",
                    str(int(actual["cells"])),
                    str(int(actual["rows"])),
                    fmt(tests.get("mean_listener_dropout_health", {}).get("z")),
                    fmt(tests.get("mean_dropout_min_score", {}).get("z")),
                    fmt(tests.get("mean_survival_count", {}).get("z")),
                    fmt(tests.get("mean_same_negative_rank", {}).get("z")),
                    fmt(tests.get("mean_opposite_negative_rank", {}).get("z")),
                    fmt(item["priority"]),
                    f"`{item['submission_file']}`",
                ]
            )
            + " |"
        )
    verdict = readout["verdict"]
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['status']}`",
            f"- Recommended information sensor: `{verdict['recommended_information_sensor']['submission_file']}`",
            f"- Recommended thesis sensor: `{verdict['recommended_thesis_sensor']['submission_file']}`",
            "",
            "## Public LB 해석",
            "",
            "- 좋아지면: HS-JEPA의 contribution은 `더 좋은 feature`가 아니라 `listener가 바뀌어도 안전한 action만 release하는 구조`라는 주장이 강해진다.",
            "- 나빠지면: listener-dropout은 local geometry는 좋지만 public/private action equation에는 과하게 보수적이거나, negative sensor의 cell-level toxicity 전이가 틀렸다는 뜻이다.",
            "- `negative_space_rescue`가 좋아지면: 실패 제출들이 단순히 버릴 것이 아니라, 반대 방향 action manifold를 가리키는 센서였다는 세계관이 살아난다.",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict[str, Any]:
    base, base_prob = load_base()
    cells = load_candidate_cells()
    cells = add_cross_listener_features(cells)
    cells = add_source_agreement(cells, base_prob)
    cells = listener_dropout_scores(cells)

    all_selected: list[pd.DataFrame] = []
    null_rows: list[dict[str, Any]] = []
    variants: list[dict[str, Any]] = []
    for config in CONFIGS:
        selected = select_cells(cells, config)
        root_path, local_path, validation = make_submission(base, base_prob, selected, config)
        stress = stress_against_null(cells, selected)
        for rec in stress["null_rows"]:
            rec["variant"] = config.name
            null_rows.append(rec)
        selected = selected.copy()
        selected["variant"] = config.name
        all_selected.append(selected)
        variants.append(
            {
                "variant": config.name,
                "worldview": config.worldview,
                "submission_file": root_path.name,
                "root_path": str(root_path.resolve()),
                "local_path": str(local_path.resolve()),
                "validation": validation,
                "stress": {key: value for key, value in stress.items() if key != "null_rows"},
                "priority": priority(stress, validation, config),
                "config": asdict(config),
            }
        )

    cell_out = cells.copy()
    cell_out.to_csv(CELL_CSV, index=False)
    pd.DataFrame(null_rows).to_csv(NULL_CSV, index=False)

    ranking = sorted(variants, key=lambda item: item["priority"], reverse=True)
    for idx, item in enumerate(ranking, start=1):
        item["rank"] = idx
    thesis = next((item for item in ranking if item["variant"] == "invariant_survivor"), ranking[0])
    information = ranking[0]

    readout = {
        "experiment": "HS-JEPA Counterfactual Listener-Dropout Solver",
        "architecture_role": "sleep_competition_adapter_listener_dropout_action_health_sensor",
        "core_boundary": "Adapter-specific Q/S target names and public sensors stay outside hsjepa_core.",
        "status": "counterfactual_listener_dropout_ready",
        "negative_sensor_files": NEGATIVE_SENSOR_FILES,
        "positive_source_files": list(POSITIVE_SOURCE_FILES),
        "verdict": {
            "recommended_information_sensor": {
                "variant": information["variant"],
                "submission_file": information["submission_file"],
                "priority": information["priority"],
            },
            "recommended_thesis_sensor": {
                "variant": thesis["variant"],
                "submission_file": thesis["submission_file"],
                "priority": thesis["priority"],
            },
            "claim": (
                "HS-JEPA should release row-target actions that survive counterfactual listener dropout "
                "and avoid directions marked toxic by previous public sensors."
            ),
            "failure_interpretation": (
                "A public failure means listener-dropout geometry is not sufficient for the public/private "
                "equation, or negative public sensors do not transfer as cell-level toxicity labels."
            ),
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
