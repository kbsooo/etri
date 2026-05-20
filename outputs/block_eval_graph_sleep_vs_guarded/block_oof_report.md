# Block OOF diagnostics

- Baseline: `guarded`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| graph_sleep_blend | 0.586096 | 0.000286 | 0.001080 | 0.000573 | 0.001766 | 0.000919 | 0.001667 | -0.000294 | 0.000029 | -0.001484 | -0.001824 | True |
| graph_blend | 0.586443 | 0.000018 | 0.000733 | 0.000016 | 0.001242 | 0.000954 | 0.001915 | -0.000074 | 0.000589 | -0.001845 | -0.001848 | True |
| sleep_min3 | 0.585653 | -0.000030 | 0.001523 | 0.001653 | 0.002732 | 0.000225 | 0.000310 | -0.002506 | -0.003133 | -0.001228 | -0.003828 | False |
| guarded | 0.587176 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
| primary | 0.588783 | -0.003647 | -0.001607 | -0.003714 | 0.000188 | -0.001249 | -0.001422 | -0.004040 | -0.005151 | -0.006990 | -0.006468 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| guarded | all | 450 | 0.587176 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| guarded | early_third | 151 | 0.586152 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| guarded | mid_third | 147 | 0.579737 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| guarded | late_third | 152 | 0.595388 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| guarded | tail_20pct | 95 | 0.605333 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| graph_blend | all | 450 | 0.586443 | 0.000733 | 0.000018 | 0.000733 | 0.001456 |
| graph_blend | early_third | 151 | 0.586136 | 0.000016 | -0.001177 | 0.000016 | 0.001168 |
| graph_blend | mid_third | 147 | 0.578495 | 0.001242 | -0.000246 | 0.001242 | 0.002785 |
| graph_blend | late_third | 152 | 0.594434 | 0.000954 | -0.000074 | 0.000954 | 0.002015 |
| graph_blend | tail_20pct | 95 | 0.603418 | 0.001915 | 0.000589 | 0.001915 | 0.003344 |
| sleep_min3 | all | 450 | 0.585653 | 0.001523 | -0.000030 | 0.001523 | 0.003050 |
| sleep_min3 | early_third | 151 | 0.584499 | 0.001653 | -0.000725 | 0.001653 | 0.004100 |
| sleep_min3 | mid_third | 147 | 0.577005 | 0.002732 | -0.000003 | 0.002732 | 0.005570 |
| sleep_min3 | late_third | 152 | 0.595163 | 0.000225 | -0.002506 | 0.000225 | 0.002921 |
| sleep_min3 | tail_20pct | 95 | 0.605024 | 0.000310 | -0.003133 | 0.000310 | 0.003636 |
| graph_sleep_blend | all | 450 | 0.586096 | 0.001080 | 0.000286 | 0.001080 | 0.001887 |
| graph_sleep_blend | early_third | 151 | 0.585579 | 0.000573 | -0.000633 | 0.000573 | 0.001782 |
| graph_sleep_blend | mid_third | 147 | 0.577970 | 0.001766 | 0.000204 | 0.001766 | 0.003451 |
| graph_sleep_blend | late_third | 152 | 0.594469 | 0.000919 | -0.000294 | 0.000919 | 0.002191 |
| graph_sleep_blend | tail_20pct | 95 | 0.603666 | 0.001667 | 0.000029 | 0.001667 | 0.003343 |
| primary | all | 450 | 0.588783 | -0.001607 | -0.003647 | -0.001607 | 0.000424 |
| primary | early_third | 151 | 0.589866 | -0.003714 | -0.007755 | -0.003714 | 0.000010 |
| primary | mid_third | 147 | 0.579549 | 0.000188 | -0.003545 | 0.000188 | 0.003734 |
| primary | late_third | 152 | 0.596638 | -0.001249 | -0.004040 | -0.001249 | 0.001633 |
| primary | tail_20pct | 95 | 0.606755 | -0.001422 | -0.005151 | -0.001422 | 0.002359 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| guarded | Q1 | 0.654274 | 0.000000 |
| guarded | Q2 | 0.646224 | 0.000000 |
| guarded | Q3 | 0.615020 | 0.000000 |
| guarded | S1 | 0.547291 | 0.000000 |
| guarded | S2 | 0.570572 | 0.000000 |
| guarded | S3 | 0.531346 | 0.000000 |
| guarded | S4 | 0.602992 | 0.000000 |
| graph_blend | Q1 | 0.655464 | -0.001190 |
| graph_blend | Q2 | 0.645800 | 0.000423 |
| graph_blend | Q3 | 0.613182 | 0.001838 |
| graph_blend | S1 | 0.546559 | 0.000731 |
| graph_blend | S2 | 0.572420 | -0.001848 |
| graph_blend | S3 | 0.530594 | 0.000752 |
| graph_blend | S4 | 0.597022 | 0.005970 |
| sleep_min3 | Q1 | 0.655464 | -0.001190 |
| sleep_min3 | Q2 | 0.645800 | 0.000423 |
| sleep_min3 | Q3 | 0.613182 | 0.001838 |
| sleep_min3 | S1 | 0.551119 | -0.003828 |
| sleep_min3 | S2 | 0.572505 | -0.001933 |
| sleep_min3 | S3 | 0.530594 | 0.000752 |
| sleep_min3 | S4 | 0.597477 | 0.005514 |
| graph_sleep_blend | Q1 | 0.655464 | -0.001190 |
| graph_sleep_blend | Q2 | 0.645800 | 0.000423 |
| graph_sleep_blend | Q3 | 0.613182 | 0.001838 |
| graph_sleep_blend | S1 | 0.546897 | 0.000394 |
| graph_sleep_blend | S2 | 0.572396 | -0.001824 |
| graph_sleep_blend | S3 | 0.530594 | 0.000752 |
| graph_sleep_blend | S4 | 0.596950 | 0.006042 |
| primary | Q1 | 0.654274 | 0.000000 |
| primary | Q2 | 0.644774 | 0.001449 |
| primary | Q3 | 0.615238 | -0.000218 |
| primary | S1 | 0.550800 | -0.003509 |
| primary | S2 | 0.570572 | 0.000000 |
| primary | S3 | 0.531346 | 0.000000 |
| primary | S4 | 0.609459 | -0.006468 |
