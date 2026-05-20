# Block OOF diagnostics

- Baseline: `graph_sleep_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_s2 | 0.584614 | -0.000008 | 0.001483 | 0.000863 | 0.002752 | 0.000871 | 0.000883 | -0.002794 | -0.003992 | -0.001386 | 0.000000 | False |
| graph_sleep_blend | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| guarded | 0.587176 | -0.001887 | -0.001080 | -0.000573 | -0.001766 | -0.000919 | -0.001667 | -0.002191 | -0.003343 | -0.002365 | -0.006042 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | all | 450 | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | early_third | 151 | 0.585579 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | mid_third | 147 | 0.577970 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | late_third | 152 | 0.594469 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | tail_20pct | 95 | 0.603666 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_s2 | all | 450 | 0.584614 | 0.001483 | -0.000008 | 0.001483 | 0.002970 |
| temporal_label_s2 | early_third | 151 | 0.584717 | 0.000863 | -0.000891 | 0.000863 | 0.002646 |
| temporal_label_s2 | mid_third | 147 | 0.575218 | 0.002752 | 0.000856 | 0.002752 | 0.004586 |
| temporal_label_s2 | late_third | 152 | 0.593598 | 0.000871 | -0.002794 | 0.000871 | 0.004487 |
| temporal_label_s2 | tail_20pct | 95 | 0.602783 | 0.000883 | -0.003992 | 0.000883 | 0.006067 |
| guarded | all | 450 | 0.587176 | -0.001080 | -0.001887 | -0.001080 | -0.000286 |
| guarded | early_third | 151 | 0.586152 | -0.000573 | -0.001782 | -0.000573 | 0.000633 |
| guarded | mid_third | 147 | 0.579737 | -0.001766 | -0.003451 | -0.001766 | -0.000204 |
| guarded | late_third | 152 | 0.595388 | -0.000919 | -0.002191 | -0.000919 | 0.000294 |
| guarded | tail_20pct | 95 | 0.605333 | -0.001667 | -0.003343 | -0.001667 | -0.000029 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| graph_sleep_blend | Q1 | 0.655464 | 0.000000 |
| graph_sleep_blend | Q2 | 0.645800 | 0.000000 |
| graph_sleep_blend | Q3 | 0.613182 | 0.000000 |
| graph_sleep_blend | S1 | 0.546897 | 0.000000 |
| graph_sleep_blend | S2 | 0.572396 | 0.000000 |
| graph_sleep_blend | S3 | 0.530594 | 0.000000 |
| graph_sleep_blend | S4 | 0.596950 | 0.000000 |
| temporal_label_s2 | Q1 | 0.655464 | 0.000000 |
| temporal_label_s2 | Q2 | 0.645800 | 0.000000 |
| temporal_label_s2 | Q3 | 0.613182 | 0.000000 |
| temporal_label_s2 | S1 | 0.546897 | 0.000000 |
| temporal_label_s2 | S2 | 0.566298 | 0.006098 |
| temporal_label_s2 | S3 | 0.530594 | 0.000000 |
| temporal_label_s2 | S4 | 0.596950 | 0.000000 |
| guarded | Q1 | 0.654274 | 0.001190 |
| guarded | Q2 | 0.646224 | -0.000423 |
| guarded | Q3 | 0.615020 | -0.001838 |
| guarded | S1 | 0.547291 | -0.000394 |
| guarded | S2 | 0.570572 | 0.001824 |
| guarded | S3 | 0.531346 | -0.000752 |
| guarded | S4 | 0.602992 | -0.006042 |
