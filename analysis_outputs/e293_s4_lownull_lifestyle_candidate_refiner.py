#!/usr/bin/env python3
"""E293: S4 low-null lifestyle candidate refiner.

E292 narrowed the lifestyle branch to one useful near-miss:

    S4 / subject_lifestyle_bin / raw delta

It reduced matched-null strict promotion sharply, but not enough to submit. This
script searches the narrow scale/selection pocket between "too small" and
"matched nulls also promote". No public LB is used.
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
NULL_DIR = OUT / "e293_s4_lownull_lifestyle_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import TARGETS, md_table, stable_seed  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import normalize_keys, prep_test_meta  # noqa: E402
from e290_lifestyle_row_placement_law_audit import align_columns  # noqa: E402
from e291_lifestyle_block_state_assignment_audit import (  # noqa: E402
    build_lifestyle_cache,
    make_block_model,
    run_block_audit,
    safe_id,
)
from e292_contrastive_lifestyle_placement_invariant import contrast_table, select_contrast  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

RNG_SEED = 20260531 + 293
MAX_PARENTS = 6
MAX_NULL_EVAL = 64
N_TEST_NULL_REPS = 7
SCALES = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
BASE_RULES = [f"base_lowmax{v}" for v in [20, 25, 30, 35, 40, 45, 50, 60]]
FIXED_NS = [8, 12, 16, 20, 28]

PREFILTER_OUT = OUT / "e293_s4_lownull_prefilter_summary.csv"
CANDIDATE_OUT = OUT / "e293_s4_lownull_candidate_summary.csv"
GOVERNOR_OUT = OUT / "e293_s4_lownull_governor_summary.csv"
SCORE_OUT = OUT / "e293_s4_lownull_scores.csv"
NULL_MAP_OUT = OUT / "e293_s4_lownull_null_map.csv"
REPORT_OUT = OUT / "e293_s4_lownull_report.md"


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


def select_top_n(score: np.ndarray, n_select: int) -> np.ndarray:
    n_select = max(1, min(int(n_select), len(score)))
    selected = np.zeros(len(score), dtype=bool)
    selected[np.argsort(np.asarray(score, dtype=np.float64))[::-1][:n_select]] = True
    return selected


def select_rule(tab: pd.DataFrame, base_frac: float, rule: str) -> np.ndarray:
    if rule.startswith("base_lowmax"):
        return select_contrast(tab, base_frac, rule)
    if rule.startswith("rarity_top"):
        n = int(rule.replace("rarity_top", ""))
        return select_top_n(tab["rarity_score"].to_numpy(dtype=np.float64), n)
    if rule.startswith("contrast_top"):
        n = int(rule.replace("contrast_top", ""))
        return select_top_n(tab["contrast_score"].to_numpy(dtype=np.float64), n)
    if rule.startswith("hybrid_low"):
        parts = rule.replace("hybrid_low", "").split("_top")
        threshold = float(parts[0]) / 100.0
        n = int(parts[1])
        mask = tab["null_max_rate"].to_numpy(dtype=np.float64) <= threshold
        if mask.sum() < 2:
            mask = np.ones(len(tab), dtype=bool)
        score = tab["rarity_score"].to_numpy(dtype=np.float64).copy()
        score[~mask] = -np.inf
        return select_top_n(score, min(n, int(mask.sum())))
    raise ValueError(rule)


def s4_parent_rows(block_summary: pd.DataFrame) -> pd.DataFrame:
    parent = block_summary[
        block_summary["target"].eq("S4")
        & block_summary["view_id"].eq("family_jepa_context")
        & block_summary["split"].eq("dateblock5")
        & block_summary["rep"].eq("cluster6")
        & block_summary["block_scheme"].eq("subject_lifestyle_bin")
        & block_summary["block_gate_bool"].astype(bool)
    ].copy()
    parent = parent.sort_values(
        ["actual_delta", "dominance", "row_dominance", "subject_dominance", "dateblock_dominance"],
        ascending=[True, False, False, False, False],
    )
    return parent.head(MAX_PARENTS).reset_index(drop=True)


def write_candidate(
    base: pd.DataFrame,
    row_block: pd.Series,
    test_blocks: pd.DataFrame,
    selected: np.ndarray,
    raw_delta: np.ndarray,
    scale: float,
    candidate_id: str,
) -> tuple[Path, np.ndarray]:
    selected_blocks = set(test_blocks.loc[selected, "block_key"].astype(str))
    row_selected = row_block.astype(str).isin(selected_blocks).to_numpy()
    selected_delta = np.where(row_selected, scale * np.asarray(raw_delta, dtype=np.float64), 0.0)
    out = base.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index("S4")] += selected_delta
    out[TARGETS] = np.clip(sigmoid(logits), 1.0e-6, 1.0 - 1.0e-6)
    path = OUT / f"submission_e293_s4lownull_{safe_id(candidate_id)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, selected_delta


def write_null_candidate(base: pd.DataFrame, selected_delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(stable_seed("e293null", source_path.name, mode, rep))
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
    logits[:, TARGETS.index("S4")] += shuffled
    out[TARGETS] = np.clip(sigmoid(logits), 1.0e-6, 1.0 - 1.0e-6)
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e293null_{source_path.stem[:72]}_{mode}_r{rep}_{short_hash(out)}.csv"
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


def candidate_rules() -> list[str]:
    rules = list(BASE_RULES)
    rules += [f"rarity_top{n}" for n in FIXED_NS]
    rules += [f"contrast_top{n}" for n in FIXED_NS]
    rules += [f"hybrid_low{thr}_top{n}" for thr in [45, 55, 65, 75] for n in [8, 12, 16]]
    return rules


def generate_candidates(block_summary: pd.DataFrame, block_cache: dict[str, dict[str, Any]], current: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray], list[Path]]:
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    paths: list[Path] = []
    parents = s4_parent_rows(block_summary)
    rules = candidate_rules()
    for _, parent in parents.iterrows():
        parent_id = str(parent["policy_id"])
        cache = block_cache[parent_id]
        x_train = cache["block_table"][cache["feature_cols"]]
        x_test = cache["test_table"].reindex(columns=["block_key", "subject_id", "dateblock_group", *cache["feature_cols"]], fill_value=0.0)[cache["feature_cols"]]
        x_train, x_test = align_columns(x_train, x_test)
        model = make_block_model()
        model.fit(x_train, cache["labels"])
        test_score = model.predict_proba(x_test)[:, 1]
        frac = float(parent["block_frac"])
        tab = contrast_table(test_score, frac, cache["test_table"], f"e293_{parent_id}_{frac:.3f}")
        for rule in rules:
            selected = select_rule(tab, frac, rule)
            if int(selected.sum()) < 2:
                continue
            for scale in SCALES:
                candidate_id = f"{parent_id}_{rule}_bf{int(frac*100):02d}_raw_s{int(scale*100):03d}"
                path, selected_delta = write_candidate(
                    current,
                    cache["test_block"],
                    cache["test_table"],
                    selected,
                    cache["raw_delta"],
                    scale,
                    candidate_id,
                )
                paths.append(path)
                deltas[path.name] = selected_delta
                rows.append(
                    {
                        "candidate_id": candidate_id,
                        "basename": path.name,
                        "source_path": rel(path),
                        "parent_policy_id": parent_id,
                        "rule": rule,
                        "scale": scale,
                        "parent_actual_delta": float(parent["actual_delta"]),
                        "parent_dominance": float(parent["dominance"]),
                        "parent_min_mode_dominance": float(min(parent["row_dominance"], parent["subject_dominance"], parent["dateblock_dominance"])),
                        "base_block_frac": frac,
                        "selected_blocks": int(selected.sum()),
                        "selected_rows": int(np.count_nonzero(np.abs(selected_delta) > 1.0e-12)),
                        "selected_null_mean_rate": float(tab.loc[selected, "null_mean_rate"].mean()),
                        "selected_null_max_rate": float(tab.loc[selected, "null_max_rate"].mean()),
                        "selected_score_rank": float(tab.loc[selected, "score_rank"].mean()),
                        "selected_rarity_score": float(tab.loc[selected, "rarity_score"].mean()),
                        "selected_contrast_score": float(tab.loc[selected, "contrast_score"].mean()),
                        "delta_mean": float(np.mean(selected_delta)),
                        "delta_p90_abs": float(np.quantile(np.abs(selected_delta), 0.90)),
                        "delta_l1": float(np.sum(np.abs(selected_delta))),
                    }
                )
    return pd.DataFrame(rows), deltas, paths


def score_prefilter(candidate_meta: pd.DataFrame, candidate_paths: list[Path], current: pd.DataFrame) -> pd.DataFrame:
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = feature_rows([OUT / CURRENT, *candidate_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    score_cols = [
        "basename",
        "promotion_decision",
        "strict_promote_gate",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    merged = candidate_meta.merge(scores[score_cols], on="basename", how="left")
    merged = merged.sort_values(
        ["strict_promote_gate", "pred_delta_vs_current_p90", "selected_null_max_rate", "pred_delta_vs_current_mean"],
        ascending=[False, True, True, True],
    ).drop_duplicates("basename").reset_index(drop=True)
    return merged


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    old = prefilter[prefilter["strict_promote_gate"].astype(bool)].copy()
    close = prefilter[
        (~prefilter["strict_promote_gate"].astype(bool))
        & prefilter["pred_delta_vs_current_mean"].lt(0.0)
        & prefilter["pred_delta_vs_current_p90"].lt(-2.0e-5)
    ].copy()
    if not old.empty:
        old["balanced_rank"] = (
            old["selected_null_max_rate"].rank(method="average", pct=True)
            + old["pred_delta_vs_current_p90"].rank(method="average", pct=True)
            + 0.25 * old["pred_delta_vs_current_mean"].rank(method="average", pct=True)
        )
    n_bucket = max(8, MAX_NULL_EVAL // 4)
    selected = pd.concat(
        [
            old.sort_values(["selected_null_max_rate", "pred_delta_vs_current_p90"]).head(n_bucket),
            old.sort_values(["pred_delta_vs_current_p90", "selected_null_max_rate"]).head(n_bucket),
            old.sort_values(["balanced_rank", "selected_null_max_rate"]).head(n_bucket),
            close.sort_values(["selected_null_max_rate", "pred_delta_vs_current_p90"]).head(n_bucket),
        ],
        ignore_index=True,
    )
    if selected.empty:
        selected = prefilter.sort_values(["pred_delta_vs_current_p90", "selected_null_max_rate"]).head(MAX_NULL_EVAL).copy()
    selected = selected.drop_duplicates("basename").reset_index(drop=True)
    if len(selected) < MAX_NULL_EVAL and len(old):
        fill = old[~old["basename"].isin(selected["basename"])].sort_values(
            ["selected_null_max_rate", "pred_delta_vs_current_p90"]
        ).head(MAX_NULL_EVAL - len(selected))
        selected = pd.concat([selected, fill], ignore_index=True).drop_duplicates("basename").reset_index(drop=True)
    return selected.head(MAX_NULL_EVAL)


def run_governor(selected: pd.DataFrame, deltas: dict[str, np.ndarray], current: pd.DataFrame, test_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    meta = prep_test_meta(test_df)
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    candidate_paths = [OUT / b for b in selected["basename"].tolist()]
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        selected_delta = deltas[basename]
        source_path = OUT / basename
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_TEST_NULL_REPS):
                null_path = write_null_candidate(current, selected_delta, source_path, meta, mode, rep)
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
    features = feature_rows([OUT / CURRENT, *candidate_paths, *null_paths], sample, refs, ref_vecs)
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
            ["public_free_submission_ready", "old_strict_promote", "null_strict_rate", "actual_p90", "mean_dominance"],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    return selected, null_map, governor


def write_report(prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    old_strict = prefilter[prefilter["strict_promote_gate"].astype(bool)] if not prefilter.empty else pd.DataFrame()
    lines = [
        "# E293 S4 Low-Null Lifestyle Candidate Refiner",
        "",
        "## Question",
        "",
        "Is there a narrow S4 lifestyle-bin raw edit between too-small movement and matched-null promotion?",
        "",
        "## Prefilter",
        "",
        f"- generated candidates: `{len(prefilter)}`",
        f"- old strict candidates: `{len(old_strict)}`",
        f"- null-evaluated candidates: `{len(selected)}`",
        "",
        md_table(
            prefilter[
                [
                    "basename",
                    "rule",
                    "scale",
                    "selected_rows",
                    "selected_null_max_rate",
                    "promotion_decision",
                    "pred_delta_vs_current_mean",
                    "pred_delta_vs_current_p90",
                    "strict_promote_gate",
                ]
            ] if not prefilter.empty else prefilter,
            n=30,
        ),
        "",
        "## Matched Null Governor",
        "",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor[
                [
                    "basename",
                    "rule",
                    "scale",
                    "selected_rows",
                    "selected_null_max_rate",
                    "old_promotion_decision",
                    "actual_mean",
                    "actual_p90",
                    "null_strict_rate",
                    "p90_dominance",
                    "mean_dominance",
                    "worst_mode_p90_dominance",
                    "final_decision",
                ]
            ] if not governor.empty else governor,
            n=50,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("At least one E293 candidate is public-free ready. Submit only the top ready S4 file as a scarce-LB test.")
    else:
        lines.append("No E293 candidate is public-free ready. The S4 low-null pocket remains diagnostic, not submit-safe.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "E293 is intentionally narrow. A win would mean the S4 lifestyle-bin story can be converted into a placement-safe edit by tuning scale and null rarity. A fail means the remaining problem is not scale granularity but a missing candidate-level invariant.",
            "",
            "## Files",
            "",
            f"- `{PREFILTER_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train_df, test_df, base_train, base_test, lifestyle_cache = build_lifestyle_cache()
    block_summary, block_cache = run_block_audit(train_df, test_df, base_train, base_test, lifestyle_cache)
    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    if not prep_test_meta(test_df)[KEYS].equals(normalize_keys(current[KEYS])):
        raise RuntimeError("E293 test features do not align with current submission")
    candidate_meta, deltas, candidate_paths = generate_candidates(block_summary, block_cache, current)
    prefilter = score_prefilter(candidate_meta, candidate_paths, current) if not candidate_meta.empty else pd.DataFrame()
    selected = select_for_null(prefilter) if not prefilter.empty else pd.DataFrame()
    selected, null_map, governor = run_governor(selected, deltas, current, test_df) if not selected.empty else (selected, pd.DataFrame(), pd.DataFrame())
    prefilter.to_csv(PREFILTER_OUT, index=False)
    selected.to_csv(CANDIDATE_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    write_report(prefilter, selected, governor)
    print(f"generated_candidates={len(prefilter)}")
    print(f"old_strict={int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}")
    print(f"null_evaluated={len(selected)}")
    print(f"nulls={len(null_map)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    if not governor.empty:
        print(f"best_null_strict={governor['null_strict_rate'].min():.6f}")
        print(f"best_actual_p90={governor['actual_p90'].min():.9f}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
