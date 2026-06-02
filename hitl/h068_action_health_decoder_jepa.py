#!/usr/bin/env python3
"""H068: action-health decoder HS-JEPA.

H057 proved that the H042 Q2 support rows can carry a full non-Q2 hidden
human-state vector. H067 then asked whether public responsibility is row
weighted. H068 changes the object again:

    context = known public submissions as counterfactual actions around H057
    target  = public action-health gradient at row-target cell level
    action  = move only cells whose H061 posterior move is predicted healthy

This is not another row expansion. The hidden variable is "which edits are
healthy under the public listener", combining public/private action response,
target route, and H061/H067 human-state evidence.
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
ANALYSIS = ROOT / "analysis_outputs"
OUT = HITL / "h068_action_health_decoder_jepa"
OUT.mkdir(parents=True, exist_ok=True)

if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))

from public_anchor_bottleneck_decomposition import known_public_table  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
NON_Q2 = [target for target in TARGETS if target != "Q2"]
S_TARGETS = ["S1", "S2", "S3", "S4"]
KEYS = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1.0e-6

H012 = "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv"
H042 = "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv"
H050 = "submission_h050_target_route_phase_b140216b_uploadsafe.csv"
H057 = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H061 = "submission_h061_h057feedback_support_69e9c079_uploadsafe.csv"
H064 = "submission_h064_contrastive_state_graph_d09a5363_uploadsafe.csv"
H065 = "submission_h065_state_transition_phase_75d5575d_uploadsafe.csv"
H066 = "submission_h066_state_sequence_episode_route_8ca9b9b6_uploadsafe.csv"
H067 = "submission_h067_rowresp_public_state_b10ea6b8_uploadsafe.csv"

MANUAL_PUBLIC = {
    H012: (0.5681234831, "manual H012 public-equation best"),
    H042: (0.5679048248, "manual H042 Q2 phase public sensor"),
    H050: (0.5679048248, "manual H050 non-Q2 route null sensor"),
    H057: (0.5677475939, "manual H057 full-row public frontier"),
}
H057_PUBLIC = MANUAL_PUBLIC[H057][0]

BAD_ANCHORS = {
    "submission_h010_objective_s1s4_v2_uploadsafe.csv",
    "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
    "submission_jepa_latent_q2_w0p45.csv",
    "submission_jepa_latent_residual_probe.csv",
    "submission_lejepa_targetwise_strict_best_scale0p5.csv",
    "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
}


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    target_policy: str
    k: int
    alpha: float
    mode: str
    exclude_null: bool
    max_per_row: int
    q2_cap: int
    rollback_k: int
    rollback_keep: float


def import_module(path: Path, name: str) -> object:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


H055MOD = import_module(HITL / "h055_postfeedback_public_listener_jepa.py", "h055mod_for_h068")


def locate(name: str | Path) -> Path | None:
    return H055MOD.locate(name)


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    return H055MOD.load_sub(name, sample)


def clip_prob(x: np.ndarray) -> np.ndarray:
    return H055MOD.clip_prob(x)


def logit(x: np.ndarray) -> np.ndarray:
    return H055MOD.logit(x)


def sigmoid(x: np.ndarray) -> np.ndarray:
    return H055MOD.sigmoid(x)


def bce(prob: np.ndarray, q: np.ndarray) -> np.ndarray:
    return H055MOD.bce(prob, q)


def rank01(values: np.ndarray, high: bool = True) -> np.ndarray:
    return H055MOD.rank01(values, high)


def md_table(frame: pd.DataFrame, n: int = 20) -> str:
    return H055MOD.md_table(frame, n)


def write_submission(sample: pd.DataFrame, prob: np.ndarray, path: Path) -> None:
    H055MOD.write_submission(sample, prob, path)


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def move_toward(base: np.ndarray, target: np.ndarray, alpha: float, mode: str) -> np.ndarray:
    if mode == "prob":
        return clip_prob((1.0 - alpha) * base + alpha * target)
    if mode == "logit":
        return clip_prob(sigmoid((1.0 - alpha) * logit(base) + alpha * logit(target)))
    raise ValueError(mode)


def cleanup_previous_outputs() -> None:
    for path in OUT.glob("submission_h068_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h068_action_health_*_uploadsafe.csv"):
        path.unlink()


def read_public_observations() -> pd.DataFrame:
    known = known_public_table().copy()
    known["known_source"] = known.get("known_source", "known_public_table")
    manual = pd.DataFrame(
        [
            {"file": file, "public_lb": lb, "note": note, "known_source": "manual_h068"}
            for file, (lb, note) in MANUAL_PUBLIC.items()
        ]
    )
    out = pd.concat([known, manual], ignore_index=True)
    out = out.drop_duplicates("file", keep="last")
    rows = [rec for rec in out.to_dict("records") if locate(str(rec["file"])) is not None]
    return pd.DataFrame(rows).sort_values("public_lb").reset_index(drop=True)


def load_q061(sample: pd.DataFrame) -> np.ndarray:
    src = HITL / "h061_h057_feedback_support_translator_jepa" / "h061_cell_posterior.csv"
    df = pd.read_csv(src)
    mat = np.zeros((len(sample), len(TARGETS)), dtype=np.float64)
    tix = {target: i for i, target in enumerate(TARGETS)}
    for rec in df.to_dict("records"):
        mat[int(rec["row"]), tix[str(rec["target"])]] = float(rec["q061"])
    return clip_prob(mat)


def changed_rows(path: str, base_prob: np.ndarray, sample: pd.DataFrame) -> set[int]:
    resolved = locate(path)
    if resolved is None:
        return set()
    prob = load_sub(resolved, sample)[TARGETS].to_numpy(dtype=np.float64)
    return set(np.where((np.abs(prob - base_prob) > 1.0e-12).any(axis=1))[0].tolist())


def fit_origin_action_model(
    x: np.ndarray,
    y: np.ndarray,
    ridge_mult: float,
    scale: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, float]:
    if scale is None:
        scale = np.sqrt(np.mean(x * x, axis=0))
        scale = np.where(scale < 1.0e-12, 1.0, scale)
    xs = x / scale
    gram = xs @ xs.T
    diag = np.diag(gram)
    lam_scale = float(np.median(diag))
    if not np.isfinite(lam_scale) or lam_scale <= 1.0e-18:
        lam_scale = float(np.mean(diag) + 1.0e-18)
    lam = ridge_mult * lam_scale
    dual = np.linalg.pinv(gram + lam * np.eye(len(y))) @ y
    beta_scaled = xs.T @ dual
    beta = beta_scaled / scale
    return beta, scale, lam


def fit_action_health(
    known: pd.DataFrame,
    pred_by_file: dict[str, np.ndarray],
    h057_prob: np.ndarray,
    q061: np.ndarray,
) -> tuple[pd.DataFrame, dict[str, object]]:
    rows: list[dict[str, object]] = []
    x_rows: list[np.ndarray] = []
    y_vals: list[float] = []
    for rec in known.to_dict("records"):
        file = str(rec["file"])
        if file == H057 or file not in pred_by_file:
            continue
        pred = pred_by_file[file]
        x = (bce(pred, q061) - bce(h057_prob, q061)).reshape(-1)
        y = float(rec["public_lb"]) - H057_PUBLIC
        x_rows.append(x)
        y_vals.append(y)
        rows.append(
            {
                "file": file,
                "public_lb": float(rec["public_lb"]),
                "actual_delta_vs_h057": y,
                "changed_cells_vs_h057": int((np.abs(pred - h057_prob) > 1.0e-12).sum()),
                "changed_rows_vs_h057": int((np.abs(pred - h057_prob) > 1.0e-12).any(axis=1).sum()),
                "x_mean": float(x.mean()),
                "x_std": float(x.std()),
            }
        )
    x = np.vstack(x_rows)
    y = np.asarray(y_vals, dtype=np.float64)

    model_rows: list[dict[str, object]] = []
    ridge_grid = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1, 1.0, 3.0]
    for ridge in ridge_grid:
        beta, scale, lam = fit_origin_action_model(x, y, ridge)
        pred_full = x @ beta
        loo = []
        for hold in range(len(y)):
            keep = np.ones(len(y), dtype=bool)
            keep[hold] = False
            beta_k, _, _ = fit_origin_action_model(x[keep], y[keep], ridge)
            loo.append(float(x[hold] @ beta_k))
        loo = np.asarray(loo, dtype=np.float64)
        err = loo - y
        model_rows.append(
            {
                "ridge_mult": ridge,
                "lambda": lam,
                "known_fit_mae": float(np.mean(np.abs(pred_full - y))),
                "loo_mae": float(np.mean(np.abs(err))),
                "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)),
                "loo_max_abs": float(np.max(np.abs(err))),
                "pairwise_sign_acc": pairwise_sign_accuracy(loo, y),
                "beta_l1": float(np.mean(np.abs(beta))),
                "beta_std": float(np.std(beta)),
            }
        )
    model_df = pd.DataFrame(model_rows)
    model_df["selection_score"] = (
        model_df["loo_mae"].rank(method="average", pct=True)
        + 0.70 * model_df["loo_p90_abs"].rank(method="average", pct=True)
        + 0.35 * (1.0 - model_df["pairwise_sign_acc"]).rank(method="average", pct=True)
    )
    selected = model_df.sort_values(["selection_score", "loo_mae"]).iloc[0].to_dict()
    beta, scale, lam = fit_origin_action_model(x, y, float(selected["ridge_mult"]))
    pred_full = x @ beta
    loo = []
    for hold in range(len(y)):
        keep = np.ones(len(y), dtype=bool)
        keep[hold] = False
        beta_k, _, _ = fit_origin_action_model(x[keep], y[keep], float(selected["ridge_mult"]))
        loo.append(float(x[hold] @ beta_k))
    fit_df = pd.DataFrame(rows)
    fit_df["action_health_pred_delta_vs_h057"] = pred_full
    fit_df["loo_pred_delta_vs_h057"] = loo
    fit_df["loo_abs_error"] = (fit_df["loo_pred_delta_vs_h057"] - fit_df["actual_delta_vs_h057"]).abs()
    selected["beta"] = beta
    selected["scale"] = scale
    selected["model_table"] = model_df.sort_values(["selection_score", "loo_mae"]).reset_index(drop=True)
    return fit_df.sort_values("actual_delta_vs_h057").reset_index(drop=True), selected


def pairwise_sign_accuracy(pred: np.ndarray, y: np.ndarray) -> float:
    ok = total = 0
    for i in range(len(y)):
        for j in range(i + 1, len(y)):
            dy = y[i] - y[j]
            dp = pred[i] - pred[j]
            if abs(dy) < 1.0e-15 or abs(dp) < 1.0e-15:
                continue
            total += 1
            ok += int(dy * dp > 0)
    return float(ok / total) if total else 0.0


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1.0e-12))


def load_row_state(sample: pd.DataFrame, h057_prob: np.ndarray) -> pd.DataFrame:
    src = HITL / "h067_row_responsibility_public_state_jepa" / "h067_row_responsibility.csv"
    rows = pd.read_csv(src)
    for col in ["sleep_date", "lifelog_date"]:
        rows[col] = pd.to_datetime(rows[col]).dt.strftime("%Y-%m-%d")
    sample_keys = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        sample_keys[col] = pd.to_datetime(sample_keys[col]).dt.strftime("%Y-%m-%d")
    if not rows[KEYS].equals(sample_keys):
        raise ValueError("H067 row responsibility keys mismatch")
    rows["h064_changed_row_validation"] = rows["row"].isin(changed_rows(H064, h057_prob, sample)).astype(int)
    rows["h065_changed_row_validation"] = rows["row"].isin(changed_rows(H065, h057_prob, sample)).astype(int)
    rows["h066_changed_row_validation"] = rows["row"].isin(changed_rows(H066, h057_prob, sample)).astype(int)
    rows["h067_changed_row_validation"] = rows["row"].isin(changed_rows(H067, h057_prob, sample)).astype(int)
    return rows


def build_cell_table(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h050_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    beta: np.ndarray,
    row_state: pd.DataFrame,
) -> pd.DataFrame:
    target_rows = []
    target_idx = {target: i for i, target in enumerate(TARGETS)}
    support = np.abs(h057_prob - h042_prob) > 1.0e-12
    h050_changed = (np.abs(h050_prob - h042_prob) > 1.0e-12).any(axis=1)
    full_delta_loss = (bce(q061, q061) - bce(h057_prob, q061)).reshape(-1)
    pred_contrib = beta * full_delta_loss
    row_loss_delta = (bce(q061, q061) - bce(h057_prob, q061)).mean(axis=1)

    for row in range(len(sample)):
        row_rec = row_state.iloc[row]
        for target in TARGETS:
            j = target_idx[target]
            flat = row * len(TARGETS) + j
            target_rows.append(
                {
                    "row": row,
                    "subject_id": sample.loc[row, "subject_id"],
                    "sleep_date": sample.loc[row, "sleep_date"],
                    "lifelog_date": sample.loc[row, "lifelog_date"],
                    "target": target,
                    "target_index": j,
                    "flat_index": flat,
                    "h057_prob": h057_prob[row, j],
                    "h042_prob": h042_prob[row, j],
                    "q061": q061[row, j],
                    "h057_support_cell": int(support[row, j]),
                    "is_h057_seed": int(row_rec["is_h057_seed"]),
                    "is_h050_null": int(h050_changed[row] and not bool(row_rec["is_h057_seed"])),
                    "public_weight": float(row_rec["public_weight"]),
                    "public_responsibility_rank": float(row_rec["public_responsibility_rank"]),
                    "seed_responsibility_score": float(row_rec["seed_responsibility_score"]),
                    "extension_score": float(row_rec["extension_score"]),
                    "context_overlap": float(row_rec["context_overlap"]),
                    "h064_changed_row": int(row_rec["h064_changed_row_validation"]),
                    "h065_changed_row": int(row_rec["h065_changed_row_validation"]),
                    "h066_changed_row": int(row_rec["h066_changed_row_validation"]),
                    "h067_changed_row": int(row_rec["h067_changed_row_validation"]),
                    "h061_support_mean": float(row_rec["h061_support_mean"]),
                    "row_q061_gain_from_h057_nonq2": float(row_rec["row_q061_gain_from_h057_nonq2"]),
                    "row_loss_delta_to_q061": float(row_loss_delta[row]),
                    "cell_loss_delta_to_q061": float(full_delta_loss[flat]),
                    "cell_q061_gain": float(-full_delta_loss[flat]),
                    "action_beta": float(beta[flat]),
                    "pred_cell_delta_to_q061": float(pred_contrib[flat]),
                    "abs_prob_move_to_q061": float(abs(q061[row, j] - h057_prob[row, j])),
                    "abs_logit_move_to_q061": float(abs(logit(q061[row, j]) - logit(h057_prob[row, j]))),
                    "direction_to_q061": int(np.sign(logit(q061[row, j]) - logit(h057_prob[row, j]))),
                }
            )
    cells = pd.DataFrame(target_rows)
    cells["action_rank"] = rank01(-cells["pred_cell_delta_to_q061"].to_numpy())
    cells["q061_gain_rank"] = rank01(cells["cell_q061_gain"].to_numpy())
    cells["row_public_rank"] = rank01(cells["public_weight"].to_numpy())
    cells["extension_rank"] = rank01(cells["extension_score"].to_numpy())
    cells["move_rank"] = rank01(cells["abs_logit_move_to_q061"].to_numpy())
    cells["source_consensus"] = (
        cells["h064_changed_row"] + cells["h065_changed_row"] + cells["h066_changed_row"] + cells["h067_changed_row"]
    ) / 4.0
    cells["target_prior_weight"] = cells["target"].map(
        {"Q1": 0.92, "Q2": 0.62, "Q3": 0.95, "S1": 1.02, "S2": 1.05, "S3": 1.08, "S4": 1.02}
    )
    cells["h068_cell_health"] = (
        0.36 * cells["action_rank"]
        + 0.16 * cells["q061_gain_rank"]
        + 0.13 * cells["row_public_rank"]
        + 0.10 * cells["extension_rank"]
        + 0.08 * cells["source_consensus"]
        + 0.06 * cells["move_rank"]
        + 0.05 * cells["h057_support_cell"]
        + 0.04 * (cells["target"] != "Q2").astype(float)
        - 0.16 * cells["is_h050_null"]
        - 0.06 * (cells["target"] == "Q2").astype(float)
    ) * cells["target_prior_weight"]
    cells.loc[cells["cell_q061_gain"] <= 0, "h068_cell_health"] -= 0.30
    return cells.sort_values("h068_cell_health", ascending=False).reset_index(drop=True)


def target_allowed(policy: str, target: str) -> bool:
    if policy == "nonq2":
        return target != "Q2"
    if policy == "all":
        return True
    if policy == "q2lite":
        return target == "Q2"
    if policy == "s_only":
        return target in S_TARGETS
    if policy == "q_and_s":
        return target in {"Q1", "Q3", "S1", "S2", "S3", "S4"}
    raise ValueError(policy)


def select_cells(spec: CandidateSpec, cells: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    pool = cells[cells["target"].map(lambda target: target_allowed(spec.target_policy, str(target)))].copy()
    if spec.exclude_null:
        pool = pool[pool["is_h050_null"] == 0]
    pool = pool[pool["cell_q061_gain"] > 0].copy()

    selected_parts: list[pd.DataFrame] = []
    rollback = pool.iloc[0:0].copy()

    if spec.family == "cell_top":
        selected = pool.sort_values("h068_cell_health", ascending=False)
        if spec.q2_cap >= 0:
            q2 = selected[selected["target"] == "Q2"].head(spec.q2_cap)
            non = selected[selected["target"] != "Q2"]
            selected = pd.concat([non, q2], ignore_index=True).sort_values("h068_cell_health", ascending=False)
        selected = selected.head(spec.k)
    elif spec.family == "row_balanced":
        rows = pool.groupby("row", as_index=False).agg(
            row_health=("h068_cell_health", "max"),
            row_action=("pred_cell_delta_to_q061", "min"),
            row_public=("public_weight", "max"),
        )
        rows["row_score"] = 0.55 * rank01(rows["row_health"].to_numpy()) + 0.30 * rank01(
            -rows["row_action"].to_numpy()
        ) + 0.15 * rank01(rows["row_public"].to_numpy())
        rows = rows.sort_values("row_score", ascending=False)
        for row in rows["row"].astype(int):
            piece = pool[pool["row"] == row].sort_values("h068_cell_health", ascending=False).head(spec.max_per_row)
            selected_parts.append(piece)
            if sum(len(part) for part in selected_parts) >= spec.k:
                break
        selected = pd.concat(selected_parts, ignore_index=True).sort_values("h068_cell_health", ascending=False).head(spec.k)
    elif spec.family == "seed_expand":
        seed = pool[pool["is_h057_seed"] == 1].sort_values("h068_cell_health", ascending=False).head(spec.k // 2)
        ext = pool[pool["is_h057_seed"] == 0].sort_values("h068_cell_health", ascending=False).head(spec.k - len(seed))
        selected = pd.concat([seed, ext], ignore_index=True).sort_values("h068_cell_health", ascending=False)
    elif spec.family == "prune_expand":
        rollback_pool = cells[
            (cells["h057_support_cell"] == 1)
            & (cells["target"] != "Q2")
            & (cells["pred_cell_delta_to_q061"] > cells["pred_cell_delta_to_q061"].median())
        ].copy()
        rollback = rollback_pool.sort_values("h068_cell_health", ascending=True).head(spec.rollback_k)
        ext = pool[(pool["h057_support_cell"] == 0) & (pool["target"] != "Q2")].sort_values(
            "h068_cell_health", ascending=False
        )
        selected = ext.head(spec.k)
    else:
        raise ValueError(spec.family)

    selected = selected.drop_duplicates("flat_index", keep="first")
    rollback = rollback.drop_duplicates("flat_index", keep="first")
    return selected, rollback


def apply_candidate(
    spec: CandidateSpec,
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    cells: pd.DataFrame,
    beta: np.ndarray,
    bad_moves: dict[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    selected, rollback = select_cells(spec, cells)
    prob = h057_prob.copy()
    target_prob = move_toward(h057_prob, q061, spec.alpha, spec.mode)
    rollback_prob = clip_prob(h042_prob + spec.rollback_keep * (h057_prob - h042_prob))

    for rec in selected.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_index"])
        prob[row, target_idx] = target_prob[row, target_idx]
    for rec in rollback.to_dict("records"):
        row = int(rec["row"])
        target_idx = int(rec["target_index"])
        prob[row, target_idx] = rollback_prob[row, target_idx]

    changed = np.abs(prob - h057_prob) > 1.0e-12
    x = (bce(prob, q061) - bce(h057_prob, q061)).reshape(-1)
    pred_delta = float(x @ beta)
    row_delta = (bce(prob, q061) - bce(h057_prob, q061)).mean(axis=1)
    row_public = cells.drop_duplicates("row").sort_values("row")["public_weight"].to_numpy(dtype=np.float64)
    resp_delta = float(np.dot(row_public, row_delta))
    move_vec = (logit(prob) - logit(h057_prob)).reshape(-1)
    bad_cos = {f"bad_cos_{Path(name).stem[:18]}": cosine(move_vec, vec) for name, vec in bad_moves.items()}
    max_bad_cos = max([max(value, 0.0) for value in bad_cos.values()] + [0.0])
    selected_rows = set(np.where(changed.any(axis=1))[0].tolist())
    selected_detail = cells[cells["row"].isin(selected_rows)]
    meta: dict[str, object] = {
        "candidate_id": "",
        "family": spec.family,
        "target_policy": spec.target_policy,
        "k": spec.k,
        "alpha": spec.alpha,
        "mode": spec.mode,
        "exclude_null": spec.exclude_null,
        "max_per_row": spec.max_per_row,
        "q2_cap": spec.q2_cap,
        "rollback_k": spec.rollback_k,
        "rollback_keep": spec.rollback_keep,
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(changed.any(axis=1).sum()),
        "selected_cells": int(len(selected)),
        "rollback_cells": int(len(rollback)),
        "public_action_pred_delta_vs_h057": pred_delta,
        "posterior_delta_vs_h057": float(x.mean()),
        "responsibility_weighted_delta_vs_h057": resp_delta,
        "max_positive_bad_cosine": max_bad_cos,
        "mean_selected_cell_health": float(selected["h068_cell_health"].mean()) if len(selected) else 0.0,
        "mean_selected_public_weight": float(selected_detail["public_weight"].mean()) if len(selected_detail) else 0.0,
        "h050_null_rows_selected": int(selected_detail["is_h050_null"].max() if len(selected_detail) else 0),
        "h050_null_cell_count": int(selected["is_h050_null"].sum()) if len(selected) else 0,
        "selected_subjects": int(selected_detail["subject_id"].nunique()) if len(selected_detail) else 0,
        "selected_rows": ",".join(map(str, sorted(selected_rows))),
    }
    meta.update(bad_cos)
    for target in TARGETS:
        meta[f"{target}_changed_vs_h057"] = int(changed[:, TARGETS.index(target)].sum())
    return clip_prob(prob), meta


def candidate_sweep(
    sample: pd.DataFrame,
    h042_prob: np.ndarray,
    h057_prob: np.ndarray,
    q061: np.ndarray,
    cells: pd.DataFrame,
    beta: np.ndarray,
    pred_by_file: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    bad_moves = {}
    for name in BAD_ANCHORS:
        if name in pred_by_file:
            bad_moves[name] = (logit(pred_by_file[name]) - logit(h057_prob)).reshape(-1)

    specs: list[CandidateSpec] = []
    for family in ["cell_top", "row_balanced", "seed_expand", "prune_expand"]:
        target_policies = ["nonq2", "s_only", "q_and_s"] if family != "cell_top" else ["nonq2", "all", "q2lite", "s_only", "q_and_s"]
        for target_policy in target_policies:
            for k in [180, 270, 360, 520, 700, 900]:
                for alpha in [0.60, 0.85, 1.00, 1.20]:
                    for mode in ["logit", "prob"]:
                        for exclude_null in [True, False]:
                            for max_per_row in ([3, 4, 6] if family == "row_balanced" else [7]):
                                for q2_cap in ([0, 24, 45, 70] if target_policy in {"all", "q2lite"} else [0]):
                                    if target_policy == "q2lite" and q2_cap == 0:
                                        continue
                                    for rollback_k in ([0, 24, 48] if family == "prune_expand" else [0]):
                                        for rollback_keep in ([0.0, 0.45, 0.75] if rollback_k else [1.0]):
                                            specs.append(
                                                CandidateSpec(
                                                    family=family,
                                                    target_policy=target_policy,
                                                    k=k,
                                                    alpha=alpha,
                                                    mode=mode,
                                                    exclude_null=exclude_null,
                                                    max_per_row=max_per_row,
                                                    q2_cap=q2_cap,
                                                    rollback_k=rollback_k,
                                                    rollback_keep=rollback_keep,
                                                )
                                            )

    rows: list[dict[str, object]] = []
    probs: dict[str, np.ndarray] = {}
    seen: set[str] = set()
    for spec in specs:
        prob, meta = apply_candidate(spec, sample, h042_prob, h057_prob, q061, cells, beta, bad_moves)
        if meta["changed_cells_vs_h057"] == 0:
            continue
        digest = short_hash(prob)
        if digest in seen:
            continue
        seen.add(digest)
        cid = (
            f"h068_{spec.family}_{spec.target_policy}_k{spec.k}_a{str(spec.alpha).replace('.', 'p')}_"
            f"{spec.mode}_null{int(spec.exclude_null)}_r{spec.rollback_k}_{digest}"
        )
        meta["candidate_id"] = cid
        meta["hash"] = digest
        rows.append(meta)
        probs[cid] = prob

    cand = pd.DataFrame(rows)
    if cand.empty:
        raise RuntimeError("no H068 candidates generated")
    cand["action_rank"] = rank01(-cand["public_action_pred_delta_vs_h057"].to_numpy())
    cand["posterior_rank"] = rank01(-cand["posterior_delta_vs_h057"].to_numpy())
    cand["responsibility_rank"] = rank01(-cand["responsibility_weighted_delta_vs_h057"].to_numpy())
    cand["bad_avoid_rank"] = rank01(-cand["max_positive_bad_cosine"].to_numpy())
    cand["cell_health_rank"] = rank01(cand["mean_selected_cell_health"].to_numpy())
    cand["public_weight_rank"] = rank01(cand["mean_selected_public_weight"].to_numpy())
    cand["size_score"] = 1.0 - (cand["changed_cells_vs_h057"] - 520).abs() / 680.0
    cand["size_score"] = cand["size_score"].clip(0.0, 1.0)
    cand["row_size_score"] = 1.0 - (cand["changed_rows_vs_h057"] - 90).abs() / 120.0
    cand["row_size_score"] = cand["row_size_score"].clip(0.0, 1.0)
    cand["null_penalty"] = (cand["h050_null_cell_count"] / cand["selected_cells"].clip(lower=1)).clip(0.0, 1.0)
    cand["q2_risk"] = (cand["Q2_changed_vs_h057"] / cand["changed_cells_vs_h057"].clip(lower=1)).clip(0.0, 1.0)
    cand["h068_score"] = (
        0.31 * cand["action_rank"]
        + 0.18 * cand["posterior_rank"]
        + 0.15 * cand["responsibility_rank"]
        + 0.11 * cand["bad_avoid_rank"]
        + 0.08 * cand["cell_health_rank"]
        + 0.06 * cand["public_weight_rank"]
        + 0.05 * cand["size_score"]
        + 0.04 * cand["row_size_score"]
        + 0.04 * (cand["target_policy"] != "q2lite").astype(float)
        - 0.08 * cand["null_penalty"]
        - 0.04 * cand["q2_risk"]
    )
    cand = cand.sort_values(["h068_score", "public_action_pred_delta_vs_h057"], ascending=[False, True]).reset_index(drop=True)
    for _, row in cand.head(120).iterrows():
        cid = str(row["candidate_id"])
        file = OUT / f"submission_{cid}.csv"
        write_submission(sample, probs[cid], file)
        cand.loc[cand["candidate_id"].eq(cid), "file"] = file.name
        cand.loc[cand["candidate_id"].eq(cid), "resolved_path"] = str(file.resolve())
    return cand, probs


def validate_submission(path: Path, sample: pd.DataFrame, h057_prob: np.ndarray) -> dict[str, object]:
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"])
    df = df.sort_values(KEYS).reset_index(drop=True)
    prob = df[TARGETS].to_numpy(dtype=np.float64)
    return {
        "path": str(path.resolve()),
        "rows": len(df),
        "keys_match": bool(df[KEYS].equals(sample[KEYS])),
        "duplicate_keys": int(df.duplicated(KEYS).sum()),
        "nan_cells": int(df[TARGETS].isna().sum().sum()),
        "min_prob": float(np.nanmin(prob)),
        "max_prob": float(np.nanmax(prob)),
        "q2_changed_vs_h057_validation": int((np.abs(prob[:, TARGETS.index("Q2")] - h057_prob[:, TARGETS.index("Q2")]) > 1.0e-12).sum()),
        "changed_cells_vs_h057_validation": int((np.abs(prob - h057_prob) > 1.0e-12).sum()),
        "upload_safe": bool(
            len(df) == len(sample)
            and df[KEYS].equals(sample[KEYS])
            and df.duplicated(KEYS).sum() == 0
            and df[TARGETS].isna().sum().sum() == 0
            and np.nanmin(prob) >= 0.0
            and np.nanmax(prob) <= 1.0
        ),
    }


def write_report(
    known: pd.DataFrame,
    fit: pd.DataFrame,
    model_table: pd.DataFrame,
    cells: pd.DataFrame,
    cand: pd.DataFrame,
    decision: pd.DataFrame,
) -> None:
    summary = pd.DataFrame(
        [
            {
                "public_observations": len(known),
                "fit_equations_vs_h057": len(fit),
                "selected_ridge_mult": float(model_table.iloc[0]["ridge_mult"]),
                "action_fit_loo_mae": float(model_table.iloc[0]["loo_mae"]),
                "action_fit_loo_p90": float(model_table.iloc[0]["loo_p90_abs"]),
                "top_candidate": str(decision.iloc[0]["selected_candidate_id"]),
                "top_changed_cells": int(decision.iloc[0]["changed_cells_vs_h057"]),
                "top_changed_rows": int(decision.iloc[0]["changed_rows_vs_h057"]),
                "top_q2_changed": int(decision.iloc[0]["Q2_changed_vs_h057"]),
                "top_pred_delta": float(decision.iloc[0]["public_action_pred_delta_vs_h057"]),
                "top_posterior_delta": float(decision.iloc[0]["posterior_delta_vs_h057"]),
            }
        ]
    )
    report = "\n".join(
        [
            "# H068 Action-Health Decoder HS-JEPA",
            "",
            "Question: is the post-H057 bottleneck row identity, or the health of the",
            "cell-level action itself under the public listener?",
            "",
            "Design:",
            "",
            "- base: H057 public frontier;",
            "- context: known public submissions as H057-relative counterfactual actions;",
            "- target: cell-level public action-health gradient fitted with an origin-constrained ridge;",
            "- action: move only H061 posterior cells whose action is predicted healthy;",
            "- stress: known-action LOO, bad-anchor cosine, H067 row responsibility, H050-null avoidance.",
            "",
            "Summary:",
            "",
            md_table(summary),
            "",
            "Action-health model sweep:",
            "",
            md_table(model_table, 12),
            "",
            "Known public action fit:",
            "",
            md_table(fit, 28),
            "",
            "Top cell-health targets:",
            "",
            md_table(
                cells[
                    [
                        "row",
                        "subject_id",
                        "sleep_date",
                        "target",
                        "h057_prob",
                        "q061",
                        "cell_q061_gain",
                        "pred_cell_delta_to_q061",
                        "h068_cell_health",
                        "is_h057_seed",
                        "is_h050_null",
                        "public_weight",
                        "source_consensus",
                    ]
                ],
                30,
            ),
            "",
            "Top candidates:",
            "",
            md_table(cand.head(30)),
            "",
            "Decision:",
            "",
            md_table(decision),
            "",
            "Interpretation rule:",
            "",
            "- If H068 improves over H057/H067, HS-JEPA's next object is action-health, not row expansion.",
            "- If H068 loses while H067 wins, public-state is row-responsibility weighted and the cell action decoder overfits.",
            "- If both H067/H068 lose, H057 remains a compact public-specific hidden state until new public feedback arrives.",
            "",
        ]
    )
    (OUT / "h068_report.md").write_text(report)


def main() -> None:
    cleanup_previous_outputs()
    known = read_public_observations()
    h057_df = load_sub(H057)
    sample = h057_df[KEYS].copy()
    h057_prob = h057_df[TARGETS].to_numpy(dtype=np.float64)
    h042_prob = load_sub(H042, sample)[TARGETS].to_numpy(dtype=np.float64)
    h050_prob = load_sub(H050, sample)[TARGETS].to_numpy(dtype=np.float64)
    q061 = load_q061(sample)

    pred_by_file = {}
    for file in known["file"].astype(str):
        pred_by_file[file] = load_sub(file, sample)[TARGETS].to_numpy(dtype=np.float64)
    for file in [H061, H064, H065, H066, H067]:
        if locate(file) is not None and file not in pred_by_file:
            pred_by_file[file] = load_sub(file, sample)[TARGETS].to_numpy(dtype=np.float64)

    fit, model = fit_action_health(known, pred_by_file, h057_prob, q061)
    model_table = model["model_table"]
    beta = np.asarray(model["beta"], dtype=np.float64)
    row_state = load_row_state(sample, h057_prob)
    cells = build_cell_table(sample, h042_prob, h050_prob, h057_prob, q061, beta, row_state)
    cand, probs = candidate_sweep(sample, h042_prob, h057_prob, q061, cells, beta, pred_by_file)

    selected = cand.iloc[0].copy()
    selected_file = OUT / str(selected["file"])
    digest = str(selected["hash"])
    root_file = ROOT / f"submission_h068_action_health_{digest}_uploadsafe.csv"
    shutil.copyfile(selected_file, root_file)
    validation = validate_submission(root_file, sample, h057_prob)
    if not validation["upload_safe"]:
        raise RuntimeError(f"selected submission is not upload safe: {validation}")

    decision = pd.DataFrame(
        [
            {
                "decision": "promote_action_health_public_state_sensor",
                "selected_candidate_id": str(selected["candidate_id"]),
                "selected_file": str(selected["file"]),
                "selected_resolved_path": str(selected["resolved_path"]),
                "root_uploadsafe_path": str(root_file.resolve()),
                "worldview": "public listener judges cell-level action-health, not just row membership",
                **selected.to_dict(),
                **validation,
            }
        ]
    )

    known.to_csv(OUT / "h068_augmented_public_observations.csv", index=False)
    model_table.to_csv(OUT / "h068_action_model_scores.csv", index=False)
    fit.to_csv(OUT / "h068_known_action_fit.csv", index=False)
    cells.to_csv(OUT / "h068_cell_action_health.csv", index=False)
    cand.to_csv(OUT / "h068_candidate_scores.csv", index=False)
    decision.to_csv(OUT / "h068_decision.csv", index=False)
    write_report(known, fit, model_table, cells, cand, decision)
    print(decision[["selected_candidate_id", "root_uploadsafe_path", "changed_cells_vs_h057", "changed_rows_vs_h057", "Q2_changed_vs_h057", "public_action_pred_delta_vs_h057", "posterior_delta_vs_h057"]].to_string(index=False))


if __name__ == "__main__":
    main()
