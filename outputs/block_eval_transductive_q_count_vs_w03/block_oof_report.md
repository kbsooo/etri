# Block OOF diagnostics

- Baseline: `primary_w03`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transductive_q_count | 0.581514 | 0.000049 | 0.002283 | 0.003868 | 0.002975 | 0.000040 | 0.002091 | -0.003874 | -0.002856 | -0.009714 | -0.001791 | False |
| primary_w03 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_w03 | all | 450 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | early_third | 151 | 0.583964 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | mid_third | 147 | 0.574254 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | late_third | 152 | 0.592862 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | tail_20pct | 95 | 0.600527 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| transductive_q_count | all | 450 | 0.581514 | 0.002283 | 0.000049 | 0.002283 | 0.004527 |
| transductive_q_count | early_third | 151 | 0.580096 | 0.003868 | 0.000107 | 0.003868 | 0.007645 |
| transductive_q_count | mid_third | 147 | 0.571279 | 0.002975 | -0.001081 | 0.002975 | 0.007175 |
| transductive_q_count | late_third | 152 | 0.592822 | 0.000040 | -0.003874 | 0.000040 | 0.004164 |
| transductive_q_count | tail_20pct | 95 | 0.598437 | 0.002091 | -0.002856 | 0.002091 | 0.007189 |

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
| transductive_q_count | Q1 | 0.656577 | -0.001791 |
| transductive_q_count | Q2 | 0.645222 | 0.000578 |
| transductive_q_count | Q3 | 0.605695 | 0.001490 |
| transductive_q_count | S1 | 0.550398 | 0.000000 |
| transductive_q_count | S2 | 0.565627 | 0.000000 |
| transductive_q_count | S3 | 0.528912 | 0.000000 |
| transductive_q_count | S4 | 0.597326 | 0.000000 |
