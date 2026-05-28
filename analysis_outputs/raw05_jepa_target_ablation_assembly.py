from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
JEPA = ROOT / "jepa"
DATA = ROOT / "data"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import KEY, TARGETS, clip, stable_tag  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from raw05_anchor_jepa_micro_injection import (  # noqa: E402
    RAW05_FILE,
    actual_anchor_score,
    integrity,
    load_arrays,
    load_donor_files,
    read_submission,
    save_submission,
)


OUT_SCAN = OUT / "raw05_jepa_target_ablation_assembly_scan.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_target_ablation_assembly_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_target_ablation_assembly_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_target_ablation_assembly_report.md"

GROUPS = {
    "all": TARGETS,
    "no_q2": ["Q1", "Q3", "S1", "S2", "S3", "S4"],
    "q3_s": ["Q3", "S1", "S2", "S3", "S4"],
    "q3_s2_s3_s4": ["Q3", "S2", "S3", "S4"],
    "s_all": ["S1", "S2", "S3", "S4"],
    "q3_s4": ["Q3", "S4"],
}

LEAVE_RAW_GROUPS = {
    "q2_s1": ["Q2", "S1"],
    "q2_s4": ["Q2", "S4"],
    "q2_s2": ["Q2", "S2"],
    "q2_s3": ["Q2", "S3"],
    "q2_q3": ["Q2", "Q3"],
    "s1_s4": ["S1", "S4"],
    "q2_s1_s4": ["Q2", "S1", "S4"],
}


def label_name(file_name: str) -> str:
    return file_name.replace("submission_", "").replace(".csv", "")


def donor_pool() -> list[str]:
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")
    constrained = pd.read_csv(OUT / "final_jepa_constrained_shortlist_20260527.csv")
    rows: list[str] = []
    rows.extend(priority["file"].astype(str).head(10).tolist())
    rows.extend(
        constrained[
            constrained["filter"].eq("balanced_raw_le_1e-7_bad_le_0p0025_posterior_le_0p5769")
        ]["file"].astype(str).head(10).tolist()
    )
    rows.extend(
        constrained[
            constrained["filter"].eq("strict_raw_le_0_bad_le_0p0025_posterior_le_0p5769")
        ]["file"].astype(str).head(10).tolist()
    )
    rows.extend(load_donor_files()[:10])
    out: list[str] = []
    seen: set[str] = set()
    for name in rows:
        if name == RAW05_FILE or name in seen:
            continue
        try:
            read_submission(name)
        except FileNotFoundError:
            continue
        seen.add(name)
        out.append(name)
    return out[:24]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    label: str,
    pred: np.ndarray,
    axes: dict[str, np.ndarray | float],
) -> None:
    pred = clip(pred)
    h = prediction_hash(pred)
    if h in seen:
        return
    seen.add(h)
    rec = {"label": label, "prediction_hash": h}
    rec.update(public_axis_features(pred, axes))
    rows.append(rec)
    preds.append(pred)


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
    return scored.sort_values(["selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"]).sort_values(
        KEY
    ).reset_index(drop=True)
    raw = read_submission(RAW05_FILE)[TARGETS].to_numpy(dtype=np.float64)
    files = donor_pool()
    arrays = load_arrays(files, sample)
    axes = public_axes()

    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for file_name, donor in arrays.items():
        short = label_name(file_name)
        add_candidate(rows, preds, seen, f"donor_full:{short}", donor, axes)
        for target in TARGETS:
            j = TARGETS.index(target)
            graft = raw.copy()
            graft[:, j] = donor[:, j]
            add_candidate(rows, preds, seen, f"single_graft:{target}<={short}", graft, axes)

            leave = donor.copy()
            leave[:, j] = raw[:, j]
            add_candidate(rows, preds, seen, f"leave_one_raw:{short}|{target}=raw05", leave, axes)
        for group_name, targets in GROUPS.items():
            mask = np.asarray([target in set(targets) for target in TARGETS], dtype=bool)
            graft = raw.copy()
            graft[:, mask] = donor[:, mask]
            add_candidate(rows, preds, seen, f"group_graft:{group_name}<={short}", graft, axes)
        for group_name, targets in LEAVE_RAW_GROUPS.items():
            mask = np.asarray([target in set(targets) for target in TARGETS], dtype=bool)
            leave = donor.copy()
            leave[:, mask] = raw[:, mask]
            add_candidate(rows, preds, seen, f"leave_group_raw:{short}|{group_name}=raw05", leave, axes)

    scored = score_candidates(rows, preds, sample)
    scored.to_csv(OUT_SCAN, index=False)

    parts = []
    filters = [
        (
            "balanced",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0025)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            30,
        ),
        (
            "strict_raw",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0027)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            25,
        ),
        (
            "low_bad",
            (scored["delta_vs_raw05_rawaxis"] <= 2.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0016)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            20,
        ),
        (
            "overall",
            (scored["delta_vs_raw05_rawaxis"] <= 5.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0030),
            25,
        ),
        (
            "actual_probe",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-6)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0031)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57715),
            16,
        ),
        (
            "pair_probe",
            scored["label"].str.contains(r"\|q2_s1=raw05", regex=True)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.0e-6)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.0018)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57715),
            8,
        ),
    ]
    for bucket, mask, limit in filters:
        sort_cols = ["actual_anchor_score_final", "selection_score"] if bucket in {"actual_probe", "pair_probe"} else [
            "selection_score",
            "actual_anchor_score_final",
        ]
        part = scored[mask].sort_values(sort_cols).head(limit).copy()
        part["bucket"] = bucket
        parts.append(part)
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    selected = selected.sort_values(["selection_score", "actual_anchor_score_final"]).copy()

    files_out = []
    for _, row in selected.iterrows():
        h = str(row["prediction_hash"])
        pred_idx = next(i for i, rec in enumerate(rows) if rec["prediction_hash"] == h)
        file_name = f"submission_raw05_jepa_targetasm_{stable_tag(str(row['label']) + h)}.csv"
        save_submission(file_name, sample, preds[pred_idx])
        files_out.append(file_name)
    selected.insert(0, "file", files_out)
    selected.to_csv(OUT_SHORTLIST, index=False)
    integ = integrity(files_out, sample)
    integ.to_csv(OUT_INTEGRITY, index=False)

    cols = [
        "file",
        "bucket",
        "actual_anchor_score_final",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "mean_abs_move_vs_raw05",
        "label",
    ]
    lines = [
        "# Raw05 JEPA Target Ablation Assembly",
        "",
        "This pass decomposes JEPA gains by target column: raw05 plus one donor target, donor minus one target, group grafts, and saved high-upside/risk-reduction target assemblies.",
        "",
        f"- donor files: {len(files)}",
        f"- generated/scored candidates: {len(scored)}",
        f"- saved candidates: {len(selected)}",
        "",
        "## Top Saved",
        "",
        "```csv",
        selected[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Best By Label Type",
        "",
        "```csv",
        scored.assign(label_type=scored['label'].str.split(':').str[0])
        .groupby('label_type', as_index=False)
        .agg(
            n=('label', 'count'),
            best_actual_anchor_score=('actual_anchor_score_final', 'min'),
            best_posterior=('posterior_expected_public_vs_anchor', 'min'),
            best_raw_delta=('delta_vs_raw05_rawaxis', 'min'),
            median_bad_axis=('bad_residual_axis_ratio', 'median'),
        )
        .sort_values('best_actual_anchor_score')
        .round(10)
        .to_csv(index=False)
        .strip(),
        "```",
        "",
        "## Integrity",
        "",
        "```csv",
        integ.head(30).round(10).to_csv(index=False).strip(),
        "```",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"donors={len(files)} scored={len(scored)} saved={len(selected)}")
    print(selected[cols].head(30).round(10).to_string(index=False))
    print(integ.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
