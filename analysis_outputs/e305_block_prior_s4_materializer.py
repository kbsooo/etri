#!/usr/bin/env python3
"""E305: materialize the E304 block-state S4 prior.

E304 found two useful facts:

1. Family-JEPA diary block context predicts hidden block target residuals better
   than matched nulls under subject holdout.
2. The rejected E299-E303 S4 candidates are anti-aligned with that predicted S4
   block state; they place positive S4 movement on blocks predicted as S4-low.

This script turns that finding into a conservative candidate generator. It does
not use public LB. It creates S4-only edits from the E304 predicted block prior,
then applies the same current-anchor plus row/subject/dateblock/sign null
governor used after E301/E303.
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
NULL_DIR = OUT / "e305_block_prior_s4_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import CURRENT  # noqa: E402
from e300_s4_mean_dominance_rescue import as_bool, load_current_and_meta, rel, safe_id, short_hash, sigmoid  # noqa: E402
from e303_s4_mean_prior_materializer import score_paths  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, clip_prob, load_sub, logit  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

TEST_BLOCK_PRIOR = OUT / "e304_hidden_block_state_test_blocks.csv"
SOURCE_PARENT = OUT / "submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv"

S4_IDX = TARGETS.index("S4")
AMPS = [0.0125, 0.0250, 0.0388, 0.0520]
TOP_KS = [4, 6, 8, 10, 12, 16]
REDIST_COUNTS = [24, 32, 38, 47, 50]
REDIST_MULTS = [0.75, 1.00, 1.16]
MAX_NULL_EVAL = 18
N_REPS = 32

CANDIDATE_OUT = OUT / "e305_block_prior_s4_candidates.csv"
PREFILTER_OUT = OUT / "e305_block_prior_s4_prefilter.csv"
GOVERNOR_OUT = OUT / "e305_block_prior_s4_governor.csv"
NULL_MAP_OUT = OUT / "e305_block_prior_s4_null_map.csv"
SCORE_OUT = OUT / "e305_block_prior_s4_scores.csv"
SUMMARY_OUT = OUT / "e305_block_prior_s4_summary.csv"
REPORT_OUT = OUT / "e305_block_prior_s4_report.md"


def md(frame: pd.DataFrame, columns: list[str] | None = None, n: int = 25) -> str:
    if frame.empty:
        return "_empty_"
    view = frame if columns is None else frame.loc[:, [c for c in columns if c in frame.columns]]
    out = view.head(n).copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    out = out.fillna("").astype(str)
    header = "| " + " | ".join(out.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(out.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in out.to_numpy()]
    return "\n".join([header, sep, *rows])


def write_submission(current: pd.DataFrame, delta: np.ndarray, tag: str, null: bool = False) -> Path:
    out = current.copy()
    logits = logit(out[TARGETS].to_numpy(dtype=np.float64)) + np.asarray(delta, dtype=np.float64)
    out[TARGETS] = clip_prob(sigmoid(logits))
    base = NULL_DIR if null else OUT
    base.mkdir(exist_ok=True)
    prefix = "submission_e305null" if null else "submission_e305_blockprior_s4"
    path = base / f"{prefix}_{safe_id(tag, 104)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def source_s4_abs(current: pd.DataFrame) -> np.ndarray:
    source = load_sub(SOURCE_PARENT, current).sort_values(KEYS).reset_index(drop=True)
    delta = logit(source[TARGETS].to_numpy(dtype=np.float64)) - logit(current[TARGETS].to_numpy(dtype=np.float64))
    vals = np.abs(delta[:, S4_IDX])
    vals = vals[vals > 1.0e-12]
    return np.sort(vals)[::-1]


def build_candidates(current: pd.DataFrame, meta: pd.DataFrame, block_prior: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    prior = block_prior.set_index("dateblock_group")["pred_S4_logit_residual"].to_dict()
    block_score = meta["dateblock_group"].map(prior).fillna(0.0).to_numpy(dtype=np.float64)
    block_series = (
        meta[["dateblock_group"]]
        .assign(pred_S4=block_score)
        .drop_duplicates("dateblock_group")
        .sort_values("pred_S4", ascending=False)
    )
    top_order = block_series["dateblock_group"].tolist()
    bottom_order = block_series.sort_values("pred_S4")["dateblock_group"].tolist()
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}

    def add_delta(tag: str, delta_s4: np.ndarray, family: str) -> None:
        delta = np.zeros((len(current), len(TARGETS)), dtype=np.float64)
        delta[:, S4_IDX] = delta_s4
        if np.count_nonzero(np.abs(delta_s4) > 1.0e-12) < 2:
            return
        path = write_submission(current, delta, tag)
        deltas[path.name] = delta
        active = np.abs(delta_s4) > 1.0e-12
        rows.append(
            {
                "basename": path.name,
                "source_path": rel(path),
                "family": family,
                "tag": tag,
                "nonzero_rows": int(active.sum()),
                "pos_rows": int(np.sum(delta_s4 > 1.0e-12)),
                "neg_rows": int(np.sum(delta_s4 < -1.0e-12)),
                "mean_abs_s4_delta": float(np.mean(np.abs(delta_s4))),
                "max_abs_s4_delta": float(np.max(np.abs(delta_s4))),
                "active_pred_S4_mean": float(np.mean(block_score[active])) if active.any() else 0.0,
                "inactive_pred_S4_mean": float(np.mean(block_score[~active])) if (~active).any() else 0.0,
            }
        )

    for k in TOP_KS:
        top = set(top_order[:k])
        bottom = set(bottom_order[:k])
        top_mask = meta["dateblock_group"].isin(top).to_numpy()
        bottom_mask = meta["dateblock_group"].isin(bottom).to_numpy()
        for amp in AMPS:
            add_delta(f"top{k}_up_amp{amp:.4f}", np.where(top_mask, amp, 0.0), "top_up")
            add_delta(f"bottom{k}_down_amp{amp:.4f}", np.where(bottom_mask, -amp, 0.0), "bottom_down")
            add_delta(
                f"signed{k}_topup_bottomdown_amp{amp:.4f}",
                np.where(top_mask, amp, 0.0) + np.where(bottom_mask, -amp, 0.0),
                "signed_top_bottom",
            )
            add_delta(f"control_top{k}_down_amp{amp:.4f}", np.where(top_mask, -amp, 0.0), "control_wrong_sign")

    source_abs = source_s4_abs(current)
    row_order = np.argsort(-block_score)
    for count in REDIST_COUNTS:
        slots = row_order[: min(count, len(row_order))]
        values = source_abs[: min(count, len(source_abs), len(slots))]
        for mult in REDIST_MULTS:
            delta_s4 = np.zeros(len(current), dtype=np.float64)
            delta_s4[slots[: len(values)]] = values * mult
            add_delta(f"redistribute_toprows_n{count}_m{mult:.2f}", delta_s4, "redistribute_toprows")
    frame = pd.DataFrame(rows)
    frame["active_minus_inactive_pred_S4"] = frame["active_pred_S4_mean"] - frame["inactive_pred_S4_mean"]
    frame.to_csv(CANDIDATE_OUT, index=False)
    return frame, deltas


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    strict = prefilter[prefilter["strict_promote_gate"].map(as_bool)].copy()
    pool = strict if not strict.empty else prefilter.copy()
    pool["selection_score"] = (
        pool["pred_delta_vs_current_p90"].fillna(0.0)
        + 0.40 * pool["pred_delta_vs_current_mean"].fillna(0.0)
        - 0.00002 * pool["active_minus_inactive_pred_S4"].fillna(0.0)
    )
    picks = [
        pool.sort_values(["selection_score"]).head(MAX_NULL_EVAL),
        pool.sort_values(["active_minus_inactive_pred_S4"], ascending=False).head(MAX_NULL_EVAL // 3 + 1),
        pool.sort_values(["pred_delta_vs_current_p90"]).head(MAX_NULL_EVAL // 3 + 1),
    ]
    return pd.concat(picks, ignore_index=True).drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def write_null_candidate(current: pd.DataFrame, delta: np.ndarray, basename: str, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    rng = np.random.default_rng(int(hashlib.sha1(f"{basename}|{mode}|{rep}|e305".encode()).hexdigest()[:8], 16))
    values = np.asarray(delta, dtype=np.float64)
    shuffled = values.copy()
    if mode == "row":
        shuffled = values[rng.permutation(len(values)), :]
    elif mode in {"subject", "dateblock"}:
        group_col = "subject_id" if mode == "subject" else "dateblock_group"
        for _, idx in meta.groupby(group_col).indices.items():
            idx_arr = np.asarray(list(idx), dtype=int)
            if len(idx_arr) > 1:
                shuffled[idx_arr, :] = values[idx_arr, :][rng.permutation(len(idx_arr)), :]
    elif mode == "sign":
        active = np.flatnonzero(np.max(np.abs(values), axis=1) > 1.0e-12)
        flips = rng.choice(np.array([-1.0, 1.0]), size=len(active))
        shuffled[active, :] = values[active, :] * flips[:, None]
    else:
        raise ValueError(mode)
    return write_submission(current, shuffled, f"{Path(basename).stem}_{mode}_r{rep:02d}", null=True)


def run_governor(selected: pd.DataFrame, deltas: dict[str, np.ndarray], current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    null_rows: list[dict[str, Any]] = []
    null_paths: list[Path] = []
    for _, row in selected.iterrows():
        basename = str(row["basename"])
        delta = deltas[basename]
        for mode in ["row", "subject", "dateblock", "sign"]:
            for rep in range(N_REPS):
                path = write_null_candidate(current, delta, basename, meta, mode, rep)
                null_paths.append(path)
                null_rows.append({"source_basename": basename, "null_basename": path.name, "null_path": rel(path), "mode": mode, "rep": rep})
    null_map = pd.DataFrame(null_rows)
    null_map.to_csv(NULL_MAP_OUT, index=False)

    paths = [OUT / str(b) for b in selected["basename"]]
    scores = score_paths([*paths, *null_paths], current)
    scores.to_csv(SCORE_OUT, index=False)
    cand_scores = scores[scores["basename"].isin(selected["basename"])].copy()
    null_scores = scores[scores["basename"].isin(null_map["null_basename"])].copy()

    rows: list[dict[str, Any]] = []
    for _, cand in selected.iterrows():
        basename = str(cand["basename"])
        actual = cand_scores[cand_scores["basename"].eq(basename)]
        if actual.empty:
            continue
        a = actual.iloc[0]
        null_names = null_map.loc[null_map["source_basename"].eq(basename), "null_basename"].tolist()
        these = null_scores[null_scores["basename"].isin(null_names)].merge(
            null_map[["null_basename", "mode"]],
            left_on="basename",
            right_on="null_basename",
            how="left",
        )
        actual_p90 = float(a["pred_delta_vs_current_p90"])
        actual_mean = float(a["pred_delta_vs_current_mean"])
        p90_vals = these["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
        mean_vals = these["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
        null_strict = float(these["strict_promote_gate"].map(as_bool).mean()) if len(these) else 1.0
        p90_dom = float(np.mean(actual_p90 < p90_vals)) if len(p90_vals) else 0.0
        mean_dom = float(np.mean(actual_mean < mean_vals)) if len(mean_vals) else 0.0
        mode_p90 = []
        mode_mean = []
        mode_strict: dict[str, float] = {}
        for mode, part in these.groupby("mode"):
            mode_p90.append(float(np.mean(actual_p90 < part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64))))
            mode_mean.append(float(np.mean(actual_mean < part["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64))))
            mode_strict[f"{mode}_null_strict_rate"] = float(part["strict_promote_gate"].map(as_bool).mean())
        worst_p90 = float(min(mode_p90)) if mode_p90 else 0.0
        worst_mean = float(min(mode_mean)) if mode_mean else 0.0
        sign_part = these[these["mode"].eq("sign")]
        sign_p90 = float(np.mean(actual_p90 < sign_part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64))) if len(sign_part) else 0.0
        ready = bool(
            as_bool(a["strict_promote_gate"])
            and null_strict <= 0.10
            and p90_dom >= 0.80
            and mean_dom >= 0.70
            and worst_p90 >= 0.60
            and worst_mean >= 0.50
            and sign_p90 >= 0.75
        )
        rows.append(
            {
                **cand.to_dict(),
                "actual_strict_promote": as_bool(a["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(a["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(a["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(a["incremental_bad_axis_vs_current"]),
                "null_count": int(len(these)),
                "null_strict_rate": null_strict,
                "p90_dominance": p90_dom,
                "mean_dominance": mean_dom,
                "worst_mode_p90_dominance": worst_p90,
                "worst_mode_mean_dominance": worst_mean,
                "sign_p90_dominance": sign_p90,
                "public_free_ready": ready,
                "decision": "candidate_ready_needs_64rep_confirm" if ready else "do_not_submit",
                **mode_strict,
            }
        )
    governor = pd.DataFrame(rows).sort_values(
        ["public_free_ready", "null_strict_rate", "mean_dominance", "actual_p90"],
        ascending=[False, True, False, True],
    ).reset_index(drop=True)
    governor.to_csv(GOVERNOR_OUT, index=False)
    return null_map, governor


def write_report(candidates: pd.DataFrame, prefilter: pd.DataFrame, selected: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_ready"].map(as_bool)] if not governor.empty else pd.DataFrame()
    summary = pd.DataFrame(
        [
            {
                "generated_candidates": len(candidates),
                "old_strict": int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0,
                "null_evaluated": len(selected),
                "ready_32rep": len(ready),
                "best_null_strict_rate": float(governor["null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_mean_dominance": float(governor["mean_dominance"].max()) if not governor.empty else np.nan,
                "best_actual_p90": float(governor["actual_p90"].min()) if not governor.empty else np.nan,
            }
        ]
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    lines = [
        "# E305 Block-Prior S4 Materializer",
        "",
        "Public LB는 사용하지 않았다. E304가 복원한 hidden S4 block prior를 S4-only probability edit으로 바꾸고 matched-null governor로 검증했다.",
        "",
        "## Summary",
        "",
        md(summary),
        "",
        "## Best Prefilter Rows",
        "",
        md(
            prefilter,
            [
                "basename",
                "family",
                "nonzero_rows",
                "active_minus_inactive_pred_S4",
                "pred_delta_vs_current_mean",
                "pred_delta_vs_current_p90",
                "strict_promote_gate",
                "pred_beats_current_rate",
            ],
            n=25,
        ),
        "",
        "## Governor Rows",
        "",
        md(
            governor,
            [
                "basename",
                "family",
                "nonzero_rows",
                "actual_mean",
                "actual_p90",
                "null_strict_rate",
                "p90_dominance",
                "mean_dominance",
                "worst_mode_p90_dominance",
                "worst_mode_mean_dominance",
                "public_free_ready",
                "decision",
            ],
            n=30,
        ),
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        lines.append("- A 32-rep public-free candidate exists, but it needs 64-rep independent confirmation before any public LB use.")
    else:
        lines.extend(
            [
                "- No E305 candidate survives the local governor.",
                "- E304's block prior is a strong diagnostic, but the simple S4 materializer is not yet a submission path.",
            ]
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(PREFILTER_OUT)}`",
            f"- `{rel(GOVERNOR_OUT)}`",
            f"- `{rel(SUMMARY_OUT)}`",
            f"- `{rel(REPORT_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    current, meta = load_current_and_meta()
    block_prior = pd.read_csv(TEST_BLOCK_PRIOR)
    candidates, deltas = build_candidates(current, meta, block_prior)
    scored = score_paths([OUT / b for b in candidates["basename"]], current)
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
    prefilter = candidates.merge(scored[score_cols], on="basename", how="left")
    prefilter = prefilter.sort_values(
        ["strict_promote_gate", "pred_delta_vs_current_p90", "active_minus_inactive_pred_S4"],
        ascending=[False, True, False],
    ).reset_index(drop=True)
    prefilter.to_csv(PREFILTER_OUT, index=False)
    selected = select_for_null(prefilter)
    _null_map, governor = run_governor(selected, deltas, current, meta)
    write_report(candidates, prefilter, selected, governor)
    ready = int(governor["public_free_ready"].map(as_bool).sum()) if not governor.empty else 0
    print(f"generated={len(candidates)} old_strict={int(prefilter['strict_promote_gate'].map(as_bool).sum())} null_eval={len(selected)} ready={ready}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
