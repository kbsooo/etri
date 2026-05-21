from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]


def run(args: argparse.Namespace) -> None:
    frame = pd.read_parquet(args.input).copy()
    frame["subject_id"] = frame["subject_id"].astype(str)
    frame["lifelog_date"] = pd.to_datetime(frame["lifelog_date"]).dt.strftime("%Y-%m-%d")
    z_cols = [col for col in frame.columns if col.startswith("z_")]
    if args.include:
        keep = [col for col in z_cols if any(pattern in col for pattern in args.include)]
    else:
        keep = z_cols
    if args.exclude:
        keep = [col for col in keep if not any(pattern in col for pattern in args.exclude)]
    if not keep:
        raise ValueError("No latent columns selected")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame[KEY_COLUMNS + keep].to_parquet(output, index=False)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Select z_* latent columns by substring filters.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--include", nargs="*", default=[])
    parser.add_argument("--exclude", nargs="*", default=[])
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
