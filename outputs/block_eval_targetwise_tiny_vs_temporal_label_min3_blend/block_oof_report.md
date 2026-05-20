# Block OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| targetwise_tiny_blend | 0.584410 | 0.000001 | 0.000053 | 0.000089 | 0.000080 | -0.000008 | -0.000043 | -0.000104 | -0.000159 | -0.000049 | -0.000071 | True |
| targetwise_raw | 0.583819 | -0.000395 | 0.000644 | 0.001360 | 0.001166 | -0.000570 | -0.001290 | -0.002474 | -0.003620 | -0.001321 | -0.003240 | False |
| temporal_label_min3_blend | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_min3_blend | all | 450 | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | early_third | 151 | 0.584703 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | mid_third | 147 | 0.575046 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | late_third | 152 | 0.593332 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | tail_20pct | 95 | 0.601707 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| targetwise_tiny_blend | all | 450 | 0.584410 | 0.000053 | 0.000001 | 0.000053 | 0.000106 |
| targetwise_tiny_blend | early_third | 151 | 0.584614 | 0.000089 | 0.000004 | 0.000089 | 0.000178 |
| targetwise_tiny_blend | mid_third | 147 | 0.574966 | 0.000080 | -0.000007 | 0.000080 | 0.000171 |
| targetwise_tiny_blend | late_third | 152 | 0.593340 | -0.000008 | -0.000104 | -0.000008 | 0.000090 |
| targetwise_tiny_blend | tail_20pct | 95 | 0.601750 | -0.000043 | -0.000159 | -0.000043 | 0.000079 |
| targetwise_raw | all | 450 | 0.583819 | 0.000644 | -0.000395 | 0.000644 | 0.001673 |
| targetwise_raw | early_third | 151 | 0.583343 | 0.001360 | -0.000296 | 0.001360 | 0.003104 |
| targetwise_raw | mid_third | 147 | 0.573881 | 0.001166 | -0.000500 | 0.001166 | 0.002868 |
| targetwise_raw | late_third | 152 | 0.593902 | -0.000570 | -0.002474 | -0.000570 | 0.001328 |
| targetwise_raw | tail_20pct | 95 | 0.602997 | -0.001290 | -0.003620 | -0.001290 | 0.001143 |

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
| targetwise_tiny_blend | Q1 | 0.655428 | 0.000000 |
| targetwise_tiny_blend | Q2 | 0.645800 | 0.000000 |
| targetwise_tiny_blend | Q3 | 0.611704 | 0.000000 |
| targetwise_tiny_blend | S1 | 0.548498 | -0.000071 |
| targetwise_tiny_blend | S2 | 0.565638 | -0.000011 |
| targetwise_tiny_blend | S3 | 0.528912 | 0.000000 |
| targetwise_tiny_blend | S4 | 0.597398 | 0.000027 |
| targetwise_raw | Q1 | 0.655428 | 0.000000 |
| targetwise_raw | Q2 | 0.645800 | 0.000000 |
| targetwise_raw | Q3 | 0.611704 | 0.000000 |
| targetwise_raw | S1 | 0.551667 | -0.003240 |
| targetwise_raw | S2 | 0.566298 | -0.000671 |
| targetwise_raw | S3 | 0.528912 | 0.000000 |
| targetwise_raw | S4 | 0.597506 | -0.000081 |
