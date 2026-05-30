# E294 S4 Candidate-Level Invariant Audit

## Question

Can the real E293 S4 lifestyle placement be distinguished from matched row/subject/dateblock null placements before spending public LB?

## Data

- E293 candidate sources: `64`
- matched null rows: `1344`
- public LB used: `0`

## LOO Actual-vs-Null Distinguishability

| feature_set | n_features | row_auc_actual_vs_null | mean_actual_rank | top1_rate | top3_rate | mean_actual_dominance | spearman_realness_vs_null_strict_rate | spearman_realness_vs_actual_p90 | spearman_realness_vs_mean_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_output | 57 | 0.883498 | 2.921875 | 0.281250 | 0.671875 | 0.908482 | 0.360322 | -0.328407 | 0.183302 |
| selector | 15 | 0.849865 | 3.843750 | 0.156250 | 0.546875 | 0.864583 | 0.478847 | -0.338435 | 0.045175 |
| anchor_geometry | 32 | 0.828462 | 3.687500 | 0.218750 | 0.656250 | 0.872024 | 0.176839 | -0.163505 | -0.023995 |
| s4_local | 11 | 0.619617 | 7.828125 | 0.015625 | 0.203125 | 0.674851 | 0.093948 | -0.149904 | 0.012549 |

## Feature Percentiles

| feature | actual_better_direction | mean_actual_better_than_null_rate | median_actual_better_than_null_rate | source_rate_ge_0p8 | source_rate_le_0p2 |
| --- | --- | --- | --- | --- | --- |
| pred_delta_vs_current_p90 | lower | 0.765625 | 0.785714 | 0.500000 | 0.000000 |
| move_abs_a2c8_S4 | higher | 0.686756 | 0.690476 | 0.296875 | 0.000000 |
| bad_axis_abs_load | lower | 0.558780 | 0.619048 | 0.140625 | 0.062500 |
| mean_prob_S4 | higher | 0.472470 | 0.476190 | 0.000000 | 0.000000 |
| pred_delta_vs_current_p10 | lower | 0.401042 | 0.380952 | 0.000000 | 0.031250 |
| pred_delta_vs_current_mean | lower | 0.394345 | 0.380952 | 0.000000 | 0.046875 |
| raw05_a2c8_compat_energy | lower | 0.354167 | 0.380952 | 0.000000 | 0.218750 |

## Top Realness Candidates

| basename | rule | scale | selected_rows | selected_null_max_rate | actual_p90 | actual_mean | null_strict_rate | mean_dominance | all_output_realness | all_output_rank | all_output_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_contras_beece709.csv | contrast_top28 | 0.600000 | 141 | 0.677579 | -0.000200 | -0.000688 | 1.000000 | 0.714286 | 0.948958 | 5 | 0.809524 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_mean_good_subject_cv_contra_079ecc8d.csv | contrast_top28 | 0.500000 | 165 | 0.709325 | -0.000200 | -0.000719 | 1.000000 | 0.523810 | 0.940241 | 1 | 1.000000 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_mean_good_subject_cv_contra_bfc29cdb.csv | contrast_top28 | 0.550000 | 165 | 0.709325 | -0.000223 | -0.000786 | 1.000000 | 0.571429 | 0.921636 | 3 | 0.904762 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__8e8ac46c.csv | hybrid_low45_top12 | 0.600000 | 60 | 0.247685 | -0.000102 | -0.000374 | 1.000000 | 0.333333 | 0.916990 | 1 | 1.000000 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__aa751036.csv | hybrid_low45_top12 | 0.550000 | 60 | 0.247685 | -0.000093 | -0.000344 | 1.000000 | 0.476190 | 0.902037 | 1 | 1.000000 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_contras_cfd77d78.csv | contrast_top28 | 0.500000 | 153 | 0.374008 | -0.000185 | -0.000614 | 1.000000 | 0.333333 | 0.885189 | 2 | 0.952381 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__d8d1bc98.csv | hybrid_low45_top12 | 0.500000 | 60 | 0.247685 | -0.000083 | -0.000315 | 1.000000 | 0.333333 | 0.878911 | 2 | 0.952381 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_mean_good_subject_cv_contra_dc1a79ee.csv | contrast_top28 | 0.600000 | 165 | 0.709325 | -0.000245 | -0.000853 | 1.000000 | 0.666667 | 0.878429 | 2 | 0.952381 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_contras_56f5a5c8.csv | contrast_top28 | 0.550000 | 153 | 0.374008 | -0.000206 | -0.000670 | 1.000000 | 0.190476 | 0.875760 | 3 | 0.904762 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__6ed4511c.csv | rarity_top12 | 0.600000 | 47 | 0.256944 | -0.000065 | -0.000245 | 0.952381 | 0.428571 | 0.867298 | 1 | 1.000000 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__6ed4511c.csv | hybrid_low55_top12 | 0.600000 | 47 | 0.256944 | -0.000065 | -0.000245 | 0.904762 | 0.333333 | 0.867292 | 1 | 1.000000 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_contras_c4efeaf6.csv | contrast_top28 | 0.450000 | 153 | 0.374008 | -0.000164 | -0.000557 | 1.000000 | 0.380952 | 0.854872 | 2 | 0.952381 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__a98231a0.csv | hybrid_low55_top12 | 0.550000 | 47 | 0.256944 | -0.000058 | -0.000226 | 0.904762 | 0.523810 | 0.849455 | 1 | 1.000000 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__a98231a0.csv | rarity_top12 | 0.550000 | 47 | 0.256944 | -0.000058 | -0.000226 | 0.809524 | 0.380952 | 0.847726 | 1 | 1.000000 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__6427a1fb.csv | hybrid_low45_top12 | 0.450000 | 60 | 0.247685 | -0.000074 | -0.000284 | 1.000000 | 0.380952 | 0.847492 | 1 | 1.000000 | blocked_by_matched_nulls |

## Top Safety-Adjusted Realness

| basename | rule | scale | selected_rows | selected_null_max_rate | actual_p90 | actual_mean | null_strict_rate | mean_dominance | realness_safety_score | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__8e8ac46c.csv | hybrid_low45_top12 | 0.600000 | 60 | 0.247685 | -0.000102 | -0.000374 | 1.000000 | 0.333333 | 0.757644 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__aa751036.csv | hybrid_low45_top12 | 0.550000 | 60 | 0.247685 | -0.000093 | -0.000344 | 1.000000 | 0.476190 | 0.742692 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__d8d1bc98.csv | hybrid_low45_top12 | 0.500000 | 60 | 0.247685 | -0.000083 | -0.000315 | 1.000000 | 0.333333 | 0.719566 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__6ed4511c.csv | rarity_top12 | 0.600000 | 47 | 0.256944 | -0.000065 | -0.000245 | 0.952381 | 0.428571 | 0.711015 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__6ed4511c.csv | hybrid_low55_top12 | 0.600000 | 47 | 0.256944 | -0.000065 | -0.000245 | 0.904762 | 0.333333 | 0.711009 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__a98231a0.csv | hybrid_low55_top12 | 0.550000 | 47 | 0.256944 | -0.000058 | -0.000226 | 0.904762 | 0.523810 | 0.693172 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__a98231a0.csv | rarity_top12 | 0.550000 | 47 | 0.256944 | -0.000058 | -0.000226 | 0.809524 | 0.380952 | 0.691443 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__6427a1fb.csv | hybrid_low45_top12 | 0.450000 | 60 | 0.247685 | -0.000074 | -0.000284 | 1.000000 | 0.380952 | 0.688147 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__0da73dd5.csv | hybrid_low55_top12 | 0.500000 | 47 | 0.256944 | -0.000052 | -0.000207 | 0.619048 | 0.380952 | 0.665149 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__0da73dd5.csv | rarity_top12 | 0.500000 | 47 | 0.256944 | -0.000052 | -0.000207 | 0.523810 | 0.523810 | 0.663164 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__ca75314c.csv | hybrid_low45_top12 | 0.400000 | 60 | 0.247685 | -0.000066 | -0.000254 | 0.857143 | 0.333333 | 0.652702 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__b62bc0b6.csv | rarity_top16 | 0.600000 | 84 | 0.265625 | -0.000144 | -0.000526 | 1.000000 | 0.380952 | 0.645448 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__b62bc0b6.csv | hybrid_low55_top16 | 0.600000 | 84 | 0.265625 | -0.000144 | -0.000526 | 1.000000 | 0.428571 | 0.643996 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__6fad25e5.csv | hybrid_low45_top12 | 0.350000 | 60 | 0.247685 | -0.000057 | -0.000223 | 0.619048 | 0.333333 | 0.611026 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_contras_cfd77d78.csv | contrast_top28 | 0.500000 | 153 | 0.374008 | -0.000185 | -0.000614 | 1.000000 | 0.333333 | 0.607652 | blocked_by_matched_nulls |

## Near Low-Null Old-Strict Rows

| basename | rule | scale | selected_rows | selected_null_max_rate | actual_p90 | actual_mean | null_strict_rate | p90_dominance | mean_dominance | all_output_realness | all_output_rank | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_hybrid__c23d5570.csv | hybrid_low45_top8 | 0.600000 | 31 | 0.232639 | -0.000055 | -0.000211 | 0.476190 | 0.761905 | 0.428571 | 0.554910 | 5 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__c23d5570.csv | rarity_top8 | 0.600000 | 31 | 0.232639 | -0.000055 | -0.000211 | 0.523810 | 0.761905 | 0.380952 | 0.557442 | 7 | blocked_by_matched_nulls |
| submission_e293_s4lownull_S4_family_jepa_context_dateblock5_cluster6_subject_lifestyle_bin_strong35_subject_cv_rarity__0da73dd5.csv | rarity_top12 | 0.500000 | 47 | 0.256944 | -0.000052 | -0.000207 | 0.523810 | 0.523810 | 0.523810 | 0.819447 | 1 | blocked_by_matched_nulls |

## Decision

No E294 candidate is public-free ready. Do not submit E293 S4 low-null files.

## Interpretation

The best actual-vs-null classifier is `all_output` with AUC `0.883498` and top3 rate `0.671875`. So the actual placement is visible in output/selector space.

But that visibility is not a healthy LeJEPA gate. Realness is positively associated with null strict promotion, while the actual placement mainly beats nulls on p90 rather than mean. In plain terms: the model can recognize the designed S4 movement, but the recognizable part is also the part matched nulls can exploit.

The S4 lifestyle state remains a diagnostic hidden state, not a submission tensor. The next useful experiment must change the target from `actual-vs-null identity` to `selector-visible and null-rare outcome`, or move to a new hidden-state axis with more positive examples.

## Files

- `e294_s4_candidate_invariant_summary.csv`
- `e294_s4_candidate_invariant_candidate_scores.csv`
- `e294_s4_candidate_invariant_feature_percentiles.csv`
