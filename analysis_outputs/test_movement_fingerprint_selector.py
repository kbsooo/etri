#!/usr/bin/env python3
"""E40 test-movement fingerprint selector audit.

This experiment asks whether label-free test prediction movement anatomy can
calibrate public selector identity better than train OOF did in E39.

It does not optimize public LB. Known public observations are used only in
leave-one-anchor-out tests. If the movement fingerprints cannot recover known
anchor ordering, they are not allowed to rank new submissions.
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
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-5

BEST_PUBLIC = 0.5774393210

KNOWN_ANCHORS = [
    {
        "name": "a2c8_best",
        "file": "analysis_outputs/submission_frontier_cvjepa_refine_a2c8d2c8.csv",
        "public_lb": 0.5774393210,
        "role": "current_best",
    },
    {
        "name": "raw_timeline",
        "file": "jepa/submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "public_lb": 0.5775263072,
        "role": "raw05_like_positive_anchor",
    },
    {
        "name": "stage2",
        "file": "analysis_outputs/submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv",
        "public_lb": 0.5779449757,
        "role": "strong_local_stage2",
    },
    {
        "name": "ordinal",
        "file": "analysis_outputs/submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
        "public_lb": 0.5783033652,
        "role": "ordinal_constraint",
    },
    {
        "name": "final9",
        "file": "analysis_outputs/submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
        "public_lb": 0.5784273528,
        "role": "subject_logit_final9",
    },
    {
        "name": "q2_jepa_bad",
        "file": "jepa/submission_jepa_latent_q2_w0p45.csv",
        "public_lb": 0.5798012862,
        "role": "bad_q2_jepa_anchor",
    },
    {
        "name": "lejepa_bad",
        "file": "jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv",
        "public_lb": 0.5802468192,
        "role": "bad_lejepa_anchor",
    },
    {
        "name": "jepa_residual_bad",
        "file": "jepa/submission_jepa_latent_residual_probe.csv",
        "public_lb": 0.5812273278,
        "role": "bad_all_target_jepa_anchor",
    },
]

VIEW_OUT = OUT / "test_movement_fingerprint_selector_views.csv"
LOOCV_OUT = OUT / "test_movement_fingerprint_selector_loocv.csv"
CAND_OUT = OUT / "test_movement_fingerprint_selector_candidates.csv"
REPORT_OUT = OUT / "test_movement_fingerprint_selector_report.md"


@dataclass
class Mask:
    name: str
    view: str
    idx: np.ndarray


def clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p.astype(np.float64), EPS, 1.0 - EPS)


def logit(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return np.log(p / (1.0 - p))


def entropy(p: np.ndarray) -> np.ndarray:
    p = clip(p)
    return -(p * np.log(p) + (1.0 - p) * np.log(1.0 - p))


def resolve_file(file_name: str) -> Path:
    path = ROOT / file_name
    if path.exists():
        return path
    for parent in (OUT, JEPA, ROOT):
        path = parent / file_name
        if path.exists():
            return path
    raise FileNotFoundError(file_name)


def read_submission(file_name: str) -> pd.DataFrame:
    path = resolve_file(file_name)
    df = pd.read_csv(path)
    for col in ("sleep_date", "lifelog_date"):
        df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    return df.sort_values(KEYS).reset_index(drop=True)


def numeric_cols(frame: pd.DataFrame) -> list[str]:
    skip = set(KEYS + TARGETS + ["split"])
    cols: list[str] = []
    for col in frame.columns:
        if col in skip:
            continue
        if not pd.api.types.is_numeric_dtype(frame[col]):
            continue
        vals = pd.to_numeric(frame[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        if int(vals.notna().sum()) >= 40:
            cols.append(col)
    return cols


def load_feature_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv")
    features = pd.read_parquet(OUT / "all_keys_deep_features.parquet")
    for df in (sample, features):
        for col in ("sleep_date", "lifelog_date"):
            df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
    sample = sample.sort_values(KEYS).reset_index(drop=True)
    train_feat = features[features["split"].eq("train")].copy().reset_index(drop=True)
    test_feat = features[features["split"].eq("submission")].copy()
    test_feat = sample[KEYS].merge(test_feat, on=KEYS, how="left", validate="one_to_one")
    if len(test_feat) != len(sample):
        raise RuntimeError("test feature alignment failed")
    return sample, train_feat.reset_index(drop=True), test_feat.reset_index(drop=True)


def make_raw_scores(train_feat: pd.DataFrame, test_feat: pd.DataFrame) -> dict[str, np.ndarray | float]:
    all_feat = pd.concat([train_feat, test_feat], axis=0, ignore_index=True)
    cols = numeric_cols(all_feat)
    x_all = all_feat[cols].replace([np.inf, -np.inf], np.nan)
    y_domain = np.r_[np.zeros(len(train_feat), dtype=int), np.ones(len(test_feat), dtype=int)]
    pipe = make_pipeline(
        SimpleImputer(strategy="median"),
        StandardScaler(),
        LogisticRegression(max_iter=1000, C=0.5, class_weight="balanced", solver="lbfgs"),
    )
    pipe.fit(x_all, y_domain)
    domain_prob = pipe.predict_proba(x_all)[:, 1]
    domain_auc = float(roc_auc_score(y_domain, domain_prob))

    prep = make_pipeline(SimpleImputer(strategy="median"), StandardScaler())
    x_train = prep.fit_transform(train_feat[cols].replace([np.inf, -np.inf], np.nan))
    x_test = prep.transform(test_feat[cols].replace([np.inf, -np.inf], np.nan))
    nn = NearestNeighbors(n_neighbors=min(8, len(train_feat)), metric="euclidean")
    nn.fit(x_train)
    dist, _ = nn.kneighbors(x_test)
    density_radius = dist[:, -1]
    missing_frac = test_feat[numeric_cols(test_feat)].replace([np.inf, -np.inf], np.nan).isna().mean(axis=1).to_numpy()

    km = KMeans(n_clusters=8, n_init=20, random_state=20260528)
    clusters = km.fit_predict(np.vstack([x_train, x_test]))[-len(test_feat) :]
    return {
        "domain_auc": domain_auc,
        "domain_prob": domain_prob[-len(test_feat) :],
        "density_radius": density_radius,
        "missing_frac": missing_frac,
        "cluster": clusters,
    }


def quantile_mask(values: np.ndarray, q: float, high: bool) -> np.ndarray:
    cut = float(np.nanquantile(values, q))
    if high:
        return np.flatnonzero(values >= cut)
    return np.flatnonzero(values <= cut)


def build_masks(sample: pd.DataFrame, raw_scores: dict[str, np.ndarray | float]) -> list[Mask]:
    n = len(sample)
    masks = [Mask("all", "target", np.arange(n, dtype=int))]
    sample = sample.copy()
    sample["_row"] = np.arange(n)

    for subject, group in sample.groupby("subject_id", sort=True):
        idx = group["_row"].to_numpy(dtype=int)
        masks.append(Mask(f"subject_{subject}", "subject", idx))

    order = np.arange(n, dtype=int)
    for i, block in enumerate(np.array_split(order, 5)):
        masks.append(Mask(f"global_order_q{i}", "order", np.asarray(block, dtype=int)))
    for frac in (0.25, 0.40):
        head = np.zeros(n, dtype=bool)
        tail = np.zeros(n, dtype=bool)
        for _subject, group in sample.groupby("subject_id", sort=True):
            idx = group["_row"].to_numpy(dtype=int)
            k = max(1, int(round(len(idx) * frac)))
            head[idx[:k]] = True
            tail[idx[-k:]] = True
        masks.append(Mask(f"per_subject_head_{frac:.2f}", "order", np.flatnonzero(head)))
        masks.append(Mask(f"per_subject_tail_{frac:.2f}", "order", np.flatnonzero(tail)))

    domain = raw_scores["domain_prob"]
    density = raw_scores["density_radius"]
    missing = raw_scores["missing_frac"]
    cluster = raw_scores["cluster"]
    assert isinstance(domain, np.ndarray)
    assert isinstance(density, np.ndarray)
    assert isinstance(missing, np.ndarray)
    assert isinstance(cluster, np.ndarray)
    for name, values in (("domain", domain), ("density_radius", density), ("missing", missing)):
        masks.append(Mask(f"{name}_low30", "raw_domain", quantile_mask(values, 0.30, high=False)))
        masks.append(Mask(f"{name}_high30", "raw_domain", quantile_mask(values, 0.70, high=True)))
    for c in sorted(set(cluster.tolist())):
        idx = np.flatnonzero(cluster == c)
        if len(idx) >= 10:
            masks.append(Mask(f"raw_cluster_{c}", "raw_domain", idx))
    return masks


def mask_features(base: np.ndarray, pred: np.ndarray, mask: Mask) -> dict[str, float]:
    idx = mask.idx
    prob_delta = pred[idx] - base[idx]
    logit_delta = logit(pred[idx]) - logit(base[idx])
    entropy_delta = entropy(pred[idx]) - entropy(base[idx])
    feats: dict[str, float] = {}
    for j, target in enumerate(TARGETS):
        feats[f"{mask.name}__{target}__prob_mean"] = float(prob_delta[:, j].mean())
        feats[f"{mask.name}__{target}__prob_abs_mean"] = float(np.abs(prob_delta[:, j]).mean())
        feats[f"{mask.name}__{target}__logit_mean"] = float(logit_delta[:, j].mean())
        feats[f"{mask.name}__{target}__logit_abs_mean"] = float(np.abs(logit_delta[:, j]).mean())
        feats[f"{mask.name}__{target}__entropy_mean"] = float(entropy_delta[:, j].mean())
    feats[f"{mask.name}__all__prob_abs_mean"] = float(np.abs(prob_delta).mean())
    feats[f"{mask.name}__all__logit_abs_mean"] = float(np.abs(logit_delta).mean())
    feats[f"{mask.name}__all__entropy_mean"] = float(entropy_delta.mean())
    return feats


def fingerprint_for_file(file_name: str, base: np.ndarray, masks: list[Mask]) -> dict[str, Any]:
    pred = clip(read_submission(file_name)[TARGETS].to_numpy(float))
    if pred.shape != base.shape:
        raise RuntimeError(f"shape mismatch for {file_name}: {pred.shape} vs {base.shape}")
    row: dict[str, Any] = {"file": file_name}
    for mask in masks:
        row.update(mask_features(base, pred, mask))
    return row


def row_kind(mask: Mask) -> str:
    return mask.view


def view_columns(fp: pd.DataFrame, masks: list[Mask], view: str) -> list[str]:
    id_cols = {"name", "file", "role", "public_lb", "public_delta_vs_best"}
    if view == "target":
        prefixes = {"all"}
    elif view == "subject":
        prefixes = {m.name for m in masks if m.view in {"target", "subject"}}
    elif view == "order":
        prefixes = {m.name for m in masks if m.view in {"target", "order"}}
    elif view == "raw_domain":
        prefixes = {m.name for m in masks if m.view in {"target", "raw_domain"}}
    elif view == "combined":
        prefixes = {m.name for m in masks}
    else:
        raise ValueError(view)
    out = []
    for col in fp.columns:
        if col in id_cols:
            continue
        prefix = col.split("__", 1)[0]
        if prefix in prefixes:
            out.append(col)
    return out


def scale_train_query(x_train: np.ndarray, x_query: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    med = np.nanmedian(x_train, axis=0)
    x_train = np.where(np.isfinite(x_train), x_train, med)
    x_query = np.where(np.isfinite(x_query), x_query, med)
    mu = x_train.mean(axis=0)
    sd = x_train.std(axis=0)
    keep = sd > 1e-10
    if int(keep.sum()) == 0:
        raise RuntimeError("all fingerprint features are constant")
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


def pairwise_rank_accuracy(actual: np.ndarray, pred: np.ndarray) -> float:
    good = 0
    total = 0
    for i in range(len(actual)):
        for j in range(i + 1, len(actual)):
            a = np.sign(actual[i] - actual[j])
            p = np.sign(pred[i] - pred[j])
            if a == 0 or p == 0:
                continue
            good += int(a == p)
            total += 1
    return float(good / total) if total else np.nan


def spearman_corr(a: np.ndarray, b: np.ndarray) -> float:
    ra = pd.Series(a).rank(method="average").to_numpy(float)
    rb = pd.Series(b).rank(method="average").to_numpy(float)
    if np.std(ra) == 0 or np.std(rb) == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


def evaluate_view(fp_known: pd.DataFrame, masks: list[Mask], view: str) -> tuple[dict[str, Any], pd.DataFrame]:
    cols = view_columns(fp_known, masks, view)
    x = fp_known[cols].to_numpy(float)
    y = fp_known["public_delta_vs_best"].to_numpy(float)
    pred = np.zeros(len(fp_known), dtype=float)
    neigh_txt = []
    for i in range(len(fp_known)):
        train_idx = np.array([j for j in range(len(fp_known)) if j != i], dtype=int)
        p, neigh = predict_knn(x[train_idx], y[train_idx], x[[i]])
        pred[i] = p[0]
        neigh_txt.append(neigh[0])
    loocv = fp_known[["name", "file", "role", "public_lb", "public_delta_vs_best"]].copy()
    loocv["view"] = view
    loocv["predicted_delta"] = pred
    loocv["error"] = pred - y
    loocv["abs_error"] = np.abs(loocv["error"])
    loocv["neighbor_indices"] = neigh_txt

    actual_stage2 = float(fp_known.loc[fp_known["name"].eq("stage2"), "public_delta_vs_best"].iloc[0])
    actual_ordinal = float(fp_known.loc[fp_known["name"].eq("ordinal"), "public_delta_vs_best"].iloc[0])
    pred_stage2 = float(loocv.loc[loocv["name"].eq("stage2"), "predicted_delta"].iloc[0])
    pred_ordinal = float(loocv.loc[loocv["name"].eq("ordinal"), "predicted_delta"].iloc[0])
    pred_a2c8 = float(loocv.loc[loocv["name"].eq("a2c8_best"), "predicted_delta"].iloc[0])
    summary = {
        "view": view,
        "n_features": int(len(cols)),
        "loocv_mae": float(loocv["abs_error"].mean()),
        "loocv_max_abs_error": float(loocv["abs_error"].max()),
        "pairwise_rank_accuracy": pairwise_rank_accuracy(y, pred),
        "spearman": spearman_corr(y, pred),
        "stage2_ordinal_order_correct": bool(np.sign(actual_stage2 - actual_ordinal) == np.sign(pred_stage2 - pred_ordinal)),
        "a2c8_predicted_best": bool(pred_a2c8 <= float(np.min(pred))),
        "raw05_near_best": bool(
            float(loocv.loc[loocv["name"].eq("raw_timeline"), "predicted_delta"].iloc[0])
            <= float(np.quantile(pred, 0.40))
        ),
    }
    rng = np.random.default_rng(20260528)
    null_rank = []
    null_mae = []
    for _ in range(500):
        y_perm = rng.permutation(y)
        pred_perm = np.zeros(len(fp_known), dtype=float)
        for i in range(len(fp_known)):
            train_idx = np.array([j for j in range(len(fp_known)) if j != i], dtype=int)
            p, _ = predict_knn(x[train_idx], y_perm[train_idx], x[[i]])
            pred_perm[i] = p[0]
        null_rank.append(pairwise_rank_accuracy(y_perm, pred_perm))
        null_mae.append(float(np.mean(np.abs(pred_perm - y_perm))))
    summary["null_rank_p_ge_actual"] = float((np.asarray(null_rank) >= summary["pairwise_rank_accuracy"]).mean())
    summary["null_mae_p_le_actual"] = float((np.asarray(null_mae) <= summary["loocv_mae"]).mean())
    summary["strict_selector_gate"] = bool(
        summary["loocv_mae"] <= 0.00055
        and summary["pairwise_rank_accuracy"] >= 0.75
        and summary["stage2_ordinal_order_correct"]
        and summary["a2c8_predicted_best"]
        and summary["null_rank_p_ge_actual"] <= 0.10
    )
    summary["loose_selector_gate"] = bool(
        summary["loocv_mae"] <= 0.00085
        and summary["pairwise_rank_accuracy"] >= 0.65
        and summary["stage2_ordinal_order_correct"]
    )
    return summary, loocv


def candidate_predictions(
    fp_known: pd.DataFrame,
    fp_query: pd.DataFrame,
    masks: list[Mask],
    view_summaries: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    y = fp_known["public_delta_vs_best"].to_numpy(float)
    for view in ["target", "subject", "order", "raw_domain", "combined"]:
        cols = view_columns(fp_known, masks, view)
        x_train = fp_known[cols].to_numpy(float)
        x_query = fp_query[cols].to_numpy(float)
        pred, neigh = predict_knn(x_train, y, x_query)
        part = fp_query[["name", "file", "role"]].copy()
        part["view"] = view
        part["predicted_delta_vs_best"] = pred
        part["predicted_public_lb"] = BEST_PUBLIC + pred
        part["neighbor_indices"] = neigh
        rows.append(part)
    out = pd.concat(rows, axis=0, ignore_index=True)
    gate_map = view_summaries.set_index("view")["strict_selector_gate"].to_dict()
    loose_map = view_summaries.set_index("view")["loose_selector_gate"].to_dict()
    out["view_strict_gate"] = out["view"].map(gate_map).fillna(False)
    out["view_loose_gate"] = out["view"].map(loose_map).fillna(False)
    return out.sort_values(["view", "predicted_delta_vs_best"]).reset_index(drop=True)


def df_to_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return "_empty_"
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_float_dtype(out[col]):
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.6g}")
        else:
            out[col] = out[col].map(lambda x: "" if pd.isna(x) else str(x))
    headers = [str(c) for c in out.columns]
    rows = out.astype(str).values.tolist()
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]

    def fmt(row: list[str]) -> str:
        return "| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(row))) + " |"

    sep = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([fmt(headers), sep] + [fmt(row) for row in rows])


def write_report(
    view_summary: pd.DataFrame,
    loocv: pd.DataFrame,
    candidates: pd.DataFrame,
    raw_scores: dict[str, np.ndarray | float],
) -> None:
    strict_n = int(view_summary["strict_selector_gate"].sum())
    loose_n = int(view_summary["loose_selector_gate"].sum())
    best_view = view_summary.sort_values(["strict_selector_gate", "loose_selector_gate", "loocv_mae"], ascending=[False, False, True]).head(1)
    candidate_pivot = (
        candidates.pivot_table(
            index=["name", "file", "role"],
            columns="view",
            values="predicted_public_lb",
            aggfunc="first",
        )
        .reset_index()
        .sort_values("combined")
    )
    candidate_pivot.columns = [str(c) for c in candidate_pivot.columns]
    lines = [
        "# E40 Test-Movement Fingerprint Selector",
        "",
        "## Observe",
        "",
        "E39 showed that OOF stability matches known-public signs but reverses stage2/ordinal rank. The next non-OOF local target is the label-free test movement fingerprint itself.",
        "",
        "## Wonder",
        "",
        "Can target, subject, row-order, and raw-domain movement anatomy recover known public LB deltas under leave-one-anchor-out strongly enough to rank new sensors?",
        "",
        "## Hypothesis",
        "",
        "H39: if the hidden public subset is encoded in test movement/raw-domain structure, then a kNN selector over label-free movement fingerprints should recover known anchor order, especially stage2 < ordinal, and pass a permutation-null stress.",
        "",
        "## Method",
        "",
        "- Fingerprints are computed from submission probability/logit/entropy movement relative to A2C8.",
        "- Views: target-only, subject, row-order, raw-domain, and combined.",
        "- Raw-domain masks use train/test domain score, train-nearest-neighbor density, missingness, and raw-feature clusters.",
        f"- Train/test domain AUC from raw features: `{float(raw_scores['domain_auc']):.6f}`.",
        "- Public LB is used only for known-anchor leave-one-out evaluation, not for direct candidate tuning.",
        "",
        "## Result",
        "",
        f"- strict selector views: `{strict_n}`.",
        f"- loose selector views: `{loose_n}`.",
        "",
        "## View Summary",
        "",
        df_to_markdown(
            view_summary[
                [
                    "view",
                    "n_features",
                    "loocv_mae",
                    "pairwise_rank_accuracy",
                    "spearman",
                    "stage2_ordinal_order_correct",
                    "a2c8_predicted_best",
                    "null_rank_p_ge_actual",
                    "strict_selector_gate",
                    "loose_selector_gate",
                ]
            ]
        ),
        "",
        "## Best View",
        "",
        df_to_markdown(best_view),
        "",
        "## Known Anchor LOOCV",
        "",
        df_to_markdown(
            loocv[
                [
                    "view",
                    "name",
                    "public_delta_vs_best",
                    "predicted_delta",
                    "abs_error",
                    "role",
                ]
            ].sort_values(["view", "public_delta_vs_best"]).head(80)
        ),
        "",
        "## Candidate Sensor Predictions",
        "",
        df_to_markdown(candidate_pivot.head(20)),
        "",
        "## Decision",
        "",
    ]
    if strict_n == 0:
        lines.append(
            "No movement-fingerprint view is a certified public selector. Treat this as another negative selector-calibration result, not as a candidate ranker."
        )
    else:
        lines.append(
            "At least one view passes the strict selector gate. Use it only as a candidate-sensor prior and require agreement with non-movement stresses before any submission claim."
        )
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{VIEW_OUT.relative_to(ROOT)}`",
        f"- `{LOOCV_OUT.relative_to(ROOT)}`",
        f"- `{CAND_OUT.relative_to(ROOT)}`",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample, train_feat, test_feat = load_feature_frames()
    raw_scores = make_raw_scores(train_feat, test_feat)
    masks = build_masks(sample, raw_scores)

    base_file = KNOWN_ANCHORS[0]["file"]
    base = clip(read_submission(base_file)[TARGETS].to_numpy(float))

    known_rows: list[dict[str, Any]] = []
    for anchor in KNOWN_ANCHORS:
        row = fingerprint_for_file(anchor["file"], base, masks)
        row.update(
            {
                "name": anchor["name"],
                "role": anchor["role"],
                "public_lb": anchor["public_lb"],
                "public_delta_vs_best": float(anchor["public_lb"] - BEST_PUBLIC),
            }
        )
        known_rows.append(row)
    fp_known = pd.DataFrame(known_rows)

    candidate_files: list[dict[str, str]] = []
    sensor_path = OUT / "worldview_sensor_discriminability_audit.csv"
    if sensor_path.exists():
        sensors = pd.read_csv(sensor_path)
        for _, row in sensors.iterrows():
            candidate_files.append({"name": str(row["role"]), "file": str(row["file"]), "role": str(row["lane"])})
    for item in KNOWN_ANCHORS:
        candidate_files.append({"name": item["name"], "file": item["file"], "role": item["role"]})
    seen: set[str] = set()
    query_rows: list[dict[str, Any]] = []
    for item in candidate_files:
        file_name = item["file"]
        if file_name in seen:
            continue
        seen.add(file_name)
        try:
            row = fingerprint_for_file(file_name, base, masks)
        except FileNotFoundError:
            continue
        row.update({"name": item["name"], "role": item["role"]})
        query_rows.append(row)
    fp_query = pd.DataFrame(query_rows)

    view_rows = []
    loocv_rows = []
    for view in ["target", "subject", "order", "raw_domain", "combined"]:
        summary, loocv = evaluate_view(fp_known, masks, view)
        view_rows.append(summary)
        loocv_rows.append(loocv)
    view_summary = pd.DataFrame(view_rows).sort_values(
        ["strict_selector_gate", "loose_selector_gate", "loocv_mae"],
        ascending=[False, False, True],
    )
    loocv_all = pd.concat(loocv_rows, axis=0, ignore_index=True)
    cand = candidate_predictions(fp_known, fp_query, masks, view_summary)

    view_summary.to_csv(VIEW_OUT, index=False)
    loocv_all.to_csv(LOOCV_OUT, index=False)
    cand.to_csv(CAND_OUT, index=False)
    write_report(view_summary, loocv_all, cand, raw_scores)

    print(f"views={len(view_summary)} strict={int(view_summary['strict_selector_gate'].sum())} loose={int(view_summary['loose_selector_gate'].sum())}")
    print(view_summary.to_string(index=False))
    print("candidate combined:")
    print(
        cand[cand["view"].eq("combined")][
            ["name", "file", "role", "predicted_public_lb", "predicted_delta_vs_best", "view_strict_gate", "view_loose_gate"]
        ]
        .sort_values("predicted_public_lb")
        .head(20)
        .to_string(index=False)
    )
    print(f"wrote {REPORT_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
