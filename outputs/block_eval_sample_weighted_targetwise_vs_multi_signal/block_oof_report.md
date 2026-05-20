# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sample_weighted_targetwise | 0.581519 | -0.000375 | 0.000073 | 0.000351 | -0.000088 | -0.000048 | -0.000134 | -0.000860 | -0.001152 | -0.002070 | -0.000333 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| sample_weighted_targetwise | all | 450 | 0.581519 | 0.000073 | -0.000375 | 0.000073 | 0.000535 |
| sample_weighted_targetwise | early_third | 151 | 0.580077 | 0.000351 | -0.000530 | 0.000351 | 0.001216 |
| sample_weighted_targetwise | mid_third | 147 | 0.571823 | -0.000088 | -0.000772 | -0.000088 | 0.000598 |
| sample_weighted_targetwise | late_third | 152 | 0.592329 | -0.000048 | -0.000860 | -0.000048 | 0.000743 |
| sample_weighted_targetwise | tail_20pct | 95 | 0.598551 | -0.000134 | -0.001152 | -0.000134 | 0.000813 |

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
| sample_weighted_targetwise | Q1 | 0.656396 | 0.000000 |
| sample_weighted_targetwise | Q2 | 0.642320 | 0.000000 |
| sample_weighted_targetwise | Q3 | 0.605681 | 0.000000 |
| sample_weighted_targetwise | S1 | 0.550509 | 0.000000 |
| sample_weighted_targetwise | S2 | 0.565290 | 0.000000 |
| sample_weighted_targetwise | S3 | 0.529003 | 0.000000 |
| sample_weighted_targetwise | S4 | 0.597106 | -0.000333 |
