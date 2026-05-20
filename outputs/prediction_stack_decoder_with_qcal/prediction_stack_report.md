# Prediction stack decoder report

- Base candidate: `graph_variant`
- Base CV: 0.602485
- Final CV: 0.596392
- Loaded candidates: latent_temporal, robust_safe, q_ranker, master_temporal, graph_original, graph_variant, q_calibrated

## Target-wise selection

| target | log_loss | base_log_loss | delta_vs_base | stack_name | feature_set | c_value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.639084 | 0.638734 | -0.000350 | stack_same_target_C0.01 | same_target | 0.010000 | 0.050000 | 1 | False |
| Q2 | 0.664314 | 0.680497 | 0.016184 | stack_all_targets_C1 | all_targets | 1.000000 | 0.500000 | 4 | True |
| Q3 | 0.636140 | 0.654485 | 0.018344 | stack_same_context_C1 | same_context | 1.000000 | 0.500000 | 4 | True |
| S1 | 0.561108 | 0.560805 | -0.000304 | stack_same_target_C0.1 | same_target | 0.100000 | 0.050000 | 1 | False |
| S2 | 0.550764 | 0.550472 | -0.000291 | stack_same_target_C0.01 | same_target | 0.010000 | 0.050000 | 1 | False |
| S3 | 0.519892 | 0.526848 | 0.006956 | stack_all_targets_C1 | all_targets | 1.000000 | 0.300000 | 4 | True |
| S4 | 0.604386 | 0.605552 | 0.001166 | stack_same_context_C1 | same_context | 1.000000 | 0.200000 | 3 | True |

## Top candidates

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.2_stack_same_context_C1 | 0.601341 | 0.646347 | 0.670451 | 0.644031 | 0.564636 | 0.555318 | 0.524219 | 0.604386 |
| blend_w0.1_stack_same_context_C1 | 0.601536 | 0.642218 | 0.674758 | 0.648735 | 0.562413 | 0.552644 | 0.525316 | 0.604665 |
| blend_w0.1_stack_all_targets_C1 | 0.601585 | 0.642490 | 0.673047 | 0.649764 | 0.562205 | 0.554085 | 0.523376 | 0.606124 |
| blend_w0.05_stack_all_targets_C1 | 0.601863 | 0.640457 | 0.676513 | 0.651924 | 0.561351 | 0.552138 | 0.524964 | 0.605691 |
| blend_w0.3_stack_same_context_C1 | 0.601910 | 0.651156 | 0.667557 | 0.640358 | 0.567493 | 0.558524 | 0.523562 | 0.604719 |
| blend_w0.05_stack_same_context_C1 | 0.601916 | 0.640397 | 0.677446 | 0.651477 | 0.561532 | 0.551497 | 0.526028 | 0.605033 |
| blend_w0.2_stack_all_targets_C1 | 0.602060 | 0.647499 | 0.667656 | 0.646631 | 0.564840 | 0.558842 | 0.521064 | 0.607890 |
| blend_w0.05_stack_same_context_C0.3 | 0.602444 | 0.640525 | 0.678240 | 0.652856 | 0.561581 | 0.551507 | 0.527115 | 0.605287 |
| blend_w0.05_stack_all_targets_C0.3 | 0.602451 | 0.640494 | 0.677942 | 0.653220 | 0.561398 | 0.552074 | 0.526204 | 0.605824 |
| blend_w0.1_stack_same_context_C0.3 | 0.602548 | 0.642443 | 0.676257 | 0.651391 | 0.562488 | 0.552650 | 0.527463 | 0.605144 |
| blend_w0.1_stack_all_targets_C0.3 | 0.602661 | 0.642486 | 0.675747 | 0.652210 | 0.562220 | 0.553903 | 0.525750 | 0.606312 |
| blend_w0.05_stack_same_context_C0.1 | 0.602919 | 0.640578 | 0.679474 | 0.654053 | 0.561695 | 0.551435 | 0.527574 | 0.605622 |
| blend_w0.05_stack_same_target_C0.01 | 0.602924 | 0.639084 | 0.681761 | 0.654564 | 0.561175 | 0.550764 | 0.527237 | 0.605884 |
| blend_w0.05_stack_same_target_C0.03 | 0.602942 | 0.639103 | 0.681808 | 0.654551 | 0.561124 | 0.550828 | 0.527244 | 0.605938 |
| blend_w0.05_stack_all_targets_C0.1 | 0.602955 | 0.640445 | 0.679571 | 0.654383 | 0.561504 | 0.551868 | 0.526943 | 0.605969 |
