#!/usr/bin/env python3
"""E134: test whether raw/block context can see E133's safe remainder field.

This is a diagnostic, not a submission generator.  E133 found that the overlap
between local E95-relative upside and public-safe veto geometry is Q3/Q1-heavy
and weakly captured by simple metadata.  Here we ask whether richer raw
overnight/block context predicts that co-located field under hidden-block
holdout.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
sys.path.insert(0, str(OUT))

import hidden_block_rate_reconstruction_audit as hbr  # noqa: E402
import raw_overnight_block_context_probe as e54  # noqa: E402

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
PRIMARY_TEACHER = "all_sign_co_vetonull_density"
TEACHERS = ["all_sign_co_vetonull_density"]
RAW_VIEWS = [
    "night_all",
    "night_phone",
    "night_watch",
    "night_context",
    "night_light",
    "night_mobility",
    "night_usage_ambience",
    "night_coverage",
]


@dataclass
class EvalRow:
    teacher: str
    feature_set: str
    model: str
    n_features: int
    js: float
    cosine: float
    pearson: float
    spearman: float
    top50_overlap: float
    truth_mass_in_pred_top50: float
    pred_mass_in_truth_top50: float
    q1q3_mass_in_pred_top50: float
    q2s3_frac_in_pred_top50: float
    target_counts_pred_top50: str


def normalize(x: np.ndarray) -> np.ndarray:
    v = np.asarray(x, dtype=np.float64).copy()
    v[~np.isfinite(v)] = 0.0
    v = np.maximum(v, 0.0)
    s = float(v.sum())
    if s <= 0.0:
        return np.full_like(v, 1.0 / len(v))
    return v / s


def minmax(x: np.ndarray) -> np.ndarray:
    v = np.asarray(x, dtype=np.float64).copy()
    v[~np.isfinite(v)] = np.nanmedian(v[np.isfinite(v)]) if np.isfinite(v).any() else 0.0
    lo = float(np.min(v))
    hi = float(np.max(v))
    if hi <= lo:
        return np.ones_like(v)
    return (v - lo) / (hi - lo)


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = normalize(p)
    q = normalize(q)
    m = 0.5 * (p + q)
    eps = 1.0e-15
    return float(
        0.5 * np.sum(p * np.log((p + eps) / (m + eps)))
        + 0.5 * np.sum(q * np.log((q + eps) / (m + eps)))
    )


def safe_corr(a: np.ndarray, b: np.ndarray, method: str) -> float:
    aa = pd.Series(np.asarray(a, dtype=np.float64))
    bb = pd.Series(np.asarray(b, dtype=np.float64))
    if aa.nunique(dropna=True) <= 1 or bb.nunique(dropna=True) <= 1:
        return 0.0
    return float(aa.corr(bb, method=method))


def top_mask(x: np.ndarray, k: int = 50) -> np.ndarray:
    k = min(k, len(x))
    idx = np.argsort(np.asarray(x, dtype=np.float64))[-k:]
    mask = np.zeros(len(x), dtype=bool)
    mask[idx] = True
    return mask


def target_count_string(df: pd.DataFrame, mask: np.ndarray) -> str:
    counts = df.loc[mask, "target"].value_counts().reindex(TARGETS, fill_value=0)
    return ",".join(f"{t}:{int(counts[t])}" for t in TARGETS if int(counts[t]) > 0)


def markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    view = df.loc[:, columns].head(max_rows).copy()
    for col in columns:
        if pd.api.types.is_numeric_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.6f}")
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(lines)


def evaluate_prediction(df: pd.DataFrame, teacher: str, pred_raw: np.ndarray, feature_set: str, model: str, n_features: int) -> EvalRow:
    truth = normalize(df[teacher].to_numpy(dtype=np.float64))
    pred = normalize(minmax(pred_raw))
    truth_top = top_mask(truth, 50)
    pred_top = top_mask(pred, 50)
    q1q3 = df["target"].isin(["Q1", "Q3"]).to_numpy()
    q2s3 = df["target"].isin(["Q2", "S3"]).to_numpy()
    return EvalRow(
        teacher=teacher,
        feature_set=feature_set,
        model=model,
        n_features=int(n_features),
        js=js_divergence(truth, pred),
        cosine=float(np.dot(truth, pred) / (np.linalg.norm(truth) * np.linalg.norm(pred) + 1.0e-15)),
        pearson=safe_corr(truth, pred, "pearson"),
        spearman=safe_corr(truth, pred, "spearman"),
        top50_overlap=float(np.mean(truth_top & pred_top) * len(truth) / 50.0),
        truth_mass_in_pred_top50=float(truth[pred_top].sum()),
        pred_mass_in_truth_top50=float(pred[truth_top].sum()),
        q1q3_mass_in_pred_top50=float(truth[pred_top & q1q3].sum()),
        q2s3_frac_in_pred_top50=float(np.mean(q2s3[pred_top])),
        target_counts_pred_top50=target_count_string(df, pred_top),
    )


def block_holdout_regression(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    model_name: str,
    random_state: int = 134,
) -> np.ndarray:
    pred = np.zeros(len(y), dtype=np.float64)
    unique_groups = pd.unique(groups)
    for g in unique_groups:
        test = groups == g
        train = ~test
        if model_name == "ridge":
            model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
        elif model_name == "extratrees":
            model = ExtraTreesRegressor(
                n_estimators=80,
                min_samples_leaf=6,
                max_features=0.75,
                random_state=random_state,
                n_jobs=1,
            )
        else:
            raise ValueError(model_name)
        model.fit(x[train], y[train])
        pred[test] = model.predict(x[test])
    return pred


def block_knn_by_target(
    block_x: np.ndarray,
    block_ids: list[str],
    df: pd.DataFrame,
    teacher: str,
    k: int = 8,
) -> np.ndarray:
    block_index = {bid: i for i, bid in enumerate(block_ids)}
    cell_block = df["hidden_block_id"].map(block_index).to_numpy(dtype=int)
    y = df[teacher].to_numpy(dtype=np.float64)
    out = np.zeros(len(df), dtype=np.float64)
    for i, row in df.iterrows():
        b = int(cell_block[i])
        target = row["target"]
        train_cells = (cell_block != b) & (df["target"].to_numpy() == target)
        train_blocks = cell_block[train_cells]
        if len(train_blocks) == 0:
            out[i] = float(np.nanmean(y))
            continue
        d = np.linalg.norm(block_x[train_blocks] - block_x[b], axis=1)
        take = np.argsort(d)[: min(k, len(d))]
        w = 1.0 / (d[take] + 1.0e-6)
        out[i] = float(np.average(y[train_cells][take], weights=w))
    return out


def encode_metadata(df: pd.DataFrame, include_submission_context: bool) -> pd.DataFrame:
    cat_cols = ["target", "subject_id", "context_type", "block_len_bin", "pos_bin", "edge_like", "is_weekend"]
    num_cols = ["block_n_rows", "edge_distance"]
    if include_submission_context:
        cat_cols += ["e72_pos_bin", "e72_abs_bin", "e101_active", "e95_moved_vs_mixmin", "e95_fallback_cell"]
        num_cols += ["e72_pos", "e72_abs_logit_delta"]
    out = pd.get_dummies(df[cat_cols].astype(str), prefix=cat_cols, dtype=float)
    for col in num_cols:
        out[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
    return out


def repeat_block_features(df: pd.DataFrame, block_ids: list[str], block_x: np.ndarray) -> np.ndarray:
    block_index = {bid: i for i, bid in enumerate(block_ids)}
    idx = df["hidden_block_id"].map(block_index)
    if idx.isna().any():
        missing = sorted(df.loc[idx.isna(), "hidden_block_id"].unique().tolist())
        raise KeyError(f"missing hidden block ids: {missing[:5]}")
    return block_x[idx.to_numpy(dtype=int)]


def make_target_onehot(df: pd.DataFrame) -> np.ndarray:
    return pd.get_dummies(df["target"], dtype=float).reindex(columns=TARGETS, fill_value=0.0).to_numpy(dtype=np.float64)


def load_raw_blocks() -> tuple[pd.DataFrame, list[hbr.Block], dict[str, np.ndarray], dict[str, dict[str, float]]]:
    train, sample = hbr.read_data()
    rows = hbr.all_rows(train, sample)
    pseudo_blocks = hbr.make_pseudo_blocks(rows)
    hidden_blocks = hbr.make_hidden_blocks(rows)
    overnight = e54.load_overnight_rows(rows)
    raw: dict[str, np.ndarray] = {}
    geom: dict[str, dict[str, float]] = {}
    for view in RAW_VIEWS:
        pack = e54.make_view_pack(view, rows, overnight, pseudo_blocks, hidden_blocks)
        raw[view] = pack.hidden_raw
        geom[view] = pack.geometry
    all_views = np.concatenate([raw[v] for v in RAW_VIEWS], axis=1)
    raw["all_raw_views"] = all_views
    geom["all_raw_views"] = {
        "view": "all_raw_views",
        "n_cols": float(sum(geom[v]["n_cols"] for v in RAW_VIEWS)),
        "row_dim": float(sum(geom[v]["row_dim"] for v in RAW_VIEWS)),
        "block_dim": float(all_views.shape[1]),
        "anisotropy": float("nan"),
        "effective_rank": float("nan"),
    }

    return rows, hidden_blocks, raw, geom


def feature_sets(df: pd.DataFrame, block_ids: list[str], raw: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    target_oh = make_target_onehot(df)
    visible_meta = encode_metadata(df, include_submission_context=False).to_numpy(dtype=np.float64)
    sub_meta = encode_metadata(df, include_submission_context=True).to_numpy(dtype=np.float64)
    sets: dict[str, np.ndarray] = {
        "target_only": target_oh,
        "visible_metadata": visible_meta,
        "submission_metadata": sub_meta,
    }
    for view, block_x in raw.items():
        cell_x = repeat_block_features(df, block_ids, block_x)
        sets[f"{view}_target"] = np.concatenate([cell_x, target_oh], axis=1)
        sets[f"{view}_visible_meta"] = np.concatenate([cell_x, visible_meta], axis=1)
        if view in {"night_all", "night_phone", "all_raw_views"}:
            sets[f"{view}_submission_meta"] = np.concatenate([cell_x, sub_meta], axis=1)
    return sets


def main() -> None:
    detail_path = OUT / "e133_local_safety_colocation_atlas_cell_detail.csv"
    if not detail_path.exists():
        raise FileNotFoundError(detail_path)
    df = pd.read_csv(detail_path)
    df = df.sort_values(["hidden_block_id", "cell_idx", "target"]).reset_index(drop=True)
    rows, hidden_blocks, raw, geom = load_raw_blocks()
    block_ids = [b.block_id for b in hidden_blocks]
    features = feature_sets(df, block_ids, raw)
    groups = df["hidden_block_id"].to_numpy()

    eval_rows: list[EvalRow] = []
    prediction_frames = []
    for teacher in TEACHERS:
        y = df[teacher].to_numpy(dtype=np.float64)
        for name, x in features.items():
            models = ["ridge"]
            if name in {
                "target_only",
                "visible_metadata",
                "submission_metadata",
                "night_all_visible_meta",
                "night_phone_visible_meta",
                "all_raw_views_visible_meta",
            }:
                models.append("extratrees")
            for model in models:
                pred = block_holdout_regression(x, y, groups, model)
                eval_rows.append(evaluate_prediction(df, teacher, pred, name, model, x.shape[1]))
                if teacher == PRIMARY_TEACHER:
                    prediction_frames.append(
                        pd.DataFrame(
                            {
                                "cell_idx": df["cell_idx"],
                                "hidden_block_id": df["hidden_block_id"],
                                "target": df["target"],
                                "teacher": y,
                                "feature_set": name,
                                "model": model,
                                "pred": pred,
                            }
                        )
                    )

        for view, block_x in raw.items():
            pred = block_knn_by_target(block_x, block_ids, df, teacher, k=8)
            eval_rows.append(evaluate_prediction(df, teacher, pred, f"{view}_blockknn", "target_knn8", block_x.shape[1]))
            if teacher == PRIMARY_TEACHER:
                prediction_frames.append(
                    pd.DataFrame(
                        {
                            "cell_idx": df["cell_idx"],
                            "hidden_block_id": df["hidden_block_id"],
                            "target": df["target"],
                            "teacher": y,
                            "feature_set": f"{view}_blockknn",
                            "model": "target_knn8",
                            "pred": pred,
                        }
                    )
                )

    summary = pd.DataFrame([r.__dict__ for r in eval_rows]).sort_values(
        ["teacher", "truth_mass_in_pred_top50", "cosine"], ascending=[True, False, False]
    )
    primary = summary[summary["teacher"].eq(PRIMARY_TEACHER)].copy()
    best = primary.iloc[0]
    geom_df = pd.DataFrame([{"view": view, **values} for view, values in geom.items()])

    summary_path = OUT / "e134_raw_block_colocation_predictability_summary.csv"
    geom_path = OUT / "e134_raw_block_colocation_predictability_geometry_summary.csv"
    pred_path = OUT / "e134_raw_block_colocation_predictability_primary_predictions.csv"
    report_path = OUT / "e134_raw_block_colocation_predictability_report.md"
    summary.to_csv(summary_path, index=False)
    geom_df.to_csv(geom_path, index=False)
    pd.concat(prediction_frames, ignore_index=True).to_csv(pred_path, index=False)

    metadata_benchmark = primary[primary["feature_set"].isin(["target_only", "visible_metadata", "submission_metadata"])]
    metadata_best = metadata_benchmark.iloc[0]
    raw_best = primary[
        ~primary["feature_set"].isin(["target_only", "visible_metadata", "submission_metadata"])
    ].iloc[0]
    top_primary = primary.head(15)

    lines = [
        "# E134 Raw/Block Co-location Predictability\n\n",
        "## Question\n\n",
        "E133 found that the useful post-E95 remainder is a small Q3/Q1-heavy overlap between local upside and veto-null/public-safe density. ",
        "This experiment asks whether that field is visible from raw overnight/block context under hidden-block holdout, or whether it is mostly a submission-geometry artifact.\n\n",
        "Primary teacher: `all_sign_co_vetonull_density` from `e133_local_safety_colocation_atlas_cell_detail.csv`.\n\n",
        "## Decision Result\n\n",
        f"- Best overall primary predictor: `{best['feature_set']}` / `{best['model']}`.\n",
        f"- Best primary truth mass in predicted top50: `{best['truth_mass_in_pred_top50']:.6f}`; cosine `{best['cosine']:.6f}`; JS `{best['js']:.6f}`.\n",
        f"- Best metadata-only truth mass in predicted top50: `{metadata_best['truth_mass_in_pred_top50']:.6f}` from `{metadata_best['feature_set']}` / `{metadata_best['model']}`.\n",
        f"- Best raw/block truth mass in predicted top50: `{raw_best['truth_mass_in_pred_top50']:.6f}` from `{raw_best['feature_set']}` / `{raw_best['model']}`.\n",
        f"- Best predicted top50 target counts: `{best['target_counts_pred_top50']}`; Q2/S3 fraction `{best['q2s3_frac_in_pred_top50']:.6f}`; Q1/Q3 truth mass `{best['q1q3_mass_in_pred_top50']:.6f}`.\n\n",
        "E133 metadata benchmark to beat was top50 truth-mass capture `0.048280` for the all-sign co-located field. ",
        "A useful raw/block representation should clear that by a material margin and keep the Q2/S3 tail suppressed.\n\n",
        "## Top Primary Predictors\n\n",
        markdown_table(
            top_primary,
            [
                "feature_set",
                "model",
                "n_features",
                "truth_mass_in_pred_top50",
                "cosine",
                "spearman",
                "js",
                "top50_overlap",
                "q1q3_mass_in_pred_top50",
                "q2s3_frac_in_pred_top50",
                "target_counts_pred_top50",
            ],
        ),
        "\n\n",
        "## Interpretation\n\n",
    ]
    if float(raw_best["truth_mass_in_pred_top50"]) >= max(0.15, float(metadata_best["truth_mass_in_pred_top50"]) * 1.5):
        lines += [
            "Raw/block context materially predicts the E133 safe-remainder teacher. ",
            "This keeps the JEPA-style context-to-hidden-remainder hypothesis alive: raw block context can be used as a target-free representation for Q3/Q1-safe movement, but it still needs a movement direction and calibration stress before any submission.\n",
        ]
    else:
        lines += [
            "Raw/block context does not materially beat the metadata visibility bar. ",
            "The E133 safe-remainder field is therefore not obviously present in observed raw overnight/block geometry. ",
            "This strengthens the plateau explanation: the local-upside direction and public-safe tail geometry overlap in probability/submission space, but the overlap is weakly visible from current raw/block context.\n",
        ]
    lines += [
        "\n## Outputs\n\n",
        f"- Summary: `{summary_path.name}`\n",
        f"- Geometry summary: `{geom_path.name}`\n",
        f"- Primary predictions: `{pred_path.name}`\n",
    ]
    report_path.write_text("".join(lines), encoding="utf-8")

    print("[E134] rows", len(df), "hidden_blocks", len(block_ids), "raw_views", len(raw))
    print("[E134] best", best["feature_set"], best["model"], "mass", f"{best['truth_mass_in_pred_top50']:.6f}")
    print("[E134] metadata_best", metadata_best["feature_set"], metadata_best["model"], f"{metadata_best['truth_mass_in_pred_top50']:.6f}")
    print("[E134] raw_best", raw_best["feature_set"], raw_best["model"], f"{raw_best['truth_mass_in_pred_top50']:.6f}")


if __name__ == "__main__":
    main()
