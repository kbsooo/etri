#!/usr/bin/env python3
"""E301: strict public-free confirmation for the single E300 ready candidate.

E300 produced one public-free-ready S4 placement rescue. This script does not
search for new candidates. It asks one narrower benchmark question:

    Does the E300 candidate still beat matched row/subject/dateblock/sign nulls
    when the null budget and seed prefix are changed?

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
NULL_DIR = OUT / "e301_s4_ready_strict_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT, evaluate_models, score_candidates  # noqa: E402
from e300_s4_mean_dominance_rescue import as_bool, load_current_and_meta, md_table, rel, safe_id, short_hash, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, clip_prob, feature_row, load_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

PARENT = OUT / "submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv"
CANDIDATE = OUT / "submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv"

N_NULL_REPS = 64
MODES = ["row", "subject", "dateblock", "sign"]

GOVERNOR_OUT = OUT / "e301_s4_ready_strict_governor.csv"
NULL_MAP_OUT = OUT / "e301_s4_ready_strict_null_map.csv"
SCORE_OUT = OUT / "e301_s4_ready_strict_scores.csv"
ANATOMY_OUT = OUT / "e301_s4_ready_strict_anatomy.csv"
REMOVED_OUT = OUT / "e301_s4_ready_strict_removed_rows.csv"
REPORT_OUT = OUT / "e301_s4_ready_strict_report.md"


def write_submission_from_delta(current: pd.DataFrame, delta: np.ndarray, tag: str) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    NULL_DIR.mkdir(exist_ok=True)
    path = NULL_DIR / f"submission_e301null_{safe_id(tag, 108)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def candidate_delta(current: pd.DataFrame, path: Path) -> np.ndarray:
    cand = load_sub(path, current).sort_values(KEYS).reset_index(drop=True)
    return logit(cand[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))


def make_null_delta(delta: np.ndarray, meta: pd.DataFrame, mode: str, rep: int) -> np.ndarray:
    seed_text = f"{CANDIDATE.name}|{mode}|{rep}|e301strict"
    rng = np.random.default_rng(int(hashlib.sha1(seed_text.encode()).hexdigest()[:8], 16))
    values = np.asarray(delta, dtype=np.float64)
    shuffled = values.copy()

    if mode == "row":
        shuffled = values[rng.permutation(len(values)), :]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(idx, dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr, :] = values[idx_arr, :][rng.permutation(len(idx_arr)), :]
    elif mode == "sign":
        shuffled = values.copy()
        active = np.flatnonzero(np.max(np.abs(values), axis=1) > 1.0e-12)
        flips = rng.choice(np.array([-1.0, 1.0]), size=len(active))
        shuffled[active, :] = values[active, :] * flips[:, None]
    else:
        raise ValueError(mode)

    return shuffled


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for path in paths:
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = rel(path)
        row["source_path"] = rel(path)
        row["basename"] = path.name
        rows.append(row)
    return pd.DataFrame(rows)


def mode_dominance(actual: float, nulls: pd.DataFrame, metric: str) -> tuple[float, float]:
    vals = nulls[metric].to_numpy(dtype=np.float64)
    overall = float(np.mean(actual < vals)) if len(vals) else 0.0
    per_mode = []
    for _, part in nulls.groupby("mode"):
        pvals = part[metric].to_numpy(dtype=np.float64)
        per_mode.append(float(np.mean(actual < pvals)) if len(pvals) else 0.0)
    return overall, float(min(per_mode)) if per_mode else 0.0


def movement_anatomy(current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    parent_delta = candidate_delta(current, PARENT)
    cand_delta = candidate_delta(current, CANDIDATE)
    active_parent = np.max(np.abs(parent_delta), axis=1) > 1.0e-12
    active_cand = np.max(np.abs(cand_delta), axis=1) > 1.0e-12
    removed = np.flatnonzero(active_parent & ~active_cand)

    rows = []
    for idx in removed:
        rows.append(
            {
                "row_idx": int(idx),
                **meta.loc[idx, KEYS + ["dateblock_group"]].to_dict(),
                "parent_S4_logit_delta": float(parent_delta[idx, TARGETS.index("S4")]),
                "candidate_S4_logit_delta": float(cand_delta[idx, TARGETS.index("S4")]),
            }
        )
    removed_df = pd.DataFrame(rows)

    active = np.max(np.abs(cand_delta), axis=1) > 1.0e-12
    anatomy_rows = []
    for group_cols, group_name in [
        (["subject_id"], "subject"),
        (["dateblock_group"], "dateblock"),
        (["subject_id", "dateblock_group"], "subject_dateblock"),
    ]:
        part = meta.loc[active, group_cols].copy()
        part["S4_logit_delta"] = cand_delta[active, TARGETS.index("S4")]
        summary = (
            part.groupby(group_cols, dropna=False)["S4_logit_delta"]
            .agg(nonzero_rows="count", mean_delta="mean", pos_rows=lambda s: int((s > 0).sum()), neg_rows=lambda s: int((s < 0).sum()))
            .reset_index()
        )
        summary["summary_level"] = group_name
        anatomy_rows.append(summary)
    anatomy_df = pd.concat(anatomy_rows, ignore_index=True, sort=False)
    return removed_df, anatomy_df


def run() -> None:
    current, meta = load_current_and_meta()
    if not CANDIDATE.exists():
        raise FileNotFoundError(CANDIDATE)
    if not PARENT.exists():
        raise FileNotFoundError(PARENT)

    delta = candidate_delta(current, CANDIDATE)
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for mode in MODES:
        for rep in range(N_NULL_REPS):
            null_delta = make_null_delta(delta, meta, mode, rep)
            path = write_submission_from_delta(current, null_delta, f"{mode}_r{rep:03d}")
            null_paths.append(path)
            null_rows.append({"source_basename": CANDIDATE.name, "null_basename": path.name, "null_path": rel(path), "mode": mode, "rep": rep})

    null_map = pd.DataFrame(null_rows)
    sample = current[KEYS].copy()
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    features = feature_rows([OUT / CURRENT, CANDIDATE, *null_paths], sample, refs, ref_vecs)
    scores = score_candidates(known, features, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    actual = scores[scores["basename"].eq(CANDIDATE.name)].iloc[0]
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].merge(
        null_map[["null_basename", "mode", "rep"]],
        left_on="basename",
        right_on="null_basename",
        how="left",
    )
    actual_p90 = float(actual["pred_delta_vs_current_p90"])
    actual_mean = float(actual["pred_delta_vs_current_mean"])
    p90_dom, worst_p90_dom = mode_dominance(actual_p90, null_scores, "pred_delta_vs_current_p90")
    mean_dom, worst_mean_dom = mode_dominance(actual_mean, null_scores, "pred_delta_vs_current_mean")
    sign_part = null_scores[null_scores["mode"].eq("sign")]
    sign_p90_dom = float(np.mean(actual_p90 < sign_part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)))
    sign_mean_dom = float(np.mean(actual_mean < sign_part["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)))
    null_strict_rate = float(null_scores["strict_promote_gate"].map(as_bool).mean())
    null_strict_by_mode = null_scores.groupby("mode")["strict_promote_gate"].apply(lambda s: float(s.map(as_bool).mean())).to_dict()
    null_better_mean_rate = float(np.mean(null_scores["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64) < actual_mean))
    null_better_p90_rate = float(np.mean(null_scores["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64) < actual_p90))

    conservative_ready = bool(
        as_bool(actual["strict_promote_gate"])
        and null_strict_rate <= 0.10
        and p90_dom >= 0.80
        and mean_dom >= 0.70
        and worst_p90_dom >= 0.60
        and worst_mean_dom >= 0.50
        and sign_p90_dom >= 0.75
    )
    watchlist_ready = bool(
        as_bool(actual["strict_promote_gate"])
        and null_strict_rate <= 0.15
        and p90_dom >= 0.75
        and mean_dom >= 0.62
        and worst_p90_dom >= 0.50
        and worst_mean_dom >= 0.40
        and sign_p90_dom >= 0.65
    )
    governor = pd.DataFrame(
        [
            {
                "basename": CANDIDATE.name,
                "public_reference": "not_used",
                "actual_promotion_decision": actual["promotion_decision"],
                "actual_strict_promote": as_bool(actual["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(actual["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(actual["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(actual["incremental_bad_axis_vs_current"]),
                "null_count": int(len(null_scores)),
                "null_reps_per_mode": int(N_NULL_REPS),
                "null_strict_rate": null_strict_rate,
                "row_null_strict_rate": float(null_strict_by_mode.get("row", np.nan)),
                "subject_null_strict_rate": float(null_strict_by_mode.get("subject", np.nan)),
                "dateblock_null_strict_rate": float(null_strict_by_mode.get("dateblock", np.nan)),
                "sign_null_strict_rate": float(null_strict_by_mode.get("sign", np.nan)),
                "p90_dominance": p90_dom,
                "mean_dominance": mean_dom,
                "worst_mode_p90_dominance": worst_p90_dom,
                "worst_mode_mean_dominance": worst_mean_dom,
                "sign_p90_dominance": sign_p90_dom,
                "sign_mean_dominance": sign_mean_dom,
                "null_better_mean_rate": null_better_mean_rate,
                "null_better_p90_rate": null_better_p90_rate,
                "conservative_public_free_ready": conservative_ready,
                "watchlist_public_free_ready": watchlist_ready,
                "decision": "submit_candidate" if conservative_ready else ("local_watchlist_only" if watchlist_ready else "do_not_submit"),
            }
        ]
    )
    governor.to_csv(GOVERNOR_OUT, index=False)

    removed, anatomy = movement_anatomy(current, meta)
    removed.to_csv(REMOVED_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)

    selected = selected_model_summary(model_df)
    null_mode = (
        null_scores.groupby("mode")
        .agg(
            n=("basename", "count"),
            strict_rate=("strict_promote_gate", lambda s: float(s.map(as_bool).mean())),
            mean_median=("pred_delta_vs_current_mean", "median"),
            mean_p10=("pred_delta_vs_current_mean", lambda s: float(np.quantile(s, 0.10))),
            mean_p90=("pred_delta_vs_current_mean", lambda s: float(np.quantile(s, 0.90))),
            p90_median=("pred_delta_vs_current_p90", "median"),
            p90_p10=("pred_delta_vs_current_p90", lambda s: float(np.quantile(s, 0.10))),
            p90_p90=("pred_delta_vs_current_p90", lambda s: float(np.quantile(s, 0.90))),
        )
        .reset_index()
    )
    write_report(governor, null_mode, selected, removed, anatomy)
    print(f"wrote {rel(REPORT_OUT)}")
    print(governor.to_string(index=False))


def selected_model_summary(model_df: pd.DataFrame) -> pd.DataFrame:
    from e272_public_free_candidate_audit import selected_models

    selected = selected_models(model_df)
    return selected[
        [
            "model",
            "feature_set",
            "loo_sign_acc",
            "l2o_sign_acc",
            "model_score",
            "current_order_pass",
        ]
    ].copy()


def write_report(governor: pd.DataFrame, null_mode: pd.DataFrame, selected: pd.DataFrame, removed: pd.DataFrame, anatomy: pd.DataFrame) -> None:
    rec = governor.iloc[0]
    cols = [
        "basename",
        "actual_strict_promote",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "mean_dominance",
        "worst_mode_p90_dominance",
        "worst_mode_mean_dominance",
        "sign_p90_dominance",
        "conservative_public_free_ready",
        "watchlist_public_free_ready",
        "decision",
    ]
    anatomy_cols = ["summary_level", "subject_id", "dateblock_group", "nonzero_rows", "mean_delta", "pos_rows", "neg_rows"]
    lines = [
        "# E301 S4 Ready Strict Confirmation",
        "",
        "Public LB는 사용하지 않았다. E300의 단일 ready 후보만 대상으로 null budget과 seed prefix를 바꿔 재검증했다.",
        "",
        "## Promotion Rule",
        "",
        "- `conservative_public_free_ready`: strict gate 유지, 전체 null strict <= 0.10, p90 dominance >= 0.80, mean dominance >= 0.70, worst-mode p90 >= 0.60, worst-mode mean >= 0.50, sign p90 dominance >= 0.75.",
        "- `watchlist_public_free_ready`: 더 느슨한 정보 후보 기준이며 public 제출 기준이 아니다.",
        "",
        "## Governor",
        "",
        md_table(governor[cols], cols, n=5),
        "",
        "## Null Mode Distribution",
        "",
        md_table(null_mode, list(null_mode.columns), n=10),
        "",
        "## Removed Parent Rows",
        "",
        md_table(removed, list(removed.columns), n=20),
        "",
        "## Candidate Movement Anatomy",
        "",
        md_table(anatomy.sort_values(["summary_level", "nonzero_rows"], ascending=[True, False]), anatomy_cols, n=40),
        "",
        "## Selected Selector Models",
        "",
        md_table(selected, list(selected.columns), n=12),
        "",
        "## Decision",
        "",
    ]
    if bool(rec["conservative_public_free_ready"]):
        lines += [
            f"- `{CANDIDATE.name}` survives the stricter public-free governor.",
            "- It is a legitimate scarce-public candidate, but still bets on one narrow S4 hidden-block correction.",
        ]
    elif bool(rec["watchlist_public_free_ready"]):
        lines += [
            f"- `{CANDIDATE.name}` survives only the watchlist rule.",
            "- Do not spend a public LB slot yet; the signal is plausible but not strong enough under the stricter null budget.",
        ]
    else:
        lines += [
            f"- `{CANDIDATE.name}` does not survive strict confirmation.",
            "- Treat E300 as a useful anatomy discovery rather than a submission candidate.",
        ]
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{rel(GOVERNOR_OUT)}`",
        f"- `{rel(NULL_MAP_OUT)}`",
        f"- `{rel(SCORE_OUT)}`",
        f"- `{rel(ANATOMY_OUT)}`",
        f"- `{rel(REMOVED_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    run()
