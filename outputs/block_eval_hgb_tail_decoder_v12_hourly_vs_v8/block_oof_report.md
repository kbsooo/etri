# Block OOF diagnostics

- Baseline: `hgb_tail_decoder_v8`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v12_hourly | 0.576672 | 0.000254 | 0.001434 | 0.000000 | 0.001082 | 0.003199 | 0.003713 | 0.000114 | -0.000754 | -0.002334 | 0.000000 | True |
| hgb_tail_decoder_v8 | 0.578106 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v8 | all | 450 | 0.578106 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v8 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v8 | mid_third | 147 | 0.570665 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v8 | late_third | 152 | 0.582996 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v8 | tail_20pct | 95 | 0.585288 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v12_hourly | all | 450 | 0.576672 | 0.001434 | 0.000254 | 0.001434 | 0.002639 |
| hgb_tail_decoder_v12_hourly | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v12_hourly | mid_third | 147 | 0.569583 | 0.001082 | -0.000520 | 0.001082 | 0.002559 |
| hgb_tail_decoder_v12_hourly | late_third | 152 | 0.579797 | 0.003199 | 0.000114 | 0.003199 | 0.006514 |
| hgb_tail_decoder_v12_hourly | tail_20pct | 95 | 0.581575 | 0.003713 | -0.000754 | 0.003713 | 0.008753 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| hgb_tail_decoder_v8 | Q1 | 0.651047 | 0.000000 |
| hgb_tail_decoder_v8 | Q2 | 0.631202 | 0.000000 |
| hgb_tail_decoder_v8 | Q3 | 0.568642 | 0.000000 |
| hgb_tail_decoder_v8 | S1 | 0.549735 | 0.000000 |
| hgb_tail_decoder_v8 | S2 | 0.562574 | 0.000000 |
| hgb_tail_decoder_v8 | S3 | 0.525282 | 0.000000 |
| hgb_tail_decoder_v8 | S4 | 0.592491 | 0.000000 |
| hgb_tail_decoder_v12_hourly | Q1 | 0.651047 | 0.000000 |
| hgb_tail_decoder_v12_hourly | Q2 | 0.625465 | 0.005737 |
| hgb_tail_decoder_v12_hourly | Q3 | 0.562490 | 0.006152 |
| hgb_tail_decoder_v12_hourly | S1 | 0.549735 | 0.000000 |
| hgb_tail_decoder_v12_hourly | S2 | 0.553949 | 0.008625 |
| hgb_tail_decoder_v12_hourly | S3 | 0.525282 | 0.000000 |
| hgb_tail_decoder_v12_hourly | S4 | 0.590610 | 0.001881 |
