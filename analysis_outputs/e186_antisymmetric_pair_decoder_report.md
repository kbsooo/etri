# E186 Antisymmetric Pair Decoder

## Question

E185 found pair-level public signal but also reciprocal orientation collapse.
Does enforcing `score(A,B)=-score(B,A)` turn that signal into an action-grade
frontier selector?

## Result In One Sentence

The best antisymmetric leave-one-file decoder is `shape_support`
with overall accuracy `0.795`, frontier accuracy
`0.867`, and E95-edge-band accuracy
`0.857`. The best leave-one-pair decoder is
`shape_only` with E95-edge-band accuracy
`1.000`. Reciprocity is fixed by
construction, so any remaining miss is selector signal, not orientation
geometry.

## Decoder Stress Summary

| feature_set | group_col | n_rows | n_groups | accuracy | auc | logloss | frontier_n | frontier_accuracy | frontier_auc | micro_n | micro_accuracy | e95_edge_n | e95_edge_accuracy | reciprocity_mae |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_support | file | 264 | 12 | 0.795454545 | 0.834768136 | 0.723760713 | 60 | 0.866666667 | 0.866666667 | 32 | 0.812500000 | 28 | 0.857142857 | 0.000000000 |
| shape_support_public_axis | file | 264 | 12 | 0.795454545 | 0.834768136 | 0.723760713 | 60 | 0.866666667 | 0.866666667 | 32 | 0.812500000 | 28 | 0.857142857 | 0.000000000 |
| shape_only | file | 264 | 12 | 0.795454545 | 0.880567034 | 0.496629149 | 60 | 0.833333333 | 0.832222222 | 32 | 0.750000000 | 28 | 0.785714286 | 0.000000000 |
| shape_only | pair | 132 | 66 | 0.969696970 | 0.995408632 | 0.117158497 | 30 | 0.933333333 | 0.986666667 | 16 | 0.875000000 | 14 | 1.000000000 | 0.000000000 |
| shape_support | pair | 132 | 66 | 0.954545455 | 0.977731864 | 0.141430550 | 30 | 0.866666667 | 0.866666667 | 16 | 0.750000000 | 14 | 0.857142857 | 0.000000000 |
| shape_support_public_axis | pair | 132 | 66 | 0.954545455 | 0.977731864 | 0.141430550 | 30 | 0.866666667 | 0.866666667 | 16 | 0.750000000 | 14 | 0.857142857 | 0.000000000 |

## E95-Edge-Band File-LOO Predictions

| feature_set | heldout | new_file | base_file | actual_delta | prob_new_better | correct | frontier_pair | micro_pair | e95_edge_pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.686729582 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.313270418 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.555518715 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.444481285 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.761887945 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.238112055 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.763466174 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.236533826 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.754170087 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.245829913 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.579993686 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.420006314 | True | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.723635094 | True | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.276364906 | True | True | True | True |
| shape_only | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.608561102 | True | True | True | True |
| shape_only | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.391438898 | True | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.274057021 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.725942979 | False | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.727602689 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.272397311 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.817076044 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.182923956 | True | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.041866854 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.958133146 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.044992239 | False | True | True | True |
| shape_only | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.955007761 | False | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.834289455 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.165710545 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.938441371 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.061558629 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.850460307 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.149539693 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.008316839 | False | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.991683161 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.005541812 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.994458188 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.939995897 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.060004103 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.878103873 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.121896127 | True | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.895616294 | True | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.104383706 | True | True | True | True |
| shape_support | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.601901736 | True | True | True | True |
| shape_support | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.398098264 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.869573546 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.130426454 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.954678810 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.045321190 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.965763962 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.034236038 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.616938852 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.383061148 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.638510495 | True | True | True | True |
| shape_support | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.361489505 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.960262264 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.039737736 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.938441371 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.061558629 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.850460307 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.149539693 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.008316839 | False | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.991683161 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.005541812 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.994458188 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.939995897 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.060004103 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.878103873 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.121896127 | True | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.895616294 | True | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.104383706 | True | True | True | True |
| shape_support_public_axis | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.601901736 | True | True | True | True |
| shape_support_public_axis | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.398098264 | True | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.869573546 | True | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.130426454 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.954678810 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.045321190 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.965763962 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.034236038 | True | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.616938852 | True | True | True | True |
| shape_support_public_axis | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.383061148 | True | True | True | True |

## E95-Edge-Band Pair-LOO Predictions

| feature_set | heldout | new_file | base_file | actual_delta | prob_new_better | correct | frontier_pair | micro_pair | e95_edge_pair |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.739403254 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.260596746 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.819695770 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.180304230 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.797351887 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.202648113 | True | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.695341158 | True | True | True | True |
| shape_only | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.304658842 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.589766784 | True | True | True | True |
| shape_only | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.410233216 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.834628016 | True | True | True | True |
| shape_only | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.165371984 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.853082007 | True | True | True | True |
| shape_only | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.146917993 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.950511122 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.049488878 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007317889 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992682111 | False | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.969629859 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.030370141 | True | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.877852766 | True | True | True | True |
| shape_support | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.122147234 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.941862218 | True | True | True | True |
| shape_support | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.058137782 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.964319262 | True | True | True | True |
| shape_support | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.035680738 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.970330522 | True | True | True | True |
| shape_support | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.029669478 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | submission_mixmin_0c916bb4.csv | -0.000006275 | 0.950511122 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e101_q2s3tail_177569bc.csv | 0.000006275 | 0.049488878 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007317889 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992682111 | False | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | submission_mixmin_0c916bb4.csv | -0.000015311 | 0.969629859 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | submission_e95_hardtail_541e3973.csv | 0.000015311 | 0.030370141 | True | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | -0.000086986 | 0.877852766 | True | True | True | True |
| shape_support_public_axis | submission_frontier_cvjepa_refine_a2c8d2c8.csv__vs__submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | submission_frontier_cvjepa_refine_a2c8d2c8.csv | 0.000086986 | 0.122147234 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000101137 | 0.941862218 | True | True | True | True |
| shape_support_public_axis | submission_mixmin_0c916bb4.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_mixmin_0c916bb4.csv | 0.000101137 | 0.058137782 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000107411 | 0.964319262 | True | True | True | True |
| shape_support_public_axis | submission_e101_q2s3tail_177569bc.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e101_q2s3tail_177569bc.csv | 0.000107411 | 0.035680738 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | -0.000116447 | 0.970330522 | True | True | True | True |
| shape_support_public_axis | submission_e95_hardtail_541e3973.csv__vs__submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e95_hardtail_541e3973.csv | 0.000116447 | 0.029669478 | True | True | True | True |

## Pressure-Branch Scores

| feature_set | candidate | scenario_count | prefers_favorable_min_rate | prob_mean | prob_min | prob_max |
| --- | --- | --- | --- | --- | --- | --- |
| shape_only | e144 | 3 | 0.000000000 | 0.016426756 | 0.005881782 | 0.026081579 |
| shape_only | e154 | 3 | 0.000000000 | 0.001610088 | 0.001369363 | 0.001816185 |
| shape_only | e176 | 3 | 1.000000000 | 0.925898875 | 0.920864017 | 0.933324089 |
| shape_support | e144 | 3 | 0.000000000 | 0.005920824 | 0.002241587 | 0.008419755 |
| shape_support | e154 | 3 | 0.000000000 | 0.002305849 | 0.000940115 | 0.004709562 |
| shape_support | e176 | 3 | 1.000000000 | 0.816469448 | 0.754047547 | 0.875250196 |
| shape_support_public_axis | e144 | 3 | 0.000000000 | 0.005920824 | 0.002241587 | 0.008419755 |
| shape_support_public_axis | e154 | 3 | 0.000000000 | 0.002305849 | 0.000940115 | 0.004709562 |
| shape_support_public_axis | e176 | 3 | 1.000000000 | 0.816469448 | 0.754047547 | 0.875250196 |

## Pressure-Branch Detail

| feature_set | candidate | scenario | prob_pressure_min_public_better | prefers_favorable_min | n_diff_cells | top_targets |
| --- | --- | --- | --- | --- | --- | --- |
| shape_only | e144 | global_t010 | 0.026081579 | False | 185 | S2,Q1,Q3,Q1 |
| shape_only | e144 | global_t010_subject_t010 | 0.005881782 | False | 185 | Q1,Q1,Q1,Q3 |
| shape_only | e144 | global_t010_subject_t020 | 0.017316907 | False | 185 | S2,Q1,Q1,Q3 |
| shape_only | e154 | global_t010 | 0.001369363 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_only | e154 | global_t010_subject_t010 | 0.001816185 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_only | e154 | global_t010_subject_t020 | 0.001644717 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_only | e176 | global_t010 | 0.920864017 | True | 904 | S1,Q3,Q3,Q3 |
| shape_only | e176 | global_t010_subject_t010 | 0.933324089 | True | 904 | S1,Q3,Q3,Q3 |
| shape_only | e176 | global_t010_subject_t020 | 0.923508519 | True | 904 | S1,Q3,Q3,Q3 |
| shape_support | e144 | global_t010 | 0.008419755 | False | 185 | S2,Q1,Q3,Q1 |
| shape_support | e144 | global_t010_subject_t010 | 0.007101130 | False | 185 | Q1,Q1,Q1,Q3 |
| shape_support | e144 | global_t010_subject_t020 | 0.002241587 | False | 185 | S2,Q1,Q1,Q3 |
| shape_support | e154 | global_t010 | 0.000940115 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_support | e154 | global_t010_subject_t010 | 0.004709562 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_support | e154 | global_t010_subject_t020 | 0.001267870 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_support | e176 | global_t010 | 0.820110603 | True | 904 | S1,Q3,Q3,Q3 |
| shape_support | e176 | global_t010_subject_t010 | 0.875250196 | True | 904 | S1,Q3,Q3,Q3 |
| shape_support | e176 | global_t010_subject_t020 | 0.754047547 | True | 904 | S1,Q3,Q3,Q3 |
| shape_support_public_axis | e144 | global_t010 | 0.008419755 | False | 185 | S2,Q1,Q3,Q1 |
| shape_support_public_axis | e144 | global_t010_subject_t010 | 0.007101130 | False | 185 | Q1,Q1,Q1,Q3 |
| shape_support_public_axis | e144 | global_t010_subject_t020 | 0.002241587 | False | 185 | S2,Q1,Q1,Q3 |
| shape_support_public_axis | e154 | global_t010 | 0.000940115 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_support_public_axis | e154 | global_t010_subject_t010 | 0.004709562 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_support_public_axis | e154 | global_t010_subject_t020 | 0.001267870 | False | 294 | Q3,Q3,Q3,Q3 |
| shape_support_public_axis | e176 | global_t010 | 0.820110603 | True | 904 | S1,Q3,Q3,Q3 |
| shape_support_public_axis | e176 | global_t010_subject_t010 | 0.875250196 | True | 904 | S1,Q3,Q3,Q3 |
| shape_support_public_axis | e176 | global_t010_subject_t020 | 0.754047547 | True | 904 | S1,Q3,Q3,Q3 |

## Interpretation

- If E186 improves edge-band stress versus E185, the main missing ingredient was
  reciprocal geometry, not raw signal.
- If E186 keeps weak edge-band stress or unstable branch scores, pair-level
  known-LB structure remains too coarse for E176/E154/E144 selection.
- A pressure-branch decision is action-grade only if it is stable across
  feature sets and survives leave-one-file frontier stress.

## Decision

No submission is created. This audit decides whether the next step should be a
geometry-constrained decoder or a different latent target entirely.
