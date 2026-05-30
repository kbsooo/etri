#!/usr/bin/env python3
"""E220: audit whether an S2 support/tail gate can rescue E216.

E219 showed that E216's public miss is dominated by the S2 graft, not by the
E154 body. This script asks the next smallest question: can a simple,
public-sensor-derived support/tail gate reduce the S2 graft's adverse capacity
below the observed miss while keeping enough expected signal to justify a later
proper OOF gate?

No submission is selected automatically. Generated candidate files are marked as
diagnostic unless a future OOF/trainable gate reproduces the same support rule.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E216_E95_FILE = "submission_e216_maskfam_jepa_s2_rank_e95_s0p75_4f8dc44d.csv"
E219_SEGMENTS = OUT / "e219_e216_public_miss_segments.csv"
E219_TOP = OUT / "e219_e216_public_miss_top_cells.csv"

E95_PUBLIC = 0.5762913298
E216_PUBLIC = 0.5772865088
OBS_DELTA = E216_PUBLIC - E95_PUBLIC
N_PUBLIC_CELLS = 250 * 7
N_SIMS = 100_000
BATCH = 20_000
RNG_SEED = 20260530 + 220
EPS = 1.0e-12

SCAN_OUT = OUT / "e220_s2_support_tail_gate_scan.csv"
SELECTED_OUT = OUT / "e220_s2_support_tail_gate_selected.csv"
REPORT_OUT = OUT / "e220_s2_support_tail_gate_report.md"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def hard_loss_deltas(p_new: np.ndarray, p_base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_new = clip_prob(p_new)
    p_base = clip_prob(p_base)
    dy1 = -np.log(p_new) + np.log(p_base)
    dy0 = -np.log(1.0 - p_new) + np.log(1.0 - p_base)
    return dy1 / N_PUBLIC_CELLS, dy0 / N_PUBLIC_CELLS


def md(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    view = view.head(n).copy()
    rendered = view.copy()
    for col in rendered.columns:
        if pd.api.types.is_float_dtype(rendered[col]):
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
        else:
            rendered[col] = rendered[col].map(lambda x: "" if pd.isna(x) else str(x))
    header = "| " + " | ".join(rendered.columns.astype(str)) + " |"
    sep = "| " + " | ".join(["---"] * len(rendered.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in rendered.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def simulate_subset(part: pd.DataFrame, prior: str, rng: np.random.Generator) -> dict[str, float]:
    if part.empty:
        return {
            "sim_mean": 0.0,
            "sim_std": 0.0,
            "sim_prob_loss": 0.0,
            "sim_prob_ge_half_obs": 0.0,
            "sim_prob_ge_obs": 0.0,
        }
    p_y = part[f"p_y1_{prior}"].to_numpy(dtype=np.float64)
    dy1 = part["delta_y1"].to_numpy(dtype=np.float64)
    dy0 = part["delta_y0"].to_numpy(dtype=np.float64)
    totals: list[np.ndarray] = []
    remaining = N_SIMS
    while remaining > 0:
        n = min(BATCH, remaining)
        labels = rng.random((n, len(part))) < p_y[None, :]
        totals.append(np.where(labels, dy1[None, :], dy0[None, :]).sum(axis=1))
        remaining -= n
    total = np.concatenate(totals)
    return {
        "sim_mean": float(total.mean()),
        "sim_std": float(total.std()),
        "sim_prob_loss": float((total > 0.0).mean()),
        "sim_prob_ge_half_obs": float((total >= 0.5 * OBS_DELTA).mean()),
        "sim_prob_ge_obs": float((total >= OBS_DELTA).mean()),
    }


def score_subset(name: str, part: pd.DataFrame, rng: np.random.Generator) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "gate": name,
        "n_cells": int(len(part)),
        "expected_focus": float(part["expected_focus_mean"].sum()) if not part.empty else 0.0,
        "support_delta": float(part["support_delta"].sum()) if not part.empty else 0.0,
        "adverse_delta": float(part["adverse_delta"].sum()) if not part.empty else 0.0,
        "total_swing": float(part["swing"].sum()) if not part.empty else 0.0,
    }
    if part.empty or float(part["swing"].sum()) <= 0:
        rec["support_prob_focus_weighted"] = np.nan
    else:
        rec["support_prob_focus_weighted"] = float(np.average(part["support_prob_focus_mean"], weights=part["swing"]))
    rec["adverse_over_observed"] = float(rec["adverse_delta"] / OBS_DELTA) if OBS_DELTA > 0 else np.nan
    rec["expected_per_cell"] = float(rec["expected_focus"] / max(rec["n_cells"], 1))
    rec.update(simulate_subset(part, "focus_mean", rng))
    rec["tail_gate_pass"] = bool(
        rec["n_cells"] >= 5
        and rec["expected_focus"] < -1.0e-5
        and rec["adverse_delta"] < OBS_DELTA
        and rec["support_prob_focus_weighted"] >= 0.50
        and rec["sim_prob_ge_obs"] <= 0.001
    )
    rec["diagnostic_score"] = (
        -rec["expected_focus"] * 10.0
        - max(rec["adverse_delta"] - OBS_DELTA, 0.0) * 25.0
        - rec["sim_prob_ge_obs"] * 0.01
        + max(rec["support_prob_focus_weighted"] - 0.5, 0.0) * 0.001
    )
    return rec


def materialize(sample: pd.DataFrame, base: np.ndarray, full: np.ndarray, rows: pd.DataFrame, tag: str) -> str:
    out = base.copy()
    j = TARGETS.index("S2")
    idx = rows["row_idx"].to_numpy(dtype=int)
    out[idx, j] = full[idx, j]
    digest = hashlib.sha1(np.round(out, 10).tobytes()).hexdigest()[:8]
    name = f"submission_e220_s2support_{tag}_{digest}.csv"
    frame = sample[KEYS].copy()
    frame[TARGETS] = clip_prob(out)
    frame.to_csv(OUT / name, index=False)
    return name


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    base_e95 = load_prob(E95_FILE, sample)
    base_e154 = load_prob(E154_FILE, sample)
    full_e216_e95 = load_prob(E216_E95_FILE, sample)
    segments = pd.read_csv(E219_SEGMENTS, low_memory=False)
    s2 = segments[segments["component"].eq("e154_to_e216_s2_graft")].copy()
    top = pd.read_csv(E219_TOP)
    top_cells = set(top.loc[top["component"].eq("e154_to_e216_s2_graft"), "cell_id"].astype(str))

    gates: dict[str, pd.Series] = {}
    gates["all_s2"] = pd.Series(True, index=s2.index)
    for thr in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]:
        gates[f"focus_support_ge_{str(thr).replace('.', 'p')}"] = s2["support_prob_focus_mean"] >= thr
    for thr in [0.50, 0.60, 0.70]:
        gates[f"subject_support_ge_{str(thr).replace('.', 'p')}"] = s2["support_prob_subject"] >= thr
        gates[f"nearest_support_ge_{str(thr).replace('.', 'p')}"] = s2["support_prob_nearest_hard085"] >= thr
    for k in [10, 20, 40, 60]:
        drop = set(list(top_cells)[:k])
        gates[f"drop_top{k}_posterior_risk"] = ~s2["cell_id"].astype(str).isin(drop)
    for thr in [0.50, 0.55, 0.60, 0.65]:
        gates[f"focus_support_ge_{str(thr).replace('.', 'p')}_expected_neg"] = (
            (s2["support_prob_focus_mean"] >= thr) & (s2["expected_focus_mean"] < 0.0)
        )
    gates["expected_neg_only"] = s2["expected_focus_mean"] < 0.0
    gates["expected_neg_drop_top20"] = (s2["expected_focus_mean"] < 0.0) & (~s2["cell_id"].astype(str).isin(set(list(top_cells)[:20])))
    gates["expected_neg_drop_top40"] = (s2["expected_focus_mean"] < 0.0) & (~s2["cell_id"].astype(str).isin(set(list(top_cells)[:40])))

    rows: list[dict[str, Any]] = []
    rng = np.random.default_rng(RNG_SEED)
    for name, mask in gates.items():
        part = s2.loc[mask].copy()
        rec = score_subset(name, part, rng)
        rows.append(rec)
    scan = pd.DataFrame(rows).sort_values(["tail_gate_pass", "diagnostic_score"], ascending=[False, False]).reset_index(drop=True)

    selected = scan[scan["tail_gate_pass"]].copy()
    if selected.empty:
        selected = scan[(scan["expected_focus"] < 0.0) & (scan["adverse_delta"] < OBS_DELTA)].head(3).copy()
        selected["diagnostic_only_reason"] = "no gate passed full criteria; kept as diagnostic no-submit rows"
    else:
        selected["diagnostic_only_reason"] = "passes tail capacity criteria but lacks train/OOF gate validation"

    files: list[str] = []
    for rec in selected.to_dict("records"):
        mask = gates[str(rec["gate"])]
        part = s2.loc[mask].copy()
        tag = str(rec["gate"]).replace("focus_support_ge_", "fsg").replace("subject_support_ge_", "ssg").replace("nearest_support_ge_", "nsg")
        files.append(materialize(sample, base_e95, full_e216_e95, part, tag[:48]))
    if not selected.empty:
        selected = selected.copy()
        selected["diagnostic_submission_file"] = files

    scan.to_csv(SCAN_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)

    cols = [
        "gate",
        "n_cells",
        "expected_focus",
        "adverse_delta",
        "adverse_over_observed",
        "support_prob_focus_weighted",
        "sim_prob_loss",
        "sim_prob_ge_half_obs",
        "sim_prob_ge_obs",
        "tail_gate_pass",
        "diagnostic_submission_file",
        "diagnostic_only_reason",
    ]
    lines = [
        "# E220 S2 Support Tail Gate Audit",
        "",
        "## Question",
        "",
        "Can the E219 support/tail diagnosis be converted into a smaller S2 gate that reduces adverse capacity below the observed E216 miss while preserving expected signal?",
        "",
        "## Gate Scan",
        "",
        md(scan, [c for c in cols if c in scan.columns], n=30),
        "",
        "## Diagnostic Rows",
        "",
        md(selected, [c for c in cols if c in selected.columns], n=10),
        "",
        "## Decision",
        "",
    ]
    if scan["tail_gate_pass"].any():
        lines.append("- Some public-tail gates reduce adverse capacity below the observed E216 miss, but they are diagnostic-only because the gate is derived from public-feedback priors and has no OOF/trainable analogue yet.")
        lines.append("- Do not submit these files directly. Next step is to build an OOF-reproducible S2 support classifier and check whether it selects a similar cell subset.")
    else:
        lines.append("- No simple support/tail gate passes all criteria. E216 remains closed as a submission lane.")
    lines.append("- The important stress rule is now explicit: expected delta alone is insufficient; S2 support probability and adverse capacity must be gated before any masked-family S2 JEPA movement is trusted.")
    lines.append("")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")

    print("[scan]")
    print(scan.round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
