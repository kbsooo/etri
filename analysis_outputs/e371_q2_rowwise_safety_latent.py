#!/usr/bin/env python3
"""E371: row-wise Q2 safety/calibration latent.

E370 showed that linear Q2 projection away from the E323 bad axis removes
validated Q2 lifestyle signal.  This experiment asks a narrower JEPA-style
question:

    context = public-free Q2 transfer score, E368 Q2 row-validity score,
              and row-wise E323 contribution risk
    target  = a row-wise Q2 trust representation, not raw Q2 probability
              reconstruction
    action  = keep E365/E368 structure, but damp Q2 only where transfer support
              is weak and E323-like contribution is high

The goal is not to sweep another blend.  The falsifiable claim is that a
row-wise safety latent can lower Q2 bad-axis exposure without deleting the
public-free lifestyle transfer signal that made E368 useful.
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
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import e368_q2s1_rowmask_cellaction_latent as e368  # noqa: E402
import e370_q2s1_risk_constrained_recalibration as e370  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import (  # noqa: E402
    clip_prob,
    load_sub_frame,
    md_table,
    normalize_dates,
    require_aligned,
    safe_id,
    sigmoid,
)
from e357_public_survival_contrast_latent import KEY, TARGETS  # noqa: E402
from e358_rowstate_public_survival_audit import load_anchor  # noqa: E402
from e369_q2s1_lifestyle_transfer_audit import load_e368_gate, rank01, safe_spearman  # noqa: E402
from public_anchor_bottleneck_decomposition import logit  # noqa: E402


EPS = 1.0e-12
UPLOAD_PREFIX = "submission_e371_q2rowsafe"

TRANSFER_ROWS_OUT = OUT / "e371_q2_rowwise_safety_transfer_rows.csv"
CANDIDATE_OUT = OUT / "e371_q2_rowwise_safety_candidates.csv"
SCORES_OUT = OUT / "e371_q2_rowwise_safety_scores.csv"
SCENARIOS_OUT = OUT / "e371_q2_rowwise_safety_scenarios.csv"
RANKS_OUT = OUT / "e371_q2_rowwise_safety_scenario_ranks.csv"
SUPPORT_OUT = OUT / "e371_q2_rowwise_safety_support.csv"
SELECTION_OUT = OUT / "e371_q2_rowwise_safety_selection.csv"
DECISION_OUT = OUT / "e371_q2_rowwise_safety_decision.csv"
GATE_DIAG_OUT = OUT / "e371_q2_rowwise_safety_gate_diagnostics.csv"
REPORT_OUT = OUT / "e371_q2_rowwise_safety_report.md"


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
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb) + EPS)
    return float(np.sum(aa * bb) / denom)


def clip_weight(w: np.ndarray, lo: float = 0.0, hi: float = 1.35) -> np.ndarray:
    return np.clip(np.nan_to_num(np.asarray(w, dtype=np.float64), nan=0.0, posinf=hi, neginf=lo), lo, hi)


def renorm_to_l1(delta: np.ndarray, ref: np.ndarray, strength: float) -> np.ndarray:
    if strength <= 0:
        return delta
    src = float(np.sum(np.abs(ref)))
    cur = float(np.sum(np.abs(delta)))
    if src <= EPS or cur <= EPS:
        return delta
    factor = (1.0 - strength) + strength * (src / cur)
    return delta * factor


def q2_contrib_metrics(delta: np.ndarray, bad: np.ndarray) -> dict[str, float]:
    prod = np.asarray(delta, dtype=np.float64) * np.asarray(bad, dtype=np.float64)
    abs_sum = float(np.sum(np.abs(prod)) + EPS)
    pos = float(np.sum(np.clip(prod, 0.0, None)))
    neg = float(np.sum(np.clip(-prod, 0.0, None)))
    return {
        "q2_bad_positive_contrib": pos,
        "q2_bad_negative_contrib": neg,
        "q2_bad_positive_share": pos / abs_sum,
        "q2_bad_signed_sum": float(np.sum(prod)),
    }


def write_candidate(base: pd.DataFrame, logits: np.ndarray, meta: dict[str, Any], rows: list[dict[str, Any]], seen: set[str]) -> None:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    digest = short_hash(out)
    if digest in seen:
        return
    seen.add(digest)
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(str(meta['variant']), 92)}_{digest}.csv"
    out.to_csv(path, index=False)
    rows.append({**meta, "file": rel(path), "basename": path.name})


def patch_e370_outputs() -> None:
    e370.TRANSFER_ROWS_OUT = TRANSFER_ROWS_OUT
    e370.SCORES_OUT = SCORES_OUT
    e370.SCENARIOS_OUT = SCENARIOS_OUT
    e370.RANKS_OUT = RANKS_OUT
    e370.SUPPORT_OUT = SUPPORT_OUT


def build_rowwise_context(anchor: pd.DataFrame) -> pd.DataFrame:
    patch_e370_outputs()
    transfer, _meta = e370.build_transfer_vectors(anchor)
    gate = load_e368_gate(anchor[KEY])
    ctx = normalize_dates(anchor[KEY].copy()).sort_values(KEY).reset_index(drop=True)
    require_aligned(ctx, transfer[KEY], "e371_transfer")
    require_aligned(ctx, gate[KEY], "e371_e368_gate")
    ctx["q2_transfer"] = rank01(transfer["q2_publicfree_transfer_score"])
    ctx["s1_transfer"] = rank01(transfer["s1_publicfree_transfer_score"])
    ctx["q2_gate"] = rank01(gate["q2_gate_pred"])
    ctx["s1_gate"] = rank01(gate["s1_gate_pred"])
    ctx["bad_gate"] = rank01(gate["bad_gate_pred"])
    ctx["row_validity"] = rank01(gate["row_validity_pred"])
    return ctx


def generate_candidates(anchor: pd.DataFrame, ctx: pd.DataFrame) -> pd.DataFrame:
    e365, e368_sel, e247, e323 = e370.load_backbones(anchor[KEY].copy())
    l365 = logit(e365[TARGETS].to_numpy(dtype=np.float64))
    l368 = logit(e368_sel[TARGETS].to_numpy(dtype=np.float64))
    l247 = logit(e247[TARGETS].to_numpy(dtype=np.float64))
    l323 = logit(e323[TARGETS].to_numpy(dtype=np.float64))
    base_delta = l368 - l365
    bad365 = l323 - l365
    bad247 = l323 - l247
    q2_idx = TARGETS.index("Q2")
    s1_idx = TARGETS.index("S1")

    q2_base = base_delta[:, q2_idx]
    s1_base = base_delta[:, s1_idx]
    q2_bad = bad365[:, q2_idx]
    transfer = ctx["q2_transfer"].to_numpy(dtype=np.float64)
    q2_gate = ctx["q2_gate"].to_numpy(dtype=np.float64)
    bad_gate = ctx["bad_gate"].to_numpy(dtype=np.float64)
    raw_bad_contrib = np.clip(q2_base * q2_bad, 0.0, None)
    contrib_risk = rank01(raw_bad_contrib)
    signed_risk = rank01(np.maximum(q2_base * q2_bad, 0.0))
    trust = rank01(0.48 * transfer + 0.32 * q2_gate + 0.20 * ctx["row_validity"].to_numpy(dtype=np.float64) - 0.35 * contrib_risk - 0.20 * bad_gate)
    safe_low = rank01(0.70 * transfer + 0.30 * q2_gate - 0.70 * contrib_risk)
    danger = rank01(0.65 * contrib_risk + 0.25 * bad_gate + 0.10 * (1.0 - transfer))

    gate_diag = pd.DataFrame(
        {
            **{k: ctx[k] for k in KEY},
            "q2_transfer": transfer,
            "q2_gate": q2_gate,
            "bad_gate": bad_gate,
            "q2_bad_contrib_risk": contrib_risk,
            "q2_trust": trust,
            "q2_safe_low": safe_low,
            "q2_danger": danger,
            "base_q2_abs_delta": np.abs(q2_base),
            "base_q2_bad_contrib": raw_bad_contrib,
        }
    )
    gate_diag.to_csv(GATE_DIAG_OUT, index=False)

    specs: list[tuple[str, np.ndarray, float]] = []
    specs.append(("identity", np.ones_like(q2_base), 0.0))
    for floor in [0.35, 0.50, 0.65]:
        for gamma in [0.7, 1.0, 1.5]:
            specs.append((f"transfer_floor{floor}_g{gamma}", floor + (1.0 - floor) * np.power(transfer, gamma), 0.25))
            specs.append((f"trust_floor{floor}_g{gamma}", floor + (1.0 - floor) * np.power(trust, gamma), 0.35))
    for damp in [0.25, 0.40, 0.55, 0.70]:
        specs.append((f"riskdamp{damp}", 1.0 - damp * danger * np.power(1.0 - transfer, 0.8), 0.15))
        specs.append((f"contribdamp{damp}", 1.0 - damp * contrib_risk * np.power(1.0 - safe_low, 0.8), 0.15))
    for keep_q in [0.55, 0.65, 0.75, 0.85]:
        keep = trust >= np.quantile(trust, keep_q)
        for floor in [0.25, 0.45, 0.65]:
            specs.append((f"hardtrust_q{keep_q}_floor{floor}", np.where(keep, 1.0, floor), 0.20))
    for cut in [0.70, 0.80, 0.90]:
        risky = (contrib_risk >= np.quantile(contrib_risk, cut)) & (transfer <= np.quantile(transfer, 0.55))
        specs.append((f"badtop{cut}_weaktransfer_damp25", np.where(risky, 0.25, 1.0), 0.10))
        specs.append((f"badtop{cut}_weaktransfer_damp45", np.where(risky, 0.45, 1.0), 0.10))

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for gate_name, raw_weight, renorm_strength in specs:
        for q2_scale in [0.85, 1.00, 1.08]:
            for s1_scale in [1.00, 1.06, 1.15]:
                weight = clip_weight(raw_weight)
                q2_delta = q2_scale * q2_base * weight
                q2_delta = renorm_to_l1(q2_delta, q2_base, renorm_strength)
                delta = np.zeros_like(base_delta)
                delta[:, q2_idx] = q2_delta
                delta[:, s1_idx] = s1_scale * s1_base
                if float(np.sum(np.abs(delta))) <= EPS:
                    continue
                logits = l365 + delta
                variant = f"e371_{gate_name}_q2{str(q2_scale).replace('.', 'p')}_s1{str(s1_scale).replace('.', 'p')}"
                metrics = q2_contrib_metrics(q2_delta, q2_bad)
                meta = {
                    "variant": variant,
                    "family": "q2_rowwise_safety_lifestyle_gate",
                    "gate_name": gate_name,
                    "q2_scale": q2_scale,
                    "s1_scale": s1_scale,
                    "q2_weight_mean": float(np.mean(weight)),
                    "q2_weight_min": float(np.min(weight)),
                    "q2_weight_p10": float(np.quantile(weight, 0.10)),
                    "q2_weight_p90": float(np.quantile(weight, 0.90)),
                    "q2_weight_max": float(np.max(weight)),
                    "q2_weight_transfer_spearman": safe_spearman(weight, transfer),
                    "q2_weight_risk_spearman": safe_spearman(weight, contrib_risk),
                    "q2_l1": float(np.sum(np.abs(q2_delta))),
                    "s1_l1": float(np.sum(np.abs(delta[:, s1_idx]))),
                    "all_l1": float(np.sum(np.abs(delta))),
                    "all_cos_e323_bad_vs_e365": cos(delta, bad365),
                    "all_cos_e323_bad_vs_e247": cos(delta, bad247),
                    "q2_cos_e323_bad_vs_e365": cos(q2_delta, q2_bad) if np.linalg.norm(q2_delta) > EPS else 0.0,
                    "q2_cos_e323_bad_vs_e247": cos(q2_delta, bad247[:, q2_idx]) if np.linalg.norm(q2_delta) > EPS else 0.0,
                    "s1_cos_e323_bad_vs_e365": cos(delta[:, s1_idx], bad365[:, s1_idx]) if np.linalg.norm(delta[:, s1_idx]) > EPS else 0.0,
                    "q2_transfer_abs_spearman": safe_spearman(np.abs(q2_delta), transfer),
                    "s1_transfer_abs_spearman": safe_spearman(np.abs(delta[:, s1_idx]), ctx["s1_transfer"].to_numpy(dtype=np.float64)),
                    "q2_transfer_signed_spearman": safe_spearman(q2_delta, transfer),
                    "s1_transfer_signed_spearman": safe_spearman(delta[:, s1_idx], ctx["s1_transfer"].to_numpy(dtype=np.float64)),
                    **metrics,
                }
                write_candidate(e365, logits, meta, rows, seen)
    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def score_candidates(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    patch_e370_outputs()
    rowmask = normalize_dates(pd.read_csv(e368.ROWMASK_OUT)).sort_values(KEY).reset_index(drop=True)
    combined, scenarios, support = e370.score_candidates(candidates, rowmask)
    for frame in [combined, support]:
        if "candidate_origin" in frame.columns:
            frame["candidate_origin"] = frame["candidate_origin"].replace({"e370_generated": "e371_generated"})
    if "top_origin" in scenarios.columns:
        scenarios["top_origin"] = scenarios["top_origin"].replace({"e370_generated": "e371_generated"})
    combined.to_csv(SCORES_OUT, index=False)
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    support.to_csv(SUPPORT_OUT, index=False)
    if RANKS_OUT.exists():
        ranks = pd.read_csv(RANKS_OUT)
        if "candidate_origin" in ranks.columns:
            ranks["candidate_origin"] = ranks["candidate_origin"].replace({"e370_generated": "e371_generated"})
            ranks.to_csv(RANKS_OUT, index=False)
    return combined, scenarios, support


def select_candidate(candidates: pd.DataFrame, combined: pd.DataFrame, support: pd.DataFrame) -> pd.DataFrame:
    e368_sel = pd.read_csv(e370.E368_SELECTION).iloc[0]
    e365_variant = str(pd.read_csv(e370.E365_SELECTION).iloc[0]["variant"])
    work = combined.merge(
        support[["variant", "top1_rate", "top5_rate", "top10_rate", "rank_mean", "score_mean"]],
        on="variant",
        how="left",
    )
    meta_cols = [
        "gate_name",
        "q2_scale",
        "s1_scale",
        "q2_weight_transfer_spearman",
        "q2_weight_risk_spearman",
        "all_cos_e323_bad_vs_e365",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "q2_transfer_signed_spearman",
        "s1_transfer_signed_spearman",
    ]
    missing = [c for c in meta_cols if c not in work.columns]
    if missing:
        work = work.merge(candidates[["variant"] + missing], on="variant", how="left")
    generated = work[work["candidate_origin"].astype(str).eq("e371_generated")].copy()
    for col in [
        "top1_rate",
        "top5_rate",
        "top10_rate",
        "rank_mean",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
    ]:
        generated[col] = pd.to_numeric(generated[col], errors="coerce").fillna(0.0)

    current = generated[
        generated["gate_name"].astype(str).eq("identity")
        & generated["q2_scale"].round(6).eq(1.0)
        & generated["s1_scale"].round(6).eq(1.0)
    ].head(1)
    if current.empty:
        current = generated.sort_values("e368_public_like_score", ascending=False).head(1)
    cur = current.iloc[0]

    generated["e371_scenario_score"] = (
        0.90 * generated["top1_rate"]
        + 0.55 * generated["top5_rate"]
        + 0.35 * generated["top10_rate"]
        + 0.30 * rank01(generated["e368_public_like_score"])
    )
    generated["e371_transfer_score"] = (
        0.80 * rank01(generated["q2_transfer_abs_spearman"])
        + 0.45 * rank01(generated["s1_transfer_abs_spearman"])
        + 0.20 * rank01(generated["q2_weight_transfer_spearman"].fillna(0.0))
        + 0.20 * rank01(-generated["q2_weight_risk_spearman"].fillna(0.0))
    )
    generated["e371_safety_score"] = (
        0.95 * rank01(-generated["q2_cos_e323_bad_vs_e365"].clip(lower=0.0))
        + 0.70 * rank01(-generated["q2_bad_positive_share"])
        + 0.65 * rank01(-generated["all_cos_e323_bad_vs_e365"].abs())
        + 0.50 * rank01(-generated["public_bad_axis_sum"].fillna(0.0))
        + 0.40 * rank01(-generated["rowstate_pred_public_loss_mean"].fillna(0.0))
        + 0.30 * rank01(-generated["rowstate_bad_minus_good_exposure"].fillna(0.0))
    )
    generated["e371_total_score"] = generated["e371_scenario_score"] + 0.70 * generated["e371_transfer_score"] + 0.80 * generated["e371_safety_score"]

    cur_q2_bad = float(cur["q2_cos_e323_bad_vs_e365"])
    cur_q2_pos = float(cur["q2_bad_positive_share"])
    cur_top10 = float(cur["top10_rate"])
    cur_pls = float(cur["e368_public_like_score"])
    cur_q2_transfer = float(cur["q2_transfer_abs_spearman"])
    eligible = generated[
        generated["e363_submission_gate"].fillna(False).astype(bool)
        & (generated["top10_rate"] >= max(0.55, cur_top10 - 0.10))
        & (generated["e368_public_like_score"] >= cur_pls - 0.12)
        & (generated["q2_cos_e323_bad_vs_e365"] <= cur_q2_bad - 0.04)
        & (generated["q2_bad_positive_share"] <= cur_q2_pos - 0.025)
        & (generated["all_cos_e323_bad_vs_e365"].abs() <= 0.05)
        & (generated["q2_transfer_abs_spearman"] >= cur_q2_transfer - 0.08)
        & (generated["s1_transfer_abs_spearman"] >= 0.10)
    ].copy()
    if len(eligible):
        chosen = eligible.sort_values("e371_total_score", ascending=False).head(1).copy()
        decision = "select_e371_q2_rowwise_safety_replacement"
        reason = "A row-wise Q2 safety latent lowers Q2 bad-axis exposure while preserving E368 stress and public-free transfer support."
        src = e370.locate(chosen.iloc[0]["file"])
        for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
            stale.unlink()
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(chosen.iloc[0]['variant']), 70)}_{short_hash(pd.read_csv(src))}_uploadsafe.csv"
        shutil.copyfile(src, upload)
    else:
        chosen = current.copy()
        decision = "keep_e368_no_rowwise_safe_replacement"
        reason = "No row-wise Q2 safety gate reduced the Q2 bad-axis warning enough while preserving E368 support and public-free transfer alignment."
        upload = e370.locate(e368_sel["selected_uploadsafe_file"])

    chosen["decision"] = decision
    chosen["reason"] = reason
    chosen["e365_variant"] = e365_variant
    chosen["current_q2_bad_cos"] = cur_q2_bad
    chosen["current_q2_bad_positive_share"] = cur_q2_pos
    chosen["current_q2_transfer_abs_spearman"] = cur_q2_transfer
    chosen["current_top10_rate"] = cur_top10
    chosen["eligible_count"] = int(len(eligible))
    chosen["selected_uploadsafe_file"] = rel(upload)
    chosen.to_csv(SELECTION_OUT, index=False)
    generated.sort_values("e371_total_score", ascending=False).to_csv(DECISION_OUT, index=False)
    return chosen


def write_report(selected: pd.DataFrame, support: pd.DataFrame) -> None:
    ranked = pd.read_csv(DECISION_OUT)
    selection_cols = [
        "decision",
        "variant",
        "eligible_count",
        "selected_uploadsafe_file",
        "reason",
        "gate_name",
        "q2_scale",
        "s1_scale",
        "top1_rate",
        "top10_rate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
    ]
    top_cols = [
        "variant",
        "gate_name",
        "q2_scale",
        "s1_scale",
        "top1_rate",
        "top10_rate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "q2_weight_transfer_spearman",
        "q2_weight_risk_spearman",
        "e371_total_score",
        "file",
    ]
    decision = str(selected["decision"].iloc[0])
    lines = [
        "# E371 Q2 Row-Wise Safety Latent",
        "",
        "## Question",
        "",
        "Can the E368 Q2 movement be made safer by a row-wise lifestyle-state trust gate instead of a linear E323 projection?",
        "",
        "## Selection",
        "",
        md_table(selected[[c for c in selection_cols if c in selected.columns]], n=5, floatfmt=".9f"),
        "",
        "## Top E371 Candidates",
        "",
        md_table(ranked[[c for c in top_cols if c in ranked.columns]].head(35), n=35, floatfmt=".9f"),
        "",
        "## Scenario Support",
        "",
        md_table(support.head(30), n=30, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    if decision.startswith("select_"):
        lines.append(
            "A row-wise Q2 safety gate survives the current local stress. Treat it as a candidate only after checking that the public-free Q2 transfer loss is small enough for the intended public probe."
        )
    else:
        lines.append(
            "The row-wise safety gate did not produce a safer E368 replacement. The useful negative result is that current Q2 trust scores lower risk mainly by shrinking or distorting the Q2 signal."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GATE_DIAG_OUT.name}`",
            f"- `{SCORES_OUT.name}`",
            f"- `{SCENARIOS_OUT.name}`",
            f"- `{RANKS_OUT.name}`",
            f"- `{SUPPORT_OUT.name}`",
            f"- `{SELECTION_OUT.name}`",
            f"- `{DECISION_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    anchor, _anchor_logit = load_anchor()
    sample = normalize_dates(anchor[KEY].copy()).sort_values(KEY).reset_index(drop=True)
    ctx = build_rowwise_context(sample)
    candidates = generate_candidates(sample, ctx)
    combined, scenarios, support = score_candidates(candidates)
    selected = select_candidate(candidates, combined, support)
    write_report(selected, support)
    print(f"generated_candidates={len(candidates)} scenarios={len(scenarios)}")
    print(selected[["decision", "variant", "eligible_count", "selected_uploadsafe_file", "reason"]].to_string(index=False))
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
