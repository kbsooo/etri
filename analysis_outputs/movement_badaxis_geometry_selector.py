#!/usr/bin/env python3
"""E41 movement + bad-axis geometry selector audit.

E40 showed that test-movement fingerprints recover some public ordering but
underprice bad JEPA anchors. This audit asks whether adding logit-space
direction geometry against known raw/good/bad anchors makes the selector
strong enough to rank candidate sensors.

Known public LBs are used only in leave-one-anchor-out selector tests and in
the final diagnostic sensor prior. The strict gate requires the selector to
recover both ordering and bad-anchor severity before it can rank new files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import test_movement_fingerprint_selector as e40


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = e40.TARGETS
BEST_PUBLIC = e40.BEST_PUBLIC

VIEW_OUT = OUT / "movement_badaxis_geometry_selector_views.csv"
LOOCV_OUT = OUT / "movement_badaxis_geometry_selector_loocv.csv"
CAND_OUT = OUT / "movement_badaxis_geometry_selector_candidates.csv"
REPORT_OUT = OUT / "movement_badaxis_geometry_selector_report.md"

BAD_ANCHORS = {"q2_jepa_bad", "lejepa_bad", "jepa_residual_bad"}
GOOD_ANCHORS = {"raw_timeline", "stage2", "ordinal", "final9"}


def read_probs(file_name: str) -> np.ndarray:
    return e40.clip(e40.read_submission(file_name)[TARGETS].to_numpy(float))


def flatten_logit_delta(pred: np.ndarray, base: np.ndarray) -> np.ndarray:
    return (e40.logit(pred) - e40.logit(base)).reshape(-1)


def named_anchor_vectors(base: np.ndarray, exclude: str | None = None) -> dict[str, np.ndarray]:
    vectors: dict[str, np.ndarray] = {}
    for anchor in e40.KNOWN_ANCHORS:
        name = str(anchor["name"])
        if name == "a2c8_best" or name == exclude:
            continue
        pred = read_probs(str(anchor["file"]))
        vectors[name] = flatten_logit_delta(pred, base)
    return vectors


def normed_dot(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def signed_projection(a: np.ndarray, b: np.ndarray) -> float:
    nb = float(np.linalg.norm(b))
    if nb <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / nb)


def compact_movement_features(pred: np.ndarray, base: np.ndarray) -> dict[str, float]:
    prob_delta = pred - base
    logit_delta = e40.logit(pred) - e40.logit(base)
    entropy_delta = e40.entropy(pred) - e40.entropy(base)
    feats: dict[str, float] = {}
    groups = {
        "all": list(range(len(TARGETS))),
        "q": [0, 1, 2],
        "s": [3, 4, 5, 6],
        "q2q3": [1, 2],
        "q3s4": [2, 6],
    }
    for group_name, cols in groups.items():
        pdlt = prob_delta[:, cols]
        ldlt = logit_delta[:, cols]
        edlt = entropy_delta[:, cols]
        feats[f"compact__{group_name}__prob_mean"] = float(pdlt.mean())
        feats[f"compact__{group_name}__prob_abs_mean"] = float(np.abs(pdlt).mean())
        feats[f"compact__{group_name}__prob_abs_p90"] = float(np.quantile(np.abs(pdlt), 0.90))
        feats[f"compact__{group_name}__prob_abs_max"] = float(np.max(np.abs(pdlt)))
        feats[f"compact__{group_name}__logit_mean"] = float(ldlt.mean())
        feats[f"compact__{group_name}__logit_abs_mean"] = float(np.abs(ldlt).mean())
        feats[f"compact__{group_name}__logit_abs_p90"] = float(np.quantile(np.abs(ldlt), 0.90))
        feats[f"compact__{group_name}__logit_l2"] = float(np.linalg.norm(ldlt.reshape(-1)) / np.sqrt(ldlt.size))
        feats[f"compact__{group_name}__entropy_mean"] = float(edlt.mean())
        feats[f"compact__{group_name}__entropy_abs_mean"] = float(np.abs(edlt).mean())
        feats[f"compact__{group_name}__positive_move_frac"] = float((pdlt > 0).mean())

    abs_by_target = np.abs(logit_delta).mean(axis=0)
    denom = float(abs_by_target.sum() + 1e-12)
    for target, val in zip(TARGETS, abs_by_target, strict=True):
        feats[f"compact__share_abs_logit__{target}"] = float(val / denom)
    for j, target in enumerate(TARGETS):
        feats[f"compact__{target}__prob_mean"] = float(prob_delta[:, j].mean())
        feats[f"compact__{target}__prob_abs_mean"] = float(np.abs(prob_delta[:, j]).mean())
        feats[f"compact__{target}__logit_mean"] = float(logit_delta[:, j].mean())
        feats[f"compact__{target}__logit_abs_mean"] = float(np.abs(logit_delta[:, j]).mean())
        feats[f"compact__{target}__entropy_mean"] = float(entropy_delta[:, j].mean())
    return feats


def axis_geometry_features(
    pred: np.ndarray,
    base: np.ndarray,
    axis_vectors: dict[str, np.ndarray],
    named: bool,
) -> dict[str, float]:
    x = flatten_logit_delta(pred, base)
    x_norm = float(np.linalg.norm(x))
    feats: dict[str, float] = {
        "axis__x_l2": x_norm,
        "axis__x_l2_per_cell": float(x_norm / np.sqrt(x.size)),
        "axis__x_abs_mean": float(np.abs(x).mean()),
        "axis__x_abs_p90": float(np.quantile(np.abs(x), 0.90)),
        "axis__x_abs_max": float(np.max(np.abs(x))),
    }
    per_axis: list[dict[str, float | str]] = []
    for name, vec in axis_vectors.items():
        cos = normed_dot(x, vec)
        proj = signed_projection(x, vec)
        row: dict[str, float | str] = {
            "name": name,
            "cos": cos,
            "proj": proj,
            "abs_proj": abs(proj),
            "proj_per_x": float(proj / max(x_norm, 1e-12)),
        }
        per_axis.append(row)
        if named:
            safe = name.replace("-", "_")
            feats[f"axis_named__{safe}__cos"] = cos
            feats[f"axis_named__{safe}__proj"] = proj
            feats[f"axis_named__{safe}__abs_proj"] = abs(proj)
            feats[f"axis_named__{safe}__proj_per_x"] = float(proj / max(x_norm, 1e-12))

    def stats(prefix: str, names: set[str]) -> None:
        rows = [r for r in per_axis if str(r["name"]) in names]
        if not rows:
            for suffix in ("cos_max", "cos_mean", "proj_pos_sum", "abs_proj_sum", "proj_per_x_pos_sum"):
                feats[f"axis_group__{prefix}__{suffix}"] = 0.0
            return
        cos_vals = np.asarray([float(r["cos"]) for r in rows], dtype=float)
        proj_vals = np.asarray([float(r["proj"]) for r in rows], dtype=float)
        abs_proj_vals = np.asarray([float(r["abs_proj"]) for r in rows], dtype=float)
        per_x_vals = np.asarray([float(r["proj_per_x"]) for r in rows], dtype=float)
        feats[f"axis_group__{prefix}__cos_max"] = float(cos_vals.max())
        feats[f"axis_group__{prefix}__cos_mean"] = float(cos_vals.mean())
        feats[f"axis_group__{prefix}__cos_p90"] = float(np.quantile(cos_vals, 0.90))
        feats[f"axis_group__{prefix}__proj_pos_sum"] = float(np.maximum(proj_vals, 0.0).sum())
        feats[f"axis_group__{prefix}__abs_proj_sum"] = float(abs_proj_vals.sum())
        feats[f"axis_group__{prefix}__proj_per_x_pos_sum"] = float(np.maximum(per_x_vals, 0.0).sum())
        feats[f"axis_group__{prefix}__proj_per_x_mean"] = float(per_x_vals.mean())

    stats("bad", BAD_ANCHORS)
    stats("good", GOOD_ANCHORS)
    feats["axis_group__bad_minus_good_cos_max"] = (
        feats["axis_group__bad__cos_max"] - feats["axis_group__good__cos_max"]
    )
    feats["axis_group__bad_minus_good_proj_pos_sum"] = (
        feats["axis_group__bad__proj_pos_sum"] - feats["axis_group__good__proj_pos_sum"]
    )
    feats["axis_group__bad_to_good_abs_proj_ratio"] = float(
        feats["axis_group__bad__abs_proj_sum"] / max(feats["axis_group__good__abs_proj_sum"], 1e-12)
    )
    return feats


def feature_row(
    file_name: str,
    base: np.ndarray,
    axis_vectors: dict[str, np.ndarray],
    view: str,
) -> dict[str, float]:
    pred = read_probs(file_name)
    feats: dict[str, float] = {}
    if "compact" in view:
        feats.update(compact_movement_features(pred, base))
    if "axis_group" in view:
        feats.update(axis_geometry_features(pred, base, axis_vectors, named=False))
    elif "axis_named" in view:
        feats.update(axis_geometry_features(pred, base, axis_vectors, named=True))
    return feats


def known_items() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for anchor in e40.KNOWN_ANCHORS:
        rows.append(
            {
                "name": str(anchor["name"]),
                "file": str(anchor["file"]),
                "role": str(anchor["role"]),
                "public_lb": float(anchor["public_lb"]),
                "public_delta_vs_best": float(anchor["public_lb"]) - BEST_PUBLIC,
            }
        )
    return rows


def candidate_items() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sensor_path = OUT / "worldview_sensor_discriminability_audit.csv"
    if sensor_path.exists():
        sensors = pd.read_csv(sensor_path)
        for _, row in sensors.iterrows():
            rows.append({"name": str(row["role"]), "file": str(row["file"]), "role": str(row["lane"])})
    rows.extend({"name": r["name"], "file": r["file"], "role": r["role"]} for r in known_items())
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        file_name = str(row["file"])
        if file_name in seen:
            continue
        seen.add(file_name)
        try:
            e40.resolve_file(file_name)
        except FileNotFoundError:
            continue
        deduped.append(row)
    return deduped


def scale_train_query(x_train: np.ndarray, x_query: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    med = np.nanmedian(x_train, axis=0)
    x_train = np.where(np.isfinite(x_train), x_train, med)
    x_query = np.where(np.isfinite(x_query), x_query, med)
    mu = x_train.mean(axis=0)
    sd = x_train.std(axis=0)
    keep = sd > 1e-10
    if int(keep.sum()) == 0:
        raise RuntimeError("all selector features are constant")
    return (x_train[:, keep] - mu[keep]) / sd[keep], (x_query[:, keep] - mu[keep]) / sd[keep]


def predict_knn(x_train: np.ndarray, y_train: np.ndarray, x_query: np.ndarray) -> tuple[np.ndarray, list[str]]:
    x_train_s, x_query_s = scale_train_query(x_train, x_query)
    preds = []
    neigh = []
    for x in x_query_s:
        dist = np.linalg.norm(x_train_s - x[None, :], axis=1)
        order = np.argsort(dist)
        k = min(3, len(order))
        top = order[:k]
        weights = 1.0 / np.maximum(dist[top], 1e-6) ** 2
        weights = weights / weights.sum()
        preds.append(float(np.dot(weights, y_train[top])))
        neigh.append(",".join(str(int(i)) for i in top))
    return np.asarray(preds, dtype=float), neigh


def matrix_from_rows(rows: list[dict[str, float]]) -> tuple[np.ndarray, list[str]]:
    frame = pd.DataFrame(rows)
    cols = sorted(str(c) for c in frame.columns)
    return frame[cols].to_numpy(float), cols


def fold_features(
    items: list[dict[str, Any]],
    base: np.ndarray,
    view: str,
    exclude_axis_name: str | None,
) -> tuple[pd.DataFrame, list[str]]:
    axes = named_anchor_vectors(base, exclude=exclude_axis_name)
    rows: list[dict[str, Any]] = []
    feature_rows: list[dict[str, float]] = []
    for item in items:
        feats = feature_row(str(item["file"]), base, axes, view)
        row = dict(item)
        row.update(feats)
        rows.append(row)
        feature_rows.append(feats)
    _, cols = matrix_from_rows(feature_rows)
    return pd.DataFrame(rows), cols


def evaluate_view(items: list[dict[str, Any]], base: np.ndarray, view: str) -> tuple[dict[str, Any], pd.DataFrame]:
    y = np.asarray([float(item["public_delta_vs_best"]) for item in items], dtype=float)
    pred = np.zeros(len(items), dtype=float)
    neigh_txt: list[str] = []
    fold_payload: list[tuple[np.ndarray, np.ndarray, list[int]]] = []

    for i, item in enumerate(items):
        exclude = str(item["name"]) if "axis" in view else None
        fold_frame, cols = fold_features(items, base, view, exclude_axis_name=exclude)
        x = fold_frame[cols].to_numpy(float)
        train_idx = [j for j in range(len(items)) if j != i]
        p, neigh = predict_knn(x[train_idx], y[train_idx], x[[i]])
        pred[i] = p[0]
        neigh_txt.append(neigh[0])
        fold_payload.append((x[train_idx], x[[i]], train_idx))

    loocv = pd.DataFrame(items)[["name", "file", "role", "public_lb", "public_delta_vs_best"]].copy()
    loocv["view"] = view
    loocv["predicted_delta"] = pred
    loocv["predicted_public_lb"] = BEST_PUBLIC + pred
    loocv["error"] = pred - y
    loocv["abs_error"] = np.abs(loocv["error"])
    loocv["underprediction"] = np.maximum(y - pred, 0.0)
    loocv["neighbor_indices"] = neigh_txt

    actual_stage2 = float(loocv.loc[loocv["name"].eq("stage2"), "public_delta_vs_best"].iloc[0])
    actual_ordinal = float(loocv.loc[loocv["name"].eq("ordinal"), "public_delta_vs_best"].iloc[0])
    pred_stage2 = float(loocv.loc[loocv["name"].eq("stage2"), "predicted_delta"].iloc[0])
    pred_ordinal = float(loocv.loc[loocv["name"].eq("ordinal"), "predicted_delta"].iloc[0])
    pred_a2c8 = float(loocv.loc[loocv["name"].eq("a2c8_best"), "predicted_delta"].iloc[0])
    bad = loocv[loocv["name"].isin(BAD_ANCHORS)]
    bad_under = float(bad["underprediction"].mean()) if len(bad) else np.nan
    bad_max_under = float(bad["underprediction"].max()) if len(bad) else np.nan
    bad_pred_mean = float(bad["predicted_delta"].mean()) if len(bad) else np.nan
    raw_pred = float(loocv.loc[loocv["name"].eq("raw_timeline"), "predicted_delta"].iloc[0])
    summary = {
        "view": view,
        "n_features": int(len(fold_features(items, base, view, None)[1])),
        "loocv_mae": float(loocv["abs_error"].mean()),
        "loocv_max_abs_error": float(loocv["abs_error"].max()),
        "pairwise_rank_accuracy": e40.pairwise_rank_accuracy(y, pred),
        "spearman": e40.spearman_corr(y, pred),
        "stage2_ordinal_order_correct": bool(np.sign(actual_stage2 - actual_ordinal) == np.sign(pred_stage2 - pred_ordinal)),
        "a2c8_predicted_best": bool(pred_a2c8 <= float(np.min(pred))),
        "raw05_near_best": bool(raw_pred <= float(np.quantile(pred, 0.40))),
        "bad_anchor_mean_underprediction": bad_under,
        "bad_anchor_max_underprediction": bad_max_under,
        "bad_anchor_predicted_delta_mean": bad_pred_mean,
    }

    rng = np.random.default_rng(20260528)
    null_rank = []
    null_mae = []
    for _ in range(500):
        y_perm = rng.permutation(y)
        pred_perm = np.zeros(len(items), dtype=float)
        for i, (x_train, x_query, train_idx) in enumerate(fold_payload):
            p, _ = predict_knn(x_train, y_perm[train_idx], x_query)
            pred_perm[i] = p[0]
        null_rank.append(e40.pairwise_rank_accuracy(y_perm, pred_perm))
        null_mae.append(float(np.mean(np.abs(pred_perm - y_perm))))
    summary["null_rank_p_ge_actual"] = float((np.asarray(null_rank) >= summary["pairwise_rank_accuracy"]).mean())
    summary["null_mae_p_le_actual"] = float((np.asarray(null_mae) <= summary["loocv_mae"]).mean())
    summary["strict_selector_gate"] = bool(
        summary["loocv_mae"] <= 0.00055
        and summary["pairwise_rank_accuracy"] >= 0.75
        and summary["stage2_ordinal_order_correct"]
        and summary["a2c8_predicted_best"]
        and summary["bad_anchor_mean_underprediction"] <= 0.00100
        and summary["null_rank_p_ge_actual"] <= 0.10
    )
    summary["loose_selector_gate"] = bool(
        summary["loocv_mae"] <= 0.00085
        and summary["pairwise_rank_accuracy"] >= 0.65
        and summary["stage2_ordinal_order_correct"]
        and summary["bad_anchor_mean_underprediction"] <= 0.00150
    )
    return summary, loocv


def candidate_predictions(items: list[dict[str, Any]], queries: list[dict[str, Any]], base: np.ndarray, views: list[str], view_summary: pd.DataFrame) -> pd.DataFrame:
    y = np.asarray([float(item["public_delta_vs_best"]) for item in items], dtype=float)
    rows: list[pd.DataFrame] = []
    for view in views:
        axes = named_anchor_vectors(base, exclude=None)
        known_features = []
        query_features = []
        for item in items:
            known_features.append(feature_row(str(item["file"]), base, axes, view))
        for item in queries:
            query_features.append(feature_row(str(item["file"]), base, axes, view))
        x_train, cols = matrix_from_rows(known_features)
        x_query = pd.DataFrame(query_features)[cols].to_numpy(float)
        pred, neigh = predict_knn(x_train, y, x_query)
        part = pd.DataFrame(queries)[["name", "file", "role"]].copy()
        part["view"] = view
        part["predicted_delta_vs_best"] = pred
        part["predicted_public_lb"] = BEST_PUBLIC + pred
        part["neighbor_indices"] = neigh
        rows.append(part)
    out = pd.concat(rows, axis=0, ignore_index=True)
    strict_map = view_summary.set_index("view")["strict_selector_gate"].to_dict()
    loose_map = view_summary.set_index("view")["loose_selector_gate"].to_dict()
    out["view_strict_gate"] = out["view"].map(strict_map).fillna(False)
    out["view_loose_gate"] = out["view"].map(loose_map).fillna(False)
    return out.sort_values(["view", "predicted_delta_vs_best"]).reset_index(drop=True)


def write_report(view_summary: pd.DataFrame, loocv: pd.DataFrame, candidates: pd.DataFrame) -> None:
    strict_n = int(view_summary["strict_selector_gate"].sum())
    loose_n = int(view_summary["loose_selector_gate"].sum())
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
    sort_col = "compact_axis_named" if "compact_axis_named" in pivot.columns else str(view_summary.iloc[0]["view"])
    pivot = pivot.sort_values(sort_col)
    lines = [
        "# E41 Movement + Bad-Axis Geometry Selector",
        "",
        "## Observe",
        "",
        "E40 recovered the stage2/ordinal public order, but it missed A2C8-best and underpredicted bad JEPA anchor severity.",
        "",
        "## Wonder",
        "",
        "Does adding logit-space direction geometry against raw/good/bad anchor movements make movement anatomy a stricter public selector?",
        "",
        "## Hypothesis",
        "",
        "H40: if the missing E40 component is bad-axis geometry rather than general movement scale, then a LOO-safe movement+axis selector should reduce bad-anchor underprediction while preserving stage2/ordinal order and A2C8-best.",
        "",
        "## Method",
        "",
        "- Base is A2C8. Features are computed from candidate logit/probability/entropy movement relative to A2C8.",
        "- Axis features use cosine and projection against known raw/medium/bad public anchor directions.",
        "- During leave-one-anchor-out, the left-out anchor's own axis is removed before features are recomputed.",
        "- Strict gate additionally requires mean bad-anchor underprediction <= 0.0010.",
        "",
        "## Result",
        "",
        f"- strict selector views: `{strict_n}`.",
        f"- loose selector views: `{loose_n}`.",
        "",
        "## View Summary",
        "",
        e40.df_to_markdown(view_summary),
        "",
        "## Known Anchor LOOCV",
        "",
        e40.df_to_markdown(
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
        e40.df_to_markdown(pivot.head(20)),
        "",
        "## Decision",
        "",
    ]
    if strict_n:
        lines.append(
            "At least one LOO-safe movement+axis view passes the strict selector gate. It can be used as a candidate prior, but only after agreement with non-public raw/anchor/selector stresses."
        )
    elif loose_n:
        lines.append(
            "Bad-axis geometry improves the movement selector only to a loose diagnostic prior. It is not a normal submission gate."
        )
    else:
        lines.append(
            "Adding bad-axis geometry does not create a certified selector. The E40 failure is not solved by simple direction geometry."
        )
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{VIEW_OUT.relative_to(ROOT)}`",
        f"- `{LOOCV_OUT.relative_to(ROOT)}`",
        f"- `{CAND_OUT.relative_to(ROOT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    base = read_probs(str(e40.KNOWN_ANCHORS[0]["file"]))
    items = known_items()
    queries = candidate_items()
    views = [
        "compact",
        "axis_group",
        "axis_named",
        "compact_axis_group",
        "compact_axis_named",
    ]
    view_rows = []
    loocv_rows = []
    for view in views:
        summary, loocv = evaluate_view(items, base, view)
        view_rows.append(summary)
        loocv_rows.append(loocv)
    view_summary = pd.DataFrame(view_rows).sort_values(
        [
            "strict_selector_gate",
            "loose_selector_gate",
            "loocv_mae",
            "bad_anchor_mean_underprediction",
        ],
        ascending=[False, False, True, True],
    )
    loocv_all = pd.concat(loocv_rows, axis=0, ignore_index=True)
    cand = candidate_predictions(items, queries, base, views, view_summary)
    view_summary.to_csv(VIEW_OUT, index=False)
    loocv_all.to_csv(LOOCV_OUT, index=False)
    cand.to_csv(CAND_OUT, index=False)
    write_report(view_summary, loocv_all, cand)

    print(
        f"views={len(view_summary)} strict={int(view_summary['strict_selector_gate'].sum())} "
        f"loose={int(view_summary['loose_selector_gate'].sum())}"
    )
    print(view_summary.to_string(index=False))
    print("candidate compact_axis_named:")
    print(
        cand[cand["view"].eq("compact_axis_named")][
            [
                "name",
                "file",
                "role",
                "predicted_public_lb",
                "predicted_delta_vs_best",
                "view_strict_gate",
                "view_loose_gate",
            ]
        ]
        .sort_values("predicted_public_lb")
        .head(20)
        .to_string(index=False)
    )
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
