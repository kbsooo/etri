# Prediction stack decoder report

- Base candidate: `graph_variant`
- Base CV: 0.602485
- Final CV: 0.596413
- Loaded candidates: latent_temporal, robust_safe, q_ranker, master_temporal, graph_original, graph_subjectless, graph_variant, q_calibrated

## Target-wise selection

| target | log_loss | base_log_loss | delta_vs_base | stack_name | feature_set | c_value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.639063 | 0.638734 | -0.000329 | stack_same_target_C0.01 | same_target | 0.010000 | 0.050000 | 1 | False |
| Q2 | 0.665512 | 0.680497 | 0.014985 | stack_all_targets_C1 | all_targets | 1.000000 | 0.300000 | 5 | True |
| Q3 | 0.634701 | 0.654485 | 0.019783 | stack_same_context_C1 | same_context | 1.000000 | 0.700000 | 3 | True |
| S1 | 0.561215 | 0.560805 | -0.000410 | stack_same_target_C0.03 | same_target | 0.030000 | 0.050000 | 1 | False |
| S2 | 0.550698 | 0.550472 | -0.000226 | stack_same_target_C0.01 | same_target | 0.010000 | 0.050000 | 1 | False |
| S3 | 0.520425 | 0.526848 | 0.006424 | stack_all_targets_C1 | all_targets | 1.000000 | 0.300000 | 4 | True |
| S4 | 0.604244 | 0.605552 | 0.001308 | stack_same_context_C1 | same_context | 1.000000 | 0.200000 | 3 | True |

## Top candidates

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.2_stack_same_context_C1 | 0.601227 | 0.645915 | 0.670358 | 0.643380 | 0.565413 | 0.555204 | 0.524075 | 0.604244 |
| blend_w0.1_stack_same_context_C1 | 0.601470 | 0.642000 | 0.674705 | 0.648391 | 0.562802 | 0.552577 | 0.525233 | 0.604580 |
| blend_w0.3_stack_same_context_C1 | 0.601764 | 0.650513 | 0.667438 | 0.639434 | 0.568654 | 0.558385 | 0.523377 | 0.604549 |
| blend_w0.1_stack_all_targets_C1 | 0.601769 | 0.642356 | 0.673351 | 0.649652 | 0.562303 | 0.554465 | 0.523482 | 0.606778 |
| blend_w0.05_stack_same_context_C1 | 0.601881 | 0.640288 | 0.677418 | 0.651300 | 0.561728 | 0.551461 | 0.525983 | 0.604986 |
| blend_w0.05_stack_all_targets_C1 | 0.601944 | 0.640384 | 0.676654 | 0.651856 | 0.561392 | 0.552315 | 0.525002 | 0.606005 |
| blend_w0.05_stack_same_context_C0.3 | 0.602411 | 0.640489 | 0.678260 | 0.652705 | 0.561715 | 0.551469 | 0.527034 | 0.605203 |
| blend_w0.05_stack_all_targets_C0.3 | 0.602473 | 0.640403 | 0.677955 | 0.653169 | 0.561271 | 0.552201 | 0.526329 | 0.605980 |
| blend_w0.1_stack_same_context_C0.3 | 0.602484 | 0.642374 | 0.676298 | 0.651094 | 0.562754 | 0.552576 | 0.527309 | 0.604982 |
| blend_w0.2_stack_all_targets_C1 | 0.602513 | 0.647279 | 0.668350 | 0.646494 | 0.565095 | 0.559704 | 0.521362 | 0.609306 |
| blend_w0.1_stack_all_targets_C0.3 | 0.602714 | 0.642304 | 0.675785 | 0.652116 | 0.561970 | 0.554165 | 0.526019 | 0.606638 |
| blend_w0.05_stack_same_context_C0.1 | 0.602894 | 0.640561 | 0.679512 | 0.653995 | 0.561803 | 0.551390 | 0.527488 | 0.605506 |
| blend_w0.05_stack_same_target_C0.01 | 0.602897 | 0.639063 | 0.681775 | 0.654587 | 0.561229 | 0.550698 | 0.527182 | 0.605747 |
| blend_w0.05_stack_same_target_C0.03 | 0.602914 | 0.639078 | 0.681817 | 0.654572 | 0.561215 | 0.550754 | 0.527179 | 0.605781 |
| blend_w0.05_stack_same_target_C0.1 | 0.602934 | 0.639116 | 0.681783 | 0.654502 | 0.561240 | 0.550856 | 0.527200 | 0.605838 |
