# H126 Component-Coefficient Equation Solver HS-JEPA

Question: is public/private action safety determined by selected row-target
support, or by coefficients over the discovered action basis?

Component basis:

| component | cells | rows | l1 | l2 | Q1_cells | Q2_cells | Q3_cells | S1_cells | S2_cells | S3_cells | S4_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core | 24 | 19 | 1.209787230 | 0.310853685 | 8 | 0 | 4 | 6 | 4 | 0 | 2 |
| q3_refill | 1 | 1 | 0.034896646 | 0.034896646 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| s3_tail | 1 | 1 | 0.003563971 | 0.003563971 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| s1_margin | 2 | 2 | 0.030158238 | 0.021325296 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| id04_closure | 2 | 2 | 0.015044681 | 0.015044681 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |

Baseline equation metrics:

| baseline | route | h098 | curv_marg | badw | badmax | h088 | margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| h122 | -0.000605227 | -0.000028654 | 0.000041326 | 0.000000000 | 0.000000000 | -0.066158219 | 0.125854365 |
| h123_q3 | -0.000705948 | -0.000030422 | 0.000041718 | 0.000000000 | 0.000000000 | -0.065576731 | 0.124798254 |
| h123_sparse | -0.000732464 | -0.000026639 | 0.000041813 | 0.000000000 | 0.000000000 | -0.065510150 | 0.124697042 |
| h124 | -0.000703471 | -0.000030810 | 0.000044398 | 0.000000000 | 0.000000000 | -0.060941722 | 0.144874136 |
| h125 | -0.000702233 | -0.000031142 | 0.000045276 | 0.000000000 | 0.000000000 | -0.054368665 | 0.154855150 |

Candidates:

| candidate_id | spec_name | h126_coeff_vector | h126_duplicate_baseline | selected_cells | changed_rows_vs_h057 | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | model_pred_delta_vs_h057 | route_basis_pred_delta_vs_h057 | h118_curv_marginal_vs_zero | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | h126_margin_gain_vs_h122 | h126_route_gain_vs_h122 | h118_h088_cosine | h126_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h126_h125_closure_soft_3fe3eee4 | h125_closure_soft | core=1.0;q3=1.0;s3=0.0;s1=1.0;closure=0.5 | False | 28 | 23 | 8 | 0 | 5 | 9 | 4 | 0 | 2 | -0.000030951 | -0.000702257 | 0.000044917 | -0.057669876 | 0.149910590 | 0.024056225 | -0.000097030 | -0.057669876 | 0.310088087 | submission_h126_h125_closure_soft_3fe3eee4.csv |
| h126_h125_closure_full_f3990392 | h125_closure_full | core=1.0;q3=1.0;s3=0.0;s1=1.0;closure=1.0 | True | 28 | 23 | 8 | 0 | 5 | 9 | 4 | 0 | 2 | -0.000031142 | -0.000702233 | 0.000045276 | -0.054368665 | 0.154855150 | 0.029000785 | -0.000097006 | -0.054368665 | 0.310752367 | submission_h126_h125_closure_full_f3990392.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | route_basis_pred_delta_vs_h057 | selected_mean_residual_toxicity | selected_mean_residual_safety | selected_mean_residual_gap | selected_mean_antidote_score | selected_same_bad_residual | selected_opp_bad_residual | selected_same_good_residual | selected_opp_good_residual | selected_h111_cells | selected_h108_rejected_cells | selected_h109_cells | selected_mean_family_count | h112_information_mass | h112_score | h118_h125_overlap_cells | h118_h125_cosine | h118_h124_overlap_cells | h118_h124_cosine | h118_h123_overlap_cells | h118_h123_cosine | h118_h122_overlap_cells | h118_h122_cosine | h118_h088_overlap_cells | h118_h088_cosine | h118_h057_overlap_cells | h118_h057_cosine | h118_zero_curv | h118_curv_pred_delta_vs_h057 | h118_curv_marginal_vs_zero | h118_mean_forbidden_same | h118_max_forbidden_same | h118_mean_forbidden_pressure | h118_mean_veto_score | h118_selected_rows | h126_core_coeff | h126_q3_coeff | h126_s3_coeff | h126_s1_margin_coeff | h126_closure_coeff | h126_margin_gain_vs_h122 | h126_route_gain_vs_h122 | h126_h098_gain_vs_h122 | h126_h088_shift_vs_h122 | h126_component_cells | h118_score | h126_group | h126_worldview | h126_fit_feature_set | h126_fit_alpha | h126_fit_score | h126_coeff_vector | h126_duplicate_baseline | h126_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h126_component_coefficient_equation_solver | h126_h125_closure_soft_3fe3eee4 | /Users/kbsoo/Downloads/cl2/submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | row-bundle closure is real but should be softened because full closure may over-complete H124 | h126_h125_closure_soft_3fe3eee4 | h125_closure_soft | public_residual_toxicity_solver | forbidden_veto_coeff_soft_closure | state_core | 0.100000000 | 34 | 1.000000000 | 0.250000000 | 28 | 28 | 23 | -0.000030951 | -0.000007967 | -0.000004191 | 0.500000000 | 0.571428571 | 0.451784694 | 0.321428571 | 0.286904539 | 0.391000000 | -0.009376656 | 0.150019664 | 0.063253843 | 0.000000000 | 0.000096273 | 0.037061466 | 7 | 53,55,59,70,79,93,97,101,102,103,131,135,137,145,148,149,150,151,164,188,196,205,207 | 0.214928812 | submission_h126_h125_closure_soft_3fe3eee4.csv | /Users/kbsoo/Downloads/cl2/hitl/h126_component_coefficient_equation_hsjepa/submission_h126_h125_closure_soft_3fe3eee4.csv | 8 | 0 | 5 | 9 | 4 | 0 | 2 | -0.161344756 | -0.178087660 | -0.176691558 | -0.147097495 | -0.163886592 | -0.189790246 | -0.170988092 | /Users/kbsoo/Downloads/cl2/hitl/h126_component_coefficient_equation_hsjepa/submission_h126_h125_closure_soft_3fe3eee4.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 28 | True | 0.000000000 | 0.000000000 | -0.057669876 | 0.149910590 | 0.140012385 | 0.149910590 | -0.000702257 | 0.409336755 | 0.672582778 | 0.263246023 | 0.801046939 | 0.001448033 | 5.063296421 | 0.058015470 | 4.938150327 | 12 | 6 | 3 | 2.607142857 | 0.699107143 | 0.444065547 | 28 | 0.999712972 | 27 | 0.999712311 | 25 | 0.997332460 | 24 | 0.991171148 | 21 | -0.057669876 | 0 | 0.000000000 | -0.000261663 | -0.000216746 | 0.000044917 | 0.000000000 | 0.000000000 | 0.000000000 | 1.000000000 | 23 | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | 0.500000000 | 0.024056225 | -0.000097030 | -0.000002297 | 0.008488343 | core:24;q3_refill:1;s3_tail:1;s1_margin:2;id04_closure:2 | 0.391031858 | coeff_soft_closure | row-bundle closure is real but should be softened because full closure may over-complete H124 | route_curvature | 30.000000000 | 0.001054773 | core=1.0;q3=1.0;s3=0.0;s1=1.0;closure=0.5 | False | 0.310088087 | /Users/kbsoo/Downloads/cl2/submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 28 | True |

Interpretation rule:

- If H126 improves, the hidden action field is an equation over components, not
  a discrete selected-cell set.
- If H124/H125 stay better, action support matters more than coefficient
  solving; H126 coefficient freedom is mostly local stress overfit.
- If route-tail variants improve, S3 tail was underweighted by previous
  diagnostics and should be brought back as a quarantined private/public route.
