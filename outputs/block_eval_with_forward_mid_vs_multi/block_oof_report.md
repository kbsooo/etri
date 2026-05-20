# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| with_forward_relaxed | 0.574825 | 0.003722 | 0.006767 | 0.000438 | 0.001893 | 0.017768 | 0.025749 | 0.009588 | 0.013273 | -0.001584 | 0.001331 | True |
| v17 | 0.574969 | 0.003445 | 0.006623 | 0.000000 | 0.002654 | 0.017041 | 0.023505 | 0.008135 | 0.009728 | -0.005557 | 0.001331 | True |
| with_forward_mid | 0.574985 | 0.003656 | 0.006607 | 0.000456 | 0.001767 | 0.017399 | 0.025358 | 0.009243 | 0.012995 | -0.001698 | 0.001331 | True |
| with_forward_safe | 0.575454 | 0.003485 | 0.006139 | 0.000467 | 0.001618 | 0.016144 | 0.023586 | 0.008815 | 0.012504 | -0.000802 | 0.001331 | True |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| with_forward_mid | all | 450 | 0.574985 | 0.006607 | 0.003656 | 0.006607 | 0.009793 |
| with_forward_mid | early_third | 151 | 0.579973 | 0.000456 | -0.001312 | 0.000456 | 0.002217 |
| with_forward_mid | mid_third | 147 | 0.569968 | 0.001767 | -0.000057 | 0.001767 | 0.003615 |
| with_forward_mid | late_third | 152 | 0.574882 | 0.017399 | 0.009243 | 0.017399 | 0.026608 |
| with_forward_mid | tail_20pct | 95 | 0.573059 | 0.025358 | 0.012995 | 0.025358 | 0.039141 |
| with_forward_relaxed | all | 450 | 0.574825 | 0.006767 | 0.003722 | 0.006767 | 0.010013 |
| with_forward_relaxed | early_third | 151 | 0.579991 | 0.000438 | -0.001743 | 0.000438 | 0.002606 |
| with_forward_relaxed | mid_third | 147 | 0.569841 | 0.001893 | -0.000226 | 0.001893 | 0.004022 |
| with_forward_relaxed | late_third | 152 | 0.574514 | 0.017768 | 0.009588 | 0.017768 | 0.027062 |
| with_forward_relaxed | tail_20pct | 95 | 0.572668 | 0.025749 | 0.013273 | 0.025749 | 0.039546 |
| with_forward_safe | all | 450 | 0.575454 | 0.006139 | 0.003485 | 0.006139 | 0.009028 |
| with_forward_safe | early_third | 151 | 0.579961 | 0.000467 | -0.000884 | 0.000467 | 0.001823 |
| with_forward_safe | mid_third | 147 | 0.570117 | 0.001618 | 0.000046 | 0.001618 | 0.003165 |
| with_forward_safe | late_third | 152 | 0.576137 | 0.016144 | 0.008815 | 0.016144 | 0.024398 |
| with_forward_safe | tail_20pct | 95 | 0.574831 | 0.023586 | 0.012504 | 0.023586 | 0.036130 |
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
| with_forward_mid | Q1 | 0.640575 | 0.015822 |
| with_forward_mid | Q2 | 0.619485 | 0.022835 |
| with_forward_mid | Q3 | 0.568642 | 0.037039 |
| with_forward_mid | S1 | 0.549178 | 0.001331 |
| with_forward_mid | S2 | 0.553376 | 0.011914 |
| with_forward_mid | S3 | 0.518377 | 0.010626 |
| with_forward_mid | S4 | 0.574543 | 0.022230 |
| with_forward_relaxed | Q1 | 0.637998 | 0.018398 |
| with_forward_relaxed | Q2 | 0.619485 | 0.022835 |
| with_forward_relaxed | Q3 | 0.568642 | 0.037039 |
| with_forward_relaxed | S1 | 0.549178 | 0.001331 |
| with_forward_relaxed | S2 | 0.553376 | 0.011914 |
| with_forward_relaxed | S3 | 0.518377 | 0.010626 |
| with_forward_relaxed | S4 | 0.574543 | 0.022230 |
| with_forward_safe | Q1 | 0.643545 | 0.012851 |
| with_forward_safe | Q2 | 0.620927 | 0.021393 |
| with_forward_safe | Q3 | 0.573016 | 0.032664 |
| with_forward_safe | S1 | 0.549178 | 0.001331 |
| with_forward_safe | S2 | 0.553376 | 0.011914 |
| with_forward_safe | S3 | 0.518377 | 0.010626 |
| with_forward_safe | S4 | 0.574543 | 0.022230 |
| v17 | Q1 | 0.651047 | 0.005349 |
| v17 | Q2 | 0.620288 | 0.022032 |
| v17 | Q3 | 0.559878 | 0.045803 |
| v17 | S1 | 0.549178 | 0.001331 |
| v17 | S2 | 0.553376 | 0.011914 |
| v17 | S3 | 0.518377 | 0.010626 |
| v17 | S4 | 0.574543 | 0.022230 |
