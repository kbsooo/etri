# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qranker_tail_w065 | 0.580839 | 0.000178 | 0.000753 | 0.000000 | 0.000570 | 0.001678 | 0.002058 | 0.000251 | -0.000195 | -0.000764 | 0.000000 | True |
| qranker_tail_w030 | 0.581031 | 0.000160 | 0.000561 | 0.000000 | 0.000570 | 0.001110 | 0.001150 | 0.000250 | 0.000025 | -0.000764 | 0.000000 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_tail_w030 | all | 450 | 0.581031 | 0.000561 | 0.000160 | 0.000561 | 0.000971 |
| qranker_tail_w030 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_tail_w030 | mid_third | 147 | 0.571165 | 0.000570 | -0.000217 | 0.000570 | 0.001367 |
| qranker_tail_w030 | late_third | 152 | 0.591172 | 0.001110 | 0.000250 | 0.001110 | 0.002045 |
| qranker_tail_w030 | tail_20pct | 95 | 0.597267 | 0.001150 | 0.000025 | 0.001150 | 0.002404 |
| qranker_tail_w065 | all | 450 | 0.580839 | 0.000753 | 0.000178 | 0.000753 | 0.001373 |
| qranker_tail_w065 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qranker_tail_w065 | mid_third | 147 | 0.571165 | 0.000570 | -0.000217 | 0.000570 | 0.001367 |
| qranker_tail_w065 | late_third | 152 | 0.590604 | 0.001678 | 0.000251 | 0.001678 | 0.003296 |
| qranker_tail_w065 | tail_20pct | 95 | 0.596359 | 0.002058 | -0.000195 | 0.002058 | 0.004628 |

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
| qranker_tail_w030 | Q1 | 0.655472 | 0.000924 |
| qranker_tail_w030 | Q2 | 0.642163 | 0.000157 |
| qranker_tail_w030 | Q3 | 0.602504 | 0.003176 |
| qranker_tail_w030 | S1 | 0.549735 | 0.000774 |
| qranker_tail_w030 | S2 | 0.565290 | 0.000000 |
| qranker_tail_w030 | S3 | 0.529003 | 0.000000 |
| qranker_tail_w030 | S4 | 0.594033 | 0.002740 |
| qranker_tail_w065 | Q1 | 0.654473 | 0.001923 |
| qranker_tail_w065 | Q2 | 0.642163 | 0.000157 |
| qranker_tail_w065 | Q3 | 0.599530 | 0.006150 |
| qranker_tail_w065 | S1 | 0.549735 | 0.000774 |
| qranker_tail_w065 | S2 | 0.565290 | 0.000000 |
| qranker_tail_w065 | S3 | 0.529003 | 0.000000 |
| qranker_tail_w065 | S4 | 0.594033 | 0.002740 |
