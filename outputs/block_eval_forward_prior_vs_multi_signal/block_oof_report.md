# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| forward_prior | 0.575320 | 0.002773 | 0.006273 | 0.004858 | 0.004611 | 0.009285 | 0.007157 | 0.003332 | 0.000142 | -0.004617 | 0.000000 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| forward_prior | all | 450 | 0.575320 | 0.006273 | 0.002773 | 0.006273 | 0.009850 |
| forward_prior | early_third | 151 | 0.575571 | 0.004858 | -0.001519 | 0.004858 | 0.011421 |
| forward_prior | mid_third | 147 | 0.567123 | 0.004611 | -0.001101 | 0.004611 | 0.010422 |
| forward_prior | late_third | 152 | 0.582997 | 0.009285 | 0.003332 | 0.009285 | 0.015279 |
| forward_prior | tail_20pct | 95 | 0.591260 | 0.007157 | 0.000142 | 0.007157 | 0.014485 |

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
| forward_prior | Q1 | 0.633361 | 0.023035 |
| forward_prior | Q2 | 0.613605 | 0.028715 |
| forward_prior | Q3 | 0.592435 | 0.013245 |
| forward_prior | S1 | 0.550509 | 0.000000 |
| forward_prior | S2 | 0.565290 | 0.000000 |
| forward_prior | S3 | 0.529003 | 0.000000 |
| forward_prior | S4 | 0.596773 | 0.000000 |
