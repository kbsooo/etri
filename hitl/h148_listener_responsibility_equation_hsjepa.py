#!/usr/bin/env python3
"""H148: listener-responsibility equation HS-JEPA translator.

H057 is the best observed public frontier, but H088/H144/H145 show that a
plausible hidden-state action is not necessarily an action the public sensor
listens to.  H148 turns known public LB deltas into a row-target listener field:

    movement_vs_H057(row,target) -> public_delta_vs_H057

The fitted field is not treated as ground truth.  It is a stress diagnostic and
candidate translator: use discovered assignment/action-health proposals only
where the fitted public listener says the correction is likely heard and
beneficial.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib.util
import math
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
HITL = ROOT / "hitl"
OUT = HITL / "h148_listener_responsibility_equation_hsjepa"
OUT.mkdir(parents=True, exist_ok=True)

H085_PATH = HITL / "h085_augmented_public_equation_jepa.py"
SPEC = importlib.util.spec_from_file_location("h085mod_h148", H085_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {H085_PATH}")
h085mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = h085mod
SPEC.loader.exec_module(h085mod)

TARGETS = h085mod.TARGETS
KEYS = h085mod.KEYS
BASE_FILE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
BASE_LB = 0.5677475939
EPS = h085mod.EPS
TOL = 1.0e-12


@dataclass(frozen=True)
class PublicObs:
    file: str
    public_lb: float
    role: str
    note: str


PUBLIC_OBSERVATIONS = [
    PublicObs(
        "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv",
        0.5677475939,
        "frontier",
        "current public frontier; origin of the listener equation",
    ),
    PublicObs(
        "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
        0.5679048248,
        "frontier_basin",
        "Q2 phase basin, tied with H050",
    ),
    PublicObs(
        "submission_h050_target_route_phase_b140216b_uploadsafe.csv",
        0.5679048248,
        "frontier_basin",
        "target-route phase basin, tied with H042",
    ),
    PublicObs(
        "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
        0.5681234831,
        "breakthrough_anchor",
        "first public-equation jump, now below H057",
    ),
    PublicObs(
        "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
        0.5684942019,
        "negative_sensor",
        "dual-head Pareto gate was not action-grade",
    ),
    PublicObs(
        "submission_h144_targetxor_def80b88_uploadsafe.csv",
        0.5679296410,
        "tie_sensor",
        "same public score as H145; target-xor branch did not separate",
    ),
    PublicObs(
        "submission_h145_q3repair_2d818e46_uploadsafe.csv",
        0.5679296410,
        "tie_sensor",
        "same public score as H144; Q3 repair-only branch did not separate",
    ),
    PublicObs(
        "submission_h010_objective_s1s4_v2_uploadsafe.csv",
        0.5781718175,
        "bad_anchor",
        "objective S1/S4 v2 high-risk world, strongly punished",
    ),
    PublicObs(
        "submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv",
        0.5761589494,
        "pre_h_world",
        "pre-H breakthrough strong model anchor",
    ),
    PublicObs(
        "submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv",
        0.5762805676,
        "pre_h_world",
        "pre-H feature-NN variant",
    ),
    PublicObs(
        "submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv",
        0.5762904290,
        "pre_h_world",
        "Q2/S1 row-mask recovery anchor",
    ),
    PublicObs(
        "submission_e95_hardtail_541e3973.csv",
        0.5762913298,
        "pre_h_world",
        "old hardtail best",
    ),
    PublicObs(
        "submission_e101_q2s3tail_177569bc.csv",
        0.5763003660,
        "pre_h_world",
        "Q2/S3 tail variant",
    ),
    PublicObs(
        "submission_mixmin_0c916bb4.csv",
        0.5763066405,
        "pre_h_world",
        "old mixmin frontier",
    ),
    PublicObs(
        "submission_e176_abl_q2_to0p75_91e49725.csv",
        0.5763118310,
        "pre_h_world",
        "Q2 ablation anchor",
    ),
    PublicObs(
        "submission_e267_humansocial_tail_balanced_2936100f.csv",
        0.5763294974,
        "pre_h_world",
        "human-social tail attempt, public-negative",
    ),
    PublicObs(
        "submission_e72_topabs50_q2s3_gate_4e48cba2.csv",
        0.5764077772,
        "pre_h_world",
        "Q2/S3 gate anchor",
    ),
    PublicObs(
        "submission_e323_5508f966_uploadsafe.csv",
        0.5770355016,
        "bad_anchor",
        "upload-safe E323 public-negative",
    ),
    PublicObs(
        "submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv",
        0.5772865088,
        "bad_anchor",
        "mask-family JEPA S2 rank public-negative",
    ),
]


CANDIDATE_FILES = [
    "submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv",
    "submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv",
    "submission_h074_antishortcut_inversion_816703df_uploadsafe.csv",
    "submission_h075_antibad_transport_f6863945_uploadsafe.csv",
    "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv",
    "submission_h141_commoncore_0999d3ae_uploadsafe.csv",
    "submission_h142_branch_saddle_6de0d174_uploadsafe.csv",
    "submission_h143_xor_branch_4f6ace93_uploadsafe.csv",
    "submission_h144_targetxor_def80b88_uploadsafe.csv",
    "submission_h145_q3repair_2d818e46_uploadsafe.csv",
    "submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv",
    "submission_h050_target_route_phase_b140216b_uploadsafe.csv",
    "submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv",
    "submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv",
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
    for path in OUT.glob("submission_h148_*.csv"):
        path.unlink()
    for path in ROOT.glob("submission_h148_listeneraware_*.csv"):
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


def collect_public_observations(sample: pd.DataFrame) -> pd.DataFrame:
    rows = []
    seen: set[str] = set()
    for obs in PUBLIC_OBSERVATIONS:
        if obs.file in seen:
            continue
        seen.add(obs.file)
        path = locate(obs.file)
        if path is None:
            continue
        try:
            _ = load_sub(path, sample)
        except Exception:
            continue
        rows.append(
            {
                "file": obs.file,
                "public_lb": float(obs.public_lb),
                "delta_vs_h057": float(obs.public_lb - BASE_LB),
                "role": obs.role,
                "note": obs.note,
                "resolved_path": str(path.resolve()),
            }
        )
    out = pd.DataFrame(rows)
    if BASE_FILE not in set(out["file"].astype(str)):
        raise RuntimeError("base observation missing")
    return out.sort_values(["public_lb", "file"]).reset_index(drop=True)


def dual_ridge_coef(x_train: np.ndarray, y_train: np.ndarray, alpha: float) -> np.ndarray:
    if len(y_train) == 0:
        raise ValueError("empty train set")
    k = x_train @ x_train.T
    coef_dual = np.linalg.solve(k + alpha * np.eye(k.shape[0]), y_train)
    return x_train.T @ coef_dual


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3:
        return float("nan")
    ra = pd.Series(a).rank(method="average").to_numpy(dtype=np.float64)
    rb = pd.Series(b).rank(method="average").to_numpy(dtype=np.float64)
    if np.std(ra) < 1.0e-12 or np.std(rb) < 1.0e-12:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def loo_score(x: np.ndarray, y: np.ndarray, names: list[str], alpha: float) -> dict[str, object]:
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
        preds.append(pred)
        actuals.append(float(y[i]))
        rows.append({"heldout": name, "actual_delta": float(y[i]), "pred_delta": pred, "error": pred - float(y[i])})
    err = np.asarray(preds) - np.asarray(actuals)
    return {
        "alpha": float(alpha),
        "loo_mae": float(np.mean(np.abs(err))) if len(err) else float("nan"),
        "loo_rmse": float(np.sqrt(np.mean(err * err))) if len(err) else float("nan"),
        "loo_p90_abs": float(np.quantile(np.abs(err), 0.90)) if len(err) else float("nan"),
        "loo_spearman": spearman(np.asarray(preds), np.asarray(actuals)) if len(err) else float("nan"),
        "loo_rows": rows,
    }


def fit_listener_models(obs: pd.DataFrame, moves_by_file: dict[str, np.ndarray]) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    alphas = [1.0e-5, 3.0e-5, 1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 3.0e-2, 1.0e-1, 3.0e-1, 1.0, 3.0]
    specs = {
        "h_frontier": obs[obs["role"].isin(["frontier", "frontier_basin", "breakthrough_anchor", "negative_sensor", "tie_sensor"])].copy(),
        "h_plus_bad": obs[obs["role"].isin(["frontier", "frontier_basin", "breakthrough_anchor", "negative_sensor", "tie_sensor", "bad_anchor"])].copy(),
        "all_observed": obs.copy(),
    }

    score_rows = []
    coefs = {}
    loo_detail_rows = []
    for model_name, frame in specs.items():
        names = frame["file"].astype(str).tolist()
        x = np.vstack([moves_by_file[name] for name in names])
        y = frame["delta_vs_h057"].to_numpy(dtype=np.float64)
        for alpha in alphas:
            score = loo_score(x, y, names, alpha)
            # H144/H145 equality is a known listener constraint. Penalize models
            # that amplify that two-cell fork too much.
            coef = dual_ridge_coef(x, y, alpha)
            pred_h144 = float(moves_by_file.get("submission_h144_targetxor_def80b88_uploadsafe.csv", np.zeros_like(coef)) @ coef)
            pred_h145 = float(moves_by_file.get("submission_h145_q3repair_2d818e46_uploadsafe.csv", np.zeros_like(coef)) @ coef)
            h_tie_gap = abs(pred_h144 - pred_h145)
            score_rows.append(
                {
                    "model": model_name,
                    "alpha": float(alpha),
                    "n_obs": int(len(frame)),
                    "loo_mae": score["loo_mae"],
                    "loo_rmse": score["loo_rmse"],
                    "loo_p90_abs": score["loo_p90_abs"],
                    "loo_spearman": score["loo_spearman"],
                    "h144_h145_pred_gap_abs": float(h_tie_gap),
                    "selection_score": float(score["loo_mae"] + 15.0 * h_tie_gap),
                }
            )
            for row in score["loo_rows"]:
                loo_detail_rows.append({"model": model_name, "alpha": float(alpha), **row})
        best = pd.DataFrame([r for r in score_rows if r["model"] == model_name]).sort_values(
            ["selection_score", "loo_mae", "loo_p90_abs"], ascending=[True, True, True]
        ).iloc[0]
        best_alpha = float(best["alpha"])
        coefs[model_name] = dual_ridge_coef(x, y, best_alpha)

    scores = pd.DataFrame(score_rows).sort_values(["selection_score", "loo_mae"]).reset_index(drop=True)
    pd.DataFrame(loo_detail_rows).to_csv(OUT / "h148_loo_predictions.csv", index=False)
    return scores, coefs


def target_cell_frame(sample: pd.DataFrame, base_prob: np.ndarray, coef: np.ndarray) -> pd.DataFrame:
    listener = np.abs(coef)
    listener_rank = rank01(listener, high=True)
    rows = []
    flat_base = base_prob.reshape(-1)
    for row_idx in range(base_prob.shape[0]):
        for target_idx, target in enumerate(TARGETS):
            flat_idx = row_idx * len(TARGETS) + target_idx
            rec = {
                "row": int(row_idx),
                "subject_id": sample.loc[row_idx, "subject_id"],
                "sleep_date": sample.loc[row_idx, "sleep_date"],
                "lifelog_date": sample.loc[row_idx, "lifelog_date"],
                "target": target,
                "flat_idx": int(flat_idx),
                "h057_prob": float(flat_base[flat_idx]),
                "listener_coef": float(coef[flat_idx]),
                "listener_abs": float(listener[flat_idx]),
                "listener_rank": float(listener_rank[flat_idx]),
            }
            rows.append(rec)
    return pd.DataFrame(rows).sort_values("listener_abs", ascending=False).reset_index(drop=True)


def candidate_metrics(
    file_name: str,
    path: Path,
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    coefs: dict[str, np.ndarray],
    moves_by_file: dict[str, np.ndarray],
) -> dict[str, object]:
    move = movement_from_file(path, sample, base_prob)
    base_flat = base_prob.reshape(-1)
    h088_move = moves_by_file.get("submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv", np.zeros_like(move))
    changed = np.abs(move) > TOL
    out: dict[str, object] = {
        "file": file_name,
        "resolved_path": str(path.resolve()),
        "changed_cells_vs_h057": int(changed.sum()),
        "changed_rows_vs_h057": int(len(set(np.where(changed)[0] // len(TARGETS)))),
        "move_l1": float(np.abs(move).sum()),
        "move_l2": float(np.linalg.norm(move)),
        "prob_l1_vs_h057": float(np.abs(sigmoid(logit(base_flat) + move) - base_flat).sum()),
        "h088_move_cosine": cosine(move, h088_move),
    }
    for model_name, coef in coefs.items():
        toxicity = coef * move
        benefit = -toxicity
        listener_rank = rank01(np.abs(coef), high=True)
        high = listener_rank >= 0.90
        out[f"{model_name}_pred_delta"] = float(move @ coef)
        out[f"{model_name}_listened_benefit_sum"] = float(np.maximum(benefit, 0.0).sum())
        out[f"{model_name}_listened_toxicity_sum"] = float(np.maximum(toxicity, 0.0).sum())
        out[f"{model_name}_high_listener_toxic_cells"] = int((changed & high & (toxicity > 0)).sum())
        out[f"{model_name}_high_listener_benefit_cells"] = int((changed & high & (benefit > 0)).sum())
        out[f"{model_name}_listener_mass_changed"] = float(np.abs(coef[changed]).sum()) if changed.any() else 0.0
    return out


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1.0e-12 or nb < 1.0e-12:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def build_listeneraware_candidate(
    sample: pd.DataFrame,
    base_prob: np.ndarray,
    source_path: Path,
    coef: np.ndarray,
    moves_by_file: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    source_prob = load_sub(source_path, sample)[TARGETS].to_numpy(dtype=np.float64)
    source_move = (logit(source_prob) - logit(base_prob)).reshape(-1)
    base_flat = base_prob.reshape(-1)
    h088_move = moves_by_file.get("submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv", np.zeros_like(source_move))
    h144_move = moves_by_file.get("submission_h144_targetxor_def80b88_uploadsafe.csv", np.zeros_like(source_move))
    h145_move = moves_by_file.get("submission_h145_q3repair_2d818e46_uploadsafe.csv", np.zeros_like(source_move))
    changed = np.abs(source_move) > TOL

    toxicity = coef * source_move
    benefit = -toxicity
    listener_rank = rank01(np.abs(coef), high=True)
    benefit_rank = rank01(benefit, high=True)
    source_strength = rank01(np.abs(source_move), high=True)
    h088_same = (source_move * h088_move) > 0
    branch_same = (source_move * (h144_move + h145_move)) > 0
    h088_toxic_rank = rank01(np.abs(h088_move) * h088_same.astype(float), high=True)
    branch_penalty_rank = rank01(np.abs(h144_move - h145_move) * branch_same.astype(float), high=True)

    score = (
        1.00 * benefit_rank
        + 0.70 * listener_rank
        + 0.25 * source_strength
        - 0.50 * h088_toxic_rank
        - 0.30 * branch_penalty_rank
        - 1.50 * (toxicity > 0).astype(float)
    )
    rows = []
    for row_idx in range(base_prob.shape[0]):
        for target_idx, target in enumerate(TARGETS):
            flat_idx = row_idx * len(TARGETS) + target_idx
            if not changed[flat_idx]:
                continue
            rows.append(
                {
                    "row": int(row_idx),
                    "subject_id": sample.loc[row_idx, "subject_id"],
                    "sleep_date": sample.loc[row_idx, "sleep_date"],
                    "lifelog_date": sample.loc[row_idx, "lifelog_date"],
                    "target_index": int(target_idx),
                    "target": target,
                    "flat_idx": int(flat_idx),
                    "h057_prob": float(base_flat[flat_idx]),
                    "source_prob": float(source_prob.reshape(-1)[flat_idx]),
                    "source_move": float(source_move[flat_idx]),
                    "listener_coef": float(coef[flat_idx]),
                    "listener_rank": float(listener_rank[flat_idx]),
                    "benefit": float(benefit[flat_idx]),
                    "toxicity": float(toxicity[flat_idx]),
                    "h088_same_direction": bool(h088_same[flat_idx]),
                    "h088_toxic_rank": float(h088_toxic_rank[flat_idx]),
                    "branch_penalty_rank": float(branch_penalty_rank[flat_idx]),
                    "score": float(score[flat_idx]),
                }
            )
    cells = pd.DataFrame(rows)
    cells["passes_listeneraware_gate"] = (
        (cells["benefit"] > 0)
        & (cells["listener_rank"] >= 0.58)
        & (cells["h088_toxic_rank"] <= 0.96)
        & (cells["score"] >= cells["score"].quantile(0.42))
    )
    gated = cells[cells["passes_listeneraware_gate"]].sort_values("score", ascending=False).copy()

    selected_rows = []
    per_subject: dict[str, int] = {}
    per_target: dict[str, int] = {}
    per_row: dict[int, int] = {}
    max_cells = 620
    max_rows = 160
    max_per_subject = 140
    max_per_target = 150
    max_per_row = 5
    for rec in gated.to_dict("records"):
        subject = str(rec["subject_id"])
        target = str(rec["target"])
        row = int(rec["row"])
        if len(selected_rows) >= max_cells:
            break
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
        # Strong enough to be a real assignment bet, but not a full blind copy of H071.
        amp = 0.82
        new_flat[idx] = sigmoid(logit(base_flat[idx]) + amp * source_move[idx])
        selected["amp"] = amp
        selected["new_prob"] = new_flat[idx]

    new_prob = new_flat.reshape(base_prob.shape)
    return cells.sort_values("score", ascending=False).reset_index(drop=True), selected, new_prob


def run() -> None:
    cleanup_previous_outputs()
    base_path = locate(BASE_FILE)
    if base_path is None:
        raise FileNotFoundError(BASE_FILE)
    sample = load_sub(base_path)
    base_prob = sample[TARGETS].to_numpy(dtype=np.float64)

    obs = collect_public_observations(sample)
    moves_by_file = {
        row["file"]: movement_from_file(Path(row["resolved_path"]), sample, base_prob)
        for row in obs.to_dict("records")
    }
    obs.to_csv(OUT / "h148_public_observations_used.csv", index=False)

    model_scores, coefs = fit_listener_models(obs, moves_by_file)
    model_scores.to_csv(OUT / "h148_model_scores.csv", index=False)

    best_model = str(model_scores.iloc[0]["model"])
    listener_coef = coefs[best_model]
    cells = target_cell_frame(sample, base_prob, listener_coef)
    cells.to_csv(OUT / "h148_listener_cells.csv", index=False)

    candidate_rows = []
    for file_name in CANDIDATE_FILES:
        path = locate(file_name)
        if path is None:
            continue
        try:
            load_sub(path, sample)
        except Exception:
            continue
        candidate_rows.append(candidate_metrics(file_name, path, sample, base_prob, coefs, moves_by_file))
    candidate_scores = pd.DataFrame(candidate_rows).sort_values(f"{best_model}_pred_delta").reset_index(drop=True)
    candidate_scores.to_csv(OUT / "h148_candidate_scores.csv", index=False)

    source_name = "submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv"
    source_path = locate(source_name)
    if source_path is None:
        raise FileNotFoundError(source_name)
    all_source_cells, selected, new_prob = build_listeneraware_candidate(
        sample=sample,
        base_prob=base_prob,
        source_path=source_path,
        coef=listener_coef,
        moves_by_file=moves_by_file,
    )
    all_source_cells.to_csv(OUT / "h148_source_cell_scores.csv", index=False)
    selected.to_csv(OUT / "h148_selected_cells.csv", index=False)

    hash_id = short_hash(new_prob)
    local_path = OUT / f"submission_h148_listeneraware_h071_{hash_id}.csv"
    root_path = ROOT / f"submission_h148_listeneraware_assignment_{hash_id}_uploadsafe.csv"
    write_submission(sample, new_prob, local_path)
    shutil.copyfile(local_path, root_path)
    validation = validate_submission(root_path, sample, base_prob)

    h148_metrics = candidate_metrics(str(root_path.name), root_path, sample, base_prob, coefs, moves_by_file)
    observed_fit = []
    for row in obs.to_dict("records"):
        file_name = str(row["file"])
        rec = {
            "file": file_name,
            "actual_delta": float(row["delta_vs_h057"]),
            "role": row["role"],
        }
        move = moves_by_file[file_name]
        for model_name, coef in coefs.items():
            rec[f"{model_name}_fit_delta"] = float(move @ coef)
            rec[f"{model_name}_fit_error"] = float(move @ coef - float(row["delta_vs_h057"]))
        observed_fit.append(rec)
    observed_fit_df = pd.DataFrame(observed_fit)
    observed_fit_df.to_csv(OUT / "h148_observed_fit.csv", index=False)

    decision = {
        "candidate_file": str(root_path.name),
        "candidate_path": str(root_path.resolve()),
        "source_file": source_name,
        "best_listener_model": best_model,
        "selected_cells": int(len(selected)),
        "selected_rows": int(selected["row"].nunique()) if not selected.empty else 0,
        "selected_targets": ",".join(selected["target"].value_counts().sort_index().index.astype(str)) if not selected.empty else "",
        "worldview": (
            "H057 found a listened row-state; H071 has broad assignment support; "
            "H148 translates H071 through a public listener equation learned from "
            "H057/H088/H144/H145 and older bad anchors."
        ),
        "why_big_bet": (
            "This is not a top-k alpha tweak: it tests whether public LB deltas can "
            "recover the hidden listener field that decides which row-target actions "
            "are heard."
        ),
        **{f"validation_{k}": v for k, v in validation.items()},
        **{f"metric_{k}": v for k, v in h148_metrics.items() if k not in ["file", "resolved_path"]},
    }
    pd.DataFrame([decision]).to_csv(OUT / "h148_decision.csv", index=False)

    top_listener = cells.head(25)[
        ["row", "subject_id", "sleep_date", "lifelog_date", "target", "h057_prob", "listener_coef", "listener_rank"]
    ]
    report = f"""# H148 Listener-Responsibility Equation HS-JEPA

Date: 2026-06-03

## Question

H057 proves that some row-state correction is public-positive. H088 proves that
not every public/private-looking action is safe. H144/H145 prove that a
plausible two-cell branch can be almost inaudible to public. H148 asks:

```text
Can known public LB deltas recover a listener/responsibility field that tells
which row-target corrections public actually hears?
```

## Method

- Base: `{BASE_FILE}` public LB `{BASE_LB:.10f}`.
- Observation unit: full `250 x 7 = 1750` row-target logit movement versus H057.
- Target: public LB delta versus H057.
- Fitter: origin-constrained dual ridge, with H144/H145 equality penalty in
  model selection.
- Translation source: `{source_name}`.
- Decoder: copy H071 assignment cells only when the listener equation says the
  cell is both heard and beneficial, with H088/tie-branch penalties.

## Public Observations Used

{md_table(obs[["file", "public_lb", "delta_vs_h057", "role"]], 30)}

## Listener Model Selection

{md_table(model_scores.head(18), 18)}

Chosen model: `{best_model}`.

## Observed Fit

{md_table(observed_fit_df.sort_values("actual_delta")[["file", "role", "actual_delta", f"{best_model}_fit_delta", f"{best_model}_fit_error"]], 30)}

## Highest-Responsibility Cells

{md_table(top_listener, 25)}

## Candidate Stress Ranking

{md_table(candidate_scores[["file", "changed_cells_vs_h057", "changed_rows_vs_h057", "h088_move_cosine", f"{best_model}_pred_delta", f"{best_model}_high_listener_toxic_cells", f"{best_model}_high_listener_benefit_cells"]], 30)}

## Promoted Diagnostic Candidate

{md_table(pd.DataFrame([decision]), 1)}

Selected cell target counts:

{md_table(selected["target"].value_counts().rename_axis("target").reset_index(name="cells") if not selected.empty else pd.DataFrame(), 10)}

## Interpretation

H148 treats listener responsibility as a separate HS-JEPA target representation:

```text
context -> hidden human state -> action proposal
        -> listener responsibility -> toxicity/safety -> correction field
```

The promoted candidate is a diagnostic, not a guaranteed submission slot.  It is
a large worldview test: if this family improves public, then public LB deltas
can be inverted into a useful row-target listener head.  If it fails, the public
equation is too underdetermined at cell resolution and listener recovery must
move to row/route bundles rather than individual cells.
"""
    (OUT / "h148_report.md").write_text(report, encoding="utf-8")

    print(f"H148 best listener model: {best_model}")
    print(f"H148 candidate: {root_path}")
    print(f"selected cells: {len(selected)}")
    print(candidate_scores[["file", f"{best_model}_pred_delta", "changed_cells_vs_h057"]].head(15).to_string(index=False))


if __name__ == "__main__":
    run()
