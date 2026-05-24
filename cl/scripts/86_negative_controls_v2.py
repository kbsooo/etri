"""Axis 3 — Negative controls v2.

For each target, run a small model and compare logloss vs the same model on
randomized data. If the randomized control matches the real model, the signal
is artifact (subject/coverage/static) not day-varying behavior.

Controls:
  C0_real                — actual labels, actual features (baseline)
  C1_within_subject_perm  — labels shuffled WITHIN each subject (preserves
                             subject prevalence, breaks day-level signal)
  C2_date_shifted_feats   — features shifted by +7 days per subject
                             (preserves marginal feature dist, breaks per-day match)
  C3_coverage_only        — only coverage features + subject dummies
  C4_subject_only         — only subject dummies
  C5_fake_target          — random Bernoulli at per-subject rate

Models tested (kept identical across controls so the gap = info, not capacity):
  M_subj_tokens : subject dummies + S8 context tokens (the 5 Q2 survivors)
  M_subj_cov    : subject dummies + top-15 coverage features

Output:
  experiments/axis3_negative_controls_report.md
  experiments/axis3_negative_controls_results.csv

Mirror_v1 fold, 3 seeds.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.cl_common import LABELS, logloss  # noqa: E402

TRAIN_CSV = ROOT / "data" / "ch2026_metrics_train.csv"
MIRROR = ROOT / "outputs" / "validation" / "folds_subject_mirror_v1.json"
COV_PARQ = ROOT / "features" / "observation_coverage_features.parquet"
IDENT_PARQ = ROOT / "features" / "observation_identity_token_features.parquet"
REPORT_MD = ROOT / "experiments" / "axis3_negative_controls_report.md"
RESULTS_CSV = ROOT / "experiments" / "axis3_negative_controls_results.csv"

SURVIVING_TOKENS = [
    "usage_app_name:카카오 T",
    "wifi_bssid:b4:a9:4f:3f:32:5b",
    "wifi_bssid:60:29:d5:4a:47:d3",
    "usage_app_name:Google Play 서비스",
    "usage_app_name:LG ThinQ",
]


def load_all():
    tr = pd.read_csv(TRAIN_CSV)
    tr["lifelog_date"] = pd.to_datetime(tr["lifelog_date"]).dt.date.astype(str)
    cov = pd.read_parquet(COV_PARQ)
    if "date" in cov.columns:
        cov = cov.rename(columns={"date": "lifelog_date"})
    cov["lifelog_date"] = pd.to_datetime(cov["lifelog_date"]).dt.date.astype(str)
    ident = pd.read_parquet(IDENT_PARQ)
    if "date" in ident.columns:
        ident = ident.rename(columns={"date": "lifelog_date"})
    ident["lifelog_date"] = pd.to_datetime(ident["lifelog_date"]).dt.date.astype(str)
    return tr, cov, ident


def split_by_fold(df: pd.DataFrame, fold: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    idx = {(r.subject_id, r.lifelog_date): i for i, r in df.reset_index(drop=True).iterrows()}
    tr_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["train_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    va_i = [idx[(k["subject_id"], k["lifelog_date"])] for k in fold["valid_keys"] if (k["subject_id"], k["lifelog_date"]) in idx]
    return df.iloc[tr_i].copy(), df.iloc[va_i].copy()


def fit_score(Xtr, ytr, Xva, yva):
    if ytr.std() < 1e-6 or Xtr.shape[1] == 0:
        p = np.full(len(yva), float(ytr.mean()))
        return logloss(yva, np.clip(p, 0.03, 0.97))
    means = np.nanmean(Xtr, axis=0)
    means[np.isnan(means)] = 0.0
    Xtr_i = np.where(np.isnan(Xtr), means, Xtr)
    Xva_i = np.where(np.isnan(Xva), means, Xva)
    sc = StandardScaler().fit(Xtr_i)
    Xtr_s, Xva_s = sc.transform(Xtr_i), sc.transform(Xva_i)
    clf = LogisticRegression(C=0.5, max_iter=2000)
    clf.fit(Xtr_s, ytr)
    p = np.clip(clf.predict_proba(Xva_s)[:, 1], 0.03, 0.97)
    return float(logloss(yva, p))


def get_subj_dummies(train, valid):
    sd = pd.get_dummies(pd.concat([train["subject_id"], valid["subject_id"]]), prefix="subj", drop_first=True).astype(float)
    return sd.iloc[:len(train)].reset_index(drop=True), sd.iloc[len(train):].reset_index(drop=True)


def get_tokens(train, valid, ident):
    present = [t for t in SURVIVING_TOKENS if t in ident.columns]
    if not present:
        return pd.DataFrame(), pd.DataFrame()
    join = ["subject_id", "lifelog_date"]
    tr = train[join].merge(ident[join + present], on=join, how="left").drop(columns=join).reset_index(drop=True)
    va = valid[join].merge(ident[join + present], on=join, how="left").drop(columns=join).reset_index(drop=True)
    return tr, va


def get_top_cov(train, valid, cov, target, k=15):
    join = ["subject_id", "lifelog_date"]
    nums = [c for c in cov.columns if c not in join + ["split"] and pd.api.types.is_numeric_dtype(cov[c])]
    tr_full = train[join].merge(cov[join + nums], on=join, how="left").drop(columns=join).fillna(0.0)
    va_full = valid[join].merge(cov[join + nums], on=join, how="left").drop(columns=join).fillna(0.0)
    y = train[target].astype(int).values
    if y.std() < 1e-6 or tr_full.shape[1] == 0:
        return pd.DataFrame(), pd.DataFrame()
    sel = SelectKBest(f_classif, k=min(k, tr_full.shape[1])).fit(tr_full.to_numpy(dtype=float), y)
    chosen = tr_full.columns[sel.get_support()].tolist()
    return tr_full[chosen].reset_index(drop=True), va_full[chosen].reset_index(drop=True)


def within_subject_permute(train, target, rng):
    """Shuffle target labels within each subject. Preserves subject prevalence."""
    out = train.copy()
    new_y = train[target].astype(int).values.copy()
    for s in train["subject_id"].unique():
        mask = (train["subject_id"] == s).values
        idx = np.where(mask)[0]
        perm = rng.permutation(idx)
        new_y[idx] = train[target].values[perm]
    out[target] = new_y
    return out


def date_shift_features(train, valid, feature_tr, feature_va, days=7):
    """Shift the feature row by +days per subject. This means for subject s,
    each row's features are replaced by the features of (s, date+days)."""
    train = train.reset_index(drop=True)
    valid = valid.reset_index(drop=True)
    feature_tr = feature_tr.reset_index(drop=True)
    feature_va = feature_va.reset_index(drop=True)
    # build lookup: (subject, date) -> feature row index in train
    key_to_idx_tr = {(s, d): i for i, (s, d) in enumerate(zip(train["subject_id"], train["lifelog_date"]))}
    new_idx_tr = []
    for s, d in zip(train["subject_id"], train["lifelog_date"]):
        d2 = (pd.to_datetime(d) + pd.Timedelta(days=days)).date().isoformat()
        new_idx_tr.append(key_to_idx_tr.get((s, d2), key_to_idx_tr[(s, d)]))
    new_idx_va = []
    for s, d in zip(valid["subject_id"], valid["lifelog_date"]):
        d2 = (pd.to_datetime(d) + pd.Timedelta(days=days)).date().isoformat()
        # if shifted date isn't in valid, just take original valid row
        new_idx_va.append(None)
    shifted_tr = feature_tr.iloc[new_idx_tr].reset_index(drop=True)
    # for valid, shift inside valid as well
    key_to_idx_va = {(s, d): i for i, (s, d) in enumerate(zip(valid["subject_id"], valid["lifelog_date"]))}
    new_va_idx = []
    for s, d in zip(valid["subject_id"], valid["lifelog_date"]):
        d2 = (pd.to_datetime(d) + pd.Timedelta(days=days)).date().isoformat()
        new_va_idx.append(key_to_idx_va.get((s, d2), key_to_idx_va[(s, d)]))
    shifted_va = feature_va.iloc[new_va_idx].reset_index(drop=True)
    return shifted_tr, shifted_va


def fake_target(train, target, rng):
    out = train.copy()
    new_y = np.empty(len(train), dtype=int)
    for s in train["subject_id"].unique():
        mask = (train["subject_id"] == s).values
        p = float(train.loc[mask, target].mean())
        new_y[mask] = (rng.random(mask.sum()) < p).astype(int)
    out[target] = new_y
    return out


def df_to_md(df):
    cols = list(df.columns)
    idx_name = df.index.name or ""
    head = "| " + " | ".join([idx_name, *map(str, cols)]) + " |"
    sep = "|" + "|".join(["---"] * (1 + len(cols))) + "|"
    lines = [head, sep]
    for ix, row in df.iterrows():
        cells = [str(ix)] + [f"{v:.4f}" if isinstance(v, (int, float, np.floating)) and not pd.isna(v) else str(v) for v in row.tolist()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main():
    df, cov, ident = load_all()
    cfg = json.loads(MIRROR.read_text())
    rng = np.random.default_rng(0)
    rows = []

    for fold in cfg["folds"]:
        train, valid = split_by_fold(df, fold)
        if len(valid) == 0:
            continue
        sd_tr, sd_va = get_subj_dummies(train, valid)
        tok_tr, tok_va = get_tokens(train, valid, ident)

        for target in LABELS:
            yva = valid[target].astype(int).to_numpy()
            cov_tr, cov_va = get_top_cov(train, valid, cov, target, k=15)

            # M_subj_tokens
            Xtr_st = pd.concat([sd_tr, tok_tr], axis=1)
            Xva_st = pd.concat([sd_va, tok_va], axis=1)

            # M_subj_cov
            Xtr_sc = pd.concat([sd_tr, cov_tr], axis=1) if not cov_tr.empty else sd_tr
            Xva_sc = pd.concat([sd_va, cov_va], axis=1) if not cov_va.empty else sd_va

            for model_name, (Xtr_m, Xva_m) in [("subj_tokens", (Xtr_st, Xva_st)), ("subj_cov", (Xtr_sc, Xva_sc))]:
                # C0 real
                ytr_real = train[target].astype(int).to_numpy()
                ll = fit_score(Xtr_m.to_numpy(dtype=float, na_value=0.0), ytr_real, Xva_m.to_numpy(dtype=float, na_value=0.0), yva)
                rows.append({"fold": fold.get("name"), "target": target, "model": model_name, "control": "C0_real", "logloss": ll})

                # C1 within-subject permute (multiple seeds)
                for seed in (0, 1, 2):
                    perm_rng = np.random.default_rng(100 + seed)
                    perm = within_subject_permute(train, target, perm_rng)
                    ytr_perm = perm[target].astype(int).to_numpy()
                    ll = fit_score(Xtr_m.to_numpy(dtype=float, na_value=0.0), ytr_perm, Xva_m.to_numpy(dtype=float, na_value=0.0), yva)
                    rows.append({"fold": fold.get("name"), "target": target, "model": model_name, "control": f"C1_within_subj_perm_seed{seed}", "logloss": ll})

                # C2 date-shifted features (real labels, shifted features)
                if not (tok_tr.empty if model_name == "subj_tokens" else cov_tr.empty):
                    base_tr = tok_tr if model_name == "subj_tokens" else cov_tr
                    base_va = tok_va if model_name == "subj_tokens" else cov_va
                    shifted_tr, shifted_va = date_shift_features(train, valid, base_tr, base_va, days=7)
                    Xtr_shift = pd.concat([sd_tr, shifted_tr], axis=1)
                    Xva_shift = pd.concat([sd_va, shifted_va], axis=1)
                    ll = fit_score(Xtr_shift.to_numpy(dtype=float, na_value=0.0), ytr_real, Xva_shift.to_numpy(dtype=float, na_value=0.0), yva)
                    rows.append({"fold": fold.get("name"), "target": target, "model": model_name, "control": "C2_date_shifted_feats", "logloss": ll})

                # C5 fake-target (random Bernoulli at per-subject rate)
                for seed in (0, 1):
                    fake = fake_target(train, target, np.random.default_rng(200 + seed))
                    ytr_fake = fake[target].astype(int).to_numpy()
                    ll = fit_score(Xtr_m.to_numpy(dtype=float, na_value=0.0), ytr_fake, Xva_m.to_numpy(dtype=float, na_value=0.0), yva)
                    rows.append({"fold": fold.get("name"), "target": target, "model": model_name, "control": f"C5_fake_target_seed{seed}", "logloss": ll})

            # subject-only & coverage-only as global controls
            ll_subj = fit_score(sd_tr.to_numpy(dtype=float, na_value=0.0), train[target].astype(int).to_numpy(), sd_va.to_numpy(dtype=float, na_value=0.0), yva)
            rows.append({"fold": fold.get("name"), "target": target, "model": "subject_only", "control": "C4_subject_only", "logloss": ll_subj})
            if not cov_tr.empty:
                ll_cov = fit_score(cov_tr.to_numpy(dtype=float, na_value=0.0), train[target].astype(int).to_numpy(), cov_va.to_numpy(dtype=float, na_value=0.0), yva)
                rows.append({"fold": fold.get("name"), "target": target, "model": "coverage_only", "control": "C3_coverage_only", "logloss": ll_cov})

            print(f"{fold.get('name'):16s} {target} done")

    res = pd.DataFrame(rows)
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(RESULTS_CSV, index=False)
    print(f"wrote {RESULTS_CSV}")

    # aggregate
    res["control_group"] = res["control"].str.split("_seed").str[0]
    agg = res.groupby(["model", "target", "control_group"])["logloss"].mean().round(4).reset_index()

    lines = []
    lines.append("# Axis 3 — Negative controls\n")
    lines.append(
        "Each model is scored on real labels (C0) and on multiple null controls.\n"
        "If a control's logloss is close to C0_real, the model's apparent skill\n"
        "is not day-varying signal — it is captured by subject or static context.\n"
    )

    for model in ["subj_tokens", "subj_cov"]:
        sub = agg[agg["model"] == model]
        if sub.empty:
            continue
        pivot = sub.pivot(index="control_group", columns="target", values="logloss").round(4)
        pivot["Tavg"] = pivot.mean(axis=1).round(4)
        lines.append(f"\n## Model: {model}\n")
        lines.append(df_to_md(pivot))

    # global controls
    sub = agg[agg["model"].isin(["subject_only", "coverage_only"])]
    if not sub.empty:
        pivot = sub.pivot_table(index="model", columns="target", values="logloss").round(4)
        pivot["Tavg"] = pivot.mean(axis=1).round(4)
        lines.append("\n## Global controls (no token / no cov mixed)\n")
        lines.append(df_to_md(pivot))

    # gap between real and within-subject perm (the key diagnostic)
    lines.append("\n## Gap: C0_real − C1_within_subject_perm (negative = real model worse than perm)\n")
    lines.append("If close to 0, model has no day-level signal beyond subject prevalence.\n")
    for model in ["subj_tokens", "subj_cov"]:
        sub = agg[agg["model"] == model]
        if sub.empty:
            continue
        pv = sub.pivot(index="control_group", columns="target", values="logloss")
        if "C0_real" in pv.index and "C1_within_subj_perm" in pv.index:
            gap = (pv.loc["C0_real"] - pv.loc["C1_within_subj_perm"]).round(4).to_frame(f"{model}: real − perm").T
            lines.append(df_to_md(gap))

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
