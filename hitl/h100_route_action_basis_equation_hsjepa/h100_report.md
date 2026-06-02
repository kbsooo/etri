# H100 Route-Action Basis Equation HS-JEPA

Question: can known public submissions be explained in route-action basis space
rather than cell-feature space?

Route-basis model scores:

| feature_set | k_basis | alpha | n_x_features | loo_mae | loo_rmse | weighted_loo_mae | weighted_loo_rmse | loo_spearman | loo_pair_acc | h088_loo_pred | h088_loo_error | h088_loo_abs_error | h088_sign_ok | base_loo_abs_error | full_fit_weighted_mae | route_basis_rank_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| signed_meta | 40 | 0.100000000 | 45 | 0.000477320 | 0.000728885 | 0.000216509 | 0.000293285 | 0.897151576 | 0.876363636 | 0.000852872 | 0.000106264 | 0.000106264 | 1.000000000 | 0.000148814 | 0.000040252 | 0.000048993 |
| signed_meta | 70 | 0.010000000 | 75 | 0.000779029 | 0.001557223 | 0.000232439 | 0.000514237 | 0.639269422 | 0.741818182 | 0.000743653 | -0.000002955 | 0.000002955 | 1.000000000 | 0.000218092 | 0.000009355 | 0.000068987 |
| signed_meta | 70 | 0.030000000 | 75 | 0.000663389 | 0.001237176 | 0.000214146 | 0.000400343 | 0.686236155 | 0.767272727 | 0.000462405 | -0.000284203 | 0.000284203 | 1.000000000 | 0.000168359 | 0.000012167 | 0.000442380 |
| signed_abs | 140 | 30.000000000 | 220 | 0.000424420 | 0.000598246 | 0.000249466 | 0.000375929 | 0.916286171 | 0.894545455 | 0.000001682 | -0.000744926 | 0.000744926 | 1.000000000 | 0.000181513 | 0.000055114 | 0.001218409 |
| signed_meta | 100 | 0.010000000 | 105 | 0.000886550 | 0.001582592 | 0.000481538 | 0.000706684 | 0.592737566 | 0.716363636 | 0.000387869 | -0.000358739 | 0.000358739 | 1.000000000 | 0.000668763 | 0.000007661 | 0.001265185 |
| signed_abs | 180 | 30.000000000 | 220 | 0.000480099 | 0.000660613 | 0.000399606 | 0.000495280 | 0.908893259 | 0.876363636 | 0.000194156 | -0.000552452 | 0.000552452 | 1.000000000 | 0.000753086 | 0.000063895 | 0.001412917 |
| signed_meta | 40 | 0.300000000 | 45 | 0.000498962 | 0.000675215 | 0.000420676 | 0.000508732 | 0.911067645 | 0.876363636 | 0.000219166 | -0.000527442 | 0.000527442 | 1.000000000 | 0.000822144 | 0.000045501 | 0.001435332 |
| signed_abs | 180 | 10.000000000 | 220 | 0.000426708 | 0.000574850 | 0.000405741 | 0.000514921 | 0.906283996 | 0.872727273 | 0.000150465 | -0.000596143 | 0.000596143 | 1.000000000 | 0.000818533 | 0.000036161 | 0.001538952 |
| signed_meta | 100 | 0.030000000 | 105 | 0.000767172 | 0.001291218 | 0.000469413 | 0.000631308 | 0.672320085 | 0.752727273 | 0.000183666 | -0.000562942 | 0.000562942 | 1.000000000 | 0.000723828 | 0.000010232 | 0.001584386 |
| signed_abs | 180 | 0.100000000 | 220 | 0.000582442 | 0.000908801 | 0.000576239 | 0.000833740 | 0.791041549 | 0.807272727 | 0.000487065 | -0.000259543 | 0.000259543 | 1.000000000 | 0.001519625 | 0.000004648 | 0.001685992 |
| signed_abs | 180 | 3.000000000 | 220 | 0.000406158 | 0.000534261 | 0.000426360 | 0.000551177 | 0.861056772 | 0.840000000 | 0.000084422 | -0.000662186 | 0.000662186 | 1.000000000 | 0.000894166 | 0.000020195 | 0.001738612 |
| signed_abs | 180 | 0.030000000 | 220 | 0.000691539 | 0.001065504 | 0.000670379 | 0.001005942 | 0.727549484 | 0.781818182 | 0.000640406 | -0.000106202 | 0.000106202 | 1.000000000 | 0.001802344 | 0.000002555 | 0.001761591 |
| signed_abs | 180 | 0.300000000 | 220 | 0.000452577 | 0.000686200 | 0.000502685 | 0.000687568 | 0.839747791 | 0.821818182 | 0.000263548 | -0.000483060 | 0.000483060 | 1.000000000 | 0.001241896 | 0.000007320 | 0.001767664 |
| signed_meta | 70 | 0.100000000 | 75 | 0.000529261 | 0.000800481 | 0.000402053 | 0.000553583 | 0.762774534 | 0.800000000 | 0.000027389 | -0.000719219 | 0.000719219 | 1.000000000 | 0.000837815 | 0.000016141 | 0.001795615 |
| signed_abs | 140 | 10.000000000 | 220 | 0.000414441 | 0.000562054 | 0.000284863 | 0.000415385 | 0.914546662 | 0.890909091 | -0.000078409 | -0.000825017 | 0.000825017 | 0.000000000 | 0.000306744 | 0.000034279 | 0.001827316 |

Selected-model LOO predictions:

| feature_set | k_basis | alpha | file | public_lb | delta_vs_h057 | frontier_weight | loo_pred_delta | loo_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| signed_meta | 40 | 0.100000000 | submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | 0.567747594 | 0.000000000 | 5.469148518 | 0.000148814 | 0.000148814 |
| signed_meta | 40 | 0.100000000 | submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.567904825 | 0.000157231 | 4.379922090 | -0.000244252 | -0.000401483 |
| signed_meta | 40 | 0.100000000 | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.000157231 | 4.379922090 | 0.000324378 | 0.000167147 |
| signed_meta | 40 | 0.100000000 | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.568123483 | 0.000375889 | 3.817133290 | 0.000218170 | -0.000157719 |
| signed_meta | 40 | 0.100000000 | submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.568494202 | 0.000746608 | 4.455340062 | 0.000852872 | 0.000106264 |
| signed_meta | 40 | 0.100000000 | submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.008411356 | 0.080509308 | 0.008702113 | 0.000290758 |
| signed_meta | 40 | 0.100000000 | submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.008532974 | 0.080173991 | 0.008682926 | 0.000149952 |
| signed_meta | 40 | 0.100000000 | submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.576290429 | 0.008542835 | 0.080148262 | 0.008789311 | 0.000246476 |
| signed_meta | 40 | 0.100000000 | submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.008543736 | 0.080145922 | 0.008558162 | 0.000014426 |
| signed_meta | 40 | 0.100000000 | submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.008552772 | 0.080122549 | 0.008573397 | 0.000020625 |
| signed_meta | 40 | 0.100000000 | submission_mixmin_0c916bb4.csv | 0.576306641 | 0.008559047 | 0.080106422 | 0.008575004 | 0.000015957 |
| signed_meta | 40 | 0.100000000 | submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.008564237 | 0.080093145 | 0.008879623 | 0.000315386 |
| signed_meta | 40 | 0.100000000 | submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.008581903 | 0.080048384 | 0.008653072 | 0.000071169 |
| signed_meta | 40 | 0.100000000 | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.008660183 | 0.079857786 | 0.008962488 | 0.000302305 |
| signed_meta | 40 | 0.100000000 | submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.009287908 | 0.078706074 | 0.008896321 | -0.000391587 |
| signed_meta | 40 | 0.100000000 | submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.009538915 | 0.078389773 | 0.008685091 | -0.000853824 |
| signed_meta | 40 | 0.100000000 | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.009778713 | 0.078143522 | 0.009627268 | -0.000151445 |
| signed_meta | 40 | 0.100000000 | submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.010197382 | 0.077815634 | 0.011503720 | 0.001306338 |
| signed_meta | 40 | 0.100000000 | submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.578171818 | 0.010424224 | 0.077680359 | 0.010005499 | -0.000418725 |
| signed_meta | 40 | 0.100000000 | submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.010555771 | 0.077612861 | 0.011078657 | 0.000522885 |
| signed_meta | 40 | 0.100000000 | submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.010679759 | 0.077555670 | 0.008859329 | -0.001820430 |
| signed_meta | 40 | 0.100000000 | submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.012053692 | 0.077197468 | 0.010636180 | -0.001417513 |
| signed_meta | 40 | 0.100000000 | submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.012499225 | 0.077145609 | 0.014421759 | 0.001922534 |
| signed_meta | 40 | 0.100000000 | submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.013479734 | 0.077081212 | 0.013237808 | -0.000241926 |

Candidates:

| candidate_id | spec_name | selected_basis_actions | selected_cells | changed_rows_vs_h057 | route_basis_pred_delta_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_conflict_rate | mean_assignment_route_score | cos_h088_direction | max_positive_bad_cosine | h100_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h100_routebasis_conflict_c80_r30_amp100_6c8e0c6b | routebasis_conflict_c80_r30_amp100 | 24 | 28 | 24 | -0.001031371 | -0.000045499 | 0.000023038 | 0.000039607 | 1.000000000 | 1.000000000 | 1.000000000 | 0.389666931 | -0.053927370 | 0.000000000 | 0.758271941 | submission_h100_routebasis_conflict_c80_r30_amp100_6c8e0c6b.csv |
| h100_routebasis_mixed_c150_r52_amp085_aa7a8207 | routebasis_mixed_c150_r52_amp085 | 33 | 37 | 33 | -0.000858230 | -0.000042628 | 0.000036634 | 0.000043174 | 1.000000000 | 0.756756757 | 0.756756757 | 0.496245334 | -0.110030233 | 0.007420646 | 0.654678687 | submission_h100_routebasis_mixed_c150_r52_amp085_aa7a8207.csv |
| h100_routebasis_highassign_c120_r28_amp075_4ef8e77e | routebasis_highassign_c120_r28_amp075 | 28 | 43 | 28 | -0.000031861 | -0.000061540 | 0.000029724 | 0.000033821 | 0.976744186 | 0.837209302 | 0.813953488 | 0.549792152 | -0.088389487 | 0.000000000 | 0.455632336 | submission_h100_routebasis_highassign_c120_r28_amp075_4ef8e77e.csv |
| h100_routebasis_objective_c140_r55_amp090_6fea2515 | routebasis_objective_c140_r55_amp090 | 35 | 42 | 35 | -0.000015376 | -0.000082066 | 0.000063128 | 0.000061703 | 1.000000000 | 0.738095238 | 0.738095238 | 0.507357790 | -0.205704775 | 0.060721487 | 0.410279677 | submission_h100_routebasis_objective_c140_r55_amp090_6fea2515.csv |
| h100_routebasis_q2tox_c70_r45_amp090_f5ff7684 | routebasis_q2tox_c70_r45_amp090 | 20 | 32 | 20 | 0.000258695 | -0.000021899 | 0.000026976 | 0.000023788 | 0.968750000 | 0.875000000 | 0.843750000 | 0.467910326 | -0.091209740 | 0.053566275 | 0.355953710 | submission_h100_routebasis_q2tox_c70_r45_amp090_f5ff7684.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | h098_feature_set | h098_alpha | route_basis_feature_set | route_basis_k_basis | route_basis_alpha | route_basis_n_x_features | route_basis_loo_mae | route_basis_loo_rmse | route_basis_weighted_loo_mae | route_basis_weighted_loo_rmse | route_basis_loo_spearman | route_basis_loo_pair_acc | route_basis_h088_loo_pred | route_basis_h088_loo_error | route_basis_h088_loo_abs_error | route_basis_h088_sign_ok | route_basis_base_loo_abs_error | route_basis_full_fit_weighted_mae | route_basis_route_basis_rank_score | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | route_basis_pred_delta_vs_h057 | route_basis_k | selected_basis_actions | mean_h100_action_score | mean_route_basis_action_delta | mean_assignment_route_score | mean_h099_route_score | basis_specs | h100_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h100_route_action_basis_equation | h100_routebasis_conflict_c80_r30_amp100_6c8e0c6b | /Users/kbsoo/Downloads/cl2/submission_h100_route_basis_6c8e0c6b_uploadsafe.csv | route-action public equation selects H057/H088 conflict assignments directly | state_core | 0.100000000 | signed_meta | 40 | 0.100000000 | 45 | 0.000477320 | 0.000728885 | 0.000216509 | 0.000293285 | 0.897151576 | 0.876363636 | 0.000852872 | 0.000106264 | 0.000106264 | 1.000000000 | 0.000148814 | 0.000040252 | 0.000048993 | h100_routebasis_conflict_c80_r30_amp100_6c8e0c6b | routebasis_conflict_c80_r30_amp100 | route_basis | conflict | state_core | 0.100000000 | 80 | 1.000000000 | 2.000000000 | 28 | 28 | 24 | -0.000045499 | 0.000023038 | 0.000039607 | 1.000000000 | 1.000000000 | 0.641579592 | 1.000000000 | 0.029634984 | 0.583857143 | -0.053927370 | 0.206952891 | 0.195536213 | 0.000000000 | 0.000251385 | 0.087877993 | 10 | 0,3,10,35,56,61,70,78,98,101,110,135,136,139,143,144,146,149,151,164,196,216,226,235 | 0.389813975 | submission_h100_routebasis_conflict_c80_r30_amp100_6c8e0c6b.csv | /Users/kbsoo/Downloads/cl2/hitl/h100_route_action_basis_equation_hsjepa/submission_h100_routebasis_conflict_c80_r30_amp100_6c8e0c6b.csv | 6 | 0 | 12 | 2 | 2 | 1 | 5 | -0.029604327 | -0.035181559 | -0.040795364 | -0.025103410 | -0.046140466 | -0.040311452 | -0.053431293 | /Users/kbsoo/Downloads/cl2/hitl/h100_route_action_basis_equation_hsjepa/submission_h100_routebasis_conflict_c80_r30_amp100_6c8e0c6b.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 28 | True | -0.001031371 | 40 | 24 | 0.699765542 | -0.000041052 | 0.389666931 | 0.593031143 | basis_conflict_a052,basis_objective_a042,basis_q2_counter_a050 | 0.758271941 | /Users/kbsoo/Downloads/cl2/submission_h100_route_basis_6c8e0c6b_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 28 | True |

Interpretation rule:

- If H100 improves over H099/H098, route-action basis is the right public/private
  equation space.
- If H099 improves but H100 loses, route constraints help but public response
  cannot be fitted directly in route basis.
- If H098 wins over both, the hidden law is sparse signed cells rather than
  discrete route assignments.
