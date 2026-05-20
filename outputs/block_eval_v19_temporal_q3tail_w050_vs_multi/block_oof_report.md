# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v19_temporal_q3tail_w050 | 0.575317 | 0.003276 | 0.006276 | 0.000000 | 0.001200 | 0.017419 | 0.026114 | 0.008748 | 0.012668 | -0.003173 | 0.001331 | True |
| q3w100 | 0.575682 | 0.003081 | 0.005911 | 0.000000 | 0.001200 | 0.016338 | 0.024384 | 0.008053 | 0.011779 | -0.002774 | 0.001331 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | all | 450 | 0.575682 | 0.005911 | 0.003081 | 0.005911 | 0.009133 |
| q3w100 | early_third | 151 | 0.580429 | 0.000000 | -0.000000 | 0.000000 | 0.000000 |
| q3w100 | mid_third | 147 | 0.570535 | 0.001200 | -0.000288 | 0.001200 | 0.002692 |
| q3w100 | late_third | 152 | 0.575944 | 0.016338 | 0.008053 | 0.016338 | 0.025444 |
| q3w100 | tail_20pct | 95 | 0.574033 | 0.024384 | 0.011779 | 0.024384 | 0.038362 |
| v19_temporal_q3tail_w050 | all | 450 | 0.575317 | 0.006276 | 0.003276 | 0.006276 | 0.009684 |
| v19_temporal_q3tail_w050 | early_third | 151 | 0.580429 | 0.000000 | -0.000000 | 0.000000 | 0.000000 |
| v19_temporal_q3tail_w050 | mid_third | 147 | 0.570535 | 0.001200 | -0.000288 | 0.001200 | 0.002692 |
| v19_temporal_q3tail_w050 | late_third | 152 | 0.574863 | 0.017419 | 0.008748 | 0.017419 | 0.027129 |
| v19_temporal_q3tail_w050 | tail_20pct | 95 | 0.572304 | 0.026114 | 0.012668 | 0.026114 | 0.040999 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| multi_signal | Q1 | 0.656396 | 0.000000 |
| multi_signal | Q2 | 0.642320 | 0.000000 |
| multi_signal | Q3 | 0.605681 | 0.000000 |
| multi_signal | S1 | 0.550509 | 0.000000 |
| multi_signal | S2 | 0.565290 | 0.000000 |
| multi_signal | S3 | 0.529003 | 0.000000 |
| multi_signal | S4 | 0.596773 | 0.000000 |
| q3w100 | Q1 | 0.651047 | 0.005349 |
| q3w100 | Q2 | 0.619485 | 0.022835 |
| q3w100 | Q3 | 0.565599 | 0.040082 |
| q3w100 | S1 | 0.549178 | 0.001331 |
| q3w100 | S2 | 0.553376 | 0.011914 |
| q3w100 | S3 | 0.518377 | 0.010626 |
| q3w100 | S4 | 0.574543 | 0.022230 |
| v19_temporal_q3tail_w050 | Q1 | 0.651047 | 0.005349 |
| v19_temporal_q3tail_w050 | Q2 | 0.619485 | 0.022835 |
| v19_temporal_q3tail_w050 | Q3 | 0.558032 | 0.047649 |
| v19_temporal_q3tail_w050 | S1 | 0.549178 | 0.001331 |
| v19_temporal_q3tail_w050 | S2 | 0.553376 | 0.011914 |
| v19_temporal_q3tail_w050 | S3 | 0.518377 | 0.010626 |
| v19_temporal_q3tail_w050 | S4 | 0.574543 | 0.022230 |
