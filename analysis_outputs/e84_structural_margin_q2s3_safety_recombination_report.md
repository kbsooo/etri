# E84 Structural Margin + Q2/S3 Safety Recombination

## Observe

E83 produced margin in non-Q2S3 structural movements and Q2/S3 safety in E72-derived movements, but no single row carried both.

## Wonder

Can the two movements be combined without reintroducing the E73 all-target public failure?

## Method

- Select E83 structural-loose `non_q2s3` rows with margin-scale combo deltas and nonworse world/raw-energy stress.
- Select E83 E72-derived loose Q2/S3-safe rows.
- Add structural deltas outside Q2/S3 and only Q2/S3 deltas from the safety rows.
- Sweep conservative structural and Q2/S3 weights, then run the same combo and nonanchor stress.

## Selected Structural Pool

| source_file | row_gate | scale | all_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_core_minus_base | world_support_minus_base | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | all_rows | 0.25 | -2.5291e-05 | 2 | 2 | -0.000182128 | -3.31539e-05 | e83_all_rows_non_q2s3_0.25_903f64a6 |
| submission_jepa_block_consensus_gate_299a7455.csv | all_rows | 0.25 | -2.52257e-05 | 2 | 2 | -0.000160738 | -5.29831e-06 | e83_all_rows_non_q2s3_0.25_c41df1a9 |
| submission_jepa_block_consensus_gate_5738e95e.csv | all_rows | 0.25 | -2.52233e-05 | 2 | 2 | -0.000160762 | -5.17967e-06 | e83_all_rows_non_q2s3_0.25_dcb21c92 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | all_rows | 0.25 | -2.52154e-05 | 2 | 2 | -0.000160781 | -5.39093e-06 | e83_all_rows_non_q2s3_0.25_431a8264 |
| submission_jepa_block_consensus_gate_aa97b049.csv | all_rows | 0.25 | -2.52146e-05 | 2 | 2 | -0.00016069 | -5.44066e-06 | e83_all_rows_non_q2s3_0.25_3432ad1b |
| submission_jepa_block_consensus_gate_c28e6346.csv | all_rows | 0.25 | -2.51996e-05 | 2 | 2 | -0.000160717 | -5.62976e-06 | e83_all_rows_non_q2s3_0.25_a31f8863 |
| submission_jepa_block_consensus_gate_76aff53b.csv | all_rows | 0.25 | -2.51991e-05 | 2 | 2 | -0.000160637 | -5.54978e-06 | e83_all_rows_non_q2s3_0.25_af9c7fa8 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | all_rows | 0.25 | -2.51921e-05 | 2 | 2 | -0.000193465 | -5.11412e-05 | e83_all_rows_non_q2s3_0.25_64795ff4 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | all_rows | 0.25 | -2.51908e-05 | 2 | 2 | -0.000192724 | -5.02472e-05 | e83_all_rows_non_q2s3_0.25_330b86b7 |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | all_rows | 0.25 | -2.51895e-05 | 2 | 2 | -0.000191983 | -4.93525e-05 | e83_all_rows_non_q2s3_0.25_6eadf884 |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | all_rows | 0.25 | -2.51882e-05 | 2 | 2 | -0.000191242 | -4.84569e-05 | e83_all_rows_non_q2s3_0.25_0a3088ce |
| submission_jepa_block_consensus_rawcorr_micro_c8d38ede.csv | all_rows | 0.25 | -2.51669e-05 | 2 | 2 | -0.000196173 | -5.3978e-05 | e83_all_rows_non_q2s3_0.25_1c88c602 |
| submission_jepa_block_consensus_rawcorr_micro_d2dbf75c.csv | all_rows | 0.25 | -2.51666e-05 | 2 | 2 | -0.000196385 | -5.42666e-05 | e83_all_rows_non_q2s3_0.25_cf3a5068 |
| submission_jepa_block_consensus_rawcorr_micro_d7f8c65c.csv | all_rows | 0.25 | -2.51664e-05 | 2 | 2 | -0.000196597 | -5.45552e-05 | e83_all_rows_non_q2s3_0.25_d0bd5493 |
| submission_jepa_block_consensus_rawcorr_micro_d9851c05.csv | all_rows | 0.25 | -2.51661e-05 | 2 | 2 | -0.000196809 | -5.48437e-05 | e83_all_rows_non_q2s3_0.25_c6fa6c1a |
| submission_jepa_block_consensus_rawcorr_micro_cc5b3053.csv | all_rows | 0.25 | -2.51659e-05 | 2 | 2 | -0.000197022 | -5.51323e-05 | e83_all_rows_non_q2s3_0.25_52df21f9 |
| submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv | all_rows | 0.25 | -2.51656e-05 | 2 | 2 | -0.000197234 | -5.54208e-05 | e83_all_rows_non_q2s3_0.25_50eed85a |
| submission_jepa_block_consensus_rawcorr_refine_a4c875f3.csv | all_rows | 0.25 | -2.51306e-05 | 2 | 2 | -0.000193775 | -4.5701e-05 | e83_all_rows_non_q2s3_0.25_988620fb |

## Selected Q2/S3 Safety Pool

| row_gate | target_scope | scale | all_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e82_energy_top100 | all | 0.75 | -8.93545e-06 | 3 | 3 | -0.000295857 | -0.000673957 | e83_e82_energy_top100_all_0.75_fc354223 |
| e82_energy_top50 | all | 1 | -7.80901e-06 | 3 | 3 | -0.000278336 | -0.000529247 | e83_e82_energy_top50_all_1.00_52b8f72c |
| e82_energy_top50 | s_all | 1 | -7.02651e-06 | 3 | 3 | -0.000147404 | -0.0002258 | e83_e82_energy_top50_s_all_1.00_00b01914 |
| e82_energy_top100 | all | 0.5 | -6.86132e-06 | 3 | 3 | -0.000198952 | -0.000450417 | e83_e82_energy_top100_all_0.50_62a7e1ec |
| e82_energy_top100 | s_all | 0.75 | -6.85775e-06 | 3 | 3 | -0.000111811 | -0.000297976 | e83_e82_energy_top100_s_all_0.75_4bcdf406 |
| e82_energy_top50 | all | 0.75 | -6.71498e-06 | 3 | 3 | -0.000210655 | -0.000397991 | e83_e82_energy_top50_all_0.75_3d859632 |
| all_rows | q2s3 | 1 | -5.95383e-06 | 3 | 3 | -0.000391043 | -0.000281016 | e83_all_rows_q2s3_1.00_69dd12a8 |
| e82_energy_top50 | s_all | 0.75 | -5.78414e-06 | 3 | 3 | -0.000111811 | -0.000170012 | e83_e82_energy_top50_s_all_0.75_43e8ea12 |
| e82_energy_top50 | q2s3 | 1 | -5.68377e-06 | 3 | 3 | -0.000278336 | -0.000170679 | e83_e82_energy_top50_q2s3_1.00_5240c5db |
| e82_energy_top50 | q3_s2_s3_s4 | 1 | -5.68119e-06 | 3 | 3 | -0.000147404 | -0.00021636 | e83_e82_energy_top50_q3_s2_s3_s4_1.00_36cabdcb |
| all_rows | q2s3 | 0.75 | -5.29554e-06 | 3 | 3 | -0.000295857 | -0.000211755 | e83_all_rows_q2s3_0.75_a12c348b |
| e82_energy_top100 | s_all | 0.5 | -5.05843e-06 | 3 | 3 | -7.53782e-05 | -0.000199222 | e83_e82_energy_top100_s_all_0.50_650ca5b6 |

## Summary

| struct_weight | q_weight | q_target_scope | rows | nonanchor_evaluated | strict | deployable | loose | structural_strict | structural_loose | best_all_delta_vs_mixmin | best_eval_all_delta_vs_mixmin | best_hidden_q2s3 | best_world |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1.5 | all | 72 | 72 | 0 | 0 | 72 | 0 | 72 | -3.14482e-05 | -3.14482e-05 | -0.00043799 | -0.000366031 |
| 1 | 1.25 | all | 72 | 72 | 0 | 0 | 72 | 0 | 72 | -3.12586e-05 | -3.12586e-05 | -0.000367408 | -0.000314763 |
| 1 | 1 | all | 72 | 72 | 0 | 0 | 72 | 0 | 72 | -3.08563e-05 | -3.08563e-05 | -0.000295857 | -0.000264112 |
| 1 | 0.75 | all | 72 | 72 | 0 | 0 | 72 | 0 | 72 | -3.00701e-05 | -3.00701e-05 | -0.000223339 | -0.00021045 |
| 1 | 1.5 | s_all | 54 | 54 | 0 | 0 | 54 | 0 | 54 | -3.215e-05 | -3.215e-05 | -0.00021606 | -9.45917e-05 |
| 1 | 1.25 | s_all | 54 | 54 | 0 | 0 | 54 | 0 | 54 | -3.16286e-05 | -3.16286e-05 | -0.000182155 | -8.95091e-05 |
| 1 | 1 | s_all | 54 | 54 | 0 | 0 | 54 | 0 | 54 | -3.08399e-05 | -3.08399e-05 | -0.000147404 | -8.19982e-05 |
| 1 | 0.75 | s_all | 54 | 54 | 0 | 0 | 54 | 0 | 54 | -2.98538e-05 | -2.98538e-05 | -0.000111811 | -7.51395e-05 |
| 0.75 | 1.5 | all | 72 | 36 | 0 | 0 | 36 | 0 | 36 | -2.77986e-05 | -2.77986e-05 | -0.00043799 | -0.00035752 |
| 1 | 1.25 | q2s3 | 18 | 18 | 0 | 0 | 18 | 0 | 18 | -3.14769e-05 | -3.14769e-05 | -0.000484506 | -0.000400911 |
| 1 | 1 | q2s3 | 18 | 18 | 0 | 0 | 18 | 0 | 18 | -3.12824e-05 | -3.12824e-05 | -0.000391043 | -0.000331954 |
| 1 | 1.5 | q2s3 | 18 | 18 | 0 | 0 | 18 | 0 | 18 | -3.11678e-05 | -3.11678e-05 | -0.000576243 | -0.000468967 |
| 1 | 0.75 | q2s3 | 18 | 18 | 0 | 0 | 18 | 0 | 18 | -3.06173e-05 | -3.06173e-05 | -0.000295857 | -0.000264112 |
| 0.75 | 1.5 | s_all | 54 | 18 | 0 | 0 | 18 | 0 | 18 | -2.84019e-05 | -2.84019e-05 | -0.00021606 | -8.65328e-05 |
| 0.75 | 1.25 | q2s3 | 18 | 18 | 0 | 0 | 18 | 0 | 18 | -2.78633e-05 | -2.78633e-05 | -0.000484506 | -0.000391778 |
| 0.75 | 1.25 | s_all | 54 | 18 | 0 | 0 | 18 | 0 | 18 | -2.78031e-05 | -2.78031e-05 | -0.000182155 | -7.9244e-05 |
| 0.75 | 1.5 | q2s3 | 18 | 18 | 0 | 0 | 18 | 0 | 18 | -2.76036e-05 | -2.76036e-05 | -0.000576243 | -0.00046076 |
| 0.75 | 1 | q2s3 | 18 | 15 | 0 | 0 | 15 | 0 | 15 | -2.75794e-05 | -2.75794e-05 | -0.000391043 | -0.000322949 |
| 0.75 | 1.25 | all | 72 | 1 | 0 | 0 | 1 | 0 | 1 | -2.75218e-05 | -2.75218e-05 | -0.000344743 | -0.000239456 |
| 0.5 | 0.75 | all | 72 | 0 | 0 | 0 | 0 | 0 | 0 | -2.08751e-05 |  |  |  |
| 0.5 | 0.75 | q2s3 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | -2.14812e-05 |  |  |  |
| 0.5 | 0.75 | s_all | 54 | 0 | 0 | 0 | 0 | 0 | 0 | -2.05643e-05 |  |  |  |
| 0.5 | 1 | all | 72 | 0 | 0 | 0 | 0 | 0 | 0 | -2.16786e-05 |  |  |  |
| 0.5 | 1 | q2s3 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | -2.21803e-05 |  |  |  |
| 0.5 | 1 | s_all | 54 | 0 | 0 | 0 | 0 | 0 | 0 | -2.15835e-05 |  |  |  |
| 0.5 | 1.25 | all | 72 | 0 | 0 | 0 | 0 | 0 | 0 | -2.21269e-05 |  |  |  |
| 0.5 | 1.25 | q2s3 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | -2.23527e-05 |  |  |  |
| 0.5 | 1.25 | s_all | 54 | 0 | 0 | 0 | 0 | 0 | 0 | -2.23691e-05 |  |  |  |
| 0.5 | 1.5 | all | 72 | 0 | 0 | 0 | 0 | 0 | 0 | -2.2331e-05 |  |  |  |
| 0.5 | 1.5 | q2s3 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | -2.19936e-05 |  |  |  |
| 0.5 | 1.5 | s_all | 54 | 0 | 0 | 0 | 0 | 0 | 0 | -2.2917e-05 |  |  |  |
| 0.75 | 0.75 | all | 72 | 0 | 0 | 0 | 0 | 0 | 0 | -2.61951e-05 |  |  |  |
| 0.75 | 0.75 | q2s3 | 18 | 0 | 0 | 0 | 0 | 0 | 0 | -2.67943e-05 |  |  |  |
| 0.75 | 0.75 | s_all | 54 | 0 | 0 | 0 | 0 | 0 | 0 | -2.59707e-05 |  |  |  |
| 0.75 | 1 | all | 72 | 0 | 0 | 0 | 0 | 0 | 0 | -2.70601e-05 |  |  |  |
| 0.75 | 1 | s_all | 54 | 0 | 0 | 0 | 0 | 0 | 0 | -2.70241e-05 |  |  |  |

## Strict Rows

None.

## Loose Rows

| struct_source_file | struct_weight | q_weight | q_target_scope | all_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_core_minus_base | hidden_q2s3_mean_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | strict_gate | loose_gate | structural_strict_gate | structural_loose_gate | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | 1 | 1.5 | s_all | -3.215e-05 | 2 | 2 | -0.000243859 | -0.00021606 | -7.23647e-05 | -5.00685e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_1c74da00 |
| submission_jepa_block_consensus_gate_299a7455.csv | 1 | 1.5 | s_all | -3.20899e-05 | 2 | 2 | -0.000222469 | -0.00021606 | -4.50502e-05 | 1.65933e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_70d605a6 |
| submission_jepa_block_consensus_gate_5738e95e.csv | 1 | 1.5 | s_all | -3.20888e-05 | 2 | 2 | -0.000222493 | -0.00021606 | -4.49348e-05 | 1.66821e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_f62744c9 |
| submission_jepa_block_consensus_gate_aa97b049.csv | 1 | 1.5 | s_all | -3.208e-05 | 2 | 2 | -0.000222422 | -0.00021606 | -4.52798e-05 | 1.64192e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_13704b35 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | 1 | 1.5 | s_all | -3.20796e-05 | 2 | 2 | -0.000222512 | -0.00021606 | -4.51457e-05 | 1.64849e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_4c2e1626 |
| submission_jepa_block_consensus_gate_76aff53b.csv | 1 | 1.5 | s_all | -3.20663e-05 | 2 | 2 | -0.000222368 | -0.00021606 | -4.52879e-05 | 1.64402e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_7e134d7c |
| submission_jepa_block_consensus_gate_c28e6346.csv | 1 | 1.5 | s_all | -3.20652e-05 | 2 | 2 | -0.000222448 | -0.00021606 | -4.53556e-05 | 1.64491e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_b4e1121a |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | 1 | 1.5 | s_all | -3.20623e-05 | 2 | 2 | -0.000255196 | -0.00021606 | -9.0247e-05 | -1.89474e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_8d01c0dd |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | 1 | 1.5 | s_all | -3.20599e-05 | 2 | 2 | -0.000254455 | -0.00021606 | -8.93752e-05 | -1.82594e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_39fe13e4 |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | 1 | 1.5 | s_all | -3.20575e-05 | 2 | 2 | -0.000253714 | -0.00021606 | -8.85058e-05 | -1.75714e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_d8b1a2ee |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | 1 | 1.5 | s_all | -3.20557e-05 | 2 | 2 | -0.000252973 | -0.00021606 | -8.76403e-05 | -1.68834e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_731d4c90 |
| submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv | 1 | 1.5 | s_all | -3.2046e-05 | 2 | 2 | -0.000258965 | -0.00021606 | -9.45917e-05 | -2.21862e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_8ec6520b |
| submission_jepa_block_consensus_rawcorr_micro_cc5b3053.csv | 1 | 1.5 | s_all | -3.20457e-05 | 2 | 2 | -0.000258753 | -0.00021606 | -9.42884e-05 | -2.19628e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_67814018 |
| submission_jepa_block_consensus_rawcorr_micro_d9851c05.csv | 1 | 1.5 | s_all | -3.20454e-05 | 2 | 2 | -0.000258541 | -0.00021606 | -9.39851e-05 | -2.17394e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_e45a6c73 |
| submission_jepa_block_consensus_rawcorr_micro_d7f8c65c.csv | 1 | 1.5 | s_all | -3.20451e-05 | 2 | 2 | -0.000258329 | -0.00021606 | -9.36818e-05 | -2.15159e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_7aff1692 |
| submission_jepa_block_consensus_rawcorr_micro_d2dbf75c.csv | 1 | 1.5 | s_all | -3.20449e-05 | 2 | 2 | -0.000258116 | -0.00021606 | -9.33784e-05 | -2.12925e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_244263c6 |
| submission_jepa_block_consensus_rawcorr_micro_c8d38ede.csv | 1 | 1.5 | s_all | -3.20446e-05 | 2 | 2 | -0.000257904 | -0.00021606 | -9.30751e-05 | -2.10691e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_9128ef0e |
| submission_jepa_block_consensus_rawcorr_refine_a4c875f3.csv | 1 | 1.5 | s_all | -3.20102e-05 | 2 | 2 | -0.000255506 | -0.00021606 | -8.49636e-05 | -1.47401e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_ded296a7 |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | 1 | 1.25 | s_all | -3.16286e-05 | 2 | 2 | -0.000234172 | -0.000182155 | -6.74357e-05 | -1.63106e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_18fc4336 |
| submission_jepa_block_consensus_gate_299a7455.csv | 1 | 1.25 | s_all | -3.1559e-05 | 2 | 2 | -0.000212782 | -0.000182155 | -3.88368e-05 | 5.28952e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_7ae08131 |
| submission_jepa_block_consensus_gate_5738e95e.csv | 1 | 1.25 | s_all | -3.15568e-05 | 2 | 2 | -0.000212806 | -0.000182155 | -3.87251e-05 | 5.37836e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_c3c52fd2 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | 1 | 1.25 | s_all | -3.15553e-05 | 2 | 2 | -0.000245509 | -0.000182155 | -8.52384e-05 | -3.02512e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_5533d9a2 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | 1 | 1.25 | s_all | -3.15525e-05 | 2 | 2 | -0.000244768 | -0.000182155 | -8.43449e-05 | -2.95632e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_0f4d2c4c |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | 1 | 1.25 | s_all | -3.15492e-05 | 2 | 2 | -0.000244027 | -0.000182155 | -8.34538e-05 | -2.88752e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_cdb16051 |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | 1 | 1.25 | s_all | -3.15459e-05 | 2 | 2 | -0.000243286 | -0.000182155 | -8.25666e-05 | -2.81872e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_fd426587 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | 1 | 1.25 | s_all | -3.15446e-05 | 2 | 2 | -0.000212825 | -0.000182155 | -3.90164e-05 | 5.18109e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_14732f0d |
| submission_jepa_block_consensus_gate_aa97b049.csv | 1 | 1.25 | s_all | -3.15434e-05 | 2 | 2 | -0.000212734 | -0.000182155 | -3.91225e-05 | 5.11538e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_5ff7e3e2 |
| submission_jepa_block_consensus_rawcorr_micro_c8d38ede.csv | 1 | 1.25 | s_all | -3.15351e-05 | 2 | 2 | -0.000248217 | -0.000182155 | -8.80655e-05 | -3.23729e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_21f1b6fb |
| submission_jepa_block_consensus_rawcorr_micro_d2dbf75c.csv | 1 | 1.25 | s_all | -3.1535e-05 | 2 | 2 | -0.000248429 | -0.000182155 | -8.83543e-05 | -3.25963e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_0999d632 |
| submission_jepa_block_consensus_rawcorr_micro_d7f8c65c.csv | 1 | 1.25 | s_all | -3.15348e-05 | 2 | 2 | -0.000248641 | -0.000182155 | -8.8643e-05 | -3.28197e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_d70ef107 |

## Best Evaluated Rows

| struct_source_file | struct_weight | q_weight | q_target_scope | all_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_core_minus_base | hidden_q2s3_mean_minus_base | world_support_minus_base | raw_energy_q_p90_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | strict_gate | loose_gate | structural_strict_gate | structural_loose_gate | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | 1 | 1.5 | s_all | -3.215e-05 | 2 | 2 | -0.000243859 | -0.00021606 | -7.23647e-05 | -5.00685e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_1c74da00 |
| submission_jepa_block_consensus_gate_299a7455.csv | 1 | 1.5 | s_all | -3.20899e-05 | 2 | 2 | -0.000222469 | -0.00021606 | -4.50502e-05 | 1.65933e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_70d605a6 |
| submission_jepa_block_consensus_gate_5738e95e.csv | 1 | 1.5 | s_all | -3.20888e-05 | 2 | 2 | -0.000222493 | -0.00021606 | -4.49348e-05 | 1.66821e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_f62744c9 |
| submission_jepa_block_consensus_gate_aa97b049.csv | 1 | 1.5 | s_all | -3.208e-05 | 2 | 2 | -0.000222422 | -0.00021606 | -4.52798e-05 | 1.64192e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_13704b35 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | 1 | 1.5 | s_all | -3.20796e-05 | 2 | 2 | -0.000222512 | -0.00021606 | -4.51457e-05 | 1.64849e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_4c2e1626 |
| submission_jepa_block_consensus_gate_76aff53b.csv | 1 | 1.5 | s_all | -3.20663e-05 | 2 | 2 | -0.000222368 | -0.00021606 | -4.52879e-05 | 1.64402e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_7e134d7c |
| submission_jepa_block_consensus_gate_c28e6346.csv | 1 | 1.5 | s_all | -3.20652e-05 | 2 | 2 | -0.000222448 | -0.00021606 | -4.53556e-05 | 1.64491e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_b4e1121a |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | 1 | 1.5 | s_all | -3.20623e-05 | 2 | 2 | -0.000255196 | -0.00021606 | -9.0247e-05 | -1.89474e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_8d01c0dd |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | 1 | 1.5 | s_all | -3.20599e-05 | 2 | 2 | -0.000254455 | -0.00021606 | -8.93752e-05 | -1.82594e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_39fe13e4 |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | 1 | 1.5 | s_all | -3.20575e-05 | 2 | 2 | -0.000253714 | -0.00021606 | -8.85058e-05 | -1.75714e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_d8b1a2ee |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | 1 | 1.5 | s_all | -3.20557e-05 | 2 | 2 | -0.000252973 | -0.00021606 | -8.76403e-05 | -1.68834e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_731d4c90 |
| submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv | 1 | 1.5 | s_all | -3.2046e-05 | 2 | 2 | -0.000258965 | -0.00021606 | -9.45917e-05 | -2.21862e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_8ec6520b |
| submission_jepa_block_consensus_rawcorr_micro_cc5b3053.csv | 1 | 1.5 | s_all | -3.20457e-05 | 2 | 2 | -0.000258753 | -0.00021606 | -9.42884e-05 | -2.19628e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_67814018 |
| submission_jepa_block_consensus_rawcorr_micro_d9851c05.csv | 1 | 1.5 | s_all | -3.20454e-05 | 2 | 2 | -0.000258541 | -0.00021606 | -9.39851e-05 | -2.17394e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_e45a6c73 |
| submission_jepa_block_consensus_rawcorr_micro_d7f8c65c.csv | 1 | 1.5 | s_all | -3.20451e-05 | 2 | 2 | -0.000258329 | -0.00021606 | -9.36818e-05 | -2.15159e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_7aff1692 |
| submission_jepa_block_consensus_rawcorr_micro_d2dbf75c.csv | 1 | 1.5 | s_all | -3.20449e-05 | 2 | 2 | -0.000258116 | -0.00021606 | -9.33784e-05 | -2.12925e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_244263c6 |
| submission_jepa_block_consensus_rawcorr_micro_c8d38ede.csv | 1 | 1.5 | s_all | -3.20446e-05 | 2 | 2 | -0.000257904 | -0.00021606 | -9.30751e-05 | -2.10691e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_9128ef0e |
| submission_jepa_block_consensus_rawcorr_refine_a4c875f3.csv | 1 | 1.5 | s_all | -3.20102e-05 | 2 | 2 | -0.000255506 | -0.00021606 | -8.49636e-05 | -1.47401e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.50_ded296a7 |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | 1 | 1.25 | s_all | -3.16286e-05 | 2 | 2 | -0.000234172 | -0.000182155 | -6.74357e-05 | -1.63106e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_18fc4336 |
| submission_jepa_block_consensus_gate_299a7455.csv | 1 | 1.25 | s_all | -3.1559e-05 | 2 | 2 | -0.000212782 | -0.000182155 | -3.88368e-05 | 5.28952e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_7ae08131 |
| submission_jepa_block_consensus_gate_5738e95e.csv | 1 | 1.25 | s_all | -3.15568e-05 | 2 | 2 | -0.000212806 | -0.000182155 | -3.87251e-05 | 5.37836e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_c3c52fd2 |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | 1 | 1.25 | s_all | -3.15553e-05 | 2 | 2 | -0.000245509 | -0.000182155 | -8.52384e-05 | -3.02512e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_5533d9a2 |
| submission_jepa_block_consensus_rawcorr_refine_e8508f79.csv | 1 | 1.25 | s_all | -3.15525e-05 | 2 | 2 | -0.000244768 | -0.000182155 | -8.43449e-05 | -2.95632e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_0f4d2c4c |
| submission_jepa_block_consensus_rawcorr_refine_1f86615e.csv | 1 | 1.25 | s_all | -3.15492e-05 | 2 | 2 | -0.000244027 | -0.000182155 | -8.34538e-05 | -2.88752e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_cdb16051 |
| submission_jepa_block_consensus_rawcorr_refine_ad008bbb.csv | 1 | 1.25 | s_all | -3.15459e-05 | 2 | 2 | -0.000243286 | -0.000182155 | -8.25666e-05 | -2.81872e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_fd426587 |
| submission_jepa_block_consensus_gate_eef3daf0.csv | 1 | 1.25 | s_all | -3.15446e-05 | 2 | 2 | -0.000212825 | -0.000182155 | -3.90164e-05 | 5.18109e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_14732f0d |
| submission_jepa_block_consensus_gate_aa97b049.csv | 1 | 1.25 | s_all | -3.15434e-05 | 2 | 2 | -0.000212734 | -0.000182155 | -3.91225e-05 | 5.11538e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_5ff7e3e2 |
| submission_jepa_block_consensus_rawcorr_micro_c8d38ede.csv | 1 | 1.25 | s_all | -3.15351e-05 | 2 | 2 | -0.000248217 | -0.000182155 | -8.80655e-05 | -3.23729e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_21f1b6fb |
| submission_jepa_block_consensus_rawcorr_micro_d2dbf75c.csv | 1 | 1.25 | s_all | -3.1535e-05 | 2 | 2 | -0.000248429 | -0.000182155 | -8.83543e-05 | -3.25963e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_0999d632 |
| submission_jepa_block_consensus_rawcorr_micro_d7f8c65c.csv | 1 | 1.25 | s_all | -3.15348e-05 | 2 | 2 | -0.000248641 | -0.000182155 | -8.8643e-05 | -3.28197e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_d70ef107 |
| submission_jepa_block_consensus_rawcorr_micro_d9851c05.csv | 1 | 1.25 | s_all | -3.15347e-05 | 2 | 2 | -0.000248854 | -0.000182155 | -8.89317e-05 | -3.30431e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_5fb4a4fb |
| submission_jepa_block_consensus_rawcorr_micro_cc5b3053.csv | 1 | 1.25 | s_all | -3.15346e-05 | 2 | 2 | -0.000249066 | -0.000182155 | -8.92204e-05 | -3.32665e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_2909fa43 |
| submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv | 1 | 1.25 | s_all | -3.15346e-05 | 2 | 2 | -0.000249278 | -0.000182155 | -8.95091e-05 | -3.349e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_9e72e1f8 |
| submission_jepa_block_consensus_gate_c28e6346.csv | 1 | 1.25 | s_all | -3.15261e-05 | 2 | 2 | -0.000212761 | -0.000182155 | -3.93256e-05 | 5.14536e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_1624b6ca |
| submission_jepa_block_consensus_gate_76aff53b.csv | 1 | 1.25 | s_all | -3.15259e-05 | 2 | 2 | -0.000212681 | -0.000182155 | -3.92393e-05 | 5.13639e-06 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_3f3c9b3b |
| submission_jepa_block_consensus_rawcorr_refine_a4c875f3.csv | 1 | 1.25 | s_all | -3.15041e-05 | 2 | 2 | -0.000245819 | -0.000182155 | -8.00136e-05 | -2.60439e-05 | 0.722222 | 0.944444 | False | True | False | True | e84_sw1.00_qw1.25_b00361b9 |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | 1 | 1.25 | q2s3 | -3.14769e-05 | 2 | 2 | -0.000320558 | -0.000484506 | -0.000379121 | -0.000248041 | 0.777778 | 1 | False | True | False | True | e84_sw1.00_qw1.25_72b0f775 |
| submission_jepa_block_consensus_rawcorr_refine_aeabeb26.csv | 1 | 1.5 | all | -3.14482e-05 | 2 | 2 | -0.000307268 | -0.00043799 | -0.000344242 | -0.000230711 | 0.833333 | 1 | False | True | False | True | e84_sw1.00_qw1.50_ad27732a |
| submission_jepa_block_consensus_rawcorr_refine_d9aefe69.csv | 1 | 1.25 | q2s3 | -3.14323e-05 | 2 | 2 | -0.000331895 | -0.000484506 | -0.000396722 | -0.000261981 | 0.777778 | 1 | False | True | False | True | e84_sw1.00_qw1.25_85d19622 |
| submission_jepa_block_consensus_rawcorr_micro_9ec2b75e.csv | 1 | 1.25 | q2s3 | -3.14279e-05 | 2 | 2 | -0.000335664 | -0.000484506 | -0.000400911 | -0.00026522 | 0.777778 | 1 | False | True | False | True | e84_sw1.00_qw1.25_5b2c4c20 |

## Decision

No strict/deployable recombination survived.

The additive decomposition is therefore not enough for a safe candidate; the conflict is likely row/block-specific rather than separable by target group.

Materialized a diagnostic inverse-top sensor only: `submission_e84_inverse_sensor_1c74da00.csv`.

This is not a deployable-safe recommendation. It tests whether the public subset behaves like the inverse-top combo set that rejects every otherwise-healthy E84 candidate.