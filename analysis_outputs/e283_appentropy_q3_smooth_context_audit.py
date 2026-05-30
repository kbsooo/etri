#!/usr/bin/env python3
"""E283: app-entropy conditioned Q3 feature-NN smoothing audit.

E247 is the current public best and the strongest "JEPA as mechanism" result:
Q3 rollback cells were selected by broad feature-nearest-neighbor smoothing.
E281/E282 say app-entropy is a real human/social story-state, but simple Q3
logit shifts collapse into generic prior movement.

This experiment tests the intersection:

    Does app-entropy help choose *which* E247-style Q3 smoothing cells to trust?

No public LB is used. A candidate must preserve E246/E237-like local geometry
and then beat matched row/subject/dateblock nulls versus the current E247
public anchor.
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
NULL_DIR = OUT / "e283_appentropy_q3_smooth_context_nulls"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

import e246_feature_nn1_smoothing_selector_ablation as e246  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
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
RNG_SEED = 20260531 + 283
N_REPS = 11

ROWS_IN = OUT / "e246_feature_nn1_smoothing_selector_rows.csv"
E246_SUMMARY_IN = OUT / "e246_feature_nn1_smoothing_selector_summary.csv"
STATE_IN = OUT / "e282_appentropy_story_state.csv"

GROUP_OUT = OUT / "e283_appentropy_q3_smooth_context_group_summary.csv"
LOCAL_SUMMARY_OUT = OUT / "e283_appentropy_q3_smooth_context_local_summary.csv"
CANDIDATE_SUMMARY_OUT = OUT / "e283_appentropy_q3_smooth_context_candidate_summary.csv"
NULLS_OUT = OUT / "e283_appentropy_q3_smooth_context_nulls.csv"
SCORES_OUT = OUT / "e283_appentropy_q3_smooth_context_scores.csv"
SUMMARY_OUT = OUT / "e283_appentropy_q3_smooth_context_summary.csv"
REPORT_OUT = OUT / "e283_appentropy_q3_smooth_context_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


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


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def zscore(values: pd.Series | np.ndarray) -> pd.Series:
    vals = pd.Series(values, dtype=float)
    mu = float(vals.mean())
    sd = float(vals.std(ddof=0))
    if sd < 1.0e-12:
        return pd.Series(np.zeros(len(vals)), index=vals.index)
    return (vals - mu) / sd


def parse_idx(text: str) -> np.ndarray:
    if not str(text).strip():
        return np.asarray([], dtype=int)
    return np.asarray([int(x) for x in str(text).split()], dtype=int)


def topk(rows: pd.DataFrame, score: pd.Series | np.ndarray, k: int) -> np.ndarray:
    ordered = rows.assign(_score=pd.Series(score, index=rows.index).astype(float)).sort_values(
        ["_score", "row_idx"], ascending=[False, True]
    )
    return ordered.head(k)["row_idx"].to_numpy(dtype=int)


def refill(base: set[int], remove: set[int], pool_order: list[int], k: int) -> np.ndarray:
    selected = [idx for idx in sorted(base) if idx not in remove]
    seen = set(selected)
    for idx in pool_order:
        if len(selected) >= k:
            break
        if idx in seen:
            continue
        selected.append(int(idx))
        seen.add(int(idx))
    return np.asarray(sorted(selected), dtype=int)


def load_rows_with_state() -> pd.DataFrame:
    if not ROWS_IN.exists() or not E246_SUMMARY_IN.exists():
        e246.main()
    rows = pd.read_csv(ROWS_IN).sort_values("row_idx").reset_index(drop=True)
    state = pd.read_csv(STATE_IN)
    test_state = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    if len(test_state) != len(rows):
        raise RuntimeError("E282 test state length does not align with E246 row table")
    rows["app_state_avg_z"] = test_state["state_avg_z"].to_numpy(dtype=np.float64)
    rows["app_state_subject_z"] = test_state["state_subject_z"].to_numpy(dtype=np.float64)
    rows["app_state_dateblock_z"] = test_state["state_dateblock_z"].to_numpy(dtype=np.float64)
    rows["app_story_score"] = test_state["story_score_actual"].to_numpy(dtype=np.float64)
    rows["app_state_rank"] = rows["app_state_avg_z"].rank(pct=True)
    rows["app_story_rank"] = rows["app_story_score"].rank(pct=True)
    rows["state_x_amp"] = zscore(rows["app_state_avg_z"]).to_numpy() * zscore(rows["rollback_amp_abs"]).to_numpy()
    rows["story_x_amp"] = zscore(rows["app_story_score"]).to_numpy() * zscore(rows["rollback_amp_abs"]).to_numpy()
    rows["smooth_z"] = zscore(rows["single_row_smooth_gain_sum"]).to_numpy()
    rows["amp_z"] = zscore(rows["rollback_amp_abs"]).to_numpy()
    rows["state_z"] = zscore(rows["app_state_avg_z"]).to_numpy()
    rows["story_z"] = zscore(rows["app_story_score"]).to_numpy()
    return rows


def e246_selector(summary: pd.DataFrame, selector_id: str) -> np.ndarray:
    hit = summary[summary["candidate_id"].eq(selector_id)]
    if hit.empty:
        raise RuntimeError(f"missing E246 selector: {selector_id}")
    return parse_idx(hit.iloc[0]["row_idx_list"])


def group_summary(rows: pd.DataFrame) -> pd.DataFrame:
    summary = pd.read_csv(E246_SUMMARY_IN)
    e247 = set(e246_selector(summary, "nn_smooth_sum_top34").tolist())
    e256 = set(e246_selector(summary, "top50_amp_then_smooth25").tolist())
    labels = []
    for _, rec in rows.iterrows():
        idx = int(rec["row_idx"])
        if idx in e247 and idx in e256:
            group = "e247_e256_common"
        elif idx in e247:
            group = "e247_only"
        elif idx in e256:
            group = "e256_only"
        else:
            group = "neither"
        labels.append(group)
    rows = rows.copy()
    rows["e247_e256_group"] = labels
    metrics = [
        "app_state_avg_z",
        "app_story_score",
        "single_row_smooth_gain_sum",
        "rollback_amp_abs",
        "state_x_amp",
        "story_x_amp",
        "nn_dist",
    ]
    out_rows: list[dict[str, object]] = []
    for group, part in rows.groupby("e247_e256_group"):
        rec: dict[str, object] = {
            "group": group,
            "n_rows": int(len(part)),
            "e237_overlap": int(part["e237_drop"].astype(bool).sum()),
            "e230_swing_overlap": int(part["e230_swing25"].astype(bool).sum()),
            "e230_risk_overlap": int(part["e230_risk21"].astype(bool).sum()),
        }
        for metric in metrics:
            vals = part[metric].astype(float)
            rec[f"{metric}_mean"] = float(vals.mean())
            rec[f"{metric}_median"] = float(vals.median())
        rec["app_state_high80_rate"] = float((part["app_state_rank"] >= 0.80).mean())
        rec["app_story_high80_rate"] = float((part["app_story_rank"] >= 0.80).mean())
        out_rows.append(rec)
    out = pd.DataFrame(out_rows).sort_values("group").reset_index(drop=True)
    out.to_csv(GROUP_OUT, index=False)
    return out


def candidate_specs(rows: pd.DataFrame) -> list[dict[str, Any]]:
    summary = pd.read_csv(E246_SUMMARY_IN)
    e247 = set(e246_selector(summary, "nn_smooth_sum_top34").tolist())
    e256 = set(e246_selector(summary, "top50_amp_then_smooth25").tolist())
    smooth_order = topk(rows, rows["single_row_smooth_gain_sum"], len(rows)).tolist()
    specs: list[dict[str, Any]] = [
        {
            "selector_id": "control_e247_nn_smooth_sum_top34",
            "rule_family": "control",
            "row_idx": np.asarray(sorted(e247), dtype=int),
            "rule_note": "current E247 selected row set",
        },
        {
            "selector_id": "control_e256_top50_amp_then_smooth25",
            "rule_family": "control_known_public_worse",
            "row_idx": np.asarray(sorted(e256), dtype=int),
            "rule_note": "E256 public-worse selected row set",
        },
    ]

    for k in [25, 34]:
        for beta in [-0.75, -0.40, -0.20, 0.20, 0.40, 0.75]:
            score = rows["smooth_z"] + beta * rows["state_z"]
            tag = str(beta).replace("-", "m").replace(".", "p")
            specs.append(
                {
                    "selector_id": f"state_score_b{tag}_top{k}",
                    "rule_family": "appentropy_score",
                    "row_idx": topk(rows, score, k),
                    "rule_note": f"smooth z-score plus {beta:+.2f} * predicted app-entropy state z, top{k}",
                }
            )
        for beta in [-0.50, 0.50]:
            score = rows["smooth_z"] + beta * rows["story_z"]
            tag = str(beta).replace("-", "m").replace(".", "p")
            specs.append(
                {
                    "selector_id": f"story_score_b{tag}_top{k}",
                    "rule_family": "appentropy_story_score",
                    "row_idx": topk(rows, score, k),
                    "rule_note": f"smooth z-score plus {beta:+.2f} * raw app-entropy story z, top{k}",
                }
            )

    for lo, hi, name in [(0.0, 0.60, "lowmid"), (0.20, 0.80, "mid"), (0.40, 1.0, "midhigh")]:
        pool = rows[(rows["app_state_rank"] >= lo) & (rows["app_state_rank"] <= hi)].copy()
        if len(pool) >= 34:
            specs.append(
                {
                    "selector_id": f"state_band_{name}_smooth_top34",
                    "rule_family": "appentropy_band",
                    "row_idx": topk(pool, pool["single_row_smooth_gain_sum"], 34),
                    "rule_note": f"top34 smooth rows inside predicted app-state rank band {lo:.1f}-{hi:.1f}",
                }
            )
    for lo, hi, name in [(0.0, 0.60, "story_lowmid"), (0.20, 0.80, "story_mid"), (0.40, 1.0, "story_midhigh")]:
        pool = rows[(rows["app_story_rank"] >= lo) & (rows["app_story_rank"] <= hi)].copy()
        if len(pool) >= 34:
            specs.append(
                {
                    "selector_id": f"{name}_smooth_top34",
                    "rule_family": "appentropy_story_band",
                    "row_idx": topk(pool, pool["single_row_smooth_gain_sum"], 34),
                    "rule_note": f"top34 smooth rows inside raw app-story rank band {lo:.1f}-{hi:.1f}",
                }
            )

    e247_part = rows[rows["row_idx"].isin(e247)].copy()
    for metric, label in [("app_state_avg_z", "state"), ("app_story_score", "story"), ("state_x_amp", "stateamp")]:
        for side, ascending in [("high", False), ("low", True)]:
            ordered = e247_part.sort_values([metric, "row_idx"], ascending=[ascending, True])
            for n_remove in [3, 5, 8]:
                remove = set(ordered.head(n_remove)["row_idx"].astype(int).tolist())
                row_idx = refill(e247, remove, smooth_order, 34)
                specs.append(
                    {
                        "selector_id": f"e247_drop_{side}_{label}{n_remove}_refill",
                        "rule_family": "e247_appentropy_refill",
                        "row_idx": row_idx,
                        "rule_note": f"remove {n_remove} E247 rows with {side} {metric}, refill by smooth order",
                    }
                )

    # Penalize the E256 failure mode: high amplitude combined with high app-entropy.
    for beta in [0.25, 0.50, 0.75, 1.00]:
        score = rows["smooth_z"] - beta * pd.Series(np.maximum(rows["state_x_amp"], 0.0), index=rows.index)
        tag = str(beta).replace(".", "p")
        specs.append(
            {
                "selector_id": f"avoid_high_state_amp_b{tag}_top34",
                "rule_family": "appentropy_amp_penalty",
                "row_idx": topk(rows, score, 34),
                "rule_note": f"top34 by smooth score penalizing positive state*amplitude interaction beta={beta:.2f}",
            }
        )

    dedup: dict[tuple[int, ...], dict[str, Any]] = {}
    for spec in specs:
        row_idx = np.asarray(sorted(set(np.asarray(spec["row_idx"], dtype=int).tolist())), dtype=int)
        spec = dict(spec)
        spec["row_idx"] = row_idx
        key = tuple(row_idx.tolist())
        if key not in dedup:
            dedup[key] = spec
    return list(dedup.values())


def materialize(sample: pd.DataFrame, pred: np.ndarray, selector_id: str) -> Path:
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    digest = short_hash(out)
    safe_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in selector_id)[:70]
    path = OUT / f"submission_e283_appentropy_q3smooth_{safe_id}_{digest}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(rows: pd.DataFrame, local_summary: pd.DataFrame) -> pd.DataFrame:
    sample = load_sub(CURRENT).sort_values(KEYS).reset_index(drop=True)
    e154 = e230.load_prob(e230.E154_FILE, sample)
    e224 = e230.load_prob(e230.E224_FILE, sample)
    current = load_sub(CURRENT, sample)
    current_prob = current[TARGETS].to_numpy(dtype=np.float64)
    records: list[dict[str, object]] = []
    candidate_paths: list[Path] = []

    for _, rec in local_summary.iterrows():
        selector_id = str(rec["candidate_id"])
        if selector_id == "control_e247_nn_smooth_sum_top34":
            continue
        row_idx = parse_idx(str(rec["row_idx_list"]))
        pred = e246.apply_q3_drop(e224, e154, row_idx)
        if np.max(np.abs(pred - current_prob)) < 1.0e-12:
            continue
        path = materialize(sample, pred, selector_id)
        candidate_paths.append(path)
        selected_rows = rows[rows["row_idx"].isin(set(row_idx.tolist()))].copy()
        records.append(
            {
                "basename": path.name,
                "source_path": rel(path),
                "selector_id": selector_id,
                "rule_family": rec["rule_family"],
                "row_count": int(len(row_idx)),
                "row_idx_list": " ".join(map(str, row_idx.tolist())),
                "mean_app_state": float(selected_rows["app_state_avg_z"].mean()),
                "mean_app_story": float(selected_rows["app_story_score"].mean()),
                "mean_smooth_gain": float(selected_rows["single_row_smooth_gain_sum"].mean()),
                "sum_smooth_gain": float(selected_rows["single_row_smooth_gain_sum"].sum()),
                "mean_amp": float(selected_rows["rollback_amp_abs"].mean()),
                "e247_overlap": int(len(set(row_idx.tolist()) & set(parse_idx(local_summary.loc[local_summary["candidate_id"].eq("control_e247_nn_smooth_sum_top34"), "row_idx_list"].iloc[0]).tolist()))),
                "e246_e237_like_gate": bool(rec["e237_like_gate"]),
                "e246_score": float(rec["e237_like_score"]),
                "expected_loss_vs_e224": float(rec["expected_loss_vs_e224"]),
                "adverse_reduction_vs_e224": float(rec["adverse_reduction_vs_e224"]),
                "actual_adverse_reduction_vs_e224": float(rec["actual_adverse_reduction_vs_e224"]),
            }
        )
    out = pd.DataFrame(records)
    out.to_csv(CANDIDATE_SUMMARY_OUT, index=False)
    return out


def test_meta(sample: pd.DataFrame) -> pd.DataFrame:
    state = pd.read_csv(STATE_IN)
    meta = state[state["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    out = meta[KEYS + ["dateblock_group"]].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    sample_norm = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        sample_norm[col] = pd.to_datetime(sample_norm[col])
    if not out[KEYS].reset_index(drop=True).equals(sample_norm.reset_index(drop=True)):
        raise RuntimeError("E283 metadata does not align with current submission keys")
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
    path = NULL_DIR / f"submission_e283null_{stem}_{mode}_r{rep}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def generate_nulls(candidates: pd.DataFrame) -> pd.DataFrame:
    NULL_DIR.mkdir(exist_ok=True)
    base = load_sub(CURRENT)
    base_logits = logit(base[TARGETS].to_numpy(dtype=np.float64))
    meta = test_meta(base[KEYS])
    rows: list[dict[str, object]] = []
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
                rows.append(
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
    nulls = pd.DataFrame(rows)
    nulls.to_csv(NULLS_OUT, index=False)
    return nulls


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
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    paths = [OUT / CURRENT]
    paths.extend(ROOT / str(path) for path in candidates["source_path"].tolist())
    paths.extend(ROOT / str(path) for path in nulls["null_path"].tolist())
    feats = feature_rows(paths, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, feats, model_df)
    scores.to_csv(SCORES_OUT, index=False)
    return scores, selected_models(model_df)


def summarize_current_anchor(scores: pd.DataFrame, candidates: pd.DataFrame, nulls: pd.DataFrame) -> pd.DataFrame:
    actual = scores.merge(candidates, on=["basename", "source_path"], how="inner")
    null_scores = scores.merge(nulls, left_on="source_path", right_on="null_path", how="inner")
    public_map = known_public_table().set_index("file")["public_lb"].to_dict()
    rows: list[dict[str, object]] = []
    for _, rec in actual.iterrows():
        base_name = str(rec["basename"])
        matched = null_scores[null_scores["source_basename"].eq(base_name)].copy()
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

        public_lb = public_map.get(base_name, np.nan)
        known_public_worse = bool(pd.notna(public_lb) and public_lb >= public_map.get(CURRENT, np.inf))
        if known_public_worse:
            decision = "blocked_known_public_worse"
        elif not bool(rec["e246_e237_like_gate"]):
            decision = "blocked_by_e246_local_geometry"
        elif not bool(rec["strict_promote_gate"]):
            decision = str(rec["promotion_decision"])
        elif not placebo_gate:
            decision = "blocked_by_matched_placebo"
        else:
            decision = "public_free_submission_candidate"
        rows.append(
            {
                "basename": base_name,
                "source_path": rec["source_path"],
                "selector_id": rec["selector_id"],
                "rule_family": rec["rule_family"],
                "row_count": int(rec["row_count"]),
                "e247_overlap": int(rec["e247_overlap"]),
                "mean_app_state": float(rec["mean_app_state"]),
                "mean_app_story": float(rec["mean_app_story"]),
                "sum_smooth_gain": float(rec["sum_smooth_gain"]),
                "mean_amp": float(rec["mean_amp"]),
                "e246_e237_like_gate": bool(rec["e246_e237_like_gate"]),
                "e246_score": float(rec["e246_score"]),
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
    out = pd.DataFrame(rows).sort_values(
        ["public_free_submission_ready", "matched_placebo_gate", "old_strict_promote", "actual_p90", "p90_dominance"],
        ascending=[False, False, False, True, False],
    )
    out.to_csv(SUMMARY_OUT, index=False)
    return out


def write_report(group: pd.DataFrame, local_summary: pd.DataFrame, candidates: pd.DataFrame, summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    ready = summary[summary["public_free_submission_ready"].astype(bool)] if not summary.empty else pd.DataFrame()
    local_gate = local_summary[local_summary["e237_like_gate"].astype(bool)].copy() if not local_summary.empty else pd.DataFrame()
    old_strict = int(summary["old_strict_promote"].astype(bool).sum()) if not summary.empty else 0
    placebo_pass = int(summary["matched_placebo_gate"].astype(bool).sum()) if not summary.empty else 0
    lines = [
        "# E283 App-Entropy Q3 Smooth Context Audit",
        "",
        "## Question",
        "",
        "Does the validated human/social app-entropy state help select public-positive E247-style Q3 feature-NN smoothing cells?",
        "",
        "## Group Anatomy",
        "",
        md_table(group, n=20),
        "",
        "## Local E246/E237 Geometry",
        "",
        f"- selectors tested: `{len(local_summary)}`",
        f"- local E237-like gate passes: `{len(local_gate)}`",
        "",
        md_table(
            local_summary[
                [
                    "candidate_id",
                    "rule_family",
                    "pruned_cells",
                    "selected_smooth_gain_sum",
                    "selected_amp_mean",
                    "expected_loss_vs_e224",
                    "adverse_reduction_vs_e224",
                    "actual_adverse_reduction_vs_e224",
                    "overlap_e237",
                    "e237_like_gate",
                    "e237_like_score",
                ]
            ].sort_values(["e237_like_gate", "e237_like_score"], ascending=[False, False]),
            n=35,
        ),
        "",
        "## Current-Anchor Governor",
        "",
        f"- materialized non-current candidates: `{len(candidates)}`",
        f"- selected public-anchor models: `{len(selected)}`",
        f"- old strict-promote candidates: `{old_strict}`",
        f"- matched-placebo gate passes: `{placebo_pass}`",
        f"- public-free submission-ready candidates: `{len(ready)}`",
        "",
        md_table(
            summary[
                [
                    "basename",
                    "selector_id",
                    "final_decision",
                    "rule_family",
                    "e247_overlap",
                    "mean_app_state",
                    "mean_app_story",
                    "old_promotion_decision",
                    "actual_mean",
                    "actual_p90",
                    "null_strict_rate",
                    "p90_dominance",
                    "worst_mode_p90_dominance",
                    "matched_placebo_gate",
                ]
            ],
            n=45,
        )
        if not summary.empty
        else "_empty_",
        "",
        "## Decision",
        "",
    ]
    if len(ready):
        best = ready.iloc[0]
        lines.append(
            f"`{best['basename']}` survived the local governor. It should be reviewed manually before any public slot because it changes the current E247 mechanism using app-entropy-conditioned cell selection."
        )
    else:
        lines.append(
            "No app-entropy-conditioned Q3 smoothing selector is submission-ready. App-entropy explains some E247/E256 cell anatomy, but it does not currently improve the public-positive E247 mechanism in a placebo-resistant way."
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The useful human/social state is not dead, but this audit separates two roles. App-entropy can describe lifestyle context around Q3 cells, while E247's public win still comes from feature-neighbor smoothing geometry. Replacing or refilling E247 cells by app-entropy criteria is not yet certified.",
            "",
            "## Files",
            "",
            f"- `{GROUP_OUT.name}`",
            f"- `{LOCAL_SUMMARY_OUT.name}`",
            f"- `{CANDIDATE_SUMMARY_OUT.name}`",
            f"- `{SUMMARY_OUT.name}`",
            f"- `{SCORES_OUT.name}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = load_rows_with_state()
    group = group_summary(rows)
    specs = candidate_specs(rows)
    local_summary, _target_df, _overlap = e246.audit_specs(rows, specs)
    local_summary = local_summary.sort_values(["e237_like_gate", "e237_like_score"], ascending=[False, False])
    local_summary.to_csv(LOCAL_SUMMARY_OUT, index=False)
    candidates = materialize_candidates(rows, local_summary)
    nulls = generate_nulls(candidates) if len(candidates) else pd.DataFrame()
    if len(candidates):
        scores, selected = score_current_anchor(candidates, nulls)
        summary = summarize_current_anchor(scores, candidates, nulls)
    else:
        selected = pd.DataFrame()
        summary = pd.DataFrame()
    write_report(group, local_summary, candidates, summary, selected)

    print(f"selectors={len(local_summary)}")
    print(f"local_gate={int(local_summary['e237_like_gate'].sum()) if len(local_summary) else 0}")
    print(f"candidates={len(candidates)}")
    print(f"ready={int(summary['public_free_submission_ready'].sum()) if not summary.empty else 0}")
    if not summary.empty:
        cols = [
            "selector_id",
            "final_decision",
            "old_promotion_decision",
            "actual_p90",
            "null_strict_rate",
            "p90_dominance",
            "matched_placebo_gate",
        ]
        print(summary[cols].head(25).round(9).to_string(index=False))
    print(f"report={REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
