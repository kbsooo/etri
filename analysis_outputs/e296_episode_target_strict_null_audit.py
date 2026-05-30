#!/usr/bin/env python3
"""E296: strict null audit for E295 episode-target signals.

E295 is an atlas: it found many human episode states that help one target under
light matched-null stress. This script reruns only the high-information
episode-target pairs with a stricter null budget. No public LB is used and no
submission file is created.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    base_label_matrix,
    build_context_views,
    groups_for,
    label_cv_loss,
    load_frames,
    md_table,
    oof_multi_ridge,
    stable_seed,
)
from e295_episode_state_jepa_audit import (  # noqa: E402
    build_episode_matrix,
    fit_predict_test,
    shuffle_episode,
)


N_REPS = 64
PREV_TARGET_OUT = OUT / "e295_episode_state_target_detail.csv"
CANDIDATE_OUT = OUT / "e296_episode_target_strict_candidates.csv"
PAIR_OUT = OUT / "e296_episode_target_pair_summary.csv"
NULL_OUT = OUT / "e296_episode_target_strict_nulls.csv"
REPORT_OUT = OUT / "e296_episode_target_strict_null_report.md"


def select_episode_targets(prev: pd.DataFrame) -> pd.DataFrame:
    gated = prev[prev["target_gate"].astype(bool)].copy()
    if gated.empty:
        return gated
    mode_min = gated[["row_dominance", "subject_dominance", "dateblock_dominance"]].min(axis=1)
    gated["all_mode_dom"] = mode_min
    pair = (
        gated.groupby(["episode", "target"])
        .agg(
            e295_gate_instances=("target_gate", "size"),
            e295_best_delta=("delta_logloss", "min"),
            e295_mean_delta=("delta_logloss", "mean"),
            e295_best_dominance=("dominance", "max"),
            e295_min_mode_dom=("all_mode_dom", "min"),
        )
        .reset_index()
    )
    consensus = pair["e295_gate_instances"].ge(2)
    strong_single = pair["e295_best_delta"].lt(-0.012) & pair["e295_best_dominance"].ge(1.0)
    selected = pair[consensus | strong_single].copy()
    selected["selection_reason"] = np.where(
        selected["e295_gate_instances"].ge(2),
        "multi_view_or_split_consensus",
        "single_view_large_all_null_win",
    )
    return selected.sort_values(["e295_gate_instances", "e295_best_delta"], ascending=[False, True])


def candidate_rows(prev: pd.DataFrame, selected_pairs: pd.DataFrame) -> pd.DataFrame:
    keys = set(zip(selected_pairs["episode"], selected_pairs["target"]))
    rows = prev[prev["target_gate"].astype(bool)].copy()
    rows = rows[[(episode, target) in keys for episode, target in zip(rows["episode"], rows["target"])]]
    rows = rows.sort_values(["episode", "target", "view_id", "split"]).reset_index(drop=True)
    rows.insert(0, "candidate_id", [f"e296_{i:03d}" for i in range(len(rows))])
    return rows


def evaluate_candidate(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    groups: pd.Series,
    pred_state: pd.DataFrame,
    row: pd.Series,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    episode = str(row["episode"])
    target = str(row["target"])
    state = pred_state[[episode]].reset_index(drop=True)
    y = train_df[target].to_numpy(dtype=int)
    baseline_loss = label_cv_loss(base_x, y, groups)
    actual_loss = label_cv_loss(pd.concat([base_x.reset_index(drop=True), state], axis=1), y, groups)
    actual_delta = actual_loss - baseline_loss
    rng = np.random.default_rng(stable_seed("e296_strict", row["candidate_id"], row["view_id"], row["split"], episode, target))

    null_rows: list[dict[str, Any]] = []
    null_by_mode: dict[str, list[float]] = {"row": [], "subject": [], "dateblock": []}
    for mode in null_by_mode:
        for rep in range(N_REPS):
            shuffled = shuffle_episode(state.to_numpy(), mode, train_df, rng)
            nx = pd.concat(
                [base_x.reset_index(drop=True), pd.DataFrame(shuffled, columns=[episode])],
                axis=1,
            )
            null_delta = label_cv_loss(nx, y, groups) - baseline_loss
            null_by_mode[mode].append(null_delta)
            null_rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "view_id": row["view_id"],
                    "split": row["split"],
                    "episode": episode,
                    "target": target,
                    "mode": mode,
                    "rep": rep,
                    "null_delta": null_delta,
                }
            )

    null = np.asarray(sum(null_by_mode.values(), []), dtype=np.float64)
    mode_dom = {mode: float(np.mean(actual_delta < np.asarray(vals))) for mode, vals in null_by_mode.items()}
    mode_q05 = {f"{mode}_q05": float(np.quantile(vals, 0.05)) for mode, vals in null_by_mode.items()}
    result = {
        "candidate_id": row["candidate_id"],
        "view_id": row["view_id"],
        "split": row["split"],
        "episode": episode,
        "target": target,
        "base_loss": baseline_loss,
        "state_loss": actual_loss,
        "delta_logloss": actual_delta,
        "null_q01": float(np.quantile(null, 0.01)),
        "null_q05": float(np.quantile(null, 0.05)),
        "null_q20": float(np.quantile(null, 0.20)),
        "null_median": float(np.median(null)),
        "null_best": float(np.min(null)),
        "dominance": float(np.mean(actual_delta < null)),
        "row_dominance": mode_dom["row"],
        "subject_dominance": mode_dom["subject"],
        "dateblock_dominance": mode_dom["dateblock"],
        "p_value_lower": float((1.0 + np.sum(null <= actual_delta)) / (1.0 + len(null))),
        "margin_to_null_q05": float(np.quantile(null, 0.05) - actual_delta),
        "min_mode_dominance": float(min(mode_dom.values())),
        "strict_gate": bool(
            actual_delta < -0.003
            and np.mean(actual_delta < null) >= 0.95
            and min(mode_dom.values()) >= 0.80
            and actual_delta < np.quantile(null, 0.05)
        ),
        "robust_gate": bool(
            actual_delta < -0.005
            and np.mean(actual_delta < null) >= 0.99
            and min(mode_dom.values()) >= 0.90
            and actual_delta < np.quantile(null, 0.01)
        ),
        **mode_q05,
    }
    return result, null_rows


def run() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not PREV_TARGET_OUT.exists():
        raise FileNotFoundError(f"Missing E295 target detail: {PREV_TARGET_OUT}")
    prev = pd.read_csv(PREV_TARGET_OUT)
    selected = select_episode_targets(prev)
    candidates = candidate_rows(prev, selected)
    if candidates.empty:
        empty = pd.DataFrame()
        return empty, empty, empty

    base, raw, _, feature_frames = load_frames()
    story_state, _ = build_episode_matrix(base, feature_frames)
    contexts = build_context_views(base, raw)
    train_mask = base["split"].eq("train").to_numpy()
    train_df = base.loc[train_mask].reset_index(drop=True)
    base_x = base_label_matrix(train_df)
    y_episode = story_state.loc[train_mask].reset_index(drop=True)

    candidate_results: list[dict[str, Any]] = []
    null_results: list[dict[str, Any]] = []
    for (view_id, split_name), subset in candidates.groupby(["view_id", "split"], sort=False):
        ctx = contexts[view_id]
        x_train = ctx.loc[train_mask].reset_index(drop=True)
        x_test = ctx.loc[~train_mask].reset_index(drop=True)
        groups = groups_for(train_df, split_name).reset_index(drop=True)
        pred_train = oof_multi_ridge(x_train, y_episode, groups)
        _ = fit_predict_test(x_train, y_episode, x_test)
        pred_state = pd.DataFrame(pred_train, columns=y_episode.columns)
        for _, row in subset.iterrows():
            result, nulls = evaluate_candidate(train_df, base_x, groups, pred_state, row)
            actual = y_episode[result["episode"]].to_numpy(dtype=np.float64)
            pred = pred_state[result["episode"]].to_numpy(dtype=np.float64)
            result["state_r2"] = float(r2_score(actual, pred))
            result["state_corr"] = float(np.corrcoef(actual, pred)[0, 1]) if np.std(pred) > 1.0e-12 else 0.0
            candidate_results.append(result)
            null_results.extend(nulls)

    cand = pd.DataFrame(candidate_results)
    pair = (
        cand.groupby(["episode", "target"])
        .agg(
            instances=("candidate_id", "count"),
            strict_instances=("strict_gate", "sum"),
            robust_instances=("robust_gate", "sum"),
            best_delta=("delta_logloss", "min"),
            mean_delta=("delta_logloss", "mean"),
            best_p_value=("p_value_lower", "min"),
            worst_min_mode_dominance=("min_mode_dominance", "min"),
            mean_margin_q05=("margin_to_null_q05", "mean"),
            best_state_corr=("state_corr", "max"),
        )
        .reset_index()
    )
    pair["pair_gate"] = (
        pair["robust_instances"].ge(2)
        | (pair["robust_instances"].ge(1) & pair["best_delta"].lt(-0.012) & pair["worst_min_mode_dominance"].ge(0.90))
    )
    pair = pair.sort_values(["pair_gate", "robust_instances", "strict_instances", "best_delta"], ascending=[False, False, False, True])
    return cand.sort_values(["robust_gate", "strict_gate", "delta_logloss"], ascending=[False, False, True]), pair, pd.DataFrame(null_results)


def write_report(cand: pd.DataFrame, pair: pd.DataFrame) -> None:
    if cand.empty:
        REPORT_OUT.write_text("# E296 Episode Target Strict Null Audit\n\nNo candidates selected from E295.\n", encoding="utf-8")
        return
    robust = cand[cand["robust_gate"].astype(bool)].copy()
    strict = cand[cand["strict_gate"].astype(bool)].copy()
    pair_gate = pair[pair["pair_gate"].astype(bool)].copy()
    target_read = (
        cand.groupby("target")
        .agg(
            candidates=("candidate_id", "count"),
            strict=("strict_gate", "sum"),
            robust=("robust_gate", "sum"),
            best_delta=("delta_logloss", "min"),
            mean_delta=("delta_logloss", "mean"),
        )
        .reset_index()
        .sort_values(["robust", "strict", "best_delta"], ascending=[False, False, True])
    )
    lines = [
        "# E296 Episode Target Strict Null Audit",
        "",
        "## Question",
        "",
        "Do the E295 human episode-target wins survive a stricter public-free matched-null audit?",
        "",
        "## Settings",
        "",
        f"- Null reps per mode: `{N_REPS}`",
        "- Modes: row, subject, dateblock",
        "- Selection: E295 multi-view/split consensus pairs plus large single-view all-null wins",
        "- Public LB: not used",
        "",
        "## Pair Gates",
        "",
        md_table(pair_gate, n=30),
        "",
        "## Top Candidate Instances",
        "",
        md_table(
            cand[
                [
                    "candidate_id",
                    "view_id",
                    "split",
                    "episode",
                    "target",
                    "delta_logloss",
                    "null_q01",
                    "null_q05",
                    "null_best",
                    "dominance",
                    "min_mode_dominance",
                    "p_value_lower",
                    "strict_gate",
                    "robust_gate",
                    "state_corr",
                ]
            ],
            n=50,
        ),
        "",
        "## Robust Instances",
        "",
        md_table(
            robust[
                [
                    "candidate_id",
                    "view_id",
                    "split",
                    "episode",
                    "target",
                    "delta_logloss",
                    "null_q01",
                    "null_q05",
                    "dominance",
                    "min_mode_dominance",
                    "p_value_lower",
                    "state_corr",
                ]
            ],
            n=50,
        ),
        "",
        "## Target Read",
        "",
        md_table(target_read, n=20),
        "",
        "## Decision",
        "",
    ]
    if len(pair_gate):
        lines.append(
            "Some E295 episode-target states survive strict local nulls. They are still not submissions; the next step is target-limited materialization with a current-best anchor and the same matched-null governor."
        )
    elif len(strict):
        lines.append(
            "Strict candidate instances survive, but no episode-target pair is robust enough across views/splits. Do not submit; use these as priors for the next materialization design."
        )
    else:
        lines.append("The E295 target wins were mostly light-null artifacts. Do not spend public LB on this branch yet.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{PAIR_OUT.name}`",
            f"- `{NULL_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    cand, pair, nulls = run()
    cand.to_csv(CANDIDATE_OUT, index=False)
    pair.to_csv(PAIR_OUT, index=False)
    nulls.to_csv(NULL_OUT, index=False)
    write_report(cand, pair)
    print(f"candidates={len(cand)}")
    print(f"strict_gates={int(cand['strict_gate'].sum()) if not cand.empty else 0}")
    print(f"robust_gates={int(cand['robust_gate'].sum()) if not cand.empty else 0}")
    print(f"pair_gates={int(pair['pair_gate'].sum()) if not pair.empty else 0}")
    if not cand.empty:
        best = cand.sort_values("delta_logloss").iloc[0]
        print(f"best={best['episode']}/{best['target']} delta={best['delta_logloss']:.9f}")
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
