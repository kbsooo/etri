# Block OOF diagnostics

- Baseline: `v17`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v18_q3tail | 0.574823 | -0.000100 | 0.000147 | 0.000000 | 0.000000 | 0.000435 | 0.000696 | -0.000279 | -0.000496 | -0.000387 | 0.000000 | False |
| v17 | 0.574969 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v17 | all | 450 | 0.574969 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v17 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v17 | mid_third | 147 | 0.569081 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v17 | late_third | 152 | 0.575241 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v17 | tail_20pct | 95 | 0.574912 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v18_q3tail | all | 450 | 0.574823 | 0.000147 | -0.000100 | 0.000147 | 0.000393 |
| v18_q3tail | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v18_q3tail | mid_third | 147 | 0.569081 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v18_q3tail | late_third | 152 | 0.574806 | 0.000435 | -0.000279 | 0.000435 | 0.001118 |
| v18_q3tail | tail_20pct | 95 | 0.574217 | 0.000696 | -0.000496 | 0.000696 | 0.001840 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v17 | Q1 | 0.651047 | 0.000000 |
| v17 | Q2 | 0.620288 | 0.000000 |
| v17 | Q3 | 0.559878 | 0.000000 |
| v17 | S1 | 0.549178 | 0.000000 |
| v17 | S2 | 0.553376 | 0.000000 |
| v17 | S3 | 0.518377 | 0.000000 |
| v17 | S4 | 0.574543 | 0.000000 |
| v18_q3tail | Q1 | 0.651047 | 0.000000 |
| v18_q3tail | Q2 | 0.620288 | 0.000000 |
| v18_q3tail | Q3 | 0.556835 | 0.003043 |
| v18_q3tail | S1 | 0.549178 | 0.000000 |
| v18_q3tail | S2 | 0.553376 | 0.000000 |
| v18_q3tail | S3 | 0.518377 | 0.000000 |
| v18_q3tail | S4 | 0.574543 | 0.000000 |
