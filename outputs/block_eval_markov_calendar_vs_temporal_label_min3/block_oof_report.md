# Block OOF diagnostics

- Baseline: `temporal_label_min3_blend`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_min3 | 0.584048 | -0.000785 | 0.000415 | -0.000091 | 0.001956 | -0.000572 | -0.001065 | -0.002861 | -0.004219 | -0.003243 | -0.002955 | False |
| calendar_blend | 0.584048 | -0.000785 | 0.000415 | -0.000091 | 0.001956 | -0.000572 | -0.001065 | -0.002861 | -0.004219 | -0.003243 | -0.002955 | False |
| markov_min3 | 0.584293 | -0.000507 | 0.000170 | 0.000631 | 0.000950 | -0.001043 | -0.001131 | -0.002341 | -0.002964 | -0.006467 | -0.007301 | False |
| temporal_label_min3_blend | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_label_min3_blend | all | 450 | 0.584463 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | early_third | 151 | 0.584703 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | mid_third | 147 | 0.575046 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | late_third | 152 | 0.593332 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| temporal_label_min3_blend | tail_20pct | 95 | 0.601707 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| markov_min3 | all | 450 | 0.584293 | 0.000170 | -0.000507 | 0.000170 | 0.000858 |
| markov_min3 | early_third | 151 | 0.584072 | 0.000631 | -0.000351 | 0.000631 | 0.001627 |
| markov_min3 | mid_third | 147 | 0.574096 | 0.000950 | -0.000216 | 0.000950 | 0.002186 |
| markov_min3 | late_third | 152 | 0.594375 | -0.001043 | -0.002341 | -0.001043 | 0.000193 |
| markov_min3 | tail_20pct | 95 | 0.602838 | -0.001131 | -0.002964 | -0.001131 | 0.000563 |
| calendar_min3 | all | 450 | 0.584048 | 0.000415 | -0.000785 | 0.000415 | 0.001547 |
| calendar_min3 | early_third | 151 | 0.584794 | -0.000091 | -0.001872 | -0.000091 | 0.001633 |
| calendar_min3 | mid_third | 147 | 0.573091 | 0.001956 | 0.000062 | 0.001956 | 0.003854 |
| calendar_min3 | late_third | 152 | 0.593904 | -0.000572 | -0.002861 | -0.000572 | 0.001749 |
| calendar_min3 | tail_20pct | 95 | 0.602772 | -0.001065 | -0.004219 | -0.001065 | 0.002115 |
| calendar_blend | all | 450 | 0.584048 | 0.000415 | -0.000785 | 0.000415 | 0.001547 |
| calendar_blend | early_third | 151 | 0.584794 | -0.000091 | -0.001872 | -0.000091 | 0.001633 |
| calendar_blend | mid_third | 147 | 0.573091 | 0.001956 | 0.000062 | 0.001956 | 0.003854 |
| calendar_blend | late_third | 152 | 0.593904 | -0.000572 | -0.002861 | -0.000572 | 0.001749 |
| calendar_blend | tail_20pct | 95 | 0.602772 | -0.001065 | -0.004219 | -0.001065 | 0.002115 |

## Late-block target deltas

| name | target | late_log_loss | late_delta_vs_baseline |
| --- | --- | --- | --- |
| temporal_label_min3_blend | Q1 | 0.655428 | 0.000000 |
| temporal_label_min3_blend | Q2 | 0.645800 | 0.000000 |
| temporal_label_min3_blend | Q3 | 0.611704 | 0.000000 |
| temporal_label_min3_blend | S1 | 0.548427 | 0.000000 |
| temporal_label_min3_blend | S2 | 0.565627 | 0.000000 |
| temporal_label_min3_blend | S3 | 0.528912 | 0.000000 |
| temporal_label_min3_blend | S4 | 0.597426 | 0.000000 |
| markov_min3 | Q1 | 0.662729 | -0.007301 |
| markov_min3 | Q2 | 0.645800 | 0.000000 |
| markov_min3 | Q3 | 0.611704 | 0.000000 |
| markov_min3 | S1 | 0.548427 | 0.000000 |
| markov_min3 | S2 | 0.565627 | 0.000000 |
| markov_min3 | S3 | 0.528912 | 0.000000 |
| markov_min3 | S4 | 0.597426 | 0.000000 |
| calendar_min3 | Q1 | 0.655428 | 0.000000 |
| calendar_min3 | Q2 | 0.645800 | 0.000000 |
| calendar_min3 | Q3 | 0.611704 | 0.000000 |
| calendar_min3 | S1 | 0.551382 | -0.002955 |
| calendar_min3 | S2 | 0.564959 | 0.000668 |
| calendar_min3 | S3 | 0.528912 | 0.000000 |
| calendar_min3 | S4 | 0.599145 | -0.001719 |
| calendar_blend | Q1 | 0.655428 | 0.000000 |
| calendar_blend | Q2 | 0.645800 | 0.000000 |
| calendar_blend | Q3 | 0.611704 | 0.000000 |
| calendar_blend | S1 | 0.551382 | -0.002955 |
| calendar_blend | S2 | 0.564959 | 0.000668 |
| calendar_blend | S3 | 0.528912 | 0.000000 |
| calendar_blend | S4 | 0.599145 | -0.001719 |
