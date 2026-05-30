#!/usr/bin/env python3
"""E268: human/social story atlas after the E267 public miss.

The question is not whether a social feature can be added to a tabular model.
The question is whether human-day stories explain the current public-positive
E247 Q3 rollback cells without collapsing into the E267 failed action.

Inputs:
- E262 day-level raw lifelog features.
- E247 public winner, E256 same-family loss, E267 social-gated loss.
- Train labels for blocked stress tests.

Outputs:
- Many explicit social/lifestyle hypotheses as story scores.
- Label lift, blocked CV deltas, train/test shift, and public-anchor movement
  alignment diagnostics.
- A report that separates "story is real" from "story became a bad action".
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

HUMAN_PATH = OUT / "e262_human_social_day_features.parquet"
E247 = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E267 = OUT / "submission_e267_humansocial_tail_balanced_2936100f.csv"
E224 = OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E95 = OUT / "submission_e95_hardtail_541e3973.csv"

STORY_OUT = OUT / "e268_human_social_story_features.parquet"
HYP_OUT = OUT / "e268_human_social_story_hypotheses.csv"
LABEL_OUT = OUT / "e268_human_social_story_label_probe.csv"
CV_OUT = OUT / "e268_human_social_story_cv.csv"
MOVE_OUT = OUT / "e268_human_social_story_movement_alignment.csv"
LATENT_OUT = OUT / "e268_human_social_story_latent.csv"
REPORT_OUT = OUT / "e268_human_social_story_atlas_report.md"


@dataclass(frozen=True)
class StorySpec:
    story_id: str
    family: str
    human_story: str
    positive_if_high: str
    terms: tuple[tuple[str, float], ...]


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".6f") -> str:
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


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def signed_log1p(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").fillna(0.0).astype(float)
    return np.sign(x) * np.log1p(np.abs(x))


def robust_z_from_train(all_s: pd.Series, train_mask: pd.Series) -> pd.Series:
    x = signed_log1p(all_s)
    tr = x[train_mask].replace([np.inf, -np.inf], np.nan).dropna()
    if tr.empty:
        return pd.Series(0.0, index=all_s.index)
    med = float(tr.median())
    q75 = float(tr.quantile(0.75))
    q25 = float(tr.quantile(0.25))
    scale = (q75 - q25) / 1.349
    if not np.isfinite(scale) or scale < 1.0e-9:
        scale = float(tr.std(ddof=0))
    if not np.isfinite(scale) or scale < 1.0e-9:
        return pd.Series(0.0, index=all_s.index)
    return ((x - med) / scale).replace([np.inf, -np.inf], 0.0).fillna(0.0)


def subject_z_from_train(s: pd.Series, df: pd.DataFrame, train_mask: pd.Series) -> pd.Series:
    out = pd.Series(0.0, index=s.index, dtype=float)
    global_mean = float(s[train_mask].mean())
    global_std = float(s[train_mask].std(ddof=0))
    if not np.isfinite(global_std) or global_std < 1.0e-9:
        global_std = 1.0
    for subject, idx in df.groupby("subject_id").groups.items():
        idx_list = list(idx)
        tr_idx = [i for i in idx_list if bool(train_mask.iloc[i])]
        if tr_idx:
            mu = float(s.iloc[tr_idx].mean())
            sd = float(s.iloc[tr_idx].std(ddof=0))
            if not np.isfinite(sd) or sd < 1.0e-9:
                sd = global_std
        else:
            mu, sd = global_mean, global_std
        out.iloc[idx_list] = (s.iloc[idx_list] - mu) / sd
    return out.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def load_human() -> pd.DataFrame:
    df = pd.read_parquet(HUMAN_PATH).copy()
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    df = df.sort_values(KEYS).reset_index(drop=True)
    df["subject_order"] = df.groupby("subject_id").cumcount().astype(int)
    df["dateblock_group"] = df["subject_id"].astype(str) + "_b" + (df["subject_order"] // 7).astype(str)
    df["weekday_sin"] = np.sin(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    df["weekday_cos"] = np.cos(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    return df


def story_specs() -> list[StorySpec]:
    return [
        StorySpec("late_msg_call", "social_overstim", "Late Kakao/message/call load before sleep.", "night social arousal", (
            ("usage_late_social_msg_time", 1.0), ("usage_late_call_time", 1.0), ("ambience_speech_late", 0.7), ("screen_m_screen_use_mean_late", 0.5)
        )),
        StorySpec("presleep_msg_drag", "social_overstim", "Presleep messaging plus repeated phone checks.", "bedtime social drag", (
            ("usage_presleep_social_msg_time", 1.0), ("usage_presleep_call_time", 0.8), ("screen_m_screen_use_count_presleep", 0.7), ("screen_m_screen_use_sum_presleep", 0.5)
        )),
        StorySpec("deepnight_phone_awake", "sleep_fragment", "Phone activity after midnight when the day should be winding down.", "fragmented sleep onset", (
            ("usage_deepnight_social_msg_time", 1.0), ("usage_deepnight_media_time", 0.9), ("usage_deepnight_search_browser_time", 0.8), ("screen_m_screen_use_mean_deepnight", 1.0), ("mlight_m_light_mean_deepnight", 0.6)
        )),
        StorySpec("late_search_spiral", "cognitive_load", "Late searching, browsing, work, finance, and shopping loops.", "cognitive rumination", (
            ("usage_late_search_browser_time", 1.0), ("usage_late_work_study_time", 0.9), ("usage_late_finance_time", 0.9), ("usage_late_shopping_time", 0.8), ("screen_m_screen_use_mean_late", 0.5)
        )),
        StorySpec("finance_shopping_stress", "cognitive_load", "Money or shopping attention late in the day.", "planning or stress", (
            ("usage_presleep_finance_time", 1.0), ("usage_late_finance_time", 1.0), ("usage_presleep_shopping_time", 0.8), ("usage_late_shopping_time", 0.8)
        )),
        StorySpec("media_binge_late", "media_binge", "Late video/music/game consumption.", "passive overstimulation", (
            ("usage_late_media_time", 1.0), ("usage_presleep_media_time", 0.8), ("usage_late_game_time", 0.8), ("usage_deepnight_media_time", 0.9)
        )),
        StorySpec("game_dopamine_late", "media_binge", "Late games with screen exposure.", "dopamine arousal", (
            ("usage_late_game_time", 1.0), ("usage_presleep_game_time", 0.8), ("screen_m_screen_use_mean_late", 0.6)
        )),
        StorySpec("ritual_anchor", "routine_anchor", "Religious/routine app use and charging before sleep.", "stable bedtime ritual", (
            ("usage_day_religion_routine_time", 0.7), ("usage_presleep_religion_routine_time", 1.0), ("usage_late_religion_routine_time", 0.8), ("charge_m_charging_mean_presleep", 1.0)
        )),
        StorySpec("charge_bed_anchor", "routine_anchor", "Phone is on charger near bedtime with low mobility.", "settled bedtime", (
            ("charge_m_charging_mean_presleep", 1.0), ("charge_m_charging_mean_late", 0.8), ("gps_speed_mean_late", -0.7), ("pedo_step_sum_late", -0.7)
        )),
        StorySpec("app_entropy_scattered_day", "routine_break", "Attention spread across many apps during the day.", "irregular day", (
            ("usage_day_app_entropy", 1.0), ("usage_day_top_app_share", -0.8), ("usage_day_total_time", 0.3)
        )),
        StorySpec("single_app_monotony", "routine_anchor", "One dominant app or ritual dominates the day.", "stable or stuck routine", (
            ("usage_day_top_app_share", 1.0), ("usage_day_app_entropy", -0.8), ("usage_day_religion_routine_time", 0.4)
        )),
        StorySpec("commute_workday", "workday_commute", "Morning/evening movement and WiFi variety consistent with commute.", "workday structure", (
            ("gps_speed_mean_morning", 1.0), ("gps_speed_mean_evening", 1.0), ("pedo_step_sum_morning", 0.6), ("pedo_step_sum_evening", 0.6), ("wifi_scan_unique_n_day", 0.5)
        )),
        StorySpec("afterwork_recovery", "workday_commute", "Commute signal followed by quiet/charging at night.", "good recovery after work", (
            ("gps_speed_mean_evening", 0.8), ("pedo_step_sum_evening", 0.5), ("charge_m_charging_mean_late", 1.0), ("usage_late_social_msg_time", -0.6), ("screen_m_screen_use_mean_late", -0.6)
        )),
        StorySpec("night_out_mobility", "nightlife_mobility", "Late/deepnight movement, public ambience, weak charging.", "night out or travel", (
            ("gps_speed_mean_late", 1.0), ("gps_speed_mean_deepnight", 1.0), ("gps_cell_unique_n_deepnight", 0.8), ("ambience_inside_public_late", 0.8), ("charge_m_charging_mean_late", -0.8)
        )),
        StorySpec("public_social_evening", "social_outing", "Evening speech/public ambience/BLE density.", "social outing", (
            ("ambience_speech_evening", 1.0), ("ambience_inside_public_evening", 1.0), ("ble_scan_unique_n_evening", 0.8), ("gps_cell_unique_n_evening", 0.5)
        )),
        StorySpec("music_ambient_late", "media_binge", "Music ambience late or deepnight.", "music/noise sleep context", (
            ("ambience_music_late", 1.0), ("ambience_music_deepnight", 1.0), ("ambience_music_evening", 0.5)
        )),
        StorySpec("bright_light_late", "sleep_fragment", "Phone/wearable light exposure near sleep.", "circadian light exposure", (
            ("mlight_m_light_mean_late", 1.0), ("wlight_w_light_mean_late", 1.0), ("mlight_m_light_mean_presleep", 0.7), ("wlight_w_light_mean_presleep", 0.7)
        )),
        StorySpec("phone_in_bed", "sleep_fragment", "Screen use while phone is charging at presleep.", "bed phone use", (
            ("screen_m_screen_use_mean_presleep", 1.0), ("screen_m_screen_use_count_presleep", 0.7), ("charge_m_charging_mean_presleep", 0.9), ("pedo_step_sum_presleep", -0.6)
        )),
        StorySpec("screen_fragmentation", "sleep_fragment", "Many short screen sessions late.", "fragmented attention", (
            ("screen_m_screen_use_count_late", 1.0), ("screen_m_screen_use_std_late", 0.6), ("screen_m_screen_use_max_late", -0.3)
        )),
        StorySpec("physical_fatigue", "physical_fatigue", "High steps/distance/calories and heart activity.", "body fatigue", (
            ("pedo_step_sum_day", 1.0), ("pedo_distance_sum_day", 0.8), ("pedo_burned_calories_sum_day", 0.8), ("hr_heart_rate_mean_mean_day", 0.5)
        )),
        StorySpec("overtraining_arousal", "physical_fatigue", "Physical load plus high evening/presleep heart rate.", "over-aroused fatigue", (
            ("pedo_step_sum_day", 0.8), ("hr_heart_rate_mean_mean_presleep", 1.0), ("hr_heart_rate_max_mean_presleep", 0.8), ("screen_m_screen_use_mean_late", 0.4)
        )),
        StorySpec("sedentary_screen_day", "sedentary_screen", "Low movement but high screen/media/social day.", "sedentary stimulation", (
            ("pedo_step_sum_day", -1.0), ("usage_day_total_time", 0.8), ("usage_presleep_media_time", 0.6), ("usage_presleep_social_msg_time", 0.6)
        )),
        StorySpec("heart_stress_late", "physiology_stress", "High late/presleep heart rate and variance.", "physiological stress", (
            ("hr_heart_rate_mean_mean_late", 1.0), ("hr_heart_rate_max_mean_late", 0.8), ("hr_heart_rate_std_mean_late", 0.8), ("hr_heart_rate_mean_mean_presleep", 0.7)
        )),
        StorySpec("low_hr_recovery", "physiology_recovery", "Low presleep heart rate and quiet charging.", "recovery state", (
            ("hr_heart_rate_mean_mean_presleep", -1.0), ("hr_heart_rate_std_mean_presleep", -0.6), ("charge_m_charging_mean_presleep", 0.8), ("screen_m_screen_use_mean_late", -0.5)
        )),
        StorySpec("home_stability", "routine_anchor", "Low GPS range, stable WiFi, charge, and low public ambience.", "home anchor", (
            ("gps_lat_range_day", -0.7), ("gps_lon_range_day", -0.7), ("wifi_scan_unique_n_day", -0.3), ("charge_m_charging_mean_presleep", 1.0), ("ambience_inside_public_evening", -0.5)
        )),
        StorySpec("sensor_sparse_day", "measurement_state", "Sparse sensor counts that may encode phone/watch availability.", "measurement dropout", (
            ("hr_heart_rate_mean_count_day", -1.0), ("pedo_step_count_day", -0.8), ("screen_m_screen_use_count_day", -0.3), ("wifi_scan_n_day", -0.4), ("ble_scan_n_day", -0.4)
        )),
        StorySpec("high_sensor_wear_day", "measurement_state", "Dense wearable and phone sensing.", "high wear compliance", (
            ("hr_heart_rate_mean_count_day", 1.0), ("pedo_step_count_day", 0.8), ("wifi_scan_n_day", 0.4), ("ble_scan_n_day", 0.4)
        )),
        StorySpec("social_isolation_media", "social_isolation", "Low direct social signal but high passive media/home utility.", "isolated screen day", (
            ("usage_day_social_msg_time", -0.8), ("usage_day_call_time", -0.8), ("ambience_speech_day", -0.5), ("usage_presleep_media_time", 0.9), ("usage_day_home_utility_time", 0.4)
        )),
        StorySpec("weekday_routine_pressure", "calendar_social", "Weekday plus commute/work/study signal.", "work pressure day", (
            ("is_weekend", -1.0), ("gps_speed_mean_morning", 0.8), ("usage_day_work_study_time", 0.7), ("usage_late_work_study_time", 0.5)
        )),
        StorySpec("weekend_social_jetlag", "calendar_social", "Weekend late social/media/deepnight phone.", "weekend social jetlag", (
            ("is_weekend", 1.0), ("usage_late_social_msg_time", 0.8), ("usage_late_media_time", 0.8), ("screen_m_screen_use_mean_deepnight", 0.6)
        )),
        StorySpec("weekend_ritual_rest", "calendar_social", "Weekend routine/religion/charge and low mobility.", "weekend recovery ritual", (
            ("is_weekend", 1.0), ("usage_day_religion_routine_time", 0.8), ("charge_m_charging_mean_presleep", 0.8), ("gps_speed_mean_evening", -0.6)
        )),
        StorySpec("morning_after_badnight", "nextday_echo", "High morning heart/mobility after a possibly fragmented night.", "next-day compensation", (
            ("hr_heart_rate_mean_mean_morning", 0.8), ("gps_speed_mean_morning", 0.8), ("screen_m_screen_use_count_morning", 0.5), ("pedo_step_sum_morning", 0.5)
        )),
        StorySpec("quiet_dark_bedtime", "routine_anchor", "Low late light/screen/mobility with charging.", "quiet bedtime", (
            ("mlight_m_light_mean_late", -1.0), ("wlight_w_light_mean_late", -0.8), ("screen_m_screen_use_mean_late", -0.8), ("pedo_step_sum_late", -0.5), ("charge_m_charging_mean_late", 0.8)
        )),
        StorySpec("outdoor_nature_day", "environment", "Outdoor/nature ambience and movement.", "outdoor day", (
            ("ambience_outside_day", 1.0), ("ambience_animal_nature_day", 0.8), ("gps_cell_unique_n_day", 0.5), ("pedo_step_sum_day", 0.5)
        )),
        StorySpec("vehicle_noise_day", "environment", "Vehicle ambience and GPS speed.", "travel/commute noise", (
            ("ambience_vehicle_day", 1.0), ("ambience_vehicle_evening", 0.7), ("gps_speed_mean_day", 0.6), ("gps_speed_mean_evening", 0.5)
        )),
    ]


def build_story_features(df: pd.DataFrame, specs: list[StorySpec]) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_mask = df["split"].eq("train")
    zcols: dict[str, pd.Series] = {}

    def zcol(col: str) -> pd.Series:
        if col not in df.columns:
            return pd.Series(0.0, index=df.index)
        if col not in zcols:
            zcols[col] = robust_z_from_train(df[col], train_mask)
        return zcols[col]

    out = df[KEYS + ["split", "weekday", "is_weekend", "subject_order", "dateblock_group"] + TARGETS].copy()
    meta_rows = []
    for spec in specs:
        score = pd.Series(0.0, index=df.index, dtype=float)
        missing = []
        used = []
        for col, weight in spec.terms:
            if col not in df.columns:
                missing.append(col)
            else:
                used.append(col)
                score = score + float(weight) * zcol(col)
        if used:
            score = robust_z_from_train(score, train_mask)
        else:
            score = pd.Series(0.0, index=df.index)
        subj_z = subject_z_from_train(score, df, train_mask)
        out[spec.story_id] = score
        out[f"{spec.story_id}_subj_z"] = subj_z
        out[f"{spec.story_id}_abs_subj_z"] = subj_z.abs()
        out[f"{spec.story_id}_weekend"] = score * df["is_weekend"].astype(float)
        meta_rows.append({
            "story_id": spec.story_id,
            "family": spec.family,
            "human_story": spec.human_story,
            "positive_if_high": spec.positive_if_high,
            "n_terms": len(spec.terms),
            "n_terms_present": len(used),
            "missing_terms": ",".join(missing),
            "used_terms": ",".join(used),
        })

    return out, pd.DataFrame(meta_rows)


def label_probe(story_df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    rows = []
    train = story_df[story_df["split"].eq("train")].copy()
    for _, m in meta.iterrows():
        sid = m["story_id"]
        for variant in [sid, f"{sid}_subj_z", f"{sid}_abs_subj_z"]:
            x = train[variant].astype(float)
            if x.nunique(dropna=True) < 4:
                continue
            q25, q75 = x.quantile([0.25, 0.75])
            low = x <= q25
            high = x >= q75
            if int(low.sum()) < 20 or int(high.sum()) < 20:
                continue
            for target in TARGETS:
                y = train[target].astype(float)
                low_mean = float(y[low].mean())
                high_mean = float(y[high].mean())
                effect = high_mean - low_mean
                corr = float(np.corrcoef(x, y)[0, 1]) if x.std(ddof=0) > 1.0e-9 else 0.0
                rows.append({
                    "story_id": sid,
                    "variant": variant.replace(sid, "score"),
                    "family": m["family"],
                    "target": target,
                    "label_mean_low_q": low_mean,
                    "label_mean_high_q": high_mean,
                    "high_minus_low": effect,
                    "abs_effect": abs(effect),
                    "corr": corr,
                })
    return pd.DataFrame(rows).sort_values(["abs_effect", "story_id"], ascending=[False, True]).reset_index(drop=True)


def make_design(df: pd.DataFrame, story_id: str | None, include_subject: bool) -> pd.DataFrame:
    x = pd.DataFrame(index=df.index)
    x["weekday_sin"] = np.sin(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    x["weekday_cos"] = np.cos(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    x["is_weekend"] = df["is_weekend"].astype(float)
    x["subject_order"] = df["subject_order"].astype(float) / max(float(df["subject_order"].max()), 1.0)
    if include_subject:
        d = pd.get_dummies(df["subject_id"], prefix="subj", dtype=float)
        x = pd.concat([x, d], axis=1)
    if story_id is not None:
        for suffix in ["", "_subj_z", "_abs_subj_z", "_weekend"]:
            col = f"{story_id}{suffix}"
            if col in df.columns:
                x[col] = df[col].astype(float)
    return x.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def predict_cv(x: pd.DataFrame, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    pred = np.zeros(len(y), dtype=float)
    gkf = GroupKFold(n_splits=min(5, len(np.unique(groups))))
    for tr_idx, va_idx in gkf.split(x, y, groups=groups):
        y_tr = y[tr_idx]
        if len(np.unique(y_tr)) < 2:
            pred[va_idx] = float(np.mean(y_tr))
            continue
        model = make_pipeline(
            StandardScaler(with_mean=False),
            LogisticRegression(C=0.5, max_iter=1000, solver="lbfgs"),
        )
        model.fit(x.iloc[tr_idx], y_tr)
        pred[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return clip_prob(pred)


def cv_probe(story_df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    train = story_df[story_df["split"].eq("train")].reset_index(drop=True).copy()
    split_specs = [
        ("dateblock5", train["dateblock_group"].astype(str).to_numpy(), True),
        ("subject5", train["subject_id"].astype(str).to_numpy(), False),
    ]
    rows = []
    baseline_cache: dict[tuple[str, str], tuple[np.ndarray, float]] = {}
    for split_name, groups, include_subject in split_specs:
        x_base = make_design(train, None, include_subject=include_subject)
        for target in TARGETS:
            y = train[target].astype(int).to_numpy()
            pred_base = predict_cv(x_base, y, groups)
            loss_base = float(log_loss(y, pred_base, labels=[0, 1]))
            baseline_cache[(split_name, target)] = (pred_base, loss_base)
        for _, m in meta.iterrows():
            sid = m["story_id"]
            x_story = make_design(train, sid, include_subject=include_subject)
            for target in TARGETS:
                y = train[target].astype(int).to_numpy()
                _, loss_base = baseline_cache[(split_name, target)]
                pred_story = predict_cv(x_story, y, groups)
                loss_story = float(log_loss(y, pred_story, labels=[0, 1]))
                rows.append({
                    "story_id": sid,
                    "family": m["family"],
                    "split": split_name,
                    "target": target,
                    "loss_base": loss_base,
                    "loss_story": loss_story,
                    "delta_logloss": loss_story - loss_base,
                })
    return pd.DataFrame(rows).sort_values(["delta_logloss", "story_id"]).reset_index(drop=True)


def load_submission(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    return df.sort_values(KEYS).reset_index(drop=True)


def cohen_d(a: pd.Series, b: pd.Series) -> float:
    aa = pd.to_numeric(a, errors="coerce").dropna().astype(float)
    bb = pd.to_numeric(b, errors="coerce").dropna().astype(float)
    if len(aa) < 2 or len(bb) < 2:
        return 0.0
    pooled = np.sqrt((aa.var(ddof=1) + bb.var(ddof=1)) / 2.0)
    if not np.isfinite(pooled) or pooled < 1.0e-9:
        return 0.0
    return float((aa.mean() - bb.mean()) / pooled)


def movement_alignment(story_df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    test = story_df[story_df["split"].eq("test")].sort_values(KEYS).reset_index(drop=True).copy()
    s247 = load_submission(E247)
    s256 = load_submission(E256)
    s267 = load_submission(E267)
    s224 = load_submission(E224)
    s95 = load_submission(E95)
    for name, sub in [("e247", s247), ("e256", s256), ("e267", s267), ("e224", s224), ("e95", s95)]:
        if not test[KEYS].equals(sub[KEYS]):
            raise RuntimeError(f"{name} key order does not match E262 test rows")

    rows = []
    neutral = pd.Series(True, index=test.index)
    q3_e247 = np.abs(logit(s247["Q3"].to_numpy()) - logit(s224["Q3"].to_numpy())) > 1.0e-10
    q3_e256 = np.abs(logit(s256["Q3"].to_numpy()) - logit(s224["Q3"].to_numpy())) > 1.0e-10
    q3_e247_only = pd.Series(q3_e247 & ~q3_e256, index=test.index)
    q3_e256_only = pd.Series(q3_e256 & ~q3_e247, index=test.index)
    q3_common = pd.Series(q3_e247 & q3_e256, index=test.index)
    q3_any = pd.Series(q3_e247 | q3_e256, index=test.index)
    e267_any = pd.Series(False, index=test.index)
    e267_q3 = pd.Series(np.abs(logit(s267["Q3"].to_numpy()) - logit(s247["Q3"].to_numpy())) > 1.0e-10, index=test.index)
    e267_s4 = pd.Series(np.abs(logit(s267["S4"].to_numpy()) - logit(s247["S4"].to_numpy())) > 1.0e-10, index=test.index)
    for target in TARGETS:
        moved = np.abs(logit(s267[target].to_numpy()) - logit(s247[target].to_numpy())) > 1.0e-10
        e267_any |= pd.Series(moved, index=test.index)
    neutral &= ~q3_any & ~e267_any

    group_defs = {
        "q3_e247_only_vs_neutral": q3_e247_only,
        "q3_e256_only_vs_neutral": q3_e256_only,
        "q3_common_vs_neutral": q3_common,
        "e267_any_moved_vs_neutral": e267_any,
        "e267_q3_moved_vs_neutral": e267_q3,
        "e267_s4_moved_vs_neutral": e267_s4,
    }
    for _, m in meta.iterrows():
        sid = m["story_id"]
        for variant in [sid, f"{sid}_subj_z"]:
            x = test[variant].astype(float)
            neutral_x = x[neutral]
            for group_name, mask in group_defs.items():
                rows.append({
                    "story_id": sid,
                    "family": m["family"],
                    "variant": variant.replace(sid, "score"),
                    "group": group_name,
                    "n_group": int(mask.sum()),
                    "n_neutral": int(neutral.sum()),
                    "mean_group": float(x[mask].mean()) if int(mask.sum()) else np.nan,
                    "mean_neutral": float(neutral_x.mean()) if int(neutral.sum()) else np.nan,
                    "cohen_d_group_vs_neutral": cohen_d(x[mask], neutral_x),
                })

        x = test[f"{sid}_subj_z"].astype(float)
        rows.append({
            "story_id": sid,
            "family": m["family"],
            "variant": "score_subj_z",
            "group": "q3_e247_only_vs_e256_only",
            "n_group": int(q3_e247_only.sum()),
            "n_neutral": int(q3_e256_only.sum()),
            "mean_group": float(x[q3_e247_only].mean()) if int(q3_e247_only.sum()) else np.nan,
            "mean_neutral": float(x[q3_e256_only].mean()) if int(q3_e256_only.sum()) else np.nan,
            "cohen_d_group_vs_neutral": cohen_d(x[q3_e247_only], x[q3_e256_only]),
        })
    return pd.DataFrame(rows).sort_values(["group", "cohen_d_group_vs_neutral"], ascending=[True, False]).reset_index(drop=True)


def train_test_shift(story_df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    rows = []
    tr = story_df["split"].eq("train")
    te = story_df["split"].eq("test")
    for _, m in meta.iterrows():
        sid = m["story_id"]
        for variant in [sid, f"{sid}_subj_z"]:
            rows.append({
                "story_id": sid,
                "family": m["family"],
                "variant": variant.replace(sid, "score"),
                "train_mean": float(story_df.loc[tr, variant].mean()),
                "test_mean": float(story_df.loc[te, variant].mean()),
                "abs_train_test_gap": abs(float(story_df.loc[te, variant].mean() - story_df.loc[tr, variant].mean())),
                "test_std": float(story_df.loc[te, variant].std(ddof=0)),
            })
    return pd.DataFrame(rows)


def latent_probe(story_df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    train = story_df[story_df["split"].eq("train")].reset_index(drop=True).copy()
    story_cols = [f"{sid}_subj_z" for sid in meta["story_id"] if f"{sid}_subj_z" in train.columns]
    x = train[story_cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    scaler = StandardScaler()
    xz = scaler.fit_transform(x)
    n_comp = min(8, xz.shape[1], xz.shape[0] - 1)
    pca = PCA(n_components=n_comp, random_state=20260531)
    z = pca.fit_transform(xz)
    groups = train["dateblock_group"].astype(str).to_numpy()
    rows = []
    eig = pca.explained_variance_ratio_
    anisotropy = float(eig[0] / max(eig.mean(), 1.0e-12)) if len(eig) else 0.0
    for target in TARGETS:
        y = train[target].astype(int).to_numpy()
        base = make_design(train, None, include_subject=True)
        latent = pd.concat([base.reset_index(drop=True), pd.DataFrame(z, columns=[f"story_pc{i+1}" for i in range(n_comp)])], axis=1)
        pred_base = predict_cv(base, y, groups)
        pred_lat = predict_cv(latent, y, groups)
        loss_base = float(log_loss(y, pred_base, labels=[0, 1]))
        loss_lat = float(log_loss(y, pred_lat, labels=[0, 1]))
        rows.append({
            "latent": "story_subj_z_pca",
            "target": target,
            "n_components": n_comp,
            "pc1_var": float(eig[0]) if len(eig) else 0.0,
            "pc8_cum_var": float(eig.sum()) if len(eig) else 0.0,
            "anisotropy_pc1_over_mean": anisotropy,
            "loss_base": loss_base,
            "loss_latent": loss_lat,
            "delta_logloss": loss_lat - loss_base,
        })
    return pd.DataFrame(rows).sort_values("delta_logloss").reset_index(drop=True)


def summarize_hypotheses(meta: pd.DataFrame, labels: pd.DataFrame, cv: pd.DataFrame, move: pd.DataFrame, shift: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, m in meta.iterrows():
        sid = m["story_id"]
        lab = labels[(labels["story_id"].eq(sid)) & (labels["variant"].eq("score_subj_z"))]
        cv_date = cv[(cv["story_id"].eq(sid)) & (cv["split"].eq("dateblock5"))]
        cv_subj = cv[(cv["story_id"].eq(sid)) & (cv["split"].eq("subject5"))]
        mv = move[(move["story_id"].eq(sid)) & (move["variant"].eq("score_subj_z"))]
        sh = shift[(shift["story_id"].eq(sid)) & (shift["variant"].eq("score_subj_z"))]
        best_label = lab.sort_values("abs_effect", ascending=False).head(1)
        best_cv = cv_date.sort_values("delta_logloss").head(1)
        e247_d = mv[mv["group"].eq("q3_e247_only_vs_neutral")]["cohen_d_group_vs_neutral"]
        e256_d = mv[mv["group"].eq("q3_e256_only_vs_neutral")]["cohen_d_group_vs_neutral"]
        e247_vs_e256 = mv[mv["group"].eq("q3_e247_only_vs_e256_only")]["cohen_d_group_vs_neutral"]
        e267_d = mv[mv["group"].eq("e267_any_moved_vs_neutral")]["cohen_d_group_vs_neutral"]
        best_cv_delta = float(best_cv["delta_logloss"].iloc[0]) if not best_cv.empty else 0.0
        best_label_abs = float(best_label["abs_effect"].iloc[0]) if not best_label.empty else 0.0
        shift_gap = float(sh["abs_train_test_gap"].max()) if not sh.empty else 0.0
        public_align = (
            abs(float(e247_d.iloc[0])) if len(e247_d) else 0.0
        ) + (
            abs(float(e247_vs_e256.iloc[0])) if len(e247_vs_e256) else 0.0
        ) - 0.5 * (
            abs(float(e267_d.iloc[0])) if len(e267_d) else 0.0
        ) - 0.25 * shift_gap
        story_real = (best_label_abs >= 0.12) or (best_cv_delta <= -0.001)
        action_safe = public_align > 0.35 and shift_gap < 0.55
        if story_real and action_safe:
            verdict = "promising_for_direct_e247_gate"
        elif story_real:
            verdict = "real_but_action_unproven"
        elif public_align > 0.5:
            verdict = "public_anchor_diagnostic_only"
        else:
            verdict = "weak_or_confounded"
        rows.append({
            "story_id": sid,
            "family": m["family"],
            "human_story": m["human_story"],
            "best_label_target": best_label["target"].iloc[0] if not best_label.empty else "",
            "best_label_abs_effect": best_label_abs,
            "best_dateblock_target": best_cv["target"].iloc[0] if not best_cv.empty else "",
            "best_dateblock_delta": best_cv_delta,
            "subject_split_best_delta": float(cv_subj["delta_logloss"].min()) if not cv_subj.empty else 0.0,
            "e247_only_d": float(e247_d.iloc[0]) if len(e247_d) else 0.0,
            "e256_only_d": float(e256_d.iloc[0]) if len(e256_d) else 0.0,
            "e247_vs_e256_d": float(e247_vs_e256.iloc[0]) if len(e247_vs_e256) else 0.0,
            "e267_moved_d": float(e267_d.iloc[0]) if len(e267_d) else 0.0,
            "train_test_gap": shift_gap,
            "public_align_score": public_align,
            "verdict": verdict,
        })
    return pd.DataFrame(rows).sort_values(
        ["verdict", "public_align_score", "best_label_abs_effect"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def write_report(meta: pd.DataFrame, hyp: pd.DataFrame, labels: pd.DataFrame, cv: pd.DataFrame, move: pd.DataFrame, latent: pd.DataFrame) -> None:
    top_label = labels.sort_values("abs_effect", ascending=False)
    top_cv = cv.sort_values("delta_logloss")
    e247_only = move[(move["group"].eq("q3_e247_only_vs_neutral")) & (move["variant"].eq("score_subj_z"))].sort_values("cohen_d_group_vs_neutral", ascending=False)
    e267_moved = move[(move["group"].eq("e267_any_moved_vs_neutral")) & (move["variant"].eq("score_subj_z"))].sort_values("cohen_d_group_vs_neutral", ascending=False)
    promising = hyp[hyp["verdict"].eq("promising_for_direct_e247_gate")]
    real = hyp[hyp["verdict"].eq("real_but_action_unproven")]
    diagnostic = hyp[hyp["verdict"].eq("public_anchor_diagnostic_only")]

    lines = [
        "# E268 Human/Social Story Atlas",
        "",
        "## Question",
        "",
        "After `submission_e267_humansocial_tail_balanced_2936100f.csv` lost publicly, does the human/social worldview die, or did it fail because it was translated through the wrong E224/E154 rollback action?",
        "",
        "This experiment treats each story as a falsifiable hidden-state hypothesis and tests it four ways: train label lift, date-block/subject CV, train/test shift, and alignment with E247/E256/E267 public-anchor movements.",
        "",
        "## Inventory",
        "",
        f"- explicit human/social stories: `{len(meta)}`",
        f"- train rows: `{int((pd.read_parquet(HUMAN_PATH)['split'] == 'train').sum())}`",
        f"- test rows: `{int((pd.read_parquet(HUMAN_PATH)['split'] == 'test').sum())}`",
        "",
        "## Best Story Verdicts",
        "",
        md_table(hyp, n=25),
        "",
        "## Strongest Label Lifts",
        "",
        md_table(top_label[["story_id", "variant", "family", "target", "high_minus_low", "abs_effect", "corr"]], n=30),
        "",
        "## Best Blocked CV Deltas",
        "",
        md_table(top_cv[["story_id", "family", "split", "target", "delta_logloss", "loss_base", "loss_story"]], n=30, floatfmt=".9f"),
        "",
        "## E247-Only Q3 Movement Alignment",
        "",
        "Positive `cohen_d` means the story is higher on the E247-only Q3 rows than on neutral rows. This is a public-anchor diagnostic, not label truth.",
        "",
        md_table(e247_only[["story_id", "family", "n_group", "n_neutral", "mean_group", "mean_neutral", "cohen_d_group_vs_neutral"]], n=25),
        "",
        "## E267 Failed-Movement Exposure",
        "",
        "If a story is high here, the failed E267 action already leaned on it. That weakens direct reuse unless the next action is changed.",
        "",
        md_table(e267_moved[["story_id", "family", "n_group", "n_neutral", "mean_group", "mean_neutral", "cohen_d_group_vs_neutral"]], n=25),
        "",
        "## Story Latent Diagnostic",
        "",
        md_table(latent, n=10, floatfmt=".9f"),
        "",
        "## Read",
        "",
        f"- Promising direct E247 gates: `{len(promising)}`.",
        f"- Real but action-unproven stories: `{len(real)}`.",
        f"- Public-anchor diagnostics only: `{len(diagnostic)}`.",
        "",
        "If no story reaches the direct-gate bucket, the lesson is not that human/social context is useless. It means the current public-positive mechanism needs a new action target: it should predict which E247 Q3 rollback cells to keep or undo directly, not inherit the E224/E154 social rollback body used by E267.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n")


def main() -> None:
    df = load_human()
    specs = story_specs()
    story_df, meta = build_story_features(df, specs)
    labels = label_probe(story_df, meta)
    cv = cv_probe(story_df, meta)
    move = movement_alignment(story_df, meta)
    shift = train_test_shift(story_df, meta)
    latent = latent_probe(story_df, meta)
    hyp = summarize_hypotheses(meta, labels, cv, move, shift)

    story_df.to_parquet(STORY_OUT, index=False)
    meta.to_csv(HYP_OUT, index=False)
    labels.to_csv(LABEL_OUT, index=False)
    cv.to_csv(CV_OUT, index=False)
    move.to_csv(MOVE_OUT, index=False)
    latent.to_csv(LATENT_OUT, index=False)
    hyp.to_csv(OUT / "e268_human_social_story_verdicts.csv", index=False)
    write_report(meta, hyp, labels, cv, move, latent)

    print(f"wrote {REPORT_OUT}")
    print(hyp.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
