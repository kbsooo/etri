# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| master_logreg_min3 | 0.580974 | -0.000647 | 0.000618 | 0.001840 | 0.000526 | -0.000508 | -0.000850 | -0.002894 | -0.003952 | -0.003583 | -0.005619 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| master_logreg_min3 | all | 450 | 0.580974 | 0.000618 | -0.000647 | 0.000618 | 0.001878 |
| master_logreg_min3 | early_third | 151 | 0.578589 | 0.001840 | -0.000284 | 0.001840 | 0.004023 |
| master_logreg_min3 | mid_third | 147 | 0.571209 | 0.000526 | -0.001575 | 0.000526 | 0.002594 |
| master_logreg_min3 | late_third | 152 | 0.592789 | -0.000508 | -0.002894 | -0.000508 | 0.001914 |
| master_logreg_min3 | tail_20pct | 95 | 0.599267 | -0.000850 | -0.003952 | -0.000850 | 0.002254 |

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
| master_logreg_min3 | Q1 | 0.659153 | -0.002757 |
| master_logreg_min3 | Q2 | 0.642320 | 0.000000 |
| master_logreg_min3 | Q3 | 0.601558 | 0.004123 |
| master_logreg_min3 | S1 | 0.556129 | -0.005619 |
| master_logreg_min3 | S2 | 0.565290 | 0.000000 |
| master_logreg_min3 | S3 | 0.529003 | 0.000000 |
| master_logreg_min3 | S4 | 0.596073 | 0.000700 |
