from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_submission_compatible(reference: pd.DataFrame, candidate: pd.DataFrame, name: str) -> None:
    if list(candidate.columns) != list(reference.columns):
        raise ValueError(f"{name} columns differ from reference submission")
    if candidate.shape != reference.shape:
        raise ValueError(f"{name} shape differs from reference submission: {candidate.shape} vs {reference.shape}")
    keys = ["subject_id", "sleep_date", "lifelog_date"]
    if not candidate[keys].astype(str).equals(reference[keys].astype(str)):
        raise ValueError(f"{name} key rows differ from reference submission")
    values = candidate[TARGET_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{name} contains non-finite predictions")
    if values.min() < 0.0 or values.max() > 1.0:
        raise ValueError(f"{name} predictions are outside [0, 1]")


def write_submission(path: Path, df: pd.DataFrame, reference: pd.DataFrame) -> None:
    assert_submission_compatible(reference, df, path.name)
    df.to_csv(path, index=False)


def build_candidates(args: argparse.Namespace) -> pd.DataFrame:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in output_dir.glob("submission_*.csv"):
        path.unlink()

    sample = pd.read_csv(args.sample_path)
    v77 = pd.read_csv(args.v77_path)
    v76 = pd.read_csv(args.v76_path)
    etri = pd.read_csv(args.etri_path)
    for name, df in [("v77", v77), ("v76", v76), ("etri", etri)]:
        assert_submission_compatible(sample, df, name)

    exact_path = output_dir / "submission_01_exact_v77_recommended.csv"
    shutil.copyfile(args.v77_path, exact_path)

    for order, weight, label in [(2, 0.95, "95_05"), (3, 0.90, "90_10"), (4, 0.80, "80_20")]:
        candidate = v77.copy()
        for target in TARGET_COLUMNS:
            candidate[target] = np.clip(weight * v77[target] + (1.0 - weight) * etri[target], 1e-5, 1.0 - 1e-5)
        write_submission(output_dir / f"submission_{order:02d}_v77_etri_blend_{label}.csv", candidate, sample)

    for order, weight, label in [(5, 1.05, "1p05"), (6, 1.10, "1p10")]:
        candidate = v77.copy()
        for target in TARGET_COLUMNS:
            raw = v76[target] + weight * (v77[target] - v76[target])
            candidate[target] = np.clip(0.9 * raw + 0.1 * etri[target], 0.02, 0.98)
        write_submission(output_dir / f"submission_{order:02d}_v76_to_v77_extrap_{label}_etri10.csv", candidate, sample)

    rows = []
    v77_values = v77[TARGET_COLUMNS].to_numpy(dtype=float)
    v76_values = v76[TARGET_COLUMNS].to_numpy(dtype=float)
    etri_values = etri[TARGET_COLUMNS].to_numpy(dtype=float)
    for path in sorted(output_dir.glob("submission_*.csv")):
        df = pd.read_csv(path)
        values = df[TARGET_COLUMNS].to_numpy(dtype=float)
        rows.append(
            {
                "file": path.name,
                "sha256": sha256_file(path),
                "mean_abs_move_from_v77": float(np.mean(np.abs(values - v77_values))),
                "mean_abs_move_from_v76": float(np.mean(np.abs(values - v76_values))),
                "corr_v77": float(np.corrcoef(values.ravel(), v77_values.ravel())[0, 1]),
                "corr_etri": float(np.corrcoef(values.ravel(), etri_values.ravel())[0, 1]),
                "min": float(values.min()),
                "max": float(values.max()),
            }
        )
    manifest = pd.DataFrame(rows)
    manifest.to_csv(output_dir / "manifest.csv", index=False)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build public-feedback candidate submissions around V77.")
    parser.add_argument("--sample-path", default="data/ch2026_submission_sample.csv")
    parser.add_argument(
        "--v77-path",
        default="/Users/kbsoo/Downloads/dacon/codex/outputs/next_upload/submission_01_v77_v60_aggressive_v76aligned.csv",
    )
    parser.add_argument(
        "--v76-path",
        default="/Users/kbsoo/Downloads/dacon/codex/outputs/upload_queue_public_balanced_hedge_v76/submission_01_v76_balanced_hedge_best.csv",
    )
    parser.add_argument("--etri-path", default="outputs/master_aggressive_decoder_fast/submission_temporal_master_oof_blend.csv")
    parser.add_argument("--output-dir", default="outputs/public_feedback_bold_candidates")
    return parser.parse_args()


def main() -> None:
    manifest = build_candidates(parse_args())
    print(manifest.to_string(index=False))


if __name__ == "__main__":
    main()
