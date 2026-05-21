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

ROUTINE_PATTERNS = [
    r"profile_.*gap",
    r"profile_.*dist",
    r"best_shift",
    r"phase_.*shift",
    r"routine_transition",
    r"routine_state_entropy",
    r"sleep_.*past(7|14|28)",
    r"wake_hour_.*shift",
    r"tst_min_.*past",
    r"sleep_eff_.*past",
]
RHYTHM_PATTERNS = [
    r"night_ratio",
    r"evening_ratio",
    r"run_count",
    r"burstiness",
    r"phase_entropy",
    r"phase_strength",
    r"phase_hour.*shift",
    r"phone_.*corr",
    r"coactive",
]
FRAGMENT_PATTERNS = [
    r"awaken",
    r"sleep_sensor_fragment",
    r"sleep_.*arousal",
    r"sleep_.*phone",
    r"sleep_.*moving",
    r"sleep_.*low_coverage",
    r"sleep_late_minus_early",
    r"longest_block",
]
PREBED_PATTERNS = [
    r"fragmentation_pressure",
    r"last_hour_conflict",
    r"pre(30m|1h|2h).*phone",
    r"pre(30m|1h|2h).*moving",
    r"pre(30m|1h|2h).*conflict",
]


def normalize_keys(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def matching_z_cols(frame: pd.DataFrame, patterns: list[str], cap: int) -> list[str]:
    z_cols = [col for col in frame.columns if col.startswith("z_")]
    compiled = [re.compile(pattern) for pattern in patterns]
    matched = [col for col in z_cols if any(pattern.search(col) for pattern in compiled)]
    if len(matched) <= cap:
        return matched
    variance = frame[matched].replace([np.inf, -np.inf], np.nan).var(axis=0, skipna=True).fillna(0.0)
    return variance.sort_values(ascending=False).head(cap).index.tolist()


def load_selected(name: str, path: Path, patterns: list[str], cap: int) -> pd.DataFrame:
    frame = normalize_keys(pd.read_parquet(path))
    if frame[KEY_COLUMNS].duplicated().any():
        raise ValueError(f"Duplicate keys in {path}")
    cols = matching_z_cols(frame, patterns, cap)
    if not cols:
        raise ValueError(f"No selected columns for {name} from {path}")
    renamed = {col: f"{name}__{col}" for col in cols}
    return frame[KEY_COLUMNS + cols].rename(columns=renamed)


def standardize(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    model = StandardScaler()
    values = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(frame[cols])
    scaled = model.fit_transform(values)
    return pd.DataFrame(scaled, columns=cols, index=frame.index)


def add_block_summaries(out: dict[str, np.ndarray], block_name: str, block: pd.DataFrame) -> None:
    arr = block.to_numpy(float)
    out[f"z_s4rf_{block_name}_mean"] = np.nanmean(arr, axis=1)
    out[f"z_s4rf_{block_name}_std"] = np.nanstd(arr, axis=1)
    out[f"z_s4rf_{block_name}_abs_mean"] = np.nanmean(np.abs(arr), axis=1)
    out[f"z_s4rf_{block_name}_max"] = np.nanmax(arr, axis=1)
    out[f"z_s4rf_{block_name}_min"] = np.nanmin(arr, axis=1)


def add_pair_interactions(
    out: dict[str, np.ndarray],
    left_name: str,
    left: pd.DataFrame,
    right_name: str,
    right: pd.DataFrame,
    max_pairs: int,
) -> None:
    left_cols = left.var(axis=0).sort_values(ascending=False).head(max_pairs).index.tolist()
    right_cols = right.var(axis=0).sort_values(ascending=False).head(max_pairs).index.tolist()
    left_arr = left[left_cols].to_numpy(float)
    right_arr = right[right_cols].to_numpy(float)
    for i, lcol in enumerate(left_cols):
        lname = re.sub(r"[^A-Za-z0-9]+", "_", lcol).strip("_")[-48:]
        for j, rcol in enumerate(right_cols):
            rname = re.sub(r"[^A-Za-z0-9]+", "_", rcol).strip("_")[-48:]
            prod = left_arr[:, i] * right_arr[:, j]
            out[f"z_s4rf_{left_name}_{right_name}_prod_{i:02d}_{j:02d}_{lname}_{rname}"] = prod
    left_score = np.nanmean(np.abs(left_arr), axis=1)
    right_score = np.nanmean(np.abs(right_arr), axis=1)
    out[f"z_s4rf_{left_name}_{right_name}_absload_product"] = left_score * right_score
    out[f"z_s4rf_{left_name}_{right_name}_signedload_product"] = np.nanmean(left_arr, axis=1) * np.nanmean(right_arr, axis=1)


def run(args: argparse.Namespace) -> None:
    routine = load_selected("routine", Path(args.routine), ROUTINE_PATTERNS, args.routine_cap)
    rhythm = load_selected("rhythm", Path(args.rhythm), RHYTHM_PATTERNS, args.rhythm_cap)
    fragment = load_selected("fragment", Path(args.fragment), FRAGMENT_PATTERNS, args.fragment_cap)
    prebed = load_selected("prebed", Path(args.prebed), PREBED_PATTERNS, args.prebed_cap)

    merged = routine.merge(rhythm, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    merged = merged.merge(fragment, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    merged = merged.merge(prebed, on=KEY_COLUMNS, how="inner", validate="one_to_one")

    blocks = {
        "routine": [col for col in merged.columns if col.startswith("routine__")],
        "rhythm": [col for col in merged.columns if col.startswith("rhythm__")],
        "fragment": [col for col in merged.columns if col.startswith("fragment__")],
        "prebed": [col for col in merged.columns if col.startswith("prebed__")],
    }
    scaled_blocks = {name: standardize(merged, cols) for name, cols in blocks.items()}

    out_cols: dict[str, np.ndarray] = {}
    for name, block in scaled_blocks.items():
        add_block_summaries(out_cols, name, block)
        for i, col in enumerate(block.var(axis=0).sort_values(ascending=False).head(args.keep_per_block).index):
            clean = re.sub(r"[^A-Za-z0-9]+", "_", col).strip("_")[-64:]
            out_cols[f"z_s4rf_{name}_{i:02d}_{clean}"] = block[col].to_numpy(float)

    add_pair_interactions(out_cols, "routine", scaled_blocks["routine"], "fragment", scaled_blocks["fragment"], args.interaction_top_k)
    add_pair_interactions(out_cols, "routine", scaled_blocks["routine"], "prebed", scaled_blocks["prebed"], args.interaction_top_k)
    add_pair_interactions(out_cols, "rhythm", scaled_blocks["rhythm"], "fragment", scaled_blocks["fragment"], args.interaction_top_k)
    add_pair_interactions(out_cols, "rhythm", scaled_blocks["rhythm"], "prebed", scaled_blocks["prebed"], args.interaction_top_k)

    out = pd.concat([merged[KEY_COLUMNS].reset_index(drop=True), pd.DataFrame(out_cols)], axis=1)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output, index=False)

    report = {
        "output": str(output),
        "rows": int(len(out)),
        "feature_count": int(len(out.columns) - len(KEY_COLUMNS)),
        "inputs": {
            "routine": args.routine,
            "rhythm": args.rhythm,
            "fragment": args.fragment,
            "prebed": args.prebed,
        },
        "selected_counts": {name: len(cols) for name, cols in blocks.items()},
        "keep_per_block": int(args.keep_per_block),
        "interaction_top_k": int(args.interaction_top_k),
        "hypothesis": "S4 may need routine/circadian break gated by actual night fragmentation or pre-bed conflict episodes.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = [
        "# S4 Routine Fragment Latents",
        "",
        "## Purpose",
        "",
        "Encode whether routine/circadian disruption is accompanied by sleep-window fragmentation or pre-bed conflict. Labels are not used.",
        "",
        f"- Output: `{output}`",
        f"- Rows: `{len(out)}`",
        f"- Feature count: `{report['feature_count']}`",
        "",
        "## Selected Source Counts",
        "",
        "| block | selected columns |",
        "| --- | ---: |",
        *[f"| {name} | {count} |" for name, count in report["selected_counts"].items()],
    ]
    output.with_suffix(".report.md").write_text("\n".join(md), encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build S4 routine-fragment interaction latents.")
    parser.add_argument("--routine", default="artifacts/domain_routine_regularity_v1.parquet")
    parser.add_argument("--rhythm", default="artifacts/domain_event_rhythm_v1.parquet")
    parser.add_argument("--fragment", default="artifacts/domain_sleep_fragment_recovery_v1.parquet")
    parser.add_argument("--prebed", default="artifacts/domain_sleep_onset_transition_prebed_fragmentation_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_s4_routine_fragment_v1.parquet")
    parser.add_argument("--routine-cap", type=int, default=60)
    parser.add_argument("--rhythm-cap", type=int, default=40)
    parser.add_argument("--fragment-cap", type=int, default=80)
    parser.add_argument("--prebed-cap", type=int, default=40)
    parser.add_argument("--keep-per-block", type=int, default=20)
    parser.add_argument("--interaction-top-k", type=int, default=10)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
