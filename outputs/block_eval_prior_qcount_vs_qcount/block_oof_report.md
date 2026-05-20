# Block OOF diagnostics

- Baseline: `block_aware_qcount`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prior_qcount | 0.581652 | -0.000492 | 0.000199 | 0.000029 | 0.000137 | 0.000426 | 0.000846 | -0.000554 | -0.000447 | -0.000722 | -0.000480 | False |
| block_aware_qcount | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | all | 450 | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | early_third | 151 | 0.581015 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | mid_third | 147 | 0.571831 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | late_third | 152 | 0.592373 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | tail_20pct | 95 | 0.598552 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prior_qcount | all | 450 | 0.581652 | 0.000199 | -0.000492 | 0.000199 | 0.000866 |
| prior_qcount | early_third | 151 | 0.580985 | 0.000029 | -0.001320 | 0.000029 | 0.001286 |
| prior_qcount | mid_third | 147 | 0.571693 | 0.000137 | -0.001012 | 0.000137 | 0.001290 |
| prior_qcount | late_third | 152 | 0.591947 | 0.000426 | -0.000554 | 0.000426 | 0.001395 |
| prior_qcount | tail_20pct | 95 | 0.597706 | 0.000846 | -0.000447 | 0.000846 | 0.002029 |

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
| prior_qcount | Q1 | 0.655598 | 0.000000 |
| prior_qcount | Q2 | 0.642916 | 0.000000 |
| prior_qcount | Q3 | 0.605835 | 0.000000 |
| prior_qcount | S1 | 0.549159 | 0.001239 |
| prior_qcount | S2 | 0.564347 | 0.001279 |
| prior_qcount | S3 | 0.529391 | -0.000480 |
| prior_qcount | S4 | 0.596379 | 0.000947 |
