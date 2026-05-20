# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| support_s4w100 | 0.581445 | -0.000069 | 0.000148 | 0.000000 | 0.000047 | 0.000391 | 0.000155 | -0.000124 | -0.000289 | -0.000845 | 0.000000 | False |
| support_s4w080 | 0.581471 | -0.000052 | 0.000121 | 0.000000 | 0.000043 | 0.000318 | 0.000127 | -0.000094 | -0.000228 | -0.000672 | 0.000000 | False |
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
| support_s4w080 | all | 450 | 0.581471 | 0.000121 | -0.000052 | 0.000121 | 0.000303 |
| support_s4w080 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| support_s4w080 | mid_third | 147 | 0.571692 | 0.000043 | -0.000292 | 0.000043 | 0.000383 |
| support_s4w080 | late_third | 152 | 0.591963 | 0.000318 | -0.000094 | 0.000318 | 0.000741 |
| support_s4w080 | tail_20pct | 95 | 0.598291 | 0.000127 | -0.000228 | 0.000127 | 0.000475 |

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
| support_s4w080 | Q1 | 0.656396 | 0.000000 |
| support_s4w080 | Q2 | 0.642320 | 0.000000 |
| support_s4w080 | Q3 | 0.605681 | 0.000000 |
| support_s4w080 | S1 | 0.550509 | 0.000000 |
| support_s4w080 | S2 | 0.565290 | 0.000000 |
| support_s4w080 | S3 | 0.529003 | 0.000000 |
| support_s4w080 | S4 | 0.594543 | 0.002229 |
