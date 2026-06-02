# H102 Bad-Axis Nullspace Assignment HS-JEPA

Question: can H100 route-actions become safer when the decoder avoids the
positive span of known bad public submission axes?

Bad axes:

| axis_name | axis_type | weight | delta_vs_h057 |
| --- | --- | --- | --- |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | bad_public | 1.207847706 | 0.000746608 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | bad_public | 0.900771346 | 0.008411356 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | bad_public | 0.904800483 | 0.008532974 |
| submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | bad_public | 0.905124804 | 0.008542835 |
| submission_e95_hardtail_541e3973.csv | bad_public | 0.905154411 | 0.008543736 |
| submission_e101_q2s3tail_177569bc.csv | bad_public | 0.905451253 | 0.008552772 |
| submission_mixmin_0c916bb4.csv | bad_public | 0.905657198 | 0.008559047 |
| submission_e176_abl_q2_to0p75_91e49725.csv | bad_public | 0.905827456 | 0.008564237 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | bad_public | 0.906406215 | 0.008581903 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | bad_public | 0.908957224 | 0.008660183 |
| submission_e323_5508f966_uploadsafe.csv | bad_public | 1.062415618 | 0.009287908 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | bad_public | 1.069942071 | 0.009538915 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | bad_public | 1.076958683 | 0.009778713 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | bad_public | 0.955068568 | 0.010197382 |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | bad_public | 1.095062721 | 0.010424224 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | bad_public | 0.964863612 | 0.010555771 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | bad_public | 0.968178504 | 0.010679759 |
| submission_jepa_latent_q2_w0p45.csv | bad_public | 1.136388336 | 0.012053692 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | bad_public | 1.146754486 | 0.012499225 |
| submission_jepa_latent_residual_probe.csv | bad_public | 1.168369304 | 0.013479734 |

Good anchor axes:

| axis_name | axis_type | weight | delta_vs_h057 |
| --- | --- | --- | --- |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | h057_positive_anchor | 1.000000000 | 0.000000000 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | h057_positive_anchor | 1.000000000 | 0.000000000 |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | h057_positive_anchor | 1.000000000 | 0.000000000 |

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

Candidates:

| candidate_id | spec_name | selected_basis_actions | selected_cells | changed_rows_vs_h057 | route_basis_pred_delta_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | h102_cum_bad_weighted_pos | h102_cum_bad_max_pos | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | anti_h088_direction_rate | h057_positive_align_rate | selected_conflict_rate | h102_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h102_routegain_badnull_c150_r52_amp085_e775939d | routegain_badnull_c150_r52_amp085 | 5 | 7 | 5 | -0.001162460 | -0.000023478 | 0.000004825 | 0.000006590 | 0.000000000 | 0.000000000 | -0.002160809 | 0.013257520 | 0.857142857 | 0.857142857 | 1.000000000 | 0.936796459 | submission_h102_routegain_badnull_c150_r52_amp085_e775939d.csv |
| h102_strict_null_conflict_c72_r28_amp100_624355db | strict_null_conflict_c72_r28_amp100 | 23 | 29 | 23 | -0.000307476 | -0.000034866 | 0.000026105 | 0.000039378 | 0.000000000 | 0.000000000 | -0.007562178 | 0.035271193 | 1.000000000 | 1.000000000 | 1.000000000 | 0.747008065 | submission_h102_strict_null_conflict_c72_r28_amp100_624355db.csv |
| h102_shadow_margin_conflict_c96_r34_amp105_008a60e1 | shadow_margin_conflict_c96_r34_amp105 | 24 | 30 | 24 | -0.000198976 | -0.000035931 | 0.000028743 | 0.000042843 | 0.000000000 | 0.000000000 | -0.007638216 | 0.035353495 | 1.000000000 | 1.000000000 | 1.000000000 | 0.714368917 | submission_h102_shadow_margin_conflict_c96_r34_amp105_008a60e1.csv |
| h102_lowtox_objective_null_c110_r40_amp095_5ea355ff | lowtox_objective_null_c110_r40_amp095 | 39 | 51 | 39 | -0.000356324 | -0.000065266 | 0.000089060 | 0.000084038 | 0.017171225 | 0.020742778 | -0.083999933 | 0.106475169 | 0.882352941 | 0.549019608 | 0.450980392 | 0.540251091 | submission_h102_lowtox_objective_null_c110_r40_amp095_5ea355ff.csv |
| h102_anchor_shadow_bridge_c128_r42_amp090_e14d75a2 | anchor_shadow_bridge_c128_r42_amp090 | 39 | 49 | 39 | -0.000096959 | -0.000111862 | 0.000079810 | 0.000079182 | 0.028512746 | 0.033289129 | -0.083431918 | 0.060249525 | 0.979591837 | 0.673469388 | 0.653061224 | 0.535106821 | submission_h102_anchor_shadow_bridge_c128_r42_amp090_e14d75a2.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | h098_feature_set | h098_alpha | route_basis_feature_set | route_basis_k_basis | route_basis_alpha | route_basis_n_x_features | route_basis_loo_mae | route_basis_loo_rmse | route_basis_weighted_loo_mae | route_basis_weighted_loo_rmse | route_basis_loo_spearman | route_basis_loo_pair_acc | route_basis_h088_loo_pred | route_basis_h088_loo_error | route_basis_h088_loo_abs_error | route_basis_h088_sign_ok | route_basis_base_loo_abs_error | route_basis_full_fit_weighted_mae | route_basis_route_basis_rank_score | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | route_basis_pred_delta_vs_h057 | route_basis_k | selected_basis_actions | mean_h100_action_score | mean_route_basis_action_delta | mean_assignment_route_score | mean_h099_route_score | basis_specs | h100_score | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | h102_cum_route_pred_delta | h102_cum_cell_pred_delta | mean_h102_axis_score | mean_h102_good_bad_margin | mean_h102_bad_weighted_pos | mean_h102_good_max_cos | h102_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h102_bad_axis_nullspace_assignment | h102_routegain_badnull_c150_r52_amp085_e775939d | /Users/kbsoo/Downloads/cl2/submission_h102_badnull_e775939d_uploadsafe.csv | route-basis gain can be expanded if the cumulative action remains bad-axis safe | state_core | 0.100000000 | signed_meta | 40 | 0.100000000 | 45 | 0.000477320 | 0.000728885 | 0.000216509 | 0.000293285 | 0.897151576 | 0.876363636 | 0.000852872 | 0.000106264 | 0.000106264 | 1.000000000 | 0.000148814 | 0.000040252 | 0.000048993 | h102_routegain_badnull_c150_r52_amp085_e775939d | routegain_badnull_c150_r52_amp085 | route_basis | routegain_badnull | state_core | 0.100000000 | 150 | 1.000000000 | 2.000000000 | 7 | 7 | 5 | -0.000023478 | 0.000004825 | 0.000006590 | 0.857142857 | 0.857142857 | 0.564995918 | 1.000000000 | 0.120601045 | 0.584244898 | -0.010019420 | 0.042358648 | 0.054912177 | 0.000000000 | 0.000061981 | 0.031760425 | 2 | 144,146,149,151,164 | 0.316674900 | submission_h102_routegain_badnull_c150_r52_amp085_e775939d.csv | /Users/kbsoo/Downloads/cl2/hitl/h102_bad_axis_nullspace_assignment_hsjepa/submission_h102_routegain_badnull_c150_r52_amp085_e775939d.csv | 1 | 0 | 3 | 2 | 0 | 0 | 1 | -0.009896550 | -0.006225191 | -0.007901219 | -0.011964224 | -0.027508856 | -0.036938037 | -0.010812756 | /Users/kbsoo/Downloads/cl2/hitl/h102_bad_axis_nullspace_assignment_hsjepa/submission_h102_routegain_badnull_c150_r52_amp085_e775939d.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 7 | True | -0.001162460 | 40 | 5 | 0.693609644 | -0.000271585 | 0.345028080 | 0.577122822 | basis_conflict_a052,basis_objective_a042,basis_tail_hybrid_a044 | 0.731509611 | 0.000000000 | 0.000000000 | -0.002160809 | 0.013257520 | 0.011200594 | 0.013257520 | -0.001162460 | -0.000023478 | 0.784524945 | 0.022946731 | 0.000680049 | 0.023626780 | 0.936796459 | /Users/kbsoo/Downloads/cl2/submission_h102_badnull_e775939d_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 7 | True |

Interpretation rule:

- If H102 improves over H100, public/private safety is a global bad-axis
  nullspace or shadow-margin problem.
- If H100 improves but H102 loses, the bad axes overlap the true positive
  H057 route too much and should not be used as hard action constraints.
- If both lose, route-action basis is still only a sensor; the safe assignment
  field needs a different route family.
