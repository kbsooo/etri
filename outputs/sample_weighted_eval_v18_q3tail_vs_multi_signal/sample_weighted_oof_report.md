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
| v18_q3tail | 0.574823 | 0.543055 | 0.053971 | 0.045428 | 0.054001 | 0.063286 | True |
| v17 | 0.574969 | 0.544497 | 0.052529 | 0.044071 | 0.052599 | 0.061629 | True |
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
| v17 | Q1 | 0.632767 | 0.617350 | 0.012127 |
| v17 | Q2 | 0.632101 | 0.585648 | 0.073066 |
| v17 | Q3 | 0.602486 | 0.506174 | 0.137253 |
| v17 | S1 | 0.552444 | 0.568887 | 0.004683 |
| v17 | S2 | 0.524347 | 0.500922 | 0.036458 |
| v17 | S3 | 0.494675 | 0.453861 | 0.035386 |
| v17 | S4 | 0.585965 | 0.578635 | 0.068732 |
| v18_q3tail | Q1 | 0.632767 | 0.617350 | 0.012127 |
| v18_q3tail | Q2 | 0.632101 | 0.585648 | 0.073066 |
| v18_q3tail | Q3 | 0.601458 | 0.496081 | 0.147346 |
| v18_q3tail | S1 | 0.552444 | 0.568887 | 0.004683 |
| v18_q3tail | S2 | 0.524347 | 0.500922 | 0.036458 |
| v18_q3tail | S3 | 0.494675 | 0.453861 | 0.035386 |
| v18_q3tail | S4 | 0.585965 | 0.578635 | 0.068732 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| v17 | mid | 100 | 0.006966 |
| v17 | late | 116 | 0.019687 |
| v17 | tail_20pct | 22 | 0.101498 |
| v18_q3tail | mid | 100 | 0.006966 |
| v18_q3tail | late | 116 | 0.020257 |
| v18_q3tail | tail_20pct | 22 | 0.104502 |
