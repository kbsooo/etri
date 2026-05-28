# E73 Pure Q2/S3 Graft Probe

## Observe

`submission_e72_topabs50_q2s3_gate_4e48cba2.csv` worsened public LB, but it was not a pure Q2/S3 test because it moved every target family.

## Wonder

Is public rejecting the isolated Q2/S3 sparse movement, the broad non-Q2/S3 base movement, or a coupled interaction between them?

## Candidate Movement Audit

| name | active_cells | active_rows | active_targets | mean_abs_logit_move | mean_abs_q2s3_logit_move | q2_cells | s3_cells | q2_increases | q2_decreases | s3_increases | s3_decreases |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_base | 0 | 0 |  | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| e73_full_submitted | 893 | 249 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.00668422 | 0.00480356 | 40 | 39 | 20 | 20 | 20 | 19 |
| pure_q2s3_graft | 79 | 72 | Q2,S3 | 0.00137245 | 0.00480356 | 40 | 39 | 20 | 20 | 20 | 19 |
| pure_q2_only_graft | 40 | 40 | Q2 | 0.000618011 | 0.00216304 | 40 | 0 | 20 | 20 | 0 | 0 |
| pure_s3_only_graft | 39 | 39 | S3 | 0.000754435 | 0.00264052 | 0 | 39 | 0 | 0 | 20 | 19 |
| non_q2s3_only_graft | 814 | 249 | Q1,Q3,S1,S2,S4 | 0.00531178 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| inverse_q2s3_public_sensor | 79 | 72 | Q2,S3 | 0.00137245 | 0.00480356 | 40 | 39 | 20 | 20 | 19 | 20 |
| inverse_q2_only_public_sensor | 40 | 40 | Q2 | 0.000618011 | 0.00216304 | 40 | 0 | 20 | 20 | 0 | 0 |
| inverse_s3_only_public_sensor | 39 | 39 | S3 | 0.000754435 | 0.00264052 | 0 | 39 | 0 | 0 | 19 | 20 |

## Stress Summary

| name | movement_family | active_cells | active_rows | active_targets | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | hidden_q2_minus_base | hidden_s3_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | strict_gate | deployable_gate | loose_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e73_full_submitted | submitted_full | 893 | 249 | Q1,Q2,Q3,S1,S2,S3,S4 | -1.05458e-05 | -1.05458e-05 | 1.00163e-05 | 1 | 1 | -0.000391043 | -0.000487278 | -0.000294809 | -0.00180604 | -0.000931677 | 0.75 | 1 | 0.00668422 | 0.00480356 | False | False | True |
| pure_q2s3_graft | pure_graft | 79 | 72 | Q2,S3 | -5.95383e-06 | -5.95383e-06 | -1.61413e-06 | 3 | 3 | -0.000391043 | -0.000487278 | -0.000294809 | -0.000281016 | -0.000144038 | 0.75 | 1 | 0.00137245 | 0.00480356 | False | False | True |
| pure_s3_only_graft | pure_graft | 39 | 39 | S3 | -5.66531e-06 | -5.66531e-06 | -1.62156e-06 | 3 | 3 | -0.000147404 | 0 | -0.000294809 | -2.64085e-05 | 4.18484e-05 | 0.611111 | 0.944444 | 0.000754435 | 0.00264052 | False | False | True |
| non_q2s3_only_graft | pure_graft | 814 | 249 | Q1,Q3,S1,S2,S4 | -4.76553e-06 | -4.76553e-06 | 1.14476e-05 | 1 | 1 | 0 | 0 | 0 | -0.00152509 | -0.000772586 | 0 | 1 | 0.00531178 | 0 | False | False | False |
| pure_q2_only_graft | pure_graft | 40 | 40 | Q2 | -4.38789e-07 | -4.38789e-07 | -1.34306e-07 | 3 | 3 | -0.000243639 | -0.000487278 | 0 | -0.000235383 | -0.000123102 | 0.444444 | 0.972222 | 0.000618011 | 0.00216304 | False | False | False |
| inverse_q2_only_public_sensor | public_inverse_sensor | 40 | 40 | Q2 | 5.17297e-06 | 5.17297e-06 | 5.28568e-06 | 0 | 0 | 0.000257628 | 0.000515256 | 0 | 0.000257374 | 0.000193482 | 0.138889 | 0.583333 | 0.000618011 | 0.00216304 | False | False | False |
| inverse_s3_only_public_sensor | public_inverse_sensor | 39 | 39 | S3 | 9.46791e-06 | 9.46791e-06 | 1.65201e-05 | 0 | 0 | 0.000160738 | 0 | 0.000321475 | 5.10107e-05 | 3.97988e-05 | 0.194444 | 0.416667 | 0.000754435 | 0.00264052 | False | False | False |
| inverse_q2s3_public_sensor | public_inverse_sensor | 79 | 72 | Q2,S3 | 1.47473e-05 | 1.47473e-05 | 2.1439e-05 | 0 | 0 | 0.000418366 | 0.000515256 | 0.000321475 | 0.000311296 | 0.00023081 | 0.0833333 | 0.277778 | 0.00137245 | 0.00480356 | False | False | False |

## Pure Graft Rows

| pred_index | base_index | name | tag | base_tag | movement_family | active_cells | active_rows | active_targets | mean_abs_logit_move | mean_abs_q2s3_logit_move | all_delta_vs_mixmin | all_minus_base | all_worst_minus_base | set_inverse_top_delta_vs_mixmin | set_inverse_top_minus_base | set_inverse_top_worst_minus_base | set_raw05_compatible_delta_vs_mixmin | set_raw05_compatible_minus_base | set_raw05_compatible_worst_minus_base | set_all_sign_delta_vs_mixmin | set_all_sign_minus_base | set_all_sign_worst_minus_base | best_set_delta_vs_mixmin | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | row_id | world_support_minus_base | raw_energy_q_p90_minus_base | hidden_core_minus_base | hidden_q2_minus_base | hidden_s3_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_mean_minus_base | block_q2s3_max_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | nonanchor_evaluated | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | all_beats_base | all_margin_vs_mixmin | all_sets_beat_base | all_sets_tail_neutral | hidden_q2s3_beats_base | world_nonworse | block_majority_beats | block_tail_safe | strict_gate | loose_gate | deployable_gate | mean_abs_logit_delta_vs_e73 | mean_abs_q2s3_logit_delta_vs_e73 | mean_abs_logit_delta_vs_e74 | mean_abs_q2s3_logit_delta_vs_e74 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 0 | pure_q2s3_graft | e80_pure_q2s3_graft_69dd12a8 | e80_mixmin_base_0c916bb4 | pure_graft | 79 | 72 | Q2,S3 | 0.00137245 | 0.00480356 | -5.95383e-06 | -5.95383e-06 | -4.32816e-06 | -1.31423e-05 | -1.31423e-05 | -7.20886e-06 | -3.10502e-06 | -3.10502e-06 | -4.32816e-06 | -1.61413e-06 | -1.61413e-06 | -4.32816e-06 | -1.31423e-05 | -1.61413e-06 | 3 | 3 | 1 | -0.000281016 | -0.000144038 | -0.000111727 | -0.000487278 | -0.000294809 | -0.000391043 | -0.000469637 | 5.55112e-17 | 0.75 | 1 | True | 0.00137245 | 0.00480356 | True | False | True | True | True | True | True | True | False | True | False | 0.00531178 | 0 | 0.00565489 | 0.00120089 |
| 4 | 0 | pure_s3_only_graft | e80_pure_s3_only_graft_52c118e6 | e80_mixmin_base_0c916bb4 | pure_graft | 39 | 39 | S3 | 0.000754435 | 0.00264052 | -5.66531e-06 | -5.66531e-06 | -4.74972e-06 | -1.25142e-05 | -1.25142e-05 | -6.18088e-06 | -2.86014e-06 | -2.86014e-06 | -4.74972e-06 | -1.62156e-06 | -1.62156e-06 | -4.74972e-06 | -1.25142e-05 | -1.62156e-06 | 3 | 3 | 3 | -2.64085e-05 | 4.18484e-05 | -4.21155e-05 | 0 | -0.000294809 | -0.000147404 | -0.000255178 | 5.76041e-05 | 0.611111 | 0.944444 | True | 0.000754435 | 0.00264052 | True | False | True | True | True | True | True | True | False | True | False | 0.00592979 | 0.00216304 | 0.0062729 | 0.00336393 |
| 3 | 0 | pure_q2_only_graft | e80_pure_q2_only_graft_e6cc7477 | e80_mixmin_base_0c916bb4 | pure_graft | 40 | 40 | Q2 | 0.000618011 | 0.00216304 | -4.38789e-07 | -4.38789e-07 | -7.69542e-07 | -8.60931e-07 | -8.60931e-07 | -1.02798e-06 | -3.2113e-07 | -3.2113e-07 | -7.69542e-07 | -1.34306e-07 | -1.34306e-07 | -7.69542e-07 | -8.60931e-07 | -1.34306e-07 | 3 | 3 | 2 | -0.000235383 | -0.000123102 | -6.96111e-05 | -0.000487278 | 0 | -0.000243639 | -0.00021446 | 9.16703e-06 | 0.444444 | 0.972222 | True | 0.000618011 | 0.00216304 | True | False | True | True | True | True | False | True | False | False | False | 0.00606621 | 0.00264052 | 0.00640932 | 0.00384141 |

## Public-Inverse Sensor Rows

| pred_index | base_index | name | tag | base_tag | movement_family | active_cells | active_rows | active_targets | mean_abs_logit_move | mean_abs_q2s3_logit_move | all_delta_vs_mixmin | all_minus_base | all_worst_minus_base | set_inverse_top_delta_vs_mixmin | set_inverse_top_minus_base | set_inverse_top_worst_minus_base | set_raw05_compatible_delta_vs_mixmin | set_raw05_compatible_minus_base | set_raw05_compatible_worst_minus_base | set_all_sign_delta_vs_mixmin | set_all_sign_minus_base | set_all_sign_worst_minus_base | best_set_delta_vs_mixmin | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | row_id | world_support_minus_base | raw_energy_q_p90_minus_base | hidden_core_minus_base | hidden_q2_minus_base | hidden_s3_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_mean_minus_base | block_q2s3_max_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | nonanchor_evaluated | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | all_beats_base | all_margin_vs_mixmin | all_sets_beat_base | all_sets_tail_neutral | hidden_q2s3_beats_base | world_nonworse | block_majority_beats | block_tail_safe | strict_gate | loose_gate | deployable_gate | mean_abs_logit_delta_vs_e73 | mean_abs_q2s3_logit_delta_vs_e73 | mean_abs_logit_delta_vs_e74 | mean_abs_q2s3_logit_delta_vs_e74 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | 0 | inverse_q2_only_public_sensor | e80_inverse_q2_only_public_sensor_134a1bf7 | e80_mixmin_base_0c916bb4 | public_inverse_sensor | 40 | 40 | Q2 | 0.000618011 | 0.00216304 | 5.17297e-06 | 5.17297e-06 | 1.3816e-05 | 4.98698e-06 | 4.98698e-06 | 4.06529e-06 | 5.28568e-06 | 5.28568e-06 | 1.3816e-05 | 5.24626e-06 | 5.24626e-06 | 1.3816e-05 | 4.98698e-06 | 5.28568e-06 | 0 | 0 | 6 | 0.000257374 | 0.000193482 | 7.3608e-05 | 0.000515256 | 0 | 0.000257628 | 0.000226733 | 0.00183244 | 0.138889 | 0.583333 | True | 0.000618011 | 0.00216304 | False | False | False | False | False | False | False | False | False | False | False | 0.00730223 | 0.0069666 | 0.00764534 | 0.00816749 |
| 8 | 0 | inverse_s3_only_public_sensor | e80_inverse_s3_only_public_sensor_5bb2a8c3 | e80_mixmin_base_0c916bb4 | public_inverse_sensor | 39 | 39 | S3 | 0.000754435 | 0.00264052 | 9.46791e-06 | 9.46791e-06 | 8.30402e-06 | 1.65201e-05 | 1.65201e-05 | 8.39169e-06 | 6.94944e-06 | 6.94944e-06 | 8.30402e-06 | 4.93416e-06 | 4.93416e-06 | 8.30402e-06 | 4.93416e-06 | 1.65201e-05 | 0 | 0 | 7 | 5.10107e-05 | 3.97988e-05 | 4.5925e-05 | 0 | 0.000321475 | 0.000160738 | 0.000268304 | 0.00250946 | 0.194444 | 0.416667 | True | 0.000754435 | 0.00264052 | False | False | False | False | False | False | False | False | False | False | False | 0.00743866 | 0.00744408 | 0.00778177 | 0.00864497 |
| 6 | 0 | inverse_q2s3_public_sensor | e80_inverse_q2s3_public_sensor_bcbe3d2d | e80_mixmin_base_0c916bb4 | public_inverse_sensor | 79 | 72 | Q2,S3 | 0.00137245 | 0.00480356 | 1.47473e-05 | 1.47473e-05 | 2.212e-05 | 2.1439e-05 | 2.1439e-05 | 1.48322e-05 | 1.2242e-05 | 1.2242e-05 | 2.212e-05 | 1.05608e-05 | 1.05608e-05 | 2.212e-05 | 1.05608e-05 | 2.1439e-05 | 0 | 0 | 5 | 0.000311296 | 0.00023081 | 0.000119533 | 0.000515256 | 0.000321475 | 0.000418366 | 0.000495037 | 0.00250946 | 0.0833333 | 0.277778 | True | 0.00137245 | 0.00480356 | False | False | False | False | False | False | False | False | False | False | False | 0.00805667 | 0.00960712 | 0.00839978 | 0.010808 |

## Decision

- No pure Q2/S3 graft survived strict/deployable stress. The E73 public failure should pause E74/E75 direct follow-ups rather than trigger an immediate pure-graft submission.
- The inverse public-sensor rows do not survive local stress; do not turn one public miss into direct sign inversion.

## Outputs

- `analysis_outputs/e73_pure_q2s3_graft_probe_scan.csv`
- `analysis_outputs/e73_pure_q2s3_graft_probe_summary.csv`
