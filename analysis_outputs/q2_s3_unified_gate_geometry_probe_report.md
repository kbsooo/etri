# E72 Unified Q2/S3 Gate Geometry Probe

## Observe

E71 preserved one strict unified row, but every strict row still used `gate=none`.

## Wonder

Is the non-`none` failure caused by hard agreement thresholds, or is deployable agreement geometry absent?

## Method

- Source strict rows: `155`.
- Unique cells: `104`; support-2 cells: `51`.
- Candidate rows: `4752`.
- Unique predictions: `4752` plus mixmin reference.
- Gates: `['none', 'top_abs50', 'top_abs30', 'agree55', 'soft_signed', 'soft_signed_sq', 'soft_agree_top50', 'q2_only', 's3_only', 'q2_agree55', 's3_agree55']`.
- Alphas: `[2.0, 4.0, 8.0, 12.0, 16.0, 24.0]`.
- Strict gate is the E70/E71 all-combo, tail, hidden, world, block, and raw-energy gate.
- Deployable gate requires strict gate and `gate != none`.

## Gate Summary

| gate | n | margin | strict | deployable | loose | best | active | weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top_abs50 | 432 | 9 | 7 | 7 | 120 | -1.05458e-05 | 0.149389 | 0.149389 |
| s3_only | 432 | 82 | 3 | 3 | 38 | -1.17053e-05 | 0.5 | 0.5 |
| none | 432 | 42 | 11 | 0 | 101 | -1.08217e-05 | 1 | 1 |
| top_abs30 | 432 | 0 | 0 | 0 | 116 | -9.48405e-06 | 0.0899444 | 0.0899444 |
| soft_agree_top50 | 432 | 0 | 0 | 0 | 88 | -9.49912e-06 | 0.137556 | 0.117398 |
| soft_signed | 432 | 0 | 0 | 0 | 64 | -9.43968e-06 | 0.237778 | 0.197322 |
| soft_signed_sq | 432 | 0 | 0 | 0 | 62 | -9.28328e-06 | 0.237778 | 0.177566 |
| agree55 | 432 | 0 | 0 | 0 | 53 | -9.61225e-06 | 0.23 | 0.23 |
| s3_agree55 | 432 | 9 | 0 | 0 | 13 | -1.01954e-05 | 0.102889 | 0.102889 |
| q2_only | 432 | 0 | 0 | 0 | 0 | -5.7625e-06 | 0.5 | 0.5 |
| q2_agree55 | 432 | 0 | 0 | 0 | 0 | -5.699e-06 | 0.127111 | 0.127111 |

## Summary

| pool | base_agg | delta_agg | gate | n | pool_size | pool_support_mean | gate_active_q2s3 | gate_weight_q2s3_mean | strict_gate | deployable_gate | loose_gate | all_margin_vs_mixmin | best_all_delta_vs_mixmin | best_all_minus_base | best_worst_set_delta | best_sets_beating_base | best_sets_tail_neutral | best_hidden_q2s3_minus_base | best_world_support_minus_base | best_block_win_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| translator_tail_soft_p90_m1.00 | mean | signed_p75 | top_abs50 | 6 | 25 | 1.36 | 0.142 | 0.142 | 2 | 2 | 3 | 2 | -1.00626e-05 | -5.10903e-06 | 7.31027e-06 | 3 | 3 | -0.000538295 | -0.000382872 | 0.694444 |
| translator_tail_soft_p90_m0.50 | mean | signed_p75 | top_abs50 | 6 | 13 | 1.46154 | 0.158 | 0.158 | 1 | 1 | 3 | 2 | -1.05458e-05 | -5.78026e-06 | 9.52914e-06 | 3 | 3 | -0.000391043 | -0.000280957 | 0.722222 |
| top75_heldout_mean | mean | mean | s3_only | 6 | 75 | 1.64 | 0.5 | 0.5 | 1 | 1 | 2 | 3 | -1.06739e-05 | -5.782e-06 | 8.09904e-06 | 3 | 3 | -0.000191783 | -8.90133e-05 | 0.777778 |
| all_unique | mean | mean | s3_only | 6 | 104 | 1.49038 | 0.5 | 0.5 | 1 | 1 | 2 | 2 | -1.04355e-05 | -5.5422e-06 | 7.63205e-06 | 3 | 3 | -0.000189363 | -8.39541e-05 | 0.777778 |
| all_unique | mean | weighted_mean | s3_only | 6 | 104 | 1.49038 | 0.5 | 0.5 | 1 | 1 | 2 | 1 | -1.01388e-05 | -5.24551e-06 | 7.50196e-06 | 3 | 3 | -0.000221642 | -9.54296e-05 | 0.777778 |
| translator_tail_soft_p90_m1.00 | mean | weighted_mean | top_abs50 | 6 | 25 | 1.36 | 0.166 | 0.166 | 1 | 1 | 2 | 1 | -1.01143e-05 | -5.16073e-06 | 7.79384e-06 | 3 | 3 | -0.000481362 | -0.000400477 | 0.722222 |
| top50_heldout_mean | mean | mean | top_abs50 | 6 | 50 | 1.84 | 0.166 | 0.166 | 1 | 1 | 2 | 1 | -1.01098e-05 | -5.30897e-06 | 7.49514e-06 | 3 | 3 | -0.000429884 | -0.00032571 | 0.75 |
| high_block | mean | signed_p75 | top_abs50 | 6 | 47 | 1.76596 | 0.158 | 0.158 | 1 | 1 | 2 | 1 | -1.00303e-05 | -5.27186e-06 | 8.60188e-06 | 3 | 3 | -0.000438968 | -0.000342428 | 0.722222 |
| top50_heldout_mean | median | mean | top_abs50 | 6 | 50 | 1.84 | 0.166 | 0.166 | 1 | 1 | 2 | 1 | -1.0015e-05 | -5.35563e-06 | 6.85301e-06 | 3 | 3 | -0.000429884 | -0.000326581 | 0.75 |
| translator_tail_soft_p90_m0.50 | mean | signed_p75 | none | 6 | 13 | 1.46154 | 1 | 1 | 1 | 0 | 2 | 3 | -1.08217e-05 | -6.05613e-06 | 1.04839e-05 | 3 | 3 | -0.000372024 | -0.000294879 | 0.833333 |
| top50_heldout_mean | mean | mean | none | 6 | 50 | 1.84 | 1 | 1 | 1 | 0 | 2 | 2 | -1.03638e-05 | -5.56297e-06 | 7.90408e-06 | 3 | 3 | -0.000469692 | -0.000370136 | 0.833333 |
| top75_heldout_mean | mean | mean | none | 6 | 75 | 1.64 | 1 | 1 | 1 | 0 | 2 | 2 | -1.03376e-05 | -5.44575e-06 | 7.53827e-06 | 3 | 3 | -0.000464872 | -0.000382115 | 0.833333 |
| support2 | mean | mean | none | 6 | 51 | 2 | 1 | 1 | 1 | 0 | 2 | 2 | -1.03117e-05 | -5.56598e-06 | 7.75192e-06 | 3 | 3 | -0.000436034 | -0.000341446 | 0.833333 |
| support2_top50 | mean | mean | none | 6 | 50 | 2 | 1 | 1 | 1 | 0 | 2 | 2 | -1.02804e-05 | -5.53386e-06 | 7.75722e-06 | 3 | 3 | -0.000439706 | -0.000344107 | 0.833333 |
| top50_heldout_mean | median | mean | none | 6 | 50 | 1.84 | 1 | 1 | 1 | 0 | 2 | 2 | -1.02702e-05 | -5.61082e-06 | 7.26198e-06 | 3 | 3 | -0.000469692 | -0.000371007 | 0.833333 |
| support2 | median | mean | none | 6 | 51 | 2 | 1 | 1 | 1 | 0 | 2 | 2 | -1.02198e-05 | -5.6098e-06 | 7.19849e-06 | 3 | 3 | -0.000436034 | -0.000342537 | 0.833333 |
| top75_heldout_mean | median | mean | none | 6 | 75 | 1.64 | 1 | 1 | 1 | 0 | 2 | 2 | -1.0194e-05 | -5.52099e-06 | 7.08316e-06 | 3 | 3 | -0.000464872 | -0.000381752 | 0.833333 |
| support2_top50 | median | mean | none | 6 | 50 | 2 | 1 | 1 | 1 | 0 | 2 | 2 | -1.017e-05 | -5.57649e-06 | 7.21806e-06 | 3 | 3 | -0.000439706 | -0.000345006 | 0.833333 |
| all_unique | mean | mean | none | 6 | 104 | 1.49038 | 1 | 1 | 1 | 0 | 2 | 1 | -1.00942e-05 | -5.20087e-06 | 7.09146e-06 | 3 | 3 | -0.000460469 | -0.000389913 | 0.833333 |
| top75_heldout_mean | mean | signed_p75 | none | 6 | 75 | 1.64 | 1 | 1 | 1 | 0 | 2 | 1 | -1.0056e-05 | -5.16412e-06 | 7.55949e-06 | 3 | 3 | -0.000477907 | -0.000413602 | 0.833333 |
| translator_tail_soft_p90_m0.50 | mean | weighted_mean | none | 6 | 13 | 1.46154 | 1 | 1 | 0 | 0 | 3 | 1 | -1.00916e-05 | -5.32607e-06 | 1.06241e-05 | 3 | 3 | -0.000412126 | -0.00034734 | 0.833333 |
| translator_tail_soft_p90_m0.50 | median | signed_p75 | top_abs50 | 6 | 13 | 1.46154 | 0.158 | 0.158 | 0 | 0 | 3 | 0 | -9.97353e-06 | -5.74584e-06 | 1.17842e-05 | 3 | 3 | -0.000391043 | -0.000281343 | 0.722222 |
| translator_tail_soft_p90_m1.00 | median | signed_p75 | top_abs50 | 6 | 25 | 1.36 | 0.142 | 0.142 | 0 | 0 | 3 | 0 | -9.77319e-06 | -5.15407e-06 | 6.26465e-06 | 3 | 3 | -0.000538295 | -0.000382754 | 0.694444 |
| translator_tail_soft_p90_m0.50 | mean | mean | top_abs50 | 6 | 13 | 1.46154 | 0.166 | 0.166 | 0 | 0 | 3 | 0 | -9.69974e-06 | -4.93421e-06 | 9.87491e-06 | 3 | 3 | -0.00052341 | -0.000431976 | 0.722222 |
| translator_tail_soft_p90_m0.50 | mean | signed_p75 | top_abs30 | 6 | 13 | 1.46154 | 0.094 | 0.094 | 0 | 0 | 3 | 0 | -9.48405e-06 | -4.71852e-06 | 8.43492e-06 | 3 | 3 | -0.000395465 | -0.000276309 | 0.555556 |
| top75_heldout_mean | mean | mean | top_abs30 | 6 | 75 | 1.64 | 0.1 | 0.1 | 0 | 0 | 3 | 0 | -9.21593e-06 | -4.32408e-06 | 6.72693e-06 | 3 | 3 | -0.000443905 | -0.00033469 | 0.611111 |
| translator_tail_soft_p90_m0.50 | median | mean | top_abs50 | 6 | 13 | 1.46154 | 0.166 | 0.166 | 0 | 0 | 3 | 0 | -9.19227e-06 | -4.96458e-06 | 1.20886e-05 | 3 | 3 | -0.00052341 | -0.000432304 | 0.722222 |
| top50_heldout_mean | mean | mean | top_abs30 | 6 | 50 | 1.84 | 0.1 | 0.1 | 0 | 0 | 3 | 0 | -9.15807e-06 | -4.3572e-06 | 7.12703e-06 | 3 | 3 | -0.000460026 | -0.000327354 | 0.611111 |
| support2_top50 | mean | mean | top_abs30 | 6 | 50 | 2 | 0.1 | 0.1 | 0 | 0 | 3 | 0 | -9.09472e-06 | -4.34815e-06 | 7.04687e-06 | 3 | 3 | -0.000437174 | -0.000309521 | 0.611111 |
| support2 | mean | mean | top_abs30 | 6 | 51 | 2 | 0.1 | 0.1 | 0 | 0 | 3 | 0 | -9.08659e-06 | -4.34091e-06 | 7.04864e-06 | 3 | 3 | -0.000432385 | -0.000306056 | 0.611111 |

## Best Full-Combo Rows

| pool | pool_size | pool_support_mean | base_agg | delta_agg | gate | alpha | all_delta_vs_mixmin | all_minus_base | sets_beating_base | sets_tail_neutral | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | strict_gate | deployable_gate | loose_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | signed_p75 | s3_only | 16 | -1.17053e-05 | -6.75168e-06 | 1 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | median | signed_p75 | s3_only | 16 | -1.14816e-05 | -6.86244e-06 | 1 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m0.50 | 13 | 1.46154 | mean | signed_p75 | s3_only | 24 | -1.14588e-05 | -6.69329e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | mean | s3_only | 24 | -1.13656e-05 | -6.41199e-06 | 1 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | signed_p75 | s3_only | 12 | -1.12779e-05 | -6.32435e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | weighted_mean | s3_only | 24 | -1.11407e-05 | -6.18707e-06 | 1 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | mean | signed_p75 | s3_only | 24 | -1.11117e-05 | -6.35329e-06 | 1 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | weighted_mean | s3_only | 16 | -1.10058e-05 | -6.05219e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | median | signed_p75 | s3_only | 12 | -1.09997e-05 | -6.38057e-06 | 2 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | mean | signed_p75 | s3_only | 16 | -1.09922e-05 | -6.23379e-06 | 2 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | mean | weighted_mean | s3_only | 24 | -1.09856e-05 | -6.22715e-06 | 1 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | median | mean | s3_only | 24 | -1.09584e-05 | -6.33926e-06 | 1 | 1 |  |  |  | False | False | False |
| support2_high_block | 36 | 2 | mean | weighted_mean | s3_only | 24 | -1.09465e-05 | -6.18973e-06 | 1 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | mean | mean | s3_only | 24 | -1.09287e-05 | -6.17034e-06 | 1 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | median | signed_p75 | s3_only | 24 | -1.09265e-05 | -6.36359e-06 | 1 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | median | weighted_mean | s3_only | 24 | -1.09161e-05 | -6.35322e-06 | 1 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | mean | s3_only | 16 | -1.09003e-05 | -5.94669e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m0.50 | 13 | 1.46154 | median | signed_p75 | s3_only | 24 | -1.08942e-05 | -6.66651e-06 | 2 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | median | signed_p75 | s3_only | 16 | -1.08755e-05 | -6.31267e-06 | 2 | 1 |  |  |  | False | False | False |
| support2_high_block | 36 | 2 | median | weighted_mean | s3_only | 24 | -1.08713e-05 | -6.3009e-06 | 1 | 1 |  |  |  | False | False | False |
| support2_high_block | 36 | 2 | mean | mean | s3_only | 24 | -1.08601e-05 | -6.10329e-06 | 2 | 1 |  |  |  | False | False | False |
| high_block | 47 | 1.76596 | median | mean | s3_only | 24 | -1.0837e-05 | -6.27414e-06 | 1 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m0.50 | 13 | 1.46154 | mean | signed_p75 | none | 16 | -1.08217e-05 | -6.05613e-06 | 2 | 1 |  |  |  | False | False | False |
| support2_high_block | 36 | 2 | median | mean | s3_only | 24 | -1.07683e-05 | -6.19796e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | median | weighted_mean | s3_only | 16 | -1.07367e-05 | -6.11755e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | median | weighted_mean | s3_only | 24 | -1.07169e-05 | -6.09782e-06 | 1 | 1 |  |  |  | False | False | False |
| top75_heldout_mean | 75 | 1.64 | mean | mean | s3_only | 16 | -1.06739e-05 | -5.782e-06 | 2 | 3 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | median | mean | s3_only | 16 | -1.06223e-05 | -6.00316e-06 | 2 | 1 |  |  |  | False | False | False |
| translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | signed_p75 | none | 8 | -1.06182e-05 | -5.66459e-06 | 3 | 1 | -0.000394856 | -0.000470485 | 0.833333 | False | False | True |
| top50_heldout_mean | 50 | 1.84 | mean | mean | s3_only | 16 | -1.06045e-05 | -5.80366e-06 | 2 | 3 |  |  |  | False | False | False |

## Best Deployable Rows

| pred_index | base_index | tag | base_tag | pool | pool_size | pool_support_mean | base_agg | delta_agg | gate | alpha | gate_active_q2s3 | gate_weight_q2s3_mean | mean_abs_q2s3_delta_unit | all_delta_vs_mixmin | all_minus_base | all_worst_minus_base | set_inverse_top_delta_vs_mixmin | set_inverse_top_minus_base | set_inverse_top_worst_minus_base | set_raw05_compatible_delta_vs_mixmin | set_raw05_compatible_minus_base | set_raw05_compatible_worst_minus_base | set_all_sign_delta_vs_mixmin | set_all_sign_minus_base | set_all_sign_worst_minus_base | best_set_delta_vs_mixmin | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | row_id | world_support_minus_base | raw_energy_q_p90_minus_base | hidden_core_minus_base | hidden_q2_minus_base | hidden_s3_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_mean_minus_base | block_q2s3_max_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | nonanchor_evaluated | mean_abs_logit_move_vs_mixmin | mean_abs_q2s3_logit_move_vs_mixmin | all_beats_base | all_margin_vs_mixmin | all_sets_beat_base | all_sets_tail_neutral | hidden_q2s3_beats_base | world_nonworse | block_majority_beats | block_tail_safe | strict_gate | loose_gate | deployable_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4449 | 4240 | e72_translator_tail_soft_p90_m0.50_top_abs50_16.00_4e48cba2 | e72_base_translator_tail_soft_p90_m0.50_mean_7ae60a81 | translator_tail_soft_p90_m0.50 | 13 | 1.46154 | mean | signed_p75 | top_abs50 | 16 | 0.158 | 0.158 | 0.000300222 | -1.05458e-05 | -5.78026e-06 | -2.48253e-06 | -4.86258e-05 | -1.29242e-05 | -7.20886e-06 | 6.97217e-06 | -2.98525e-06 | -2.48253e-06 | 1.00163e-05 | -1.4313e-06 | -2.48253e-06 | -4.86258e-05 | 1.00163e-05 | 3 | 3 | 4432 | -0.000280957 | -0.000159091 | -0.000111727 | -0.000487278 | -0.000294809 | -0.000391043 | -0.000469637 | 0 | 0.722222 | 1 | True | 0.00668422 | 0.00480356 | True | True | True | True | True | True | True | True | True | True | True |
| 184 | 0 | e72_all_unique_s3_only_12.00_95efe661 | e72_base_all_unique_mean_615a77f1 | all_unique | 104 | 1.49038 | mean | weighted_mean | s3_only | 12 | 0.5 | 0.5 | 0.000324933 | -1.01388e-05 | -5.24551e-06 | -2.73746e-06 | -4.45524e-05 | -1.41593e-05 | -5.67045e-06 | 5.64822e-06 | -1.57519e-06 | -2.73746e-06 | 8.48775e-06 | -2.0359e-09 | -2.73746e-06 | -4.45524e-05 | 8.48775e-06 | 3 | 3 | 183 | -9.54296e-05 | -4.52913e-05 | -6.33262e-05 | 0 | -0.000443284 | -0.000221642 | -0.000417054 | 4.53346e-05 | 0.777778 | 0.972222 | True | 0.00544891 | 0.00389919 | True | True | True | True | True | True | True | True | True | True | True |
| 3852 | 3710 | e72_translator_tail_soft_p90_m1.00_top_abs50_12.00_3479b699 | e72_base_translator_tail_soft_p90_m1.00_mean_36d47d03 | translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | weighted_mean | top_abs50 | 12 | 0.166 | 0.166 | 0.000434591 | -1.01143e-05 | -5.16073e-06 | -8.6899e-07 | -4.47384e-05 | -1.24793e-05 | -5.65111e-06 | 5.54987e-06 | -2.47523e-06 | -8.6899e-07 | 8.84559e-06 | -5.27631e-07 | -8.6899e-07 | -4.47384e-05 | 8.84559e-06 | 3 | 3 | 3837 | -0.000400477 | -0.00021957 | -0.000137532 | -0.000648845 | -0.000313879 | -0.000481362 | -0.000560452 | 0 | 0.722222 | 1 | True | 0.00613914 | 0.00521509 | True | True | True | True | True | True | True | True | True | True | True |
| 1070 | 1060 | e72_top50_heldout_mean_top_abs50_12.00_c4ecd44e | e72_base_top50_heldout_mean_mean_71407b39 | top50_heldout_mean | 50 | 1.84 | mean | mean | top_abs50 | 12 | 0.166 | 0.166 | 0.00040501 | -1.01098e-05 | -5.30897e-06 | -2.56979e-06 | -4.38442e-05 | -1.28252e-05 | -5.67959e-06 | 5.34997e-06 | -2.32473e-06 | -2.56979e-06 | 8.16473e-06 | -7.76963e-07 | -2.56979e-06 | -4.38442e-05 | 8.16473e-06 | 3 | 3 | 1065 | -0.00032571 | -0.000163981 | -0.000122824 | -0.00048897 | -0.000370797 | -0.000429884 | -0.000546971 | 0 | 0.75 | 1 | True | 0.00579456 | 0.00486012 | True | True | True | True | True | True | True | True | True | True | True |
| 3917 | 3710 | e72_translator_tail_soft_p90_m1.00_top_abs50_8.00_64d2bee7 | e72_base_translator_tail_soft_p90_m1.00_mean_36d47d03 | translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | signed_p75 | top_abs50 | 8 | 0.142 | 0.142 | 0.000512274 | -1.00626e-05 | -5.10903e-06 | -2.23235e-06 | -4.24092e-05 | -1.01502e-05 | -3.40622e-06 | 4.91113e-06 | -3.11398e-06 | -2.23235e-06 | 7.31027e-06 | -2.06295e-06 | -2.23235e-06 | -4.24092e-05 | 7.31027e-06 | 3 | 3 | 3902 | -0.000255412 | -0.000130471 | -0.000104141 | -0.000468693 | -0.000260294 | -0.000364494 | -0.000449195 | 0 | 0.694444 | 1 | True | 0.00582002 | 0.00409819 | True | True | True | True | True | True | True | True | True | True | True |
| 2858 | 2650 | e72_high_block_top_abs50_12.00_d4cb6581 | e72_base_high_block_mean_f74e6873 | high_block | 47 | 1.76596 | mean | signed_p75 | top_abs50 | 12 | 0.158 | 0.158 | 0.000423528 | -1.00303e-05 | -5.27186e-06 | -6.01972e-07 | -4.59681e-05 | -1.32478e-05 | -5.64128e-06 | 6.11033e-06 | -2.39054e-06 | -6.01972e-07 | 9.76695e-06 | -1.77247e-07 | -6.01972e-07 | -4.59681e-05 | 9.76695e-06 | 3 | 3 | 2847 | -0.000342428 | -0.0002078 | -0.000125419 | -0.000570542 | -0.000307394 | -0.000438968 | -0.000533215 | 0 | 0.722222 | 1 | True | 0.00628091 | 0.00508233 | True | True | True | True | True | True | True | True | True | True | True |
| 1642 | 1590 | e72_top75_heldout_mean_s3_only_12.00_e052e415 | e72_base_top75_heldout_mean_mean_89ad5b47 | top75_heldout_mean | 75 | 1.64 | mean | mean | s3_only | 12 | 0.5 | 0.5 | 0.000261511 | -1.00248e-05 | -5.13298e-06 | -1.29565e-06 | -4.4381e-05 | -1.35286e-05 | -6.30646e-06 | 5.68423e-06 | -1.76054e-06 | -1.29565e-06 | 8.62224e-06 | -1.09813e-07 | -1.29565e-06 | -4.4381e-05 | 8.62224e-06 | 3 | 3 | 1635 | -8.90133e-05 | -4.50311e-05 | -5.47951e-05 | 0 | -0.000383566 | -0.000191783 | -0.000360098 | 3.02573e-05 | 0.777778 | 0.972222 | True | 0.00527783 | 0.00313813 | True | True | True | True | True | True | True | True | True | True | True |
| 3918 | 3710 | e72_translator_tail_soft_p90_m1.00_top_abs50_12.00_89aaaea1 | e72_base_translator_tail_soft_p90_m1.00_mean_36d47d03 | translator_tail_soft_p90_m1.00 | 25 | 1.36 | mean | signed_p75 | top_abs50 | 12 | 0.142 | 0.142 | 0.000512274 | -1.00244e-05 | -5.07083e-06 | -6.34171e-07 | -4.49551e-05 | -1.2696e-05 | -3.45586e-06 | 5.97839e-06 | -2.04672e-06 | -6.34171e-07 | 8.90342e-06 | -4.69797e-07 | -6.34171e-07 | -4.49551e-05 | 8.90342e-06 | 3 | 3 | 3903 | -0.000382872 | -0.000193293 | -0.000153798 | -0.000693468 | -0.000383121 | -0.000538295 | -0.000665677 | 0 | 0.694444 | 1 | True | 0.00640548 | 0.00614728 | True | True | True | True | True | True | True | True | True | True | True |
| 52 | 0 | e72_all_unique_s3_only_12.00_ca3ab984 | e72_base_all_unique_mean_615a77f1 | all_unique | 104 | 1.49038 | mean | mean | s3_only | 12 | 0.5 | 0.5 | 0.000272756 | -1.00226e-05 | -5.1293e-06 | -1.99607e-06 | -4.3692e-05 | -1.32989e-05 | -6.07807e-06 | 5.4453e-06 | -1.77811e-06 | -1.99607e-06 | 8.1789e-06 | -3.10886e-07 | -1.99607e-06 | -4.3692e-05 | 8.1789e-06 | 3 | 3 | 51 | -8.39541e-05 | -4.40081e-05 | -5.41038e-05 | 0 | -0.000378727 | -0.000189363 | -0.000351548 | 4.28971e-05 | 0.777778 | 0.972222 | True | 0.00527002 | 0.00327307 | True | True | True | True | True | True | True | True | True | True | True |
| 1335 | 1325 | e72_top50_heldout_mean_top_abs50_12.00_cd11454e | e72_base_top50_heldout_mean_median_4b6034d0 | top50_heldout_mean | 50 | 1.84 | median | mean | top_abs50 | 12 | 0.166 | 0.166 | 0.00040501 | -1.0015e-05 | -5.35563e-06 | -2.56979e-06 | -4.23859e-05 | -1.28548e-05 | -5.67959e-06 | 4.78889e-06 | -2.46423e-06 | -2.56979e-06 | 7.55208e-06 | -7.47898e-07 | -2.56979e-06 | -4.23859e-05 | 7.55208e-06 | 3 | 3 | 1329 | -0.000326581 | -0.000163148 | -0.000122824 | -0.00048897 | -0.000370797 | -0.000429884 | -0.000546971 | 0 | 0.75 | 1 | True | 0.00543666 | 0.00486012 | True | True | True | True | True | True | True | True | True | True | True |

## Best Loose Non-None Rows

| pool | base_agg | delta_agg | gate | alpha | all_delta_vs_mixmin | all_minus_base | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | loose_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| translator_tail_soft_p90_m0.50 | mean | signed_p75 | top_abs50 | 16 | -1.05458e-05 | -5.78026e-06 | 3 | 3 | -0.000391043 | -0.000280957 | 0.722222 | True |
| all_unique | mean | weighted_mean | s3_only | 12 | -1.01388e-05 | -5.24551e-06 | 3 | 3 | -0.000221642 | -9.54296e-05 | 0.777778 | True |
| translator_tail_soft_p90_m1.00 | mean | weighted_mean | top_abs50 | 12 | -1.01143e-05 | -5.16073e-06 | 3 | 3 | -0.000481362 | -0.000400477 | 0.722222 | True |
| top50_heldout_mean | mean | mean | top_abs50 | 12 | -1.01098e-05 | -5.30897e-06 | 3 | 3 | -0.000429884 | -0.00032571 | 0.75 | True |
| translator_tail_soft_p90_m1.00 | mean | signed_p75 | top_abs50 | 8 | -1.00626e-05 | -5.10903e-06 | 3 | 3 | -0.000364494 | -0.000255412 | 0.694444 | True |
| high_block | mean | signed_p75 | top_abs50 | 12 | -1.00303e-05 | -5.27186e-06 | 3 | 3 | -0.000438968 | -0.000342428 | 0.722222 | True |
| top75_heldout_mean | mean | mean | s3_only | 12 | -1.00248e-05 | -5.13298e-06 | 3 | 3 | -0.000191783 | -8.90133e-05 | 0.777778 | True |
| translator_tail_soft_p90_m1.00 | mean | signed_p75 | top_abs50 | 12 | -1.00244e-05 | -5.07083e-06 | 3 | 3 | -0.000538295 | -0.000382872 | 0.694444 | True |
| all_unique | mean | mean | s3_only | 12 | -1.00226e-05 | -5.1293e-06 | 3 | 3 | -0.000189363 | -8.39541e-05 | 0.777778 | True |
| top50_heldout_mean | median | mean | top_abs50 | 12 | -1.0015e-05 | -5.35563e-06 | 3 | 3 | -0.000429884 | -0.000326581 | 0.75 | True |
| top75_heldout_mean | mean | mean | top_abs50 | 12 | -9.9954e-06 | -5.10354e-06 | 3 | 3 | -0.000421314 | -0.000330309 | 0.722222 | True |
| translator_tail_soft_p90_m0.50 | median | signed_p75 | top_abs50 | 16 | -9.97353e-06 | -5.74584e-06 | 3 | 3 | -0.000391043 | -0.000281343 | 0.722222 | True |
| support2_top50 | mean | mean | top_abs50 | 12 | -9.94802e-06 | -5.20146e-06 | 3 | 3 | -0.000403851 | -0.000300299 | 0.75 | True |
| support2 | mean | mean | top_abs50 | 12 | -9.93768e-06 | -5.192e-06 | 3 | 3 | -0.000400054 | -0.000297395 | 0.75 | True |
| high_block | median | signed_p75 | top_abs50 | 12 | -9.9314e-06 | -5.36852e-06 | 3 | 3 | -0.000438968 | -0.000343197 | 0.722222 | True |
| all_unique | median | weighted_mean | s3_only | 12 | -9.92545e-06 | -5.22307e-06 | 3 | 3 | -0.000221642 | -9.36241e-05 | 0.777778 | True |
| translator_tail_soft_p90_m1.00 | median | weighted_mean | top_abs50 | 12 | -9.87696e-06 | -5.25784e-06 | 3 | 3 | -0.000481362 | -0.000400147 | 0.722222 | True |
| support2 | median | mean | top_abs50 | 12 | -9.87107e-06 | -5.26105e-06 | 3 | 3 | -0.000400054 | -0.000298672 | 0.75 | True |
| translator_tail_soft_p90_m1.00 | mean | mean | top_abs50 | 12 | -9.86691e-06 | -4.91333e-06 | 3 | 1 | -0.000476593 | -0.000387713 | 0.722222 | True |
| top75_heldout_mean | median | mean | s3_only | 12 | -9.86385e-06 | -5.1908e-06 | 3 | 3 | -0.000191783 | -9.0214e-05 | 0.777778 | True |

## Decision

- Deployable non-`none` gates exist: `10`. Build a candidate-file stress next, not a blind submission.
- No submission file is produced.

## Outputs

- `analysis_outputs/q2_s3_unified_gate_geometry_probe_scan.csv`
- `analysis_outputs/q2_s3_unified_gate_geometry_probe_summary.csv`
