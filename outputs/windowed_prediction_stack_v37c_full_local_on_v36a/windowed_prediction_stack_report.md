# Windowed prediction stack decoder report

- Baseline: `v36a`
- Base CV: `0.563651`
- Final CV: `0.558883`
- Improvement: `0.004768`
- Bootstrap p025: `0.002812`
- Require sample support: `False`

## Selected Windows

| target | window | used | reason | n_train | n_sample | spec | feature_set | c_value | blend_weight | window_delta | target_delta | folds_improved | worst_fold_delta | worst_subject_delta | option_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | early | True | selected | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.004132 | 0.002149 | 3.000000 | 0.003399 | -0.010083 | 0.000132 |
| Q1 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.005554 | 0.001259 | 2.000000 | 0.005461 | -0.005207 | 0.000218 |
| Q1 | late_mid | False | no_passing_option | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| Q1 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| Q2 | early | True | selected | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.500000 | 0.025467 | 0.013243 | 3.000000 | 0.014712 | -0.010220 | 0.011199 |
| Q2 | mid | False | no_passing_option | 102 | 130 |  |  |  |  |  |  |  |  |  |  |
| Q2 | late_mid | True | selected | 92 | 0 | all_targets_C0.03 | all_targets | 0.030000 | 0.050000 | 0.000898 | 0.000184 | 2.000000 | 0.000612 | -0.020482 | -0.003913 |
| Q2 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| Q3 | early | True | selected | 234 | 0 | all_targets_C0.01 | all_targets | 0.010000 | 0.100000 | 0.002439 | 0.001268 | 2.000000 | -0.004692 | -0.005046 | 0.000259 |
| Q3 | mid | True | selected | 102 | 130 | same_context_C0.3 | same_context | 0.300000 | 0.050000 | 0.001468 | 0.000333 | 2.000000 | 0.001397 | -0.003716 | -0.000411 |
| Q3 | late_mid | True | selected | 92 | 0 | all_targets_C0.3 | all_targets | 0.300000 | 0.050000 | 0.004377 | 0.000895 | 2.000000 | 0.002343 | -0.008477 | -0.000801 |
| Q3 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S1 | early | True | selected | 234 | 0 | all_targets_C0.01 | all_targets | 0.010000 | 0.050000 | 0.000531 | 0.000276 | 2.000000 | -0.000000 | -0.002391 | -0.000202 |
| S1 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.002823 | 0.000640 | 2.000000 | 0.002538 | -0.003394 | -0.000039 |
| S1 | late_mid | False | no_passing_option | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| S1 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S2 | early | True | selected | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000388 | 0.000202 | 2.000000 | -0.000129 | -0.002148 | -0.000228 |
| S2 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000792 | 0.000179 | 2.000000 | 0.000012 | -0.003201 | -0.000461 |
| S2 | late_mid | True | selected | 92 | 0 | all_targets_C0.3 | all_targets | 0.300000 | 0.050000 | 0.003331 | 0.000681 | 2.000000 | 0.001006 | -0.010128 | -0.001345 |
| S2 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S3 | early | True | selected | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.200000 | 0.006606 | 0.003435 | 3.000000 | 0.004796 | -0.008281 | 0.001779 |
| S3 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000978 | 0.000222 | 2.000000 | 0.000437 | -0.002268 | -0.000232 |
| S3 | late_mid | True | selected | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.050000 | 0.001938 | 0.000396 | 2.000000 | 0.001913 | -0.002944 | -0.000192 |
| S3 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S4 | early | False | no_passing_option | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| S4 | mid | False | no_passing_option | 102 | 130 |  |  |  |  |  |  |  |  |  |  |
| S4 | late_mid | True | selected | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.300000 | 0.039205 | 0.008015 | 2.000000 | 0.035982 | -0.014553 | 0.005105 |
| S4 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |

## Top Options

| target | window | n_train | n_sample | spec | feature_set | c_value | blend_weight | window_delta | target_delta | folds_improved | worst_fold_delta | worst_subject_delta | option_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.500000 | 0.025467 | 0.013243 | 3 | 0.014712 | -0.010220 | 0.011199 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.700000 | 0.027884 | 0.014500 | 3 | 0.013729 | -0.024956 | 0.009509 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.300000 | 0.018459 | 0.009599 | 3 | 0.011657 | -0.002127 | 0.009173 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.500000 | 0.019163 | 0.009965 | 3 | 0.013642 | -0.012159 | 0.007533 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.200000 | 0.013363 | 0.006949 | 3 | 0.008703 | -0.000155 | 0.006918 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.300000 | 0.013905 | 0.007231 | 3 | 0.010048 | -0.004305 | 0.006370 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.700000 | 0.020997 | 0.010918 | 3 | 0.014616 | -0.024757 | 0.005967 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.500000 | 0.053788 | 0.010997 | 2 | 0.043837 | -0.028754 | 0.005246 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.300000 | 0.039205 | 0.008015 | 2 | 0.035982 | -0.014553 | 0.005105 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.200000 | 0.010070 | 0.005236 | 3 | 0.007312 | -0.001921 | 0.004852 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.200000 | 0.028682 | 0.005864 | 2 | 0.027232 | -0.008753 | 0.004113 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.007218 | 0.003753 | 3 | 0.004818 | 0.000542 | 0.003753 |
| S4 | late_mid | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.300000 | 0.033319 | 0.006812 | 2 | 0.031799 | -0.018415 | 0.003129 |
| S4 | late_mid | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.200000 | 0.024612 | 0.005032 | 2 | 0.023290 | -0.011449 | 0.002742 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.100000 | 0.005439 | 0.002828 | 3 | 0.003962 | -0.000496 | 0.002729 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.015747 | 0.003219 | 2 | 0.015307 | -0.003880 | 0.002443 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.700000 | 0.059716 | 0.012209 | 2 | 0.036226 | -0.049654 | 0.002278 |
| S4 | late_mid | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.500000 | 0.044985 | 0.009197 | 2 | 0.044140 | -0.034681 | 0.002261 |
| Q2 | early | 234 | 0 | same_target_C0.03 | same_target | 0.030000 | 0.300000 | 0.008096 | 0.004210 | 3 | 0.004579 | -0.011146 | 0.001981 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.003745 | 0.001948 | 3 | 0.002526 | 0.000425 | 0.001948 |
| S3 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.200000 | 0.006606 | 0.003435 | 3 | 0.004796 | -0.008281 | 0.001779 |
| S3 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.300000 | 0.009001 | 0.004681 | 3 | 0.005796 | -0.014657 | 0.001749 |
| Q2 | early | 234 | 0 | same_target_C0.03 | same_target | 0.030000 | 0.200000 | 0.005996 | 0.003118 | 3 | 0.003481 | -0.006896 | 0.001739 |
| S4 | late_mid | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.100000 | 0.013658 | 0.002792 | 2 | 0.012846 | -0.005297 | 0.001733 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.050000 | 0.002822 | 0.001467 | 3 | 0.002058 | -0.000133 | 0.001441 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.008259 | 0.001689 | 2 | 0.008097 | -0.001811 | 0.001326 |
| S3 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.200000 | 0.004426 | 0.002302 | 3 | 0.003865 | -0.005357 | 0.001230 |
| S3 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.003613 | 0.001879 | 3 | 0.002879 | -0.003360 | 0.001207 |
| Q2 | early | 234 | 0 | same_target_C0.03 | same_target | 0.030000 | 0.500000 | 0.010501 | 0.005460 | 3 | 0.005457 | -0.021358 | 0.001189 |
| S3 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.300000 | 0.006029 | 0.003135 | 3 | 0.005425 | -0.009752 | 0.001185 |
