#!/usr/bin/env python3
"""E292: contrastive lifestyle placement invariant audit.

E289/E290/E291 showed a repeated pattern:

    human lifestyle signal exists on train,
    but direct test placement is reproducible by matched nulls.

This audit changes the question again. Instead of asking "which block is good?",
it asks "which selected block looks unlike the blocks selected by null
placement with the same movement budget?"

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
NULL_DIR = OUT / "e292_contrastive_lifestyle_placement_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, md_table, stable_seed  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import normalize_keys, prep_test_meta  # noqa: E402
from e290_lifestyle_row_placement_law_audit import align_columns  # noqa: E402
from e291_lifestyle_block_state_assignment_audit import (  # noqa: E402
    build_lifestyle_cache,
    build_slice_oof_components,
    build_test_components,
    block_delta,
    crossfit_block_score,
    make_block_model,
    run_block_audit,
    safe_id,
    select_blocks,
    shuffle_block_scores,
)
from public_anchor_bottleneck_decomposition import KEYS, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

RNG_SEED = 20260531 + 292
MAX_SOURCE_POLICIES = 14
MAX_MATERIALIZE_POLICIES = 14
N_RATE_REPS = 36
N_TRAIN_NULL_REPS = 48
N_TEST_NULL_REPS = 5
SCALES = [0.25, 0.50]
DELTA_MODES = ["raw", "centered"]

CONTRAST_OUT = OUT / "e292_contrastive_lifestyle_placement_summary.csv"
CANDIDATE_OUT = OUT / "e292_contrastive_lifestyle_candidate_summary.csv"
GOVERNOR_OUT = OUT / "e292_contrastive_lifestyle_governor_summary.csv"
SCORE_OUT = OUT / "e292_contrastive_lifestyle_scores.csv"
NULL_MAP_OUT = OUT / "e292_contrastive_lifestyle_null_map.csv"
REPORT_OUT = OUT / "e292_contrastive_lifestyle_report.md"


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def percentile_rank(score: np.ndarray) -> np.ndarray:
    return pd.Series(np.asarray(score, dtype=np.float64)).rank(method="average", pct=True).to_numpy(dtype=np.float64)


def select_top_n(score: np.ndarray, n_select: int) -> np.ndarray:
    n_select = max(1, min(int(n_select), len(score)))
    selected = np.zeros(len(score), dtype=bool)
    selected[np.argsort(np.asarray(score, dtype=np.float64))[::-1][:n_select]] = True
    return selected


def estimate_null_rates(
    score: np.ndarray,
    frac: float,
    block_table: pd.DataFrame,
    seed_key: str,
    n_reps: int = N_RATE_REPS,
) -> pd.DataFrame:
    rates = {mode: np.zeros(len(score), dtype=np.float64) for mode in ["row", "subject", "dateblock"]}
    for mode in rates:
        rng = np.random.default_rng(stable_seed("e292_rates", seed_key, mode))
        for _ in range(n_reps):
            shuffled = shuffle_block_scores(score, mode, block_table, rng)
            rates[mode] += select_blocks(shuffled, frac).astype(float)
        rates[mode] /= float(n_reps)
    out = pd.DataFrame({f"null_{mode}_rate": vals for mode, vals in rates.items()})
    out["null_mean_rate"] = out[[f"null_{m}_rate" for m in rates]].mean(axis=1)
    out["null_max_rate"] = out[[f"null_{m}_rate" for m in rates]].max(axis=1)
    out["null_min_rate"] = out[[f"null_{m}_rate" for m in rates]].min(axis=1)
    return out


def contrast_table(score: np.ndarray, frac: float, block_table: pd.DataFrame, seed_key: str) -> pd.DataFrame:
    score = np.asarray(score, dtype=np.float64)
    rank = percentile_rank(score)
    scale = np.nanpercentile(score, 75) - np.nanpercentile(score, 25)
    if not np.isfinite(scale) or scale <= 1.0e-12:
        scale = float(np.nanstd(score) + 1.0e-6)
    z = np.clip((score - float(np.nanmedian(score))) / scale, -4.0, 4.0)
    rates = estimate_null_rates(score, frac, block_table, seed_key)
    tab = pd.DataFrame(
        {
            "block_key": block_table["block_key"].astype(str).to_numpy(),
            "subject_id": block_table["subject_id"].astype(str).to_numpy(),
            "dateblock_group": block_table["dateblock_group"].astype(str).to_numpy(),
            "score": score,
            "score_rank": rank,
            "score_z": z,
        }
    )
    tab = pd.concat([tab, rates], axis=1)
    tab["contrast_score"] = tab["score_rank"] - 0.80 * tab["null_mean_rate"] - 0.35 * tab["null_max_rate"] + 0.08 * tab["score_z"]
    tab["rarity_score"] = tab["score_rank"] * (1.0 - tab["null_max_rate"]) - 0.20 * tab["null_mean_rate"]
    tab["null_gap"] = tab["score_rank"] - tab["null_max_rate"]
    tab["base_selected"] = select_blocks(score, frac)
    return tab.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def select_contrast(tab: pd.DataFrame, base_frac: float, rule: str) -> np.ndarray:
    base_n = max(1, int(round(len(tab) * float(base_frac))))
    if rule == "contrast_half":
        return select_top_n(tab["contrast_score"].to_numpy(dtype=np.float64), max(1, int(round(base_n * 0.50))))
    if rule == "contrast_third":
        return select_top_n(tab["contrast_score"].to_numpy(dtype=np.float64), max(1, int(round(base_n * 0.34))))
    if rule == "rarity_half":
        return select_top_n(tab["rarity_score"].to_numpy(dtype=np.float64), max(1, int(round(base_n * 0.50))))
    if rule == "rarity_third":
        return select_top_n(tab["rarity_score"].to_numpy(dtype=np.float64), max(1, int(round(base_n * 0.34))))
    if rule.startswith("base_lowmax"):
        threshold = float(rule.replace("base_lowmax", "")) / 100.0
        selected = tab["base_selected"].to_numpy(dtype=bool) & (tab["null_max_rate"].to_numpy(dtype=np.float64) <= threshold)
        if selected.sum() == 0:
            selected = select_top_n(tab["rarity_score"].to_numpy(dtype=np.float64), max(1, int(round(base_n * 0.25))))
        return selected
    raise ValueError(rule)


def selected_block_stats(tab: pd.DataFrame, selected: np.ndarray) -> dict[str, float]:
    if not np.any(selected):
        return {
            "selected_blocks": 0.0,
            "selected_null_mean": np.nan,
            "selected_null_max": np.nan,
            "selected_score_rank": np.nan,
            "selected_contrast_score": np.nan,
        }
    part = tab.loc[selected]
    return {
        "selected_blocks": float(len(part)),
        "selected_null_mean": float(part["null_mean_rate"].mean()),
        "selected_null_max": float(part["null_max_rate"].mean()),
        "selected_score_rank": float(part["score_rank"].mean()),
        "selected_contrast_score": float(part["contrast_score"].mean()),
    }


def contrast_train_stress(
    y: np.ndarray,
    base_prob: np.ndarray,
    aug_prob: np.ndarray,
    row_block: pd.Series,
    block_table: pd.DataFrame,
    tab: pd.DataFrame,
    selected: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, float]:
    n_select = int(np.count_nonzero(selected))
    actual = block_delta(y, base_prob, aug_prob, row_block, block_table, selected)
    null_rows = []
    score = tab["contrast_score"].to_numpy(dtype=np.float64)
    for mode in ["row", "subject", "dateblock"]:
        for _ in range(N_TRAIN_NULL_REPS):
            shuffled = shuffle_block_scores(score, mode, block_table, rng)
            null_selected = select_top_n(shuffled, n_select)
            null_rows.append({"mode": mode, "delta": block_delta(y, base_prob, aug_prob, row_block, block_table, null_selected)})
    null = pd.DataFrame(null_rows)
    vals = null["delta"].to_numpy(dtype=np.float64)
    out: dict[str, float] = {
        "selected_blocks": float(n_select),
        "selected_rows": float(row_block.astype(str).isin(set(block_table.loc[selected, "block_key"].astype(str))).sum()),
        "actual_delta": actual,
        "null_q20": float(np.quantile(vals, 0.20)),
        "null_median": float(np.median(vals)),
        "null_best": float(np.min(vals)),
        "dominance": float(np.mean(actual < vals)),
        "placebo_adjusted_vs_median": float(actual - np.median(vals)),
    }
    for mode in ["row", "subject", "dateblock"]:
        mvals = null.loc[null["mode"].eq(mode), "delta"].to_numpy(dtype=np.float64)
        out[f"{mode}_dominance"] = float(np.mean(actual < mvals))
        out[f"{mode}_null_best"] = float(np.min(mvals))
    out["contrast_gate"] = float(
        actual < -0.00025
        and out["dominance"] >= 0.80
        and min(out["row_dominance"], out["subject_dominance"], out["dateblock_dominance"]) >= 0.58
        and actual <= out["null_q20"] - 1.0e-5
    )
    return out


def source_rows(block_summary: pd.DataFrame) -> pd.DataFrame:
    source = block_summary[block_summary["block_gate_bool"].astype(bool)].copy()
    if source.empty:
        source = block_summary.copy()
    source = source.sort_values(
        ["actual_delta", "dominance", "row_dominance", "subject_dominance", "dateblock_dominance"],
        ascending=[True, False, False, False, False],
    )
    return source.head(MAX_SOURCE_POLICIES).reset_index(drop=True)


def rebuild_slice_components(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    lifestyle_cache: dict[tuple[str, str], dict[str, Any]],
    block_summary: pd.DataFrame,
) -> dict[str, dict[str, Any]]:
    components: dict[str, dict[str, Any]] = {}
    for _, row in block_summary.drop_duplicates("slice_id").iterrows():
        slice_id = str(row["slice_id"])
        target = str(row["target"])
        view_id = str(row["view_id"])
        split_name = str(row["split"])
        rep_id = str(row["rep"])
        rep_train, rep_test = lifestyle_cache[(view_id, split_name)]["reps"][rep_id]
        base_oof, aug_oof, benefit, _ = build_slice_oof_components(train_df, base_train, target, rep_train, split_name)
        _, _, raw_delta, centered_delta, _ = build_test_components(train_df, test_df, base_train, base_test, target, rep_train, rep_test)
        components[slice_id] = {
            "target": target,
            "base_oof": base_oof,
            "aug_oof": aug_oof,
            "benefit": benefit,
            "raw_delta": raw_delta,
            "centered_delta": centered_delta,
        }
    return components


def run_contrast_audit(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    lifestyle_cache: dict[tuple[str, str], dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict[str, Any]]]:
    block_summary, block_cache = run_block_audit(train_df, test_df, base_train, base_test, lifestyle_cache)
    if block_summary.empty:
        return block_summary, pd.DataFrame(), block_cache
    components = rebuild_slice_components(train_df, test_df, base_train, base_test, lifestyle_cache, block_summary)
    rng = np.random.default_rng(RNG_SEED)
    rows: list[dict[str, Any]] = []
    source = source_rows(block_summary)
    for _, src in source.iterrows():
        policy_id = str(src["policy_id"])
        cache = block_cache[policy_id]
        comp = components[str(src["slice_id"])]
        block_table = cache["block_table"]
        feature_cols = cache["feature_cols"]
        cv_groups = block_table["subject_id"].astype(str) if str(src["cv_group"]) == "subject_cv" else block_table["dateblock_group"].astype(str)
        score = crossfit_block_score(block_table[feature_cols], cache["labels"], cv_groups)
        frac = float(src["block_frac"])
        tab = contrast_table(score, frac, block_table, f"train_{policy_id}_{frac:.3f}")
        y = train_df[str(src["target"])].to_numpy(dtype=int)
        for rule in ["contrast_half", "contrast_third", "rarity_half", "rarity_third", "base_lowmax50", "base_lowmax35", "base_lowmax25"]:
            selected = select_contrast(tab, frac, rule)
            if int(selected.sum()) < 1:
                continue
            stress = contrast_train_stress(
                y,
                comp["base_oof"],
                comp["aug_oof"],
                cache["train_block"],
                block_table,
                tab,
                selected,
                rng,
            )
            rows.append(
                {
                    "contrast_policy_id": f"{policy_id}_{rule}_bf{int(frac * 100):02d}",
                    "parent_policy_id": policy_id,
                    "slice_id": src["slice_id"],
                    "target": src["target"],
                    "view_id": src["view_id"],
                    "split": src["split"],
                    "rep": src["rep"],
                    "block_scheme": src["block_scheme"],
                    "label_mode": src["label_mode"],
                    "cv_group": src["cv_group"],
                    "rule": rule,
                    "base_block_frac": frac,
                    "parent_actual_delta": float(src["actual_delta"]),
                    "parent_dominance": float(src["dominance"]),
                    "parent_min_mode_dominance": float(min(src["row_dominance"], src["subject_dominance"], src["dateblock_dominance"])),
                    **selected_block_stats(tab, selected),
                    **stress,
                    "contrast_gate_bool": bool(stress["contrast_gate"]),
                }
            )
    contrast = pd.DataFrame(rows)
    if not contrast.empty:
        contrast = contrast.sort_values(
            ["contrast_gate_bool", "actual_delta", "dominance", "selected_null_max"],
            ascending=[False, True, False, True],
        ).reset_index(drop=True)
    block_summary.attrs["components"] = components
    return block_summary, contrast, block_cache


def write_contrast_candidate(
    base: pd.DataFrame,
    target: str,
    row_block: pd.Series,
    test_blocks: pd.DataFrame,
    selected: np.ndarray,
    delta: np.ndarray,
    scale: float,
    candidate_id: str,
) -> tuple[Path, np.ndarray]:
    selected_blocks = set(test_blocks.loc[selected, "block_key"].astype(str))
    row_selected = row_block.astype(str).isin(selected_blocks).to_numpy()
    selected_delta = np.where(row_selected, scale * np.asarray(delta, dtype=np.float64), 0.0)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += selected_delta
    out[TARGETS] = np.clip(sigmoid(logits), 1.0e-6, 1.0 - 1.0e-6)
    path = OUT / f"submission_e292_contrastlife_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, selected_delta


def write_null_candidate(base: pd.DataFrame, target: str, selected_delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(stable_seed("e292null", source_path.name, mode, rep))
    values = np.asarray(selected_delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values))]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
    else:
        raise ValueError(mode)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += shuffled
    out[TARGETS] = np.clip(sigmoid(logits), 1.0e-6, 1.0 - 1.0e-6)
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e292null_{source_path.stem[:72]}_{mode}_r{rep}_{short_hash(out)}.csv"
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


def materialize(
    contrast: pd.DataFrame,
    block_cache: dict[str, dict[str, Any]],
    current: pd.DataFrame,
    test_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    selected = contrast[contrast["contrast_gate_bool"].astype(bool)].copy()
    if selected.empty:
        selected = contrast.sort_values(["actual_delta", "dominance", "selected_null_max"], ascending=[True, False, True]).head(MAX_MATERIALIZE_POLICIES).copy()
    else:
        selected = selected.sort_values(["actual_delta", "dominance", "selected_null_max"], ascending=[True, False, True]).head(MAX_MATERIALIZE_POLICIES).copy()

    meta = prep_test_meta(test_df)
    candidate_paths: list[Path] = []
    candidate_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    score_cache: dict[str, np.ndarray] = {}
    table_cache: dict[tuple[str, float], pd.DataFrame] = {}
    for _, row in selected.iterrows():
        parent_id = str(row["parent_policy_id"])
        cache = block_cache[parent_id]
        frac = float(row["base_block_frac"])
        if parent_id not in score_cache:
            x_train = cache["block_table"][cache["feature_cols"]]
            x_test = cache["test_table"].reindex(columns=["block_key", "subject_id", "dateblock_group", *cache["feature_cols"]], fill_value=0.0)[cache["feature_cols"]]
            x_train, x_test = align_columns(x_train, x_test)
            model = make_block_model()
            model.fit(x_train, cache["labels"])
            score_cache[parent_id] = model.predict_proba(x_test)[:, 1]
        key = (parent_id, frac)
        if key not in table_cache:
            table_cache[key] = contrast_table(score_cache[parent_id], frac, cache["test_table"], f"test_{parent_id}_{frac:.3f}")
        tab = table_cache[key]
        selected_blocks = select_contrast(tab, frac, str(row["rule"]))
        if int(selected_blocks.sum()) < 1:
            continue
        for delta_mode, delta in [("raw", cache["raw_delta"]), ("centered", cache["centered_delta"])]:
            if delta_mode not in DELTA_MODES:
                continue
            for scale in SCALES:
                candidate_id = f"{row['contrast_policy_id']}_{delta_mode}_s{int(scale * 100):03d}"
                path, selected_delta = write_contrast_candidate(
                    current,
                    str(row["target"]),
                    cache["test_block"],
                    cache["test_table"],
                    selected_blocks,
                    delta,
                    scale,
                    candidate_id,
                )
                candidate_paths.append(path)
                candidate_rows.append(
                    {
                        "candidate_id": candidate_id,
                        "basename": path.name,
                        "source_path": rel(path),
                        "contrast_policy_id": row["contrast_policy_id"],
                        "parent_policy_id": parent_id,
                        "target": row["target"],
                        "view_id": row["view_id"],
                        "split": row["split"],
                        "rep": row["rep"],
                        "block_scheme": row["block_scheme"],
                        "label_mode": row["label_mode"],
                        "cv_group": row["cv_group"],
                        "rule": row["rule"],
                        "base_block_frac": frac,
                        "delta_mode": delta_mode,
                        "scale": scale,
                        "train_actual_delta": float(row["actual_delta"]),
                        "train_dominance": float(row["dominance"]),
                        "train_min_mode_dominance": float(min(row["row_dominance"], row["subject_dominance"], row["dateblock_dominance"])),
                        "train_selected_null_max": float(row["selected_null_max"]),
                        "test_selected_blocks": int(selected_blocks.sum()),
                        "test_selected_rows": int(np.count_nonzero(np.abs(selected_delta) > 1.0e-12)),
                        "test_null_mean_rate": float(tab.loc[selected_blocks, "null_mean_rate"].mean()),
                        "test_null_max_rate": float(tab.loc[selected_blocks, "null_max_rate"].mean()),
                        "test_contrast_score": float(tab.loc[selected_blocks, "contrast_score"].mean()),
                        "test_delta_mean": float(np.mean(selected_delta)),
                        "test_delta_p90_abs": float(np.quantile(np.abs(selected_delta), 0.90)),
                        "test_delta_l1": float(np.sum(np.abs(selected_delta))),
                    }
                )
                for null_mode in ["row", "subject", "dateblock"]:
                    for rep in range(N_TEST_NULL_REPS):
                        null_path = write_null_candidate(current, str(row["target"]), selected_delta, path, meta, null_mode, rep)
                        null_rows.append(
                            {
                                "source_basename": path.name,
                                "null_basename": null_path.name,
                                "null_path": rel(null_path),
                                "mode": null_mode,
                                "rep": rep,
                            }
                        )
    candidate_meta = pd.DataFrame(candidate_rows)
    null_map = pd.DataFrame(null_rows)
    if candidate_meta.empty:
        return candidate_meta, null_map, pd.DataFrame()

    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    null_paths = [ROOT / p for p in null_map["null_path"].tolist()]
    score_features = feature_rows([OUT / CURRENT, *candidate_paths, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, score_features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    candidate_score = scores[scores["basename"].isin(candidate_meta["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()
    rows: list[dict[str, Any]] = []
    for _, cand in candidate_meta.iterrows():
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
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].mean()) if len(these_null) else 1.0
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        p90_dominance = float(np.mean(float(a["pred_delta_vs_current_p90"]) < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(float(a["pred_delta_vs_current_mean"]) < mean_vals)) if len(mean_vals) else 0.0
        mode_doms = []
        for _, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms.append(float(np.mean(float(a["pred_delta_vs_current_p90"]) < vals)))
        worst_mode = float(min(mode_doms)) if mode_doms else 0.0
        ready = bool(old_strict and null_strict_rate <= 0.10 and p90_dominance >= 0.80 and mean_dominance >= 0.70 and worst_mode >= 0.55)
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
                "public_free_submission_ready": ready,
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_matched_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "actual_p90", "p90_dominance"],
            ascending=[False, False, True, False],
        ).reset_index(drop=True)
    return candidate_meta, null_map, governor


def write_report(block_summary: pd.DataFrame, contrast: pd.DataFrame, candidates: pd.DataFrame, governor: pd.DataFrame) -> None:
    gates = contrast[contrast["contrast_gate_bool"].astype(bool)] if not contrast.empty else pd.DataFrame()
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    lines = [
        "# E292 Contrastive Lifestyle Placement Invariant Audit",
        "",
        "## Question",
        "",
        "Can real Q3/S4 lifestyle block placement be separated from matched-null placement before materializing a submission?",
        "",
        "## Train Contrast Stress",
        "",
        f"- parent block policies: `{len(block_summary)}`",
        f"- contrast rows: `{len(contrast)}`",
        f"- contrast gates: `{len(gates)}`",
        "",
        md_table(
            contrast[
                [
                    "contrast_policy_id",
                    "target",
                    "block_scheme",
                    "rule",
                    "base_block_frac",
                    "parent_actual_delta",
                    "actual_delta",
                    "null_median",
                    "dominance",
                    "row_dominance",
                    "subject_dominance",
                    "dateblock_dominance",
                    "selected_null_max",
                    "contrast_gate_bool",
                ]
            ] if not contrast.empty else contrast,
            n=50,
        ),
        "",
        "## Materialization Governor",
        "",
        f"- candidates: `{len(candidates)}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor[
                [
                    "basename",
                    "target",
                    "block_scheme",
                    "rule",
                    "delta_mode",
                    "scale",
                    "test_selected_rows",
                    "test_null_max_rate",
                    "old_promotion_decision",
                    "actual_mean",
                    "actual_p90",
                    "null_strict_rate",
                    "p90_dominance",
                    "worst_mode_p90_dominance",
                    "final_decision",
                ]
            ] if not governor.empty else governor,
            n=60,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("At least one E292 candidate is public-free ready. Submit only the top ready candidate as the next scarce-LB test.")
    else:
        lines.append("No E292 candidate is public-free ready. The contrastive invariant is not yet strong enough to spend public LB.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit specifically attacks the E289-E291 failure mode: matched nulls can mimic lifestyle probability movement. A pass would mean the model has found an invariant of real placement, not just plausible human stories. A fail means the current contrast score is still a diagnostic, not a translator.",
            "",
            "## Files",
            "",
            f"- `{CONTRAST_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train_df, test_df, base_train, base_test, lifestyle_cache = build_lifestyle_cache()
    block_summary, contrast, block_cache = run_contrast_audit(train_df, test_df, base_train, base_test, lifestyle_cache)
    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    if not prep_test_meta(test_df)[KEYS].equals(normalize_keys(current[KEYS])):
        raise RuntimeError("E292 test features do not align with current submission")
    candidates, null_map, governor = materialize(contrast, block_cache, current, test_df) if not contrast.empty else (pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    contrast.to_csv(CONTRAST_OUT, index=False)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(block_summary, contrast, candidates, governor)
    print(f"parent_block_policies={len(block_summary)}")
    print(f"contrast_rows={len(contrast)}")
    print(f"contrast_gates={int(contrast['contrast_gate_bool'].sum()) if not contrast.empty else 0}")
    print(f"candidates={len(candidates)}")
    print(f"nulls={len(null_map)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    print(f"best_contrast_delta={contrast['actual_delta'].min():.9f}" if not contrast.empty else "best_contrast_delta=nan")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
