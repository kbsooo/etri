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
| master_q3s4 | 0.581569 | 0.595963 | 0.001063 | 0.000236 | 0.001070 | 0.001882 | True |
| support_s4w100 | 0.581445 | 0.596441 | 0.000585 | 0.000161 | 0.000590 | 0.001017 | True |
| master_q1q3s4 | 0.581560 | 0.596782 | 0.000244 | -0.000709 | 0.000260 | 0.001220 | False |
| master_q1q3s1s4 | 0.581437 | 0.596905 | 0.000121 | -0.001030 | 0.000139 | 0.001307 | False |
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
| master_q1q3s1s4 | Q1 | 0.635397 | 0.635210 | -0.005733 |
| master_q1q3s1s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| master_q1q3s1s4 | Q3 | 0.620853 | 0.634608 | 0.008819 |
| master_q1q3s1s4 | S1 | 0.553009 | 0.574431 | -0.000861 |
| master_q1q3s1s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| master_q1q3s1s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| master_q1q3s1s4 | S4 | 0.593846 | 0.648741 | -0.001374 |
| master_q1q3s4 | Q1 | 0.635397 | 0.635210 | -0.005733 |
| master_q1q3s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| master_q1q3s4 | Q3 | 0.620853 | 0.634608 | 0.008819 |
| master_q1q3s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| master_q1q3s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| master_q1q3s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| master_q1q3s4 | S4 | 0.593846 | 0.648741 | -0.001374 |
| master_q3s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| master_q3s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| master_q3s4 | Q3 | 0.620853 | 0.634608 | 0.008819 |
| master_q3s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| master_q3s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| master_q3s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| master_q3s4 | S4 | 0.593846 | 0.648741 | -0.001374 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| support_s4w100 | mid | 100 | 0.000514 |
| support_s4w100 | late | 116 | 0.000130 |
| support_s4w100 | tail_20pct | 22 | 0.000669 |
| master_q1q3s1s4 | mid | 100 | 0.000695 |
| master_q1q3s1s4 | late | 116 | 0.000002 |
| master_q1q3s1s4 | tail_20pct | 22 | -0.000636 |
| master_q1q3s4 | mid | 100 | -0.000079 |
| master_q1q3s4 | late | 116 | 0.000193 |
| master_q1q3s4 | tail_20pct | 22 | 0.000464 |
| master_q3s4 | mid | 100 | -0.000573 |
| master_q3s4 | late | 116 | 0.000586 |
| master_q3s4 | tail_20pct | 22 | 0.002743 |
