# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tail_q3_support_s4 | 0.581296 | 0.000024 | 0.000296 | 0.000000 | 0.000047 | 0.000832 | 0.000859 | 0.000156 | 0.000024 | -0.000613 | 0.000000 | True |
| tail_q3 | 0.581444 | -0.000013 | 0.000149 | 0.000000 | 0.000000 | 0.000440 | 0.000705 | -0.000022 | -0.000049 | -0.000057 | 0.000000 | False |
| support_s4w100 | 0.581445 | -0.000069 | 0.000148 | 0.000000 | 0.000047 | 0.000391 | 0.000155 | -0.000124 | -0.000289 | -0.000845 | 0.000000 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| support_s4w100 | all | 450 | 0.581445 | 0.000148 | -0.000069 | 0.000148 | 0.000374 |
| support_s4w100 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| support_s4w100 | mid_third | 147 | 0.571687 | 0.000047 | -0.000370 | 0.000047 | 0.000473 |
| support_s4w100 | late_third | 152 | 0.591890 | 0.000391 | -0.000124 | 0.000391 | 0.000919 |
| support_s4w100 | tail_20pct | 95 | 0.598262 | 0.000155 | -0.000289 | 0.000155 | 0.000590 |
| tail_q3 | all | 450 | 0.581444 | 0.000149 | -0.000013 | 0.000149 | 0.000325 |
| tail_q3 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| tail_q3 | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| tail_q3 | late_third | 152 | 0.591841 | 0.000440 | -0.000022 | 0.000440 | 0.000920 |
| tail_q3 | tail_20pct | 95 | 0.597713 | 0.000705 | -0.000049 | 0.000705 | 0.001480 |
| tail_q3_support_s4 | all | 450 | 0.581296 | 0.000296 | 0.000024 | 0.000296 | 0.000579 |
| tail_q3_support_s4 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| tail_q3_support_s4 | mid_third | 147 | 0.571687 | 0.000047 | -0.000370 | 0.000047 | 0.000473 |
| tail_q3_support_s4 | late_third | 152 | 0.591450 | 0.000832 | 0.000156 | 0.000832 | 0.001533 |
| tail_q3_support_s4 | tail_20pct | 95 | 0.597558 | 0.000859 | 0.000024 | 0.000859 | 0.001777 |

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
| support_s4w100 | Q1 | 0.656396 | 0.000000 |
| support_s4w100 | Q2 | 0.642320 | 0.000000 |
| support_s4w100 | Q3 | 0.605681 | 0.000000 |
| support_s4w100 | S1 | 0.550509 | 0.000000 |
| support_s4w100 | S2 | 0.565290 | 0.000000 |
| support_s4w100 | S3 | 0.529003 | 0.000000 |
| support_s4w100 | S4 | 0.594033 | 0.002740 |
| tail_q3 | Q1 | 0.656396 | 0.000000 |
| tail_q3 | Q2 | 0.642320 | 0.000000 |
| tail_q3 | Q3 | 0.602598 | 0.003082 |
| tail_q3 | S1 | 0.550509 | 0.000000 |
| tail_q3 | S2 | 0.565290 | 0.000000 |
| tail_q3 | S3 | 0.529003 | 0.000000 |
| tail_q3 | S4 | 0.596773 | 0.000000 |
| tail_q3_support_s4 | Q1 | 0.656396 | 0.000000 |
| tail_q3_support_s4 | Q2 | 0.642320 | 0.000000 |
| tail_q3_support_s4 | Q3 | 0.602598 | 0.003082 |
| tail_q3_support_s4 | S1 | 0.550509 | 0.000000 |
| tail_q3_support_s4 | S2 | 0.565290 | 0.000000 |
| tail_q3_support_s4 | S3 | 0.529003 | 0.000000 |
| tail_q3_support_s4 | S4 | 0.594033 | 0.002740 |
