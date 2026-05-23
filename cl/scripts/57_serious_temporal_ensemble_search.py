#!/usr/bin/env python3
"""Serious temporal ensemble search for interleaved same-subject lifelog task.

This goes beyond one-off smoothing: for each target it evaluates a constrained
ensemble of
  - base sensor/feature logistic model,
  - both-side temporal label smoother,
  - learned temporal-state calibrator,
  - raw subject local mean,
under many test-pattern masks plus tail masks.  It then writes robust candidate
submissions with detailed shift reports.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util, json, warnings
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments"
OUT = ROOT / "outputs"

# Import existing, already-vetted primitives.
spec = importlib.util.spec_from_file_location("ts", ROOT / "scripts/50_eval_temporal_state_smoothing.py")
ts = importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)
spec2 = importlib.util.spec_from_file_location("lc", ROOT / "scripts/53_eval_learned_temporal_calibrator.py")
lc = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(lc)
LABELS = ts.LABELS
ID_COLS = ts.ID_COLS


def subject_mean_component(anchor: pd.DataFrame, query: pd.DataFrame, target: str) -> np.ndarray:
    g = float(anchor[target].mean())
    means = anchor.groupby("subject_id")[target].mean().to_dict()
    return np.clip(query["subject_id"].map(means).fillna(g).to_numpy(float), 0.02, 0.98)


def calibrator_component(known: pd.DataFrame, query: pd.DataFrame, target: str, p_known_base: np.ndarray, p_query_base: np.ndarray, C: float) -> np.ndarray:
    Xtr = lc.temporal_feature_frame(known, known, target, p_known_base, exclude_self=True)
    Xq = lc.temporal_feature_frame(known, query, target, p_query_base, exclude_self=False)
    pipe = lc.make_pipe(C)
    pipe.fit(Xtr, known[target].astype(int).to_numpy())
    return np.clip(pipe.predict_proba(Xq)[:, 1], 0.02, 0.98)


def make_tail_mask_frac(train: pd.DataFrame, frac: float) -> np.ndarray:
    mask = np.zeros(len(train), dtype=bool)
    for sid, sub in train.groupby("subject_id"):
        n = max(3, int(round(len(sub) * frac)))
        chosen = sub.sort_values("sleep_date").tail(n).index
        mask[train.index.get_indexer(chosen)] = True
    return mask


def eval_search():
    df = ts.load_all()
    train = df[df.is_train.eq(1)].copy().sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    sample = df[df.is_train.eq(0)].copy().sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)

    masks = []
    # Wide enough for signal, small enough to iterate quickly in Discord session.
    for seed in range(6):
        masks.append(("testpattern", seed, ts.make_testpattern_mask(train, sample, seed)))
    for frac in [0.30, 0.36, 0.44]:
        masks.append((f"tail{frac:.2f}", int(frac * 100), make_tail_mask_frac(train, frac)))

    taus = [3, 7, 14, 30]
    alphas = [1, 5, 10]
    Cs = [0.01, 0.03]
    # Constrained grid: avoid giant public shifts.
    smooth_ws = [0.00, 0.10, 0.20, 0.30, 0.40]
    calib_ws = [0.00, 0.10, 0.20, 0.30, 0.40]
    subj_ws = [0.00, 0.10]
    clips = [0.02]

    rows = []
    for split, seed, val_mask in masks:
        known_mask = ~val_mask
        known = train.loc[known_mask].copy()
        val = train.loc[val_mask].copy()
        for y in LABELS:
            qmask = val_mask
            pbase = ts.base_predict_for(train, known_mask, qmask, y, None)
            pknown_base = ts.base_predict_for(train, known_mask, known_mask, y, None)
            ytrue = val[y].astype(int).to_numpy()
            base_loss = log_loss(ytrue, pbase, labels=[0, 1])
            psubj = subject_mean_component(known, val, y)

            smooth_cache = {}
            for tau in taus:
                for alpha in alphas:
                    smooth_cache[(tau, alpha)] = ts.temporal_label_smooth(known, val, y, tau, alpha, use_future=True)
            calib_cache = {}
            for C in Cs:
                calib_cache[C] = calibrator_component(known, val, y, pknown_base, pbase, C)

            # Also record pure components.
            for (tau, alpha), ps in smooth_cache.items():
                rows.append({"split": split, "seed": seed, "target": y, "kind": "component_smooth", "tau": tau, "alpha": alpha, "C": np.nan, "ws": 1.0, "wc": 0.0, "wu": 0.0, "clip": 0.02, "logloss": log_loss(ytrue, ps, labels=[0,1]), "base_logloss": base_loss})
            for C, pc in calib_cache.items():
                rows.append({"split": split, "seed": seed, "target": y, "kind": "component_calib", "tau": np.nan, "alpha": np.nan, "C": C, "ws": 0.0, "wc": 1.0, "wu": 0.0, "clip": 0.02, "logloss": log_loss(ytrue, pc, labels=[0,1]), "base_logloss": base_loss})
            rows.append({"split": split, "seed": seed, "target": y, "kind": "component_subj", "tau": np.nan, "alpha": np.nan, "C": np.nan, "ws": 0.0, "wc": 0.0, "wu": 1.0, "clip": 0.02, "logloss": log_loss(ytrue, psubj, labels=[0,1]), "base_logloss": base_loss})

            for tau in taus:
                for alpha in alphas:
                    ps = smooth_cache[(tau, alpha)]
                    for C in Cs:
                        pc = calib_cache[C]
                        for ws in smooth_ws:
                            for wc in calib_ws:
                                for wu in subj_ws:
                                    if ws + wc + wu > 0.65:
                                        continue
                                    wb = 1.0 - ws - wc - wu
                                    raw = wb * pbase + ws * ps + wc * pc + wu * psubj
                                    for clip in clips:
                                        p = np.clip(raw, clip, 1 - clip)
                                        rows.append({"split": split, "seed": seed, "target": y, "kind": "blend", "tau": tau, "alpha": alpha, "C": C, "ws": ws, "wc": wc, "wu": wu, "clip": clip, "logloss": log_loss(ytrue, p, labels=[0,1]), "base_logloss": base_loss})
    res = pd.DataFrame(rows)
    EXP.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    res.to_csv(EXP / "serious_temporal_ensemble_search_results.csv", index=False)
    return df, train, sample, res


def summarize_and_select(res: pd.DataFrame) -> pd.DataFrame:
    keys = ["target", "kind", "tau", "alpha", "C", "ws", "wc", "wu", "clip"]
    tp = res[res.split.eq("testpattern")]
    summ = tp.groupby(keys, dropna=False).agg(
        tp_logloss=("logloss", "mean"),
        tp_std=("logloss", "std"),
        tp_base=("base_logloss", "mean"),
    ).reset_index()
    summ["tp_delta"] = summ.tp_logloss - summ.tp_base
    tail = res[res.split.str.startswith("tail")].groupby(keys, dropna=False).agg(
        tail_logloss=("logloss", "mean"),
        tail_base=("base_logloss", "mean"),
    ).reset_index()
    summ = summ.merge(tail, on=keys, how="left")
    summ["tail_delta"] = summ.tail_logloss - summ.tail_base
    summ.to_csv(EXP / "serious_temporal_ensemble_summary.csv", index=False)

    selected = []
    for y, g in summ[summ.kind.eq("blend")].groupby("target"):
        # Robust primary: meaningful tp improvement, no bad multi-tail average, not too variable.
        gate = g[(g.tp_delta < -0.006) & (g.tail_delta <= 0.003) & (g.tp_std <= 0.045)].copy()
        if len(gate) == 0:
            gate = g[(g.tp_delta < -0.003) & (g.tail_delta <= 0.008)].copy()
        if len(gate) == 0:
            row = g.sort_values("tp_logloss").iloc[0].copy()
            row["apply"] = False
            row["reason"] = "no_robust_gate"
        else:
            # Prefer lower risk among near-best: less total non-base weight and lower tail delta.
            best_tp = gate.tp_logloss.min()
            near = gate[gate.tp_logloss <= best_tp + 0.004].copy()
            near["nonbase"] = near.ws + near.wc + near.wu
            row = near.sort_values(["tail_delta", "nonbase", "tp_logloss"]).iloc[0].copy()
            row["apply"] = True
            row["reason"] = "robust_gate"
        selected.append(row)
    sel = pd.DataFrame(selected).sort_values("target")
    sel.to_csv(EXP / "serious_temporal_ensemble_selected.csv", index=False)
    return sel


def make_submission(train: pd.DataFrame, sample: pd.DataFrame, full: pd.DataFrame, sel: pd.DataFrame, name: str, allowed: set[str] | None, max_nonbase: float | None = None):
    known_mask = np.r_[np.ones(len(train), bool), np.zeros(len(sample), bool)]
    query_mask = np.r_[np.zeros(len(train), bool), np.ones(len(sample), bool)]
    sub = sample[ID_COLS].copy().reset_index(drop=True)
    base_sub = sample[ID_COLS].copy().reset_index(drop=True)
    used = {}; shifts = []
    for y in LABELS:
        pbase = ts.base_predict_for(full, known_mask, query_mask, y, None)
        base_sub[y] = pbase
        row = sel[sel.target.eq(y)].iloc[0]
        apply = bool(row.apply)
        if allowed is not None and y not in allowed:
            apply = False
        nonbase = float(row.ws + row.wc + row.wu)
        if max_nonbase is not None and nonbase > max_nonbase:
            apply = False
        p = pbase.copy()
        if apply:
            ps = ts.temporal_label_smooth(train, sample, y, float(row.tau), float(row.alpha), use_future=True)
            pknown_base = ts.base_predict_for(train, np.ones(len(train), bool), np.ones(len(train), bool), y, None)
            pc = calibrator_component(train, sample, y, pknown_base, pbase, float(row.C))
            pu = subject_mean_component(train, sample, y)
            wb = 1.0 - float(row.ws) - float(row.wc) - float(row.wu)
            p = np.clip(wb * pbase + float(row.ws) * ps + float(row.wc) * pc + float(row.wu) * pu, float(row.clip), 1 - float(row.clip))
        sub[y] = p
        d = np.abs(p - pbase)
        shift = {
            "target": y, "apply": bool(apply), "tau": None if pd.isna(row.tau) else float(row.tau), "alpha": None if pd.isna(row.alpha) else float(row.alpha), "C": None if pd.isna(row.C) else float(row.C),
            "ws": float(row.ws), "wc": float(row.wc), "wu": float(row.wu), "clip": float(row.clip),
            "tp_delta": float(row.tp_delta), "tail_delta": float(row.tail_delta), "tp_logloss": float(row.tp_logloss), "tp_base": float(row.tp_base),
            "changed_rows": int((d > 1e-12).sum()), "mean_abs_delta": float(d.mean()), "max_abs_delta": float(d.max()),
            "corr_vs_base": float(np.corrcoef(p, pbase)[0,1]) if d.max() > 0 else 1.0,
        }
        shifts.append(shift); used[y] = shift
    out = OUT / f"{name}.csv"
    sub.to_csv(out, index=False)
    pd.DataFrame(shifts).to_csv(EXP / f"{name}_shift.csv", index=False)
    (EXP / f"{name}_used.json").write_text(json.dumps(used, indent=2), encoding="utf-8")
    print("\n### wrote", out)
    print(pd.DataFrame(shifts).to_string(index=False))


def main():
    df, train, sample, res = eval_search()
    sel = summarize_and_select(res)
    print("\n### selected robust targetwise configs")
    cols = ["target", "apply", "reason", "tau", "alpha", "C", "ws", "wc", "wu", "clip", "tp_logloss", "tp_base", "tp_delta", "tp_std", "tail_delta"]
    print(sel[cols].to_string(index=False))
    full = pd.concat([train, sample], ignore_index=True)
    make_submission(train, sample, full, sel, "submission_serious_temporal_ensemble_robust_prob", allowed=None)
    make_submission(train, sample, full, sel, "submission_serious_temporal_ensemble_q1q2s4_prob", allowed={"Q1", "Q2", "S4"})
    make_submission(train, sample, full, sel, "submission_serious_temporal_ensemble_safe30_prob", allowed=None, max_nonbase=0.30)

if __name__ == "__main__":
    main()
