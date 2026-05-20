# Block OOF diagnostics

- Baseline: `block_aware_qcount`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_on_qcount_min3 | 0.581834 | -0.000181 | 0.000018 | -0.000050 | 0.000013 | 0.000089 | 0.000346 | -0.000304 | -0.000220 | -0.000691 | 0.000000 | False |
| block_aware_qcount | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| block_aware_qcount | all | 450 | 0.581851 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | early_third | 151 | 0.581015 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | mid_third | 147 | 0.571831 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | late_third | 152 | 0.592373 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| block_aware_qcount | tail_20pct | 95 | 0.598552 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_on_qcount_min3 | all | 450 | 0.581834 | 0.000018 | -0.000181 | 0.000018 | 0.000225 |
| graph_on_qcount_min3 | early_third | 151 | 0.581064 | -0.000050 | -0.000298 | -0.000050 | 0.000196 |
| graph_on_qcount_min3 | mid_third | 147 | 0.571818 | 0.000013 | -0.000333 | 0.000013 | 0.000390 |
| graph_on_qcount_min3 | late_third | 152 | 0.592284 | 0.000089 | -0.000304 | 0.000089 | 0.000542 |
| graph_on_qcount_min3 | tail_20pct | 95 | 0.598205 | 0.000346 | -0.000220 | 0.000346 | 0.000995 |

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
| graph_on_qcount_min3 | Q1 | 0.655598 | 0.000000 |
| graph_on_qcount_min3 | Q2 | 0.642916 | 0.000000 |
| graph_on_qcount_min3 | Q3 | 0.605835 | 0.000000 |
| graph_on_qcount_min3 | S1 | 0.549912 | 0.000486 |
| graph_on_qcount_min3 | S2 | 0.565627 | 0.000000 |
| graph_on_qcount_min3 | S3 | 0.528773 | 0.000139 |
| graph_on_qcount_min3 | S4 | 0.597326 | 0.000000 |
