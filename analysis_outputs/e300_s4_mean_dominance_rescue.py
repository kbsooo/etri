#!/usr/bin/env python3
"""E300: rescue the S4 mean-dominance failure from E299.

E299 found a near-miss S4 lifestyle candidate:

    old strict: yes
    p90 edge: yes
    null strict: 0.095
    p90/worst-mode dominance: yes
    mean dominance: no

This script asks whether that last failure is fixable by changing row/sign/mask
placement, without touching public LB. It uses row-level public-free selector
probes only to propose masks, and then applies the same matched row/subject/
dateblock null governor as E299.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e300_s4_mean_dominance_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import load_frames  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import normalize_keys, prep_test_meta  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, clip_prob, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

SOURCE = OUT / "submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv"

ROW_PROBE_OUT = OUT / "e300_s4_mean_dominance_row_probes.csv"
CANDIDATE_OUT = OUT / "e300_s4_mean_dominance_candidates.csv"
PREFILTER_OUT = OUT / "e300_s4_mean_dominance_prefilter.csv"
GOVERNOR_OUT = OUT / "e300_s4_mean_dominance_governor.csv"
SCORE_OUT = OUT / "e300_s4_mean_dominance_scores.csv"
NULL_MAP_OUT = OUT / "e300_s4_mean_dominance_null_map.csv"
REPORT_OUT = OUT / "e300_s4_mean_dominance_report.md"

MAX_NULL_EVAL = 120
N_TEST_NULL_REPS = 7
S4_IDX = TARGETS.index("S4")
MASK_MULTS = [0.85, 0.97, 1.00, 1.08, 1.16]
PROBE_SCALE = 1.0


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def safe_id(text: str, limit: int = 92) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def as_bool(value: Any) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, float, np.integer, np.floating)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def md_table(df: pd.DataFrame, columns: list[str], n: int = 20) -> str:
    if df.empty:
        return "_없음_"
    view = df.loc[:, columns].head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{x:.9f}")
    view = view.fillna("").astype(str)
    header = "| " + " | ".join(view.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(view.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in view.to_numpy()]
    return "\n".join([header, sep, *rows])


def load_current_and_meta() -> tuple[pd.DataFrame, pd.DataFrame]:
    base, _raw, *_rest = load_frames()
    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = prep_test_meta(test_df)
    merged = normalize_keys(current[KEYS]).merge(meta, on=KEYS, how="left", validate="one_to_one")
    if merged["dateblock_group"].isna().any():
        raise RuntimeError("Could not align dateblock metadata to current")
    return current, merged.reset_index(drop=True)


def source_delta(current: pd.DataFrame) -> np.ndarray:
    source = load_sub(SOURCE, current).sort_values(KEYS).reset_index(drop=True)
    delta = logit(source[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))
    return delta


def write_candidate(current: pd.DataFrame, delta: np.ndarray, tag: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e300_s4mean_{safe_id(tag)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def write_null_candidate(current: pd.DataFrame, applied_delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    seed_text = f"{source_path.name}|{mode}|{rep}|e300"
    rng = np.random.default_rng(int(hashlib.sha1(seed_text.encode()).hexdigest()[:8], 16))
    values = np.asarray(applied_delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values)), :]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr, :] = values[idx_arr, :][rng.permutation(len(idx_arr)), :]
    else:
        raise ValueError(mode)

    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + shuffled
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e300null_{safe_id(source_path.stem, 86)}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel(path)
        row["source_path"] = rel(path)
        row["basename"] = path.name
        rows.append(row)
    return pd.DataFrame(rows)


def score_paths(paths: list[Path], current: pd.DataFrame) -> pd.DataFrame:
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = feature_rows([OUT / CURRENT, *paths], sample, refs, ref_vecs)
    return score_candidates(known, features, model_df)


def row_probe_scores(delta: np.ndarray, current: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    s4 = delta[:, S4_IDX]
    idx = np.flatnonzero(np.abs(s4) > 1.0e-12)
    paths: list[Path] = []
    rows: list[dict[str, Any]] = []
    for row_idx in idx:
        probe = np.zeros_like(delta)
        probe[row_idx, S4_IDX] = PROBE_SCALE * s4[row_idx]
        path = write_candidate(current, probe, f"probe_r{row_idx:03d}")
        paths.append(path)
        rows.append(
            {
                "basename": path.name,
                "row_idx": int(row_idx),
                "s4_delta": float(s4[row_idx]),
                "abs_s4_delta": float(abs(s4[row_idx])),
                "sign": "pos" if s4[row_idx] > 0 else "neg",
                **meta.loc[row_idx, KEYS + ["dateblock_group"]].to_dict(),
            }
        )
    probes = pd.DataFrame(rows)
    scores = score_paths(paths, current)
    keep = [
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
    out = probes.merge(scores[keep], on="basename", how="left")
    out["row_score"] = (
        out["pred_delta_vs_current_mean"].fillna(0.0)
        + out["pred_delta_vs_current_p90"].fillna(0.0)
        + 0.00005 * (1.0 - out["pred_beats_current_rate"].fillna(0.0))
    )
    return out.sort_values("row_score").reset_index(drop=True)


def add_mask(masks: list[tuple[str, np.ndarray]], name: str, mask: np.ndarray) -> None:
    clean = np.asarray(mask, dtype=bool)
    if clean.any():
        masks.append((safe_id(name), clean))


def build_masks(delta: np.ndarray, meta: pd.DataFrame, probes: pd.DataFrame) -> list[tuple[str, np.ndarray]]:
    s4 = delta[:, S4_IDX]
    nonzero = np.abs(s4) > 1.0e-12
    pos = s4 > 1.0e-12
    neg = s4 < -1.0e-12
    masks: list[tuple[str, np.ndarray]] = []
    add_mask(masks, "all", nonzero)
    add_mask(masks, "pos_only", pos)
    add_mask(masks, "neg_only", neg)
    add_mask(masks, "abs_top20", np.isin(np.arange(len(s4)), np.argsort(np.abs(s4))[::-1][:20]) & nonzero)
    add_mask(masks, "abs_top35", np.isin(np.arange(len(s4)), np.argsort(np.abs(s4))[::-1][:35]) & nonzero)
    add_mask(masks, "pos_cap", pos & (np.abs(s4) >= np.quantile(np.abs(s4[nonzero]), 0.70)))
    add_mask(masks, "neg_cap", neg & (np.abs(s4) >= np.quantile(np.abs(s4[nonzero]), 0.70)))

    ordered = probes.sort_values("row_score")
    for k in [8, 12, 16, 20, 28, 36]:
        add_mask(masks, f"probe_top{k}", np.isin(np.arange(len(s4)), ordered["row_idx"].head(k).to_numpy()) & nonzero)
    for k in [8, 12, 16, 20]:
        best_pos = ordered[ordered["sign"].eq("pos")]["row_idx"].head(k).to_numpy()
        best_neg = ordered[ordered["sign"].eq("neg")]["row_idx"].head(k).to_numpy()
        add_mask(masks, f"probe_pos_top{k}", np.isin(np.arange(len(s4)), best_pos) & nonzero)
        add_mask(masks, f"probe_neg_top{k}", np.isin(np.arange(len(s4)), best_neg) & nonzero)
        add_mask(masks, f"probe_mix_pos{k}_neg{k}", np.isin(np.arange(len(s4)), np.r_[best_pos, best_neg]) & nonzero)

    for subject, idxs in meta.groupby("subject_id").indices.items():
        idx_mask = np.isin(np.arange(len(s4)), np.asarray(list(idxs), dtype=int))
        add_mask(masks, f"keep_subject_{subject}", nonzero & idx_mask)
        add_mask(masks, f"drop_subject_{subject}", nonzero & ~idx_mask)
        add_mask(masks, f"keep_subject_{subject}_pos", pos & idx_mask)
        add_mask(masks, f"keep_subject_{subject}_neg", neg & idx_mask)
        add_mask(masks, f"drop_subject_{subject}_neg", nonzero & ~(neg & idx_mask))
        add_mask(masks, f"drop_subject_{subject}_pos", nonzero & ~(pos & idx_mask))

    for group, idxs in meta.groupby("dateblock_group").indices.items():
        idx_mask = np.isin(np.arange(len(s4)), np.asarray(list(idxs), dtype=int))
        if np.sum(nonzero & idx_mask) >= 2:
            add_mask(masks, f"keep_dateblock_{group}", nonzero & idx_mask)
            add_mask(masks, f"drop_dateblock_{group}", nonzero & ~idx_mask)

    # Balanced masks: choose the best rows within each subject so subject-level
    # shuffles have less freedom to beat the real placement.
    for k_sub in [2, 3, 4, 5, 6]:
        chosen: list[int] = []
        for _subject, part in ordered.groupby("subject_id", sort=False):
            chosen.extend(part["row_idx"].head(k_sub).astype(int).tolist())
        add_mask(masks, f"probe_top{k_sub}_per_subject", np.isin(np.arange(len(s4)), chosen) & nonzero)

    dedup: dict[bytes, str] = {}
    unique: list[tuple[str, np.ndarray]] = []
    for name, mask in masks:
        key = np.packbits(mask).tobytes()
        if key in dedup:
            continue
        dedup[key] = name
        unique.append((name, mask))
    return unique


def transform_delta(delta: np.ndarray, mask: np.ndarray, mult: float, transform: str) -> np.ndarray:
    out = np.zeros_like(delta)
    s4 = delta[:, S4_IDX].copy()
    if transform == "raw":
        vals = s4
    elif transform == "abs_pos":
        vals = np.abs(s4)
    elif transform == "abs_neg":
        vals = -np.abs(s4)
    elif transform == "demean_subject":
        vals = s4.copy()
        # Demean over selected rows only within each subject by a lightweight
        # deterministic loop supplied by the caller via mask groups later.
    else:
        raise ValueError(transform)
    out[mask, S4_IDX] = mult * vals[mask]
    return out


def apply_subject_demean(applied: np.ndarray, mask: np.ndarray, meta: pd.DataFrame) -> np.ndarray:
    out = applied.copy()
    vals = out[:, S4_IDX]
    for _subject, idxs in meta.groupby("subject_id").indices.items():
        idx = np.asarray(list(idxs), dtype=int)
        sel = idx[mask[idx]]
        if len(sel) >= 2:
            vals[sel] = vals[sel] - float(vals[sel].mean())
    out[:, S4_IDX] = vals
    return out


def generate_candidates(delta: np.ndarray, current: pd.DataFrame, meta: pd.DataFrame, probes: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    masks = build_masks(delta, meta, probes)
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    transforms = ["raw", "abs_pos", "abs_neg"]
    for mask_name, mask in masks:
        for transform in transforms:
            for mult in MASK_MULTS:
                applied = transform_delta(delta, mask, mult, transform)
                if np.count_nonzero(np.abs(applied) > 1.0e-12) < 2:
                    continue
                tag = f"{mask_name}_{transform}_m{mult:.2f}".replace(".", "p")
                path = write_candidate(current, applied, tag)
                deltas[path.name] = applied
                rows.append(
                    {
                        "basename": path.name,
                        "source_path": rel(path),
                        "mask_name": mask_name,
                        "transform": transform,
                        "multiplier": float(mult),
                        "nonzero_rows": int(np.count_nonzero(np.max(np.abs(applied), axis=1) > 1.0e-12)),
                        "pos_rows": int(np.count_nonzero(applied[:, S4_IDX] > 1.0e-12)),
                        "neg_rows": int(np.count_nonzero(applied[:, S4_IDX] < -1.0e-12)),
                        "mean_abs_delta": float(np.mean(np.abs(applied[:, S4_IDX]))),
                        "max_abs_delta": float(np.max(np.abs(applied[:, S4_IDX]))),
                    }
                )
                if transform == "raw":
                    centered = apply_subject_demean(applied, mask, meta)
                    if np.count_nonzero(np.abs(centered) > 1.0e-12) >= 2:
                        ctag = f"{mask_name}_subject_demean_m{mult:.2f}".replace(".", "p")
                        cpath = write_candidate(current, centered, ctag)
                        deltas[cpath.name] = centered
                        rows.append(
                            {
                                "basename": cpath.name,
                                "source_path": rel(cpath),
                                "mask_name": mask_name,
                                "transform": "subject_demean",
                                "multiplier": float(mult),
                                "nonzero_rows": int(np.count_nonzero(np.max(np.abs(centered), axis=1) > 1.0e-12)),
                                "pos_rows": int(np.count_nonzero(centered[:, S4_IDX] > 1.0e-12)),
                                "neg_rows": int(np.count_nonzero(centered[:, S4_IDX] < -1.0e-12)),
                                "mean_abs_delta": float(np.mean(np.abs(centered[:, S4_IDX]))),
                                "max_abs_delta": float(np.max(np.abs(centered[:, S4_IDX]))),
                            }
                        )
    meta_df = pd.DataFrame(rows).drop_duplicates("basename").reset_index(drop=True)
    return meta_df, deltas


def score_prefilter(candidate_meta: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    if candidate_meta.empty:
        return candidate_meta
    scores = score_paths([OUT / b for b in candidate_meta["basename"]], current)
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
    return candidate_meta.merge(scores[score_cols], on="basename", how="left").sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    if prefilter.empty:
        return prefilter
    strict = prefilter[prefilter["strict_promote_gate"].map(as_bool)].copy()
    info = prefilter[
        (~prefilter["strict_promote_gate"].map(as_bool))
        & prefilter["info_sensor_gate"].map(as_bool)
        & prefilter["pred_delta_vs_current_p90"].lt(-2.0e-5)
    ].copy()
    source_best = (
        prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby(["mask_name", "transform"], as_index=False)
        .head(1)
    )
    selected = pd.concat(
        [
            strict.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 2),
            info.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 4),
            source_best,
        ],
        ignore_index=True,
    )
    if selected.empty:
        selected = prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL)
    return selected.drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def run_governor(selected: pd.DataFrame, deltas: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return selected, pd.DataFrame(), pd.DataFrame()

    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        applied = deltas[basename]
        source_path = OUT / basename
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_TEST_NULL_REPS):
                null_path = write_null_candidate(current, applied, source_path, meta, mode, rep)
                null_paths.append(null_path)
                null_rows.append(
                    {
                        "source_basename": basename,
                        "null_basename": null_path.name,
                        "null_path": rel(null_path),
                        "mode": mode,
                        "rep": rep,
                    }
                )

    null_map = pd.DataFrame(null_rows)
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / b for b in selected["basename"]]
    features = feature_rows([OUT / CURRENT, *paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    candidate_score = scores[scores["basename"].isin(selected["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        actual = candidate_score[candidate_score["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these_null = null_scores[null_scores["basename"].isin(null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].map(as_bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = []
        mode_mean_doms = []
        for _, part in these_null.groupby("mode"):
            p90_part = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mean_part = part["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
            mode_doms.append(float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_part)))
            mode_mean_doms.append(float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_part)))
        worst_mode = float(min(mode_doms)) if mode_doms else 0.0
        worst_mean_mode = float(min(mode_mean_doms)) if mode_mean_doms else 0.0
        ready = bool(
            old_strict
            and null_strict_rate <= 0.10
            and p90_dominance >= 0.80
            and mean_dominance >= 0.70
            and worst_mode >= 0.55
        )
        rows.append(
            {
                **cand.to_dict(),
                "old_promotion_decision": a.get("promotion_decision", ""),
                "old_strict_promote": old_strict,
                "actual_mean": float(a["pred_delta_vs_current_mean"]),
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": float(a["pred_delta_vs_current_p90"]),
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these_null)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode,
                "worst_mode_mean_dominance": worst_mean_mode,
                "public_free_submission_ready": ready,
                "final_decision": "public_free_submission_ready"
                if ready
                else ("blocked_by_matched_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "null_strict_rate", "mean_dominance", "actual_p90"],
            ascending=[False, False, True, False, True],
        ).reset_index(drop=True)
    return selected, null_map, governor


def write_report(probes: pd.DataFrame, prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].map(as_bool)] if not governor.empty else pd.DataFrame()
    family = (
        governor.groupby(["mask_name", "transform"], dropna=False)
        .agg(
            n=("basename", "count"),
            ready=("public_free_submission_ready", "sum"),
            old_strict=("old_strict_promote", "sum"),
            min_null=("null_strict_rate", "min"),
            best_mean_dom=("mean_dominance", "max"),
            best_p90=("actual_p90", "min"),
            best_mean=("actual_mean", "min"),
        )
        .reset_index()
        .sort_values(["ready", "old_strict", "min_null", "best_mean_dom", "best_p90"], ascending=[False, False, True, False, True])
        if not governor.empty
        else pd.DataFrame()
    )
    cols = [
        "mask_name",
        "transform",
        "multiplier",
        "nonzero_rows",
        "pos_rows",
        "neg_rows",
        "old_strict_promote",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "worst_mode_mean_dominance",
        "public_free_submission_ready",
        "basename",
    ]
    probe_cols = [
        "row_idx",
        "subject_id",
        "sleep_date",
        "s4_delta",
        "sign",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "row_score",
    ]
    lines = [
        "# E300 S4 Mean-Dominance Rescue",
        "",
        "Public LB는 사용하지 않았다. E299 closest S4 후보의 row/sign/mask placement를 바꿔 mean dominance 실패를 구조적으로 고칠 수 있는지 검사했다.",
        "",
        "## Counts",
        "",
        f"- row probes: `{len(probes)}`",
        f"- generated candidates: `{len(prefilter)}`",
        f"- old strict prefilter candidates: `{int(prefilter['strict_promote_gate'].map(as_bool).sum()) if not prefilter.empty else 0}`",
        f"- null-evaluated candidates: `{len(selected)}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        "## Best Row Probes",
        "",
        md_table(probes, probe_cols, n=20),
        "",
        "## Family Summary",
        "",
        md_table(family, ["mask_name", "transform", "n", "ready", "old_strict", "min_null", "best_mean_dom", "best_p90", "best_mean"], n=30),
        "",
        "## Best Governor Rows",
        "",
        md_table(governor, cols, n=30),
        "",
        "## Interpretation",
        "",
    ]
    if len(ready):
        lines += [
            "- A public-free ready S4 mean-dominance rescue exists. Inspect duplicate risk and movement anatomy before any public submission.",
        ]
    else:
        lines += [
            "- No S4 sign/mask/within-subject rescue crossed the full public-free gate.",
            "- If old-strict candidates remain numerous but ready is zero, the issue is not simply row removal or sign balancing.",
            "- The next branch should move from hand masks to a learned outcome target or use a genuinely new context target, not another S4 scalar mask sweep.",
        ]
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{rel(ROW_PROBE_OUT)}`",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(PREFILTER_OUT)}`",
        f"- `{rel(GOVERNOR_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    current, meta = load_current_and_meta()
    delta = source_delta(current)
    probes = row_probe_scores(delta, current, meta)
    candidates, deltas = generate_candidates(delta, current, meta, probes)
    prefilter = score_prefilter(candidates, current) if not candidates.empty else candidates
    selected = select_for_null(prefilter)
    selected, null_map, governor = run_governor(selected, deltas, current, meta) if not selected.empty else (selected, pd.DataFrame(), pd.DataFrame())

    probes.to_csv(ROW_PROBE_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    prefilter.to_csv(PREFILTER_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    if not null_map.empty:
        null_map.to_csv(NULL_MAP_OUT, index=False)
    write_report(probes, prefilter, selected, governor)

    ready_n = int(governor["public_free_submission_ready"].map(as_bool).sum()) if not governor.empty else 0
    strict_n = int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0
    print(f"row_probes={len(probes)} generated={len(prefilter)} strict={strict_n} null_eval={len(selected)} ready={ready_n}")
    if not governor.empty:
        print(
            f"best_null={governor['null_strict_rate'].min():.6f} "
            f"best_mean_dom={governor['mean_dominance'].max():.6f} best_p90={governor['actual_p90'].min():.9f}"
        )
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
