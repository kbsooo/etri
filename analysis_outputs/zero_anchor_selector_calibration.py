#!/usr/bin/env python3
"""E42 fixed-zero-anchor selector calibration stress.

E41 failed mainly because A2C8 is not recovered as best under full LOO. That
may be too harsh: A2C8 is a known public anchor, not an unknown candidate.
This experiment keeps A2C8 fixed while leaving out every nonbaseline anchor,
then asks whether the resulting selector has enough resolution to rank
frontier-scale candidates.

The key anti-overfit check is resolution. If the selector's nonbaseline LOO
error is much larger than the raw05-vs-A2C8 public gap, then predictions that
place unobserved candidates slightly below raw05 are not actionable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import movement_badaxis_geometry_selector as e41
import test_movement_fingerprint_selector as e40


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
BEST_PUBLIC = e40.BEST_PUBLIC
RAW05_DELTA = float(
    next(a for a in e40.KNOWN_ANCHORS if a["name"] == "raw_timeline")["public_lb"] - BEST_PUBLIC
)

VIEW_OUT = OUT / "zero_anchor_selector_calibration_views.csv"
LOOCV_OUT = OUT / "zero_anchor_selector_calibration_loocv.csv"
CAND_OUT = OUT / "zero_anchor_selector_calibration_candidates.csv"
TRAJ_OUT = OUT / "zero_anchor_selector_calibration_trajectories.csv"
REPORT_OUT = OUT / "zero_anchor_selector_calibration_report.md"

VIEWS = [
    "compact",
    "axis_group",
    "axis_named",
    "compact_axis_group",
    "compact_axis_named",
]
SCALES = [0.05, 0.10, 0.25, 0.50, 0.75, 1.00]


def feature_row_from_pred(pred: np.ndarray, base: np.ndarray, axes: dict[str, np.ndarray], view: str) -> dict[str, float]:
    feats: dict[str, float] = {}
    if "compact" in view:
        feats.update(e41.compact_movement_features(pred, base))
    if "axis_group" in view:
        feats.update(e41.axis_geometry_features(pred, base, axes, named=False))
    elif "axis_named" in view:
        feats.update(e41.axis_geometry_features(pred, base, axes, named=True))
    return feats


def feature_matrix_for_items(
    items: list[dict[str, Any]],
    base: np.ndarray,
    axes: dict[str, np.ndarray],
    view: str,
) -> tuple[pd.DataFrame, list[str]]:
    rows: list[dict[str, Any]] = []
    feature_rows: list[dict[str, float]] = []
    for item in items:
        feats = e41.feature_row(str(item["file"]), base, axes, view)
        row = dict(item)
        row.update(feats)
        rows.append(row)
        feature_rows.append(feats)
    _, cols = e41.matrix_from_rows(feature_rows)
    return pd.DataFrame(rows), cols


def evaluate_fixed_zero_view(items: list[dict[str, Any]], base: np.ndarray, view: str) -> tuple[dict[str, Any], pd.DataFrame]:
    names = [str(item["name"]) for item in items]
    y_all = np.asarray([float(item["public_delta_vs_best"]) for item in items], dtype=float)
    a2c8_idx = names.index("a2c8_best")
    nonbaseline_idx = [i for i, name in enumerate(names) if name != "a2c8_best"]
    pred_by_idx: dict[int, float] = {}
    neigh_by_idx: dict[int, str] = {}

    for i in nonbaseline_idx:
        heldout = names[i]
        axes = e41.named_anchor_vectors(base, exclude=heldout if "axis" in view else None)
        frame, cols = feature_matrix_for_items(items, base, axes, view)
        x = frame[cols].to_numpy(float)
        train_idx = [j for j in range(len(items)) if j != i]
        if a2c8_idx not in train_idx:
            raise RuntimeError("A2C8 must remain fixed in every nonbaseline fold")
        pred, neigh = e41.predict_knn(x[train_idx], y_all[train_idx], x[[i]])
        pred_by_idx[i] = float(pred[0])
        neigh_by_idx[i] = neigh[0]

    rows: list[dict[str, Any]] = []
    for i in nonbaseline_idx:
        actual = float(y_all[i])
        pred = pred_by_idx[i]
        rows.append(
            {
                "name": names[i],
                "file": str(items[i]["file"]),
                "role": str(items[i]["role"]),
                "public_lb": float(items[i]["public_lb"]),
                "public_delta_vs_best": actual,
                "view": view,
                "predicted_delta": pred,
                "predicted_public_lb": BEST_PUBLIC + pred,
                "error": pred - actual,
                "abs_error": abs(pred - actual),
                "underprediction": max(actual - pred, 0.0),
                "neighbor_indices": neigh_by_idx[i],
            }
        )
    loocv = pd.DataFrame(rows)
    actual = loocv["public_delta_vs_best"].to_numpy(float)
    pred = loocv["predicted_delta"].to_numpy(float)
    pred_stage2 = float(loocv.loc[loocv["name"].eq("stage2"), "predicted_delta"].iloc[0])
    pred_ordinal = float(loocv.loc[loocv["name"].eq("ordinal"), "predicted_delta"].iloc[0])
    actual_stage2 = float(loocv.loc[loocv["name"].eq("stage2"), "public_delta_vs_best"].iloc[0])
    actual_ordinal = float(loocv.loc[loocv["name"].eq("ordinal"), "public_delta_vs_best"].iloc[0])
    raw_pred = float(loocv.loc[loocv["name"].eq("raw_timeline"), "predicted_delta"].iloc[0])
    bad = loocv[loocv["name"].isin(e41.BAD_ANCHORS)]

    summary = {
        "view": view,
        "n_features": int(len(feature_matrix_for_items(items, base, e41.named_anchor_vectors(base), view)[1])),
        "nonbaseline_loocv_mae": float(loocv["abs_error"].mean()),
        "nonbaseline_loocv_max_abs_error": float(loocv["abs_error"].max()),
        "pairwise_rank_accuracy": e40.pairwise_rank_accuracy(actual, pred),
        "spearman": e40.spearman_corr(actual, pred),
        "stage2_ordinal_order_correct": bool(np.sign(actual_stage2 - actual_ordinal) == np.sign(pred_stage2 - pred_ordinal)),
        "raw05_predicted_best_nonbaseline": bool(raw_pred <= float(np.min(pred))),
        "raw05_abs_error": float(abs(raw_pred - RAW05_DELTA)),
        "bad_anchor_mean_underprediction": float(bad["underprediction"].mean()),
        "bad_anchor_max_underprediction": float(bad["underprediction"].max()),
        "raw05_gap_to_mae_ratio": float(RAW05_DELTA / max(float(loocv["abs_error"].mean()), 1e-12)),
    }

    rng = np.random.default_rng(20260528)
    fold_payload: list[tuple[np.ndarray, np.ndarray, list[int]]] = []
    for i in nonbaseline_idx:
        heldout = names[i]
        axes = e41.named_anchor_vectors(base, exclude=heldout if "axis" in view else None)
        frame, cols = feature_matrix_for_items(items, base, axes, view)
        x = frame[cols].to_numpy(float)
        train_idx = [j for j in range(len(items)) if j != i]
        fold_payload.append((x[train_idx], x[[i]], train_idx))
    null_rank = []
    null_mae = []
    for _ in range(500):
        y_perm = y_all.copy()
        permuted_nonbase = rng.permutation(y_all[nonbaseline_idx])
        y_perm[nonbaseline_idx] = permuted_nonbase
        y_perm[a2c8_idx] = 0.0
        pred_perm = np.zeros(len(nonbaseline_idx), dtype=float)
        for k, (x_train, x_query, train_idx) in enumerate(fold_payload):
            p, _ = e41.predict_knn(x_train, y_perm[train_idx], x_query)
            pred_perm[k] = p[0]
        null_rank.append(e40.pairwise_rank_accuracy(permuted_nonbase, pred_perm))
        null_mae.append(float(np.mean(np.abs(pred_perm - permuted_nonbase))))
    summary["null_rank_p_ge_actual"] = float((np.asarray(null_rank) >= summary["pairwise_rank_accuracy"]).mean())
    summary["null_mae_p_le_actual"] = float((np.asarray(null_mae) <= summary["nonbaseline_loocv_mae"]).mean())
    return summary, loocv


def candidate_predictions_fixed_zero(
    items: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    base: np.ndarray,
    views: list[str],
    view_summary: pd.DataFrame,
) -> pd.DataFrame:
    y = np.asarray([float(item["public_delta_vs_best"]) for item in items], dtype=float)
    rows: list[pd.DataFrame] = []
    for view in views:
        axes = e41.named_anchor_vectors(base, exclude=None)
        train_features = [e41.feature_row(str(item["file"]), base, axes, view) for item in items]
        query_features = [e41.feature_row(str(item["file"]), base, axes, view) for item in queries]
        x_train, cols = e41.matrix_from_rows(train_features)
        x_query = pd.DataFrame(query_features)[cols].to_numpy(float)
        pred, neigh = e41.predict_knn(x_train, y, x_query)
        part = pd.DataFrame(queries)[["name", "file", "role"]].copy()
        part["view"] = view
        part["predicted_delta_vs_best"] = pred
        part["predicted_public_lb"] = BEST_PUBLIC + pred
        part["neighbor_indices"] = neigh
        rows.append(part)
    out = pd.concat(rows, axis=0, ignore_index=True)
    usable_map = view_summary.set_index("view")["usable_zero_anchor_gate"].to_dict()
    fixed_map = view_summary.set_index("view")["fixed_zero_nonbaseline_gate"].to_dict()
    out["view_usable_zero_anchor_gate"] = out["view"].map(usable_map).fillna(False)
    out["view_fixed_zero_nonbaseline_gate"] = out["view"].map(fixed_map).fillna(False)
    out["predicted_better_than_raw05"] = out["predicted_delta_vs_best"] < RAW05_DELTA
    return out.sort_values(["view", "predicted_delta_vs_best"]).reset_index(drop=True)


def trajectory_stress(items: list[dict[str, Any]], base: np.ndarray, views: list[str]) -> pd.DataFrame:
    item_by_name = {str(item["name"]): item for item in items}
    y = np.asarray([float(item["public_delta_vs_best"]) for item in items], dtype=float)
    rows: list[dict[str, Any]] = []
    for view in views:
        axes = e41.named_anchor_vectors(base, exclude=None)
        train_features = [e41.feature_row(str(item["file"]), base, axes, view) for item in items]
        x_train, cols = e41.matrix_from_rows(train_features)
        for name, item in item_by_name.items():
            if name == "a2c8_best":
                continue
            anchor = e41.read_probs(str(item["file"]))
            anchor_logit_delta = e40.logit(anchor) - e40.logit(base)
            for scale in SCALES:
                pred_probs = e40.clip(1.0 / (1.0 + np.exp(-(e40.logit(base) + scale * anchor_logit_delta))))
                feats = feature_row_from_pred(pred_probs, base, axes, view)
                x_query = pd.DataFrame([feats])[cols].to_numpy(float)
                pred_delta, neigh = e41.predict_knn(x_train, y, x_query)
                rows.append(
                    {
                        "view": view,
                        "anchor": name,
                        "role": str(item["role"]),
                        "scale": float(scale),
                        "anchor_actual_delta": float(item["public_delta_vs_best"]),
                        "linear_delta_reference": float(scale * float(item["public_delta_vs_best"])),
                        "predicted_delta": float(pred_delta[0]),
                        "predicted_public_lb": BEST_PUBLIC + float(pred_delta[0]),
                        "neighbor_indices": neigh[0],
                    }
                )
    return pd.DataFrame(rows)


def add_candidate_and_trajectory_metrics(
    view_summary: pd.DataFrame,
    candidates: pd.DataFrame,
    trajectories: pd.DataFrame,
) -> pd.DataFrame:
    out = view_summary.copy()
    known_files = {str(item["file"]) for item in e41.known_items()}
    rows = []
    for _, row in out.iterrows():
        view = str(row["view"])
        cand = candidates[(candidates["view"].eq(view)) & (~candidates["file"].isin(known_files))].copy()
        better = cand[cand["predicted_delta_vs_best"] < RAW05_DELTA]
        best_delta = float(cand["predicted_delta_vs_best"].min()) if len(cand) else np.nan
        raw_adv = float(RAW05_DELTA - best_delta) if len(cand) else np.nan
        traj = trajectories[trajectories["view"].eq(view)].copy()
        monotonic_good = []
        for _anchor, group in traj.groupby("anchor"):
            vals = group.sort_values("scale")["predicted_delta"].to_numpy(float)
            monotonic_good.append(bool(np.all(np.diff(vals) >= -1e-10)))
        half = traj[np.isclose(traj["scale"], 0.50)]
        bad_half = half[half["anchor"].isin(e41.BAD_ANCHORS)]["predicted_delta"].mean()
        good_half = half[half["anchor"].isin(e41.GOOD_ANCHORS)]["predicted_delta"].mean()
        rows.append(
            {
                "view": view,
                "n_unobserved_candidates": int(len(cand)),
                "n_unobserved_better_than_raw05": int(len(better)),
                "best_unobserved_predicted_delta": best_delta,
                "best_unobserved_advantage_vs_raw05": raw_adv,
                "best_unobserved_advantage_to_mae_ratio": float(raw_adv / max(float(row["nonbaseline_loocv_mae"]), 1e-12)),
                "trajectory_monotonic_rate": float(np.mean(monotonic_good)) if monotonic_good else np.nan,
                "bad_half_predicted_delta_mean": float(bad_half),
                "good_half_predicted_delta_mean": float(good_half),
                "bad_half_above_good_half": bool(float(bad_half) > float(good_half)),
            }
        )
    metrics = pd.DataFrame(rows)
    out = out.merge(metrics, on="view", how="left", validate="one_to_one")
    out["fixed_zero_nonbaseline_gate"] = (
        (out["nonbaseline_loocv_mae"] <= 0.00085)
        & (out["pairwise_rank_accuracy"] >= 0.65)
        & (out["stage2_ordinal_order_correct"])
        & (out["raw05_predicted_best_nonbaseline"])
        & (out["bad_anchor_mean_underprediction"] <= 0.00125)
        & (out["trajectory_monotonic_rate"] >= 0.85)
        & (out["bad_half_above_good_half"])
    )
    out["frontier_resolution_gate"] = (
        (out["raw05_gap_to_mae_ratio"] >= 0.25)
        & (out["best_unobserved_advantage_to_mae_ratio"] >= 0.25)
    )
    out["zero_anchor_collapse_warning"] = (
        (out["n_unobserved_better_than_raw05"] >= 3)
        & (out["best_unobserved_advantage_to_mae_ratio"] < 0.25)
    )
    out["usable_zero_anchor_gate"] = (
        out["fixed_zero_nonbaseline_gate"]
        & out["frontier_resolution_gate"]
        & ~out["zero_anchor_collapse_warning"]
    )
    return out


def df_to_markdown(df: pd.DataFrame) -> str:
    return e40.df_to_markdown(df)


def write_report(view_summary: pd.DataFrame, loocv: pd.DataFrame, candidates: pd.DataFrame, trajectories: pd.DataFrame) -> None:
    fixed_n = int(view_summary["fixed_zero_nonbaseline_gate"].sum())
    usable_n = int(view_summary["usable_zero_anchor_gate"].sum())
    best_view = view_summary.sort_values(
        ["usable_zero_anchor_gate", "fixed_zero_nonbaseline_gate", "nonbaseline_loocv_mae"],
        ascending=[False, False, True],
    ).head(1)
    pivot = (
        candidates.pivot_table(
            index=["name", "file", "role"],
            columns="view",
            values="predicted_public_lb",
            aggfunc="first",
        )
        .reset_index()
    )
    pivot.columns = [str(c) for c in pivot.columns]
    sort_col = str(best_view.iloc[0]["view"])
    pivot = pivot.sort_values(sort_col)
    lines = [
        "# E42 Fixed-Zero Anchor Selector Calibration",
        "",
        "## Observe",
        "",
        "E41 fails the full LOO gate mainly because A2C8 is not recovered as the zero-loss current-best point when it is held out.",
        "",
        "## Wonder",
        "",
        "Is that failure just an overly harsh LOO design, or does keeping A2C8 fixed create a near-zero movement prior whose apparent candidate improvements are below selector resolution?",
        "",
        "## Hypothesis",
        "",
        "H41: if A2C8 should be treated as a known fixed zero anchor, then nonbaseline leave-one-out should recover public ordering and the selector should still have enough resolution to rank candidates beyond the raw05-A2C8 gap.",
        "",
        "## Method",
        "",
        "- A2C8 is kept in every training fold with delta 0.",
        "- Each nonbaseline public anchor is held out in turn.",
        "- Axis views still remove the held-out anchor's own axis before prediction.",
        "- A frontier-resolution gate compares nonbaseline MAE against the raw05-A2C8 public gap.",
        "- A zero-neighborhood collapse check counts unobserved candidates predicted better than raw05 by less than selector error.",
        "",
        "## Result",
        "",
        f"- fixed-zero nonbaseline gates: `{fixed_n}`.",
        f"- usable zero-anchor gates after frontier-resolution/collapse stress: `{usable_n}`.",
        "",
        "## View Summary",
        "",
        df_to_markdown(view_summary),
        "",
        "## Best View",
        "",
        df_to_markdown(best_view),
        "",
        "## Nonbaseline LOOCV",
        "",
        df_to_markdown(
            loocv[
                [
                    "view",
                    "name",
                    "public_delta_vs_best",
                    "predicted_delta",
                    "abs_error",
                    "underprediction",
                    "role",
                ]
            ].sort_values(["view", "public_delta_vs_best"])
        ),
        "",
        "## Candidate Sensor Predictions",
        "",
        df_to_markdown(pivot.head(20)),
        "",
        "## Trajectory Sample",
        "",
        df_to_markdown(
            trajectories[
                [
                    "view",
                    "anchor",
                    "scale",
                    "linear_delta_reference",
                    "predicted_delta",
                    "role",
                ]
            ].sort_values(["view", "anchor", "scale"]).head(80)
        ),
        "",
        "## Decision",
        "",
    ]
    if usable_n:
        lines.append(
            "At least one view survives fixed-zero and frontier-resolution stress. It can become a selector prior, but still requires independent agreement before a public submission claim."
        )
    elif fixed_n:
        lines.append(
            "Keeping A2C8 fixed makes some nonbaseline ordering look plausible, but the frontier-resolution/collapse stress rejects it as a submission gate."
        )
    else:
        lines.append(
            "Even with A2C8 fixed, the selector does not pass the nonbaseline calibration gate. Fixed-zero anchoring does not repair the bottleneck."
        )
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{VIEW_OUT.relative_to(ROOT)}`",
        f"- `{LOOCV_OUT.relative_to(ROOT)}`",
        f"- `{CAND_OUT.relative_to(ROOT)}`",
        f"- `{TRAJ_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    base = e41.read_probs(str(e40.KNOWN_ANCHORS[0]["file"]))
    items = e41.known_items()
    queries = e41.candidate_items()
    view_rows = []
    loocv_rows = []
    for view in VIEWS:
        summary, loocv = evaluate_fixed_zero_view(items, base, view)
        view_rows.append(summary)
        loocv_rows.append(loocv)
    view_summary_initial = pd.DataFrame(view_rows)
    loocv_all = pd.concat(loocv_rows, axis=0, ignore_index=True)
    candidates = candidate_predictions_fixed_zero(items, queries, base, VIEWS, view_summary_initial.assign(
        usable_zero_anchor_gate=False,
        fixed_zero_nonbaseline_gate=False,
    ))
    trajectories = trajectory_stress(items, base, VIEWS)
    view_summary = add_candidate_and_trajectory_metrics(view_summary_initial, candidates, trajectories).sort_values(
        [
            "usable_zero_anchor_gate",
            "fixed_zero_nonbaseline_gate",
            "nonbaseline_loocv_mae",
            "best_unobserved_advantage_to_mae_ratio",
        ],
        ascending=[False, False, True, False],
    )
    candidates = candidate_predictions_fixed_zero(items, queries, base, VIEWS, view_summary)

    view_summary.to_csv(VIEW_OUT, index=False)
    loocv_all.to_csv(LOOCV_OUT, index=False)
    candidates.to_csv(CAND_OUT, index=False)
    trajectories.to_csv(TRAJ_OUT, index=False)
    write_report(view_summary, loocv_all, candidates, trajectories)

    print(
        f"views={len(view_summary)} fixed={int(view_summary['fixed_zero_nonbaseline_gate'].sum())} "
        f"usable={int(view_summary['usable_zero_anchor_gate'].sum())}"
    )
    print(
        view_summary[
            [
                "view",
                "nonbaseline_loocv_mae",
                "pairwise_rank_accuracy",
                "raw05_gap_to_mae_ratio",
                "n_unobserved_better_than_raw05",
                "best_unobserved_advantage_to_mae_ratio",
                "fixed_zero_nonbaseline_gate",
                "frontier_resolution_gate",
                "zero_anchor_collapse_warning",
                "usable_zero_anchor_gate",
            ]
        ].to_string(index=False)
    )
    print("best candidate rows by best view:")
    best_view = str(view_summary.iloc[0]["view"])
    print(
        candidates[candidates["view"].eq(best_view)][
            [
                "name",
                "file",
                "role",
                "predicted_public_lb",
                "predicted_delta_vs_best",
                "predicted_better_than_raw05",
            ]
        ].head(20).to_string(index=False)
    )
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
