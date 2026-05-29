#!/usr/bin/env python3
"""E101 Q2/S3 tail graft probe.

E100 found that E89 is not a broad E95 successor. Its only live pocket is a
Q2/S3 diffuse-tail counterfactual: E89 beats E95 mostly when the E72 public-miss
budget is spread through Q2/S3-like cells rather than the hard-tail cells E95
localized.

This probe asks the smaller falsifiable question:

Can that E89 Q2/S3 pocket be isolated as a graft on top of E95, or is the whole
E89 file the only coherent public sensor for that world?

No public labels are fitted. The transfer check reuses E96 tail scenarios and
E99's E72+E95-conditioned alpha/lambda worlds.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub, logit  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e89_e86_e72_decontamination_scan as e89mod  # noqa: E402
import e94_soft_health_hard_tail_audit as e94  # noqa: E402
import e95_hard_tail_gate_scan as e95mod  # noqa: E402
import e96_public_miss_budget_tail_scenarios as e96mod  # noqa: E402
import e99_e95_conditioned_tail_transfer as e99mod  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


MIXMIN_FILE = "submission_mixmin_0c916bb4.csv"
E72_FILE = "submission_e72_topabs50_q2s3_gate_4e48cba2.csv"
E85_FILE = "submission_e85_inverse_conflict_pruned_58b23ed1.csv"
E86_FILE = "submission_e86_e85_consensus_a3f7c96f.csv"
E89_FILE = "submission_e89_e72decontam_00d7807f.csv"
E90_FILE = "submission_e90_e72pareto_28925de5.csv"
E95_FILE = "submission_e95_hardtail_541e3973.csv"
NOQ2_FILE = "submission_e87_noq2_source_consensus_a85c4e39.csv"

SCAN_OUT = OUT / "e101_q2s3_tail_graft_probe_scan.csv"
SUMMARY_OUT = OUT / "e101_q2s3_tail_graft_probe_summary.csv"
TRANSFER_OUT = OUT / "e101_q2s3_tail_graft_probe_transfer.csv"
REPORT_OUT = OUT / "e101_q2s3_tail_graft_probe_report.md"
SUBMISSION_PREFIX = "submission_e101_q2s3tail"

EPS = 1.0e-6
Q2 = TARGETS.index("Q2")
S3 = TARGETS.index("S3")
Q2S3 = [Q2, S3]
TRANSFER_FILTERS = {
    "broad_plausible": lambda x: x["is_broad_plausible"],
    "broad_q2s3": lambda x: x["is_broad_plausible"] & x["mask_name"].eq("q2s3"),
    "broad_not_q2s3": lambda x: x["is_broad_plausible"] & ~x["mask_name"].eq("q2s3"),
    "tight_plausible": lambda x: x["is_tight_plausible"],
    "near_unit_tail": lambda x: x["is_near_unit_tail"],
}


def md_table(frame: pd.DataFrame, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    headers = [str(c) for c in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for rec in frame.to_dict("records"):
        row: list[str] = []
        for col in frame.columns:
            value = rec[col]
            if pd.isna(value):
                row.append("")
            elif isinstance(value, (float, np.floating)):
                row.append(format(float(value), floatfmt))
            else:
                row.append(str(value))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(np.asarray(x, dtype=np.float64), -40.0, 40.0)))


def load_pred(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return clip_prob(load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64))


def pred_key(pred: np.ndarray) -> str:
    rounded = np.round(np.asarray(pred, dtype=np.float64), 12)
    return hashlib.sha256(rounded.tobytes()).hexdigest()


def target_scope_mask(n_rows: int, scope: str) -> np.ndarray:
    mask = np.zeros((n_rows, len(TARGETS)), dtype=bool)
    if scope == "q2":
        mask[:, Q2] = True
    elif scope == "s3":
        mask[:, S3] = True
    elif scope == "q2s3":
        mask[:, Q2S3] = True
    else:
        raise KeyError(scope)
    return mask


def positive_quantile_mask(values: np.ndarray, base_mask: np.ndarray, q: float) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    masked = arr[base_mask & (arr > 1.0e-12)]
    if len(masked) == 0:
        return np.zeros_like(base_mask, dtype=bool)
    cut = float(np.quantile(masked, q))
    return base_mask & (arr >= cut)


def add_pred(
    rows: list[dict[str, Any]],
    preds: list[np.ndarray],
    seen_pred: dict[str, int],
    pred: np.ndarray,
    rec: dict[str, Any],
    base_index: int = 0,
) -> None:
    key = pred_key(pred)
    if key in seen_pred:
        pred_index = seen_pred[key]
    else:
        pred_index = len(preds)
        seen_pred[key] = pred_index
        preds.append(pred)
    tag = e83.stable_tag(pred, f"e101_{rec['strategy']}_")
    rows.append({"pred_index": pred_index, "base_index": base_index, "tag": tag, **rec})


def build_refs(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    return {
        "mixmin": load_pred(MIXMIN_FILE, sample),
        "failed_e72": load_pred(E72_FILE, sample),
        "e85": load_pred(E85_FILE, sample),
        "e86": load_pred(E86_FILE, sample),
        "noq2": load_pred(NOQ2_FILE, sample),
        "e90": load_pred(E90_FILE, sample),
        "e89": load_pred(E89_FILE, sample),
        "e95": load_pred(E95_FILE, sample),
    }


def build_candidates(
    sample: pd.DataFrame,
) -> tuple[pd.DataFrame, list[np.ndarray], dict[str, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    refs = build_refs(sample)
    mixmin = refs["mixmin"]
    e72_delta, e72_weight, wrong_is_zero, wrong_is_one = e95mod.e72_adverse_setup(
        mixmin, refs["failed_e72"]
    )
    e95_tail = e95mod.hard_tail_map(refs["e95"], mixmin, wrong_is_zero, wrong_is_one)
    e89_tail = e95mod.hard_tail_map(refs["e89"], mixmin, wrong_is_zero, wrong_is_one)
    e72_pos = np.maximum(
        e96mod.adverse_delta_for_e72_direction(refs["failed_e72"], mixmin, wrong_is_zero, wrong_is_one),
        0.0,
    )

    e95_logit = logit(refs["e95"])
    source_logits = {name: logit(refs[name]) for name in ["e89", "e85", "e86", "e90", "mixmin"]}
    tail_advantage = e95_tail - e89_tail
    diff_abs = np.abs(logit(refs["e89"]) - logit(refs["e95"]))
    fallback_cell = np.abs(logit(refs["e95"]) - logit(refs["e86"])) > 1.0e-9

    rows: list[dict[str, Any]] = []
    preds: list[np.ndarray] = [mixmin]
    seen_pred: dict[str, int] = {pred_key(mixmin): 0}

    for name in ["e85", "e86", "noq2", "e90", "e89", "e95"]:
        add_pred(rows, preds, seen_pred, refs[name], {"strategy": "control", "source": name})

    selectors: list[tuple[str, np.ndarray]] = []
    for scope in ["q2s3", "q2", "s3"]:
        scope_mask = target_scope_mask(len(sample), scope)
        selectors.append((f"{scope}_all", scope_mask))
        selectors.append((f"{scope}_e95_fallback", scope_mask & fallback_cell))
        for q in [0.00, 0.25, 0.50, 0.75, 0.90]:
            selectors.append((f"{scope}_e89_tail_adv_q{q:.2f}", positive_quantile_mask(tail_advantage, scope_mask, q)))
            selectors.append((f"{scope}_e72_pos_q{q:.2f}", positive_quantile_mask(e72_pos, scope_mask, q)))
            selectors.append((f"{scope}_diff_abs_q{q:.2f}", positive_quantile_mask(diff_abs, scope_mask, q)))

    alphas = [0.25, 0.50, 0.75, 1.00]
    for fallback in ["e89", "e85", "mixmin"]:
        fallback_logit = source_logits[fallback]
        for selector_name, selector_mask in selectors:
            selected_cells = int(selector_mask.sum())
            if selected_cells == 0:
                continue
            selected_rows = int(np.any(selector_mask, axis=1).sum())
            target_scope = selector_name.split("_", 1)[0]
            for alpha in alphas:
                move = (fallback_logit - e95_logit) * selector_mask
                pred = clip_prob(sigmoid(e95_logit + alpha * move))
                selected_tail_adv = float(np.mean(tail_advantage[selector_mask]))
                selected_e72_pos = float(np.mean(e72_pos[selector_mask]))
                add_pred(
                    rows,
                    preds,
                    seen_pred,
                    pred,
                    {
                        "strategy": "e95_q2s3_tail_graft",
                        "source": "e95",
                        "fallback": fallback,
                        "selector": selector_name,
                        "target_scope": target_scope,
                        "graft_alpha": alpha,
                        "selected_cells": selected_cells,
                        "selected_rows": selected_rows,
                        "selected_tail_adv_mean": selected_tail_adv,
                        "selected_e72_pos_mean": selected_e72_pos,
                    },
                )

    return pd.DataFrame(rows), preds, refs, (e72_delta, e72_weight, wrong_is_zero, wrong_is_one)


def score_candidates(
    sample: pd.DataFrame,
    rows: pd.DataFrame,
    preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> pd.DataFrame:
    e72_delta, e72_weight, wrong_is_zero, wrong_is_one = tail_state
    labels, worlds, views, state = e89mod.build_stress_state(sample, refs["mixmin"])
    scan = e83.score_candidate_rows(rows, preds, sample, refs["mixmin"], labels, worlds, views, state)

    tail_rows: list[dict[str, Any]] = []
    for idx, pred in enumerate(preds):
        metrics = e95mod.hard_tail_metrics(pred, refs["mixmin"], e72_weight, wrong_is_zero, wrong_is_one)
        tail_rows.append({"pred_index": idx, **metrics})
    tail = pd.DataFrame(tail_rows)
    scan = scan.merge(tail, on="pred_index", how="left")

    scan["move_l1_vs_e95"] = [
        float(np.mean(np.abs(logit(preds[int(i)]) - logit(refs["e95"])))) for i in scan["pred_index"]
    ]
    scan["active_cells_vs_e95"] = [
        int((np.abs(logit(preds[int(i)]) - logit(refs["e95"])) > 1.0e-9).sum()) for i in scan["pred_index"]
    ]
    scan["is_graft"] = scan["strategy"].eq("e95_q2s3_tail_graft")
    e95_control_tail = float(
        scan.loc[
            scan["strategy"].eq("control") & scan["source"].eq("e95"),
            "e72_adverse_positive_exposure_all",
        ].min()
    )
    scan["is_strict_like"] = (
        scan["is_graft"]
        & scan["nonanchor_evaluated"].fillna(False).astype(bool)
        & scan["strict_gate"].fillna(False).astype(bool)
        & (scan["all_delta_vs_mixmin"] < -2.0e-5)
        & (scan["hidden_q2s3_mean_minus_base"] < 0.0)
        & (scan["world_support_minus_base"] < 0.0)
        & (scan["block_q2s3_beats_base_rate"] >= 0.50)
        & (scan["e72_adverse_positive_exposure_all"] <= e95_control_tail + 5.0e-7)
    )
    return scan


def build_transfer_summary(
    sample: pd.DataFrame,
    scan: pd.DataFrame,
    preds: list[np.ndarray],
    refs: dict[str, np.ndarray],
    tail_state: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> pd.DataFrame:
    e72_delta, _, wrong_is_zero, wrong_is_one = tail_state
    n_cells = refs["mixmin"].size
    e72_pos = np.maximum(
        e96mod.adverse_delta_for_e72_direction(refs["failed_e72"], refs["mixmin"], wrong_is_zero, wrong_is_one),
        0.0,
    )
    base_masks = e96mod.build_masks(refs, e72_pos, e72_delta)
    candidate_idxs = scan["pred_index"].drop_duplicates().astype(int).tolist()
    adverse_flat = {
        f"p{idx}": e96mod.adverse_delta_for_e72_direction(
            preds[idx], refs["mixmin"], wrong_is_zero, wrong_is_one
        ).reshape(-1)
        for idx in candidate_idxs
    }
    budget_sum = e96mod.E72_PUBLIC_MISS * n_cells
    meta, long = e96mod.build_scenarios(e72_pos.reshape(-1), base_masks, adverse_flat, budget_sum, n_cells)
    scenario_tail = meta.merge(long, on="scenario_id", how="left")
    wide = scenario_tail.pivot(index="scenario_id", columns="candidate", values="delta_vs_mixmin")

    context_cols = [
        "scenario_id",
        "family",
        "mask_name",
        "order_name",
        "gamma",
        "alpha",
        "lambda",
        "is_broad_plausible",
        "is_tight_plausible",
        "is_near_unit_tail",
    ]
    context = pd.read_csv(e99mod.SCENARIO_OUT)[context_cols]
    detail = context.set_index("scenario_id").join(wide, how="inner").reset_index()

    local_by_idx = (
        scan.sort_values(["is_graft", "all_delta_vs_mixmin"], ascending=[False, True])
        .drop_duplicates("pred_index")
        .set_index("pred_index")["all_delta_vs_mixmin"]
        .astype(float)
        .to_dict()
    )
    row_meta = scan.drop_duplicates("pred_index").set_index("pred_index")
    rows: list[dict[str, Any]] = []
    for idx in candidate_idxs:
        col = f"p{idx}"
        if col not in detail.columns:
            continue
        local_delta = float(local_by_idx[idx])
        for filter_name, filter_fn in TRANSFER_FILTERS.items():
            subset = detail[filter_fn(detail)].copy()
            if subset.empty:
                continue
            pred_delta = subset["alpha"] * local_delta + subset["lambda"] * subset[col].astype(float)
            vs_e95 = pred_delta - e99mod.OBSERVED_PUBLIC_DELTA["e95"]
            meta_row = row_meta.loc[idx]
            rows.append(
                {
                    "pred_index": idx,
                    "filter": filter_name,
                    "tag": meta_row.get("tag", ""),
                    "strategy": meta_row.get("strategy", ""),
                    "fallback": meta_row.get("fallback", ""),
                    "selector": meta_row.get("selector", ""),
                    "target_scope": meta_row.get("target_scope", ""),
                    "graft_alpha": meta_row.get("graft_alpha", np.nan),
                    "n_scenarios": len(subset),
                    "local_delta": local_delta,
                    "mean_pred_delta": float(pred_delta.mean()),
                    "median_pred_delta": float(pred_delta.median()),
                    "p90_pred_delta": float(pred_delta.quantile(0.90)),
                    "p95_pred_delta": float(pred_delta.quantile(0.95)),
                    "mean_vs_e95": float(vs_e95.mean()),
                    "median_vs_e95": float(vs_e95.median()),
                    "p90_vs_e95": float(vs_e95.quantile(0.90)),
                    "p95_vs_e95": float(vs_e95.quantile(0.95)),
                    "beat_e95_rate": float((pred_delta < e99mod.OBSERVED_PUBLIC_DELTA["e95"] - 1.0e-12).mean()),
                }
            )
    return pd.DataFrame(rows)


def merge_transfer(scan: pd.DataFrame, transfer: pd.DataFrame) -> pd.DataFrame:
    keep_filters = ["broad_plausible", "broad_q2s3", "tight_plausible", "near_unit_tail"]
    wide = transfer[transfer["filter"].isin(keep_filters)].copy()
    wide = wide.pivot_table(
        index="pred_index",
        columns="filter",
        values=["mean_vs_e95", "p95_vs_e95", "beat_e95_rate", "mean_pred_delta"],
        aggfunc="first",
    )
    wide.columns = [f"{metric}_{filter_name}" for metric, filter_name in wide.columns]
    wide = wide.reset_index()
    out = scan.merge(wide, on="pred_index", how="left")
    out["e101_pass"] = (
        out["is_graft"].fillna(False).astype(bool)
        & (out["is_strict_like"].fillna(False).astype(bool))
        & (out["mean_vs_e95_broad_plausible"] < -1.0e-8)
        & (out["p95_vs_e95_broad_plausible"] <= 0.0)
        & (out["beat_e95_rate_broad_plausible"] > 0.75)
        & (out["mean_vs_e95_broad_q2s3"] < 0.0)
    )
    return out


def materialize(scan: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> Path | None:
    eligible = scan[scan["e101_pass"].fillna(False).astype(bool)].copy()
    if eligible.empty:
        return None
    chosen = eligible.sort_values(
        [
            "p95_vs_e95_broad_plausible",
            "mean_vs_e95_broad_plausible",
            "beat_e95_rate_broad_plausible",
            "active_cells_vs_e95",
        ],
        ascending=[True, True, False, True],
    ).iloc[0]
    pred = preds[int(chosen["pred_index"])]
    file_tag = e83.stable_tag(pred, f"{SUBMISSION_PREFIX}_")
    out = OUT / f"{file_tag}.csv"
    sub = sample[KEYS].copy()
    for j, target in enumerate(TARGETS):
        sub[target] = pred[:, j]
    sub.to_csv(out, index=False)
    return out


def write_report(scan: pd.DataFrame, transfer: pd.DataFrame, selected_path: Path | None) -> None:
    control = scan[scan["strategy"].eq("control")].copy()
    control_cols = [
        "source",
        "all_delta_vs_mixmin",
        "e72_adverse_positive_exposure_all",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "block_q2s3_beats_base_rate",
        "mean_vs_e95_broad_plausible",
        "beat_e95_rate_broad_plausible",
        "mean_vs_e95_broad_q2s3",
        "beat_e95_rate_broad_q2s3",
    ]
    best_local = scan[scan["is_graft"].fillna(False).astype(bool)].sort_values("all_delta_vs_mixmin").head(10)
    best_transfer = scan[scan["is_graft"].fillna(False).astype(bool)].sort_values(
        ["mean_vs_e95_broad_plausible", "p95_vs_e95_broad_plausible"]
    ).head(10)
    best_q2s3 = scan[scan["is_graft"].fillna(False).astype(bool)].sort_values(
        ["mean_vs_e95_broad_q2s3", "beat_e95_rate_broad_q2s3"],
        ascending=[True, False],
    ).head(10)
    pass_rows = scan[scan["e101_pass"].fillna(False).astype(bool)].copy()
    transfer_head = transfer[
        transfer["filter"].isin(["broad_plausible", "broad_q2s3"])
        & transfer["strategy"].eq("e95_q2s3_tail_graft")
    ].sort_values(["filter", "mean_vs_e95"]).head(20)

    report = f"""# E101 Q2/S3 Tail Graft Probe

## Question

E100 says E89 is only live when the public hard-label tail is Q2/S3-diffuse.
This probe tests whether that pocket can be separated from full E89 by grafting
selected Q2/S3 cells from E89/E85/mixmin onto E95.

## Result

- total rows: `{len(scan)}`
- graft rows: `{int(scan['is_graft'].fillna(False).sum())}`
- strict-like graft rows: `{int(scan['is_strict_like'].fillna(False).sum())}`
- E101 pass rows: `{int(scan['e101_pass'].fillna(False).sum())}`
- materialized submission: `{selected_path.name if selected_path else 'none'}`

## Controls

{md_table(control[control_cols].sort_values('all_delta_vs_mixmin'), '.9f')}

## Best Local Grafts

{md_table(best_local[['tag','fallback','selector','graft_alpha','selected_cells','strict_gate','e101_pass','all_delta_vs_mixmin','e72_adverse_positive_exposure_all','hidden_q2s3_mean_minus_base','world_support_minus_base','block_q2s3_beats_base_rate','mean_vs_e95_broad_plausible','beat_e95_rate_broad_plausible']], '.9f')}

## Best Broad Transfer Grafts

{md_table(best_transfer[['tag','fallback','selector','graft_alpha','selected_cells','strict_gate','e101_pass','all_delta_vs_mixmin','mean_vs_e95_broad_plausible','beat_e95_rate_broad_plausible','p95_vs_e95_broad_plausible','mean_vs_e95_broad_q2s3','beat_e95_rate_broad_q2s3']], '.9f')}

## Best Q2/S3-Slice Transfer Grafts

{md_table(best_q2s3[['tag','fallback','selector','graft_alpha','selected_cells','strict_gate','e101_pass','all_delta_vs_mixmin','mean_vs_e95_broad_q2s3','beat_e95_rate_broad_q2s3','mean_vs_e95_broad_plausible','beat_e95_rate_broad_plausible']], '.9f')}

## Transfer Detail Sample

{md_table(transfer_head[['filter','tag','fallback','selector','graft_alpha','n_scenarios','local_delta','mean_vs_e95','beat_e95_rate','p95_vs_e95']], '.9f')}

## Interpretation

If E101 pass is empty, the E89 Q2/S3 pocket is not locally separable as a
cleaner E95 graft under the current local+tail abstraction. In that case the
full E89 file remains a public sensor for diffuse Q2/S3 tail allocation, but it
should not be converted into a new claimed-improvement candidate.

If E101 pass is non-empty, submit the materialized file before full E89 because
it would test the same hidden-world hypothesis with less non-Q2/S3 movement.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    rows, preds, refs, tail_state = build_candidates(sample)
    scan = score_candidates(sample, rows, preds, refs, tail_state)
    transfer = build_transfer_summary(sample, scan, preds, refs, tail_state)
    scan = merge_transfer(scan, transfer)
    selected_path = materialize(scan, preds, sample)

    scan.to_csv(SCAN_OUT, index=False)
    summary = (
        scan.groupby(["strategy", "fallback", "target_scope"], dropna=False)
        .agg(
            rows=("pred_index", "count"),
            strict_like=("is_strict_like", "sum"),
            e101_pass=("e101_pass", "sum"),
            best_local_delta=("all_delta_vs_mixmin", "min"),
            best_broad_mean_vs_e95=("mean_vs_e95_broad_plausible", "min"),
            best_broad_q2s3_mean_vs_e95=("mean_vs_e95_broad_q2s3", "min"),
            best_broad_beat_e95=("beat_e95_rate_broad_plausible", "max"),
        )
        .reset_index()
        .sort_values(["e101_pass", "best_broad_mean_vs_e95"], ascending=[False, True])
    )
    summary.to_csv(SUMMARY_OUT, index=False)
    transfer.to_csv(TRANSFER_OUT, index=False)
    write_report(scan, transfer, selected_path)

    print(f"wrote {SCAN_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {TRANSFER_OUT}")
    print(f"wrote {REPORT_OUT}")
    if selected_path:
        print(f"materialized {selected_path}")
    else:
        print("materialized none")


if __name__ == "__main__":
    main()
