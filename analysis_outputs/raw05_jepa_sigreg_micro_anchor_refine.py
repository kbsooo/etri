from __future__ import annotations

from pathlib import Path
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
    training_pool_files,
)
from raw05_jepa_q3stress_counterweight_local_refine import profile_vector, unique_existing  # noqa: E402
from raw05_jepa_sigreg_gated_microrefine import (  # noqa: E402
    add_candidate,
    axis_scale,
    gated_logit,
    load_arrays,
    quick_health,
)


OUT_SCAN = OUT / "raw05_jepa_sigreg_micro_anchor_refine_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_sigreg_micro_anchor_refine_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_sigreg_micro_anchor_refine_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_sigreg_micro_anchor_refine_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_sigreg_micro_anchor_refine_report.md"

MICRO_BETAS = [0.08, 0.14, 0.22, 0.32]
RECOVERY_BETAS = [0.28, 0.44, 0.62, 0.80]
GATE_SPECS = [
    ("anchor_bad_f015", 0.15, 0.80, 0.15, 0.85, "bad_sig_min"),
    ("anchor_energy_f020", 0.20, 0.85, 0.20, 0.85, "bad_sig_energy_min"),
    ("anchor_balance_f015", 0.15, 0.80, 0.15, 0.80, "sig_balance"),
]


def read_optional(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def top_files(frame: pd.DataFrame, sort_cols: list[str], n: int, mask: pd.Series | None = None) -> list[str]:
    if frame.empty or "file" not in frame.columns:
        return []
    part = frame[mask] if mask is not None else frame
    if part.empty:
        return []
    cols = [col for col in sort_cols if col in part.columns]
    if not cols:
        return part["file"].astype(str).head(n).tolist()
    return part.sort_values(cols)["file"].astype(str).head(n).tolist()


def cap(files: list[str], n: int) -> list[str]:
    return unique_existing(files)[:n]


def candidate_pools() -> tuple[list[str], list[str], list[str], list[str]]:
    priority = read_optional("final_jepa_candidate_priority_20260527.csv")
    sigreg = read_optional("lejepa_sigreg_candidate_audit.csv")
    micro = read_optional("raw05_jepa_energyfront_microrefine_shortlist.csv")
    efgate = read_optional("raw05_jepa_efmicro_gate_refine_shortlist.csv")
    efback = read_optional("raw05_jepa_efgate_backoff_frontier_shortlist.csv")
    siggate = read_optional("raw05_jepa_sigreg_gated_microrefine_shortlist.csv")
    energy = read_optional("raw05_jepa_energy_constrained_frontier_shortlist.csv")

    micro_mask = sigreg["family"].eq("raw05_jepa_efmicro") if "family" in sigreg.columns else None
    siggate_mask = sigreg["family"].eq("raw05_jepa_siggate") if "family" in sigreg.columns else None

    micro_bases: list[str] = []
    micro_bases.extend(priority["file"].astype(str).head(7).tolist() if not priority.empty else [])
    micro_bases.extend(top_files(sigreg, ["lejepa_combined_rank", "actual_anchor_score_final"], 14, micro_mask))
    micro_bases.extend(top_files(micro, ["actual_anchor_score_final"], 12))
    micro_bases.extend(top_files(micro, ["bad_residual_axis_ratio", "actual_anchor_score_final"], 10))
    micro_bases.extend(top_files(energy, ["actual_anchor_score_final"], 5))

    micro_donors: list[str] = []
    micro_donors.extend(top_files(sigreg, ["lejepa_combined_rank", "actual_anchor_score_final"], 18, micro_mask))
    micro_donors.extend(top_files(micro, ["actual_anchor_score_final"], 14))
    micro_donors.extend(top_files(micro, ["bad_residual_axis_ratio", "actual_anchor_score_final"], 12))
    micro_donors.extend(top_files(energy, ["actual_anchor_score_final"], 6))

    lowbad_donors: list[str] = []
    lowbad_donors.extend(top_files(sigreg, ["bad_residual_axis_ratio", "lejepa_residual_health"], 14, siggate_mask))
    lowbad_donors.extend(top_files(sigreg, ["lejepa_combined_rank", "actual_anchor_score_final"], 12, siggate_mask))
    lowbad_donors.extend(top_files(siggate, ["sigreg_rank_score", "actual_anchor_score_final"], 16))
    lowbad_donors.extend(top_files(siggate, ["bad_residual_axis_ratio", "quick_lejepa_health"], 16))
    lowbad_donors.extend(top_files(efgate, ["bad_residual_axis_ratio", "actual_anchor_score_final"], 12))
    lowbad_donors.extend(top_files(efback, ["bad_residual_axis_ratio", "actual_anchor_score_final"], 12))
    lowbad_donors.extend(top_files(efgate, ["actual_anchor_score_final", "bad_residual_axis_ratio"], 8))
    lowbad_donors.extend(top_files(efback, ["actual_anchor_score_final", "bad_residual_axis_ratio"], 8))

    lowbad_bases = lowbad_donors.copy()

    return (
        cap(micro_bases, 16),
        cap(lowbad_donors, 22),
        cap(lowbad_bases, 16),
        cap(micro_donors, 18),
    )


def blend_profiles() -> list[tuple[str, np.ndarray]]:
    return [
        ("context_only", profile_vector(Q1=1.0, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("q1light", profile_vector(Q1=0.42, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("q2s1heavy", profile_vector(Q1=0.70, Q2=1.22, S1=1.22, S2=0.82, S3=0.82)),
        ("target_tiny", profile_vector(Q1=0.72, Q2=0.90, Q3=0.05, S1=0.90, S2=0.88, S3=0.88, S4=0.05)),
    ]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def generate_direction(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    direction: str,
    bases: list[str],
    donors: list[str],
    betas: list[float],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    model: dict[str, np.ndarray | float],
    axes: dict[str, np.ndarray | float],
    axis_scale_value: np.ndarray,
) -> None:
    raw_logit = logit(raw)
    logits = {file_name: logit(arrays[file_name]) for file_name in set(bases + donors) if file_name in arrays}
    energy_cache = {file_name: energy_rows(logits[file_name] - raw_logit, model) for file_name in logits}

    for base_file in bases:
        if base_file not in logits:
            continue
        base_logit = logits[base_file]
        base_energy = energy_cache[base_file]
        for donor_file in donors:
            if donor_file == base_file or donor_file not in logits:
                continue
            donor_logit = logits[donor_file]
            donor_energy = energy_cache[donor_file]
            step0 = donor_logit - base_logit
            for profile_name, profile_gate in blend_profiles():
                step = step0 * profile_gate
                if np.abs(step).mean() <= 1e-10:
                    continue
                for beta in betas:
                    prop_logit = base_logit + beta * step
                    for gate_name, bad_floor, bad_scale, sig_floor, sig_scale, kind in GATE_SPECS:
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
                        pred_hash = prediction_hash(pred)
                        if pred_hash in seen:
                            continue
                        seen.add(pred_hash)
                        final_energy = energy_rows(final_logit - raw_logit, model)
                        label = (
                            f"{direction}|{base_file}|donor={donor_file}|profile={profile_name}|"
                            f"b={beta:.3f}|siganchor={gate_name}"
                        )
                        meta = {
                            "direction": direction,
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
                        row = {"label": label, "prediction_hash": pred_hash}
                        row.update(meta)
                        row.update(public_axis_features(pred, axes))
                        rows.append(row)
                        preds.append(pred)


def generate_candidates(
    micro_bases: list[str],
    lowbad_donors: list[str],
    lowbad_bases: list[str],
    micro_donors: list[str],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    model: dict[str, np.ndarray | float],
    axes: dict[str, np.ndarray | float],
) -> tuple[list[dict[str, object]], list[np.ndarray]]:
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()
    scale_bases = unique_existing([*micro_bases, *lowbad_bases, *micro_donors])
    axis_scale_value = axis_scale(raw, scale_bases, arrays, axes)

    generate_direction(
        rows,
        preds,
        seen,
        "micro_to_lowbad",
        micro_bases,
        lowbad_donors,
        MICRO_BETAS,
        arrays,
        raw,
        model,
        axes,
        axis_scale_value,
    )
    generate_direction(
        rows,
        preds,
        seen,
        "lowbad_to_micro",
        lowbad_bases,
        micro_donors,
        RECOVERY_BETAS,
        arrays,
        raw,
        model,
        axes,
        axis_scale_value,
    )
    return rows, preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["bad_abs"] = frame["bad_residual_axis_ratio"].abs()
    frame["proxy_health_penalty"] = (
        np.maximum(frame["public_norm_delta_mean"], 0.0) * 0.000008
        + np.maximum(frame["row_aniso_delta_mean"], 0.0) * 0.000005
        + np.maximum(frame["energy_delta_vs_base"], 0.0) * 0.00018
    )
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 260.0
        + np.maximum(frame["bad_abs"] - 0.00055, 0.0) * 0.080
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.00155, 0.0) * 0.030
        + frame["proxy_health_penalty"]
    )

    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.05e-7)
            & (frame["bad_abs"] <= 0.00055)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.576925)
            & (frame["public_norm_delta_mean"] <= 0.025),
            ["prefilter_score"],
            1000,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_abs"] <= 0.00072)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.576925),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["bad_abs"] <= 0.00032)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.15e-7)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["bad_abs", "prefilter_score"],
            850,
        ),
        (
            (frame["energy_delta_vs_base"] <= 0.0)
            & (frame["public_norm_delta_mean"] <= 0.0)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_abs"] <= 0.00075),
            ["prefilter_score"],
            750,
        ),
        (
            (frame["direction"].eq("lowbad_to_micro"))
            & (frame["bad_abs"] <= 0.00042)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.15e-7),
            ["prefilter_score"],
            750,
        ),
    ]
    parts = [frame[mask].sort_values(sort_cols).head(limit) for mask, sort_cols, limit in specs]
    parts.append(frame.sort_values("prefilter_score").head(1200))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(3600)


def score_candidates(
    selected_for_scoring: pd.DataFrame,
    preds: list[np.ndarray],
    sample: pd.DataFrame,
    raw: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> pd.DataFrame:
    indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["bad_abs"] = scored["bad_residual_axis_ratio"].abs()
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 265.0
        + np.maximum(scored["bad_abs"] - 0.00052, 0.0) * 0.085
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.75
        + np.maximum(scored["energy_delta_vs_base"], 0.0) * 0.00018
        + np.maximum(scored["public_norm_delta_mean"], 0.0) * 0.000004
    )

    health_pool = pd.concat(
        [
            scored.sort_values("selection_score").head(900),
            scored.sort_values("actual_anchor_score_final").head(850),
            scored.sort_values(["bad_abs", "actual_anchor_score_final"]).head(700),
            scored[scored["posterior_expected_public_vs_anchor"] <= 0.576895]
            .sort_values("actual_anchor_score_final")
            .head(550),
            scored[scored["direction"].eq("lowbad_to_micro")].sort_values("selection_score").head(550),
        ],
        ignore_index=False,
    ).drop_duplicates("prediction_hash")
    health_pool = health_pool.sort_values(["selection_score", "actual_anchor_score_final"]).head(1900).reset_index(drop=True)

    rng = np.random.default_rng(2026052703)
    raw_logit = logit(raw)
    health_rows = [quick_health(preds[int(row["candidate_index"])], raw, raw_logit, axes, rng) for _, row in health_pool.iterrows()]
    health = pd.DataFrame(health_rows)
    health_pool = pd.concat([health_pool, health], axis=1)
    health_pool["actual_rank"] = health_pool["actual_anchor_score_final"].rank(method="min")
    health_pool["health_rank"] = health_pool["quick_lejepa_health"].rank(method="min")
    health_pool["bad_abs_rank"] = health_pool["bad_abs"].rank(method="min")
    health_pool["posterior_rank"] = health_pool["posterior_expected_public_vs_anchor"].rank(method="min")
    health_pool["anchor_rank_score"] = (
        0.52 * health_pool["actual_rank"]
        + 0.20 * health_pool["health_rank"]
        + 0.18 * health_pool["bad_abs_rank"]
        + 0.10 * health_pool["posterior_rank"]
    )
    health_pool["anchor_selection_score"] = (
        health_pool["selection_score"]
        + np.maximum(health_pool["quick_lejepa_health"] - 10.30, 0.0) * 0.00000016
    )
    return health_pool.sort_values(["anchor_rank_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "siganchor_balanced",
            (scored["actual_anchor_score_final"] <= 0.57783935)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.05e-7)
            & (scored["bad_abs"] <= 0.00058)
            & (scored["quick_lejepa_health"] <= 10.60),
            ["anchor_rank_score", "actual_anchor_score_final"],
            18,
        ),
        (
            "siganchor_lowbad",
            (scored["actual_anchor_score_final"] <= 0.57783985)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.10e-7)
            & (scored["bad_abs"] <= 0.00032),
            ["bad_abs", "actual_anchor_score_final"],
            18,
        ),
        (
            "siganchor_health",
            (scored["actual_anchor_score_final"] <= 0.57783985)
            & (scored["quick_lejepa_health"] <= 9.90)
            & (scored["bad_abs"] <= 0.00062),
            ["quick_lejepa_health", "actual_anchor_score_final"],
            16,
        ),
        (
            "siganchor_posterior",
            (scored["actual_anchor_score_final"] <= 0.57783995)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.576895)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.15e-7)
            & (scored["bad_abs"] <= 0.00058),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            16,
        ),
        (
            "siganchor_recovered_lowbad",
            (scored["direction"].eq("lowbad_to_micro"))
            & (scored["actual_anchor_score_final"] <= 0.57783995)
            & (scored["bad_abs"] <= 0.00036)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.15e-7),
            ["actual_anchor_score_final", "bad_abs"],
            16,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    parts.append(scored.sort_values(["anchor_rank_score", "actual_anchor_score_final"]).head(24).assign(bucket="siganchor_rank_fallback"))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["anchor_rank_score", "actual_anchor_score_final"]).head(72).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_siganchor_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scan: pd.DataFrame, scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "direction",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "quick_lejepa_health",
        "anchor_rank_score",
        "energy_delta_vs_base",
        "public_norm_delta_mean",
        "row_aniso_delta_mean",
        "blend_profile",
        "beta",
        "row_gate",
        "gate_mean",
        "base_file",
        "donor_file",
    ]
    by_direction = (
        scored.sort_values("anchor_rank_score")
        .groupby(["direction", "blend_profile", "row_gate"], as_index=False)
        .head(1)
        .sort_values("anchor_rank_score")
    )
    lines = [
        "# Raw05 JEPA SIGReg Micro Anchor Refine",
        "",
        "This pass keeps the LeJEPA/SIGReg gate but restricts the search around efmicro/energyfront actual anchors.",
        "It tests whether low-bad siggate moves can be pulled back toward efmicro without losing the residual-health benefit.",
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
        selected[cols].head(72).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best By Direction / Blend / Gate",
        "",
        "```csv",
        by_direction[
            [
                "direction",
                "blend_profile",
                "row_gate",
                "beta",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "bad_residual_axis_ratio",
                "quick_lejepa_health",
                "anchor_rank_score",
                "base_file",
                "donor_file",
            ]
        ]
        .head(72)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(72).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    micro_bases, lowbad_donors, lowbad_bases, micro_donors = candidate_pools()
    train_files = training_pool_files()
    files = unique_existing([RAW05_FILE, *micro_bases, *lowbad_donors, *lowbad_bases, *micro_donors, *train_files])
    arrays = load_arrays(files, sample)
    axes = public_axes()
    model = fit_context_target_energy({name: arrays[name] for name in train_files if name in arrays}, raw)

    rows, preds = generate_candidates(micro_bases, lowbad_donors, lowbad_bases, micro_donors, arrays, raw, model, axes)
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
        "direction",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "quick_lejepa_health",
        "anchor_rank_score",
        "energy_delta_vs_base",
        "blend_profile",
        "beta",
        "row_gate",
        "base_file",
        "donor_file",
    ]
    print(
        f"train_files={len(train_files)} micro_bases={len(micro_bases)} lowbad_donors={len(lowbad_donors)} "
        f"lowbad_bases={len(lowbad_bases)} micro_donors={len(micro_donors)} generated={len(scan)} "
        f"rescored={len(scored)} saved={len(selected)}"
    )
    print(selected[cols].head(50).round(10).to_string(index=False))
    print(integ.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
