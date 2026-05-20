# Prediction stack decoder report

- Base candidate: `graph_variant`
- Base CV: 0.602485
- Final CV: 0.592416
- Loaded candidates: latent_temporal, robust_safe, q_ranker, master_temporal, graph_original, graph_variant, q_calibrated

## Target-wise selection

| target | log_loss | base_log_loss | delta_vs_base | stack_name | feature_set | c_value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.643804 | 0.638734 | -0.005070 | stack_same_context_C100 | same_context | 100.000000 | 0.200000 | 2 | False |
| Q2 | 0.659619 | 0.680497 | 0.020878 | stack_all_targets_C100 | all_targets | 100.000000 | 0.300000 | 5 | True |
| Q3 | 0.625697 | 0.654485 | 0.028788 | stack_same_context_C30 | same_context | 30.000000 | 0.500000 | 4 | True |
| S1 | 0.563691 | 0.560805 | -0.002886 | stack_same_context_C100 | same_context | 100.000000 | 0.200000 | 1 | False |
| S2 | 0.554538 | 0.550472 | -0.004065 | stack_same_context_C100 | same_context | 100.000000 | 0.200000 | 0 | False |
| S3 | 0.507900 | 0.526848 | 0.018948 | stack_all_targets_C100 | all_targets | 100.000000 | 0.500000 | 4 | True |
| S4 | 0.603682 | 0.605552 | 0.001870 | stack_same_context_C30 | same_context | 30.000000 | 0.200000 | 3 | True |

## Top candidates

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.3_stack_same_context_C100 | 0.598168 | 0.647842 | 0.666459 | 0.631886 | 0.566382 | 0.557611 | 0.513063 | 0.603935 |
| blend_w0.3_stack_same_context_C30 | 0.598291 | 0.648134 | 0.666198 | 0.632013 | 0.566798 | 0.557707 | 0.513354 | 0.603832 |
| blend_w0.2_stack_same_context_C100 | 0.598479 | 0.643804 | 0.669327 | 0.637611 | 0.563691 | 0.554538 | 0.516663 | 0.603723 |
| blend_w0.2_stack_same_context_C30 | 0.598601 | 0.644046 | 0.669186 | 0.637761 | 0.564017 | 0.554622 | 0.516891 | 0.603682 |
| blend_w0.3_stack_same_context_C10 | 0.598730 | 0.648664 | 0.666047 | 0.633043 | 0.567313 | 0.557840 | 0.514303 | 0.603900 |
| blend_w0.2_stack_same_context_C10 | 0.598960 | 0.644475 | 0.669139 | 0.638576 | 0.564414 | 0.554750 | 0.517617 | 0.603751 |
| blend_w0.2_stack_all_targets_C100 | 0.599854 | 0.646184 | 0.663503 | 0.642630 | 0.565688 | 0.559178 | 0.512718 | 0.609078 |
| blend_w0.2_stack_all_targets_C30 | 0.599929 | 0.646381 | 0.663693 | 0.642608 | 0.565609 | 0.559001 | 0.513221 | 0.608987 |
| blend_w0.2_stack_same_context_C3 | 0.599946 | 0.645542 | 0.669444 | 0.640706 | 0.564688 | 0.555039 | 0.520161 | 0.604042 |
| blend_w0.3_stack_same_context_C3 | 0.600029 | 0.650100 | 0.666331 | 0.635854 | 0.567653 | 0.558187 | 0.517787 | 0.604292 |
| blend_w0.2_stack_all_targets_C10 | 0.600199 | 0.646869 | 0.664008 | 0.642942 | 0.565585 | 0.558970 | 0.514426 | 0.608590 |
| blend_w0.2_stack_all_targets_C3 | 0.600873 | 0.647393 | 0.665198 | 0.644018 | 0.565288 | 0.558948 | 0.517127 | 0.608138 |
| blend_w0.5_stack_same_context_C30 | 0.601063 | 0.659522 | 0.665677 | 0.625697 | 0.574913 | 0.566181 | 0.509089 | 0.606363 |
| blend_w0.5_stack_same_context_C100 | 0.601063 | 0.659294 | 0.666273 | 0.625820 | 0.574484 | 0.566125 | 0.508770 | 0.606678 |
| blend_w0.5_stack_same_context_C10 | 0.601458 | 0.659995 | 0.665149 | 0.626787 | 0.575486 | 0.566196 | 0.510231 | 0.606363 |
