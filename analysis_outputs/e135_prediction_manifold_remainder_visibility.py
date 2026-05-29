#!/usr/bin/env python3
"""E135: can existing prediction-manifold geometry see the safe remainder?

E134 showed raw overnight/block context only weakly predicts E133's
Q3/Q1-heavy safe-remainder field.  This audit asks a different question:
is the same field visible in the disagreement geometry of the important
existing submissions, or is it weak even in prediction space?
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
PRIMARY_TEACHER = "all_sign_co_vetonull_density"

SUBMISSIONS = {
    "e95": OUT / "submission_e95_hardtail_541e3973.csv",
    "mixmin": OUT / "submission_mixmin_0c916bb4.csv",
    "e101": OUT / "submission_e101_q2s3tail_177569bc.csv",
    "e72": OUT / "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
    "e85": OUT / "submission_e85_inverse_conflict_pruned_58b23ed1.csv",
    "e86": OUT / "submission_e86_e85_consensus_a3f7c96f.csv",
    "e89": OUT / "submission_e89_e72decontam_00d7807f.csv",
    "e90": OUT / "submission_e90_e72pareto_28925de5.csv",
    "a2c8": OUT / "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "stage2": OUT / "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
    "final9": OUT / "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "ordinal": OUT / "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
}


@dataclass
class EvalRow:
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


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(p, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


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
    if not np.isfinite(v).all():
        finite = v[np.isfinite(v)]
        v[~np.isfinite(v)] = float(np.nanmedian(finite)) if len(finite) else 0.0
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


def evaluate_prediction(df: pd.DataFrame, pred_raw: np.ndarray, feature_set: str, model: str, n_features: int) -> EvalRow:
    truth = normalize(df[PRIMARY_TEACHER].to_numpy(dtype=np.float64))
    pred = normalize(minmax(pred_raw))
    truth_top = top_mask(truth, 50)
    pred_top = top_mask(pred, 50)
    q1q3 = df["target"].isin(["Q1", "Q3"]).to_numpy()
    q2s3 = df["target"].isin(["Q2", "S3"]).to_numpy()
    return EvalRow(
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


def hidden_block_cv_predict(x: np.ndarray, y: np.ndarray, groups: np.ndarray, model_name: str) -> np.ndarray:
    pred = np.zeros(len(y), dtype=np.float64)
    for group in pd.unique(groups):
        test = groups == group
        train = ~test
        if model_name == "ridge":
            model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
        elif model_name == "extratrees":
            model = ExtraTreesRegressor(
                n_estimators=120,
                min_samples_leaf=5,
                max_features=0.75,
                random_state=135,
                n_jobs=1,
            )
        else:
            raise ValueError(model_name)
        model.fit(x[train], y[train])
        pred[test] = model.predict(x[test])
    return pred


def encode_metadata(df: pd.DataFrame, include_submission_context: bool) -> np.ndarray:
    cat_cols = ["target", "subject_id", "context_type", "block_len_bin", "pos_bin", "edge_like", "is_weekend"]
    num_cols = ["block_n_rows", "edge_distance"]
    if include_submission_context:
        cat_cols += ["e72_pos_bin", "e72_abs_bin", "e101_active", "e95_moved_vs_mixmin", "e95_fallback_cell"]
        num_cols += ["e72_pos", "e72_abs_logit_delta"]
    out = pd.get_dummies(df[cat_cols].astype(str), prefix=cat_cols, dtype=float)
    for col in num_cols:
        out[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
    return out.to_numpy(dtype=np.float64)


def load_submissions() -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    missing = [name for name, path in SUBMISSIONS.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing submissions: {missing}")
    for name, path in SUBMISSIONS.items():
        frame = pd.read_csv(path)
        out[name] = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    n = {arr.shape[0] for arr in out.values()}
    if len(n) != 1:
        raise ValueError(f"inconsistent submission row counts: {n}")
    return out


def repeat_row_features(df: pd.DataFrame, row_x: np.ndarray) -> np.ndarray:
    idx = df["sub_idx"].to_numpy(dtype=int)
    return row_x[idx]


def cell_values(df: pd.DataFrame, arr: np.ndarray) -> np.ndarray:
    row_idx = df["sub_idx"].to_numpy(dtype=int)
    target_idx = df["target"].map({t: i for i, t in enumerate(TARGETS)}).to_numpy(dtype=int)
    return arr[row_idx, target_idx]


def target_onehot(df: pd.DataFrame) -> np.ndarray:
    return pd.get_dummies(df["target"], dtype=float).reindex(columns=TARGETS, fill_value=0.0).to_numpy(dtype=np.float64)


def make_features(df: pd.DataFrame, submissions: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    target_oh = target_onehot(df)
    visible_meta = encode_metadata(df, include_submission_context=False)
    submission_meta = encode_metadata(df, include_submission_context=True)
    e95 = submissions["e95"]
    mixmin = submissions["mixmin"]

    row_prob = np.concatenate([submissions[name] for name in SUBMISSIONS], axis=1)
    row_logit = np.concatenate([logit(submissions[name]) for name in SUBMISSIONS], axis=1)
    row_delta_e95 = np.concatenate([logit(submissions[name]) - logit(e95) for name in SUBMISSIONS if name != "e95"], axis=1)
    row_delta_mixmin = np.concatenate([logit(submissions[name]) - logit(mixmin) for name in SUBMISSIONS if name != "mixmin"], axis=1)
    row_all = np.concatenate([row_prob, row_logit, row_delta_e95, row_delta_mixmin], axis=1)

    row_pca = make_pipeline(StandardScaler(), PCA(n_components=12, random_state=135)).fit_transform(row_all)
    cell_scalar_cols = []
    for name, arr in submissions.items():
        cell_scalar_cols.append(cell_values(df, arr)[:, None])
        cell_scalar_cols.append(logit(cell_values(df, arr))[:, None])
        cell_scalar_cols.append((logit(cell_values(df, arr)) - logit(cell_values(df, e95)))[:, None])
        cell_scalar_cols.append((logit(cell_values(df, arr)) - logit(cell_values(df, mixmin)))[:, None])
    cell_scalar = np.concatenate(cell_scalar_cols, axis=1)

    # Row disagreement/uncertainty is target-free context repeated to each cell.
    stack = np.stack([submissions[name] for name in SUBMISSIONS], axis=0)
    row_mean = stack.mean(axis=0)
    row_std = stack.std(axis=0)
    row_range = stack.max(axis=0) - stack.min(axis=0)
    row_unc = np.concatenate([row_mean, row_std, row_range], axis=1)

    return {
        "target_only": target_oh,
        "visible_metadata": visible_meta,
        "submission_metadata": submission_meta,
        "cell_prediction_scalars": np.concatenate([cell_scalar, target_oh], axis=1),
        "cell_prediction_scalars_meta": np.concatenate([cell_scalar, submission_meta], axis=1),
        "row_prediction_pca_target": np.concatenate([repeat_row_features(df, row_pca), target_oh], axis=1),
        "row_prediction_pca_meta": np.concatenate([repeat_row_features(df, row_pca), submission_meta], axis=1),
        "row_prediction_full_target": np.concatenate([repeat_row_features(df, row_all), target_oh], axis=1),
        "row_uncertainty_target": np.concatenate([repeat_row_features(df, row_unc), target_oh], axis=1),
        "prediction_manifold_full": np.concatenate(
            [cell_scalar, repeat_row_features(df, row_pca), repeat_row_features(df, row_unc), submission_meta],
            axis=1,
        ),
    }


def main() -> None:
    detail_path = OUT / "e133_local_safety_colocation_atlas_cell_detail.csv"
    df = pd.read_csv(detail_path).sort_values(["hidden_block_id", "cell_idx", "target"]).reset_index(drop=True)
    submissions = load_submissions()
    features = make_features(df, submissions)
    y = df[PRIMARY_TEACHER].to_numpy(dtype=np.float64)
    groups = df["hidden_block_id"].to_numpy()

    rows: list[EvalRow] = []
    pred_frames = []
    for name, x in features.items():
        models = ["ridge"]
        if name in {
            "target_only",
            "visible_metadata",
            "submission_metadata",
            "cell_prediction_scalars_meta",
            "row_prediction_pca_meta",
            "prediction_manifold_full",
        }:
            models.append("extratrees")
        for model in models:
            pred = hidden_block_cv_predict(x, y, groups, model)
            rows.append(evaluate_prediction(df, pred, name, model, x.shape[1]))
            pred_frames.append(
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

    summary = pd.DataFrame([r.__dict__ for r in rows]).sort_values(
        ["truth_mass_in_pred_top50", "cosine"], ascending=[False, False]
    )
    best = summary.iloc[0]
    metadata_best = summary[summary["feature_set"].isin(["target_only", "visible_metadata", "submission_metadata"])].iloc[0]
    manifold_best = summary[~summary["feature_set"].isin(["target_only", "visible_metadata", "submission_metadata"])].iloc[0]

    summary_path = OUT / "e135_prediction_manifold_remainder_visibility_summary.csv"
    pred_path = OUT / "e135_prediction_manifold_remainder_visibility_predictions.csv"
    report_path = OUT / "e135_prediction_manifold_remainder_visibility_report.md"
    summary.to_csv(summary_path, index=False)
    pd.concat(pred_frames, ignore_index=True).to_csv(pred_path, index=False)

    top = summary.head(15)
    lines = [
        "# E135 Prediction-Manifold Remainder Visibility\n\n",
        "## Question\n\n",
        "E134 says raw/block context only weakly sees E133's safe remainder. ",
        "This audit asks whether the disagreement geometry of the main existing submissions sees it better under hidden-block holdout.\n\n",
        "Primary teacher: `all_sign_co_vetonull_density`.\n\n",
        "## Decision Result\n\n",
        f"- Best predictor: `{best['feature_set']}` / `{best['model']}`.\n",
        f"- Best top50 truth-mass capture: `{best['truth_mass_in_pred_top50']:.6f}`; cosine `{best['cosine']:.6f}`; JS `{best['js']:.6f}`.\n",
        f"- Metadata-only best top50 truth-mass capture: `{metadata_best['truth_mass_in_pred_top50']:.6f}` from `{metadata_best['feature_set']}` / `{metadata_best['model']}`.\n",
        f"- Prediction-manifold best top50 truth-mass capture: `{manifold_best['truth_mass_in_pred_top50']:.6f}` from `{manifold_best['feature_set']}` / `{manifold_best['model']}`.\n",
        f"- Best predicted top50 target counts: `{best['target_counts_pred_top50']}`; Q2/S3 fraction `{best['q2s3_frac_in_pred_top50']:.6f}`; Q1/Q3 truth mass `{best['q1q3_mass_in_pred_top50']:.6f}`.\n\n",
        "Reference bars: E133 metadata `0.048280`, E134 metadata `0.063040`, E134 raw/block `0.073497`. ",
        "A useful prediction-manifold target should clear raw/block by a material margin and not revive Q2/S3.\n\n",
        "## Top Predictors\n\n",
        markdown_table(
            top,
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
    if float(manifold_best["truth_mass_in_pred_top50"]) >= max(0.12, 1.5 * 0.073497):
        lines += [
            "The prediction manifold materially improves over raw/block visibility. ",
            "This keeps a non-raw JEPA-style target alive: existing submission disagreement may encode the safe remainder even when observed raw context barely does. ",
            "It is still not a submission by itself; the next test must convert this visibility into a movement that survives E128/E129/E124 stress.\n",
        ]
    else:
        lines += [
            "The prediction manifold does not materially improve over E134 raw/block visibility. ",
            "This closes the cheap old-submission-disagreement path: the E133 safe remainder is weak in raw context and weak in the existing prediction manifold. ",
            "The next useful representation must change the target itself or use a new source of supervision, not just rerank old submission disagreement.\n",
        ]
    lines += [
        "\n## Outputs\n\n",
        f"- Summary: `{summary_path.name}`\n",
        f"- Predictions: `{pred_path.name}`\n",
    ]
    report_path.write_text("".join(lines), encoding="utf-8")

    print("[E135] cells", len(df), "hidden_blocks", len(pd.unique(groups)), "submissions", len(submissions))
    print("[E135] best", best["feature_set"], best["model"], f"{best['truth_mass_in_pred_top50']:.6f}")
    print("[E135] metadata_best", metadata_best["feature_set"], metadata_best["model"], f"{metadata_best['truth_mass_in_pred_top50']:.6f}")
    print("[E135] manifold_best", manifold_best["feature_set"], manifold_best["model"], f"{manifold_best['truth_mass_in_pred_top50']:.6f}")


if __name__ == "__main__":
    main()
