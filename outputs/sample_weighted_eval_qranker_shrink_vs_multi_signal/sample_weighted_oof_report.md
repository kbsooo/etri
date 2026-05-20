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
| qranker_tail_full | 0.580692 | 0.590582 | 0.006444 | 0.004191 | 0.006467 | 0.008856 | True |
| qranker_tail_w065 | 0.580839 | 0.592029 | 0.004997 | 0.003483 | 0.005021 | 0.006645 | True |
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
| qranker_tail_full | Q1 | 0.634497 | 0.620063 | 0.009415 |
| qranker_tail_full | Q2 | 0.639269 | 0.657441 | 0.001273 |
| qranker_tail_full | Q3 | 0.618482 | 0.615933 | 0.027494 |
| qranker_tail_full | S1 | 0.552632 | 0.570736 | 0.002834 |
| qranker_tail_full | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_tail_full | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_tail_full | S4 | 0.592548 | 0.643273 | 0.004094 |
| qranker_tail_w065 | Q1 | 0.634807 | 0.623099 | 0.006378 |
| qranker_tail_w065 | Q2 | 0.639269 | 0.657441 | 0.001273 |
| qranker_tail_w065 | Q3 | 0.619205 | 0.623030 | 0.020397 |
| qranker_tail_w065 | S1 | 0.552632 | 0.570736 | 0.002834 |
| qranker_tail_w065 | S2 | 0.529019 | 0.537380 | 0.000000 |
| qranker_tail_w065 | S3 | 0.498396 | 0.489247 | 0.000000 |
| qranker_tail_w065 | S4 | 0.592548 | 0.643273 | 0.004094 |
| tail_q3_support_s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| tail_q3_support_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| tail_q3_support_s4 | Q3 | 0.620241 | 0.633205 | 0.010222 |
| tail_q3_support_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| tail_q3_support_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| tail_q3_support_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| tail_q3_support_s4 | S4 | 0.592548 | 0.643273 | 0.004094 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| qranker_tail_full | mid | 100 | 0.001403 |
| qranker_tail_full | late | 116 | 0.002283 |
| qranker_tail_full | tail_20pct | 22 | 0.011904 |
| qranker_tail_w065 | mid | 100 | 0.001403 |
| qranker_tail_w065 | late | 116 | 0.001711 |
| qranker_tail_w065 | tail_20pct | 22 | 0.008888 |
| tail_q3_support_s4 | mid | 100 | 0.000514 |
| tail_q3_support_s4 | late | 116 | 0.000706 |
| tail_q3_support_s4 | tail_20pct | 22 | 0.003711 |
