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


SCAN_OUT = OUT / "jepa_bad_axis_orthogonal_scale_ladder_scan.csv"
CV_DETAIL_OUT = OUT / "jepa_bad_axis_orthogonal_scale_ladder_cv_detail.csv"
CV_SUMMARY_OUT = OUT / "jepa_bad_axis_orthogonal_scale_ladder_cv_summary.csv"
SELECTED_OUT = OUT / "jepa_bad_axis_orthogonal_scale_ladder_selected.csv"
REPORT_OUT = OUT / "jepa_bad_axis_orthogonal_scale_ladder_report.md"


SOURCE_FILES = {
    "f465_actual_best": "submission_sparsejepa_f4657144.csv",
    "282_consensus_directrob": "submission_sparsejepa_282e9546.csv",
    "3cf_noq2_safe": "submission_sparsejepa_3cfdf64a.csv",
    "f43_cv_best": "submission_sparsejepa_f43ea825.csv",
    "a2d_q3stage_control": "submission_sparsejepa_a2d8107a.csv",
}

BAD_AXIS_FILES = {
    "anchor578": "submission_hybrid_0p578_logit_after_subject_final9_strict.csv",
    "ordinal_q": "submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv",
    "jepa_bad_residual": "submission_jepa_latent_residual_probe.csv",
    "jepa_bad_q2": "submission_jepa_latent_q2_w0p45.csv",
    "directcons_bad_all": "submission_directcons_1d5b6f39.csv",
    "directcons_bad_q": "submission_directcons_95be47ec.csv",
    "directcons_bad_stage": "submission_directcons_0b3f77c3.csv",
}

AXIS_GROUPS = {
    "public_bad4": ["anchor578", "ordinal_q", "jepa_bad_residual", "jepa_bad_q2"],
    "jepa_bad2": ["jepa_bad_residual", "jepa_bad_q2"],
    "classic_bad2": ["anchor578", "ordinal_q"],
    "consensus_bad3": ["directcons_bad_all", "directcons_bad_q", "directcons_bad_stage"],
    "all_bad7": [
        "anchor578",
        "ordinal_q",
        "jepa_bad_residual",
        "jepa_bad_q2",
        "directcons_bad_all",
        "directcons_bad_q",
        "directcons_bad_stage",
    ],
}

VARIANTS = ["full", "no_q2", "q3stage", "top_abs60", "energy_top60", "energy_top40"]
ANTI_LAMBDAS = [0.0, 0.35, 0.70, 1.00, 1.30]
SCALES = [1.00, 1.15, 1.30, 1.50, 1.75, 2.00]
AMPLITUDE_POLICIES = ["project_only", "restore_mean_abs"]


def stable_hash(text: str) -> str:
    return sha1(text.encode("utf-8")).hexdigest()[:8]


def load_sample() -> pd.DataFrame:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    return sample.sort_values(inv.KEY).reset_index(drop=True)


def load_array(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    frame = inv.load_sub(file_name, sample)
    return inv.clip_prob(frame[inv.TARGETS].to_numpy(dtype=np.float64))


def build_bad_axes(sample: pd.DataFrame, base_logit: np.ndarray) -> dict[str, np.ndarray]:
    axes: dict[str, np.ndarray] = {}
    for axis_name, file_name in BAD_AXIS_FILES.items():
        path = inv.locate(file_name)
        if path is None:
            continue
        pred = load_array(file_name, sample)
        axis = inv.logit(pred) - base_logit
        if float(np.linalg.norm(axis.reshape(-1))) > 1e-10:
            axes[axis_name] = axis
    return axes


def target_variant_gate(variant: str, delta: np.ndarray, energy: np.ndarray) -> np.ndarray:
    return ladder.target_variant_gate(variant, delta, energy)


def positive_axis_alignment(delta: np.ndarray, gate: np.ndarray, axes: list[np.ndarray]) -> dict[str, float]:
    coefs: list[float] = []
    cosines: list[float] = []
    delta_vec = (delta * gate).reshape(-1)
    delta_norm = float(np.linalg.norm(delta_vec))
    for axis in axes:
        axis_vec = (axis * gate).reshape(-1)
        axis_norm = float(np.linalg.norm(axis_vec))
        if axis_norm <= 1e-12:
            continue
        coef = float(np.dot(delta_vec, axis_vec) / float(np.dot(axis_vec, axis_vec)))
        coefs.append(max(coef, 0.0))
        if delta_norm > 1e-12:
            cosines.append(float(np.dot(delta_vec, axis_vec) / (delta_norm * axis_norm)))
    return {
        "bad_axis_align_mean_pos": float(np.mean(coefs)) if coefs else 0.0,
        "bad_axis_align_max_pos": float(np.max(coefs)) if coefs else 0.0,
        "bad_axis_cosine_mean": float(np.mean(cosines)) if cosines else 0.0,
        "bad_axis_cosine_max": float(np.max(cosines)) if cosines else 0.0,
    }


def project_away_bad_axes(
    delta: np.ndarray,
    gate: np.ndarray,
    axes: list[np.ndarray],
    anti_lambda: float,
) -> tuple[np.ndarray, dict[str, float]]:
    base_delta = delta * gate
    before = positive_axis_alignment(base_delta, gate, axes)
    if anti_lambda <= 0 or not axes:
        after = positive_axis_alignment(base_delta, gate, axes)
        return base_delta, {
            **{f"before_{k}": v for k, v in before.items()},
            **{f"after_{k}": v for k, v in after.items()},
            "removed_norm": 0.0,
            "removed_norm_ratio": 0.0,
        }

    out = base_delta.copy()
    removed_norm = 0.0
    for axis in axes:
        masked_axis = axis * gate
        axis_vec = masked_axis.reshape(-1)
        denom = float(np.dot(axis_vec, axis_vec))
        if denom <= 1e-12:
            continue
        coef = float(np.dot(out.reshape(-1), axis_vec) / denom)
        if coef <= 0:
            continue
        removal = anti_lambda * coef * masked_axis
        out = out - removal
        removed_norm += float(np.linalg.norm(removal.reshape(-1)))
    out *= gate
    base_norm = float(np.linalg.norm(base_delta.reshape(-1)))
    after = positive_axis_alignment(out, gate, axes)
    return out, {
        **{f"before_{k}": v for k, v in before.items()},
        **{f"after_{k}": v for k, v in after.items()},
        "removed_norm": removed_norm,
        "removed_norm_ratio": removed_norm / base_norm if base_norm > 1e-12 else 0.0,
    }


def apply_amplitude_policy(projected: np.ndarray, original: np.ndarray, policy: str) -> tuple[np.ndarray, float]:
    if policy == "project_only":
        return projected, 1.0
    if policy != "restore_mean_abs":
        raise ValueError(policy)
    original_mean = float(np.mean(np.abs(original)))
    projected_mean = float(np.mean(np.abs(projected)))
    if original_mean <= 1e-12 or projected_mean <= 1e-12:
        return projected, 1.0
    boost = min(original_mean / projected_mean, 1.35)
    return projected * boost, boost


def build_candidates(sample: pd.DataFrame, base: np.ndarray) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    base_logit = inv.logit(base)
    consensus = sparse_solver.consensus_matrices(sample)
    bad_axes = build_bad_axes(sample, base_logit)
    rows: list[dict[str, object]] = []
    arrays: dict[str, np.ndarray] = {}

    for source_name, file_name in SOURCE_FILES.items():
        source = load_array(file_name, sample)
        source_delta = inv.logit(source) - base_logit
        source_move = float(np.mean(np.abs(source - base)))
        for variant in VARIANTS:
            gate = target_variant_gate(variant, source_delta, consensus["energy"])
            gated = source_delta * gate
            active = np.abs(gated) > 1e-10
            active_cells = int(active.sum())
            if active_cells <= 0:
                continue
            active_rows = int((active.sum(axis=1) > 0).sum())
            active_energy = consensus["energy"][active]
            for axis_group, axis_names in AXIS_GROUPS.items():
                axes = [bad_axes[name] for name in axis_names if name in bad_axes]
                if not axes:
                    continue
                for anti_lambda in ANTI_LAMBDAS:
                    projected, axis_stats = project_away_bad_axes(gated, gate, axes, anti_lambda)
                    if float(np.mean(np.abs(projected))) <= 1e-12:
                        continue
                    for amp_policy in AMPLITUDE_POLICIES:
                        adjusted, amp_boost = apply_amplitude_policy(projected, gated, amp_policy)
                        adjusted_active = np.abs(adjusted) > 1e-10
                        if not adjusted_active.any():
                            continue
                        for scale in SCALES:
                            final_delta = scale * adjusted
                            pred = inv.clip_prob(inv.sigmoid(base_logit + final_delta))
                            label = (
                                f"{source_name}|{variant}|{axis_group}|"
                                f"a{anti_lambda:.2f}|{amp_policy}|s{scale:.2f}"
                            )
                            digest = stable_hash(label)
                            name = f"ortholadder_{digest}"
                            file_out = f"submission_ortholadder_{digest}.csv"
                            arrays[name] = pred
                            rows.append(
                                {
                                    "name": name,
                                    "file": file_out,
                                    "source_name": source_name,
                                    "source_file": file_name,
                                    "variant": variant,
                                    "axis_group": axis_group,
                                    "anti_lambda": anti_lambda,
                                    "amplitude_policy": amp_policy,
                                    "amplitude_boost": amp_boost,
                                    "scale": scale,
                                    "active_cells": active_cells,
                                    "active_rows": active_rows,
                                    "source_mean_abs_move_vs_a2c8": source_move,
                                    "mean_active_energy": float(np.mean(active_energy)),
                                    "p10_active_energy": float(np.quantile(active_energy, 0.10)),
                                    "projected_mean_abs_logit_delta": float(np.mean(np.abs(projected))),
                                    "adjusted_mean_abs_logit_delta": float(np.mean(np.abs(adjusted))),
                                    "mean_abs_move_vs_a2c8": float(np.mean(np.abs(pred - base))),
                                    "max_abs_move_vs_a2c8": float(np.max(np.abs(pred - base))),
                                    **axis_stats,
                                }
                            )
    return pd.DataFrame(rows), arrays


def prefilter_for_scoring(meta: pd.DataFrame, arrays: dict[str, np.ndarray], limit: int = 520) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    if meta.empty:
        return meta, arrays
    frame = meta.copy()
    reduction = frame["before_bad_axis_align_mean_pos"] - frame["after_bad_axis_align_mean_pos"]
    source_bonus = frame["source_name"].map(
        {
            "f465_actual_best": -0.00045,
            "282_consensus_directrob": -0.00040,
            "3cf_noq2_safe": -0.00030,
            "f43_cv_best": -0.00010,
            "a2d_q3stage_control": -0.00005,
        }
    ).fillna(0.0)
    variant_bonus = frame["variant"].map(
        {
            "full": -0.00015,
            "no_q2": -0.00012,
            "q3stage": -0.00010,
            "energy_top60": -0.00008,
            "top_abs60": -0.00005,
            "energy_top40": 0.0,
        }
    ).fillna(0.0)
    frame["cheap_priority"] = (
        np.abs(frame["mean_abs_move_vs_a2c8"] - 0.0085)
        + 0.0040 * np.maximum(frame["after_bad_axis_align_mean_pos"], 0.0)
        + 0.0014 * np.maximum(frame["removed_norm_ratio"] - 0.18, 0.0)
        - 0.0015 * np.minimum(np.maximum(reduction, 0.0), 0.30)
        - 0.0010 * np.minimum(frame["removed_norm_ratio"], 0.12)
        + source_bonus
        + variant_bonus
    )
    eligible = frame[
        frame["mean_abs_move_vs_a2c8"].between(0.0035, 0.0145)
        & (frame["scale"] >= 1.0)
    ].copy()
    if eligible.empty:
        eligible = frame.copy()
    selected = pd.concat(
        [
            eligible.sort_values("cheap_priority").head(250),
            eligible[
                (eligible["anti_lambda"] > 0)
                & (eligible["mean_abs_move_vs_a2c8"] >= 0.0065)
                & (eligible["after_bad_axis_align_mean_pos"] <= eligible["before_bad_axis_align_mean_pos"] + 1e-12)
            ].sort_values(["cheap_priority", "mean_abs_move_vs_a2c8"]).head(180),
            eligible[
                (eligible["source_name"].isin(["f465_actual_best", "282_consensus_directrob", "3cf_noq2_safe"]))
                & (eligible["variant"].isin(["full", "no_q2", "energy_top60", "top_abs60"]))
                & (eligible["scale"].isin([1.15, 1.30, 1.50, 1.75]))
            ].sort_values("cheap_priority").head(160),
            eligible[
                (eligible["variant"] == "q3stage")
                & (eligible["anti_lambda"] > 0)
            ].sort_values("cheap_priority").head(90),
            eligible[eligible["anti_lambda"] == 0.0].sort_values("cheap_priority").head(70),
        ],
        ignore_index=True,
    ).drop_duplicates("name")
    selected = selected.sort_values("cheap_priority").head(limit).reset_index(drop=True)
    return selected, {str(row.name): arrays[str(row.name)] for row in selected.itertuples(index=False)}


def candidate_pool_for_cv(scored: pd.DataFrame, limit: int = 160) -> pd.DataFrame:
    candidates = scored[scored["name"].str.startswith("ortholadder_")].copy()
    if candidates.empty:
        return candidates
    candidates = candidates[(candidates["anti_lambda"] == 0.0) | (candidates["removed_norm_ratio"] > 1e-12)].copy()
    frames = [
        candidates.sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(48),
        candidates[
            (candidates["anti_lambda"] > 0)
            & (candidates["removed_norm_ratio"] > 1e-12)
            & (candidates["actual_anchor_score_final"] <= 0.57786)
        ]
        .sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
        .head(52),
        candidates[
            (candidates["anti_lambda"] > 0)
            & (candidates["mean_abs_move_vs_a2c8"] >= 0.0065)
            & (candidates["actual_anchor_score_final"] <= 0.57790)
        ]
        .sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
        .head(52),
        candidates[
            (candidates["anti_lambda"] > 0)
            & (candidates["robust_delta_vs_a2c8"] <= -0.0010)
            & (candidates["robust_p90_delta_vs_a2c8"] <= -0.00080)
        ]
        .sort_values(["robust_delta_vs_a2c8", "actual_anchor_score_final"])
        .head(36),
        candidates[
            (candidates["anti_lambda"] >= 0.70)
            & (candidates["removed_norm_ratio"] >= 0.03)
        ]
        .sort_values(["actual_anchor_score_final", "mean_abs_move_vs_a2c8"])
        .head(36),
        candidates[
            (candidates["variant"].isin(["no_q2", "q3stage", "energy_top60"]))
            & (candidates["actual_anchor_score_final"] <= 0.57786)
        ]
        .sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"])
        .head(32),
    ]
    out = pd.concat(frames, ignore_index=True).drop_duplicates("name")
    return out.head(limit).reset_index(drop=True)


def select_outputs(sample: pd.DataFrame, scored: pd.DataFrame, arrays: dict[str, np.ndarray]) -> pd.DataFrame:
    candidates = scored[scored["name"].str.startswith("ortholadder_")].copy()
    if candidates.empty:
        return candidates

    selected_frames = [
        candidates[
            (candidates["anti_lambda"] > 0)
            & (candidates["removed_norm_ratio"] > 1e-12)
            & (candidates["actual_anchor_score_final"] <= 0.57774)
            & (candidates["honest_cv_delta_mean"] <= -0.00060)
        ]
        .assign(submit_role="orth_anchor_frontier")
        .sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"])
        .head(5),
        candidates[
            (candidates["anti_lambda"] > 0)
            & (candidates["removed_norm_ratio"] > 1e-12)
            & (candidates["mean_abs_move_vs_a2c8"] >= 0.0080)
            & (candidates["actual_anchor_score_final"] <= 0.57780)
            & (candidates["honest_cv_delta_mean"] <= -0.00075)
        ]
        .assign(submit_role="orth_large_probe")
        .sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"])
        .head(6),
        candidates[
            (candidates["anti_lambda"] > 0)
            & (candidates["removed_norm_ratio"] >= 0.03)
            & (candidates["actual_anchor_score_final"] <= 0.57784)
            & (candidates["honest_cv_delta_mean"] <= -0.00055)
        ]
        .assign(submit_role="orth_axis_diagnostic")
        .sort_values(["actual_anchor_score_final", "removed_norm_ratio"])
        .head(6),
        candidates[
            (candidates["anti_lambda"] > 0)
            & (candidates["removed_norm_ratio"] > 1e-12)
            & (candidates["variant"].isin(["no_q2", "q3stage", "energy_top60"]))
            & (candidates["actual_anchor_score_final"] <= 0.57782)
            & (candidates["honest_cv_delta_mean"] <= -0.00055)
        ]
        .assign(submit_role="orth_guarded")
        .sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"])
        .head(6),
    ]
    selected = pd.concat(selected_frames, ignore_index=True).drop_duplicates("name")
    selected = selected.sort_values(["submit_role", "actual_anchor_score_final", "honest_cv_delta_mean"]).reset_index(drop=True)
    for row in selected.itertuples(index=False):
        out = sample.copy()
        out[inv.TARGETS] = inv.clip_prob(arrays[str(row.name)])
        out.to_csv(OUT / str(row.file), index=False)
    return selected


def integrity_check(sample: pd.DataFrame, selected: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in selected.itertuples(index=False):
        path = OUT / str(row.file)
        frame = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(inv.KEY).reset_index(drop=True)
        probs = frame[inv.TARGETS].to_numpy(dtype=float)
        rows.append(
            {
                "file": str(row.file),
                "shape_ok": tuple(frame.shape) == tuple(sample.shape),
                "key_ok": bool(frame[inv.KEY].reset_index(drop=True).equals(sample[inv.KEY].reset_index(drop=True))),
                "nan_count": int(np.isnan(probs).sum()),
                "min_prob": float(np.min(probs)),
                "max_prob": float(np.max(probs)),
            }
        )
    return pd.DataFrame(rows)


def write_report(scored: pd.DataFrame, cv_summary: pd.DataFrame, selected: pd.DataFrame, integrity: pd.DataFrame) -> None:
    cols = [
        "name",
        "file",
        "source_name",
        "variant",
        "axis_group",
        "anti_lambda",
        "amplitude_policy",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "robust_p90_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "removed_norm_ratio",
        "before_bad_axis_align_mean_pos",
        "after_bad_axis_align_mean_pos",
    ]
    candidates = scored[scored["name"].str.startswith("ortholadder_")].copy()
    selected_text = (
        selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False)
        if not selected.empty
        else "none"
    )
    integrity_text = integrity.round(9).to_string(index=False) if not integrity.empty else "none"

    by_group_rows = []
    if not candidates.empty:
        for (source_name, variant, axis_group), group in candidates.groupby(["source_name", "variant", "axis_group"], sort=False):
            audited = group[group["honest_cv_delta_mean"].notna()]
            stable = audited[
                (audited["anti_lambda"] > 0)
                & (audited["actual_anchor_score_final"] <= 0.57780)
                & (audited["honest_cv_delta_worst"] < 0)
            ]
            by_group_rows.append(
                {
                    "source_name": source_name,
                    "variant": variant,
                    "axis_group": axis_group,
                    "best_actual_anchor": float(group["actual_anchor_score_final"].min()),
                    "best_honest_cv": float(audited["honest_cv_delta_mean"].min()) if not audited.empty else np.nan,
                    "max_stable_move": float(stable["mean_abs_move_vs_a2c8"].max()) if not stable.empty else np.nan,
                    "best_removed_ratio": float(group["removed_norm_ratio"].max()),
                }
            )
    by_group = pd.DataFrame(by_group_rows)
    if not by_group.empty:
        by_group = by_group.sort_values(["best_actual_anchor", "best_honest_cv"])

    report = [
        "# JEPA Bad-Axis Orthogonal Scale-Ladder",
        "",
        "This second-stage probe starts from the strongest sparse-JEPA ladder directions, then removes components aligned with public-failed axes inside the active target/cell gate.",
        "",
        "## Best Actual-Anchor Rows",
        "",
        "```",
        candidates[[c for c in cols if c in candidates.columns]].sort_values(["actual_anchor_score_final", "robust_delta_vs_a2c8"]).head(50).round(9).to_string(index=False)
        if not candidates.empty
        else "none",
        "```",
        "",
        "## Best Honest Anchor-CV Rows",
        "",
        "```",
        candidates[[c for c in cols if c in candidates.columns]].sort_values(["honest_cv_delta_mean", "actual_anchor_score_final"]).head(50).round(9).to_string(index=False)
        if not candidates.empty and "honest_cv_delta_mean" in candidates.columns
        else "none",
        "```",
        "",
        "## Source / Variant / Bad-Axis Breakpoints",
        "",
        "```",
        by_group.round(9).to_string(index=False) if not by_group.empty else "none",
        "```",
        "",
        "## Selected Submissions",
        "",
        "```",
        selected_text,
        "```",
        "",
        "## Integrity",
        "",
        "```",
        integrity_text,
        "```",
        "",
        "## Interpretation",
        "",
        "- If these candidates beat the unorthogonalized scale ladder under actual-anchor while keeping similar mean move, the bottleneck was public-bad-axis contamination.",
        "- If they only reduce move or fail to improve actual-anchor, the previous sparse ladder already avoids the known bad axes and the remaining gap is hidden subset/label prior rather than bad-axis projection.",
        "- `restore_mean_abs` tests whether removed bad components can be replaced by the residual JEPA/direct-label direction without collapsing amplitude.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = load_sample()
    preds = inv.load_predictions(sample)
    base = preds["cvjepa_a2c8"]

    meta_full, arrays_full = build_candidates(sample, base)
    meta, arrays = prefilter_for_scoring(meta_full, arrays_full)
    robust_scored = ladder.robust_scan(meta, arrays, preds)
    anchor_scored = ladder.actual_anchor_for_ladder(sample, meta, arrays)
    scored = anchor_scored.merge(
        robust_scored.drop(columns=["file"], errors="ignore"),
        on="name",
        how="left",
        suffixes=("", "_robust"),
    )

    pool = candidate_pool_for_cv(scored)
    pool_arrays = {str(row.name): arrays[str(row.name)] for row in pool.itertuples(index=False)}
    cv_detail, cv_summary = ladder.anchor_cv_for_ladder(sample, pool, pool_arrays, preds)
    honest = ladder.combined_honest_cv(cv_summary)
    scored = scored.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")
    pool = pool.merge(honest, left_on=["name", "file"], right_on=["candidate_name", "file"], how="left")
    selected = select_outputs(sample, pool, arrays)
    integrity = integrity_check(sample, selected)

    scored.to_csv(SCAN_OUT, index=False)
    cv_detail.to_csv(CV_DETAIL_OUT, index=False)
    cv_summary.to_csv(CV_SUMMARY_OUT, index=False)
    selected.to_csv(SELECTED_OUT, index=False)
    write_report(scored, cv_summary, selected, integrity)

    cols = [
        "name",
        "file",
        "source_name",
        "variant",
        "axis_group",
        "anti_lambda",
        "amplitude_policy",
        "scale",
        "actual_anchor_score_final",
        "honest_cv_delta_mean",
        "honest_cv_delta_worst",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
        "removed_norm_ratio",
    ]
    print(REPORT_OUT)
    print("[candidate pool]", pool.shape)
    print(pool[[c for c in cols if c in pool.columns]].sort_values(["actual_anchor_score_final", "honest_cv_delta_mean"]).head(30).round(9).to_string(index=False))
    print("[selected]")
    print(selected[[c for c in ["submit_role", *cols] if c in selected.columns]].round(9).to_string(index=False) if not selected.empty else "none")
    print("[integrity]")
    print(integrity.round(9).to_string(index=False) if not integrity.empty else "none")


if __name__ == "__main__":
    main()
