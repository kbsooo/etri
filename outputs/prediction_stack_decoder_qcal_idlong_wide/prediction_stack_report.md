# Prediction stack decoder report

- Base candidate: `graph_variant`
- Base CV: 0.602485
- Final CV: 0.592725
- Loaded candidates: latent_temporal, robust_safe, q_ranker, master_temporal, graph_original, graph_subjectless, graph_id_long, graph_variant, q_calibrated

## Target-wise selection

| target | log_loss | base_log_loss | delta_vs_base | stack_name | feature_set | c_value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.639471 | 0.638734 | -0.000737 | stack_same_target_C0.1 | same_target | 0.100000 | 0.100000 | 0 | False |
| Q2 | 0.664998 | 0.680497 | 0.015499 | stack_same_context_C3 | same_context | 3.000000 | 0.500000 | 4 | True |
| Q3 | 0.625883 | 0.654485 | 0.028602 | stack_same_context_C10 | same_context | 10.000000 | 0.500000 | 4 | True |
| S1 | 0.561685 | 0.560805 | -0.000881 | stack_same_target_C0.1 | same_target | 0.100000 | 0.100000 | 1 | False |
| S2 | 0.551280 | 0.550472 | -0.000807 | stack_same_target_C0.1 | same_target | 0.100000 | 0.100000 | 1 | False |
| S3 | 0.504730 | 0.526848 | 0.022118 | stack_all_targets_C10 | all_targets | 10.000000 | 0.500000 | 4 | True |
| S4 | 0.603453 | 0.605552 | 0.002099 | stack_same_context_C10 | same_context | 10.000000 | 0.200000 | 4 | True |

## Top candidates

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.3_stack_same_context_C10 | 0.598841 | 0.648520 | 0.666127 | 0.632204 | 0.569177 | 0.558047 | 0.514135 | 0.603679 |
| blend_w0.2_stack_same_context_C10 | 0.598959 | 0.644322 | 0.669131 | 0.637918 | 0.565619 | 0.554822 | 0.517451 | 0.603453 |
| blend_w0.2_stack_same_context_C3 | 0.599777 | 0.645050 | 0.669265 | 0.639930 | 0.565623 | 0.554991 | 0.519850 | 0.603732 |
| blend_w0.3_stack_same_context_C3 | 0.599856 | 0.649405 | 0.666145 | 0.634837 | 0.569078 | 0.558173 | 0.517356 | 0.603997 |
| blend_w0.1_stack_same_context_C10 | 0.600172 | 0.641074 | 0.673908 | 0.645324 | 0.562836 | 0.552310 | 0.521674 | 0.604081 |
| blend_w0.1_stack_same_context_C3 | 0.600654 | 0.641506 | 0.674039 | 0.646465 | 0.562872 | 0.552436 | 0.523009 | 0.604254 |
| blend_w0.1_stack_all_targets_C10 | 0.600849 | 0.641861 | 0.672804 | 0.647093 | 0.563907 | 0.554440 | 0.518313 | 0.607524 |
| blend_w0.2_stack_same_context_C1 | 0.601116 | 0.645932 | 0.670341 | 0.643258 | 0.565340 | 0.555202 | 0.523775 | 0.603967 |
| blend_w0.1_stack_all_targets_C3 | 0.601196 | 0.641979 | 0.672909 | 0.648045 | 0.563090 | 0.554651 | 0.520601 | 0.607100 |
| blend_w0.1_stack_same_context_C1 | 0.601405 | 0.642005 | 0.674680 | 0.648310 | 0.562765 | 0.552576 | 0.525083 | 0.604419 |
| blend_w0.2_stack_all_targets_C10 | 0.601519 | 0.647078 | 0.668493 | 0.642502 | 0.568868 | 0.560283 | 0.511953 | 0.611454 |
| blend_w0.3_stack_same_context_C1 | 0.601626 | 0.650549 | 0.667459 | 0.639308 | 0.568548 | 0.558382 | 0.522928 | 0.604206 |
| blend_w0.1_stack_all_targets_C1 | 0.601676 | 0.641997 | 0.673595 | 0.649501 | 0.562241 | 0.554566 | 0.523174 | 0.606656 |
| blend_w0.2_stack_all_targets_C3 | 0.601833 | 0.646990 | 0.668247 | 0.643920 | 0.566999 | 0.560354 | 0.516005 | 0.610316 |
| blend_w0.5_stack_same_context_C10 | 0.602040 | 0.660055 | 0.665588 | 0.625883 | 0.578810 | 0.566894 | 0.510218 | 0.606833 |
