#!/usr/bin/env python3
"""H149: bundle-listener route translator HS-JEPA.

H148 showed that full cell-level listener recovery is underdetermined: the
frontier-only equation can explain H057/H088/H144/H145 locally but collapses to
a tiny 22-cell action.  H149 moves the listener target representation up one
level, from cells to human-state bundles:

    target / subject / row-order / weekday / pay-window / base-probability route

Each public observation is represented by signed logit movement summed over
these bundles.  The learned bundle coefficients are then projected back to
row-target gradients and used as a listener-aware route decoder over multiple
HS-JEPA action proposals.
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


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h149_bundle_listener_route_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H148_PATH = HITL / "h148_listener_responsibility_equation_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h148mod_h149", H148_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H148_PATH}")
h148mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h148mod
SPEC.loader.exec_module(h148mod)

h085mod = h148mod.h085mod
TARGETS = h148mod.TARGETS
KEYS = h148mod.KEYS
BASE_FILE = h148mod.BASE_FILE
BASE_LB = h148mod.BASE_LB
EPS = h148mod.EPS
TOL = h148mod.TOL


@dataclass(frozen=True)
class BundleFeature:
    name: str
    indices: np.ndarray
    family: str


SOURCE_FILES = [
    "submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv",
    "submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv",
    "submission_h074_antishortcut_inversion_816703df_uploadsafe.csv",
    "submission_h075_antibad_transport_f6863945_uploadsafe.csv",
    "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv",
]


def locate(name: str | Path) -> Path | None:
    return h085mod.locate(name)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(x)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(values, high=high)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h149_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h149_bundle_listener_*.csv"):
        path.unlink()


def load_sub(path: Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return h085mod.load_sub(path, sample)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    h085mod.write_submission(sample, prob, path)


def validate_submission(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> dict[str, object]:
    return h085mod.validate_submission(path, sample, base_prob)


def movement_from_file(path: Path, sample: pd.DataFrame, base_prob: np.ndarray) -> np.ndarray:
    prob = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
    return (logit(prob) - logit(base_prob)).reshape(-1)


def flat_indices(rows: np.ndarray, targets: np.ndarray) -> np.ndarray:
    return rows * len(TARGETS) + targets


def add_feature(features: list[BundleFeature], name: str, family: str, mask: np.ndarray) -> None:
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return
    features.append(BundleFeature(name=name, family=family, indices=idx.astype(int)))


def build_bundle_features(sample: pd.DataFrame, base_prob: np.ndarray) -> list[BundleFeature]:
    n_rows, n_targets = base_prob.shape
    row_grid = np.repeat(np.arange(n_rows), n_targets)
    target_grid = np.tile(np.arange(n_targets), n_rows)
    base_flat = base_prob.reshape(-1)
    subject = sample["subject_id"].astype(str).to_numpy()
    subject_grid = np.repeat(subject, n_targets)
    sleep = pd.to_datetime(sample["sleep_date"])
    lifelog = pd.to_datetime(sample["lifelog_date"])
    dow = lifelog.dt.dayofweek.to_numpy()
    day = lifelog.dt.day.to_numpy()
    month = lifelog.dt.month.to_numpy()
    dow_grid = np.repeat(dow, n_targets)
    day_grid = np.repeat(day, n_targets)
    month_grid = np.repeat(month, n_targets)
    row_decile = pd.Series(np.arange(n_rows)).rank(pct=True).mul(10).astype(int).clip(0, 9).to_numpy()
    row_decile_grid = np.repeat(row_decile, n_targets)
    row_quintile = pd.Series(np.arange(n_rows)).rank(pct=True).mul(5).astype(int).clip(0, 4).to_numpy()
    row_quintile_grid = np.repeat(row_quintile, n_targets)

    weekend = dow >= 5
    friday = dow == 4
    monday = dow == 0
    pay25 = np.abs(day - 25) <= 1
    pay10 = np.abs(day - 10) <= 1
    month_end = day >= 28
    month_start = day <= 3
    date_flags = {
        "weekend": np.repeat(weekend, n_targets),
        "friday": np.repeat(friday, n_targets),
        "monday": np.repeat(monday, n_targets),
        "pay25_window": np.repeat(pay25, n_targets),
        "pay10_window": np.repeat(pay10, n_targets),
        "month_end": np.repeat(month_end, n_targets),
        "month_start": np.repeat(month_start, n_targets),
    }

    features: list[BundleFeature] = []
    add_feature(features, "all", "global", np.ones(n_rows * n_targets, dtype=bool))

    q_mask = target_grid <= 2
    s_mask = target_grid >= 3
    add_feature(features, "target_group=Q", "target_group", q_mask)
    add_feature(features, "target_group=S", "target_group", s_mask)

    for tidx, target in enumerate(TARGETS):
        tmask = target_grid == tidx
        add_feature(features, f"target={target}", "target", tmask)
        for sid in sorted(set(subject)):
            add_feature(features, f"subject={sid}|target={target}", "subject_target", tmask & (subject_grid == sid))
        for decile in range(10):
            add_feature(features, f"row_decile={decile}|target={target}", "row_order_target", tmask & (row_decile_grid == decile))

    for sid in sorted(set(subject)):
        smask = subject_grid == sid
        add_feature(features, f"subject={sid}|Q", "subject_group", smask & q_mask)
        add_feature(features, f"subject={sid}|S", "subject_group", smask & s_mask)

    for decile in range(10):
        dmask = row_decile_grid == decile
        add_feature(features, f"row_decile={decile}|Q", "row_order_group", dmask & q_mask)
        add_feature(features, f"row_decile={decile}|S", "row_order_group", dmask & s_mask)

    for quintile in range(5):
        qmask = row_quintile_grid == quintile
        add_feature(features, f"row_quintile={quintile}", "row_order", qmask)

    for name, flag_grid in date_flags.items():
        add_feature(features, f"{name}|Q", "human_social_date", flag_grid & q_mask)
        add_feature(features, f"{name}|S", "human_social_date", flag_grid & s_mask)
        for tidx, target in enumerate(TARGETS):
            add_feature(features, f"{name}|target={target}", "human_social_date_target", flag_grid & (target_grid == tidx))

    for month_value in sorted(set(month)):
        mmask = month_grid == month_value
        add_feature(features, f"month={month_value}|Q", "month_group", mmask & q_mask)
        add_feature(features, f"month={month_value}|S", "month_group", mmask & s_mask)

    # Base-probability regimes are a compact proxy for target confidence/tail risk.
    for tidx, target in enumerate(TARGETS):
        tmask = target_grid == tidx
        vals = base_flat[tmask]
        quant = pd.Series(vals).rank(method="average", pct=True).to_numpy()
        target_indices = np.flatnonzero(tmask)
        for bin_id, lo, hi in [
            (0, 0.0, 0.20),
            (1, 0.20, 0.40),
            (2, 0.40, 0.60),
            (3, 0.60, 0.80),
            (4, 0.80, 1.01),
        ]:
            idx = target_indices[(quant >= lo) & (quant < hi)]
            if len(idx):
                features.append(BundleFeature(name=f"baseq={bin_id}|target={target}", family="base_prob_target", indices=idx.astype(int)))
        add_feature(features, f"base_high|target={target}", "base_prob_tail", tmask & (base_flat >= np.quantile(vals, 0.80)))
        add_feature(features, f"base_low|target={target}", "base_prob_tail", tmask & (base_flat <= np.quantile(vals, 0.20)))

    # Remove exact duplicate index sets while keeping the first semantic name.
    seen = set()
    unique: list[BundleFeature] = []
    for feat in features:
        key = tuple(feat.indices.tolist())
        if key in seen:
            continue
        seen.add(key)
        unique.append(feat)
    return unique


def feature_matrix(moves: dict[str, np.ndarray], names: list[str], features: list[BundleFeature]) -> tuple[np.ndarray, np.ndarray]:
    x = np.zeros((len(names), len(features)), dtype=np.float64)
    for i, name in enumerate(names):
        move = moves[name]
        for j, feat in enumerate(features):
            x[i, j] = float(move[feat.indices].sum())
    scale = np.std(x, axis=0)
    scale = np.where(scale < 1.0e-9, 1.0, scale)
    return x / scale, scale


def dual_ridge_coef(x_train: np.ndarray, y_train: np.ndarray, alpha: float) -> np.ndarray:
    k = x_train @ x_train.T
    dual = np.linalg.solve(k + alpha * np.eye(k.shape[0]), y_train)
    return x_train.T @ dual


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = pd.Series(a).rank(method="average").to_numpy(dtype=np.float64)
    rb = pd.Series(b).rank(method="average").to_numpy(dtype=np.float64)
    if np.std(ra) < 1.0e-12 or np.std(rb) < 1.0e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def loo_score(x: np.ndarray, y: np.ndarray, names: list[str], alpha: float) -> tuple[dict[str, float], list[dict[str, object]]]:
    preds = []
    actuals = []
    rows = []
    for i, name in enumerate(names):
        if name == BASE_FILE:
            continue
        mask = np.ones(len(y), dtype=bool)
        mask[i] = False
        coef = dual_ridge_coef(x[mask], y[mask], alpha)
        pred = float(x[i] @ coef)
        actual = float(y[i])
        preds.append(pred)
        actuals.append(actual)
        rows.append({"heldout": name, "actual_delta": actual, "pred_delta": pred, "error": pred - actual})
    err = np.asarray(preds) - np.asarray(actuals)
    metrics = {
        "loo_mae": float(np.mean(np.abs(err))) if len(err) else float("nan"),
        "loo_rmse": float(np.sqrt(np.mean(err * err))) if len(err) else float("nan"),
        "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)) if len(err) else float("nan"),
        "loo_spearman": spearman(np.asarray(preds), np.asarray(actuals)) if len(err) else float("nan"),
    }
    return metrics, rows


def fit_bundle_models(
    obs: pd.DataFrame,
    moves: dict[str, np.ndarray],
    features: list[BundleFeature],
) -> tuple[pd.DataFrame, dict[str, dict[str, object]]]:
    specs = {
        "bundle_frontier": obs[obs["role"].isin(["frontier", "frontier_basin", "breakthrough_anchor", "negative_sensor", "tie_sensor"])].copy(),
        "bundle_plus_bad": obs[obs["role"].isin(["frontier", "frontier_basin", "breakthrough_anchor", "negative_sensor", "tie_sensor", "bad_anchor"])].copy(),
        "bundle_all": obs.copy(),
    }
    alphas = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]
    score_rows = []
    loo_rows = []
    fitted: dict[str, dict[str, object]] = {}
    h144 = "submission_h144_targetxor_def80b88_uploadsafe.csv"
    h145 = "submission_h145_q3repair_2d818e46_uploadsafe.csv"
    for model_name, frame in specs.items():
        names = frame["file"].astype(str).tolist()
        x, scale = feature_matrix(moves, names, features)
        y = frame["delta_vs_h057"].to_numpy(dtype=np.float64)
        model_scores = []
        for alpha in alphas:
            metrics, rows = loo_score(x, y, names, alpha)
            coef = dual_ridge_coef(x, y, alpha)
            h144_x, _ = feature_matrix(moves, [h144], features)
            h145_x, _ = feature_matrix(moves, [h145], features)
            # feature_matrix([single]) would scale with std=0, so build with
            # current model scale explicitly.
            h144_raw = raw_feature_vector(moves[h144], features) / scale
            h145_raw = raw_feature_vector(moves[h145], features) / scale
            tie_gap = abs(float(h144_raw @ coef) - float(h145_raw @ coef))
            spearman_penalty = max(0.0, -float(metrics["loo_spearman"])) * 0.001 if not np.isnan(metrics["loo_spearman"]) else 0.001
            selection_score = float(metrics["loo_mae"] + 12.0 * tie_gap + spearman_penalty)
            rec = {
                "model": model_name,
                "alpha": float(alpha),
                "n_obs": int(len(frame)),
                "n_features": int(len(features)),
                **metrics,
                "h144_h145_pred_gap_abs": float(tie_gap),
                "selection_score": selection_score,
            }
            score_rows.append(rec)
            model_scores.append(rec)
            for row in rows:
                loo_rows.append({"model": model_name, "alpha": float(alpha), **row})
        best = pd.DataFrame(model_scores).sort_values(["selection_score", "loo_mae"]).iloc[0]
        best_alpha = float(best["alpha"])
        coef = dual_ridge_coef(x, y, best_alpha)
        fitted[model_name] = {"coef": coef, "scale": scale, "names": names, "x": x, "y": y, "alpha": best_alpha}
    pd.DataFrame(loo_rows).to_csv(OUT / "h149_loo_predictions.csv", index=False)
    return pd.DataFrame(score_rows).sort_values(["selection_score", "loo_mae"]).reset_index(drop=True), fitted


def raw_feature_vector(move: np.ndarray, features: list[BundleFeature]) -> np.ndarray:
    return np.asarray([float(move[feat.indices].sum()) for feat in features], dtype=np.float64)


def cell_gradient(coef: np.ndarray, scale: np.ndarray, features: list[BundleFeature], n_cells: int) -> np.ndarray:
    grad = np.zeros(n_cells, dtype=np.float64)
    adj = coef / scale
    for c, feat in zip(adj, features):
        grad[feat.indices] += c
    return grad


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1.0e-12 or nb < 1.0e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def candidate_metrics(
    file_name: str,
    path: Path,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    features: list[BundleFeature],
    fitted: dict[str, dict[str, object]],
    moves: dict[str, np.ndarray],
) -> dict[str, object]:
    move = movement_from_file(path, sample, base_prob)
    h088 = moves.get("submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv", np.zeros_like(move))
    changed = np.abs(move) > TOL
    out: dict[str, object] = {
        "file": file_name,
        "resolved_path": str(path.resolve()),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(len(set(np.where(changed)[0] // len(TARGETS)))),
        "move_l1": float(np.abs(move).sum()),
        "move_l2": float(np.linalg.norm(move)),
        "h088_move_cosine": cosine(move, h088),
    }
    raw = raw_feature_vector(move, features)
    for model_name, obj in fitted.items():
        coef = obj["coef"]
        scale = obj["scale"]
        grad = cell_gradient(coef, scale, features, len(move))
        toxicity = grad * move
        out[f"{model_name}_pred_delta"] = float((raw / scale) @ coef)
        out[f"{model_name}_benefit_sum"] = float(np.maximum(-toxicity, 0.0).sum())
        out[f"{model_name}_toxicity_sum"] = float(np.maximum(toxicity, 0.0).sum())
        out[f"{model_name}_high_toxic_cells"] = int((changed & (rank01(np.abs(grad), high=True) >= 0.90) & (toxicity > 0)).sum())
        out[f"{model_name}_high_benefit_cells"] = int((changed & (rank01(np.abs(grad), high=True) >= 0.90) & (toxicity < 0)).sum())
    return out


def build_multisource_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    features: list[BundleFeature],
    fitted: dict[str, dict[str, object]],
    moves: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    base_flat = base_prob.reshape(-1)
    n_cells = len(base_flat)
    h088 = moves.get("submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv", np.zeros(n_cells))
    primary_name = "bundle_all" if "bundle_all" in fitted else list(fitted)[0]
    secondary_name = "bundle_plus_bad" if "bundle_plus_bad" in fitted else primary_name
    frontier_name = "bundle_frontier" if "bundle_frontier" in fitted else primary_name
    gradients = {
        name: cell_gradient(obj["coef"], obj["scale"], features, n_cells)
        for name, obj in fitted.items()
    }
    primary_grad = gradients[primary_name]
    secondary_grad = gradients[secondary_name]
    frontier_grad = gradients[frontier_name]

    source_rows = []
    for source_name in SOURCE_FILES:
        path = locate(source_name)
        if path is None:
            continue
        try:
            source_prob = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        except Exception:
            continue
        source_flat = source_prob.reshape(-1)
        move = logit(source_flat) - logit(base_flat)
        changed = np.abs(move) > TOL
        benefit_primary = -primary_grad * move
        benefit_secondary = -secondary_grad * move
        benefit_frontier = -frontier_grad * move
        h088_penalty = ((move * h088) > 0).astype(float) * rank01(np.abs(h088), high=True)
        score = (
            rank01(benefit_primary, high=True)
            + 0.55 * rank01(benefit_secondary, high=True)
            + 0.30 * rank01(benefit_frontier, high=True)
            + 0.25 * rank01(np.abs(move), high=True)
            - 0.55 * h088_penalty
            - 1.60 * (benefit_primary < 0).astype(float)
            - 0.80 * (benefit_secondary < 0).astype(float)
        )
        for flat_idx in np.flatnonzero(changed):
            row_idx = flat_idx // len(TARGETS)
            target_idx = flat_idx % len(TARGETS)
            source_rows.append(
                {
                    "source_file": source_name,
                    "row": int(row_idx),
                    "subject_id": sample.loc[row_idx, "subject_id"],
                    "sleep_date": sample.loc[row_idx, "sleep_date"],
                    "lifelog_date": sample.loc[row_idx, "lifelog_date"],
                    "target_index": int(target_idx),
                    "target": TARGETS[target_idx],
                    "flat_idx": int(flat_idx),
                    "h057_prob": float(base_flat[flat_idx]),
                    "source_prob": float(source_flat[flat_idx]),
                    "source_move": float(move[flat_idx]),
                    "primary_grad": float(primary_grad[flat_idx]),
                    "secondary_grad": float(secondary_grad[flat_idx]),
                    "frontier_grad": float(frontier_grad[flat_idx]),
                    "benefit_primary": float(benefit_primary[flat_idx]),
                    "benefit_secondary": float(benefit_secondary[flat_idx]),
                    "benefit_frontier": float(benefit_frontier[flat_idx]),
                    "h088_same_direction": bool((move[flat_idx] * h088[flat_idx]) > 0),
                    "h088_penalty": float(h088_penalty[flat_idx]),
                    "score": float(score[flat_idx]),
                }
            )
    all_cells = pd.DataFrame(source_rows)
    if all_cells.empty:
        raise RuntimeError("no source action cells available")
    all_cells = all_cells.sort_values(
        ["flat_idx", "score", "benefit_primary", "benefit_secondary"],
        ascending=[True, False, False, False],
    ).drop_duplicates("flat_idx", keep="first")

    all_cells["passes_gate"] = (
        (all_cells["benefit_primary"] > 0)
        & (all_cells["benefit_secondary"] > 0)
        & (all_cells["score"] >= all_cells["score"].quantile(0.55))
        & (all_cells["h088_penalty"] <= 0.97)
    )
    ranked = all_cells[all_cells["passes_gate"]].sort_values("score", ascending=False).copy()
    if len(ranked) < 180:
        ranked = all_cells[(all_cells["benefit_primary"] > 0) & (all_cells["score"] >= all_cells["score"].quantile(0.48))].sort_values("score", ascending=False).copy()

    selected_rows = []
    per_subject: dict[str, int] = {}
    per_target: dict[str, int] = {}
    per_row: dict[int, int] = {}
    max_cells = 460
    max_rows = 165
    max_per_subject = 115
    max_per_target = 105
    max_per_row = 5
    for rec in ranked.to_dict("records"):
        if len(selected_rows) >= max_cells:
            break
        row = int(rec["row"])
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        if len({int(x["row"]) for x in selected_rows}) >= max_rows and row not in per_row:
            continue
        if per_subject.get(subject, 0) >= max_per_subject:
            continue
        if per_target.get(target, 0) >= max_per_target:
            continue
        if per_row.get(row, 0) >= max_per_row:
            continue
        selected_rows.append(rec)
        per_subject[subject] = per_subject.get(subject, 0) + 1
        per_target[target] = per_target.get(target, 0) + 1
        per_row[row] = per_row.get(row, 0) + 1

    selected = pd.DataFrame(selected_rows)
    new_flat = base_flat.copy()
    if not selected.empty:
        idx = selected["flat_idx"].to_numpy(dtype=int)
        move = selected["source_move"].to_numpy(dtype=np.float64)
        # Bundle listener is a bigger structural bet than H148, but still keeps
        # amplitude below a full source copy to avoid action toxicity tails.
        amp = 0.68
        new_flat[idx] = sigmoid(logit(base_flat[idx]) + amp * move)
        selected["amp"] = amp
        selected["new_prob"] = new_flat[idx]
    return all_cells.sort_values("score", ascending=False).reset_index(drop=True), selected, new_flat.reshape(base_prob.shape)


def run() -> None:
    cleanup_previous_outputs()
    base_path = locate(BASE_FILE)
    if base_path is None:
        raise FileNotFoundError(BASE_FILE)
    sample = load_sub(base_path)
    base_prob = sample[TARGETS].to_numpy(dtype=np.float64)
    obs = h148mod.collect_public_observations(sample)
    moves = {row["file"]: movement_from_file(Path(row["resolved_path"]), sample, base_prob) for row in obs.to_dict("records")}
    features = build_bundle_features(sample, base_prob)
    feature_frame = pd.DataFrame([{"feature": f.name, "family": f.family, "n_cells": len(f.indices)} for f in features])
    feature_frame.to_csv(OUT / "h149_bundle_features.csv", index=False)
    obs.to_csv(OUT / "h149_public_observations_used.csv", index=False)

    model_scores, fitted = fit_bundle_models(obs, moves, features)
    model_scores.to_csv(OUT / "h149_model_scores.csv", index=False)
    best_model = str(model_scores.iloc[0]["model"])

    candidate_rows = []
    for file_name in h148mod.CANDIDATE_FILES:
        path = locate(file_name)
        if path is None:
            continue
        try:
            load_sub(path, sample)
        except Exception:
            continue
        candidate_rows.append(candidate_metrics(file_name, path, sample, base_prob, features, fitted, moves))
    candidate_scores = pd.DataFrame(candidate_rows).sort_values(f"{best_model}_pred_delta").reset_index(drop=True)
    candidate_scores.to_csv(OUT / "h149_candidate_scores.csv", index=False)

    all_source_cells, selected, new_prob = build_multisource_candidate(sample, base_prob, features, fitted, moves)
    all_source_cells.to_csv(OUT / "h149_source_cell_scores.csv", index=False)
    selected.to_csv(OUT / "h149_selected_cells.csv", index=False)

    hash_id = short_hash(new_prob)
    local_path = OUT / f"submission_h149_bundle_listener_route_{hash_id}.csv"
    root_path = ROOT / f"submission_h149_bundle_listener_route_{hash_id}_uploadsafe.csv"
    write_submission(sample, new_prob, local_path)
    shutil.copyfile(local_path, root_path)
    validation = validate_submission(root_path, sample, base_prob)
    h149_metrics = candidate_metrics(str(root_path.name), root_path, sample, base_prob, features, fitted, moves)

    observed_fit = []
    for row in obs.to_dict("records"):
        raw = raw_feature_vector(moves[row["file"]], features)
        rec = {"file": row["file"], "role": row["role"], "actual_delta": float(row["delta_vs_h057"])}
        for name, obj in fitted.items():
            rec[f"{name}_fit_delta"] = float((raw / obj["scale"]) @ obj["coef"])
            rec[f"{name}_fit_error"] = rec[f"{name}_fit_delta"] - rec["actual_delta"]
        observed_fit.append(rec)
    observed_fit_df = pd.DataFrame(observed_fit)
    observed_fit_df.to_csv(OUT / "h149_observed_fit.csv", index=False)

    decision = {
        "candidate_file": str(root_path.name),
        "candidate_path": str(root_path.resolve()),
        "best_bundle_model": best_model,
        "selected_cells": int(len(selected)),
        "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
        "selected_source_mix": selected["source_file"].value_counts().to_dict() if not selected.empty else {},
        "selected_target_mix": selected["target"].value_counts().to_dict() if not selected.empty else {},
        "worldview": (
            "Listener responsibility is not recoverable safely at individual-cell "
            "resolution, but may be recoverable as human-state bundles over "
            "target, subject, row-order, weekend/pay-window, and base-probability regimes."
        ),
        "failure_interpretation": (
            "If this fails, route-bundle listener inversion is still too weak; the "
            "translator must move from supervised public equations to discrete "
            "row-target assignment constraints or new public sensors."
        ),
        **{f"validation_{k}": v for k, v in validation.items()},
        **{f"metric_{k}": v for k, v in h149_metrics.items() if k not in ["file", "resolved_path"]},
    }
    pd.DataFrame([decision]).to_csv(OUT / "h149_decision.csv", index=False)

    top_features = []
    for name, obj in fitted.items():
        coef = obj["coef"]
        scale = obj["scale"]
        for feat, c, s in zip(features, coef, scale):
            top_features.append({"model": name, "feature": feat.name, "family": feat.family, "coef_per_unit": float(c / s), "coef": float(c), "scale": float(s), "n_cells": len(feat.indices)})
    top_features_df = pd.DataFrame(top_features).sort_values("coef_per_unit", key=lambda x: np.abs(x), ascending=False)
    top_features_df.to_csv(OUT / "h149_bundle_coefficients.csv", index=False)

    report = f"""# H149 Bundle-Listener Route HS-JEPA

Date: 2026-06-03

## Question

H148 recovered a cell-level listener, but it collapsed to a tiny action. H149
tests a stronger HS-JEPA claim:

```text
the public/private listener is a human-state bundle field, not an isolated
cell field.
```

Bundles include target, subject, row-order, weekend/friday/monday, pay-window,
month boundary, month, and H057 base-probability regimes.

## Public Observations Used

{md_table(obs[["file", "public_lb", "delta_vs_h057", "role"]], 30)}

## Bundle Model Selection

{md_table(model_scores.head(24), 24)}

Chosen model by selection score: `{best_model}`.

## Observed Fit

{md_table(observed_fit_df[["file", "role", "actual_delta", f"{best_model}_fit_delta", f"{best_model}_fit_error"]].sort_values("actual_delta"), 30)}

## Candidate Stress Ranking

{md_table(candidate_scores[["file", "changed_cells_vs_h057", "changed_rows_vs_h057", "h088_move_cosine", f"{best_model}_pred_delta", f"{best_model}_high_toxic_cells", f"{best_model}_high_benefit_cells"]], 30)}

## Strongest Bundle Coefficients

{md_table(top_features_df.head(30), 30)}

## Promoted Diagnostic Candidate

{md_table(pd.DataFrame([decision]), 1)}

Source mix:

{md_table(selected["source_file"].value_counts().rename_axis("source_file").reset_index(name="cells") if not selected.empty else pd.DataFrame(), 10)}

Target mix:

{md_table(selected["target"].value_counts().rename_axis("target").reset_index(name="cells") if not selected.empty else pd.DataFrame(), 10)}

## Interpretation

H149 is the first direct row-target correction translator that uses all three
current HS-JEPA pieces together:

```text
human-social/date/subject/route context -> bundle listener
multi-source action proposal -> listener-aware row-target assignment
anti-shortcut/H088 penalty -> correction field
```

If H149-style candidates look public-negative offline, that is strong evidence
that H071/H073/H074 are not missing only a small alpha.  They need a different
assignment equation.  If they look public-positive, this becomes the next
candidate family to probe when submission slots return.
"""
    (OUT / "h149_report.md").write_text(report, encoding="utf-8")

    print(f"H149 best bundle model: {best_model}")
    print(f"H149 candidate: {root_path}")
    print(f"selected cells: {len(selected)}")
    print(candidate_scores[["file", f"{best_model}_pred_delta", "changed_cells_vs_h057"]].head(14).to_string(index=False))


if __name__ == "__main__":
    run()
