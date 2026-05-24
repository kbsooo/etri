#!/usr/bin/env python3
"""Phase 6: raw timeline plots for representative Q2 diary days.

Insight-only. No model, no validation, no submission. Produces 24h timelines
for selected Q2 transition days from raw app/screen/GPS/activity/HR/light/ambience.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ITEMS = DATA / "ch2025_data_items"
AN = ROOT / "analysis"
FIG = AN / "figures" / "phase6_timelines"
FIG.mkdir(parents=True, exist_ok=True)
AN.mkdir(exist_ok=True)
KEYS = ["subject_id", "lifelog_date"]
LABELS = ["Q1","Q2","Q3","S1","S2","S3","S4"]

APP_CATS = {
    "messaging_social": ["카카오톡", "instagram", "facebook", "discord", "threads", "메시지", "라인", "twitter", "x"],
    "video_music_media": ["youtube", "melon", "music", "넷플릭스", "netflix", "티빙", "wavve", "spotify", "동영상", "웹툰", "tiktok"],
    "finance_auth": ["bank", "뱅크", "카드", "pay", "페이", "토스", "kb", "신한", "auth", "인증", "증권", "stock"],
    "mobility_car": ["tmap", "카카오t", "네이버지도", "지도", "kia", "auto", "버스", "지하철", "길찾기", "코레일"],
    "shopping_delivery": ["shop", "쇼핑", "쿠팡", "배달", "mart", "몰", "store", "당근"],
    "work_study": ["teams", "slack", "notion", "docs", "pdf", "office", "word", "excel", "class", "study", "학교", "캘린더"],
    "game": ["game", "게임", "bricks", "goblin", "sort", "nonogram", "match", "클래시", "royal"],
    "utility_home": ["one ui", "시스템", "설정", "카메라", "갤러리", "전화", "통화", "lg thinq", "weather", "날씨", "launcher"],
    "religion_health": ["성경", "bible", "캐시워크", "health", "fit", "samsung health", "건강", "타임스프레드"],
}
CAT_ORDER = ["messaging_social", "video_music_media", "game", "utility_home", "shopping_delivery", "mobility_car", "finance_auth", "religion_health", "work_study", "other"]
REP_DAYS = [
    ("id10", "2024-09-07", "night social phone / low mobility"),
    ("id05", "2024-09-22", "zero-step + YouTube/night-phone"),
    ("id01", "2024-08-31", "low-mobility/low-HR/rest"),
    ("id09", "2024-07-13", "webtoon/TikTok/night-phone"),
    ("id08", "2024-08-16", "Q2=1 Q3=0 app/internal case"),
    ("id03", "2024-07-25", "high-Q anchor, active but Q2 flip"),
]


def cat_app(a: str):
    s = str(a).strip().lower()
    for cat, kws in APP_CATS.items():
        if any(kw.lower() in s for kw in kws):
            return cat
    return "other"


def parse_list(x):
    if isinstance(x, list): return x
    if isinstance(x, np.ndarray): return x.tolist()
    return []


def dt_range(date):
    start = pd.Timestamp(date)
    end = start + pd.Timedelta(days=1)
    return start, end


def filter_day(df, sid, date, time_col="timestamp"):
    st, en = dt_range(date)
    return df[(df.subject_id.eq(sid)) & (df[time_col] >= st) & (df[time_col] < en)].copy()


def hour_bin(ts):
    return pd.to_datetime(ts).dt.hour + pd.to_datetime(ts).dt.minute / 60.0


def load_raw():
    raw = {}
    for name in ["mUsageStats", "mScreenStatus", "mGps", "mActivity", "mAmbience", "wHr", "mLight", "wLight"]:
        p = ITEMS / f"ch2025_{name}.parquet"
        if p.exists():
            raw[name] = pd.read_parquet(p)
    for df in raw.values():
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    labels = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    labels["lifelog_date"] = pd.to_datetime(labels["lifelog_date"]).dt.date.astype(str)
    diaries = pd.read_csv(AN / "phase5_q2_transition_day_diaries.csv") if (AN / "phase5_q2_transition_day_diaries.csv").exists() else pd.DataFrame()
    return raw, labels, diaries


def app_day(raw_app, sid, date):
    d = filter_day(raw_app, sid, date)
    rows=[]
    for _, r in d.iterrows():
        h = r.timestamp.hour + r.timestamp.minute / 60
        for it in parse_list(r.m_usage_stats):
            app = str(it.get("app_name", "")).strip().lower()
            sec = float(it.get("total_time", 0) or 0) / 1000.0
            if app and sec > 0:
                rows.append({"hour": h, "app": app, "category": cat_app(app), "minutes": sec/60.0})
    return pd.DataFrame(rows)


def gps_day(raw_gps, sid, date):
    d = filter_day(raw_gps, sid, date)
    rows=[]
    for _, r in d.iterrows():
        pts = parse_list(r.m_gps)
        if not pts: continue
        speeds=[]; lats=[]; lons=[]
        for p in pts:
            try:
                speeds.append(float(p.get("speed", np.nan)))
                lats.append(float(p.get("latitude", np.nan)))
                lons.append(float(p.get("longitude", np.nan)))
            except Exception:
                pass
        rows.append({"timestamp": r.timestamp, "hour": r.timestamp.hour + r.timestamp.minute/60, "gps_n": len(pts), "speed_mean": np.nanmean(speeds), "lat_std": np.nanstd(lats), "lon_std": np.nanstd(lons)})
    return pd.DataFrame(rows)


def hr_day(raw_hr, sid, date):
    d = filter_day(raw_hr, sid, date)
    rows=[]
    for _, r in d.iterrows():
        vals = [float(v) for v in parse_list(r.heart_rate) if pd.notna(v)]
        if vals:
            rows.append({"timestamp": r.timestamp, "hour": r.timestamp.hour + r.timestamp.minute/60, "hr_mean": np.mean(vals), "hr_min": np.min(vals), "hr_max": np.max(vals)})
    return pd.DataFrame(rows)


def ambience_day(raw_amb, sid, date):
    d = filter_day(raw_amb, sid, date)
    rows=[]
    for _, r in d.iterrows():
        labels = parse_list(r.m_ambience)
        if not labels: continue
        # keep top semantic tags and coarse inside/outside/music/speech/vehicle scores
        rec={"hour": r.timestamp.hour + r.timestamp.minute/60, "top": str(labels[0][0]) if labels else ""}
        text_scores = {"Music":0, "Speech":0, "Vehicle":0, "Outside":0, "Inside":0}
        for pair in labels:
            if len(pair) < 2: continue
            name, score = str(pair[0]), float(pair[1])
            for k in text_scores:
                if k.lower() in name.lower(): text_scores[k] += score
        rec.update(text_scores); rows.append(rec)
    return pd.DataFrame(rows)


def bin_numeric(df, value, agg="mean"):
    if df.empty or value not in df: return pd.Series(dtype=float)
    x = df.copy(); x["bin"] = np.floor(x["hour"]*2)/2
    return x.groupby("bin")[value].agg(agg)


def top_apps_str(appdf):
    if appdf.empty: return ""
    top = appdf.groupby("app")["minutes"].sum().sort_values(ascending=False).head(6)
    return ", ".join([f"{a}({m:.0f}m)" for a,m in top.items()])


def plot_day(raw, labels, diaries, sid, date, note):
    lab = labels[(labels.subject_id.eq(sid)) & (labels.lifelog_date.eq(date))]
    lab_str = " ".join([f"{l}={int(lab.iloc[0][l])}" for l in LABELS]) if len(lab) else ""
    app = app_day(raw["mUsageStats"], sid, date) if "mUsageStats" in raw else pd.DataFrame()
    screen = filter_day(raw["mScreenStatus"], sid, date) if "mScreenStatus" in raw else pd.DataFrame()
    act = filter_day(raw["mActivity"], sid, date) if "mActivity" in raw else pd.DataFrame()
    gps = gps_day(raw["mGps"], sid, date) if "mGps" in raw else pd.DataFrame()
    hr = hr_day(raw["wHr"], sid, date) if "wHr" in raw else pd.DataFrame()
    ml = filter_day(raw["mLight"], sid, date) if "mLight" in raw else pd.DataFrame()
    wl = filter_day(raw["wLight"], sid, date) if "wLight" in raw else pd.DataFrame()
    amb = ambience_day(raw["mAmbience"], sid, date) if "mAmbience" in raw else pd.DataFrame()

    fig, axes = plt.subplots(6, 1, figsize=(12, 11), sharex=True)
    fig.suptitle(f"{sid} {date} — {note}\n{lab_str}", fontsize=12)

    # app stacked 30min
    if not app.empty:
        app["bin"] = np.floor(app.hour*2)/2
        pivot = app.groupby(["bin", "category"])["minutes"].sum().unstack(fill_value=0)
        for c in CAT_ORDER:
            if c not in pivot: pivot[c]=0
        bottom = np.zeros(len(pivot.index))
        for c in CAT_ORDER:
            vals = pivot[c].values
            axes[0].bar(pivot.index, vals, width=0.45, bottom=bottom, label=c)
            bottom += vals
        axes[0].legend(ncol=5, fontsize=6, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    axes[0].set_ylabel("app min/30m")

    if not screen.empty:
        screen["hour"] = hour_bin(screen.timestamp)
        s = bin_numeric(screen, "m_screen_use", "mean")
        axes[1].plot(s.index, s.values, color="tab:blue")
        axes[1].fill_between(s.index, 0, s.values, color="tab:blue", alpha=.25)
    axes[1].set_ylabel("screen use")

    if not act.empty:
        act["hour"] = hour_bin(act.timestamp)
        a = bin_numeric(act, "m_activity", "sum")
        axes[2].bar(a.index, a.values, width=.45, color="tab:green")
    axes[2].set_ylabel("activity sum")

    if not gps.empty:
        sp = bin_numeric(gps, "speed_mean", "mean")
        gn = bin_numeric(gps, "gps_n", "sum")
        axes[3].plot(sp.index, sp.values, color="tab:red", label="speed")
        ax2 = axes[3].twinx(); ax2.bar(gn.index, gn.values, width=.45, color="gray", alpha=.25, label="gps_n")
        ax2.set_ylabel("gps_n")
    axes[3].set_ylabel("gps speed")

    if not hr.empty:
        h = bin_numeric(hr, "hr_mean", "mean")
        axes[4].plot(h.index, h.values, color="tab:purple", label="HR")
    for lightdf, col, color in [(ml, "m_light", "orange"), (wl, "w_light", "gold")]:
        if not lightdf.empty:
            lightdf["hour"] = hour_bin(lightdf.timestamp)
            l = bin_numeric(lightdf, col, "mean")
            axes[4].plot(l.index, np.log1p(l.values), color=color, alpha=.5, label=f"log {col}")
    axes[4].legend(fontsize=7); axes[4].set_ylabel("HR / log light")

    if not amb.empty:
        for k in ["Music", "Speech", "Vehicle", "Outside", "Inside"]:
            s = bin_numeric(amb, k, "mean")
            if len(s): axes[5].plot(s.index, s.values, label=k)
        axes[5].legend(fontsize=7)
    axes[5].set_ylabel("ambience score")
    axes[5].set_xlabel("hour")
    axes[5].set_xlim(0, 24); axes[5].set_xticks(range(0,25,3))
    for ax in axes: ax.grid(alpha=.2)
    fig.tight_layout(rect=[0, 0, 0.86, .95])
    fname = f"{sid}_{date}.png"
    fig.savefig(FIG / fname, dpi=170)
    plt.close(fig)

    # derive concise notes
    night_app = app[(app.hour>=21) | (app.hour<6)].groupby("category")["minutes"].sum().sort_values(ascending=False) if not app.empty else pd.Series(dtype=float)
    total_app = app.minutes.sum() if not app.empty else 0
    night_screen = screen[(screen.timestamp.dt.hour>=21) | (screen.timestamp.dt.hour<6)]["m_screen_use"].sum() if not screen.empty else np.nan
    gps_n = gps.gps_n.sum() if not gps.empty else 0
    activity_sum = act.m_activity.sum() if not act.empty else np.nan
    hr_mean = hr.hr_mean.mean() if not hr.empty else np.nan
    return {
        "subject_id": sid, "lifelog_date": date, "note": note, "labels": lab_str,
        "figure": str(FIG / fname), "top_apps": top_apps_str(app),
        "total_app_min": total_app, "night_top_category": night_app.index[0] if len(night_app) else "NA",
        "night_top_min": night_app.iloc[0] if len(night_app) else np.nan,
        "night_screen_sum": night_screen, "activity_sum_raw": activity_sum,
        "gps_points": gps_n, "hr_mean": hr_mean,
    }


def write_report(rows):
    df = pd.DataFrame(rows)
    df.to_csv(AN / "phase6_raw_timeline_summary.csv", index=False)
    lines = ["# Phase 6 — Raw timeline inspection for Q2 diary days\n",
             "대표 Q2 0→1 날짜를 raw sensor/app timeline으로 그려서 Phase 5의 `inward day` 해석이 시간축에서도 보이는지 확인했다. 예측모델/OOF/submission 없음.\n",
             "## Timeline summary\n", md_table(df.drop(columns=["figure"]).round(2)), "\n",
             "## Figures\n"]
    for _, r in df.iterrows():
        lines.append(f"- `{r['subject_id']} {r['lifelog_date']}` — {r['note']}: `{r['figure']}`\n")
    lines.append("\n## 해석 메모\n")
    lines.append("- Q2 diary 대표일은 대체로 외부 이동 증가보다는 app/screen burst, 낮은 activity, 적은 GPS/context, 또는 긴 screen-off/rest block 중 하나로 설명된다.\n")
    lines.append("- 다만 id03처럼 활동량이 높은데도 Q2가 켜지는 contradiction day가 있어, Q2는 단일 규칙이 아니라 subject-specific transition subtype으로 봐야 한다.\n")
    lines.append("- 이 단계는 feature selection이 아니라 label semantics 검증이다. 다음은 S2 contradiction timeline 또는 subtype별 subject comparison이 자연스럽다.\n")
    (AN / "phase6_raw_timeline_report.md").write_text("\n".join(lines), encoding="utf-8")
    idx = """# Phase 6 index — Raw timelines

Insight-only raw timeline inspection.

- `analysis/phase6_raw_timeline.py`
- `analysis/phase6_raw_timeline_report.md`
- `analysis/phase6_raw_timeline_summary.csv`
- `analysis/figures/phase6_timelines/*.png`

Non-goals: no model, no OOF, no submission.
"""
    (AN / "phase6_index.md").write_text(idx, encoding="utf-8")


def md_table(df: pd.DataFrame, max_rows=None, floatfmt=".2f"):
    d=df.copy()
    if max_rows: d=d.head(max_rows)
    cols=list(d.columns)
    lines=["| "+" | ".join(cols)+" |", "|"+"|".join(["---"]*len(cols))+"|"]
    for _, row in d.iterrows():
        cells=[]
        for v in row.tolist():
            if isinstance(v, (float, np.floating)) and not pd.isna(v): cells.append(format(float(v), floatfmt))
            else: cells.append(str(v))
        lines.append("| "+" | ".join(cells)+" |")
    return "\n".join(lines)


def main():
    raw, labels, diaries = load_raw()
    rows=[]
    for sid, date, note in REP_DAYS:
        rows.append(plot_day(raw, labels, diaries, sid, date, note))
    write_report(rows)
    print("WROTE Phase 6 raw timeline report and figures", FIG)

if __name__ == "__main__":
    main()
