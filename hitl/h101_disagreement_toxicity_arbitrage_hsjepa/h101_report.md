# H101 Disagreement-Toxicity Arbitrage HS-JEPA

Question: is the safe assignment field the region where route-basis equations
predict benefit while H098's cell equation does not mark the action as toxic?

Stability models:

| model_index | feature_set | k_basis | alpha | source_route_basis_rank_score | source_weighted_loo_mae | source_h088_loo_pred | source_h088_loo_error | full_fit_mae | full_fit_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | signed_meta | 40 | 0.100000000 | 0.000048993 | 0.000216509 | 0.000852872 | 0.000106264 | 0.000183571 | 0.951946098 |
| 1 | signed_meta | 70 | 0.010000000 | 0.000068987 | 0.000232439 | 0.000743653 | -0.000002955 | 0.000069228 | 0.977168973 |
| 2 | signed_meta | 70 | 0.030000000 | 0.000442380 | 0.000214146 | 0.000462405 | -0.000284203 | 0.000099959 | 0.964992412 |
| 3 | signed_abs | 140 | 30.000000000 | 0.001218409 | 0.000249466 | 0.000001682 | -0.000744926 | 0.000284854 | 0.928229665 |
| 4 | signed_meta | 100 | 0.010000000 | 0.001265185 | 0.000481538 | 0.000387869 | -0.000358739 | 0.000042669 | 0.977168973 |
| 5 | signed_abs | 180 | 30.000000000 | 0.001412917 | 0.000399606 | 0.000194156 | -0.000552452 | 0.000332281 | 0.925853468 |
| 6 | signed_meta | 40 | 0.300000000 | 0.001435332 | 0.000420676 | 0.000219166 | -0.000527442 | 0.000208681 | 0.947597326 |
| 7 | signed_abs | 180 | 10.000000000 | 0.001538952 | 0.000405741 | 0.000150465 | -0.000596143 | 0.000230845 | 0.926723223 |
| 8 | signed_meta | 100 | 0.030000000 | 0.001584386 | 0.000469413 | 0.000183666 | -0.000562942 | 0.000068129 | 0.967601675 |
| 9 | signed_abs | 180 | 0.100000000 | 0.001685992 | 0.000576239 | 0.000487065 | -0.000259543 | 0.000052160 | 0.955425115 |
| 10 | signed_abs | 180 | 3.000000000 | 0.001738612 | 0.000426360 | 0.000084422 | -0.000662186 | 0.000158346 | 0.963252904 |
| 11 | signed_abs | 180 | 0.300000000 | 0.001767664 | 0.000502685 | 0.000263548 | -0.000483060 | 0.000075983 | 0.953685606 |

Candidates:

| candidate_id | spec_name | selected_basis_actions | selected_cells | changed_rows_vs_h057 | route_basis_pred_delta_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_conflict_rate | mean_h101_route_neg_rate | mean_h101_route_cell_gap | cos_h088_direction | max_positive_bad_cosine | h101_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h101_conflict_stable_c72_r30_amp100_9e088156 | conflict_stable_c72_r30_amp100 | 5 | 6 | 5 | -0.000641455 | -0.000013693 | 0.000002988 | 0.000002753 | 0.833333333 | 0.833333333 | 1.000000000 | 0.550000000 | 0.000107892 | -0.012011850 | 0.000000000 | 0.573890268 | submission_h101_conflict_stable_c72_r30_amp100_9e088156.csv |
| h101_h100_pruned_c56_r24_amp090_20ece395 | h100_pruned_c56_r24_amp090 | 5 | 6 | 5 | -0.000576578 | -0.000012548 | 0.000002426 | 0.000002215 | 0.833333333 | 0.833333333 | 1.000000000 | 0.550000000 | 0.000107892 | -0.011934202 | 0.000000000 | 0.558798242 | submission_h101_h100_pruned_c56_r24_amp090_20ece395.csv |
| h101_stable_concord_c80_r36_amp100_12e2f66e | stable_concord_c80_r36_amp100 | 1 | 1 | 1 | 0.000001496 | -0.000002541 | 0.000000005 | -0.000000004 | 1.000000000 | 1.000000000 | 1.000000000 | 0.666666667 | -0.000000279 | -0.000827399 | 0.000000000 | 0.490227466 | submission_h101_stable_concord_c80_r36_amp100_12e2f66e.csv |
| h101_route_advantage_c70_r30_amp095_53fae6e7 | route_advantage_c70_r30_amp095 | 1 | 1 | 1 | 0.000002348 | -0.000002819 | 0.000000106 | 0.000000034 | 1.000000000 | 1.000000000 | 1.000000000 | 0.583333333 | 0.000014866 | -0.000827399 | 0.000000000 | 0.476739187 | submission_h101_route_advantage_c70_r30_amp095_53fae6e7.csv |
| h101_highassign_stable_c110_r34_amp080_3d45b771 | highassign_stable_c110_r34_amp080 | 4 | 7 | 4 | -0.000402654 | -0.000018161 | 0.000002644 | 0.000005327 | 0.285714286 | 0.285714286 | 0.714285714 | 0.583333333 | 0.000096106 | -0.007612965 | 0.007808167 | 0.342524959 | submission_h101_highassign_stable_c110_r34_amp080_3d45b771.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | h098_feature_set | h098_alpha | route_basis_feature_set | route_basis_k | route_basis_alpha | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | route_basis_pred_delta_vs_h057 | selected_basis_actions | mean_h100_action_score | mean_route_basis_action_delta | mean_assignment_route_score | mean_h099_route_score | basis_specs | h100_score | mean_h101_stability_score | mean_h101_route_pred_mean | mean_h101_route_neg_rate | mean_h101_route_cell_gap | mean_h101_route_pred_std | h101_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h101_disagreement_toxicity_arbitrage | h101_conflict_stable_c72_r30_amp100_9e088156 | /Users/kbsoo/Downloads/cl2/submission_h101_disagreement_toxicity_9e088156_uploadsafe.csv | H057/H088 conflict cells are safe only when route-basis models agree | state_core | 0.100000000 | signed_meta | 40 | 0.100000000 | h101_conflict_stable_c72_r30_amp100_9e088156 | conflict_stable_c72_r30_amp100 | route_basis | conflict_stable | state_core | 0.100000000 | 72 | 1.000000000 | 2.000000000 | 6 | 6 | 5 | -0.000013693 | 0.000002988 | 0.000002753 | 0.833333333 | 0.833333333 | 0.580890476 | 1.000000000 | 0.114749352 | 0.600476190 | -0.012011850 | 0.012713402 | 0.033233762 | 0.000000000 | 0.000041592 | 0.029891215 | 3 | 70,144,146,149,164 | 0.301280305 | submission_h101_conflict_stable_c72_r30_amp100_9e088156.csv | /Users/kbsoo/Downloads/cl2/hitl/h101_disagreement_toxicity_arbitrage_hsjepa/submission_h101_conflict_stable_c72_r30_amp100_9e088156.csv | 0 | 0 | 2 | 2 | 0 | 1 | 1 | -0.008605337 | -0.005326670 | -0.006907336 | -0.006863969 | -0.014785400 | -0.009336907 | -0.022383003 | /Users/kbsoo/Downloads/cl2/hitl/h101_disagreement_toxicity_arbitrage_hsjepa/submission_h101_conflict_stable_c72_r30_amp100_9e088156.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 6 | True | -0.000641455 | 5 | 0.632594258 | -0.000112856 | 0.332670290 | 0.561278204 | basis_conflict_a052,basis_objective_a042,basis_q2_counter_a050 | 0.579024185 | 0.632594258 | -0.000112856 | 0.550000000 | 0.000107892 | 0.000213856 | 0.573890268 | /Users/kbsoo/Downloads/cl2/submission_h101_disagreement_toxicity_9e088156_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 6 | True |

Interpretation rule:

- If H101 improves over H100, the action toxicity boundary is the disagreement
  filter between route-basis and cell-equation decoders.
- If H100 improves but H101 loses, the stronger route-basis signal should not
  be diluted by cell-equation caution.
- If both lose, route-basis action decoding is likely explanatory but not
  action-grade.
