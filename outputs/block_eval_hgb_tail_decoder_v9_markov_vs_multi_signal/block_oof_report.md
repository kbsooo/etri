# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v9_markov_q1 | 0.577938 | 0.001573 | 0.003654 | 0.000724 | 0.001926 | 0.008237 | 0.011813 | 0.002366 | 0.002240 | -0.006438 | -0.001990 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v9_markov_q1 | all | 450 | 0.577938 | 0.003654 | 0.001573 | 0.003654 | 0.005905 |
| hgb_tail_decoder_v9_markov_q1 | early_third | 151 | 0.579705 | 0.000724 | -0.000085 | 0.000724 | 0.001552 |
| hgb_tail_decoder_v9_markov_q1 | mid_third | 147 | 0.569809 | 0.001926 | 0.000435 | 0.001926 | 0.003445 |
| hgb_tail_decoder_v9_markov_q1 | late_third | 152 | 0.584045 | 0.008237 | 0.002366 | 0.008237 | 0.014746 |
| hgb_tail_decoder_v9_markov_q1 | tail_20pct | 95 | 0.586604 | 0.011813 | 0.002240 | 0.011813 | 0.022022 |

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
| hgb_tail_decoder_v9_markov_q1 | Q1 | 0.658386 | -0.001990 |
| hgb_tail_decoder_v9_markov_q1 | Q2 | 0.631202 | 0.011118 |
| hgb_tail_decoder_v9_markov_q1 | Q3 | 0.568642 | 0.037039 |
| hgb_tail_decoder_v9_markov_q1 | S1 | 0.549735 | 0.000774 |
| hgb_tail_decoder_v9_markov_q1 | S2 | 0.562574 | 0.002717 |
| hgb_tail_decoder_v9_markov_q1 | S3 | 0.525282 | 0.003721 |
| hgb_tail_decoder_v9_markov_q1 | S4 | 0.592491 | 0.004282 |
