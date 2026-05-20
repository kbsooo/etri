# Block OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_min3 | 0.584100 | -0.000680 | 0.000363 | -0.000456 | 0.000581 | 0.000965 | 0.002335 | -0.000782 | 0.000041 | -0.004480 | -0.003554 | False |
| graph_min3_blend | 0.584100 | -0.000680 | 0.000363 | -0.000456 | 0.000581 | 0.000965 | 0.002335 | -0.000782 | 0.000041 | -0.004480 | -0.003554 | False |
| graph_min4 | 0.584425 | -0.000165 | 0.000038 | 0.000046 | 0.000031 | 0.000037 | 0.000302 | -0.000389 | -0.000292 | -0.000270 | 0.000000 | False |
| temporal_label_min3_blend | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_min3_blend | all | 450 | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | early_third | 151 | 0.584703 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | mid_third | 147 | 0.575046 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | late_third | 152 | 0.593332 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | tail_20pct | 95 | 0.601707 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_min4 | all | 450 | 0.584425 | 0.000038 | -0.000165 | 0.000038 | 0.000234 |
| graph_min4 | early_third | 151 | 0.584657 | 0.000046 | -0.000196 | 0.000046 | 0.000289 |
| graph_min4 | mid_third | 147 | 0.575015 | 0.000031 | -0.000292 | 0.000031 | 0.000381 |
| graph_min4 | late_third | 152 | 0.593295 | 0.000037 | -0.000389 | 0.000037 | 0.000525 |
| graph_min4 | tail_20pct | 95 | 0.601405 | 0.000302 | -0.000292 | 0.000302 | 0.000984 |
| graph_min3 | all | 450 | 0.584100 | 0.000363 | -0.000680 | 0.000363 | 0.001382 |
| graph_min3 | early_third | 151 | 0.585159 | -0.000456 | -0.002095 | -0.000456 | 0.001131 |
| graph_min3 | mid_third | 147 | 0.574465 | 0.000581 | -0.001198 | 0.000581 | 0.002406 |
| graph_min3 | late_third | 152 | 0.592366 | 0.000965 | -0.000782 | 0.000965 | 0.002714 |
| graph_min3 | tail_20pct | 95 | 0.599372 | 0.002335 | 0.000041 | 0.002335 | 0.004718 |
| graph_min3_blend | all | 450 | 0.584100 | 0.000363 | -0.000680 | 0.000363 | 0.001382 |
| graph_min3_blend | early_third | 151 | 0.585159 | -0.000456 | -0.002095 | -0.000456 | 0.001131 |
| graph_min3_blend | mid_third | 147 | 0.574465 | 0.000581 | -0.001198 | 0.000581 | 0.002406 |
| graph_min3_blend | late_third | 152 | 0.592366 | 0.000965 | -0.000782 | 0.000965 | 0.002714 |
| graph_min3_blend | tail_20pct | 95 | 0.599372 | 0.002335 | 0.000041 | 0.002335 | 0.004718 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| temporal_label_min3_blend | Q1 | 0.655428 | 0.000000 |
| temporal_label_min3_blend | Q2 | 0.645800 | 0.000000 |
| temporal_label_min3_blend | Q3 | 0.611704 | 0.000000 |
| temporal_label_min3_blend | S1 | 0.548427 | 0.000000 |
| temporal_label_min3_blend | S2 | 0.565627 | 0.000000 |
| temporal_label_min3_blend | S3 | 0.528912 | 0.000000 |
| temporal_label_min3_blend | S4 | 0.597426 | 0.000000 |
| graph_min4 | Q1 | 0.655428 | 0.000000 |
| graph_min4 | Q2 | 0.645800 | 0.000000 |
| graph_min4 | Q3 | 0.611704 | 0.000000 |
| graph_min4 | S1 | 0.548427 | 0.000000 |
| graph_min4 | S2 | 0.565627 | 0.000000 |
| graph_min4 | S3 | 0.528653 | 0.000259 |
| graph_min4 | S4 | 0.597426 | 0.000000 |
| graph_min3 | Q1 | 0.658982 | -0.003554 |
| graph_min3 | Q2 | 0.645501 | 0.000299 |
| graph_min3 | Q3 | 0.611117 | 0.000587 |
| graph_min3 | S1 | 0.548427 | 0.000000 |
| graph_min3 | S2 | 0.565627 | 0.000000 |
| graph_min3 | S3 | 0.528653 | 0.000259 |
| graph_min3 | S4 | 0.588259 | 0.009167 |
| graph_min3_blend | Q1 | 0.658982 | -0.003554 |
| graph_min3_blend | Q2 | 0.645501 | 0.000299 |
| graph_min3_blend | Q3 | 0.611117 | 0.000587 |
| graph_min3_blend | S1 | 0.548427 | 0.000000 |
| graph_min3_blend | S2 | 0.565627 | 0.000000 |
| graph_min3_blend | S3 | 0.528653 | 0.000259 |
| graph_min3_blend | S4 | 0.588259 | 0.009167 |
