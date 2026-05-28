from __future__ import annotations

from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import KEY, TARGETS, clip, logit, sigmoid, stable_tag  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from lejepa_sigreg_candidate_audit import epps_pulley_sigreg, normalize_global  # noqa: E402
from raw05_anchor_jepa_micro_injection import (  # noqa: E402
    RAW05_FILE,
    actual_anchor_score,
    integrity,
    read_submission,
    save_submission,
)
from raw05_jepa_context_target_energy_gate import (  # noqa: E402
    energy_rows,
    fit_context_target_energy,
    row_gate,
    training_pool_files,
)
from raw05_jepa_efmicro_gate_refine import extract_targetw_from_labels  # noqa: E402
from raw05_jepa_q3stress_counterweight_local_refine import profile_vector, unique_existing  # noqa: E402


OUT_SCAN = OUT / "raw05_jepa_sigreg_gated_microrefine_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_sigreg_gated_microrefine_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_sigreg_gated_microrefine_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_sigreg_gated_microrefine_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_sigreg_gated_microrefine_report.md"

BETAS = [0.20, 0.28, 0.36, 0.44, 0.52, 0.60]
SIG_GATE_SPECS = [
    ("sig_bad_min_f010", 0.10, 0.80, 0.12, 0.90, "bad_sig_min"),
    ("sig_bad_min_f020", 0.20, 0.95, 0.18, 1.00, "bad_sig_min"),
    ("sig_energy_min_f015", 0.15, 0.85, 0.15, 0.90, "bad_sig_energy_min"),
    ("sig_balance_f010", 0.10, 0.80, 0.10, 0.75, "sig_balance"),
    ("sig_soft_only_f020", 0.20, 1.00, 0.20, 1.00, "sig_only"),
]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def load_arrays(files: list[str], sample: pd.DataFrame) -> dict[str, np.ndarray]:
    ref_key = sample[KEY].reset_index(drop=True)
    arrays: dict[str, np.ndarray] = {}
    for file_name in files:
        frame = read_submission(file_name)
        if not frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"key mismatch: {file_name}")
        arrays[file_name] = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    return arrays


def candidate_pools() -> tuple[list[str], list[str]]:
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    sigreg = pd.read_csv(OUT / "lejepa_sigreg_candidate_audit.csv")
    micro = pd.read_csv(OUT / "raw05_jepa_energyfront_microrefine_shortlist.csv")
    efgate = pd.read_csv(OUT / "raw05_jepa_efmicro_gate_refine_shortlist.csv")
    efback = pd.read_csv(OUT / "raw05_jepa_efgate_backoff_frontier_shortlist.csv")
    energy = pd.read_csv(OUT / "raw05_jepa_energy_constrained_frontier_shortlist.csv")
    targetw = pd.read_csv(OUT / "raw05_jepa_target_weight_optimizer_shortlist.csv")
    ctx = pd.read_csv(OUT / "raw05_jepa_context_target_energy_gate_shortlist.csv")

    bases: list[str] = []
    bases.extend(priority["file"].astype(str).head(8).tolist())
    bases.extend(
        sigreg[sigreg["family"].eq("raw05_jepa_efmicro")]
        .sort_values(["lejepa_combined_rank", "actual_anchor_score_final"])["file"]
        .astype(str)
        .head(14)
        .tolist()
    )
    bases.extend(micro.sort_values("actual_anchor_score_final")["file"].astype(str).head(8).tolist())
    bases.extend(micro.sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"].astype(str).head(8).tolist())
    bases.extend(energy.sort_values("actual_anchor_score_final")["file"].astype(str).head(4).tolist())

    donors: list[str] = []
    donors.extend(
        sigreg[sigreg["family"].isin(["raw05_jepa_efmicro", "raw05_jepa_efgate", "raw05_jepa_efback"])]
        .sort_values(["lejepa_residual_health", "actual_anchor_score_final"])["file"]
        .astype(str)
        .head(18)
        .tolist()
    )
    donors.extend(efgate.sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"].astype(str).head(12).tolist())
    donors.extend(efgate.sort_values(["actual_anchor_score_final", "bad_residual_axis_ratio"])["file"].astype(str).head(8).tolist())
    donors.extend(efback.sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"].astype(str).head(10).tolist())
    donors.extend(efback.sort_values(["actual_anchor_score_final", "bad_residual_axis_ratio"])["file"].astype(str).head(8).tolist())
    donors.extend(extract_targetw_from_labels(micro.sort_values("actual_anchor_score_final"), 6))
    donors.extend(
        targetw[targetw["bucket"].isin(["low_bad", "strict_raw", "raw_boundary"])]
        .sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"]
        .astype(str)
        .head(6)
        .tolist()
    )
    donors.extend(ctx.sort_values(["energy_delta_vs_base", "actual_anchor_score_final"])["file"].astype(str).head(5).tolist())
    donors.append(RAW05_FILE)

    return unique_existing(bases), unique_existing(donors)


def blend_profiles() -> list[tuple[str, np.ndarray]]:
    return [
        ("context_only", profile_vector(Q1=1.0, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("q1light", profile_vector(Q1=0.45, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("q2s1heavy", profile_vector(Q1=0.75, Q2=1.18, S1=1.18, S2=0.86, S3=0.86)),
        ("s123soft", profile_vector(Q1=0.55, Q2=0.95, S1=1.05, S2=0.74, S3=0.74)),
        ("target_tiny", profile_vector(Q1=0.75, Q2=0.90, Q3=0.08, S1=0.90, S2=0.90, S3=0.90, S4=0.08)),
    ]


def logistic_gate(diff: np.ndarray, floor: float, scale_mult: float) -> np.ndarray:
    scale = max(float(np.median(np.abs(diff))) * scale_mult, 1e-8)
    soft = 1.0 / (1.0 + np.exp(-np.clip(diff / scale, -40.0, 40.0)))
    return floor + (1.0 - floor) * soft


def bad_gate(base_pred: np.ndarray, prop_pred: np.ndarray, axes: dict[str, np.ndarray | float], floor: float, scale_mult: float) -> np.ndarray:
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    bad_axis = np.asarray(axes["bad_axis"], dtype=np.float64)
    base_contrib = ((base_pred - stage2) * bad_axis).sum(axis=1)
    prop_contrib = ((prop_pred - stage2) * bad_axis).sum(axis=1)
    return logistic_gate(base_contrib - prop_contrib, floor, scale_mult)


def public_axis_embedding(pred: np.ndarray, raw: np.ndarray, axes: dict[str, np.ndarray | float]) -> np.ndarray:
    delta = pred - raw
    bad = np.asarray(axes["bad_axis"], dtype=np.float64)
    ordinal = np.asarray(axes["ordinal_axis"], dtype=np.float64)
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    raw05 = np.asarray(axes["raw05"], dtype=np.float64)
    stage2_axis = stage2 - raw05
    return np.column_stack(
        [
            (delta * bad).sum(axis=1),
            (delta * ordinal).sum(axis=1),
            (delta * stage2_axis).sum(axis=1),
            np.abs(delta).mean(axis=1),
        ]
    )


def public_axis_norm(pred: np.ndarray, raw: np.ndarray, axes: dict[str, np.ndarray | float], scale: np.ndarray) -> np.ndarray:
    z = public_axis_embedding(pred, raw, axes)
    return np.sqrt(np.mean((z / scale.reshape(1, -1)) ** 2, axis=1))


def row_anisotropy(residual_logit: np.ndarray) -> np.ndarray:
    abs_res = np.abs(residual_logit)
    rms = np.sqrt(np.mean(abs_res**2, axis=1))
    return abs_res.max(axis=1) / np.maximum(rms, 1e-12)


def sigreg_proxy_gate(
    base_pred: np.ndarray,
    prop_pred: np.ndarray,
    raw_pred: np.ndarray,
    base_logit: np.ndarray,
    prop_logit: np.ndarray,
    raw_logit: np.ndarray,
    axes: dict[str, np.ndarray | float],
    scale: np.ndarray,
    floor: float,
    scale_mult: float,
) -> tuple[np.ndarray, dict[str, float]]:
    base_norm = public_axis_norm(base_pred, raw_pred, axes, scale)
    prop_norm = public_axis_norm(prop_pred, raw_pred, axes, scale)
    base_aniso = row_anisotropy(base_logit - raw_logit)
    prop_aniso = row_anisotropy(prop_logit - raw_logit)
    norm_diff = base_norm - prop_norm
    aniso_diff = base_aniso - prop_aniso
    gate_norm = logistic_gate(norm_diff, floor, scale_mult)
    gate_aniso = logistic_gate(aniso_diff, floor, scale_mult)
    gate = np.minimum(gate_norm, gate_aniso)
    meta = {
        "public_norm_delta_mean": float((prop_norm - base_norm).mean()),
        "public_norm_delta_p90": float(np.quantile(prop_norm - base_norm, 0.90)),
        "row_aniso_delta_mean": float((prop_aniso - base_aniso).mean()),
        "row_aniso_delta_p90": float(np.quantile(prop_aniso - base_aniso, 0.90)),
        "sig_gate_mean": float(gate.mean()),
        "sig_gate_p10": float(np.quantile(gate, 0.10)),
    }
    return gate, meta


def gated_logit(
    gate_name: str,
    bad_floor: float,
    bad_scale: float,
    sig_floor: float,
    sig_scale: float,
    kind: str,
    base_logit: np.ndarray,
    prop_logit: np.ndarray,
    raw_logit: np.ndarray,
    raw_pred: np.ndarray,
    model: dict[str, np.ndarray | float],
    axes: dict[str, np.ndarray | float],
    axis_scale: np.ndarray,
) -> tuple[np.ndarray, dict[str, float]]:
    base_pred = sigmoid(base_logit)
    prop_pred = sigmoid(prop_logit)
    g_bad = bad_gate(base_pred, prop_pred, axes, bad_floor, bad_scale)
    g_sig, sig_meta = sigreg_proxy_gate(
        base_pred, prop_pred, raw_pred, base_logit, prop_logit, raw_logit, axes, axis_scale, sig_floor, sig_scale
    )
    e_base = energy_rows(base_logit - raw_logit, model)
    e_prop = energy_rows(prop_logit - raw_logit, model)
    g_energy = row_gate(e_base, e_prop, "soft_floor")

    if kind == "bad_sig_energy_min":
        gate = np.minimum(np.minimum(g_bad, g_sig), g_energy)
    elif kind == "bad_sig_min":
        gate = np.minimum(g_bad, g_sig)
    elif kind == "sig_balance":
        gate = np.minimum(g_sig, 0.65 * g_bad + 0.35 * g_energy)
    elif kind == "sig_only":
        gate = g_sig
    else:
        raise ValueError(f"unknown gate kind: {kind}")

    final_logit = base_logit + (prop_logit - base_logit) * gate.reshape(-1, 1)
    meta = {
        "row_gate": gate_name,
        "gate_mean": float(gate.mean()),
        "gate_p10": float(np.quantile(gate, 0.10)),
        "bad_gate_mean": float(g_bad.mean()),
        "energy_gate_mean": float(g_energy.mean()),
    }
    meta.update(sig_meta)
    return final_logit, meta


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    label: str,
    pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
    meta: dict[str, object],
) -> None:
    pred = clip(pred)
    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    row = {"label": label, "prediction_hash": pred_hash}
    row.update(meta)
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def axis_scale(raw: np.ndarray, bases: list[str], arrays: dict[str, np.ndarray], axes: dict[str, np.ndarray | float]) -> np.ndarray:
    embeds = [public_axis_embedding(arrays[file_name], raw, axes) for file_name in bases if file_name in arrays]
    z = np.vstack(embeds)
    scale = np.median(np.abs(z - np.median(z, axis=0, keepdims=True)), axis=0)
    return np.maximum(scale, 1e-8)


def generate_candidates(
    bases: list[str],
    donors: list[str],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    model: dict[str, np.ndarray | float],
    axes: dict[str, np.ndarray | float],
) -> tuple[list[dict[str, object]], list[np.ndarray]]:
    raw_logit = logit(raw)
    logits = {file_name: logit(arrays[file_name]) for file_name in arrays}
    energy_cache = {file_name: energy_rows(logits[file_name] - raw_logit, model) for file_name in arrays}
    axis_scale_value = axis_scale(raw, bases, arrays, axes)
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in bases:
        base_logit = logits[base_file]
        base_energy = energy_cache[base_file]
        for donor_file in donors:
            if donor_file == base_file:
                continue
            donor_logit = logits[donor_file]
            donor_energy = energy_cache[donor_file]
            step0 = donor_logit - base_logit
            for profile_name, profile_gate in blend_profiles():
                step = step0 * profile_gate
                if np.abs(step).mean() <= 1e-10:
                    continue
                for beta in BETAS:
                    prop_logit = base_logit + beta * step
                    for gate_name, bad_floor, bad_scale, sig_floor, sig_scale, kind in SIG_GATE_SPECS:
                        final_logit, gate_meta = gated_logit(
                            gate_name,
                            bad_floor,
                            bad_scale,
                            sig_floor,
                            sig_scale,
                            kind,
                            base_logit,
                            prop_logit,
                            raw_logit,
                            raw,
                            model,
                            axes,
                            axis_scale_value,
                        )
                        pred = sigmoid(final_logit)
                        final_energy = energy_rows(final_logit - raw_logit, model)
                        label = (
                            f"{base_file}|donor={donor_file}|profile={profile_name}|b={beta:.3f}|"
                            f"siggate={gate_name}"
                        )
                        meta = {
                            "base_file": base_file,
                            "donor_file": donor_file,
                            "blend_profile": profile_name,
                            "beta": float(beta),
                            "base_energy_mean": float(base_energy.mean()),
                            "donor_energy_mean": float(donor_energy.mean()),
                            "final_energy_mean": float(final_energy.mean()),
                            "energy_delta_vs_base": float(final_energy.mean() - base_energy.mean()),
                            "energy_delta_vs_donor": float(final_energy.mean() - donor_energy.mean()),
                            "energy_improve_rate_vs_base": float((final_energy < base_energy).mean()),
                        }
                        meta.update(gate_meta)
                        add_candidate(rows, preds, seen, label, pred, axes, meta)
    return rows, preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["proxy_health_penalty"] = (
        np.maximum(frame["public_norm_delta_mean"], 0.0) * 0.000010
        + np.maximum(frame["row_aniso_delta_mean"], 0.0) * 0.000006
        + np.maximum(frame["energy_delta_vs_base"], 0.0) * 0.00022
    )
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 270.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.00068, 0.0) * 0.085
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.00155, 0.0) * 0.035
        + frame["proxy_health_penalty"]
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.15e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00068)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692)
            & (frame["public_norm_delta_mean"] <= 0.03),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 8.5e-8)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00085)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["prefilter_score"],
            850,
        ),
        (
            (frame["bad_residual_axis_ratio"].abs() <= 0.00045)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.15e-7)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["bad_residual_axis_ratio", "prefilter_score"],
            700,
        ),
        (
            (frame["energy_delta_vs_base"] <= 0.0)
            & (frame["public_norm_delta_mean"] <= 0.0)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00090),
            ["prefilter_score"],
            700,
        ),
        (
            (frame["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00090),
            ["posterior_expected_public_vs_anchor", "prefilter_score"],
            600,
        ),
    ]
    parts = [frame[mask].sort_values(sort_cols).head(limit) for mask, sort_cols, limit in specs]
    parts.append(frame.sort_values("prefilter_score").head(1000))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(3200)


def quick_health(pred: np.ndarray, raw: np.ndarray, raw_logit: np.ndarray, axes: dict[str, np.ndarray | float], rng: np.random.Generator) -> dict[str, float]:
    pred_logit = logit(pred)
    z_all = pred_logit - raw_logit
    z_target = pred_logit[:, [TARGETS.index("Q3"), TARGETS.index("S4")]] - raw_logit[
        :, [TARGETS.index("Q3"), TARGETS.index("S4")]
    ]
    z_public = public_axis_embedding(pred, raw, axes)

    zg_all, stats_all = normalize_global(z_all)
    zg_target, _ = normalize_global(z_target)
    zg_public, stats_public = normalize_global(z_public)

    all_sigreg = epps_pulley_sigreg(zg_all, rng, num_slices=40)
    target_sigreg = epps_pulley_sigreg(zg_target, rng, num_slices=40)
    public_sigreg = epps_pulley_sigreg(zg_public, rng, num_slices=40)
    health = (
        0.34 * all_sigreg
        + 0.22 * target_sigreg
        + 0.29 * public_sigreg
        + 0.15 * float(stats_all["cov_eig_cv"])
    )
    return {
        "quick_lejepa_health": float(health),
        "quick_all_sigreg": float(all_sigreg),
        "quick_target_q3s4_sigreg": float(target_sigreg),
        "quick_public_axis_sigreg": float(public_sigreg),
        "quick_all_cov_eig_cv": float(stats_all["cov_eig_cv"]),
        "quick_public_axis_cov_eig_cv": float(stats_public["cov_eig_cv"]),
    }


def score_candidates(selected_for_scoring: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame, raw: np.ndarray, axes: dict[str, np.ndarray | float]) -> pd.DataFrame:
    indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 260.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00065, 0.0) * 0.080
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.70
        + np.maximum(scored["energy_delta_vs_base"], 0.0) * 0.00022
        + np.maximum(scored["public_norm_delta_mean"], 0.0) * 0.000004
    )
    scored["lowbad_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00038, 0.0) * 0.090
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57692, 0.0) * 0.70
    )

    sigreg_pool = pd.concat(
        [
            scored.sort_values("selection_score").head(900),
            scored.sort_values("actual_anchor_score_final").head(650),
            scored.sort_values(["bad_residual_axis_ratio", "selection_score"]).head(500),
            scored[scored["energy_delta_vs_base"] <= 0.0].sort_values("selection_score").head(450),
            scored[scored["posterior_expected_public_vs_anchor"] <= 0.57690].sort_values("selection_score").head(400),
        ],
        ignore_index=False,
    ).drop_duplicates("prediction_hash")
    sigreg_pool = sigreg_pool.sort_values(["selection_score", "actual_anchor_score_final"]).head(1700).reset_index(drop=True)

    rng = np.random.default_rng(2026052702)
    raw_logit = logit(raw)
    health_rows = []
    for _, row in sigreg_pool.iterrows():
        health_rows.append(quick_health(preds[int(row["candidate_index"])], raw, raw_logit, axes, rng))
    health = pd.DataFrame(health_rows)
    sigreg_pool = pd.concat([sigreg_pool, health], axis=1)
    sigreg_pool["actual_rank"] = sigreg_pool["actual_anchor_score_final"].rank(method="min")
    sigreg_pool["health_rank"] = sigreg_pool["quick_lejepa_health"].rank(method="min")
    sigreg_pool["bad_rank"] = sigreg_pool["bad_residual_axis_ratio"].rank(method="min")
    sigreg_pool["posterior_rank"] = sigreg_pool["posterior_expected_public_vs_anchor"].rank(method="min")
    sigreg_pool["sigreg_rank_score"] = (
        0.48 * sigreg_pool["actual_rank"]
        + 0.26 * sigreg_pool["health_rank"]
        + 0.16 * sigreg_pool["bad_rank"]
        + 0.10 * sigreg_pool["posterior_rank"]
    )
    sigreg_pool["sigreg_selection_score"] = (
        sigreg_pool["selection_score"]
        + np.maximum(sigreg_pool["quick_lejepa_health"] - 10.25, 0.0) * 0.00000018
    )
    return sigreg_pool.sort_values(["sigreg_rank_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "siggate_combined",
            (scored["delta_vs_raw05_rawaxis"] <= 1.15e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00068)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["sigreg_rank_score", "actual_anchor_score_final"],
            24,
        ),
        (
            "siggate_health_micro",
            (scored["quick_lejepa_health"] <= 10.35)
            & (scored["actual_anchor_score_final"] <= 0.5778394)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00075),
            ["quick_lejepa_health", "actual_anchor_score_final"],
            18,
        ),
        (
            "siggate_energy_guarded",
            (scored["energy_delta_vs_base"] <= 0.0)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["quick_lejepa_health"] <= 10.75),
            ["actual_anchor_score_final", "quick_lejepa_health"],
            18,
        ),
        (
            "siggate_lowbad",
            (scored["bad_residual_axis_ratio"].abs() <= 0.00020)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["quick_lejepa_health", "actual_anchor_score_final"],
            16,
        ),
        (
            "siggate_posterior_safe",
            (scored["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00085),
            ["sigreg_rank_score", "actual_anchor_score_final"],
            16,
        ),
        (
            "siggate_raw_tight",
            (scored["delta_vs_raw05_rawaxis"] <= 8.5e-8)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00085)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57693),
            ["sigreg_rank_score", "actual_anchor_score_final"],
            16,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["sigreg_rank_score", "actual_anchor_score_final"]).head(18).assign(bucket="siggate_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["sigreg_rank_score", "actual_anchor_score_final"]).head(64).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_siggate_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "quick_lejepa_health",
        "sigreg_rank_score",
        "mean_abs_move_vs_raw05",
        "energy_delta_vs_base",
        "public_norm_delta_mean",
        "row_aniso_delta_mean",
        "blend_profile",
        "beta",
        "row_gate",
        "gate_mean",
        "sig_gate_mean",
        "base_file",
        "donor_file",
    ]
    by_gate = (
        scored.sort_values("sigreg_rank_score")
        .groupby(["blend_profile", "row_gate", "beta"], as_index=False)
        .head(1)
        .sort_values("sigreg_rank_score")
    )
    lines = [
        "# Raw05 JEPA SIGReg-Gated Microrefine",
        "",
        "This pass applies the LeJEPA residual-health idea during row gating.",
        "Rows are moved only when bad-axis, context-target energy, and cheap public-axis/SIGReg proxies agree enough.",
        "",
        "## Counts",
        "",
        f"- generated candidates: {len(scan)}",
        f"- actual-anchor and quick-SIGReg rescored candidates: {len(scored)}",
        f"- saved candidates: {len(selected)}",
        "",
        "## Top Saved",
        "",
        "```csv",
        selected[cols].head(64).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best By Blend / Gate / Beta",
        "",
        "```csv",
        by_gate[
            [
                "blend_profile",
                "row_gate",
                "beta",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "bad_residual_axis_ratio",
                "quick_lejepa_health",
                "sigreg_rank_score",
                "energy_delta_vs_base",
                "public_norm_delta_mean",
                "row_aniso_delta_mean",
                "base_file",
                "donor_file",
            ]
        ]
        .head(64)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(64).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    bases, donors = candidate_pools()
    train_files = training_pool_files()
    files = unique_existing([RAW05_FILE, *bases, *donors, *train_files])
    arrays = load_arrays(files, sample)
    axes = public_axes()
    model = fit_context_target_energy({name: arrays[name] for name in train_files if name in arrays}, raw)

    rows, preds = generate_candidates(bases, donors, arrays, raw, model, axes)
    scan = pd.DataFrame(rows)
    scan.to_csv(OUT_SCAN, index=False)

    selected_for_scoring = prefilter(scan)
    scored = score_candidates(selected_for_scoring, preds, sample, raw, axes)
    scored.to_csv(OUT_SCORED, index=False)

    selected = select_and_save(scored, preds, sample)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(selected["file"].tolist(), sample)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scan, scored, selected, integ)

    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "quick_lejepa_health",
        "sigreg_rank_score",
        "energy_delta_vs_base",
        "blend_profile",
        "beta",
        "row_gate",
        "base_file",
        "donor_file",
    ]
    print(
        f"train_files={len(train_files)} bases={len(bases)} donors={len(donors)} "
        f"generated={len(scan)} rescored={len(scored)} saved={len(selected)}"
    )
    print(selected[cols].head(45).round(10).to_string(index=False))
    print(integ.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
