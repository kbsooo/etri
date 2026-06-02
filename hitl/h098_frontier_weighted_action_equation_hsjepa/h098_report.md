# H098 Frontier-Weighted Signed Action Equation HS-JEPA

Question: can the signed public-action equation explain H088 when frontier
observations are weighted above old bad submissions?

Frontier model scores:

| feature_set | alpha | n_x_features | loo_mae | loo_rmse | weighted_loo_mae | weighted_loo_rmse | loo_spearman | loo_pair_acc | h088_loo_pred | h088_loo_error | h088_loo_abs_error | h088_sign_ok | base_loo_abs_error | full_fit_weighted_mae | frontier_rank_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| state_core | 0.100000000 | 105 | 0.000382080 | 0.000599751 | 0.000417068 | 0.000733256 | 0.921069820 | 0.905454545 | 0.000756822 | 0.000010214 | 0.000010214 | 1.000000000 | 0.001495198 | 0.000010844 | 0.001130166 |
| state_context | 0.300000000 | 120 | 0.000483356 | 0.000741965 | 0.000453877 | 0.000694594 | 0.988040902 | 0.963636364 | 0.000563381 | -0.000183227 | 0.000183227 | 1.000000000 | 0.001365549 | 0.000026551 | 0.001324957 |
| state_core | 0.300000000 | 105 | 0.000378832 | 0.000518409 | 0.000471839 | 0.000683344 | 0.927592977 | 0.912727273 | 0.000218363 | -0.000528245 | 0.000528245 | 1.000000000 | 0.001314198 | 0.000019580 | 0.001871714 |
| state_core | 0.030000000 | 105 | 0.000460536 | 0.000805610 | 0.000558961 | 0.000876598 | 0.928897608 | 0.905454545 | 0.001220230 | 0.000473622 | 0.000473622 | 1.000000000 | 0.001725743 | 0.000004942 | 0.002227087 |
| state_core | 0.003000000 | 105 | 0.000438698 | 0.000751654 | 0.000585237 | 0.000996206 | 0.965862167 | 0.934545455 | 0.001057396 | 0.000310788 | 0.000310788 | 1.000000000 | 0.002030645 | 0.000001208 | 0.002235906 |
| state_context | 0.100000000 | 120 | 0.000421551 | 0.000611679 | 0.000575594 | 0.000824723 | 0.980213113 | 0.952727273 | 0.001297413 | 0.000550805 | 0.000550805 | 1.000000000 | 0.001606176 | 0.000015525 | 0.002252509 |
| state_core | 0.010000000 | 105 | 0.000480525 | 0.000833271 | 0.000616090 | 0.000964401 | 0.961078518 | 0.930909091 | 0.001327755 | 0.000581147 | 0.000581147 | 1.000000000 | 0.001895964 | 0.000002332 | 0.002598612 |
| state_context | 1.000000000 | 120 | 0.000555726 | 0.000802157 | 0.000524746 | 0.000699704 | 0.983692130 | 0.956363636 | -0.000121287 | -0.000867895 | 0.000867895 | 0.000000000 | 0.001137902 | 0.000042149 | 0.002697366 |
| state_core | 1.000000000 | 105 | 0.000486224 | 0.000622912 | 0.000541896 | 0.000737497 | 0.964557535 | 0.934545455 | -0.000311242 | -0.001057850 | 0.001057850 | 0.000000000 | 0.001160783 | 0.000034242 | 0.003056165 |
| state_context | 100.000000000 | 120 | 0.000771175 | 0.001056613 | 0.000606784 | 0.000762733 | 0.980213113 | 0.952727273 | -0.000647214 | -0.001393822 | 0.001393822 | 0.000000000 | 0.000643444 | 0.000228896 | 0.003328856 |
| state_core | 100.000000000 | 105 | 0.000754724 | 0.001055874 | 0.000619033 | 0.000765676 | 0.984996762 | 0.960000000 | -0.000626589 | -0.001373197 | 0.001373197 | 0.000000000 | 0.000680976 | 0.000237398 | 0.003332038 |
| target_only | 100.000000000 | 59 | 0.000757447 | 0.001173141 | 0.000628694 | 0.000803888 | 0.978908482 | 0.949090909 | -0.000758306 | -0.001504914 | 0.001504914 | 0.000000000 | 0.000505594 | 0.000275264 | 0.003458215 |
| state_context | 3.000000000 | 120 | 0.000573642 | 0.000722520 | 0.000574337 | 0.000777056 | 0.983692130 | 0.956363636 | -0.000612873 | -0.001359481 | 0.001359481 | 0.000000000 | 0.000985033 | 0.000059739 | 0.003468939 |
| state_core | 3.000000000 | 105 | 0.000541524 | 0.000682783 | 0.000596888 | 0.000831643 | 0.982822376 | 0.952727273 | -0.000751738 | -0.001498346 | 0.001498346 | 0.000000000 | 0.001033018 | 0.000053710 | 0.003770171 |
| state_context | 0.030000000 | 120 | 0.000382944 | 0.000629477 | 0.000773402 | 0.001076105 | 0.966731921 | 0.938181818 | 0.002045058 | 0.001298450 | 0.001298450 | 1.000000000 | 0.001892180 | 0.000007240 | 0.003949540 |

Selected-model LOO predictions:

| feature_set | alpha | file | public_lb | delta_vs_h057 | frontier_weight | loo_pred_delta | loo_error |
| --- | --- | --- | --- | --- | --- | --- | --- |
| state_core | 0.100000000 | submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | 0.567747594 | 0.000000000 | 5.469148518 | -0.001495198 | -0.001495198 |
| state_core | 0.100000000 | submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.567904825 | 0.000157231 | 4.379922090 | 0.000343423 | 0.000186192 |
| state_core | 0.100000000 | submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.000157231 | 4.379922090 | 0.000169770 | 0.000012539 |
| state_core | 0.100000000 | submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.568123483 | 0.000375889 | 3.817133290 | 0.000286721 | -0.000089168 |
| state_core | 0.100000000 | submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.568494202 | 0.000746608 | 4.455340062 | 0.000756822 | 0.000010214 |
| state_core | 0.100000000 | submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.008411356 | 0.080509308 | 0.008659837 | 0.000248482 |
| state_core | 0.100000000 | submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.008532974 | 0.080173991 | 0.008679010 | 0.000146036 |
| state_core | 0.100000000 | submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.576290429 | 0.008542835 | 0.080148262 | 0.008648781 | 0.000105945 |
| state_core | 0.100000000 | submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.008543736 | 0.080145922 | 0.008627335 | 0.000083599 |
| state_core | 0.100000000 | submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.008552772 | 0.080122549 | 0.008645136 | 0.000092363 |
| state_core | 0.100000000 | submission_mixmin_0c916bb4.csv | 0.576306641 | 0.008559047 | 0.080106422 | 0.008678317 | 0.000119270 |
| state_core | 0.100000000 | submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.008564237 | 0.080093145 | 0.008677004 | 0.000112767 |
| state_core | 0.100000000 | submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.008581903 | 0.080048384 | 0.008705502 | 0.000123598 |
| state_core | 0.100000000 | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.008660183 | 0.079857786 | 0.008762817 | 0.000102634 |
| state_core | 0.100000000 | submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.009287908 | 0.078706074 | 0.008946557 | -0.000341351 |
| state_core | 0.100000000 | submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.009538915 | 0.078389773 | 0.008564706 | -0.000974209 |
| state_core | 0.100000000 | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.009778713 | 0.078143522 | 0.009944311 | 0.000165598 |
| state_core | 0.100000000 | submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.010197382 | 0.077815634 | 0.010055198 | -0.000142184 |
| state_core | 0.100000000 | submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.578171818 | 0.010424224 | 0.077680359 | 0.008973766 | -0.001450458 |
| state_core | 0.100000000 | submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.010555771 | 0.077612861 | 0.010147771 | -0.000408000 |
| state_core | 0.100000000 | submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.010679759 | 0.077555670 | 0.011610357 | 0.000930598 |
| state_core | 0.100000000 | submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.012053692 | 0.077197468 | 0.012345422 | 0.000291729 |
| state_core | 0.100000000 | submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.012499225 | 0.077145609 | 0.011149510 | -0.001349715 |
| state_core | 0.100000000 | submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.013479734 | 0.077081212 | 0.013291664 | -0.000188070 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_conflict_rate | cos_h088_direction | cos_h057_vs_h042_direction | max_positive_bad_cosine | h098_frontier_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h098_frontier_conflict_c83_a052_a748e477 | frontier_conflict_c83_a052 | 46 | 20 | -0.000133512 | 0.000157151 | 0.000224030 | 1.000000000 | 1.000000000 | 1.000000000 | -0.078470824 | 0.351986279 | 0.000000000 | 0.514096034 | submission_h098_frontier_conflict_c83_a052_a748e477.csv |
| h098_frontier_descent_all_c220_a040_7dd22fd7 | frontier_descent_all_c220_a040 | 208 | 120 | -0.001041800 | 0.000487924 | 0.000497597 | 0.745192308 | 0.187500000 | 0.211538462 | -0.244724287 | 0.055845538 | 0.074364748 | 0.425879394 | submission_h098_frontier_descent_all_c220_a040_7dd22fd7.csv |
| h098_frontier_objective_c160_a045_a5e2b09b | frontier_objective_c160_a045 | 159 | 106 | -0.000913463 | 0.000419475 | 0.000392558 | 0.779874214 | 0.220125786 | 0.238993711 | -0.222249242 | 0.042551572 | 0.096024724 | 0.403799274 | submission_h098_frontier_objective_c160_a045_a5e2b09b.csv |
| h098_frontier_counter_h088_c180_a045_01e6348a | frontier_counter_h088_c180_a045 | 168 | 102 | -0.000200572 | 0.000673659 | 0.000540501 | 1.000000000 | 0.255952381 | 0.255952381 | -0.529245835 | 0.063498943 | 0.230822746 | 0.239392517 | submission_h098_frontier_counter_h088_c180_a045_01e6348a.csv |
| h098_frontier_q2_c85_a060_a15ca596 | frontier_q2_c85_a060 | 63 | 63 | -0.000520862 | 0.000454597 | 0.000503113 | 0.539682540 | 0.000000000 | 0.000000000 | -0.092254272 | 0.000000000 | 0.043027183 | 0.206969676 | submission_h098_frontier_q2_c85_a060_a15ca596.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | response_feature_set | response_alpha | response_n_x_features | response_loo_mae | response_loo_rmse | response_weighted_loo_mae | response_weighted_loo_rmse | response_loo_spearman | response_loo_pair_acc | response_h088_loo_pred | response_h088_loo_error | response_h088_loo_abs_error | response_h088_sign_ok | response_base_loo_abs_error | response_full_fit_weighted_mae | response_frontier_rank_score | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h098_frontier_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h098_frontier_weighted_action_equation | h098_frontier_conflict_c83_a052_a748e477 | /Users/kbsoo/Downloads/cl2/submission_h098_frontier_equation_a748e477_uploadsafe.csv | frontier equation keeps the H096 conflict field but uses lower amplitude | state_core | 0.100000000 | 105 | 0.000382080 | 0.000599751 | 0.000417068 | 0.000733256 | 0.921069820 | 0.905454545 | 0.000756822 | 0.000010214 | 0.000010214 | 1.000000000 | 0.001495198 | 0.000010844 | 0.001130166 | h098_frontier_conflict_c83_a052_a748e477 | frontier_conflict_c83_a052 | conflict_invert | conflict | state_core | 0.100000000 | 83 | 0.520000000 | 0.680000000 | 46 | 46 | 20 | -0.000133512 | 0.000157151 | 0.000224030 | 1.000000000 | 1.000000000 | 0.660273913 | 1.000000000 | 0.057449801 | 0.656434783 | -0.078470824 | 0.351986279 | 0.328211989 | 0.000000000 | 0.001022429 | 0.087877993 | 8 | 0,3,10,61,70,78,98,101,110,135,136,139,143,144,146,149,151,164,196,226 | 0.438368065 | submission_h098_frontier_conflict_c83_a052_a748e477.csv | /Users/kbsoo/Downloads/cl2/hitl/h098_frontier_weighted_action_equation_hsjepa/submission_h098_frontier_conflict_c83_a052_a748e477.csv | 6 | 0 | 11 | 8 | 5 | 7 | 9 | -0.101501877 | -0.096880741 | -0.111672906 | -0.076834341 | -0.089902057 | -0.104276101 | -0.097777920 | /Users/kbsoo/Downloads/cl2/hitl/h098_frontier_weighted_action_equation_hsjepa/submission_h098_frontier_conflict_c83_a052_a748e477.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 46 | True | 0.514096034 | /Users/kbsoo/Downloads/cl2/submission_h098_frontier_equation_a748e477_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 46 | True |

Interpretation rule:

- If H098 improves, the action-equation solver should be frontier-weighted and
  H088 must be a first-class training sensor.
- If H098 loses but H096 wins, the H088 sensor is useful only as local conflict
  inversion, not as a global response model.
- If both lose, the signed equation needs row/route constraints rather than
  cell-level gradients.
