#!/usr/bin/env python3
"""E270: payday / cash-flow cycle story atlas.

The user hypothesis is that a human calendar event such as payday may change
sleep behavior. We do not assume one official payday. Instead we test multiple
monthly anchors (10/15/20/25/end-of-month/month-start) and ask whether finance,
shopping, social, mobility, and late-phone states interact with those anchors.

This is a story atlas, not a model sweep:
- label lift by target;
- date-block and subject-block CV deltas;
- train/test shift;
- alignment with the E247/E256 Q3 public boundary and the E267 failed action.
"""

from __future__ import annotations

from dataclasses import dataclass
from calendar import monthrange
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

HUMAN_PATH = OUT / "e262_human_social_day_features.parquet"
E247 = OUT / "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256 = OUT / "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"
E267 = OUT / "submission_e267_humansocial_tail_balanced_2936100f.csv"
E224 = OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"

FEATURE_OUT = OUT / "e270_payday_cashflow_story_features.parquet"
HYP_OUT = OUT / "e270_payday_cashflow_story_verdicts.csv"
LABEL_OUT = OUT / "e270_payday_cashflow_label_probe.csv"
CV_OUT = OUT / "e270_payday_cashflow_cv.csv"
MOVE_OUT = OUT / "e270_payday_cashflow_movement_alignment.csv"
REPORT_OUT = OUT / "e270_payday_cashflow_story_atlas_report.md"


@dataclass(frozen=True)
class StorySpec:
    story_id: str
    anchor: str
    phase: str
    family: str
    human_story: str
    terms: tuple[tuple[str, float], ...]


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
    for _, idx in df.groupby("subject_id").groups.items():
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


def load_human() -> pd.DataFrame:
    df = pd.read_parquet(HUMAN_PATH).copy()
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = pd.to_datetime(df[col])
    df = df.sort_values(KEYS).reset_index(drop=True)
    df["lifelog_dom"] = df["lifelog_date"].dt.day.astype(int)
    df["lifelog_month_days"] = [monthrange(d.year, d.month)[1] for d in df["lifelog_date"]]
    df["days_to_eom"] = df["lifelog_month_days"] - df["lifelog_dom"]
    df["subject_order"] = df.groupby("subject_id").cumcount().astype(int)
    df["dateblock_group"] = df["subject_id"].astype(str) + "_b" + (df["subject_order"] // 7).astype(str)
    for col in ["sleep_date", "lifelog_date"]:
        df[col] = df[col].dt.strftime("%Y-%m-%d")
    return df


def anchor_day(df: pd.DataFrame, anchor: str) -> pd.Series:
    if anchor == "eom":
        return df["lifelog_month_days"]
    if anchor == "month_start":
        return pd.Series(1, index=df.index)
    return pd.Series(int(anchor), index=df.index)


def circular_dist_to_anchor(dom: pd.Series, anchor: pd.Series, month_days: pd.Series) -> pd.Series:
    forward = (dom - anchor) % month_days
    backward = (anchor - dom) % month_days
    return pd.concat([forward, backward], axis=1).min(axis=1).astype(float)


def phase_score(df: pd.DataFrame, anchor: str, phase: str) -> pd.Series:
    dom = df["lifelog_dom"].astype(int)
    mdays = df["lifelog_month_days"].astype(int)
    ad = anchor_day(df, anchor).astype(int)
    delta_after = (dom - ad) % mdays
    delta_before = (ad - dom) % mdays
    if phase == "exact":
        raw = (dom == ad).astype(float)
    elif phase == "post3":
        raw = ((delta_after >= 0) & (delta_after <= 3)).astype(float)
    elif phase == "post7":
        raw = ((delta_after >= 0) & (delta_after <= 7)).astype(float)
    elif phase == "pre3":
        raw = ((delta_before >= 1) & (delta_before <= 3)).astype(float)
    elif phase == "pre7":
        raw = ((delta_before >= 1) & (delta_before <= 7)).astype(float)
    elif phase == "near3":
        raw = (circular_dist_to_anchor(dom, ad, mdays) <= 3).astype(float)
    elif phase == "near7":
        raw = (circular_dist_to_anchor(dom, ad, mdays) <= 7).astype(float)
    else:
        raise ValueError(phase)
    return raw.astype(float)


def build_base_scores(df: pd.DataFrame) -> pd.DataFrame:
    train_mask = df["split"].eq("train")
    out = pd.DataFrame(index=df.index)

    def z(col: str) -> pd.Series:
        if col not in df.columns:
            return pd.Series(0.0, index=df.index)
        return robust_z_from_train(df[col], train_mask)

    out["finance_day"] = z("usage_day_finance_time")
    out["finance_late"] = z("usage_late_finance_time") + z("usage_presleep_finance_time") + z("usage_deepnight_finance_time")
    out["shopping_day"] = z("usage_day_shopping_time")
    out["shopping_late"] = z("usage_late_shopping_time") + z("usage_presleep_shopping_time") + z("usage_deepnight_shopping_time")
    out["money_app_total"] = out["finance_day"] + out["shopping_day"]
    out["money_late_total"] = out["finance_late"] + out["shopping_late"]
    out["social_spend_outing"] = (
        z("usage_presleep_social_msg_time")
        + z("usage_late_social_msg_time")
        + z("usage_presleep_media_time")
        + z("usage_late_media_time")
        + z("ambience_inside_public_evening")
        + z("gps_speed_mean_evening")
        + z("gps_speed_mean_late")
    )
    out["quiet_budget_home"] = (
        z("charge_m_charging_mean_presleep")
        - z("gps_speed_mean_late")
        - z("usage_late_media_time")
        - z("usage_late_social_msg_time")
        - z("screen_m_screen_use_mean_late")
    )
    out["bedtime_money_rumination"] = (
        z("usage_late_finance_time")
        + z("usage_late_shopping_time")
        + z("usage_late_search_browser_time")
        + z("screen_m_screen_use_mean_late")
    )
    out["nextday_finance_check"] = z("usage_morning_finance_time") + z("usage_morning_shopping_time")
    for col in list(out.columns):
        out[col] = robust_z_from_train(out[col], train_mask)
    return out


def story_specs() -> list[StorySpec]:
    anchors = ["10", "15", "20", "25", "eom", "month_start"]
    specs: list[StorySpec] = []
    for anchor in anchors:
        specs.extend([
            StorySpec(f"pay{anchor}_post3_spend_outing", anchor, "post3", "post_pay_spend", f"First 3 days after anchor {anchor}: spending/social outing state.", (("phase", 1.0), ("money_app_total", 0.8), ("social_spend_outing", 0.8))),
            StorySpec(f"pay{anchor}_post7_spend_outing", anchor, "post7", "post_pay_spend", f"First week after anchor {anchor}: broader spending/social state.", (("phase", 1.0), ("money_app_total", 0.7), ("shopping_day", 0.6), ("social_spend_outing", 0.6))),
            StorySpec(f"pay{anchor}_pre3_cash_stress", anchor, "pre3", "pre_pay_stress", f"Last 3 days before anchor {anchor}: finance/checking stress.", (("phase", 1.0), ("finance_late", 0.9), ("bedtime_money_rumination", 0.8), ("shopping_day", -0.4))),
            StorySpec(f"pay{anchor}_pre7_budget_squeeze", anchor, "pre7", "pre_pay_stress", f"Week before anchor {anchor}: budget squeeze and late money rumination.", (("phase", 1.0), ("finance_day", 0.6), ("bedtime_money_rumination", 0.8), ("quiet_budget_home", 0.4))),
            StorySpec(f"pay{anchor}_near3_money_rumination", anchor, "near3", "cashflow_transition", f"Near anchor {anchor}: finance/shopping/search rumination.", (("phase", 1.0), ("bedtime_money_rumination", 1.0), ("money_late_total", 0.6))),
            StorySpec(f"pay{anchor}_near7_calendar_only", anchor, "near7", "calendar_only", f"Near anchor {anchor}: pure monthly-cycle calendar state.", (("phase", 1.0),)),
            StorySpec(f"pay{anchor}_post3_relief_home", anchor, "post3", "post_pay_relief", f"After anchor {anchor}: money available but quiet home/charging routine.", (("phase", 1.0), ("quiet_budget_home", 0.8), ("finance_day", 0.4), ("shopping_late", -0.4))),
            StorySpec(f"pay{anchor}_post3_late_shopping", anchor, "post3", "post_pay_spend", f"After anchor {anchor}: late shopping or finance phone use.", (("phase", 1.0), ("shopping_late", 1.0), ("finance_late", 0.7), ("screen_m_screen_use_mean_late", 0.4))),
        ])
    specs.extend([
        StorySpec("eom_bill_anxiety", "eom", "pre7", "bill_cycle", "End-of-month bill/card anxiety: late finance/search near month end.", (("phase", 1.0), ("finance_late", 1.0), ("bedtime_money_rumination", 1.0))),
        StorySpec("monthstart_reset_relief", "month_start", "post3", "bill_cycle", "Month-start reset: quiet home after monthly cycle rolls over.", (("phase", 1.0), ("quiet_budget_home", 1.0), ("money_late_total", -0.3))),
        StorySpec("monthstart_spending_reset", "month_start", "post7", "bill_cycle", "Month-start spending reset: finance/shopping/social usage after new month starts.", (("phase", 1.0), ("money_app_total", 0.8), ("social_spend_outing", 0.5))),
    ])
    return specs


def build_story_features(df: pd.DataFrame, specs: list[StorySpec]) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_mask = df["split"].eq("train")
    base = build_base_scores(df)
    out = df[KEYS + ["split", "weekday", "is_weekend", "lifelog_dom", "subject_order", "dateblock_group"] + TARGETS].copy()
    parts = []
    meta_rows = []
    for spec in specs:
        phase = phase_score(df, spec.anchor, spec.phase)
        raw = pd.Series(0.0, index=df.index, dtype=float)
        for name, weight in spec.terms:
            if name == "phase":
                raw = raw + weight * phase
            elif name in base.columns:
                raw = raw + weight * base[name] * phase
            elif name in df.columns:
                raw = raw + weight * robust_z_from_train(df[name], train_mask) * phase
        score = robust_z_from_train(raw, train_mask)
        subj_z = subject_z_from_train(score, df, train_mask)
        parts.append(pd.DataFrame({
            spec.story_id: score,
            f"{spec.story_id}_subj_z": subj_z,
            f"{spec.story_id}_active": phase.astype(float),
        }))
        meta_rows.append({
            "story_id": spec.story_id,
            "anchor": spec.anchor,
            "phase": spec.phase,
            "family": spec.family,
            "human_story": spec.human_story,
            "active_train_n": int((phase[df["split"].eq("train")] > 0).sum()),
            "active_test_n": int((phase[df["split"].eq("test")] > 0).sum()),
        })
    out = pd.concat([out, *parts], axis=1)
    return out, pd.DataFrame(meta_rows)


def label_probe(story_df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    train = story_df[story_df["split"].eq("train")].copy()
    rows = []
    for _, m in meta.iterrows():
        sid = m["story_id"]
        for variant in [sid, f"{sid}_subj_z", f"{sid}_active"]:
            x = train[variant].astype(float)
            if x.nunique(dropna=True) < 2:
                continue
            if variant.endswith("_active"):
                high = x > 0
                low = x <= 0
            else:
                q25, q75 = x.quantile([0.25, 0.75])
                high = x >= q75
                low = x <= q25
            if int(high.sum()) < 10 or int(low.sum()) < 20:
                continue
            for target in TARGETS:
                y = train[target].astype(float)
                effect = float(y[high].mean() - y[low].mean())
                corr = float(np.corrcoef(x, y)[0, 1]) if x.std(ddof=0) > 1.0e-9 else 0.0
                rows.append({
                    "story_id": sid,
                    "anchor": m["anchor"],
                    "phase": m["phase"],
                    "family": m["family"],
                    "variant": variant.replace(sid, "score"),
                    "target": target,
                    "high_minus_low": effect,
                    "abs_effect": abs(effect),
                    "corr": corr,
                    "high_n": int(high.sum()),
                })
    return pd.DataFrame(rows).sort_values(["abs_effect", "story_id"], ascending=[False, True]).reset_index(drop=True)


def make_design(df: pd.DataFrame, story_id: str | None, include_subject: bool) -> pd.DataFrame:
    x = pd.DataFrame(index=df.index)
    x["weekday_sin"] = np.sin(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    x["weekday_cos"] = np.cos(2.0 * np.pi * df["weekday"].astype(float) / 7.0)
    x["is_weekend"] = df["is_weekend"].astype(float)
    x["subject_order"] = df["subject_order"].astype(float) / max(float(df["subject_order"].max()), 1.0)
    if include_subject:
        x = pd.concat([x, pd.get_dummies(df["subject_id"], prefix="subj", dtype=float)], axis=1)
    if story_id is not None:
        for suffix in ["", "_subj_z", "_active"]:
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
        model = make_pipeline(StandardScaler(with_mean=False), LogisticRegression(C=0.35, max_iter=1000, solver="lbfgs"))
        model.fit(x.iloc[tr_idx], y_tr)
        pred[va_idx] = model.predict_proba(x.iloc[va_idx])[:, 1]
    return clip_prob(pred)


def cv_probe(story_df: pd.DataFrame, meta: pd.DataFrame) -> pd.DataFrame:
    train = story_df[story_df["split"].eq("train")].reset_index(drop=True)
    split_specs = [
        ("dateblock5", train["dateblock_group"].astype(str).to_numpy(), True),
        ("subject5", train["subject_id"].astype(str).to_numpy(), False),
    ]
    rows = []
    base_cache: dict[tuple[str, str], float] = {}
    for split_name, groups, include_subject in split_specs:
        xb = make_design(train, None, include_subject)
        for target in TARGETS:
            y = train[target].astype(int).to_numpy()
            pb = predict_cv(xb, y, groups)
            base_cache[(split_name, target)] = float(log_loss(y, pb, labels=[0, 1]))
        for _, m in meta.iterrows():
            sid = m["story_id"]
            xs = make_design(train, sid, include_subject)
            for target in TARGETS:
                y = train[target].astype(int).to_numpy()
                ps = predict_cv(xs, y, groups)
                loss_story = float(log_loss(y, ps, labels=[0, 1]))
                loss_base = base_cache[(split_name, target)]
                rows.append({
                    "story_id": sid,
                    "anchor": m["anchor"],
                    "phase": m["phase"],
                    "family": m["family"],
                    "split": split_name,
                    "target": target,
                    "loss_base": loss_base,
                    "loss_story": loss_story,
                    "delta_logloss": loss_story - loss_base,
                })
    return pd.DataFrame(rows).sort_values(["delta_logloss", "story_id"]).reset_index(drop=True)


def load_sub(path: Path) -> pd.DataFrame:
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
    test = story_df[story_df["split"].eq("test")].sort_values(KEYS).reset_index(drop=True)
    e247 = load_sub(E247)
    e256 = load_sub(E256)
    e224 = load_sub(E224)
    e267 = load_sub(E267)
    for name, sub in [("e247", e247), ("e256", e256), ("e224", e224), ("e267", e267)]:
        if not test[KEYS].equals(sub[KEYS]):
            raise RuntimeError(f"{name} key order mismatch")
    d247 = logit(e247["Q3"].to_numpy()) - logit(e224["Q3"].to_numpy())
    d256 = logit(e256["Q3"].to_numpy()) - logit(e224["Q3"].to_numpy())
    q3_e247 = np.abs(d247) > 1.0e-10
    q3_e256 = np.abs(d256) > 1.0e-10
    q3_e247_only = pd.Series(q3_e247 & ~q3_e256, index=test.index)
    q3_e256_only = pd.Series(q3_e256 & ~q3_e247, index=test.index)
    q3_common = pd.Series(q3_e247 & q3_e256, index=test.index)
    e267_any = pd.Series(False, index=test.index)
    for target in TARGETS:
        e267_any |= pd.Series(np.abs(logit(e267[target].to_numpy()) - logit(e247[target].to_numpy())) > 1.0e-10, index=test.index)
    neutral = ~(q3_e247_only | q3_e256_only | q3_common | e267_any)
    groups = {
        "q3_e247_only_vs_neutral": q3_e247_only,
        "q3_e256_only_vs_neutral": q3_e256_only,
        "q3_common_vs_neutral": q3_common,
        "e267_any_moved_vs_neutral": e267_any,
    }
    rows = []
    for _, m in meta.iterrows():
        sid = m["story_id"]
        for variant in [sid, f"{sid}_subj_z", f"{sid}_active"]:
            x = test[variant].astype(float)
            for group_name, mask in groups.items():
                rows.append({
                    "story_id": sid,
                    "anchor": m["anchor"],
                    "phase": m["phase"],
                    "family": m["family"],
                    "variant": variant.replace(sid, "score"),
                    "group": group_name,
                    "n_group": int(mask.sum()),
                    "n_neutral": int(neutral.sum()),
                    "mean_group": float(x[mask].mean()) if int(mask.sum()) else np.nan,
                    "mean_neutral": float(x[neutral].mean()) if int(neutral.sum()) else np.nan,
                    "cohen_d_group_vs_neutral": cohen_d(x[mask], x[neutral]),
                })
        x = test[f"{sid}_subj_z"].astype(float)
        rows.append({
            "story_id": sid,
            "anchor": m["anchor"],
            "phase": m["phase"],
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
    tr = story_df["split"].eq("train")
    te = story_df["split"].eq("test")
    rows = []
    for _, m in meta.iterrows():
        sid = m["story_id"]
        for variant in [sid, f"{sid}_subj_z", f"{sid}_active"]:
            rows.append({
                "story_id": sid,
                "variant": variant.replace(sid, "score"),
                "gap": abs(float(story_df.loc[te, variant].mean() - story_df.loc[tr, variant].mean())),
            })
    return pd.DataFrame(rows)


def summarize(meta: pd.DataFrame, labels: pd.DataFrame, cv: pd.DataFrame, move: pd.DataFrame, shift: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, m in meta.iterrows():
        sid = m["story_id"]
        lab = labels[(labels["story_id"].eq(sid)) & (labels["variant"].eq("score_subj_z"))]
        cvd = cv[(cv["story_id"].eq(sid)) & (cv["split"].eq("dateblock5"))]
        cvs = cv[(cv["story_id"].eq(sid)) & (cv["split"].eq("subject5"))]
        mv = move[(move["story_id"].eq(sid)) & (move["variant"].eq("score_subj_z"))]
        sh = shift[(shift["story_id"].eq(sid)) & (shift["variant"].eq("score_subj_z"))]
        best_lab = lab.sort_values("abs_effect", ascending=False).head(1)
        best_cvd = cvd.sort_values("delta_logloss").head(1)
        e247 = mv[mv["group"].eq("q3_e247_only_vs_neutral")]["cohen_d_group_vs_neutral"]
        e256 = mv[mv["group"].eq("q3_e256_only_vs_neutral")]["cohen_d_group_vs_neutral"]
        sep = mv[mv["group"].eq("q3_e247_only_vs_e256_only")]["cohen_d_group_vs_neutral"]
        e267 = mv[mv["group"].eq("e267_any_moved_vs_neutral")]["cohen_d_group_vs_neutral"]
        gap = float(sh["gap"].max()) if not sh.empty else 0.0
        label_abs = float(best_lab["abs_effect"].iloc[0]) if not best_lab.empty else 0.0
        date_delta = float(best_cvd["delta_logloss"].iloc[0]) if not best_cvd.empty else 0.0
        public_align = (
            abs(float(e247.iloc[0])) if len(e247) else 0.0
        ) + (
            abs(float(sep.iloc[0])) if len(sep) else 0.0
        ) - 0.4 * (
            abs(float(e267.iloc[0])) if len(e267) else 0.0
        ) - 0.25 * gap
        story_real = label_abs >= 0.12 or date_delta <= -0.002
        if story_real and public_align >= 0.6 and gap <= 0.45:
            verdict = "promising_cashflow_gate"
        elif story_real:
            verdict = "real_but_not_public_action_safe"
        elif public_align >= 0.8:
            verdict = "public_boundary_diagnostic_only"
        else:
            verdict = "weak_or_confounded"
        rows.append({
            "story_id": sid,
            "anchor": m["anchor"],
            "phase": m["phase"],
            "family": m["family"],
            "active_train_n": int(m["active_train_n"]),
            "active_test_n": int(m["active_test_n"]),
            "best_label_target": best_lab["target"].iloc[0] if not best_lab.empty else "",
            "best_label_abs_effect": label_abs,
            "best_dateblock_target": best_cvd["target"].iloc[0] if not best_cvd.empty else "",
            "best_dateblock_delta": date_delta,
            "subject_best_delta": float(cvs["delta_logloss"].min()) if not cvs.empty else 0.0,
            "e247_only_d": float(e247.iloc[0]) if len(e247) else 0.0,
            "e256_only_d": float(e256.iloc[0]) if len(e256) else 0.0,
            "e247_vs_e256_d": float(sep.iloc[0]) if len(sep) else 0.0,
            "e267_moved_d": float(e267.iloc[0]) if len(e267) else 0.0,
            "train_test_gap": gap,
            "public_align_score": public_align,
            "verdict": verdict,
            "human_story": m["human_story"],
        })
    order = {"promising_cashflow_gate": 0, "public_boundary_diagnostic_only": 1, "real_but_not_public_action_safe": 2, "weak_or_confounded": 3}
    out = pd.DataFrame(rows)
    out["_order"] = out["verdict"].map(order).fillna(9)
    return out.sort_values(["_order", "public_align_score", "best_label_abs_effect"], ascending=[True, False, False]).drop(columns="_order").reset_index(drop=True)


def write_report(hyp: pd.DataFrame, labels: pd.DataFrame, cv: pd.DataFrame, move: pd.DataFrame) -> None:
    top_label = labels.sort_values("abs_effect", ascending=False)
    top_cv = cv.sort_values("delta_logloss")
    e247 = move[(move["group"].eq("q3_e247_only_vs_neutral")) & (move["variant"].eq("score_subj_z"))].sort_values("cohen_d_group_vs_neutral", ascending=False)
    sep = move[(move["group"].eq("q3_e247_only_vs_e256_only")) & (move["variant"].eq("score_subj_z"))].sort_values("cohen_d_group_vs_neutral", ascending=False)
    lines = [
        "# E270 Payday / Cash-Flow Story Atlas",
        "",
        "## Question",
        "",
        "Could monthly cash-flow events such as payday, card bills, or budget squeeze create sleep-relevant hidden states?",
        "",
        "No single payday is assumed. Anchors tested: `10`, `15`, `20`, `25`, `eom`, and `month_start`, with post/pre/near windows and finance-shopping-social interactions.",
        "",
        "## Best Verdicts",
        "",
        md_table(hyp, n=30),
        "",
        "## Strongest Label Lifts",
        "",
        md_table(top_label[["story_id", "anchor", "phase", "family", "variant", "target", "high_minus_low", "abs_effect", "high_n"]], n=30),
        "",
        "## Best Blocked CV Deltas",
        "",
        md_table(top_cv[["story_id", "anchor", "phase", "family", "split", "target", "delta_logloss", "loss_base", "loss_story"]], n=30, floatfmt=".9f"),
        "",
        "## E247-Only Q3 Alignment",
        "",
        md_table(e247[["story_id", "anchor", "phase", "family", "n_group", "mean_group", "mean_neutral", "cohen_d_group_vs_neutral"]], n=25),
        "",
        "## E247 vs E256 Separation",
        "",
        md_table(sep[["story_id", "anchor", "phase", "family", "mean_group", "mean_neutral", "cohen_d_group_vs_neutral"]], n=25),
        "",
        "## Read",
        "",
        f"- promising cashflow gates: `{int(hyp['verdict'].eq('promising_cashflow_gate').sum())}`",
        f"- public-boundary diagnostics only: `{int(hyp['verdict'].eq('public_boundary_diagnostic_only').sum())}`",
        f"- real but not action-safe: `{int(hyp['verdict'].eq('real_but_not_public_action_safe').sum())}`",
        "",
        "A useful result here would not prove a literal payday. It would indicate that monthly financial rhythm is a proxy for a human state: relief/spend/social outing, pre-pay stress, bill anxiety, or budget squeeze.",
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
    hyp = summarize(meta, labels, cv, move, shift)
    story_df.to_parquet(FEATURE_OUT, index=False)
    hyp.to_csv(HYP_OUT, index=False)
    labels.to_csv(LABEL_OUT, index=False)
    cv.to_csv(CV_OUT, index=False)
    move.to_csv(MOVE_OUT, index=False)
    write_report(hyp, labels, cv, move)
    print(f"wrote {REPORT_OUT}")
    print(hyp.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
