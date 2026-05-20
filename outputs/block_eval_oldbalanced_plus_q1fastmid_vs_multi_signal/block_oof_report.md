# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oldbalanced_plus_q1fastmid | 0.580760 | 0.000281 | 0.000832 | 0.000000 | 0.000956 | 0.001539 | 0.001150 | 0.000468 | 0.000025 | -0.000489 | 0.000000 | True |
| old_balanced_w030 | 0.581031 | 0.000160 | 0.000561 | 0.000000 | 0.000570 | 0.001110 | 0.001150 | 0.000250 | 0.000025 | -0.000764 | 0.000000 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| old_balanced_w030 | all | 450 | 0.581031 | 0.000561 | 0.000160 | 0.000561 | 0.000971 |
| old_balanced_w030 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| old_balanced_w030 | mid_third | 147 | 0.571165 | 0.000570 | -0.000217 | 0.000570 | 0.001367 |
| old_balanced_w030 | late_third | 152 | 0.591172 | 0.001110 | 0.000250 | 0.001110 | 0.002045 |
| old_balanced_w030 | tail_20pct | 95 | 0.597267 | 0.001150 | 0.000025 | 0.001150 | 0.002404 |
| oldbalanced_plus_q1fastmid | all | 450 | 0.580760 | 0.000832 | 0.000281 | 0.000832 | 0.001419 |
| oldbalanced_plus_q1fastmid | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| oldbalanced_plus_q1fastmid | mid_third | 147 | 0.570779 | 0.000956 | -0.000362 | 0.000956 | 0.002278 |
| oldbalanced_plus_q1fastmid | late_third | 152 | 0.590742 | 0.001539 | 0.000468 | 0.001539 | 0.002645 |
| oldbalanced_plus_q1fastmid | tail_20pct | 95 | 0.597267 | 0.001150 | 0.000025 | 0.001150 | 0.002404 |

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
| old_balanced_w030 | Q1 | 0.655472 | 0.000924 |
| old_balanced_w030 | Q2 | 0.642163 | 0.000157 |
| old_balanced_w030 | Q3 | 0.602504 | 0.003176 |
| old_balanced_w030 | S1 | 0.549735 | 0.000774 |
| old_balanced_w030 | S2 | 0.565290 | 0.000000 |
| old_balanced_w030 | S3 | 0.529003 | 0.000000 |
| old_balanced_w030 | S4 | 0.594033 | 0.002740 |
| oldbalanced_plus_q1fastmid | Q1 | 0.652467 | 0.003929 |
| oldbalanced_plus_q1fastmid | Q2 | 0.642163 | 0.000157 |
| oldbalanced_plus_q1fastmid | Q3 | 0.602504 | 0.003176 |
| oldbalanced_plus_q1fastmid | S1 | 0.549735 | 0.000774 |
| oldbalanced_plus_q1fastmid | S2 | 0.565290 | 0.000000 |
| oldbalanced_plus_q1fastmid | S3 | 0.529003 | 0.000000 |
| oldbalanced_plus_q1fastmid | S4 | 0.594033 | 0.002740 |
