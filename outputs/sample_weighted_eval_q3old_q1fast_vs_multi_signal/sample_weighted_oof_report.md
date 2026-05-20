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
| aggressive_w065 | 0.580839 | 0.592029 | 0.004997 | 0.003483 | 0.005021 | 0.006645 | True |
| q3old_q1fast | 0.580805 | 0.593728 | 0.003298 | 0.002290 | 0.003315 | 0.004382 | True |
| old_balanced_w030 | 0.581031 | 0.593912 | 0.003114 | 0.002257 | 0.003132 | 0.004036 | True |
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
| old_balanced_w030 | Q1 | 0.635144 | 0.626412 | 0.003065 |
| old_balanced_w030 | Q2 | 0.639269 | 0.657441 | 0.001273 |
| old_balanced_w030 | Q3 | 0.620209 | 0.632893 | 0.010534 |
| old_balanced_w030 | S1 | 0.552632 | 0.570736 | 0.002834 |
| old_balanced_w030 | S2 | 0.529019 | 0.537380 | 0.000000 |
| old_balanced_w030 | S3 | 0.498396 | 0.489247 | 0.000000 |
| old_balanced_w030 | S4 | 0.592548 | 0.643273 | 0.004094 |
| q3old_q1fast | Q1 | 0.633559 | 0.625125 | 0.004353 |
| q3old_q1fast | Q2 | 0.639269 | 0.657441 | 0.001273 |
| q3old_q1fast | Q3 | 0.620209 | 0.632893 | 0.010534 |
| q3old_q1fast | S1 | 0.552632 | 0.570736 | 0.002834 |
| q3old_q1fast | S2 | 0.529019 | 0.537380 | 0.000000 |
| q3old_q1fast | S3 | 0.498396 | 0.489247 | 0.000000 |
| q3old_q1fast | S4 | 0.592548 | 0.643273 | 0.004094 |
| aggressive_w065 | Q1 | 0.634807 | 0.623099 | 0.006378 |
| aggressive_w065 | Q2 | 0.639269 | 0.657441 | 0.001273 |
| aggressive_w065 | Q3 | 0.619205 | 0.623030 | 0.020397 |
| aggressive_w065 | S1 | 0.552632 | 0.570736 | 0.002834 |
| aggressive_w065 | S2 | 0.529019 | 0.537380 | 0.000000 |
| aggressive_w065 | S3 | 0.498396 | 0.489247 | 0.000000 |
| aggressive_w065 | S4 | 0.592548 | 0.643273 | 0.004094 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| old_balanced_w030 | mid | 100 | 0.001403 |
| old_balanced_w030 | late | 116 | 0.000967 |
| old_balanced_w030 | tail_20pct | 22 | 0.004967 |
| q3old_q1fast | mid | 100 | 0.002566 |
| q3old_q1fast | late | 116 | 0.000843 |
| q3old_q1fast | tail_20pct | 22 | 0.004055 |
| aggressive_w065 | mid | 100 | 0.001403 |
| aggressive_w065 | late | 116 | 0.001711 |
| aggressive_w065 | tail_20pct | 22 | 0.008888 |
