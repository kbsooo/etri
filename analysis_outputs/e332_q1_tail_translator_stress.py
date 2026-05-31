#!/usr/bin/env python3
"""E332: Q1 residual-tail translator stress.

E331 localized the target-residual lifestyle latent, but the materialized
E247 edits were too small for submission. The cleanest object was:

    target=Q1, view=jepa_resid, split=dateblock, positive residual tail

This experiment keeps that latent fixed and tests the missing piece: the
translator from latent state to probability movement.

JEPA/data2vec interpretation:
    context view  -> Q1 base-residual state
    residual tail -> hidden lifestyle episode state
    translator    -> action representation, not raw reconstruction

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
NULL_DIR = OUT / "e332_q1_tail_translator_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, E323, clip_prob, load_sub_frame, md_table, safe_id, sigmoid  # noqa: E402
from e330_target_residual_lifestyle_latent import (  # noqa: E402
    base_label_matrix_all,
    fit_ridge_full_predict,
    groups_for,
    oof_proba,
    oof_ridge_scalar,
    shuffled_feature,
)
from e331_residual_state_localization import train_test_state  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 332
TARGET = "Q1"
VIEW_ID = "jepa_resid"
SPLIT_NAME = "dateblock"
NULL_REPS = 12
MOVEMENT_NULL_REPS = 10
MAX_SELECTED = 10
LOGIT_GRID = np.linspace(-0.55, 0.55, 221)
SCALES = [0.35, 0.50, 0.75, 1.00, 1.25, 1.60, 2.00]
LOGIT_CAP = 0.42
EPS = 1.0e-12

SUMMARY_OUT = OUT / "e332_q1_tail_translator_summary.csv"
NULL_OUT = OUT / "e332_q1_tail_translator_nulls.csv"
SELECTED_OUT = OUT / "e332_q1_tail_translator_selected.csv"
CANDIDATE_OUT = OUT / "e332_q1_tail_translator_candidates.csv"
SCORE_OUT = OUT / "e332_q1_tail_translator_candidate_scores.csv"
ANATOMY_OUT = OUT / "e332_q1_tail_translator_candidate_anatomy.csv"
MOVE_NULL_OUT = OUT / "e332_q1_tail_translator_movement_nulls.csv"
REPORT_OUT = OUT / "e332_q1_tail_translator_report.md"


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


def shifted_prob(base_prob: np.ndarray, shift: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + shift))


def optimize_scale(base_prob: np.ndarray, y: np.ndarray, weights: np.ndarray, grid: np.ndarray = LOGIT_GRID) -> tuple[float, float]:
    base_prob = clip_prob(base_prob)
    y = np.asarray(y, dtype=int)
    weights = np.asarray(weights, dtype=np.float64)
    if np.max(np.abs(weights)) < EPS:
        return 0.0, float(log_loss(y, base_prob, labels=[0, 1]))
    z = logit(base_prob)
    logits = z[None, :] + np.asarray(grid, dtype=np.float64)[:, None] * weights[None, :]
    probs = clip_prob(sigmoid(logits))
    y2 = y[None, :]
    losses = -np.mean(y2 * np.log(probs) + (1 - y2) * np.log(1.0 - probs), axis=1)
    best_idx = int(np.argmin(losses))
    return float(grid[best_idx]), float(losses[best_idx])


def cv_translator(base_prob: np.ndarray, y: np.ndarray, weights: np.ndarray, groups: pd.Series) -> tuple[np.ndarray, list[float], float]:
    groups = groups.reset_index(drop=True)
    pred = base_prob.copy()
    deltas = np.zeros(len(y), dtype=np.float64)
    fold_ds: list[float] = []
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    for tr_idx, va_idx in cv.split(np.zeros((len(y), 1)), y, groups):
        d, _loss = optimize_scale(base_prob[tr_idx], y[tr_idx], weights[tr_idx])
        fold_ds.append(float(d))
        shift = np.clip(d * weights[va_idx], -LOGIT_CAP, LOGIT_CAP)
        deltas[va_idx] = shift
        pred[va_idx] = shifted_prob(base_prob[va_idx], shift)
    return pred, fold_ds, float(log_loss(y, pred, labels=[0, 1]))


def policy_threshold(train_score: np.ndarray, policy: str) -> tuple[np.ndarray, dict[str, float]]:
    score = np.asarray(train_score, dtype=np.float64)
    info: dict[str, float] = {}
    if policy.startswith("pos_q"):
        q = float(policy.replace("pos_q", "")) / 100.0
        threshold = float(np.quantile(score, q))
        gate = score >= threshold
        info["threshold"] = threshold
        return gate, info
    if policy.startswith("band_q"):
        lo_s, hi_s = policy.replace("band_q", "").split("_q")
        lo = float(lo_s) / 100.0
        hi = float(hi_s) / 100.0
        lo_t = float(np.quantile(score, lo))
        hi_t = float(np.quantile(score, hi))
        gate = (score >= lo_t) & (score < hi_t)
        info["threshold_lo"] = lo_t
        info["threshold_hi"] = hi_t
        return gate, info
    raise ValueError(policy)


def apply_policy(score: np.ndarray, policy: str, info: dict[str, float]) -> np.ndarray:
    score = np.asarray(score, dtype=np.float64)
    if policy.startswith("pos_q"):
        return score >= float(info["threshold"])
    if policy.startswith("band_q"):
        return (score >= float(info["threshold_lo"])) & (score < float(info["threshold_hi"]))
    raise ValueError(policy)


def weights_for(score: np.ndarray, train_score: np.ndarray, gate: np.ndarray, policy: str, style: str, info: dict[str, float]) -> np.ndarray:
    score = np.asarray(score, dtype=np.float64)
    train_score = np.asarray(train_score, dtype=np.float64)
    gate = np.asarray(gate, dtype=bool)
    out = np.zeros(len(score), dtype=np.float64)
    if not np.any(gate):
        return out
    if style == "const":
        out[gate] = 1.0
        return out
    if policy.startswith("pos_q"):
        threshold = float(info["threshold"])
        denom = float(np.quantile(train_score, 0.99) - threshold)
        denom = denom if abs(denom) > EPS else float(np.std(train_score) + EPS)
        raw = np.clip((score - threshold) / denom, 0.0, 1.50)
    else:
        center = 0.5 * (float(info["threshold_lo"]) + float(info["threshold_hi"]))
        denom = float(abs(float(info["threshold_hi"]) - float(info["threshold_lo"])) + EPS)
        raw = np.clip(1.0 - np.abs(score - center) / denom, 0.0, 1.25)
    if style == "rank":
        out[gate] = np.clip(raw[gate], 0.05, 1.50)
    elif style == "softplus":
        out[gate] = np.clip(0.35 + raw[gate], 0.35, 1.85)
    else:
        raise ValueError(style)
    return out


def build_q1_state() -> dict[str, Any]:
    train, test, train_views, test_views = train_test_state()
    base_x_train, base_x_test = base_label_matrix_all(train, test)
    groups = groups_for(train, SPLIT_NAME).reset_index(drop=True)
    y = train[TARGET].astype(int).to_numpy()
    base_oof = oof_proba(base_x_train, y, groups)
    teacher = y.astype(float) - base_oof
    pred_train, _pred_full, student_r2 = oof_ridge_scalar(train_views[VIEW_ID], teacher, groups)
    pred_test = fit_ridge_full_predict(train_views[VIEW_ID], teacher, test_views[VIEW_ID])
    return {
        "train": train,
        "test": test,
        "base_x_train": base_x_train,
        "base_x_test": base_x_test,
        "groups": groups,
        "y": y,
        "base_oof": base_oof,
        "teacher": teacher,
        "pred_train": pred_train,
        "pred_test": pred_test,
        "student_r2": float(student_r2),
    }


def evaluate_translators(state: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pred_train = np.asarray(state["pred_train"], dtype=np.float64)
    base_oof = np.asarray(state["base_oof"], dtype=np.float64)
    y = np.asarray(state["y"], dtype=int)
    groups = state["groups"].reset_index(drop=True)
    base_loss = float(log_loss(y, base_oof, labels=[0, 1]))
    null_groups = {
        "row": groups,
        "subject": groups_for(state["train"], "subject").reset_index(drop=True),
        "dateblock": groups_for(state["train"], "dateblock").reset_index(drop=True),
    }
    policies = ["pos_q75", "pos_q78", "pos_q80", "pos_q83", "pos_q85", "pos_q88", "pos_q90", "pos_q92", "pos_q95", "band_q75_q90", "band_q80_q92"]
    styles = ["const", "rank", "softplus"]

    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    selected_payloads: list[dict[str, Any]] = []

    for policy in policies:
        train_gate, info = policy_threshold(pred_train, policy)
        if int(train_gate.sum()) < 10:
            continue
        for style in styles:
            weights = weights_for(pred_train, pred_train, train_gate, policy, style, info)
            if np.max(np.abs(weights)) < EPS:
                continue
            pred_cv, fold_ds, loss = cv_translator(base_oof, y, weights, groups)
            actual_delta = float(loss - base_loss)
            full_d, full_loss = optimize_scale(base_oof, y, weights)
            train_shift = np.clip(full_d * weights, -LOGIT_CAP, LOGIT_CAP)
            null_vals: list[float] = []
            rng = np.random.default_rng(stable_seed("translator_null", policy, style))
            for mode, mgroups in null_groups.items():
                for rep in range(NULL_REPS):
                    shuffled = shuffled_feature(weights, mode, mgroups, rng)
                    _p, _ds, null_loss = cv_translator(base_oof, y, shuffled, groups)
                    null_delta = float(null_loss - base_loss)
                    null_vals.append(null_delta)
                    null_rows.append(
                        {
                            "policy": policy,
                            "style": style,
                            "mode": mode,
                            "rep": rep,
                            "null_delta": null_delta,
                        }
                    )
            null_arr = np.asarray(null_vals, dtype=np.float64)
            dominance = float(np.mean(actual_delta < null_arr))
            placebo_adjusted = actual_delta - float(np.median(null_arr))
            gate = bool(actual_delta < -0.0005 and dominance >= 0.85 and placebo_adjusted < -0.00025)
            rec = {
                "target": TARGET,
                "view_id": VIEW_ID,
                "split": SPLIT_NAME,
                "policy": policy,
                "style": style,
                "student_r2": float(state["student_r2"]),
                "base_loss": base_loss,
                "cv_loss": loss,
                "actual_delta": actual_delta,
                "full_fit_loss": float(full_loss),
                "full_d": float(full_d),
                "fold_d_mean": float(np.mean(fold_ds)) if fold_ds else 0.0,
                "fold_d_std": float(np.std(fold_ds)) if fold_ds else 0.0,
                "null_best": float(np.min(null_arr)),
                "null_median": float(np.median(null_arr)),
                "null_q20": float(np.quantile(null_arr, 0.20)),
                "dominance": dominance,
                "placebo_adjusted_vs_median": placebo_adjusted,
                "train_rows": int(train_gate.sum()),
                "train_shift_mean_abs": float(np.mean(np.abs(train_shift))),
                "train_shift_max_abs": float(np.max(np.abs(train_shift))),
                "gate": gate,
                **info,
            }
            rows.append(rec)
            if gate:
                selected_payloads.append({**rec, "weights_train": weights, "info": info})

    summary = pd.DataFrame(rows).sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]).reset_index(drop=True)
    nulls = pd.DataFrame(null_rows)
    if selected_payloads:
        selected = pd.DataFrame([{k: v for k, v in item.items() if k not in {"weights_train", "info"}} for item in selected_payloads])
        selected = selected.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_SELECTED).reset_index(drop=True)
    else:
        selected = summary[(summary["actual_delta"] < 0.0) & (summary["dominance"] >= 0.75)].head(MAX_SELECTED).copy()
    return summary, nulls, selected


def make_test_weights(pred_train: np.ndarray, pred_test: np.ndarray, policy: str, style: str, row: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    info: dict[str, float] = {}
    for key in ["threshold", "threshold_lo", "threshold_hi"]:
        if key in row.index and pd.notna(row[key]):
            info[key] = float(row[key])
    train_gate = apply_policy(pred_train, policy, info)
    test_gate = apply_policy(pred_test, policy, info)
    train_weights = weights_for(pred_train, pred_train, train_gate, policy, style, info)
    test_weights = weights_for(pred_test, pred_train, test_gate, policy, style, info)
    return train_weights, test_weights


def write_submission(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e332_q1tail_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(state: dict[str, Any], selected: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], pd.DataFrame]:
    train = state["train"]
    test = state["test"]
    base = load_sub_frame(E247, test[KEYS])
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    target_idx = TARGETS.index(TARGET)
    pred_train = np.asarray(state["pred_train"], dtype=np.float64)
    pred_test = np.asarray(state["pred_test"], dtype=np.float64)
    base_oof = np.asarray(state["base_oof"], dtype=np.float64)
    y = np.asarray(state["y"], dtype=int)

    paths: list[Path] = []
    rows: list[dict[str, Any]] = []
    for _, row in selected.iterrows():
        policy = str(row["policy"])
        style = str(row["style"])
        train_weights, test_weights = make_test_weights(pred_train, pred_test, policy, style, row)
        if int(np.count_nonzero(test_weights)) == 0:
            continue
        full_d, full_loss = optimize_scale(base_oof, y, train_weights)
        raw_test_delta = np.clip(full_d * test_weights, -LOGIT_CAP, LOGIT_CAP)
        raw_train_delta = np.clip(full_d * train_weights, -LOGIT_CAP, LOGIT_CAP)
        if np.max(np.abs(raw_test_delta)) < EPS:
            continue
        # Wrong-sign controls are generated for the two strongest selected rows
        # to detect whether the selector only likes Q1 movement magnitude.
        control_allowed = len(rows) < 2
        for scale in SCALES:
            for sign_name, sign in [("actual", 1.0), ("signflip", -1.0)]:
                if sign_name == "signflip" and not control_allowed:
                    continue
                logits = base_logits.copy()
                move = np.clip(sign * scale * raw_test_delta, -LOGIT_CAP, LOGIT_CAP)
                logits[:, target_idx] += move
                cid = f"{policy}_{style}_{sign_name}_s{str(scale).replace('.', 'p')}"
                path = write_submission(base, logits, cid)
                paths.append(path)
                rows.append(
                    {
                        "candidate_id": cid,
                        "file": rel(path),
                        "basename": path.name,
                        "target": TARGET,
                        "view_id": VIEW_ID,
                        "split": SPLIT_NAME,
                        "policy": policy,
                        "style": style,
                        "sign": sign_name,
                        "scale": scale,
                        "source_actual_delta": float(row["actual_delta"]),
                        "source_dominance": float(row["dominance"]),
                        "source_full_d": float(full_d),
                        "source_full_loss": float(full_loss),
                        "train_rows": int(np.count_nonzero(train_weights)),
                        "test_rows": int(np.count_nonzero(test_weights)),
                        "changed_rows": int(np.count_nonzero(np.abs(move) > EPS)),
                        "changed_cells": int(np.count_nonzero(np.abs(move) > EPS)),
                        "mean_abs_logit_move": float(np.mean(np.abs(move))),
                        "max_abs_logit_move": float(np.max(np.abs(move))),
                        "train_mean_abs_delta": float(np.mean(np.abs(raw_train_delta))),
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
    path_out = NULL_DIR / f"submission_e332null_{path.stem.replace('submission_', '')[:82]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path_out, index=False)
    return path_out


def movement_null_stress(paths: list[Path], base: pd.DataFrame, scores: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    if not paths or scores.empty:
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    actual_only = candidates[candidates["sign"].eq("actual")]["basename"].astype(str)
    non_current = non_current[non_current["basename"].isin(set(actual_only))]
    chosen = non_current.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(18)
    path_by_name = {p.name: p for p in paths}
    sample = load_sub(E247)[KEYS]
    _train, test_meta, _train_views, _test_views = train_test_state()
    meta = test_meta[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        meta[col] = pd.to_datetime(meta[col])
    if not meta[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise RuntimeError("E332 movement-null metadata does not align with E247 sample")
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
    out = pd.DataFrame(rows).sort_values(["actual_strict_promote", "actual_p90_dominance", "actual_p90"], ascending=[False, False, True]).reset_index(drop=True)
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(summary: pd.DataFrame, nulls: pd.DataFrame, selected: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame, move_null: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    actual_scores = non_current.merge(candidates[["basename", "sign", "policy", "style", "scale"]], on="basename", how="left") if len(non_current) and len(candidates) else pd.DataFrame()
    actual_only = actual_scores[actual_scores["sign"].eq("actual")] if len(actual_scores) else pd.DataFrame()
    signflip = actual_scores[actual_scores["sign"].eq("signflip")] if len(actual_scores) else pd.DataFrame()
    promoted = actual_only[actual_only["strict_promote_gate"].astype(bool)] if len(actual_only) else pd.DataFrame()
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
        "# E332 Q1 Tail Translator Stress",
        "",
        "## Question",
        "",
        "E331 found a clean Q1 positive residual-tail latent but no submission-grade action. Can a direct OOF-trained logit-shift translator make that latent visible while preserving E247 and avoiding E323?",
        "",
        "## Translator Stress",
        "",
        md_table(summary, n=40, floatfmt=".9f"),
        "",
        "## Selected Translators",
        "",
        md_table(selected, n=20, floatfmt=".9f") if len(selected) else "_none_",
        "",
        "## Candidate Probes",
        "",
        md_table(candidates, n=50, floatfmt=".9f") if len(candidates) else "_none_",
        "",
        "## Public-Free Selector Scores: Actual Direction",
        "",
    ]
    if len(actual_only):
        cols = [
            "basename",
            "policy",
            "style",
            "scale",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
        ]
        lines.append(md_table(actual_only[cols], n=60, floatfmt=".9f"))
    else:
        lines.append("_none_")
    lines.extend(["", "## Signflip Controls", ""])
    if len(signflip):
        cols = [
            "basename",
            "policy",
            "style",
            "scale",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
        ]
        lines.append(md_table(signflip[cols], n=30, floatfmt=".9f"))
    else:
        lines.append("_none_")
    lines.extend(["", "## E323-Negative Anatomy", ""])
    lines.append(md_table(anatomy, n=60, floatfmt=".9f") if len(anatomy) else "_none_")
    lines.extend(["", "## Movement-Null Stress", ""])
    lines.append(md_table(move_null, n=40, floatfmt=".9f") if len(move_null) else "_none_")
    lines.extend(["", "## Decision", ""])
    if len(move_safe):
        best = move_safe.sort_values(["actual_p90", "actual_mean"]).iloc[0]
        lines.append(
            f"`{best['basename']}` survives actual-direction selector, E323-negative anatomy, and movement-null stress. Treat it as a candidate for one additional high-repetition stress before public submission."
        )
    elif len(safe_promoted):
        lines.append(
            "Some actual-direction candidates clear the selector and E323 anatomy, but movement-null stress blocks them. Do not submit without a stronger placement invariant."
        )
    elif int(summary["gate"].sum()) > 0:
        lines.append(
            "Q1 tail translators survive local label/null stress, but none become selector-grade after E247 materialization. The bottleneck is still action visibility."
        )
    else:
        lines.append(
            "No Q1 tail translator survives train label/null stress. This rejects the direct logit-shift translator before submission scoring."
        )
    lines.extend(
        [
            "",
            f"- local translator gates: `{int(summary['gate'].sum()) if len(summary) else 0}`",
            f"- generated candidates: `{len(candidates)}`",
            f"- actual-direction selector-promoted candidates: `{int(promoted['strict_promote_gate'].sum()) if len(promoted) else 0}`",
            f"- selector+E323-safe actual candidates: `{len(safe_promoted)}`",
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
    summary, nulls, selected = evaluate_translators(state)
    candidates, paths, base = materialize_candidates(state, selected)
    scores = score_candidate_files(paths)
    anatomy = candidate_anatomy(paths, base)
    move_null = movement_null_stress(paths, base, scores, candidates)

    summary.to_csv(SUMMARY_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(summary, nulls, selected, candidates, scores, anatomy, move_null)

    print(REPORT_OUT)
    print("[summary]")
    print(summary.head(30).round(9).to_string(index=False))
    if len(scores):
        view = scores[~scores["basename"].eq(CURRENT)].copy()
        print("[scores]")
        print(view[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate"]].head(40).round(9).to_string(index=False))
    if len(move_null):
        print("[move_null]")
        print(move_null.head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
