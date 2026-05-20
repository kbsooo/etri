# Block OOF diagnostics

- Baseline: `multi_signal`
- Blocks are per-subject chronological train thirds plus the final 20% tail.
- Positive deltas mean the candidate improves over baseline.

## Candidate summary

| name | avg_log_loss | overall_p025 | overall_improvement | early_delta | mid_delta | late_delta | tail20_delta | late_p025 | tail20_p025 | worst_subject_delta | worst_late_target_delta | promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_tail_decoder_v10_markov_q1q2 | 0.577876 | 0.001554 | 0.003716 | 0.001004 | 0.001494 | 0.008560 | 0.012006 | 0.002666 | 0.002514 | -0.007342 | -0.001990 | False |
| multi_signal | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |

## Block scores

| name | block | n_rows | avg_log_loss | delta_vs_baseline | improvement_p025 | improvement | improvement_p975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | all | 450 | 0.581592 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | early_third | 151 | 0.580429 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | mid_third | 147 | 0.571735 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | late_third | 152 | 0.592282 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| multi_signal | tail_20pct | 95 | 0.598417 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| hgb_tail_decoder_v10_markov_q1q2 | all | 450 | 0.577876 | 0.003716 | 0.001554 | 0.003716 | 0.005991 |
| hgb_tail_decoder_v10_markov_q1q2 | early_third | 151 | 0.579425 | 0.001004 | -0.000043 | 0.001004 | 0.002105 |
| hgb_tail_decoder_v10_markov_q1q2 | mid_third | 147 | 0.570241 | 0.001494 | -0.000126 | 0.001494 | 0.003105 |
| hgb_tail_decoder_v10_markov_q1q2 | late_third | 152 | 0.583721 | 0.008560 | 0.002666 | 0.008560 | 0.014991 |
| hgb_tail_decoder_v10_markov_q1q2 | tail_20pct | 95 | 0.586411 | 0.012006 | 0.002514 | 0.012006 | 0.022166 |

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
| hgb_tail_decoder_v10_markov_q1q2 | Q1 | 0.658386 | -0.001990 |
| hgb_tail_decoder_v10_markov_q1q2 | Q2 | 0.628940 | 0.013380 |
| hgb_tail_decoder_v10_markov_q1q2 | Q3 | 0.568642 | 0.037039 |
| hgb_tail_decoder_v10_markov_q1q2 | S1 | 0.549735 | 0.000774 |
| hgb_tail_decoder_v10_markov_q1q2 | S2 | 0.562574 | 0.002717 |
| hgb_tail_decoder_v10_markov_q1q2 | S3 | 0.525282 | 0.003721 |
| hgb_tail_decoder_v10_markov_q1q2 | S4 | 0.592491 | 0.004282 |
