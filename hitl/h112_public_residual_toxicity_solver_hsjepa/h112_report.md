# H112 Public-Residual Toxicity Solver HS-JEPA

Question: after the H098 public equation explains known submissions, can the
leave-one-out residual be projected back to row-target actions as the actual
public/private toxicity field?

Residual sources:

| file | public_lb | delta_vs_h057 | loo_pred_delta | actual_minus_pred | residual_bad | residual_good | frontier_weight |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.578171818 | 0.010424224 | 0.008973766 | 0.001450458 | 0.001450458 | 0.000000000 | 0.077680359 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.012499225 | 0.011149510 | 0.001349715 | 0.001349715 | 0.000000000 | 0.077145609 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.009538915 | 0.008564706 | 0.000974209 | 0.000974209 | 0.000000000 | 0.078389773 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.010679759 | 0.011610357 | -0.000930598 | 0.000000000 | 0.000930598 | 0.077555670 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.010555771 | 0.010147771 | 0.000408000 | 0.000408000 | 0.000000000 | 0.077612861 |
| submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.009287908 | 0.008946557 | 0.000341351 | 0.000341351 | 0.000000000 | 0.078706074 |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.012053692 | 0.012345422 | -0.000291729 | 0.000000000 | 0.000291729 | 0.077197468 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.008411356 | 0.008659837 | -0.000248482 | 0.000000000 | 0.000248482 | 0.080509308 |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.013479734 | 0.013291664 | 0.000188070 | 0.000188070 | 0.000000000 | 0.077081212 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.567904825 | 0.000157231 | 0.000343423 | -0.000186192 | 0.000000000 | 0.000186192 | 4.379922090 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.009778713 | 0.009944311 | -0.000165598 | 0.000000000 | 0.000165598 | 0.078143522 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.008532974 | 0.008679010 | -0.000146036 | 0.000000000 | 0.000146036 | 0.080173991 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.010197382 | 0.010055198 | 0.000142184 | 0.000142184 | 0.000000000 | 0.077815634 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.008581903 | 0.008705502 | -0.000123598 | 0.000000000 | 0.000123598 | 0.080048384 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.008559047 | 0.008678317 | -0.000119270 | 0.000000000 | 0.000119270 | 0.080106422 |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.008564237 | 0.008677004 | -0.000112767 | 0.000000000 | 0.000112767 | 0.080093145 |
| submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.576290429 | 0.008542835 | 0.008648781 | -0.000105945 | 0.000000000 | 0.000105945 | 0.080148262 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.008660183 | 0.008762817 | -0.000102634 | 0.000000000 | 0.000102634 | 0.079857786 |

Pool audit:

| group | cells | mean_residual_toxicity | mean_residual_safety | mean_residual_gap | mean_assignment_score |
| --- | --- | --- | --- | --- | --- |
| all_pool | 1750 | 0.497214640 | 0.402760438 | -0.094454202 | -0.109289254 |
| h111_selected | 53 | 0.550647057 | 0.684321958 | 0.133674901 | 0.250771337 |
| h110_selected | 37 | 0.573417413 | 0.675411098 | 0.101993685 | 0.211185600 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | model_pred_delta_vs_h057 | route_basis_pred_delta_vs_h057 | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | selected_mean_residual_toxicity | selected_mean_residual_safety | selected_mean_residual_gap | selected_mean_antidote_score | selected_h111_cells | selected_h108_rejected_cells | h112_information_mass | h112_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h112_residual_h111_pruned_boundary_c86_a056_68b26f11 | residual_h111_pruned_boundary_c86_a056 | 40 | 23 | 4 | 0 | 14 | 7 | 4 | 4 | 7 | -0.000018318 | -0.000980341 | 0.000000000 | -0.011877601 | 0.118414291 | 0.489754207 | 0.681666540 | 0.191912333 | 0.728513857 | 37 | 14 | 0.970000000 | 0.542405283 | submission_h112_residual_h111_pruned_boundary_c86_a056_68b26f11.csv |
| h112_residual_h010_e216_antidote_c72_a064_07801191 | residual_h010_e216_antidote_c72_a064 | 32 | 21 | 3 | 0 | 13 | 5 | 2 | 4 | 5 | -0.000025398 | -0.001025252 | 0.000000000 | -0.012522537 | 0.077181639 | 0.486138384 | 0.688497273 | 0.202358889 | 0.744687679 | 30 | 10 | 0.870000000 | 0.534936862 | submission_h112_residual_h010_e216_antidote_c72_a064_07801191.csv |
| h112_residual_broad_safety_c140_a044_031aa2cc | residual_broad_safety_c140_a044 | 52 | 29 | 5 | 0 | 16 | 9 | 9 | 4 | 9 | -0.000018474 | -0.000732862 | 0.000000000 | -0.011589929 | 0.123797070 | 0.525442687 | 0.676943068 | 0.151500381 | 0.647572143 | 44 | 17 | 1.000000000 | 0.498042821 | submission_h112_residual_broad_safety_c140_a044_031aa2cc.csv |
| h112_residual_antitoxic_kernel_c52_a078_63b4b19e | residual_antitoxic_kernel_c52_a078 | 13 | 10 | 2 | 0 | 3 | 1 | 1 | 4 | 2 | -0.000005990 | -0.000492182 | 0.000000000 | -0.014377947 | 0.044272578 | 0.468825099 | 0.726116702 | 0.257291603 | 0.814036484 | 12 | 0 | 0.380000000 | 0.410709628 | submission_h112_residual_antitoxic_kernel_c52_a078_63b4b19e.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | known_public_observations | residual_fit_feature_set | residual_fit_alpha | largest_bad_residual_file | largest_bad_residual | largest_good_residual_file | largest_good_residual | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | route_basis_pred_delta_vs_h057 | selected_mean_residual_toxicity | selected_mean_residual_safety | selected_mean_residual_gap | selected_mean_antidote_score | selected_same_bad_residual | selected_opp_bad_residual | selected_same_good_residual | selected_opp_good_residual | selected_h111_cells | selected_h108_rejected_cells | selected_h109_cells | selected_mean_family_count | h112_information_mass | h112_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h112_public_residual_toxicity_solver | h112_residual_h111_pruned_boundary_c86_a056_68b26f11 | /Users/kbsoo/Downloads/cl2/submission_h112_residualtox_68b26f11_uploadsafe.csv | H111 was directionally right but needs pruning by leave-one-out public residual toxicity before becoming action-grade | 24 | state_core | 0.100000000 | submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.001450458 | submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.000930598 | h112_residual_h111_pruned_boundary_c86_a056_68b26f11 | residual_h111_pruned_boundary_c86_a056 | public_residual_toxicity_solver | h111_pruned | state_core | 0.100000000 | 86 | 0.560000000 | 0.230000000 | 40 | 40 | 23 | -0.000018318 | 0.000009151 | 0.000016725 | 0.850000000 | 0.975000000 | 0.508007857 | 0.875000000 | 0.063176520 | 0.722150000 | -0.044269849 | 0.290408946 | 0.260364091 | 0.000000000 | 0.000200134 | 0.032959256 | 9 | 0,3,10,56,61,70,78,93,98,101,110,135,136,139,144,146,148,149,150,151,164,196,216 | 0.373552929 | submission_h112_residual_h111_pruned_boundary_c86_a056_68b26f11.csv | /Users/kbsoo/Downloads/cl2/hitl/h112_public_residual_toxicity_solver_hsjepa/submission_h112_residual_h111_pruned_boundary_c86_a056_68b26f11.csv | 4 | 0 | 14 | 7 | 4 | 4 | 7 | -0.102107359 | -0.102999553 | -0.110205569 | -0.084739460 | -0.107210114 | -0.120488581 | -0.101854051 | /Users/kbsoo/Downloads/cl2/hitl/h112_public_residual_toxicity_solver_hsjepa/submission_h112_residual_h111_pruned_boundary_c86_a056_68b26f11.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 40 | True | 0.000000000 | 0.000000000 | -0.011877601 | 0.118414291 | 0.117797303 | 0.118414291 | -0.000980341 | 0.489754207 | 0.681666540 | 0.191912333 | 0.728513857 | 0.022945803 | 0.677220076 | 0.028269556 | 0.690507837 | 37 | 14 | 3 | 4.325000000 | 0.970000000 | 0.542405283 | /Users/kbsoo/Downloads/cl2/submission_h112_residualtox_68b26f11_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 40 | True |

Interpretation rule:

- If H112 improves over H111/H110, the missing HS-JEPA decoder is not another
  context encoder or local toxicity score. It is a public-residual toxicity
  assignment equation.
- If H111 improves more, residual projection over-pruned or inverted useful
  globally safe cells.
- If H110 improves more, H098 residuals are too underidentified and local
  benefit-toxicity remains the cleaner action-grade field.
- If H109 improves more, public-safe action is still a tiny coefficient kernel.
