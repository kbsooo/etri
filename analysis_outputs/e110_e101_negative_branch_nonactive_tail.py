#!/usr/bin/env python3
"""E110 E101-negative branch non-active tail audit.

E109 closed the obvious E101 tie/loss rescue: do not push the same active
Q2/S3 rollback line harder. The remaining question is sharper:

If E101 ties or loses because its 50 active labels failed, can the older E89
diffuse-tail hypothesis still be isolated outside those active cells, or does a
negative E101 result simply leave E95 as the only supported action?

This script builds E95-relative non-active grafts and active-restored E89/E85
variants, then tests them with the existing structural, E95-conditioned tail
transfer, and E109 active hard-label loss diagnostics. It does not use public
labels beyond the already logged E72/E95 observations.
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
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e101_q2s3_tail_graft_probe as e101  # noqa: E402
import e109_e101_tie_loss_label_world_audit as e109  # noqa: E402


CELLS_IN = OUT / "e105_e101_public_label_breakeven_cells.csv"

SCAN_OUT = OUT / "e110_e101_negative_branch_nonactive_tail_scan.csv"
ACTIVE_OUT = OUT / "e110_e101_negative_branch_active_worlds.csv"
SUMMARY_OUT = OUT / "e110_e101_negative_branch_nonactive_tail_summary.csv"
TRANSFER_OUT = OUT / "e110_e101_negative_branch_nonactive_tail_transfer.csv"
DECISION_OUT = OUT / "e110_e101_negative_branch_nonactive_tail_decision.csv"
REPORT_OUT = OUT / "e110_e101_negative_branch_nonactive_tail_report.md"
SUBMISSION_PREFIX = "submission_e110_e101neg_nonactive_tail"

EPS = 1.0e-6


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for rec in frame.to_dict("records"):
        vals: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                vals.append("")
            elif isinstance(value, (float, np.floating)):
                vals.append(format(float(value), floatfmt))
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def target_mask(n_rows: int, scope: str) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    if scope == "all":
        mask[:, :] = True
    elif scope == "q2s3":
        mask[:, [TARGETS.index("Q2"), TARGETS.index("S3")]] = True
    elif scope == "q2":
        mask[:, TARGETS.index("Q2")] = True
    elif scope == "s3":
        mask[:, TARGETS.index("S3")] = True
    elif scope == "s1s2s3":
        mask[:, [TARGETS.index("S1"), TARGETS.index("S2"), TARGETS.index("S3")]] = True
    else:
        raise KeyError(scope)
    return mask


def active_mask_from_cells(sample: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    cells = e109.attach_priors(pd.read_csv(CELLS_IN))
    target_index = {target: i for i, target in enumerate(TARGETS)}
    mask = np.zeros((len(sample), len(TARGETS)), dtype=bool)
    rows = cells["sub_idx"].to_numpy(dtype=int)
    cols = cells["target"].map(target_index).to_numpy(dtype=int)
    mask[rows, cols] = True
    if int(mask.sum()) != len(cells):
        raise RuntimeError("active mask/cell table mismatch")
    return cells, mask


def build_tail_state(refs: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    e72_delta, e72_weight, wrong_is_zero, wrong_is_one = e95mod.e72_adverse_setup(
        refs["mixmin"], refs["failed_e72"]
    )
    return e72_delta, e72_weight, wrong_is_zero, wrong_is_one


def add_row(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
) -> None:
    pred = clip_prob(pred)
    key = e101.pred_key(pred)
    if key in seen:
        pred_index = seen[key]
    else:
        pred_index = len(preds)
        seen[key] = pred_index
        preds.append(pred)
    tag = e83.stable_tag(pred, f"e110_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": 0, "tag": tag, **rec})


def build_candidates(sample: pd.DataFrame) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], pd.DataFrame, np.ndarray]:
    refs = e101.build_refs(sample)
    refs["e101"] = e101.load_pred(e101.SUBMISSION_PREFIX + "_177569bc.csv", sample)
    refs["e108_amp050"] = e101.load_pred("submission_e108_if_e101win_amp050_079aab57.csv", sample)
    refs["e108_strict_amp038"] = e101.load_pred("submission_e108_if_e101win_strict_amp038_64514c53.csv", sample)

    cells, active_mask = active_mask_from_cells(sample)
    e95 = refs["e95"]
    e95_z = logit(e95)

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [refs["mixmin"]]
    seen: dict[str, int] = {e101.pred_key(refs["mixmin"]): 0}

    for name in ["mixmin", "e95", "e101", "e108_amp050", "e108_strict_amp038", "e89", "e85", "e90", "e86"]:
        add_row(
            rows,
            preds,
            seen,
            refs[name],
            {
                "strategy": "control",
                "source": name,
                "base": name,
                "fallback": "",
                "selector": "",
                "target_scope": "",
                "graft_alpha": np.nan,
                "selected_cells": int((np.abs(logit(refs[name]) - e95_z) > 1.0e-9).sum()),
                "selected_rows": int(np.any(np.abs(logit(refs[name]) - e95_z) > 1.0e-9, axis=1).sum()),
            },
        )

    # Keep E89/E85's non-active movement, but undo the 50 E101-active cells.
    for base_name in ["e89", "e85"]:
        base = refs[base_name].copy()
        for restore_name in ["e95", "e90", "e86"]:
            pred = base.copy()
            pred[active_mask] = refs[restore_name][active_mask]
            add_row(
                rows,
                preds,
                seen,
                pred,
                {
                    "strategy": "active_restored_tail",
                    "source": base_name,
                    "base": base_name,
                    "fallback": restore_name,
                    "selector": "restore_e101_active",
                    "target_scope": "active_q2s3",
                    "graft_alpha": 1.0,
                    "selected_cells": int(active_mask.sum()),
                    "selected_rows": int(np.any(active_mask, axis=1).sum()),
                },
            )

    # Move from E95 toward older structural/tail candidates, but only outside
    # the E101-active cells. This asks whether the residual diffuse tail is
    # separable after the active hard-label failure is removed.
    for source_name in ["e89", "e85", "e90", "e86"]:
        source = refs[source_name]
        source_z = logit(source)
        changed = np.abs(source_z - e95_z) > 1.0e-9
        for scope in ["q2s3", "s3", "q2", "s1s2s3", "all"]:
            selector = changed & ~active_mask & target_mask(len(sample), scope)
            if int(selector.sum()) == 0:
                continue
            for alpha in [0.25, 0.50, 0.75, 1.00]:
                pred = sigmoid(e95_z + alpha * (source_z - e95_z) * selector)
                add_row(
                    rows,
                    preds,
                    seen,
                    pred,
                    {
                        "strategy": "nonactive_tail_graft",
                        "source": "e95",
                        "base": "e95",
                        "fallback": source_name,
                        "selector": f"nonactive_{scope}_{source_name}",
                        "target_scope": scope,
                        "graft_alpha": alpha,
                        "selected_cells": int(selector.sum()),
                        "selected_rows": int(np.any(selector, axis=1).sum()),
                    },
                )

    return pd.DataFrame(rows), preds, refs, cells, active_mask


def active_world_summary(
    sample: pd.DataFrame,
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    cells: pd.DataFrame,
) -> pd.DataFrame:
    target_index = {target: i for i, target in enumerate(TARGETS)}
    row_idx = cells["sub_idx"].to_numpy(dtype=int)
    col_idx = cells["target"].map(target_index).to_numpy(dtype=int)
    probs: dict[str, np.ndarray] = {}
    for rec in rows.drop_duplicates("pred_index").to_dict("records"):
        idx = int(rec["pred_index"])
        probs[f"p{idx}"] = clip_prob(preds[idx][row_idx, col_idx])

    # Keep reference names for the outcome definition and easier report tables.
    tag_to_idx = rows.drop_duplicates("pred_index").set_index("tag")["pred_index"].to_dict()
    probs["e95"] = clip_prob(e101.load_pred(e101.E95_FILE, sample)[row_idx, col_idx])
    probs["e101"] = clip_prob(e101.load_pred(e101.SUBMISSION_PREFIX + "_177569bc.csv", sample)[row_idx, col_idx])

    deltas = e109.candidate_label_deltas(probs)
    labels = e109.simulate_labels(cells, "subject")
    d0_e101, d1_e101 = deltas["e101"]
    e101_delta = (
        np.where(labels, d1_e101.reshape(1, -1), d0_e101.reshape(1, -1)).sum(axis=1)
        / e109.TOTAL_TEST_CELLS
    )
    active = e109.candidate_summary(labels, e101_delta, "subject", deltas)
    active = active[active["outcome"].isin(["tie", "small_loss", "large_loss"])].copy()

    idx_to_meta = rows.drop_duplicates("pred_index").set_index("pred_index")
    meta_rows: list[dict[str, Any]] = []
    for rec in active.to_dict("records"):
        cand = str(rec["candidate"])
        if not cand.startswith("p"):
            continue
        pred_index = int(cand[1:])
        meta = idx_to_meta.loc[pred_index].to_dict()
        meta_rows.append({**meta, **rec, "pred_index": pred_index})
    out = pd.DataFrame(meta_rows)
    if out.empty:
        raise RuntimeError("no active-world rows")
    return out


def classify(scan: pd.DataFrame, active: pd.DataFrame, transfer: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    transfer_wide = (
        transfer[transfer["filter"].isin(["broad_plausible", "broad_q2s3", "tight_plausible", "near_unit_tail"])]
        .pivot_table(
            index="pred_index",
            columns="filter",
            values=["mean_vs_e95", "p95_vs_e95", "beat_e95_rate"],
            aggfunc="first",
        )
    )
    transfer_wide.columns = [f"{metric}_{filter_name}" for metric, filter_name in transfer_wide.columns]
    transfer_wide = transfer_wide.reset_index()

    active_wide = active.pivot_table(
        index="pred_index",
        columns="outcome",
        values=["active_mean_vs_e101", "active_p95_vs_e101", "active_beat_e101_rate"],
        aggfunc="first",
    )
    active_wide.columns = [f"{metric}_{outcome}" for metric, outcome in active_wide.columns]
    active_wide = active_wide.reset_index()

    out = scan.merge(transfer_wide, on="pred_index", how="left").merge(active_wide, on="pred_index", how="left")
    out["e110_active_loss_safe"] = (
        (out["active_mean_vs_e101_small_loss"] < 0.0)
        & (out["active_p95_vs_e101_small_loss"] <= 0.0)
        & (out["active_mean_vs_e101_large_loss"] < 0.0)
        & (out["active_p95_vs_e101_large_loss"] <= 0.0)
    )
    out["e110_strict_candidate"] = (
        out["strategy"].ne("control")
        & out["strict_gate"].fillna(False).astype(bool)
        & out["deployable_gate"].fillna(False).astype(bool)
        & out["e110_active_loss_safe"].fillna(False).astype(bool)
        & (out["mean_vs_e95_broad_plausible"] < 0.0)
        & (out["p95_vs_e95_broad_plausible"] <= 0.0)
        & (out["beat_e95_rate_broad_plausible"] >= 0.75)
    )
    out["e110_sensor_candidate"] = (
        out["strategy"].ne("control")
        & out["strict_gate"].fillna(False).astype(bool)
        & out["deployable_gate"].fillna(False).astype(bool)
        & (out["active_mean_vs_e101_small_loss"] < 0.0)
        & (out["mean_vs_e95_broad_q2s3"] < 0.0)
        & (out["beat_e95_rate_broad_q2s3"] >= 0.50)
    )

    decision_cols = [
        "pred_index",
        "tag",
        "strategy",
        "base",
        "fallback",
        "selector",
        "target_scope",
        "graft_alpha",
        "selected_cells",
        "strict_gate",
        "deployable_gate",
        "e110_active_loss_safe",
        "e110_strict_candidate",
        "e110_sensor_candidate",
        "all_delta_vs_mixmin",
        "mean_vs_e95_broad_plausible",
        "p95_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
        "mean_vs_e95_broad_q2s3",
        "beat_e95_rate_broad_q2s3",
        "active_mean_vs_e101_tie",
        "active_p95_vs_e101_tie",
        "active_mean_vs_e101_small_loss",
        "active_p95_vs_e101_small_loss",
        "active_mean_vs_e101_large_loss",
        "active_p95_vs_e101_large_loss",
    ]
    decision = out[decision_cols].drop_duplicates("pred_index").copy()
    decision = decision.sort_values(
        [
            "e110_strict_candidate",
            "e110_sensor_candidate",
            "e110_active_loss_safe",
            "mean_vs_e95_broad_plausible",
            "p95_vs_e95_broad_plausible",
        ],
        ascending=[False, False, False, True, True],
    )
    return out, decision


def materialize(decision: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    strict = decision[decision["e110_strict_candidate"].fillna(False).astype(bool)].copy()
    if strict.empty:
        return None
    chosen = strict.iloc[0]
    pred = preds[int(chosen["pred_index"])]
    file_tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{file_tag}.csv"
    sub = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        sub[target] = pred[:, j]
    sub.to_csv(out, index=False)
    return out


def write_report(scan: pd.DataFrame, active: pd.DataFrame, decision: pd.DataFrame, selected_path: Path | None) -> None:
    control = decision[decision["strategy"].eq("control")].copy()
    best = decision.head(20)
    active_focus = active[
        active["outcome"].isin(["tie", "small_loss", "large_loss"])
        & active["strategy"].isin(["control", "active_restored_tail", "nonactive_tail_graft"])
    ].sort_values(["outcome", "active_mean_vs_e101"]).groupby("outcome", as_index=False).head(12)
    summary = (
        decision.groupby(["strategy", "fallback", "target_scope"], dropna=False)
        .agg(
            rows=("pred_index", "count"),
            active_loss_safe=("e110_active_loss_safe", "sum"),
            sensor_candidates=("e110_sensor_candidate", "sum"),
            strict_candidates=("e110_strict_candidate", "sum"),
            best_broad_mean_vs_e95=("mean_vs_e95_broad_plausible", "min"),
            best_broad_p95_vs_e95=("p95_vs_e95_broad_plausible", "min"),
            best_small_loss_active_mean=("active_mean_vs_e101_small_loss", "min"),
        )
        .reset_index()
        .sort_values(["strict_candidates", "sensor_candidates", "best_broad_mean_vs_e95"], ascending=[False, False, True])
    )

    report = f"""# E110 E101-Negative Branch Non-Active Tail Audit

## Question

E109 says an E101 tie/loss should not be rescued by amplifying the same active
Q2/S3 rollback cells. E110 asks whether the remaining E89 diffuse-tail
hypothesis can be isolated outside those cells.

## Result

- total unique candidates: `{decision['pred_index'].nunique()}`
- active-loss-safe non-control rows: `{int(decision[decision['strategy'].ne('control')]['e110_active_loss_safe'].sum())}`
- sensor candidates: `{int(decision['e110_sensor_candidate'].sum())}`
- strict candidates: `{int(decision['e110_strict_candidate'].sum())}`
- materialized submission: `{selected_path.name if selected_path else 'none'}`

## Summary By Family

{md_table(summary, '.9f')}

## Controls

{md_table(control[['tag','base','selected_cells','all_delta_vs_mixmin','mean_vs_e95_broad_plausible','p95_vs_e95_broad_plausible','beat_e95_rate_broad_plausible','active_mean_vs_e101_small_loss','active_p95_vs_e101_small_loss','active_mean_vs_e101_large_loss','active_p95_vs_e101_large_loss']], '.9f')}

## Best Decision Rows

{md_table(best[['tag','strategy','base','fallback','selector','target_scope','graft_alpha','selected_cells','e110_active_loss_safe','e110_sensor_candidate','e110_strict_candidate','all_delta_vs_mixmin','mean_vs_e95_broad_plausible','p95_vs_e95_broad_plausible','beat_e95_rate_broad_plausible','mean_vs_e95_broad_q2s3','beat_e95_rate_broad_q2s3','active_mean_vs_e101_small_loss','active_p95_vs_e101_small_loss']], '.9f')}

## Active-World Behavior

{md_table(active_focus[['outcome','tag','strategy','base','fallback','selector','active_mean_vs_e101','active_p95_vs_e101','active_beat_e101_rate','active_mean_vs_e95','active_p95_vs_e95','rank_vs_e101']], '.9f')}

## Interpretation

If strict candidates are zero, then a negative E101 public result should not
automatically route to full E89 or a non-active E89 graft. The active-cell
failure can be separated diagnostically, but the remaining diffuse-tail movement
does not yet clear E95-conditioned downside stress.

If a strict candidate is materialized, it should be used only after E101
tie/loss and only as a test of non-active diffuse-tail allocation, not as a
general successor to E95.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, refs, cells, _ = build_candidates(sample)
    tail_state = build_tail_state(refs)
    scan = e101.score_candidates(sample, rows, preds, refs, tail_state)
    transfer = e101.build_transfer_summary(sample, scan, preds, refs, tail_state)
    active = active_world_summary(sample, rows, preds, cells)
    scan, decision = classify(scan, active, transfer)
    selected_path = materialize(decision, preds, sample)

    scan.to_csv(SCAN_OUT, index=False)
    active.to_csv(ACTIVE_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    decision.to_csv(DECISION_OUT, index=False)
    summary = (
        decision.groupby(["strategy", "fallback", "target_scope"], dropna=False)
        .agg(
            rows=("pred_index", "count"),
            active_loss_safe=("e110_active_loss_safe", "sum"),
            sensor_candidates=("e110_sensor_candidate", "sum"),
            strict_candidates=("e110_strict_candidate", "sum"),
            best_broad_mean_vs_e95=("mean_vs_e95_broad_plausible", "min"),
            best_broad_p95_vs_e95=("p95_vs_e95_broad_plausible", "min"),
        )
        .reset_index()
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    write_report(scan, active, decision, selected_path)

    assert decision["pred_index"].is_unique
    controls = set(decision.loc[decision["strategy"].eq("control"), "base"])
    assert {"e95", "e101", "e89", "e85", "e90", "e86"}.issubset(controls)
    assert int(decision.loc[decision["strategy"].ne("control"), "e110_active_loss_safe"].sum()) > 0

    print(f"wrote {SCAN_OUT}")
    print(f"wrote {ACTIVE_OUT}")
    print(f"wrote {TRANSFER_OUT}")
    print(f"wrote {DECISION_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")
    if selected_path:
        print(f"materialized {selected_path}")
    else:
        print("materialized none")


if __name__ == "__main__":
    main()
