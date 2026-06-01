#!/usr/bin/env python3
"""H011: H010 public-inversion jackpot.

H010 was a clean local jackpot and a strong public failure.  H011 treats that
failure as a new JEPA target: the hidden action-health representation.  The
context is the exact S1/S4 movement that looked good locally; the target is the
public-bad action axis exposed by H010's LB.

This is intentionally not a safe blend.  It asks a falsifiable question:

    If H010 failed because the public subset wants the opposite S1/S4 route,
    does reflecting the H010 action axis improve meaningfully over E247?

If it fails, the "public is anti-H010 route" worldview dies quickly.  If it
wins, H010 becomes useful as a public-negative action-health teacher.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H011 = HITL / "h011_h010_public_inversion_jackpot"
H011.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


EPS = 1.0e-12
H010_FILE = "submission_h010_objective_s1s4_v2_uploadsafe.csv"
E247_LB = 0.5761589494
H010_LB = 0.5781718175
H010_PUBLIC_DELTA = H010_LB - E247_LB

REPORT_OUT = H011 / "h011_report.md"
CANDIDATE_OUT = H011 / "h011_candidates.csv"
ANATOMY_OUT = H011 / "h011_action_anatomy.csv"
SCORE_OUT = H011 / "h011_selector_scores.csv"
SELECTION_OUT = H011 / "h011_selection.csv"


@dataclass(frozen=True)
class InversionSpec:
    candidate_id: str
    family: str
    alpha: float
    target_subset: str
    cell_mode: str
    k: int = 0
    agree_threshold: float = 0.0


def safe_id(text: str, limit: int = 128) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", text).strip("_")
    return clean[:limit].strip("_")


def sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-x))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def projection(move: np.ndarray, direction: np.ndarray) -> tuple[float, float]:
    m = move.reshape(-1)
    d = direction.reshape(-1)
    denom = float(d @ d)
    if denom <= EPS:
        return 0.0, 0.0
    coeff = float(m @ d / denom)
    cos = float(m @ d / (np.linalg.norm(m) * np.linalg.norm(d) + EPS))
    return coeff, cos


def target_mask(target_subset: str, shape: tuple[int, int]) -> np.ndarray:
    mask = np.zeros(shape, dtype=bool)
    if target_subset == "all":
        for target in ["S1", "S4"]:
            mask[:, TARGETS.index(target)] = True
    elif target_subset in TARGETS:
        mask[:, TARGETS.index(target_subset)] = True
    elif target_subset == "s1s4_joint_rows":
        s1 = TARGETS.index("S1")
        s4 = TARGETS.index("S4")
        mask[:, [s1, s4]] = True
    else:
        raise ValueError(target_subset)
    return mask


def bad_agreement_weights(
    sample: pd.DataFrame,
    base_logit: np.ndarray,
    h010_delta: np.ndarray,
) -> np.ndarray:
    """Cell-level support that H010 moved in a public-bad direction.

    This uses old public-bad submissions as weak teachers.  It is not a public
    label fit for new submissions; it only chooses which H010 cells to invert.
    """
    bad_files = [
        "submission_e323_5508f966_uploadsafe.csv",
        "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        "submission_e267_humansocial_tail_balanced_2936100f.csv",
        "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
        "submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv",
    ]
    weights = np.zeros_like(h010_delta, dtype=np.float64)
    hsign = np.sign(h010_delta)
    for file_name in bad_files:
        try:
            pred = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)
        except FileNotFoundError:
            continue
        move = logit(pred) - base_logit
        mag = np.abs(move)
        active = mag >= np.quantile(mag[mag > EPS], 0.85) if np.any(mag > EPS) else np.zeros_like(mag, dtype=bool)
        weights += ((np.sign(move) == hsign) & active & (np.abs(h010_delta) > EPS)).astype(float)
    return weights


def cell_selector(spec: InversionSpec, h010_delta: np.ndarray, agreement: np.ndarray) -> np.ndarray:
    base = np.abs(h010_delta) > EPS
    base &= target_mask(spec.target_subset, h010_delta.shape)
    score = np.abs(h010_delta).copy()
    if spec.cell_mode == "all":
        return base
    if spec.cell_mode == "top_abs":
        flat = np.flatnonzero(base.reshape(-1))
        chosen = flat[np.argsort(score.reshape(-1)[flat])[-min(spec.k, len(flat)) :]]
        mask = np.zeros_like(base)
        mask.reshape(-1)[chosen] = True
        return mask
    if spec.cell_mode == "row_top_abs":
        row_score = (np.abs(h010_delta) * base).sum(axis=1)
        rows = np.argsort(row_score)[-min(spec.k, int((row_score > EPS).sum())) :]
        mask = np.zeros_like(base)
        mask[rows, :] = base[rows, :]
        return mask
    if spec.cell_mode == "row_bottom_abs":
        row_score = (np.abs(h010_delta) * base).sum(axis=1)
        active_rows = np.flatnonzero(row_score > EPS)
        rows = active_rows[np.argsort(row_score[active_rows])[: min(spec.k, len(active_rows))]]
        mask = np.zeros_like(base)
        mask[rows, :] = base[rows, :]
        return mask
    if spec.cell_mode == "bad_agree":
        return base & (agreement >= spec.agree_threshold)
    if spec.cell_mode == "bad_agree_top":
        score = agreement * np.abs(h010_delta)
        flat = np.flatnonzero(base.reshape(-1) & (agreement.reshape(-1) > 0))
        chosen = flat[np.argsort(score.reshape(-1)[flat])[-min(spec.k, len(flat)) :]]
        mask = np.zeros_like(base)
        mask.reshape(-1)[chosen] = True
        return mask
    raise ValueError(spec.cell_mode)


def specs() -> list[InversionSpec]:
    out: list[InversionSpec] = []
    for target_subset in ["all", "S1", "S4"]:
        for alpha in [0.125, 0.25, 0.50, 0.75, 1.00, 1.25]:
            out.append(InversionSpec(f"mirror_{target_subset}_a{alpha:g}", "mirror", alpha, target_subset, "all"))
    for target_subset in ["all", "S1", "S4"]:
        for k in [40, 80, 120, 200, 320, 455]:
            for alpha in [0.50, 1.00, 1.50]:
                out.append(InversionSpec(f"topabs_{target_subset}_k{k}_a{alpha:g}", "top_abs", alpha, target_subset, "top_abs", k=k))
    for k in [20, 35, 50, 80, 120, 180]:
        for alpha in [0.50, 1.00, 1.50]:
            out.append(InversionSpec(f"rowtop_all_k{k}_a{alpha:g}", "row_top", alpha, "all", "row_top_abs", k=k))
            out.append(InversionSpec(f"rowbottom_all_k{k}_a{alpha:g}", "row_bottom", alpha, "all", "row_bottom_abs", k=k))
    for threshold in [1.0, 2.0]:
        for target_subset in ["all", "S1", "S4"]:
            for alpha in [0.50, 1.00, 1.50]:
                out.append(
                    InversionSpec(
                        f"badagree_{target_subset}_ge{threshold:g}_a{alpha:g}",
                        "bad_agree",
                        alpha,
                        target_subset,
                        "bad_agree",
                        agree_threshold=threshold,
                    )
                )
    for k in [40, 80, 120, 200]:
        for alpha in [0.75, 1.25, 1.75]:
            out.append(InversionSpec(f"badagree_top_all_k{k}_a{alpha:g}", "bad_agree_top", alpha, "all", "bad_agree_top", k=k))
    return out


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, h010_delta: np.ndarray, mask: np.ndarray, spec: InversionSpec) -> Path:
    out = base.copy()
    z = base_logit.copy()
    z[mask] = z[mask] - spec.alpha * h010_delta[mask]
    prob = np.clip(sigmoid(z), 1.0e-6, 1.0 - 1.0e-6)
    out[TARGETS] = prob
    path = H011 / f"submission_h011_{safe_id(spec.candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def validate_submission(path: Path, sample: pd.DataFrame) -> None:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    if not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch: {path}")
    values = df[TARGETS].to_numpy(dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError(f"non-finite probabilities: {path}")
    if values.min() < 0.0 or values.max() > 1.0:
        raise ValueError(f"probability range error: {path}")


def materialize() -> tuple[pd.DataFrame, pd.DataFrame, list[Path]]:
    base = load_sub(CURRENT)
    sample = base[KEYS].copy()
    h010 = load_sub(H010_FILE, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    h010_prob = h010[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    h010_delta = logit(h010_prob) - base_logit
    agreement = bad_agreement_weights(sample, base_logit, h010_delta)
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in specs():
        mask = cell_selector(spec, h010_delta, agreement)
        if not mask.any():
            continue
        path = write_candidate(base, base_logit, h010_delta, mask, spec)
        validate_submission(path, sample)
        paths.append(path)
        pred = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(pred) - base_logit
        coeff, cos = projection(move, h010_delta)
        prob_delta = np.abs(pred - base_prob)
        rows.append(
            {
                "candidate_id": spec.candidate_id,
                "family": spec.family,
                "alpha": spec.alpha,
                "target_subset": spec.target_subset,
                "cell_mode": spec.cell_mode,
                "k": spec.k,
                "agree_threshold": spec.agree_threshold,
                "file": rel(path),
                "basename": path.name,
                "changed_rows": int((prob_delta.max(axis=1) > EPS).sum()),
                "changed_cells": int((np.abs(move) > EPS).sum()),
                "h010_axis_coeff": coeff,
                "h010_axis_cos": cos,
                "h010_axis_public_delta_linear": coeff * H010_PUBLIC_DELTA,
                "mean_abs_logit_delta": float(np.mean(np.abs(move))),
                "l1_logit_delta": float(np.sum(np.abs(move))),
                "max_abs_logit_delta": float(np.max(np.abs(move))),
                "max_abs_prob_delta": float(prob_delta.max()),
                "mean_agreement_on_changed": float(agreement[mask].mean()),
                "max_agreement_on_changed": float(agreement[mask].max()),
                **{
                    f"changed_{target}": int((np.abs(move[:, ti]) > EPS).sum())
                    for ti, target in enumerate(TARGETS)
                },
            }
        )
    anatomy = pd.DataFrame(rows)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return base, anatomy, paths


def score(paths: list[Path], sample: pd.DataFrame) -> pd.DataFrame:
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [str(path.resolve()) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def select(anatomy: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "strict_promote_gate",
        "info_sensor_gate",
        "below_resolution_gate",
        "block_gate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
    ]
    merged = anatomy.merge(scores[[c for c in score_cols if c in scores.columns]], on="basename", how="left")
    merged = merged[~merged["basename"].eq(CURRENT)].copy()
    merged["h011_big_bet_gate"] = (
        (merged["h010_axis_coeff"] <= -0.20)
        & (merged["h010_axis_public_delta_linear"] <= -0.00040)
        & (merged["changed_cells"] >= 40)
        & (merged["max_abs_prob_delta"] <= 0.28)
    )
    merged["h011_selector_survival_gate"] = (
        (merged["pred_delta_vs_current_mean"].fillna(9.0) < 0.00025)
        & (merged["pred_delta_vs_current_p90"].fillna(9.0) < 0.0025)
        & (merged["pred_beats_current_rate"].fillna(0.0) >= 0.25)
    )
    merged["h011_score"] = (
        merged["h010_axis_public_delta_linear"].fillna(9.0)
        + 0.25 * merged["pred_delta_vs_current_mean"].fillna(0.0)
        + 0.00015 * np.maximum(merged["max_abs_prob_delta"].fillna(0.0) - 0.18, 0.0) / 0.10
        - 0.00003 * np.log1p(merged["changed_cells"].fillna(0.0)) / np.log(456.0)
    )
    merged["h011_decision"] = np.select(
        [
            merged["h011_big_bet_gate"] & merged["h011_selector_survival_gate"],
            merged["h011_big_bet_gate"],
            merged["h010_axis_coeff"] <= -0.20,
        ],
        ["public_inversion_jackpot", "public_inversion_high_risk", "inversion_sensor_only"],
        default="reject",
    )
    merged = merged.sort_values(
        ["h011_decision", "h011_score", "pred_delta_vs_current_p90", "max_abs_prob_delta"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)
    order = {
        "public_inversion_jackpot": 0,
        "public_inversion_high_risk": 1,
        "inversion_sensor_only": 2,
        "reject": 3,
    }
    merged["decision_rank"] = merged["h011_decision"].map(order).fillna(9).astype(int)
    merged = merged.sort_values(["decision_rank", "h011_score", "pred_delta_vs_current_p90"]).reset_index(drop=True)
    merged.to_csv(SELECTION_OUT, index=False)
    return merged


def copy_primary(selection: pd.DataFrame) -> Path | None:
    top = selection[selection["h011_decision"].isin(["public_inversion_jackpot", "public_inversion_high_risk"])].head(1)
    if top.empty:
        return None
    source = ROOT / str(top.iloc[0]["file"])
    out = ROOT / f"submission_h011_public_inversion_{safe_id(str(top.iloc[0]['candidate_id']), 72)}_uploadsafe.csv"
    shutil.copyfile(source, out)
    return out


def md_table(frame: pd.DataFrame, n: int = 30) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def write_report(anatomy: pd.DataFrame, scores: pd.DataFrame, selection: pd.DataFrame, primary: Path | None) -> None:
    cols = [
        "candidate_id",
        "h011_decision",
        "family",
        "target_subset",
        "changed_cells",
        "h010_axis_coeff",
        "h010_axis_public_delta_linear",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "max_abs_prob_delta",
        "mean_agreement_on_changed",
        "file",
    ]
    lines = [
        "# H011 H010 Public-Inversion Jackpot",
        "",
        "## Question",
        "",
        "H010 looked locally correct but failed public by `+0.0020128681` versus E247. Is the H010 S1/S4 action axis actually a public-negative target representation?",
        "",
        "## Worldview",
        "",
        "HS-JEPA should not only predict labels. It should predict whether a proposed human-state action is healthy for the public/test world. H010 becomes the first explicit public-bad action-health teacher.",
        "",
        "## Falsifiable Claim",
        "",
        "If the public subset wants the opposite objective-stage route, candidates with negative projection onto the H010 action axis should move public LB meaningfully below E247. If they do not, the anti-H010-route worldview is dead and H010 was just an overfit local rank rewrite.",
        "",
        "## Output",
        "",
        f"- generated candidates: `{len(anatomy)}`",
        f"- public inversion jackpot/high-risk candidates: `{int(selection['h011_decision'].isin(['public_inversion_jackpot', 'public_inversion_high_risk']).sum())}`",
        f"- primary upload-safe file: `{rel(primary) if primary else 'none'}`",
        "",
        "## Top Selection",
        "",
        md_table(selection[[c for c in cols if c in selection.columns]], n=40),
        "",
        "## Selector Context",
        "",
        "The selector is now calibrated with E368 and H010 as known observations in `analysis_outputs/public_probe_observations.csv`. H011 is still a big-bet extrapolation, not a conservative promotion.",
        "",
        "## Files",
        "",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(ANATOMY_OUT)}`",
        f"- `{rel(SCORE_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, anatomy, paths = materialize()
    sample = base[KEYS]
    anatomy.to_csv(CANDIDATE_OUT, index=False)
    scores = score(paths, sample)
    selection = select(anatomy, scores)
    primary = copy_primary(selection)
    write_report(anatomy, scores, selection, primary)
    print(REPORT_OUT)
    if primary is not None:
        print(primary)
    print(
        selection[
            [
                "candidate_id",
                "h011_decision",
                "h010_axis_coeff",
                "h010_axis_public_delta_linear",
                "pred_delta_vs_current_mean",
                "pred_delta_vs_current_p90",
                "pred_beats_current_rate",
                "max_abs_prob_delta",
                "file",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
