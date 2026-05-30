# E308 Governed Action-Outcome Atlas

Public LB는 사용하지 않았다. E279-E307 matched-null governor 결과를 하나의 supervision table로 묶고, action outcome이 leave-experiment-out으로 예측 가능한지 확인했다.

## Dataset

- governed candidate rows: `1304`
- experiments loaded: `18`
- numeric features for outcome model: `122`
- categorical features for outcome model: `4`

## Counts

- selector_visible: `367`
- null_rare: `918`
- visible_null_rare: `2`
- strict_large_null_ready raw: `1`
- certified_public_free_ready after E301 supersession: `0`
- post-S4-handbuilt rows E299-E307: `260`, visible_null_rare `2`
- post-E303 S4 rows: `68`, visible_null_rare `0`, null_rare `0`

## Leave-Experiment-Out Outcome Models

| task | n_valid | positive_rate | auc | average_precision | mae | spearman | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| selector_visible | 1304 | 0.281441718 | 0.998857156 | 0.997192957 |  |  | 0.299299220 |
| null_rare | 1304 | 0.703987730 | 0.982793751 | 0.987580507 |  |  | 0.661852691 |
| null_common | 1304 | 0.277607362 | 0.986466434 | 0.968662000 |  |  | 0.305653942 |
| visible_null_common | 1304 | 0.273773006 | 0.989141591 | 0.965909878 |  |  | 0.293658927 |
| edge_ok | 1304 | 0.282208589 | 0.997822603 | 0.994663163 |  |  | 0.305473659 |
| null_strict_rate | 1304 |  |  |  | 0.144815064 | 0.775868457 | 0.266993661 |
| actual_p90 | 1304 |  |  |  | 0.000029494 | 0.944567710 | 0.000008169 |

## Group Summary

| experiment | target_norm | family | outcome_quadrant | n | selector_visible | null_rare | visible_null_rare | visible_null_common | best_actual_p90 | best_null_strict | best_mean_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e300 | multi | unknown | ready_like | 1 | 1 | 1 | 1 | 0 | -0.000051307 | 0.095238095 | 0.714285714 |
| e299 | multi | unknown | visible_null_rare_but_weak_dominance | 1 | 1 | 1 | 1 | 0 | -0.000050918 | 0.095238095 | 0.476190476 |
| e300 | multi | unknown | visible_but_null_common | 83 | 83 | 0 | 0 | 83 | -0.000094964 | 0.428571429 | 0.809523810 |
| e299 | multi | unknown | visible_but_null_common | 47 | 47 | 0 | 0 | 47 | -0.000557161 | 0.428571429 | 0.857142857 |
| e293 | multi | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv | visible_but_null_common | 37 | 37 | 0 | 0 | 37 | -0.000228841 | 0.476190476 | 0.714285714 |
| e307 | multi | unknown | visible_but_null_common | 22 | 22 | 0 | 0 | 22 | -0.000197843 | 0.750000000 | 0.546875000 |
| e306 | multi | unknown | visible_but_null_common | 20 | 20 | 0 | 0 | 20 | -0.000114916 | 0.625000000 | 0.671875000 |
| e290 | Q3 | Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow | visible_but_null_common | 16 | 16 | 0 | 0 | 16 | -0.000298834 | 0.466666667 | 0.533333333 |
| e305 | multi | unknown | visible_but_null_common | 14 | 14 | 0 | 0 | 14 | -0.000127522 | 0.648437500 | 0.562500000 |
| e279 | multi | unknown | visible_but_null_common | 13 | 13 | 0 | 0 | 13 | -0.000129314 | 0.666666667 | 0.476190476 |
| e303 | multi | unknown | visible_but_null_common | 11 | 11 | 0 | 0 | 11 | -0.000074119 | 0.601562500 | 0.695312500 |
| e297 | S1 | routine_fragmentation | visible_but_null_common | 10 | 10 | 0 | 0 | 10 | -0.000565475 | 0.904761905 | 0.857142857 |
| e297 | S1 | bedtime_arousal | visible_but_null_common | 10 | 10 | 0 | 0 | 10 | -0.000525463 | 0.714285714 | 0.571428571 |
| e290 | Q3 | Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2 | visible_but_null_common | 8 | 8 | 0 | 0 | 8 | -0.000308253 | 1.000000000 | 0.533333333 |
| e293 | multi | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_mean_good_subject_cv | visible_but_null_common | 8 | 8 | 0 | 0 | 8 | -0.000245446 | 1.000000000 | 0.666666667 |
| e291 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv | visible_but_null_common | 6 | 6 | 0 | 0 | 6 | -0.000226541 | 0.666666667 | 0.600000000 |
| e289 | Q3 | family_jepa_context | visible_but_null_common | 4 | 4 | 0 | 0 | 4 | -0.000417427 | 1.000000000 | 0.733333333 |
| e289 | Q3 | raw_human_context | visible_but_null_common | 4 | 4 | 0 | 0 | 4 | -0.000385893 | 1.000000000 | 0.933333333 |
| e291 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_mean_good_subject_cv | visible_but_null_common | 4 | 4 | 0 | 0 | 4 | -0.000190085 | 1.000000000 | 0.533333333 |
| e293 | multi | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_mean_good_dateblock_cv | visible_but_null_common | 3 | 3 | 0 | 0 | 3 | -0.000267622 | 1.000000000 | 0.380952381 |
| e290 | Q3 | Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow | visible_but_null_common | 3 | 3 | 0 | 0 | 3 | -0.000105463 | 0.933333333 | 0.466666667 |
| e300 | multi | unknown | visible_but_null_not_rare | 3 | 3 | 0 | 0 | 0 | -0.000054171 | 0.190476190 | 0.666666667 |
| e291 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekend_strong35_subject_cv | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000314151 | 1.000000000 | 0.733333333 |
| e289 | S4 | family_jepa_context | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000268727 | 1.000000000 | 0.466666667 |
| e291 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekday_strong35_subject_cv | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000268588 | 1.000000000 | 0.333333333 |
| e291 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_mean_good_dateblock_cv | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000239985 | 1.000000000 | 0.533333333 |
| e289 | S4 | raw_human_context | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000238160 | 1.000000000 | 0.533333333 |
| e290 | Q3 | Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1 | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000233068 | 1.000000000 | 0.666666667 |
| e290 | Q3 | Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l2 | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000183078 | 1.000000000 | 0.666666667 |
| e291 | S4 | S4_raw_human_context_dateblock5_cluster6_subject_weekday_strong35_subject_cv | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000172845 | 1.000000000 | 0.466666667 |
| e292 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekday_strong35_subject_cv_contrast_half_bf70 | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000156679 | 1.000000000 | 0.466666667 |
| e292 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekday_strong35_subject_cv_rarity_half_bf70 | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000144738 | 1.000000000 | 0.600000000 |
| e290 | Q3 | Q3_raw_human_context_subject5_pc_strong35_subject5_hgb_shallow | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000142722 | 1.000000000 | 0.466666667 |
| e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_contrast_half_bf70 | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000125983 | 0.866666667 | 0.533333333 |
| e292 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekday_strong35_subject_cv_contrast_third_bf70 | visible_but_null_common | 2 | 2 | 0 | 0 | 2 | -0.000106094 | 0.866666667 | 0.400000000 |

## Nearest Rows

| experiment | target_norm | family | outcome_quadrant | failure_mode | selector_visible | null_rare | visible_null_rare | actual_p90 | null_strict_rate | mean_dominance | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e300 | multi | unknown | ready_like | survives_all_public_free_gates | True | True | True | -0.000051307 | 0.095238095 | 0.714285714 | submission_e300_s4mean_drop_dateblock_id07_b9_raw_m1p16_d285ff4a.csv |
| e299 | multi | unknown | visible_null_rare_but_weak_dominance | mean_dominance_shortfall | True | True | True | -0.000050918 | 0.095238095 | 0.476190476 | submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p970_66cc85cf.csv |
| e303 | multi | unknown | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000052481 | 0.187500000 | 0.593750000 | submission_e303_s4meanprior_single_prior_drop_worst12_raw_m0p85_709df9bb.csv |
| e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_base_lowmax35_bf70 | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000052582 | 0.133333333 | 0.466666667 | submission_e292_contrastlife_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_base_lo_f83c007a.csv |
| e300 | multi | unknown | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000051611 | 0.380952381 | 0.666666667 | submission_e300_s4mean_drop_dateblock_id01_b4_raw_m1p16_67acd4d3.csv |
| e299 | multi | unknown | visible_but_null_common | matched_null_hallucination | True | False | False | -0.000059832 | 0.428571429 | 0.761904762 | submission_e299_bridge_null_rare_edge_near_e297_epstate_routine_fragmentation_S1_raw_human_context_date_m1p200_e02cc4bc.csv |
| e300 | multi | unknown | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000054171 | 0.190476190 | 0.428571429 | submission_e300_s4mean_abs_top35_raw_m1p16_76734941.csv |
| e300 | multi | unknown | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000052159 | 0.285714286 | 0.523809524 | submission_e300_s4mean_drop_dateblock_id02_b5_raw_m1p16_7cdd0efe.csv |
| e299 | multi | unknown | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000050909 | 0.190476190 | 0.428571429 | submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p990_9a53d270.csv |
| e292 | S4 | S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_dateblock_cv_contrast_half_bf70 | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000051437 | 0.200000000 | 0.400000000 | submission_e292_contrastlife_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_dateblock_cv_contr_0ddd0196.csv |
| e299 | multi | unknown | visible_but_null_not_rare | matched_null_not_rare | True | False | False | -0.000052025 | 0.238095238 | 0.428571429 | submission_e299_bridge_visible_low_null_near_e292_contrastlife_S4_family_jepa_context_dateblock5_cluste_m0p990_df233e89.csv |
| e297 | S1 | routine_fragmentation | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000048876 | 0.095238095 | 0.809523810 | submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_all_centered_s006_7e48318e.csv |
| e300 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000046217 | 0.000000000 | 0.714285714 | submission_e300_s4mean_drop_dateblock_id07_b10_raw_m1p16_309fc05d.csv |
| e299 | multi | unknown | visible_but_null_common | matched_null_hallucination | True | False | False | -0.000066403 | 0.571428571 | 0.714285714 | submission_e299_bridge_null_rare_edge_near_e297_epstate_routine_fragmentation_S1_raw_human_context_date_m1p300_023271ed.csv |
| e297 | S1 | routine_fragmentation | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000021188 | 0.000000000 | 0.761904762 | submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs64_s006_55330ee9.csv |
| e300 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000049441 | 0.047619048 | 0.666666667 | submission_e300_s4mean_drop_subject_id03_pos_raw_m1p16_66e72ced.csv |
| e297 | S1 | routine_fragmentation | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000046502 | 0.095238095 | 0.666666667 | submission_e297_epstate_routine_fragmentation_S1_raw_human_context_dateblock5_topabs16_s015_c61fbdcd.csv |
| e300 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000045725 | 0.000000000 | 0.666666667 | submission_e300_s4mean_drop_subject_id03_pos_raw_m1p08_022c2d92.csv |
| e292 | Q3 | Q3_family_jepa_context_dateblock5_pc_subject_weekday_strong35_subject_cv_base_lowmax35_bf70 | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000043631 | 0.000000000 | 0.666666667 | submission_e292_contrastlife_Q3_family_jepa_context_dateblock5_pc_subject_weekday_strong35_subject_cv_base_lowmax35_bf70__06636bce.csv |
| e285 | multi | human_boundary_add | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000003481 | 0.000000000 | 0.809523810 | submission_e285_e247resid_add_e247like_z_diary_state_pc6_top5_f0p25_6f3cde41.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000002460 | 0.000000000 | 1.000000000 | submission_e269_phonebed_e247only_top8_amp015_bd6b7fee.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000001908 | 0.000000000 | 0.952380952 | submission_e269_phonebed_e247only_top5_amp025_d487a8ab.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000001460 | 0.000000000 | 0.857142857 | submission_e269_e247only_all_amp006_control_2cef7c9d.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000001312 | 0.000000000 | 0.952380952 | submission_e271_calendar_only_control_top8_36405aed.csv |
| e279 | multi | unknown | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | -0.000000763 | 0.000000000 | 0.809523810 | submission_e271_cashflow_top6_amp014_ecc2b44c.csv |
| e285 | multi | human_boundary_add | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | 0.000000365 | 0.000000000 | 0.761904762 | submission_e285_e247resid_add_e247like_amp_z_top3_f0p25_aa6c6b32.csv |
| e286 | e247_common_vs_e284_extra | cell_geometry | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | 0.000000630 | 0.000000000 | 0.857142857 | submission_e286_e247contrast_e247_common_vs_e28_cell_geometry_lr_l2_c0p3_raw_undo_low_preserve_top3_9b72c3db.csv |
| e286 | e247_common_vs_e284_extra | cell_geometry | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | 0.000001266 | 0.000000000 | 0.857142857 | submission_e286_e247contrast_e247_common_vs_e28_cell_geometry_lr_l2_c0p3_raw_undo_low_preserve_top3_1686bb8e.csv |
| e285 | multi | e247_undo_rank | null_rare_but_no_selector_edge | safe_but_too_small_or_wrong_sign | False | True | False | 0.000001373 | 0.000000000 | 0.904761905 | submission_e285_e247resid_undo_low_smooth_top3_f0p25_5ce11742.csv |
| e300 | multi | unknown | visible_but_null_common | matched_null_hallucination | True | False | False | -0.000055274 | 0.428571429 | 0.476190476 | submission_e300_s4mean_drop_dateblock_id02_b10_raw_m1p16_04e140b6.csv |

## Null-Common Model Top Coefficients

| feature | coef_null_common | abs_coef |
| --- | --- | --- |
| num__old_strict_promote | 1.784970069 | 1.784970069 |
| num__actual_beats_current_rate | 0.987505213 | 0.987505213 |
| num__actual_p10 | -0.870315689 | 0.870315689 |
| num__actual_mean | -0.744677224 | 0.744677224 |
| num__post_e303_s4_handbuilt | 0.723486104 | 0.723486104 |
| num__test_delta_mean | 0.576587248 | 0.576587248 |
| num__actual_p90 | -0.544970369 | 0.544970369 |
| num__source_actual_p90 | -0.540336973 | 0.540336973 |
| num__strict_promote_gate | 0.509079243 | 0.509079243 |
| num__add_fraction | 0.497769796 | 0.497769796 |
| num__post_s4_handbuilt | 0.488785228 | 0.488785228 |
| num__nonzero_cells | 0.409518740 | 0.409518740 |
| num__undo_fraction | 0.406967465 | 0.406967465 |
| num__neg_rows | -0.388413471 | 0.388413471 |
| num__train_actual_delta | -0.360688082 | 0.360688082 |
| num__add_count | -0.344712022 | 0.344712022 |
| num__multiplier | 0.287456715 | 0.287456715 |
| num__fraction | -0.279078874 | 0.279078874 |
| num__scale | 0.262703836 | 0.262703836 |
| num__pred_delta_vs_current_p10 | -0.260828700 | 0.260828700 |
| num__min_ap_lift | 0.251921627 | 0.251921627 |
| num__experiment_num | -0.246177785 | 0.246177785 |
| num__mean_abs_delta_S4 | -0.234939577 | 0.234939577 |
| num__pos_rows | 0.232222798 | 0.232222798 |
| num__test_selected_blocks | 0.226210863 | 0.226210863 |

## Decision

- No certified public-free candidate exists in the governed archive.
- The two visible/null-rare S4 rows before E303 were not enough: one is the E300 small-governor row superseded by E301, and post-E303 S4 action families have `0` null-rare rows.
- The learned outcome table is useful as a diagnostic, but positive labels for `visible_null_rare` are too sparse to generate submissions directly.
- Next high-value experiment should pivot from hand-built S4 deltas to a different target interaction or create synthetic/action-health training labels with explicit controls.

## Outputs

- `analysis_outputs/e308_action_outcome_all.csv`
- `analysis_outputs/e308_action_outcome_group_summary.csv`
- `analysis_outputs/e308_action_outcome_model_oof.csv`
- `analysis_outputs/e308_action_outcome_model_summary.csv`
- `analysis_outputs/e308_action_outcome_feature_importance.csv`
- `analysis_outputs/e308_action_outcome_report.md`
