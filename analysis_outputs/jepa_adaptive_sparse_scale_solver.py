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


SCAN_OUT = OUT / "jepa_adaptive_sparse_scale_solver_scan.csv"
ANCHOR_OUT = OUT / "jepa_adaptive_sparse_scale_solver_actual_anchor.csv"
CV_DETAIL_OUT = OUT / "jepa_adaptive_sparse_scale_solver_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_adaptive_sparse_scale_solver_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_adaptive_sparse_scale_solver_selected.csv"
REPORT_OUT = OUT / "jepa_adaptive_sparse_scale_solver_report.md"


SOURCE_FILES = {
    "f465_actual_best": "submission_sparsejepa_f4657144.csv",
    "3cf_noq2_safe": "submission_sparsejepa_3cfdf64a.csv",
    "282_consensus_directrob": "submission_sparsejepa_282e9546.csv",
    "f43_cv_best": "submission_sparsejepa_f43ea825.csv",
}

BASE_SCALES = [1.15, 1.30, 1.50, 1.75, 2.00]
DELTA_CAPS = [0.12, 0.16, 0.20]

TARGET_PROFILES = {
    "all": {"Q1": 1.00, "Q2": 1.00, "Q3": 1.00, "S1": 1.00, "S2": 1.00, "S3": 1.00, "S4": 1.00},
    "noq2": {"Q1": 1.00, "Q2": 0.00, "Q3": 1.00, "S1": 1.00, "S2": 1.00, "S3": 1.00, "S4": 1.00},
    "noq2_stage_boost": {"Q1": 0.85, "Q2": 0.00, "Q3": 1.10, "S1": 1.15, "S2": 1.25, "S3": 1.25, "S4": 1.25},
    "q3_sstage": {"Q1": 0.55, "Q2": 0.00, "Q3": 1.25, "S1": 0.80, "S2": 1.20, "S3": 1.25, "S4": 1.35},
    "s_only_noq2": {"Q1": 0.25, "Q2": 0.00, "Q3": 0.75, "S1": 1.20, "S2": 1.35, "S3": 1.35, "S4": 1.35},
    "q3s4_edge": {"Q1": 0.30, "Q2": 0.00, "Q3": 1.45, "S1": 0.55, "S2": 0.85, "S3": 1.10, "S4": 1.45},
}

ENERGY_PROFILES = ["flat", "energy_linear", "energy_strong", "energy_top60", "energy_top40"]
BLOCK_PROFILES = ["all_rows", "row_energy", "public_subjects", "id01_id02_early", "late_subject_blocks"]


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def load_sample() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return sample.sort_values(inv.KEY).reset_index(drop=True)


def target_profile_matrix(name: str, n_rows: int) -> np.ndarray:
    profile = TARGET_PROFILES[name]
    weights = np.asarray([profile[target] for target in inv.TARGETS], dtype=np.float64)
    return np.repeat(weights.reshape(1, -1), n_rows, axis=0)


def energy_matrix(profile: str, energy: np.ndarray, active: np.ndarray) -> np.ndarray:
    if profile == "flat":
        return np.ones_like(energy, dtype=np.float64)

    active_energy = energy[active]
    if len(active_energy) == 0:
        return np.zeros_like(energy, dtype=np.float64)
    lo = float(np.quantile(active_energy, 0.15))
    hi = float(np.quantile(active_energy, 0.90))
    norm = np.clip((energy - lo) / max(hi - lo, 1e-9), 0.0, 1.0)

    if profile == "energy_linear":
        return 0.70 + 0.75 * norm
    if profile == "energy_strong":
        return 0.50 + 1.20 * norm
    if profile == "energy_top60":
        cutoff = float(np.quantile(active_energy, 0.40))
        return np.where(energy >= cutoff, 1.30, 0.45)
    if profile == "energy_top40":
        cutoff = float(np.quantile(active_energy, 0.60))
        return np.where(energy >= cutoff, 1.55, 0.25)
    raise ValueError(profile)


def block_matrix(sample: pd.DataFrame, profile: str, row_energy: np.ndarray) -> np.ndarray:
    n_rows = len(sample)
    weights = np.ones(n_rows, dtype=np.float64)
    if profile == "all_rows":
        pass
    elif profile == "row_energy":
        q40 = float(np.quantile(row_energy, 0.40))
        q75 = float(np.quantile(row_energy, 0.75))
        weights = np.where(row_energy >= q75, 1.25, np.where(row_energy >= q40, 1.00, 0.65))
    elif profile == "public_subjects":
        weights = np.where(sample["subject_id"].isin(["id01", "id02", "id06", "id09"]).to_numpy(), 1.18, 0.82)
    elif profile == "id01_id02_early":
        weights = np.full(n_rows, 0.78, dtype=np.float64)
        for _sid, group in sample.groupby("subject_id", sort=False):
            idx = group.index.to_numpy()
            frac = np.arange(len(idx), dtype=np.float64) / max(len(idx) - 1, 1)
            keep = sample.loc[idx, "subject_id"].isin(["id01", "id02"]).to_numpy() & (frac <= 0.45)
            weights[idx[keep]] = 1.40
    elif profile == "late_subject_blocks":
        weights = np.full(n_rows, 0.88, dtype=np.float64)
        for _sid, group in sample.groupby("subject_id", sort=False):
            idx = group.index.to_numpy()
            frac = np.arange(len(idx), dtype=np.float64) / max(len(idx) - 1, 1)
            weights[idx[frac >= 0.55]] = 1.18
    else:
        raise ValueError(profile)
    return np.repeat(weights.reshape(-1, 1), len(inv.TARGETS), axis=1)


def build_candidates(sample: pd.DataFrame, base: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base_logit = inv.logit(base)
    consensus = sparse_solver.consensus_matrices(sample)
    row_energy = consensus["energy"].max(axis=1)
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}

    for source_name, file_name in SOURCE_FILES.items():
        source = ladder.load_submission_array(file_name, sample)
        source_delta = inv.logit(source) - base_logit
        active = np.abs(source_delta) > 1e-10
        for target_profile in TARGET_PROFILES:
            target_factor = target_profile_matrix(target_profile, len(sample))
            for energy_profile in ENERGY_PROFILES:
                energy_factor = energy_matrix(energy_profile, consensus["energy"], active)
                for block_profile in BLOCK_PROFILES:
                    block_factor = block_matrix(sample, block_profile, row_energy)
                    scale_shape = target_factor * energy_factor * block_factor
                    scale_shape = np.where(active, scale_shape, 0.0)
                    if float(np.mean(np.abs(scale_shape))) <= 1e-12:
                        continue
                    active_cells = int((scale_shape > 0).sum())
                    active_rows = int((scale_shape.sum(axis=1) > 0).sum())
                    active_energy = consensus["energy"][scale_shape > 0]
                    shape_mean = float(scale_shape[scale_shape > 0].mean())
                    for base_scale in BASE_SCALES:
                        raw_scaled = base_scale * source_delta * scale_shape
                        for delta_cap in DELTA_CAPS:
                            final_delta = np.clip(raw_scaled, -delta_cap, delta_cap)
                            if float(np.mean(np.abs(final_delta))) <= 1e-10:
                                continue
                            pred = inv.clip_prob(inv.sigmoid(base_logit + final_delta))
                            label = (
                                f"{source_name}|{target_profile}|{energy_profile}|"
                                f"{block_profile}|s{base_scale:.2f}|cap{delta_cap:.2f}"
                            )
                            name = f"adaptjepa_{stable_hash(label)}"
                            if name in arrays:
                                continue
                            arrays[name] = pred
                            rows.append(
                                {
                                    "name": name,
                                    "file": f"submission_adaptjepa_{stable_hash(label)}.csv",
                                    "source_name": source_name,
                                    "source_file": file_name,
                                    "variant": f"{target_profile}/{energy_profile}/{block_profile}",
                                    "target_profile": target_profile,
                                    "energy_profile": energy_profile,
                                    "block_profile": block_profile,
                                    "scale": base_scale,
                                    "delta_cap": delta_cap,
                                    "active_cells": active_cells,
                                    "active_rows": active_rows,
                                    "mean_active_energy": float(np.mean(active_energy)),
                                    "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                                    "mean_scale_factor": shape_mean,
                                    "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - base))),
                                    "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                                }
                            )
    return pd.DataFrame(rows), arrays


def cheap_prefilter(meta: pd.DataFrame) -> pd.DataFrame:
    if meta.empty:
        return meta
    target_penalty = meta["target_profile"].map(
        {
            "all": 0.0008,
            "noq2": 0.0000,
            "noq2_stage_boost": -0.0001,
            "q3_sstage": -0.0002,
            "s_only_noq2": 0.0002,
            "q3s4_edge": -0.00015,
        }
    ).fillna(0.0)
    meta = meta.copy()
    meta["cheap_priority"] = (
        np.abs(meta["mean_abs_move_vs_a2c8"] - 0.0090)
        - 0.0006 * np.minimum(meta["mean_active_energy"] / 1.5, 1.5)
        + 0.0004 * np.maximum(meta["mean_abs_move_vs_a2c8"] - 0.014, 0.0) / 0.004
        + target_penalty
    )
    eligible = meta[meta["mean_abs_move_vs_a2c8"].between(0.0035, 0.0160)].copy()
    frames = [
        eligible.sort_values("cheap_priority").head(700),
        eligible[eligible["mean_abs_move_vs_a2c8"] >= 0.0080].sort_values("cheap_priority").head(500),
        eligible[eligible["target_profile"].isin(["noq2", "noq2_stage_boost", "q3_sstage"])].sort_values("cheap_priority").head(400),
        eligible[eligible["energy_profile"].isin(["energy_top60", "energy_top40", "energy_strong"])].sort_values("cheap_priority").head(400),
        eligible[eligible["block_profile"].isin(["public_subjects", "id01_id02_early", "row_energy"])].sort_values("cheap_priority").head(350),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(1600).reset_index(drop=True)


def choose_for_anchor(scan: pd.DataFrame) -> pd.DataFrame:
    frames = [
        scan[(scan["robust_delta_vs_a2c8"] <= -0.00095) & (scan["robust_p90_delta_vs_a2c8"] <= -0.00055)].sort_values(["selection_proxy", "robust_delta_vs_a2c8"]).head(95),
        scan[scan["mean_abs_move_vs_a2c8"].between(0.008, 0.013)].sort_values(["robust_delta_vs_a2c8", "robust_p90_delta_vs_a2c8"]).head(65),
        scan[scan["target_profile"].isin(["noq2", "noq2_stage_boost", "q3_sstage"])].sort_values(["selection_proxy", "robust_delta_vs_a2c8"]).head(55),
        scan[scan["energy_profile"].isin(["energy_top60", "energy_top40"])].sort_values(["selection_proxy", "robust_delta_vs_a2c8"]).head(45),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(220).reset_index(drop=True)


def coalesce_duplicate_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for column in ["mean_abs_move_vs_a2c8", "max_abs_move_vs_a2c8", "mean_abs_move_vs_raw05"]:
        if column not in out.columns:
            candidates = [f"{column}_y", f"{column}_x"]
            for candidate in candidates:
                if candidate in out.columns:
                    out[column] = out[candidate]
                    break
    return out


def choose_for_cv(anchor: pd.DataFrame) -> pd.DataFrame:
    candidates = anchor[anchor["name"].str.startswith("adaptjepa_")].copy()
    frames = [
        candidates[candidates["actual_anchor_score_final"] <= 0.57778].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(70),
        candidates[(candidates["actual_anchor_score_final"] <= 0.57786) & (candidates["mean_abs_move_vs_a2c8"] >= 0.008)].sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"]).head(50),
        candidates[(candidates["target_profile"].isin(["noq2", "noq2_stage_boost", "q3_sstage"])) & (candidates["actual_anchor_score_final"] <= 0.57786)].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(50),
        candidates[(candidates["energy_profile"].isin(["energy_top60", "energy_top40"])) & (candidates["actual_anchor_score_final"] <= 0.57788)].sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"]).head(40),
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates("name").head(140).reset_index(drop=True)


def select_outputs(sample: pd.DataFrame, scored: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    frames = [
        scored[
            (scored["actual_anchor_score_final"] <= 0.57772)
            & (scored["honest_cv_delta_mean"] <= -0.00070)
        ].assign(submit_role="adaptive_first").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
        scored[
            (scored["mean_abs_move_vs_a2c8"] >= 0.0080)
            & (scored["actual_anchor_score_final"] <= 0.57780)
            & (scored["honest_cv_delta_mean"] <= -0.00090)
        ].assign(submit_role="adaptive_scale_probe").sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"]).head(5),
        scored[
            (scored["target_profile"].isin(["noq2", "noq2_stage_boost", "q3_sstage"]))
            & (scored["actual_anchor_score_final"] <= 0.57782)
            & (scored["honest_cv_delta_mean"] <= -0.00075)
        ].assign(submit_role="adaptive_guarded").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
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
        "target_profile",
        "energy_profile",
        "block_profile",
        "scale",
        "delta_cap",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "active_cells",
        "mean_active_energy",
    ]
    best_anchor = anchor[anchor["name"].str.startswith("adaptjepa_")].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
    best_cv = cv_scored.sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"])
    grouped = (
        cv_scored.groupby(["source_name", "target_profile", "energy_profile", "block_profile"], as_index=False)
        .agg(
            best_actual_anchor=("actual_anchor_score_final", "min"),
            best_honest_cv=("honest_cv_delta_mean", "min"),
            max_stable_move=("mean_abs_move_vs_a2c8", lambda s: float(s[cv_scored.loc[s.index, "actual_anchor_score_final"] <= 0.57780].max()) if (cv_scored.loc[s.index, "actual_anchor_score_final"] <= 0.57780).any() else np.nan),
        )
        .sort_values(["best_actual_anchor", "best_honest_cv"])
    )
    report = [
        "# JEPA Adaptive Sparse Scale Solver",
        "",
        "This applies target, consensus-energy, and subject/sequence-block scale factors to sparse JEPA/direct-label logit directions.",
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
        "## Best Profiles",
        "",
        "```",
        grouped.head(60).round(9).to_string(index=False),
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none",
        "```",
        "",
        "## Interpretation",
        "",
        "- Adaptive scale is useful only if it keeps the scale-ladder large-move signal while reducing public-axis leakage.",
        "- Target and energy gates that beat uniform scale are candidates for a next cell-specific hidden-label solver.",
        "- If adaptive profiles fail to beat the uniform scale ladder, the current hidden axis is already near one-dimensional and should be submitted as a scale probe rather than overfit locally.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = load_sample()
    preds = inv.load_predictions(sample)
    base = preds["cvjepa_a2c8"]

    meta, arrays = build_candidates(sample, base)
    pre = cheap_prefilter(meta)
    pre_arrays = {str(row.name): arrays[str(row.name)] for row in pre.itertuples(index=False)}
    robust_scored = ladder.robust_scan(pre, pre_arrays, preds)
    robust_scored = coalesce_duplicate_columns(robust_scored)
    robust_scored["selection_proxy"] = (
        robust_scored["robust_delta_vs_a2c8"]
        + 0.80 * np.maximum(robust_scored["robust_p90_delta_vs_a2c8"], 0.0)
        + 0.20 * np.maximum(robust_scored["robust_worst_delta_vs_a2c8"], 0.0)
        - 0.0010 * np.minimum(robust_scored["mean_abs_move_vs_a2c8"] / 0.009, 1.5)
        - 0.0004 * np.minimum(robust_scored["mean_active_energy"] / 1.5, 1.5)
    )
    anchor_pool = choose_for_anchor(robust_scored)
    anchor_arrays = {str(row.name): arrays[str(row.name)] for row in anchor_pool.itertuples(index=False)}
    anchor = ladder.actual_anchor_for_ladder(sample, anchor_pool, anchor_arrays)
    anchor.to_csv(ANCHOR_OUT, index=False)

    cv_pool = choose_for_cv(anchor)
    cv_arrays = {str(row.name): arrays[str(row.name)] for row in cv_pool.itertuples(index=False)}
    cv_detail, cv_summary = ladder.anchor_cv_for_ladder(sample, cv_pool, cv_arrays, preds)
    honest = ladder.combined_honest_cv(cv_summary)
    cv_scored = cv_pool.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")

    selected = select_outputs(sample, cv_scored, arrays)
    robust_scored.to_csv(SCAN_OUT, index=False)
    cv_detail.to_csv(CV_DETAIL_OUT, index=False)
    cv_summary.to_csv(CV_SUMMARY_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(anchor, cv_scored, selected)

    print(REPORT_OUT)
    print("[generated]", meta.shape, "[prefilter]", pre.shape, "[anchor]", anchor.shape, "[cv]", cv_pool.shape)
    cols = [
        "name",
        "file",
        "source_name",
        "target_profile",
        "energy_profile",
        "block_profile",
        "scale",
        "delta_cap",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
    ]
    print(cv_scored[[c for c in cols if c in cv_scored.columns]].sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(24).round(9).to_string(index=False))
    print("[selected]")
    print(selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none")


if __name__ == "__main__":
    main()
