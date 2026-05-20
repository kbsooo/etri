# Windowed prediction stack decoder report

- Baseline: `v36a`
- Base CV: `0.563651`
- Final CV: `0.563275`
- Improvement: `0.000376`
- Bootstrap p025: `0.000105`
- Require sample support: `True`

## Selected Windows

| target | window | used | reason | n_train | n_sample | spec | feature_set | c_value | blend_weight | window_delta | target_delta | folds_improved | worst_fold_delta | worst_subject_delta | option_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | early | False | no_sample_rows | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| Q1 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.005554 | 0.001259 | 2.000000 | 0.005461 | -0.005207 | 0.000218 |
| Q1 | late_mid | False | no_sample_rows | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| Q1 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| Q2 | early | False | no_sample_rows | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| Q2 | mid | False | no_passing_option | 102 | 130 |  |  |  |  |  |  |  |  |  |  |
| Q2 | late_mid | False | no_sample_rows | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| Q2 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| Q3 | early | False | no_sample_rows | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| Q3 | mid | True | selected | 102 | 130 | same_context_C0.3 | same_context | 0.300000 | 0.050000 | 0.001468 | 0.000333 | 2.000000 | 0.001397 | -0.003716 | -0.000411 |
| Q3 | late_mid | False | no_sample_rows | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| Q3 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S1 | early | False | no_sample_rows | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| S1 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.002823 | 0.000640 | 2.000000 | 0.002538 | -0.003394 | -0.000039 |
| S1 | late_mid | False | no_sample_rows | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| S1 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S2 | early | False | no_sample_rows | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| S2 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000792 | 0.000179 | 2.000000 | 0.000012 | -0.003201 | -0.000461 |
| S2 | late_mid | False | no_sample_rows | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| S2 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S3 | early | False | no_sample_rows | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| S3 | mid | True | selected | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000978 | 0.000222 | 2.000000 | 0.000437 | -0.002268 | -0.000232 |
| S3 | late_mid | False | no_sample_rows | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| S3 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |
| S4 | early | False | no_sample_rows | 234 | 0 |  |  |  |  |  |  |  |  |  |  |
| S4 | mid | False | no_passing_option | 102 | 130 |  |  |  |  |  |  |  |  |  |  |
| S4 | late_mid | False | no_sample_rows | 92 | 0 |  |  |  |  |  |  |  |  |  |  |
| S4 | tail20 | False | no_passing_option | 22 | 120 |  |  |  |  |  |  |  |  |  |  |

## Top Options

| target | window | n_train | n_sample | spec | feature_set | c_value | blend_weight | window_delta | target_delta | folds_improved | worst_fold_delta | worst_subject_delta | option_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.005554 | 0.001259 | 2 | 0.005461 | -0.005207 | 0.000218 |
| Q1 | mid | 102 | 130 | same_context_C0.1 | same_context | 0.100000 | 0.050000 | 0.003474 | 0.000787 | 2 | 0.000110 | -0.002989 | 0.000190 |
| Q1 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.002863 | 0.000649 | 2 | 0.002831 | -0.002514 | 0.000146 |
| Q1 | mid | 102 | 130 | same_context_C0.1 | same_context | 0.100000 | 0.100000 | 0.006385 | 0.001447 | 1 | -0.000118 | -0.006561 | 0.000135 |
| Q1 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.200000 | 0.010429 | 0.002364 | 2 | 0.010131 | -0.011164 | 0.000131 |
| Q1 | mid | 102 | 130 | same_target_C0.1 | same_target | 0.100000 | 0.100000 | 0.004177 | 0.000947 | 2 | 0.003726 | -0.004240 | 0.000099 |
| Q1 | mid | 102 | 130 | same_target_C0.1 | same_target | 0.100000 | 0.050000 | 0.002146 | 0.000486 | 2 | 0.001916 | -0.002040 | 0.000078 |
| Q1 | mid | 102 | 130 | same_context_C0.03 | same_context | 0.030000 | 0.050000 | 0.002500 | 0.000567 | 2 | 0.000648 | -0.002491 | 0.000068 |
| Q1 | mid | 102 | 130 | same_context_C0.03 | same_context | 0.030000 | 0.100000 | 0.004744 | 0.001075 | 2 | 0.001172 | -0.005095 | 0.000056 |
| S1 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.002823 | 0.000640 | 2 | 0.002538 | -0.003394 | -0.000039 |
| Q1 | mid | 102 | 130 | same_target_C0.1 | same_target | 0.100000 | 0.200000 | 0.007892 | 0.001789 | 2 | 0.007033 | -0.009145 | -0.000040 |
| S1 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.005301 | 0.001202 | 2 | 0.004572 | -0.006868 | -0.000172 |
| Q1 | mid | 102 | 130 | same_context_C0.03 | same_context | 0.030000 | 0.200000 | 0.008488 | 0.001924 | 2 | 0.001855 | -0.010651 | -0.000206 |
| S3 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000978 | 0.000222 | 2 | 0.000437 | -0.002268 | -0.000232 |
| Q1 | mid | 102 | 130 | same_target_C0.03 | same_target | 0.030000 | 0.050000 | 0.001511 | 0.000342 | 2 | 0.001161 | -0.002927 | -0.000243 |
| Q1 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.300000 | 0.014625 | 0.003315 | 2 | 0.014029 | -0.017943 | -0.000273 |
| Q1 | mid | 102 | 130 | same_context_C0.3 | same_context | 0.300000 | 0.050000 | 0.003570 | 0.000809 | 1 | -0.001277 | -0.005644 | -0.000320 |
| S1 | mid | 102 | 130 | same_target_C0.1 | same_target | 0.100000 | 0.050000 | 0.002158 | 0.000489 | 2 | 0.001929 | -0.004369 | -0.000385 |
| Q3 | mid | 102 | 130 | same_context_C0.3 | same_context | 0.300000 | 0.050000 | 0.001468 | 0.000333 | 2 | 0.001397 | -0.003716 | -0.000411 |
| Q1 | mid | 102 | 130 | same_target_C0.1 | same_target | 0.100000 | 0.300000 | 0.011142 | 0.002525 | 2 | 0.009931 | -0.014779 | -0.000430 |
| Q1 | mid | 102 | 130 | same_context_C0.01 | same_context | 0.010000 | 0.050000 | 0.001438 | 0.000326 | 2 | 0.000303 | -0.003830 | -0.000440 |
| Q3 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000919 | 0.000208 | 2 | 0.000894 | -0.003258 | -0.000443 |
| S2 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.050000 | 0.000792 | 0.000179 | 2 | 0.000012 | -0.003201 | -0.000461 |
| S4 | mid | 102 | 130 | same_context_C0.01 | same_context | 0.010000 | 0.050000 | 0.000281 | 0.000064 | 1 | -0.000555 | -0.002676 | -0.000472 |
| S4 | mid | 102 | 130 | all_targets_C0.01 | all_targets | 0.010000 | 0.050000 | 0.000709 | 0.000161 | 1 | -0.000430 | -0.003241 | -0.000488 |
| S3 | mid | 102 | 130 | same_target_C0.1 | same_target | 0.100000 | 0.050000 | 0.000259 | 0.000059 | 1 | -0.000174 | -0.002802 | -0.000502 |
| S3 | mid | 102 | 130 | same_target_C0.3 | same_target | 0.300000 | 0.100000 | 0.001881 | 0.000426 | 2 | 0.000845 | -0.004665 | -0.000507 |
| Q1 | mid | 102 | 130 | same_target_C0.03 | same_target | 0.030000 | 0.100000 | 0.002933 | 0.000665 | 2 | 0.002249 | -0.005872 | -0.000510 |
| S3 | mid | 102 | 130 | same_context_C0.3 | same_context | 0.300000 | 0.050000 | 0.001262 | 0.000286 | 2 | 0.000172 | -0.004219 | -0.000558 |
| Q3 | mid | 102 | 130 | same_context_C0.1 | same_context | 0.100000 | 0.050000 | 0.000839 | 0.000190 | 2 | 0.000607 | -0.003983 | -0.000606 |
