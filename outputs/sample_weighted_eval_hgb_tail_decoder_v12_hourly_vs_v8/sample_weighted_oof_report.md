# Sample-weighted OOF diagnostics

- Baseline: `hgb_tail_decoder_v8`
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
| hgb_tail_decoder_v12_hourly | 0.576672 | 0.558987 | 0.009187 | 0.006125 | 0.009185 | 0.012432 | True |
| hgb_tail_decoder_v8 | 0.578106 | 0.568174 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Target scores

| name | target | uniform_log_loss | weighted_log_loss | weighted_delta_vs_baseline |
| --- | --- | --- | --- | --- |
| hgb_tail_decoder_v8 | Q1 | 0.632767 | 0.617350 | 0.000000 |
| hgb_tail_decoder_v8 | Q2 | 0.635787 | 0.621843 | 0.000000 |
| hgb_tail_decoder_v8 | Q3 | 0.608771 | 0.520594 | 0.000000 |
| hgb_tail_decoder_v8 | S1 | 0.552632 | 0.570736 | 0.000000 |
| hgb_tail_decoder_v8 | S2 | 0.527620 | 0.531631 | 0.000000 |
| hgb_tail_decoder_v8 | S3 | 0.497139 | 0.476906 | 0.000000 |
| hgb_tail_decoder_v8 | S4 | 0.592027 | 0.638157 | 0.000000 |
| hgb_tail_decoder_v12_hourly | Q1 | 0.632767 | 0.617350 | 0.000000 |
| hgb_tail_decoder_v12_hourly | Q2 | 0.633849 | 0.602819 | 0.019025 |
| hgb_tail_decoder_v12_hourly | Q3 | 0.604219 | 0.510149 | 0.010444 |
| hgb_tail_decoder_v12_hourly | S1 | 0.552632 | 0.570736 | 0.000000 |
| hgb_tail_decoder_v12_hourly | S2 | 0.524707 | 0.503027 | 0.028603 |
| hgb_tail_decoder_v12_hourly | S3 | 0.497139 | 0.476906 | 0.000000 |
| hgb_tail_decoder_v12_hourly | S4 | 0.591392 | 0.631920 | 0.006237 |

## Block deltas

| name | block | n_rows | delta_vs_baseline |
| --- | --- | --- | --- |
| hgb_tail_decoder_v8 | mid | 100 | 0.000000 |
| hgb_tail_decoder_v8 | late | 116 | 0.000000 |
| hgb_tail_decoder_v8 | tail_20pct | 22 | 0.000000 |
| hgb_tail_decoder_v12_hourly | mid | 100 | 0.002783 |
| hgb_tail_decoder_v12_hourly | late | 116 | 0.003165 |
| hgb_tail_decoder_v12_hourly | tail_20pct | 22 | 0.016031 |
