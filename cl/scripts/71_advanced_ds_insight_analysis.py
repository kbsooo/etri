#!/usr/bin/env python3
"""Advanced data-science insight analysis for the CH2026 lifelog sleep task.

Focus: understand latent label regimes, feature-family signal, and observable
mechanisms. This script intentionally avoids producing submission files.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import warnings
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler, StandardScaler

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXP = ROOT / "experiments"
SCRIPTS = ROOT / "scripts"
EXP.mkdir(exist_ok=True)
LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
IDS = ["subject_id", "sleep_date", "lifelog_date"]

spec = importlib.util.spec_from_file_location("big67", SCRIPTS / "67_big_swing_all_experiments.py")
big67 = importlib.util.module_from_spec(spec)
sys.modules["big67"] = big67
spec.loader.exec_module(big67)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def safe_logloss(y, p):
    p = np.clip(np.asarray(p, float), 0.02, 0.98)
    return log_loss(np.asarray(y, int), p, labels=[0, 1])


def entropy_binary(p):
    p = np.clip(np.asarray(p, float), 1e-9, 1 - 1e-9)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def logsumexp(a, axis=1):
    m = np.max(a, axis=axis, keepdims=True)
    return m + np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True))


def fit_bernoulli_mixture(X, ks=range(2, 6), seeds=range(30), beta=0.5, max_iter=500, tol=1e-8):
    X = np.asarray(X, float)
    n, d = X.shape
    best = None
    rows = []
    for K in ks:
        for seed in seeds:
            rng = np.random.default_rng(seed + 1000 * K)
            # Start around real rows plus jitter to avoid symmetric states.
            centers = X[rng.choice(n, size=K, replace=False)].astype(float)
            p = np.clip(0.12 + 0.76 * centers + rng.normal(0, 0.08, size=(K, d)), 0.05, 0.95)
            pi = np.ones(K) / K
            prev_ll = -np.inf
            for it in range(max_iter):
                lp = np.log(pi + 1e-12)[None, :] + X @ np.log(p + 1e-12).T + (1 - X) @ np.log(1 - p + 1e-12).T
                lse = logsumexp(lp, axis=1)
                r = np.exp(lp - lse)
                ll = float(lse.sum())
                nk = r.sum(axis=0) + 1e-12
                pi = nk / n
                p = (r.T @ X + beta) / (nk[:, None] + 2 * beta)
                p = np.clip(p, 0.03, 0.97)
                if abs(ll - prev_ll) < tol * max(1, abs(prev_ll)):
                    break
                prev_ll = ll
            params = (K - 1) + K * d
            bic = -2 * ll + params * math.log(n)
            rows.append({"K": K, "seed": seed, "loglik": ll, "bic": bic, "iter": it + 1})
            if best is None or bic < best["bic"]:
                best = {"K": K, "pi": pi.copy(), "p": p.copy(), "resp": r.copy(), "loglik": ll, "bic": bic, "seed": seed}
    return best, pd.DataFrame(rows).sort_values("bic")


def sort_states_by_profile(pi, p, resp):
    # Sort states by broad severity: S-family then Q-family prevalence.
    severity = p[:, [LABELS.index(x) for x in ["S1", "S2", "S3", "S4", "Q2", "Q3", "Q1"]]].mean(axis=1)
    order = np.argsort(severity)
    inv = np.zeros_like(order)
    inv[order] = np.arange(len(order))
    return pi[order], p[order], resp[:, order], inv


def temporal_smooth(known, query, target, tau=14, alpha=5, future=True):
    y = known[target].astype(float).to_numpy()
    g = float(np.mean(y))
    out = np.zeros(len(query), float)
    for sid, qsub in query.groupby("subject_id"):
        k = known[known.subject_id.astype(str).eq(str(sid))]
        if len(k) == 0:
            out[query.index.get_indexer(qsub.index)] = g
            continue
        kd = k.sleep_date.values.astype("datetime64[D]").astype(int)
        qd = qsub.sleep_date.values.astype("datetime64[D]").astype(int)
        dist = np.abs(qd[:, None] - kd[None, :]).astype(float)
        if not future:
            dist = np.where(kd[None, :] < qd[:, None], dist, np.inf)
        w = np.exp(-dist / tau)
        w[~np.isfinite(w)] = 0
        p = (w @ k[target].astype(float).to_numpy() + alpha * g) / (w.sum(axis=1) + alpha)
        out[query.index.get_indexer(qsub.index)] = np.clip(p, 0.02, 0.98)
    return out


def make_interleaved_masks(train, sample, seeds=range(4)):
    masks = []
    n = len(train)
    for seed in seeds:
        rng = np.random.default_rng(700 + seed)
        mask = np.zeros(n, bool)
        for sid, sub in train.groupby("subject_id"):
            sub = sub.sort_values("sleep_date")
            tst = sample[sample.subject_id == sid].sort_values("sleep_date")
            all_dates = pd.concat([
                sub[["sleep_date"]].assign(kind="train"),
                tst[["sleep_date"]].assign(kind="test"),
            ]).sort_values("sleep_date").reset_index(drop=True)
            test_fracs = all_dates.index[all_dates.kind.eq("test")].to_numpy() / max(1, len(all_dates) - 1)
            ranks = np.linspace(0, 1, len(sub))
            prob = np.ones(len(sub)) * 0.05
            for f in test_fracs:
                prob += np.exp(-0.5 * ((ranks - f) / 0.10) ** 2)
            prob = prob / prob.sum()
            size = min(len(sub) - 2, max(3, len(tst)))
            chosen = rng.choice(sub.index.to_numpy(), size=size, replace=False, p=prob)
            mask[train.index.get_indexer(chosen)] = True
        masks.append((f"adv_interleaved_rank{seed}", mask, True, "interleaved_rank"))
    return masks


def family_of_col(c):
    c = c.lower()
    rules = [
        ("ssl", ["ssl", "dino", "ae_", "cluster", "proto"]),
        ("sleep_episode", ["sleep", "psw", "s4x", "q1qual", "q2lr", "crossnight", "cn_"]),
        ("screen_phone", ["screen", "usage", "app_"]),
        ("activity_steps", ["step", "pedo", "activity"]),
        ("heart_light", ["hr_", "heartrate", "light"]),
        ("location_context", ["gps", "wifi", "ble", "amb", "place"]),
        ("routine_axes", ["routine", "axis_", "human_"]),
        ("hourly_shape", ["_h", "h00", "h01", "h02", "h03", "h04", "h05", "h06", "h07", "h08", "h09", "h10", "h11", "h12", "h13", "h14", "h15", "h16", "h17", "h18", "h19", "h20", "h21", "h22", "h23"]),
    ]
    for name, toks in rules:
        if any(t in c for t in toks):
            return name
    return "other_numeric"


def feature_cols(df, max_cols=1200):
    return big67.numeric_cols(
        df,
        contains=("sleep", "quiet", "screen", "steps", "activity", "hr_", "gps_", "app_", "wifi_", "ble_", "amb_", "axis_", "human_", "psw", "s4x", "q1qual", "q2lr", "ssl", "dino", "ae_", "cluster", "routine", "light"),
        max_cols=max_cols,
    )


def fit_predict_family(df, cols, target, train_mask, val_mask, k=60, C=0.05):
    cols = [c for c in cols if c in df.columns]
    y = df.loc[train_mask, target].astype(int).to_numpy()
    if len(cols) < 2 or len(np.unique(y)) < 2:
        return np.repeat(float(np.mean(y)), int(val_mask.sum()))
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sel", SelectKBest(f_classif, k=min(k, len(cols)))),
        ("scale", RobustScaler()),
        ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
    ])
    pipe.fit(df.loc[train_mask, cols], y)
    return np.clip(pipe.predict_proba(df.loc[val_mask, cols])[:, 1], 0.02, 0.98)


def state_predictability(df, train, sample, cols, states):
    # Multi-class state prediction under masks similar to the actual split.
    masks = []
    masks += [(name, mask, future, "testpattern") for name, mask, future in big67.make_testpattern_masks(train, sample, seeds=range(4))]
    masks += make_interleaved_masks(train, sample, seeds=range(4))
    rows = []
    y_state = pd.Series(states, index=train.index)
    for name, mask, future, scheme in masks:
        trm = ~mask
        vam = mask
        ytr = y_state.loc[trm].to_numpy()
        yva = y_state.loc[vam].to_numpy()
        if len(np.unique(ytr)) < 2:
            continue
        pipe = Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sel", SelectKBest(f_classif, k=min(120, len(cols)))),
            ("scale", RobustScaler()),
            ("clf", LogisticRegression(C=0.08, solver="lbfgs", max_iter=2000, random_state=42)),
        ])
        pipe.fit(train.loc[trm, cols], ytr)
        classes = pipe.named_steps["clf"].classes_
        proba_raw = pipe.predict_proba(train.loc[vam, cols])
        # Align to all classes.
        K = int(states.max() + 1)
        proba = np.ones((vam.sum(), K)) * (1e-6)
        for j, cls in enumerate(classes):
            proba[:, int(cls)] = proba_raw[:, j]
        proba = proba / proba.sum(axis=1, keepdims=True)
        pred = proba.argmax(axis=1)
        rows.append({
            "mask": name,
            "scheme": scheme,
            "n": int(vam.sum()),
            "accuracy": float(accuracy_score(yva, pred)),
            "balanced_accuracy": float(balanced_accuracy_score(yva, pred)),
            "state_logloss": float(log_loss(yva, proba, labels=list(range(K)))),
            "majority_acc": float(pd.Series(ytr).value_counts(normalize=True).max()),
        })
    return pd.DataFrame(rows)


def feature_separators(df, train, cols, states, topn=160):
    # State-vs-rest standardized mean differences, more interpretable than model coefficients.
    imp = SimpleImputer(strategy="median")
    X = imp.fit_transform(train[cols])
    sc = StandardScaler()
    Xz = sc.fit_transform(X)
    rows = []
    K = int(states.max() + 1)
    for k in range(K):
        in_state = states == k
        if in_state.sum() < 8 or (~in_state).sum() < 8:
            continue
        diff = Xz[in_state].mean(axis=0) - Xz[~in_state].mean(axis=0)
        idx = np.argsort(np.abs(diff))[::-1][:topn]
        for rank, j in enumerate(idx, 1):
            rows.append({
                "state": int(k),
                "rank": rank,
                "feature": cols[j],
                "family": family_of_col(cols[j]),
                "std_mean_diff": float(diff[j]),
                "direction": "higher_in_state" if diff[j] > 0 else "lower_in_state",
            })
    return pd.DataFrame(rows)


def family_target_signal(df, train, sample, cols):
    # Coarse, mechanism-level target/family audit under public-like masks.
    masks = [(name, mask, future, "testpattern") for name, mask, future in big67.make_testpattern_masks(train, sample, seeds=range(3))] + make_interleaved_masks(train, sample, seeds=range(3))
    fam_cols = defaultdict(list)
    for c in cols:
        fam_cols[family_of_col(c)].append(c)
    # Keep non-trivial families.
    fam_cols = {k: v[:220] for k, v in fam_cols.items() if len(v) >= 4}
    rows = []
    for name, mask, future, scheme in masks:
        trm = ~mask
        vam = mask
        known = train.loc[trm].copy().reset_index(drop=True)
        val = train.loc[vam].copy().reset_index(drop=True)
        for y in LABELS:
            yva = val[y].astype(int)
            prior = np.repeat(float(known[y].mean()), len(val))
            temp = temporal_smooth(known, val, y, tau=14, alpha=5, future=future)
            rows.append({"mask": name, "scheme": scheme, "target": y, "family": "global_prior", "n_cols": 0, "logloss": safe_logloss(yva, prior)})
            rows.append({"mask": name, "scheme": scheme, "target": y, "family": "same_subject_temporal_label", "n_cols": 0, "logloss": safe_logloss(yva, temp)})
            for fam, fcols in fam_cols.items():
                try:
                    pred = fit_predict_family(train, fcols, y, trm, vam, k=min(70, len(fcols)), C=0.04)
                    rows.append({"mask": name, "scheme": scheme, "target": y, "family": fam, "n_cols": len(fcols), "logloss": safe_logloss(yva, pred)})
                except Exception:
                    continue
    res = pd.DataFrame(rows)
    # improvement vs global prior within same mask/target.
    prior = res[res.family.eq("global_prior")][["mask", "target", "logloss"]].rename(columns={"logloss": "prior_logloss"})
    res = res.merge(prior, on=["mask", "target"], how="left")
    res["improvement_vs_prior"] = res["prior_logloss"] - res["logloss"]
    return res


def main():
    train0 = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    df = big67.load_base_table().sort_values(["is_train", "subject_id", "sleep_date"], ascending=[False, True, True]).reset_index(drop=True)
    train = df[df.is_train.eq(1)].copy().reset_index(drop=True)
    sample_full = df[df.is_train.eq(0)].copy().reset_index(drop=True)

    cols = feature_cols(df, max_cols=1400)
    (EXP / "advanced_ds_feature_inventory.json").write_text(json.dumps({
        "n_cols": len(cols),
        "family_counts": Counter(family_of_col(c) for c in cols),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # 1) Latent label-state discovery.
    Xlab = train[LABELS].astype(int).to_numpy()
    mix, mix_grid = fit_bernoulli_mixture(Xlab)
    pi, p, resp, inv = sort_states_by_profile(mix["pi"], mix["p"], mix["resp"])
    states = resp.argmax(axis=1)
    # states were already sorted because resp sorted; use sorted assignment.
    K = len(pi)
    mix_grid.to_csv(EXP / "advanced_ds_bernoulli_mixture_bic.csv", index=False)
    emission = pd.DataFrame(p, columns=LABELS)
    emission.insert(0, "state", range(K))
    emission["mixing_weight"] = pi
    emission["severity_mean"] = emission[LABELS].mean(axis=1)
    emission.to_csv(EXP / "advanced_ds_latent_state_emissions.csv", index=False)

    state_df = train[IDS + LABELS].copy()
    state_df["latent_state"] = states
    state_df["state_confidence"] = resp.max(axis=1)
    state_df.to_csv(EXP / "advanced_ds_row_latent_states.csv", index=False)

    # Transition matrix and subject occupancy.
    trans = np.zeros((K, K), float)
    run_rows = []
    for sid, sub in state_df.sort_values(["subject_id", "sleep_date"]).groupby("subject_id"):
        arr = sub.latent_state.to_numpy(int)
        if len(arr) > 1:
            for a, b in zip(arr[:-1], arr[1:]):
                trans[a, b] += 1
        cur = arr[0]; l = 1
        for z in arr[1:]:
            if z == cur:
                l += 1
            else:
                run_rows.append({"subject_id": sid, "state": int(cur), "run_len": int(l)})
                cur = z; l = 1
        run_rows.append({"subject_id": sid, "state": int(cur), "run_len": int(l)})
    trans_prob = trans / np.maximum(1, trans.sum(axis=1, keepdims=True))
    pd.DataFrame(trans_prob, index=[f"from_{i}" for i in range(K)], columns=[f"to_{i}" for i in range(K)]).to_csv(EXP / "advanced_ds_latent_state_transition_matrix.csv")
    runs = pd.DataFrame(run_rows)
    runs.to_csv(EXP / "advanced_ds_latent_state_runs.csv", index=False)

    occ = pd.crosstab(state_df.subject_id, state_df.latent_state, normalize="index").reindex(columns=range(K), fill_value=0)
    occ.columns = [f"state_{c}_share" for c in occ.columns]
    subj_targets = train.groupby("subject_id")[LABELS].mean()
    occ = occ.join(subj_targets).reset_index()
    occ.to_csv(EXP / "advanced_ds_subject_state_occupancy.csv", index=False)

    # Entropy / information decomposition.
    info_rows = []
    for y in LABELS:
        py = train[y].mean()
        hy = float(entropy_binary(py))
        cond = 0.0
        for k in range(K):
            w = float((states == k).mean())
            pk = float(train.loc[states == k, y].mean()) if (states == k).sum() else py
            cond += w * float(entropy_binary(pk))
        info_rows.append({"target": y, "H_y_bits": hy, "H_y_given_state_bits": cond, "MI_state_y_bits": hy - cond, "explained_entropy_share": (hy - cond) / hy if hy > 0 else np.nan})
    info = pd.DataFrame(info_rows)
    info.to_csv(EXP / "advanced_ds_state_label_information.csv", index=False)

    # 2) Is latent state observable from sensors/features?
    state_pred = state_predictability(df, train, sample_full, cols, states)
    state_pred.to_csv(EXP / "advanced_ds_latent_state_predictability.csv", index=False)
    separators = feature_separators(df, train, cols, states)
    separators.to_csv(EXP / "advanced_ds_state_feature_separators.csv", index=False)
    sep_family = separators.groupby(["state", "family"]).agg(n_top=("feature", "count"), mean_abs_smd=("std_mean_diff", lambda s: float(np.mean(np.abs(s))))).reset_index().sort_values(["state", "n_top", "mean_abs_smd"], ascending=[True, False, False])
    sep_family.to_csv(EXP / "advanced_ds_state_separator_family_summary.csv", index=False)

    # 3) Feature-family target signal audit.
    family_res = family_target_signal(df, train, sample_full, cols)
    family_res.to_csv(EXP / "advanced_ds_feature_family_signal_raw.csv", index=False)
    fam_summary = family_res.groupby(["scheme", "target", "family"]).agg(
        masks=("mask", "count"),
        mean_logloss=("logloss", "mean"),
        mean_improvement_vs_prior=("improvement_vs_prior", "mean"),
        std_improvement=("improvement_vs_prior", "std"),
    ).reset_index().sort_values(["scheme", "target", "mean_improvement_vs_prior"], ascending=[True, True, False])
    fam_summary.to_csv(EXP / "advanced_ds_feature_family_signal_summary.csv", index=False)

    top_by_target = []
    for (scheme, y), g in fam_summary[~fam_summary.family.eq("global_prior")].groupby(["scheme", "target"]):
        gg = g.sort_values("mean_improvement_vs_prior", ascending=False).head(5)
        for rank, (_, r) in enumerate(gg.iterrows(), 1):
            top_by_target.append({"scheme": scheme, "target": y, "rank": rank, "family": r.family, "mean_improvement_vs_prior": r.mean_improvement_vs_prior, "mean_logloss": r.mean_logloss})
    top_by_target = pd.DataFrame(top_by_target)
    top_by_target.to_csv(EXP / "advanced_ds_top_feature_families_by_target.csv", index=False)

    # 4) Synthesis report.
    best_mix = mix_grid.iloc[0].to_dict()
    avg_state_pred = state_pred.groupby("scheme").agg(
        masks=("mask", "count"),
        acc=("accuracy", "mean"),
        bal_acc=("balanced_accuracy", "mean"),
        state_logloss=("state_logloss", "mean"),
        majority_acc=("majority_acc", "mean"),
    ).reset_index() if len(state_pred) else pd.DataFrame()

    stable_fam = fam_summary.copy()
    stable_fam["robust_score"] = stable_fam["mean_improvement_vs_prior"] - stable_fam["std_improvement"].fillna(0)
    stable_top = stable_fam[~stable_fam.family.isin(["global_prior"])]\
        .sort_values(["target", "robust_score"], ascending=[True, False])\
        .groupby("target").head(6)

    lines = []
    lines += ["# Advanced DS Insight Analysis", ""]
    lines += ["## 0. 질문 재정의", "", "이번 분석은 제출 파일을 만들지 않고, `라벨 생성 구조가 무엇인지`, `그 구조가 센서/행동 feature에서 관측 가능한지`, `target별로 어떤 feature family가 실제 신호를 갖는지`를 보는 분석이다.", ""]
    lines += ["## 1. Latent label-state discovery", "", f"Best Bernoulli mixture: K={int(best_mix['K'])}, BIC={best_mix['bic']:.2f}, loglik={best_mix['loglik']:.2f}", ""]
    lines += ["### State emission probabilities", "", emission.to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["### Label entropy explained by latent state", "", info.to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["### State transition matrix", "", pd.DataFrame(trans_prob, index=[f"from_{i}" for i in range(K)], columns=[f"to_{i}" for i in range(K)]).to_string(float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["### Subject state occupancy", "", occ.to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["## 2. Are latent states observable from features?", ""]
    if len(avg_state_pred):
        lines += [avg_state_pred.to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["### Top separator feature families by latent state", "", sep_family.groupby("state").head(8).to_string(index=False, float_format=lambda x: f"{x:.3f}"), ""]
    lines += ["## 3. Feature-family signal by target", "", "Top families below are ranked by mean logloss improvement over global prior under masked validation. Positive means the family carries signal; negative means mostly noise/overfit in this setup.", "", top_by_target.to_string(index=False, float_format=lambda x: f"{x:.4f}"), ""]
    lines += ["## 4. Robust target/family map", "", stable_top[["scheme", "target", "family", "mean_improvement_vs_prior", "std_improvement", "robust_score"]].to_string(index=False, float_format=lambda x: f"{x:.4f}"), ""]
    lines += ["## 5. Interpretation", ""]
    lines += ["- 라벨별 모델 적용은 맞다. 다만 더 정확히는 `라벨별 모델`이라기보다 `라벨별 생성 메커니즘/latent state 연결 방식`을 다르게 둬야 한다."]
    lines += ["- Bernoulli mixture state가 여러 target의 entropy를 동시에 설명하면, target을 독립 binary로만 보면 정보가 버려진다. 특히 S-family/Q2-Q3류는 joint state 관점이 맞다."]
    lines += ["- state가 feature로 예측 가능하면 graph/label smoothing만의 문제가 아니라, 센서 feature 안에 실제 behavioral regime 신호가 있다는 뜻이다. 반대로 state 예측력이 낮으면 feature보다 subject-time label interpolation 문제가 크다."]
    lines += ["- feature-family별 신호가 target마다 갈리면, 다음 단계는 제출 후보가 아니라 `각 target의 측정 의미`를 feature family 관점에서 재해석하는 것이다."]
    lines += ["", "## 6. Output files", ""]
    for name in [
        "advanced_ds_bernoulli_mixture_bic.csv",
        "advanced_ds_latent_state_emissions.csv",
        "advanced_ds_row_latent_states.csv",
        "advanced_ds_latent_state_transition_matrix.csv",
        "advanced_ds_subject_state_occupancy.csv",
        "advanced_ds_state_label_information.csv",
        "advanced_ds_latent_state_predictability.csv",
        "advanced_ds_state_feature_separators.csv",
        "advanced_ds_state_separator_family_summary.csv",
        "advanced_ds_feature_family_signal_raw.csv",
        "advanced_ds_feature_family_signal_summary.csv",
        "advanced_ds_top_feature_families_by_target.csv",
    ]:
        lines.append(f"- `experiments/{name}`")
    report = "\n".join(lines) + "\n"
    (EXP / "advanced_ds_insight_report.md").write_text(report, encoding="utf-8")
    print(report[:5000])
    print("\n[written]", EXP / "advanced_ds_insight_report.md")


if __name__ == "__main__":
    main()
