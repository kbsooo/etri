# E312 Action-Health World Model

Public LB는 사용하지 않았다. E310/E311 이후 병목을 `human story -> target delta`가 아니라 `candidate action -> visible/null-rare health`로 재정의해 검증했다.

## Data

- governed rows: `1383`
- experiments: `20`
- selector_visible: `418`
- null_rare: `930`
- visible_null_rare: `2`
- strict_health: `1`

| experiment | rows | selector_visible | null_rare | visible_null_rare | visible_null_common | strict_health | best_p90 | best_null_strict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e279 | 66 | 13 | 46 | 0 | 13 | 0 | -0.000129 | 0.000000 |
| e284 | 9 | 0 | 9 | 0 | 0 | 0 | 0.000025 | 0.000000 |
| e285 | 158 | 0 | 158 | 0 | 0 | 0 | -0.000003 | 0.000000 |
| e286 | 533 | 0 | 533 | 0 | 0 | 0 | -0.000004 | 0.000000 |
| e287 | 3 | 0 | 3 | 0 | 0 | 0 | -0.000035 | 0.000000 |
| e289 | 28 | 12 | 15 | 0 | 12 | 0 | -0.000417 | 0.000000 |
| e290 | 48 | 33 | 12 | 0 | 33 | 0 | -0.000308 | 0.000000 |
| e291 | 40 | 18 | 22 | 0 | 18 | 0 | -0.000314 | 0.000000 |
| e292 | 56 | 18 | 38 | 0 | 16 | 0 | -0.000157 | 0.000000 |
| e293 | 64 | 48 | 14 | 0 | 48 | 0 | -0.000268 | 0.000000 |
| e297 | 39 | 20 | 17 | 0 | 20 | 0 | -0.000565 | 0.000000 |
| e299 | 71 | 50 | 21 | 1 | 47 | 0 | -0.000557 | 0.000000 |
| e300 | 120 | 87 | 30 | 1 | 83 | 1 | -0.000095 | 0.000000 |
| e301 | 1 | 0 | 0 | 0 | 0 | 0 | -0.000051 | 0.164062 |
| e303 | 12 | 12 | 0 | 0 | 11 | 0 | -0.000074 | 0.187500 |
| e305 | 14 | 14 | 0 | 0 | 14 | 0 | -0.000128 | 0.648438 |
| e306 | 20 | 20 | 0 | 0 | 20 | 0 | -0.000115 | 0.625000 |
| e307 | 22 | 22 | 0 | 0 | 22 | 0 | -0.000198 | 0.750000 |
| e310 | 42 | 23 | 9 | 0 | 23 | 0 | -0.000380 | 0.000000 |
| e311 | 37 | 28 | 3 | 0 | 28 | 0 | -0.000808 | 0.000000 |

## Feature Blocks

| feature_block | numeric_cols | categorical_cols | sample_numeric | sample_categorical |
| --- | --- | --- | --- | --- |
| semantic_only | 4 | 15 | mean_app_story, story_episode_mean_pred, story_episode_p90_pred, story_episode_strict_prob | target_norm, family, target_kind, rule_family, target_task, target, episode, source_target |
| geometry_only | 122 | 8 | old_strict_promote, actual_mean, actual_p10, actual_p90, actual_beats_current_rate, incremental_bad_axis_vs_current, train_gate_splits, train_actual_delta_mean | split, policy, action, view_id, delta_mode, rule, recipe, rules |
| full_safe | 126 | 50 | old_strict_promote, actual_mean, actual_p10, actual_p90, actual_beats_current_rate, incremental_bad_axis_vs_current, train_gate_splits, train_actual_delta_mean | train_policy_id, train_support_gate, experiment, target_norm, family, view, model, split |

## Leave-Experiment-Out Metrics

| feature_block | task | n_valid | positive_rate | auc | average_precision | mae | spearman | pred_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_safe | null_common | 1383 | 0.299349 | 0.982065 | 0.962457 |  |  | 0.334434 |
| geometry_only | null_common | 1383 | 0.299349 | 0.984890 | 0.962115 |  |  | 0.333964 |
| semantic_only | null_common | 1383 | 0.299349 | 0.713484 | 0.496780 |  |  | 0.557036 |
| full_safe | null_rare | 1383 | 0.672451 | 0.981646 | 0.987426 |  |  | 0.634005 |
| geometry_only | null_rare | 1383 | 0.672451 | 0.980414 | 0.986112 |  |  | 0.638297 |
| semantic_only | null_rare | 1383 | 0.672451 | 0.774261 | 0.880674 |  |  | 0.431210 |
| full_safe | visible_null_common | 1383 | 0.295011 | 0.987680 | 0.967077 |  |  | 0.318045 |
| geometry_only | visible_null_common | 1383 | 0.295011 | 0.988155 | 0.964141 |  |  | 0.317858 |
| semantic_only | visible_null_common | 1383 | 0.295011 | 0.708787 | 0.485408 |  |  | 0.554895 |
| full_safe | action_cliff | 1383 | 0.300795 | 0.994332 | 0.982901 |  |  | 0.320561 |
| geometry_only | action_cliff | 1383 | 0.300795 | 0.994126 | 0.982575 |  |  | 0.321494 |
| semantic_only | action_cliff | 1383 | 0.300795 | 0.713287 | 0.497925 |  |  | 0.555832 |
| full_safe | safe_invisible | 1383 | 0.671005 | 0.984119 | 0.988560 |  |  | 0.635145 |
| geometry_only | safe_invisible | 1383 | 0.671005 | 0.983309 | 0.987259 |  |  | 0.639228 |
| semantic_only | safe_invisible | 1383 | 0.671005 | 0.776213 | 0.880973 |  |  | 0.431708 |
| full_safe | strict_health | 1263 | 0.000000 |  |  |  |  | 0.002417 |
| geometry_only | strict_health | 1263 | 0.000000 |  |  |  |  | 0.002418 |
| semantic_only | strict_health | 1263 | 0.000000 |  |  |  |  | 0.203967 |
| full_safe | null_strict_rate | 1383 |  |  |  | 0.176184 | 0.794260 | 0.309035 |
| geometry_only | null_strict_rate | 1383 |  |  |  | 0.175150 | 0.789075 | 0.277892 |
| semantic_only | null_strict_rate | 1383 |  |  |  | 0.432951 | 0.088724 | 0.442207 |
| full_safe | readiness_distance | 1383 |  |  |  | 0.794639 | 0.102712 | 1.531860 |
| geometry_only | readiness_distance | 1383 |  |  |  | 0.864921 | 0.027462 | 1.493517 |
| semantic_only | readiness_distance | 1383 |  |  |  | 0.652573 | 0.229852 | 1.478210 |
| full_safe | actual_p90 | 1383 |  |  |  | 0.000038 | 0.965661 | -0.000009 |
| geometry_only | actual_p90 | 1383 |  |  |  | 0.000028 | 0.962391 | -0.000010 |
| semantic_only | actual_p90 | 1383 |  |  |  | 0.000106 | -0.394986 | -0.000027 |

## E310/E311 Held-Out Risk Readout

| experiment | basename | family | target_norm | selector_visible | null_rare | null_common | actual_p90 | null_strict_rate | pred_submission_hope | failure_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e310 | submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_diff_top64_s007_3c930841.csv | cashflow_stress | multi | False | True | False | -0.000049 | 0.000000 | 0.048339 | safe_but_too_small_or_wrong_sign |
| e310 | submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs96_s004_bc5bcc90.csv | cashflow_stress | multi | False | False | False | -0.000046 | 0.111111 | 0.046212 | no_local_edge |
| e310 | submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs64_s004_022cb388.csv | cashflow_stress | multi | False | True | False | -0.000045 | 0.000000 | 0.044759 | safe_but_too_small_or_wrong_sign |
| e310 | submission_e310_pair_cashflow_stress_Q1_S1_hybrid_context_subject5_joint_centered_s010_71d2b41a.csv | cashflow_stress | multi | False | False | False | -0.000046 | 0.333333 | 0.043829 | no_local_edge |
| e310 | submission_e310_pair_cashflow_stress_S1_S3_hybrid_context_subject5_topabs96_s010_39ebc7b6.csv | cashflow_stress | multi | False | False | False | -0.000050 | 0.388889 | 0.043722 | no_local_edge |
| e310 | submission_e310_pair_home_recovery_Q1_S3_hybrid_context_dateblock5_diff_top64_s007_4d8fa86b.csv | home_recovery | multi | False | False | False | -0.000044 | 0.388889 | 0.038589 | no_local_edge |
| e310 | submission_e310_pair_home_recovery_Q1_S3_hybrid_context_dateblock5_topabs32_s010_4922eea0.csv | home_recovery | multi | False | False | True | -0.000044 | 0.611111 | 0.037363 | no_local_edge |
| e310 | submission_e310_pair_cashflow_stress_S1_S2_raw_human_context_subject5_opp_sign_top64_s014_d9e0a872.csv | cashflow_stress | multi | False | True | False | -0.000043 | 0.000000 | 0.035893 | safe_but_too_small_or_wrong_sign |
| e310 | submission_e310_pair_bedtime_arousal_S1_S2_raw_human_context_subject5_topabs64_s020_1036355e.csv | bedtime_arousal | multi | False | False | False | -0.000040 | 0.111111 | 0.018911 | no_local_edge |
| e310 | submission_e310_pair_bedtime_arousal_S1_S2_raw_human_context_subject5_joint_centered_s020_eedc566d.csv | bedtime_arousal | multi | False | False | False | -0.000044 | 0.222222 | 0.017736 | no_local_edge |
| e310 | submission_e310_pair_home_recovery_S3_S4_hybrid_context_dateblock5_same_sign_top64_s020_62d65151.csv | home_recovery | multi | False | False | False | -0.000017 | 0.111111 | 0.015844 | no_local_edge |
| e310 | submission_e310_pair_home_recovery_S3_S4_hybrid_context_dateblock5_topabs64_s020_62d65151.csv | home_recovery | multi | False | False | False | -0.000017 | 0.111111 | 0.015509 | no_local_edge |
| e310 | submission_e310_pair_cashflow_stress_S1_S4_hybrid_context_subject5_topabs96_s020_ce269ae7.csv | cashflow_stress | multi | False | False | False | -0.000048 | 0.277778 | 0.014242 | no_local_edge |
| e311 | submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_75_k32_w0_75_afa649b8.csv | unknown | multi | False | True | False | -0.000038 | 0.055556 | 0.011667 | safe_but_too_small_or_wrong_sign |
| e311 | submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__wrong_swap_l1_25_k32_w0_75_3e369651.csv | unknown | multi | False | False | False | -0.000044 | 0.111111 | 0.011308 | no_local_edge |
| e311 | submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__all_controls_l1_00_k32_w0_75_915cc5fb.csv | unknown | multi | False | True | False | -0.000030 | 0.000000 | 0.010850 | safe_but_too_small_or_wrong_sign |
| e311 | submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l1_00_k32_w0_75_8ee0d609.csv | unknown | multi | False | False | False | -0.000034 | 0.166667 | 0.008067 | no_local_edge |
| e311 | submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l0_75_k32_w0_75_5d89ae36.csv | unknown | multi | False | False | False | -0.000047 | 0.277778 | 0.007095 | no_local_edge |
| e311 | submission_e311_pairmicro_resid_submission_e310_pair_cashflow_stress_Q1__row_subject_date_l1_25_k64_w0_75_151e6697.csv | unknown | multi | False | False | False | -0.000045 | 0.277778 | 0.006310 | no_local_edge |
| e310 | submission_e310_pair_cashflow_stress_Q1_S1_raw_human_context_subject5_topabs32_s014_8756c44a.csv | cashflow_stress | multi | True | False | True | -0.000148 | 0.666667 | 0.004298 | matched_null_hallucination |

## Decision

- full_safe null_common OOF AUC: `0.982065`
- geometry_only null_common OOF AUC: `0.984890`
- semantic_only null_common OOF AUC: `0.713484`
- full_safe readiness_distance OOF Spearman: `0.102712`
- If geometry is close to full and semantic is weaker, the current bottleneck is action geometry rather than lack of social stories.
- If E310/E311 top predicted hope rows are still actual null-common or too-small, outcome modeling is currently a blocker/gate, not a submission generator.
- Next useful experiment should generate a new action class with different geometry, or learn local row/block action health from richer synthetic controls before materialization.

## Outputs

- `analysis_outputs/e312_action_health_all.csv`
- `analysis_outputs/e312_action_health_metrics.csv`
- `analysis_outputs/e312_action_health_oof.csv`
- `analysis_outputs/e312_action_health_risk_readout.csv`
- `analysis_outputs/e312_action_health_feature_blocks.csv`
- `analysis_outputs/e312_action_health_world_model_report.md`
