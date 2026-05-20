# Block OOF diagnostics

- Baseline: `trp_base`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| weather_s4tail_plus_gru_s3tail | 0.573874 | -0.000139 | 0.000354 | 0.000000 | 0.000000 | 0.001047 | 0.001675 | -0.000408 | -0.000632 | -0.000709 | 0.000000 | False |
| trp_base | 0.574228 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| trp_base | all | 450 | 0.574228 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | late_third | 152 | 0.574306 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| trp_base | tail_20pct | 95 | 0.573442 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | all | 450 | 0.573874 | 0.000354 | -0.000139 | 0.000354 | 0.000888 |
| weather_s4tail_plus_gru_s3tail | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | mid_third | 147 | 0.567778 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | late_third | 152 | 0.573259 | 0.001047 | -0.000408 | 0.001047 | 0.002604 |
| weather_s4tail_plus_gru_s3tail | tail_20pct | 95 | 0.571767 | 0.001675 | -0.000632 | 0.001675 | 0.004103 |

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
| weather_s4tail_plus_gru_s3tail | Q1 | 0.651214 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | Q2 | 0.621548 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | Q3 | 0.564188 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | S1 | 0.549259 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | S2 | 0.537785 | 0.000000 |
| weather_s4tail_plus_gru_s3tail | S3 | 0.517680 | 0.001866 |
| weather_s4tail_plus_gru_s3tail | S4 | 0.571137 | 0.005463 |
