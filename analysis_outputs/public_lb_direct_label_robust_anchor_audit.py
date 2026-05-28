from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs"
DATA = ROOT / "data"
if str(OUT) not in sys.path:
    sys.path.append(str(OUT))

from raw05_anchor_jepa_micro_injection import TARGETS, actual_anchor_score, read_submission  # noqa: E402


SELECTED = OUT / "public_lb_direct_label_robust_selector_selected.csv"
SCORE_OUT = OUT / "public_lb_direct_label_robust_selector_actual_anchor.csv"
REPORT_OUT = OUT / "public_lb_direct_label_robust_anchor_audit_report.md"

CONTROL_FILES = [
    "submission_frontier_cvjepa_refine_a2c8d2c8.csv",
    "submission_raw_timeline_jepa_rescue_strict_scale0p5.csv",
]


def write_report(scored: pd.DataFrame) -> None:
    cols = [
        "file",
        "submit_role",
        "actual_anchor_score_final",
        "mean_actual_anchor",
        "min_set_score",
        "max_set_score",
        "source_mask_name",
        "source_loocv_mae",
        "source_l2o_mae",
        "target_mask",
        "strength",
        "cap",
        "robust_delta_vs_a2c8",
        "mean_abs_move_vs_a2c8",
    ]
    best = scored.sort_values("actual_anchor_score_final").head(12)
    controls = scored[scored["file"].isin(CONTROL_FILES)]
    report = [
        "# Robust Direct-Label Actual-Anchor Audit",
        "",
        "This applies the existing actual-anchor scenario/mask proxy to robust direct-label selected submissions.",
        "",
        "## Best Robust Candidates",
        "",
        "```",
        best[[c for c in cols if c in best.columns]].round(9).to_string(index=False),
        "```",
        "",
        "## Controls",
        "",
        "```",
        controls[[c for c in cols if c in controls.columns]].round(9).to_string(index=False),
        "```",
        "",
        "## Interpretation",
        "",
        "- This proxy is calibrated only as a consistency filter over known public-anchor scenario/mask families.",
        "- Robust candidates beating a2c8 on this proxy means they remain compatible with previous public anchor geometry, not that their public LB is proven.",
        "",
    ]
    REPORT_OUT.write_text("\n".join(report), encoding="utf-8")


def main() -> None:
    sample = pd.read_csv(DATA / "ch2026_submission_sample.csv", parse_dates=["sleep_date", "lifelog_date"])
    sample = sample.sort_values(["subject_id", "sleep_date", "lifelog_date"]).reset_index(drop=True)
    selected = pd.read_csv(SELECTED)
    files = CONTROL_FILES + selected["file"].astype(str).tolist()
    preds = [read_submission(file_name)[TARGETS].to_numpy(dtype=float) for file_name in files]
    scored = actual_anchor_score(preds, sample)
    scored["file"] = files
    scored = scored.merge(
        selected[
            [
                "file",
                "submit_role",
                "source_mask_name",
                "source_loocv_mae",
                "source_l2o_mae",
                "target_mask",
                "strength",
                "cap",
                "robust_delta_vs_a2c8",
                "mean_abs_move_vs_a2c8",
            ]
        ],
        on="file",
        how="left",
    )
    scored = scored.sort_values("actual_anchor_score_final").reset_index(drop=True)
    scored.to_csv(SCORE_OUT, index=False)
    write_report(scored)
    print(REPORT_OUT)
    print(
        scored[
            [
                "file",
                "submit_role",
                "actual_anchor_score_final",
                "source_mask_name",
                "source_loocv_mae",
                "source_l2o_mae",
                "target_mask",
                "strength",
                "cap",
                "robust_delta_vs_a2c8",
                "mean_abs_move_vs_a2c8",
            ]
        ]
        .head(20)
        .round(9)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
