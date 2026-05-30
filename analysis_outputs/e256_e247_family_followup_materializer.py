#!/usr/bin/env python3
"""E256: materialize the first post-E247 feature-NN1 follow-up.

E247's public win promotes feature-NN1 Q3 smoothing from diagnostic geometry to
the current public-positive JEPA mechanism. The first follow-up should not be a
blind sweep. E255 ranks `top50_amp_then_smooth25` as the sharpest next sensor:
it keeps the smoothing idea but constrains it to high-amplitude Q3 cells.

Question:
    Did public like broad feature-neighbor smoothness, or only high-amplitude
    smooth cells?

No public LB is used here and exactly one submission file is created.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
if str(OUT) not in sys.path:
    sys.path.insert(0, str(OUT))

from public_anchor_bottleneck_decomposition import A2C8, KEYS, TARGETS, load_sub  # noqa: E402
import e138_blocktarget_vetonull_overlap_probe as e138  # noqa: E402
import e230_e224_support_tail_prune_audit as e230  # noqa: E402
import e246_feature_nn1_smoothing_selector_ablation as e246  # noqa: E402
import e247_feature_nn1_smoothing_materializer as e247  # noqa: E402


SELECTOR_ID = "top50_amp_then_smooth25"
SUMMARY_IN = OUT / "e246_feature_nn1_smoothing_selector_summary.csv"
ROWS_IN = OUT / "e246_feature_nn1_smoothing_selector_rows.csv"
REPORT_OUT = OUT / "e256_e247_family_followup_materializer_report.md"
AUDIT_OUT = OUT / "e256_e247_family_followup_materializer_audit.csv"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def sha1_pred(pred: np.ndarray) -> str:
    return hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_rows(value: Any) -> np.ndarray:
    return np.fromiter((int(x) for x in str(value).split() if str(x).strip()), dtype=int)


def main() -> None:
    if not SUMMARY_IN.exists() or not ROWS_IN.exists():
        e246.main()
    summary = pd.read_csv(SUMMARY_IN)
    selected_row = summary[summary["candidate_id"].eq(SELECTOR_ID)]
    if selected_row.empty:
        raise RuntimeError(f"selector not found: {SELECTOR_ID}")
    selector = selected_row.iloc[0]
    row_idx = parse_rows(selector["row_idx_list"])

    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    e154 = e230.load_prob(e230.E154_FILE, sample)
    e224 = e230.load_prob(e230.E224_FILE, sample)
    pred = e246.apply_q3_drop(e224, e154, row_idx)

    out_path = OUT / f"submission_e256_featnn1_{SELECTOR_ID}_{sha1_pred(pred)}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(out_path, index=False)

    written = pd.read_csv(out_path)
    sample_template = pd.read_csv(ROOT / "data" / "ch2026_submission_sample.csv")
    exact_columns = list(written.columns) == list(sample_template.columns)
    exact_keys = written[KEYS].astype(str).equals(sample_template[KEYS].astype(str))
    probs = written[TARGETS].to_numpy(dtype=float)
    finite_probs = bool(np.isfinite(probs).all())
    in_bounds = bool(((probs >= 0.0) & (probs <= 1.0)).all())

    e224_df = load_sub(e230.E224_FILE, sample).sort_values(KEYS).reset_index(drop=True)
    diff = np.abs(written[TARGETS].to_numpy(dtype=float) - e224_df[TARGETS].to_numpy(dtype=float)) > 1.0e-12
    changed_rows, changed_targets = np.where(diff)
    changed = pd.DataFrame(
        {
            "row_idx": changed_rows,
            "target": [TARGETS[i] for i in changed_targets],
            "old_prob_e224": e224_df[TARGETS].to_numpy(dtype=float)[changed_rows, changed_targets],
            "new_prob_e256": written[TARGETS].to_numpy(dtype=float)[changed_rows, changed_targets],
        }
    )

    rows = pd.read_csv(ROWS_IN)
    selected_rows = rows[rows["row_idx"].isin(set(row_idx.tolist()))].copy()
    smoothing = e247.pair_smoothing_delta(rows, row_idx)
    audit = pd.DataFrame(
        [
            {
                "file_name": out_path.name,
                "selector_id": SELECTOR_ID,
                "sha256": sha256_file(out_path),
                "exact_columns": exact_columns,
                "exact_keys": exact_keys,
                "finite_probs": finite_probs,
                "in_bounds": in_bounds,
                "changed_cells_vs_e224": int(diff.sum()),
                "changed_q3_vs_e224": int((changed["target"] == "Q3").sum()) if not changed.empty else 0,
                "changed_other_targets_vs_e224": int((changed["target"] != "Q3").sum()) if not changed.empty else 0,
                "row_idx_list": " ".join(map(str, row_idx.tolist())),
                **{
                    k: selector[k]
                    for k in selector.index
                    if k
                    in {
                        "expected_loss_vs_e224",
                        "adverse_reduction_vs_e224",
                        "support_gain_vs_e224",
                        "actual_expected_delta_vs_e224",
                        "actual_adverse_reduction_vs_e224",
                        "actual_support_gain_vs_e224",
                        "q3_top1_over_abs_expected",
                        "q3_adverse_delta",
                        "selected_smooth_gain_sum",
                        "overlap_e237",
                        "overlap_e230_swing25",
                        "overlap_e230_risk21",
                        "overlap_amp_top25",
                        "e237_like_score",
                    }
                },
                **smoothing,
            }
        ]
    )
    audit.to_csv(AUDIT_OUT, index=False)

    top_cols = [
        "file_name",
        "selector_id",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "q3_top1_over_abs_expected",
        "selected_smooth_gain_sum",
        "global_pair_abs_delta",
        "affected_pair_abs_delta",
        "overlap_e237",
        "overlap_e230_swing25",
        "overlap_amp_top25",
        "changed_cells_vs_e224",
        "sha256",
    ]
    row_cols = [
        "row_idx",
        "subject_id",
        "lifelog_date",
        "nn_row_idx",
        "nn_dist",
        "rollback_amp_abs",
        "single_row_smooth_gain_sum",
        "e237_drop",
        "e230_swing25",
        "e230_risk21",
        "amp_rank",
        "smooth_sum_rank",
    ]
    lines = [
        "# E256 E247-Family Follow-Up Materializer",
        "",
        "## Question",
        "",
        "Did public like broad feature-neighbor Q3 smoothness, or only high-amplitude smooth cells?",
        "",
        "## Selected Candidate",
        "",
        md_table(audit, top_cols, n=1),
        "",
        "## Integrity",
        "",
        f"- exact sample columns: `{exact_columns}`",
        f"- exact sample key order: `{exact_keys}`",
        f"- finite probabilities: `{finite_probs}`",
        f"- probabilities in [0, 1]: `{in_bounds}`",
        f"- changed cells vs E224: `{int(diff.sum())}`, Q3-only: `{int((changed['target'] == 'Q3').sum()) if not changed.empty else 0}`",
        "",
        "## Selected Rows",
        "",
        md_table(selected_rows.sort_values("single_row_smooth_gain_sum", ascending=False), row_cols, n=40),
        "",
        "## Public Feedback Decoder",
        "",
        "- If E256 beats E247, public prefers high-amplitude smoothing cells and E247 included too much broad smoothness.",
        "- If E256 is close but worse, E247's broader top34 smoothing cells are probably carrying real public signal.",
        "- If E256 fails hard, E247 may depend on a nonlocal interaction between the E224 body and the exact top34 smoothness set.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(audit[top_cols].to_string(index=False))
    print(f"wrote: {out_path}")
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
