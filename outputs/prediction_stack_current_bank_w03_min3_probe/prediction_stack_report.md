# Prediction stack decoder report

- Base candidate: `primary_w03`
- Base CV: 0.583798
- Final CV: 0.583686
- Loaded candidates: primary_w03, temporal_label_min3, targetwise_resid, master_resid_raw, graph_after_temporal, calendar_min3, markov_min3, sleep_metric_min3, q_ranker_tuned, graph_sleep, guarded

## Target-wise selection

| target | log_loss | base_log_loss | delta_vs_base | stack_name | feature_set | c_value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.637656 | 0.637368 | -0.000288 | stack_all_targets_C0.001 | all_targets | 0.001000 | 0.050000 | 1 | False |
| Q2 | 0.649526 | 0.650305 | 0.000779 | stack_same_target_C0.1 | same_target | 0.100000 | 0.200000 | 3 | True |
| Q3 | 0.623173 | 0.622920 | -0.000253 | stack_same_target_C0.1 | same_target | 0.100000 | 0.050000 | 2 | False |
| S1 | 0.554566 | 0.554273 | -0.000293 | stack_same_target_C0.1 | same_target | 0.100000 | 0.050000 | 3 | False |
| S2 | 0.529237 | 0.529220 | -0.000017 | stack_same_target_C0.1 | same_target | 0.100000 | 0.050000 | 3 | False |
| S3 | 0.498505 | 0.498416 | -0.000089 | stack_same_target_C0.1 | same_target | 0.100000 | 0.050000 | 3 | False |
| S4 | 0.594282 | 0.594084 | -0.000199 | stack_same_target_C0.03 | same_target | 0.030000 | 0.050000 | 2 | False |

## Top candidates

| name | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.05_stack_same_target_C0.1 | 0.583941 | 0.637824 | 0.649983 | 0.623173 | 0.554566 | 0.529237 | 0.498505 | 0.594296 |
| blend_w0.05_stack_same_target_C0.03 | 0.584014 | 0.637762 | 0.650263 | 0.623261 | 0.554570 | 0.529278 | 0.498681 | 0.594282 |
| blend_w0.05_stack_same_target_C0.01 | 0.584103 | 0.637730 | 0.650611 | 0.623291 | 0.554616 | 0.529377 | 0.498787 | 0.594309 |
| blend_w0.1_stack_same_target_C0.1 | 0.584113 | 0.638295 | 0.649745 | 0.623455 | 0.554883 | 0.529270 | 0.498602 | 0.594538 |
| blend_w0.1_stack_same_target_C0.03 | 0.584250 | 0.638166 | 0.650282 | 0.623622 | 0.554884 | 0.529343 | 0.498950 | 0.594502 |
| blend_w0.05_stack_same_target_C0.003 | 0.584278 | 0.637756 | 0.650971 | 0.623338 | 0.554773 | 0.529627 | 0.498994 | 0.594485 |
| blend_w0.15_stack_same_target_C0.1 | 0.584314 | 0.638781 | 0.649593 | 0.623767 | 0.555225 | 0.529318 | 0.498707 | 0.594809 |
| blend_w0.1_stack_same_target_C0.01 | 0.584420 | 0.638099 | 0.650960 | 0.623672 | 0.554968 | 0.529536 | 0.499163 | 0.594545 |
| blend_w0.15_stack_same_target_C0.03 | 0.584506 | 0.638580 | 0.650363 | 0.624003 | 0.555216 | 0.529413 | 0.499224 | 0.594742 |
| blend_w0.2_stack_same_target_C0.1 | 0.584546 | 0.639282 | 0.649526 | 0.624109 | 0.555591 | 0.529382 | 0.498820 | 0.595111 |
| blend_w0.05_stack_same_target_C0.001 | 0.584577 | 0.637887 | 0.651304 | 0.623477 | 0.555059 | 0.530065 | 0.499409 | 0.594839 |
| blend_w0.05_stack_all_targets_C0.003 | 0.584595 | 0.637898 | 0.652087 | 0.624196 | 0.554604 | 0.529706 | 0.498978 | 0.594697 |
| blend_w0.05_stack_all_targets_C0.001 | 0.584621 | 0.637656 | 0.651923 | 0.624075 | 0.554766 | 0.529954 | 0.499175 | 0.594798 |
| blend_w0.15_stack_same_target_C0.01 | 0.584750 | 0.638474 | 0.651352 | 0.624063 | 0.555330 | 0.529697 | 0.499543 | 0.594791 |
| blend_w0.1_stack_same_target_C0.003 | 0.584772 | 0.638150 | 0.651660 | 0.623759 | 0.555281 | 0.530050 | 0.499609 | 0.594893 |
