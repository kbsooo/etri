# H006 H005 Route Materializer

## Question

Can the strongest H005 human-state route families be translated into sparse, public-free-safe E247 edits?

## Method

- Rebuild each selected H005 state score on train+test without public LB.
- Rank test rows by the human-state score and move only a tiny set of rows.
- Apply only the declared target route, with 1-3 targets per candidate.
- Promote only if both selector and movement-shape gates pass.

## Candidate Gate

| candidate_id | h006_decision | active_targets | changed_rows | changed_cells | max_abs_prob_delta | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current | shape_gate | h006_strict_upload_gate | h006_info_gate | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s4_mobility_only_top20_amp0p008 | too_small_to_submit | S4 | 20 | 20 | 0.001992488 | -0.000007063 | 0.000002881 | 0.888888889 | 0.000116564 | True | False | True | submission_h006_s4_mobility_only_top20_amp0p008_4ab3c0e1.csv |
| s4_mobility_only_top28 | too_small_to_submit | S4 | 28 | 28 | 0.001498418 | -0.000007607 | 0.000002976 | 0.888888889 | 0.000211798 | True | False | True | submission_h006_s4_mobility_only_top28_3aa3d8d2.csv |
| s4_mobility_only_top36_amp0p008 | too_small_to_submit | S4 | 36 | 36 | 0.001997824 | -0.000013045 | 0.000005221 | 0.888888889 | 0.000394520 | True | False | True | submission_h006_s4_mobility_only_top36_amp0p008_52d4d1e1.csv |
| s4_mobility_only_top50_amp0p006 | too_small_to_submit | S4 | 50 | 50 | 0.001498418 | -0.000011961 | 0.000005900 | 0.833333333 | 0.000483818 | True | False | True | submission_h006_s4_mobility_only_top50_amp0p006_cd002efd.csv |
| vehicle_s4s1_top22 | shape_ok_but_selector_rejects | S1,S4 | 22 | 44 | 0.001497031 | -0.000006423 | 0.000002363 | 0.513888889 | 0.000403890 | True | False | False | submission_h006_vehicle_s4s1_top22_e1657b33.csv |
| mobility_errand_s4s1q1_top18 | shape_ok_but_selector_rejects | Q1,S1,S4 | 18 | 54 | 0.001499999 | -0.000008514 | 0.000003935 | 0.472222222 | 0.000617021 | True | False | False | submission_h006_mobility_errand_s4s1q1_top18_6d0c2398.csv |
| forced_commute_q3s4q1_top16 | shape_ok_but_selector_rejects | Q1,Q3,S4 | 16 | 48 | 0.001249953 | -0.000015510 | 0.000005455 | 0.486111111 | -0.000304225 | True | False | False | submission_h006_forced_commute_q3s4q1_top16_4bb09eea.csv |
| balanced_routebook_tiny | reject_shape_or_bad_axis | Q1,Q2,S1,S2,S3,S4 | 27 | 87 | 0.001549999 | 0.000002812 | 0.000006454 | 0.083333333 | 0.000182589 | False | False | False | submission_h006_balanced_routebook_tiny_18e5792e.csv |
| s4_mobility_only_top50_amp0p008 | shape_ok_but_selector_rejects | S4 | 50 | 50 | 0.001997824 | -0.000014517 | 0.000012108 | 0.458333333 | 0.000645090 | True | False | False | submission_h006_s4_mobility_only_top50_amp0p008_2fcc469d.csv |
| weekend_obligation_s4q2s1_top18 | shape_ok_but_selector_rejects | Q2,S1,S4 | 18 | 54 | 0.001499868 | 0.000008253 | 0.000018354 | 0.111111111 | -0.000726871 | True | False | False | submission_h006_weekend_obligation_s4q2s1_top18_e55fb596.csv |
| q2s2_recovery_only_top24 | shape_ok_but_selector_rejects | Q2,S2 | 24 | 48 | 0.001372252 | 0.000003704 | 0.000019608 | 0.319444444 | 0.001403777 | True | False | False | submission_h006_q2s2_recovery_only_top24_b23d9daa.csv |
| bedtime_decision_s3q1q2_top18 | shape_ok_but_selector_rejects | Q1,Q2,S3 | 18 | 54 | 0.001249999 | 0.000006165 | 0.000021090 | 0.166666667 | -0.000244817 | True | False | False | submission_h006_bedtime_decision_s3q1q2_top18_ec607fdb.csv |
| s4_mobility_down_control_top28_amp0p006 | shape_ok_but_selector_rejects | S4 | 28 | 28 | 0.001498696 | 0.000006367 | 0.000028118 | 0.166666667 | -0.000211798 | True | False | False | submission_h006_s4_mobility_down_control_top28_amp0p006_aee91ace.csv |
| routine_anchor_q2s2q1_top18 | shape_ok_but_selector_rejects | Q1,Q2,S2 | 18 | 54 | 0.001249832 | 0.000004602 | 0.000032290 | 0.555555556 | 0.000819989 | True | False | False | submission_h006_routine_anchor_q2s2q1_top18_d1bb6df2.csv |
| s4_mobility_down_control_top36_amp0p008 | shape_ok_but_selector_rejects | S4 | 36 | 36 | 0.001998319 | 0.000011205 | 0.000049975 | 0.152777778 | -0.000394520 | True | False | False | submission_h006_s4_mobility_down_control_top36_amp0p008_dca8a631.csv |

## Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h006_s4_mobility_only_top20_amp0p008_4ab3c0e1.csv | too_small_to_submit | -0.000007063 | -0.000029472 | 0.000002881 | 0.888888889 | 0.000116564 |
| submission_h006_s4_mobility_only_top28_3aa3d8d2.csv | too_small_to_submit | -0.000007607 | -0.000030881 | 0.000002976 | 0.888888889 | 0.000211798 |
| submission_h006_s4_mobility_only_top36_amp0p008_52d4d1e1.csv | too_small_to_submit | -0.000013045 | -0.000054526 | 0.000005221 | 0.888888889 | 0.000394520 |
| submission_h006_s4_mobility_only_top50_amp0p006_cd002efd.csv | too_small_to_submit | -0.000011961 | -0.000056291 | 0.000005900 | 0.833333333 | 0.000483818 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | below_selector_resolution | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_h006_vehicle_s4s1_top22_e1657b33.csv | below_selector_resolution | -0.000006423 | -0.000021318 | 0.000002363 | 0.513888889 | 0.000403890 |
| submission_h006_mobility_errand_s4s1q1_top18_6d0c2398.csv | below_selector_resolution | -0.000008514 | -0.000031349 | 0.000003935 | 0.472222222 | 0.000617021 |
| submission_h006_forced_commute_q3s4q1_top16_4bb09eea.csv | below_selector_resolution | -0.000015510 | -0.000045279 | 0.000005455 | 0.486111111 | -0.000304225 |
| submission_h006_balanced_routebook_tiny_18e5792e.csv | below_selector_resolution | 0.000002812 | 0.000000692 | 0.000006454 | 0.083333333 | 0.000182589 |
| submission_h006_s4_mobility_only_top50_amp0p008_2fcc469d.csv | below_selector_resolution | -0.000014517 | -0.000075150 | 0.000012108 | 0.458333333 | 0.000645090 |
| submission_h006_weekend_obligation_s4q2s1_top18_e55fb596.csv | below_selector_resolution | 0.000008253 | -0.000000192 | 0.000018354 | 0.111111111 | -0.000726871 |
| submission_h006_q2s2_recovery_only_top24_b23d9daa.csv | below_selector_resolution | 0.000003704 | -0.000004191 | 0.000019608 | 0.319444444 | 0.001403777 |
| submission_h006_bedtime_decision_s3q1q2_top18_ec607fdb.csv | below_selector_resolution | 0.000006165 | -0.000018577 | 0.000021090 | 0.166666667 | -0.000244817 |
| submission_h006_s4_mobility_down_control_top28_amp0p006_aee91ace.csv | below_selector_resolution | 0.000006367 | -0.000003298 | 0.000028118 | 0.166666667 | -0.000211798 |
| submission_h006_routine_anchor_q2s2q1_top18_d1bb6df2.csv | below_selector_resolution | 0.000004602 | -0.000004620 | 0.000032290 | 0.555555556 | 0.000819989 |
| submission_h006_s4_mobility_down_control_top36_amp0p008_dca8a631.csv | below_selector_resolution | 0.000011205 | -0.000005690 | 0.000049975 | 0.152777778 | -0.000394520 |

## Component Rows

| candidate_id | component | route_key | selected_rows | eligible_rows | amp | h005_best_avg_delta | h005_mean_avg_delta | matched_feature_count_sum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mobility_errand_s4s1q1_top18 | errand_mobility | S4_up|S1_down|Q1_down | 18 | 250 | 0.006000000 | -0.000095829 | -0.000091316 | 41 |
| weekend_obligation_s4q2s1_top18 | weekend_obligation | S4_up|Q2_up|S1_down | 18 | 250 | 0.006000000 | -0.000095356 | -0.000095356 | 23 |
| routine_anchor_q2s2q1_top18 | routine_anchor | Q2_down|S2_up|Q1_up | 18 | 100 | 0.005000000 | -0.000082579 | -0.000082579 | 8 |
| bedtime_decision_s3q1q2_top18 | decision_fatigue | S3_down|Q1_down|Q2_up | 18 | 250 | 0.005000000 | -0.000080647 | -0.000080647 | 42 |
| forced_commute_q3s4q1_top16 | forced_commute_after_badnight | Q3_up|S4_up|Q1_down | 16 | 250 | 0.005000000 | -0.000083732 | -0.000083732 | 4 |
| vehicle_s4s1_top22 | vehicle_exposure | S4_up|S1_down | 22 | 106 | 0.006000000 | -0.000064124 | -0.000064124 | 12 |
| q2s2_recovery_only_top24 | q2s2_recovery | Q2_down|S2_up | 24 | 163 | 0.005500000 | -0.000082579 | -0.000068719 | 15 |
| s4_mobility_only_top28 | s4_mobility_consensus | S4_up | 28 | 250 | 0.006000000 | -0.000095356 | -0.000084190 | 63 |
| balanced_routebook_tiny | mobility_tiny | S4_up|S1_down|Q1_down | 10 | 250 | 0.003200000 | -0.000095829 | -0.000094460 | 32 |
| balanced_routebook_tiny | routine_tiny | Q2_down|S2_up|Q1_up | 10 | 100 | 0.003000000 | -0.000082579 | -0.000082579 | 8 |
| balanced_routebook_tiny | bedtime_tiny | S3_down|Q1_down|Q2_up | 10 | 250 | 0.003000000 | -0.000080647 | -0.000080647 | 42 |
| s4_mobility_only_top20_amp0p008 | s4_mobility_consensus_scaled | S4_up | 20 | 250 | 0.008000000 | -0.000095356 | -0.000084190 | 63 |
| s4_mobility_only_top36_amp0p008 | s4_mobility_consensus_scaled | S4_up | 36 | 250 | 0.008000000 | -0.000095356 | -0.000084190 | 63 |
| s4_mobility_only_top50_amp0p006 | s4_mobility_consensus_scaled | S4_up | 50 | 250 | 0.006000000 | -0.000095356 | -0.000084190 | 63 |
| s4_mobility_only_top50_amp0p008 | s4_mobility_consensus_scaled | S4_up | 50 | 250 | 0.008000000 | -0.000095356 | -0.000084190 | 63 |
| s4_mobility_down_control_top28_amp0p006 | s4_mobility_opposite_control | S4_down | 28 | 250 | 0.006000000 | -0.000095356 | -0.000084190 | 63 |
| s4_mobility_down_control_top36_amp0p008 | s4_mobility_opposite_control | S4_down | 36 | 250 | 0.008000000 | -0.000095356 | -0.000084190 | 63 |

## Movement Anatomy

| basename | changed_rows_vs_current | changed_cells_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current | cos_delta_with_h003_tiny | l1_ratio_to_h003_tiny |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h006_s4_mobility_only_top20_amp0p008_4ab3c0e1.csv | 20 | 20 | 0.160000000 | 0.001992488 | 0.004951606 | 0.011815758 |
| submission_h006_s4_mobility_only_top28_3aa3d8d2.csv | 28 | 28 | 0.168000000 | 0.001498418 | -0.011947300 | 0.012406545 |
| submission_h006_s4_mobility_down_control_top28_amp0p006_aee91ace.csv | 28 | 28 | 0.168000000 | 0.001498696 | 0.011947300 | 0.012406545 |
| submission_h006_forced_commute_q3s4q1_top16_4bb09eea.csv | 16 | 48 | 0.240000000 | 0.001249953 | 0.000468438 | 0.017723636 |
| submission_h006_q2s2_recovery_only_top24_b23d9daa.csv | 24 | 48 | 0.264000000 | 0.001372252 | -0.071355341 | 0.019496000 |
| submission_h006_vehicle_s4s1_top22_e1657b33.csv | 22 | 44 | 0.264000000 | 0.001497031 | -0.016043065 | 0.019496000 |
| submission_h006_routine_anchor_q2s2q1_top18_d1bb6df2.csv | 18 | 54 | 0.270000000 | 0.001249832 | -0.008978196 | 0.019939091 |
| submission_h006_bedtime_decision_s3q1q2_top18_ec607fdb.csv | 18 | 54 | 0.270000000 | 0.001249999 | -0.060479314 | 0.019939091 |
| submission_h006_balanced_routebook_tiny_18e5792e.csv | 27 | 87 | 0.276000000 | 0.001549999 | -0.046852473 | 0.020382182 |
| submission_h006_s4_mobility_only_top36_amp0p008_52d4d1e1.csv | 36 | 36 | 0.288000000 | 0.001997824 | -0.024078223 | 0.021268364 |
| submission_h006_s4_mobility_down_control_top36_amp0p008_dca8a631.csv | 36 | 36 | 0.288000000 | 0.001998319 | 0.024078223 | 0.021268364 |
| submission_h006_s4_mobility_only_top50_amp0p006_cd002efd.csv | 50 | 50 | 0.300000000 | 0.001498418 | -0.038573422 | 0.022154545 |
| submission_h006_weekend_obligation_s4q2s1_top18_e55fb596.csv | 18 | 54 | 0.324000000 | 0.001499868 | 0.008417435 | 0.023926909 |
| submission_h006_mobility_errand_s4s1q1_top18_6d0c2398.csv | 18 | 54 | 0.324000000 | 0.001499999 | -0.031892169 | 0.023926909 |
| submission_h006_s4_mobility_only_top50_amp0p008_2fcc469d.csv | 50 | 50 | 0.400000000 | 0.001997824 | -0.038573422 | 0.029539394 |

## Selection

_empty_

## Interpretation

No candidate passed strict upload gate. `submission_h006_s4_mobility_only_top20_amp0p008_4ab3c0e1.csv` is the best diagnostic sensor, but not submission-grade by the current public-free rule.

## Files

- `hitl/h006_h005_route_materializer/h006_candidates.csv`
- `hitl/h006_h005_route_materializer/h006_component_rows.csv`
- `hitl/h006_h005_route_materializer/h006_selector_scores.csv`
- `hitl/h006_h005_route_materializer/h006_candidate_anatomy.csv`
- `hitl/h006_h005_route_materializer/h006_gate_scores.csv`
- `hitl/h006_h005_route_materializer/h006_selection.csv`
