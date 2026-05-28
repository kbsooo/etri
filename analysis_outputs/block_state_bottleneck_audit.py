from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
DATA = ROOT / "data"
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]


def read_csv(name: str) -> pd.DataFrame:
    path = OUT / name
    if not path.exists():
        raise FileNotFoundError(f"required input is missing: {path}")
    return pd.read_csv(path)


def scalar_row(df: pd.DataFrame, key: str, value: str) -> pd.Series:
    rows = df[df[key] == value]
    if rows.empty:
        raise KeyError(f"{value!r} not found in {key!r}")
    return rows.iloc[0]


def safe_float(x: object) -> float:
    if pd.isna(x):
        return float("nan")
    return float(x)


def build_target_detail(
    oracle: pd.DataFrame,
    markov: pd.DataFrame,
    threshold: pd.DataFrame,
    lag: pd.DataFrame,
    hidden_detail: pd.DataFrame,
) -> pd.DataFrame:
    oracle_i = oracle.set_index("model")
    threshold_i = threshold.set_index("model")
    temporal = oracle_i.loc["temporal_base_foldsafe"]
    block_oracle = oracle_i.loc["validation_block_rate_oracle"]
    subject_oracle = oracle_i.loc["full_subject_rate_oracle"]
    leave_one = oracle_i.loc["validation_block_leave_one_oracle"]

    markov_best = markov[markov["model"].eq("pattern_markov")].sort_values("mean").iloc[0]

    detail_rows = []
    for target in TARGETS:
        lag_target = lag[lag["target"].eq(target)].set_index("lag")
        hd_target = hidden_detail[hidden_detail["target"].eq(target)].set_index("method")
        subject_hidden = safe_float(hd_target.loc["subject_mean", "target_logloss"]) if "subject_mean" in hd_target.index else np.nan
        endpoint_hidden = (
            safe_float(hd_target.loc["endpoint_local_nonoverlap", "target_logloss"])
            if "endpoint_local_nonoverlap" in hd_target.index
            else np.nan
        )
        detail_rows.append(
            {
                "target": target,
                "temporal_base": safe_float(temporal[target]),
                "validation_block_rate_oracle": safe_float(block_oracle[target]),
                "full_subject_rate_oracle": safe_float(subject_oracle[target]),
                "leave_one_in_block_oracle": safe_float(leave_one[target]),
                "oracle_gain_temporal_to_block": safe_float(temporal[target] - block_oracle[target]),
                "block_state_gap_after_subject_identity": safe_float(subject_oracle[target] - block_oracle[target]),
                "subject_identity_gain": safe_float(temporal[target] - subject_oracle[target]),
                "best_markov": safe_float(markov_best[target]),
                "best_markov_delta_vs_temporal": safe_float(markov_best[target] - temporal[target]),
                "nested_threshold": safe_float(threshold_i.loc["nested_single_threshold", target]),
                "nested_threshold_delta_vs_temporal": safe_float(
                    threshold_i.loc["nested_single_threshold", target] - temporal[target]
                ),
                "cheating_threshold": safe_float(threshold_i.loc["oracle_val_selected_threshold", target]),
                "cheating_threshold_gain_vs_temporal": safe_float(
                    temporal[target] - threshold_i.loc["oracle_val_selected_threshold", target]
                ),
                "hidden_endpoint_logloss": endpoint_hidden,
                "hidden_subject_mean_logloss": subject_hidden,
                "hidden_endpoint_gain_vs_subject_mean": safe_float(subject_hidden - endpoint_hidden),
                "lag1_corr": safe_float(lag_target.loc[1, "corr"]) if 1 in lag_target.index else np.nan,
                "lag7_corr": safe_float(lag_target.loc[7, "corr"]) if 7 in lag_target.index else np.nan,
                "lag1_copy_accuracy": safe_float(lag_target.loc[1, "copy_accuracy"]) if 1 in lag_target.index else np.nan,
            }
        )
    return pd.DataFrame(detail_rows)


def build_block_topology(blocks: pd.DataFrame) -> pd.DataFrame:
    sub = blocks[blocks["split"].eq("submission")].copy()
    train = blocks[blocks["split"].eq("train")].copy()
    surrounded = sub["prev_train_gap_days"].notna() & sub["next_train_gap_days"].notna()
    one_sided = sub["prev_train_gap_days"].notna() ^ sub["next_train_gap_days"].notna()

    patterns = (
        blocks.groupby("subject_id", sort=True)
        .apply(lambda g: " ".join(g["split"].str[0].str.upper() + g["n"].astype(str)))
        .rename("split_pattern")
        .reset_index()
    )
    patterns.to_csv(OUT / "block_state_bottleneck_subject_patterns.csv", index=False)

    return pd.DataFrame(
        [
            {
                "metric": "subjects",
                "value": float(blocks["subject_id"].nunique()),
                "interpretation": "same-subject train/test sharing is real",
            },
            {
                "metric": "all_blocks",
                "value": float(len(blocks)),
                "interpretation": "timeline is block-interleaved",
            },
            {
                "metric": "train_blocks",
                "value": float(len(train)),
                "interpretation": "known blocks that can provide context",
            },
            {
                "metric": "submission_blocks",
                "value": float(len(sub)),
                "interpretation": "hidden block-rate targets to infer",
            },
            {
                "metric": "submission_rows",
                "value": float(sub["n"].sum()),
                "interpretation": "rows affected by hidden block state",
            },
            {
                "metric": "submission_blocks_with_two_train_flanks",
                "value": float(surrounded.sum()),
                "interpretation": "boundary context is often present but not sufficient",
            },
            {
                "metric": "submission_blocks_with_one_train_flank",
                "value": float(one_sided.sum()),
                "interpretation": "partial context blocks remain common",
            },
            {
                "metric": "submission_block_median_rows",
                "value": float(sub["n"].median()),
                "interpretation": "target should be block-rate/count, not only row label",
            },
            {
                "metric": "submission_block_max_rows",
                "value": float(sub["n"].max()),
                "interpretation": "large hidden blocks create high logloss leverage",
            },
            {
                "metric": "submission_block_mean_rows",
                "value": float(sub["n"].mean()),
                "interpretation": "average hidden segment is non-trivial",
            },
        ]
    )


def build_summary(
    oracle: pd.DataFrame,
    markov: pd.DataFrame,
    threshold: pd.DataFrame,
    hidden_summary: pd.DataFrame,
    structured_public: pd.DataFrame,
    topology: pd.DataFrame,
    target_detail: pd.DataFrame,
) -> pd.DataFrame:
    oracle_i = oracle.set_index("model")
    temporal = safe_float(oracle_i.loc["temporal_base_foldsafe", "mean"])
    block_oracle = safe_float(oracle_i.loc["validation_block_rate_oracle", "mean"])
    subject_oracle = safe_float(oracle_i.loc["full_subject_rate_oracle", "mean"])
    leave_one = safe_float(oracle_i.loc["validation_block_leave_one_oracle", "mean"])
    markov_best = markov[markov["model"].eq("pattern_markov")].sort_values("mean").iloc[0]
    threshold_i = threshold.set_index("model")
    nested_threshold = safe_float(threshold_i.loc["nested_single_threshold", "mean"])
    cheating_threshold = safe_float(threshold_i.loc["oracle_val_selected_threshold", "mean"])
    hidden_best = hidden_summary.sort_values("weighted_logloss").iloc[0]
    hidden_subject = scalar_row(hidden_summary, "method", "subject_mean")
    structured_best = structured_public.sort_values("loocv_mae").iloc[0]
    two_flank_blocks = topology[topology["metric"].eq("submission_blocks_with_two_train_flanks")]["value"].iloc[0]
    sub_blocks = topology[topology["metric"].eq("submission_blocks")]["value"].iloc[0]

    oracle_gap = temporal - block_oracle
    subject_identity_gain = temporal - subject_oracle
    remaining_after_subject = subject_oracle - block_oracle
    hidden_endpoint_gain = safe_float(hidden_subject["weighted_logloss"] - hidden_best["weighted_logloss"])

    rows = [
        {
            "claim": "block_rate_oracle_reaches_0p5_range",
            "value": block_oracle,
            "reference": "breakthrough_oracle_bounds.csv",
            "interpretation": "0.54 is structurally possible if hidden block rates are identified",
        },
        {
            "claim": "temporal_to_block_oracle_gap",
            "value": oracle_gap,
            "reference": "breakthrough_oracle_bounds.csv",
            "interpretation": "main missing signal is block-rate/state, not row smoothing",
        },
        {
            "claim": "subject_identity_explains_fraction_of_oracle_gap",
            "value": subject_identity_gain / oracle_gap,
            "reference": "breakthrough_oracle_bounds.csv",
            "interpretation": "subject prior helps but leaves most block-local state unexplained",
        },
        {
            "claim": "remaining_gap_after_full_subject_oracle",
            "value": remaining_after_subject,
            "reference": "breakthrough_oracle_bounds.csv",
            "interpretation": "static user identity is not enough",
        },
        {
            "claim": "markov_best_delta_vs_temporal",
            "value": safe_float(markov_best["mean"] - temporal),
            "reference": "breakthrough_markov_results.csv",
            "interpretation": "label-state transition dynamics do not recover hidden block rates",
        },
        {
            "claim": "nested_threshold_delta_vs_temporal",
            "value": nested_threshold - temporal,
            "reference": "breakthrough_threshold_results.csv",
            "interpretation": "single-feature sensor thresholds do not transfer under nested selection",
        },
        {
            "claim": "cheating_threshold_gain_vs_temporal",
            "value": temporal - cheating_threshold,
            "reference": "breakthrough_threshold_results.csv",
            "interpretation": "feature matrix contains fold-specific slices, but selection does not generalize",
        },
        {
            "claim": "endpoint_reconstruction_gain_vs_subject_mean",
            "value": hidden_endpoint_gain,
            "reference": "hidden_block_rate_reconstruction_summary.csv",
            "interpretation": "known block flanks recover only a small part of the needed block-state gap",
        },
        {
            "claim": "endpoint_gain_fraction_of_oracle_gap",
            "value": hidden_endpoint_gain / oracle_gap,
            "reference": "hidden_block_rate_reconstruction_summary.csv",
            "interpretation": "current endpoint pseudo-hidden method captures only a small fraction of oracle headroom",
        },
        {
            "claim": "leave_one_in_block_delta_vs_temporal",
            "value": leave_one - temporal,
            "reference": "breakthrough_oracle_bounds.csv",
            "interpretation": "block-rate latent is useful as a target representation; rowwise neighbor labels are noisy",
        },
        {
            "claim": "two_train_flank_submission_block_fraction",
            "value": two_flank_blocks / sub_blocks,
            "reference": "breakthrough_split_blocks.csv",
            "interpretation": "context exists for most hidden blocks, so failure is context interpretation rather than no context",
        },
        {
            "claim": "best_structured_public_mask_loocv_mae",
            "value": safe_float(structured_best["loocv_mae"]),
            "reference": "structured_public_subset_feasibility_summary.csv",
            "interpretation": "simple public-subset mask recovery is too noisy to choose candidates",
        },
        {
            "claim": "mean_lag1_target_corr",
            "value": safe_float(target_detail["lag1_corr"].mean()),
            "reference": "data_dissection_label_lag_autocorr.csv",
            "interpretation": "short-lag autocorrelation exists but is far weaker than block-rate oracle headroom",
        },
    ]
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame) -> str:
    display = df.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda x: "" if pd.isna(x) else f"{float(x):.6f}")
        else:
            display[col] = display[col].astype(str)
    cols = list(display.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in display.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def write_report(summary: pd.DataFrame, target_detail: pd.DataFrame, topology: pd.DataFrame) -> None:
    summary_lookup = summary.set_index("claim")["value"].to_dict()
    target_compact = target_detail[
        [
            "target",
            "oracle_gain_temporal_to_block",
            "block_state_gap_after_subject_identity",
            "subject_identity_gain",
            "best_markov_delta_vs_temporal",
            "nested_threshold_delta_vs_temporal",
            "hidden_endpoint_gain_vs_subject_mean",
            "lag1_corr",
        ]
    ].copy()

    lines = [
        "# Block-State Bottleneck Audit",
        "",
        "## Question",
        "",
        "Is the 0.577439 plateau caused by lack of row-level features, or by failure to identify hidden subject/block target-rate states?",
        "",
        "## Core Findings",
        "",
        f"- Validation block-rate oracle mean LogLoss: `{summary_lookup['block_rate_oracle_reaches_0p5_range']:.6f}`.",
        f"- Temporal-to-block-rate oracle gap: `{summary_lookup['temporal_to_block_oracle_gap']:.6f}`.",
        f"- Full subject identity explains only `{summary_lookup['subject_identity_explains_fraction_of_oracle_gap']:.3f}` of that gap.",
        f"- Remaining gap after full subject-rate oracle: `{summary_lookup['remaining_gap_after_full_subject_oracle']:.6f}`.",
        f"- Best Markov transition model is worse than temporal by `{summary_lookup['markov_best_delta_vs_temporal']:.6f}`.",
        f"- Nested single-feature threshold is worse than temporal by `{summary_lookup['nested_threshold_delta_vs_temporal']:.6f}`.",
        f"- Validation-selected cheating threshold improves by `{summary_lookup['cheating_threshold_gain_vs_temporal']:.6f}`, proving fold-specific slices exist but do not transfer.",
        f"- Endpoint pseudo-hidden block reconstruction gains only `{summary_lookup['endpoint_reconstruction_gain_vs_subject_mean']:.6f}` over subject mean.",
        f"- Submission blocks with two train flanks: `{summary_lookup['two_train_flank_submission_block_fraction']:.3f}` of hidden blocks.",
        f"- Best simple structured public mask LOO MAE: `{summary_lookup['best_structured_public_mask_loocv_mae']:.9f}`.",
        "",
        "## Target-Level Stress",
        "",
        markdown_table(target_compact.round(6)),
        "",
        "## Block Topology",
        "",
        markdown_table(topology.round(6)),
        "",
        "## Interpretation",
        "",
        "The strongest 0.5-range path is not another row-level model. The oracle that knows validation block rates reaches the required range, while subject identity, Markov transitions, endpoint labels, and nested one-feature rules fail to reconstruct those rates.",
        "",
        "This makes the hidden state more specific than user prior and more stable than row label transitions: it is a block-level rate/count latent. JEPA-style work should therefore predict large block target representations from sparse context, not reconstruct raw features or add another row classifier.",
        "",
        "## Decision",
        "",
        "- Strengthen the block-state bottleneck hypothesis.",
        "- Keep current improvement submission gate closed.",
        "- Next useful representation experiment: context = subject train-block summaries + overnight/raw measurement-process context; target = held-out block rate vector; energy = block-rate prediction residual plus geometry/isotropy diagnostics.",
        "- Do not repeat simple Markov, endpoint propagation, one-feature threshold, or simple public-mask recovery without a new independent anchor.",
        "",
    ]
    (OUT / "block_state_bottleneck_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    oracle = read_csv("breakthrough_oracle_bounds.csv")
    markov = read_csv("breakthrough_markov_results.csv")
    threshold = read_csv("breakthrough_threshold_results.csv")
    blocks = read_csv("breakthrough_split_blocks.csv")
    lag = read_csv("data_dissection_label_lag_autocorr.csv")
    hidden_summary = read_csv("hidden_block_rate_reconstruction_summary.csv")
    hidden_detail = read_csv("hidden_block_rate_reconstruction_target_detail.csv")
    structured_public = read_csv("structured_public_subset_feasibility_summary.csv")

    topology = build_block_topology(blocks)
    target_detail = build_target_detail(oracle, markov, threshold, lag, hidden_detail)
    summary = build_summary(oracle, markov, threshold, hidden_summary, structured_public, topology, target_detail)

    summary.to_csv(OUT / "block_state_bottleneck_summary.csv", index=False)
    target_detail.to_csv(OUT / "block_state_bottleneck_target_detail.csv", index=False)
    topology.to_csv(OUT / "block_state_bottleneck_topology.csv", index=False)
    write_report(summary, target_detail, topology)

    print("wrote:")
    print(OUT / "block_state_bottleneck_summary.csv")
    print(OUT / "block_state_bottleneck_target_detail.csv")
    print(OUT / "block_state_bottleneck_topology.csv")
    print(OUT / "block_state_bottleneck_subject_patterns.csv")
    print(OUT / "block_state_bottleneck_report.md")


if __name__ == "__main__":
    main()
