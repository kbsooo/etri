#!/usr/bin/env python3
"""E333: Q1 contrastive action translator.

E332 showed a clean but underpowered fact:

    Q1 jepa_resid/dateblock positive-tail state is directional,
    but direct scalar translation is not submission-grade.

This experiment changes the translator target, not the latent.  Instead of
"move Q1 tail rows down harder", it asks whether Q1 tail movement needs a
contrastive background component to stay visible and p90-safe.

JEPA/data2vec interpretation:
    context latent       -> Q1 residual-tail lifestyle state
    target representation -> contrast between tail and non-tail/background state
    action health         -> selector-visible, E323-negative, movement-null rare

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
NULL_DIR = OUT / "e333_q1_contrastive_action_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, E323, clip_prob, load_sub_frame, md_table, safe_id, sigmoid  # noqa: E402
from e330_target_residual_lifestyle_latent import groups_for, shuffled_feature  # noqa: E402
from e331_residual_state_localization import train_test_state  # noqa: E402
from e332_q1_tail_translator_stress import (  # noqa: E402
    TARGET,
    VIEW_ID,
    SPLIT_NAME,
    build_q1_state,
    make_test_weights,
    optimize_scale,
    shifted_prob,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 333
NULL_REPS = 8
MOVEMENT_NULL_REPS = 8
MAX_TRANSLATORS = 14
EPS = 1.0e-12
CAP = 0.42
SCALES = [0.25, 0.35, 0.50, 0.75, 1.00, 1.25]

SUMMARY_OUT = OUT / "e333_q1_contrastive_action_summary.csv"
NULL_OUT = OUT / "e333_q1_contrastive_action_nulls.csv"
SELECTED_OUT = OUT / "e333_q1_contrastive_action_selected.csv"
CANDIDATE_OUT = OUT / "e333_q1_contrastive_action_candidates.csv"
SCORE_OUT = OUT / "e333_q1_contrastive_action_candidate_scores.csv"
ANATOMY_OUT = OUT / "e333_q1_contrastive_action_candidate_anatomy.csv"
MOVE_NULL_OUT = OUT / "e333_q1_contrastive_action_movement_nulls.csv"
REPORT_OUT = OUT / "e333_q1_contrastive_action_report.md"


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


def normalize_component(x: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.asarray(x, dtype=np.float64).copy()
    out[~np.asarray(mask, dtype=bool)] = 0.0
    if np.max(np.abs(out)) < EPS:
        return out
    pos = np.abs(out) > EPS
    scale = float(np.mean(np.abs(out[pos])))
    if scale < EPS:
        return out
    out = out / scale
    return np.clip(out, -2.0, 2.0)


def background_component(
    score_train: np.ndarray,
    score_test: np.ndarray,
    tail_train: np.ndarray,
    tail_test: np.ndarray,
    name: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    tr = np.asarray(score_train, dtype=np.float64)
    te = np.asarray(score_test, dtype=np.float64)
    tail_train = np.asarray(tail_train, dtype=bool)
    tail_test = np.asarray(tail_test, dtype=bool)
    info: dict[str, float] = {}

    if name == "none":
        return np.zeros_like(tr), np.zeros_like(te), info
    if name == "nontail_all":
        tr_mask = ~tail_train
        te_mask = ~tail_test
        tr_raw = np.ones_like(tr)
        te_raw = np.ones_like(te)
    elif name.startswith("low_q"):
        q = float(name.replace("low_q", "")) / 100.0
        thr = float(np.quantile(tr, q))
        info["bg_threshold"] = thr
        tr_mask = tr <= thr
        te_mask = te <= thr
        tr_raw = np.ones_like(tr)
        te_raw = np.ones_like(te)
    elif name.startswith("mid_q"):
        lo_s, hi_s = name.replace("mid_q", "").split("_q")
        lo = float(lo_s) / 100.0
        hi = float(hi_s) / 100.0
        lo_t = float(np.quantile(tr, lo))
        hi_t = float(np.quantile(tr, hi))
        info["bg_threshold_lo"] = lo_t
        info["bg_threshold_hi"] = hi_t
        tr_mask = (tr >= lo_t) & (tr <= hi_t) & ~tail_train
        te_mask = (te >= lo_t) & (te <= hi_t) & ~tail_test
        center = 0.5 * (lo_t + hi_t)
        denom = abs(hi_t - lo_t) + EPS
        tr_raw = 1.0 - np.abs(tr - center) / denom
        te_raw = 1.0 - np.abs(te - center) / denom
    elif name.startswith("ring_q"):
        lo = float(name.replace("ring_q", "")) / 100.0
        lo_t = float(np.quantile(tr, lo))
        tail_lo = float(np.min(tr[tail_train])) if np.any(tail_train) else float(np.quantile(tr, 0.80))
        info["bg_threshold_lo"] = lo_t
        info["bg_threshold_hi"] = tail_lo
        tr_mask = (tr >= lo_t) & (tr < tail_lo) & ~tail_train
        te_mask = (te >= lo_t) & (te < tail_lo) & ~tail_test
        denom = abs(tail_lo - lo_t) + EPS
        tr_raw = np.clip((tr - lo_t) / denom, 0.0, 1.0)
        te_raw = np.clip((te - lo_t) / denom, 0.0, 1.0)
    else:
        raise ValueError(name)

    return normalize_component(tr_raw, tr_mask), normalize_component(te_raw, te_mask), info


def rho_values(tail_train: np.ndarray, bg_train: np.ndarray) -> list[tuple[str, float]]:
    vals: list[tuple[str, float]] = [("same025", 0.25), ("opp025", -0.25), ("opp050", -0.50), ("opp075", -0.75), ("opp100", -1.00)]
    tail_mass = float(np.sum(np.abs(tail_train)))
    bg_mass = float(np.sum(np.abs(bg_train)))
    if bg_mass > EPS:
        neutral = -tail_mass / bg_mass
        vals.append(("massneutral", float(np.clip(neutral, -1.25, -0.05))))
    vals.append(("direct000", 0.0))
    seen: set[str] = set()
    out: list[tuple[str, float]] = []
    for name, value in vals:
        if name in seen:
            continue
        seen.add(name)
        out.append((name, value))
    return out


def cv_one_dim(base_prob: np.ndarray, y: np.ndarray, weights: np.ndarray, groups: pd.Series) -> tuple[float, float, float, float]:
    base_loss = float(log_loss(y, base_prob, labels=[0, 1]))
    pred = base_prob.copy()
    ds: list[float] = []
    cv = GroupKFold(n_splits=min(5, int(groups.nunique())))
    for tr_idx, va_idx in cv.split(np.zeros((len(y), 1)), y, groups.reset_index(drop=True)):
        d, _loss = optimize_scale(base_prob[tr_idx], y[tr_idx], weights[tr_idx])
        ds.append(float(d))
        shift = np.clip(d * weights[va_idx], -CAP, CAP)
        pred[va_idx] = shifted_prob(base_prob[va_idx], shift)
    loss = float(log_loss(y, pred, labels=[0, 1]))
    return loss, loss - base_loss, float(np.mean(ds)) if ds else 0.0, float(np.std(ds)) if ds else 0.0


def evaluate_translators(state: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    source = pd.read_csv(OUT / "e332_q1_tail_translator_summary.csv")
    source = source[source["gate"].astype(bool)].copy()
    source = source[source["policy"].isin(["pos_q75", "pos_q78", "pos_q80", "pos_q83", "pos_q85", "pos_q90"])]
    source = source[source["style"].isin(["const", "softplus", "rank"])]
    source = source.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(12).reset_index(drop=True)

    pred_train = np.asarray(state["pred_train"], dtype=np.float64)
    pred_test = np.asarray(state["pred_test"], dtype=np.float64)
    base_oof = np.asarray(state["base_oof"], dtype=np.float64)
    y = np.asarray(state["y"], dtype=int)
    groups = state["groups"].reset_index(drop=True)
    base_loss = float(log_loss(y, base_oof, labels=[0, 1]))
    null_groups = {
        "row": groups,
        "subject": groups_for(state["train"], "subject").reset_index(drop=True),
        "dateblock": groups_for(state["train"], "dateblock").reset_index(drop=True),
    }
    bg_names = ["none", "nontail_all", "low_q25", "low_q35", "mid_q25_q65", "mid_q35_q75", "ring_q50", "ring_q65"]

    rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for _, src in source.iterrows():
        policy = str(src["policy"])
        style = str(src["style"])
        tail_train, tail_test = make_test_weights(pred_train, pred_test, policy, style, src)
        tail_mask_train = np.abs(tail_train) > EPS
        tail_mask_test = np.abs(tail_test) > EPS
        if int(tail_mask_train.sum()) < 10 or int(tail_mask_test.sum()) < 3:
            continue
        tail_train_n = normalize_component(tail_train, tail_mask_train)
        tail_test_n = normalize_component(tail_test, tail_mask_test)
        for bg_name in bg_names:
            bg_train, _bg_test, bg_info = background_component(pred_train, pred_test, tail_mask_train, tail_mask_test, bg_name)
            if bg_name != "none" and int(np.count_nonzero(np.abs(bg_train) > EPS)) < 10:
                continue
            for rho_name, rho in rho_values(tail_train_n, bg_train):
                if bg_name == "none" and abs(rho) > EPS:
                    continue
                if bg_name != "none" and rho_name == "direct000":
                    continue
                weights = tail_train_n + float(rho) * bg_train
                if np.max(np.abs(weights)) < EPS:
                    continue
                loss, actual_delta, fold_d_mean, fold_d_std = cv_one_dim(base_oof, y, weights, groups)
                full_d, full_loss = optimize_scale(base_oof, y, weights)
                if full_d >= 0:
                    sign_ok = False
                else:
                    sign_ok = True
                null_vals: list[float] = []
                rng = np.random.default_rng(stable_seed("contrast_null", policy, style, bg_name, rho_name))
                for mode, mgroups in null_groups.items():
                    for rep in range(NULL_REPS):
                        shuffled = shuffled_feature(weights, mode, mgroups, rng)
                        _loss, null_delta, _dm, _ds = cv_one_dim(base_oof, y, shuffled, groups)
                        null_vals.append(null_delta)
                        null_rows.append(
                            {
                                "policy": policy,
                                "style": style,
                                "background": bg_name,
                                "rho_name": rho_name,
                                "rho": float(rho),
                                "mode": mode,
                                "rep": rep,
                                "null_delta": null_delta,
                            }
                        )
                null_arr = np.asarray(null_vals, dtype=np.float64)
                dominance = float(np.mean(actual_delta < null_arr))
                placebo_adjusted = float(actual_delta - np.median(null_arr))
                gate = bool(sign_ok and actual_delta < -0.0005 and dominance >= 0.85 and placebo_adjusted < -0.00025)
                rows.append(
                    {
                        "target": TARGET,
                        "view_id": VIEW_ID,
                        "split": SPLIT_NAME,
                        "policy": policy,
                        "style": style,
                        "background": bg_name,
                        "rho_name": rho_name,
                        "rho": float(rho),
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
                        "tail_train_rows": int(tail_mask_train.sum()),
                        "tail_test_rows": int(tail_mask_test.sum()),
                        "bg_train_rows": int(np.count_nonzero(np.abs(bg_train) > EPS)),
                        "sign_ok": sign_ok,
                        "gate": gate,
                        "threshold": float(src["threshold"]) if "threshold" in src.index and pd.notna(src["threshold"]) else np.nan,
                        "threshold_lo": float(src["threshold_lo"]) if "threshold_lo" in src.index and pd.notna(src["threshold_lo"]) else np.nan,
                        "threshold_hi": float(src["threshold_hi"]) if "threshold_hi" in src.index and pd.notna(src["threshold_hi"]) else np.nan,
                        **bg_info,
                    }
                )
    summary = pd.DataFrame(rows).sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]).reset_index(drop=True)
    nulls = pd.DataFrame(null_rows)
    if int(summary["gate"].sum()) > 0:
        selected = summary[summary["gate"].astype(bool)].head(MAX_TRANSLATORS).copy()
    else:
        selected = summary[(summary["sign_ok"].astype(bool)) & (summary["actual_delta"] < 0) & (summary["dominance"] >= 0.75)].head(MAX_TRANSLATORS).copy()
    return summary, nulls, selected.reset_index(drop=True)


def write_submission(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e333_q1contrast_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(state: dict[str, Any], selected: pd.DataFrame) -> tuple[pd.DataFrame, list[Path], pd.DataFrame]:
    if selected.empty:
        return pd.DataFrame(), [], pd.DataFrame()
    test = state["test"]
    base = load_sub_frame(E247, test[KEYS])
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    target_idx = TARGETS.index(TARGET)
    pred_train = np.asarray(state["pred_train"], dtype=np.float64)
    pred_test = np.asarray(state["pred_test"], dtype=np.float64)
    base_oof = np.asarray(state["base_oof"], dtype=np.float64)
    y = np.asarray(state["y"], dtype=int)

    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for _, row in selected.iterrows():
        policy = str(row["policy"])
        style = str(row["style"])
        bg_name = str(row["background"])
        rho_name = str(row["rho_name"])
        rho = float(row["rho"])
        tail_train, tail_test = make_test_weights(pred_train, pred_test, policy, style, row)
        tail_train_n = normalize_component(tail_train, np.abs(tail_train) > EPS)
        tail_test_n = normalize_component(tail_test, np.abs(tail_test) > EPS)
        bg_train, bg_test, _info = background_component(pred_train, pred_test, np.abs(tail_train) > EPS, np.abs(tail_test) > EPS, bg_name)
        train_weights = tail_train_n + rho * bg_train
        test_weights = tail_test_n + rho * bg_test
        if np.max(np.abs(test_weights)) < EPS:
            continue
        full_d, full_loss = optimize_scale(base_oof, y, train_weights)
        raw_move = np.clip(full_d * test_weights, -CAP, CAP)
        raw_train_move = np.clip(full_d * train_weights, -CAP, CAP)
        if np.max(np.abs(raw_move)) < EPS:
            continue
        for scale in SCALES:
            logits = base_logits.copy()
            move = np.clip(scale * raw_move, -CAP, CAP)
            logits[:, target_idx] += move
            cid = f"{policy}_{style}_{bg_name}_{rho_name}_s{str(scale).replace('.', 'p')}"
            path = write_submission(base, logits, cid)
            paths.append(path)
            rows.append(
                {
                    "candidate_id": cid,
                    "file": rel(path),
                    "basename": path.name,
                    "target": TARGET,
                    "policy": policy,
                    "style": style,
                    "background": bg_name,
                    "rho_name": rho_name,
                    "rho": rho,
                    "scale": scale,
                    "source_actual_delta": float(row["actual_delta"]),
                    "source_dominance": float(row["dominance"]),
                    "source_full_d": float(full_d),
                    "source_full_loss": float(full_loss),
                    "tail_train_rows": int(row["tail_train_rows"]),
                    "tail_test_rows": int(row["tail_test_rows"]),
                    "bg_train_rows": int(row["bg_train_rows"]),
                    "changed_rows": int(np.count_nonzero(np.abs(move) > EPS)),
                    "changed_cells": int(np.count_nonzero(np.abs(move) > EPS)),
                    "mean_abs_logit_move": float(np.mean(np.abs(move))),
                    "max_abs_logit_move": float(np.max(np.abs(move))),
                    "train_mean_abs_delta": float(np.mean(np.abs(raw_train_move))),
                }
            )
    candidates = pd.DataFrame(rows)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths, base


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
    path_out = NULL_DIR / f"submission_e333null_{path.stem.replace('submission_', '')[:82]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path_out, index=False)
    return path_out


def movement_null_stress(paths: list[Path], base: pd.DataFrame, scores: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    if not paths or scores.empty or candidates.empty:
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    chosen = non_current.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).head(20)
    path_by_name = {p.name: p for p in paths}
    sample = load_sub(E247)[KEYS]
    _train, test_meta, _train_views, _test_views = train_test_state()
    meta = test_meta[KEYS + ["dateblock_group"]].copy()
    sample_keys = sample.copy()
    for frame in [sample_keys, meta]:
        for col in ["sleep_date", "lifelog_date"]:
            frame[col] = pd.to_datetime(frame[col]).dt.strftime("%Y-%m-%d")
    meta = sample_keys.merge(meta, on=KEYS, how="left", validate="one_to_one")
    if meta["dateblock_group"].isna().any():
        raise RuntimeError("E333 movement-null metadata does not align with E247 sample")

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
    scored = non_current.merge(candidates[["basename", "policy", "style", "background", "rho_name", "rho", "scale"]], on="basename", how="left") if len(non_current) and len(candidates) else pd.DataFrame()
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
        "# E333 Q1 Contrastive Action Translator",
        "",
        "## Question",
        "",
        "E332 proved the Q1 tail latent is directional but direct scalar shifts are not visible enough. Does a contrastive tail/background action make the same latent p90-safe and selector-visible?",
        "",
        "## Local Translator Stress",
        "",
        md_table(summary, n=50, floatfmt=".9f") if len(summary) else "_none_",
        "",
        "## Selected Translators",
        "",
        md_table(selected, n=30, floatfmt=".9f") if len(selected) else "_none_",
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
            "background",
            "rho_name",
            "scale",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
        ]
        lines.append(md_table(scored[cols], n=80, floatfmt=".9f"))
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
            f"`{best['basename']}` survives selector, E323 anatomy, and movement-null stress. It should get one high-repetition confirmation before any public use."
        )
    elif len(safe_promoted):
        lines.append("At least one contrastive action clears selector+E323, but movement-null stress blocks it. Do not submit.")
    elif int(summary["gate"].sum()) > 0:
        lines.append("Contrastive Q1 translators improve local label/null stress, but none become selector-grade after E247 materialization.")
    else:
        lines.append("Contrastive background components do not improve the Q1-tail translator enough to pass local translator gates.")
    lines.extend(
        [
            "",
            f"- local translator gates: `{int(summary['gate'].sum()) if len(summary) else 0}`",
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
    summary, nulls, selected = evaluate_translators(state)
    summary.to_csv(SUMMARY_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    candidates, paths, base = materialize_candidates(state, selected)
    scores = score_candidate_files(paths)
    anatomy = candidate_anatomy(paths, base) if paths else pd.DataFrame()
    move_null = movement_null_stress(paths, base, scores, candidates) if paths else pd.DataFrame()
    write_report(summary, selected, candidates, scores, anatomy, move_null)
    print(REPORT_OUT)
    if len(summary):
        print(summary.head(20).round(9).to_string(index=False))
    if len(scores):
        cols = [
            "basename",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
        ]
        print(scores[~scores["basename"].eq(CURRENT)][cols].head(30).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
