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
| tail_q3_support_s4 | 0.581296 | 0.594981 | 0.002045 | 0.001415 | 0.002056 | 0.002699 | True |
| multi_signal | 0.581592 | 0.597026 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| q23_broadgrid | 0.581269 | 0.597039 | -0.000013 | -0.000902 | -0.000006 | 0.000889 | False |
| sleep_s4 | 0.581503 | 0.597216 | -0.000190 | -0.000634 | -0.000194 | 0.000251 | False |
| broad_q1 | 0.581476 | 0.597247 | -0.000221 | -0.000780 | -0.000220 | 0.000358 | False |
| markov_q123 | 0.581304 | 0.598514 | -0.001488 | -0.002370 | -0.001484 | -0.000630 | False |

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
| tail_q3_support_s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| tail_q3_support_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| tail_q3_support_s4 | Q3 | 0.620241 | 0.633205 | 0.010222 |
| tail_q3_support_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| tail_q3_support_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| tail_q3_support_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| tail_q3_support_s4 | S4 | 0.592548 | 0.643273 | 0.004094 |
| q23_broadgrid | Q1 | 0.635456 | 0.629477 | 0.000000 |
| q23_broadgrid | Q2 | 0.637645 | 0.655154 | 0.003561 |
| q23_broadgrid | Q3 | 0.620914 | 0.647082 | -0.003655 |
| q23_broadgrid | S1 | 0.553868 | 0.573569 | 0.000000 |
| q23_broadgrid | S2 | 0.529019 | 0.537380 | 0.000000 |
| q23_broadgrid | S3 | 0.498396 | 0.489247 | 0.000000 |
| q23_broadgrid | S4 | 0.593582 | 0.647367 | 0.000000 |
| markov_q123 | Q1 | 0.634262 | 0.631654 | -0.002177 |
| markov_q123 | Q2 | 0.638845 | 0.666888 | -0.008174 |
| markov_q123 | Q3 | 0.621158 | 0.643494 | -0.000067 |
| markov_q123 | S1 | 0.553868 | 0.573569 | 0.000000 |
| markov_q123 | S2 | 0.529019 | 0.537380 | 0.000000 |
| markov_q123 | S3 | 0.498396 | 0.489247 | 0.000000 |
| markov_q123 | S4 | 0.593582 | 0.647367 | 0.000000 |
| broad_q1 | Q1 | 0.634646 | 0.631026 | -0.001549 |
| broad_q1 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| broad_q1 | Q3 | 0.621282 | 0.643427 | 0.000000 |
| broad_q1 | S1 | 0.553868 | 0.573569 | 0.000000 |
| broad_q1 | S2 | 0.529019 | 0.537380 | 0.000000 |
| broad_q1 | S3 | 0.498396 | 0.489247 | 0.000000 |
| broad_q1 | S4 | 0.593582 | 0.647367 | 0.000000 |
| sleep_s4 | Q1 | 0.635456 | 0.629477 | 0.000000 |
| sleep_s4 | Q2 | 0.639543 | 0.658715 | 0.000000 |
| sleep_s4 | Q3 | 0.621282 | 0.643427 | 0.000000 |
| sleep_s4 | S1 | 0.553868 | 0.573569 | 0.000000 |
| sleep_s4 | S2 | 0.529019 | 0.537380 | 0.000000 |
| sleep_s4 | S3 | 0.498396 | 0.489247 | 0.000000 |
| sleep_s4 | S4 | 0.592957 | 0.648697 | -0.001330 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| tail_q3_support_s4 | mid | 100 | 0.000514 |
| tail_q3_support_s4 | late | 116 | 0.000706 |
| tail_q3_support_s4 | tail_20pct | 22 | 0.003711 |
| q23_broadgrid | mid | 100 | 0.000581 |
| q23_broadgrid | late | 116 | 0.000122 |
| q23_broadgrid | tail_20pct | 22 | -0.000652 |
| markov_q123 | mid | 100 | -0.000642 |
| markov_q123 | late | 116 | -0.000492 |
| markov_q123 | tail_20pct | 22 | -0.002315 |
| broad_q1 | mid | 100 | 0.000686 |
| broad_q1 | late | 116 | -0.000296 |
| broad_q1 | tail_20pct | 22 | -0.001289 |
| sleep_s4 | mid | 100 | 0.000487 |
| sleep_s4 | late | 116 | -0.000115 |
| sleep_s4 | tail_20pct | 22 | -0.000933 |
