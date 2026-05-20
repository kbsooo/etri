# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v12_hourly | 0.576672 | 0.002241 | 0.004920 | 0.000000 | 0.002152 | 0.012485 | 0.016842 | 0.005066 | 0.004937 | -0.004433 | 0.000774 | True |
| hgb_tail_decoder_v8 | 0.578106 | 0.001511 | 0.003486 | 0.000000 | 0.001069 | 0.009286 | 0.013130 | 0.003655 | 0.003934 | -0.002099 | 0.000774 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v8 | all | 450 | 0.578106 | 0.003486 | 0.001511 | 0.003486 | 0.005699 |
| hgb_tail_decoder_v8 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v8 | mid_third | 147 | 0.570665 | 0.001069 | -0.000365 | 0.001069 | 0.002475 |
| hgb_tail_decoder_v8 | late_third | 152 | 0.582996 | 0.009286 | 0.003655 | 0.009286 | 0.015637 |
| hgb_tail_decoder_v8 | tail_20pct | 95 | 0.585288 | 0.013130 | 0.003934 | 0.013130 | 0.023048 |
| hgb_tail_decoder_v12_hourly | all | 450 | 0.576672 | 0.004920 | 0.002241 | 0.004920 | 0.007774 |
| hgb_tail_decoder_v12_hourly | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v12_hourly | mid_third | 147 | 0.569583 | 0.002152 | 0.000081 | 0.002152 | 0.004110 |
| hgb_tail_decoder_v12_hourly | late_third | 152 | 0.579797 | 0.012485 | 0.005066 | 0.012485 | 0.020847 |
| hgb_tail_decoder_v12_hourly | tail_20pct | 95 | 0.581575 | 0.016842 | 0.004937 | 0.016842 | 0.030092 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | Q1 | 0.656396 | 0.000000 |
| multi_signal | Q2 | 0.642320 | 0.000000 |
| multi_signal | Q3 | 0.605681 | 0.000000 |
| multi_signal | S1 | 0.550509 | 0.000000 |
| multi_signal | S2 | 0.565290 | 0.000000 |
| multi_signal | S3 | 0.529003 | 0.000000 |
| multi_signal | S4 | 0.596773 | 0.000000 |
| hgb_tail_decoder_v8 | Q1 | 0.651047 | 0.005349 |
| hgb_tail_decoder_v8 | Q2 | 0.631202 | 0.011118 |
| hgb_tail_decoder_v8 | Q3 | 0.568642 | 0.037039 |
| hgb_tail_decoder_v8 | S1 | 0.549735 | 0.000774 |
| hgb_tail_decoder_v8 | S2 | 0.562574 | 0.002717 |
| hgb_tail_decoder_v8 | S3 | 0.525282 | 0.003721 |
| hgb_tail_decoder_v8 | S4 | 0.592491 | 0.004282 |
| hgb_tail_decoder_v12_hourly | Q1 | 0.651047 | 0.005349 |
| hgb_tail_decoder_v12_hourly | Q2 | 0.625465 | 0.016855 |
| hgb_tail_decoder_v12_hourly | Q3 | 0.562490 | 0.043190 |
| hgb_tail_decoder_v12_hourly | S1 | 0.549735 | 0.000774 |
| hgb_tail_decoder_v12_hourly | S2 | 0.553949 | 0.011341 |
| hgb_tail_decoder_v12_hourly | S3 | 0.525282 | 0.003721 |
| hgb_tail_decoder_v12_hourly | S4 | 0.590610 | 0.006163 |
