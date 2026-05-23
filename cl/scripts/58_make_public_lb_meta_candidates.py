#!/usr/bin/env python3
"""Create public-LB-informed meta candidates from existing validated submission families.

Known public feedback: temporal_state_smoothing_wcap02 = 0.6311869686.
This script avoids retraining.  It constructs controlled targetwise candidates by
starting from the best public-supported temporal smoothing family and adding only
small, locally-supported deltas from DL/calibrator families.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
EXP = ROOT / "experiments"
LABELS = ["Q1","Q2","Q3","S1","S2","S3","S4"]
IDS = ["subject_id","sleep_date","lifelog_date"]


def read(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name)


def assert_same(a: pd.DataFrame, b: pd.DataFrame):
    if not a[IDS].astype(str).equals(b[IDS].astype(str)):
        raise ValueError("ID rows mismatch")


def write_candidate(name: str, df: pd.DataFrame, base: pd.DataFrame, notes: str):
    out = OUT / name
    df.to_csv(out, index=False)
    rows=[]
    for y in LABELS:
        d = np.abs(df[y].to_numpy(float) - base[y].to_numpy(float))
        rows.append({
            "target": y,
            "changed_rows": int((d > 1e-12).sum()),
            "mean_abs_delta_vs_anchor": float(d.mean()),
            "max_abs_delta_vs_anchor": float(d.max()),
            "corr_vs_anchor": float(np.corrcoef(df[y], base[y])[0,1]) if d.max() > 0 else 1.0,
            "mean_prob": float(df[y].mean()),
            "anchor_mean_prob": float(base[y].mean()),
        })
    shift = pd.DataFrame(rows)
    shift.to_csv(EXP / f"{name.replace('.csv','')}_shift.csv", index=False)
    (EXP / f"{name.replace('.csv','')}_notes.json").write_text(json.dumps({"file": str(out), "notes": notes}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n###", name)
    print(notes)
    print(shift.to_string(index=False))


def main():
    anchor = read("submission_lbdiag_w02_all_except_q3_prob.csv")
    base_v4 = read("submission_base_v4_replicate_prob.csv")
    w02 = read("submission_temporal_state_smoothing_wcap02_prob.csv")
    tiny_s2_30 = read("submission_tiny_dl_golf_s2_blend30_prob.csv")
    tiny_q1s2_20 = read("submission_tiny_dl_golf_q1s2_blend20_prob.csv")
    learned30 = read("submission_learned_calibrator_q1q2s4_blend30_prob.csv")
    for x in [base_v4,w02,tiny_s2_30,tiny_q1s2_20,learned30]:
        assert_same(anchor, x)

    # Candidate 1: already recommended diagnostic anchor; re-write with explicit naming.
    write_candidate(
        "submission_meta_anchor_w02_noq3_prob.csv",
        anchor.copy(),
        w02,
        "Anchor: public-supported w=0.2 temporal smoothing, but Q3 reverted to base. Tests whether Q3 was hurting the known 0.6311869686 file.",
    )

    # Candidate 2: add only S2 tiny-DL delta on top of anchor, at two-thirds of its existing 30% blend delta (= extra 20% neural-vs-base equivalent).
    c2 = anchor.copy()
    c2["S2"] = np.clip(anchor["S2"] + (2/3) * (tiny_s2_30["S2"] - base_v4["S2"]), 0.02, 0.98)
    write_candidate(
        "submission_meta_anchor_plus_s2dl20_prob.csv",
        c2,
        anchor,
        "Anchor + small S2 tiny-DL residual. S2 was the cleanest DL signal locally; delta capped to ~20% neural equivalent to avoid pure-DL shift.",
    )

    # Candidate 3: Q1+S2 tiny DL diagnostic, but only half of the existing 20% file delta, layered on anchor.
    c3 = anchor.copy()
    for y in ["Q1","S2"]:
        c3[y] = np.clip(anchor[y] + 0.5 * (tiny_q1s2_20[y] - base_v4[y]), 0.02, 0.98)
    write_candidate(
        "submission_meta_anchor_plus_q1s2dl10_prob.csv",
        c3,
        anchor,
        "Anchor + very small Q1/S2 tiny-DL residual. Q1 DL was mixed on tail, so only half of the existing 20% blend delta is applied.",
    )

    # Candidate 4: small learned temporal calibrator only on Q1/Q2/S4, half of blend30 (= blend15). Higher risk than C2/C3 but directly targets hard labels.
    c4 = anchor.copy()
    for y in ["Q1","Q2","S4"]:
        c4[y] = np.clip(anchor[y] + 0.5 * (learned30[y] - base_v4[y]), 0.02, 0.98)
    write_candidate(
        "submission_meta_anchor_plus_calib15_q1q2s4_prob.csv",
        c4,
        anchor,
        "Anchor + learned temporal calibrator residual at ~15% blend for Q1/Q2/S4. This is the aggressive hard-target diagnostic; use after safer anchor/S2 tests.",
    )

    # Candidate 5: combine the safest two orthogonal residuals: S2 DL + tiny calibrator only for Q1/S4 (skip Q2 because Q2 shifts were large).
    c5 = anchor.copy()
    c5["S2"] = c2["S2"]
    for y in ["Q1","S4"]:
        c5[y] = np.clip(anchor[y] + (1/3) * (learned30[y] - base_v4[y]), 0.02, 0.98)  # ~10% calibrator
    write_candidate(
        "submission_meta_anchor_plus_s2dl20_q1s4calib10_prob.csv",
        c5,
        anchor,
        "Combined safer meta: S2 DL residual + very small Q1/S4 learned-calibrator residual; skips Q2 because calibrator public-shift risk is largest there.",
    )

    print("\nWrote meta candidates and shift reports under outputs/ and experiments/.")

if __name__ == "__main__":
    main()
