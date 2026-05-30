#!/usr/bin/env python3
"""E247: materialize the strongest E246 feature-NN1 smoothing selector.

E246 changed the status of the feature-NN1 JEPA idea from "supportive
diagnostic" to "candidate generator": a non-clone selector built only from
directed feature-nearest-neighbor Q3 smoothing passed the E237-like stress gate.

This script materializes exactly one candidate, audits schema/delta integrity,
and writes a compact report. It does not use public LB.
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


EPS = 1.0e-12
Q3_IDX = TARGETS.index("Q3")
SUMMARY_IN = OUT / "e246_feature_nn1_smoothing_selector_summary.csv"
ROWS_IN = OUT / "e246_feature_nn1_smoothing_selector_rows.csv"
REPORT_OUT = OUT / "e247_feature_nn1_smoothing_materializer_report.md"
AUDIT_OUT = OUT / "e247_feature_nn1_smoothing_materializer_audit.csv"


def clip_prob(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, dtype=np.float64), 1.0e-6, 1.0 - 1.0e-6)


def md_table(frame: pd.DataFrame, cols: list[str] | None = None, n: int = 40, floatfmt: str = ".9f") -> str:
    if frame.empty:
        return "_empty_"
    view = frame if cols is None else frame[[c for c in cols if c in frame.columns]]
    return e138.md_table(view.head(n), floatfmt)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def choose_selector(summary: pd.DataFrame) -> pd.Series:
    feature = summary[
        ~summary["rule_family"].eq("control")
        & summary["e237_like_gate"].astype(bool)
        & (summary["overlap_e237"].fillna(999).astype(float) < 20)
    ].copy()
    if feature.empty:
        raise RuntimeError("no non-clone feature-NN1 E237-like gate pass to materialize")
    return feature.sort_values(
        ["e237_like_score", "adverse_reduction_vs_e224", "support_gain_vs_e224"],
        ascending=[False, False, False],
    ).iloc[0]


def materialize(sample: pd.DataFrame, pred: np.ndarray, selector_id: str) -> Path:
    digest = hashlib.sha1(np.round(pred, 10).tobytes()).hexdigest()[:8]
    safe_id = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in selector_id)[:52]
    out_path = OUT / f"submission_e247_featnn1_{safe_id}_{digest}.csv"
    out = sample[KEYS].copy()
    out[TARGETS] = clip_prob(pred)
    out.to_csv(out_path, index=False)
    return out_path


def pair_smoothing_delta(rows: pd.DataFrame, selected: np.ndarray) -> dict[str, Any]:
    sorted_rows = rows.sort_values("row_idx").reset_index(drop=True)
    e224 = sorted_rows["e224_q3_logit"].to_numpy(dtype=np.float64)
    e154 = sorted_rows["e154_q3_logit"].to_numpy(dtype=np.float64)
    nn = sorted_rows["nn_row_idx"].to_numpy(dtype=int)
    candidate = e224.copy()
    candidate[selected] = e154[selected]
    changed = np.zeros(len(e224), dtype=bool)
    changed[selected] = True
    affected = changed | changed[nn]
    before = np.abs(e224 - e224[nn])
    after = np.abs(candidate - candidate[nn])
    return {
        "global_pair_abs_delta": float(after.mean() - before.mean()),
        "affected_pair_abs_delta": float(after[affected].mean() - before[affected].mean()) if affected.any() else np.nan,
        "affected_pair_count": int(affected.sum()),
        "positive_pair_delta_share": float((after[affected] - before[affected] > 0).mean()) if affected.any() else np.nan,
    }


def main() -> None:
    if not SUMMARY_IN.exists() or not ROWS_IN.exists():
        e246.main()
    summary = pd.read_csv(SUMMARY_IN)
    selector = choose_selector(summary)
    selector_id = str(selector["candidate_id"])
    rows = pd.read_csv(ROWS_IN)
    selected = np.fromiter((int(x) for x in str(selector["row_idx_list"]).split()), dtype=int)

    sample = load_sub(A2C8).sort_values(KEYS).reset_index(drop=True)
    e154 = e230.load_prob(e230.E154_FILE, sample)
    e224 = e230.load_prob(e230.E224_FILE, sample)
    pred = e246.apply_q3_drop(e224, e154, selected)
    out_path = materialize(sample, pred, selector_id)

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
            "new_prob_e247": written[TARGETS].to_numpy(dtype=float)[changed_rows, changed_targets],
        }
    )

    selected_rows = rows[rows["row_idx"].isin(set(selected.tolist()))].copy()
    smoothing = pair_smoothing_delta(rows, selected)
    audit = pd.DataFrame(
        [
            {
                "file_name": out_path.name,
                "selector_id": selector_id,
                "sha256": sha256_file(out_path),
                "exact_columns": exact_columns,
                "exact_keys": exact_keys,
                "finite_probs": finite_probs,
                "in_bounds": in_bounds,
                "changed_cells_vs_e224": int(diff.sum()),
                "changed_q3_vs_e224": int((changed["target"] == "Q3").sum()) if not changed.empty else 0,
                "changed_other_targets_vs_e224": int((changed["target"] != "Q3").sum()) if not changed.empty else 0,
                **{k: selector[k] for k in selector.index if k in {
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
                }},
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
        "# E247 Feature-NN1 Smoothing Materializer",
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
        md_table(selected_rows.sort_values("single_row_smooth_gain_sum", ascending=False), row_cols, n=50),
        "",
        "## Submission Interpretation",
        "",
        "- This file bets that the recoverable hidden law is not the masked-family S2 translator from E216, but Q3 local consistency under the E207 broad-stage2 feature-nearest-neighbor representation.",
        "- A public improvement would promote feature-NN1 JEPA from diagnostic geometry to actionable selector.",
        "- A public loss would mean the E246 local stress gate is still too close to calibration-prior smoothing and not enough to identify public-safe labels.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print(audit[top_cols].to_string(index=False))
    print(f"wrote: {out_path}")
    print(f"wrote: {REPORT_OUT}")


if __name__ == "__main__":
    main()
