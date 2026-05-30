# E189 Shape/Support Disagreement Atlas

## Question

E187/E188 showed that support-heavy known-LB pair geometry helps wider edge
stress but breaks the exact E95/E101 boundary. Are support's wins broad, or are
they just one anchor family?

## Result In One Sentence

In the primary file-LOO E95-edge slice, support rescues `6` rows and shape-only wins `4` rows; support rescues are E72-frontier-neighbor rows at rate `1.000`, while shape-only wins are exact E95/E101 rows at rate `1.000`.

## Primary Edge-Band Disagreements

| disagreement_class | heldout | new_tag | base_tag | actual_delta | p_shape | p_support | pair_context | pair_is_e72_frontier_neighbor | pair_is_e95_e101 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only_win | submission_e101_q2s3tail_177569bc.csv | e95 | e101 | -0.000009036 | 0.761887945 | 0.008316839 | e101__e95 | False | True |
| shape_only_win | submission_e95_hardtail_541e3973.csv | e95 | e101 | -0.000009036 | 0.763466174 | 0.005541812 | e101__e95 | False | True |
| shape_only_win | submission_e101_q2s3tail_177569bc.csv | e101 | e95 | 0.000009036 | 0.238112055 | 0.991683161 | e101__e95 | False | True |
| shape_only_win | submission_e95_hardtail_541e3973.csv | e101 | e95 | 0.000009036 | 0.236533826 | 0.994458188 | e101__e95 | False | True |
| support_rescue | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e95 | e72 | -0.000116447 | 0.044992239 | 0.638510495 | e72__e95 | True | False |
| support_rescue | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e101 | e72 | -0.000107411 | 0.041866854 | 0.616938852 | e101__e72 | True | False |
| support_rescue | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | mixmin | e72 | -0.000101137 | 0.274057021 | 0.869573546 | e72__mixmin | True | False |
| support_rescue | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e72 | mixmin | 0.000101137 | 0.725942979 | 0.130426454 | e72__mixmin | True | False |
| support_rescue | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e72 | e101 | 0.000107411 | 0.958133146 | 0.383061148 | e101__e72 | True | False |
| support_rescue | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e72 | e95 | 0.000116447 | 0.955007761 | 0.361489505 | e72__e95 | True | False |

## Disagreement Summary

| support_variant | slice | n_rows | shape_accuracy | support_accuracy | both_correct | support_rescue | shape_only_win | both_wrong | e72_neighbor_share | exact_e95_e101_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_support | all | 264 | 0.795454545 | 0.795454545 | 196 | 14 | 14 | 40 | 0.045454545 | 0.015151515 |
| shape_support | e72_frontier_neighbor | 12 | 0.500000000 | 1.000000000 | 6 | 6 | 0 | 0 | 1.000000000 | 0.000000000 |
| shape_support | e95_edge | 28 | 0.785714286 | 0.857142857 | 18 | 6 | 4 | 0 | 0.428571429 | 0.142857143 |
| shape_support | exact_e95_e101 | 4 | 1.000000000 | 0.000000000 | 0 | 0 | 4 | 0 | 0.000000000 | 1.000000000 |
| shape_support | frontier | 60 | 0.833333333 | 0.866666667 | 46 | 6 | 4 | 4 | 0.200000000 | 0.066666667 |
| shape_support | micro | 32 | 0.750000000 | 0.812500000 | 20 | 6 | 4 | 2 | 0.375000000 | 0.125000000 |
| shape_support_drop_subject | all | 264 | 0.795454545 | 0.803030303 | 196 | 16 | 14 | 38 | 0.045454545 | 0.015151515 |
| shape_support_drop_subject | e72_frontier_neighbor | 12 | 0.500000000 | 1.000000000 | 6 | 6 | 0 | 0 | 1.000000000 | 0.000000000 |
| shape_support_drop_subject | e95_edge | 28 | 0.785714286 | 0.857142857 | 18 | 6 | 4 | 0 | 0.428571429 | 0.142857143 |
| shape_support_drop_subject | exact_e95_e101 | 4 | 1.000000000 | 0.000000000 | 0 | 0 | 4 | 0 | 0.000000000 | 1.000000000 |
| shape_support_drop_subject | frontier | 60 | 0.833333333 | 0.900000000 | 46 | 8 | 4 | 2 | 0.200000000 | 0.066666667 |
| shape_support_drop_subject | micro | 32 | 0.750000000 | 0.812500000 | 20 | 6 | 4 | 2 | 0.375000000 | 0.125000000 |
| shape_support_keep_hard_only | all | 264 | 0.795454545 | 0.787878788 | 186 | 22 | 24 | 32 | 0.045454545 | 0.015151515 |
| shape_support_keep_hard_only | e72_frontier_neighbor | 12 | 0.500000000 | 0.666666667 | 6 | 2 | 0 | 4 | 1.000000000 | 0.000000000 |
| shape_support_keep_hard_only | e95_edge | 28 | 0.785714286 | 0.642857143 | 16 | 2 | 6 | 4 | 0.428571429 | 0.142857143 |
| shape_support_keep_hard_only | exact_e95_e101 | 4 | 1.000000000 | 0.000000000 | 0 | 0 | 4 | 0 | 0.000000000 | 1.000000000 |
| shape_support_keep_hard_only | frontier | 60 | 0.833333333 | 0.733333333 | 42 | 2 | 8 | 8 | 0.200000000 | 0.066666667 |
| shape_support_keep_hard_only | micro | 32 | 0.750000000 | 0.625000000 | 18 | 2 | 6 | 6 | 0.375000000 | 0.125000000 |

## Gate Scores

| support_variant | gate | slice | n_rows | accuracy | auc | logloss | support_use_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shape_support | support_only_on_e72_frontier_neighbors | all | 264 | 0.818181818 | 0.899563820 | 0.443015335 | 0.045454545 |
| shape_support | support_on_e72_or_shape_exact | all | 264 | 0.818181818 | 0.899563820 | 0.443015335 | 0.045454545 |
| shape_support | support_with_exact_e95e101_veto | all | 264 | 0.810606061 | 0.853592746 | 0.652222346 | 0.984848485 |
| shape_support | shape_only | all | 264 | 0.795454545 | 0.880567034 | 0.496629149 | 0.000000000 |
| shape_support | support_only | all | 264 | 0.795454545 | 0.834768136 | 0.723760713 | 1.000000000 |
| shape_support | support_only | e72_frontier_neighbor | 12 | 1.000000000 | 1.000000000 | 0.198853313 | 1.000000000 |
| shape_support | support_with_exact_e95e101_veto | e72_frontier_neighbor | 12 | 1.000000000 | 1.000000000 | 0.198853313 | 1.000000000 |
| shape_support | support_only_on_e72_frontier_neighbors | e72_frontier_neighbor | 12 | 1.000000000 | 1.000000000 | 0.198853313 | 1.000000000 |
| shape_support | support_on_e72_or_shape_exact | e72_frontier_neighbor | 12 | 1.000000000 | 1.000000000 | 0.198853313 | 1.000000000 |
| shape_support | shape_only | e72_frontier_neighbor | 12 | 0.500000000 | 0.416666667 | 1.378357218 | 0.000000000 |
| shape_support | support_with_exact_e95e101_veto | e95_edge | 28 | 1.000000000 | 1.000000000 | 0.197874928 | 0.857142857 |
| shape_support | support_only_on_e72_frontier_neighbors | e95_edge | 28 | 1.000000000 | 1.000000000 | 0.310402228 | 0.428571429 |
| shape_support | support_on_e72_or_shape_exact | e95_edge | 28 | 1.000000000 | 1.000000000 | 0.310402228 | 0.428571429 |
| shape_support | support_only | e95_edge | 28 | 0.857142857 | 0.734693878 | 0.872379531 | 1.000000000 |
| shape_support | shape_only | e95_edge | 28 | 0.785714286 | 0.678571429 | 0.815903902 | 0.000000000 |
| shape_support | shape_only | exact_e95_e101 | 4 | 1.000000000 | 1.000000000 | 0.270921124 | 0.000000000 |
| shape_support | support_with_exact_e95e101_veto | exact_e95_e101 | 4 | 1.000000000 | 1.000000000 | 0.270921124 | 0.000000000 |
| shape_support | support_only_on_e72_frontier_neighbors | exact_e95_e101 | 4 | 1.000000000 | 1.000000000 | 0.270921124 | 0.000000000 |
| shape_support | support_on_e72_or_shape_exact | exact_e95_e101 | 4 | 1.000000000 | 1.000000000 | 0.270921124 | 0.000000000 |
| shape_support | support_only | exact_e95_e101 | 4 | 0.000000000 | 0.000000000 | 4.992453345 | 1.000000000 |
| shape_support | support_with_exact_e95e101_veto | frontier | 60 | 0.933333333 | 0.995555556 | 0.194829340 | 0.933333333 |
| shape_support | support_only_on_e72_frontier_neighbors | frontier | 60 | 0.933333333 | 0.962222222 | 0.283340764 | 0.200000000 |
| shape_support | support_on_e72_or_shape_exact | frontier | 60 | 0.933333333 | 0.962222222 | 0.283340764 | 0.200000000 |
| shape_support | support_only | frontier | 60 | 0.866666667 | 0.866666667 | 0.509598155 | 1.000000000 |
| shape_support | shape_only | frontier | 60 | 0.833333333 | 0.832222222 | 0.519241545 | 0.000000000 |
| shape_support | support_with_exact_e95e101_veto | micro | 32 | 0.937500000 | 0.902343750 | 0.371157689 | 0.875000000 |
| shape_support | support_only_on_e72_frontier_neighbors | micro | 32 | 0.937500000 | 0.902343750 | 0.474992273 | 0.375000000 |
| shape_support | support_on_e72_or_shape_exact | micro | 32 | 0.937500000 | 0.902343750 | 0.474992273 | 0.375000000 |
| shape_support | support_only | micro | 32 | 0.812500000 | 0.683593750 | 0.961349216 | 1.000000000 |
| shape_support | shape_only | micro | 32 | 0.750000000 | 0.609375000 | 0.917306237 | 0.000000000 |

## Structural Feature Differences

| feature | family | support_rescue_abs_mean | shape_only_win_abs_mean | abs_mean_diff_rescue_minus_shapewin | support_rescue_aligned_mean | shape_only_win_aligned_mean | aligned_mean_diff_rescue_minus_shapewin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| z__sup_top1_flank_mean_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top1_all_prior_adverse_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | -1.000000000 | 1.000000000 | -2.000000000 |
| z__sup_top1_subject_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top4_flank_mean_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top4_focus_mean_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top1_nearest_hard085_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top1_global_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top1_focus_mean_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top1_all_prior_support_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top4_nearest_hard085_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top1_visible_mean_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top4_visible_mean_hard_rate | support | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__shape_top1_support_label_swing | shape | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__shape_top1_support_label_mean | shape | 1.000000000 | 1.000000000 | 0.000000000 | 1.000000000 | -1.000000000 | 2.000000000 |
| z__sup_top16_flank_mean_hard_rate | support | 0.750000000 | 0.875000000 | -0.125000000 | 0.750000000 | -0.875000000 | 1.625000000 |
| z__sup_top16_visible_mean_hard_rate | support | 0.750000000 | 0.875000000 | -0.125000000 | 0.750000000 | -0.875000000 | 1.625000000 |
| z__sup_top4_all_prior_adverse_rate | support | 0.583333333 | 1.000000000 | -0.416666667 | -0.583333333 | 1.000000000 | -1.583333333 |
| z__sup_top4_all_prior_support_rate | support | 0.583333333 | 1.000000000 | -0.416666667 | 0.583333333 | -1.000000000 | 1.583333333 |
| z__sup_top4_subject_hard_rate | support | 0.500000000 | 1.000000000 | -0.500000000 | 0.500000000 | -1.000000000 | 1.500000000 |
| z__sup_top16_nearest_hard085_hard_rate | support | 0.708333333 | 0.750000000 | -0.041666667 | 0.708333333 | -0.750000000 | 1.458333333 |
| z__sup_top16_focus_mean_hard_rate | support | 0.708333333 | 0.750000000 | -0.041666667 | 0.708333333 | -0.750000000 | 1.458333333 |
| z__sup_top4_flank_mean_swing | support | 0.491980577 | 0.919124349 | -0.427143772 | 0.491980577 | -0.919124349 | 1.411104926 |
| z__sup_top4_flank_mean_mean | support | 0.492549932 | 0.918268789 | -0.425718857 | 0.492549932 | -0.918268789 | 1.410818721 |
| z__sup_top4_nearest_hard085_swing | support | 0.700000000 | 0.700000000 | 0.000000000 | 0.700000000 | -0.700000000 | 1.400000000 |
| z__sup_top1_nearest_hard085_swing | support | 0.700000000 | 0.700000000 | 0.000000000 | 0.700000000 | -0.700000000 | 1.400000000 |
| z__sup_top4_nearest_hard085_mean | support | 0.700000000 | 0.700000000 | 0.000000000 | 0.700000000 | -0.700000000 | 1.400000000 |
| z__sup_top1_nearest_hard085_mean | support | 0.700000000 | 0.700000000 | 0.000000000 | 0.700000000 | -0.700000000 | 1.400000000 |
| z__sup_top16_subject_hard_rate | support | 0.583333333 | 0.750000000 | -0.166666667 | 0.583333333 | -0.750000000 | 1.333333333 |
| z__target_top1_S3_support_swing | target | 0.333333333 | 1.000000000 | -0.666666667 | 0.333333333 | -1.000000000 | 1.333333333 |
| z__sup_top4_global_hard_rate | support | 0.333333333 | 1.000000000 | -0.666666667 | 0.333333333 | -1.000000000 | 1.333333333 |
| z__target_top4_S3_support_swing | target | 0.333333333 | 1.000000000 | -0.666666667 | 0.333333333 | -1.000000000 | 1.333333333 |
| z__shape_top4_support_label_mean | shape | 0.333333333 | 1.000000000 | -0.666666667 | 0.333333333 | -1.000000000 | 1.333333333 |
| z__shape_top4_support_label_swing | shape | 0.333571402 | 1.000000000 | -0.666428598 | 0.333095265 | -1.000000000 | 1.333095265 |
| z__sup_top1_subject_swing | support | 0.406746032 | 0.916666667 | -0.509920635 | 0.406746032 | -0.916666667 | 1.323412698 |
| z__sup_top1_subject_mean | support | 0.406746032 | 0.916666667 | -0.509920635 | 0.406746032 | -0.916666667 | 1.323412698 |
| z__sup_top1_flank_mean_mean | support | 0.351769863 | 0.938888889 | -0.587119026 | 0.351769863 | -0.938888889 | 1.290658752 |
| z__sup_top1_flank_mean_swing | support | 0.351769863 | 0.938888889 | -0.587119026 | 0.351769863 | -0.938888889 | 1.290658752 |
| z__sup_top4_subject_swing | support | 0.386114718 | 0.886518593 | -0.500403875 | 0.386114718 | -0.886518593 | 1.272633311 |
| z__sup_top4_subject_mean | support | 0.386239353 | 0.885416667 | -0.499177313 | 0.386239353 | -0.885416667 | 1.271656020 |
| z__sup_top16_all_prior_support_rate | support | 0.583333333 | 0.687500000 | -0.104166667 | 0.583333333 | -0.687500000 | 1.270833333 |

## Interpretation

- Support's primary E95-edge gain is an E72-neighbor correction, not a general
  frontier law.
- Shape-only's primary E95-edge advantage is the exact E95/E101 hardtail
  boundary.
- A file-identity gate can make known-pair E95-edge stress look perfect, but
  that is not deployable to live pressure branches because the live branch does
  not come with an E72/E95/E101 filename.
- The useful world model is now anchor-specific: E72-contamination and
  E95/E101 hardtail boundary are different hidden sensors.

## Decision

No submission is created. Support-heavy pair structure can be used only as an
E72-adjacency diagnostic or as auxiliary evidence. It should not rank E176,
E154, or E144 without a new structural target that separates E72-contamination
from tight hardtail frontier boundaries.
