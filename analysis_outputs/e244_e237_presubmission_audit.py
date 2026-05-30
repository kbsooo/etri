from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis_outputs"

KEY = ["subject_id", "sleep_date", "lifelog_date"]
TARGETS = ["Q1", "Q2", "Q3", "S1", "S2", "S3", "S4"]
EXPECTED_COLUMNS = KEY + TARGETS

SAMPLE = DATA / "ch2026_submission_sample.csv"
E237 = OUT / "submission_e237_cell_decisive_all3_latent_no_targetid_hgb_shallow_subject5_risk_q0p10_drop_q3_top25_426424f2.csv"
E224 = OUT / "submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv"
E95 = OUT / "submission_e95_hardtail_541e3973.csv"
SELECTED = OUT / "e237_cell_decisive_jepa_target_selected.csv"

REPORT = OUT / "e244_e237_presubmission_audit_report.md"
SCHEMA_CSV = OUT / "e244_e237_presubmission_schema_audit.csv"
TARGET_DELTA_CSV = OUT / "e244_e237_presubmission_target_delta_audit.csv"
CHANGED_CELLS_CSV = OUT / "e244_e237_presubmission_changed_cells_audit.csv"


def read_submission(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clipped_logit(values: np.ndarray) -> np.ndarray:
    values = np.clip(values.astype(float), 1e-6, 1 - 1e-6)
    return np.log(values / (1 - values))


def audit_schema(sample: pd.DataFrame, sub: pd.DataFrame) -> pd.DataFrame:
    key_cols = KEY
    target_values = sub[TARGETS].to_numpy(dtype=float)
    checks = [
        ("columns_exact", list(sub.columns) == EXPECTED_COLUMNS),
        ("shape_exact_250x10", tuple(sub.shape) == (250, 10)),
        ("key_order_matches_sample", sub[key_cols].astype(str).equals(sample[key_cols].astype(str))),
        ("keys_unique", not sub[key_cols].duplicated().any()),
        ("sample_keys_unique", not sample[key_cols].duplicated().any()),
        ("probabilities_finite", np.isfinite(target_values).all()),
        ("probabilities_in_unit_interval", ((target_values >= 0) & (target_values <= 1)).all()),
        ("no_missing_values", not sub.isna().any().any()),
    ]
    return pd.DataFrame(checks, columns=["check", "pass"])


def target_delta(left: pd.DataFrame, right: pd.DataFrame, label: str) -> pd.DataFrame:
    rows = []
    for target in TARGETS:
        l = left[target].to_numpy(dtype=float)
        r = right[target].to_numpy(dtype=float)
        prob_delta = l - r
        logit_delta = clipped_logit(l) - clipped_logit(r)
        changed = np.abs(prob_delta) > 1e-12
        rows.append(
            {
                "comparison": label,
                "target": target,
                "changed_cells": int(changed.sum()),
                "mean_abs_prob_delta": float(np.mean(np.abs(prob_delta))),
                "max_abs_prob_delta": float(np.max(np.abs(prob_delta))),
                "mean_abs_logit_delta": float(np.mean(np.abs(logit_delta))),
                "max_abs_logit_delta": float(np.max(np.abs(logit_delta))),
                "signed_prob_delta_sum": float(np.sum(prob_delta)),
                "signed_logit_delta_sum": float(np.sum(logit_delta)),
            }
        )
    return pd.DataFrame(rows)


def changed_cells(e237: pd.DataFrame, e224: pd.DataFrame, e95: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for target in TARGETS:
        e237_values = e237[target].to_numpy(dtype=float)
        e224_values = e224[target].to_numpy(dtype=float)
        e95_values = e95[target].to_numpy(dtype=float)
        prob_delta = e237_values - e224_values
        logit_delta = clipped_logit(e237_values) - clipped_logit(e224_values)
        mask = np.abs(prob_delta) > 1e-12
        for idx in np.flatnonzero(mask):
            rows.append(
                {
                    "row_idx": int(idx),
                    **{col: e237.loc[idx, col] for col in KEY},
                    "target": target,
                    "e95_prob": float(e95_values[idx]),
                    "e224_prob": float(e224_values[idx]),
                    "e237_prob": float(e237_values[idx]),
                    "prob_delta_vs_e224": float(prob_delta[idx]),
                    "abs_prob_delta_vs_e224": float(abs(prob_delta[idx])),
                    "logit_delta_vs_e224": float(logit_delta[idx]),
                    "abs_logit_delta_vs_e224": float(abs(logit_delta[idx])),
                    "prob_delta_vs_e95": float(e237_values[idx] - e95_values[idx]),
                }
            )
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["target", "abs_logit_delta_vs_e224"], ascending=[True, False])
    return out


def selected_metrics() -> dict[str, object]:
    selected = pd.read_csv(SELECTED)
    row = selected.iloc[0].to_dict()
    wanted = [
        "candidate_id",
        "submission_file",
        "q3_dropped_cells",
        "s4_dropped_cells",
        "expected_loss_vs_e224",
        "adverse_reduction_vs_e224",
        "support_gain_vs_e224",
        "q3_top1_over_abs_expected",
        "actual_expected_delta_vs_e224",
        "actual_adverse_reduction_vs_e224",
        "actual_support_gain_vs_e224",
        "e237_gate",
        "e237_score",
    ]
    return {key: row.get(key) for key in wanted}


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    shown = df if max_rows is None else df.head(max_rows)
    if shown.empty:
        return "_empty_"
    columns = [str(col) for col in shown.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in shown.iterrows():
        values = []
        for col in shown.columns:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.12g}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    sample = read_submission(SAMPLE)
    e237 = read_submission(E237)
    e224 = read_submission(E224)
    e95 = read_submission(E95)

    schema = audit_schema(sample, e237)
    delta = pd.concat(
        [
            target_delta(e237, e224, "e237_vs_e224"),
            target_delta(e237, e95, "e237_vs_e95"),
        ],
        ignore_index=True,
    )
    cells = changed_cells(e237, e224, e95)
    metrics = selected_metrics()

    moved_targets = sorted(cells["target"].unique().tolist()) if not cells.empty else []
    only_q3 = moved_targets == ["Q3"]
    q3_cells = int((cells["target"] == "Q3").sum()) if not cells.empty else 0
    ready = bool(schema["pass"].all() and only_q3 and q3_cells == 25)

    schema.to_csv(SCHEMA_CSV, index=False)
    delta.to_csv(TARGET_DELTA_CSV, index=False)
    cells.to_csv(CHANGED_CELLS_CSV, index=False)

    report = [
        "# E244 E237 Pre-Submission Audit",
        "",
        "## Verdict",
        "",
        f"- status: `{'READY' if ready else 'NOT_READY'}`",
        f"- file: `{E237.relative_to(ROOT)}`",
        f"- sha256: `{sha256(E237)}`",
        f"- sample schema: `{SAMPLE.relative_to(ROOT)}`",
        f"- moved targets vs E224: `{','.join(moved_targets) if moved_targets else 'none'}`",
        f"- changed Q3 cells vs E224: `{q3_cells}`",
        "",
        "E237 is submission-ready only as the pre-registered learned Q3 cell-tail sensor. "
        "It is not a broad reblend: compared with E224 it changes exactly 25 Q3 cells and leaves Q1/Q2/S1/S2/S3/S4 unchanged.",
        "",
        "## Schema Checks",
        "",
        markdown_table(schema),
        "",
        "## Movement Summary",
        "",
        markdown_table(delta),
        "",
        "## Selected E237 Metrics",
        "",
        markdown_table(pd.DataFrame([metrics]).T.reset_index().rename(columns={"index": "metric", 0: "value"})),
        "",
        "## Changed Cells Versus E224",
        "",
        markdown_table(cells, max_rows=25),
        "",
        "## Public Interpretation Protocol",
        "",
        "If this file is submitted, decode public feedback with:",
        "",
        "```bash",
        "python3 analysis_outputs/e238_e237_public_feedback_decoder.py --score <PUBLIC_LB>",
        "```",
        "",
        "If E224 public is known, include it as a contrast:",
        "",
        "```bash",
        "python3 analysis_outputs/e238_e237_public_feedback_decoder.py --score <E237_LB> --e224-score <E224_LB>",
        "```",
        "",
        "A win strengthens the learned Q3 decisive-cell worldview. "
        "A loss does not automatically kill E224 unless it reaches the E216-like collapse band.",
        "",
    ]
    REPORT.write_text("\n".join(report), encoding="utf-8")

    print(f"ready={ready}")
    print(f"sha256={sha256(E237)}")
    print(f"changed_cells_vs_e224={len(cells)}")
    print(delta.to_string(index=False))


if __name__ == "__main__":
    main()
