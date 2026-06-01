#!/usr/bin/env python3
"""H005: test every imported human-state route hypothesis.

The input CSV is not treated as a feature dump.  Each row is interpreted as:

    observable lifelog pattern -> hidden human state -> target route,
    under a row condition/gate.

For every hypothesis we build a local state score from existing human/social
features, apply its expected tiny target movement to OOF base predictions, and
compare it against no-move, opposite-direction, and shuffled-row controls.
No public LB is used.
"""

from __future__ import annotations

import hashlib
import re
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H005 = HITL / "h005_all_human_route_hypotheses"
H005.mkdir(parents=True, exist_ok=True)

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from e288_lifestyle_bundle_jepa_audit import (  # noqa: E402
    KEYS,
    TARGETS,
    base_label_matrix,
    clip_prob,
    folds_for,
    groups_for,
    load_frames,
    md_table,
)
from e295_episode_state_jepa_audit import (  # noqa: E402
    base_story_cols,
    build_episode_matrix,
    preferred_col,
    robust_standardize,
)


RNG_SEED = 20260601 + 5
EPS = 1.0e-12

HYPOTHESIS_IN = HITL / "human_state_route_hypotheses_1000.csv"
PARSED_OUT = H005 / "h005_hypothesis_parsed.csv"
TEST_OUT = H005 / "h005_all_route_tests.csv"
STATE_OUT = H005 / "h005_state_summary.csv"
GATE_OUT = H005 / "h005_gate_summary.csv"
FAMILY_OUT = H005 / "h005_route_family_summary.csv"
SHORTLIST_OUT = H005 / "h005_shortlist.csv"
NULL_OUT = H005 / "h005_route_null_controls.csv"
REPORT_OUT = H005 / "h005_report.md"


TOP_FRACS = [0.12, 0.18, 0.25, 0.35]
AMPS = [0.003, 0.006, 0.010, 0.015]
NULL_REPS = 3
MIN_SELECTED = 8


CORE_EPISODES = [
    "commute_pressure",
    "bedtime_arousal",
    "routine_fragmentation",
    "routine_anchor_recovery",
    "cashflow_stress",
    "cashflow_relief_spend",
    "physiology_strain",
    "home_recovery",
    "social_overload",
    "measurement_wear_confidence",
    "badnight_aftereffect",
]


KEYWORD_EPISODE_MAP: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (
        ("badnight", "nocturnal", "inertia", "slump", "irritability", "masked_badnight", "after_badnight"),
        ("badnight_aftereffect", "bedtime_arousal"),
    ),
    (("home", "cocoon", "domestic", "decompression", "recovery", "anchor", "ritual"), ("home_recovery", "routine_anchor_recovery")),
    (("arousal", "rumination", "deadline", "screen", "compulsive", "dopamine", "bedtime"), ("bedtime_arousal",)),
    (("social", "relationship", "caregiving", "outing", "isolation"), ("social_overload",)),
    (("fragment", "drift", "errand", "switching", "schedule", "routine"), ("routine_fragmentation",)),
    (("commute", "vehicle", "workday", "forced"), ("commute_pressure",)),
    (("physical", "activity", "health", "illness", "strain", "sedentary", "fatigue", "mood"), ("physiology_strain",)),
    (("cash", "payday", "budget", "financial", "finance", "monthstart", "eom", "bill"), ("cashflow_stress", "cashflow_relief_spend")),
    (("measurement", "sensor", "wear", "valid", "placement", "confidence"), ("measurement_wear_confidence",)),
]


SEMANTIC_ALIASES: dict[str, tuple[str, ...]] = {
    "finance": ("finance_shopping_stress", "money_rumination", "budget_squeeze", "cash_stress"),
    "shopping": ("finance_shopping_stress", "spend_outing", "late_shopping"),
    "commute": ("commute_workday", "vehicle_noise_day"),
    "vehicle": ("vehicle_noise_day",),
    "home": ("home_stability", "afterwork_recovery"),
    "social": ("late_msg_call", "presleep_msg_drag", "public_social_evening"),
    "message": ("late_msg_call", "presleep_msg_drag"),
    "msg": ("late_msg_call", "presleep_msg_drag"),
    "call": ("late_msg_call",),
    "search": ("late_search_spiral",),
    "browser": ("late_search_spiral",),
    "media": ("media_binge_late", "social_isolation_media"),
    "game": ("game_dopamine_late",),
    "routine": ("ritual_anchor", "weekend_ritual_rest", "quiet_dark_bedtime"),
    "ritual": ("ritual_anchor",),
    "religion": ("ritual_anchor",),
    "app_entropy": ("app_entropy_scattered_day",),
    "entropy": ("app_entropy_scattered_day",),
    "health": ("physical_fatigue", "outdoor_nature_day", "low_hr_recovery"),
    "walk": ("outdoor_nature_day", "physical_fatigue"),
    "physical": ("physical_fatigue", "overtraining_arousal"),
    "outdoor": ("outdoor_nature_day",),
    "sedentary": ("sedentary_screen_day",),
    "heart": ("heart_stress_late", "low_hr_recovery"),
    "hr": ("heart_stress_late", "low_hr_recovery"),
    "badnight": ("morning_after_badnight", "deepnight_phone_awake"),
    "morning_after_badnight": ("morning_after_badnight",),
    "deepnight": ("deepnight_phone_awake",),
    "late": ("late_msg_call", "late_search_spiral", "media_binge_late", "bright_light_late"),
    "presleep": ("presleep_msg_drag", "quiet_dark_bedtime", "phone_in_bed"),
    "sensor": ("high_sensor_wear_day", "sensor_sparse_day"),
    "missing": ("sensor_sparse_day",),
    "gps": ("night_out_mobility", "vehicle_noise_day", "outdoor_nature_day"),
    "mobility": ("night_out_mobility", "vehicle_noise_day", "outdoor_nature_day"),
}


NEGATION_WORDS = (
    "low",
    "zero",
    "absent",
    "drop",
    "less",
    "decrease",
    "낮",
    "없",
    "줄",
    "희박",
)


@dataclass
class RouteTerm:
    target: str
    direction: str
    strength: float


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def stable_seed(*parts: object) -> int:
    text = "|".join(str(p) for p in parts)
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return RNG_SEED + int(digest[:8], 16) % 100000


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def clean_text(*parts: Any) -> str:
    return " ".join(str(p) for p in parts if pd.notna(p)).lower()


def parse_routes(text: str) -> tuple[list[RouteTerm], str]:
    terms: list[RouteTerm] = []
    fragments = [f.strip() for f in str(text).split(";") if f.strip()]
    for frag in fragments:
        m = re.search(r"\b(Q[123]|S[1234])\b", frag, flags=re.I)
        if not m:
            continue
        target = m.group(1).upper()
        tail = frag[m.end() :].lower()
        if "no_direct" in tail or "ambiguous" in tail or "up/down" in tail:
            continue
        if "neutral/up" in tail:
            terms.append(RouteTerm(target, "up", 0.5))
            continue
        if "neutral/down" in tail:
            terms.append(RouteTerm(target, "down", 0.5))
            continue
        if re.search(r"\bup\b", tail) and not re.search(r"\bdown\b", tail):
            terms.append(RouteTerm(target, "up", 1.0))
        elif re.search(r"\bdown\b", tail) and not re.search(r"\bup\b", tail):
            terms.append(RouteTerm(target, "down", 1.0))
    # Keep one action per target.  If conflicting, drop that target.
    by_target: dict[str, list[RouteTerm]] = {}
    for term in terms:
        by_target.setdefault(term.target, []).append(term)
    deduped: list[RouteTerm] = []
    for target, vals in by_target.items():
        dirs = {v.direction for v in vals}
        if len(dirs) == 1:
            deduped.append(RouteTerm(target, vals[0].direction, float(np.mean([v.strength for v in vals]))))
    route_key = "|".join(f"{t.target}_{t.direction}" for t in deduped) or "no_direct_or_ambiguous"
    return deduped, route_key


def build_feature_pool(feature_frames: dict[str, pd.DataFrame]) -> dict[str, tuple[str, str]]:
    pool: dict[str, tuple[str, str]] = {}
    for source, frame in feature_frames.items():
        for base_col in base_story_cols(frame):
            col = preferred_col(frame, base_col)
            if col is not None:
                pool[base_col] = (source, col)
    return pool


def sign_for_match(text: str, feature_name: str) -> float:
    idx = text.find(feature_name.lower())
    if idx < 0:
        return 1.0
    window = text[max(0, idx - 28) : min(len(text), idx + len(feature_name) + 28)]
    return -1.0 if any(word in window for word in NEGATION_WORDS) else 1.0


def matched_features(text: str, pool: dict[str, tuple[str, str]]) -> list[tuple[str, float]]:
    text_l = text.lower()
    out: dict[str, float] = {}
    for name in pool:
        if name.lower() in text_l:
            out[name] = sign_for_match(text_l, name)
    for word, names in SEMANTIC_ALIASES.items():
        if word in text_l:
            for name in names:
                for candidate in pool:
                    if name in candidate:
                        out.setdefault(candidate, sign_for_match(text_l, candidate))
    return sorted(out.items())


def rank01(values: np.ndarray | pd.Series, train_mask: np.ndarray | None = None) -> np.ndarray:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if train_mask is None:
        ref = s
    else:
        ref = s.iloc[np.asarray(train_mask, dtype=bool)]
    if ref.nunique(dropna=False) <= 1:
        return np.full(len(s), 0.5, dtype=np.float64)
    ranks = pd.concat([ref, s], ignore_index=True).rank(method="average", pct=True).iloc[len(ref) :].to_numpy(dtype=np.float64)
    return ranks


def standardize_all(values: np.ndarray | pd.Series, train_mask: np.ndarray) -> np.ndarray:
    return robust_standardize(pd.Series(values), train_mask).to_numpy(dtype=np.float64)


def build_z_feature_matrix(
    base: pd.DataFrame,
    feature_frames: dict[str, pd.DataFrame],
    pool: dict[str, tuple[str, str]],
    train_mask: np.ndarray,
) -> pd.DataFrame:
    zcols: dict[str, np.ndarray] = {}
    for name, (source, col) in pool.items():
        zcols[name] = robust_standardize(feature_frames[source][col], train_mask).to_numpy(dtype=np.float64)
    return pd.DataFrame(zcols, index=base.index)


def fallback_episodes(hidden_state: str, full_text: str) -> list[str]:
    text = clean_text(hidden_state, full_text)
    if hidden_state in CORE_EPISODES:
        return [hidden_state]
    episodes: list[str] = []
    for keywords, mapped in KEYWORD_EPISODE_MAP:
        if any(k in text for k in keywords):
            for episode in mapped:
                if episode not in episodes:
                    episodes.append(episode)
    return episodes


def make_hypothesis_score(
    row: pd.Series,
    z_features: pd.DataFrame,
    episodes: pd.DataFrame,
    pool: dict[str, tuple[str, str]],
    train_mask: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    text = clean_text(row["hidden_human_state"], row["human_story"], row["observable_log_pattern"])
    matches = matched_features(text, pool)
    parts: list[np.ndarray] = []
    part_names: list[str] = []
    if matches:
        values = np.zeros(len(z_features), dtype=np.float64)
        total = 0.0
        for name, weight in matches:
            values += float(weight) * z_features[name].to_numpy(dtype=np.float64)
            total += abs(float(weight))
        if total > EPS:
            parts.append(values / total)
            part_names.append("observable_features")
    mapped = fallback_episodes(str(row["hidden_human_state"]), text)
    if mapped:
        vals = episodes[mapped].mean(axis=1).to_numpy(dtype=np.float64)
        parts.append(vals)
        part_names.append("episode_fallback" if str(row["hidden_human_state"]) not in CORE_EPISODES else "core_episode")
    if not parts:
        score = np.zeros(len(z_features), dtype=np.float64)
        source = "unmapped_zero"
    elif len(parts) == 1:
        score = parts[0]
        source = part_names[0]
    else:
        score = 0.55 * parts[0] + 0.45 * parts[1]
        source = "+".join(part_names)
    score = standardize_all(score, train_mask)
    return score, {
        "score_source": source,
        "matched_feature_count": len(matches),
        "matched_features": ",".join(name for name, _ in matches[:24]),
        "fallback_episodes": ",".join(mapped),
    }


def quantile_mask(values: np.ndarray, train_mask: np.ndarray, q: float, greater: bool = True) -> np.ndarray:
    ref = np.asarray(values, dtype=np.float64)[train_mask]
    threshold = float(np.nanquantile(ref, q))
    if greater:
        return np.asarray(values, dtype=np.float64) >= threshold
    return np.asarray(values, dtype=np.float64) <= threshold


def condition_gate(
    row: pd.Series,
    base: pd.DataFrame,
    episodes: pd.DataFrame,
    z_features: pd.DataFrame,
    train_mask: np.ndarray,
) -> tuple[np.ndarray, str, bool]:
    # Only the declared row condition should define the gate.  The
    # `minimal_experiment` text intentionally mentions many counterfactual
    # checks such as weekday/weekend/sign-flip; parsing it as a gate makes
    # contradictory masks and then falsely relaxes them.
    text = clean_text(row["likely_row_condition"])
    mask = np.ones(len(base), dtype=bool)
    tags: list[str] = []

    def apply(m: np.ndarray, tag: str) -> None:
        nonlocal mask
        mask &= np.asarray(m, dtype=bool)
        tags.append(tag)

    if "high sensor" in text or "measurement evidence" in text or "clean subset" in text:
        apply(quantile_mask(episodes["measurement_wear_confidence"].to_numpy(dtype=np.float64), train_mask, 0.45, True), "high_sensor")
    if "low sensor" in text or "sparse" in text or "missing physiology" in text or "not worn" in text:
        sparse = quantile_mask(episodes["measurement_wear_confidence"].to_numpy(dtype=np.float64), train_mask, 0.45, False)
        if "sensor_sparse_day" in z_features:
            sparse |= quantile_mask(z_features["sensor_sparse_day"].to_numpy(dtype=np.float64), train_mask, 0.55, True)
        apply(sparse, "low_sensor")
    if text.startswith("weekday") or "commute/work" in text or "work/study pressure" in text:
        apply(base["is_weekend"].to_numpy(dtype=int) == 0, "weekday")
    if text.startswith("weekend") or "rest-day" in text:
        apply(base["is_weekend"].to_numpy(dtype=int) == 1, "weekend")
    if "late" in text or "deepnight" in text or "presleep" in text or "bedtime window" in text:
        apply(quantile_mask(episodes["bedtime_arousal"].to_numpy(dtype=np.float64), train_mask, 0.55, True), "late_arousal")
    if "badnight" in text or "residue" in text or "lag alignment" in text:
        apply(quantile_mask(episodes["badnight_aftereffect"].to_numpy(dtype=np.float64), train_mask, 0.55, True), "badnight_residue")
    if "payday" in text or "eom" in text or "month-start" in text or "cashflow" in text:
        cash = np.maximum(
            np.abs(standardize_all(episodes["cashflow_stress"].to_numpy(dtype=np.float64), train_mask)),
            np.abs(standardize_all(episodes["cashflow_relief_spend"].to_numpy(dtype=np.float64), train_mask)),
        )
        apply(quantile_mask(cash, train_mask, 0.55, True), "cashflow_calendar")
    if "subject-specific residual" in text or "subject-normalized" in text or "rolling or median baseline" in text:
        tags.append("subject_residual")
    if "date-block" in text or "public-private" in text or "block split" in text:
        tags.append("block_stress_required")
    if "sign flip" in text or "opposite direction" in text:
        tags.append("subject_sign_flip")

    train_count = int((mask & train_mask).sum())
    relaxed = False
    if train_count < MIN_SELECTED:
        relaxed = True
        tags.append("gate_relaxed_too_small")
        mask = np.ones(len(base), dtype=bool)
    return mask, ",".join(tags) if tags else "all_rows", relaxed


def oof_base_predictions(train: pd.DataFrame, split_name: str) -> pd.DataFrame:
    x = base_label_matrix(train).reset_index(drop=True)
    groups = groups_for(train, split_name).reset_index(drop=True)
    preds = np.zeros((len(train), len(TARGETS)), dtype=np.float64)
    for ti, target in enumerate(TARGETS):
        y = train[target].to_numpy(dtype=int)
        for tr_idx, va_idx in folds_for(groups):
            y_tr = y[tr_idx]
            if len(np.unique(y_tr)) < 2:
                preds[va_idx, ti] = float(np.mean(y_tr))
                continue
            model = make_pipeline(
                SimpleImputer(strategy="median"),
                StandardScaler(),
                LogisticRegression(C=0.35, max_iter=1200, solver="lbfgs"),
            )
            model.fit(x.iloc[tr_idx], y_tr)
            preds[va_idx, ti] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return pd.DataFrame(clip_prob(preds), columns=TARGETS)


def multilabel_loss(y_true: np.ndarray, pred: np.ndarray) -> float:
    losses = []
    for i in range(y_true.shape[1]):
        losses.append(log_loss(y_true[:, i], clip_prob(pred[:, i]), labels=[0, 1]))
    return float(np.mean(losses))


def cell_loss(y_true: np.ndarray, pred: np.ndarray) -> np.ndarray:
    p = clip_prob(pred)
    y = np.asarray(y_true, dtype=np.float64)
    return -(y * np.log(p) + (1.0 - y) * np.log1p(-p))


def apply_route(pred: np.ndarray, selected: np.ndarray, routes: list[RouteTerm], amp: float, reverse: bool = False) -> np.ndarray:
    out = clip_prob(pred).copy()
    logits = logit(out)
    for term in routes:
        sign = 1.0 if term.direction == "up" else -1.0
        if reverse:
            sign *= -1.0
        logits[selected, TARGETS.index(term.target)] += sign * float(term.strength) * amp
    return clip_prob(sigmoid(logits))


def select_by_score(score: np.ndarray, gate: np.ndarray, train_mask: np.ndarray, top_frac: float) -> np.ndarray:
    score = np.asarray(score, dtype=np.float64)
    eligible = np.asarray(gate, dtype=bool) & np.asarray(train_mask, dtype=bool)
    selected = np.zeros(len(score), dtype=bool)
    if int(eligible.sum()) < MIN_SELECTED:
        return selected
    q = max(0.0, min(1.0, 1.0 - float(top_frac)))
    cutoff = float(np.nanquantile(score[eligible], q))
    selected = np.asarray(gate, dtype=bool) & (score >= cutoff)
    return selected & train_mask


def direction_label_support(train: pd.DataFrame, selected: np.ndarray, routes: list[RouteTerm]) -> tuple[float, float]:
    if int(selected.sum()) < MIN_SELECTED or int((~selected).sum()) < MIN_SELECTED:
        return 0.0, 0.0
    vals = []
    for term in routes:
        sel_mean = float(train.loc[selected, term.target].mean())
        rest_mean = float(train.loc[~selected, term.target].mean())
        signed = sel_mean - rest_mean if term.direction == "up" else rest_mean - sel_mean
        vals.append(signed)
    arr = np.asarray(vals, dtype=np.float64)
    return float(np.mean(arr)), float(np.mean(arr > 0.0))


def fast_route_delta(
    y: np.ndarray,
    base_pred: np.ndarray,
    base_losses: np.ndarray,
    selected: np.ndarray,
    routes: list[RouteTerm],
    amp: float,
    reverse: bool = False,
) -> float:
    if int(selected.sum()) == 0:
        return 0.0
    selected_idx = np.where(selected)[0]
    total_delta = 0.0
    for term in routes:
        target_idx = TARGETS.index(term.target)
        sign = 1.0 if term.direction == "up" else -1.0
        if reverse:
            sign *= -1.0
        old_p = clip_prob(base_pred[selected_idx, target_idx])
        moved = sigmoid(logit(old_p) + sign * float(term.strength) * amp)
        new_loss = cell_loss(y[selected_idx, target_idx], moved)
        old_loss = base_losses[selected_idx, target_idx]
        total_delta += float(np.sum(new_loss - old_loss))
    return total_delta / float(y.shape[0] * len(TARGETS))


def evaluate_one(
    hyp: pd.Series,
    score_all: np.ndarray,
    gate_all: np.ndarray,
    routes: list[RouteTerm],
    train: pd.DataFrame,
    train_mask: np.ndarray,
    base_pred_arrays: dict[str, np.ndarray],
    base_cell_losses: dict[str, np.ndarray],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    score_train = score_all[train_mask]
    gate_train = gate_all[train_mask]
    local_train_mask = np.ones(len(train), dtype=bool)
    y = train[TARGETS].to_numpy(dtype=int)
    best: dict[str, Any] | None = None
    for top_frac in TOP_FRACS:
        selected = select_by_score(score_train, gate_train, local_train_mask, top_frac)
        n_sel = int(selected.sum())
        if n_sel < MIN_SELECTED:
            continue
        for amp in AMPS:
            split_delta: dict[str, float] = {}
            split_opp: dict[str, float] = {}
            for split_name, pred in base_pred_arrays.items():
                split_delta[split_name] = fast_route_delta(y, pred, base_cell_losses[split_name], selected, routes, amp, reverse=False)
                split_opp[split_name] = fast_route_delta(y, pred, base_cell_losses[split_name], selected, routes, amp, reverse=True)
            avg_delta = float(np.mean(list(split_delta.values())))
            worst_delta = float(np.max(list(split_delta.values())))
            avg_opp = float(np.mean(list(split_opp.values())))
            support_mean, support_rate = direction_label_support(train, selected, routes)
            rec = {
                "top_frac": top_frac,
                "amp": amp,
                "selected_rows": n_sel,
                "subject5_delta": split_delta["subject5"],
                "dateblock5_delta": split_delta["dateblock5"],
                "avg_delta": avg_delta,
                "worst_delta": worst_delta,
                "subject5_opposite_delta": split_opp["subject5"],
                "dateblock5_opposite_delta": split_opp["dateblock5"],
                "opposite_avg_delta": avg_opp,
                "direction_support_mean": support_mean,
                "direction_support_rate": support_rate,
            }
            if best is None or (rec["worst_delta"], rec["avg_delta"], -rec["selected_rows"]) < (
                best["worst_delta"],
                best["avg_delta"],
                -best["selected_rows"],
            ):
                best = rec
    null_rows: list[dict[str, Any]] = []
    if best is None:
        out = {
            "hypothesis_id": hyp["hypothesis_id"],
            "selected_rows": 0,
            "top_frac": np.nan,
            "amp": np.nan,
            "subject5_delta": np.nan,
            "dateblock5_delta": np.nan,
            "avg_delta": np.nan,
            "worst_delta": np.nan,
            "opposite_avg_delta": np.nan,
            "direction_support_mean": 0.0,
            "direction_support_rate": 0.0,
            "null_median": np.nan,
            "null_dominance": 0.0,
            "verdict": "not_enough_rows",
        }
        return out, null_rows

    selected = select_by_score(score_train, gate_train, local_train_mask, float(best["top_frac"]))
    rng = np.random.default_rng(stable_seed("null", hyp["hypothesis_id"]))
    null_avg: list[float] = []
    for mode in ["row", "subject", "dateblock"]:
        for rep in range(NULL_REPS):
            if mode == "row":
                eligible = np.where(gate_train)[0]
                if len(eligible) < int(selected.sum()):
                    null_sel = selected.copy()
                else:
                    pick = rng.choice(eligible, size=int(selected.sum()), replace=False)
                    null_sel = np.zeros(len(train), dtype=bool)
                    null_sel[pick] = True
            else:
                group_col = "subject_id" if mode == "subject" else "dateblock_group"
                shuffled = score_train.copy()
                for _, idx in train.reset_index().groupby(group_col)["index"]:
                    idx_arr = idx.to_numpy(dtype=int)
                    shuffled[idx_arr] = shuffled[idx_arr][rng.permutation(len(idx_arr))]
                null_sel = select_by_score(shuffled, gate_train, local_train_mask, float(best["top_frac"]))
            split_vals = []
            for split_name, pred in base_pred_arrays.items():
                split_vals.append(fast_route_delta(y, pred, base_cell_losses[split_name], null_sel, routes, float(best["amp"]), reverse=False))
            avg = float(np.mean(split_vals))
            null_avg.append(avg)
            null_rows.append(
                {
                    "hypothesis_id": hyp["hypothesis_id"],
                    "mode": mode,
                    "rep": rep,
                    "null_selected_rows": int(null_sel.sum()),
                    "null_avg_delta": avg,
                }
            )
    null_arr = np.asarray(null_avg, dtype=np.float64)
    null_median = float(np.median(null_arr)) if len(null_arr) else np.nan
    null_dominance = float(np.mean(float(best["avg_delta"]) < null_arr)) if len(null_arr) else 0.0
    expected_beats_opposite = bool(float(best["avg_delta"]) < float(best["opposite_avg_delta"]))

    if (
        float(best["subject5_delta"]) < -1.0e-5
        and float(best["dateblock5_delta"]) < -1.0e-5
        and expected_beats_opposite
        and float(best["direction_support_rate"]) >= 0.5
        and null_dominance >= 0.55
    ):
        verdict = "survives_both_splits"
    elif float(best["subject5_delta"]) < 0.0 and float(best["dateblock5_delta"]) >= 0.0:
        verdict = "subject_only_fragile"
    elif float(best["dateblock5_delta"]) < 0.0 and float(best["subject5_delta"]) >= 0.0:
        verdict = "dateblock_only_fragile"
    elif not expected_beats_opposite:
        verdict = "direction_reversed_or_ambiguous"
    elif float(best["avg_delta"]) < 0.0:
        verdict = "weak_avg_only"
    else:
        verdict = "no_local_support"

    out = {
        "hypothesis_id": hyp["hypothesis_id"],
        **best,
        "null_median": null_median,
        "null_dominance": null_dominance,
        "expected_beats_opposite": expected_beats_opposite,
        "verdict": verdict,
    }
    return out, null_rows


def summarize(results: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    state = (
        results.groupby("hidden_human_state")
        .agg(
            n=("hypothesis_id", "count"),
            high=("priority", lambda s: int((s == "high").sum())),
            survives=("verdict", lambda s: int((s == "survives_both_splits").sum())),
            weak=("verdict", lambda s: int((s == "weak_avg_only").sum())),
            reversed=("verdict", lambda s: int((s == "direction_reversed_or_ambiguous").sum())),
            best_avg_delta=("avg_delta", "min"),
            best_worst_delta=("worst_delta", "min"),
            median_avg_delta=("avg_delta", "median"),
            best_null_dominance=("null_dominance", "max"),
        )
        .sort_values(["survives", "best_worst_delta", "best_avg_delta"], ascending=[False, True, True])
        .reset_index()
    )
    gate = (
        results.assign(gate_primary=results["gate_tags"].astype(str).str.split(",").str[0])
        .groupby("gate_primary")
        .agg(
            n=("hypothesis_id", "count"),
            survives=("verdict", lambda s: int((s == "survives_both_splits").sum())),
            best_avg_delta=("avg_delta", "min"),
            median_avg_delta=("avg_delta", "median"),
        )
        .sort_values(["survives", "best_avg_delta"], ascending=[False, True])
        .reset_index()
    )
    family = (
        results.groupby("route_key")
        .agg(
            n=("hypothesis_id", "count"),
            survives=("verdict", lambda s: int((s == "survives_both_splits").sum())),
            weak=("verdict", lambda s: int((s == "weak_avg_only").sum())),
            best_avg_delta=("avg_delta", "min"),
            best_worst_delta=("worst_delta", "min"),
            median_avg_delta=("avg_delta", "median"),
        )
        .sort_values(["survives", "best_worst_delta", "best_avg_delta"], ascending=[False, True, True])
        .reset_index()
    )
    shortlist = results.sort_values(
        [
            "verdict_rank",
            "worst_delta",
            "avg_delta",
            "null_dominance",
            "direction_support_rate",
            "selected_rows",
        ],
        ascending=[True, True, True, False, False, False],
    ).head(80)
    return state, gate, family, shortlist


def write_report(
    parsed: pd.DataFrame,
    results: pd.DataFrame,
    state: pd.DataFrame,
    gate: pd.DataFrame,
    family: pd.DataFrame,
    shortlist: pd.DataFrame,
) -> None:
    verdict_counts = results["verdict"].value_counts().rename_axis("verdict").reset_index(name="n")
    priority_counts = parsed["priority"].value_counts().rename_axis("priority").reset_index(name="n")
    cols = [
        "hypothesis_id",
        "hidden_human_state",
        "priority",
        "route_key",
        "gate_tags",
        "selected_rows",
        "amp",
        "top_frac",
        "subject5_delta",
        "dateblock5_delta",
        "avg_delta",
        "worst_delta",
        "opposite_avg_delta",
        "null_dominance",
        "direction_support_rate",
        "verdict",
    ]
    state_cols = [
        "hidden_human_state",
        "n",
        "high",
        "survives",
        "weak",
        "reversed",
        "best_avg_delta",
        "best_worst_delta",
        "median_avg_delta",
        "best_null_dominance",
    ]
    family_cols = ["route_key", "n", "survives", "weak", "best_avg_delta", "best_worst_delta", "median_avg_delta"]
    lines = [
        "# H005 All Human-State Route Hypotheses",
        "",
        "## Question",
        "",
        "Can the 1000 imported human/social hypotheses be converted into falsifiable HS-JEPA route tests, and which story families survive local direction, split, and null stress?",
        "",
        "## Method",
        "",
        "- Parse each row into `hidden_human_state`, row gate, and direct target route.",
        "- Build a state score from matched human/social/cashflow features plus core HS-JEPA episode fallback.",
        "- On train OOF predictions, apply only the stated tiny route direction.",
        "- Compare against no move, opposite direction, subject/dateblock OOF, and shuffled controls.",
        "- No public LB is used.",
        "",
        "## Inventory",
        "",
        f"- hypotheses: `{len(parsed)}`",
        f"- direct-testable hypotheses: `{int(results['is_testable'].sum())}`",
        f"- states: `{parsed['hidden_human_state'].nunique()}`",
        f"- route families: `{parsed['route_key'].nunique()}`",
        "",
        "### Priority Counts",
        "",
        md_table(priority_counts, n=10),
        "",
        "### Verdict Counts",
        "",
        md_table(verdict_counts, n=20),
        "",
        "## Shortlist",
        "",
        md_table(shortlist[cols], n=30, floatfmt=".9f"),
        "",
        "## Best Hidden States",
        "",
        md_table(state[state_cols], n=35, floatfmt=".9f"),
        "",
        "## Best Route Families",
        "",
        md_table(family[family_cols], n=35, floatfmt=".9f"),
        "",
        "## Gate Summary",
        "",
        md_table(gate, n=30, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    strict_n = int((results["verdict"] == "survives_both_splits").sum())
    weak_n = int((results["verdict"] == "weak_avg_only").sum())
    reversed_n = int((results["verdict"] == "direction_reversed_or_ambiguous").sum())
    if strict_n:
        lines.append(
            f"`{strict_n}` hypotheses survived both subject and dateblock stress. These are not submission-ready by themselves, but they are route-library candidates for a later sparse materializer."
        )
    else:
        lines.append(
            "No hypothesis passed the strict both-split gate. The CSV is still useful as a story generator, but direct translation from story to target movement remains the bottleneck."
        )
    lines.append(
        f"`{weak_n}` hypotheses were average-favorable but split-fragile; `{reversed_n}` looked more consistent in the opposite direction or had ambiguous directional support."
    )
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(PARSED_OUT)}`",
            f"- `{rel(TEST_OUT)}`",
            f"- `{rel(NULL_OUT)}`",
            f"- `{rel(STATE_OUT)}`",
            f"- `{rel(GATE_OUT)}`",
            f"- `{rel(FAMILY_OUT)}`",
            f"- `{rel(SHORTLIST_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not HYPOTHESIS_IN.exists():
        raise FileNotFoundError(HYPOTHESIS_IN)

    hypotheses = pd.read_csv(HYPOTHESIS_IN)
    base, raw, stories, feature_frames = load_frames()
    episodes, episode_defs = build_episode_matrix(base, feature_frames)
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)

    pool = build_feature_pool(feature_frames)
    z_features = build_z_feature_matrix(base, feature_frames, pool, train_mask)
    base_preds = {
        "subject5": oof_base_predictions(train, "subject5"),
        "dateblock5": oof_base_predictions(train, "dateblock5"),
    }
    y_train = train[TARGETS].to_numpy(dtype=int)
    base_pred_arrays = {split: pred[TARGETS].to_numpy(dtype=np.float64) for split, pred in base_preds.items()}
    base_cell_losses = {split: cell_loss(y_train, pred) for split, pred in base_pred_arrays.items()}
    base_losses = {split: float(losses.mean()) for split, losses in base_cell_losses.items()}

    parsed_rows: list[dict[str, Any]] = []
    result_rows: list[dict[str, Any]] = []
    null_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(hypotheses.itertuples(index=False), start=1):
        if idx == 1 or idx % 100 == 0:
            print(f"[h005] evaluating {idx}/{len(hypotheses)}", flush=True)
        hyp = pd.Series(row._asdict())
        routes, route_key = parse_routes(str(hyp["expected_target_route"]))
        score, score_meta = make_hypothesis_score(hyp, z_features, episodes, pool, train_mask)
        gate, gate_tags, gate_relaxed = condition_gate(hyp, base, episodes, z_features, train_mask)
        active_targets = ",".join(term.target for term in routes)
        parsed = {
            "hypothesis_id": hyp["hypothesis_id"],
            "hidden_human_state": hyp["hidden_human_state"],
            "priority": hyp["priority"],
            "route_key": route_key,
            "active_targets": active_targets,
            "n_route_targets": len(routes),
            "gate_tags": gate_tags,
            "gate_relaxed": gate_relaxed,
            "train_gate_rows": int((gate & train_mask).sum()),
            "test_gate_rows": int((gate & ~train_mask).sum()),
            **score_meta,
            "human_story": hyp["human_story"],
            "observable_log_pattern": hyp["observable_log_pattern"],
            "expected_target_route": hyp["expected_target_route"],
            "likely_row_condition": hyp["likely_row_condition"],
            "minimal_experiment": hyp["minimal_experiment"],
            "prediction_role": hyp["prediction_role"],
            "risk_of_being_spurious_leakage_public_overfit": hyp["risk_of_being_spurious_leakage_public_overfit"],
        }
        parsed_rows.append(parsed)
        if not routes:
            result = {
                "hypothesis_id": hyp["hypothesis_id"],
                "selected_rows": 0,
                "top_frac": np.nan,
                "amp": np.nan,
                "subject5_delta": np.nan,
                "dateblock5_delta": np.nan,
                "avg_delta": np.nan,
                "worst_delta": np.nan,
                "opposite_avg_delta": np.nan,
                "direction_support_mean": 0.0,
                "direction_support_rate": 0.0,
                "null_median": np.nan,
                "null_dominance": 0.0,
                "expected_beats_opposite": False,
                "verdict": "no_direct_route",
            }
        else:
            result, nrows = evaluate_one(hyp, score, gate, routes, train, train_mask, base_pred_arrays, base_cell_losses)
            null_rows.extend(nrows)
        result.update(parsed)
        result["is_testable"] = bool(routes)
        result_rows.append(result)

    parsed_df = pd.DataFrame(parsed_rows)
    results = pd.DataFrame(result_rows)
    verdict_rank = {
        "survives_both_splits": 0,
        "weak_avg_only": 1,
        "subject_only_fragile": 2,
        "dateblock_only_fragile": 3,
        "direction_reversed_or_ambiguous": 4,
        "no_local_support": 5,
        "not_enough_rows": 6,
        "no_direct_route": 7,
    }
    results["verdict_rank"] = results["verdict"].map(verdict_rank).fillna(99).astype(int)

    state, gate_summary, family, shortlist = summarize(results)

    parsed_df.to_csv(PARSED_OUT, index=False)
    results.sort_values(["verdict_rank", "worst_delta", "avg_delta"], ascending=[True, True, True]).to_csv(TEST_OUT, index=False)
    pd.DataFrame(null_rows).to_csv(NULL_OUT, index=False)
    state.to_csv(STATE_OUT, index=False)
    gate_summary.to_csv(GATE_OUT, index=False)
    family.to_csv(FAMILY_OUT, index=False)
    shortlist.to_csv(SHORTLIST_OUT, index=False)
    write_report(parsed_df, results, state, gate_summary, family, shortlist)

    print(f"report={rel(REPORT_OUT)}")
    print("[base_losses]", {k: round(v, 9) for k, v in base_losses.items()})
    print("[verdict_counts]")
    print(results["verdict"].value_counts().to_string())
    print("[shortlist]")
    cols = [
        "hypothesis_id",
        "hidden_human_state",
        "priority",
        "route_key",
        "gate_tags",
        "selected_rows",
        "subject5_delta",
        "dateblock5_delta",
        "avg_delta",
        "null_dominance",
        "verdict",
    ]
    print(shortlist[cols].head(25).round(9).to_string(index=False))


if __name__ == "__main__":
    main()
