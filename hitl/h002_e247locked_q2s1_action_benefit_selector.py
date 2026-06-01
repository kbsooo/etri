#!/usr/bin/env python3
"""H002: E247-locked Q2/S1 action-benefit selector.

Human-in-the-loop question:
    H001 showed that the E368 Q2/S1 action is not inherently the same as the
    E323-bad direction once the public-best E247 body is frozen.  But H001 also
    showed that a blind transplant is not submission-safe.

    So H002 asks a narrower JEPA-style question:

        context = public-free transfer score, learned row validity, bad-row
                  risk, and E247-frame E323-axis exposure
        target  = an action-benefit representation for Q2/S1 rows
        action  = apply only Q2/S1 logit deltas to the E247 body

    The falsifiable claim is that the useful hidden lifestyle state is row
    selective.  If this is true, E247-locked candidates should concentrate
    movement on high-benefit / low-danger rows and survive local stress better
    than H001's all-row transplant.
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
H002 = HITL / "h002_e247locked_q2s1_action_benefit_selector"
H002.mkdir(parents=True, exist_ok=True)

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
NON_Q2S1 = [i for i, target in enumerate(TARGETS) if target not in {"Q2", "S1"}]

CANDIDATES_OUT = H002 / "h002_candidates.csv"
CONTEXT_OUT = H002 / "h002_action_context.csv"
MOVEMENT_OUT = H002 / "h002_movement_audit.csv"
SCORES_OUT = H002 / "h002_scores.csv"
SCENARIOS_OUT = H002 / "h002_scenarios.csv"
RANKS_OUT = H002 / "h002_scenario_ranks.csv"
SUPPORT_OUT = H002 / "h002_support.csv"
SELECTION_OUT = H002 / "h002_selection.csv"
RANKED_OUT = H002 / "h002_ranked_candidates.csv"
REPORT_OUT = H002 / "h002_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def locate(path_or_name: object) -> Path:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(str(path_or_name))


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


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    w = np.asarray(weights, dtype=np.float64)
    denom = float(np.sum(np.abs(w)))
    if denom <= EPS:
        return 0.0
    return float(np.sum(np.asarray(values, dtype=np.float64) * np.abs(w)) / denom)


def require_same_keys(left: pd.DataFrame, right: pd.DataFrame, label: str) -> None:
    if not left[KEY].reset_index(drop=True).equals(right[KEY].reset_index(drop=True)):
        raise RuntimeError(f"{label} key mismatch")


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
    path = H002 / f"submission_{safe_id(variant, 92)}_{digest}.csv"
    out.to_csv(path, index=False)
    rows.append({"variant": variant, "family": family, "file": rel(path), "basename": path.name, **meta})


def build_backbone_logits(sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, np.ndarray]]:
    e365, e368_sel, e247, e323 = e370.load_backbones(sample)
    frames = {
        "e365": normalize_dates(e365).sort_values(KEY).reset_index(drop=True),
        "e368": normalize_dates(e368_sel).sort_values(KEY).reset_index(drop=True),
        "e247": normalize_dates(e247).sort_values(KEY).reset_index(drop=True),
        "e323": normalize_dates(e323).sort_values(KEY).reset_index(drop=True),
    }
    for name, frame in frames.items():
        require_same_keys(sample, frame, name)
    logits = {name: logit(frame[TARGETS].to_numpy(dtype=np.float64)) for name, frame in frames.items()}
    return sample, frames, logits


def build_action_context(
    sample: pd.DataFrame,
    base_action: np.ndarray,
    bad247: np.ndarray,
) -> pd.DataFrame:
    e370.TRANSFER_ROWS_OUT = H002 / "h002_transfer_rows.csv"
    transfer, _transfer_meta = e370.build_transfer_vectors(sample)
    transfer = normalize_dates(transfer).sort_values(KEY).reset_index(drop=True)
    rowmask = normalize_dates(pd.read_csv(e368.ROWMASK_OUT)).sort_values(KEY).reset_index(drop=True)
    require_same_keys(sample, transfer, "h002_transfer")
    require_same_keys(sample, rowmask, "h002_rowmask")

    q2_transfer = rank01(transfer["q2_publicfree_transfer_score"])
    s1_transfer = rank01(transfer["s1_publicfree_transfer_score"])
    q2_valid = rank01(rowmask.get("pred_public_validity_Q2", rowmask["pred_q2_valid_rank"]))
    s1_valid = rank01(rowmask.get("pred_public_validity_S1", rowmask["pred_s1_valid_rank"]))
    row_valid = rank01(rowmask["pred_validity_rank"])
    bad_rank = rank01(rowmask["pred_bad_rank"])

    q2_e247_bad_risk = rank01(np.clip(base_action[:, Q2] * bad247[:, Q2], 0.0, None))
    s1_e247_bad_risk = rank01(np.clip(base_action[:, S1] * bad247[:, S1], 0.0, None))
    q2_abs = rank01(np.abs(base_action[:, Q2]))
    s1_abs = rank01(np.abs(base_action[:, S1]))

    q2_benefit = rank01(
        0.42 * q2_transfer
        + 0.30 * q2_valid
        + 0.18 * row_valid
        + 0.10 * q2_abs
        - 0.28 * q2_e247_bad_risk
        - 0.14 * bad_rank
    )
    s1_benefit = rank01(
        0.46 * s1_transfer
        + 0.29 * s1_valid
        + 0.15 * row_valid
        + 0.10 * s1_abs
        - 0.18 * s1_e247_bad_risk
        - 0.12 * bad_rank
    )
    q2_danger = rank01(0.56 * q2_e247_bad_risk + 0.26 * bad_rank + 0.18 * (1.0 - q2_transfer))
    s1_danger = rank01(0.45 * s1_e247_bad_risk + 0.30 * bad_rank + 0.25 * (1.0 - s1_transfer))

    ctx = sample[KEY].copy()
    ctx["q2_transfer"] = q2_transfer
    ctx["s1_transfer"] = s1_transfer
    ctx["q2_valid"] = q2_valid
    ctx["s1_valid"] = s1_valid
    ctx["row_valid"] = row_valid
    ctx["bad_rank"] = bad_rank
    ctx["q2_e247_bad_risk"] = q2_e247_bad_risk
    ctx["s1_e247_bad_risk"] = s1_e247_bad_risk
    ctx["q2_benefit"] = q2_benefit
    ctx["s1_benefit"] = s1_benefit
    ctx["q2_danger"] = q2_danger
    ctx["s1_danger"] = s1_danger
    ctx["q2_base_abs_rank"] = q2_abs
    ctx["s1_base_abs_rank"] = s1_abs
    ctx.to_csv(CONTEXT_OUT, index=False)
    return ctx


def make_gate_weights(ctx: pd.DataFrame, gate_name: str) -> tuple[np.ndarray, np.ndarray]:
    q2_b = ctx["q2_benefit"].to_numpy(dtype=np.float64)
    s1_b = ctx["s1_benefit"].to_numpy(dtype=np.float64)
    q2_d = ctx["q2_danger"].to_numpy(dtype=np.float64)
    s1_d = ctx["s1_danger"].to_numpy(dtype=np.float64)
    q2_t = ctx["q2_transfer"].to_numpy(dtype=np.float64)
    s1_t = ctx["s1_transfer"].to_numpy(dtype=np.float64)
    q2_v = ctx["q2_valid"].to_numpy(dtype=np.float64)
    s1_v = ctx["s1_valid"].to_numpy(dtype=np.float64)
    bad = ctx["bad_rank"].to_numpy(dtype=np.float64)

    ones = np.ones(len(ctx), dtype=np.float64)
    if gate_name == "all":
        return ones, ones
    if gate_name == "benefit_floor035":
        return 0.35 + 0.65 * q2_b, 0.35 + 0.65 * s1_b
    if gate_name == "benefit_floor050":
        return 0.50 + 0.50 * q2_b, 0.50 + 0.50 * s1_b
    if gate_name == "benefit_top25":
        return (q2_b >= np.quantile(q2_b, 0.75)).astype(float), (s1_b >= np.quantile(s1_b, 0.75)).astype(float)
    if gate_name == "benefit_top35":
        return (q2_b >= np.quantile(q2_b, 0.65)).astype(float), (s1_b >= np.quantile(s1_b, 0.65)).astype(float)
    if gate_name == "benefit_transfer_soft":
        return np.sqrt(np.clip(q2_b * q2_t, 0.0, 1.0)), np.sqrt(np.clip(s1_b * s1_t, 0.0, 1.0))
    if gate_name == "validity_lowbad":
        return ((q2_v >= 0.70) & (bad <= 0.70)).astype(float), ((s1_v >= 0.70) & (bad <= 0.70)).astype(float)
    if gate_name == "danger_veto25":
        q2_risky = (q2_d >= np.quantile(q2_d, 0.75)) & (q2_b < np.quantile(q2_b, 0.60))
        s1_risky = (s1_d >= np.quantile(s1_d, 0.75)) & (s1_b < np.quantile(s1_b, 0.60))
        return np.where(q2_risky, 0.25, 1.0), np.where(s1_risky, 0.25, 1.0)
    if gate_name == "q2_off_s1_benefit":
        return np.zeros(len(ctx), dtype=np.float64), 0.35 + 0.65 * s1_b
    raise ValueError(gate_name)


def action_meta(delta: np.ndarray, action: np.ndarray, ctx: pd.DataFrame, bad247: np.ndarray, bad365: np.ndarray) -> dict[str, float]:
    q2_delta = delta[:, Q2]
    s1_delta = delta[:, S1]
    out: dict[str, float] = {
        "move_l1": float(np.abs(delta).sum()),
        "move_l2": float(np.sqrt(np.sum(delta * delta))),
        "changed_cells_1e12": float((np.abs(delta) > 1.0e-12).sum()),
        "changed_rows_1e12": float((np.abs(delta).sum(axis=1) > 1.0e-12).sum()),
        "non_q2s1_l1": float(np.abs(delta[:, NON_Q2S1]).sum()),
        "all_cos_e323_bad_vs_e247": cos(delta, bad247),
        "all_cos_e323_bad_vs_e365": cos(delta, bad365),
        "q2_cos_e323_bad_vs_e247": cos(q2_delta, bad247[:, Q2]) if np.linalg.norm(q2_delta) > EPS else 0.0,
        "q2_cos_e323_bad_vs_e365": cos(q2_delta, bad365[:, Q2]) if np.linalg.norm(q2_delta) > EPS else 0.0,
        "s1_cos_e323_bad_vs_e247": cos(s1_delta, bad247[:, S1]) if np.linalg.norm(s1_delta) > EPS else 0.0,
        "s1_cos_e323_bad_vs_e365": cos(s1_delta, bad365[:, S1]) if np.linalg.norm(s1_delta) > EPS else 0.0,
        "q2_transfer_abs_spearman": safe_spearman(np.abs(q2_delta), ctx["q2_transfer"].to_numpy(dtype=np.float64)),
        "s1_transfer_abs_spearman": safe_spearman(np.abs(s1_delta), ctx["s1_transfer"].to_numpy(dtype=np.float64)),
        "q2_benefit_abs_wmean": weighted_mean(ctx["q2_benefit"].to_numpy(dtype=np.float64), q2_delta),
        "s1_benefit_abs_wmean": weighted_mean(ctx["s1_benefit"].to_numpy(dtype=np.float64), s1_delta),
        "q2_danger_abs_wmean": weighted_mean(ctx["q2_danger"].to_numpy(dtype=np.float64), q2_delta),
        "s1_danger_abs_wmean": weighted_mean(ctx["s1_danger"].to_numpy(dtype=np.float64), s1_delta),
        "q2_base_action_abs_spearman": safe_spearman(np.abs(q2_delta), np.abs(action[:, Q2])),
        "s1_base_action_abs_spearman": safe_spearman(np.abs(s1_delta), np.abs(action[:, S1])),
    }
    out["q2_benefit_minus_danger"] = out["q2_benefit_abs_wmean"] - out["q2_danger_abs_wmean"]
    out["s1_benefit_minus_danger"] = out["s1_benefit_abs_wmean"] - out["s1_danger_abs_wmean"]
    for j, target in enumerate(TARGETS):
        out[f"l1_{target}"] = float(np.abs(delta[:, j]).sum())
        out[f"signed_sum_{target}"] = float(delta[:, j].sum())
        out[f"changed_{target}"] = float((np.abs(delta[:, j]) > 1.0e-12).sum())
    return out


def add_candidate_from_action(
    base: pd.DataFrame,
    l247: np.ndarray,
    action: np.ndarray,
    ctx: pd.DataFrame,
    bad247: np.ndarray,
    bad365: np.ndarray,
    source_id: str,
    source_family: str,
    gate_name: str,
    q2_scale: float,
    s1_scale: float,
    rows: list[dict[str, Any]],
    movement_rows: list[dict[str, Any]],
    seen: set[str],
) -> None:
    q2_w, s1_w = make_gate_weights(ctx, gate_name)
    delta = np.zeros_like(l247)
    delta[:, Q2] = float(q2_scale) * action[:, Q2] * q2_w
    delta[:, S1] = float(s1_scale) * action[:, S1] * s1_w
    if float(np.abs(delta).sum()) <= EPS:
        return
    q2_token = str(q2_scale).replace(".", "p")
    s1_token = str(s1_scale).replace(".", "p")
    variant = f"h002_{source_id}_{gate_name}_q2{q2_token}_s1{s1_token}"
    meta = {
        "source_id": source_id,
        "source_family": source_family,
        "gate": gate_name,
        "q2_scale": float(q2_scale),
        "s1_scale": float(s1_scale),
        "q2_weight_nonzero": int((np.abs(q2_w) > EPS).sum()),
        "s1_weight_nonzero": int((np.abs(s1_w) > EPS).sum()),
        "q2_weight_mean": float(np.mean(q2_w)),
        "s1_weight_mean": float(np.mean(s1_w)),
    }
    before = len(rows)
    write_candidate(base, l247 + delta, variant, "h002_e247locked_q2s1_action_benefit", meta, rows, seen)
    if len(rows) > before:
        movement_rows.append({**rows[-1], **action_meta(delta, action, ctx, bad247, bad365)})


def add_source_file_actions(
    source_csv: Path,
    total_score_col: str,
    limit: int,
    sample: pd.DataFrame,
    l365: np.ndarray,
    l247: np.ndarray,
    base: pd.DataFrame,
    ctx: pd.DataFrame,
    bad247: np.ndarray,
    bad365: np.ndarray,
    rows: list[dict[str, Any]],
    movement_rows: list[dict[str, Any]],
    seen: set[str],
) -> None:
    if not source_csv.exists():
        return
    src = pd.read_csv(source_csv).sort_values(total_score_col, ascending=False).head(limit)
    gates = ["all", "benefit_floor050", "danger_veto25"]
    for _, rec in src.iterrows():
        path = locate(rec["file"])
        sub = load_sub_frame(path, sample)
        src_logit = logit(sub[TARGETS].to_numpy(dtype=np.float64))
        action = np.zeros_like(l247)
        raw_action = src_logit - l365
        action[:, Q2] = raw_action[:, Q2]
        action[:, S1] = raw_action[:, S1]
        path_hash = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:6]
        source_id = safe_id(f"{rec['variant']}_{path_hash}", 60)
        for gate_name in gates:
            add_candidate_from_action(
                base,
                l247,
                action,
                ctx,
                bad247,
                bad365,
                source_id,
                str(rec.get("family", source_csv.stem)),
                gate_name,
                1.0,
                1.0,
                rows,
                movement_rows,
                seen,
            )


def build_candidates() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    for stale in H002.glob("submission_h002_*.csv"):
        stale.unlink()
    anchor, _anchor_logit = load_anchor()
    sample = normalize_dates(anchor[KEY].copy()).sort_values(KEY).reset_index(drop=True)
    sample, frames, logits = build_backbone_logits(sample)
    l247 = logits["e247"]
    l365 = logits["e365"]
    l368 = logits["e368"]
    l323 = logits["e323"]
    base_action = np.zeros_like(l247)
    raw_action = l368 - l365
    base_action[:, Q2] = raw_action[:, Q2]
    base_action[:, S1] = raw_action[:, S1]
    bad247 = l323 - l247
    bad365 = l323 - l365
    ctx = build_action_context(sample, base_action, bad247)

    rows: list[dict[str, Any]] = []
    movement_rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    write_candidate(
        frames["e247"],
        l247,
        "h002_control_e247_identity",
        "h002_control",
        {"source_id": "e247_identity", "source_family": "control", "gate": "identity", "q2_scale": 0.0, "s1_scale": 0.0},
        rows,
        seen,
    )
    movement_rows.append({**rows[-1], **action_meta(np.zeros_like(l247), base_action, ctx, bad247, bad365)})

    for name, logits_key in [("e365_body", "e365"), ("e368_public_file", "e368")]:
        write_candidate(
            frames["e247"],
            logits[logits_key],
            f"h002_control_{name}",
            "h002_control",
            {"source_id": name, "source_family": "control", "gate": "control_body", "q2_scale": np.nan, "s1_scale": np.nan},
            rows,
            seen,
        )
        sub_delta = logits[logits_key] - l247
        movement_rows.append({**rows[-1], **action_meta(sub_delta, base_action, ctx, bad247, bad365)})

    q2_scales = [0.0, 0.25, 0.50, 0.75, 1.00, 1.08]
    s1_scales = [0.0, 0.50, 0.75, 1.00, 1.15]
    gates = [
        "all",
        "benefit_floor035",
        "benefit_floor050",
        "benefit_top25",
        "benefit_top35",
        "benefit_transfer_soft",
        "validity_lowbad",
        "danger_veto25",
        "q2_off_s1_benefit",
    ]
    for gate_name in gates:
        for q2_scale in q2_scales:
            for s1_scale in s1_scales:
                if q2_scale == 0.0 and s1_scale == 0.0:
                    continue
                add_candidate_from_action(
                    frames["e247"],
                    l247,
                    base_action,
                    ctx,
                    bad247,
                    bad365,
                    "e368_minus_e365",
                    "e368_base_action",
                    gate_name,
                    q2_scale,
                    s1_scale,
                    rows,
                    movement_rows,
                    seen,
                )

    add_source_file_actions(
        OUT / "e371_q2_rowwise_safety_decision.csv",
        "e371_total_score",
        10,
        sample,
        l365,
        l247,
        frames["e247"],
        ctx,
        bad247,
        bad365,
        rows,
        movement_rows,
        seen,
    )
    add_source_file_actions(
        OUT / "e370_q2s1_risk_constrained_decision.csv",
        "e370_total_score",
        8,
        sample,
        l365,
        l247,
        frames["e247"],
        ctx,
        bad247,
        bad365,
        rows,
        movement_rows,
        seen,
    )

    candidates = pd.DataFrame(rows)
    movement = pd.DataFrame(movement_rows)
    candidates.to_csv(CANDIDATES_OUT, index=False)
    movement.to_csv(MOVEMENT_OUT, index=False)
    return candidates, movement, ctx


def score_candidates(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    rowmask = normalize_dates(pd.read_csv(e368.ROWMASK_OUT)).sort_values(KEY).reset_index(drop=True)

    e360.KNOWN_OUT = H002 / "h002_rowstate_known.csv"
    e368.KNOWN_OUT = H002 / "h002_public_known.csv"
    e368.SCORES_OUT = SCORES_OUT
    e368.SCENARIOS_OUT = SCENARIOS_OUT
    e368.RANKS_OUT = RANKS_OUT
    e368.SUPPORT_OUT = SUPPORT_OUT

    selector = selector_scores(candidates, anchor)
    rowstate = rowstate_public_scores(selector, anchor, anchor_logit, state, base_cols, story_cols)
    e363_scored = add_e363_scores(rowstate)
    combined, known_scored, _feature_cols = e368.public_score_candidates(e363_scored, rowmask)
    combined["candidate_origin"] = combined["candidate_origin"].replace({"e368_generated": "h002_generated"})
    feature_sets = e368.available_feature_sets(known_scored, combined)
    scenarios, ranks = e368.run_scenarios(known_scored, combined, feature_sets, "h002_control_e247_identity")
    if "candidate_origin" in ranks.columns:
        ranks["candidate_origin"] = ranks["candidate_origin"].replace({"e368_generated": "h002_generated"})
    support = e368.aggregate_support(ranks, len(scenarios)) if len(ranks) else pd.DataFrame()
    if "candidate_origin" in support.columns:
        support["candidate_origin"] = support["candidate_origin"].replace({"e368_generated": "h002_generated"})
    combined.to_csv(SCORES_OUT, index=False)
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    ranks.to_csv(RANKS_OUT, index=False)
    support.to_csv(SUPPORT_OUT, index=False)
    return combined, scenarios, support


def select_candidate(movement: pd.DataFrame, combined: pd.DataFrame, support: pd.DataFrame) -> pd.DataFrame:
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
    movement_metric_cols = [
        "move_l1",
        "move_l2",
        "changed_cells_1e12",
        "changed_rows_1e12",
        "non_q2s1_l1",
        "all_cos_e323_bad_vs_e247",
        "all_cos_e323_bad_vs_e365",
        "q2_cos_e323_bad_vs_e247",
        "q2_cos_e323_bad_vs_e365",
        "s1_cos_e323_bad_vs_e247",
        "s1_cos_e323_bad_vs_e365",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "q2_benefit_abs_wmean",
        "s1_benefit_abs_wmean",
        "q2_danger_abs_wmean",
        "s1_danger_abs_wmean",
        "q2_benefit_minus_danger",
        "s1_benefit_minus_danger",
        "q2_base_action_abs_spearman",
        "s1_base_action_abs_spearman",
        "l1_Q1",
        "l1_Q2",
        "l1_Q3",
        "l1_S1",
        "l1_S2",
        "l1_S3",
        "l1_S4",
    ]
    for col in movement_metric_cols:
        move_col = f"{col}_move"
        if move_col in work.columns:
            work[col] = work[move_col]
    generated = work[work["family"].astype(str).eq("h002_e247locked_q2s1_action_benefit")].copy()
    numeric_cols = [
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
        "q2_cos_e323_bad_vs_e365",
        "q2_benefit_minus_danger",
        "s1_benefit_minus_danger",
        "q2_benefit_abs_wmean",
        "s1_benefit_abs_wmean",
        "q2_danger_abs_wmean",
        "s1_danger_abs_wmean",
        "non_q2s1_l1",
        "move_l1",
        "l1_Q2",
        "l1_S1",
    ]
    for col in numeric_cols:
        if col in generated.columns:
            generated[col] = pd.to_numeric(generated[col], errors="coerce").fillna(0.0)

    generated["h002_action_score"] = (
        0.80 * rank01(generated["top1_rate"])
        + 0.55 * rank01(generated["top10_rate"])
        + 0.45 * rank01(generated["e368_public_like_score"])
        + 0.40 * rank01(-generated["rowstate_pred_public_loss_mean"])
        + 0.32 * rank01(-generated["rowstate_bad_minus_good_exposure"])
        + 0.28 * rank01(-generated["public_bad_axis_sum"])
        + 0.55 * rank01(generated["q2_benefit_minus_danger"])
        + 0.40 * rank01(generated["s1_benefit_minus_danger"])
        + 0.35 * rank01(generated["q2_transfer_abs_spearman"])
        + 0.25 * rank01(generated["s1_transfer_abs_spearman"])
        + 0.70 * rank01(-generated["q2_cos_e323_bad_vs_e247"].clip(lower=0.0))
    )
    generated["hard_invariant_ok"] = generated["non_q2s1_l1"].abs() <= 1.0e-10
    generated["action_context_ok"] = (
        (generated["q2_cos_e323_bad_vs_e247"] <= 0.05)
        & (generated["q2_benefit_minus_danger"] >= -0.05)
        & (generated["s1_benefit_minus_danger"] >= -0.10)
        & (generated["q2_benefit_abs_wmean"] >= 0.40)
        & (generated["s1_benefit_abs_wmean"] >= 0.35)
    )
    generated["stress_ready"] = (
        generated["hard_invariant_ok"]
        & generated["action_context_ok"]
        & generated["e363_submission_gate"].fillna(False).astype(bool)
        & (generated["top10_rate"] >= 0.08)
    )
    generated["human_review_ready"] = (
        generated["hard_invariant_ok"]
        & generated["action_context_ok"]
        & (generated["q2_cos_e323_bad_vs_e247"] <= 0.02)
        & (generated["move_l1"] <= 0.30)
        & (generated["l1_Q2"] <= 0.12)
        & (generated["l1_S1"] <= 0.22)
    )
    generated = generated.sort_values("h002_action_score", ascending=False)
    selected = generated[generated["stress_ready"]].head(1).copy()
    if len(selected):
        decision = "promote_h002_e247locked_action_benefit_candidate"
        reason = "E247-locked Q2/S1 action is concentrated on benefit rows and passes the current public-free stress gate."
        src = ROOT / str(selected.iloc[0]["file"])
        upload = H002 / f"submission_{safe_id(str(selected.iloc[0]['variant']), 80)}_{short_hash(pd.read_csv(src))}_uploadsafe.csv"
        shutil.copyfile(src, upload)
    else:
        selected = generated.head(1).copy()
        decision = "diagnostic_only_no_h002_submission"
        reason = "No E247-locked action-benefit candidate passed the conservative stress-ready gate; use the top row as a diagnostic, not a submission."
        upload = None
    selected["decision"] = decision
    selected["reason"] = reason
    selected["stress_ready_count"] = int(generated["stress_ready"].sum())
    selected["human_review_ready_count"] = int(generated["human_review_ready"].sum())
    selected["selected_uploadsafe_file"] = rel(upload) if upload is not None else "none"
    selected.to_csv(SELECTION_OUT, index=False)
    generated.to_csv(RANKED_OUT, index=False)
    return selected


def write_report(movement: pd.DataFrame, support: pd.DataFrame, selected: pd.DataFrame) -> None:
    ranked = pd.read_csv(RANKED_OUT)
    selection_cols = [
        "decision",
        "variant",
        "stress_ready_count",
        "human_review_ready_count",
        "selected_uploadsafe_file",
        "reason",
        "source_id",
        "gate",
        "q2_scale",
        "s1_scale",
        "top1_rate",
        "top10_rate",
        "e363_submission_gate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e247",
        "q2_benefit_minus_danger",
        "s1_benefit_minus_danger",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "h002_action_score",
    ]
    top_cols = [
        "variant",
        "source_id",
        "gate",
        "q2_scale",
        "s1_scale",
        "stress_ready",
        "human_review_ready",
        "top1_rate",
        "top10_rate",
        "e363_submission_gate",
        "e368_public_like_score",
        "rowstate_pred_public_loss_mean",
        "public_bad_axis_sum",
        "q2_cos_e323_bad_vs_e247",
        "q2_benefit_minus_danger",
        "s1_benefit_minus_danger",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "move_l1",
        "l1_Q2",
        "l1_S1",
        "h002_action_score",
        "file",
    ]
    move_cols = [
        "variant",
        "source_id",
        "gate",
        "q2_scale",
        "s1_scale",
        "move_l1",
        "non_q2s1_l1",
        "l1_Q2",
        "l1_S1",
        "q2_cos_e323_bad_vs_e247",
        "q2_cos_e323_bad_vs_e365",
        "q2_benefit_abs_wmean",
        "q2_danger_abs_wmean",
        "s1_benefit_abs_wmean",
        "s1_danger_abs_wmean",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "file",
    ]
    lines = [
        "# H002 E247-Locked Q2/S1 Action-Benefit Selector",
        "",
        "## Question",
        "",
        "Can the Q2/S1 hidden lifestyle-state action become useful when E247 is fixed and action is applied only to rows with high benefit and low E247-frame risk?",
        "",
        "## Construction",
        "",
        "- Base body: E247 public-best, fixed.",
        "- Action sources: E368-minus-E365 Q2/S1, plus top E370/E371 row-wise Q2/S1 actions re-expressed in the E247 frame.",
        "- Context: public-free transfer, learned Q2/S1 validity, row validity, bad-row rank, and E247-frame E323 contribution risk.",
        "- Hard invariant: Q1/Q3/S2/S3/S4 stay exactly E247 for generated candidates.",
        "",
        "## Selection",
        "",
        md_table(selected[[c for c in selection_cols if c in selected.columns]], n=5, floatfmt=".9f"),
        "",
        "## Top H002 Candidates",
        "",
        md_table(ranked[[c for c in top_cols if c in ranked.columns]].head(35), n=35, floatfmt=".9f"),
        "",
        "## Movement Audit",
        "",
        md_table(movement[[c for c in move_cols if c in movement.columns]].head(45), n=45, floatfmt=".9f"),
        "",
        "## Scenario Support",
        "",
        md_table(support.head(30), n=30, floatfmt=".9f") if len(support) else "(no scenario-gated support rows)",
        "",
        "## Interpretation",
        "",
    ]
    if str(selected["decision"].iloc[0]).startswith("promote_"):
        lines.append(
            "H002 found an E247-locked Q2/S1 action-benefit candidate that passes the current local stress. This supports the row-selective hidden-state hypothesis."
        )
    else:
        lines.append(
            "H002 did not find a submission-ready E247-locked Q2/S1 selector. This weakens the idea that the current Q2/S1 latent can be safely translated by row selection alone; the next useful test should either improve the benefit target or move beyond Q2/S1-only edits."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(CONTEXT_OUT)}`",
            f"- `{rel(CANDIDATES_OUT)}`",
            f"- `{rel(MOVEMENT_OUT)}`",
            f"- `{rel(SCORES_OUT)}`",
            f"- `{rel(SCENARIOS_OUT)}`",
            f"- `{rel(RANKS_OUT)}`",
            f"- `{rel(SUPPORT_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
            f"- `{rel(RANKED_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    candidates, movement, _ctx = build_candidates()
    combined, scenarios, support = score_candidates(candidates)
    selected = select_candidate(movement, combined, support)
    write_report(movement, support, selected)
    print(f"h002_candidates={len(candidates)} scenarios={len(scenarios)}")
    print(
        selected[
            [
                "decision",
                "variant",
                "stress_ready_count",
                "human_review_ready_count",
                "selected_uploadsafe_file",
                "reason",
            ]
        ].to_string(index=False)
    )
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
