#!/usr/bin/env python3
"""E354: E247 support-latent graft/guard on the E351 lifestyle state.

Question:
    E353 showed that cleaning E351 against known public-bad tangents removes
    visibility together with risk.  Is there an independent E247 support latent
    that can be grafted onto E351, or is the safer move to guard E351 where it
    interferes with the E247 Q3 body?

This is a JEPA/data2vec-style test:
    context = compact E351 lifestyle-state action plus E286 preserve/avoid rows
    target  = E247 public-positive Q3 support representation
    action  = graft a tiny learned support residual, or mask E351's Q3
              interference on E247-support rows

No new public LB is used.  Known public results only define the already observed
E247/E256/E323/etc. sensor axes.
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


RNG_SEED = 20260531 + 354
EPS = 1.0e-12
NULL_REPS = 6
Q3_IDX = TARGETS.index("Q3")

E247_FILE = OUT / CURRENT
E349_FILE = OUT / "submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv"
E350_FILE = OUT / "submission_e350_compactplateau_selected_compact_t45_s1_005_s3a1_00_ef54727b_uploadsafe.csv"
E351_FILE = OUT / "submission_e351_robustplateau_selected_compact_t75_s1_005_s3a0_25_58e03127_uploadsafe.csv"
CELL_IN = OUT / "e285_e247_residual_human_state_cell_summary.csv"
SCORE_IN = OUT / "e286_e247_preserve_avoid_cell_score_summary.csv"
GOVERNOR_IN = OUT / "e286_e247_preserve_avoid_governor_summary.csv"
OBS_AXIS_IN = OUT / "e346_public_analog_observed_axes.csv"

CANDIDATE_OUT = OUT / "e354_e247_support_lifestyle_graft_candidates.csv"
SCORE_OUT = OUT / "e354_e247_support_lifestyle_graft_scores.csv"
PUBLIC_ANALOG_OUT = OUT / "e354_e247_support_lifestyle_graft_public_analog.csv"
NULL_OUT = OUT / "e354_e247_support_lifestyle_graft_nulls.csv"
ANATOMY_OUT = OUT / "e354_e247_support_lifestyle_graft_anatomy.csv"
SUPPORT_SOURCE_OUT = OUT / "e354_e247_support_lifestyle_graft_support_sources.csv"
REPORT_OUT = OUT / "e354_e247_support_lifestyle_graft_report.md"
UPLOAD_PREFIX = "submission_e354_e247support"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


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


def norm(delta: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(delta, dtype=np.float64).reshape(-1)))


def dot(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(np.asarray(a).reshape(-1), np.asarray(b).reshape(-1)))


def cos(a: np.ndarray, b: np.ndarray) -> float:
    den = norm(a) * norm(b)
    return 0.0 if den <= EPS else dot(a, b) / den


def target_abs(delta: np.ndarray) -> dict[str, float]:
    return {f"abs_{target}": float(np.abs(delta[:, i]).sum()) for i, target in enumerate(TARGETS)}


def key_norm(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out.reset_index(drop=True)


def load_base() -> tuple[pd.DataFrame, np.ndarray]:
    base = load_sub(E247_FILE).sort_values(KEYS).reset_index(drop=True)
    return base, logit(base[TARGETS].to_numpy(dtype=np.float64))


def load_delta(path: Path, base: pd.DataFrame, base_logit: np.ndarray) -> np.ndarray:
    frame = load_candidate(path, base[KEYS])
    return logit(frame[TARGETS].to_numpy(dtype=np.float64)) - base_logit


def observed_axis_deltas(base: pd.DataFrame, base_logit: np.ndarray, severe_only: bool = False) -> list[np.ndarray]:
    obs = pd.read_csv(OBS_AXIS_IN)
    if severe_only:
        obs = obs[obs["loss_tier"].eq("severe")]
    axes: list[np.ndarray] = []
    for rec in obs[obs["exists"].fillna(False).astype(bool)].to_dict("records"):
        axes.append(load_delta(locate(rec["file"]), base, base_logit))
    return axes


def remove_positive_sequential(delta: np.ndarray, axes: list[np.ndarray]) -> tuple[np.ndarray, int, float]:
    out = np.asarray(delta, dtype=np.float64).copy()
    count = 0
    max_pos = 0.0
    for axis in axes:
        denom = dot(axis, axis)
        if denom <= EPS:
            continue
        coeff = dot(out, axis) / denom
        c = cos(out, axis)
        if coeff <= 0.0 or c <= 0.0:
            continue
        out = out - coeff * axis
        count += 1
        max_pos = max(max_pos, c)
    return out, count, max_pos


def support_score_frame(base: pd.DataFrame) -> pd.DataFrame:
    cells = pd.read_csv(CELL_IN).sort_values(KEYS).reset_index(drop=True)
    scores = pd.read_csv(SCORE_IN).sort_values(KEYS).reset_index(drop=True)
    if len(cells) != len(base) or not key_norm(cells).equals(key_norm(base)):
        raise RuntimeError("E285 cell summary does not align with E247 base")
    if len(scores) != len(base) or not key_norm(scores).equals(key_norm(base)):
        raise RuntimeError("E286 cell-score summary does not align with E247 base")
    score_cols = [c for c in scores.columns if c.startswith("score_")]
    human_cols = [c for c in score_cols if "human" in c]
    oldlaw_cols = [c for c in score_cols if "oldlaw" in c]
    only_cols = [c for c in score_cols if "e247_only_vs_e256" in c]
    clean_cols = [c for c in score_cols if "e247_body_vs_clean" in c]
    bodyrisk_cols = [c for c in score_cols if "e247_body_vs_risk" in c]

    out = cells.copy()
    out["support_score_all"] = scores[score_cols].mean(axis=1)
    out["support_score_human"] = scores[human_cols].mean(axis=1)
    out["support_score_oldlaw"] = scores[oldlaw_cols].mean(axis=1)
    out["support_score_only"] = scores[only_cols].mean(axis=1)
    out["support_score_clean"] = scores[clean_cols].mean(axis=1)
    out["support_score_bodyrisk"] = scores[bodyrisk_cols].mean(axis=1)
    out["support_score_hybrid"] = (
        0.35 * out["support_score_only"].fillna(out["support_score_all"])
        + 0.35 * out["support_score_clean"].fillna(out["support_score_all"])
        + 0.20 * out["support_score_oldlaw"].fillna(out["support_score_all"])
        + 0.10 * out["support_score_human"].fillna(out["support_score_all"])
    )
    return out


def e351_support_anatomy(delta: np.ndarray, support: pd.DataFrame, label: str) -> dict[str, Any]:
    q3 = delta[:, Q3_IDX]
    rollback = support["rollback_logit_step"].to_numpy(dtype=np.float64)
    rollback_sign = np.sign(rollback)
    valid = np.abs(rollback) > EPS
    body = support["in_e247"].astype(bool).to_numpy()
    common = support["e247_common"].astype(bool).to_numpy()
    only = support["e247_only"].astype(bool).to_numpy()
    e256_only = support["e256_only"].astype(bool).to_numpy()
    support_high = support["support_score_hybrid"].rank(pct=True).to_numpy() >= 0.90

    def group_metrics(mask: np.ndarray, prefix: str) -> dict[str, Any]:
        m = mask & valid
        aligned = m & (q3 * rollback_sign > EPS)
        opposite = m & (q3 * rollback_sign < -EPS)
        abs_sum = float(np.abs(q3[m]).sum())
        opp = float(np.abs(q3[opposite]).sum())
        align = float(np.abs(q3[aligned]).sum())
        return {
            f"{prefix}_n": int(m.sum()),
            f"{prefix}_q3_abs": abs_sum,
            f"{prefix}_q3_aligned_abs": align,
            f"{prefix}_q3_opposite_abs": opp,
            f"{prefix}_alignment_ratio": align / max(align + opp, EPS),
        }

    row: dict[str, Any] = {
        "label": label,
        "total_q3_abs": float(np.abs(q3).sum()),
        "q3_nonzero_rows": int((np.abs(q3) > EPS).sum()),
    }
    row.update(group_metrics(body, "e247_body"))
    row.update(group_metrics(common, "e247_common"))
    row.update(group_metrics(only, "e247_only"))
    row.update(group_metrics(e256_only, "e256_only"))
    row.update(group_metrics(support_high, "support_high"))
    row["support_interference_l1"] = row["e247_body_q3_opposite_abs"] + 0.5 * row["support_high_q3_opposite_abs"]
    row["support_alignment_score"] = row["e247_body_alignment_ratio"] + 0.25 * row["support_high_alignment_ratio"]
    return row


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, spec: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    out = base[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(base_logit + delta))
    tag = safe_id(str(spec["variant"]), 96)
    path = OUT / f"{UPLOAD_PREFIX}_{tag}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    meta = {
        **spec,
        "file": rel(path),
        "basename": path.name,
        "changed_rows_vs_e247": int((np.abs(delta).sum(axis=1) > EPS).sum()),
        "changed_cells_vs_e247": int((np.abs(delta) > EPS).sum()),
        "move_l1": float(np.abs(delta).sum()),
        "move_l2": norm(delta),
        **target_abs(delta),
    }
    return path, meta


def reference_row(name: str, path: Path, base: pd.DataFrame, base_logit: np.ndarray) -> dict[str, Any]:
    delta = load_delta(path, base, base_logit)
    return {
        "variant": name,
        "source_family": "reference",
        "source_file": rel(path),
        "operation": "reference",
        "beta": 0.0,
        "guard_factor": 1.0,
        "guard_group": "none",
        "badclean_count": 0,
        "badclean_max_poscos": 0.0,
        "file": rel(path),
        "basename": path.name,
        "changed_rows_vs_e247": int((np.abs(delta).sum(axis=1) > EPS).sum()),
        "changed_cells_vs_e247": int((np.abs(delta) > EPS).sum()),
        "move_l1": float(np.abs(delta).sum()),
        "move_l2": norm(delta),
        **target_abs(delta),
    }


def select_support_sources(base: pd.DataFrame, base_logit: np.ndarray, e351_delta: np.ndarray) -> pd.DataFrame:
    gov = pd.read_csv(GOVERNOR_IN)
    gov = gov[gov["source_path"].map(lambda x: Path(str(x)).exists() or (ROOT / str(x)).exists())].copy()
    gov = gov[
        (gov["actual_p90"] < -1.0e-6)
        & (gov["actual_beats_current_rate"] >= 0.95)
        & (gov["incremental_bad_axis_vs_current"].abs() <= 0.0015)
        & (~gov["known_public_worse_than_current"].fillna(False).astype(bool))
    ].copy()
    gov = gov.sort_values(["actual_p90", "incremental_bad_axis_vs_current", "actual_mean"]).drop_duplicates("candidate_id").head(12)
    rows: list[dict[str, Any]] = []
    for rec in gov.to_dict("records"):
        path = locate(rec["source_path"])
        d = load_delta(path, base, base_logit)
        rows.append(
            {
                **rec,
                "source_path": rel(path),
                "support_move_l2": norm(d),
                "support_move_l1": float(np.abs(d).sum()),
                "support_cos_e351": cos(d, e351_delta),
                "support_changed_cells": int((np.abs(d) > EPS).sum()),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(SUPPORT_SOURCE_OUT, index=False)
    return out


def create_guard_delta(e351_delta: np.ndarray, support: pd.DataFrame, group: str, factor: float, opposite_only: bool) -> np.ndarray:
    out = e351_delta.copy()
    if group == "e247_body":
        mask = support["in_e247"].astype(bool).to_numpy()
    elif group == "e247_only":
        mask = support["e247_only"].astype(bool).to_numpy()
    elif group == "e247_common":
        mask = support["e247_common"].astype(bool).to_numpy()
    elif group == "e256_only":
        mask = support["e256_only"].astype(bool).to_numpy()
    elif group == "boundary":
        mask = (support["e247_only"].astype(bool) | support["e256_only"].astype(bool)).to_numpy()
    elif group == "support_high10":
        mask = support["support_score_hybrid"].rank(pct=True).to_numpy() >= 0.90
    elif group == "support_high20":
        mask = support["support_score_hybrid"].rank(pct=True).to_numpy() >= 0.80
    else:
        raise ValueError(group)

    if opposite_only:
        rollback = support["rollback_logit_step"].to_numpy(dtype=np.float64)
        opp = e351_delta[:, Q3_IDX] * np.sign(rollback) < -EPS
        mask = mask & opp
    out[mask, Q3_IDX] *= float(factor)
    return out


def create_candidates(base: pd.DataFrame, base_logit: np.ndarray, support: pd.DataFrame) -> pd.DataFrame:
    e349_delta = load_delta(E349_FILE, base, base_logit)
    e350_delta = load_delta(E350_FILE, base, base_logit)
    e351_delta = load_delta(E351_FILE, base, base_logit)
    severe_axes = observed_axis_deltas(base, base_logit, severe_only=True)

    rows: list[dict[str, Any]] = [
        reference_row("canonical_e349", E349_FILE, base, base_logit),
        reference_row("canonical_e350", E350_FILE, base, base_logit),
        reference_row("canonical_e351", E351_FILE, base, base_logit),
    ]
    hashes = {row["basename"].rsplit("_", 1)[-1].replace(".csv", "") for row in rows}

    # Guard variants: preserve the E247 Q3 support body by damping only E351's
    # Q3 component on support rows, especially where it opposes the E247 rollback
    # direction.
    for group in ["e247_body", "e247_only", "e247_common", "e256_only", "boundary", "support_high10", "support_high20"]:
        for opposite_only in [True, False]:
            for factor in [0.0, 0.25, 0.50, 0.75]:
                if factor == 0.75 and not opposite_only:
                    continue
                delta = create_guard_delta(e351_delta, support, group, factor, opposite_only)
                if norm(delta - e351_delta) <= 1.0e-10:
                    continue
                spec = {
                    "variant": f"guard_{group}_{'opp' if opposite_only else 'all'}_f{factor:.2f}",
                    "source_family": "e351_q3_guard",
                    "source_file": rel(E351_FILE),
                    "operation": "q3_guard",
                    "beta": 0.0,
                    "guard_factor": factor,
                    "guard_group": group,
                    "opposite_only": opposite_only,
                    "badclean_count": 0,
                    "badclean_max_poscos": 0.0,
                }
                path, meta = write_candidate(base, base_logit, delta, spec)
                h = path.stem.rsplit("_", 1)[-1]
                if h in hashes:
                    path.unlink(missing_ok=True)
                    continue
                hashes.add(h)
                rows.append(meta)

    # Graft variants: add the strongest E286 E247-preserve micro-actions onto
    # E351.  Also try a severe-bad-axis-cleaned version of each support action.
    sources = select_support_sources(base, base_logit, e351_delta)
    for rec in sources.to_dict("records"):
        source_path = locate(rec["source_path"])
        raw_support = load_delta(source_path, base, base_logit)
        cleaned_support, clean_count, clean_pos = remove_positive_sequential(raw_support, severe_axes)
        for support_kind, support_delta, clean_count_i, clean_pos_i in [
            ("raw", raw_support, 0, 0.0),
            ("severe_clean", cleaned_support, clean_count, clean_pos),
        ]:
            if norm(support_delta) <= 1.0e-12:
                continue
            for beta in [0.50, 1.00, 1.50, 2.00, 3.00]:
                delta = e351_delta + float(beta) * support_delta
                spec = {
                    "variant": f"graft_{support_kind}_{safe_id(str(rec['candidate_id']), 44)}_b{beta:.2f}",
                    "source_family": "e286_support_graft",
                    "source_file": rec["source_path"],
                    "operation": f"graft_{support_kind}",
                    "beta": beta,
                    "guard_factor": 1.0,
                    "guard_group": "none",
                    "opposite_only": False,
                    "badclean_count": clean_count_i,
                    "badclean_max_poscos": clean_pos_i,
                    "support_actual_p90": float(rec["actual_p90"]),
                    "support_actual_mean": float(rec["actual_mean"]),
                    "support_source_transfer_auc": float(rec["source_transfer_auc"]),
                }
                path, meta = write_candidate(base, base_logit, delta, spec)
                h = path.stem.rsplit("_", 1)[-1]
                if h in hashes:
                    path.unlink(missing_ok=True)
                    continue
                hashes.add(h)
                rows.append(meta)

    out = pd.DataFrame(rows).sort_values(["source_family", "operation", "variant"]).reset_index(drop=True)
    out.to_csv(CANDIDATE_OUT, index=False)

    anatomy = []
    for rec in out.to_dict("records"):
        anatomy.append({**rec, **e351_support_anatomy(load_delta(locate(rec["file"]), base, base_logit), support, rec["variant"])})
    pd.DataFrame(anatomy).to_csv(ANATOMY_OUT, index=False)
    return out


def score_public_analog(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    obs_axes = pd.read_csv(OBS_AXIS_IN)
    axes = axis_records(obs_axes, base, base_logit)
    meta = test_meta(base)
    modes = ["row_perm", "target_perm", "sign_flip", "row_sign", "subject_perm", "dateblock_perm"]
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = locate(rec["file"])
        delta = load_delta(path, base, base_logit)
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
    scores = scores.merge(pd.DataFrame(agg_rows), on="basename", how="left")
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


def combined_scores(candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray, support: pd.DataFrame) -> pd.DataFrame:
    sample = base[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    files = [CURRENT] + candidates["file"].astype(str).tolist()
    e272_candidates = build_features(files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    selector = score_candidates(known, e272_candidates, model_df)

    public_scores, _ = score_public_analog(candidates, base, base_logit)
    latent, state_cols, residual_cols, calendar_cols = load_lifestyle_teacher(base[KEYS])
    e351_prob = load_candidate(E351_FILE, base[KEYS])[TARGETS].to_numpy(dtype=np.float64)
    e351_delta = load_delta(E351_FILE, base, base_logit)
    anatomy = pd.read_csv(ANATOMY_OUT)

    spec_rows: list[dict[str, Any]] = []
    diff_rows: list[dict[str, Any]] = []
    for rec in candidates.to_dict("records"):
        path = locate(rec["file"])
        pred = load_candidate(path, base[KEYS])
        prob = pred[TARGETS].to_numpy(dtype=np.float64)
        delta = logit(prob) - base_logit
        spec_rows.append({"basename": rec["basename"], **specificity_metrics(delta, latent, state_cols, residual_cols, calendar_cols, rec["basename"])})
        d351 = np.abs(prob - e351_prob)
        diff_rows.append(
            {
                "basename": rec["basename"],
                "prob_l1_delta_vs_e351": float(d351.sum()),
                "prob_max_abs_delta_vs_e351": float(d351.max()),
                "changed_cells_vs_e351": int((d351 > 1.0e-12).sum()),
                "delta_cos_vs_e351": cos(delta, e351_delta),
            }
        )

    scores = candidates.merge(selector, on="basename", how="left", suffixes=("", "_selector"))
    scores = scores.merge(public_scores, on="basename", how="left", suffixes=("", "_public"))
    scores = scores.merge(pd.DataFrame(spec_rows), on="basename", how="left")
    scores = scores.merge(pd.DataFrame(diff_rows), on="basename", how="left")
    scores = scores.merge(
        anatomy[
            [
                "basename",
                "support_interference_l1",
                "support_alignment_score",
                "e247_body_q3_opposite_abs",
                "e247_body_alignment_ratio",
                "e247_only_q3_opposite_abs",
                "e256_only_q3_abs",
                "support_high_q3_opposite_abs",
            ]
        ],
        on="basename",
        how="left",
    )

    e351 = scores[scores["variant"].eq("canonical_e351")].iloc[0]
    risk_cols = ["poscos_e323", "poscos_e216", "poscos_e267", "poscos_e256"]
    for col in risk_cols:
        if col not in scores:
            scores[col] = 0.0
    scores["direct_bad_poscos_sum"] = scores[risk_cols].fillna(0.0).sum(axis=1)
    scores["p90_delta_vs_e351"] = scores["pred_delta_vs_current_p90"].fillna(1.0) - float(e351["pred_delta_vs_current_p90"])
    scores["risk_delta_vs_e351"] = scores["public_analog_risk_score"].fillna(9.0) - float(e351["public_analog_risk_score"])
    scores["q1_margin_delta_vs_e351"] = scores["q1_specificity_margin"].fillna(-9.0) - float(e351["q1_specificity_margin"])
    scores["support_interference_delta_vs_e351"] = scores["support_interference_l1"].fillna(9.0) - float(e351["support_interference_l1"])
    scores["support_alignment_delta_vs_e351"] = scores["support_alignment_score"].fillna(0.0) - float(e351["support_alignment_score"])

    graft_transfer_ok = (
        ~scores["source_family"].eq("e286_support_graft")
        | (scores["support_source_transfer_auc"].fillna(1.0) >= 0.45)
    )
    support_change = (
        (scores["support_interference_delta_vs_e351"] <= -1.0e-5)
        | (scores["support_alignment_delta_vs_e351"] >= 0.01)
        | (
            scores["source_family"].eq("e286_support_graft")
            & (scores["support_source_transfer_auc"].fillna(0.0) >= 0.45)
            & (scores["prob_l1_delta_vs_e351"].fillna(0.0) >= 0.0005)
        )
    )
    scores["e354_local_gate"] = (
        ~scores["source_family"].eq("reference")
        & scores["strict_promote_gate"].fillna(False).astype(bool)
        & (scores["pred_delta_vs_current_p90"].fillna(1.0) < -0.00005)
        & (scores["p90_delta_vs_e351"] <= 4.0e-7)
        & (scores["incremental_bad_axis_vs_current"].fillna(9.0).abs() <= 0.015)
        & (scores["risk_delta_vs_e351"] <= 0.00050)
        & (scores["q1_margin_delta_vs_e351"] >= -0.035)
        & scores["q1_specificity_pass"].fillna(False).astype(bool)
        & (~scores["broad_state_not_specific"].fillna(True).astype(bool))
        & (scores["direct_bad_poscos_sum"].fillna(0.0) <= 0.0010)
        & (scores["delta_cos_vs_e351"].fillna(0.0) >= 0.985)
        & graft_transfer_ok
        & support_change
    )
    scores["e354_rank_score"] = (
        -1600.0 * scores["p90_delta_vs_e351"].fillna(0.0).clip(lower=0.0)
        - 600.0 * scores["risk_delta_vs_e351"].fillna(0.0).clip(lower=0.0)
        + 1400.0 * (-scores["support_interference_delta_vs_e351"].fillna(0.0)).clip(lower=0.0)
        + 2.0 * scores["public_analog_survival_score"].fillna(0.0)
        + 0.9 * scores["state_specificity_score"].fillna(0.0)
        + 0.5 * scores["support_alignment_delta_vs_e351"].fillna(0.0)
        + 0.15 * scores["support_source_transfer_auc"].fillna(0.0)
        - 4.0 * scores["direct_bad_poscos_sum"].fillna(0.0)
        - 0.6 * (1.0 - scores["delta_cos_vs_e351"].fillna(0.0)).clip(lower=0.0)
    )
    out = scores.sort_values(["e354_local_gate", "e354_rank_score"], ascending=[False, False]).reset_index(drop=True)
    out.to_csv(SCORE_OUT, index=False)
    return out


def materialize_selection(scores: pd.DataFrame) -> Path | None:
    for old in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        old.unlink(missing_ok=True)
    selected = scores[scores["e354_local_gate"].fillna(False).astype(bool)].head(1)
    if selected.empty:
        return None
    rec = selected.iloc[0]
    src = locate(rec["file"])
    frame = pd.read_csv(src)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(rec['variant']), 58)}_{short_hash(frame)}_uploadsafe.csv"
    if src.resolve() != out.resolve():
        frame.to_csv(out, index=False)
    scores.loc[scores["basename"].eq(rec["basename"]), "selected_uploadsafe_file"] = rel(out)
    scores.to_csv(SCORE_OUT, index=False)
    return out


def write_report(scores: pd.DataFrame, selected_path: Path | None, support_sources: pd.DataFrame) -> None:
    refs = scores[scores["source_family"].eq("reference")].copy()
    generated = scores[~scores["source_family"].eq("reference")].copy()
    passed = scores[scores["e354_local_gate"].fillna(False).astype(bool)].copy()
    anatomy = pd.read_csv(ANATOMY_OUT)
    anatomy_refs = anatomy[anatomy["variant"].isin(["canonical_e349", "canonical_e350", "canonical_e351"])].copy()
    family_summary = (
        generated.groupby(["source_family", "operation"], dropna=False)
        .agg(
            n=("basename", "count"),
            gate_pass=("e354_local_gate", "sum"),
            best_p90_delta=("p90_delta_vs_e351", "min"),
            best_risk_delta=("risk_delta_vs_e351", "min"),
            best_interference_delta=("support_interference_delta_vs_e351", "min"),
            best_rank=("e354_rank_score", "max"),
        )
        .reset_index()
        .sort_values(["gate_pass", "best_rank"], ascending=[False, False])
    )
    top_cols = [
        "variant",
        "source_family",
        "operation",
        "beta",
        "guard_group",
        "guard_factor",
        "opposite_only",
        "e354_local_gate",
        "e354_rank_score",
        "pred_delta_vs_current_p90",
        "p90_delta_vs_e351",
        "public_analog_risk_score",
        "risk_delta_vs_e351",
        "incremental_bad_axis_vs_current",
        "direct_bad_poscos_sum",
        "q1_specificity_margin",
        "q1_margin_delta_vs_e351",
        "support_interference_l1",
        "support_interference_delta_vs_e351",
        "support_alignment_score",
        "support_alignment_delta_vs_e351",
        "delta_cos_vs_e351",
        "prob_l1_delta_vs_e351",
        "selected_uploadsafe_file",
    ]
    top_cols = [c for c in top_cols if c in scores.columns]
    anatomy_cols = [
        "variant",
        "source_family",
        "operation",
        "total_q3_abs",
        "e247_body_q3_abs",
        "e247_body_q3_aligned_abs",
        "e247_body_q3_opposite_abs",
        "e247_body_alignment_ratio",
        "e247_only_q3_opposite_abs",
        "e256_only_q3_abs",
        "support_high_q3_opposite_abs",
        "support_interference_l1",
        "support_alignment_score",
    ]
    anatomy_cols = [c for c in anatomy_cols if c in anatomy.columns]
    selected_text = rel(selected_path) if selected_path is not None else "none"
    lines = [
        "# E354 E247 Support-Latent Lifestyle Graft",
        "",
        "## Question",
        "",
        "Can the small E286 E247-preserve latent become useful when grafted onto E351, or can E351 be improved by guarding Q3 where it interferes with E247's public-positive support body?",
        "",
        "## Method",
        "",
        "- Base/current anchor: E247 public-best.",
        "- Source state: E351 compact hidden lifestyle-state action.",
        "- Support target: E247/E256 Q3 body from E285/E286 preserve-avoid latent.",
        "- Candidate families: E351 Q3 support guards, plus E286 micro-action grafts with optional severe-public-bad cleanup.",
        "- Stress: E272 selector, E346 public-analog nulls, E347/E349 lifestyle specificity, E247 support-interference metrics.",
        "- Public LB is not used for any new candidate.",
        "",
        "## Decision",
        "",
        f"- candidates tested: `{len(scores)}`",
        f"- generated candidates: `{len(generated)}`",
        f"- E354 local gate pass count: `{len(passed)}`",
        f"- selected upload-safe candidate: `{selected_text}`",
        "",
    ]
    if selected_path is None:
        lines.extend(
            [
                "No E247-support graft/guard candidate passed the full local gate.",
                "Interpretation: the E286 support latent explains E247 cell identity, but it still does not add a distinct action-safe direction on top of E351. The strongest path remains E351 unless a new support latent is learned from a richer target than the current E247/E256 cell boundary.",
            ]
        )
    else:
        lines.extend(
            [
                "A candidate passed the E354 gate.",
                "Interpretation: E247-support preservation is separable enough from E351 to justify a scarce public sensor.",
            ]
        )
    lines.extend(
        [
            "",
            "## E351 Support Anatomy",
            "",
            md_table(anatomy_refs[anatomy_cols], n=10, floatfmt=".9f"),
            "",
            "## Family Summary",
            "",
            md_table(family_summary, n=40, floatfmt=".9f"),
            "",
            "## Reference Candidates",
            "",
            md_table(refs[top_cols], n=10, floatfmt=".9f"),
            "",
            "## Top Candidates",
            "",
            md_table(scores[top_cols], n=50, floatfmt=".9f"),
            "",
            "## Gate-Pass Candidates",
            "",
            md_table(passed[top_cols], n=50, floatfmt=".9f") if len(passed) else "_none_",
            "",
            "## Support Sources",
            "",
            md_table(support_sources, n=20, floatfmt=".9f"),
            "",
            "## Files",
            "",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(PUBLIC_ANALOG_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(ANATOMY_OUT)}`",
            f"- `{rel(SUPPORT_SOURCE_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, base_logit = load_base()
    support = support_score_frame(base)
    e351_delta = load_delta(E351_FILE, base, base_logit)
    support_sources = select_support_sources(base, base_logit, e351_delta)
    candidates = create_candidates(base, base_logit, support)
    scores = combined_scores(candidates, base, base_logit, support)
    scores["selected_uploadsafe_file"] = ""
    selected_path = materialize_selection(scores)
    write_report(scores, selected_path, support_sources)
    print(f"candidates: {len(scores)}")
    print(f"gate passes: {int(scores['e354_local_gate'].fillna(False).sum())}")
    print(f"selected: {rel(selected_path) if selected_path is not None else 'none'}")
    cols = [
        "variant",
        "source_family",
        "operation",
        "e354_local_gate",
        "pred_delta_vs_current_p90",
        "p90_delta_vs_e351",
        "risk_delta_vs_e351",
        "support_interference_delta_vs_e351",
        "q1_margin_delta_vs_e351",
        "delta_cos_vs_e351",
    ]
    print(scores[cols].head(25).to_string(index=False))
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
