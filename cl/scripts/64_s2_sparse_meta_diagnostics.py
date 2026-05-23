#!/usr/bin/env python3
"""Public-LB-informed S2 sparse-head meta diagnostics.

Builds actual-test S2 predictions from the latest no-submit finding:
  existing_no_flat raw SelectK32 C=0.003

Then layers that signal onto the current public-supported temporal-smoothing anchor
in several controlled ways and writes shift reports.  These are diagnostic
candidate files, not automatic submission recommendations.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
EXP = ROOT / "experiments"
spec = importlib.util.spec_from_file_location("ts", ROOT / "scripts/50_eval_temporal_state_smoothing.py")
ts = importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)

LABELS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
IDS = ["subject_id", "sleep_date", "lifelog_date"]
TARGET = "S2"


def read_out(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)


def assert_same(a: pd.DataFrame, b: pd.DataFrame):
    if not a[IDS].astype(str).equals(b[IDS].astype(str)):
        raise ValueError("ID rows mismatch")


def valid_cols(df: pd.DataFrame, mask: np.ndarray, cols: list[str]) -> list[str]:
    out = []
    for c in cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df.loc[mask, c], errors="coerce")
        if s.notna().sum() > 20 and s.nunique(dropna=True) > 1:
            out.append(c)
    return out


def make_sparse_s2_prediction() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = ts.load_all().sort_values(["subject_id", "sleep_date"]).reset_index(drop=True)
    train_mask = df.is_train.eq(1).to_numpy()
    test_mask = df.is_train.eq(0).to_numpy()
    train = df.loc[train_mask].copy()
    sample = df.loc[test_mask].copy()
    all_cols = [c for c in df.columns if c not in ts.DROP]
    cols = valid_cols(df, train_mask, ts.base_subset(all_cols, "no_flat_hourly"))
    k, C = 32, 0.003
    pipe = Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sel", SelectKBest(f_classif, k=min(k, len(cols)))),
        ("scale", RobustScaler()),
        ("clf", LogisticRegression(C=C, solver="liblinear", max_iter=1000, random_state=42)),
    ])
    pipe.fit(df.loc[train_mask, cols], df.loc[train_mask, TARGET].astype(int).to_numpy())
    p = np.clip(pipe.predict_proba(df.loc[test_mask, cols])[:, 1], 0.02, 0.98)
    selected = pd.DataFrame({"feature": np.array(cols)[pipe.named_steps["sel"].get_support()]})
    pred = sample[IDS].copy().reset_index(drop=True)
    pred[TARGET] = p
    return pred, selected


def shift_rows(df: pd.DataFrame, anchor: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y in LABELS:
        d = np.abs(df[y].to_numpy(float) - anchor[y].to_numpy(float))
        rows.append({
            "target": y,
            "changed_rows": int((d > 1e-12).sum()),
            "mean_abs_delta_vs_anchor": float(d.mean()),
            "p95_abs_delta_vs_anchor": float(np.quantile(d, 0.95)),
            "max_abs_delta_vs_anchor": float(d.max()),
            "corr_vs_anchor": float(np.corrcoef(df[y], anchor[y])[0, 1]) if d.max() > 0 else 1.0,
            "candidate_mean_prob": float(df[y].mean()),
            "anchor_mean_prob": float(anchor[y].mean()),
            "mean_prob_shift": float(df[y].mean() - anchor[y].mean()),
        })
    return pd.DataFrame(rows)


def write_candidate(name: str, df: pd.DataFrame, anchor: pd.DataFrame, notes: dict):
    path = OUT / name
    df.to_csv(path, index=False)
    shift = shift_rows(df, anchor)
    stem = name.replace(".csv", "")
    shift.to_csv(EXP / f"{stem}_shift.csv", index=False)
    (EXP / f"{stem}_notes.json").write_text(json.dumps({"file": str(path), **notes}, ensure_ascii=False, indent=2), encoding="utf-8")
    return shift


def main():
    OUT.mkdir(exist_ok=True); EXP.mkdir(exist_ok=True)
    # Public-supported anchor from previous report: w=0.2 temporal smoothing, Q3 reverted.
    anchor = read_out("submission_meta_anchor_w02_noq3_prob.csv")
    base = read_out("submission_base_v4_replicate_prob.csv")
    prev_s2dl = read_out("submission_meta_anchor_plus_s2dl20_prob.csv")
    for x in [base, prev_s2dl]:
        assert_same(anchor, x)

    sparse_pred, selected = make_sparse_s2_prediction()
    assert_same(anchor, sparse_pred.assign(**{y: anchor[y] for y in LABELS if y != TARGET}))
    selected.to_csv(EXP / "s2_sparse_meta_selected_features.csv", index=False)

    # Component table for inspection.
    comp = anchor[IDS + [TARGET]].rename(columns={TARGET: "anchor_S2"}).copy()
    comp["base_S2"] = base[TARGET]
    comp["s2_sparse_raw32_C0003"] = sparse_pred[TARGET]
    comp["prev_s2dl20_S2"] = prev_s2dl[TARGET]
    comp["delta_sparse_minus_anchor"] = comp["s2_sparse_raw32_C0003"] - comp["anchor_S2"]
    comp["delta_sparse_minus_base"] = comp["s2_sparse_raw32_C0003"] - comp["base_S2"]
    comp.to_csv(EXP / "s2_sparse_meta_component_predictions.csv", index=False)

    reports = []
    candidates = []

    def add(name: str, s2_values, description: str, mode: str):
        c = anchor.copy()
        c[TARGET] = np.clip(np.asarray(s2_values, dtype=float), 0.02, 0.98)
        shift = write_candidate(name, c, anchor, {
            "description": description,
            "mode": mode,
            "local_evidence": "S2 existing_no_flat raw SelectK32 C=0.003: robust mean delta about -0.01 vs base; latent compression failed.",
            "submission_status": "diagnostic artifact; not recommended automatically",
        })
        s2row = shift[shift.target.eq(TARGET)].iloc[0].to_dict()
        reports.append({"file": name, "description": description, **{f"S2_{k}": v for k, v in s2row.items() if k != "target"}})
        candidates.append(c)

    raw = sparse_pred[TARGET].to_numpy(float)
    anc = anchor[TARGET].to_numpy(float)
    bas = base[TARGET].to_numpy(float)
    prev = prev_s2dl[TARGET].to_numpy(float)

    # 1) Safer interpolation between public anchor S2 and sparse S2.
    for w in [0.30, 0.50, 0.70]:
        add(
            f"submission_meta_anchor_s2sparse_blend{int(w*100):02d}_prob.csv",
            (1 - w) * anc + w * raw,
            f"Anchor S2 interpolated {int(w*100)}% toward sparse raw32 head.",
            f"S2=(1-{w})*anchor + {w}*sparse_raw32",
        )

    # 2) Residual-on-base style, analogous to previous S2 DL residual candidates.
    for w in [0.30, 0.50]:
        add(
            f"submission_meta_anchor_plus_s2sparse_resid{int(w*100):02d}_prob.csv",
            anc + w * (raw - bas),
            f"Anchor plus {int(w*100)}% of sparse raw32 minus base residual on S2.",
            f"S2=anchor + {w}*(sparse_raw32-base_v4)",
        )

    # 3) Direct replacement is diagnostic only; useful to inspect distribution shift.
    add(
        "submission_meta_anchor_s2sparse_replace_prob.csv",
        raw,
        "Full S2 replacement with sparse raw32 head. Diagnostic/highest shift; not first submission choice.",
        "S2=sparse_raw32",
    )

    # 4) Combine previous S2-DL residual and sparse S2 gently: average their S2 changes from anchor.
    add(
        "submission_meta_anchor_s2dl20_s2sparse30_avg_prob.csv",
        anc + 0.5 * ((prev - anc) + (0.30 * (raw - anc))),
        "Average previous S2-DL20 residual with a mild 30% sparse-S2 interpolation residual.",
        "S2=anchor + 0.5*((prev_s2dl20-anchor)+0.30*(sparse_raw32-anchor))",
    )

    rep = pd.DataFrame(reports)
    rep.to_csv(EXP / "s2_sparse_meta_candidate_shift_summary.csv", index=False)

    lines = [
        "# S2 sparse-head public-LB-informed meta diagnostics",
        "",
        "Diagnostic candidate files were written, but no automatic submission recommendation is made.",
        "",
        "## Anchor",
        "`outputs/submission_meta_anchor_w02_noq3_prob.csv`",
        "",
        "## Component",
        "S2 sparse head: `existing_no_flat` + SelectK=32 + Logistic C=0.003 trained on all train rows.",
        "",
        "## Candidate S2 shift summary",
        rep.to_string(index=False, float_format=lambda x: f"{x:.6f}"),
        "",
        "## Selected sparse S2 features",
        selected.head(40).to_string(index=False),
        "",
        "## Interpretation",
        "Use the interpolation candidates first if public probing is allowed. Residual and replacement variants are higher-shift diagnostics.",
        "The safest new S2-only files by shift are the 30/50% anchor-to-sparse blends; the replacement file is intentionally not first-choice.",
    ]
    out = EXP / "s2_sparse_meta_diagnostic_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out)
    print(rep.to_string(index=False))


if __name__ == "__main__":
    main()
