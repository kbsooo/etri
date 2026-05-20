# Block OOF diagnostics

- Baseline: `trp_base`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| trp_plus_gru28_s3tail_w100 | 0.574138 | -0.000042 | 0.000090 | 0.000000 | 0.000000 | 0.000267 | 0.000426 | -0.000121 | -0.000212 | -0.000193 | 0.000000 | False |
| trp_base | 0.574228 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trp_base | all | 450 | 0.574228 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | late_third | 152 | 0.574306 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | tail_20pct | 95 | 0.573442 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | all | 450 | 0.574138 | 0.000090 | -0.000042 | 0.000090 | 0.000264 |
| trp_plus_gru28_s3tail_w100 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | late_third | 152 | 0.574039 | 0.000267 | -0.000121 | 0.000267 | 0.000817 |
| trp_plus_gru28_s3tail_w100 | tail_20pct | 95 | 0.573015 | 0.000426 | -0.000212 | 0.000426 | 0.001269 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| trp_base | Q1 | 0.651214 | 0.000000 |
| trp_base | Q2 | 0.621548 | 0.000000 |
| trp_base | Q3 | 0.564188 | 0.000000 |
| trp_base | S1 | 0.549259 | 0.000000 |
| trp_base | S2 | 0.537785 | 0.000000 |
| trp_base | S3 | 0.519546 | 0.000000 |
| trp_base | S4 | 0.576600 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | Q1 | 0.651214 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | Q2 | 0.621548 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | Q3 | 0.564188 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | S1 | 0.549259 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | S2 | 0.537785 | 0.000000 |
| trp_plus_gru28_s3tail_w100 | S3 | 0.517680 | 0.001866 |
| trp_plus_gru28_s3tail_w100 | S4 | 0.576600 | 0.000000 |
