# H150 Bundle-Listener Stress HS-JEPA

Date: 2026-06-03

## Question

H149 is the strongest current bundle-listener candidate, but its large upside
could be an old-anchor shortcut. H150 stress-tests that possibility.

## Stress Results

### Variant Best Scores

| variant | description | n_obs | n_features | alpha | loo_mae | loo_spearman | h144_h145_pred_gap_abs | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_bad | remove bad-anchor worlds | 16 | 317 | 0.300000000 | 0.000288111 | 0.869411051 | 0.000000915 | 0.000299093 |
| human_social_only | date/social/pay/month plus target only | 19 | 83 | 0.300000000 | 0.000414252 | 0.901859985 | 0.000000531 | 0.000420622 |
| no_subject | drop subject identity bundles | 19 | 227 | 1.000000000 | 0.000430681 | 0.860537649 | 0.000000910 | 0.000441600 |
| no_base_prob | drop H057 probability-regime bundles | 19 | 268 | 1.000000000 | 0.000436497 | 0.804752496 | 0.000000931 | 0.000447669 |
| no_human_social | drop date/social/pay/month features | 19 | 244 | 0.300000000 | 0.000438975 | 0.825413664 | 0.000001117 | 0.000452378 |
| structural_only | no human-social date features | 19 | 244 | 0.300000000 | 0.000438975 | 0.825413664 | 0.000001117 | 0.000452378 |
| all_full | all observations and all bundle features | 19 | 317 | 1.000000000 | 0.000450715 | 0.858471532 | 0.000000922 | 0.000461776 |
| no_row_order | drop row-order bundles | 19 | 222 | 100.000000000 | 0.000473523 | 0.765496276 | 0.000000239 | 0.000476386 |
| no_pre_h | remove old pre-H public worlds | 10 | 317 | 30.000000000 | 0.000716345 | 0.605063381 | 0.000000278 | 0.000719684 |
| frontier_only | post-H frontier sensor only | 7 | 317 | 0.003000000 | 0.000193230 | -0.735612358 | 0.000000002 | 0.000928862 |

### Role Holdout

| heldout_role | file | actual_delta | pred_delta | error | train_n_obs | train_loo_mae | train_loo_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bad_anchor | submission_e323_5508f966_uploadsafe.csv | 0.009287908 | 0.008293746 | -0.000994162 | 16 | 0.000288111 | 0.869411051 |
| bad_anchor | submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.009538915 | 0.008680852 | -0.000858063 | 16 | 0.000288111 | 0.869411051 |
| bad_anchor | submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.010424224 | 0.008743465 | -0.001680758 | 16 | 0.000288111 | 0.869411051 |
| breakthrough_anchor | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.000375889 | 0.001111276 | 0.000735387 | 18 | 0.000463250 | 0.704295009 |
| frontier_basin | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.000157231 | 0.000417424 | 0.000260193 | 17 | 0.000501672 | 0.799117214 |
| frontier_basin | submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.000157231 | -0.000198022 | -0.000355253 | 17 | 0.000501672 | 0.799117214 |
| negative_sensor | submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.000746608 | -0.002727492 | -0.003474100 | 18 | 0.000269255 | 0.826994488 |
| pre_h_world | submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.008411356 | 0.009386090 | 0.000974734 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.008532974 | 0.009457304 | 0.000924330 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.008542835 | 0.009434549 | 0.000891713 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_e95_hardtail_541e3973.csv | 0.008543736 | 0.009320577 | 0.000776841 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_e101_q2s3tail_177569bc.csv | 0.008552772 | 0.009325538 | 0.000772766 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_mixmin_0c916bb4.csv | 0.008559047 | 0.009302747 | 0.000743700 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_e176_abl_q2_to0p75_91e49725.csv | 0.008564237 | 0.009293410 | 0.000729173 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_e267_humansocial_tail_balanced_2936100f.csv | 0.008581903 | 0.009505634 | 0.000923730 | 10 | 0.000716345 | 0.605063381 |
| pre_h_world | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.008660183 | 0.009491405 | 0.000831222 | 10 | 0.000716345 | 0.605063381 |
| tie_sensor | submission_h144_targetxor_def80b88_uploadsafe.csv | 0.000182047 | -0.000049704 | -0.000231751 | 17 | 0.000487534 | 0.778513824 |
| tie_sensor | submission_h145_q3repair_2d818e46_uploadsafe.csv | 0.000182047 | -0.000050275 | -0.000232322 | 17 | 0.000487534 | 0.778513824 |

### Null Permutation Summary

| real_loo_mae | real_loo_spearman | real_h149_pred_delta | null_spearman_ge_real_frac | null_mae_le_real_frac | null_h149_pred_le_real_frac | null_h149_pred_mean | null_h149_pred_p05 | null_h149_pred_p50 | null_h149_pred_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.000450715 | 0.858471532 | -0.004994063 | 0.000000000 | 0.000000000 | 0.640000000 | -0.008288506 | -0.026009410 | -0.007929061 | 0.010387052 |

### Dropout Stability

| candidate | mean_pred_delta | p05_pred_delta | p50_pred_delta | p95_pred_delta | negative_frac |
| --- | --- | --- | --- | --- | --- |
| h149_bundle_listener_route_d8e1d789 | -0.004805090 | -0.005391969 | -0.004806037 | -0.004187567 | 1.000000000 |
| h073_humanaction_bridge_7a2cbf07 | -0.001037544 | -0.001834274 | -0.001030982 | -0.000270256 | 0.994444444 |
| h075_antibad_transport_f6863945 | -0.000982902 | -0.001771216 | -0.001014748 | -0.000190408 | 0.983333333 |
| h071_rowtarget_assignment_a52b6b57 | -0.000315965 | -0.001099234 | -0.000273723 | 0.000330394 | 0.744444444 |
| h074_antishortcut_inversion_816703df | -0.000161837 | -0.000902398 | -0.000139262 | 0.000455081 | 0.638888889 |
| h126_coeffeq_3fe3eee4 | -0.000017004 | -0.000131198 | -0.000063582 | 0.000111834 | 0.577777778 |
| h145_q3repair_2d818e46 | 0.000125097 | 0.000080630 | 0.000133456 | 0.000151367 | 0.000000000 |
| h050_target_route_phase_b140216b | 0.000125745 | 0.000098691 | 0.000129355 | 0.000139152 | 0.000000000 |
| h144_targetxor_def80b88 | 0.000125926 | 0.000081430 | 0.000134428 | 0.000151969 | 0.000000000 |
| h141_commoncore_0999d3ae | 0.000128246 | 0.000082780 | 0.000135489 | 0.000154795 | 0.000000000 |
| h042_target_Q2_phase_k45_s0.5_c45_50fc6607 | 0.000205877 | 0.000185260 | 0.000201220 | 0.000240079 | 0.000000000 |
| h012_public_equation_top_all_k1200_a0.7 | 0.000393520 | 0.000383127 | 0.000390876 | 0.000411553 | 0.000000000 |
| h088_dual_state_gate_c31cc15b | 0.000727240 | 0.000717477 | 0.000728219 | 0.000734243 | 0.000000000 |

## Candidate Ranking Across Listener Worlds

| file | changed_cells_vs_h057 | changed_rows_vs_h057 | h088_move_cosine | robust_positive_variant_count | robust_mean_pred_delta | robust_min_pred_delta | robust_max_pred_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 349 | 154 | 0.121063141 | 10 | -0.003753061 | -0.005149816 | -0.000168024 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 657 | 141 | 0.887213191 | 9 | -0.000958129 | -0.002204466 | 0.000678887 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 524 | 152 | 0.835549425 | 9 | -0.000898995 | -0.001567561 | 0.000478660 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 736 | 158 | 0.887472000 | 8 | -0.000248202 | -0.000908499 | 0.000458205 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 597 | 152 | 0.828647527 | 8 | -0.000242905 | -0.000655681 | 0.000466735 |
| submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 28 | 23 | -0.057669876 | 7 | -0.000017778 | -0.000083814 | 0.000135712 |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | 27 | 22 | -0.063807440 | 2 | 0.000117499 | -0.000054764 | 0.000182036 |
| submission_h144_targetxor_def80b88_uploadsafe.csv | 28 | 23 | -0.064775307 | 2 | 0.000118195 | -0.000054526 | 0.000182035 |
| submission_h141_commoncore_0999d3ae_uploadsafe.csv | 27 | 22 | -0.063558603 | 2 | 0.000120320 | -0.000055042 | 0.000182669 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | 343 | 111 | -0.125396149 | 0 | 0.000142039 | 0.000030229 | 0.000234195 |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 270 | 45 | -0.144085796 | 0 | 0.000261721 | 0.000157237 | 0.000719746 |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 315 | 45 | -0.144102131 | 0 | 0.000465923 | 0.000375882 | 0.000977702 |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 980 | 168 | 1.000000000 | 0 | 0.000637180 | 0.000000860 | 0.000746606 |

## Promoted Robust Candidate

| candidate_file | candidate_path | selected_cells | selected_rows | selected_source_mix | selected_target_mix | worldview | h149_status | validation_path | validation_rows | validation_keys_match | validation_duplicate_keys | validation_nan_cells | validation_min_prob | validation_max_prob | validation_changed_cells_vs_h057_validation | validation_upload_safe | metric_changed_cells_vs_h057 | metric_changed_rows_vs_h057 | metric_move_l1 | metric_move_l2 | metric_h088_move_cosine | metric_all_full_pred_delta | metric_all_full_benefit_sum | metric_all_full_toxicity_sum | metric_no_pre_h_pred_delta | metric_no_pre_h_benefit_sum | metric_no_pre_h_toxicity_sum | metric_no_bad_pred_delta | metric_no_bad_benefit_sum | metric_no_bad_toxicity_sum | metric_frontier_only_pred_delta | metric_frontier_only_benefit_sum | metric_frontier_only_toxicity_sum | metric_no_human_social_pred_delta | metric_no_human_social_benefit_sum | metric_no_human_social_toxicity_sum | metric_no_subject_pred_delta | metric_no_subject_benefit_sum | metric_no_subject_toxicity_sum | metric_no_row_order_pred_delta | metric_no_row_order_benefit_sum | metric_no_row_order_toxicity_sum | metric_no_base_prob_pred_delta | metric_no_base_prob_benefit_sum | metric_no_base_prob_toxicity_sum | metric_structural_only_pred_delta | metric_structural_only_benefit_sum | metric_structural_only_toxicity_sum | metric_human_social_only_pred_delta | metric_human_social_only_benefit_sum | metric_human_social_only_toxicity_sum | null_real_loo_mae | null_real_loo_spearman | null_real_h149_pred_delta | null_null_spearman_ge_real_frac | null_null_mae_le_real_frac | null_null_h149_pred_le_real_frac | null_null_h149_pred_mean | null_null_h149_pred_p05 | null_null_h149_pred_p50 | null_null_h149_pred_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | /Users/kbsoo/Downloads/cl2/submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 364 | 157 | {'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 102, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 91, 'submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv': 58, 'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 53, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 45, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 15} | {'S3': 93, 'S4': 59, 'S1': 54, 'S2': 52, 'Q2': 36, 'Q1': 36, 'Q3': 34} | A safe row-target correction should survive multiple listener worlds: all observations, no-pre-H, no-bad, frontier-only, and feature-family ablations. | H149 remains the highest-upside bundle listener bet, but H150 tests whether a robust consensus translator can keep the same worldview with less old-anchor dependence. | /Users/kbsoo/Downloads/cl2/submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 364 | True | 364 | 157 | 28.437477431 | 2.217910718 | 0.188791860 | -0.003842840 | 0.003842840 | 0.000000000 | -0.002360980 | 0.002362806 | 0.000001826 | -0.002583350 | 0.002684758 | 0.000101409 | -0.000161581 | 0.000588513 | 0.000426933 | -0.003976129 | 0.004105399 | 0.000129270 | -0.003681154 | 0.003735570 | 0.000054416 | -0.001977530 | 0.002025335 | 0.000047805 | -0.003981643 | 0.004003841 | 0.000022198 | -0.003976129 | 0.004105399 | 0.000129270 | -0.002869942 | 0.003745136 | 0.000875194 | 0.000450715 | 0.858471532 | -0.004994063 | 0.000000000 | 0.000000000 | 0.640000000 | -0.008288506 | -0.026009410 | -0.007929061 | 0.010387052 |

Source mix:

| source_file | cells |
| --- | --- |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 102 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 91 |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 58 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 53 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 45 |
| submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 15 |

Target mix:

| target | cells |
| --- | --- |
| S3 | 93 |
| S4 | 59 |
| S1 | 54 |
| S2 | 52 |
| Q2 | 36 |
| Q1 | 36 |
| Q3 | 34 |

## Interpretation

H150 does not replace H149 as the high-upside public probe unless robustness is
preferred over upside.  Its role is sharper:

```text
If H149 fails, H150 tells whether the bundle-listener worldview died or only
the aggressive all-observed decoder died.
```

The key architectural decision is whether HS-JEPA should:

1. keep H149-style all-observed bundle listener as the next big public probe;
2. move to H150-style consensus listener before public submission;
3. abandon supervised public equations and solve discrete row-route constraints.
