#!/usr/bin/env python3
"""E370: Q2/S1 risk-constrained recalibration after E369.

Question:
    E369 says the E368 Q2/S1 movement is backed by a public-free hidden
    lifestyle residual state.  But E369 also found a Q2-only E323-axis warning
    versus the E365 backbone.  Is there a safer Q2/S1 amplitude/orthogonalized
    variant that keeps the lifestyle-transfer signal while reducing Q2 bad-axis
    exposure?

This is deliberately a small, falsifiable experiment.  It does not search
arbitrary features or model families; it only edits the E368-vs-E365 Q2/S1
delta and stress-tests whether a safer version deserves to replace E368.
"""

from __future__ import annotations

import hashlib
import re
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
from e328_ownlatent_lifestyle_state_experiment import (  # noqa: E402
    build_views,
    clip_prob,
    load_frames,
    load_sub_frame,
    md_table,
    normalize_dates,
    require_aligned,
    safe_id,
    sigmoid,
)
from e357_public_survival_contrast_latent import KEY, TARGETS  # noqa: E402
from e358_rowstate_public_survival_audit import load_anchor, load_row_state  # noqa: E402
from e359_rowplacement_action_health_probe import selector_scores  # noqa: E402
from e360_learned_row_action_health_generator import rowstate_public_scores  # noqa: E402
from e363_cell_action_robustness_probe import add_e363_scores  # noqa: E402
from e369_q2s1_lifestyle_transfer_audit import (  # noqa: E402
    build_cluster_scores,
    build_knn_scores,
    collect_alignment_rows,
    fit_base_context_residuals,
    load_e368_gate,
    movement_audit,
    rank01,
    safe_spearman,
    support_from_null,
    z01,
)
from public_anchor_bottleneck_decomposition import logit  # noqa: E402


RNG_SEED = 20260531 + 370
EPS = 1.0e-12
UPLOAD_PREFIX = "submission_e370_q2s1safe"

E365_SELECTION = OUT / "e365_public_like_jackknife_selection.csv"
E368_SELECTION = OUT / "e368_q2s1_rowmask_cellaction_selection.csv"
E369_SUMMARY = OUT / "e369_q2s1_lifestyle_transfer_summary.csv"

CANDIDATE_OUT = OUT / "e370_q2s1_risk_constrained_candidates.csv"
TRANSFER_ROWS_OUT = OUT / "e370_q2s1_risk_constrained_transfer_rows.csv"
SCORES_OUT = OUT / "e370_q2s1_risk_constrained_scores.csv"
SCENARIOS_OUT = OUT / "e370_q2s1_risk_constrained_scenarios.csv"
RANKS_OUT = OUT / "e370_q2s1_risk_constrained_scenario_ranks.csv"
SUPPORT_OUT = OUT / "e370_q2s1_risk_constrained_support.csv"
SELECTION_OUT = OUT / "e370_q2s1_risk_constrained_selection.csv"
DECISION_OUT = OUT / "e370_q2s1_risk_constrained_decision.csv"
REPORT_OUT = OUT / "e370_q2s1_risk_constrained_report.md"


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


def locate(path_or_name: object) -> Path:
    raw = Path(str(path_or_name))
    candidates = [raw] if raw.is_absolute() else [ROOT / raw, OUT / raw.name, OUT / str(path_or_name)]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(str(path_or_name))


def cos(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb) + EPS)
    return float(np.sum(aa * bb) / denom)


def project_away(delta: np.ndarray, bad: np.ndarray, alpha: float, renorm: bool) -> np.ndarray:
    d = np.asarray(delta, dtype=np.float64).copy()
    b = np.asarray(bad, dtype=np.float64)
    denom = float(np.sum(b * b) + EPS)
    comp = float(np.sum(d * b) / denom) * b
    out = d - float(alpha) * comp
    if renorm:
        src_l1 = float(np.sum(np.abs(d)))
        out_l1 = float(np.sum(np.abs(out)))
        if src_l1 > EPS and out_l1 > EPS:
            out *= src_l1 / out_l1
    return out


def load_backbones(sample: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    e365_path = locate(pd.read_csv(E365_SELECTION).iloc[0]["selected_uploadsafe_file"])
    e368_path = locate(pd.read_csv(E368_SELECTION).iloc[0]["selected_uploadsafe_file"])
    e365 = load_sub_frame(e365_path, sample)
    e368_sel = load_sub_frame(e368_path, sample)
    e247 = load_sub_frame(e368.E247 if hasattr(e368, "E247") else OUT / e368.ANCHOR_FILE, sample)
    e323 = load_sub_frame(OUT / "submission_e323_5508f966_uploadsafe.csv", sample)
    return e365, e368_sel, e247, e323


def write_candidate(base: pd.DataFrame, logits: np.ndarray, meta: dict[str, Any], rows: list[dict[str, Any]], seen: set[str]) -> None:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    digest = short_hash(out)
    if digest in seen:
        return
    seen.add(digest)
    name = safe_id(str(meta["variant"]), 86)
    path = OUT / f"{UPLOAD_PREFIX}_{name}_{digest}.csv"
    out.to_csv(path, index=False)
    rows.append({**meta, "file": rel(path), "basename": path.name})


def build_transfer_vectors(test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = load_frames()
    state = frames["state"].copy()
    views = build_views(frames)
    train_mask = state["split"].eq("train").to_numpy()
    train = state.loc[train_mask].reset_index(drop=True)
    test_state = state.loc[~train_mask].sort_values(KEY).reset_index(drop=True)
    require_aligned(test[KEY].sort_values(KEY).reset_index(drop=True), test_state[KEY], "e370_test_state")

    gate = load_e368_gate(test_state[KEY])
    movement = movement_audit(test_state, gate)
    local, pred_store = fit_base_context_residuals(train, test_state, views, train_mask)
    _knn, knn_store = build_knn_scores(train, views, train_mask, pred_store)
    _cluster, cluster_store = build_cluster_scores(train, views, train_mask, pred_store)
    summary, _nulls = collect_alignment_rows(gate, movement, local, pred_store, knn_store, cluster_store)
    summary.to_csv(TRANSFER_ROWS_OUT, index=False)

    def vector_for(rec: pd.Series) -> np.ndarray:
        method = str(rec["method"])
        target = str(rec["target"])
        view = str(rec["view_id"])
        split = str(rec["split"])
        if method == "masked_residual_student_test":
            return np.asarray(pred_store[(target, view, split)]["test_score"], dtype=np.float64)
        m = re.match(r"knn(\d+)_train_residual", method)
        if m:
            return np.asarray(knn_store[(target, view, split, int(m.group(1)))], dtype=np.float64)
        m = re.match(r"kmeans(\d+)_train_residual", method)
        if m:
            return np.asarray(cluster_store[(target, view, split, int(m.group(1)))], dtype=np.float64)
        raise ValueError(method)

    out = test_state[KEY].copy()
    for target in ["Q2", "S1"]:
        sub = summary[summary["target"].astype(str).eq(target) & summary["any_transfer_support"].fillna(False).astype(bool)].copy()
        sub["strength"] = sub[["gate_spearman", "abs_delta_spearman", "signed_delta_spearman"]].abs().max(axis=1)
        sub = sub.sort_values(["abs_delta_support", "gate_support", "strength"], ascending=[False, False, False]).head(18)
        pieces = []
        meta_rows = []
        for _, rec in sub.iterrows():
            vec = vector_for(rec)
            orient_source = rec["abs_delta_spearman"] if bool(rec.get("abs_delta_support", False)) else rec["gate_spearman"]
            orient = 1.0 if float(orient_source) >= 0.0 else -1.0
            pieces.append(z01(orient * vec))
            meta_rows.append(
                {
                    "target": target,
                    "view_id": rec["view_id"],
                    "split": rec["split"],
                    "method": rec["method"],
                    "strength": float(rec["strength"]),
                    "orientation": orient,
                }
            )
        if pieces:
            score = rank01(np.mean(np.vstack(pieces), axis=0))
        else:
            score = np.zeros(len(test_state), dtype=np.float64)
        out[f"{target.lower()}_publicfree_transfer_score"] = score
        out[f"{target.lower()}_publicfree_transfer_top20"] = score >= np.quantile(score, 0.80)
    return out, pd.DataFrame(meta_rows if "meta_rows" in locals() else [])


def generate_candidates(sample: pd.DataFrame, transfer: pd.DataFrame) -> pd.DataFrame:
    e365, e368_sel, e247, e323 = load_backbones(sample)
    l365 = logit(e365[TARGETS].to_numpy(dtype=np.float64))
    l368 = logit(e368_sel[TARGETS].to_numpy(dtype=np.float64))
    l247 = logit(e247[TARGETS].to_numpy(dtype=np.float64))
    l323 = logit(e323[TARGETS].to_numpy(dtype=np.float64))
    base_delta = l368 - l365
    bad365 = l323 - l365
    bad247 = l323 - l247
    q2_idx = TARGETS.index("Q2")
    s1_idx = TARGETS.index("S1")

    q2_scales = [0.00, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00]
    s1_scales = [0.70, 0.85, 1.00, 1.06, 1.15]
    orth_alphas = [0.0, 0.25, 0.50, 0.75, 1.00]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for q2_scale in q2_scales:
        for s1_scale in s1_scales:
            for alpha in orth_alphas:
                for renorm in ([False, True] if alpha > 0 else [False]):
                    delta = np.zeros_like(base_delta)
                    q2_delta = q2_scale * base_delta[:, q2_idx]
                    if alpha > 0 and q2_scale > 0:
                        q2_delta = project_away(q2_delta, bad365[:, q2_idx], alpha=alpha, renorm=renorm)
                    delta[:, q2_idx] = q2_delta
                    delta[:, s1_idx] = s1_scale * base_delta[:, s1_idx]
                    if float(np.sum(np.abs(delta))) <= EPS:
                        continue
                    q2_token = str(q2_scale).replace(".", "p")
                    s1_token = str(s1_scale).replace(".", "p")
                    alpha_token = str(alpha).replace(".", "p")
                    variant = f"e370_q2{q2_token}_s1{s1_token}_orth{alpha_token}_{'renorm' if renorm else 'plain'}"
                    logits = l365 + delta
                    meta = {
                        "variant": variant,
                        "family": "q2s1_risk_constrained_recalibration",
                        "q2_scale": q2_scale,
                        "s1_scale": s1_scale,
                        "q2_orth_alpha": alpha,
                        "q2_orth_renorm": bool(renorm),
                        "q2_l1": float(np.sum(np.abs(delta[:, q2_idx]))),
                        "s1_l1": float(np.sum(np.abs(delta[:, s1_idx]))),
                        "all_l1": float(np.sum(np.abs(delta))),
                        "all_cos_e323_bad_vs_e365": cos(delta, bad365),
                        "all_cos_e323_bad_vs_e247": cos(delta, bad247),
                        "q2_cos_e323_bad_vs_e365": cos(delta[:, q2_idx], bad365[:, q2_idx]) if np.linalg.norm(delta[:, q2_idx]) > EPS else 0.0,
                        "q2_cos_e323_bad_vs_e247": cos(delta[:, q2_idx], bad247[:, q2_idx]) if np.linalg.norm(delta[:, q2_idx]) > EPS else 0.0,
                        "s1_cos_e323_bad_vs_e365": cos(delta[:, s1_idx], bad365[:, s1_idx]) if np.linalg.norm(delta[:, s1_idx]) > EPS else 0.0,
                        "q2_transfer_abs_spearman": safe_spearman(np.abs(delta[:, q2_idx]), transfer["q2_publicfree_transfer_score"].to_numpy(dtype=np.float64)),
                        "s1_transfer_abs_spearman": safe_spearman(np.abs(delta[:, s1_idx]), transfer["s1_publicfree_transfer_score"].to_numpy(dtype=np.float64)),
                        "q2_transfer_signed_spearman": safe_spearman(delta[:, q2_idx], transfer["q2_publicfree_transfer_score"].to_numpy(dtype=np.float64)),
                        "s1_transfer_signed_spearman": safe_spearman(delta[:, s1_idx], transfer["s1_publicfree_transfer_score"].to_numpy(dtype=np.float64)),
                    }
                    write_candidate(e365, logits, meta, rows, seen)
    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def score_candidates(candidates: pd.DataFrame, rowmask: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    selector = selector_scores(candidates, anchor)
    rowstate = rowstate_public_scores(selector, anchor, anchor_logit, state, base_cols, story_cols)
    e363_scored = add_e363_scores(rowstate)

    # Reuse the E368 public/view jackknife machinery, but redirect its outputs
    # so E368 artifacts remain immutable.
    e368.KNOWN_OUT = OUT / "e370_q2s1_risk_constrained_known.csv"
    e368.SCORES_OUT = SCORES_OUT
    e368.SCENARIOS_OUT = SCENARIOS_OUT
    e368.RANKS_OUT = RANKS_OUT
    e368.SUPPORT_OUT = SUPPORT_OUT
    combined, known_scored, _ = e368.public_score_candidates(e363_scored, rowmask)
    combined["candidate_origin"] = combined["candidate_origin"].replace({"e368_generated": "e370_generated"})
    feature_sets = e368.available_feature_sets(known_scored, combined)
    e365_variant = str(pd.read_csv(E365_SELECTION).iloc[0]["variant"])
    scenarios, ranks = e368.run_scenarios(known_scored, combined, feature_sets, e365_variant)
    ranks["candidate_origin"] = ranks["candidate_origin"].replace({"e368_generated": "e370_generated"})
    support = e368.aggregate_support(ranks, len(scenarios))
    support["candidate_origin"] = support["candidate_origin"].replace({"e368_generated": "e370_generated"})
    combined.to_csv(SCORES_OUT, index=False)
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    ranks.to_csv(RANKS_OUT, index=False)
    support.to_csv(SUPPORT_OUT, index=False)
    return combined, scenarios, support


def select_candidate(candidates: pd.DataFrame, combined: pd.DataFrame, support: pd.DataFrame) -> pd.DataFrame:
    current = str(pd.read_csv(E368_SELECTION).iloc[0]["variant"])
    e365_variant = str(pd.read_csv(E365_SELECTION).iloc[0]["variant"])
    work = combined.merge(
        support[["variant", "top1_rate", "top5_rate", "top10_rate", "rank_mean", "score_mean"]],
        on="variant",
        how="left",
    )
    meta_cols = [
        "q2_scale",
        "s1_scale",
        "q2_orth_alpha",
        "q2_orth_renorm",
        "all_cos_e323_bad_vs_e365",
        "q2_cos_e323_bad_vs_e365",
        "q2_cos_e323_bad_vs_e247",
        "s1_cos_e323_bad_vs_e365",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "q2_transfer_signed_spearman",
        "s1_transfer_signed_spearman",
    ]
    missing_meta = [c for c in meta_cols if c not in work.columns]
    if missing_meta:
        work = work.merge(candidates[["variant"] + missing_meta], on="variant", how="left")
    generated = work[work["candidate_origin"].astype(str).eq("e370_generated")].copy()
    current_row = generated[
        generated["q2_scale"].round(6).eq(1.0)
        & generated["s1_scale"].round(6).eq(1.0)
        & generated["q2_orth_alpha"].round(6).eq(0.0)
    ].head(1)
    if current_row.empty:
        current_row = generated.sort_values("e368_public_like_score", ascending=False).head(1)
    cur = current_row.iloc[0]

    for col in ["top1_rate", "top5_rate", "top10_rate", "rank_mean", "e368_public_like_score"]:
        generated[col] = pd.to_numeric(generated[col], errors="coerce").fillna(0.0)
    generated["e370_transfer_score"] = (
        0.60 * rank01(generated["q2_transfer_abs_spearman"].fillna(0.0))
        + 0.50 * rank01(generated["s1_transfer_abs_spearman"].fillna(0.0))
        + 0.25 * rank01(generated["q2_transfer_signed_spearman"].fillna(0.0))
        + 0.25 * rank01(generated["s1_transfer_signed_spearman"].fillna(0.0))
    )
    generated["e370_safety_score"] = (
        0.95 * rank01(-generated["all_cos_e323_bad_vs_e365"].fillna(0.0).abs())
        + 1.15 * rank01(-generated["q2_cos_e323_bad_vs_e365"].fillna(0.0).clip(lower=0.0))
        + 0.55 * rank01(-generated["public_bad_axis_sum"].fillna(0.0))
        + 0.45 * rank01(-generated["rowstate_pred_public_loss_mean"].fillna(0.0))
        + 0.35 * rank01(-generated["rowstate_bad_minus_good_exposure"].fillna(0.0))
    )
    generated["e370_scenario_score"] = (
        0.85 * generated["top1_rate"]
        + 0.55 * generated["top5_rate"]
        + 0.35 * generated["top10_rate"]
        + 0.30 * rank01(generated["e368_public_like_score"].fillna(0.0))
    )
    generated["e370_total_score"] = (
        generated["e370_scenario_score"]
        + 0.75 * generated["e370_safety_score"]
        + 0.55 * generated["e370_transfer_score"]
    )

    cur_q2_bad = float(cur.get("q2_cos_e323_bad_vs_e365", np.inf))
    cur_top10 = float(cur.get("top10_rate", 0.0))
    cur_top1 = float(cur.get("top1_rate", 0.0))
    cur_pls = float(cur.get("e368_public_like_score", 0.0))
    eligible = generated[
        generated["e363_submission_gate"].fillna(False).astype(bool)
        & (generated["top10_rate"] >= max(0.60, cur_top10 - 0.12))
        & (generated["top1_rate"] >= max(0.10, cur_top1 - 0.20))
        & (generated["e368_public_like_score"] >= cur_pls - 0.12)
        & (generated["q2_cos_e323_bad_vs_e365"] <= cur_q2_bad - 0.12)
        & (generated["all_cos_e323_bad_vs_e365"].abs() <= 0.05)
        & (generated["q2_transfer_abs_spearman"] >= 0.0)
        & (generated["s1_transfer_abs_spearman"] >= -0.05)
    ].copy()
    if len(eligible):
        chosen = eligible.sort_values("e370_total_score", ascending=False).head(1).copy()
        decision = "select_e370_q2s1_risk_constrained_replacement"
        reason = "A Q2/S1 recalibration reduces Q2 E323-axis exposure while preserving E368 scenario support and public-free transfer alignment."
        src = locate(chosen.iloc[0]["file"])
        for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
            stale.unlink()
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(chosen.iloc[0]['variant']), 70)}_{short_hash(pd.read_csv(src))}_uploadsafe.csv"
        shutil.copyfile(src, upload)
    else:
        chosen = current_row.copy()
        decision = "keep_e368_no_safer_e370_replacement"
        reason = "No Q2/S1 recalibration reduced the Q2 bad-axis warning enough without losing E368 stress support or transfer alignment."
        upload = locate(pd.read_csv(E368_SELECTION).iloc[0]["selected_uploadsafe_file"])

    chosen["decision"] = decision
    chosen["reason"] = reason
    chosen["current_e368_variant"] = current
    chosen["e365_variant"] = e365_variant
    chosen["current_q2_bad_cos"] = cur_q2_bad
    chosen["current_top1_rate"] = cur_top1
    chosen["current_top10_rate"] = cur_top10
    chosen["eligible_count"] = int(len(eligible))
    chosen["selected_uploadsafe_file"] = rel(upload)
    chosen.to_csv(SELECTION_OUT, index=False)
    generated.sort_values("e370_total_score", ascending=False).to_csv(DECISION_OUT, index=False)
    return chosen


def write_report(candidates: pd.DataFrame, combined: pd.DataFrame, support: pd.DataFrame, selected: pd.DataFrame) -> None:
    generated = pd.read_csv(DECISION_OUT)
    selection_cols = [
        "decision",
        "variant",
        "eligible_count",
        "selected_uploadsafe_file",
        "reason",
        "q2_scale",
        "s1_scale",
        "q2_orth_alpha",
        "q2_orth_renorm",
        "top1_rate",
        "top10_rate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e365",
        "all_cos_e323_bad_vs_e365",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
    ]
    lines = [
        "# E370 Q2/S1 Risk-Constrained Recalibration",
        "",
        "## Question",
        "",
        "Can E368's validated Q2/S1 lifestyle-state movement be made safer by reducing Q2-only E323-axis exposure without losing stress support?",
        "",
        "## Construction",
        "",
        "- Backbone: E365.",
        "- Delta source: E368 selected Q2/S1-only movement.",
        "- Search: Q2 scale, S1 scale, and optional Q2 projection away from E323-vs-E365 bad axis.",
        "- Stress: E363/E364/E365/E368 public-like scenario support, E369 public-free transfer alignment, E323-axis movement audit.",
        "",
        "## Selection",
        "",
        md_table(selected[[c for c in selection_cols if c in selected.columns]], n=5, floatfmt=".9f"),
        "",
        "## Top E370 Candidates",
        "",
    ]
    cols = [
        "variant",
        "q2_scale",
        "s1_scale",
        "q2_orth_alpha",
        "q2_orth_renorm",
        "top1_rate",
        "top10_rate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e365",
        "all_cos_e323_bad_vs_e365",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "e370_total_score",
        "file",
    ]
    lines.append(md_table(generated[[c for c in cols if c in generated.columns]].head(30), n=30, floatfmt=".9f"))
    lines.extend(
        [
            "",
            "## Scenario Support",
            "",
            md_table(support.head(30), n=30, floatfmt=".9f"),
            "",
            "## Interpretation",
            "",
        ]
    )
    decision = str(selected["decision"].iloc[0])
    if decision.startswith("select_"):
        lines.append(
            "A safer E370 candidate exists under the local stress. Treat it as a candidate only if the user wants a lower-risk E368 derivative; it is not a broad new model."
        )
    else:
        lines.append(
            "No safer Q2/S1 recalibration beat E368 under the combined support constraints. The useful conclusion is conservative: keep E368 and do not amplify Q2 until a stronger Q2 bad-axis neutralizer exists."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{TRANSFER_ROWS_OUT.name}`",
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
    sample = anchor[KEY].copy()
    transfer, _meta = build_transfer_vectors(anchor)
    candidates = generate_candidates(sample, transfer)
    rowmask = normalize_dates(pd.read_csv(e368.ROWMASK_OUT)).sort_values(KEY).reset_index(drop=True)
    combined, scenarios, support = score_candidates(candidates, rowmask)
    selected = select_candidate(candidates, combined, support)
    write_report(candidates, combined, support, selected)
    print(f"generated_candidates={len(candidates)} scenarios={len(scenarios)}")
    print(selected[["decision", "variant", "eligible_count", "selected_uploadsafe_file", "reason"]].to_string(index=False))
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
