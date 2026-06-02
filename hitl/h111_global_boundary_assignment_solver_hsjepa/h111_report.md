# H111 Global Boundary Assignment Solver HS-JEPA

Question: did H110 find the right local toxicity signal but use the wrong
greedy/global assignment boundary?

Boundary audit:

| group | cells | mean_boundary_score | mean_gap | mean_benefit | mean_toxicity | mean_bad_pressure | mean_shortcut |
| --- | --- | --- | --- | --- | --- | --- | --- |
| h108_kept | 29 | 0.400023670 | 0.408382442 | 0.925374172 | 0.516991729 | 0.553684729 | 0.619537438 |
| h108_rejected | 18 | 0.456159298 | 0.468639344 | 0.946721757 | 0.478082413 | 0.638222222 | 0.721969841 |
| h110_added | 8 | 0.327191815 | 0.374727829 | 0.895631829 | 0.520904000 | 0.607642857 | 0.698910714 |
| h108_all | 47 | 0.421522421 | 0.431459554 | 0.933549843 | 0.502090289 | 0.586060790 | 0.658766869 |
| h110_all | 37 | 0.384276242 | 0.401105769 | 0.918943395 | 0.517837626 | 0.565351351 | 0.636699228 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | model_pred_delta_vs_h057 | route_basis_pred_delta_vs_h057 | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | selected_mean_boundary_score | selected_mean_gap | selected_mean_toxicity | selected_h108_kept_cells | selected_h108_rejected_cells | selected_h110_added_cells | selected_h109_cells | h111_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h111_boundary_broad_null_c150_a048_7cbf5e9d | boundary_broad_null_c150_a048 | 53 | 28 | 6 | 0 | 15 | 10 | 10 | 4 | 8 | -0.000020178 | -0.000680043 | 0.000000000 | -0.015317815 | 0.132167651 | 0.404987830 | 0.432487397 | 0.494625364 | 27 | 14 | 5 | 3 | 0.739950881 | submission_h111_boundary_broad_null_c150_a048_7cbf5e9d.csv |
| h111_boundary_objective_beam_c110_a058_320ba60f | boundary_objective_beam_c110_a058 | 39 | 26 | 0 | 0 | 14 | 8 | 8 | 2 | 7 | -0.000015923 | -0.000402362 | 0.000000000 | -0.019715849 | 0.115203794 | 0.414777140 | 0.446386678 | 0.482935534 | 20 | 12 | 3 | 2 | 0.714846192 | submission_h111_boundary_objective_beam_c110_a058_320ba60f.csv |
| h111_boundary_kernel_beam_c70_a078_40634dbb | boundary_kernel_beam_c70_a078 | 15 | 13 | 1 | 0 | 5 | 3 | 1 | 1 | 4 | -0.000025334 | -0.000484081 | 0.000000000 | -0.013572488 | 0.034146620 | 0.426996048 | 0.451050573 | 0.497879025 | 9 | 3 | 1 | 1 | 0.681319497 | submission_h111_boundary_kernel_beam_c70_a078_40634dbb.csv |
| h111_rescue_h108_rejected_c62_a072_112bee63 | rescue_h108_rejected_c62_a072 | 2 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | -0.000008432 | -0.000468399 | 0.000000000 | -0.007380900 | 0.024769107 | 0.462569566 | 0.498524791 | 0.469067000 | 1 | 1 | 0 | 1 | 0.557628690 | submission_h111_rescue_h108_rejected_c62_a072_112bee63.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | h108_cells | h110_cells | h108_kept | h108_rejected | h110_added | h098_feature_set | h098_alpha | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | route_basis_pred_delta_vs_h057 | selected_mean_boundary_score | selected_mean_gap | selected_mean_toxicity | selected_h108_kept_cells | selected_h108_rejected_cells | selected_h110_added_cells | selected_h109_cells | selected_mean_family_count | selected_mean_vote_weight | h111_information_mass | h111_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h111_global_boundary_assignment_solver | h111_boundary_broad_null_c150_a048_7cbf5e9d | /Users/kbsoo/Downloads/cl2/submission_h111_boundary_7cbf5e9d_uploadsafe.csv | a broad low-toxicity field is possible if assignment is solved globally instead of greedily | 47 | 37 | 29 | 18 | 8 | state_core | 0.100000000 | h111_boundary_broad_null_c150_a048_7cbf5e9d | boundary_broad_null_c150_a048 | global_boundary_assignment_solver | broad_null | state_core | 0.100000000 | 150 | 0.480000000 | 0.200000000 | 53 | 53 | 28 | -0.000020178 | 0.000010760 | 0.000018347 | 0.905660377 | 0.924528302 | 0.576232345 | 0.830188679 | 0.111038618 | 0.604630728 | -0.078865353 | 0.274493531 | 0.256537493 | 0.000000000 | 0.000201258 | 0.028222576 | 10 | 0,3,6,10,35,56,61,70,78,93,98,99,101,110,131,135,136,139,143,144,148,150,151,164,196,216,235,238 | 0.376536068 | submission_h111_boundary_broad_null_c150_a048_7cbf5e9d.csv | /Users/kbsoo/Downloads/cl2/hitl/h111_global_boundary_assignment_solver_hsjepa/submission_h111_boundary_broad_null_c150_a048_7cbf5e9d.csv | 6 | 0 | 15 | 10 | 10 | 4 | 8 | -0.069767366 | -0.061556044 | -0.073267336 | -0.053174064 | -0.071867036 | -0.057956693 | -0.074547763 | /Users/kbsoo/Downloads/cl2/hitl/h111_global_boundary_assignment_solver_hsjepa/submission_h111_boundary_broad_null_c150_a048_7cbf5e9d.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 53 | True | 0.000000000 | 0.000000000 | -0.015317815 | 0.132167651 | 0.131396701 | 0.132167651 | -0.000680043 | 0.404987830 | 0.432487397 | 0.494625364 | 27 | 14 | 5 | 3 | 4.339622642 | 11.873326617 | 1.000000000 | 0.739950881 | /Users/kbsoo/Downloads/cl2/submission_h111_boundary_7cbf5e9d_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 53 | True |

Interpretation rule:

- If H111 improves over H110, the missing module is global assignment over the
  benefit/toxicity field, not another local toxicity score.
- If H110 improves more, the local toxicity-gap greedy boundary was already
  better than H108-rejected rescue.
- If H108 improves more, both H110 and H111 over-modeled toxicity.
- If H109 improves more, public-safe action is a tiny kernel rather than a
  boundary optimization problem.
