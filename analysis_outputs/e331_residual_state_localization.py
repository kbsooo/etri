#!/usr/bin/env python3
"""E331: residual-state localization.

E330 found target-specific lifestyle residual states, but diffuse target-wide
calibration did not become a public-free candidate. This experiment asks the
next JEPA/data2vec question:

    Can the residual state identify *where* the action belongs?

For each strong E330 residual-state row, we build localized features:
absolute tails, positive/negative tails, and dateblock tails. Each localized
feature must improve blocked train logloss and beat row/subject/dateblock
shuffled feature nulls before it is materialized on E247.

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


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e331_residual_state_localization_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import E247, E323, build_views, clip_prob, load_frames, load_sub_frame, md_table, safe_id, sigmoid  # noqa: E402
from e330_target_residual_lifestyle_latent import (  # noqa: E402
    base_label_matrix_all,
    cv_logloss,
    fit_logistic_predict,
    fit_ridge_full_predict,
    groups_for,
    oof_proba,
    oof_ridge_scalar,
    shuffled_feature,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


RNG_SEED = 20260531 + 331
NULL_REPS = 10
TOP_SOURCE_ROWS = 10
MAX_LOCAL_GATES = 14
SCALES = [0.40, 0.70, 1.00]
CAP = 0.085
MOVEMENT_NULL_REPS = 4
EPS = 1.0e-12

LOCAL_OUT = OUT / "e331_residual_state_localization_summary.csv"
LOCAL_NULL_OUT = OUT / "e331_residual_state_localization_feature_nulls.csv"
CANDIDATE_OUT = OUT / "e331_residual_state_localization_candidates.csv"
SCORE_OUT = OUT / "e331_residual_state_localization_candidate_scores.csv"
ANATOMY_OUT = OUT / "e331_residual_state_localization_candidate_anatomy.csv"
MOVE_NULL_OUT = OUT / "e331_residual_state_localization_movement_nulls.csv"
REPORT_OUT = OUT / "e331_residual_state_localization_report.md"


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


def train_test_state() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    frames = load_frames()
    state = frames["state"].copy()
    views = build_views(frames)
    train_idx = state.index[state["split"].eq("train")].to_numpy()
    test_idx = state.index[state["split"].eq("test")].to_numpy()
    test_idx = state.loc[test_idx].sort_values(KEYS).index.to_numpy()
    train = state.loc[train_idx].reset_index(drop=True)
    test = state.loc[test_idx].reset_index(drop=True)
    view_ids = ["family", "jepa_resid", "story_bundle", "raw_day", "family_story", "family_jepa_story"]
    train_views = {k: views[k].loc[train_idx].reset_index(drop=True) for k in view_ids}
    test_views = {k: views[k].loc[test_idx].reset_index(drop=True) for k in view_ids}
    return train, test, train_views, test_views


def source_rows() -> pd.DataFrame:
    src = pd.read_csv(OUT / "e330_target_residual_lifestyle_latent_summary.csv")
    gated = src[src["gate"].astype(bool)].copy()
    if gated.empty:
        gated = src[(src["actual_delta"] < 0.0) & (src["dominance"] >= 0.75)].copy()
    return gated.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(TOP_SOURCE_ROWS).reset_index(drop=True)


def policy_feature(
    pred_train: np.ndarray,
    pred_test: np.ndarray,
    train: pd.DataFrame,
    test: pd.DataFrame,
    policy: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict[str, object]]:
    tr = np.asarray(pred_train, dtype=np.float64)
    te = np.asarray(pred_test, dtype=np.float64)
    info: dict[str, object] = {"policy": policy}
    if policy.startswith("abs_q"):
        q = float(policy.replace("abs_q", "")) / 100.0
        threshold = float(np.quantile(np.abs(tr), q))
        tr_gate = np.abs(tr) >= threshold
        te_gate = np.abs(te) >= threshold
        tr_feat = tr * tr_gate
        te_feat = te * te_gate
        info["threshold"] = threshold
    elif policy.startswith("pos_q"):
        q = float(policy.replace("pos_q", "")) / 100.0
        threshold = float(np.quantile(tr, q))
        tr_gate = tr >= threshold
        te_gate = te >= threshold
        tr_feat = tr * tr_gate
        te_feat = te * te_gate
        info["threshold"] = threshold
    elif policy.startswith("neg_q"):
        q = float(policy.replace("neg_q", "")) / 100.0
        threshold = float(np.quantile(tr, 1.0 - q))
        tr_gate = tr <= threshold
        te_gate = te <= threshold
        tr_feat = tr * tr_gate
        te_feat = te * te_gate
        info["threshold"] = threshold
    elif policy.startswith("blockabs_q"):
        q = float(policy.replace("blockabs_q", "")) / 100.0
        train_block = pd.DataFrame({"block": train["dateblock_group"].astype(str), "score": np.abs(tr)})
        block_score = train_block.groupby("block")["score"].mean()
        threshold = float(np.quantile(block_score.to_numpy(dtype=np.float64), q))
        train_block_gate = train["dateblock_group"].astype(str).map((block_score >= threshold).to_dict()).fillna(False).to_numpy(dtype=bool)
        test_block_score = pd.DataFrame({"block": test["dateblock_group"].astype(str), "score": np.abs(te)}).groupby("block")["score"].mean()
        test_block_gate = test["dateblock_group"].astype(str).map((test_block_score >= threshold).to_dict()).fillna(False).to_numpy(dtype=bool)
        tr_gate = train_block_gate
        te_gate = test_block_gate
        tr_feat = tr * tr_gate
        te_feat = te * te_gate
        info["threshold"] = threshold
        info["train_blocks"] = int(sum(block_score >= threshold))
        info["test_blocks"] = int(sum(test_block_score >= threshold))
    else:
        raise ValueError(policy)
    info["train_rows"] = int(np.sum(tr_gate))
    info["test_rows"] = int(np.sum(te_gate))
    return tr_feat, te_feat, tr_gate.astype(bool), te_gate.astype(bool), info


def cv_with_feature(base_x: pd.DataFrame, feature: np.ndarray, y: np.ndarray, groups: pd.Series) -> float:
    x = pd.concat([base_x.reset_index(drop=True), pd.Series(feature, name="localized_resid_state")], axis=1)
    return cv_logloss(x, y, groups)


def build_localization() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, list[Path], pd.DataFrame]:
    train, test, train_views, test_views = train_test_state()
    base_x_train, base_x_test = base_label_matrix_all(train, test)
    source = source_rows()
    policies = ["abs_q75", "abs_q85", "abs_q92", "pos_q80", "pos_q90", "neg_q80", "neg_q90", "blockabs_q65", "blockabs_q80"]
    local_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    materializers: list[dict[str, Any]] = []

    for _, src in source.iterrows():
        target = str(src["target"])
        view_id = str(src["view_id"])
        split_name = str(src["split"])
        y = train[target].astype(int).to_numpy()
        groups = groups_for(train, split_name).reset_index(drop=True)
        base_oof = oof_proba(base_x_train, y, groups)
        teacher = y.astype(float) - base_oof
        pred_train, _, _r2 = oof_ridge_scalar(train_views[view_id], teacher, groups)
        pred_test = fit_ridge_full_predict(train_views[view_id], teacher, test_views[view_id])
        base_loss = cv_logloss(base_x_train, y, groups)
        null_groups = {
            "row": groups,
            "subject": groups_for(train, "subject").reset_index(drop=True),
            "dateblock": groups_for(train, "dateblock").reset_index(drop=True),
        }
        for policy in policies:
            tr_feat, te_feat, tr_gate, te_gate, info = policy_feature(pred_train, pred_test, train, test, policy)
            if int(tr_gate.sum()) < 8 or int(te_gate.sum()) < 3:
                continue
            actual_loss = cv_with_feature(base_x_train, tr_feat, y, groups)
            actual_delta = float(actual_loss - base_loss)
            null_vals: list[float] = []
            rng = np.random.default_rng(stable_seed("feature_null", target, view_id, split_name, policy))
            for mode, mgroups in null_groups.items():
                for rep in range(NULL_REPS):
                    shuffled = shuffled_feature(tr_feat, mode, mgroups, rng)
                    null_delta = float(cv_with_feature(base_x_train, shuffled, y, groups) - base_loss)
                    null_vals.append(null_delta)
                    null_rows.append(
                        {
                            "target": target,
                            "view_id": view_id,
                            "split": split_name,
                            "policy": policy,
                            "mode": mode,
                            "rep": rep,
                            "null_delta": null_delta,
                        }
                    )
            null_arr = np.asarray(null_vals, dtype=np.float64)
            dominance = float(np.mean(actual_delta < null_arr))
            placebo_adjusted = actual_delta - float(np.median(null_arr))
            gate = bool(actual_delta < -0.0005 and dominance >= 0.85 and placebo_adjusted < -0.00025)
            row = {
                "target": target,
                "view_id": view_id,
                "split": split_name,
                "policy": policy,
                "source_delta": float(src["actual_delta"]),
                "source_dominance": float(src["dominance"]),
                "base_loss": base_loss,
                "localized_loss": actual_loss,
                "actual_delta": actual_delta,
                "null_best": float(np.min(null_arr)),
                "null_median": float(np.median(null_arr)),
                "null_q20": float(np.quantile(null_arr, 0.20)),
                "dominance": dominance,
                "placebo_adjusted_vs_median": placebo_adjusted,
                "train_rows": int(tr_gate.sum()),
                "test_rows": int(te_gate.sum()),
                "gate": gate,
                **info,
            }
            local_rows.append(row)
            if gate:
                materializers.append({**row, "train_feature": tr_feat, "test_feature": te_feat, "test_gate": te_gate, "y": y})

    local = pd.DataFrame(local_rows).sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]).reset_index(drop=True)
    nulls = pd.DataFrame(null_rows)
    selected = pd.DataFrame([{k: v for k, v in m.items() if k not in {"train_feature", "test_feature", "test_gate", "y"}} for m in materializers])
    if selected.empty:
        materializers = []
    else:
        selected = selected.sort_values(["actual_delta", "dominance"], ascending=[True, False]).head(MAX_LOCAL_GATES).reset_index(drop=True)
        keep_ids = set(zip(selected["target"], selected["view_id"], selected["split"], selected["policy"]))
        materializers = [
            m for m in materializers
            if (m["target"], m["view_id"], m["split"], m["policy"]) in keep_ids
        ][:MAX_LOCAL_GATES]

    candidates, paths, base = materialize_candidates(materializers, train, test, base_x_train, base_x_test)
    return local, nulls, candidates, selected, paths, base


def materialize_candidates(
    materializers: list[dict[str, Any]],
    train: pd.DataFrame,
    test: pd.DataFrame,
    base_x_train: pd.DataFrame,
    base_x_test: pd.DataFrame,
) -> tuple[pd.DataFrame, list[Path], pd.DataFrame]:
    base = load_sub_frame(E247, test[KEYS])
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    paths: list[Path] = []
    rows: list[dict[str, Any]] = []
    combo_logits = base_logits.copy()
    combo_parts: list[str] = []
    for m in materializers:
        target = str(m["target"])
        target_idx = TARGETS.index(target)
        y = np.asarray(m["y"], dtype=int)
        tr_feat = np.asarray(m["train_feature"], dtype=np.float64)
        te_feat = np.asarray(m["test_feature"], dtype=np.float64)
        te_gate = np.asarray(m["test_gate"], dtype=bool)
        x_aug_train = pd.concat([base_x_train.reset_index(drop=True), pd.Series(tr_feat, name="localized_resid_state")], axis=1)
        x_aug_test = pd.concat([base_x_test.reset_index(drop=True), pd.Series(te_feat, name="localized_resid_state")], axis=1)
        p_base = fit_logistic_predict(base_x_train, y, base_x_test)
        p_aug = fit_logistic_predict(x_aug_train, y, x_aug_test)
        raw_delta = np.clip(logit(p_aug) - logit(p_base), -CAP, CAP)
        raw_delta = np.where(te_gate, raw_delta, 0.0)
        if np.max(np.abs(raw_delta)) < 1.0e-12:
            continue
        for scale in SCALES:
            logits = base_logits.copy()
            logits[:, target_idx] += scale * raw_delta
            cid = f"{target}_{m['view_id']}_{m['split']}_{m['policy']}_s{str(scale).replace('.', 'p')}"
            path = write_submission(base, logits, cid)
            paths.append(path)
            move = np.zeros_like(base_logits)
            move[:, target_idx] = scale * raw_delta
            rows.append(
                {
                    "candidate_id": cid,
                    "file": rel(path),
                    "basename": path.name,
                    "target": target,
                    "view_id": m["view_id"],
                    "split": m["split"],
                    "policy": m["policy"],
                    "scale": scale,
                    "source_actual_delta": float(m["actual_delta"]),
                    "source_dominance": float(m["dominance"]),
                    "train_rows": int(m["train_rows"]),
                    "test_rows": int(m["test_rows"]),
                    "changed_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
                    "changed_cells": int((np.abs(move) > 1.0e-12).sum()),
                    "mean_abs_logit_move": float(np.mean(np.abs(move))),
                    "max_abs_logit_move": float(np.max(np.abs(move))),
                }
            )
        if len(combo_parts) < 4:
            combo_logits[:, target_idx] += 0.55 * raw_delta
            combo_parts.append(f"{target}:{m['view_id']}:{m['policy']}")
    if combo_parts:
        path = write_submission(base, combo_logits, "combo_local_top_s0p55")
        paths.append(path)
        move = combo_logits - base_logits
        rows.append(
            {
                "candidate_id": "combo_local_top_s0p55",
                "file": rel(path),
                "basename": path.name,
                "target": ",".join(sorted({p.split(':')[0] for p in combo_parts})),
                "view_id": ";".join(combo_parts),
                "split": "combo",
                "policy": "combo",
                "scale": 0.55,
                "source_actual_delta": float(np.mean([m["actual_delta"] for m in materializers[:4]])),
                "source_dominance": float(np.mean([m["dominance"] for m in materializers[:4]])),
                "train_rows": int(np.mean([m["train_rows"] for m in materializers[:4]])),
                "test_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
                "changed_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
                "changed_cells": int((np.abs(move) > 1.0e-12).sum()),
                "mean_abs_logit_move": float(np.mean(np.abs(move))),
                "max_abs_logit_move": float(np.max(np.abs(move))),
            }
        )
    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out, paths, base


def write_submission(base: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base.copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e331_localresid_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


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
                "changed_rows": int(np.any(np.abs(move) > 1.0e-12, axis=1).sum()),
                "changed_cells": int((np.abs(move) > 1.0e-12).sum()),
                "mean_abs_logit_delta": float(np.mean(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(cand[TARGETS].to_numpy(dtype=np.float64) - base[TARGETS].to_numpy(dtype=np.float64)))),
                "cos_with_e323_bad_delta": float(np.sum(move * bad) / denom) if denom else 0.0,
                "l1_ratio_to_e323_delta": float(np.sum(np.abs(move)) / (np.sum(np.abs(bad)) + EPS)),
            }
        )
    out = pd.DataFrame(rows).sort_values(["cos_with_e323_bad_delta", "l1_ratio_to_e323_delta"]).reset_index(drop=True)
    out.to_csv(ANATOMY_OUT, index=False)
    return out


def write_movement_null(path: Path, base: pd.DataFrame, meta: pd.DataFrame, mode: str, rep: int, seed: int) -> Path:
    rng = np.random.default_rng(seed)
    current = logit(base[TARGETS].to_numpy(dtype=np.float64))
    cand = load_sub_frame(path, base[KEYS])
    delta = logit(cand[TARGETS].to_numpy(dtype=np.float64)) - current
    shuffled = np.zeros_like(delta)
    if mode == "row":
        order = rng.permutation(len(delta))
        shuffled = delta[order]
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
    null_path = NULL_DIR / f"submission_e331null_{path.stem.replace('submission_', '')[:78]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(null_path, index=False)
    return null_path


def movement_null_stress(paths: list[Path], base: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    if not paths or scores.empty:
        return pd.DataFrame()
    non_current = scores[~scores["basename"].eq(CURRENT)].copy()
    # Only stress candidates with any plausible local edge, to keep the run bounded.
    chosen = non_current.sort_values(["promotion_decision", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(12)
    path_by_name = {p.name: p for p in paths}
    sample = load_sub(E247)[KEYS]
    _train, test_meta, _train_views, _test_views = train_test_state()
    meta = test_meta[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        meta[col] = pd.to_datetime(meta[col])
    if not meta[KEYS].reset_index(drop=True).equals(sample[KEYS].reset_index(drop=True)):
        raise RuntimeError("E331 movement-null metadata does not align with E247 sample")
    null_paths: list[Path] = []
    null_map: list[dict[str, object]] = []
    for _, rec in chosen.iterrows():
        path = path_by_name.get(str(rec["basename"]))
        if path is None:
            continue
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(MOVEMENT_NULL_REPS):
                npath = write_movement_null(path, base, meta, mode, rep, stable_seed("move_null", path.name, mode, rep))
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
    actual = non_current[["basename", "pred_delta_vs_current_mean", "pred_delta_vs_current_p90", "pred_beats_current_rate", "strict_promote_gate"]].rename(
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
    out = pd.DataFrame(rows).sort_values(["actual_p90_dominance", "actual_p90"], ascending=[False, True]).reset_index(drop=True)
    out.to_csv(MOVE_NULL_OUT, index=False)
    return out


def write_report(local: pd.DataFrame, selected: pd.DataFrame, candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame, move_null: pd.DataFrame) -> None:
    non_current = scores[~scores["basename"].eq(CURRENT)].copy() if len(scores) else pd.DataFrame()
    promoted = non_current[non_current["strict_promote_gate"].astype(bool)] if len(non_current) else pd.DataFrame()
    e323_safe = anatomy[anatomy["cos_with_e323_bad_delta"] <= 0.05] if len(anatomy) else pd.DataFrame()
    safe_promoted = promoted[promoted["basename"].isin(set(e323_safe["basename"]))] if len(promoted) and len(e323_safe) else pd.DataFrame()
    move_safe = pd.DataFrame()
    if len(safe_promoted) and len(move_null):
        move_safe = safe_promoted.merge(move_null, on="basename", how="inner")
        move_safe = move_safe[(move_safe["actual_p90_dominance"] >= 0.75) & (move_safe["null_strict_promote_rate"] <= 0.10)]
    lines = [
        "# E331 Residual-State Localization",
        "",
        "## Question",
        "",
        "E330 proved target-specific residual states exist, but full-target calibration was too diffuse. Can those states localize row/block/cell actions while preserving E247 and avoiding E323?",
        "",
        "## Localized Feature Stress",
        "",
        md_table(local.sort_values(["gate", "actual_delta", "dominance"], ascending=[False, True, False]), n=40, floatfmt=".9f"),
        "",
        "## Selected Gates",
        "",
        md_table(selected, n=30, floatfmt=".9f") if len(selected) else "_no gates_",
        "",
        "## Candidate Probes",
        "",
        md_table(candidates, n=40, floatfmt=".9f") if len(candidates) else "_no candidates_",
        "",
        "## Public-Free Selector Scores",
        "",
    ]
    if len(non_current):
        cols = [
            "basename",
            "promotion_decision",
            "pred_delta_vs_current_mean",
            "pred_delta_vs_current_p10",
            "pred_delta_vs_current_p90",
            "pred_beats_current_rate",
            "incremental_bad_axis_vs_current",
        ]
        lines.append(md_table(non_current[cols], n=50, floatfmt=".9f"))
    else:
        lines.append("_no scores_")
    lines.extend(["", "## E323-Negative Anatomy", ""])
    lines.append(md_table(anatomy, n=50, floatfmt=".9f") if len(anatomy) else "_no anatomy_")
    lines.extend(["", "## Movement-Null Stress", ""])
    lines.append(md_table(move_null, n=30, floatfmt=".9f") if len(move_null) else "_no movement null stress_")
    lines.extend(["", "## Decision", ""])
    if len(move_safe):
        best = move_safe.sort_values(["actual_p90", "pred_delta_vs_current_mean"]).iloc[0]
        lines.append(
            f"`{best['basename']}` survives selector, E323-negative anatomy, and movement-null stress. It is a candidate for a final high-repetition null check before any public submission."
        )
    elif len(safe_promoted):
        lines.append(
            "At least one candidate clears selector and E323-negative anatomy, but movement-null stress is not strong enough. Do not submit before high-repetition null confirmation."
        )
    elif int(local["gate"].sum()) == 0:
        lines.append(
            "Localization did not produce label/null-stable residual-state gates. The E330 signal remains representational only."
        )
    else:
        lines.append(
            "Localized residual-state gates exist, but their materialized E247 actions are still not submission-grade under selector/E323/movement-null stress."
        )
    lines.extend(
        [
            "",
            f"- localized gates: `{int(local['gate'].sum()) if len(local) else 0}`",
            f"- generated candidates: `{len(candidates)}`",
            f"- selector-promoted candidates: `{int(non_current['strict_promote_gate'].sum()) if len(non_current) else 0}`",
            f"- selector+E323-safe candidates: `{len(safe_promoted)}`",
            f"- selector+E323+movement-null-safe candidates: `{len(move_safe)}`",
            "",
            "## Files",
            "",
            f"- `{LOCAL_OUT.name}`",
            f"- `{LOCAL_NULL_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{ANATOMY_OUT.name}`",
            f"- `{MOVE_NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    local, nulls, candidates, selected, paths, base = build_localization()
    scores = score_candidate_files(paths)
    anatomy = candidate_anatomy(paths, base)
    move_null = movement_null_stress(paths, base, scores)

    local.to_csv(LOCAL_OUT, index=False)
    nulls.to_csv(LOCAL_NULL_OUT, index=False)
    if not selected.empty:
        selected.to_csv(OUT / "e331_residual_state_localization_selected.csv", index=False)
    write_report(local, selected, candidates, scores, anatomy, move_null)

    print(REPORT_OUT)
    print("[local]")
    print(local.head(25).round(9).to_string(index=False))
    if len(scores):
        print("[scores]")
        print(scores[["basename", "promotion_decision", "pred_delta_vs_current_mean", "pred_delta_vs_current_p10", "pred_delta_vs_current_p90", "pred_beats_current_rate"]].head(30).round(9).to_string(index=False))
    if len(move_null):
        print("[move null]")
        print(move_null.head(20).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
