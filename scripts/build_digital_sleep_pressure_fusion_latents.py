from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


KEY_COLUMNS = ["subject_id", "lifelog_date"]

DEFAULT_BLOCKS = {
    "boundary_prebed": "artifacts/domain_digital_boundary_prebed_v1.parquet",
    "boundary_sleep_phone": "artifacts/domain_digital_boundary_sleep_phone_v1.parquet",
    "isolation_phone_fragmentation": "artifacts/domain_digital_isolation_phone_fragmentation_v1.parquet",
    "isolation_prebed_consumption": "artifacts/domain_digital_isolation_prebed_consumption_v1.parquet",
    "sleep_fragment_sleep_digital": "artifacts/domain_sleep_fragment_recovery_sleep_digital_v1.parquet",
    "sleep_fragment_postwake_digital": "artifacts/domain_sleep_fragment_recovery_postwake_digital_v1.parquet",
    "chronotype_prebed_arousal": "artifacts/domain_chronotype_sleep_debt_prebed_arousal_v1.parquet",
    "chronotype_postwake_digital": "artifacts/domain_chronotype_sleep_debt_postwake_digital_v1.parquet",
    "wake_phone_inertia": "artifacts/domain_wake_activation_inertia_phone_inertia_v1.parquet",
    "routine_phone_rhythm": "artifacts/domain_routine_regularity_phone_rhythm_v1.parquet",
    "s2_phone_motion_conflict": "artifacts/domain_s2_micro_awake_phone_motion_conflict_v1.parquet",
    "onset_settled_no_phone": "artifacts/domain_sleep_onset_transition_micro_settled_no_phone_v1.parquet",
    "onset_phone_charging_conflict": "artifacts/domain_sleep_onset_transition_micro_phone_charging_conflict_v1.parquet",
    "consensus_prebed_conflict": "artifacts/domain_sleep_consensus_purity_prebed_conflict_v1.parquet",
}


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def clean_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")[-54:]


def read_block(name: str, path: Path, cap: int) -> tuple[pd.DataFrame, list[str]]:
    frame = normalize(pd.read_parquet(path))
    z_cols = [col for col in frame.columns if col.startswith("z_")]
    if not z_cols:
        raise ValueError(f"No latent columns found in {path}")
    variances = frame[z_cols].replace([np.inf, -np.inf], np.nan).var(axis=0, skipna=True).fillna(0.0)
    selected = variances.sort_values(ascending=False).head(cap).index.tolist()
    renamed = {col: f"{name}__{col}" for col in selected}
    return frame[KEY_COLUMNS + selected].rename(columns=renamed), [renamed[col] for col in selected]


def scaled_block(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    values = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(frame[cols])
    scaled = StandardScaler().fit_transform(values)
    return pd.DataFrame(scaled, columns=cols, index=frame.index)


def add_stats(out: dict[str, np.ndarray], prefix: str, block: pd.DataFrame) -> None:
    arr = block.to_numpy(float)
    out[f"z_dspf_{prefix}_mean"] = np.nanmean(arr, axis=1)
    out[f"z_dspf_{prefix}_std"] = np.nanstd(arr, axis=1)
    out[f"z_dspf_{prefix}_abs_mean"] = np.nanmean(np.abs(arr), axis=1)
    out[f"z_dspf_{prefix}_pos_mean"] = np.nanmean(np.maximum(arr, 0.0), axis=1)
    out[f"z_dspf_{prefix}_neg_mean"] = np.nanmean(np.minimum(arr, 0.0), axis=1)
    out[f"z_dspf_{prefix}_max"] = np.nanmax(arr, axis=1)
    out[f"z_dspf_{prefix}_min"] = np.nanmin(arr, axis=1)


def add_top_cols(out: dict[str, np.ndarray], prefix: str, block: pd.DataFrame, keep: int) -> list[str]:
    cols = block.var(axis=0).sort_values(ascending=False).head(keep).index.tolist()
    for i, col in enumerate(cols):
        out[f"z_dspf_{prefix}_{i:02d}_{clean_name(col)}"] = block[col].to_numpy(float)
    return cols


def add_pressure_interactions(out: dict[str, np.ndarray], blocks: dict[str, pd.DataFrame]) -> None:
    def mean_abs(name: str) -> np.ndarray:
        arr = blocks[name].to_numpy(float)
        return np.nanmean(np.abs(arr), axis=1)

    def mean_signed(name: str) -> np.ndarray:
        arr = blocks[name].to_numpy(float)
        return np.nanmean(arr, axis=1)

    prebed = mean_signed("boundary_prebed") + mean_signed("isolation_prebed_consumption") + mean_signed("chronotype_prebed_arousal")
    sleep_phone = mean_signed("boundary_sleep_phone") + mean_signed("sleep_fragment_sleep_digital")
    postwake = mean_signed("sleep_fragment_postwake_digital") + mean_signed("chronotype_postwake_digital") + mean_signed("wake_phone_inertia")
    fragmentation = mean_abs("isolation_phone_fragmentation") + mean_abs("s2_phone_motion_conflict")
    rhythm = mean_abs("routine_phone_rhythm")
    settled = mean_signed("onset_settled_no_phone")
    conflict = mean_abs("onset_phone_charging_conflict") + mean_abs("consensus_prebed_conflict")

    out["z_dspf_prebed_digital_pressure"] = prebed
    out["z_dspf_sleep_window_digital_pressure"] = sleep_phone
    out["z_dspf_postwake_digital_inertia"] = postwake
    out["z_dspf_phone_fragmentation_pressure"] = fragmentation
    out["z_dspf_phone_rhythm_irregularity"] = rhythm
    out["z_dspf_settled_no_phone_score"] = settled
    out["z_dspf_phone_conflict_pressure"] = conflict
    out["z_dspf_prebed_sleep_conflict_product"] = prebed * sleep_phone
    out["z_dspf_fragmented_sleep_product"] = fragmentation * sleep_phone
    out["z_dspf_arousal_inertia_product"] = prebed * postwake
    out["z_dspf_good_digital_hygiene_contrast"] = settled - prebed - sleep_phone - fragmentation
    out["z_dspf_bad_sleep_digital_load"] = prebed + sleep_phone + fragmentation + conflict - settled
    out["z_dspf_rebound_phone_after_sleep"] = postwake - sleep_phone


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in frame.iterrows():
        vals = []
        for col in cols:
            value = row[col]
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    block_specs = DEFAULT_BLOCKS.copy()
    for item in args.block:
        if "=" not in item:
            raise ValueError(f"Block override must be name=path, got {item}")
        name, path = item.split("=", 1)
        block_specs[name] = path

    merged: pd.DataFrame | None = None
    block_cols: dict[str, list[str]] = {}
    for name, raw_path in block_specs.items():
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(path)
        block, cols = read_block(name, path, args.cap_per_block)
        merged = block if merged is None else merged.merge(block, on=KEY_COLUMNS, how="inner", validate="one_to_one")
        block_cols[name] = cols
    if merged is None:
        raise ValueError("No blocks loaded")

    scaled_blocks = {name: scaled_block(merged, cols) for name, cols in block_cols.items()}
    out_cols: dict[str, np.ndarray] = {}
    top_cols: dict[str, list[str]] = {}
    for name, block in scaled_blocks.items():
        add_stats(out_cols, name, block)
        top_cols[name] = add_top_cols(out_cols, name, block, args.keep_per_block)
    add_pressure_interactions(out_cols, scaled_blocks)

    out = pd.concat([merged[KEY_COLUMNS].reset_index(drop=True), pd.DataFrame(out_cols)], axis=1)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output, index=False)

    best = normalize(pd.read_parquet(args.best))
    best_cols = [col for col in best.columns if col.startswith("z_")]
    additive = best[KEY_COLUMNS + best_cols].merge(out, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    additive_output = Path(args.additive_output)
    additive_output.parent.mkdir(parents=True, exist_ok=True)
    additive.to_parquet(additive_output, index=False)

    block_summary = pd.DataFrame(
        [
            {
                "block": name,
                "source": block_specs[name],
                "selected_features": len(block_cols[name]),
                "top_kept": len(top_cols[name]),
            }
            for name in block_specs
        ]
    )
    stats = pd.DataFrame(
        {
            "feature": [col for col in out.columns if col.startswith("z_")],
            "mean": [float(out[col].mean(skipna=True)) for col in out.columns if col.startswith("z_")],
            "std": [float(out[col].std(skipna=True)) for col in out.columns if col.startswith("z_")],
        }
    )
    report = {
        "output": str(output),
        "additive_output": str(additive_output),
        "rows": int(len(out)),
        "feature_count": int(len(out.columns) - len(KEY_COLUMNS)),
        "blocks": block_summary.to_dict(orient="records"),
        "hypothesis": "Digital behavior should be represented as a sleep-pressure timeline: pre-bed arousal, sleep-window intrusion, phone fragmentation, rhythm break, and post-wake inertia.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    output.with_suffix(".report.md").write_text(
        "\n".join(
            [
                "# Digital Sleep Pressure Fusion Latents",
                "",
                "## Hypothesis",
                "",
                report["hypothesis"],
                "",
                f"- Output: `{output}`",
                f"- Additive output: `{additive_output}`",
                f"- Rows: `{len(out)}`",
                f"- Feature count: `{report['feature_count']}`",
                "",
                "## Blocks",
                "",
                dataframe_to_markdown(block_summary),
                "",
                "## Feature Summary",
                "",
                dataframe_to_markdown(stats.head(80)),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fuse digital sleep-pressure feature families.")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_digital_sleep_pressure_fusion_v1.parquet")
    parser.add_argument("--additive-output", default="artifacts/domain_best_plus_digital_sleep_pressure_fusion_v1.parquet")
    parser.add_argument("--cap-per-block", type=int, default=36)
    parser.add_argument("--keep-per-block", type=int, default=8)
    parser.add_argument("--block", action="append", default=[], help="Optional block override as name=path.")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
