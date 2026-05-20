# Block OOF diagnostics

- Baseline: `v33a`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v34a | 0.570913 | -0.000149 | 0.000106 | 0.000000 | -0.000020 | 0.000333 | 0.000141 | -0.000101 | -0.000121 | -0.000502 | 0.000000 | False |
| v33a | 0.571019 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v33a | all | 450 | 0.571019 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33a | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33a | mid_third | 147 | 0.563370 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33a | late_third | 152 | 0.569128 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v33a | tail_20pct | 95 | 0.567546 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | all | 450 | 0.570913 | 0.000106 | -0.000149 | 0.000106 | 0.000357 |
| v34a | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | mid_third | 147 | 0.563390 | -0.000020 | -0.000654 | -0.000020 | 0.000601 |
| v34a | late_third | 152 | 0.568796 | 0.000333 | -0.000101 | 0.000333 | 0.000765 |
| v34a | tail_20pct | 95 | 0.567406 | 0.000141 | -0.000121 | 0.000141 | 0.000431 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v33a | Q1 | 0.647814 | 0.000000 |
| v33a | Q2 | 0.615742 | 0.000000 |
| v33a | Q3 | 0.538100 | 0.000000 |
| v33a | S1 | 0.543891 | 0.000000 |
| v33a | S2 | 0.550381 | 0.000000 |
| v33a | S3 | 0.515956 | 0.000000 |
| v33a | S4 | 0.572014 | 0.000000 |
| v34a | Q1 | 0.647814 | 0.000000 |
| v34a | Q2 | 0.615742 | 0.000000 |
| v34a | Q3 | 0.535772 | 0.002328 |
| v34a | S1 | 0.543891 | 0.000000 |
| v34a | S2 | 0.550381 | 0.000000 |
| v34a | S3 | 0.515956 | 0.000000 |
| v34a | S4 | 0.572014 | 0.000000 |
