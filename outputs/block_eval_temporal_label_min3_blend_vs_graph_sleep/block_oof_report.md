# Block OOF diagnostics

- Baseline: `graph_sleep_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_min3_blend | 0.584463 | 0.000172 | 0.001633 | 0.000876 | 0.002924 | 0.001137 | 0.001959 | -0.002214 | -0.002475 | -0.001707 | -0.001531 | True |
| temporal_s2_blend | 0.584769 | 0.000142 | 0.001328 | 0.000763 | 0.002281 | 0.000967 | 0.001068 | -0.001952 | -0.002822 | -0.000947 | 0.000000 | True |
| temporal_label_min3 | 0.584289 | -0.000021 | 0.001807 | 0.000925 | 0.003522 | 0.001025 | 0.001946 | -0.003146 | -0.003646 | -0.002374 | -0.001983 | False |
| graph_sleep_blend | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | all | 450 | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | early_third | 151 | 0.585579 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | mid_third | 147 | 0.577970 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | late_third | 152 | 0.594469 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | tail_20pct | 95 | 0.603666 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | all | 450 | 0.584463 | 0.001633 | 0.000172 | 0.001633 | 0.003129 |
| temporal_label_min3_blend | early_third | 151 | 0.584703 | 0.000876 | -0.001175 | 0.000876 | 0.002973 |
| temporal_label_min3_blend | mid_third | 147 | 0.575046 | 0.002924 | 0.000995 | 0.002924 | 0.004748 |
| temporal_label_min3_blend | late_third | 152 | 0.593332 | 0.001137 | -0.002214 | 0.001137 | 0.004512 |
| temporal_label_min3_blend | tail_20pct | 95 | 0.601707 | 0.001959 | -0.002475 | 0.001959 | 0.006803 |
| temporal_s2_blend | all | 450 | 0.584769 | 0.001328 | 0.000142 | 0.001328 | 0.002525 |
| temporal_s2_blend | early_third | 151 | 0.584816 | 0.000763 | -0.000640 | 0.000763 | 0.002180 |
| temporal_s2_blend | mid_third | 147 | 0.575689 | 0.002281 | 0.000763 | 0.002281 | 0.003746 |
| temporal_s2_blend | late_third | 152 | 0.593502 | 0.000967 | -0.001952 | 0.000967 | 0.003897 |
| temporal_s2_blend | tail_20pct | 95 | 0.602598 | 0.001068 | -0.002822 | 0.001068 | 0.005235 |
| temporal_label_min3 | all | 450 | 0.584289 | 0.001807 | -0.000021 | 0.001807 | 0.003667 |
| temporal_label_min3 | early_third | 151 | 0.584654 | 0.000925 | -0.001609 | 0.000925 | 0.003511 |
| temporal_label_min3 | mid_third | 147 | 0.574448 | 0.003522 | 0.001125 | 0.003522 | 0.005791 |
| temporal_label_min3 | late_third | 152 | 0.593444 | 0.001025 | -0.003146 | 0.001025 | 0.005223 |
| temporal_label_min3 | tail_20pct | 95 | 0.601720 | 0.001946 | -0.003646 | 0.001946 | 0.007975 |

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
| temporal_label_min3_blend | Q1 | 0.655428 | 0.000036 |
| temporal_label_min3_blend | Q2 | 0.645800 | 0.000000 |
| temporal_label_min3_blend | Q3 | 0.611704 | 0.001478 |
| temporal_label_min3_blend | S1 | 0.548427 | -0.001531 |
| temporal_label_min3_blend | S2 | 0.565627 | 0.006770 |
| temporal_label_min3_blend | S3 | 0.528912 | 0.001682 |
| temporal_label_min3_blend | S4 | 0.597426 | -0.000476 |
| temporal_s2_blend | Q1 | 0.655464 | 0.000000 |
| temporal_s2_blend | Q2 | 0.645800 | 0.000000 |
| temporal_s2_blend | Q3 | 0.613182 | 0.000000 |
| temporal_s2_blend | S1 | 0.546897 | 0.000000 |
| temporal_s2_blend | S2 | 0.565627 | 0.006770 |
| temporal_s2_blend | S3 | 0.530594 | 0.000000 |
| temporal_s2_blend | S4 | 0.596950 | 0.000000 |
| temporal_label_min3 | Q1 | 0.655434 | 0.000030 |
| temporal_label_min3 | Q2 | 0.645800 | 0.000000 |
| temporal_label_min3 | Q3 | 0.611507 | 0.001674 |
| temporal_label_min3 | S1 | 0.548880 | -0.001983 |
| temporal_label_min3 | S2 | 0.566298 | 0.006098 |
| temporal_label_min3 | S3 | 0.528569 | 0.002025 |
| temporal_label_min3 | S4 | 0.597621 | -0.000671 |
