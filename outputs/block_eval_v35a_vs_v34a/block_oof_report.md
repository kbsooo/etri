# Block OOF diagnostics

- Baseline: `v34a`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v35a | 0.570663 | 0.000002 | 0.000250 | 0.000000 | 0.000517 | 0.000239 | 0.000000 | -0.000220 | 0.000000 | -0.000157 | 0.000000 | True |
| v34a | 0.570913 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v34a | all | 450 | 0.570913 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | mid_third | 147 | 0.563390 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | late_third | 152 | 0.568796 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | tail_20pct | 95 | 0.567406 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35a | all | 450 | 0.570663 | 0.000250 | 0.000002 | 0.000250 | 0.000502 |
| v35a | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35a | mid_third | 147 | 0.562873 | 0.000517 | -0.000049 | 0.000517 | 0.001109 |
| v35a | late_third | 152 | 0.568557 | 0.000239 | -0.000220 | 0.000239 | 0.000732 |
| v35a | tail_20pct | 95 | 0.567406 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v34a | Q1 | 0.647814 | 0.000000 |
| v34a | Q2 | 0.615742 | 0.000000 |
| v34a | Q3 | 0.535772 | 0.000000 |
| v34a | S1 | 0.543891 | 0.000000 |
| v34a | S2 | 0.550381 | 0.000000 |
| v34a | S3 | 0.515956 | 0.000000 |
| v34a | S4 | 0.572014 | 0.000000 |
| v35a | Q1 | 0.647814 | 0.000000 |
| v35a | Q2 | 0.615742 | 0.000000 |
| v35a | Q3 | 0.535772 | 0.000000 |
| v35a | S1 | 0.542220 | 0.001671 |
| v35a | S2 | 0.550381 | 0.000000 |
| v35a | S3 | 0.515956 | 0.000000 |
| v35a | S4 | 0.572014 | 0.000000 |
