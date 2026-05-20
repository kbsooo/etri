# Block OOF diagnostics

- Baseline: `v34a`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stack | 0.567602 | 0.001788 | 0.003310 | 0.003914 | 0.003447 | 0.002578 | -0.000232 | -0.000110 | -0.003591 | -0.002713 | -0.000211 | True |
| v34a | 0.570913 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| v34a | all | 450 | 0.570913 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | early_third | 151 | 0.580367 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | mid_third | 147 | 0.563390 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | late_third | 152 | 0.568796 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v34a | tail_20pct | 95 | 0.567406 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| stack | all | 450 | 0.567602 | 0.003310 | 0.001788 | 0.003310 | 0.004797 |
| stack | early_third | 151 | 0.576453 | 0.003914 | 0.001195 | 0.003914 | 0.006559 |
| stack | mid_third | 147 | 0.559943 | 0.003447 | 0.000933 | 0.003447 | 0.005948 |
| stack | late_third | 152 | 0.566218 | 0.002578 | -0.000110 | 0.002578 | 0.005219 |
| stack | tail_20pct | 95 | 0.567637 | -0.000232 | -0.003591 | -0.000232 | 0.003075 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| v34a | Q1 | 0.647814 | 0.000000 |
| v34a | Q2 | 0.615742 | 0.000000 |
| v34a | Q3 | 0.535772 | 0.000000 |
| v34a | S1 | 0.543891 | 0.000000 |
| v34a | S2 | 0.550381 | 0.000000 |
| v34a | S3 | 0.515956 | 0.000000 |
| v34a | S4 | 0.572014 | 0.000000 |
| stack | Q1 | 0.646574 | 0.001240 |
| stack | Q2 | 0.603704 | 0.012038 |
| stack | Q3 | 0.532252 | 0.003520 |
| stack | S1 | 0.544102 | -0.000211 |
| stack | S2 | 0.550381 | 0.000000 |
| stack | S3 | 0.515956 | 0.000000 |
| stack | S4 | 0.570557 | 0.001458 |
