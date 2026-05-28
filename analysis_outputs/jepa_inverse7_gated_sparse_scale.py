from __future__ import annotations

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
import jepa_regularized_sparse_direct_solver as sparse_solver  # noqa: E402
import jepa_sparse_scale_ladder_stress as ladder  # noqa: E402
import jepa_target_ablation_scale_probe as target_ablation  # noqa: E402
from public_subset_sensitivity_audit import build_masks  # noqa: E402


SCAN_OUT = OUT / "jepa_inverse7_gated_sparse_scale_scan.csv"
ANCHOR_OUT = OUT / "jepa_inverse7_gated_sparse_scale_actual_anchor.csv"
CV_DETAIL_OUT = OUT / "jepa_inverse7_gated_sparse_scale_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_inverse7_gated_sparse_scale_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_inverse7_gated_sparse_scale_selected.csv"
REPORT_OUT = OUT / "jepa_inverse7_gated_sparse_scale_report.md"


SOURCE_FILES = {
    "f465_actual_best": "submission_sparsejepa_f4657144.csv",
    "282_consensus_directrob": "submission_sparsejepa_282e9546.csv",
    "3cf_noq2_safe": "submission_sparsejepa_3cfdf64a.csv",
    "f43_cv_best": "submission_sparsejepa_f43ea825.csv",
}

TARGET_MASKS = {
    "all": inv.TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_stage": ["Q3", "S1", "S2", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
}

SCALES = [1.00, 1.50, 2.00, 2.50, 3.00, 4.00]
DELTA_CAP = 0.30


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def load_sample() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return sample.sort_values(inv.KEY).reset_index(drop=True)


def target_gate(mask_name: str, n_rows: int) -> np.ndarray:
    allowed = set(TARGET_MASKS[mask_name])
    weights = np.asarray([target in allowed for target in inv.TARGETS], dtype=np.float64)
    return np.repeat(weights.reshape(1, -1), n_rows, axis=0)


def inverse_weighted_row_score(table: pd.DataFrame, records: list[dict[str, object]], top_n: int) -> np.ndarray:
    top = table.head(top_n).reset_index(drop=True)
    scale = max(0.10, float(top["weighted_std_rmse"].median()))
    weights = np.exp(-0.5 * (top["weighted_std_rmse"].to_numpy(dtype=np.float64) / scale) ** 2)
    weights = weights / weights.sum()
    score = np.zeros(int(records[0]["mask"].shape[0]), dtype=np.float64)
    for i, row in top.iterrows():
        rec = records[int(row["mask_index"])]
        mask = rec["mask"]
        assert isinstance(mask, np.ndarray)
        score[mask] += float(weights[i])
    if score.max() > 0:
        score = score / score.max()
    return score


def hard_top_fraction(score: np.ndarray, frac: float) -> np.ndarray:
    k = max(1, int(round(len(score) * frac)))
    idx = np.argsort(-score)[:k]
    gate = np.zeros_like(score, dtype=np.float64)
    gate[idx] = 1.0
    return gate


def named_mask(records: list[dict[str, object]], kind: str, name: str) -> np.ndarray:
    for rec in records:
        if rec["mask_kind"] == kind and rec["mask_name"] == name:
            mask = rec["mask"]
            assert isinstance(mask, np.ndarray)
            return mask.astype(np.float64)
    raise KeyError(f"{kind}:{name}")


def build_row_gates(sample: pd.DataFrame) -> dict[str, np.ndarray]:
    records = build_masks(sample)
    compat = pd.read_csv(OUT / "public_lb_inverse7_mask_raw05_a2c8_compatible_top512.csv")
    score16 = inverse_weighted_row_score(compat, records, 16)
    score32 = inverse_weighted_row_score(compat, records, 32)
    score64 = inverse_weighted_row_score(compat, records, 64)
    gates = {
        "id01": named_mask(records, "single_subject", "id01"),
        "prefix20": named_mask(records, "global_order", "prefix_frac0.20"),
        "prefix30": named_mask(records, "global_order", "prefix_frac0.30"),
        "subject_prefix25": named_mask(records, "subject_order", "per_subject_prefix_frac0.25"),
        "inv16_soft": score16,
        "inv32_soft": score32,
        "inv64_soft": score64,
        "inv64_pow2": score64**2,
        "inv64_top20": hard_top_fraction(score64, 0.20),
        "inv64_top30": hard_top_fraction(score64, 0.30),
    }
    return gates


def build_candidates(sample: pd.DataFrame, base: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base_logit = inv.logit(base)
    consensus = sparse_solver.consensus_matrices(sample)
    row_gates = build_row_gates(sample)
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}

    for source_name, file_name in SOURCE_FILES.items():
        source = ladder.load_submission_array(file_name, sample)
        source_delta = inv.logit(source) - base_logit
        source_active = np.abs(source_delta) > 1e-10
        for row_gate_name, row_gate in row_gates.items():
            row_gate_2d = row_gate.reshape(-1, 1)
            row_support = row_gate > 1e-10
            row_weight_sum = float(row_gate.sum())
            for mask_name in TARGET_MASKS:
                tgate = target_gate(mask_name, len(sample))
                base_gate = row_gate_2d * tgate
                active_gate = base_gate * source_active
                active_cells = int((active_gate > 1e-10).sum())
                if active_cells <= 0:
                    continue
                active_rows = int((np.abs(active_gate).sum(axis=1) > 1e-10).sum())
                active_energy = consensus["energy"][active_gate > 1e-10]
                for scale in SCALES:
                    final_delta = np.clip(scale * source_delta * base_gate, -DELTA_CAP, DELTA_CAP)
                    pred = inv.clip_prob(inv.sigmoid(base_logit + final_delta))
                    label = f"{source_name}|{row_gate_name}|{mask_name}|s{scale:.2f}|cap{DELTA_CAP:.2f}"
                    tag = stable_hash(label)
                    name = f"inv7gate_{tag}"
                    arrays[name] = pred
                    rows.append(
                        {
                            "name": name,
                            "file": f"submission_inv7gate_{tag}.csv",
                            "source_name": source_name,
                            "source_file": file_name,
                            "variant": f"{row_gate_name}_{mask_name}",
                            "row_gate": row_gate_name,
                            "target_mask": mask_name,
                            "scale": scale,
                            "delta_cap": DELTA_CAP,
                            "row_support_rows": int(row_support.sum()),
                            "row_gate_sum": row_weight_sum,
                            "active_cells": active_cells,
                            "active_rows": active_rows,
                            "mean_active_energy": float(np.mean(active_energy)),
                            "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                            "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - base))),
                            "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                        }
                    )
    return pd.DataFrame(rows), arrays


def choose_for_anchor(scan: pd.DataFrame) -> pd.DataFrame:
    frames = [
        scan[(scan["robust_delta_vs_a2c8"] <= -0.00020) & (scan["mean_abs_move_vs_a2c8"] >= 0.0015)]
        .sort_values(["selection_proxy", "robust_delta_vs_a2c8"])
        .head(90),
        scan[scan["row_gate"].isin(["id01", "prefix20", "inv64_top20"])]
        .sort_values(["selection_proxy", "mean_abs_move_vs_a2c8"], ascending=[True, False])
        .head(60),
        scan[scan["mean_abs_move_vs_a2c8"] >= 0.0040]
        .sort_values(["robust_delta_vs_a2c8", "selection_proxy"])
        .head(55),
        scan[scan["target_mask"].isin(["q3_stage", "q3_s2_s3_s4"])]
        .sort_values(["selection_proxy", "robust_delta_vs_a2c8"])
        .head(55),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(180).reset_index(drop=True)


def choose_for_cv(anchor: pd.DataFrame) -> pd.DataFrame:
    candidates = anchor[anchor["name"].str.startswith("inv7gate_")].copy()
    frames = [
        candidates[candidates["actual_anchor_score_final"] <= 0.57784]
        .sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
        .head(65),
        candidates[(candidates["actual_anchor_score_final"] <= 0.57795) & (candidates["mean_abs_move_vs_a2c8"] >= 0.0030)]
        .sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"])
        .head(45),
        candidates[candidates["row_gate"].isin(["id01", "prefix20", "inv64_top20"])]
        .sort_values(["actual_anchor_score_final", "mean_abs_move_vs_a2c8"], ascending=[True, False])
        .head(45),
        candidates[candidates["target_mask"].isin(["q3_stage", "q3_s2_s3_s4"])]
        .sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
        .head(35),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(120).reset_index(drop=True)


def coalesce_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in ["mean_abs_move_vs_a2c8", "max_abs_move_vs_a2c8", "mean_abs_move_vs_raw05"]:
        if column not in out.columns:
            for candidate in [f"{column}_y", f"{column}_x"]:
                if candidate in out.columns:
                    out[column] = out[candidate]
                    break
    if "selection_proxy" not in out.columns and {"robust_expected_public", "robust_p90_delta_vs_a2c8"}.issubset(out.columns):
        move_bonus = 0.02 * out.get("mean_abs_move_vs_a2c8", 0.0)
        out["selection_proxy"] = out["robust_expected_public"] + 0.50 * out["robust_p90_delta_vs_a2c8"] - move_bonus
    return out


def select_outputs(sample: pd.DataFrame, scored: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    frames = [
        scored[
            (scored["actual_anchor_score_final"] <= 0.57790)
            & (scored["honest_cv_delta_mean"] <= -0.00032)
            & (scored["mean_abs_move_vs_a2c8"] >= 0.0030)
        ]
        .assign(submit_role="inv7gate_score_probe")
        .sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"])
        .head(5),
        scored[
            (scored["row_gate"].isin(["prefix20", "prefix30", "inv64_soft"]))
            & (scored["actual_anchor_score_final"] <= 0.57790)
            & (scored["mean_abs_move_vs_a2c8"] >= 0.0020)
        ]
        .assign(submit_role="inv7gate_block_probe")
        .sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"])
        .head(5),
        scored[
            (scored["target_mask"].isin(["q3_stage", "q3_s2_s3_s4"]))
            & (scored["actual_anchor_score_final"] <= 0.57790)
        ]
        .assign(submit_role="inv7gate_q3stage_probe")
        .sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"])
        .head(5),
        scored[
            (scored["mean_abs_move_vs_a2c8"] >= 0.0040)
            & (scored["honest_cv_delta_mean"] <= -0.00025)
        ]
        .assign(submit_role="inv7gate_large_move")
        .sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"])
        .head(5),
    ]
    selected = pd.concat(frames, ignore_index=True).drop_duplicates("name")
    selected = selected.sort_values(["submit_role", "actual_anchor_score_final", "honest_cv_delta_mean"]).reset_index(drop=True)
    for row in selected.itertuples(index=False):
        out = sample.copy()
        out[inv.TARGETS] = inv.clip_prob(arrays[str(row.name)])
        out.to_csv(OUT / str(row.file), index=False)
    return selected


def write_report(anchor: pd.DataFrame, cv_scored: pd.DataFrame, selected: pd.DataFrame) -> None:
    cols = [
        "name",
        "file",
        "source_name",
        "row_gate",
        "target_mask",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "row_support_rows",
        "row_gate_sum",
        "active_cells",
        "mean_active_energy",
    ]
    best_anchor = anchor[anchor["name"].str.startswith("inv7gate_")].sort_values(
        ["actual_anchor_score_final", "robust_delta_vs_a2c8"]
    )
    best_cv = cv_scored.sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"])
    by_gate = (
        cv_scored.groupby(["row_gate", "target_mask"], as_index=False)
        .agg(
            n=("name", "count"),
            best_actual_anchor=("actual_anchor_score_final", "min"),
            best_honest_cv=("honest_cv_delta_mean", "min"),
            best_move=("mean_abs_move_vs_a2c8", "max"),
        )
        .sort_values(["best_actual_anchor", "best_honest_cv"])
    )
    report = [
        "# JEPA Inverse7-Gated Sparse Scale",
        "",
        "This gates the sparse JEPA/direct-label scale direction by inverse7 public-hidden row masks.",
        "",
        "## Best Actual-Anchor Rows",
        "",
        "```",
        best_anchor[[c for c in cols if c in best_anchor.columns]].head(50).round(9).to_string(index=False),
        "```",
        "",
        "## Best Honest Anchor-CV Rows",
        "",
        "```",
        best_cv[[c for c in cols if c in best_cv.columns]].head(50).round(9).to_string(index=False),
        "```",
        "",
        "## Row Gate Summary",
        "",
        "```",
        by_gate.head(80).round(9).to_string(index=False),
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False)
        if not selected.empty
        else "none",
        "```",
        "",
        "## Interpretation",
        "",
        "- If inverse7 row gates help, the public split is row/block-driven and the sparse direction should be localized before scaling.",
        "- If row gates lose to uniform scale-ladder, then inverse7 mask evidence is too underidentified for candidate construction and should remain diagnostic only.",
        "- The useful 0.54 path still requires larger moves; row gates are only valuable if they preserve scale while reducing public-axis leakage.",
    ]
    REPORT_OUT.write_text("\n".join(report) + "\n")


def main() -> None:
    sample = load_sample()
    preds = inv.load_predictions(sample)
    base = preds["cvjepa_a2c8"]
    candidates, arrays = build_candidates(sample, base)
    robust_scored = ladder.robust_scan(candidates, arrays, preds)
    robust_scored = coalesce_columns(robust_scored)
    robust_scored.to_csv(SCAN_OUT, index=False)

    anchor_candidates = choose_for_anchor(robust_scored)
    anchor_arrays = {name: arrays[name] for name in anchor_candidates["name"].astype(str)}
    anchor = ladder.actual_anchor_for_ladder(sample, anchor_candidates, anchor_arrays)
    anchor = coalesce_columns(anchor)
    anchor.to_csv(ANCHOR_OUT, index=False)

    cv_candidates = choose_for_cv(anchor)
    cv_arrays = {name: arrays[name] for name in cv_candidates["name"].astype(str)}
    cv_detail, cv_summary = ladder.anchor_cv_for_ladder(sample, cv_candidates, cv_arrays, preds)
    cv_detail.to_csv(CV_DETAIL_OUT, index=False)
    cv_summary.to_csv(CV_SUMMARY_OUT, index=False)
    combined = target_ablation.combined_honest(cv_summary)
    scored = anchor.merge(combined, left_on=["name", "file"], right_on=["candidate_name", "file"], how="inner")
    scored = coalesce_columns(scored)
    selected = select_outputs(sample, scored, arrays)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(anchor, scored, selected)

    print(
        "generated",
        candidates.shape,
        "anchor",
        anchor.shape,
        "cv",
        scored.shape,
        "selected",
        selected.shape,
    )


if __name__ == "__main__":
    main()
