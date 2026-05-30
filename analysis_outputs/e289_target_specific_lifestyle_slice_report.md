# E289 Target-Specific Lifestyle Slice Audit

## Question

Does the E288 lifestyle bundle become useful when split by target, and can a surviving slice be safely materialized on E247 without public LB?

## Target Slice Stress

- slice rows: `84`
- target-gate rows: `7`

| slice_id | target | actual_delta | null_median | null_best | dominance | row_dominance | subject_dominance | dateblock_dominance | target_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3_raw_human_context_subject5_pc | Q3 | -0.014466 | 0.015737 | -0.029511 | 0.962963 | 1.000000 | 1.000000 | 0.888889 | True |
| S4_family_jepa_context_dateblock5_cluster6 | S4 | -0.011131 | 0.007267 | -0.003348 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | True |
| S4_raw_human_context_dateblock5_cluster6 | S4 | -0.009936 | 0.006003 | -0.003870 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | True |
| Q3_family_jepa_context_dateblock5_pc | Q3 | -0.006200 | 0.011141 | -0.011688 | 0.981481 | 1.000000 | 1.000000 | 0.944444 | True |
| Q3_raw_human_context_dateblock5_cluster6 | Q3 | -0.005295 | 0.006540 | -0.007018 | 0.962963 | 1.000000 | 1.000000 | 0.888889 | True |
| S1_raw_human_context_dateblock5_pc | S1 | -0.003654 | 0.010129 | -0.008954 | 0.962963 | 0.944444 | 1.000000 | 0.944444 | True |
| Q3_family_jepa_context_subject5_cluster6 | Q3 | -0.003437 | 0.006929 | -0.010980 | 0.944444 | 0.944444 | 0.944444 | 0.944444 | True |
| S2_family_jepa_context_dateblock5_cluster6 | S2 | -0.001378 | 0.007349 | -0.006561 | 0.851852 | 0.833333 | 0.888889 | 0.833333 | False |
| S2_raw_human_context_dateblock5_cluster6 | S2 | -0.000959 | 0.004921 | -0.008800 | 0.888889 | 0.888889 | 0.833333 | 0.944444 | False |
| Q3_hybrid_context_dateblock5_cluster6 | Q3 | -0.000482 | 0.009668 | 0.000676 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | False |
| Q3_hybrid_context_subject5_pc | Q3 | -0.000358 | 0.015701 | -0.009755 | 0.888889 | 0.944444 | 1.000000 | 0.722222 | False |
| S4_family_jepa_context_dateblock5_pc | S4 | -0.000343 | 0.009107 | -0.009790 | 0.888889 | 0.833333 | 1.000000 | 0.833333 | False |
| S4_raw_human_context_dateblock5_pc | S4 | -0.000328 | 0.015241 | -0.004907 | 0.925926 | 0.944444 | 0.888889 | 0.944444 | False |
| S3_raw_human_context_dateblock5_cluster6 | S3 | -0.000061 | 0.005142 | -0.006306 | 0.833333 | 0.888889 | 0.777778 | 0.833333 | False |
| S2_hybrid_context_dateblock5_pc | S2 | 0.000293 | 0.011251 | -0.003378 | 0.907407 | 0.944444 | 1.000000 | 0.777778 | False |
| S2_hybrid_context_dateblock5_cluster6 | S2 | 0.001751 | 0.004848 | -0.006719 | 0.777778 | 0.833333 | 0.833333 | 0.666667 | False |
| Q3_hybrid_context_dateblock5_pc | Q3 | 0.002315 | 0.012328 | 0.001391 | 0.962963 | 0.944444 | 1.000000 | 0.944444 | False |
| Q2_family_jepa_context_dateblock5_cluster6 | Q2 | 0.002350 | 0.008932 | -0.010336 | 0.907407 | 0.944444 | 0.833333 | 0.944444 | False |
| Q2_raw_human_context_dateblock5_cluster6 | Q2 | 0.002759 | 0.005773 | -0.006580 | 0.740741 | 0.666667 | 0.833333 | 0.722222 | False |
| S4_hybrid_context_dateblock5_pc | S4 | 0.003758 | 0.012059 | -0.007093 | 0.759259 | 0.611111 | 0.833333 | 0.833333 | False |
| S4_hybrid_context_dateblock5_cluster6 | S4 | 0.004246 | 0.007316 | -0.004448 | 0.740741 | 0.777778 | 0.722222 | 0.722222 | False |
| Q2_hybrid_context_dateblock5_pc | Q2 | 0.004821 | 0.013608 | 0.001108 | 0.888889 | 1.000000 | 0.833333 | 0.833333 | False |
| Q2_hybrid_context_dateblock5_cluster6 | Q2 | 0.005086 | 0.006062 | -0.005464 | 0.629630 | 0.611111 | 0.611111 | 0.666667 | False |
| Q1_family_jepa_context_subject5_cluster6 | Q1 | 0.005176 | 0.007660 | -0.011181 | 0.611111 | 0.777778 | 0.666667 | 0.388889 | False |
| Q2_raw_human_context_subject5_pc | Q2 | 0.005612 | 0.019143 | -0.017550 | 0.759259 | 0.722222 | 0.777778 | 0.777778 | False |
| S3_hybrid_context_subject5_pc | S3 | 0.005710 | 0.015226 | -0.013726 | 0.833333 | 0.777778 | 0.722222 | 1.000000 | False |
| S1_hybrid_context_dateblock5_cluster6 | S1 | 0.005730 | 0.006309 | -0.012700 | 0.574074 | 0.555556 | 0.666667 | 0.500000 | False |
| Q2_raw_human_context_dateblock5_pc | Q2 | 0.006155 | 0.013014 | -0.007638 | 0.722222 | 0.555556 | 0.888889 | 0.722222 | False |
| S3_hybrid_context_dateblock5_cluster6 | S3 | 0.006783 | 0.008088 | -0.007650 | 0.592593 | 0.555556 | 0.611111 | 0.611111 | False |
| S2_family_jepa_context_subject5_cluster6 | S2 | 0.007825 | 0.006458 | -0.005835 | 0.388889 | 0.555556 | 0.222222 | 0.388889 | False |
| Q3_family_jepa_context_dateblock5_cluster6 | Q3 | 0.008211 | 0.010042 | -0.009944 | 0.592593 | 0.666667 | 0.388889 | 0.722222 | False |
| Q1_raw_human_context_dateblock5_cluster6 | Q1 | 0.008679 | 0.004439 | -0.009577 | 0.185185 | 0.333333 | 0.166667 | 0.055556 | False |
| S3_family_jepa_context_dateblock5_cluster6 | S3 | 0.009601 | 0.008027 | -0.010651 | 0.388889 | 0.444444 | 0.444444 | 0.277778 | False |
| S1_family_jepa_context_dateblock5_pc | S1 | 0.009871 | 0.011056 | -0.001368 | 0.574074 | 0.555556 | 0.666667 | 0.500000 | False |
| Q1_hybrid_context_dateblock5_cluster6 | Q1 | 0.010074 | 0.007643 | -0.006018 | 0.296296 | 0.333333 | 0.277778 | 0.277778 | False |
| Q2_family_jepa_context_subject5_pc | Q2 | 0.010233 | 0.022976 | -0.008193 | 0.814815 | 0.611111 | 0.833333 | 1.000000 | False |
| S3_hybrid_context_dateblock5_pc | S3 | 0.010297 | 0.010999 | -0.005173 | 0.518519 | 0.555556 | 0.500000 | 0.500000 | False |
| S3_family_jepa_context_dateblock5_pc | S3 | 0.010371 | 0.008764 | -0.007510 | 0.351852 | 0.500000 | 0.333333 | 0.222222 | False |
| S1_family_jepa_context_subject5_cluster6 | S1 | 0.010508 | 0.009747 | 0.000133 | 0.462963 | 0.611111 | 0.388889 | 0.388889 | False |
| Q1_raw_human_context_dateblock5_pc | Q1 | 0.010662 | 0.012032 | -0.006569 | 0.537037 | 0.666667 | 0.500000 | 0.444444 | False |

## Materialization Governor

- candidates: `28`
- public-free ready candidates: `0`

| basename | target | view_id | split | rep | delta_mode | scale | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e289_lifeslice_Q3_family_jepa_context_subject5_cluster6_raw_s050_09f712a2.csv | Q3 | family_jepa_context | subject5 | cluster6 | raw | 0.500000 | promote_candidate | -0.000674 | -0.000417 | 1.000000 | 0.466667 | 0.000000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_centered_s050_a5007702.csv | Q3 | family_jepa_context | dateblock5 | pc | centered | 0.500000 | promote_candidate | -0.000583 | -0.000399 | 1.000000 | 0.800000 | 0.600000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_Q3_raw_human_context_dateblock5_cluster6_raw_s050_e502ea53.csv | Q3 | raw_human_context | dateblock5 | cluster6 | raw | 0.500000 | promote_candidate | -0.000719 | -0.000386 | 1.000000 | 0.533333 | 0.400000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_S4_family_jepa_context_dateblock5_cluster6_raw_s050_a32b1096.csv | S4 | family_jepa_context | dateblock5 | cluster6 | raw | 0.500000 | promote_candidate | -0.000865 | -0.000269 | 1.000000 | 0.800000 | 0.400000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_S4_raw_human_context_dateblock5_cluster6_raw_s050_7a8e30f1.csv | S4 | raw_human_context | dateblock5 | cluster6 | raw | 0.500000 | promote_candidate | -0.000742 | -0.000238 | 1.000000 | 0.600000 | 0.400000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_Q3_family_jepa_context_subject5_cluster6_raw_s025_8e4a42d3.csv | Q3 | family_jepa_context | subject5 | cluster6 | raw | 0.250000 | promote_candidate | -0.000318 | -0.000210 | 1.000000 | 0.666667 | 0.200000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_Q3_raw_human_context_dateblock5_cluster6_raw_s025_dcf6ef83.csv | Q3 | raw_human_context | dateblock5 | cluster6 | raw | 0.250000 | promote_candidate | -0.000343 | -0.000194 | 1.000000 | 0.800000 | 0.400000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_centered_s025_78b305b4.csv | Q3 | family_jepa_context | dateblock5 | pc | centered | 0.250000 | promote_candidate | -0.000283 | -0.000190 | 1.000000 | 0.533333 | 0.400000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_Q3_raw_human_context_subject5_pc_centered_s050_726a66f2.csv | Q3 | raw_human_context | subject5 | pc | centered | 0.500000 | promote_candidate | -0.000300 | -0.000156 | 1.000000 | 0.000000 | 0.000000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_S4_family_jepa_context_dateblock5_cluster6_raw_s025_7028d955.csv | S4 | family_jepa_context | dateblock5 | cluster6 | raw | 0.250000 | promote_candidate | -0.000446 | -0.000127 | 1.000000 | 0.866667 | 0.600000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_S4_raw_human_context_dateblock5_cluster6_raw_s025_ed16db5d.csv | S4 | raw_human_context | dateblock5 | cluster6 | raw | 0.250000 | promote_candidate | -0.000386 | -0.000114 | 1.000000 | 0.600000 | 0.200000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_Q3_raw_human_context_subject5_pc_centered_s025_c4162f27.csv | Q3 | raw_human_context | subject5 | pc | centered | 0.250000 | promote_candidate | -0.000134 | -0.000079 | 1.000000 | 0.066667 | 0.000000 | blocked_by_matched_nulls |
| submission_e289_lifeslice_S1_raw_human_context_dateblock5_pc_raw_s050_d8b40b15.csv | S1 | raw_human_context | dateblock5 | pc | raw | 0.500000 | too_small_to_submit | -0.000090 | 0.000010 | 0.266667 | 0.466667 | 0.000000 | too_small_to_submit |
| submission_e289_lifeslice_S1_raw_human_context_dateblock5_pc_centered_s050_139a16bf.csv | S1 | raw_human_context | dateblock5 | pc | centered | 0.500000 | too_small_to_submit | -0.000389 | 0.000010 | 0.000000 | 0.466667 | 0.400000 | too_small_to_submit |
| submission_e289_lifeslice_S1_raw_human_context_dateblock5_pc_centered_s025_12cb13a6.csv | S1 | raw_human_context | dateblock5 | pc | centered | 0.250000 | too_small_to_submit | -0.000182 | 0.000013 | 0.000000 | 0.600000 | 0.600000 | too_small_to_submit |
| submission_e289_lifeslice_S1_raw_human_context_dateblock5_pc_raw_s025_7b9ff5c6.csv | S1 | raw_human_context | dateblock5 | pc | raw | 0.250000 | below_selector_resolution | -0.000018 | 0.000029 | 0.066667 | 0.333333 | 0.000000 | below_selector_resolution |
| submission_e289_lifeslice_Q3_raw_human_context_subject5_pc_raw_s025_10f4f218.csv | Q3 | raw_human_context | subject5 | pc | raw | 0.250000 | below_selector_resolution | 0.000038 | 0.000070 | 0.000000 | 0.066667 | 0.000000 | below_selector_resolution |
| submission_e289_lifeslice_Q3_raw_human_context_subject5_pc_raw_s050_e6ddbb9c.csv | Q3 | raw_human_context | subject5 | pc | raw | 0.500000 | below_selector_resolution | 0.000028 | 0.000137 | 0.000000 | 0.066667 | 0.000000 | below_selector_resolution |
| submission_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_raw_s025_750b0763.csv | Q3 | family_jepa_context | dateblock5 | pc | raw | 0.250000 | block_or_reject | 0.000128 | 0.000160 | 0.000000 | 0.466667 | 0.200000 | block_or_reject |
| submission_e289_lifeslice_Q3_raw_human_context_dateblock5_cluster6_centered_s025_8d52bc40.csv | Q3 | raw_human_context | dateblock5 | cluster6 | centered | 0.250000 | block_or_reject | 0.000190 | 0.000237 | 0.000000 | 0.866667 | 0.800000 | block_or_reject |
| submission_e289_lifeslice_Q3_family_jepa_context_subject5_cluster6_centered_s025_dc4a6957.csv | Q3 | family_jepa_context | subject5 | cluster6 | centered | 0.250000 | block_or_reject | 0.000195 | 0.000243 | 0.000000 | 0.800000 | 0.600000 | block_or_reject |
| submission_e289_lifeslice_Q3_family_jepa_context_dateblock5_pc_raw_s050_761585f9.csv | Q3 | family_jepa_context | dateblock5 | pc | raw | 0.500000 | block_or_reject | 0.000210 | 0.000304 | 0.000000 | 0.666667 | 0.400000 | block_or_reject |
| submission_e289_lifeslice_S4_family_jepa_context_dateblock5_cluster6_centered_s025_9643309a.csv | S4 | family_jepa_context | dateblock5 | cluster6 | centered | 0.250000 | below_selector_resolution | 0.000239 | 0.000412 | 0.000000 | 0.533333 | 0.200000 | below_selector_resolution |
| submission_e289_lifeslice_S4_raw_human_context_dateblock5_cluster6_centered_s025_c4c96e6b.csv | S4 | raw_human_context | dateblock5 | cluster6 | centered | 0.250000 | below_selector_resolution | 0.000250 | 0.000431 | 0.000000 | 0.533333 | 0.000000 | below_selector_resolution |
| submission_e289_lifeslice_Q3_raw_human_context_dateblock5_cluster6_centered_s050_5795b74f.csv | Q3 | raw_human_context | dateblock5 | cluster6 | centered | 0.500000 | block_or_reject | 0.000366 | 0.000459 | 0.000000 | 0.866667 | 0.600000 | block_or_reject |
| submission_e289_lifeslice_Q3_family_jepa_context_subject5_cluster6_centered_s050_8d8db650.csv | Q3 | family_jepa_context | subject5 | cluster6 | centered | 0.500000 | block_or_reject | 0.000373 | 0.000460 | 0.000000 | 0.333333 | 0.200000 | block_or_reject |
| submission_e289_lifeslice_S4_family_jepa_context_dateblock5_cluster6_centered_s050_9c1e103a.csv | S4 | family_jepa_context | dateblock5 | cluster6 | centered | 0.500000 | block_or_reject | 0.000484 | 0.000837 | 0.000000 | 0.600000 | 0.200000 | block_or_reject |
| submission_e289_lifeslice_S4_raw_human_context_dateblock5_cluster6_centered_s050_126fa814.csv | S4 | raw_human_context | dateblock5 | cluster6 | centered | 0.500000 | block_or_reject | 0.000509 | 0.000880 | 0.000000 | 0.533333 | 0.200000 | block_or_reject |

## Decision

No E289 candidate is public-free ready. Keep target-specific lifestyle slices as diagnostics until they pass the current-anchor matched-null governor.

## Interpretation

This experiment is stricter than E288. A target can improve locally and still fail if the resulting current-submission delta is too small, selector-adverse, or reproducible by row/subject/dateblock shuffles.

## Files

- `e289_target_specific_lifestyle_slice_summary.csv`
- `e289_target_specific_lifestyle_slice_target_nulls.csv`
- `e289_target_specific_lifestyle_slice_candidate_summary.csv`
- `e289_target_specific_lifestyle_slice_governor_summary.csv`
