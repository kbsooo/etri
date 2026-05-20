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
| portfolio_q3tail | 0.575700 | 0.544919 | 0.052107 | 0.044219 | 0.052114 | 0.060448 | True |
| robust_portfolio | 0.575829 | 0.546176 | 0.050850 | 0.042974 | 0.050876 | 0.059026 | True |
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
| robust_portfolio | Q1 | 0.632767 | 0.617350 | 0.012127 |
| robust_portfolio | Q2 | 0.631830 | 0.582987 | 0.075728 |
| robust_portfolio | Q3 | 0.608771 | 0.520594 | 0.122833 |
| robust_portfolio | S1 | 0.552444 | 0.568887 | 0.004683 |
| robust_portfolio | S2 | 0.524347 | 0.500922 | 0.036458 |
| robust_portfolio | S3 | 0.494675 | 0.453861 | 0.035386 |
| robust_portfolio | S4 | 0.585965 | 0.578635 | 0.068732 |
| portfolio_q3tail | Q1 | 0.632767 | 0.617350 | 0.012127 |
| portfolio_q3tail | Q2 | 0.631830 | 0.582987 | 0.075728 |
| portfolio_q3tail | Q3 | 0.607875 | 0.511791 | 0.131636 |
| portfolio_q3tail | S1 | 0.552444 | 0.568887 | 0.004683 |
| portfolio_q3tail | S2 | 0.524347 | 0.500922 | 0.036458 |
| portfolio_q3tail | S3 | 0.494675 | 0.453861 | 0.035386 |
| portfolio_q3tail | S4 | 0.585965 | 0.578635 | 0.068732 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| robust_portfolio | mid | 100 | 0.003159 |
| robust_portfolio | late | 116 | 0.019636 |
| robust_portfolio | tail_20pct | 22 | 0.102291 |
| portfolio_q3tail | mid | 100 | 0.003159 |
| portfolio_q3tail | late | 116 | 0.020133 |
| portfolio_q3tail | tail_20pct | 22 | 0.104910 |
