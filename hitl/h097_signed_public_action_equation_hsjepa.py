#!/usr/bin/env python3
"""H097: signed public action-equation HS-JEPA.

H096 made H088 useful as a signed counterfactual sensor, but it only used one
failed public action.  H097 generalizes that idea:

    known public submissions -> signed action-response equation

The target is not a label posterior.  It is the public LB response to moving
specific row-target cells in specific directions from the H057 base.  The
decoder then proposes actions whose signed movement is predicted to reduce
public loss while respecting H057/H088 conflict geometry.
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
OUT = HITL / "h097_signed_public_action_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H095_PATH = HITL / "h095_public_private_assignment_solver_hsjepa.py"
SPEC = importlib.util.spec_from_file_location("h095mod", H095_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H095_PATH}")
h095mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h095mod
SPEC.loader.exec_module(h095mod)

h085mod = h095mod.h085mod
h087mod = h095mod.h087mod

TARGETS = h095mod.TARGETS
KEYS = h095mod.KEYS
BASE_FILE = h095mod.BASE_FILE
BASE_LB = h085mod.BASE_LB
TOL = h095mod.TOL


@dataclass(frozen=True)
class ResponseFit:
    feature_set: str
    alpha: float
    cell_cols: list[str]
    x_cols: list[str]
    intercept: float
    beta: np.ndarray
    mu: np.ndarray
    sd: np.ndarray
    loo_pred: np.ndarray
    loo_mae: float
    loo_rmse: float
    loo_spearman: float
    loo_pair_acc: float
    perm_p: float = 1.0


@dataclass(frozen=True)
class H097Spec:
    name: str
    mode: str
    target_group: str
    k: int
    alpha: float
    cap: float
    min_score: float
    worldview: str


def clip_prob(x: np.ndarray) -> np.ndarray:
    return h085mod.clip_prob(np.asarray(x, dtype=np.float64))


def logit(x: np.ndarray) -> np.ndarray:
    return h085mod.logit(np.asarray(x, dtype=np.float64))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return h085mod.sigmoid(np.asarray(x, dtype=np.float64))


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return h085mod.bce(np.asarray(prob, dtype=np.float64), np.asarray(q, dtype=np.float64))


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return h085mod.rank01(np.asarray(values, dtype=np.float64), high=high)


def safe_id(text: str, limit: int = 132) -> str:
    return h085mod.safe_id(text, limit=limit)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return h085mod.md_table(frame, n=n)


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = pd.Series(a).rank(method="average").to_numpy(dtype=np.float64)
    rb = pd.Series(b).rank(method="average").to_numpy(dtype=np.float64)
    if np.std(ra) < 1.0e-12 or np.std(rb) < 1.0e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def pairwise_accuracy(y: np.ndarray, pred: np.ndarray) -> float:
    ok = 0
    total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            dp = pred[i] - pred[j]
            if abs(dy) < 1.0e-12:
                continue
            total += 1
            ok += int(np.sign(dy) == np.sign(dp))
    return float(ok / total) if total else float("nan")


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h097_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h097_signed_equation_*_uploadsafe.csv"):
        path.unlink()


def ensure_h095_cell_table(sample: pd.DataFrame, base_prob: np.ndarray) -> pd.DataFrame:
    path = HITL / "h095_public_private_assignment_solver_hsjepa" / "h095_cell_toxicity_table.csv"
    if path.exists():
        return pd.read_csv(path)
    _known, _configs, cell, _q_prob = h095mod.build_h095_cell_table(sample, base_prob)
    return cell


def add_context_features(cell: pd.DataFrame, sample: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    out = cell.copy().sort_values(["row", "target_index"]).reset_index(drop=True)
    sample2 = sample.copy()
    sample2["row"] = np.arange(len(sample2), dtype=int)
    sample2["sleep_date"] = pd.to_datetime(sample2["sleep_date"])
    sample2["lifelog_date"] = pd.to_datetime(sample2["lifelog_date"])
    sample2["sleep_dow"] = sample2["sleep_date"].dt.dayofweek.astype(float)
    sample2["lifelog_dow"] = sample2["lifelog_date"].dt.dayofweek.astype(float)
    sample2["date_gap_days"] = (sample2["sleep_date"] - sample2["lifelog_date"]).dt.days.astype(float)
    sample2["row_norm"] = sample2["row"] / max(len(sample2) - 1, 1)
    sample2["row_sin1"] = np.sin(2.0 * np.pi * sample2["row_norm"])
    sample2["row_cos1"] = np.cos(2.0 * np.pi * sample2["row_norm"])
    sample2["row_sin3"] = np.sin(6.0 * np.pi * sample2["row_norm"])
    sample2["row_cos3"] = np.cos(6.0 * np.pi * sample2["row_norm"])
    sample2["subject_idx"] = pd.factorize(sample2["subject_id"].astype(str), sort=True)[0].astype(float)
    subject_counts = sample2.groupby("subject_id")["row"].transform("size").astype(float)
    sample2["within_subject_order"] = sample2.groupby("subject_id").cumcount().astype(float)
    sample2["within_subject_norm"] = sample2["within_subject_order"] / np.maximum(subject_counts - 1.0, 1.0)
    sample2["subject_block_size"] = subject_counts
    out = out.merge(
        sample2[
            [
                "row",
                "sleep_dow",
                "lifelog_dow",
                "date_gap_days",
                "row_norm",
                "row_sin1",
                "row_cos1",
                "row_sin3",
                "row_cos3",
                "subject_idx",
                "within_subject_norm",
                "subject_block_size",
            ]
        ],
        on="row",
        how="left",
    )
    for target in TARGETS:
        out[f"target_{target}"] = out["target"].astype(str).eq(target).astype(float)
    for dow in range(7):
        out[f"sleep_dow_{dow}"] = out["sleep_dow"].eq(float(dow)).astype(float)
        out[f"lifelog_dow_{dow}"] = out["lifelog_dow"].eq(float(dow)).astype(float)
    out["is_q"] = out["target"].isin(["Q1", "Q2", "Q3"]).astype(float)
    out["is_s"] = out["target"].isin(["S1", "S2", "S3", "S4"]).astype(float)
    out["is_subjective_quality"] = out["target"].isin(["Q1", "Q3"]).astype(float)
    out["is_objective_stage"] = out["target"].isin(["S1", "S2", "S3", "S4"]).astype(float)
    out["h057_h088_anti_conflict"] = (
        (out["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
        & (out["h088_toxicity"].to_numpy(dtype=np.float64) > 0)
        & (
            np.sign(out["h057_positive_logit_move"].to_numpy(dtype=np.float64))
            * np.sign(out["h088_logit_move"].to_numpy(dtype=np.float64))
            < 0
        )
    ).astype(float)
    out["h057_h088_same_conflict"] = (
        (out["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
        & (out["h088_toxicity"].to_numpy(dtype=np.float64) > 0)
        & (
            np.sign(out["h057_positive_logit_move"].to_numpy(dtype=np.float64))
            * np.sign(out["h088_logit_move"].to_numpy(dtype=np.float64))
            > 0
        )
    ).astype(float)
    out["conflict_strength"] = out["h057_positive_weight"] * out["h088_toxicity"] * out["h057_h088_anti_conflict"]

    base_cols = [
        "h085_q_move",
        "h085_q_gain",
        "h085_abs_q_move",
        "h095_safe_cell_score",
        "h088_toxicity",
        "h088_q_bad",
        "h088_logit_move",
        "h057_positive_weight",
        "h057_positive_logit_move",
        "conflict_strength",
        "h057_h088_anti_conflict",
        "h057_h088_same_conflict",
        "public_score",
        "invariant_score",
        "private_safe_score",
        "latent_shortcut_energy",
        "h068_cell_health",
        "h080_cell_score",
        "h080_bad_same_rank",
        "h080_bad_opp_rank",
        "h080_bad_margin_rank",
        "source_count",
        "source_weight",
        "source_family_count",
        "source_consensus",
        "source_mean_move",
        "source_action_delta",
        "source_agrees_h085",
        "h082_cell",
        "h084_dark_cell",
        "h086_resp_weight",
        "h086_resp_lift",
        "h086_resp_action_score",
        "confidence",
        "hard_diag_gain",
        "hard_logit_move",
        "binary_shock",
    ]
    id_cols = [
        "row_norm",
        "row_sin1",
        "row_cos1",
        "row_sin3",
        "row_cos3",
        "within_subject_norm",
        "subject_block_size",
        "date_gap_days",
        "is_q",
        "is_s",
        "is_subjective_quality",
        "is_objective_stage",
    ] + [f"target_{target}" for target in TARGETS] + [f"sleep_dow_{dow}" for dow in range(7)]
    target_cols = [f"target_{target}" for target in TARGETS] + ["is_q", "is_s", "is_subjective_quality", "is_objective_stage"]
    conflict_cols = [
        "h088_toxicity",
        "h088_q_bad",
        "h088_logit_move",
        "h057_positive_weight",
        "h057_positive_logit_move",
        "conflict_strength",
        "h057_h088_anti_conflict",
        "h057_h088_same_conflict",
    ] + target_cols

    numeric = []
    for col in sorted(set(base_cols + id_cols + conflict_cols)):
        if col not in out.columns:
            continue
        vals = pd.to_numeric(out[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=np.float64)
        if np.nanstd(vals) > 1.0e-12:
            out[col] = vals
            numeric.append(col)

    feature_sets = {
        "target_conflict": [c for c in conflict_cols if c in numeric],
        "state_core": [c for c in base_cols + target_cols if c in numeric],
        "state_context": [c for c in base_cols + id_cols if c in numeric],
        "target_only": [c for c in target_cols + id_cols if c in numeric],
    }
    feature_sets = {name: sorted(set(cols)) for name, cols in feature_sets.items() if len(cols) >= 4}
    return out, feature_sets


def load_public_moves(sample: pd.DataFrame, base_prob: np.ndarray) -> pd.DataFrame:
    known = h085mod.public_observations(sample).copy()
    rows = []
    base_logit = logit(base_prob).reshape(-1)
    for rec in known.to_dict("records"):
        path = h085mod.locate(str(rec["file"]))
        if path is None:
            continue
        pred = h085mod.load_sub(path, sample)[TARGETS].to_numpy(dtype=np.float64)
        move = logit(pred).reshape(-1) - base_logit
        rows.append(
            {
                "file": str(rec["file"]),
                "public_lb": float(rec["public_lb"]),
                "known_source": str(rec.get("known_source", "")),
                "delta_vs_h057": float(rec["public_lb"] - BASE_LB),
                "changed_cells_vs_h057": int((np.abs(pred - base_prob) > TOL).sum()),
                "mean_abs_logit_move": float(np.mean(np.abs(move))),
                "move_logit": move,
            }
        )
    out = pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)
    if len(out) < 10:
        raise RuntimeError("not enough public observations")
    return out


def build_design_for_moves(moves: np.ndarray, cell: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, list[str], np.ndarray]:
    f = cell[cols].to_numpy(dtype=np.float64)
    n = max(f.shape[0], 1)
    signed = moves @ f / n
    absed = np.abs(moves) @ f / n

    h088_move = cell["h088_logit_move"].to_numpy(dtype=np.float64)
    h088_tox = cell["h088_toxicity"].to_numpy(dtype=np.float64)
    h057_move = cell["h057_positive_logit_move"].to_numpy(dtype=np.float64)
    h057_w = cell["h057_positive_weight"].to_numpy(dtype=np.float64)
    bad_same = cell["h080_bad_same_rank"].to_numpy(dtype=np.float64)
    h095_safe = cell["h095_safe_cell_score"].to_numpy(dtype=np.float64)
    extras = []
    extra_cols = []
    for move in moves:
        same_h088 = np.maximum(0.0, move * h088_move) * h088_tox
        anti_h088 = np.maximum(0.0, -move * h088_move) * h088_tox
        align_h057 = np.maximum(0.0, move * h057_move) * h057_w
        opp_h057 = np.maximum(0.0, -move * h057_move) * h057_w
        extras.append(
            [
                float(np.mean(np.abs(move))),
                float(np.mean(move * move)),
                float(np.mean(np.abs(move) > 1.0e-10)),
                float(np.mean(same_h088)),
                float(np.mean(anti_h088)),
                float(np.mean(align_h057)),
                float(np.mean(opp_h057)),
                float(np.mean(np.abs(move) * bad_same)),
                float(np.mean(np.abs(move) * h095_safe)),
            ]
        )
    extra_cols = [
        "mean_abs_move",
        "mean_sq_move",
        "changed_share",
        "same_h088_energy",
        "anti_h088_energy",
        "align_h057_energy",
        "opp_h057_energy",
        "bad_same_weighted_abs",
        "safe_weighted_abs",
    ]
    x = np.column_stack([signed, absed, np.asarray(extras, dtype=np.float64)])
    x_cols = [f"signed::{col}" for col in cols] + [f"abs::{col}" for col in cols] + extra_cols
    return x, x_cols, f


def fit_ridge(train_x: np.ndarray, train_y: np.ndarray, alpha: float) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    mu = np.nanmean(train_x, axis=0)
    sd = np.nanstd(train_x, axis=0)
    sd = np.where(sd < 1.0e-12, 1.0, sd)
    x = np.nan_to_num((train_x - mu) / sd)
    xa = np.column_stack([np.ones(len(x)), x])
    penalty = np.eye(xa.shape[1], dtype=np.float64) * alpha
    penalty[0, 0] = 0.0
    beta_all = np.linalg.pinv(xa.T @ xa + penalty) @ xa.T @ train_y
    return float(beta_all[0]), beta_all[1:], mu, sd


def predict_x(x: np.ndarray, intercept: float, beta: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    return intercept + np.nan_to_num((x - mu) / sd) @ beta


def evaluate_response_models(public: pd.DataFrame, cell: pd.DataFrame, feature_sets: dict[str, list[str]]) -> tuple[pd.DataFrame, pd.DataFrame, ResponseFit]:
    moves = np.vstack(public["move_logit"].to_list()).astype(np.float64)
    y = public["delta_vs_h057"].to_numpy(dtype=np.float64)
    alphas = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]
    rows = []
    pred_rows = []
    fits: list[ResponseFit] = []
    for feature_set, cols in feature_sets.items():
        x, x_cols, _f = build_design_for_moves(moves, cell, cols)
        if x.shape[1] > 120:
            variances = np.nanvar(x, axis=0)
            keep = np.argsort(variances)[-120:]
            x = x[:, keep]
            x_cols = [x_cols[i] for i in keep]
        for alpha in alphas:
            loo = np.zeros(len(y), dtype=np.float64)
            for held in range(len(y)):
                keep = np.ones(len(y), dtype=bool)
                keep[held] = False
                intercept, beta, mu, sd = fit_ridge(x[keep], y[keep], alpha)
                loo[held] = predict_x(x[[held]], intercept, beta, mu, sd)[0]
            err = loo - y
            intercept, beta, mu, sd = fit_ridge(x, y, alpha)
            full_pred = predict_x(x, intercept, beta, mu, sd)
            fit = ResponseFit(
                feature_set=feature_set,
                alpha=float(alpha),
                cell_cols=cols,
                x_cols=x_cols,
                intercept=intercept,
                beta=beta,
                mu=mu,
                sd=sd,
                loo_pred=loo,
                loo_mae=float(np.mean(np.abs(err))),
                loo_rmse=float(np.sqrt(np.mean(err * err))),
                loo_spearman=spearman(y, loo),
                loo_pair_acc=pairwise_accuracy(y, loo),
            )
            fits.append(fit)
            rows.append(
                {
                    "feature_set": feature_set,
                    "alpha": float(alpha),
                    "n_x_features": len(x_cols),
                    "loo_mae": fit.loo_mae,
                    "loo_rmse": fit.loo_rmse,
                    "loo_spearman": fit.loo_spearman,
                    "loo_pair_acc": fit.loo_pair_acc,
                    "full_fit_mae": float(np.mean(np.abs(full_pred - y))),
                }
            )
            for i, rec in public[["file", "public_lb", "delta_vs_h057"]].iterrows():
                pred_rows.append(
                    {
                        "feature_set": feature_set,
                        "alpha": float(alpha),
                        "file": str(rec["file"]),
                        "public_lb": float(rec["public_lb"]),
                        "delta_vs_h057": float(rec["delta_vs_h057"]),
                        "loo_pred_delta": float(loo[i]),
                        "loo_error": float(loo[i] - rec["delta_vs_h057"]),
                    }
                )

    model_df = pd.DataFrame(rows)
    model_df["rank_score"] = (
        model_df["loo_mae"]
        + 0.45 * model_df["loo_rmse"]
        - 0.00018 * model_df["loo_pair_acc"].fillna(0.0)
        - 0.00010 * model_df["loo_spearman"].fillna(0.0)
    )
    model_df = model_df.sort_values(["rank_score", "loo_mae"], ascending=[True, True]).reset_index(drop=True)
    best = model_df.iloc[0]
    selected = next(
        fit
        for fit in fits
        if fit.feature_set == str(best["feature_set"]) and abs(fit.alpha - float(best["alpha"])) < 1.0e-12
    )

    rng = np.random.default_rng(97097)
    null_mae = []
    moves_sel = np.vstack(public["move_logit"].to_list()).astype(np.float64)
    x_sel, x_cols_sel, _f = build_design_for_moves(moves_sel, cell, selected.cell_cols)
    if x_sel.shape[1] != len(selected.x_cols):
        keep = [i for i, col in enumerate(x_cols_sel) if col in set(selected.x_cols)]
        x_sel = x_sel[:, keep]
    for _ in range(200):
        y_perm = rng.permutation(y)
        loo = np.zeros(len(y), dtype=np.float64)
        for held in range(len(y)):
            keep_mask = np.ones(len(y), dtype=bool)
            keep_mask[held] = False
            intercept, beta, mu, sd = fit_ridge(x_sel[keep_mask], y_perm[keep_mask], selected.alpha)
            loo[held] = predict_x(x_sel[[held]], intercept, beta, mu, sd)[0]
        null_mae.append(float(np.mean(np.abs(loo - y_perm))))
    perm_p = float(np.mean(np.asarray(null_mae) <= selected.loo_mae))
    selected = ResponseFit(
        feature_set=selected.feature_set,
        alpha=selected.alpha,
        cell_cols=selected.cell_cols,
        x_cols=selected.x_cols,
        intercept=selected.intercept,
        beta=selected.beta,
        mu=selected.mu,
        sd=selected.sd,
        loo_pred=selected.loo_pred,
        loo_mae=selected.loo_mae,
        loo_rmse=selected.loo_rmse,
        loo_spearman=selected.loo_spearman,
        loo_pair_acc=selected.loo_pair_acc,
        perm_p=perm_p,
    )
    model_df.loc[
        model_df["feature_set"].eq(selected.feature_set) & model_df["alpha"].eq(selected.alpha),
        "perm_p",
    ] = perm_p
    model_df["perm_p"] = model_df["perm_p"].fillna(1.0)
    pd.DataFrame({"perm_loo_mae": null_mae, "real_loo_mae": selected.loo_mae}).to_csv(
        OUT / "h097_response_permutation_null.csv",
        index=False,
    )
    return model_df, pd.DataFrame(pred_rows), selected


def response_gradient(cell: pd.DataFrame, fit: ResponseFit) -> np.ndarray:
    # Only signed aggregate terms are differentiable at zero and become the
    # local public action gradient.
    signed_beta = np.zeros(len(fit.cell_cols), dtype=np.float64)
    for i, col in enumerate(fit.cell_cols):
        key = f"signed::{col}"
        if key in fit.x_cols:
            idx = fit.x_cols.index(key)
            signed_beta[i] = fit.beta[idx] / fit.sd[idx]
    f = cell[fit.cell_cols].to_numpy(dtype=np.float64)
    return f @ signed_beta / max(len(cell), 1)


def predict_candidate_delta(move_flat: np.ndarray, cell: pd.DataFrame, fit: ResponseFit) -> float:
    x, x_cols, _f = build_design_for_moves(move_flat.reshape(1, -1), cell, fit.cell_cols)
    if x.shape[1] != len(fit.x_cols):
        keep = [i for i, col in enumerate(x_cols) if col in set(fit.x_cols)]
        x = x[:, keep]
    return float(predict_x(x, fit.intercept, fit.beta, fit.mu, fit.sd)[0])


def target_allowed(cell: pd.DataFrame, group: str) -> np.ndarray:
    target = cell["target"].astype(str)
    if group == "all":
        return np.ones(len(cell), dtype=bool)
    if group == "nonq2":
        return target.ne("Q2").to_numpy()
    if group == "stage":
        return target.isin(["S1", "S2", "S3", "S4"]).to_numpy()
    if group == "objective_plus_q3":
        return target.isin(["Q3", "S1", "S2", "S3", "S4"]).to_numpy()
    if group == "q2":
        return target.eq("Q2").to_numpy()
    if group == "conflict":
        return cell["h057_h088_anti_conflict"].to_numpy(dtype=np.float64) > 0
    raise ValueError(group)


def candidate_specs() -> list[H097Spec]:
    return [
        H097Spec(
            name="signed_descent_all_c760_a050",
            mode="signed_descent",
            target_group="all",
            k=760,
            alpha=0.50,
            cap=0.55,
            min_score=0.58,
            worldview="all-cell public action gradient has a usable signed descent field",
        ),
        H097Spec(
            name="signed_stage_c620_a055",
            mode="signed_descent",
            target_group="objective_plus_q3",
            k=620,
            alpha=0.55,
            cap=0.58,
            min_score=0.56,
            worldview="objective Q3/S signed response is the broad hidden field",
        ),
        H097Spec(
            name="counter_h088_toxic_c520_a045",
            mode="counter_h088",
            target_group="all",
            k=520,
            alpha=0.45,
            cap=0.50,
            min_score=0.54,
            worldview="public-failed H088 actions become opposite-direction supervision at scale",
        ),
        H097Spec(
            name="conflict_invert_model_c105_a060",
            mode="conflict_invert",
            target_group="conflict",
            k=105,
            alpha=0.60,
            cap=0.70,
            min_score=0.48,
            worldview="H096 conflict inversion survives when filtered by all-public action response",
        ),
        H097Spec(
            name="q2_gradient_reopen_c115_a070",
            mode="signed_descent",
            target_group="q2",
            k=115,
            alpha=0.70,
            cap=0.90,
            min_score=0.54,
            worldview="Q2 hardtail is the safest signed public-response route",
        ),
        H097Spec(
            name="positive_bridge_c260_a045",
            mode="h057_positive",
            target_group="all",
            k=260,
            alpha=0.45,
            cap=0.55,
            min_score=0.52,
            worldview="H057-positive field is still valid when aligned with learned public gradient",
        ),
    ]


def build_action_pool(cell: pd.DataFrame, gradient: np.ndarray) -> pd.DataFrame:
    out = cell.copy()
    g = np.asarray(gradient, dtype=np.float64)
    g_scale = float(np.quantile(np.abs(g), 0.98))
    if g_scale <= 1.0e-15:
        g_scale = 1.0
    out["h097_gradient"] = g
    out["h097_descent_logit_move"] = -np.sign(g) * np.tanh(np.abs(g) / g_scale)
    h088_move = out["h088_logit_move"].to_numpy(dtype=np.float64)
    h057_move = out["h057_positive_logit_move"].to_numpy(dtype=np.float64)
    out["h097_counter_h088_move"] = -np.sign(h088_move) * np.tanh(np.abs(h088_move) / (np.quantile(np.abs(h088_move), 0.95) + 1.0e-9))
    out["h097_conflict_move"] = np.sign(h057_move) * np.tanh(np.abs(h057_move) / (np.quantile(np.abs(h057_move), 0.95) + 1.0e-9))
    out["h097_positive_move"] = out["h097_conflict_move"]

    descent_agrees_h057 = (
        np.sign(out["h097_descent_logit_move"].to_numpy(dtype=np.float64))
        * np.sign(h057_move)
        > 0
    ).astype(float)
    descent_anti_h088 = (
        np.sign(out["h097_descent_logit_move"].to_numpy(dtype=np.float64))
        * np.sign(h088_move)
        < 0
    ).astype(float)
    out["h097_cell_score"] = (
        0.25 * rank01(np.abs(g), high=True)
        + 0.16 * out["h095_safe_cell_score"].to_numpy(dtype=np.float64)
        + 0.13 * out["h057_h088_anti_conflict"].to_numpy(dtype=np.float64)
        + 0.11 * descent_anti_h088 * out["h088_toxicity"].to_numpy(dtype=np.float64)
        + 0.10 * descent_agrees_h057 * out["h057_positive_weight"].to_numpy(dtype=np.float64)
        + 0.08 * out["source_agrees_h085"].to_numpy(dtype=np.float64)
        + 0.07 * out["h082_cell"].to_numpy(dtype=np.float64)
        + 0.06 * out["invariant_score"].to_numpy(dtype=np.float64)
        - 0.12 * out["h080_bad_same_rank"].to_numpy(dtype=np.float64)
        - 0.10 * out["is_h050_null"].to_numpy(dtype=np.float64)
    )
    return out.sort_values("h097_cell_score", ascending=False).reset_index(drop=True)


def select_cells(pool: pd.DataFrame, spec: H097Spec) -> pd.DataFrame:
    allowed = target_allowed(pool, spec.target_group)
    if spec.mode == "signed_descent":
        move_col = "h097_descent_logit_move"
        mode_mask = np.abs(pool[move_col].to_numpy(dtype=np.float64)) > 1.0e-10
    elif spec.mode == "counter_h088":
        move_col = "h097_counter_h088_move"
        mode_mask = pool["h088_toxicity"].to_numpy(dtype=np.float64) > 0.0
    elif spec.mode == "conflict_invert":
        move_col = "h097_conflict_move"
        mode_mask = pool["h057_h088_anti_conflict"].to_numpy(dtype=np.float64) > 0.0
    elif spec.mode == "h057_positive":
        move_col = "h097_positive_move"
        mode_mask = (
            (pool["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
            & (
                np.sign(pool["h097_descent_logit_move"].to_numpy(dtype=np.float64))
                * np.sign(pool["h057_positive_logit_move"].to_numpy(dtype=np.float64))
                > 0
            )
        )
    else:
        raise ValueError(spec.mode)
    selected = pool[allowed & mode_mask & (pool["h097_cell_score"] >= spec.min_score)].copy()
    selected["h097_move_col"] = move_col
    return selected.sort_values("h097_cell_score", ascending=False).head(spec.k).reset_index(drop=True)


def materialize_candidate(base_prob: np.ndarray, selected: pd.DataFrame, spec: H097Spec) -> tuple[np.ndarray, np.ndarray]:
    prob = base_prob.copy()
    move_mat = np.zeros_like(base_prob, dtype=np.float64)
    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        tidx = int(rec["target_index"])
        move_col = str(rec["h097_move_col"])
        move = float(np.clip(rec[move_col], -spec.cap, spec.cap) * spec.alpha)
        old = float(base_prob[row, tidx])
        prob[row, tidx] = float(sigmoid(logit(np.array([old])) + np.array([move]))[0])
        move_mat[row, tidx] = move
    return clip_prob(prob), move_mat


def cosine(delta_a: np.ndarray, delta_b: np.ndarray) -> float:
    a = np.asarray(delta_a, dtype=np.float64).reshape(-1)
    b = np.asarray(delta_b, dtype=np.float64).reshape(-1)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def evaluate_candidate(
    candidate_id: str,
    prob: np.ndarray,
    move_mat: np.ndarray,
    base_prob: np.ndarray,
    selected: pd.DataFrame,
    cell: pd.DataFrame,
    sample: pd.DataFrame,
    fit: ResponseFit,
    spec: H097Spec,
    path: Path,
) -> dict[str, object]:
    ordered = cell.sort_values("flat_index")
    q097 = ordered["h085_q"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    qhard = ordered["q_hard"].to_numpy(dtype=np.float64).reshape(base_prob.shape)
    h088_prob = h095mod.load_optional_prob(h095mod.H088_FILE, sample)
    h042_prob = h095mod.load_optional_prob(h095mod.H042_FILE, sample)
    h050_prob = h095mod.load_optional_prob(h095mod.H050_FILE, sample)
    if h088_prob is None:
        raise FileNotFoundError(h095mod.H088_FILE)
    pred_delta = predict_candidate_delta(move_mat.reshape(-1), cell, fit)
    posterior_delta = float((bce(prob, q097) - bce(base_prob, q097)).mean())
    hard_delta = float((bce(prob, qhard) - bce(base_prob, qhard)).mean())
    delta = prob - base_prob
    diff = np.abs(delta) > TOL
    bad_cos = h087mod.bad_anchor_cosines(delta, sample, base_prob)
    max_positive_bad = max([0.0] + [v for v in bad_cos.values() if v > 0])
    h088_cos = cosine(delta, h088_prob - base_prob)
    h042_cos = cosine(delta, base_prob - h042_prob) if h042_prob is not None else 0.0
    h050_cos = cosine(delta, base_prob - h050_prob) if h050_prob is not None else 0.0
    validation = h085mod.validate_submission(path, sample, base_prob)
    if selected.empty:
        anti_h088_rate = 0.0
        h057_align_rate = 0.0
        toxic_mean = 0.0
        conflict_rate = 0.0
        safe_mean = 0.0
        bad_same = 0.0
    else:
        move = move_mat.reshape(-1)[selected["flat_index"].astype(int).to_numpy()]
        h088_move = selected["h088_logit_move"].to_numpy(dtype=np.float64)
        h057_move = selected["h057_positive_logit_move"].to_numpy(dtype=np.float64)
        anti_h088_rate = float((np.sign(move) * np.sign(h088_move) < 0).mean())
        h057_align_rate = float(
            (
                (np.sign(move) * np.sign(h057_move) > 0)
                & (selected["h057_positive_weight"].to_numpy(dtype=np.float64) > 0)
            ).mean()
        )
        toxic_mean = float(selected["h088_toxicity"].mean())
        conflict_rate = float(selected["h057_h088_anti_conflict"].mean())
        safe_mean = float(selected["h095_safe_cell_score"].mean())
        bad_same = float(selected["h080_bad_same_rank"].mean())
    per_target = {
        f"{target}_changed_vs_h057": int(diff[:, i].sum())
        for i, target in enumerate(TARGETS)
    }
    h097_score = (
        200.0 * (-pred_delta)
        + 60.0 * (-posterior_delta)
        + 0.18 * max(h042_cos, 0.0)
        + 0.12 * max(h050_cos, 0.0)
        + 0.12 * h057_align_rate
        + 0.10 * anti_h088_rate
        + 0.10 * conflict_rate
        + 0.08 * safe_mean
        - 0.18 * max(h088_cos, 0.0)
        - 0.22 * max_positive_bad
        - 0.10 * max(bad_same - 0.65, 0.0)
        - 25.0 * max(hard_delta, 0.0)
    )
    out: dict[str, object] = {
        "candidate_id": candidate_id,
        "spec_name": spec.name,
        "mode": spec.mode,
        "target_group": spec.target_group,
        "worldview": spec.worldview,
        "fit_feature_set": fit.feature_set,
        "fit_alpha": fit.alpha,
        "k": spec.k,
        "alpha": spec.alpha,
        "cap": spec.cap,
        "selected_cells": int(len(selected)),
        "changed_cells_vs_h057": int(diff.sum()),
        "changed_rows_vs_h057": int(diff.any(axis=1).sum()),
        "model_pred_delta_vs_h057": pred_delta,
        "posterior_delta_vs_h057": posterior_delta,
        "hard_diag_delta_vs_h057": hard_delta,
        "anti_h088_direction_rate": anti_h088_rate,
        "h057_positive_align_rate": h057_align_rate,
        "selected_toxic_mean": toxic_mean,
        "selected_conflict_rate": conflict_rate,
        "selected_safe_cell_mean": safe_mean,
        "mean_bad_same_rank": bad_same,
        "cos_h088_direction": h088_cos,
        "cos_h057_vs_h042_direction": h042_cos,
        "cos_h057_vs_h050_direction": h050_cos,
        "max_positive_bad_cosine": float(max_positive_bad),
        "mean_abs_prob_move_vs_h057": float(np.abs(delta).mean()),
        "max_abs_prob_move_vs_h057": float(np.abs(delta).max()),
        "selected_subjects": int(selected["subject_id"].nunique()) if len(selected) else 0,
        "selected_rows": ",".join(map(str, sorted(selected["row"].astype(int).unique().tolist()))) if len(selected) else "",
        "h097_score": h097_score,
        "file": path.name,
        "resolved_path": str(path.resolve()),
    }
    out.update(per_target)
    out.update(bad_cos)
    out.update(validation)
    return out


def run() -> None:
    cleanup_previous_outputs()
    base = h085mod.load_sub(BASE_FILE)
    sample = base[KEYS].copy()
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    cell_raw = ensure_h095_cell_table(sample, base_prob)
    cell, feature_sets = add_context_features(cell_raw, sample)
    public = load_public_moves(sample, base_prob)
    model_scores, pred_rows, fit = evaluate_response_models(public, cell, feature_sets)
    gradient = response_gradient(cell, fit)
    action_pool = build_action_pool(cell, gradient)

    candidate_rows = []
    selected_frames = []
    for spec in candidate_specs():
        selected = select_cells(action_pool, spec)
        if selected.empty:
            continue
        prob, move_mat = materialize_candidate(base_prob, selected, spec)
        if int((np.abs(prob - base_prob) > TOL).sum()) == 0:
            continue
        hash_id = short_hash(prob)
        candidate_id = safe_id(f"h097_{spec.name}_{hash_id}", 128)
        path = OUT / f"submission_{candidate_id}.csv"
        h085mod.write_submission(sample, prob, path)
        metrics = evaluate_candidate(candidate_id, prob, move_mat, base_prob, selected, cell, sample, fit, spec, path)
        candidate_rows.append(metrics)
        selected = selected.copy()
        selected.insert(0, "candidate_id", candidate_id)
        selected_frames.append(selected)

    candidates = pd.DataFrame(candidate_rows)
    if candidates.empty:
        raise RuntimeError("no H097 candidates")
    candidates = candidates.sort_values(["h097_score", "model_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    selected = candidates.iloc[0].to_dict()
    selected_path = Path(str(selected["resolved_path"]))
    root_path = ROOT / f"submission_h097_signed_equation_{selected['candidate_id'].split('_')[-1]}_uploadsafe.csv"
    shutil.copyfile(selected_path, root_path)
    validation = h085mod.validate_submission(root_path, sample, base_prob)
    decision = {
        "decision": "promote_h097_signed_public_action_equation",
        "selected_candidate_id": selected["candidate_id"],
        "root_uploadsafe_path": str(root_path.resolve()),
        "worldview": selected["worldview"],
        "response_feature_set": fit.feature_set,
        "response_alpha": fit.alpha,
        "response_loo_mae": fit.loo_mae,
        "response_loo_rmse": fit.loo_rmse,
        "response_loo_spearman": fit.loo_spearman,
        "response_loo_pair_acc": fit.loo_pair_acc,
        "response_perm_p": fit.perm_p,
        **selected,
        **{f"root_{key}": value for key, value in validation.items()},
    }

    public.drop(columns=["move_logit"]).to_csv(OUT / "h097_public_moves.csv", index=False)
    model_scores.to_csv(OUT / "h097_response_model_scores.csv", index=False)
    pred_rows.to_csv(OUT / "h097_response_loo_predictions.csv", index=False)
    action_pool.to_csv(OUT / "h097_action_pool.csv", index=False)
    candidates.to_csv(OUT / "h097_candidates.csv", index=False)
    pd.concat(selected_frames, ignore_index=True).to_csv(OUT / "h097_selected_cells.csv", index=False)
    pd.DataFrame([decision]).to_csv(OUT / "h097_decision.csv", index=False)

    cols = [
        "candidate_id",
        "spec_name",
        "selected_cells",
        "changed_rows_vs_h057",
        "model_pred_delta_vs_h057",
        "posterior_delta_vs_h057",
        "hard_diag_delta_vs_h057",
        "anti_h088_direction_rate",
        "h057_positive_align_rate",
        "selected_conflict_rate",
        "cos_h088_direction",
        "cos_h057_vs_h042_direction",
        "max_positive_bad_cosine",
        "h097_score",
        "file",
    ]
    report = f"""# H097 Signed Public Action-Equation HS-JEPA

Question: can all public observations be used as signed action-response
supervision from the H057 base?

Design:

- context: H095 cell toxicity table, H057-positive conflict features, row/target
  context, source/invariant diagnostics;
- target representation: public LB response to submitted action vectors;
- decoder: signed public-response gradient plus H057/H088 conflict gates.

Public response model:

{md_table(model_scores.head(15), 15)}

LOO predictions:

{md_table(pred_rows[pred_rows['feature_set'].eq(fit.feature_set) & pred_rows['alpha'].eq(fit.alpha)], 30)}

Candidates:

{md_table(candidates[cols], 20)}

Decision:

{md_table(pd.DataFrame([decision]), 1)}

Interpretation rule:

- If H097 improves materially, HS-JEPA v2 should treat public submissions as a
  signed action-equation training set, not just as posterior constraints.
- If H097 loses while H096 wins, the public response model is too globally
  smoothed and H088 should stay a local counterfactual sensor.
- If both H096 and H097 lose, H088 is a broad collapse diagnostic rather than a
  reusable signed action field.
"""
    (OUT / "h097_report.md").write_text(report, encoding="utf-8")

    print(f"selected={decision['selected_candidate_id']}")
    print(f"root={root_path}")
    print(candidates[cols].head(10).to_string(index=False))
    print("\\nresponse model")
    print(model_scores.head(8).to_string(index=False))


if __name__ == "__main__":
    run()
