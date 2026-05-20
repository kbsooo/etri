# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v17 | 0.574969 | 0.003445 | 0.006623 | 0.000000 | 0.002654 | 0.017041 | 0.023505 | 0.008135 | 0.009728 | -0.005557 | 0.001331 | True |
| with_forward | 0.575454 | 0.003485 | 0.006139 | 0.000467 | 0.001618 | 0.016144 | 0.023586 | 0.008815 | 0.012504 | -0.000802 | 0.001331 | True |
| portfolio_v17_robust | 0.575829 | 0.002968 | 0.005764 | 0.000000 | 0.001200 | 0.015903 | 0.023688 | 0.007747 | 0.011001 | -0.002882 | 0.001331 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| with_forward | all | 450 | 0.575454 | 0.006139 | 0.003485 | 0.006139 | 0.009028 |
| with_forward | early_third | 151 | 0.579961 | 0.000467 | -0.000884 | 0.000467 | 0.001823 |
| with_forward | mid_third | 147 | 0.570117 | 0.001618 | 0.000046 | 0.001618 | 0.003165 |
| with_forward | late_third | 152 | 0.576137 | 0.016144 | 0.008815 | 0.016144 | 0.024398 |
| with_forward | tail_20pct | 95 | 0.574831 | 0.023586 | 0.012504 | 0.023586 | 0.036130 |
| portfolio_v17_robust | all | 450 | 0.575829 | 0.005764 | 0.002968 | 0.005764 | 0.008892 |
| portfolio_v17_robust | early_third | 151 | 0.580429 | 0.000000 | -0.000000 | 0.000000 | 0.000000 |
| portfolio_v17_robust | mid_third | 147 | 0.570535 | 0.001200 | -0.000285 | 0.001200 | 0.002673 |
| portfolio_v17_robust | late_third | 152 | 0.576378 | 0.015903 | 0.007747 | 0.015903 | 0.024897 |
| portfolio_v17_robust | tail_20pct | 95 | 0.574729 | 0.023688 | 0.011001 | 0.023688 | 0.037583 |
| v17 | all | 450 | 0.574969 | 0.006623 | 0.003445 | 0.006623 | 0.010082 |
| v17 | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| v17 | mid_third | 147 | 0.569081 | 0.002654 | -0.000247 | 0.002654 | 0.005352 |
| v17 | late_third | 152 | 0.575241 | 0.017041 | 0.008135 | 0.017041 | 0.026673 |
| v17 | tail_20pct | 95 | 0.574912 | 0.023505 | 0.009728 | 0.023505 | 0.038296 |

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
| with_forward | Q1 | 0.643545 | 0.012851 |
| with_forward | Q2 | 0.620927 | 0.021393 |
| with_forward | Q3 | 0.573016 | 0.032664 |
| with_forward | S1 | 0.549178 | 0.001331 |
| with_forward | S2 | 0.553376 | 0.011914 |
| with_forward | S3 | 0.518377 | 0.010626 |
| with_forward | S4 | 0.574543 | 0.022230 |
| portfolio_v17_robust | Q1 | 0.651047 | 0.005349 |
| portfolio_v17_robust | Q2 | 0.619485 | 0.022835 |
| portfolio_v17_robust | Q3 | 0.568642 | 0.037039 |
| portfolio_v17_robust | S1 | 0.549178 | 0.001331 |
| portfolio_v17_robust | S2 | 0.553376 | 0.011914 |
| portfolio_v17_robust | S3 | 0.518377 | 0.010626 |
| portfolio_v17_robust | S4 | 0.574543 | 0.022230 |
| v17 | Q1 | 0.651047 | 0.005349 |
| v17 | Q2 | 0.620288 | 0.022032 |
| v17 | Q3 | 0.559878 | 0.045803 |
| v17 | S1 | 0.549178 | 0.001331 |
| v17 | S2 | 0.553376 | 0.011914 |
| v17 | S3 | 0.518377 | 0.010626 |
| v17 | S4 | 0.574543 | 0.022230 |
