# Block OOF diagnostics

- Baseline: `v13b`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v14 | 0.576224 | 0.000003 | 0.000151 | 0.000000 | 0.000130 | 0.000322 | 0.000485 | -0.000038 | 0.000102 | -0.000318 | 0.000000 | True |
| v13b | 0.576376 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v13b | all | 450 | 0.576376 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | mid_third | 147 | 0.569211 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | late_third | 152 | 0.579279 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v13b | tail_20pct | 95 | 0.581343 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v14 | all | 450 | 0.576224 | 0.000151 | 0.000003 | 0.000151 | 0.000301 |
| v14 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v14 | mid_third | 147 | 0.569081 | 0.000130 | -0.000147 | 0.000130 | 0.000402 |
| v14 | late_third | 152 | 0.578957 | 0.000322 | -0.000038 | 0.000322 | 0.000665 |
| v14 | tail_20pct | 95 | 0.580858 | 0.000485 | 0.000102 | 0.000485 | 0.000894 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v13b | Q1 | 0.651047 | 0.000000 |
| v13b | Q2 | 0.625465 | 0.000000 |
| v13b | Q3 | 0.559878 | 0.000000 |
| v13b | S1 | 0.549735 | 0.000000 |
| v13b | S2 | 0.553949 | 0.000000 |
| v13b | S3 | 0.525282 | 0.000000 |
| v13b | S4 | 0.589595 | 0.000000 |
| v14 | Q1 | 0.651047 | 0.000000 |
| v14 | Q2 | 0.625465 | 0.000000 |
| v14 | Q3 | 0.559878 | 0.000000 |
| v14 | S1 | 0.549178 | 0.000558 |
| v14 | S2 | 0.553376 | 0.000573 |
| v14 | S3 | 0.524789 | 0.000493 |
| v14 | S4 | 0.588964 | 0.000630 |
