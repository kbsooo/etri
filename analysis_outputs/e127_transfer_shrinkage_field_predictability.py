#!/usr/bin/env python3
"""E127 predictability of the E101-compatible transfer-shrinkage field.

SAUNA question:
E126 showed that E101-compatible public-loss budget is mostly outside the cells
E101 changed. This script asks whether that budget field is visible before a
new probability move: does it align with public-free scenario proxies, and do
simple structural metadata views predict it under hidden-block holdout?

No submission is generated. E101 public feedback is used only to define the
post-feedback teacher whose predictability is being audited.
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

import e126_e101_survivor_cell_budget_anatomy as e126  # noqa: E402
import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
from public_anchor_bottleneck_decomposition import KEYS, TARGETS, load_sub, logit  # noqa: E402


CELL_SUMMARY_OUT = OUT / "e127_transfer_shrinkage_cell_summary.csv"
PROXY_SUMMARY_OUT = OUT / "e127_transfer_shrinkage_proxy_summary.csv"
CATEGORY_SUMMARY_OUT = OUT / "e127_transfer_shrinkage_category_cv_summary.csv"
TOP_CELLS_OUT = OUT / "e127_transfer_shrinkage_top_cells_summary.csv"
REPORT_OUT = OUT / "e127_transfer_shrinkage_field_predictability_report.md"

GROUPS = [
    "broad",
    "broad_all_or_top50",
    "broad_low_alpha",
    "broad_q2s3",
    "broad_tail_equal",
    "e101_plausible",
]

PROXY_GROUPS = [
    "broad",
    "broad_all_or_top50",
    "broad_low_alpha",
    "broad_q2s3",
    "broad_tail_equal",
]

CATEGORICAL_VIEWS: dict[str, list[str]] = {
    "constant": [],
    "target": ["target"],
    "target_context": ["target", "context_type"],
    "target_position": ["target", "pos_bin"],
    "target_context_position": ["target", "context_type", "pos_bin"],
    "target_tail": ["target", "e95_fallback_cell", "e95_moved_vs_mixmin"],
    "target_context_tail": ["target", "context_type", "e95_fallback_cell", "e95_moved_vs_mixmin"],
    "target_context_tail_e72bin": ["target", "context_type", "e95_fallback_cell", "e95_moved_vs_mixmin", "e72_pos_bin"],
    "subject_target": ["subject_id", "target"],
    "subject_context_target": ["subject_id", "context_type", "target"],
    "blocklen_context_target": ["block_len_bin", "context_type", "target"],
}


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


def normalize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.where(np.isfinite(arr), np.maximum(arr, 0.0), 0.0)
    total = float(arr.sum())
    if total <= 0:
        return np.ones_like(arr) / len(arr)
    return arr / total


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


def distribution_metrics(truth: np.ndarray, pred: np.ndarray, prefix: str = "") -> dict[str, float]:
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
    for k in [20, 50, 100, 200]:
        kk = min(k, len(p))
        truth_top = set(order_truth[:kk])
        pred_top = set(order_pred[:kk])
        out[f"{prefix}top{k}_overlap"] = float(len(truth_top & pred_top) / kk)
        out[f"{prefix}truth_mass_in_pred_top{k}"] = float(p[order_pred[:kk]].sum())
        out[f"{prefix}pred_mass_in_truth_top{k}"] = float(q[order_truth[:kk]].sum())
    return out


def load_cell_meta() -> pd.DataFrame:
    sample = load_sub(e126.FILES["mixmin"]).sort_values(KEYS).reset_index(drop=True)
    train, sample_from_data = hbr.read_data()
    sample_from_data = sample_from_data.sort_values(KEYS).reset_index(drop=True)
    train = train.sort_values(["subject_id", "lifelog_date"]).reset_index(drop=True)
    if not sample[KEYS].astype(str).equals(sample_from_data[KEYS].astype(str)):
        raise RuntimeError("submission sample keys do not match data sample keys")

    preds = {name: e126.load_pred(file_name, sample) for name, file_name in e126.FILES.items()}
    base = preds["mixmin"]
    e72 = preds["failed_e72"]
    e72_delta = logit(e72) - logit(base)
    wrong_is_zero = e72_delta > e126.EPS
    wrong_is_one = e72_delta < -e126.EPS
    adverse = {
        name: e126.e96.adverse_delta_for_e72_direction(pred, base, wrong_is_zero, wrong_is_one)
        for name, pred in preds.items()
    }
    e72_pos = np.maximum(adverse["failed_e72"], 0.0)
    masks = e126.e96.build_masks(preds, e72_pos, e72_delta)
    row_meta = e126.build_hidden_row_meta(train, sample)
    return e126.build_flat_cell_meta(sample, row_meta, preds, masks, e72_pos, e72_delta)


def ensure_selected_detail() -> pd.DataFrame:
    if not e126.SELECTED_OUT.exists():
        e126.main()
    return pd.read_csv(e126.SELECTED_OUT)


def build_cell_summary() -> pd.DataFrame:
    selected = ensure_selected_detail()
    cell_meta = load_cell_meta()
    mass = selected.groupby(["group_name", "cell_idx"], sort=False)["budget_mass"].sum().unstack(0).fillna(0.0)
    scenario_count = selected.groupby("group_name")["scenario_id"].nunique().to_dict()

    cell = cell_meta.copy()
    for group in GROUPS:
        raw = mass[group] if group in mass.columns else pd.Series(0.0, index=mass.index)
        cell[f"{group}_mass"] = cell["cell_idx"].map(raw).fillna(0.0).astype(float)
        total = float(cell[f"{group}_mass"].sum())
        cell[f"{group}_share"] = cell[f"{group}_mass"] / total if total > 0 else 0.0
        n = int(scenario_count.get(group, 0))
        cell[f"{group}_mass_per_scenario"] = cell[f"{group}_mass"] / max(n, 1)

    positive = cell["e72_pos"].gt(0)
    cell["e72_pos_bin"] = "zero"
    if positive.any():
        cell.loc[positive, "e72_pos_bin"] = pd.qcut(
            cell.loc[positive, "e72_pos"].rank(method="first"),
            q=5,
            labels=["p01_low", "p02", "p03", "p04", "p05_high"],
        ).astype(str)
    cell["e72_abs_bin"] = "zero"
    if cell["e72_abs_logit_delta"].gt(0).any():
        pos_abs = cell["e72_abs_logit_delta"].gt(0)
        cell.loc[pos_abs, "e72_abs_bin"] = pd.qcut(
            cell.loc[pos_abs, "e72_abs_logit_delta"].rank(method="first"),
            q=5,
            labels=["a01_low", "a02", "a03", "a04", "a05_high"],
        ).astype(str)
    return cell


def summarize_proxy_views(cell: pd.DataFrame) -> pd.DataFrame:
    truth = cell["e101_plausible_share"].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    for group in PROXY_GROUPS:
        pred = cell[f"{group}_share"].to_numpy(dtype=np.float64)
        row = {"proxy_view": group}
        row.update(distribution_metrics(truth, pred))
        row["proxy_mass_on_e101_active"] = float(cell.loc[cell["e101_active"], f"{group}_share"].sum())
        row["proxy_mass_on_q2s3"] = float(cell.loc[cell["target_is_q2s3"], f"{group}_share"].sum())
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["js_divergence", "tv_distance"], ascending=[True, True])


def category_key(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    if not cols:
        return pd.Series(["__constant__"] * len(frame), index=frame.index)
    return frame[cols].astype(str).agg("||".join, axis=1)


def cv_category_predict(cell: pd.DataFrame, cols: list[str], target_col: str = "e101_plausible_mass") -> np.ndarray:
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
        means = train.groupby(train_key)[target_col].mean()
        valid_key = category_key(valid, cols)
        preds[valid_idx] = valid_key.map(means).fillna(global_mean).to_numpy(dtype=np.float64)
    return preds


def all_data_category_predict(cell: pd.DataFrame, cols: list[str], target_col: str = "e101_plausible_mass") -> np.ndarray:
    if not cols:
        return np.full(len(cell), float(cell[target_col].mean()), dtype=np.float64)
    key = category_key(cell, cols)
    means = cell.groupby(key)[target_col].mean()
    return key.map(means).fillna(float(cell[target_col].mean())).to_numpy(dtype=np.float64)


def summarize_category_views(cell: pd.DataFrame) -> pd.DataFrame:
    truth = cell["e101_plausible_share"].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    for name, cols in CATEGORICAL_VIEWS.items():
        cv_pred = cv_category_predict(cell, cols)
        all_pred = all_data_category_predict(cell, cols)
        row: dict[str, Any] = {
            "view": name,
            "features": ",".join(cols) if cols else "constant",
            "n_feature_cols": len(cols),
            "n_all_data_bins": int(category_key(cell, cols).nunique()),
        }
        row.update(distribution_metrics(truth, cv_pred, prefix="cv_"))
        row.update(distribution_metrics(truth, all_pred, prefix="all_"))
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["cv_js_divergence", "cv_tv_distance"], ascending=[True, True])


def summarize_top_cells(cell: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "cell_idx",
        "sub_idx",
        "target",
        "subject_id",
        "hidden_block_id",
        "context_type",
        "pos_bin",
        "block_len_bin",
        "e101_plausible_share",
        "broad_tail_equal_share",
        "broad_low_alpha_share",
        "broad_share",
        "target_is_q2s3",
        "e101_active",
        "e95_fallback_cell",
        "e95_moved_vs_mixmin",
        "e72_pos",
        "e72_pos_bin",
        "edge_like",
        "is_weekend",
    ]
    return cell.sort_values("e101_plausible_share", ascending=False)[cols].head(50)


def write_report(proxy: pd.DataFrame, category: pd.DataFrame, top_cells: pd.DataFrame) -> None:
    best_proxy = proxy.iloc[0]
    best_cv = category.iloc[0]
    target_view = category[category["view"].eq("target")].iloc[0]
    q2s3_proxy = proxy[proxy["proxy_view"].eq("broad_q2s3")].iloc[0]

    report = f"""# E127 Transfer-shrinkage field predictability

## Question

E126 showed that E101-compatible public-loss budget is mostly outside the
cells E101 changed. E127 asks whether that post-feedback budget field was
visible before another probability move.

## Proxy Distribution Stress

{md_table(proxy[[
    'proxy_view',
    'cosine',
    'spearman',
    'tv_distance',
    'js_divergence',
    'top50_overlap',
    'truth_mass_in_pred_top50',
    'proxy_mass_on_e101_active',
    'proxy_mass_on_q2s3',
]], '.6f')}

## Structural Metadata Predictability

{md_table(category[[
    'view',
    'features',
    'n_all_data_bins',
    'cv_cosine',
    'cv_spearman',
    'cv_tv_distance',
    'cv_js_divergence',
    'cv_top50_overlap',
    'cv_truth_mass_in_pred_top50',
    'all_js_divergence',
]], '.6f')}

## Top E101-compatible Budget Cells

{md_table(top_cells.head(20)[[
    'cell_idx',
    'target',
    'subject_id',
    'hidden_block_id',
    'context_type',
    'pos_bin',
    'e101_plausible_share',
    'broad_tail_equal_share',
    'broad_low_alpha_share',
    'target_is_q2s3',
    'e101_active',
    'e95_fallback_cell',
    'e72_pos_bin',
]], '.6f')}

## Interpretation

- Best public-free scenario proxy: `{best_proxy['proxy_view']}` with JS `{float(best_proxy['js_divergence']):.6f}`, TV `{float(best_proxy['tv_distance']):.6f}`, and top50 truth-mass capture `{float(best_proxy['truth_mass_in_pred_top50']):.6f}`.
- The rejected q2s3 proxy has JS `{float(q2s3_proxy['js_divergence']):.6f}` and top50 truth-mass capture `{float(q2s3_proxy['truth_mass_in_pred_top50']):.6f}`.
- Best hidden-block-heldout metadata view: `{best_cv['view']}` with CV JS `{float(best_cv['cv_js_divergence']):.6f}` and top50 truth-mass capture `{float(best_cv['cv_truth_mass_in_pred_top50']):.6f}`.
- Target-only heldout view has CV JS `{float(target_view['cv_js_divergence']):.6f}`.

The transfer-shrinkage field is not arbitrary: scenario-level tail-neutral /
low-alpha proxies see it better than q2s3. But structural metadata alone is only
a weak action sensor under hidden-block holdout. This supports the E126 world
model as an explanation and a negative gate, while rejecting a direct metadata
gate as the next submission generator.

## Decision

No submission. The next useful branch should build a public-free
tail-neutral/low-alpha transfer-shrinkage representation, then test whether it
creates probability movement larger than selector noise without reintroducing
E72/E101 active-cell tail risk.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    cell = build_cell_summary()
    proxy = summarize_proxy_views(cell)
    category = summarize_category_views(cell)
    top_cells = summarize_top_cells(cell)

    cell.to_csv(CELL_SUMMARY_OUT, index=False)
    proxy.to_csv(PROXY_SUMMARY_OUT, index=False)
    category.to_csv(CATEGORY_SUMMARY_OUT, index=False)
    top_cells.to_csv(TOP_CELLS_OUT, index=False)
    write_report(proxy, category, top_cells)

    print("Wrote:")
    for path in [CELL_SUMMARY_OUT, PROXY_SUMMARY_OUT, CATEGORY_SUMMARY_OUT, TOP_CELLS_OUT, REPORT_OUT]:
        print(f"- {path.relative_to(ROOT)}")
    print("\nProxy summary:")
    print(proxy[["proxy_view", "cosine", "spearman", "tv_distance", "js_divergence", "top50_overlap", "truth_mass_in_pred_top50"]].to_string(index=False))
    print("\nCategory CV summary:")
    print(category[["view", "cv_cosine", "cv_spearman", "cv_tv_distance", "cv_js_divergence", "cv_top50_overlap", "cv_truth_mass_in_pred_top50"]].to_string(index=False))


if __name__ == "__main__":
    main()
