# E44 Large-Edge Low-Risk Census

## Observe

E43 showed that near-frontier candidate edges are smaller than selector error. The remaining cheap falsification is whether the existing scored universe already contains a larger sign-consistent movement that current selectors overlooked.

## Wonder

Do we have any candidate whose favorable edge is large enough to beat the best selector error while also passing low-bad-axis/raw05/two-selector stress?

## Hypothesis

H43: if the plateau is mostly a candidate-selection failure rather than a representation/selector-resolution failure, at least one existing scored candidate should have a pairwise public-order edge larger than the current best selector error and survive low-risk gates.

## Method

- Raw05-A2C8 public gap: `0.0000869862`.
- Best current selector error from E43: `0.000218288`.
- Scored tables loaded: `29`.
- Normal large-safe gate: pair p90 edge greater than selector error, low bad-axis, raw05-compatible, no hard veto, and either two-selector or submit-like support.

## Result

| loaded_tables | row_count | unique_files | pair_negative_rows | pair_negative_files | pair_edge_gt_raw05_gap_rows | pair_edge_gt_raw05_gap_files | pair_edge_gt_selector_error_rows | pair_edge_gt_selector_error_files | large_pair_lowbad_rows | large_pair_lowbad_files | large_pair_two_selector_rows | large_pair_two_selector_files | normal_large_safe_rows | normal_large_safe_files | any_edge_gt_selector_error_rows | any_edge_gt_selector_error_files | best_pair_edge | best_pair_edge_over_selector_error | best_pair_edge_over_raw05_gap | best_any_edge | best_any_edge_over_selector_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 29.000000 | 69869.000000 | 48088.000000 | 12855.000000 | 12309.000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 25.000000 | 21.000000 | 0.000073768 | 0.337941 | 0.848048 | 0.001036338 | 4.747576 |

## Source Breakdown

| source_table | rows | unique_files | pair_negative | pair_edge_gt_raw05_gap | pair_edge_gt_selector_error | normal_large_safe | any_edge_gt_selector_error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inverse7_raw_anchor_bridge_scale_scan_scores.csv | 22 | 22 | 0 | 0 | 0 | 0 | 19 |
| worldview_sensor_discriminability_audit.csv | 10 | 10 | 3 | 0 | 0 | 0 | 5 |
| public_probe_independent_evidence_audit_summary.csv | 5 | 5 | 3 | 0 | 0 | 0 | 1 |
| block_measurement_selector_rescore.csv | 3808 | 3808 | 0 | 0 | 0 | 0 | 0 |
| block_measurement_selector_rescore_shortlist.csv | 71 | 71 | 0 | 0 | 0 | 0 | 0 |
| direction_probe_selector_reconciliation.csv | 22 | 22 | 0 | 0 | 0 | 0 | 0 |
| focused_label_flow_survival_review.csv | 163 | 163 | 163 | 0 | 0 | 0 | 0 |
| hidden_public_local_bridge_shortlist.csv | 580 | 580 | 0 | 0 | 0 | 0 | 0 |
| hidden_public_localization_candidate_ranking.csv | 368 | 368 | 0 | 0 | 0 | 0 | 0 |
| jepa_selector_frontier_audit_candidates.csv | 7318 | 7318 | 0 | 0 | 0 | 0 | 0 |
| label_flow_blockrate_jepa_pairwise_scored.csv | 556 | 556 | 0 | 0 | 0 | 0 | 0 |
| label_flow_combo_focused_submit_pairwise_scored.csv | 180 | 180 | 180 | 0 | 0 | 0 | 0 |
| label_flow_combo_gate_pairwise_scored.csv | 11248 | 11248 | 8094 | 0 | 0 | 0 | 0 |
| label_flow_gated_candidate_pairwise_scored.csv | 7240 | 7240 | 50 | 0 | 0 | 0 | 0 |
| label_flow_gated_candidate_shortlist.csv | 3263 | 3263 | 50 | 0 | 0 | 0 | 0 |
| label_flow_localized_sensor_audit.csv | 960 | 960 | 807 | 0 | 0 | 0 | 0 |
| label_flow_localized_sensor_audit_shortlist.csv | 40 | 40 | 40 | 0 | 0 | 0 | 0 |
| label_flow_sensor_scale_curve.csv | 108 | 108 | 108 | 0 | 0 | 0 | 0 |
| label_flow_sensor_scale_curve_shortlist.csv | 30 | 30 | 30 | 0 | 0 | 0 | 0 |
| label_flow_targetwise_amplified_gate_pairwise_scored.csv | 9444 | 9444 | 3024 | 0 | 0 | 0 | 0 |
| old_positive_anchor_pairwise_rescore.csv | 212 | 212 | 0 | 0 | 0 | 0 | 0 |
| old_positive_anchor_pairwise_rescore_shortlist.csv | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| public_lb_inverse8_selected_stress_audit.csv | 50 | 50 | 0 | 0 | 0 | 0 | 0 |
| public_pairwise_order_selector_candidates.csv | 1893 | 1893 | 46 | 0 | 0 | 0 | 0 |
| public_pairwise_order_selector_shortlist.csv | 224 | 224 | 46 | 0 | 0 | 0 | 0 |
| public_selector_universe_audit_candidates.csv | 15871 | 15867 | 0 | 0 | 0 | 0 | 0 |
| s4q3_oof_top_selector_rescore.csv | 407 | 407 | 0 | 0 | 0 | 0 | 0 |
| selector_disambiguation_sensor_candidates.csv | 4 | 4 | 2 | 0 | 0 | 0 | 0 |
| selector_support_topology_audit.csv | 5769 | 5769 | 209 | 0 | 0 | 0 | 0 |

## Top Pair-Favorable Rows

| file | family | best_min_pair_p90 | best_max_pair_edge | best_max_pair_edge_over_selector_error | best_max_pair_edge_over_raw05_gap | large_pair_lowbad_gate | large_pair_two_selector_gate | normal_large_safe_gate | source_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id07_s1p00_e1c5f36d.csv | label_flow_localized_sensor | -0.000073768 | 0.000073768 | 0.337941 | 0.848048 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id05_s1p00_23a548ed.csv | label_flow_localized_sensor | -0.000071827 | 0.000071827 | 0.329045 | 0.825724 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id05_b07_s1p00_88ed7366.csv | label_flow_localized_sensor | -0.000071659 | 0.000071659 | 0.328279 | 0.823800 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id07_b00_s1p00_ec45a2d0.csv | label_flow_localized_sensor | -0.000071295 | 0.000071295 | 0.326612 | 0.819618 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id04_s1p00_1a75e50d.csv | label_flow_localized_sensor | -0.000071147 | 0.000071147 | 0.325931 | 0.817909 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id01_s1p00_9eeacf05.csv | label_flow_localized_sensor | -0.000070983 | 0.000070983 | 0.325181 | 0.816027 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id03_s1p00_81e5d1a6.csv | label_flow_localized_sensor | -0.000069231 | 0.000069231 | 0.317153 | 0.795882 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_s4_not_subject_id05_s1p00_070b9d44.csv | label_flow_localized_sensor | -0.000068395 | 0.000068395 | 0.313325 | 0.786275 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_s4_not_block_id05_b07_s1p00_6aa18401.csv | label_flow_localized_sensor | -0.000066954 | 0.000066954 | 0.306723 | 0.769707 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_s4_not_block_id07_b00_s1p00_f2d58680.csv | label_flow_localized_sensor | -0.000066951 | 0.000066951 | 0.306709 | 0.769673 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_s4_not_subject_id07_s1p00_c5af6639.csv | label_flow_localized_sensor | -0.000066806 | 0.000066806 | 0.306045 | 0.768005 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id01_b03_s1p00_14594db4.csv | label_flow_localized_sensor | -0.000066623 | 0.000066623 | 0.305209 | 0.765908 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id04_b06_s1p00_c3e9ba2f.csv | label_flow_localized_sensor | -0.000066427 | 0.000066427 | 0.304311 | 0.763655 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_s4_not_subject_id01_s1p00_4c6d033a.csv | label_flow_localized_sensor | -0.000066277 | 0.000066277 | 0.303620 | 0.761921 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id07_b04_s1p00_172bf526.csv | label_flow_localized_sensor | -0.000065489 | 0.000065489 | 0.300011 | 0.752864 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id04_b01_s1p00_07da8fed.csv | label_flow_localized_sensor | -0.000065228 | 0.000065228 | 0.298815 | 0.749864 | False | False | False | 2 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id03_b00_s1p00_a1e7c7b8.csv | label_flow_localized_sensor | -0.000065226 | 0.000065226 | 0.298809 | 0.749847 | False | False | False | 2 |
| submission_label_flow_focused_6b9335b1.csv | other | -0.000065217 | 0.000065217 | 0.298767 | 0.749743 | False | False | False | 6 |
| submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id04_b02_s1p00_0dce4d70.csv | label_flow_localized_sensor | -0.000065217 | 0.000065217 | 0.298767 | 0.749743 | False | False | False | 1 |
| submission_label_flow_sensorcurve_contrast_6b_q2_q3_s4_s1p00_224dffb3.csv | label_flow_sensor_scale_curve | -0.000065217 | 0.000065217 | 0.298767 | 0.749743 | False | False | False | 1 |

## Top Any-Edge Conflict Rows

| file | family | best_min_pair_p90 | best_min_old_p90 | best_min_raw_mean | best_min_anchor_low_half_max | best_max_best_observed_edge | best_max_edge_over_selector_error | normal_large_safe_gate | diagnostic_large_conflict_gate | source_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bridge_scan_candidates/submission_bridge_inv7_s1p50.csv | pure_inv7 | 0.000180513 |  | -0.001036338 | -0.000014675 | 0.001036338 | 4.747576 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_inv7_s1p25.csv | pure_inv7 | 0.000151016 |  | -0.000872888 | -0.000021503 | 0.000872888 | 3.998795 | False | True | 1 |
| submission_inverse7blend_1040423d.csv | direct_inverse | 0.000122038 | 0.000617292 | -0.000705727 | -0.000024619 | 0.000705727 | 3.233012 | False | True | 6 |
| bridge_scan_candidates/submission_bridge_inv7_s1p00.csv | pure_inv7 | 0.000122038 | 0.000617292 | -0.000705727 | -0.000024619 | 0.000705727 | 3.233012 | False | True | 2 |
| bridge_scan_candidates/submission_bridge_blend_m0p25_s1p25.csv | inv7_mixmin_blend | 0.000279825 |  | -0.000671997 | -0.000225059 | 0.000671997 | 3.078490 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p25_s1p00.csv | inv7_mixmin_blend | 0.000226558 |  | -0.000551692 | -0.000194141 | 0.000551692 | 2.527358 | False | True | 1 |
| submission_mixmin_0c916bb4.csv | mixmin | 0.000879200 | 0.001041933 | 0.000065107 | -0.000537096 | 0.000537096 | 2.460494 | False | True | 7 |
| bridge_scan_candidates/submission_bridge_mixmin_s1p00.csv | pure_mixmin | 0.000879200 |  | 0.000065107 | -0.000537096 | 0.000537096 | 2.460494 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_inv7_s0p75.csv | pure_inv7 | 0.000094018 |  | -0.000534856 | -0.000024025 | 0.000534856 | 2.450233 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv | inv7_mixmin_blend | 0.000824065 |  | -0.000149338 | -0.000511296 | 0.000511296 | 2.342301 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_mixmin_s0p75.csv | pure_mixmin | 0.000650543 |  | -0.000005730 | -0.000457382 | 0.000457382 | 2.095315 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p75_s1p00.csv | inv7_mixmin_blend | 0.000652288 |  | -0.000166235 | -0.000455802 | 0.000455802 | 2.088078 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p50_s1p25.csv | inv7_mixmin_blend | 0.000539786 |  | -0.000430788 | -0.000388298 | 0.000430788 | 1.973485 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p25_s0p75.csv | inv7_mixmin_blend | 0.000171414 |  | -0.000424337 | -0.000156175 | 0.000424337 | 1.943935 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p75_s0p75.csv | inv7_mixmin_blend | 0.000486586 |  | -0.000159758 | -0.000376933 | 0.000376933 | 1.726770 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p50_s1p00.csv | inv7_mixmin_blend | 0.000432363 |  | -0.000371848 | -0.000337856 | 0.000371848 | 1.703476 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_inv7_s0p50.csv | pure_inv7 | 0.000064372 | 0.000607068 | -0.000360277 | -0.000019722 | 0.000360277 | 1.650466 | False | True | 2 |
| bridge_scan_candidates/submission_bridge_mixmin_s0p50.csv | pure_mixmin | 0.000431661 |  | -0.000040208 | -0.000341310 | 0.000341310 | 1.563576 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p50_s0p75.csv | inv7_mixmin_blend | 0.000323816 |  | -0.000299299 | -0.000273805 | 0.000299299 | 1.371122 | False | True | 1 |
| bridge_scan_candidates/submission_bridge_blend_m0p25_s0p50.csv | inv7_mixmin_blend | 0.000116208 | 0.000640247 | -0.000289936 | -0.000111161 | 0.000289936 | 1.328228 | False | True | 2 |

## Normal Large-Safe Candidates

_none_

## Decision

No candidate has a selector-error-scale pairwise public-order edge. Large favorable signals exist only in raw/anchor/honest-CV views and are exactly the worldview conflict already diagnosed in E38-E43.

## Outputs

- `analysis_outputs/large_edge_lowrisk_census_rows.csv`
- `analysis_outputs/large_edge_lowrisk_census_by_file.csv`
- `analysis_outputs/large_edge_lowrisk_census_summary.csv`
- `analysis_outputs/large_edge_lowrisk_census_report.md`
