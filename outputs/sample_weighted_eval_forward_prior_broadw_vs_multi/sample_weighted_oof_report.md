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
| v17 | 0.574969 | 0.544497 | 0.052529 | 0.044071 | 0.052599 | 0.061629 | True |
| portfolio_v17_robust | 0.575829 | 0.546176 | 0.050850 | 0.043055 | 0.050905 | 0.059113 | True |
| forward_prior_broadw | 0.573959 | 0.591282 | 0.005744 | 0.001315 | 0.005751 | 0.010167 | True |
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
| forward_prior_broadw | Q1 | 0.624761 | 0.608359 | 0.021118 |
| forward_prior_broadw | Q2 | 0.609029 | 0.658497 | 0.000217 |
| forward_prior_broadw | Q3 | 0.609057 | 0.624552 | 0.018875 |
| forward_prior_broadw | S1 | 0.553868 | 0.573569 | 0.000000 |
| forward_prior_broadw | S2 | 0.529019 | 0.537380 | 0.000000 |
| forward_prior_broadw | S3 | 0.498396 | 0.489247 | 0.000000 |
| forward_prior_broadw | S4 | 0.593582 | 0.647367 | 0.000000 |
| v17 | Q1 | 0.632767 | 0.617350 | 0.012127 |
| v17 | Q2 | 0.632101 | 0.585648 | 0.073066 |
| v17 | Q3 | 0.602486 | 0.506174 | 0.137253 |
| v17 | S1 | 0.552444 | 0.568887 | 0.004683 |
| v17 | S2 | 0.524347 | 0.500922 | 0.036458 |
| v17 | S3 | 0.494675 | 0.453861 | 0.035386 |
| v17 | S4 | 0.585965 | 0.578635 | 0.068732 |
| portfolio_v17_robust | Q1 | 0.632767 | 0.617350 | 0.012127 |
| portfolio_v17_robust | Q2 | 0.631830 | 0.582987 | 0.075728 |
| portfolio_v17_robust | Q3 | 0.608771 | 0.520594 | 0.122833 |
| portfolio_v17_robust | S1 | 0.552444 | 0.568887 | 0.004683 |
| portfolio_v17_robust | S2 | 0.524347 | 0.500922 | 0.036458 |
| portfolio_v17_robust | S3 | 0.494675 | 0.453861 | 0.035386 |
| portfolio_v17_robust | S4 | 0.585965 | 0.578635 | 0.068732 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| forward_prior_broadw | mid | 100 | 0.006436 |
| forward_prior_broadw | late | 116 | 0.009777 |
| forward_prior_broadw | tail_20pct | 22 | 0.004999 |
| v17 | mid | 100 | 0.006966 |
| v17 | late | 116 | 0.019687 |
| v17 | tail_20pct | 22 | 0.101498 |
| portfolio_v17_robust | mid | 100 | 0.003159 |
| portfolio_v17_robust | late | 116 | 0.019636 |
| portfolio_v17_robust | tail_20pct | 22 | 0.102291 |
