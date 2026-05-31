# E315 Human-Readiness Composition Materializer

Public LB는 사용하지 않았다. E314가 남긴 공백인 non-single human-ready composition을 검증했다. 단일 seed lift는 금지하고, family/target consensus, negative-edge stack, orthogonal story stack, target-balanced story stack만 생성했다.

Question: 여러 human/social seed가 같은 숨은 생활 상태를 바라본다면, 조합된 action geometry는 단일 seed amplitude와 달리 matched null을 이길 수 있는가?

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

- generated candidates: `660`
- old strict candidates: `229`
- info candidates: `297`
- null-evaluated candidates: `67`

| recipe | generated | old_strict | info | best_p90 | best_mean | median_l1 |
| --- | --- | --- | --- | --- | --- | --- |
| ranked_negative_stack | 120 | 95 | 25 | -0.000217727 | -0.000312515 | 1.050000000 |
| family_consensus | 180 | 66 | 96 | -0.000338863 | -0.000671327 | 3.791483261 |
| orthogonal_story_stack | 150 | 48 | 55 | -0.000342131 | -0.000822501 | 5.089820972 |
| target_balanced_story_stack | 60 | 15 | 30 | -0.000089512 | -0.000210017 | 11.722482679 |
| target_consensus | 150 | 5 | 91 | -0.000523248 | -0.001506650 | 7.000000000 |

## Matched Null Governor

- public-free ready candidates: `0`

| recipe | evaluated | old_strict | ready | best_p90 | best_null_strict | best_worst_mode |
| --- | --- | --- | --- | --- | --- | --- |
| family_consensus | 18 | 17 | 0 | -0.000338863 | 0.454545455 | 0.800000000 |
| ranked_negative_stack | 13 | 13 | 0 | -0.000217727 | 0.590909091 | 1.000000000 |
| orthogonal_story_stack | 12 | 6 | 0 | -0.000342131 | 0.090909091 | 0.800000000 |
| target_balanced_story_stack | 6 | 6 | 0 | -0.000089512 | 0.409090909 | 0.000000000 |
| target_consensus | 18 | 0 | 0 | -0.000523248 | 0.363636364 | 0.800000000 |

| basename | recipe | seed_count | nonzero_rows | nonzero_cells | l1_delta | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e315_humancomp_tbstory_bedtime_arousal_all_call_w1_50_98ae1d86.csv | target_balanced_story_stack | 2 | 41 | 87 | 6.867003977 | -0.000186720 | -0.000089512 | 0.409090909 | 0.818181818 | 0.909090909 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_tbstory_bedtime_arousal_s_call_w1_50_98ae1d86.csv | target_balanced_story_stack | 2 | 41 | 87 | 6.867003977 | -0.000186720 | -0.000089512 | 0.409090909 | 0.818181818 | 0.863636364 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_tbstory_bedtime_arousal_s_c96_w1_50_98ae1d86.csv | target_balanced_story_stack | 2 | 41 | 87 | 6.867003977 | -0.000186720 | -0.000089512 | 0.409090909 | 0.772727273 | 0.818181818 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c160_w12_00_6e0c7ea0.csv | family_consensus | 4 | 41 | 87 | 12.304791619 | -0.000460487 | -0.000264853 | 0.454545455 | 0.863636364 | 0.772727273 | 0.600000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_tbstory_bedtime_arousal_all_c96_w1_50_98ae1d86.csv | target_balanced_story_stack | 2 | 41 | 87 | 6.867003977 | -0.000186720 | -0.000089512 | 0.454545455 | 0.818181818 | 0.863636364 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c48_w8_00_af769609.csv | family_consensus | 4 | 32 | 48 | 13.217701734 | -0.000574945 | -0.000336672 | 0.500000000 | 0.727272727 | 0.681818182 | 0.400000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c160_w8_00_6d271745.csv | family_consensus | 4 | 41 | 87 | 15.465654190 | -0.000511492 | -0.000293559 | 0.500000000 | 0.954545455 | 0.727272727 | 0.800000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_orth_s0_n3_maxavg_c64_w5_00_deb13e14.csv | orthogonal_story_stack | 3 | 27 | 50 | 6.222499784 | -0.000254560 | -0.000184223 | 0.500000000 | 0.909090909 | 0.454545455 | 0.600000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_tbstory_bedtime_arousal_qs_c96_w1_50_98ae1d86.csv | target_balanced_story_stack | 2 | 41 | 87 | 6.867003977 | -0.000186720 | -0.000089512 | 0.500000000 | 0.727272727 | 0.818181818 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_call_w8_00_6d271745.csv | family_consensus | 4 | 41 | 87 | 15.465654190 | -0.000511492 | -0.000293559 | 0.545454545 | 0.909090909 | 0.818181818 | 0.600000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c96_w8_00_6d271745.csv | family_consensus | 4 | 41 | 87 | 15.465654190 | -0.000511492 | -0.000293559 | 0.545454545 | 0.863636364 | 0.772727273 | 0.600000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c160_w5_00_5548dd85.csv | family_consensus | 4 | 41 | 87 | 12.069038065 | -0.000411450 | -0.000199706 | 0.545454545 | 0.727272727 | 0.818181818 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_call_w5_00_5548dd85.csv | family_consensus | 4 | 41 | 87 | 12.069038065 | -0.000411450 | -0.000199706 | 0.545454545 | 0.590909091 | 0.727272727 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_tbstory_bedtime_arousal_qs_call_w1_50_98ae1d86.csv | target_balanced_story_stack | 2 | 41 | 87 | 6.867003977 | -0.000186720 | -0.000089512 | 0.545454545 | 0.727272727 | 0.727272727 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c96_w12_00_6e0c7ea0.csv | family_consensus | 4 | 41 | 87 | 12.304791619 | -0.000460487 | -0.000264853 | 0.590909091 | 0.863636364 | 0.863636364 | 0.600000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c48_w5_00_d15a6127.csv | family_consensus | 4 | 32 | 48 | 10.664067780 | -0.000445524 | -0.000228935 | 0.590909091 | 0.636363636 | 0.681818182 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c48_w10_00_f27cec0c.csv | ranked_negative_stack | 3 | 25 | 47 | 4.940362798 | -0.000301386 | -0.000205065 | 0.590909091 | 0.545454545 | 0.545454545 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c160_w7_00_7bdd4f0d.csv | ranked_negative_stack | 3 | 25 | 47 | 4.157516498 | -0.000270174 | -0.000192613 | 0.590909091 | 0.681818182 | 0.636363636 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_orth_s0_n3_maxavg_c128_w5_00_deb13e14.csv | orthogonal_story_stack | 3 | 27 | 50 | 6.222499784 | -0.000254560 | -0.000184223 | 0.590909091 | 0.909090909 | 0.500000000 | 0.800000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w8_00_82833aba.csv | family_consensus | 4 | 21 | 24 | 8.330724232 | -0.000548179 | -0.000291070 | 0.636363636 | 0.636363636 | 0.636363636 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_call_w12_00_6e0c7ea0.csv | family_consensus | 4 | 41 | 87 | 12.304791619 | -0.000460487 | -0.000264853 | 0.636363636 | 0.772727273 | 0.727272727 | 0.400000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c48_w12_00_e61f47be.csv | family_consensus | 4 | 32 | 48 | 10.740127980 | -0.000454611 | -0.000257824 | 0.636363636 | 0.727272727 | 0.772727273 | 0.400000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w5_00_827a8fe9.csv | family_consensus | 4 | 21 | 24 | 7.609706841 | -0.000435134 | -0.000235295 | 0.636363636 | 0.590909091 | 0.681818182 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c160_w10_00_f27cec0c.csv | ranked_negative_stack | 3 | 25 | 47 | 4.940362798 | -0.000301386 | -0.000205065 | 0.636363636 | 0.590909091 | 0.590909091 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c24_w7_00_36ae47f4.csv | ranked_negative_stack | 3 | 21 | 24 | 3.864870827 | -0.000277599 | -0.000201018 | 0.636363636 | 0.636363636 | 0.545454545 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c96_w5_00_5548dd85.csv | family_consensus | 4 | 41 | 87 | 12.069038065 | -0.000411450 | -0.000199706 | 0.636363636 | 0.772727273 | 0.727272727 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c24_w4_00_45b3e432.csv | ranked_negative_stack | 3 | 21 | 24 | 2.948979449 | -0.000249821 | -0.000198198 | 0.636363636 | 0.818181818 | 0.772727273 | 0.600000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c48_w7_00_7bdd4f0d.csv | ranked_negative_stack | 3 | 25 | 47 | 4.157516498 | -0.000270174 | -0.000192613 | 0.636363636 | 0.636363636 | 0.545454545 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c96_w4_00_f7d22a7c.csv | ranked_negative_stack | 3 | 25 | 47 | 3.116205547 | -0.000245613 | -0.000191570 | 0.636363636 | 0.818181818 | 0.681818182 | 0.600000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c160_w4_00_f7d22a7c.csv | ranked_negative_stack | 3 | 25 | 47 | 3.116205547 | -0.000245613 | -0.000191570 | 0.636363636 | 0.727272727 | 0.545454545 | 0.400000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_orth_s0_n3_maxavg_c64_w8_00_5dabd4d6.csv | orthogonal_story_stack | 3 | 27 | 50 | 7.275410857 | -0.000345492 | -0.000174392 | 0.636363636 | 0.636363636 | 0.636363636 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_orth_s0_n3_maxavg_c128_w8_00_5dabd4d6.csv | orthogonal_story_stack | 3 | 27 | 50 | 7.275410857 | -0.000345492 | -0.000174392 | 0.636363636 | 0.863636364 | 0.590909091 | 0.400000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_orth_s0_n3_maxavg_call_w8_00_5dabd4d6.csv | orthogonal_story_stack | 3 | 27 | 50 | 7.275410857 | -0.000345492 | -0.000174392 | 0.636363636 | 0.727272727 | 0.590909091 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_l1mean_c24_w12_00_0958e5f2.csv | family_consensus | 4 | 22 | 24 | 7.622449396 | -0.000474582 | -0.000290500 | 0.681818182 | 0.636363636 | 0.681818182 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c96_w10_00_f27cec0c.csv | ranked_negative_stack | 3 | 25 | 47 | 4.940362798 | -0.000301386 | -0.000205065 | 0.681818182 | 0.500000000 | 0.409090909 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c96_w7_00_7bdd4f0d.csv | ranked_negative_stack | 3 | 25 | 47 | 4.157516498 | -0.000270174 | -0.000192613 | 0.681818182 | 0.545454545 | 0.545454545 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_orth_s0_n3_maxavg_call_w5_00_deb13e14.csv | orthogonal_story_stack | 3 | 27 | 50 | 6.222499784 | -0.000254560 | -0.000184223 | 0.681818182 | 0.954545455 | 0.545454545 | 0.800000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w12_00_7d4e5920.csv | family_consensus | 4 | 21 | 24 | 8.400000000 | -0.000560152 | -0.000303502 | 0.727272727 | 0.772727273 | 0.772727273 | 0.400000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c24_w10_00_043a0d25.csv | ranked_negative_stack | 3 | 21 | 24 | 4.522297553 | -0.000312515 | -0.000217727 | 0.727272727 | 0.500000000 | 0.545454545 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c48_w4_00_f7d22a7c.csv | ranked_negative_stack | 3 | 25 | 47 | 3.116205547 | -0.000245613 | -0.000191570 | 0.727272727 | 0.727272727 | 0.500000000 | 0.200000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_family_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv__09a4b12d.csv | family_consensus | 4 | 15 | 15 | 4.464068427 | -0.000636403 | -0.000171437 | 0.772727273 | 0.454545455 | 0.545454545 | 0.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_neg_top3_l1avg_c24_w2_00_987ad0c0.csv | ranked_negative_stack | 3 | 21 | 24 | 2.121087489 | -0.000215074 | -0.000171788 | 0.818181818 | 1.000000000 | 0.590909091 | 1.000000000 | blocked_by_human_ready_composition_nulls |
| submission_e315_humancomp_orth_s0_n8_maxavg_c64_w8_00_7750cef1.csv | orthogonal_story_stack | 8 | 54 | 64 | 16.334838245 | -0.000822501 | -0.000342131 | 0.090909091 | 0.590909091 | 0.545454545 | 0.000000000 | hold_for_more_local_evidence |
| submission_e315_humancomp_orth_s0_n8_maxavg_call_w8_00_400d1da5.csv | orthogonal_story_stack | 8 | 67 | 118 | 17.514416607 | -0.000799447 | -0.000321387 | 0.090909091 | 0.727272727 | 0.636363636 | 0.200000000 | hold_for_more_local_evidence |
| submission_e315_humancomp_orth_s0_n8_maxavg_call_w5_00_9dadb527.csv | orthogonal_story_stack | 8 | 67 | 118 | 14.754218765 | -0.000686871 | -0.000258122 | 0.136363636 | 0.863636364 | 0.727272727 | 0.600000000 | hold_for_more_local_evidence |
| submission_e315_humancomp_orth_s0_n8_maxavg_c128_w5_00_9dadb527.csv | orthogonal_story_stack | 8 | 67 | 118 | 14.754218765 | -0.000686871 | -0.000258122 | 0.136363636 | 0.818181818 | 0.681818182 | 0.400000000 | hold_for_more_local_evidence |
| submission_e315_humancomp_orth_s0_n8_maxavg_c128_w8_00_400d1da5.csv | orthogonal_story_stack | 8 | 67 | 118 | 17.514416607 | -0.000799447 | -0.000321387 | 0.181818182 | 0.818181818 | 0.772727273 | 0.600000000 | hold_for_more_local_evidence |
| submission_e315_humancomp_orth_s0_n8_maxavg_c64_w5_00_7a284107.csv | orthogonal_story_stack | 8 | 54 | 64 | 14.016982289 | -0.000701049 | -0.000270334 | 0.181818182 | 0.727272727 | 0.545454545 | 0.400000000 | hold_for_more_local_evidence |
| submission_e315_humancomp_target_norm_S1_maxmean_call_w5_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.363636364 | 0.727272727 | 0.545454545 | 0.200000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_call_w3_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.409090909 | 0.727272727 | 0.500000000 | 0.200000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_c48_w8_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.454545455 | 0.863636364 | 0.409090909 | 0.800000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_c48_w5_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.454545455 | 0.954545455 | 0.409090909 | 0.800000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_c48_w3_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.454545455 | 0.954545455 | 0.500000000 | 0.800000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_c96_w1_50_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.454545455 | 0.954545455 | 0.454545455 | 0.800000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_call_w8_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.545454545 | 0.636363636 | 0.636363636 | 0.400000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_c96_w8_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.545454545 | 0.863636364 | 0.454545455 | 0.600000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_c160_w5_00_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.545454545 | 0.909090909 | 0.454545455 | 0.800000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_c160_w1_50_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.545454545 | 0.681818182 | 0.545454545 | 0.400000000 | information_sensor_only |
| submission_e315_humancomp_family_bedtime_arousal_maxmean_c48_w12_00_8467d720.csv | family_consensus | 4 | 32 | 48 | 15.255028877 | -0.000620536 | -0.000338863 | 0.545454545 | 0.727272727 | 0.772727273 | 0.200000000 | information_sensor_only |
| submission_e315_humancomp_target_norm_S1_maxmean_call_w1_50_3f3c3c9d.csv | target_consensus | 2 | 36 | 36 | 12.600000000 | -0.001506650 | -0.000523248 | 0.590909091 | 0.772727273 | 0.500000000 | 0.600000000 | information_sensor_only |

## Decision

- No E315 human-readiness composition is public-free ready.
- If generated compositions become old-strict but null-common, human-readiness composition still falls into the current action-geometry cliff.
- If null-rare compositions remain below selector resolution, the next action needs a different target-level materializer rather than broader stacking.

## Outputs

- `analysis_outputs/e315_human_ready_composition_candidates.csv`
- `analysis_outputs/e315_human_ready_composition_selected.csv`
- `analysis_outputs/e315_human_ready_composition_governor.csv`
- `analysis_outputs/e315_human_ready_composition_scores.csv`
- `analysis_outputs/e315_human_ready_composition_null_map.csv`
- `analysis_outputs/e315_human_ready_composition_report.md`
