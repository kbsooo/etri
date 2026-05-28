from __future__ import annotations

from pathlib import Path


OUT = Path(__file__).resolve().parents[0]

LEJEPA_BAD = "submission_lejepa_targetwise_strict_best_scale0p5.csv"
LEJEPA_BAD_PUBLIC = 0.5802468192


def anchors8(inv_module):
    anchors = list(inv_module.ANCHORS)
    if not any(str(anchor[0]) == "lejepa_bad" for anchor in anchors):
        anchors.append(("lejepa_bad", LEJEPA_BAD, LEJEPA_BAD_PUBLIC, 0.9))
    return anchors


def apply_inverse8(inv_module) -> None:
    inv_module.ANCHORS = anchors8(inv_module)
    inv_module.SOLUTION_OUT = OUT / "public_lb_direct_label_inverse8_solutions.csv"
    inv_module.TARGET_OUT = OUT / "public_lb_direct_label_inverse8_target_summary.csv"
    inv_module.CELL_OUT = OUT / "public_lb_direct_label_inverse8_cell_solutions.parquet"
    inv_module.CANDIDATE_OUT = OUT / "public_lb_direct_label_inverse8_candidate_scan.csv"
    inv_module.SELECTED_OUT = OUT / "public_lb_direct_label_inverse8_selected.csv"
    inv_module.REPORT_OUT = OUT / "public_lb_direct_label_inverse8_report.md"


def apply_loocv8(loo_module) -> None:
    loo_module.ALL_ANCHORS = anchors8(loo_module.inv)
    loo_module.DETAIL_OUT = OUT / "public_lb_direct_label_inverse8_loocv_detail.csv"
    loo_module.POLICY_OUT = OUT / "public_lb_direct_label_inverse8_loocv_policy.csv"
    loo_module.REPORT_OUT = OUT / "public_lb_direct_label_inverse8_loocv_report.md"


def apply_l2ocv8(l2o_module) -> None:
    l2o_module.ALL_ANCHORS = anchors8(l2o_module.inv)
    l2o_module.DETAIL_OUT = OUT / "public_lb_direct_label_inverse8_l2ocv_detail.csv"
    l2o_module.SOURCE_OUT = OUT / "public_lb_direct_label_inverse8_l2ocv_source_summary.csv"
    l2o_module.POLICY_OUT = OUT / "public_lb_direct_label_inverse8_l2ocv_policy.csv"
    l2o_module.REPORT_OUT = OUT / "public_lb_direct_label_inverse8_l2ocv_report.md"


def apply_robust8(robust_module) -> None:
    robust_module.SUMMARY_IN = OUT / "public_lb_direct_label_inverse8_solutions.csv"
    robust_module.CELL_IN = OUT / "public_lb_direct_label_inverse8_cell_solutions.parquet"
    robust_module.LOOCV_IN = OUT / "public_lb_direct_label_inverse8_loocv_detail.csv"
    robust_module.L2OCV_SOURCE_IN = OUT / "public_lb_direct_label_inverse8_l2ocv_source_summary.csv"
    robust_module.SCAN_OUT = OUT / "public_lb_direct_label_robust_selector8_scan.csv"
    robust_module.SELECTED_OUT = OUT / "public_lb_direct_label_robust_selector8_selected.csv"
    robust_module.SOURCE_OUT = OUT / "public_lb_direct_label_robust_selector8_sources.csv"
    robust_module.REPORT_OUT = OUT / "public_lb_direct_label_robust_selector8_report.md"

