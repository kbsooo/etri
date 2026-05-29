#!/usr/bin/env python3
"""E87 decompose E86 public risk into Q2 add-back and overstep axes.

E86 is the current highest-upside local candidate, but its public risk is
ambiguous: it adds Q2 back to the E85 S1/S2/S3 law and uses shrink 1.25. This
probe materializes contrast candidates that isolate those risks without
introducing a new model family.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"

if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import KEYS, TARGETS  # noqa: E402
import e83_q2s3_energy_structural_gate_scan as e83  # noqa: E402
import e86_e85_target_prune_robustness as e86  # noqa: E402
import mixmin_hard_raw_world_probe as e56  # noqa: E402


SCAN_OUT = OUT / "e87_e86_risk_decomposition_scan.csv"
CHOICES_OUT = OUT / "e87_e86_risk_decomposition_choices.csv"
REPORT_OUT = OUT / "e87_e86_risk_decomposition_report.md"


def exact_pick(scan: pd.DataFrame, **criteria: Any) -> pd.Series | None:
    mask = pd.Series(True, index=scan.index)
    for key, value in criteria.items():
        if isinstance(value, float):
            mask &= np.isclose(scan[key].astype(float), value)
        else:
            mask &= scan[key].eq(value)
    rows = scan[mask].copy()
    if rows.empty:
        return None
    rows = rows.sort_values(["all_delta_vs_mixmin", "set_inverse_top_delta_vs_mixmin"], ascending=[True, True])
    return rows.iloc[0]


def best_pick(scan: pd.DataFrame, name: str) -> pd.Series:
    strict = scan[scan["strict_gate"].fillna(False).astype(bool)].copy()
    if name == "e86_frontier":
        rows = strict[
            strict["keep_targets"].eq("Q2,S1,S2,S3")
            & strict["selection_mode"].eq("top")
            & strict["aggregator"].eq("mean")
            & strict["selected_n"].eq(40)
            & np.isclose(strict["shrink"].astype(float), 1.25)
        ]
        if len(rows):
            return rows.sort_values("all_delta_vs_mixmin").iloc[0]
    if name == "noq2_source_diverse":
        row = exact_pick(
            strict,
            keep_targets="S1,S2,S3",
            selection_mode="top",
            selected_n=40,
            aggregator="mean",
            shrink=1.25,
        )
        if row is not None:
            return row
        rows = strict[strict["keep_targets"].eq("S1,S2,S3") & strict["unique_source_files"].ge(10)]
        return rows.sort_values(["unique_source_files", "all_delta_vs_mixmin"], ascending=[False, True]).iloc[0]
    if name == "q2_no_overstep":
        row = exact_pick(
            strict,
            keep_targets="Q2,S1,S2,S3",
            selection_mode="top",
            selected_n=40,
            aggregator="mean",
            shrink=1.00,
        )
        if row is not None:
            return row
        rows = strict[
            strict["keep_targets"].eq("Q2,S1,S2,S3")
            & strict["unique_source_files"].ge(10)
            & strict["shrink"].le(1.00)
        ]
        return rows.sort_values(["unique_source_files", "all_delta_vs_mixmin"], ascending=[False, True]).iloc[0]
    if name == "inverse_top_prior":
        rows = strict[
            strict["unique_source_files"].ge(10)
            & strict["set_inverse_top_delta_vs_mixmin"].lt(-1.0e-5)
            & strict["set_raw05_compatible_delta_vs_mixmin"].lt(0.0)
            & strict["set_all_sign_delta_vs_mixmin"].lt(0.0)
        ]
        return rows.sort_values(
            ["set_inverse_top_delta_vs_mixmin", "all_delta_vs_mixmin"],
            ascending=[True, True],
        ).iloc[0]
    raise ValueError(f"unknown pick: {name}")


def write_submission(sample: pd.DataFrame, pred: np.ndarray, prefix: str, tag: str) -> Path:
    out = sample[KEYS].copy()
    out[TARGETS] = pred
    path = OUT / f"{prefix}_{tag[-8:]}.csv"
    out.to_csv(path, index=False)
    return path


def materialize_choices(sample: pd.DataFrame, preds: list[np.ndarray], scan: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    choice_defs = [
        (
            "e86_frontier",
            "already_materialized",
            "Current highest-upside E86: Q2 add-back plus shrink 1.25.",
            None,
        ),
        (
            "noq2_source_diverse",
            "submission_e87_noq2_source_consensus",
            "Q2 add-back removed while keeping source-diverse S1/S2/S3 consensus and shrink 1.25.",
            "If this beats E86 public, Q2 add-back was the likely contaminant.",
        ),
        (
            "q2_no_overstep",
            "submission_e87_q2_nooverstep_consensus",
            "Q2 kept, but shrink reduced from 1.25 to 1.00 to isolate overstep risk.",
            "If this beats E86 public, consensus direction was right but 1.25 overstepped calibration.",
        ),
        (
            "inverse_top_prior",
            "submission_e87_inverse_top_prior_consensus",
            "Chooses the strict source-diverse row with strongest inverse-top support.",
            "If this beats E86/E85, public is closer to inverse-top target geometry than all-delta geometry.",
        ),
    ]
    for role, prefix, intent, public_read in choice_defs:
        rec = best_pick(scan, role)
        pred = preds[int(rec["pred_index"])]
        path: Path | None
        if prefix is None or prefix == "already_materialized":
            path = OUT / "submission_e86_e85_consensus_a3f7c96f.csv"
        else:
            path = write_submission(sample, pred, prefix, str(rec["tag"]))
        item = rec.to_dict()
        item.update(
            {
                "choice_role": role,
                "submission_file": path.name if path is not None else "",
                "intent": intent,
                "public_read": public_read or "",
            }
        )
        rows.append(item)
    return pd.DataFrame(rows)


def write_report(choices: pd.DataFrame) -> None:
    cols = [
        "choice_role",
        "submission_file",
        "keep_targets",
        "selection_mode",
        "selected_n",
        "unique_source_files",
        "unique_seed_ranks",
        "aggregator",
        "shrink",
        "all_delta_vs_mixmin",
        "set_inverse_top_delta_vs_mixmin",
        "set_raw05_compatible_delta_vs_mixmin",
        "set_all_sign_delta_vs_mixmin",
        "hidden_q2s3_mean_minus_base",
        "world_support_minus_base",
        "raw_energy_q_p90_minus_base",
        "block_q2s3_beats_base_rate",
        "block_q2s3_tail_safe_rate",
    ]
    lines = [
        "# E87 E86 Risk Decomposition",
        "",
        "## Observe",
        "",
        "E86 is locally stronger than E85, but its public failure modes are not separated: it both adds Q2 back and uses shrink `1.25`.",
        "",
        "## Wonder",
        "",
        "If E86 misses public, is the problem Q2 add-back, overstep amplitude, or the whole inverse-top target-prune worldview?",
        "",
        "## Method",
        "",
        "- Rebuild the deterministic E86 consensus pool.",
        "- Select three contrast candidates without changing model family: no-Q2, no-overstep, and inverse-top-prioritized.",
        "- Keep all candidates strict/deployable under the same E86 combo, hidden/world/block, raw-energy, and tail stress.",
        "",
        "## Choices",
        "",
        e56.markdown_table(choices[cols]),
        "",
        "## Public Interpretation",
        "",
        "- If `submission_e86_e85_consensus_a3f7c96f.csv` improves, source-consensus target-prune remains the highest-upside law.",
        "- If E86 worsens but `submission_e87_noq2_source_consensus_*` improves, Q2 add-back was the contaminating axis.",
        "- If E86 worsens but `submission_e87_q2_nooverstep_consensus_*` improves, shrink `1.25` overstepped calibration while direction stayed useful.",
        "- If `submission_e87_inverse_top_prior_consensus_*` improves, public is closer to inverse-top target geometry than all-delta geometry.",
        "- If all fail, E85/E86 target-prune was likely a local combo-world artifact and row/block or all-sign/raw05-compatible alternatives should reopen.",
        "",
        "## Decision",
        "",
        "Do not promote E87 above E86 before public feedback. E87 exists to reduce interpretation entropy after the next public observation.",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sample, mixmin, labels, worlds, views, state, e85_rows, e85_preds, e85_scan = e86.rebuild_e85_predictions()
    rows, preds = e86.build_consensus_candidates(e85_rows, e85_preds, e85_scan, mixmin)
    scan = e83.score_candidate_rows(rows, preds, sample, mixmin, labels, worlds, views, state)
    choices = materialize_choices(sample, preds, scan)
    scan.to_csv(SCAN_OUT, index=False)
    choices.to_csv(CHOICES_OUT, index=False)
    write_report(choices)
    print(
        {
            "scan_rows": int(len(scan)),
            "strict": int(scan["strict_gate"].sum()),
            "choices": choices[["choice_role", "submission_file"]].to_dict("records"),
        }
    )


if __name__ == "__main__":
    main()
