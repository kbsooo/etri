#!/usr/bin/env python3
"""Probe listener-invariant contrastive alignment for HS-JEPA.

This probe asks whether listener responsibility and route-invariant action
health point to the same row-local bundles.  A strong HS-JEPA decoder should
not simply move cells with high listener score; it should move them when the
candidate action also preserves the learned human-state/output invariant.
"""

from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

LISTENER_RANKED = ROOT / "paper_hsjepa_core" / "outputs" / "listener_responsibility_jepa" / "listener_responsibility_ranked_cells.csv"
BRIDGE_TABLES = {
    "stagebridge": {
        "candidates": ROOT / "paper_hsjepa_core" / "outputs" / "stage_bridge_conservation_solver" / "stage_bridge_stagebridge_jackpot_candidates.csv",
        "selected": ROOT / "paper_hsjepa_core" / "outputs" / "stage_bridge_conservation_solver" / "stage_bridge_stagebridge_jackpot_selected.csv",
        "score_col": "solver_score",
    },
    "s2hub": {
        "candidates": ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_bridge_solver" / "s2hub_s2hub_jackpot_raw_candidates.csv",
        "selected": ROOT / "paper_hsjepa_core" / "outputs" / "s2hub_bridge_solver" / "s2hub_s2hub_jackpot_selected.csv",
        "score_col": "s2hub_score",
    },
}

REPORT_JSON = OUT / "listener_invariant_contrastive_probe.json"
REPORT_MD = OUT / "listener_invariant_contrastive_probe_ko.md"
SCORED_CSV = OUT / "listener_invariant_contrastive_scored_bundles.csv"


def rank01(values: pd.Series | np.ndarray, ascending: bool = True) -> pd.Series:
    s = pd.Series(values).astype(np.float64).replace([np.inf, -np.inf], np.nan)
    if s.notna().any():
        s = s.fillna(float(s.median()))
    else:
        s = s.fillna(0.0)
    return s.rank(method="average", pct=True, ascending=ascending).astype(np.float64)


def spearman(a: pd.Series, b: pd.Series) -> float | None:
    if len(a) < 3 or a.nunique(dropna=True) < 2 or b.nunique(dropna=True) < 2:
        return None
    return float(a.rank().corr(b.rank()))


def fmt(value: object, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    try:
        val = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(val):
        return "n/a"
    return f"{val:.{digits}f}"


def load_listener() -> pd.DataFrame:
    lr = pd.read_csv(LISTENER_RANKED)
    lr["flat_idx"] = lr["flat_idx"].astype(int)
    lr["sign"] = lr["sign"].astype(int)
    cols = [
        "flat_idx",
        "sign",
        "selection_score",
        "responsibility_score",
        "listener_benefit_rank",
        "source_consensus_rank",
        "human_state_responsibility",
        "h088_safe_rank",
    ]
    return lr[[c for c in cols if c in lr]].drop_duplicates(["flat_idx", "sign"])


def signed_listener_lookup(listener: pd.DataFrame, flat: pd.Series, step: pd.Series, prefix: str) -> pd.DataFrame:
    key = pd.DataFrame({"flat_idx": flat.astype(int), "sign": np.sign(step).astype(int)})
    key["sign"] = key["sign"].replace(0, 1)
    merged = key.merge(listener, on=["flat_idx", "sign"], how="left")
    for col in [
        "selection_score",
        "responsibility_score",
        "listener_benefit_rank",
        "source_consensus_rank",
        "human_state_responsibility",
        "h088_safe_rank",
    ]:
        if col not in merged:
            merged[col] = 0.0
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)
    return merged.add_prefix(prefix)


def score_bundle_table(name: str, listener: pd.DataFrame) -> pd.DataFrame:
    paths = BRIDGE_TABLES[name]
    candidates = pd.read_csv(paths["candidates"])
    selected = pd.read_csv(paths["selected"])
    selected_keys = set(zip(selected["driver_flat"].astype(int), selected["bridge_flat"].astype(int), selected["driver_step"].round(12), selected["bridge_step"].round(12)))

    scored = candidates.copy()
    scored["probe_name"] = name
    scored["selected_by_existing_decoder"] = [
        (int(r.driver_flat), int(r.bridge_flat), round(float(r.driver_step), 12), round(float(r.bridge_step), 12)) in selected_keys
        for r in scored.itertuples(index=False)
    ]
    driver = signed_listener_lookup(listener, scored["driver_flat"], scored["driver_step"], "driver_")
    bridge = signed_listener_lookup(listener, scored["bridge_flat"], scored["bridge_step"], "bridge_")
    scored = pd.concat([scored.reset_index(drop=True), driver, bridge], axis=1)
    scored["listener_pair_score"] = (
        0.46 * scored["driver_selection_score"]
        + 0.30 * scored["bridge_selection_score"]
        + 0.14 * scored["driver_human_state_responsibility"]
        + 0.10 * scored["bridge_human_state_responsibility"]
    )
    scored["route_safety_score"] = rank01(-scored["route_energy_delta"])
    scored["public_utility_score"] = rank01(scored["public_utility"])
    scored["toxicity_safety_score"] = 1.0 - rank01(scored["driver_h088_alignment"])
    scored["listener_rank"] = rank01(scored["listener_pair_score"])
    scored["contrastive_score"] = (
        0.34 * scored["listener_rank"]
        + 0.34 * scored["route_safety_score"]
        + 0.20 * scored["public_utility_score"]
        + 0.12 * scored["toxicity_safety_score"]
    )
    return scored


def table_metrics(scored: pd.DataFrame, name: str) -> dict[str, object]:
    selected = scored["selected_by_existing_decoder"].astype(bool)
    high_listener = scored["listener_rank"] >= scored["listener_rank"].quantile(0.75)
    high_route = scored["route_safety_score"] >= scored["route_safety_score"].quantile(0.75)
    low_listener = scored["listener_rank"] <= scored["listener_rank"].quantile(0.25)
    low_route = scored["route_safety_score"] <= scored["route_safety_score"].quantile(0.25)
    top_k = int(selected.sum())
    contrastive_selected = scored.sort_values("contrastive_score", ascending=False, kind="mergesort").head(top_k)
    existing_keys = set(zip(scored.loc[selected, "driver_flat"].astype(int), scored.loc[selected, "bridge_flat"].astype(int)))
    contrastive_keys = set(zip(contrastive_selected["driver_flat"].astype(int), contrastive_selected["bridge_flat"].astype(int)))
    overlap = existing_keys & contrastive_keys
    return {
        "probe": name,
        "candidate_bundles": int(len(scored)),
        "existing_selected_bundles": top_k,
        "listener_route_spearman": spearman(scored["listener_pair_score"], scored["route_safety_score"]),
        "listener_public_spearman": spearman(scored["listener_pair_score"], scored["public_utility_score"]),
        "listener_existing_solver_spearman": spearman(scored["listener_pair_score"], scored[BRIDGE_TABLES[name]["score_col"]]),
        "selected_listener_mean": float(scored.loc[selected, "listener_pair_score"].mean()),
        "candidate_listener_mean": float(scored["listener_pair_score"].mean()),
        "selected_route_safety_mean": float(scored.loc[selected, "route_safety_score"].mean()),
        "candidate_route_safety_mean": float(scored["route_safety_score"].mean()),
        "selected_public_utility_mean": float(scored.loc[selected, "public_utility"].mean()),
        "candidate_public_utility_mean": float(scored["public_utility"].mean()),
        "high_listener_low_route_rate": float((high_listener & low_route).mean()),
        "high_route_low_listener_rate": float((high_route & low_listener).mean()),
        "high_listener_high_route_rate": float((high_listener & high_route).mean()),
        "contrastive_topk_overlap_with_existing": len(overlap),
        "contrastive_topk_overlap_rate": len(overlap) / top_k if top_k else 0.0,
        "contrastive_route_safety_mean": float(contrastive_selected["route_safety_score"].mean()),
        "contrastive_listener_mean": float(contrastive_selected["listener_pair_score"].mean()),
        "contrastive_public_utility_mean": float(contrastive_selected["public_utility"].mean()),
    }


def verdict(metrics: list[dict[str, object]]) -> dict[str, object]:
    mean_listener_route = float(np.mean([m["listener_route_spearman"] for m in metrics if m["listener_route_spearman"] is not None]))
    mean_overlap = float(np.mean([m["contrastive_topk_overlap_rate"] for m in metrics]))
    mean_conflict = float(np.mean([m["high_listener_low_route_rate"] for m in metrics]))
    if mean_listener_route >= 0.20 and mean_overlap >= 0.45:
        status = "listener_invariant_decoder_promising"
    elif mean_listener_route >= 0.05 and mean_conflict <= 0.10:
        status = "listener_invariant_decoder_alive_but_weak"
    else:
        status = "listener_invariant_decoder_not_ready"
    return {
        "status": status,
        "mean_listener_route_spearman": mean_listener_route,
        "mean_contrastive_overlap_rate": mean_overlap,
        "mean_high_listener_low_route_rate": mean_conflict,
        "interpretation": (
            "Listener responsibility and route-invariant safety are aligned enough to justify a contrastive decoder experiment."
            if status != "listener_invariant_decoder_not_ready"
            else "Listener responsibility and invariant safety are not sufficiently aligned; use this as a diagnostic before making new submissions."
        ),
    }


def build_markdown(report: dict[str, object]) -> str:
    rows = ["| Probe | Listener-route rho | Existing overlap | Conflict rate | Selected listener | Contrastive listener |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for m in report["metrics"]:
        rows.append(
            f"| `{m['probe']}` | `{fmt(m['listener_route_spearman'])}` | `{fmt(m['contrastive_topk_overlap_rate'])}` | "
            f"`{fmt(m['high_listener_low_route_rate'])}` | `{fmt(m['selected_listener_mean'])}` | `{fmt(m['contrastive_listener_mean'])}` |"
        )
    v = report["verdict"]
    return "\n".join(
        [
            "# Listener-Invariant Contrastive Probe",
            "",
            "이 프로브는 listener responsibility와 route-invariant safety가 같은 action bundle을 가리키는지 확인한다.",
            "",
            "## Verdict",
            "",
            f"- Status: `{v['status']}`",
            f"- Mean listener-route Spearman: `{fmt(v['mean_listener_route_spearman'])}`",
            f"- Mean contrastive overlap with existing decoder: `{fmt(v['mean_contrastive_overlap_rate'])}`",
            f"- Mean high-listener/low-route conflict rate: `{fmt(v['mean_high_listener_low_route_rate'])}`",
            "",
            v["interpretation"],
            "",
            "## Metrics",
            "",
            *rows,
            "",
            "## Boundary",
            "",
            "- 이 프로브는 새 submission을 만들지 않는다.",
            "- 목적은 action-health decoder의 다음 big-bet이 살아 있는지 확인하는 것이다.",
            "- conflict가 높으면 listener score만 믿는 decoder는 public/private 모두에서 위험하다.",
            "",
        ]
    )


def run() -> dict[str, object]:
    listener = load_listener()
    frames = []
    metrics = []
    for name in BRIDGE_TABLES:
        scored = score_bundle_table(name, listener)
        frames.append(scored)
        metrics.append(table_metrics(scored, name))
    combined = pd.concat(frames, ignore_index=True)
    report = {
        "package": "Listener-Invariant Contrastive Probe",
        "status": "probe_ready",
        "uses_public_score_ledger": False,
        "uses_submission_source_artifacts": True,
        "verdict": verdict(metrics),
        "metrics": metrics,
    }
    combined.to_csv(SCORED_CSV, index=False)
    REPORT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    REPORT_MD.write_text(build_markdown(report), encoding="utf-8")
    result = {
        "report_json": str(REPORT_JSON.resolve()),
        "report_md": str(REPORT_MD.resolve()),
        "scored_csv": str(SCORED_CSV.resolve()),
        "status": report["verdict"]["status"],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return result


if __name__ == "__main__":
    run()
