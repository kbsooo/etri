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
| dloss_q2s4 | 0.581519 | 0.596441 | 0.000585 | 0.000161 | 0.000590 | 0.001017 | True |
| minimax_positive_tail | 0.581830 | 0.596987 | 0.000039 | -0.000200 | 0.000040 | 0.000282 | False |
| qcount | 0.581851 | 0.596995 | 0.000031 | -0.000213 | 0.000032 | 0.000279 | False |
| multi_signal | 0.581592 | 0.597026 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| subj_rate_s124 | 0.581513 | 0.598215 | -0.001189 | -0.001781 | -0.001188 | -0.000594 | False |

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
| qcount | Q1 | 0.635832 | 0.629335 | 0.000142 |
| qcount | Q2 | 0.639767 | 0.657441 | 0.001273 |
| qcount | Q3 | 0.621368 | 0.643460 | -0.000034 |
| qcount | S1 | 0.554273 | 0.573709 | -0.000139 |
| qcount | S2 | 0.529220 | 0.538441 | -0.001060 |
| qcount | S3 | 0.498416 | 0.489487 | -0.000240 |
| qcount | S4 | 0.594084 | 0.647093 | 0.000274 |
| dloss_q2s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| dloss_q2s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| dloss_q2s4 | Q3 | 0.621282 | 0.643427 | 0.000000 |
| dloss_q2s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| dloss_q2s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| dloss_q2s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| dloss_q2s4 | S4 | 0.593071 | 0.643273 | 0.004094 |
| subj_rate_s124 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| subj_rate_s124 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| subj_rate_s124 | Q3 | 0.621282 | 0.643427 | 0.000000 |
| subj_rate_s124 | S1 | 0.553868 | 0.573569 | 0.000000 |
| subj_rate_s124 | S2 | 0.529019 | 0.537380 | 0.000000 |
| subj_rate_s124 | S3 | 0.498396 | 0.489247 | 0.000000 |
| subj_rate_s124 | S4 | 0.593024 | 0.655688 | -0.008322 |
| minimax_positive_tail | Q1 | 0.635790 | 0.629371 | 0.000106 |
| minimax_positive_tail | Q2 | 0.639727 | 0.657399 | 0.001316 |
| minimax_positive_tail | Q3 | 0.621353 | 0.643527 | -0.000100 |
| minimax_positive_tail | S1 | 0.554251 | 0.573700 | -0.000131 |
| minimax_positive_tail | S2 | 0.529209 | 0.538387 | -0.001006 |
| minimax_positive_tail | S3 | 0.498411 | 0.489427 | -0.000180 |
| minimax_positive_tail | S4 | 0.594067 | 0.647099 | 0.000268 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| qcount | mid | 100 | 0.000009 |
| qcount | late | 116 | -0.000191 |
| qcount | tail_20pct | 22 | 0.000055 |
| dloss_q2s4 | mid | 100 | 0.000514 |
| dloss_q2s4 | late | 116 | -0.000446 |
| dloss_q2s4 | tail_20pct | 22 | 0.000669 |
| subj_rate_s124 | mid | 100 | -0.000327 |
| subj_rate_s124 | late | 116 | 0.000662 |
| subj_rate_s124 | tail_20pct | 22 | -0.002222 |
| minimax_positive_tail | mid | 100 | 0.000029 |
| minimax_positive_tail | late | 116 | -0.000183 |
| minimax_positive_tail | tail_20pct | 22 | 0.000050 |
