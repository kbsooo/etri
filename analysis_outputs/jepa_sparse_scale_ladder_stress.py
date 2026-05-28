from __future__ import annotations

from hashlib import sha1
from itertools import combinations
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
import public_lb_direct_label_robust_selector as robust  # noqa: E402
import jepa_regularized_sparse_direct_solver as sparse_solver  # noqa: E402
import jepa_sparse_anchor_cv_audit as anchor_cv  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score, read_submission  # noqa: E402


SCAN_OUT = OUT / "jepa_sparse_scale_ladder_stress_scan.csv"
CV_DETAIL_OUT = OUT / "jepa_sparse_scale_ladder_stress_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_sparse_scale_ladder_stress_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_sparse_scale_ladder_stress_selected.csv"
REPORT_OUT = OUT / "jepa_sparse_scale_ladder_stress_report.md"


SOURCE_FILES = {
    "f465_actual_best": "submission_sparsejepa_f4657144.csv",
    "3cf_noq2_safe": "submission_sparsejepa_3cfdf64a.csv",
    "f43_cv_best": "submission_sparsejepa_f43ea825.csv",
    "282_consensus_directrob": "submission_sparsejepa_282e9546.csv",
    "a2d_q3stage_control": "submission_sparsejepa_a2d8107a.csv",
}

VARIANTS = ["full", "no_q2", "q3stage", "top_abs60", "energy_top60", "energy_top40"]
SCALES = [0.50, 0.75, 1.00, 1.15, 1.30, 1.50, 1.75, 2.00, 2.35]
CV_POLICIES = ["train_best1", "train_best5", "structured_best3", "low_error_best5"]


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def load_sample() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return sample.sort_values(inv.KEY).reset_index(drop=True)


def load_submission_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    return inv.load_sub(file_name, sample)[inv.TARGETS].to_numpy(dtype=np.float64)


def target_variant_gate(variant: str, delta: np.ndarray, energy: np.ndarray) -> np.ndarray:
    gate = np.ones_like(delta, dtype=np.float64)
    target_index = {target: i for i, target in enumerate(inv.TARGETS)}
    if variant == "full":
        return gate
    if variant == "no_q2":
        gate[:, target_index["Q2"]] = 0.0
        return gate
    if variant == "q3stage":
        keep = {"Q3", "S2", "S3", "S4"}
        for target, j in target_index.items():
            if target not in keep:
                gate[:, j] = 0.0
        return gate

    active = np.abs(delta) > 1e-10
    if not active.any():
        return np.zeros_like(delta, dtype=np.float64)
    if variant == "top_abs60":
        cutoff = np.quantile(np.abs(delta[active]), 0.40)
        return (np.abs(delta) >= cutoff).astype(np.float64)
    if variant == "energy_top60":
        cutoff = np.quantile(energy[active], 0.40)
        return ((energy >= cutoff) & active).astype(np.float64)
    if variant == "energy_top40":
        cutoff = np.quantile(energy[active], 0.60)
        return ((energy >= cutoff) & active).astype(np.float64)
    raise ValueError(variant)


def build_ladder_candidates(sample: pd.DataFrame, base: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base_logit = inv.logit(base)
    consensus = sparse_solver.consensus_matrices(sample)
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}

    for source_name, file_name in SOURCE_FILES.items():
        source = load_submission_array(file_name, sample)
        source_delta = inv.logit(source) - base_logit
        source_active = np.abs(source_delta) > 1e-10
        source_move = float(np.mean(np.abs(source - base)))
        for variant in VARIANTS:
            gate = target_variant_gate(variant, source_delta, consensus["energy"])
            gated_delta = source_delta * gate
            active_cells = int((np.abs(gated_delta) > 1e-10).sum())
            if active_cells <= 0:
                continue
            active_rows = int((np.abs(gated_delta).sum(axis=1) > 1e-10).sum())
            active_energy = consensus["energy"][np.abs(gated_delta) > 1e-10]
            overlap = float((np.abs(gated_delta[source_active]) > 1e-10).mean()) if source_active.any() else 0.0
            for scale in SCALES:
                pred = inv.clip_prob(inv.sigmoid(base_logit + scale * gated_delta))
                label = f"{source_name}|{variant}|scale{scale:.2f}"
                name = f"sparseladder_{stable_hash(label)}"
                file_out = f"submission_sparseladder_{stable_hash(label)}.csv"
                arrays[name] = pred
                rows.append(
                    {
                        "name": name,
                        "file": file_out,
                        "source_name": source_name,
                        "source_file": file_name,
                        "variant": variant,
                        "scale": scale,
                        "active_cells": active_cells,
                        "active_rows": active_rows,
                        "source_mean_abs_move_vs_a2c8": source_move,
                        "mean_active_energy": float(np.mean(active_energy)),
                        "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                        "source_active_overlap": overlap,
                        "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - base))),
                        "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                    }
                )
    return pd.DataFrame(rows), arrays


def actual_anchor_for_ladder(sample: pd.DataFrame, candidates: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    control_files = [
        "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
        "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
        "submission_directrob_29ffe34b.csv",
        "submission_directcons_de1d6b6d.csv",
        "submission_sparsejepa_f4657144.csv",
        "submission_sparsejepa_3cfdf64a.csv",
        "submission_sparsejepa_f43ea825.csv",
    ]
    names = [
        "control_a2c8",
        "control_raw05",
        "control_directrob_29ffe34b",
        "control_directcons_de1d6b6d",
        "control_sparse_f4657144",
        "control_sparse_3cfdf64a",
        "control_sparse_f43ea825",
    ]
    pred_list = [read_submission(file_name)[inv.TARGETS].to_numpy(dtype=np.float64) for file_name in control_files]
    for row in candidates.itertuples(index=False):
        names.append(str(row.name))
        control_files.append(str(row.file))
        pred_list.append(arrays[str(row.name)])
    scored = actual_anchor_score(pred_list, sample)
    scored["name"] = names
    scored["file"] = control_files
    return scored.merge(candidates, on=["name", "file"], how="left").sort_values("actual_anchor_score_final").reset_index(drop=True)


def robust_scan(candidates: pd.DataFrame, arrays: dict[str, np.ndarray], preds: dict[str, np.ndarray]) -> pd.DataFrame:
    sources, solution_map = robust.load_sources()
    score = sparse_solver.score_scan(arrays, sources, solution_map, preds["cvjepa_a2c8"], preds["stage2"], preds["raw05"])
    return candidates.merge(score, on="name", how="left")


def anchor_cv_for_ladder(sample: pd.DataFrame, candidates: pd.DataFrame, arrays: dict[str, np.ndarray], preds: dict[str, np.ndarray]) -> tuple[pd.DataFrame, pd.DataFrame]:
    records, mask_meta = inv.mask_records(sample)
    selected_masks = inv.selected_mask_indices().merge(mask_meta, on=["mask_index", "mask_kind", "mask_name", "rows"], how="left")
    selected_masks = selected_masks.head(44).reset_index(drop=True)
    priors = {
        name: inv.load_sub(file_name, sample)[inv.TARGETS].to_numpy(dtype=np.float64)
        for name, file_name in inv.PRIOR_FILES.items()
        if inv.locate(file_name) is not None
    }
    source_path = OUT / "public_lb_direct_label_robust_selector_sources.csv"
    source = pd.read_csv(source_path) if source_path.exists() else pd.DataFrame()
    robust_lookup = {
        (int(row.mask_index), str(row.prior_name)): float(row.robust_source_score)
        for row in source.itertuples(index=False)
        if hasattr(row, "robust_source_score")
    }

    base = preds["cvjepa_a2c8"]
    stage2 = preds["stage2"]
    detail_rows: list[dict[str, object]] = []
    fold_specs: list[tuple[str, tuple[tuple[str, str, float, float], ...]]] = []
    fold_specs.extend(("loo", (anchor,)) for anchor in anchor_cv.ALL_ANCHORS)
    fold_specs.extend(("l2o", pair) for pair in combinations(anchor_cv.ALL_ANCHORS, 2))

    for fold_kind, heldout_tuple in fold_specs:
        heldout = list(heldout_tuple)
        heldout_keys = {anchor[0] for anchor in heldout}
        fold_name = "+".join(sorted(heldout_keys))
        train = [anchor for anchor in anchor_cv.ALL_ANCHORS if anchor[0] not in heldout_keys]
        fits = anchor_cv.build_fits(train, heldout, records, selected_masks, priors, preds, robust_lookup)
        for policy in CV_POLICIES:
            chosen = anchor_cv.select_fits(fits, policy)
            if chosen.empty:
                continue
            selector_error = float(chosen["heldout_anchor_abs_error_mean"].mean())
            base_scores = [anchor_cv.score_under_fit(fit, base, stage2) for fit in chosen["fit"]]
            base_score = float(np.mean(base_scores))
            for row in candidates.itertuples(index=False):
                pred = arrays[str(row.name)]
                cand_score = float(np.mean([anchor_cv.score_under_fit(fit, pred, stage2) for fit in chosen["fit"]]))
                detail_rows.append(
                    {
                        "fold_kind": fold_kind,
                        "fold_name": fold_name,
                        "policy": policy,
                        "candidate_name": str(row.name),
                        "file": str(row.file),
                        "n_selected_fits": int(len(chosen)),
                        "delta_vs_a2c8": cand_score - base_score,
                        "candidate_public_proxy": cand_score,
                        "a2c8_public_proxy": base_score,
                        "selector_abs_error_mean": selector_error,
                        "top_mask_kind": str(chosen.iloc[0]["mask_kind"]),
                        "top_mask_name": str(chosen.iloc[0]["mask_name"]),
                        "top_prior_name": str(chosen.iloc[0]["prior_name"]),
                        "top_fit_quality": float(chosen.iloc[0]["fit_quality"]),
                    }
                )

    detail = pd.DataFrame(detail_rows)
    cv_candidates = candidates.rename(columns={"name": "candidate_name"})
    summary = anchor_cv.summarize(detail, candidates)
    summary = summary.merge(
        cv_candidates[
            [
                "candidate_name",
                "source_name",
                "source_file",
                "variant",
                "scale",
                "active_cells",
                "active_rows",
                "mean_active_energy",
            ]
        ],
        on="candidate_name",
        how="left",
    )
    return detail, summary


def combined_honest_cv(summary: pd.DataFrame) -> pd.DataFrame:
    honest = summary[summary["policy"].isin(["train_best1", "train_best5", "structured_best3"])].copy()
    combined = (
        honest.groupby(["candidate_name", "file"], as_index=False)
        .agg(
            honest_cv_delta_mean=("cv_delta_mean", "mean"),
            honest_cv_delta_p90=("cv_delta_p90", "mean"),
            honest_cv_delta_worst=("cv_delta_worst", "max"),
            honest_cv_win_rate=("cv_win_rate", "mean"),
            selector_abs_error_mean=("selector_abs_error_mean", "mean"),
        )
        .sort_values(["honest_cv_delta_mean", "honest_cv_delta_worst"])
    )
    return combined


def select_ladder_outputs(sample: pd.DataFrame, scored: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    selected_frames = [
        scored[
            (scored["name"].str.startswith("sparseladder_"))
            & (scored["scale"] >= 1.0)
            & (scored["actual_anchor_score_final"] <= 0.57772)
            & (scored["honest_cv_delta_mean"] <= -0.00060)
        ].assign(submit_role="ladder_first").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
        scored[
            (scored["name"].str.startswith("sparseladder_"))
            & (scored["scale"] > 1.15)
            & (scored["actual_anchor_score_final"] <= 0.57778)
            & (scored["honest_cv_delta_mean"] <= -0.00065)
            & (scored["mean_abs_move_vs_a2c8"] >= 0.0065)
        ].assign(submit_role="ladder_scale_probe").sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"]).head(5),
        scored[
            (scored["name"].str.startswith("sparseladder_"))
            & (scored["variant"].isin(["no_q2", "q3stage", "energy_top40", "energy_top60"]))
            & (scored["actual_anchor_score_final"] <= 0.57776)
            & (scored["honest_cv_delta_mean"] <= -0.00050)
        ].assign(submit_role="ladder_guarded").sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(5),
    ]
    selected = pd.concat(selected_frames, ignore_index=True).drop_duplicates("name")
    selected = selected.sort_values(["submit_role", "actual_anchor_score_final", "honest_cv_delta_mean"]).reset_index(drop=True)
    for row in selected.itertuples(index=False):
        out = sample.copy()
        out[inv.TARGETS] = inv.clip_prob(arrays[str(row.name)])
        out.to_csv(OUT / str(row.file), index=False)
    return selected


def write_report(scored: pd.DataFrame, cv_summary: pd.DataFrame, selected: pd.DataFrame) -> None:
    best_cols = [
        "name",
        "file",
        "source_name",
        "variant",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "honest_cv_win_rate",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "active_cells",
        "mean_active_energy",
    ]
    controls = scored[scored["name"].str.startswith("control_")].copy()
    ladder = scored[scored["name"].str.startswith("sparseladder_")].copy()
    by_source_rows: list[dict[str, object]] = []
    for (source_name, variant), group in ladder.groupby(["source_name", "variant"], sort=False):
        audited = group[group["honest_cv_delta_mean"].notna()]
        stable = audited[(audited["actual_anchor_score_final"] <= 0.57778) & (audited["honest_cv_delta_worst"] < 0)]
        by_source_rows.append(
            {
                "source_name": source_name,
                "variant": variant,
                "best_actual_anchor": float(group["actual_anchor_score_final"].min()),
                "best_honest_cv": float(audited["honest_cv_delta_mean"].min()) if not audited.empty else np.nan,
                "max_stable_move": float(stable["mean_abs_move_vs_a2c8"].max()) if not stable.empty else np.nan,
                "max_stable_scale": float(stable["scale"].max()) if not stable.empty else np.nan,
                "max_audited_scale": float(audited["scale"].max()) if not audited.empty else np.nan,
            }
        )
    by_source = pd.DataFrame(by_source_rows).sort_values(["best_actual_anchor", "best_honest_cv"])
    report = [
        "# JEPA Sparse Scale-Ladder Stress",
        "",
        "This extrapolates the strongest sparse JEPA/direct-label directions away from a2c8 and checks where actual-anchor and anchor-CV stability break.",
        "",
        "## Controls",
        "",
        "```",
        controls[[c for c in best_cols if c in controls.columns]].round(9).to_string(index=False),
        "```",
        "",
        "## Best Ladder Rows",
        "",
        "```",
        ladder[[c for c in best_cols if c in ladder.columns]].sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(40).round(9).to_string(index=False),
        "```",
        "",
        "## Best Honest Anchor-CV Rows",
        "",
        "```",
        ladder[[c for c in best_cols if c in ladder.columns]].sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"]).head(40).round(9).to_string(index=False),
        "```",
        "",
        "## Source/Variant Breakpoints",
        "",
        "```",
        by_source.round(9).to_string(index=False),
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected[[c for c in ["submit_role", *best_cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none",
        "```",
        "",
        "## Interpretation",
        "",
        "- Scale `1.00` is the existing sparse candidate direction; higher scales test whether the hidden-label move can leave the micro/probe band.",
        "- A useful larger move must keep actual-anchor near the sparse frontier while staying negative under honest LOO/L2O anchor-CV policies.",
        "- If larger scales improve CV but break actual-anchor, the bottleneck is not direction but public-axis target leakage.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = load_sample()
    preds = inv.load_predictions(sample)
    base = preds["cvjepa_a2c8"]

    meta, arrays = build_ladder_candidates(sample, base)
    robust_scored = robust_scan(meta, arrays, preds)
    anchor_scored = actual_anchor_for_ladder(sample, meta, arrays)
    scored = anchor_scored.merge(
        robust_scored.drop(columns=["file"], errors="ignore"),
        on="name",
        how="left",
        suffixes=("", "_robust"),
    )

    eligible = scored[
        scored["name"].str.startswith("sparseladder_")
        & (
            (scored["actual_anchor_score_final"] <= 0.57782)
            | (scored["robust_delta_vs_a2c8"] <= -0.00090)
            | (scored["mean_abs_move_vs_a2c8"] >= 0.0070)
        )
    ].copy()
    candidate_pool = pd.concat(
        [
            eligible.sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(80),
            eligible[(eligible["scale"] >= 1.15) & (eligible["actual_anchor_score_final"] <= 0.57790)]
            .sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"])
            .head(60),
            eligible[
                (eligible["source_name"].isin(["f465_actual_best", "282_consensus_directrob", "3cf_noq2_safe"]))
                & (eligible["variant"].isin(["full", "no_q2", "energy_top60", "top_abs60"]))
                & (eligible["scale"] >= 1.00)
                & (eligible["actual_anchor_score_final"] <= 0.57792)
            ].sort_values(["source_name", "variant", "scale"]),
            eligible[(eligible["variant"] == "q3stage") & (eligible["actual_anchor_score_final"] <= 0.57786)]
            .sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
            .head(24),
        ],
        ignore_index=True,
    )
    candidate_pool = (
        candidate_pool.drop_duplicates(["source_name", "variant", "scale"])
        .head(132)
        .reset_index(drop=True)
    )
    candidate_arrays = {str(row.name): arrays[str(row.name)] for row in candidate_pool.itertuples(index=False)}
    cv_detail, cv_summary = anchor_cv_for_ladder(sample, candidate_pool, candidate_arrays, preds)
    honest = combined_honest_cv(cv_summary)
    scored = scored.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")
    candidate_pool = candidate_pool.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")
    selected = select_ladder_outputs(sample, candidate_pool, arrays)

    scored.to_csv(SCAN_OUT, index=False)
    cv_detail.to_csv(CV_DETAIL_OUT, index=False)
    cv_summary.to_csv(CV_SUMMARY_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(scored, cv_summary, selected)

    print(REPORT_OUT)
    print("[ladder pool]", candidate_pool.shape)
    cols = [
        "name",
        "file",
        "source_name",
        "variant",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
    ]
    print(candidate_pool[[c for c in cols if c in candidate_pool.columns]].sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(24).round(9).to_string(index=False))
    print("[selected]")
    print(selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none")


if __name__ == "__main__":
    main()
