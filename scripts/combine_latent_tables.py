from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


KEY_COLUMNS = ["subject_id", "lifelog_date"]


def parse_source(item: str) -> tuple[str, Path]:
    if "=" not in item:
        raise ValueError(f"Source must be name=path, got {item}")
    name, path = item.split("=", 1)
    return name, Path(path)


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def load_prefixed(name: str, path: Path) -> pd.DataFrame:
    frame = normalize_keys(pd.read_parquet(path))
    z_cols = [col for col in frame.columns if col.startswith("z_")]
    if not z_cols:
        raise ValueError(f"No z_* columns in {path}")
    renamed = {col: f"z_{name}_{col.removeprefix('z_')}" for col in z_cols}
    return frame[KEY_COLUMNS + z_cols].rename(columns=renamed)


def run(args: argparse.Namespace) -> None:
    if len(args.source) < 2:
        raise ValueError("Need at least two --source name=path values")
    merged = None
    for item in args.source:
        name, path = parse_source(item)
        part = load_prefixed(name, path)
        if merged is None:
            merged = part
        else:
            merged = merged.merge(part, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    if merged is None:
        raise RuntimeError("No sources loaded")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(output, index=False)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Concatenate fold-safe latent parquet tables by day key.")
    parser.add_argument("--source", action="append", required=True, help="Latent source as name=path")
    parser.add_argument("--output", required=True)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
