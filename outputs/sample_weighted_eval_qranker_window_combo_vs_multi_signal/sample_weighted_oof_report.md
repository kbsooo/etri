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
| qranker_q3q1_s4_q2_s1 | 0.580543 | 0.590240 | 0.006786 | 0.004339 | 0.006820 | 0.009440 | True |
| qranker_q3q1_s4_q2 | 0.580719 | 0.590645 | 0.006381 | 0.003983 | 0.006388 | 0.008977 | True |
| qranker_q3q1_s4 | 0.580759 | 0.590827 | 0.006199 | 0.003779 | 0.006208 | 0.008816 | True |
| qranker_q3tail | 0.581192 | 0.593098 | 0.003928 | 0.001795 | 0.003940 | 0.006199 | True |
| tail_q3_support_s4 | 0.581296 | 0.594981 | 0.002045 | 0.001415 | 0.002056 | 0.002699 | True |
| support_s4w100 | 0.581445 | 0.596441 | 0.000585 | 0.000161 | 0.000590 | 0.001017 | True |
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
| support_s4w100 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| support_s4w100 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| support_s4w100 | Q3 | 0.621282 | 0.643427 | 0.000000 |
| support_s4w100 | S1 | 0.553868 | 0.573569 | 0.000000 |
| support_s4w100 | S2 | 0.529019 | 0.537380 | 0.000000 |
| support_s4w100 | S3 | 0.498396 | 0.489247 | 0.000000 |
| support_s4w100 | S4 | 0.592548 | 0.643273 | 0.004094 |
| tail_q3_support_s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| tail_q3_support_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| tail_q3_support_s4 | Q3 | 0.620241 | 0.633205 | 0.010222 |
| tail_q3_support_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| tail_q3_support_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| tail_q3_support_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| tail_q3_support_s4 | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_q3tail | Q1 | 0.635456 | 0.629477 | 0.000000 |
| qranker_q3tail | Q2 | 0.639543 | 0.658715 | 0.000000 |
| qranker_q3tail | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3tail | S1 | 0.553868 | 0.573569 | 0.000000 |
| qranker_q3tail | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3tail | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3tail | S4 | 0.593582 | 0.647367 | 0.000000 |
| qranker_q3q1_s4 | Q1 | 0.633454 | 0.617669 | 0.011808 |
| qranker_q3q1_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| qranker_q3q1_s4 | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3q1_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| qranker_q3q1_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3q1_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3q1_s4 | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_q3q1_s4_q2 | Q1 | 0.633454 | 0.617669 | 0.011808 |
| qranker_q3q1_s4_q2 | Q2 | 0.639269 | 0.657441 | 0.001273 |
| qranker_q3q1_s4_q2 | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3q1_s4_q2 | S1 | 0.553868 | 0.573569 | 0.000000 |
| qranker_q3q1_s4_q2 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3q1_s4_q2 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3q1_s4_q2 | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_q3q1_s4_q2_s1 | Q1 | 0.633454 | 0.617669 | 0.011808 |
| qranker_q3q1_s4_q2_s1 | Q2 | 0.639269 | 0.657441 | 0.001273 |
| qranker_q3q1_s4_q2_s1 | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_q3q1_s4_q2_s1 | S1 | 0.552632 | 0.570736 | 0.002834 |
| qranker_q3q1_s4_q2_s1 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_q3q1_s4_q2_s1 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_q3q1_s4_q2_s1 | S4 | 0.592548 | 0.643273 | 0.004094 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| support_s4w100 | mid | 100 | 0.000514 |
| support_s4w100 | late | 116 | 0.000130 |
| support_s4w100 | tail_20pct | 22 | 0.000669 |
| tail_q3_support_s4 | mid | 100 | 0.000514 |
| tail_q3_support_s4 | late | 116 | 0.000706 |
| tail_q3_support_s4 | tail_20pct | 22 | 0.003711 |
| qranker_q3tail | mid | 100 | 0.000000 |
| qranker_q3tail | late | 116 | 0.001552 |
| qranker_q3tail | tail_20pct | 22 | 0.008183 |
| qranker_q3q1_s4 | mid | 100 | 0.001337 |
| qranker_q3q1_s4 | late | 116 | 0.002081 |
| qranker_q3q1_s4 | tail_20pct | 22 | 0.011654 |
| qranker_q3q1_s4_q2 | mid | 100 | 0.001453 |
| qranker_q3q1_s4_q2 | late | 116 | 0.002134 |
| qranker_q3q1_s4_q2 | tail_20pct | 22 | 0.011904 |
| qranker_q3q1_s4_q2_s1 | mid | 100 | 0.002227 |
| qranker_q3q1_s4_q2_s1 | late | 116 | 0.002151 |
| qranker_q3q1_s4_q2_s1 | tail_20pct | 22 | 0.011904 |
