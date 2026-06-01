#!/usr/bin/env python3
"""H008: translate the strong H007 S4 mobility latent into E247 S4 geometry.

H007 showed the HS-JEPA mobility latent is real for S4 under subject/dateblock
stress, but sparse direct edits stayed below public-free selector resolution.
H008 changes the translator:

    train S4 latent classifier -> compare with E247 S4 -> gated logit blend

This tests whether the bottleneck is the latent itself or the row-edit
translator.  No public LB is used.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
HITL = ROOT / "hitl"
H008 = HITL / "h008_s4_latent_column_translator"
H008.mkdir(parents=True, exist_ok=True)

for path in [OUT, HITL]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import h007_s4_mobility_latent_model as h007  # noqa: E402
from e288_lifestyle_bundle_jepa_audit import KEYS, TARGETS, base_label_matrix, clip_prob, md_table  # noqa: E402
from e272_public_free_candidate_audit import CURRENT, build_features, evaluate_models, score_candidates  # noqa: E402
from e328_ownlatent_lifestyle_state_experiment import safe_id, sigmoid  # noqa: E402
from public_anchor_bottleneck_decomposition import load_sub as load_anchor_sub, logit  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


EPS = 1.0e-12
TARGET = "S4"
TIDX = TARGETS.index(TARGET)
E247 = OUT / CURRENT
H003_TINY = HITL / "h003_hs_jepa_prototype" / "submission_h003_semantic_tiny_11e7aa3b.csv"

MODEL_OUT = H008 / "h008_s4_model_test_predictions.csv"
CANDIDATE_OUT = H008 / "h008_candidates.csv"
SCORE_OUT = H008 / "h008_selector_scores.csv"
ANATOMY_OUT = H008 / "h008_candidate_anatomy.csv"
GATE_OUT = H008 / "h008_gate_scores.csv"
SELECTION_OUT = H008 / "h008_selection.csv"
REPORT_OUT = H008 / "h008_report.md"


def rel(path: Path | None) -> str:
    if path is None:
        return "none"
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def short_hash(frame: pd.DataFrame) -> str:
    arr = np.asarray(frame[TARGETS], dtype=np.float64)
    return hashlib.sha1(np.round(arr, 12).tobytes()).hexdigest()[:8]


def normalize_sample_keys(sample: pd.DataFrame) -> pd.DataFrame:
    out = sample[KEYS].copy()
    for col in ["sleep_date", "lifelog_date"]:
        out[col] = pd.to_datetime(out[col])
    return out.reset_index(drop=True)


def write_candidate(base_sub: pd.DataFrame, logits: np.ndarray, candidate_id: str) -> Path:
    out = base_sub[KEYS].copy()
    out[TARGETS] = clip_prob(sigmoid(logits))
    path = H008 / f"submission_h008_{safe_id(candidate_id, 90)}_{short_hash(out)}.csv"
    out.to_csv(path, index=False)
    return path


def build_s4_latent_predictions() -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    base, latent, _, _ = h007.build_latent_features()
    train_mask = base["split"].eq("train").to_numpy()
    train = base.loc[train_mask].reset_index(drop=True)
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    test_idx = base.loc[~train_mask].sort_values(KEYS).index.to_numpy(dtype=int)
    y = train[TARGET].to_numpy(dtype=int)

    chosen = {"feature_set": "mobility_jepa", "C": 0.05}
    cols = h007.FEATURE_SETS[chosen["feature_set"]]
    base_x_train = base_label_matrix(train).reset_index(drop=True)
    base_x_test = base_label_matrix(test).reset_index(drop=True)
    add_train = latent.loc[train_mask, cols].astype(float).reset_index(drop=True)
    add_test = latent.loc[test_idx, cols].astype(float).reset_index(drop=True)
    plus_train = pd.concat([base_x_train, add_train], axis=1)
    plus_test = pd.concat([base_x_test, add_test], axis=1)
    p_plus = h007.full_predict_binary(plus_train, y, plus_test, float(chosen["C"]))
    p_base = h007.full_predict_binary(base_x_train, y, base_x_test, float(chosen["C"]))

    test_state = latent.loc[
        test_idx,
        KEYS
        + [
            "h005_mobility_teacher_z",
            "h005_mobility_teacher_rank",
            "jepa_mobility_pred_z",
            "jepa_mobility_residual_z",
            "jepa_mobility_energy",
            "jepa_mobility_low_energy",
            "jepa_mobility_agreement",
        ],
    ].reset_index(drop=True)
    pred_frame = test_state.copy()
    pred_frame["s4_latent_prob"] = p_plus
    pred_frame["s4_calendar_prob"] = p_base
    pred_frame["latent_minus_calendar_logit"] = logit(p_plus) - logit(p_base)
    pred_frame.to_csv(MODEL_OUT, index=False)
    return base, p_plus, pred_frame


def candidate_specs() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for w in [0.015, 0.025, 0.040, 0.065, 0.090]:
        specs.append({"candidate_id": f"full_logit_blend_w{str(w).replace('.', 'p')}", "mode": "full_blend", "weight": w, "cap": 0.080})
    for k, w, cap in [(40, 0.06, 0.020), (60, 0.06, 0.020), (80, 0.05, 0.018), (120, 0.04, 0.015)]:
        specs.append({"candidate_id": f"pos_consensus_top{k}_w{str(w).replace('.', 'p')}_cap{str(cap).replace('.', 'p')}", "mode": "pos_consensus", "top_k": k, "weight": w, "cap": cap})
    for k, w, cap in [(60, 0.07, 0.020), (90, 0.06, 0.018), (120, 0.05, 0.016)]:
        specs.append({"candidate_id": f"lowenergy_signed_top{k}_w{str(w).replace('.', 'p')}_cap{str(cap).replace('.', 'p')}", "mode": "lowenergy_signed", "top_k": k, "weight": w, "cap": cap})
    for k, w, cap in [(40, 0.08, 0.022), (60, 0.07, 0.020)]:
        specs.append({"candidate_id": f"two_tail_top{k}_w{str(w).replace('.', 'p')}_cap{str(cap).replace('.', 'p')}", "mode": "two_tail", "top_k": k, "weight": w, "cap": cap})
    for k, w, cap in [(30, 0.075, 0.020), (40, 0.070, 0.020), (40, 0.078, 0.020), (50, 0.070, 0.020), (60, 0.060, 0.018)]:
        specs.append({"candidate_id": f"two_tail_refine_top{k}_w{str(w).replace('.', 'p')}_cap{str(cap).replace('.', 'p')}", "mode": "two_tail", "top_k": k, "weight": w, "cap": cap})
    for k, w, cap in [(40, 0.060, 0.018), (60, 0.055, 0.018), (80, 0.045, 0.015)]:
        specs.append({"candidate_id": f"delta_two_tail_top{k}_w{str(w).replace('.', 'p')}_cap{str(cap).replace('.', 'p')}", "mode": "delta_two_tail", "top_k": k, "weight": w, "cap": cap})
    specs.append({"candidate_id": "down_control_highmob_top60_w0p06_cap0p02", "mode": "down_control", "top_k": 60, "weight": 0.06, "cap": 0.020})
    return specs


def select_top(score: np.ndarray, k: int) -> np.ndarray:
    k = int(min(max(k, 1), len(score)))
    selected = np.zeros(len(score), dtype=bool)
    selected[np.argsort(score)[-k:]] = True
    return selected


def materialize_candidates(base: pd.DataFrame, p_plus: np.ndarray, pred_frame: pd.DataFrame) -> tuple[pd.DataFrame, list[Path]]:
    train_mask = base["split"].eq("train").to_numpy()
    test = base.loc[~train_mask].sort_values(KEYS).reset_index(drop=True)
    sample = normalize_sample_keys(test[KEYS])
    base_sub = load_anchor_sub(E247, sample)
    base_prob = base_sub[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    z_plus = logit(p_plus)
    z_e247 = base_logit[:, TIDX]
    raw_delta = z_plus - z_e247

    mobility_rank = pred_frame["h005_mobility_teacher_rank"].to_numpy(dtype=np.float64)
    low_energy = h007.rank01(pred_frame["jepa_mobility_low_energy"].to_numpy(dtype=np.float64))
    agreement = h007.rank01(pred_frame["jepa_mobility_agreement"].to_numpy(dtype=np.float64))
    pos_score = 0.50 * mobility_rank + 0.30 * h007.rank01(np.maximum(raw_delta, 0.0)) + 0.20 * low_energy
    signed_score = 0.45 * low_energy + 0.35 * agreement + 0.20 * h007.rank01(np.abs(raw_delta))

    rows: list[dict[str, Any]] = []
    paths: list[Path] = []
    for spec in candidate_specs():
        move = np.zeros(len(test), dtype=np.float64)
        mode = str(spec["mode"])
        weight = float(spec["weight"])
        cap = float(spec["cap"])
        if mode == "full_blend":
            move = np.clip(weight * raw_delta, -cap, cap)
            selected = np.abs(move) > EPS
        elif mode == "pos_consensus":
            selected = select_top(pos_score, int(spec["top_k"]))
            move[selected] = np.clip(weight * np.maximum(raw_delta[selected], 0.0), 0.0, cap)
            selected = np.abs(move) > EPS
        elif mode == "lowenergy_signed":
            selected = select_top(signed_score, int(spec["top_k"]))
            move[selected] = np.clip(weight * raw_delta[selected], -cap, cap)
            selected = np.abs(move) > EPS
        elif mode == "two_tail":
            half = max(1, int(spec["top_k"]) // 2)
            high = select_top(pos_score, half)
            low = select_top(-pos_score, half)
            move[high] = np.clip(weight * np.maximum(raw_delta[high], 0.0), 0.0, cap)
            move[low] = np.clip(weight * np.minimum(raw_delta[low], 0.0), -cap, 0.0)
            selected = np.abs(move) > EPS
        elif mode == "delta_two_tail":
            half = max(1, int(spec["top_k"]) // 2)
            high_score = h007.rank01(raw_delta) + 0.30 * low_energy + 0.20 * agreement
            low_score = h007.rank01(-raw_delta) + 0.30 * low_energy + 0.20 * agreement
            high = select_top(high_score, half)
            low = select_top(low_score, half)
            move[high] = np.clip(weight * np.maximum(raw_delta[high], 0.0), 0.0, cap)
            move[low] = np.clip(weight * np.minimum(raw_delta[low], 0.0), -cap, 0.0)
            selected = np.abs(move) > EPS
        elif mode == "down_control":
            selected = select_top(pos_score, int(spec["top_k"]))
            move[selected] = -np.clip(weight * np.maximum(raw_delta[selected], 0.0), 0.0, cap)
            selected = np.abs(move) > EPS
        else:
            raise ValueError(mode)

        logits = base_logit.copy()
        logits[:, TIDX] += move
        path = write_candidate(base_sub, logits, str(spec["candidate_id"]))
        paths.append(path)
        rows.append(
            {
                "candidate_id": spec["candidate_id"],
                "mode": mode,
                "file": rel(path),
                "basename": path.name,
                "weight": weight,
                "cap": cap,
                "top_k": int(spec.get("top_k", len(test))),
                "changed_rows": int((np.abs(move) > EPS).sum()),
                "changed_cells": int((np.abs(move) > EPS).sum()),
                "mean_abs_logit_move": float(np.mean(np.abs(move))),
                "l1_logit_move": float(np.sum(np.abs(move))),
                "max_abs_logit_move": float(np.max(np.abs(move))),
                "max_abs_prob_delta": float(np.max(np.abs(sigmoid(logits)[:, TIDX] - base_prob[:, TIDX]))),
                "move_mean": float(np.mean(move)),
                "selected_raw_delta_mean": float(np.mean(raw_delta[np.abs(move) > EPS])) if int((np.abs(move) > EPS).sum()) else np.nan,
                "selected_mobility_rank_mean": float(np.mean(mobility_rank[np.abs(move) > EPS])) if int((np.abs(move) > EPS).sum()) else np.nan,
                "selected_low_energy_mean": float(np.mean(low_energy[np.abs(move) > EPS])) if int((np.abs(move) > EPS).sum()) else np.nan,
            }
        )
    candidates = pd.DataFrame(rows)
    candidates.to_csv(CANDIDATE_OUT, index=False)
    return candidates, paths


def score_new_candidates(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    model_df = evaluate_models(known)
    files = [CURRENT] + [str(path.resolve()) for path in paths]
    candidates = build_features(files, sample, refs, ref_vecs)
    scores = score_candidates(known, candidates, model_df)
    scores.to_csv(SCORE_OUT, index=False)
    return scores


def candidate_anatomy(paths: list[Path]) -> pd.DataFrame:
    sample = load_anchor_sub(E247)[KEYS]
    base = load_anchor_sub(E247, sample)
    base_prob = base[TARGETS].to_numpy(dtype=np.float64)
    base_logit = logit(base_prob)
    h003_move = None
    if H003_TINY.exists():
        h003 = load_anchor_sub(H003_TINY, sample)
        h003_move = logit(h003[TARGETS].to_numpy(dtype=np.float64)) - base_logit
    rows: list[dict[str, Any]] = []
    for path in paths:
        cand = load_anchor_sub(path, sample)
        prob = cand[TARGETS].to_numpy(dtype=np.float64)
        move = logit(prob) - base_logit
        rec: dict[str, Any] = {
            "file": rel(path),
            "basename": path.name,
            "changed_rows_vs_current": int((np.abs(move).max(axis=1) > EPS).sum()),
            "changed_cells_vs_current": int((np.abs(move) > EPS).sum()),
            "mean_abs_logit_delta_vs_current": float(np.mean(np.abs(move))),
            "l1_logit_delta_vs_current": float(np.sum(np.abs(move))),
            "max_abs_logit_delta_vs_current": float(np.max(np.abs(move))),
            "max_abs_prob_delta_vs_current": float(np.max(np.abs(prob - base_prob))),
        }
        for ti, target in enumerate(TARGETS):
            rec[f"changed_{target}"] = int((np.abs(move[:, ti]) > EPS).sum())
        if h003_move is not None:
            denom = float(np.linalg.norm(move) * np.linalg.norm(h003_move) + EPS)
            rec["cos_delta_with_h003_tiny"] = float(np.sum(move * h003_move) / denom)
            rec["l1_ratio_to_h003_tiny"] = float(np.sum(np.abs(move)) / (np.sum(np.abs(h003_move)) + EPS))
        rows.append(rec)
    anatomy = pd.DataFrame(rows).sort_values(["l1_logit_delta_vs_current", "basename"]).reset_index(drop=True)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return anatomy


def build_gate_scores(candidates: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame) -> pd.DataFrame:
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "strict_promote_gate",
        "info_sensor_gate",
        "below_resolution_gate",
        "block_gate",
        "bad_axis_abs_load",
        "mean_abs_move_vs_a2c8",
        "mean_abs_move_vs_raw05",
    ]
    merged = candidates.merge(scores[[col for col in score_cols if col in scores.columns]], on="basename", how="left")
    anatomy_cols = [
        "basename",
        "changed_rows_vs_current",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    merged = merged.merge(anatomy[[col for col in anatomy_cols if col in anatomy.columns]], on="basename", how="left")
    ratio = merged.get("l1_ratio_to_h003_tiny", pd.Series(0.0, index=merged.index)).fillna(0.0)
    merged["shape_soft_gate"] = (
        (merged["changed_cells"] <= 140)
        & (merged["max_abs_prob_delta"] <= 0.0050)
        & (ratio <= 0.16)
        & (merged["incremental_bad_axis_vs_current"].abs() <= 0.020)
    )
    merged["h008_strict_upload_gate"] = merged["shape_soft_gate"] & merged["strict_promote_gate"].fillna(False).astype(bool)
    merged["h008_aggressive_gate"] = (
        merged["shape_soft_gate"]
        & (merged["pred_delta_vs_current_mean"] < -0.00001)
        & (merged["pred_beats_current_rate"] >= 0.80)
        & (merged["pred_delta_vs_current_p90"] <= 0.000012)
    )
    merged["h008_info_gate"] = merged["shape_soft_gate"] & (
        merged["h008_aggressive_gate"]
        | merged["info_sensor_gate"].fillna(False).astype(bool)
        | ((merged["pred_delta_vs_current_mean"] < 0.0) & (merged["pred_beats_current_rate"] >= 0.60))
    )
    merged["h008_decision"] = np.select(
        [
            merged["h008_strict_upload_gate"],
            merged["h008_aggressive_gate"],
            merged["h008_info_gate"] & ~merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["h008_info_gate"] & merged["below_resolution_gate"].fillna(False).astype(bool),
            merged["shape_soft_gate"],
        ],
        [
            "uploadsafe_candidate",
            "hitl_aggressive_candidate",
            "diagnostic_public_sensor_only",
            "too_small_to_submit",
            "shape_ok_but_selector_rejects",
        ],
        default="reject_shape_or_bad_axis",
    )
    gate = merged.sort_values(
        ["h008_strict_upload_gate", "h008_aggressive_gate", "h008_info_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"],
        ascending=[False, False, False, True, True],
    ).reset_index(drop=True)
    gate.to_csv(GATE_OUT, index=False)
    return gate


def write_uploadsafe_files(gate_scores: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rec in gate_scores[gate_scores["h008_strict_upload_gate"].astype(bool)].to_dict("records"):
        src = ROOT / str(rec["file"])
        if not src.exists():
            src = H008 / str(rec["basename"])
        dst = H008 / src.name.replace(".csv", "_uploadsafe.csv")
        shutil.copyfile(src, dst)
        rows.append({"candidate_id": rec["candidate_id"], "basename": dst.name, "file": rel(dst), "reason": "passed strict H008 gate"})
    selection = pd.DataFrame(rows)
    selection.to_csv(SELECTION_OUT, index=False)
    return selection


def write_report(
    pred_frame: pd.DataFrame,
    candidates: pd.DataFrame,
    scores: pd.DataFrame,
    anatomy: pd.DataFrame,
    gate: pd.DataFrame,
    selection: pd.DataFrame,
) -> None:
    pred_summary = pd.DataFrame(
        [
            {
                "n_test": len(pred_frame),
                "s4_latent_prob_mean": float(pred_frame["s4_latent_prob"].mean()),
                "s4_calendar_prob_mean": float(pred_frame["s4_calendar_prob"].mean()),
                "latent_minus_calendar_logit_mean": float(pred_frame["latent_minus_calendar_logit"].mean()),
                "latent_minus_calendar_logit_std": float(pred_frame["latent_minus_calendar_logit"].std(ddof=0)),
            }
        ]
    )
    gate_cols = [
        "candidate_id",
        "h008_decision",
        "mode",
        "changed_cells",
        "max_abs_prob_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "shape_soft_gate",
        "h008_strict_upload_gate",
        "h008_aggressive_gate",
        "basename",
    ]
    score_cols = [
        "basename",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    cand_cols = [
        "candidate_id",
        "mode",
        "changed_cells",
        "l1_logit_move",
        "max_abs_prob_delta",
        "selected_raw_delta_mean",
        "selected_mobility_rank_mean",
        "selected_low_energy_mean",
        "basename",
    ]
    anatomy_cols = [
        "basename",
        "changed_cells_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
        "cos_delta_with_h003_tiny",
        "l1_ratio_to_h003_tiny",
    ]
    lines = [
        "# H008 S4 Latent Column Translator",
        "",
        "## Question",
        "",
        "Can the strong H007 S4 mobility latent beat the tiny-edit bottleneck by blending the S4 column toward a supervised latent model?",
        "",
        "## S4 Model Prediction Summary",
        "",
        md_table(pred_summary, n=5, floatfmt=".9f"),
        "",
        "## Candidate Gate",
        "",
        md_table(gate[[col for col in gate_cols if col in gate.columns]], n=40, floatfmt=".9f"),
        "",
        "## Candidate Geometry",
        "",
        md_table(candidates[[col for col in cand_cols if col in candidates.columns]], n=40, floatfmt=".9f"),
        "",
        "## Selector Scores",
        "",
        md_table(scores[[col for col in score_cols if col in scores.columns]], n=40, floatfmt=".9f"),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[[col for col in anatomy_cols if col in anatomy.columns]], n=40, floatfmt=".9f"),
        "",
        "## Selection",
        "",
        md_table(selection, n=20, floatfmt=".9f"),
        "",
        "## Interpretation",
        "",
    ]
    strict_n = int(gate["h008_strict_upload_gate"].sum())
    aggressive_n = int(gate["h008_aggressive_gate"].sum())
    if strict_n:
        best = gate[gate["h008_strict_upload_gate"].astype(bool)].iloc[0]
        lines.append(f"`{strict_n}` strict upload candidate(s). Best: `{best['basename']}`.")
    elif aggressive_n:
        best = gate[gate["h008_aggressive_gate"].astype(bool)].iloc[0]
        lines.append(
            f"No strict candidate, but `{aggressive_n}` HITL-aggressive candidate(s) survived the soft shape gate. Best: `{best['basename']}`."
        )
    else:
        best = gate.iloc[0]
        lines.append(f"No strict/aggressive candidate. Best diagnostic row: `{best['basename']}`.")
    lines.extend(
        [
            "",
            "## Files",
            "",
            f"- `{rel(MODEL_OUT)}`",
            f"- `{rel(CANDIDATE_OUT)}`",
            f"- `{rel(SCORE_OUT)}`",
            f"- `{rel(ANATOMY_OUT)}`",
            f"- `{rel(GATE_OUT)}`",
            f"- `{rel(SELECTION_OUT)}`",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    base, p_plus, pred_frame = build_s4_latent_predictions()
    candidates, paths = materialize_candidates(base, p_plus, pred_frame)
    scores = score_new_candidates(paths)
    anatomy = candidate_anatomy(paths)
    gate = build_gate_scores(candidates, scores, anatomy)
    selection = write_uploadsafe_files(gate)
    write_report(pred_frame, candidates, scores, anatomy, gate, selection)
    print(f"report={rel(REPORT_OUT)}")
    print("[h008 gate]")
    cols = [
        "candidate_id",
        "h008_decision",
        "changed_cells",
        "max_abs_prob_delta",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
        "basename",
    ]
    print(gate[cols].round(9).to_string(index=False))
    if not selection.empty:
        print("[uploadsafe]")
        print(selection.to_string(index=False))


if __name__ == "__main__":
    main()
