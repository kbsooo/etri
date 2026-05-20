# Sample-weighted OOF diagnostics

- Baseline: `multi_signal`
- Weights match train rows to the submission sample panel-position distribution.

## Position bins

| bin | train_frac | sample_frac | weight_ratio |
| --- | --- | --- | --- |
| [0.000,0.333) | 0.520000 | 0.000000 | 0.000000 |
| [0.333,0.667) | 0.226667 | 0.520000 | 2.294118 |
| [0.667,0.800) | 0.204444 | 0.000000 | 0.000000 |
| [0.800,1.000) | 0.048889 | 0.480000 | 9.818182 |

## Candidate summary

| name | uniform_avg_log_loss | weighted_avg_log_loss | weighted_delta_vs_baseline | weighted_p025 | weighted_p500 | weighted_p975 | promote_weighted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qranker_q3q1tail_s4_q2_s1 | 0.580692 | 0.590582 | 0.006444 | 0.004191 | 0.006467 | 0.008856 | True |
| qranker_q3q1tail_s4_q2 | 0.580868 | 0.590987 | 0.006039 | 0.003819 | 0.006051 | 0.008433 | True |
| qranker_q3q1tail_s4 | 0.580908 | 0.591168 | 0.005858 | 0.003624 | 0.005865 | 0.008265 | True |
| qranker_q3tail_s4 | 0.581045 | 0.592513 | 0.004513 | 0.002324 | 0.004543 | 0.006866 | True |
| tail_q3_support_s4 | 0.581296 | 0.594981 | 0.002045 | 0.001415 | 0.002056 | 0.002699 | True |
| multi_signal | 0.581592 | 0.597026 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| multi_signal | Q1 | 0.635456 | 0.629477 | 0.000000 |
| multi_signal | Q2 | 0.639543 | 0.658715 | 0.000000 |
| multi_signal | Q3 | 0.621282 | 0.643427 | 0.000000 |
| multi_signal | S1 | 0.553868 | 0.573569 | 0.000000 |
| multi_signal | S2 | 0.529019 | 0.537380 | 0.000000 |
| multi_signal | S3 | 0.498396 | 0.489247 | 0.000000 |
| multi_signal | S4 | 0.593582 | 0.647367 | 0.000000 |
| tail_q3_support_s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| tail_q3_support_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| tail_q3_support_s4 | Q3 | 0.620241 | 0.633205 | 0.010222 |
| tail_q3_support_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| tail_q3_support_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| tail_q3_support_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| tail_q3_support_s4 | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_q3tail_s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| qranker_q3tail_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| qranker_q3tail_s4 | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3tail_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| qranker_q3tail_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3tail_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3tail_s4 | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_q3q1tail_s4 | Q1 | 0.634497 | 0.620063 | 0.009415 |
| qranker_q3q1tail_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| qranker_q3q1tail_s4 | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3q1tail_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| qranker_q3q1tail_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3q1tail_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3q1tail_s4 | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_q3q1tail_s4_q2 | Q1 | 0.634497 | 0.620063 | 0.009415 |
| qranker_q3q1tail_s4_q2 | Q2 | 0.639269 | 0.657441 | 0.001273 |
| qranker_q3q1tail_s4_q2 | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3q1tail_s4_q2 | S1 | 0.553868 | 0.573569 | 0.000000 |
| qranker_q3q1tail_s4_q2 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3q1tail_s4_q2 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3q1tail_s4_q2 | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_q3q1tail_s4_q2_s1 | Q1 | 0.634497 | 0.620063 | 0.009415 |
| qranker_q3q1tail_s4_q2_s1 | Q2 | 0.639269 | 0.657441 | 0.001273 |
| qranker_q3q1tail_s4_q2_s1 | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3q1tail_s4_q2_s1 | S1 | 0.552632 | 0.570736 | 0.002834 |
| qranker_q3q1tail_s4_q2_s1 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3q1tail_s4_q2_s1 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3q1tail_s4_q2_s1 | S4 | 0.592548 | 0.643273 | 0.004094 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| tail_q3_support_s4 | mid | 100 | 0.000514 |
| tail_q3_support_s4 | late | 116 | 0.000706 |
| tail_q3_support_s4 | tail_20pct | 22 | 0.003711 |
| qranker_q3tail_s4 | mid | 100 | 0.000514 |
| qranker_q3tail_s4 | late | 116 | 0.001681 |
| qranker_q3tail_s4 | tail_20pct | 22 | 0.008852 |
| qranker_q3q1tail_s4 | mid | 100 | 0.000514 |
| qranker_q3q1tail_s4 | late | 116 | 0.002213 |
| qranker_q3q1tail_s4 | tail_20pct | 22 | 0.011654 |
| qranker_q3q1tail_s4_q2 | mid | 100 | 0.000629 |
| qranker_q3q1tail_s4_q2 | late | 116 | 0.002265 |
| qranker_q3q1tail_s4_q2 | tail_20pct | 22 | 0.011904 |
| qranker_q3q1tail_s4_q2_s1 | mid | 100 | 0.001403 |
| qranker_q3q1tail_s4_q2_s1 | late | 116 | 0.002283 |
| qranker_q3q1tail_s4_q2_s1 | tail_20pct | 22 | 0.011904 |
