# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v7 | 0.578181 | 0.001424 | 0.003411 | 0.000000 | 0.001069 | 0.009065 | 0.012777 | 0.003470 | 0.003764 | -0.001909 | 0.000774 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v7 | all | 450 | 0.578181 | 0.003411 | 0.001424 | 0.003411 | 0.005588 |
| hgb_tail_decoder_v7 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v7 | mid_third | 147 | 0.570665 | 0.001069 | -0.000365 | 0.001069 | 0.002475 |
| hgb_tail_decoder_v7 | late_third | 152 | 0.583216 | 0.009065 | 0.003470 | 0.009065 | 0.015218 |
| hgb_tail_decoder_v7 | tail_20pct | 95 | 0.585640 | 0.012777 | 0.003764 | 0.012777 | 0.022497 |

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
| hgb_tail_decoder_v7 | Q1 | 0.651047 | 0.005349 |
| hgb_tail_decoder_v7 | Q2 | 0.631202 | 0.011118 |
| hgb_tail_decoder_v7 | Q3 | 0.568642 | 0.037039 |
| hgb_tail_decoder_v7 | S1 | 0.549735 | 0.000774 |
| hgb_tail_decoder_v7 | S2 | 0.562574 | 0.002717 |
| hgb_tail_decoder_v7 | S3 | 0.525282 | 0.003721 |
| hgb_tail_decoder_v7 | S4 | 0.594033 | 0.002740 |
