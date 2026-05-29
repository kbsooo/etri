# E146 E144/E143 Tail Prior Audit

## Question

E144 beats E143 locally by only `~1.75e-7`. This audit isolates the cells where E144 differs from E143 and asks whether public-free global/subject/flank priors prefer E144's retained active-tail movement.

## Cell Anatomy

- differing cells: `24`
- rows touched: `24`
- subjects touched: `4`
- edge-like cells: `7`
- flank-conflict cells: `0`
- total flip benefit over differing cells: `0.114000000000`

Target counts:

| target | cells |
| --- | --- |
| S3 | 24 |

Direction counts:

| target | moved_toward_e95 | moved_away_from_e95 | cells |
| --- | --- | --- | --- |
| S3 | False | True | 21 |
| S3 | True | False | 3 |

## Prior Summary

| prior | expected_delta_e144_minus_e143 | expected_delta_total | hard_support_cells | hard_support_flip_share | mean_support_probability | top10_support_rate | edge_support_rate | prefers_e144 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nearest_hard085 | -0.000010294767 | -0.018015842410 | 10 | 0.631578947368 | 0.441666666667 | 0.700000000000 | 0.571428571429 | True |
| both_equal_beta | -0.000006541182 | -0.011447067931 | 10 | 0.631578947368 | 0.425952767471 | 0.700000000000 | 0.571428571429 | True |
| nearest_beta | -0.000005020258 | -0.008785451769 | 10 | 0.631578947368 | 0.422375326393 | 0.700000000000 | 0.571428571429 | True |
| edge_endpoint_beta | -0.000005020258 | -0.008785451769 | 10 | 0.631578947368 | 0.422375326393 | 0.700000000000 | 0.571428571429 | True |
| global | -0.000004480164 | -0.007840286855 | 10 | 0.508771929825 | 0.472962962963 | 0.600000000000 | 0.428571428571 | True |
| both_distance_beta | -0.000003693019 | -0.006462783312 | 10 | 0.631578947368 | 0.436641380183 | 0.700000000000 | 0.571428571429 | True |
| conflict_flat | -0.000003693019 | -0.006462783312 | 10 | 0.631578947368 | 0.436641380183 | 0.700000000000 | 0.571428571429 | True |
| next_beta | -0.000002942812 | -0.005149921424 | 10 | 0.631578947368 | 0.430018774175 | 0.700000000000 | 0.571428571429 | True |
| prev_beta | -0.000001993560 | -0.003488730602 | 10 | 0.631578947368 | 0.432527229969 | 0.700000000000 | 0.571428571429 | True |
| subject | -0.000001097289 | -0.001920256449 | 9 | 0.359649122807 | 0.425229656256 | 0.600000000000 | 0.285714285714 | True |

## Prior Simulation

| prior | sim_mean_delta_e144_minus_e143 | sim_p05 | sim_p50 | sim_p95 | p_e144_beats_e143 | support_cells_mean | support_flip_share_mean | top10_support_rate | edge_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nearest_hard085 | -0.000010288504 | -0.000018009053 | -0.000012866196 | 0.000003133804 | 0.925720000000 | 10.600780000000 | 0.592009122807 | 0.640018000000 | 0.550039285714 |
| both_equal_beta | -0.000006556361 | -0.000018009053 | -0.000006580481 | 0.000006562376 | 0.804815000000 | 10.226220000000 | 0.534717456140 | 0.618140500000 | 0.481399285714 |
| nearest_beta | -0.000005029136 | -0.000018009053 | -0.000004866196 | 0.000008276661 | 0.734130000000 | 10.139615000000 | 0.511273201754 | 0.606344000000 | 0.456324285714 |
| edge_endpoint_beta | -0.000004975456 | -0.000018009053 | -0.000004866196 | 0.000008276661 | 0.731115000000 | 10.133805000000 | 0.510449166667 | 0.605846000000 | 0.456181428571 |
| global | -0.000004491750 | -0.000019723339 | -0.000004866196 | 0.000011133804 | 0.696435000000 | 11.353890000000 | 0.503023859649 | 0.532688000000 | 0.476713571429 |
| both_distance_beta | -0.000003706567 | -0.000018009053 | -0.000004866196 | 0.000011133804 | 0.659925000000 | 10.483660000000 | 0.490970614035 | 0.585232500000 | 0.456627142857 |
| conflict_flat | -0.000003679639 | -0.000018009053 | -0.000004866196 | 0.000011133804 | 0.657815000000 | 10.481205000000 | 0.490557236842 | 0.585326000000 | 0.456055000000 |
| next_beta | -0.000002924176 | -0.000018009053 | -0.000003151910 | 0.000012848090 | 0.626700000000 | 10.317135000000 | 0.478960219298 | 0.578388000000 | 0.429865714286 |
| prev_beta | -0.000001985521 | -0.000016294767 | -0.000003151910 | 0.000012848090 | 0.580845000000 | 10.375320000000 | 0.464551052632 | 0.567246000000 | 0.427740714286 |
| subject | -0.000001090633 | -0.000016294767 | -0.000001437624 | 0.000014562376 | 0.540545000000 | 10.203535000000 | 0.450813728070 | 0.558659000000 | 0.399294285714 |

## Highest Impact Cells

| sub_idx | subject_id | lifelog_date | target | p_e143 | p_e144 | support_y_for_e144 | flip_benefit | pos_bin | flank_conflict | support_probability_subject | support_probability_edge_endpoint_beta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 248 | id10 | 2024-09-25 00:00:00 | S3 | 0.467567 | 0.463338 | 0 | 0.017000 | near_edge | False | 0.515152 | 0.676768 |
| 64 | id03 | 2024-08-22 00:00:00 | S3 | 0.471066 | 0.475303 | 1 | 0.017000 | interior | False | 0.484848 | 0.656566 |
| 69 | id03 | 2024-08-28 00:00:00 | S3 | 0.386129 | 0.390166 | 1 | 0.017000 | right_edge | False | 0.484848 | 0.656566 |
| 155 | id07 | 2024-07-16 00:00:00 | S3 | 0.789680 | 0.790178 | 1 | 0.003000 | interior | False | 0.795918 | 0.863946 |
| 58 | id02 | 2024-10-15 00:00:00 | S3 | 0.932948 | 0.932760 | 0 | 0.003000 | right_edge | False | 0.104167 | 0.069444 |
| 176 | id07 | 2024-08-26 00:00:00 | S3 | 0.782941 | 0.783451 | 1 | 0.003000 | interior | False | 0.795918 | 0.863946 |
| 166 | id07 | 2024-07-27 00:00:00 | S3 | 0.825301 | 0.825733 | 1 | 0.003000 | right_edge | False | 0.795918 | 0.863946 |
| 49 | id02 | 2024-10-05 00:00:00 | S3 | 0.801085 | 0.801563 | 1 | 0.003000 | interior | False | 0.895833 | 0.930556 |
| 67 | id03 | 2024-08-26 00:00:00 | S3 | 0.440121 | 0.439382 | 0 | 0.003000 | interior | False | 0.515152 | 0.343434 |
| 162 | id07 | 2024-07-23 00:00:00 | S3 | 0.822406 | 0.821967 | 0 | 0.003000 | interior | False | 0.204082 | 0.136054 |
| 177 | id07 | 2024-08-27 00:00:00 | S3 | 0.805249 | 0.804779 | 0 | 0.003000 | interior | False | 0.204082 | 0.136054 |
| 56 | id02 | 2024-10-13 00:00:00 | S3 | 0.891427 | 0.891137 | 0 | 0.003000 | interior | False | 0.104167 | 0.069444 |

## Interpretation

- Priors preferring E144 over E143: `10/10`.
- Best expected prior: `nearest_hard085` with delta `-0.000010294767`.
- Worst expected prior: `subject` with delta `-0.000001097289`.
- Best simulated prior: `nearest_hard085` with `p_e144_beats_e143=0.925720`.
- Read: independent priors mostly support the retained E144 tail.

## Decision

No submission is created. E144 remains the next public sensor because it passes the pre-registered strict gates. Because the priors support E144, a narrow E144 loss should not automatically promote E143 as a safer expected-score file; it would mainly say that public S3 tail labels are more adverse than visible priors. E143 remains a clean contrast only if the public slot is meant to test fine-tail retention itself.
