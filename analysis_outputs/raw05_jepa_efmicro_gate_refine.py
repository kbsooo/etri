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
from raw05_jepa_q3stress_counterweight_local_refine import profile_vector, unique_existing  # noqa: E402


OUT_SCAN = OUT / "raw05_jepa_efmicro_gate_refine_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_efmicro_gate_refine_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_efmicro_gate_refine_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_efmicro_gate_refine_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_efmicro_gate_refine_report.md"

BETAS = [0.40, 0.44, 0.46, 0.48, 0.50, 0.52, 0.56]
BAD_GATE_SPECS = [
    ("none", 1.00, 1.00, "none"),
    ("bad_f005_s075", 0.05, 0.75, "soft"),
    ("bad_f010_s075", 0.10, 0.75, "soft"),
    ("bad_f020_s100", 0.20, 1.00, "soft"),
    ("bad_hard_f010", 0.10, 1.00, "hard"),
    ("energy_soft_floor", 0.20, 1.00, "energy"),
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


def extract_targetw_from_labels(frame: pd.DataFrame, limit: int = 20) -> list[str]:
    out: list[str] = []
    pattern = re.compile(r"donor=(submission_raw05_jepa_targetw_[0-9a-f]+\.csv)")
    for text in frame.get("label", pd.Series(dtype=str)).astype(str).head(limit * 4):
        match = pattern.search(text)
        if match:
            out.append(match.group(1))
    return out[:limit]


def candidate_pools() -> tuple[list[str], list[str]]:
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    micro = pd.read_csv(OUT / "raw05_jepa_energyfront_microrefine_shortlist.csv")
    energy = pd.read_csv(OUT / "raw05_jepa_energy_constrained_frontier_shortlist.csv")
    targetw = pd.read_csv(OUT / "raw05_jepa_target_weight_optimizer_shortlist.csv")
    ctx = pd.read_csv(OUT / "raw05_jepa_context_target_energy_gate_shortlist.csv")

    bases: list[str] = []
    bases.extend(priority["file"].astype(str).head(6).tolist())
    bases.extend(micro.sort_values("actual_anchor_score_final")["file"].astype(str).head(8).tolist())
    bases.extend(micro.sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"].astype(str).head(6).tolist())
    bases.extend(energy.sort_values("actual_anchor_score_final")["file"].astype(str).head(6).tolist())

    donors: list[str] = []
    donors.extend(extract_targetw_from_labels(micro.sort_values("actual_anchor_score_final"), 5))
    donors.extend(extract_targetw_from_labels(micro.sort_values("bad_residual_axis_ratio"), 5))
    donors.extend(
        targetw[targetw["bucket"].isin(["low_bad", "strict_raw", "actual_probe", "raw_boundary"])]
        .sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"]
        .astype(str)
        .head(6)
        .tolist()
    )
    donors.extend(energy.sort_values("actual_anchor_score_final")["file"].astype(str).head(6).tolist())
    donors.extend(energy.sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"].astype(str).head(6).tolist())
    donors.extend(ctx.sort_values(["energy_delta_vs_base", "actual_anchor_score_final"])["file"].astype(str).head(4).tolist())
    donors.append(RAW05_FILE)

    return unique_existing(bases), unique_existing(donors)


def blend_profiles() -> list[tuple[str, np.ndarray]]:
    return [
        ("context_only", profile_vector(Q1=1.0, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("q1light", profile_vector(Q1=0.45, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("q2s1heavy", profile_vector(Q1=0.80, Q2=1.18, S1=1.18, S2=0.86, S3=0.86)),
    ]


def bad_gate_values(
    base_pred: np.ndarray,
    prop_pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
    floor: float,
    scale_mult: float,
    kind: str,
) -> np.ndarray:
    stage2 = np.asarray(axes["stage2"], dtype=np.float64)
    bad_axis = np.asarray(axes["bad_axis"], dtype=np.float64)
    base_contrib = ((base_pred - stage2) * bad_axis).sum(axis=1)
    prop_contrib = ((prop_pred - stage2) * bad_axis).sum(axis=1)
    diff = base_contrib - prop_contrib
    if kind == "hard":
        return np.where(diff > 0.0, 1.0, floor).astype(np.float64)
    scale = max(float(np.median(np.abs(diff))) * scale_mult, 1e-7)
    soft = 1.0 / (1.0 + np.exp(-np.clip(diff / scale, -40.0, 40.0)))
    return floor + (1.0 - floor) * soft


def gated_logit(
    gate_name: str,
    floor: float,
    scale_mult: float,
    kind: str,
    base_logit: np.ndarray,
    prop_logit: np.ndarray,
    raw_logit: np.ndarray,
    model: dict[str, np.ndarray | float],
    axes: dict[str, np.ndarray | float],
) -> tuple[np.ndarray, float, float]:
    if kind == "none":
        gate = np.ones(base_logit.shape[0], dtype=np.float64)
    elif kind == "energy":
        e_base = energy_rows(base_logit - raw_logit, model)
        e_prop = energy_rows(prop_logit - raw_logit, model)
        gate = row_gate(e_base, e_prop, "soft_floor")
    else:
        gate = bad_gate_values(sigmoid(base_logit), sigmoid(prop_logit), axes, floor, scale_mult, kind)
    final_logit = base_logit + (prop_logit - base_logit) * gate.reshape(-1, 1)
    return final_logit, float(gate.mean()), float(np.quantile(gate, 0.10))


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
                    for gate_name, floor, scale_mult, kind in BAD_GATE_SPECS:
                        final_logit, gate_mean, gate_p10 = gated_logit(
                            gate_name, floor, scale_mult, kind, base_logit, prop_logit, raw_logit, model, axes
                        )
                        pred = sigmoid(final_logit)
                        final_energy = energy_rows(final_logit - raw_logit, model)
                        label = (
                            f"{base_file}|donor={donor_file}|profile={profile_name}|b={beta:.3f}|"
                            f"gate={gate_name}"
                        )
                        meta = {
                            "base_file": base_file,
                            "donor_file": donor_file,
                            "blend_profile": profile_name,
                            "beta": float(beta),
                            "row_gate": gate_name,
                            "gate_floor": float(floor),
                            "gate_scale_mult": float(scale_mult),
                            "gate_mean": gate_mean,
                            "gate_p10": gate_p10,
                            "base_energy_mean": float(base_energy.mean()),
                            "donor_energy_mean": float(donor_energy.mean()),
                            "final_energy_mean": float(final_energy.mean()),
                            "energy_delta_vs_base": float(final_energy.mean() - base_energy.mean()),
                            "energy_delta_vs_donor": float(final_energy.mean() - donor_energy.mean()),
                            "energy_improve_rate_vs_base": float((final_energy < base_energy).mean()),
                        }
                        add_candidate(rows, preds, seen, label, pred, axes, meta)
    return rows, preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 280.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.00075, 0.0) * 0.090
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.00155, 0.0) * 0.040
        + np.maximum(frame["energy_delta_vs_base"], 0.0) * 0.00025
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00075)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["actual_proxy_prefilter" if False else "prefilter_score"],
            900,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 9.0e-8)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00085)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["bad_residual_axis_ratio"].abs() <= 0.00050)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["bad_residual_axis_ratio", "prefilter_score"],
            700,
        ),
        (
            (frame["energy_delta_vs_base"] <= 0.0)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00090)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
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
    return selected.sort_values("prefilter_score").head(3600)


def score_candidates(selected_for_scoring: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 250.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00075, 0.0) * 0.080
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.70
        + np.maximum(scored["energy_delta_vs_base"], 0.0) * 0.00022
    )
    scored["lowbad_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00045, 0.0) * 0.085
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57692, 0.0) * 0.70
    )
    scored["guardrail_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 8.0e-8, 0.0) * 275.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00080, 0.0) * 0.070
        + np.maximum(scored["energy_delta_vs_base"], 0.0) * 0.00045
    )
    return scored.sort_values(["selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "gate_actual",
            (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00075)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["actual_anchor_score_final", "selection_score"],
            26,
        ),
        (
            "gate_raw_tight",
            (scored["delta_vs_raw05_rawaxis"] <= 8.0e-8)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00085)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["actual_anchor_score_final", "guardrail_score"],
            22,
        ),
        (
            "gate_lowest_bad",
            (scored["bad_residual_axis_ratio"].abs() <= 0.00050)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["lowbad_score", "actual_anchor_score_final"],
            20,
        ),
        (
            "gate_energy_improved",
            (scored["energy_delta_vs_base"] <= 0.0)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00090),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            18,
        ),
        (
            "gate_posterior_safe",
            (scored["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00090),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            18,
        ),
        (
            "gate_strict_raw",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00090)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            16,
        ),
    ]
    parts = []
    for bucket, mask, sort_cols, limit in specs:
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["selection_score", "actual_anchor_score_final"]).copy()

    files = []
    for _, row in selected.iterrows():
        pred = preds[int(row["candidate_index"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_efgate_{tag}.csv"
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
        "mean_abs_move_vs_raw05",
        "energy_delta_vs_base",
        "blend_profile",
        "beta",
        "row_gate",
        "gate_mean",
        "gate_p10",
        "base_file",
        "donor_file",
    ]
    best_by_gate = (
        scored.sort_values("actual_anchor_score_final")
        .groupby(["blend_profile", "row_gate", "beta"], as_index=False)
        .head(1)
        .sort_values("actual_anchor_score_final")
    )
    lines = [
        "# Raw05 JEPA EFMicro Gate Refine",
        "",
        "This pass refines the second-stage bad-axis row gate around the energyfront/micro frontier.",
        "It varies bad-gate floor/scale and beta to test whether the low-bad micro structure can recover the actual-anchor frontier.",
        "",
        "## Counts",
        "",
        f"- generated candidates: {len(scan)}",
        f"- actual-anchor rescored candidates: {len(scored)}",
        f"- saved candidates: {len(selected)}",
        "",
        "## Top Saved",
        "",
        "```csv",
        selected[cols].head(70).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best By Blend / Gate / Beta",
        "",
        "```csv",
        best_by_gate[
            [
                "blend_profile",
                "row_gate",
                "beta",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "energy_delta_vs_base",
                "gate_mean",
                "gate_p10",
                "base_file",
                "donor_file",
            ]
        ]
        .head(70)
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(70).round(10).to_csv(index=False).strip(),
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
    scored = score_candidates(selected_for_scoring, preds, sample)
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
        "energy_delta_vs_base",
        "blend_profile",
        "beta",
        "row_gate",
        "gate_mean",
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
