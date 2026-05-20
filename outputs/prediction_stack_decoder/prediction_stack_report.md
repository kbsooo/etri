# Prediction stack decoder report

- Base candidate: `graph_variant`
- Base CV: 0.602485
- Final CV: 0.598173
- Loaded candidates: latent_temporal, robust_safe, q_ranker, master_temporal, graph_original, graph_subjectless, graph_variant

## Target-wise selection

| target | log_loss | base_log_loss | delta_vs_base | stack_name | feature_set | c_value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.639044 | 0.638734 | -0.000310 | stack_same_target_C0.01 | same_target | 0.010000 | 0.050000 | 1 | False |
| Q2 | 0.672256 | 0.680497 | 0.008242 | stack_same_context_C1 | same_context | 1.000000 | 0.300000 | 4 | True |
| Q3 | 0.642295 | 0.654485 | 0.012190 | stack_same_context_C1 | same_context | 1.000000 | 0.500000 | 4 | True |
| S1 | 0.561232 | 0.560805 | -0.000427 | stack_same_target_C0.03 | same_target | 0.030000 | 0.050000 | 1 | False |
| S2 | 0.550680 | 0.550472 | -0.000207 | stack_same_target_C0.01 | same_target | 0.010000 | 0.050000 | 2 | False |
| S3 | 0.518675 | 0.526848 | 0.008173 | stack_all_targets_C1 | all_targets | 1.000000 | 0.300000 | 4 | True |
| S4 | 0.603971 | 0.605552 | 0.001581 | stack_same_context_C1 | same_context | 1.000000 | 0.200000 | 3 | True |

## Top candidates

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.1_stack_same_context_C1 | 0.602134 | 0.642941 | 0.676613 | 0.650143 | 0.563272 | 0.552594 | 0.524954 | 0.604422 |
| blend_w0.05_stack_all_targets_C1 | 0.602148 | 0.640536 | 0.677987 | 0.652214 | 0.561408 | 0.552450 | 0.524660 | 0.605777 |
| blend_w0.1_stack_all_targets_C1 | 0.602164 | 0.642666 | 0.675927 | 0.650323 | 0.562350 | 0.554738 | 0.522826 | 0.606321 |
| blend_w0.05_stack_same_context_C1 | 0.602216 | 0.640739 | 0.678413 | 0.652194 | 0.561958 | 0.551466 | 0.525836 | 0.604902 |
| blend_w0.2_stack_same_context_C1 | 0.602538 | 0.647947 | 0.673862 | 0.646753 | 0.566389 | 0.555264 | 0.523581 | 0.603971 |
| blend_w0.05_stack_all_targets_C0.3 | 0.602583 | 0.640403 | 0.678755 | 0.653339 | 0.561324 | 0.552304 | 0.526040 | 0.605916 |
| blend_w0.05_stack_same_context_C0.3 | 0.602617 | 0.640645 | 0.679115 | 0.653249 | 0.561942 | 0.551470 | 0.526780 | 0.605118 |
| blend_w0.1_stack_same_context_C0.3 | 0.602898 | 0.642714 | 0.677964 | 0.652176 | 0.563213 | 0.552582 | 0.526818 | 0.604819 |
| blend_w0.05_stack_same_target_C0.01 | 0.602903 | 0.639044 | 0.681864 | 0.654578 | 0.561244 | 0.550680 | 0.527177 | 0.605732 |
| blend_w0.05_stack_same_target_C0.03 | 0.602921 | 0.639054 | 0.681933 | 0.654572 | 0.561232 | 0.550727 | 0.527168 | 0.605757 |
| blend_w0.1_stack_all_targets_C0.3 | 0.602935 | 0.642319 | 0.677347 | 0.652438 | 0.562088 | 0.554374 | 0.525466 | 0.606510 |
| blend_w0.05_stack_same_target_C0.1 | 0.602947 | 0.639092 | 0.681907 | 0.654546 | 0.561258 | 0.550824 | 0.527184 | 0.605818 |
| blend_w0.05_stack_same_target_C0.3 | 0.602975 | 0.639153 | 0.681802 | 0.654498 | 0.561339 | 0.550938 | 0.527223 | 0.605875 |
| blend_w0.05_stack_same_context_C0.1 | 0.602988 | 0.640605 | 0.680091 | 0.654205 | 0.562002 | 0.551384 | 0.527210 | 0.605422 |
| blend_w0.05_stack_all_targets_C0.1 | 0.602989 | 0.640314 | 0.679932 | 0.654412 | 0.561456 | 0.552022 | 0.526799 | 0.605989 |
