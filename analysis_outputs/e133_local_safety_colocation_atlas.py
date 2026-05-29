#!/usr/bin/env python3
"""E133 local-upside / tail-safety co-location atlas.

SAUNA question:
E132 removed old donors and still found no E95 tangent movement that was both
local-strict and transfer-veto-actionable. The next smallest question is not
"which probability should we move?" but "where do local gradient reward and
tail-safety geometry separate?"

This script builds a cell-level atlas from direct E95 combo-set gradients,
transfer-shrinkage density, E72 hard-tail signs, and hidden-block metadata. It
does not create a submission. It asks whether co-located local-upside and
tail-safety cells are structurally visible enough to be a next latent target.
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

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e130_tail_density_synthesis_probe as e130  # noqa: E402
import e132_veto_nullspace_gradient_probe as e132  # noqa: E402
import q2_s3_tail_gate_independence_probe as e68  # noqa: E402


CELL_OUT = OUT / "e133_local_safety_colocation_atlas_cell_detail.csv"
SUMMARY_OUT = OUT / "e133_local_safety_colocation_atlas_summary.csv"
CATEGORY_OUT = OUT / "e133_local_safety_colocation_atlas_category_summary.csv"
TOP_OUT = OUT / "e133_local_safety_colocation_atlas_top_cells.csv"
REPORT_OUT = OUT / "e133_local_safety_colocation_atlas_report.md"

CONTEXTS = ["all", *[f"loo_{name}" for name in e68.COMBO_TABLES.keys()], *list(e68.COMBO_TABLES.keys())]
TOP_KS = [20, 50, 100, 200]
CATEGORY_VIEWS: dict[str, list[str]] = {
    "constant": [],
    "target": ["target"],
    "target_context": ["target", "context_type"],
    "target_position": ["target", "pos_bin"],
    "target_context_position": ["target", "context_type", "pos_bin"],
    "target_tail": ["target", "e95_fallback_cell", "e95_moved_vs_mixmin"],
    "target_context_tail": ["target", "context_type", "e95_fallback_cell", "e95_moved_vs_mixmin"],
    "target_context_tail_e72bin": [
        "target",
        "context_type",
        "e95_fallback_cell",
        "e95_moved_vs_mixmin",
        "e72_pos_bin",
    ],
    "target_context_pos_tail_e72bin": [
        "target",
        "context_type",
        "pos_bin",
        "e95_fallback_cell",
        "e95_moved_vs_mixmin",
        "e72_pos_bin",
    ],
    "subject_target": ["subject_id", "target"],
    "subject_context_target": ["subject_id", "context_type", "target"],
    "blocklen_context_target": ["block_len_bin", "context_type", "target"],
}


def normalize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.where(np.isfinite(arr), np.maximum(arr, 0.0), 0.0)
    total = float(arr.sum())
    if total <= 0.0:
        return np.ones_like(arr, dtype=np.float64) / len(arr)
    return arr / total


def minmax(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    out = np.zeros_like(arr, dtype=np.float64)
    valid = np.isfinite(arr)
    if not valid.any():
        return out
    lo = float(np.min(arr[valid]))
    hi = float(np.max(arr[valid]))
    if hi <= lo + 1.0e-15:
        return out
    out[valid] = (arr[valid] - lo) / (hi - lo)
    return out


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    if float(np.std(aa)) <= 1.0e-15 or float(np.std(bb)) <= 1.0e-15:
        return np.nan
    return float(np.corrcoef(aa, bb)[0, 1])


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    eps = 1.0e-15
    pp = normalize(p)
    qq = normalize(q)
    mm = 0.5 * (pp + qq)
    return float(0.5 * np.sum(pp * np.log((pp + eps) / (mm + eps))) + 0.5 * np.sum(qq * np.log((qq + eps) / (mm + eps))))


def dist_metrics(truth: np.ndarray, pred: np.ndarray, prefix: str = "") -> dict[str, float]:
    p = normalize(truth)
    q = normalize(pred)
    ranks_p = pd.Series(p).rank(method="average").to_numpy()
    ranks_q = pd.Series(q).rank(method="average").to_numpy()
    out = {
        f"{prefix}cosine": float(np.dot(p, q) / max(np.sqrt(np.dot(p, p) * np.dot(q, q)), 1.0e-15)),
        f"{prefix}pearson": safe_corr(p, q),
        f"{prefix}spearman": safe_corr(ranks_p, ranks_q),
        f"{prefix}tv_distance": float(0.5 * np.abs(p - q).sum()),
        f"{prefix}js_divergence": js_divergence(p, q),
    }
    order_truth = np.argsort(-p)
    order_pred = np.argsort(-q)
    for k in TOP_KS:
        kk = min(k, len(p))
        truth_top = set(order_truth[:kk])
        pred_top = set(order_pred[:kk])
        out[f"{prefix}top{k}_overlap"] = float(len(truth_top & pred_top) / kk)
        out[f"{prefix}truth_mass_in_pred_top{k}"] = float(p[order_pred[:kk]].sum())
        out[f"{prefix}pred_mass_in_truth_top{k}"] = float(q[order_truth[:kk]].sum())
    return out


def top_mask(values: np.ndarray, k: int) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    kk = min(k, len(arr))
    mask = np.zeros(len(arr), dtype=bool)
    if kk <= 0:
        return mask
    order = np.argsort(-arr)
    mask[order[:kk]] = True
    return mask


def quantile_gate(values: np.ndarray, q: float, high: bool = True) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    valid = np.isfinite(arr)
    if not valid.any():
        return np.zeros_like(arr, dtype=bool)
    cut = float(np.quantile(arr[valid], q))
    return valid & (arr >= cut if high else arr <= cut)


def md_table(frame: pd.DataFrame, floatfmt: str = ".6f") -> str:
    if frame.empty:
        return "_empty_"
    lines = [
        "| " + " | ".join(str(c) for c in frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
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


def category_key(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series(["__constant__"] * len(frame), index=frame.index)
    return frame[cols].astype(str).agg("||".join, axis=1)


def cv_category_predict(cell: pd.DataFrame, cols: list[str], target_col: str) -> np.ndarray:
    groups = pd.Series(cell["hidden_block_id"].astype(str).unique()).sort_values().tolist()
    fold_map = {group: i % 5 for i, group in enumerate(groups)}
    folds = cell["hidden_block_id"].astype(str).map(fold_map).to_numpy()
    preds = np.zeros(len(cell), dtype=np.float64)
    for fold in sorted(set(folds)):
        train_idx = folds != fold
        valid_idx = folds == fold
        train = cell.loc[train_idx]
        valid = cell.loc[valid_idx]
        global_mean = float(train[target_col].mean())
        if not cols:
            preds[valid_idx] = global_mean
            continue
        train_key = category_key(train, cols)
        valid_key = category_key(valid, cols)
        means = train.groupby(train_key)[target_col].mean()
        preds[valid_idx] = valid_key.map(means).fillna(global_mean).to_numpy(dtype=np.float64)
    return np.maximum(preds, 0.0)


def share(mask: np.ndarray, weight: np.ndarray | None = None) -> float:
    mm = np.asarray(mask, dtype=bool)
    if weight is None:
        return float(mm.mean())
    ww = np.asarray(weight, dtype=np.float64)
    den = float(np.sum(ww))
    return float(np.sum(ww[mm]) / den) if den > 0.0 else np.nan


def target_shares(cell: pd.DataFrame, mask: np.ndarray, prefix: str) -> dict[str, float]:
    out: dict[str, float] = {}
    sub = cell.loc[np.asarray(mask, dtype=bool)]
    for target in TARGETS:
        out[f"{prefix}_{target}_frac"] = float(sub["target"].eq(target).mean()) if len(sub) else np.nan
    return out


def context_summary(cell: pd.DataFrame, context: str) -> dict[str, Any]:
    local = cell[f"{context}_local_merit"].to_numpy(dtype=np.float64)
    co = cell[f"{context}_co_vetonull_density"].to_numpy(dtype=np.float64)
    safe = cell[f"{context}_safe_density"].to_numpy(dtype=np.float64)
    local_share = normalize(local)
    safe_share = normalize(safe)
    co_share = normalize(co)

    veto_null = cell[f"{context}_veto_null"].to_numpy(bool)
    low_adverse = cell[f"{context}_low_adverse75"].to_numpy(bool)
    density70 = quantile_gate(cell["density_rank"].to_numpy(dtype=np.float64), 0.70)
    local_top50 = top_mask(local_share, 50)
    co_top50 = top_mask(co_share, 50)

    rec: dict[str, Any] = {
        "context": context,
        "grad_mean_abs": float(cell[f"{context}_grad_abs"].mean()),
        "grad_max_abs": float(cell[f"{context}_grad_abs"].max()),
        "local_safe_cosine": dist_metrics(local, safe)["cosine"],
        "local_co_cosine": dist_metrics(local, co)["cosine"],
        "local_mass_in_veto_null": share(veto_null, local_share),
        "local_mass_in_low_adverse75": share(low_adverse, local_share),
        "local_mass_in_density70": share(density70, local_share),
        "local_mass_in_vetonull_density70": share(veto_null & density70, local_share),
        "local_mass_in_co_top50": share(co_top50, local_share),
        "co_mass_in_local_top50": share(local_top50, co_share),
        "local_top50_veto_null_frac": share(veto_null[local_top50]),
        "local_top50_low_adverse75_frac": share(low_adverse[local_top50]),
        "local_top50_density70_frac": share(density70[local_top50]),
        "local_top50_q2s3_frac": share(cell.loc[local_top50, "target_is_q2s3"].to_numpy(bool)),
        "local_top50_e101_active_frac": share(cell.loc[local_top50, "e101_active"].to_numpy(bool)),
        "local_top50_edge_like_frac": share(cell.loc[local_top50, "edge_like"].to_numpy(bool)),
        "co_top50_veto_null_frac": share(veto_null[co_top50]),
        "co_top50_low_adverse75_frac": share(low_adverse[co_top50]),
        "co_top50_density70_frac": share(density70[co_top50]),
        "co_top50_q2s3_frac": share(cell.loc[co_top50, "target_is_q2s3"].to_numpy(bool)),
        "co_top50_e101_active_frac": share(cell.loc[co_top50, "e101_active"].to_numpy(bool)),
        "co_top50_edge_like_frac": share(cell.loc[co_top50, "edge_like"].to_numpy(bool)),
        "co_nonzero_cells": int(np.count_nonzero(co > 0.0)),
        "co_total_raw": float(np.sum(co)),
    }
    rec.update(target_shares(cell, local_top50, "local_top50"))
    rec.update(target_shares(cell, co_top50, "co_top50"))
    return rec


def build_cell_atlas() -> tuple[pd.DataFrame, pd.DataFrame]:
    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    refs = e130.load_refs(sample)
    _masks, density = e130.build_density_masks(sample, refs)
    tail_state = e132.e95mod.e72_adverse_setup(refs["mixmin"], refs["failed_e72"])
    risk_sign = e132.risk_signs(tail_state)
    risk_weight = (
        1.00 * density["plausible"]
        + 0.75 * density["e101_active"]
        + 0.50 * density["q2s3"]
        + 0.25 * density["tail_equal"]
    )

    cell = pd.read_csv(e130.CELL_IN).sort_values("cell_idx").reset_index(drop=True)
    if len(cell) != len(sample) * len(TARGETS):
        raise RuntimeError("cell metadata shape mismatch")
    flat_density = {
        "tail_equal": density["tail_equal"].reshape(-1),
        "low_alpha": density["low_alpha"].reshape(-1),
        "plausible": density["plausible"].reshape(-1),
        "density_score": density["density_score"].reshape(-1),
    }
    cell["density_rank"] = minmax(flat_density["density_score"])
    cell["tail_equal_rank"] = minmax(flat_density["tail_equal"])
    cell["low_alpha_rank"] = minmax(flat_density["low_alpha"])
    cell["plausible_rank"] = minmax(flat_density["plausible"])

    grad_diag_rows: list[dict[str, Any]] = []
    for context in CONTEXTS:
        grad = e132.gradient_for_context(sample, refs["e95"], context)
        unit = -grad
        adverse = e132.weighted_adverse(unit, risk_sign, risk_weight)
        adverse_flat = adverse.reshape(-1)
        unit_flat = unit.reshape(-1)
        grad_flat = grad.reshape(-1)
        veto_null = (unit * risk_sign <= 1.0e-15).reshape(-1)
        low_adverse75 = quantile_gate(adverse_flat, 0.75, high=False)
        local_merit = np.square(grad_flat)
        safe_density = cell["density_rank"].to_numpy(dtype=np.float64) * veto_null.astype(float) * low_adverse75.astype(float)
        co_vetonull_density = local_merit * safe_density
        co_tail_equal = local_merit * cell["tail_equal_rank"].to_numpy(dtype=np.float64) * veto_null.astype(float)
        co_low_alpha = local_merit * cell["low_alpha_rank"].to_numpy(dtype=np.float64) * veto_null.astype(float)

        cell[f"{context}_grad"] = grad_flat
        cell[f"{context}_grad_abs"] = np.abs(grad_flat)
        cell[f"{context}_unit"] = unit_flat
        cell[f"{context}_adverse"] = adverse_flat
        cell[f"{context}_veto_null"] = veto_null
        cell[f"{context}_low_adverse75"] = low_adverse75
        cell[f"{context}_local_merit"] = local_merit
        cell[f"{context}_safe_density"] = safe_density
        cell[f"{context}_co_vetonull_density"] = co_vetonull_density
        cell[f"{context}_co_tail_equal"] = co_tail_equal
        cell[f"{context}_co_low_alpha"] = co_low_alpha
        grad_diag_rows.append(
            {
                "context": context,
                "grad_mean_abs": float(np.mean(np.abs(grad_flat))),
                "grad_max_abs": float(np.max(np.abs(grad_flat))),
                "veto_null_frac": float(veto_null.mean()),
                "low_adverse75_frac": float(low_adverse75.mean()),
                "co_nonzero": int(np.count_nonzero(co_vetonull_density > 0.0)),
            }
        )
    return cell, pd.DataFrame(grad_diag_rows)


def build_category_cv(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for context in CONTEXTS:
        target_col = f"{context}_co_vetonull_density"
        truth = cell[target_col].to_numpy(dtype=np.float64)
        for view_name, cols in CATEGORY_VIEWS.items():
            pred = cv_category_predict(cell, cols, target_col)
            rec: dict[str, Any] = {"context": context, "view": view_name, "cols": ",".join(cols) if cols else "constant"}
            rec.update(dist_metrics(truth, pred))
            rows.append(rec)
    return pd.DataFrame(rows).sort_values(["js_divergence", "tv_distance"], ascending=[True, True])


def build_top_cells(cell: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    keep_cols = [
        "cell_idx",
        "sub_idx",
        "target",
        "subject_id",
        "hidden_block_id",
        "context_type",
        "pos_bin",
        "e101_active",
        "target_is_q2s3",
        "e95_fallback_cell",
        "e72_pos",
        "density_rank",
        "tail_equal_rank",
        "low_alpha_rank",
    ]
    for context in CONTEXTS:
        for field in ["local_merit", "co_vetonull_density", "co_tail_equal", "co_low_alpha"]:
            col = f"{context}_{field}"
            top = cell.sort_values(col, ascending=False).head(50).copy()
            top.insert(0, "rank", np.arange(1, len(top) + 1))
            top.insert(0, "field", field)
            top.insert(0, "context", context)
            top["score"] = top[col].to_numpy(dtype=np.float64)
            rows.append(top[["context", "field", "rank", "score", *keep_cols]])
    return pd.concat(rows, ignore_index=True)


def write_report(summary: pd.DataFrame, category: pd.DataFrame, top_cells: pd.DataFrame, grad_diag: pd.DataFrame) -> None:
    best_cv = category.groupby("context", as_index=False).head(3)
    cols_summary = [
        "context",
        "local_safe_cosine",
        "local_mass_in_vetonull_density70",
        "local_top50_veto_null_frac",
        "local_top50_density70_frac",
        "local_top50_q2s3_frac",
        "local_top50_e101_active_frac",
        "co_top50_q2s3_frac",
        "co_top50_e101_active_frac",
        "co_nonzero_cells",
        "co_total_raw",
    ]
    top_cols = [
        "context",
        "field",
        "rank",
        "score",
        "target",
        "subject_id",
        "hidden_block_id",
        "context_type",
        "pos_bin",
        "e101_active",
        "target_is_q2s3",
        "density_rank",
    ]
    lines = [
        "# E133 Local-Safety Co-location Atlas",
        "",
        "## Question",
        "",
        "After E132 rejected donor-free E95 tangent moves, where do local combo-gradient reward and transfer-tail safety separate at the cell level?",
        "",
        "## Method",
        "",
        "- Compute E95 combo-set gradients for all, leave-one-combo, and single-combo contexts.",
        "- Convert squared gradient into a local-reward field.",
        "- Build a transfer-safe field from veto-null direction, low-adverse hard-tail exposure, and E127/E130 density rank.",
        "- Measure whether local reward mass lies inside safe density and whether hidden-block-heldout categorical views can predict the co-located field.",
        "- No submission is generated.",
        "",
        "## Gradient Diagnostics",
        "",
        md_table(grad_diag, ".9f"),
        "",
        "## Co-location Summary",
        "",
        md_table(summary[cols_summary], ".9f"),
        "",
        "## Best Hidden-Block CV Category Views",
        "",
        md_table(best_cv[["context", "view", "cosine", "spearman", "js_divergence", "truth_mass_in_pred_top50", "top50_overlap"]].head(30), ".9f"),
        "",
        "## Top Co-located Cells",
        "",
        md_table(top_cells[top_cells["field"].eq("co_vetonull_density")][top_cols].head(40), ".9f"),
        "",
        "## Decision",
        "",
        "No submission. This is an atlas for the next latent target, not a probability movement.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    cell, grad_diag = build_cell_atlas()
    summary = pd.DataFrame([context_summary(cell, context) for context in CONTEXTS]).sort_values(
        ["local_mass_in_vetonull_density70", "local_safe_cosine"],
        ascending=[False, False],
    )
    category = build_category_cv(cell)
    top_cells = build_top_cells(cell)

    cell.to_csv(CELL_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    category.to_csv(CATEGORY_OUT, index=False)
    top_cells.to_csv(TOP_OUT, index=False)
    write_report(summary, category, top_cells, grad_diag)

    print(
        {
            "contexts": len(CONTEXTS),
            "cells": len(cell),
            "best_context": str(summary.iloc[0]["context"]) if len(summary) else None,
            "best_local_mass_in_vetonull_density70": float(summary.iloc[0]["local_mass_in_vetonull_density70"]) if len(summary) else None,
            "best_category_js": float(category["js_divergence"].min()) if len(category) else None,
            "report": str(REPORT_OUT),
        }
    )
    print(summary.head(10).to_string(index=False))
    print(category.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
