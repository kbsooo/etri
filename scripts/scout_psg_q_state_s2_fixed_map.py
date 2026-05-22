from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


TARGET_COLUMNS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]

BASE_TARGET_MAP = {
    "Q1": "boundary_target_map__absolute__c0.03_b0.2",
    "Q2": "best_plus_scc_rolling__absolute__c0.3_b0.2",
    "Q3": "best_plus_cc_recovery__deviation__c0.3_b0.2",
    "S1": "best_plus_wai_sleep_recovery_interaction__absolute_plus_deviation__c0.3_b0.2",
    "S2": "scp_subject_relative_only__absolute_plus_deviation__c0.03_b0.2",
    "S3": "best_plus_sot_micro_subject_relative_only__absolute_plus_deviation__c0.3_b0.2",
    "S4": "best_plus_rr_coverage_rhythm__absolute_plus_deviation__c0.3_b0.2",
}

VARIANTS = {
    "current": {},
    "old_psg_s2_s4": {
        "S2": "psg_q__deviation__c0.1_b0.2",
        "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2",
    },
    "opp_s2_old_s4": {
        "S2": "psg_opp__deviation__c0.3_b0.2",
        "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2",
    },
    "opp_mob_s2_old_s4": {
        "S2": "psg_opp_mob__deviation__c0.1_b0.2",
        "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2",
    },
    "qrel_s2_old_s4": {
        "S2": "best_plus_psg_qrel__absolute__c0.1_b0.2",
        "S4": "psg_core__absolute_plus_deviation__c0.1_b0.2",
    },
    "opp_s2_qcore_s4": {
        "S2": "psg_opp__deviation__c0.3_b0.2",
        "S4": "psg_qcore__absolute_plus_deviation__c0.3_b0.2",
    },
    "opp_mob_s2_qcore_s4": {
        "S2": "psg_opp_mob__deviation__c0.1_b0.2",
        "S4": "psg_qcore__absolute_plus_deviation__c0.3_b0.2",
    },
    "qrel_s2_qcore_s4": {
        "S2": "best_plus_psg_qrel__absolute__c0.1_b0.2",
        "S4": "psg_qcore__absolute_plus_deviation__c0.3_b0.2",
    },
    "qrel_s2_best_plus_qcore_s4": {
        "S2": "best_plus_psg_qrel__absolute__c0.1_b0.2",
        "S4": "best_plus_psg_qcore__absolute_plus_deviation__c0.3_b0.2",
    },
}


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    cols = frame.columns.tolist()
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in frame.itertuples(index=False):
        vals = []
        for value in row:
            vals.append(f"{value:.6f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def evaluate_variant(lookup: dict[tuple[str, str], float], name: str, replacements: dict[str, str]) -> dict[str, object]:
    target_losses = {}
    for target, base_source in BASE_TARGET_MAP.items():
        source = replacements.get(target, base_source)
        key = (source, target)
        if key not in lookup:
            raise KeyError(f"Missing fold loss for {target}: {source}")
        target_losses[target] = lookup[key]
    row = {
        "variant": name,
        "avg_log_loss": sum(target_losses.values()) / len(TARGET_COLUMNS),
        "replacements": json.dumps(replacements, ensure_ascii=False),
    }
    row.update(target_losses)
    return row


def run(args: argparse.Namespace) -> None:
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    losses = pd.read_csv(args.fold_losses)
    mean = losses.groupby(["source", "target"], as_index=False)["loss"].mean()
    lookup = {(row.source, row.target): float(row.loss) for row in mean.itertuples(index=False)}
    rows = [evaluate_variant(lookup, name, replacements) for name, replacements in VARIANTS.items()]
    result = pd.DataFrame(rows).sort_values("avg_log_loss")
    result.to_csv(output_dir / "fixed_map_scout.csv", index=False)
    report = {
        "fold_losses": args.fold_losses,
        "base_target_map": BASE_TARGET_MAP,
        "variants": result.to_dict(orient="records"),
    }
    (output_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown = [
        "# PSG Q-State S2 Fixed Map Scout",
        "",
        "Fixed target-map diagnostic using the current specialist map as the baseline and replacing only S2/S4 with Q-state split probes. This is not source selection; it tests whether the smaller S2 opportunity signal can improve the previous PSG replacement under the same fixed-map accounting.",
        "",
        dataframe_to_markdown(result[["variant", "avg_log_loss", *TARGET_COLUMNS, "replacements"]]),
        "",
        "## Read",
        "",
        "- `opp_s2_*` tests the smaller opportunity-only S2 hypothesis that beat the broad Q-state S2 probe in direct fold means.",
        "- `qcore_s4` tests whether the compact Q-block can replace the earlier PSG core S4 scout.",
        "- If a split variant improves both the fixed map and nested diagnostics, carry it forward; otherwise treat it as OOF selection noise.",
    ]
    (output_dir / "report.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scout fixed S2/S4 substitutions for PSG Q-state split variants.")
    parser.add_argument(
        "--fold-losses",
        default="outputs/domain_all_specialists_plus_psg_q_state_s2_variants_probe_v1/fold_target_losses.csv",
    )
    parser.add_argument("--output-dir", default="outputs/domain_psg_q_state_s2_fixed_map_scout_v1")
    return parser


if __name__ == "__main__":
    run(build_arg_parser().parse_args())
