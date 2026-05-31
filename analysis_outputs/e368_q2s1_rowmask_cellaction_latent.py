#!/usr/bin/env python3
"""E368: Q2/S1 lifestyle row-mask cell-action latent.

Question:
    E367 killed the aggregate public/private row-mask gate, but the
    target-specific diagnostics did not die uniformly.  Q2 row-validity was
    strongly learnable from lifestyle/story context and S1 was weakly but
    non-random.  Is the hidden lifestyle state useful only when translated
    into the Q2/S1 cells instead of the whole 7-target vector?

JEPA/data2vec translation:
    context = E328/E358 lifestyle state and human/social story features
    target  = known-public Q2 and S1 row-validity representations
    action  = preserve the E365 donor-graft backbone while changing only the
              Q2/S1 cells according to learned lifestyle row masks.

The public scores are used as fixed sensors.  The script does not tune against
new leaderboard feedback and rejects generated candidates when direct-public,
null, or permuted Q2/S1 masks explain the score better than learned masks.
"""

from __future__ import annotations

import hashlib
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e357_public_survival_contrast_latent import (  # noqa: E402
    KEY,
    TARGETS,
    add_axis_features,
    align_delta,
    feature_columns as movement_feature_columns,
    load_known,
    locate,
    logit_frame,
    make_axes,
    movement_features,
    safe_spearman,
)
from e358_rowstate_public_survival_audit import load_anchor, load_row_state, rowstate_features  # noqa: E402
from e359_rowplacement_action_health_probe import clip_prob, load_source, logit, selector_scores, sigmoid  # noqa: E402
from e360_learned_row_action_health_generator import rowstate_public_scores  # noqa: E402
from e363_cell_action_robustness_probe import add_e363_scores  # noqa: E402
from e364_public_like_cellaction_calibration import public_axis_summaries  # noqa: E402
from e366_hidden_lifestyle_donor_family_latent import (  # noqa: E402
    E364_SCORES_IN,
    E365_SELECTION_IN,
    available_feature_sets as e366_feature_sets,
    candidate_prefeatures,
    good_high,
    good_low,
    load_family_sources,
    make_model,
    rank01,
)


RNG_SEED = 20260531 + 368
ANCHOR_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
UPLOAD_PREFIX = "submission_e368_q2s1rowmask"

ROWMASK_OUT = OUT / "e368_q2s1_rowmask_cellaction_rows.csv"
KNOWN_OUT = OUT / "e368_q2s1_rowmask_cellaction_known.csv"
DIAGNOSTICS_OUT = OUT / "e368_q2s1_rowmask_cellaction_diagnostics.csv"
STABILITY_OUT = OUT / "e368_q2s1_rowmask_cellaction_stability.csv"
CANDIDATES_OUT = OUT / "e368_q2s1_rowmask_cellaction_candidates.csv"
SCORES_OUT = OUT / "e368_q2s1_rowmask_cellaction_scores.csv"
SCENARIOS_OUT = OUT / "e368_q2s1_rowmask_cellaction_scenarios.csv"
RANKS_OUT = OUT / "e368_q2s1_rowmask_cellaction_scenario_ranks.csv"
SUPPORT_OUT = OUT / "e368_q2s1_rowmask_cellaction_support.csv"
SELECTION_OUT = OUT / "e368_q2s1_rowmask_cellaction_selection.csv"
REPORT_OUT = OUT / "e368_q2s1_rowmask_cellaction_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def zscore(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    sd = float(np.std(arr))
    if not np.isfinite(sd) or sd < 1.0e-12:
        return np.zeros_like(arr)
    return (arr - float(np.mean(arr))) / sd


def minmax01(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    lo = float(np.min(arr))
    hi = float(np.max(arr))
    if hi - lo < 1.0e-12:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    denom = float(np.sum(weights))
    if denom <= 1.0e-12:
        return 0.0
    return float(np.sum(values * weights) / denom)


def renorm_l1(delta: np.ndarray, reference: np.ndarray, scale: float = 1.0) -> np.ndarray:
    denom = float(np.abs(delta).sum())
    target = float(np.abs(reference).sum()) * float(scale)
    if denom <= 1.0e-12 or target <= 1.0e-12:
        return delta
    return delta * (target / denom)


def build_rowmask_maps(
    known: pd.DataFrame,
    known_deltas: dict[str, np.ndarray],
    exclude_basename: str | None = None,
) -> tuple[dict[str, np.ndarray], pd.DataFrame]:
    avail = known[known["available"].fillna(False).astype(bool)].copy()
    avail = avail[avail["basename"].astype(str).isin(known_deltas)].copy()
    avail = avail[avail["basename"].astype(str).ne(ANCHOR_FILE)].copy()
    if exclude_basename is not None:
        avail = avail[avail["basename"].astype(str).ne(str(exclude_basename))].copy()
    if len(avail) < 5:
        raise RuntimeError("not enough known public rows to build a row-mask target")

    deltas = avail["delta_vs_e247"].astype(float).to_numpy()
    positive = np.maximum(deltas, 1.0e-9)
    good_scale = max(float(np.quantile(positive, 0.40)), 1.0e-4)
    good_w = np.exp(-positive / good_scale)
    # Keep the very-near public files as positive support, but do not let one
    # tiny delta dominate the whole same-level target.
    good_w = np.sqrt(good_w)
    bad_w = np.power(positive / max(float(np.max(positive)), 1.0e-9), 1.35)
    good_w = good_w / max(float(good_w.sum()), 1.0e-12)
    bad_w = bad_w / max(float(bad_w.sum()), 1.0e-12)

    first = next(iter(known_deltas.values()))
    good_abs = np.zeros_like(first)
    bad_abs = np.zeros_like(first)
    good_signed = np.zeros_like(first)
    bad_signed = np.zeros_like(first)
    weight_rows = []
    for i, (_, row) in enumerate(avail.reset_index(drop=True).iterrows()):
        name = str(row["basename"])
        d = np.asarray(known_deltas[name], dtype=np.float64)
        good_abs += good_w[i] * np.abs(d)
        bad_abs += bad_w[i] * np.abs(d)
        good_signed += good_w[i] * d
        bad_signed += bad_w[i] * d
        weight_rows.append(
            {
                "basename": name,
                "file": row["file"],
                "public_lb": float(row["public_lb"]),
                "delta_vs_e247": float(row["delta_vs_e247"]),
                "good_weight": float(good_w[i]),
                "bad_weight": float(bad_w[i]),
                "excluded": exclude_basename or "none",
            }
        )

    good_row = good_abs.sum(axis=1)
    bad_row = bad_abs.sum(axis=1)
    signed_gap = np.abs(good_signed - bad_signed).sum(axis=1)
    maps: dict[str, np.ndarray] = {
        "public_good_row_support": rank01(good_row),
        "public_bad_row_support": rank01(bad_row),
        "public_row_validity": rank01(good_row) - rank01(bad_row),
        "public_signed_gap": rank01(signed_gap),
    }
    for j, target in enumerate(TARGETS):
        maps[f"public_good_{target}"] = rank01(good_abs[:, j])
        maps[f"public_bad_{target}"] = rank01(bad_abs[:, j])
        maps[f"public_validity_{target}"] = rank01(good_abs[:, j]) - rank01(bad_abs[:, j])
        maps[f"public_signed_gap_{target}"] = rank01(np.abs(good_signed[:, j] - bad_signed[:, j]))
    return maps, pd.DataFrame(weight_rows)


def rowmask_stability(known: pd.DataFrame, known_deltas: dict[str, np.ndarray], full_maps: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for name in known[known["available"].fillna(False).astype(bool)]["basename"].astype(str):
        if name == ANCHOR_FILE or name not in known_deltas:
            continue
        try:
            drop_maps, _ = build_rowmask_maps(known, known_deltas, exclude_basename=name)
        except RuntimeError:
            continue
        rec = {"dropped_public": name}
        for key in ["public_row_validity", "public_bad_row_support", "public_validity_Q2", "public_validity_S1"]:
            rec[f"{key}_spearman"] = safe_spearman(full_maps[key], drop_maps[key])
        rows.append(rec)
    out = pd.DataFrame(rows)
    out.to_csv(STABILITY_OUT, index=False)
    return out


def model_for(name: str, seed: int = RNG_SEED):
    if name == "ridge_10":
        return make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    if name == "ridge_1":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if name == "extratrees":
        return ExtraTreesRegressor(n_estimators=72, min_samples_leaf=4, max_features=0.70, random_state=seed, n_jobs=1)
    raise ValueError(name)


def kfold_oof(x: pd.DataFrame, y: np.ndarray, seed: int) -> tuple[np.ndarray, dict[str, float]]:
    preds = np.zeros((len(y), 3), dtype=np.float64)
    counts = np.zeros(len(y), dtype=np.float64)
    splitter = KFold(n_splits=5, shuffle=True, random_state=seed)
    model_names = ["ridge_10", "ridge_1", "extratrees"]
    for fold, (tr, va) in enumerate(splitter.split(x)):
        for m, name in enumerate(model_names):
            model = model_for(name, seed + fold * 13 + m)
            model.fit(x.iloc[tr], y[tr])
            preds[va, m] += np.asarray(model.predict(x.iloc[va]), dtype=np.float64)
        counts[va] += 1.0
    counts[counts == 0] = 1.0
    pred = preds.mean(axis=1) / counts
    return pred, {"kfold_spearman": safe_spearman(y, pred)}


def group_oof(x: pd.DataFrame, y: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, float]:
    unique = np.unique(groups)
    if len(unique) < 3:
        return np.zeros(len(y), dtype=np.float64), np.nan
    n_splits = min(5, len(unique))
    pred = np.full(len(y), np.nan, dtype=np.float64)
    splitter = GroupKFold(n_splits=n_splits)
    for fold, (tr, va) in enumerate(splitter.split(x, y, groups)):
        model = model_for("extratrees", seed + fold * 17)
        model.fit(x.iloc[tr], y[tr])
        pred[va] = np.asarray(model.predict(x.iloc[va]), dtype=np.float64)
    return np.nan_to_num(pred, nan=float(np.nanmean(pred))), safe_spearman(y, pred)


def learn_rowmask_latent(
    anchor: pd.DataFrame,
    state: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
    maps: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    feature_cols = [c for c in base_cols + story_cols if c in state.columns]
    x = state[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)
    groups = pd.to_numeric(state["ownlife_k8"], errors="coerce").fillna(-1).astype(int).to_numpy()
    targets = {
        "public_row_validity": maps["public_row_validity"],
        "public_bad_row_support": maps["public_bad_row_support"],
        "public_validity_Q1": maps["public_validity_Q1"],
        "public_validity_Q2": maps["public_validity_Q2"],
        "public_validity_Q3": maps["public_validity_Q3"],
        "public_validity_S1": maps["public_validity_S1"],
        "public_signed_gap": maps["public_signed_gap"],
    }
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    pred_cols: dict[str, np.ndarray] = {}
    for target_name, y_raw in targets.items():
        y = zscore(y_raw)
        pred, diag = kfold_oof(x, y, RNG_SEED + len(rows))
        group_pred, group_sp = group_oof(x, y, groups, RNG_SEED + 101 + len(rows))
        null_scores = []
        for i in range(12):
            yp = rng.permutation(y)
            null_pred, _ = kfold_oof(x, yp, RNG_SEED + 1000 + i)
            null_scores.append(safe_spearman(yp, null_pred))
        null_arr = np.asarray([v for v in null_scores if np.isfinite(v)], dtype=np.float64)
        null_p95 = float(np.quantile(null_arr, 0.95)) if len(null_arr) else np.nan
        pred_cols[f"pred_{target_name}"] = pred
        pred_cols[f"group_pred_{target_name}"] = group_pred
        rows.append(
            {
                "target": target_name,
                "kfold_spearman": float(diag["kfold_spearman"]),
                "group_spearman": float(group_sp) if np.isfinite(group_sp) else np.nan,
                "null_p95": null_p95,
                "beats_null_p95": bool(np.isfinite(diag["kfold_spearman"]) and np.isfinite(null_p95) and diag["kfold_spearman"] > null_p95),
                "target_std": float(np.std(y_raw)),
                "feature_count": int(len(feature_cols)),
            }
        )
    diag_frame = pd.DataFrame(rows)
    rowmask = anchor[KEY].copy()
    for key, vals in maps.items():
        rowmask[key] = vals
    for key, vals in pred_cols.items():
        rowmask[key] = vals
    rowmask["pred_validity_rank"] = rank01(rowmask["pred_public_row_validity"])
    rowmask["pred_bad_rank"] = rank01(rowmask["pred_public_bad_row_support"])
    rowmask["pred_q2_valid_rank"] = rank01(rowmask["pred_public_validity_Q2"])
    rowmask["pred_s1_valid_rank"] = rank01(rowmask["pred_public_validity_S1"])
    rowmask.to_csv(ROWMASK_OUT, index=False)
    diag_frame.to_csv(DIAGNOSTICS_OUT, index=False)
    return rowmask, diag_frame


def rowmask_features(delta: np.ndarray, rowmask: pd.DataFrame) -> dict[str, float]:
    absd = np.abs(delta)
    row_abs = absd.sum(axis=1)
    total = float(row_abs.sum())
    out: dict[str, float] = {}
    scalar_cols = [
        "public_row_validity",
        "public_good_row_support",
        "public_bad_row_support",
        "pred_public_row_validity",
        "pred_public_bad_row_support",
        "pred_validity_rank",
        "pred_bad_rank",
        "pred_public_signed_gap",
    ]
    for col in scalar_cols:
        if col not in rowmask:
            continue
        vals = rowmask[col].to_numpy(dtype=np.float64)
        out[f"rowmask_wmean_{col}"] = weighted_mean(vals, row_abs)
        top = vals >= np.quantile(vals, 0.80)
        out[f"rowmask_top20_share_{col}"] = float(row_abs[top].sum() / total) if total > 0 else 0.0
        out[f"rowmask_corr_{col}"] = safe_spearman(row_abs, vals)
    for j, target in enumerate(TARGETS):
        w = absd[:, j]
        for col in [f"public_validity_{target}", f"pred_public_validity_{target}"]:
            if col in rowmask:
                vals = rowmask[col].to_numpy(dtype=np.float64)
                out[f"rowmask_{target}_wmean_{col}"] = weighted_mean(vals, w)
    return out


def materialize(
    anchor: pd.DataFrame,
    anchor_logit: np.ndarray,
    delta: np.ndarray,
    sources: dict[str, dict[str, Any]],
    state: pd.DataFrame,
    rowmask: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
    meta: dict[str, Any],
    rows: list[dict[str, Any]],
    seen: set[str],
) -> None:
    if not np.isfinite(delta).all() or float(np.abs(delta).sum()) < 1.0e-9:
        return
    delta = delta.copy()
    delta[:, TARGETS.index("S3")] = 0.0
    digest = hashlib.sha1(np.round(delta, 8).tobytes()).hexdigest()[:12]
    if digest in seen:
        return
    seen.add(digest)
    out = anchor[KEY].copy()
    out[TARGETS] = clip_prob(sigmoid(anchor_logit + delta))
    variant = str(meta["variant"])
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(variant, 112)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    rec = candidate_prefeatures(delta, sources, state, base_cols, story_cols, meta)
    rec.update(rowmask_features(delta, rowmask))
    rec["file"] = rel(path)
    rec["basename"] = path.name
    rows.append(rec)


def scale_delta_by_row(base: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return base * np.asarray(scale, dtype=np.float64)[:, None]


def generate_candidates(
    anchor: pd.DataFrame,
    anchor_logit: np.ndarray,
    state: pd.DataFrame,
    rowmask: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    sources = load_family_sources(anchor, anchor_logit)
    deltas = {k: v["delta"] for k, v in sources.items()}
    base_key = "q3s1" if "q3s1" in deltas else next(iter(deltas))
    base = deltas[base_key]
    q3 = deltas.get("q3", base)
    s1 = deltas.get("s1", base)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    q2_valid = rank01(rowmask["pred_public_validity_Q2"])
    s1_valid = rank01(rowmask["pred_public_validity_S1"])
    bad = rank01(rowmask["pred_public_bad_row_support"])
    direct_q2 = rank01(rowmask["public_validity_Q2"])
    direct_s1 = rank01(rowmask["public_validity_S1"])
    rng = np.random.default_rng(RNG_SEED)

    def emit_policy(policy: str, family: str, q2v: np.ndarray, s1v: np.ndarray, b: np.ndarray, direct: bool = False) -> None:
        q2_tail = np.clip((q2v - 0.62) / 0.38, 0.0, 1.0)
        q2_low = np.clip((0.38 - q2v) / 0.38, 0.0, 1.0)
        s1_tail = np.clip((s1v - 0.62) / 0.38, 0.0, 1.0)
        s1_low = np.clip((0.38 - s1v) / 0.38, 0.0, 1.0)
        bad_tail = np.clip((b - 0.62) / 0.38, 0.0, 1.0)
        for amp in [0.88, 0.94, 1.00, 1.06]:
            if policy == "q2s1_validity_scale":
                delta = base.copy()
                delta[:, TARGETS.index("Q2")] *= np.clip(0.72 + amp * (0.62 * q2_tail) - 0.30 * bad_tail, 0.35, 1.34)
                delta[:, TARGETS.index("S1")] *= np.clip(0.72 + amp * (0.70 * s1_tail) - 0.28 * bad_tail, 0.35, 1.42)
            elif policy == "q2_damp_s1_recover":
                delta = base.copy()
                delta[:, TARGETS.index("Q2")] *= np.clip(1.03 - amp * (0.45 * q2_low + 0.30 * bad_tail), 0.40, 1.08)
                delta[:, TARGETS.index("S1")] = (
                    (1.0 - 0.55 * s1_tail) * base[:, TARGETS.index("S1")]
                    + (0.55 * s1_tail) * s1[:, TARGETS.index("S1")]
                )
                delta[:, TARGETS.index("S1")] *= np.clip(0.86 + amp * 0.50 * s1_tail - 0.20 * bad_tail, 0.45, 1.38)
            elif policy == "q2s1_sparse_tail":
                delta = base.copy()
                q2_scale = np.where(q2_tail > 0.45, 1.00 + amp * 0.22, np.where(q2_low > 0.45, 1.00 - amp * 0.28, 1.00))
                s1_scale = np.where(s1_tail > 0.45, 1.00 + amp * 0.28, np.where(s1_low > 0.45, 1.00 - amp * 0.18, 1.00))
                trap = np.where(bad_tail > 0.55, 0.78, 1.00)
                delta[:, TARGETS.index("Q2")] *= np.clip(q2_scale * trap, 0.45, 1.30)
                delta[:, TARGETS.index("S1")] *= np.clip(s1_scale * trap, 0.48, 1.36)
            elif policy == "s1_source_q2_mask":
                delta = base.copy()
                delta[:, TARGETS.index("Q2")] *= np.clip(0.82 + amp * 0.50 * q2_tail - 0.24 * bad_tail, 0.44, 1.30)
                delta[:, TARGETS.index("S1")] = (
                    (1.0 - s1_tail) * base[:, TARGETS.index("S1")]
                    + s1_tail * s1[:, TARGETS.index("S1")]
                )
                delta[:, TARGETS.index("S1")] *= np.clip(0.88 + amp * 0.36 * s1_tail - 0.18 * bad_tail, 0.50, 1.34)
            else:
                raise ValueError(policy)
            delta[:, TARGETS.index("S3")] = 0.0
            meta = {
                "variant": f"e368_{'direct_' if direct else ''}{policy}_amp{amp:.2f}",
                "family": family,
                "row_policy": policy,
                "amplitude_scale": amp,
                "q2_gate_mean": float(np.mean(q2_tail)),
                "q2_gate_p90": float(np.quantile(q2_tail, 0.90)),
                "s1_gate_mean": float(np.mean(s1_tail)),
                "s1_gate_p90": float(np.quantile(s1_tail, 0.90)),
                "bad_gate_mean": float(np.mean(bad_tail)),
                "bad_gate_p90": float(np.quantile(bad_tail, 0.90)),
            }
            materialize(anchor, anchor_logit, delta, sources, state, rowmask, base_cols, story_cols, meta, rows, seen)

    for policy in ["q2s1_validity_scale", "q2_damp_s1_recover", "q2s1_sparse_tail", "s1_source_q2_mask"]:
        emit_policy(policy, "learned_q2s1_lifestyle_cell_gate", q2_valid, s1_valid, bad)

    # Direct Q2/S1 public masks are diagnostic controls.  If they beat learned
    # masks, the target exists but our lifestyle translator has not learned it.
    for policy in ["q2s1_validity_scale", "q2_damp_s1_recover", "q2s1_sparse_tail", "s1_source_q2_mask"]:
        emit_policy(policy, "diagnostic_direct_q2s1_public_cell_gate", direct_q2, direct_s1, bad, direct=True)

    null_specs = {
        "inverse_q2s1": (1.0 - q2_valid, 1.0 - s1_valid, bad),
        "swap_q2_s1": (s1_valid, q2_valid, bad),
        "perm_q2s1_0": (rng.permutation(q2_valid), rng.permutation(s1_valid), bad),
        "perm_q2s1_1": (rng.permutation(q2_valid), rng.permutation(s1_valid), bad),
        "random_q2s1": (rng.random(len(q2_valid)), rng.random(len(s1_valid)), bad),
    }
    for null_id, (q2v, s1v, b) in null_specs.items():
        for policy in ["q2s1_validity_scale", "q2_damp_s1_recover", "q2s1_sparse_tail", "s1_source_q2_mask"]:
            q2_tail = np.clip((q2v - 0.62) / 0.38, 0.0, 1.0)
            q2_low = np.clip((0.38 - q2v) / 0.38, 0.0, 1.0)
            s1_tail = np.clip((s1v - 0.62) / 0.38, 0.0, 1.0)
            s1_low = np.clip((0.38 - s1v) / 0.38, 0.0, 1.0)
            bad_tail = np.clip((b - 0.62) / 0.38, 0.0, 1.0)
            amp = 1.0
            if policy == "q2s1_validity_scale":
                delta = base.copy()
                delta[:, TARGETS.index("Q2")] *= np.clip(0.72 + amp * (0.62 * q2_tail) - 0.30 * bad_tail, 0.35, 1.34)
                delta[:, TARGETS.index("S1")] *= np.clip(0.72 + amp * (0.70 * s1_tail) - 0.28 * bad_tail, 0.35, 1.42)
            elif policy == "q2_damp_s1_recover":
                delta = base.copy()
                delta[:, TARGETS.index("Q2")] *= np.clip(1.03 - amp * (0.45 * q2_low + 0.30 * bad_tail), 0.40, 1.08)
                delta[:, TARGETS.index("S1")] = (
                    (1.0 - 0.55 * s1_tail) * base[:, TARGETS.index("S1")]
                    + (0.55 * s1_tail) * s1[:, TARGETS.index("S1")]
                )
                delta[:, TARGETS.index("S1")] *= np.clip(0.86 + amp * 0.50 * s1_tail - 0.20 * bad_tail, 0.45, 1.38)
            elif policy == "q2s1_sparse_tail":
                delta = base.copy()
                q2_scale = np.where(q2_tail > 0.45, 1.22, np.where(q2_low > 0.45, 0.72, 1.00))
                s1_scale = np.where(s1_tail > 0.45, 1.28, np.where(s1_low > 0.45, 0.82, 1.00))
                trap = np.where(bad_tail > 0.55, 0.78, 1.00)
                delta[:, TARGETS.index("Q2")] *= np.clip(q2_scale * trap, 0.45, 1.30)
                delta[:, TARGETS.index("S1")] *= np.clip(s1_scale * trap, 0.48, 1.36)
            else:
                delta = base.copy()
                delta[:, TARGETS.index("Q2")] *= np.clip(0.82 + 0.50 * q2_tail - 0.24 * bad_tail, 0.44, 1.30)
                delta[:, TARGETS.index("S1")] = (
                    (1.0 - s1_tail) * base[:, TARGETS.index("S1")]
                    + s1_tail * s1[:, TARGETS.index("S1")]
                )
                delta[:, TARGETS.index("S1")] *= np.clip(0.88 + 0.36 * s1_tail - 0.18 * bad_tail, 0.50, 1.34)
            delta[:, TARGETS.index("S3")] = 0.0
            materialize(
                anchor,
                anchor_logit,
                delta,
                sources,
                state,
                rowmask,
                base_cols,
                story_cols,
                {
                    "variant": f"e368_null_{policy}_{null_id}",
                    "family": "null_q2s1_cell_gate",
                    "row_policy": policy,
                    "gate_id": null_id,
                    "q2_gate_mean": float(np.mean(q2_tail)),
                    "q2_gate_p90": float(np.quantile(q2_tail, 0.90)),
                    "s1_gate_mean": float(np.mean(s1_tail)),
                    "s1_gate_p90": float(np.quantile(s1_tail, 0.90)),
                    "bad_gate_mean": float(np.mean(bad_tail)),
                    "bad_gate_p90": float(np.quantile(bad_tail, 0.90)),
                },
                rows,
                seen,
            )

    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATES_OUT, index=False)
    return out, sources


def add_rowmask_and_movement_features(frame: pd.DataFrame, anchor_logit_frame: pd.DataFrame, axes: dict[str, np.ndarray], rowmask: pd.DataFrame) -> pd.DataFrame:
    rows = []
    delta_lookup: dict[str, np.ndarray] = {}
    for rec in frame.to_dict("records"):
        path = locate(rec.get("file", ""))
        if path is None:
            continue
        delta = align_delta(path, anchor_logit_frame)
        basename = path.name
        delta_lookup[basename] = delta
        out = {
            "variant": rec.get("variant", basename),
            "family": rec.get("family", ""),
            "file": rel(path),
            "basename": basename,
            **movement_features(delta),
            **rowmask_features(delta, rowmask),
        }
        rows.append(out)
    movement = pd.DataFrame(rows)
    movement = add_axis_features(movement, delta_lookup, axes)
    movement = public_axis_summaries(movement)
    return movement


def public_score_candidates(scored: pd.DataFrame, rowmask: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    anchor_logit_frame = logit_frame(OUT / ANCHOR_FILE)
    known, known_deltas, _ = load_known(anchor_logit_frame)
    axes = make_axes(known_deltas)
    known = add_axis_features(known, known_deltas, axes)
    known = public_axis_summaries(known)
    known_extra = []
    for _, row in known.iterrows():
        name = str(row.get("basename", ""))
        d = known_deltas.get(name)
        known_extra.append(rowmask_features(d, rowmask) if d is not None else {})
    known = pd.concat([known.reset_index(drop=True), pd.DataFrame(known_extra)], axis=1)
    known.to_csv(KNOWN_OUT, index=False)
    feature_cols = movement_feature_columns(known)

    existing = pd.read_csv(E364_SCORES_IN).replace([np.inf, -np.inf], np.nan)
    existing["candidate_origin"] = "e364_existing"
    generated = scored.copy()
    generated["candidate_origin"] = "e368_generated"
    base = pd.concat([existing, generated], ignore_index=True, sort=False)
    movement = add_rowmask_and_movement_features(base, anchor_logit_frame, axes, rowmask)

    keys = ["variant", "family", "file", "basename"]
    blocked = set(movement.columns) - set(keys)
    pool = base.drop(columns=[c for c in blocked if c in base.columns], errors="ignore").merge(movement, on=keys, how="inner")

    train = known[known["available"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    x = train[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    xp = pool.reindex(columns=feature_cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    pred_cols = []
    for model_name in ["ridge_10", "ridge_1", "knn3", "extratrees"]:
        model = make_model(model_name, len(train))
        model.fit(x, y)
        col = f"e368_pred_public_delta_{model_name}"
        pool[col] = np.asarray(model.predict(xp), dtype=np.float64)
        pred_cols.append(col)
    pool["e368_pred_public_delta_mean"] = pool[pred_cols].mean(axis=1)
    pool["e368_pred_public_delta_std"] = pool[pred_cols].std(axis=1).fillna(0.0)
    pool["e368_pred_public_delta_max"] = pool[pred_cols].max(axis=1)
    for col, default in {
        "public_bad_axis_sum": 0.0,
        "public_bad_good_gap": 0.0,
        "rowstate_pred_public_loss_mean": 0.0,
        "rowstate_bad_minus_good_exposure": 0.0,
        "e363_robust_score": 0.0,
        "pred_delta_vs_current_p90": 0.0,
        "rowmask_wmean_pred_public_row_validity": 0.0,
        "rowmask_wmean_pred_public_bad_row_support": 0.0,
        "rowmask_corr_pred_public_row_validity": 0.0,
        "rowmask_Q2_wmean_pred_public_validity_Q2": 0.0,
        "rowmask_S1_wmean_pred_public_validity_S1": 0.0,
        "rowmask_Q2_wmean_public_validity_Q2": 0.0,
        "rowmask_S1_wmean_public_validity_S1": 0.0,
    }.items():
        if col not in pool:
            pool[col] = default
        pool[col] = pd.to_numeric(pool[col], errors="coerce").fillna(default)
    if "e363_submission_gate" not in pool:
        pool["e363_submission_gate"] = False
    pool["e368_public_like_score"] = (
        1.10 * good_low(pool["e368_pred_public_delta_mean"])
        + 0.70 * good_low(pool["e368_pred_public_delta_std"])
        + 0.85 * good_low(pool["public_bad_axis_sum"])
        + 0.50 * good_low(pool["public_bad_good_gap"])
        + 0.85 * good_low(pool["rowstate_pred_public_loss_mean"])
        + 0.75 * good_low(pool["rowstate_bad_minus_good_exposure"])
        + 0.85 * good_high(pool["e363_robust_score"])
        + 0.50 * good_low(pool["pred_delta_vs_current_p90"])
        + 0.55 * good_high(pool["rowmask_wmean_pred_public_row_validity"])
        + 0.45 * good_low(pool["rowmask_wmean_pred_public_bad_row_support"])
        + 0.35 * good_high(pool["rowmask_corr_pred_public_row_validity"])
        + 0.72 * good_high(pool["rowmask_Q2_wmean_pred_public_validity_Q2"])
        + 0.48 * good_high(pool["rowmask_S1_wmean_pred_public_validity_S1"])
        + 0.18 * good_high(pool["rowmask_Q2_wmean_public_validity_Q2"])
        + 0.12 * good_high(pool["rowmask_S1_wmean_public_validity_S1"])
    )
    pool = pool.sort_values("e368_public_like_score", ascending=False).reset_index(drop=True)
    pool.to_csv(SCORES_OUT, index=False)
    return pool, known, feature_cols


def available_feature_sets(known: pd.DataFrame, pool: pd.DataFrame) -> dict[str, list[str]]:
    out = e366_feature_sets(known, pool)
    base = [c for c in movement_feature_columns(known) if c in pool.columns]
    rowmask = [c for c in base if c.startswith("rowmask_")]
    if len(rowmask) >= 3:
        out["rowmask"] = rowmask
    return out


def predict_pool(train: pd.DataFrame, pool: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    x = train[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    xp = pool.reindex(columns=cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    preds = []
    diag: dict[str, float] = {}
    for model_name in ["ridge_10", "ridge_1", "knn3", "extratrees"]:
        model = make_model(model_name, len(train))
        model.fit(x, y)
        pred = np.asarray(model.predict(xp), dtype=np.float64)
        preds.append(pred)
        fitted = np.asarray(model.predict(x), dtype=np.float64)
        diag[f"train_spearman_{model_name}"] = safe_spearman(y, fitted)
    arr = np.vstack(preds)
    return arr.mean(axis=0), arr.std(axis=0), diag


def score_scenario(pool: pd.DataFrame, pred_mean: np.ndarray, pred_std: np.ndarray, base_variant: str) -> pd.DataFrame:
    scored = pool.copy()
    scored["scenario_pred_public_delta_mean"] = pred_mean
    scored["scenario_pred_public_delta_std"] = pred_std
    for col in [
        "public_bad_axis_sum",
        "public_bad_good_gap",
        "rowstate_pred_public_loss_mean",
        "rowstate_bad_minus_good_exposure",
        "e363_robust_score",
        "pred_delta_vs_current_p90",
        "rowmask_wmean_pred_public_row_validity",
        "rowmask_wmean_pred_public_bad_row_support",
        "rowmask_corr_pred_public_row_validity",
        "rowmask_Q2_wmean_pred_public_validity_Q2",
        "rowmask_S1_wmean_pred_public_validity_S1",
        "rowmask_Q2_wmean_public_validity_Q2",
        "rowmask_S1_wmean_public_validity_S1",
    ]:
        if col not in scored:
            scored[col] = 0.0
        scored[col] = pd.to_numeric(scored[col], errors="coerce").fillna(0.0)
    scored["scenario_public_like_score"] = (
        1.10 * good_low(scored["scenario_pred_public_delta_mean"])
        + 0.70 * good_low(scored["scenario_pred_public_delta_std"])
        + 0.85 * good_low(scored["public_bad_axis_sum"])
        + 0.50 * good_low(scored["public_bad_good_gap"])
        + 0.85 * good_low(scored["rowstate_pred_public_loss_mean"])
        + 0.75 * good_low(scored["rowstate_bad_minus_good_exposure"])
        + 0.85 * good_high(scored["e363_robust_score"])
        + 0.50 * good_low(scored["pred_delta_vs_current_p90"])
        + 0.55 * good_high(scored["rowmask_wmean_pred_public_row_validity"])
        + 0.45 * good_low(scored["rowmask_wmean_pred_public_bad_row_support"])
        + 0.35 * good_high(scored["rowmask_corr_pred_public_row_validity"])
        + 0.72 * good_high(scored["rowmask_Q2_wmean_pred_public_validity_Q2"])
        + 0.48 * good_high(scored["rowmask_S1_wmean_pred_public_validity_S1"])
        + 0.18 * good_high(scored["rowmask_Q2_wmean_public_validity_Q2"])
        + 0.12 * good_high(scored["rowmask_S1_wmean_public_validity_S1"])
    )
    base = scored[scored["variant"].astype(str).eq(base_variant)].head(1)
    if base.empty:
        base = scored[scored["candidate_origin"].astype(str).eq("e364_existing")].sort_values("e368_public_like_score", ascending=False).head(1)
    base_row = base.iloc[0]
    scored["scenario_gate"] = (
        scored["e363_submission_gate"].fillna(False).astype(bool)
        & (scored["scenario_pred_public_delta_mean"] <= float(base_row["scenario_pred_public_delta_mean"]) + 5.0e-5)
        & (scored["scenario_pred_public_delta_std"] <= float(base_row["scenario_pred_public_delta_std"]) + 2.5e-4)
        & (scored["public_bad_axis_sum"] <= float(base_row["public_bad_axis_sum"]) + 0.12)
        & (scored["rowstate_pred_public_loss_mean"] <= float(base_row["rowstate_pred_public_loss_mean"]) + 2.5e-4)
        & (scored["rowstate_bad_minus_good_exposure"] <= float(base_row["rowstate_bad_minus_good_exposure"]) + 0.035)
        & (scored["e363_robust_score"] >= max(0.50, float(base_row["e363_robust_score"]) - 0.08))
    )
    gated = scored[scored["scenario_gate"]].copy()
    scored["scenario_rank"] = np.nan
    if not gated.empty:
        ranks = gated["scenario_public_like_score"].rank(ascending=False, method="min")
        scored.loc[gated.index, "scenario_rank"] = ranks
    return scored


def run_scenarios(known: pd.DataFrame, pool: pd.DataFrame, feature_sets: dict[str, list[str]], e365_variant: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    train0 = known[known["available"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    drops: list[tuple[str, str | None]] = [("none", None)]
    drops += [(f"drop_{safe_id(b, 42)}", b) for b in train0["basename"].astype(str).tolist()]
    scenario_rows: list[dict[str, Any]] = []
    rank_rows: list[pd.DataFrame] = []
    for view_name, cols in feature_sets.items():
        for drop_name, drop_base in drops:
            train = train0.copy()
            if drop_base is not None:
                train = train[~train["basename"].astype(str).eq(drop_base)].reset_index(drop=True)
            pred_mean, pred_std, diag = predict_pool(train, pool, cols)
            scored = score_scenario(pool, pred_mean, pred_std, e365_variant)
            gated = scored[scored["scenario_gate"]].copy()
            if gated.empty:
                continue
            top = gated.sort_values("scenario_public_like_score", ascending=False).iloc[0]
            e365 = scored[scored["variant"].astype(str).eq(e365_variant)].head(1)
            generated = gated[gated["candidate_origin"].astype(str).eq("e368_generated")].copy()
            best_generated = generated.sort_values("scenario_public_like_score", ascending=False).head(1)
            scenario_id = f"{view_name}__{drop_name}"
            row = {
                "scenario_id": scenario_id,
                "feature_view": view_name,
                "dropped_public": drop_base or "none",
                "train_rows": int(len(train)),
                "feature_count": int(len(cols)),
                "gated_count": int(len(gated)),
                "top_variant": top["variant"],
                "top_family": top.get("family", ""),
                "top_origin": top.get("candidate_origin", ""),
                "top_file": top.get("file", ""),
                "top_score": float(top["scenario_public_like_score"]),
                "generated_gated_count": int(len(generated)),
                **diag,
            }
            if len(e365):
                row["e365_rank"] = float(e365.iloc[0]["scenario_rank"]) if pd.notna(e365.iloc[0]["scenario_rank"]) else np.nan
                row["e365_score"] = float(e365.iloc[0]["scenario_public_like_score"])
                row["top_beats_e365"] = bool(float(top["scenario_public_like_score"]) > float(e365.iloc[0]["scenario_public_like_score"]))
                row["top_is_e365"] = bool(str(top["variant"]) == e365_variant)
            if len(best_generated):
                bg = best_generated.iloc[0]
                row["best_generated_variant"] = bg["variant"]
                row["best_generated_family"] = bg.get("family", "")
                row["best_generated_rank"] = float(bg["scenario_rank"]) if pd.notna(bg["scenario_rank"]) else np.nan
                row["best_generated_score"] = float(bg["scenario_public_like_score"])
            scenario_rows.append(row)
            slim = scored[
                [
                    "variant",
                    "family",
                    "file",
                    "candidate_origin",
                    "scenario_gate",
                    "scenario_rank",
                    "scenario_public_like_score",
                    "scenario_pred_public_delta_mean",
                    "scenario_pred_public_delta_std",
                ]
            ].copy()
            slim["scenario_id"] = scenario_id
            rank_rows.append(slim[slim["scenario_gate"] | slim["variant"].astype(str).eq(e365_variant)])
    scenarios = pd.DataFrame(scenario_rows)
    ranks = pd.concat(rank_rows, ignore_index=True) if rank_rows else pd.DataFrame()
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    ranks.to_csv(RANKS_OUT, index=False)
    return scenarios, ranks


def aggregate_support(ranks: pd.DataFrame, scenario_count: int) -> pd.DataFrame:
    if ranks.empty:
        return pd.DataFrame()
    support = (
        ranks.groupby(["variant", "family", "file", "candidate_origin"], dropna=False)
        .agg(
            gate_count=("scenario_gate", "sum"),
            rank_mean=("scenario_rank", "mean"),
            rank_median=("scenario_rank", "median"),
            rank_min=("scenario_rank", "min"),
            top1_count=("scenario_rank", lambda x: int((x == 1).sum())),
            top5_count=("scenario_rank", lambda x: int((x <= 5).sum())),
            top10_count=("scenario_rank", lambda x: int((x <= 10).sum())),
            score_mean=("scenario_public_like_score", "mean"),
            score_std=("scenario_public_like_score", "std"),
            pred_mean=("scenario_pred_public_delta_mean", "mean"),
            pred_std_mean=("scenario_pred_public_delta_std", "mean"),
        )
        .reset_index()
    )
    for col in ["gate_count", "top1_count", "top5_count", "top10_count"]:
        support[f"{col.replace('_count', '')}_rate"] = support[col] / max(1, scenario_count)
    support = support.sort_values(["top1_count", "top5_count", "rank_mean", "score_mean"], ascending=[False, False, True, False]).reset_index(drop=True)
    support.to_csv(SUPPORT_OUT, index=False)
    return support


def copy_uploadsafe(path: Path, variant: str) -> Path:
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    frame = pd.read_csv(path)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(variant, 70)}_{short_hash(frame)}_uploadsafe.csv"
    frame.to_csv(out, index=False)
    return out


def decide(
    combined: pd.DataFrame,
    support: pd.DataFrame,
    scenarios: pd.DataFrame,
    diagnostics: pd.DataFrame,
    stability: pd.DataFrame,
    e365_variant: str,
) -> pd.DataFrame:
    generated = support[support["candidate_origin"].astype(str).eq("e368_generated")].copy()
    null_support = generated[generated["family"].astype(str).str.startswith("null_")].copy()
    diagnostic_support = generated[generated["family"].astype(str).str.startswith("diagnostic_")].copy()
    real_support = generated[
        ~generated["family"].astype(str).str.startswith("null_")
        & ~generated["family"].astype(str).str.startswith("diagnostic_")
    ].copy()
    best_real = real_support.head(1)
    best_null = null_support.head(1)
    best_diag = diagnostic_support.head(1)
    e365_support = support[support["variant"].astype(str).eq(e365_variant)].head(1)
    e365_score = combined[combined["variant"].astype(str).eq(e365_variant)].head(1)

    def rate(frame: pd.DataFrame, col: str) -> float:
        return float(frame[col].iloc[0]) if len(frame) and col in frame else 0.0

    e365_top1 = rate(e365_support, "top1_rate")
    e365_top10 = rate(e365_support, "top10_rate")
    real_top1 = rate(best_real, "top1_rate")
    real_top10 = rate(best_real, "top10_rate")
    null_top1 = rate(best_null, "top1_rate")
    null_top10 = rate(best_null, "top10_rate")
    diag_top1 = rate(best_diag, "top1_rate")
    e365_pls = float(e365_score["e368_public_like_score"].iloc[0]) if len(e365_score) else 0.0
    best_real_variant = str(best_real.iloc[0]["variant"]) if len(best_real) else "none"
    real_score_row = combined[combined["variant"].astype(str).eq(best_real_variant)].head(1)
    real_pls = float(real_score_row["e368_public_like_score"].iloc[0]) if len(real_score_row) else -np.inf

    q2_diag = diagnostics[diagnostics["target"].astype(str).eq("public_validity_Q2")].head(1)
    s1_diag = diagnostics[diagnostics["target"].astype(str).eq("public_validity_S1")].head(1)
    q2_predictive_ok = bool(
        len(q2_diag)
        and float(q2_diag["kfold_spearman"].iloc[0]) > float(q2_diag["null_p95"].iloc[0])
        and float(q2_diag["group_spearman"].iloc[0]) > 0.02
    )
    s1_predictive_ok = bool(
        len(s1_diag)
        and float(s1_diag["kfold_spearman"].iloc[0]) > float(s1_diag["null_p95"].iloc[0])
        and float(s1_diag["group_spearman"].iloc[0]) > 0.02
    )
    rowmask_predictive_ok = bool(q2_predictive_ok and s1_predictive_ok)
    stability_cols = [c for c in ["public_validity_Q2_spearman", "public_validity_S1_spearman"] if c in stability.columns]
    stability_min = float(stability[stability_cols].min().min()) if len(stability) and stability_cols else np.nan
    stability_med = float(stability[stability_cols].median().median()) if len(stability) and stability_cols else np.nan
    rowmask_stable_ok = bool(np.isfinite(stability_min) and stability_min > 0.20 and stability_med > 0.50)
    null_veto = len(best_null) and null_top1 >= max(real_top1 + 0.10, 0.20)
    direct_veto = len(best_diag) and diag_top1 >= max(real_top1 + 0.05, 0.20)

    if not rowmask_predictive_ok:
        decision = "reject_e368_q2s1_masks_not_jointly_predictive_keep_e365"
        chosen_variant = e365_variant
        reason = "Q2/S1 public row-validity must both be predictable from lifestyle/story context; otherwise this is not a joint hidden lifestyle-state translator."
    elif not rowmask_stable_ok:
        decision = "reject_e368_q2s1_public_target_unstable_keep_e365"
        chosen_variant = e365_variant
        reason = "Q2/S1 row-validity changes too much when known public observations are dropped."
    elif null_veto:
        decision = "reject_e368_null_q2s1_mask_wins_keep_e365"
        chosen_variant = e365_variant
        reason = "A null/permuted Q2/S1 mask beats the learned lifestyle masks under jackknife; keep E365."
    elif direct_veto:
        decision = "reject_e368_direct_public_q2s1_mask_wins_keep_e365"
        chosen_variant = e365_variant
        reason = "Direct public Q2/S1 masks beat learned masks; the target exists, but the lifestyle translator has not learned it."
    elif len(best_real) and real_top1 >= max(0.20, e365_top1 + 0.10) and real_pls >= e365_pls - 0.05:
        decision = "select_e368_q2s1_lifestyle_cell_replacement"
        chosen_variant = best_real_variant
        reason = "The learned Q2/S1 lifestyle cell gate beats E365, direct-public controls, and null masks under jackknife stress."
    elif len(best_real) and real_top10 >= e365_top10 + 0.10 and real_pls >= e365_pls + 0.10:
        decision = "select_e368_q2s1_lifestyle_cell_stable_alt"
        chosen_variant = best_real_variant
        reason = "The learned Q2/S1 lifestyle cell gate is more stable top10 and stronger on public-like score than E365."
    else:
        decision = "keep_e365_no_e368_uplift"
        chosen_variant = e365_variant
        reason = "The Q2/S1 row-mask latent is diagnostic, but generated candidates do not beat E365 strongly enough."

    chosen = combined[combined["variant"].astype(str).eq(chosen_variant)].head(1)
    if chosen.empty:
        chosen = combined.head(1)
        chosen_variant = str(chosen.iloc[0]["variant"])
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    src = locate(chosen.iloc[0]["file"])
    upload: Path | None = None
    if decision.startswith("select_") and src is not None:
        upload = copy_uploadsafe(src, chosen_variant)
    else:
        e365_upload = str(pd.read_csv(E365_SELECTION_IN).iloc[0].get("selected_uploadsafe_file", ""))
        upload = locate(e365_upload) if e365_upload else src
    row = chosen.iloc[0].to_dict()
    row.update(
        {
            "decision": decision,
            "reason": reason,
            "scenario_count": int(len(scenarios)),
            "e365_variant": e365_variant,
            "e365_top1_rate": e365_top1,
            "e365_top10_rate": e365_top10,
            "best_real_variant": best_real_variant,
            "best_real_top1_rate": real_top1,
            "best_real_top10_rate": real_top10,
            "best_null_variant": str(best_null.iloc[0]["variant"]) if len(best_null) else "none",
            "best_null_top1_rate": null_top1,
            "best_null_top10_rate": null_top10,
            "best_diagnostic_direct_variant": str(best_diag.iloc[0]["variant"]) if len(best_diag) else "none",
            "best_diagnostic_direct_top1_rate": diag_top1,
            "q2_predictive_ok": q2_predictive_ok,
            "s1_predictive_ok": s1_predictive_ok,
            "rowmask_predictive_ok": rowmask_predictive_ok,
            "rowmask_stable_ok": rowmask_stable_ok,
            "direct_public_veto": direct_veto,
            "rowmask_stability_min": stability_min,
            "rowmask_stability_median": stability_med,
            "e365_public_like_score": e365_pls,
            "best_real_public_like_score": real_pls,
            "selected_uploadsafe_file": rel(upload),
        }
    )
    out = pd.DataFrame([row])
    out.to_csv(SELECTION_OUT, index=False)
    return out


def write_report(
    known_weights: pd.DataFrame,
    diagnostics: pd.DataFrame,
    stability: pd.DataFrame,
    candidates: pd.DataFrame,
    combined: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    scenarios: pd.DataFrame,
    support: pd.DataFrame,
    selected: pd.DataFrame,
) -> None:
    scenario_summary = (
        scenarios.groupby("feature_view")
        .agg(
            scenarios=("scenario_id", "size"),
            top_generated_rate=("top_origin", lambda x: float(np.mean(pd.Series(x).astype(str).eq("e368_generated")))),
            top_e365_rate=("top_is_e365", "mean"),
            e365_rank_mean=("e365_rank", "mean"),
            generated_gated_mean=("generated_gated_count", "mean"),
        )
        .reset_index()
        if not scenarios.empty
        else pd.DataFrame()
    )
    support_cols = [
        "variant",
        "family",
        "candidate_origin",
        "top1_count",
        "top5_count",
        "top10_count",
        "rank_mean",
        "score_mean",
        "pred_mean",
        "file",
    ]
    score_cols = [
        "variant",
        "family",
        "candidate_origin",
        "e368_public_like_score",
        "e368_pred_public_delta_mean",
        "e368_pred_public_delta_std",
        "public_bad_axis_sum",
        "rowstate_pred_public_loss_mean",
        "rowmask_wmean_pred_public_row_validity",
        "rowmask_wmean_pred_public_bad_row_support",
        "rowmask_corr_pred_public_row_validity",
        "rowmask_Q2_wmean_pred_public_validity_Q2",
        "rowmask_S1_wmean_pred_public_validity_S1",
        "e363_submission_gate",
        "file",
    ]
    selection_cols = [
        "decision",
        "variant",
        "family",
        "candidate_origin",
        "selected_uploadsafe_file",
        "scenario_count",
        "q2_predictive_ok",
        "s1_predictive_ok",
        "rowmask_predictive_ok",
        "rowmask_stable_ok",
        "direct_public_veto",
        "rowmask_stability_min",
        "e365_top1_rate",
        "best_real_top1_rate",
        "best_null_top1_rate",
        "e365_top10_rate",
        "best_real_top10_rate",
        "best_null_top10_rate",
        "reason",
    ]
    lines = [
        "# E368 Q2/S1 Row-Mask Cell-Action Latent",
        "",
        "## Question",
        "",
        "Can the Q2 and S1 parts of known public row-validity be translated from lifestyle/story context into a target-cell action that improves the E365 donor-graft family?",
        "",
        "## Method",
        "",
        "- Anchor: E247 public-best probability tensor.",
        "- Context: E328/E358 own-lifestyle state plus human/social story axes.",
        "- Target representation: Q2/S1 row-level public-good support minus public-bad support, built from fixed known-public observations.",
        "- Action: preserve E365 globally, then change only Q2/S1 cells through learned row-validity masks.",
        "- Anti-collapse: Q2/S1 predictability check, leave-public stability, direct-public diagnostic veto, and null/permuted row-mask candidate stress.",
        "",
        "## Public Row-Mask Weights",
        "",
        md_table(known_weights.sort_values("delta_vs_e247").head(20), n=20, floatfmt=".6f"),
        "",
        "## Lifestyle Predictability Diagnostics",
        "",
        md_table(diagnostics, n=20, floatfmt=".6f"),
        "",
        "## Leave-Public Row-Mask Stability",
        "",
        md_table(stability.describe(include="all").reset_index(), n=20, floatfmt=".6f") if not stability.empty else "_No stability rows._",
        "",
        "## Inputs",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- combined pool: `{len(combined)}`",
        f"- feature views: " + ", ".join(f"`{k}`({len(v)})" for k, v in feature_sets.items()),
        "",
        "## Scenario Summary",
        "",
        md_table(scenario_summary, n=20, floatfmt=".6f") if not scenario_summary.empty else "_No scenarios._",
        "",
        "## Top Jackknife Support",
        "",
        md_table(support[[c for c in support_cols if c in support.columns]].head(30), n=30, floatfmt=".6f") if not support.empty else "_No support._",
        "",
        "## Top Public-Like Scores",
        "",
        md_table(combined[[c for c in score_cols if c in combined.columns]].head(30), n=30, floatfmt=".6f"),
        "",
        "## Decision",
        "",
        md_table(selected[[c for c in selection_cols if c in selected.columns]], n=5, floatfmt=".6f"),
        "",
        "## Interpretation",
        "",
        "- If Q2 or S1 cannot be predicted from lifestyle context, the joint hidden-life-state translator is not established.",
        "- If direct public masks beat learned masks, the row target exists but our context-to-target translator is still missing.",
        "- If null row masks beat learned row masks, row placement is still a shortcut.",
        "- Only a learned Q2/S1 candidate that beats direct/null controls and E365 should become a submission.",
        "",
        "## Files",
        "",
        f"- `{rel(ROWMASK_OUT)}`",
        f"- `{rel(KNOWN_OUT)}`",
        f"- `{rel(DIAGNOSTICS_OUT)}`",
        f"- `{rel(STABILITY_OUT)}`",
        f"- `{rel(CANDIDATES_OUT)}`",
        f"- `{rel(SCORES_OUT)}`",
        f"- `{rel(SCENARIOS_OUT)}`",
        f"- `{rel(SUPPORT_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    anchor_logit_frame = logit_frame(OUT / ANCHOR_FILE)
    known, known_deltas, _ = load_known(anchor_logit_frame)
    maps, known_weights = build_rowmask_maps(known, known_deltas)
    stability = rowmask_stability(known, known_deltas, maps)
    rowmask, diagnostics = learn_rowmask_latent(anchor, state, base_cols, story_cols, maps)
    candidates, _ = generate_candidates(anchor, anchor_logit, state, rowmask, base_cols, story_cols)
    selector = selector_scores(candidates, anchor)
    rowstate = rowstate_public_scores(selector, anchor, anchor_logit, state, base_cols, story_cols)
    e363_scored = add_e363_scores(rowstate)
    combined, known_scored, _ = public_score_candidates(e363_scored, rowmask)
    e365_variant = str(pd.read_csv(E365_SELECTION_IN).iloc[0]["variant"])
    feature_sets = available_feature_sets(known_scored, combined)
    scenarios, ranks = run_scenarios(known_scored, combined, feature_sets, e365_variant)
    support = aggregate_support(ranks, len(scenarios))
    selected = decide(combined, support, scenarios, diagnostics, stability, e365_variant)
    write_report(known_weights, diagnostics, stability, candidates, combined, feature_sets, scenarios, support, selected)

    print(f"generated_candidates={len(candidates)} combined_pool={len(combined)} scenarios={len(scenarios)}")
    print(f"feature_views={ {k: len(v) for k, v in feature_sets.items()} }")
    print(diagnostics.round(6).to_string(index=False))
    print(support[["variant", "family", "candidate_origin", "top1_count", "top10_count", "rank_mean", "score_mean"]].head(12).round(6).to_string(index=False))
    print(
        selected[
            [
                "decision",
                "variant",
                "family",
                "candidate_origin",
                "selected_uploadsafe_file",
                "q2_predictive_ok",
                "s1_predictive_ok",
                "rowmask_stable_ok",
                "direct_public_veto",
                "best_real_top1_rate",
                "best_null_top1_rate",
            ]
        ]
        .round(6)
        .to_string(index=False)
    )
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
