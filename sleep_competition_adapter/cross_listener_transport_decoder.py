#!/usr/bin/env python3
"""Cross-listener transport decoder for the sleep competition adapter.

This is a competition-adapter big bet, not generic HS-JEPA core code.

The previous target-listener route-lift submission was a useful negative
sensor: S2/listener posterior found coherent objective-stage cells, but
releasing those cells directly made public LB worse.  This decoder uses the
same listener evidence differently:

    target-listener posterior is not an action generator;
    it is a transport calibrator over actions proposed by route/fusion/core.

In HS-JEPA terms, the hidden human state is allowed to move probability mass
between listeners only when an independent action decoder already proposes the
cell and the listener transport field confirms it.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
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

from sleep_competition_adapter.decoder_order_jury_solver import load_base, z_and_p  # noqa: E402
from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (  # noqa: E402
    TARGETS,
    clip_prob,
    short_hash,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "cross_listener_transport_decoder"
OUT.mkdir(parents=True, exist_ok=True)

STRICT_CELLS = HERE / "outputs" / "decoder_order_jury_solver" / "decoder_order_jury_cells.csv"
BOUNDARY_CELLS = HERE / "outputs" / "decoder_boundary_tomography_solver" / "decoder_boundary_tomography_cells.csv"
TARGET_LISTENER_AUDIT = (
    ROOT
    / "paper_hsjepa_core"
    / "outputs"
    / "target_listener_route_lift_solver"
    / "s2hub_listener_lift_jackpot_action_audit.csv"
)
TARGET_LISTENER_READOUT = (
    ROOT / "paper_hsjepa_core" / "outputs" / "target_listener_route_lift_solver" / "target_listener_route_lift_readout.json"
)
PUBLIC_LEDGER = ROOT / "data_analytics" / "hsjepa_public_score_ledger.csv"
TARGET_LISTENER_NEGATIVE_PUBLIC_LB = 0.5680255019

READOUT_JSON = OUT / "cross_listener_transport_readout.json"
READOUT_MD = OUT / "cross_listener_transport_readout_ko.md"
CELL_CSV = OUT / "cross_listener_transport_cells.csv"
NULL_CSV = OUT / "cross_listener_transport_null_stress.csv"


@dataclass(frozen=True)
class TransportConfig:
    name: str
    boundary_classes: tuple[str, ...]
    require_cell_listener: bool
    require_row_s2_listener: bool
    min_transport_score: float
    max_cells: int
    max_extra_cells: int
    strict_base_scale: float
    extra_base_scale: float
    listener_gain: float
    s2_gain: float
    probe_role: str


CONFIGS = [
    TransportConfig(
        name="strict_listener_recalibrated",
        boundary_classes=("strict_jury",),
        require_cell_listener=True,
        require_row_s2_listener=True,
        min_transport_score=0.42,
        max_cells=22,
        max_extra_cells=0,
        strict_base_scale=0.84,
        extra_base_scale=0.0,
        listener_gain=0.18,
        s2_gain=0.08,
        probe_role="tests whether strict jury actions should be amplitude-calibrated by listener posterior",
    ),
    TransportConfig(
        name="listener_confirmed_shadow",
        boundary_classes=("strict_jury", "consensus_shadow"),
        require_cell_listener=True,
        require_row_s2_listener=True,
        min_transport_score=0.44,
        max_cells=28,
        max_extra_cells=6,
        strict_base_scale=0.82,
        extra_base_scale=0.34,
        listener_gain=0.20,
        s2_gain=0.09,
        probe_role="tests whether target-listener confirmed shadow cells are safer than broad shadow release",
    ),
    TransportConfig(
        name="objective_listener_island_probe",
        boundary_classes=("strict_jury", "consensus_shadow", "route_only", "fusion_only"),
        require_cell_listener=True,
        require_row_s2_listener=True,
        min_transport_score=0.47,
        max_cells=34,
        max_extra_cells=12,
        strict_base_scale=0.80,
        extra_base_scale=0.28,
        listener_gain=0.22,
        s2_gain=0.10,
        probe_role="tests whether an objective-listener island exists outside the current public row-state support",
    ),
    TransportConfig(
        name="row_s2_transport_pressure",
        boundary_classes=("strict_jury", "consensus_shadow", "route_only", "fusion_only"),
        require_cell_listener=False,
        require_row_s2_listener=True,
        min_transport_score=0.50,
        max_cells=36,
        max_extra_cells=14,
        strict_base_scale=0.78,
        extra_base_scale=0.24,
        listener_gain=0.16,
        s2_gain=0.16,
        probe_role="tests whether row-level S2 listener responsibility can release cells not directly selected by the listener-lift teacher",
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


def rank01(values: pd.Series) -> pd.Series:
    if values.empty:
        return pd.Series(dtype=float)
    return values.astype(float).rank(pct=True, method="average").fillna(0.0)


def load_public_score(file_name: str) -> float | None:
    if not PUBLIC_LEDGER.exists():
        return None
    ledger = pd.read_csv(PUBLIC_LEDGER)
    hit = ledger.loc[ledger["file"].eq(file_name), "public_lb"]
    if hit.empty:
        if file_name == "submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv":
            return TARGET_LISTENER_NEGATIVE_PUBLIC_LB
        return None
    return float(hit.iloc[-1])


def load_cells() -> pd.DataFrame:
    strict = pd.read_csv(STRICT_CELLS)
    strict = strict[strict["config"].eq("family_supermajority")].copy()
    strict["boundary_class"] = "strict_jury"
    strict["source_table"] = "decoder_order_jury"
    strict["action_delta"] = strict["released_delta"].astype(float)
    strict["action_score"] = strict["consensus_score"].astype(float)
    strict["opposed_weight"] = 0.0

    boundary = pd.read_csv(BOUNDARY_CELLS).copy()
    boundary = boundary[boundary["boundary_class"].isin(["consensus_shadow", "route_only", "fusion_only"])].copy()
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
    return cells.drop_duplicates(["cell_key", "boundary_class"], keep="first").reset_index(drop=True)


def load_listener_evidence() -> tuple[pd.DataFrame, dict[str, Any]]:
    if not TARGET_LISTENER_AUDIT.exists():
        raise FileNotFoundError(TARGET_LISTENER_AUDIT)
    audit = pd.read_csv(TARGET_LISTENER_AUDIT)
    audit["row"] = audit["row"].astype(int)
    audit["target"] = audit["target"].astype(str)
    audit["cell_key"] = audit["row"].astype(str) + ":" + audit["target"]
    audit["listener_source_is_extra"] = audit["source"].astype(str).eq("listener_lift_extra")

    row_s2 = (
        audit[audit["target"].eq("S2")]
        .groupby("row")
        .agg(
            row_s2_listener_prob=("full_listener_prob", "max"),
            row_s2_listener_score=("listener_score", "max"),
            row_s2_move=("decoded_logit_move", "mean"),
        )
        .reset_index()
    )
    row_any = (
        audit.groupby("row")
        .agg(
            row_listener_cells=("cell_key", "count"),
            row_listener_targets=("target", "nunique"),
            row_listener_mean_prob=("full_listener_prob", "mean"),
            row_listener_mean_score=("listener_score", "mean"),
            row_listener_extra_cells=("listener_source_is_extra", "sum"),
        )
        .reset_index()
    )
    audit = audit.merge(row_s2, on="row", how="left").merge(row_any, on="row", how="left")

    readout: dict[str, Any] = {}
    if TARGET_LISTENER_READOUT.exists():
        readout = json.loads(TARGET_LISTENER_READOUT.read_text(encoding="utf-8"))
    return audit, readout


def enrich_cells(cells: pd.DataFrame, audit: pd.DataFrame) -> pd.DataFrame:
    listener_cols = [
        "cell_key",
        "source",
        "full_listener_prob",
        "full_listener_move",
        "listener_score",
        "teacher_has_action",
        "listener_source_is_extra",
        "route_energy_delta",
        "row_s2_listener_prob",
        "row_s2_listener_score",
        "row_s2_move",
        "row_listener_cells",
        "row_listener_targets",
        "row_listener_mean_prob",
        "row_listener_mean_score",
        "row_listener_extra_cells",
    ]
    out = cells.merge(audit[listener_cols].drop_duplicates("cell_key"), on="cell_key", how="left")
    out["listener_confirmed"] = out["full_listener_prob"].notna()
    for col in [
        "full_listener_prob",
        "full_listener_move",
        "listener_score",
        "row_s2_listener_prob",
        "row_s2_listener_score",
        "row_s2_move",
        "row_listener_cells",
        "row_listener_targets",
        "row_listener_mean_prob",
        "row_listener_mean_score",
        "row_listener_extra_cells",
    ]:
        out[col] = out[col].fillna(0.0).astype(float)
    out["listener_source_is_extra"] = out["listener_source_is_extra"].fillna(False).astype(bool)
    out["target_is_s2"] = out["target"].eq("S2")
    out["target_is_stage_tail"] = out["target"].isin(["S1", "S3", "S4"])
    out["same_listener_direction"] = np.sign(out["action_delta"].astype(float)).eq(
        np.sign(out["full_listener_move"].replace(0.0, np.nan)).fillna(np.sign(out["action_delta"]))
    )
    out["action_score_rank"] = rank01(out["action_score"])
    out["listener_score_rank"] = rank01(out["listener_score"])
    out["row_s2_score_rank"] = rank01(out["row_s2_listener_score"])
    out["row_diversity_rank"] = rank01(out["row_listener_targets"])
    out["cross_listener_transport_score"] = (
        0.28 * out["action_score_rank"]
        + 0.22 * out["listener_score_rank"]
        + 0.20 * out["row_s2_score_rank"]
        + 0.12 * out["family_balance"].astype(float).clip(0, 1)
        + 0.10 * out["vote_coverage"].astype(float).clip(0, 1)
        + 0.08 * out["row_diversity_rank"]
    )
    out.loc[~out["same_listener_direction"], "cross_listener_transport_score"] -= 0.25
    out.loc[out["listener_source_is_extra"], "cross_listener_transport_score"] -= 0.08
    out.loc[out["boundary_class"].eq("fusion_only"), "cross_listener_transport_score"] -= 0.08
    out.loc[out["boundary_class"].eq("route_only"), "cross_listener_transport_score"] -= 0.04
    out.loc[out["target_is_s2"], "cross_listener_transport_score"] += 0.03
    return out.sort_values(
        ["cross_listener_transport_score", "action_score", "listener_score"],
        ascending=[False, False, False],
        kind="mergesort",
    ).reset_index(drop=True)


def select_cells(cells: pd.DataFrame, config: TransportConfig) -> pd.DataFrame:
    pool = cells[cells["boundary_class"].isin(config.boundary_classes)].copy()
    if config.require_cell_listener:
        pool = pool[pool["listener_confirmed"]].copy()
    if config.require_row_s2_listener:
        pool = pool[pool["row_s2_listener_score"].gt(0.0)].copy()
    pool = pool[pool["cross_listener_transport_score"].ge(config.min_transport_score)].copy()
    if pool.empty:
        return pool

    strict = pool[pool["boundary_class"].eq("strict_jury")].copy()
    extra = pool[~pool["boundary_class"].eq("strict_jury")].copy()
    strict = strict.sort_values(
        ["cross_listener_transport_score", "action_score"],
        ascending=[False, False],
        kind="mergesort",
    )
    extra = extra.sort_values(
        ["cross_listener_transport_score", "action_score"],
        ascending=[False, False],
        kind="mergesort",
    ).head(config.max_extra_cells)
    selected = pd.concat([strict, extra], ignore_index=True)
    selected = selected.sort_values(
        ["boundary_class", "cross_listener_transport_score", "action_score"],
        ascending=[True, False, False],
        kind="mergesort",
    ).head(config.max_cells)
    if selected.empty:
        return selected

    scales = []
    for rec in selected.to_dict("records"):
        base_scale = config.strict_base_scale if rec["boundary_class"] == "strict_jury" else config.extra_base_scale
        listener_component = config.listener_gain * finite(rec.get("full_listener_prob"))
        s2_component = config.s2_gain * min(1.0, finite(rec.get("row_s2_listener_score")) / 1.40)
        if rec.get("listener_source_is_extra"):
            listener_component *= 0.75
        scale = float(np.clip(base_scale + listener_component + s2_component, 0.12, 1.12))
        scales.append(scale)
    selected = selected.copy()
    selected["transport_scale"] = scales
    selected["released_delta"] = selected["action_delta"].astype(float) * selected["transport_scale"].astype(float)
    selected["config"] = config.name
    return selected.reset_index(drop=True)


def score_cells(frame: pd.DataFrame) -> dict[str, float]:
    if frame.empty:
        return {
            "cells": 0.0,
            "rows": 0.0,
            "extra_cells": 0.0,
            "mean_transport_score": 0.0,
            "mean_listener_score": 0.0,
            "mean_row_s2_score": 0.0,
            "mean_action_score": 0.0,
            "same_listener_direction_rate": 0.0,
            "strict_rate": 0.0,
            "shadow_rate": 0.0,
            "route_only_rate": 0.0,
            "fusion_only_rate": 0.0,
            "s2_rate": 0.0,
        }
    return {
        "cells": float(len(frame)),
        "rows": float(frame["row"].nunique()),
        "extra_cells": float((~frame["boundary_class"].eq("strict_jury")).sum()),
        "mean_transport_score": float(frame["cross_listener_transport_score"].mean()),
        "mean_listener_score": float(frame["listener_score"].mean()),
        "mean_row_s2_score": float(frame["row_s2_listener_score"].mean()),
        "mean_action_score": float(frame["action_score"].mean()),
        "same_listener_direction_rate": float(frame["same_listener_direction"].mean()),
        "strict_rate": float(frame["boundary_class"].eq("strict_jury").mean()),
        "shadow_rate": float(frame["boundary_class"].eq("consensus_shadow").mean()),
        "route_only_rate": float(frame["boundary_class"].eq("route_only").mean()),
        "fusion_only_rate": float(frame["boundary_class"].eq("fusion_only").mean()),
        "s2_rate": float(frame["target"].eq("S2").mean()),
    }


def sample_null(cells: pd.DataFrame, selected: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    if selected.empty:
        return selected.copy()
    sampled = []
    for boundary_class, group in selected.groupby("boundary_class"):
        pool = cells[cells["boundary_class"].eq(boundary_class)]
        if pool.empty:
            pool = cells
        sampled.append(
            pool.sample(
                n=len(group),
                replace=len(pool) < len(group),
                random_state=int(rng.integers(0, 2**31 - 1)),
            )
        )
    out = pd.concat(sampled, ignore_index=True)
    out = out.copy()
    out["transport_scale"] = 1.0
    out["released_delta"] = out["action_delta"].astype(float)
    return out


def stress_against_null(cells: pd.DataFrame, selected: pd.DataFrame, seed: int = 20260611, iters: int = 500) -> dict[str, Any]:
    actual = score_cells(selected)
    rng = np.random.default_rng(seed)
    null_rows = []
    for idx in range(iters):
        metrics = score_cells(sample_null(cells, selected, rng))
        metrics["iteration"] = idx
        null_rows.append(metrics)
    null = pd.DataFrame(null_rows)
    tests: dict[str, Any] = {}
    if not null.empty:
        for key in [
            "mean_transport_score",
            "mean_listener_score",
            "mean_row_s2_score",
            "mean_action_score",
            "same_listener_direction_rate",
            "s2_rate",
        ]:
            tests[key] = z_and_p(actual[key], null[key].to_list(), higher_is_better=True)
    return {"actual": actual, "tests": tests, "null_rows": null_rows}


def make_submission(
    base: pd.DataFrame,
    base_prob: np.ndarray,
    selected: pd.DataFrame,
    config: TransportConfig,
) -> tuple[Path, Path, dict[str, object]]:
    prob = base_prob.copy()
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_idx"])
        prob[row, target_idx] = clip_prob(prob[row, target_idx] + float(rec["released_delta"]))
    suffix = short_hash(prob)
    file_name = f"submission_hsjepa_cross_listener_transport_{config.name}_{suffix}_uploadsafe.csv"
    root_path = ROOT / file_name
    local_path = OUT / file_name
    write_submission(root_path, base, prob)
    write_submission(local_path, base, prob)
    validation = validate_submission(root_path, base, base_prob)
    return root_path, local_path, validation


def variant_priority(stress: dict[str, Any], validation: dict[str, Any]) -> float:
    tests = stress.get("tests", {})
    actual = stress.get("actual", {})
    transport_z = finite(tests.get("mean_transport_score", {}).get("z"))
    listener_z = finite(tests.get("mean_listener_score", {}).get("z"))
    s2_z = finite(tests.get("mean_row_s2_score", {}).get("z"))
    action_z = finite(tests.get("mean_action_score", {}).get("z"))
    cells = finite(actual.get("cells"))
    extras = finite(actual.get("extra_cells"))
    upload = 1.0 if validation.get("upload_safe") else -1.0
    return (
        0.28 * max(-1.0, min(2.0, transport_z / 3.0))
        + 0.22 * max(-1.0, min(2.0, listener_z / 3.0))
        + 0.18 * max(-1.0, min(2.0, s2_z / 3.0))
        + 0.14 * max(-1.0, min(2.0, action_z / 3.0))
        + 0.10 * min(cells, 34.0) / 34.0
        + 0.05 * min(extras, 14.0) / 14.0
        + 0.03 * upload
    )


def build_markdown(readout: dict[str, Any]) -> str:
    observed = readout.get("observed_public_sensors", [])
    lines = [
        "# Cross-Listener Transport Decoder",
        "",
        "## 핵심 해석",
        "",
        "이 모듈은 실패한 target-listener route-lift를 그대로 반복하지 않는다.",
        "listener posterior는 action을 직접 생성하지 않고, route/fusion/core가 제안한 cell의 이동량과 release 경계를 보정하는 transport calibrator로만 사용한다.",
        "",
        "## Verdict",
        "",
        f"- Status: `{readout['status']}`",
        f"- Recommended LB sensor: `{readout['verdict']['recommended_lb_sensor']['submission_file']}`",
        f"- Recommended big-bet sensor: `{readout['verdict']['recommended_big_bet']['submission_file']}`",
        f"- Prior negative sensor: target-listener lift public LB `{readout['negative_sensor']['public_lb']}`",
        "",
    ]
    if observed:
        lines.extend(
            [
                "## Observed Public Sensors",
                "",
                "| Variant | Public LB | Interpretation | File |",
                "| --- | ---: | --- | --- |",
            ]
        )
        for item in observed:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{item['variant']}`",
                        fmt(item.get("public_lb"), 10),
                        item["interpretation"],
                        f"`{item['submission_file']}`",
                    ]
                )
                + " |"
            )
        lines.append("")
    lines.extend(
        [
        "## Ranking",
        "",
        "| Rank | Variant | Cells | Extra | Transport z | Listener z | S2 z | Action z | Public LB | Priority | File |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
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
                    str(int(actual["extra_cells"])),
                    fmt(tests.get("mean_transport_score", {}).get("z")),
                    fmt(tests.get("mean_listener_score", {}).get("z")),
                    fmt(tests.get("mean_row_s2_score", {}).get("z")),
                    fmt(tests.get("mean_action_score", {}).get("z")),
                    fmt(item.get("public_lb_observed"), 10),
                    fmt(item["priority"]),
                    f"`{item['submission_file']}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## What This Tests",
            "",
            "- 좋아지면: target-listener posterior는 직접 action generator가 아니어도, action release/calibration boundary로는 전이된다는 뜻이다.",
            "- 나빠지면: listener posterior는 representation diagnostic으로만 남고, public-safe assignment는 decoder jury/core-health가 계속 맡아야 한다.",
            "- 특히 `objective_listener_island_probe`가 이기면 현재 H057 row-state 밖에도 objective-stage listener island가 있다는 강한 증거다.",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict[str, Any]:
    base, base_prob = load_base()
    cells = enrich_cells(load_cells(), load_listener_evidence()[0])
    cells.to_csv(CELL_CSV, index=False)

    negative_lb = load_public_score("submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv")
    ranking = []
    null_rows = []
    for config in CONFIGS:
        selected = select_cells(cells, config)
        root_path, local_path, validation = make_submission(base, base_prob, selected, config)
        stress = stress_against_null(cells, selected)
        for rec in stress["null_rows"]:
            rec["variant"] = config.name
            null_rows.append(rec)
        public_lb_observed = load_public_score(root_path.name)
        item = {
            "variant": config.name,
            "status": "upload_safe" if validation.get("upload_safe") else "invalid",
            "submission_file": root_path.name,
            "root_path": str(root_path.resolve()),
            "local_path": str(local_path.resolve()),
            "validation": validation,
            "selected_cells": int(len(selected)),
            "stress": {key: value for key, value in stress.items() if key != "null_rows"},
            "public_lb_observed": public_lb_observed,
            "priority": variant_priority(stress, validation),
            "config": asdict(config),
        }
        ranking.append(item)
    pd.DataFrame(null_rows).to_csv(NULL_CSV, index=False)

    ranking = sorted(ranking, key=lambda item: item["priority"], reverse=True)
    for idx, item in enumerate(ranking, start=1):
        item["rank"] = idx
    observed_public = [
        {
            "variant": item["variant"],
            "submission_file": item["submission_file"],
            "public_lb": item["public_lb_observed"],
            "interpretation": (
                "listener-calibrated shadow release did not beat H057; keep listener posterior as a diagnostic/boundary feature, not as the final release gate"
                if item["variant"] == "listener_confirmed_shadow"
                else "public-observed cross-listener variant"
            ),
        }
        for item in ranking
        if item.get("public_lb_observed") is not None
    ]
    readout = {
        "experiment": "Cross-Listener Transport Decoder",
        "architecture_role": "adapter-side listener transport calibrator",
        "status": "cross_listener_transport_ready",
        "negative_sensor": {
            "file": "submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv",
            "public_lb": negative_lb,
            "interpretation": "direct listener-lift is not action-grade; use listener posterior only as a release/calibration prior",
        },
        "verdict": {
            "status": "cross_listener_transport_ready",
            "recommended_lb_sensor": ranking[0],
            "recommended_big_bet": next((item for item in ranking if item["variant"] == "objective_listener_island_probe"), ranking[0]),
            "claim": "Cross-listener evidence should calibrate route/fusion/core actions, not generate actions by itself.",
            "failure_interpretation": "If this loses to strict jury/core-health, listener posterior stays diagnostic and should not control action release.",
        },
        "observed_public_sensors": observed_public,
        "ranking": ranking,
        "outputs": {
            "cells": str(CELL_CSV.resolve()),
            "null_stress": str(NULL_CSV.resolve()),
            "markdown": str(READOUT_MD.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps({"status": readout["status"], "recommended": readout["verdict"]["recommended_lb_sensor"]["submission_file"]}, indent=2))
    return readout


if __name__ == "__main__":
    run()
