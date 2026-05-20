# Block OOF diagnostics

- Baseline: `v35a`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v35e | 0.570315 | 0.000012 | 0.000349 | 0.000000 | 0.000186 | 0.000851 | 0.000000 | 0.000208 | 0.000000 | -0.000347 | 0.000000 | True |
| v35a | 0.570663 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v35a | all | 450 | 0.570663 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35a | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35a | mid_third | 147 | 0.562873 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35a | late_third | 152 | 0.568557 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35a | tail_20pct | 95 | 0.567406 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | all | 450 | 0.570315 | 0.000349 | 0.000012 | 0.000349 | 0.000684 |
| v35e | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | mid_third | 147 | 0.562686 | 0.000186 | -0.000591 | 0.000186 | 0.000944 |
| v35e | late_third | 152 | 0.567706 | 0.000851 | 0.000208 | 0.000851 | 0.001543 |
| v35e | tail_20pct | 95 | 0.567406 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v35a | Q1 | 0.647814 | 0.000000 |
| v35a | Q2 | 0.615742 | 0.000000 |
| v35a | Q3 | 0.535772 | 0.000000 |
| v35a | S1 | 0.542220 | 0.000000 |
| v35a | S2 | 0.550381 | 0.000000 |
| v35a | S3 | 0.515956 | 0.000000 |
| v35a | S4 | 0.572014 | 0.000000 |
| v35e | Q1 | 0.647814 | 0.000000 |
| v35e | Q2 | 0.612710 | 0.003032 |
| v35e | Q3 | 0.532843 | 0.002929 |
| v35e | S1 | 0.542220 | 0.000000 |
| v35e | S2 | 0.550381 | 0.000000 |
| v35e | S3 | 0.515956 | 0.000000 |
| v35e | S4 | 0.572014 | 0.000000 |
