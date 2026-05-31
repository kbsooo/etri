#!/usr/bin/env python3
"""E353: public-bad tangent neutralization for the E351 lifestyle-state action.

Question:
    E351 is selector-stable locally.  Is there still a removable component that
    points toward already observed public-bad movements?

This is a JEPA-style action-health test rather than a public LB optimizer:
context is the E351 compact lifestyle-state action, target representation is
the known public-adverse tangent span, and the operation removes only positive
projection onto that span.  A candidate is useful only if the lifestyle-state
action remains visible after the neutralization.
"""

from __future__ import annotations

import hashlib
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

warnings.filterwarnings("ignore", message="An input array is constant")

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e346_counteraxis_public_analog_audit import axis_records, null_delta, public_analog_metrics, test_meta  # noqa: E402
from e347_lifestyle_state_candidate_reaudit import load_candidate, load_lifestyle_teacher  # noqa: E402
from e349_e347_target_cell_ablation_stress import clip_prob, short_hash, sigmoid, specificity_metrics  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 353
EPS = 1.0e-12
NULL_REPS = 8

E247_FILE = OUT / CURRENT
E347_FILE = OUT / "submission_e347_stateful_counteraxis_lifestyle_e344_nullsafe_top5_e131968c_uploadsafe.csv"
E349_FILE = OUT / "submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv"
E350_FILE = OUT / "submission_e350_compactplateau_selected_compact_t45_s1_005_s3a1_00_ef54727b_uploadsafe.csv"
E351_FILE = OUT / "submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv"
OBS_AXIS_IN = OUT / "e346_public_analog_observed_axes.csv"

CANDIDATE_OUT = OUT / "e353_public_tangent_neutralization_candidates.csv"
SCORE_OUT = OUT / "e353_public_tangent_neutralization_scores.csv"
PUBLIC_ANALOG_OUT = OUT / "e353_public_tangent_neutralization_public_analog.csv"
NULL_OUT = OUT / "e353_public_tangent_neutralization_nulls.csv"
REPORT_OUT = OUT / "e353_public_tangent_neutralization_report.md"
UPLOAD_PREFIX = "submission_e353_publictangent"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
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


def norm(delta: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(delta, dtype=np.float64).reshape(-1)))


def dot(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a.reshape(-1), b.reshape(-1)))


def cos(a: np.ndarray, b: np.ndarray) -> float:
    den = norm(a) * norm(b)
    return 0.0 if den <= EPS else dot(a, b) / den


def target_abs(delta: np.ndarray) -> dict[str, float]:
    return {f"abs_{target}": float(np.abs(delta[:, i]).sum()) for i, target in enumerate(TARGETS)}


def load_base() -> tuple[pd.DataFrame, np.ndarray]:
    base = load_sub(E247_FILE).sort_values(KEYS).reset_index(drop=True)
    base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    return base, base_logit


def load_delta(path: Path, base: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray:
    frame = load_candidate(path, base[KEYS])
    return logit(frame[TARGETS].to_numpy(dtype=np.float64)) - base_logit


def observed_axis_deltas(base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    obs = pd.read_csv(OBS_AXIS_IN)
    rows: list[dict[str, Any]] = []
    for rec in obs[obs["exists"].fillna(False).astype(bool)].to_dict("records"):
        path = locate(rec["file"])
        delta = load_delta(path, base, base_logit)
        rows.append(
            {
                "file": rec["file"],
                "loss_tier": rec.get("loss_tier", ""),
                "public_delta_vs_e247": float(rec.get("public_delta_vs_e247", 0.0)),
                "delta": delta,
            }
        )
    return pd.DataFrame(rows)


def axis_sets(axis_df: pd.DataFrame) -> dict[str, list[np.ndarray]]:
    def pick(*tokens: str) -> list[np.ndarray]:
        out: list[np.ndarray] = []
        for rec in axis_df.to_dict("records"):
            name = str(rec["file"]).lower()
            if any(token in name for token in tokens):
                out.append(rec["delta"])
        return out

    severe = [rec["delta"] for rec in axis_df.to_dict("records") if float(rec["public_delta_vs_e247"]) >= 0.0005]
    mild = [rec["delta"] for rec in axis_df.to_dict("records") if 0.0 < float(rec["public_delta_vs_e247"]) < 0.0005]
    return {
        "all_existing": [rec["delta"] for rec in axis_df.to_dict("records")],
        "severe_existing": severe,
        "mild_existing": mild,
        "e323": pick("e323"),
        "e216": pick("e216"),
        "e256_e267": pick("e256", "e267"),
        "e95_e101_e176": pick("e95", "e101", "e176"),
        "broad_residual": pick("hybrid_0p578", "foldsafe_stage2", "ordinal"),
    }


def remove_positive_sequential(delta: np.ndarray, axes: list[np.ndarray], alpha: float) -> tuple[np.ndarray, float, float, int]:
    out = np.asarray(delta, dtype=np.float64).copy()
    removed_l2 = 0.0
    max_pos_cos = 0.0
    count = 0
    for axis in axes:
        denom = dot(axis, axis)
        if denom <= EPS:
            continue
        coeff = dot(out, axis) / denom
        c = cos(out, axis)
        if coeff <= 0.0 or c <= 0.0:
            continue
        component = coeff * axis
        out = out - float(alpha) * component
        removed_l2 += norm(float(alpha) * component)
        max_pos_cos = max(max_pos_cos, c)
        count += 1
    return out, removed_l2, max_pos_cos, count


def remove_positive_span(delta: np.ndarray, axes: list[np.ndarray], alpha: float) -> tuple[np.ndarray, float, float, int]:
    if not axes:
        return np.asarray(delta, dtype=np.float64).copy(), 0.0, 0.0, 0
    cols = []
    for axis in axes:
        v = axis.reshape(-1)
        if float(np.linalg.norm(v)) > EPS:
            cols.append(v)
    if not cols:
        return np.asarray(delta, dtype=np.float64).copy(), 0.0, 0.0, 0
    x = np.column_stack(cols)
    y = delta.reshape(-1)
    beta = np.linalg.pinv(x.T @ x + 1.0e-8 * np.eye(x.shape[1])) @ x.T @ y
    beta_pos = np.maximum(beta, 0.0)
    component = x @ beta_pos
    out = (y - float(alpha) * component).reshape(delta.shape)
    max_pos_cos = max(max(cos(delta, axis), 0.0) for axis in axes)
    return out, float(np.linalg.norm(float(alpha) * component)), max_pos_cos, int((beta_pos > 0.0).sum())


def candidate_meta(spec: dict[str, Any], path: Path, delta: np.ndarray, source_delta: np.ndarray) -> dict[str, Any]:
    return {
        **spec,
        "file": rel(path),
        "basename": path.name,
        "changed_rows_vs_e247": int((np.abs(delta).sum(axis=1) > EPS).sum()),
        "changed_cells_vs_e247": int((np.abs(delta) > EPS).sum()),
        "move_l1": float(np.abs(delta).sum()),
        "move_l2": norm(delta),
        "source_move_l2": norm(source_delta),
        "delta_l2_vs_source": norm(delta - source_delta),
        "delta_cos_vs_source": cos(delta, source_delta),
        **target_abs(delta),
    }


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, spec: dict[str, Any], source_delta: np.ndarray) -> tuple[Path, dict[str, Any]]:
    out = base[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(base_logit + delta))
    tag = safe_id(str(spec["variant"]), 88)
    path = OUT / f"{UPLOAD_PREFIX}_{tag}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, candidate_meta(spec, path, delta, source_delta)


def reference_row(name: str, path: Path, base: pd.DataFrame, base_logit: np.ndarray, source_delta: np.ndarray) -> dict[str, Any]:
    delta = load_delta(path, base, base_logit)
    spec = {
        "variant": name,
        "source": "reference",
        "axis_set": "none",
        "method": "none",
        "alpha": 0.0,
        "removed_l2": 0.0,
        "source_poscos_before": 0.0,
        "removed_component_count": 0,
    }
    return candidate_meta(spec, path, delta, source_delta)


def create_candidates(base: pd.DataFrame, base_logit: np.ndarray, axis_df: pd.DataFrame) -> pd.DataFrame:
    source_delta = load_delta(E351_FILE, base, base_logit)
    rows: list[dict[str, Any]] = [
        reference_row("canonical_e347", E347_FILE, base, base_logit, source_delta),
        reference_row("canonical_e349", E349_FILE, base, base_logit, source_delta),
        reference_row("canonical_e350", E350_FILE, base, base_logit, source_delta),
        reference_row("canonical_e351", E351_FILE, base, base_logit, source_delta),
    ]
    hashes = {Path(str(row["basename"])).stem.rsplit("_", 1)[-1] for row in rows}
    sets = axis_sets(axis_df)
    alphas = [0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 0.75, 1.00]
    for set_name, axes in sets.items():
        if not axes:
            continue
        for method in ["sequential", "span"]:
            for alpha in alphas:
                if method == "sequential":
                    delta, removed, max_pos, count = remove_positive_sequential(source_delta, axes, alpha)
                else:
                    delta, removed, max_pos, count = remove_positive_span(source_delta, axes, alpha)
                if removed <= 1.0e-10:
                    continue
                spec = {
                    "variant": f"{method}_{set_name}_a{alpha:.2f}",
                    "source": "e351",
                    "axis_set": set_name,
                    "method": method,
                    "alpha": alpha,
                    "removed_l2": removed,
                    "source_poscos_before": max_pos,
                    "removed_component_count": count,
                }
                path, meta = write_candidate(base, base_logit, delta, spec, source_delta)
                frame_hash = path.stem.rsplit("_", 1)[-1]
                if frame_hash in hashes:
                    path.unlink(missing_ok=True)
                    continue
                hashes.add(frame_hash)
                rows.append(meta)
    out = pd.DataFrame(rows).sort_values(["source", "axis_set", "method", "alpha", "variant"]).reset_index(drop=True)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def score_public_analog(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    obs_axes = pd.read_csv(OBS_AXIS_IN)
    axes = axis_records(obs_axes, base, base_logit)
    meta = test_meta(base)
    modes = ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm", "subject_perm", "dateblock_perm"]
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = locate(rec["file"])
        pred = load_candidate(path, base[KEYS])
        delta = logit(pred[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append({"basename": rec["basename"], **public_analog_metrics(delta, axes)})
        for mode in modes:
            for rep in range(NULL_REPS):
                nd = null_delta(delta, mode, meta, stable_seed(rec["basename"], mode, rep))
                null_rows.append({"basename": rec["basename"], "mode": mode, "rep": rep, **public_analog_metrics(nd, axes)})

    scores = pd.DataFrame(rows)
    nulls = pd.DataFrame(null_rows)
    risk_cols = [
        "public_loss_weighted_pos_cos",
        "severe_loss_weighted_pos_cos",
        "max_severe_pos_cos",
        "poscos_e323",
        "poscos_e216",
        "poscos_e267",
        "poscos_e256",
    ]
    for col in risk_cols:
        if col not in scores:
            scores[col] = 0.0
        if col not in nulls:
            nulls[col] = 0.0
    agg_rows: list[dict[str, Any]] = []
    for rec in scores.to_dict("records"):
        part = nulls[nulls["basename"].eq(rec["basename"])]
        item: dict[str, Any] = {"basename": rec["basename"]}
        for col in risk_cols:
            item[f"{col}_null_p90"] = float(part[col].quantile(0.90))
            item[f"{col}_dominance_lower_is_better"] = float(np.mean(float(rec[col]) < part[col].to_numpy(dtype=float)))
        agg_rows.append(item)
    agg = pd.DataFrame(agg_rows)
    scores = scores.merge(agg, on="basename", how="left")
    dominance_cols = [c for c in scores.columns if c.endswith("_dominance_lower_is_better")]
    scores["public_analog_survival_score"] = scores[dominance_cols].fillna(0.0).mean(axis=1)
    scores["public_analog_risk_score"] = (
        scores["public_loss_weighted_pos_cos"].fillna(0.0)
        + scores["severe_loss_weighted_pos_cos"].fillna(0.0)
        + scores["max_severe_pos_cos"].fillna(0.0)
        + scores.get("poscos_e323", 0.0)
        + scores.get("poscos_e216", 0.0)
    )
    scores.to_csv(PUBLIC_ANALOG_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    return scores, nulls


def combined_scores(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    sample = base[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    files = [CURRENT] + candidates["file"].astype(str).tolist()
    e272_candidates = build_features(files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    selector = score_candidates(known, e272_candidates, model_df)

    public_scores, _ = score_public_analog(candidates, base, base_logit)
    latent, state_cols, residual_cols, calendar_cols = load_lifestyle_teacher(base[KEYS])
    spec_rows: list[dict[str, Any]] = []
    e351_prob = load_candidate(E351_FILE, base[KEYS])[TARGETS].to_numpy(dtype=np.float64)
    e349_prob = load_candidate(E349_FILE, base[KEYS])[TARGETS].to_numpy(dtype=np.float64)
    diff_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = locate(rec["file"])
        pred = load_candidate(path, base[KEYS])
        prob = pred[TARGETS].to_numpy(dtype=np.float64)
        delta = logit(prob) - base_logit
        spec_rows.append({"basename": rec["basename"], **specificity_metrics(delta, latent, state_cols, residual_cols, calendar_cols, rec["basename"])})
        d351 = np.abs(prob - e351_prob)
        d349 = np.abs(prob - e349_prob)
        diff_rows.append(
            {
                "basename": rec["basename"],
                "prob_l1_delta_vs_e351": float(d351.sum()),
                "prob_max_abs_delta_vs_e351": float(d351.max()),
                "changed_cells_vs_e351": int((d351 > 1.0e-12).sum()),
                "prob_l1_delta_vs_e349": float(d349.sum()),
                "prob_max_abs_delta_vs_e349": float(d349.max()),
                "changed_cells_vs_e349": int((d349 > 1.0e-12).sum()),
            }
        )

    scores = candidates.merge(selector, on="basename", how="left", suffixes=("", "_selector"))
    scores = scores.merge(public_scores, on="basename", how="left", suffixes=("", "_public"))
    scores = scores.merge(pd.DataFrame(spec_rows), on="basename", how="left")
    scores = scores.merge(pd.DataFrame(diff_rows), on="basename", how="left")

    e351 = scores[scores["variant"].eq("canonical_e351")].iloc[0]
    risk_cols = ["poscos_e323", "poscos_e216", "poscos_e267", "poscos_e256"]
    for col in risk_cols:
        if col not in scores:
            scores[col] = 0.0
    scores["direct_bad_poscos_sum"] = scores[risk_cols].fillna(0.0).sum(axis=1)
    scores["p90_delta_vs_e351"] = scores["pred_delta_vs_current_p90"].fillna(1.0) - float(e351["pred_delta_vs_current_p90"])
    scores["risk_delta_vs_e351"] = scores["public_analog_risk_score"].fillna(9.0) - float(e351["public_analog_risk_score"])
    scores["q1_margin_delta_vs_e351"] = scores["q1_specificity_margin"].fillna(-9.0) - float(e351["q1_specificity_margin"])
    scores["e353_local_gate"] = (
        scores["source"].eq("e351")
        & scores["strict_promote_gate"].fillna(False).astype(bool)
        & (scores["pred_delta_vs_current_p90"].fillna(1.0) < -0.00005)
        & (scores["incremental_bad_axis_vs_current"].fillna(9.0).abs() <= 0.015)
        & (scores["p90_delta_vs_e351"] <= 2.0e-7)
        & (scores["risk_delta_vs_e351"] <= -1.0e-5)
        & (scores["q1_margin_delta_vs_e351"] >= -0.03)
        & scores["q1_specificity_pass"].fillna(False).astype(bool)
        & (~scores["broad_state_not_specific"].fillna(True).astype(bool))
        & (scores["direct_bad_poscos_sum"].fillna(0.0) <= 1.0e-9)
        & (scores["prob_l1_delta_vs_e351"].fillna(0.0) >= 0.0005)
        & (scores["delta_cos_vs_source"].fillna(0.0) >= 0.95)
    )
    scores["e353_rank_score"] = (
        5000.0 * (-scores["risk_delta_vs_e351"].fillna(0.0)).clip(lower=0.0)
        - 1400.0 * scores["p90_delta_vs_e351"].fillna(0.0).clip(lower=0.0)
        + 1.5 * scores["public_analog_survival_score"].fillna(0.0)
        + 0.8 * scores["state_specificity_score"].fillna(0.0)
        - 2.0 * scores["direct_bad_poscos_sum"].fillna(0.0)
        - 0.5 * (1.0 - scores["delta_cos_vs_source"].fillna(0.0)).clip(lower=0.0)
    )
    out = scores.sort_values(["e353_local_gate", "e353_rank_score"], ascending=[False, False]).reset_index(drop=True)
    out.to_csv(SCORE_OUT, index=False)
    return out


def materialize_selection(scores: pd.DataFrame) -> Path | None:
    selected = scores[scores["e353_local_gate"].fillna(False).astype(bool)].head(1)
    if selected.empty:
        return None
    rec = selected.iloc[0]
    src = locate(rec["file"])
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(rec['variant']), 56)}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() != out.resolve():
        frame.to_csv(out, index=False)
    scores.loc[scores["basename"].eq(rec["basename"]), "selected_uploadsafe_file"] = rel(out)
    scores.to_csv(SCORE_OUT, index=False)
    return out


def write_report(scores: pd.DataFrame, selected_path: Path | None, axis_df: pd.DataFrame) -> None:
    refs = scores[scores["source"].eq("reference")].copy()
    generated = scores[scores["source"].eq("e351")].copy()
    passed = scores[scores["e353_local_gate"].fillna(False).astype(bool)].copy()
    top_cols = [
        "variant",
        "source",
        "axis_set",
        "method",
        "alpha",
        "e353_local_gate",
        "e353_rank_score",
        "pred_delta_vs_current_p90",
        "p90_delta_vs_e351",
        "incremental_bad_axis_vs_current",
        "public_analog_risk_score",
        "risk_delta_vs_e351",
        "public_analog_survival_score",
        "direct_bad_poscos_sum",
        "q1_specificity_margin",
        "q1_margin_delta_vs_e351",
        "removed_l2",
        "source_poscos_before",
        "removed_component_count",
        "prob_l1_delta_vs_e351",
        "delta_cos_vs_source",
        "selected_uploadsafe_file",
    ]
    top_cols = [c for c in top_cols if c in scores.columns]
    axis_summary = (
        axis_df.assign(axis_norm=axis_df["delta"].map(norm))
        .drop(columns=["delta"])
        .sort_values("public_delta_vs_e247", ascending=False)
    )
    selected_text = rel(selected_path) if selected_path is not None else "none"
    lines = [
        "# E353 Public-Bad Tangent Neutralization",
        "",
        "## Question",
        "",
        "Can the E351 compact lifestyle-state action be made safer by removing positive projection onto known public-bad movement tangents?",
        "",
        "## Method",
        "",
        "- Base: E247 public-best submission.",
        "- Source action: logit(E351) - logit(E247).",
        "- Target representation: known public-adverse tangent axes from fixed public observations, especially E323/E216/E256/E267 and broad residual failures.",
        "- Operation: remove only positive projection from E351, using sequential one-axis removal and span removal at alphas `0.01-1.00`.",
        "- Stress: E272 public-free selector, E346 public-analog nulls, Q1 dateblock lifestyle-state specificity, E351 p90/risk/specificity deltas.",
        "- Public LB is not used to choose a score or tune a prior.",
        "",
        "## Decision",
        "",
        f"- candidates tested: `{len(scores)}`",
        f"- generated neutralized candidates: `{len(generated)}`",
        f"- E353 local gate pass count: `{len(passed)}`",
        f"- selected upload-safe candidate: `{selected_text}`",
        "",
    ]
    if selected_path is None:
        lines.extend(
            [
                "No neutralized variant beat E351 on public-analog risk while preserving p90, bad-axis safety, and Q1 lifestyle-state specificity.",
                "Interpretation: E351 is already close to the public-bad-tangent-neutral center under the current known-axis set. The next public-free improvement probably needs a new independent latent/support axis, not another projection cleanup.",
            ]
        )
    else:
        lines.extend(
            [
                "A neutralized variant passed the E353 gate.",
                "Interpretation: known public-bad tangent removal can improve E351 without destroying the compact lifestyle-state action.",
            ]
        )
    lines.extend(
        [
            "",
            "## Reference Candidates",
            "",
            md_table(refs[top_cols], n=10, floatfmt=".9f"),
            "",
            "## Top Generated Candidates",
            "",
            md_table(scores[top_cols], n=40, floatfmt=".9f"),
            "",
            "## Gate-Pass Candidates",
            "",
            md_table(passed[top_cols], n=40, floatfmt=".9f") if len(passed) else "_none_",
            "",
            "## Public Observation Axes Used",
            "",
            md_table(axis_summary, n=30, floatfmt=".9f"),
            "",
            "## Files",
            "",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(PUBLIC_ANALOG_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, base_logit = load_base()
    axis_df = observed_axis_deltas(base, base_logit)
    candidates = create_candidates(base, base_logit, axis_df)
    scores = combined_scores(candidates, base, base_logit)
    selected_path = materialize_selection(scores)
    write_report(scores, selected_path, axis_df)
    print(f"candidates: {len(scores)}")
    print(f"gate passes: {int(scores['e353_local_gate'].fillna(False).sum())}")
    print(f"selected: {rel(selected_path) if selected_path is not None else 'none'}")
    print(scores[["variant", "e353_local_gate", "pred_delta_vs_current_p90", "risk_delta_vs_e351", "q1_margin_delta_vs_e351", "prob_l1_delta_vs_e351"]].head(20).to_string(index=False))
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
