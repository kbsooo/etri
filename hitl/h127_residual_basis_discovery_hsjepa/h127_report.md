# H127 Residual Basis Discovery HS-JEPA

Question: after H126 proves coefficient solving is too narrow, does a new
safe action basis exist outside the current support and outside the H122-pruned
toxic sector?

Audit:

| spec_name | condition | pool_rows | added_cells | component_gain |
| --- | --- | --- | --- | --- |
| objective_residual_newbasis | objective | 25 |  |  |
| subjective_q_residual_newbasis | q_subjective | 13 |  |  |
| anti_h088_residual_newbasis | anti_h088 | 6 |  |  |
| null_antidote_residual_newbasis | null_antidote | 28 |  |  |
| episode_neighbor_residual_newbasis | episode_neighbor | 7 | 1.000000000 | 0.000701942 |

Start metrics:

| baseline | route | h098 | curv_marg | badw | badmax | h088 | margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| h126_soft | -0.000702257 | -0.000030951 | 0.000044917 | 0.000000000 | 0.000000000 | -0.057669876 | 0.149910590 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | h127_added_cells | h127_added_targets | h127_delta_start_route | h127_delta_start_h098 | h127_delta_start_h088 | h127_delta_start_margin | model_pred_delta_vs_h057 | route_basis_pred_delta_vs_h057 | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | h127_component_gain | h127_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h127_episode_neighbor_residual_newbasis_9b7f8d9a | episode_neighbor_residual_newbasis | 29 | 24 | 8 | 0 | 5 | 9 | 5 | 0 | 2 | 1 | S2:1 | 0.000001059 | -0.000000360 | 0.006511447 | 0.010523322 | -0.000031310 | -0.000701198 | -0.051158429 | 0.160433912 | 0.000701942 | 0.327437825 | submission_h127_episode_neighbor_residual_newbasis_9b7f8d9a.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | route_basis_pred_delta_vs_h057 | selected_mean_residual_toxicity | selected_mean_residual_safety | selected_mean_residual_gap | selected_mean_antidote_score | selected_same_bad_residual | selected_opp_bad_residual | selected_same_good_residual | selected_opp_good_residual | selected_h111_cells | selected_h108_rejected_cells | selected_h109_cells | selected_mean_family_count | h112_information_mass | h112_score | h118_h126_overlap_cells | h118_h126_cosine | h118_h125_overlap_cells | h118_h125_cosine | h118_h124_overlap_cells | h118_h124_cosine | h118_h122_overlap_cells | h118_h122_cosine | h118_h088_overlap_cells | h118_h088_cosine | h118_zero_curv | h118_curv_pred_delta_vs_h057 | h118_curv_marginal_vs_zero | h118_mean_forbidden_same | h118_max_forbidden_same | h118_mean_forbidden_pressure | h118_mean_veto_score | h118_selected_rows | h127_start_cells | h127_added_cells | h127_added_rows | h127_added_targets | h127_component_gain | h127_delta_start_route | h127_delta_start_h098 | h127_delta_start_h088 | h127_delta_start_margin | h118_score | h127_worldview | h127_fit_feature_set | h127_fit_alpha | h127_fit_score | h127_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h127_residual_basis_discovery | h127_episode_neighbor_residual_newbasis_9b7f8d9a | /Users/kbsoo/Downloads/cl2/submission_h127_residbasis_9b7f8d9a_uploadsafe.csv | safe action basis is an episode-neighbor extension around current rows, not isolated global top cells | h127_episode_neighbor_residual_newbasis_9b7f8d9a | episode_neighbor_residual_newbasis | public_residual_toxicity_solver | forbidden_veto_residual_episode | state_core | 0.100000000 | 38 | 1.000000000 | 0.250000000 | 29 | 29 | 24 | -0.000031310 | -0.000007967 | -0.000004191 | 0.482758621 | 0.586206897 | 0.457403941 | 0.310344828 | 0.290289915 | 0.383674877 | -0.009376656 | 0.150019664 | 0.063253843 | 0.000000000 | 0.000096273 | 0.037061466 | 7 | 53,55,59,70,79,93,97,101,102,103,131,135,137,144,145,148,149,150,151,164,188,196,205,207 | 0.214212458 | submission_h127_episode_neighbor_residual_newbasis_9b7f8d9a.csv | /Users/kbsoo/Downloads/cl2/hitl/h127_residual_basis_discovery_hsjepa/submission_h127_episode_neighbor_residual_newbasis_9b7f8d9a.csv | 8 | 0 | 5 | 9 | 5 | 0 | 2 | -0.161344790 | -0.178087704 | -0.176691595 | -0.147097523 | -0.163886616 | -0.189790277 | -0.170988122 | /Users/kbsoo/Downloads/cl2/hitl/h127_residual_basis_discovery_hsjepa/submission_h127_episode_neighbor_residual_newbasis_9b7f8d9a.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 29 | True | 0.000000000 | 0.000000000 | -0.051158429 | 0.160433912 | 0.150558741 | 0.160433912 | -0.000701198 | 0.408105586 | 0.673961589 | 0.265856003 | 0.801268571 | 0.001398101 | 5.295196287 | 0.056898231 | 5.178361535 | 13 | 6 | 3 | 2.689655172 | 0.727844828 | 0.450372514 | 28 | 0.998718401 | 28 | 0.998431741 | 27 | 0.998431081 | 24 | 0.989900864 | 22 | -0.051158429 | -0.000261663 | -0.000216171 | 0.000045493 | 0.000000000 | 0.000000000 | 0.000000000 | 1.000000000 | 24 | 28 | 1 | 1 | S2:1 | 0.000701942 | 0.000001059 | -0.000000360 | 0.006511447 | 0.010523322 | 0.391381166 | safe action basis is an episode-neighbor extension around current rows, not isolated global top cells | route_curvature | 30.000000000 | 0.001054773 | 0.327437825 | /Users/kbsoo/Downloads/cl2/submission_h127_residbasis_9b7f8d9a_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 29 | True |

Interpretation rule:

- If H127 improves, H126 was missing an orthogonal residual action component.
- If H126/H125/H124 improve more, residual basis discovery is still finding
  local stress artifacts, and the next big bet must change the proposal
  generator rather than mine the same residual pool.
- If no H127 candidate improves or survives, the current residual pool is
  diagnostic only after H122 pruning.
