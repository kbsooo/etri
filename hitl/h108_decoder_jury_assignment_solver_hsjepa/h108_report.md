# H108 Decoder-Jury Assignment Solver HS-JEPA

Question: is the action-grade row-target field the intersection of independent
HS-JEPA decoders rather than any single decoder family?

Source candidates:

| family | candidate_id | weight | score_rank | route_basis_pred_delta_vs_h057 | model_pred_delta_vs_h057 |
| --- | --- | --- | --- | --- | --- |
| h103 | h103_dense_nullplus_conflict_c132_r45_amp100_89496ed5 | 1.651860000 | 1.000000000 | -0.002437589 | -0.000063254 |
| h103 | h103_balanced_shadow_portfolio_c180_r62_amp090_e85cab26 | 1.461096504 | 0.800000000 | -0.002173610 | -0.000067556 |
| h103 | h103_qsubjective_gain_cancel_c90_r30_amp085_181367a1 | 1.287972000 | 0.600000000 | -0.001619338 | -0.000070178 |
| h103 | h103_objective_shadow_bridge_c150_r55_amp080_1815e908 | 1.106028000 | 0.400000000 | -0.001600737 | -0.000100108 |
| h103 | h103_id06_block_shadow_cancel_c96_r20_amp110_db0fed69 | 0.924084000 | 0.200000000 | -0.001600801 | -0.000043057 |
| h104 | h104_broad_route_resid_c160_a085_52f826e6 | 1.529402112 | 1.000000000 | -0.001758283 | -0.000085942 |
| h104 | h104_objective_resid_q2zero_c120_a095_5ee42853 | 1.117200000 | 0.500000000 | -0.000689315 | -0.000237998 |
| h105 | h105_discrete_plus_only_c90_s30_8f0e502e | 1.761984000 | 1.000000000 | -0.002727077 | -0.000018480 |
| h105 | h105_signed_null_lagrange_c120_s42_74a05a1d | 1.519392000 | 0.750000000 | -0.002716992 | -0.000018375 |
| h105 | h105_objective_coeff_q2zero_c150_s52_127f76c9 | 1.276800000 | 0.500000000 | -0.002325639 | -0.000060165 |
| h105 | h105_broad_coeff_transport_c180_s58_7971b5d7 | 1.032139584 | 0.250000000 | -0.002160681 | -0.000069436 |
| h106 | h106_broad_conflict_consensus_c96_a065_f315d99a | 1.573200000 | 1.000000000 | -0.000795951 | -0.000039827 |
| h106 | h106_objective_consensus_q2zero_c88_a070_9be1339a | 1.356600000 | 0.750000000 | -0.000888380 | -0.000039512 |
| h106 | h106_kernel_seed_expand_c44_a090_64df3d49 | 1.140000000 | 0.500000000 | -0.001055926 | -0.000014881 |
| h106 | h106_strict_conflict_core_c24_a100_f6acb108 | 0.919706400 | 0.250000000 | -0.001095705 | -0.000017737 |
| h107 | h107_strict_antitoxic_core_c44_a045_a0ea1eec | 1.281744000 | 1.000000000 | -0.000078536 | 0.000003505 |
| h107 | h107_kernel_antipode_transfer_c64_a050_d46c942f | 1.105272000 | 0.750000000 | -0.000114640 | 0.000003660 |
| h107 | h107_broad_antipode_shadow_c140_a030_8dfc1f63 | 0.911600000 | 0.500000000 | 0.000067359 | -0.000002467 |
| h107 | h107_objective_antipode_c96_a042_a91647e7 | 0.696600000 | 0.250000000 | 0.000022589 | 0.000002569 |

Candidates:

| candidate_id | spec_name | selected_cells | changed_rows_vs_h057 | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | model_pred_delta_vs_h057 | route_basis_pred_delta_vs_h057 | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_bad_margin | anti_h088_direction_rate | h057_positive_align_rate | selected_mean_family_count | selected_mean_family_consensus | selected_mean_vote_weight | h108_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h108_strict_intersection_c48_a085_610a26a0 | strict_intersection_c48_a085 | 47 | 27 | 5 | 0 | 14 | 10 | 7 | 2 | 9 | -0.000050438 | -0.001528316 | 0.000000000 | -0.009025173 | 0.107886104 | 0.914893617 | 0.914893617 | 3.851063830 | 1.000000000 | 11.552750148 | 0.927303690 | submission_h108_strict_intersection_c48_a085_610a26a0.csv |
| h108_kernel_jury_transfer_c64_a080_082a4d88 | kernel_jury_transfer_c64_a080 | 58 | 28 | 7 | 0 | 18 | 11 | 9 | 4 | 9 | -0.000052252 | -0.001419850 | 0.000000000 | -0.003760328 | 0.119161071 | 0.879310345 | 0.913793103 | 3.551724138 | 1.000000000 | 10.617274438 | 0.893920930 | submission_h108_kernel_jury_transfer_c64_a080_082a4d88.csv |
| h108_portfolio_residual_core_c82_a070_fd9c4d12 | portfolio_residual_core_c82_a070 | 36 | 30 | 4 | 2 | 11 | 6 | 6 | 1 | 6 | -0.000053691 | -0.001355660 | 0.000000000 | -0.022949978 | 0.076752121 | 0.916666667 | 0.777777778 | 3.833333333 | 1.000000000 | 11.632906775 | 0.866772234 | submission_h108_portfolio_residual_core_c82_a070_fd9c4d12.csv |
| h108_objective_decoder_jury_c110_a060_603c278e | objective_decoder_jury_c110_a060 | 55 | 31 | 0 | 0 | 18 | 12 | 11 | 4 | 10 | -0.000030211 | -0.000588264 | 0.000000000 | -0.006860504 | 0.135846062 | 0.854545455 | 0.872727273 | 3.363636364 | 1.000000000 | 9.984220264 | 0.771420257 | submission_h108_objective_decoder_jury_c110_a060_603c278e.csv |

Decision:

| decision | selected_candidate_id | root_uploadsafe_path | worldview | source_candidates | source_families | h098_feature_set | h098_alpha | candidate_id | spec_name | mode | target_group | fit_feature_set | fit_alpha | k | alpha | cap | selected_cells | changed_cells_vs_h057 | changed_rows_vs_h057 | model_pred_delta_vs_h057 | posterior_delta_vs_h057 | hard_diag_delta_vs_h057 | anti_h088_direction_rate | h057_positive_align_rate | selected_toxic_mean | selected_conflict_rate | selected_safe_cell_mean | mean_bad_same_rank | cos_h088_direction | cos_h057_vs_h042_direction | cos_h057_vs_h050_direction | max_positive_bad_cosine | mean_abs_prob_move_vs_h057 | max_abs_prob_move_vs_h057 | selected_subjects | selected_rows | h097_score | file | resolved_path | Q1_changed_vs_h057 | Q2_changed_vs_h057 | Q3_changed_vs_h057 | S1_changed_vs_h057 | S2_changed_vs_h057 | S3_changed_vs_h057 | S4_changed_vs_h057 | bad_cos_submission_h010_objectiv | bad_cos_submission_e216_maskfam | bad_cos_submission_e323_5508f966 | bad_cos_submission_jepa_latent_q | bad_cos_submission_jepa_latent_r | bad_cos_submission_lejepa_target | bad_cos_submission_ordinal_q_con | path | rows | keys_match | duplicate_keys | nan_cells | min_prob | max_prob | changed_cells_vs_h057_validation | upload_safe | h102_cum_bad_max_pos | h102_cum_bad_weighted_pos | h102_cum_h088_axis_cos | h102_cum_good_max_cos | h102_cum_good_mean_cos | h102_cum_good_bad_margin | route_basis_pred_delta_vs_h057 | selected_mean_family_count | selected_mean_family_consensus | selected_mean_vote_weight | selected_mean_jury_score | selected_h103_cells | selected_h104_cells | selected_h105_cells | selected_h106_cells | selected_h107_cells | h108_score | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote_h108_decoder_jury_assignment_solver | h108_strict_intersection_c48_a085_610a26a0 | /Users/kbsoo/Downloads/cl2/submission_h108_jury_610a26a0_uploadsafe.csv | only non-Q2 cells supported by at least three independent decoder families are action-grade | 19 | h103,h104,h105,h106,h107 | state_core | 0.100000000 | h108_strict_intersection_c48_a085_610a26a0 | strict_intersection_c48_a085 | decoder_jury_assignment_solver | strict_intersection | state_core | 0.100000000 | 48 | 0.850000000 | 0.300000000 | 47 | 47 | 27 | -0.000050438 | 0.000024731 | 0.000039182 | 0.914893617 | 0.914893617 | 0.603999392 | 0.872340426 | 0.081792306 | 0.609708207 | -0.063985353 | 0.256474711 | 0.239706048 | 0.000000000 | 0.000359840 | 0.049670107 | 10 | 0,3,10,35,56,61,70,78,93,98,101,110,131,135,136,139,144,146,149,151,164,196,216,226,234,235,238 | 0.377608473 | submission_h108_strict_intersection_c48_a085_610a26a0.csv | /Users/kbsoo/Downloads/cl2/hitl/h108_decoder_jury_assignment_solver_hsjepa/submission_h108_strict_intersection_c48_a085_610a26a0.csv | 5 | 0 | 14 | 10 | 7 | 2 | 9 | -0.065093768 | -0.062636126 | -0.070031993 | -0.053850811 | -0.077109951 | -0.064232996 | -0.072731585 | /Users/kbsoo/Downloads/cl2/hitl/h108_decoder_jury_assignment_solver_hsjepa/submission_h108_strict_intersection_c48_a085_610a26a0.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 47 | True | 0.000000000 | 0.000000000 | -0.009025173 | 0.107886104 | 0.107229892 | 0.107886104 | -0.001528316 | 3.851063830 | 1.000000000 | 11.552750148 | 0.851907024 | 42 | 38 | 15 | 46 | 40 | 0.927303690 | /Users/kbsoo/Downloads/cl2/submission_h108_jury_610a26a0_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 47 | True |

Interpretation rule:

- If H108 improves over the individual H103-H107 branches, decoder-family
  consensus is closer to the hidden public/private assignment law than any
  single decoder.
- If H108 loses while one branch wins, the action equation is branch-specific
  and consensus averaging destroys useful structure.
- If all H103-H108 lose, the current solver basis is diagnostic only and the
  next breakthrough must identify a new public subset sensor.
