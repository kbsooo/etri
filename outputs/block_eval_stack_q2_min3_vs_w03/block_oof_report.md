# Block OOF diagnostics

- Baseline: `primary_w03`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stack_q2_min3 | 0.583686 | -0.000370 | 0.000111 | 0.000509 | -0.000275 | 0.000090 | -0.000316 | -0.000754 | -0.001487 | -0.001867 | 0.000000 | False |
| primary_w03 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_w03 | all | 450 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | early_third | 151 | 0.583964 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | mid_third | 147 | 0.574254 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | late_third | 152 | 0.592862 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | tail_20pct | 95 | 0.600527 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| stack_q2_min3 | all | 450 | 0.583686 | 0.000111 | -0.000370 | 0.000111 | 0.000596 |
| stack_q2_min3 | early_third | 151 | 0.583455 | 0.000509 | -0.000310 | 0.000509 | 0.001340 |
| stack_q2_min3 | mid_third | 147 | 0.574529 | -0.000275 | -0.001164 | -0.000275 | 0.000624 |
| stack_q2_min3 | late_third | 152 | 0.592772 | 0.000090 | -0.000754 | 0.000090 | 0.000875 |
| stack_q2_min3 | tail_20pct | 95 | 0.600843 | -0.000316 | -0.001487 | -0.000316 | 0.000843 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| primary_w03 | Q1 | 0.654786 | 0.000000 |
| primary_w03 | Q2 | 0.645800 | 0.000000 |
| primary_w03 | Q3 | 0.607185 | 0.000000 |
| primary_w03 | S1 | 0.550398 | 0.000000 |
| primary_w03 | S2 | 0.565627 | 0.000000 |
| primary_w03 | S3 | 0.528912 | 0.000000 |
| primary_w03 | S4 | 0.597326 | 0.000000 |
| stack_q2_min3 | Q1 | 0.654786 | 0.000000 |
| stack_q2_min3 | Q2 | 0.645170 | 0.000630 |
| stack_q2_min3 | Q3 | 0.607185 | 0.000000 |
| stack_q2_min3 | S1 | 0.550398 | 0.000000 |
| stack_q2_min3 | S2 | 0.565627 | 0.000000 |
| stack_q2_min3 | S3 | 0.528912 | 0.000000 |
| stack_q2_min3 | S4 | 0.597326 | 0.000000 |
