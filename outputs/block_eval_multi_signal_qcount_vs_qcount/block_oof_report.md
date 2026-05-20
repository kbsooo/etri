# Block OOF diagnostics

- Baseline: `block_aware_qcount`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.581592 | 0.000009 | 0.000259 | 0.000586 | 0.000096 | 0.000091 | 0.000135 | -0.000329 | -0.000404 | -0.001124 | -0.000798 | True |
| block_aware_qcount | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | all | 450 | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | early_third | 151 | 0.581015 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | mid_third | 147 | 0.571831 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | late_third | 152 | 0.592373 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | tail_20pct | 95 | 0.598552 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | all | 450 | 0.581592 | 0.000259 | 0.000009 | 0.000259 | 0.000502 |
| multi_signal | early_third | 151 | 0.580429 | 0.000586 | 0.000133 | 0.000586 | 0.001028 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000096 | -0.000324 | 0.000096 | 0.000515 |
| multi_signal | late_third | 152 | 0.592282 | 0.000091 | -0.000329 | 0.000091 | 0.000518 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000135 | -0.000404 | 0.000135 | 0.000664 |

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
| multi_signal | Q1 | 0.656396 | -0.000798 |
| multi_signal | Q2 | 0.642320 | 0.000596 |
| multi_signal | Q3 | 0.605681 | 0.000154 |
| multi_signal | S1 | 0.550509 | -0.000111 |
| multi_signal | S2 | 0.565290 | 0.000336 |
| multi_signal | S3 | 0.529003 | -0.000091 |
| multi_signal | S4 | 0.596773 | 0.000553 |
