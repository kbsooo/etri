#!/usr/bin/env python3
"""E310: materialize E309 human target-pair interactions.

E309 found a live representation-level signal: human/social episode states
explain Q/S joint target patterns under row/subject/dateblock nulls. E310 asks
the public-free action question:

    Can those joint signals be translated into coupled target deltas on the
    current E247 tensor, while wrong-pair and shuffled-state controls lose?

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
NULL_DIR = OUT / "e310_pair_interaction_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    base_label_matrix,
    build_context_views,
    clip_prob,
    load_frames,
    stable_seed,
)
from e289_target_specific_lifestyle_slice_audit import normalize_keys, prep_test_meta, safe_id  # noqa: E402
from e295_episode_state_jepa_audit import build_episode_matrix, fit_predict_test  # noqa: E402
from e297_episode_state_materializer import align_matrix_to_current, align_meta_to_current, feature_rows, sigmoid  # noqa: E402
from e309_episode_target_interaction_probe import interaction_story, joint_code, pair_family  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

SOURCE_OUT = OUT / "e309_episode_target_interaction_strict.csv"
CANDIDATE_OUT = OUT / "e310_pair_interaction_candidates.csv"
SELECTED_OUT = OUT / "e310_pair_interaction_selected.csv"
GOVERNOR_OUT = OUT / "e310_pair_interaction_governor.csv"
SCORE_OUT = OUT / "e310_pair_interaction_scores.csv"
NULL_MAP_OUT = OUT / "e310_pair_interaction_null_map.csv"
REPORT_OUT = OUT / "e310_pair_interaction_report.md"

SCALES = [0.04, 0.07, 0.10, 0.14, 0.20]
RULES = ["joint_centered", "topabs32", "topabs64", "topabs96", "same_sign_top64", "opp_sign_top64", "diff_top64"]
CAP = 0.45
MAX_SOURCE_ROWS = 14
MAX_NULL_EVAL = 42
N_NULL_REPS = 4


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame is None or frame.empty:
        return "_empty_"
    out = frame.head(n).copy()
    for col in out.select_dtypes(include=[np.floating]).columns:
        out[col] = out[col].map(lambda x: f"{x:{floatfmt}}")
    cols = list(out.columns)
    rows = [[str(value) for value in row] for row in out.itertuples(index=False, name=None)]
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def pair_prob_model(x_train: pd.DataFrame, y: np.ndarray, x_test: pd.DataFrame) -> np.ndarray:
    counts = np.bincount(y, minlength=4).astype(np.float64) + 1.0
    prior = counts / counts.sum()
    if len(np.unique(y)) < 2:
        return np.tile(prior, (len(x_test), 1))
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(C=0.30, max_iter=1500, solver="lbfgs"),
    )
    model.fit(x_train, y)
    out = np.zeros((len(x_test), 4), dtype=np.float64)
    out[:] = prior * 0.02
    classes = model.named_steps["logisticregression"].classes_.astype(int)
    out[:, classes] += 0.98 * model.predict_proba(x_test)
    return out / out.sum(axis=1, keepdims=True)


def pair_marginals(prob: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p = clip_prob(prob)
    first = p[:, 2] + p[:, 3]
    second = p[:, 1] + p[:, 3]
    return clip_prob(first), clip_prob(second)


def source_rows() -> pd.DataFrame:
    src = pd.read_csv(SOURCE_OUT)
    live = src[src["robust_gate"].astype(bool)].copy()
    if live.empty:
        live = src[src["strict_gate"].astype(bool)].copy()
    live = live.sort_values(
        ["robust_gate", "strict_gate", "delta_logloss", "margin_to_null_q05"],
        ascending=[False, False, True, False],
    )
    # Keep repeated evidence for cashflow/Q1_S1, but avoid letting one family
    # consume the entire materialization budget.
    top = live.groupby(["episode", "pair"], as_index=False).head(3)
    return top.head(MAX_SOURCE_ROWS).reset_index(drop=True)


def centered_delta(delta: np.ndarray) -> np.ndarray:
    out = np.asarray(delta, dtype=np.float64).copy()
    out = out - np.median(out, axis=0, keepdims=True)
    return np.clip(out, -CAP, CAP)


def rule_delta(delta: np.ndarray, rule: str) -> np.ndarray:
    values = centered_delta(delta)
    out = np.zeros_like(values)
    score = np.max(np.abs(values), axis=1)
    if rule == "joint_centered":
        return values
    if rule.startswith("topabs"):
        n = int(rule.replace("topabs", ""))
        idx = np.argsort(score)[::-1][: min(n, len(values))]
        out[idx] = values[idx]
        return out
    if rule == "same_sign_top64":
        mask = np.sign(values[:, 0]) == np.sign(values[:, 1])
        idx = np.where(mask)[0][np.argsort(score[mask])[::-1][: min(64, int(mask.sum()))]]
        out[idx] = values[idx]
        return out
    if rule == "opp_sign_top64":
        mask = np.sign(values[:, 0]) != np.sign(values[:, 1])
        idx = np.where(mask)[0][np.argsort(score[mask])[::-1][: min(64, int(mask.sum()))]]
        out[idx] = values[idx]
        return out
    if rule == "diff_top64":
        diff = np.abs(values[:, 0] - values[:, 1])
        idx = np.argsort(diff)[::-1][: min(64, len(values))]
        out[idx] = values[idx]
        return out
    raise ValueError(rule)


def write_pair_candidate(current: pd.DataFrame, pair: tuple[str, str], delta: np.ndarray, candidate_id: str, scale: float) -> tuple[Path, np.ndarray]:
    a, b = pair
    applied = scale * np.asarray(delta, dtype=np.float64)
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(a)] += applied[:, 0]
    logits[:, TARGETS.index(b)] += applied[:, 1]
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = OUT / f"submission_e310_pair_{safe_id(candidate_id)}_s{int(scale*100):03d}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path, applied


def wrong_pair_for(pair: tuple[str, str], rep: int) -> tuple[str, str]:
    a, b = pair
    fam = pair_family(a, b)
    candidates: list[tuple[str, str]] = []
    for i, x in enumerate(TARGETS):
        for y in TARGETS[i + 1 :]:
            if (x, y) == pair:
                continue
            if pair_family(x, y) == fam:
                candidates.append((x, y))
    if not candidates:
        candidates = [(x, y) for i, x in enumerate(TARGETS) for y in TARGETS[i + 1 :] if (x, y) != pair]
    return candidates[rep % len(candidates)]


def write_null_candidate(
    current: pd.DataFrame,
    pair: tuple[str, str],
    applied_delta: np.ndarray,
    source_path: Path,
    meta: pd.DataFrame,
    mode: str,
    rep: int,
) -> Path:
    rng = np.random.default_rng(stable_seed("e310null", source_path.name, mode, rep))
    values = np.asarray(applied_delta, dtype=np.float64)
    shuffled = values.copy()
    target_pair = pair
    if mode == "row":
        shuffled = values[rng.permutation(len(values))]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr] = values[idx_arr][rng.permutation(len(idx_arr))]
    elif mode == "swap_targets":
        shuffled = values[:, ::-1]
    elif mode == "wrong_pair":
        target_pair = wrong_pair_for(pair, rep)
    elif mode == "sign_flip":
        shuffled = -values
    else:
        raise ValueError(mode)

    a, b = target_pair
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64))
    logits[:, TARGETS.index(a)] += shuffled[:, 0]
    logits[:, TARGETS.index(b)] += shuffled[:, 1]
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e310null_{source_path.stem[:64]}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_candidates() -> tuple[pd.DataFrame, dict[str, tuple[tuple[str, str], np.ndarray]], pd.DataFrame, pd.DataFrame]:
    sources = source_rows()
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
    deltas: dict[str, tuple[tuple[str, str], np.ndarray]] = {}
    for (view_id, split_name), subset in sources.groupby(["view_id", "split"], sort=False):
        ctx = contexts[view_id]
        x_train = ctx.loc[train_mask].reset_index(drop=True)
        x_test = ctx.loc[~train_mask].reset_index(drop=True)
        pred_test = fit_predict_test(x_train, y_episode, x_test)
        pred_test_df = align_matrix_to_current(test_df, pred_test, current, list(y_episode.columns))

        for _, source in subset.iterrows():
            episode = str(source["episode"])
            a, b = str(source["pair"]).split("_")
            pair = (a, b)
            state_train = y_episode[[episode]].reset_index(drop=True)
            state_test = pred_test_df[[episode]].reset_index(drop=True)
            y_pair = joint_code(train_df, a, b)
            x_base_tr, x_base_te = base_train.align(base_test, join="outer", axis=1, fill_value=0.0)
            x_aug_tr = pd.concat([x_base_tr.reset_index(drop=True), state_train.rename(columns={episode: "episode_state"})], axis=1)
            x_aug_te = pd.concat([x_base_te.reset_index(drop=True), state_test.rename(columns={episode: "episode_state"})], axis=1)
            base_prob = pair_prob_model(x_base_tr, y_pair, x_base_te)
            aug_prob = pair_prob_model(x_aug_tr, y_pair, x_aug_te)
            base_ma, base_mb = pair_marginals(base_prob)
            aug_ma, aug_mb = pair_marginals(aug_prob)
            raw_delta_unsorted = np.column_stack([logit(aug_ma) - logit(base_ma), logit(aug_mb) - logit(base_mb)])
            raw_delta = align_matrix_to_current(test_df, raw_delta_unsorted, current, ["d0", "d1"])[["d0", "d1"]].to_numpy()
            for rule in RULES:
                shaped = rule_delta(raw_delta, rule)
                if np.count_nonzero(np.abs(shaped) > 1.0e-12) == 0:
                    continue
                for scale in SCALES:
                    candidate_id = f"{episode}_{a}_{b}_{view_id}_{split_name}_{rule}"
                    path, applied = write_pair_candidate(current, pair, shaped, candidate_id, scale)
                    deltas[path.name] = (pair, applied)
                    rows.append(
                        {
                            "basename": path.name,
                            "source_path": rel(path),
                            "episode": episode,
                            "pair": f"{a}_{b}",
                            "pair_family": pair_family(a, b),
                            "interaction_story": interaction_story(episode, f"{a}_{b}"),
                            "view_id": view_id,
                            "split": split_name,
                            "rule": rule,
                            "scale": scale,
                            "source_delta_logloss": float(source["delta_logloss"]),
                            "source_robust_gate": bool(source["robust_gate"]),
                            "source_strict_dominance": float(source["strict_dominance"]),
                            "source_min_mode_dominance": float(source["strict_min_mode_dominance"]),
                            "source_margin_to_null_q05": float(source["margin_to_null_q05"]),
                            "nonzero_rows": int(np.any(np.abs(applied) > 1.0e-12, axis=1).sum()),
                            "mean_abs_delta": float(np.mean(np.abs(applied))),
                            "max_abs_delta": float(np.max(np.abs(applied))),
                            "signed_delta_sum_a": float(np.sum(applied[:, 0])),
                            "signed_delta_sum_b": float(np.sum(applied[:, 1])),
                            "delta_corr": float(np.corrcoef(applied[:, 0], applied[:, 1])[0, 1]) if np.std(applied[:, 0]) > 1e-12 and np.std(applied[:, 1]) > 1e-12 else 0.0,
                        }
                    )
    return pd.DataFrame(rows), deltas, current, align_meta_to_current(base.loc[~train_mask].reset_index(drop=True), current)


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
        .groupby(["episode", "pair"], as_index=False)
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


def run_governor(selected: pd.DataFrame, deltas: dict[str, tuple[tuple[str, str], np.ndarray]], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if selected.empty:
        return selected, pd.DataFrame(), pd.DataFrame()
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    modes = ["row", "subject", "dateblock", "swap_targets", "wrong_pair", "sign_flip"]
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        pair, applied = deltas[basename]
        source_path = OUT / basename
        for mode in modes:
            reps = N_NULL_REPS if mode in {"row", "subject", "dateblock", "wrong_pair"} else 1
            for rep in range(reps):
                null_path = write_null_candidate(current, pair, applied, source_path, meta, mode, rep)
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
                "final_decision": "public_free_submission_ready" if ready else ("blocked_by_pair_nulls" if old_strict else str(a.get("promotion_decision", "hold"))),
            }
        )
    governor = pd.DataFrame(rows)
    if not governor.empty:
        governor = governor.sort_values(
            ["public_free_submission_ready", "old_strict_promote", "null_strict_rate", "actual_p90", "wrong_pair_p90_dominance"],
            ascending=[False, False, True, True, False],
        ).reset_index(drop=True)
    return selected, null_map, governor


def write_report(prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    old_strict = prefilter[prefilter["strict_promote_gate"].astype(bool)] if not prefilter.empty else pd.DataFrame()
    source_read = (
        prefilter.groupby(["episode", "pair", "pair_family"], dropna=False)
        .agg(
            generated=("basename", "count"),
            old_strict=("strict_promote_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_mean=("pred_delta_vs_current_mean", "min"),
            median_move=("mean_abs_delta", "median"),
        )
        .reset_index()
        .sort_values(["old_strict", "best_p90"], ascending=[False, True])
        if not prefilter.empty
        else pd.DataFrame()
    )
    lines = [
        "# E310 Pair-Interaction Materializer",
        "",
        "Public LB는 사용하지 않았다. E309에서 살아남은 human episode target-pair representation을 current E247 tensor에 coupled target deltas로 번역하고, row/subject/dateblock/wrong-pair/swap/sign controls로 막았다.",
        "",
        "## Prefilter",
        "",
        f"- generated candidates: `{len(prefilter)}`",
        f"- old strict candidates: `{len(old_strict)}`",
        f"- null-evaluated candidates: `{len(selected)}`",
        "",
        "## Source Read",
        "",
        md_table(source_read, n=40),
        "",
        "## Matched Pair-Null Governor",
        "",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        md_table(
            governor[
                [
                    "basename",
                    "episode",
                    "pair",
                    "rule",
                    "scale",
                    "old_strict_promote",
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
            ]
            if not governor.empty
            else governor,
            n=60,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        top = ready.iloc[0]
        lines.append(
            f"`{top['basename']}` is public-free ready under E310 pair controls. It should be treated as a scarce-slot hypothesis for `{top['episode']}/{top['pair']}` target dependency."
        )
    else:
        lines.extend(
            [
                "- No E310 pair materialization is public-free ready.",
                "- If old strict candidates exist but wrong-pair or shuffled controls also promote, E309 remains a representation breakthrough but not yet a submission translator.",
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
