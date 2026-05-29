# E82 Pure Q2/S3 Source-Graft Scan

## Observe

E81 rejected direct E73/E74/E75 follow-up because the submitted E73 file moved all seven targets, while isolated final-file Q2/S3 was only sub-margin.

## Wonder

Does the broader E72/E75/E76 source universe contain a pure mixmin-anchored Q2/S3 movement that survives combo-tail stress once non-Q2/S3 base movement is removed?

## Method

- Reconstruct E72 adaptive gate rows, E75 target-ridge rows, and E76 subset-stability rows.
- For each source row, build both value graft and delta graft variants over Q2/S3, Q2-only, and S3-only.
- Score all rows on combo sets first, then run non-anchor hidden/world/block stress only on the combo-promising subset.

## Source Universe

| source | source_rows | source_preds | rows | nonanchor_evaluated | strict | deployable | loose | best_all | best_eval_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e72 | 1051 | 4770 | 2916 | 0 | 0 | 0 | 0 | -6.94692e-06 |  |
| e75 | 120 | 121 | 280 | 16 | 0 | 0 | 16 | -7.74856e-06 | -7.74856e-06 |
| e76 | 1894 | 2068 | 5206 | 684 | 0 | 0 | 684 | -7.95667e-06 | -7.90328e-06 |

## Summary

| source | graft_mode | target_scope | rows | nonanchor_evaluated | strict | deployable | loose | best_all_delta_vs_mixmin | best_eval_all_delta_vs_mixmin | best_deployable_all_delta | best_loose_all_delta | best_hidden_q2s3 | best_world | best_block_win |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e76 | delta_graft | q2s3 | 1714 | 342 | 0 | 0 | 342 | -7.95667e-06 | -7.90328e-06 |  | -7.90328e-06 | -0.000520081 | -0.000335798 | 0.805556 |
| e76 | value_graft | q2s3 | 1714 | 342 | 0 | 0 | 342 | -7.95667e-06 | -7.90328e-06 |  | -7.90328e-06 | -0.000520081 | -0.000335798 | 0.805556 |
| e75 | delta_graft | q2s3 | 120 | 8 | 0 | 0 | 8 | -7.74856e-06 | -7.74856e-06 |  | -7.74856e-06 | -0.000476334 | -0.000295181 | 0.777778 |
| e75 | value_graft | q2s3 | 120 | 8 | 0 | 0 | 8 | -7.74856e-06 | -7.74856e-06 |  | -7.74856e-06 | -0.000476334 | -0.000295181 | 0.805556 |
| e72 | delta_graft | q2_only | 416 | 0 | 0 | 0 | 0 | -1.01001e-06 |  |  |  |  |  |  |
| e72 | delta_graft | q2s3 | 561 | 0 | 0 | 0 | 0 | -6.94692e-06 |  |  |  |  |  |  |
| e72 | delta_graft | s3_only | 481 | 0 | 0 | 0 | 0 | -6.94692e-06 |  |  |  |  |  |  |
| e72 | value_graft | q2_only | 416 | 0 | 0 | 0 | 0 | -1.01001e-06 |  |  |  |  |  |  |
| e72 | value_graft | q2s3 | 561 | 0 | 0 | 0 | 0 | -6.94692e-06 |  |  |  |  |  |  |
| e72 | value_graft | s3_only | 481 | 0 | 0 | 0 | 0 | -6.94692e-06 |  |  |  |  |  |  |
| e75 | delta_graft | q2_only | 10 | 0 | 0 | 0 | 0 | -7.94448e-07 |  |  |  |  |  |  |
| e75 | delta_graft | s3_only | 10 | 0 | 0 | 0 | 0 | -7.09023e-06 |  |  |  |  |  |  |
| e75 | value_graft | q2_only | 10 | 0 | 0 | 0 | 0 | -7.94448e-07 |  |  |  |  |  |  |
| e75 | value_graft | s3_only | 10 | 0 | 0 | 0 | 0 | -7.09023e-06 |  |  |  |  |  |  |
| e76 | delta_graft | q2_only | 315 | 0 | 0 | 0 | 0 | -8.15289e-07 |  |  |  |  |  |  |
| e76 | delta_graft | s3_only | 574 | 0 | 0 | 0 | 0 | -7.34041e-06 |  |  |  |  |  |  |
| e76 | value_graft | q2_only | 315 | 0 | 0 | 0 | 0 | -8.15289e-07 |  |  |  |  |  |  |
| e76 | value_graft | s3_only | 574 | 0 | 0 | 0 | 0 | -7.34041e-06 |  |  |  |  |  |  |

## Best Evaluated Rows

| source | graft_mode | target_scope | pool | gate | pair_name | variant_kind | variant_name | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | sets_beating_base | sets_tail_neutral | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | strict_gate | deployable_gate | loose_gate | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_059 | -7.90328e-06 | -7.90328e-06 | -6.16043e-07 | 3 | 3 | -0.000399766 | -0.000190053 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_530bf861 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_059 | -7.90328e-06 | -7.90328e-06 | -6.16043e-07 | 3 | 3 | -0.000399766 | -0.000190053 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_530bf861 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_028 | -7.87232e-06 | -7.87232e-06 | -6.30554e-07 | 3 | 3 | -0.000374684 | -0.000205931 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_2433db1c |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_028 | -7.87232e-06 | -7.87232e-06 | -6.30554e-07 | 3 | 3 | -0.000374684 | -0.000205931 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_2433db1c |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_059 | -7.86327e-06 | -7.86327e-06 | -5.00889e-07 | 3 | 3 | -0.000460342 | -0.000256464 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_b6b358d5 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_059 | -7.86327e-06 | -7.86327e-06 | -5.00889e-07 | 3 | 3 | -0.000460342 | -0.000256464 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_b6b358d5 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_031 | -7.85976e-06 | -7.85976e-06 | -4.44306e-07 | 3 | 3 | -0.000381698 | -0.000196761 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_33647fd3 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_031 | -7.85976e-06 | -7.85976e-06 | -4.44306e-07 | 3 | 3 | -0.000381698 | -0.000196761 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_33647fd3 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | jackknife | drop_cell_097 | -7.84133e-06 | -7.84133e-06 | -1.90653e-07 | 3 | 3 | -0.000382251 | -0.000189953 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_109603c5 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | jackknife | drop_cell_097 | -7.84133e-06 | -7.84133e-06 | -1.90653e-07 | 3 | 3 | -0.000382251 | -0.000189953 | 0.777778 | False | False | True | e82_e76_delta_graft_q2s3_109603c5 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_001 | -7.8299e-06 | -7.8299e-06 | -8.46776e-07 | 3 | 3 | -0.00037906 | -0.000176492 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_313e2484 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_001 | -7.8299e-06 | -7.8299e-06 | -8.46776e-07 | 3 | 3 | -0.00037906 | -0.000176492 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_313e2484 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_028 | -7.82647e-06 | -7.82647e-06 | -5.13479e-07 | 3 | 3 | -0.000435185 | -0.000271293 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_74b02815 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_028 | -7.82647e-06 | -7.82647e-06 | -5.13479e-07 | 3 | 3 | -0.000435185 | -0.000271293 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_74b02815 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | group_keep | base_cell_gate_all | -7.82563e-06 | -7.82563e-06 | -6.23153e-07 | 3 | 3 | -0.00038754 | -0.000193647 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_f4d365ec |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | group_keep | base_cell_gate_all | -7.82563e-06 | -7.82563e-06 | -6.23153e-07 | 3 | 3 | -0.00038754 | -0.000193647 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_f4d365ec |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_002 | -7.82189e-06 | -7.82189e-06 | -8.98597e-07 | 3 | 3 | -0.000388146 | -0.000177843 | 0.777778 | False | False | True | e82_e76_delta_graft_q2s3_7690b2df |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_002 | -7.82189e-06 | -7.82189e-06 | -8.98597e-07 | 3 | 3 | -0.000388146 | -0.000177843 | 0.777778 | False | False | True | e82_e76_value_graft_q2s3_7690b2df |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_051 | -7.81955e-06 | -7.81955e-06 | -5.08072e-07 | 3 | 3 | -0.000380878 | -0.000194088 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_f97489ee |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_051 | -7.81955e-06 | -7.81955e-06 | -5.08072e-07 | 3 | 3 | -0.000380878 | -0.000194088 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_f97489ee |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a8_s3a26 | bootstrap8 | bootstrap8_059 | -7.80499e-06 | -7.80499e-06 | -1.03619e-06 | 3 | 3 | -0.000381368 | -0.000186545 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_868ca69f |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a8_s3a26 | bootstrap8 | bootstrap8_059 | -7.80499e-06 | -7.80499e-06 | -1.03619e-06 | 3 | 3 | -0.000381368 | -0.000186545 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_868ca69f |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_034 | -7.80334e-06 | -7.80334e-06 | -8.45325e-07 | 3 | 3 | -0.000376124 | -0.000177198 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_af70f3f1 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_034 | -7.80334e-06 | -7.80334e-06 | -8.45325e-07 | 3 | 3 | -0.000376124 | -0.000177198 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_af70f3f1 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_031 | -7.80113e-06 | -7.80113e-06 | -3.05388e-07 | 3 | 3 | -0.000442137 | -0.000262161 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_def1555f |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_031 | -7.80113e-06 | -7.80113e-06 | -3.05388e-07 | 3 | 3 | -0.000442137 | -0.000262161 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_def1555f |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_001 | -7.79133e-06 | -7.79133e-06 | -7.43461e-07 | 3 | 3 | -0.000439594 | -0.000240011 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_c8bf8dd2 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_001 | -7.79133e-06 | -7.79133e-06 | -7.43461e-07 | 3 | 3 | -0.000439594 | -0.000240011 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_c8bf8dd2 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | jackknife | drop_cell_097 | -7.78854e-06 | -7.78854e-06 | -9.0245e-08 | 3 | 3 | -0.000444545 | -0.000259129 | 0.777778 | False | False | True | e82_e76_delta_graft_q2s3_331af7c6 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | jackknife | drop_cell_097 | -7.78854e-06 | -7.78854e-06 | -9.0245e-08 | 3 | 3 | -0.000444545 | -0.000259129 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_331af7c6 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | group_keep | base_cell_gate_all | -7.7805e-06 | -7.7805e-06 | -4.95706e-07 | 3 | 3 | -0.000449014 | -0.000261073 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_16b33f11 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | group_keep | base_cell_gate_all | -7.7805e-06 | -7.7805e-06 | -4.95706e-07 | 3 | 3 | -0.000449014 | -0.000261073 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_16b33f11 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_002 | -7.77956e-06 | -7.77956e-06 | -8.0973e-07 | 3 | 3 | -0.000449631 | -0.000246193 | 0.777778 | False | False | True | e82_e76_delta_graft_q2s3_0af7bea0 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_002 | -7.77956e-06 | -7.77956e-06 | -8.0973e-07 | 3 | 3 | -0.000449631 | -0.000246193 | 0.777778 | False | False | True | e82_e76_value_graft_q2s3_0af7bea0 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_051 | -7.77554e-06 | -7.77554e-06 | -3.95232e-07 | 3 | 3 | -0.000442207 | -0.00026144 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_b526c987 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a12_s3a28 | bootstrap8 | bootstrap8_051 | -7.77554e-06 | -7.77554e-06 | -3.95232e-07 | 3 | 3 | -0.000442207 | -0.00026144 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_b526c987 |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_048 | -7.77322e-06 | -7.77322e-06 | -2.42593e-07 | 3 | 3 | -0.000383141 | -0.000174375 | 0.805556 | False | False | True | e82_e76_delta_graft_q2s3_795db78a |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | asym8_28_e75 | bootstrap8 | bootstrap8_048 | -7.77322e-06 | -7.77322e-06 | -2.42593e-07 | 3 | 3 | -0.000383141 | -0.000174375 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_795db78a |
| e76 | delta_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a8_s3a26 | jackknife | drop_cell_097 | -7.77061e-06 | -7.77061e-06 | -7.29751e-07 | 3 | 3 | -0.000365414 | -0.000187002 | 0.777778 | False | False | True | e82_e76_delta_graft_q2s3_26339690 |
| e76 | value_graft | q2s3 | translator_tail_soft_p90_m0.50 | top_abs50 | q2a8_s3a26 | jackknife | drop_cell_097 | -7.77061e-06 | -7.77061e-06 | -7.29751e-07 | 3 | 3 | -0.000365414 | -0.000187002 | 0.805556 | False | False | True | e82_e76_value_graft_q2s3_26339690 |

## Deployable Rows

_None._

## Loose Rows

| source | graft_mode | target_scope | pair_name | variant_kind | variant_name | all_delta_vs_mixmin | worst_set_delta_vs_mixmin | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e76 | delta_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_059 | -7.90328e-06 | -6.16043e-07 | -0.000399766 | -0.000190053 | 0.805556 | e82_e76_delta_graft_q2s3_530bf861 |
| e76 | value_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_059 | -7.90328e-06 | -6.16043e-07 | -0.000399766 | -0.000190053 | 0.805556 | e82_e76_value_graft_q2s3_530bf861 |
| e76 | delta_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_028 | -7.87232e-06 | -6.30554e-07 | -0.000374684 | -0.000205931 | 0.805556 | e82_e76_delta_graft_q2s3_2433db1c |
| e76 | value_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_028 | -7.87232e-06 | -6.30554e-07 | -0.000374684 | -0.000205931 | 0.805556 | e82_e76_value_graft_q2s3_2433db1c |
| e76 | delta_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_059 | -7.86327e-06 | -5.00889e-07 | -0.000460342 | -0.000256464 | 0.805556 | e82_e76_delta_graft_q2s3_b6b358d5 |
| e76 | value_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_059 | -7.86327e-06 | -5.00889e-07 | -0.000460342 | -0.000256464 | 0.805556 | e82_e76_value_graft_q2s3_b6b358d5 |
| e76 | delta_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_031 | -7.85976e-06 | -4.44306e-07 | -0.000381698 | -0.000196761 | 0.805556 | e82_e76_delta_graft_q2s3_33647fd3 |
| e76 | value_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_031 | -7.85976e-06 | -4.44306e-07 | -0.000381698 | -0.000196761 | 0.805556 | e82_e76_value_graft_q2s3_33647fd3 |
| e76 | value_graft | q2s3 | asym8_28_e75 | jackknife | drop_cell_097 | -7.84133e-06 | -1.90653e-07 | -0.000382251 | -0.000189953 | 0.805556 | e82_e76_value_graft_q2s3_109603c5 |
| e76 | delta_graft | q2s3 | asym8_28_e75 | jackknife | drop_cell_097 | -7.84133e-06 | -1.90653e-07 | -0.000382251 | -0.000189953 | 0.777778 | e82_e76_delta_graft_q2s3_109603c5 |
| e76 | delta_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_001 | -7.8299e-06 | -8.46776e-07 | -0.00037906 | -0.000176492 | 0.805556 | e82_e76_delta_graft_q2s3_313e2484 |
| e76 | value_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_001 | -7.8299e-06 | -8.46776e-07 | -0.00037906 | -0.000176492 | 0.805556 | e82_e76_value_graft_q2s3_313e2484 |
| e76 | delta_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_028 | -7.82647e-06 | -5.13479e-07 | -0.000435185 | -0.000271293 | 0.805556 | e82_e76_delta_graft_q2s3_74b02815 |
| e76 | value_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_028 | -7.82647e-06 | -5.13479e-07 | -0.000435185 | -0.000271293 | 0.805556 | e82_e76_value_graft_q2s3_74b02815 |
| e76 | delta_graft | q2s3 | asym8_28_e75 | group_keep | base_cell_gate_all | -7.82563e-06 | -6.23153e-07 | -0.00038754 | -0.000193647 | 0.805556 | e82_e76_delta_graft_q2s3_f4d365ec |
| e76 | value_graft | q2s3 | asym8_28_e75 | group_keep | base_cell_gate_all | -7.82563e-06 | -6.23153e-07 | -0.00038754 | -0.000193647 | 0.805556 | e82_e76_value_graft_q2s3_f4d365ec |
| e76 | delta_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_002 | -7.82189e-06 | -8.98597e-07 | -0.000388146 | -0.000177843 | 0.777778 | e82_e76_delta_graft_q2s3_7690b2df |
| e76 | value_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_002 | -7.82189e-06 | -8.98597e-07 | -0.000388146 | -0.000177843 | 0.777778 | e82_e76_value_graft_q2s3_7690b2df |
| e76 | delta_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_051 | -7.81955e-06 | -5.08072e-07 | -0.000380878 | -0.000194088 | 0.805556 | e82_e76_delta_graft_q2s3_f97489ee |
| e76 | value_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_051 | -7.81955e-06 | -5.08072e-07 | -0.000380878 | -0.000194088 | 0.805556 | e82_e76_value_graft_q2s3_f97489ee |
| e76 | value_graft | q2s3 | q2a8_s3a26 | bootstrap8 | bootstrap8_059 | -7.80499e-06 | -1.03619e-06 | -0.000381368 | -0.000186545 | 0.805556 | e82_e76_value_graft_q2s3_868ca69f |
| e76 | delta_graft | q2s3 | q2a8_s3a26 | bootstrap8 | bootstrap8_059 | -7.80499e-06 | -1.03619e-06 | -0.000381368 | -0.000186545 | 0.805556 | e82_e76_delta_graft_q2s3_868ca69f |
| e76 | delta_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_034 | -7.80334e-06 | -8.45325e-07 | -0.000376124 | -0.000177198 | 0.805556 | e82_e76_delta_graft_q2s3_af70f3f1 |
| e76 | value_graft | q2s3 | asym8_28_e75 | bootstrap8 | bootstrap8_034 | -7.80334e-06 | -8.45325e-07 | -0.000376124 | -0.000177198 | 0.805556 | e82_e76_value_graft_q2s3_af70f3f1 |
| e76 | delta_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_031 | -7.80113e-06 | -3.05388e-07 | -0.000442137 | -0.000262161 | 0.805556 | e82_e76_delta_graft_q2s3_def1555f |
| e76 | value_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_031 | -7.80113e-06 | -3.05388e-07 | -0.000442137 | -0.000262161 | 0.805556 | e82_e76_value_graft_q2s3_def1555f |
| e76 | delta_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_001 | -7.79133e-06 | -7.43461e-07 | -0.000439594 | -0.000240011 | 0.805556 | e82_e76_delta_graft_q2s3_c8bf8dd2 |
| e76 | value_graft | q2s3 | q2a12_s3a28 | bootstrap8 | bootstrap8_001 | -7.79133e-06 | -7.43461e-07 | -0.000439594 | -0.000240011 | 0.805556 | e82_e76_value_graft_q2s3_c8bf8dd2 |
| e76 | delta_graft | q2s3 | q2a12_s3a28 | jackknife | drop_cell_097 | -7.78854e-06 | -9.0245e-08 | -0.000444545 | -0.000259129 | 0.777778 | e82_e76_delta_graft_q2s3_331af7c6 |
| e76 | value_graft | q2s3 | q2a12_s3a28 | jackknife | drop_cell_097 | -7.78854e-06 | -9.0245e-08 | -0.000444545 | -0.000259129 | 0.805556 | e82_e76_value_graft_q2s3_331af7c6 |

## Decision

- No pure source graft survived strict/deployable stress. The Q2/S3 latent remains useful energy but not a submission source.

## Outputs

- `analysis_outputs/e82_pure_q2s3_source_graft_scan.csv`
- `analysis_outputs/e82_pure_q2s3_source_graft_summary.csv`
- `analysis_outputs/e82_pure_q2s3_source_graft_source_summary.csv`
