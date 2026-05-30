#!/usr/bin/env python3
"""E309: human episode -> target-pair interaction probe.

E297 showed that strict human episode states can help individual train targets,
but direct single-target materialization becomes null-common on the current
submission tensor. This probe asks a different question:

    Are these human states really acting on target *interactions*?

For example, bedtime arousal may not be "S1 up" or "S3 down" alone. It may
change the S1/S3 joint pattern. We evaluate episode-state context against every
target pair using grouped OOF multiclass logloss and matched row/subject/
dateblock nulls. No public LB is used and no submission is created.
"""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
import sys
from typing import Any
import warnings

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    TARGETS,
    base_label_matrix,
    build_context_views,
    clip_prob,
    folds_for,
    groups_for,
    load_frames,
    md_table,
    oof_multi_ridge,
    stable_seed,
)
from e295_episode_state_jepa_audit import (  # noqa: E402
    EPISODE_SPECS,
    build_episode_matrix,
    shuffle_episode,
)


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

STRICT_REPS = 12
MAX_STRICT = 32

SCAN_OUT = OUT / "e309_episode_target_interaction_scan.csv"
STRICT_OUT = OUT / "e309_episode_target_interaction_strict.csv"
NULL_OUT = OUT / "e309_episode_target_interaction_nulls.csv"
PAIR_OUT = OUT / "e309_episode_target_interaction_pair_summary.csv"
REPORT_OUT = OUT / "e309_episode_target_interaction_report.md"
E296_PAIR_OUT = OUT / "e296_episode_target_pair_summary.csv"


PAIR_STORIES = {
    "QQ": "subjective report consistency",
    "QS": "subjective-objective sleep translation",
    "SS": "objective sleep-stage composition",
}


def pair_family(a: str, b: str) -> str:
    if a.startswith("Q") and b.startswith("Q"):
        return "QQ"
    if a.startswith("S") and b.startswith("S"):
        return "SS"
    return "QS"


def joint_code(df: pd.DataFrame, a: str, b: str) -> np.ndarray:
    return (df[a].to_numpy(dtype=int) * 2 + df[b].to_numpy(dtype=int)).astype(int)


def multiclass_cv_loss(x: pd.DataFrame, y: np.ndarray, groups: pd.Series) -> float:
    pred = np.zeros((len(y), 4), dtype=np.float64)
    for tr_idx, va_idx in folds_for(groups):
        y_tr = y[tr_idx]
        counts = np.bincount(y_tr, minlength=4).astype(np.float64) + 1.0
        prior = counts / counts.sum()
        if len(np.unique(y_tr)) < 2:
            pred[va_idx] = prior
            continue
        model = make_pipeline(
            SimpleImputer(strategy="median"),
            StandardScaler(),
            LogisticRegression(C=0.30, max_iter=1500, solver="lbfgs"),
        )
        model.fit(x.iloc[tr_idx], y_tr)
        fold_pred = np.zeros((len(va_idx), 4), dtype=np.float64)
        fold_pred[:] = prior * 0.02
        classes = model.named_steps["logisticregression"].classes_.astype(int)
        fold_pred[:, classes] += 0.98 * model.predict_proba(x.iloc[va_idx])
        pred[va_idx] = fold_pred / fold_pred.sum(axis=1, keepdims=True)
    return float(log_loss(y, clip_prob(pred), labels=[0, 1, 2, 3]))


def episode_story(episode: str) -> str:
    spec = EPISODE_SPECS.get(episode, {})
    return str(spec.get("human_story", episode))


def interaction_story(episode: str, pair: str) -> str:
    a, b = pair.split("_")
    fam = pair_family(a, b)
    base = PAIR_STORIES[fam]
    if episode == "bedtime_arousal" and fam == "SS":
        return "late screen/message arousal changing sleep-stage composition"
    if episode == "routine_fragmentation" and fam in {"SS", "QS"}:
        return "scattered routine changing stage stability and subjective-objective alignment"
    if episode == "routine_anchor_recovery":
        return "stable bedtime/home routine restoring stage and quality consistency"
    if episode == "cashflow_stress":
        return "money rumination affecting subjective satisfaction and stage stress"
    if episode == "social_overload":
        return "late social load changing objective-stage and subjective quality translation"
    if episode == "home_recovery":
        return "home recovery linking physiological calm with sleep-stage consistency"
    if episode == "badnight_aftereffect":
        return "previous bad night carrying into next-day subjective/objective mismatch"
    return f"{episode_story(episode)} -> {base}"


def candidate_pairs_by_episode() -> dict[str, list[tuple[str, str]]]:
    all_pairs = list(combinations(TARGETS, 2))
    if not E296_PAIR_OUT.exists():
        return {episode: all_pairs for episode in EPISODE_SPECS}
    e296 = pd.read_csv(E296_PAIR_OUT)
    supports: dict[str, set[str]] = {}
    for _, row in e296.iterrows():
        keep = bool(row.get("pair_gate", False)) or int(row.get("strict_instances", 0)) > 0 or float(row.get("best_delta", 0.0)) < -0.006
        if keep:
            supports.setdefault(str(row["episode"]), set()).add(str(row["target"]))
    out: dict[str, list[tuple[str, str]]] = {}
    for episode, targets in supports.items():
        pairs = set()
        for target in targets:
            for other in TARGETS:
                if other == target:
                    continue
                pairs.add(tuple(sorted((target, other), key=TARGETS.index)))
        # If two or more targets already survived for an episode, make their
        # direct interaction mandatory and rank it first.
        for a, b in combinations(sorted(targets, key=TARGETS.index), 2):
            pairs.add((a, b))
        out[episode] = sorted(pairs, key=lambda p: (0 if set(p).issubset(targets) else 1, TARGETS.index(p[0]), TARGETS.index(p[1])))
    return out


def mode_groups(train_df: pd.DataFrame, eval_split: str) -> dict[str, pd.Series]:
    return {
        "row": groups_for(train_df, eval_split).reset_index(drop=True),
        "subject": groups_for(train_df, "subject5").reset_index(drop=True),
        "dateblock": groups_for(train_df, "dateblock5").reset_index(drop=True),
    }


def evaluate_state_pair(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    groups: pd.Series,
    state: pd.Series,
    pair: tuple[str, str],
) -> tuple[float, float]:
    a, b = pair
    y = joint_code(train_df, a, b)
    base_loss = multiclass_cv_loss(base_x, y, groups)
    x = pd.concat([base_x.reset_index(drop=True), state.reset_index(drop=True).rename("episode_state")], axis=1)
    state_loss = multiclass_cv_loss(x, y, groups)
    return base_loss, state_loss


def evaluate_state_pair_with_base(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    groups: pd.Series,
    state: pd.Series,
    pair: tuple[str, str],
    base_loss: float,
) -> float:
    a, b = pair
    y = joint_code(train_df, a, b)
    x = pd.concat([base_x.reset_index(drop=True), state.reset_index(drop=True).rename("episode_state")], axis=1)
    return multiclass_cv_loss(x, y, groups)


def null_deltas(
    train_df: pd.DataFrame,
    base_x: pd.DataFrame,
    groups: pd.Series,
    state: pd.Series,
    pair: tuple[str, str],
    eval_split: str,
    reps: int,
    actual_delta: float,
    seed_parts: tuple[object, ...],
) -> tuple[list[dict[str, Any]], np.ndarray, dict[str, float]]:
    a, b = pair
    y = joint_code(train_df, a, b)
    base_loss = multiclass_cv_loss(base_x, y, groups)
    rng = np.random.default_rng(stable_seed("e309", *seed_parts, reps))
    rows: list[dict[str, Any]] = []
    vals_by_mode: dict[str, list[float]] = {"row": [], "subject": [], "dateblock": []}
    for mode, mgroups in mode_groups(train_df, eval_split).items():
        for rep in range(reps):
            shuffled = shuffle_episode(state.to_numpy().reshape(-1, 1), mode, train_df, rng).ravel()
            nx = pd.concat(
                [base_x.reset_index(drop=True), pd.Series(shuffled, name="episode_state").reset_index(drop=True)],
                axis=1,
            )
            delta = multiclass_cv_loss(nx, y, groups) - base_loss
            vals_by_mode[mode].append(delta)
            rows.append(
                {
                    "mode": mode,
                    "rep": rep,
                    "null_delta": delta,
                }
            )
    vals = np.asarray(sum(vals_by_mode.values(), []), dtype=np.float64)
    dom = {f"{mode}_dominance": float(np.mean(actual_delta < np.asarray(v))) for mode, v in vals_by_mode.items()}
    return rows, vals, dom


def scan() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base, raw, _, feature_frames = load_frames()
    story_state, _definitions = build_episode_matrix(base, feature_frames)
    contexts = build_context_views(base, raw)
    train_mask = base["split"].eq("train").to_numpy()
    train_df = base.loc[train_mask].reset_index(drop=True)
    y_episode = story_state.loc[train_mask].reset_index(drop=True)
    base_x = base_label_matrix(train_df)
    pairs_by_episode = candidate_pairs_by_episode()

    rows: list[dict[str, Any]] = []
    state_cache: dict[tuple[str, str], pd.DataFrame] = {}
    state_diag: dict[tuple[str, str, str], dict[str, float]] = {}
    baseline_cache: dict[tuple[str, tuple[str, str]], float] = {}

    for view_id, ctx in contexts.items():
        for split_name in ["subject5", "dateblock5"]:
            x_train = ctx.loc[train_mask].reset_index(drop=True)
            groups = groups_for(train_df, split_name).reset_index(drop=True)
            pred_train = oof_multi_ridge(x_train, y_episode, groups)
            pred_state = pd.DataFrame(pred_train, columns=y_episode.columns)
            state_cache[(view_id, split_name)] = pred_state
            for episode in pred_state.columns:
                actual = y_episode[episode].to_numpy(dtype=np.float64)
                pred = pred_state[episode].to_numpy(dtype=np.float64)
                state_diag[(view_id, split_name, episode)] = {
                    "state_r2": float(r2_score(actual, pred)),
                    "state_corr": float(np.corrcoef(actual, pred)[0, 1]) if np.std(pred) > 1.0e-12 else 0.0,
                }

            for episode in pred_state.columns:
                target_pairs = pairs_by_episode.get(episode, [])
                if not target_pairs:
                    continue
                state = pred_state[episode]
                for pair in target_pairs:
                    base_key = (split_name, pair)
                    if base_key not in baseline_cache:
                        baseline_cache[base_key] = multiclass_cv_loss(base_x, joint_code(train_df, *pair), groups)
                    base_loss = baseline_cache[base_key]
                    state_loss = evaluate_state_pair_with_base(train_df, base_x, groups, state, pair, base_loss)
                    actual_delta = state_loss - base_loss
                    rows.append(
                        {
                            "view_id": view_id,
                            "split": split_name,
                            "episode": episode,
                            "pair": f"{pair[0]}_{pair[1]}",
                            "pair_family": pair_family(*pair),
                            "interaction_story": interaction_story(episode, f"{pair[0]}_{pair[1]}"),
                            "base_loss": base_loss,
                            "state_loss": state_loss,
                            "delta_logloss": actual_delta,
                            "null_q05": np.nan,
                            "null_q20": np.nan,
                            "null_median": np.nan,
                            "null_best": np.nan,
                            "dominance": np.nan,
                            "min_mode_dominance": np.nan,
                            "quick_gate": bool(actual_delta < -0.006),
                            "row_dominance": np.nan,
                            "subject_dominance": np.nan,
                            "dateblock_dominance": np.nan,
                            **state_diag[(view_id, split_name, episode)],
                        }
                    )

    scan_df = pd.DataFrame(rows).sort_values(["quick_gate", "delta_logloss"], ascending=[False, True]).reset_index(drop=True)
    strict_sources = scan_df[
        scan_df["quick_gate"].astype(bool)
        | (scan_df["delta_logloss"] < -0.010)
    ].head(MAX_STRICT)
    if strict_sources.empty:
        strict_sources = scan_df.head(min(MAX_STRICT, len(scan_df))).copy()

    strict_rows: list[dict[str, Any]] = []
    null_detail: list[dict[str, Any]] = []
    for _, src in strict_sources.iterrows():
        view_id = str(src["view_id"])
        split_name = str(src["split"])
        episode = str(src["episode"])
        a, b = str(src["pair"]).split("_")
        pair = (a, b)
        groups = groups_for(train_df, split_name).reset_index(drop=True)
        state = state_cache[(view_id, split_name)][episode]
        base_loss, state_loss = evaluate_state_pair(train_df, base_x, groups, state, pair)
        actual_delta = state_loss - base_loss
        null_rows, null_vals, dom = null_deltas(
            train_df,
            base_x,
            groups,
            state,
            pair,
            split_name,
            STRICT_REPS,
            actual_delta,
            (view_id, split_name, episode, a, b, "strict"),
        )
        for nr in null_rows:
            nr.update(
                {
                    "view_id": view_id,
                    "split": split_name,
                    "episode": episode,
                    "pair": f"{a}_{b}",
                }
            )
            null_detail.append(nr)
        mode_min = min(dom.values()) if dom else 0.0
        strict_rows.append(
            {
                **src.to_dict(),
                "base_loss": base_loss,
                "state_loss": state_loss,
                "delta_logloss": actual_delta,
                "strict_null_q01": float(np.quantile(null_vals, 0.01)),
                "strict_null_q05": float(np.quantile(null_vals, 0.05)),
                "strict_null_q20": float(np.quantile(null_vals, 0.20)),
                "strict_null_median": float(np.median(null_vals)),
                "strict_null_best": float(np.min(null_vals)),
                "strict_dominance": float(np.mean(actual_delta < null_vals)),
                "strict_min_mode_dominance": mode_min,
                "p_value_lower": float((1.0 + np.sum(null_vals <= actual_delta)) / (1.0 + len(null_vals))),
                "margin_to_null_q05": float(np.quantile(null_vals, 0.05) - actual_delta),
                "strict_gate": bool(
                    actual_delta < -0.006
                    and np.mean(actual_delta < null_vals) >= 0.95
                    and mode_min >= 0.80
                    and actual_delta < np.quantile(null_vals, 0.05)
                ),
                "robust_gate": bool(
                    actual_delta < -0.010
                    and np.mean(actual_delta < null_vals) >= 0.99
                    and mode_min >= 0.90
                    and actual_delta < np.quantile(null_vals, 0.01)
                ),
                **dom,
            }
        )

    strict_df = pd.DataFrame(strict_rows).sort_values(["robust_gate", "strict_gate", "delta_logloss"], ascending=[False, False, True])
    pair_summary = (
        strict_df.groupby(["episode", "pair", "pair_family", "interaction_story"], dropna=False)
        .agg(
            instances=("pair", "count"),
            strict_instances=("strict_gate", "sum"),
            robust_instances=("robust_gate", "sum"),
            best_delta=("delta_logloss", "min"),
            mean_delta=("delta_logloss", "mean"),
            best_p_value=("p_value_lower", "min"),
            worst_mode_dom=("strict_min_mode_dominance", "min"),
            mean_margin_q05=("margin_to_null_q05", "mean"),
            best_state_corr=("state_corr", "max"),
        )
        .reset_index()
        .sort_values(["robust_instances", "strict_instances", "best_delta"], ascending=[False, False, True])
    )
    pair_summary["pair_gate"] = (
        pair_summary["robust_instances"].ge(1)
        | (pair_summary["strict_instances"].ge(2) & pair_summary["best_delta"].lt(-0.008) & pair_summary["worst_mode_dom"].ge(0.80))
    )
    return scan_df, strict_df, pd.DataFrame(null_detail), pair_summary


def write_report(scan_df: pd.DataFrame, strict_df: pd.DataFrame, pair_summary: pd.DataFrame) -> None:
    pair_gates = pair_summary[pair_summary["pair_gate"].astype(bool)].copy() if not pair_summary.empty else pair_summary
    strict_gates = strict_df[strict_df["strict_gate"].astype(bool)].copy() if not strict_df.empty else strict_df
    robust_gates = strict_df[strict_df["robust_gate"].astype(bool)].copy() if not strict_df.empty else strict_df
    family = (
        strict_df.groupby("pair_family")
        .agg(
            rows=("pair", "count"),
            strict=("strict_gate", "sum"),
            robust=("robust_gate", "sum"),
            best_delta=("delta_logloss", "min"),
            mean_delta=("delta_logloss", "mean"),
        )
        .reset_index()
        .sort_values(["robust", "strict", "best_delta"], ascending=[False, False, True])
        if not strict_df.empty
        else pd.DataFrame()
    )
    lines = [
        "# E309 Episode Target-Interaction Probe",
        "",
        "Public LB는 사용하지 않았다. E297의 단일 target materialization 실패를 반대로 해석해, 인간 episode state가 target pair의 joint pattern을 설명하는지 검증했다.",
        "",
        "## Settings",
        "",
        "- quick scan: all episode/pair actual deltas only; no nulls",
        f"- strict null reps per mode: `{STRICT_REPS}`",
        "- null modes: row, subject, dateblock",
        "- target object: 4-class joint label for each target pair",
        "",
        "## Counts",
        "",
        f"- quick scanned rows: `{len(scan_df)}`",
        f"- strict rerun rows: `{len(strict_df)}`",
        f"- strict gates: `{int(strict_df['strict_gate'].sum()) if not strict_df.empty else 0}`",
        f"- robust gates: `{int(strict_df['robust_gate'].sum()) if not strict_df.empty else 0}`",
        f"- pair gates: `{int(pair_summary['pair_gate'].sum()) if not pair_summary.empty else 0}`",
        "",
        "## Pair-Family Read",
        "",
        md_table(family, n=10),
        "",
        "## Strong Pair Gates",
        "",
        md_table(
            pair_gates[
                [
                    "episode",
                    "pair",
                    "pair_family",
                    "instances",
                    "strict_instances",
                    "robust_instances",
                    "best_delta",
                    "best_p_value",
                    "worst_mode_dom",
                    "best_state_corr",
                    "interaction_story",
                ]
            ]
            if not pair_gates.empty
            else pair_gates,
            n=30,
        ),
        "",
        "## Strongest Strict Rows",
        "",
        md_table(
            strict_df[
                [
                    "view_id",
                    "split",
                    "episode",
                    "pair",
                    "pair_family",
                    "delta_logloss",
                    "strict_null_q05",
                    "strict_dominance",
                    "strict_min_mode_dominance",
                    "p_value_lower",
                    "margin_to_null_q05",
                    "strict_gate",
                    "robust_gate",
                    "state_corr",
                    "interaction_story",
                ]
            ]
            if not strict_df.empty
            else strict_df,
            n=35,
        ),
        "",
        "## Decision",
        "",
    ]
    if not pair_gates.empty:
        lines.extend(
            [
                "- Human episode state does survive as a target-interaction representation.",
                "- This does not justify public submission yet. E297 already showed that single-target transfer collapses into null-common current-tensor movement.",
                "- Next experiment should materialize only the gated pair interaction: coupled target deltas with wrong-pair and shuffled-state controls, then E308-style governor.",
            ]
        )
    else:
        lines.extend(
            [
                "- No target-pair interaction survived enough strict null stress to justify materialization.",
                "- This weakens the hypothesis that E297 failed only because single-target translation missed pair dependency.",
                "- Next high-value path should be learned action-health labels or a different hidden block target, not pair dependency materialization.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{SCAN_OUT.relative_to(ROOT)}`",
            f"- `{STRICT_OUT.relative_to(ROOT)}`",
            f"- `{PAIR_OUT.relative_to(ROOT)}`",
            f"- `{NULL_OUT.relative_to(ROOT)}`",
            f"- `{REPORT_OUT.relative_to(ROOT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    scan_df, strict_df, null_df, pair_summary = scan()
    scan_df.to_csv(SCAN_OUT, index=False)
    strict_df.to_csv(STRICT_OUT, index=False)
    null_df.to_csv(NULL_OUT, index=False)
    pair_summary.to_csv(PAIR_OUT, index=False)
    write_report(scan_df, strict_df, pair_summary)
    print(
        "quick_rows={} strict_rows={} strict_gates={} robust_gates={} pair_gates={}".format(
            len(scan_df),
            len(strict_df),
            int(strict_df["strict_gate"].sum()) if not strict_df.empty else 0,
            int(strict_df["robust_gate"].sum()) if not strict_df.empty else 0,
            int(pair_summary["pair_gate"].sum()) if not pair_summary.empty else 0,
        )
    )
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
