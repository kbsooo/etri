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
| new_tail_decoder_v2 | 0.579118 | 0.576965 | 0.020061 | 0.015283 | 0.020083 | 0.025037 | True |
| new_q3tail_combo | 0.579709 | 0.582972 | 0.014054 | 0.010333 | 0.014084 | 0.017789 | True |
| oldbalanced_plus_q1fastmid | 0.580760 | 0.593290 | 0.003736 | 0.002705 | 0.003747 | 0.004807 | True |
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
| new_q3tail_combo | Q1 | 0.633559 | 0.625125 | 0.004353 |
| new_q3tail_combo | Q2 | 0.639269 | 0.657441 | 0.001273 |
| new_q3tail_combo | Q3 | 0.612541 | 0.557603 | 0.085823 |
| new_q3tail_combo | S1 | 0.552632 | 0.570736 | 0.002834 |
| new_q3tail_combo | S2 | 0.529019 | 0.537380 | 0.000000 |
| new_q3tail_combo | S3 | 0.498396 | 0.489247 | 0.000000 |
| new_q3tail_combo | S4 | 0.592548 | 0.643273 | 0.004094 |
| new_tail_decoder_v2 | Q1 | 0.633559 | 0.625125 | 0.004353 |
| new_tail_decoder_v2 | Q2 | 0.636081 | 0.624724 | 0.033990 |
| new_tail_decoder_v2 | Q3 | 0.612541 | 0.557603 | 0.085823 |
| new_tail_decoder_v2 | S1 | 0.552632 | 0.570736 | 0.002834 |
| new_tail_decoder_v2 | S2 | 0.529019 | 0.537380 | 0.000000 |
| new_tail_decoder_v2 | S3 | 0.497446 | 0.479916 | 0.009331 |
| new_tail_decoder_v2 | S4 | 0.592548 | 0.643273 | 0.004094 |
| oldbalanced_plus_q1fastmid | Q1 | 0.633247 | 0.622060 | 0.007418 |
| oldbalanced_plus_q1fastmid | Q2 | 0.639269 | 0.657441 | 0.001273 |
| oldbalanced_plus_q1fastmid | Q3 | 0.620209 | 0.632893 | 0.010534 |
| oldbalanced_plus_q1fastmid | S1 | 0.552632 | 0.570736 | 0.002834 |
| oldbalanced_plus_q1fastmid | S2 | 0.529019 | 0.537380 | 0.000000 |
| oldbalanced_plus_q1fastmid | S3 | 0.498396 | 0.489247 | 0.000000 |
| oldbalanced_plus_q1fastmid | S4 | 0.592548 | 0.643273 | 0.004094 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| new_q3tail_combo | mid | 100 | 0.002566 |
| new_q3tail_combo | late | 116 | 0.005093 |
| new_q3tail_combo | tail_20pct | 22 | 0.026462 |
| new_tail_decoder_v2 | mid | 100 | 0.002451 |
| new_tail_decoder_v2 | late | 116 | 0.007486 |
| new_tail_decoder_v2 | tail_20pct | 22 | 0.039105 |
| oldbalanced_plus_q1fastmid | mid | 100 | 0.002566 |
| oldbalanced_plus_q1fastmid | late | 116 | 0.001016 |
| oldbalanced_plus_q1fastmid | tail_20pct | 22 | 0.004967 |
