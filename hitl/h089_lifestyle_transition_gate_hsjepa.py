#!/usr/bin/env python3
"""H089: lifestyle-transition gate HS-JEPA.

H087/H088 exposed a decoder conflict: posterior-friendly actions and
hard/private-friendly actions are not the same object.  H089 tests a larger
worldview:

    public/private decoder choice is controlled by row-level human lifestyle
    state transitions, not by route support alone.

The context is the human/social story state built from raw logs in E268/H072,
plus within-subject temporal deltas.  The target representation is a hidden
decoder-head assignment:

    transition/public head, stable/private head, objective-body head,
    or calendar-Q2 head.

This is a JEPA-style context-to-hidden-state experiment.  It does not directly
map human stories to labels; it asks whether those stories decide which
row-target value law should translate a route into probabilities.
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
OUT = HITL / "h089_lifestyle_transition_gate_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h087mod = import_module(HITL / "h087_route_value_law_hsjepa.py", "h087mod_for_h089")
h088mod = import_module(HITL / "h088_dual_state_value_gate_hsjepa.py", "h088mod_for_h089")
h072mod = import_module(HITL / "h072_human_social_state_engine_jepa.py", "h072mod_for_h089")

TARGETS = h087mod.TARGETS
KEYS = h087mod.KEYS
TOL = h087mod.TOL
BASE_FILE = h087mod.BASE_FILE

POSTERIOR_MODES = {"h085_q", "source_mean", "q_source_bridge", "h085_hard_bridge", "triad_consensus"}
PRIVATE_MODES = {"hard_q", "hard_binary_edge", "hard_source_bridge", "h085_hard_bridge", "triad_consensus"}
OBJECTIVE_TARGETS = {"Q3", "S1", "S2", "S3", "S4"}


@dataclass(frozen=True)
class H089Spec:
    name: str
    profile: str
    target_group: str
    max_routes: int
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_h089_score: float
    min_state_score: float
    alpha: float
    cap: float
    novelty: str


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h089_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h089_lifestyle_transition_gate_*_uploadsafe.csv"):
        path.unlink()


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h087mod.clip_prob(np.asarray(x, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h087mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def safe_id(text: str, limit: int = 132) -> str:
    return h087mod.safe_id(text, limit=limit)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h087mod.md_table(frame, n=n)


def parse_targets(text: object) -> list[str]:
    return [target for target in str(text).split(",") if target]


def target_allowed(targets: list[str], group: str) -> bool:
    target_set = set(targets)
    if group == "all":
        return True
    if group == "nonq2":
        return "Q2" not in target_set
    if group == "objective":
        return bool(target_set) and target_set.issubset(OBJECTIVE_TARGETS)
    if group == "q_route":
        return bool(target_set & {"Q1", "Q2", "Q3"}) and len(target_set & {"S1", "S2", "S3", "S4"}) <= 1
    if group == "q2_route":
        return "Q2" in target_set
    raise ValueError(group)


def build_transition_state(sample: pd.DataFrame) -> pd.DataFrame:
    family = h072mod.build_family_features(sample).sort_values("row").reset_index(drop=True)
    fam_cols = [f"family_{name}" for name in h072mod.FAMILY_NAMES]
    broad_cols = [
        "arousal_pressure",
        "recovery_pressure",
        "routine_calendar_pressure",
        "objective_measure_pressure",
        "family_entropy",
        "family_max_score",
    ]
    state_cols = fam_cols + broad_cols

    rows: list[pd.DataFrame] = []
    for _, group in family.sort_values(["subject_id", "lifelog_date"]).groupby("subject_id", sort=False):
        g = group.copy()
        values = g[state_cols].to_numpy(dtype=np.float64)
        prev_values = np.vstack([values[0:1], values[:-1]])
        next_values = np.vstack([values[1:], values[-1:]])
        subj_median = np.nanmedian(values, axis=0, keepdims=True)
        g["prev_state_delta"] = np.mean(np.abs(values - prev_values), axis=1)
        g["next_state_delta"] = np.mean(np.abs(next_values - values), axis=1)
        g["two_sided_state_delta"] = 0.55 * g["prev_state_delta"] + 0.45 * g["next_state_delta"]
        g["state_acceleration"] = np.mean(np.abs(next_values - 2.0 * values + prev_values), axis=1)
        g["subject_state_novelty"] = np.mean(np.abs(values - subj_median), axis=1)
        g["subject_row_order"] = np.arange(len(g), dtype=float)
        g["subject_edge_proximity"] = np.maximum(
            1.0 - np.minimum(g["subject_row_order"], len(g) - 1 - g["subject_row_order"]) / 4.0,
            0.0,
        )
        rows.append(g)

    state = pd.concat(rows, ignore_index=True).sort_values("row").reset_index(drop=True)
    state["transition_energy_raw"] = (
        0.34 * rank01(state["two_sided_state_delta"].to_numpy())
        + 0.24 * rank01(state["state_acceleration"].to_numpy())
        + 0.22 * rank01(state["subject_state_novelty"].to_numpy())
        + 0.10 * rank01(state["family_entropy"].to_numpy())
        + 0.10 * rank01(state["subject_edge_proximity"].to_numpy())
    )
    calendar = np.maximum.reduce(
        [
            state["month_start_prox"].to_numpy(dtype=float),
            state["month_end_prox"].to_numpy(dtype=float),
            state["payday_25_prox"].to_numpy(dtype=float),
            state["is_weekend"].to_numpy(dtype=float),
        ]
    )
    state["calendar_shock_score"] = rank01(calendar)
    state["social_arousal_score"] = np.clip(
        0.42 * state["arousal_pressure"]
        + 0.20 * state["family_social_load"]
        + 0.18 * state["family_bedtime_arousal"]
        + 0.12 * state["family_nocturnal_awake"]
        + 0.08 * rank01(state["transition_energy_raw"].to_numpy()),
        0.0,
        1.0,
    )
    state["public_transition_score"] = np.clip(
        0.36 * rank01(state["transition_energy_raw"].to_numpy())
        + 0.22 * state["social_arousal_score"]
        + 0.15 * state["routine_calendar_pressure"]
        + 0.12 * state["family_cashflow_stress"]
        + 0.10 * state["calendar_shock_score"]
        + 0.05 * state["family_weekend_rhythm"],
        0.0,
        1.0,
    )
    state["private_stable_score"] = np.clip(
        0.30 * state["recovery_pressure"]
        + 0.20 * state["family_routine_anchor"]
        + 0.16 * state["family_measurement_confidence"]
        + 0.14 * (1.0 - rank01(state["transition_energy_raw"].to_numpy()))
        + 0.12 * state["family_recovery_rest"]
        + 0.08 * (1.0 - state["social_arousal_score"]),
        0.0,
        1.0,
    )
    state["objective_body_score"] = np.clip(
        0.42 * state["objective_measure_pressure"]
        + 0.24 * state["family_measurement_confidence"]
        + 0.18 * state["family_body_fatigue"]
        + 0.10 * state["family_nocturnal_awake"]
        + 0.06 * (1.0 - state["family_cashflow_stress"]),
        0.0,
        1.0,
    )
    state["calendar_q2_score"] = np.clip(
        0.32 * state["family_cashflow_stress"]
        + 0.24 * state["routine_calendar_pressure"]
        + 0.20 * state["calendar_shock_score"]
        + 0.14 * state["family_routine_pressure"]
        + 0.10 * state["family_weekend_rhythm"],
        0.0,
        1.0,
    )
    head_cols = [
        "public_transition_score",
        "private_stable_score",
        "objective_body_score",
        "calendar_q2_score",
    ]
    head_names = ["public_transition", "private_stable", "objective_body", "calendar_q2"]
    head_values = state[head_cols].to_numpy(dtype=np.float64)
    state["lifestyle_head"] = [head_names[i] for i in head_values.argmax(axis=1)]
    state["lifestyle_head_score"] = head_values.max(axis=1)
    state["lifestyle_head_margin"] = np.sort(head_values, axis=1)[:, -1] - np.sort(head_values, axis=1)[:, -2]
    keep = [
        "row",
        *KEYS,
        "family_top",
        *fam_cols,
        "arousal_pressure",
        "recovery_pressure",
        "routine_calendar_pressure",
        "objective_measure_pressure",
        "prev_state_delta",
        "next_state_delta",
        "two_sided_state_delta",
        "state_acceleration",
        "subject_state_novelty",
        "transition_energy_raw",
        "calendar_shock_score",
        "social_arousal_score",
        "public_transition_score",
        "private_stable_score",
        "objective_body_score",
        "calendar_q2_score",
        "lifestyle_head",
        "lifestyle_head_score",
        "lifestyle_head_margin",
    ]
    return state[keep]


def build_route_preference_support(actions: pd.DataFrame, state: pd.DataFrame) -> pd.DataFrame:
    _hyp, mined = h072mod.hypothesis_route_table()
    pref = h072mod.normalize_pref(h072mod.MANUAL_ROUTE_PREF, mined)
    pref = pref.pivot_table(
        index="story_family",
        columns="route_name",
        values="route_pref",
        aggfunc="sum",
        fill_value=0.0,
    )
    family_names = list(h072mod.FAMILY_NAMES)
    fam_cols = [f"family_{name}" for name in family_names]
    row_family = state.set_index("row")[fam_cols]

    support = []
    best_family = []
    for rec in actions[["row", "route_name"]].to_dict("records"):
        row = int(rec["row"])
        route = str(rec["route_name"])
        fam_values = row_family.loc[row].to_numpy(dtype=np.float64)
        route_pref = np.array([float(pref.loc[name, route]) if route in pref.columns else 0.0 for name in family_names])
        contrib = fam_values * route_pref
        support.append(float(contrib.sum()))
        best_family.append(family_names[int(contrib.argmax())] if contrib.size else "")
    out = actions.copy()
    out["human_route_support"] = support
    out["human_route_support_rank"] = rank01(np.asarray(support, dtype=np.float64))
    out["human_best_family"] = best_family
    return out


def add_lifestyle_scores(actions: pd.DataFrame, state: pd.DataFrame) -> pd.DataFrame:
    out = actions.merge(state, on="row", how="left", validate="many_to_one", suffixes=("", "_state"))
    out = build_route_preference_support(out, state)

    route_targets = out["targets"].map(parse_targets)
    out["has_q2"] = route_targets.map(lambda targets: "Q2" in targets).astype(float)
    out["has_q"] = route_targets.map(lambda targets: bool(set(targets) & {"Q1", "Q2", "Q3"})).astype(float)
    out["is_objective_route"] = route_targets.map(lambda targets: bool(targets) and set(targets).issubset(OBJECTIVE_TARGETS)).astype(float)
    out["is_full_state_route"] = (out["route_name"].astype(str) == "full_state").astype(float)
    out["is_recovery_route"] = out["route_name"].astype(str).isin(["recovery_route", "nonq2_full", "s_stage"]).astype(float)

    out["posterior_mode"] = out["value_mode"].astype(str).isin(POSTERIOR_MODES).astype(float)
    out["private_mode"] = out["value_mode"].astype(str).isin(PRIVATE_MODES).astype(float)
    out["posterior_gain_pos"] = (-out["posterior_delta_sum"].astype(float)).clip(lower=0.0)
    out["hard_gain_pos"] = (-out["hard_delta_sum"].astype(float)).clip(lower=0.0)
    out["source_gain_pos"] = (-out["source_proxy_sum"].astype(float)).clip(lower=0.0)
    out["resp_gain_pos"] = (-out["resp_delta_sum"].astype(float)).clip(lower=0.0)
    out["source_safe"] = (out["source_proxy_sum"].astype(float) <= 2.0e-6).astype(float)
    out["hard_safe"] = (out["hard_delta_sum"].astype(float) <= 1.0e-6).astype(float)
    out["posterior_safe"] = (out["posterior_delta_sum"].astype(float) <= 1.0e-6).astype(float)
    out["dual_pareto"] = out.get("dual_pareto", 0).fillna(0).astype(float)

    out["public_head_score"] = (
        0.30 * out["public_transition_score"]
        + 0.16 * out["social_arousal_score"]
        + 0.16 * out["posterior_gain_rank"]
        + 0.12 * out["source_gain_rank"]
        + 0.10 * out["posterior_mode"]
        + 0.08 * out["human_route_support_rank"]
        + 0.08 * out["posterior_safe"]
    )
    out["private_head_score"] = (
        0.30 * out["private_stable_score"]
        + 0.18 * out["hard_gain_rank"]
        + 0.14 * out["dual_pareto"]
        + 0.12 * out["private_mode"]
        + 0.10 * out["hard_safe"]
        + 0.08 * out["is_recovery_route"]
        + 0.08 * out["human_route_support_rank"]
    )
    out["objective_head_score"] = (
        0.34 * out["objective_body_score"]
        + 0.18 * out["is_objective_route"]
        + 0.14 * out["h082_rank"]
        + 0.12 * out["source_gain_rank"]
        + 0.10 * out["source_safe"]
        + 0.07 * out["human_route_support_rank"]
        + 0.05 * out["private_mode"]
    )
    out["calendar_q2_head_score"] = (
        0.34 * out["calendar_q2_score"]
        + 0.20 * out["has_q2"]
        + 0.12 * out["posterior_gain_rank"]
        + 0.11 * out["hard_gain_rank"]
        + 0.09 * out["source_gain_rank"]
        + 0.08 * out["human_route_support_rank"]
        + 0.06 * out["posterior_safe"]
    )

    head_cols = ["public_head_score", "private_head_score", "objective_head_score", "calendar_q2_head_score"]
    head_names = ["public_transition", "private_stable", "objective_body", "calendar_q2"]
    head_values = out[head_cols].to_numpy(dtype=np.float64)
    out["decoder_head"] = [head_names[i] for i in head_values.argmax(axis=1)]
    out["decoder_head_score"] = head_values.max(axis=1)
    out["decoder_head_margin"] = np.sort(head_values, axis=1)[:, -1] - np.sort(head_values, axis=1)[:, -2]
    base_value = out.get("dual_score", out["value_law_score"]).astype(float)
    out["h089_action_score"] = (
        0.24 * out["decoder_head_score"]
        + 0.15 * rank01(base_value.to_numpy())
        + 0.13 * out["human_route_support_rank"]
        + 0.12 * out["assignment_rank"]
        + 0.10 * out["source_gain_rank"]
        + 0.10 * out["hard_gain_rank"]
        + 0.08 * out["posterior_gain_rank"]
        + 0.04 * out["bad_avoid_rank"]
        + 0.04 * out["h082_rank"]
        - 0.10 * (out["mean_bad_same_rank"].astype(float) > 0.74).astype(float)
        - 0.06 * (out["source_proxy_sum"].astype(float) > 3.0e-6).astype(float)
    )
    return out.sort_values("h089_action_score", ascending=False).reset_index(drop=True)


def spec_list() -> list[H089Spec]:
    return [
        H089Spec(
            name="lifestyle_transition_switch_c1120_r190_q125",
            profile="mixed_switch",
            target_group="all",
            max_routes=190,
            max_cells=1120,
            max_rows=190,
            q2_cap=125,
            max_per_subject=34,
            min_h089_score=0.590,
            min_state_score=0.680,
            alpha=1.16,
            cap=2.05,
            novelty="public_private_head_by_lifestyle_transition",
        ),
        H089Spec(
            name="transition_public_head_c900_r175_q110",
            profile="transition_public",
            target_group="all",
            max_routes=175,
            max_cells=900,
            max_rows=175,
            q2_cap=110,
            max_per_subject=30,
            min_h089_score=0.585,
            min_state_score=0.670,
            alpha=1.20,
            cap=2.15,
            novelty="volatile_rows_use_public_posterior_head",
        ),
        H089Spec(
            name="stable_private_head_c900_r180_q80",
            profile="stable_private",
            target_group="all",
            max_routes=180,
            max_cells=900,
            max_rows=180,
            q2_cap=80,
            max_per_subject=30,
            min_h089_score=0.575,
            min_state_score=0.660,
            alpha=1.10,
            cap=1.95,
            novelty="routine_recovery_rows_use_private_head",
        ),
        H089Spec(
            name="objective_body_head_c760_r170",
            profile="objective_body",
            target_group="objective",
            max_routes=170,
            max_cells=760,
            max_rows=170,
            q2_cap=0,
            max_per_subject=28,
            min_h089_score=0.560,
            min_state_score=0.650,
            alpha=1.14,
            cap=1.85,
            novelty="sensor_body_rows_use_objective_head",
        ),
        H089Spec(
            name="calendar_q2_head_c560_r165_q145",
            profile="calendar_q2",
            target_group="q2_route",
            max_routes=165,
            max_cells=560,
            max_rows=165,
            q2_cap=145,
            max_per_subject=25,
            min_h089_score=0.540,
            min_state_score=0.630,
            alpha=1.22,
            cap=2.20,
            novelty="calendar_cashflow_rows_use_q2_route_head",
        ),
        H089Spec(
            name="lifestyle_aggressive_c1320_r215_q145",
            profile="mixed_switch",
            target_group="all",
            max_routes=215,
            max_cells=1320,
            max_rows=215,
            q2_cap=145,
            max_per_subject=38,
            min_h089_score=0.555,
            min_state_score=0.630,
            alpha=1.24,
            cap=2.25,
            novelty="aggressive_lifestyle_head_assignment",
        ),
    ]


def allowed_by_profile(rec: dict[str, object], spec: H089Spec) -> bool:
    targets = parse_targets(rec["targets"])
    if not target_allowed(targets, spec.target_group):
        return False
    if float(rec["h089_action_score"]) < spec.min_h089_score:
        return False
    if float(rec["decoder_head_score"]) < spec.min_state_score:
        return False
    if float(rec["mean_bad_same_rank"]) > 0.78:
        return False

    profile = spec.profile
    head = str(rec["decoder_head"])
    mode = str(rec["value_mode"])
    if profile == "mixed_switch":
        return bool(
            (head == "public_transition" and mode in POSTERIOR_MODES and float(rec["posterior_delta_sum"]) <= 1.0e-6)
            or (head == "private_stable" and mode in PRIVATE_MODES and float(rec["hard_delta_sum"]) <= 1.0e-6)
            or (head == "objective_body" and float(rec["is_objective_route"]) > 0 and float(rec["source_proxy_sum"]) <= 3.0e-6)
            or (head == "calendar_q2" and float(rec["has_q2"]) > 0 and float(rec["posterior_delta_sum"]) <= 1.0e-6)
        )
    if profile == "transition_public":
        return bool(
            head == "public_transition"
            and float(rec["public_transition_score"]) >= 0.54
            and mode in POSTERIOR_MODES
            and float(rec["posterior_delta_sum"]) <= 1.0e-6
            and float(rec["source_proxy_sum"]) <= 3.0e-6
        )
    if profile == "stable_private":
        return bool(
            head == "private_stable"
            and float(rec["private_stable_score"]) >= 0.50
            and mode in PRIVATE_MODES
            and float(rec["hard_delta_sum"]) <= 1.0e-6
        )
    if profile == "objective_body":
        return bool(
            head == "objective_body"
            and float(rec["objective_body_score"]) >= 0.49
            and float(rec["is_objective_route"]) > 0
            and float(rec["source_proxy_sum"]) <= 3.0e-6
        )
    if profile == "calendar_q2":
        return bool(
            head == "calendar_q2"
            and float(rec["calendar_q2_score"]) >= 0.54
            and float(rec["has_q2"]) > 0
            and float(rec["posterior_delta_sum"]) <= 2.0e-6
        )
    raise ValueError(profile)


def select_actions(actions: pd.DataFrame, spec: H089Spec) -> pd.DataFrame:
    selected: list[dict[str, object]] = []
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    n_cells = 0
    q2_cells = 0

    for rec in actions.sort_values("h089_action_score", ascending=False).to_dict("records"):
        if not allowed_by_profile(rec, spec):
            continue
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(selected) >= spec.max_routes or len(used_rows) >= spec.max_rows:
            break
        if n_cells + int(rec["n_cells"]) > spec.max_cells:
            continue
        if q2_cells + int(rec["q2_cells"]) > spec.q2_cap:
            continue
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        selected.append(rec)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        n_cells += int(rec["n_cells"])
        q2_cells += int(rec["q2_cells"])

    return pd.DataFrame(selected)


def add_h089_metrics(metrics: dict[str, object], selected_actions: pd.DataFrame, selected_cells: pd.DataFrame) -> dict[str, object]:
    posterior = float(metrics["posterior_delta_vs_h057"])
    hard = float(metrics["hard_delta_vs_h057"])
    source = float(metrics["source_proxy_delta_vs_h057"])
    resp = float(metrics["responsibility_weighted_delta_vs_h057"])
    bad = float(metrics["max_positive_bad_cosine"])
    source_agree = float(metrics["source_agree_rate"])
    h082 = float(metrics["h082_ratio"])
    scale = float(metrics["selected_cells"]) / (250 * 7)

    if selected_actions.empty:
        mean_head = 0.0
        mean_route_support = 0.0
        mean_transition = 0.0
        head_mix = ""
        lifestyle_mix = ""
    else:
        mean_head = float(selected_actions["decoder_head_score"].mean())
        mean_route_support = float(selected_actions["human_route_support_rank"].mean())
        mean_transition = float(selected_actions["public_transition_score"].mean())
        head_mix = ";".join(
            f"{k}:{v}" for k, v in selected_actions["decoder_head"].value_counts().sort_index().items()
        )
        lifestyle_mix = ";".join(
            f"{k}:{v}" for k, v in selected_actions["lifestyle_head"].value_counts().sort_index().items()
        )

    if selected_cells.empty:
        overlap_h088 = 0.0
        overlap_h087 = 0.0
    else:
        own = selected_cells[["row", "target"]].drop_duplicates()
        h088_decision = pd.read_csv(HITL / "h088_dual_state_value_gate_hsjepa" / "h088_decision.csv").iloc[0]
        h088_cells = pd.read_csv(HITL / "h088_dual_state_value_gate_hsjepa" / "h088_selected_cells.csv")
        h088_cells = h088_cells[h088_cells["candidate_id"] == str(h088_decision["candidate_id"])][["row", "target"]].drop_duplicates()
        h087_decision = pd.read_csv(HITL / "h087_route_value_law_hsjepa" / "h087_decision.csv").iloc[0]
        h087_cells = pd.read_csv(HITL / "h087_route_value_law_hsjepa" / "h087_selected_cells.csv")
        h087_cells = h087_cells[h087_cells["candidate_id"] == str(h087_decision["candidate_id"])][["row", "target"]].drop_duplicates()
        overlap_h088 = float(len(own.merge(h088_cells, on=["row", "target"], how="inner")) / max(len(own), 1))
        overlap_h087 = float(len(own.merge(h087_cells, on=["row", "target"], how="inner")) / max(len(own), 1))

    score = (
        360.0 * (-posterior)
        + 320.0 * (-hard)
        + 180.0 * (-source)
        + 120.0 * (-resp)
        + 0.13 * source_agree
        + 0.12 * h082
        + 0.12 * mean_head
        + 0.10 * mean_route_support
        + 0.08 * mean_transition
        + 0.08 * min(scale / 0.60, 1.0)
        + 0.05 * (1.0 - overlap_h088)
        - 0.38 * bad
        - 0.16 * max(float(metrics["mean_bad_same_rank"]) - 0.52, 0.0)
    )
    metrics.update(
        {
            "h089_score": score,
            "mean_decoder_head_score": mean_head,
            "mean_human_route_support_rank": mean_route_support,
            "mean_public_transition_score": mean_transition,
            "decoder_head_mix": head_mix,
            "lifestyle_head_mix": lifestyle_mix,
            "overlap_h088_root_cells": overlap_h088,
            "overlap_h087_root_cells": overlap_h087,
        }
    )
    return metrics


def run() -> None:
    cleanup_previous_outputs()
    sample = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv", parse_dates=KEYS)
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    base = h087mod.h085mod.load_sub(BASE_FILE, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)

    state = build_transition_state(sample)
    state.to_csv(OUT / "h089_lifestyle_transition_state.csv", index=False)

    cell = h087mod.build_cell_table()
    route_actions = h088mod.build_dual_actions(h087mod.build_route_actions(cell))
    route_actions = add_lifestyle_scores(route_actions, state)
    route_actions.to_csv(OUT / "h089_lifestyle_route_actions.csv", index=False)

    candidate_rows: list[dict[str, object]] = []
    all_selected_actions: list[pd.DataFrame] = []
    all_selected_cells: list[pd.DataFrame] = []
    for spec in spec_list():
        selected_actions = select_actions(route_actions, spec)
        if selected_actions.empty:
            continue
        h087_spec = h087mod.CandidateSpec(
            name=spec.name,
            target_group=spec.target_group if spec.target_group != "q2_route" else "all",
            value_modes=tuple(sorted(selected_actions["value_mode"].astype(str).unique())),
            max_routes=spec.max_routes,
            max_cells=spec.max_cells,
            max_rows=spec.max_rows,
            q2_cap=spec.q2_cap,
            max_per_subject=spec.max_per_subject,
            min_action_score=spec.min_h089_score,
            alpha=spec.alpha,
            cap=spec.cap,
            novelty_bonus=spec.novelty,
        )
        prob, selected_cells = h087mod.materialize_candidate(sample, base_prob, cell, selected_actions, h087_spec)
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h089_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h087mod.h085mod.write_submission(sample, prob, path)
        metrics = h087mod.evaluate_candidate(candidate_id, prob, base_prob, selected_actions, selected_cells, cell, sample, h087_spec, path)
        metrics.update({"profile": spec.profile, "h089_novelty": spec.novelty})
        metrics = add_h089_metrics(metrics, selected_actions, selected_cells)
        candidate_rows.append(metrics)
        selected_actions = selected_actions.copy()
        selected_actions.insert(0, "candidate_id", candidate_id)
        selected_cells = selected_cells.copy()
        selected_cells.insert(0, "candidate_id", candidate_id)
        all_selected_actions.append(selected_actions)
        all_selected_cells.append(selected_cells)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H089 candidates")
    candidates = candidates.sort_values("h089_score", ascending=False).reset_index(drop=True)
    candidates.to_csv(OUT / "h089_candidates.csv", index=False)
    pd.concat(all_selected_actions, ignore_index=True).to_csv(OUT / "h089_selected_route_actions.csv", index=False)
    pd.concat(all_selected_cells, ignore_index=True).to_csv(OUT / "h089_selected_cells.csv", index=False)

    decision = candidates.iloc[0].to_dict()
    selected_path = Path(str(decision["resolved_path"]))
    root_path = ROOT / f"submission_h089_lifestyle_transition_gate_{decision['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h087mod.h085mod.validate_submission(root_path, sample, base_prob)
    decision.update({"root_uploadsafe_path": str(root_path.resolve()), **{f"root_{k}": v for k, v in validation.items()}})
    pd.DataFrame([decision]).to_csv(OUT / "h089_decision.csv", index=False)

    top_state = state.sort_values("public_transition_score", ascending=False)[
        [
            "row",
            "subject_id",
            "lifelog_date",
            "family_top",
            "lifestyle_head",
            "public_transition_score",
            "private_stable_score",
            "objective_body_score",
            "calendar_q2_score",
            "transition_energy_raw",
            "social_arousal_score",
        ]
    ].head(30)
    top_actions = route_actions.head(50)[
        [
            "route_id",
            "row",
            "subject_id",
            "sleep_date",
            "route_name",
            "targets",
            "value_mode",
            "decoder_head",
            "h089_action_score",
            "decoder_head_score",
            "human_route_support_rank",
            "public_transition_score",
            "private_stable_score",
            "objective_body_score",
            "calendar_q2_score",
            "posterior_delta_sum",
            "hard_delta_sum",
            "source_proxy_sum",
            "dual_pareto",
        ]
    ]
    trimmed = candidates.drop(columns=[c for c in candidates.columns if c.startswith("bad_cos_")], errors="ignore")
    report = f"""# H089 Lifestyle-Transition Gate HS-JEPA

Question: does raw-log-derived human lifestyle transition state decide which
public/private decoder head should translate each route?

Worldview:

- H087 route-value decoding and H088 dual-head Pareto gating are both partial.
- The missing factor may be row-level human state transition: volatile social
  rows need a public/posterior head, routine/recovery rows need a private/hard
  head, sensor/body rows need an objective head, and calendar/cashflow rows need
  a Q2 route head.
- H089 uses the H072 human/social latent only as context. The target is the
  hidden decoder-head assignment, not a direct label rule.

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview |
| --- | --- | --- | --- |
| promote_lifestyle_transition_gate_bigbet | {decision['candidate_id']} | {decision['root_uploadsafe_path']} | lifestyle transition latent controls the HS-JEPA public/private decoder head |

Candidates:

{md_table(trimmed, n=20)}

Top Lifestyle Transition Rows:

{md_table(top_state, n=30)}

Top Lifestyle-Gated Route Actions:

{md_table(top_actions, n=50)}

Interpretation rule:

- If H089 improves by >= 0.001 vs H057/H088, HS-JEPA should make
  human-state transition the gate before public/private value decoding.
- If H089 is close to H088 but not better, lifestyle state is a diagnostic
  prior but not yet action-grade.
- If H089 loses badly, direct lifestyle-transition control is too noisy; the
  lifestyle context should be trained through a stronger latent target before
  it can choose decoder heads.
"""
    (OUT / "h089_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['candidate_id']}")
    print(f"root={root_path}")
    print(candidates.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
