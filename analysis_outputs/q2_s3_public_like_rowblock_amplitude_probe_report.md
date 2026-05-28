# E79 Public-Like Row/Block Q2/S3 Amplitude Probe

## Observe

E75's full-pool Q2/S3 sparse amplitude is still the best local all-combo amplitude sensor, while E76-E78 rejected source-subset consensus and posterior averaging as reliable amplitude repairs.

The remaining oddity is that the actual data are not iid rows: submission rows appear in subject-specific calendar runs bracketed by train rows, so the context can include row position, flanking train labels, subject priors, and latent movement energy.

## Wonder

Is the E75 amplitude direction valid, but only on public-like row/block/flank contexts rather than across all Q2/S3 sparse cells?

## Hypothesis

H75: a hidden public-like subset is better approximated by row/block topology and nearest train-label flanks than by E76 source-subset reliability. If true, some rowblock-localized amplitude candidates should beat E75 local all-combo under the same deployable stress gates.

## Method

- Base movement: E75 full-pool `translator_tail_soft_p90_m0.50` / `top_abs50` unit delta.
- Q2 alpha grid: `[0.0, 4.0, 8.0, 12.0, 16.0, 20.0]`.
- S3 alpha grid: `[16.0, 20.0, 24.0, 28.0, 32.0, 36.0]`.
- Masks: topology, topology x E75 unit energy, subject priors, subject ids, nearest flanking train target priors, and target-specific Q2/S3 flank gates.
- Stress: the same all-combo, hidden, world, block, raw-energy, strict/deployable gates used by E76-E78.

## Context Summary

| subject_id | rows | sub_blocks | mean_block_n | q2_rate | s3_rate | flank_q2_mean | flank_s3_mean | near_train_le2 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| id01 | 27 | 2 | 13.5185 | 0.560976 | 0.853659 | 1 | 1 | 0.148148 |
| id02 | 32 | 2 | 16 | 0.666667 | 0.895833 | 1 | 1 | 0.1875 |
| id03 | 21 | 2 | 10.5238 | 0.818182 | 0.484848 | 1 | 1 | 0.190476 |
| id04 | 27 | 7 | 5.37037 | 0.491228 | 0.54386 | 0.555556 | 0.611111 | 0.703704 |
| id05 | 21 | 5 | 5.09524 | 0.431818 | 0.136364 | 0.833333 | 0.0952381 | 0.52381 |
| id06 | 24 | 5 | 5.91667 | 0.395833 | 0.958333 | 0.729167 | 1 | 0.583333 |
| id07 | 30 | 2 | 15 | 0.510204 | 0.795918 | 0 | 1 | 0.2 |
| id08 | 19 | 7 | 3.63158 | 0.785714 | 0.660714 | 0.736842 | 0.684211 | 0.789474 |
| id09 | 27 | 2 | 13.5185 | 0.439024 | 0.707317 | 0.481481 | 1 | 0.148148 |
| id10 | 22 | 2 | 11 | 0.545455 | 0.484848 | 0.25 | 0.25 | 0.136364 |

## Mask Summary

| source_name | mask_mode | threshold | row_count | row_coverage | subjects | mask_mean_q2 | mask_mean_s3 | mask_active_q2 | mask_active_s3 | active_subjects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control | identity |  | 72 | 0.288 | 10 | 1 | 1 | 1 | 1 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| unit_energy | top30 | 0.00117506 | 22 | 0.088 | 9 | 0.175 | 0.538462 | 0.175 | 0.538462 | id01,id02,id04,id05,id06,id07,id08,id09,id10 |
| unit_energy | top50 | 0.00103396 | 36 | 0.144 | 10 | 0.4 | 0.692308 | 0.4 | 0.692308 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| unit_energy | low50 | 0.00103396 | 36 | 0.144 | 9 | 0.6 | 0.307692 | 0.6 | 0.307692 | id01,id02,id03,id04,id06,id07,id08,id09,id10 |
| unit_energy | soft_rank_positive |  | 72 | 0.288 | 10 | 0.463889 | 0.614672 | 1 | 1 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| topology | two_flank_train |  | 41 | 0.164 | 9 | 0.525 | 0.615385 | 0.525 | 0.615385 | id01,id02,id03,id04,id05,id06,id07,id08,id10 |
| topology_x_energy | two_flank_train_energy_top50 |  | 19 | 0.076 | 9 | 0.175 | 0.410256 | 0.175 | 0.410256 | id01,id02,id03,id04,id05,id06,id07,id08,id10 |
| topology | one_flank_train |  | 31 | 0.124 | 8 | 0.475 | 0.384615 | 0.475 | 0.384615 | id01,id02,id03,id04,id06,id07,id09,id10 |
| topology_x_energy | one_flank_train_energy_top50 |  | 17 | 0.068 | 7 | 0.225 | 0.282051 | 0.225 | 0.282051 | id01,id02,id04,id06,id07,id09,id10 |
| topology | near_train_le1 |  | 13 | 0.052 | 5 | 0.175 | 0.230769 | 0.175 | 0.230769 | id02,id04,id06,id07,id09 |
| topology_x_energy | near_train_le1_energy_top50 |  | 7 | 0.028 | 4 | 0.1 | 0.153846 | 0.1 | 0.153846 | id04,id06,id07,id09 |
| topology | near_train_le2 |  | 25 | 0.1 | 8 | 0.325 | 0.435897 | 0.325 | 0.435897 | id01,id02,id04,id05,id06,id07,id08,id09 |
| topology_x_energy | near_train_le2_energy_top50 |  | 12 | 0.048 | 5 | 0.15 | 0.282051 | 0.15 | 0.282051 | id04,id05,id06,id07,id09 |
| topology | near_train_le3 |  | 40 | 0.16 | 10 | 0.525 | 0.641026 | 0.525 | 0.641026 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| topology_x_energy | near_train_le3_energy_top50 |  | 18 | 0.072 | 8 | 0.2 | 0.410256 | 0.2 | 0.410256 | id01,id04,id05,id06,id07,id08,id09,id10 |
| topology | block_edge |  | 17 | 0.068 | 8 | 0.2 | 0.307692 | 0.2 | 0.307692 | id02,id03,id04,id05,id06,id07,id08,id09 |
| topology_x_energy | block_edge_energy_top50 |  | 8 | 0.032 | 5 | 0.1 | 0.179487 | 0.1 | 0.179487 | id04,id05,id06,id07,id09 |
| topology | block_inner |  | 55 | 0.22 | 10 | 0.8 | 0.692308 | 0.8 | 0.692308 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| topology_x_energy | block_inner_energy_top50 |  | 28 | 0.112 | 9 | 0.3 | 0.512821 | 0.3 | 0.512821 | id01,id02,id03,id04,id05,id06,id07,id08,id10 |
| topology | block_first2 |  | 25 | 0.1 | 10 | 0.3 | 0.435897 | 0.3 | 0.435897 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| topology_x_energy | block_first2_energy_top50 |  | 11 | 0.044 | 5 | 0.125 | 0.25641 | 0.125 | 0.25641 | id04,id05,id06,id07,id09 |
| topology | block_last2 |  | 17 | 0.068 | 9 | 0.175 | 0.307692 | 0.175 | 0.307692 | id01,id02,id04,id05,id06,id07,id08,id09,id10 |
| topology_x_energy | block_last2_energy_top50 |  | 9 | 0.036 | 6 | 0.05 | 0.230769 | 0.05 | 0.230769 | id01,id02,id04,id05,id06,id07 |
| topology | block_first_half |  | 43 | 0.172 | 10 | 0.65 | 0.564103 | 0.65 | 0.564103 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| topology_x_energy | block_first_half_energy_top50 |  | 20 | 0.08 | 8 | 0.3 | 0.333333 | 0.3 | 0.333333 | id02,id03,id04,id05,id06,id07,id09,id10 |
| topology | block_second_half |  | 33 | 0.132 | 10 | 0.45 | 0.461538 | 0.45 | 0.461538 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| topology_x_energy | block_second_half_energy_top50 |  | 18 | 0.072 | 8 | 0.15 | 0.384615 | 0.15 | 0.384615 | id01,id02,id04,id05,id06,id07,id08,id10 |
| topology | short_block_le5 |  | 13 | 0.052 | 4 | 0.15 | 0.230769 | 0.15 | 0.230769 | id04,id05,id06,id08 |
| topology_x_energy | short_block_le5_energy_top50 |  | 7 | 0.028 | 3 | 0.075 | 0.153846 | 0.075 | 0.153846 | id04,id05,id06 |
| topology | long_block_ge10 |  | 41 | 0.164 | 6 | 0.55 | 0.512821 | 0.55 | 0.512821 | id01,id02,id03,id07,id09,id10 |
| topology_x_energy | long_block_ge10_energy_top50 |  | 20 | 0.08 | 6 | 0.2 | 0.333333 | 0.2 | 0.333333 | id01,id02,id03,id07,id09,id10 |
| topology | subject_early_half |  | 30 | 0.12 | 9 | 0.4 | 0.410256 | 0.4 | 0.410256 | id01,id02,id03,id04,id05,id06,id07,id08,id10 |
| topology_x_energy | subject_early_half_energy_top50 |  | 14 | 0.056 | 9 | 0.125 | 0.282051 | 0.125 | 0.282051 | id01,id02,id03,id04,id05,id06,id07,id08,id10 |
| topology | subject_late_half |  | 43 | 0.172 | 10 | 0.625 | 0.589744 | 0.625 | 0.589744 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| topology_x_energy | subject_late_half_energy_top50 |  | 22 | 0.088 | 8 | 0.275 | 0.410256 | 0.275 | 0.410256 | id01,id02,id04,id05,id06,id07,id09,id10 |
| subject_prior | q2_high | 0.510204 | 43 | 0.172 | 6 | 0.575 | 0.564103 | 0.575 | 0.564103 | id01,id02,id03,id07,id08,id10 |
| subject_prior | q2_low | 0.510204 | 40 | 0.16 | 5 | 0.675 | 0.487179 | 0.675 | 0.487179 | id04,id05,id06,id07,id09 |
| subject_prior | s3_high | 0.707317 | 44 | 0.176 | 5 | 0.625 | 0.589744 | 0.625 | 0.589744 | id01,id02,id06,id07,id09 |
| subject_prior | s3_low | 0.707317 | 31 | 0.124 | 6 | 0.425 | 0.435897 | 0.425 | 0.435897 | id03,id04,id05,id08,id09,id10 |
| subject_prior_target | q2_low_s3_high |  | 46 | 0.184 | 6 | 0.675 | 0.589744 | 0.675 | 0.589744 | id01,id02,id04,id06,id07,id09 |
| subject_prior_target | q2_high_s3_low |  | 39 | 0.156 | 8 | 0.575 | 0.435897 | 0.575 | 0.435897 | id01,id03,id04,id05,id07,id08,id09,id10 |
| subject_id | id01 |  | 8 | 0.032 | 1 | 0.05 | 0.153846 | 0.05 | 0.153846 | id01 |
| subject_id | id02 |  | 7 | 0.028 | 1 | 0 | 0.179487 | 0 | 0.179487 | id02 |
| subject_id | id03 |  | 3 | 0.012 | 1 | 0.05 | 0.025641 | 0.05 | 0.025641 | id03 |
| subject_id | id04 |  | 9 | 0.036 | 1 | 0.1 | 0.179487 | 0.1 | 0.179487 | id04 |
| subject_id | id05 |  | 2 | 0.008 | 1 | 0 | 0.0512821 | 0 | 0.0512821 | id05 |
| subject_id | id06 |  | 15 | 0.06 | 1 | 0.275 | 0.179487 | 0.275 | 0.179487 | id06 |
| subject_id | id07 |  | 11 | 0.044 | 1 | 0.25 | 0.0512821 | 0.25 | 0.0512821 | id07 |
| subject_id | id08 |  | 5 | 0.02 | 1 | 0.075 | 0.0769231 | 0.075 | 0.0769231 | id08 |
| subject_id | id09 |  | 3 | 0.012 | 1 | 0.05 | 0.025641 | 0.05 | 0.025641 | id09 |
| subject_id | id10 |  | 9 | 0.036 | 1 | 0.15 | 0.0769231 | 0.15 | 0.0769231 | id10 |
| flank_prior | has_q2_or_s3_flank |  | 72 | 0.288 | 10 | 1 | 1 | 1 | 1 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| flank_prior | q2_high |  | 56 | 0.224 | 9 | 0.675 | 0.897436 | 0.675 | 0.897436 | id01,id02,id03,id04,id05,id06,id08,id09,id10 |
| flank_prior | q2_low |  | 38 | 0.152 | 6 | 0.625 | 0.384615 | 0.625 | 0.384615 | id04,id05,id06,id07,id08,id10 |
| flank_prior | s3_high |  | 63 | 0.252 | 10 | 0.9 | 0.846154 | 0.9 | 0.846154 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| flank_prior | s3_low |  | 20 | 0.08 | 4 | 0.2 | 0.333333 | 0.2 | 0.333333 | id04,id05,id08,id10 |
| flank_prior | q2_low_s3_high |  | 31 | 0.124 | 6 | 0.55 | 0.282051 | 0.55 | 0.282051 | id04,id05,id06,id07,id08,id10 |
| flank_prior | q2_high_s3_low |  | 15 | 0.06 | 4 | 0.125 | 0.282051 | 0.125 | 0.282051 | id04,id05,id08,id10 |
| flank_prior_target | q2_low_s3_high |  | 56 | 0.224 | 10 | 0.625 | 0.846154 | 0.625 | 0.846154 | id01,id02,id03,id04,id05,id06,id07,id08,id09,id10 |
| flank_prior_target | q2_strong_low_s3_strong_high |  | 38 | 0.152 | 9 | 0.325 | 0.666667 | 0.325 | 0.666667 | id01,id02,id03,id04,id06,id07,id08,id09,id10 |
| flank_prior_target | q2_strong_high_s3_strong_low |  | 20 | 0.08 | 8 | 0.375 | 0.153846 | 0.375 | 0.153846 | id01,id03,id04,id05,id06,id08,id09,id10 |

## Source Stress Summary

| source_name | rows | strict | deployable | loose | beats_e75 | deployable_beats_e75 | best_all | best_hidden | best_world | best_block |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| topology | 1620 | 283 | 283 | 1020 | 0 | 0 | -1.22937e-05 | -0.000554926 | -0.00037977 | 0.722222 |
| topology_x_energy | 1620 | 268 | 268 | 630 | 0 | 0 | -1.19902e-05 | -0.000477343 | -0.000342565 | 0.666667 |
| flank_prior | 756 | 210 | 210 | 504 | 0 | 0 | -1.23676e-05 | -0.000619843 | -0.000417868 | 0.722222 |
| subject_id | 1080 | 182 | 182 | 360 | 0 | 0 | -1.20137e-05 | -0.000427393 | -0.000355572 | 0.611111 |
| unit_energy | 432 | 164 | 164 | 353 | 0 | 0 | -1.21712e-05 | -0.000524068 | -0.000384477 | 0.722222 |
| flank_prior_target | 324 | 80 | 80 | 194 | 0 | 0 | -1.21593e-05 | -0.00056813 | -0.000417868 | 0.666667 |
| subject_prior | 432 | 73 | 73 | 204 | 0 | 0 | -1.22237e-05 | -0.000536669 | -0.00041555 | 0.694444 |
| subject_prior_target | 216 | 38 | 38 | 102 | 0 | 0 | -1.22004e-05 | -0.000536669 | -0.00041555 | 0.666667 |
| control | 36 | 20 | 20 | 36 | 0 | 0 | -1.23676e-05 | -0.000615034 | -0.000395783 | 0.722222 |

## Best Mask/Localization Rows

| source_name | mask_mode | localization | rows | strict | deployable | loose | beats_e75_local_all | deployable_beats_e75 | best_all_delta_vs_mixmin | best_all_minus_base | best_worst_set_delta | best_hidden_q2s3_minus_base | best_world_support_minus_base | best_block_win_rate | best_alpha_q2 | best_alpha_s3 | row_count | subjects | mask_active_q2 | mask_active_s3 | best_deployable_delta | best_strict_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| unit_energy | soft_rank_positive | both | 36 | 23 | 23 | 30 | 0 | 0 | -1.12292e-05 | -6.46362e-06 | 8.60654e-06 | -0.000371018 | -0.000159589 | 0.722222 | 12 | 36 | 72 | 10 | 1 | 1 | -1.12292e-05 | -1.12292e-05 |
| unit_energy | soft_rank_positive | s3_local_q2_full | 36 | 22 | 22 | 30 | 0 | 0 | -1.14091e-05 | -6.64357e-06 | 8.39046e-06 | -0.000510606 | -0.000292914 | 0.722222 | 8 | 36 | 72 | 10 | 1 | 1 | -1.14091e-05 | -1.14091e-05 |
| unit_energy | top50 | s3_local_q2_full | 36 | 22 | 22 | 30 | 0 | 0 | -1.11365e-05 | -6.37094e-06 | 8.58208e-06 | -0.000524068 | -0.000299038 | 0.611111 | 8 | 28 | 36 | 10 | 0.4 | 0.692308 | -1.11365e-05 | -1.11365e-05 |
| control | identity | both | 36 | 20 | 20 | 36 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000615034 | -0.000395783 | 0.722222 | 8 | 28 | 72 | 10 | 1 | 1 | -1.23676e-05 | -1.23676e-05 |
| flank_prior | has_q2_or_s3_flank | both | 36 | 20 | 20 | 36 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000615034 | -0.000395783 | 0.722222 | 8 | 28 | 72 | 10 | 1 | 1 | -1.23676e-05 | -1.23676e-05 |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000615034 | -0.000395783 | 0.722222 | 8 | 28 | 72 | 10 | 1 | 1 | -1.23676e-05 | -1.23676e-05 |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.23676e-05 | -7.6021e-06 | 9.51415e-06 | -0.000615034 | -0.000395783 | 0.722222 | 8 | 28 | 72 | 10 | 1 | 1 | -1.23676e-05 | -1.23676e-05 |
| topology | block_first_half | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.22451e-05 | -7.47954e-06 | 9.55173e-06 | -0.000509199 | -0.000301298 | 0.694444 | 8 | 28 | 43 | 10 | 0.65 | 0.564103 | -1.22451e-05 | -1.22451e-05 |
| topology | subject_late_half | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.22407e-05 | -7.47515e-06 | 9.47999e-06 | -0.000534326 | -0.000349081 | 0.666667 | 12 | 28 | 43 | 10 | 0.625 | 0.589744 | -1.22407e-05 | -1.22407e-05 |
| subject_prior | s3_high | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.22237e-05 | -7.4582e-06 | 9.50417e-06 | -0.000528472 | -0.000348072 | 0.638889 | 8 | 28 | 44 | 5 | 0.625 | 0.589744 | -1.22237e-05 | -1.22237e-05 |
| subject_prior | q2_low | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.22004e-05 | -7.43489e-06 | 9.48292e-06 | -0.000536669 | -0.000311391 | 0.638889 | 8 | 28 | 40 | 5 | 0.675 | 0.487179 | -1.22004e-05 | -1.22004e-05 |
| subject_prior_target | q2_low_s3_high | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.22004e-05 | -7.43489e-06 | 9.48292e-06 | -0.000536669 | -0.000311391 | 0.638889 | 8 | 28 | 46 | 6 | 0.675 | 0.589744 | -1.22004e-05 | -1.22004e-05 |
| topology | one_flank_train | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.21629e-05 | -7.39735e-06 | 9.61478e-06 | -0.000506465 | -0.000325987 | 0.638889 | 12 | 28 | 31 | 8 | 0.475 | 0.384615 | -1.21629e-05 | -1.21629e-05 |
| flank_prior | q2_low | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.21593e-05 | -7.39376e-06 | 9.57071e-06 | -0.000511061 | -0.000252952 | 0.666667 | 8 | 28 | 38 | 6 | 0.625 | 0.384615 | -1.21593e-05 | -1.21593e-05 |
| flank_prior_target | q2_low_s3_high | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.21593e-05 | -7.39376e-06 | 9.57071e-06 | -0.000511061 | -0.000252952 | 0.666667 | 8 | 28 | 56 | 10 | 0.625 | 0.846154 | -1.21593e-05 | -1.21593e-05 |
| flank_prior | q2_low_s3_high | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.2095e-05 | -7.32948e-06 | 9.56046e-06 | -0.000466113 | -0.000203752 | 0.638889 | 8 | 28 | 31 | 6 | 0.55 | 0.282051 | -1.2095e-05 | -1.2095e-05 |
| subject_id | id07 | q2_local_s3_full | 36 | 20 | 20 | 36 | 0 | 0 | -1.20137e-05 | -7.24817e-06 | 9.63618e-06 | -0.000402114 | -0.000228157 | 0.583333 | 12 | 28 | 11 | 1 | 0.25 | 0.0512821 | -1.20137e-05 | -1.20137e-05 |
| unit_energy | top50 | both | 36 | 20 | 20 | 29 | 0 | 0 | -1.07621e-05 | -5.99657e-06 | 8.94718e-06 | -0.000386404 | -0.000189221 | 0.555556 | 8 | 28 | 36 | 10 | 0.4 | 0.692308 | -1.07621e-05 | -1.07621e-05 |
| flank_prior | s3_high | q2_local_s3_full | 36 | 19 | 19 | 36 | 0 | 0 | -1.23001e-05 | -7.53457e-06 | 9.51488e-06 | -0.000568639 | -0.000354673 | 0.694444 | 8 | 28 | 63 | 10 | 0.9 | 0.846154 | -1.23001e-05 | -1.23001e-05 |
| topology | block_inner | q2_local_s3_full | 36 | 19 | 19 | 36 | 0 | 0 | -1.22937e-05 | -7.52818e-06 | 9.57443e-06 | -0.000554926 | -0.000346681 | 0.694444 | 8 | 28 | 55 | 10 | 0.8 | 0.692308 | -1.22937e-05 | -1.22937e-05 |
| flank_prior_target | q2_strong_low_s3_strong_high | q2_local_s3_full | 36 | 19 | 19 | 36 | 0 | 0 | -1.20587e-05 | -7.2932e-06 | 9.65967e-06 | -0.000447062 | -0.000273513 | 0.611111 | 12 | 28 | 38 | 9 | 0.325 | 0.666667 | -1.20587e-05 | -1.20587e-05 |
| unit_energy | soft_rank_positive | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.21712e-05 | -7.40562e-06 | 9.70475e-06 | -0.000475446 | -0.000265782 | 0.722222 | 12 | 28 | 72 | 10 | 1 | 1 | -1.19753e-05 | -1.19753e-05 |
| subject_prior | q2_high | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.21691e-05 | -7.40362e-06 | 9.733e-06 | -0.000480479 | -0.000314253 | 0.666667 | 8 | 28 | 43 | 6 | 0.575 | 0.564103 | -1.19657e-05 | -1.19657e-05 |
| subject_prior_target | q2_high_s3_low | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.21691e-05 | -7.40362e-06 | 9.733e-06 | -0.000480479 | -0.000314253 | 0.666667 | 8 | 28 | 39 | 8 | 0.575 | 0.435897 | -1.19657e-05 | -1.19657e-05 |
| topology | long_block_ge10 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.21501e-05 | -7.3846e-06 | 9.77915e-06 | -0.000475764 | -0.000289535 | 0.666667 | 8 | 28 | 41 | 6 | 0.55 | 0.512821 | -1.19347e-05 | -1.19347e-05 |
| unit_energy | low50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.20903e-05 | -7.32473e-06 | 9.66365e-06 | -0.000450346 | -0.00021377 | 0.722222 | 8 | 28 | 36 | 9 | 0.6 | 0.307692 | -1.18713e-05 | -1.18713e-05 |
| topology | near_train_le3 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.20026e-05 | -7.23705e-06 | 9.65486e-06 | -0.000470845 | -0.000228047 | 0.666667 | 8 | 28 | 40 | 10 | 0.525 | 0.641026 | -1.18031e-05 | -1.18031e-05 |
| topology_x_energy | block_inner_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.19902e-05 | -7.22465e-06 | 9.75039e-06 | -0.00043676 | -0.000239989 | 0.666667 | 8 | 28 | 28 | 9 | 0.3 | 0.512821 | -1.17951e-05 | -1.17951e-05 |
| topology_x_energy | block_first_half_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.1982e-05 | -7.21647e-06 | 9.77296e-06 | -0.000430276 | -0.000221691 | 0.666667 | 8 | 28 | 20 | 8 | 0.3 | 0.333333 | -1.17922e-05 | -1.17922e-05 |
| topology | near_train_le2 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.1941e-05 | -7.17551e-06 | 9.66446e-06 | -0.000397084 | -0.000184005 | 0.638889 | 8 | 28 | 25 | 8 | 0.325 | 0.435897 | -1.17351e-05 | -1.17351e-05 |
| topology | block_second_half | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.19318e-05 | -7.16627e-06 | 9.84586e-06 | -0.000443498 | -0.000235602 | 0.722222 | 8 | 28 | 33 | 10 | 0.45 | 0.461538 | -1.17336e-05 | -1.17336e-05 |
| topology | block_first2 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.19234e-05 | -7.15789e-06 | 9.6972e-06 | -0.000384821 | -0.000154956 | 0.666667 | 8 | 28 | 25 | 10 | 0.3 | 0.435897 | -1.17113e-05 | -1.17113e-05 |
| topology_x_energy | long_block_ge10_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.19182e-05 | -7.15264e-06 | 9.84767e-06 | -0.000403493 | -0.000199362 | 0.638889 | 8 | 28 | 20 | 6 | 0.2 | 0.333333 | -1.17116e-05 | -1.17116e-05 |
| subject_id | id06 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.19085e-05 | -7.14299e-06 | 9.69104e-06 | -0.000427393 | -0.000219566 | 0.611111 | 8 | 28 | 15 | 1 | 0.275 | 0.179487 | -1.17046e-05 | -1.17046e-05 |
| topology_x_energy | subject_late_half_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.19084e-05 | -7.14287e-06 | 9.86981e-06 | -0.000438858 | -0.000253007 | 0.611111 | 8 | 28 | 22 | 8 | 0.275 | 0.410256 | -1.17138e-05 | -1.17138e-05 |
| topology_x_energy | one_flank_train_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.19032e-05 | -7.1377e-06 | 9.83776e-06 | -0.00042974 | -0.000244844 | 0.611111 | 8 | 28 | 17 | 7 | 0.225 | 0.282051 | -1.17093e-05 | -1.17093e-05 |
| topology | short_block_le5 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.18482e-05 | -7.08271e-06 | 9.70135e-06 | -0.000356236 | -0.000161373 | 0.638889 | 12 | 28 | 13 | 4 | 0.15 | 0.230769 | -1.16357e-05 | -1.16357e-05 |
| flank_prior | s3_low | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.18424e-05 | -7.07688e-06 | 9.94834e-06 | -0.000373437 | -0.000122226 | 0.638889 | 8 | 28 | 20 | 4 | 0.2 | 0.333333 | -1.16106e-05 | -1.16106e-05 |
| subject_id | id10 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.18125e-05 | -7.04696e-06 | 9.97129e-06 | -0.000368584 | -0.000134395 | 0.611111 | 8 | 28 | 9 | 1 | 0.15 | 0.0769231 | -1.15845e-05 | -1.15845e-05 |
| topology_x_energy | two_flank_train_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.18068e-05 | -7.04127e-06 | 9.93961e-06 | -0.000360311 | -0.000149654 | 0.638889 | 8 | 28 | 19 | 9 | 0.175 | 0.410256 | -1.16083e-05 | -1.16083e-05 |
| topology_x_energy | subject_early_half_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.18025e-05 | -7.03698e-06 | 9.92936e-06 | -0.000351194 | -0.000137945 | 0.638889 | 8 | 28 | 14 | 9 | 0.125 | 0.282051 | -1.16037e-05 | -1.16037e-05 |
| topology_x_energy | near_train_le3_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17895e-05 | -7.02401e-06 | 9.93281e-06 | -0.000390657 | -0.000193735 | 0.611111 | 8 | 28 | 18 | 8 | 0.2 | 0.410256 | -1.15962e-05 | -1.15962e-05 |
| flank_prior | q2_high_s3_low | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17781e-05 | -7.0126e-06 | 9.95693e-06 | -0.00032849 | -0.000104567 | 0.611111 | 8 | 28 | 15 | 4 | 0.125 | 0.282051 | -1.15669e-05 | -1.15669e-05 |
| topology | block_last2 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17763e-05 | -7.01073e-06 | 9.9463e-06 | -0.000355706 | -0.000119018 | 0.666667 | 8 | 28 | 17 | 9 | 0.175 | 0.307692 | -1.1576e-05 | -1.1576e-05 |
| topology | block_edge | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.1768e-05 | -7.00244e-06 | 9.92737e-06 | -0.00037279 | -0.000154634 | 0.638889 | 8 | 28 | 17 | 8 | 0.2 | 0.307692 | -1.15743e-05 | -1.15743e-05 |
| topology_x_energy | near_train_le2_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17649e-05 | -6.99937e-06 | 9.95592e-06 | -0.000366856 | -0.000163075 | 0.583333 | 8 | 28 | 12 | 5 | 0.15 | 0.282051 | -1.15689e-05 | -1.15689e-05 |
| topology_x_energy | block_first2_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17625e-05 | -6.99696e-06 | 9.94862e-06 | -0.000357668 | -0.00014835 | 0.583333 | 8 | 28 | 11 | 5 | 0.125 | 0.25641 | -1.15719e-05 | -1.15719e-05 |
| topology_x_energy | block_second_half_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17618e-05 | -6.99624e-06 | 9.9606e-06 | -0.00037815 | -0.000190876 | 0.638889 | 8 | 28 | 18 | 8 | 0.15 | 0.384615 | -1.15583e-05 | -1.15583e-05 |
| subject_id | id03 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17497e-05 | -6.98418e-06 | 9.91204e-06 | -0.000318783 | -0.000132085 | 0.611111 | 12 | 28 | 3 | 1 | 0.05 | 0.025641 | -1.15418e-05 | -1.15418e-05 |
| topology | near_train_le1 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17471e-05 | -6.98156e-06 | 9.95377e-06 | -0.000369384 | -0.000161017 | 0.611111 | 4 | 28 | 13 | 5 | 0.175 | 0.230769 | -1.15502e-05 | -1.15502e-05 |
| topology_x_energy | short_block_le5_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17467e-05 | -6.98116e-06 | 9.95173e-06 | -0.000340243 | -0.000139161 | 0.611111 | 8 | 28 | 7 | 3 | 0.075 | 0.153846 | -1.1543e-05 | -1.1543e-05 |
| subject_id | id01 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.1738e-05 | -6.97248e-06 | 9.97129e-06 | -0.000312682 | -0.000124763 | 0.583333 | 8 | 28 | 8 | 1 | 0.05 | 0.153846 | -1.15228e-05 | -1.15228e-05 |
| subject_id | id08 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17342e-05 | -6.9687e-06 | 9.95046e-06 | -0.00032979 | -0.000116387 | 0.611111 | 8 | 28 | 5 | 1 | 0.075 | 0.0769231 | -1.15256e-05 | -1.15256e-05 |
| subject_id | id04 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17249e-05 | -6.95932e-06 | 9.97129e-06 | -0.000320133 | -0.000104567 | 0.583333 | 4 | 28 | 9 | 1 | 0.1 | 0.179487 | -1.15173e-05 | -1.15173e-05 |
| subject_id | id09 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17203e-05 | -6.95476e-06 | 9.97129e-06 | -0.000325075 | -0.000104567 | 0.611111 | 8 | 28 | 3 | 1 | 0.05 | 0.025641 | -1.15108e-05 | -1.15108e-05 |
| topology_x_energy | block_last2_energy_top50 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17181e-05 | -6.95253e-06 | 9.97129e-06 | -0.000323317 | -0.000116786 | 0.583333 | 4 | 28 | 9 | 6 | 0.05 | 0.230769 | -1.15101e-05 | -1.15101e-05 |
| subject_id | id02 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17109e-05 | -6.9454e-06 | 9.97129e-06 | -0.000312682 | -0.000104567 | 0.583333 | 12 | 28 | 7 | 1 | 0 | 0.179487 | -1.15031e-05 | -1.15031e-05 |
| subject_id | id05 | q2_local_s3_full | 36 | 18 | 18 | 36 | 0 | 0 | -1.17109e-05 | -6.9454e-06 | 9.97129e-06 | -0.000312682 | -0.000104567 | 0.583333 | 12 | 28 | 2 | 1 | 0 | 0.0512821 | -1.15031e-05 | -1.15031e-05 |
| flank_prior_target | q2_strong_high_s3_strong_low | q2_local_s3_full | 36 | 17 | 17 | 36 | 0 | 0 | -1.19423e-05 | -7.17678e-06 | 9.87562e-06 | -0.000416655 | -0.000251546 | 0.638889 | 8 | 28 | 20 | 8 | 0.375 | 0.153846 | -1.17106e-05 | -1.17106e-05 |
| topology_x_energy | near_train_le1_energy_top50 | q2_local_s3_full | 36 | 17 | 17 | 36 | 0 | 0 | -1.17309e-05 | -6.96534e-06 | 9.97129e-06 | -0.000353291 | -0.000151901 | 0.583333 | 4 | 28 | 7 | 4 | 0.1 | 0.153846 | -1.15248e-05 | -1.15248e-05 |

## Best Rows

| source_name | mask_mode | localization | alpha_q2 | alpha_s3 | dominant_axis | row_count | subjects | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | raw_energy_q_p90_minus_base | strict_gate | deployable_gate | loose_gate | beats_e75_local_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control | identity | both | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | both | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | True | True | True | False |
| control | identity | both | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | both | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 8 | 32 | s3_higher | 72 | 10 | -1.23151e-05 | -7.54959e-06 | 1.25166e-05 | 2 | 3 | -0.0004049 | -0.000212302 | 0.722222 | -0.000130179 | False | False | True | False |
| control | identity | both | 8 | 32 | s3_higher | 72 | 10 | -1.23151e-05 | -7.54959e-06 | 1.25166e-05 | 2 | 3 | -0.0004049 | -0.000212302 | 0.722222 | -0.000130179 | False | False | True | False |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 8 | 32 | s3_higher | 72 | 10 | -1.23151e-05 | -7.54959e-06 | 1.25166e-05 | 2 | 3 | -0.0004049 | -0.000212302 | 0.722222 | -0.000130179 | False | False | True | False |
| flank_prior | has_q2_or_s3_flank | both | 8 | 32 | s3_higher | 72 | 10 | -1.23151e-05 | -7.54959e-06 | 1.25166e-05 | 2 | 3 | -0.0004049 | -0.000212302 | 0.722222 | -0.000130179 | False | False | True | False |
| flank_prior | s3_high | q2_local_s3_full | 8 | 28 | s3_higher | 63 | 10 | -1.23001e-05 | -7.53457e-06 | 1.13343e-05 | 3 | 3 | -0.00035382 | -0.000184353 | 0.694444 | -0.000118576 | True | True | True | False |
| topology | block_inner | q2_local_s3_full | 8 | 28 | s3_higher | 55 | 10 | -1.22937e-05 | -7.52818e-06 | 1.13904e-05 | 3 | 3 | -0.000348241 | -0.000180441 | 0.694444 | -0.000114175 | True | True | True | False |
| flank_prior | has_q2_or_s3_flank | both | 12 | 32 | s3_higher | 72 | 10 | -1.22778e-05 | -7.51226e-06 | 1.25802e-05 | 2 | 3 | -0.000465372 | -0.000271239 | 0.722222 | -0.000160829 | False | False | True | False |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 12 | 32 | s3_higher | 72 | 10 | -1.22778e-05 | -7.51226e-06 | 1.25802e-05 | 2 | 3 | -0.000465372 | -0.000271239 | 0.722222 | -0.000160829 | False | False | True | False |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 12 | 32 | s3_higher | 72 | 10 | -1.22778e-05 | -7.51226e-06 | 1.25802e-05 | 2 | 3 | -0.000465372 | -0.000271239 | 0.722222 | -0.000160829 | False | False | True | False |
| control | identity | both | 12 | 32 | s3_higher | 72 | 10 | -1.22778e-05 | -7.51226e-06 | 1.25802e-05 | 2 | 3 | -0.000465372 | -0.000271239 | 0.722222 | -0.000160829 | False | False | True | False |
| flank_prior | s3_high | q2_local_s3_full | 12 | 28 | s3_higher | 63 | 10 | -1.22616e-05 | -7.49604e-06 | 1.14009e-05 | 3 | 3 | -0.000405012 | -0.000233646 | 0.694444 | -0.000147306 | True | True | True | False |
| topology | block_inner | q2_local_s3_full | 12 | 28 | s3_higher | 55 | 10 | -1.22528e-05 | -7.48727e-06 | 1.14977e-05 | 2 | 3 | -0.000396691 | -0.000228798 | 0.694444 | -0.000140717 | False | False | True | False |
| topology | block_inner | q2_local_s3_full | 8 | 32 | s3_higher | 55 | 10 | -1.22521e-05 | -7.48658e-06 | 1.25266e-05 | 2 | 3 | -0.000380449 | -0.000192958 | 0.694444 | -0.000121846 | False | False | True | False |
| flank_prior | s3_high | q2_local_s3_full | 8 | 32 | s3_higher | 63 | 10 | -1.22458e-05 | -7.48031e-06 | 1.25185e-05 | 2 | 3 | -0.000386028 | -0.000196869 | 0.694444 | -0.000126247 | False | False | True | False |
| topology | block_first_half | q2_local_s3_full | 8 | 28 | s3_higher | 43 | 10 | -1.22451e-05 | -7.47954e-06 | 1.13475e-05 | 3 | 3 | -0.000329533 | -0.000162157 | 0.666667 | -9.25093e-05 | True | True | True | False |
| topology | subject_late_half | q2_local_s3_full | 12 | 28 | s3_higher | 43 | 10 | -1.22407e-05 | -7.47515e-06 | 1.13079e-05 | 3 | 3 | -0.000383805 | -0.000229622 | 0.666667 | -0.000127839 | True | True | True | False |
| subject_prior | s3_high | q2_local_s3_full | 8 | 28 | s3_higher | 44 | 5 | -1.22237e-05 | -7.4582e-06 | 1.13e-05 | 3 | 3 | -0.000337118 | -0.000180928 | 0.638889 | -0.000106283 | True | True | True | False |
| topology | block_inner | q2_local_s3_full | 12 | 32 | s3_higher | 55 | 10 | -1.2221e-05 | -7.45545e-06 | 1.26013e-05 | 2 | 3 | -0.000428899 | -0.000240602 | 0.694444 | -0.000148388 | False | False | True | False |
| topology | block_first_half | q2_local_s3_full | 12 | 28 | s3_higher | 43 | 10 | -1.22208e-05 | -7.45528e-06 | 1.14027e-05 | 3 | 3 | -0.000368837 | -0.000201236 | 0.694444 | -0.00011006 | True | True | True | False |
| subject_prior | s3_high | q2_local_s3_full | 12 | 28 | s3_higher | 44 | 5 | -1.22202e-05 | -7.45465e-06 | 1.13083e-05 | 3 | 3 | -0.000380278 | -0.000227787 | 0.638889 | -0.000128956 | True | True | True | False |
| topology | subject_late_half | q2_local_s3_full | 8 | 28 | s3_higher | 43 | 10 | -1.2215e-05 | -7.4495e-06 | 1.13453e-05 | 3 | 3 | -0.000339475 | -0.000182347 | 0.666667 | -0.000105539 | True | True | True | False |
| flank_prior | s3_high | q2_local_s3_full | 12 | 32 | s3_higher | 63 | 10 | -1.22126e-05 | -7.44707e-06 | 1.25559e-05 | 2 | 3 | -0.000437221 | -0.000246235 | 0.694444 | -0.000154976 | False | False | True | False |

## Best Deployable Rows

| source_name | mask_mode | localization | alpha_q2 | alpha_s3 | dominant_axis | row_count | subjects | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | raw_energy_q_p90_minus_base | beats_e75_local_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control | identity | both | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| flank_prior | has_q2_or_s3_flank | both | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 8 | 28 | s3_higher | 72 | 10 | -1.23676e-05 | -7.6021e-06 | 1.13299e-05 | 3 | 3 | -0.000372692 | -0.000200351 | 0.722222 | -0.000122508 | False |
| control | identity | both | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | False |
| flank_prior | has_q2_or_s3_flank | both | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | False |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | False |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 12 | 28 | s3_higher | 72 | 10 | -1.23248e-05 | -7.55932e-06 | 1.14286e-05 | 3 | 3 | -0.000433163 | -0.000259239 | 0.722222 | -0.000153158 | False |
| flank_prior | s3_high | q2_local_s3_full | 8 | 28 | s3_higher | 63 | 10 | -1.23001e-05 | -7.53457e-06 | 1.13343e-05 | 3 | 3 | -0.00035382 | -0.000184353 | 0.694444 | -0.000118576 | False |
| topology | block_inner | q2_local_s3_full | 8 | 28 | s3_higher | 55 | 10 | -1.22937e-05 | -7.52818e-06 | 1.13904e-05 | 3 | 3 | -0.000348241 | -0.000180441 | 0.694444 | -0.000114175 | False |
| flank_prior | s3_high | q2_local_s3_full | 12 | 28 | s3_higher | 63 | 10 | -1.22616e-05 | -7.49604e-06 | 1.14009e-05 | 3 | 3 | -0.000405012 | -0.000233646 | 0.694444 | -0.000147306 | False |
| topology | block_first_half | q2_local_s3_full | 8 | 28 | s3_higher | 43 | 10 | -1.22451e-05 | -7.47954e-06 | 1.13475e-05 | 3 | 3 | -0.000329533 | -0.000162157 | 0.666667 | -9.25093e-05 | False |
| topology | subject_late_half | q2_local_s3_full | 12 | 28 | s3_higher | 43 | 10 | -1.22407e-05 | -7.47515e-06 | 1.13079e-05 | 3 | 3 | -0.000383805 | -0.000229622 | 0.666667 | -0.000127839 | False |
| subject_prior | s3_high | q2_local_s3_full | 8 | 28 | s3_higher | 44 | 5 | -1.22237e-05 | -7.4582e-06 | 1.13e-05 | 3 | 3 | -0.000337118 | -0.000180928 | 0.638889 | -0.000106283 | False |
| topology | block_first_half | q2_local_s3_full | 12 | 28 | s3_higher | 43 | 10 | -1.22208e-05 | -7.45528e-06 | 1.14027e-05 | 3 | 3 | -0.000368837 | -0.000201236 | 0.694444 | -0.00011006 | False |
| subject_prior | s3_high | q2_local_s3_full | 12 | 28 | s3_higher | 44 | 5 | -1.22202e-05 | -7.45465e-06 | 1.13083e-05 | 3 | 3 | -0.000380278 | -0.000227787 | 0.638889 | -0.000128956 | False |
| topology | subject_late_half | q2_local_s3_full | 8 | 28 | s3_higher | 43 | 10 | -1.2215e-05 | -7.4495e-06 | 1.13453e-05 | 3 | 3 | -0.000339475 | -0.000182347 | 0.666667 | -0.000105539 | False |
| subject_prior_target | q2_low_s3_high | q2_local_s3_full | 8 | 28 | s3_higher | 46 | 6 | -1.22004e-05 | -7.43489e-06 | 1.12813e-05 | 3 | 3 | -0.000340452 | -0.000165935 | 0.638889 | -0.000107038 | False |
| subject_prior | q2_low | q2_local_s3_full | 8 | 28 | s3_higher | 40 | 5 | -1.22004e-05 | -7.43489e-06 | 1.12813e-05 | 3 | 3 | -0.000340452 | -0.000165935 | 0.638889 | -0.000107038 | False |
| subject_prior | q2_low | q2_local_s3_full | 12 | 28 | s3_higher | 40 | 5 | -1.21792e-05 | -7.41363e-06 | 1.12968e-05 | 3 | 3 | -0.000385251 | -0.000205893 | 0.638889 | -0.000130081 | False |
| subject_prior_target | q2_low_s3_high | q2_local_s3_full | 12 | 28 | s3_higher | 46 | 6 | -1.21792e-05 | -7.41363e-06 | 1.12968e-05 | 3 | 3 | -0.000385251 | -0.000205893 | 0.638889 | -0.000130081 | False |
| control | identity | both | 4 | 28 | s3_higher | 72 | 10 | -1.21708e-05 | -7.40525e-06 | 1.14449e-05 | 3 | 3 | -0.000311343 | -0.000140666 | 0.694444 | -9.16068e-05 | False |
| flank_prior | has_q2_or_s3_flank | both | 4 | 28 | s3_higher | 72 | 10 | -1.21708e-05 | -7.40525e-06 | 1.14449e-05 | 3 | 3 | -0.000311343 | -0.000140666 | 0.694444 | -9.16068e-05 | False |
| flank_prior | has_q2_or_s3_flank | q2_local_s3_full | 4 | 28 | s3_higher | 72 | 10 | -1.21708e-05 | -7.40525e-06 | 1.14449e-05 | 3 | 3 | -0.000311343 | -0.000140666 | 0.694444 | -9.16068e-05 | False |
| flank_prior | has_q2_or_s3_flank | s3_local_q2_full | 4 | 28 | s3_higher | 72 | 10 | -1.21708e-05 | -7.40525e-06 | 1.14449e-05 | 3 | 3 | -0.000311343 | -0.000140666 | 0.694444 | -9.16068e-05 | False |
| topology | one_flank_train | q2_local_s3_full | 12 | 28 | s3_higher | 31 | 8 | -1.21629e-05 | -7.39735e-06 | 1.14115e-05 | 3 | 3 | -0.000366739 | -0.000215948 | 0.638889 | -0.000117951 | False |
| flank_prior_target | q2_low_s3_high | q2_local_s3_full | 8 | 28 | s3_higher | 56 | 10 | -1.21593e-05 | -7.39376e-06 | 1.14052e-05 | 3 | 3 | -0.000330133 | -0.000140188 | 0.666667 | -0.000105087 | False |
| flank_prior | q2_low | q2_local_s3_full | 8 | 28 | s3_higher | 38 | 6 | -1.21593e-05 | -7.39376e-06 | 1.14052e-05 | 3 | 3 | -0.000330133 | -0.000140188 | 0.666667 | -0.000105087 | False |
| control | identity | both | 8 | 24 | s3_higher | 72 | 10 | -1.2158e-05 | -7.39243e-06 | 1.04763e-05 | 3 | 3 | -0.000339634 | -0.000187624 | 0.722222 | -0.000114594 | False |
| flank_prior | has_q2_or_s3_flank | both | 8 | 24 | s3_higher | 72 | 10 | -1.2158e-05 | -7.39243e-06 | 1.04763e-05 | 3 | 3 | -0.000339634 | -0.000187624 | 0.722222 | -0.000114594 | False |

## Decision

- H75 is weakened: row/block masks create deployable variants, but none beat E75 local all-combo.
- This probe writes no submission by default. Materialize only if a candidate beats E75 and has a clearer stress profile than E72/E74/E75.

## Outputs

- `analysis_outputs/q2_s3_public_like_rowblock_amplitude_probe_scan.csv`
- `analysis_outputs/q2_s3_public_like_rowblock_amplitude_probe_summary.csv`
- `analysis_outputs/q2_s3_public_like_rowblock_amplitude_probe_mask_summary.csv`
- `analysis_outputs/q2_s3_public_like_rowblock_amplitude_probe_context_summary.csv`
