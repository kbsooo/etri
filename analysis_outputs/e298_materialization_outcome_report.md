# E298 Materialization Outcome Atlas

Public LB는 사용하지 않았다. 기존 current-anchor governor와 matched-null 결과만 집계했다.

## 입력

- governor files loaded: 11
- candidate rows: 1044
- missing files: 0

## 핵심 카운트

- ready_like: 0
- selector_visible: 162
- null_rare: 867
- selector_visible AND null_rare: 0
- selector_visible AND null_common: 160
- null_rare AND edge_ok: 0

## Outcome Quadrants

| experiment | outcome_quadrant | n | targets | best_actual_p90 | median_null_strict_rate | min_readiness_distance |
| --- | --- | --- | --- | --- | --- | --- |
| e279 | null_rare_but_no_selector_edge | 46 | multi | -0.000026449 | 0.000000000 | 0.547540394 |
| e279 | visible_but_null_common | 13 | multi | -0.000129314 | 0.952380952 | 1.092857143 |
| e279 | adverse_or_no_edge | 7 | multi | -0.000048780 | 0.380952381 | 1.641696351 |
| e284 | null_rare_but_no_selector_edge | 9 | contrast,risk | 0.000025223 | 0.000000000 | 0.698900156 |
| e285 | null_rare_but_no_selector_edge | 158 | multi | -0.000003481 | 0.000000000 | 0.546519458 |
| e286 | null_rare_but_no_selector_edge | 533 | e247_body_vs_clean_neither,e247_common_vs_e284_extra,e247_only_vs_e256_only | -0.000004493 | 0.000000000 | 0.550630084 |
| e287 | null_rare_but_no_selector_edge | 3 | multi | -0.000034973 | 0.000000000 | 1.326932037 |
| e289 | null_rare_but_no_selector_edge | 15 | Q3,S1,S4 | 0.000010369 | 0.000000000 | 0.786849946 |
| e289 | visible_but_null_common | 12 | Q3,S4 | -0.000417427 | 1.000000000 | 1.050000000 |
| e289 | adverse_or_no_edge | 1 | S1 | 0.000009589 | 0.266666667 | 1.842922602 |
| e290 | visible_but_null_common | 33 | Q3 | -0.000308253 | 1.000000000 | 0.933333333 |
| e290 | null_rare_but_no_selector_edge | 12 | Q3 | -0.000029232 | 0.000000000 | 1.481645913 |
| e290 | adverse_or_no_edge | 3 | Q3 | -0.000048388 | 0.333333333 | 2.128331804 |
| e291 | null_rare_but_no_selector_edge | 22 | Q3,S4 | -0.000046341 | 0.000000000 | 0.782358656 |
| e291 | visible_but_null_common | 18 | Q3,S4 | -0.000314151 | 1.000000000 | 0.900000000 |
| e292 | null_rare_but_no_selector_edge | 38 | Q3,S4 | -0.000043631 | 0.000000000 | 0.539702362 |
| e292 | visible_but_null_common | 16 | Q3,S4 | -0.000156679 | 1.000000000 | 0.933333333 |
| e292 | visible_but_null_not_rare | 2 | S4 | -0.000052582 | 0.166666667 | 0.266666667 |
| e293 | visible_but_null_common | 48 | multi | -0.000267622 | 1.000000000 | 0.685714286 |
| e293 | null_rare_but_no_selector_edge | 14 | multi | -0.000044422 | 0.000000000 | 0.782336564 |
| e293 | adverse_or_no_edge | 2 | multi | -0.000049961 | 0.142857143 | 0.814325132 |
| e297 | visible_but_null_common | 20 | S1 | -0.000565475 | 1.000000000 | 0.742857143 |
| e297 | null_rare_but_no_selector_edge | 17 | S1,S2,S3 | -0.000048876 | 0.000000000 | 0.501123757 |
| e297 | adverse_or_no_edge | 2 | S1 | -0.000049338 | 0.309523810 | 0.901071436 |

## 가장 가까운 후보들

| experiment | target_norm | family | outcome_quadrant | failure_mode | readiness_defects | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e297 | S1 | routine_fragmentation | visible_but_null_common | matched_null_hallucination | 1 | -0.000096369 | 0.904761905 | 0.904761905 | 0.809523810 | 0.714285714 | submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s010_c5e3baaf.csv |
| e297 | S1 | routine_fragmentation | visible_but_null_common | matched_null_hallucination | 1 | -0.000352474 | 0.952380952 | 0.904761905 | 0.857142857 | 0.714285714 | submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s022_7c891264.csv |
| e291 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekend_strong35_subject_cv | visible_but_null_common | matched_null_hallucination | 1 | -0.000156781 | 1.000000000 | 0.933333333 | 0.733333333 | 0.800000000 | submission_e291_lifeblock_Q3_family_jepa_context_dateblock5_pc_subject_weekend_strong35_subject_cv_bf70_centered_s025_f0ca188e.csv |
| e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_base_lowmax35_bf70 | visible_but_null_not_rare | matched_null_not_rare | 2 | -0.000052582 | 0.133333333 | 0.866666667 | 0.466666667 | 0.600000000 | submission_e292_contrastlife_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_base_lo_f83c007a.csv |
| e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_dateblock_cv_contrast_half_bf70 | visible_but_null_not_rare | matched_null_not_rare | 2 | -0.000051437 | 0.200000000 | 1.000000000 | 0.400000000 | 1.000000000 | submission_e292_contrastlife_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_dateblock_cv_contr_0ddd0196.csv |
| e297 | S1 | routine_fragmentation | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000048876 | 0.095238095 | 0.904761905 | 0.809523810 | 0.714285714 | submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s006_7e48318e.csv |
| e297 | S1 | routine_fragmentation | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000021188 | 0.000000000 | 0.857142857 | 0.761904762 | 0.714285714 | submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s006_55330ee9.csv |
| e285 | multi | human_boundary_add | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000003481 | 0.000000000 | 0.952380952 | 0.809523810 | 0.857142857 | submission_e285_e247resid_add_e247like_z_diary_state_pc6_top5_f0p25_6f3cde41.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000002460 | 0.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | submission_e269_phonebed_e247only_top8_amp015_bd6b7fee.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000001908 | 0.000000000 | 0.857142857 | 0.952380952 | 0.714285714 | submission_e269_phonebed_e247only_top5_amp025_d487a8ab.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000001460 | 0.000000000 | 0.857142857 | 0.857142857 | 0.571428571 | submission_e269_e247only_all_amp006_control_2cef7c9d.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000001312 | 0.000000000 | 0.952380952 | 0.952380952 | 0.857142857 | submission_e271_calendar_only_control_top8_36405aed.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | -0.000000763 | 0.000000000 | 0.952380952 | 0.809523810 | 0.857142857 | submission_e271_cashflow_top6_amp014_ecc2b44c.csv |
| e285 | multi | human_boundary_add | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000000365 | 0.000000000 | 0.952380952 | 0.761904762 | 0.857142857 | submission_e285_e247resid_add_e247like_amp_z_top3_f0p25_aa6c6b32.csv |
| e286 | e247_common_vs_e284_extra | cell_geometry | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000000630 | 0.000000000 | 0.952380952 | 0.857142857 | 0.857142857 | submission_e286_e247contrast_e247_common_vs_e28_cell_geometry_lr_l2_c0p3_raw_undo_low_preserve_top3_9b72c3db.csv |
| e286 | e247_common_vs_e284_extra | cell_geometry | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000001266 | 0.000000000 | 0.904761905 | 0.857142857 | 0.857142857 | submission_e286_e247contrast_e247_common_vs_e28_cell_geometry_lr_l2_c0p3_raw_undo_low_preserve_top3_1686bb8e.csv |
| e285 | multi | e247_undo_rank | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000001373 | 0.000000000 | 0.904761905 | 0.904761905 | 0.714285714 | submission_e285_e247resid_undo_low_smooth_top3_f0p25_5ce11742.csv |
| e285 | multi | e247_undo_rank | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000002756 | 0.000000000 | 0.857142857 | 0.904761905 | 0.714285714 | submission_e285_e247resid_undo_low_smooth_top3_f0p5_781451e1.csv |
| e285 | multi | human_boundary_undo | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000002765 | 0.000000000 | 0.809523810 | 0.761904762 | 0.714285714 | submission_e285_e247resid_undo_e256like_z_paymonth_start_post3_late_shoppi_top3_f0p25_149092e6.csv |
| e285 | multi | human_boundary_undo | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000003046 | 0.000000000 | 0.857142857 | 0.904761905 | 0.714285714 | submission_e285_e247resid_undo_e256like_z_pay15_post3_late_shopping_subj_z_top3_f0p25_6314f6be.csv |
| e286 | e247_body_vs_clean_neither | cell_geometry | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000003273 | 0.000000000 | 0.952380952 | 0.904761905 | 0.857142857 | submission_e286_e247contrast_e247_body_vs_clean_cell_geometry_lr_l2_c0p3_anti_amp_undo_low_preserve_top3_2b344e02.csv |
| e285 | multi | human_boundary_undo | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000004432 | 0.000000000 | 0.904761905 | 0.952380952 | 0.857142857 | submission_e285_e247resid_undo_e256like_z_paymonth_start_post3_late_shoppi_top5_f0p25_bfe1796c.csv |
| e285 | multi | human_boundary_control | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000004690 | 0.000000000 | 0.809523810 | 0.857142857 | 0.714285714 | submission_e285_e247resid_undo_e247like_ctrl_z_jepa_prednorm_subject_social_top5_f0p25_875a43c2.csv |
| e286 | e247_only_vs_e256_only | human_social | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000004738 | 0.000000000 | 0.857142857 | 0.761904762 | 0.714285714 | submission_e286_e247contrast_e247_only_vs_e256__human_social_lr_l2_c0p3_raw_swap_low_high_top3_cf0afb63.csv |
| e285 | multi | e247_undo_rank | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000004986 | 0.000000000 | 0.857142857 | 0.904761905 | 0.714285714 | submission_e285_e247resid_undo_high_story_top3_f0p25_476b9ada.csv |
| e285 | multi | human_boundary_undo | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000005582 | 0.000000000 | 0.809523810 | 0.809523810 | 0.714285714 | submission_e285_e247resid_undo_e256like_z_paymonth_start_post3_late_shoppi_top3_f0p5_4ca17c93.csv |
| e285 | multi | e247_undo_rank | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000005805 | 0.000000000 | 0.809523810 | 0.857142857 | 0.714285714 | submission_e285_e247resid_undo_high_e284_oldlaw_top5_f0p25_56beeffa.csv |
| e285 | multi | human_boundary_undo | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000005981 | 0.000000000 | 0.952380952 | 1.000000000 | 0.857142857 | submission_e285_e247resid_undo_e256like_z_pay15_post3_late_shopping_subj_z_top5_f0p5_b9fb5377.csv |
| e285 | multi | human_boundary_undo | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000006131 | 0.000000000 | 0.904761905 | 0.952380952 | 0.857142857 | submission_e285_e247resid_undo_e256like_z_pay15_post3_late_shopping_subj_z_top3_f0p5_d2a4f3bb.csv |
| e286 | e247_only_vs_e256_only | human_social | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | 2 | 0.000006400 | 0.000000000 | 0.809523810 | 0.857142857 | 0.714285714 | submission_e286_e247contrast_e247_only_vs_e256__human_social_lr_l2_c0p3_smooth_weighted_swap_low_high_top3_890cca5f.csv |

## 해석

- 기존 human/social materialization 중 public-free ready 후보는 없다.
- 특히 selector-visible 후보가 null에서도 흔하게 재현되면, 그 후보는 생활 가설이 틀렸다기보다 확률 번역기가 null hallucination을 만든 것이다.

## 다음 행동

1. public LB 없이 진행한다.
2. ready_like가 없으면 새 사회적 feature를 바로 제출하지 말고, `selector_visible AND null_rare`를 목표로 하는 2-stage translator를 만든다.
3. strong social state는 feature/latent로 유지하되, submission 확률 이동은 governor-visible/null-rare placement만 허용한다.

## 산출물

- `analysis_outputs/e298_materialization_outcome_all.csv`
- `analysis_outputs/e298_materialization_outcome_family_summary.csv`
- `analysis_outputs/e298_materialization_outcome_near_miss.csv`
- `analysis_outputs/e298_materialization_outcome_quadrants.csv`
