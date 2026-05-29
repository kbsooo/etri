# E122 E101 Independent Sensor Boundary Audit

## Question

E121 says the observed E101 small-loss boundary is roughly a greedy top-flip support count of `22` instead of `23`. Did any non-public sensor already identify that boundary, or would a same-line post-E101 gate be public-score fitting?

## Sensor Forecasts

Actual E101-vs-E95 public delta: `+0.0000090362`.

Best expectation-style sensors by absolute error to the observed delta:

| sensor | family | mode | expected_delta_vs_e95 | error_vs_actual_delta | predicted_e116_branch | branch_matches_actual | p_beats_e95 | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw_full_subject_prior_y1 | raw_context_prior | probability_expectation | 0.000008889 | -0.000000148 | small_loss | True |  | expected hard-label delta from E114 raw-context support probabilities |
| flank_conflict_flat | train_flank_prior | probability_expectation | 0.000009521 | 0.000000485 | small_loss | True |  | expected hard-label delta from E118 support probabilities |
| flank_both_distance_beta | train_flank_prior | probability_expectation | 0.000009532 | 0.000000495 | small_loss | True |  | expected hard-label delta from E118 support probabilities |
| flank_subject | train_flank_prior | probability_expectation | 0.000007853 | -0.000001183 | small_loss | True |  | expected hard-label delta from E118 support probabilities |
| raw_subject_prior_y1 | raw_context_prior | probability_expectation | 0.000007853 | -0.000001183 | small_loss | True |  | expected hard-label delta from E114 raw-context support probabilities |
| flank_prev_beta | train_flank_prior | probability_expectation | 0.000010847 | 0.000001811 | small_loss | True |  | expected hard-label delta from E118 support probabilities |
| flank_next_beta | train_flank_prior | probability_expectation | 0.000007156 | -0.000001880 | small_loss | True |  | expected hard-label delta from E118 support probabilities |
| flank_nearest_beta | train_flank_prior | probability_expectation | 0.000005753 | -0.000003283 | small_loss | True |  | expected hard-label delta from E118 support probabilities |
| flank_both_equal_beta | train_flank_prior | probability_expectation | 0.000004720 | -0.000004317 | small_loss | True |  | expected hard-label delta from E118 support probabilities |
| raw_raw_plus_prior_y1 | raw_context_prior | probability_expectation | 0.000014021 | 0.000004985 | small_loss | True |  | expected hard-label delta from E114 raw-context support probabilities |
| raw_validation_gated_raw_y1 | raw_context_prior | probability_expectation | 0.000014457 | 0.000005421 | small_loss | True |  | expected hard-label delta from E114 raw-context support probabilities |
| flank_edge_endpoint_beta | train_flank_prior | probability_expectation | 0.000003014 | -0.000006022 | small_loss | True |  | expected hard-label delta from E118 support probabilities |

Best deterministic `p >= 0.5` support gates:

| sensor | family | expected_delta_vs_e95 | error_vs_actual_delta | predicted_e116_branch | hard_support_cells | hard_support_flip_share | top23_support_rate | s3_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flank_prev_beta | train_flank_prior | 0.000009283 | 0.000000247 | small_loss | 29.000000000 | 0.656364597 | 0.782608696 | 0.564102564 |
| raw_full_subject_prior_y1 | raw_context_prior | 0.000007325 | -0.000001711 | small_loss | 26.000000000 | 0.662714843 | 0.782608696 | 0.589743590 |
| raw_subject_prior_y1 | raw_context_prior | 0.000007325 | -0.000001711 | small_loss | 26.000000000 | 0.662714843 | 0.782608696 | 0.589743590 |
| flank_subject | train_flank_prior | 0.000007325 | -0.000001711 | small_loss | 26.000000000 | 0.662714843 | 0.782608696 | 0.589743590 |
| flank_both_equal_beta | train_flank_prior | 0.000011355 | 0.000002319 | small_loss | 29.000000000 | 0.649646286 | 0.782608696 | 0.538461538 |
| flank_both_distance_beta | train_flank_prior | 0.000003523 | -0.000005513 | small_loss | 29.000000000 | 0.675044591 | 0.782608696 | 0.589743590 |
| flank_nearest_hard085 | train_flank_prior | 0.000001553 | -0.000007483 | tie | 30.000000000 | 0.681432172 | 0.782608696 | 0.589743590 |
| flank_edge_endpoint_beta | train_flank_prior | -0.000008630 | -0.000017667 | small_win | 31.000000000 | 0.714458375 | 0.826086957 | 0.615384615 |
| flank_nearest_beta | train_flank_prior | -0.000008630 | -0.000017667 | small_win | 31.000000000 | 0.714458375 | 0.826086957 | 0.615384615 |
| flank_next_beta | train_flank_prior | -0.000010665 | -0.000019701 | small_win | 29.000000000 | 0.721057305 | 0.826086957 | 0.666666667 |
| raw_global_prior_y1 | raw_context_prior | 0.000030311 | 0.000021274 | large_loss | 25.000000000 | 0.588172545 | 0.695652174 | 0.487179487 |
| flank_global | train_flank_prior | 0.000030311 | 0.000021274 | large_loss | 25.000000000 | 0.588172545 | 0.695652174 | 0.487179487 |

## Critical Boundary Cells

The greedy budget says rank `22` is closest to the observed small loss and rank `23` is the first top-flip support count that would beat E95.

| flip_rank | sub_idx | target | subject_id | hidden_block_id | lifelog_date | pos_bin | flank_conflict | support_label | flip_benefit | delta_if_topk_support_per_all | support_probability_subject | support_probability_edge_endpoint_beta | support_probability_nearest_beta | support_probability_conflict_flat | raw_plus_prior_y1_support_probability | validation_gated_raw_y1_support_probability | posterior_support_mean | posterior_support_std | posterior_support_minus_prior_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18 | 115 | S3 | id05 | id05_b4 | 2024-10-13 | near_edge | False | 0 | 0.014214 | 0.000036 | 0.863636 | 0.909091 | 0.909091 | 0.888683 | 0.891797 | 0.891797 | 0.852292 | 0.125879 | 0.018932 |
| 19 | 47 | S3 | id02 | id02_b4 | 2024-10-03 | interior | False | 1 | 0.013913 | 0.000028 | 0.895833 | 0.930556 | 0.930556 | 0.903846 | 0.902783 | 0.902783 | 0.897111 | 0.042124 | 0.016402 |
| 20 | 22 | S3 | id01 | id01_b4 | 2024-09-10 | interior | False | 0 | 0.013743 | 0.000021 | 0.146341 | 0.097561 | 0.097561 | 0.139373 | 0.392819 | 0.392819 | 0.152556 | 0.116796 | 0.003430 |
| 21 | 158 | S3 | id07 | id07_b2 | 2024-07-19 | interior | False | 1 | 0.013228 | 0.000013 | 0.795918 | 0.863946 | 0.863946 | 0.818913 | 0.842776 | 0.842776 | 0.833855 | 0.035570 | 0.015055 |
| 22 | 49 | S3 | id02 | id02_b4 | 2024-10-05 | interior | False | 0 | 0.013089 | 0.000005 | 0.104167 | 0.069444 | 0.069444 | 0.098039 | 0.145957 | 0.145957 | 0.125880 | 0.125842 | 0.006023 |
| 23 | 147 | S3 | id06 | id06_b10 | 2024-08-20 | near_edge | False | 1 | 0.013068 | -0.000002 | 0.958333 | 0.972222 | 0.972222 | 0.966667 | 0.864418 | 0.864418 | 0.940119 | 0.061845 | 0.015563 |
| 24 | 91 | S3 | id04 | id04_b6 | 2024-09-24 | interior | True | 0 | 0.013052 | -0.000009 | 0.456140 | 0.637427 | 0.637427 | 0.500000 | 0.650002 | 0.650002 | 0.537034 | 0.137302 | 0.001090 |
| 25 | 103 | S3 | id04 | id04_b12 | 2024-10-25 | right_edge | False | 1 | 0.012383 | -0.000017 | 0.543860 | 0.362573 | 0.362573 | 0.326316 | 0.581544 | 0.581544 | 0.378790 | 0.173106 | -0.004663 |
| 26 | 27 | S3 | id02 | id02_b2 | 2024-08-25 | left_edge | False | 1 | 0.011125 | -0.000023 | 0.895833 | 0.930556 | 0.930556 | 0.931973 | 0.884483 | 0.884483 | 0.903180 | 0.054219 | 0.012123 |

Rank `22` support probability under subject / edge / raw / posterior:

- subject: `0.104167`
- edge endpoint: `0.069444`
- raw+prior: `0.145957`
- posterior mean: `0.125880`

Rank `23` support probability under subject / edge / raw / posterior:

- subject: `0.958333`
- edge endpoint: `0.972222`
- raw+prior: `0.864418`
- posterior mean: `0.940119`

## Belief Update

The failed sensor is the local transfer model: it expected E101 mean `-0.000016205` and p95 near the win/tie edge, while public returned `+0.000009036`. The simple train-derived priors are closer to the observed small loss. Subject prior expected `+0.000007853` and raw+prior expected `+0.000014021`.

But this does not create a submission gate. The critical rank `23` cell still has high support under subject/edge/posterior views, and raw is not an independent pro-E101 validator. The visible sensors explain why E101 was not catastrophic, but they do not identify a clean cell to stop before E95 is beaten.

## Decision

Same-line E101 posterior gating remains closed. The strongest current world model is:

> E95 sits on a narrow S3-heavy hard-label boundary. Visible subject/flank priors forecast a small loss better than local tail-transfer, but no non-public sensor identifies the exact high-impact S3 support/adverse cells with enough resolution to justify a new E95-to-E101 submission.

Next highest-information action: either search for a genuinely different non-public sensor of high-impact S3 cell support, or leave the same Q2/S3 rollback line and test a different hidden-structure hypothesis.
