#!/usr/bin/env python3
"""E297: materialize strict human episode-state signals on the current best.

E296 found a small number of episode-target states that survived strict train
matched-null stress. This script asks the next public-free question: if those
states are translated into target-limited edits on the current best submission,
do the edits survive the existing current-anchor governor and matched test
nulls?

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
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e297_episode_state_materializer_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    base_label_matrix,
    build_context_views,
    clip_prob,
    groups_for,
    load_frames,
    md_table,
    oof_multi_ridge,
    stable_seed,
)
from e289_target_specific_lifestyle_slice_audit import normalize_keys, prep_test_meta, safe_id  # noqa: E402
from e295_episode_state_jepa_audit import build_episode_matrix, fit_predict_test  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

STRICT_OUT = OUT / "e296_episode_target_strict_candidates.csv"
CANDIDATE_OUT = OUT / "e297_episode_state_materializer_candidates.csv"
SELECTED_OUT = OUT / "e297_episode_state_materializer_selected.csv"
GOVERNOR_OUT = OUT / "e297_episode_state_materializer_governor.csv"
SCORE_OUT = OUT / "e297_episode_state_materializer_scores.csv"
NULL_MAP_OUT = OUT / "e297_episode_state_materializer_null_map.csv"
REPORT_OUT = OUT / "e297_episode_state_materializer_report.md"

SCALES = [0.06, 0.10, 0.15, 0.22, 0.30]
RULES = ["all_centered", "topabs16", "topabs32", "topabs64", "pos_top24", "neg_top24"]
CAP = 0.65
MAX_SOURCE_INSTANCES = 5
MAX_NULL_EVAL = 40
N_TEST_NULL_REPS = 7


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


def align_matrix_to_current(test_df: pd.DataFrame, values: np.ndarray, current: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    meta = prep_test_meta(test_df)[KEYS].copy()
    val_df = pd.DataFrame(np.asarray(values, dtype=np.float64), columns=cols)
    keyed = pd.concat([meta, val_df], axis=1)
    merged = normalize_keys(current[KEYS]).merge(keyed, on=KEYS, how="left", validate="one_to_one")
    if merged[cols].isna().any().any():
        raise RuntimeError("Could not align test values to current submission keys")
    return merged[cols].reset_index(drop=True)


def align_meta_to_current(test_df: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    meta = prep_test_meta(test_df)
    merged = normalize_keys(current[KEYS]).merge(meta, on=KEYS, how="left", validate="one_to_one")
    if merged["dateblock_group"].isna().any():
        raise RuntimeError("Could not align test metadata to current submission keys")
    return merged.reset_index(drop=True)


def fit_prob(x: pd.DataFrame, y: np.ndarray):
    if len(np.unique(y)) < 2:
        return None
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.35, max_iter=1200, solver="lbfgs"),
    )
    model.fit(x, y)
    return model


def model_delta(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    base_train: pd.DataFrame,
    base_test: pd.DataFrame,
    state_train: pd.Series,
    state_test: pd.Series,
    target: str,
) -> np.ndarray:
    y = train_df[target].to_numpy(dtype=int)
    x_base_tr = base_train.reset_index(drop=True)
    x_base_te = base_test.reset_index(drop=True)
    x_aug_tr = pd.concat([x_base_tr, state_train.reset_index(drop=True).rename("episode_state")], axis=1)
    x_aug_te = pd.concat([x_base_te, state_test.reset_index(drop=True).rename("episode_state")], axis=1)
    x_base_tr, x_base_te = x_base_tr.align(x_base_te, join="outer", axis=1, fill_value=0.0)
    x_aug_tr, x_aug_te = x_aug_tr.align(x_aug_te, join="outer", axis=1, fill_value=0.0)
    base_model = fit_prob(x_base_tr, y)
    aug_model = fit_prob(x_aug_tr, y)
    if base_model is None or aug_model is None:
        return np.zeros(len(test_df), dtype=np.float64)
    base_prob = base_model.predict_proba(x_base_te)[:, 1]
    aug_prob = aug_model.predict_proba(x_aug_te)[:, 1]
    delta = logit(aug_prob) - logit(base_prob)
    delta = delta - float(np.median(delta))
    return np.clip(delta, -CAP, CAP)


def rule_delta(delta: np.ndarray, rule: str) -> np.ndarray:
    values = np.asarray(delta, dtype=np.float64).copy()
    out = np.zeros_like(values)
    if rule == "all_centered":
        return values
    if rule.startswith("topabs"):
        n = int(rule.replace("topabs", ""))
        idx = np.argsort(np.abs(values))[::-1][: min(n, len(values))]
        out[idx] = values[idx]
        return out
    if rule.startswith("pos_top"):
        n = int(rule.replace("pos_top", ""))
        idx = np.argsort(values)[::-1][: min(n, len(values))]
        out[idx] = np.maximum(values[idx], 0.0)
        return out
    if rule.startswith("neg_top"):
        n = int(rule.replace("neg_top", ""))
        idx = np.argsort(values)[: min(n, len(values))]
        out[idx] = np.minimum(values[idx], 0.0)
        return out
    raise ValueError(rule)


def write_candidate(current: pd.DataFrame, target: str, delta: np.ndarray, candidate_id: str, scale: float) -> tuple[Path, np.ndarray]:
    applied = scale * np.asarray(delta, dtype=np.float64)
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += applied
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e297_epstate_{safe_id(candidate_id)}_s{int(scale*100):03d}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, applied


def write_null_candidate(current: pd.DataFrame, target: str, applied_delta: np.ndarray, source_path: Path, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(stable_seed("e297null", source_path.name, mode, rep))
    values = np.asarray(applied_delta, dtype=np.float64)
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
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(target)] += shuffled
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e297null_{source_path.stem[:72]}_{mode}_r{rep}_{short_hash(out)}.csv"
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


def source_instances() -> pd.DataFrame:
    strict = pd.read_csv(STRICT_OUT)
    robust = strict[strict["robust_gate"].astype(bool)].copy()
    if robust.empty:
        robust = strict[strict["strict_gate"].astype(bool)].copy()
    robust = robust.sort_values(["robust_gate", "delta_logloss", "margin_to_null_q05"], ascending=[False, True, False])
    return robust.head(MAX_SOURCE_INSTANCES).reset_index(drop=True)


def generate_candidates() -> tuple[pd.DataFrame, dict[str, np.ndarray], pd.DataFrame, pd.DataFrame]:
    sources = source_instances()
    if sources.empty:
        return pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame()
    base, raw, _, feature_frames = load_frames()
    current = load_sub(OUT / CURRENT).sort_values(KEYS).reset_index(drop=True)
    story_state, _ = build_episode_matrix(base, feature_frames)
    contexts = build_context_views(base, raw)
    train_mask = base["split"].eq("train").to_numpy()
    train_df = base.loc[train_mask].reset_index(drop=True)
    test_df = base.loc[~train_mask].reset_index(drop=True)
    base_train = base_label_matrix(train_df)
    base_test = base_label_matrix(test_df)
    base_train, base_test = base_train.align(base_test, join="outer", axis=1, fill_value=0.0)
    y_episode = story_state.loc[train_mask].reset_index(drop=True)
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    paths: list[Path] = []

    for (view_id, split_name), subset in sources.groupby(["view_id", "split"], sort=False):
        ctx = contexts[view_id]
        x_train = ctx.loc[train_mask].reset_index(drop=True)
        x_test = ctx.loc[~train_mask].reset_index(drop=True)
        groups = groups_for(train_df, split_name).reset_index(drop=True)
        pred_train = oof_multi_ridge(x_train, y_episode, groups)
        pred_test = fit_predict_test(x_train, y_episode, x_test)
        pred_train_df = pd.DataFrame(pred_train, columns=y_episode.columns)
        pred_test_df = align_matrix_to_current(test_df, pred_test, current, list(y_episode.columns))
        for _, source in subset.iterrows():
            episode = str(source["episode"])
            target = str(source["target"])
            delta_unsorted = model_delta(
                train_df,
                test_df,
                base_train,
                base_test,
                pred_train_df[episode],
                pd.Series(pred_test[:, list(y_episode.columns).index(episode)]),
                target,
            )
            delta = align_matrix_to_current(test_df, delta_unsorted.reshape(-1, 1), current, ["delta"])["delta"].to_numpy()
            for rule in RULES:
                shaped = rule_delta(delta, rule)
                if np.count_nonzero(np.abs(shaped) > 1.0e-12) == 0:
                    continue
                for scale in SCALES:
                    candidate_id = f"{episode}_{target}_{view_id}_{split_name}_{rule}"
                    path, applied = write_candidate(current, target, shaped, candidate_id, scale)
                    paths.append(path)
                    deltas[path.name] = applied
                    rows.append(
                        {
                            "basename": path.name,
                            "source_path": rel(path),
                            "episode": episode,
                            "target": target,
                            "view_id": view_id,
                            "split": split_name,
                            "rule": rule,
                            "scale": scale,
                            "source_delta_logloss": float(source["delta_logloss"]),
                            "source_robust_gate": bool(source["robust_gate"]),
                            "source_dominance": float(source["dominance"]),
                            "source_min_mode_dominance": float(source["min_mode_dominance"]),
                            "nonzero_rows": int(np.count_nonzero(np.abs(applied) > 1.0e-12)),
                            "mean_abs_delta": float(np.mean(np.abs(applied))),
                            "max_abs_delta": float(np.max(np.abs(applied))),
                            "signed_delta_sum": float(np.sum(applied)),
                        }
                    )
    return pd.DataFrame(rows), deltas, current, align_meta_to_current(test_df, current)


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
        .groupby(["episode", "target"], as_index=False)
        .head(2)
    )
    selected = pd.concat(
        [
            strict.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 2),
            info.sort_values(["pred_delta_vs_current_p90", "pred_delta_vs_current_mean"]).head(MAX_NULL_EVAL // 3),
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
        target = str(row["target"])
        applied = deltas[basename]
        source_path = OUT / basename
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_TEST_NULL_REPS):
                null_path = write_null_candidate(current, target, applied, source_path, meta, mode, rep)
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
        "# E297 Episode-State Materializer",
        "",
        "## Question",
        "",
        "Can the strict E296 human episode-target states be translated into current-best E247 edits that survive the public-free governor?",
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
                    "episode",
                    "target",
                    "rule",
                    "scale",
                    "nonzero_rows",
                    "promotion_decision",
                    "pred_delta_vs_current_mean",
                    "pred_delta_vs_current_p90",
                    "strict_promote_gate",
                ]
            ] if not prefilter.empty else prefilter,
            n=35,
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
                    "episode",
                    "target",
                    "rule",
                    "scale",
                    "nonzero_rows",
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
            n=60,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        top = ready.iloc[0]
        lines.append(
            f"`{top['basename']}` is public-free ready. Treat it as a scarce-slot hypothesis: bedtime/routine episode state can safely adjust `{top['target']}` on top of E247."
        )
    else:
        lines.append(
            "No E297 materialization is public-free ready. The episode states are real local label signals, but this translator does not yet make a placebo-resistant E247 edit."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This is the first strict bridge from human/social episode theory to current-submission action in this branch. A fail does not kill the bedtime/routine state; it says the current logistic delta translator is too crude or too selector-visible compared with matched null placements.",
            "",
            "## Files",
            "",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{SELECTED_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
            f"- `{SCORE_OUT.name}`",
            f"- `{NULL_MAP_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    candidate_meta, deltas, current, meta = generate_candidates()
    prefilter = score_prefilter(candidate_meta, current) if not candidate_meta.empty else pd.DataFrame()
    selected = select_for_null(prefilter) if not prefilter.empty else pd.DataFrame()
    selected, null_map, governor = run_governor(selected, deltas, current, meta) if not selected.empty else (selected, pd.DataFrame(), pd.DataFrame())
    prefilter.to_csv(CANDIDATE_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    governor.to_csv(GOVERNOR_OUT, index=False)
    if not null_map.empty:
        null_map.to_csv(NULL_MAP_OUT, index=False)
    write_report(prefilter, selected, governor)
    print(f"generated_candidates={len(prefilter)}")
    print(f"old_strict={int(prefilter['strict_promote_gate'].sum()) if not prefilter.empty else 0}")
    print(f"null_evaluated={len(selected)}")
    print(f"public_ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    if not governor.empty:
        print(f"best_actual_p90={governor['actual_p90'].min():.9f}")
        print(f"best_null_strict={governor['null_strict_rate'].min():.6f}")
    print(f"report={rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
