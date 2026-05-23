#!/usr/bin/env python3
"""No-submission temporal label diagnostics.

Purpose: quantify whether each target behaves like same-subject temporal state
completion.  This does NOT create submission files.  It tests label-only
predictors under many masked splits:
  - actual-test-pattern masks
  - tail masks
  - random within-subject gap masks
If a target is not robust even for label-only interpolation, calibrator/smoothing
submission ideas should be treated as weak.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util
import json
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
DATA = ROOT / "data"
spec = importlib.util.spec_from_file_location("ts", ROOT / "scripts/50_eval_temporal_state_smoothing.py")
ts = importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
LABELS = ts.LABELS


def prep():
    train = pd.read_csv(DATA / "ch2026_metrics_train.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    train = train.sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    sample = sample.sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    return train, sample


def random_gap_mask(train: pd.DataFrame, seed: int, frac: float = 0.28) -> np.ndarray:
    rng = np.random.default_rng(seed)
    mask = np.zeros(len(train), dtype=bool)
    for sid, sub in train.groupby("subject_id"):
        sub = sub.sort_values("sleep_date")
        n = max(3, int(round(len(sub) * frac)))
        ranks = np.linspace(0, 1, len(sub))
        # Prefer middle+late dates but less test-specific than ts.make_testpattern_mask.
        prob = 0.2 + 0.7 * ranks + np.exp(-0.5 * ((ranks - 0.55) / 0.22) ** 2)
        prob = prob / prob.sum()
        chosen = rng.choice(sub.index.to_numpy(), size=min(n, len(sub)-2), replace=False, p=prob)
        mask[train.index.get_indexer(chosen)] = True
    return mask


def tail_mask(train: pd.DataFrame, frac: float) -> np.ndarray:
    mask = np.zeros(len(train), dtype=bool)
    for sid, sub in train.groupby("subject_id"):
        n = max(3, int(round(len(sub) * frac)))
        chosen = sub.sort_values("sleep_date").tail(n).index
        mask[train.index.get_indexer(chosen)] = True
    return mask


def safe_clip(x):
    return np.clip(np.asarray(x, dtype=float), 0.02, 0.98)


def local_predictors(known: pd.DataFrame, query: pd.DataFrame, target: str) -> dict[str, np.ndarray]:
    g = float(known[target].mean())
    out = {"global": np.full(len(query), g, dtype=float)}
    subj_mean = known.groupby("subject_id")[target].mean().to_dict()
    out["subject_mean"] = query["subject_id"].map(subj_mean).fillna(g).to_numpy(float)
    preds = {k: [] for k in [
        "prev1", "next1", "nearest", "prevnext_mean", "linear_interp",
        "past_exp_tau7", "past_exp_tau30", "both_exp_tau7", "both_exp_tau30",
        "both_exp_tau7_alpha5", "local3_mean"
    ]}
    for r in query.itertuples(index=False):
        sid = r.subject_id; d = r.sleep_date
        k = known[known.subject_id.eq(sid)].sort_values("sleep_date")
        vals = k[target].astype(float).to_numpy()
        dates = k.sleep_date.to_numpy(dtype="datetime64[D]").astype(int)
        qd = np.datetime64(d, "D").astype(int)
        if len(k) == 0:
            for kk in preds: preds[kk].append(g)
            continue
        prev = k[k.sleep_date < d].tail(1)
        nxt = k[k.sleep_date > d].head(1)
        pv = float(prev[target].iloc[0]) if len(prev) else g
        nv = float(nxt[target].iloc[0]) if len(nxt) else g
        pdist = float((d - prev.sleep_date.iloc[0]).days) if len(prev) else 999.0
        ndist = float((nxt.sleep_date.iloc[0] - d).days) if len(nxt) else 999.0
        dist = np.abs(dates - qd).astype(float)
        nearest = float(vals[int(np.argmin(dist))])
        preds["prev1"].append(pv)
        preds["next1"].append(nv)
        preds["nearest"].append(nearest)
        preds["prevnext_mean"].append((pv + nv) / 2)
        if len(prev) and len(nxt):
            # closer neighbor gets more weight
            preds["linear_interp"].append((nv * pdist + pv * ndist) / max(pdist + ndist, 1e-9))
        elif len(prev):
            preds["linear_interp"].append(pv)
        elif len(nxt):
            preds["linear_interp"].append(nv)
        else:
            preds["linear_interp"].append(g)
        for tau in [7, 30]:
            past_mask = dates < qd
            if past_mask.any():
                ds = qd - dates[past_mask]
                w = np.exp(-ds / tau)
                pp = float((w @ vals[past_mask]) / (w.sum() + 1e-9))
            else:
                pp = g
            preds[f"past_exp_tau{tau}"].append(pp)
            w = np.exp(-dist / tau)
            bp = float((w @ vals) / (w.sum() + 1e-9))
            preds[f"both_exp_tau{tau}"].append(bp)
        # alpha-smoothed local mean, less oracle-like/overconfident
        tau = 7
        w = np.exp(-dist / tau)
        preds["both_exp_tau7_alpha5"].append(float((w @ vals + 5 * g) / (w.sum() + 5)))
        nearest_idx = np.argsort(dist)[:min(3, len(vals))]
        preds["local3_mean"].append(float(vals[nearest_idx].mean()))
    for k, v in preds.items():
        out[k] = np.asarray(v, dtype=float)
    return {k: safe_clip(v) for k, v in out.items()}


def main():
    EXP.mkdir(exist_ok=True)
    train, sample = prep()
    masks = []
    for seed in range(12):
        masks.append(("testpattern", seed, ts.make_testpattern_mask(train, sample, seed)))
    for seed in range(12):
        masks.append(("random_gap", seed, random_gap_mask(train, seed)))
    for frac in [0.20, 0.30, 0.40]:
        masks.append((f"tail{frac:.2f}", int(frac * 100), tail_mask(train, frac)))

    rows = []
    for split, seed, val_mask in masks:
        known = train.loc[~val_mask].copy()
        val = train.loc[val_mask].copy()
        for y in LABELS:
            ytrue = val[y].astype(int).to_numpy()
            preds = local_predictors(known, val, y)
            for method, p in preds.items():
                try:
                    auc = roc_auc_score(ytrue, p) if len(set(ytrue)) == 2 else np.nan
                except Exception:
                    auc = np.nan
                rows.append({
                    "split": split, "seed": seed, "target": y, "method": method,
                    "logloss": log_loss(ytrue, p, labels=[0, 1]),
                    "auc": auc,
                    "n": int(len(ytrue)),
                    "pos_rate": float(ytrue.mean()),
                })
    res = pd.DataFrame(rows)
    out = EXP / "label_temporal_diagnostics_no_submit.csv"
    res.to_csv(out, index=False)

    # Summary: compare methods to global and subject_mean within each split/target.
    base = res[res.method.eq("global")].groupby(["split", "target"])["logloss"].mean().rename("global_loss")
    subj = res[res.method.eq("subject_mean")].groupby(["split", "target"])["logloss"].mean().rename("subject_loss")
    summ = res.groupby(["split", "target", "method"]).agg(
        logloss=("logloss", "mean"),
        std=("logloss", "std"),
        auc=("auc", "mean"),
    ).reset_index().merge(base, on=["split", "target"]).merge(subj, on=["split", "target"])
    summ["delta_vs_global"] = summ.logloss - summ.global_loss
    summ["delta_vs_subject"] = summ.logloss - summ.subject_loss
    summ.to_csv(EXP / "label_temporal_diagnostics_no_submit_summary.csv", index=False)

    lines = ["# Label-temporal diagnostics, no submission", ""]
    lines.append("This experiment uses train labels only under masked validation. It does not produce submission files.")
    lines.append("")
    for group_name, predicate in [
        ("testpattern", lambda s: s == "testpattern"),
        ("random_gap", lambda s: s == "random_gap"),
        ("tail", lambda s: str(s).startswith("tail")),
    ]:
        sub = summ[summ.split.map(predicate)]
        if len(sub) == 0: continue
        agg = sub.groupby(["target", "method"]).agg(
            logloss=("logloss", "mean"),
            delta_vs_subject=("delta_vs_subject", "mean"),
            auc=("auc", "mean"),
        ).reset_index()
        best = agg.sort_values(["target", "logloss"]).groupby("target").head(3)
        lines.append(f"## {group_name} best methods")
        lines.append("")
        lines.append(best.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
        lines.append("")
    report = EXP / "label_temporal_diagnostics_no_submit_report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out)
    print("wrote", report)
    print("\nQuick best by group/target:")
    for group_name, predicate in [
        ("testpattern", lambda s: s == "testpattern"),
        ("random_gap", lambda s: s == "random_gap"),
        ("tail", lambda s: str(s).startswith("tail")),
    ]:
        sub = summ[summ.split.map(predicate)]
        agg = sub.groupby(["target", "method"]).agg(logloss=("logloss","mean"), delta_vs_subject=("delta_vs_subject","mean"), auc=("auc","mean")).reset_index()
        best = agg.sort_values(["target","logloss"]).groupby("target").head(1)
        print("\n", group_name)
        print(best.to_string(index=False))

if __name__ == "__main__":
    main()
