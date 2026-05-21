from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "lifelog_date"]

CHANNEL_GROUP_TOKENS = {
    "body": ("act_", "pedo", "step", "running", "walking", "distance", "speed", "cal", "hr_", "body_activity"),
    "phone": ("screen", "charging", "usage", "phone_activity"),
    "light": ("mlight", "wlight"),
    "gps_radio": ("gps", "wifi", "ble", "mobility"),
    "ambience": ("amb_",),
    "missingness": ("ev_present", "missing_run", "missing_until_next", "present_run", "ev_no_wear", "ev_low_coverage", "sensor_coverage"),
    "event": ("ev_phone", "ev_charging", "ev_moving", "ev_social", "ev_event", "ev_transition"),
    "cross_modal": ("gap", "activity"),
}


def normalize_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.strftime("%Y-%m-%d")


def all_keys(grid: pd.DataFrame) -> pd.DataFrame:
    keys = grid[["subject_id", "date"]].drop_duplicates().copy()
    keys["subject_id"] = keys["subject_id"].astype(str)
    keys["lifelog_date"] = normalize_date(keys["date"])
    keys = keys.drop(columns=["date"]).sort_values(KEY_COLUMNS).reset_index(drop=True)
    return keys


def numeric_columns(grid: pd.DataFrame) -> list[str]:
    blocked = {"subject_id", "date", "lifelog_date", "tok"}
    return [col for col in grid.columns if col not in blocked and pd.api.types.is_numeric_dtype(grid[col])]


def group_for_column(column: str) -> str:
    low = column.lower()
    matches = [name for name, tokens in CHANNEL_GROUP_TOKENS.items() if any(token in low for token in tokens)]
    if "gap" in low or ("body" in low and "phone" in low) or ("mobility" in low and "phone" in low):
        return "cross_modal"
    return matches[0] if matches else "other"


def build_tensor(grid: pd.DataFrame, tokens_per_day: int) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str], list[str], dict]:
    table = grid.copy()
    table["subject_id"] = table["subject_id"].astype(str)
    table["date"] = normalize_date(table["date"])
    table["tok"] = table["tok"].astype(int)
    keys = all_keys(table)
    cols = numeric_columns(table)

    skeleton = keys.rename(columns={"lifelog_date": "date"})[["subject_id", "date"]].loc[keys.index.repeat(tokens_per_day)].reset_index(drop=True)
    skeleton["tok"] = np.tile(np.arange(tokens_per_day), len(keys)).astype(int)
    merged = skeleton.merge(table[["subject_id", "date", "tok"] + cols], on=["subject_id", "date", "tok"], how="left", validate="one_to_one")

    raw = merged[cols].replace([np.inf, -np.inf], np.nan)
    mask = raw.notna().astype(np.float32)
    filled = raw.fillna(raw.median(axis=0, skipna=True).fillna(0.0))
    values = StandardScaler().fit_transform(filled.astype(float))
    values = np.clip(np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0), -8.0, 8.0).astype(np.float32)
    mask_values = mask.to_numpy(np.float32)

    n_days = len(keys)
    n_channels = len(cols)
    values = values.reshape(n_days, tokens_per_day, n_channels).transpose(0, 2, 1)
    mask_values = mask_values.reshape(n_days, tokens_per_day, n_channels).transpose(0, 2, 1)
    groups = [group_for_column(col) for col in cols]
    group_counts = pd.Series(groups).value_counts().sort_index().to_dict()
    diag = {
        "n_days": int(n_days),
        "tokens_per_day": int(tokens_per_day),
        "n_channels": int(n_channels),
        "observed_fraction": float(mask_values.mean()),
        "channel_group_counts": {str(k): int(v) for k, v in group_counts.items()},
        "date_min": str(keys["lifelog_date"].min()),
        "date_max": str(keys["lifelog_date"].max()),
        "subjects": sorted(keys["subject_id"].unique().tolist()),
    }
    return keys, values, mask_values, cols, groups, diag


def write_reports(output_npz: Path, experiment_dir: Path, keys: pd.DataFrame, channels: list[str], groups: list[str], diag: dict) -> None:
    experiment_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "artifact": str(output_npz),
        **diag,
        "channels": channels,
        "channel_groups": groups,
    }
    (experiment_dir / "domain_encoder_tokens_v1_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    group_df = pd.Series(groups).value_counts().sort_index().reset_index()
    group_df.columns = ["group", "channels"]
    lines = [
        "# Domain Encoder Tokens v1",
        "",
        "## Purpose",
        "",
        "Create an encoder-first value/mask tensor from the 30-minute lifelog grid. This is the shared input for Transformer/Diffusion/SSL experiments and does not use labels.",
        "",
        "## Tensor",
        "",
        f"- Artifact: `{output_npz}`",
        f"- Shape values/mask: `[days={diag['n_days']}, channels={diag['n_channels']}, tokens={diag['tokens_per_day']}]`",
        f"- Observed fraction: `{diag['observed_fraction']:.6f}`",
        f"- Date range: `{diag['date_min']}..{diag['date_max']}`",
        "",
        "## Channel Groups",
        "",
        "| group | channels |",
        "| --- | ---: |",
    ]
    lines.extend(f"| {row.group} | {int(row.channels)} |" for row in group_df.itertuples(index=False))
    lines.extend(
        [
            "",
            "## Encoder-First Contract",
            "",
            "- `values` contains standardized sensor/event values.",
            "- `mask` explicitly distinguishes observed values from imputed cells.",
            "- `channel_groups` allows family ablation without touching label data.",
            "- Label probes must be separate downstream diagnostics, not part of token construction.",
        ]
    )
    (experiment_dir / "domain_encoder_tokens_v1_report.md").write_text("\n".join(lines), encoding="utf-8")
    keys.to_csv(experiment_dir / "domain_encoder_token_day_index.csv", index=False)


def run(args: argparse.Namespace) -> None:
    grid = pd.read_parquet(args.grid_path)
    keys, values, mask, channels, groups, diag = build_tensor(grid, args.tokens_per_day)
    output_npz = Path(args.output_path)
    output_npz.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_npz,
        values=values,
        mask=mask,
        subject_id=keys["subject_id"].to_numpy(dtype=object),
        lifelog_date=keys["lifelog_date"].to_numpy(dtype=object),
        channels=np.asarray(channels, dtype=object),
        channel_groups=np.asarray(groups, dtype=object),
    )
    write_reports(output_npz, Path(args.experiment_dir), keys, channels, groups, diag)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build encoder-first value/mask token tensors from the domain lifelog grid.")
    parser.add_argument("--grid-path", default="artifacts/multires_30min_event_hybrid_grid.parquet")
    parser.add_argument("--output-path", default="artifacts/domain_encoder_tokens_v1.npz")
    parser.add_argument("--experiment-dir", default="experiments/domain_idea_bank")
    parser.add_argument("--tokens-per-day", type=int, default=48)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
