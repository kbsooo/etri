#!/usr/bin/env python3
"""H070: full HS-JEPA joint correction-field decoder.

H069 showed that public/private factorization is possible, but a threshold gate
on public_score + invariant_score - shortcut_score shrinks the H068 move. H070
changes the object: instead of selecting cells by hand-written factor cuts, it
learns a joint latent correction field from multiple masked views.

JEPA translation for this table:

    context view  -> predict public/action representation
    route view    -> predict private-safe correction representation
    shortcut view -> predict negative/shortcut representation
    joint latent  -> decode row-target correction field toward H061 q061

The point is not raw reconstruction. The point is whether visible human/context
and target-route structure can predict the hidden action-health state strongly
enough to propose row-target actions outside the H069 threshold basin.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h070_full_hsjepa_joint_decoder"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6
TOL = 1.0e-12

H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H061 = "submission_h061_h057feedback_support_69e9c079_uploadsafe.csv"
H068 = "submission_h068_action_health_3cb4f94c_uploadsafe.csv"
H069_ROOT = "submission_h069_public_private_factor_4ffd6cd6_uploadsafe.csv"

BAD_ANCHORS = [
    "submission_h010_objective_s1s4_v2_uploadsafe.csv",
    "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
    "submission_e323_5508f966_uploadsafe.csv",
    "gpt_pro_pack/q2s1_hidden_state_translation/submissions/submission_e323_5508f966_uploadsafe.csv",
    "jepa/submission_jepa_latent_q2_w0p45.csv",
    "jepa/submission_jepa_latent_residual_probe.csv",
    "jepa/submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
]


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    k: int
    alpha: float
    mode: str
    max_per_row: int
    q2_cap: int
    min_score: float
    min_gain_rank: float
    outside_h069_min: int
    target_policy: str


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H069MOD = import_module(HITL / "h069_public_private_factorization_jepa.py", "h069mod_for_h070")


def locate(name: str | Path) -> Path | None:
    return H069MOD.locate(name)


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return H069MOD.load_sub(name, sample)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H069MOD.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return H069MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H069MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H069MOD.bce(prob, q)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H069MOD.rank01(values, high)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H069MOD.md_table(frame, n)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    H069MOD.write_submission(sample, prob, path)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def move_toward(base: np.ndarray, target: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * target)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(target)))
    raise ValueError(mode)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h070_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h070_full_hsjepa_*_uploadsafe.csv"):
        path.unlink()


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    return H069MOD.load_q061(sample)


def as_prob_matrix(name: str, sample: pd.DataFrame) -> np.ndarray | None:
    path = locate(name)
    if path is None:
        return None
    try:
        return load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    except Exception:
        return None


def story_route_prior() -> pd.DataFrame:
    src = HITL / "human_state_route_hypotheses_1000.csv"
    story = pd.read_csv(src)
    priority_weight = {"high": 3.0, "medium": 1.5, "low": 1.0}
    rows = []
    for target in TARGETS:
        up = down = nodirect = direct = 0.0
        for rec in story.to_dict("records"):
            route = str(rec.get("expected_target_route", ""))
            weight = priority_weight.get(str(rec.get("priority", "")).lower(), 1.0)
            parts = [part.strip() for part in route.split(";")]
            for part in parts:
                if not part.startswith(target):
                    continue
                text = part.lower()
                if "no_direct" in text:
                    nodirect += weight
                elif "up" in text:
                    up += weight
                    direct += weight
                elif "down" in text:
                    down += weight
                    direct += weight
        total = up + down + nodirect + EPS
        rows.append(
            {
                "target": target,
                "story_route_up": up / total,
                "story_route_down": down / total,
                "story_route_no_direct": nodirect / total,
                "story_route_direct": direct / total,
                "story_route_balance": (up - down) / total,
            }
        )
    return pd.DataFrame(rows)


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    dt = pd.to_datetime(out["lifelog_date"])
    out["dow"] = dt.dt.dayofweek.astype(float)
    out["is_weekend"] = (dt.dt.dayofweek >= 5).astype(float)
    out["day_of_month"] = dt.dt.day.astype(float)
    out["month_start_prox"] = (1.0 - np.minimum(np.abs(dt.dt.day.astype(float) - 1.0), 10.0) / 10.0).astype(float)
    out["month_end_prox"] = (1.0 - np.minimum(np.abs(dt.dt.days_in_month.astype(float) - dt.dt.day.astype(float)), 10.0) / 10.0).astype(float)
    out["payday_25_prox"] = (1.0 - np.minimum(np.abs(dt.dt.day.astype(float) - 25.0), 10.0) / 10.0).astype(float)
    return out


def load_base_frames() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    h057 = load_sub(H057)
    sample = h057[KEYS].copy()
    h057_prob = h057[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = load_sub(H042, sample)[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = load_sub(H050, sample)[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)
    h069 = as_prob_matrix(H069_ROOT, sample)
    h068 = as_prob_matrix(H068, sample)
    factors = pd.read_csv(HITL / "h069_public_private_factorization_jepa" / "h069_factor_table.csv")
    factors = factors.merge(story_route_prior(), on="target", how="left", validate="many_to_one")
    factors = add_calendar_features(factors)

    if h069 is None:
        raise FileNotFoundError(H069_ROOT)
    if h068 is None:
        raise FileNotFoundError(H068)
    factors["h069_selected_cell"] = (np.abs(h069 - h057_prob) > TOL).reshape(-1).astype(float)
    factors["h068_selected_cell"] = (np.abs(h068 - h057_prob) > TOL).reshape(-1).astype(float)
    factors["outside_h069_cell"] = 1.0 - factors["h069_selected_cell"]
    factors["outside_h068_cell"] = 1.0 - factors["h068_selected_cell"]
    factors["h068_h069_disagree"] = (factors["h068_selected_cell"] != factors["h069_selected_cell"]).astype(float)
    factors["subject_num"] = factors["subject_id"].astype(str).str.replace("id", "", regex=False).astype(float)

    mats = {
        "h057": h057_prob,
        "h042": h042_prob,
        "h050": h050_prob,
        "q061": q061,
        "h068": h068,
        "h069": h069,
    }
    return sample, factors.fillna(0.0), mats


def feature_matrix(frame: pd.DataFrame, columns: list[str], add_dummies: bool = True) -> pd.DataFrame:
    x = frame[columns].copy()
    if add_dummies:
        target_dummies = pd.get_dummies(frame["target"], prefix="target", dtype=float)
        subject_dummies = pd.get_dummies(frame["subject_id"], prefix="subject", dtype=float)
        x = pd.concat([x, target_dummies, subject_dummies], axis=1)
    return x.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def safe_auc(y: np.ndarray, score: np.ndarray) -> float:
    yb = np.asarray(y) > 0.5
    if yb.min() == yb.max():
        return float("nan")
    return float(roc_auc_score(yb.astype(int), score))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ar = pd.Series(a).rank(method="average").to_numpy(dtype=float)
    br = pd.Series(b).rank(method="average").to_numpy(dtype=float)
    if np.std(ar) < 1.0e-12 or np.std(br) < 1.0e-12:
        return 0.0
    return float(np.corrcoef(ar, br)[0, 1])


def fit_oof(
    frame: pd.DataFrame,
    columns: list[str],
    target: str,
    groups: np.ndarray,
    model_kind: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, float]]:
    x = feature_matrix(frame, columns)
    y = frame[target].to_numpy(dtype=np.float64)
    oof = np.zeros(len(frame), dtype=np.float64)
    folds = GroupKFold(n_splits=5)
    fold_rows = []
    for fold, (tr, va) in enumerate(folds.split(x, y, groups=groups)):
        if model_kind == "trees":
            model = ExtraTreesRegressor(
                n_estimators=240,
                max_depth=7,
                min_samples_leaf=8,
                max_features=0.65,
                random_state=700 + fold,
                n_jobs=-1,
            )
        elif model_kind == "ridge":
            model = make_pipeline(StandardScaler(), Ridge(alpha=14.0))
        else:
            raise ValueError(model_kind)
        model.fit(x.iloc[tr], y[tr])
        pred = np.asarray(model.predict(x.iloc[va]), dtype=np.float64)
        oof[va] = pred
        fold_rows.append(
            {
                "fold": fold,
                "target": target,
                "view": model_kind,
                "mae": float(mean_absolute_error(y[va], pred)),
                "rmse": float(mean_squared_error(y[va], pred) ** 0.5),
                "spearman": spearman(y[va], pred),
            }
        )
    if model_kind == "trees":
        full_model = ExtraTreesRegressor(
            n_estimators=320,
            max_depth=8,
            min_samples_leaf=6,
            max_features=0.70,
            random_state=777,
            n_jobs=-1,
        )
    else:
        full_model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    full_model.fit(x, y)
    full_pred = np.asarray(full_model.predict(x), dtype=np.float64)
    metrics = {
        "target": target,
        "model_kind": model_kind,
        "mae": float(mean_absolute_error(y, oof)),
        "rmse": float(mean_squared_error(y, oof) ** 0.5),
        "spearman": spearman(y, oof),
        "auc_h069": safe_auc(frame["h069_selected_cell"].to_numpy(dtype=float), oof),
        "auc_h068": safe_auc(frame["h068_selected_cell"].to_numpy(dtype=float), oof),
        "fold_metrics": fold_rows,
    }
    return oof, full_pred, metrics


def build_latent(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    all_numeric = [
        col
        for col in frame.columns
        if col not in {"subject_id", "sleep_date", "lifelog_date", "target"}
        and pd.api.types.is_numeric_dtype(frame[col])
    ]
    public_cols = [
        "public_score",
        "h068_cell_health",
        "action_rank",
        "row_public_rank",
        "public_weight",
        "h067_public_weight",
        "h067_public_responsibility_rank",
        "pred_cell_delta_to_q061",
        "action_beta",
    ]
    shortcut_cols = [
        col
        for col in all_numeric
        if col.startswith("bad_pressure") or col in {"shortcut_score", "bad_top90_rate", "bad_same_direction_rate", "is_h050_null", "h050_route_cell"}
    ]
    context_cols = [
        col
        for col in [
            "h063_row_score",
            "context_consensus",
            "human_social_context",
            "raw_context",
            "h063_episode_near",
            "h064_row_score",
            "graph_consensus",
            "contrast_consensus",
            "seed_context",
            "null_context",
            "null_avoidance",
            "h067_seed_responsibility_score",
            "h067_extension_score",
            "h067_context_overlap",
            "h066_emission",
            "row_top4_gain_rank",
            "extension_score",
            "context_overlap",
            "is_weekend",
            "month_start_prox",
            "month_end_prox",
            "payday_25_prox",
        ]
        if col in frame.columns
    ]
    route_cols = [
        col
        for col in [
            "h057_prob",
            "h042_prob",
            "q061",
            "cell_q061_gain",
            "q061_gain_rank",
            "row_q061_gain_from_h057_nonq2",
            "row_loss_delta_to_q061",
            "cell_loss_delta_to_q061",
            "abs_prob_move_to_q061",
            "abs_logit_move_to_q061",
            "direction_to_q061",
            "target_index",
            "target_is_q2",
            "target_is_s",
            "target_is_nonq2",
            "target_prior_weight",
            "story_route_up",
            "story_route_down",
            "story_route_no_direct",
            "story_route_direct",
            "story_route_balance",
            "dow",
            "day_of_month",
        ]
        if col in frame.columns
    ]
    public_cols = [col for col in public_cols if col in frame.columns]
    shortcut_cols = [col for col in shortcut_cols if col in frame.columns]
    groups = frame["subject_id"].astype(str).to_numpy()

    tasks = [
        ("ctx_to_public", context_cols + route_cols + shortcut_cols, "public_score", "trees"),
        ("ctx_to_private", context_cols + route_cols + shortcut_cols, "private_safe_score", "trees"),
        ("ctx_to_action", context_cols + route_cols + shortcut_cols, "factor_action_score", "trees"),
        ("route_to_private", route_cols + shortcut_cols, "private_safe_score", "trees"),
        ("public_to_invariant", public_cols + route_cols + shortcut_cols, "invariant_score", "trees"),
        ("shortcut_pred", context_cols + route_cols + public_cols, "shortcut_score", "trees"),
        ("linear_ctx_public", context_cols + route_cols + shortcut_cols, "public_score", "ridge"),
        ("linear_ctx_private", context_cols + route_cols + shortcut_cols, "private_safe_score", "ridge"),
    ]

    latent = frame.copy()
    metric_rows = []
    fold_rows = []
    for name, cols, target, kind in tasks:
        oof, full, metrics = fit_oof(frame, cols, target, groups, kind)
        latent[f"{name}_oof"] = oof
        latent[f"{name}_full"] = full
        metric = {k: v for k, v in metrics.items() if k != "fold_metrics"}
        metric["task"] = name
        metric["n_features"] = len(feature_matrix(frame, cols).columns)
        metric_rows.append(metric)
        fold_rows.extend([{**row, "task": name} for row in metrics["fold_metrics"]])

    # LeJEPA-style health: a useful latent should be view-consistent, not one
    # collapsed public shortcut.
    pred_cols = [
        "ctx_to_public_full",
        "ctx_to_private_full",
        "ctx_to_action_full",
        "route_to_private_full",
        "public_to_invariant_full",
    ]
    pred_mat = latent[pred_cols].to_numpy(dtype=np.float64)
    latent["latent_agreement"] = 1.0 - rank01(pred_mat.std(axis=1), high=True)
    latent["latent_public_residual"] = np.abs(latent["ctx_to_public_oof"] - latent["public_score"])
    latent["latent_private_residual"] = np.abs(latent["ctx_to_private_oof"] - latent["private_safe_score"])
    latent["latent_residual_energy"] = rank01(latent["latent_public_residual"].to_numpy() + latent["latent_private_residual"].to_numpy(), high=True)
    latent["latent_context_energy"] = (
        0.32 * pd.Series(latent["ctx_to_public_full"]).rank(pct=True).to_numpy()
        + 0.26 * pd.Series(latent["ctx_to_private_full"]).rank(pct=True).to_numpy()
        + 0.22 * pd.Series(latent["ctx_to_action_full"]).rank(pct=True).to_numpy()
        + 0.12 * latent["latent_agreement"]
        + 0.08 * (1.0 - latent["latent_residual_energy"])
    )
    latent["latent_shortcut_energy"] = (
        0.55 * pd.Series(latent["shortcut_pred_full"]).rank(pct=True).to_numpy()
        + 0.30 * pd.Series(latent["shortcut_score"]).rank(pct=True).to_numpy()
        + 0.15 * pd.Series(latent["bad_pressure_rank"]).rank(pct=True).to_numpy()
    )
    latent["latent_hsjepa_score"] = (
        0.30 * pd.Series(latent["latent_context_energy"]).rank(pct=True).to_numpy()
        + 0.18 * pd.Series(latent["public_score"]).rank(pct=True).to_numpy()
        + 0.17 * pd.Series(latent["invariant_score"]).rank(pct=True).to_numpy()
        + 0.14 * pd.Series(latent["factor_action_score"]).rank(pct=True).to_numpy()
        + 0.10 * pd.Series(latent["cell_q061_gain"]).rank(pct=True).to_numpy()
        + 0.06 * latent["story_route_direct"].to_numpy(dtype=float)
        + 0.05 * latent["outside_h069_cell"].to_numpy(dtype=float)
        - 0.22 * pd.Series(latent["latent_shortcut_energy"]).rank(pct=True).to_numpy()
    )
    latent.loc[latent["cell_q061_gain"] <= 0, "latent_hsjepa_score"] -= 0.75
    latent.loc[latent["is_h050_null"] > 0, "latent_hsjepa_score"] -= 0.35
    return latent.sort_values("latent_hsjepa_score", ascending=False).reset_index(drop=True), pd.DataFrame(metric_rows), pd.DataFrame(fold_rows)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def bad_vectors(h057_prob: np.ndarray, sample: pd.DataFrame) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    for name in BAD_ANCHORS:
        prob = as_prob_matrix(name, sample)
        if prob is None:
            continue
        out[name] = (logit(prob) - logit(h057_prob)).reshape(-1)
    return out


def target_allowed(policy: str, target: str) -> bool:
    if policy == "all":
        return True
    if policy == "nonq2":
        return target != "Q2"
    if policy == "s_only":
        return target in S_TARGETS
    if policy == "q_plus_s":
        return target in {"Q1", "Q3", "S1", "S2", "S3", "S4"}
    raise ValueError(policy)


def select_cells(spec: CandidateSpec, latent: pd.DataFrame) -> pd.DataFrame:
    pool = latent[latent["target"].map(lambda t: target_allowed(spec.target_policy, str(t)))].copy()
    pool = pool[pool["cell_q061_gain"] > 0]
    pool = pool[pool["q061_gain_rank"] >= spec.min_gain_rank]
    pool = pool[pool["latent_hsjepa_score"] >= spec.min_score]
    pool = pool[pool["is_h050_null"] == 0]

    if spec.family == "joint_decoder":
        sort_cols = ["latent_hsjepa_score", "latent_context_energy", "factor_action_score"]
        asc = [False, False, False]
    elif spec.family == "outside_h069":
        pool = pool[pool["outside_h069_cell"] > 0]
        sort_cols = ["latent_hsjepa_score", "ctx_to_public_full", "invariant_score"]
        asc = [False, False, False]
    elif spec.family == "agreement_core":
        pool = pool[pool["latent_agreement"] >= 0.45]
        sort_cols = ["latent_context_energy", "latent_agreement", "latent_hsjepa_score"]
        asc = [False, False, False]
    elif spec.family == "anti_shortcut_decoder":
        pool = pool[pool["latent_shortcut_energy"] <= 0.48]
        sort_cols = ["latent_hsjepa_score", "latent_shortcut_energy", "public_score"]
        asc = [False, True, False]
    elif spec.family == "story_route_decoder":
        pool = pool[pool["story_route_direct"] >= 0.55]
        sort_cols = ["latent_hsjepa_score", "story_route_direct", "ctx_to_action_full"]
        asc = [False, False, False]
    else:
        raise ValueError(spec.family)

    pool = pool.sort_values(sort_cols, ascending=asc)
    selected = []
    row_counts: dict[int, int] = {}
    q2_count = 0
    outside_count = 0
    for rec in pool.to_dict("records"):
        row = int(rec["row"])
        target = str(rec["target"])
        if row_counts.get(row, 0) >= spec.max_per_row:
            continue
        if target == "Q2":
            if spec.q2_cap <= 0 or q2_count >= spec.q2_cap:
                continue
        selected.append(pd.DataFrame([rec]))
        row_counts[row] = row_counts.get(row, 0) + 1
        q2_count += int(target == "Q2")
        outside_count += int(float(rec["outside_h069_cell"]) > 0.5)
        if len(selected) >= spec.k and outside_count >= spec.outside_h069_min:
            break
    if not selected:
        return pool.iloc[0:0].copy()
    return pd.concat(selected, ignore_index=True)


def apply_candidate(
    spec: CandidateSpec,
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    latent: pd.DataFrame,
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    selected = select_cells(spec, latent)
    h057_prob = mats["h057"]
    q061 = mats["q061"]
    prob = h057_prob.copy()
    moved = move_toward(h057_prob, q061, spec.alpha, spec.mode)
    for rec in selected.to_dict("records"):
        prob[int(rec["row"]), int(rec["target_index"])] = moved[int(rec["row"]), int(rec["target_index"])]
    changed = np.abs(prob - h057_prob) > TOL
    x = (bce(prob, q061) - bce(h057_prob, q061)).reshape(-1)
    row_delta = (bce(prob, q061) - bce(h057_prob, q061)).mean(axis=1)
    row_public = latent.drop_duplicates("row").sort_values("row")["h067_public_weight"].to_numpy(dtype=np.float64)
    move_vec = (logit(prob) - logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:18]}": cosine(move_vec, vec) for name, vec in bad_vecs.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    rows = sorted(set(selected["row"].astype(int).tolist())) if len(selected) else []
    meta: dict[str, object] = {
        "candidate_id": "",
        "family": spec.family,
        "k": spec.k,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "max_per_row": spec.max_per_row,
        "q2_cap": spec.q2_cap,
        "min_score": spec.min_score,
        "min_gain_rank": spec.min_gain_rank,
        "outside_h069_min": spec.outside_h069_min,
        "target_policy": spec.target_policy,
        "selected_cells": int(len(selected)),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "outside_h069_cells": int(selected["outside_h069_cell"].sum()) if len(selected) else 0,
        "outside_h068_cells": int(selected["outside_h068_cell"].sum()) if len(selected) else 0,
        "h069_overlap_cells": int(selected["h069_selected_cell"].sum()) if len(selected) else 0,
        "h068_overlap_cells": int(selected["h068_selected_cell"].sum()) if len(selected) else 0,
        "public_action_pred_delta_vs_h057": float(x @ beta),
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": float(np.dot(row_public, row_delta)),
        "max_positive_bad_cosine": max_bad_cos,
        "mean_latent_hsjepa_score": float(selected["latent_hsjepa_score"].mean()) if len(selected) else 0.0,
        "mean_latent_context_energy": float(selected["latent_context_energy"].mean()) if len(selected) else 0.0,
        "mean_latent_shortcut_energy": float(selected["latent_shortcut_energy"].mean()) if len(selected) else 1.0,
        "mean_public_score": float(selected["public_score"].mean()) if len(selected) else 0.0,
        "mean_invariant_score": float(selected["invariant_score"].mean()) if len(selected) else 0.0,
        "mean_shortcut_score": float(selected["shortcut_score"].mean()) if len(selected) else 1.0,
        "h057_support_selected": int(selected["h057_support_cell"].sum()) if len(selected) else 0,
        "h050_null_selected": int(selected["is_h050_null"].sum()) if len(selected) else 0,
        "selected_subjects": int(selected["subject_id"].nunique()) if len(selected) else 0,
        "selected_rows": ",".join(map(str, rows)),
        **bad_cos,
    }
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return clip_prob(prob), meta


def candidate_sweep(
    sample: pd.DataFrame,
    mats: dict[str, np.ndarray],
    latent: pd.DataFrame,
    beta: np.ndarray,
    bad_vecs: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    specs = []
    for family in ["joint_decoder", "outside_h069", "agreement_core", "anti_shortcut_decoder", "story_route_decoder"]:
        for target_policy in ["all", "nonq2", "q_plus_s"]:
            for k in [360, 520, 700]:
                q2_cap = 42 if target_policy == "all" else 0
                outside_min = 80 if family in {"outside_h069", "joint_decoder", "story_route_decoder"} else 20
                specs.append(
                    CandidateSpec(
                        family=family,
                        k=k,
                        alpha=1.0,
                        mode="logit",
                        max_per_row=4 if family != "outside_h069" else 3,
                        q2_cap=q2_cap,
                        min_score=0.42 if family != "agreement_core" else 0.36,
                        min_gain_rank=0.40,
                        outside_h069_min=outside_min,
                        target_policy=target_policy,
                    )
                )
    rows = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    for spec in specs:
        prob, meta = apply_candidate(spec, sample, mats, latent, beta, bad_vecs)
        if meta["changed_cells_vs_h057"] < 110:
            continue
        if meta["outside_h069_cells"] < spec.outside_h069_min:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = (
            f"h070_{spec.family}_{spec.target_policy}_k{spec.k}_a{spec.alpha:.2f}_"
            f"mp{spec.max_per_row}_q2{spec.q2_cap}_out{meta['outside_h069_cells']}_{digest}"
        ).replace(".", "p")
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob
    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H070 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["latent_rank"] = rank01(cand["mean_latent_hsjepa_score"].to_numpy())
    cand["context_rank"] = rank01(cand["mean_latent_context_energy"].to_numpy())
    cand["shortcut_avoid_rank"] = rank01(-cand["mean_latent_shortcut_energy"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["outside_h069_ratio"] = cand["outside_h069_cells"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["q2_risk"] = cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)
    cand["bigbet_scale_score"] = ((-cand["public_action_pred_delta_vs_h057"] - 0.00045) / 0.0010).clip(0.0, 1.0)
    cand["h070_score"] = (
        0.23 * cand["action_rank"]
        + 0.15 * cand["latent_rank"]
        + 0.14 * cand["context_rank"]
        + 0.12 * cand["outside_h069_ratio"].clip(0.0, 1.0)
        + 0.11 * cand["responsibility_rank"]
        + 0.09 * cand["shortcut_avoid_rank"]
        + 0.08 * cand["bigbet_scale_score"]
        + 0.06 * cand["posterior_rank"]
        + 0.04 * cand["bad_avoid_rank"]
        - 0.06 * cand["q2_risk"]
        - 0.05 * (cand["h050_null_selected"] > 0).astype(float)
    )
    cand = cand.sort_values(["h070_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, rec in cand.head(120).iterrows():
        cid = str(rec["candidate_id"])
        path = OUT / f"submission_{cid}.csv"
        write_submission(sample, probs[cid], path)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = path.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(path.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path)
    lhs = df[KEYS].copy()
    rhs = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        lhs[col] = pd.to_datetime(lhs[col]).dt.strftime("%Y-%m-%d")
        rhs[col] = pd.to_datetime(rhs[col]).dt.strftime("%Y-%m-%d")
    keys_match = lhs.equals(rhs.reset_index(drop=True))
    duplicate_keys = int(df.duplicated(KEYS).sum())
    target = df[TARGETS].to_numpy(dtype=np.float64)
    nan_cells = int(np.isnan(target).sum())
    changed = np.abs(target - h057_prob) > TOL
    return {
        "path": str(path.resolve()),
        "rows": int(len(df)),
        "keys_match": bool(keys_match),
        "duplicate_keys": duplicate_keys,
        "nan_cells": nan_cells,
        "min_prob": float(np.nanmin(target)),
        "max_prob": float(np.nanmax(target)),
        "changed_cells_vs_h057_validation": int(changed.sum()),
        "upload_safe": bool(keys_match and duplicate_keys == 0 and nan_cells == 0 and np.nanmin(target) >= 0.0 and np.nanmax(target) <= 1.0),
    }


def latent_geometry(latent: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "ctx_to_public_full",
        "ctx_to_private_full",
        "ctx_to_action_full",
        "route_to_private_full",
        "public_to_invariant_full",
        "shortcut_pred_full",
        "latent_hsjepa_score",
    ]
    x = latent[cols].to_numpy(dtype=np.float64)
    x = (x - x.mean(axis=0)) / (x.std(axis=0) + EPS)
    cov = np.cov(x, rowvar=False)
    eig = np.linalg.eigvalsh(cov)
    eig = np.maximum(eig, 0.0)
    anisotropy = float(eig.max() / (eig.mean() + EPS))
    return pd.DataFrame(
        [
            {
                "latent_dims": len(cols),
                "anisotropy": anisotropy,
                "eig_max": float(eig.max()),
                "eig_min": float(eig.min()),
                "score_std": float(latent["latent_hsjepa_score"].std()),
                "score_top50_mean": float(latent.head(50)["latent_hsjepa_score"].mean()),
                "score_all_mean": float(latent["latent_hsjepa_score"].mean()),
                "top200_outside_h069_rate": float(latent.head(200)["outside_h069_cell"].mean()),
                "top200_h068_overlap_rate": float(latent.head(200)["h068_selected_cell"].mean()),
            }
        ]
    )


def write_report(metrics: pd.DataFrame, geometry: pd.DataFrame, latent: pd.DataFrame, cand: pd.DataFrame, decision: pd.DataFrame) -> None:
    report = "\n".join(
        [
            "# H070 Full HS-JEPA Joint Decoder",
            "",
            "Question: can visible human/context/route/story structure predict the",
            "hidden public/action-health representation strongly enough to propose a",
            "new row-target correction field beyond H069 threshold gating?",
            "",
            "Design:",
            "",
            "- base: H057 public frontier;",
            "- context view: H063 human/social context, H064 graph contrast, H067 row-state;",
            "- target representation: public_score, private_safe_score, factor_action_score, shortcut_score;",
            "- human-state vocabulary: 1000 story hypotheses converted to target-route priors;",
            "- predictor: masked-view ExtraTrees/Ridge decoders with subject-group OOF diagnostics;",
            "- decoder: latent_hsjepa_score materialized toward H061 q061.",
            "",
            "Masked-view diagnostics:",
            "",
            md_table(metrics, 20),
            "",
            "Latent geometry:",
            "",
            md_table(geometry),
            "",
            "Top latent cells:",
            "",
            md_table(
                latent[
                    [
                        "row",
                        "subject_id",
                        "sleep_date",
                        "target",
                        "latent_hsjepa_score",
                        "latent_context_energy",
                        "latent_shortcut_energy",
                        "public_score",
                        "invariant_score",
                        "shortcut_score",
                        "cell_q061_gain",
                        "h069_selected_cell",
                        "h068_selected_cell",
                    ]
                ].head(35),
                35,
            ),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(35), 35),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H070 improves by >= 0.001, HS-JEPA's joint latent decoder becomes the main route.",
            "- If it is neutral but H069/H068 lose, context-predicted action state is safer than public-only action-health.",
            "- If it loses badly, context-to-action prediction is not yet action-grade and H071 assignment must avoid using this score directly.",
            "",
        ]
    )
    (OUT / "h070_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    sample, factors, mats = load_base_frames()
    beta, fit, model_table = H069MOD.refit_h068_beta(sample, mats["h057"], mats["q061"])
    latent, metrics, fold_metrics = build_latent(factors)
    bad_vecs = bad_vectors(mats["h057"], sample)
    cand, probs = candidate_sweep(sample, mats, latent, beta, bad_vecs)
    geometry = latent_geometry(latent)

    selected = cand.iloc[0].copy()
    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h070_full_hsjepa_{digest}_uploadsafe.csv"
    shutil.copyfile(selected_file, root_file)
    validation = validate_submission(root_file, sample, mats["h057"])
    if not validation["upload_safe"]:
        raise RuntimeError(f"selected submission is not upload safe: {validation}")

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_full_hsjepa_joint_decoder_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected["resolved_path"]),
                "root_uploadsafe_path": str(root_file.resolve()),
                "worldview": "human/context/route/story views can predict hidden action-health and decode a correction field beyond threshold factorization",
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    model_table.to_csv(OUT / "h070_h068_action_model_refit.csv", index=False)
    fit.to_csv(OUT / "h070_known_action_fit_refit.csv", index=False)
    metrics.to_csv(OUT / "h070_masked_view_metrics.csv", index=False)
    fold_metrics.to_csv(OUT / "h070_masked_view_fold_metrics.csv", index=False)
    geometry.to_csv(OUT / "h070_latent_geometry.csv", index=False)
    latent.to_csv(OUT / "h070_latent_table.csv", index=False)
    cand.to_csv(OUT / "h070_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h070_decision.csv", index=False)
    write_report(metrics, geometry, latent, cand, decision)
    print(
        decision[
            [
                "selected_candidate_id",
                "root_uploadsafe_path",
                "changed_cells_vs_h057",
                "changed_rows_vs_h057",
                "outside_h069_cells",
                "Q2_changed_vs_h057",
                "public_action_pred_delta_vs_h057",
                "posterior_delta_vs_h057",
                "mean_latent_hsjepa_score",
                "mean_latent_shortcut_energy",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
