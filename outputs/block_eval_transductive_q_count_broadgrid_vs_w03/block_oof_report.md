# Block OOF diagnostics

- Baseline: `primary_w03`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qcount_broadgrid | 0.581703 | -0.000357 | 0.002095 | 0.003482 | 0.002440 | 0.000382 | 0.001706 | -0.003878 | -0.003758 | -0.011010 | 0.000000 | False |
| primary_w03 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| primary_w03 | all | 450 | 0.583798 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | early_third | 151 | 0.583964 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | mid_third | 147 | 0.574254 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | late_third | 152 | 0.592862 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| primary_w03 | tail_20pct | 95 | 0.600527 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| qcount_broadgrid | all | 450 | 0.581703 | 0.002095 | -0.000357 | 0.002095 | 0.004546 |
| qcount_broadgrid | early_third | 151 | 0.580483 | 0.003482 | -0.000730 | 0.003482 | 0.007670 |
| qcount_broadgrid | mid_third | 147 | 0.571814 | 0.002440 | -0.001886 | 0.002440 | 0.006857 |
| qcount_broadgrid | late_third | 152 | 0.592480 | 0.000382 | -0.003878 | 0.000382 | 0.004746 |
| qcount_broadgrid | tail_20pct | 95 | 0.598822 | 0.001706 | -0.003758 | 0.001706 | 0.007263 |

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
| qcount_broadgrid | Q1 | 0.654786 | 0.000000 |
| qcount_broadgrid | Q2 | 0.644786 | 0.001014 |
| qcount_broadgrid | Q3 | 0.605523 | 0.001662 |
| qcount_broadgrid | S1 | 0.550398 | 0.000000 |
| qcount_broadgrid | S2 | 0.565627 | 0.000000 |
| qcount_broadgrid | S3 | 0.528912 | 0.000000 |
| qcount_broadgrid | S4 | 0.597326 | 0.000000 |
