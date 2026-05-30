#!/usr/bin/env python3
"""E275: q-sleep diary energy amplitude robustness audit.

E274 found the first near-promoted diary-energy candidate:
`q_sleep_subjective_top12`, mean predicted delta -9.8e-5 and p90 -4.878e-5
against E247, just above the strict -5e-5 promotion bar.

This script does not tune for public LB. It tests whether the signal is stable
across a pre-declared amplitude ladder. A single threshold crossing is not a
submission reason; adjacent strict passes with margin are required.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from e272_public_free_candidate_audit import (  # noqa: E402
    CURRENT,
    build_features,
    evaluate_models,
    movement_anatomy,
    score_candidates,
    selected_models,
)
from e274_target_specific_diary_energy_audit import (  # noqa: E402
    AXIS_OUT,
    FEATURE_PATH,
    TARGETS,
    apply_axis_moves,
    short_hash,
)
from public_anchor_bottleneck_decomposition import KEYS, load_sub  # noqa: E402
from public_selector_universe_audit import build_known_and_refs  # noqa: E402


SCAN_OUT = OUT / "e275_q_sleep_diary_energy_amplitude_scan.csv"
SCORE_OUT = OUT / "e275_q_sleep_diary_energy_amplitude_scores.csv"
ANATOMY_OUT = OUT / "e275_q_sleep_diary_energy_amplitude_anatomy.csv"
CELLS_OUT = OUT / "e275_q_sleep_diary_energy_amplitude_cells.csv"
REPORT_OUT = OUT / "e275_q_sleep_diary_energy_amplitude_report.md"


def md_table(frame: pd.DataFrame, n: int = 30, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame.head(n).copy()
    for col in view.columns:
        if pd.api.types.is_float_dtype(view[col]):
            view[col] = view[col].map(lambda x: "" if pd.isna(x) else format(float(x), floatfmt))
    view = view.fillna("")
    headers = [str(c) for c in view.columns]
    rows = [[str(v).replace("\n", " ") for v in row] for row in view.to_numpy()]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(out)


def materialize_ladder() -> tuple[list[str], pd.DataFrame, pd.DataFrame]:
    base = load_sub(CURRENT)
    features = pd.read_parquet(FEATURE_PATH)
    axes = pd.read_csv(AXIS_OUT)
    q_axes = axes[axes["target"].isin(["Q1", "Q2", "Q3"])].copy()
    q_axes = q_axes.sort_values("local_axis_score", ascending=False).head(12).reset_index(drop=True)

    rows: list[dict[str, object]] = []
    cells: list[pd.DataFrame] = []
    files: list[str] = []
    for mult in [0.60, 0.80, 1.00, 1.15, 1.30, 1.45, 1.60]:
        cfg = {
            "candidate_id": f"q_sleep_amp_m{int(mult * 100):03d}",
            "n_axes": 12,
            "top_each": 12,
            "amp": 0.045 * mult,
            "cap": min(0.090, 0.055 * mult),
            "include_diagnostic": True,
            "targets": ["Q1", "Q2", "Q3"],
        }
        out, cell_frame = apply_axis_moves(base, features, q_axes, cfg)
        h = short_hash(out)
        filename = f"submission_e275_{cfg['candidate_id']}_{h}.csv"
        out.to_csv(OUT / filename, index=False)
        files.append(filename)
        rows.append({
            "candidate_id": cfg["candidate_id"],
            "submission_file": filename,
            "amp_mult": mult,
            "amp": cfg["amp"],
            "cap": cfg["cap"],
            "axis_count": len(q_axes),
            "cell_rows": int(len(cell_frame)),
        })
        if not cell_frame.empty:
            cell_frame["submission_file"] = filename
            cell_frame["amp_mult"] = mult
            cells.append(cell_frame)
    scan = pd.DataFrame(rows)
    cell_out = pd.concat(cells, ignore_index=True) if cells else pd.DataFrame()
    scan.to_csv(SCAN_OUT, index=False)
    cell_out.to_csv(CELLS_OUT, index=False)
    return files, scan, cell_out


def audit(files: list[str]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample = load_sub(CURRENT)[KEYS]
    known, refs, ref_vecs = build_known_and_refs(sample)
    all_files = [CURRENT, *files]
    candidates = build_features(all_files, sample, refs, ref_vecs)
    model_df = evaluate_models(known)
    scores = score_candidates(known, candidates, model_df)
    anatomy = movement_anatomy(all_files, sample)
    scores.to_csv(SCORE_OUT, index=False)
    anatomy.to_csv(ANATOMY_OUT, index=False)
    return scores, anatomy, selected_models(model_df)


def write_report(scan: pd.DataFrame, scores: pd.DataFrame, anatomy: pd.DataFrame, selected: pd.DataFrame) -> None:
    merged = scores.merge(scan, left_on="basename", right_on="submission_file", how="left")
    ladder = merged[merged["basename"].str.startswith("submission_e275_", na=False)].sort_values("amp_mult")
    strict = ladder[ladder["strict_promote_gate"].astype(bool)].copy()
    adjacent = False
    if len(strict) >= 2:
        idxs = strict["amp_mult"].to_numpy(dtype=float)
        adjacent = bool(np.any(np.isclose(np.diff(np.sort(idxs)), 0.15) | np.isclose(np.diff(np.sort(idxs)), 0.20)))
    robust_gate = bool(
        len(strict) >= 2
        and adjacent
        and float(strict["pred_delta_vs_current_p90"].min()) <= -0.000065
        and float(strict["pred_beats_current_rate"].min()) >= 0.75
    )

    score_cols = [
        "basename",
        "amp_mult",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p10",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]
    anatomy_cols = [
        "basename",
        "changed_cells_vs_current",
        "changed_rows_vs_current",
        "l1_logit_delta_vs_current",
        "max_abs_prob_delta_vs_current",
    ]
    lines = [
        "# E275 Q-Sleep Diary Energy Amplitude Audit",
        "",
        "## Question",
        "",
        "Is E274's near-promoted Q1/Q2/Q3 diary-energy movement robust across amplitude, or just a selector-threshold accident?",
        "",
        "## Robustness Rule",
        "",
        "A candidate is not submission-worthy unless at least two adjacent amplitude settings pass `strict_promote_gate`, the best p90 delta is <= `-0.000065`, and all strict settings beat current in at least `75%` of scenarios.",
        "",
        "## Selector Reliability",
        "",
        f"- selected E272-style selector models: `{len(selected)}`",
        f"- strict ladder rows: `{len(strict)}`",
        f"- adjacent strict pass: `{adjacent}`",
        f"- robust amplitude gate: `{robust_gate}`",
        "",
        "## Ladder Scores",
        "",
        md_table(ladder[score_cols], n=20),
        "",
        "## Movement Anatomy",
        "",
        md_table(anatomy[anatomy["basename"].str.startswith("submission_e275_", na=False)][anatomy_cols], n=20),
        "",
        "## Decision",
        "",
    ]
    if robust_gate:
        best = ladder.sort_values(["strict_promote_gate", "pred_delta_vs_current_p90", "pred_delta_vs_current_mean"], ascending=[False, True, True]).iloc[0]
        lines.append(f"`{best['basename']}` is promoted by the E275 robustness rule, pending manual review of target/axis anatomy.")
    else:
        lines.append("No E275 q-sleep amplitude is promoted. If a strict row appears, it is not robust enough by the pre-declared adjacent-amplitude rule.")
    lines.extend([
        "",
        "## Files",
        "",
        f"- `{SCAN_OUT.name}`",
        f"- `{SCORE_OUT.name}`",
        f"- `{ANATOMY_OUT.name}`",
        f"- `{CELLS_OUT.name}`",
    ])
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    files, scan, _ = materialize_ladder()
    scores, anatomy, selected = audit(files)
    write_report(scan, scores, anatomy, selected)
    print(REPORT_OUT)
    merged = scores.merge(scan, left_on="basename", right_on="submission_file", how="left")
    print(merged[merged["basename"].str.startswith("submission_e275_", na=False)][[
        "basename",
        "amp_mult",
        "promotion_decision",
        "pred_delta_vs_current_mean",
        "pred_delta_vs_current_p90",
        "pred_beats_current_rate",
        "incremental_bad_axis_vs_current",
    ]].round(9).to_string(index=False))


if __name__ == "__main__":
    main()
