#!/usr/bin/env python3
"""H150: bundle-listener stress and robust translator HS-JEPA.

H149 produced a large bundle-listener candidate, but its largest upside came
from the all-observed public equation.  H150 asks whether that equation is a
real listener representation or an old-anchor shortcut.

Stress tests:

1. role holdout: train without each public-observation role and predict it;
2. feature-family ablation: remove subject/order/human-social/base regimes;
3. null permutation: compare real LOO/ranking against shuffled public deltas;
4. random feature dropout: check candidate sign stability.

The promoted H150 candidate is built only from source-action cells that have
positive benefit under multiple bundle-listener variants.
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
OUT = HITL / "h150_bundle_listener_stress_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H149_PATH = HITL / "h149_bundle_listener_route_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h149mod_h150", H149_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H149_PATH}")
h149mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h149mod
SPEC.loader.exec_module(h149mod)

h148mod = h149mod.h148mod
h085mod = h149mod.h085mod
TARGETS = h149mod.TARGETS
BASE_FILE = h149mod.BASE_FILE
BASE_LB = h149mod.BASE_LB
TOL = h149mod.TOL


@dataclass(frozen=True)
class VariantSpec:
    name: str
    roles_include: tuple[str, ...] | None = None
    roles_exclude: tuple[str, ...] = ()
    family_keep: tuple[str, ...] | None = None
    family_drop: tuple[str, ...] = ()
    description: str = ""


ALPHAS = [0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]
CORE_SOURCE_FILES = h149mod.SOURCE_FILES
H149_FILE = "submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv"


def locate(name: str | Path) -> Path | None:
    return h085mod.locate(name)


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
    for path in OUT.glob("submission_h150_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h150_robust_bundle_listener_*.csv"):
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


def select_features(features: list[h149mod.BundleFeature], spec: VariantSpec) -> list[h149mod.BundleFeature]:
    out = []
    for feat in features:
        if spec.family_keep is not None and feat.family not in spec.family_keep:
            continue
        if feat.family in spec.family_drop:
            continue
        out.append(feat)
    if not out:
        raise RuntimeError(f"variant {spec.name} selected no features")
    return out


def select_obs(obs: pd.DataFrame, spec: VariantSpec) -> pd.DataFrame:
    frame = obs.copy()
    if spec.roles_include is not None:
        frame = frame[frame["role"].isin(spec.roles_include)].copy()
    if spec.roles_exclude:
        frame = frame[~frame["role"].isin(spec.roles_exclude)].copy()
    if BASE_FILE not in set(frame["file"].astype(str)):
        base = obs[obs["file"].eq(BASE_FILE)]
        frame = pd.concat([base, frame], ignore_index=True).drop_duplicates("file", keep="first")
    return frame.sort_values(["public_lb", "file"]).reset_index(drop=True)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = pd.Series(a).rank(method="average").to_numpy(dtype=np.float64)
    rb = pd.Series(b).rank(method="average").to_numpy(dtype=np.float64)
    if np.std(ra) < 1.0e-12 or np.std(rb) < 1.0e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def loo_metrics(x: np.ndarray, y: np.ndarray, names: list[str], alpha: float) -> tuple[dict[str, float], list[dict[str, object]]]:
    preds = []
    actuals = []
    rows = []
    for i, name in enumerate(names):
        if name == BASE_FILE:
            continue
        mask = np.ones(len(y), dtype=bool)
        mask[i] = False
        coef = h149mod.dual_ridge_coef(x[mask], y[mask], alpha)
        pred = float(x[i] @ coef)
        actual = float(y[i])
        preds.append(pred)
        actuals.append(actual)
        rows.append({"heldout": name, "actual_delta": actual, "pred_delta": pred, "error": pred - actual})
    err = np.asarray(preds) - np.asarray(actuals)
    return (
        {
            "loo_mae": float(np.mean(np.abs(err))) if len(err) else float("nan"),
            "loo_rmse": float(np.sqrt(np.mean(err * err))) if len(err) else float("nan"),
            "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)) if len(err) else float("nan"),
            "loo_spearman": spearman(np.asarray(preds), np.asarray(actuals)) if len(err) else float("nan"),
        },
        rows,
    )


def fit_variant(
    obs: pd.DataFrame,
    moves: dict[str, np.ndarray],
    features: list[h149mod.BundleFeature],
    spec: VariantSpec,
) -> dict[str, object]:
    frame = select_obs(obs, spec)
    feats = select_features(features, spec)
    names = frame["file"].astype(str).tolist()
    x, scale = h149mod.feature_matrix(moves, names, feats)
    y = frame["delta_vs_h057"].to_numpy(dtype=np.float64)
    h144 = "submission_h144_targetxor_def80b88_uploadsafe.csv"
    h145 = "submission_h145_q3repair_2d818e46_uploadsafe.csv"
    score_rows = []
    detail_rows = []
    for alpha in ALPHAS:
        metrics, rows = loo_metrics(x, y, names, alpha)
        coef = h149mod.dual_ridge_coef(x, y, alpha)
        h144_raw = h149mod.raw_feature_vector(moves[h144], feats) / scale
        h145_raw = h149mod.raw_feature_vector(moves[h145], feats) / scale
        tie_gap = abs(float(h144_raw @ coef) - float(h145_raw @ coef))
        spearman_penalty = max(0.0, -float(metrics["loo_spearman"])) * 0.001 if not np.isnan(metrics["loo_spearman"]) else 0.001
        selection_score = float(metrics["loo_mae"] + 12.0 * tie_gap + spearman_penalty)
        score_rows.append(
            {
                "variant": spec.name,
                "alpha": float(alpha),
                "n_obs": int(len(frame)),
                "n_features": int(len(feats)),
                **metrics,
                "h144_h145_pred_gap_abs": float(tie_gap),
                "selection_score": selection_score,
            }
        )
        for row in rows:
            detail_rows.append({"variant": spec.name, "alpha": float(alpha), **row})
    scores = pd.DataFrame(score_rows).sort_values(["selection_score", "loo_mae"]).reset_index(drop=True)
    best = scores.iloc[0]
    coef = h149mod.dual_ridge_coef(x, y, float(best["alpha"]))
    return {
        "spec": spec,
        "frame": frame,
        "features": feats,
        "names": names,
        "x": x,
        "y": y,
        "scale": scale,
        "coef": coef,
        "scores": scores,
        "loo_detail": pd.DataFrame(detail_rows),
        "best": best.to_dict(),
    }


def predict_move(move: np.ndarray, model: dict[str, object]) -> float:
    raw = h149mod.raw_feature_vector(move, model["features"]) / model["scale"]
    return float(raw @ model["coef"])


def gradient(model: dict[str, object], n_cells: int) -> np.ndarray:
    return h149mod.cell_gradient(model["coef"], model["scale"], model["features"], n_cells)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return h149mod.cosine(a, b)


def role_holdout(
    obs: pd.DataFrame,
    moves: dict[str, np.ndarray],
    features: list[h149mod.BundleFeature],
) -> pd.DataFrame:
    rows = []
    roles = [r for r in sorted(obs["role"].unique()) if r != "frontier"]
    for role in roles:
        spec = VariantSpec(name=f"holdout_role={role}", roles_exclude=(role,), description=f"train without {role}")
        model = fit_variant(obs, moves, features, spec)
        holdout = obs[obs["role"].eq(role)].copy()
        for rec in holdout.to_dict("records"):
            move = moves[str(rec["file"])]
            pred = predict_move(move, model)
            actual = float(rec["delta_vs_h057"])
            rows.append(
                {
                    "heldout_role": role,
                    "file": rec["file"],
                    "actual_delta": actual,
                    "pred_delta": pred,
                    "error": pred - actual,
                    "train_n_obs": int(len(model["frame"])),
                    "best_alpha": float(model["best"]["alpha"]),
                    "train_loo_mae": float(model["best"]["loo_mae"]),
                    "train_loo_spearman": float(model["best"]["loo_spearman"]),
                }
            )
    return pd.DataFrame(rows)


def null_permutation_stress(
    obs: pd.DataFrame,
    moves: dict[str, np.ndarray],
    features: list[h149mod.BundleFeature],
    h149_move: np.ndarray,
    n_perm: int = 250,
) -> tuple[pd.DataFrame, dict[str, float]]:
    spec = VariantSpec(name="all_full")
    model = fit_variant(obs, moves, features, spec)
    names = model["names"]
    x = model["x"]
    y = model["y"].copy()
    alpha = float(model["best"]["alpha"])
    real_pred = predict_move(h149_move, model)
    real_metrics, _ = loo_metrics(x, y, names, alpha)

    rng = np.random.default_rng(150)
    rows = []
    movable = np.array([i for i, name in enumerate(names) if name != BASE_FILE], dtype=int)
    for i in range(n_perm):
        y_perm = y.copy()
        y_perm[movable] = rng.permutation(y_perm[movable])
        metrics, _ = loo_metrics(x, y_perm, names, alpha)
        coef = h149mod.dual_ridge_coef(x, y_perm, alpha)
        raw = h149mod.raw_feature_vector(h149_move, model["features"]) / model["scale"]
        pred = float(raw @ coef)
        rows.append(
            {
                "perm": i,
                "loo_mae": metrics["loo_mae"],
                "loo_spearman": metrics["loo_spearman"],
                "h149_pred_delta": pred,
            }
        )
    null_df = pd.DataFrame(rows)
    summary = {
        "real_loo_mae": float(real_metrics["loo_mae"]),
        "real_loo_spearman": float(real_metrics["loo_spearman"]),
        "real_h149_pred_delta": float(real_pred),
        "null_spearman_ge_real_frac": float((null_df["loo_spearman"] >= real_metrics["loo_spearman"]).mean()),
        "null_mae_le_real_frac": float((null_df["loo_mae"] <= real_metrics["loo_mae"]).mean()),
        "null_h149_pred_le_real_frac": float((null_df["h149_pred_delta"] <= real_pred).mean()),
        "null_h149_pred_mean": float(null_df["h149_pred_delta"].mean()),
        "null_h149_pred_p05": float(null_df["h149_pred_delta"].quantile(0.05)),
        "null_h149_pred_p50": float(null_df["h149_pred_delta"].quantile(0.50)),
        "null_h149_pred_p95": float(null_df["h149_pred_delta"].quantile(0.95)),
    }
    return null_df, summary


def dropout_stability(
    obs: pd.DataFrame,
    moves: dict[str, np.ndarray],
    features: list[h149mod.BundleFeature],
    candidate_moves: dict[str, np.ndarray],
    n_trials: int = 180,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(151)
    names = obs["file"].astype(str).tolist()
    y = obs["delta_vs_h057"].to_numpy(dtype=np.float64)
    rows = []
    feature_rows = []
    for trial in range(n_trials):
        keep_prob = rng.uniform(0.45, 0.78)
        mask = rng.random(len(features)) < keep_prob
        if mask.sum() < 24:
            mask[rng.choice(len(features), size=24, replace=False)] = True
        feats = [f for f, keep in zip(features, mask) if keep]
        x, scale = h149mod.feature_matrix(moves, names, feats)
        coef = h149mod.dual_ridge_coef(x, y, alpha=1.0)
        rec = {"trial": trial, "keep_prob": float(keep_prob), "n_features": int(len(feats))}
        for cname, move in candidate_moves.items():
            pred = float((h149mod.raw_feature_vector(move, feats) / scale) @ coef)
            rec[f"{cname}_pred_delta"] = pred
        rows.append(rec)
        for feat, c, s in zip(feats, coef, scale):
            feature_rows.append(
                {
                    "trial": trial,
                    "feature": feat.name,
                    "family": feat.family,
                    "coef_per_unit": float(c / s),
                }
            )
    drop_df = pd.DataFrame(rows)
    feat_df = pd.DataFrame(feature_rows)
    return drop_df, feat_df


def candidate_metric_row(
    file_name: str,
    move: np.ndarray,
    models: dict[str, dict[str, object]],
    h088_move: np.ndarray,
) -> dict[str, object]:
    changed = np.abs(move) > TOL
    out: dict[str, object] = {
        "file": file_name,
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(len(set(np.where(changed)[0] // len(TARGETS)))),
        "move_l1": float(np.abs(move).sum()),
        "move_l2": float(np.linalg.norm(move)),
        "h088_move_cosine": cosine(move, h088_move),
    }
    for name, model in models.items():
        grad = gradient(model, len(move))
        tox = grad * move
        out[f"{name}_pred_delta"] = predict_move(move, model)
        out[f"{name}_benefit_sum"] = float(np.maximum(-tox, 0.0).sum())
        out[f"{name}_toxicity_sum"] = float(np.maximum(tox, 0.0).sum())
    return out


def build_robust_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    models: dict[str, dict[str, object]],
    moves: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    base_flat = base_prob.reshape(-1)
    n_cells = len(base_flat)
    h088 = moves.get("submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv", np.zeros(n_cells))
    grads = {name: gradient(model, n_cells) for name, model in models.items()}
    source_rows = []
    for source_file in CORE_SOURCE_FILES + [H149_FILE]:
        path = locate(source_file)
        if path is None:
            continue
        source_prob = load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        source_flat = source_prob.reshape(-1)
        move = logit(source_flat) - logit(base_flat)
        changed = np.abs(move) > TOL
        if not changed.any():
            continue
        benefit_matrix = np.vstack([-grad * move for grad in grads.values()])
        pos_frac = (benefit_matrix > 0).mean(axis=0)
        mean_benefit = benefit_matrix.mean(axis=0)
        min_benefit = benefit_matrix.min(axis=0)
        allfull_benefit = benefit_matrix[list(grads).index("all_full")]
        frontier_benefit = benefit_matrix[list(grads).index("frontier_only")]
        no_pre_benefit = benefit_matrix[list(grads).index("no_pre_h")]
        h088_same = (move * h088) > 0
        h088_penalty = h088_same.astype(float) * rank01(np.abs(h088), high=True)
        score = (
            1.15 * rank01(mean_benefit, high=True)
            + 0.95 * pos_frac
            + 0.45 * rank01(min_benefit, high=True)
            + 0.30 * rank01(np.abs(move), high=True)
            - 0.70 * h088_penalty
            - 1.20 * (allfull_benefit < 0).astype(float)
            - 0.80 * (frontier_benefit < 0).astype(float)
            - 0.80 * (no_pre_benefit < 0).astype(float)
        )
        for flat_idx in np.flatnonzero(changed):
            row_idx = flat_idx // len(TARGETS)
            target_idx = flat_idx % len(TARGETS)
            source_rows.append(
                {
                    "source_file": source_file,
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
                    "pos_frac": float(pos_frac[flat_idx]),
                    "mean_benefit": float(mean_benefit[flat_idx]),
                    "min_benefit": float(min_benefit[flat_idx]),
                    "allfull_benefit": float(allfull_benefit[flat_idx]),
                    "frontier_benefit": float(frontier_benefit[flat_idx]),
                    "no_pre_benefit": float(no_pre_benefit[flat_idx]),
                    "h088_same_direction": bool(h088_same[flat_idx]),
                    "h088_penalty": float(h088_penalty[flat_idx]),
                    "score": float(score[flat_idx]),
                }
            )
    all_cells = pd.DataFrame(source_rows)
    all_cells = all_cells.sort_values(
        ["flat_idx", "score", "pos_frac", "mean_benefit"],
        ascending=[True, False, False, False],
    ).drop_duplicates("flat_idx", keep="first")
    all_cells["passes_gate"] = (
        (all_cells["pos_frac"] >= 0.70)
        & (all_cells["mean_benefit"] > 0)
        & (all_cells["allfull_benefit"] > 0)
        & (all_cells["no_pre_benefit"] > -2.0e-6)
        & (all_cells["h088_penalty"] <= 0.98)
        & (all_cells["score"] >= all_cells["score"].quantile(0.52))
    )
    ranked = all_cells[all_cells["passes_gate"]].sort_values("score", ascending=False).copy()
    if len(ranked) < 180:
        ranked = all_cells[
            (all_cells["pos_frac"] >= 0.60)
            & (all_cells["mean_benefit"] > 0)
            & (all_cells["score"] >= all_cells["score"].quantile(0.46))
        ].sort_values("score", ascending=False).copy()

    selected_rows = []
    per_subject: dict[str, int] = {}
    per_target: dict[str, int] = {}
    per_row: dict[int, int] = {}
    max_cells = 430
    max_rows = 165
    max_per_subject = 110
    max_per_target = 95
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
        amp = 0.60
        new_flat[idx] = sigmoid(logit(base_flat[idx]) + amp * selected["source_move"].to_numpy(dtype=np.float64))
        selected["amp"] = amp
        selected["new_prob"] = new_flat[idx]
    return all_cells.sort_values("score", ascending=False).reset_index(drop=True), selected, new_flat.reshape(base_prob.shape)


def variant_specs() -> list[VariantSpec]:
    human = ("human_social_date", "human_social_date_target", "month_group")
    subject = ("subject_target", "subject_group")
    row_order = ("row_order_target", "row_order_group", "row_order")
    base = ("base_prob_target", "base_prob_tail")
    structural_keep = (
        "global",
        "target_group",
        "target",
        "subject_target",
        "subject_group",
        "row_order_target",
        "row_order_group",
        "row_order",
        "base_prob_target",
        "base_prob_tail",
    )
    human_keep = (
        "global",
        "target_group",
        "target",
        "human_social_date",
        "human_social_date_target",
        "month_group",
    )
    return [
        VariantSpec("all_full", description="all observations and all bundle features"),
        VariantSpec("no_pre_h", roles_exclude=("pre_h_world",), description="remove old pre-H public worlds"),
        VariantSpec("no_bad", roles_exclude=("bad_anchor",), description="remove bad-anchor worlds"),
        VariantSpec("frontier_only", roles_include=("frontier", "frontier_basin", "breakthrough_anchor", "negative_sensor", "tie_sensor"), description="post-H frontier sensor only"),
        VariantSpec("no_human_social", family_drop=human, description="drop date/social/pay/month features"),
        VariantSpec("no_subject", family_drop=subject, description="drop subject identity bundles"),
        VariantSpec("no_row_order", family_drop=row_order, description="drop row-order bundles"),
        VariantSpec("no_base_prob", family_drop=base, description="drop H057 probability-regime bundles"),
        VariantSpec("structural_only", family_keep=structural_keep, description="no human-social date features"),
        VariantSpec("human_social_only", family_keep=human_keep, description="date/social/pay/month plus target only"),
    ]


def run() -> None:
    cleanup_previous_outputs()
    base_path = locate(BASE_FILE)
    if base_path is None:
        raise FileNotFoundError(BASE_FILE)
    sample = load_sub(base_path)
    base_prob = sample[TARGETS].to_numpy(dtype=np.float64)
    obs = h148mod.collect_public_observations(sample)
    moves = {row["file"]: movement_from_file(Path(row["resolved_path"]), sample, base_prob) for row in obs.to_dict("records")}
    features = h149mod.build_bundle_features(sample, base_prob)

    # Include source/candidate moves for stress and materialization.
    candidate_move_files = set(h148mod.CANDIDATE_FILES + CORE_SOURCE_FILES + [H149_FILE])
    for file_name in sorted(candidate_move_files):
        path = locate(file_name)
        if path is None:
            continue
        try:
            load_sub(path, sample)
        except Exception:
            continue
        moves[file_name] = movement_from_file(path, sample, base_prob)

    specs = variant_specs()
    models = {spec.name: fit_variant(obs, moves, features, spec) for spec in specs}
    variant_scores = pd.concat([model["scores"].assign(description=model["spec"].description) for model in models.values()], ignore_index=True)
    variant_scores.to_csv(OUT / "h150_variant_scores.csv", index=False)
    pd.concat([model["loo_detail"] for model in models.values()], ignore_index=True).to_csv(OUT / "h150_loo_predictions.csv", index=False)

    role_holdout_df = role_holdout(obs, moves, features)
    role_holdout_df.to_csv(OUT / "h150_role_holdout.csv", index=False)

    h149_path = locate(H149_FILE)
    if h149_path is None:
        raise FileNotFoundError(H149_FILE)
    h149_move = movement_from_file(h149_path, sample, base_prob)
    null_df, null_summary = null_permutation_stress(obs, moves, features, h149_move)
    null_df.to_csv(OUT / "h150_null_permutation.csv", index=False)
    pd.DataFrame([null_summary]).to_csv(OUT / "h150_null_summary.csv", index=False)

    candidate_moves = {
        name.replace("submission_", "").replace("_uploadsafe.csv", "")[:48]: moves[name]
        for name in sorted(candidate_move_files)
        if name in moves
    }
    drop_df, drop_feature_df = dropout_stability(obs, moves, features, candidate_moves)
    drop_df.to_csv(OUT / "h150_dropout_stability.csv", index=False)
    drop_feature_df.to_csv(OUT / "h150_dropout_feature_coefficients.csv", index=False)

    h088_move = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    candidate_rows = []
    for file_name in sorted(candidate_move_files):
        if file_name not in moves:
            continue
        candidate_rows.append(candidate_metric_row(file_name, moves[file_name], models, h088_move))
    candidate_scores = pd.DataFrame(candidate_rows)
    candidate_scores["robust_min_pred_delta"] = candidate_scores[[f"{name}_pred_delta" for name in models]].min(axis=1)
    candidate_scores["robust_max_pred_delta"] = candidate_scores[[f"{name}_pred_delta" for name in models]].max(axis=1)
    candidate_scores["robust_mean_pred_delta"] = candidate_scores[[f"{name}_pred_delta" for name in models]].mean(axis=1)
    candidate_scores["robust_positive_variant_count"] = (candidate_scores[[f"{name}_pred_delta" for name in models]] < 0).sum(axis=1)
    candidate_scores = candidate_scores.sort_values(["robust_positive_variant_count", "robust_mean_pred_delta"], ascending=[False, True]).reset_index(drop=True)
    candidate_scores.to_csv(OUT / "h150_candidate_scores.csv", index=False)

    all_source_cells, selected, new_prob = build_robust_candidate(sample, base_prob, models, moves)
    all_source_cells.to_csv(OUT / "h150_source_cell_scores.csv", index=False)
    selected.to_csv(OUT / "h150_selected_cells.csv", index=False)

    hash_id = short_hash(new_prob)
    local_path = OUT / f"submission_h150_robust_bundle_listener_{hash_id}.csv"
    root_path = ROOT / f"submission_h150_robust_bundle_listener_{hash_id}_uploadsafe.csv"
    write_submission(sample, new_prob, local_path)
    shutil.copyfile(local_path, root_path)
    validation = validate_submission(root_path, sample, base_prob)
    h150_move = movement_from_file(root_path, sample, base_prob)
    h150_metrics = candidate_metric_row(root_path.name, h150_move, models, h088_move)

    variant_best = pd.DataFrame([model["best"] | {"variant": name, "description": model["spec"].description, "n_features": len(model["features"]), "n_obs": len(model["frame"])} for name, model in models.items()])
    variant_best.to_csv(OUT / "h150_variant_best.csv", index=False)

    dropout_summary_rows = []
    for col in [c for c in drop_df.columns if c.endswith("_pred_delta")]:
        dropout_summary_rows.append(
            {
                "candidate": col.replace("_pred_delta", ""),
                "mean_pred_delta": float(drop_df[col].mean()),
                "p05_pred_delta": float(drop_df[col].quantile(0.05)),
                "p50_pred_delta": float(drop_df[col].quantile(0.50)),
                "p95_pred_delta": float(drop_df[col].quantile(0.95)),
                "negative_frac": float((drop_df[col] < 0).mean()),
            }
        )
    dropout_summary = pd.DataFrame(dropout_summary_rows).sort_values(["negative_frac", "mean_pred_delta"], ascending=[False, True])
    dropout_summary.to_csv(OUT / "h150_dropout_summary.csv", index=False)

    decision = {
        "candidate_file": root_path.name,
        "candidate_path": str(root_path.resolve()),
        "selected_cells": int(len(selected)),
        "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
        "selected_source_mix": selected["source_file"].value_counts().to_dict() if not selected.empty else {},
        "selected_target_mix": selected["target"].value_counts().to_dict() if not selected.empty else {},
        "worldview": (
            "A safe row-target correction should survive multiple listener worlds: "
            "all observations, no-pre-H, no-bad, frontier-only, and feature-family ablations."
        ),
        "h149_status": (
            "H149 remains the highest-upside bundle listener bet, but H150 tests "
            "whether a robust consensus translator can keep the same worldview "
            "with less old-anchor dependence."
        ),
        **{f"validation_{k}": v for k, v in validation.items()},
        **{f"metric_{k}": v for k, v in h150_metrics.items() if k != "file"},
        **{f"null_{k}": v for k, v in null_summary.items()},
    }
    pd.DataFrame([decision]).to_csv(OUT / "h150_decision.csv", index=False)

    report = f"""# H150 Bundle-Listener Stress HS-JEPA

Date: 2026-06-03

## Question

H149 is the strongest current bundle-listener candidate, but its large upside
could be an old-anchor shortcut. H150 stress-tests that possibility.

## Stress Results

### Variant Best Scores

{md_table(variant_best[["variant", "description", "n_obs", "n_features", "alpha", "loo_mae", "loo_spearman", "h144_h145_pred_gap_abs", "selection_score"]].sort_values("selection_score"), 20)}

### Role Holdout

{md_table(role_holdout_df[["heldout_role", "file", "actual_delta", "pred_delta", "error", "train_n_obs", "train_loo_mae", "train_loo_spearman"]], 30)}

### Null Permutation Summary

{md_table(pd.DataFrame([null_summary]), 1)}

### Dropout Stability

{md_table(dropout_summary.head(20), 20)}

## Candidate Ranking Across Listener Worlds

{md_table(candidate_scores[["file", "changed_cells_vs_h057", "changed_rows_vs_h057", "h088_move_cosine", "robust_positive_variant_count", "robust_mean_pred_delta", "robust_min_pred_delta", "robust_max_pred_delta"]], 30)}

## Promoted Robust Candidate

{md_table(pd.DataFrame([decision]), 1)}

Source mix:

{md_table(selected["source_file"].value_counts().rename_axis("source_file").reset_index(name="cells") if not selected.empty else pd.DataFrame(), 10)}

Target mix:

{md_table(selected["target"].value_counts().rename_axis("target").reset_index(name="cells") if not selected.empty else pd.DataFrame(), 10)}

## Interpretation

H150 does not replace H149 as the high-upside public probe unless robustness is
preferred over upside.  Its role is sharper:

```text
If H149 fails, H150 tells whether the bundle-listener worldview died or only
the aggressive all-observed decoder died.
```

The key architectural decision is whether HS-JEPA should:

1. keep H149-style all-observed bundle listener as the next big public probe;
2. move to H150-style consensus listener before public submission;
3. abandon supervised public equations and solve discrete row-route constraints.
"""
    (OUT / "h150_report.md").write_text(report, encoding="utf-8")

    print(f"H150 candidate: {root_path}")
    print(f"selected cells: {len(selected)}")
    print("variant best:")
    print(variant_best[["variant", "alpha", "loo_mae", "loo_spearman"]].to_string(index=False))
    print("candidate top:")
    print(candidate_scores[["file", "robust_positive_variant_count", "robust_mean_pred_delta"]].head(14).to_string(index=False))


if __name__ == "__main__":
    run()
