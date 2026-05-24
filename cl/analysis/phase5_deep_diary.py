#!/usr/bin/env python3
"""Phase 5: deeper insight-only diary/taxonomy analysis.

No predictive modeling, no submission. This script turns daily lifelog rows into
human-readable day diaries and subject profile cards, then builds a descriptive
Q2-transition taxonomy.
"""
from __future__ import annotations

from pathlib import Path
import re
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
AN.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
KEYS = ["subject_id", "lifelog_date"]
LABELS = ["Q1","Q2","Q3","S1","S2","S3","S4"]

FEATURES = [
    "steps_sum", "activity_sum_21_03",
    "app_total_time", "app_unique_count", "app_time_21_03", "app_social_time", "app_media_time", "app_browser_search_time", "app_game_time",
    "screen_use_sum", "screen_use_00_06", "screen_use_18_24", "longest_screenoff_run_h", "longest_quiet_run_h",
    "gps_count", "gps_speed_mean", "gps_radius_proxy", "gps_unique_grid4", "wifi_unique_bssid", "ble_records", "ble_unique_addr",
    "hr_count", "hr_mean", "hr_std", "hr_mean_00_06", "hr_mean_21_03",
    "mlight_mean", "mlight_max", "wlight_mean", "wlight_max", "state_entropy", "night_state_entropy",
]
APP_CATS = {
    "messaging_social": ["카카오톡", "instagram", "facebook", "discord", "threads", "메시지", "라인", "twitter", "x"],
    "video_music_media": ["youtube", "melon", "music", "넷플릭스", "netflix", "티빙", "wavve", "spotify", "동영상"],
    "finance_auth": ["bank", "뱅크", "카드", "pay", "페이", "토스", "kb", "신한", "auth", "인증", "증권", "stock"],
    "mobility_car": ["tmap", "카카오t", "네이버지도", "지도", "kia", "auto", "버스", "지하철", "길찾기"],
    "shopping_delivery": ["shop", "쇼핑", "쿠팡", "배달", "mart", "몰", "store", "당근"],
    "work_study": ["teams", "slack", "notion", "docs", "pdf", "office", "word", "excel", "class", "study", "학교", "캘린더"],
    "game": ["game", "게임", "bricks", "goblin", "sort", "nonogram", "match", "클래시"],
    "utility_home": ["one ui", "시스템", "설정", "카메라", "갤러리", "전화", "통화", "lg thinq", "weather", "날씨", "launcher"],
    "religion_health": ["성경", "bible", "캐시워크", "health", "fit", "samsung health", "건강", "타임스프레드"],
}
AXES = {
    "low_activity": ["steps_sum__z", "activity_sum_21_03__z"],
    "night_phone": ["screen_use_00_06__z", "screen_use_18_24__z", "app_time_21_03__z"],
    "phone_internal": ["app_total_time__z", "app_unique_count__z", "app_social_time__z", "app_media_time__z"],
    "rest_quiet": ["longest_screenoff_run_h__z", "longest_quiet_run_h__z"],
    "low_mobility_context": ["gps_radius_proxy__z", "gps_unique_grid4__z", "wifi_unique_bssid__z", "ble_unique_addr__z", "state_entropy__z"],
    "physio_light_low": ["hr_mean__z", "hr_std__z", "mlight_mean__z", "wlight_mean__z"],
}


def md_table(df: pd.DataFrame, max_rows=None, floatfmt=".3f"):
    d = df.copy()
    if max_rows is not None: d = d.head(max_rows)
    cols = list(d.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "|".join(["---"]*len(cols)) + "|"]
    for _, row in d.iterrows():
        cells=[]
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and not pd.isna(v): cells.append(format(float(v), floatfmt))
            else: cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def cat_app(app: str):
    a = str(app).strip().lower()
    for cat, kws in APP_CATS.items():
        if any(kw.lower() in a for kw in kws): return cat
    return "other"


def parse_list(x):
    if isinstance(x, list): return x
    if isinstance(x, np.ndarray): return x.tolist()
    return []


def load_data():
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    train["lifelog_date"] = pd.to_datetime(train["lifelog_date"]).dt.date.astype(str)
    feat = pd.read_parquet(ROOT / "features" / "model_features_v0.parquet")
    feat["lifelog_date"] = pd.to_datetime(feat["lifelog_date"]).dt.date.astype(str)
    keep = KEYS + [c for c in FEATURES if c in feat.columns]
    df = train.merge(feat[keep], on=KEYS, how="left")
    df["date"] = pd.to_datetime(df["lifelog_date"])
    for c in [c for c in FEATURES if c in df.columns]:
        g = df.groupby("subject_id")[c]
        df[c + "__z"] = (df[c] - g.transform("mean")) / g.transform("std").replace(0, np.nan)

    raw = pd.read_parquet(ITEMS / "ch2025_mUsageStats.parquet")
    raw["lifelog_date"] = pd.to_datetime(raw["timestamp"]).dt.date.astype(str)
    rows=[]
    for _, r in raw.iterrows():
        hour = pd.to_datetime(r["timestamp"]).hour
        for it in parse_list(r["m_usage_stats"]):
            app = str(it.get("app_name", "")).strip().lower()
            sec = float(it.get("total_time", 0) or 0) / 1000.0
            if not app or sec <= 0: continue
            rows.append({"subject_id": r.subject_id, "lifelog_date": r.lifelog_date, "hour": hour, "app": app, "minutes": sec/60.0, "category": cat_app(app)})
    app = pd.DataFrame(rows)
    if len(app):
        cat_daily = app.groupby(KEYS + ["category"], as_index=False)["minutes"].sum().pivot_table(index=KEYS, columns="category", values="minutes", fill_value=0).reset_index()
        top_daily = app.groupby(KEYS + ["app"], as_index=False)["minutes"].sum().sort_values(KEYS + ["minutes"], ascending=[True, True, False])
    else:
        cat_daily = pd.DataFrame(columns=KEYS)
        top_daily = pd.DataFrame(columns=KEYS+["app","minutes"])
    df = df.merge(cat_daily, on=KEYS, how="left")
    for c in [c for c in cat_daily.columns if c not in KEYS]:
        df[c] = df[c].fillna(0)
        g = df.groupby("subject_id")[c]
        df[c + "__z"] = (df[c] - g.transform("mean")) / g.transform("std").replace(0, np.nan)
    return df, app, top_daily


def add_q2_events(df):
    d = df.sort_values(["subject_id", "date"]).copy()
    d["prev_Q2"] = d.groupby("subject_id")["Q2"].shift(1)
    d["next_Q2"] = d.groupby("subject_id")["Q2"].shift(-1)
    d["prev_Q3"] = d.groupby("subject_id")["Q3"].shift(1)
    def ev(r):
        if pd.isna(r.prev_Q2): return "start"
        if r.prev_Q2 == 0 and r.Q2 == 1: return "Q2_0_to_1"
        if r.prev_Q2 == 1 and r.Q2 == 0: return "Q2_1_to_0"
        if r.Q2 == 1: return "stable_1"
        return "stable_0"
    d["q2_event"] = d.apply(ev, axis=1)
    return d


def axis_scores(d):
    for axis, cols in AXES.items():
        cols = [c for c in cols if c in d.columns]
        if not cols: d[axis] = np.nan; continue
        val = d[cols].mean(axis=1)
        # For axes named low_*, invert so high score means low-activity/low-context/low-light story.
        if axis in {"low_activity", "low_mobility_context", "physio_light_low"}:
            val = -val
        d[axis] = val
    d["diary_intensity"] = d[[a for a in AXES if a in d]].abs().mean(axis=1)
    return d


def taxonomy(d):
    trans = d[d.q2_event.eq("Q2_0_to_1")].copy()
    axes = [a for a in AXES if a in trans]
    X = trans[axes].replace([np.inf, -np.inf], np.nan).fillna(0)
    Z = StandardScaler().fit_transform(X)
    k = min(5, len(trans))
    trans["q2_transition_type"] = KMeans(n_clusters=k, random_state=7, n_init=50).fit_predict(Z)
    summary = trans.groupby("q2_transition_type").agg(n_days=("Q2", "size"), Q1_rate=("Q1","mean"), Q3_rate=("Q3","mean"), S_all_rate=("S1","mean")).reset_index()
    # replace S_all_rate with mean of S labels
    smean = trans.groupby("q2_transition_type")[["S1","S2","S3","S4"]].mean().mean(axis=1).rename("S_family_mean").reset_index()
    summary = summary.drop(columns=["S_all_rate"]).merge(smean, on="q2_transition_type")
    axis_mean = trans.groupby("q2_transition_type")[axes].mean().reset_index()
    summary = summary.merge(axis_mean, on="q2_transition_type")
    # names from top axes
    names=[]
    for _, r in summary.iterrows():
        top = sorted([(a, r[a]) for a in axes], key=lambda x: x[1], reverse=True)[:2]
        names.append(" + ".join([a for a,v in top if v > 0.15]) or "mixed/weak")
    summary["type_name"] = names
    summary = summary[["q2_transition_type","type_name","n_days","Q1_rate","Q3_rate","S_family_mean",*axes]]
    summary.to_csv(AN/"phase5_q2_transition_taxonomy.csv", index=False)
    trans.to_csv(AN/"phase5_q2_transition_days_with_types.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 4))
    mat = summary.set_index("type_name")[axes]
    im = ax.imshow(mat.values, aspect="auto", cmap="coolwarm", vmin=-0.8, vmax=0.8)
    ax.set_xticks(range(len(axes)), axes, rotation=35, ha="right")
    ax.set_yticks(range(len(mat.index)), mat.index)
    ax.set_title("Phase5 A: Q2 0→1 transition taxonomy axes")
    fig.colorbar(im, ax=ax, fraction=.03); fig.tight_layout(); fig.savefig(FIG/"p5_A_q2_transition_taxonomy.png", dpi=180); plt.close(fig)

    lines=["# Phase 5A — Q2 0→1 transition taxonomy\n",
           "Q2 0→1 전환일을 하나의 현상으로 보지 않고, 생활 축별로 유형화했다. 값은 subject-normalized axis score이며, positive는 해당 narrative가 강하다는 뜻이다.\n",
           md_table(summary.round(3)), "\n"]
    (AN/"phase5_A_q2_transition_taxonomy.md").write_text("\n".join(lines), encoding="utf-8")
    return trans, summary


def day_diaries(d, top_daily):
    trans = d[d.q2_event.eq("Q2_0_to_1")].copy().sort_values("diary_intensity", ascending=False).head(35)
    rows=[]
    for _, r in trans.iterrows():
        key = (r.subject_id, r.lifelog_date)
        apps = top_daily[(top_daily.subject_id==key[0]) & (top_daily.lifelog_date==key[1])].head(4)
        app_str = ", ".join([f"{a.app}({a.minutes:.0f}m)" for _, a in apps.iterrows()])
        axes = sorted([(a, r.get(a, np.nan)) for a in AXES], key=lambda x: abs(x[1]) if pd.notna(x[1]) else -1, reverse=True)[:3]
        axis_str = ", ".join([f"{a}:{v:+.2f}" for a,v in axes if pd.notna(v)])
        narrative=[]
        if r.get("low_activity", 0) > 0.7: narrative.append("저활동")
        if r.get("night_phone", 0) > 0.7: narrative.append("야간폰")
        if r.get("phone_internal", 0) > 0.7: narrative.append("폰/앱 내부 체류")
        if r.get("low_mobility_context", 0) > 0.7: narrative.append("저이동/저context")
        if r.get("rest_quiet", 0) > 0.7: narrative.append("긴 휴식/무화면")
        if r.get("physio_light_low", 0) > 0.7: narrative.append("낮은 생체/빛 signal")
        if not narrative: narrative.append("혼합/약한 이벤트")
        rows.append({
            "subject_id": r.subject_id, "lifelog_date": r.lifelog_date,
            "labels": "".join([f"{l}{int(r[l])}" for l in LABELS]),
            "diary_type": "+".join(narrative),
            "top_axes": axis_str,
            "steps": r.get("steps_sum", np.nan),
            "night_screen": r.get("screen_use_00_06", np.nan),
            "screenoff_h": r.get("longest_screenoff_run_h", np.nan),
            "gps_radius": r.get("gps_radius_proxy", np.nan),
            "wifi_unique": r.get("wifi_unique_bssid", np.nan),
            "hr_mean": r.get("hr_mean", np.nan),
            "top_apps": app_str,
        })
    out = pd.DataFrame(rows)
    out.to_csv(AN/"phase5_q2_transition_day_diaries.csv", index=False)
    lines=["# Phase 5B — Q2 0→1 day diaries\n",
           "강한 Q2 0→1 전환일을 사람이 읽는 diary 형태로 바꿨다. 모델 피처가 아니라 라벨 의미를 해석하기 위한 field note다.\n",
           md_table(out.round(2), max_rows=35), "\n"]
    (AN/"phase5_B_q2_day_diaries.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def subject_cards(d, top_daily):
    cards=[]
    md=[]
    md.append("# Phase 5C — Subject profile cards\n")
    for s, g in d.groupby("subject_id"):
        q2trans = g[g.q2_event.eq("Q2_0_to_1")]
        apps = top_daily[top_daily.subject_id.eq(s)].groupby("app", as_index=False)["minutes"].sum().sort_values("minutes", ascending=False).head(6)
        axes_q2 = {}
        for a in AXES:
            axes_q2[a] = q2trans[a].mean() if len(q2trans) else np.nan
        top_axes = sorted(axes_q2.items(), key=lambda x: abs(x[1]) if pd.notna(x[1]) else -1, reverse=True)[:3]
        label_rates = {l: g[l].mean() for l in LABELS}
        card = {
            "subject_id": s, "n_days": len(g), "n_q2_0to1": len(q2trans),
            **{f"{l}_rate": v for l,v in label_rates.items()},
            "dominant_q2_axes": ", ".join([f"{a}:{v:+.2f}" for a,v in top_axes if pd.notna(v)]),
            "top_apps": ", ".join([f"{r.app}({r.minutes:.0f}m)" for _, r in apps.iterrows()]),
            "night_screen_mean": g.get("screen_use_00_06", pd.Series(dtype=float)).mean(),
            "screenoff_mean_h": g.get("longest_screenoff_run_h", pd.Series(dtype=float)).mean(),
            "gps_radius_mean": g.get("gps_radius_proxy", pd.Series(dtype=float)).mean(),
        }
        # narrative heuristic
        notes=[]
        if label_rates["Q1"] > 0.75: notes.append("Q1-high anchor")
        if label_rates["Q1"] < 0.25: notes.append("Q1-low anchor")
        if label_rates["Q2"] > 0.72: notes.append("Q2-high regime")
        if g["screen_use_00_06"].mean() > 50: notes.append("night-phone heavy")
        if g["longest_screenoff_run_h"].mean() < 3.5: notes.append("short screen-off/rest block")
        if label_rates["S1"] > .85 and label_rates["S2"] > .85 and label_rates["S3"] > .85: notes.append("S-family high/static")
        card["profile_tags"] = ", ".join(notes) or "mixed"
        cards.append(card)
        md.append(f"## {s}\n")
        md.append(f"- tags: **{card['profile_tags']}**\n")
        md.append("- label rates: " + ", ".join([f"{l}={label_rates[l]:.2f}" for l in LABELS]) + "\n")
        md.append(f"- Q2 0→1 count: {len(q2trans)}; dominant axes: {card['dominant_q2_axes']}\n")
        md.append(f"- mean night screen={card['night_screen_mean']:.1f}, screenoff={card['screenoff_mean_h']:.1f}h, gps_radius={card['gps_radius_mean']:.3f}\n")
        md.append(f"- top apps: {card['top_apps']}\n")
    out = pd.DataFrame(cards)
    out.to_csv(AN/"phase5_subject_profile_cards.csv", index=False)
    md.insert(2, "## compact table\n" + md_table(out.round(3)) + "\n")
    (AN/"phase5_C_subject_profile_cards.md").write_text("\n".join(md), encoding="utf-8")
    return out


def q2_q3_split(d):
    sub = d[d.Q2.eq(1)].copy()
    rows=[]
    for name, g in [("Q2=1,Q3=1", sub[sub.Q3.eq(1)]), ("Q2=1,Q3=0", sub[sub.Q3.eq(0)])]:
        rec={"class": name, "n_days": len(g), "Q1_rate": g.Q1.mean()}
        for a in AXES: rec[a] = g[a].mean()
        rows.append(rec)
    out=pd.DataFrame(rows)
    diff={"class":"diff_(Q3=1_minus_0)", "n_days": np.nan, "Q1_rate": rows[0]["Q1_rate"]-rows[1]["Q1_rate"]}
    for a in AXES: diff[a]=rows[0][a]-rows[1][a]
    out=pd.concat([out,pd.DataFrame([diff])], ignore_index=True)
    out.to_csv(AN/"phase5_q2_q3_semantic_split.csv", index=False)
    lines=["# Phase 5D — Q2 안에서 Q3가 갈라지는 의미\n",
           "Q2=1인 날만 놓고 Q3=1과 Q3=0의 생활 축을 비교했다. Q3가 Q2와 완전히 같은 라벨인지, 별도 의미가 있는지 보기 위한 분석이다.\n",
           md_table(out.round(3)), "\n"]
    (AN/"phase5_D_q2_q3_semantic_split.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def synthesis(tax, diaries, cards, split):
    # Extract interpretable facts
    top_types = tax.sort_values("n_days", ascending=False).head(3)
    q3diff = split[split["class"].eq("diff_(Q3=1_minus_0)")].iloc[0]
    lines=["# Phase 5 synthesis — day diary와 Q2 transition taxonomy\n",
           "Phase 5는 예측모델 없이 Q2 0→1 전환일을 사람이 읽을 수 있는 diary/taxonomy로 바꾼 분석이다.\n",
           "## 핵심 발견\n"]
    lines.append("1. **Q2 0→1은 단일 현상이 아니라 여러 subtype이다.** 가장 큰 subtype들은 다음과 같다.\n")
    lines.append(md_table(top_types[["type_name","n_days","Q1_rate","Q3_rate","S_family_mean","low_activity","night_phone","phone_internal","low_mobility_context","physio_light_low"]].round(3)))
    lines.append("\n2. **Q2 transition diary는 두 계열로 갈라진다.** 하나는 `low_mobility/context + low_activity` 계열, 다른 하나는 `night_phone/phone_internal` 계열이다. 즉 Q2는 ‘많이 움직임’이 아니라 `정지/실내/휴식/폰 내부 체류` 쪽 의미가 더 강하다.\n")
    lines.append(f"3. **Q3는 Q2와 같지만은 않다.** Q2=1 내에서 Q3=1 minus Q3=0 차이는 night_phone={q3diff['night_phone']:+.3f}, phone_internal={q3diff['phone_internal']:+.3f}, low_mobility_context={q3diff['low_mobility_context']:+.3f}, Q1_rate={q3diff['Q1_rate']:+.3f}. Q3는 Q2의 rest/low-mobility보다 `phone/social/subjective co-state` 쪽을 더 볼 가능성이 있다.\n")
    lines.append("4. **subject profile card가 필요하다.** id03/id06처럼 라벨 anchor가 다른 사람과 id08/id10처럼 night-phone regime인 사람은 같은 Q2=1이라도 의미가 다르다.\n")
    lines.append("\n## 다음 순수 DS 작업\n")
    lines.append("- Q2 subtype별 대표 날짜를 raw timeline으로 1분/10분 단위 plot: screen, app category, GPS radius, steps, HR.\n")
    lines.append("- id08/id10 night-phone profile과 id06 rest/recovery profile을 분리해서 label semantics를 비교.\n")
    lines.append("- Q3가 붙는 Q2=1과 안 붙는 Q2=1의 day diary를 더 많이 읽기.\n")
    lines.append("- S2 contradiction card: S2만 다르게 켜지는 날짜들의 diary 생성.\n")
    (AN/"phase5_synthesis_report.md").write_text("\n".join(lines), encoding="utf-8")

    idx="""# Phase 5 index — Q2 diary/taxonomy deep dive

Insight-only. 모델/OOF/submission 없음.

## Reports

1. `analysis/phase5_A_q2_transition_taxonomy.md`
2. `analysis/phase5_B_q2_day_diaries.md`
3. `analysis/phase5_C_subject_profile_cards.md`
4. `analysis/phase5_D_q2_q3_semantic_split.md`
5. `analysis/phase5_synthesis_report.md`

## CSV/Figure outputs

- `analysis/phase5_q2_transition_taxonomy.csv`
- `analysis/phase5_q2_transition_days_with_types.csv`
- `analysis/phase5_q2_transition_day_diaries.csv`
- `analysis/phase5_subject_profile_cards.csv`
- `analysis/phase5_q2_q3_semantic_split.csv`
- `analysis/figures/p5_A_q2_transition_taxonomy.png`
"""
    (AN/"phase5_index.md").write_text(idx, encoding="utf-8")


def main():
    df, app, top_daily = load_data()
    d = axis_scores(add_q2_events(df))
    trans, tax = taxonomy(d)
    diaries = day_diaries(d, top_daily)
    cards = subject_cards(d, top_daily)
    split = q2_q3_split(d)
    synthesis(tax, diaries, cards, split)
    print("WROTE Phase 5 diary/taxonomy reports under", AN)

if __name__ == "__main__":
    main()
