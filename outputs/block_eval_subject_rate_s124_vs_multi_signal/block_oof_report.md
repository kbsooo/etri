# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subj_rate_s124 | 0.581513 | -0.000476 | 0.000080 | -0.000280 | -0.000017 | 0.000531 | 0.000649 | -0.000529 | -0.000655 | -0.001053 | 0.000000 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| subj_rate_s124 | all | 450 | 0.581513 | 0.000080 | -0.000476 | 0.000080 | 0.000626 |
| subj_rate_s124 | early_third | 151 | 0.580708 | -0.000280 | -0.001228 | -0.000280 | 0.000624 |
| subj_rate_s124 | mid_third | 147 | 0.571752 | -0.000017 | -0.000931 | -0.000017 | 0.000896 |
| subj_rate_s124 | late_third | 152 | 0.591751 | 0.000531 | -0.000529 | 0.000531 | 0.001523 |
| subj_rate_s124 | tail_20pct | 95 | 0.597768 | 0.000649 | -0.000655 | 0.000649 | 0.001965 |

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
| subj_rate_s124 | Q1 | 0.656396 | 0.000000 |
| subj_rate_s124 | Q2 | 0.642320 | 0.000000 |
| subj_rate_s124 | Q3 | 0.605681 | 0.000000 |
| subj_rate_s124 | S1 | 0.550509 | 0.000000 |
| subj_rate_s124 | S2 | 0.565290 | 0.000000 |
| subj_rate_s124 | S3 | 0.529003 | 0.000000 |
| subj_rate_s124 | S4 | 0.593058 | 0.003715 |
