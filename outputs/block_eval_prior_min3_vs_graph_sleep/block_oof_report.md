# Block OOF diagnostics

- Baseline: `graph_sleep_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prior_min3 | 0.585999 | -0.000464 | 0.000098 | 0.000113 | 0.000076 | 0.000104 | 0.000425 | -0.000759 | -0.000696 | -0.000616 | -0.000744 | False |
| graph_sleep_blend | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | all | 450 | 0.586096 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | early_third | 151 | 0.585579 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | mid_third | 147 | 0.577970 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | late_third | 152 | 0.594469 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_sleep_blend | tail_20pct | 95 | 0.603666 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| prior_min3 | all | 450 | 0.585999 | 0.000098 | -0.000464 | 0.000098 | 0.000646 |
| prior_min3 | early_third | 151 | 0.585466 | 0.000113 | -0.000959 | 0.000113 | 0.001109 |
| prior_min3 | mid_third | 147 | 0.577895 | 0.000076 | -0.000826 | 0.000076 | 0.000994 |
| prior_min3 | late_third | 152 | 0.594365 | 0.000104 | -0.000759 | 0.000104 | 0.000965 |
| prior_min3 | tail_20pct | 95 | 0.603241 | 0.000425 | -0.000696 | 0.000425 | 0.001459 |

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
| prior_min3 | Q1 | 0.655464 | 0.000000 |
| prior_min3 | Q2 | 0.645800 | 0.000000 |
| prior_min3 | Q3 | 0.613182 | 0.000000 |
| prior_min3 | S1 | 0.546014 | 0.000883 |
| prior_min3 | S2 | 0.573141 | -0.000744 |
| prior_min3 | S3 | 0.530594 | 0.000000 |
| prior_min3 | S4 | 0.596360 | 0.000590 |
