# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v18_pool | 0.575103 | 0.003663 | 0.006490 | 0.000000 | 0.002502 | 0.016793 | 0.023375 | 0.008804 | 0.011379 | -0.003112 | 0.001331 | True |
| robust_portfolio | 0.575829 | 0.002993 | 0.005764 | 0.000000 | 0.001200 | 0.015903 | 0.023688 | 0.007778 | 0.011320 | -0.002882 | 0.001331 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| robust_portfolio | all | 450 | 0.575829 | 0.005764 | 0.002993 | 0.005764 | 0.008898 |
| robust_portfolio | early_third | 151 | 0.580429 | 0.000000 | -0.000000 | 0.000000 | 0.000000 |
| robust_portfolio | mid_third | 147 | 0.570535 | 0.001200 | -0.000288 | 0.001200 | 0.002692 |
| robust_portfolio | late_third | 152 | 0.576378 | 0.015903 | 0.007778 | 0.015903 | 0.024811 |
| robust_portfolio | tail_20pct | 95 | 0.574729 | 0.023688 | 0.011320 | 0.023688 | 0.037393 |
| v18_pool | all | 450 | 0.575103 | 0.006490 | 0.003663 | 0.006490 | 0.009608 |
| v18_pool | early_third | 151 | 0.580429 | 0.000000 | -0.000000 | 0.000000 | 0.000000 |
| v18_pool | mid_third | 147 | 0.569233 | 0.002502 | 0.000054 | 0.002502 | 0.004862 |
| v18_pool | late_third | 152 | 0.575488 | 0.016793 | 0.008804 | 0.016793 | 0.025594 |
| v18_pool | tail_20pct | 95 | 0.575042 | 0.023375 | 0.011379 | 0.023375 | 0.036687 |

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
| robust_portfolio | Q1 | 0.651047 | 0.005349 |
| robust_portfolio | Q2 | 0.619485 | 0.022835 |
| robust_portfolio | Q3 | 0.568642 | 0.037039 |
| robust_portfolio | S1 | 0.549178 | 0.001331 |
| robust_portfolio | S2 | 0.553376 | 0.011914 |
| robust_portfolio | S3 | 0.518377 | 0.010626 |
| robust_portfolio | S4 | 0.574543 | 0.022230 |
| v18_pool | Q1 | 0.651047 | 0.005349 |
| v18_pool | Q2 | 0.619485 | 0.022835 |
| v18_pool | Q3 | 0.562412 | 0.043269 |
| v18_pool | S1 | 0.549178 | 0.001331 |
| v18_pool | S2 | 0.553376 | 0.011914 |
| v18_pool | S3 | 0.518377 | 0.010626 |
| v18_pool | S4 | 0.574543 | 0.022230 |
