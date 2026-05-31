#!/usr/bin/env python3
"""E363: E362 cell-action robustness and anti-collapse probe.

Question:
    E362 produced one passing row x target cell-action candidate.  Is that a
    real hidden lifestyle-action structure, or a one-point threshold accident?

JEPA/data2vec translation:
    context = E362 cell-action anatomy plus row-state/story latent exposures
    target  = robust action-health under counterfactual target ablations,
              donor grafts, row-risk dampers, and scale perturbations
    action  = choose a more robust E362-neighborhood tensor only if actual
              E272/E358 stress supports it.

No public LB is optimized.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e358_rowstate_public_survival_audit import load_anchor, load_row_state, rowstate_features  # noqa: E402
from e359_rowplacement_action_health_probe import (  # noqa: E402
    KEY,
    TARGETS,
    clip_prob,
    load_source,
    logit,
    row_state_scores,
    selector_scores,
    sigmoid,
)
from e360_learned_row_action_health_generator import rowstate_public_scores  # noqa: E402
from e362_row_target_cell_action_generator import candidate_features, pct_rank_good  # noqa: E402


RNG_SEED = 20260531 + 363
UPLOAD_PREFIX = "submission_e363_cellrobust"

E362_SELECTION = OUT / "e362_row_target_cell_action_selection.csv"
E362_SCORES = OUT / "e362_row_target_cell_action_scores.csv"

CANDIDATE_OUT = OUT / "e363_cell_action_robustness_candidates.csv"
SCORE_OUT = OUT / "e363_cell_action_robustness_scores.csv"
SELECTION_OUT = OUT / "e363_cell_action_robustness_selection.csv"
REPORT_OUT = OUT / "e363_cell_action_robustness_report.md"


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def zarr(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    sd = float(np.std(arr))
    if not np.isfinite(sd) or sd < 1.0e-12:
        return np.zeros_like(arr)
    return (arr - float(np.mean(arr))) / sd


def load_delta(path: Path, anchor: pd.DataFrame, anchor_logit: np.ndarray) -> np.ndarray:
    frame = load_source(path, anchor)
    return logit(frame[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit


def materialize(
    anchor: pd.DataFrame,
    anchor_logit: np.ndarray,
    state: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
    selected_delta: np.ndarray,
    delta: np.ndarray,
    meta: dict[str, Any],
    rows: list[dict[str, Any]],
    seen: set[str],
) -> None:
    if not np.isfinite(delta).all() or float(np.abs(delta).sum()) < 1.0e-9:
        return
    digest = hashlib.sha1(np.round(delta, 8).tobytes()).hexdigest()[:12]
    if digest in seen:
        return
    seen.add(digest)
    out = anchor[KEY].copy()
    out[TARGETS] = clip_prob(sigmoid(anchor_logit + delta))
    variant = str(meta["variant"])
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(variant, 112)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    rec = candidate_features(
        source_id=str(meta.get("source_id", "e362_selected")),
        source_delta=selected_delta,
        delta=delta,
        state=state,
        base_cols=base_cols,
        story_cols=story_cols,
        meta=meta,
    )
    rec["file"] = rel(path)
    rec["basename"] = path.name
    rows.append(rec)


def donor_rows(scores: pd.DataFrame) -> pd.DataFrame:
    pools: list[pd.DataFrame] = []
    if "e362_submission_gate" in scores:
        pools.append(scores[scores["e362_submission_gate"].fillna(False).astype(bool)])
    if "e362_nearmiss_gate" in scores:
        pools.append(scores[scores["e362_nearmiss_gate"].fillna(False).astype(bool)].head(8))
    pools.append(scores.sort_values("e362_actual_score", ascending=False).head(16))
    pools.append(scores.sort_values("rowstate_pred_public_loss_mean", ascending=True).head(12))
    pools.append(scores.sort_values("pred_delta_vs_current_p90", ascending=True).head(12))
    out = pd.concat(pools, ignore_index=True).drop_duplicates("file")
    out = out[out["file"].astype(str).str.len() > 0].head(30).reset_index(drop=True)
    return out


def row_gates(state: pd.DataFrame) -> dict[str, np.ndarray]:
    scores = row_state_scores(state)
    risk = scores["risk_core"].to_numpy(dtype=np.float64)
    good = scores["good_core"].to_numpy(dtype=np.float64)
    bad_rate = scores["bad_cluster_rate"].to_numpy(dtype=np.float64)
    gates: dict[str, np.ndarray] = {"identity": np.ones(len(state), dtype=np.float64)}
    for q, damp in [(0.75, 0.55), (0.80, 0.45), (0.85, 0.30), (0.90, 0.15)]:
        gate = np.ones(len(state), dtype=np.float64)
        gate[risk >= np.quantile(risk, q)] = damp
        gates[f"riskq{int(q*100)}_damp{str(damp).replace('.', 'p')}"] = gate
    for q, boost, damp in [(0.80, 1.12, 0.50), (0.90, 1.18, 0.40)]:
        gate = np.ones(len(state), dtype=np.float64)
        gate[good >= np.quantile(good, q)] = boost
        gate[risk >= np.quantile(risk, q)] = damp
        gates[f"goodq{int(q*100)}_riskq{int(q*100)}"] = gate
    gate = np.ones(len(state), dtype=np.float64)
    gate[bad_rate >= np.quantile(bad_rate, 0.80)] = 0.35
    gates["badrate_top20_damp0p35"] = gate
    return gates


def generate_candidates(anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> pd.DataFrame:
    selection = pd.read_csv(E362_SELECTION).iloc[0]
    selected_path = ROOT / str(selection["selected_uploadsafe_file"])
    selected_delta = load_delta(selected_path, anchor, anchor_logit)
    scores = pd.read_csv(E362_SCORES).replace([np.inf, -np.inf], np.nan)
    donors = donor_rows(scores)
    gates = row_gates(state)

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    # Seed: keep E362 itself in the robustness universe.
    materialize(
        anchor,
        anchor_logit,
        state,
        base_cols,
        story_cols,
        selected_delta,
        selected_delta,
        {"variant": "e362_seed_selected", "family": "seed", "source_id": "e362_selected"},
        rows,
        seen,
    )

    # Target-scale neighborhood around the selected cell-action.  This asks
    # whether the Q-story/S-recovery structure has a local basin.
    q1_scales = [0.94, 1.00, 1.04, 1.08]
    q2_scales = [0.90, 1.00, 1.08, 1.16]
    q3_scales = [0.00, 0.45, 0.75, 1.00]
    s1_scales = [0.70, 0.90, 1.00, 1.15, 1.30]
    global_scales = [0.96, 1.00, 1.03, 1.06]
    for gs in global_scales:
        for q1 in q1_scales:
            for q2 in q2_scales:
                for q3 in q3_scales:
                    for s1 in s1_scales:
                        scales = np.ones(len(TARGETS), dtype=np.float64)
                        scales[TARGETS.index("Q1")] = q1
                        scales[TARGETS.index("Q2")] = q2
                        scales[TARGETS.index("Q3")] = q3
                        scales[TARGETS.index("S1")] = s1
                        scales[TARGETS.index("S3")] = 0.0
                        delta = selected_delta * scales[None, :] * gs
                        meta = {
                            "variant": f"e362_scale_g{gs:.2f}_q1{q1:.2f}_q2{q2:.2f}_q3{q3:.2f}_s1{s1:.2f}",
                            "family": "target_scale",
                            "source_id": "e362_selected",
                            "global_scale": gs,
                            "q1_scale2": q1,
                            "q2_scale2": q2,
                            "q3_scale2": q3,
                            "s1_scale2": s1,
                        }
                        materialize(anchor, anchor_logit, state, base_cols, story_cols, selected_delta, delta, meta, rows, seen)

    # Row-risk perturbations over only the visible target cells.
    for gate_id, gate in gates.items():
        if gate_id == "identity":
            continue
        for renorm in [1.00, 1.06, 1.12]:
            delta = selected_delta.copy()
            for target in ["Q1", "Q2", "Q3", "S1"]:
                idx = TARGETS.index(target)
                before = float(np.abs(delta[:, idx]).sum())
                delta[:, idx] *= gate
                after = float(np.abs(delta[:, idx]).sum())
                if after > 1.0e-12:
                    delta[:, idx] *= min(renorm * before / after, 1.35)
            delta[:, TARGETS.index("S3")] = 0.0
            meta = {
                "variant": f"e362_rowgate_{gate_id}_renorm{renorm:.2f}",
                "family": "rowgate",
                "source_id": "e362_selected",
                "row_gate_id": gate_id,
                "row_renorm": renorm,
            }
            materialize(anchor, anchor_logit, state, base_cols, story_cols, selected_delta, delta, meta, rows, seen)

    # Donor blends/grafts ask whether the selected cell law is improved by
    # healthier near-misses without collapsing back to the E360/E361 tradeoff.
    target_sets = {
        "donor_q3": ["Q3"],
        "donor_s1": ["S1"],
        "donor_q3s1": ["Q3", "S1"],
        "donor_q2q3": ["Q2", "Q3"],
        "keep_q12_donor_s": ["S1", "S3"],
    }
    for _, donor in donors.iterrows():
        donor_path = ROOT / str(donor["file"])
        if not donor_path.exists():
            continue
        donor_delta = load_delta(donor_path, anchor, anchor_logit)
        donor_id = safe_id(str(donor["variant"]), 56)
        for w in [0.15, 0.25, 0.35, 0.50, 0.65]:
            delta = (1.0 - w) * selected_delta + w * donor_delta
            delta[:, TARGETS.index("S3")] = 0.0
            meta = {
                "variant": f"e362_donorblend_{donor_id}_w{w:.2f}",
                "family": "donor_blend",
                "source_id": str(donor["variant"]),
                "donor_weight": w,
            }
            materialize(anchor, anchor_logit, state, base_cols, story_cols, selected_delta, delta, meta, rows, seen)
        for graft_id, targets in target_sets.items():
            delta = selected_delta.copy()
            for target in targets:
                idx = TARGETS.index(target)
                delta[:, idx] = donor_delta[:, idx]
            delta[:, TARGETS.index("S3")] = 0.0
            meta = {
                "variant": f"e362_graft_{graft_id}_{donor_id}",
                "family": "donor_graft",
                "source_id": str(donor["variant"]),
                "graft_id": graft_id,
            }
            materialize(anchor, anchor_logit, state, base_cols, story_cols, selected_delta, delta, meta, rows, seen)

    # Target ablations are negative controls.  If a small ablation beats the
    # full action, E362's story should be simplified.
    masks = {
        "q1q2_only": ["Q1", "Q2"],
        "q1q2q3": ["Q1", "Q2", "Q3"],
        "q1q2s1": ["Q1", "Q2", "S1"],
        "q1_only": ["Q1"],
        "q2_only": ["Q2"],
        "s1_only": ["S1"],
        "drop_q3": ["Q1", "Q2", "S1"],
        "drop_s1": ["Q1", "Q2", "Q3"],
    }
    for mask_id, keep in masks.items():
        delta = np.zeros_like(selected_delta)
        for target in keep:
            delta[:, TARGETS.index(target)] = selected_delta[:, TARGETS.index(target)]
        for amp in [1.00, 1.08, 1.16, 1.28]:
            meta = {
                "variant": f"e362_ablate_{mask_id}_amp{amp:.2f}",
                "family": "target_ablation",
                "source_id": "e362_selected",
                "ablation_id": mask_id,
                "ablation_amp": amp,
            }
            materialize(anchor, anchor_logit, state, base_cols, story_cols, selected_delta, delta * amp, meta, rows, seen)

    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def add_e363_scores(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["e363_submission_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00082)
        & (out["rowstate_pred_public_loss_std"] <= 0.00055)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.145)
    )
    out["e363_near_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00095)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.150)
    )
    margins = pd.DataFrame(
        {
            "p90_margin": (-out["pred_delta_vs_current_p90"] - 0.00005) / 0.00001,
            "bad_axis_margin": (0.015 - out["incremental_bad_axis_vs_current"].abs()) / 0.003,
            "rowloss_margin": (0.00082 - out["rowstate_pred_public_loss_mean"]) / 0.00020,
            "rowstd_margin": (0.00055 - out["rowstate_pred_public_loss_std"]) / 0.00015,
            "exposure_margin": (0.145 - out["rowstate_bad_minus_good_exposure"]) / 0.025,
        }
    )
    for col in margins:
        out[col] = margins[col]
    out["e363_min_gate_margin"] = margins.min(axis=1)
    out["e363_family_count"] = out.groupby("family")["variant"].transform("count")
    out["e363_family_submit_count"] = out.groupby("family")["e363_submission_gate"].transform("sum")
    out["e363_family_near_count"] = out.groupby("family")["e363_near_gate"].transform("sum")
    out["e363_family_submit_rate"] = out["e363_family_submit_count"] / out["e363_family_count"].clip(lower=1)
    out["e363_family_near_rate"] = out["e363_family_near_count"] / out["e363_family_count"].clip(lower=1)
    out["e363_robust_score"] = (
        1.20 * pct_rank_good(-out["pred_delta_vs_current_p90"])
        + 1.15 * pct_rank_good(-out["rowstate_pred_public_loss_mean"])
        + 0.85 * pct_rank_good(-out["rowstate_pred_public_loss_std"])
        + 0.95 * pct_rank_good(-out["rowstate_bad_minus_good_exposure"])
        + 0.85 * pct_rank_good(0.015 - out["incremental_bad_axis_vs_current"].abs())
        + 0.45 * pct_rank_good(out["e363_min_gate_margin"])
        + 0.35 * pct_rank_good(out["e363_family_near_rate"])
        + 0.25 * pct_rank_good(-out["share_S3"])
    ) / 6.05
    out = out.sort_values(["e363_submission_gate", "e363_robust_score"], ascending=[False, False]).reset_index(drop=True)
    return out


def select(scored: pd.DataFrame) -> pd.DataFrame:
    e362 = pd.read_csv(E362_SELECTION).iloc[0]
    passed = scored[scored["e363_submission_gate"].fillna(False).astype(bool)].copy()
    if passed.empty:
        selected = scored.head(1).copy()
        selected["decision"] = "no_e363_replacement"
        selected["selected_uploadsafe_file"] = str(e362["selected_uploadsafe_file"])
        selected["reason"] = "No E362-neighborhood perturbation passed the strict combined gate; keep E362 as the pending probe."
    else:
        non_seed = passed[passed["variant"] != "e362_seed_selected"].copy()
        preferred = non_seed if not non_seed.empty else passed
        selected = preferred.sort_values(["e363_family_submit_rate", "e363_robust_score"], ascending=[False, False]).head(1).copy()
        src = ROOT / str(selected.iloc[0]["file"])
        frame = pd.read_csv(src)
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(selected.iloc[0]['variant']), 72)}_{short_hash(frame)}_uploadsafe.csv"
        shutil.copyfile(src, upload)
        selected["decision"] = "select_e363_robust_cellaction_probe"
        selected["selected_uploadsafe_file"] = rel(upload)
        selected["reason"] = "E362-neighborhood perturbation passed strict stress, preserves the E362 source action, and has the strongest family-level pass rate."
    selected.to_csv(SELECTION_OUT, index=False)
    scored.to_csv(SCORE_OUT, index=False)
    return selected


def write_report(scored: pd.DataFrame, selected: pd.DataFrame) -> None:
    top_cols = [
        "variant",
        "family",
        "source_id",
        "e363_submission_gate",
        "e363_near_gate",
        "e363_robust_score",
        "e363_min_gate_margin",
        "e363_family_submit_rate",
        "e363_family_submit_count",
        "e363_family_near_rate",
        "e363_family_near_count",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "rowstate_pred_public_loss_mean",
        "rowstate_pred_public_loss_std",
        "rowstate_bad_minus_good_exposure",
        "move_l1",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "share_S1",
        "share_S3",
        "file",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    summary = (
        scored.groupby("family", dropna=False)
        .agg(
            n=("variant", "count"),
            submit=("e363_submission_gate", "sum"),
            near=("e363_near_gate", "sum"),
            strict=("strict_promote_gate", "sum"),
            submit_rate=("e363_submission_gate", "mean"),
            near_rate=("e363_near_gate", "mean"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_rowloss=("rowstate_pred_public_loss_mean", "min"),
            best_exposure=("rowstate_bad_minus_good_exposure", "min"),
            best_margin=("e363_min_gate_margin", "max"),
            best_score=("e363_robust_score", "max"),
        )
        .reset_index()
        .sort_values(["submit", "near", "best_score"], ascending=[False, False, False])
    )
    lines = [
        "# E363 Cell-Action Robustness Probe",
        "",
        "## Question",
        "",
        "Is E362 a robust row x target lifestyle-state action, or a one-point threshold accident?",
        "",
        "## Method",
        "",
        "- Start from the E362 selected cell-action.",
        "- Generate target-scale, row-risk, donor-blend/graft, and target-ablation perturbations.",
        "- Re-score every materialized file with actual E272 output selector and E358 row-state public-survival.",
        "",
        "## Decision",
        "",
        md_table(selected[["decision", "variant", "selected_uploadsafe_file", "e363_robust_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure", "reason"]], n=5, floatfmt=".9f"),
        "",
        "## Family Summary",
        "",
        md_table(summary, n=20, floatfmt=".9f"),
        "",
        "## Top Candidates",
        "",
        md_table(scored[top_cols].head(50), n=50, floatfmt=".9f"),
        "",
        "## Gate-Passing Candidates",
        "",
        md_table(scored[scored["e363_submission_gate"]][top_cols], n=80, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        "- If several target-scale neighbors pass, E362 is a local basin rather than a one-point accident.",
        "- If only the seed passes, keep E362 but treat it as fragile.",
        "- If a donor graft passes, the E362 law can borrow a healthier target cell from a near-miss.",
        "- If target ablations pass, simplify the hidden action story.",
        "",
        "## Counts",
        "",
        f"- candidates: `{len(scored)}`",
        f"- strict output candidates: `{int(scored['strict_promote_gate'].sum())}`",
        f"- near candidates: `{int(scored['e363_near_gate'].sum())}`",
        f"- submission-gate candidates: `{int(scored['e363_submission_gate'].sum())}`",
        "",
        "## Files",
        "",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(SCORE_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    candidates = generate_candidates(anchor, anchor_logit, state, base_cols, story_cols)
    selector = selector_scores(candidates, anchor)
    rowstate = rowstate_public_scores(selector, anchor, anchor_logit, state, base_cols, story_cols)
    scored = add_e363_scores(rowstate)
    selected = select(scored)
    scored = pd.read_csv(SCORE_OUT)
    write_report(scored, selected)
    print(f"candidates={len(candidates)}")
    print(selected[["decision", "variant", "selected_uploadsafe_file", "e363_robust_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure"]].round(9).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
