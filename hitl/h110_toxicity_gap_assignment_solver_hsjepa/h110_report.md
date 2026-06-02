# H110 Toxicity-Gap Assignment Solver HS-JEPA

Question: can HS-JEPA separate row-target benefit from public-action toxicity
before assigning cells?

Source candidates:

| family | candidate_id | h109_source_weight | route_basis_pred_delta_vs_h057 | model_pred_delta_vs_h057 |
| --- | --- | --- | --- | --- |
| h103 | h103_dense_nullplus_conflict_c132_r45_amp100_89496ed5 | 1.651860000 | -0.002437589 | -0.000063254 |
| h103 | h103_balanced_shadow_portfolio_c180_r62_amp090_e85cab26 | 1.461096504 | -0.002173610 | -0.000067556 |
| h103 | h103_qsubjective_gain_cancel_c90_r30_amp085_181367a1 | 1.287972000 | -0.001619338 | -0.000070178 |
| h103 | h103_objective_shadow_bridge_c150_r55_amp080_1815e908 | 1.106028000 | -0.001600737 | -0.000100108 |
| h103 | h103_id06_block_shadow_cancel_c96_r20_amp110_db0fed69 | 0.924084000 | -0.001600801 | -0.000043057 |
| h104 | h104_broad_route_resid_c160_a085_52f826e6 | 1.529402112 | -0.001758283 | -0.000085942 |
| h104 | h104_objective_resid_q2zero_c120_a095_5ee42853 | 1.117200000 | -0.000689315 | -0.000237998 |
| h105 | h105_discrete_plus_only_c90_s30_8f0e502e | 1.761984000 | -0.002727077 | -0.000018480 |
| h105 | h105_signed_null_lagrange_c120_s42_74a05a1d | 1.519392000 | -0.002716992 | -0.000018375 |
| h105 | h105_objective_coeff_q2zero_c150_s52_127f76c9 | 1.276800000 | -0.002325639 | -0.000060165 |
| h105 | h105_broad_coeff_transport_c180_s58_7971b5d7 | 1.032139584 | -0.002160681 | -0.000069436 |
| h106 | h106_broad_conflict_consensus_c96_a065_f315d99a | 1.573200000 | -0.000795951 | -0.000039827 |
| h106 | h106_objective_consensus_q2zero_c88_a070_9be1339a | 1.356600000 | -0.000888380 | -0.000039512 |
| h106 | h106_kernel_seed_expand_c44_a090_64df3d49 | 1.140000000 | -0.001055926 | -0.000014881 |
| h106 | h106_strict_conflict_core_c24_a100_f6acb108 | 0.919706400 | -0.001095705 | -0.000017737 |
| h107 | h107_strict_antitoxic_core_c44_a045_a0ea1eec | 1.281744000 | -0.000078536 | 0.000003505 |
| h107 | h107_kernel_antipode_transfer_c64_a050_d46c942f | 1.105272000 | -0.000114640 | 0.000003660 |
| h107 | h107_broad_antipode_shadow_c140_a030_8dfc1f63 | 0.911600000 | 0.000067359 | -0.000002467 |
| h107 | h107_objective_antipode_c96_a042_a91647e7 | 0.696600000 | 0.000022589 | 0.000002569 |
| h108 | h108_strict_intersection_c48_a085_610a26a0 | 1.720000000 | -0.001528316 | -0.000050438 |
| h109 | h109_kernel_coeff_focus_c48_t7_54147083 | 1.380000000 | -0.001861699 | 0.000015065 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | model_pred_delta_vs_h057 | route_basis_pred_delta_vs_h057 | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | selected_mean_benefit | selected_mean_toxicity | selected_mean_gap | selected_mean_family_count | selected_h109_cells | h110_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h110_toxgap_kernel_release_c64_a085_7b02f196 | toxgap_kernel_release_c64_a085 | 37 | 23 | 5 | 0 | 14 | 4 | 6 | 4 | 4 | -0.000036672 | -0.001036947 | 0.000000000 | -0.008961007 | 0.066098302 | 0.918943395 | 0.517837626 | 0.401105769 | 4.324324324 | 1 | 0.804067054 | submission_h110_toxgap_kernel_release_c64_a085_7b02f196.csv |
| h110_toxgap_jury_bridge_c82_a070_62f2fdb1 | toxgap_jury_bridge_c82_a070 | 23 | 18 | 4 | 0 | 9 | 2 | 4 | 1 | 3 | -0.000001601 | -0.000871638 | 0.000000000 | -0.018745390 | 0.033012517 | 0.922046887 | 0.499758272 | 0.422288615 | 4.695652174 | 1 | 0.790536637 | submission_h110_toxgap_jury_bridge_c82_a070_62f2fdb1.csv |
| h110_toxgap_broad_null_c140_a052_8af9ba8a | toxgap_broad_null_c140_a052 | 66 | 34 | 7 | 2 | 19 | 12 | 12 | 4 | 10 | -0.000035942 | -0.000912432 | 0.000000000 | -0.004311878 | 0.141552486 | 0.909410055 | 0.493127861 | 0.416282194 | 4.136363636 | 4 | 0.771357790 | submission_h110_toxgap_broad_null_c140_a052_8af9ba8a.csv |
| h110_toxgap_objective_field_c120_a060_c96c5208 | toxgap_objective_field_c120_a060 | 56 | 32 | 0 | 0 | 19 | 12 | 11 | 4 | 10 | -0.000028984 | -0.000612081 | 0.000000000 | -0.006853665 | 0.134783081 | 0.913406239 | 0.487759043 | 0.425647196 | 4.178571429 | 3 | 0.746516779 | submission_h110_toxgap_objective_field_c120_a060_c96c5208.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | source_candidates | source_families | h098_feature_set | h098_alpha | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | route_basis_pred_delta_vs_h057 | selected_mean_benefit | selected_mean_toxicity | selected_mean_gap | selected_mean_local_bad | selected_mean_local_good | selected_mean_family_count | selected_mean_family_consensus | selected_mean_vote_weight | selected_h109_cells | h110_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h110_toxicity_gap_assignment_solver | h110_toxgap_kernel_release_c64_a085_7b02f196 | /Users/kbsoo/Downloads/cl2/submission_h110_toxgap_7b02f196_uploadsafe.csv | H109 over-sharpened the H105 kernel; release nearby low-toxicity kernel cells instead of pure coefficient collapse | 21 | h103,h104,h105,h106,h107,h108,h109 | state_core | 0.100000000 | h110_toxgap_kernel_release_c64_a085_7b02f196 | toxgap_kernel_release_c64_a085 | toxicity_gap_assignment_solver | kernel_release | state_core | 0.100000000 | 64 | 0.850000000 | 0.310000000 | 37 | 37 | 23 | -0.000036672 | 0.000016556 | 0.000026890 | 0.918918919 | 0.864864865 | 0.636958301 | 0.837837838 | 0.064336250 | 0.591606178 | -0.058389606 | 0.203862414 | 0.196468324 | 0.000000000 | 0.000245333 | 0.050183630 | 10 | 10,35,56,61,70,78,98,110,131,135,136,139,143,144,146,149,151,164,196,216,234,235,238 | 0.350546620 | submission_h110_toxgap_kernel_release_c64_a085_7b02f196.csv | /Users/kbsoo/Downloads/cl2/hitl/h110_toxicity_gap_assignment_solver_hsjepa/submission_h110_toxgap_kernel_release_c64_a085_7b02f196.csv | 5 | 0 | 14 | 4 | 6 | 4 | 4 | -0.041711053 | -0.036584494 | -0.034808704 | -0.030458937 | -0.050065565 | -0.036594171 | -0.052798403 | /Users/kbsoo/Downloads/cl2/hitl/h110_toxicity_gap_assignment_solver_hsjepa/submission_h110_toxgap_kernel_release_c64_a085_7b02f196.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 37 | True | 0.000000000 | 0.000000000 | -0.008961007 | 0.066098302 | 0.065148077 | 0.066098302 | -0.001036947 | 0.918943395 | 0.517837626 | 0.401105769 | 0.001544867 | 0.012074427 | 4.324324324 | 1.000000000 | 11.766620471 | 1 | 0.804067054 | /Users/kbsoo/Downloads/cl2/submission_h110_toxgap_7b02f196_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 37 | True |

Interpretation rule:

- If H110 improves over H108, the missing action decoder is benefit-toxicity
  factorization, not raw decoder-family intersection.
- If H108 improves more, local toxicity scoring over-pruned useful cells.
- If H109 improves more, the true public-safe action remains a tiny kernel.
- If all H108-H110 lose, H103-H109 decoder witnesses are diagnostic only and a
  new public subset sensor is required.
