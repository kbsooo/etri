# Windowed prediction stack decoder report

- Baseline: `v36a`
- Base CV: `0.563651`
- Final CV: `0.550513`
- Improvement: `0.013138`
- Bootstrap p025: `0.007305`
- Require sample support: `False`

## Selected Windows

| target | window | used | reason | n_train | n_sample | spec | feature_set | c_value | blend_weight | window_delta | target_delta | folds_improved | worst_fold_delta | worst_subject_delta | option_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | early | True | selected | 234 | 0 | same_target_C10 | same_target | 10.000000 | 0.500000 | 0.020796 | 0.010814 | 3.000000 | 0.013541 | -0.099155 | 0.010814 |
| Q1 | mid | True | selected | 102 | 130 | same_target_C1 | same_target | 1.000000 | 0.700000 | 0.027280 | 0.006184 | 2.000000 | 0.017756 | -0.060038 | 0.006184 |
| Q1 | late_mid | True | selected | 92 | 0 | same_target_C10 | same_target | 10.000000 | 0.100000 | 0.003363 | 0.000688 | 1.000000 | -0.003494 | -0.016392 | 0.000688 |
| Q1 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| Q2 | early | True | selected | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.700000 | 0.032270 | 0.016780 | 3.000000 | 0.004007 | -0.027412 | 0.016780 |
| Q2 | mid | False | no_passing_option | 102 | 130 |  |  |  |  |  |  |  |  |  |  |
| Q2 | late_mid | True | selected | 92 | 0 | all_targets_C3 | all_targets | 3.000000 | 0.100000 | 0.005080 | 0.001039 | 2.000000 | 0.001563 | -0.071512 | 0.001039 |
| Q2 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| Q3 | early | True | selected | 234 | 0 | all_targets_C10 | all_targets | 10.000000 | 0.200000 | 0.015133 | 0.007869 | 2.000000 | -0.033334 | -0.121729 | 0.007869 |
| Q3 | mid | True | selected | 102 | 130 | same_target_C1 | same_target | 1.000000 | 0.500000 | 0.007364 | 0.001669 | 2.000000 | 0.007172 | -0.051935 | 0.001669 |
| Q3 | late_mid | True | selected | 92 | 0 | all_targets_C1 | all_targets | 1.000000 | 0.200000 | 0.012115 | 0.002477 | 2.000000 | 0.004112 | -0.051661 | 0.002477 |
| Q3 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S1 | early | True | selected | 234 | 0 | all_targets_C0.03 | all_targets | 0.030000 | 0.300000 | 0.002017 | 0.001049 | 2.000000 | -0.002258 | -0.024312 | 0.001049 |
| S1 | mid | True | selected | 102 | 130 | same_target_C10 | same_target | 10.000000 | 0.300000 | 0.021007 | 0.004762 | 2.000000 | 0.010434 | -0.038557 | 0.004762 |
| S1 | late_mid | False | no_passing_option | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| S1 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S2 | early | True | selected | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.300000 | 0.002983 | 0.001551 | 2.000000 | -0.002711 | -0.013610 | 0.001551 |
| S2 | mid | True | selected | 102 | 130 | same_target_C10 | same_target | 10.000000 | 0.300000 | 0.009905 | 0.002245 | 2.000000 | 0.007751 | -0.031996 | 0.002245 |
| S2 | late_mid | True | selected | 92 | 0 | all_targets_C10 | all_targets | 10.000000 | 0.300000 | 0.038073 | 0.007784 | 1.000000 | -0.008053 | -0.105500 | 0.007784 |
| S2 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S3 | early | True | selected | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.500000 | 0.016247 | 0.008448 | 3.000000 | 0.000112 | -0.047908 | 0.008448 |
| S3 | mid | True | selected | 102 | 130 | same_target_C3 | same_target | 3.000000 | 0.500000 | 0.013714 | 0.003108 | 2.000000 | 0.013345 | -0.033086 | 0.003108 |
| S3 | late_mid | True | selected | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.700000 | 0.011712 | 0.002394 | 2.000000 | 0.010790 | -0.046117 | 0.002394 |
| S3 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S4 | early | False | no_passing_option | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| S4 | mid | True | selected | 102 | 130 | all_targets_C10 | all_targets | 10.000000 | 0.100000 | 0.003955 | 0.000897 | 1.000000 | -0.007495 | -0.033656 | 0.000897 |
| S4 | late_mid | True | selected | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.700000 | 0.059716 | 0.012209 | 2.000000 | 0.036226 | -0.049654 | 0.012209 |
| S4 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |

## Top Options

| target | window | n_train | n_sample | spec | feature_set | c_value | blend_weight | window_delta | target_delta | folds_improved | worst_fold_delta | worst_subject_delta | option_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | early | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.700000 | 0.032270 | 0.016780 | 3 | 0.004007 | -0.027412 | 0.016780 |
| Q2 | early | 234 | 0 | same_target_C10 | same_target | 10.000000 | 0.500000 | 0.032083 | 0.016683 | 3 | 0.009788 | -0.013452 | 0.016683 |
| Q2 | early | 234 | 0 | same_target_C10 | same_target | 10.000000 | 0.700000 | 0.031901 | 0.016588 | 3 | 0.000835 | -0.034186 | 0.016588 |
| Q2 | early | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.500000 | 0.031320 | 0.016286 | 3 | 0.011113 | -0.009470 | 0.016286 |
| Q2 | early | 234 | 0 | same_target_C1 | same_target | 1.000000 | 0.700000 | 0.031160 | 0.016203 | 3 | 0.008161 | -0.025035 | 0.016203 |
| Q2 | early | 234 | 0 | same_target_C1 | same_target | 1.000000 | 0.500000 | 0.029392 | 0.015284 | 3 | 0.012747 | -0.008621 | 0.015284 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.700000 | 0.027884 | 0.014500 | 3 | 0.013729 | -0.024956 | 0.014500 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.500000 | 0.025467 | 0.013243 | 3 | 0.014712 | -0.010220 | 0.013243 |
| Q2 | early | 234 | 0 | same_target_C10 | same_target | 10.000000 | 0.300000 | 0.024454 | 0.012716 | 3 | 0.010951 | -0.002338 | 0.012716 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.700000 | 0.059716 | 0.012209 | 2 | 0.036226 | -0.049654 | 0.012209 |
| Q2 | early | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.300000 | 0.023451 | 0.012195 | 3 | 0.011277 | -0.000441 | 0.012195 |
| S4 | late_mid | 92 | 0 | same_target_C1 | same_target | 1.000000 | 0.700000 | 0.059067 | 0.012076 | 2 | 0.026446 | -0.093397 | 0.012076 |
| S4 | late_mid | 92 | 0 | same_target_C1 | same_target | 1.000000 | 0.500000 | 0.055639 | 0.011375 | 2 | 0.039842 | -0.048785 | 0.011375 |
| Q2 | early | 234 | 0 | same_target_C1 | same_target | 1.000000 | 0.300000 | 0.021681 | 0.011274 | 3 | 0.011569 | -0.000366 | 0.011274 |
| S4 | late_mid | 92 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.500000 | 0.053788 | 0.010997 | 2 | 0.043837 | -0.028754 | 0.010997 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.700000 | 0.020997 | 0.010918 | 3 | 0.014616 | -0.024757 | 0.010918 |
| Q1 | early | 234 | 0 | same_target_C10 | same_target | 10.000000 | 0.500000 | 0.020796 | 0.010814 | 3 | 0.013541 | -0.099155 | 0.010814 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 1.000000 | 0.020121 | 0.010463 | 3 | 0.003360 | -0.068399 | 0.010463 |
| S4 | late_mid | 92 | 0 | same_target_C3 | same_target | 3.000000 | 0.500000 | 0.050609 | 0.010347 | 2 | 0.037369 | -0.087648 | 0.010347 |
| Q1 | early | 234 | 0 | same_target_C10 | same_target | 10.000000 | 0.700000 | 0.019488 | 0.010134 | 3 | 0.005878 | -0.164518 | 0.010134 |
| S4 | late_mid | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.700000 | 0.049558 | 0.010132 | 2 | 0.045678 | -0.053958 | 0.010132 |
| Q2 | early | 234 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.500000 | 0.019163 | 0.009965 | 3 | 0.013642 | -0.012159 | 0.009965 |
| S4 | late_mid | 92 | 0 | same_target_C3 | same_target | 3.000000 | 0.700000 | 0.048559 | 0.009928 | 2 | 0.021803 | -0.139831 | 0.009928 |
| Q1 | early | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.500000 | 0.018804 | 0.009778 | 3 | 0.011653 | -0.090515 | 0.009778 |
| Q1 | early | 234 | 0 | same_context_C10 | same_context | 10.000000 | 0.300000 | 0.018460 | 0.009599 | 3 | 0.013010 | -0.062696 | 0.009599 |
| Q2 | early | 234 | 0 | same_target_C0.3 | same_target | 0.300000 | 0.300000 | 0.018459 | 0.009599 | 3 | 0.011657 | -0.002127 | 0.009599 |
| Q1 | early | 234 | 0 | same_target_C3 | same_target | 3.000000 | 0.700000 | 0.018240 | 0.009485 | 3 | 0.004049 | -0.149371 | 0.009485 |
| Q2 | early | 234 | 0 | same_target_C10 | same_target | 10.000000 | 0.200000 | 0.018039 | 0.009380 | 3 | 0.008946 | 0.000254 | 0.009380 |
| Q1 | early | 234 | 0 | same_target_C1 | same_target | 1.000000 | 0.700000 | 0.017879 | 0.009297 | 3 | 0.002421 | -0.128214 | 0.009297 |
| S4 | late_mid | 92 | 0 | same_target_C0.1 | same_target | 0.100000 | 0.500000 | 0.044985 | 0.009197 | 2 | 0.044140 | -0.034681 | 0.009197 |
