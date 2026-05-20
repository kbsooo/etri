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
| sample_weighted_targetwise | 0.581519 | 0.596441 | 0.000585 | 0.000161 | 0.000590 | 0.001017 | True |
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
| sample_weighted_targetwise | Q1 | 0.635456 | 0.629477 | 0.000000 |
| sample_weighted_targetwise | Q2 | 0.639543 | 0.658715 | 0.000000 |
| sample_weighted_targetwise | Q3 | 0.621282 | 0.643427 | 0.000000 |
| sample_weighted_targetwise | S1 | 0.553868 | 0.573569 | 0.000000 |
| sample_weighted_targetwise | S2 | 0.529019 | 0.537380 | 0.000000 |
| sample_weighted_targetwise | S3 | 0.498396 | 0.489247 | 0.000000 |
| sample_weighted_targetwise | S4 | 0.593071 | 0.643273 | 0.004094 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| sample_weighted_targetwise | mid | 100 | 0.000514 |
| sample_weighted_targetwise | late | 116 | -0.000446 |
| sample_weighted_targetwise | tail_20pct | 22 | 0.000669 |
