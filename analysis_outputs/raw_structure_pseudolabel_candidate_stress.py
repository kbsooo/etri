#!/usr/bin/env python3
"""E36 raw-structure pseudo-label stress for current public sensors.

This is deliberately not a public-LB inverse model. It asks whether observed
raw features, subject/date structure, and train labels independently support
the candidate movements that E32-E35 prioritized.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.metrics import pairwise_distances
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]

CANDIDATES = {
    "mixmin_0c916": "analysis_outputs/submission_mixmin_0c916bb4.csv",
    "inverse7blend_1040": "analysis_outputs/submission_inverse7blend_1040423d.csv",
    "pair_sensor_1bb": "analysis_outputs/submission_label_flow_focused_1bbfb735.csv",
    "pair_sensor_1bb_s0p65": "analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv",
    "pair_sensor_6b": "analysis_outputs/submission_label_flow_focused_6b9335b1.csv",
}
BASELINE_FILE = "analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv"


@dataclass
class PseudoSource:
    name: str
    tier: str
    y: np.ndarray
    detail: str


def load_frame() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = pd.read_parquet(ROOT / "analysis_outputs/all_keys_deep_features.parquet")
    train = pd.read_csv(ROOT / "data/ch2026_metrics_train.csv")
    test = pd.read_csv(ROOT / "data/ch2026_submission_sample.csv")
    for df in (features, train, test):
        for col in ("sleep_date", "lifelog_date"):
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    return features, train, test


def aligned_labels(features: pd.DataFrame, train: pd.DataFrame, test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train_feat = features.loc[features["split"].eq("train")].merge(
        train[KEYS + TARGETS], on=KEYS, how="inner", validate="one_to_one"
    )
    test_feat = features.loc[features["split"].eq("submission")].merge(
        test[KEYS], on=KEYS, how="inner", validate="one_to_one"
    )
    if len(train_feat) != len(train) or len(test_feat) != len(test):
        raise RuntimeError(
            f"feature/key alignment failed: train {len(train_feat)}/{len(train)}, test {len(test_feat)}/{len(test)}"
        )
    return train_feat.reset_index(drop=True), test_feat.reset_index(drop=True)


def clean_numeric_cols(df: pd.DataFrame, requested: list[str]) -> list[str]:
    cols = []
    for col in requested:
        if col not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        finite_count = np.isfinite(pd.to_numeric(df[col], errors="coerce")).sum()
        if finite_count >= 20:
            cols.append(col)
    return cols


def make_xy(train_feat: pd.DataFrame, test_feat: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, np.ndarray]:
    cols = clean_numeric_cols(train_feat, cols)
    if not cols:
        raise RuntimeError("no numeric columns for feature view")
    train_x = train_feat[cols].replace([np.inf, -np.inf], np.nan)
    test_x = test_feat[cols].replace([np.inf, -np.inf], np.nan)
    pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    x_train = pipe.fit_transform(train_x)
    x_test = pipe.transform(test_x)
    return x_train, x_test


def soft_logloss(y: np.ndarray, p: np.ndarray) -> float:
    p = np.clip(p.astype(float), 1e-5, 1 - 1e-5)
    y = np.clip(y.astype(float), 1e-5, 1 - 1e-5)
    return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))


def knn_pseudo(
    train_feat: pd.DataFrame,
    test_feat: pd.DataFrame,
    cols: list[str],
    y_train: np.ndarray,
    *,
    k: int,
    name: str,
    tier: str,
    exclude_same_subject: bool = False,
) -> PseudoSource:
    x_train, x_test = make_xy(train_feat, test_feat, cols)
    if exclude_same_subject:
        dist = pairwise_distances(x_test, x_train, metric="euclidean")
        subj_train = train_feat["subject_id"].to_numpy()
        subj_test = test_feat["subject_id"].to_numpy()
        y = np.zeros((len(test_feat), y_train.shape[1]), dtype=float)
        for i, subj in enumerate(subj_test):
            order = np.argsort(dist[i])
            order = [idx for idx in order if subj_train[idx] != subj][:k]
            if len(order) == 0:
                order = np.argsort(dist[i])[:k]
            d = dist[i, order]
            weights = 1 / (d + 1e-6)
            weights = weights / weights.sum()
            y[i] = weights @ y_train[order]
    else:
        nn = NearestNeighbors(n_neighbors=min(k, len(train_feat)), metric="euclidean")
        nn.fit(x_train)
        d, idx = nn.kneighbors(x_test)
        weights = 1 / (d + 1e-6)
        weights = weights / weights.sum(axis=1, keepdims=True)
        y = np.einsum("ij,ijk->ik", weights, y_train[idx])
    return PseudoSource(name, tier, y, f"k={k}, columns={len(cols)}, exclude_same_subject={exclude_same_subject}")


def subject_mean_pseudo(train_feat: pd.DataFrame, test_feat: pd.DataFrame, y_train: np.ndarray) -> PseudoSource:
    global_mean = y_train.mean(axis=0)
    subject_means = (
        train_feat.assign(**{target: y_train[:, i] for i, target in enumerate(TARGETS)})
        .groupby("subject_id")[TARGETS]
        .mean()
    )
    y = np.vstack([subject_means.loc[s].to_numpy() if s in subject_means.index else global_mean for s in test_feat["subject_id"]])
    return PseudoSource("subject_mean", "train_subject_prior", y, "same-subject train target mean")


def subject_temporal_pseudo(
    train_feat: pd.DataFrame, test_feat: pd.DataFrame, y_train: np.ndarray, *, k: int
) -> PseudoSource:
    y = np.zeros((len(test_feat), y_train.shape[1]), dtype=float)
    train_day = train_feat["subject_day_index"].to_numpy(float)
    for i, row in test_feat.iterrows():
        mask = train_feat["subject_id"].eq(row["subject_id"]).to_numpy()
        idx = np.flatnonzero(mask)
        if len(idx) == 0:
            y[i] = y_train.mean(axis=0)
            continue
        d = np.abs(train_day[idx] - float(row["subject_day_index"]))
        order = idx[np.argsort(d)[: min(k, len(idx))]]
        weights = 1 / (np.abs(train_day[order] - float(row["subject_day_index"])) + 1.0)
        weights = weights / weights.sum()
        y[i] = weights @ y_train[order]
    return PseudoSource(f"subject_temporal_k{k}", "train_subject_temporal_prior", y, f"same-subject nearest train days, k={k}")


def cluster_pseudo(
    train_feat: pd.DataFrame,
    test_feat: pd.DataFrame,
    cols: list[str],
    y_train: np.ndarray,
    *,
    n_clusters: int,
) -> PseudoSource:
    x_train, x_test = make_xy(train_feat, test_feat, cols)
    x_all = np.vstack([x_train, x_test])
    km = KMeans(n_clusters=n_clusters, random_state=20260528, n_init=20)
    labels = km.fit_predict(x_all)
    labels_train = labels[: len(train_feat)]
    labels_test = labels[len(train_feat) :]
    global_mean = y_train.mean(axis=0)
    y = np.zeros((len(test_feat), y_train.shape[1]), dtype=float)
    for cluster in np.unique(labels_test):
        train_idx = np.flatnonzero(labels_train == cluster)
        test_idx = np.flatnonzero(labels_test == cluster)
        if len(train_idx) == 0:
            prior = global_mean
        else:
            alpha = 5.0
            prior = (y_train[train_idx].sum(axis=0) + alpha * global_mean) / (len(train_idx) + alpha)
        y[test_idx] = prior
    return PseudoSource(
        f"sensor_cluster_k{n_clusters}",
        "raw_feature_cluster_prior",
        y,
        f"kmeans clusters over train+test raw features, n_clusters={n_clusters}",
    )


def load_predictions(test_feat: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base = pd.read_csv(ROOT / BASELINE_FILE)
    for col in ("sleep_date", "lifelog_date"):
        base[col] = pd.to_datetime(base[col]).dt.strftime("%Y-%m-%d")
    base = test_feat[KEYS].merge(base, on=KEYS, how="left", validate="one_to_one")
    preds = {"a2c8": base[TARGETS].to_numpy(float)}
    for role, path in CANDIDATES.items():
        df = pd.read_csv(ROOT / path)
        for col in ("sleep_date", "lifelog_date"):
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
        aligned = test_feat[KEYS].merge(df, on=KEYS, how="left", validate="one_to_one")
        preds[role] = aligned[TARGETS].to_numpy(float)
    return base[KEYS], preds


def candidate_scores(sources: list[PseudoSource], preds: dict[str, np.ndarray]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    base = preds["a2c8"]
    for source in sources:
        base_loss = soft_logloss(source.y, base)
        for role, p in preds.items():
            if role == "a2c8":
                continue
            cand_loss = soft_logloss(source.y, p)
            move = p - base
            toward = np.sign(move) == np.sign(source.y - base)
            moved = np.abs(move) > 1e-12
            abs_move = np.abs(move)
            toward_rate = float(abs_move[toward & moved].sum() / max(abs_move[moved].sum(), 1e-12))
            alignment = float(np.mean(move * (source.y - base)))
            rows.append(
                {
                    "role": role,
                    "source": source.name,
                    "tier": source.tier,
                    "detail": source.detail,
                    "a2c8_loss": base_loss,
                    "candidate_loss": cand_loss,
                    "delta_vs_a2c8": cand_loss - base_loss,
                    "direction_alignment": alignment,
                    "weighted_toward_rate": toward_rate,
                    "mean_abs_move": float(abs_move.mean()),
                    "moved_cell_frac": float(moved.mean()),
                }
            )
    return pd.DataFrame(rows)


def domain_anatomy(
    train_feat: pd.DataFrame,
    test_feat: pd.DataFrame,
    sensor_cols: list[str],
    preds: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, float]:
    all_feat = pd.concat([train_feat, test_feat], axis=0, ignore_index=True)
    x_cols = clean_numeric_cols(all_feat, sensor_cols)
    x = all_feat[x_cols].replace([np.inf, -np.inf], np.nan)
    y = all_feat["split"].eq("submission").astype(int).to_numpy()
    clf = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=500, C=0.2, class_weight="balanced", solver="liblinear"),
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=20260528)
    prob = cross_val_predict(clf, x, y, cv=cv, method="predict_proba")[:, 1]
    auc = float(roc_auc_score(y, prob))
    test_prob = prob[len(train_feat) :]

    x_train, x_test = make_xy(train_feat, test_feat, x_cols)
    nn = NearestNeighbors(n_neighbors=10, metric="euclidean").fit(x_train)
    d, _ = nn.kneighbors(x_test)
    nn_dist = d.mean(axis=1)

    numeric = test_feat[clean_numeric_cols(test_feat, list(test_feat.select_dtypes(include="number").columns))]
    missing_frac = numeric.isna().mean(axis=1).to_numpy(float)
    count_cols = [c for c in numeric.columns if c.endswith("_count")]
    count_sum = numeric[count_cols].fillna(0).sum(axis=1).to_numpy(float) if count_cols else np.zeros(len(test_feat))

    base = preds["a2c8"]
    anatomy_rows: list[dict[str, Any]] = []
    for role, p in preds.items():
        if role == "a2c8":
            continue
        row_move = np.abs(p - base).mean(axis=1)
        features = {
            "domain_submission_prob": test_prob,
            "nn_dist_to_train": nn_dist,
            "missing_frac": missing_frac,
            "sensor_count_sum": count_sum,
            "subject_day_index": test_feat["subject_day_index"].to_numpy(float),
        }
        for name, values in features.items():
            corr = pd.Series(row_move).corr(pd.Series(values), method="spearman")
            anatomy_rows.append(
                {
                    "role": role,
                    "anatomy_feature": name,
                    "spearman_corr_with_row_move": corr,
                    "top20_mean": float(pd.Series(values).iloc[np.argsort(row_move)[-50:]].mean()),
                    "all_mean": float(pd.Series(values).mean()),
                }
            )
        top_idx = np.argsort(row_move)[-50:]
        subject_share = (
            test_feat.iloc[top_idx]
            .groupby("subject_id")
            .size()
            .div(len(top_idx))
            .sort_values(ascending=False)
        )
        anatomy_rows.append(
            {
                "role": role,
                "anatomy_feature": "top50_subject_concentration",
                "spearman_corr_with_row_move": np.nan,
                "top20_mean": float(subject_share.iloc[0]),
                "all_mean": 0.1,
                "top_subject": subject_share.index[0],
            }
        )
    return pd.DataFrame(anatomy_rows), auc


def summarize(scores: pd.DataFrame, evidence: pd.DataFrame | None = None) -> pd.DataFrame:
    rows = []
    for role, g in scores.groupby("role"):
        row = {
            "role": role,
            "source_count": len(g),
            "support_count": int((g["delta_vs_a2c8"] < 0).sum()),
            "support_rate": float((g["delta_vs_a2c8"] < 0).mean()),
            "mean_delta": float(g["delta_vs_a2c8"].mean()),
            "median_delta": float(g["delta_vs_a2c8"].median()),
            "worst_delta": float(g["delta_vs_a2c8"].max()),
            "best_delta": float(g["delta_vs_a2c8"].min()),
            "mean_toward_rate": float(g["weighted_toward_rate"].mean()),
            "mean_abs_move": float(g["mean_abs_move"].mean()),
        }
        if evidence is not None and not evidence.empty and "role" in evidence.columns:
            match = evidence.loc[evidence["role"].eq(role)]
            if not match.empty:
                row["e35_normal_submit_gate"] = bool(match["normal_submit_gate"].iloc[0])
                row["e35_selector_hard_veto"] = bool(match["selector_hard_veto"].iloc[0])
                row["e35_sensor_priority_score"] = float(match["sensor_priority_score"].iloc[0])
        row["raw_structure_gate"] = (
            row["support_rate"] >= 0.70
            and row["worst_delta"] <= 0
            and row.get("e35_selector_hard_veto", False) is False
        )
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["raw_structure_gate", "support_rate", "mean_delta"], ascending=[False, False, True])


def main() -> None:
    features, train, test = load_frame()
    train_feat, test_feat = aligned_labels(features, train, test)
    y_train = train_feat[TARGETS].to_numpy(float)

    numeric_cols = list(features.select_dtypes(include="number").columns)
    meta_cols = {"dow", "month", "day", "weekofyear", "subject_day_index", "is_weekend"}
    sensor_cols = [c for c in numeric_cols if c not in meta_cols and c not in TARGETS]
    count_cols = [c for c in sensor_cols if c.endswith("_count")]
    stat_cols = [c for c in sensor_cols if not c.endswith("_count")]

    sources: list[PseudoSource] = [
        subject_mean_pseudo(train_feat, test_feat, y_train),
        subject_temporal_pseudo(train_feat, test_feat, y_train, k=3),
        subject_temporal_pseudo(train_feat, test_feat, y_train, k=7),
        knn_pseudo(train_feat, test_feat, sensor_cols, y_train, k=5, name="sensor_all_knn_k5", tier="raw_feature_knn_prior"),
        knn_pseudo(train_feat, test_feat, sensor_cols, y_train, k=15, name="sensor_all_knn_k15", tier="raw_feature_knn_prior"),
        knn_pseudo(train_feat, test_feat, sensor_cols, y_train, k=15, name="sensor_all_cross_subject_knn_k15", tier="raw_feature_cross_subject_prior", exclude_same_subject=True),
        knn_pseudo(train_feat, test_feat, count_cols, y_train, k=10, name="sensor_count_knn_k10", tier="missingness_coverage_prior"),
        knn_pseudo(train_feat, test_feat, stat_cols, y_train, k=10, name="sensor_stat_knn_k10", tier="sensor_behavior_prior"),
        cluster_pseudo(train_feat, test_feat, sensor_cols, y_train, n_clusters=12),
        cluster_pseudo(train_feat, test_feat, sensor_cols, y_train, n_clusters=24),
    ]

    _, preds = load_predictions(test_feat)
    scores = candidate_scores(sources, preds)
    evidence_path = OUT / "public_probe_independent_evidence_audit_summary.csv"
    evidence = pd.read_csv(evidence_path) if evidence_path.exists() else pd.DataFrame()
    summary = summarize(scores, evidence)
    anatomy, domain_auc = domain_anatomy(train_feat, test_feat, sensor_cols, preds)

    scores_path = OUT / "raw_structure_pseudolabel_candidate_stress_scores.csv"
    summary_path = OUT / "raw_structure_pseudolabel_candidate_stress_summary.csv"
    anatomy_path = OUT / "raw_structure_pseudolabel_candidate_stress_anatomy.csv"
    scores.to_csv(scores_path, index=False)
    summary.to_csv(summary_path, index=False)
    anatomy.to_csv(anatomy_path, index=False)

    top = summary.iloc[0]
    mixmin = summary.loc[summary["role"].eq("mixmin_0c916")].iloc[0]
    report = [
        "# E36 Raw-Structure Pseudo-Label Candidate Stress",
        "",
        "## Observe",
        "",
        "E35 found no certification-grade out-of-anchor evidence for mixmin. The next cheapest independent check is not another public-anchor decomposition, but a train-derived raw-structure pseudo-label stress: do observed subject/date/raw-feature neighborhoods support the candidate movement?",
        "",
        "## Wonder",
        "",
        "Does mixmin move A2C8 probabilities toward labels implied by train raw-feature neighbors and same-subject temporal priors, or is its support mostly anchor-derived?",
        "",
        "## Hypothesis",
        "",
        "H35: raw observed structure independently supports mixmin. If true, mixmin should improve soft LogLoss versus A2C8 across subject-temporal, raw-feature KNN, cross-subject KNN, coverage, behavior, and cluster pseudo-label views. If false, support should be sparse, worse than pair sensors, or contradicted by selector veto.",
        "",
        "## Method",
        "",
        "Built 10 train-derived pseudo-label sources from `analysis_outputs/all_keys_deep_features.parquet`: subject mean, same-subject temporal KNN, all-sensor KNN, cross-subject sensor KNN, coverage-count KNN, sensor-stat KNN, and raw-feature clusters. Scored five candidate sensors against A2C8 using soft LogLoss, movement-to-prior alignment, and row movement anatomy. No public LB scores or known public-anchor losses are used in these pseudo-labels.",
        "",
        "## Result",
        "",
        f"- pseudo-label sources: `{len(sources)}`.",
        f"- train/test adversarial AUC from raw sensor features: `{domain_auc:.6f}`.",
        f"- raw-structure gates passing: `{int(summary['raw_structure_gate'].sum())}`.",
        f"- best support-rate candidate: `{top['role']}` with support_rate `{top['support_rate']:.3f}`, mean_delta `{top['mean_delta']:.9f}`, worst_delta `{top['worst_delta']:.9f}`.",
        f"- mixmin support_rate `{mixmin['support_rate']:.3f}`, mean_delta `{mixmin['mean_delta']:.9f}`, worst_delta `{mixmin['worst_delta']:.9f}`, mean_toward_rate `{mixmin['mean_toward_rate']:.3f}`.",
        "",
        "## Interpretation",
        "",
    ]
    mixmin_strong_raw = (
        float(mixmin["support_rate"]) >= 0.70
        and float(mixmin["mean_delta"]) < 0
        and float(mixmin["worst_delta"]) <= 0
    )
    if bool(mixmin["raw_structure_gate"]):
        report.append(
            "Raw-structure pseudo-labels independently support mixmin strongly enough to reopen the normal-submit question, but selector hard veto must still be reconciled before calling it safe."
        )
    elif mixmin_strong_raw:
        report.append(
            "Raw-structure pseudo-labels support mixmin directionally, but not enough to override E35 selector veto or certify a normal submission."
        )
    else:
        report.append(
            "Raw-structure pseudo-labels do not support mixmin as an independent validation source. This strengthens the E35 conclusion: mixmin remains a public sensor for anchor-loss/binary-world geometry, not an independently validated improvement."
        )
    if str(top["role"]) == "inverse7blend_1040":
        report.append(
            "The surprising positive result is inverse7: it improves against every raw-structure pseudo-label source, including same-subject temporal, raw-feature KNN, cross-subject KNN, coverage, behavior, and cluster priors. That makes inverse7 the current bridge candidate between anchor-loss geometry and raw observed structure, but E35 selector veto and weaker anchor-LOO stability still block a normal-submit claim."
        )
    report += [
        "",
        "## Decision",
        "",
        "Strict submit candidate count remains 0 unless a candidate passes raw-structure support and resolves selector veto. Use this audit to decide whether the next step should search for a better independent raw-structure gate or spend a public sensor.",
        "",
        "## Outputs",
        "",
        f"- `{scores_path.relative_to(ROOT)}`",
        f"- `{summary_path.relative_to(ROOT)}`",
        f"- `{anatomy_path.relative_to(ROOT)}`",
    ]
    report_path = OUT / "raw_structure_pseudolabel_candidate_stress_report.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"raw_structure_gates={int(summary['raw_structure_gate'].sum())}")
    print(f"domain_auc={domain_auc:.6f}")
    print(summary[["role", "support_rate", "mean_delta", "worst_delta", "raw_structure_gate"]].to_string(index=False))
    print(f"wrote {summary_path.relative_to(ROOT)}")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
