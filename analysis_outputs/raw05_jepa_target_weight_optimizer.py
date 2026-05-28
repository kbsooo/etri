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
    load_arrays,
    read_submission,
    save_submission,
)
from raw05_jepa_target_ablation_assembly import donor_pool, label_name  # noqa: E402


OUT_SCAN = OUT / "raw05_jepa_target_weight_optimizer_scan.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_target_weight_optimizer_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_target_weight_optimizer_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_target_weight_optimizer_report.md"

TARGET_INDEX = {target: i for i, target in enumerate(TARGETS)}


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def weight_vector(**kwargs: float) -> np.ndarray:
    weights = np.ones(len(TARGETS), dtype=np.float64)
    for target, value in kwargs.items():
        weights[TARGET_INDEX[target]] = float(value)
    return weights


def template_weight_vectors() -> list[tuple[str, np.ndarray]]:
    templates: list[tuple[str, np.ndarray]] = []

    for q2 in [0.0, 0.15, 0.30, 0.50, 0.75, 1.0]:
        for s1 in [0.0, 0.15, 0.30, 0.50, 0.75, 1.0]:
            templates.append((f"q2s1_plane|q2{q2:.2f}|s1{s1:.2f}", weight_vector(Q2=q2, S1=s1)))

    for q2 in [0.0, 0.20, 0.45, 0.70]:
        for s1 in [0.0, 0.20, 0.45, 0.70]:
            for s4 in [0.60, 0.80, 1.0]:
                templates.append(
                    (
                        f"q2s1s4|q2{q2:.2f}|s1{s1:.2f}|s4{s4:.2f}",
                        weight_vector(Q2=q2, S1=s1, S4=s4),
                    )
                )

    for q2 in [0.0, 0.25, 0.50]:
        for s1 in [0.0, 0.25, 0.50]:
            for s2 in [0.80, 1.0]:
                for s3 in [0.80, 1.0]:
                    templates.append(
                        (
                            f"q2sblock|q2{q2:.2f}|s1{s1:.2f}|s2{s2:.2f}|s3{s3:.2f}",
                            weight_vector(Q2=q2, S1=s1, S2=s2, S3=s3),
                        )
                    )

    # Q3 is the most important donor target in ablation. Only test mild attenuation
    # or boost while Q2/S1 absorb public-risk correction.
    for q2 in [0.0, 0.25, 0.50]:
        for s1 in [0.0, 0.25, 0.50]:
            for q3 in [0.85, 1.0, 1.10]:
                templates.append(
                    (
                        f"q2s1q3|q2{q2:.2f}|s1{s1:.2f}|q3{q3:.2f}",
                        weight_vector(Q2=q2, S1=s1, Q3=q3),
                    )
                )

    for q2 in [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
        for s1 in [0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
            for q3 in [1.04, 1.07, 1.10, 1.13, 1.16]:
                templates.append(
                    (
                        f"q2s1q3_refine|q2{q2:.2f}|s1{s1:.2f}|q3{q3:.2f}",
                        weight_vector(Q2=q2, S1=s1, Q3=q3),
                    )
                )

    for q2 in [0.50, 0.55, 0.60, 0.65, 0.70]:
        for s1 in [0.50, 0.55, 0.60, 0.65, 0.70]:
            for q3 in [1.16, 1.19, 1.22, 1.25]:
                templates.append(
                    (
                        f"q2s1q3_refine2|q2{q2:.2f}|s1{s1:.2f}|q3{q3:.2f}",
                        weight_vector(Q2=q2, S1=s1, Q3=q3),
                    )
                )

    for q2 in [0.65, 0.70, 0.75, 0.80]:
        for s1 in [0.65, 0.70, 0.75, 0.80]:
            for q3 in [1.25, 1.30, 1.35, 1.40]:
                templates.append(
                    (
                        f"q2s1q3_stress|q2{q2:.2f}|s1{s1:.2f}|q3{q3:.2f}",
                        weight_vector(Q2=q2, S1=s1, Q3=q3),
                    )
                )

    seen: set[str] = set()
    unique: list[tuple[str, np.ndarray]] = []
    for name, weights in templates:
        key = ",".join(f"{x:.3f}" for x in weights)
        if key in seen:
            continue
        seen.add(key)
        unique.append((name, weights))
    return unique


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    label: str,
    donor_file: str,
    template: str,
    weights: np.ndarray,
    pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> None:
    pred = clip(pred)
    pred_hash = prediction_hash(pred)
    if pred_hash in seen:
        return
    seen.add(pred_hash)
    row = {
        "label": label,
        "donor_file": donor_file,
        "donor_short": label_name(donor_file),
        "template": template,
        "prediction_hash": pred_hash,
    }
    for target, value in zip(TARGETS, weights):
        row[f"w_{target}"] = float(value)
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate_candidates(
    raw: np.ndarray,
    arrays: dict[str, np.ndarray],
    axes: dict[str, np.ndarray | float],
) -> tuple[list[dict[str, object]], list[np.ndarray]]:
    raw_logit = logit(raw)
    templates = template_weight_vectors()
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for donor_file, donor in arrays.items():
        donor_logit = logit(donor)
        delta = donor_logit - raw_logit
        for template, weights in templates:
            pred = sigmoid(raw_logit + delta * weights.reshape(1, -1))
            label = f"{label_name(donor_file)}|{template}"
            add_candidate(rows, preds, seen, label, donor_file, template, weights, pred, axes)

    return rows, preds


def score_candidates(rows: list[dict[str, object]], preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    actual = actual_anchor_score(preds, sample).drop(columns=["candidate_index"])
    scored = pd.concat([frame, actual], axis=1)
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 200.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.0024, 0.0) * 0.020
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.5769, 0.0) * 0.75
    )
    scored["risk_reduced_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 260.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.0014, 0.0) * 0.030
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57695, 0.0) * 0.55
    )
    return scored.sort_values(["selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, rows: list[dict[str, object]], preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    hash_to_pred = {str(row["prediction_hash"]): preds[i] for i, row in enumerate(rows)}
    specs = [
        (
            "balanced",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0025)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["selection_score", "actual_anchor_score_final"],
            35,
        ),
        (
            "strict_raw",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0027)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["selection_score", "actual_anchor_score_final"],
            30,
        ),
        (
            "low_bad",
            (scored["delta_vs_raw05_rawaxis"] <= 2.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0015)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57702),
            ["risk_reduced_score", "actual_anchor_score_final"],
            25,
        ),
        (
            "actual_probe",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-6)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0030)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57715),
            ["actual_anchor_score_final", "selection_score"],
            25,
        ),
        (
            "raw_boundary",
            scored["template"].str.startswith("q2s1q3_stress")
            & (scored["w_Q3"] >= 1.30)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0025)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["actual_anchor_score_final", "selection_score"],
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
        pred = hash_to_pred[str(row["prediction_hash"])]
        tag = stable_tag(str(row["label"]) + str(row["prediction_hash"]))
        file_name = f"submission_raw05_jepa_targetw_{tag}.csv"
        save_submission(file_name, sample, pred)
        files.append(file_name)
    selected.insert(0, "file", files)
    return selected


def write_report(scored: pd.DataFrame, selected: pd.DataFrame, integ: pd.DataFrame) -> None:
    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "w_Q2",
        "w_S1",
        "w_Q3",
        "w_S4",
        "label",
    ]
    best_by_template = (
        scored.assign(template_family=scored["template"].str.split("|").str[0])
        .sort_values("actual_anchor_score_final")
        .groupby("template_family", as_index=False)
        .head(1)
        .sort_values("actual_anchor_score_final")
    )
    lines = [
        "# Raw05 JEPA Target Weight Optimizer",
        "",
        "This pass treats JEPA donor deltas as target-block representation confidence rather than binary target grafts.",
        "Each candidate is logit(raw05) + target_weight * (logit(donor) - logit(raw05)).",
        "",
        "## Counts",
        "",
        f"- scored candidates: {len(scored)}",
        f"- saved candidates: {len(selected)}",
        "",
        "## Top Saved",
        "",
        "```csv",
        selected[cols].head(35).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best By Template Family",
        "",
        "```csv",
        best_by_template[
            [
                "template_family",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "w_Q2",
                "w_S1",
                "w_Q3",
                "w_S4",
                "label",
            ]
        ].round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(35).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    files = donor_pool()
    arrays = load_arrays(files, sample)
    axes = public_axes()

    rows, preds = generate_candidates(raw, arrays, axes)
    scored = score_candidates(rows, preds, sample)
    scored.to_csv(OUT_SCAN, index=False)

    selected = select_and_save(scored, rows, preds, sample)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(selected["file"].tolist(), sample)
    integ.to_csv(OUT_INTEGRITY, index=False)
    write_report(scored, selected, integ)

    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "w_Q2",
        "w_S1",
        "w_Q3",
        "w_S4",
        "label",
    ]
    print(f"donors={len(files)} scored={len(scored)} saved={len(selected)}")
    print(selected[cols].head(30).round(10).to_string(index=False))
    print(integ.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
