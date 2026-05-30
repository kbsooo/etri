#!/usr/bin/env python3
"""E303: materialize the E302 S4 mean-placement prior.

E302 found weak but real human-diary signal for S4 placement mean health. This
script turns that diagnostic into a constrained candidate generator:

1. Fit placement-health decoders on E301 null placements.
2. Generate S4-only masks from the E299 parent movement, ranked by predicted
   mean placement health rather than p90.
3. Prefilter with the current-anchor selector.
4. Confirm selected candidates against row/subject/dateblock/sign nulls.

No public LB is used.
"""

from __future__ import annotations

import hashlib
from itertools import combinations
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e303_s4_mean_prior_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e300_s4_mean_dominance_rescue import as_bool, load_current_and_meta, rel, safe_id, short_hash, sigmoid  # noqa: E402
from e302_s4_placement_health_decoder import (  # noqa: E402
    aggregate_placement,
    feature_sets,
    load_placement_table,
    s4_delta_for,
    test_human_features,
)
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, clip_prob, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

PARENT = OUT / "submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv"
E300_READY = OUT / "submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv"

S4_IDX = TARGETS.index("S4")
RNG_SEED = 20260531 + 303
MULTS = [0.85, 0.97, 1.00, 1.08, 1.16]
MAX_PREFILTER = 260
MAX_NULL_EVAL = 12
N_CONFIRM_REPS = 32

ROW_PRIOR_OUT = OUT / "e303_s4_mean_prior_row_scores.csv"
CANDIDATE_OUT = OUT / "e303_s4_mean_prior_candidates.csv"
PREFILTER_OUT = OUT / "e303_s4_mean_prior_prefilter.csv"
GOVERNOR_OUT = OUT / "e303_s4_mean_prior_governor.csv"
NULL_MAP_OUT = OUT / "e303_s4_mean_prior_null_map.csv"
SCORE_OUT = OUT / "e303_s4_mean_prior_scores.csv"
SUMMARY_OUT = OUT / "e303_s4_mean_prior_summary.csv"
REPORT_OUT = OUT / "e303_s4_mean_prior_report.md"


def md(frame: pd.DataFrame, columns: list[str] | None = None, n: int = 25) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if columns is None else frame.loc[:, [c for c in columns if c in frame.columns]]
    out = view.head(n).copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    out = out.fillna("").astype(str)
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *rows])


def write_submission(current: pd.DataFrame, delta: np.ndarray, tag: str, null: bool = False) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    base = NULL_DIR if null else OUT
    base.mkdir(exist_ok=True)
    prefix = "submission_e303null" if null else "submission_e303_s4meanprior"
    path = base / f"{prefix}_{safe_id(tag, 104)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def score_paths(paths: list[Path], current: pd.DataFrame) -> pd.DataFrame:
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    rows: list[dict[str, Any]] = []
    for path in [OUT / CURRENT, *paths]:
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel(path)
        row["source_path"] = rel(path)
        row["basename"] = path.name
        rows.append(row)
    features = pd.DataFrame(rows)
    return score_candidates(known, features, model_df)


def source_delta(current: pd.DataFrame) -> np.ndarray:
    parent = load_sub(PARENT, current).sort_values(KEYS).reset_index(drop=True)
    return logit(parent[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def fit_decoders(current: pd.DataFrame, meta: pd.DataFrame, row_features: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame]:
    placements = load_placement_table()
    rows: list[dict[str, Any]] = []
    for rec in placements.to_dict("records"):
        path = Path(str(rec["source_path"]))
        if not path.is_absolute():
            path = ROOT / path
        delta = np.zeros((len(current), len(TARGETS)), dtype=np.float64)
        delta[:, S4_IDX] = s4_delta_for(path, current)
        rows.append({**rec, **aggregate_placement(delta[:, S4_IDX], row_features, meta)})
    frame = pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    nulls = frame[~frame["is_actual"]].reset_index(drop=True)
    sets = feature_sets(frame)
    decoders: dict[str, Any] = {"sets": sets, "nulls": nulls}
    for set_name in ["human_all", "human_all_plus_topology", "story_episode", "topology"]:
        cols = sets[set_name]
        mean_model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=25.0))
        p90_model = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), Ridge(alpha=25.0))
        strict_model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=0.25, max_iter=1000, solver="lbfgs"),
        )
        mean_model.fit(nulls[cols], nulls["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64))
        p90_model.fit(nulls[cols], nulls["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64))
        y_strict = nulls["strict_bool"].astype(int).to_numpy()
        strict_model.fit(nulls[cols], y_strict)
        decoders[set_name] = {
            "columns": cols,
            "mean_model": mean_model,
            "p90_model": p90_model,
            "strict_model": strict_model,
        }
    return decoders, frame


def decoder_predictions(delta_s4: np.ndarray, row_features: pd.DataFrame, meta: pd.DataFrame, decoders: dict[str, Any]) -> dict[str, float]:
    rec = aggregate_placement(delta_s4, row_features, meta)
    df = pd.DataFrame([rec]).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    out: dict[str, float] = {}
    for set_name in ["human_all", "human_all_plus_topology", "story_episode", "topology"]:
        info = decoders[set_name]
        cols = info["columns"]
        out[f"{set_name}_mean_pred"] = float(info["mean_model"].predict(df[cols])[0])
        out[f"{set_name}_p90_pred"] = float(info["p90_model"].predict(df[cols])[0])
        out[f"{set_name}_strict_prob"] = float(info["strict_model"].predict_proba(df[cols])[:, 1][0])
    out["prior_score"] = (
        out["human_all_mean_pred"]
        + 0.60 * out["human_all_plus_topology_mean_pred"]
        + 0.25 * out["story_episode_mean_pred"]
        + 0.15 * out["topology_mean_pred"]
    )
    out["prior_p90_score"] = (
        out["human_all_p90_pred"]
        + 0.50 * out["human_all_plus_topology_p90_pred"]
        + 0.25 * out["topology_p90_pred"]
    )
    out["prior_strict_prob"] = float(
        np.mean(
            [
                out["human_all_strict_prob"],
                out["human_all_plus_topology_strict_prob"],
                out["story_episode_strict_prob"],
                out["topology_strict_prob"],
            ]
        )
    )
    return out


def build_row_scores(source_s4: np.ndarray, row_features: pd.DataFrame, meta: pd.DataFrame, decoders: dict[str, Any]) -> pd.DataFrame:
    active = np.flatnonzero(np.abs(source_s4) > 1.0e-12)
    all_delta = source_s4.copy()
    base_pred = decoder_predictions(all_delta, row_features, meta, decoders)
    rows: list[dict[str, Any]] = []
    for idx in active:
        singleton = np.zeros_like(source_s4)
        singleton[idx] = source_s4[idx]
        single_pred = decoder_predictions(singleton, row_features, meta, decoders)
        dropped = all_delta.copy()
        dropped[idx] = 0.0
        drop_pred = decoder_predictions(dropped, row_features, meta, decoders)
        rows.append(
            {
                "row_idx": int(idx),
                **meta.loc[idx, KEYS + ["dateblock_group"]].to_dict(),
                "s4_source_delta": float(source_s4[idx]),
                "sign": "pos" if source_s4[idx] > 0 else "neg",
                "singleton_prior_score": single_pred["prior_score"],
                "drop_prior_score": drop_pred["prior_score"],
                "drop_improvement_vs_all": float(drop_pred["prior_score"] - base_pred["prior_score"]),
                "human_all_single_mean": single_pred["human_all_mean_pred"],
                "human_all_plus_topology_single_mean": single_pred["human_all_plus_topology_mean_pred"],
                "story_single_mean": single_pred["story_episode_mean_pred"],
                "prior_strict_prob_single": single_pred["prior_strict_prob"],
            }
        )
    return pd.DataFrame(rows).sort_values(["singleton_prior_score", "drop_improvement_vs_all"]).reset_index(drop=True)


def add_mask(masks: list[tuple[str, np.ndarray]], name: str, mask: np.ndarray) -> None:
    mask = np.asarray(mask, dtype=bool)
    if mask.any():
        masks.append((safe_id(name), mask))


def build_masks(source_s4: np.ndarray, row_scores: pd.DataFrame, meta: pd.DataFrame, row_features: pd.DataFrame, decoders: dict[str, Any]) -> list[tuple[str, np.ndarray]]:
    n = len(source_s4)
    active = np.abs(source_s4) > 1.0e-12
    pos = source_s4 > 1.0e-12
    neg = source_s4 < -1.0e-12
    masks: list[tuple[str, np.ndarray]] = []
    add_mask(masks, "all_parent", active)
    add_mask(masks, "pos_only", pos)
    add_mask(masks, "neg_only", neg)
    add_mask(masks, "e300_ready_shape", np.abs(s4_delta_for(E300_READY, load_current_and_meta()[0])) > 1.0e-12)

    ordered_single = row_scores.sort_values("singleton_prior_score")
    ordered_drop = row_scores.sort_values("drop_improvement_vs_all")
    for k in [20, 24, 28, 32, 36, 40, 44, 47, 50]:
        idx = ordered_single["row_idx"].head(k).to_numpy(dtype=int)
        add_mask(masks, f"single_prior_top{k}", np.isin(np.arange(n), idx) & active)
    for k in [2, 3, 5, 8, 12, 16]:
        bad_idx = ordered_single["row_idx"].tail(k).to_numpy(dtype=int)
        add_mask(masks, f"single_prior_drop_worst{k}", active & ~np.isin(np.arange(n), bad_idx))
        drop_bad = ordered_drop["row_idx"].head(k).to_numpy(dtype=int)
        add_mask(masks, f"drop_prior_bestdrop{k}", active & ~np.isin(np.arange(n), drop_bad))

    # Subject and dateblock masks from human prior predictions.
    for subject, idxs in meta.groupby("subject_id").indices.items():
        idx = np.asarray(list(idxs), dtype=int)
        if np.sum(active[idx]) >= 1:
            add_mask(masks, f"drop_subject_{subject}", active & ~np.isin(np.arange(n), idx))
            add_mask(masks, f"keep_subject_{subject}", active & np.isin(np.arange(n), idx))
    block_scores: list[tuple[str, float]] = []
    for group, idxs in meta.groupby("dateblock_group").indices.items():
        idx = np.asarray(list(idxs), dtype=int)
        if np.sum(active[idx]) < 1:
            continue
        drop = source_s4.copy()
        drop[idx] = 0.0
        pred = decoder_predictions(drop, row_features, meta, decoders)
        block_scores.append((str(group), pred["prior_score"]))
        add_mask(masks, f"drop_dateblock_{group}", active & ~np.isin(np.arange(n), idx))
        if np.sum(active[idx]) >= 2:
            add_mask(masks, f"keep_dateblock_{group}", active & np.isin(np.arange(n), idx))
    block_scores = sorted(block_scores, key=lambda x: x[1])
    for k in [1, 2, 3, 4]:
        for combo in combinations([b for b, _score in block_scores[:8]], k):
            bad = set(combo)
            drop_idx = meta.index[meta["dateblock_group"].astype(str).isin(bad)].to_numpy(dtype=int)
            add_mask(masks, f"drop_prior_dateblocks_{'_'.join(combo)}", active & ~np.isin(np.arange(n), drop_idx))
            if len(masks) > 220:
                break
        if len(masks) > 220:
            break

    # Deduplicate by packed mask.
    seen: set[bytes] = set()
    unique: list[tuple[str, np.ndarray]] = []
    for name, mask in masks:
        key = np.packbits(mask).tobytes()
        if key in seen:
            continue
        seen.add(key)
        unique.append((name, mask))
    return unique


def materialize_candidates(
    source_s4: np.ndarray,
    current: pd.DataFrame,
    meta: pd.DataFrame,
    row_features: pd.DataFrame,
    decoders: dict[str, Any],
    masks: list[tuple[str, np.ndarray]],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    for mask_name, mask in masks:
        for mult in MULTS:
            delta = np.zeros((len(current), len(TARGETS)), dtype=np.float64)
            delta[mask, S4_IDX] = source_s4[mask] * mult
            if np.count_nonzero(np.abs(delta[:, S4_IDX]) > 1.0e-12) < 2:
                continue
            pred = decoder_predictions(delta[:, S4_IDX], row_features, meta, decoders)
            tag = f"{mask_name}_raw_m{mult:.2f}".replace(".", "p")
            path = write_submission(current, delta, tag)
            deltas[path.name] = delta
            rows.append(
                {
                    "basename": path.name,
                    "source_path": rel(path),
                    "mask_name": mask_name,
                    "multiplier": float(mult),
                    "nonzero_rows": int(np.count_nonzero(np.abs(delta[:, S4_IDX]) > 1.0e-12)),
                    "pos_rows": int(np.count_nonzero(delta[:, S4_IDX] > 1.0e-12)),
                    "neg_rows": int(np.count_nonzero(delta[:, S4_IDX] < -1.0e-12)),
                    "mean_abs_s4_delta": float(np.mean(np.abs(delta[:, S4_IDX]))),
                    "max_abs_s4_delta": float(np.max(np.abs(delta[:, S4_IDX]))),
                    **pred,
                }
            )
    candidates = pd.DataFrame(rows).sort_values(["prior_score", "prior_p90_score"]).head(MAX_PREFILTER).reset_index(drop=True)
    deltas = {b: deltas[b] for b in candidates["basename"] if b in deltas}
    return candidates, deltas


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    strict = prefilter[prefilter["strict_promote_gate"].map(as_bool)].copy()
    if strict.empty:
        pool = prefilter.copy()
    else:
        pool = strict
    pool["selection_score"] = (
        pool["pred_delta_vs_current_p90"].fillna(0.0)
        + 0.35 * pool["pred_delta_vs_current_mean"].fillna(0.0)
        + 0.25 * pool["prior_score"].fillna(0.0)
        + 0.00003 * pool["null_like_penalty"].fillna(0.0)
    )
    by_prior = pool.sort_values(["prior_score", "pred_delta_vs_current_p90"]).head(MAX_NULL_EVAL // 3 + 1)
    by_selector = pool.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 3 + 1)
    by_combo = pool.sort_values(["selection_score"]).head(MAX_NULL_EVAL)
    return pd.concat([by_prior, by_selector, by_combo], ignore_index=True).drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def write_null_candidate(current: pd.DataFrame, delta: np.ndarray, basename: str, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    seed_text = f"{basename}|{mode}|{rep}|e303"
    rng = np.random.default_rng(int(hashlib.sha1(seed_text.encode()).hexdigest()[:8], 16))
    values = np.asarray(delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values)), :]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(list(idx), dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr, :] = values[idx_arr, :][rng.permutation(len(idx_arr)), :]
    elif mode == "sign":
        active = np.flatnonzero(np.max(np.abs(values), axis=1) > 1.0e-12)
        flips = rng.choice(np.array([-1.0, 1.0]), size=len(active))
        shuffled[active, :] = values[active, :] * flips[:, None]
    else:
        raise ValueError(mode)
    return write_submission(current, shuffled, f"{Path(basename).stem}_{mode}_r{rep:02d}", null=True)


def run_governor(selected: pd.DataFrame, deltas: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        delta = deltas[basename]
        for mode in ["row", "subject", "dateblock", "sign"]:
            for rep in range(N_CONFIRM_REPS):
                path = write_null_candidate(current, delta, basename, meta, mode, rep)
                null_paths.append(path)
                null_rows.append({"source_basename": basename, "null_basename": path.name, "null_path": rel(path), "mode": mode, "rep": rep})
    null_map = pd.DataFrame(null_rows)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    paths = [OUT / str(b) for b in selected["basename"]]
    scores = score_paths([*paths, *null_paths], current)
    scores.to_csv(SCORE_OUT, index=False)
    cand_scores = scores[scores["basename"].isin(selected["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()

    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        actual = cand_scores[cand_scores["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these = null_scores[null_scores["basename"].isin(null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        p90_vals = these["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        actual_p90 = float(a["pred_delta_vs_current_p90"])
        actual_mean = float(a["pred_delta_vs_current_mean"])
        null_strict = float(these["strict_promote_gate"].map(as_bool).mean()) if len(these) else 1.0
        p90_dom = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dom = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_p90 = []
        mode_mean = []
        mode_strict: dict[str, float] = {}
        for mode, part in these.groupby("mode"):
            mode_p90.append(float(np.mean(actual_p90 < part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64))))
            mode_mean.append(float(np.mean(actual_mean < part["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64))))
            mode_strict[f"{mode}_null_strict_rate"] = float(part["strict_promote_gate"].map(as_bool).mean())
        worst_p90 = float(min(mode_p90)) if mode_p90 else 0.0
        worst_mean = float(min(mode_mean)) if mode_mean else 0.0
        sign_part = these[these["mode"].eq("sign")]
        sign_p90 = float(np.mean(actual_p90 < sign_part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64))) if len(sign_part) else 0.0
        ready = bool(
            as_bool(a["strict_promote_gate"])
            and null_strict <= 0.10
            and p90_dom >= 0.80
            and mean_dom >= 0.70
            and worst_p90 >= 0.60
            and worst_mean >= 0.50
            and sign_p90 >= 0.75
        )
        rows.append(
            {
                **cand.to_dict(),
                "actual_strict_promote": as_bool(a["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these)),
                "null_strict_rate": null_strict,
                "p90_dominance": p90_dom,
                "mean_dominance": mean_dom,
                "worst_mode_p90_dominance": worst_p90,
                "worst_mode_mean_dominance": worst_mean,
                "sign_p90_dominance": sign_p90,
                "public_free_ready": ready,
                "decision": "candidate_ready_needs_64rep_confirm" if ready else "do_not_submit",
                **mode_strict,
            }
        )
    governor = pd.DataFrame(rows).sort_values(
        ["public_free_ready", "null_strict_rate", "mean_dominance", "actual_p90"],
        ascending=[False, True, False, True],
    ).reset_index(drop=True)
    governor.to_csv(GOVERNOR_OUT, index=False)
    return null_map, governor


def write_report(row_scores: pd.DataFrame, candidates: pd.DataFrame, prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_ready"].map(as_bool)] if not governor.empty else pd.DataFrame()
    summary = pd.DataFrame(
        [
            {
                "generated_candidates": len(candidates),
                "prefilter_scored": len(prefilter),
                "old_strict": int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0,
                "null_evaluated": len(selected),
                "ready_32rep": len(ready),
                "best_null_strict_rate": float(governor["null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_mean_dominance": float(governor["mean_dominance"].max()) if not governor.empty else np.nan,
                "best_actual_p90": float(governor["actual_p90"].min()) if not governor.empty else np.nan,
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)

    lines = [
        "# E303 S4 Mean-Placement Prior Materializer",
        "",
        "Public LB는 사용하지 않았다. E302 mean-placement decoder를 실제 S4 mask generator로 바꿔도 large-null gate를 통과하는지 검사했다.",
        "",
        "## Summary",
        "",
        md(summary, n=5),
        "",
        "## Best Row Prior Scores",
        "",
        md(
            row_scores,
            [
                "row_idx",
                "subject_id",
                "sleep_date",
                "dateblock_group",
                "s4_source_delta",
                "sign",
                "singleton_prior_score",
                "drop_improvement_vs_all",
                "human_all_single_mean",
                "story_single_mean",
            ],
            n=20,
        ),
        "",
        "## Best Prefilter Rows",
        "",
        md(
            prefilter,
            [
                "basename",
                "mask_name",
                "multiplier",
                "nonzero_rows",
                "prior_score",
                "human_all_mean_pred",
                "pred_delta_vs_current_mean",
                "pred_delta_vs_current_p90",
                "strict_promote_gate",
                "pred_beats_current_rate",
            ],
            n=20,
        ),
        "",
        "## Governor Rows",
        "",
        md(
            governor,
            [
                "basename",
                "mask_name",
                "multiplier",
                "nonzero_rows",
                "actual_mean",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "mean_dominance",
                "worst_mode_p90_dominance",
                "worst_mode_mean_dominance",
                "public_free_ready",
                "decision",
            ],
            n=30,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines += [
            "- A 32-rep public-free candidate exists, but it still needs E301-equivalent 64-rep confirmation before any public LB use.",
        ]
    else:
        lines += [
            "- No E303 candidate survives the 32-rep/mode large-null governor.",
            "- The E302 mean-placement prior is diagnostic, not yet a submission generator.",
            "- This weakens the current S4 mask-surgery branch; the next S4 attempt must add a genuinely new block-placement target or the branch should yield to broader episode/block-state work.",
        ]
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{rel(ROW_PRIOR_OUT)}`",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(PREFILTER_OUT)}`",
        f"- `{rel(GOVERNOR_OUT)}`",
        f"- `{rel(SUMMARY_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    current, meta = load_current_and_meta()
    row_features, _feature_meta = test_human_features(current)
    decoders, placement_frame = fit_decoders(current, meta, row_features)
    source = source_delta(current)[:, S4_IDX]
    row_scores = build_row_scores(source, row_features, meta, decoders)
    row_scores.to_csv(ROW_PRIOR_OUT, index=False)
    masks = build_masks(source, row_scores, meta, row_features, decoders)
    candidates, deltas = materialize_candidates(source, current, meta, row_features, decoders, masks)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    scored = score_paths([OUT / b for b in candidates["basename"]], current)
    score_cols = [
        "basename",
        "promotion_decision",
        "strict_promote_gate",
        "info_sensor_gate",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    prefilter = candidates.merge(scored[score_cols], on="basename", how="left")
    nulls = placement_frame[~placement_frame["is_actual"]]
    prefilter["null_like_penalty"] = np.minimum(
        np.abs(prefilter["human_all_mean_pred"].to_numpy() - float(nulls["pred_delta_vs_current_mean"].median())) / 1.0e-5,
        20.0,
    )
    prefilter = prefilter.sort_values(
        ["strict_promote_gate", "prior_score", "pred_delta_vs_current_p90"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    prefilter.to_csv(PREFILTER_OUT, index=False)
    selected = select_for_null(prefilter)
    _null_map, governor = run_governor(selected, deltas, current, meta)
    write_report(row_scores, candidates, prefilter, selected, governor)

    print(f"generated={len(candidates)} old_strict={int(prefilter['strict_promote_gate'].map(as_bool).sum())} null_eval={len(selected)} ready={int(governor['public_free_ready'].map(as_bool).sum()) if not governor.empty else 0}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
