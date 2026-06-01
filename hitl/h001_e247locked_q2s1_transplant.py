#!/usr/bin/env python3
"""H001: E247-locked Q2/S1 transplant diagnostic.

Human-in-the-loop question:
    GPT Pro pointed out that E368 was selected in the E365 coordinate frame,
    but publicly judged against E247.  Does the Q2/S1 hidden-state action still
    look viable when the E247 body is frozen and only the E365->E368 Q2/S1
    delta is transplanted?

This script is a diagnostic, not a blind submission generator.  It materializes
E247-locked Q2/S1 variants, scores them with existing public-free stress tools,
and rejects the branch unless it preserves E247 non-Q2/S1 cells and improves
action-health style stress over null/body-confounded alternatives.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H001 = HITL / "h001_e247locked_q2s1_transplant"
H001.mkdir(parents=True, exist_ok=True)

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import e360_learned_row_action_health_generator as e360  # noqa: E402
import e368_q2s1_rowmask_cellaction_latent as e368  # noqa: E402
import e370_q2s1_risk_constrained_recalibration as e370  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import (  # noqa: E402
    clip_prob,
    load_sub_frame,
    md_table,
    normalize_dates,
    safe_id,
    sigmoid,
)
from e357_public_survival_contrast_latent import KEY, TARGETS, safe_spearman  # noqa: E402
from e358_rowstate_public_survival_audit import load_anchor, load_row_state  # noqa: E402
from e359_rowplacement_action_health_probe import selector_scores  # noqa: E402
from e360_learned_row_action_health_generator import rowstate_public_scores  # noqa: E402
from e363_cell_action_robustness_probe import add_e363_scores  # noqa: E402
from public_anchor_bottleneck_decomposition import logit  # noqa: E402


EPS = 1.0e-12
Q2 = TARGETS.index("Q2")
S1 = TARGETS.index("S1")
NON_Q2S1 = [i for i, t in enumerate(TARGETS) if t not in {"Q2", "S1"}]

CANDIDATES_OUT = H001 / "h001_candidates.csv"
MOVEMENT_OUT = H001 / "h001_movement_audit.csv"
SCORES_OUT = H001 / "h001_scores.csv"
SCENARIOS_OUT = H001 / "h001_scenarios.csv"
RANKS_OUT = H001 / "h001_scenario_ranks.csv"
SUPPORT_OUT = H001 / "h001_support.csv"
SELECTION_OUT = H001 / "h001_selection.csv"
REPORT_OUT = H001 / "h001_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def cos(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64).reshape(-1)
    bb = np.asarray(b, dtype=np.float64).reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb) + EPS)
    return float(np.sum(aa * bb) / denom)


def rank01(values: np.ndarray | pd.Series) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if s.nunique() <= 1:
        return np.zeros(len(s), dtype=np.float64)
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def write_candidate(
    base: pd.DataFrame,
    logits: np.ndarray,
    variant: str,
    family: str,
    meta: dict[str, Any],
    rows: list[dict[str, Any]],
    seen: set[str],
) -> None:
    out = base[KEY].copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    digest = short_hash(out)
    if digest in seen:
        return
    seen.add(digest)
    path = H001 / f"submission_{safe_id(variant, 92)}_{digest}.csv"
    out.to_csv(path, index=False)
    rows.append(
        {
            "variant": variant,
            "family": family,
            "file": rel(path),
            "basename": path.name,
            **meta,
        }
    )


def movement_metrics(delta: np.ndarray, bad247: np.ndarray, bad365: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {
        "move_l1": float(np.abs(delta).sum()),
        "move_l2": float(np.sqrt(np.sum(delta * delta))),
        "changed_cells_1e12": float((np.abs(delta) > 1.0e-12).sum()),
        "changed_rows_1e12": float((np.abs(delta).sum(axis=1) > 1.0e-12).sum()),
        "non_q2s1_l1": float(np.abs(delta[:, NON_Q2S1]).sum()),
        "all_cos_e323_bad_vs_e247": cos(delta, bad247),
        "all_cos_e323_bad_vs_e365": cos(delta, bad365),
        "q2_cos_e323_bad_vs_e247": cos(delta[:, Q2], bad247[:, Q2]) if np.linalg.norm(delta[:, Q2]) > EPS else 0.0,
        "q2_cos_e323_bad_vs_e365": cos(delta[:, Q2], bad365[:, Q2]) if np.linalg.norm(delta[:, Q2]) > EPS else 0.0,
        "s1_cos_e323_bad_vs_e247": cos(delta[:, S1], bad247[:, S1]) if np.linalg.norm(delta[:, S1]) > EPS else 0.0,
        "s1_cos_e323_bad_vs_e365": cos(delta[:, S1], bad365[:, S1]) if np.linalg.norm(delta[:, S1]) > EPS else 0.0,
    }
    for j, target in enumerate(TARGETS):
        out[f"l1_{target}"] = float(np.abs(delta[:, j]).sum())
        out[f"signed_sum_{target}"] = float(delta[:, j].sum())
        out[f"changed_{target}"] = float((np.abs(delta[:, j]) > 1.0e-12).sum())
    return out


def build_candidates() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    anchor, _anchor_logit = load_anchor()
    sample = normalize_dates(anchor[KEY].copy()).sort_values(KEY).reset_index(drop=True)
    e365, e368_sel, e247, e323 = e370.load_backbones(sample)
    # Keep all frame orders exactly aligned to the current E247 anchor.
    e247 = e247.sort_values(KEY).reset_index(drop=True)
    e365 = e365.sort_values(KEY).reset_index(drop=True)
    e368_sel = e368_sel.sort_values(KEY).reset_index(drop=True)
    e323 = e323.sort_values(KEY).reset_index(drop=True)

    l247 = logit(e247[TARGETS].to_numpy(dtype=np.float64))
    l365 = logit(e365[TARGETS].to_numpy(dtype=np.float64))
    l368 = logit(e368_sel[TARGETS].to_numpy(dtype=np.float64))
    l323 = logit(e323[TARGETS].to_numpy(dtype=np.float64))
    action = l368 - l365
    q2s1_action = np.zeros_like(action)
    q2s1_action[:, Q2] = action[:, Q2]
    q2s1_action[:, S1] = action[:, S1]
    bad247 = l323 - l247
    bad365 = l323 - l365

    rowmask = normalize_dates(pd.read_csv(e368.ROWMASK_OUT)).sort_values(KEY).reset_index(drop=True)
    transfer, _transfer_meta = e370.build_transfer_vectors(sample)
    transfer = normalize_dates(transfer).sort_values(KEY).reset_index(drop=True)
    if not sample[KEY].equals(rowmask[KEY]):
        raise RuntimeError("rowmask key mismatch")
    if not sample[KEY].equals(transfer[KEY]):
        raise RuntimeError("transfer key mismatch")

    q2_transfer = transfer["q2_publicfree_transfer_score"].to_numpy(dtype=np.float64)
    s1_transfer = transfer["s1_publicfree_transfer_score"].to_numpy(dtype=np.float64)
    q2_transfer_top20 = q2_transfer >= np.quantile(q2_transfer, 0.80)
    s1_transfer_top20 = s1_transfer >= np.quantile(s1_transfer, 0.80)
    q2_rowmask_gate = (
        rowmask["pred_q2_valid_rank"].to_numpy(dtype=np.float64) >= 0.80
    ) & (rowmask["pred_bad_rank"].to_numpy(dtype=np.float64) <= 0.75)
    s1_rowmask_gate = (
        rowmask["pred_s1_valid_rank"].to_numpy(dtype=np.float64) >= 0.80
    ) & (rowmask["pred_bad_rank"].to_numpy(dtype=np.float64) <= 0.75)
    gates = {
        "all": (np.ones(len(sample), dtype=bool), np.ones(len(sample), dtype=bool)),
        "transfer_top20": (q2_transfer_top20, s1_transfer_top20 | q2_transfer_top20),
        "rowmask_valid": (q2_rowmask_gate, s1_rowmask_gate | q2_rowmask_gate),
        "agreement": (q2_transfer_top20 & q2_rowmask_gate, (s1_transfer_top20 & s1_rowmask_gate) | (q2_transfer_top20 & q2_rowmask_gate)),
    }

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    write_candidate(
        e247,
        l247,
        "h001_control_e247_identity",
        "h001_control",
        {"q2_scale": 0.0, "s1_scale": 0.0, "gate": "identity"},
        rows,
        seen,
    )
    # Include E365/E368 controls for the same stress table, but never select them.
    write_candidate(
        e247,
        l365,
        "h001_control_e365_body",
        "h001_control",
        {"q2_scale": np.nan, "s1_scale": np.nan, "gate": "control_body"},
        rows,
        seen,
    )
    write_candidate(
        e247,
        l368,
        "h001_control_e368_public_file",
        "h001_control",
        {"q2_scale": np.nan, "s1_scale": np.nan, "gate": "control_body_action"},
        rows,
        seen,
    )

    q2_scales = [0.0, 0.25, 0.50, 0.75, 1.00, 1.25]
    s1_scales = [0.0, 0.50, 0.75, 1.00, 1.06, 1.25]
    for gate_name, (q2_gate, s1_gate) in gates.items():
        for q2_scale in q2_scales:
            for s1_scale in s1_scales:
                if q2_scale == 0.0 and s1_scale == 0.0:
                    continue
                delta = np.zeros_like(l247)
                delta[:, Q2] = q2_scale * q2s1_action[:, Q2] * q2_gate.astype(np.float64)
                delta[:, S1] = s1_scale * q2s1_action[:, S1] * s1_gate.astype(np.float64)
                if np.abs(delta).sum() <= EPS:
                    continue
                variant = (
                    f"h001_e247locked_{gate_name}_q2{str(q2_scale).replace('.', 'p')}"
                    f"_s1{str(s1_scale).replace('.', 'p')}"
                )
                meta = {
                    "q2_scale": q2_scale,
                    "s1_scale": s1_scale,
                    "gate": gate_name,
                    "q2_gate_rows": int(q2_gate.sum()),
                    "s1_gate_rows": int(s1_gate.sum()),
                }
                write_candidate(e247, l247 + delta, variant, "h001_e247locked_q2s1_transplant", meta, rows, seen)

    candidates = pd.DataFrame(rows)
    movement_rows = []
    for rec in candidates.to_dict("records"):
        sub = load_sub_frame(ROOT / str(rec["file"]), sample)
        d = logit(sub[TARGETS].to_numpy(dtype=np.float64)) - l247
        movement_rows.append({**rec, **movement_metrics(d, bad247, bad365)})
    movement = pd.DataFrame(movement_rows)
    movement["q2_transfer_abs_spearman"] = [
        safe_spearman(
            np.abs(logit(load_sub_frame(ROOT / str(file), sample)[TARGETS].to_numpy(dtype=np.float64))[:, Q2] - l247[:, Q2]),
            q2_transfer,
        )
        for file in movement["file"]
    ]
    movement["s1_transfer_abs_spearman"] = [
        safe_spearman(
            np.abs(logit(load_sub_frame(ROOT / str(file), sample)[TARGETS].to_numpy(dtype=np.float64))[:, S1] - l247[:, S1]),
            s1_transfer,
        )
        for file in movement["file"]
    ]
    movement["q2_transfer_signed_spearman"] = [
        safe_spearman(
            logit(load_sub_frame(ROOT / str(file), sample)[TARGETS].to_numpy(dtype=np.float64))[:, Q2] - l247[:, Q2],
            q2_transfer,
        )
        for file in movement["file"]
    ]
    movement["s1_transfer_signed_spearman"] = [
        safe_spearman(
            logit(load_sub_frame(ROOT / str(file), sample)[TARGETS].to_numpy(dtype=np.float64))[:, S1] - l247[:, S1],
            s1_transfer,
        )
        for file in movement["file"]
    ]
    candidates.to_csv(CANDIDATES_OUT, index=False)
    movement.to_csv(MOVEMENT_OUT, index=False)
    return candidates, movement, rowmask, e247, e365, e368_sel, e323, q2s1_action, bad247


def score_candidates(candidates: pd.DataFrame, rowmask: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    e360.KNOWN_OUT = H001 / "h001_rowstate_known.csv"
    e368.KNOWN_OUT = H001 / "h001_public_known.csv"
    e368.SCORES_OUT = SCORES_OUT
    e368.SCENARIOS_OUT = SCENARIOS_OUT
    e368.RANKS_OUT = RANKS_OUT
    e368.SUPPORT_OUT = SUPPORT_OUT

    selector = selector_scores(candidates, anchor)
    rowstate = rowstate_public_scores(selector, anchor, anchor_logit, state, base_cols, story_cols)
    e363_scored = add_e363_scores(rowstate)
    combined, known_scored, _feature_cols = e368.public_score_candidates(e363_scored, rowmask)
    combined["candidate_origin"] = combined["candidate_origin"].replace({"e368_generated": "h001_generated"})
    feature_sets = e368.available_feature_sets(known_scored, combined)
    base_variant = "h001_control_e247_identity"
    scenarios, ranks = e368.run_scenarios(known_scored, combined, feature_sets, base_variant)
    if "candidate_origin" in ranks.columns:
        ranks["candidate_origin"] = ranks["candidate_origin"].replace({"e368_generated": "h001_generated"})
    support = e368.aggregate_support(ranks, len(scenarios)) if len(ranks) else pd.DataFrame()
    if "candidate_origin" in support.columns:
        support["candidate_origin"] = support["candidate_origin"].replace({"e368_generated": "h001_generated"})
    combined.to_csv(SCORES_OUT, index=False)
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    ranks.to_csv(RANKS_OUT, index=False)
    support.to_csv(SUPPORT_OUT, index=False)
    return combined, scenarios, support


def select_candidate(candidates: pd.DataFrame, movement: pd.DataFrame, combined: pd.DataFrame, support: pd.DataFrame) -> pd.DataFrame:
    support_cols = ["variant", "top1_rate", "top5_rate", "top10_rate", "rank_mean", "score_mean"]
    if support.empty or "variant" not in support.columns:
        support = pd.DataFrame({"variant": combined["variant"].astype(str).unique()})
        for col in support_cols:
            if col != "variant":
                support[col] = 0.0
    work = combined.merge(support[[c for c in support_cols if c in support.columns]], on="variant", how="left")
    work = work.merge(
        movement.drop(columns=[c for c in ["file", "basename", "family"] if c in movement.columns], errors="ignore"),
        on="variant",
        how="left",
        suffixes=("", "_move"),
    )
    h = work[work["family"].astype(str).eq("h001_e247locked_q2s1_transplant")].copy()
    for col in [
        "top1_rate",
        "top5_rate",
        "top10_rate",
        "e368_public_like_score",
        "rowstate_pred_public_loss_mean",
        "rowstate_bad_minus_good_exposure",
        "public_bad_axis_sum",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "q2_cos_e323_bad_vs_e247",
        "non_q2s1_l1",
    ]:
        if col in h:
            h[col] = pd.to_numeric(h[col], errors="coerce").fillna(0.0)
    h["h001_score"] = (
        0.90 * rank01(h["top1_rate"])
        + 0.65 * rank01(h["top10_rate"])
        + 0.55 * rank01(h["e368_public_like_score"])
        + 0.45 * rank01(-h["rowstate_pred_public_loss_mean"])
        + 0.40 * rank01(-h["rowstate_bad_minus_good_exposure"])
        + 0.35 * rank01(-h["public_bad_axis_sum"])
        + 0.40 * rank01(h["q2_transfer_abs_spearman"])
        + 0.25 * rank01(h["s1_transfer_abs_spearman"])
        + 0.60 * rank01(-h["q2_cos_e323_bad_vs_e247"].clip(lower=0.0))
    )
    h["hard_invariant_ok"] = h["non_q2s1_l1"].abs() <= 1.0e-10
    h["stress_ready"] = (
        h["hard_invariant_ok"]
        & h["e363_submission_gate"].fillna(False).astype(bool)
        & (h["top10_rate"] >= 0.25)
        & (h["q2_transfer_abs_spearman"] >= 0.0)
        & (h["q2_cos_e323_bad_vs_e247"] <= 0.10)
    )
    h = h.sort_values("h001_score", ascending=False)
    selected = h[h["stress_ready"]].head(1).copy()
    if len(selected):
        decision = "promote_h001_e247locked_q2s1_diagnostic_candidate"
        reason = "E247-locked Q2/S1 transplant preserves non-Q2/S1 cells and passes public-free stress gates."
        src = ROOT / str(selected.iloc[0]["file"])
        upload = H001 / f"submission_{safe_id(str(selected.iloc[0]['variant']), 80)}_{short_hash(pd.read_csv(src))}_uploadsafe.csv"
        shutil.copyfile(src, upload)
    else:
        selected = h.head(1).copy()
        decision = "diagnostic_only_no_h001_submission"
        reason = "E247-locked Q2/S1 transplant isolates the body confound, but no variant passes the conservative stress-ready gate."
        upload = None
    selected["decision"] = decision
    selected["reason"] = reason
    selected["stress_ready_count"] = int(h["stress_ready"].sum())
    selected["selected_uploadsafe_file"] = rel(upload) if upload is not None else "none"
    selected.to_csv(SELECTION_OUT, index=False)
    h.to_csv(H001 / "h001_ranked_candidates.csv", index=False)
    return selected


def write_report(
    movement: pd.DataFrame,
    combined: pd.DataFrame,
    support: pd.DataFrame,
    selected: pd.DataFrame,
) -> None:
    ranked = pd.read_csv(H001 / "h001_ranked_candidates.csv")
    move_cols = [
        "variant",
        "family",
        "gate",
        "q2_scale",
        "s1_scale",
        "move_l1",
        "non_q2s1_l1",
        "l1_Q1",
        "l1_Q2",
        "l1_Q3",
        "l1_S1",
        "q2_cos_e323_bad_vs_e247",
        "q2_cos_e323_bad_vs_e365",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "file",
    ]
    sel_cols = [
        "decision",
        "variant",
        "stress_ready_count",
        "selected_uploadsafe_file",
        "reason",
        "gate",
        "q2_scale",
        "s1_scale",
        "top1_rate",
        "top10_rate",
        "e363_submission_gate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e247",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "h001_score",
    ]
    top_cols = [
        "variant",
        "gate",
        "q2_scale",
        "s1_scale",
        "stress_ready",
        "top1_rate",
        "top10_rate",
        "e363_submission_gate",
        "e368_public_like_score",
        "rowstate_pred_public_loss_mean",
        "public_bad_axis_sum",
        "q2_cos_e323_bad_vs_e247",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "h001_score",
        "file",
    ]
    lines = [
        "# H001 E247-Locked Q2/S1 Transplant",
        "",
        "## Question",
        "",
        "Was E368's public loss caused by the Q2/S1 hidden-state action itself, or by testing that action inside an E365-like body instead of the E247 public-best body?",
        "",
        "## Construction",
        "",
        "- Base body: E247 public-best, fixed.",
        "- Action source: `logit(E368) - logit(E365)` for Q2 and S1 only.",
        "- Hard invariant: Q1/Q3/S2/S3/S4 must remain exactly E247.",
        "- Candidate families: all-row transplant, public-free transfer top20 gate, E368 rowmask-valid gate, and agreement gate.",
        "- Scoring: existing public-free selector, rowstate, E363/E368 scenario stress, E369 transfer alignment, and E323 bad-axis exposure.",
        "",
        "## Selection",
        "",
        md_table(selected[[c for c in sel_cols if c in selected.columns]], n=5, floatfmt=".9f"),
        "",
        "## Movement Controls",
        "",
        md_table(movement[[c for c in move_cols if c in movement.columns]].head(40), n=40, floatfmt=".9f"),
        "",
        "## Top H001 Ranked Candidates",
        "",
        md_table(ranked[[c for c in top_cols if c in ranked.columns]].head(30), n=30, floatfmt=".9f"),
        "",
        "## Support Summary",
        "",
        md_table(support.head(30), n=30, floatfmt=".9f") if len(support) else "(no scenario-gated support rows)",
        "",
        "## Interpretation",
        "",
    ]
    decision = str(selected["decision"].iloc[0])
    if decision.startswith("promote_"):
        lines.append(
            "H001 supports the E247-frame action incompatibility diagnosis: the Q2/S1 action can be expressed as an E247-locked edit that keeps the hard body invariant and passes conservative local stress. This is a candidate for human review, not an automatic submission."
        )
    else:
        lines.append(
            "H001 isolates the E365-body confound, but the current E247-locked Q2/S1 transplant still does not pass the conservative stress-ready gate. Do not submit another Q2/S1 file until a sharper action-benefit target exists."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(CANDIDATES_OUT)}`",
            f"- `{rel(MOVEMENT_OUT)}`",
            f"- `{rel(SCORES_OUT)}`",
            f"- `{rel(SCENARIOS_OUT)}`",
            f"- `{rel(RANKS_OUT)}`",
            f"- `{rel(SUPPORT_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    # Keep E370 transfer artifacts inside HITL for this run.
    e370.TRANSFER_ROWS_OUT = H001 / "h001_transfer_rows.csv"
    candidates, movement, rowmask, *_ = build_candidates()
    combined, _scenarios, support = score_candidates(candidates, rowmask)
    selected = select_candidate(candidates, movement, combined, support)
    write_report(movement, combined, support, selected)
    print(f"h001_candidates={len(candidates)}")
    print(selected[["decision", "variant", "stress_ready_count", "selected_uploadsafe_file", "reason"]].to_string(index=False))
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
