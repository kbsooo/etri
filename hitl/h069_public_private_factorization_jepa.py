#!/usr/bin/env python3
"""H069: public/private hidden-state factorization HS-JEPA.

H012 and H057 prove that a public-readable hidden state exists. H068 then
learned a cell-level action-health field from known public interventions. H069
asks the larger private-safety question:

    Which public-healthy actions are also visible from invariant human/context
    state, and which are likely public-only or shortcut actions?

The experiment decomposes each row-target action into:

    public_score     = action response under known public observations
    invariant_score  = human/context/row-state support independent of LB
    shortcut_score   = alignment with known bad anchors and null states

Only actions with positive public and invariant scores, and low shortcut
pressure, are materialized. This is the first explicit public/private
factorization layer of HS-JEPA.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h069_public_private_factorization_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H061 = "submission_h061_h057feedback_support_69e9c079_uploadsafe.csv"
H064 = "submission_h064_contrastive_state_graph_d09a5363_uploadsafe.csv"
H065 = "submission_h065_state_transition_phase_75d5575d_uploadsafe.csv"
H066 = "submission_h066_state_sequence_episode_route_8ca9b9b6_uploadsafe.csv"
H067 = "submission_h067_rowresp_public_state_b10ea6b8_uploadsafe.csv"
H068 = "submission_h068_action_health_3cb4f94c_uploadsafe.csv"

BAD_ANCHORS = [
    "submission_h010_objective_s1s4_v2_uploadsafe.csv",
    "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
    "submission_e323_5508f966_uploadsafe.csv",
    "gpt_pro_pack/q2s1_hidden_state_translation/submissions/submission_e323_5508f966_uploadsafe.csv",
    "jepa/submission_jepa_latent_q2_w0p45.csv",
    "jepa/submission_jepa_latent_residual_probe.csv",
    "jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
]


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    target_policy: str
    k: int
    alpha: float
    mode: str
    max_per_row: int
    q2_cap: int
    min_public: float
    min_invariant: float
    max_shortcut: float
    row_quota: int


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H068MOD = import_module(HITL / "h068_action_health_decoder_jepa.py", "h068mod_for_h069")


def locate(name: str | Path) -> Path | None:
    return H068MOD.locate(name)


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return H068MOD.load_sub(name, sample)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H068MOD.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return H068MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H068MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H068MOD.bce(prob, q)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H068MOD.rank01(values, high)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H068MOD.md_table(frame, n)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    H068MOD.write_submission(sample, prob, path)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def move_toward(base: np.ndarray, target: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * target)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(target)))
    raise ValueError(mode)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h069_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h069_public_private_factor_*_uploadsafe.csv"):
        path.unlink()


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    df = pd.read_csv(HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv")
    out = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    tix = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        out[int(rec["row"]), tix[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(out)


def load_row_frame(path: Path, sample: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    sample_keys = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        sample_keys[col] = pd.to_datetime(sample_keys[col]).dt.strftime("%Y-%m-%d")
    if "row" not in df.columns:
        raise ValueError(f"{path} has no row column")
    if not df.sort_values("row").reset_index(drop=True)[KEYS].equals(sample_keys.reset_index(drop=True)):
        df = df.sort_values("row").reset_index(drop=True)
    if len(df) != len(sample):
        raise ValueError(f"{path} row count mismatch")
    return df.sort_values("row").reset_index(drop=True)


def resolved_bad_anchors(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    for name in BAD_ANCHORS:
        path = locate(name)
        if path is None:
            continue
        try:
            out[name] = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        except Exception:
            continue
    return out


def refit_h068_beta(sample: pd.DataFrame, h057_prob: np.ndarray, q061: np.ndarray) -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
    known = H068MOD.read_public_observations()
    pred_by_file = {}
    for file in known["file"].astype(str):
        pred_by_file[file] = load_sub(file, sample)[TARGETS].to_numpy(dtype=np.float64)
    for file in [H061, H064, H065, H066, H067, H068]:
        if locate(file) is not None and file not in pred_by_file:
            pred_by_file[file] = load_sub(file, sample)[TARGETS].to_numpy(dtype=np.float64)
    fit, model = H068MOD.fit_action_health(known, pred_by_file, h057_prob, q061)
    beta = np.asarray(model["beta"], dtype=np.float64)
    model_table = model["model_table"]
    return beta, fit, model_table


def compute_bad_features(
    h057_prob: np.ndarray,
    q061: np.ndarray,
    bad_probs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    n_cells = h057_prob.size
    target_dir = np.sign((logit(q061) - logit(h057_prob)).reshape(-1))
    rows: dict[str, np.ndarray] = {}
    move_vecs: dict[str, np.ndarray] = {}
    same_direction = np.zeros(n_cells, dtype=np.float64)
    bad_pressure = np.zeros(n_cells, dtype=np.float64)
    bad_count = np.zeros(n_cells, dtype=np.float64)
    for name, prob in bad_probs.items():
        vec = (logit(prob) - logit(h057_prob)).reshape(-1)
        move_vecs[name] = vec
        signed = target_dir * vec
        pressure = np.maximum(signed, 0.0)
        rows[f"bad_pressure_{Path(name).stem[:22]}"] = pressure
        same_direction += (pressure > np.quantile(pressure, 0.90)).astype(float)
        bad_pressure = np.maximum(bad_pressure, pressure)
        bad_count += (pressure > 1.0e-12).astype(float)
    if bad_probs:
        same_direction /= float(len(bad_probs))
        bad_count /= float(len(bad_probs))
    feat = pd.DataFrame(
        {
            "flat_index": np.arange(n_cells, dtype=int),
            "bad_pressure_raw": bad_pressure,
            "bad_pressure_rank": rank01(bad_pressure),
            "bad_top90_rate": same_direction,
            "bad_same_direction_rate": bad_count,
            **rows,
        }
    )
    return feat, move_vecs


def build_factor_table(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h050_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    beta: np.ndarray,
    bad_probs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    h068_cells = pd.read_csv(HITL / "h068_action_health_decoder_jepa" / "h068_cell_action_health.csv")
    h063_rows = load_row_frame(HITL / "h063_human_context_seed_jepa" / "h063_row_scores.csv", sample)
    h064_rows = load_row_frame(HITL / "h064_contrastive_state_graph_jepa" / "h064_row_scores.csv", sample)
    h067_rows = load_row_frame(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv", sample)
    bad_features, bad_vecs = compute_bad_features(h057_prob, q061, bad_probs)

    h068_cells = h068_cells.merge(
        h063_rows[
            [
                "row",
                "h063_row_score",
                "context_consensus",
                "human_social_context",
                "raw_context",
                "episode_near",
            ]
        ].rename(columns={"episode_near": "h063_episode_near"}),
        on="row",
        how="left",
        validate="many_to_one",
    )
    h068_cells = h068_cells.merge(
        h064_rows[
            [
                "row",
                "h064_row_score",
                "graph_consensus",
                "contrast_consensus",
                "seed_context",
                "null_context",
                "null_avoidance",
            ]
        ],
        on="row",
        how="left",
        validate="many_to_one",
    )
    h068_cells = h068_cells.merge(
        h067_rows[
            [
                "row",
                "public_weight",
                "public_responsibility_rank",
                "seed_responsibility_score",
                "extension_score",
                "context_overlap",
                "h066_emission",
                "row_top4_gain_rank",
                "is_h057_seed",
                "is_h050_null",
            ]
        ].rename(
            columns={
                "public_weight": "h067_public_weight",
                "public_responsibility_rank": "h067_public_responsibility_rank",
                "seed_responsibility_score": "h067_seed_responsibility_score",
                "extension_score": "h067_extension_score",
                "context_overlap": "h067_context_overlap",
                "is_h057_seed": "h067_is_h057_seed",
                "is_h050_null": "h067_is_h050_null",
            }
        ),
        on="row",
        how="left",
        validate="many_to_one",
    )
    h068_cells = h068_cells.merge(bad_features, on="flat_index", how="left", validate="one_to_one")
    h068_cells = h068_cells.fillna(0.0)

    h050_changed = (np.abs(h050_prob - h042_prob) > TOL).reshape(-1)
    h057_support = (np.abs(h057_prob - h042_prob) > TOL).reshape(-1)
    h068_cells["h050_route_cell"] = h050_changed.astype(int)
    h068_cells["h057_support_cell_recalc"] = h057_support.astype(int)
    h068_cells["target_is_q2"] = (h068_cells["target"] == "Q2").astype(float)
    h068_cells["target_is_s"] = h068_cells["target"].isin(S_TARGETS).astype(float)
    h068_cells["target_is_nonq2"] = (h068_cells["target"] != "Q2").astype(float)

    # Public score: what known public observations say about the action.
    h068_cells["public_score"] = (
        0.34 * h068_cells["action_rank"]
        + 0.23 * rank01(-h068_cells["pred_cell_delta_to_q061"].to_numpy())
        + 0.18 * h068_cells["h068_cell_health"].rank(method="average", pct=True)
        + 0.10 * h068_cells["row_public_rank"]
        + 0.08 * h068_cells["source_consensus"]
        + 0.07 * h068_cells["q061_gain_rank"]
    )

    # Invariant score: human/context/row-state evidence that does not directly
    # depend on public LB equations.
    h068_cells["invariant_score"] = (
        0.19 * h068_cells["h063_row_score"].rank(method="average", pct=True)
        + 0.14 * h068_cells["context_consensus"].rank(method="average", pct=True)
        + 0.13 * h068_cells["human_social_context"].rank(method="average", pct=True)
        + 0.13 * h068_cells["h064_row_score"].rank(method="average", pct=True)
        + 0.10 * h068_cells["graph_consensus"].rank(method="average", pct=True)
        + 0.09 * h068_cells["contrast_consensus"].rank(method="average", pct=True)
        + 0.08 * h068_cells["null_avoidance"].rank(method="average", pct=True)
        + 0.06 * h068_cells["h067_extension_score"].rank(method="average", pct=True)
        + 0.05 * h068_cells["h067_context_overlap"].rank(method="average", pct=True)
        + 0.03 * h068_cells["h057_support_cell"]
    )

    # Shortcut score: known bad direction, H050-null exposure, and Q2 fragility.
    h068_cells["shortcut_score"] = (
        0.39 * h068_cells["bad_pressure_rank"]
        + 0.21 * h068_cells["bad_top90_rate"]
        + 0.14 * h068_cells["bad_same_direction_rate"]
        + 0.12 * h068_cells["is_h050_null"].astype(float)
        + 0.08 * h068_cells["h067_is_h050_null"].astype(float)
        + 0.04 * h068_cells["target_is_q2"]
        + 0.02 * (1.0 - h068_cells["cell_q061_gain"].clip(lower=0.0).rank(method="average", pct=True))
    )

    h068_cells["public_only_gap"] = h068_cells["public_score"] - h068_cells["invariant_score"]
    h068_cells["private_safe_score"] = (
        0.48 * h068_cells["public_score"]
        + 0.48 * h068_cells["invariant_score"]
        - 0.74 * h068_cells["shortcut_score"]
        + 0.07 * h068_cells["target_is_nonq2"]
    )
    h068_cells["factor_action_score"] = (
        0.42 * h068_cells["private_safe_score"].rank(method="average", pct=True)
        + 0.18 * h068_cells["public_score"].rank(method="average", pct=True)
        + 0.18 * h068_cells["invariant_score"].rank(method="average", pct=True)
        + 0.12 * (1.0 - h068_cells["shortcut_score"].rank(method="average", pct=True))
        + 0.06 * h068_cells["source_consensus"]
        + 0.04 * h068_cells["target_prior_weight"].rank(method="average", pct=True)
    )
    h068_cells.loc[h068_cells["cell_q061_gain"] <= 0, "factor_action_score"] -= 0.50
    return h068_cells.sort_values("factor_action_score", ascending=False).reset_index(drop=True), bad_vecs


def target_allowed(policy: str, target: str) -> bool:
    if policy == "all":
        return True
    if policy == "nonq2":
        return target != "Q2"
    if policy == "s_only":
        return target in S_TARGETS
    if policy == "q2lite":
        return target == "Q2"
    if policy == "q_and_s":
        return target in {"Q1", "Q3", "S1", "S2", "S3", "S4"}
    raise ValueError(policy)


def select_cells(spec: CandidateSpec, factors: pd.DataFrame) -> pd.DataFrame:
    pool = factors[factors["target"].map(lambda target: target_allowed(spec.target_policy, str(target)))].copy()
    pool = pool[pool["cell_q061_gain"] > 0].copy()
    pool = pool[pool["public_score"] >= spec.min_public]
    pool = pool[pool["invariant_score"] >= spec.min_invariant]
    pool = pool[pool["shortcut_score"] <= spec.max_shortcut]
    pool = pool[pool["is_h050_null"] == 0]
    if spec.family == "public_private_core":
        sort_cols = ["factor_action_score", "private_safe_score", "public_score"]
    elif spec.family == "invariant_heavy":
        sort_cols = ["invariant_score", "private_safe_score", "public_score"]
    elif spec.family == "anti_shortcut":
        pool = pool[pool["bad_pressure_rank"] <= min(0.55, spec.max_shortcut + 0.10)]
        sort_cols = ["private_safe_score", "shortcut_score", "invariant_score"]
    elif spec.family == "assignment_balanced":
        sort_cols = ["factor_action_score", "invariant_score", "public_score"]
    elif spec.family == "seed_private":
        pool = pool[(pool["h057_support_cell"] > 0) | (pool["is_h057_seed"] > 0)]
        sort_cols = ["private_safe_score", "factor_action_score", "public_score"]
    else:
        raise ValueError(spec.family)

    ascending = [False] * len(sort_cols)
    if "shortcut_score" in sort_cols:
        ascending[sort_cols.index("shortcut_score")] = True
    pool = pool.sort_values(sort_cols, ascending=ascending)

    selected: list[pd.DataFrame] = []
    row_counts: dict[int, int] = {}
    subject_counts: dict[str, int] = {}
    q2_count = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        if target == "Q2":
            if spec.q2_cap <= 0 or q2_count >= spec.q2_cap:
                continue
        if row_counts.get(row, 0) >= spec.max_per_row:
            continue
        if spec.row_quota > 0 and subject_counts.get(subject, 0) >= spec.row_quota:
            continue
        selected.append(pd.DataFrame([rec]))
        row_counts[row] = row_counts.get(row, 0) + 1
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        q2_count += int(target == "Q2")
        if len(selected) >= spec.k:
            break
    if not selected:
        return pool.iloc[0:0].copy()
    return pd.concat(selected, ignore_index=True)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def apply_candidate(
    spec: CandidateSpec,
    sample: pd.DataFrame,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    factors: pd.DataFrame,
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    selected = select_cells(spec, factors)
    prob = h057_prob.copy()
    moved = move_toward(h057_prob, q061, spec.alpha, spec.mode)
    for rec in selected.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = moved[int(rec["row"]), int(rec["target_index"])]

    changed = np.abs(prob - h057_prob) > TOL
    x = (bce(prob, q061) - bce(h057_prob, q061)).reshape(-1)
    move_vec = (logit(prob) - logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:18]}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    row_public = factors.drop_duplicates("row").sort_values("row")["h067_public_weight"].to_numpy(dtype=np.float64)
    row_delta = (bce(prob, q061) - bce(h057_prob, q061)).mean(axis=1)
    selected_rows = sorted(set(selected["row"].astype(int).tolist())) if len(selected) else []
    meta: dict[str, object] = {
        "candidate_id": "",
        "family": spec.family,
        "target_policy": spec.target_policy,
        "k": spec.k,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "max_per_row": spec.max_per_row,
        "q2_cap": spec.q2_cap,
        "min_public": spec.min_public,
        "min_invariant": spec.min_invariant,
        "max_shortcut": spec.max_shortcut,
        "row_quota": spec.row_quota,
        "selected_cells": int(len(selected)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_public_score": float(selected["public_score"].mean()) if len(selected) else 0.0,
        "mean_invariant_score": float(selected["invariant_score"].mean()) if len(selected) else 0.0,
        "mean_shortcut_score": float(selected["shortcut_score"].mean()) if len(selected) else 1.0,
        "mean_private_safe_score": float(selected["private_safe_score"].mean()) if len(selected) else 0.0,
        "mean_factor_action_score": float(selected["factor_action_score"].mean()) if len(selected) else 0.0,
        "h057_support_selected": int(selected["h057_support_cell"].sum()) if len(selected) else 0,
        "h050_null_selected": int(selected["is_h050_null"].sum()) if len(selected) else 0,
        "selected_subjects": int(selected["subject_id"].nunique()) if len(selected) else 0,
        "selected_rows": ",".join(map(str, selected_rows)),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return clip_prob(prob), meta


def candidate_sweep(
    sample: pd.DataFrame,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    factors: pd.DataFrame,
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    specs: list[CandidateSpec] = []
    policies_by_family = {
        "public_private_core": ["all", "nonq2", "q_and_s"],
        "invariant_heavy": ["nonq2", "q_and_s", "s_only"],
        "anti_shortcut": ["all", "nonq2", "q_and_s"],
        "assignment_balanced": ["all", "nonq2", "q_and_s"],
        "seed_private": ["all", "nonq2"],
    }
    threshold_profiles = [
        # broad public/private intersection
        (0.54, 0.54, 0.50),
        # balanced private-safe field
        (0.60, 0.60, 0.50),
        # explosive factorization: still requires invariant evidence, but lets
        # the shortcut filter become a stress variable rather than a hard veto.
        (0.48, 0.48, 0.72),
        (0.54, 0.48, 0.72),
        (0.48, 0.60, 0.70),
    ]
    for family, target_policies in policies_by_family.items():
        for target_policy in target_policies:
            for k in [360, 520, 700]:
                for alpha in [1.00]:
                    for max_per_row in ([3] if family == "assignment_balanced" else [7]):
                        q2_caps = [36] if target_policy == "all" else [0]
                        for q2_cap in q2_caps:
                            row_quota_values = [0] if family != "assignment_balanced" else [24]
                            for row_quota in row_quota_values:
                                for min_public, min_invariant, max_shortcut in threshold_profiles:
                                    specs.append(
                                        CandidateSpec(
                                            family=family,
                                            target_policy=target_policy,
                                            k=k,
                                            alpha=alpha,
                                            mode="logit",
                                            max_per_row=max_per_row,
                                            q2_cap=q2_cap,
                                            min_public=min_public,
                                            min_invariant=min_invariant,
                                            max_shortcut=max_shortcut,
                                            row_quota=row_quota,
                                        )
                                    )

    rows = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    for spec in specs:
        prob, meta = apply_candidate(spec, sample, h057_prob, q061, factors, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 90:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = (
            f"h069_{spec.family}_{spec.target_policy}_k{spec.k}_a{str(spec.alpha).replace('.', 'p')}_"
            f"{spec.mode}_mp{spec.min_public:.2f}_mi{spec.min_invariant:.2f}_xs{spec.max_shortcut:.2f}_{digest}"
        ).replace(".", "p")
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H069 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["private_rank"] = rank01(cand["mean_private_safe_score"].to_numpy())
    cand["invariant_rank"] = rank01(cand["mean_invariant_score"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_shortcut_score"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["size_score"] = (1.0 - (cand["changed_cells_vs_h057"] - 520).abs() / 650.0).clip(0.0, 1.0)
    cand["q2_risk"] = (cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)).clip(0.0, 1.0)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00030) / 0.00080).clip(0.0, 1.0)
    cand["h069_score"] = (
        0.27 * cand["action_rank"]
        + 0.15 * cand["private_rank"]
        + 0.13 * cand["invariant_rank"]
        + 0.11 * cand["shortcut_avoid_rank"]
        + 0.11 * cand["responsibility_rank"]
        + 0.08 * cand["posterior_rank"]
        + 0.08 * cand["bigbet_scale_score"]
        + 0.05 * cand["bad_avoid_rank"]
        + 0.04 * cand["size_score"]
        + 0.03 * (cand["target_policy"] != "s_only").astype(float)
        - 0.06 * cand["q2_risk"]
        - 0.04 * (cand["h050_null_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h069_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(140).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(df[TARGETS].isna().sum().sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "changed_cells_vs_h057_validation": int((np.abs(prob - h057_prob) > TOL).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and df.duplicated(KEYS).sum() == 0
            and df[TARGETS].isna().sum().sum() == 0
            and np.nanmin(prob) >= 0.0
            and np.nanmax(prob) <= 1.0
        ),
    }


def write_report(
    bad_probs: dict[str, np.ndarray],
    fit: pd.DataFrame,
    model_table: pd.DataFrame,
    factors: pd.DataFrame,
    cand: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    summary = pd.DataFrame(
        [
            {
                "bad_anchors_used": len(bad_probs),
                "h068_action_loo_mae": float(model_table.iloc[0]["loo_mae"]),
                "h068_action_pairwise": float(model_table.iloc[0]["pairwise_sign_acc"]),
                "factor_cells": int(len(factors)),
                "top_candidate": str(decision.loc[0, "selected_candidate_id"]),
                "top_changed_cells": int(decision.loc[0, "changed_cells_vs_h057"]),
                "top_changed_rows": int(decision.loc[0, "changed_rows_vs_h057"]),
                "top_q2_changed": int(decision.loc[0, "Q2_changed_vs_h057"]),
                "top_public_delta": float(decision.loc[0, "public_action_pred_delta_vs_h057"]),
                "top_private_safe_score": float(decision.loc[0, "mean_private_safe_score"]),
                "top_shortcut_score": float(decision.loc[0, "mean_shortcut_score"]),
            }
        ]
    )
    top_factors = factors[
        [
            "row",
            "subject_id",
            "sleep_date",
            "target",
            "public_score",
            "invariant_score",
            "shortcut_score",
            "private_safe_score",
            "factor_action_score",
            "h068_cell_health",
            "cell_q061_gain",
            "bad_pressure_rank",
            "is_h057_seed",
            "is_h050_null",
        ]
    ].head(35)
    report = "\n".join(
        [
            "# H069 Public/Private Factorization HS-JEPA",
            "",
            "Question: can we keep the public-readable H012/H057/H068 signal while",
            "discarding public-only shortcut actions using human/context invariant evidence?",
            "",
            "Design:",
            "",
            "- base: H057 public frontier;",
            "- public view: H068 cell-level public action-health;",
            "- invariant view: H063 human context, H064 contrastive graph, H067 row-state responsibility;",
            "- shortcut view: H050-null rows plus known bad anchors;",
            "- target representation: private-safe row-target correction field toward H061 `q061`;",
            "- action: materialize only cells with public_score and invariant_score high, shortcut_score low.",
            "",
            "Summary:",
            "",
            md_table(summary),
            "",
            "H068 action-health refit:",
            "",
            md_table(model_table, 12),
            "",
            "Known action fit:",
            "",
            md_table(fit, 28),
            "",
            "Top private-safe factor cells:",
            "",
            md_table(top_factors, 35),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(30), 30),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H069 improves by >= 0.001, public/private factorization becomes the main HS-JEPA route.",
            "- If H069 is neutral but safer than H068, the factorization reduces shortcut risk but needs a stronger decoder.",
            "- If H069 loses badly, H068 public action-health is public-only or the invariant context is not yet action-grade.",
            "",
        ]
    )
    (OUT / "h069_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    h057 = load_sub(H057)
    sample = h057[KEYS].copy()
    h057_prob = h057[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = load_sub(H042, sample)[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = load_sub(H050, sample)[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)
    beta, fit, model_table = refit_h068_beta(sample, h057_prob, q061)
    bad_probs = resolved_bad_anchors(sample)
    factors, bad_vecs = build_factor_table(sample, h042_prob, h050_prob, h057_prob, q061, beta, bad_probs)
    cand, probs = candidate_sweep(sample, h057_prob, q061, factors, beta, bad_vecs)

    selected = cand.iloc[0].copy()
    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h069_public_private_factor_{digest}_uploadsafe.csv"
    shutil.copyfile(selected_file, root_file)
    validation = validate_submission(root_file, sample, h057_prob)
    if not validation["upload_safe"]:
        raise RuntimeError(f"selected submission is not upload safe: {validation}")

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_public_private_factorization_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected["resolved_path"]),
                "root_uploadsafe_path": str(root_file.resolve()),
                "worldview": "public-readable action-health must also be invariant-human-state supported and shortcut-negative",
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    pd.DataFrame({"bad_anchor": list(bad_probs.keys())}).to_csv(OUT / "h069_bad_anchors_used.csv", index=False)
    model_table.to_csv(OUT / "h069_h068_action_model_refit.csv", index=False)
    fit.to_csv(OUT / "h069_known_action_fit_refit.csv", index=False)
    factors.to_csv(OUT / "h069_factor_table.csv", index=False)
    cand.to_csv(OUT / "h069_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h069_decision.csv", index=False)
    write_report(bad_probs, fit, model_table, factors, cand, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "Q2_changed_vs_h057",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "mean_invariant_score",
                "mean_shortcut_score",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
