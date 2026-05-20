# Prediction stack decoder report

- Base candidate: `graph_variant`
- Base CV: 0.602485
- Final CV: 0.592923
- Loaded candidates: latent_temporal, robust_safe, q_ranker, master_temporal, graph_original, graph_variant, q_calibrated

## Target-wise selection

| target | log_loss | base_log_loss | delta_vs_base | stack_name | feature_set | c_value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.639560 | 0.638734 | -0.000826 | stack_same_target_C0.1 | same_target | 0.100000 | 0.100000 | 1 | False |
| Q2 | 0.660037 | 0.680497 | 0.020461 | stack_all_targets_C10 | all_targets | 10.000000 | 0.300000 | 5 | True |
| Q3 | 0.626787 | 0.654485 | 0.027697 | stack_same_context_C10 | same_context | 10.000000 | 0.500000 | 4 | True |
| S1 | 0.561433 | 0.560805 | -0.000628 | stack_same_target_C0.1 | same_target | 0.100000 | 0.100000 | 1 | False |
| S2 | 0.551396 | 0.550472 | -0.000923 | stack_same_target_C0.1 | same_target | 0.100000 | 0.100000 | 0 | False |
| S3 | 0.509876 | 0.526848 | 0.016973 | stack_same_context_C10 | same_context | 10.000000 | 0.700000 | 4 | True |
| S4 | 0.603751 | 0.605552 | 0.001801 | stack_same_context_C10 | same_context | 10.000000 | 0.200000 | 3 | True |

## Top candidates

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.3_stack_same_context_C10 | 0.598730 | 0.648664 | 0.666047 | 0.633043 | 0.567313 | 0.557840 | 0.514303 | 0.603900 |
| blend_w0.2_stack_same_context_C10 | 0.598960 | 0.644475 | 0.669139 | 0.638576 | 0.564414 | 0.554750 | 0.517617 | 0.603751 |
| blend_w0.2_stack_same_context_C3 | 0.599946 | 0.645542 | 0.669444 | 0.640706 | 0.564688 | 0.555039 | 0.520161 | 0.604042 |
| blend_w0.3_stack_same_context_C3 | 0.600029 | 0.650100 | 0.666331 | 0.635854 | 0.567653 | 0.558187 | 0.517787 | 0.604292 |
| blend_w0.2_stack_all_targets_C10 | 0.600199 | 0.646869 | 0.664008 | 0.642942 | 0.565585 | 0.558970 | 0.514426 | 0.608590 |
| blend_w0.1_stack_same_context_C10 | 0.600210 | 0.641179 | 0.673944 | 0.645705 | 0.562252 | 0.552306 | 0.521785 | 0.604302 |
| blend_w0.1_stack_all_targets_C10 | 0.600352 | 0.641958 | 0.670828 | 0.647450 | 0.562393 | 0.553943 | 0.519640 | 0.606252 |
| blend_w0.1_stack_same_context_C3 | 0.600765 | 0.641766 | 0.674157 | 0.646904 | 0.562412 | 0.552479 | 0.523177 | 0.604463 |
| blend_w0.1_stack_all_targets_C3 | 0.600823 | 0.642313 | 0.671585 | 0.648194 | 0.562317 | 0.554038 | 0.521195 | 0.606122 |
| blend_w0.2_stack_all_targets_C3 | 0.600873 | 0.647393 | 0.665198 | 0.644018 | 0.565288 | 0.558948 | 0.517127 | 0.608138 |
| blend_w0.2_stack_same_context_C1 | 0.601341 | 0.646347 | 0.670451 | 0.644031 | 0.564636 | 0.555318 | 0.524219 | 0.604386 |
| blend_w0.5_stack_same_context_C10 | 0.601458 | 0.659995 | 0.665149 | 0.626787 | 0.575486 | 0.566196 | 0.510231 | 0.606363 |
| blend_w0.1_stack_same_context_C1 | 0.601536 | 0.642218 | 0.674758 | 0.648735 | 0.562413 | 0.552644 | 0.525316 | 0.604665 |
| blend_w0.1_stack_all_targets_C1 | 0.601585 | 0.642490 | 0.673047 | 0.649764 | 0.562205 | 0.554085 | 0.523376 | 0.606124 |
| blend_w0.3_stack_same_context_C1 | 0.601910 | 0.651156 | 0.667557 | 0.640358 | 0.567493 | 0.558524 | 0.523562 | 0.604719 |
