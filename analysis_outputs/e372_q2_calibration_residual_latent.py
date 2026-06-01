#!/usr/bin/env python3
"""E372: Q2 calibration-residual hidden lifestyle-state latent.

E370/E371 gave a useful negative result: shrinking E368's Q2 movement lowers
E323-like exposure, but the public-free Q2 lifestyle-transfer signal disappears
with it.  This experiment changes the question.

    context = masked lifestyle/social/raw/calendar views
    target  = train-side Q2 residual after subject/calendar calibration
    action  = replace or blend E368's Q2 movement only when the learned
              residual-calibration state is locally real and not null-like

This is a JEPA/data2vec-style probe in the tabular setting: it predicts a
latent residual state, not raw lifelog values or public LB.
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
from e330_target_residual_lifestyle_latent import (  # noqa: E402
    base_label_matrix_all,
    cv_logloss,
    fit_logistic_predict,
    fit_ridge_full_predict,
    groups_for,
    oof_proba,
    oof_ridge_scalar,
    safe_spearman,
    shuffled_feature,
)
from e357_public_survival_contrast_latent import KEY, TARGETS  # noqa: E402
from e358_rowstate_public_survival_audit import load_anchor  # noqa: E402
from e369_q2s1_lifestyle_transfer_audit import rank01  # noqa: E402
from public_anchor_bottleneck_decomposition import logit  # noqa: E402


RNG_SEED = 20260531 + 372
EPS = 1.0e-12
TARGET = "Q2"
VIEW_IDS = ["family", "jepa_resid", "story_bundle", "raw_day", "family_story", "family_jepa_story"]
GROUP_SPLITS = ["subject", "dateblock"]
NULL_REPS = 10
MAX_LATENTS = 12
CAP = 0.075
UPLOAD_PREFIX = "submission_e372_q2calib"

CALIB_OUT = OUT / "e372_q2_calibration_residual_latents.csv"
NULL_OUT = OUT / "e372_q2_calibration_residual_nulls.csv"
VECTOR_OUT = OUT / "e372_q2_calibration_residual_test_vectors.csv"
CANDIDATE_OUT = OUT / "e372_q2_calibration_residual_candidates.csv"
SCORES_OUT = OUT / "e372_q2_calibration_residual_scores.csv"
SCENARIOS_OUT = OUT / "e372_q2_calibration_residual_scenarios.csv"
RANKS_OUT = OUT / "e372_q2_calibration_residual_scenario_ranks.csv"
SUPPORT_OUT = OUT / "e372_q2_calibration_residual_support.csv"
SELECTION_OUT = OUT / "e372_q2_calibration_residual_selection.csv"
DECISION_OUT = OUT / "e372_q2_calibration_residual_decision.csv"
REPORT_OUT = OUT / "e372_q2_calibration_residual_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def stable_seed(*parts: object) -> int:
    payload = "|".join(map(str, parts)).encode("utf-8")
    return RNG_SEED + int(hashlib.sha1(payload).hexdigest()[:8], 16) % 100000


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def cos(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb) + EPS)
    return float(np.sum(aa * bb) / denom)


def as_model_frame(view: pd.DataFrame) -> pd.DataFrame:
    return view.replace([np.inf, -np.inf], 0.0).fillna(0.0).reset_index(drop=True)


def patch_e370_outputs() -> None:
    e370.TRANSFER_ROWS_OUT = OUT / "e372_q2_calibration_residual_transfer_rows.csv"
    e370.SCORES_OUT = SCORES_OUT
    e370.SCENARIOS_OUT = SCENARIOS_OUT
    e370.RANKS_OUT = RANKS_OUT
    e370.SUPPORT_OUT = SUPPORT_OUT


def load_transfer_context(sample: pd.DataFrame) -> pd.DataFrame:
    diag_path = OUT / "e371_q2_rowwise_safety_gate_diagnostics.csv"
    if diag_path.exists():
        ctx = normalize_dates(pd.read_csv(diag_path)).sort_values(KEY).reset_index(drop=True)
        sample_norm = normalize_dates(sample.copy()).sort_values(KEY).reset_index(drop=True)
        require_aligned(sample_norm, ctx[KEY], "e371_gate_diag")
        return ctx
    # Fallback: build a minimal transfer context.  This only runs when the E371
    # diagnostic file is absent.
    patch_e370_outputs()
    transfer, _meta = e370.build_transfer_vectors(sample)
    out = normalize_dates(sample[KEY].copy()).sort_values(KEY).reset_index(drop=True)
    require_aligned(out, transfer[KEY], "e372_transfer")
    out["q2_transfer"] = rank01(transfer["q2_publicfree_transfer_score"])
    out["s1_transfer"] = rank01(transfer["s1_publicfree_transfer_score"])
    out["q2_gate"] = 0.0
    out["s1_gate"] = 0.0
    out["bad_gate"] = 0.0
    out["row_validity_pred"] = 0.0
    return out


def build_q2_residual_latents() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    frames = load_frames()
    state = frames["state"].copy()
    views = build_views(frames)
    train_mask = state["split"].eq("train").to_numpy()
    train = state.loc[train_mask].reset_index(drop=True)
    test = state.loc[~train_mask].sort_values(KEY).reset_index(drop=True)

    for name, view in views.items():
        require_aligned(state, normalize_dates(pd.concat([state[KEY], view], axis=1)), f"view_{name}")

    base_x_train, base_x_test = base_label_matrix_all(train, test)
    train_views = {k: as_model_frame(v.loc[train_mask]) for k, v in views.items() if k in VIEW_IDS}
    test_views = {k: as_model_frame(v.loc[~train_mask]) for k, v in views.items() if k in VIEW_IDS}

    y = train[TARGET].astype(int).to_numpy()
    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    vectors: list[pd.DataFrame] = []

    for split_name in GROUP_SPLITS:
        groups = groups_for(train, split_name).reset_index(drop=True)
        null_groups = {
            "row": groups,
            "subject": groups_for(train, "subject").reset_index(drop=True),
            "dateblock": groups_for(train, "dateblock").reset_index(drop=True),
        }
        if int(groups.nunique()) < 3:
            continue
        base_oof = oof_proba(base_x_train, y, groups)
        base_loss = cv_logloss(base_x_train, y, groups)
        teacher = y.astype(float) - base_oof
        for view_id in VIEW_IDS:
            x_view_train = train_views[view_id]
            x_view_test = test_views[view_id]
            pred_oof, _pred_full_train, r2 = oof_ridge_scalar(x_view_train, teacher, groups)
            pred_test = fit_ridge_full_predict(x_view_train, teacher, x_view_test)
            x_aug = pd.concat([base_x_train.reset_index(drop=True), pd.Series(pred_oof, name="q2_calib_resid_state")], axis=1)
            aug_loss = cv_logloss(x_aug, y, groups)
            actual_delta = float(aug_loss - base_loss)

            rng = np.random.default_rng(stable_seed("null", split_name, view_id))
            null_vals = []
            for mode, mgroups in null_groups.items():
                for rep in range(NULL_REPS):
                    shuf = shuffled_feature(pred_oof, mode, mgroups, rng)
                    nx = pd.concat([base_x_train.reset_index(drop=True), pd.Series(shuf, name="q2_calib_resid_state")], axis=1)
                    null_delta = float(cv_logloss(nx, y, groups) - base_loss)
                    null_vals.append(null_delta)
                    null_rows.append(
                        {
                            "target": TARGET,
                            "view_id": view_id,
                            "split": split_name,
                            "mode": mode,
                            "rep": rep,
                            "null_delta": null_delta,
                        }
                    )
            null_arr = np.asarray(null_vals, dtype=np.float64)
            dominance = float(np.mean(actual_delta < null_arr))
            placebo_adjusted = actual_delta - float(np.median(null_arr))

            p_base_test = fit_logistic_predict(base_x_train, y, base_x_test)
            p_aug_test = fit_logistic_predict(x_aug, y, pd.concat([base_x_test.reset_index(drop=True), pd.Series(pred_test, name="q2_calib_resid_state")], axis=1))
            raw_delta = np.clip(logit(p_aug_test) - logit(p_base_test), -CAP, CAP)
            latent_id = f"{TARGET}_{view_id}_{split_name}"
            vectors.append(
                pd.DataFrame(
                    {
                        **{k: test[k].to_numpy() for k in KEY},
                        "latent_id": latent_id,
                        "q2_resid_score": pred_test,
                        "q2_calib_logit_delta": raw_delta,
                        "q2_calib_abs_delta": np.abs(raw_delta),
                    }
                )
            )
            rows.append(
                {
                    "latent_id": latent_id,
                    "target": TARGET,
                    "view_id": view_id,
                    "split": split_name,
                    "context_cols": int(x_view_train.shape[1]),
                    "base_logloss": float(base_loss),
                    "aug_logloss": float(aug_loss),
                    "actual_delta": actual_delta,
                    "teacher_std": float(np.std(teacher)),
                    "student_oof_r2": float(r2),
                    "student_spearman": safe_spearman(pred_oof, teacher),
                    "null_best": float(np.min(null_arr)),
                    "null_median": float(np.median(null_arr)),
                    "null_q20": float(np.quantile(null_arr, 0.20)),
                    "dominance": dominance,
                    "placebo_adjusted_vs_median": placebo_adjusted,
                    "test_delta_l1": float(np.sum(np.abs(raw_delta))),
                    "test_delta_std": float(np.std(raw_delta)),
                    "gate": bool(actual_delta < -0.0004 and dominance >= 0.80 and placebo_adjusted < -0.00015),
                }
            )

    latent = pd.DataFrame(rows).sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]).reset_index(drop=True)
    nulls = pd.DataFrame(null_rows)
    vector_df = pd.concat(vectors, ignore_index=True) if vectors else pd.DataFrame()
    return latent, nulls, vector_df, train, test


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
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(str(meta['variant']), 98)}_{digest}.csv"
    out.to_csv(path, index=False)
    rows.append({**meta, "file": rel(path), "basename": path.name})


def add_meta(
    variant: str,
    family: str,
    latent_rec: dict[str, Any],
    delta: np.ndarray,
    e368_delta: np.ndarray,
    bad365: np.ndarray,
    bad247: np.ndarray,
    ctx: pd.DataFrame,
) -> dict[str, Any]:
    q2_idx = TARGETS.index("Q2")
    s1_idx = TARGETS.index("S1")
    q2_delta = delta[:, q2_idx]
    s1_delta = delta[:, s1_idx]
    q2_bad = bad365[:, q2_idx]
    q2_e368 = e368_delta[:, q2_idx]
    return {
        "variant": variant,
        "family": family,
        "latent_id": latent_rec.get("latent_id", "none"),
        "view_id": latent_rec.get("view_id", "none"),
        "split": latent_rec.get("split", "none"),
        "local_actual_delta": float(latent_rec.get("actual_delta", np.nan)),
        "local_dominance": float(latent_rec.get("dominance", np.nan)),
        "local_placebo_adjusted": float(latent_rec.get("placebo_adjusted_vs_median", np.nan)),
        "student_spearman": float(latent_rec.get("student_spearman", np.nan)),
        "student_oof_r2": float(latent_rec.get("student_oof_r2", np.nan)),
        "latent_gate": bool(latent_rec.get("gate", False)),
        "q2_l1": float(np.sum(np.abs(q2_delta))),
        "s1_l1": float(np.sum(np.abs(s1_delta))),
        "all_l1": float(np.sum(np.abs(delta))),
        "all_cos_e323_bad_vs_e365": cos(delta, bad365),
        "all_cos_e323_bad_vs_e247": cos(delta, bad247),
        "q2_cos_e323_bad_vs_e365": cos(q2_delta, q2_bad) if np.linalg.norm(q2_delta) > EPS else 0.0,
        "q2_cos_e323_bad_vs_e247": cos(q2_delta, bad247[:, q2_idx]) if np.linalg.norm(q2_delta) > EPS else 0.0,
        "s1_cos_e323_bad_vs_e365": cos(s1_delta, bad365[:, s1_idx]) if np.linalg.norm(s1_delta) > EPS else 0.0,
        "q2_abs_delta_spearman_vs_e368": safe_spearman(np.abs(q2_delta), np.abs(q2_e368)),
        "q2_signed_delta_spearman_vs_e368": safe_spearman(q2_delta, q2_e368),
        "q2_transfer_abs_spearman": safe_spearman(np.abs(q2_delta), ctx["q2_transfer"].to_numpy(dtype=np.float64)) if "q2_transfer" in ctx else 0.0,
        "s1_transfer_abs_spearman": safe_spearman(np.abs(s1_delta), ctx["s1_transfer"].to_numpy(dtype=np.float64)) if "s1_transfer" in ctx else 0.0,
        **q2_contrib_metrics(q2_delta, q2_bad),
    }


def generate_candidates(latent: pd.DataFrame, vectors: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    sample = test[KEY].sort_values(KEY).reset_index(drop=True)
    e365, e368_sel, e247, e323 = e370.load_backbones(sample)
    l365 = logit(e365[TARGETS].to_numpy(dtype=np.float64))
    l368 = logit(e368_sel[TARGETS].to_numpy(dtype=np.float64))
    l247 = logit(e247[TARGETS].to_numpy(dtype=np.float64))
    l323 = logit(e323[TARGETS].to_numpy(dtype=np.float64))
    e368_delta = l368 - l365
    bad365 = l323 - l365
    bad247 = l323 - l247
    q2_idx = TARGETS.index("Q2")
    s1_idx = TARGETS.index("S1")
    ctx = load_transfer_context(sample)

    selected = latent[latent["gate"]].copy()
    if selected.empty:
        selected = latent[(latent["actual_delta"] < 0.0) & (latent["dominance"] >= 0.65)].copy()
    selected = selected.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_LATENTS).reset_index(drop=True)

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    identity = e368_delta.copy()
    meta = add_meta("e372_identity_e368", "identity_e368", {"latent_id": "identity_e368"}, identity, e368_delta, bad365, bad247, ctx)
    write_candidate(e365, l365 + identity, meta, rows, seen)

    if selected.empty:
        out = pd.DataFrame(rows)
        out.to_csv(CANDIDATE_OUT, index=False)
        return out

    for _, rec in selected.iterrows():
        latent_id = str(rec["latent_id"])
        vec = vectors[vectors["latent_id"].astype(str).eq(latent_id)].sort_values(KEY).reset_index(drop=True)
        require_aligned(sample, vec[KEY], f"e372_vec_{latent_id}")
        calib_delta = vec["q2_calib_logit_delta"].to_numpy(dtype=np.float64)
        if float(np.sum(np.abs(calib_delta))) < EPS:
            continue
        calib_abs_rank = rank01(np.abs(calib_delta))
        e368_q2 = e368_delta[:, q2_idx]
        agree = np.sign(calib_delta) == np.sign(e368_q2)
        strong = calib_abs_rank >= np.quantile(calib_abs_rank, 0.55)

        for q2_scale in [0.35, 0.50, 0.75, 1.00, 1.25]:
            for s1_scale in [1.00, 1.06, 1.15]:
                delta = np.zeros_like(e368_delta)
                delta[:, q2_idx] = q2_scale * calib_delta
                delta[:, s1_idx] = s1_scale * e368_delta[:, s1_idx]
                variant = f"e372_calibonly_{safe_id(latent_id, 40)}_q2{q2_scale}_s1{s1_scale}".replace(".", "p")
                meta = add_meta(variant, "q2_calib_replace_e368_s1", rec.to_dict(), delta, e368_delta, bad365, bad247, ctx)
                write_candidate(e365, l365 + delta, meta, rows, seen)

        for blend in [0.25, 0.50, 0.75]:
            for amp in [0.85, 1.00, 1.08]:
                for s1_scale in [1.00, 1.06, 1.15]:
                    delta = np.zeros_like(e368_delta)
                    delta[:, q2_idx] = amp * ((1.0 - blend) * e368_q2 + blend * calib_delta)
                    delta[:, s1_idx] = s1_scale * e368_delta[:, s1_idx]
                    variant = f"e372_blend_{safe_id(latent_id, 40)}_w{blend}_amp{amp}_s1{s1_scale}".replace(".", "p")
                    meta = add_meta(variant, "q2_e368_calib_blend", rec.to_dict(), delta, e368_delta, bad365, bad247, ctx)
                    write_candidate(e365, l365 + delta, meta, rows, seen)

        for floor in [0.25, 0.45, 0.65]:
            for amp in [0.85, 1.00, 1.08]:
                for s1_scale in [1.00, 1.06]:
                    keep = agree & strong
                    weight = np.where(keep, 1.0, floor)
                    delta = np.zeros_like(e368_delta)
                    delta[:, q2_idx] = amp * e368_q2 * weight
                    delta[:, s1_idx] = s1_scale * e368_delta[:, s1_idx]
                    variant = f"e372_agreegate_{safe_id(latent_id, 40)}_floor{floor}_amp{amp}_s1{s1_scale}".replace(".", "p")
                    meta = add_meta(variant, "q2_calib_agreement_gate", rec.to_dict(), delta, e368_delta, bad365, bad247, ctx)
                    meta["q2_agree_keep_rate"] = float(np.mean(keep))
                    write_candidate(e365, l365 + delta, meta, rows, seen)

    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def score_candidates(candidates: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    patch_e370_outputs()
    rowmask = normalize_dates(pd.read_csv(e368.ROWMASK_OUT)).sort_values(KEY).reset_index(drop=True)
    combined, scenarios, support = e370.score_candidates(candidates, rowmask)
    for frame in [combined, support]:
        if "candidate_origin" in frame.columns:
            frame["candidate_origin"] = frame["candidate_origin"].replace({"e370_generated": "e372_generated"})
    if "top_origin" in scenarios.columns:
        scenarios["top_origin"] = scenarios["top_origin"].replace({"e370_generated": "e372_generated"})
    combined.to_csv(SCORES_OUT, index=False)
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    support.to_csv(SUPPORT_OUT, index=False)
    if RANKS_OUT.exists():
        ranks = pd.read_csv(RANKS_OUT)
        if "candidate_origin" in ranks.columns:
            ranks["candidate_origin"] = ranks["candidate_origin"].replace({"e370_generated": "e372_generated"})
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
        "family",
        "latent_id",
        "view_id",
        "split",
        "local_actual_delta",
        "local_dominance",
        "local_placebo_adjusted",
        "student_spearman",
        "student_oof_r2",
        "latent_gate",
        "all_cos_e323_bad_vs_e365",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_abs_delta_spearman_vs_e368",
        "q2_signed_delta_spearman_vs_e368",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "q2_l1",
        "s1_l1",
        "all_l1",
    ]
    missing = [c for c in meta_cols if c not in work.columns]
    if missing:
        work = work.merge(candidates[["variant"] + missing], on="variant", how="left")
    generated = work[work["candidate_origin"].astype(str).eq("e372_generated")].copy()
    numeric_cols = [
        "top1_rate",
        "top5_rate",
        "top10_rate",
        "rank_mean",
        "e368_public_like_score",
        "local_actual_delta",
        "local_dominance",
        "local_placebo_adjusted",
        "student_spearman",
        "student_oof_r2",
        "all_cos_e323_bad_vs_e365",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_abs_delta_spearman_vs_e368",
        "q2_signed_delta_spearman_vs_e368",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "q2_l1",
        "s1_l1",
        "all_l1",
        "public_bad_axis_sum",
        "rowstate_pred_public_loss_mean",
        "rowstate_bad_minus_good_exposure",
    ]
    for col in numeric_cols:
        if col in generated:
            generated[col] = pd.to_numeric(generated[col], errors="coerce")

    current = generated[generated["variant"].astype(str).eq("e372_identity_e368")].head(1)
    if current.empty:
        current = generated.sort_values("e368_public_like_score", ascending=False).head(1)
    cur = current.iloc[0]

    for col in numeric_cols:
        if col in generated:
            fill = 0.0 if col not in ["local_actual_delta", "local_placebo_adjusted"] else 1.0
            generated[col] = generated[col].fillna(fill)

    generated["e372_local_score"] = (
        1.05 * rank01(-generated["local_actual_delta"])
        + 0.75 * rank01(generated["local_dominance"])
        + 0.50 * rank01(-generated["local_placebo_adjusted"])
        + 0.25 * rank01(generated["student_spearman"].abs())
    )
    generated["e372_scenario_score"] = (
        0.90 * generated["top1_rate"]
        + 0.55 * generated["top5_rate"]
        + 0.35 * generated["top10_rate"]
        + 0.30 * rank01(generated["e368_public_like_score"])
    )
    generated["e372_safety_score"] = (
        0.95 * rank01(-generated["q2_cos_e323_bad_vs_e365"].clip(lower=0.0))
        + 0.70 * rank01(-generated["q2_bad_positive_share"])
        + 0.60 * rank01(-generated["all_cos_e323_bad_vs_e365"].abs())
        + 0.45 * rank01(-generated["public_bad_axis_sum"].fillna(0.0))
        + 0.35 * rank01(-generated["rowstate_pred_public_loss_mean"].fillna(0.0))
        + 0.25 * rank01(-generated["rowstate_bad_minus_good_exposure"].fillna(0.0))
    )
    generated["e372_transfer_score"] = (
        0.60 * rank01(generated["q2_abs_delta_spearman_vs_e368"])
        + 0.30 * rank01(generated["q2_transfer_abs_spearman"])
        + 0.20 * rank01(generated["s1_transfer_abs_spearman"])
    )
    generated["e372_total_score"] = (
        generated["e372_scenario_score"]
        + 0.70 * generated["e372_safety_score"]
        + 0.55 * generated["e372_local_score"]
        + 0.35 * generated["e372_transfer_score"]
    )

    cur_q2_bad = float(cur.get("q2_cos_e323_bad_vs_e365", np.inf))
    cur_q2_pos = float(cur.get("q2_bad_positive_share", np.inf))
    cur_top10 = float(cur.get("top10_rate", 0.0))
    cur_pls = float(cur.get("e368_public_like_score", 0.0))
    cur_q2_l1 = float(cur.get("q2_l1", np.inf))

    non_identity = generated[~generated["variant"].astype(str).eq("e372_identity_e368")].copy()
    eligible = non_identity[
        non_identity["e363_submission_gate"].fillna(False).astype(bool)
        & (non_identity["top10_rate"] >= max(0.58, cur_top10 - 0.16))
        & (non_identity["e368_public_like_score"] >= cur_pls - 0.15)
        & (non_identity["local_actual_delta"] < 0.0)
        & (non_identity["local_dominance"] >= 0.65)
        & (non_identity["q2_cos_e323_bad_vs_e365"] <= cur_q2_bad - 0.04)
        & (non_identity["q2_bad_positive_share"] <= cur_q2_pos - 0.015)
        & (non_identity["all_cos_e323_bad_vs_e365"].abs() <= 0.06)
        & (non_identity["q2_l1"] <= max(cur_q2_l1 * 1.25, 1.0e-9))
        & (non_identity["s1_transfer_abs_spearman"] >= 0.08)
    ].copy()
    if len(eligible):
        chosen = eligible.sort_values("e372_total_score", ascending=False).head(1).copy()
        decision = "select_e372_q2_calibration_residual_candidate"
        reason = "A train-side Q2 residual-calibration latent replaces/blends E368 Q2 while preserving stress support and lowering Q2 bad-axis exposure."
        src = e370.locate(chosen.iloc[0]["file"])
        for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
            stale.unlink()
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(chosen.iloc[0]['variant']), 70)}_{short_hash(pd.read_csv(src))}_uploadsafe.csv"
        shutil.copyfile(src, upload)
    else:
        chosen = current.copy()
        decision = "keep_e368_no_q2_calibration_residual_replacement"
        reason = "No Q2 calibration-residual latent reduced E323-like Q2 risk while preserving E368 stress support; the residual state is diagnostic, not submission-grade."
        upload = e370.locate(e368_sel["selected_uploadsafe_file"])

    chosen["decision"] = decision
    chosen["reason"] = reason
    chosen["e365_variant"] = e365_variant
    chosen["current_q2_bad_cos"] = cur_q2_bad
    chosen["current_q2_bad_positive_share"] = cur_q2_pos
    chosen["current_top10_rate"] = cur_top10
    chosen["current_e368_public_like_score"] = cur_pls
    chosen["eligible_count"] = int(len(eligible))
    chosen["selected_uploadsafe_file"] = rel(upload)
    chosen.to_csv(SELECTION_OUT, index=False)
    generated.sort_values("e372_total_score", ascending=False).to_csv(DECISION_OUT, index=False)
    return chosen


def write_report(latent: pd.DataFrame, selected: pd.DataFrame, support: pd.DataFrame) -> None:
    ranked = pd.read_csv(DECISION_OUT)
    selection_cols = [
        "decision",
        "variant",
        "eligible_count",
        "selected_uploadsafe_file",
        "reason",
        "family",
        "latent_id",
        "local_actual_delta",
        "local_dominance",
        "top1_rate",
        "top10_rate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_abs_delta_spearman_vs_e368",
    ]
    top_cols = [
        "variant",
        "family",
        "latent_id",
        "local_actual_delta",
        "local_dominance",
        "top1_rate",
        "top10_rate",
        "e368_public_like_score",
        "q2_cos_e323_bad_vs_e365",
        "q2_bad_positive_share",
        "q2_abs_delta_spearman_vs_e368",
        "q2_transfer_abs_spearman",
        "s1_transfer_abs_spearman",
        "e372_total_score",
        "file",
    ]
    lines = [
        "# E372 Q2 Calibration-Residual Hidden Lifestyle Latent",
        "",
        "## Question",
        "",
        "Can a train-side Q2 calibration-residual lifestyle latent replace or reshape E368's risky Q2 movement without deleting the useful Q2/S1 structure?",
        "",
        "## Local Latent Health",
        "",
        md_table(latent.head(30), n=30, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selected[[c for c in selection_cols if c in selected.columns]], n=5, floatfmt=".9f"),
        "",
        "## Top E372 Candidates",
        "",
        md_table(ranked[[c for c in top_cols if c in ranked.columns]].head(40), n=40, floatfmt=".9f"),
        "",
        "## Scenario Support",
        "",
        md_table(support.head(30), n=30, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    decision = str(selected["decision"].iloc[0])
    if decision.startswith("select_"):
        lines.append(
            "The Q2 calibration-residual latent is strong enough to create a guarded candidate. The claim is specific: Q2 residual calibration, not generic lifestyle state, carries the actionable signal."
        )
    else:
        lines.append(
            "The Q2 calibration-residual latent did not become a safer replacement for E368. This strengthens the current bottleneck diagnosis: E368's Q2 edge is not cleanly separable into an independently calibrated train-side residual state."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{CALIB_OUT.name}`",
            f"- `{NULL_OUT.name}`",
            f"- `{VECTOR_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
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
    latent, nulls, vectors, _train, test = build_q2_residual_latents()
    latent.to_csv(CALIB_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    vectors.to_csv(VECTOR_OUT, index=False)

    anchor, _anchor_logit = load_anchor()
    sample = normalize_dates(anchor[KEY].copy()).sort_values(KEY).reset_index(drop=True)
    require_aligned(sample, test[KEY], "e372_test_anchor")

    candidates = generate_candidates(latent, vectors, test)
    combined, scenarios, support = score_candidates(candidates)
    selected = select_candidate(candidates, combined, support)
    write_report(latent, selected, support)
    print(f"latents={len(latent)} gated={int(latent['gate'].sum()) if len(latent) else 0} candidates={len(candidates)} scenarios={len(scenarios)}")
    print(selected[["decision", "variant", "eligible_count", "selected_uploadsafe_file", "reason"]].to_string(index=False))
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
