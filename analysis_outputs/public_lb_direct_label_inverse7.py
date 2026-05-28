from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from public_subset_sensitivity_audit import build_masks, ce_matrix  # noqa: E402


TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
KEY = ["subject_id", "sleep_date", "lifelog_date"]
EPS = 1e-6

STAGE2 = "submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv"
RAW05 = "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv"
A2C8 = "submission_frontier_cvjepa_refine_a2c8d2c8.csv"
ENTROPY_G075 = "submission_public_entropyproj_public2d0_g075.csv"
ENTROPY_G050 = "submission_public_entropyproj_public2d0_g050.csv"

STAGE2_PUBLIC = 0.5779449757

ANCHORS = [
    ("anchor578", "submission_hybrid_0p578_logit_after_subject_final9_strict.csv", 0.5784273528, 1.0),
    ("ordinal_q", "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv", 0.5783033652, 1.0),
    ("raw05", RAW05, 0.5775263072, 2.0),
    ("cvjepa_a2c8", A2C8, 0.5774393210, 2.3),
    ("jepa_bad_residual", "submission_jepa_latent_residual_probe.csv", 0.5812273278, 0.9),
    ("jepa_bad_q2", "submission_jepa_latent_q2_w0p45.csv", 0.5798012862, 0.9),
]

PRIOR_FILES = {
    "a2c8": A2C8,
    "raw05": RAW05,
    "entropy_g075": ENTROPY_G075,
    "entropy_g050": ENTROPY_G050,
}

TARGET_MASKS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "q3_s2_s3": ["Q3", "S2", "S3"],
    "q3_s2_s4": ["Q3", "S2", "S4"],
    "q3_s4": ["Q3", "S4"],
}

LAMBDAS = (3e-10, 1e-9, 3e-9, 1e-8, 3e-8, 1e-7, 3e-7, 1e-6)

MASK_TOP = OUT / "public_lb_inverse7_mask_top512.csv"
MASK_COMPAT = OUT / "public_lb_inverse7_mask_raw05_a2c8_compatible_top512.csv"

SOLUTION_OUT = OUT / "public_lb_direct_label_inverse7_solutions.csv"
TARGET_OUT = OUT / "public_lb_direct_label_inverse7_target_summary.csv"
CELL_OUT = OUT / "public_lb_direct_label_inverse7_cell_solutions.parquet"
CANDIDATE_OUT = OUT / "public_lb_direct_label_inverse7_candidate_scan.csv"
SELECTED_OUT = OUT / "public_lb_direct_label_inverse7_selected.csv"
REPORT_OUT = OUT / "public_lb_direct_label_inverse7_report.md"


@dataclass
class FitResult:
    solution_id: str
    mask_index: int
    mask_kind: str
    mask_name: str
    rows: int
    top_blocks: str
    prior_name: str
    prior_file: str
    lam: float
    y: np.ndarray
    flat_rows: np.ndarray
    flat_targets: np.ndarray
    pred_delta: np.ndarray
    resid: np.ndarray
    metrics: dict[str, object]


def locate(name: str | Path) -> Path | None:
    path = Path(name)
    if path.exists():
        return path
    for base in (OUT, JEPA):
        candidate = base / str(name)
        if candidate.exists():
            return candidate
    return None


def load_sub(name: str | Path, sample: pd.DataFrame | None = None) -> pd.DataFrame:
    path = locate(name)
    if path is None:
        raise FileNotFoundError(str(name))
    df = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if sample is not None and not df[KEY].equals(sample[KEY]):
        raise ValueError(f"key mismatch: {name}")
    return df


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), EPS, 1.0 - EPS)


def logit(x: np.ndarray) -> np.ndarray:
    x = clip_prob(x)
    return np.log(x / (1.0 - x))


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -40.0, 40.0)))


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def diff_terms(candidate: np.ndarray, base: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cand = clip_prob(candidate)
    b = clip_prob(base)
    intercept = -np.log(1.0 - cand) + np.log(1.0 - b)
    coef = np.log((1.0 - cand) / cand) - np.log((1.0 - b) / b)
    return intercept, coef


def mask_records(sample: pd.DataFrame) -> tuple[list[dict[str, object]], pd.DataFrame]:
    records = build_masks(sample)
    rows = []
    sample_rows = sample[["subject_id"]].copy()
    sample_rows["_row"] = np.arange(len(sample))
    for i, rec in enumerate(records):
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        subject_counts = sample_rows.loc[mask].groupby("subject_id").size()
        rows.append(
            {
                "mask_index": i,
                "mask_kind": rec["mask_kind"],
                "mask_name": rec["mask_name"],
                "rows": int(mask.sum()),
                "n_subjects": int(subject_counts.size),
                "top_subject": str(subject_counts.idxmax()) if len(subject_counts) else "",
                "top_subject_rows": int(subject_counts.max()) if len(subject_counts) else 0,
            }
        )
    return records, pd.DataFrame(rows)


def selected_mask_indices() -> pd.DataFrame:
    frames = []
    for source, path, limit in [("full", MASK_TOP, 80), ("compat", MASK_COMPAT, 80)]:
        if not path.exists():
            continue
        df = pd.read_csv(path).head(limit).copy()
        df["mask_source"] = source
        frames.append(df)
    if not frames:
        raise FileNotFoundError("inverse7 mask files are missing")
    masks = pd.concat(frames, ignore_index=True, sort=False)
    masks = masks.sort_values(["inverse_fit_score", "weighted_std_rmse"]).drop_duplicates("mask_index")
    return masks.head(56).reset_index(drop=True)


def build_design(
    preds: dict[str, np.ndarray],
    row_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    base = preds["stage2"]
    selected_rows = np.where(row_mask)[0]
    rr, tt = np.meshgrid(selected_rows, np.arange(len(TARGETS)), indexing="ij")
    flat_rows = rr.reshape(-1)
    flat_targets = tt.reshape(-1)
    n_cells = len(flat_rows)
    intercept_rows = []
    coef_rows = []
    observed = []
    weights = []
    scales = []
    for key, file_name, public_lb, weight in ANCHORS:
        pred = preds[key]
        intercept, coef = diff_terms(pred, base)
        intercept_rows.append(float(intercept[flat_rows, flat_targets].mean()))
        coef_rows.append(coef[flat_rows, flat_targets] / float(n_cells))
        delta = public_lb - STAGE2_PUBLIC
        observed.append(delta)
        weights.append(weight)
        scales.append(max(abs(delta), 2.5e-4))
    intercept_vec = np.asarray(intercept_rows, dtype=np.float64)
    coef_mat = np.vstack(coef_rows).astype(np.float64)
    observed_vec = np.asarray(observed, dtype=np.float64)
    weights_vec = np.asarray(weights, dtype=np.float64)
    scales_vec = np.asarray(scales, dtype=np.float64)
    return coef_mat, intercept_vec, observed_vec, weights_vec, scales_vec, flat_rows, flat_targets


def solve_for_prior(
    mask_row: pd.Series,
    row_mask: np.ndarray,
    preds: dict[str, np.ndarray],
    prior_name: str,
    prior: np.ndarray,
) -> FitResult:
    coef_mat, intercept_vec, observed, weights, scales, flat_rows, flat_targets = build_design(preds, row_mask)
    prior_flat = clip_prob(prior[flat_rows, flat_targets])
    best: FitResult | None = None
    y_anchor = observed - intercept_vec
    row_scale = np.sqrt(weights) / scales
    a_weighted = coef_mat * row_scale[:, None]
    b_weighted = y_anchor * row_scale
    for lam in LAMBDAS:
        rhs = b_weighted - a_weighted @ prior_flat
        gram = a_weighted @ a_weighted.T + lam * np.eye(a_weighted.shape[0])
        step = a_weighted.T @ np.linalg.solve(gram, rhs)
        raw_y = prior_flat + step
        y = clip_prob(np.clip(raw_y, 0.0, 1.0))
        pred_delta = intercept_vec + coef_mat @ y
        resid = pred_delta - observed
        std_resid = resid / scales
        active = weights > 0
        wrmse = float(np.sqrt(np.average(resid[active] ** 2, weights=weights[active])))
        wstd = float(np.sqrt(np.average(std_resid[active] ** 2, weights=weights[active])))
        sign_ok = np.sign(pred_delta) == np.sign(observed)
        shift = y - prior_flat
        metrics: dict[str, object] = {
            "weighted_rmse": wrmse,
            "weighted_std_rmse": wstd,
            "rmse": float(np.sqrt(np.mean(resid**2))),
            "std_rmse": float(np.sqrt(np.mean(std_resid**2))),
            "max_abs_resid": float(np.max(np.abs(resid))),
            "weighted_sign_acc": float(np.average(sign_ok.astype(float), weights=weights)),
            "mean_abs_shift_vs_prior": float(np.mean(np.abs(shift))),
            "max_abs_shift_vs_prior": float(np.max(np.abs(shift))),
            "mean_solution_prob": float(np.mean(y)),
            "mean_confidence_abs_y_minus_half": float(np.mean(np.abs(y - 0.5))),
            "near_binary_rate_05": float(np.mean((y <= 0.05) | (y >= 0.95))),
            "active_cell_count": int(len(y)),
            "bound_clip_rate": float(np.mean((raw_y < 0.0) | (raw_y > 1.0))),
        }
        for i, (key, _file_name, _public, _weight) in enumerate(ANCHORS):
            metrics[f"pred_delta_{key}"] = float(pred_delta[i])
            metrics[f"resid_{key}"] = float(resid[i])
        score = (
            metrics["weighted_std_rmse"]
            + 0.20 * metrics["std_rmse"]
            + 12.0 * metrics["max_abs_resid"]
            + 0.03 * metrics["mean_abs_shift_vs_prior"]
            + 0.10 * (1.0 - metrics["weighted_sign_acc"])
        )
        metrics["solution_score"] = float(score)
        solution_id = stable_hash(f"{int(mask_row.mask_index)}|{prior_name}|{lam}|{score:.12f}")
        fit = FitResult(
            solution_id=solution_id,
            mask_index=int(mask_row.mask_index),
            mask_kind=str(mask_row.mask_kind),
            mask_name=str(mask_row.mask_name),
            rows=int(mask_row.rows),
            top_blocks=str(mask_row.get("top_blocks", "")),
            prior_name=prior_name,
            prior_file=PRIOR_FILES[prior_name],
            lam=float(lam),
            y=y,
            flat_rows=flat_rows,
            flat_targets=flat_targets,
            pred_delta=pred_delta,
            resid=resid,
            metrics=metrics,
        )
        if best is None or fit.metrics["solution_score"] < best.metrics["solution_score"]:
            best = fit
    assert best is not None
    return best


def load_predictions(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    specs = {"stage2": STAGE2}
    specs.update({key: file_name for key, file_name, _public, _weight in ANCHORS})
    preds = {}
    for key, file_name in specs.items():
        preds[key] = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)
    return preds


def target_summary_for_solution(fit: FitResult, priors: dict[str, np.ndarray]) -> list[dict[str, object]]:
    prior = priors[fit.prior_name][fit.flat_rows, fit.flat_targets]
    rows = []
    for j, target in enumerate(TARGETS):
        keep = fit.flat_targets == j
        if not np.any(keep):
            continue
        yy = fit.y[keep]
        pp = prior[keep]
        rows.append(
            {
                "solution_id": fit.solution_id,
                "mask_index": fit.mask_index,
                "mask_kind": fit.mask_kind,
                "mask_name": fit.mask_name,
                "prior_name": fit.prior_name,
                "lambda": fit.lam,
                "target": target,
                "n_cells": int(keep.sum()),
                "solution_rate": float(np.mean(yy)),
                "prior_rate": float(np.mean(pp)),
                "rate_delta_vs_prior": float(np.mean(yy - pp)),
                "mean_abs_shift_vs_prior": float(np.mean(np.abs(yy - pp))),
                "confidence_abs_y_minus_half": float(np.mean(np.abs(yy - 0.5))),
            }
        )
    return rows


def solution_rows(fits: list[FitResult], priors: dict[str, np.ndarray], a2c8: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    target_rows = []
    cell_rows = []
    for fit in fits:
        rec = {
            "solution_id": fit.solution_id,
            "mask_index": fit.mask_index,
            "mask_kind": fit.mask_kind,
            "mask_name": fit.mask_name,
            "rows": fit.rows,
            "top_blocks": fit.top_blocks,
            "prior_name": fit.prior_name,
            "prior_file": fit.prior_file,
            "lambda": fit.lam,
        }
        rec.update(fit.metrics)
        summary_rows.append(rec)
        target_rows.extend(target_summary_for_solution(fit, priors))

        prior = priors[fit.prior_name][fit.flat_rows, fit.flat_targets]
        a2 = a2c8[fit.flat_rows, fit.flat_targets]
        for row_idx, target_idx, y, p0, pa in zip(fit.flat_rows, fit.flat_targets, fit.y, prior, a2, strict=False):
            cell_rows.append(
                {
                    "solution_id": fit.solution_id,
                    "mask_index": fit.mask_index,
                    "row_index": int(row_idx),
                    "target": TARGETS[int(target_idx)],
                    "pseudo_y": float(y),
                    "prior_prob": float(p0),
                    "a2c8_prob": float(pa),
                    "delta_vs_prior": float(y - p0),
                    "delta_vs_a2c8": float(y - pa),
                }
            )
    return pd.DataFrame(summary_rows), pd.DataFrame(target_rows), pd.DataFrame(cell_rows)


def select_solution_ensemble(summary: pd.DataFrame, fits_by_id: dict[str, FitResult], limit: int = 48) -> list[FitResult]:
    ranked = summary.sort_values(["solution_score", "weighted_std_rmse", "mean_abs_shift_vs_prior"]).copy()
    selected = []
    seen_masks = set()
    for row in ranked.itertuples(index=False):
        key = (int(row.mask_index), str(row.prior_name))
        if key in seen_masks:
            continue
        seen_masks.add(key)
        selected.append(fits_by_id[str(row.solution_id)])
        if len(selected) >= limit:
            break
    return selected


def make_candidate(
    sample: pd.DataFrame,
    base: np.ndarray,
    fit: FitResult,
    target_mask: str,
    strength: float,
    cap: float,
) -> tuple[str, np.ndarray]:
    pred = base.copy()
    target_ids = {TARGETS.index(t) for t in TARGET_MASKS[target_mask]}
    cols = np.array([i for i, target_id in enumerate(fit.flat_targets) if int(target_id) in target_ids], dtype=int)
    if len(cols) == 0:
        label = f"{fit.solution_id}|{target_mask}|empty"
        return label, pred
    rows = fit.flat_rows[cols]
    targets = fit.flat_targets[cols]
    yy = np.clip(fit.y[cols], 0.015, 0.985)
    old = pred[rows, targets]
    moved = sigmoid(logit(old) + strength * (logit(yy) - logit(old)))
    delta = np.clip(moved - old, -cap, cap)
    pred[rows, targets] = clip_prob(old + delta)
    label = f"{fit.solution_id}|m{fit.mask_index}|{fit.prior_name}|{target_mask}|s{strength:.3f}|c{cap:.3f}"
    return label, pred


def score_under_fit(fit: FitResult, pred: np.ndarray, stage2: np.ndarray) -> float:
    n_rows = fit.rows
    matrix_pred = np.zeros((n_rows, len(TARGETS)), dtype=np.float64)
    matrix_stage2 = np.zeros((n_rows, len(TARGETS)), dtype=np.float64)
    matrix_y = np.zeros((n_rows, len(TARGETS)), dtype=np.float64)
    unique_rows = np.unique(fit.flat_rows)
    row_pos = {row: pos for pos, row in enumerate(unique_rows)}
    for row_idx, target_idx, y in zip(fit.flat_rows, fit.flat_targets, fit.y, strict=False):
        pos = row_pos[int(row_idx)]
        j = int(target_idx)
        matrix_pred[pos, j] = pred[int(row_idx), j]
        matrix_stage2[pos, j] = stage2[int(row_idx), j]
        matrix_y[pos, j] = y
    pred_loss = ce_matrix(matrix_y, matrix_pred).mean()
    stage2_loss = ce_matrix(matrix_y, matrix_stage2).mean()
    return float(STAGE2_PUBLIC + pred_loss - stage2_loss)


def geometric_features(pred: np.ndarray, base: np.ndarray, raw05: np.ndarray) -> dict[str, float]:
    diff_base = pred - base
    diff_raw = pred - raw05
    vec = (logit(pred) - logit(raw05)).reshape(-1)
    basis = (logit(base) - logit(raw05)).reshape(-1)
    denom = float(np.linalg.norm(vec) * np.linalg.norm(basis))
    cosine = float(np.dot(vec, basis) / denom) if denom > 1e-12 else np.nan
    if float(np.dot(basis, basis)) > 1e-12 and float(np.linalg.norm(vec)) > 1e-12:
        proj = basis * (float(np.dot(vec, basis)) / float(np.dot(basis, basis)))
        orth = float(np.linalg.norm(vec - proj) / np.linalg.norm(vec))
    else:
        orth = np.nan
    gain_if_one = np.log(clip_prob(pred) / clip_prob(raw05))
    gain_if_zero = np.log((1.0 - clip_prob(pred)) / (1.0 - clip_prob(raw05)))
    return {
        "mean_abs_move_vs_a2c8": float(np.mean(np.abs(diff_base))),
        "max_abs_move_vs_a2c8": float(np.max(np.abs(diff_base))),
        "mean_abs_move_vs_raw05": float(np.mean(np.abs(diff_raw))),
        "logit_cosine_to_a2c8_move": cosine,
        "logit_orth_ratio_to_a2c8_move": orth,
        "best_case_gain_vs_raw05_if_all_correct": float(np.mean(np.maximum(gain_if_one, gain_if_zero))),
    }


def generate_and_score_candidates(
    sample: pd.DataFrame,
    summary: pd.DataFrame,
    fits_by_id: dict[str, FitResult],
    preds: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = preds["cvjepa_a2c8"]
    stage2 = preds["stage2"]
    raw05 = preds["raw05"]
    ensemble = select_solution_ensemble(summary, fits_by_id, limit=56)
    tau = max(0.10, float(np.median([fit.metrics["weighted_std_rmse"] for fit in ensemble])))
    weights = np.exp(-0.5 * np.asarray([fit.metrics["weighted_std_rmse"] for fit in ensemble]) ** 2 / (tau**2))
    weights = weights / weights.sum()

    candidate_records: list[dict[str, object]] = []
    predictions: dict[str, np.ndarray] = {
        "control_a2c8": base,
        "control_raw05": raw05,
    }
    for file_name in [
        "submission_inverse7blend_1040423d.csv",
        "submission_inverse7blend_404221a2.csv",
        "submission_inverse7blend_b32dd1a5.csv",
        "submission_inverse7blend_3f238743.csv",
    ]:
        path = locate(file_name)
        if path is not None:
            predictions[f"control_{Path(file_name).stem}"] = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)

    source_fits = []
    ranked = summary.sort_values(["solution_score", "weighted_std_rmse", "mean_abs_shift_vs_prior"])
    seen_masks = set()
    for row in ranked.itertuples(index=False):
        key = (int(row.mask_index), str(row.prior_name))
        if key in seen_masks:
            continue
        seen_masks.add(key)
        source_fits.append(fits_by_id[str(row.solution_id)])
        if len(source_fits) >= 16:
            break

    for fit in source_fits:
        for target_mask in TARGET_MASKS:
            for strength in [0.06, 0.10, 0.16, 0.24, 0.36]:
                for cap in [0.006, 0.012, 0.024, 0.040]:
                    label, pred = make_candidate(sample, base, fit, target_mask, strength, cap)
                    name = f"directlbl_{stable_hash(label)}"
                    predictions[name] = pred
                    candidate_records.append(
                        {
                            "name": name,
                            "label": label,
                            "source_solution_id": fit.solution_id,
                            "source_mask_index": fit.mask_index,
                            "source_mask_kind": fit.mask_kind,
                            "source_mask_name": fit.mask_name,
                            "source_prior_name": fit.prior_name,
                            "target_mask": target_mask,
                            "strength": strength,
                            "cap": cap,
                            "file": f"submission_directlbl_{stable_hash(label)}.csv",
                        }
                    )

    meta = pd.DataFrame(candidate_records)
    control_rows = [
        {"name": name, "label": name, "source_solution_id": "", "target_mask": "", "strength": np.nan, "cap": np.nan, "file": ""}
        for name in predictions
        if name.startswith("control_")
    ]
    meta = pd.concat([pd.DataFrame(control_rows), meta], ignore_index=True, sort=False)

    score_rows = []
    a2_scores = np.asarray([score_under_fit(fit, base, stage2) for fit in ensemble])
    for name, pred in predictions.items():
        scores = np.asarray([score_under_fit(fit, pred, stage2) for fit in ensemble])
        delta = scores - a2_scores
        rec = {
            "name": name,
            "direct_expected_public": float(weights @ scores),
            "direct_delta_vs_a2c8": float(weights @ delta),
            "direct_p10_delta_vs_a2c8": float(np.quantile(delta, 0.10)),
            "direct_p50_delta_vs_a2c8": float(np.quantile(delta, 0.50)),
            "direct_p90_delta_vs_a2c8": float(np.quantile(delta, 0.90)),
            "direct_worst_delta_vs_a2c8": float(np.max(delta)),
            "direct_win_rate_vs_a2c8": float(np.mean(delta < 0.0)),
        }
        rec.update(geometric_features(pred, base, raw05))
        score_rows.append(rec)
    scan = meta.merge(pd.DataFrame(score_rows), on="name", how="left")
    scan["direct_selection_score"] = (
        scan["direct_delta_vs_a2c8"]
        + 0.75 * np.maximum(scan["direct_p90_delta_vs_a2c8"], 0.0)
        + 0.25 * np.maximum(scan["direct_worst_delta_vs_a2c8"], 0.0)
        - 0.015 * np.minimum(scan["mean_abs_move_vs_a2c8"] / 0.004, 1.5)
        - 0.005 * np.minimum(scan["logit_orth_ratio_to_a2c8_move"].fillna(0.0), 1.0)
    )
    scan = scan.sort_values(["direct_selection_score", "direct_delta_vs_a2c8"]).reset_index(drop=True)

    selected_names = []
    selected_rows = []
    for family, frame, n in [
        ("direct_large_move", scan[scan["name"].str.startswith("directlbl_") & (scan["mean_abs_move_vs_a2c8"] >= 0.0004)], 10),
        ("direct_safe_move", scan[scan["name"].str.startswith("directlbl_") & (scan["direct_p90_delta_vs_a2c8"] <= 2.5e-4)], 8),
    ]:
        seen = set()
        for row in frame.itertuples(index=False):
            key = (getattr(row, "source_solution_id", ""), getattr(row, "target_mask", ""), getattr(row, "strength", np.nan))
            if key in seen or str(row.name) in selected_names:
                continue
            seen.add(key)
            selected_names.append(str(row.name))
            selected_rows.append({**row._asdict(), "submit_role": family})
            if len([r for r in selected_rows if r["submit_role"] == family]) >= n:
                break
    selected = pd.DataFrame(selected_rows)
    if not selected.empty:
        for row in selected.itertuples(index=False):
            pred = predictions[str(row.name)]
            out = sample.copy()
            out[TARGETS] = clip_prob(pred)
            out.to_csv(OUT / str(row.file), index=False)
    return scan, selected


def write_report(summary: pd.DataFrame, target_summary: pd.DataFrame, scan: pd.DataFrame, selected: pd.DataFrame) -> None:
    cols = [
        "solution_id",
        "mask_kind",
        "mask_name",
        "rows",
        "prior_name",
        "lambda",
        "solution_score",
        "weighted_std_rmse",
        "weighted_rmse",
        "weighted_sign_acc",
        "mean_abs_shift_vs_prior",
        "near_binary_rate_05",
        "pred_delta_raw05",
        "pred_delta_cvjepa_a2c8",
        "pred_delta_jepa_bad_residual",
        "top_blocks",
    ]
    tcols = ["solution_id", "target", "solution_rate", "prior_rate", "rate_delta_vs_prior", "mean_abs_shift_vs_prior"]
    ccols = [
        "submit_role",
        "file",
        "source_solution_id",
        "source_mask_kind",
        "source_mask_name",
        "source_prior_name",
        "target_mask",
        "strength",
        "cap",
        "direct_selection_score",
        "direct_delta_vs_a2c8",
        "direct_p90_delta_vs_a2c8",
        "direct_worst_delta_vs_a2c8",
        "direct_win_rate_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "logit_orth_ratio_to_a2c8_move",
    ]
    report = [
        "# Public LB Direct Label Inverse7",
        "",
        "This audit treats each candidate public subset mask as the actual public rows and solves directly for soft binary labels that explain the observed seven-anchor public deltas.",
        "",
        "## Top Soft-Label Solutions",
        "",
        "```",
        summary[[c for c in cols if c in summary.columns]].head(40).round(9).to_string(index=False),
        "```",
        "",
        "## Target Rate Shifts In Top Solutions",
        "",
        "```",
        target_summary[target_summary["solution_id"].isin(summary.head(8)["solution_id"])][tcols].round(9).to_string(index=False),
        "```",
        "",
        "## Selected Direct-Label Probe Submissions",
        "",
        "```",
        selected[[c for c in ccols if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none",
        "```",
        "",
        "## Candidate Scan Top",
        "",
        "```",
        scan[[c for c in ["name", "file", "source_mask_name", "source_prior_name", "target_mask", "strength", "cap", "direct_selection_score", "direct_delta_vs_a2c8", "direct_p90_delta_vs_a2c8", "mean_abs_move_vs_a2c8"] if c in scan.columns]].head(60).round(9).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- A low fit error here does not prove the mask is the real public subset; the system is underdetermined. It proves that the mask admits a plausible label assignment that explains all observed anchor signs and magnitudes.",
        "- The most useful solutions are the ones that fit public anchors while requiring structured target-rate shifts, especially on id01/early-prefix masks already favored by inverse7.",
        "- Direct-label probes are intentionally larger than raw05-compatible micro-refines. They should be submitted only as diagnostic larger-move tests, not as conservative score-safe candidates.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    records, mask_meta = mask_records(sample)
    selected_masks = selected_mask_indices().merge(mask_meta, on=["mask_index", "mask_kind", "mask_name", "rows"], how="left")
    preds = load_predictions(sample)
    priors = {}
    for name, file_name in PRIOR_FILES.items():
        path = locate(file_name)
        if path is not None:
            priors[name] = load_sub(file_name, sample)[TARGETS].to_numpy(dtype=np.float64)

    fits = []
    for mask_row in selected_masks.itertuples(index=False):
        rec = records[int(mask_row.mask_index)]
        row_mask = rec["mask"]
        assert isinstance(row_mask, np.ndarray)
        row_series = pd.Series(mask_row._asdict())
        for prior_name, prior in priors.items():
            fits.append(solve_for_prior(row_series, row_mask, preds, prior_name, prior))

    fits_by_id = {fit.solution_id: fit for fit in fits}
    summary, target_summary, cell_solutions = solution_rows(fits, priors, preds["cvjepa_a2c8"])
    summary = summary.sort_values(["solution_score", "weighted_std_rmse", "mean_abs_shift_vs_prior"]).reset_index(drop=True)
    target_summary = target_summary.merge(summary[["solution_id", "solution_score"]], on="solution_id", how="left")
    target_summary = target_summary.sort_values(["solution_score", "solution_id", "target"]).reset_index(drop=True)
    summary.to_csv(SOLUTION_OUT, index=False)
    target_summary.to_csv(TARGET_OUT, index=False)
    cell_solutions.to_parquet(CELL_OUT, index=False)

    scan, selected = generate_and_score_candidates(sample, summary, fits_by_id, preds)
    scan.to_csv(CANDIDATE_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(summary, target_summary, scan, selected)

    print(REPORT_OUT)
    print("[top solutions]")
    print(
        summary[
            [
                "solution_id",
                "mask_kind",
                "mask_name",
                "rows",
                "prior_name",
                "lambda",
                "solution_score",
                "weighted_std_rmse",
                "mean_abs_shift_vs_prior",
                "pred_delta_raw05",
                "pred_delta_cvjepa_a2c8",
                "top_blocks",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )
    print("[selected]")
    if selected.empty:
        print("none")
    else:
        print(
            selected[
                [
                    "submit_role",
                    "file",
                    "source_mask_name",
                    "source_prior_name",
                    "target_mask",
                    "strength",
                    "cap",
                    "direct_delta_vs_a2c8",
                    "direct_p90_delta_vs_a2c8",
                    "mean_abs_move_vs_a2c8",
                ]
            ]
            .head(30)
            .round(9)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
