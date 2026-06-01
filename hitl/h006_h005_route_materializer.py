#!/usr/bin/env python3
"""H006: materialize H005 human-route hypotheses into sparse E247 edits.

H005 said many imported human/social hypotheses survive local subject/dateblock
stress, but that does not mean they are submission-ready.  This script tests
the next translation step:

    human-state route library -> tiny target-specific test movement

No public LB is used.  Candidates are scored by the existing public-free
selector anchored on the resolved E247 frontier.  The only candidates that get
an `_uploadsafe` copy are those that pass both selector and movement-shape
gates.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H006 = HITL / "h006_h005_route_materializer"
H006.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import h005_all_human_route_hypotheses as h005  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import KEYS, TARGETS, clip_prob, load_frames, md_table  # noqa: E402
from e295_episode_state_jepa_audit import build_episode_matrix  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


EPS = 1.0e-12
H005_DIR = HITL / "h005_all_human_route_hypotheses"
H005_TEST = H005_DIR / "h005_all_route_tests.csv"
H003_TINY = HITL / "h003_hs_jepa_prototype" / "submission_h003_semantic_tiny_11e7aa3b.csv"
E247 = OUT / CURRENT

CANDIDATE_OUT = H006 / "h006_candidates.csv"
COMPONENT_OUT = H006 / "h006_component_rows.csv"
SCORE_OUT = H006 / "h006_selector_scores.csv"
ANATOMY_OUT = H006 / "h006_candidate_anatomy.csv"
GATE_OUT = H006 / "h006_gate_scores.csv"
SELECTION_OUT = H006 / "h006_selection.csv"
REPORT_OUT = H006 / "h006_report.md"


ROUTE_SPECS: list[dict[str, Any]] = [
    {
        "candidate_id": "mobility_errand_s4s1q1_top18",
        "story": "errand/weekend mobility drains recovery: S4 up, S1/Q1 down",
        "components": [
            {
                "name": "errand_mobility",
                "hypothesis_ids": ["H0568", "H0562", "H0774"],
                "route_terms": [("S4", "up", 1.0), ("S1", "down", 1.0), ("Q1", "down", 1.0)],
                "top_k": 18,
                "amp": 0.0060,
            }
        ],
    },
    {
        "candidate_id": "weekend_obligation_s4q2s1_top18",
        "story": "weekend-looking obligation/commute is not rest: S4/Q2 up, S1 down",
        "components": [
            {
                "name": "weekend_obligation",
                "hypothesis_ids": ["H0704"],
                "route_terms": [("S4", "up", 1.0), ("Q2", "up", 1.0), ("S1", "down", 1.0)],
                "top_k": 18,
                "amp": 0.0060,
            }
        ],
    },
    {
        "candidate_id": "routine_anchor_q2s2q1_top18",
        "story": "routine anchor/recovery lowers intervention and improves Q1/S2",
        "components": [
            {
                "name": "routine_anchor",
                "hypothesis_ids": ["H0447"],
                "route_terms": [("Q2", "down", 1.0), ("S2", "up", 1.0), ("Q1", "up", 1.0)],
                "top_k": 18,
                "amp": 0.0050,
            }
        ],
    },
    {
        "candidate_id": "bedtime_decision_s3q1q2_top18",
        "story": "bedtime decision fatigue/arousal hurts S3/Q1 and raises Q2",
        "components": [
            {
                "name": "decision_fatigue",
                "hypothesis_ids": ["H0284"],
                "route_terms": [("S3", "down", 1.0), ("Q1", "down", 1.0), ("Q2", "up", 1.0)],
                "top_k": 18,
                "amp": 0.0050,
            }
        ],
    },
    {
        "candidate_id": "forced_commute_q3s4q1_top16",
        "story": "bad-night residue plus forced commute shifts Q3/S4 up and Q1 down",
        "components": [
            {
                "name": "forced_commute_after_badnight",
                "hypothesis_ids": ["H0094"],
                "route_terms": [("Q3", "up", 1.0), ("S4", "up", 1.0), ("Q1", "down", 1.0)],
                "top_k": 16,
                "amp": 0.0050,
            }
        ],
    },
    {
        "candidate_id": "vehicle_s4s1_top22",
        "story": "high-confidence vehicle/mobility exposure mostly changes S4/S1",
        "components": [
            {
                "name": "vehicle_exposure",
                "hypothesis_ids": ["H0646"],
                "route_terms": [("S4", "up", 1.0), ("S1", "down", 1.0)],
                "top_k": 22,
                "amp": 0.0060,
            }
        ],
    },
    {
        "candidate_id": "q2s2_recovery_only_top24",
        "story": "safe recovery-only slice: Q2 down and S2 up without broad Q/S side effects",
        "components": [
            {
                "name": "q2s2_recovery",
                "hypothesis_ids": ["H0447", "H0761"],
                "route_terms": [("Q2", "down", 1.0), ("S2", "up", 1.0)],
                "top_k": 24,
                "amp": 0.0055,
            }
        ],
    },
    {
        "candidate_id": "s4_mobility_only_top28",
        "story": "most conservative mobility read: only S4 on consensus mobility rows",
        "components": [
            {
                "name": "s4_mobility_consensus",
                "hypothesis_ids": ["H0704", "H0774", "H0646"],
                "route_terms": [("S4", "up", 1.0)],
                "top_k": 28,
                "amp": 0.0060,
            }
        ],
    },
    {
        "candidate_id": "balanced_routebook_tiny",
        "story": "tiny multi-story routebook: mobility, routine, and bedtime axes, each below usual movement scale",
        "components": [
            {
                "name": "mobility_tiny",
                "hypothesis_ids": ["H0568", "H0774"],
                "route_terms": [("S4", "up", 1.0), ("S1", "down", 1.0), ("Q1", "down", 1.0)],
                "top_k": 10,
                "amp": 0.0032,
            },
            {
                "name": "routine_tiny",
                "hypothesis_ids": ["H0447"],
                "route_terms": [("Q2", "down", 1.0), ("S2", "up", 1.0), ("Q1", "up", 1.0)],
                "top_k": 10,
                "amp": 0.0030,
            },
            {
                "name": "bedtime_tiny",
                "hypothesis_ids": ["H0284"],
                "route_terms": [("S3", "down", 1.0), ("Q1", "down", 1.0), ("Q2", "up", 1.0)],
                "top_k": 10,
                "amp": 0.0030,
            },
        ],
    },
]

for top_k, amp in [(20, 0.0080), (36, 0.0080), (50, 0.0060), (50, 0.0080)]:
    ROUTE_SPECS.append(
        {
            "candidate_id": f"s4_mobility_only_top{top_k}_amp{str(amp).replace('.', 'p')}",
            "story": "S4-only mobility scale ladder: test whether H005's cleanest social route has enough selector resolution",
            "components": [
                {
                    "name": "s4_mobility_consensus_scaled",
                    "hypothesis_ids": ["H0704", "H0774", "H0646"],
                    "route_terms": [("S4", "up", 1.0)],
                    "top_k": top_k,
                    "amp": amp,
                }
            ],
        }
    )

for top_k, amp in [(28, 0.0060), (36, 0.0080)]:
    ROUTE_SPECS.append(
        {
            "candidate_id": f"s4_mobility_down_control_top{top_k}_amp{str(amp).replace('.', 'p')}",
            "story": "S4-only mobility opposite-direction control",
            "components": [
                {
                    "name": "s4_mobility_opposite_control",
                    "hypothesis_ids": ["H0704", "H0774", "H0646"],
                    "route_terms": [("S4", "down", 1.0)],
                    "top_k": top_k,
                    "amp": amp,
                }
            ],
        }
    )


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def normalize_sample_keys(sample: pd.DataFrame) -> pd.DataFrame:
    out = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    return out.reset_index(drop=True)


def route_terms(spec_terms: list[tuple[str, str, float]]) -> list[h005.RouteTerm]:
    return [h005.RouteTerm(target=t, direction=d, strength=float(s)) for t, d, s in spec_terms]


def load_context() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, tuple[str, str]], pd.DataFrame]:
    if not H005_TEST.exists():
        raise FileNotFoundError(f"run H005 first: {H005_TEST}")
    h005_results = pd.read_csv(H005_TEST)
    base, _, _, feature_frames = load_frames()
    episodes, _ = build_episode_matrix(base, feature_frames)
    train_mask = base["split"].eq("train").to_numpy()
    pool = h005.build_feature_pool(feature_frames)
    z_features = h005.build_z_feature_matrix(base, feature_frames, pool, train_mask)
    return h005_results, base, episodes, pool, z_features


def component_score(
    comp: dict[str, Any],
    h005_results: pd.DataFrame,
    base: pd.DataFrame,
    episodes: pd.DataFrame,
    pool: dict[str, tuple[str, str]],
    z_features: pd.DataFrame,
    train_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    scores: list[np.ndarray] = []
    gates: list[np.ndarray] = []
    notes: list[str] = []
    local_deltas: list[float] = []
    matched_counts: list[int] = []
    for hyp_id in comp["hypothesis_ids"]:
        rows = h005_results[h005_results["hypothesis_id"].astype(str).eq(str(hyp_id))]
        if rows.empty:
            raise KeyError(f"missing H005 hypothesis id: {hyp_id}")
        hyp = rows.iloc[0]
        score, score_meta = h005.make_hypothesis_score(hyp, z_features, episodes, pool, train_mask)
        gate, gate_tags, gate_relaxed = h005.condition_gate(hyp, base, episodes, z_features, train_mask)
        scores.append(h005.rank01(score, train_mask))
        gates.append(gate)
        notes.append(f"{hyp_id}:{hyp['hidden_human_state']}:{gate_tags}:relaxed={gate_relaxed}")
        local_deltas.append(float(hyp.get("avg_delta", np.nan)))
        matched_counts.append(int(score_meta.get("matched_feature_count", 0)))
    score_all = np.mean(np.vstack(scores), axis=0)
    gate_all = np.any(np.vstack(gates), axis=0)
    meta = {
        "hypothesis_ids": ",".join(map(str, comp["hypothesis_ids"])),
        "hypothesis_notes": " | ".join(notes),
        "h005_best_avg_delta": float(np.nanmin(local_deltas)) if local_deltas else np.nan,
        "h005_mean_avg_delta": float(np.nanmean(local_deltas)) if local_deltas else np.nan,
        "matched_feature_count_sum": int(np.sum(matched_counts)),
    }
    return score_all, gate_all, meta


def select_test_rows(score_sorted: np.ndarray, gate_sorted: np.ndarray, top_k: int) -> tuple[np.ndarray, float]:
    eligible = np.asarray(gate_sorted, dtype=bool)
    if int(eligible.sum()) == 0:
        eligible = np.ones(len(score_sorted), dtype=bool)
    k = int(min(max(int(top_k), 1), int(eligible.sum())))
    eligible_idx = np.where(eligible)[0]
    order = eligible_idx[np.argsort(score_sorted[eligible_idx])]
    selected_idx = order[-k:]
    selected = np.zeros(len(score_sorted), dtype=bool)
    selected[selected_idx] = True
    cutoff = float(np.min(score_sorted[selected_idx])) if len(selected_idx) else np.nan
    return selected, cutoff


def apply_terms(move: np.ndarray, selected: np.ndarray, terms: list[h005.RouteTerm], amp: float) -> None:
    for term in terms:
        target_idx = TARGETS.index(term.target)
        sign = 1.0 if term.direction == "up" else -1.0
        move[selected, target_idx] += sign * float(term.strength) * float(amp)


def write_candidate(base_sub: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base_sub[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = H006 / f"submission_h006_{safe_id(candidate_id, 90)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_candidates(
    h005_results: pd.DataFrame,
    base: pd.DataFrame,
    episodes: pd.DataFrame,
    pool: dict[str, tuple[str, str]],
    z_features: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, list[Path]]:
    train_mask = base["split"].eq("train").to_numpy()
    test_unsorted = base.loc[~train_mask].copy()
    test_unsorted["_full_idx"] = test_unsorted.index.to_numpy(dtype=int)
    test = test_unsorted.sort_values(KEYS).reset_index(drop=True)
    full_idx_sorted = test["_full_idx"].to_numpy(dtype=int)
    sample = normalize_sample_keys(test[KEYS])
    base_sub = load_anchor_sub(E247, sample)
    base_prob = base_sub[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)

    candidate_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in ROUTE_SPECS:
        move = np.zeros_like(base_logit)
        for comp in spec["components"]:
            score_all, gate_all, comp_meta = component_score(comp, h005_results, base, episodes, pool, z_features, train_mask)
            score_test = score_all[full_idx_sorted]
            gate_test = gate_all[full_idx_sorted]
            selected, cutoff = select_test_rows(score_test, gate_test, int(comp["top_k"]))
            terms = route_terms(comp["route_terms"])
            apply_terms(move, selected, terms, float(comp["amp"]))
            component_rows.append(
                {
                    "candidate_id": spec["candidate_id"],
                    "component": comp["name"],
                    "story": spec["story"],
                    "route_key": "|".join(f"{t.target}_{t.direction}" for t in terms),
                    "top_k": int(comp["top_k"]),
                    "amp": float(comp["amp"]),
                    "selected_rows": int(selected.sum()),
                    "eligible_rows": int(gate_test.sum()),
                    "score_cutoff": cutoff,
                    "selected_score_mean": float(np.mean(score_test[selected])) if int(selected.sum()) else np.nan,
                    "selected_score_min": float(np.min(score_test[selected])) if int(selected.sum()) else np.nan,
                    "selected_score_max": float(np.max(score_test[selected])) if int(selected.sum()) else np.nan,
                    **comp_meta,
                }
            )

        logits = base_logit + move
        path = write_candidate(base_sub, logits, str(spec["candidate_id"]))
        paths.append(path)
        changed_by_target = {target: int((np.abs(move[:, idx]) > EPS).sum()) for idx, target in enumerate(TARGETS)}
        active_targets = [target for target, count in changed_by_target.items() if count > 0]
        candidate_rows.append(
            {
                "candidate_id": spec["candidate_id"],
                "story": spec["story"],
                "file": rel(path),
                "basename": path.name,
                "active_targets": ",".join(active_targets),
                "n_active_targets": len(active_targets),
                "changed_rows": int(np.any(np.abs(move) > EPS, axis=1).sum()),
                "changed_cells": int(np.sum(np.abs(move) > EPS)),
                "mean_abs_logit_move": float(np.mean(np.abs(move))),
                "l1_logit_move": float(np.sum(np.abs(move))),
                "max_abs_logit_move": float(np.max(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(clip_prob(sigmoid(logits)) - base_prob))),
                **{f"changed_{target}": changed_by_target[target] for target in TARGETS},
            }
        )
    return pd.DataFrame(candidate_rows), pd.DataFrame(component_rows), paths


def score_new_candidates(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [str(path.resolve()) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    base = load_anchor_sub(E247, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    h003_move = None
    if H003_TINY.exists():
        h003 = load_anchor_sub(H003_TINY, sample)
        h003_move = logit(h003[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_anchor_sub(path, sample)
        prob = cand[TARGETS].to_numpy(dtype=np.float64)
        move = logit(prob) - base_logit
        rec: dict[str, Any] = {
            "file": rel(path),
            "basename": path.name,
            "changed_rows_vs_current": int((np.abs(move).max(axis=1) > EPS).sum()),
            "changed_cells_vs_current": int((np.abs(move) > EPS).sum()),
            "mean_abs_logit_delta_vs_current": float(np.mean(np.abs(move))),
            "l1_logit_delta_vs_current": float(np.sum(np.abs(move))),
            "max_abs_logit_delta_vs_current": float(np.max(np.abs(move))),
            "max_abs_prob_delta_vs_current": float(np.max(np.abs(prob - base_prob))),
        }
        for ti, target in enumerate(TARGETS):
            rec[f"changed_{target}"] = int((np.abs(move[:, ti]) > EPS).sum())
        if h003_move is not None:
            denom = float(np.linalg.norm(move) * np.linalg.norm(h003_move) + EPS)
            rec["cos_delta_with_h003_tiny"] = float(np.sum(move * h003_move) / denom)
            rec["l1_ratio_to_h003_tiny"] = float(np.sum(np.abs(move)) / (np.sum(np.abs(h003_move)) + EPS))
        rows.append(rec)
    return pd.DataFrame(rows).sort_values(["l1_logit_delta_vs_current", "basename"]).reset_index(drop=True)


def build_gate_scores(candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame) -> pd.DataFrame:
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "strict_promote_gate",
        "info_sensor_gate",
        "below_resolution_gate",
        "block_gate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
    ]
    present_score_cols = [col for col in score_cols if col in scores.columns]
    merged = candidates.merge(scores[present_score_cols], on="basename", how="left")
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    present_anatomy_cols = [col for col in anatomy_cols if col in anatomy.columns]
    merged = merged.merge(anatomy[present_anatomy_cols], on="basename", how="left")
    ratio = merged.get("l1_ratio_to_h003_tiny", pd.Series(0.0, index=merged.index)).fillna(0.0)
    merged["shape_gate"] = (
        (merged["n_active_targets"] <= 3)
        & (merged["changed_cells"] <= 90)
        & (merged["max_abs_prob_delta"] <= 0.0020)
        & (ratio <= 0.25)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.020)
    )
    merged["h006_strict_upload_gate"] = merged["shape_gate"] & merged["strict_promote_gate"].fillna(False).astype(bool)
    merged["h006_info_gate"] = merged["shape_gate"] & (
        merged["info_sensor_gate"].fillna(False).astype(bool)
        | (
            (merged["pred_delta_vs_current_mean"] < 0.0)
            & (merged["pred_beats_current_rate"] >= 0.55)
            & (merged["incremental_bad_axis_vs_current"].abs() <= 0.025)
        )
    )
    merged["h006_decision"] = np.select(
        [
            merged["h006_strict_upload_gate"],
            merged["h006_info_gate"] & ~merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["h006_info_gate"] & merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["shape_gate"],
        ],
        [
            "uploadsafe_candidate",
            "diagnostic_public_sensor_only",
            "too_small_to_submit",
            "shape_ok_but_selector_rejects",
        ],
        default="reject_shape_or_bad_axis",
    )
    return merged.sort_values(
        ["h006_strict_upload_gate", "h006_info_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)


def write_uploadsafe_files(gate_scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in gate_scores[gate_scores["h006_strict_upload_gate"].astype(bool)].to_dict("records"):
        src = ROOT / str(rec["file"])
        if not src.exists():
            src = H006 / str(rec["basename"])
        dst = H006 / src.name.replace(".csv", "_uploadsafe.csv")
        shutil.copyfile(src, dst)
        rows.append(
            {
                "candidate_id": rec["candidate_id"],
                "basename": dst.name,
                "file": rel(dst),
                "reason": "passed H006 strict selector + movement-shape gate",
            }
        )
    return pd.DataFrame(rows)


def write_report(
    candidates: pd.DataFrame,
    components: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
    gate_scores: pd.DataFrame,
    selection: pd.DataFrame,
) -> None:
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    gate_cols = [
        "candidate_id",
        "h006_decision",
        "active_targets",
        "changed_rows",
        "changed_cells",
        "max_abs_prob_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "shape_gate",
        "h006_strict_upload_gate",
        "h006_info_gate",
        "basename",
    ]
    comp_cols = [
        "candidate_id",
        "component",
        "route_key",
        "selected_rows",
        "eligible_rows",
        "amp",
        "h005_best_avg_delta",
        "h005_mean_avg_delta",
        "matched_feature_count_sum",
    ]
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    lines = [
        "# H006 H005 Route Materializer",
        "",
        "## Question",
        "",
        "Can the strongest H005 human-state route families be translated into sparse, public-free-safe E247 edits?",
        "",
        "## Method",
        "",
        "- Rebuild each selected H005 state score on train+test without public LB.",
        "- Rank test rows by the human-state score and move only a tiny set of rows.",
        "- Apply only the declared target route, with 1-3 targets per candidate.",
        "- Promote only if both selector and movement-shape gates pass.",
        "",
        "## Candidate Gate",
        "",
        md_table(gate_scores[[col for col in gate_cols if col in gate_scores.columns]], n=40, floatfmt=".9f"),
        "",
        "## Selector Scores",
        "",
        md_table(scores[[col for col in score_cols if col in scores.columns]], n=40, floatfmt=".9f"),
        "",
        "## Component Rows",
        "",
        md_table(components[comp_cols], n=40, floatfmt=".9f"),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[[col for col in anatomy_cols if col in anatomy.columns]], n=40, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=20, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    strict_n = int(gate_scores["h006_strict_upload_gate"].sum())
    info_n = int(gate_scores["h006_info_gate"].sum())
    if strict_n:
        best = gate_scores[gate_scores["h006_strict_upload_gate"].astype(bool)].iloc[0]
        lines.append(
            f"`{strict_n}` candidate(s) passed the strict gate. Best upload-safe bet: `{best['basename']}`."
        )
    elif info_n:
        best = gate_scores[gate_scores["h006_info_gate"].astype(bool)].iloc[0]
        lines.append(
            f"No candidate passed strict upload gate. `{best['basename']}` is the best diagnostic sensor, but not submission-grade by the current public-free rule."
        )
    else:
        lines.append(
            "No H005 route translation passed the H006 selector gate. This weakens direct story-to-submission translation and keeps H005 as a feature/latent guide rather than a final postprocess."
        )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(COMPONENT_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(ANATOMY_OUT)}`",
            f"- `{rel(GATE_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    h005_results, base, episodes, pool, z_features = load_context()
    candidates, components, paths = materialize_candidates(h005_results, base, episodes, pool, z_features)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths)
    gate_scores = build_gate_scores(candidates, scores, anatomy)
    selection = write_uploadsafe_files(gate_scores)

    candidates.to_csv(CANDIDATE_OUT, index=False)
    components.to_csv(COMPONENT_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    gate_scores.to_csv(GATE_OUT, index=False)
    selection.to_csv(SELECTION_OUT, index=False)
    write_report(candidates, components, scores, anatomy, gate_scores, selection)

    print(f"report={rel(REPORT_OUT)}")
    print("[h006 gate]")
    cols = [
        "candidate_id",
        "h006_decision",
        "active_targets",
        "changed_cells",
        "max_abs_prob_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "basename",
    ]
    print(gate_scores[cols].round(9).to_string(index=False))
    if not selection.empty:
        print("[uploadsafe]")
        print(selection.to_string(index=False))


if __name__ == "__main__":
    main()
