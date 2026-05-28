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
    row_gate,
    training_pool_files,
)
from raw05_jepa_efmicro_gate_refine import bad_gate_values  # noqa: E402
from raw05_jepa_q3stress_counterweight_local_refine import unique_existing  # noqa: E402


OUT_SCAN = OUT / "raw05_jepa_efgate_backoff_frontier_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_efgate_backoff_frontier_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_efgate_backoff_frontier_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_efgate_backoff_frontier_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_efgate_backoff_frontier_report.md"

LAMBDAS = [-0.08, -0.04, 0.025, 0.05, 0.075, 0.10, 0.14, 0.18, 0.24, 0.32, 0.45, 0.60]
GATE_SPECS = [
    ("none", 1.00, 1.00, "none"),
    ("bad_f005_s075", 0.05, 0.75, "soft"),
    ("bad_f010_s075", 0.10, 0.75, "soft"),
    ("bad_f020_s100", 0.20, 1.00, "soft"),
    ("bad_hard_f010", 0.10, 1.00, "hard"),
    ("energy_soft_floor", 0.20, 1.00, "energy"),
]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def profile(name: str) -> np.ndarray:
    weights = {
        "all": {target: 1.0 for target in TARGETS},
        "context_only": {"Q1": 1.0, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0},
        "q1light": {"Q1": 0.45, "Q2": 1.0, "S1": 1.0, "S2": 1.0, "S3": 1.0},
        "q2s1heavy": {"Q1": 0.80, "Q2": 1.18, "S1": 1.18, "S2": 0.86, "S3": 0.86},
        "context_q3s4tiny": {
            "Q1": 1.0,
            "Q2": 1.0,
            "Q3": 0.16,
            "S1": 1.0,
            "S2": 1.0,
            "S3": 1.0,
            "S4": 0.16,
        },
    }[name]
    return np.asarray([weights.get(target, 0.0) for target in TARGETS], dtype=np.float64).reshape(1, -1)


def candidate_pools() -> tuple[list[str], list[str]]:
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    efgate = pd.read_csv(OUT / "raw05_jepa_efmicro_gate_refine_shortlist.csv")
    efmicro = pd.read_csv(OUT / "raw05_jepa_energyfront_microrefine_shortlist.csv")
    energyfront = pd.read_csv(OUT / "raw05_jepa_energy_constrained_frontier_shortlist.csv")

    bases: list[str] = []
    bases.extend(priority["file"].astype(str).head(10).tolist())
    bases.extend(efmicro.sort_values("actual_anchor_score_final")["file"].astype(str).head(5).tolist())
    bases.extend(energyfront.sort_values("actual_anchor_score_final")["file"].astype(str).head(5).tolist())

    donors: list[str] = []
    donors.extend(efgate.sort_values("actual_anchor_score_final")["file"].astype(str).head(8).tolist())
    donors.extend(efgate.sort_values("bad_residual_axis_ratio")["file"].astype(str).head(8).tolist())
    donors.extend(efgate.sort_values("posterior_expected_public_vs_anchor")["file"].astype(str).head(6).tolist())
    donors.append(RAW05_FILE)

    return unique_existing(bases), unique_existing(donors)


def load_arrays(files: list[str], sample: pd.DataFrame) -> dict[str, np.ndarray]:
    ref_key = sample[KEY].reset_index(drop=True)
    arrays: dict[str, np.ndarray] = {}
    for file_name in files:
        frame = read_submission(file_name)
        if not frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"key mismatch: {file_name}")
        arrays[file_name] = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    return arrays


def gated_backoff(
    base_logit: np.ndarray,
    prop_logit: np.ndarray,
    raw_logit: np.ndarray,
    model: dict[str, np.ndarray | float],
    axes: dict[str, np.ndarray | float],
    gate_name: str,
    floor: float,
    scale_mult: float,
    kind: str,
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
            base_to_donor = donor_logit - base_logit
            if np.abs(base_to_donor).mean() <= 1e-10:
                continue
            for profile_name in ["all", "context_only", "q1light", "q2s1heavy", "context_q3s4tiny"]:
                step = base_to_donor * profile(profile_name)
                if np.abs(step).mean() <= 1e-10:
                    continue
                for lam in LAMBDAS:
                    prop_logit = base_logit + lam * step
                    for gate_name, floor, scale_mult, kind in GATE_SPECS:
                        final_logit, gate_mean, gate_p10 = gated_backoff(
                            base_logit, prop_logit, raw_logit, model, axes, gate_name, floor, scale_mult, kind
                        )
                        pred = sigmoid(final_logit)
                        final_energy = energy_rows(final_logit - raw_logit, model)
                        label = (
                            f"{base_file}|toward={donor_file}|profile={profile_name}|lam={lam:.3f}|"
                            f"gate={gate_name}"
                        )
                        meta = {
                            "base_file": base_file,
                            "donor_file": donor_file,
                            "blend_profile": profile_name,
                            "lambda": float(lam),
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
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 300.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.00060, 0.0) * 0.10
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.00155, 0.0) * 0.04
        + np.maximum(frame["energy_delta_vs_base"], 0.0) * 0.00022
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00070)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 9.0e-8)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00070)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["bad_residual_axis_ratio"].abs() <= 0.00025)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["bad_residual_axis_ratio", "prefilter_score"],
            700,
        ),
        (
            (frame["energy_delta_vs_base"] <= 0.0)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00080),
            ["prefilter_score"],
            700,
        ),
        (
            (frame["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00080),
            ["posterior_expected_public_vs_anchor", "prefilter_score"],
            700,
        ),
    ]
    parts = [frame[mask].sort_values(sort_cols).head(limit) for mask, sort_cols, limit in specs]
    parts.append(frame.sort_values("prefilter_score").head(1000))
    return pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash").sort_values("prefilter_score").head(3600)


def score_candidates(selected: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected.index.to_numpy(dtype=int)
    actual = actual_anchor_score([preds[i] for i in indices], sample).drop(columns=["candidate_index"])
    scored = selected.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 280.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00055, 0.0) * 0.085
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.70
        + np.maximum(scored["energy_delta_vs_base"], 0.0) * 0.00022
    )
    scored["lowbad_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00020, 0.0) * 0.080
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.70
    )
    scored["rawtight_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 8.0e-8, 0.0) * 300.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00065, 0.0) * 0.08
    )
    return scored.sort_values(["selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "backoff_actual",
            (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00070)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["actual_anchor_score_final", "selection_score"],
            18,
        ),
        (
            "backoff_risk_none",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00060)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57690),
            ["actual_anchor_score_final", "bad_residual_axis_ratio"],
            18,
        ),
        (
            "backoff_ultralow_bad",
            (scored["bad_residual_axis_ratio"].abs() <= 0.00012)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["lowbad_score", "actual_anchor_score_final"],
            18,
        ),
        (
            "backoff_raw_tight",
            (scored["delta_vs_raw05_rawaxis"] <= 8.0e-8)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00070)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["actual_anchor_score_final", "rawtight_score"],
            18,
        ),
        (
            "backoff_energy_improved",
            (scored["energy_delta_vs_base"] <= 0.0)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00080),
            ["actual_anchor_score_final", "selection_score"],
            18,
        ),
        (
            "backoff_posterior_floor",
            (scored["posterior_expected_public_vs_anchor"] <= 0.57689)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00080),
            ["actual_anchor_score_final", "posterior_expected_public_vs_anchor"],
            18,
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
        file_name = f"submission_raw05_jepa_efback_{tag}.csv"
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
        "lambda",
        "row_gate",
        "gate_mean",
        "gate_p10",
        "base_file",
        "donor_file",
    ]
    lines = [
        "# Raw05 JEPA EFGate Backoff Frontier",
        "",
        "This pass interpolates from the actual-anchor frontier toward efgate low-bad candidates.",
        "It tests whether a small JEPA row-gate backoff can keep the frontier while inheriting lower posterior/bad-axis exposure.",
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
        "## Best Scored By Actual",
        "",
        "```csv",
        scored.sort_values("actual_anchor_score_final")[cols[2:]].head(70).round(10).to_csv(index=False).strip(),
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
        "lambda",
        "row_gate",
        "gate_mean",
        "base_file",
        "donor_file",
    ]
    print(
        f"train_files={len(train_files)} bases={len(bases)} donors={len(donors)} "
        f"generated={len(scan)} rescored={len(scored)} saved={len(selected)}"
    )
    print(selected[cols].head(50).round(10).to_string(index=False))
    print(integ.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
