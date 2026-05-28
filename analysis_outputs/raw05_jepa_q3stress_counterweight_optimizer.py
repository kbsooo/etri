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


OUT_SCAN = OUT / "raw05_jepa_q3stress_counterweight_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_q3stress_counterweight_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_q3stress_counterweight_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_q3stress_counterweight_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_q3stress_counterweight_report.md"

TARGET_INDEX = {target: i for i, target in enumerate(TARGETS)}

TARGET_MASKS = {
    "q2_only": ["Q2"],
    "s1_only": ["S1"],
    "q2_s1": ["Q2", "S1"],
    "q2_s1_s4": ["Q2", "S1", "S4"],
    "q1_q2_s1": ["Q1", "Q2", "S1"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "non_q3_s4": ["Q1", "Q2", "S1", "S2", "S3"],
    "non_q3": ["Q1", "Q2", "S1", "S2", "S3", "S4"],
    "all": TARGETS,
}

ALPHAS = [0.04, 0.07, 0.10, 0.14, 0.20, 0.28, 0.38, 0.52]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def target_mask(name: str) -> np.ndarray:
    allowed = set(TARGET_MASKS[name])
    return np.asarray([target in allowed for target in TARGETS], dtype=np.float64).reshape(1, -1)


def file_exists(file_name: str) -> bool:
    try:
        read_submission(file_name)
    except FileNotFoundError:
        return False
    return True


def unique_existing(files: list[str]) -> list[str]:
    keep: list[str] = []
    seen: set[str] = set()
    for file_name in files:
        if file_name in seen:
            continue
        if not file_exists(file_name):
            continue
        seen.add(file_name)
        keep.append(file_name)
    return keep


def choose_base_and_counter_files() -> tuple[list[str], list[str]]:
    targetw = pd.read_csv(OUT / "raw05_jepa_target_weight_optimizer_shortlist.csv")
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")

    bases: list[str] = []
    bases.extend(
        targetw[targetw["bucket"].eq("actual_probe")]
        .sort_values("actual_anchor_score_final")["file"]
        .astype(str)
        .head(16)
        .tolist()
    )
    bases.extend(
        targetw[targetw["bucket"].eq("raw_boundary")]
        .sort_values("actual_anchor_score_final")["file"]
        .astype(str)
        .head(14)
        .tolist()
    )
    bases.extend(
        targetw[targetw["template"].str.startswith("q2s1q3_refine2")]
        .sort_values("actual_anchor_score_final")["file"]
        .astype(str)
        .head(8)
        .tolist()
    )

    counters: list[str] = [RAW05_FILE]
    counters.extend(
        targetw[targetw["bucket"].eq("low_bad")]
        .sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"]
        .astype(str)
        .head(18)
        .tolist()
    )
    counters.extend(
        targetw[targetw["bucket"].eq("strict_raw")]
        .sort_values(["delta_vs_raw05_rawaxis", "bad_residual_axis_ratio"])["file"]
        .astype(str)
        .head(12)
        .tolist()
    )
    counters.extend(
        targetw[
            targetw["bucket"].eq("balanced")
            & (targetw["bad_residual_axis_ratio"].abs() <= 0.0018)
            & (targetw["delta_vs_raw05_rawaxis"] <= 1.0e-7)
        ]
        .sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"]
        .astype(str)
        .head(12)
        .tolist()
    )
    counters.extend(priority["file"].astype(str).head(10).tolist())

    return unique_existing(bases), unique_existing(counters)


def load_arrays(files: list[str], sample: pd.DataFrame) -> dict[str, np.ndarray]:
    ref_key = sample[KEY].reset_index(drop=True)
    arrays: dict[str, np.ndarray] = {}
    for file_name in files:
        frame = read_submission(file_name)
        if not frame[KEY].reset_index(drop=True).equals(ref_key):
            raise ValueError(f"key mismatch: {file_name}")
        arrays[file_name] = clip(frame[TARGETS].to_numpy(dtype=np.float64))
    return arrays


def cell_gate(name: str, base_delta: np.ndarray, counter_delta: np.ndarray) -> np.ndarray:
    if name == "all":
        return np.ones_like(base_delta, dtype=np.float64)
    closer = np.abs(counter_delta) < np.abs(base_delta)
    opposing = np.sign(counter_delta) != np.sign(base_delta)
    nonzero = (np.abs(counter_delta) > 1e-10) & (np.abs(base_delta) > 1e-10)
    if name == "closer":
        return closer.astype(np.float64)
    if name == "opposing":
        return (opposing & nonzero).astype(np.float64)
    if name == "closer_or_opposing":
        return ((closer | opposing) & nonzero).astype(np.float64)
    raise ValueError(name)


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    label: str,
    base_file: str,
    counter_file: str,
    target_mask_name: str,
    cell_gate_name: str,
    alpha: float,
    pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
    active_gate_mean: float,
) -> None:
    pred = clip(pred)
    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    row = {
        "label": label,
        "base_file": base_file,
        "counter_file": counter_file,
        "target_mask": target_mask_name,
        "cell_gate": cell_gate_name,
        "alpha": float(alpha),
        "active_gate_mean": float(active_gate_mean),
        "prediction_hash": pred_hash,
    }
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate_candidates(
    bases: list[str],
    counters: list[str],
    arrays: dict[str, np.ndarray],
    raw: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> tuple[list[dict[str, object]], list[np.ndarray]]:
    raw_logit = logit(raw)
    logits = {file_name: logit(arrays[file_name]) for file_name in arrays}
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in bases:
        base_logit = logits[base_file]
        base_delta = base_logit - raw_logit
        for counter_file in counters:
            if counter_file == base_file:
                continue
            counter_logit = logits[counter_file]
            counter_delta = counter_logit - raw_logit
            step = counter_logit - base_logit
            for target_mask_name in TARGET_MASKS:
                target_gate = target_mask(target_mask_name)
                for cell_gate_name in ["all", "closer", "opposing", "closer_or_opposing"]:
                    gate = target_gate * cell_gate(cell_gate_name, base_delta, counter_delta)
                    active = float(gate.mean())
                    if active <= 1e-8:
                        continue
                    gated_step = step * gate
                    if np.abs(gated_step).mean() <= 1e-10:
                        continue
                    for alpha in ALPHAS:
                        pred = sigmoid(base_logit + alpha * gated_step)
                        label = (
                            f"{base_file}|counter={counter_file}|mask={target_mask_name}|"
                            f"gate={cell_gate_name}|a={alpha:.2f}"
                        )
                        add_candidate(
                            rows,
                            preds,
                            seen,
                            label,
                            base_file,
                            counter_file,
                            target_mask_name,
                            cell_gate_name,
                            alpha,
                            pred,
                            axes,
                            active,
                        )

    return rows, preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 220.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.0024, 0.0) * 0.025
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.00162, 0.0) * 0.030
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 6.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00275)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["prefilter_score"],
            1000,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0025)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["prefilter_score"],
            1000,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.0026)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57698),
            ["prefilter_score"],
            850,
        ),
        (
            (frame["bad_residual_axis_ratio"].abs() <= 0.0018)
            & (frame["delta_vs_raw05_rawaxis"] <= 2.0e-7)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57702),
            ["prefilter_score"],
            650,
        ),
    ]
    parts = []
    for mask, sort_cols, limit in specs:
        parts.append(frame[mask].sort_values(sort_cols).head(limit))
    parts.append(frame.sort_values("prefilter_score").head(700))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(3200)


def score_candidates(selected_for_scoring: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 220.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.0024, 0.0) * 0.025
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57692, 0.0) * 0.80
    )
    scored["strict_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"], 0.0) * 280.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00245, 0.0) * 0.030
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57695, 0.0) * 0.70
    )
    scored["lowbad_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.0016, 0.0) * 0.035
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57698, 0.0) * 0.55
    )
    return scored.sort_values(["selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "actual_probe",
            (scored["delta_vs_raw05_rawaxis"] <= 6.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00275)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["actual_anchor_score_final", "selection_score"],
            28,
        ),
        (
            "raw_boundary",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0025)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["actual_anchor_score_final", "selection_score"],
            28,
        ),
        (
            "strict_raw",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00255)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57698),
            ["strict_score", "actual_anchor_score_final"],
            24,
        ),
        (
            "low_bad",
            (scored["bad_residual_axis_ratio"].abs() <= 0.0018)
            & (scored["delta_vs_raw05_rawaxis"] <= 2.0e-7)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57702),
            ["lowbad_score", "actual_anchor_score_final"],
            20,
        ),
        (
            "posterior",
            (scored["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (scored["delta_vs_raw05_rawaxis"] <= 2.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00265),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            12,
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
        file_name = f"submission_raw05_jepa_q3cw_{tag}.csv"
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
        "target_mask",
        "cell_gate",
        "alpha",
        "base_file",
        "counter_file",
    ]
    best_by_mask = (
        scored.sort_values("actual_anchor_score_final")
        .groupby(["target_mask", "cell_gate"], as_index=False)
        .head(1)
        .sort_values("actual_anchor_score_final")
    )
    lines = [
        "# Raw05 JEPA Q3 Stress Counterweight Optimizer",
        "",
        "This pass keeps the Q3-stress JEPA base signal and blends only selected target blocks toward low-bad/strict counter candidates.",
        "The intent is JEPA-style representation agreement: Q3 carries the hidden target-block signal, while Q2/S1/S-blocks serve as raw05/public-axis counterweights.",
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
        selected[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best By Target Mask / Cell Gate",
        "",
        "```csv",
        best_by_mask[
            [
                "target_mask",
                "cell_gate",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "alpha",
                "base_file",
                "counter_file",
            ]
        ].head(35).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(40).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    bases, counters = choose_base_and_counter_files()
    files = unique_existing([RAW05_FILE, *bases, *counters])
    arrays = load_arrays(files, sample)
    axes = public_axes()

    rows, preds = generate_candidates(bases, counters, arrays, raw, axes)
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
        "target_mask",
        "cell_gate",
        "alpha",
        "base_file",
        "counter_file",
    ]
    print(f"bases={len(bases)} counters={len(counters)} generated={len(scan)} rescored={len(scored)} saved={len(selected)}")
    print(selected[cols].head(30).round(10).to_string(index=False))
    print(integ.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
