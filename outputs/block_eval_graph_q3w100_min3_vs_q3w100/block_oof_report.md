# Block OOF diagnostics

- Baseline: `q3w100`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_q3w100_min3 | 0.575567 | -0.000467 | 0.000114 | -0.000684 | 0.000237 | 0.000788 | 0.001123 | 0.000010 | -0.000011 | -0.001617 | 0.000000 | False |
| q3w100 | 0.575682 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| q3w100 | all | 450 | 0.575682 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | mid_third | 147 | 0.570535 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | late_third | 152 | 0.575944 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| q3w100 | tail_20pct | 95 | 0.574033 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_q3w100_min3 | all | 450 | 0.575567 | 0.000114 | -0.000467 | 0.000114 | 0.000705 |
| graph_q3w100_min3 | early_third | 151 | 0.581112 | -0.000684 | -0.001780 | -0.000684 | 0.000281 |
| graph_q3w100_min3 | mid_third | 147 | 0.570298 | 0.000237 | -0.000873 | 0.000237 | 0.001366 |
| graph_q3w100_min3 | late_third | 152 | 0.575155 | 0.000788 | 0.000010 | 0.000788 | 0.001624 |
| graph_q3w100_min3 | tail_20pct | 95 | 0.572910 | 0.001123 | -0.000011 | 0.001123 | 0.002310 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| q3w100 | Q1 | 0.651047 | 0.000000 |
| q3w100 | Q2 | 0.619485 | 0.000000 |
| q3w100 | Q3 | 0.565599 | 0.000000 |
| q3w100 | S1 | 0.549178 | 0.000000 |
| q3w100 | S2 | 0.553376 | 0.000000 |
| q3w100 | S3 | 0.518377 | 0.000000 |
| q3w100 | S4 | 0.574543 | 0.000000 |
| graph_q3w100_min3 | Q1 | 0.651047 | 0.000000 |
| graph_q3w100_min3 | Q2 | 0.619485 | 0.000000 |
| graph_q3w100_min3 | Q3 | 0.565599 | 0.000000 |
| graph_q3w100_min3 | S1 | 0.548337 | 0.000841 |
| graph_q3w100_min3 | S2 | 0.553376 | 0.000000 |
| graph_q3w100_min3 | S3 | 0.518365 | 0.000012 |
| graph_q3w100_min3 | S4 | 0.569877 | 0.004666 |
