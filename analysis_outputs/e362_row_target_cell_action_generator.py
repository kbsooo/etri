#!/usr/bin/env python3
"""E362: row x target cell-action generator.

Question:
    E360/E361 showed that row placement and amplitude alone do not reconcile
    output visibility with row-state health.  Can a target-specific row/action
    pattern solve the contradiction?

JEPA/data2vec translation:
    context = hidden lifestyle row state and story axes
    target  = action-health measured after each target's cells are moved on
              different row-state views
    action  = row x target gate matrix, verified by E272/E358 stress

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
    SOURCES,
    TARGETS,
    clip_prob,
    load_source,
    logit,
    row_state_scores,
    selector_scores,
    sigmoid,
)
from e360_learned_row_action_health_generator import row_gate_basis, rowstate_public_scores  # noqa: E402


RNG_SEED = 20260531 + 362
UPLOAD_PREFIX = "submission_e362_cellaction"

E360_SCORES = OUT / "e360_learned_row_action_health_scores.csv"
E361_SCORES = OUT / "e361_rowaction_amplitude_restore_scores.csv"

CANDIDATE_OUT = OUT / "e362_row_target_cell_action_candidates.csv"
SCORE_OUT = OUT / "e362_row_target_cell_action_scores.csv"
SELECTION_OUT = OUT / "e362_row_target_cell_action_selection.csv"
REPORT_OUT = OUT / "e362_row_target_cell_action_report.md"

N_GENERATE = 1550


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


def pct_rank_good(values: pd.Series | np.ndarray, higher_is_better: bool = True) -> pd.Series:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    if not higher_is_better:
        s = -s
    return s.rank(pct=True, method="average").fillna(0.5)


def source_score(frame: pd.DataFrame) -> pd.Series:
    return (
        1.05 * pct_rank_good(-frame["rowstate_pred_public_loss_mean"])
        + 0.95 * pct_rank_good(-frame["pred_delta_vs_current_p90"])
        + 0.70 * pct_rank_good(0.015 - frame["incremental_bad_axis_vs_current"].abs())
        + 0.65 * pct_rank_good(-frame["rowstate_bad_minus_good_exposure"])
    )


def load_source_deltas(anchor: pd.DataFrame, anchor_logit: np.ndarray) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    for source_id, path in SOURCES.items():
        if path.exists():
            src = load_source(path, anchor)
            out[source_id] = logit(src[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit

    for label, path in [("e360", E360_SCORES), ("e361", E361_SCORES)]:
        if not path.exists():
            continue
        frame = pd.read_csv(path).replace([np.inf, -np.inf], np.nan)
        frame["source_pick_score"] = source_score(frame)
        picks = []
        picks.append(frame.sort_values("source_pick_score", ascending=False).head(8))
        picks.append(frame.sort_values("rowstate_pred_public_loss_mean").head(6))
        picks.append(frame.sort_values("pred_delta_vs_current_p90").head(6))
        if "strict_promote_gate" in frame:
            picks.append(frame[frame["strict_promote_gate"].fillna(False).astype(bool)].head(8))
        chosen = pd.concat(picks, ignore_index=True).drop_duplicates("file").head(18)
        for _, rec in chosen.iterrows():
            p = ROOT / str(rec["file"])
            if not p.exists():
                continue
            name = f"{label}_{safe_id(str(rec['variant']), 64)}"
            src = load_source(p, anchor)
            out[name] = logit(src[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
    if not out:
        raise RuntimeError("no source deltas")
    return out


def make_cell_gate(rng: np.random.Generator, basis: dict[str, np.ndarray], target: str, family: str) -> tuple[np.ndarray, dict[str, Any]]:
    n = len(next(iter(basis.values())))
    raw = np.zeros(n, dtype=np.float64)
    meta: dict[str, Any] = {}
    if family == "q_social_lowrisk":
        raw += rng.uniform(-1.25, -0.25) * basis["risk_core"]
        raw += rng.uniform(0.25, 1.25) * basis["good_core"]
        raw += rng.normal(0.0, 0.40) * basis.get("story:weekend_social_jetlag_subj_z", 0.0)
        raw += rng.normal(0.0, 0.40) * basis.get("story:late_msg_call_subj_z", 0.0)
    elif family == "s_recovery":
        raw += rng.uniform(-1.00, -0.20) * basis["bad_cluster"]
        raw += rng.uniform(0.15, 1.00) * basis["good_cluster"]
        raw += rng.normal(0.0, 0.55) * basis.get("story:low_hr_recovery_subj_z", 0.0)
        raw += rng.normal(-0.30, 0.45) * basis["energy"]
    elif family == "pc_episode":
        pcs = [k for k in basis if k.startswith("ownlife_pc")]
        for name in rng.choice(pcs, size=min(len(pcs), int(rng.integers(2, 5))), replace=False):
            raw += rng.normal(0.0, 0.75) * basis[name]
        raw += rng.uniform(-0.55, 0.15) * basis["bad_minus_good"]
    elif family == "story_counter":
        stories = [k for k in basis if k.startswith("story:")]
        for name in rng.choice(stories, size=min(len(stories), int(rng.integers(2, 5))), replace=False):
            raw += rng.normal(0.0, 0.85) * basis[name]
        raw += rng.uniform(-0.70, -0.10) * basis["risk_core"]
    elif family == "anti_bad":
        raw += rng.uniform(-1.65, -0.35) * basis["bad_cluster"]
        raw += rng.uniform(-0.75, -0.05) * basis["e256_cluster"]
        raw += rng.uniform(0.10, 1.10) * basis["good_cluster"]
    else:
        names = list(basis.keys())
        for name in rng.choice(names, size=int(rng.integers(3, 7)), replace=False):
            raw += rng.normal(0.0, 0.65) * basis[name]

    if target == "S3":
        raw += rng.normal(-1.30, 0.45)
    elif target in {"Q1", "Q2", "Q3"}:
        raw += rng.normal(0.05, 0.35)
    else:
        raw += rng.normal(-0.05, 0.35)

    temp = rng.uniform(0.75, 2.70)
    low = rng.choice([0.0, 0.05, 0.12, 0.20, 0.35])
    high = rng.uniform(0.80, 1.35)
    gate = low + (high - low) * sigmoid(temp * raw)
    if rng.random() < (0.30 if target != "S3" else 0.55):
        q = rng.uniform(0.55, 0.84)
        cutoff = np.quantile(gate, q)
        gate = np.where(gate >= cutoff, gate, gate * rng.uniform(0.0, 0.30))
        meta["sparse_" + target] = 1
    else:
        meta["sparse_" + target] = 0
    meta[f"{target}_gate_mean"] = float(np.mean(gate))
    meta[f"{target}_gate_p90"] = float(np.quantile(gate, 0.90))
    meta[f"{target}_gate_std"] = float(np.std(gate))
    return gate.astype(np.float64), meta


def recipe(rng: np.random.Generator) -> tuple[dict[str, str], np.ndarray, str]:
    modes = {
        "split_qs": {
            "Q1": "q_social_lowrisk",
            "Q2": "q_social_lowrisk",
            "Q3": "pc_episode",
            "S1": "s_recovery",
            "S3": "anti_bad",
        },
        "q_story_s_recovery": {
            "Q1": "story_counter",
            "Q2": "story_counter",
            "Q3": "q_social_lowrisk",
            "S1": "s_recovery",
            "S3": "anti_bad",
        },
        "pc_all_s_suppressed": {
            "Q1": "pc_episode",
            "Q2": "pc_episode",
            "Q3": "pc_episode",
            "S1": "s_recovery",
            "S3": "anti_bad",
        },
        "anti_bad_all": {
            "Q1": "anti_bad",
            "Q2": "anti_bad",
            "Q3": "anti_bad",
            "S1": "anti_bad",
            "S3": "anti_bad",
        },
        "free_cell": {
            "Q1": "free",
            "Q2": "story_counter",
            "Q3": "pc_episode",
            "S1": "s_recovery",
            "S3": "anti_bad",
        },
    }
    recipe_id = str(rng.choice(list(modes), p=[0.24, 0.24, 0.20, 0.17, 0.15]))
    scales = np.ones(len(TARGETS), dtype=np.float64)
    for target in ["Q1", "Q2", "Q3", "S1"]:
        scales[TARGETS.index(target)] = rng.uniform(0.70, 1.55)
    scales[TARGETS.index("S3")] = rng.choice([0.0, rng.uniform(0.0, 0.45), rng.uniform(0.45, 0.95)], p=[0.30, 0.50, 0.20])
    return modes[recipe_id], scales, recipe_id


def candidate_features(
    source_id: str,
    source_delta: np.ndarray,
    delta: np.ndarray,
    state: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
    meta: dict[str, Any],
) -> dict[str, Any]:
    absd = np.abs(delta)
    row_abs = absd.sum(axis=1)
    target_abs = absd.sum(axis=0)
    total = float(target_abs.sum())
    rec: dict[str, Any] = {
        **meta,
        "source_id": source_id,
        "source_l1": float(np.abs(source_delta).sum()),
        "move_l1": float(absd.sum()),
        "move_l2": float(np.linalg.norm(delta.reshape(-1))),
        "row_l1_p90": float(np.quantile(row_abs, 0.90)),
        "row_target_entropy": 0.0,
        "changed_rows_vs_e247": int((row_abs > 1.0e-12).sum()),
        "changed_cells_vs_e247": int((absd > 1.0e-12).sum()),
    }
    if total > 0:
        p = absd.reshape(-1) / total
        p = p[p > 0]
        rec["row_target_entropy"] = float(-(p * np.log(p)).sum() / max(np.log(absd.size), 1.0))
    rec["gated_l1_ratio"] = rec["move_l1"] / rec["source_l1"] if rec["source_l1"] > 0 else 0.0
    for i, target in enumerate(TARGETS):
        rec[f"abs_{target}"] = float(target_abs[i])
        rec[f"share_{target}"] = float(target_abs[i] / total) if total > 0 else 0.0
    rec.update(rowstate_features(delta, state, base_cols, story_cols))
    return rec


def generate_candidates(anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    basis = row_gate_basis(state, row_state_scores(state), story_cols)
    sources = load_source_deltas(anchor, anchor_logit)
    source_names = list(sources.keys())
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    attempts = 0
    while len(rows) < N_GENERATE and attempts < N_GENERATE * 6:
        attempts += 1
        source_id = str(rng.choice(source_names))
        source_delta = sources[source_id]
        target_families, target_scales, recipe_id = recipe(rng)
        gate_mat = np.ones_like(source_delta)
        meta: dict[str, Any] = {"recipe_id": recipe_id}
        for target, family in target_families.items():
            gate, gate_meta = make_cell_gate(rng, basis, target, family)
            idx = TARGETS.index(target)
            gate_mat[:, idx] = gate * target_scales[idx]
            meta[f"{target}_family"] = family
            meta[f"{target}_scale"] = float(target_scales[idx])
            meta.update(gate_meta)
        # The compact family has no meaningful S2/S4 action; preserve that.
        for target in ["S2", "S4"]:
            gate_mat[:, TARGETS.index(target)] = 0.0
        delta = source_delta * gate_mat
        source_l1 = float(np.abs(source_delta).sum())
        l1 = float(np.abs(delta).sum())
        if l1 < source_l1 * 0.50:
            delta *= min(source_l1 * rng.uniform(0.70, 1.05) / max(l1, 1.0e-12), 1.65)
        elif l1 > source_l1 * 1.35:
            delta *= source_l1 * rng.uniform(1.00, 1.25) / l1
        if np.abs(delta).sum() < 2.25:
            continue
        digest = hashlib.sha1(np.round(delta, 7).tobytes()).hexdigest()[:12]
        if digest in seen:
            continue
        seen.add(digest)
        row_id = len(rows)
        meta["variant"] = f"{source_id}__cellaction_{recipe_id}_{row_id:04d}"
        rec = candidate_features(source_id, source_delta, delta, state, base_cols, story_cols, meta)
        out = anchor[KEY].copy()
        out[TARGETS] = clip_prob(sigmoid(anchor_logit + delta))
        path = OUT / f"{UPLOAD_PREFIX}_{safe_id(meta['variant'], 112)}_{short_hash(out)}.csv"
        out.to_csv(path, index=False)
        rec["file"] = rel(path)
        rec["basename"] = path.name
        rows.append(rec)
    frame = pd.DataFrame(rows)
    frame.to_csv(CANDIDATE_OUT, index=False)
    return frame


def select(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["e362_actual_score"] = (
        1.25 * pct_rank_good(-out["pred_delta_vs_current_p90"])
        + 1.15 * pct_rank_good(-out["rowstate_pred_public_loss_mean"])
        + 0.80 * pct_rank_good(-out["rowstate_pred_public_loss_std"])
        + 0.90 * pct_rank_good(-out["rowstate_bad_minus_good_exposure"])
        + 0.85 * pct_rank_good(0.015 - out["incremental_bad_axis_vs_current"].abs())
        + 0.50 * pct_rank_good(out["row_target_entropy"])
        + 0.35 * pct_rank_good(-out["share_S3"])
    ) / 5.80
    out["e362_submission_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00082)
        & (out["rowstate_pred_public_loss_std"] <= 0.00055)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.145)
    )
    out["e362_nearmiss_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00095)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.150)
    )
    ranked = out.sort_values(["e362_submission_gate", "e362_actual_score"], ascending=[False, False]).reset_index(drop=True)
    passed = ranked[ranked["e362_submission_gate"]].head(1)
    if passed.empty:
        selected = ranked.head(1).copy()
        selected["decision"] = "no_cellaction_submission"
        selected["selected_uploadsafe_file"] = "none"
        selected["reason"] = "Target-specific row-cell actions did not clear strict output plus row-state gates."
    else:
        selected = passed.copy()
        src = ROOT / str(selected.iloc[0]["file"])
        frame = pd.read_csv(src)
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(selected.iloc[0]['variant']), 72)}_{short_hash(frame)}_uploadsafe.csv"
        shutil.copyfile(src, upload)
        selected["decision"] = "select_cellaction_probe"
        selected["selected_uploadsafe_file"] = rel(upload)
        selected["reason"] = "Target-specific row-cell action passed strict local stress gates."
    selected.to_csv(SELECTION_OUT, index=False)
    ranked.to_csv(SCORE_OUT, index=False)
    return selected


def write_report(scored: pd.DataFrame, selected: pd.DataFrame) -> None:
    top_cols = [
        "variant",
        "source_id",
        "recipe_id",
        "e362_submission_gate",
        "e362_nearmiss_gate",
        "e362_actual_score",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "rowstate_pred_public_loss_mean",
        "rowstate_pred_public_loss_std",
        "rowstate_bad_minus_good_exposure",
        "move_l1",
        "gated_l1_ratio",
        "row_target_entropy",
        "share_Q1",
        "share_Q2",
        "share_Q3",
        "share_S1",
        "share_S3",
        "file",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    summary = (
        scored.groupby("recipe_id", dropna=False)
        .agg(
            n=("variant", "count"),
            submit=("e362_submission_gate", "sum"),
            near=("e362_nearmiss_gate", "sum"),
            strict=("strict_promote_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_rowloss=("rowstate_pred_public_loss_mean", "min"),
            best_exposure=("rowstate_bad_minus_good_exposure", "min"),
            best_actual=("e362_actual_score", "max"),
        )
        .reset_index()
        .sort_values(["submit", "near", "best_actual"], ascending=[False, False, False])
    )
    lines = [
        "# E362 Row x Target Cell-Action Generator",
        "",
        "## Question",
        "",
        "Can target-specific row-cell action geometry solve the E360/E361 health-versus-visibility contradiction?",
        "",
        "## Method",
        "",
        "- Source actions: compact family plus selected E360/E361 healthy/visible rows.",
        "- Action: independent row gates for Q1/Q2/Q3/S1/S3 over ownlife PCs, row-state risk/good clusters, and human/social story axes.",
        "- Verification: actual E272 public-free selector and E358 row-state public-survival.",
        "",
        "## Decision",
        "",
        md_table(selected[["decision", "variant", "selected_uploadsafe_file", "e362_actual_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure", "reason"]], n=5, floatfmt=".9f"),
        "",
        "## Recipe Summary",
        "",
        md_table(summary, n=30, floatfmt=".9f"),
        "",
        "## Top Actual-Stress Candidates",
        "",
        md_table(scored[top_cols].head(50), n=50, floatfmt=".9f"),
        "",
        "## Gate-Passing Candidates",
        "",
        md_table(scored[scored["e362_submission_gate"]][top_cols], n=50, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        "- A pass would mean the hidden action law is target-specific row-cell geometry, not broad row placement.",
        "- No pass means either the compact source action family is exhausted or the cell-action generator still lacks the right latent target.",
        "",
        "## Counts",
        "",
        f"- candidates: `{len(scored)}`",
        f"- strict output candidates: `{int(scored['strict_promote_gate'].sum())}`",
        f"- near-miss candidates: `{int(scored['e362_nearmiss_gate'].sum())}`",
        f"- submission-gate candidates: `{int(scored['e362_submission_gate'].sum())}`",
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
    selected_cols = selector_scores(candidates, anchor)
    scored = rowstate_public_scores(selected_cols, anchor, anchor_logit, state, base_cols, story_cols)
    selected = select(scored)
    scored = pd.read_csv(SCORE_OUT)
    write_report(scored, selected)
    print(f"candidates={len(candidates)}")
    print(selected[["decision", "variant", "selected_uploadsafe_file", "e362_actual_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure"]].round(9).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
