#!/usr/bin/env python3
"""H112: public-residual toxicity solver HS-JEPA.

H111 asked whether H110's local benefit/toxicity field needs a global
assignment boundary.  H112 asks a different question: after the H098
frontier-weighted public equation has explained each known public submission,
which row-target directions are still responsible for the unexplained public
loss residual?

The target representation is not the label and not the raw public score.  It is
the leave-one-out public-equation residual projected back onto signed
row-target actions.  A cell is toxic when it moves in the same direction as
unexpectedly bad public submissions, and safe when it moves opposite to those
residual-bad directions or with unexpectedly good residual directions.
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
OUT = HITL / "h112_public_residual_toxicity_solver_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H111_PATH = HITL / "h111_global_boundary_assignment_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h111mod", H111_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H111_PATH}")
h111mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h111mod
SPEC.loader.exec_module(h111mod)

h110mod = h111mod.h110mod
h109mod = h111mod.h109mod
h102mod = h111mod.h102mod
h100mod = h111mod.h100mod
h097mod = h111mod.h097mod
h085mod = h111mod.h085mod

TARGETS = h111mod.TARGETS
KEYS = h111mod.KEYS
BASE_FILE = h111mod.BASE_FILE
TOL = h111mod.TOL


@dataclass(frozen=True)
class H112Spec:
    name: str
    group: str
    max_cells: int
    max_rows: int
    max_per_subject: int
    max_per_target: int
    q2_cap: int
    amp: float
    cap: float
    pool_top: int
    beam_width: int
    min_score: float
    min_gap: float
    max_residual_toxicity: float
    min_residual_safety: float
    min_family_count: int
    max_bad_weighted_pos: float
    max_bad_max_pos: float
    max_h088_cos: float
    min_good_margin: float
    route_pred_cap: float
    h098_pred_cap: float
    worldview: str


@dataclass
class BeamState:
    selected: tuple[int, ...]
    move_mat: np.ndarray
    rows: frozenset[int]
    subjects: tuple[tuple[str, int], ...]
    targets: tuple[tuple[str, int], ...]
    q2_count: int
    score: float
    axis: dict[str, float]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h112_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h112_residualtox_*.csv"):
        path.unlink()


def materialize(base_prob: np.ndarray, move_mat: np.ndarray) -> np.ndarray:
    return clip_prob(sigmoid(logit(base_prob) + move_mat))


def route_pred(move_flat: np.ndarray, basis_fit_df: pd.DataFrame, basis_fit_moves: np.ndarray, route_fit: h100mod.RouteBasisFit) -> float:
    return h100mod.predict_candidate_delta(move_flat, basis_fit_df, basis_fit_moves, route_fit)


def h098_pred(move_flat: np.ndarray, cell: pd.DataFrame, h098_fit: h097mod.ResponseFit) -> float:
    return h097mod.predict_candidate_delta(move_flat, cell, h098_fit)


def dict_get(items: tuple[tuple[str, int], ...], key: str) -> int:
    return dict(items).get(key, 0)


def dict_inc(items: tuple[tuple[str, int], ...], key: str) -> tuple[tuple[str, int], ...]:
    d = dict(items)
    d[key] = d.get(key, 0) + 1
    return tuple(sorted(d.items()))


def initial_state(shape: tuple[int, int]) -> BeamState:
    return BeamState(
        selected=tuple(),
        move_mat=np.zeros(shape, dtype=np.float64),
        rows=frozenset(),
        subjects=tuple(),
        targets=tuple(),
        q2_count=0,
        score=0.0,
        axis={
            "h102_cum_bad_max_pos": 0.0,
            "h102_cum_bad_weighted_pos": 0.0,
            "h102_cum_h088_axis_cos": 0.0,
            "h102_cum_good_max_cos": 0.0,
            "h102_cum_good_mean_cos": 0.0,
            "h102_cum_good_bad_margin": 0.0,
        },
    )


def load_h098_selected_residuals(public: pd.DataFrame) -> pd.DataFrame:
    pred_path = HITL / "h098_frontier_weighted_action_equation_hsjepa" / "h098_frontier_loo_predictions.csv"
    score_path = HITL / "h098_frontier_weighted_action_equation_hsjepa" / "h098_frontier_model_scores.csv"
    if not (pred_path.exists() and score_path.exists()):
        raise FileNotFoundError("H098 LOO residual files are missing")
    scores = pd.read_csv(score_path).sort_values(["frontier_rank_score", "h088_loo_abs_error"]).reset_index(drop=True)
    selected = scores.iloc[0]
    preds = pd.read_csv(pred_path)
    preds = preds[
        preds["feature_set"].astype(str).eq(str(selected["feature_set"]))
        & np.isclose(preds["alpha"].astype(float), float(selected["alpha"]))
    ].copy()
    if preds.empty:
        raise RuntimeError("selected H098 LOO residual rows missing")
    keep = public[["file", "changed_cells_vs_h057", "mean_abs_logit_move"]].copy()
    out = preds.merge(keep, on="file", how="inner")
    out["actual_minus_pred"] = out["delta_vs_h057"].astype(float) - out["loo_pred_delta"].astype(float)
    out["residual_bad"] = np.maximum(out["actual_minus_pred"].to_numpy(dtype=np.float64), 0.0)
    out["residual_good"] = np.maximum(-out["actual_minus_pred"].to_numpy(dtype=np.float64), 0.0)
    no_action = out["changed_cells_vs_h057"].astype(int).to_numpy() == 0
    out.loc[no_action, ["residual_bad", "residual_good"]] = 0.0
    out["abs_residual"] = np.abs(out["actual_minus_pred"].to_numpy(dtype=np.float64))
    out.loc[no_action, "abs_residual"] = 0.0
    out["h112_fit_feature_set"] = str(selected["feature_set"])
    out["h112_fit_alpha"] = float(selected["alpha"])
    return out.sort_values("abs_residual", ascending=False).reset_index(drop=True)


def residual_source_profiles(residuals: pd.DataFrame, public: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in residuals.to_dict("records"):
        file_name = str(rec["file"])
        pub = public[public["file"].astype(str).eq(file_name)]
        if pub.empty:
            continue
        move = pub.iloc[0]["move_logit"]
        scale = float(np.quantile(np.abs(move), 0.95))
        scale = max(scale, 1.0e-6)
        rows.append(
            {
                "file": file_name,
                "public_lb": float(rec["public_lb"]),
                "delta_vs_h057": float(rec["delta_vs_h057"]),
                "loo_pred_delta": float(rec["loo_pred_delta"]),
                "actual_minus_pred": float(rec["actual_minus_pred"]),
                "abs_residual": float(abs(rec["actual_minus_pred"])),
                "residual_bad": float(rec["residual_bad"]),
                "residual_good": float(rec["residual_good"]),
                "frontier_weight": float(rec.get("frontier_weight", 1.0)),
                "changed_cells_vs_h057": int(rec.get("changed_cells_vs_h057", 0)),
                "mean_abs_logit_move": float(rec.get("mean_abs_logit_move", 0.0)),
                "move_scale_p95": scale,
            }
        )
    return pd.DataFrame(rows).sort_values("abs_residual" if "abs_residual" in residuals.columns else "actual_minus_pred", ascending=False)


def annotate_residual_toxicity(pool: pd.DataFrame, public: pd.DataFrame, residuals: pd.DataFrame) -> pd.DataFrame:
    out = pool.copy()
    pub = public.merge(residuals[["file", "actual_minus_pred", "residual_bad", "residual_good"]], on="file", how="inner")
    if pub.empty:
        raise RuntimeError("no public residual moves")

    moves = np.vstack(pub["move_logit"].to_list()).astype(np.float64)
    scales = np.maximum(np.quantile(np.abs(moves), 0.95, axis=1), 1.0e-6)
    moves_norm = moves / scales[:, None]
    bad = pub["residual_bad"].to_numpy(dtype=np.float64)
    good = pub["residual_good"].to_numpy(dtype=np.float64)
    bad = bad / max(float(bad.max()), 1.0e-12)
    good = good / max(float(good.max()), 1.0e-12)

    raw = out["h110_raw_mean_move"].to_numpy(dtype=np.float64)
    if "h108_raw_mean_move" in out.columns:
        raw = np.where(np.abs(raw) > 1.0e-12, raw, out["h108_raw_mean_move"].to_numpy(dtype=np.float64))
    raw = np.where(np.abs(raw) > 1.0e-12, raw, out["h085_q_move"].to_numpy(dtype=np.float64))
    sign = np.sign(raw)
    sign = np.where(sign == 0.0, 1.0, sign)
    flat = out["flat_index"].astype(int).to_numpy()
    local = moves_norm[:, flat].T
    same = np.maximum(0.0, local * sign[:, None])
    opp = np.maximum(0.0, -local * sign[:, None])

    out["h112_candidate_raw_move"] = raw
    out["h112_same_bad_residual"] = same @ bad / max(float(bad.sum()), 1.0e-12)
    out["h112_opp_bad_residual"] = opp @ bad / max(float(bad.sum()), 1.0e-12)
    out["h112_same_good_residual"] = same @ good / max(float(good.sum()), 1.0e-12)
    out["h112_opp_good_residual"] = opp @ good / max(float(good.sum()), 1.0e-12)

    file_names = pub["file"].astype(str).to_numpy()
    for label, pattern in {
        "h088": "h088",
        "e216": "e216",
        "h010": "h010",
        "lejepa": "lejepa",
        "ordinal": "ordinal",
    }.items():
        mask = np.asarray([pattern in name for name in file_names], dtype=bool)
        if mask.any():
            out[f"h112_same_{label}"] = same[:, mask].mean(axis=1)
            out[f"h112_opp_{label}"] = opp[:, mask].mean(axis=1)
        else:
            out[f"h112_same_{label}"] = 0.0
            out[f"h112_opp_{label}"] = 0.0

    out["h112_residual_toxicity"] = (
        0.34 * rank01(out["h112_same_bad_residual"].to_numpy(), high=True)
        + 0.18 * rank01(out["h112_opp_good_residual"].to_numpy(), high=True)
        + 0.12 * rank01(out["h112_same_e216"].to_numpy(), high=True)
        + 0.10 * rank01(out["h112_same_h010"].to_numpy(), high=True)
        + 0.08 * rank01(out["h112_same_lejepa"].to_numpy(), high=True)
        + 0.06 * out["latent_shortcut_energy"].to_numpy(dtype=np.float64)
        + 0.06 * out["bad_pressure_rank"].to_numpy(dtype=np.float64)
        + 0.04 * out["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        + 0.02 * out["h088_toxicity"].to_numpy(dtype=np.float64)
    )
    out["h112_residual_safety"] = (
        0.28 * rank01(out["h112_opp_bad_residual"].to_numpy(), high=True)
        + 0.24 * rank01(out["h112_same_good_residual"].to_numpy(), high=True)
        + 0.14 * rank01(out["h110_benefit_score"].to_numpy(), high=True)
        + 0.10 * rank01(out["h111_boundary_score"].to_numpy(), high=True)
        + 0.08 * out["h110_anti_h088"].to_numpy(dtype=np.float64)
        + 0.06 * out["h110_align_h057"].to_numpy(dtype=np.float64)
        + 0.05 * out["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.05 * out["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
    )
    out["h112_residual_gap"] = out["h112_residual_safety"] - out["h112_residual_toxicity"]
    out["h112_antidote_score"] = (
        0.45 * rank01(out["h112_opp_bad_residual"].to_numpy(), high=True)
        + 0.20 * rank01(out["h112_opp_e216"].to_numpy(), high=True)
        + 0.16 * rank01(out["h112_opp_h010"].to_numpy(), high=True)
        + 0.10 * out["h110_anti_h088"].to_numpy(dtype=np.float64)
        + 0.09 * out["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
    )
    out["h112_assignment_score"] = (
        0.28 * out["h112_residual_gap"].to_numpy(dtype=np.float64)
        + 0.20 * out["h112_residual_safety"].to_numpy(dtype=np.float64)
        - 0.24 * out["h112_residual_toxicity"].to_numpy(dtype=np.float64)
        + 0.18 * out["h111_boundary_score"].to_numpy(dtype=np.float64)
        + 0.16 * out["h110_benefit_toxicity_gap"].to_numpy(dtype=np.float64)
        + 0.10 * out["h110_benefit_score"].to_numpy(dtype=np.float64)
        - 0.08 * out["h110_toxicity_score"].to_numpy(dtype=np.float64)
        + 0.05 * out["h111_in_h109"].to_numpy(dtype=np.float64)
        + 0.04 * out["h111_h108_rejected"].to_numpy(dtype=np.float64)
        - 0.04 * out["target"].astype(str).eq("Q2").astype(float).to_numpy()
    )

    h111_selected_path = HITL / "h111_global_boundary_assignment_solver_hsjepa" / "h111_selected_cells.csv"
    decision_path = HITL / "h111_global_boundary_assignment_solver_hsjepa" / "h111_decision.csv"
    h111_selected: set[int] = set()
    if h111_selected_path.exists() and decision_path.exists():
        decision = pd.read_csv(decision_path).iloc[0]
        h111_id = str(decision["selected_candidate_id"])
        h111_cells = pd.read_csv(h111_selected_path)
        h111_selected = set(h111_cells[h111_cells["candidate_id"].astype(str).eq(h111_id)]["flat_index"].astype(int))
    out["h112_in_h111_selected"] = out["flat_index"].astype(int).isin(h111_selected).astype(float)
    return out.sort_values("h112_assignment_score", ascending=False).reset_index(drop=True)


def candidate_specs() -> list[H112Spec]:
    return [
        H112Spec(
            name="residual_antitoxic_kernel_c52_a078",
            group="antitoxic_kernel",
            max_cells=52,
            max_rows=30,
            max_per_subject=12,
            max_per_target=16,
            q2_cap=0,
            amp=0.78,
            cap=0.30,
            pool_top=120,
            beam_width=88,
            min_score=0.22,
            min_gap=-0.08,
            max_residual_toxicity=0.60,
            min_residual_safety=0.40,
            min_family_count=2,
            max_bad_weighted_pos=0.006,
            max_bad_max_pos=0.034,
            max_h088_cos=-0.003,
            min_good_margin=0.012,
            route_pred_cap=0.000130,
            h098_pred_cap=0.000085,
            worldview="safe cells are H110/H111 kernel actions whose signed direction avoids unexplained public residual toxicity",
        ),
        H112Spec(
            name="residual_h010_e216_antidote_c72_a064",
            group="bad_residual_antidote",
            max_cells=72,
            max_rows=46,
            max_per_subject=12,
            max_per_target=22,
            q2_cap=0,
            amp=0.64,
            cap=0.26,
            pool_top=170,
            beam_width=96,
            min_score=0.15,
            min_gap=-0.16,
            max_residual_toxicity=0.64,
            min_residual_safety=0.34,
            min_family_count=2,
            max_bad_weighted_pos=0.010,
            max_bad_max_pos=0.048,
            max_h088_cos=-0.002,
            min_good_margin=0.008,
            route_pred_cap=0.000170,
            h098_pred_cap=0.000095,
            worldview="the missing public/private field is an antidote to H010/E216 unexplained bad residual directions, not merely H088 opposition",
        ),
        H112Spec(
            name="residual_h111_pruned_boundary_c86_a056",
            group="h111_pruned",
            max_cells=86,
            max_rows=52,
            max_per_subject=13,
            max_per_target=24,
            q2_cap=2,
            amp=0.56,
            cap=0.23,
            pool_top=180,
            beam_width=100,
            min_score=0.14,
            min_gap=-0.18,
            max_residual_toxicity=0.66,
            min_residual_safety=0.32,
            min_family_count=2,
            max_bad_weighted_pos=0.014,
            max_bad_max_pos=0.060,
            max_h088_cos=0.000,
            min_good_margin=0.004,
            route_pred_cap=0.000200,
            h098_pred_cap=0.000105,
            worldview="H111 was directionally right but needs pruning by leave-one-out public residual toxicity before becoming action-grade",
        ),
        H112Spec(
            name="residual_broad_safety_c140_a044",
            group="broad_safety",
            max_cells=140,
            max_rows=78,
            max_per_subject=13,
            max_per_target=34,
            q2_cap=5,
            amp=0.44,
            cap=0.19,
            pool_top=230,
            beam_width=104,
            min_score=0.08,
            min_gap=-0.24,
            max_residual_toxicity=0.70,
            min_residual_safety=0.28,
            min_family_count=2,
            max_bad_weighted_pos=0.016,
            max_bad_max_pos=0.070,
            max_h088_cos=0.000,
            min_good_margin=0.002,
            route_pred_cap=0.000230,
            h098_pred_cap=0.000115,
            worldview="a broad action field can survive if the assignment solver explicitly minimizes observed public residual toxicity",
        ),
        H112Spec(
            name="residual_q2_micro_c16_a038",
            group="q2_micro",
            max_cells=16,
            max_rows=16,
            max_per_subject=5,
            max_per_target=16,
            q2_cap=16,
            amp=0.38,
            cap=0.16,
            pool_top=80,
            beam_width=64,
            min_score=0.06,
            min_gap=-0.20,
            max_residual_toxicity=0.72,
            min_residual_safety=0.26,
            min_family_count=2,
            max_bad_weighted_pos=0.008,
            max_bad_max_pos=0.040,
            max_h088_cos=-0.002,
            min_good_margin=0.004,
            route_pred_cap=0.000260,
            h098_pred_cap=0.000100,
            worldview="Q2 can only reopen as a tiny residual-safe micro-action, not as a broad target route",
        ),
    ]


def group_allowed(row: dict[str, object], spec: H112Spec) -> bool:
    target = str(row["target"])
    if spec.group == "antitoxic_kernel":
        return target != "Q2" and (
            bool(row.get("h111_in_h109", False))
            or bool(row.get("h111_h108_kept", False))
            or bool(row.get("h111_in_h110", False))
        )
    if spec.group == "bad_residual_antidote":
        return target != "Q2" and float(row.get("h112_antidote_score", 0.0)) >= 0.42
    if spec.group == "h111_pruned":
        return bool(row.get("h112_in_h111_selected", False)) or bool(row.get("h111_in_h110", False))
    if spec.group == "broad_safety":
        return True
    if spec.group == "q2_micro":
        return target == "Q2"
    raise ValueError(spec.group)


def state_rank_score(state: BeamState) -> float:
    return (
        state.score
        + 0.16 * max(state.axis["h102_cum_good_bad_margin"], 0.0)
        + 0.06 * max(-state.axis["h102_cum_h088_axis_cos"], 0.0)
        + 0.006 * len(state.selected)
        - 0.52 * max(state.axis["h102_cum_bad_weighted_pos"], 0.0)
        - 0.28 * max(state.axis["h102_cum_bad_max_pos"], 0.0)
        - 0.24 * max(state.axis["h102_cum_h088_axis_cos"], 0.0)
    )


def select_with_beam(
    pool: pd.DataFrame,
    spec: H112Spec,
    base_shape: tuple[int, int],
    bad_axes: pd.DataFrame,
    bad_moves: np.ndarray,
    good_moves: np.ndarray,
) -> tuple[pd.DataFrame, np.ndarray, dict[str, float]]:
    work = pool.copy()
    work["h112_move"] = np.clip(work["h112_candidate_raw_move"].to_numpy(dtype=np.float64) * spec.amp, -spec.cap, spec.cap)
    work = work[np.abs(work["h112_move"].to_numpy(dtype=np.float64)) > 1.0e-10]
    work = work[work["h112_assignment_score"].to_numpy(dtype=np.float64) >= spec.min_score]
    work = work[work["h112_residual_gap"].to_numpy(dtype=np.float64) >= spec.min_gap]
    work = work[work["h112_residual_toxicity"].to_numpy(dtype=np.float64) <= spec.max_residual_toxicity]
    work = work[work["h112_residual_safety"].to_numpy(dtype=np.float64) >= spec.min_residual_safety]
    work = work[work["h110_family_count"].astype(int) >= spec.min_family_count]
    work = work[work.apply(lambda row: group_allowed(row, spec), axis=1)]
    work = work.sort_values(["h112_assignment_score", "h112_residual_gap"], ascending=[False, False]).head(spec.pool_top).reset_index(drop=True)

    states = [initial_state(base_shape)]
    for idx, rec in enumerate(work.to_dict("records")):
        next_states = states.copy()
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        target_index = int(rec["target_index"])
        for state in states:
            if len(state.selected) >= spec.max_cells:
                continue
            if row not in state.rows and len(state.rows) >= spec.max_rows:
                continue
            if row not in state.rows and dict_get(state.subjects, subject) + 1 > spec.max_per_subject:
                continue
            if dict_get(state.targets, target) >= spec.max_per_target:
                continue
            if target == "Q2" and state.q2_count >= spec.q2_cap:
                continue
            tmp = state.move_mat.copy()
            tmp[row, target_index] = float(rec["h112_move"])
            axis = h102mod.cumulative_axis_metrics(tmp.reshape(-1), bad_axes, bad_moves, good_moves)
            if axis["h102_cum_bad_weighted_pos"] > spec.max_bad_weighted_pos:
                continue
            if axis["h102_cum_bad_max_pos"] > spec.max_bad_max_pos:
                continue
            if axis["h102_cum_h088_axis_cos"] > spec.max_h088_cos:
                continue
            if axis["h102_cum_good_bad_margin"] < spec.min_good_margin:
                continue
            bonus = (
                float(rec["h112_assignment_score"])
                + 0.10 * float(rec["h112_residual_safety"])
                + 0.06 * float(rec["h112_antidote_score"])
                + 0.05 * float(rec["h111_h108_rejected"])
                + 0.03 * float(rec["h111_in_h109"])
                - 0.10 * float(rec["h112_residual_toxicity"])
            )
            next_states.append(
                BeamState(
                    selected=state.selected + (idx,),
                    move_mat=tmp,
                    rows=state.rows | {row},
                    subjects=dict_inc(state.subjects, subject) if row not in state.rows else state.subjects,
                    targets=dict_inc(state.targets, target),
                    q2_count=state.q2_count + int(target == "Q2"),
                    score=state.score + bonus,
                    axis=axis,
                )
            )
        states = sorted(next_states, key=state_rank_score, reverse=True)[: spec.beam_width]

    final_states = [s for s in states if s.selected]
    if not final_states:
        return pd.DataFrame(), np.zeros(base_shape, dtype=np.float64), initial_state(base_shape).axis
    best = sorted(final_states, key=state_rank_score, reverse=True)[0]
    selected = work.iloc[list(best.selected)].copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    selected["h097_move_col"] = "h112_move"
    selected["h112_beam_rank_score"] = state_rank_score(best)
    return selected, best.move_mat, best.axis


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    selected_cells: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    h098_fit: h097mod.ResponseFit,
    route_fit: h100mod.RouteBasisFit,
    basis_fit_df: pd.DataFrame,
    basis_fit_moves: np.ndarray,
    spec: H112Spec,
    path: Path,
    axis: dict[str, float],
) -> dict[str, object]:
    proxy = h097mod.H097Spec(
        name=spec.name,
        mode="public_residual_toxicity_solver",
        target_group=spec.group,
        k=spec.max_cells,
        alpha=spec.amp,
        cap=spec.cap,
        min_score=spec.min_score,
        worldview=spec.worldview,
    )
    out = h097mod.evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected_cells, cell, sample, h098_fit, proxy, path)
    out.update(axis)
    out["route_basis_pred_delta_vs_h057"] = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
    out["selected_mean_residual_toxicity"] = float(selected_cells["h112_residual_toxicity"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_residual_safety"] = float(selected_cells["h112_residual_safety"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_residual_gap"] = float(selected_cells["h112_residual_gap"].mean()) if len(selected_cells) else 0.0
    out["selected_mean_antidote_score"] = float(selected_cells["h112_antidote_score"].mean()) if len(selected_cells) else 0.0
    out["selected_same_bad_residual"] = float(selected_cells["h112_same_bad_residual"].mean()) if len(selected_cells) else 0.0
    out["selected_opp_bad_residual"] = float(selected_cells["h112_opp_bad_residual"].mean()) if len(selected_cells) else 0.0
    out["selected_same_good_residual"] = float(selected_cells["h112_same_good_residual"].mean()) if len(selected_cells) else 0.0
    out["selected_opp_good_residual"] = float(selected_cells["h112_opp_good_residual"].mean()) if len(selected_cells) else 0.0
    out["selected_h111_cells"] = int(selected_cells["h112_in_h111_selected"].sum()) if len(selected_cells) else 0
    out["selected_h108_rejected_cells"] = int(selected_cells["h111_h108_rejected"].sum()) if len(selected_cells) else 0
    out["selected_h109_cells"] = int(selected_cells["h111_in_h109"].sum()) if len(selected_cells) else 0
    out["selected_mean_family_count"] = float(selected_cells["h110_family_count"].mean()) if len(selected_cells) else 0.0
    out["h112_information_mass"] = (
        0.42 * min(float(out["selected_cells"]) / 42.0, 1.0)
        + 0.24 * min(float(out["changed_rows_vs_h057"]) / 24.0, 1.0)
        + 0.18 * min(float(out["selected_h111_cells"]) / 24.0, 1.0)
        + 0.10 * min(float(out["selected_h108_rejected_cells"]) / 10.0, 1.0)
        + 0.06 * min(float(out["selected_mean_family_count"]) / 4.0, 1.0)
    )
    out["h112_score"] = (
        120.0 * (-float(out["model_pred_delta_vs_h057"]))
        + 105.0 * (-float(out["route_basis_pred_delta_vs_h057"]))
        + 0.20 * float(out["h112_information_mass"])
        + 0.16 * float(out["selected_mean_residual_safety"])
        + 0.14 * float(out["selected_mean_residual_gap"])
        + 0.10 * float(out["selected_mean_antidote_score"])
        + 0.08 * float(out["anti_h088_direction_rate"])
        + 0.06 * float(out["h057_positive_align_rate"])
        + 0.05 * max(float(out["h102_cum_good_bad_margin"]), 0.0)
        + 0.04 * max(-float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.20 * float(out["selected_mean_residual_toxicity"])
        - 0.12 * max(float(out["h102_cum_h088_axis_cos"]), 0.0)
        - 0.52 * max(float(out["h102_cum_bad_weighted_pos"]), 0.0)
        - 0.30 * max(float(out["h102_cum_bad_max_pos"]), 0.0)
        - 0.22 * max(float(out["max_positive_bad_cosine"]), 0.0)
        - 22.0 * max(float(out["hard_diag_delta_vs_h057"]), 0.0)
        - 10.0 * max(float(out["posterior_delta_vs_h057"]), 0.0)
    )
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell, h098_fit, route_fit, basis_fit_df, basis_fit_moves, bad_axes, bad_moves, _good_axes, good_moves = h109mod.build_context()
    public = h097mod.load_public_moves(sample, base_prob)
    residuals = load_h098_selected_residuals(public)
    residual_sources = residual_source_profiles(residuals, public)
    pool = annotate_residual_toxicity(h111mod.load_boundary_pool(), public, residuals)

    audit = pd.DataFrame(
        [
            {
                "group": "all_pool",
                "cells": int(len(pool)),
                "mean_residual_toxicity": float(pool["h112_residual_toxicity"].mean()),
                "mean_residual_safety": float(pool["h112_residual_safety"].mean()),
                "mean_residual_gap": float(pool["h112_residual_gap"].mean()),
                "mean_assignment_score": float(pool["h112_assignment_score"].mean()),
            },
            {
                "group": "h111_selected",
                "cells": int(pool["h112_in_h111_selected"].sum()),
                "mean_residual_toxicity": float(pool.loc[pool["h112_in_h111_selected"].astype(bool), "h112_residual_toxicity"].mean()),
                "mean_residual_safety": float(pool.loc[pool["h112_in_h111_selected"].astype(bool), "h112_residual_safety"].mean()),
                "mean_residual_gap": float(pool.loc[pool["h112_in_h111_selected"].astype(bool), "h112_residual_gap"].mean()),
                "mean_assignment_score": float(pool.loc[pool["h112_in_h111_selected"].astype(bool), "h112_assignment_score"].mean()),
            },
            {
                "group": "h110_selected",
                "cells": int(pool["h111_in_h110"].sum()),
                "mean_residual_toxicity": float(pool.loc[pool["h111_in_h110"].astype(bool), "h112_residual_toxicity"].mean()),
                "mean_residual_safety": float(pool.loc[pool["h111_in_h110"].astype(bool), "h112_residual_safety"].mean()),
                "mean_residual_gap": float(pool.loc[pool["h111_in_h110"].astype(bool), "h112_residual_gap"].mean()),
                "mean_assignment_score": float(pool.loc[pool["h111_in_h110"].astype(bool), "h112_assignment_score"].mean()),
            },
        ]
    )

    candidate_rows = []
    selected_frames = []
    top_frames = []
    for spec in candidate_specs():
        selected_cells, move_mat, axis = select_with_beam(pool, spec, base_prob.shape, bad_axes, bad_moves, good_moves)
        if selected_cells.empty:
            continue
        rpred = route_pred(move_mat.reshape(-1), basis_fit_df, basis_fit_moves, route_fit)
        cpred = h098_pred(move_mat.reshape(-1), cell, h098_fit)
        if rpred > spec.route_pred_cap:
            continue
        if cpred > spec.h098_pred_cap:
            continue
        prob = materialize(base_prob, move_mat)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h112_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(
            candidate_id,
            prob,
            move_mat,
            selected_cells,
            cell,
            sample,
            base_prob,
            h098_fit,
            route_fit,
            basis_fit_df,
            basis_fit_moves,
            spec,
            path,
            axis,
        )
        candidate_rows.append(metrics)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected_cells)
        top = pool.sort_values(["h112_assignment_score", "h112_residual_gap"], ascending=[False, False]).head(420).copy()
        top.insert(0, "candidate_id", candidate_id)
        top_frames.append(top)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H112 candidates")
    candidates = candidates.sort_values(["h112_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h112_residualtox_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)

    decision = {
        "decision": "promote_h112_public_residual_toxicity_solver",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "known_public_observations": int(len(public)),
        "residual_fit_feature_set": str(residuals["h112_fit_feature_set"].iloc[0]),
        "residual_fit_alpha": float(residuals["h112_fit_alpha"].iloc[0]),
        "largest_bad_residual_file": str(residuals.sort_values("residual_bad", ascending=False)["file"].iloc[0]),
        "largest_bad_residual": float(residuals["residual_bad"].max()),
        "largest_good_residual_file": str(residuals.sort_values("residual_good", ascending=False)["file"].iloc[0]),
        "largest_good_residual": float(residuals["residual_good"].max()),
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    pool.to_csv(OUT / "h112_residual_toxicity_pool.csv", index=False)
    residuals.to_csv(OUT / "h112_public_residuals.csv", index=False)
    residual_sources.to_csv(OUT / "h112_residual_sources.csv", index=False)
    audit.to_csv(OUT / "h112_residual_audit.csv", index=False)
    candidates.to_csv(OUT / "h112_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h112_selected_cells.csv", index=False)
    pd.concat(top_frames, ignore_index=True).to_csv(OUT / "h112_top_residual_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h112_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "changed_rows_vs_h057",
        "Q1_changed_vs_h057",
        "Q2_changed_vs_h057",
        "Q3_changed_vs_h057",
        "S1_changed_vs_h057",
        "S2_changed_vs_h057",
        "S3_changed_vs_h057",
        "S4_changed_vs_h057",
        "model_pred_delta_vs_h057",
        "route_basis_pred_delta_vs_h057",
        "h102_cum_bad_weighted_pos",
        "h102_cum_h088_axis_cos",
        "h102_cum_good_bad_margin",
        "selected_mean_residual_toxicity",
        "selected_mean_residual_safety",
        "selected_mean_residual_gap",
        "selected_mean_antidote_score",
        "selected_h111_cells",
        "selected_h108_rejected_cells",
        "h112_information_mass",
        "h112_score",
        "file",
    ]
    report = f"""# H112 Public-Residual Toxicity Solver HS-JEPA

Question: after the H098 public equation explains known submissions, can the
leave-one-out residual be projected back to row-target actions as the actual
public/private toxicity field?

Residual sources:

{md_table(residuals[["file", "public_lb", "delta_vs_h057", "loo_pred_delta", "actual_minus_pred", "residual_bad", "residual_good", "frontier_weight"]], 18)}

Pool audit:

{md_table(audit, 10)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H112 improves over H111/H110, the missing HS-JEPA decoder is not another
  context encoder or local toxicity score. It is a public-residual toxicity
  assignment equation.
- If H111 improves more, residual projection over-pruned or inverted useful
  globally safe cells.
- If H110 improves more, H098 residuals are too underidentified and local
  benefit-toxicity remains the cleaner action-grade field.
- If H109 improves more, public-safe action is still a tiny coefficient kernel.
"""
    (OUT / "h112_report.md").write_text(report, encoding="utf-8")

    print("H112 selected candidate")
    print(candidates[cols].head(10).to_string(index=False))
    print("\nDecision")
    print(pd.DataFrame([decision])[["decision", "selected_candidate_id", "root_uploadsafe_path", "root_upload_safe"]].to_string(index=False))


if __name__ == "__main__":
    run()
