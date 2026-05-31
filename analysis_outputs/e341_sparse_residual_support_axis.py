#!/usr/bin/env python3
"""E341: sparse residual lifestyle support axis.

E330 found target-residual lifestyle states that improve blocked train CV, but
their direct test materialization moved all 250 rows and failed the public-free
selector.  E340 then showed that combining small safe sensors improves stability
but remains below visibility.

This experiment asks a narrower question:

    Are the E330 residual states useful only on rare lifestyle tails?

JEPA translation:
    context = masked lifestyle views and human/social story state
    target  = target-specific residual representation from blocked CV
    action  = sparse tail movement on rows where the residual state is extreme

No public LB is used.  Candidates must be judged by E272 selector geometry,
E323/E216 bad-axis anatomy, and fresh movement-null stress.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from scipy.special import expit


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e341_sparse_residual_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import load_sub_frame, md_table, safe_id  # noqa: E402
from e330_target_residual_lifestyle_latent import (  # noqa: E402
    base_label_matrix_all,
    fit_logistic_predict,
    fit_ridge_full_predict,
    groups_for,
    load_frames,
    oof_proba,
    oof_ridge_scalar,
    train_mask,
    build_views,
)
from e337_residual_lifestyle_cluster_state import (  # noqa: E402
    bad_axes,
    cell_bad_veto,
    center_by_target,
    cos,
    target_abs,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

RNG_SEED = 20260531 + 341
EPS = 1.0e-12
CAP = 0.18
MAX_SOURCE_ROWS = 6
TOPKS = [12, 20, 34]
SCALES = [0.55, 1.00, 1.60]
MAX_NULL_CANDIDATES = 28
NULL_REPS = 4

SOURCE_SUMMARY = OUT / "e330_target_residual_lifestyle_latent_summary.csv"
SOURCE_OUT = OUT / "e341_sparse_residual_support_sources.csv"
CANDIDATE_OUT = OUT / "e341_sparse_residual_support_candidates.csv"
SCORE_OUT = OUT / "e341_sparse_residual_support_scores.csv"
ANATOMY_OUT = OUT / "e341_sparse_residual_support_anatomy.csv"
MOVE_NULL_OUT = OUT / "e341_sparse_residual_support_movement_nulls.csv"
REPORT_OUT = OUT / "e341_sparse_residual_support_report.md"


def stable_seed(*parts: object) -> int:
    text = "|".join(map(str, parts))
    return RNG_SEED + int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100000


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_current() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return expit(np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0))


def write_candidate(base: pd.DataFrame, base_logit: np.ndarray, delta: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(base_logit + np.clip(delta, -CAP, CAP)))
    path = OUT / f"submission_e341_sparseresid_{safe_id(candidate_id, 120)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def load_source_rows() -> pd.DataFrame:
    src = pd.read_csv(SOURCE_SUMMARY)
    src["gate"] = src["gate"].astype(bool)
    selected = src[src["gate"]].copy()
    if selected.empty:
        selected = src[(src["actual_delta"] < 0.0) & (src["dominance"] >= 0.80)].copy()
    selected = selected.sort_values(
        ["gate", "actual_delta", "dominance", "placebo_adjusted_vs_median"],
        ascending=[False, True, False, True],
    ).head(MAX_SOURCE_ROWS)
    selected.to_csv(SOURCE_OUT, index=False)
    return selected.reset_index(drop=True)


def zscore_against_train(test_values: np.ndarray, train_values: np.ndarray) -> np.ndarray:
    train = np.asarray(train_values, dtype=np.float64)
    test = np.asarray(test_values, dtype=np.float64)
    med = float(np.nanmedian(train))
    q75 = float(np.nanquantile(train, 0.75))
    q25 = float(np.nanquantile(train, 0.25))
    scale = (q75 - q25) / 1.349
    if not np.isfinite(scale) or scale < 1.0e-8:
        scale = float(np.nanstd(train))
    if not np.isfinite(scale) or scale < 1.0e-8:
        scale = 1.0
    return np.clip((test - med) / scale, -8.0, 8.0)


def top_mask(score: np.ndarray, k: int) -> np.ndarray:
    x = np.asarray(score, dtype=np.float64)
    mask = np.zeros(len(x), dtype=bool)
    if len(x) == 0:
        return mask
    kk = min(max(1, int(k)), len(x))
    idx = np.argsort(-x)[:kk]
    mask[idx] = np.isfinite(x[idx])
    return mask


def tail_masks(raw_delta: np.ndarray, pred_test: np.ndarray, pred_train: np.ndarray, topk: int) -> dict[str, np.ndarray]:
    z = zscore_against_train(pred_test, pred_train)
    abs_delta = np.abs(raw_delta)
    masks = {
        "absdelta": top_mask(abs_delta, topk),
        "posdelta": top_mask(np.where(raw_delta > 0.0, raw_delta, -np.inf), topk),
        "negdelta": top_mask(np.where(raw_delta < 0.0, -raw_delta, -np.inf), topk),
        "state_abs_x_delta": top_mask(np.abs(z) * (abs_delta + EPS), topk),
    }
    return {k: v for k, v in masks.items() if int(v.sum()) > 0}


def compute_source_delta(
    rec: pd.Series,
    train: pd.DataFrame,
    test: pd.DataFrame,
    train_views: dict[str, pd.DataFrame],
    test_views: dict[str, pd.DataFrame],
    base_x_train: pd.DataFrame,
    base_x_test: pd.DataFrame,
) -> dict[str, Any] | None:
    target = str(rec["target"])
    view_id = str(rec["view_id"])
    split_name = str(rec["split"])
    if view_id not in train_views:
        return None
    groups = groups_for(train, split_name).reset_index(drop=True)
    y = train[target].astype(int).to_numpy()
    if len(np.unique(y)) < 2:
        return None
    base_oof = oof_proba(base_x_train, y, groups)
    teacher = y.astype(float) - base_oof
    pred_oof, _pred_full_train, state_r2 = oof_ridge_scalar(train_views[view_id], teacher, groups)
    pred_test = fit_ridge_full_predict(train_views[view_id], teacher, test_views[view_id])

    x_aug_train = pd.concat(
        [base_x_train.reset_index(drop=True), pd.Series(pred_oof, name="target_resid_state")],
        axis=1,
    )
    x_aug_test = pd.concat(
        [base_x_test.reset_index(drop=True), pd.Series(pred_test, name="target_resid_state")],
        axis=1,
    )
    p_base = fit_logistic_predict(base_x_train, y, base_x_test)
    p_aug = fit_logistic_predict(x_aug_train, y, x_aug_test)
    raw_delta = np.clip(logit(p_aug) - logit(p_base), -0.08, 0.08)
    if float(np.nanstd(raw_delta)) < 1.0e-12:
        return None
    return {
        "target": target,
        "view_id": view_id,
        "split": split_name,
        "raw_delta": raw_delta,
        "pred_train": pred_oof,
        "pred_test": pred_test,
        "state_r2_recomputed": float(state_r2),
        "source_actual_delta": float(rec["actual_delta"]),
        "source_dominance": float(rec["dominance"]),
        "source_placebo_adjusted": float(rec["placebo_adjusted_vs_median"]),
        "source_student_spearman": float(rec["student_spearman"]),
    }


def target_delta_matrix(target: str, row_delta: np.ndarray) -> np.ndarray:
    out = np.zeros((len(row_delta), len(TARGETS)), dtype=np.float64)
    out[:, TARGETS.index(target)] = np.asarray(row_delta, dtype=np.float64)
    return out


def transform_variants(delta: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray) -> dict[str, np.ndarray]:
    raw = np.asarray(delta, dtype=np.float64)
    return {
        "raw": raw,
        "inv": -raw,
        "bad_veto": cell_bad_veto(raw, e323_bad, e216_bad, strength=0.20),
        "inv_bad_veto": cell_bad_veto(-raw, e323_bad, e216_bad, strength=0.20),
    }


def materialize_candidates() -> tuple[pd.DataFrame, list[Path], pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    sources = load_source_rows()
    frames = load_frames()
    state = frames["state"].copy()
    views = build_views(frames)
    mask = train_mask(state)
    train = state.loc[mask].reset_index(drop=True)
    test = state.loc[~mask].sort_values(KEYS).reset_index(drop=True)
    test_index = state.loc[~mask].sort_values(KEYS).index.to_numpy()
    view_ids = sorted(set(sources["view_id"].astype(str)))
    train_views = {k: views[k].loc[mask].reset_index(drop=True) for k in view_ids if k in views}
    test_views = {k: views[k].loc[test_index].reset_index(drop=True) for k in view_ids if k in views}
    base_x_train, base_x_test = base_label_matrix_all(train, test)
    base = load_sub_frame(OUT / CURRENT, test[KEYS]).sort_values(KEYS).reset_index(drop=True)
    base_logit, e323_bad, e216_bad = bad_axes(base)

    paths: list[Path] = []
    rows: list[dict[str, Any]] = []
    source_payloads: list[dict[str, Any]] = []
    for _, rec in sources.iterrows():
        payload = compute_source_delta(rec, train, test, train_views, test_views, base_x_train, base_x_test)
        if payload is not None:
            source_payloads.append(payload)

    for src_idx, payload in enumerate(source_payloads):
        raw_delta = np.asarray(payload["raw_delta"], dtype=np.float64)
        for topk in TOPKS:
            for mask_name, mask in tail_masks(raw_delta, payload["pred_test"], payload["pred_train"], topk).items():
                sparse_row_delta = np.zeros_like(raw_delta)
                sparse_row_delta[mask] = raw_delta[mask]
                base_delta = target_delta_matrix(str(payload["target"]), sparse_row_delta)
                variants = transform_variants(base_delta, e323_bad, e216_bad)
                for variant_name, variant_delta in variants.items():
                    if float(np.sum(np.abs(variant_delta))) <= EPS:
                        continue
                    for scale in SCALES:
                        delta = variant_delta * float(scale)
                        if float(np.sum(np.abs(delta))) <= EPS:
                            continue
                        candidate_id = (
                            f"{payload['target']}_{payload['view_id']}_{payload['split']}"
                            f"_{mask_name}_top{topk}_{variant_name}_s{scale:.2f}"
                        )
                        path = write_candidate(base, base_logit, delta, candidate_id)
                        paths.append(path)
                        row_abs = np.sum(np.abs(delta), axis=1)
                        rows.append(
                            {
                                "candidate_id": candidate_id,
                                "file": rel(path),
                                "basename": path.name,
                                "source_idx": src_idx,
                                "target": payload["target"],
                                "view_id": payload["view_id"],
                                "split": payload["split"],
                                "tail_mask": mask_name,
                                "topk": int(topk),
                                "variant": variant_name,
                                "scale": float(scale),
                                "source_actual_delta": payload["source_actual_delta"],
                                "source_dominance": payload["source_dominance"],
                                "source_placebo_adjusted": payload["source_placebo_adjusted"],
                                "source_student_spearman": payload["source_student_spearman"],
                                "state_r2_recomputed": payload["state_r2_recomputed"],
                                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                                "changed_cells": int((np.abs(delta) > EPS).sum()),
                                "row_energy_entropy": entropy(row_abs),
                                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                                "l1_logit_delta": float(np.sum(np.abs(delta))),
                                "cos_with_e323_bad": cos(delta, e323_bad),
                                "cos_with_e216_bad": cos(delta, e216_bad),
                                **target_abs(delta),
                            }
                        )
    candidates = pd.DataFrame(rows)
    if len(candidates):
        candidates = candidates.drop_duplicates("basename").sort_values(
            ["target", "view_id", "split", "tail_mask", "topk", "variant", "scale"]
        ).reset_index(drop=True)
        keep = set(candidates["basename"])
        paths = [path for path in paths if path.name in keep]
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths, base, base_logit, e323_bad, e216_bad


def entropy(weights: np.ndarray) -> float:
    x = np.asarray(weights, dtype=np.float64)
    x = np.abs(x)
    total = float(x.sum())
    if total <= EPS:
        return 0.0
    p = x / total
    nz = p[p > 0.0]
    return float(-(nz * np.log(nz)).sum() / np.log(len(p))) if len(p) > 1 else 0.0


def score_paths(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        pd.DataFrame().to_csv(SCORE_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = build_features([CURRENT] + [rel(path) for path in paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def anatomy(paths: list[Path], base: pd.DataFrame, base_logit: np.ndarray, e323_bad: np.ndarray, e216_bad: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(delta) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(delta) > EPS).sum()),
                "l1_logit_delta": float(np.sum(np.abs(delta))),
                "mean_abs_logit_delta": float(np.mean(np.abs(delta))),
                "max_abs_logit_delta": float(np.max(np.abs(delta))),
                "cos_with_e323_bad": cos(delta, e323_bad),
                "cos_with_e216_bad": cos(delta, e216_bad),
                "signed_bad_overlap": float(np.mean((delta * e323_bad > 0.0) | (delta * e216_bad > 0.0))),
                **target_abs(delta),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad", "cos_with_e216_bad", "l1_logit_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def test_meta(base: pd.DataFrame) -> pd.DataFrame:
    state = pd.read_parquet(OUT / "e273_human_diary_state_jepa_audit_features.parquet")
    meta = state[state["split"].eq("test")][KEYS + ["dateblock_group", "weekday", "is_weekend", "subject_order"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        meta[col] = pd.to_datetime(meta[col]).dt.strftime("%Y-%m-%d")
    keys = base[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        keys[col] = pd.to_datetime(keys[col]).dt.strftime("%Y-%m-%d")
    aligned = keys.merge(meta, on=KEYS, how="left", validate="one_to_one")
    if aligned["dateblock_group"].isna().any():
        raise RuntimeError("test metadata alignment failed")
    return aligned.reset_index(drop=True)


def make_null_delta(delta: np.ndarray, meta: pd.DataFrame, mode: str, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    arr = np.asarray(delta, dtype=np.float64).copy()
    if mode == "row_perm":
        return arr[rng.permutation(arr.shape[0]), :]
    if mode == "target_perm":
        return arr[:, rng.permutation(arr.shape[1])]
    if mode == "sign_flip":
        return -arr
    if mode == "row_sign":
        return arr * rng.choice([-1.0, 1.0], size=(arr.shape[0], 1))
    if mode == "cell_perm":
        flat = arr.reshape(-1).copy()
        rng.shuffle(flat)
        return flat.reshape(arr.shape)
    if mode in {"subject_perm", "dateblock_perm"}:
        key = "subject_id" if mode == "subject_perm" else "dateblock_group"
        out = arr.copy()
        for _, idx in meta.groupby(key).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                out[idx_arr] = arr[idx_arr][rng.permutation(len(idx_arr))]
        return out
    raise ValueError(mode)


def movement_null_stress(scores: pd.DataFrame, candidates: pd.DataFrame, base: pd.DataFrame, base_logit: np.ndarray) -> pd.DataFrame:
    if scores.empty or candidates.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    joined = non_current.merge(candidates, on="basename", how="left", suffixes=("_score", "_meta"))
    chosen = joined.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(MAX_NULL_CANDIDATES)
    if chosen.empty:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    meta = test_meta(base)
    path_by_name = {
        str(row["basename"]): str(row["file"])
        for row in candidates[["basename", "file"]].dropna().to_dict("records")
    }
    null_paths: list[Path] = []
    null_rows: list[dict[str, Any]] = []
    NULL_DIR.mkdir(exist_ok=True)
    for rec in chosen.to_dict("records"):
        file_value = path_by_name.get(str(rec["basename"]), str(rec.get("file", "")))
        if not file_value or file_value.lower() == "nan":
            continue
        path = ROOT / file_value
        if not path.exists():
            path = OUT / str(rec.get("basename", ""))
        if not path.exists():
            continue
        cand = load_sub_frame(path, base[KEYS])
        delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - base_logit
        for mode in ["row_perm", "target_perm", "sign_flip", "row_sign", "cell_perm", "subject_perm", "dateblock_perm"]:
            for rep in range(NULL_REPS):
                nd = make_null_delta(delta, meta, mode, stable_seed(rec["basename"], mode, rep))
                npath = write_candidate(base, base_logit, nd, f"null_{Path(rec['basename']).stem}_{mode}_{rep}")
                null_paths.append(npath)
                null_rows.append({"basename": rec["basename"], "null_basename": npath.name, "mode": mode, "rep": rep})
    if not null_paths:
        pd.DataFrame().to_csv(MOVE_NULL_OUT, index=False)
        return pd.DataFrame()
    sample = load_sub(OUT / CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_features = build_features([CURRENT] + [rel(path) for path in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_features, model_df)
    cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    null_map = pd.DataFrame(null_rows).merge(null_scores[cols].rename(columns={"basename": "null_basename"}), on="null_basename", how="left")
    actual = non_current[cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
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
                "actual_beats_rate": float(a["actual_beats_rate"]),
                "actual_strict_promote": bool(a["actual_strict_promote"]),
                "null_mean_best": float(part["pred_delta_vs_current_mean"].min()),
                "null_mean_median": float(part["pred_delta_vs_current_mean"].median()),
                "null_p90_best": float(part["pred_delta_vs_current_p90"].min()),
                "null_p90_median": float(part["pred_delta_vs_current_p90"].median()),
                "actual_mean_dominance": float(np.mean(float(a["actual_mean"]) < part["pred_delta_vs_current_mean"].to_numpy(dtype=float))),
                "actual_p90_dominance": float(np.mean(float(a["actual_p90"]) < part["pred_delta_vs_current_p90"].to_numpy(dtype=float))),
                "null_strict_promote_rate": float(part["strict_promote_gate"].astype(bool).mean()),
                "mode_count": int(part["mode"].nunique()),
                "strict_null_modes": ",".join(sorted(part.loc[part["strict_promote_gate"].astype(bool), "mode"].unique())),
            }
        )
    out = pd.DataFrame(rows).sort_values(
        ["actual_strict_promote", "actual_p90_dominance", "actual_mean_dominance", "actual_p90"],
        ascending=[False, False, False, True],
    )
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(sources: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anat: pd.DataFrame, nulls: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current["strict_promote_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    info = non_current[non_current["info_sensor_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    safe = pd.DataFrame()
    if len(promoted) and len(nulls):
        safe = promoted.merge(nulls, on="basename", how="inner")
        safe = safe[
            (safe["actual_mean_dominance"] >= 0.70)
            & (safe["actual_p90_dominance"] >= 0.75)
            & (safe["null_strict_promote_rate"] <= 0.05)
        ]
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    cand_cols = [
        "basename",
        "target",
        "view_id",
        "split",
        "tail_mask",
        "topk",
        "variant",
        "scale",
        "source_actual_delta",
        "changed_rows",
        "mean_abs_logit_delta",
        "cos_with_e323_bad",
        "cos_with_e216_bad",
    ]
    lines = [
        "# E341 Sparse Residual Lifestyle Support Axis",
        "",
        "## Question",
        "",
        "Can E330's locally useful target-residual lifestyle states become public-visible if moved only on rare test tails?",
        "",
        "## Source Residual States",
        "",
        md_table(sources, n=16, floatfmt=".9f"),
        "",
        "## Generated Candidates",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- selector-promoted candidates: `{len(promoted)}`",
        f"- information-sensor candidates: `{len(info)}`",
        f"- movement-null-safe promoted candidates: `{len(safe)}`",
        "",
        "### Best Selector Scores",
        "",
        md_table(
            non_current.sort_values(
                ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
                ascending=[False, False, True, True],
            )[score_cols]
            if len(non_current)
            else non_current,
            n=50,
            floatfmt=".9f",
        ),
        "",
        "### Best Candidate Anatomy",
        "",
        md_table(candidates.sort_values(["cos_with_e323_bad", "mean_abs_logit_delta"])[cand_cols] if len(candidates) else candidates, n=50, floatfmt=".9f"),
        "",
        "## Movement-Null Stress",
        "",
        md_table(nulls, n=40, floatfmt=".9f"),
        "",
        "## Decision",
        "",
    ]
    if len(safe):
        best = safe.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).iloc[0]
        lines.append(f"`{best['basename']}` is a submission candidate: it clears selector and fresh movement-null gates.")
    elif len(promoted):
        lines.append("Sparse residual tails can cross selector visibility, but no promoted file survives movement-null stress. Treat as shortcut-prone until a cleaner state appears.")
    elif len(info):
        best = non_current.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).iloc[0]
        lines.append(f"Sparse residual tails remain information sensors only. Best p90 is `{best['pred_delta_vs_current_p90']:.9f}`, below submission standard but useful as support-axis evidence.")
    else:
        lines.append("Sparse residual tails do not improve the selector enough. E330 residual states are local CV features, not public-visible support axes in this form.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{SOURCE_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if CANDIDATE_OUT.exists() and SCORE_OUT.exists() and ANATOMY_OUT.exists():
        candidates = pd.read_csv(CANDIDATE_OUT)
        scores = pd.read_csv(SCORE_OUT)
        anat = pd.read_csv(ANATOMY_OUT)
        base = load_current()
        base_logit = logit(base[TARGETS].to_numpy(dtype=np.float64))
    else:
        candidates, paths, base, base_logit, e323_bad, e216_bad = materialize_candidates()
        scores = score_paths(paths)
        anat = anatomy(paths, base, base_logit, e323_bad, e216_bad)
    if MOVE_NULL_OUT.exists():
        nulls = pd.read_csv(MOVE_NULL_OUT)
    else:
        nulls = movement_null_stress(scores, candidates, base, base_logit)
    sources = pd.read_csv(SOURCE_OUT) if SOURCE_OUT.exists() else load_source_rows()
    write_report(sources, candidates, scores, anat, nulls)
    print(REPORT_OUT)
    if len(scores):
        non_current = scores[~scores["basename"].eq(CURRENT)].copy()
        cols = ["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate"]
        print(non_current[cols].head(50).round(9).to_string(index=False))
    if len(nulls):
        print("[movement-null]")
        print(nulls.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
