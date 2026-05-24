#!/usr/bin/env python3
"""Phase 4: pure data-insight exploration.

This script deliberately avoids predictive modeling/submission generation. It builds
human-readable, data-grounded field notes about lifelog behavior, day archetypes,
Q2/Q3 event narratives, app semantics, and sensor coverage as behavior.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
AN = ROOT / "analysis"
FIG = AN / "figures"
AN.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

LABELS = ["Q1","Q2","Q3","S1","S2","S3","S4"]
KEYS = ["subject_id","lifelog_date"]

# Compact feature set for descriptive, not predictive, analysis.
CORE_FEATURES = [
    "steps_sum", "activity_sum_21_03", "app_total_time", "app_unique_count",
    "app_time_21_03", "app_social_time", "app_media_time", "app_browser_search_time", "app_game_time", "app_study_work_time",
    "screen_use_sum", "screen_use_00_06", "screen_use_18_24", "longest_screenoff_run_h", "longest_quiet_run_h",
    "gps_count", "gps_speed_mean", "gps_radius_proxy", "gps_unique_grid4", "wifi_unique_bssid", "ble_records", "ble_unique_addr",
    "hr_count", "hr_mean", "hr_std", "hr_mean_00_06", "hr_mean_21_03",
    "mlight_mean", "mlight_max", "wlight_mean", "wlight_max", "state_entropy", "night_state_entropy",
]

FAMILY_COLS = {
    "activity": ["steps_sum", "activity_sum_21_03"],
    "phone_screen": ["app_total_time", "app_unique_count", "screen_use_sum", "screen_use_00_06", "app_time_21_03"],
    "media_social": ["app_social_time", "app_media_time", "app_browser_search_time", "app_game_time", "app_study_work_time"],
    "rest_quiet": ["longest_screenoff_run_h", "longest_quiet_run_h"],
    "mobility_context": ["gps_radius_proxy", "gps_unique_grid4", "wifi_unique_bssid", "ble_unique_addr", "state_entropy"],
    "physiology_light": ["hr_mean", "hr_std", "hr_mean_00_06", "hr_mean_21_03", "mlight_mean", "wlight_mean"],
}

APP_CATS = {
    "messaging_social": ["카카오톡", "instagram", "facebook", "discord", "threads", "메시지", "라인", "twitter", "x"],
    "video_music_media": ["youtube", "melon", "music", "넷플릭스", "netflix", "티빙", "wavve", "spotify", "동영상"],
    "finance_auth": ["bank", "뱅크", "카드", "pay", "페이", "토스", "kb", "신한", "auth", "인증", "증권", "stock"],
    "mobility_car": ["tmap", "카카오t", "네이버지도", "지도", "kia", "auto", "버스", "지하철", "길찾기"],
    "shopping_delivery": ["shop", "쇼핑", "쿠팡", "배달", "mart", "몰", "store"],
    "work_study": ["teams", "slack", "notion", "docs", "pdf", "office", "word", "excel", "class", "study", "학교", "캘린더"],
    "game": ["game", "게임", "bricks", "goblin", "sort", "nonogram", "match"],
    "utility_home": ["one ui", "시스템", "설정", "카메라", "갤러리", "전화", "통화", "lg thinq", "weather", "날씨"],
    "religion_health": ["성경", "bible", "캐시워크", "health", "fit", "samsung health", "건강"],
}


def md_table(df: pd.DataFrame, max_rows: int | None = None, floatfmt: str = ".3f") -> str:
    d = df.copy()
    if max_rows is not None:
        d = d.head(max_rows)
    cols = list(d.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"]*len(cols)) + "|"]
    for _, row in d.iterrows():
        cells=[]
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and not pd.isna(v): cells.append(format(float(v), floatfmt))
            else: cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def load_daily() -> pd.DataFrame:
    tr = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    feat = pd.read_parquet(ROOT / "features" / "model_features_v0.parquet")
    feat["lifelog_date"] = pd.to_datetime(feat["lifelog_date"]).dt.date.astype(str)
    keep = KEYS + [c for c in CORE_FEATURES if c in feat.columns]
    df = tr.merge(feat[keep], on=KEYS, how="left")
    df["date"] = pd.to_datetime(df["lifelog_date"])
    df["dow"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.dayofweek >= 5
    # subject-normalized deviations for narrative comparisons
    for c in [c for c in CORE_FEATURES if c in df.columns]:
        g = df.groupby("subject_id")[c]
        mu = g.transform("mean")
        sd = g.transform("std").replace(0, np.nan)
        df[c + "__subj_z"] = (df[c] - mu) / sd
    return df


def parse_list_cell(x):
    if isinstance(x, np.ndarray): return x.tolist()
    if isinstance(x, list): return x
    return []


def load_app_daily() -> tuple[pd.DataFrame, pd.DataFrame]:
    p = ITEMS / "ch2025_mUsageStats.parquet"
    raw = pd.read_parquet(p)
    raw["date"] = pd.to_datetime(raw["timestamp"]).dt.date.astype(str)
    rows=[]
    for _, r in raw.iterrows():
        hour = pd.to_datetime(r["timestamp"]).hour
        for item in parse_list_cell(r["m_usage_stats"]):
            app = str(item.get("app_name", "")).strip().lower()
            total = float(item.get("total_time", 0) or 0) / 1000.0 / 60.0  # minutes-ish
            if not app or total <= 0: continue
            cat = "other"
            for k, kws in APP_CATS.items():
                if any(kw.lower() in app for kw in kws):
                    cat = k; break
            rows.append({"subject_id": r["subject_id"], "lifelog_date": r["date"], "hour": hour, "app": app, "minutes": total, "category": cat})
    app = pd.DataFrame(rows)
    if app.empty:
        return app, app
    daily_cat = app.groupby(["subject_id","lifelog_date","category"], as_index=False)["minutes"].sum()
    pivot = daily_cat.pivot_table(index=["subject_id","lifelog_date"], columns="category", values="minutes", fill_value=0).reset_index()
    return app, pivot


def subject_fieldnotes(df: pd.DataFrame, app_daily: pd.DataFrame):
    rows=[]
    for s, g in df.groupby("subject_id"):
        rec={"subject_id":s, "n_days":len(g)}
        for lab in LABELS: rec[f"{lab}_rate"] = g[lab].mean()
        for c in ["steps_sum","app_total_time","screen_use_sum","screen_use_00_06","longest_screenoff_run_h","gps_radius_proxy","gps_unique_grid4","state_entropy","hr_mean"]:
            if c in g: rec[c] = g[c].mean()
        # strongest Q2-vs-not-Q2 deviations by feature family
        q2hi, q2lo = g[g.Q2==1], g[g.Q2==0]
        diffs=[]
        for fam, cols in FAMILY_COLS.items():
            zcols=[c+"__subj_z" for c in cols if c+"__subj_z" in g]
            if len(q2hi) and len(q2lo) and zcols:
                diffs.append((fam, float(q2hi[zcols].mean().mean() - q2lo[zcols].mean().mean())))
        diffs=sorted(diffs, key=lambda x: abs(x[1]), reverse=True)
        rec["q2_top_deviation_family"] = diffs[0][0] if diffs else "NA"
        rec["q2_top_deviation_delta"] = diffs[0][1] if diffs else np.nan
        if not app_daily.empty:
            ag = app_daily[app_daily.subject_id==s]
            cat_cols=[c for c in ag.columns if c not in KEYS]
            means=ag[cat_cols].mean().sort_values(ascending=False) if len(ag) else pd.Series(dtype=float)
            rec["top_app_category_1"] = means.index[0] if len(means)>0 else "NA"
            rec["top_app_category_2"] = means.index[1] if len(means)>1 else "NA"
        rows.append(rec)
    out=pd.DataFrame(rows).sort_values("subject_id")
    out.to_csv(AN/"phase4_subject_fieldnotes.csv", index=False)

    # figure label rates
    rate_cols=[f"{l}_rate" for l in LABELS]
    fig, ax=plt.subplots(figsize=(9,4))
    mat=out.set_index("subject_id")[rate_cols]
    im=ax.imshow(mat.values, aspect="auto", vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(len(rate_cols)), [c.replace('_rate','') for c in rate_cols])
    ax.set_yticks(range(len(mat.index)), mat.index)
    ax.set_title("Phase4 A: subject label-rate field notes")
    fig.colorbar(im, ax=ax, fraction=.03)
    fig.tight_layout(); fig.savefig(FIG/"p4_A_subject_label_rates.png", dpi=180); plt.close(fig)

    lines=["# Phase 4A — Subject field notes\n",
           "목적: 예측 모델이 아니라, 각 subject가 어떤 생활/라벨 문법을 가진 사람처럼 보이는지 요약한다.\n",
           "## subject별 요약 테이블\n", md_table(out.round(3)), "\n"]
    lines.append("## 읽는 법\n")
    lines.append("- `q2_top_deviation_family`는 Q2=1인 날과 Q2=0인 날 사이에서 subject-normalized feature family 차이가 가장 큰 축이다.\n")
    lines.append("- 이 값은 인과/예측 성능이 아니라, 각 subject의 Q2가 어떤 생활 변화와 같이 나타나는지 보는 field note다.\n")
    (AN/"phase4_A_subject_fieldnotes.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def day_archetypes(df: pd.DataFrame):
    cols=[c for c in CORE_FEATURES if c in df.columns]
    X=df[cols].replace([np.inf,-np.inf], np.nan)
    X=X.fillna(X.median(numeric_only=True))
    Z=StandardScaler().fit_transform(X)
    km=KMeans(n_clusters=5, random_state=42, n_init=30)
    cl=km.fit_predict(Z)
    d=df[KEYS+LABELS+cols].copy(); d["archetype"]=cl
    d.to_csv(AN/"phase4_day_archetype_assignments.csv", index=False)
    rates=d.groupby("archetype")[LABELS].mean()
    sizes=d.groupby("archetype").size().rename("n_days")
    feat_means=d.groupby("archetype")[cols].mean()
    global_means=d[cols].mean()
    global_std=d[cols].std().replace(0,np.nan)
    zdesc=((feat_means-global_means)/global_std).T
    top_rows=[]
    for a in sorted(d.archetype.unique()):
        top=zdesc[a].dropna().sort_values(key=lambda s: s.abs(), ascending=False).head(8)
        for f,v in top.items(): top_rows.append({"archetype":a,"feature":f,"z_vs_global":v})
    topdf=pd.DataFrame(top_rows)
    summary=pd.concat([sizes, rates], axis=1).reset_index()
    summary.to_csv(AN/"phase4_day_archetype_summary.csv", index=False)
    topdf.to_csv(AN/"phase4_day_archetype_top_features.csv", index=False)

    fig, ax=plt.subplots(figsize=(8,4))
    im=ax.imshow(rates.values, aspect="auto", vmin=0, vmax=1, cmap="magma")
    ax.set_xticks(range(len(LABELS)), LABELS); ax.set_yticks(range(len(rates.index)), [f"A{a}" for a in rates.index])
    ax.set_title("Phase4 B: label rates by descriptive day archetype")
    fig.colorbar(im, ax=ax, fraction=.03); fig.tight_layout(); fig.savefig(FIG/"p4_B_archetype_label_rates.png", dpi=180); plt.close(fig)

    lines=["# Phase 4B — Descriptive day archetypes\n",
           "KMeans를 예측 모델로 쓰는 게 아니라, 일상 day를 몇 가지 **서술 가능한 생활 상태**로 묶어 라벨 분포를 본다.\n",
           "## archetype별 label rate\n", md_table(summary.round(3)), "\n",
           "## archetype을 가장 잘 설명하는 feature\n", md_table(topdf.round(3), max_rows=50), "\n"]
    (AN/"phase4_B_day_archetypes.md").write_text("\n".join(lines), encoding="utf-8")
    return d, summary, topdf


def q2_flip_narratives(df: pd.DataFrame):
    d=df.sort_values(["subject_id","date"]).copy()
    d["prev_Q2"]=d.groupby("subject_id")["Q2"].shift(1)
    d["next_Q2"]=d.groupby("subject_id")["Q2"].shift(-1)
    def cls(r):
        if pd.isna(r.prev_Q2): return "start"
        if r.prev_Q2==0 and r.Q2==1: return "Q2_0_to_1"
        if r.prev_Q2==1 and r.Q2==0: return "Q2_1_to_0"
        if r.Q2==1: return "stable_1"
        return "stable_0"
    d["q2_event"]=d.apply(cls, axis=1)
    zcols=[c for c in d.columns if c.endswith("__subj_z")]
    family_rows=[]
    for ev,g in d.groupby("q2_event"):
        rec={"q2_event":ev,"n_days":len(g),"Q1_rate":g.Q1.mean(),"Q2_rate":g.Q2.mean(),"Q3_rate":g.Q3.mean()}
        for fam, cols in FAMILY_COLS.items():
            zs=[c+"__subj_z" for c in cols if c+"__subj_z" in d]
            rec[fam+"_zmean"] = g[zs].mean().mean() if zs else np.nan
        family_rows.append(rec)
    famdf=pd.DataFrame(family_rows).sort_values("q2_event")
    famdf.to_csv(AN/"phase4_q2_event_family_profile.csv", index=False)

    # Top concrete example days for Q2 0->1 with multi-family deviations
    d["event_intensity"] = 0
    for fam, cols in FAMILY_COLS.items():
        zs=[c+"__subj_z" for c in cols if c+"__subj_z" in d]
        if zs: d["event_intensity"] += d[zs].abs().mean(axis=1).fillna(0)
    examples=d[d.q2_event.eq("Q2_0_to_1")].sort_values("event_intensity", ascending=False).head(20)
    ex_cols=KEYS+["Q1","Q2","Q3","S1","S2","S3","S4","event_intensity"] + [c for c in ["steps_sum","app_total_time","screen_use_00_06","longest_screenoff_run_h","gps_radius_proxy","wifi_unique_bssid","hr_mean"] if c in d]
    examples[ex_cols].to_csv(AN/"phase4_q2_flip_example_days.csv", index=False)

    fig, ax=plt.subplots(figsize=(8,4))
    plot=famdf.set_index("q2_event")[[c for c in famdf.columns if c.endswith("_zmean")]]
    im=ax.imshow(plot.values, aspect="auto", cmap="coolwarm", vmin=-0.5, vmax=0.5)
    ax.set_xticks(range(len(plot.columns)), [c.replace('_zmean','') for c in plot.columns], rotation=35, ha='right')
    ax.set_yticks(range(len(plot.index)), plot.index)
    ax.set_title("Phase4 C: Q2 event class family deviations")
    fig.colorbar(im, ax=ax, fraction=.03); fig.tight_layout(); fig.savefig(FIG/"p4_C_q2_event_family_deviation.png", dpi=180); plt.close(fig)

    lines=["# Phase 4C — Q2 flip narratives\n",
           "Q2를 예측하려는 게 아니라, Q2가 바뀌는 날이 어떤 생활 변화와 같이 나타나는지 본다.\n",
           "## Q2 event class별 family profile\n", md_table(famdf.round(3)), "\n",
           "## 강한 Q2 0→1 example days\n", md_table(examples[ex_cols].round(3), max_rows=20), "\n"]
    (AN/"phase4_C_q2_flip_narratives.md").write_text("\n".join(lines), encoding="utf-8")
    return famdf, examples


def app_lifestyle_semantics(df: pd.DataFrame, app: pd.DataFrame, app_daily: pd.DataFrame):
    if app.empty:
        return pd.DataFrame()
    # top apps per subject, anonymized enough as app names already in dataset; include top categories too.
    top_apps=app.groupby(["subject_id","app"], as_index=False)["minutes"].sum()
    top_apps=top_apps.sort_values(["subject_id","minutes"], ascending=[True,False])
    top_apps.groupby("subject_id").head(10).to_csv(AN/"phase4_top_apps_by_subject.csv", index=False)
    cat_mean=app_daily.groupby("subject_id").mean(numeric_only=True).reset_index()
    cat_mean.to_csv(AN/"phase4_app_category_minutes_by_subject.csv", index=False)
    merged=df[KEYS+LABELS].merge(app_daily, on=KEYS, how="left").fillna(0)
    cat_cols=[c for c in app_daily.columns if c not in KEYS]
    qrows=[]
    for cat in cat_cols:
        q2hi=merged[merged.Q2==1][cat].mean(); q2lo=merged[merged.Q2==0][cat].mean()
        q3hi=merged[merged.Q3==1][cat].mean(); q3lo=merged[merged.Q3==0][cat].mean()
        qrows.append({"category":cat,"Q2_1_minus_0_min":q2hi-q2lo,"Q3_1_minus_0_min":q3hi-q3lo,"overall_min":merged[cat].mean()})
    qdf=pd.DataFrame(qrows).sort_values("Q2_1_minus_0_min", key=lambda s: s.abs(), ascending=False)
    qdf.to_csv(AN/"phase4_app_category_q2q3_contrasts.csv", index=False)

    fig, ax=plt.subplots(figsize=(9,4))
    mat=cat_mean.set_index("subject_id")[[c for c in cat_mean.columns if c!='subject_id']]
    mat=mat.loc[:, mat.mean().sort_values(ascending=False).head(8).index]
    im=ax.imshow(np.log1p(mat.values), aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(mat.columns)), mat.columns, rotation=35, ha='right')
    ax.set_yticks(range(len(mat.index)), mat.index)
    ax.set_title("Phase4 D: app category fingerprints, log minutes")
    fig.colorbar(im, ax=ax, fraction=.03); fig.tight_layout(); fig.savefig(FIG/"p4_D_app_category_fingerprints.png", dpi=180); plt.close(fig)

    lines=["# Phase 4D — App/lifestyle semantics\n",
           "앱 사용은 예측 피처가 아니라 subject의 생활 문맥을 읽는 텍스트 단서처럼 본다.\n",
           "## subject별 app category 평균 minutes-ish\n", md_table(cat_mean.round(2)), "\n",
           "## Q2/Q3 label contrast가 큰 app category\n", md_table(qdf.round(2), max_rows=20), "\n",
           "## subject별 top apps\n", md_table(top_apps.groupby('subject_id').head(5).round(2), max_rows=80), "\n"]
    (AN/"phase4_D_app_lifestyle_semantics.md").write_text("\n".join(lines), encoding="utf-8")
    return qdf


def coverage_behavior(df: pd.DataFrame):
    cov_cols=[c for c in ["gps_count","app_records","screen_n","wifi_unique_bssid","ble_records","hr_count","mlight_n","wlight_n"] if c in df]
    rows=[]
    for c in cov_cols:
        vals=df[c].replace([np.inf,-np.inf],np.nan)
        lo=vals <= vals.quantile(0.2)
        hi=vals >= vals.quantile(0.8)
        rec={"coverage_feature":c,"low_n":int(lo.sum()),"high_n":int(hi.sum())}
        for lab in LABELS:
            rec[f"{lab}_low_minus_high"] = df.loc[lo,lab].mean() - df.loc[hi,lab].mean()
        rows.append(rec)
    out=pd.DataFrame(rows).sort_values("Q2_low_minus_high", key=lambda s:s.abs(), ascending=False)
    out.to_csv(AN/"phase4_coverage_label_contrasts.csv", index=False)

    subj=[]
    for s,g in df.groupby("subject_id"):
        rec={"subject_id":s}
        for c in cov_cols: rec[c]=g[c].mean()
        subj.append(rec)
    subj=pd.DataFrame(subj)
    subj.to_csv(AN/"phase4_coverage_by_subject.csv", index=False)

    fig, ax=plt.subplots(figsize=(8,4))
    plot=out.set_index("coverage_feature")[[f"{l}_low_minus_high" for l in LABELS]]
    im=ax.imshow(plot.values, aspect="auto", cmap="coolwarm", vmin=-0.25, vmax=0.25)
    ax.set_xticks(range(len(LABELS)), LABELS); ax.set_yticks(range(len(plot.index)), plot.index)
    ax.set_title("Phase4 E: low-vs-high coverage label contrast")
    fig.colorbar(im, ax=ax, fraction=.03); fig.tight_layout(); fig.savefig(FIG/"p4_E_coverage_label_contrast.png", dpi=180); plt.close(fig)

    lines=["# Phase 4E — Sensor coverage as behavior\n",
           "센서 coverage를 결측/품질 지표로만 보지 않고, 생활 패턴과 얽힌 관측 과정으로 본다.\n",
           "## low coverage vs high coverage label contrast\n", md_table(out.round(3)), "\n",
           "## subject별 coverage 평균\n", md_table(subj.round(2)), "\n"]
    (AN/"phase4_E_sensor_coverage_behavior.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def write_index_and_synthesis(field, arch, q2fam, appq, cov):
    # pull a few numbers for synthesis
    q1_range=(field.Q1_rate.min(), field.Q1_rate.max())
    q2fam2=q2fam.set_index("q2_event")
    synth=[]
    synth.append("# Phase 4 synthesis — 데이터에서 읽은 생활/라벨 인사이트\n")
    synth.append("이번 Phase 4는 모델을 만들지 않고, 데이터 자체에서 **사람별 생활 문맥과 라벨 사용 방식**을 읽는 데 집중했다.\n")
    synth.append("## 핵심 인사이트\n")
    synth.append(f"1. **Q1 personal anchor는 더 강해졌다.** subject별 Q1 rate가 {q1_range[0]:.3f}~{q1_range[1]:.3f}까지 벌어진다. 같은 라벨이라도 사람마다 기준점이 다르다.\n")
    if "Q2_0_to_1" in q2fam2.index:
        row=q2fam2.loc["Q2_0_to_1"]
        fams=[c for c in q2fam.columns if c.endswith("_zmean")]
        top=sorted([(c.replace('_zmean',''), row[c]) for c in fams], key=lambda x: abs(x[1]), reverse=True)[:3]
        synth.append("2. **Q2 0→1은 한 가지 센서가 아니라 multi-family event처럼 보인다.** Q2 0→1에서 큰 축: " + ", ".join([f"{a}({b:+.2f}z)" for a,b in top]) + ".\n")
    synth.append("3. **Day archetype은 라벨 해석의 배경이다.** 같은 Q2=1이라도 phone-heavy day, mobility/context-heavy day, rest/quiet day는 의미가 다를 수 있다.\n")
    if not appq.empty:
        topapp=appq.iloc[0]
        synth.append(f"4. **앱 사용은 행동 의미를 읽는 단서다.** Q2 contrast가 큰 app category 중 최상위는 `{topapp['category']}`이며, Q2=1과 Q2=0의 평균 차이는 {topapp['Q2_1_minus_0_min']:+.2f} minutes-ish다.\n")
    if not cov.empty:
        topcov=cov.iloc[0]
        synth.append(f"5. **coverage는 품질 문제가 아니라 관측 과정이다.** `{topcov['coverage_feature']}`의 low-vs-high contrast가 Q2에서 {topcov['Q2_low_minus_high']:+.3f}로 가장 크다.\n")
    synth.append("\n## 이제 해야 할 연구\n")
    synth.append("- subject별 fieldnote를 수작업으로 읽고 id03/id06/id08/id09/id10의 narrative를 고정한다.\n")
    synth.append("- Q2 0→1 example days를 timeline으로 시각화해서, phone/media event인지 rest/recovery event인지 분리한다.\n")
    synth.append("- 앱 category와 GPS/WiFi/BLE archetype을 합쳐 `day diary` 형태의 row-level 설명을 만든다.\n")
    synth.append("- 모델링은 아직 보류. 지금은 데이터 generating process를 더 잘 명명하는 단계다.\n")
    (AN/"phase4_synthesis_report.md").write_text("\n".join(synth), encoding="utf-8")

    idx="""# Phase 4 index — Insight-only exploration

이번 Phase 4는 예측 모델/OOF/submission이 아니라 데이터 자체에서 해석 가능한 인사이트를 찾는 라운드다.

## Reports

1. `analysis/phase4_A_subject_fieldnotes.md` — subject별 생활/라벨 field notes
2. `analysis/phase4_B_day_archetypes.md` — descriptive day archetypes
3. `analysis/phase4_C_q2_flip_narratives.md` — Q2 transition day narratives
4. `analysis/phase4_D_app_lifestyle_semantics.md` — app category / lifestyle semantics
5. `analysis/phase4_E_sensor_coverage_behavior.md` — sensor coverage as behavior
6. `analysis/phase4_synthesis_report.md` — 종합 인사이트

## Tables/Figures

- `analysis/phase4_*.csv`
- `analysis/figures/p4_*.png`

## Non-goals

- submission 생성 없음
- predictive model 생성 없음
- 기존 pipeline/feature 수정 없음
"""
    (AN/"phase4_index.md").write_text(idx, encoding="utf-8")


def main():
    df=load_daily()
    app, app_daily=load_app_daily()
    field=subject_fieldnotes(df, app_daily)
    arch_assign, arch_summary, arch_top=day_archetypes(df)
    q2fam, q2ex=q2_flip_narratives(df)
    appq=app_lifestyle_semantics(df, app, app_daily)
    cov=coverage_behavior(df)
    write_index_and_synthesis(field, arch_summary, q2fam, appq, cov)
    print("WROTE Phase 4 insight-only reports under", AN)

if __name__ == "__main__":
    main()
