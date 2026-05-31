# E314 Human-Readiness Lift Materializer

Public LB는 사용하지 않았다. E313에서 human-readiness가 높은데 safe-but-too-small으로 남은 seed actions를 개별 확대/희소화해서 보이게 만들 수 있는지 검증했다.

Important limitation: 이번 run은 `single_human_ready_lift` 후보가 `MAX_CANDIDATES`를 모두 채워서 consensus/negative-stack branch까지 도달하지 못했다. 따라서 E314는 individual scalar lift를 반증한 것이지, 모든 human-ready composition을 반증한 것은 아니다.

## Seed Pool

- safe human-ready seeds loaded: `180`

| experiment | basename | family | target_norm | actual_p90 | null_strict_rate | readiness_distance | pred_ready__human_signature | pred_ready__geometry_only | seed_abs_l1 | seed_changed_rows | failure_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e286 | submission_e286_e247contrast_e247_common_vs_e28_human_plus_geometr_lr_l2_c0p3_anti_amp_add_high_preserve_top3_eaa52596.csv | human_plus_geometry | e247_common_vs_e284_extra | -0.000003163 | 0.000000000 | 2.311122883 | -0.764377383 | 1.392503139 | 0.058895572 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_common_vs_e28_human_plus_geometr_lr_l2_c0p3_anti_amp_add_high_preserve_top3_03ccfe02.csv | human_plus_geometry | e247_common_vs_e284_extra | -0.000001815 | 0.000000000 | 2.502947183 | -0.764377383 | 1.393900897 | 0.033654613 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_undo_low_preserve_top3_2b344e02.csv | cell_geometry | e247_body_vs_clean_neither | 0.000003273 | 0.000000000 | 0.553272931 | -0.111750871 | 1.673001578 | 0.028453682 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_undo_low_preserve_top3_a41b61fd.csv | cell_geometry | e247_body_vs_clean_neither | 0.000006552 | 0.000000000 | 0.556552242 | -0.111750871 | 1.675112092 | 0.056907364 | 3 | safe_but_too_small_or_wrong_sign |
| e310 | submission_e310_pair_bedtime_arousal_Q1_S1_raw_human_context_subject5_opp_sign_top64_s020_e16333df.csv | bedtime_arousal | multi | -0.000002748 | 0.000000000 | 1.097251554 | -0.103699946 | 1.819043661 | 0.156992574 | 22 | safe_but_too_small_or_wrong_sign |
| e310 | submission_e310_pair_bedtime_arousal_Q1_S1_raw_human_context_subject5_opp_sign_top64_s014_415aafad.csv | bedtime_arousal | multi | -0.000001874 | 0.000000000 | 1.098126366 | -0.103699946 | 1.765916390 | 0.109894802 | 22 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_common_vs_e28_human_plus_geometr_lr_l2_c0p3_anti_amp_swap_low_high_top3_80ab918c.csv | human_plus_geometry | e247_common_vs_e284_extra | -0.000001494 | 0.000000000 | 2.550886662 | -0.014013587 | 1.402110817 | 0.053301245 | 6 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_swap_low_high_top3_754c906f.csv | cell_geometry | e247_body_vs_clean_neither | 0.000006599 | 0.000000000 | 2.416123008 | 0.036174195 | 1.674944099 | 0.066299179 | 6 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_add_high_preserve_top3_3b1c3d2e.csv | cell_geometry | e247_body_vs_clean_neither | 0.000007340 | 0.000000000 | 2.512101627 | 0.124743148 | 1.642369359 | 0.066229619 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_add_high_preserve_top3_88b70a26.csv | cell_geometry | e247_body_vs_clean_neither | 0.000004180 | 0.000000000 | 2.604180028 | 0.124743148 | 1.640714421 | 0.037845496 | 3 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_paymonth_start_near3_money_rumin_top3_f0p5_165a43e0.csv | human_boundary_undo | multi | 0.000015228 | 0.000000000 | 0.565227716 | 0.132896405 | 1.961349692 | 0.133058568 | 3 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_paymonth_start_near3_money_rumin_top3_f0p25_ab2ac6d8.csv | human_boundary_undo | multi | 0.000007598 | 0.000000000 | 0.557597762 | 0.132896405 | 1.959162104 | 0.066529284 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_oldlaw__lr_l2_c0p3_raw_add_high_preserve_top3_eae4879d.csv | human_plus_oldlaw_context | e247_body_vs_clean_neither | 0.000001199 | 0.000000000 | 2.315484466 | 0.226119347 | 1.549487591 | 0.058269960 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_oldlaw__lr_l2_c0p3_raw_add_high_preserve_top3_4d726a04.csv | human_plus_oldlaw_context | e247_body_vs_clean_neither | 0.000000675 | 0.000000000 | 2.505437066 | 0.226119347 | 1.549494491 | 0.033297120 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_smooth_weighted_ctrl_undo_high_preserve_top3_40fc3712.csv | cell_geometry | e247_body_vs_clean_neither | 0.000007313 | 0.000000000 | 0.557312568 | 0.254969473 | 1.650729909 | 0.066415758 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_smooth_weighted_undo_low_preserve_top3_4d6262b1.csv | human_plus_geometry | e247_body_vs_clean_neither | -0.000002851 | 0.000000000 | 1.168577725 | 0.260575781 | 1.392576241 | 0.055715838 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_smooth_weighted_undo_low_preserve_top3_7515967c.csv | human_plus_geometry | e247_body_vs_clean_neither | -0.000001430 | 0.000000000 | 1.279521935 | 0.260575781 | 1.394173055 | 0.027857919 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_oldlaw__lr_l2_c0p3_anti_amp_ctrl_undo_high_preserve_top5_8be7e300.csv | human_plus_oldlaw_context | e247_body_vs_clean_neither | 0.000012183 | 0.000000000 | 0.562182594 | 0.278071419 | 1.653584113 | 0.107109885 | 5 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_high_e284_oldlaw_top3_f0p5_d782dddc.csv | e247_undo_rank | multi | 0.000004179 | 0.000000000 | 0.587512506 | 0.317102089 | 1.958223383 | 0.097371711 | 3 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_high_e284_oldlaw_top3_f0p25_16fd395c.csv | e247_undo_rank | multi | 0.000002079 | 0.000000000 | 0.637792969 | 0.317102089 | 1.957603407 | 0.048685856 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_anti_amp_swap_low_high_top3_74b24159.csv | human_plus_geometry | e247_body_vs_clean_neither | 0.000004167 | 0.000000000 | 1.366071545 | 0.319255534 | 1.665372086 | 0.100149170 | 6 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_jepa_prednorm_dateblock_bedtime__top5_f0p25_9206c97f.csv | human_boundary_undo | multi | 0.000007235 | 0.000000000 | 0.557234857 | 0.332012623 | 1.985203910 | 0.074628878 | 5 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e256like_z_jepa_prednorm_dateblock_bedtime__top5_f0p5_2f25b414.csv | human_boundary_undo | multi | 0.000014485 | 0.000000000 | 0.771627588 | 0.332012623 | 1.988514130 | 0.149257756 | 5 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_only_vs_e256__human_social_lr_l1_c0p2_raw_undo_low_preserve_top5_9aa3e3a1.csv | human_social | e247_only_vs_e256_only | 0.000010642 | 0.000000000 | 0.560642142 | 0.336802601 | 1.603363950 | 0.131722395 | 5 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_only_vs_e256__human_social_lr_l1_c0p2_raw_undo_low_preserve_top5_be9d8f4d.csv | human_social | e247_only_vs_e256_only | 0.000021393 | 0.000000000 | 0.826154744 | 0.336802601 | 1.608743123 | 0.263444789 | 5 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e247like_ctrl_smooth_z_top3_f0p5_1350e4c1.csv | human_boundary_control | multi | 0.000014660 | 0.000000000 | 0.564660483 | 0.372149765 | 1.961116219 | 0.132831515 | 3 | safe_but_too_small_or_wrong_sign |
| e285 | submission_e285_e247resid_undo_e247like_ctrl_smooth_z_top3_f0p25_40fc3712.csv | human_boundary_control | multi | 0.000007313 | 0.000000000 | 0.557312568 | 0.372149765 | 1.959044012 | 0.066415758 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_oldlaw__lr_l1_c0p2_raw_ctrl_undo_high_preserve_top5_ab16dfaa.csv | human_plus_oldlaw_context | e247_body_vs_clean_neither | 0.000016138 | 0.000000000 | 0.566138459 | 0.376248722 | 1.655793027 | 0.142980860 | 5 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_anti_amp_undo_low_preserve_top3_b2cc75ee.csv | human_plus_geometry | e247_body_vs_clean_neither | 0.000007680 | 0.000000000 | 0.955299122 | 0.379873710 | 1.520398252 | 0.124607348 | 3 | safe_but_too_small_or_wrong_sign |
| e286 | submission_e286_e247contrast_e247_body_vs_clean_human_plus_geometr_lr_l2_c0p3_anti_amp_undo_low_preserve_top3_e602638e.csv | human_plus_geometry | e247_body_vs_clean_neither | 0.000003835 | 0.000000000 | 0.734786896 | 0.379873710 | 1.518771782 | 0.062303674 | 3 | safe_but_too_small_or_wrong_sign |

## Prefilter

- generated candidates: `360`
- old strict candidates: `33`
- info candidates: `134`
- null-evaluated candidates: `40`

| recipe | generated | old_strict | info | best_p90 | best_mean | median_l1 |
| --- | --- | --- | --- | --- | --- | --- |
| single_human_ready_lift | 360 | 33 | 134 | -0.000087616 | -0.000142712 | 0.512166280 |

## Matched Null Governor

- public-free ready candidates: `0`

| recipe | evaluated | old_strict | ready | best_p90 | best_null_strict | best_worst_mode |
| --- | --- | --- | --- | --- | --- | --- |
| single_human_ready_lift | 40 | 27 | 0 | -0.000087616 | 0.000000000 | 0.666666667 |

| basename | recipe | seed_count | nonzero_rows | nonzero_cells | l1_delta | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e314_humanready_single_rank1_kall_w12_0_d2ad305c.csv | single_human_ready_lift | 1 | 3 | 3 | 0.644885187 | -0.000081031 | -0.000054758 | 0.346153846 | 0.807692308 | 0.307692308 | 0.500000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k3_w12_0_d2ad305c.csv | single_human_ready_lift | 1 | 3 | 3 | 0.644885187 | -0.000081031 | -0.000054758 | 0.500000000 | 0.538461538 | 0.192307692 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k8_w12_0_d2ad305c.csv | single_human_ready_lift | 1 | 3 | 3 | 0.644885187 | -0.000081031 | -0.000054758 | 0.576923077 | 0.653846154 | 0.230769231 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k5_w12_0_d2ad305c.csv | single_human_ready_lift | 1 | 3 | 3 | 0.644885187 | -0.000081031 | -0.000054758 | 0.576923077 | 0.538461538 | 0.153846154 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank7_k5_w26_0_4e9e20bb.csv | single_human_ready_lift | 1 | 5 | 5 | 1.080674000 | -0.000099607 | -0.000055394 | 0.615384615 | 0.461538462 | 0.307692308 | 0.000000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k8_w26_0_59e818a4.csv | single_human_ready_lift | 1 | 3 | 3 | 0.954160192 | -0.000142712 | -0.000087616 | 0.692307692 | 0.807692308 | 0.307692308 | 0.666666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k20_w26_0_59e818a4.csv | single_human_ready_lift | 1 | 3 | 3 | 0.954160192 | -0.000142712 | -0.000087616 | 0.692307692 | 0.692307692 | 0.307692308 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k5_w26_0_59e818a4.csv | single_human_ready_lift | 1 | 3 | 3 | 0.954160192 | -0.000142712 | -0.000087616 | 0.692307692 | 0.730769231 | 0.269230769 | 0.333333333 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k8_w18_0_b333d023.csv | single_human_ready_lift | 1 | 3 | 3 | 0.792327780 | -0.000110523 | -0.000071696 | 0.692307692 | 0.692307692 | 0.307692308 | 0.333333333 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k20_w18_0_b333d023.csv | single_human_ready_lift | 1 | 3 | 3 | 0.792327780 | -0.000110523 | -0.000071696 | 0.692307692 | 0.807692308 | 0.307692308 | 0.500000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k12_w18_0_b333d023.csv | single_human_ready_lift | 1 | 3 | 3 | 0.792327780 | -0.000110523 | -0.000071696 | 0.692307692 | 0.769230769 | 0.269230769 | 0.333333333 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k3_w18_0_b333d023.csv | single_human_ready_lift | 1 | 3 | 3 | 0.792327780 | -0.000110523 | -0.000071696 | 0.692307692 | 0.692307692 | 0.192307692 | 0.500000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank7_k12_w26_0_d5dd85d8.csv | single_human_ready_lift | 1 | 6 | 6 | 1.225908396 | -0.000117972 | -0.000071567 | 0.692307692 | 0.615384615 | 0.307692308 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank7_k20_w26_0_d5dd85d8.csv | single_human_ready_lift | 1 | 6 | 6 | 1.225908396 | -0.000117972 | -0.000071567 | 0.692307692 | 0.500000000 | 0.307692308 | 0.000000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank7_kall_w26_0_d5dd85d8.csv | single_human_ready_lift | 1 | 6 | 6 | 1.225908396 | -0.000117972 | -0.000071567 | 0.692307692 | 0.500000000 | 0.269230769 | 0.000000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank2_k12_w26_0_ed9b6ac1.csv | single_human_ready_lift | 1 | 3 | 3 | 0.715095946 | -0.000095131 | -0.000063880 | 0.692307692 | 0.692307692 | 0.346153846 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank2_kall_w26_0_ed9b6ac1.csv | single_human_ready_lift | 1 | 3 | 3 | 0.715095946 | -0.000095131 | -0.000063880 | 0.692307692 | 0.807692308 | 0.230769231 | 0.500000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank2_k8_w26_0_ed9b6ac1.csv | single_human_ready_lift | 1 | 3 | 3 | 0.715095946 | -0.000095131 | -0.000063880 | 0.692307692 | 0.730769231 | 0.230769231 | 0.333333333 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k3_w26_0_59e818a4.csv | single_human_ready_lift | 1 | 3 | 3 | 0.954160192 | -0.000142712 | -0.000087616 | 0.730769231 | 0.730769231 | 0.230769231 | 0.500000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k12_w26_0_59e818a4.csv | single_human_ready_lift | 1 | 3 | 3 | 0.954160192 | -0.000142712 | -0.000087616 | 0.730769231 | 0.692307692 | 0.153846154 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_kall_w18_0_b333d023.csv | single_human_ready_lift | 1 | 3 | 3 | 0.792327780 | -0.000110523 | -0.000071696 | 0.730769231 | 0.730769231 | 0.230769231 | 0.333333333 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k5_w18_0_b333d023.csv | single_human_ready_lift | 1 | 3 | 3 | 0.792327780 | -0.000110523 | -0.000071696 | 0.730769231 | 0.653846154 | 0.192307692 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank7_k8_w26_0_d5dd85d8.csv | single_human_ready_lift | 1 | 6 | 6 | 1.225908396 | -0.000117972 | -0.000071567 | 0.730769231 | 0.500000000 | 0.230769231 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_kall_w26_0_59e818a4.csv | single_human_ready_lift | 1 | 3 | 3 | 0.954160192 | -0.000142712 | -0.000087616 | 0.769230769 | 0.615384615 | 0.192307692 | 0.000000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank2_k5_w26_0_ed9b6ac1.csv | single_human_ready_lift | 1 | 3 | 3 | 0.715095946 | -0.000095131 | -0.000063880 | 0.769230769 | 0.730769231 | 0.230769231 | 0.666666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank2_k20_w26_0_ed9b6ac1.csv | single_human_ready_lift | 1 | 3 | 3 | 0.715095946 | -0.000095131 | -0.000063880 | 0.769230769 | 0.500000000 | 0.192307692 | 0.000000000 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank2_k3_w26_0_ed9b6ac1.csv | single_human_ready_lift | 1 | 3 | 3 | 0.715095946 | -0.000095131 | -0.000063880 | 0.807692308 | 0.615384615 | 0.153846154 | 0.166666667 | blocked_by_human_ready_lift_nulls |
| submission_e314_humanready_single_rank1_k8_w8_0_aa0e9343.csv | single_human_ready_lift | 1 | 3 | 3 | 0.471164578 | -0.000050558 | -0.000035024 | 0.000000000 | 0.500000000 | 0.307692308 | 0.000000000 | too_small_to_submit |
| submission_e314_humanready_single_rank1_kall_w8_0_aa0e9343.csv | single_human_ready_lift | 1 | 3 | 3 | 0.471164578 | -0.000050558 | -0.000035024 | 0.000000000 | 0.346153846 | 0.192307692 | 0.000000000 | too_small_to_submit |
| submission_e314_humanready_single_rank1_k5_w8_0_aa0e9343.csv | single_human_ready_lift | 1 | 3 | 3 | 0.471164578 | -0.000050558 | -0.000035024 | 0.000000000 | 0.307692308 | 0.192307692 | 0.000000000 | too_small_to_submit |
| submission_e314_humanready_single_rank1_k20_w8_0_aa0e9343.csv | single_human_ready_lift | 1 | 3 | 3 | 0.471164578 | -0.000050558 | -0.000035024 | 0.000000000 | 0.307692308 | 0.192307692 | 0.000000000 | too_small_to_submit |
| submission_e314_humanready_single_rank1_k3_w8_0_aa0e9343.csv | single_human_ready_lift | 1 | 3 | 3 | 0.471164578 | -0.000050558 | -0.000035024 | 0.000000000 | 0.346153846 | 0.153846154 | 0.000000000 | too_small_to_submit |
| submission_e314_humanready_single_rank1_k12_w8_0_aa0e9343.csv | single_human_ready_lift | 1 | 3 | 3 | 0.471164578 | -0.000050558 | -0.000035024 | 0.076923077 | 0.384615385 | 0.153846154 | 0.000000000 | too_small_to_submit |
| submission_e314_humanready_single_rank2_kall_w18_0_6b6edf9b.csv | single_human_ready_lift | 1 | 3 | 3 | 0.602758732 | -0.000072524 | -0.000047603 | 0.230769231 | 0.730769231 | 0.230769231 | 0.333333333 | too_small_to_submit |
| submission_e314_humanready_single_rank2_k12_w18_0_6b6edf9b.csv | single_human_ready_lift | 1 | 3 | 3 | 0.602758732 | -0.000072524 | -0.000047603 | 0.269230769 | 0.653846154 | 0.307692308 | 0.166666667 | too_small_to_submit |
| submission_e314_humanready_single_rank2_k8_w18_0_6b6edf9b.csv | single_human_ready_lift | 1 | 3 | 3 | 0.602758732 | -0.000072524 | -0.000047603 | 0.269230769 | 0.576923077 | 0.230769231 | 0.166666667 | too_small_to_submit |
| submission_e314_humanready_single_rank2_k3_w18_0_6b6edf9b.csv | single_human_ready_lift | 1 | 3 | 3 | 0.602758732 | -0.000072524 | -0.000047603 | 0.346153846 | 0.576923077 | 0.307692308 | 0.166666667 | too_small_to_submit |
| submission_e314_humanready_single_rank2_k20_w18_0_6b6edf9b.csv | single_human_ready_lift | 1 | 3 | 3 | 0.602758732 | -0.000072524 | -0.000047603 | 0.384615385 | 0.538461538 | 0.269230769 | 0.166666667 | too_small_to_submit |
| submission_e314_humanready_single_rank2_k5_w18_0_6b6edf9b.csv | single_human_ready_lift | 1 | 3 | 3 | 0.602758732 | -0.000072524 | -0.000047603 | 0.500000000 | 0.461538462 | 0.153846154 | 0.000000000 | too_small_to_submit |
| submission_e314_humanready_single_rank7_k5_w18_0_6a6bbca7.csv | single_human_ready_lift | 1 | 5 | 5 | 0.855851231 | -0.000072830 | -0.000047232 | 0.500000000 | 0.384615385 | 0.230769231 | 0.000000000 | too_small_to_submit |

## Decision

- No E314 human-readiness lift is public-free ready.
- If generated candidates become old-strict but null-common, human-readiness is not enough to cross the visibility/null-rarity cliff by individual scalar lift.
- If top rows remain safe-but-too-small, the next action needs a different target-level materializer rather than more amplitude.
- Consensus/orthogonal-stack recipes still need a quota-reserved E314b run before they can be judged.

## Outputs

- `analysis_outputs/e314_human_ready_lift_candidates.csv`
- `analysis_outputs/e314_human_ready_lift_selected.csv`
- `analysis_outputs/e314_human_ready_lift_governor.csv`
- `analysis_outputs/e314_human_ready_lift_scores.csv`
- `analysis_outputs/e314_human_ready_lift_null_map.csv`
- `analysis_outputs/e314_human_ready_lift_report.md`
