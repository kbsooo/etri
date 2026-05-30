# E251 E237/E250 Cell-Set Contrast

## Question

Is E250 a feature-NN1-context variant that adds useful Q3 cells beyond E237, or mostly a sibling of the same learned Q3 tail?

## Headline

- E237 Q3 cells: `25`.
- E250 Q3 cells: `21`.
- shared cells: `15`.
- E237-only cells: `10`.
- E250-only cells: `6`.
- union cells: `31`.
- materialization gate passes: `5` of `7` graft rows.

## Gate-Passing Cell Sets

| candidate_id | source_type | known_oof_loss_vs_full | known_oof_tail_auc | q3_rows | overlap_e237 | overlap_e250 | shared_cells_in_candidate | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | q3_top1_over_abs_expected | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | materialization_gate | e237_like_score_no_oof |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| union_e237_e250 | union |  |  | 31 | 25 | 21 | 15 | -0.000035272 | 0.000721005 | 0.010353010 | 0.506203451 | -0.000035272 | 0.000688037 | True | 0.077866812 |
| e237_top25 | known_e237 | -0.000271441 | 0.901873158 | 25 | 25 | 15 | 15 | -0.000005612 | 0.000576400 | 0.006450259 | 0.747139811 | -0.000005612 | 0.000553281 | True | 0.058941606 |
| e250_top21 | known_e250 | -0.000185023 | 0.887356598 | 21 | 15 | 21 | 15 | -0.000000845 | 0.000524271 | 0.005790882 | 0.660128450 | -0.000000845 | 0.000502064 | True | 0.053008707 |
| symmetric_difference | difference |  |  | 16 | 10 | 6 | 0 | -0.000064087 | 0.000341339 | 0.006941819 | 0.557289090 | -0.000064087 | 0.000320729 | True | 0.043661466 |
| e237_only | difference |  |  | 10 | 10 | 0 | 0 | -0.000034427 | 0.000196734 | 0.003597882 | 0.669889646 | -0.000034427 | 0.000185973 | True | 0.024780965 |

## All Graft Rows

| candidate_id | source_type | known_oof_loss_vs_full | known_oof_tail_auc | q3_rows | overlap_e237 | overlap_e250 | shared_cells_in_candidate | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | q3_top1_over_abs_expected | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | materialization_gate | e237_like_score_no_oof |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| union_e237_e250 | union |  |  | 31 | 25 | 21 | 15 | -0.000035272 | 0.000721005 | 0.010353010 | 0.506203451 | -0.000035272 | 0.000688037 | True | 0.077866812 |
| e237_top25 | known_e237 | -0.000271441 | 0.901873158 | 25 | 25 | 15 | 15 | -0.000005612 | 0.000576400 | 0.006450259 | 0.747139811 | -0.000005612 | 0.000553281 | True | 0.058941606 |
| e250_top21 | known_e250 | -0.000185023 | 0.887356598 | 21 | 15 | 21 | 15 | -0.000000845 | 0.000524271 | 0.005790882 | 0.660128450 | -0.000000845 | 0.000502064 | True | 0.053008707 |
| symmetric_difference | difference |  |  | 16 | 10 | 6 | 0 | -0.000064087 | 0.000341339 | 0.006941819 | 0.557289090 | -0.000064087 | 0.000320729 | True | 0.043661466 |
| shared_intersection | overlap |  |  | 15 | 15 | 15 | 15 | 0.000028815 | 0.000379666 | 0.002274234 | 1.054974961 | 0.000028815 | 0.000367308 | False | 0.026920210 |
| e237_only | difference |  |  | 10 | 10 | 0 | 0 | -0.000034427 | 0.000196734 | 0.003597882 | 0.669889646 | -0.000034427 | 0.000185973 | True | 0.024780965 |
| e250_only | difference |  |  | 6 | 0 | 6 | 0 | -0.000029661 | 0.000144605 | 0.003048691 | 0.692368577 | -0.000029661 | 0.000134756 | False | 0.018856881 |

## Overlap

| candidate_id | q3_rows | overlap_e237 | overlap_e250 | jaccard_e237 | jaccard_e250 | e237_only_cells_in_candidate | e250_only_cells_in_candidate | shared_cells_in_candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| union_e237_e250 | 31 | 25 | 21 | 0.806451613 | 0.677419355 | 10 | 6 | 15 |
| e237_top25 | 25 | 25 | 15 | 1.000000000 | 0.483870968 | 10 | 0 | 15 |
| e250_top21 | 21 | 15 | 21 | 0.483870968 | 1.000000000 | 0 | 6 | 15 |
| symmetric_difference | 16 | 10 | 6 | 0.322580645 | 0.193548387 | 10 | 6 | 0 |
| shared_intersection | 15 | 15 | 15 | 0.600000000 | 0.714285714 | 0 | 0 | 15 |
| e237_only | 10 | 10 | 0 | 0.400000000 | 0.000000000 | 10 | 0 | 0 |
| e250_only | 6 | 0 | 6 | 0.000000000 | 0.285714286 | 0 | 6 | 0 |

## Decision

- The union survives materialization, so E237/E250 may be complementary. This is still not submission-ready without an OOF analogue for the union.
- Public LB is not used and no new submission is created.
