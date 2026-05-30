#!/usr/bin/env python3
"""E285: E247-relative human-state residual cell audit.

E283 rejected scalar app-entropy re-ranking of E247 smoothing cells, and E284
showed that app-entropy helps an older E224/E154 decisive-cell target while
missing most of the current E247 public-positive body.

This experiment moves the target anchor forward:

    human/social context + feature-NN1 cell geometry -> preserve/undo/avoid
    decisions around the current E247 Q3 smoothing cells.

It does not spend public LB. Candidate tensors are only considered interesting
if they beat E247 under the current-anchor selector and also beat matched
row/subject/dateblock placebo movement.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
NULL_DIR = OUT / "e285_e247_residual_human_state_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e246_feature_nn1_smoothing_selector_ablation as e246  # noqa: E402
import e283_appentropy_q3_smooth_context_audit as e283  # noqa: E402
from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    evaluate_models,
    score_candidates,
    selected_models,
)
from public_anchor_bottleneck_decomposition import (  # noqa: E402
    KEYS,
    TARGETS,
    feature_row,
    known_public_table,
    load_sub,
    logit,
)
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


Q3_IDX = TARGETS.index("Q3")
RNG_SEED = 20260531 + 285
N_REPS = 7

BOUNDARY_OUT = OUT / "e285_e247_residual_human_state_boundary_summary.csv"
CELL_OUT = OUT / "e285_e247_residual_human_state_cell_summary.csv"
CANDIDATE_OUT = OUT / "e285_e247_residual_human_state_candidate_summary.csv"
NULLS_OUT = OUT / "e285_e247_residual_human_state_nulls.csv"
SCORES_OUT = OUT / "e285_e247_residual_human_state_scores.csv"
GOVERNOR_OUT = OUT / "e285_e247_residual_human_state_governor_summary.csv"
REPORT_OUT = OUT / "e285_e247_residual_human_state_report.md"

E273_FEATURES = OUT / "e273_human_diary_state_jepa_audit_features.parquet"
E273_BOUNDARY = OUT / "e273_human_diary_state_jepa_audit_boundary.csv"
E268_FEATURES = OUT / "e268_human_social_story_features.parquet"
E270_FEATURES = OUT / "e270_payday_cashflow_story_features.parquet"
E280_SUMMARY = OUT / "e280_story_transfer_alignment_summary.csv"
E284_SELECTED = OUT / "e284_appentropy_decisive_cell_jepa_selected_summary.csv"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(df: pd.DataFrame) -> str:
    arr = np.asarray(df[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 80) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(text))[:limit]


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def parse_idx(text: str) -> np.ndarray:
    if not str(text).strip() or str(text).lower() == "nan":
        return np.asarray([], dtype=int)
    return np.asarray([int(x) for x in str(text).split()], dtype=int)


def zscore(values: pd.Series | np.ndarray) -> pd.Series:
    vals = pd.Series(values, dtype=float)
    sd = float(vals.std(ddof=0))
    if sd < 1.0e-12:
        return pd.Series(np.zeros(len(vals)), index=vals.index)
    return (vals - float(vals.mean())) / sd


def key_norm(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out.reset_index(drop=True)


def topk(part: pd.DataFrame, score: pd.Series | np.ndarray, k: int, ascending: bool = False) -> np.ndarray:
    score_ser = pd.Series(score, index=part.index, dtype=float)
    ordered = part.assign(_score=score_ser).sort_values(["_score", "row_idx"], ascending=[ascending, True])
    return ordered.head(k)["row_idx"].to_numpy(dtype=int)


def ensure_e246() -> None:
    if not e246.SELECTOR_OUT.exists() or not e246.SUMMARY_OUT.exists():
        rows = e246.build_selector_rows()
        local_summary, target_df, overlap = e246.audit_specs(rows, e246.selector_specs(rows))
        local_summary.to_csv(e246.SUMMARY_OUT, index=False)
        target_df.to_csv(e246.TARGET_OUT, index=False)
        overlap.to_csv(e246.OVERLAP_OUT, index=False)
        rows.to_csv(e246.SELECTOR_OUT, index=False)


def selector_set(selector_id: str) -> set[int]:
    ensure_e246()
    summary = pd.read_csv(e246.SUMMARY_OUT)
    hit = summary[summary["candidate_id"].eq(selector_id)]
    if hit.empty:
        raise RuntimeError(f"missing selector {selector_id}")
    return set(parse_idx(str(hit.iloc[0]["row_idx_list"])).tolist())


def selected_q3_rows(path: Path, sample: pd.DataFrame, e224: np.ndarray, e154: np.ndarray) -> set[int]:
    if not path.exists():
        return set()
    cand = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    dist_to_e154 = np.abs(cand[:, Q3_IDX] - e154[:, Q3_IDX])
    dist_to_e224 = np.abs(cand[:, Q3_IDX] - e224[:, Q3_IDX])
    return set(np.where((dist_to_e154 < 1.0e-9) & (dist_to_e224 > 1.0e-9))[0].astype(int).tolist())


def e284_row_features(sample: pd.DataFrame, e224: np.ndarray, e154: np.ndarray) -> pd.DataFrame:
    rows = pd.DataFrame({"row_idx": np.arange(len(sample), dtype=int)})
    rows["e284_select_count"] = 0
    rows["e284_score_sum"] = 0.0
    rows["e284_score_max"] = 0.0
    rows["e284_top2_count"] = 0
    if not E284_SELECTED.exists():
        return rows
    selected = pd.read_csv(E284_SELECTED)
    selected = selected[selected["submission_file"].notna()].copy()
    ranked = selected.sort_values("e237_score", ascending=False).reset_index(drop=True)
    for rank, rec in ranked.iterrows():
        path = OUT / str(rec["submission_file"])
        dropped = selected_q3_rows(path, sample, e224, e154)
        score = float(rec.get("e237_score", 0.0))
        if not dropped:
            continue
        mask = rows["row_idx"].isin(dropped)
        rows.loc[mask, "e284_select_count"] += 1
        rows.loc[mask, "e284_score_sum"] += score
        rows.loc[mask, "e284_score_max"] = np.maximum(rows.loc[mask, "e284_score_max"].to_numpy(dtype=float), score)
        if rank < 2:
            rows.loc[mask, "e284_top2_count"] += 1
    return rows


def load_test_feature_frame(path: Path, sample: pd.DataFrame) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_parquet(path)
    test = df[df["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    if len(test) != len(sample) or not key_norm(test).equals(key_norm(sample)):
        raise RuntimeError(f"feature frame key mismatch: {path}")
    out = test.copy()
    out["row_idx"] = np.arange(len(out), dtype=int)
    return out


def candidate_human_columns(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    frames: list[pd.DataFrame] = []
    cols: list[str] = []

    e273 = load_test_feature_frame(E273_FEATURES, sample)
    if not e273.empty:
        boundary = pd.read_csv(E273_BOUNDARY) if E273_BOUNDARY.exists() else pd.DataFrame()
        boundary_cols = [
            str(x)
            for x in boundary.sort_values("abs_boundary_signal", ascending=False)["feature"].head(18).tolist()
            if str(x) in e273.columns
        ]
        family_cols = [
            "diary_state_pc6",
            "diary_state_energy",
            "jepa_prednorm_subject_social_comm",
            "jepa_prednorm_dateblock_social_comm",
            "jepa_prednorm_subject_cognitive_money",
            "jepa_prednorm_subject_bedtime_phone",
            "jepa_prednorm_subject_mobility_context",
            "jepa_prednorm_dateblock_mobility_context",
            "jepa_resid_subject_routine_calendar",
            "routine_calendar_energy",
        ]
        keep = list(dict.fromkeys([c for c in [*boundary_cols, *family_cols] if c in e273.columns]))
        part = e273[["row_idx", *keep]].copy()
        frames.append(part)
        cols.extend(keep)

    e268 = load_test_feature_frame(E268_FEATURES, sample)
    if not e268.empty:
        story_cols = [
            "app_entropy_scattered_day_subj_z",
            "single_app_monotony_subj_z",
            "commute_workday_subj_z",
            "bright_light_late_subj_z",
            "phone_in_bed_subj_z",
            "late_msg_call_subj_z",
            "presleep_msg_drag_subj_z",
            "screen_fragmentation_subj_z",
            "home_stability_subj_z",
            "vehicle_noise_day_subj_z",
            "weekend_social_jetlag_subj_z",
            "weekend_ritual_rest_subj_z",
        ]
        if E280_SUMMARY.exists():
            e280 = pd.read_csv(E280_SUMMARY)
            story_cols.extend(str(x) for x in e280.sort_values("transfer_survival_score", ascending=False)["score_col"].head(10))
        keep = list(dict.fromkeys([c for c in story_cols if c in e268.columns]))
        frames.append(e268[["row_idx", *keep]].copy())
        cols.extend(keep)

    e270 = load_test_feature_frame(E270_FEATURES, sample)
    if not e270.empty:
        cash_cols = [
            "paymonth_start_near3_money_rumination_subj_z",
            "paymonth_start_post3_late_shopping_subj_z",
            "pay15_post3_late_shopping_subj_z",
            "pay25_pre7_budget_squeeze_subj_z",
            "eom_bill_anxiety_subj_z",
            "monthstart_spending_reset_subj_z",
        ]
        keep = [c for c in cash_cols if c in e270.columns]
        frames.append(e270[["row_idx", *keep]].copy())
        cols.extend(keep)

    base = pd.DataFrame({"row_idx": np.arange(len(sample), dtype=int)})
    for frame in frames:
        base = base.merge(frame, on="row_idx", how="left")
    cols = list(dict.fromkeys(cols))
    for col in cols:
        base[col] = pd.to_numeric(base[col], errors="coerce").astype(float).fillna(0.0)
        base[f"z_{col}"] = zscore(base[col]).to_numpy()
    z_cols = [f"z_{col}" for col in cols]
    return base[["row_idx", *z_cols]], z_cols


def build_cell_table() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    ensure_e246()
    sample = load_sub(CURRENT).sort_values(KEYS).reset_index(drop=True)
    rows = e283.load_rows_with_state().sort_values("row_idx").reset_index(drop=True)
    e247 = selector_set("nn_smooth_sum_top34")
    e256 = selector_set("top50_amp_then_smooth25")
    e224 = load_sub(e230.E224_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    e154 = load_sub(e230.E154_FILE, sample)[TARGETS].to_numpy(dtype=np.float64)
    current = load_sub(CURRENT, sample)[TARGETS].to_numpy(dtype=np.float64)

    rows["in_e247"] = rows["row_idx"].isin(e247)
    rows["in_e256"] = rows["row_idx"].isin(e256)
    rows["e247_common"] = rows["in_e247"] & rows["in_e256"]
    rows["e247_only"] = rows["in_e247"] & ~rows["in_e256"]
    rows["e256_only"] = ~rows["in_e247"] & rows["in_e256"]
    rows["smooth_z"] = zscore(rows["single_row_smooth_gain_sum"]).to_numpy()
    rows["amp_z"] = zscore(rows["rollback_amp_abs"]).to_numpy()
    rows["state_z"] = zscore(rows["app_state_avg_z"]).to_numpy()
    rows["story_z"] = zscore(rows["app_story_score"]).to_numpy()
    rows["state_amp_z"] = zscore(zscore(rows["app_state_avg_z"]) * zscore(rows["rollback_amp_abs"])).to_numpy()
    rows["smooth_state_risk"] = rows["smooth_z"] - np.maximum(rows["state_amp_z"], 0.0)

    human, human_cols = candidate_human_columns(sample)
    rows = rows.merge(human, on="row_idx", how="left")
    for col in human_cols:
        rows[col] = rows[col].fillna(0.0)

    e284_features = e284_row_features(sample, e224, e154)
    rows = rows.merge(e284_features, on="row_idx", how="left")
    for col in ["e284_select_count", "e284_score_sum", "e284_score_max", "e284_top2_count"]:
        rows[col] = rows[col].fillna(0.0)
    rows["e284_score_z"] = zscore(rows["e284_score_max"]).to_numpy()
    rows["e284_extra"] = (rows["e284_select_count"] > 0) & ~rows["in_e247"]

    boundary = boundary_summary(rows, human_cols)
    cell_summary = cell_group_summary(rows)
    rows.to_csv(CELL_OUT, index=False)
    return rows, boundary, cell_summary, current, e224, e154


def boundary_summary(rows: pd.DataFrame, human_cols: list[str]) -> pd.DataFrame:
    e247_only = rows[rows["e247_only"]].copy()
    e256_only = rows[rows["e256_only"]].copy()
    neither = rows[~rows["in_e247"] & ~rows["in_e256"]].copy()
    records: list[dict[str, object]] = []
    feature_cols = [
        "state_z",
        "story_z",
        "state_amp_z",
        "smooth_z",
        "amp_z",
        "e284_score_z",
        *human_cols,
    ]
    for col in feature_cols:
        if col not in rows.columns:
            continue
        all_sd = float(rows[col].std(ddof=0))
        if all_sd < 1.0e-12:
            continue
        rec = {
            "feature": col,
            "mean_e247_only": float(e247_only[col].mean()) if len(e247_only) else np.nan,
            "mean_e256_only": float(e256_only[col].mean()) if len(e256_only) else np.nan,
            "mean_neither": float(neither[col].mean()) if len(neither) else np.nan,
        }
        rec["e247_vs_e256_d"] = float((rec["mean_e247_only"] - rec["mean_e256_only"]) / all_sd)
        rec["e247_vs_neither_d"] = float((rec["mean_e247_only"] - rec["mean_neither"]) / all_sd)
        rec["e256_vs_neither_d"] = float((rec["mean_e256_only"] - rec["mean_neither"]) / all_sd)
        rec["abs_boundary_signal"] = abs(float(rec["e247_vs_e256_d"]))
        records.append(rec)
    out = pd.DataFrame(records).sort_values("abs_boundary_signal", ascending=False).reset_index(drop=True)
    out.to_csv(BOUNDARY_OUT, index=False)
    return out


def cell_group_summary(rows: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    groups = {
        "e247_common": rows["e247_common"],
        "e247_only": rows["e247_only"],
        "e256_only": rows["e256_only"],
        "e284_extra": rows["e284_extra"],
        "neither": ~rows["in_e247"] & ~rows["in_e256"],
    }
    metrics = [
        "single_row_smooth_gain_sum",
        "rollback_amp_abs",
        "app_state_avg_z",
        "app_story_score",
        "state_amp_z",
        "e284_select_count",
        "e284_score_max",
        "nn_dist",
    ]
    for group, mask in groups.items():
        part = rows[mask].copy()
        if part.empty:
            continue
        rec: dict[str, object] = {
            "group": group,
            "n_rows": int(len(part)),
            "e237_overlap": int(part["e237_drop"].astype(bool).sum()) if "e237_drop" in part else 0,
            "e230_swing_overlap": int(part["e230_swing25"].astype(bool).sum()) if "e230_swing25" in part else 0,
            "e230_risk_overlap": int(part["e230_risk21"].astype(bool).sum()) if "e230_risk21" in part else 0,
        }
        for metric in metrics:
            rec[f"{metric}_mean"] = float(part[metric].mean())
            rec[f"{metric}_median"] = float(part[metric].median())
        records.append(rec)
    out = pd.DataFrame(records)
    out.to_csv(CELL_OUT.with_name("e285_e247_residual_human_state_group_summary.csv"), index=False)
    return out


def row_set_note(rows: pd.DataFrame, row_idx: np.ndarray) -> dict[str, object]:
    selected = rows[rows["row_idx"].isin(set(row_idx.astype(int)))]
    if selected.empty:
        return {
            "row_count": 0,
            "e247_overlap": 0,
            "e256_overlap": 0,
            "e284_overlap": 0,
            "mean_smooth_gain": np.nan,
            "sum_smooth_gain": 0.0,
            "mean_amp": np.nan,
            "mean_app_state": np.nan,
            "mean_app_story": np.nan,
            "mean_state_amp_z": np.nan,
        }
    return {
        "row_count": int(len(selected)),
        "e247_overlap": int(selected["in_e247"].sum()),
        "e256_overlap": int(selected["in_e256"].sum()),
        "e284_overlap": int((selected["e284_select_count"] > 0).sum()),
        "mean_smooth_gain": float(selected["single_row_smooth_gain_sum"].mean()),
        "sum_smooth_gain": float(selected["single_row_smooth_gain_sum"].sum()),
        "mean_amp": float(selected["rollback_amp_abs"].mean()),
        "mean_app_state": float(selected["app_state_avg_z"].mean()),
        "mean_app_story": float(selected["app_story_score"].mean()),
        "mean_state_amp_z": float(selected["state_amp_z"].mean()),
    }


def candidate_specs(rows: pd.DataFrame, boundary: pd.DataFrame) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    e247_part = rows[rows["in_e247"]].copy()
    outside = rows[~rows["in_e247"]].copy()
    e247_only = rows[rows["e247_only"]].copy()
    common = rows[rows["e247_common"]].copy()
    e256_only = rows[rows["e256_only"]].copy()
    e284_extra = rows[rows["e284_extra"]].copy()
    fractions = [0.25, 0.50, 1.00]

    base_groups = [
        ("undo_e247_only", e247_only["row_idx"].to_numpy(dtype=int), "undo", "all E247-only cells"),
        ("undo_common", common["row_idx"].to_numpy(dtype=int), "undo", "E247/E256 common core cells"),
        ("add_e256_only", e256_only["row_idx"].to_numpy(dtype=int), "add", "known E256-only public-worse added cells"),
    ]
    if len(e284_extra):
        extra_top = e284_extra.sort_values(["e284_select_count", "e284_score_max"], ascending=[False, False]).head(8)
        base_groups.append(("add_e284_extra_top8", extra_top["row_idx"].to_numpy(dtype=int), "add", "old-law E284 extra cells outside E247"))

    for prefix, idx, action, note in base_groups:
        for frac in fractions:
            if len(idx):
                specs.append(
                    {
                        "candidate_id": f"{prefix}_f{str(frac).replace('.', 'p')}",
                        "action": action,
                        "row_idx": np.asarray(sorted(set(idx.tolist())), dtype=int),
                        "fraction": frac,
                        "rule_family": "membership_control",
                        "rule_note": note,
                    }
                )

    ranked_rules = [
        ("high_state", "app_state_avg_z", False, "high predicted routine-fragmentation state"),
        ("low_state", "app_state_avg_z", True, "low predicted routine-fragmentation state"),
        ("high_story", "app_story_score", False, "high raw app-entropy story score"),
        ("high_stateamp", "state_amp_z", False, "high app-state by rollback-amplitude interaction"),
        ("high_amp", "rollback_amp_abs", False, "large rollback amplitude"),
        ("low_smooth", "single_row_smooth_gain_sum", True, "weak feature-NN1 smoothing gain"),
        ("high_e284_oldlaw", "e284_score_max", False, "high old E284 stale-target score"),
    ]
    for label, col, ascending, note in ranked_rules:
        if col not in rows.columns:
            continue
        for k in [3, 5, 8]:
            idx = topk(e247_part, e247_part[col], k, ascending=ascending)
            for frac in [0.25, 0.50]:
                specs.append(
                    {
                        "candidate_id": f"undo_{label}_top{k}_f{str(frac).replace('.', 'p')}",
                        "action": "undo",
                        "row_idx": idx,
                        "fraction": frac,
                        "rule_family": "e247_undo_rank",
                        "rule_note": f"undo E247 rows with {note}",
                    }
                )

    top_boundary = boundary[boundary["feature"].isin(rows.columns)].head(14)
    for _, rec in top_boundary.iterrows():
        feature = str(rec["feature"])
        d = float(rec["e247_vs_e256_d"])
        # E256-like direction is the side opposite the E247-only mean.
        e256_like_ascending = bool(d > 0.0)
        e247_like_ascending = not e256_like_ascending
        for k in [3, 5]:
            idx_bad = topk(e247_part, e247_part[feature], k, ascending=e256_like_ascending)
            idx_good = topk(e247_part, e247_part[feature], k, ascending=e247_like_ascending)
            for frac in [0.25, 0.50]:
                specs.append(
                    {
                        "candidate_id": f"undo_e256like_{safe_id(feature, 34)}_top{k}_f{str(frac).replace('.', 'p')}",
                        "action": "undo",
                        "row_idx": idx_bad,
                        "fraction": frac,
                        "rule_family": "human_boundary_undo",
                        "rule_note": f"undo E247 rows that look E256-like on {feature} (d={d:.3f})",
                    }
                )
                specs.append(
                    {
                        "candidate_id": f"undo_e247like_ctrl_{safe_id(feature, 30)}_top{k}_f{str(frac).replace('.', 'p')}",
                        "action": "undo",
                        "row_idx": idx_good,
                        "fraction": frac,
                        "rule_family": "human_boundary_control",
                        "rule_note": f"control: undo E247-like side on {feature} (d={d:.3f})",
                    }
                )
        # Addition branch: add outside-E247 rows that look E247-like and still have smoothing support.
        score = rows["smooth_z"] + np.sign(d if d != 0.0 else 1.0) * rows[feature]
        outside_score = score.loc[outside.index]
        for k in [3, 5]:
            idx_add = topk(outside, outside_score, k, ascending=False)
            specs.append(
                {
                    "candidate_id": f"add_e247like_{safe_id(feature, 36)}_top{k}_f0p25",
                    "action": "add",
                    "row_idx": idx_add,
                    "fraction": 0.25,
                    "rule_family": "human_boundary_add",
                    "rule_note": f"add outside rows that look E247-like on {feature} and smooth well",
                }
            )

    dedup: dict[tuple[str, tuple[int, ...], float], dict[str, object]] = {}
    for spec in specs:
        row_idx = np.asarray(sorted(set(np.asarray(spec["row_idx"], dtype=int).tolist())), dtype=int)
        if len(row_idx) == 0:
            continue
        spec = dict(spec)
        spec["row_idx"] = row_idx
        key = (str(spec["action"]), tuple(row_idx.tolist()), float(spec["fraction"]))
        dedup.setdefault(key, spec)
    return list(dedup.values())


def apply_candidate(current: np.ndarray, e224: np.ndarray, e154: np.ndarray, row_idx: np.ndarray, action: str, fraction: float) -> np.ndarray:
    pred = current.copy()
    idx = np.asarray(row_idx, dtype=int)
    if action == "undo":
        target = logit(e224[:, Q3_IDX])
    elif action == "add":
        target = logit(e154[:, Q3_IDX])
    else:
        raise ValueError(action)
    base = logit(pred[:, Q3_IDX])
    pred[idx, Q3_IDX] = sigmoid(base[idx] + float(fraction) * (target[idx] - base[idx]))
    return clip_prob(pred)


def materialize_candidates(rows: pd.DataFrame, specs: list[dict[str, object]], current: np.ndarray, e224: np.ndarray, e154: np.ndarray) -> pd.DataFrame:
    sample = load_sub(CURRENT).sort_values(KEYS).reset_index(drop=True)
    records: list[dict[str, object]] = []
    seen_hashes: set[str] = set()
    for spec in specs:
        row_idx = np.asarray(spec["row_idx"], dtype=int)
        pred = apply_candidate(current, e224, e154, row_idx, str(spec["action"]), float(spec["fraction"]))
        if np.max(np.abs(pred - current)) < 1.0e-12:
            continue
        out = sample[KEYS].copy()
        out[TARGETS] = pred
        digest = short_hash(out)
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        name = f"submission_e285_e247resid_{safe_id(str(spec['candidate_id']), 78)}_{digest}.csv"
        path = OUT / name
        out.to_csv(path, index=False)
        note = row_set_note(rows, row_idx)
        records.append(
            {
                "basename": name,
                "source_path": rel(path),
                "candidate_id": spec["candidate_id"],
                "action": spec["action"],
                "fraction": float(spec["fraction"]),
                "rule_family": spec["rule_family"],
                "rule_note": spec["rule_note"],
                "row_idx_list": " ".join(map(str, row_idx.tolist())),
                **note,
            }
        )
    out_df = pd.DataFrame(records)
    out_df.to_csv(CANDIDATE_OUT, index=False)
    return out_df


def test_meta(base: pd.DataFrame) -> pd.DataFrame:
    state = pd.read_csv(e283.STATE_IN)
    meta = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    if not key_norm(meta).equals(key_norm(base)):
        raise RuntimeError("E285 test metadata does not align with current base")
    out = meta[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    return out


def write_null_candidate(base: pd.DataFrame, delta: np.ndarray, meta: pd.DataFrame, source_path: Path, mode: str, rep: int, seed: int) -> Path:
    rng = np.random.default_rng(seed)
    shuffled = np.zeros_like(delta)
    for target_idx in range(delta.shape[1]):
        values = delta[:, target_idx].copy()
        if mode == "row":
            shuffled[:, target_idx] = values[rng.permutation(len(values))]
        elif mode == "subject":
            for _, idx in meta.groupby("subject_id").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        elif mode == "dateblock":
            for _, idx in meta.groupby("dateblock_group").indices.items():
                idx_arr = np.asarray(idx, dtype=int)
                shuffled[idx_arr, target_idx] = values[idx_arr][rng.permutation(len(idx_arr))]
        else:
            raise ValueError(mode)
    out = base.copy()
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    out[TARGETS] = clip_prob(sigmoid(base_logits + shuffled))
    stem = source_path.stem.replace("submission_", "")[:80]
    path = NULL_DIR / f"submission_e285null_{stem}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_nulls(candidates: pd.DataFrame) -> pd.DataFrame:
    NULL_DIR.mkdir(exist_ok=True)
    if candidates.empty:
        out = pd.DataFrame()
        out.to_csv(NULLS_OUT, index=False)
        return out
    base = load_sub(CURRENT)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    meta = test_meta(base[KEYS])
    records: list[dict[str, object]] = []
    for cand_idx, rec in enumerate(candidates.to_dict("records")):
        path = ROOT / str(rec["source_path"])
        candidate = load_sub(path, base[KEYS])
        delta = logit(candidate[TARGETS].to_numpy(dtype=np.float64)) - base_logits
        if np.max(np.abs(delta)) < 1.0e-12:
            continue
        for mode in ["row", "subject", "dateblock"]:
            for rep in range(N_REPS):
                seed = RNG_SEED + cand_idx * 1009 + rep * 97 + {"row": 0, "subject": 1, "dateblock": 2}[mode]
                null_path = write_null_candidate(base, delta, meta, path, mode, rep, seed)
                records.append(
                    {
                        "source_path": rec["source_path"],
                        "source_basename": rec["basename"],
                        "null_path": rel(null_path),
                        "null_basename": null_path.name,
                        "mode": mode,
                        "rep": rep,
                        "seed": seed,
                    }
                )
    out = pd.DataFrame(records)
    out.to_csv(NULLS_OUT, index=False)
    return out


def feature_rows(paths: list[Path], sample: pd.DataFrame, refs: dict[str, np.ndarray], ref_vecs: dict[str, np.ndarray]) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for path in paths:
        key = rel(path)
        if key in seen:
            continue
        seen.add(key)
        row = feature_row(path, sample, refs, ref_vecs)
        row["file"] = key
        row["source_path"] = key
        row["basename"] = path.name
        records.append(row)
    return pd.DataFrame(records)


def score_current_anchor(candidates: pd.DataFrame, nulls: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if candidates.empty:
        out = pd.DataFrame()
        out.to_csv(SCORES_OUT, index=False)
        return out, pd.DataFrame()
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    paths = [OUT / CURRENT]
    paths.extend(ROOT / str(path) for path in candidates["source_path"].tolist())
    if not nulls.empty:
        paths.extend(ROOT / str(path) for path in nulls["null_path"].tolist())
    feats = feature_rows(paths, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, feats, model_df)
    scores.to_csv(SCORES_OUT, index=False)
    return scores, selected_models(model_df)


def summarize_governor(scores: pd.DataFrame, candidates: pd.DataFrame, nulls: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty or scores.empty:
        out = pd.DataFrame()
        out.to_csv(GOVERNOR_OUT, index=False)
        return out
    actual = scores.merge(candidates, on=["basename", "source_path"], how="inner")
    null_scores = scores.merge(nulls, left_on="source_path", right_on="null_path", how="inner") if not nulls.empty else pd.DataFrame()
    public_map = known_public_table().set_index("file")["public_lb"].to_dict()
    records: list[dict[str, object]] = []
    for _, rec in actual.iterrows():
        matched = null_scores[null_scores["source_basename"].eq(rec["basename"])].copy() if not null_scores.empty else pd.DataFrame()
        actual_p90 = float(rec["pred_delta_vs_current_p90"])
        actual_mean = float(rec["pred_delta_vs_current_mean"])
        if matched.empty:
            p90_dom = mean_dom = worst_mode_dom = null_strict_rate = np.nan
            placebo_gate = False
            mode_fields: dict[str, object] = {}
        else:
            null_p90 = matched["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
            null_mean = matched["pred_delta_vs_current_mean"].to_numpy(dtype=np.float64)
            strict_null = matched["strict_promote_gate"].astype(bool).to_numpy()
            p90_dom = float(np.mean(actual_p90 < null_p90))
            mean_dom = float(np.mean(actual_mean < null_mean))
            null_strict_rate = float(np.mean(strict_null))
            mode_fields = {
                "null_p90_q20": float(np.quantile(null_p90, 0.20)),
                "null_p90_median": float(np.median(null_p90)),
                "null_p90_best": float(np.min(null_p90)),
            }
            mode_doms = []
            for mode, group in matched.groupby("mode"):
                g_p90 = group["pred_delta_vs_current_p90"].to_numpy(dtype=np.float64)
                dom = float(np.mean(actual_p90 < g_p90))
                mode_doms.append(dom)
                mode_fields[f"{mode}_p90_dominance"] = dom
                mode_fields[f"{mode}_null_strict_rate"] = float(group["strict_promote_gate"].astype(bool).mean())
            worst_mode_dom = float(min(mode_doms)) if mode_doms else 0.0
            placebo_gate = bool(
                bool(rec["strict_promote_gate"])
                and p90_dom >= 0.85
                and mean_dom >= 0.75
                and worst_mode_dom >= 0.65
                and null_strict_rate <= 0.10
                and actual_p90 <= mode_fields["null_p90_q20"] - 1.0e-6
            )
        public_lb = public_map.get(str(rec["basename"]), np.nan)
        known_public_worse = bool(pd.notna(public_lb) and public_lb >= public_map.get(CURRENT, np.inf))
        if known_public_worse:
            decision = "blocked_known_public_worse"
        elif not bool(rec["strict_promote_gate"]):
            decision = str(rec["promotion_decision"])
        elif not placebo_gate:
            decision = "blocked_by_matched_placebo"
        else:
            decision = "public_free_submission_candidate"
        records.append(
            {
                "basename": rec["basename"],
                "source_path": rec["source_path"],
                "candidate_id": rec["candidate_id"],
                "action": rec["action"],
                "fraction": float(rec["fraction"]),
                "rule_family": rec["rule_family"],
                "row_count": int(rec["row_count"]),
                "e247_overlap": int(rec["e247_overlap"]),
                "e256_overlap": int(rec["e256_overlap"]),
                "e284_overlap": int(rec["e284_overlap"]),
                "sum_smooth_gain": float(rec["sum_smooth_gain"]),
                "mean_amp": float(rec["mean_amp"]),
                "mean_app_state": float(rec["mean_app_state"]),
                "mean_app_story": float(rec["mean_app_story"]),
                "mean_state_amp_z": float(rec["mean_state_amp_z"]),
                "old_promotion_decision": rec["promotion_decision"],
                "old_strict_promote": bool(rec["strict_promote_gate"]),
                "actual_mean": actual_mean,
                "actual_p10": float(rec["pred_delta_vs_current_p10"]),
                "actual_p90": actual_p90,
                "actual_beats_current_rate": float(rec["pred_beats_current_rate"]),
                "incremental_bad_axis_vs_current": float(rec["incremental_bad_axis_vs_current"]),
                "null_count": int(len(matched)),
                "null_strict_rate": null_strict_rate,
                "p90_dominance": p90_dom,
                "mean_dominance": mean_dom,
                "worst_mode_p90_dominance": worst_mode_dom,
                "matched_placebo_gate": placebo_gate,
                "public_lb_if_known": public_lb,
                "known_public_worse_than_current": known_public_worse,
                "public_free_submission_ready": bool(decision == "public_free_submission_candidate"),
                "final_decision": decision,
                **mode_fields,
            }
        )
    out = pd.DataFrame(records).sort_values(
        ["public_free_submission_ready", "matched_placebo_gate", "old_strict_promote", "actual_p90", "p90_dominance"],
        ascending=[False, False, False, True, False],
    )
    out.to_csv(GOVERNOR_OUT, index=False)
    return out


def write_report(boundary: pd.DataFrame, cell_groups: pd.DataFrame, candidates: pd.DataFrame, governor: pd.DataFrame, selected: pd.DataFrame) -> None:
    ready = governor[governor["public_free_submission_ready"].astype(bool)] if not governor.empty else pd.DataFrame()
    old_strict = int(governor["old_strict_promote"].astype(bool).sum()) if not governor.empty else 0
    placebo_pass = int(governor["matched_placebo_gate"].astype(bool).sum()) if not governor.empty else 0
    undo = governor[governor["action"].eq("undo")] if not governor.empty else pd.DataFrame()
    add = governor[governor["action"].eq("add")] if not governor.empty else pd.DataFrame()
    gov_cols = [
        "basename",
        "candidate_id",
        "action",
        "fraction",
        "rule_family",
        "row_count",
        "final_decision",
        "old_promotion_decision",
        "actual_mean",
        "actual_p90",
        "null_strict_rate",
        "p90_dominance",
        "worst_mode_p90_dominance",
        "matched_placebo_gate",
    ]
    cand_cols = [
        "candidate_id",
        "action",
        "fraction",
        "rule_family",
        "row_count",
        "e247_overlap",
        "e256_overlap",
        "e284_overlap",
        "sum_smooth_gain",
        "mean_amp",
        "mean_app_state",
        "mean_app_story",
        "mean_state_amp_z",
    ]
    lines = [
        "# E285 E247-Residual Human-State Audit",
        "",
        "## Question",
        "",
        "Can human/social diary state produce an E247-relative preserve/undo/avoid rule, instead of using stale E224/E154 rollback targets?",
        "",
        "## Human Boundary Features",
        "",
        md_table(boundary, n=24),
        "",
        "## Cell Group Anatomy",
        "",
        md_table(cell_groups, n=12),
        "",
        "## Candidate Tensor Families",
        "",
        f"- materialized candidates: `{len(candidates)}`",
        f"- current-anchor selected models: `{len(selected)}`",
        f"- old strict-promote candidates: `{old_strict}`",
        f"- matched-placebo gate passes: `{placebo_pass}`",
        f"- public-free ready candidates: `{len(ready)}`",
        "",
        "### Candidate Anatomy",
        "",
        md_table(candidates.sort_values(["rule_family", "candidate_id"]), cand_cols, n=50) if not candidates.empty else "_empty_",
        "",
        "### Current-Anchor Governor",
        "",
        md_table(governor, gov_cols, n=50) if not governor.empty else "_empty_",
        "",
        "## Preserve / Undo Read",
        "",
    ]
    if len(undo):
        lines.extend(
            [
                f"- best undo actual p90: `{float(undo['actual_p90'].min()):.9f}`",
                f"- undo old strict-promote count: `{int(undo['old_strict_promote'].sum())}`",
                f"- undo matched-placebo pass count: `{int(undo['matched_placebo_gate'].sum())}`",
            ]
        )
    if len(add):
        lines.extend(
            [
                f"- best add actual p90: `{float(add['actual_p90'].min()):.9f}`",
                f"- add old strict-promote count: `{int(add['old_strict_promote'].sum())}`",
                f"- add matched-placebo pass count: `{int(add['matched_placebo_gate'].sum())}`",
            ]
        )
    lines.extend(["", "## Decision", ""])
    if len(ready):
        best = ready.iloc[0]
        lines.append(
            f"`{best['basename']}` survived the local governor. It needs manual review because it directly edits the current E247 body."
        )
    else:
        lines.append(
            "No E247-relative human-state residual candidate is submission-ready. This supports preserving the current E247 Q3 smoothing body until a stronger E247-specific target is learned."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The experiment deliberately avoided public LB. If undo candidates fail, that means current local sensors do not find a safe subset of E247 cells to remove. If add candidates fail, it means E247's public-positive body should not be extended with social/story-like cells by handcrafted rules.",
            "",
            "## Files",
            "",
            f"- `{BOUNDARY_OUT.name}`",
            f"- `{CELL_OUT.name}`",
            f"- `{CANDIDATE_OUT.name}`",
            f"- `{GOVERNOR_OUT.name}`",
            f"- `{SCORES_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows, boundary, cell_groups, current, e224, e154 = build_cell_table()
    specs = candidate_specs(rows, boundary)
    candidates = materialize_candidates(rows, specs, current, e224, e154)
    nulls = generate_nulls(candidates)
    scores, selected = score_current_anchor(candidates, nulls)
    governor = summarize_governor(scores, candidates, nulls)
    write_report(boundary, cell_groups, candidates, governor, selected)

    print(f"boundary_features={len(boundary)}")
    print(f"candidate_specs={len(specs)}")
    print(f"candidates={len(candidates)}")
    print(f"nulls={len(nulls)}")
    print(f"old_strict={int(governor['old_strict_promote'].sum()) if not governor.empty else 0}")
    print(f"matched_placebo={int(governor['matched_placebo_gate'].sum()) if not governor.empty else 0}")
    print(f"ready={int(governor['public_free_submission_ready'].sum()) if not governor.empty else 0}")
    if not governor.empty:
        cols = [
            "candidate_id",
            "action",
            "final_decision",
            "old_promotion_decision",
            "actual_p90",
            "null_strict_rate",
            "p90_dominance",
            "matched_placebo_gate",
        ]
        print(governor[cols].head(25).round(9).to_string(index=False))
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
