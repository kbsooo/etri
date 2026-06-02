# H120 Toxic-Posterior Row-Sensor HS-JEPA

Question: after H119 failed, can H085 still be useful as a row-level public
sensor if the actual action is decoded by H118/H112 residual safety?

Filter audit:

| spec_name | prefilter_rows | row_sensor_rank_pass | row_sensor_raw_pass | residual_safety_pass | residual_toxicity_pass | h118_score_pass |
| --- | --- | --- | --- | --- | --- | --- |
| toxrow_contra_core_c48_a052 | 492 | 107 | 102 | 488 | 297 | 491 |
| toxrow_stage_bridge_c56_a046 | 1633 | 744 | 651 | 745 | 1207 | 1205 |
| toxrow_h112_anchor_c40_a058 | 1857 | 822 | 720 | 584 | 1168 | 1262 |
| toxrow_h114_null_c42_a054 | 157 | 44 | 42 | 157 | 134 | 157 |
| toxrow_sparse_highsensor_c26_a060 | 1941 | 496 | 625 | 758 | 1352 | 1370 |

Top row sensors:

| row | h120_row_sensor_raw | h120_row_sensor_cells | h120_row_sensor_max_gain | h120_row_sensor_mean_h088 | h120_row_sensor_rank |
| --- | --- | --- | --- | --- | --- |
| 205 | 0.017565216 | 2.000000000 | 0.011165211 | 0.388007143 | 1.000000000 |
| 195 | 0.017166888 | 7.000000000 | 0.007217144 | 0.631923810 | 0.996000000 |
| 62 | 0.016386322 | 5.000000000 | 0.003237823 | 0.567371429 | 0.992000000 |
| 219 | 0.015941895 | 6.000000000 | 0.003725418 | 0.629957143 | 0.988000000 |
| 228 | 0.015824885 | 4.000000000 | 0.010155404 | 0.429661224 | 0.984000000 |
| 30 | 0.014689697 | 5.000000000 | 0.004129226 | 0.539571429 | 0.980000000 |
| 221 | 0.014645604 | 3.000000000 | 0.007563371 | 0.379930612 | 0.976000000 |
| 214 | 0.012495745 | 4.000000000 | 0.002914394 | 0.571182143 | 0.972000000 |
| 26 | 0.012318300 | 6.000000000 | 0.006188865 | 0.527253061 | 0.968000000 |
| 244 | 0.012204709 | 2.000000000 | 0.005083061 | 0.658371429 | 0.964000000 |
| 207 | 0.011657798 | 4.000000000 | 0.004329118 | 0.602571429 | 0.960000000 |
| 236 | 0.011031479 | 5.000000000 | 0.002805614 | 0.677224490 | 0.956000000 |
| 92 | 0.010929801 | 5.000000000 | 0.006696389 | 0.375424490 | 0.952000000 |
| 74 | 0.009897545 | 5.000000000 | 0.003029901 | 0.551571429 | 0.948000000 |
| 229 | 0.009427702 | 5.000000000 | 0.004608073 | 0.598983673 | 0.944000000 |
| 249 | 0.009113479 | 3.000000000 | 0.008324464 | 0.560216327 | 0.940000000 |
| 84 | 0.008785179 | 4.000000000 | 0.002279801 | 0.712502041 | 0.936000000 |
| 107 | 0.008754771 | 5.000000000 | 0.004163236 | 0.599142857 | 0.932000000 |
| 156 | 0.008208079 | 4.000000000 | 0.002830804 | 0.567869388 | 0.928000000 |
| 14 | 0.008022676 | 4.000000000 | 0.002408269 | 0.608681633 | 0.924000000 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | posterior_delta_vs_h057 | model_pred_delta_vs_h057 | route_basis_pred_delta_vs_h057 | h118_curv_marginal_vs_zero | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | selected_mean_residual_toxicity | selected_mean_residual_safety | selected_mean_residual_gap | h120_mean_row_sensor_rank | h120_h085_action_align_rate | h120_h085_action_contra_rate | h120_mean_h085_q_gain | h120_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h120_toxrow_stage_bridge_c56_a046_0b84c821 | toxrow_stage_bridge_c56_a046 | 18 | 15 | 0 | 0 | 6 | 1 | 1 | 6 | 4 | 0.000003495 | -0.000015069 | -0.000229105 | 0.000021967 | 0.000000000 | -0.000002958 | 0.106932305 | 0.425667381 | 0.603213150 | 0.177545770 | 0.789111111 | 0.500000000 | 0.500000000 | 0.000729619 | 0.366902649 | submission_h120_toxrow_stage_bridge_c56_a046_0b84c821.csv |
| h120_toxrow_contra_core_c48_a052_369d7e97 | toxrow_contra_core_c48_a052 | 6 | 6 | 0 | 0 | 3 | 0 | 0 | 3 | 0 | 0.000004116 | -0.000008994 | 0.000010716 | 0.000004417 | 0.000393182 | -0.011508186 | 0.000513034 | 0.481796524 | 0.631163149 | 0.149366625 | 0.814000000 | 0.000000000 | 1.000000000 | 0.000718963 | 0.348386856 | submission_h120_toxrow_contra_core_c48_a052_369d7e97.csv |
| h120_toxrow_h114_null_c42_a054_8b563ae4 | toxrow_h114_null_c42_a054 | 9 | 8 | 0 | 0 | 2 | 1 | 2 | 3 | 1 | 0.000000572 | -0.000006683 | -0.000097631 | 0.000041869 | 0.000000000 | -0.004803155 | 0.334332061 | 0.433804286 | 0.636877380 | 0.203073095 | 0.718666667 | 0.444444444 | 0.555555556 | 0.000560200 | 0.295771718 | submission_h120_toxrow_h114_null_c42_a054_8b563ae4.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | route_basis_pred_delta_vs_h057 | selected_mean_residual_toxicity | selected_mean_residual_safety | selected_mean_residual_gap | selected_mean_antidote_score | selected_same_bad_residual | selected_opp_bad_residual | selected_same_good_residual | selected_opp_good_residual | selected_h111_cells | selected_h108_rejected_cells | selected_h109_cells | selected_mean_family_count | h112_information_mass | h112_score | h118_h118_overlap_cells | h118_h118_cosine | h118_h115_overlap_cells | h118_h115_cosine | h118_h114_overlap_cells | h118_h114_cosine | h118_h113_overlap_cells | h118_h113_cosine | h118_h112_overlap_cells | h118_h112_cosine | h118_h107_overlap_cells | h118_h107_cosine | h118_zero_curv | h118_curv_pred_delta_vs_h057 | h118_curv_marginal_vs_zero | h118_mean_forbidden_same | h118_max_forbidden_same | h118_mean_forbidden_pressure | h118_mean_veto_score | h118_selected_rows | h120_mean_row_sensor_raw | h120_mean_row_sensor_rank | h120_mean_row_sensor_cells | h120_h085_action_align_rate | h120_h085_action_contra_rate | h120_mean_h085_q_gain | h120_mean_h085_cell_score | h118_score | h120_fit_feature_set | h120_fit_alpha | h120_fit_score | h120_forbidden_axes | h120_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h120_toxic_posterior_row_sensor | h120_toxrow_stage_bridge_c56_a046_0b84c821 | /Users/kbsoo/Downloads/cl2/submission_h120_toxrow_0b84c821_uploadsafe.csv | public-sensitive rows marked by H085 should be corrected through Q/S stage-balance residual actions | h120_toxrow_stage_bridge_c56_a046_0b84c821 | toxrow_stage_bridge_c56_a046 | public_residual_toxicity_solver | forbidden_veto_stage_bridge | state_core | 0.100000000 | 56 | 0.460000000 | 0.170000000 | 18 | 18 | 15 | -0.000015069 | 0.000003495 | 0.000001968 | 0.500000000 | 0.333333333 | 0.446642857 | 0.166666667 | 0.393113803 | 0.438904762 | 0.003047999 | 0.029791169 | 0.027974436 | 0.000000000 | 0.000088118 | 0.019918921 | 8 | 5,14,16,40,70,87,93,112,125,148,151,172,176,228,249 | 0.149041377 | submission_h120_toxrow_stage_bridge_c56_a046_0b84c821.csv | /Users/kbsoo/Downloads/cl2/hitl/h120_toxic_posterior_row_sensor_hsjepa/submission_h120_toxrow_stage_bridge_c56_a046_0b84c821.csv | 0 | 0 | 6 | 1 | 1 | 6 | 4 | -0.041216966 | -0.022296260 | -0.049285768 | -0.020657054 | -0.042576551 | -0.068165269 | -0.059874390 | /Users/kbsoo/Downloads/cl2/hitl/h120_toxic_posterior_row_sensor_hsjepa/submission_h120_toxrow_stage_bridge_c56_a046_0b84c821.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 18 | True | 0.000000000 | 0.000000000 | -0.000002958 | 0.106932305 | 0.106481182 | 0.106932305 | -0.000229105 | 0.425667381 | 0.603213150 | 0.177545770 | 0.562708413 | 0.014129409 | 0.887832992 | 0.059358388 | 0.917714232 | 6 | 3 | 0 | 1.777777778 | 0.431666667 | 0.269973972 | 6 | 0.156150524 | 1 | 0.066613205 | 3 | 0.032252832 | 4 | 0.247857070 | 6 | 0.229112104 | 1 | 0.013086976 | -0.000261663 | -0.000239696 | 0.000021967 | 0.000000000 | 0.000000000 | 0.000000000 | 1.000000000 | 15 | 0.005106462 | 0.789111111 | 4.444444444 | 0.500000000 | 0.500000000 | 0.000729619 | 0.517276316 | 0.271425691 | route_curvature | 30.000000000 | 0.001054773 | 264 | 0.366902649 | /Users/kbsoo/Downloads/cl2/submission_h120_toxrow_0b84c821_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 18 | True |

Interpretation rule:

- If H120 improves, H085 is not an action target; it is a row/context sensor.
- If H120 loses while H118 improves, H085 row localization is contaminated and
  action should remain residual/nullspace only.
- If both H118 and H120 lose, the current public/private solver is still using
  the wrong observation equation.
