#!/usr/bin/env python3
"""H072: human-social state engine for HS-JEPA.

H071 made the action unit discrete:

    row -> route template -> row-target correction support

H072 tests whether the 1000 human-state stories can become a useful context
view for that assignment problem. The stories are not label rules. They are
compressed into human-state family latents, then used only as route priors and
health diagnostics.

The falsifiable question:

    Do human-social latent families rediscover or extend the H057/H068/H071
    hidden states better than subject-preserving null permutations?
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
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h072_human_social_state_engine_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-9
TOL = 1.0e-12
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H071MOD = import_module(HITL / "h071_rowtarget_assignment_solver_jepa.py", "h071mod_for_h072")


@dataclass(frozen=True)
class H072Spec:
    family: str
    max_cells: int
    max_rows: int
    q2_cap: int
    max_per_subject: int
    min_route_score: float
    min_human_support: float
    min_cell_score: float
    novelty: str
    alpha: float
    mode: str
    allowed_routes: tuple[str, ...]
    focus_families: tuple[str, ...]


FAMILY_CHANNELS: dict[str, dict[str, float]] = {
    "badnight_aftereffect": {
        "morning_after_badnight": 0.36,
        "deepnight_phone_awake": 0.22,
        "phone_in_bed": 0.14,
        "screen_fragmentation": 0.12,
        "high_sensor_wear_day": 0.10,
        "presleep_msg_drag": 0.06,
    },
    "nocturnal_awake": {
        "deepnight_phone_awake": 0.38,
        "phone_in_bed": 0.22,
        "presleep_msg_drag": 0.16,
        "bright_light_late": 0.12,
        "charge_bed_anchor": 0.12,
    },
    "bedtime_arousal": {
        "late_msg_call": 0.15,
        "presleep_msg_drag": 0.16,
        "media_binge_late": 0.14,
        "game_dopamine_late": 0.11,
        "late_search_spiral": 0.13,
        "bright_light_late": 0.10,
        "phone_in_bed": 0.12,
        "heart_stress_late": 0.09,
    },
    "social_load": {
        "late_msg_call": 0.22,
        "public_social_evening": 0.22,
        "night_out_mobility": 0.20,
        "social_isolation_media": 0.12,
        "presleep_msg_drag": 0.14,
        "music_ambient_late": 0.10,
    },
    "routine_pressure": {
        "commute_workday": 0.24,
        "weekday_routine_pressure": 0.28,
        "app_entropy_scattered_day": 0.16,
        "single_app_monotony": 0.12,
        "vehicle_noise_day": 0.12,
        "sedentary_screen_day": 0.08,
    },
    "recovery_rest": {
        "ritual_anchor": 0.18,
        "charge_bed_anchor": 0.15,
        "afterwork_recovery": 0.14,
        "low_hr_recovery": 0.17,
        "home_stability": 0.14,
        "quiet_dark_bedtime": 0.14,
        "outdoor_nature_day": 0.08,
    },
    "cashflow_stress": {
        "finance_shopping_stress": 0.44,
        "late_search_spiral": 0.16,
        "weekday_routine_pressure": 0.12,
        "heart_stress_late": 0.10,
        "media_binge_late": 0.08,
    },
    "measurement_confidence": {
        "high_sensor_wear_day": 0.42,
        "charge_bed_anchor": 0.18,
        "sensor_sparse_day": -0.30,
        "home_stability": 0.10,
    },
    "weekend_rhythm": {
        "weekend_social_jetlag": 0.30,
        "weekend_ritual_rest": 0.24,
        "night_out_mobility": 0.12,
        "public_social_evening": 0.12,
        "media_binge_late": 0.10,
        "is_weekend": 0.12,
    },
    "body_fatigue": {
        "physical_fatigue": 0.26,
        "overtraining_arousal": 0.17,
        "sedentary_screen_day": 0.15,
        "heart_stress_late": 0.18,
        "low_hr_recovery": -0.16,
        "vehicle_noise_day": 0.08,
    },
    "isolation_cocoon": {
        "social_isolation_media": 0.30,
        "home_stability": 0.20,
        "single_app_monotony": 0.17,
        "quiet_dark_bedtime": 0.18,
        "outdoor_nature_day": 0.15,
    },
    "routine_anchor": {
        "ritual_anchor": 0.28,
        "charge_bed_anchor": 0.20,
        "home_stability": 0.22,
        "weekday_routine_pressure": 0.12,
        "quiet_dark_bedtime": 0.18,
    },
}

FAMILY_NAMES = tuple(FAMILY_CHANNELS)

MANUAL_ROUTE_PREF: dict[str, dict[str, float]] = {
    "badnight_aftereffect": {
        "q3_s_stage": 0.26,
        "q_subjective": 0.20,
        "q2_s3_tail": 0.14,
        "full_state": 0.17,
        "s_stage": 0.12,
        "nonq2_full": 0.11,
    },
    "nocturnal_awake": {
        "q3_s_stage": 0.30,
        "s_stage": 0.24,
        "q2_s3_tail": 0.14,
        "full_state": 0.14,
        "nonq2_full": 0.10,
        "s23_core": 0.08,
    },
    "bedtime_arousal": {
        "q3_s_stage": 0.24,
        "q_subjective": 0.21,
        "q2_s3_tail": 0.16,
        "full_state": 0.18,
        "nonq2_full": 0.13,
        "q3_quality": 0.08,
    },
    "social_load": {
        "q_subjective": 0.28,
        "q3_s_stage": 0.20,
        "full_state": 0.20,
        "nonq2_full": 0.16,
        "q1q3_subjective": 0.10,
        "q2_s3_tail": 0.06,
    },
    "routine_pressure": {
        "full_state": 0.24,
        "q_subjective": 0.20,
        "q2_hardtail": 0.18,
        "q2_s3_tail": 0.14,
        "nonq2_full": 0.12,
        "q3_s_stage": 0.12,
    },
    "recovery_rest": {
        "recovery_route": 0.30,
        "nonq2_full": 0.22,
        "s_stage": 0.18,
        "full_state": 0.12,
        "q1q3_subjective": 0.10,
        "s23_core": 0.08,
    },
    "cashflow_stress": {
        "q2_s3_tail": 0.28,
        "q_subjective": 0.23,
        "full_state": 0.20,
        "q2_hardtail": 0.15,
        "q3_s_stage": 0.14,
    },
    "measurement_confidence": {
        "s_stage": 0.32,
        "q3_s_stage": 0.22,
        "nonq2_full": 0.18,
        "s23_core": 0.12,
        "s14_edge": 0.10,
        "full_state": 0.06,
    },
    "weekend_rhythm": {
        "full_state": 0.24,
        "nonq2_full": 0.20,
        "recovery_route": 0.18,
        "q3_s_stage": 0.16,
        "s_stage": 0.12,
        "q_subjective": 0.10,
    },
    "body_fatigue": {
        "s_stage": 0.26,
        "q3_s_stage": 0.24,
        "recovery_route": 0.18,
        "nonq2_full": 0.14,
        "s23_core": 0.10,
        "full_state": 0.08,
    },
    "isolation_cocoon": {
        "recovery_route": 0.28,
        "nonq2_full": 0.24,
        "q1q3_subjective": 0.18,
        "q_subjective": 0.12,
        "s_stage": 0.10,
        "full_state": 0.08,
    },
    "routine_anchor": {
        "recovery_route": 0.28,
        "s_stage": 0.20,
        "nonq2_full": 0.20,
        "q1q3_subjective": 0.12,
        "full_state": 0.10,
        "q3_s_stage": 0.10,
    },
}


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.size == 0:
        return values
    if np.nanstd(values) < 1.0e-12:
        return np.full_like(values, 0.5, dtype=np.float64)
    return H071MOD.rank01(np.nan_to_num(values, nan=np.nanmedian(values)), high=high)


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    yb = np.asarray(y, dtype=float) > 0.5
    if yb.size == 0 or bool(yb.min()) == bool(yb.max()):
        return float("nan")
    return float(roc_auc_score(yb.astype(int), np.nan_to_num(score, nan=0.0)))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ar = pd.Series(a).rank(method="average").to_numpy(dtype=float)
    br = pd.Series(b).rank(method="average").to_numpy(dtype=float)
    if np.std(ar) < 1.0e-12 or np.std(br) < 1.0e-12:
        return 0.0
    return float(np.corrcoef(ar, br)[0, 1])


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H071MOD.md_table(frame, n)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h072_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h072_humansocial_route_*_uploadsafe.csv"):
        path.unlink()


def normalize_dates(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out


def channel_score(frame: pd.DataFrame, channel: str) -> np.ndarray:
    parts: list[tuple[float, np.ndarray]] = []
    for suffix, weight in [("", 0.34), ("_subj_z", 0.30), ("_abs_subj_z", 0.22), ("_weekend", 0.14)]:
        col = f"{channel}{suffix}"
        if col not in frame.columns:
            continue
        values = frame[col].to_numpy(dtype=np.float64)
        high = True
        parts.append((weight, rank01(values, high=high)))
    if not parts:
        return np.full(len(frame), 0.5, dtype=np.float64)
    denom = sum(weight for weight, _ in parts)
    return sum(weight * values for weight, values in parts) / max(denom, EPS)


def load_story_context(sample: pd.DataFrame) -> pd.DataFrame:
    story = pd.read_parquet(ROOT / "analysis_outputs" / "e268_human_social_story_features.parquet")
    story = normalize_dates(story)
    left = normalize_dates(sample[KEYS].reset_index().rename(columns={"index": "row"}))
    merged = left.merge(story, on=KEYS, how="left", validate="one_to_one")
    missing = int(merged["split"].isna().sum()) if "split" in merged.columns else int(merged.isna().all(axis=1).sum())
    if missing:
        print(f"[H072] warning: {missing} sample rows did not match E268 story features")
    dt = pd.to_datetime(merged["lifelog_date"])
    merged["dow"] = dt.dt.dayofweek.astype(float)
    merged["is_weekend"] = (dt.dt.dayofweek >= 5).astype(float)
    merged["day_of_month"] = dt.dt.day.astype(float)
    merged["month_start_prox"] = (1.0 - np.minimum(np.abs(dt.dt.day.astype(float) - 1.0), 10.0) / 10.0).astype(float)
    merged["month_end_prox"] = (
        1.0 - np.minimum(np.abs(dt.dt.days_in_month.astype(float) - dt.dt.day.astype(float)), 10.0) / 10.0
    ).astype(float)
    merged["payday_25_prox"] = (1.0 - np.minimum(np.abs(dt.dt.day.astype(float) - 25.0), 10.0) / 10.0).astype(float)
    return merged.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def build_family_features(sample: pd.DataFrame) -> pd.DataFrame:
    frame = load_story_context(sample)
    channel_cache = {channel: channel_score(frame, channel) for channels in FAMILY_CHANNELS.values() for channel in channels}
    rows = frame[["row", *KEYS, "dow", "is_weekend", "day_of_month", "month_start_prox", "month_end_prox", "payday_25_prox"]].copy()
    for family, channels in FAMILY_CHANNELS.items():
        vals = []
        weights = []
        for channel, weight in channels.items():
            score = channel_cache.get(channel, np.full(len(frame), 0.5, dtype=np.float64))
            if weight < 0:
                score = 1.0 - score
            vals.append(abs(weight) * score)
            weights.append(abs(weight))
        score = sum(vals) / max(sum(weights), EPS)
        if family == "cashflow_stress":
            cal = np.maximum.reduce(
                [
                    rows["payday_25_prox"].to_numpy(dtype=float),
                    rows["month_start_prox"].to_numpy(dtype=float),
                    rows["month_end_prox"].to_numpy(dtype=float),
                ]
            )
            score = 0.72 * score + 0.28 * rank01(cal)
        elif family == "weekend_rhythm":
            score = 0.84 * score + 0.16 * rows["is_weekend"].to_numpy(dtype=float)
        elif family == "measurement_confidence":
            sparse = channel_cache.get("sensor_sparse_day", np.full(len(frame), 0.5, dtype=np.float64))
            wear = channel_cache.get("high_sensor_wear_day", np.full(len(frame), 0.5, dtype=np.float64))
            score = 0.58 * wear + 0.30 * (1.0 - sparse) + 0.12 * score
        rows[f"family_{family}"] = np.clip(score, 0.0, 1.0)
    fam_cols = [f"family_{family}" for family in FAMILY_NAMES]
    fam = rows[fam_cols].to_numpy(dtype=np.float64)
    rows["family_max_score"] = fam.max(axis=1)
    rows["family_mean_score"] = fam.mean(axis=1)
    rows["family_entropy"] = -np.sum(np.clip(fam, EPS, 1.0) * np.log(np.clip(fam, EPS, 1.0)), axis=1) / len(fam_cols)
    top_ix = fam.argmax(axis=1)
    rows["family_top"] = [FAMILY_NAMES[i] for i in top_ix]
    rows["arousal_pressure"] = rows[
        ["family_badnight_aftereffect", "family_nocturnal_awake", "family_bedtime_arousal", "family_social_load"]
    ].mean(axis=1)
    rows["recovery_pressure"] = rows[
        ["family_recovery_rest", "family_isolation_cocoon", "family_routine_anchor"]
    ].mean(axis=1)
    rows["routine_calendar_pressure"] = rows[
        ["family_routine_pressure", "family_weekend_rhythm", "family_cashflow_stress"]
    ].mean(axis=1)
    rows["objective_measure_pressure"] = rows[
        ["family_measurement_confidence", "family_body_fatigue", "family_nocturnal_awake"]
    ].mean(axis=1)
    return rows


def story_family_from_text(text: str) -> str:
    lower = str(text).lower()
    if any(key in lower for key in ["cash", "financial", "finance", "pay", "salary", "month", "rumination"]):
        return "cashflow_stress"
    if any(key in lower for key in ["nocturnal", "awake", "deepnight", "night_awake"]):
        return "nocturnal_awake"
    if any(key in lower for key in ["badnight", "inertia", "after_badnight", "slump", "irritability", "withdrawal"]):
        return "badnight_aftereffect"
    if any(key in lower for key in ["social", "message", "call", "arousal", "bedtime_social"]):
        return "bedtime_arousal"
    if any(key in lower for key in ["commute", "work", "routine", "weekday", "forced"]):
        return "routine_pressure"
    if any(key in lower for key in ["weekend", "jetlag"]):
        return "weekend_rhythm"
    if any(key in lower for key in ["home", "recovery", "cocoon", "domestic", "rest"]):
        return "recovery_rest"
    if any(key in lower for key in ["sensor", "wear", "measurement", "confidence"]):
        return "measurement_confidence"
    if any(key in lower for key in ["fatigue", "body", "physical", "overtraining"]):
        return "body_fatigue"
    return "social_load"


def route_from_expected(text: str) -> str:
    lower = str(text).lower()
    direct_targets: set[str] = set()
    for target in TARGETS:
        target_lower = target.lower()
        for part in lower.split(";"):
            part = part.strip()
            if not part.startswith(target_lower):
                continue
            if "no_direct" in part or "no direct" in part:
                continue
            if any(word in part for word in ["up", "down", "direct", "tiny"]):
                direct_targets.add(target)
    if not direct_targets:
        return "no_direct"
    if direct_targets == set(TARGETS):
        return "full_state"
    if direct_targets == {"Q2"}:
        return "q2_hardtail"
    if direct_targets == {"Q3"}:
        return "q3_quality"
    if direct_targets == {"Q1", "Q2", "Q3"}:
        return "q_subjective"
    if direct_targets == {"Q1", "Q3"}:
        return "q1q3_subjective"
    if direct_targets == {"Q2", "S3"}:
        return "q2_s3_tail"
    if "Q3" in direct_targets and any(t in direct_targets for t in S_TARGETS):
        return "q3_s_stage"
    if direct_targets == set(S_TARGETS):
        return "s_stage"
    if direct_targets == {"S2", "S3"}:
        return "s23_core"
    if direct_targets == {"S1", "S4"}:
        return "s14_edge"
    if direct_targets.issubset(set(S_TARGETS)):
        return "s_stage"
    if direct_targets.issuperset({"Q1", "S2", "S3"}) and "Q2" not in direct_targets:
        return "recovery_route"
    if "Q2" not in direct_targets and len(direct_targets) >= 4:
        return "nonq2_full"
    return "full_state" if len(direct_targets) >= 5 else "q3_s_stage"


def hypothesis_route_table() -> tuple[pd.DataFrame, pd.DataFrame]:
    hyp = pd.read_csv(HITL / "human_state_route_hypotheses_1000.csv")
    priority_weight = {"high": 3.0, "medium": 1.6, "low": 1.0}
    hyp["story_family"] = hyp["hidden_human_state"].map(story_family_from_text)
    hyp["route_template"] = hyp["expected_target_route"].map(route_from_expected)
    hyp["priority_weight"] = hyp["priority"].astype(str).str.lower().map(priority_weight).fillna(1.0)
    table = (
        hyp.groupby(["story_family", "route_template"], as_index=False)
        .agg(
            hypotheses=("hypothesis_id", "count"),
            weighted_hypotheses=("priority_weight", "sum"),
            high_priority=("priority", lambda s: int((s.astype(str).str.lower() == "high").sum())),
        )
        .sort_values(["story_family", "weighted_hypotheses"], ascending=[True, False])
    )
    return hyp, table


def normalize_pref(pref: dict[str, dict[str, float]], mined: pd.DataFrame) -> pd.DataFrame:
    routes = tuple(H071MOD.ROUTES)
    rows = []
    mined_pivot = mined.pivot_table(
        index="story_family",
        columns="route_template",
        values="weighted_hypotheses",
        aggfunc="sum",
        fill_value=0.0,
    )
    for family in FAMILY_NAMES:
        manual = {route: float(pref.get(family, {}).get(route, 0.0)) for route in routes}
        manual_sum = sum(manual.values())
        manual = {route: value / manual_sum for route, value in manual.items()} if manual_sum else manual
        mined_row = mined_pivot.loc[family].to_dict() if family in mined_pivot.index else {}
        mined_vals = {route: float(mined_row.get(route, 0.0)) for route in routes}
        mined_sum = sum(mined_vals.values())
        mined_vals = {route: value / mined_sum for route, value in mined_vals.items()} if mined_sum else mined_vals
        for route in routes:
            rows.append(
                {
                    "story_family": family,
                    "route_name": route,
                    "manual_pref": manual.get(route, 0.0),
                    "hypothesis_pref": mined_vals.get(route, 0.0),
                    "route_pref": 0.82 * manual.get(route, 0.0) + 0.18 * mined_vals.get(route, 0.0),
                }
            )
    out = pd.DataFrame(rows)
    sums = out.groupby("story_family")["route_pref"].transform("sum").replace(0, 1.0)
    out["route_pref"] = out["route_pref"] / sums
    return out


def preference_matrix(pref: pd.DataFrame) -> tuple[np.ndarray, dict[str, int], dict[str, int]]:
    routes = tuple(H071MOD.ROUTES)
    family_ix = {family: i for i, family in enumerate(FAMILY_NAMES)}
    route_ix = {route: i for i, route in enumerate(routes)}
    mat = np.zeros((len(FAMILY_NAMES), len(routes)), dtype=np.float64)
    for rec in pref.to_dict("records"):
        mat[family_ix[str(rec["story_family"])], route_ix[str(rec["route_name"])]] = float(rec["route_pref"])
    return mat, family_ix, route_ix


def support_from_arrays(fam_values: np.ndarray, route_names: np.ndarray, pref_mat: np.ndarray, route_ix: dict[str, int]) -> np.ndarray:
    idx = np.array([route_ix[str(name)] for name in route_names], dtype=int)
    weights = pref_mat[:, idx].T
    return np.sum(fam_values * weights, axis=1)


def add_human_route_scores(routes: pd.DataFrame, family: pd.DataFrame, pref: pd.DataFrame, h071_route_ids: set[str]) -> pd.DataFrame:
    pref_mat, _family_ix, route_ix = preference_matrix(pref)
    fam_cols = [f"family_{name}" for name in FAMILY_NAMES]
    row_fam = family.set_index("row")[fam_cols]
    out = routes.merge(family[["row", *fam_cols, "family_max_score", "family_top"]], on="row", how="left")
    fam_values = out[fam_cols].fillna(0.5).to_numpy(dtype=np.float64)
    route_names = out["route_name"].astype(str).to_numpy()
    support = support_from_arrays(fam_values, route_names, pref_mat, route_ix)
    route_pref_for_rows = pref_mat[:, np.array([route_ix[name] for name in route_names])].T
    contributions = fam_values * route_pref_for_rows
    best_ix = contributions.argmax(axis=1)
    out["human_route_support"] = support
    out["human_route_support_rank"] = rank01(support)
    out["human_best_family"] = [FAMILY_NAMES[i] for i in best_ix]
    out["human_best_family_contrib"] = contributions.max(axis=1)
    out["h071_selected_route"] = out["route_id"].astype(str).isin(h071_route_ids).astype(float)
    out["h071_row_route_overlap"] = out["row"].isin(set(routes[routes["route_id"].isin(h071_route_ids)]["row"].astype(int))).astype(float)
    out["assignment_rank_h072"] = rank01(out["assignment_route_score"].to_numpy())
    out["public_rank_h072"] = rank01(out["mean_public_score"].to_numpy())
    out["invariant_rank_h072"] = rank01(out["mean_invariant_score"].to_numpy())
    out["gain_rank_h072"] = rank01(out["sum_cell_gain"].to_numpy())
    out["shortcut_avoid_rank_h072"] = rank01(-out["mean_shortcut_energy"].to_numpy())
    out["novelty_h071_rank"] = rank01((1.0 - out["h071_selected_route"]).to_numpy() + out["outside_h069_cells"].to_numpy())
    out["h072_route_score"] = (
        0.31 * out["human_route_support_rank"]
        + 0.23 * out["assignment_rank_h072"]
        + 0.12 * out["public_rank_h072"]
        + 0.11 * out["invariant_rank_h072"]
        + 0.09 * out["shortcut_avoid_rank_h072"]
        + 0.07 * out["gain_rank_h072"]
        + 0.05 * out["novelty_h071_rank"]
        + 0.02 * out["family_max_score"].fillna(0.5)
    )
    # If the story and assignment disagree badly, keep it diagnostic but do not
    # let assignment score alone dominate the final ordering.
    out.loc[out["human_route_support"] < 0.18, "h072_route_score"] -= 0.12
    return out.sort_values(["h072_route_score", "assignment_route_score"], ascending=[False, False]).reset_index(drop=True)


def row_latent_diagnostics(family: pd.DataFrame, latent: pd.DataFrame, h071_route_sel: pd.DataFrame) -> pd.DataFrame:
    row_state = (
        latent.groupby("row", as_index=False)
        .agg(
            h057_seed_row=("is_h057_seed", "max"),
            h068_selected_row=("h068_selected_cell", "max"),
            h069_selected_row=("h069_selected_cell", "max"),
            h070_selected_row=("h070_selected_cell", "max"),
            mean_public_score=("public_score", "mean"),
            mean_latent_hsjepa_score=("latent_hsjepa_score", "mean"),
        )
        .merge(family, on="row", how="left")
    )
    h071_rows = set(h071_route_sel["row"].astype(int))
    row_state["h071_selected_row"] = row_state["row"].isin(h071_rows).astype(float)
    rows = []
    for fam in FAMILY_NAMES:
        col = f"family_{fam}"
        score = row_state[col].to_numpy(dtype=float)
        rows.append(
            {
                "family": fam,
                "mean_score": float(np.mean(score)),
                "max_score": float(np.max(score)),
                "auc_h057_seed_row": safe_auc(row_state["h057_seed_row"], score),
                "auc_h068_selected_row": safe_auc(row_state["h068_selected_row"], score),
                "auc_h069_selected_row": safe_auc(row_state["h069_selected_row"], score),
                "auc_h070_selected_row": safe_auc(row_state["h070_selected_row"], score),
                "auc_h071_selected_row": safe_auc(row_state["h071_selected_row"], score),
                "spearman_public_score": spearman(row_state["mean_public_score"], score),
                "spearman_latent_hsjepa": spearman(row_state["mean_latent_hsjepa_score"], score),
                "selected_h071_mean": float(row_state.loc[row_state["h071_selected_row"] > 0, col].mean()),
                "not_selected_h071_mean": float(row_state.loc[row_state["h071_selected_row"] <= 0, col].mean()),
            }
        )
    fam_mat = row_state[[f"family_{fam}" for fam in FAMILY_NAMES]].to_numpy(dtype=float)
    corr = np.corrcoef(fam_mat.T)
    corr_abs_mean = float(np.nanmean(np.abs(corr[np.triu_indices_from(corr, k=1)])))
    geom = pd.DataFrame(
        [
            {
                "family": "__geometry__",
                "mean_score": float(fam_mat.mean()),
                "max_score": float(fam_mat.max()),
                "auc_h057_seed_row": float("nan"),
                "auc_h068_selected_row": float("nan"),
                "auc_h069_selected_row": float("nan"),
                "auc_h070_selected_row": float("nan"),
                "auc_h071_selected_row": float("nan"),
                "spearman_public_score": float("nan"),
                "spearman_latent_hsjepa": float("nan"),
                "selected_h071_mean": float("nan"),
                "not_selected_h071_mean": float("nan"),
                "family_corr_abs_mean": corr_abs_mean,
            }
        ]
    )
    return pd.concat([pd.DataFrame(rows), geom], ignore_index=True)


def route_null_stress(
    routes: pd.DataFrame,
    family: pd.DataFrame,
    pref: pd.DataFrame,
    h071_route_ids: set[str],
    n_iter: int = 300,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pref_mat, _family_ix, route_ix = preference_matrix(pref)
    fam_cols = [f"family_{name}" for name in FAMILY_NAMES]
    fam_by_row = family.sort_values("row")[fam_cols].to_numpy(dtype=np.float64)
    subjects = family.sort_values("row")["subject_id"].astype(str).to_numpy()
    route_rows = routes["row"].to_numpy(dtype=int)
    route_names = routes["route_name"].astype(str).to_numpy()
    h071_flag = routes["route_id"].astype(str).isin(h071_route_ids).to_numpy(dtype=bool)
    topk = max(int(h071_flag.sum()), 1)
    real_support = support_from_arrays(fam_by_row[route_rows], route_names, pref_mat, route_ix)
    real_top = np.argsort(-real_support)[:topk]
    real_metrics = {
        "iter": -1,
        "kind": "real",
        "mean_h071_route_support": float(real_support[h071_flag].mean()) if h071_flag.any() else 0.0,
        "topk_h071_overlap": float(h071_flag[real_top].mean()),
        "auc_h071_route": safe_auc(h071_flag.astype(float), real_support),
        "spearman_assignment": spearman(routes["assignment_route_score"].to_numpy(dtype=float), real_support),
    }
    rows = [real_metrics]
    rng = np.random.default_rng(72072)
    subject_groups = [np.where(subjects == subject)[0] for subject in np.unique(subjects)]
    base_idx = np.arange(len(fam_by_row))
    for i in range(n_iter):
        perm_idx = base_idx.copy()
        for idx in subject_groups:
            perm_idx[idx] = rng.permutation(idx)
        perm_support = support_from_arrays(fam_by_row[perm_idx][route_rows], route_names, pref_mat, route_ix)
        top = np.argsort(-perm_support)[:topk]
        rows.append(
            {
                "iter": i,
                "kind": "subject_row_permutation",
                "mean_h071_route_support": float(perm_support[h071_flag].mean()) if h071_flag.any() else 0.0,
                "topk_h071_overlap": float(h071_flag[top].mean()),
                "auc_h071_route": safe_auc(h071_flag.astype(float), perm_support),
                "spearman_assignment": spearman(routes["assignment_route_score"].to_numpy(dtype=float), perm_support),
            }
        )
    stress = pd.DataFrame(rows)
    null = stress[stress["iter"] >= 0]
    summary_rows = []
    for metric in ["mean_h071_route_support", "topk_h071_overlap", "auc_h071_route", "spearman_assignment"]:
        real = float(real_metrics[metric])
        vals = null[metric].to_numpy(dtype=float)
        summary_rows.append(
            {
                "metric": metric,
                "real": real,
                "null_mean": float(np.nanmean(vals)),
                "null_std": float(np.nanstd(vals)),
                "null_p95": float(np.nanpercentile(vals, 95)),
                "z_vs_null": float((real - np.nanmean(vals)) / (np.nanstd(vals) + EPS)),
                "p_ge_real": float(np.mean(vals >= real)),
            }
        )
    return stress, pd.DataFrame(summary_rows)


def allowed_by_spec(spec: H072Spec, rec: dict[str, object]) -> bool:
    route_name = str(rec["route_name"])
    if spec.allowed_routes and route_name not in spec.allowed_routes:
        return False
    if float(rec["h072_route_score"]) < spec.min_route_score:
        return False
    if float(rec["human_route_support"]) < spec.min_human_support:
        return False
    if spec.novelty == "outside_h071" and float(rec["h071_selected_route"]) > 0:
        return False
    if spec.novelty == "outside_h069" and int(rec["outside_h069_cells"]) < max(1, int(rec["n_cells"]) // 2):
        return False
    if spec.novelty == "anti_shortcut" and float(rec["mean_shortcut_energy"]) > 0.42:
        return False
    if spec.focus_families and str(rec["human_best_family"]) not in spec.focus_families:
        return False
    return True


def select_human_assignments(
    spec: H072Spec,
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = routes[routes.apply(lambda row: allowed_by_spec(spec, row.to_dict()), axis=1)].copy()
    pool = pool.sort_values(["h072_route_score", "human_route_support", "assignment_route_score"], ascending=False)
    used_rows: set[int] = set()
    subject_counts: dict[str, int] = {}
    selected_routes = []
    selected_cells = []
    total_cells = 0
    q2_cells = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        if row in used_rows:
            continue
        if len(used_rows) >= spec.max_rows:
            break
        if subject_counts.get(subject, 0) >= spec.max_per_subject:
            continue
        cells = cells_by_route[str(rec["route_id"])].copy()
        cells = cells[cells["cell_assignment_score"] >= spec.min_cell_score]
        cells = cells[cells["cell_q061_gain"] > 0]
        cells = cells[cells["is_h050_null"] == 0]
        if cells.empty:
            continue
        if total_cells + len(cells) > spec.max_cells:
            continue
        new_q2 = int((cells["target"] == "Q2").sum())
        if q2_cells + new_q2 > spec.q2_cap:
            continue
        selected_routes.append(pd.DataFrame([rec]))
        selected_cells.append(cells)
        used_rows.add(row)
        subject_counts[subject] = subject_counts.get(subject, 0) + 1
        total_cells += int(len(cells))
        q2_cells += new_q2
        if total_cells >= spec.max_cells * 0.96:
            break
    if not selected_routes:
        return pool.iloc[0:0].copy(), pool.iloc[0:0].copy()
    route_sel = pd.concat(selected_routes, ignore_index=True)
    cell_sel = pd.concat(selected_cells, ignore_index=True)
    return route_sel, cell_sel


def h072_specs() -> list[H072Spec]:
    all_routes = tuple(H071MOD.ROUTES)
    return [
        H072Spec("human_route_big", 900, 205, 86, 25, 0.58, 0.20, 0.33, "outside_h069", 1.0, "logit", all_routes, ()),
        H072Spec("human_route_big", 760, 190, 72, 22, 0.61, 0.22, 0.35, "outside_h071", 1.0, "logit", all_routes, ()),
        H072Spec(
            "bedtime_social_big",
            720,
            185,
            74,
            24,
            0.55,
            0.21,
            0.33,
            "outside_h069",
            1.0,
            "logit",
            ("q3_s_stage", "q_subjective", "q2_s3_tail", "full_state", "nonq2_full", "q3_quality"),
            ("badnight_aftereffect", "nocturnal_awake", "bedtime_arousal", "social_load"),
        ),
        H072Spec(
            "recovery_objective_big",
            760,
            200,
            24,
            24,
            0.55,
            0.20,
            0.33,
            "outside_h069",
            1.0,
            "logit",
            ("recovery_route", "nonq2_full", "s_stage", "q3_s_stage", "s23_core", "s14_edge", "full_state"),
            ("recovery_rest", "isolation_cocoon", "routine_anchor", "measurement_confidence", "body_fatigue"),
        ),
        H072Spec(
            "cashflow_routine_big",
            640,
            180,
            86,
            22,
            0.52,
            0.20,
            0.32,
            "outside_h069",
            1.0,
            "logit",
            ("q2_s3_tail", "q_subjective", "full_state", "q2_hardtail", "q3_s_stage", "nonq2_full"),
            ("cashflow_stress", "routine_pressure", "weekend_rhythm"),
        ),
        H072Spec(
            "measurement_stage_big",
            660,
            190,
            0,
            24,
            0.54,
            0.20,
            0.33,
            "anti_shortcut",
            1.0,
            "logit",
            ("s_stage", "q3_s_stage", "nonq2_full", "s23_core", "s14_edge", "recovery_route"),
            ("measurement_confidence", "body_fatigue", "nocturnal_awake"),
        ),
        H072Spec(
            "anti_shortcut_human_big",
            760,
            205,
            60,
            24,
            0.56,
            0.20,
            0.33,
            "anti_shortcut",
            1.0,
            "logit",
            all_routes,
            (),
        ),
        H072Spec(
            "fullvector_social_state",
            980,
            220,
            90,
            25,
            0.53,
            0.18,
            0.30,
            "outside_h069",
            1.0,
            "logit",
            ("full_state", "nonq2_full", "q3_s_stage", "q_subjective", "s_stage", "recovery_route"),
            ("badnight_aftereffect", "bedtime_arousal", "social_load", "routine_pressure", "weekend_rhythm"),
        ),
    ]


def apply_candidate(
    spec: H072Spec,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    route_sel, cell_sel = select_human_assignments(spec, routes, cells_by_route)
    h057_prob = mats["h057"]
    q061 = mats["q061"]
    prob = h057_prob.copy()
    moved = H071MOD.move_toward(h057_prob, q061, spec.alpha, spec.mode)
    for rec in cell_sel.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = moved[int(rec["row"]), int(rec["target_index"])]
    prob = H071MOD.clip_prob(prob)
    changed = np.abs(prob - h057_prob) > TOL
    x = (H071MOD.bce(prob, q061) - H071MOD.bce(h057_prob, q061)).reshape(-1)
    row_delta = (H071MOD.bce(prob, q061) - H071MOD.bce(h057_prob, q061)).mean(axis=1)
    row_public = (
        pd.read_csv(HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv")
        .sort_values("row")["public_weight"]
        .to_numpy(dtype=np.float64)
    )
    move_vec = (H071MOD.logit(prob) - H071MOD.logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:18]}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    route_counts = route_sel["route_name"].value_counts().to_dict() if len(route_sel) else {}
    family_counts = route_sel["human_best_family"].value_counts().to_dict() if len(route_sel) else {}
    meta: dict[str, object] = {
        "candidate_id": "",
        "family": spec.family,
        "max_cells": spec.max_cells,
        "max_rows": spec.max_rows,
        "q2_cap": spec.q2_cap,
        "max_per_subject": spec.max_per_subject,
        "min_route_score": spec.min_route_score,
        "min_human_support": spec.min_human_support,
        "min_cell_score": spec.min_cell_score,
        "novelty": spec.novelty,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "selected_routes": int(len(route_sel)),
        "selected_cells": int(len(cell_sel)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "outside_h071_routes": int((1.0 - route_sel["h071_selected_route"]).sum()) if len(route_sel) else 0,
        "outside_h070_cells": int(cell_sel["outside_h070_cell"].sum()) if len(cell_sel) else 0,
        "outside_h069_cells": int(cell_sel["outside_h069_cell"].sum()) if len(cell_sel) else 0,
        "h071_route_overlap": int(route_sel["h071_selected_route"].sum()) if len(route_sel) else 0,
        "h070_overlap_cells": int(cell_sel["h070_selected_cell"].sum()) if len(cell_sel) else 0,
        "h069_overlap_cells": int(cell_sel["h069_selected_cell"].sum()) if len(cell_sel) else 0,
        "h068_overlap_cells": int(cell_sel["h068_selected_cell"].sum()) if len(cell_sel) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_h072_route_score": float(route_sel["h072_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_human_route_support": float(route_sel["human_route_support"].mean()) if len(route_sel) else 0.0,
        "mean_assignment_route_score": float(route_sel["assignment_route_score"].mean()) if len(route_sel) else 0.0,
        "mean_cell_assignment_score": float(cell_sel["cell_assignment_score"].mean()) if len(cell_sel) else 0.0,
        "mean_public_score": float(cell_sel["public_score"].mean()) if len(cell_sel) else 0.0,
        "mean_invariant_score": float(cell_sel["invariant_score"].mean()) if len(cell_sel) else 0.0,
        "mean_shortcut_energy": float(cell_sel["latent_shortcut_energy"].mean()) if len(cell_sel) else 1.0,
        "h050_null_selected": int(cell_sel["is_h050_null"].sum()) if len(cell_sel) else 0,
        "selected_subjects": int(cell_sel["subject_id"].nunique()) if len(cell_sel) else 0,
        "route_templates": ";".join(f"{k}:{v}" for k, v in sorted(route_counts.items())),
        "human_family_templates": ";".join(f"{k}:{v}" for k, v in sorted(family_counts.items())),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return prob, meta


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    routes: pd.DataFrame,
    cells_by_route: dict[str, pd.DataFrame],
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
    null_summary: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    rows = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    null_z = float(
        null_summary.loc[null_summary["metric"].eq("mean_h071_route_support"), "z_vs_null"].iloc[0]
    )
    for spec in h072_specs():
        prob, meta = apply_candidate(spec, sample, mats, routes, cells_by_route, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 120 or meta["selected_routes"] < 20:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = f"h072_{spec.family}_{spec.novelty}_c{spec.max_cells}_r{spec.max_rows}_q2{spec.q2_cap}_{digest}"
        meta["candidate_id"] = cid
        meta["hash"] = digest
        meta["h071_route_support_null_z"] = null_z
        rows.append(meta)
        probs[cid] = prob
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H072 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["human_rank"] = rank01(cand["mean_human_route_support"].to_numpy())
    cand["route_rank"] = rank01(cand["mean_h072_route_score"].to_numpy())
    cand["assignment_rank"] = rank01(cand["mean_assignment_route_score"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_shortcut_energy"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["outside_h071_route_ratio"] = cand["outside_h071_routes"] / cand["selected_routes"].clip(lower=1)
    cand["q2_risk"] = cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["route_diversity"] = cand["route_templates"].map(lambda text: len(str(text).split(";")) if text else 0)
    cand["human_family_diversity"] = cand["human_family_templates"].map(lambda text: len(str(text).split(";")) if text else 0)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00080) / 0.00120).clip(0.0, 1.0)
    cand["h072_score"] = (
        0.21 * cand["action_rank"]
        + 0.15 * cand["human_rank"]
        + 0.12 * cand["route_rank"]
        + 0.12 * cand["responsibility_rank"]
        + 0.10 * cand["outside_h069_ratio"].clip(0, 1)
        + 0.09 * cand["outside_h071_route_ratio"].clip(0, 1)
        + 0.08 * cand["shortcut_avoid_rank"]
        + 0.06 * cand["assignment_rank"]
        + 0.05 * cand["bigbet_scale_score"]
        + 0.04 * cand["posterior_rank"]
        + 0.03 * cand["bad_avoid_rank"]
        + 0.02 * (cand["route_diversity"] / cand["route_diversity"].clip(lower=1).max()).clip(0, 1)
        + 0.02 * (cand["human_family_diversity"] / cand["human_family_diversity"].clip(lower=1).max()).clip(0, 1)
        - 0.06 * cand["q2_risk"]
        - 0.06 * (cand["h050_null_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h072_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(80).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        H071MOD.write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    return H071MOD.validate_submission(path, sample, h057_prob)


def write_report(
    family: pd.DataFrame,
    hyp_routes: pd.DataFrame,
    route_diag: pd.DataFrame,
    null_summary: pd.DataFrame,
    cand: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    fam_cols = [f"family_{name}" for name in FAMILY_NAMES]
    family_summary = pd.DataFrame(
        [
            {
                "family": name,
                "mean": float(family[f"family_{name}"].mean()),
                "p90": float(family[f"family_{name}"].quantile(0.90)),
                "top_rows": int((family[f"family_{name}"] >= family[f"family_{name}"].quantile(0.90)).sum()),
            }
            for name in FAMILY_NAMES
        ]
    ).sort_values("p90", ascending=False)
    report = "\n".join(
        [
            "# H072 Human-Social State Engine HS-JEPA",
            "",
            "Question: can 1000 human-state stories become an action-grade",
            "route prior, instead of a direct label rule?",
            "",
            "Design:",
            "",
            "- story text is compressed into human-state families;",
            "- E268 human/social features produce row-level family scores;",
            "- hypothesis routes plus manual priors map families to route templates;",
            "- H071 row-route candidates are rescored by human-route support;",
            "- subject-preserving row permutations test whether the support is a shortcut;",
            "- final submissions only materialize via H071 row-target route actions toward H061 q061.",
            "",
            "Family score summary:",
            "",
            md_table(family_summary, 20),
            "",
            "Hypothesis-derived route priors:",
            "",
            md_table(hyp_routes.head(40), 40),
            "",
            "Family-to-latent diagnostics:",
            "",
            md_table(route_diag, 20),
            "",
            "Subject-preserving null stress:",
            "",
            md_table(null_summary, 20),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(40), 40),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H072 wins by >= 0.001, human-social stories are an action-grade HS-JEPA context view.",
            "- If H072 loses mildly but H071 wins, story families are explanatory priors but not yet route selectors.",
            "- If H072 loses badly, direct human story routing is too noisy and H073 should use anti-shortcut inversion.",
            "",
            f"Family columns: {', '.join(fam_cols)}",
            "",
        ]
    )
    (OUT / "h072_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    sample, latent, mats, beta, bad_vecs = H071MOD.load_runtime()
    routes, cells_by_route = H071MOD.build_route_candidates(latent)
    h071_spec = H071MOD.AssignmentSpec(
        family="assignment_big",
        max_cells=820,
        max_rows=185,
        q2_cap=72,
        max_per_subject=24,
        min_route_score=0.48,
        min_cell_score=0.34,
        novelty="outside_h069",
        alpha=1.0,
        mode="logit",
    )
    h071_route_sel, _h071_cell_sel = H071MOD.select_assignments(h071_spec, routes, cells_by_route)
    h071_route_ids = set(h071_route_sel["route_id"].astype(str))

    family = build_family_features(sample)
    _hyp, hyp_routes = hypothesis_route_table()
    route_pref = normalize_pref(MANUAL_ROUTE_PREF, hyp_routes)
    h072_routes = add_human_route_scores(routes, family, route_pref, h071_route_ids)
    route_diag = row_latent_diagnostics(family, latent, h071_route_sel)
    null_stress, null_summary = route_null_stress(h072_routes, family, route_pref, h071_route_ids)
    cand, probs = candidate_sweep(sample, mats, h072_routes, cells_by_route, beta, bad_vecs, null_summary)

    null_z = float(null_summary.loc[null_summary["metric"].eq("mean_h071_route_support"), "z_vs_null"].iloc[0])
    null_p = float(null_summary.loc[null_summary["metric"].eq("mean_h071_route_support"), "p_ge_real"].iloc[0])
    null_support_ok = bool(null_z >= 1.5 and null_p <= 0.10)

    bigbet = cand[
        (cand["max_positive_bad_cosine"] <= 0.0)
        & (cand["h050_null_selected"] == 0)
        & (cand["public_action_pred_delta_vs_h057"] <= -0.00090)
        & (cand["responsibility_weighted_delta_vs_h057"] <= -0.00075)
        & (cand["changed_cells_vs_h057"] >= 600)
        & (cand["mean_human_route_support"] >= 0.20)
    ].sort_values(["public_action_pred_delta_vs_h057", "h072_score"], ascending=[True, False])
    if len(bigbet):
        selected = bigbet.iloc[0].copy()
        if null_support_ok:
            decision_name = "promote_humansocial_route_architecture_bigbet"
            worldview = (
                "human-social story latents recover H071-like row-target routes above subject-preserving nulls"
            )
        else:
            decision_name = "promote_humansocial_route_sensor_null_failed"
            worldview = (
                "human-social route priors create a large action-health candidate, but null stress does not yet prove "
                "they recover H071-like hidden routes"
            )
    else:
        selected = cand.iloc[0].copy()
        decision_name = "promote_humansocial_route_sensor"
        worldview = (
            "human-social story latents are a route-prior sensor; public feedback should decide if they are action-grade"
        )
    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h072_humansocial_route_{digest}_uploadsafe.csv"
    shutil.copyfile(selected_file, root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    if not validation["upload_safe"]:
        raise RuntimeError(f"selected submission is not upload safe: {validation}")

    decision = pd.DataFrame(
        [
            {
                "decision": decision_name,
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected["resolved_path"]),
                "root_uploadsafe_path": str(root_file.resolve()),
                "worldview": worldview,
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    family.to_csv(OUT / "h072_story_family_features.csv", index=False)
    hyp_routes.to_csv(OUT / "h072_hypothesis_family_routes.csv", index=False)
    route_pref.to_csv(OUT / "h072_story_route_preferences.csv", index=False)
    h072_routes.to_csv(OUT / "h072_route_candidates.csv", index=False)
    route_diag.to_csv(OUT / "h072_story_route_diagnostics.csv", index=False)
    null_stress.to_csv(OUT / "h072_story_family_null_stress.csv", index=False)
    null_summary.to_csv(OUT / "h072_story_family_null_summary.csv", index=False)
    cand.to_csv(OUT / "h072_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h072_decision.csv", index=False)
    write_report(family, hyp_routes, route_diag, null_summary, cand, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "selected_routes",
                "outside_h071_routes",
                "outside_h069_cells",
                "Q2_changed_vs_h057",
                "mean_human_route_support",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "responsibility_weighted_delta_vs_h057",
                "route_templates",
                "human_family_templates",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
