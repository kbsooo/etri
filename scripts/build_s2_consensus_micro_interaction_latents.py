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
CONSENSUS_PATTERNS = [
    r"sleep_(full|first|mid|final).*sleep_consensus.*(subdev|subrz|subpct)",
    r"sleep_(full|first|mid|final).*observed_quiet.*(subdev|subrz|subpct)",
    r"sleep_(full|first|mid|final).*missing_sleep_like.*(subdev|subrz|subpct)",
    r"sleep_(full|first|mid|final).*device_off_conflict.*(subdev|subrz|subpct)",
    r"sleep_(full|first|mid|final).*quiet_break.*(subdev|subrz|subpct)",
    r"purity_final_minus_first.*(subdev|subrz|subpct)",
    r"consensus_duration_share.*(subdev|subrz|subpct)",
]
MICRO_PATTERNS = [
    r"sleep_(full|first|mid|final)_micro_awake_score_past(3|7|14|28)",
    r"sleep_(full|first|mid|final)_quiet_break_ratio_past(3|7|14|28)",
]


def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out["subject_id"] = out["subject_id"].astype(str)
    out["lifelog_date"] = pd.to_datetime(out["lifelog_date"]).dt.strftime("%Y-%m-%d")
    return out


def select_columns(frame: pd.DataFrame, patterns: list[str], cap: int) -> list[str]:
    compiled = [re.compile(pattern) for pattern in patterns]
    selected = [
        col
        for col in frame.columns
        if col.startswith("z_scp_") and any(pattern.search(col) for pattern in compiled)
    ]
    selected = sorted(set(selected))
    if len(selected) <= cap:
        return selected
    variances = frame[selected].replace([np.inf, -np.inf], np.nan).var(axis=0, skipna=True).fillna(0.0)
    return variances.sort_values(ascending=False).head(cap).index.tolist()


def scaled_block(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    values = SimpleImputer(strategy="median", keep_empty_features=True).fit_transform(frame[cols])
    scaled = StandardScaler().fit_transform(values)
    return pd.DataFrame(scaled, columns=cols, index=frame.index)


def clean_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")[-56:]


def add_block_summary(out: dict[str, np.ndarray], name: str, block: pd.DataFrame) -> None:
    arr = block.to_numpy(float)
    out[f"z_s2cmi_{name}_mean"] = np.nanmean(arr, axis=1)
    out[f"z_s2cmi_{name}_std"] = np.nanstd(arr, axis=1)
    out[f"z_s2cmi_{name}_abs_mean"] = np.nanmean(np.abs(arr), axis=1)
    out[f"z_s2cmi_{name}_max"] = np.nanmax(arr, axis=1)
    out[f"z_s2cmi_{name}_min"] = np.nanmin(arr, axis=1)


def add_top_columns(out: dict[str, np.ndarray], name: str, block: pd.DataFrame, keep: int) -> list[str]:
    cols = block.var(axis=0).sort_values(ascending=False).head(keep).index.tolist()
    for i, col in enumerate(cols):
        out[f"z_s2cmi_{name}_{i:02d}_{clean_name(col)}"] = block[col].to_numpy(float)
    return cols


def add_interactions(
    out: dict[str, np.ndarray],
    consensus: pd.DataFrame,
    micro: pd.DataFrame,
    top_k: int,
) -> None:
    c_cols = consensus.var(axis=0).sort_values(ascending=False).head(top_k).index.tolist()
    m_cols = micro.var(axis=0).sort_values(ascending=False).head(top_k).index.tolist()
    c_arr = consensus[c_cols].to_numpy(float)
    m_arr = micro[m_cols].to_numpy(float)
    c_abs = np.nanmean(np.abs(c_arr), axis=1)
    m_abs = np.nanmean(np.abs(m_arr), axis=1)
    c_mean = np.nanmean(c_arr, axis=1)
    m_mean = np.nanmean(m_arr, axis=1)
    out["z_s2cmi_consensus_micro_absload_product"] = c_abs * m_abs
    out["z_s2cmi_consensus_micro_signedload_product"] = c_mean * m_mean
    out["z_s2cmi_consensus_micro_conflict_load"] = c_abs * np.maximum(m_mean, 0.0)
    out["z_s2cmi_consensus_micro_recovery_load"] = np.maximum(c_mean, 0.0) * np.maximum(-m_mean, 0.0)
    for i, c_col in enumerate(c_cols):
        for j, m_col in enumerate(m_cols):
            out[f"z_s2cmi_prod_{i:02d}_{j:02d}_{clean_name(c_col)}__{clean_name(m_col)}"] = c_arr[:, i] * m_arr[:, j]


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
    consensus = normalize(pd.read_parquet(args.consensus))
    micro = normalize(pd.read_parquet(args.micro))
    best = normalize(pd.read_parquet(args.best))
    c_cols = select_columns(consensus, CONSENSUS_PATTERNS, args.consensus_cap)
    m_cols = select_columns(micro, MICRO_PATTERNS, args.micro_cap)
    if not c_cols:
        raise ValueError("No consensus columns selected")
    if not m_cols:
        raise ValueError("No micro columns selected")

    merged = consensus[KEY_COLUMNS + c_cols].merge(micro[KEY_COLUMNS + m_cols], on=KEY_COLUMNS, how="inner", validate="one_to_one")
    consensus_block = scaled_block(merged, c_cols)
    micro_block = scaled_block(merged, m_cols)
    out_cols: dict[str, np.ndarray] = {}
    add_block_summary(out_cols, "consensus", consensus_block)
    add_block_summary(out_cols, "micro", micro_block)
    kept_consensus = add_top_columns(out_cols, "consensus", consensus_block, args.keep_per_block)
    kept_micro = add_top_columns(out_cols, "micro", micro_block, args.keep_per_block)
    add_interactions(out_cols, consensus_block, micro_block, args.interaction_top_k)

    out = pd.concat([merged[KEY_COLUMNS].reset_index(drop=True), pd.DataFrame(out_cols)], axis=1)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output, index=False)

    best_cols = [c for c in best.columns if c.startswith("z_")]
    additive = best[KEY_COLUMNS + best_cols].merge(out, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    additive_output = Path(args.additive_output)
    additive_output.parent.mkdir(parents=True, exist_ok=True)
    additive.to_parquet(additive_output, index=False)

    report = {
        "output": str(output),
        "additive_output": str(additive_output),
        "rows": int(len(out)),
        "feature_count": int(len(out.columns) - len(KEY_COLUMNS)),
        "selected_consensus_count": int(len(c_cols)),
        "selected_micro_count": int(len(m_cols)),
        "kept_consensus_columns": kept_consensus,
        "kept_micro_columns": kept_micro,
        "interaction_top_k": int(args.interaction_top_k),
        "hypothesis": "S2 needs gated interaction between subject-relative sleep-consensus purity and recent rolling micro-awakening, not a direct replacement.",
    }
    output.with_suffix(".report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    stats = pd.DataFrame(
        {
            "feature": [c for c in out.columns if c.startswith("z_")],
            "mean": [float(out[c].mean(skipna=True)) for c in out.columns if c.startswith("z_")],
            "std": [float(out[c].std(skipna=True)) for c in out.columns if c.startswith("z_")],
        }
    )
    output.with_suffix(".report.md").write_text(
        "\n".join(
            [
                "# S2 Consensus Micro Interaction Latents",
                "",
                "## Purpose",
                "",
                report["hypothesis"],
                "",
                f"- Output: `{output}`",
                f"- Additive output: `{additive_output}`",
                f"- Rows: `{len(out)}`",
                f"- Feature count: `{report['feature_count']}`",
                f"- Selected consensus columns: `{len(c_cols)}`",
                f"- Selected micro columns: `{len(m_cols)}`",
                "",
                "## Feature Summary",
                "",
                dataframe_to_markdown(stats.head(60)),
            ]
        ),
        encoding="utf-8",
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build S2 consensus/micro-awakening interaction latents.")
    parser.add_argument("--consensus", default="artifacts/domain_sleep_consensus_purity_subject_relative_only_v1.parquet")
    parser.add_argument("--micro", default="artifacts/domain_s2_micro_awake_rolling_sleep_micro_v1.parquet")
    parser.add_argument("--best", default="artifacts/domain_best_late_fusion_v1.parquet")
    parser.add_argument("--output", default="artifacts/domain_s2_consensus_micro_interaction_v1.parquet")
    parser.add_argument("--additive-output", default="artifacts/domain_best_plus_s2_consensus_micro_interaction_v1.parquet")
    parser.add_argument("--consensus-cap", type=int, default=120)
    parser.add_argument("--micro-cap", type=int, default=64)
    parser.add_argument("--keep-per-block", type=int, default=24)
    parser.add_argument("--interaction-top-k", type=int, default=8)
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
