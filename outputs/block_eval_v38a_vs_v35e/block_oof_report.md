# Block OOF diagnostics

- Baseline: `v35e`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v38a | 0.549791 | 0.013942 | 0.020524 | 0.019851 | 0.015926 | 0.025640 | 0.027881 | 0.014323 | 0.013897 | -0.002565 | 0.001195 | True |
| v35e | 0.570315 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v35e | all | 450 | 0.570315 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | mid_third | 147 | 0.562686 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | late_third | 152 | 0.567706 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v35e | tail_20pct | 95 | 0.567406 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v38a | all | 450 | 0.549791 | 0.020524 | 0.013942 | 0.020524 | 0.027011 |
| v38a | early_third | 151 | 0.560516 | 0.019851 | 0.007951 | 0.019851 | 0.031706 |
| v38a | mid_third | 147 | 0.546760 | 0.015926 | 0.005182 | 0.015926 | 0.026634 |
| v38a | late_third | 152 | 0.542066 | 0.025640 | 0.014323 | 0.025640 | 0.036698 |
| v38a | tail_20pct | 95 | 0.539524 | 0.027881 | 0.013897 | 0.027881 | 0.041628 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v35e | Q1 | 0.647814 | 0.000000 |
| v35e | Q2 | 0.612710 | 0.000000 |
| v35e | Q3 | 0.532843 | 0.000000 |
| v35e | S1 | 0.542220 | 0.000000 |
| v35e | S2 | 0.550381 | 0.000000 |
| v35e | S3 | 0.515956 | 0.000000 |
| v35e | S4 | 0.572014 | 0.000000 |
| v38a | Q1 | 0.609448 | 0.038366 |
| v38a | Q2 | 0.579878 | 0.032832 |
| v38a | Q3 | 0.512006 | 0.020837 |
| v38a | S1 | 0.541025 | 0.001195 |
| v38a | S2 | 0.524314 | 0.026067 |
| v38a | S3 | 0.501599 | 0.014358 |
| v38a | S4 | 0.526193 | 0.045822 |
