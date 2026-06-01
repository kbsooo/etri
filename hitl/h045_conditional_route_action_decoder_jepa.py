#!/usr/bin/env python3
"""H045: conditional route-to-action decoder HS-JEPA.

H044 rejected scalar human-route thresholds. H045 keeps the human route latent,
but changes its role:

    route is not the selector;
    route is the context that conditions how an upload action is priced.

Known public LB responses are used to learn whether a candidate's movement in
public/transition/private/H042-like regimes is a good or bad action. Candidate
materialization is reused from H043/H044, but the action decoder receives
route-decomposed movement features that H042 did not see.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h045_conditional_route_action_decoder_jepa"
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
Q2_I = TARGETS.index("Q2")
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H043 = "submission_h043_q2_top120_a0.66_c105_ca1478b7_uploadsafe.csv"
H012_LB = 0.5681234831
H042_LB = 0.5679048248


@dataclass(frozen=True)
class RidgeFit:
    feature_set: str
    alpha: float
    cols: list[str]
    intercept: float
    beta: np.ndarray
    mu: np.ndarray
    sd: np.ndarray


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h043 = import_module(HITL / "h043_q2_phase_manifold_jepa.py", "h043_for_h045")
h044 = import_module(HITL / "h044_q2_human_route_split_jepa.py", "h044_for_h045")
h043.OUT = OUT
h043.h042.OUT = OUT
h044.OUT = OUT
h044.h043.OUT = OUT
h044.h042.OUT = OUT
h036 = h043.h036
h042 = h043.h042


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    p = clip_prob(x)
    return np.log(p / (1.0 - p))


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


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    out = sample.copy()
    for i, target in enumerate(TARGETS):
        out[target] = clip_prob(prob[:, i])
    out.to_csv(path, index=False)


def fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    mu = x.mean(axis=0)
    sd = x.std(axis=0)
    sd[sd < 1.0e-9] = 1.0
    z = (x - mu) / sd
    z1 = np.column_stack([np.ones(len(z)), z])
    penalty = np.eye(z1.shape[1]) * float(alpha)
    penalty[0, 0] = 0.0
    coef = np.linalg.solve(z1.T @ z1 + penalty, z1.T @ y)
    return float(coef[0]), coef[1:], mu, sd


def predict_ridge(x: np.ndarray, fit: RidgeFit) -> np.ndarray:
    z = (np.asarray(x, dtype=np.float64) - fit.mu) / fit.sd
    return fit.intercept + z @ fit.beta


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return np.nan
    return float(pd.Series(a).rank().corr(pd.Series(b).rank()))


def pairwise_accuracy(y: np.ndarray, pred: np.ndarray) -> float:
    total = 0
    ok = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            if abs(dy) < 1.0e-12:
                continue
            total += 1
            ok += int(np.sign(dy) == np.sign(pred[i] - pred[j]))
    return float(ok / total) if total else np.nan


def rank01(x: np.ndarray, high_good: bool = True) -> np.ndarray:
    r = pd.Series(np.asarray(x, dtype=np.float64)).rank(method="average", pct=True).to_numpy(dtype=np.float64)
    return r if high_good else 1.0 - r


def load_anchor_probs() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    sample, h012_prob, h042_prob = h043.load_anchor_probs()
    h043_prob = h036.load_sub(ROOT / H043, sample)[TARGETS].to_numpy(dtype=np.float64)
    return sample, h012_prob, h042_prob, h043_prob


def build_route_context(rt: dict[str, object], state: dict[str, np.ndarray], h012_prob: np.ndarray, h042_prob: np.ndarray, h043_prob: np.ndarray) -> pd.DataFrame:
    route = h044.route_scores(rt, state, h042_prob, h043_prob, h012_prob)
    public = route["h044_public_transition_score"].to_numpy(dtype=np.float64)
    private = route["h044_private_routine_score"].to_numpy(dtype=np.float64)
    q2regime = route["h044_public_q2_regime_score"].to_numpy(dtype=np.float64)
    h042like = route["h044_h042_like_score"].to_numpy(dtype=np.float64)
    phase = route["h044_phase_energy_score"].to_numpy(dtype=np.float64)
    route["h045_public_high"] = public >= np.quantile(public, 0.60)
    route["h045_private_high"] = private >= np.quantile(private, 0.60)
    route["h045_private_low"] = private <= np.quantile(private, 0.55)
    route["h045_q2regime_high"] = q2regime >= np.quantile(q2regime, 0.60)
    route["h045_h042like_high"] = h042like >= np.quantile(h042like, 0.60)
    route["h045_phase_high"] = phase >= np.quantile(phase, 0.60)
    route["h045_public_not_private"] = route["h045_public_high"] & route["h045_private_low"]
    route["h045_q2_public_context"] = route["h045_q2regime_high"] & route["h045_public_not_private"]
    route.to_csv(OUT / "h045_route_context.csv", index=False)
    return route


def weighted_stat(x: np.ndarray, w: np.ndarray) -> tuple[float, float, float]:
    w = np.asarray(w, dtype=np.float64)
    if float(w.sum()) <= 1.0e-12:
        return 0.0, 0.0, 0.0
    x = np.asarray(x, dtype=np.float64)
    signed = float(np.sum(x * w) / np.sum(w))
    abs_mean = float(np.sum(np.abs(x) * w) / np.sum(w))
    energy = float(np.sqrt(np.sum((x * w) ** 2) / np.sum(w)))
    return signed, abs_mean, energy


def route_conditional_features(
    prob: np.ndarray,
    h012_prob: np.ndarray,
    h042_prob: np.ndarray,
    h043_prob: np.ndarray,
    route: pd.DataFrame,
    prefix: str = "h045",
) -> dict[str, float]:
    z = logit(prob)
    z012 = logit(h012_prob)
    dz = z - z012
    q2 = dz[:, Q2_I]
    q2_abs = np.abs(q2)
    h042_delta = logit(h042_prob)[:, Q2_I] - z012[:, Q2_I]
    h043_delta = logit(h043_prob)[:, Q2_I] - z012[:, Q2_I]
    phase_score = route["h044_phase_energy_score"].to_numpy(dtype=np.float64)
    public_score = route["h044_public_transition_score"].to_numpy(dtype=np.float64)
    private_score = route["h044_private_routine_score"].to_numpy(dtype=np.float64)
    q2regime_score = route["h044_public_q2_regime_score"].to_numpy(dtype=np.float64)
    h042like_score = route["h044_h042_like_score"].to_numpy(dtype=np.float64)

    masks = {
        "all": np.ones(len(route), dtype=bool),
        "h042": route["h042_q2_support"].to_numpy(dtype=bool),
        "h043": route["h043_q2_support"].to_numpy(dtype=bool),
        "h043_tail": route["h043_q2_support"].to_numpy(dtype=bool) & ~route["h042_q2_support"].to_numpy(dtype=bool),
        "public_high": route["h045_public_high"].to_numpy(dtype=bool),
        "private_high": route["h045_private_high"].to_numpy(dtype=bool),
        "private_low": route["h045_private_low"].to_numpy(dtype=bool),
        "q2regime_high": route["h045_q2regime_high"].to_numpy(dtype=bool),
        "h042like_high": route["h045_h042like_high"].to_numpy(dtype=bool),
        "phase_high": route["h045_phase_high"].to_numpy(dtype=bool),
        "public_not_private": route["h045_public_not_private"].to_numpy(dtype=bool),
        "q2_public_context": route["h045_q2_public_context"].to_numpy(dtype=bool),
    }
    out: dict[str, float] = {}
    out[f"{prefix}_q2_abs_sum"] = float(q2_abs.sum())
    out[f"{prefix}_q2_signed_sum"] = float(q2.sum())
    out[f"{prefix}_q2_changed"] = float(np.sum(q2_abs > 1.0e-7))
    out[f"{prefix}_q2_prob_abs_sum"] = float(np.abs(prob[:, Q2_I] - h012_prob[:, Q2_I]).sum())
    for name, mask in masks.items():
        m = np.asarray(mask, dtype=bool)
        if not np.any(m):
            continue
        out[f"{prefix}_{name}_count"] = float(m.sum())
        out[f"{prefix}_{name}_move_count"] = float(np.sum(q2_abs[m] > 1.0e-7))
        out[f"{prefix}_{name}_move_share"] = float(np.sum(q2_abs[m]) / (q2_abs.sum() + 1.0e-12))
        out[f"{prefix}_{name}_signed_mean"] = float(q2[m].mean())
        out[f"{prefix}_{name}_abs_mean"] = float(q2_abs[m].mean())
        out[f"{prefix}_{name}_energy"] = float(np.sqrt(np.mean(q2[m] ** 2)))
    for name, w in {
        "w_public": public_score,
        "w_private": private_score,
        "w_q2regime": q2regime_score,
        "w_h042like": h042like_score,
        "w_phase": phase_score,
        "w_public_not_private": public_score * (1.0 - private_score),
    }.items():
        signed, abs_mean, energy = weighted_stat(q2, w)
        out[f"{prefix}_{name}_signed"] = signed
        out[f"{prefix}_{name}_abs"] = abs_mean
        out[f"{prefix}_{name}_energy"] = energy

    def cosine(a: np.ndarray, b: np.ndarray, mask: np.ndarray | None = None) -> float:
        if mask is not None:
            a = a[mask]
            b = b[mask]
        denom = float(np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12)
        return float(np.dot(a, b) / denom)

    for name, mask in {"all": None, "h042": masks["h042"], "h043": masks["h043"], "tail": masks["h043_tail"]}.items():
        out[f"{prefix}_{name}_cos_h042"] = cosine(q2, h042_delta, mask)
        out[f"{prefix}_{name}_cos_h043"] = cosine(q2, h043_delta, mask)
    out[f"{prefix}_public_minus_private_abs"] = out[f"{prefix}_w_public_abs"] - out[f"{prefix}_w_private_abs"]
    out[f"{prefix}_q2regime_minus_private_abs"] = out[f"{prefix}_w_q2regime_abs"] - out[f"{prefix}_w_private_abs"]
    out[f"{prefix}_tail_vs_core_share"] = out.get(f"{prefix}_h043_tail_move_share", 0.0) - out.get(f"{prefix}_h042_move_share", 0.0)
    return out


def known_augmented_features(rt: dict[str, object], atoms: list[object], h012_prob: np.ndarray, h042_prob: np.ndarray, h043_prob: np.ndarray, route: pd.DataFrame) -> pd.DataFrame:
    known, _base_scores, _ = h043.known_features_with_h042(rt, atoms, h042_prob)
    rows = []
    for rec in known.to_dict("records"):
        file_name = str(rec["file"])
        if file_name == H042:
            prob = h042_prob
        elif file_name in rt["pred_by_file"]:
            prob = rt["pred_by_file"][file_name]
        else:
            prob = h036.load_sub(file_name, rt["sample"])[TARGETS].to_numpy(dtype=np.float64)
        rows.append({"file": file_name, **route_conditional_features(prob, h012_prob, h042_prob, h043_prob, route)})
    cond = pd.DataFrame(rows)
    out = known.merge(cond, on="file", how="left")
    out.to_csv(OUT / "h045_known_conditional_features.csv", index=False)
    return out


def feature_sets(cols: list[str]) -> dict[str, list[str]]:
    cond = [c for c in cols if c.startswith("h045_")]
    coord = [c for c in cols if c.startswith("coord_")]
    cos = [c for c in cols if c.startswith("cos_")]
    world = [c for c in cols if ("delta" in c or "world" in c or "public" in c or "private" in c or "transition" in c) and not c.startswith("h045_")]
    compact = [c for c in cols if c not in coord and c not in cos]
    return {
        "cond_only": cond,
        "cond_plus_world": cond + world,
        "cond_plus_coords": cond + coord,
        "cond_cos_compact": cond + cos + compact,
    }


def evaluate_decoders(known: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    blocked = {"file", "source", "public_lb", "delta_vs_h012"}
    numeric = [c for c in known.columns if c not in blocked and pd.api.types.is_numeric_dtype(known[c]) and known[c].nunique(dropna=True) > 1]
    y = known["delta_vs_h012"].to_numpy(dtype=np.float64)
    sets = feature_sets(numeric)
    rows = []
    pred_rows = []
    for set_name, cols in sets.items():
        cols = [c for c in cols if c in numeric]
        if len(cols) < 4:
            continue
        x = known[cols].to_numpy(dtype=np.float64)
        for alpha in [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]:
            loo = np.zeros(len(y), dtype=np.float64)
            for i in range(len(y)):
                train = np.ones(len(y), dtype=bool)
                train[i] = False
                intercept, beta, mu, sd = fit_ridge(x[train], y[train], alpha)
                fit = RidgeFit(set_name, alpha, cols, intercept, beta, mu, sd)
                loo[i] = predict_ridge(x[[i]], fit)[0]
            rows.append(
                {
                    "feature_set": set_name,
                    "alpha": alpha,
                    "n_features": len(cols),
                    "loo_mae": float(np.mean(np.abs(loo - y))),
                    "loo_rmse": float(np.sqrt(np.mean((loo - y) ** 2))),
                    "loo_spearman": spearman(y, loo),
                    "loo_pair_acc": pairwise_accuracy(y, loo),
                }
            )
            for file_name, actual, pred in zip(known["file"].astype(str), y, loo):
                pred_rows.append({"file": file_name, "feature_set": set_name, "alpha": alpha, "actual_delta": float(actual), "loo_pred_delta": float(pred)})
    score = pd.DataFrame(rows).sort_values(["loo_mae", "loo_rmse"]).reset_index(drop=True)
    pred = pd.DataFrame(pred_rows)
    score.to_csv(OUT / "h045_conditional_decoder_scores.csv", index=False)
    pred.to_csv(OUT / "h045_conditional_decoder_loo.csv", index=False)
    return score, pred


def load_candidate_pool() -> pd.DataFrame:
    frames = []
    for source, path in [
        ("h043", HITL / "h043_q2_phase_manifold_jepa" / "h043_candidate_scores.csv"),
        ("h044", HITL / "h044_q2_human_route_split_jepa" / "h044_candidate_scores.csv"),
    ]:
        df = pd.read_csv(path)
        df["candidate_source"] = source
        frames.append(df)
    pool = pd.concat(frames, ignore_index=True)
    pool = pool.drop_duplicates("resolved_path", keep="first").reset_index(drop=True)
    pool.to_csv(OUT / "h045_candidate_pool.csv", index=False)
    return pool


def candidate_conditional_features(pool: pd.DataFrame, rt: dict[str, object], atoms: list[object], h012_prob: np.ndarray, h042_prob: np.ndarray, h043_prob: np.ndarray, route: pd.DataFrame) -> pd.DataFrame:
    rows = []
    missing = []
    for rec in pool.to_dict("records"):
        path = Path(str(rec["resolved_path"]))
        if not path.exists():
            missing.append(str(path))
            continue
        prob = h036.load_sub(path, rt["sample"])[TARGETS].to_numpy(dtype=np.float64)
        base = h042.action_features(prob, rt, atoms, str(rec["file"]), "h045_candidate")
        cond = route_conditional_features(prob, h012_prob, h042_prob, h043_prob, route)
        rows.append({"file": str(rec["file"]), "resolved_path": str(path), **base, **cond})
    if missing:
        pd.Series(missing, name="missing_path").to_csv(OUT / "h045_missing_candidate_paths.csv", index=False)
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "h045_candidate_conditional_features.csv", index=False)
    return out


def predict_candidates(known: pd.DataFrame, candidates: pd.DataFrame, decoder_scores: pd.DataFrame) -> pd.DataFrame:
    blocked = {"file", "source", "public_lb", "delta_vs_h012"}
    numeric = [c for c in known.columns if c not in blocked and pd.api.types.is_numeric_dtype(known[c]) and known[c].nunique(dropna=True) > 1]
    sets = feature_sets(numeric)
    top_models = decoder_scores.head(12)
    h012_row = known[known["file"] == H012]
    pre_h042 = known[known["file"] != H042].copy()
    rows = []
    for model in top_models.to_dict("records"):
        cols = [c for c in sets[str(model["feature_set"])] if c in numeric and c in candidates.columns]
        if len(cols) < 4:
            continue
        alpha = float(model["alpha"])
        for tag, train_df in [("full_known", known), ("pre_h042", pre_h042)]:
            x_train = train_df[cols].to_numpy(dtype=np.float64)
            y_train = train_df["delta_vs_h012"].to_numpy(dtype=np.float64)
            intercept, beta, mu, sd = fit_ridge(x_train, y_train, alpha)
            fit = RidgeFit(str(model["feature_set"]), alpha, cols, intercept, beta, mu, sd)
            pred = predict_ridge(candidates[cols].to_numpy(dtype=np.float64), fit)
            h012_pred = float(predict_ridge(h012_row[cols].to_numpy(dtype=np.float64), fit)[0]) if len(h012_row) else 0.0
            for file_name, resolved_path, p in zip(candidates["file"].astype(str), candidates["resolved_path"].astype(str), pred):
                rows.append(
                    {
                        "file": file_name,
                        "resolved_path": resolved_path,
                        "model_tag": tag,
                        "feature_set": str(model["feature_set"]),
                        "alpha": alpha,
                        "pred_delta": float(p),
                        "pred_margin_vs_h012": float(p - h012_pred),
                    }
                )
    raw = pd.DataFrame(rows)
    raw.to_csv(OUT / "h045_candidate_conditional_predictions_long.csv", index=False)
    if raw.empty:
        return pd.DataFrame()
    agg = (
        raw.groupby(["file", "resolved_path", "model_tag"])
        .agg(
            cond_pred_delta_median=("pred_delta", "median"),
            cond_pred_delta_p10=("pred_delta", lambda x: float(np.quantile(x, 0.10))),
            cond_pred_delta_p90=("pred_delta", lambda x: float(np.quantile(x, 0.90))),
            cond_margin_vs_h012_median=("pred_margin_vs_h012", "median"),
            cond_margin_vs_h012_p10=("pred_margin_vs_h012", lambda x: float(np.quantile(x, 0.10))),
            cond_margin_vs_h012_p90=("pred_margin_vs_h012", lambda x: float(np.quantile(x, 0.90))),
            cond_support_better_than_h012=("pred_margin_vs_h012", lambda x: float(np.mean(np.asarray(x) < 0.0))),
            cond_model_count=("pred_margin_vs_h012", "size"),
        )
        .reset_index()
    )
    wide_parts = []
    for tag in ["full_known", "pre_h042"]:
        part = agg[agg["model_tag"] == tag].drop(columns=["model_tag"]).copy()
        wide_parts.append(part.rename(columns={c: f"{tag}_{c}" for c in part.columns if c not in {"file", "resolved_path"}}))
    wide = wide_parts[0]
    for part in wide_parts[1:]:
        wide = wide.merge(part, on=["file", "resolved_path"], how="outer")
    wide.to_csv(OUT / "h045_candidate_conditional_predictions.csv", index=False)
    return wide


def score_candidates(pool: pd.DataFrame, pred: pd.DataFrame) -> pd.DataFrame:
    if pred.empty:
        return pd.DataFrame()
    out = pool.merge(pred, on=["file", "resolved_path"], how="inner")
    full_margin = out["full_known_cond_margin_vs_h012_median"].fillna(0.01)
    pre_margin = out["pre_h042_cond_margin_vs_h012_median"].fillna(0.01)
    action = out.get("pre_h012_action_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    route_delta = out["route_equation_delta_vs_h012"].fillna(0.01)
    h024 = out.get("pre_h012_h024_margin_vs_h012_median", pd.Series(0.01, index=out.index)).fillna(0.01)
    h025 = out.get("h025_score", pd.Series(1.0, index=out.index)).fillna(1.0)
    changed = out["changed_cells_vs_h012"].fillna(999)
    out["h045_conditional_score"] = (
        1.15 * full_margin.rank(method="average", pct=True)
        + 0.55 * pre_margin.rank(method="average", pct=True)
        + 0.70 * action.rank(method="average", pct=True)
        + 0.75 * route_delta.rank(method="average", pct=True)
        + 0.45 * h025.rank(method="average", pct=True)
        + 0.30 * h024.rank(method="average", pct=True)
        + 0.20 * changed.rank(method="average", pct=True)
        - 0.35 * out["full_known_cond_support_better_than_h012"].fillna(0.0)
        - 0.15 * out["pre_h042_cond_support_better_than_h012"].fillna(0.0)
    )
    out["is_current_h043"] = out["file"].astype(str).eq("submission_h043_q2_top120_a0.66_c105_ca1478b7.csv")
    out["h045_promotable"] = (
        (~out["is_current_h043"])
        & (out["changed_cells_vs_h012"] <= 125)
        & (out["full_known_cond_margin_vs_h012_median"] < -0.00008)
        & (out["full_known_cond_support_better_than_h012"] >= 0.58)
        & (out["pre_h042_cond_margin_vs_h012_median"] < 0.00018)
        & (out["route_equation_delta_vs_h012"] < -0.00016)
        & (out["h025_score"] < 0.0)
        & (out["pre_h012_h024_margin_vs_h012_median"] < 0.00090)
    )
    out = out.sort_values(["h045_promotable", "h045_conditional_score", "route_equation_delta_vs_h012"], ascending=[False, True, True]).reset_index(drop=True)
    out.to_csv(OUT / "h045_candidate_scores.csv", index=False)
    return out


def select_and_copy(scored: pd.DataFrame, sample: pd.DataFrame) -> pd.DataFrame:
    if scored.empty:
        return pd.DataFrame([{"decision": "no_candidate", "promote": False, "reason": "no scored candidates"}])
    selected = scored.iloc[0].copy()
    source = Path(str(selected["resolved_path"]))
    candidate_id = str(selected["candidate_id"])
    suffix = candidate_id.rsplit("_", 1)[-1]
    if "q2regime_top75" in candidate_id:
        root_name = f"submission_h045_condroute_q2regime75_a0.66_{suffix}_uploadsafe.csv"
    else:
        safe_id = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in candidate_id)[:88]
        root_name = f"submission_h045_condroute_{safe_id}_uploadsafe.csv"
    root_path = ROOT / root_name
    promote = bool(selected.get("h045_promotable", False))
    if promote:
        prob = h036.load_sub(source, sample)[TARGETS].to_numpy(dtype=np.float64)
        write_submission(sample, prob, root_path)
    dec = {
        "decision": "promote" if promote else "do_not_promote",
        "promote": promote,
        "selected_candidate_id": selected["candidate_id"],
        "selected_file": selected["file"],
        "candidate_source": selected.get("candidate_source", ""),
        "selected_resolved_path": str(source),
        "root_uploadsafe_path": str(root_path) if promote else "",
        "expected_relation": "beats H043 if route-conditioned action pricing fixes Q2 support/amplitude",
        "reason": "conditional route-action decoder gate passed" if promote else "no non-H043 candidate passed H045 conditional gate",
    }
    for col in [
        "changed_cells_vs_h012",
        "full_known_cond_margin_vs_h012_median",
        "full_known_cond_support_better_than_h012",
        "pre_h042_cond_margin_vs_h012_median",
        "pre_h042_cond_support_better_than_h012",
        "pre_h012_action_margin_vs_h012_median",
        "route_equation_delta_vs_h012",
        "pre_h012_h024_margin_vs_h012_median",
        "h025_score",
        "h045_conditional_score",
        "h045_promotable",
    ]:
        dec[col] = selected.get(col, np.nan)
    out = pd.DataFrame([dec])
    out.to_csv(OUT / "h045_decision.csv", index=False)
    return out


def write_report(known_scores: pd.DataFrame, scored: pd.DataFrame, decision: pd.DataFrame) -> None:
    lines = [
        "# H045 Conditional Route-to-Action Decoder HS-JEPA",
        "",
        "## Question",
        "",
        "Can human-state route context price Q2 actions better than scalar route thresholding?",
        "",
        "## Decoder",
        "",
        md_table(known_scores.head(10)),
        "",
        "## Top Candidates",
        "",
        md_table(
            scored[
                [
                    "candidate_id",
                    "candidate_source",
                    "changed_cells_vs_h012",
                    "full_known_cond_margin_vs_h012_median",
                    "full_known_cond_support_better_than_h012",
                    "pre_h042_cond_margin_vs_h012_median",
                    "pre_h012_action_margin_vs_h012_median",
                    "route_equation_delta_vs_h012",
                    "pre_h012_h024_margin_vs_h012_median",
                    "h025_score",
                    "h045_promotable",
                    "h045_conditional_score",
                ]
            ].head(25)
            if not scored.empty
            else scored
        ),
        "",
        "## Decision",
        "",
        md_table(decision),
        "",
        "## Interpretation",
        "",
        "- If promoted, the file is a public sensor for conditional route-to-action pricing, not scalar route gating.",
        "- If not promoted, H044's failure stands: the current route latent is explanatory but not yet an upload-action decoder.",
        "",
    ]
    (OUT / "h045_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    sample, h012_prob, h042_prob, h043_prob = load_anchor_probs()
    rt = h042.rebuild_route_world()
    atoms = h042.build_atoms(rt)
    state = h043.build_q2_phase_state(rt, sample, h012_prob, h042_prob)
    route = build_route_context(rt, state, h012_prob, h042_prob, h043_prob)
    known = known_augmented_features(rt, atoms, h012_prob, h042_prob, h043_prob, route)
    decoder_scores, _decoder_loo = evaluate_decoders(known)
    pool = load_candidate_pool()
    cand_features = candidate_conditional_features(pool, rt, atoms, h012_prob, h042_prob, h043_prob, route)
    pred = predict_candidates(known, cand_features, decoder_scores)
    scored = score_candidates(pool, pred)
    decision = select_and_copy(scored, sample)
    write_report(decoder_scores, scored, decision)
    print("H045 selected:", decision.iloc[0]["selected_candidate_id"])
    print("H045 decision:", decision.iloc[0]["decision"])
    print("H045 reason:", decision.iloc[0]["reason"])


if __name__ == "__main__":
    main()
