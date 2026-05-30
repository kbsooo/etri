#!/usr/bin/env python3
"""E258: body-vs-rollback attribution atlas for the E247 public win.

E247 is public-positive, but it is not a pure smoothing file. It is:

    E95 -> E224 capped Q3/S4 JEPA body
    E224 -> E247 Q3 feature-NN1 smoothing rollback

This audit separates those two movements and compares them with E256's
high-amplitude rollback follow-up. It creates no submission and uses no new
public LB.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e162_branch_readability_flip_thresholds as e162  # noqa: E402
import e222_e211_support_tail_audit as e222  # noqa: E402


E95_FILE = "submission_e95_hardtail_541e3973.csv"
E154_FILE = "submission_e154_s3repair_9f2e2e73.csv"
E224_FILE = "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E247_FILE = "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv"
E256_FILE = "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv"

COMPONENT_OUT = OUT / "e258_e247_attribution_component_summary.csv"
TARGET_OUT = OUT / "e258_e247_attribution_target_summary.csv"
OVERLAP_OUT = OUT / "e258_e247_attribution_overlap_summary.csv"
TOP_CELLS_OUT = OUT / "e258_e247_attribution_top_cells.csv"
REPORT_OUT = OUT / "e258_e247_body_rollback_attribution_report.md"

EPS = 1.0e-12


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def load_prob(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def flat(x: np.ndarray) -> np.ndarray:
    return np.asarray(x, dtype=np.float64).reshape(-1)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = flat(a)
    bb = flat(b)
    den = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if den <= EPS:
        return float("nan")
    return float(np.dot(aa, bb) / den)


def summarize_vector(component_id: str, p_new: np.ndarray, p_base: np.ndarray) -> dict[str, Any]:
    dlogit = logit(p_new) - logit(p_base)
    dprob = p_new - p_base
    moved = np.abs(dlogit) > 1.0e-10
    total_abs_logit = float(np.abs(dlogit).sum())
    rec: dict[str, Any] = {
        "component_id": component_id,
        "moved_cells": int(moved.sum()),
        "moved_rows": int(np.unique(np.where(moved)[0]).size),
        "l1_abs_logit": total_abs_logit,
        "l2_logit": float(np.linalg.norm(flat(dlogit))),
        "mean_abs_logit": float(np.abs(dlogit).mean()),
        "max_abs_logit": float(np.abs(dlogit).max()),
        "l1_abs_prob": float(np.abs(dprob).sum()),
        "mean_abs_prob": float(np.abs(dprob).mean()),
        "max_abs_prob": float(np.abs(dprob).max()),
    }
    moved_targets = []
    for j, target in enumerate(TARGETS):
        target_abs = float(np.abs(dlogit[:, j]).sum())
        target_cells = int((np.abs(dlogit[:, j]) > 1.0e-10).sum())
        rec[f"{target}_abs_logit"] = target_abs
        rec[f"{target}_abs_share"] = float(target_abs / max(total_abs_logit, EPS))
        rec[f"{target}_moved_cells"] = target_cells
        if target_cells:
            moved_targets.append(target)
    rec["targets_moved"] = ",".join(moved_targets)
    return rec


def pair_summary(
    component_id: str,
    p_new: np.ndarray,
    p_base: np.ndarray,
    base_name: str,
    priors: dict[str, np.ndarray],
    sample: pd.DataFrame,
    note: str,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    spec = e222.Candidate(
        candidate_id=component_id,
        file_name=component_id,
        anchor_file=base_name,
        family="e258_e247_body_rollback_attribution",
        status="diagnostic",
        note=note,
    )
    rec, target_df, top = e222.pair_audit(spec, "component_pair", p_new, p_base, base_name, priors, sample)
    rec.update(summarize_vector(component_id, p_new, p_base))
    return rec, target_df, top


def overlap_record(
    component_id: str,
    body: np.ndarray,
    rollback: np.ndarray,
    total: np.ndarray,
    selector_mask: np.ndarray,
) -> dict[str, Any]:
    b = np.asarray(body, dtype=np.float64)
    r = np.asarray(rollback, dtype=np.float64)
    t = np.asarray(total, dtype=np.float64)
    mask = selector_mask.astype(bool)
    body_on = b[mask]
    rollback_on = r[mask]
    denom_body_on = float(np.abs(body_on).sum())
    denom_body_all = float(np.abs(b).sum())
    return {
        "component_id": component_id,
        "selected_cells": int(mask.sum()),
        "cos_body_rollback_all": cosine(b, r),
        "cos_body_rollback_selected": cosine(body_on, rollback_on),
        "cos_rollback_total": cosine(r, t),
        "rollback_l2_over_body_l2": float(np.linalg.norm(flat(r)) / max(np.linalg.norm(flat(b)), EPS)),
        "rollback_l2_over_total_l2": float(np.linalg.norm(flat(r)) / max(np.linalg.norm(flat(t)), EPS)),
        "selected_body_abs_share": float(denom_body_on / max(denom_body_all, EPS)),
        "rollback_abs_over_selected_body_abs": float(np.abs(rollback_on).sum() / max(denom_body_on, EPS)),
        "opposite_sign_share_selected": float(np.mean((body_on * rollback_on) < 0.0)) if mask.sum() else np.nan,
        "same_sign_share_selected": float(np.mean((body_on * rollback_on) > 0.0)) if mask.sum() else np.nan,
        "body_zero_share_selected": float(np.mean(np.abs(body_on) <= 1.0e-10)) if mask.sum() else np.nan,
        "median_abs_body_selected": float(np.median(np.abs(body_on))) if mask.sum() else np.nan,
        "median_abs_rollback_selected": float(np.median(np.abs(rollback_on))) if mask.sum() else np.nan,
    }


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    priors = e162.prior_arrays(sample)
    p = {
        "e95": load_prob(E95_FILE, sample),
        "e154": load_prob(E154_FILE, sample),
        "e224": load_prob(E224_FILE, sample),
        "e247": load_prob(E247_FILE, sample),
        "e256": load_prob(E256_FILE, sample),
    }

    components = [
        (
            "e224_body_vs_e95",
            p["e224"],
            p["e95"],
            E95_FILE,
            "Clean capped-Q3/S4 JEPA body relative to the previous E95 frontier.",
        ),
        (
            "e247_rollback_vs_e224",
            p["e247"],
            p["e224"],
            E224_FILE,
            "E247 Q3 feature-NN1 smoothing rollback added on top of E224.",
        ),
        (
            "e256_rollback_vs_e224",
            p["e256"],
            p["e224"],
            E224_FILE,
            "E256 high-amplitude constrained smoothing rollback added on top of E224.",
        ),
        (
            "e247_total_vs_e95",
            p["e247"],
            p["e95"],
            E95_FILE,
            "Observed public-positive E247 total movement relative to E95.",
        ),
        (
            "e256_total_vs_e95",
            p["e256"],
            p["e95"],
            E95_FILE,
            "E256 total movement relative to E95.",
        ),
        (
            "e224_body_vs_e154",
            p["e224"],
            p["e154"],
            E154_FILE,
            "E224 body relative to its E154 anchor.",
        ),
    ]

    component_rows: list[dict[str, Any]] = []
    target_parts: list[pd.DataFrame] = []
    top_parts: list[pd.DataFrame] = []
    for component_id, p_new, p_base, base_name, note in components:
        rec, target_df, top = pair_summary(component_id, p_new, p_base, base_name, priors, sample, note)
        component_rows.append(rec)
        if not target_df.empty:
            target_parts.append(target_df)
        if not top.empty:
            top_parts.append(top)

    component_summary = pd.DataFrame(component_rows)
    target_summary = pd.concat(target_parts, ignore_index=True) if target_parts else pd.DataFrame()
    top_cells = pd.concat(top_parts, ignore_index=True) if top_parts else pd.DataFrame()

    z = {name: logit(arr) for name, arr in p.items()}
    body = z["e224"] - z["e95"]
    rollback247 = z["e247"] - z["e224"]
    rollback256 = z["e256"] - z["e224"]
    total247 = z["e247"] - z["e95"]
    total256 = z["e256"] - z["e95"]
    overlap = pd.DataFrame(
        [
            overlap_record("e247_rollback_vs_e224", body, rollback247, total247, np.abs(rollback247) > 1.0e-10),
            overlap_record("e256_rollback_vs_e224", body, rollback256, total256, np.abs(rollback256) > 1.0e-10),
        ]
    )

    component_summary.to_csv(COMPONENT_OUT, index=False)
    target_summary.to_csv(TARGET_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    overlap.to_csv(OVERLAP_OUT, index=False)

    component_cols = [
        "component_id",
        "moved_cells",
        "targets_moved",
        "l2_logit",
        "l1_abs_logit",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
        "Q3_abs_share",
        "S4_abs_share",
    ]
    target_cols = [
        "candidate_id",
        "target",
        "moved_cells",
        "expected_focus",
        "adverse_delta",
        "support_prob_focus_swing_weighted",
        "top1_over_abs_expected",
    ]
    overlap_cols = [
        "component_id",
        "selected_cells",
        "cos_body_rollback_all",
        "cos_body_rollback_selected",
        "rollback_l2_over_body_l2",
        "rollback_l2_over_total_l2",
        "selected_body_abs_share",
        "rollback_abs_over_selected_body_abs",
        "opposite_sign_share_selected",
    ]

    e247_overlap = overlap[overlap["component_id"].eq("e247_rollback_vs_e224")].iloc[0]
    e256_overlap = overlap[overlap["component_id"].eq("e256_rollback_vs_e224")].iloc[0]
    lines = [
        "# E258 E247 Body/Rollback Attribution Atlas",
        "",
        "## Question",
        "",
        "E247 is public-positive, but did public reward the E224 capped-Q3/S4 body, the Q3 feature-NN1 rollback, or their interaction?",
        "",
        "## Component Summary",
        "",
        md_table(component_summary, component_cols, n=20),
        "",
        "## Target Summary",
        "",
        md_table(target_summary.sort_values(["candidate_id", "target"]), target_cols, n=60),
        "",
        "## Rollback vs Body Overlap",
        "",
        md_table(overlap, overlap_cols, n=10),
        "",
        "## Interpretation",
        "",
        f"- E247 rollback touches `{int(e247_overlap['selected_cells'])}` cells and is mostly an opposite-sign trim of E224 body on those cells: opposite-sign share `{float(e247_overlap['opposite_sign_share_selected']):.6f}`.",
        f"- E247 rollback L2 is `{float(e247_overlap['rollback_l2_over_body_l2']):.6f}` of the E224 body and `{float(e247_overlap['rollback_l2_over_total_l2']):.6f}` of the final E247 movement.",
        f"- E256 rollback touches `{int(e256_overlap['selected_cells'])}` cells and has opposite-sign share `{float(e256_overlap['opposite_sign_share_selected']):.6f}`.",
        "- Therefore E247 should be read as E224 body plus a Q3 tail correction, not as a standalone smoothing replacement.",
        "- Public E247 feedback alone cannot attribute the win. E224 is the clean body-attribution public question; E256 is the score-plus-information broad-vs-amplitude rollback question.",
        "",
        "## Decision",
        "",
        "- If the next slot prioritizes immediate score while staying inside the validated E247 mechanism, use E256.",
        "- If the next slot prioritizes explaining why E247 won, use E224 because it removes the Q3 rollback and isolates the body.",
        "- Do not build an E247/E256 blend before one of those attribution sensors is observed.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print("[E258 component summary]")
    print(component_summary[component_cols].round(9).to_string(index=False))
    print(f"\nwrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
