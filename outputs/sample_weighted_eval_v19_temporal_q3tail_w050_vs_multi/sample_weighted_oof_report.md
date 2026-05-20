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
| v19_temporal_q3tail_w050 | 0.575317 | 0.541150 | 0.055876 | 0.047365 | 0.055897 | 0.064691 | True |
| q3w100 | 0.575682 | 0.544735 | 0.052291 | 0.044368 | 0.052301 | 0.060640 | True |
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
| q3w100 | Q1 | 0.632767 | 0.617350 | 0.012127 |
| q3w100 | Q2 | 0.631830 | 0.582987 | 0.075728 |
| q3w100 | Q3 | 0.607743 | 0.510501 | 0.132926 |
| q3w100 | S1 | 0.552444 | 0.568887 | 0.004683 |
| q3w100 | S2 | 0.524347 | 0.500922 | 0.036458 |
| q3w100 | S3 | 0.494675 | 0.453861 | 0.035386 |
| q3w100 | S4 | 0.585965 | 0.578635 | 0.068732 |
| v19_temporal_q3tail_w050 | Q1 | 0.632767 | 0.617350 | 0.012127 |
| v19_temporal_q3tail_w050 | Q2 | 0.631830 | 0.582987 | 0.075728 |
| v19_temporal_q3tail_w050 | Q3 | 0.605187 | 0.485406 | 0.158021 |
| v19_temporal_q3tail_w050 | S1 | 0.552444 | 0.568887 | 0.004683 |
| v19_temporal_q3tail_w050 | S2 | 0.524347 | 0.500922 | 0.036458 |
| v19_temporal_q3tail_w050 | S3 | 0.494675 | 0.453861 | 0.035386 |
| v19_temporal_q3tail_w050 | S4 | 0.585965 | 0.578635 | 0.068732 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| q3w100 | mid | 100 | 0.003159 |
| q3w100 | late | 116 | 0.020206 |
| q3w100 | tail_20pct | 22 | 0.105294 |
| v19_temporal_q3tail_w050 | mid | 100 | 0.003159 |
| v19_temporal_q3tail_w050 | late | 116 | 0.021622 |
| v19_temporal_q3tail_w050 | tail_20pct | 22 | 0.112763 |
