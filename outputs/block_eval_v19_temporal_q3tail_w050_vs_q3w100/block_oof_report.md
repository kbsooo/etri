# Block OOF diagnostics

- Baseline: `q3w100`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v19_temporal_q3tail_w050 | 0.575317 | -0.000157 | 0.000365 | 0.000000 | 0.000000 | 0.001081 | 0.001730 | -0.000427 | -0.000752 | -0.000853 | 0.000000 | False |
| q3w100 | 0.575682 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3w100 | all | 450 | 0.575682 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | mid_third | 147 | 0.570535 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | late_third | 152 | 0.575944 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | tail_20pct | 95 | 0.574033 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v19_temporal_q3tail_w050 | all | 450 | 0.575317 | 0.000365 | -0.000157 | 0.000365 | 0.000910 |
| v19_temporal_q3tail_w050 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v19_temporal_q3tail_w050 | mid_third | 147 | 0.570535 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v19_temporal_q3tail_w050 | late_third | 152 | 0.574863 | 0.001081 | -0.000427 | 0.001081 | 0.002764 |
| v19_temporal_q3tail_w050 | tail_20pct | 95 | 0.572304 | 0.001730 | -0.000752 | 0.001730 | 0.004287 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| q3w100 | Q1 | 0.651047 | 0.000000 |
| q3w100 | Q2 | 0.619485 | 0.000000 |
| q3w100 | Q3 | 0.565599 | 0.000000 |
| q3w100 | S1 | 0.549178 | 0.000000 |
| q3w100 | S2 | 0.553376 | 0.000000 |
| q3w100 | S3 | 0.518377 | 0.000000 |
| q3w100 | S4 | 0.574543 | 0.000000 |
| v19_temporal_q3tail_w050 | Q1 | 0.651047 | 0.000000 |
| v19_temporal_q3tail_w050 | Q2 | 0.619485 | 0.000000 |
| v19_temporal_q3tail_w050 | Q3 | 0.558032 | 0.007567 |
| v19_temporal_q3tail_w050 | S1 | 0.549178 | 0.000000 |
| v19_temporal_q3tail_w050 | S2 | 0.553376 | 0.000000 |
| v19_temporal_q3tail_w050 | S3 | 0.518377 | 0.000000 |
| v19_temporal_q3tail_w050 | S4 | 0.574543 | 0.000000 |
