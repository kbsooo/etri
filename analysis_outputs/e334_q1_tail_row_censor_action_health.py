#!/usr/bin/env python3
"""E334: Q1 tail row-censor action-health audit.

E332 showed Q1 positive-tail is directional but too small/p90-risky.
E333 showed broad non-tail compensation is a local-validation shortcut.

This experiment keeps the Q1 latent and sign fixed, then changes only row
placement.  The question is whether a subset/censor of the Q1-tail action can
be visible on the E247 tensor without reproducing E323 public-bad movement.

No public LB is used.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import log_loss
from sklearn.model_selection import GroupKFold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e334_q1_tail_row_censor_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, E323, clip_prob, load_sub_frame, md_table, safe_id, sigmoid  # noqa: E402
from e330_target_residual_lifestyle_latent import groups_for, shuffled_feature  # noqa: E402
from e331_residual_state_localization import train_test_state  # noqa: E402
from e332_q1_tail_translator_stress import TARGET, build_q1_state, make_test_weights, optimize_scale, shifted_prob  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 334
EPS = 1.0e-12
CAP = 0.42
NULL_REPS = 5
MOVEMENT_NULL_REPS = 8
MAX_MATERIALIZE = 72
SCALES = [0.25, 0.35, 0.50, 0.65, 0.80, 1.00]

SUMMARY_OUT = OUT / "e334_q1_tail_row_censor_summary.csv"
NULL_OUT = OUT / "e334_q1_tail_row_censor_nulls.csv"
SELECTED_OUT = OUT / "e334_q1_tail_row_censor_selected.csv"
CANDIDATE_OUT = OUT / "e334_q1_tail_row_censor_candidates.csv"
SCORE_OUT = OUT / "e334_q1_tail_row_censor_candidate_scores.csv"
ANATOMY_OUT = OUT / "e334_q1_tail_row_censor_candidate_anatomy.csv"
MOVE_NULL_OUT = OUT / "e334_q1_tail_row_censor_movement_nulls.csv"
REPORT_OUT = OUT / "e334_q1_tail_row_censor_report.md"


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


def cv_one_dim(base_prob: np.ndarray, y: np.ndarray, weights: np.ndarray, groups: pd.Series) -> tuple[float, float, float, float]:
    base_loss = float(log_loss(y, base_prob, labels=[0, 1]))
    pred = base_prob.copy()
    ds: list[float] = []
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    for tr_idx, va_idx in cv.split(np.zeros((len(y), 1)), y, groups.reset_index(drop=True)):
        d, _loss = optimize_scale(base_prob[tr_idx], y[tr_idx], weights[tr_idx])
        ds.append(float(d))
        pred[va_idx] = shifted_prob(base_prob[va_idx], np.clip(d * weights[va_idx], -CAP, CAP))
    loss = float(log_loss(y, pred, labels=[0, 1]))
    return loss, loss - base_loss, float(np.mean(ds)) if ds else 0.0, float(np.std(ds)) if ds else 0.0


def active_quantile_mask(
    score_train: np.ndarray,
    score_test: np.ndarray,
    active_train: np.ndarray,
    active_test: np.ndarray,
    q: float,
    side: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    tr_values = np.asarray(score_train, dtype=np.float64)[active_train]
    if len(tr_values) == 0:
        return active_train & False, active_test & False, {"mask_threshold": np.nan}
    if side == "top":
        threshold = float(np.quantile(tr_values, 1.0 - q))
        return active_train & (score_train >= threshold), active_test & (score_test >= threshold), {"mask_threshold": threshold}
    if side == "bottom":
        threshold = float(np.quantile(tr_values, q))
        return active_train & (score_train <= threshold), active_test & (score_test <= threshold), {"mask_threshold": threshold}
    raise ValueError(side)


def calendar_condition(frame: pd.DataFrame, name: str) -> np.ndarray:
    d = pd.to_datetime(frame["sleep_date"])
    dow = d.dt.dayofweek.to_numpy()
    day = d.dt.day.to_numpy()
    if name == "weekend":
        return dow >= 5
    if name == "weekday":
        return dow < 5
    if name == "month_start":
        return day <= 5
    if name == "salary_end":
        return day >= 25
    if name == "midmonth":
        return (day >= 10) & (day <= 20)
    raise ValueError(name)


def build_masks(
    train: pd.DataFrame,
    test: pd.DataFrame,
    active_train: np.ndarray,
    active_test: np.ndarray,
    tail_train: np.ndarray,
    tail_test: np.ndarray,
    pred_train: np.ndarray,
    pred_test: np.ndarray,
    base_oof: np.ndarray,
    base_q1_test: np.ndarray,
) -> list[dict[str, Any]]:
    masks: list[dict[str, Any]] = [
        {"mask_name": "all_tail", "train_mask": active_train.copy(), "test_mask": active_test.copy(), "family": "all"},
    ]

    for score_name, tr_score, te_score in [
        ("latent", pred_train, pred_test),
        ("tail_weight", np.abs(tail_train), np.abs(tail_test)),
        ("base_q1", base_oof, base_q1_test),
    ]:
        for q in [0.35, 0.50, 0.65, 0.80]:
            for side in ["top", "bottom"]:
                tr_mask, te_mask, info = active_quantile_mask(tr_score, te_score, active_train, active_test, q, side)
                masks.append(
                    {
                        "mask_name": f"{score_name}_{side}{int(q * 100)}",
                        "train_mask": tr_mask,
                        "test_mask": te_mask,
                        "family": score_name,
                        **info,
                    }
                )

    for condition in ["weekend", "weekday", "month_start", "salary_end", "midmonth"]:
        tr_cond = calendar_condition(train, condition)
        te_cond = calendar_condition(test, condition)
        masks.append(
            {
                "mask_name": f"calendar_keep_{condition}",
                "train_mask": active_train & tr_cond,
                "test_mask": active_test & te_cond,
                "family": "calendar_keep",
            }
        )
        masks.append(
            {
                "mask_name": f"calendar_drop_{condition}",
                "train_mask": active_train & ~tr_cond,
                "test_mask": active_test & ~te_cond,
                "family": "calendar_drop",
            }
        )

    for subject in sorted(set(test["subject_id"].astype(str))):
        tr_sub = train["subject_id"].astype(str).to_numpy() == subject
        te_sub = test["subject_id"].astype(str).to_numpy() == subject
        masks.append(
            {
                "mask_name": f"subject_drop_{subject}",
                "train_mask": active_train & ~tr_sub,
                "test_mask": active_test & ~te_sub,
                "family": "subject_drop",
            }
        )
        masks.append(
            {
                "mask_name": f"subject_keep_{subject}",
                "train_mask": active_train & tr_sub,
                "test_mask": active_test & te_sub,
                "family": "subject_keep",
            }
        )

    # Dateblock censors are restricted to blocks that carry non-trivial test
    # tail mass; this tests placement without exploding the candidate universe.
    block_mass = (
        pd.DataFrame(
            {
                "block": test["dateblock_group"].astype(str),
                "mass": np.abs(tail_test) * active_test.astype(float),
                "active": active_test.astype(int),
            }
        )
        .groupby("block", as_index=False)
        .agg(mass=("mass", "sum"), active=("active", "sum"))
        .query("active >= 2")
        .sort_values(["mass", "active"], ascending=[False, False])
        .head(18)
    )
    for block in block_mass["block"].astype(str):
        tr_block = train["dateblock_group"].astype(str).to_numpy() == block
        te_block = test["dateblock_group"].astype(str).to_numpy() == block
        masks.append(
            {
                "mask_name": f"dateblock_drop_{block}",
                "train_mask": active_train & ~tr_block,
                "test_mask": active_test & ~te_block,
                "family": "dateblock_drop",
            }
        )
        masks.append(
            {
                "mask_name": f"dateblock_keep_{block}",
                "train_mask": active_train & tr_block,
                "test_mask": active_test & te_block,
                "family": "dateblock_keep",
            }
        )

    out: list[dict[str, Any]] = []
    seen: set[tuple[bytes, bytes, str]] = set()
    for rec in masks:
        tr = np.asarray(rec["train_mask"], dtype=bool)
        te = np.asarray(rec["test_mask"], dtype=bool)
        if int(tr.sum()) < 8 or int(te.sum()) < 3:
            continue
        key = (np.packbits(tr).tobytes(), np.packbits(te).tobytes(), str(rec["family"]))
        if key in seen:
            continue
        seen.add(key)
        rec["train_mask"] = tr
        rec["test_mask"] = te
        rec["train_rows"] = int(tr.sum())
        rec["test_rows"] = int(te.sum())
        out.append(rec)
    return out


def evaluate_row_censors(state: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(OUT / "e332_q1_tail_translator_summary.csv")
    source = source[source["gate"].astype(bool)].copy()
    source = source[source["policy"].isin(["pos_q75", "pos_q78", "pos_q80", "pos_q83", "pos_q85"])]
    source = source[source["style"].isin(["softplus", "const"])]
    source = source.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(10).reset_index(drop=True)

    train = state["train"]
    test = state["test"]
    pred_train = np.asarray(state["pred_train"], dtype=np.float64)
    pred_test = np.asarray(state["pred_test"], dtype=np.float64)
    base_oof = np.asarray(state["base_oof"], dtype=np.float64)
    y = np.asarray(state["y"], dtype=int)
    groups = state["groups"].reset_index(drop=True)
    base_q1_test = load_sub_frame(E247, test[KEYS])[TARGET].to_numpy(dtype=np.float64)
    base_loss = float(log_loss(y, base_oof, labels=[0, 1]))
    null_groups = {
        "row": groups,
        "subject": groups_for(train, "subject").reset_index(drop=True),
        "dateblock": groups_for(train, "dateblock").reset_index(drop=True),
    }

    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for _, src in source.iterrows():
        policy = str(src["policy"])
        style = str(src["style"])
        tail_train, tail_test = make_test_weights(pred_train, pred_test, policy, style, src)
        active_train = np.abs(tail_train) > EPS
        active_test = np.abs(tail_test) > EPS
        masks = build_masks(train, test, active_train, active_test, tail_train, tail_test, pred_train, pred_test, base_oof, base_q1_test)
        for mask_rec in masks:
            train_mask = np.asarray(mask_rec["train_mask"], dtype=bool)
            test_mask = np.asarray(mask_rec["test_mask"], dtype=bool)
            weights = tail_train * train_mask.astype(float)
            if np.max(np.abs(weights)) < EPS:
                continue
            loss, actual_delta, fold_d_mean, fold_d_std = cv_one_dim(base_oof, y, weights, groups)
            full_d, full_loss = optimize_scale(base_oof, y, weights)
            sign_ok = bool(full_d < 0.0)
            null_vals: list[float] = []
            rng = np.random.default_rng(stable_seed("row_censor_null", policy, style, mask_rec["mask_name"]))
            for mode, mgroups in null_groups.items():
                for rep in range(NULL_REPS):
                    shuffled = shuffled_feature(weights, mode, mgroups, rng)
                    _loss, null_delta, _dm, _ds = cv_one_dim(base_oof, y, shuffled, groups)
                    null_vals.append(null_delta)
                    null_rows.append(
                        {
                            "policy": policy,
                            "style": style,
                            "mask_name": mask_rec["mask_name"],
                            "family": mask_rec["family"],
                            "mode": mode,
                            "rep": rep,
                            "null_delta": null_delta,
                        }
                    )
            null_arr = np.asarray(null_vals, dtype=np.float64)
            dominance = float(np.mean(actual_delta < null_arr))
            placebo_adjusted = float(actual_delta - np.median(null_arr))
            gate = bool(sign_ok and actual_delta < -0.0005 and dominance >= 0.80 and placebo_adjusted < -0.00025)
            rows.append(
                {
                    "target": TARGET,
                    "policy": policy,
                    "style": style,
                    "mask_name": mask_rec["mask_name"],
                    "family": mask_rec["family"],
                    "source_actual_delta": float(src["actual_delta"]),
                    "source_dominance": float(src["dominance"]),
                    "base_loss": base_loss,
                    "cv_loss": loss,
                    "actual_delta": actual_delta,
                    "full_fit_loss": float(full_loss),
                    "full_d": float(full_d),
                    "fold_d_mean": fold_d_mean,
                    "fold_d_std": fold_d_std,
                    "null_best": float(np.min(null_arr)),
                    "null_median": float(np.median(null_arr)),
                    "null_q20": float(np.quantile(null_arr, 0.20)),
                    "dominance": dominance,
                    "placebo_adjusted_vs_median": placebo_adjusted,
                    "source_train_rows": int(active_train.sum()),
                    "source_test_rows": int(active_test.sum()),
                    "train_rows": int(train_mask.sum()),
                    "test_rows": int(test_mask.sum()),
                    "sign_ok": sign_ok,
                    "gate": gate,
                    "threshold": float(src["threshold"]) if "threshold" in src.index and pd.notna(src["threshold"]) else np.nan,
                    "threshold_lo": float(src["threshold_lo"]) if "threshold_lo" in src.index and pd.notna(src["threshold_lo"]) else np.nan,
                    "threshold_hi": float(src["threshold_hi"]) if "threshold_hi" in src.index and pd.notna(src["threshold_hi"]) else np.nan,
                    "mask_threshold": float(mask_rec["mask_threshold"]) if "mask_threshold" in mask_rec and pd.notna(mask_rec["mask_threshold"]) else np.nan,
                }
            )
    summary = pd.DataFrame(rows).sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]).reset_index(drop=True)
    nulls = pd.DataFrame(null_rows)
    gated = summary[summary["gate"].astype(bool)].copy()
    if gated.empty:
        selected = summary[(summary["sign_ok"].astype(bool)) & (summary["actual_delta"] < 0) & (summary["dominance"] >= 0.65)].head(MAX_MATERIALIZE // len(SCALES)).copy()
    else:
        # keep diversity by family before filling with best local rows
        diverse = gated.sort_values(["actual_delta", "dominance"], ascending=[True, False]).groupby("family", as_index=False).head(3)
        fill = gated[~gated.index.isin(diverse.index)].sort_values(["actual_delta", "dominance"], ascending=[True, False])
        selected = pd.concat([diverse, fill], axis=0).head(MAX_MATERIALIZE // len(SCALES)).reset_index(drop=True)
    return summary, nulls, selected.reset_index(drop=True)


def reconstruct_mask(state: dict[str, Any], rec: pd.Series) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    train = state["train"]
    test = state["test"]
    pred_train = np.asarray(state["pred_train"], dtype=np.float64)
    pred_test = np.asarray(state["pred_test"], dtype=np.float64)
    base_oof = np.asarray(state["base_oof"], dtype=np.float64)
    base_q1_test = load_sub_frame(E247, test[KEYS])[TARGET].to_numpy(dtype=np.float64)
    tail_train, tail_test = make_test_weights(pred_train, pred_test, str(rec["policy"]), str(rec["style"]), rec)
    active_train = np.abs(tail_train) > EPS
    active_test = np.abs(tail_test) > EPS
    masks = build_masks(train, test, active_train, active_test, tail_train, tail_test, pred_train, pred_test, base_oof, base_q1_test)
    for mask_rec in masks:
        if str(mask_rec["mask_name"]) == str(rec["mask_name"]) and str(mask_rec["family"]) == str(rec["family"]):
            return tail_train, tail_test, np.asarray(mask_rec["train_mask"], dtype=bool), np.asarray(mask_rec["test_mask"], dtype=bool)
    raise RuntimeError(f"mask not found: {rec['mask_name']}")


def write_submission(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e334_q1rowcensor_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(state: dict[str, Any], selected: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], pd.DataFrame]:
    if selected.empty:
        return pd.DataFrame(), [], pd.DataFrame()
    test = state["test"]
    base = load_sub_frame(E247, test[KEYS])
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    target_idx = TARGETS.index(TARGET)
    base_oof = np.asarray(state["base_oof"], dtype=np.float64)
    y = np.asarray(state["y"], dtype=int)
    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for _, rec in selected.iterrows():
        tail_train, tail_test, train_mask, test_mask = reconstruct_mask(state, rec)
        train_weights = tail_train * train_mask.astype(float)
        test_weights = tail_test * test_mask.astype(float)
        if np.max(np.abs(test_weights)) < EPS:
            continue
        full_d, full_loss = optimize_scale(base_oof, y, train_weights)
        raw_move = np.clip(full_d * test_weights, -CAP, CAP)
        raw_train_move = np.clip(full_d * train_weights, -CAP, CAP)
        for scale in SCALES:
            move = np.clip(scale * raw_move, -CAP, CAP)
            if np.max(np.abs(move)) < EPS:
                continue
            logits = base_logits.copy()
            logits[:, target_idx] += move
            cid = f"{rec['policy']}_{rec['style']}_{rec['mask_name']}_s{str(scale).replace('.', 'p')}"
            path = write_submission(base, logits, cid)
            paths.append(path)
            rows.append(
                {
                    "candidate_id": cid,
                    "file": rel(path),
                    "basename": path.name,
                    "target": TARGET,
                    "policy": str(rec["policy"]),
                    "style": str(rec["style"]),
                    "mask_name": str(rec["mask_name"]),
                    "family": str(rec["family"]),
                    "scale": float(scale),
                    "source_actual_delta": float(rec["actual_delta"]),
                    "source_dominance": float(rec["dominance"]),
                    "source_full_d": float(full_d),
                    "source_full_loss": float(full_loss),
                    "train_rows": int(train_mask.sum()),
                    "test_rows": int(test_mask.sum()),
                    "changed_rows": int(np.count_nonzero(np.abs(move) > EPS)),
                    "changed_cells": int(np.count_nonzero(np.abs(move) > EPS)),
                    "mean_abs_logit_move": float(np.mean(np.abs(move))),
                    "max_abs_logit_move": float(np.max(np.abs(move))),
                    "train_mean_abs_delta": float(np.mean(np.abs(raw_train_move))),
                }
            )
    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out, paths, base


def score_candidate_files(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        return pd.DataFrame()
    sample = load_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [rel(path) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path], base: pd.DataFrame) -> pd.DataFrame:
    if not paths:
        return pd.DataFrame()
    current = logit(base[TARGETS].to_numpy(dtype=np.float64))
    e323 = logit(load_sub_frame(E323, base[KEYS])[TARGETS].to_numpy(dtype=np.float64))
    bad = e323 - current
    rows = []
    for path in paths:
        cand = load_sub_frame(path, base[KEYS])
        move = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - current
        denom = float(np.linalg.norm(move) * np.linalg.norm(bad) + EPS)
        rows.append(
            {
                "basename": path.name,
                "changed_rows": int(np.any(np.abs(move) > EPS, axis=1).sum()),
                "changed_cells": int((np.abs(move) > EPS).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(cand[TARGETS].to_numpy(dtype=np.float64) - base[TARGETS].to_numpy(dtype=np.float64)))),
                "cos_with_e323_bad_delta": float(np.sum(move * bad) / denom) if denom else 0.0,
                "l1_ratio_to_e323_delta": float(np.sum(np.abs(move)) / (np.sum(np.abs(bad)) + EPS)),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad_delta", "l1_ratio_to_e323_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def aligned_test_meta(sample: pd.DataFrame) -> pd.DataFrame:
    _train, test_meta, _train_views, _test_views = train_test_state()
    meta = test_meta[KEYS + ["dateblock_group"]].copy()
    sample_keys = sample.copy()
    for frame in [sample_keys, meta]:
        for col in ["sleep_date", "lifelog_date"]:
            frame[col] = pd.to_datetime(frame[col]).dt.strftime("%Y-%m-%d")
    meta = sample_keys.merge(meta, on=KEYS, how="left", validate="one_to_one")
    if meta["dateblock_group"].isna().any():
        raise RuntimeError("E334 movement-null metadata does not align with E247 sample")
    return meta


def write_movement_null(path: Path, base: pd.DataFrame, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(stable_seed("move_null", path.name, mode, rep))
    current = logit(base[TARGETS].to_numpy(dtype=np.float64))
    cand = load_sub_frame(path, base[KEYS])
    delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - current
    shuffled = np.zeros_like(delta)
    if mode == "row":
        shuffled = delta[rng.permutation(len(delta))]
    elif mode == "subject":
        for _, idx in meta.groupby("subject_id").indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            shuffled[idx_arr] = delta[idx_arr][rng.permutation(len(idx_arr))]
    elif mode == "dateblock":
        for _, idx in meta.groupby("dateblock_group").indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            shuffled[idx_arr] = delta[idx_arr][rng.permutation(len(idx_arr))]
    else:
        raise ValueError(mode)
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(current + shuffled))
    NULL_DIR.mkdir(exist_ok=True)
    path_out = NULL_DIR / f"submission_e334null_{path.stem.replace('submission_', '')[:82]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path_out, index=False)
    return path_out


def movement_null_stress(paths: list[Path], base: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    if not paths or scores.empty:
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    chosen = non_current.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(20)
    path_by_name = {p.name: p for p in paths}
    sample = load_sub(E247)[KEYS]
    meta = aligned_test_meta(sample)
    null_paths: list[Path] = []
    null_map: list[dict[str, object]] = []
    for _, rec in chosen.iterrows():
        path = path_by_name.get(str(rec["basename"]))
        if path is None:
            continue
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(MOVEMENT_NULL_REPS):
                npath = write_movement_null(path, base, meta, mode, rep)
                null_paths.append(npath)
                null_map.append({"basename": path.name, "null_basename": npath.name, "mode": mode, "rep": rep})
    if not null_paths:
        return pd.DataFrame()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_candidates = build_features([CURRENT] + [rel(p) for p in null_paths], sample, refs, ref_vecs)
    null_scores = score_candidates(known, null_candidates, model_df)
    score_cols = ["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]
    map_df = pd.DataFrame(null_map).merge(
        null_scores[score_cols].rename(columns={"basename": "null_basename"}),
        on="null_basename",
        how="left",
    )
    actual = non_current[score_cols].rename(
        columns={
            "pred_delta_vs_current_mean": "actual_mean",
            "pred_delta_vs_current_p90": "actual_p90",
            "pred_beats_current_rate": "actual_beats_rate",
            "strict_promote_gate": "actual_strict_promote",
        }
    )
    rows = []
    for basename, part in map_df.groupby("basename"):
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
                "null_strict_promote_rate": float(part["strict_promote_gate"].mean()),
            }
        )
    out = pd.DataFrame(rows).sort_values(
        ["actual_strict_promote", "actual_p90_dominance", "actual_p90"],
        ascending=[False, False, True],
    ).reset_index(drop=True)
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(summary: pd.DataFrame, selected: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame, move_null: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    scored = non_current.merge(candidates[["basename", "policy", "style", "mask_name", "family", "scale"]], on="basename", how="left") if len(non_current) and len(candidates) else pd.DataFrame()
    promoted = scored[scored["strict_promote_gate"].astype(bool)] if len(scored) else pd.DataFrame()
    e323_safe = anatomy[anatomy["cos_with_e323_bad_delta"] <= 0.05] if len(anatomy) else pd.DataFrame()
    safe_promoted = promoted[promoted["basename"].isin(set(e323_safe["basename"]))] if len(promoted) and len(e323_safe) else pd.DataFrame()
    move_safe = pd.DataFrame()
    if len(safe_promoted) and len(move_null):
        move_safe = safe_promoted.merge(move_null, on="basename", how="inner")
        move_safe = move_safe[
            (move_safe["actual_p90_dominance"] >= 0.80)
            & (move_safe["actual_mean_dominance"] >= 0.65)
            & (move_safe["null_strict_promote_rate"] <= 0.10)
        ]

    lines = [
        "# E334 Q1 Tail Row-Censor Action-Health Audit",
        "",
        "## Question",
        "",
        "E332 found Q1-tail direction but not visibility. E333 rejected broad non-tail compensation. Can row placement/censoring of the same Q1-tail action make it p90-safe and selector-visible?",
        "",
        "## Local Row-Censor Stress",
        "",
        md_table(summary, n=60, floatfmt=".9f") if len(summary) else "_none_",
        "",
        "## Selected Censors",
        "",
        md_table(selected, n=40, floatfmt=".9f") if len(selected) else "_none_",
        "",
        "## Candidate Probes",
        "",
        md_table(candidates, n=50, floatfmt=".9f") if len(candidates) else "_none_",
        "",
        "## Public-Free Selector Scores",
        "",
    ]
    if len(scored):
        cols = [
            "basename",
            "policy",
            "style",
            "mask_name",
            "family",
            "scale",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
        ]
        lines.append(md_table(scored[cols], n=90, floatfmt=".9f"))
    else:
        lines.append("_none_")
    lines.extend(["", "## E323 Anatomy", ""])
    lines.append(md_table(anatomy, n=60, floatfmt=".9f") if len(anatomy) else "_none_")
    lines.extend(["", "## Movement-Null Stress", ""])
    lines.append(md_table(move_null, n=60, floatfmt=".9f") if len(move_null) else "_none_")
    lines.extend(["", "## Decision", ""])
    if len(move_safe):
        best = move_safe.sort_values(["actual_p90", "actual_mean"]).iloc[0]
        lines.append(
            f"`{best['basename']}` survives selector, E323 anatomy, and movement-null stress. It needs one high-repetition confirmation before public use."
        )
    elif len(safe_promoted):
        lines.append("At least one row-censor candidate clears selector+E323, but movement-null stress blocks it. Do not submit.")
    elif int(summary["gate"].sum()) > 0:
        lines.append("Row-censoring produces local label/null gates, but no materialized candidate becomes selector-grade.")
    else:
        lines.append("No row-censor action survives local label/null stress.")
    lines.extend(
        [
            "",
            f"- local row-censor gates: `{int(summary['gate'].sum()) if len(summary) else 0}`",
            f"- generated candidates: `{len(candidates)}`",
            f"- selector-promoted candidates: `{int(promoted['strict_promote_gate'].sum()) if len(promoted) else 0}`",
            f"- selector+E323-safe candidates: `{len(safe_promoted)}`",
            f"- selector+E323+movement-null-safe candidates: `{len(move_safe)}`",
            "",
            "## Files",
            "",
            f"- `{SUMMARY_OUT.name}`",
            f"- `{NULL_OUT.name}`",
            f"- `{SELECTED_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    state = build_q1_state()
    summary, nulls, selected = evaluate_row_censors(state)
    summary.to_csv(SUMMARY_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    candidates, paths, base = materialize_candidates(state, selected)
    scores = score_candidate_files(paths)
    anatomy = candidate_anatomy(paths, base) if paths else pd.DataFrame()
    move_null = movement_null_stress(paths, base, scores) if paths else pd.DataFrame()
    write_report(summary, selected, candidates, scores, anatomy, move_null)
    print(REPORT_OUT)
    if len(summary):
        print(summary.head(25).round(9).to_string(index=False))
    if len(scores):
        cols = [
            "basename",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
        ]
        print(scores[~scores["basename"].eq(CURRENT)][cols].head(35).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
