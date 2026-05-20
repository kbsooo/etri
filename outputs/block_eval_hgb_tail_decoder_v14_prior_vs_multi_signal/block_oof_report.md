# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v14 | 0.576224 | 0.002561 | 0.005368 | 0.000000 | 0.002654 | 0.013325 | 0.017559 | 0.005809 | 0.005607 | -0.004254 | 0.001331 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v14 | all | 450 | 0.576224 | 0.005368 | 0.002561 | 0.005368 | 0.008299 |
| v14 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v14 | mid_third | 147 | 0.569081 | 0.002654 | -0.000247 | 0.002654 | 0.005352 |
| v14 | late_third | 152 | 0.578957 | 0.013325 | 0.005809 | 0.013325 | 0.021875 |
| v14 | tail_20pct | 95 | 0.580858 | 0.017559 | 0.005607 | 0.017559 | 0.030701 |

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
| v14 | Q1 | 0.651047 | 0.005349 |
| v14 | Q2 | 0.625465 | 0.016855 |
| v14 | Q3 | 0.559878 | 0.045803 |
| v14 | S1 | 0.549178 | 0.001331 |
| v14 | S2 | 0.553376 | 0.011914 |
| v14 | S3 | 0.524789 | 0.004214 |
| v14 | S4 | 0.588964 | 0.007809 |
