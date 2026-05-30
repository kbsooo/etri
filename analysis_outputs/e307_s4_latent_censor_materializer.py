#!/usr/bin/env python3
"""E307: S4 latent-state censor/materializer.

E304 and E306 say the S4 hidden state is visible at block and row level, but
directly adding positive S4 mass is null-common. This script flips the action:
instead of asking where to raise S4, ask where the current S4 probability is
overconfident relative to the recovered latent state.

Actions tested:
- temper current S4 logits toward 0.5 on latent/current disagreement rows;
- decrease S4 where current S4 is high but latent state is low;
- bidirectionally correct current S4 toward the latent state;
- include wrong-direction controls.

No public LB is used. Candidates must survive row/subject/dateblock/sign nulls.
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
NULL_DIR = OUT / "e307_s4_latent_censor_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e300_s4_mean_dominance_rescue import as_bool, load_current_and_meta, rel, safe_id, short_hash, sigmoid  # noqa: E402
from e303_s4_mean_prior_materializer import score_paths  # noqa: E402
from e289_target_specific_lifestyle_slice_audit import normalize_keys  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, clip_prob, logit  # noqa: E402


warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

RNG_SEED = 20260531 + 307
S4_IDX = TARGETS.index("S4")
N_REPS = 32
MAX_NULL_EVAL = 22

TEST_ROWS = OUT / "e306_within_block_s4_test_rows.csv"

CANDIDATE_OUT = OUT / "e307_s4_latent_censor_candidates.csv"
PREFILTER_OUT = OUT / "e307_s4_latent_censor_prefilter.csv"
GOVERNOR_OUT = OUT / "e307_s4_latent_censor_governor.csv"
NULL_MAP_OUT = OUT / "e307_s4_latent_censor_null_map.csv"
SCORE_OUT = OUT / "e307_s4_latent_censor_scores.csv"
SUMMARY_OUT = OUT / "e307_s4_latent_censor_summary.csv"
REPORT_OUT = OUT / "e307_s4_latent_censor_report.md"


def zscore(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    std = float(np.nanstd(arr))
    if not np.isfinite(std) or std < 1.0e-12:
        return np.zeros_like(arr)
    return (arr - float(np.nanmean(arr))) / std


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
    prefix = "submission_e307null" if null else "submission_e307_s4latentcensor"
    path = base / f"{prefix}_{safe_id(tag, 104)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def align_state(current: pd.DataFrame) -> pd.DataFrame:
    rows = pd.read_csv(TEST_ROWS)
    left = normalize_keys(current[KEYS])
    right_keys = normalize_keys(rows[KEYS])
    right = pd.concat([right_keys, rows.drop(columns=KEYS)], axis=1)
    aligned = left.merge(right, on=KEYS, how="left", validate="one_to_one")
    if aligned["dateblock_group"].isna().any():
        raise RuntimeError("Could not align E306 latent row state to current")
    current_s4 = current["S4"].to_numpy(dtype=np.float64)
    current_logit = logit(current_s4)
    block_z = zscore(aligned["block_pred_S4"].to_numpy(dtype=np.float64))
    row_z = zscore(aligned["row_s4_centered"].to_numpy(dtype=np.float64))
    rank_z = zscore(aligned["row_s4_rank_centered"].to_numpy(dtype=np.float64))
    latent_z = zscore(0.60 * block_z + 0.30 * row_z + 0.10 * rank_z)
    current_z = zscore(current_logit)
    aligned["current_S4"] = current_s4
    aligned["current_S4_logit"] = current_logit
    aligned["current_S4_conf"] = np.abs(current_logit)
    aligned["block_z"] = block_z
    aligned["row_z"] = row_z
    aligned["rank_z"] = rank_z
    aligned["latent_z"] = latent_z
    aligned["current_logit_z"] = current_z
    aligned["latent_minus_current_z"] = latent_z - current_z
    aligned["current_minus_latent_z"] = current_z - latent_z
    aligned["mismatch_abs_z"] = np.abs(latent_z - current_z)
    aligned["overconf_lowlatent_score"] = aligned["current_minus_latent_z"] + 0.20 * zscore(aligned["current_S4_conf"].to_numpy())
    aligned["underconf_highlatent_score"] = aligned["latent_minus_current_z"] + 0.20 * zscore(aligned["current_S4_conf"].to_numpy())
    return aligned


def active_stats(meta: pd.DataFrame, delta_s4: np.ndarray, family: str, tag: str, path: Path) -> dict[str, Any]:
    active = np.abs(delta_s4) > 1.0e-12
    pos = delta_s4 > 1.0e-12
    neg = delta_s4 < -1.0e-12
    return {
        "basename": path.name,
        "source_path": rel(path),
        "family": family,
        "tag": tag,
        "nonzero_rows": int(active.sum()),
        "pos_rows": int(pos.sum()),
        "neg_rows": int(neg.sum()),
        "mean_abs_s4_delta": float(np.mean(np.abs(delta_s4))),
        "max_abs_s4_delta": float(np.max(np.abs(delta_s4))) if len(delta_s4) else 0.0,
        "active_latent_mean": float(meta.loc[active, "latent_z"].mean()) if active.any() else 0.0,
        "inactive_latent_mean": float(meta.loc[~active, "latent_z"].mean()) if (~active).any() else 0.0,
        "active_current_logit_mean": float(meta.loc[active, "current_S4_logit"].mean()) if active.any() else 0.0,
        "active_mismatch_mean": float(meta.loc[active, "mismatch_abs_z"].mean()) if active.any() else 0.0,
        "active_overconf_mean": float(meta.loc[active, "overconf_lowlatent_score"].mean()) if active.any() else 0.0,
        "active_underconf_mean": float(meta.loc[active, "underconf_highlatent_score"].mean()) if active.any() else 0.0,
        "delta_latent_alignment": float(np.corrcoef(delta_s4, meta["latent_z"].to_numpy(dtype=np.float64))[0, 1])
        if np.std(delta_s4) > 1.0e-12
        else 0.0,
        "delta_current_alignment": float(np.corrcoef(delta_s4, meta["current_S4_logit"].to_numpy(dtype=np.float64))[0, 1])
        if np.std(delta_s4) > 1.0e-12
        else 0.0,
    }


def build_candidates(current: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    current_logit = meta["current_S4_logit"].to_numpy(dtype=np.float64)
    latent_minus_current = meta["latent_minus_current_z"].to_numpy(dtype=np.float64)
    current_minus_latent = meta["current_minus_latent_z"].to_numpy(dtype=np.float64)
    mismatch = meta["mismatch_abs_z"].to_numpy(dtype=np.float64)
    over = meta["overconf_lowlatent_score"].to_numpy(dtype=np.float64)
    under = meta["underconf_highlatent_score"].to_numpy(dtype=np.float64)
    latent = meta["latent_z"].to_numpy(dtype=np.float64)

    def add_delta(tag: str, delta_s4: np.ndarray, family: str) -> None:
        if np.count_nonzero(np.abs(delta_s4) > 1.0e-12) < 2:
            return
        delta = np.zeros((len(current), len(TARGETS)), dtype=np.float64)
        delta[:, S4_IDX] = np.asarray(delta_s4, dtype=np.float64)
        path = write_submission(current, delta, tag)
        deltas[path.name] = delta
        rows.append(active_stats(meta, delta_s4, family, tag, path))

    top_ns = [10, 12, 16, 20, 24, 32, 40, 50, 64]
    shrinks = [0.08, 0.12, 0.16, 0.22, 0.30]
    amps = [0.0125, 0.025, 0.0388, 0.052, 0.070]
    caps = [0.0388, 0.052, 0.070, 0.090]

    mismatch_order = np.argsort(-mismatch)
    over_order = np.argsort(-over)
    under_order = np.argsort(-under)
    latent_high_order = np.argsort(-latent)
    latent_low_order = np.argsort(latent)

    for n in top_ns:
        idx_m = mismatch_order[:n]
        idx_o = over_order[:n]
        idx_u = under_order[:n]
        idx_hi = latent_high_order[:n]
        idx_lo = latent_low_order[:n]
        for shrink in shrinks:
            for cap in caps:
                delta = np.zeros(len(meta), dtype=np.float64)
                delta[idx_m] = np.clip(-shrink * current_logit[idx_m], -cap, cap)
                add_delta(f"temper_mismatch_top{n}_s{shrink:.2f}_cap{cap:.4f}", delta, "temper_mismatch")

                delta = np.zeros(len(meta), dtype=np.float64)
                delta[idx_o] = np.clip(-shrink * current_logit[idx_o], -cap, cap)
                add_delta(f"temper_overconf_top{n}_s{shrink:.2f}_cap{cap:.4f}", delta, "temper_overconf")

                control = np.zeros(len(meta), dtype=np.float64)
                control[idx_o] = np.clip(shrink * current_logit[idx_o], -cap, cap)
                add_delta(f"control_sharpen_overconf_top{n}_s{shrink:.2f}_cap{cap:.4f}", control, "control_sharpen")

        for amp in amps:
            delta = np.zeros(len(meta), dtype=np.float64)
            delta[idx_o] = -amp
            add_delta(f"down_overconf_top{n}_a{amp:.4f}", delta, "down_overconf")

            delta = np.zeros(len(meta), dtype=np.float64)
            delta[idx_u] = amp
            add_delta(f"up_underconf_top{n}_a{amp:.4f}", delta, "up_underconf")

            delta = np.zeros(len(meta), dtype=np.float64)
            delta[idx_m] = amp * np.sign(latent_minus_current[idx_m])
            add_delta(f"bidir_mismatch_top{n}_a{amp:.4f}", delta, "bidir_mismatch")

            delta = np.zeros(len(meta), dtype=np.float64)
            delta[idx_hi] = amp
            delta[idx_lo] = -amp
            add_delta(f"signed_latent_hi_lo_top{n}_a{amp:.4f}", delta, "signed_latent_hi_lo")

            control = np.zeros(len(meta), dtype=np.float64)
            control[idx_o] = amp
            add_delta(f"control_up_overconf_top{n}_a{amp:.4f}", control, "control_wrong_overconf")

    frame = pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    frame["active_minus_inactive_latent"] = frame["active_latent_mean"] - frame["inactive_latent_mean"]
    frame.to_csv(CANDIDATE_OUT, index=False)
    return frame, deltas


def select_for_null(prefilter: pd.DataFrame) -> pd.DataFrame:
    if prefilter.empty:
        return prefilter
    strict = prefilter[prefilter["strict_promote_gate"].map(as_bool)].copy()
    pool = strict if not strict.empty else prefilter.copy()
    pool["selection_score"] = (
        pool["pred_delta_vs_current_p90"].fillna(0.0)
        + 0.45 * pool["pred_delta_vs_current_mean"].fillna(0.0)
        - 0.00001 * pool["active_mismatch_mean"].fillna(0.0)
        - 0.00001 * np.abs(pool["delta_current_alignment"].fillna(0.0))
    )
    pieces = [
        pool.sort_values("selection_score").head(MAX_NULL_EVAL),
        pool[pool["family"].str.contains("temper", na=False)].sort_values("selection_score").head(8),
        pool[pool["family"].str.contains("down_overconf|bidir", na=False)].sort_values("selection_score").head(8),
        pool[pool["family"].str.contains("control", na=False)].sort_values("selection_score").head(4),
    ]
    return pd.concat(pieces, ignore_index=True).drop_duplicates("basename").head(MAX_NULL_EVAL).reset_index(drop=True)


def write_null_candidate(current: pd.DataFrame, delta: np.ndarray, basename: str, meta: pd.DataFrame, mode: str, rep: int) -> Path:
    seed = int(hashlib.sha1(f"{basename}|{mode}|{rep}|e307".encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
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
    if selected.empty:
        return pd.DataFrame(), pd.DataFrame()
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
        mode_stats: dict[str, float] = {}
        mode_p90 = []
        mode_mean = []
        for mode, part in these.groupby("mode"):
            mp90 = float(np.mean(actual_p90 < part["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)))
            mmean = float(np.mean(actual_mean < part["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)))
            mode_p90.append(mp90)
            mode_mean.append(mmean)
            mode_stats[f"{mode}_p90_dominance"] = mp90
            mode_stats[f"{mode}_mean_dominance"] = mmean
            mode_stats[f"{mode}_null_strict_rate"] = float(part["strict_promote_gate"].map(as_bool).mean())
        worst_p90 = float(min(mode_p90)) if mode_p90 else 0.0
        worst_mean = float(min(mode_mean)) if mode_mean else 0.0
        dateblock_p90 = mode_stats.get("dateblock_p90_dominance", 0.0)
        dateblock_mean = mode_stats.get("dateblock_mean_dominance", 0.0)
        sign_p90 = mode_stats.get("sign_p90_dominance", 0.0)
        ready = bool(
            as_bool(a["strict_promote_gate"])
            and null_strict <= 0.10
            and p90_dom >= 0.80
            and mean_dom >= 0.70
            and worst_p90 >= 0.60
            and worst_mean >= 0.50
            and dateblock_p90 >= 0.65
            and dateblock_mean >= 0.55
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
                "public_free_ready": ready,
                "decision": "candidate_ready_needs_64rep_confirm" if ready else "do_not_submit",
                **mode_stats,
            }
        )
    governor = pd.DataFrame(rows).sort_values(
        ["public_free_ready", "null_strict_rate", "mean_dominance", "dateblock_p90_dominance", "actual_p90"],
        ascending=[False, True, False, False, True],
    ).reset_index(drop=True)
    governor.to_csv(GOVERNOR_OUT, index=False)
    return null_map, governor


def write_report(meta: pd.DataFrame, candidates: pd.DataFrame, prefilter: pd.DataFrame, governor: pd.DataFrame) -> None:
    ready = governor[governor["public_free_ready"].map(as_bool)] if not governor.empty else pd.DataFrame()
    state_summary = pd.DataFrame(
        [
            {
                "n_rows": len(meta),
                "corr_latent_current_logit": float(np.corrcoef(meta["latent_z"], meta["current_S4_logit"])[0, 1]),
                "corr_block_row_state": float(np.corrcoef(meta["block_z"], meta["row_z"])[0, 1]),
                "mismatch_top24_current_mean": float(meta.sort_values("mismatch_abs_z", ascending=False).head(24)["current_S4"].mean()),
                "mismatch_top24_latent_mean": float(meta.sort_values("mismatch_abs_z", ascending=False).head(24)["latent_z"].mean()),
            }
        ]
    )
    summary = pd.DataFrame(
        [
            {
                "generated_candidates": len(candidates),
                "old_strict": int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0,
                "null_evaluated": len(governor),
                "ready_32rep": len(ready),
                "best_null_strict_rate": float(governor["null_strict_rate"].min()) if not governor.empty else np.nan,
                "best_mean_dominance": float(governor["mean_dominance"].max()) if not governor.empty else np.nan,
                "best_dateblock_p90_dominance": float(governor["dateblock_p90_dominance"].max()) if not governor.empty and "dateblock_p90_dominance" in governor.columns else np.nan,
                "best_actual_p90": float(governor["actual_p90"].min()) if not governor.empty else np.nan,
            }
        ]
    )
    out_summary = pd.concat([state_summary, summary], axis=1)
    out_summary.to_csv(SUMMARY_OUT, index=False)

    lines = [
        "# E307 S4 Latent Censor Materializer",
        "",
        "Public LB는 사용하지 않았다. E304/E306 latent를 positive S4 generator로 쓰지 않고, current S4 과신을 누그러뜨리는 censor/calibration action으로 바꿔 검증했다.",
        "",
        "## Question",
        "",
        "S4 병목이 `어디를 올릴까`가 아니라 `어디가 과신인가`라면, hidden block/row state와 current S4 logit의 충돌 row를 0.5 쪽으로 tempering하는 편이 dateblock null보다 건강해야 한다.",
        "",
        "## Summary",
        "",
        md(out_summary),
        "",
        "## Best Prefilter Rows",
        "",
        md(
            prefilter,
            [
                "basename",
                "family",
                "nonzero_rows",
                "active_mismatch_mean",
                "delta_latent_alignment",
                "delta_current_alignment",
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
                "dateblock_p90_dominance",
                "dateblock_mean_dominance",
                "sign_p90_dominance",
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
        lines.append("- A 32-rep public-free latent-censor candidate exists, but it needs 64-rep independent confirmation before any public LB use.")
    else:
        lines.extend(
            [
                "- No E307 candidate survives the local governor.",
                "- This rejects simple S4 latent-vs-current censoring as a direct submission path.",
                "- The useful signal remains diagnostic: hidden row/block state exposes calibration-risk rows, but action health still needs a learned/null-aware translator.",
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
    current, _current_meta = load_current_and_meta()
    meta = align_state(current)
    candidates, deltas = build_candidates(current, meta)
    scored = score_paths([OUT / b for b in candidates["basename"]], current)
    keep = [
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
    prefilter = candidates.merge(scored[keep], on="basename", how="left")
    prefilter = prefilter.sort_values(
        ["strict_promote_gate", "pred_delta_vs_current_p90", "active_mismatch_mean"],
        ascending=[False, True, False],
    ).reset_index(drop=True)
    prefilter.to_csv(PREFILTER_OUT, index=False)
    selected = select_for_null(prefilter)
    _null_map, governor = run_governor(selected, deltas, current, meta)
    write_report(meta, candidates, prefilter, governor)
    old_strict = int(prefilter["strict_promote_gate"].map(as_bool).sum()) if not prefilter.empty else 0
    ready = int(governor["public_free_ready"].map(as_bool).sum()) if not governor.empty else 0
    print(f"generated={len(candidates)} old_strict={old_strict} null_eval={len(governor)} ready={ready}")
    print(f"wrote {rel(REPORT_OUT)}")


if __name__ == "__main__":
    main()
