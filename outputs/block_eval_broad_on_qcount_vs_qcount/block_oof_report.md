# Block OOF diagnostics

- Baseline: `block_aware_qcount`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| broad_on_qcount | 0.581264 | -0.000514 | 0.000588 | 0.001763 | 0.000967 | -0.000947 | -0.002068 | -0.002903 | -0.004778 | -0.001242 | -0.006965 | False |
| block_aware_qcount | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | all | 450 | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | early_third | 151 | 0.581015 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | mid_third | 147 | 0.571831 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | late_third | 152 | 0.592373 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | tail_20pct | 95 | 0.598552 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| broad_on_qcount | all | 450 | 0.581264 | 0.000588 | -0.000514 | 0.000588 | 0.001671 |
| broad_on_qcount | early_third | 151 | 0.579252 | 0.001763 | -0.000108 | 0.001763 | 0.003699 |
| broad_on_qcount | mid_third | 147 | 0.570864 | 0.000967 | -0.000885 | 0.000967 | 0.002734 |
| broad_on_qcount | late_third | 152 | 0.593320 | -0.000947 | -0.002903 | -0.000947 | 0.000968 |
| broad_on_qcount | tail_20pct | 95 | 0.600620 | -0.002068 | -0.004778 | -0.002068 | 0.000651 |

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
| broad_on_qcount | Q1 | 0.656326 | -0.000728 |
| broad_on_qcount | Q2 | 0.642916 | 0.000000 |
| broad_on_qcount | Q3 | 0.605835 | 0.000000 |
| broad_on_qcount | S1 | 0.557363 | -0.006965 |
| broad_on_qcount | S2 | 0.565627 | 0.000000 |
| broad_on_qcount | S3 | 0.528912 | 0.000000 |
| broad_on_qcount | S4 | 0.596260 | 0.001066 |
