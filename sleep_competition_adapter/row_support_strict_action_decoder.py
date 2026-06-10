#!/usr/bin/env python3
"""Row-support gated action decoder for the sleep competition adapter.

This is an adapter-side big bet, not HS-JEPA core code.

The masked row-support objective says that actionable rows are partially
recoverable from portable human/context views.  This decoder asks the next
question:

    Can that row-support representation safely control real row-target actions?

It starts from route-conserving S2/stage bridge bundles, then keeps only bundles
whose rows are supported by the masked row-support sensor and whose cells pass
factorized broad-public / hard-world toxicity checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sleep_competition_adapter.hidden_row_support_sensor_probe import (  # noqa: E402
    INPUT_CSV,
    build_row_frame,
    clean_matrix,
    columns_for_family,
    feature_families,
    fit_sensor,
    rank01,
)
from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (  # noqa: E402
    TARGETS,
    TOL,
    candidate1,
    clip_prob,
    logit,
    short_hash,
    sigmoid,
    validate_submission,
    write_submission,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "row_support_strict_action_decoder"
OUT.mkdir(parents=True, exist_ok=True)

SECTORS_CSV = HERE / "outputs" / "hardworld_toxicity_factorization_sectors.csv"
STAGE_SELECTED = ROOT / "paper_hsjepa_core" / "outputs" / "stage_bridge_conservation_solver" / "stage_bridge_stagebridge_jackpot_selected.csv"
STAGE_CANDIDATES = ROOT / "paper_hsjepa_core" / "outputs" / "stage_bridge_conservation_solver" / "stage_bridge_stagebridge_jackpot_candidates.csv"
S2_SELECTED = ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_bridge_solver" / "s2hub_s2hub_jackpot_selected.csv"
S2_CANDIDATES = ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_bridge_solver" / "s2hub_s2hub_jackpot_raw_candidates.csv"

READOUT_JSON = OUT / "row_support_strict_action_decoder_readout.json"
READOUT_MD = OUT / "row_support_strict_action_decoder_readout_ko.md"
AUDIT_CSV = OUT / "row_support_strict_action_decoder_audit.csv"
NULL_CSV = OUT / "row_support_strict_action_decoder_null_stress.csv"

BOOL_COLS = [
    "teacher_has_action",
    "lrj_has_cell",
    "lrj_teacher_sign_match",
    "broad_safe_hardworld_toxic",
    "broad_toxic_hardworld_safe",
    "hardworld_top_toxic",
    "broad_top_toxic",
    "selected_by_existing_decoder",
]


@dataclass(frozen=True)
class DecoderConfig:
    name: str
    min_row_support_rank: float
    min_driver_joint_safety: float
    min_bundle_joint_safety: float
    min_hardworld_safe: float
    min_broad_safe: float
    max_h088_alignment: float
    min_route_gain: float
    min_source_support: int
    max_bundles: int
    max_bundles_per_row: int
    base_amp: float
    max_amp: float
    min_amp: float


CONFIGS = [
    DecoderConfig(
        name="strict_route_support_gate",
        min_row_support_rank=0.66,
        min_driver_joint_safety=0.54,
        min_bundle_joint_safety=0.50,
        min_hardworld_safe=0.58,
        min_broad_safe=0.42,
        max_h088_alignment=0.64,
        min_route_gain=0.010,
        min_source_support=4,
        max_bundles=22,
        max_bundles_per_row=1,
        base_amp=0.54,
        min_amp=0.50,
        max_amp=0.92,
    ),
    DecoderConfig(
        name="exploratory_route_support_gate",
        min_row_support_rank=0.56,
        min_driver_joint_safety=0.47,
        min_bundle_joint_safety=0.44,
        min_hardworld_safe=0.50,
        min_broad_safe=0.35,
        max_h088_alignment=0.72,
        min_route_gain=0.004,
        min_source_support=3,
        max_bundles=36,
        max_bundles_per_row=1,
        base_amp=0.62,
        min_amp=0.52,
        max_amp=1.02,
    ),
]


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def fmt(value: object, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def z_and_p(actual: float, null_values: list[float], higher_is_better: bool = True) -> dict[str, float]:
    arr = np.asarray(null_values, dtype=np.float64)
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    z = float((actual - float(arr.mean())) / (std + 1e-12))
    p = float((arr >= actual).mean()) if higher_is_better else float((arr <= actual).mean())
    return {"actual": float(actual), "null_mean": float(arr.mean()), "null_std": std, "z": z, "p": p}


def load_sectors() -> pd.DataFrame:
    sectors = pd.read_csv(SECTORS_CSV)
    for col in BOOL_COLS:
        if col in sectors:
            sectors[col] = as_bool(sectors[col])
    return sectors


def row_support_scores() -> pd.DataFrame:
    cell_frame = pd.read_csv(INPUT_CSV)
    row_frame = build_row_frame(cell_frame)
    families = feature_families(cell_frame)
    family = families["portable_row_support_composite"]
    cols = columns_for_family(row_frame, family)
    score_parts: list[pd.DataFrame] = []
    teachers = sorted(row_frame["teacher"].unique())
    for train_teacher in teachers:
        for test_teacher in teachers:
            if train_teacher == test_teacher:
                continue
            train = row_frame.loc[row_frame["teacher"].eq(train_teacher)].copy()
            test = row_frame.loc[row_frame["teacher"].eq(test_teacher)].copy()
            x_train, x_test = clean_matrix(train, test, cols)
            model = fit_sensor(x_train, train["teacher_row_has_action"].to_numpy(dtype=int))
            pred = model.predict_proba(x_test)[:, 1]
            score_parts.append(
                pd.DataFrame(
                    {
                        "row": test["row"].astype(int).to_numpy(),
                        "test_teacher": str(test_teacher),
                        "train_teacher": str(train_teacher),
                        "row_support_score": pred,
                    }
                )
            )
    scores = pd.concat(score_parts, ignore_index=True)
    out = scores.groupby("row", as_index=False).agg(
        row_support_score=("row_support_score", "mean"),
        row_support_min=("row_support_score", "min"),
        row_support_max=("row_support_score", "max"),
    )
    out["row_support_rank"] = rank01(out["row_support_score"])
    out["row_support_min_rank"] = rank01(out["row_support_min"])
    return out


def read_bundle_file(path: Path, source: str, selected_seed: bool) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame = frame.copy()
    frame["bundle_source"] = source
    frame["selected_seed"] = bool(selected_seed)
    if "s2hub_score" not in frame:
        frame["s2hub_score"] = frame.get("solver_score", 0.0)
    frame["route_gain"] = -frame["route_energy_delta"].astype(float)
    return frame


def bundle_pool() -> pd.DataFrame:
    parts = [
        read_bundle_file(STAGE_CANDIDATES, "stagebridge_candidates", False),
        read_bundle_file(S2_CANDIDATES, "s2hub_candidates", False),
        read_bundle_file(STAGE_SELECTED, "stagebridge_selected", True),
        read_bundle_file(S2_SELECTED, "s2hub_selected", True),
    ]
    pool = pd.concat(parts, ignore_index=True)
    pool["_key"] = (
        pool["row"].astype(str)
        + "|"
        + pool["driver_flat"].astype(int).astype(str)
        + "|"
        + pool["bridge_flat"].astype(int).astype(str)
        + "|"
        + np.sign(pool["driver_step"].astype(float)).astype(int).astype(str)
        + "|"
        + np.sign(pool["bridge_step"].astype(float)).astype(int).astype(str)
    )
    pool = pool.sort_values(
        ["selected_seed", "route_gain", "s2hub_score", "solver_score"],
        ascending=[False, False, False, False],
        kind="mergesort",
    ).drop_duplicates("_key", keep="first")
    return pool.reset_index(drop=True)


def lookup_cell(sectors: pd.DataFrame, flat_idx: int, step: float) -> dict[str, object]:
    sign = int(np.sign(float(step)))
    if sign == 0:
        sign = 1
    match = sectors[(sectors["flat_idx"].astype(int) == int(flat_idx)) & (sectors["candidate_sign"].astype(int) == sign)]
    if match.empty:
        return {
            "matched": False,
            "joint_safety_min_rank": 0.54,
            "hardworld_safe_rank": 0.54,
            "broad_safe_rank_ex_hardworld": 0.42,
            "hardworld_top_toxic": False,
            "broad_top_toxic": False,
            "broad_safe_hardworld_toxic": False,
            "responsibility_score": 0.0,
            "selection_score": 0.0,
            "listener_benefit_rank": 0.0,
            "human_state_responsibility": 0.0,
        }
    row = match.sort_values("joint_safety_min_rank", ascending=False).iloc[0].to_dict()
    row["matched"] = True
    return row


def enrich_bundles(pool: pd.DataFrame, sectors: pd.DataFrame, support: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    support_map = support.set_index("row").to_dict("index")
    for rec in pool.to_dict("records"):
        driver = lookup_cell(sectors, int(rec["driver_flat"]), float(rec["driver_step"]))
        bridge = lookup_cell(sectors, int(rec["bridge_flat"]), float(rec["bridge_step"]))
        support_rec = support_map.get(int(rec["row"]), {})
        driver_joint = float(driver["joint_safety_min_rank"])
        bridge_joint = float(bridge["joint_safety_min_rank"])
        driver_hard = float(driver["hardworld_safe_rank"])
        bridge_hard = float(bridge["hardworld_safe_rank"])
        driver_broad = float(driver["broad_safe_rank_ex_hardworld"])
        bridge_broad = float(bridge["broad_safe_rank_ex_hardworld"])
        route_quality = float(rec["route_gain"])
        rows.append(
            {
                **rec,
                "row_support_score": float(support_rec.get("row_support_score", 0.0)),
                "row_support_rank": float(support_rec.get("row_support_rank", 0.0)),
                "row_support_min_rank": float(support_rec.get("row_support_min_rank", 0.0)),
                "driver_matched_toxicity": bool(driver["matched"]),
                "bridge_matched_toxicity": bool(bridge["matched"]),
                "driver_joint_safety": driver_joint,
                "bridge_joint_safety": bridge_joint,
                "bundle_joint_safety": min(driver_joint, bridge_joint),
                "driver_hardworld_safe": driver_hard,
                "bridge_hardworld_safe": bridge_hard,
                "bundle_hardworld_safe": min(driver_hard, bridge_hard),
                "driver_broad_safe": driver_broad,
                "bridge_broad_safe": bridge_broad,
                "bundle_broad_safe": min(driver_broad, bridge_broad),
                "driver_hardworld_top_toxic": bool(driver["hardworld_top_toxic"]),
                "bridge_hardworld_top_toxic": bool(bridge["hardworld_top_toxic"]),
                "driver_broad_top_toxic": bool(driver["broad_top_toxic"]),
                "bridge_broad_top_toxic": bool(bridge["broad_top_toxic"]),
                "driver_conflict": bool(driver["broad_safe_hardworld_toxic"]),
                "bridge_conflict": bool(bridge["broad_safe_hardworld_toxic"]),
                "mean_responsibility": float(np.mean([float(driver["responsibility_score"]), float(bridge["responsibility_score"])])),
                "mean_selection": float(np.mean([float(driver["selection_score"]), float(bridge["selection_score"])])),
                "mean_listener_benefit": float(np.mean([float(driver["listener_benefit_rank"]), float(bridge["listener_benefit_rank"])])),
                "mean_human_state_responsibility": float(np.mean([float(driver["human_state_responsibility"]), float(bridge["human_state_responsibility"])])),
                "route_quality_raw": route_quality,
            }
        )
    out = pd.DataFrame(rows)
    out["route_quality_rank"] = rank01(out["route_quality_raw"])
    out["support_route_safety_score"] = (
        0.30 * out["row_support_rank"].astype(float)
        + 0.22 * out["route_quality_rank"].astype(float)
        + 0.20 * out["bundle_joint_safety"].astype(float)
        + 0.10 * out["mean_selection"].astype(float)
        + 0.08 * out["mean_listener_benefit"].astype(float)
        + 0.06 * out["mean_human_state_responsibility"].astype(float)
        + 0.04 * out["source_support"].astype(float).clip(0, 8) / 8.0
    )
    out["support_route_safety_score"] = out["support_route_safety_score"].where(
        out["same_direction"].astype(bool),
        out["support_route_safety_score"] - 0.10,
    )
    out["support_route_safety_score"] = out["support_route_safety_score"].where(
        ~(out["driver_conflict"] | out["bridge_conflict"]),
        out["support_route_safety_score"] - 0.20,
    )
    out["support_route_safety_score"] = out["support_route_safety_score"].where(
        ~(out["driver_hardworld_top_toxic"] | out["bridge_hardworld_top_toxic"]),
        out["support_route_safety_score"] - 0.25,
    )
    return out


def passes_config(row: pd.Series, config: DecoderConfig) -> bool:
    return bool(
        row["selected_seed"]
        and row["driver_matched_toxicity"]
        and row["row_support_rank"] >= config.min_row_support_rank
        and row["driver_joint_safety"] >= config.min_driver_joint_safety
        and row["bundle_joint_safety"] >= config.min_bundle_joint_safety
        and row["bundle_hardworld_safe"] >= config.min_hardworld_safe
        and row["bundle_broad_safe"] >= config.min_broad_safe
        and row["route_gain"] >= config.min_route_gain
        and row["source_support"] >= config.min_source_support
        and row["driver_h088_alignment"] <= config.max_h088_alignment
        and bool(row["same_direction"])
        and not bool(row["driver_hardworld_top_toxic"])
        and not bool(row["driver_conflict"])
    )


def select_bundles(enriched: pd.DataFrame, config: DecoderConfig) -> pd.DataFrame:
    pool = enriched[enriched.apply(lambda row: passes_config(row, config), axis=1)].copy()
    pool = pool.sort_values("support_route_safety_score", ascending=False, kind="mergesort")
    selected_rows: list[dict[str, object]] = []
    row_counts: dict[int, int] = {}
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        if row_counts.get(row, 0) >= config.max_bundles_per_row:
            continue
        selected_rows.append(rec)
        row_counts[row] = row_counts.get(row, 0) + 1
        if len(selected_rows) >= config.max_bundles:
            break
    return pd.DataFrame(selected_rows)


def movement_amp(row: pd.Series, config: DecoderConfig) -> float:
    amp = (
        config.base_amp
        + 0.14 * float(row["row_support_rank"])
        + 0.12 * float(row["bundle_joint_safety"])
        + 0.10 * float(row["route_quality_rank"])
        + 0.04 * float(row["mean_listener_benefit"])
    )
    if bool(row["bridge_conflict"]) or bool(row["bridge_hardworld_top_toxic"]):
        amp -= 0.12
    return float(np.clip(amp, config.min_amp, config.max_amp))


def decode(
    selected: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    base_logit: np.ndarray,
    base_grads: np.ndarray,
    semantic_grads: np.ndarray,
    h088_move: np.ndarray,
    config: DecoderConfig,
) -> tuple[np.ndarray, pd.DataFrame, dict[str, object]]:
    move = np.zeros(base_prob.size, dtype=np.float64)
    audit_rows: list[dict[str, object]] = []
    for rec in selected.to_dict("records"):
        amp = movement_amp(pd.Series(rec), config)
        for action_kind in ["driver", "bridge"]:
            flat = int(rec[f"{action_kind}_flat"])
            step = float(rec[f"{action_kind}_step"]) * amp
            move[flat] += step
            audit_rows.append(
                {
                    **rec,
                    "action_kind": action_kind,
                    "flat_idx": flat,
                    "target": rec[f"{action_kind}_target"],
                    "raw_step": float(rec[f"{action_kind}_step"]),
                    "amp": amp,
                    "decoded_logit_move": step,
                }
            )
    prob = clip_prob(sigmoid(base_logit + move).reshape(base_prob.shape))
    audit = pd.DataFrame(audit_rows)
    changed = np.abs(move) > TOL
    bundle_summary = summarize_bundles(selected)
    diagnostics = {
        "variant": config.name,
        "changed_cells": int(changed.sum()),
        "changed_rows": int(len(set(np.where(changed)[0] // len(TARGETS)))),
        "selected_bundles": int(len(selected)),
        "bundle_summary": bundle_summary,
        "listener_metrics": candidate1.candidate_metrics(move, base_grads, semantic_grads, h088_move),
        "target_counts": audit["target"].value_counts().reindex(TARGETS).fillna(0).astype(int).to_dict() if not audit.empty else {},
        "mean_amp": float(audit["amp"].mean()) if not audit.empty else 0.0,
        "min_amp": float(audit["amp"].min()) if not audit.empty else 0.0,
        "max_amp": float(audit["amp"].max()) if not audit.empty else 0.0,
    }
    return prob, audit, diagnostics


def summarize_bundles(frame: pd.DataFrame) -> dict[str, object]:
    if frame.empty:
        return {
            "bundles": 0,
            "mean_row_support_rank": None,
            "mean_route_gain": None,
            "mean_bundle_joint_safety": None,
            "hardworld_top_toxic_bundle_rate": None,
            "conflict_bundle_rate": None,
        }
    return {
        "bundles": int(len(frame)),
        "rows": int(frame["row"].nunique()),
        "mean_row_support_rank": float(frame["row_support_rank"].mean()),
        "mean_route_gain": float(frame["route_gain"].mean()),
        "mean_bundle_joint_safety": float(frame["bundle_joint_safety"].mean()),
        "mean_driver_joint_safety": float(frame["driver_joint_safety"].mean()),
        "mean_support_route_safety_score": float(frame["support_route_safety_score"].mean()),
        "hardworld_top_toxic_bundle_rate": float((frame["driver_hardworld_top_toxic"] | frame["bridge_hardworld_top_toxic"]).mean()),
        "conflict_bundle_rate": float((frame["driver_conflict"] | frame["bridge_conflict"]).mean()),
        "s2_any_rate": float((frame["driver_target"].eq("S2") | frame["bridge_target"].eq("S2")).mean()),
        "selected_seed_rate": float(frame["selected_seed"].mean()),
        "source_counts": frame["bundle_source"].value_counts().to_dict(),
    }


def stress_variant(enriched: pd.DataFrame, selected: pd.DataFrame, config: DecoderConfig, iterations: int = 2000) -> dict[str, object]:
    if selected.empty:
        return {"variant": config.name, "status": "empty_selection"}
    rng = np.random.default_rng(int(hashlib.sha1(config.name.encode("utf-8")).hexdigest()[:8], 16))
    feasible = enriched[
        (enriched["selected_seed"])
        & (enriched["route_gain"] >= config.min_route_gain)
        & (enriched["source_support"] >= config.min_source_support)
        & (enriched["driver_h088_alignment"] <= config.max_h088_alignment)
        & (enriched["same_direction"].astype(bool))
    ].copy()
    if feasible.empty:
        feasible = enriched[enriched["selected_seed"]].copy()
    n = len(selected)
    null_rows = []
    for idx in range(iterations):
        draw = feasible.sample(n=n, replace=len(feasible) < n, random_state=int(rng.integers(0, 2**31 - 1)))
        summary = summarize_bundles(draw)
        null_rows.append(
            {
                "variant": config.name,
                "iteration": idx,
                "mean_row_support_rank": summary["mean_row_support_rank"],
                "mean_route_gain": summary["mean_route_gain"],
                "mean_bundle_joint_safety": summary["mean_bundle_joint_safety"],
                "mean_support_route_safety_score": summary["mean_support_route_safety_score"],
            }
        )
    null = pd.DataFrame(null_rows)
    actual = summarize_bundles(selected)
    return {
        "variant": config.name,
        "status": "stress_ready",
        "iterations": iterations,
        "feasible_pool_size": int(len(feasible)),
        "row_support_rank": z_and_p(float(actual["mean_row_support_rank"]), null["mean_row_support_rank"].tolist(), True),
        "route_gain": z_and_p(float(actual["mean_route_gain"]), null["mean_route_gain"].tolist(), True),
        "bundle_joint_safety": z_and_p(float(actual["mean_bundle_joint_safety"]), null["mean_bundle_joint_safety"].tolist(), True),
        "support_route_safety_score": z_and_p(
            float(actual["mean_support_route_safety_score"]),
            null["mean_support_route_safety_score"].tolist(),
            True,
        ),
        "null_frame": null,
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Variant | File | Bundles | Changed cells | Row support | Route gain | Joint safety | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, item in readout["variants"].items():
        b = item["decode_diagnostics"]["bundle_summary"]
        rows.append(
            f"| `{name}` | `{item['submission_file']}` | `{b['bundles']}` | "
            f"`{item['decode_diagnostics']['changed_cells']}` | `{fmt(b['mean_row_support_rank'])}` | "
            f"`{fmt(b['mean_route_gain'])}` | `{fmt(b['mean_bundle_joint_safety'])}` | "
            f"`{item['validation']['upload_safe']}` |"
        )
    stress_rows = [
        "| Variant | Support z | Route z | Safety z | Combined z |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, item in readout["stress"].items():
        if item.get("status") != "stress_ready":
            stress_rows.append(f"| `{name}` | n/a | n/a | n/a | n/a |")
            continue
        stress_rows.append(
            f"| `{name}` | `{fmt(item['row_support_rank']['z'], 2)}` | "
            f"`{fmt(item['route_gain']['z'], 2)}` | `{fmt(item['bundle_joint_safety']['z'], 2)}` | "
            f"`{fmt(item['support_route_safety_score']['z'], 2)}` |"
        )
    return "\n".join(
        [
            "# Row-Support Strict Action Decoder",
            "",
            "이 실험은 masked row-support representation을 실제 row-target action으로 번역할 수 있는지 보는 adapter-side big bet이다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['verdict']['status']}`",
            f"- Recommended variant: `{readout['verdict']['recommended_variant']}`",
            f"- Reason: {readout['verdict']['reason']}",
            "",
            "## Worldview",
            "",
            "좋은 action은 세 조건을 동시에 만족해야 한다.",
            "",
            "1. row-support가 높은 row여야 한다.",
            "2. route/S2 bridge invariant를 깨지 않아야 한다.",
            "3. broad-public / hard-world toxicity가 낮아야 한다.",
            "",
            "## Generated Candidates",
            "",
            *rows,
            "",
            "## Local Null Stress",
            "",
            *stress_rows,
            "",
            "## Interpretation",
            "",
            "- 좋아지면 masked row-support가 action-health decoder로 승격될 수 있다는 신호다.",
            "- 나빠지면 row-support representation은 살아있지만, route/toxicity 조건만으로는 아직 action assignment가 부족하다는 뜻이다.",
            "- 이 실험은 HS-JEPA core가 아니라 sleep competition adapter의 row-target action solver다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    sectors = load_sectors()
    support = row_support_scores()
    enriched = enrich_bundles(bundle_pool(), sectors, support)

    variants: dict[str, object] = {}
    audits = []
    stress: dict[str, object] = {}
    null_frames = []
    for config in CONFIGS:
        selected = select_bundles(enriched, config)
        prob, audit, diagnostics = decode(
            selected,
            sample,
            base_prob,
            base_logit,
            base_grads,
            semantic_grads,
            h088_move,
            config,
        )
        digest = short_hash(prob)
        name = f"submission_hsjepa_row_support_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / name
        root_path = ROOT / name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        audit["variant"] = config.name
        audits.append(audit)
        stress_result = stress_variant(enriched, selected, config)
        null_frame = stress_result.pop("null_frame", None)
        if null_frame is not None:
            null_frames.append(null_frame)
        stress[config.name] = stress_result
        variants[config.name] = {
            "submission_file": name,
            "local_path": str(local_path.resolve()),
            "root_path": str(root_path.resolve()),
            "config": config.__dict__,
            "decode_diagnostics": diagnostics,
            "validation": validate_submission(root_path, sample, base_prob),
        }

    verdict = build_verdict(variants, stress)
    audit = pd.concat(audits, ignore_index=True) if audits else pd.DataFrame()
    audit.to_csv(AUDIT_CSV, index=False)
    if null_frames:
        pd.concat(null_frames, ignore_index=True).to_csv(NULL_CSV, index=False)
    else:
        pd.DataFrame().to_csv(NULL_CSV, index=False)

    readout = {
        "experiment": "Row-Support Strict Action Decoder",
        "architecture_role": "sleep_competition_adapter_row_target_action_solver",
        "core_boundary": "HS-JEPA core supplies masked row-support representation; this adapter uses route, public-sensitive, and toxicity competition artifacts.",
        "input_claim": "Masked row-support is alive as representation but needs action-health translation.",
        "status": verdict["status"],
        "verdict": verdict,
        "variants": variants,
        "stress": stress,
        "row_support_summary": {
            "rows": int(len(support)),
            "mean_score": float(support["row_support_score"].mean()),
            "std_score": float(support["row_support_score"].std()),
        },
        "bundle_pool_summary": {
            "bundles": int(len(enriched)),
            "selected_seed_bundles": int(enriched["selected_seed"].sum()),
            "mean_route_gain": float(enriched["route_gain"].mean()),
        },
        "outputs": {
            "readout_json": str(READOUT_JSON.resolve()),
            "readout_md": str(READOUT_MD.resolve()),
            "audit_csv": str(AUDIT_CSV.resolve()),
            "null_csv": str(NULL_CSV.resolve()),
        },
    }
    READOUT_JSON.write_text(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    READOUT_MD.write_text(build_markdown(readout), encoding="utf-8")
    print(json.dumps(readout, indent=2, ensure_ascii=False, allow_nan=False))
    return readout


def build_verdict(variants: dict[str, object], stress: dict[str, object]) -> dict[str, object]:
    exploratory = variants.get("exploratory_route_support_gate", {})
    strict = variants.get("strict_route_support_gate", {})
    exp_diag = exploratory.get("decode_diagnostics", {}) if isinstance(exploratory, dict) else {}
    strict_diag = strict.get("decode_diagnostics", {}) if isinstance(strict, dict) else {}
    exp_stress = stress.get("exploratory_route_support_gate", {})
    exp_safety_z = float(exp_stress.get("bundle_joint_safety", {}).get("z", 0.0)) if isinstance(exp_stress, dict) else 0.0
    exp_combined_z = float(exp_stress.get("support_route_safety_score", {}).get("z", 0.0)) if isinstance(exp_stress, dict) else 0.0
    exp_changed = int(exp_diag.get("changed_cells", 0))
    exp_route = float(exp_diag.get("bundle_summary", {}).get("mean_route_gain", 0.0)) if isinstance(exp_diag, dict) else 0.0
    strict_changed = int(strict_diag.get("changed_cells", 0)) if isinstance(strict_diag, dict) else 0

    if exp_changed >= 20 and exp_safety_z >= 2.0 and exp_route > 0.0 and exp_combined_z >= 1.0:
        status = "row_support_action_decoder_alive_with_route_tradeoff"
        recommended = "exploratory_route_support_gate"
        reason = (
            "The exploratory variant moves enough cells to be LB-informative and is strongly safer than local feasible nulls, "
            "but route-gain is not superior to null, so it is a big-bet candidate rather than a safe release candidate."
        )
    elif strict_changed > 0 and exp_safety_z >= 2.0:
        status = "row_support_action_decoder_too_conservative"
        recommended = "strict_route_support_gate"
        reason = (
            "The safety signal works, but the strict gate leaves too few cells for a large LB move. "
            "Use it as a diagnostic unless the goal is a tiny low-risk sensor submission."
        )
    else:
        status = "row_support_action_decoder_not_ready"
        recommended = "none"
        reason = "The decoder does not yet convert row-support into a locally safer and sufficiently large action field."

    return {
        "status": status,
        "recommended_variant": recommended,
        "reason": reason,
        "exploratory_changed_cells": exp_changed,
        "exploratory_safety_z": exp_safety_z,
        "exploratory_combined_z": exp_combined_z,
        "exploratory_mean_route_gain": exp_route,
        "strict_changed_cells": strict_changed,
    }


if __name__ == "__main__":
    run()
