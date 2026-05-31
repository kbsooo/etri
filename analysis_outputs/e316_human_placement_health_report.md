# E316 Human Placement-Health Learner

Public LB는 사용하지 않았다. E315의 actual/null placement들을 하나의 mini-world로 보고, raw human diary signature가 실제 placement와 건강한 placement를 구분하는지 검증했다.

## Dataset

- placement rows: `1541`
- sources: `67`
- actual rows: `67`
- placement null rows: `1005`
- all null rows: `1474`

## Actual vs Placement Null

| task | feature_block | n | positive_rate | auc | average_precision | logloss | pred_mean | target_mean | spearman | pearson | rmse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| actual_vs_placement_null | human_signature | 1072 | 0.062500 | 0.998856 | 0.992019 | 0.071854 | 0.118591 |  |  |  |  |
| actual_vs_placement_null | human_plus_shape | 1072 | 0.062500 | 0.998129 | 0.990256 | 0.072025 | 0.118475 |  |  |  |  |
| actual_vs_placement_null | action_shape | 1072 | 0.062500 | 0.500000 | 0.062500 | 0.693147 | 0.500000 |  |  |  |  |
| actual_vs_placement_null | shape_signature | 1072 | 0.062500 | 0.500000 | 0.062500 | 0.693147 | 0.500000 |  |  |  |  |

## Local Score Regression

| task | feature_block | n | positive_rate | auc | average_precision | logloss | pred_mean | target_mean | spearman | pearson | rmse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| predict_local_p90 | human_plus_shape | 1072 |  |  |  |  |  | -0.000267 | 0.900789 | 0.934248 | 0.000063 |
| predict_local_p90 | action_shape | 1072 |  |  |  |  |  | -0.000267 | 0.813769 | 0.893401 | 0.000079 |
| predict_local_p90 | shape_signature | 1072 |  |  |  |  |  | -0.000267 | 0.803734 | 0.881864 | 0.000082 |
| predict_local_p90 | human_signature | 1072 |  |  |  |  |  | -0.000267 | 0.391977 | 0.436571 | 0.000174 |

## Source-Level Identity Readout

| feature_block | sources | mean_actual_rank | median_actual_rank | top_quartile_rate | mean_identity_health_gap |
| --- | --- | --- | --- | --- | --- |
| human_plus_shape | 67 | 0.999005 | 1.000000 | 1.000000 | 0.643781 |
| human_signature | 67 | 0.999005 | 1.000000 | 1.000000 | 0.643781 |
| action_shape | 67 | 0.000000 | 0.000000 | 0.000000 | -0.355224 |
| shape_signature | 67 | 0.000000 | 0.000000 | 0.000000 | -0.355224 |

## Identity vs Health Correlation

| feature_block | identity_rank_vs | spearman | pearson | n |
| --- | --- | --- | --- | --- |
| action_shape | source_dateblock_p90_dominance |  |  | 67 |
| action_shape | source_mean_dominance |  |  | 67 |
| action_shape | source_null_strict_rate |  |  | 67 |
| action_shape | source_p90_dominance |  |  | 67 |
| action_shape | source_row_p90_dominance |  |  | 67 |
| action_shape | source_subject_p90_dominance |  |  | 67 |
| action_shape | source_worst_mode_p90_dominance |  |  | 67 |
| human_plus_shape | source_dateblock_p90_dominance | 0.194714 | 0.232746 | 67 |
| human_plus_shape | source_mean_dominance | 0.064049 | 0.066681 | 67 |
| human_plus_shape | source_null_strict_rate | -0.206034 | -0.175498 | 67 |
| human_plus_shape | source_p90_dominance | 0.211853 | 0.296037 | 67 |
| human_plus_shape | source_row_p90_dominance | 0.110593 | 0.037757 | 67 |
| human_plus_shape | source_subject_p90_dominance | 0.184094 | 0.190965 | 67 |
| human_plus_shape | source_worst_mode_p90_dominance | 0.159448 | 0.151436 | 67 |
| human_signature | source_dateblock_p90_dominance | 0.194714 | 0.232746 | 67 |
| human_signature | source_mean_dominance | 0.064049 | 0.066681 | 67 |
| human_signature | source_null_strict_rate | -0.206034 | -0.175498 | 67 |
| human_signature | source_p90_dominance | 0.211853 | 0.296037 | 67 |
| human_signature | source_row_p90_dominance | 0.110593 | 0.037757 | 67 |
| human_signature | source_subject_p90_dominance | 0.184094 | 0.190965 | 67 |
| human_signature | source_worst_mode_p90_dominance | 0.159448 | 0.151436 | 67 |
| shape_signature | source_dateblock_p90_dominance |  |  | 67 |
| shape_signature | source_mean_dominance |  |  | 67 |
| shape_signature | source_null_strict_rate |  |  | 67 |
| shape_signature | source_p90_dominance |  |  | 67 |
| shape_signature | source_row_p90_dominance |  |  | 67 |
| shape_signature | source_subject_p90_dominance |  |  | 67 |
| shape_signature | source_worst_mode_p90_dominance |  |  | 67 |

## Near-Miss Anatomy

| feature_block | source_basename | recipe | actual_rank_vs_placement_null | source_actual_p90 | source_null_strict_rate | source_worst_mode_p90_dominance | source_row_p90_dominance | source_subject_p90_dominance | source_dateblock_p90_dominance | source_final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human_plus_shape | submission_e315_humancomp_family_bedtime_arousal_l1mean_c24_w12_00_0958e5f2.csv | family_consensus | 1.000000 | -0.000290 | 0.681818 | 0.000000 | 1.000000 | 0.000000 | 0.400000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w5_00_827a8fe9.csv | family_consensus | 1.000000 | -0.000235 | 0.636364 | 0.000000 | 1.000000 | 0.000000 | 0.200000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w8_00_82833aba.csv | family_consensus | 1.000000 | -0.000291 | 0.636364 | 0.000000 | 1.000000 | 0.400000 | 0.000000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_family_bedtime_arousal_maxmean_call_w5_00_5548dd85.csv | family_consensus | 1.000000 | -0.000200 | 0.545455 | 0.000000 | 1.000000 | 0.000000 | 0.200000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_neg_top3_l1avg_c160_w10_00_f27cec0c.csv | ranked_negative_stack | 1.000000 | -0.000205 | 0.636364 | 0.000000 | 1.000000 | 0.200000 | 0.000000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_neg_top3_l1avg_c24_w10_00_043a0d25.csv | ranked_negative_stack | 1.000000 | -0.000218 | 0.727273 | 0.000000 | 0.800000 | 0.000000 | 0.000000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_neg_top3_l1avg_c48_w10_00_f27cec0c.csv | ranked_negative_stack | 1.000000 | -0.000205 | 0.590909 | 0.000000 | 1.000000 | 0.000000 | 0.000000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_neg_top3_l1avg_c96_w10_00_f27cec0c.csv | ranked_negative_stack | 1.000000 | -0.000205 | 0.681818 | 0.000000 | 0.800000 | 0.000000 | 0.000000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_neg_top3_l1avg_c96_w7_00_7bdd4f0d.csv | ranked_negative_stack | 1.000000 | -0.000193 | 0.681818 | 0.000000 | 1.000000 | 0.000000 | 0.000000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_orth_s0_n3_maxavg_c64_w8_00_5dabd4d6.csv | orthogonal_story_stack | 1.000000 | -0.000174 | 0.636364 | 0.000000 | 0.600000 | 0.000000 | 0.800000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_orth_s0_n8_maxavg_c64_w8_00_7750cef1.csv | orthogonal_story_stack | 1.000000 | -0.000342 | 0.090909 | 0.000000 | 1.000000 | 0.000000 | 0.200000 | hold_for_more_local_evidence |
| human_plus_shape | submission_e315_humancomp_tbstory_bedtime_arousal_all_c96_w1_50_98ae1d86.csv | target_balanced_story_stack | 1.000000 | -0.000090 | 0.454545 | 0.000000 | 1.000000 | 0.800000 | 0.600000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_tbstory_bedtime_arousal_all_call_w1_50_98ae1d86.csv | target_balanced_story_stack | 1.000000 | -0.000090 | 0.409091 | 0.000000 | 1.000000 | 0.800000 | 0.600000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_tbstory_bedtime_arousal_qs_c96_w1_50_98ae1d86.csv | target_balanced_story_stack | 1.000000 | -0.000090 | 0.500000 | 0.000000 | 1.000000 | 0.200000 | 0.800000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_tbstory_bedtime_arousal_qs_call_w1_50_98ae1d86.csv | target_balanced_story_stack | 1.000000 | -0.000090 | 0.545455 | 0.000000 | 1.000000 | 0.400000 | 0.800000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_tbstory_bedtime_arousal_s_c96_w1_50_98ae1d86.csv | target_balanced_story_stack | 1.000000 | -0.000090 | 0.409091 | 0.000000 | 1.000000 | 0.400000 | 0.800000 | blocked_by_human_ready_composition_nulls |
| human_plus_shape | submission_e315_humancomp_tbstory_bedtime_arousal_s_call_w1_50_98ae1d86.csv | target_balanced_story_stack | 1.000000 | -0.000090 | 0.409091 | 0.000000 | 1.000000 | 0.800000 | 0.800000 | blocked_by_human_ready_composition_nulls |
| human_signature | submission_e315_humancomp_family_bedtime_arousal_l1mean_c24_w12_00_0958e5f2.csv | family_consensus | 1.000000 | -0.000290 | 0.681818 | 0.000000 | 1.000000 | 0.000000 | 0.400000 | blocked_by_human_ready_composition_nulls |
| human_signature | submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w5_00_827a8fe9.csv | family_consensus | 1.000000 | -0.000235 | 0.636364 | 0.000000 | 1.000000 | 0.000000 | 0.200000 | blocked_by_human_ready_composition_nulls |
| human_signature | submission_e315_humancomp_family_bedtime_arousal_maxmean_c24_w8_00_82833aba.csv | family_consensus | 1.000000 | -0.000291 | 0.636364 | 0.000000 | 1.000000 | 0.400000 | 0.000000 | blocked_by_human_ready_composition_nulls |

## Top Human Coefficients

| feature_block | feature | coef_actual_identity | abs_coef |
| --- | --- | --- | --- |
| human_plus_shape | human_signed__story_low_hr_recovery_subj_z | 0.304177 | 0.304177 |
| human_signature | human_signed__story_low_hr_recovery_subj_z | 0.302792 | 0.302792 |
| human_signature | human_active__cash_payeom_post3_late_shopping_subj_z | 0.270258 | 0.270258 |
| human_plus_shape | human_active__cash_payeom_post3_late_shopping_subj_z | 0.261523 | 0.261523 |
| human_signature | human_absw__story_quiet_dark_bedtime_subj_z | -0.238412 | 0.238412 |
| human_plus_shape | human_absw__story_quiet_dark_bedtime_subj_z | -0.236834 | 0.236834 |
| human_signature | human_absw__diary_diary_state_k10_2 | 0.234127 | 0.234127 |
| human_plus_shape | human_absw__diary_diary_state_k10_2 | 0.233085 | 0.233085 |
| human_signature | human_signed__story_late_search_spiral | 0.205279 | 0.205279 |
| human_plus_shape | human_signed__story_late_search_spiral | 0.201827 | 0.201827 |
| human_plus_shape | human_signed__story_late_search_spiral_subj_z | 0.191866 | 0.191866 |
| human_signature | human_signed__story_late_search_spiral_subj_z | 0.190871 | 0.190871 |
| human_signature | human_q_minus_s__story_presleep_msg_drag_subj_z | 0.187349 | 0.187349 |
| human_plus_shape | human_q_minus_s__story_presleep_msg_drag_subj_z | 0.185066 | 0.185066 |
| human_plus_shape | human_signed__diary_physiology_activity_pc2 | 0.183641 | 0.183641 |
| human_signature | human_signed__diary_physiology_activity_pc2 | 0.181948 | 0.181948 |
| human_signature | human_signed__story_morning_after_badnight | 0.178388 | 0.178388 |
| human_signature | human_signed__cash_paymonth_start_near3_money_rumination_subj_z | 0.177404 | 0.177404 |
| human_plus_shape | human_signed__cash_paymonth_start_near3_money_rumination_subj_z | 0.175076 | 0.175076 |
| human_plus_shape | human_signed__diary_jepa_prednorm_subject_physiology_activity | -0.173310 | 0.173310 |
| human_signature | human_signed__diary_jepa_prednorm_dateblock_cognitive_money | 0.172626 | 0.172626 |
| human_plus_shape | human_signed__story_morning_after_badnight | 0.172491 | 0.172491 |
| human_signature | human_signed__diary_jepa_prednorm_subject_physiology_activity | -0.171930 | 0.171930 |
| human_plus_shape | human_signed__cash_payeom_near3_money_rumination_active | -0.171794 | 0.171794 |
| human_plus_shape | human_signed__cash_payeom_pre3_cash_stress_subj_z | -0.170705 | 0.170705 |
| human_plus_shape | human_signed__diary_social_comm_energy | -0.170463 | 0.170463 |
| human_signature | human_signed__story_late_msg_call_subj_z | -0.169869 | 0.169869 |
| human_plus_shape | human_absw__cash_paymonth_start_pre3_cash_stress_subj_z | -0.169591 | 0.169591 |
| human_signature | human_q_minus_s__diary_physiology_activity_pc4 | 0.169377 | 0.169377 |
| human_plus_shape | human_signed__diary_jepa_prednorm_dateblock_cognitive_money | 0.169325 | 0.169325 |
| human_signature | human_signed__diary_social_comm_energy | -0.168902 | 0.168902 |
| human_signature | human_absw__story_overtraining_arousal | -0.168527 | 0.168527 |
| human_signature | human_signed__cash_payeom_near3_money_rumination_active | -0.168444 | 0.168444 |
| human_signature | human_absw__cash_paymonth_start_pre3_cash_stress_subj_z | -0.168358 | 0.168358 |
| human_plus_shape | human_q_minus_s__diary_physiology_activity_pc4 | 0.167873 | 0.167873 |
| human_plus_shape | human_absw__cash_payeom_post3_late_shopping_subj_z | 0.167548 | 0.167548 |
| human_plus_shape | human_absw__story_overtraining_arousal | -0.167327 | 0.167327 |
| human_plus_shape | human_signed__story_late_msg_call_subj_z | -0.167247 | 0.167247 |
| human_signature | human_signed__diary_physiology_activity_pc1 | 0.166983 | 0.166983 |
| human_plus_shape | human_signed__cash_payeom_near3_money_rumination_subj_z | -0.166508 | 0.166508 |

## Decision

- Human diary signatures can identify intended placement above chance, so hidden placement is partially learnable.
- However this is not enough for submission unless the identity rank correlates with subject/dateblock/worst-mode health.
- Next action: train a placement-health target, not just an actual-vs-null identity target.

## Outputs

- `analysis_outputs/e316_human_placement_health_features.csv`
- `analysis_outputs/e316_human_placement_health_metrics.csv`
- `analysis_outputs/e316_human_placement_health_oof.csv`
- `analysis_outputs/e316_human_placement_health_source_readout.csv`
- `analysis_outputs/e316_human_placement_health_top_features.csv`
- `analysis_outputs/e316_human_placement_health_report.md`
