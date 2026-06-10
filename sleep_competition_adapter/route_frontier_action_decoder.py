#!/usr/bin/env python3
"""Route-frontier action decoder for the sleep competition adapter.

The previous row-support strict decoder showed a clear boundary:
row-support and toxicity safety were strong, but route-gain was not stronger
than its null.  This adapter-side big bet inverts the priority.

Instead of asking "which supported rows are safe?", it asks:

    Which route-conserving actions sit on the frontier while still preserving
    row-support and toxicity constraints?

This is not HS-JEPA core code.  It is a competition adapter probe for the
action decoder stage.
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
    decode,
    enrich_bundles,
    fmt,
    load_sectors,
    row_support_scores,
    summarize_bundles,
    z_and_p,
    bundle_pool,
)


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "route_frontier_action_decoder"
OUT.mkdir(parents=True, exist_ok=True)

READOUT_JSON = OUT / "route_frontier_action_decoder_readout.json"
READOUT_MD = OUT / "route_frontier_action_decoder_readout_ko.md"
AUDIT_CSV = OUT / "route_frontier_action_decoder_audit.csv"
NULL_CSV = OUT / "route_frontier_action_decoder_null_stress.csv"


@dataclass(frozen=True)
class FrontierConfig:
    name: str
    require_selected_seed: bool
    require_open_candidate: bool
    require_s2_any: bool
    min_route_rank: float
    min_row_support_rank: float
    min_bundle_joint_safety: float
    min_bundle_hardworld_safe: float
    min_bundle_broad_safe: float
    min_source_support: int
    max_h088_alignment: float
    max_bundles: int
    max_bundles_per_row: int
    base_amp: float
    max_amp: float
    min_amp: float


CONFIGS = [
    FrontierConfig(
        name="seed_route_frontier",
        require_selected_seed=True,
        require_open_candidate=False,
        require_s2_any=False,
        min_route_rank=0.45,
        min_row_support_rank=0.45,
        min_bundle_joint_safety=0.35,
        min_bundle_hardworld_safe=0.40,
        min_bundle_broad_safe=0.25,
        min_source_support=3,
        max_h088_alignment=0.72,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.58,
        min_amp=0.50,
        max_amp=0.92,
    ),
    FrontierConfig(
        name="s2_route_frontier",
        require_selected_seed=True,
        require_open_candidate=False,
        require_s2_any=True,
        min_route_rank=0.45,
        min_row_support_rank=0.45,
        min_bundle_joint_safety=0.35,
        min_bundle_hardworld_safe=0.40,
        min_bundle_broad_safe=0.25,
        min_source_support=3,
        max_h088_alignment=0.72,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.60,
        min_amp=0.50,
        max_amp=0.95,
    ),
    FrontierConfig(
        name="open_route_frontier",
        require_selected_seed=False,
        require_open_candidate=True,
        require_s2_any=False,
        min_route_rank=0.45,
        min_row_support_rank=0.35,
        min_bundle_joint_safety=0.20,
        min_bundle_hardworld_safe=0.35,
        min_bundle_broad_safe=0.20,
        min_source_support=3,
        max_h088_alignment=0.72,
        max_bundles=10,
        max_bundles_per_row=1,
        base_amp=0.48,
        min_amp=0.42,
        max_amp=0.80,
    ),
]


def route_frontier_score(frame: pd.DataFrame) -> pd.Series:
    public_rank = frame["public_utility"].rank(pct=True, method="average").fillna(0.0)
    source_rank = frame["source_support"].astype(float).clip(0, 9) / 9.0
    score = (
        0.34 * frame["route_quality_rank"].astype(float)
        + 0.20 * frame["row_support_rank"].astype(float)
        + 0.16 * frame["bundle_joint_safety"].astype(float)
        + 0.09 * frame["mean_selection"].astype(float)
        + 0.07 * frame["mean_listener_benefit"].astype(float)
        + 0.06 * frame["mean_human_state_responsibility"].astype(float)
        + 0.05 * public_rank.astype(float)
        + 0.03 * source_rank.astype(float)
    )
    score = score.where(frame["same_direction"].astype(bool), score - 0.20)
    score = score.where(~(frame["driver_conflict"] | frame["bridge_conflict"]), score - 0.22)
    score = score.where(~(frame["driver_hardworld_top_toxic"] | frame["bridge_hardworld_top_toxic"]), score - 0.25)
    return score


def broad_feasible(enriched: pd.DataFrame, config: FrontierConfig) -> pd.DataFrame:
    pool = enriched[
        (enriched["same_direction"].astype(bool))
        & (enriched["source_support"].astype(float) >= config.min_source_support)
        & (enriched["driver_h088_alignment"].astype(float) <= config.max_h088_alignment)
        & (~enriched["driver_hardworld_top_toxic"].astype(bool))
        & (~enriched["driver_conflict"].astype(bool))
    ].copy()
    if config.require_selected_seed:
        pool = pool[pool["selected_seed"].astype(bool)].copy()
    if config.require_open_candidate:
        pool = pool[~pool["selected_seed"].astype(bool)].copy()
    if config.require_s2_any:
        pool = pool[pool["driver_target"].eq("S2") | pool["bridge_target"].eq("S2")].copy()
    return pool


def matched_feasible(enriched: pd.DataFrame, config: FrontierConfig) -> pd.DataFrame:
    pool = broad_feasible(enriched, config)
    return pool[
        (pool["route_quality_rank"].astype(float) >= config.min_route_rank)
        & (pool["row_support_rank"].astype(float) >= config.min_row_support_rank)
        & (pool["bundle_joint_safety"].astype(float) >= config.min_bundle_joint_safety)
        & (pool["bundle_hardworld_safe"].astype(float) >= config.min_bundle_hardworld_safe)
        & (pool["bundle_broad_safe"].astype(float) >= config.min_bundle_broad_safe)
    ].copy()


def select_frontier(enriched: pd.DataFrame, config: FrontierConfig) -> pd.DataFrame:
    pool = matched_feasible(enriched, config)
    if pool.empty:
        return pool
    pool = pool.copy()
    pool["route_frontier_score"] = route_frontier_score(pool)
    pool = pool.sort_values(
        ["route_frontier_score", "route_quality_rank", "row_support_rank", "bundle_joint_safety"],
        ascending=[False, False, False, False],
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


def summarize_frontier(frame: pd.DataFrame) -> dict[str, object]:
    summary = summarize_bundles(frame)
    if frame.empty:
        summary.update(
            {
                "mean_route_frontier_score": None,
                "mean_route_quality_rank": None,
                "open_candidate_rate": None,
            }
        )
        return summary
    return {
        **summary,
        "mean_route_frontier_score": float(frame["route_frontier_score"].mean()),
        "mean_route_quality_rank": float(frame["route_quality_rank"].mean()),
        "open_candidate_rate": float((~frame["selected_seed"].astype(bool)).mean()),
    }


def draw_unique_rows(pool: pd.DataFrame, n: int, rng: np.random.Generator) -> pd.DataFrame:
    if pool.empty:
        return pool
    rows = []
    row_counts: dict[int, int] = {}
    used_cells: set[int] = set()
    shuffled = pool.sample(frac=1.0, replace=False, random_state=int(rng.integers(0, 2**31 - 1)))
    for rec in shuffled.to_dict("records"):
        row = int(rec["row"])
        if row_counts.get(row, 0) >= 1:
            continue
        cells = {int(rec["driver_flat"]), int(rec["bridge_flat"])}
        if used_cells & cells:
            continue
        rows.append(rec)
        row_counts[row] = 1
        used_cells.update(cells)
        if len(rows) >= n:
            break
    if len(rows) < n:
        extra = pool.sample(n=n - len(rows), replace=True, random_state=int(rng.integers(0, 2**31 - 1)))
        rows.extend(extra.to_dict("records"))
    return pd.DataFrame(rows)


def stress_variant(enriched: pd.DataFrame, selected: pd.DataFrame, config: FrontierConfig, iterations: int = 2000) -> tuple[dict[str, object], pd.DataFrame]:
    if selected.empty:
        return {"variant": config.name, "status": "empty_selection"}, pd.DataFrame()
    rng = np.random.default_rng(int(hashlib.sha1(config.name.encode("utf-8")).hexdigest()[:8], 16))
    selected = selected.copy()
    selected["route_frontier_score"] = route_frontier_score(selected)
    actual = summarize_frontier(selected)
    n = len(selected)
    pools = {
        "broad": broad_feasible(enriched, config),
        "matched": matched_feasible(enriched, config),
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
        pool["route_frontier_score"] = route_frontier_score(pool)
        metrics = {
            "mean_route_gain": [],
            "mean_route_quality_rank": [],
            "mean_row_support_rank": [],
            "mean_bundle_joint_safety": [],
            "mean_route_frontier_score": [],
        }
        for idx in range(iterations):
            draw = draw_unique_rows(pool, n, rng)
            summary = summarize_frontier(draw)
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
            "route_frontier_score": z_and_p(float(actual["mean_route_frontier_score"]), metrics["mean_route_frontier_score"], True),
        }
    return stress, pd.DataFrame(null_rows)


def build_verdict(variants: dict[str, object], stress: dict[str, object]) -> dict[str, object]:
    scored = []
    for name, item in variants.items():
        diag = item.get("decode_diagnostics", {})
        variant_stress = stress.get(name, {})
        broad = variant_stress.get("broad", {}) if isinstance(variant_stress, dict) else {}
        matched = variant_stress.get("matched", {}) if isinstance(variant_stress, dict) else {}
        changed = int(diag.get("changed_cells", 0))
        route_z = float(broad.get("route_gain", {}).get("z", 0.0)) if isinstance(broad, dict) else 0.0
        score_z = float(matched.get("route_frontier_score", {}).get("z", 0.0)) if isinstance(matched, dict) else 0.0
        upload_safe = bool(item.get("validation", {}).get("upload_safe"))
        scored.append((name, changed, route_z, score_z, upload_safe))
    viable = [row for row in scored if row[1] >= 20 and row[2] >= 2.0 and row[4]]
    if viable:
        best = sorted(viable, key=lambda row: (row[3], row[2], row[1]), reverse=True)[0]
        status = "route_frontier_action_decoder_alive_with_matched_boundary"
        reason = (
            "The selected frontier beats broad route nulls and is upload-safe. "
            "Matched-null score remains the boundary, so this is a big-bet LB sensor rather than a default release."
        )
    else:
        best = sorted(scored, key=lambda row: (row[2], row[3], row[1]), reverse=True)[0]
        status = "route_frontier_action_decoder_not_release_ready"
        reason = (
            "No variant simultaneously moved enough cells and beat broad route nulls with enough margin. "
            "Route-frontier selection should remain diagnostic."
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
                "matched_score_z": score_z,
                "upload_safe": upload_safe,
            }
            for name, changed, route_z, score_z, upload_safe in scored
        ],
    }


def build_markdown(readout: dict[str, object]) -> str:
    rows = [
        "| Variant | File | Bundles | Changed cells | Route gain | Route rank | Row support | Open rate | Upload-safe |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, item in readout["variants"].items():
        b = item["decode_diagnostics"]["frontier_summary"]
        rows.append(
            f"| `{name}` | `{item['submission_file']}` | `{b['bundles']}` | "
            f"`{item['decode_diagnostics']['changed_cells']}` | `{fmt(b['mean_route_gain'])}` | "
            f"`{fmt(b['mean_route_quality_rank'])}` | `{fmt(b['mean_row_support_rank'])}` | "
            f"`{fmt(b['open_candidate_rate'])}` | `{item['validation']['upload_safe']}` |"
        )
    stress_rows = [
        "| Variant | Broad route z | Broad score z | Matched route z | Matched score z |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, item in readout["stress"].items():
        broad = item.get("broad", {})
        matched = item.get("matched", {})
        stress_rows.append(
            f"| `{name}` | `{fmt(broad.get('route_gain', {}).get('z'), 2)}` | "
            f"`{fmt(broad.get('route_frontier_score', {}).get('z'), 2)}` | "
            f"`{fmt(matched.get('route_gain', {}).get('z'), 2)}` | "
            f"`{fmt(matched.get('route_frontier_score', {}).get('z'), 2)}` |"
        )
    return "\n".join(
        [
            "# Route-Frontier Action Decoder",
            "",
            "이 실험은 row-support decoder의 약점이었던 route-gain/null 문제를 정면으로 찌른다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{readout['verdict']['status']}`",
            f"- Recommended variant: `{readout['verdict']['recommended_variant']}`",
            f"- Reason: {readout['verdict']['reason']}",
            "",
            "## Worldview",
            "",
            "HS-JEPA action decoder는 좋은 row를 찾는 것만으로는 부족하다. 실제 output을 움직이려면 route manifold의 frontier 위에 있는 action만 살아남아야 한다.",
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
            "- 좋아지면 route-frontier decoder가 hidden row-support를 안전한 action field로 번역할 수 있다는 뜻이다.",
            "- 나빠지면 route energy만으로는 public/private toxicity를 이기지 못한다는 뜻이다.",
            "- open frontier가 좋아지면 기존 public-selected action 후보 밖에도 살아있는 route-invariant action이 있다는 큰 발견이다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    candidate1.ensure_prerequisites()
    sample, base_prob, base_logit, base_grads, semantic_grads, h088_move = candidate1.load_world()
    base_prob = clip_prob(base_prob)
    enriched = enrich_bundles(bundle_pool(), load_sectors(), row_support_scores())
    enriched = enriched.copy()
    enriched["route_frontier_score"] = route_frontier_score(enriched)

    variants: dict[str, object] = {}
    audits = []
    stress: dict[str, object] = {}
    null_frames = []
    for config in CONFIGS:
        selected = select_frontier(enriched, config)
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
        diagnostics["frontier_summary"] = summarize_frontier(selected)
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
        "experiment": "Route-Frontier Action Decoder",
        "architecture_role": "sleep_competition_adapter_route_frontier_action_solver",
        "core_boundary": "HS-JEPA core supplies row-support representation; this adapter asks whether route-frontier actions are safer than null.",
        "status": verdict["status"],
        "verdict": verdict,
        "variants": variants,
        "stress": stress,
        "bundle_pool_summary": {
            "bundles": int(len(enriched)),
            "selected_seed_bundles": int(enriched["selected_seed"].sum()),
            "mean_route_gain": float(enriched["route_gain"].mean()),
            "mean_route_quality_rank": float(enriched["route_quality_rank"].mean()),
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
