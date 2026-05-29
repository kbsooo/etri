#!/usr/bin/env python3
"""E136: does target compression make the safe remainder visible?

E133/E134/E135 all tried to see the same cell-level safe-remainder teacher.
The next SAUNA question is whether that target is the wrong representation:
maybe the hidden law is visible only after compressing cells into row, block,
or target-group states.  This audit keeps the same hidden-block holdout and
asks whether compressed target representations are materially easier to
predict from raw/block context or old-prediction geometry.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
sys.path.insert(0, str(OUT))

import e134_raw_block_colocation_predictability as e134  # noqa: E402
import e135_prediction_manifold_remainder_visibility as e135  # noqa: E402


TARGETS = e135.TARGETS
PRIMARY_TEACHER = "all_sign_co_vetonull_density"
RAW_VIEWS = ["night_all", "night_mobility", "all_raw_views"]


@dataclass
class EvalRow:
    unit_type: str
    feature_set: str
    model: str
    n_units: int
    n_features: int
    top10_truth_mass: float
    top10_enrichment: float
    top10_capture_ratio: float
    top10_overlap: float
    top20_truth_mass: float
    top20_enrichment: float
    top20_capture_ratio: float
    top20_overlap: float
    js: float
    cosine: float
    pearson: float
    spearman: float
    top10_profile: str


def normalize(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64).copy()
    arr[~np.isfinite(arr)] = 0.0
    arr = np.maximum(arr, 0.0)
    total = float(arr.sum())
    if total <= 0.0:
        return np.full(len(arr), 1.0 / len(arr), dtype=np.float64)
    return arr / total


def minmax(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64).copy()
    finite = np.isfinite(arr)
    if not finite.any():
        return np.ones(len(arr), dtype=np.float64)
    fill = float(np.nanmedian(arr[finite]))
    arr[~finite] = fill
    lo = float(np.min(arr))
    hi = float(np.max(arr))
    if hi <= lo:
        return np.ones(len(arr), dtype=np.float64)
    return (arr - lo) / (hi - lo)


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    pp = normalize(p)
    qq = normalize(q)
    mm = 0.5 * (pp + qq)
    eps = 1.0e-15
    return float(
        0.5 * np.sum(pp * np.log((pp + eps) / (mm + eps)))
        + 0.5 * np.sum(qq * np.log((qq + eps) / (mm + eps)))
    )


def safe_corr(a: np.ndarray, b: np.ndarray, method: str) -> float:
    aa = pd.Series(np.asarray(a, dtype=np.float64))
    bb = pd.Series(np.asarray(b, dtype=np.float64))
    if aa.nunique(dropna=True) <= 1 or bb.nunique(dropna=True) <= 1:
        return 0.0
    return float(aa.corr(bb, method=method))


def top_mask(values: np.ndarray, frac: float) -> np.ndarray:
    k = max(1, int(np.ceil(len(values) * frac)))
    idx = np.argsort(np.asarray(values, dtype=np.float64))[-k:]
    mask = np.zeros(len(values), dtype=bool)
    mask[idx] = True
    return mask


def profile_string(frame: pd.DataFrame, mask: np.ndarray) -> str:
    if "target" in frame.columns:
        counts = frame.loc[mask, "target"].value_counts().reindex(TARGETS, fill_value=0)
        return ",".join(f"{t}:{int(counts[t])}" for t in TARGETS if int(counts[t]) > 0)
    if "target_family" in frame.columns:
        counts = frame.loc[mask, "target_family"].value_counts()
        return ",".join(f"{k}:{int(v)}" for k, v in counts.items())
    if "subject_id" in frame.columns:
        counts = frame.loc[mask, "subject_id"].value_counts()
        return ",".join(f"{k}:{int(v)}" for k, v in counts.head(6).items())
    return f"units:{int(mask.sum())}"


def evaluate_prediction(
    unit: pd.DataFrame,
    pred_raw: np.ndarray,
    unit_type: str,
    feature_set: str,
    model: str,
    n_features: int,
) -> EvalRow:
    truth = normalize(unit["teacher"].to_numpy(dtype=np.float64))
    pred = normalize(minmax(pred_raw))
    truth_top10 = top_mask(truth, 0.10)
    pred_top10 = top_mask(pred, 0.10)
    truth_top20 = top_mask(truth, 0.20)
    pred_top20 = top_mask(pred, 0.20)
    oracle10 = float(truth[truth_top10].sum())
    oracle20 = float(truth[truth_top20].sum())
    mass10 = float(truth[pred_top10].sum())
    mass20 = float(truth[pred_top20].sum())
    return EvalRow(
        unit_type=unit_type,
        feature_set=feature_set,
        model=model,
        n_units=len(unit),
        n_features=int(n_features),
        top10_truth_mass=mass10,
        top10_enrichment=mass10 / 0.10,
        top10_capture_ratio=mass10 / oracle10 if oracle10 > 0.0 else 0.0,
        top10_overlap=float(np.mean(truth_top10 & pred_top10) * len(unit) / max(1, pred_top10.sum())),
        top20_truth_mass=mass20,
        top20_enrichment=mass20 / 0.20,
        top20_capture_ratio=mass20 / oracle20 if oracle20 > 0.0 else 0.0,
        top20_overlap=float(np.mean(truth_top20 & pred_top20) * len(unit) / max(1, pred_top20.sum())),
        js=js_divergence(truth, pred),
        cosine=float(np.dot(truth, pred) / (np.linalg.norm(truth) * np.linalg.norm(pred) + 1.0e-15)),
        pearson=safe_corr(truth, pred, "pearson"),
        spearman=safe_corr(truth, pred, "spearman"),
        top10_profile=profile_string(unit, pred_top10),
    )


def hidden_block_ridge(x: np.ndarray, y: np.ndarray, groups: np.ndarray) -> np.ndarray:
    out = np.zeros(len(y), dtype=np.float64)
    for group in pd.unique(groups):
        test = groups == group
        train = ~test
        model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
        model.fit(x[train], y[train])
        out[test] = model.predict(x[test])
    return out


def hidden_block_knn(x: np.ndarray, y: np.ndarray, groups: np.ndarray, k: int = 8) -> np.ndarray:
    out = np.zeros(len(y), dtype=np.float64)
    for group in pd.unique(groups):
        test = groups == group
        train = ~test
        scaler = StandardScaler()
        x_train = scaler.fit_transform(x[train])
        x_test = scaler.transform(x[test])
        y_train = y[train]
        kk = min(k, len(y_train))
        for local_i, vector in zip(np.where(test)[0], x_test):
            dist = np.linalg.norm(x_train - vector, axis=1)
            take = np.argsort(dist)[:kk]
            weights = 1.0 / (dist[take] + 1.0e-6)
            out[local_i] = float(np.average(y_train[take], weights=weights))
    return out


def encode(frame: pd.DataFrame, cat_cols: list[str], num_cols: list[str]) -> np.ndarray:
    parts = []
    if cat_cols:
        parts.append(pd.get_dummies(frame[cat_cols].astype(str), prefix=cat_cols, dtype=float))
    nums = pd.DataFrame(index=frame.index)
    for col in num_cols:
        nums[col] = pd.to_numeric(frame[col], errors="coerce").fillna(0.0).astype(float)
    if num_cols:
        parts.append(nums)
    if not parts:
        return np.ones((len(frame), 1), dtype=np.float64)
    return pd.concat(parts, axis=1).to_numpy(dtype=np.float64)


def block_raw_features(unit: pd.DataFrame, block_ids: list[str], raw: dict[str, np.ndarray], view: str) -> np.ndarray:
    block_index = {bid: i for i, bid in enumerate(block_ids)}
    idx = unit["hidden_block_id"].map(block_index)
    if idx.isna().any():
        missing = sorted(unit.loc[idx.isna(), "hidden_block_id"].unique().tolist())
        raise KeyError(f"missing blocks for {view}: {missing[:5]}")
    return raw[view][idx.to_numpy(dtype=int)]


def row_prediction_matrix(submissions: dict[str, np.ndarray]) -> np.ndarray:
    e95 = submissions["e95"]
    mixmin = submissions["mixmin"]
    probs = np.concatenate([submissions[name] for name in e135.SUBMISSIONS], axis=1)
    logits = np.concatenate([e135.logit(submissions[name]) for name in e135.SUBMISSIONS], axis=1)
    delta_e95 = np.concatenate(
        [e135.logit(submissions[name]) - e135.logit(e95) for name in e135.SUBMISSIONS if name != "e95"],
        axis=1,
    )
    delta_mixmin = np.concatenate(
        [e135.logit(submissions[name]) - e135.logit(mixmin) for name in e135.SUBMISSIONS if name != "mixmin"],
        axis=1,
    )
    full = np.concatenate([probs, logits, delta_e95, delta_mixmin], axis=1)
    pca = make_pipeline(StandardScaler(), PCA(n_components=12, random_state=136)).fit_transform(full)
    stack = np.stack([submissions[name] for name in e135.SUBMISSIONS], axis=0)
    uncertainty = np.concatenate([stack.mean(axis=0), stack.std(axis=0), stack.max(axis=0) - stack.min(axis=0)], axis=1)
    return np.concatenate([pca, uncertainty], axis=1)


def aggregate_rows(cell: pd.DataFrame) -> pd.DataFrame:
    meta_cols = [
        "sub_idx",
        "hidden_block_id",
        "subject_id",
        "context_type",
        "block_len_bin",
        "pos_bin",
        "edge_like",
        "is_weekend",
        "block_n_rows",
        "edge_distance",
    ]
    out = cell.groupby(meta_cols, dropna=False, as_index=False)[PRIMARY_TEACHER].sum()
    return out.rename(columns={PRIMARY_TEACHER: "teacher"})


def aggregate_block_target(cell: pd.DataFrame) -> pd.DataFrame:
    block_meta = block_metadata(cell)
    out = cell.groupby(["hidden_block_id", "target"], dropna=False, as_index=False)[PRIMARY_TEACHER].sum()
    out = out.rename(columns={PRIMARY_TEACHER: "teacher"})
    return out.merge(block_meta, on="hidden_block_id", how="left")


def family_of_target(target: str) -> str:
    if target in {"Q1", "Q3"}:
        return "Q1Q3"
    if target in {"Q2", "S3"}:
        return "Q2S3"
    return "other"


def aggregate_block_family(cell: pd.DataFrame) -> pd.DataFrame:
    tmp = cell.copy()
    tmp["target_family"] = tmp["target"].map(family_of_target)
    block_meta = block_metadata(cell)
    out = tmp.groupby(["hidden_block_id", "target_family"], dropna=False, as_index=False)[PRIMARY_TEACHER].sum()
    out = out.rename(columns={PRIMARY_TEACHER: "teacher"})
    return out.merge(block_meta, on="hidden_block_id", how="left")


def aggregate_block_total(cell: pd.DataFrame) -> pd.DataFrame:
    block_meta = block_metadata(cell)
    out = cell.groupby(["hidden_block_id"], dropna=False, as_index=False)[PRIMARY_TEACHER].sum()
    out = out.rename(columns={PRIMARY_TEACHER: "teacher"})
    return out.merge(block_meta, on="hidden_block_id", how="left")


def block_metadata(cell: pd.DataFrame) -> pd.DataFrame:
    def first_value(series: pd.Series) -> object:
        return series.dropna().iloc[0] if series.dropna().size else np.nan

    grouped = cell.groupby("hidden_block_id", dropna=False)
    meta = grouped.agg(
        subject_id=("subject_id", first_value),
        context_type=("context_type", first_value),
        block_len_bin=("block_len_bin", first_value),
        block_n_rows=("sub_idx", "nunique"),
        edge_like_frac=("edge_like", lambda s: float(pd.Series(s).astype(bool).mean())),
        is_weekend_frac=("is_weekend", lambda s: float(pd.Series(s).astype(bool).mean())),
        min_edge_distance=("edge_distance", "min"),
        mean_edge_distance=("edge_distance", "mean"),
    ).reset_index()
    return meta


def row_pred_features(unit: pd.DataFrame, row_pred: np.ndarray) -> np.ndarray:
    idx = unit["sub_idx"].to_numpy(dtype=int)
    return row_pred[idx]


def block_pred_features(unit: pd.DataFrame, row_unit: pd.DataFrame, row_pred: np.ndarray) -> np.ndarray:
    row_frame = row_unit[["sub_idx", "hidden_block_id"]].copy()
    pred_cols = [f"pred_{i}" for i in range(row_pred.shape[1])]
    row_pred_frame = pd.DataFrame(row_pred[row_frame["sub_idx"].to_numpy(dtype=int)], columns=pred_cols)
    row_pred_frame["hidden_block_id"] = row_frame["hidden_block_id"].to_numpy()
    stats = row_pred_frame.groupby("hidden_block_id")[pred_cols].agg(["mean", "std"])
    stats.columns = [f"{a}_{b}" for a, b in stats.columns]
    stats = stats.fillna(0.0)
    return unit["hidden_block_id"].map(lambda b: stats.loc[b].to_numpy(dtype=np.float64)).to_list()


def as_matrix(rows: list[np.ndarray] | np.ndarray) -> np.ndarray:
    if isinstance(rows, np.ndarray):
        return rows
    return np.vstack(rows).astype(np.float64)


def make_feature_sets(
    unit_type: str,
    unit: pd.DataFrame,
    row_unit: pd.DataFrame,
    row_pred: np.ndarray,
    block_ids: list[str],
    raw: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    if unit_type == "row_total":
        meta = encode(
            unit,
            ["subject_id", "context_type", "block_len_bin", "pos_bin", "edge_like", "is_weekend"],
            ["block_n_rows", "edge_distance"],
        )
        pred = row_pred_features(unit, row_pred)
    elif unit_type == "block_target":
        meta = encode(
            unit,
            ["target", "subject_id", "context_type", "block_len_bin"],
            ["block_n_rows", "edge_like_frac", "is_weekend_frac", "min_edge_distance", "mean_edge_distance"],
        )
        pred = as_matrix(block_pred_features(unit, row_unit, row_pred))
    elif unit_type == "block_family":
        meta = encode(
            unit,
            ["target_family", "subject_id", "context_type", "block_len_bin"],
            ["block_n_rows", "edge_like_frac", "is_weekend_frac", "min_edge_distance", "mean_edge_distance"],
        )
        pred = as_matrix(block_pred_features(unit, row_unit, row_pred))
    elif unit_type == "block_total":
        meta = encode(
            unit,
            ["subject_id", "context_type", "block_len_bin"],
            ["block_n_rows", "edge_like_frac", "is_weekend_frac", "min_edge_distance", "mean_edge_distance"],
        )
        pred = as_matrix(block_pred_features(unit, row_unit, row_pred))
    else:
        raise ValueError(unit_type)

    sets: dict[str, np.ndarray] = {
        "metadata": meta,
        "prediction_geometry": np.concatenate([meta, pred], axis=1),
    }
    for view in RAW_VIEWS:
        raw_x = block_raw_features(unit, block_ids, raw, view)
        sets[f"{view}_raw"] = np.concatenate([meta, raw_x], axis=1)
        sets[f"{view}_raw_pred"] = np.concatenate([meta, raw_x, pred], axis=1)
    return sets


def markdown_table(frame: pd.DataFrame, columns: list[str], max_rows: int = 16) -> str:
    view = frame.loc[:, columns].head(max_rows).copy()
    for col in columns:
        if pd.api.types.is_numeric_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.6f}")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def run_unit(
    unit_type: str,
    unit: pd.DataFrame,
    row_unit: pd.DataFrame,
    row_pred: np.ndarray,
    block_ids: list[str],
    raw: dict[str, np.ndarray],
) -> tuple[list[EvalRow], pd.DataFrame]:
    groups = unit["hidden_block_id"].to_numpy()
    y = unit["teacher"].to_numpy(dtype=np.float64)
    feature_sets = make_feature_sets(unit_type, unit, row_unit, row_pred, block_ids, raw)
    rows: list[EvalRow] = []
    pred_frames = []
    for name, x in feature_sets.items():
        for model in ["ridge", "knn8"]:
            pred = hidden_block_ridge(x, y, groups) if model == "ridge" else hidden_block_knn(x, y, groups, k=8)
            rows.append(evaluate_prediction(unit, pred, unit_type, name, model, x.shape[1]))
            pred_frames.append(
                pd.DataFrame(
                    {
                        "unit_type": unit_type,
                        "unit_index": np.arange(len(unit)),
                        "hidden_block_id": unit["hidden_block_id"].to_numpy(),
                        "feature_set": name,
                        "model": model,
                        "teacher": y,
                        "pred": pred,
                    }
                )
            )
    return rows, pd.concat(pred_frames, ignore_index=True)


def main() -> None:
    detail_path = OUT / "e133_local_safety_colocation_atlas_cell_detail.csv"
    if not detail_path.exists():
        raise FileNotFoundError(detail_path)
    cell = pd.read_csv(detail_path)
    cell = cell.sort_values(["hidden_block_id", "sub_idx", "target"]).reset_index(drop=True)
    _, hidden_blocks, raw, _ = e134.load_raw_blocks()
    block_ids = [block.block_id for block in hidden_blocks]
    submissions = e135.load_submissions()
    row_pred = row_prediction_matrix(submissions)

    row_unit = aggregate_rows(cell)
    units = {
        "row_total": row_unit,
        "block_target": aggregate_block_target(cell),
        "block_family": aggregate_block_family(cell),
        "block_total": aggregate_block_total(cell),
    }

    eval_rows: list[EvalRow] = []
    pred_tables = []
    for unit_type, unit in units.items():
        rows, pred = run_unit(unit_type, unit, row_unit, row_pred, block_ids, raw)
        eval_rows.extend(rows)
        pred_tables.append(pred)

    summary = pd.DataFrame([row.__dict__ for row in eval_rows]).sort_values(
        ["top10_enrichment", "top10_truth_mass", "cosine"], ascending=[False, False, False]
    )
    by_unit = summary.sort_values(["unit_type", "top10_enrichment"], ascending=[True, False]).groupby("unit_type").head(5)
    predictions = pd.concat(pred_tables, ignore_index=True)

    summary_path = OUT / "e136_target_compression_visibility_summary.csv"
    pred_path = OUT / "e136_target_compression_visibility_predictions.csv"
    report_path = OUT / "e136_target_compression_visibility_report.md"
    summary.to_csv(summary_path, index=False)
    predictions.to_csv(pred_path, index=False)

    best = summary.iloc[0]
    block_target_best = summary[summary["unit_type"].eq("block_target")].iloc[0]
    row_best = summary[summary["unit_type"].eq("row_total")].iloc[0]
    cell_e134_enrichment = 0.073497 / (50.0 / 1750.0)
    cell_e135_enrichment = 0.063430 / (50.0 / 1750.0)

    lines = [
        "# E136 Target-Compression Visibility Audit\n\n",
        "## Question\n\n",
        "E133/E134/E135 tested the same cell-level safe-remainder teacher and found weak visibility. ",
        "This audit asks whether the target representation itself is too sparse: if we compress the teacher into row, block-target, block-family, or block-total states, does hidden-block-heldout visibility become materially stronger?\n\n",
        "Primary teacher remains `all_sign_co_vetonull_density`, aggregated by unit. Contexts tested: metadata, raw block views, old-prediction geometry, and raw+prediction combinations.\n\n",
        "## Decision Result\n\n",
        f"- Best compressed unit: `{best['unit_type']}` with `{best['feature_set']}` / `{best['model']}`.\n",
        f"- Best top10 truth-mass capture: `{best['top10_truth_mass']:.6f}`; enrichment over random top10: `{best['top10_enrichment']:.6f}`; capture ratio vs oracle top10: `{best['top10_capture_ratio']:.6f}`.\n",
        f"- Best block-target top10 enrichment: `{block_target_best['top10_enrichment']:.6f}` from `{block_target_best['feature_set']}` / `{block_target_best['model']}`.\n",
        f"- Best row-total top10 enrichment: `{row_best['top10_enrichment']:.6f}` from `{row_best['feature_set']}` / `{row_best['model']}`.\n",
        f"- Cell-level references: E134 raw/block top50 enrichment `{cell_e134_enrichment:.6f}`, E135 prediction-manifold top50 enrichment `{cell_e135_enrichment:.6f}`.\n\n",
        "## Top Overall Predictors\n\n",
        markdown_table(
            summary,
            [
                "unit_type",
                "feature_set",
                "model",
                "n_units",
                "n_features",
                "top10_truth_mass",
                "top10_enrichment",
                "top10_capture_ratio",
                "top20_truth_mass",
                "top20_enrichment",
                "cosine",
                "spearman",
                "top10_profile",
            ],
        ),
        "\n\n",
        "## Best By Unit Type\n\n",
        markdown_table(
            by_unit,
            [
                "unit_type",
                "feature_set",
                "model",
                "n_units",
                "top10_truth_mass",
                "top10_enrichment",
                "top10_capture_ratio",
                "top20_truth_mass",
                "top20_enrichment",
                "top10_profile",
            ],
            max_rows=24,
        ),
        "\n\n",
        "## Interpretation\n\n",
    ]
    if float(best["top10_enrichment"]) >= max(3.25, cell_e134_enrichment * 1.25):
        lines += [
            "Target compression materially improves hidden-block-heldout visibility. ",
            "This keeps a JEPA-style target redesign branch alive: the visible context may not identify individual safe cells, but it can identify a coarser hidden state where the safe mass lives. ",
            "The next experiment should test whether movement can be generated from the best compressed state without translating it back through the weak E133 cell ranking.\n",
        ]
    else:
        lines += [
            "Target compression does not materially rescue visibility beyond the cell-level E134/E135 references. ",
            "The safe remainder is not merely too sparse at cell resolution; it remains weak under row/block/target-group aggregation with current raw and prediction contexts. ",
            "This strengthens the plateau model: the current teacher may be a diagnostic artifact of local-vs-tail geometry rather than a directly learnable hidden state.\n",
        ]
    lines += [
        "\n## Outputs\n\n",
        f"- Summary: `{summary_path.name}`\n",
        f"- Predictions: `{pred_path.name}`\n",
    ]
    report_path.write_text("".join(lines), encoding="utf-8")

    print("[E136] units", {name: len(unit) for name, unit in units.items()})
    print(
        "[E136] best",
        best["unit_type"],
        best["feature_set"],
        best["model"],
        "top10_enrichment",
        f"{best['top10_enrichment']:.6f}",
    )
    print(
        "[E136] block_target_best",
        block_target_best["feature_set"],
        block_target_best["model"],
        f"{block_target_best['top10_enrichment']:.6f}",
    )
    print(
        "[E136] cell_refs",
        f"e134={cell_e134_enrichment:.6f}",
        f"e135={cell_e135_enrichment:.6f}",
    )


if __name__ == "__main__":
    main()
