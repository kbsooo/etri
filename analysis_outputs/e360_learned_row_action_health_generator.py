#!/usr/bin/env python3
"""E360: learned row-action-health generator.

Question:
    E359 rejected hand-shaped row gates over the compact lifestyle-state action.
    Is row-action health itself learnable enough to propose a different,
    non-monotone row placement that survives both output visibility and
    row-state public-survival stress?

JEPA/data2vec translation:
    context = source compact action + row-level lifestyle/story state +
              candidate movement exposure
    target  = action-health representation measured by E272 visibility,
              bad-axis safety, and E358 row-state survival
    action  = learned shortlist of nonlinear row placements, then actual
              public-free stress verification

No public LB is optimized.  Known public observations are used only through the
fixed E272/E358 diagnostic sensors already established before E360.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.model_selection import GroupKFold, KFold


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e328_ownlatent_lifestyle_state_experiment import md_table, safe_id  # noqa: E402
from e358_rowstate_public_survival_audit import (  # noqa: E402
    feature_columns as e358_feature_columns,
    known_observations as e358_known_observations,
    load_anchor,
    load_row_state,
    make_models as e358_make_models,
    rowstate_features,
)
from e359_rowplacement_action_health_probe import (  # noqa: E402
    EPS,
    KEY,
    SOURCES,
    TARGETS,
    clip_prob,
    load_source,
    logit,
    row_state_scores,
    selector_scores,
    sigmoid,
)


RNG_SEED = 20260531 + 360
UPLOAD_PREFIX = "submission_e360_rowaction"

TRAIN_IN = OUT / "e359_rowplacement_action_health_scores.csv"
POOL_PREFEATURE_OUT = OUT / "e360_learned_row_action_health_pool_prefeatures.csv"
TRAIN_DIAG_OUT = OUT / "e360_learned_row_action_health_surrogate_diagnostics.csv"
CANDIDATE_OUT = OUT / "e360_learned_row_action_health_candidates.csv"
SCORE_OUT = OUT / "e360_learned_row_action_health_scores.csv"
KNOWN_OUT = OUT / "e360_learned_row_action_health_known.csv"
SELECTION_OUT = OUT / "e360_learned_row_action_health_selection.csv"
REPORT_OUT = OUT / "e360_learned_row_action_health_report.md"

N_POOL = 1800
N_SHORTLIST = 140


def short_hash(frame: pd.DataFrame) -> str:
    payload = pd.util.hash_pandas_object(frame[KEY + TARGETS], index=False).to_numpy(dtype=np.uint64).tobytes()
    return hashlib.sha1(payload).hexdigest()[:8]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def zarr(values: pd.Series | np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    sd = float(np.std(arr))
    if not np.isfinite(sd) or sd < 1.0e-12:
        return np.zeros_like(arr)
    return (arr - float(np.mean(arr))) / sd


def pct_rank_good(values: pd.Series | np.ndarray, higher_is_better: bool = True) -> pd.Series:
    s = pd.Series(values, dtype="float64").replace([np.inf, -np.inf], np.nan)
    if not higher_is_better:
        s = -s
    return s.rank(pct=True, method="average").fillna(0.5)


def safe_spearman(a: pd.Series | np.ndarray, b: pd.Series | np.ndarray) -> float:
    x = pd.Series(a, dtype="float64")
    y = pd.Series(b, dtype="float64")
    mask = x.notna() & y.notna()
    if int(mask.sum()) < 8:
        return np.nan
    x = x[mask]
    y = y[mask]
    if x.nunique() < 2 or y.nunique() < 2:
        return np.nan
    val = spearmanr(x, y).correlation
    return float(val) if np.isfinite(val) else np.nan


def add_health_targets(train: pd.DataFrame) -> pd.DataFrame:
    out = train.copy()
    out["y_visibility"] = -pd.to_numeric(out["pred_delta_vs_current_p90"], errors="coerce")
    out["y_mean_visibility"] = -pd.to_numeric(out["pred_delta_vs_current_mean"], errors="coerce")
    out["y_beats"] = pd.to_numeric(out["pred_beats_current_rate"], errors="coerce")
    out["y_bad_axis"] = 0.015 - pd.to_numeric(out["incremental_bad_axis_vs_current"], errors="coerce").abs()
    out["y_rowloss"] = -pd.to_numeric(out["rowstate_pred_public_loss_mean"], errors="coerce")
    out["y_rowvar"] = -pd.to_numeric(out["rowstate_pred_public_loss_std"], errors="coerce")
    out["y_exposure"] = -pd.to_numeric(out["rowstate_bad_minus_good_exposure"], errors="coerce")
    out["y_move"] = pd.to_numeric(out["move_l1"], errors="coerce")
    out["y_rowaction_health"] = (
        1.45 * pct_rank_good(out["y_visibility"])
        + 1.10 * pct_rank_good(out["y_mean_visibility"])
        + 0.65 * pct_rank_good(out["y_beats"])
        + 1.10 * pct_rank_good(out["y_bad_axis"])
        + 1.45 * pct_rank_good(out["y_rowloss"])
        + 0.75 * pct_rank_good(out["y_rowvar"])
        + 1.05 * pct_rank_good(out["y_exposure"])
        + 0.35 * pct_rank_good(out["y_move"])
    ) / 7.90
    out["near_miss_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (pd.to_numeric(out["rowstate_pred_public_loss_mean"], errors="coerce") <= 0.00108)
        & (pd.to_numeric(out["rowstate_bad_minus_good_exposure"], errors="coerce") <= 0.1565)
    )
    return out


def gate_family(gate_id: object) -> str:
    text = str(gate_id)
    if text.startswith("risk_top"):
        return "risk_top"
    if text.startswith("smooth"):
        return "smooth_risk"
    if text.startswith("goodboost"):
        return "goodboost"
    if text.startswith("cluster"):
        return "cluster_suppress"
    if text.startswith("badcluster"):
        return "badcluster"
    if text.startswith("learned"):
        return "learned"
    return "other"


BLOCK_TOKENS = (
    "pred_delta",
    "pred_beats",
    "strict_promote",
    "info_sensor",
    "below_resolution",
    "block_gate",
    "promotion_decision",
    "rowstate_pred_public_loss",
    "e359_gate",
    "e359_rowgate_score",
    "e360_",
    "decision",
    "selected",
    "reason",
    "y_",
    "near_miss",
    "file",
    "basename",
    "source_path",
    "current_anchor",
)


def feature_matrix(frame: pd.DataFrame, fit_columns: list[str] | None = None) -> tuple[pd.DataFrame, list[str]]:
    work = frame.copy()
    work["gate_family"] = work.get("gate_id", pd.Series("unknown", index=work.index)).map(gate_family)
    cat_cols = [c for c in ["source_id", "gate_family", "policy_family", "target_policy"] if c in work.columns]
    numeric_cols: list[str] = []
    for col in work.columns:
        if col in cat_cols:
            continue
        if any(tok in col for tok in BLOCK_TOKENS):
            continue
        if pd.api.types.is_numeric_dtype(work[col]) and work[col].nunique(dropna=True) > 1:
            numeric_cols.append(col)
    num = work[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    cat = pd.get_dummies(work[cat_cols].astype(str), columns=cat_cols, dummy_na=False) if cat_cols else pd.DataFrame(index=work.index)
    x = pd.concat([num, cat], axis=1)
    if fit_columns is None:
        return x, x.columns.tolist()
    return x.reindex(columns=fit_columns, fill_value=0.0), fit_columns


def train_surrogates(train: pd.DataFrame) -> tuple[dict[str, Any], list[str], pd.DataFrame]:
    x, columns = feature_matrix(train)
    y = train["y_rowaction_health"].to_numpy(dtype=np.float64)
    models: dict[str, Any] = {
        "extratrees": ExtraTreesRegressor(n_estimators=220, min_samples_leaf=3, max_features=0.65, random_state=RNG_SEED, n_jobs=1),
        "randomforest": RandomForestRegressor(n_estimators=220, min_samples_leaf=3, max_features=0.65, random_state=RNG_SEED + 1, n_jobs=1),
    }
    rows: list[dict[str, Any]] = []
    splits: list[tuple[str, Any]] = [
        ("random5", KFold(n_splits=5, shuffle=True, random_state=RNG_SEED)),
        ("leave_source", GroupKFold(n_splits=max(2, min(4, train["source_id"].nunique())))),
    ]
    for model_name, model in models.items():
        for split_name, splitter in splits:
            pred = np.full(len(train), np.nan, dtype=np.float64)
            if split_name == "leave_source":
                iterator = splitter.split(x, y, groups=train["source_id"].astype(str))
            else:
                iterator = splitter.split(x, y)
            for tr, va in iterator:
                m = model.__class__(**model.get_params())
                m.fit(x.iloc[tr], y[tr])
                pred[va] = m.predict(x.iloc[va])
            rows.append(
                {
                    "model": model_name,
                    "split": split_name,
                    "spearman_health": safe_spearman(pred, y),
                    "spearman_visibility": safe_spearman(pred, train["y_visibility"]),
                    "spearman_rowloss": safe_spearman(pred, train["y_rowloss"]),
                    "top20_overlap": float(np.mean(train.iloc[np.argsort(-pred)[: max(1, len(train) // 5)]]["y_rowaction_health"].rank(pct=True) >= 0.80)),
                    "n": len(train),
                }
            )
    for model in models.values():
        model.fit(x, y)
    diag = pd.DataFrame(rows).sort_values(["spearman_health", "spearman_rowloss"], ascending=[False, False]).reset_index(drop=True)
    diag.to_csv(TRAIN_DIAG_OUT, index=False)
    return models, columns, diag


def selected_story_features(state: pd.DataFrame, story_cols: list[str], n: int = 18) -> list[str]:
    target = pd.Series(state["rowstate_bad_minus_good"], dtype="float64")
    rows: list[tuple[float, str]] = []
    for col in story_cols:
        s = pd.Series(state[col], dtype="float64")
        val = safe_spearman(s, target)
        if np.isfinite(val):
            rows.append((abs(val), col))
    rows.sort(reverse=True)
    return [col for _, col in rows[:n]]


def row_gate_basis(state: pd.DataFrame, base_scores: pd.DataFrame, story_cols: list[str]) -> dict[str, np.ndarray]:
    basis: dict[str, np.ndarray] = {
        "risk_core": zarr(base_scores["risk_core"]),
        "good_core": zarr(base_scores["good_core"]),
        "bad_cluster": zarr(state["rowstate_e323_cluster_rate"]),
        "good_cluster": zarr(state["rowstate_e247_cluster_rate"]),
        "e256_cluster": zarr(state["rowstate_e256_cluster_rate"]),
        "bad_minus_good": zarr(state["rowstate_bad_minus_good"]),
        "energy": zarr(state["ownlife_energy"]),
        "resid_mean": zarr(state["ownlife_student_resid_mean"]),
        "cluster_distance": zarr(state["ownlife_cluster_distance"]),
        "weekend": zarr(state["is_weekend"]),
        "weekday": zarr(state["weekday"]),
    }
    for i in range(1, 9):
        col = f"ownlife_pc{i}"
        if col in state:
            basis[col] = zarr(state[col])
    for col in selected_story_features(state, story_cols, n=18):
        basis[f"story:{col}"] = zarr(state[col])
    return basis


def target_scales(rng: np.random.Generator, policy: str) -> np.ndarray:
    scales = np.ones(len(TARGETS), dtype=np.float64)
    if policy == "compact_qs1":
        for target, value in {"Q1": 1.00, "Q2": 1.00, "Q3": 1.00, "S1": 1.00, "S3": 0.35}.items():
            scales[TARGETS.index(target)] = value
    elif policy == "low_s3":
        scales[TARGETS.index("S3")] = rng.uniform(0.0, 0.45)
    elif policy == "subjective_heavy":
        for target in ["Q1", "Q2", "Q3"]:
            scales[TARGETS.index(target)] = rng.uniform(0.95, 1.18)
        scales[TARGETS.index("S1")] = rng.uniform(0.70, 1.05)
        scales[TARGETS.index("S3")] = rng.uniform(0.0, 0.60)
    elif policy == "s1_counter":
        scales[TARGETS.index("Q1")] = rng.uniform(0.85, 1.05)
        scales[TARGETS.index("Q2")] = rng.uniform(0.80, 1.05)
        scales[TARGETS.index("Q3")] = rng.uniform(0.70, 1.05)
        scales[TARGETS.index("S1")] = rng.uniform(1.00, 1.22)
        scales[TARGETS.index("S3")] = rng.uniform(0.0, 0.75)
    else:
        for target in ["Q1", "Q2", "Q3", "S1", "S3"]:
            scales[TARGETS.index(target)] = rng.uniform(0.75, 1.18)
    return scales


def make_gate(rng: np.random.Generator, basis: dict[str, np.ndarray], state: pd.DataFrame, policy_family: str) -> tuple[np.ndarray, dict[str, Any]]:
    names = list(basis.keys())
    raw = np.zeros(len(state), dtype=np.float64)
    meta: dict[str, Any] = {"policy_family": policy_family}
    if policy_family == "health_prior":
        coeffs = {
            "risk_core": rng.uniform(-1.4, -0.35),
            "good_core": rng.uniform(0.25, 1.20),
            "bad_minus_good": rng.uniform(-1.0, -0.10),
            "energy": rng.uniform(-0.45, 0.25),
        }
        for name, coef in coeffs.items():
            raw += coef * basis[name]
        k = int(rng.integers(1, 4))
        extra = rng.choice([n for n in names if n not in coeffs], size=k, replace=False)
        for name in extra:
            raw += rng.normal(0.0, 0.35) * basis[name]
        meta["feature_count"] = len(coeffs) + k
    elif policy_family == "anti_bad_cluster":
        raw += rng.uniform(-1.8, -0.45) * basis["bad_cluster"]
        raw += rng.uniform(0.15, 1.10) * basis["good_cluster"]
        raw += rng.normal(0.0, 0.35) * basis["resid_mean"]
        meta["feature_count"] = 3
    elif policy_family == "story_nonmonotone":
        story = [n for n in names if n.startswith("story:")]
        pick = rng.choice(story, size=min(len(story), int(rng.integers(2, 5))), replace=False)
        for name in pick:
            raw += rng.normal(0.0, 0.85) * basis[name]
        raw += rng.uniform(-0.9, -0.15) * basis["risk_core"]
        meta["feature_count"] = len(pick) + 1
    elif policy_family == "pc_episode":
        pcs = [n for n in names if n.startswith("ownlife_pc")]
        pick = rng.choice(pcs, size=min(len(pcs), int(rng.integers(2, 5))), replace=False)
        for name in pick:
            raw += rng.normal(0.0, 0.75) * basis[name]
        raw += rng.uniform(0.10, 0.75) * basis["good_core"]
        meta["feature_count"] = len(pick) + 1
    else:
        pick = rng.choice(names, size=int(rng.integers(3, 7)), replace=False)
        for name in pick:
            raw += rng.normal(0.0, 0.65) * basis[name]
        meta["feature_count"] = len(pick)

    clusters = pd.to_numeric(state["ownlife_k8"], errors="coerce").fillna(-1).astype(int).to_numpy()
    if rng.random() < 0.55:
        chosen = rng.choice(np.arange(8), size=int(rng.integers(1, 4)), replace=False)
        for cluster_id in chosen:
            raw[clusters == int(cluster_id)] += rng.normal(0.0, 0.95)
        meta["cluster_bias_count"] = len(chosen)
    else:
        meta["cluster_bias_count"] = 0

    raw += rng.normal(-0.10, 0.35)
    temperature = rng.uniform(0.70, 2.40)
    low = rng.choice([0.0, 0.08, 0.15, 0.25, 0.35])
    high = rng.uniform(0.80, 1.22)
    gate = low + (high - low) * sigmoid(temperature * raw)
    if rng.random() < 0.20:
        # Sparse high-confidence row placement. This is deliberately not the
        # same as the monotone E359 top-risk suppression.
        cutoff = np.quantile(gate, rng.uniform(0.62, 0.82))
        gate = np.where(gate >= cutoff, gate, gate * rng.uniform(0.0, 0.35))
        meta["sparsified"] = 1
    else:
        meta["sparsified"] = 0
    meta["gate_mean"] = float(np.mean(gate))
    meta["gate_std"] = float(np.std(gate))
    meta["gate_p10"] = float(np.quantile(gate, 0.10))
    meta["gate_p90"] = float(np.quantile(gate, 0.90))
    return gate.astype(np.float64), meta


def candidate_prefeatures(
    source_id: str,
    source_delta: np.ndarray,
    gated_delta: np.ndarray,
    state: pd.DataFrame,
    base_cols: list[str],
    story_cols: list[str],
    meta: dict[str, Any],
) -> dict[str, Any]:
    absd = np.abs(gated_delta)
    target_abs = absd.sum(axis=0)
    total = float(target_abs.sum())
    row_abs = absd.sum(axis=1)
    rec: dict[str, Any] = {
        **meta,
        "source_id": source_id,
        "source_l1": float(np.abs(source_delta).sum()),
        "move_l1": float(absd.sum()),
        "move_l2": float(np.linalg.norm(gated_delta.reshape(-1))),
        "row_l1_p90": float(np.quantile(row_abs, 0.90)),
        "changed_rows_vs_e247": int((row_abs > 1.0e-12).sum()),
        "changed_cells_vs_e247": int((absd > 1.0e-12).sum()),
    }
    rec["gated_l1_ratio"] = rec["move_l1"] / rec["source_l1"] if rec["source_l1"] > 0 else 0.0
    for i, target in enumerate(TARGETS):
        rec[f"abs_{target}"] = float(target_abs[i])
        rec[f"share_{target}"] = float(target_abs[i] / total) if total > 0 else 0.0
    rec.update(rowstate_features(gated_delta, state, base_cols, story_cols))
    return rec


def generate_pool(anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> tuple[pd.DataFrame, dict[int, np.ndarray]]:
    rng = np.random.default_rng(RNG_SEED)
    base_scores = row_state_scores(state)
    basis = row_gate_basis(state, base_scores, story_cols)
    source_deltas: dict[str, np.ndarray] = {}
    for source_id, path in SOURCES.items():
        if not path.exists():
            continue
        src = load_source(path, anchor)
        source_deltas[source_id] = logit(src[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
    if not source_deltas:
        raise RuntimeError("No source deltas available for E360")

    policies = ["health_prior", "anti_bad_cluster", "story_nonmonotone", "pc_episode", "free_mixture"]
    target_policies = ["compact_qs1", "low_s3", "subjective_heavy", "s1_counter", "random_compact"]
    source_ids = list(source_deltas.keys())
    rows: list[dict[str, Any]] = []
    deltas: dict[int, np.ndarray] = {}
    seen: set[str] = set()
    attempts = 0
    while len(rows) < N_POOL and attempts < N_POOL * 8:
        attempts += 1
        source_id = str(rng.choice(source_ids, p=np.array([0.18, 0.26, 0.26, 0.30])[: len(source_ids)] / np.array([0.18, 0.26, 0.26, 0.30])[: len(source_ids)].sum()))
        policy_family = str(rng.choice(policies, p=[0.30, 0.22, 0.18, 0.18, 0.12]))
        target_policy = str(rng.choice(target_policies, p=[0.24, 0.24, 0.20, 0.18, 0.14]))
        gate, meta = make_gate(rng, basis, state, policy_family)
        scales = target_scales(rng, target_policy)
        base = source_deltas[source_id]
        gated = base * gate[:, None] * scales[None, :]
        base_l1 = float(np.abs(base).sum())
        gated_l1 = float(np.abs(gated).sum())
        if gated_l1 <= 1.0e-12:
            continue
        cap = float(rng.choice([0.95, 1.00, 1.05, 1.10, 1.15]))
        if gated_l1 > base_l1 * cap:
            gated *= (base_l1 * cap) / gated_l1
        elif gated_l1 < base_l1 * 0.55:
            gated *= min(base_l1 * 0.85 / gated_l1, 1.18)
        if np.abs(gated).sum() < 2.4:
            continue
        digest = hashlib.sha1(np.round(gated, 7).tobytes()).hexdigest()[:12]
        if digest in seen:
            continue
        seen.add(digest)
        row_id = len(rows)
        meta = {
            **meta,
            "pool_id": row_id,
            "gate_id": f"learned_{policy_family}_{target_policy}_{row_id:04d}",
            "variant": f"{source_id}__learned_{policy_family}_{target_policy}_{row_id:04d}",
            "target_policy": target_policy,
            "renorm_cap": cap,
        }
        rec = candidate_prefeatures(source_id, base, gated, state, base_cols, story_cols, meta)
        rows.append(rec)
        deltas[row_id] = gated
    pool = pd.DataFrame(rows).reset_index(drop=True)
    pool.to_csv(POOL_PREFEATURE_OUT, index=False)
    return pool, deltas


def predict_pool(train: pd.DataFrame, pool: pd.DataFrame, models: dict[str, Any], columns: list[str]) -> pd.DataFrame:
    x_pool, _ = feature_matrix(pool, columns)
    out = pool.copy()
    pred_cols = []
    for name, model in models.items():
        col = f"e360_surrogate_{name}"
        out[col] = np.asarray(model.predict(x_pool), dtype=np.float64)
        pred_cols.append(col)
    out["e360_surrogate_mean"] = out[pred_cols].mean(axis=1)
    out["e360_surrogate_std"] = out[pred_cols].std(axis=1)
    out["e360_prefilter_score"] = (
        1.20 * pct_rank_good(out["e360_surrogate_mean"])
        + 0.70 * pct_rank_good(-out["wmean_rowstate_bad_minus_good"])
        + 0.55 * pct_rank_good(-out["move_share_top20_rowstate_e323_cluster_rate"])
        + 0.40 * pct_rank_good(out["gated_l1_ratio"])
        + 0.35 * pct_rank_good(-out["share_S3"])
        - 0.45 * pct_rank_good(out["e360_surrogate_std"])
    )
    baseline_best = float(train["y_rowaction_health"].max())
    out["surrogate_above_e359_best"] = out["e360_surrogate_mean"] > baseline_best
    out = out.sort_values(["e360_prefilter_score", "e360_surrogate_mean"], ascending=[False, False]).reset_index(drop=True)
    out.to_csv(POOL_PREFEATURE_OUT, index=False)
    return out


def write_candidate(anchor: pd.DataFrame, anchor_logit: np.ndarray, delta: np.ndarray, rec: pd.Series) -> tuple[Path, dict[str, Any]]:
    out = anchor[KEY].copy()
    out[TARGETS] = clip_prob(sigmoid(anchor_logit + delta))
    variant = str(rec["variant"])
    path = OUT / f"{UPLOAD_PREFIX}_{safe_id(variant, 96)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    row = rec.to_dict()
    row["file"] = rel(path)
    row["basename"] = path.name
    return path, row


def materialize_shortlist(pool: pd.DataFrame, deltas: dict[int, np.ndarray], anchor: pd.DataFrame, anchor_logit: np.ndarray) -> pd.DataFrame:
    # Take top candidates, but force policy/source diversity so the actual
    # stress test is a learned-generator test rather than one narrow mode.
    selected_idx: list[int] = []
    for _, group in pool.groupby(["source_id", "policy_family", "target_policy"], dropna=False):
        selected_idx.extend(group.head(2).index.tolist())
    selected_idx.extend(pool.head(N_SHORTLIST).index.tolist())
    ordered = []
    seen = set()
    for idx in selected_idx:
        if idx in seen:
            continue
        seen.add(idx)
        ordered.append(idx)
        if len(ordered) >= N_SHORTLIST:
            break
    rows: list[dict[str, Any]] = []
    for idx in ordered:
        rec = pool.loc[idx]
        _, row = write_candidate(anchor, anchor_logit, deltas[int(rec["pool_id"])], rec)
        rows.append(row)
    out = pd.DataFrame(rows)
    out.to_csv(CANDIDATE_OUT, index=False)
    return out


def rowstate_public_scores(scored: pd.DataFrame, anchor: pd.DataFrame, anchor_logit: np.ndarray, state: pd.DataFrame, base_cols: list[str], story_cols: list[str]) -> pd.DataFrame:
    known = e358_known_observations(anchor, anchor_logit, state, base_cols, story_cols)
    known.to_csv(KNOWN_OUT, index=False)
    cols = e358_feature_columns(known)
    x_known = known[cols].replace([np.inf, -np.inf], 0.0).fillna(0.0)
    y = known["delta_vs_e247"].to_numpy(dtype=np.float64)
    rows: list[dict[str, Any]] = []
    for rec in scored.to_dict("records"):
        path = Path(str(rec["file"]))
        if not path.is_absolute():
            path = ROOT / path
        sub = load_source(path, anchor)
        delta = logit(sub[TARGETS].to_numpy(dtype=np.float64)) - anchor_logit
        feats = rowstate_features(delta, state, base_cols, story_cols)
        rows.append({**rec, **feats})
    out = pd.DataFrame(rows)
    x_pool = out.reindex(columns=cols).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    pred_cols = []
    for name, model in e358_make_models().items():
        model.fit(x_known, y)
        col = f"rowstate_pred_public_loss_{name}"
        out[col] = np.asarray(model.predict(x_pool), dtype=np.float64)
        pred_cols.append(col)
    out["rowstate_pred_public_loss_mean"] = out[pred_cols].mean(axis=1)
    out["rowstate_pred_public_loss_std"] = out[pred_cols].std(axis=1)
    out["rowstate_bad_exposure"] = out["wmean_rowstate_e323_cluster_rate"] + out["wmean_rowstate_e256_cluster_rate"]
    out["rowstate_good_exposure"] = out["wmean_rowstate_e247_cluster_rate"]
    out["rowstate_bad_minus_good_exposure"] = out["rowstate_bad_exposure"] - out["rowstate_good_exposure"]
    return out


def select(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    out["e360_actual_score"] = (
        1.30 * pct_rank_good(-out["pred_delta_vs_current_p90"])
        + 1.10 * pct_rank_good(-out["rowstate_pred_public_loss_mean"])
        + 0.85 * pct_rank_good(-out["rowstate_pred_public_loss_std"])
        + 0.90 * pct_rank_good(-out["rowstate_bad_minus_good_exposure"])
        + 0.85 * pct_rank_good(0.015 - out["incremental_bad_axis_vs_current"].abs())
        + 0.45 * pct_rank_good(out["e360_surrogate_mean"])
    ) / 5.45
    out["e360_submission_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00082)
        & (out["rowstate_pred_public_loss_std"] <= 0.00055)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.145)
    )
    out["e360_nearmiss_gate"] = (
        out["strict_promote_gate"].fillna(False).astype(bool)
        & (out["pred_delta_vs_current_p90"] < -0.00005)
        & (out["incremental_bad_axis_vs_current"].abs() <= 0.015)
        & (out["rowstate_pred_public_loss_mean"] <= 0.00096)
        & (out["rowstate_bad_minus_good_exposure"] <= 0.150)
    )
    ranked = out.sort_values(["e360_submission_gate", "e360_actual_score"], ascending=[False, False]).reset_index(drop=True)
    passed = ranked[ranked["e360_submission_gate"]].head(1)
    if passed.empty:
        selected = ranked.head(1).copy()
        selected["decision"] = "no_rowaction_submission"
        selected["selected_uploadsafe_file"] = "none"
        selected["reason"] = "Learned row-action generator did not clear strict E272 visibility plus E358 row-state health gates."
    else:
        selected = passed.copy()
        src = ROOT / str(selected.iloc[0]["file"])
        frame = pd.read_csv(src)
        upload = OUT / f"{UPLOAD_PREFIX}_selected_{safe_id(str(selected.iloc[0]['variant']), 72)}_{short_hash(frame)}_uploadsafe.csv"
        shutil.copyfile(src, upload)
        selected["decision"] = "select_learned_rowaction_probe"
        selected["selected_uploadsafe_file"] = rel(upload)
        selected["reason"] = "Learned row-action generator passed strict output and row-state health gates."
    selected.to_csv(SELECTION_OUT, index=False)
    ranked.to_csv(SCORE_OUT, index=False)
    return selected


def write_report(train: pd.DataFrame, diag: pd.DataFrame, pool: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame) -> None:
    top_cols = [
        "variant",
        "source_id",
        "policy_family",
        "target_policy",
        "e360_submission_gate",
        "e360_nearmiss_gate",
        "e360_actual_score",
        "e360_surrogate_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "rowstate_pred_public_loss_mean",
        "rowstate_pred_public_loss_std",
        "rowstate_bad_minus_good_exposure",
        "wmean_rowstate_bad_minus_good",
        "move_l1",
        "gated_l1_ratio",
        "share_S3",
        "file",
    ]
    top_cols = [c for c in top_cols if c in scored.columns]
    source_summary = (
        scored.groupby(["source_id", "policy_family"], dropna=False)
        .agg(
            n=("variant", "count"),
            submit=("e360_submission_gate", "sum"),
            near=("e360_nearmiss_gate", "sum"),
            strict=("strict_promote_gate", "sum"),
            best_p90=("pred_delta_vs_current_p90", "min"),
            best_rowloss=("rowstate_pred_public_loss_mean", "min"),
            best_exposure=("rowstate_bad_minus_good_exposure", "min"),
            best_actual=("e360_actual_score", "max"),
        )
        .reset_index()
        .sort_values(["submit", "near", "best_actual"], ascending=[False, False, False])
    )
    lines = [
        "# E360 Learned Row-Action-Health Generator",
        "",
        "## Question",
        "",
        "Can a learned nonlinear row-action generator do what E359 hand gates could not: preserve output visibility while lowering row-state public-survival risk?",
        "",
        "## Method",
        "",
        "- Training data: E359 row-gated compact action outcomes.",
        "- Target representation: composite of E272 p90 visibility, mean visibility, bad-axis margin, row-state predicted public loss, row-state variance, bad-minus-good exposure, and movement size.",
        "- Context: source action, gate/action geometry, movement-weighted E328 lifestyle state, and E268 story-tail exposures.",
        "- Generator: random nonlinear row policies over risk/good clusters, ownlife PCs, and human/social story axes, shortlisted by the learned surrogate.",
        "- Verification: actual E272 selector plus actual E358 row-state public-survival scoring.",
        "",
        "## Surrogate Diagnostics",
        "",
        md_table(diag, n=20, floatfmt=".6f"),
        "",
        "## Decision",
        "",
        md_table(selected[["decision", "variant", "selected_uploadsafe_file", "e360_actual_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure", "reason"]], n=5, floatfmt=".9f"),
        "",
        "## Source/Policy Summary",
        "",
        md_table(source_summary, n=30, floatfmt=".9f"),
        "",
        "## Top Actual-Stress Candidates",
        "",
        md_table(scored[top_cols].head(40), n=40, floatfmt=".9f"),
        "",
        "## Gate-Passing Candidates",
        "",
        md_table(scored[scored["e360_submission_gate"]][top_cols], n=40, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
        "- A pass would mean row-action health can be generated from lifestyle/story state rather than only diagnosed after the fact.",
        "- No pass means the current compact action family still cannot separate output visibility from row-state risk, even with learned nonlinear row placement.",
        "- The key next split is then whether to change the source action family or learn a lower-level cell-action generator instead of row-only gates.",
        "",
        "## Counts",
        "",
        f"- E359 training rows: `{len(train)}`",
        f"- generated prefilter pool: `{len(pool)}`",
        f"- materialized shortlist: `{len(scored)}`",
        f"- strict output candidates: `{int(scored['strict_promote_gate'].sum())}`",
        f"- near-miss candidates: `{int(scored['e360_nearmiss_gate'].sum())}`",
        f"- submission-gate candidates: `{int(scored['e360_submission_gate'].sum())}`",
        "",
        "## Files",
        "",
        f"- `{rel(POOL_PREFEATURE_OUT)}`",
        f"- `{rel(TRAIN_DIAG_OUT)}`",
        f"- `{rel(CANDIDATE_OUT)}`",
        f"- `{rel(SCORE_OUT)}`",
        f"- `{rel(KNOWN_OUT)}`",
        f"- `{rel(SELECTION_OUT)}`",
        f"- `{rel(REPORT_OUT)}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    anchor, anchor_logit = load_anchor()
    state, base_cols, story_cols = load_row_state(anchor)
    train = add_health_targets(pd.read_csv(TRAIN_IN).replace([np.inf, -np.inf], np.nan))
    models, columns, diag = train_surrogates(train)
    pool, deltas = generate_pool(anchor, anchor_logit, state, base_cols, story_cols)
    pool = predict_pool(train, pool, models, columns)
    materialized = materialize_shortlist(pool, deltas, anchor, anchor_logit)
    selected_cols = selector_scores(materialized, anchor)
    scored = rowstate_public_scores(selected_cols, anchor, anchor_logit, state, base_cols, story_cols)
    selected = select(scored)
    scored = pd.read_csv(SCORE_OUT)
    write_report(train, diag, pool, scored, selected)
    print(f"train={len(train)} pool={len(pool)} materialized={len(materialized)}")
    print(diag.round(6).to_string(index=False))
    print(selected[["decision", "variant", "selected_uploadsafe_file", "e360_actual_score", "pred_delta_vs_current_p90", "rowstate_pred_public_loss_mean", "rowstate_bad_minus_good_exposure"]].round(9).to_string(index=False))
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
