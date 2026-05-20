# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dloss_q2s4 | 0.581519 | -0.000373 | 0.000073 | 0.000351 | -0.000088 | -0.000048 | -0.000134 | -0.000859 | -0.001169 | -0.002070 | -0.000333 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| dloss_q2s4 | all | 450 | 0.581519 | 0.000073 | -0.000373 | 0.000073 | 0.000546 |
| dloss_q2s4 | early_third | 151 | 0.580077 | 0.000351 | -0.000552 | 0.000351 | 0.001197 |
| dloss_q2s4 | mid_third | 147 | 0.571823 | -0.000088 | -0.000797 | -0.000088 | 0.000593 |
| dloss_q2s4 | late_third | 152 | 0.592329 | -0.000048 | -0.000859 | -0.000048 | 0.000743 |
| dloss_q2s4 | tail_20pct | 95 | 0.598551 | -0.000134 | -0.001169 | -0.000134 | 0.000799 |

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
| dloss_q2s4 | Q1 | 0.656396 | 0.000000 |
| dloss_q2s4 | Q2 | 0.642320 | 0.000000 |
| dloss_q2s4 | Q3 | 0.605681 | 0.000000 |
| dloss_q2s4 | S1 | 0.550509 | 0.000000 |
| dloss_q2s4 | S2 | 0.565290 | 0.000000 |
| dloss_q2s4 | S3 | 0.529003 | 0.000000 |
| dloss_q2s4 | S4 | 0.597106 | -0.000333 |
