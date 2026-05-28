from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
JEPA = ROOT / "jepa"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from hidden_block_latent_audit import KEY, TARGETS, clip  # noqa: E402
from jepa_energy_ensemble_optimizer import public_axes, public_axis_features  # noqa: E402
from raw05_anchor_jepa_micro_injection import actual_anchor_score  # noqa: E402


SOURCE = OUT / "jepa_block_count_shift_shortlist.csv"
OUT_CSV = OUT / "jepa_block_count_shift_actual_anchor_augmented.csv"
REPORT = OUT / "jepa_block_count_shift_actual_anchor_augmented_report.md"
RAW05_PUBLIC = 0.5775263072
STAGE2_PUBLIC = 0.5779449757

PUBLIC_AXIS_COLS = [
    "posterior_expected_public_vs_anchor",
    "raw_axis_expected_public_vs_stage2",
    "delta_vs_raw05_rawaxis",
    "bad_residual_axis_ratio",
    "ordinal_axis_ratio",
    "mean_abs_move_vs_raw05",
    "min_prob",
    "max_prob",
]


def locate(file_name: str) -> Path | None:
    path = Path(file_name)
    if path.exists():
        return path
    for base in (OUT, JEPA, ROOT):
        candidate = base / file_name
        if candidate.exists():
            return candidate
    return None


def read_submission(file_name: str, sample: pd.DataFrame) -> np.ndarray:
    path = locate(file_name)
    if path is None:
        raise FileNotFoundError(file_name)
    frame = pd.read_csv(path, parse_dates=["sleep_date", "lifelog_date"]).sort_values(KEY).reset_index(drop=True)
    if not frame[KEY].reset_index(drop=True).equals(sample[KEY].reset_index(drop=True)):
        raise ValueError(f"key mismatch: {file_name}")
    return clip(frame[TARGETS].to_numpy(dtype=np.float64))


def candidate_family(file_name: str) -> str:
    stem = file_name.replace("submission_", "").replace(".csv", "")
    if stem.startswith("jepa_block_countshift"):
        return "jepa_block_countshift"
    return stem.rsplit("_", 1)[0]


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)

    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(KEY).reset_index(drop=True)
    source = pd.read_csv(SOURCE).drop_duplicates("file").reset_index(drop=True)
    source = source[source["file"].map(lambda f: locate(str(f)) is not None)].reset_index(drop=True)
    if source.empty:
        raise ValueError("no locatable block-count shift candidates")

    preds = [read_submission(file_name, sample) for file_name in source["file"].astype(str)]
    actual = actual_anchor_score(preds, sample)
    actual["file"] = source["file"].astype(str).to_numpy()

    axes = public_axes()
    axis_rows = []
    for file_name, pred in zip(source["file"].astype(str), preds, strict=True):
        row = {"file": file_name, "family": candidate_family(file_name)}
        row.update(public_axis_features(pred, axes))
        axis_rows.append(row)
    axis_df = pd.DataFrame(axis_rows)

    out = source.drop(columns=PUBLIC_AXIS_COLS, errors="ignore")
    out = out.merge(actual.drop(columns=["candidate_index"]), on="file", how="left").merge(axis_df, on="file", how="left")
    out["source"] = "jepa_block_count_shift_actual_anchor_augmented"
    out["source_rank"] = np.arange(1, len(out) + 1)
    out["actual_anchor_gap_vs_raw05_public"] = out["actual_anchor_score_final"] - RAW05_PUBLIC
    out["actual_anchor_gap_vs_stage2_public"] = out["actual_anchor_score_final"] - STAGE2_PUBLIC
    out["ranker_selection_score"] = (
        out["actual_anchor_score_final"]
        + np.maximum(out["delta_vs_raw05_rawaxis"] - 2.0e-7, 0.0) * 120.0
        + np.maximum(out["bad_residual_axis_ratio"].abs() - 0.0028, 0.0) * 0.030
        + np.maximum(out["posterior_expected_public_vs_anchor"] - 0.57690, 0.0) * 2.0
        + np.maximum(out["mean_abs_move_vs_raw05"] - 0.0028, 0.0) * 0.030
    )
    out = out.sort_values(["ranker_selection_score", "actual_anchor_score_final"]).reset_index(drop=True)
    out.to_csv(OUT_CSV, index=False)

    cols = [
        "file",
        "base",
        "rate_source",
        "gate",
        "target_set",
        "alpha",
        "cap",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "ranker_selection_score",
        "posterior_expected_public_vs_anchor",
        "delta_vs_raw05_rawaxis",
        "bad_residual_axis_ratio",
        "ordinal_axis_ratio",
        "mean_abs_move_vs_raw05",
        "focused_scenario_score",
    ]
    family = (
        out.groupby("family", as_index=False)
        .agg(
            n=("file", "size"),
            best_actual_anchor=("actual_anchor_score_final", "min"),
            best_ranker_selection=("ranker_selection_score", "min"),
            best_raw_abs=("delta_vs_raw05_rawaxis", lambda s: float(s.abs().min())),
            best_bad_abs=("bad_residual_axis_ratio", lambda s: float(s.abs().min())),
            median_move=("mean_abs_move_vs_raw05", "median"),
        )
        .sort_values("best_ranker_selection")
    )
    report = [
        "# JEPA Block-Count Shift Actual-Anchor Augmentation",
        "",
        f"- candidates scored: `{len(out)}`",
        f"- source: `{SOURCE}`",
        f"- output: `{OUT_CSV}`",
        "",
        "## Family Summary",
        "",
        "```csv",
        family.round(10).to_csv(index=False).strip(),
        "```",
        "",
        "## Top Candidates",
        "",
        "```csv",
        out[cols].head(40).round(10).to_csv(index=False).strip(),
        "```",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")

    print(f"scored={len(out)} wrote={OUT_CSV}")
    print(family.round(10).to_string(index=False))
    print(out[cols].head(20).round(10).to_string(index=False))


if __name__ == "__main__":
    main()
