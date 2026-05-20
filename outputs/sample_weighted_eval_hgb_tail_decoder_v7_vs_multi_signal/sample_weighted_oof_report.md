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
| hgb_tail_decoder_v7 | 0.578181 | 0.568905 | 0.028121 | 0.022477 | 0.028219 | 0.034193 | True |
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
| hgb_tail_decoder_v7 | Q1 | 0.632767 | 0.617350 | 0.012127 |
| hgb_tail_decoder_v7 | Q2 | 0.635787 | 0.621843 | 0.036871 |
| hgb_tail_decoder_v7 | Q3 | 0.608771 | 0.520594 | 0.122833 |
| hgb_tail_decoder_v7 | S1 | 0.552632 | 0.570736 | 0.002834 |
| hgb_tail_decoder_v7 | S2 | 0.527620 | 0.531631 | 0.005750 |
| hgb_tail_decoder_v7 | S3 | 0.497139 | 0.476906 | 0.012341 |
| hgb_tail_decoder_v7 | S4 | 0.592548 | 0.643273 | 0.004094 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | mid | 100 | 0.000000 |
| multi_signal | late | 116 | 0.000000 |
| multi_signal | tail_20pct | 22 | 0.000000 |
| hgb_tail_decoder_v7 | mid | 100 | 0.002989 |
| hgb_tail_decoder_v7 | late | 116 | 0.010657 |
| hgb_tail_decoder_v7 | tail_20pct | 22 | 0.055174 |
