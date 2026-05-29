# E155 E154 Branch-Body Ablation

## Question

E154 repaired S3 active-boundary actionability, but also added an E144-plus-orthogonal branch body. E155 asks whether that body can be reduced or target-ablated while keeping the all-four health gate and local edge over E144.

## Source

- selected E154 source tag: `e152_efe33e46`.
- selected E154 source pred index: `1275`.
- detected repair cells: `3`.
- repair targets: `S3`.
- E144->E154 body norm: `0.046299048155`.

## Controls

| strategy | all_minus_base | all_four_health | relaxed_structural_tol1e12 | budget_ok | post101_ok | gate_strict_actionable | body_norm_ratio | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control_source_unrepaired | -0.000012258 | False | True | True | True | False | 0.883547042 | -0.000004688 | -0.000002860 | e155_efe33e46 |
| control_e154 | -0.000012158 | True | True | True | True | True | 1.000000000 | -0.000004653 | -0.000002860 | e155_9f2e2e73 |
| control_e144 | -0.000009726 | True | True | True | True | True | 0.000000000 | -0.000003430 | -0.000000000 | e155_d7b4b331 |
| control_e95 | 0.000000000 | False | False | True | False | False | 5.490323977 | 0.000000000 | 0.000000000 | e155_541e3973 |

## Summary

| ablation_family | strategy | rows | all_four_health | e155_submit | best_all_minus_base | best_body_norm_ratio | best_post101_p95 | best_e72_gap | lowest_risk_submit_tag | lowest_risk_submit_body_ratio | lowest_risk_submit_all_minus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target_drop | target_drop | 12 | 12 | 12 | -0.000012158 | 1.000000000 | -0.000004653 | -0.000002860 | e155_10c1b6be | 0.419571767 | -0.000010505 |
| target_only | target_only | 12 | 12 | 7 | -0.000011724 | 0.820839553 | -0.000004315 | 0.000000000 | e155_93cc160e | 0.336807099 | -0.000010215 |
| body_amplitude | branch_body_alpha | 10 | 8 | 6 | -0.000012843 | 1.300000000 | -0.000005024 | -0.000003573 | e155_d27e7965 | 0.250000000 | -0.000010362 |
| source_s3_repair | source_repair_keep | 6 | 2 | 2 | -0.000012258 | 0.883547042 | -0.000004688 | -0.000002860 | e155_9f2e2e73 | 1.000000000 | -0.000012158 |
| control | control_e144 | 1 | 1 | 0 | -0.000009726 | 0.000000000 | -0.000003430 | -0.000000000 |  |  |  |
| control | control_e154 | 1 | 1 | 0 | -0.000012158 | 1.000000000 | -0.000004653 | -0.000002860 |  |  |  |
| control | control_source_unrepaired | 1 | 0 | 0 | -0.000012258 | 0.883547042 | -0.000004688 | -0.000002860 |  |  |  |
| control | control_e95 | 1 | 0 | 0 | 0.000000000 | 5.490323977 | 0.000000000 | 0.000000000 |  |  |  |

## Target Ablation

| ablation_family | target_group | rows | all_four_health | e155_submit | best_all_minus_base | best_body_norm_ratio | best_relaxed | best_budget | best_post101 | best_actionable | best_health_class | best_tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| target_drop | Q2 | 1 | 1 | 1 | -0.000012158 | 1.000000000 | True | True | True | True | all_four | e155_9f2e2e73 |
| target_drop | S1 | 1 | 1 | 1 | -0.000012158 | 1.000000000 | True | True | True | True | all_four | e155_9f2e2e73 |
| target_drop | S4 | 1 | 1 | 1 | -0.000012032 | 0.986943787 | True | True | True | True | all_four | e155_8eef29d1 |
| target_drop | S3 | 1 | 1 | 1 | -0.000012028 | 0.858125292 | True | True | True | True | all_four | e155_183a24f8 |
| target_drop | S2 | 1 | 1 | 1 | -0.000011981 | 0.981499117 | True | True | True | True | all_four | e155_8ea3523b |
| target_drop | S2_S3_S4 | 1 | 1 | 1 | -0.000011724 | 0.820839553 | True | True | True | True | all_four | e155_d5efde72 |
| target_drop | S_all | 1 | 1 | 1 | -0.000011724 | 0.820839553 | True | True | True | True | all_four | e155_d5efde72 |
| target_drop | Q1 | 1 | 1 | 1 | -0.000011659 | 0.941573671 | True | True | True | True | all_four | e155_4fa8341c |
| target_drop | Q3 | 1 | 1 | 1 | -0.000010588 | 0.663069717 | True | True | True | True | all_four | e155_ef4823c5 |
| target_drop | Q3_S3 | 1 | 1 | 1 | -0.000010505 | 0.419571767 | True | True | True | True | all_four | e155_10c1b6be |
| target_drop | Q1_Q3 | 1 | 1 | 1 | -0.000010113 | 0.571158847 | True | True | True | True | all_four | e155_5f072c5a |
| target_drop | Q_all | 1 | 1 | 1 | -0.000010113 | 0.571158847 | True | True | True | True | all_four | e155_5f072c5a |
| target_only | Q1_Q3 | 1 | 1 | 1 | -0.000011724 | 0.820839553 | True | True | True | True | all_four | e155_d5efde72 |
| target_only | Q_all | 1 | 1 | 1 | -0.000011724 | 0.820839553 | True | True | True | True | all_four | e155_d5efde72 |
| target_only | Q3_S3 | 1 | 1 | 1 | -0.000011341 | 0.907722167 | True | True | True | True | all_four | e155_3f9446c3 |
| target_only | Q3 | 1 | 1 | 1 | -0.000011226 | 0.748557646 | True | True | True | True | all_four | e155_ecb2bcca |
| target_only | Q1 | 1 | 1 | 1 | -0.000010215 | 0.336807099 | True | True | True | True | all_four | e155_93cc160e |
| target_only | S2_S3_S4 | 1 | 1 | 1 | -0.000010113 | 0.571158847 | True | True | True | True | all_four | e155_5f072c5a |
| target_only | S_all | 1 | 1 | 1 | -0.000010113 | 0.571158847 | True | True | True | True | all_four | e155_5f072c5a |
| target_only | S2 | 1 | 1 | 0 | -0.000009893 | 0.191466665 | True | True | True | True | all_four | e155_8ecc5d52 |
| target_only | S4 | 1 | 1 | 0 | -0.000009845 | 0.161065085 | True | True | True | True | all_four | e155_bae3c6a0 |
| target_only | S3 | 1 | 1 | 0 | -0.000009820 | 0.513440340 | True | True | True | True | all_four | e155_ce178ec5 |
| target_only | Q2 | 1 | 1 | 0 | -0.000009726 | 0.000000000 | True | True | True | True | all_four | e155_d7b4b331 |
| target_only | S1 | 1 | 1 | 0 | -0.000009726 | 0.000000000 | True | True | True | True | all_four | e155_d7b4b331 |

## Frontier Rows

| strategy | ablation_family | target_group | alpha | keep_factor | all_minus_base | all_four_health | e155_submit | beats_e144_local | relaxed_structural_tol1e12 | budget_ok | post101_ok | gate_strict_actionable | body_norm_ratio | body_cos_e154 | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| branch_body_alpha | body_amplitude | all | 0.250000000 |  | -0.000010362 | True | True | True | True | True | True | True | 0.250000000 | 1.000000000 | -0.000003746 | -0.000001077 | e155_d27e7965 |
| target_only | target_only | Q1 |  |  | -0.000010215 | True | True | True | True | True | True | True | 0.336807099 | 0.336807099 | -0.000003783 | 0.000000000 | e155_93cc160e |
| target_drop | target_drop | Q3_S3 |  |  | -0.000010505 | True | True | True | True | True | True | True | 0.419571767 | 0.419571767 | -0.000004070 | -0.000002860 | e155_10c1b6be |
| branch_body_alpha | body_amplitude | all | 0.500000000 |  | -0.000010979 | True | True | True | True | True | True | True | 0.500000000 | 1.000000000 | -0.000004055 | -0.000001671 | e155_6a410d4c |
| target_drop | target_drop | Q_all |  |  | -0.000010113 | True | True | True | True | True | True | True | 0.571158847 | 0.571158847 | -0.000003893 | -0.000002860 | e155_5f072c5a |
| target_only | target_only | S_all |  |  | -0.000010113 | True | True | True | True | True | True | True | 0.571158847 | 0.571158847 | -0.000003893 | -0.000002860 | e155_5f072c5a |
| target_drop | target_drop | Q1_Q3 |  |  | -0.000010113 | True | True | True | True | True | True | True | 0.571158847 | 0.571158847 | -0.000003893 | -0.000002860 | e155_5f072c5a |
| target_only | target_only | S2_S3_S4 |  |  | -0.000010113 | True | True | True | True | True | True | True | 0.571158847 | 0.571158847 | -0.000003893 | -0.000002860 | e155_5f072c5a |
| branch_body_alpha | body_amplitude | all | 0.650000000 |  | -0.000011338 | True | True | True | True | True | True | True | 0.650000000 | 1.000000000 | -0.000004236 | -0.000002028 | e155_adb5a576 |
| target_drop | target_drop | Q3 |  |  | -0.000010588 | True | True | True | True | True | True | True | 0.663069717 | 0.663069717 | -0.000004099 | -0.000002860 | e155_ef4823c5 |
| target_only | target_only | Q3 |  |  | -0.000011226 | True | True | True | True | True | True | True | 0.748557646 | 0.748557646 | -0.000003960 | 0.000000000 | e155_ecb2bcca |
| branch_body_alpha | body_amplitude | all | 0.750000000 |  | -0.000011574 | True | True | True | True | True | True | True | 0.750000000 | 1.000000000 | -0.000004356 | -0.000002266 | e155_a808986c |
| target_only | target_only | Q_all |  |  | -0.000011724 | True | True | True | True | True | True | True | 0.820839553 | 0.820839553 | -0.000004315 | 0.000000000 | e155_d5efde72 |
| target_drop | target_drop | S_all |  |  | -0.000011724 | True | True | True | True | True | True | True | 0.820839553 | 0.820839553 | -0.000004315 | 0.000000000 | e155_d5efde72 |
| target_only | target_only | Q1_Q3 |  |  | -0.000011724 | True | True | True | True | True | True | True | 0.820839553 | 0.820839553 | -0.000004315 | 0.000000000 | e155_d5efde72 |
| target_drop | target_drop | S2_S3_S4 |  |  | -0.000011724 | True | True | True | True | True | True | True | 0.820839553 | 0.820839553 | -0.000004315 | 0.000000000 | e155_d5efde72 |
| branch_body_alpha | body_amplitude | all | 0.850000000 |  | -0.000011809 | True | True | True | True | True | True | True | 0.850000000 | 1.000000000 | -0.000004475 | -0.000002503 | e155_db69771c |
| target_drop | target_drop | S3 |  |  | -0.000012028 | True | True | True | True | True | True | True | 0.858125292 | 0.858125292 | -0.000004607 | -0.000002860 | e155_183a24f8 |
| target_only | target_only | Q3_S3 |  |  | -0.000011341 | True | True | True | True | True | True | True | 0.907722167 | 0.907722167 | -0.000004000 | 0.000000000 | e155_3f9446c3 |
| target_drop | target_drop | Q1 |  |  | -0.000011659 | True | True | True | True | True | True | True | 0.941573671 | 0.941573671 | -0.000004374 | -0.000002860 | e155_4fa8341c |
| target_drop | target_drop | S2 |  |  | -0.000011981 | True | True | True | True | True | True | True | 0.981499117 | 0.981499117 | -0.000004405 | 0.000000000 | e155_8ea3523b |
| target_drop | target_drop | S4 |  |  | -0.000012032 | True | True | True | True | True | True | True | 0.986943787 | 0.986943787 | -0.000004609 | -0.000002860 | e155_8eef29d1 |
| source_repair_keep | source_s3_repair | repair_mask |  | 0.250000000 | -0.000012158 | True | True | True | True | True | True | True | 1.000000000 | 1.000000000 | -0.000004653 | -0.000002860 | e155_9f2e2e73 |
| branch_body_alpha | body_amplitude | all | 1.000000000 |  | -0.000012158 | True | True | True | True | True | True | True | 1.000000000 | 1.000000000 | -0.000004653 | -0.000002860 | e155_9f2e2e73 |
| target_drop | target_drop | Q2 |  |  | -0.000012158 | True | True | True | True | True | True | True | 1.000000000 | 1.000000000 | -0.000004653 | -0.000002860 | e155_9f2e2e73 |
| target_drop | target_drop | S1 |  |  | -0.000012158 | True | True | True | True | True | True | True | 1.000000000 | 1.000000000 | -0.000004653 | -0.000002860 | e155_9f2e2e73 |
| source_repair_keep | source_s3_repair | repair_mask |  | 0.100000000 | -0.000012134 | True | True | True | True | True | True | True | 1.043572470 | 0.997302279 | -0.000004645 | -0.000002860 | e155_7dda52b2 |
| control_e144 | control |  |  |  | -0.000009726 | True | False | False | True | True | True | True | 0.000000000 | 0.000000000 | -0.000003430 | -0.000000000 | e155_d7b4b331 |
| branch_body_alpha | body_amplitude | all | 0.000000000 |  | -0.000009726 | True | False | False | True | True | True | True | 0.000000000 | 0.000000000 | -0.000003430 | -0.000000000 | e155_d7b4b331 |
| target_only | target_only | Q2 |  |  | -0.000009726 | True | False | False | True | True | True | True | 0.000000000 | 0.000000000 | -0.000003430 | -0.000000000 | e155_d7b4b331 |
| target_only | target_only | S1 |  |  | -0.000009726 | True | False | False | True | True | True | True | 0.000000000 | 0.000000000 | -0.000003430 | -0.000000000 | e155_d7b4b331 |
| branch_body_alpha | body_amplitude | all | 0.100000000 |  | -0.000009982 | True | False | True | True | True | True | True | 0.100000000 | 1.000000000 | -0.000003557 | -0.000000470 | e155_d2b4a85f |
| target_only | target_only | S4 |  |  | -0.000009845 | True | False | True | True | True | True | True | 0.161065085 | 0.161065085 | -0.000003473 | 0.000000000 | e155_bae3c6a0 |
| target_only | target_only | S2 |  |  | -0.000009893 | True | False | True | True | True | True | True | 0.191466665 | 0.191466665 | -0.000003824 | -0.000002860 | e155_8ecc5d52 |
| target_only | target_only | S3 |  |  | -0.000009820 | True | False | True | True | True | True | True | 0.513440340 | 0.513440340 | -0.000003464 | 0.000000000 | e155_ce178ec5 |
| control_e154 | control |  |  |  | -0.000012158 | True | False | True | True | True | True | True | 1.000000000 | 1.000000000 | -0.000004653 | -0.000002860 | e155_9f2e2e73 |
| source_repair_keep | source_s3_repair | repair_mask |  | 1.000000000 | -0.000012258 | False | False | True | True | True | True | False | 0.883547042 | 0.901156307 | -0.000004688 | -0.000002860 | e155_efe33e46 |
| control_source_unrepaired | control |  |  |  | -0.000012258 | False | False | True | True | True | True | False | 0.883547042 | 0.901156307 | -0.000004688 | -0.000002860 | e155_efe33e46 |
| source_repair_keep | source_s3_repair | repair_mask |  | 0.750000000 | -0.000012228 | False | False | True | True | True | True | False | 0.901078210 | 0.959009607 | -0.000004678 | -0.000002860 | e155_8bda5da3 |
| source_repair_keep | source_s3_repair | repair_mask |  | 0.500000000 | -0.000012194 | False | False | True | True | True | True | False | 0.940774582 | 0.990748844 | -0.000004666 | -0.000002860 | e155_7bc4def7 |
| source_repair_keep | source_s3_repair | repair_mask |  | 0.000000000 | -0.000012118 | False | False | True | False | True | True | True | 1.075533121 | 0.992929598 | -0.000004639 | -0.000002860 | e155_c9890c09 |
| branch_body_alpha | body_amplitude | all | 1.150000000 |  | -0.000012503 | False | False | True | False | True | True | True | 1.150000000 | 1.000000000 | -0.000004830 | -0.000003216 | e155_a6e9f2a0 |
| branch_body_alpha | body_amplitude | all | 1.300000000 |  | -0.000012843 | False | False | True | False | True | True | False | 1.300000000 | 1.000000000 | -0.000005024 | -0.000003573 | e155_18752b17 |
| control_e95 | control |  |  |  | 0.000000000 | False | False | False | False | True | False | False | 5.490323977 | 0.048545127 | 0.000000000 | 0.000000000 | e155_541e3973 |

## Decision

Materialized `submission_e155_bodytemp_d27e7965.csv` as a lower-body-ratio all-four E154-family candidate.
