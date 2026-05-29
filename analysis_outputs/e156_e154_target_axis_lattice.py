#!/usr/bin/env python3
"""E156: does E154's repaired body decompose into stable target axes?

E155 showed that E154 is not an exact point: lower-amplitude variants of the
E144->E154 body still pass the all-four health gate. E156 asks a sharper
question before creating another submission:

Can a smaller target-axis combination than the E155 25% diagonal carry the same
health signal, or is E155 already the minimal coherent body?

This is a public-free lattice over target-wise amplitudes of the E144->E154
body. It is intentionally a diagnostic first. A file is materialized only if a
candidate beats E144 locally, passes the all-four gate, and uses less total body
norm than E155.
"""

from __future__ import annotations

from itertools import product
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
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e153_gate_intersection_failure_atlas as e153  # noqa: E402
import e155_e154_branch_body_ablation as e155  # noqa: E402


SCAN_OUT = OUT / "e156_e154_target_axis_lattice_scan.csv"
SUMMARY_OUT = OUT / "e156_e154_target_axis_lattice_summary.csv"
REPORT_OUT = OUT / "e156_e154_target_axis_lattice_report.md"
SUBMISSION_PREFIX = "submission_e156_targetaxis"

EPS = 1.0e-6
LEVELS = [0.0, 0.25, 0.50, 0.75, 1.0]
MIN_LOCAL_EDGE = -1.0e-5


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def load_aligned(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
) -> None:
    key = e138.pred_key(pred)
    if key in seen:
        pred_index = seen[key]
    else:
        pred_index = len(preds)
        seen[key] = pred_index
        preds.append(pred)
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": e83.stable_tag(pred, "e156_"), **rec})


def axis_metadata(body: np.ndarray) -> tuple[list[str], dict[str, float]]:
    norms: dict[str, float] = {}
    active: list[str] = []
    for idx, target in enumerate(TARGETS):
        norm = float(np.linalg.norm(body[:, idx]))
        norms[target] = norm
        if norm > 1.0e-12:
            active.append(target)
    return active, norms


def build_lattice(sample: pd.DataFrame, refs: dict[str, np.ndarray]) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, Any]]:
    e144_logit = logit(refs["e144"])
    e154_logit = logit(refs["e154"])
    body = e154_logit - e144_logit
    body_norm = float(np.linalg.norm(body.reshape(-1)))
    active_targets, target_norms = axis_metadata(body)
    target_to_idx = {target: idx for idx, target in enumerate(TARGETS)}

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = []
    seen: dict[str, int] = {}

    controls = {
        "control_e95": refs["e95"],
        "control_e144": refs["e144"],
        "control_e154": refs["e154"],
        "control_e155": refs["e155"],
    }
    for strategy, pred in controls.items():
        move = logit(pred) - e144_logit
        alpha_rec = {f"alpha_{target}": np.nan for target in TARGETS}
        add_pred(
            rows,
            preds,
            seen,
            pred,
            {
                "strategy": strategy,
                "target_axes": "",
                "active_axis_count": int((np.linalg.norm(move, axis=0) > 1.0e-12).sum()),
                "alpha_sum": np.nan,
                "alpha_mean_active": np.nan,
                **alpha_rec,
                **e155.body_metrics(pred, refs, body, body_norm),
            },
        )

    for levels in product(LEVELS, repeat=len(active_targets)):
        scaled = np.zeros_like(body)
        active_axis_count = 0
        alpha_rec = {f"alpha_{target}": 0.0 for target in TARGETS}
        active_axis_names: list[str] = []
        for target, alpha in zip(active_targets, levels, strict=False):
            idx = target_to_idx[target]
            alpha_rec[f"alpha_{target}"] = float(alpha)
            if float(alpha) > 0.0:
                active_axis_count += 1
                active_axis_names.append(target)
            scaled[:, idx] = float(alpha) * body[:, idx]
        pred = clip_prob(sigmoid(e144_logit + scaled))
        add_pred(
            rows,
            preds,
            seen,
            pred,
            {
                "strategy": "target_axis_lattice",
                "target_axes": "+".join(active_axis_names),
                "active_axis_count": active_axis_count,
                "alpha_sum": float(sum(levels)),
                "alpha_mean_active": float(sum(levels) / active_axis_count) if active_axis_count else 0.0,
                **alpha_rec,
                **e155.body_metrics(pred, refs, body, body_norm),
            },
        )

    meta = {
        "active_targets": ",".join(active_targets),
        "body_norm": body_norm,
        **{f"body_norm_{target}": norm for target, norm in target_norms.items()},
    }
    return pd.DataFrame(rows), preds, meta


def add_e156_flags(scan: pd.DataFrame) -> pd.DataFrame:
    out = e155.add_health_flags(scan, e144_all_minus=float(scan.loc[scan["strategy"].eq("control_e144"), "all_minus_base"].iloc[0]))
    e155_body = float(scan.loc[scan["strategy"].eq("control_e155"), "body_norm_ratio"].iloc[0])
    e155_all = float(scan.loc[scan["strategy"].eq("control_e155"), "all_minus_base"].iloc[0])
    out["beats_e155_local"] = out["all_minus_base"].lt(e155_all - 1.0e-12)
    out["uses_less_body_than_e155"] = out["body_norm_ratio"].lt(e155_body - 1.0e-12)
    out["e156_strict_candidate"] = (
        out["strategy"].eq("target_axis_lattice")
        & out["all_four_health"].fillna(False).astype(bool)
        & out["beats_e144_local"].fillna(False).astype(bool)
        & out["all_minus_base"].lt(MIN_LOCAL_EDGE)
    )
    out["e156_minbody_submit"] = out["e156_strict_candidate"] & out["uses_less_body_than_e155"]
    return out


def summarize(scan: pd.DataFrame) -> pd.DataFrame:
    variants = scan[scan["strategy"].eq("target_axis_lattice")].copy()
    rows: list[dict[str, Any]] = []
    for axis_count, group in variants.groupby("active_axis_count"):
        strict = group[group["e156_strict_candidate"].fillna(False).astype(bool)].copy()
        minbody = group[group["e156_minbody_submit"].fillna(False).astype(bool)].copy()
        all_four = group[group["all_four_health"].fillna(False).astype(bool)].copy()
        best = group.sort_values(["all_minus_base", "body_norm_ratio"], ascending=[True, True]).iloc[0]
        lowest_strict = strict.sort_values(["body_norm_ratio", "all_minus_base"], ascending=[True, True]).head(1)
        rows.append(
            {
                "active_axis_count": int(axis_count),
                "rows": int(len(group)),
                "all_four": int(len(all_four)),
                "strict_candidates": int(len(strict)),
                "minbody_submit": int(len(minbody)),
                "best_all_minus_base": float(best["all_minus_base"]),
                "best_body_norm_ratio": float(best["body_norm_ratio"]),
                "best_axes": str(best["target_axes"]),
                "lowest_strict_tag": str(lowest_strict["tag"].iloc[0]) if len(lowest_strict) else "",
                "lowest_strict_body_norm_ratio": float(lowest_strict["body_norm_ratio"].iloc[0]) if len(lowest_strict) else np.nan,
                "lowest_strict_all_minus_base": float(lowest_strict["all_minus_base"].iloc[0]) if len(lowest_strict) else np.nan,
                "lowest_strict_axes": str(lowest_strict["target_axes"].iloc[0]) if len(lowest_strict) else "",
            }
        )
    return pd.DataFrame(rows).sort_values("active_axis_count")


def select_submission(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["e156_minbody_submit"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        ["body_norm_ratio", "active_axis_count", "post101_p95_vs_e95_e101_sensor", "all_minus_base"],
        ascending=[True, True, True, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    tag = str(chosen["tag"]).split("_")[-1]
    path = OUT / f"{SUBMISSION_PREFIX}_{tag}.csv"
    sub = sample[KEYS].copy()
    sub[TARGETS] = clip_prob(pred)
    sub.to_csv(path, index=False)
    return path


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40) -> str:
    if frame.empty:
        return "_empty_"
    if cols is not None:
        keep = [col for col in cols if col in frame.columns]
        frame = frame[keep]
    return e155.md_table(frame.head(n), list(frame.columns), n=n)


def write_report(scan: pd.DataFrame, summary: pd.DataFrame, meta: dict[str, Any], submission_path: Path | None) -> None:
    variants = scan[scan["strategy"].eq("target_axis_lattice")].copy()
    strict = variants[variants["e156_strict_candidate"].fillna(False).astype(bool)].copy()
    minbody = variants[variants["e156_minbody_submit"].fillna(False).astype(bool)].copy()
    controls = scan[scan["strategy"].astype(str).str.startswith("control_")].copy()
    if submission_path is not None:
        decision = f"Materialized `{submission_path.name}` because it is all-four, beats E144, and uses less body norm than E155."
    elif len(minbody):
        decision = "Min-body rows exist, but no file was selected by the deterministic selector."
    elif len(strict):
        decision = "Strict target-axis rows exist, but none use less body norm than E155. E155 remains the minimal conservative repaired-body candidate."
    else:
        decision = "No strict target-axis row. The E154/E155 repaired body is not separable into a smaller target-axis law under this lattice."

    front = variants.sort_values(
        ["e156_minbody_submit", "e156_strict_candidate", "body_norm_ratio", "all_minus_base"],
        ascending=[False, False, True, True],
    )
    lines = [
        "# E156 E154 Target-Axis Lattice",
        "",
        "## Question",
        "",
        "Can the E154 repaired body be decomposed into a smaller target-axis combination than E155's 25% diagonal, or is E155 already the minimal coherent low-amplitude repair?",
        "",
        "## Body",
        "",
        f"- active target axes: `{meta['active_targets']}`.",
        f"- E144->E154 body norm: `{meta['body_norm']:.12f}`.",
        "",
        "## Controls",
        "",
        md_table(
            controls.sort_values("all_minus_base"),
            [
                "strategy",
                "all_minus_base",
                "all_four_health",
                "body_norm_ratio",
                "post101_p95_vs_e95_e101_sensor",
                "e72_plausible_gap_vs_e95",
                "tag",
            ],
            10,
        ),
        "",
        "## Summary By Active Target Count",
        "",
        md_table(summary, list(summary.columns), 20),
        "",
        "## Frontier Rows",
        "",
        md_table(
            front,
            [
                "tag",
                "target_axes",
                "active_axis_count",
                "all_minus_base",
                "all_four_health",
                "e156_strict_candidate",
                "e156_minbody_submit",
                "body_norm_ratio",
                "beats_e155_local",
                "post101_p95_vs_e95_e101_sensor",
                "e72_plausible_gap_vs_e95",
                "alpha_Q1",
                "alpha_Q3",
                "alpha_S2",
                "alpha_S3",
                "alpha_S4",
            ],
            60,
        ),
        "",
        "## Decision",
        "",
        decision,
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    refs["e144"] = load_aligned("submission_e144_activeboundary_d7b4b331.csv", sample)
    refs["e154"] = load_aligned("submission_e154_s3repair_9f2e2e73.csv", sample)
    refs["e155"] = load_aligned("submission_e155_bodytemp_d27e7965.csv", sample)
    _state, density, tail_state = e153.e152.setup_state(sample, refs)

    rows, preds, meta = build_lattice(sample, refs)
    labels, worlds, views, stress_state = e89mod.build_stress_state(sample, refs["mixmin"])
    # The default E83 scorer keeps only the best 700 rows for expensive
    # non-anchor diagnostics. E156's kill question is about low-body candidates,
    # which can be locally modest and would otherwise be left unscored.
    e83.e70.MAX_NONANCHOR_ROWS = max(int(e83.e70.MAX_NONANCHOR_ROWS), len(rows) + 10)
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, stress_state)
    scan = e130.add_tail_and_veto_metrics(scan, preds, refs, density, tail_state)
    transfer = e130.post_e101_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = e130.merge_transfer(scan, transfer)
    scan = add_e156_flags(scan)

    summary = summarize(scan)
    submission_path = select_submission(scan, preds, sample)
    scan["materialized_submission"] = False
    if submission_path is not None:
        suffix = submission_path.stem.split("_")[-1]
        scan["materialized_submission"] = scan["tag"].astype(str).str.endswith(suffix)

    scan.to_csv(SCAN_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, summary, meta, submission_path)

    variants = scan[scan["strategy"].eq("target_axis_lattice")].copy()
    print(
        {
            "rows": int(len(scan)),
            "variants": int(len(variants)),
            "all_four": int(variants["all_four_health"].fillna(False).astype(bool).sum()),
            "strict_candidates": int(variants["e156_strict_candidate"].fillna(False).astype(bool).sum()),
            "minbody_submit": int(variants["e156_minbody_submit"].fillna(False).astype(bool).sum()),
            "submission": str(submission_path) if submission_path is not None else None,
        }
    )
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
