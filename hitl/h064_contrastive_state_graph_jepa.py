#!/usr/bin/env python3
"""H064: Contrastive state-graph HS-JEPA.

H057 showed that H042's 45 Q2-support rows carry a full non-Q2 target vector.
H063 then asked whether those rows are discoverable from human/raw context.

H064 adds a hard negative:

    H050 moved Q1/Q3 route rows and tied H042, so H050 non-seed route rows are
    treated as null examples of "looks actionable, but not the H057 state".

The experiment learns a label-free graph score from positive H057 seed rows and
negative H050-null rows, then moves full non-Q2 vectors only on rows that are
close to H057 state and far from H050 null state.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import shutil

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h064_contrastive_state_graph_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
NON_Q2 = [t for t in TARGETS if t != "Q2"]
EPS = 1.0e-6

H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H062 = "submission_h062_h057seed_rowstate_expand_23beb8eb_uploadsafe.csv"
H063 = "submission_h063_humancontext_seed_2c748a8e_uploadsafe.csv"


@dataclass(frozen=True)
class ContextView:
    name: str
    path: Path
    max_features: int | None = None
    knn: int = 18


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    k_rows: int
    alpha: float
    mode: str
    max_per_subject: int


VIEWS = [
    ContextView("h013_raw_human", HITL / "h013_raw_human_state_jepa_gate" / "h013_human_state_features.csv"),
    ContextView("e262_social_day", ROOT / "analysis_outputs" / "e262_human_social_day_features.parquet"),
    ContextView("e268_story", ROOT / "analysis_outputs" / "e268_human_social_story_features.parquet"),
    ContextView("e328_ownlife", ROOT / "analysis_outputs" / "e328_ownlatent_lifestyle_state_features.parquet"),
    ContextView("deep_raw_top500", ROOT / "analysis_outputs" / "all_keys_deep_features.parquet", max_features=500),
]


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float64)))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = clip_prob(prob)
    qq = clip_prob(q)
    return -(qq * np.log(p) + (1.0 - qq) * np.log(1.0 - p))


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def key_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col]).dt.strftime("%Y-%m-%d")
    out["subject_id"] = out["subject_id"].astype(str)
    return out


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = ROOT / name if not Path(name).is_absolute() else Path(name)
    df = pd.read_csv(path)
    df = key_frame(df).sort_values(KEYS).reset_index(drop=True)
    if sample is not None and not df[KEYS].equals(sample[KEYS]):
        raise ValueError(f"key mismatch for {name}")
    return df


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.9f}")
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    src = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
    df = pd.read_csv(src)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    tix = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        mat[int(rec["row"]), tix[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(mat)


def move(base: np.ndarray, q: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * q)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(q)))
    raise ValueError(mode)


def support_rows_by_diff(a: np.ndarray, b: np.ndarray, targets: list[str]) -> np.ndarray:
    ix = [TARGETS.index(t) for t in targets]
    changed = np.abs(a[:, ix] - b[:, ix]) > 1.0e-12
    return np.where(changed.any(axis=1))[0]


def changed_rows(path: str, base_prob: np.ndarray, sample: pd.DataFrame) -> set[int]:
    root_path = ROOT / path
    if not root_path.exists():
        return set()
    df = load_sub(root_path, sample)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return set(np.where((np.abs(prob - base_prob) > 1.0e-12).any(axis=1))[0].tolist())


def nearest_seed_distance(sample: pd.DataFrame, seed_rows: np.ndarray) -> np.ndarray:
    dist = np.full(len(sample), 999.0, dtype=np.float64)
    for subject, sub in sample.reset_index().groupby("subject_id"):
        idx = sub["index"].to_numpy(dtype=int)
        seed = np.array([row for row in seed_rows if sample.loc[row, "subject_id"] == subject], dtype=int)
        if len(seed) == 0:
            continue
        for row in idx:
            dist[row] = float(np.min(np.abs(seed - row)))
    return dist


def read_view(view: ContextView) -> pd.DataFrame:
    if view.path.suffix == ".parquet":
        df = pd.read_parquet(view.path)
    else:
        df = pd.read_csv(view.path)
    return key_frame(df).drop_duplicates(KEYS, keep="last").sort_values(KEYS).reset_index(drop=True)


def robust_l2_features(df: pd.DataFrame, max_features: int | None) -> tuple[np.ndarray, list[str]]:
    excluded = set(KEYS + TARGETS + ["split"])
    num_cols = [c for c in df.columns if c not in excluded and pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        raise ValueError("no numeric columns")
    x = df[num_cols].replace([np.inf, -np.inf], np.nan).astype(np.float64)
    x = x.loc[:, x.notna().any(axis=0)]
    if max_features is not None and x.shape[1] > max_features:
        keep = x.var(axis=0, skipna=True).fillna(0.0).sort_values(ascending=False).head(max_features).index.tolist()
        x = x[keep]
    med = x.median(axis=0, skipna=True)
    q25 = x.quantile(0.25, axis=0)
    q75 = x.quantile(0.75, axis=0)
    iqr = (q75 - q25).replace(0.0, np.nan)
    scaled = ((x.fillna(med) - med) / iqr.fillna(1.0)).clip(-8.0, 8.0).fillna(0.0)
    mat = scaled.to_numpy(dtype=np.float64)
    norm = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.maximum(norm, 1.0e-12), list(scaled.columns)


def pairwise_cosine_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    sim = np.clip(a @ b.T, -1.0, 1.0)
    return np.sqrt(np.maximum(0.0, 2.0 - 2.0 * sim))


def rank_pct_high(values: np.ndarray) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64))
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def label_propagation_scores(z: np.ndarray, seed_rows: np.ndarray, null_rows: np.ndarray, knn: int) -> np.ndarray:
    sim = np.maximum(z @ z.T, 0.0)
    np.fill_diagonal(sim, 0.0)
    n = sim.shape[0]
    w = np.zeros_like(sim)
    for i in range(n):
        idx = np.argpartition(-sim[i], kth=min(knn, n - 1))[:knn]
        vals = sim[i, idx]
        keep = vals > 0
        w[i, idx[keep]] = vals[keep]
    row_sum = w.sum(axis=1, keepdims=True)
    w = w / np.maximum(row_sum, 1.0e-12)
    y = np.zeros(n, dtype=np.float64)
    y[seed_rows] = 1.0
    y[null_rows] = -1.0
    score = y.copy()
    for _ in range(80):
        score = 0.82 * (w @ score) + 0.18 * y
        score[seed_rows] = 1.0
        score[null_rows] = -1.0
    return score


def view_contrast_scores(
    view: ContextView,
    sample: pd.DataFrame,
    seed_rows: np.ndarray,
    null_rows: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, object]]:
    df = read_view(view)
    sample_keys = [tuple(row) for row in sample[KEYS].to_numpy()]
    key_to_pos = {tuple(row): i for i, row in enumerate(df[KEYS].to_numpy())}
    missing = [k for k in sample_keys if k not in key_to_pos]
    if missing:
        raise ValueError(f"{view.name} missing sample keys: {missing[:3]}")
    mat_all, cols = robust_l2_features(df, view.max_features)
    sample_pos = np.array([key_to_pos[k] for k in sample_keys], dtype=int)
    z = mat_all[sample_pos]

    seed_dist = pairwise_cosine_distance(z, z[seed_rows])
    null_dist = pairwise_cosine_distance(z, z[null_rows])
    for j, row in enumerate(seed_rows):
        seed_dist[row, j] = np.inf
    for j, row in enumerate(null_rows):
        null_dist[row, j] = np.inf
    min_seed_dist = np.min(seed_dist, axis=1)
    min_null_dist = np.min(null_dist, axis=1)
    seed_score = rank_pct_high(-min_seed_dist)
    null_score = rank_pct_high(-min_null_dist)
    contrast_margin = seed_score - null_score
    contrast_rank = rank_pct_high(contrast_margin)
    graph_raw = label_propagation_scores(z, seed_rows, null_rows, view.knn)
    graph_rank = rank_pct_high(graph_raw)

    seed_to_seed = min_seed_dist[seed_rows]
    seed_to_null = np.min(pairwise_cosine_distance(z[seed_rows], z[null_rows]), axis=1)
    separation = float(np.mean(seed_to_null) - np.mean(seed_to_seed))
    weight = float(max(0.05, min(1.0, 0.5 + 1.5 * separation)))
    score = pd.DataFrame(
        {
            "row": np.arange(len(sample), dtype=int),
            f"{view.name}_seed_dist": min_seed_dist,
            f"{view.name}_null_dist": min_null_dist,
            f"{view.name}_seed_score": seed_score,
            f"{view.name}_null_score": null_score,
            f"{view.name}_contrast_rank": contrast_rank,
            f"{view.name}_graph_raw": graph_raw,
            f"{view.name}_graph_rank": graph_rank,
        }
    )
    diag = {
        "view": view.name,
        "path": str(view.path),
        "rows": int(len(df)),
        "features_used": int(len(cols)),
        "seed_internal_distance_mean": float(np.mean(seed_to_seed)),
        "seed_to_null_distance_mean": float(np.mean(seed_to_null)),
        "separation": separation,
        "top45_graph_seed_hit_rate": float(np.isin(np.argsort(-graph_rank)[:45], seed_rows).mean()),
        "top45_graph_null_hit_rate": float(np.isin(np.argsort(-graph_rank)[:45], null_rows).mean()),
        "context_weight": weight,
    }
    return score, diag


def build_row_scores(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h050_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    seed_rows = support_rows_by_diff(h057_prob, h042_prob, NON_Q2)
    h050_route_rows = support_rows_by_diff(h050_prob, h042_prob, NON_Q2)
    null_rows = np.array(sorted(set(h050_route_rows.tolist()) - set(seed_rows.tolist())), dtype=int)
    h062_rows = changed_rows(H062, h057_prob, sample)
    h063_rows = changed_rows(H063, h057_prob, sample)
    order_dist = nearest_seed_distance(sample, seed_rows)
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]

    records = []
    for row in range(len(sample)):
        gain_by_target = bce(h057_prob[row, nonq_ix], q061[row, nonq_ix]) - bce(q061[row, nonq_ix], q061[row, nonq_ix])
        records.append(
            {
                "row": row,
                "subject_id": sample.loc[row, "subject_id"],
                "sleep_date": sample.loc[row, "sleep_date"],
                "lifelog_date": sample.loc[row, "lifelog_date"],
                "is_h057_seed": int(row in set(seed_rows.tolist())),
                "is_h050_null": int(row in set(null_rows.tolist())),
                "h062_changed_row": int(row in h062_rows),
                "h063_changed_row": int(row in h063_rows),
                "nearest_seed_order_distance": float(order_dist[row]),
                "episode_near": float(order_dist[row] <= 3),
                "row_gain_to_q061_nonq2": float(gain_by_target.sum()),
                "min_target_gain": float(np.min(gain_by_target)),
                "positive_targets": int((gain_by_target > 0).sum()),
                "Q1_gain": float(gain_by_target[NON_Q2.index("Q1")]),
                "Q3_gain": float(gain_by_target[NON_Q2.index("Q3")]),
                "S1_gain": float(gain_by_target[NON_Q2.index("S1")]),
                "S2_gain": float(gain_by_target[NON_Q2.index("S2")]),
                "S3_gain": float(gain_by_target[NON_Q2.index("S3")]),
                "S4_gain": float(gain_by_target[NON_Q2.index("S4")]),
            }
        )
    rows = pd.DataFrame(records)
    rows["gain_rank"] = rank_pct_high(rows["row_gain_to_q061_nonq2"].to_numpy())
    rows["min_gain_rank"] = rank_pct_high(rows["min_target_gain"].to_numpy())
    rows["positive_rank"] = rank_pct_high(rows["positive_targets"].to_numpy())
    rows["episode_rank"] = rank_pct_high(rows["episode_near"].to_numpy())

    diagnostics = []
    weights = []
    graph_cols = []
    contrast_cols = []
    seed_cols = []
    null_cols = []
    for view in VIEWS:
        view_scores, diag = view_contrast_scores(view, sample, seed_rows, null_rows)
        rows = rows.merge(view_scores, on="row", how="left", validate="one_to_one")
        diagnostics.append(diag)
        weights.append(float(diag["context_weight"]))
        graph_cols.append(f"{view.name}_graph_rank")
        contrast_cols.append(f"{view.name}_contrast_rank")
        seed_cols.append(f"{view.name}_seed_score")
        null_cols.append(f"{view.name}_null_score")

    w = np.asarray(weights, dtype=np.float64)
    w = w / np.maximum(w.sum(), 1.0e-12)
    rows["graph_consensus"] = rows[graph_cols].to_numpy(dtype=np.float64) @ w
    rows["contrast_consensus"] = rows[contrast_cols].to_numpy(dtype=np.float64) @ w
    rows["seed_context"] = rows[seed_cols].to_numpy(dtype=np.float64) @ w
    rows["null_context"] = rows[null_cols].to_numpy(dtype=np.float64) @ w
    rows["null_avoidance"] = 1.0 - rows["null_context"]
    rows["h064_row_score"] = (
        0.30 * rows["graph_consensus"]
        + 0.22 * rows["contrast_consensus"]
        + 0.18 * rows["gain_rank"]
        + 0.09 * rows["min_gain_rank"]
        + 0.07 * rows["episode_rank"]
        + 0.06 * rows["h062_changed_row"]
        + 0.06 * rows["h063_changed_row"]
        - 0.28 * rows["is_h050_null"]
    )
    return rows.sort_values("h064_row_score", ascending=False).reset_index(drop=True), pd.DataFrame(diagnostics), seed_rows, null_rows


def select_rows(row_scores: pd.DataFrame, spec: CandidateSpec) -> pd.DataFrame:
    df = row_scores[row_scores["is_h057_seed"] == 0].copy()
    if spec.family == "contrast_strict":
        df = df[df["is_h050_null"] == 0]
        score_col = "h064_row_score"
    elif spec.family == "contrast_episode":
        df = df[(df["is_h050_null"] == 0) & (df["episode_near"] > 0)]
        score_col = "h064_row_score"
    elif spec.family == "graph_strict":
        df = df[df["is_h050_null"] == 0]
        score_col = "graph_consensus"
    elif spec.family == "h062_h063_intersection":
        df = df[(df["is_h050_null"] == 0) & ((df["h062_changed_row"] > 0) | (df["h063_changed_row"] > 0))]
        score_col = "h064_row_score"
    elif spec.family == "null_recovery":
        df = df[(df["is_h050_null"] > 0) & (df["graph_consensus"] > 0.65)]
        score_col = "h064_row_score"
    else:
        raise ValueError(spec.family)

    selected = []
    counts: dict[str, int] = {}
    for rec in df.sort_values([score_col, "row_gain_to_q061_nonq2"], ascending=[False, False]).to_dict("records"):
        subject = str(rec["subject_id"])
        if counts.get(subject, 0) >= spec.max_per_subject:
            continue
        selected.append(rec)
        counts[subject] = counts.get(subject, 0) + 1
        if len(selected) >= spec.k_rows:
            break
    return pd.DataFrame(selected)


def make_candidate(
    spec: CandidateSpec,
    sample: pd.DataFrame,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    row_scores: pd.DataFrame,
) -> tuple[np.ndarray, dict[str, object]]:
    selected = select_rows(row_scores, spec)
    prob = h057_prob.copy()
    moved = move(h057_prob, q061, spec.alpha, spec.mode)
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]
    for row in selected["row"].astype(int).tolist():
        prob[row, nonq_ix] = moved[row, nonq_ix]
    diff = np.abs(prob - h057_prob) > 1.0e-12
    selected_set = set(selected["row"].astype(int).tolist())
    delta = float(np.mean(bce(prob, q061) - bce(h057_prob, q061)))
    per_target = {f"{target}_changed_vs_h057": int(diff[:, i].sum()) for i, target in enumerate(TARGETS)}
    return clip_prob(prob), {
        "family": spec.family,
        "k_rows": spec.k_rows,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "max_per_subject": spec.max_per_subject,
        "selected_rows": ",".join(map(str, selected["row"].astype(int).tolist())),
        "posterior_delta_vs_h057": delta,
        "changed_cells_vs_h057": int(diff.sum()),
        "changed_rows_vs_h057": int(diff.any(axis=1).sum()),
        "q2_changed_vs_h057": int(diff[:, TARGETS.index("Q2")].sum()),
        "mean_graph_consensus": float(selected["graph_consensus"].mean()) if len(selected) else 0.0,
        "mean_contrast_consensus": float(selected["contrast_consensus"].mean()) if len(selected) else 0.0,
        "mean_seed_context": float(selected["seed_context"].mean()) if len(selected) else 0.0,
        "mean_null_context": float(selected["null_context"].mean()) if len(selected) else 0.0,
        "mean_selected_gain": float(selected["row_gain_to_q061_nonq2"].mean()) if len(selected) else 0.0,
        "episode_near_rate": float(selected["episode_near"].mean()) if len(selected) else 0.0,
        "selected_subjects": int(selected["subject_id"].nunique()) if len(selected) else 0,
        "h050_null_rows_selected": int(selected["is_h050_null"].sum()) if len(selected) else 0,
        "h062_overlap_rows": int(selected["h062_changed_row"].sum()) if len(selected) else 0,
        "h063_overlap_rows": int(selected["h063_changed_row"].sum()) if len(selected) else 0,
        "h062_overlap_rate": float(selected["h062_changed_row"].mean()) if len(selected) else 0.0,
        "h063_overlap_rate": float(selected["h063_changed_row"].mean()) if len(selected) else 0.0,
        **per_target,
    }


def sweep_candidates(
    sample: pd.DataFrame,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    row_scores: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Path]]:
    specs = [
        CandidateSpec(family, k_rows, alpha, mode, max_per_subject)
        for family in ["contrast_strict", "contrast_episode", "graph_strict", "h062_h063_intersection", "null_recovery"]
        for k_rows in [18, 24, 36, 48, 72, 96]
        for alpha in [0.45, 0.65, 0.85, 1.00]
        for mode in ["logit", "prob"]
        for max_per_subject in [4, 6, 10, 16]
    ]
    rows = []
    paths: dict[str, Path] = {}
    for spec in specs:
        selected = select_rows(row_scores, spec)
        if len(selected) < min(spec.k_rows, 12):
            continue
        prob, meta = make_candidate(spec, sample, h057_prob, q061, row_scores)
        digest = short_hash(prob)
        cid = (
            f"h064_{spec.family}_r{spec.k_rows}_a{str(spec.alpha).replace('.', 'p')}_"
            f"{spec.mode}_mps{spec.max_per_subject}_{digest}"
        )
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)
        paths[cid] = path
        rows.append({"candidate_id": cid, "file": path.name, "resolved_path": str(path), **meta})
    out = pd.DataFrame(rows)
    out["h064_score"] = (
        0.95 * rank_pct_high(-out["posterior_delta_vs_h057"].to_numpy())
        + 0.42 * out["mean_graph_consensus"].rank(method="average", pct=True)
        + 0.34 * out["mean_contrast_consensus"].rank(method="average", pct=True)
        + 0.26 * out["h063_overlap_rate"].rank(method="average", pct=True)
        + 0.22 * out["h062_overlap_rate"].rank(method="average", pct=True)
        + 0.16 * out["selected_subjects"].rank(method="average", pct=True)
        + 0.10 * out["episode_near_rate"].rank(method="average", pct=True)
        - 0.35 * (out["h050_null_rows_selected"] > 0).astype(float)
        - 0.18 * (out["changed_cells_vs_h057"] > 576).astype(float)
        - 0.12 * (out["changed_cells_vs_h057"] < 144).astype(float)
    )
    return out.sort_values(["h064_score", "posterior_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True), paths


def validate(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    df = load_sub(path, sample)
    probs = df[TARGETS].to_numpy(dtype=np.float64)
    diff = np.abs(probs - h057_prob) > 1.0e-12
    return {
        "path": str(path),
        "rows": int(len(df)),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(df[TARGETS].isna().sum().sum()),
        "min_prob": float(np.min(probs)),
        "max_prob": float(np.max(probs)),
        "q2_changed_vs_h057_validation": int(diff[:, TARGETS.index("Q2")].sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and df.duplicated(KEYS).sum() == 0
            and df[TARGETS].isna().sum().sum() == 0
            and np.min(probs) > 0.0
            and np.max(probs) < 1.0
            and diff[:, TARGETS.index("Q2")].sum() == 0
        ),
    }


def main() -> None:
    h042 = load_sub(H042)
    sample = h042[KEYS].copy()
    h050 = load_sub(H050, sample)
    h057 = load_sub(H057, sample)
    h042_prob = h042[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = h050[TARGETS].to_numpy(dtype=np.float64)
    h057_prob = h057[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)

    row_scores, diagnostics, seed_rows, null_rows = build_row_scores(sample, h042_prob, h050_prob, h057_prob, q061)
    candidates, paths = sweep_candidates(sample, h057_prob, q061, row_scores)
    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    selected_prob = load_sub(selected_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    root_name = f"submission_h064_contrastive_state_graph_{short_hash(selected_prob)}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)
    check = validate(root_path, sample, h057_prob)

    top_nonseed = row_scores[(row_scores["is_h057_seed"] == 0) & (row_scores["is_h050_null"] == 0)].head(60)
    summary = pd.DataFrame(
        [
            {
                "h057_seed_rows": int(len(seed_rows)),
                "h050_null_rows": int(len(null_rows)),
                "candidate_rows_outside_seed_null": int(((row_scores["is_h057_seed"] == 0) & (row_scores["is_h050_null"] == 0)).sum()),
                "top60_h062_overlap": float(top_nonseed["h062_changed_row"].mean()),
                "top60_h063_overlap": float(top_nonseed["h063_changed_row"].mean()),
                "top60_episode_near_rate": float(top_nonseed["episode_near"].mean()),
                "top60_mean_graph": float(top_nonseed["graph_consensus"].mean()),
                "top60_mean_contrast": float(top_nonseed["contrast_consensus"].mean()),
                "top60_mean_gain": float(top_nonseed["row_gain_to_q061_nonq2"].mean()),
            }
        ]
    )
    decision = pd.DataFrame(
        [
            {
                "decision": "promote_contrastive_state_graph_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H057 row-state is graph-propagatable when H050 null-route rows are used as hard negatives",
                **selected.to_dict(),
                **check,
            }
        ]
    )

    diagnostics.to_csv(OUT / "h064_view_diagnostics.csv", index=False)
    row_scores.to_csv(OUT / "h064_row_scores.csv", index=False)
    candidates.to_csv(OUT / "h064_candidate_scores.csv", index=False)
    summary.to_csv(OUT / "h064_summary.csv", index=False)
    decision.to_csv(OUT / "h064_decision.csv", index=False)

    report = f"""# H064 Contrastive State-Graph HS-JEPA

Question: can H057's full-vector row-state be propagated through a human/raw
feature graph if H050's public-null route rows are used as hard negatives?

Design:

- base: H057 public frontier;
- positive target representation: the `45` H057 full-vector row-state rows;
- negative/null representation: H050 non-seed route rows that did not improve
  over H042;
- context: H013 raw human, E262 social-day, E268 story, E328 own-life, and
  deep raw feature graphs;
- action: freeze Q2 and move full non-Q2 vectors toward H061 `q061` on selected
  positive-graph / null-far rows.

Summary:

{md_table(summary)}

View diagnostics:

{md_table(diagnostics)}

Decision:

{md_table(decision)}

Top contrastive non-seed, non-null rows:

{md_table(top_nonseed.head(45), n=45)}

Top generated submissions:

{md_table(candidates.head(25), n=25)}

Interpretation rule:

- If H064 improves over H057, H050's failure was not evidence against row-state
  propagation; it was a wrong-route/null anchor that helps define the state
  boundary.
- If H064 fails while H063 improves, the negative anchor is too aggressive and
  H050-null rows should not be excluded.
- If both H063 and H064 fail, the H057 state is likely compact/public-specific
  and expansion requires a stronger target-side state translator.
"""
    (OUT / "h064_report.md").write_text(report)
    print(f"H064 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H064 root: {root_path}")
    print(
        decision[
            [
                "selected_candidate_id",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "posterior_delta_vs_h057",
                "mean_graph_consensus",
                "mean_contrast_consensus",
                "h062_overlap_rate",
                "h063_overlap_rate",
                "h050_null_rows_selected",
                "selected_subjects",
                "upload_safe",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
