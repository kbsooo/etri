#!/usr/bin/env python3
from __future__ import annotations

import math
import textwrap
from pathlib import Path
from itertools import combinations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mutual_info_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEATURES = ROOT / "features"
ANALYSIS = ROOT / "analysis"
FIG = ANALYSIS / "figures"
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q_LABELS = ["Q1", "Q2", "Q3"]
S_LABELS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
FOCUS_SUBJECTS = ["id03", "id06", "id08", "id09", "id10"]


def ensure_dirs():
    ANALYSIS.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)


def entropy01(x):
    p = pd.Series(x).dropna().mean()
    if pd.isna(p) or p <= 0 or p >= 1:
        return 0.0
    return float(-(p * math.log2(p) + (1 - p) * math.log2(1 - p)))


def safe_corr(a, b):
    a = pd.Series(a).astype(float)
    b = pd.Series(b).astype(float)
    m = a.notna() & b.notna()
    if m.sum() < 5 or a[m].nunique() < 2 or b[m].nunique() < 2:
        return np.nan
    return float(np.corrcoef(a[m], b[m])[0, 1])


def point_biserial(y, x):
    y = pd.Series(y).astype(float)
    x = pd.Series(x).astype(float).replace([np.inf, -np.inf], np.nan)
    m = y.notna() & x.notna()
    if m.sum() < 8 or y[m].nunique() < 2 or x[m].std() == 0:
        return np.nan
    return float(np.corrcoef(y[m], x[m])[0, 1])


def add_prev_next(df):
    df = df.sort_values(["subject_id", "lifelog_date"]).copy()
    for lab in LABELS:
        df[f"{lab}_prev"] = df.groupby("subject_id")[lab].shift(1)
        df[f"{lab}_next"] = df.groupby("subject_id")[lab].shift(-1)
        df[f"{lab}_changed_from_prev"] = (df[lab] != df[f"{lab}_prev"]).where(df[f"{lab}_prev"].notna())
    return df


def load_main():
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv")
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    train["split"] = "train"
    sample["split"] = "test"
    for d in [train, sample]:
        d["lifelog_date"] = pd.to_datetime(d["lifelog_date"])
        d["sleep_date"] = pd.to_datetime(d["sleep_date"])
    feat = pd.read_parquet(FEATURES / "model_features_v0.parquet")
    feat["lifelog_date"] = pd.to_datetime(feat["lifelog_date"])
    merged = train.merge(feat, on=["subject_id", "lifelog_date"], how="left", suffixes=("", "__feat"))
    merged = add_prev_next(merged)
    all_rows = pd.concat([train[KEYS + ["split"]], sample[KEYS + ["split"]]], ignore_index=True)
    all_rows = all_rows.merge(feat, on=["subject_id", "lifelog_date"], how="left")
    return train, sample, feat, merged, all_rows


def classify_family(col: str) -> str:
    c = col.lower()
    if any(k in c for k in ["sleep", "quiet", "screenoff", "s4x", "pre_sleep", "prevnight"]):
        return "sleep/long-rest"
    if any(k in c for k in ["gps", "wifi", "ble", "location", "grid", "radius"]):
        return "gps/context"
    if any(k in c for k in ["step", "pedo", "activity", "distance", "speed"]):
        return "activity/step"
    if any(k in c for k in ["screen", "app", "usage", "phone"]):
        return "phone/app/screen"
    if any(k in c for k in ["hr", "light", "amb", "ac_"]):
        return "sensor/coverage"
    if any(k in c for k in ["entropy", "fragment", "weekday", "roll", "prev_delta", "dev_"]):
        return "routine/regularity"
    return "other"


def subject_label_language(df):
    rows = []
    pair_rows = []
    for sid, g in df.groupby("subject_id"):
        g = g.sort_values("lifelog_date")
        for lab in LABELS:
            vals = g[lab]
            persist = (vals == vals.shift(1)).iloc[1:].mean()
            rows.append({
                "subject_id": sid,
                "label": lab,
                "n": len(g),
                "prevalence": float(vals.mean()),
                "entropy_bits": entropy01(vals),
                "persistence": float(persist) if not pd.isna(persist) else np.nan,
                "transition_rate": float(1 - persist) if not pd.isna(persist) else np.nan,
            })
        for a, b in combinations(LABELS, 2):
            pair_rows.append({"subject_id": sid, "a": a, "b": b, "corr": safe_corr(g[a], g[b]), "mi": mutual_info_score(g[a], g[b])})
    subj = pd.DataFrame(rows)
    pairs = pd.DataFrame(pair_rows)

    # compact subject-level summary for interpretability
    wide_prev = subj.pivot(index="subject_id", columns="label", values="prevalence")
    wide_ent = subj.pivot(index="subject_id", columns="label", values="entropy_bits")
    q_anchor = wide_prev[Q_LABELS].std(axis=1).rename("q_prevalence_spread")
    s_anchor = wide_prev[S_LABELS].std(axis=1).rename("s_prevalence_spread")
    summary = pd.concat([wide_prev.add_prefix("prev_"), wide_ent.add_prefix("entropy_"), q_anchor, s_anchor], axis=1).reset_index()

    # Q3 shape: closer to Q1 or Q2 per subject and globally
    qshape = []
    for sid, g in df.groupby("subject_id"):
        qshape.append({
            "subject_id": sid,
            "corr_Q3_Q1": safe_corr(g["Q3"], g["Q1"]),
            "corr_Q3_Q2": safe_corr(g["Q3"], g["Q2"]),
            "corr_Q1_Q2": safe_corr(g["Q1"], g["Q2"]),
            "Q3_type_hint": "Q2-like" if abs(safe_corr(g["Q3"], g["Q2"]) or 0) > abs(safe_corr(g["Q3"], g["Q1"]) or 0) else "Q1-like/anchor-like",
        })
    qshape = pd.DataFrame(qshape)

    # S2 contradictions: S2 against S1/S3/S4 majority
    dd = df.copy()
    dd["S_others_mean"] = dd[["S1", "S3", "S4"]].mean(axis=1)
    dd["S2_contradiction"] = ((dd["S2"] == 1) & (dd["S_others_mean"] <= 1/3)) | ((dd["S2"] == 0) & (dd["S_others_mean"] >= 2/3))
    s2 = dd.groupby("subject_id").agg(n=("S2", "size"), s2_prev=("S2", "mean"), s2_contradiction_rate=("S2_contradiction", "mean"), s_others_mean=("S_others_mean", "mean")).reset_index()
    return subj, pairs, summary, qshape, s2


def make_deviation_tables(df):
    zcols = [c for c in df.columns if c.endswith("__subj_z") and pd.api.types.is_numeric_dtype(df[c])]
    # Remove very sparse pathological cols
    keep = []
    for c in zcols:
        x = df[c].replace([np.inf, -np.inf], np.nan)
        if x.notna().mean() > 0.5 and x.std(skipna=True) > 1e-6:
            keep.append(c)
    zcols = keep[:]
    fam = {c: classify_family(c) for c in zcols}

    # family deviation score per row
    dev = df[KEYS + LABELS].copy()
    for f in sorted(set(fam.values())):
        cols = [c for c, ff in fam.items() if ff == f]
        if cols:
            dev[f"dev_{f}"] = df[cols].abs().mean(axis=1)
    dev_cols = [c for c in dev.columns if c.startswith("dev_")]
    dev["dev_overall"] = dev[dev_cols].mean(axis=1)

    # target x family high-vs-low target rate and correlations
    rows = []
    for lab in LABELS:
        for c in dev_cols + ["dev_overall"]:
            x = dev[c]
            q70 = x.quantile(0.7)
            q30 = x.quantile(0.3)
            hi = dev.loc[x >= q70, lab].mean()
            lo = dev.loc[x <= q30, lab].mean()
            rows.append({"label": lab, "deviation_family": c.replace("dev_", ""), "corr": point_biserial(dev[lab], x), "high70_rate": hi, "low30_rate": lo, "high_minus_low": hi - lo, "n_high": int((x >= q70).sum()), "n_low": int((x <= q30).sum())})
    fam_signal = pd.DataFrame(rows)

    # top individual subject-normalized features by label
    top_rows = []
    for lab in LABELS:
        vals = []
        for c in zcols:
            corr = point_biserial(df[lab], df[c])
            if pd.notna(corr):
                vals.append((abs(corr), corr, c, fam[c]))
        for rank, (ab, corr, c, f) in enumerate(sorted(vals, reverse=True)[:40], 1):
            top_rows.append({"label": lab, "rank": rank, "feature": c, "family": f, "corr": corr, "abs_corr": ab})
    top = pd.DataFrame(top_rows)

    # most unusual train days
    unusual = dev.sort_values("dev_overall", ascending=False).head(80)
    return dev, fam_signal, top, unusual


def long_rest_event_study(df):
    # Avoid `s4x_sleep_block_len_h` as an event threshold: in this feature set it is capped at 19h
    # and marks almost every row as 12h+. Use cross-night quiet/screenoff runs as the long-rest
    # event proxy, then keep the capped sleep-block columns only in downstream deviation analysis.
    candidates = [c for c in [
        "s4x_cross_quiet_longest_h", "s4x_cross_screenoff_longest_h", "longest_screenoff_run_h", "longest_quiet_run_h"
    ] if c in df.columns]
    prev_cols = [f"{lab}_prev" for lab in LABELS if f"{lab}_prev" in df.columns]
    next_cols = [f"{lab}_next" for lab in LABELS if f"{lab}_next" in df.columns]
    out = df[KEYS + LABELS + prev_cols + next_cols + candidates].copy()
    if not candidates:
        out["long_rest_proxy_h"] = np.nan
    else:
        out["long_rest_proxy_h"] = out[candidates].max(axis=1)
    out = out.sort_values(["subject_id", "lifelog_date"])
    out["long_rest_event_12h"] = out["long_rest_proxy_h"] >= 12
    out["pre_long_rest"] = out.groupby("subject_id")["long_rest_event_12h"].shift(-1).fillna(False)
    out["post_long_rest"] = out.groupby("subject_id")["long_rest_event_12h"].shift(1).fillna(False)
    def event_class(r):
        if r["long_rest_event_12h"]: return "long_rest"
        if r["pre_long_rest"]: return "pre_long_rest"
        if r["post_long_rest"]: return "post_long_rest"
        return "normal"
    out["event_class"] = out.apply(event_class, axis=1)
    counts = out.groupby(["subject_id", "event_class"]).size().unstack(fill_value=0).reset_index()
    label_rates = out.groupby("event_class")[LABELS].agg(["mean", "count"])
    label_rates.columns = [f"{a}_{b}" for a,b in label_rates.columns]
    label_rates = label_rates.reset_index()
    by_subject_rates = out.groupby(["subject_id", "event_class"])[LABELS + ["long_rest_proxy_h"]].mean().reset_index()

    # q2 transition class
    out["Q2_transition"] = np.select([
        (out["Q2_prev"] == 0) & (out["Q2"] == 1),
        (out["Q2_prev"] == 1) & (out["Q2"] == 0),
        (out["Q2_prev"] == 0) & (out["Q2"] == 0),
        (out["Q2_prev"] == 1) & (out["Q2"] == 1),
    ], ["0_to_1", "1_to_0", "stable_0", "stable_1"], default="first/unknown")
    q2tab = out.groupby("Q2_transition")[LABELS + ["long_rest_proxy_h", "long_rest_event_12h"]].mean().reset_index()
    return out, counts, label_rates, by_subject_rates, q2tab, candidates


def gps_archaeology(train):
    gps_path = DATA / "ch2025_data_items" / "ch2025_mGps.parquet"
    gps = pd.read_parquet(gps_path)
    gps["date"] = pd.to_datetime(gps["timestamp"]).dt.normalize()
    def get_lat(x):
        try:
            if len(x) == 0: return np.nan
            return float(x[0].get("latitude", np.nan))
        except Exception:
            return np.nan
    def get_lon(x):
        try:
            if len(x) == 0: return np.nan
            return float(x[0].get("longitude", np.nan))
        except Exception:
            return np.nan
    gps["lat"] = gps["m_gps"].map(get_lat)
    gps["lon"] = gps["m_gps"].map(get_lon)
    gps = gps.dropna(subset=["lat", "lon"])
    rows = []
    daily_rows = []
    for precision in [2, 3, 4, 5]:
        gps["cell"] = gps["lat"].round(precision).astype(str) + "," + gps["lon"].round(precision).astype(str)
        for sid, sg in gps.groupby("subject_id"):
            vc = sg["cell"].value_counts()
            home = vc.index[0]
            home_share_all = vc.iloc[0] / vc.sum()
            rows.append({"subject_id": sid, "precision": precision, "home_cell": home, "home_share_all_records": home_share_all, "unique_cells": int(vc.size), "records": int(vc.sum())})
            dg = sg.groupby("date").agg(records=("cell", "size"), home_records=("cell", lambda s, h=home: int((s == h).sum())), unique_cells=("cell", "nunique")).reset_index()
            dg["home_share"] = dg["home_records"] / dg["records"].clip(lower=1)
            dg["subject_id"] = sid
            dg["precision"] = precision
            daily_rows.append(dg)
    summary = pd.DataFrame(rows)
    daily = pd.concat(daily_rows, ignore_index=True)
    # link train labels by lifelog_date at precision=3/4
    label_link = []
    tr = train.copy()
    tr["date"] = pd.to_datetime(tr["lifelog_date"]).dt.normalize()
    for precision in [3,4]:
        merged = tr.merge(daily[daily["precision"] == precision], on=["subject_id", "date"], how="left")
        for lab in LABELS:
            label_link.append({"precision": precision, "label": lab, "corr_home_share": point_biserial(merged[lab], merged["home_share"]), "corr_unique_cells": point_biserial(merged[lab], merged["unique_cells"])})
    return summary, daily, pd.DataFrame(label_link)


def cluster_validation(df, feat):
    # subject-level lifestyle profile from stable interpretable columns
    base_terms = ["screen_use_sum", "steps_sum", "distance_sum", "gps_unique_grid4", "gps_radius_proxy", "wifi_unique_bssid", "ble_unique_addr", "app_total_time", "app_unique_count", "longest_quiet_run_h", "longest_screenoff_run_h", "s4x_sleep_block_len_h", "state_entropy", "night_state_entropy"]
    cols = [c for c in base_terms if c in feat.columns and pd.api.types.is_numeric_dtype(feat[c])]
    prof = feat.groupby("subject_id")[cols].mean().replace([np.inf,-np.inf], np.nan).fillna(0)
    X = StandardScaler().fit_transform(prof)
    k = min(3, len(prof))
    km = KMeans(n_clusters=k, random_state=42, n_init=20).fit(X)
    clusters = pd.DataFrame({"subject_id": prof.index, "cluster": km.labels_}).reset_index(drop=True)
    clusters["cluster"] = "C" + clusters["cluster"].astype(str)
    # order clusters by mean mobility if possible
    if "gps_radius_proxy" in prof.columns:
        tmp = clusters.merge(prof[["gps_radius_proxy"]].reset_index(), on="subject_id")
        order = tmp.groupby("cluster")["gps_radius_proxy"].mean().sort_values().index.tolist()
        remap = {c: f"C{i}_mobility_rank" for i,c in enumerate(order)}
        clusters["cluster"] = clusters["cluster"].map(remap)
    labeled = df.merge(clusters, on="subject_id", how="left")
    rates = labeled.groupby("cluster")[LABELS].agg(["mean", "count"])
    rates.columns = [f"{a}_{b}" for a,b in rates.columns]
    rates = rates.reset_index()
    subj_cluster = clusters.merge(df.groupby("subject_id")[LABELS].mean().reset_index(), on="subject_id", how="left")
    return clusters, prof.reset_index(), rates, subj_cluster


def write_md(path, title, body):
    path.write_text(f"# {title}\n\n" + body.strip() + "\n", encoding="utf-8")


def make_figures(summary, qshape, dev_signal, event_out, gps_summary, clusters, cluster_rates):
    plt.style.use("default")
    # A prevalence heatmap
    prev = summary.set_index("subject_id")[[f"prev_{l}" for l in LABELS]]
    fig, ax = plt.subplots(figsize=(9, 4))
    im = ax.imshow(prev.values, aspect="auto", vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(len(LABELS)), LABELS)
    ax.set_yticks(range(len(prev.index)), prev.index)
    ax.set_title("Phase3 A: label prevalence by subject")
    fig.colorbar(im, ax=ax, label="prevalence")
    fig.tight_layout(); fig.savefig(FIG / "p3_A_subject_label_prevalence.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(qshape))
    ax.bar(x-0.2, qshape["corr_Q3_Q1"].fillna(0), width=0.4, label="corr(Q3,Q1)")
    ax.bar(x+0.2, qshape["corr_Q3_Q2"].fillna(0), width=0.4, label="corr(Q3,Q2)")
    ax.set_xticks(x, qshape["subject_id"], rotation=45)
    ax.axhline(0, color="black", lw=0.8)
    ax.legend(); ax.set_title("Phase3 A: Q3 shape: Q1-like vs Q2-like")
    fig.tight_layout(); fig.savefig(FIG / "p3_A_q3_shape_by_subject.png", dpi=160); plt.close(fig)

    # B deviation family signal Q2/Q3/Q1
    sub = dev_signal[dev_signal["label"].isin(["Q1","Q2","Q3"])].copy()
    piv = sub.pivot_table(index="deviation_family", columns="label", values="high_minus_low")
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(piv.fillna(0).values, aspect="auto", cmap="coolwarm", vmin=-0.25, vmax=0.25)
    ax.set_xticks(range(len(piv.columns)), piv.columns)
    ax.set_yticks(range(len(piv.index)), piv.index)
    ax.set_title("Phase3 B: high-deviation day label-rate lift")
    fig.colorbar(im, ax=ax, label="high70 - low30")
    fig.tight_layout(); fig.savefig(FIG / "p3_B_deviation_signal_heatmap.png", dpi=160); plt.close(fig)

    # C long rest by subject
    cnt = event_out.groupby("subject_id")["long_rest_event_12h"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8,4))
    cnt.plot(kind="bar", ax=ax)
    ax.set_title("Phase3 C: 12h+ long-rest proxy count by subject")
    ax.set_ylabel("days")
    fig.tight_layout(); fig.savefig(FIG / "p3_C_long_rest_counts.png", dpi=160); plt.close(fig)

    # D gps home share precision for id09/id10/focus
    gps_focus = gps_summary[gps_summary["subject_id"].isin(FOCUS_SUBJECTS)]
    fig, ax = plt.subplots(figsize=(8,4))
    for sid, g in gps_focus.groupby("subject_id"):
        ax.plot(g["precision"], g["home_share_all_records"], marker="o", label=sid)
    ax.set_xlabel("rounding precision"); ax.set_ylabel("dominant-cell share")
    ax.set_title("Phase3 D: GPS home recovery by rounding precision")
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "p3_D_gps_home_recovery.png", dpi=160); plt.close(fig)

    # E clusters
    cr = cluster_rates.set_index("cluster")[[f"{l}_mean" for l in LABELS]]
    fig, ax = plt.subplots(figsize=(9,4))
    im = ax.imshow(cr.values, aspect="auto", vmin=0, vmax=1, cmap="magma")
    ax.set_xticks(range(len(LABELS)), LABELS)
    ax.set_yticks(range(len(cr.index)), cr.index)
    ax.set_title("Phase3 E: target prevalence by lifestyle cluster")
    fig.colorbar(im, ax=ax)
    fig.tight_layout(); fig.savefig(FIG / "p3_E_cluster_target_prevalence.png", dpi=160); plt.close(fig)


def main():
    ensure_dirs()
    train, sample, feat, df, all_rows = load_main()
    subj, pairs, summary, qshape, s2 = subject_label_language(df)
    dev, dev_signal, top_dev, unusual = make_deviation_tables(df)
    event_out, event_counts, event_rates, event_subject_rates, q2_transition, long_rest_cols = long_rest_event_study(df)
    gps_summary, gps_daily, gps_label_link = gps_archaeology(train)
    clusters, cluster_profile, cluster_rates, subj_cluster = cluster_validation(df, feat)

    # Save CSVs
    subj.to_csv(ANALYSIS / "phase3_subject_label_language_long.csv", index=False)
    pairs.to_csv(ANALYSIS / "phase3_subject_pair_relations.csv", index=False)
    summary.to_csv(ANALYSIS / "phase3_subject_label_language_summary.csv", index=False)
    qshape.to_csv(ANALYSIS / "phase3_q3_shape_by_subject.csv", index=False)
    s2.to_csv(ANALYSIS / "phase3_s2_contradiction_by_subject.csv", index=False)
    dev.to_csv(ANALYSIS / "phase3_day_deviation_scores.csv", index=False)
    dev_signal.to_csv(ANALYSIS / "phase3_day_deviation_target_signal.csv", index=False)
    top_dev.to_csv(ANALYSIS / "phase3_top_deviation_features_by_target.csv", index=False)
    unusual.to_csv(ANALYSIS / "phase3_unusual_days_top.csv", index=False)
    event_out.to_csv(ANALYSIS / "phase3_long_rest_event_rows.csv", index=False)
    event_counts.to_csv(ANALYSIS / "phase3_long_rest_event_counts.csv", index=False)
    event_rates.to_csv(ANALYSIS / "phase3_long_rest_label_rates.csv", index=False)
    event_subject_rates.to_csv(ANALYSIS / "phase3_long_rest_by_subject_rates.csv", index=False)
    q2_transition.to_csv(ANALYSIS / "phase3_q2_transition_long_rest_table.csv", index=False)
    gps_summary.to_csv(ANALYSIS / "phase3_gps_precision_home_summary.csv", index=False)
    gps_daily.to_csv(ANALYSIS / "phase3_gps_daily_home_precision.csv", index=False)
    gps_label_link.to_csv(ANALYSIS / "phase3_gps_home_label_link.csv", index=False)
    clusters.to_csv(ANALYSIS / "phase3_lifestyle_clusters.csv", index=False)
    cluster_profile.to_csv(ANALYSIS / "phase3_lifestyle_cluster_profiles.csv", index=False)
    cluster_rates.to_csv(ANALYSIS / "phase3_lifestyle_cluster_target_rates.csv", index=False)
    subj_cluster.to_csv(ANALYSIS / "phase3_subject_cluster_label_summary.csv", index=False)

    make_figures(summary, qshape, dev_signal, event_out, gps_summary, clusters, cluster_rates)

    # Pull key numbers for reports
    q1_spread = summary[["subject_id", "prev_Q1"]].sort_values("prev_Q1")
    q2_dev = dev_signal[dev_signal.label.eq("Q2")].sort_values("high_minus_low", ascending=False).head(8)
    q3_dev = dev_signal[dev_signal.label.eq("Q3")].sort_values("high_minus_low", ascending=False).head(5)
    q1_dev = dev_signal[dev_signal.label.eq("Q1")].sort_values("high_minus_low", ascending=False).head(5)
    focus_summary = summary[summary.subject_id.isin(FOCUS_SUBJECTS)]
    id06_events = event_out[event_out.subject_id.eq("id06")][["subject_id","lifelog_date","long_rest_proxy_h","event_class","Q1","Q2","Q3","S1","S2","S3","S4"]].sort_values("long_rest_proxy_h", ascending=False).head(12)
    gps_focus = gps_summary[gps_summary.subject_id.isin(["id09","id10"])].sort_values(["subject_id","precision"])

    def md_table(d, n=10):
        return d.head(n).round(4).to_markdown(index=False)

    write_md(ANALYSIS / "phase3_A_subject_label_language.md", "Phase 3A — Subject-specific label language map", f"""
## 핵심 요약

- Q1은 전역 label이라기보다 subject별 personal anchor 성격을 강하게 보인다. subject별 Q1 prevalence 범위가 `{q1_spread.prev_Q1.min():.3f} ~ {q1_spread.prev_Q1.max():.3f}`이다.
- Q3는 subject마다 Q1형/anchor형인지 Q2형/event형인지 갈린다. 따라서 Q-family를 한 덩어리로 두면 안 된다.
- S2는 S1/S3/S4 majority와 충돌하는 row가 subject별로 다르게 나타난다. single S-latent로 S2를 크게 움직이는 것은 위험하다.

## Focus subjects

{md_table(focus_summary, 10)}

## Q3 shape by subject

{md_table(qshape, 12)}

## S2 contradiction by subject

{md_table(s2.sort_values('s2_contradiction_rate', ascending=False), 12)}

## 산출물

- `analysis/phase3_subject_label_language_long.csv`
- `analysis/phase3_subject_pair_relations.csv`
- `analysis/phase3_subject_label_language_summary.csv`
- `analysis/phase3_q3_shape_by_subject.csv`
- `analysis/phase3_s2_contradiction_by_subject.csv`
- `analysis/figures/p3_A_subject_label_prevalence.png`
- `analysis/figures/p3_A_q3_shape_by_subject.png`
""")

    write_md(ANALYSIS / "phase3_B_day_deviation.md", "Phase 3B — Day deviation model", f"""
## 핵심 요약

- raw value보다 `__subj_z` 기반의 subject-normalized deviation을 사용했다.
- Q2에서 high-deviation day와 low-deviation day의 label-rate 차이가 가장 해석 가능한 후보를 만든다.
- Q1은 personal anchor가 강하므로 deviation signal이 보여도 negative-control 없이 크게 쓰면 안 된다.

## Q2 deviation family signal 상위

{md_table(q2_dev, 10)}

## Q3 deviation family signal 상위

{md_table(q3_dev, 10)}

## Q1 deviation family signal 상위 — anchor/허위 signal 가능성 주의

{md_table(q1_dev, 10)}

## 가장 unusual한 subject-days

{md_table(unusual[["subject_id","lifelog_date","dev_overall"] + [c for c in unusual.columns if c.startswith('dev_')][:5]], 12)}

## 해석

- 이 분석은 “그 사람답지 않은 날”이 target과 연결되는지를 보기 위한 것이다.
- 향후 모델 번역 시 Q2는 event/deviation residual 후보, Q1은 subject anchor 이후 매우 작은 residual, S-family는 freeze/작은 cap이 기본이다.

## 산출물

- `analysis/phase3_day_deviation_scores.csv`
- `analysis/phase3_day_deviation_target_signal.csv`
- `analysis/phase3_top_deviation_features_by_target.csv`
- `analysis/phase3_unusual_days_top.csv`
- `analysis/figures/p3_B_deviation_signal_heatmap.png`
""")

    write_md(ANALYSIS / "phase3_C_long_rest_event.md", "Phase 3C — Long-rest / vacation event study", f"""
## 핵심 요약

- long-rest proxy 후보: `{', '.join(long_rest_cols)}`.
- 12h+ long-rest는 system anomaly로 제거하기보다 subject-specific behavior event 후보로 보는 것이 안전하다.
- 특히 id06의 long-rest row는 Q2/Q3 event grammar와 연결될 가능성이 있어 별도 추적 대상이다.

## Long-rest event counts by subject

{md_table(event_counts, 12)}

## Event class label rates

{md_table(event_rates, 10)}

## Q2 transition x long-rest proxy

{md_table(q2_transition, 10)}

## id06 top long-rest rows

{md_table(id06_events, 12)}

## 해석

- `long_rest`, `pre_long_rest`, `post_long_rest`를 분리했으므로, Q2가 피로 누적/회복/휴식 이벤트 중 어디에 반응하는지 다음 단계에서 더 볼 수 있다.
- row 수가 작기 때문에 CV 세 번째 자리식 판단보다 event direction과 subject 반복성을 우선한다.

## 산출물

- `analysis/phase3_long_rest_event_rows.csv`
- `analysis/phase3_long_rest_event_counts.csv`
- `analysis/phase3_long_rest_label_rates.csv`
- `analysis/phase3_long_rest_by_subject_rates.csv`
- `analysis/phase3_q2_transition_long_rest_table.csv`
- `analysis/figures/p3_C_long_rest_counts.png`
""")

    write_md(ANALYSIS / "phase3_D_gps_archaeology_v2.md", "Phase 3D — GPS archaeology v2", f"""
## 핵심 요약

- GPS dominant-cell share를 rounding precision 2~5로 다시 계산했다.
- id09와 id10은 같은 “low home”처럼 보여도 다르게 처리해야 한다. id09는 좌표 precision/noise 문제일 가능성, id10은 실제 nomad regime 가능성이 핵심이다.
- precision 변화에 따라 dominant-cell share가 회복되면 noise-splitting, precision을 낮춰도 낮으면 nomad/multi-place 생활로 해석한다.

## id09/id10 precision summary

{md_table(gps_focus, 20)}

## GPS home share와 target link

{md_table(gps_label_link.sort_values(['label','precision']), 20)}

## 해석

- id09는 corrected home-stay / location entropy feature를 재계산할 후보이다.
- id10은 home-stay ratio보다 mobility radius, dominant-place stability, sleep-location consistency 같은 nomad-aware feature가 더 적절하다.
- sparse GPS/context는 subject fingerprint 위험이 있으므로 subject-debiased 또는 within-subject 검증을 통과해야 한다.

## 산출물

- `analysis/phase3_gps_precision_home_summary.csv`
- `analysis/phase3_gps_daily_home_precision.csv`
- `analysis/phase3_gps_home_label_link.csv`
- `analysis/figures/p3_D_gps_home_recovery.png`
""")

    write_md(ANALYSIS / "phase3_E_cluster_validation.md", "Phase 3E — Cluster-aware validation sketch", f"""
## 핵심 요약

- subject-level lifestyle profile을 KMeans(k=3)로 나눴다. 목적은 점수 개선이 아니라 feature 의미가 cluster마다 달라지는지 확인하는 것이다.
- cluster별 target prevalence가 다르면 단일 global residual보다 cluster-aware cap/calibration이 더 안전하다.
- 단, subject가 10명뿐이라 cluster별 별도 대형 모델은 과적합 위험이 크다.

## Subject cluster assignment

{md_table(subj_cluster, 12)}

## Cluster target rates

{md_table(cluster_rates, 10)}

## 해석

- 권장 구조는 `global anchor + cluster-aware residual/cap`이다.
- id08 같은 outlier는 포함/제외 sensitivity를 별도 확인해야 한다.
- id10 nomad cluster는 home-based feature를 약화하고 mobility/stability feature 중심으로 해석해야 한다.

## 산출물

- `analysis/phase3_lifestyle_clusters.csv`
- `analysis/phase3_lifestyle_cluster_profiles.csv`
- `analysis/phase3_lifestyle_cluster_target_rates.csv`
- `analysis/phase3_subject_cluster_label_summary.csv`
- `analysis/figures/p3_E_cluster_target_prevalence.png`
""")

    # Index report
    write_md(ANALYSIS / "phase3_index.md", "Phase 3 — Subject language + day deviation research index", f"""
## 이번 Phase 3의 질문

Phase 1+2의 결론을 바탕으로, 이번에는 **subject-specific label language**와 **day-level deviation/event grammar**를 직접 확인했다.

> working hypothesis: `label = personal anchor + lifestyle/static regime + day-level deviation/event + observation process + Q/S별 measurement language`

## 트랙별 보고서

1. `analysis/phase3_A_subject_label_language.md` — subject별 label prevalence/entropy/persistence/correlation, Q3 shape, S2 contradiction
2. `analysis/phase3_B_day_deviation.md` — subject-normalized deviation family와 target 연결
3. `analysis/phase3_C_long_rest_event.md` — 12h+ long-rest / pre/post event study
4. `analysis/phase3_D_gps_archaeology_v2.md` — GPS rounding precision별 home 회복, id09/id10 분리
5. `analysis/phase3_E_cluster_validation.md` — lifestyle cluster별 target prevalence와 validation sketch

## 핵심 판정

- **Q1:** subject-specific personal anchor 성격이 강하다. coverage/deviation signal을 바로 쓰지 말고 residual cap을 작게 둔다.
- **Q2:** day-deviation/event signal을 가장 먼저 번역할 target이다. long-rest/coverage/context/routine deviation을 우선 추적한다.
- **Q3:** subject별로 Q1형과 Q2형 힌트가 갈린다. Q2 event와 동조하는지 추가 확인 후 움직인다.
- **S-family:** lifestyle/static regime 성격이 강하다. 큰 movement 금지.
- **S2:** S-family 안에서 contradiction/autopsy 대상. latent-based move 금지.
- **GPS:** id09는 correction, id10은 nomad regime. 같은 low-home feature로 묶으면 안 된다.

## 모델 번역 메모

- Q2 cap: `0.08~0.12` 후보.
- Q3 cap: Q2 event 동조 근거가 있을 때 `0.03~0.06`.
- Q1 cap: `0.00~0.03`, coverage gating 금지.
- S1/S2/S3: freeze 기본.
- S4: corrected context/GPS가 subject-debiased 검증을 통과할 때만 `0.00~0.05`.

## 생성된 figure

- `analysis/figures/p3_A_subject_label_prevalence.png`
- `analysis/figures/p3_A_q3_shape_by_subject.png`
- `analysis/figures/p3_B_deviation_signal_heatmap.png`
- `analysis/figures/p3_C_long_rest_counts.png`
- `analysis/figures/p3_D_gps_home_recovery.png`
- `analysis/figures/p3_E_cluster_target_prevalence.png`
""")

    print("Phase 3 analysis complete")
    print("Reports written under", ANALYSIS)

if __name__ == "__main__":
    main()
