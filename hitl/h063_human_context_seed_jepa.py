#!/usr/bin/env python3
"""H063: Human-context seed-state HS-JEPA.

H057 proved that H042's Q2 support rows can carry a full non-Q2 target vector.
H062 then asked whether those rows are seed examples of a larger state using
mostly posterior/row-gain evidence.

H063 asks the sharper HS-JEPA question:

    Can the H057 seed row-state be rediscovered from human/social/lifestyle/raw
    context alone, and then translated into a full non-Q2 target route?

Context views are label-free feature tables.  Target representation is the H057
seed membership plus the H061 posterior vector.  The submission action freezes
Q2 and moves full non-Q2 vectors on context-nearest non-seed rows.
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
OUT = HITL / "h063_human_context_seed_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
NON_Q2 = [t for t in TARGETS if t != "Q2"]
EPS = 1.0e-6

H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H062 = "submission_h062_h057seed_rowstate_expand_23beb8eb_uploadsafe.csv"


@dataclass(frozen=True)
class ContextView:
    name: str
    path: Path
    max_features: int | None = None


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


def support_rows(h042_prob: np.ndarray, h057_prob: np.ndarray) -> np.ndarray:
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]
    changed = np.abs(h057_prob[:, nonq_ix] - h042_prob[:, nonq_ix]) > 1.0e-12
    return np.where(changed.any(axis=1))[0]


def h062_rows(sample: pd.DataFrame, h057_prob: np.ndarray) -> set[int]:
    path = ROOT / H062
    if not path.exists():
        return set()
    h062 = load_sub(path, sample)
    h062_prob = h062[TARGETS].to_numpy(dtype=np.float64)
    changed = np.abs(h062_prob - h057_prob) > 1.0e-12
    return set(np.where(changed.any(axis=1))[0].tolist())


def move(base: np.ndarray, q: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * q)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(q)))
    raise ValueError(mode)


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


def robust_l2_features(df: pd.DataFrame, max_features: int | None) -> tuple[np.ndarray, list[str]]:
    excluded = set(KEYS + TARGETS + ["split"])
    num_cols = [c for c in df.columns if c not in excluded and pd.api.types.is_numeric_dtype(df[c])]
    if not num_cols:
        raise ValueError("no numeric columns")
    x = df[num_cols].replace([np.inf, -np.inf], np.nan).astype(np.float64)
    valid = x.notna().any(axis=0)
    x = x.loc[:, valid]
    if max_features is not None and x.shape[1] > max_features:
        var = x.var(axis=0, skipna=True).fillna(0.0).sort_values(ascending=False)
        keep = var.head(max_features).index.tolist()
        x = x[keep]
    med = x.median(axis=0, skipna=True)
    q25 = x.quantile(0.25, axis=0)
    q75 = x.quantile(0.75, axis=0)
    iqr = (q75 - q25).replace(0.0, np.nan)
    scaled = (x.fillna(med) - med) / iqr.fillna(1.0)
    scaled = scaled.clip(-8.0, 8.0).fillna(0.0)
    mat = scaled.to_numpy(dtype=np.float64)
    norm = np.linalg.norm(mat, axis=1, keepdims=True)
    mat = mat / np.maximum(norm, 1.0e-12)
    return mat, list(scaled.columns)


def read_view(view: ContextView) -> pd.DataFrame:
    if view.path.suffix == ".parquet":
        df = pd.read_parquet(view.path)
    else:
        df = pd.read_csv(view.path)
    return key_frame(df).drop_duplicates(KEYS, keep="last").sort_values(KEYS).reset_index(drop=True)


def pairwise_cosine_distance(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    sim = np.clip(a @ b.T, -1.0, 1.0)
    return np.sqrt(np.maximum(0.0, 2.0 - 2.0 * sim))


def rank_pct_high(values: np.ndarray) -> np.ndarray:
    s = pd.Series(np.asarray(values, dtype=np.float64))
    return s.rank(method="average", pct=True).to_numpy(dtype=np.float64)


def view_seed_scores(
    view: ContextView,
    sample: pd.DataFrame,
    seed_rows: np.ndarray,
    rng: np.random.Generator,
    n_perm: int = 300,
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

    dist = pairwise_cosine_distance(z, z[seed_rows])
    for j, seed_row in enumerate(seed_rows):
        dist[seed_row, j] = np.inf
    min_dist = np.min(dist, axis=1)
    context_score = rank_pct_high(-min_dist)

    seed_loo = min_dist[seed_rows]
    actual = float(np.mean(seed_loo))
    random_means = []
    all_rows = np.arange(len(sample), dtype=int)
    for _ in range(n_perm):
        draw = np.sort(rng.choice(all_rows, size=len(seed_rows), replace=False))
        d = pairwise_cosine_distance(z[draw], z[draw])
        np.fill_diagonal(d, np.inf)
        random_means.append(float(np.mean(np.min(d, axis=1))))
    random_means_arr = np.asarray(random_means, dtype=np.float64)
    p_cohesion = float((np.sum(random_means_arr <= actual) + 1.0) / (len(random_means_arr) + 1.0))
    weight = float(max(0.05, 1.0 - min(1.0, 2.0 * p_cohesion)))
    score = pd.DataFrame(
        {
            "row": np.arange(len(sample), dtype=int),
            f"{view.name}_seed_distance": min_dist,
            f"{view.name}_context_score": context_score,
        }
    )
    diag = {
        "view": view.name,
        "path": str(view.path),
        "rows": int(len(df)),
        "features_used": int(len(cols)),
        "seed_internal_loo_distance_mean": actual,
        "seed_internal_loo_distance_median": float(np.median(seed_loo)),
        "nonseed_distance_mean": float(np.mean(np.delete(min_dist, seed_rows))),
        "top45_seed_hit_rate": float(np.isin(np.argsort(-context_score)[:45], seed_rows).mean()),
        "seed_cohesion_perm_p": p_cohesion,
        "context_weight": weight,
    }
    return score, diag


def base_row_scores(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    seed_rows: np.ndarray,
) -> pd.DataFrame:
    seed_set = set(seed_rows.tolist())
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]
    order_dist = nearest_seed_distance(sample, seed_rows)
    rows = []
    for row in range(len(sample)):
        gain_by_target = bce(h057_prob[row, nonq_ix], q061[row, nonq_ix]) - bce(q061[row, nonq_ix], q061[row, nonq_ix])
        rows.append(
            {
                "row": row,
                "subject_id": sample.loc[row, "subject_id"],
                "sleep_date": sample.loc[row, "sleep_date"],
                "lifelog_date": sample.loc[row, "lifelog_date"],
                "is_h057_seed": int(row in seed_set),
                "row_gain_to_q061_nonq2": float(gain_by_target.sum()),
                "min_target_gain": float(np.min(gain_by_target)),
                "positive_targets": int((gain_by_target > 0).sum()),
                "nearest_seed_order_distance": float(order_dist[row]),
                "episode_near": float(order_dist[row] <= 3),
                "Q1_gain": float(gain_by_target[NON_Q2.index("Q1")]),
                "Q3_gain": float(gain_by_target[NON_Q2.index("Q3")]),
                "S1_gain": float(gain_by_target[NON_Q2.index("S1")]),
                "S2_gain": float(gain_by_target[NON_Q2.index("S2")]),
                "S3_gain": float(gain_by_target[NON_Q2.index("S3")]),
                "S4_gain": float(gain_by_target[NON_Q2.index("S4")]),
            }
        )
    out = pd.DataFrame(rows)
    out["gain_rank"] = rank_pct_high(out["row_gain_to_q061_nonq2"].to_numpy())
    out["min_gain_rank"] = rank_pct_high(out["min_target_gain"].to_numpy())
    out["positive_rank"] = rank_pct_high(out["positive_targets"].to_numpy())
    out["episode_rank"] = rank_pct_high(out["episode_near"].to_numpy())
    return out


def build_context_row_scores(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    seed_rows = support_rows(h042_prob, h057_prob)
    rng = np.random.default_rng(63063)
    rows = base_row_scores(sample, h042_prob, h057_prob, q061, seed_rows)
    diagnostics = []
    weighted_cols = []
    weights = []
    for view in VIEWS:
        score, diag = view_seed_scores(view, sample, seed_rows, rng)
        rows = rows.merge(score, on="row", how="left", validate="one_to_one")
        diagnostics.append(diag)
        weighted_cols.append(f"{view.name}_context_score")
        weights.append(float(diag["context_weight"]))

    w = np.asarray(weights, dtype=np.float64)
    w = w / np.maximum(w.sum(), 1.0e-12)
    scores = rows[weighted_cols].to_numpy(dtype=np.float64)
    rows["context_consensus"] = scores @ w
    rows["human_social_context"] = rows[
        [
            "h013_raw_human_context_score",
            "e262_social_day_context_score",
            "e268_story_context_score",
            "e328_ownlife_context_score",
        ]
    ].mean(axis=1)
    rows["raw_context"] = rows["deep_raw_top500_context_score"]
    rows["context_consensus_rank"] = rank_pct_high(rows["context_consensus"].to_numpy())
    rows["human_social_rank"] = rank_pct_high(rows["human_social_context"].to_numpy())
    rows["raw_context_rank"] = rank_pct_high(rows["raw_context"].to_numpy())
    rows["h063_row_score"] = (
        0.42 * rows["context_consensus_rank"]
        + 0.26 * rows["gain_rank"]
        + 0.13 * rows["min_gain_rank"]
        + 0.10 * rows["positive_rank"]
        + 0.09 * rows["episode_rank"]
    )
    rows = rows.sort_values("h063_row_score", ascending=False).reset_index(drop=True)
    return rows, pd.DataFrame(diagnostics)


def select_rows(row_scores: pd.DataFrame, spec: CandidateSpec, seed_rows: np.ndarray) -> pd.DataFrame:
    score_col = {
        "mixed_context_gain": "h063_row_score",
        "context_consensus": "context_consensus",
        "human_social": "human_social_context",
        "story_only": "e268_story_context_score",
        "ownlife_only": "e328_ownlife_context_score",
        "social_day_only": "e262_social_day_context_score",
        "deep_raw": "deep_raw_top500_context_score",
    }[spec.family]
    df = row_scores[row_scores["is_h057_seed"] == 0].copy()
    df["select_score"] = df[score_col]
    selected = []
    counts: dict[str, int] = {}
    for rec in df.sort_values(["select_score", "row_gain_to_q061_nonq2"], ascending=[False, False]).to_dict("records"):
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
    seed_rows: np.ndarray,
    h062_changed_rows: set[int],
) -> tuple[np.ndarray, dict[str, object]]:
    selected_rows = select_rows(row_scores, spec, seed_rows)
    prob = h057_prob.copy()
    moved = move(h057_prob, q061, spec.alpha, spec.mode)
    nonq_ix = [TARGETS.index(t) for t in NON_Q2]
    for row in selected_rows["row"].astype(int).tolist():
        prob[row, nonq_ix] = moved[row, nonq_ix]
    diff = np.abs(prob - h057_prob) > 1.0e-12
    selected_set = set(selected_rows["row"].astype(int).tolist())
    delta = float(np.mean(bce(prob, q061) - bce(h057_prob, q061)))
    per_target = {f"{target}_changed_vs_h057": int(diff[:, i].sum()) for i, target in enumerate(TARGETS)}
    return clip_prob(prob), {
        "family": spec.family,
        "k_rows": spec.k_rows,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "max_per_subject": spec.max_per_subject,
        "selected_rows": ",".join(map(str, selected_rows["row"].astype(int).tolist())),
        "posterior_delta_vs_h057": delta,
        "changed_cells_vs_h057": int(diff.sum()),
        "changed_rows_vs_h057": int(diff.any(axis=1).sum()),
        "q2_changed_vs_h057": int(diff[:, TARGETS.index("Q2")].sum()),
        "mean_selected_context": float(selected_rows["context_consensus"].mean()) if len(selected_rows) else 0.0,
        "mean_selected_human_social": float(selected_rows["human_social_context"].mean()) if len(selected_rows) else 0.0,
        "mean_selected_gain": float(selected_rows["row_gain_to_q061_nonq2"].mean()) if len(selected_rows) else 0.0,
        "mean_selected_order_seed_dist": float(selected_rows["nearest_seed_order_distance"].mean()) if len(selected_rows) else 999.0,
        "episode_near_rate": float(selected_rows["episode_near"].mean()) if len(selected_rows) else 0.0,
        "selected_subjects": int(selected_rows["subject_id"].nunique()) if len(selected_rows) else 0,
        "h062_overlap_rows": int(len(selected_set & h062_changed_rows)),
        "h062_overlap_rate": float(len(selected_set & h062_changed_rows) / max(len(selected_set), 1)),
        **per_target,
    }


def sweep_candidates(
    sample: pd.DataFrame,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    row_scores: pd.DataFrame,
    seed_rows: np.ndarray,
    h062_changed_rows: set[int],
) -> tuple[pd.DataFrame, dict[str, Path]]:
    specs = [
        CandidateSpec(family, k_rows, alpha, mode, max_per_subject)
        for family in [
            "mixed_context_gain",
            "context_consensus",
            "human_social",
            "story_only",
            "ownlife_only",
            "social_day_only",
            "deep_raw",
        ]
        for k_rows in [24, 36, 48, 72, 96]
        for alpha in [0.45, 0.65, 0.85, 1.00]
        for mode in ["logit", "prob"]
        for max_per_subject in [6, 10, 16]
    ]
    rows = []
    paths: dict[str, Path] = {}
    for spec in specs:
        chosen = select_rows(row_scores, spec, seed_rows)
        if len(chosen) < min(spec.k_rows, 12):
            continue
        prob, meta = make_candidate(spec, sample, h057_prob, q061, row_scores, seed_rows, h062_changed_rows)
        digest = short_hash(prob)
        cid = (
            f"h063_{spec.family}_r{spec.k_rows}_a{str(spec.alpha).replace('.', 'p')}_"
            f"{spec.mode}_mps{spec.max_per_subject}_{digest}"
        )
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, prob, path)
        paths[cid] = path
        rows.append({"candidate_id": cid, "file": path.name, "resolved_path": str(path), **meta})
    out = pd.DataFrame(rows)
    out["h063_score"] = (
        -0.90 * out["posterior_delta_vs_h057"].rank(method="average", pct=True)
        + 0.45 * out["mean_selected_context"].rank(method="average", pct=True)
        + 0.25 * out["mean_selected_human_social"].rank(method="average", pct=True)
        + 0.25 * out["selected_subjects"].rank(method="average", pct=True)
        + 0.20 * out["h062_overlap_rate"].rank(method="average", pct=True)
        + 0.10 * out["changed_cells_vs_h057"].rank(method="average", pct=True)
        - 0.35 * (out["q2_changed_vs_h057"] > 0).astype(float)
        - 0.20 * (out["changed_cells_vs_h057"] > 600).astype(float)
        - 0.15 * (out["changed_cells_vs_h057"] < 240).astype(float)
    )
    return out.sort_values(["h063_score", "posterior_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True), paths


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
    h057 = load_sub(H057, sample)
    h042_prob = h042[TARGETS].to_numpy(dtype=np.float64)
    h057_prob = h057[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)
    seed_rows = support_rows(h042_prob, h057_prob)
    h062_changed = h062_rows(sample, h057_prob)

    row_scores, diagnostics = build_context_row_scores(sample, h042_prob, h057_prob, q061)
    row_scores["h062_changed_row"] = row_scores["row"].map(lambda x: int(int(x) in h062_changed))
    candidates, paths = sweep_candidates(sample, h057_prob, q061, row_scores, seed_rows, h062_changed)

    selected = candidates.iloc[0]
    selected_path = paths[str(selected["candidate_id"])]
    selected_prob = load_sub(selected_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    root_name = f"submission_h063_humancontext_seed_{short_hash(selected_prob)}_uploadsafe.csv"
    root_path = ROOT / root_name
    shutil.copyfile(selected_path, root_path)
    check = validate(root_path, sample, h057_prob)

    top_nonseed = row_scores[row_scores["is_h057_seed"] == 0].head(60)
    summary = pd.DataFrame(
        [
            {
                "h057_seed_rows": int(len(seed_rows)),
                "candidate_rows_outside_seed": int((row_scores["is_h057_seed"] == 0).sum()),
                "h062_changed_rows_known": int(len(h062_changed)),
                "top60_context_h062_overlap": float(top_nonseed["h062_changed_row"].mean()),
                "top60_episode_near_rate": float(top_nonseed["episode_near"].mean()),
                "top60_mean_context": float(top_nonseed["context_consensus"].mean()),
                "top60_mean_gain": float(top_nonseed["row_gain_to_q061_nonq2"].mean()),
            }
        ]
    )
    decision = pd.DataFrame(
        [
            {
                "decision": "promote_human_context_seed_state_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected_path),
                "root_uploadsafe_path": str(root_path),
                "worldview": "H057 seed row-state is discoverable from human/social/lifestyle/raw context",
                **selected.to_dict(),
                **check,
            }
        ]
    )

    diagnostics.to_csv(OUT / "h063_view_diagnostics.csv", index=False)
    row_scores.to_csv(OUT / "h063_row_scores.csv", index=False)
    candidates.to_csv(OUT / "h063_candidate_scores.csv", index=False)
    summary.to_csv(OUT / "h063_summary.csv", index=False)
    decision.to_csv(OUT / "h063_decision.csv", index=False)

    report = f"""# H063 Human-Context Seed-State HS-JEPA

Question: can the H057 full-vector row-state be rediscovered from label-free
human/social/lifestyle/raw context, rather than only from public-equation
posterior gain?

Design:

- base: H057 public frontier;
- seed representation: H057's `45` non-Q2 row-state rows;
- context views: H013 raw human calendar/payday, E262 social-day usage, E268
  social story features, E328 own-life latent, and deep raw aggregates;
- target representation: H061 posterior `q061`;
- action: freeze Q2, select context-nearest non-seed rows, move full non-Q2
  vectors toward `q061`.

Summary:

{md_table(summary)}

View diagnostics:

{md_table(diagnostics)}

Decision:

{md_table(decision)}

Top non-seed row-state candidates:

{md_table(row_scores[row_scores["is_h057_seed"] == 0].head(35))}

Top generated submissions:

{md_table(candidates.head(25))}

Interpretation rule:

- If H063 improves over H057, HS-JEPA has a stronger claim: H057 was not just a
  public-equation artifact; its row-state is recoverable from human context.
- If H063 fails while H062 also fails, H057 is likely a compact public-specific
  support and the current context translator is not enough.
- If H063 fails but H062 improves, posterior gain finds the state better than
  human-context similarity, so the next model should learn a supervised
  seed-state classifier instead of using nearest-context distance.
"""
    (OUT / "h063_report.md").write_text(report)
    print(f"H063 selected: {decision.loc[0, 'selected_candidate_id']}")
    print(f"H063 root: {root_path}")
    print(
        decision[
            [
                "selected_candidate_id",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "posterior_delta_vs_h057",
                "mean_selected_context",
                "h062_overlap_rate",
                "selected_subjects",
                "upload_safe",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
