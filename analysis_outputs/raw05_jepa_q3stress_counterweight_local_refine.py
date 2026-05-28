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


OUT_SCAN = OUT / "raw05_jepa_q3stress_counterweight_local_scan.csv"
OUT_SCORED = OUT / "raw05_jepa_q3stress_counterweight_local_scored.csv"
OUT_SHORTLIST = OUT / "raw05_jepa_q3stress_counterweight_local_shortlist.csv"
OUT_INTEGRITY = OUT / "raw05_jepa_q3stress_counterweight_local_integrity.csv"
OUT_REPORT = OUT / "raw05_jepa_q3stress_counterweight_local_report.md"

TARGET_INDEX = {target: i for i, target in enumerate(TARGETS)}

ALPHAS = [
    0.42,
    0.44,
    0.46,
    0.48,
    0.50,
    0.52,
    0.54,
    0.56,
    0.58,
    0.60,
    0.62,
    0.64,
]


def prediction_hash(pred: np.ndarray) -> str:
    return stable_tag(np.round(clip(pred), 10).tobytes().hex())


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
        if file_name in seen or not file_exists(file_name):
            continue
        seen.add(file_name)
        keep.append(file_name)
    return keep


def profile_vector(**weights: float) -> np.ndarray:
    vec = np.zeros(len(TARGETS), dtype=np.float64)
    for target, value in weights.items():
        vec[TARGET_INDEX[target]] = float(value)
    return vec.reshape(1, -1)


def target_profiles() -> list[tuple[str, np.ndarray]]:
    return [
        ("nonq3s4_flat", profile_vector(Q1=1.0, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("nonq3s4_noq1", profile_vector(Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("nonq3s4_q1light", profile_vector(Q1=0.45, Q2=1.0, S1=1.0, S2=1.0, S3=1.0)),
        ("nonq3s4_q2light", profile_vector(Q1=1.0, Q2=0.55, S1=1.0, S2=1.0, S3=1.0)),
        ("nonq3s4_q2s1heavy", profile_vector(Q1=0.80, Q2=1.15, S1=1.15, S2=0.85, S3=0.85)),
        ("nonq3s4_s23heavy", profile_vector(Q1=0.75, Q2=0.85, S1=0.85, S2=1.20, S3=1.20)),
        ("nonq3s4_q2s1only", profile_vector(Q2=1.0, S1=1.0)),
        ("nonq3s4_sonly", profile_vector(S1=1.0, S2=1.0, S3=1.0)),
        ("nonq3_s4tiny", profile_vector(Q1=1.0, Q2=1.0, S1=1.0, S2=1.0, S3=1.0, S4=0.20)),
    ]


def choose_refine_pool() -> tuple[list[str], list[str]]:
    coarse = pd.read_csv(OUT / "raw05_jepa_q3stress_counterweight_scored.csv")
    coarse_short = pd.read_csv(OUT / "raw05_jepa_q3stress_counterweight_shortlist.csv")
    targetw = pd.read_csv(OUT / "raw05_jepa_target_weight_optimizer_shortlist.csv")
    priority = pd.read_csv(OUT / "final_jepa_candidate_priority_20260527.csv")

    nonq = coarse[coarse["target_mask"].eq("non_q3_s4") & coarse["cell_gate"].eq("all")].copy()
    bases: list[str] = []
    counters: list[str] = [RAW05_FILE]

    bases.extend(nonq.sort_values("actual_anchor_score_final")["base_file"].astype(str).head(22).tolist())
    bases.extend(
        nonq[nonq["bad_residual_axis_ratio"].abs() <= 0.00175]
        .sort_values("actual_anchor_score_final")["base_file"]
        .astype(str)
        .head(14)
        .tolist()
    )
    bases.extend(coarse_short.sort_values("actual_anchor_score_final")["base_file"].astype(str).head(18).tolist())
    bases.extend(
        targetw[targetw["bucket"].isin(["actual_probe", "raw_boundary"])]
        .sort_values("actual_anchor_score_final")["file"]
        .astype(str)
        .head(18)
        .tolist()
    )
    bases.extend(
        targetw[targetw["template"].str.startswith("q2s1q3_refine2")]
        .sort_values("actual_anchor_score_final")["file"]
        .astype(str)
        .head(8)
        .tolist()
    )

    counters.extend(nonq.sort_values("actual_anchor_score_final")["counter_file"].astype(str).head(24).tolist())
    counters.extend(
        nonq[nonq["bad_residual_axis_ratio"].abs() <= 0.00165]
        .sort_values("actual_anchor_score_final")["counter_file"]
        .astype(str)
        .head(18)
        .tolist()
    )
    counters.extend(
        coarse_short[coarse_short["bad_residual_axis_ratio"].abs() <= 0.0018]
        .sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["counter_file"]
        .astype(str)
        .head(18)
        .tolist()
    )
    counters.extend(
        targetw[targetw["bucket"].eq("low_bad")]
        .sort_values(["bad_residual_axis_ratio", "actual_anchor_score_final"])["file"]
        .astype(str)
        .head(20)
        .tolist()
    )
    counters.extend(
        targetw[targetw["bucket"].eq("strict_raw")]
        .sort_values(["delta_vs_raw05_rawaxis", "bad_residual_axis_ratio"])["file"]
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


def add_candidate(
    rows: list[dict[str, object]],
    preds: list[np.ndarray],
    seen: set[str],
    label: str,
    base_file: str,
    counter_file: str,
    profile: str,
    alpha: float,
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
        "base_file": base_file,
        "counter_file": counter_file,
        "profile": profile,
        "alpha": float(alpha),
        "prediction_hash": pred_hash,
    }
    row.update(public_axis_features(pred, axes))
    rows.append(row)
    preds.append(pred)


def generate_candidates(
    bases: list[str],
    counters: list[str],
    arrays: dict[str, np.ndarray],
    axes: dict[str, np.ndarray | float],
) -> tuple[list[dict[str, object]], list[np.ndarray]]:
    logits = {file_name: logit(arrays[file_name]) for file_name in arrays}
    profiles = target_profiles()
    rows: list[dict[str, object]] = []
    preds: list[np.ndarray] = []
    seen: set[str] = set()

    for base_file in bases:
        base_logit = logits[base_file]
        for counter_file in counters:
            if counter_file == base_file:
                continue
            step = logits[counter_file] - base_logit
            for profile_name, profile_gate in profiles:
                gated_step = step * profile_gate
                if np.abs(gated_step).mean() <= 1e-10:
                    continue
                for alpha in ALPHAS:
                    pred = sigmoid(base_logit + alpha * gated_step)
                    label = f"{base_file}|counter={counter_file}|profile={profile_name}|a={alpha:.2f}"
                    add_candidate(rows, preds, seen, label, base_file, counter_file, profile_name, alpha, pred, axes)

    return rows, preds


def prefilter(scan: pd.DataFrame) -> pd.DataFrame:
    frame = scan.copy()
    frame["prefilter_score"] = (
        frame["posterior_expected_public_vs_anchor"]
        + np.maximum(frame["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 240.0
        + np.maximum(frame["bad_residual_axis_ratio"].abs() - 0.00178, 0.0) * 0.050
        + np.maximum(frame["mean_abs_move_vs_raw05"] - 0.00158, 0.0) * 0.035
    )
    specs = [
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.6e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00185)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["prefilter_score"],
            1100,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00180)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["prefilter_score"],
            1000,
        ),
        (
            (frame["delta_vs_raw05_rawaxis"] <= 0.0)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00190)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["prefilter_score"],
            900,
        ),
        (
            (frame["bad_residual_axis_ratio"].abs() <= 0.00155)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["prefilter_score"],
            700,
        ),
        (
            (frame["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (frame["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (frame["bad_residual_axis_ratio"].abs() <= 0.00175),
            ["prefilter_score"],
            700,
        ),
    ]
    parts = [frame[mask].sort_values(sort_cols).head(limit) for mask, sort_cols, limit in specs]
    parts.append(frame.sort_values("prefilter_score").head(600))
    selected = pd.concat(parts, ignore_index=False).drop_duplicates("prediction_hash")
    return selected.sort_values("prefilter_score").head(2800)


def score_candidates(selected_for_scoring: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    indices = selected_for_scoring.index.to_numpy(dtype=int)
    score_preds = [preds[i] for i in indices]
    actual = actual_anchor_score(score_preds, sample).drop(columns=["candidate_index"])
    scored = selected_for_scoring.reset_index(drop=True).copy()
    scored.insert(0, "candidate_index", indices)
    scored = pd.concat([scored, actual], axis=1)
    scored["selection_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"] - 1.0e-7, 0.0) * 240.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00178, 0.0) * 0.050
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57692, 0.0) * 0.80
    )
    scored["strict_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["delta_vs_raw05_rawaxis"], 0.0) * 300.0
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00180, 0.0) * 0.050
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57694, 0.0) * 0.70
    )
    scored["lowbad_score"] = (
        scored["actual_anchor_score_final"]
        + np.maximum(scored["bad_residual_axis_ratio"].abs() - 0.00150, 0.0) * 0.060
        + np.maximum(scored["posterior_expected_public_vs_anchor"] - 0.57691, 0.0) * 0.70
    )
    return scored.sort_values(["selection_score", "actual_anchor_score_final"]).reset_index(drop=True)


def select_and_save(scored: pd.DataFrame, preds: list[np.ndarray], sample: pd.DataFrame) -> pd.DataFrame:
    specs = [
        (
            "actual_probe",
            (scored["delta_vs_raw05_rawaxis"] <= 1.6e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00185)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["actual_anchor_score_final", "selection_score"],
            28,
        ),
        (
            "raw_boundary",
            (scored["delta_vs_raw05_rawaxis"] <= 1.0e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00180)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57694),
            ["actual_anchor_score_final", "selection_score"],
            28,
        ),
        (
            "strict_raw",
            (scored["delta_vs_raw05_rawaxis"] <= 0.0)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00190)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57695),
            ["strict_score", "actual_anchor_score_final"],
            24,
        ),
        (
            "very_low_bad",
            (scored["bad_residual_axis_ratio"].abs() <= 0.00125)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57691),
            ["bad_residual_axis_ratio", "actual_anchor_score_final"],
            12,
        ),
        (
            "low_bad",
            (scored["bad_residual_axis_ratio"].abs() <= 0.00155)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["posterior_expected_public_vs_anchor"] <= 0.57692),
            ["lowbad_score", "actual_anchor_score_final"],
            20,
        ),
        (
            "posterior",
            (scored["posterior_expected_public_vs_anchor"] <= 0.57690)
            & (scored["delta_vs_raw05_rawaxis"] <= 1.2e-7)
            & (scored["bad_residual_axis_ratio"].abs() <= 0.00175),
            ["posterior_expected_public_vs_anchor", "actual_anchor_score_final"],
            14,
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
        file_name = f"submission_raw05_jepa_q3cwlocal_{tag}.csv"
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
        "profile",
        "alpha",
        "base_file",
        "counter_file",
    ]
    best_by_profile = (
        scored.sort_values("actual_anchor_score_final")
        .groupby(["profile", "alpha"], as_index=False)
        .head(1)
        .sort_values("actual_anchor_score_final")
    )
    lines = [
        "# Raw05 JEPA Q3 Stress Counterweight Local Refine",
        "",
        "This pass narrows the previous counterweight result: keep Q3/S4 in the stress base, refine alpha 0.42-0.64, and test nearby non-Q3/S4 target profiles.",
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
        "## Best By Profile / Alpha",
        "",
        "```csv",
        best_by_profile[
            [
                "profile",
                "alpha",
                "actual_anchor_score_final",
                "posterior_expected_public_vs_anchor",
                "delta_vs_raw05_rawaxis",
                "bad_residual_axis_ratio",
                "base_file",
                "counter_file",
            ]
        ].head(40).round(10).to_csv(index=False).strip(),
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
    bases, counters = choose_refine_pool()
    files = unique_existing([RAW05_FILE, *bases, *counters])
    arrays = load_arrays(files, sample)
    axes = public_axes()

    rows, preds = generate_candidates(bases, counters, arrays, axes)
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
        "profile",
        "alpha",
        "base_file",
        "counter_file",
    ]
    print(f"bases={len(bases)} counters={len(counters)} generated={len(scan)} rescored={len(scored)} saved={len(selected)}")
    print(selected[cols].head(30).round(10).to_string(index=False))
    print(integ.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
