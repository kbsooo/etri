#!/usr/bin/env python3
"""Big Bet 1: Public-Listener Tomography HS-JEPA.

World model:
    Public LB deltas are not only scores. They are projections of a hidden
    public/private listener over row-target bundles. The task is to reconstruct
    that listener from prior submissions, then translate candidate action fields
    through the listener instead of trusting raw cell-level moves.

This script is intentionally separate from the cohort/autobiographical bet. It
uses current public-sensor artifacts (H149/H150 modules) as a measurement
backbone, but emits a clean final candidate and audit tables under
`hsjepa_big_bets/outputs`.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import shutil
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hsjepa_big_bets" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

H150_PATH = ROOT / "hitl" / "h150_bundle_listener_stress_hsjepa.py"
BEST_BASE = "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv"
H150_FILE = "submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv"
TARGET_LIMITS = {"Q1": 70, "Q2": 85, "Q3": 70, "S1": 85, "S2": 85, "S3": 90, "S4": 85}


def import_h150():
    spec = importlib.util.spec_from_file_location("h150_bigbet1", H150_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {H150_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def short_hash(prob: np.ndarray) -> str:
    return hashlib.sha1(np.round(np.asarray(prob, dtype=np.float64), 12).tobytes()).hexdigest()[:8]


def robust_summary(metrics: dict[str, object], model_names: list[str]) -> dict[str, object]:
    preds = np.asarray([float(metrics[f"{name}_pred_delta"]) for name in model_names], dtype=np.float64)
    return {
        "robust_min_pred_delta": float(preds.min()),
        "robust_max_pred_delta": float(preds.max()),
        "robust_mean_pred_delta": float(preds.mean()),
        "robust_positive_variant_count": int((preds < 0).sum()),
    }


def build_listener_world(h150):
    base_path = h150.locate(BEST_BASE)
    if base_path is None:
        raise FileNotFoundError(BEST_BASE)

    sample = h150.load_sub(base_path)
    base_prob = sample[h150.TARGETS].to_numpy(dtype=np.float64)
    obs = h150.h148mod.collect_public_observations(sample)
    moves = {
        row["file"]: h150.movement_from_file(Path(row["resolved_path"]), sample, base_prob)
        for row in obs.to_dict("records")
    }
    features = h150.h149mod.build_bundle_features(sample, base_prob)

    source_files = sorted(set(h150.h148mod.CANDIDATE_FILES + h150.CORE_SOURCE_FILES + [h150.H149_FILE, H150_FILE]))
    for file_name in source_files:
        path = h150.locate(file_name)
        if path is None:
            continue
        try:
            h150.load_sub(path, sample)
        except Exception:
            continue
        moves[file_name] = h150.movement_from_file(path, sample, base_prob)

    models = {spec.name: h150.fit_variant(obs, moves, features, spec) for spec in h150.variant_specs()}
    return sample, base_prob, obs, moves, models


def collect_tomography_cells(h150, sample, base_prob, moves, models) -> pd.DataFrame:
    base_flat = base_prob.reshape(-1)
    base_logit = h150.logit(base_flat)
    h088 = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    gradients = {name: h150.gradient(model, len(base_flat)) for name, model in models.items()}
    source_files = h150.CORE_SOURCE_FILES + [h150.H149_FILE, H150_FILE]
    source_bonus = {
        h150.H149_FILE: 0.35,
        H150_FILE: 0.45,
        "submission_h075_antibad_transport_f6863945_uploadsafe.csv": 0.10,
        "submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv": 0.08,
        "submission_h074_antishortcut_inversion_816703df_uploadsafe.csv": 0.06,
        "submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv": 0.04,
        "submission_h126_coeffeq_3fe3eee4_uploadsafe.csv": 0.12,
    }

    rows: list[dict[str, object]] = []
    for source_file in source_files:
        path = h150.locate(source_file)
        if path is None:
            continue
        source_prob = h150.load_sub(path, sample)[h150.TARGETS].to_numpy(dtype=np.float64).reshape(-1)
        move = h150.logit(source_prob) - base_logit
        changed = np.abs(move) > h150.TOL
        benefits = {name: -grad * move for name, grad in gradients.items()}
        benefit_matrix = np.vstack([benefits[name] for name in models])
        pos_frac = (benefit_matrix > 0).mean(axis=0)
        mean_benefit = benefit_matrix.mean(axis=0)
        min_benefit = benefit_matrix.min(axis=0)
        h088_same = (move * h088) > 0

        for flat_idx in np.flatnonzero(changed):
            row_idx = int(flat_idx // len(h150.TARGETS))
            target_idx = int(flat_idx % len(h150.TARGETS))
            rows.append(
                {
                    "source_file": source_file,
                    "flat_idx": int(flat_idx),
                    "row": row_idx,
                    "subject_id": sample.loc[row_idx, "subject_id"],
                    "sleep_date": sample.loc[row_idx, "sleep_date"],
                    "lifelog_date": sample.loc[row_idx, "lifelog_date"],
                    "target_index": target_idx,
                    "target": h150.TARGETS[target_idx],
                    "h057_prob": float(base_flat[flat_idx]),
                    "source_prob": float(source_prob[flat_idx]),
                    "source_move": float(move[flat_idx]),
                    "pos_frac": float(pos_frac[flat_idx]),
                    "mean_benefit": float(mean_benefit[flat_idx]),
                    "min_benefit": float(min_benefit[flat_idx]),
                    "all_full_benefit": float(benefits["all_full"][flat_idx]),
                    "no_pre_h_benefit": float(benefits["no_pre_h"][flat_idx]),
                    "frontier_only_benefit": float(benefits["frontier_only"][flat_idx]),
                    "human_social_only_benefit": float(benefits["human_social_only"][flat_idx]),
                    "h088_same_direction": bool(h088_same[flat_idx]),
                    "h088_abs": float(abs(h088[flat_idx])),
                    "source_bonus": float(source_bonus.get(source_file, 0.0)),
                }
            )

    if not rows:
        raise RuntimeError("no source action cells found")

    cells = pd.DataFrame(rows)
    cells["h088_rank"] = cells["h088_abs"].rank(method="average", pct=True)
    cells["abs_move_rank"] = cells["source_move"].abs().rank(method="average", pct=True)
    cells["mean_rank"] = cells["mean_benefit"].rank(method="average", pct=True)
    cells["min_rank"] = cells["min_benefit"].rank(method="average", pct=True)
    cells["score"] = (
        1.20 * cells["mean_rank"]
        + 0.90 * cells["pos_frac"]
        + 0.45 * cells["min_rank"]
        + 0.25 * cells["abs_move_rank"]
        + cells["source_bonus"]
        - 0.85 * cells["h088_same_direction"].astype(float) * cells["h088_rank"]
        - 0.80 * (cells["frontier_only_benefit"] < 0).astype(float)
        - 0.55 * (cells["no_pre_h_benefit"] < 0).astype(float)
    )
    return (
        cells.sort_values(["flat_idx", "score", "mean_benefit"], ascending=[True, False, False])
        .drop_duplicates("flat_idx", keep="first")
        .sort_values("score", ascending=False)
        .reset_index(drop=True)
    )


def materialize_variant(h150, sample, base_prob, cells: pd.DataFrame, name: str, quantile: float, topn: int, amp: float) -> tuple[pd.DataFrame, np.ndarray]:
    pool = cells[
        (cells["pos_frac"] >= 0.70)
        & (cells["mean_benefit"] > 0)
        & (cells["frontier_only_benefit"] > -1.0e-6)
        & (cells["score"] >= cells["score"].quantile(quantile))
        & ~(cells["h088_same_direction"] & (cells["h088_rank"] > 0.90))
    ].copy()

    selected_rows: list[dict[str, object]] = []
    per_target: dict[str, int] = {}
    per_row: dict[int, int] = {}
    per_subject: dict[str, int] = {}
    for rec in pool.sort_values("score", ascending=False).to_dict("records"):
        if len(selected_rows) >= topn:
            break
        row = int(rec["row"])
        target = str(rec["target"])
        subject = str(sample.loc[row, "subject_id"])
        if per_target.get(target, 0) >= TARGET_LIMITS[target]:
            continue
        if per_row.get(row, 0) >= 5:
            continue
        if per_subject.get(subject, 0) >= 110:
            continue
        selected_rows.append(rec)
        per_target[target] = per_target.get(target, 0) + 1
        per_row[row] = per_row.get(row, 0) + 1
        per_subject[subject] = per_subject.get(subject, 0) + 1

    selected = pd.DataFrame(selected_rows)
    new_flat = base_prob.reshape(-1).copy()
    base_flat = base_prob.reshape(-1)
    if not selected.empty:
        for rec in selected.to_dict("records"):
            idx = int(rec["flat_idx"])
            local_amp = amp * (0.72 if bool(rec["h088_same_direction"]) else 1.0)
            if str(rec["source_file"]) == H150_FILE:
                local_amp *= 0.90
            new_flat[idx] = h150.sigmoid(h150.logit(base_flat[idx]) + local_amp * float(rec["source_move"]))
        selected["variant"] = name
        selected["amp"] = amp
        selected["new_prob"] = new_flat[selected["flat_idx"].to_numpy(dtype=int)]
    return selected, new_flat.reshape(base_prob.shape)


def write_submission(h150, sample, prob: np.ndarray, stem: str) -> tuple[Path, Path]:
    hash_id = short_hash(prob)
    local_path = OUT / f"{stem}_{hash_id}.csv"
    root_path = ROOT / f"{stem}_{hash_id}_uploadsafe.csv"
    h150.write_submission(sample, prob, local_path)
    shutil.copyfile(local_path, root_path)
    return local_path, root_path


def main() -> None:
    h150 = import_h150()
    sample, base_prob, obs, moves, models = build_listener_world(h150)
    cells = collect_tomography_cells(h150, sample, base_prob, moves, models)
    cells.to_csv(OUT / "bigbet1_public_listener_tomography_cell_scores.csv", index=False)

    model_names = list(models)
    variants = [
        ("tomography_consensus", 0.48, 420, 0.62),
        ("tomography_antitoxic", 0.55, 340, 0.72),
        ("tomography_human_social", 0.45, 390, 0.68),
    ]
    rows = []
    selected_by_variant = []
    probs_by_variant = {}
    h088_move = moves["submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv"]
    for name, quantile, topn, amp in variants:
        selected, prob = materialize_variant(h150, sample, base_prob, cells, name, quantile, topn, amp)
        probs_by_variant[name] = prob
        move = (h150.logit(prob) - h150.logit(base_prob)).reshape(-1)
        metrics = h150.candidate_metric_row(name, move, models, h088_move)
        metrics.update(robust_summary(metrics, model_names))
        metrics["selected_cells"] = int(len(selected))
        metrics["selected_rows"] = int(selected["row"].nunique()) if not selected.empty else 0
        metrics["target_mix"] = selected["target"].value_counts().to_dict() if not selected.empty else {}
        metrics["source_mix"] = selected["source_file"].value_counts().to_dict() if not selected.empty else {}
        metrics["quantile"] = quantile
        metrics["amp"] = amp
        rows.append(metrics)
        selected_by_variant.append(selected)

    result = pd.DataFrame(rows).sort_values(["frontier_only_pred_delta", "robust_mean_pred_delta"]).reset_index(drop=True)
    result.to_csv(OUT / "bigbet1_public_listener_tomography_results.csv", index=False)
    pd.concat(selected_by_variant, ignore_index=True).to_csv(OUT / "bigbet1_public_listener_tomography_selected_cells.csv", index=False)

    promoted = "tomography_antitoxic"
    local_path, root_path = write_submission(h150, sample, probs_by_variant[promoted], "submission_bigbet1_public_listener_tomography")
    validation = h150.validate_submission(root_path, sample, base_prob)
    decision = {
        "promoted_variant": promoted,
        "local_submission": str(local_path.resolve()),
        "root_submission": str(root_path.resolve()),
        "world_model": "public LB response is a bundle-level listener equation over row-target human-state routes",
        "kill_criterion": "if public worsens, H149/H150 bundle listener is overfitting known public sensors or H088 toxicity is still under-modeled",
        **validation,
    }
    pd.DataFrame([decision]).to_csv(OUT / "bigbet1_public_listener_tomography_decision.csv", index=False)
    print(pd.DataFrame([decision]).to_string(index=False))
    print(result[["file", "selected_cells", "selected_rows", "h088_move_cosine", "frontier_only_pred_delta", "robust_mean_pred_delta", "robust_positive_variant_count"]].to_string(index=False))


if __name__ == "__main__":
    main()
