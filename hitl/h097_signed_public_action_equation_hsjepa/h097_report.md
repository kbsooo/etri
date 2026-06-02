# H097 Signed Public Action-Equation HS-JEPA

Question: can all public observations be used as signed action-response
supervision from the H057 base?

Design:

- context: H095 cell toxicity table, H057-positive conflict features, row/target
  context, source/invariant diagnostics;
- target representation: public LB response to submitted action vectors;
- decoder: signed public-response gradient plus H057/H088 conflict gates.

Public response model:

| feature_set | alpha | n_x_features | loo_mae | loo_rmse | loo_spearman | loo_pair_acc | full_fit_mae | rank_score | perm_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| state_context | 10.000000000 | 120 | 0.000423023 | 0.000588558 | 0.978473604 | 0.952727273 | 0.000280079 | 0.000418536 | 0.000000000 |
| state_core | 10.000000000 | 105 | 0.000457706 | 0.000623350 | 0.977603850 | 0.949090909 | 0.000279389 | 0.000469617 | 1.000000000 |
| state_context | 3.000000000 | 120 | 0.000431062 | 0.000710650 | 0.980213113 | 0.952727273 | 0.000187993 | 0.000481342 | 1.000000000 |
| state_context | 30.000000000 | 120 | 0.000506049 | 0.000644866 | 0.978473604 | 0.952727273 | 0.000413063 | 0.000526900 | 1.000000000 |
| state_core | 30.000000000 | 105 | 0.000519028 | 0.000651750 | 0.976734096 | 0.949090909 | 0.000400887 | 0.000543806 | 1.000000000 |
| state_context | 1.000000000 | 120 | 0.000458416 | 0.000816854 | 0.980213113 | 0.952727273 | 0.000129855 | 0.000556488 | 1.000000000 |
| state_core | 3.000000000 | 105 | 0.000481638 | 0.000765163 | 0.979343359 | 0.949090909 | 0.000191328 | 0.000557191 | 1.000000000 |
| target_only | 30.000000000 | 59 | 0.000541299 | 0.000696142 | 0.978473604 | 0.952727273 | 0.000438791 | 0.000585225 | 1.000000000 |
| target_only | 10.000000000 | 59 | 0.000526210 | 0.000747742 | 0.974994587 | 0.949090909 | 0.000310887 | 0.000594358 | 1.000000000 |
| state_context | 0.300000000 | 120 | 0.000471069 | 0.000872194 | 0.971515570 | 0.938181818 | 0.000077479 | 0.000597532 | 1.000000000 |
| state_context | 0.100000000 | 120 | 0.000480627 | 0.000876389 | 0.966297044 | 0.923636364 | 0.000042649 | 0.000612118 | 1.000000000 |
| state_core | 1.000000000 | 105 | 0.000521177 | 0.000890008 | 0.970645816 | 0.934545455 | 0.000132623 | 0.000656397 | 1.000000000 |
| state_context | 0.030000000 | 120 | 0.000512110 | 0.000939849 | 0.968906307 | 0.930909091 | 0.000024158 | 0.000670587 | 1.000000000 |
| state_core | 0.100000000 | 105 | 0.000522147 | 0.000953092 | 0.961078518 | 0.920000000 | 0.000038120 | 0.000689330 | 1.000000000 |
| state_core | 0.030000000 | 105 | 0.000524409 | 0.000978928 | 0.961948272 | 0.920000000 | 0.000020076 | 0.000703131 | 1.000000000 |

LOO predictions:

| feature_set | alpha | file | public_lb | delta_vs_h057 | loo_pred_delta | loo_error |
| --- | --- | --- | --- | --- | --- | --- |
| state_context | 10.000000000 | submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | 0.567747594 | 0.000000000 | -0.001207548 | -0.001207548 |
| state_context | 10.000000000 | submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.567904825 | 0.000157231 | 0.000540078 | 0.000382847 |
| state_context | 10.000000000 | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.000157231 | 0.000317524 | 0.000160293 |
| state_context | 10.000000000 | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.568123483 | 0.000375889 | 0.000402526 | 0.000026637 |
| state_context | 10.000000000 | submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.568494202 | 0.000746608 | -0.000641687 | -0.001388295 |
| state_context | 10.000000000 | submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.008411356 | 0.008798617 | 0.000387261 |
| state_context | 10.000000000 | submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.008532974 | 0.008811449 | 0.000278476 |
| state_context | 10.000000000 | submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.576290429 | 0.008542835 | 0.008815678 | 0.000272842 |
| state_context | 10.000000000 | submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.008543736 | 0.008877042 | 0.000333307 |
| state_context | 10.000000000 | submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.008552772 | 0.008884643 | 0.000331871 |
| state_context | 10.000000000 | submission_mixmin_0c916bb4.csv | 0.576306641 | 0.008559047 | 0.008924156 | 0.000365110 |
| state_context | 10.000000000 | submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.008564237 | 0.008929889 | 0.000365652 |
| state_context | 10.000000000 | submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.008581903 | 0.008866650 | 0.000284747 |
| state_context | 10.000000000 | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.008660183 | 0.009003436 | 0.000343252 |
| state_context | 10.000000000 | submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.009287908 | 0.009207328 | -0.000080580 |
| state_context | 10.000000000 | submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.009538915 | 0.009095108 | -0.000443807 |
| state_context | 10.000000000 | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.009778713 | 0.009901837 | 0.000123124 |
| state_context | 10.000000000 | submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.010197382 | 0.010128631 | -0.000068751 |
| state_context | 10.000000000 | submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.578171818 | 0.010424224 | 0.009329119 | -0.001095104 |
| state_context | 10.000000000 | submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.010555771 | 0.010312611 | -0.000243160 |
| state_context | 10.000000000 | submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.010679759 | 0.010562589 | -0.000117170 |
| state_context | 10.000000000 | submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.012053692 | 0.012243244 | 0.000189551 |
| state_context | 10.000000000 | submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.012499225 | 0.012320153 | -0.000179073 |
| state_context | 10.000000000 | submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.013479734 | 0.011995634 | -0.001484100 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_conflict_rate | cos_h088_direction | cos_h057_vs_h042_direction | max_positive_bad_cosine | h097_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h097_positive_bridge_c260_a045_062bff8e | positive_bridge_c260_a045 | 9 | 5 | -0.000499183 | 0.000024563 | 0.000042872 | 1.000000000 | 1.000000000 | 1.000000000 | -0.039966616 | 0.148903258 | 0.006845614 | 0.466474138 | submission_h097_positive_bridge_c260_a045_062bff8e.csv |
| h097_conflict_invert_model_c105_a060_bb08d082 | conflict_invert_model_c105_a060 | 19 | 11 | -0.000409199 | 0.000078503 | 0.000117705 | 1.000000000 | 1.000000000 | 1.000000000 | -0.057225100 | 0.197759704 | 0.000000000 | 0.462854051 | submission_h097_conflict_invert_model_c105_a060_bb08d082.csv |
| h097_signed_descent_all_c760_a050_ba5b6ed8 | signed_descent_all_c760_a050 | 3 | 1 | -0.000529906 | 0.000011329 | 0.000019539 | 1.000000000 | 1.000000000 | 1.000000000 | -0.027309471 | 0.112485600 | 0.000000000 | 0.448933832 | submission_h097_signed_descent_all_c760_a050_ba5b6ed8.csv |
| h097_signed_stage_c620_a055_f7305ac0 | signed_stage_c620_a055 | 4 | 2 | -0.000533793 | 0.000014242 | 0.000023479 | 0.750000000 | 0.750000000 | 1.000000000 | -0.027200483 | 0.111927386 | 0.000000000 | 0.417548200 | submission_h097_signed_stage_c620_a055_f7305ac0.csv |
| h097_counter_h088_toxic_c520_a045_6b9179a5 | counter_h088_toxic_c520_a045 | 13 | 7 | -0.000501473 | 0.000068533 | 0.000059410 | 1.000000000 | 0.461538462 | 0.461538462 | -0.252210404 | 0.037759230 | 0.143030738 | 0.306352055 | submission_h097_counter_h088_toxic_c520_a045_6b9179a5.csv |
| h097_q2_gradient_reopen_c115_a070_5c2467ba | q2_gradient_reopen_c115_a070 | 5 | 5 | -0.000500777 | 0.000128930 | 0.000091265 | 1.000000000 | 0.000000000 | 0.000000000 | -0.115715627 | 0.000000000 | 0.072216821 | 0.217962614 | submission_h097_q2_gradient_reopen_c115_a070_5c2467ba.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | response_feature_set | response_alpha | response_loo_mae | response_loo_rmse | response_loo_spearman | response_loo_pair_acc | response_perm_p | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h097_signed_public_action_equation | h097_positive_bridge_c260_a045_062bff8e | /Users/kbsoo/Downloads/cl2/submission_h097_signed_equation_062bff8e_uploadsafe.csv | H057-positive field is still valid when aligned with learned public gradient | state_context | 10.000000000 | 0.000423023 | 0.000588558 | 0.978473604 | 0.952727273 | 0.000000000 | h097_positive_bridge_c260_a045_062bff8e | positive_bridge_c260_a045 | h057_positive | all | state_context | 10.000000000 | 260 | 0.450000000 | 0.550000000 | 9 | 9 | 5 | -0.000499183 | 0.000024563 | 0.000042872 | 1.000000000 | 1.000000000 | 0.723184127 | 1.000000000 | 0.088848394 | 0.616158730 | -0.039966616 | 0.148903258 | 0.139822802 | 0.006845614 | 0.000203834 | 0.058690528 | 5 | 3,70,101,151,235 | 0.466474138 | submission_h097_positive_bridge_c260_a045_062bff8e.csv | /Users/kbsoo/Downloads/cl2/hitl/h097_signed_public_action_equation_hsjepa/submission_h097_positive_bridge_c260_a045_062bff8e.csv | 1 | 0 | 3 | 1 | 1 | 1 | 2 | -0.014522889 | 0.001406616 | -0.009561778 | 0.006845614 | -0.004178916 | -0.009377928 | -0.012480151 | /Users/kbsoo/Downloads/cl2/hitl/h097_signed_public_action_equation_hsjepa/submission_h097_positive_bridge_c260_a045_062bff8e.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 9 | True | /Users/kbsoo/Downloads/cl2/submission_h097_signed_equation_062bff8e_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 9 | True |

Interpretation rule:

- If H097 improves materially, HS-JEPA v2 should treat public submissions as a
  signed action-equation training set, not just as posterior constraints.
- If H097 loses while H096 wins, the public response model is too globally
  smoothed and H088 should stay a local counterfactual sensor.
- If both H096 and H097 lose, H088 is a broad collapse diagnostic rather than a
  reusable signed action field.
