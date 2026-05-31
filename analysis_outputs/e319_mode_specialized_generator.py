#!/usr/bin/env python3
"""E319: mode-specialized generator from E318 regime policies.

E318 showed a real but bounded signal: human/identity/action predictions can
select healthier row/subject/dateblock placement regimes inside the E315
actual/null mini-world.  Directly submitting those selected null controls would
make public LB the checker again.

E319 instead treats E318 selections as a routebook.  It constructs fresh
consensus, blend, and residual action tensors from the selected regimes, then
runs the same public-free matched-null governor used by E315.

No public LB is used.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib
import sys
import warnings

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e319_mode_specialized_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, clip_prob, load_frames, stable_seed  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import safe_id  # noqa: E402
from e297_episode_state_materializer import align_meta_to_current, feature_rows, sigmoid  # noqa: E402
from e315_human_ready_composition_materializer import (  # noqa: E402
    cap_delta,
    flat_cosine,
    md,
    normalize_delta,
    row_consensus,
    score_prefilter,
    signed_consensus,
    target_balance,
    top_cells,
)
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

E318_SELECTED = OUT / "e318_mode_specialized_policy_selected.csv"
E318_SCORES = OUT / "e318_mode_specialized_policy_scores.csv"

CANDIDATE_OUT = OUT / "e319_mode_specialized_generator_candidates.csv"
SELECTED_OUT = OUT / "e319_mode_specialized_generator_selected.csv"
GOVERNOR_OUT = OUT / "e319_mode_specialized_generator_governor.csv"
SCORE_OUT = OUT / "e319_mode_specialized_generator_scores.csv"
NULL_MAP_OUT = OUT / "e319_mode_specialized_generator_null_map.csv"
SUMMARY_OUT = OUT / "e319_mode_specialized_generator_summary.csv"
REPORT_OUT = OUT / "e319_mode_specialized_generator_report.md"

POLICIES = [
    "human_identity_action_p90_rank",
    "human_action_p90_rank",
    "regime_then_geometry",
    "human_regime_only",
    "oracle_p90_rank",
]
NON_ORACLE_POLICIES = [p for p in POLICIES if not p.startswith("oracle")]

MAX_CANDIDATES = 560
MAX_NULL_EVAL = 54
N_NULL_REPS = 4
CAP = 0.35


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def path_from_rel(value: str) -> Path:
    path = Path(str(value))
    if path.is_absolute():
        return path
    return ROOT / path


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def current_frame() -> pd.DataFrame:
    return load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)


def load_delta(path: Path, current: pd.DataFrame) -> np.ndarray:
    sub = load_sub(path).sort_values(KEYS).reset_index(drop=True)
    if not sub[KEYS].equals(current[KEYS]):
        raise ValueError(f"key mismatch: {path}")
    return logit(sub[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def write_submission(current: pd.DataFrame, delta: np.ndarray, candidate_id: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + cap_delta(delta, CAP)
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e319_modespec_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def describe_delta(delta: np.ndarray) -> dict[str, Any]:
    abs_by_target = np.abs(delta).sum(axis=0)
    total = float(abs_by_target.sum())
    return {
        "nonzero_rows": int(np.any(np.abs(delta) > 1.0e-12, axis=1).sum()),
        "nonzero_cells": int(np.sum(np.abs(delta) > 1.0e-12)),
        "mean_abs_delta": float(np.mean(np.abs(delta))),
        "max_abs_delta": float(np.max(np.abs(delta))),
        "l1_delta": total,
        "signed_delta_sum": float(np.sum(delta)),
        "q_abs_share": float(abs_by_target[:3].sum() / max(total, 1e-12)),
        "s_abs_share": float(abs_by_target[3:].sum() / max(total, 1e-12)),
        **{f"abs_{t}": float(abs_by_target[i]) for i, t in enumerate(TARGETS)},
    }


def add_candidate(
    rows: list[dict[str, Any]],
    delta_map: dict[str, np.ndarray],
    current: pd.DataFrame,
    candidate_id: str,
    delta: np.ndarray,
    recipe: str,
    policy: str,
    group_key: str,
    base_variant: str,
    source_names: list[str],
    selected_modes: list[str],
    weight: float,
    oracle_control: bool,
) -> None:
    if len(rows) >= MAX_CANDIDATES:
        return
    delta = cap_delta(delta, CAP)
    if np.max(np.abs(delta)) < 1.0e-12:
        return
    path = write_submission(current, delta, candidate_id)
    basename = path.name
    if basename in delta_map:
        return
    delta_map[basename] = delta
    mode_counts = pd.Series(selected_modes).value_counts().to_dict()
    rows.append(
        {
            "basename": basename,
            "source_path": rel(path),
            "recipe": recipe,
            "policy": policy,
            "group_key": group_key,
            "base_variant": base_variant,
            "source_count": len(source_names),
            "source_basenames": "|".join(source_names[:18]),
            "selected_mode_mix": "|".join(f"{k}:{v}" for k, v in sorted(mode_counts.items())),
            "weight": weight,
            "oracle_control": oracle_control,
            **describe_delta(delta),
        }
    )


def selected_rows() -> pd.DataFrame:
    selected = pd.read_csv(E318_SELECTED)
    scores = pd.read_csv(E318_SCORES)
    actual = scores[scores["placement_mode"].eq("actual")][
        ["source_basename", "path", "target_p90", "target_mean"]
    ].rename(
        columns={
            "path": "actual_path",
            "target_p90": "actual_target_p90",
            "target_mean": "actual_target_mean",
        }
    )
    out = selected[selected["policy"].isin(POLICIES)].merge(actual, on="source_basename", how="left")
    out = out[out["path"].notna() & out["actual_path"].notna()].copy()
    out["selected_path"] = out["path"].map(path_from_rel)
    out["actual_path"] = out["actual_path"].map(path_from_rel)
    out["policy_score_rank"] = out.groupby("policy")["selected_score"].rank(ascending=False, method="first")
    return out.reset_index(drop=True)


def attach_deltas(rows: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    cache: dict[str, np.ndarray] = {}

    def get(path: Path) -> np.ndarray:
        key = str(path)
        if key not in cache:
            cache[key] = load_delta(path, current)
        return cache[key]

    rows = rows.copy()
    rows.attrs["selected_delta"] = []
    rows.attrs["actual_delta"] = []
    rows.attrs["blend35_delta"] = []
    rows.attrs["blend65_delta"] = []
    rows.attrs["residual_delta"] = []
    for _, row in rows.iterrows():
        selected_delta = get(row["selected_path"])
        actual_delta = get(row["actual_path"])
        rows.attrs["selected_delta"].append(selected_delta)
        rows.attrs["actual_delta"].append(actual_delta)
        rows.attrs["blend35_delta"].append(0.65 * actual_delta + 0.35 * selected_delta)
        rows.attrs["blend65_delta"].append(0.35 * actual_delta + 0.65 * selected_delta)
        rows.attrs["residual_delta"].append(selected_delta - actual_delta)
    return rows


def mean_norm(deltas: list[np.ndarray], norm: str = "max") -> np.ndarray:
    return np.mean([normalize_delta(d, norm) for d in deltas], axis=0)


def l1sum_norm(deltas: list[np.ndarray]) -> np.ndarray:
    return np.sum([normalize_delta(d, "l1") for d in deltas], axis=0) / np.sqrt(len(deltas))


def build_group_delta_variants(deltas: dict[str, list[np.ndarray]]) -> dict[str, np.ndarray]:
    selected = deltas["selected"]
    actual = deltas["actual"]
    blend35 = deltas["blend35"]
    blend65 = deltas["blend65"]
    residual = deltas["residual"]
    variants: dict[str, np.ndarray] = {
        "selected_maxmean": mean_norm(selected, "max"),
        "selected_l1sum": l1sum_norm(selected),
        "selected_vote2": signed_consensus(selected, min_votes=2),
        "selected_row2": row_consensus(selected, min_support=2),
        "selected_tbal": target_balance(mean_norm(selected, "max")),
        "blend35_maxmean": mean_norm(blend35, "max"),
        "blend65_maxmean": mean_norm(blend65, "max"),
        "blend65_tbal": target_balance(mean_norm(blend65, "max")),
        "actual_plus_resid35": mean_norm(actual, "max") + 0.35 * mean_norm(residual, "max"),
        "actual_plus_resid65": mean_norm(actual, "max") + 0.65 * mean_norm(residual, "max"),
        "residual_maxmean": mean_norm(residual, "max"),
    }
    if len(selected) >= 4:
        variants["selected_vote3"] = signed_consensus(selected, min_votes=3)
    return {k: v for k, v in variants.items() if np.max(np.abs(v)) > 1.0e-12}


def source_group_specs(rows: pd.DataFrame) -> list[tuple[str, pd.DataFrame]]:
    specs: list[tuple[str, pd.DataFrame]] = []
    for policy in POLICIES:
        part = rows[rows["policy"].eq(policy)].copy()
        if part.empty:
            continue
        part = part.sort_values(["selected_score", "true_p90_rank_health"], ascending=[False, False])
        specs.append((f"{policy}__all", part))
        specs.append((f"{policy}__top24", part.head(24)))
        nonactual = part[~part["placement_mode"].eq("actual")]
        if len(nonactual) >= 6:
            specs.append((f"{policy}__nonactual", nonactual))
        visible = part[part["true_visible"].astype(bool)]
        if len(visible) >= 4:
            specs.append((f"{policy}__visible", visible))
        for mode, mode_part in part.groupby("placement_mode"):
            if len(mode_part) >= 4:
                specs.append((f"{policy}__mode_{mode}", mode_part))
        for recipe, recipe_part in part.groupby("recipe"):
            if len(recipe_part) >= 4:
                specs.append((f"{policy}__recipe_{safe_id(str(recipe))}", recipe_part))
        for (recipe, mode), rm_part in part.groupby(["recipe", "placement_mode"]):
            if len(rm_part) >= 3:
                specs.append((f"{policy}__recipe_{safe_id(str(recipe))}__mode_{mode}", rm_part))
    return specs


def generate_candidates(current: pd.DataFrame, selected: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    delta_map: dict[str, np.ndarray] = {}
    delta_lists = {
        "selected": selected.attrs["selected_delta"],
        "actual": selected.attrs["actual_delta"],
        "blend35": selected.attrs["blend35_delta"],
        "blend65": selected.attrs["blend65_delta"],
        "residual": selected.attrs["residual_delta"],
    }
    selected = selected.reset_index(drop=True).copy()
    selected["delta_idx"] = np.arange(len(selected))
    recipe_counts: dict[str, int] = {}
    recipe_limits = {
        "policy_all": 120,
        "policy_top": 100,
        "policy_mode": 120,
        "policy_recipe": 120,
        "policy_recipe_mode": 100,
    }
    policy_counts: dict[str, int] = {}
    policy_limits = {
        "human_identity_action_p90_rank": 130,
        "human_action_p90_rank": 115,
        "regime_then_geometry": 115,
        "human_regime_only": 90,
        "oracle_p90_rank": 90,
    }

    for group_key, part in source_group_specs(selected):
        if len(rows) >= MAX_CANDIDATES:
            break
        if len(part) < 3:
            continue
        idxs = part["delta_idx"].astype(int).to_list()
        group_deltas = {k: [v[i] for i in idxs] for k, v in delta_lists.items()}
        variants = build_group_delta_variants(group_deltas)
        if "__recipe_" in group_key and "__mode_" in group_key:
            recipe = "policy_recipe_mode"
        elif "__recipe_" in group_key:
            recipe = "policy_recipe"
        elif "__mode_" in group_key:
            recipe = "policy_mode"
        elif "__top" in group_key or "__visible" in group_key or "__nonactual" in group_key:
            recipe = "policy_top"
        else:
            recipe = "policy_all"
        if recipe_counts.get(recipe, 0) >= recipe_limits[recipe]:
            continue
        policy = str(part["policy"].iloc[0])
        if policy_counts.get(policy, 0) >= policy_limits.get(policy, MAX_CANDIDATES):
            continue
        oracle_control = policy.startswith("oracle")
        source_names = part["source_basename"].astype(str).tolist()
        modes = part["placement_mode"].astype(str).tolist()
        # Larger recipe groups get sparse variants first; all-mode aggregates can
        # afford a few full tensors for the stress test.
        keep_grid = [32, 64, 128, 0] if len(part) >= 8 else [32, 64, 0]
        weight_grid = [0.75, 1.5, 3.0, 5.0, 8.0]
        for variant_name, base_delta in variants.items():
            if (
                len(rows) >= MAX_CANDIDATES
                or recipe_counts.get(recipe, 0) >= recipe_limits[recipe]
                or policy_counts.get(policy, 0) >= policy_limits.get(policy, MAX_CANDIDATES)
            ):
                break
            # Residual-only candidates are volatile; keep them sparse and small.
            local_keep = [32, 64] if variant_name.startswith("residual") else keep_grid
            local_weights = [0.75, 1.5, 3.0] if variant_name.startswith("residual") else weight_grid
            for keep in local_keep:
                shaped = top_cells(base_delta, keep) if keep else base_delta
                for weight in local_weights:
                    candidate_id = f"{group_key}__{variant_name}__c{keep or 'all'}__w{weight:.2f}"
                    before = len(rows)
                    add_candidate(
                        rows,
                        delta_map,
                        current,
                        candidate_id,
                        shaped * weight,
                        recipe,
                        policy,
                        group_key,
                        variant_name,
                        source_names,
                        modes,
                        weight,
                        oracle_control,
                    )
                    if len(rows) > before:
                        recipe_counts[recipe] = recipe_counts.get(recipe, 0) + 1
                        policy_counts[policy] = policy_counts.get(policy, 0) + 1
                    if (
                        len(rows) >= MAX_CANDIDATES
                        or recipe_counts.get(recipe, 0) >= recipe_limits[recipe]
                        or policy_counts.get(policy, 0) >= policy_limits.get(policy, MAX_CANDIDATES)
                    ):
                        break
                if (
                    len(rows) >= MAX_CANDIDATES
                    or recipe_counts.get(recipe, 0) >= recipe_limits[recipe]
                    or policy_counts.get(policy, 0) >= policy_limits.get(policy, MAX_CANDIDATES)
                ):
                    break
    return pd.DataFrame(rows), delta_map


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    if prefilter.empty:
        return prefilter
    non_oracle = prefilter[~prefilter["oracle_control"].astype(bool)].copy()
    oracle = prefilter[prefilter["oracle_control"].astype(bool)].copy()
    strict = non_oracle[non_oracle["strict_promote_gate"].astype(bool)].copy()
    info = non_oracle[
        (~non_oracle["strict_promote_gate"].astype(bool))
        & non_oracle["info_sensor_gate"].astype(bool)
        & non_oracle["pred_delta_vs_current_p90"].lt(-2.0e-5)
    ].copy()
    recipe_best = (
        non_oracle.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby("recipe", as_index=False)
        .head(7)
    )
    policy_best = (
        non_oracle.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"])
        .groupby("policy", as_index=False)
        .head(5)
    )
    oracle_best = (
        oracle.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(8)
        if not oracle.empty
        else pd.DataFrame()
    )
    selected = pd.concat(
        [
            strict.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(28),
            info.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(10),
            recipe_best,
            policy_best,
            oracle_best,
        ],
        ignore_index=True,
    )
    if selected.empty:
        selected = prefilter.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL)
    return selected.drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def shuffle_rows(delta: np.ndarray, mode: str, meta: pd.DataFrame, seed_parts: tuple[Any, ...]) -> np.ndarray:
    rng = np.random.default_rng(stable_seed("e319shuffle", *map(str, seed_parts)))
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


def null_delta(delta: np.ndarray, mode: str, rep: int, meta: pd.DataFrame, basename: str) -> np.ndarray:
    if mode in {"row", "subject", "dateblock"}:
        return shuffle_rows(delta, mode, meta, (basename, mode, rep))
    if mode == "sign_flip":
        return -delta
    if mode == "target_perm":
        rng = np.random.default_rng(stable_seed("e319targetperm", basename, rep))
        return delta[:, rng.permutation(len(TARGETS))]
    if mode == "q_s_swap":
        out = np.zeros_like(delta)
        out[:, :3] = delta[:, [3, 4, 5]]
        out[:, 3:6] = delta[:, :3]
        out[:, 6] = delta[:, 6]
        return out
    raise ValueError(mode)


def write_null(current: pd.DataFrame, delta: np.ndarray, basename: str, mode: str, rep: int, meta: pd.DataFrame) -> Path:
    out = current.copy()
    nd = cap_delta(null_delta(delta, mode, rep, meta, basename), CAP)
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + nd
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e319null_{basename[:64]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def run_governor(
    selected: pd.DataFrame,
    delta_map: dict[str, np.ndarray],
    current: pd.DataFrame,
    meta: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return selected, pd.DataFrame(), pd.DataFrame()
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    modes = ["row", "subject", "dateblock", "target_perm", "sign_flip", "q_s_swap"]
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        delta = delta_map[basename]
        for mode in modes:
            reps = N_NULL_REPS if mode in {"row", "subject", "dateblock", "target_perm"} else 1
            for rep in range(reps):
                path = write_null(current, delta, basename, mode, rep, meta)
                null_paths.append(path)
                null_rows.append(
                    {
                        "source_basename": basename,
                        "null_basename": path.name,
                        "null_path": rel(path),
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
        these_null = null_scores.merge(
            null_map[null_map["source_basename"].eq(basename)][["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="inner",
        )
        p90_vals = these_null["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these_null["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        actual_p90 = float(a["pred_delta_vs_current_p90"])
        actual_mean = float(a["pred_delta_vs_current_mean"])
        old_strict = bool(a.get("strict_promote_gate", False))
        null_strict_rate = float(these_null["strict_promote_gate"].astype(bool).mean()) if len(these_null) else 1.0
        p90_dominance = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dominance = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_doms: dict[str, float] = {}
        for mode, part in these_null.groupby("mode"):
            vals = part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            mode_doms[f"{mode}_p90_dominance"] = float(np.mean(actual_p90 < vals))
        worst_mode = float(min(mode_doms.values())) if mode_doms else 0.0
        ready = bool(
            (not bool(cand.get("oracle_control", False)))
            and old_strict
            and actual_p90 <= -2.0e-5
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
                "actual_mean": actual_mean,
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these_null)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dominance,
                "mean_dominance": mean_dominance,
                "worst_mode_p90_dominance": worst_mode,
                **mode_doms,
                "public_free_submission_ready": ready,
                "final_decision": (
                    "public_free_submission_ready"
                    if ready
                    else ("oracle_control_not_submittable" if bool(cand.get("oracle_control", False)) else "blocked_by_e319_nulls")
                ),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            [
                "public_free_submission_ready",
                "oracle_control",
                "old_strict_promote",
                "null_strict_rate",
                "actual_p90",
                "mean_dominance",
            ],
            ascending=[False, True, False, True, True, False],
        ).reset_index(drop=True)
    return selected, null_map, governor


def write_report(
    selected_routes: pd.DataFrame,
    prefilter: pd.DataFrame,
    selected: pd.DataFrame,
    governor: pd.DataFrame,
) -> pd.DataFrame:
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    non_oracle_gov = governor[~governor.get("oracle_control", pd.Series(False, index=governor.index)).astype(bool)] if not governor.empty else pd.DataFrame()
    summary_rows: list[dict[str, Any]] = []
    for label, frame in [
        ("prefilter_all", prefilter),
        ("governor_non_oracle", non_oracle_gov),
        ("governor_all", governor),
    ]:
        if frame.empty:
            summary_rows.append({"slice": label, "rows": 0})
            continue
        row = {
            "slice": label,
            "rows": int(len(frame)),
            "old_strict": int(frame["strict_promote_gate"].sum()) if "strict_promote_gate" in frame else int(frame["old_strict_promote"].sum()),
            "info": int(frame["info_sensor_gate"].sum()) if "info_sensor_gate" in frame else np.nan,
            "ready": int(frame["public_free_submission_ready"].sum()) if "public_free_submission_ready" in frame else np.nan,
            "best_p90": float(frame["pred_delta_vs_current_p90"].min()) if "pred_delta_vs_current_p90" in frame else float(frame["actual_p90"].min()),
            "best_mean": float(frame["pred_delta_vs_current_mean"].min()) if "pred_delta_vs_current_mean" in frame else float(frame["actual_mean"].min()),
        }
        if "null_strict_rate" in frame:
            row["best_null_strict"] = float(frame["null_strict_rate"].min())
            row["best_worst_mode"] = float(frame["worst_mode_p90_dominance"].max())
        summary_rows.append(row)
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY_OUT, index=False)

    recipe_pref = (
        prefilter.groupby(["recipe", "oracle_control"], dropna=False)
        .agg(
            generated=("basename", "count"),
            old_strict=("strict_promote_gate", "sum"),
            info=("info_sensor_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_mean=("pred_delta_vs_current_mean", "min"),
            median_l1=("l1_delta", "median"),
        )
        .reset_index()
        .sort_values(["old_strict", "best_p90"], ascending=[False, True])
        if not prefilter.empty
        else pd.DataFrame()
    )
    recipe_gov = (
        governor.groupby(["recipe", "oracle_control"], dropna=False)
        .agg(
            evaluated=("basename", "count"),
            old_strict=("old_strict_promote", "sum"),
            ready=("public_free_submission_ready", "sum"),
            best_p90=("actual_p90", "min"),
            best_null_strict=("null_strict_rate", "min"),
            best_worst_mode=("worst_mode_p90_dominance", "max"),
        )
        .reset_index()
        .sort_values(["ready", "old_strict", "best_null_strict", "best_p90"], ascending=[False, False, True, True])
        if not governor.empty
        else pd.DataFrame()
    )
    mode_readout = (
        selected_routes[selected_routes["policy"].isin(POLICIES)]
        .groupby(["policy", "placement_mode"])
        .agg(count=("basename", "count"), true_rank_mean=("true_p90_rank_health", "mean"))
        .reset_index()
        .sort_values(["policy", "count"], ascending=[True, False])
    )
    show_cols = [
        "basename",
        "recipe",
        "policy",
        "group_key",
        "base_variant",
        "source_count",
        "selected_mode_mix",
        "oracle_control",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "final_decision",
    ]
    lines = [
        "# E319 Mode-Specialized Generator",
        "",
        "Public LB was not used. E318 route policies were used only to build fresh consensus/blend/residual tensors; selected E315 null-control files were not promoted directly.",
        "",
        "## Question",
        "",
        "Can the hidden placement-regime signal become a new probability tensor that is both selector-visible and rare under matched row/subject/dateblock/target/sign controls?",
        "",
        "## Route Readout",
        "",
        md(mode_readout, n=40),
        "",
        "## Prefilter",
        "",
        f"- generated candidates: `{len(prefilter)}`",
        f"- old strict candidates: `{int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}`",
        f"- info candidates: `{int(prefilter['info_sensor_gate'].sum()) if not prefilter.empty else 0}`",
        f"- null-evaluated candidates: `{len(selected)}`",
        "",
        md(recipe_pref, n=30),
        "",
        "## Matched Null Governor",
        "",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md(summary, n=10),
        "",
        md(recipe_gov, n=30),
        "",
        md(governor[[c for c in show_cols if c in governor.columns]] if not governor.empty else governor, n=60),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        top = ready.iloc[0]
        lines.append(f"`{top['basename']}` is public-free ready. It should still be treated as a scarce-slot hypothesis test, not as proof of the route policy.")
    else:
        lines.extend(
            [
                "- No E319 fresh mode-specialized tensor is public-free ready.",
                "- If old-strict tensors are null-common, the E318 regime signal is still diagnostic rather than generative.",
                "- If oracle-control tensors also fail, the archive's placement oracle cannot be translated by consensus alone.",
                "- The next branch should learn mode-specific action geometry directly instead of averaging selected placements.",
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
            f"- `{SUMMARY_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    current = current_frame()
    base, _, _, _ = load_frames()
    test_df = base.loc[base["split"].eq("test")].reset_index(drop=True)
    meta = align_meta_to_current(test_df, current)
    routes = attach_deltas(selected_rows(), current)
    candidate_meta, delta_map = generate_candidates(current, routes)
    prefilter = score_prefilter(candidate_meta, current) if not candidate_meta.empty else pd.DataFrame()
    selected = select_for_null(prefilter) if not prefilter.empty else pd.DataFrame()
    selected, nulls, governor = run_governor(selected, delta_map, current, meta) if not selected.empty else (selected, pd.DataFrame(), pd.DataFrame())
    prefilter.to_csv(CANDIDATE_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    if not nulls.empty:
        nulls.to_csv(NULL_MAP_OUT, index=False)
    summary = write_report(routes, prefilter, selected, governor)
    ready_count = int(governor["public_free_submission_ready"].sum()) if not governor.empty else 0
    old_strict = int(prefilter["strict_promote_gate"].sum()) if not prefilter.empty else 0
    print(f"routes={len(routes)}")
    print(f"generated_candidates={len(prefilter)}")
    print(f"old_strict={old_strict}")
    print(f"null_evaluated={len(selected)}")
    print(f"public_ready={ready_count}")
    if not governor.empty:
        print(f"best_actual_p90={governor['actual_p90'].min():.9f}")
        print(f"best_null_strict={governor['null_strict_rate'].min():.6f}")
    print(f"summary_rows={len(summary)}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
