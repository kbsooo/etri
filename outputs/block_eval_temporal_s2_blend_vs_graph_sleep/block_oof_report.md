# Block OOF diagnostics

- Baseline: `graph_sleep_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_s2_blend | 0.584769 | 0.000142 | 0.001328 | 0.000763 | 0.002281 | 0.000967 | 0.001068 | -0.001952 | -0.002822 | -0.000947 | 0.000000 | True |
| temporal_label_s2 | 0.584614 | -0.000008 | 0.001483 | 0.000863 | 0.002752 | 0.000871 | 0.000883 | -0.002794 | -0.003992 | -0.001386 | 0.000000 | False |
| graph_sleep_blend | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | all | 450 | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | early_third | 151 | 0.585579 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | mid_third | 147 | 0.577970 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | late_third | 152 | 0.594469 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | tail_20pct | 95 | 0.603666 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_s2_blend | all | 450 | 0.584769 | 0.001328 | 0.000142 | 0.001328 | 0.002525 |
| temporal_s2_blend | early_third | 151 | 0.584816 | 0.000763 | -0.000640 | 0.000763 | 0.002180 |
| temporal_s2_blend | mid_third | 147 | 0.575689 | 0.002281 | 0.000763 | 0.002281 | 0.003746 |
| temporal_s2_blend | late_third | 152 | 0.593502 | 0.000967 | -0.001952 | 0.000967 | 0.003897 |
| temporal_s2_blend | tail_20pct | 95 | 0.602598 | 0.001068 | -0.002822 | 0.001068 | 0.005235 |
| temporal_label_s2 | all | 450 | 0.584614 | 0.001483 | -0.000008 | 0.001483 | 0.002970 |
| temporal_label_s2 | early_third | 151 | 0.584717 | 0.000863 | -0.000891 | 0.000863 | 0.002646 |
| temporal_label_s2 | mid_third | 147 | 0.575218 | 0.002752 | 0.000856 | 0.002752 | 0.004586 |
| temporal_label_s2 | late_third | 152 | 0.593598 | 0.000871 | -0.002794 | 0.000871 | 0.004487 |
| temporal_label_s2 | tail_20pct | 95 | 0.602783 | 0.000883 | -0.003992 | 0.000883 | 0.006067 |

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
| temporal_s2_blend | Q1 | 0.655464 | 0.000000 |
| temporal_s2_blend | Q2 | 0.645800 | 0.000000 |
| temporal_s2_blend | Q3 | 0.613182 | 0.000000 |
| temporal_s2_blend | S1 | 0.546897 | 0.000000 |
| temporal_s2_blend | S2 | 0.565627 | 0.006770 |
| temporal_s2_blend | S3 | 0.530594 | 0.000000 |
| temporal_s2_blend | S4 | 0.596950 | 0.000000 |
| temporal_label_s2 | Q1 | 0.655464 | 0.000000 |
| temporal_label_s2 | Q2 | 0.645800 | 0.000000 |
| temporal_label_s2 | Q3 | 0.613182 | 0.000000 |
| temporal_label_s2 | S1 | 0.546897 | 0.000000 |
| temporal_label_s2 | S2 | 0.566298 | 0.006098 |
| temporal_label_s2 | S3 | 0.530594 | 0.000000 |
| temporal_label_s2 | S4 | 0.596950 | 0.000000 |
