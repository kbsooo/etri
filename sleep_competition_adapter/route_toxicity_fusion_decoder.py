#!/usr/bin/env python3
"""Route-first plus toxicity-fusion action decoder for the sleep adapter.

This is a competition-adapter big bet, not HS-JEPA core code.

The current action-decoder ablation says route-first selection is the sharpest
local signal, while the hard-world toxicity factorization says action-health is
not a scalar public-good score.  This decoder fuses both claims:

    1. Select row-target bundles on the route frontier first.
    2. Require broad-public and hard-world toxicity to agree that the action is
       not toxic.
    3. Use row-support only as a secondary guard.

If this works on public LB, the HS-JEPA adapter gains an action-grade rule:
hidden state is useful only after it is translated through an invariant route
and a factorized action-health field.
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

from sleep_competition_adapter.factorized_toxicity_decoder_candidate import (  # noqa: E402
    TOL,
    candidate1,
    clip_prob,
    short_hash,
    validate_submission,
    write_submission,
)
from sleep_competition_adapter.row_support_strict_action_decoder import (  # noqa: E402
    bundle_pool,
    decode,
    enrich_bundles,
    fmt,
    load_sectors,
    row_support_scores,
    summarize_bundles,
    z_and_p,
)
from sleep_competition_adapter.route_frontier_action_decoder import draw_unique_rows  # noqa: E402


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_toxicity_fusion_decoder"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "route_toxicity_fusion_decoder_readout.json"
READOUT_MD = OUT / "route_toxicity_fusion_decoder_readout_ko.md"
AUDIT_CSV = OUT / "route_toxicity_fusion_decoder_audit.csv"
NULL_CSV = OUT / "route_toxicity_fusion_decoder_null_stress.csv"


@dataclass(frozen=True)
class FusionConfig:
    name: str
    require_selected_seed: bool
    require_open_candidate: bool
    require_s2_any: bool
    require_bridge_matched_toxicity: bool
    min_route_rank: float
    min_row_support_rank: float
    min_bundle_joint_safety: float
    min_bundle_hardworld_safe: float
    min_bundle_broad_safe: float
    min_driver_joint_safety: float
    min_driver_hardworld_safe: float
    min_driver_broad_safe: float
    min_source_support: int
    max_h088_alignment: float
    max_bundles: int
    max_bundles_per_row: int
    base_amp: float
    max_amp: float
    min_amp: float


CONFIGS = [
    FusionConfig(
        name="s2_route_toxicity_fusion",
        require_selected_seed=True,
        require_open_candidate=False,
        require_s2_any=True,
        require_bridge_matched_toxicity=True,
        min_route_rank=0.45,
        min_row_support_rank=0.42,
        min_bundle_joint_safety=0.54,
        min_bundle_hardworld_safe=0.58,
        min_bundle_broad_safe=0.42,
        min_driver_joint_safety=0.56,
        min_driver_hardworld_safe=0.60,
        min_driver_broad_safe=0.44,
        min_source_support=3,
        max_h088_alignment=0.70,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.56,
        min_amp=0.48,
        max_amp=0.90,
    ),
    FusionConfig(
        name="seed_route_toxicity_fusion",
        require_selected_seed=True,
        require_open_candidate=False,
        require_s2_any=False,
        require_bridge_matched_toxicity=True,
        min_route_rank=0.45,
        min_row_support_rank=0.42,
        min_bundle_joint_safety=0.54,
        min_bundle_hardworld_safe=0.58,
        min_bundle_broad_safe=0.42,
        min_driver_joint_safety=0.56,
        min_driver_hardworld_safe=0.60,
        min_driver_broad_safe=0.44,
        min_source_support=3,
        max_h088_alignment=0.70,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.54,
        min_amp=0.48,
        max_amp=0.88,
    ),
    FusionConfig(
        name="open_route_toxicity_fusion",
        require_selected_seed=False,
        require_open_candidate=True,
        require_s2_any=False,
        require_bridge_matched_toxicity=True,
        min_route_rank=0.43,
        min_row_support_rank=0.34,
        min_bundle_joint_safety=0.50,
        min_bundle_hardworld_safe=0.55,
        min_bundle_broad_safe=0.38,
        min_driver_joint_safety=0.52,
        min_driver_hardworld_safe=0.56,
        min_driver_broad_safe=0.40,
        min_source_support=3,
        max_h088_alignment=0.72,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.44,
        min_amp=0.40,
        max_amp=0.74,
    ),
    FusionConfig(
        name="s2_driver_safe_route_fusion",
        require_selected_seed=True,
        require_open_candidate=False,
        require_s2_any=True,
        require_bridge_matched_toxicity=False,
        min_route_rank=0.45,
        min_row_support_rank=0.40,
        min_bundle_joint_safety=0.39,
        min_bundle_hardworld_safe=0.42,
        min_bundle_broad_safe=0.32,
        min_driver_joint_safety=0.50,
        min_driver_hardworld_safe=0.54,
        min_driver_broad_safe=0.32,
        min_source_support=3,
        max_h088_alignment=0.72,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.50,
        min_amp=0.44,
        max_amp=0.82,
    ),
    FusionConfig(
        name="seed_driver_safe_route_fusion",
        require_selected_seed=True,
        require_open_candidate=False,
        require_s2_any=False,
        require_bridge_matched_toxicity=False,
        min_route_rank=0.45,
        min_row_support_rank=0.40,
        min_bundle_joint_safety=0.39,
        min_bundle_hardworld_safe=0.42,
        min_bundle_broad_safe=0.32,
        min_driver_joint_safety=0.50,
        min_driver_hardworld_safe=0.54,
        min_driver_broad_safe=0.32,
        min_source_support=3,
        max_h088_alignment=0.72,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.48,
        min_amp=0.42,
        max_amp=0.80,
    ),
    FusionConfig(
        name="open_driver_safe_route_fusion",
        require_selected_seed=False,
        require_open_candidate=True,
        require_s2_any=False,
        require_bridge_matched_toxicity=False,
        min_route_rank=0.42,
        min_row_support_rank=0.32,
        min_bundle_joint_safety=0.34,
        min_bundle_hardworld_safe=0.42,
        min_bundle_broad_safe=0.26,
        min_driver_joint_safety=0.47,
        min_driver_hardworld_safe=0.50,
        min_driver_broad_safe=0.30,
        min_source_support=3,
        max_h088_alignment=0.74,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.38,
        min_amp=0.35,
        max_amp=0.66,
    ),
]


def route_toxicity_fusion_score(frame: pd.DataFrame) -> pd.Series:
    public_rank = frame["public_utility"].rank(pct=True, method="average").fillna(0.0)
    source_rank = frame["source_support"].astype(float).clip(0, 9) / 9.0
    score = (
        0.26 * frame["route_quality_rank"].astype(float)
        + 0.18 * frame["bundle_joint_safety"].astype(float)
        + 0.14 * frame["bundle_hardworld_safe"].astype(float)
        + 0.09 * frame["bundle_broad_safe"].astype(float)
        + 0.10 * frame["row_support_rank"].astype(float)
        + 0.08 * frame["mean_selection"].astype(float)
        + 0.06 * frame["mean_listener_benefit"].astype(float)
        + 0.04 * frame["mean_human_state_responsibility"].astype(float)
        + 0.03 * public_rank.astype(float)
        + 0.02 * source_rank.astype(float)
    )
    score = score.where(frame["same_direction"].astype(bool), score - 0.20)
    score = score.where(~(frame["driver_conflict"] | frame["bridge_conflict"]), score - 0.25)
    score = score.where(~(frame["driver_hardworld_top_toxic"] | frame["bridge_hardworld_top_toxic"]), score - 0.28)
    score = score.where(~(frame["driver_broad_top_toxic"] | frame["bridge_broad_top_toxic"]), score - 0.18)
    score = score.where(frame["driver_matched_toxicity"] & frame["bridge_matched_toxicity"], score - 0.16)
    return score


def broad_route_pool(enriched: pd.DataFrame, config: FusionConfig) -> pd.DataFrame:
    pool = enriched[
        (enriched["same_direction"].astype(bool))
        & (enriched["source_support"].astype(float) >= config.min_source_support)
        & (enriched["driver_h088_alignment"].astype(float) <= config.max_h088_alignment)
        & (~enriched["driver_conflict"].astype(bool))
        & (~enriched["driver_hardworld_top_toxic"].astype(bool))
    ].copy()
    if config.require_selected_seed:
        pool = pool[pool["selected_seed"].astype(bool)].copy()
    if config.require_open_candidate:
        pool = pool[~pool["selected_seed"].astype(bool)].copy()
    if config.require_s2_any:
        pool = pool[pool["driver_target"].eq("S2") | pool["bridge_target"].eq("S2")].copy()
    return pool


def toxicity_matched_pool(enriched: pd.DataFrame, config: FusionConfig) -> pd.DataFrame:
    pool = broad_route_pool(enriched, config)
    matched = pool[
        (pool["route_quality_rank"].astype(float) >= config.min_route_rank)
        & (pool["row_support_rank"].astype(float) >= config.min_row_support_rank)
        & (pool["bundle_joint_safety"].astype(float) >= config.min_bundle_joint_safety)
        & (pool["bundle_hardworld_safe"].astype(float) >= config.min_bundle_hardworld_safe)
        & (pool["bundle_broad_safe"].astype(float) >= config.min_bundle_broad_safe)
        & (pool["driver_joint_safety"].astype(float) >= config.min_driver_joint_safety)
        & (pool["driver_hardworld_safe"].astype(float) >= config.min_driver_hardworld_safe)
        & (pool["driver_broad_safe"].astype(float) >= config.min_driver_broad_safe)
        & (pool["driver_matched_toxicity"].astype(bool))
        & (~pool["bridge_conflict"].astype(bool))
        & (~pool["bridge_hardworld_top_toxic"].astype(bool))
        & (~pool["driver_broad_top_toxic"].astype(bool))
        & (~pool["bridge_broad_top_toxic"].astype(bool))
    ].copy()
    if config.require_bridge_matched_toxicity:
        matched = matched[matched["bridge_matched_toxicity"].astype(bool)].copy()
    return matched


def select_fusion(enriched: pd.DataFrame, config: FusionConfig) -> pd.DataFrame:
    pool = toxicity_matched_pool(enriched, config)
    if pool.empty:
        return pool
    pool = pool.copy()
    pool["route_toxicity_fusion_score"] = route_toxicity_fusion_score(pool)
    pool = pool.sort_values(
        [
            "route_toxicity_fusion_score",
            "route_quality_rank",
            "bundle_joint_safety",
            "bundle_hardworld_safe",
            "row_support_rank",
        ],
        ascending=[False, False, False, False, False],
        kind="mergesort",
    )
    selected_rows: list[dict[str, Any]] = []
    row_counts: dict[int, int] = {}
    used_cells: set[int] = set()
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        if row_counts.get(row, 0) >= config.max_bundles_per_row:
            continue
        cells = {int(rec["driver_flat"]), int(rec["bridge_flat"])}
        if used_cells & cells:
            continue
        selected_rows.append(rec)
        used_cells.update(cells)
        row_counts[row] = row_counts.get(row, 0) + 1
        if len(selected_rows) >= config.max_bundles:
            break
    return pd.DataFrame(selected_rows)


def summarize_fusion(frame: pd.DataFrame) -> dict[str, object]:
    summary = summarize_bundles(frame)
    if frame.empty:
        summary.update(
            {
                "mean_route_toxicity_fusion_score": None,
                "mean_route_quality_rank": None,
                "mean_bundle_hardworld_safe": None,
                "mean_bundle_broad_safe": None,
                "open_candidate_rate": None,
            }
        )
        return summary
    return {
        **summary,
        "mean_route_toxicity_fusion_score": float(frame["route_toxicity_fusion_score"].mean()),
        "mean_route_quality_rank": float(frame["route_quality_rank"].mean()),
        "mean_bundle_hardworld_safe": float(frame["bundle_hardworld_safe"].mean()),
        "mean_bundle_broad_safe": float(frame["bundle_broad_safe"].mean()),
        "open_candidate_rate": float((~frame["selected_seed"].astype(bool)).mean()),
    }


def stress_variant(
    enriched: pd.DataFrame,
    selected: pd.DataFrame,
    config: FusionConfig,
    iterations: int = 2000,
) -> tuple[dict[str, object], pd.DataFrame]:
    if selected.empty:
        return {"variant": config.name, "status": "empty_selection"}, pd.DataFrame()
    rng = np.random.default_rng(int(hashlib.sha1(config.name.encode("utf-8")).hexdigest()[:8], 16))
    selected = selected.copy()
    selected["route_toxicity_fusion_score"] = route_toxicity_fusion_score(selected)
    actual = summarize_fusion(selected)
    n = len(selected)
    pools = {
        "broad_route": broad_route_pool(enriched, config),
        "toxicity_matched": toxicity_matched_pool(enriched, config),
    }
    stress: dict[str, object] = {
        "variant": config.name,
        "status": "stress_ready",
        "iterations": iterations,
        "actual": actual,
    }
    null_rows = []
    for null_name, pool in pools.items():
        if pool.empty:
            continue
        pool = pool.copy()
        pool["route_toxicity_fusion_score"] = route_toxicity_fusion_score(pool)
        metrics = {
            "mean_route_gain": [],
            "mean_route_quality_rank": [],
            "mean_row_support_rank": [],
            "mean_bundle_joint_safety": [],
            "mean_bundle_hardworld_safe": [],
            "mean_bundle_broad_safe": [],
            "mean_route_toxicity_fusion_score": [],
        }
        for idx in range(iterations):
            draw = draw_unique_rows(pool, n, rng)
            summary = summarize_fusion(draw)
            row = {"variant": config.name, "null_type": null_name, "iteration": idx}
            for key in metrics:
                value = summary.get(key)
                metrics[key].append(float(value) if value is not None else 0.0)
                row[key] = metrics[key][-1]
            null_rows.append(row)
        stress[null_name] = {
            "pool_size": int(len(pool)),
            "route_gain": z_and_p(float(actual["mean_route_gain"]), metrics["mean_route_gain"], True),
            "route_quality_rank": z_and_p(float(actual["mean_route_quality_rank"]), metrics["mean_route_quality_rank"], True),
            "row_support_rank": z_and_p(float(actual["mean_row_support_rank"]), metrics["mean_row_support_rank"], True),
            "bundle_joint_safety": z_and_p(float(actual["mean_bundle_joint_safety"]), metrics["mean_bundle_joint_safety"], True),
            "bundle_hardworld_safe": z_and_p(float(actual["mean_bundle_hardworld_safe"]), metrics["mean_bundle_hardworld_safe"], True),
            "bundle_broad_safe": z_and_p(float(actual["mean_bundle_broad_safe"]), metrics["mean_bundle_broad_safe"], True),
            "route_toxicity_fusion_score": z_and_p(
                float(actual["mean_route_toxicity_fusion_score"]),
                metrics["mean_route_toxicity_fusion_score"],
                True,
            ),
        }
    return stress, pd.DataFrame(null_rows)


def build_verdict(variants: dict[str, object], stress: dict[str, object]) -> dict[str, object]:
    scored = []
    for name, item in variants.items():
        diag = item.get("decode_diagnostics", {})
        variant_stress = stress.get(name, {})
        broad = variant_stress.get("broad_route", {}) if isinstance(variant_stress, dict) else {}
        matched = variant_stress.get("toxicity_matched", {}) if isinstance(variant_stress, dict) else {}
        changed = int(diag.get("changed_cells", 0))
        route_z = float(broad.get("route_gain", {}).get("z", 0.0)) if isinstance(broad, dict) else 0.0
        safety_z = float(matched.get("bundle_joint_safety", {}).get("z", 0.0)) if isinstance(matched, dict) else 0.0
        fusion_z = float(matched.get("route_toxicity_fusion_score", {}).get("z", 0.0)) if isinstance(matched, dict) else 0.0
        upload_safe = bool(item.get("validation", {}).get("upload_safe"))
        scored.append((name, changed, route_z, safety_z, fusion_z, upload_safe))
    viable = [row for row in scored if row[1] >= 20 and row[2] >= 1.5 and row[5]]
    if viable:
        best = sorted(viable, key=lambda row: (row[4], row[3], row[2], row[1]), reverse=True)[0]
        status = "route_toxicity_fusion_decoder_alive"
        reason = (
            "Route-first bundles survive upload safety while also passing factorized hard-world and broad-public "
            "toxicity gates. This is an LB sensor for the fused action decoder."
        )
    else:
        best = sorted(scored, key=lambda row: (row[4], row[2], row[3], row[1]), reverse=True)[0]
        status = "route_toxicity_fusion_decoder_boundary"
        reason = (
            "The fusion rule is locally interpretable, but no variant simultaneously moves enough cells and beats "
            "route/fusion nulls strongly enough. Treat as diagnostic unless public LB is surprisingly good."
        )
    return {
        "status": status,
        "recommended_variant": best[0],
        "reason": reason,
        "variant_scores": [
            {
                "variant": name,
                "changed_cells": changed,
                "broad_route_z": route_z,
                "toxicity_matched_safety_z": safety_z,
                "toxicity_matched_fusion_z": fusion_z,
                "upload_safe": upload_safe,
            }
            for name, changed, route_z, safety_z, fusion_z, upload_safe in scored
        ],
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Variant | File | Bundles | Changed cells | Route gain | Route rank | Joint safety | Hard safe | Broad safe | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, item in readout["variants"].items():
        b = item["decode_diagnostics"]["fusion_summary"]
        rows.append(
            f"| `{name}` | `{item['submission_file']}` | `{b['bundles']}` | "
            f"`{item['decode_diagnostics']['changed_cells']}` | `{fmt(b['mean_route_gain'])}` | "
            f"`{fmt(b['mean_route_quality_rank'])}` | `{fmt(b['mean_bundle_joint_safety'])}` | "
            f"`{fmt(b['mean_bundle_hardworld_safe'])}` | `{fmt(b['mean_bundle_broad_safe'])}` | "
            f"`{item['validation']['upload_safe']}` |"
        )
    stress_rows = [
        "| Variant | Broad route z | Matched fusion z | Matched safety z | Matched hard-safe z | Matched broad-safe z |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, item in readout["stress"].items():
        broad = item.get("broad_route", {})
        matched = item.get("toxicity_matched", {})
        stress_rows.append(
            f"| `{name}` | `{fmt(broad.get('route_gain', {}).get('z'), 2)}` | "
            f"`{fmt(matched.get('route_toxicity_fusion_score', {}).get('z'), 2)}` | "
            f"`{fmt(matched.get('bundle_joint_safety', {}).get('z'), 2)}` | "
            f"`{fmt(matched.get('bundle_hardworld_safe', {}).get('z'), 2)}` | "
            f"`{fmt(matched.get('bundle_broad_safe', {}).get('z'), 2)}` |"
        )
    return "\n".join(
        [
            "# Route-Toxicity Fusion Decoder",
            "",
            "이 실험은 HS-JEPA sleep adapter의 네 번째 action-decoder 계열이다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['verdict']['status']}`",
            f"- Recommended variant: `{readout['verdict']['recommended_variant']}`",
            f"- Reason: {readout['verdict']['reason']}",
            "",
            "## Worldview",
            "",
            "좋은 action은 route frontier 위에 있으면서 broad-public toxicity와 hard-world toxicity를 동시에 통과해야 한다. "
            "따라서 route-first와 action-health-first는 대립이 아니라 순서가 있는 두 단계로 본다.",
            "",
            "## Generated Candidates",
            "",
            *rows,
            "",
            "## Null Stress",
            "",
            *stress_rows,
            "",
            "## Interpretation",
            "",
            "- 좋아지면 HS-JEPA의 action-grade decoder는 `route invariant -> factorized action-health -> sparse decode` 순서가 맞다는 뜻이다.",
            "- 나빠지면 toxicity gate가 public-good route action까지 과하게 잘랐거나, hard-world toxicity가 아직 private-safe field가 아니라는 뜻이다.",
            "- open fusion이 좋아지면 selected seed 밖에도 안전한 hidden route가 존재한다는 강한 증거다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    enriched = enrich_bundles(bundle_pool(), load_sectors(), row_support_scores())
    enriched = enriched.copy()
    enriched["route_toxicity_fusion_score"] = route_toxicity_fusion_score(enriched)

    variants: dict[str, object] = {}
    audits = []
    stress: dict[str, object] = {}
    null_frames = []
    for config in CONFIGS:
        selected = select_fusion(enriched, config)
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
        diagnostics["fusion_summary"] = summarize_fusion(selected)
        digest = short_hash(prob)
        name = f"submission_hsjepa_{config.name}_{digest}_uploadsafe.csv"
        local_path = OUT / name
        root_path = ROOT / name
        write_submission(local_path, sample, prob)
        write_submission(root_path, sample, prob)
        if not audit.empty:
            audit["variant"] = config.name
            audits.append(audit)
        stress_result, null_frame = stress_variant(enriched, selected, config)
        if not null_frame.empty:
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
        "experiment": "Route-Toxicity Fusion Decoder",
        "architecture_role": "sleep_competition_adapter_route_first_factorized_action_health_solver",
        "core_boundary": (
            "HS-JEPA core defines hidden-state, invariant, and action-health interfaces. "
            "This adapter supplies Q/S route bundles, public-sensor toxicity, and upload-safe sparse decoding."
        ),
        "status": verdict["status"],
        "verdict": verdict,
        "variants": variants,
        "stress": stress,
        "bundle_pool_summary": {
            "bundles": int(len(enriched)),
            "selected_seed_bundles": int(enriched["selected_seed"].sum()),
            "mean_route_gain": float(enriched["route_gain"].mean()),
            "mean_route_quality_rank": float(enriched["route_quality_rank"].mean()),
            "mean_bundle_joint_safety": float(enriched["bundle_joint_safety"].mean()),
            "mean_bundle_hardworld_safe": float(enriched["bundle_hardworld_safe"].mean()),
            "mean_bundle_broad_safe": float(enriched["bundle_broad_safe"].mean()),
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


if __name__ == "__main__":
    run()
