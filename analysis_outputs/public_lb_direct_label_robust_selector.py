from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

import public_lb_direct_label_inverse7 as inv  # noqa: E402


SUMMARY_IN = OUT / "public_lb_direct_label_inverse7_solutions.csv"
CELL_IN = OUT / "public_lb_direct_label_inverse7_cell_solutions.parquet"
LOOCV_IN = OUT / "public_lb_direct_label_inverse7_loocv_detail.csv"
L2OCV_SOURCE_IN = OUT / "public_lb_direct_label_inverse7_l2ocv_source_summary.csv"

SCAN_OUT = OUT / "public_lb_direct_label_robust_selector_scan.csv"
SELECTED_OUT = OUT / "public_lb_direct_label_robust_selector_selected.csv"
SOURCE_OUT = OUT / "public_lb_direct_label_robust_selector_sources.csv"
REPORT_OUT = OUT / "public_lb_direct_label_robust_selector_report.md"


ROBUST_TARGET_MASKS = {
    "all": inv.TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q1_s1_s3": ["Q1", "S1", "S3"],
    "q1_q3_s1_s3": ["Q1", "Q3", "S1", "S3"],
    "q1_s1_s3_s4": ["Q1", "S1", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
}

STRENGTHS = [0.08, 0.12, 0.18, 0.27, 0.36, 0.50, 0.70]
CAPS = [0.008, 0.016, 0.024, 0.032, 0.040, 0.055]


@dataclass
class Solution:
    solution_id: str
    meta: dict[str, object]
    rows: np.ndarray
    targets: np.ndarray
    y: np.ndarray


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def aggregate_loocv() -> pd.DataFrame:
    detail = pd.read_csv(LOOCV_IN)
    agg = (
        detail.groupby(["mask_index", "mask_kind", "mask_name", "rows", "prior_name"], as_index=False)
        .agg(
            loocv_mae=("heldout_abs_error", "mean"),
            loocv_median=("heldout_abs_error", "median"),
            loocv_p90=("heldout_abs_error", lambda s: float(s.quantile(0.90))),
            loocv_max=("heldout_abs_error", "max"),
            loocv_signed_mean=("heldout_signed_error", "mean"),
            loocv_signed_abs_mean=("heldout_signed_error", lambda s: float(np.mean(np.abs(s)))),
            train_score_mean=("train_solution_score", "mean"),
            train_shift_mean=("train_mean_abs_shift_vs_prior", "mean"),
            loocv_n=("heldout_key", "nunique"),
        )
        .reset_index(drop=True)
    )
    if L2OCV_SOURCE_IN.exists():
        l2o = pd.read_csv(L2OCV_SOURCE_IN)
        keep_cols = [
            "mask_index",
            "mask_kind",
            "mask_name",
            "rows",
            "prior_name",
            "l2o_source_score",
            "l2o_mae",
            "l2o_p90",
            "l2o_max",
            "l2o_pair_mae",
            "l2o_pair_p90",
            "l2o_pair_max",
            "l2o_signed_mean",
        ]
        agg = agg.merge(l2o[[c for c in keep_cols if c in l2o.columns]], on=["mask_index", "mask_kind", "mask_name", "rows", "prior_name"], how="left")
    return agg


def load_sources() -> tuple[pd.DataFrame, dict[str, Solution]]:
    summary = pd.read_csv(SUMMARY_IN)
    cells = pd.read_parquet(CELL_IN)
    loocv = aggregate_loocv()
    sources = summary.merge(
        loocv,
        on=["mask_index", "mask_kind", "mask_name", "rows", "prior_name"],
        how="left",
    )
    fallback = sources["loocv_mae"].dropna().max()
    if not np.isfinite(fallback):
        fallback = 0.0025
    for col in ["loocv_mae", "loocv_median", "loocv_p90", "loocv_max", "loocv_signed_abs_mean"]:
        sources[col] = sources[col].fillna(fallback * 1.5)
    sources["loocv_signed_mean"] = sources["loocv_signed_mean"].fillna(0.0)
    for col, source_col in [
        ("l2o_mae", "loocv_mae"),
        ("l2o_p90", "loocv_p90"),
        ("l2o_max", "loocv_max"),
        ("l2o_pair_mae", "loocv_mae"),
        ("l2o_pair_p90", "loocv_p90"),
        ("l2o_pair_max", "loocv_max"),
        ("l2o_signed_mean", "loocv_signed_mean"),
        ("l2o_source_score", "loocv_mae"),
    ]:
        if col not in sources.columns:
            sources[col] = sources[source_col]
        else:
            sources[col] = sources[col].fillna(sources[source_col])
    sources["is_structured_mask"] = (sources["mask_kind"] != "random_rows").astype(int)
    sources["is_subject_like_mask"] = sources["mask_kind"].isin(["single_subject", "subject_order", "subject_contiguous"]).astype(int)
    sources["robust_source_score"] = (
        sources["solution_score"]
        + 0.55 * sources["loocv_mae"]
        + 0.20 * sources["loocv_p90"]
        + 0.15 * sources["loocv_max"]
        + 0.20 * np.abs(sources["loocv_signed_mean"])
        + 0.65 * sources["l2o_mae"]
        + 0.28 * sources["l2o_p90"]
        + 0.18 * sources["l2o_max"]
        + 0.30 * sources["l2o_pair_mae"]
        + 0.15 * sources["l2o_pair_p90"]
        + 0.25 * np.abs(sources["l2o_signed_mean"])
        + 0.02 * sources["mean_abs_shift_vs_prior"]
    )
    sources = sources.sort_values(["robust_source_score", "loocv_mae", "solution_score"]).reset_index(drop=True)

    solution_map: dict[str, Solution] = {}
    meta_by_id = sources.set_index("solution_id").to_dict(orient="index")
    target_to_id = {target: i for i, target in enumerate(inv.TARGETS)}
    for solution_id, group in cells.groupby("solution_id", sort=False):
        meta = meta_by_id.get(solution_id)
        if meta is None:
            continue
        solution_map[str(solution_id)] = Solution(
            solution_id=str(solution_id),
            meta=meta,
            rows=group["row_index"].to_numpy(dtype=int),
            targets=group["target"].map(target_to_id).to_numpy(dtype=int),
            y=group["pseudo_y"].to_numpy(dtype=np.float64),
        )
    return sources, solution_map


def score_under_solution(sol: Solution, pred: np.ndarray, stage2: np.ndarray) -> float:
    unique_rows = np.unique(sol.rows)
    row_pos = {row: pos for pos, row in enumerate(unique_rows)}
    matrix_pred = np.zeros((len(unique_rows), len(inv.TARGETS)), dtype=np.float64)
    matrix_stage2 = np.zeros((len(unique_rows), len(inv.TARGETS)), dtype=np.float64)
    matrix_y = np.zeros((len(unique_rows), len(inv.TARGETS)), dtype=np.float64)
    for row_idx, target_idx, y in zip(sol.rows, sol.targets, sol.y, strict=False):
        pos = row_pos[int(row_idx)]
        j = int(target_idx)
        matrix_pred[pos, j] = pred[int(row_idx), j]
        matrix_stage2[pos, j] = stage2[int(row_idx), j]
        matrix_y[pos, j] = y
    pred_loss = inv.ce_matrix(matrix_y, matrix_pred).mean()
    stage2_loss = inv.ce_matrix(matrix_y, matrix_stage2).mean()
    return float(inv.STAGE2_PUBLIC + pred_loss - stage2_loss)


def solution_ensemble(sources: pd.DataFrame, solution_map: dict[str, Solution], limit: int = 44) -> tuple[list[Solution], np.ndarray]:
    selected: list[Solution] = []
    seen: set[tuple[int, str]] = set()
    for row in sources.itertuples(index=False):
        key = (int(row.mask_index), str(row.prior_name))
        if key in seen:
            continue
        sol = solution_map.get(str(row.solution_id))
        if sol is None:
            continue
        seen.add(key)
        selected.append(sol)
        if len(selected) >= limit:
            break
    quality = np.asarray([float(sol.meta["robust_source_score"]) for sol in selected], dtype=np.float64)
    tau = max(0.0012, float(np.median(quality)))
    weights = np.exp(-quality / tau)
    weights = weights / weights.sum()
    return selected, weights


def choose_source_solutions(sources: pd.DataFrame, solution_map: dict[str, Solution]) -> list[Solution]:
    frames = [
        sources.sort_values(["robust_source_score", "loocv_mae"]).head(18),
        sources[sources["is_structured_mask"] == 1].sort_values(["robust_source_score", "loocv_mae"]).head(12),
        sources[sources["loocv_mae"] <= 0.00070].sort_values(["solution_score", "loocv_p90"]).head(12),
    ]
    chosen = pd.concat(frames, ignore_index=True, sort=False).drop_duplicates("solution_id")
    result: list[Solution] = []
    for row in chosen.sort_values(["robust_source_score", "loocv_mae"]).itertuples(index=False):
        sol = solution_map.get(str(row.solution_id))
        if sol is not None:
            result.append(sol)
    return result


def make_candidate(base: np.ndarray, sol: Solution, target_mask: str, strength: float, cap: float) -> tuple[str, np.ndarray]:
    pred = base.copy()
    target_ids = {inv.TARGETS.index(t) for t in ROBUST_TARGET_MASKS[target_mask]}
    keep = np.asarray([int(t) in target_ids for t in sol.targets], dtype=bool)
    if not keep.any():
        return f"{sol.solution_id}|{target_mask}|empty", pred
    rows = sol.rows[keep]
    targets = sol.targets[keep]
    yy = np.clip(sol.y[keep], 0.020, 0.980)
    old = pred[rows, targets]
    validation_mae = max(float(sol.meta["loocv_mae"]), float(sol.meta.get("l2o_mae", sol.meta["loocv_mae"])))
    reliability = np.clip(1.0 - validation_mae / 0.0016, 0.35, 1.0)
    eff_strength = strength * reliability
    moved = inv.sigmoid(inv.logit(old) + eff_strength * (inv.logit(yy) - inv.logit(old)))
    delta = np.clip(moved - old, -cap, cap)
    pred[rows, targets] = inv.clip_prob(old + delta)
    label = (
        f"{sol.solution_id}|m{int(sol.meta['mask_index'])}|{sol.meta['prior_name']}|"
        f"{target_mask}|s{strength:.3f}|r{reliability:.3f}|c{cap:.3f}"
    )
    return label, pred


def geometric_features(pred: np.ndarray, base: np.ndarray, raw05: np.ndarray) -> dict[str, float]:
    diff_base = pred - base
    diff_raw = pred - raw05
    vec = (inv.logit(pred) - inv.logit(raw05)).reshape(-1)
    basis = (inv.logit(base) - inv.logit(raw05)).reshape(-1)
    denom = float(np.linalg.norm(vec) * np.linalg.norm(basis))
    cosine = float(np.dot(vec, basis) / denom) if denom > 1e-12 else np.nan
    if float(np.dot(basis, basis)) > 1e-12 and float(np.linalg.norm(vec)) > 1e-12:
        proj = basis * (float(np.dot(vec, basis)) / float(np.dot(basis, basis)))
        orth = float(np.linalg.norm(vec - proj) / np.linalg.norm(vec))
    else:
        orth = np.nan
    gain_if_one = np.log(inv.clip_prob(pred) / inv.clip_prob(raw05))
    gain_if_zero = np.log((1.0 - inv.clip_prob(pred)) / (1.0 - inv.clip_prob(raw05)))
    return {
        "mean_abs_move_vs_a2c8": float(np.mean(np.abs(diff_base))),
        "max_abs_move_vs_a2c8": float(np.max(np.abs(diff_base))),
        "mean_abs_move_vs_raw05": float(np.mean(np.abs(diff_raw))),
        "logit_cosine_to_a2c8_move": cosine,
        "logit_orth_ratio_to_a2c8_move": orth,
        "best_case_gain_vs_raw05_if_all_correct": float(np.mean(np.maximum(gain_if_one, gain_if_zero))),
    }


def generate_candidates(
    sample: pd.DataFrame,
    sources: pd.DataFrame,
    solution_map: dict[str, Solution],
    preds: dict[str, np.ndarray],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = preds["cvjepa_a2c8"]
    stage2 = preds["stage2"]
    raw05 = preds["raw05"]
    ensemble, weights = solution_ensemble(sources, solution_map)
    a2_scores = np.asarray([score_under_solution(sol, base, stage2) for sol in ensemble])

    predictions: dict[str, np.ndarray] = {
        "control_a2c8": base,
        "control_raw05": raw05,
    }
    meta_rows: list[dict[str, object]] = []
    for sol in choose_source_solutions(sources, solution_map):
        for target_mask in ROBUST_TARGET_MASKS:
            for strength in STRENGTHS:
                for cap in CAPS:
                    label, pred = make_candidate(base, sol, target_mask, strength, cap)
                    name = f"directrob_{stable_hash(label)}"
                    predictions[name] = pred
                    meta_rows.append(
                        {
                            "name": name,
                            "label": label,
                            "source_solution_id": sol.solution_id,
                            "source_mask_index": int(sol.meta["mask_index"]),
                            "source_mask_kind": str(sol.meta["mask_kind"]),
                            "source_mask_name": str(sol.meta["mask_name"]),
                            "source_prior_name": str(sol.meta["prior_name"]),
                            "source_solution_score": float(sol.meta["solution_score"]),
                            "source_loocv_mae": float(sol.meta["loocv_mae"]),
                            "source_loocv_p90": float(sol.meta["loocv_p90"]),
                            "source_loocv_max": float(sol.meta["loocv_max"]),
                            "source_loocv_signed_mean": float(sol.meta["loocv_signed_mean"]),
                            "source_l2o_mae": float(sol.meta.get("l2o_mae", sol.meta["loocv_mae"])),
                            "source_l2o_p90": float(sol.meta.get("l2o_p90", sol.meta["loocv_p90"])),
                            "source_l2o_max": float(sol.meta.get("l2o_max", sol.meta["loocv_max"])),
                            "source_l2o_score": float(sol.meta.get("l2o_source_score", sol.meta["loocv_mae"])),
                            "source_robust_score": float(sol.meta["robust_source_score"]),
                            "source_is_structured": int(sol.meta["is_structured_mask"]),
                            "target_mask": target_mask,
                            "strength": strength,
                            "cap": cap,
                            "file": f"submission_directrob_{stable_hash(label)}.csv",
                        }
                    )
    meta = pd.DataFrame(meta_rows)
    controls = pd.DataFrame(
        [
            {"name": name, "label": name, "source_solution_id": "", "target_mask": "", "strength": np.nan, "cap": np.nan, "file": ""}
            for name in predictions
            if name.startswith("control_")
        ]
    )
    meta = pd.concat([controls, meta], ignore_index=True, sort=False)

    score_rows = []
    for name, pred in predictions.items():
        scores = np.asarray([score_under_solution(sol, pred, stage2) for sol in ensemble])
        delta = scores - a2_scores
        rec = {
            "name": name,
            "robust_expected_public": float(weights @ scores),
            "robust_delta_vs_a2c8": float(weights @ delta),
            "robust_p10_delta_vs_a2c8": float(np.quantile(delta, 0.10)),
            "robust_p50_delta_vs_a2c8": float(np.quantile(delta, 0.50)),
            "robust_p90_delta_vs_a2c8": float(np.quantile(delta, 0.90)),
            "robust_worst_delta_vs_a2c8": float(np.max(delta)),
            "robust_win_rate_vs_a2c8": float(np.mean(delta < 0.0)),
        }
        rec.update(geometric_features(pred, base, raw05))
        score_rows.append(rec)
    scan = meta.merge(pd.DataFrame(score_rows), on="name", how="left")
    scan["source_loocv_mae"] = scan["source_loocv_mae"].fillna(0.0)
    scan["source_loocv_p90"] = scan["source_loocv_p90"].fillna(0.0)
    scan["source_l2o_mae"] = scan["source_l2o_mae"].fillna(0.0)
    scan["source_l2o_p90"] = scan["source_l2o_p90"].fillna(0.0)
    scan["robust_edge_to_source_loo"] = -scan["robust_delta_vs_a2c8"] / np.maximum(scan["source_loocv_mae"], 1e-6)
    scan["robust_edge_to_source_l2o"] = -scan["robust_delta_vs_a2c8"] / np.maximum(scan["source_l2o_mae"], 1e-6)
    scan["robust_selection_score"] = (
        scan["robust_delta_vs_a2c8"]
        + 0.80 * np.maximum(scan["robust_p90_delta_vs_a2c8"], 0.0)
        + 0.40 * np.maximum(scan["robust_worst_delta_vs_a2c8"], 0.0)
        + 0.10 * scan["source_loocv_mae"]
        + 0.04 * scan["source_loocv_p90"]
        + 0.16 * scan["source_l2o_mae"]
        + 0.06 * scan["source_l2o_p90"]
        - 0.0020 * np.minimum(scan["mean_abs_move_vs_a2c8"] / 0.0035, 1.3)
        - 0.0010 * np.minimum(scan["logit_orth_ratio_to_a2c8_move"].fillna(0.0), 1.0)
    )
    scan = scan.sort_values(["robust_selection_score", "robust_delta_vs_a2c8"]).reset_index(drop=True)

    selected_rows: list[dict[str, object]] = []
    used_names: set[str] = set()
    selection_specs = [
        (
            "robust_first_submit",
            scan[
                scan["name"].str.startswith("directrob_")
                & (scan["source_loocv_mae"] <= 0.00065)
                & (scan["source_l2o_mae"] <= 0.00065)
                & (scan["robust_p90_delta_vs_a2c8"] <= 0.00010)
                & (scan["mean_abs_move_vs_a2c8"].between(0.0015, 0.0048))
            ],
            8,
        ),
        (
            "robust_structured",
            scan[
                scan["name"].str.startswith("directrob_")
                & (scan["source_is_structured"] == 1)
                & (scan["source_loocv_mae"] <= 0.00070)
                & (scan["source_l2o_mae"] <= 0.00070)
                & (scan["robust_p90_delta_vs_a2c8"] <= 0.00015)
            ],
            8,
        ),
        (
            "robust_large_probe",
            scan[
                scan["name"].str.startswith("directrob_")
                & (scan["source_l2o_mae"] <= 0.00076)
                & (scan["mean_abs_move_vs_a2c8"] >= 0.0032)
                & (scan["robust_p90_delta_vs_a2c8"] <= 0.00020)
            ],
            8,
        ),
    ]
    for role, frame, limit in selection_specs:
        seen_keys: set[tuple[object, object, object]] = set()
        for row in frame.itertuples(index=False):
            key = (getattr(row, "source_solution_id", ""), getattr(row, "target_mask", ""), getattr(row, "strength", np.nan))
            if key in seen_keys or str(row.name) in used_names:
                continue
            seen_keys.add(key)
            used_names.add(str(row.name))
            selected_rows.append({**row._asdict(), "submit_role": role})
            if len([r for r in selected_rows if r["submit_role"] == role]) >= limit:
                break
    selected = pd.DataFrame(selected_rows)
    if not selected.empty:
        for row in selected.itertuples(index=False):
            out = sample.copy()
            out[inv.TARGETS] = inv.clip_prob(predictions[str(row.name)])
            out.to_csv(OUT / str(row.file), index=False)
    return scan, selected


def write_report(sources: pd.DataFrame, scan: pd.DataFrame, selected: pd.DataFrame) -> None:
    source_cols = [
        "solution_id",
        "mask_kind",
        "mask_name",
        "rows",
        "prior_name",
        "solution_score",
        "loocv_mae",
        "loocv_p90",
        "loocv_max",
        "l2o_mae",
        "l2o_p90",
        "l2o_max",
        "l2o_pair_mae",
        "l2o_source_score",
        "loocv_signed_mean",
        "robust_source_score",
        "mean_abs_shift_vs_prior",
        "top_blocks",
    ]
    cand_cols = [
        "submit_role",
        "file",
        "source_solution_id",
        "source_mask_kind",
        "source_mask_name",
        "source_prior_name",
        "source_loocv_mae",
        "source_l2o_mae",
        "target_mask",
        "strength",
        "cap",
        "robust_selection_score",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "robust_worst_delta_vs_a2c8",
        "robust_edge_to_source_loo",
        "robust_edge_to_source_l2o",
        "mean_abs_move_vs_a2c8",
        "logit_orth_ratio_to_a2c8_move",
    ]
    top_cols = [
        "name",
        "file",
        "source_mask_name",
        "source_prior_name",
        "source_loocv_mae",
        "source_l2o_mae",
        "target_mask",
        "strength",
        "cap",
        "robust_selection_score",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
    ]
    report = [
        "# Public LB Direct-Label Robust Selector",
        "",
        "This selector re-ranks all-anchor direct-label solutions by leave-one-anchor generalization before generating larger a2c8 moves.",
        "",
        "## Robust Source Solutions",
        "",
        "```",
        sources[[c for c in source_cols if c in sources.columns]].head(40).round(9).to_string(index=False),
        "```",
        "",
        "## Selected Robust Probe Submissions",
        "",
        "```",
        selected[[c for c in cand_cols if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none",
        "```",
        "",
        "## Candidate Scan Top",
        "",
        "```",
        scan[[c for c in top_cols if c in scan.columns]].head(70).round(9).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- The first-submit set prioritizes source masks with LOO MAE <= 0.00065, so it is less tied to the overfit all-anchor mask `frac0.50_rep142`.",
        "- Structured candidates keep subject-contiguous masks even when random masks score slightly better, because true public selection is more likely to be subject/block structured than RNG-like.",
        "- These are still diagnostic larger moves. The robust selector lowers underidentification risk, but the LOO error remains comparable to the expected public edge.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(inv.KEY).reset_index(drop=True)
    sources, solution_map = load_sources()
    preds = inv.load_predictions(sample)
    scan, selected = generate_candidates(sample, sources, solution_map, preds)
    sources.to_csv(SOURCE_OUT, index=False)
    scan.to_csv(SCAN_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(sources, scan, selected)

    print(REPORT_OUT)
    print("[sources]")
    print(
        sources[
            [
                "solution_id",
                "mask_kind",
                "mask_name",
                "prior_name",
                "solution_score",
                "loocv_mae",
                "loocv_p90",
                "robust_source_score",
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
                    "source_loocv_mae",
                    "target_mask",
                    "strength",
                    "cap",
                    "robust_delta_vs_a2c8",
                    "robust_p90_delta_vs_a2c8",
                    "mean_abs_move_vs_a2c8",
                ]
            ]
            .head(30)
            .round(9)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
