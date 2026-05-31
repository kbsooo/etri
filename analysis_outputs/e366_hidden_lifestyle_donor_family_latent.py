#!/usr/bin/env python3
"""E366: hidden lifestyle-state donor-family latent stress.

Question:
    E365 says a donor-graft family around Q3/S1 is locally more public-like
    than the earlier target-scale point.  Is that family a real hidden
    lifestyle-state representation, or just one lucky file?

JEPA/data2vec translation:
    context views = E328/E358 row lifestyle latent, public-good/bad row-state
                    clusters, and human/social story tails
    target view   = robust candidate action-health and known-public movement
                    survival, not raw lifelog reconstruction
    prediction    = a row-wise donor-family latent action: which source member
                    should a hidden lifestyle state trust for each row?

The generated candidates are not leaderboard blends.  They are family-center
and row-state-gated reconstructions of the E365 donor-graft support set.
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
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e357_public_survival_contrast_latent import (  # noqa: E402
    KEY,
    TARGETS,
    add_axis_features,
    align_delta,
    feature_columns as movement_feature_columns,
    load_known,
    locate,
    logit_frame,
    make_axes,
    movement_features,
    safe_spearman,
)
from e358_rowstate_public_survival_audit import load_anchor, load_row_state, rowstate_features  # noqa: E402
from e359_rowplacement_action_health_probe import clip_prob, load_source, logit, row_state_scores, selector_scores, sigmoid  # noqa: E402
from e360_learned_row_action_health_generator import rowstate_public_scores  # noqa: E402
from e363_cell_action_robustness_probe import add_e363_scores  # noqa: E402
from e364_public_like_cellaction_calibration import public_axis_summaries  # noqa: E402


RNG_SEED = 20260531 + 366
ANCHOR_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
UPLOAD_PREFIX = "submission_e366_hiddenlife_donorlatent"

E364_SCORES_IN = OUT / "e364_public_like_cellaction_scores.csv"
E365_SUPPORT_IN = OUT / "e365_public_like_jackknife_candidate_support.csv"
E365_SELECTION_IN = OUT / "e365_public_like_jackknife_selection.csv"
E363_SELECTION_IN = OUT / "e363_cell_action_robustness_selection.csv"

KNOWN_OUT = OUT / "e366_hidden_lifestyle_donor_family_known.csv"
CANDIDATES_OUT = OUT / "e366_hidden_lifestyle_donor_family_candidates.csv"
SCORES_OUT = OUT / "e366_hidden_lifestyle_donor_family_scores.csv"
SCENARIOS_OUT = OUT / "e366_hidden_lifestyle_donor_family_scenarios.csv"
RANKS_OUT = OUT / "e366_hidden_lifestyle_donor_family_scenario_ranks.csv"
SUPPORT_OUT = OUT / "e366_hidden_lifestyle_donor_family_support.csv"
SELECTION_OUT = OUT / "e366_hidden_lifestyle_donor_family_selection.csv"
REPORT_OUT = OUT / "e366_hidden_lifestyle_donor_family_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def zarr(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    sd = float(np.std(arr))
    if not np.isfinite(sd) or sd < 1.0e-12:
        return np.zeros_like(arr)
    return (arr - float(np.mean(arr))) / sd


def rank01(values: pd.Series | np.ndarray) -> np.ndarray:
    return pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0).rank(pct=True).to_numpy(dtype=np.float64)


def good_low(values: pd.Series | np.ndarray) -> pd.Series:
    v = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    return (-v.fillna(v.median())).rank(pct=True)


def good_high(values: pd.Series | np.ndarray) -> pd.Series:
    v = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    return v.fillna(v.median()).rank(pct=True)


def make_model(name: str, train_n: int):
    if name == "ridge_10":
        return make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    if name == "ridge_1":
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if name == "knn3":
        return make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=min(3, max(1, train_n - 1)), weights="distance"))
    if name == "extratrees":
        return ExtraTreesRegressor(n_estimators=144, min_samples_leaf=2, max_features=0.70, random_state=RNG_SEED, n_jobs=1)
    raise ValueError(name)


def source_key(variant: str) -> str | None:
    text = str(variant)
    if "donor_q3s1" in text:
        return "q3s1"
    if "donor_q3_" in text and "donor_q3s1" not in text:
        return "q3"
    if "donor_s1_" in text:
        return "s1"
    return None


def load_family_sources(anchor: pd.DataFrame, anchor_logit: np.ndarray) -> dict[str, dict[str, Any]]:
    support = pd.read_csv(E365_SUPPORT_IN).replace([np.inf, -np.inf], np.nan)
    scores = pd.read_csv(E364_SCORES_IN).replace([np.inf, -np.inf], np.nan)
    donors = support[support["family"].astype(str).eq("donor_graft")].copy()
    donors = donors.sort_values(["top1_count", "top10_count", "rank_mean"], ascending=[False, False, True]).reset_index(drop=True)

    picked: dict[str, pd.Series] = {}
    for _, row in donors.iterrows():
        key = source_key(str(row["variant"]))
        if key is not None and key not in picked:
            picked[key] = row
        if len(picked) >= 3:
            break
    for i, (_, row) in enumerate(donors.head(5).iterrows(), start=1):
        key = f"support{i}"
        if key not in picked and source_key(str(row["variant"])) is None:
            picked[key] = row

    if len(picked) < 2:
        raise RuntimeError("E365 donor-graft support did not expose enough source members")

    sources: dict[str, dict[str, Any]] = {}
    for key, row in picked.items():
        path = locate(row["file"])
        if path is None:
            continue
        frame = load_source(path, anchor)
        delta = logit(frame[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
        score_row = scores[scores["file"].astype(str).eq(str(row["file"]))].head(1)
        meta = score_row.iloc[0].to_dict() if len(score_row) else {}
        sources[key] = {
            "key": key,
            "variant": str(row["variant"]),
            "file": rel(path),
            "path": path,
            "delta": delta,
            "support_top1": float(row.get("top1_count", 0.0)),
            "support_top5": float(row.get("top5_count", 0.0)),
            "support_top10": float(row.get("top10_count", 0.0)),
            "support_rank_mean": float(row.get("rank_mean", np.nan)),
            "support_score_mean": float(row.get("score_mean", np.nan)),
            "e364_public_like_score": float(meta.get("e364_public_like_score", np.nan)),
            "e363_robust_score": float(meta.get("e363_robust_score", np.nan)),
            "rowstate_loss": float(meta.get("rowstate_pred_public_loss_mean", np.nan)),
            "rowstate_exposure": float(meta.get("rowstate_bad_minus_good_exposure", np.nan)),
        }
    return sources


def story_gate(state: pd.DataFrame, cols: list[str]) -> np.ndarray:
    vals = []
    for col in cols:
        if col in state.columns:
            vals.append(zarr(state[col]))
    if not vals:
        return np.zeros(len(state), dtype=np.float64)
    score = np.mean(np.vstack(vals), axis=0)
    return rank01(score)


def lifestyle_gates(state: pd.DataFrame) -> dict[str, np.ndarray]:
    scores = row_state_scores(state)
    risk = rank01(scores["risk_core"])
    bad = rank01(state["rowstate_bad_minus_good"])
    energy = rank01(state["ownlife_energy"])
    dist = rank01(state["ownlife_cluster_distance"])
    weekend = pd.to_numeric(state.get("is_weekend", 0.0), errors="coerce").fillna(0.0).to_numpy(dtype=np.float64)
    cluster = pd.to_numeric(state["ownlife_k8"], errors="coerce").fillna(-1).astype(int).to_numpy()

    high_bad_cluster = np.isin(cluster, [3, 5, 6]).astype(float)
    good_cluster = np.isin(cluster, [1, 3, 5]).astype(float)
    phone = story_gate(state, ["phone_in_bed_subj_z", "deepnight_phone_awake_subj_z", "late_msg_call_subj_z", "presleep_msg_drag_abs_subj_z"])
    finance = story_gate(state, ["finance_shopping_stress_abs_subj_z", "payeom_pre7_budget_squeeze_subj_z", "pay25_post3_late_shopping_subj_z"])
    routine = story_gate(state, ["weekday_routine_pressure_abs_subj_z", "commute_workday_abs_subj_z", "afterwork_recovery_abs_subj_z"])
    recovery = story_gate(state, ["low_hr_recovery_subj_z", "physical_fatigue_abs_subj_z", "overtraining_arousal_subj_z", "morning_after_badnight_abs_subj_z"])
    weekend_rest = np.maximum(weekend, story_gate(state, ["weekend_ritual_rest_subj_z", "weekend_social_jetlag_subj_z"]))

    return {
        "risk_tail": np.clip((risk - 0.65) / 0.35, 0.0, 1.0),
        "badstate_tail": np.clip((bad - 0.60) / 0.40, 0.0, 1.0),
        "energy_tail": np.clip((energy - 0.65) / 0.35, 0.0, 1.0),
        "cluster_356_bad": high_bad_cluster,
        "good_cluster_q3": good_cluster,
        "phone_bed_tail": np.clip((phone - 0.60) / 0.40, 0.0, 1.0),
        "finance_cash_tail": np.clip((finance - 0.62) / 0.38, 0.0, 1.0),
        "routine_pressure_tail": np.clip((routine - 0.62) / 0.38, 0.0, 1.0),
        "recovery_fatigue_tail": np.clip((recovery - 0.62) / 0.38, 0.0, 1.0),
        "weekend_rest_tail": np.clip((weekend_rest - 0.50) / 0.50, 0.0, 1.0),
        "risk_x_phone": np.sqrt(np.clip((risk - 0.55) / 0.45, 0.0, 1.0) * np.clip((phone - 0.55) / 0.45, 0.0, 1.0)),
        "bad_x_finance": np.sqrt(np.clip((bad - 0.55) / 0.45, 0.0, 1.0) * np.clip((finance - 0.55) / 0.45, 0.0, 1.0)),
        "energy_x_recovery": np.sqrt(np.clip((energy - 0.55) / 0.45, 0.0, 1.0) * np.clip((recovery - 0.55) / 0.45, 0.0, 1.0)),
        "distance_tail": np.clip((dist - 0.70) / 0.30, 0.0, 1.0),
    }


def normalize_weights(weights: dict[str, np.ndarray], n: int) -> dict[str, np.ndarray]:
    keys = list(weights)
    mat = np.vstack([np.asarray(weights[k], dtype=np.float64) for k in keys]).T
    mat = np.clip(mat, 0.0, None)
    denom = mat.sum(axis=1)
    denom[denom <= 1.0e-12] = 1.0
    mat = mat / denom[:, None]
    return {k: mat[:, i] for i, k in enumerate(keys)}


def row_blend(deltas: dict[str, np.ndarray], weights: dict[str, np.ndarray]) -> np.ndarray:
    n = next(iter(deltas.values())).shape[0]
    norm = normalize_weights(weights, n)
    out = np.zeros_like(next(iter(deltas.values())))
    for key, w in norm.items():
        out += deltas[key] * w[:, None]
    out[:, TARGETS.index("S3")] = 0.0
    return out


def constant_weights(keys: list[str], weights: dict[str, float], n: int) -> dict[str, np.ndarray]:
    return {k: np.full(n, float(weights.get(k, 0.0)), dtype=np.float64) for k in keys}


def interpolate_weights(keys: list[str], low: dict[str, float], high: dict[str, float], gate: np.ndarray) -> dict[str, np.ndarray]:
    g = np.asarray(gate, dtype=np.float64)
    return {k: (1.0 - g) * float(low.get(k, 0.0)) + g * float(high.get(k, 0.0)) for k in keys}


def candidate_prefeatures(
    delta: np.ndarray,
    sources: dict[str, dict[str, Any]],
    state: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
    meta: dict[str, Any],
) -> dict[str, Any]:
    absd = np.abs(delta)
    target_abs = absd.sum(axis=0)
    total = float(target_abs.sum())
    row_abs = absd.sum(axis=1)
    rec: dict[str, Any] = {
        **meta,
        "source_l1_mean": float(np.mean([np.abs(src["delta"]).sum() for src in sources.values()])),
        "move_l1": float(absd.sum()),
        "move_l2": float(np.linalg.norm(delta.reshape(-1))),
        "row_l1_p90": float(np.quantile(row_abs, 0.90)),
        "changed_rows_vs_e247": int((row_abs > 1.0e-12).sum()),
        "changed_cells_vs_e247": int((absd > 1.0e-12).sum()),
    }
    rec["gated_l1_ratio"] = rec["move_l1"] / rec["source_l1_mean"] if rec["source_l1_mean"] > 0 else 0.0
    for i, target in enumerate(TARGETS):
        rec[f"abs_{target}"] = float(target_abs[i])
        rec[f"share_{target}"] = float(target_abs[i] / total) if total > 0 else 0.0
    rec.update(rowstate_features(delta, state, base_cols, story_cols))
    return rec


def materialize(
    anchor: pd.DataFrame,
    anchor_logit: np.ndarray,
    delta: np.ndarray,
    sources: dict[str, dict[str, Any]],
    state: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
    meta: dict[str, Any],
    rows: list[dict[str, Any]],
    seen: set[str],
) -> None:
    if not np.isfinite(delta).all() or float(np.abs(delta).sum()) < 1.0e-9:
        return
    digest = hashlib.sha1(np.round(delta, 8).tobytes()).hexdigest()[:12]
    if digest in seen:
        return
    seen.add(digest)
    out = anchor[KEY].copy()
    out[TARGETS] = clip_prob(sigmoid(anchor_logit + delta))
    variant = str(meta["variant"])
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(variant, 112)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    rec = candidate_prefeatures(delta, sources, state, base_cols, story_cols, meta)
    rec["file"] = rel(path)
    rec["basename"] = path.name
    rows.append(rec)


def generate_candidates(anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> tuple[pd.DataFrame, dict[str, dict[str, Any]]]:
    sources = load_family_sources(anchor, anchor_logit)
    deltas = {k: v["delta"] for k, v in sources.items()}
    keys = [k for k in ["q3s1", "q3", "s1"] if k in deltas]
    if len(keys) < 2:
        keys = list(deltas)[: max(2, len(deltas))]
    n = anchor.shape[0]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    # Family centers: tests whether E365 discovered a basin, not a one-file edge.
    support_weights = {
        k: sources[k]["support_top1"] + 0.35 * sources[k]["support_top5"] + 0.10 * sources[k]["support_top10"]
        for k in keys
    }
    top10_weights = {k: max(0.0, sources[k]["support_top10"]) for k in keys}
    rank_weights = {k: 1.0 / max(1.0, sources[k]["support_rank_mean"]) for k in keys}
    e364_weights = {k: max(0.0, sources[k]["e364_public_like_score"]) for k in keys}
    center_specs = {
        "center_support": support_weights,
        "center_top10": top10_weights,
        "center_rankinv": rank_weights,
        "center_publicscore": e364_weights,
        "center_equal": {k: 1.0 for k in keys},
    }
    for center_id, weights in center_specs.items():
        if sum(weights.values()) <= 0:
            continue
        delta = row_blend(deltas, constant_weights(keys, weights, n))
        materialize(
            anchor,
            anchor_logit,
            delta,
            sources,
            state,
            base_cols,
            story_cols,
            {"variant": f"e366_{center_id}", "family": "family_center", "center_id": center_id},
            rows,
            seen,
        )

    # Pairwise centers: tests whether Q3-only, S1-only, or the selected Q3S1
    # point is the actual latent center.
    for a, b in [("q3s1", "q3"), ("q3s1", "s1"), ("q3", "s1")]:
        if a not in deltas or b not in deltas:
            continue
        for wa in [0.25, 0.40, 0.50, 0.60, 0.75]:
            weights = {a: wa, b: 1.0 - wa}
            delta = row_blend(deltas, constant_weights(keys, weights, n))
            materialize(
                anchor,
                anchor_logit,
                delta,
                sources,
                state,
                base_cols,
                story_cols,
                {"variant": f"e366_pair_{a}_{b}_wa{wa:.2f}", "family": "pair_center", "pair_a": a, "pair_b": b, "weight_a": wa},
                rows,
                seen,
            )

    # Target-family recombinations: tests whether the latent is target-specific
    # rather than a row-wise mixture.
    if {"q3s1", "q3", "s1"}.issubset(deltas):
        q3_idx = TARGETS.index("Q3")
        s1_idx = TARGETS.index("S1")
        for spec_id, q3_src, s1_src, base_src in [
            ("q3_from_q3_s1_from_s1_base_q3s1", "q3", "s1", "q3s1"),
            ("q3_from_q3_s1_from_q3s1_base_q3", "q3", "q3s1", "q3"),
            ("q3_from_q3s1_s1_from_s1_base_q3", "q3s1", "s1", "q3"),
        ]:
            delta = deltas[base_src].copy()
            delta[:, q3_idx] = deltas[q3_src][:, q3_idx]
            delta[:, s1_idx] = deltas[s1_src][:, s1_idx]
            delta[:, TARGETS.index("S3")] = 0.0
            materialize(
                anchor,
                anchor_logit,
                delta,
                sources,
                state,
                base_cols,
                story_cols,
                {"variant": f"e366_targetcell_{spec_id}", "family": "target_cell_center", "target_cell_spec": spec_id},
                rows,
                seen,
            )

    gates = lifestyle_gates(state)
    low_q3 = {"q3": 0.72, "q3s1": 0.22, "s1": 0.06}
    high_s1 = {"q3": 0.16, "q3s1": 0.48, "s1": 0.36}
    high_q3s1 = {"q3": 0.08, "q3s1": 0.82, "s1": 0.10}
    high_q3 = {"q3": 0.84, "q3s1": 0.14, "s1": 0.02}
    high_balanced = {"q3": 0.26, "q3s1": 0.56, "s1": 0.18}
    row_policies = [
        ("risk_to_s1", low_q3, high_s1),
        ("risk_to_q3s1", low_q3, high_q3s1),
        ("badstate_to_s1", low_q3, high_s1),
        ("phone_to_s1", low_q3, high_s1),
        ("finance_to_q3s1", low_q3, high_q3s1),
        ("routine_to_q3", high_balanced, high_q3),
        ("recovery_to_s1", low_q3, high_s1),
        ("weekend_to_q3s1", low_q3, high_balanced),
        ("distance_to_q3s1", low_q3, high_q3s1),
    ]
    gate_map = {
        "risk_to_s1": "risk_tail",
        "risk_to_q3s1": "risk_tail",
        "badstate_to_s1": "badstate_tail",
        "phone_to_s1": "phone_bed_tail",
        "finance_to_q3s1": "finance_cash_tail",
        "routine_to_q3": "routine_pressure_tail",
        "recovery_to_s1": "recovery_fatigue_tail",
        "weekend_to_q3s1": "weekend_rest_tail",
        "distance_to_q3s1": "distance_tail",
    }
    for policy_id, low, high in row_policies:
        gate = gates[gate_map[policy_id]]
        for strength in [0.70, 1.00]:
            g = np.clip(gate * strength, 0.0, 1.0)
            weights = interpolate_weights(keys, low, high, g)
            delta = row_blend(deltas, weights)
            materialize(
                anchor,
                anchor_logit,
                delta,
                sources,
                state,
                base_cols,
                story_cols,
                {
                    "variant": f"e366_rowlatent_{policy_id}_s{strength:.2f}",
                    "family": "row_lifestyle_gate",
                    "row_policy": policy_id,
                    "gate_id": gate_map[policy_id],
                    "gate_mean": float(np.mean(g)),
                    "gate_p90": float(np.quantile(g, 0.90)),
                },
                rows,
                seen,
            )

    # Target-specific row gates: Q3 may be safe on routine/good rows while S1
    # recovery may be the anti-bad-state component on tail rows.
    if {"q3s1", "q3", "s1"}.issubset(deltas):
        for gate_id in ["risk_x_phone", "bad_x_finance", "energy_x_recovery", "cluster_356_bad"]:
            g = gates[gate_id]
            for target_policy in ["s1_tail_only", "q3_good_s1_bad"]:
                delta = deltas["q3"].copy()
                if target_policy == "s1_tail_only":
                    delta[:, TARGETS.index("S1")] = (1.0 - g) * deltas["q3"][:, TARGETS.index("S1")] + g * deltas["s1"][:, TARGETS.index("S1")]
                    delta[:, TARGETS.index("Q1")] = (1.0 - 0.25 * g) * deltas["q3"][:, TARGETS.index("Q1")] + 0.25 * g * deltas["q3s1"][:, TARGETS.index("Q1")]
                    delta[:, TARGETS.index("Q2")] = (1.0 - 0.25 * g) * deltas["q3"][:, TARGETS.index("Q2")] + 0.25 * g * deltas["q3s1"][:, TARGETS.index("Q2")]
                else:
                    delta[:, TARGETS.index("Q3")] = (1.0 - g) * deltas["q3"][:, TARGETS.index("Q3")] + g * deltas["q3s1"][:, TARGETS.index("Q3")]
                    delta[:, TARGETS.index("S1")] = (1.0 - g) * deltas["q3s1"][:, TARGETS.index("S1")] + g * deltas["s1"][:, TARGETS.index("S1")]
                delta[:, TARGETS.index("S3")] = 0.0
                materialize(
                    anchor,
                    anchor_logit,
                    delta,
                    sources,
                    state,
                    base_cols,
                    story_cols,
                    {
                        "variant": f"e366_targetrow_{target_policy}_{gate_id}",
                        "family": "target_row_lifestyle_gate",
                        "target_policy": target_policy,
                        "gate_id": gate_id,
                        "gate_mean": float(np.mean(g)),
                        "gate_p90": float(np.quantile(g, 0.90)),
                    },
                    rows,
                    seen,
                )

        # Anti-collapse controls for the strongest cluster gate.  These keep
        # the same target-row translator but destroy the lifestyle-state row
        # identity.  If they rank with the real cluster gate, the latent gate is
        # just a movable mask and should not be trusted.
        rng = np.random.default_rng(RNG_SEED)
        base_gate = gates["cluster_356_bad"]
        null_gates: dict[str, np.ndarray] = {
            "inverse_cluster_356_bad": 1.0 - base_gate,
            "random_rate_match_0": (rng.random(n) < float(np.mean(base_gate))).astype(float),
            "random_rate_match_1": (rng.random(n) < float(np.mean(base_gate))).astype(float),
            "random_rate_match_2": (rng.random(n) < float(np.mean(base_gate))).astype(float),
            "perm_cluster_0": rng.permutation(base_gate),
            "perm_cluster_1": rng.permutation(base_gate),
            "perm_cluster_2": rng.permutation(base_gate),
        }
        for null_id, g in null_gates.items():
            delta = deltas["q3"].copy()
            delta[:, TARGETS.index("Q3")] = (1.0 - g) * deltas["q3"][:, TARGETS.index("Q3")] + g * deltas["q3s1"][:, TARGETS.index("Q3")]
            delta[:, TARGETS.index("S1")] = (1.0 - g) * deltas["q3s1"][:, TARGETS.index("S1")] + g * deltas["s1"][:, TARGETS.index("S1")]
            delta[:, TARGETS.index("S3")] = 0.0
            materialize(
                anchor,
                anchor_logit,
                delta,
                sources,
                state,
                base_cols,
                story_cols,
                {
                    "variant": f"e366_nulltargetrow_q3_good_s1_bad_{null_id}",
                    "family": "null_row_lifestyle_gate",
                    "target_policy": "q3_good_s1_bad",
                    "gate_id": null_id,
                    "gate_mean": float(np.mean(g)),
                    "gate_p90": float(np.quantile(g, 0.90)),
                },
                rows,
                seen,
            )

    # Tiny amplitude checks around the best conceptual centers.  This is not a
    # sweep; it asks whether the latent action is overconfident.
    base_rows = list(rows)
    for rec in base_rows[:12]:
        path = locate(rec["file"])
        if path is None:
            continue
        base_delta = logit(load_source(path, anchor)[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
        for scale in [0.97, 1.03]:
            delta = base_delta * scale
            delta[:, TARGETS.index("S3")] = 0.0
            materialize(
                anchor,
                anchor_logit,
                delta,
                sources,
                state,
                base_cols,
                story_cols,
                {
                    "variant": f"{rec['variant']}_amp{scale:.2f}",
                    "family": f"{rec['family']}_amp",
                    "amplitude_scale": scale,
                },
                rows,
                seen,
            )

    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATES_OUT, index=False)
    return out, sources


def public_score_candidates(scored: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    anchor = logit_frame(OUT / ANCHOR_FILE)
    known, known_deltas, _ = load_known(anchor)
    axes = make_axes(known_deltas)
    known = add_axis_features(known, known_deltas, axes)
    known = public_axis_summaries(known)
    known.to_csv(KNOWN_OUT, index=False)
    feature_cols = movement_feature_columns(known)

    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    for rec in scored.to_dict("records"):
        path = locate(rec["file"])
        if path is None:
            continue
        delta = align_delta(path, anchor)
        deltas[path.name] = delta
        rows.append(
            {
                "variant": rec["variant"],
                "family": rec["family"],
                "file": rel(path),
                "basename": path.name,
                **movement_features(delta),
            }
        )
    movement = pd.DataFrame(rows)
    movement = add_axis_features(movement, deltas, axes)
    movement = public_axis_summaries(movement)

    keys = ["variant", "family", "file", "basename"]
    blocked = set(movement.columns) - set(keys)
    pool = scored.drop(columns=[c for c in blocked if c in scored.columns], errors="ignore").merge(movement, on=keys, how="inner")

    train = known[known["available"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    x = train[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    xp = pool.reindex(columns=feature_cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    pred_cols: list[str] = []
    for model_name in ["ridge_10", "ridge_1", "knn3", "extratrees"]:
        model = make_model(model_name, len(train))
        model.fit(x, y)
        col = f"e366_pred_public_delta_{model_name}"
        pool[col] = np.asarray(model.predict(xp), dtype=np.float64)
        pred_cols.append(col)
    pool["e366_pred_public_delta_mean"] = pool[pred_cols].mean(axis=1)
    pool["e366_pred_public_delta_std"] = pool[pred_cols].std(axis=1).fillna(0.0)
    pool["e366_pred_public_delta_max"] = pool[pred_cols].max(axis=1)

    existing = pd.read_csv(E364_SCORES_IN).replace([np.inf, -np.inf], np.nan)
    existing = existing.rename(
        columns={
            "e364_pred_public_delta_mean": "e366_pred_public_delta_mean",
            "e364_pred_public_delta_std": "e366_pred_public_delta_std",
            "e364_pred_public_delta_max": "e366_pred_public_delta_max",
            "e364_public_like_score": "previous_public_like_score",
        }
    )
    existing["candidate_origin"] = "e364_existing"
    pool["candidate_origin"] = "e366_generated"
    combined = pd.concat([existing, pool], ignore_index=True, sort=False)

    defaults = {
        "public_bad_axis_sum": 0.0,
        "public_bad_good_gap": 0.0,
        "rowstate_pred_public_loss_mean": 0.0,
        "rowstate_bad_minus_good_exposure": 0.0,
        "e363_robust_score": 0.0,
        "pred_delta_vs_current_p90": 0.0,
    }
    for col, default in defaults.items():
        if col not in combined:
            combined[col] = default
        combined[col] = pd.to_numeric(combined[col], errors="coerce").fillna(default)
    if "e363_submission_gate" not in combined:
        combined["e363_submission_gate"] = False

    combined["e366_public_like_score"] = (
        1.15 * good_low(combined["e366_pred_public_delta_mean"])
        + 0.75 * good_low(combined["e366_pred_public_delta_std"])
        + 0.95 * good_low(combined["public_bad_axis_sum"])
        + 0.55 * good_low(combined["public_bad_good_gap"])
        + 0.90 * good_low(combined["rowstate_pred_public_loss_mean"])
        + 0.80 * good_low(combined["rowstate_bad_minus_good_exposure"])
        + 0.90 * good_high(combined["e363_robust_score"])
        + 0.55 * good_low(combined["pred_delta_vs_current_p90"])
    )
    combined = combined.sort_values("e366_public_like_score", ascending=False).reset_index(drop=True)
    combined.to_csv(SCORES_OUT, index=False)
    return combined, known, feature_cols


def available_feature_sets(known: pd.DataFrame, pool: pd.DataFrame) -> dict[str, list[str]]:
    base = [c for c in movement_feature_columns(known) if c in pool.columns]
    axis = [c for c in base if c.startswith(("cos_", "proj_", "posproj_", "absproj_")) or c.startswith("public_")]
    target_tokens = tuple([f"_{t}" for t in TARGETS] + [f"{t}_" for t in TARGETS])
    target = [c for c in base if c.startswith(("share_", "l1_", "signed_sum_", "mean_", "maxabs_", "pos_frac_", "neg_frac_")) or any(tok in c for tok in target_tokens)]
    anatomy = [
        c
        for c in base
        if c.startswith(("cell_", "row_", "changed_", "top5_", "top20_"))
        or c in {"target_entropy", "row_entropy", "cell_mean_abs", "cell_signed_mean"}
    ]
    bad_good = [c for c in base if "bad" in c or "good" in c or "e323" in c or "e216" in c or "e267" in c]
    compact = [
        c
        for c in [
            "cell_l1",
            "cell_l2",
            "cell_linf",
            "row_l1_mean",
            "row_l1_p90",
            "row_l1_max",
            "target_entropy",
            "row_entropy",
            "share_Q1",
            "share_Q2",
            "share_Q3",
            "share_S1",
            "share_S2",
            "share_S3",
            "share_S4",
            "public_bad_axis_sum",
            "public_good_axis_sum",
            "public_bad_good_gap",
            "public_bad_cos_max",
            "public_good_cos_max",
        ]
        if c in base
    ]
    return {k: v for k, v in {"all": base, "axis": axis, "target": target, "anatomy": anatomy, "bad_good": bad_good, "compact": compact}.items() if len(v) >= 3}


def predict_pool(train: pd.DataFrame, pool: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    x = train[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = train["delta_vs_e247"].to_numpy(dtype=np.float64)
    xp = pool.reindex(columns=cols).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    preds = []
    diag: dict[str, float] = {}
    for model_name in ["ridge_10", "ridge_1", "knn3", "extratrees"]:
        model = make_model(model_name, len(train))
        model.fit(x, y)
        pred = np.asarray(model.predict(xp), dtype=np.float64)
        preds.append(pred)
        fitted = np.asarray(model.predict(x), dtype=np.float64)
        diag[f"train_spearman_{model_name}"] = safe_spearman(y, fitted)
    arr = np.vstack(preds)
    return arr.mean(axis=0), arr.std(axis=0), diag


def score_scenario(pool: pd.DataFrame, pred_mean: np.ndarray, pred_std: np.ndarray, base_variant: str) -> pd.DataFrame:
    scored = pool.copy()
    scored["scenario_pred_public_delta_mean"] = pred_mean
    scored["scenario_pred_public_delta_std"] = pred_std
    for col in [
        "public_bad_axis_sum",
        "public_bad_good_gap",
        "rowstate_pred_public_loss_mean",
        "rowstate_bad_minus_good_exposure",
        "e363_robust_score",
        "pred_delta_vs_current_p90",
    ]:
        if col not in scored:
            scored[col] = 0.0
        scored[col] = pd.to_numeric(scored[col], errors="coerce").fillna(0.0)
    scored["scenario_public_like_score"] = (
        1.15 * good_low(scored["scenario_pred_public_delta_mean"])
        + 0.75 * good_low(scored["scenario_pred_public_delta_std"])
        + 0.95 * good_low(scored["public_bad_axis_sum"])
        + 0.55 * good_low(scored["public_bad_good_gap"])
        + 0.90 * good_low(scored["rowstate_pred_public_loss_mean"])
        + 0.80 * good_low(scored["rowstate_bad_minus_good_exposure"])
        + 0.90 * good_high(scored["e363_robust_score"])
        + 0.55 * good_low(scored["pred_delta_vs_current_p90"])
    )
    base = scored[scored["variant"].astype(str).eq(base_variant)].head(1)
    if base.empty:
        base = scored[scored["candidate_origin"].astype(str).eq("e364_existing")].sort_values("e366_public_like_score", ascending=False).head(1)
    base_row = base.iloc[0]
    scored["scenario_gate"] = (
        scored["e363_submission_gate"].fillna(False).astype(bool)
        & (scored["scenario_pred_public_delta_mean"] <= float(base_row["scenario_pred_public_delta_mean"]) + 5.0e-5)
        & (scored["scenario_pred_public_delta_std"] <= float(base_row["scenario_pred_public_delta_std"]) + 2.5e-4)
        & (scored["public_bad_axis_sum"] <= float(base_row["public_bad_axis_sum"]) + 0.12)
        & (scored["rowstate_pred_public_loss_mean"] <= float(base_row["rowstate_pred_public_loss_mean"]) + 2.5e-4)
        & (scored["rowstate_bad_minus_good_exposure"] <= float(base_row["rowstate_bad_minus_good_exposure"]) + 0.035)
        & (scored["e363_robust_score"] >= max(0.50, float(base_row["e363_robust_score"]) - 0.08))
    )
    gated = scored[scored["scenario_gate"]].copy()
    scored["scenario_rank"] = np.nan
    if not gated.empty:
        ranks = gated["scenario_public_like_score"].rank(ascending=False, method="min")
        scored.loc[gated.index, "scenario_rank"] = ranks
    return scored


def run_scenarios(known: pd.DataFrame, pool: pd.DataFrame, feature_sets: dict[str, list[str]], e365_variant: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    train0 = known[known["available"].fillna(False).astype(bool)].copy().reset_index(drop=True)
    drops: list[tuple[str, str | None]] = [("none", None)]
    drops += [(f"drop_{safe_id(b, 42)}", b) for b in train0["basename"].astype(str).tolist()]
    scenario_rows: list[dict[str, Any]] = []
    rank_rows: list[pd.DataFrame] = []
    for view_name, cols in feature_sets.items():
        for drop_name, drop_base in drops:
            train = train0.copy()
            if drop_base is not None:
                train = train[~train["basename"].astype(str).eq(drop_base)].reset_index(drop=True)
            pred_mean, pred_std, diag = predict_pool(train, pool, cols)
            scored = score_scenario(pool, pred_mean, pred_std, e365_variant)
            gated = scored[scored["scenario_gate"]].copy()
            if gated.empty:
                continue
            top = gated.sort_values("scenario_public_like_score", ascending=False).iloc[0]
            e365 = scored[scored["variant"].astype(str).eq(e365_variant)].head(1)
            generated = gated[gated["candidate_origin"].astype(str).eq("e366_generated")].copy()
            best_generated = generated.sort_values("scenario_public_like_score", ascending=False).head(1)
            scenario_id = f"{view_name}__{drop_name}"
            row = {
                "scenario_id": scenario_id,
                "feature_view": view_name,
                "dropped_public": drop_base or "none",
                "train_rows": int(len(train)),
                "feature_count": int(len(cols)),
                "gated_count": int(len(gated)),
                "top_variant": top["variant"],
                "top_family": top.get("family", ""),
                "top_origin": top.get("candidate_origin", ""),
                "top_file": top.get("file", ""),
                "top_score": float(top["scenario_public_like_score"]),
                "generated_gated_count": int(len(generated)),
                **diag,
            }
            if len(e365):
                row["e365_rank"] = float(e365.iloc[0]["scenario_rank"]) if pd.notna(e365.iloc[0]["scenario_rank"]) else np.nan
                row["e365_score"] = float(e365.iloc[0]["scenario_public_like_score"])
                row["top_beats_e365"] = bool(float(top["scenario_public_like_score"]) > float(e365.iloc[0]["scenario_public_like_score"]))
                row["top_is_e365"] = bool(str(top["variant"]) == e365_variant)
            if len(best_generated):
                bg = best_generated.iloc[0]
                row["best_generated_variant"] = bg["variant"]
                row["best_generated_family"] = bg.get("family", "")
                row["best_generated_rank"] = float(bg["scenario_rank"]) if pd.notna(bg["scenario_rank"]) else np.nan
                row["best_generated_score"] = float(bg["scenario_public_like_score"])
            scenario_rows.append(row)
            slim = scored[
                [
                    "variant",
                    "family",
                    "file",
                    "candidate_origin",
                    "scenario_gate",
                    "scenario_rank",
                    "scenario_public_like_score",
                    "scenario_pred_public_delta_mean",
                    "scenario_pred_public_delta_std",
                ]
            ].copy()
            slim["scenario_id"] = scenario_id
            rank_rows.append(slim[slim["scenario_gate"] | slim["variant"].astype(str).eq(e365_variant)])
    scenarios = pd.DataFrame(scenario_rows)
    ranks = pd.concat(rank_rows, ignore_index=True) if rank_rows else pd.DataFrame()
    scenarios.to_csv(SCENARIOS_OUT, index=False)
    ranks.to_csv(RANKS_OUT, index=False)
    return scenarios, ranks


def aggregate_support(ranks: pd.DataFrame, scenario_count: int) -> pd.DataFrame:
    if ranks.empty:
        return pd.DataFrame()
    support = (
        ranks.groupby(["variant", "family", "file", "candidate_origin"], dropna=False)
        .agg(
            gate_count=("scenario_gate", "sum"),
            rank_mean=("scenario_rank", "mean"),
            rank_median=("scenario_rank", "median"),
            rank_min=("scenario_rank", "min"),
            top1_count=("scenario_rank", lambda x: int((x == 1).sum())),
            top5_count=("scenario_rank", lambda x: int((x <= 5).sum())),
            top10_count=("scenario_rank", lambda x: int((x <= 10).sum())),
            score_mean=("scenario_public_like_score", "mean"),
            score_std=("scenario_public_like_score", "std"),
            pred_mean=("scenario_pred_public_delta_mean", "mean"),
            pred_std_mean=("scenario_pred_public_delta_std", "mean"),
        )
        .reset_index()
    )
    for col in ["gate_count", "top1_count", "top5_count", "top10_count"]:
        support[f"{col.replace('_count', '')}_rate"] = support[col] / max(1, scenario_count)
    support = support.sort_values(["top1_count", "top5_count", "rank_mean", "score_mean"], ascending=[False, False, True, False]).reset_index(drop=True)
    support.to_csv(SUPPORT_OUT, index=False)
    return support


def copy_uploadsafe(path: Path, variant: str) -> Path:
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    frame = pd.read_csv(path)
    for target in TARGETS:
        frame[target] = clip_prob(frame[target].to_numpy(dtype=np.float64))
    out = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(variant, 70)}_{short_hash(frame)}_uploadsafe.csv"
    frame.to_csv(out, index=False)
    return out


def decide(combined: pd.DataFrame, support: pd.DataFrame, scenarios: pd.DataFrame, e365_variant: str) -> pd.DataFrame:
    e365_support = support[support["variant"].astype(str).eq(e365_variant)].head(1)
    generated_support = support[support["candidate_origin"].astype(str).eq("e366_generated")].copy()
    is_null = generated_support["family"].astype(str).str.startswith("null_")
    null_support = generated_support[is_null].copy()
    real_generated_support = generated_support[~is_null].copy()
    best_generated = real_generated_support.head(1)
    best_null = null_support.head(1)
    e365_score = combined[combined["variant"].astype(str).eq(e365_variant)].head(1)
    best_generated_score = pd.DataFrame()
    if len(best_generated):
        best_generated_score = combined[combined["variant"].astype(str).eq(str(best_generated.iloc[0]["variant"]))].head(1)

    e365_top1 = float(e365_support["top1_rate"].iloc[0]) if len(e365_support) else 0.0
    e365_top10 = float(e365_support["top10_rate"].iloc[0]) if len(e365_support) else 0.0
    gen_top1 = float(best_generated["top1_rate"].iloc[0]) if len(best_generated) else 0.0
    gen_top10 = float(best_generated["top10_rate"].iloc[0]) if len(best_generated) else 0.0
    e365_pls = float(e365_score["e366_public_like_score"].iloc[0]) if len(e365_score) else 0.0
    gen_pls = float(best_generated_score["e366_public_like_score"].iloc[0]) if len(best_generated_score) else -np.inf
    null_top1 = float(best_null["top1_rate"].iloc[0]) if len(best_null) else 0.0
    null_top10 = float(best_null["top10_rate"].iloc[0]) if len(best_null) else 0.0
    null_variant = str(best_null.iloc[0]["variant"]) if len(best_null) else "none"

    null_veto = len(best_null) and null_top1 >= max(gen_top1 + 0.10, 0.20)
    if null_veto:
        chosen_variant = e365_variant
        decision = "reject_e366_lifestyle_gate_keep_e365"
        reason = (
            "A permuted/random null row gate beats the real lifestyle-state gates under jackknife. "
            "This kills the row-gate translator as a trustworthy hidden-state discovery; keep E365."
        )
    elif len(best_generated) and gen_top1 >= max(0.20, e365_top1 + 0.10) and gen_pls >= e365_pls - 0.05:
        chosen_variant = str(best_generated.iloc[0]["variant"])
        decision = "select_e366_lifestyle_latent_replacement"
        reason = "A generated hidden lifestyle-state family member wins clearly more jackknife top1 scenarios without losing the public-like score."
    elif len(best_generated) and gen_top10 >= e365_top10 + 0.10 and gen_pls >= e365_pls + 0.10:
        chosen_variant = str(best_generated.iloc[0]["variant"])
        decision = "select_e366_lifestyle_latent_stable_alt"
        reason = "A generated hidden lifestyle-state family member is not top1 dominant, but is more stable in top10 and stronger on the public-like score."
    else:
        chosen_variant = e365_variant
        decision = "keep_e365_donor_graft_selected"
        reason = "The lifestyle-state latent centers did not beat the E365 selected donor-graft point under jackknife stress; treat the family as non-linear, not averageable."

    chosen = combined[combined["variant"].astype(str).eq(chosen_variant)].head(1)
    if chosen.empty:
        chosen = combined.head(1)
        chosen_variant = str(chosen.iloc[0]["variant"])
    src = locate(chosen.iloc[0]["file"])
    for stale in OUT.glob(f"{UPLOAD_PREFIX}_selected_*_uploadsafe.csv"):
        stale.unlink()
    upload = None
    if decision == "reject_e366_lifestyle_gate_keep_e365":
        e365_upload = str(pd.read_csv(E365_SELECTION_IN).iloc[0].get("selected_uploadsafe_file", ""))
        upload = locate(e365_upload) if e365_upload else src
    elif src is not None:
        upload = copy_uploadsafe(src, chosen_variant)
    row = chosen.iloc[0].to_dict()
    row.update(
        {
            "decision": decision,
            "reason": reason,
            "scenario_count": int(len(scenarios)),
            "e365_variant": e365_variant,
            "e365_top1_rate": e365_top1,
            "e365_top10_rate": e365_top10,
            "best_generated_variant": str(best_generated.iloc[0]["variant"]) if len(best_generated) else "none",
            "best_generated_top1_rate": gen_top1,
            "best_generated_top10_rate": gen_top10,
            "best_null_variant": null_variant,
            "best_null_top1_rate": null_top1,
            "best_null_top10_rate": null_top10,
            "e365_public_like_score": e365_pls,
            "best_generated_public_like_score": gen_pls,
            "selected_uploadsafe_file": rel(upload),
        }
    )
    out = pd.DataFrame([row])
    out.to_csv(SELECTION_OUT, index=False)
    return out


def write_report(
    candidates: pd.DataFrame,
    sources: dict[str, dict[str, Any]],
    combined: pd.DataFrame,
    known: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    scenarios: pd.DataFrame,
    support: pd.DataFrame,
    selected: pd.DataFrame,
    e365_variant: str,
) -> None:
    source_rows = pd.DataFrame([{k: v for k, v in src.items() if k != "delta" and k != "path"} for src in sources.values()])
    scenario_summary = (
        scenarios.groupby("feature_view")
        .agg(
            scenarios=("scenario_id", "size"),
            top_generated_rate=("top_origin", lambda x: float(np.mean(pd.Series(x).astype(str).eq("e366_generated")))),
            top_e365_rate=("top_is_e365", "mean"),
            e365_rank_mean=("e365_rank", "mean"),
            generated_gated_mean=("generated_gated_count", "mean"),
        )
        .reset_index()
        if not scenarios.empty
        else pd.DataFrame()
    )
    top_score_cols = [
        "variant",
        "family",
        "candidate_origin",
        "e366_public_like_score",
        "e366_pred_public_delta_mean",
        "e366_pred_public_delta_std",
        "public_bad_axis_sum",
        "rowstate_pred_public_loss_mean",
        "rowstate_bad_minus_good_exposure",
        "e363_robust_score",
        "pred_delta_vs_current_p90",
        "e363_submission_gate",
        "file",
    ]
    support_cols = [
        "variant",
        "family",
        "candidate_origin",
        "top1_count",
        "top5_count",
        "top10_count",
        "rank_mean",
        "score_mean",
        "pred_mean",
        "file",
    ]
    selected_cols = [
        "decision",
        "variant",
        "family",
        "candidate_origin",
        "selected_uploadsafe_file",
        "scenario_count",
        "e365_top1_rate",
        "e365_top10_rate",
        "best_generated_variant",
        "best_generated_top1_rate",
        "best_generated_top10_rate",
        "best_null_variant",
        "best_null_top1_rate",
        "best_null_top10_rate",
        "e365_public_like_score",
        "best_generated_public_like_score",
        "reason",
    ]
    lines = [
        "# E366 Hidden Lifestyle-State Donor-Family Latent",
        "",
        "## Question",
        "",
        "Can the E365 Q3/S1 donor-graft support set be turned into a row-wise hidden lifestyle-state latent, or is the selected E365 point already the non-linear optimum?",
        "",
        "## Method",
        "",
        "- Anchor: E247 public-best probability tensor.",
        "- Source family: E365 jackknife-supported donor-graft members (`q3s1`, `q3`, `s1` when available).",
        "- Hidden state: E328/E358 own-lifestyle latent, row-state bad/good cluster rates, and selected human/social story tails.",
        "- Generated actions: family centers, target-cell recombinations, and row-state gates such as phone-bed, finance/cashflow, routine pressure, recovery fatigue, and E323-heavy clusters.",
        "- Stress: E363 output/row-state gates, E364 known-public movement-axis score, and E365-style feature-view + leave-public-out jackknife.",
        "",
        "## Inputs",
        "",
        f"- generated candidates: `{len(candidates)}`",
        f"- known public rows available: `{int(known['available'].fillna(False).sum())}`",
        f"- feature views: " + ", ".join(f"`{k}`({len(v)})" for k, v in feature_sets.items()),
        f"- E365 reference variant: `{e365_variant}`",
        "",
        "## Source Family",
        "",
        md_table(source_rows, n=20, floatfmt=".6f"),
        "",
        "## Scenario Summary",
        "",
        md_table(scenario_summary, n=20, floatfmt=".6f") if not scenario_summary.empty else "_No scenarios._",
        "",
        "## Top Jackknife Support",
        "",
        md_table(support[[c for c in support_cols if c in support.columns]].head(30), n=30, floatfmt=".6f") if not support.empty else "_No support._",
        "",
        "## Top Public-Like Scores",
        "",
        md_table(combined[[c for c in top_score_cols if c in combined.columns]].head(30), n=30, floatfmt=".6f"),
        "",
        "## Decision",
        "",
        md_table(selected[[c for c in selected_cols if c in selected.columns]], n=5, floatfmt=".6f"),
        "",
        "## Interpretation",
        "",
        "- If a generated row-lifestyle candidate beats E365 under jackknife and also beats null gates, the donor-graft signal is a transferable hidden state and not a one-file edge.",
        "- If a permuted/random null gate beats the real lifestyle gate, the row-state translator is rejected even if its local score is high.",
        "- If centers score well but fail top1/top10 stability, the family is real but non-linear; E365 should remain the actionable submission.",
        "- If row-story gates underperform constant centers, the human/social latent is useful as a diagnostic exposure but not yet as a probability translator.",
        "",
        "## Files",
        "",
        f"- `{rel(CANDIDATES_OUT)}`",
        f"- `{rel(SCORES_OUT)}`",
        f"- `{rel(SCENARIOS_OUT)}`",
        f"- `{rel(SUPPORT_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    candidates, sources = generate_candidates(anchor, anchor_logit, state, base_cols, story_cols)
    selector = selector_scores(candidates, anchor)
    rowstate = rowstate_public_scores(selector, anchor, anchor_logit, state, base_cols, story_cols)
    e363_scored = add_e363_scores(rowstate)
    combined, known, _ = public_score_candidates(e363_scored)
    e365_variant = str(pd.read_csv(E365_SELECTION_IN).iloc[0]["variant"])
    feature_sets = available_feature_sets(known, combined)
    scenarios, ranks = run_scenarios(known, combined, feature_sets, e365_variant)
    support = aggregate_support(ranks, len(scenarios))
    selected = decide(combined, support, scenarios, e365_variant)
    write_report(candidates, sources, combined, known, feature_sets, scenarios, support, selected, e365_variant)

    print(f"generated_candidates={len(candidates)} combined_pool={len(combined)} scenarios={len(scenarios)}")
    print(f"feature_views={ {k: len(v) for k, v in feature_sets.items()} }")
    print(support[["variant", "family", "candidate_origin", "top1_count", "top10_count", "rank_mean", "score_mean"]].head(12).round(6).to_string(index=False))
    print(selected[["decision", "variant", "family", "candidate_origin", "selected_uploadsafe_file", "e365_top1_rate", "best_generated_top1_rate", "e365_top10_rate", "best_generated_top10_rate"]].round(6).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
