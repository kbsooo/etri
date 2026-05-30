#!/usr/bin/env python3
"""E311: combine or residualize E310 pair actions.

E310 showed a cliff:

    visible pair actions -> null-common
    null-rare pair actions -> too small

E311 asks whether that cliff is only a single-action artifact. It tries two
public-free translators:

1. stack the null-rare micro pair actions until they become visible;
2. subtract matched-null movement from visible actions, keeping only the part
   that is not reproduced by row/subject/dateblock/wrong-pair controls.

No public LB is used.
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
NULL_DIR = OUT / "e311_pair_micro_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob, load_frames, stable_seed  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import safe_id  # noqa: E402
from e297_episode_state_materializer import align_meta_to_current, feature_rows, sigmoid  # noqa: E402
import e310_pair_interaction_materializer as e310  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

E310_CANDIDATES = OUT / "e310_pair_interaction_candidates.csv"
E310_SELECTED = OUT / "e310_pair_interaction_selected.csv"
E310_GOVERNOR = OUT / "e310_pair_interaction_governor.csv"
E310_NULL_MAP = OUT / "e310_pair_interaction_null_map.csv"

CANDIDATE_OUT = OUT / "e311_pair_micro_candidates.csv"
SELECTED_OUT = OUT / "e311_pair_micro_selected.csv"
GOVERNOR_OUT = OUT / "e311_pair_micro_governor.csv"
SCORE_OUT = OUT / "e311_pair_micro_scores.csv"
NULL_MAP_OUT = OUT / "e311_pair_micro_null_map.csv"
REPORT_OUT = OUT / "e311_pair_micro_report.md"

MAX_COMBO_CANDIDATES = 420
MAX_NULL_EVAL = 48
N_NULL_REPS = 4


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def md(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame is None or frame.empty:
        return "_empty_"
    out = frame.head(n).copy()
    for col in out.select_dtypes(include=[np.floating]).columns:
        out[col] = out[col].map(lambda x: f"{x:{floatfmt}}")
    out = out.fillna("").astype(str)
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *rows])


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def sorted_sub(path: Path) -> pd.DataFrame:
    return load_sub(path).sort_values(KEYS).reset_index(drop=True)


def current_frame() -> pd.DataFrame:
    return sorted_sub(OUT / CURRENT)


def load_delta(path: Path, current: pd.DataFrame) -> np.ndarray:
    sub = sorted_sub(path)
    if not sub[KEYS].equals(current[KEYS]):
        raise ValueError(f"Key mismatch for {path}")
    return logit(sub[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def write_submission(current: pd.DataFrame, delta: np.ndarray, candidate_id: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e311_pairmicro_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def target_pair(pair_text: str) -> tuple[str, str]:
    a, b = str(pair_text).split("_")
    return a, b


def pair_delta_only(delta: np.ndarray, pair: tuple[str, str]) -> np.ndarray:
    out = np.zeros_like(delta)
    a, b = pair
    out[:, TARGETS.index(a)] = delta[:, TARGETS.index(a)]
    out[:, TARGETS.index(b)] = delta[:, TARGETS.index(b)]
    return out


def move_pair_to(delta: np.ndarray, source_pair: tuple[str, str], target_pair_: tuple[str, str]) -> np.ndarray:
    out = np.zeros_like(delta)
    a, b = source_pair
    x, y = target_pair_
    out[:, TARGETS.index(x)] += delta[:, TARGETS.index(a)]
    out[:, TARGETS.index(y)] += delta[:, TARGETS.index(b)]
    return out


def shuffle_rows(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed_parts: tuple[Any, ...]) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("e311shuffle", *map(str, seed_parts)))
    values = np.asarray(delta, dtype=np.float64)
    out = values.copy()
    if mode == "row":
        return values[rng.permutation(len(values))]
    if mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                out[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
        return out
    raise ValueError(mode)


def ensure_e310_artifacts() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not E310_CANDIDATES.exists() or not E310_GOVERNOR.exists() or not E310_SELECTED.exists():
        candidate_meta, _, _, _ = e310.generate_candidates()
        prefilter = e310.score_prefilter(candidate_meta, current_frame())
        selected = e310.select_for_null(prefilter)
        prefilter.to_csv(E310_CANDIDATES, index=False)
        selected.to_csv(E310_SELECTED, index=False)
    candidates = pd.read_csv(E310_CANDIDATES)
    governor = pd.read_csv(E310_GOVERNOR)
    selected = pd.read_csv(E310_SELECTED)
    null_map = pd.read_csv(E310_NULL_MAP)
    scores = pd.read_csv(OUT / "e310_pair_interaction_scores.csv")

    missing_candidates = [OUT / b for b in candidates["basename"] if not (OUT / b).exists()]
    missing_nulls = [ROOT / p for p in null_map["null_path"] if not (ROOT / p).exists()]
    if missing_candidates or missing_nulls:
        candidate_meta, deltas, current, meta = e310.generate_candidates()
        prefilter = e310.score_prefilter(candidate_meta, current)
        selected = e310.select_for_null(prefilter)
        _, null_map, governor = e310.run_governor(selected, deltas, current, meta)
        prefilter.to_csv(E310_CANDIDATES, index=False)
        selected.to_csv(E310_SELECTED, index=False)
        governor.to_csv(E310_GOVERNOR, index=False)
        null_map.to_csv(E310_NULL_MAP, index=False)
        scores = pd.read_csv(OUT / "e310_pair_interaction_scores.csv")
        candidates = prefilter
    return candidates, governor, selected, null_map, scores


def null_mean_delta(null_map: pd.DataFrame, source_basename: str, current: pd.DataFrame, modes: set[str]) -> np.ndarray:
    rows = null_map[null_map["source_basename"].eq(source_basename) & null_map["mode"].isin(modes)]
    if rows.empty:
        return np.zeros((len(current), len(TARGETS)), dtype=np.float64)
    deltas = [load_delta(ROOT / path, current) for path in rows["null_path"] if (ROOT / path).exists()]
    if not deltas:
        return np.zeros((len(current), len(TARGETS)), dtype=np.float64)
    return np.mean(deltas, axis=0)


def top_abs(delta: np.ndarray, n: int) -> np.ndarray:
    values = np.asarray(delta, dtype=np.float64)
    if n <= 0 or n >= len(values):
        return values.copy()
    out = np.zeros_like(values)
    score = np.max(np.abs(values), axis=1)
    idx = np.argsort(score)[::-1][:n]
    out[idx] = values[idx]
    return out


def cap_delta(delta: np.ndarray, cap: float) -> np.ndarray:
    return np.clip(np.asarray(delta, dtype=np.float64), -cap, cap)


def component_from_row(row: pd.Series, current: pd.DataFrame) -> dict[str, Any]:
    basename = str(row["basename"])
    pair = target_pair(row["pair"])
    delta = pair_delta_only(load_delta(OUT / basename, current), pair)
    return {
        "basename": basename,
        "pair": pair,
        "episode": str(row["episode"]),
        "rule": str(row.get("rule", "")),
        "delta": delta,
    }


def component_null_delta(component: dict[str, Any], mode: str, rep: int, meta: pd.DataFrame) -> np.ndarray:
    delta = np.asarray(component["delta"], dtype=np.float64)
    pair = component["pair"]
    if mode in {"row", "subject", "dateblock"}:
        return shuffle_rows(delta, mode, meta, (component["basename"], mode, rep))
    if mode == "swap_targets":
        a, b = pair
        return move_pair_to(delta, pair, (b, a))
    if mode == "wrong_pair":
        return move_pair_to(delta, pair, e310.wrong_pair_for(pair, rep))
    if mode == "sign_flip":
        return -delta
    raise ValueError(mode)


def combo_null_delta(components: list[dict[str, Any]], mode: str, rep: int, meta: pd.DataFrame) -> np.ndarray:
    return np.sum([component_null_delta(component, mode, rep, meta) for component in components], axis=0)


def add_candidate(
    rows: list[dict[str, Any]],
    components: dict[str, list[dict[str, Any]]],
    current: pd.DataFrame,
    candidate_id: str,
    delta: np.ndarray,
    parts: list[dict[str, Any]],
    recipe: str,
    weight: float,
    source_note: str,
) -> None:
    delta = cap_delta(delta, 0.40)
    if np.max(np.abs(delta)) < 1.0e-12:
        return
    path = write_submission(current, delta, candidate_id)
    basename = path.name
    components[basename] = parts
    nonzero = int(np.any(np.abs(delta) > 1.0e-12, axis=1).sum())
    affected_targets = [
        target for j, target in enumerate(TARGETS) if np.any(np.abs(delta[:, j]) > 1.0e-12)
    ]
    rows.append(
        {
            "basename": basename,
            "source_path": rel(path),
            "recipe": recipe,
            "source_note": source_note,
            "weight": weight,
            "n_parts": len(parts),
            "episodes": ",".join(sorted({p["episode"] for p in parts})),
            "pairs": ",".join(sorted({f"{p['pair'][0]}_{p['pair'][1]}" for p in parts})),
            "rules": ",".join(sorted({p["rule"] for p in parts if p["rule"]})),
            "affected_targets": ",".join(affected_targets),
            "nonzero_rows": nonzero,
            "mean_abs_delta": float(np.mean(np.abs(delta))),
            "max_abs_delta": float(np.max(np.abs(delta))),
            "signed_delta_sum": float(np.sum(delta)),
            "q_sum": float(np.sum(delta[:, :3])),
            "s_sum": float(np.sum(delta[:, 3:])),
        }
    )


def generate_micro_combos(current: pd.DataFrame, governor: pd.DataFrame, null_map: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, list[dict[str, Any]]]]:
    rows: list[dict[str, Any]] = []
    components: dict[str, list[dict[str, Any]]] = {}

    safe = governor[
        governor["old_strict_promote"].eq(False)
        & governor["actual_p90"].lt(0)
        & governor["null_strict_rate"].le(0.12)
        & governor["p90_dominance"].ge(0.60)
        & governor["mean_dominance"].ge(0.50)
        & governor["wrong_pair_p90_dominance"].ge(0.50)
        & governor["swap_targets_p90_dominance"].ge(0.50)
    ].copy()
    safe = safe.sort_values(["null_strict_rate", "actual_p90", "actual_mean"]).reset_index(drop=True)
    safe_components = [component_from_row(row, current) for _, row in safe.iterrows()]

    for n in [2, 3, 4, 5, 6, 8, 10]:
        subset = safe_components[: min(n, len(safe_components))]
        if len(subset) < 2:
            continue
        base_delta = np.sum([p["delta"] for p in subset], axis=0)
        for weight in [0.75, 1.00, 1.25, 1.50, 2.00]:
            add_candidate(
                rows,
                components,
                current,
                f"microstack_top{len(subset)}_w{weight:.2f}",
                weight * base_delta,
                [{**p, "delta": weight * p["delta"]} for p in subset],
                "microstack",
                weight,
                "stack top null-rare too-small E310 rows",
            )

    by_pair = safe.sort_values(["null_strict_rate", "actual_p90"]).groupby("pair", as_index=False).head(1)
    diverse_parts = [component_from_row(row, current) for _, row in by_pair.iterrows()]
    for n in [2, 3, 4, 5]:
        subset = diverse_parts[: min(n, len(diverse_parts))]
        if len(subset) < 2:
            continue
        base_delta = np.sum([p["delta"] for p in subset], axis=0)
        for weight in [0.75, 1.00, 1.25, 1.50, 2.00]:
            add_candidate(
                rows,
                components,
                current,
                f"microdiverse_top{len(subset)}_w{weight:.2f}",
                weight * base_delta,
                [{**p, "delta": weight * p["delta"]} for p in subset],
                "microdiverse",
                weight,
                "stack one null-rare row per target pair",
            )

    cash = safe[safe["episode"].eq("cashflow_stress")].copy()
    cash_parts = [component_from_row(row, current) for _, row in cash.iterrows()]
    for n in [2, 3, 4, 5]:
        subset = cash_parts[: min(n, len(cash_parts))]
        if len(subset) < 2:
            continue
        base_delta = np.sum([p["delta"] for p in subset], axis=0)
        for weight in [0.75, 1.00, 1.25, 1.50]:
            add_candidate(
                rows,
                components,
                current,
                f"microcash_top{len(subset)}_w{weight:.2f}",
                weight * base_delta,
                [{**p, "delta": weight * p["delta"]} for p in subset],
                "microcash",
                weight,
                "stack cashflow-only null-rare pair actions",
            )

    visible = governor[governor["old_strict_promote"].eq(True)].copy()
    visible = visible.sort_values(["actual_p90", "actual_mean"]).head(24).reset_index(drop=True)
    mode_sets = {
        "row_subject_date": {"row", "subject", "dateblock"},
        "wrong_swap": {"wrong_pair", "swap_targets"},
        "all_controls": {"row", "subject", "dateblock", "wrong_pair", "swap_targets"},
    }
    for _, row in visible.iterrows():
        source_basename = str(row["basename"])
        pair = target_pair(row["pair"])
        actual = pair_delta_only(load_delta(OUT / source_basename, current), pair)
        for mode_name, modes in mode_sets.items():
            null_mean = pair_delta_only(null_mean_delta(null_map, source_basename, current, modes), pair)
            for lam in [0.50, 0.75, 1.00, 1.25]:
                resid = actual - lam * null_mean
                for keep in [32, 64, 96, 0]:
                    shaped = top_abs(resid, keep) if keep else resid
                    for weight in [0.75, 1.00, 1.25, 1.50]:
                        part = {
                            "basename": source_basename,
                            "pair": pair,
                            "episode": str(row["episode"]),
                            "rule": f"resid_{mode_name}_lam{lam:.2f}_top{keep or 'all'}",
                            "delta": weight * shaped,
                        }
                        add_candidate(
                            rows,
                            components,
                            current,
                            f"resid_{source_basename[:40]}_{mode_name}_l{lam:.2f}_k{keep or 'all'}_w{weight:.2f}",
                            weight * shaped,
                            [part],
                            "residualized_visible",
                            weight,
                            f"subtract E310 {mode_name} null mean from old-strict pair action",
                        )
                        if len(rows) >= MAX_COMBO_CANDIDATES:
                            return pd.DataFrame(rows), components

    return pd.DataFrame(rows), components


def score_prefilter(candidate_meta: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    if candidate_meta.empty:
        return candidate_meta
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    paths = [OUT / b for b in candidate_meta["basename"]]
    features = feature_rows([OUT / CURRENT, *paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
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
    merged = candidate_meta.merge(scores[score_cols], on="basename", how="left")
    return merged.sort_values(
        ["strict_promote_gate", "info_sensor_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    if prefilter.empty:
        return prefilter
    strict = prefilter[prefilter["strict_promote_gate"].astype(bool)].copy()
    info = prefilter[
        (~prefilter["strict_promote_gate"].astype(bool))
        & prefilter["info_sensor_gate"].astype(bool)
        & prefilter["pred_delta_vs_current_p90"].lt(-2.0e-5)
    ].copy()
    source_best = (
        prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby(["recipe", "pairs"], as_index=False)
        .head(2)
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


def write_null_candidate(
    current: pd.DataFrame,
    components: list[dict[str, Any]],
    basename: str,
    mode: str,
    rep: int,
    meta: pd.DataFrame,
) -> Path:
    if mode in {"row", "subject", "dateblock", "sign_flip"}:
        combined = np.sum([component["delta"] for component in components], axis=0)
        null_delta = -combined if mode == "sign_flip" else shuffle_rows(combined, mode, meta, (basename, mode, rep))
    else:
        null_delta = combo_null_delta(components, mode, rep, meta)
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + cap_delta(null_delta, 0.40)
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e311null_{basename[:64]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def run_governor(selected: pd.DataFrame, component_map: dict[str, list[dict[str, Any]]], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return selected, pd.DataFrame(), pd.DataFrame()
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    modes = ["row", "subject", "dateblock", "swap_targets", "wrong_pair", "sign_flip"]
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        parts = component_map[basename]
        for mode in modes:
            reps = N_NULL_REPS if mode in {"row", "subject", "dateblock", "wrong_pair"} else 1
            for rep in range(reps):
                null_path = write_null_candidate(current, parts, basename, mode, rep, meta)
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
        null_strict_rate = float(these_null["strict_promote_gate"].astype(bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = {}
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms[f"{mode}_p90_dominance"] = float(np.mean(float(a["pred_delta_vs_current_p90"]) < vals))
        worst_mode = float(min(mode_doms.values())) if mode_doms else 0.0
        ready = bool(
            old_strict
            and null_strict_rate <= 0.10
            and p90_dominance >= 0.80
            and mean_dominance >= 0.70
            and worst_mode >= 0.55
            and mode_doms.get("wrong_pair_p90_dominance", 0.0) >= 0.75
            and mode_doms.get("swap_targets_p90_dominance", 0.0) >= 0.50
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
                **mode_doms,
                "public_free_submission_ready": ready,
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_pair_micro_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "null_strict_rate", "actual_p90", "wrong_pair_p90_dominance"],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    return selected, null_map, governor


def source_read(prefilter: pd.DataFrame, governor: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    recipe_summary = (
        prefilter.groupby("recipe", dropna=False)
        .agg(
            generated=("basename", "count"),
            old_strict=("strict_promote_gate", "sum"),
            info=("info_sensor_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_mean=("pred_delta_vs_current_mean", "min"),
            median_move=("mean_abs_delta", "median"),
        )
        .reset_index()
        .sort_values(["old_strict", "best_p90"], ascending=[False, True])
        if not prefilter.empty
        else pd.DataFrame()
    )
    gov_summary = (
        governor.groupby("recipe", dropna=False)
        .agg(
            evaluated=("basename", "count"),
            old_strict=("old_strict_promote", "sum"),
            ready=("public_free_submission_ready", "sum"),
            best_actual_p90=("actual_p90", "min"),
            best_null_strict=("null_strict_rate", "min"),
            best_worst_mode=("worst_mode_p90_dominance", "max"),
        )
        .reset_index()
        .sort_values(["ready", "old_strict", "best_null_strict", "best_actual_p90"], ascending=[False, False, True, True])
        if not governor.empty
        else pd.DataFrame()
    )
    return recipe_summary, gov_summary


def write_report(prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame, e310_governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    recipe_summary, gov_summary = source_read(prefilter, governor)
    e310_cliff = (
        e310_governor.groupby("final_decision", dropna=False)
        .agg(n=("basename", "count"), best_p90=("actual_p90", "min"), best_null_strict=("null_strict_rate", "min"))
        .reset_index()
        if not e310_governor.empty
        else pd.DataFrame()
    )
    show_cols = [
        "basename",
        "recipe",
        "n_parts",
        "pairs",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "wrong_pair_p90_dominance",
        "swap_targets_p90_dominance",
        "worst_mode_p90_dominance",
        "final_decision",
    ]
    lines = [
        "# E311 Pair Micro-Action Combiner",
        "",
        "Public LB는 사용하지 않았다. E310의 visibility/null-rarity cliff를 두 방식으로 찔렀다: null-rare micro pair actions를 stack하고, old-strict pair actions에서 matched-null 평균 움직임을 빼서 residual action을 만든다.",
        "",
        "## E310 Cliff Input",
        "",
        md(e310_cliff, n=20),
        "",
        "## Prefilter",
        "",
        f"- generated candidates: `{len(prefilter)}`",
        f"- old strict candidates: `{int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}`",
        f"- info candidates: `{int(prefilter['info_sensor_gate'].sum()) if not prefilter.empty else 0}`",
        f"- null-evaluated candidates: `{len(selected)}`",
        "",
        md(recipe_summary, n=20),
        "",
        "## Matched Null Governor",
        "",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md(gov_summary, n=20),
        "",
        md(governor[[c for c in show_cols if c in governor.columns]] if not governor.empty else governor, n=60),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        top = ready.iloc[0]
        lines.append(
            f"`{top['basename']}` is public-free ready under E311 micro-combo controls. Treat it as a scarce-slot hypothesis, not as a public-LB optimized file."
        )
    else:
        lines.extend(
            [
                "- No E311 micro-combo or null-residualized pair action is public-free ready.",
                "- If micro stacks remain too small or become null-common when visible, the visibility/null-rarity cliff is structural for the current pair translator.",
                "- If residualized visible actions are still null-common, matched-null subtraction is not enough; a learned action-health target is needed.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{CANDIDATE_OUT.relative_to(ROOT)}`",
            f"- `{SELECTED_OUT.relative_to(ROOT)}`",
            f"- `{GOVERNOR_OUT.relative_to(ROOT)}`",
            f"- `{SCORE_OUT.relative_to(ROOT)}`",
            f"- `{NULL_MAP_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    candidates, e310_governor, _, null_map, _ = ensure_e310_artifacts()
    current = current_frame()
    base, _, _, _ = load_frames()
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = align_meta_to_current(test_df, current)

    candidate_meta, component_map = generate_micro_combos(current, e310_governor, null_map)
    prefilter = score_prefilter(candidate_meta, current) if not candidate_meta.empty else pd.DataFrame()
    selected = select_for_null(prefilter) if not prefilter.empty else pd.DataFrame()
    selected, nulls, governor = run_governor(selected, component_map, current, meta) if not selected.empty else (selected, pd.DataFrame(), pd.DataFrame())
    prefilter.to_csv(CANDIDATE_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    if not nulls.empty:
        nulls.to_csv(NULL_MAP_OUT, index=False)
    write_report(prefilter, selected, governor, e310_governor)
    print(f"generated_candidates={len(prefilter)}")
    print(f"old_strict={int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}")
    print(f"null_evaluated={len(selected)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    if not governor.empty:
        print(f"best_actual_p90={governor['actual_p90'].min():.9f}")
        print(f"best_null_strict={governor['null_strict_rate'].min():.6f}")
    print(f"e310_candidates_loaded={len(candidates)}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
