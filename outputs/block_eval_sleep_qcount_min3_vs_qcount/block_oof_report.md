# Block OOF diagnostics

- Baseline: `block_aware_qcount`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sleep_qcount_min3 | 0.581558 | -0.000532 | 0.000293 | 0.000940 | 0.000412 | -0.000466 | -0.000999 | -0.001747 | -0.002504 | -0.001493 | -0.003341 | False |
| block_aware_qcount | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | all | 450 | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | early_third | 151 | 0.581015 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | mid_third | 147 | 0.571831 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | late_third | 152 | 0.592373 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | tail_20pct | 95 | 0.598552 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| sleep_qcount_min3 | all | 450 | 0.581558 | 0.000293 | -0.000532 | 0.000293 | 0.001128 |
| sleep_qcount_min3 | early_third | 151 | 0.580074 | 0.000940 | -0.000631 | 0.000940 | 0.002556 |
| sleep_qcount_min3 | mid_third | 147 | 0.571419 | 0.000412 | -0.000909 | 0.000412 | 0.001767 |
| sleep_qcount_min3 | late_third | 152 | 0.592839 | -0.000466 | -0.001747 | -0.000466 | 0.000830 |
| sleep_qcount_min3 | tail_20pct | 95 | 0.599551 | -0.000999 | -0.002504 | -0.000999 | 0.000464 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| block_aware_qcount | Q1 | 0.655598 | 0.000000 |
| block_aware_qcount | Q2 | 0.642916 | 0.000000 |
| block_aware_qcount | Q3 | 0.605835 | 0.000000 |
| block_aware_qcount | S1 | 0.550398 | 0.000000 |
| block_aware_qcount | S2 | 0.565627 | 0.000000 |
| block_aware_qcount | S3 | 0.528912 | 0.000000 |
| block_aware_qcount | S4 | 0.597326 | 0.000000 |
| sleep_qcount_min3 | Q1 | 0.655598 | 0.000000 |
| sleep_qcount_min3 | Q2 | 0.642916 | 0.000000 |
| sleep_qcount_min3 | Q3 | 0.605835 | 0.000000 |
| sleep_qcount_min3 | S1 | 0.553739 | -0.003341 |
| sleep_qcount_min3 | S2 | 0.565627 | 0.000000 |
| sleep_qcount_min3 | S3 | 0.528912 | 0.000000 |
| sleep_qcount_min3 | S4 | 0.597246 | 0.000079 |
