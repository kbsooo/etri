# E77 Q2/S3 Amplitude Posterior Probe

## Observe

E76 separates direction from exact amplitude: S3-heavy beats symmetric controls in every source-subset variant, but exact asym8/28 is deployable in only 49/94 variants.

## Wonder

Can the E76 source-subset prediction distribution be used as a latent posterior over amplitude, reducing exact-alpha fragility without losing local margin, hidden support, world support, or block stress?

## Method

- Source scan: `analysis_outputs/q2_s3_target_amplitude_stability_probe_scan.csv`.
- Selectors: `19` groups from exact asym rows, best deployable rows per variant, all S3-heavy deployable rows, and dynamically stable alpha pairs.
- Base references: `['mixmin', 'e73', 'e74']`.
- Aggregators: `['mean', 'median', 'signed_p60', 'signed_p75', 'signed_p90']`.
- Target scopes: `['q2s3', 's3_only', 'full']`.
- Shrinks: `[0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5]`.
- Candidates are built as logit-space posterior movements from mixmin/E73/E74, then scored by the same combo, hidden, world, block, raw-energy gates used by E76.

## Selector Summary

| selector_name | description | source_rows | source_variants | source_pairs | deployable_rate | strict_rate | loose_rate | best_source_all_delta | median_source_all_delta | best_source_hidden_q2s3 | best_source_world |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact_asym_all | all exact E75 asym8/28 rows | 94 | 94 | 1 | 0.521277 | 0.521277 | 1 | -1.256e-05 | -1.21647e-05 | -0.000399766 | -0.000252404 |
| exact_asym_deployable | deployable exact E75 asym8/28 rows | 49 | 49 | 1 | 1 | 1 | 1 | -1.256e-05 | -1.22607e-05 | -0.000399766 | -0.000229799 |
| best_deployable_per_variant | best deployable row in each source variant | 94 | 94 | 6 | 1 | 1 | 1 | -1.256e-05 | -1.21132e-05 | -0.000399766 | -0.000229799 |
| best_s3_deployable_per_variant | best S3-heavy deployable row in each source variant | 94 | 94 | 6 | 1 | 1 | 1 | -1.256e-05 | -1.21132e-05 | -0.000399766 | -0.000229799 |
| all_s3_deployable | all S3-heavy deployable rows | 810 | 94 | 14 | 1 | 1 | 1 | -1.256e-05 | -1.17761e-05 | -0.000510273 | -0.000342999 |
| pair_all_q2a8_s3a22 | all rows for stable pair q2a8_s3a22 | 94 | 94 | 1 | 1 | 1 | 1 | -1.19732e-05 | -1.17097e-05 | -0.000343958 | -0.000226974 |
| pair_deployable_q2a8_s3a22 | deployable rows for stable pair q2a8_s3a22 | 94 | 94 | 1 | 1 | 1 | 1 | -1.19732e-05 | -1.17097e-05 | -0.000343958 | -0.000226974 |
| pair_all_q2a12_s3a22 | all rows for stable pair q2a12_s3a22 | 94 | 94 | 1 | 1 | 1 | 1 | -1.1936e-05 | -1.1661e-05 | -0.000406016 | -0.000289324 |
| pair_deployable_q2a12_s3a22 | deployable rows for stable pair q2a12_s3a22 | 94 | 94 | 1 | 1 | 1 | 1 | -1.1936e-05 | -1.1661e-05 | -0.000406016 | -0.000289324 |
| pair_all_q2a8_s3a20 | all rows for stable pair q2a8_s3a20 | 94 | 94 | 1 | 1 | 1 | 1 | -1.1681e-05 | -1.14445e-05 | -0.000325133 | -0.000218326 |
| pair_deployable_q2a8_s3a20 | deployable rows for stable pair q2a8_s3a20 | 94 | 94 | 1 | 1 | 1 | 1 | -1.1681e-05 | -1.14445e-05 | -0.000325133 | -0.000218326 |
| pair_all_q2a8_s3a24 | all rows for stable pair q2a8_s3a24 | 94 | 94 | 1 | 0.861702 | 0.861702 | 1 | -1.22263e-05 | -1.19165e-05 | -0.000362765 | -0.000235546 |
| pair_deployable_q2a8_s3a24 | deployable rows for stable pair q2a8_s3a24 | 81 | 81 | 1 | 1 | 1 | 1 | -1.22263e-05 | -1.19605e-05 | -0.000362765 | -0.000213608 |
| pair_all_q2a12_s3a24 | all rows for stable pair q2a12_s3a24 | 94 | 94 | 1 | 0.819149 | 0.819149 | 1 | -1.21852e-05 | -1.18746e-05 | -0.000424384 | -0.000297765 |
| pair_deployable_q2a12_s3a24 | deployable rows for stable pair q2a12_s3a24 | 77 | 77 | 1 | 1 | 1 | 1 | -1.21852e-05 | -1.19219e-05 | -0.000424384 | -0.000274974 |
| pair_all_q2a8_s3a26 | all rows for stable pair q2a8_s3a26 | 94 | 94 | 1 | 0.808511 | 0.808511 | 1 | -1.24216e-05 | -1.20818e-05 | -0.000381368 | -0.000244042 |
| pair_deployable_q2a8_s3a26 | deployable rows for stable pair q2a8_s3a26 | 76 | 76 | 1 | 1 | 1 | 1 | -1.24216e-05 | -1.21294e-05 | -0.000381368 | -0.000221969 |
| pair_all_sym16_e73 | all rows for stable pair sym16_e73 | 94 | 94 | 1 | 0.765957 | 0.765957 | 1 | -1.05728e-05 | -1.0344e-05 | -0.000411011 | -0.000324166 |
| pair_deployable_sym16_e73 | deployable rows for stable pair sym16_e73 | 72 | 72 | 1 | 1 | 1 | 1 | -1.05728e-05 | -1.03835e-05 | -0.000411011 | -0.000312312 |

## Stress Summary

| base_ref | target_scope | rows | strict | deployable | loose | beats_e75_local_all | best_all_delta_vs_mixmin | best_all_minus_base | best_worst_set_delta | best_hidden_q2s3_minus_base | best_world_support_minus_base | best_block_win_rate | best_deployable_delta | best_strict_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin | s3_only | 760 | 0 | 0 | 713 | 0 | -7.41764e-06 | -7.41764e-06 | -1.672e-06 | -0.000617922 | -0.000143578 | 0.75 |  |  |
| mixmin | q2s3 | 760 | 0 | 0 | 688 | 0 | -8.09547e-06 | -8.09547e-06 | -2.16163e-06 | -0.0012026 | -0.000779359 | 0.833333 |  |  |
| e73 | s3_only | 760 | 0 | 0 | 645 | 0 | -1.23675e-05 | -1.82174e-06 | 9.97427e-06 | -0.000330329 | -0.000141312 | 0.805556 |  |  |
| mixmin | full | 760 | 0 | 0 | 611 | 9 | -1.25991e-05 | -1.25991e-05 | 2.14243e-06 | -0.0012026 | -0.00475625 | 0.833333 |  |  |
| e74 | s3_only | 760 | 0 | 0 | 416 | 0 | -1.16935e-05 | -9.67422e-07 | 1.06401e-05 | -0.000284107 | -8.80612e-05 | 0.833333 |  |  |
| e73 | full | 760 | 0 | 0 | 26 | 6 | -1.24948e-05 | -1.94897e-06 | 9.8588e-06 | -0.000124382 | -0.000136513 | 0.666667 |  |  |
| e74 | q2s3 | 760 | 0 | 0 | 0 | 7 | -1.26541e-05 | -1.92802e-06 | 9.80686e-06 | 2.52697e-05 | 2.64704e-05 | 0.583333 |  |  |
| e73 | q2s3 | 760 | 0 | 0 | 0 | 35 | -1.26522e-05 | -2.10637e-06 | 9.83032e-06 | -0.000124382 | -4.67809e-05 | 0.666667 |  |  |
| e74 | full | 760 | 0 | 0 | 0 | 5 | -1.25473e-05 | -1.82124e-06 | 9.90335e-06 | 2.52697e-05 | 8.17522e-06 | 0.583333 |  |  |

## By Selector

| selector_name | rows | strict | deployable | loose | beats_e75 | best_all | best_minus_base | best_hidden | best_world | best_block |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pair_deployable_q2a12_s3a24 | 360 | 0 | 0 | 191 | 4 | -1.24333e-05 | -1.22664e-05 | -0.00101423 | -0.00459272 | 0.833333 |
| pair_deployable_q2a8_s3a24 | 360 | 0 | 0 | 181 | 2 | -1.23756e-05 | -1.23019e-05 | -0.000862704 | -0.00444047 | 0.833333 |
| pair_all_q2a12_s3a24 | 360 | 0 | 0 | 180 | 2 | -1.24754e-05 | -1.22192e-05 | -0.0010244 | -0.00461348 | 0.833333 |
| all_s3_deployable | 360 | 0 | 0 | 178 | 6 | -1.25639e-05 | -1.23632e-05 | -0.0012026 | -0.00475625 | 0.833333 |
| pair_deployable_q2a8_s3a26 | 360 | 0 | 0 | 176 | 5 | -1.24789e-05 | -1.24557e-05 | -0.000898596 | -0.00445336 | 0.833333 |
| pair_all_q2a8_s3a22 | 360 | 0 | 0 | 174 | 0 | -1.229e-05 | -1.20799e-05 | -0.00083331 | -0.00444122 | 0.833333 |
| pair_deployable_q2a8_s3a22 | 360 | 0 | 0 | 174 | 0 | -1.229e-05 | -1.20799e-05 | -0.00083331 | -0.00444122 | 0.833333 |
| pair_all_q2a8_s3a24 | 360 | 0 | 0 | 171 | 2 | -1.24479e-05 | -1.22711e-05 | -0.000870986 | -0.00445859 | 0.833333 |
| exact_asym_deployable | 360 | 0 | 0 | 170 | 24 | -1.26453e-05 | -1.25991e-05 | -0.000923371 | -0.0043988 | 0.833333 |
| pair_all_q2a12_s3a22 | 360 | 0 | 0 | 169 | 0 | -1.23618e-05 | -1.20285e-05 | -0.000986729 | -0.00459611 | 0.833333 |
| pair_deployable_q2a12_s3a22 | 360 | 0 | 0 | 169 | 0 | -1.23618e-05 | -1.20285e-05 | -0.000986729 | -0.00459611 | 0.833333 |
| exact_asym_all | 360 | 0 | 0 | 168 | 7 | -1.26541e-05 | -1.24876e-05 | -0.00094196 | -0.00449067 | 0.833333 |
| pair_all_q2a8_s3a26 | 360 | 0 | 0 | 164 | 4 | -1.25397e-05 | -1.24076e-05 | -0.000907204 | -0.0044754 | 0.833333 |
| best_deployable_per_variant | 360 | 0 | 0 | 163 | 3 | -1.25799e-05 | -1.24935e-05 | -0.000940895 | -0.00448627 | 0.833333 |
| best_s3_deployable_per_variant | 360 | 0 | 0 | 163 | 3 | -1.25799e-05 | -1.24935e-05 | -0.000940895 | -0.00448627 | 0.833333 |
| pair_all_q2a8_s3a20 | 360 | 0 | 0 | 149 | 0 | -1.18135e-05 | -1.18135e-05 | -0.000794182 | -0.0044233 | 0.833333 |
| pair_deployable_q2a8_s3a20 | 360 | 0 | 0 | 149 | 0 | -1.18135e-05 | -1.18135e-05 | -0.000794182 | -0.0044233 | 0.833333 |
| pair_deployable_sym16_e73 | 360 | 0 | 0 | 105 | 0 | -1.07462e-05 | -1.07045e-05 | -0.00100202 | -0.00467792 | 0.833333 |
| pair_all_sym16_e73 | 360 | 0 | 0 | 105 | 0 | -1.07205e-05 | -1.07205e-05 | -0.00101266 | -0.00469519 | 0.833333 |

## Best Rows

| selector_name | base_ref | agg_mode | target_scope | shrink | dominant_axis | source_rows | source_variants | source_pairs | all_delta_vs_mixmin | all_minus_base | worst_set_delta_vs_mixmin | hidden_q2s3_mean_minus_base | world_support_minus_base | block_q2s3_beats_base_rate | strict_gate | deployable_gate | loose_gate | beats_e75_local_all |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact_asym_all | e74 | signed_p90 | q2s3 | 0.75 | s3_higher | 94 | 94 | 1 | -1.26541e-05 | -1.92802e-06 | 1.14859e-05 | 3.95652e-05 | 0.000107171 | 0.555556 | False | False | False | True |
| exact_asym_all | e73 | signed_p90 | q2s3 | 1 | s3_higher | 94 | 94 | 1 | -1.26522e-05 | -2.10637e-06 | 1.21417e-05 | -2.4239e-05 | 5.58981e-05 | 0.638889 | False | False | False | True |
| exact_asym_deployable | e74 | signed_p90 | q2s3 | 1 | balanced | 49 | 49 | 1 | -1.26453e-05 | -1.91926e-06 | 1.15943e-05 | 7.84181e-05 | 0.000143185 | 0.555556 | False | False | False | True |
| exact_asym_all | e74 | signed_p90 | q2s3 | 1 | s3_higher | 94 | 94 | 1 | -1.26149e-05 | -1.88884e-06 | 1.23588e-05 | 5.49693e-05 | 0.000144482 | 0.583333 | False | False | False | True |
| exact_asym_deployable | e74 | signed_p90 | q2s3 | 0.75 | balanced | 49 | 49 | 1 | -1.26041e-05 | -1.87799e-06 | 1.10325e-05 | 5.73077e-05 | 0.000106258 | 0.527778 | False | False | False | True |
| exact_asym_deployable | mixmin | signed_p75 | full | 1 | s3_higher | 49 | 49 | 1 | -1.25991e-05 | -1.25991e-05 | 1.1598e-05 | -0.000405265 | -0.00175119 | 0.805556 | False | False | True | True |
| best_deployable_per_variant | e73 | signed_p90 | q2s3 | 1 | s3_higher | 94 | 94 | 6 | -1.25799e-05 | -2.0341e-06 | 1.1929e-05 | -2.36597e-05 | 7.43669e-05 | 0.638889 | False | False | False | True |
| best_s3_deployable_per_variant | e73 | signed_p90 | q2s3 | 1 | s3_higher | 94 | 94 | 6 | -1.25799e-05 | -2.0341e-06 | 1.1929e-05 | -2.36597e-05 | 7.43669e-05 | 0.638889 | False | False | False | True |
| exact_asym_deployable | e73 | signed_p90 | q2s3 | 1 | s3_higher | 49 | 49 | 1 | -1.25743e-05 | -2.02853e-06 | 1.14021e-05 | -1.15876e-05 | 7.70652e-05 | 0.611111 | False | False | False | True |
| exact_asym_all | e73 | signed_p90 | q2s3 | 0.75 | s3_higher | 94 | 94 | 1 | -1.25736e-05 | -2.02777e-06 | 1.11264e-05 | -1.96536e-05 | 4.1411e-05 | 0.611111 | False | False | False | True |
| exact_asym_deployable | mixmin | signed_p90 | full | 1 | s3_higher | 49 | 49 | 1 | -1.25655e-05 | -1.25655e-05 | 1.21346e-05 | -0.000405374 | -0.0017878 | 0.833333 | False | False | True | True |
| all_s3_deployable | e73 | signed_p90 | q2s3 | 1 | s3_higher | 810 | 94 | 14 | -1.25639e-05 | -2.01813e-06 | 1.17177e-05 | -1.46672e-05 | 6.65439e-05 | 0.611111 | False | False | False | True |
| exact_asym_deployable | e74 | signed_p90 | full | 1 | balanced | 49 | 49 | 1 | -1.25473e-05 | -1.82124e-06 | 1.11285e-05 | 7.84181e-05 | 0.000223582 | 0.555556 | False | False | False | True |
| pair_all_q2a8_s3a26 | e73 | signed_p90 | q2s3 | 1 | s3_higher | 94 | 94 | 1 | -1.25397e-05 | -1.9939e-06 | 1.15249e-05 | -9.253e-06 | 7.9623e-05 | 0.583333 | False | False | False | True |
| exact_asym_deployable | e74 | signed_p90 | full | 0.75 | balanced | 49 | 49 | 1 | -1.25284e-05 | -1.8023e-06 | 1.06645e-05 | 5.73077e-05 | 0.000166111 | 0.527778 | False | False | False | True |
| exact_asym_deployable | e73 | signed_p75 | q2s3 | 1 | s3_higher | 49 | 49 | 1 | -1.25241e-05 | -1.97835e-06 | 1.13465e-05 | -9.91045e-06 | 7.80546e-05 | 0.611111 | False | False | False | True |
| exact_asym_deployable | e74 | signed_p75 | q2s3 | 1 | balanced | 49 | 49 | 1 | -1.25235e-05 | -1.79744e-06 | 1.13533e-05 | 8.35159e-05 | 0.000147901 | 0.555556 | False | False | False | True |
| best_deployable_per_variant | e73 | signed_p90 | q2s3 | 0.75 | s3_higher | 94 | 94 | 6 | -1.25043e-05 | -1.95851e-06 | 1.10152e-05 | -1.92113e-05 | 5.52585e-05 | 0.611111 | False | False | False | True |
| best_s3_deployable_per_variant | e73 | signed_p90 | q2s3 | 0.75 | s3_higher | 94 | 94 | 6 | -1.25043e-05 | -1.95851e-06 | 1.10152e-05 | -1.92113e-05 | 5.52585e-05 | 0.611111 | False | False | False | True |
| exact_asym_deployable | e73 | signed_p75 | full | 1 | s3_higher | 49 | 49 | 1 | -1.24948e-05 | -1.94897e-06 | 1.08257e-05 | -9.91045e-06 | 0.000145718 | 0.611111 | False | False | False | True |
| best_s3_deployable_per_variant | mixmin | signed_p90 | full | 1 | s3_higher | 94 | 94 | 6 | -1.24935e-05 | -1.24935e-05 | 1.29648e-05 | -0.00041269 | -0.00182341 | 0.833333 | False | False | True | True |
| best_deployable_per_variant | mixmin | signed_p90 | full | 1 | s3_higher | 94 | 94 | 6 | -1.24935e-05 | -1.24935e-05 | 1.29648e-05 | -0.00041269 | -0.00182341 | 0.833333 | False | False | True | True |
| exact_asym_deployable | e74 | signed_p75 | full | 1 | balanced | 49 | 49 | 1 | -1.24928e-05 | -1.76675e-06 | 1.08365e-05 | 8.35159e-05 | 0.000215565 | 0.555556 | False | False | False | True |
| exact_asym_all | mixmin | signed_p90 | full | 1 | s3_higher | 94 | 94 | 1 | -1.24876e-05 | -1.24876e-05 | 1.30373e-05 | -0.000413201 | -0.0018252 | 0.833333 | False | False | True | True |
| pair_deployable_q2a8_s3a26 | e73 | signed_p90 | q2s3 | 1 | s3_higher | 76 | 76 | 1 | -1.24789e-05 | -1.93307e-06 | 1.14072e-05 | 2.06499e-06 | 7.6526e-05 | 0.555556 | False | False | False | True |
| exact_asym_deployable | e73 | signed_p90 | q2s3 | 0.75 | s3_higher | 49 | 49 | 1 | -1.24777e-05 | -1.93191e-06 | 1.06455e-05 | -1.00776e-05 | 5.69725e-05 | 0.583333 | False | False | False | True |
| pair_all_q2a12_s3a24 | e73 | signed_p90 | q2s3 | 1.25 | s3_higher | 94 | 94 | 1 | -1.24754e-05 | -1.92964e-06 | 1.19139e-05 | -6.92306e-05 | 3.48248e-05 | 0.666667 | False | False | False | True |
| exact_asym_deployable | e73 | signed_p90 | full | 1 | s3_higher | 49 | 49 | 1 | -1.24753e-05 | -1.92953e-06 | 1.09015e-05 | -1.15876e-05 | 0.000157368 | 0.611111 | False | False | False | True |
| exact_asym_deployable | e74 | signed_p75 | q2s3 | 0.75 | balanced | 49 | 49 | 1 | -1.24716e-05 | -1.74554e-06 | 1.08691e-05 | 6.12215e-05 | 0.000109831 | 0.5 | False | False | False | True |
| exact_asym_deployable | e74 | signed_p75 | full | 0.75 | balanced | 49 | 49 | 1 | -1.24703e-05 | -1.74423e-06 | 1.04674e-05 | 6.12215e-05 | 0.000160688 | 0.5 | False | False | False | True |

## Best Strict Rows

_None._

## Best Deployable Rows

_None._

## Decision

- Posterior aggregation does not solve the exact-amplitude instability under the current stress gate.
- This probe writes no submission. If a row is later materialized, it should be treated as an amplitude-posterior hypothesis, not as a generic ensemble.

## Outputs

- `analysis_outputs/q2_s3_amplitude_posterior_probe_scan.csv`
- `analysis_outputs/q2_s3_amplitude_posterior_probe_summary.csv`
- `analysis_outputs/q2_s3_amplitude_posterior_probe_selector_summary.csv`
