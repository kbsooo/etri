#!/usr/bin/env python3
"""E336: public-negative action latent audit.

E335 found a learnable Q1 action-health latent, but its generator collapsed
into safe-invisible movements.  This experiment asks a different question:

    Can resolved public-bad movement anatomy be used as a same-level latent
    target, so that E247 is preserved while E323/E216-style movement is
    explicitly suppressed?

This is not a public-LB optimizer.  Public feedback is used only as a resolved
negative/positive sensor:

    context = E247-relative movement + lifestyle/action signatures
    target  = public-surviving vs public-adverse movement anatomy

Generated probes are scored only by local selector, E323/E216 anatomy, and
matched movement-null stress.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e336_public_negative_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e335_q1_action_health_latent_generator import entropy_from_groups, test_meta_aligned, weighted_stats  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 336
EPS = 1.0e-12
CAP = 0.35
NULL_REPS = 4
TOP_NULL_CANDIDATES = 12

E247 = OUT / CURRENT
E323 = OUT / "submission_e323_5508f966_uploadsafe.csv"
E216 = OUT / "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv"
E95 = OUT / "submission_e95_hardtail_541e3973.csv"
MIXMIN = OUT / "submission_mixmin_0c916bb4.csv"
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E267 = OUT / "submission_e267_humansocial_tail_balanced_2936100f.csv"
E101 = OUT / "submission_e101_q2s3tail_177569bc.csv"
E176 = OUT / "submission_e176_abl_q2_to0p75_91e49725.csv"
E72 = OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"

AXIS_OUT = OUT / "e336_public_negative_axis_signatures.csv"
CANDIDATE_OUT = OUT / "e336_public_negative_candidates.csv"
SCORE_OUT = OUT / "e336_public_negative_scores.csv"
ANATOMY_OUT = OUT / "e336_public_negative_anatomy.csv"
SIGNATURE_OUT = OUT / "e336_public_negative_candidate_signatures.csv"
NULL_OUT = OUT / "e336_public_negative_nulls.csv"
REPORT_OUT = OUT / "e336_public_negative_report.md"

PUBLIC_LB = {
    CURRENT: 0.5761589494,
    E256.name: 0.5762805676,
    E95.name: 0.5762913298,
    E101.name: 0.5763003660,
    MIXMIN.name: 0.5763066405,
    E176.name: 0.5763118310,
    E267.name: 0.5763294974,
    E72.name: 0.5764077772,
    E323.name: 0.5770355016,
    E216.name: 0.5772865088,
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def load_frame(path: Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return load_sub(path, sample).sort_values(KEYS).reset_index(drop=True)


def logits(path: Path, sample: pd.DataFrame) -> np.ndarray:
    return logit(load_frame(path, sample)[TARGETS].to_numpy(dtype=np.float64))


def clip_delta(delta: np.ndarray, cap: float = CAP) -> np.ndarray:
    return np.clip(np.asarray(delta, dtype=np.float64), -cap, cap)


def topk_mask(direction: np.ndarray, k: int | str) -> np.ndarray:
    flat = np.abs(direction).reshape(-1)
    mask = np.zeros_like(flat, dtype=bool)
    if k == "all" or int(k) >= len(flat):
        mask[:] = flat > EPS
    else:
        kk = max(1, int(k))
        idx = np.argsort(-flat)[:kk]
        mask[idx] = flat[idx] > EPS
    return mask.reshape(direction.shape)


def projection_coeff(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1)
    bb = b.reshape(-1)
    denom = float(bb @ bb)
    if denom <= EPS:
        return 0.0
    return float((aa @ bb) / denom)


def remove_bad_projection(direction: np.ndarray, bad_axes: list[np.ndarray]) -> np.ndarray:
    out = np.asarray(direction, dtype=np.float64).copy()
    for bad in bad_axes:
        out = out - projection_coeff(out, bad) * bad
    return out


def save_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = expit(np.clip(base_logit + clip_delta(delta), -40.0, 40.0))
    path = OUT / f"submission_e336_{safe_id(candidate_id, 110)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def target_abs(delta: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    total = float(np.sum(np.abs(delta))) + EPS
    for i, target in enumerate(TARGETS):
        val = float(np.sum(np.abs(delta[:, i])))
        out[f"abs_{target}"] = val
        out[f"share_{target}"] = val / total
    return out


def cos(a: np.ndarray, b: np.ndarray) -> float:
    aa = a.reshape(-1)
    bb = b.reshape(-1)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb) + EPS)
    return float((aa @ bb) / denom)


def axis_signature_rows(base: pd.DataFrame, base_logit: np.ndarray, axes: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for name, delta in axes.items():
        flat = delta.reshape(-1)
        rec: dict[str, Any] = {
            "axis": name,
            "changed_cells": int((np.abs(flat) > EPS).sum()),
            "changed_rows": int((np.max(np.abs(delta), axis=1) > EPS).sum()),
            "l1": float(np.sum(np.abs(flat))),
            "mean_abs": float(np.mean(np.abs(flat))),
            "max_abs": float(np.max(np.abs(flat))),
            "signed_sum": float(np.sum(flat)),
            **target_abs(delta),
        }
        for other, other_delta in axes.items():
            if other != name:
                rec[f"cos_with_{other}"] = cos(delta, other_delta)
        rows.append(rec)
    out = pd.DataFrame(rows)
    out.to_csv(AXIS_OUT, index=False)
    return out


def make_axes(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, dict[str, np.ndarray]]:
    base = load_frame(E247)
    base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    frames = {
        "e323_bad": logits(E323, sample) - base_logit,
        "e216_bad": logits(E216, sample) - base_logit,
        "e247_minus_e95": base_logit - logits(E95, sample),
        "e247_minus_mixmin": base_logit - logits(MIXMIN, sample),
        "e247_minus_e256": base_logit - logits(E256, sample),
        "e247_minus_e267": base_logit - logits(E267, sample),
        "e247_minus_mildavg": base_logit
        - np.mean([logits(p, sample) for p in [E95, MIXMIN, E256, E267, E101, E176, E72]], axis=0),
    }
    frames["bad_combo"] = 0.55 * frames["e323_bad"] + 0.45 * frames["e216_bad"]
    frames["away_e323"] = -frames["e323_bad"]
    frames["away_e216"] = -frames["e216_bad"]
    frames["away_bad_combo"] = -frames["bad_combo"]
    frames["good_mild_orth_bad"] = remove_bad_projection(frames["e247_minus_mildavg"], [frames["e323_bad"], frames["e216_bad"]])
    frames["good_e95_orth_bad"] = remove_bad_projection(frames["e247_minus_e95"], [frames["e323_bad"], frames["e216_bad"]])
    axis_signature_rows(base, base_logit, frames)
    return base, base_logit, frames


def generate_candidates() -> tuple[pd.DataFrame, list[Path], pd.DataFrame, np.ndarray, dict[str, np.ndarray]]:
    sample = load_sub(E247)[KEYS]
    base, base_logit, axes = make_axes(sample)
    specs: list[tuple[str, np.ndarray, list[int | str], list[float]]] = [
        ("away_e323", axes["away_e323"], [20, 34, 50, 80, 120], [0.05, 0.10, 0.16, 0.24]),
        ("away_e216", axes["away_e216"], [20, 34, 50, 80, 120], [0.03, 0.06, 0.10, 0.16]),
        ("away_bad_combo", axes["away_bad_combo"], [20, 34, 50, 80, 120], [0.03, 0.06, 0.10, 0.16]),
        ("good_mild", axes["e247_minus_mildavg"], [20, 34, 50, 80, 120, "all"], [0.05, 0.10, 0.16, 0.24]),
        ("good_e95", axes["e247_minus_e95"], [20, 34, 50, 80, 120, "all"], [0.05, 0.10, 0.16, 0.24]),
        ("good_mixmin", axes["e247_minus_mixmin"], [20, 34, 50, 80, 120, "all"], [0.04, 0.08, 0.14, 0.20]),
        ("good_mild_orth_bad", axes["good_mild_orth_bad"], [20, 34, 50, 80, 120], [0.06, 0.12, 0.20]),
        ("good_e95_orth_bad", axes["good_e95_orth_bad"], [20, 34, 50, 80, 120], [0.06, 0.12, 0.20]),
    ]
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for family, direction, topks, scales in specs:
        for topk in topks:
            mask = topk_mask(direction, topk)
            if int(mask.sum()) == 0:
                continue
            for scale in scales:
                delta = np.zeros_like(direction)
                delta[mask] = direction[mask] * float(scale)
                candidate_id = f"{family}_top{topk}_s{scale:.2f}"
                path = save_candidate(base, base_logit, delta, candidate_id)
                paths.append(path)
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "file": rel(path),
                        "basename": path.name,
                        "family": family,
                        "topk": str(topk),
                        "scale": float(scale),
                        "changed_cells": int((np.abs(delta) > EPS).sum()),
                        "changed_rows": int((np.max(np.abs(delta), axis=1) > EPS).sum()),
                        "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                        "max_abs_logit_delta": float(np.max(np.abs(delta))),
                        "l1_logit_delta": float(np.sum(np.abs(delta))),
                        "cos_with_e323_bad": cos(delta, axes["e323_bad"]),
                        "cos_with_e216_bad": cos(delta, axes["e216_bad"]),
                        "cos_with_good_mild": cos(delta, axes["e247_minus_mildavg"]),
                        **target_abs(delta),
                    }
                )
    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out, paths, base, base_logit, axes


def score_paths(paths: list[Path]) -> pd.DataFrame:
    sample = load_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    candidates = build_features([CURRENT] + [rel(path) for path in paths], sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def anatomy(paths: list[Path], base_logit: np.ndarray, axes: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_frame(path, load_sub(E247)[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rec: dict[str, Any] = {
            "basename": path.name,
            "changed_cells": int((np.abs(delta) > EPS).sum()),
            "changed_rows": int((np.max(np.abs(delta), axis=1) > EPS).sum()),
            "l1_logit_delta": float(np.sum(np.abs(delta))),
            "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
            "max_abs_logit_delta": float(np.max(np.abs(delta))),
            "cos_with_e323_bad": cos(delta, axes["e323_bad"]),
            "cos_with_e216_bad": cos(delta, axes["e216_bad"]),
            "cos_with_bad_combo": cos(delta, axes["bad_combo"]),
            "cos_with_good_mild": cos(delta, axes["e247_minus_mildavg"]),
            "cos_with_good_e95": cos(delta, axes["e247_minus_e95"]),
            "cos_with_good_mixmin": cos(delta, axes["e247_minus_mixmin"]),
            **target_abs(delta),
        }
        rows.append(rec)
    out = pd.DataFrame(rows).sort_values(["cos_with_bad_combo", "l1_logit_delta"], ascending=[True, True])
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def candidate_signatures(candidates: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    current = load_frame(E247)
    test = test_meta_aligned(current)
    numeric_cols = [
        c
        for c in [
            "weekday",
            "is_weekend",
            "lifelog_dom",
            "lifelog_month",
            "social_comm_energy",
            "cognitive_money_energy",
            "media_game_energy",
            "bedtime_phone_energy",
            "mobility_context_energy",
            "physiology_activity_energy",
            "routine_calendar_energy",
            "sensor_measurement_energy",
            "diary_state_energy",
            "diary_state_pc1",
            "diary_state_pc2",
            "diary_state_pc3",
            "diary_state_pc4",
            "diary_state_pc5",
            "jepa_resid_dateblock_social_comm",
            "jepa_resid_dateblock_cognitive_money",
            "jepa_resid_dateblock_media_game",
            "jepa_resid_dateblock_bedtime_phone",
            "jepa_resid_dateblock_mobility_context",
            "jepa_resid_dateblock_physiology_activity",
            "jepa_resid_dateblock_routine_calendar",
            "jepa_resid_dateblock_sensor_measurement",
        ]
        if c in test.columns and pd.api.types.is_numeric_dtype(test[c])
    ]
    rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = Path(str(rec["file"]))
        if not path.is_absolute():
            path = ROOT / path
        cand = load_frame(path, current[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        row_energy = np.sum(np.abs(delta), axis=1)
        changed = row_energy > EPS
        item: dict[str, Any] = {
            "basename": rec["basename"],
            "sig_abs_sum": float(row_energy.sum()),
            "sig_changed_rows": int(changed.sum()),
            "sig_subject_entropy": entropy_from_groups(test["subject_id"], row_energy),
            "sig_dateblock_entropy": entropy_from_groups(test["dateblock_group"], row_energy),
        }
        for col in numeric_cols:
            mean, std = weighted_stats(pd.to_numeric(test[col], errors="coerce").to_numpy(dtype=np.float64), row_energy)
            item[f"sig_{col}_wmean"] = mean
            item[f"sig_{col}_wstd"] = std
        rows.append(item)
    out = pd.DataFrame(rows)
    out.to_csv(SIGNATURE_OUT, index=False)
    return out


def make_null_delta(delta: np.ndarray, mode: str, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.asarray(delta, dtype=np.float64).copy()
    if mode == "row_perm":
        return out[rng.permutation(out.shape[0]), :]
    if mode == "target_perm":
        return out[:, rng.permutation(out.shape[1])]
    if mode == "sign_flip":
        return -out
    if mode == "row_sign":
        signs = rng.choice([-1.0, 1.0], size=(out.shape[0], 1))
        return out * signs
    if mode == "cell_perm":
        flat = out.reshape(-1).copy()
        rng.shuffle(flat)
        return flat.reshape(out.shape)
    raise ValueError(mode)


def movement_null_stress(
    scores: pd.DataFrame,
    candidates: pd.DataFrame,
    base: pd.DataFrame,
    base_logit: np.ndarray,
) -> pd.DataFrame:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    if non_current.empty:
        pd.DataFrame().to_csv(NULL_OUT, index=False)
        return pd.DataFrame()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    chosen = joined.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(TOP_NULL_CANDIDATES)

    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for rec in chosen.to_dict("records"):
        path = ROOT / str(rec.get("file_meta", rec.get("file", rec.get("source_path", ""))))
        cand = load_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        for mode in ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm"]:
            for rep in range(NULL_REPS):
                nd = make_null_delta(delta, mode, stable_seed(rec["basename"], mode, rep))
                null_id = f"null_{Path(rec['basename']).stem}_{mode}_{rep}"
                npth = save_candidate(base, base_logit, nd, null_id)
                null_paths.append(npth)
                null_rows.append({"basename": rec["basename"], "null_basename": npth.name, "mode": mode, "rep": rep})

    sample = load_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(p) for p in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_features, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    null_map = pd.DataFrame(null_rows).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_current_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )

    rows: list[dict[str, Any]] = []
    for basename, part in null_map.groupby("basename"):
        act = actual[actual["basename"].eq(basename)]
        if act.empty:
            continue
        a = act.iloc[0]
        rows.append(
            {
                "basename": basename,
                "null_count": int(len(part)),
                "actual_mean": float(a["actual_mean"]),
                "actual_p90": float(a["actual_p90"]),
                "actual_beats_rate": float(a["actual_beats_current_rate"]),
                "actual_strict_promote": bool(a["actual_strict_promote"]),
                "null_mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "null_mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "null_p90_best": float(part["pred_delta_vs_current_p90"].min()),
                "null_p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "actual_mean_dominance": float(np.mean(float(a["actual_mean"]) < part["pred_delta_vs_current_mean"].to_numpy(dtype=float))),
                "actual_p90_dominance": float(np.mean(float(a["actual_p90"]) < part["pred_delta_vs_current_p90"].to_numpy(dtype=float))),
                "null_strict_promote_rate": float(part["strict_promote_gate"].astype(bool).mean()),
            }
        )
    out = pd.DataFrame(rows).sort_values(["actual_strict_promote", "actual_p90_dominance", "actual_p90"], ascending=[False, False, True])
    out.to_csv(NULL_OUT, index=False)
    return out


def write_report(
    axis_df: pd.DataFrame,
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anat: pd.DataFrame,
    signatures: pd.DataFrame,
    nulls: pd.DataFrame,
) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    scored = non_current.merge(candidates, on="basename", how="left") if len(non_current) else pd.DataFrame()
    scored = scored.merge(anat, on="basename", how="left", suffixes=("", "_anat")) if len(scored) and len(anat) else scored
    promoted = scored[scored["strict_promote_gate"].astype(bool)] if len(scored) else pd.DataFrame()
    bad_safe = promoted[(promoted["cos_with_e323_bad"] <= 0.05) & (promoted["cos_with_e216_bad"] <= 0.05)] if len(promoted) else pd.DataFrame()
    null_safe = pd.DataFrame()
    if len(bad_safe) and len(nulls):
        null_safe = bad_safe.merge(nulls, on="basename", how="inner")
        null_safe = null_safe[
            (null_safe["actual_p90_dominance"] >= 0.80)
            & (null_safe["actual_mean_dominance"] >= 0.65)
            & (null_safe["null_strict_promote_rate"] <= 0.10)
        ]

    lines = [
        "# E336 Public-Negative Action Latent",
        "",
        "## Question",
        "",
        "Can resolved public-bad anatomy be used as a same-level action latent, preserving E247 while suppressing E323/E216-like movement?",
        "",
        "## Axis Signatures",
        "",
        md_table(axis_df.sort_values("l1", ascending=False), n=24, floatfmt=".6f"),
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{int(non_current['strict_promote_gate'].sum()) if len(non_current) else 0}`",
        f"- selector+public-bad-safe candidates: `{len(bad_safe)}`",
        f"- selector+public-bad+null-safe candidates: `{len(null_safe)}`",
        "",
        md_table(candidates.sort_values(["family", "topk", "scale"]), n=36, floatfmt=".6f"),
        "",
        "## Public-Free Selector Scores",
        "",
    ]
    if len(scored):
        score_cols = [
            "basename",
            "family",
            "topk",
            "scale",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
            "cos_with_e323_bad",
            "cos_with_e216_bad",
            "cos_with_good_mild",
        ]
        lines.append(md_table(scored[score_cols], n=60, floatfmt=".9f"))
    else:
        lines.append("_no scores_")
    lines.extend(["", "## Movement Anatomy", "", md_table(anat, n=50, floatfmt=".9f") if len(anat) else "_none_"])
    sig_cols = [c for c in signatures.columns if c in {"basename", "sig_abs_sum", "sig_changed_rows", "sig_subject_entropy", "sig_dateblock_entropy", "sig_bedtime_phone_energy_wmean", "sig_mobility_context_energy_wmean", "sig_cognitive_money_energy_wmean", "sig_diary_state_energy_wmean"}]
    lines.extend(["", "## Lifestyle Signatures", "", md_table(signatures[sig_cols], n=40, floatfmt=".6f") if len(sig_cols) else "_none_"])
    lines.extend(["", "## Movement-Null Stress", "", md_table(nulls, n=30, floatfmt=".9f") if len(nulls) else "_none_"])
    lines.extend(["", "## Decision", ""])
    if len(null_safe):
        best = null_safe.sort_values(["actual_p90", "actual_mean"]).iloc[0]
        lines.append(f"`{best['basename']}` clears selector, public-bad anatomy, and movement-null gates. It is the next candidate for manual review.")
    else:
        lines.append(
            "No E336 candidate clears selector + public-bad anatomy + movement-null gates. This rejects the simple output-space fix: moving opposite E323/E216 or extrapolating E247-vs-old-frontier directions does not currently create a public-grade hidden lifestyle action."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{AXIS_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{SIGNATURE_OUT.name}`",
            f"- `{NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    candidates, paths, base, base_logit, axes = generate_candidates()
    scores = score_paths(paths)
    anat = anatomy(paths, base_logit, axes)
    signatures = candidate_signatures(candidates, base_logit)
    nulls = movement_null_stress(scores, candidates, base, base_logit)
    axis_df = pd.read_csv(AXIS_OUT)
    write_report(axis_df, candidates, scores, anat, signatures, nulls)
    print(REPORT_OUT)
    if len(scores):
        view = scores[~scores["basename"].eq(CURRENT)]
        print(
            view[
                [
                    "basename",
                    "promotion_decision",
                    "pred_delta_vs_current_mean",
                    "pred_delta_vs_current_p90",
                    "pred_beats_current_rate",
                ]
            ]
            .head(40)
            .round(9)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
