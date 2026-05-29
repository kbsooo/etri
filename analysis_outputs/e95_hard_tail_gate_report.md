# E95 Hard-Tail Gate Scan

## Question

Can E94 hard-label tail exposure become an actionable gate that creates a new non-dominated successor to E86/E90/E89, or does it only restate the existing E89/E90 tradeoff?

## Method

- Use mixmin as base and E72 as the known public-negative hard-tail direction.
- Generate only controlled candidates: E86/E90 hard-tail row or cell fallback to E89, E85, or mixmin, plus scalar blends.
- Score with the same combo, hidden/world/block, raw-energy, and strict gates used by E89/E90.
- Promote a file only if a non-control row is strict and non-dominated on both hard-tail exposure and local margin versus E89/E90/E85.
- Report both raw best-tail and strict best-tail because broad fallback to mixmin can look tail-perfect while failing the structural stress gate.

## Controls

| source | all_delta_vs_mixmin | e72_adverse_positive_exposure_all | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | strict_gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e86 | -0.000027706 | 0.001010242 | -0.000307439 | -0.000377585 | 0.750000000 | 1.000000000 | True |
| noq2 | -0.000026946 | 0.000906798 | -0.000171638 | -0.000254206 | 0.611111111 | 0.944444444 | True |
| e90 | -0.000026932 | 0.000934031 | -0.000250999 | -0.000299838 | 0.750000000 | 1.000000000 | True |
| e89 | -0.000025896 | 0.000799109 | -0.000140452 | -0.000216060 | 0.611111111 | 0.944444444 | True |
| e85 | -0.000023876 | 0.000739201 | -0.000130361 | -0.000216060 | 0.583333333 | 0.944444444 | True |

## Summary

| strategy | source | fallback | target_scope | tail_quantile | rows | evaluated | strict | nondominated | best_tail | best_tail_all_delta | best_strict_tail | best_strict_tail_all_delta | best_margin | best_margin_tail | best_world | best_hidden_q2s3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_e86_e89 | e86 | e89 |  |  | 5 | 5 | 5 | 1 | 0.000841155 | -2.64115e-05 | 0.000841155 | -2.64115e-05 | -2.74803e-05 | 0.000967821 | -0.000272026 | -0.000345686 |
| cell_hardtail_fallback | e86 | e85 | all | 0.5 | 1 | 1 | 1 | 1 | 0.000788914 | -2.62074e-05 | 0.000788914 | -2.62074e-05 | -2.62074e-05 | 0.000788914 | -0.000132931 | -0.00025114 |
| row_hardtail_fallback | e86 | e85 | all | 0.5 | 1 | 1 | 1 | 1 | 0.000793975 | -2.59456e-05 | 0.000793975 | -2.59456e-05 | -2.59456e-05 | 0.000793975 | -0.000176543 | -0.000265009 |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.5 | 1 | 1 | 1 | 1 | 0.000865828 | -2.69417e-05 | 0.000865828 | -2.69417e-05 | -2.69417e-05 | 0.000865828 | -0.000185811 | -0.00025114 |
| row_hardtail_fallback | e86 | e89 | q2s3 | 0.5 | 1 | 1 | 1 | 1 | 0.00087068 | -2.71242e-05 | 0.00087068 | -2.71242e-05 | -2.71242e-05 | 0.00087068 | -0.000202532 | -0.000265009 |
| row_hardtail_fallback | e86 | e89 | all | 0.6 | 1 | 1 | 1 | 1 | 0.000875912 | -2.69913e-05 | 0.000875912 | -2.69913e-05 | -2.69913e-05 | 0.000875912 | -0.000221847 | -0.000297509 |
| cell_hardtail_fallback | e86 | e85 | all | 0.7 | 1 | 1 | 1 | 1 | 0.000878103 | -2.6953e-05 | 0.000878103 | -2.6953e-05 | -2.6953e-05 | 0.000878103 | -0.000222766 | -0.000326244 |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.6 | 1 | 1 | 1 | 1 | 0.000898062 | -2.71924e-05 | 0.000898062 | -2.71924e-05 | -2.71924e-05 | 0.000898062 | -0.000215597 | -0.000294667 |
| row_hardtail_fallback | e86 | e89 | q2s3 | 0.6 | 1 | 1 | 1 | 1 | 0.000901704 | -2.73143e-05 | 0.000901704 | -2.73143e-05 | -2.73143e-05 | 0.000901704 | -0.000235245 | -0.000297509 |
| row_hardtail_fallback | e86 | e89 | all | 0.7 | 1 | 1 | 1 | 1 | 0.000910111 | -2.71622e-05 | 0.000910111 | -2.71622e-05 | -2.71622e-05 | 0.000910111 | -0.000241894 | -0.000318242 |
| cell_hardtail_fallback | e86 | e89 | all | 0.7 | 1 | 1 | 1 | 1 | 0.000912654 | -2.7053e-05 | 0.000912654 | -2.7053e-05 | -2.7053e-05 | 0.000912654 | -0.000237398 | -0.000326244 |
| cell_hardtail_fallback | e86 | e85 | s1s2s3 | 0.6 | 1 | 1 | 1 | 1 | 0.000915951 | -2.71195e-05 | 0.000915951 | -2.71195e-05 | -2.71195e-05 | 0.000915951 | -0.000255236 | -0.00036655 |
| row_hardtail_fallback | e86 | e85 | all | 0.8 | 1 | 1 | 1 | 1 | 0.000917382 | -2.71142e-05 | 0.000917382 | -2.71142e-05 | -2.71142e-05 | 0.000917382 | -0.00027505 | -0.000341482 |
| row_hardtail_fallback | e90 | e89 | all | 0.9 | 1 | 1 | 1 | 1 | 0.000918731 | -2.69633e-05 | 0.000918731 | -2.69633e-05 | -2.69633e-05 | 0.000918731 | -0.000250969 | -0.000295936 |
| row_hardtail_fallback | e90 | e89 | s1s2s3 | 0.9 | 1 | 1 | 1 | 1 | 0.000921424 | -2.69686e-05 | 0.000921424 | -2.69686e-05 | -2.69686e-05 | 0.000921424 | -0.000247944 | -0.000295935 |
| row_hardtail_fallback | e86 | e89 | q2s3 | 0.7 | 1 | 1 | 1 | 1 | 0.000925914 | -2.74426e-05 | 0.000925914 | -2.74426e-05 | -2.74426e-05 | 0.000925914 | -0.000244433 | -0.000318242 |
| cell_hardtail_fallback | e86 | e85 | all | 0.8 | 1 | 1 | 1 | 1 | 0.000928006 | -2.72613e-05 | 0.000928006 | -2.72613e-05 | -2.72613e-05 | 0.000928006 | -0.000278468 | -0.000361205 |
| cell_hardtail_fallback | e86 | e85 | s1s2s3 | 0.7 | 1 | 1 | 1 | 1 | 0.000929031 | -2.72686e-05 | 0.000929031 | -2.72686e-05 | -2.72686e-05 | 0.000929031 | -0.00026756 | -0.000368073 |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.7 | 1 | 1 | 1 | 1 | 0.000932694 | -2.73349e-05 | 0.000932694 | -2.73349e-05 | -2.73349e-05 | 0.000932694 | -0.000252859 | -0.000326244 |
| blend_e90_e89 | e90 | e89 |  |  | 3 | 3 | 3 | 0 | 0.000832681 | -2.62617e-05 | 0.000832681 | -2.62617e-05 | -2.67792e-05 | 0.000900134 | -0.000220753 | -0.000279166 |
| control | e85 |  |  |  | 1 | 1 | 1 | 0 | 0.000739201 | -2.38758e-05 | 0.000739201 | -2.38758e-05 | -2.38758e-05 | 0.000739201 | -0.000130361 | -0.00021606 |
| control | e89 |  |  |  | 1 | 1 | 1 | 0 | 0.000799109 | -2.5896e-05 | 0.000799109 | -2.5896e-05 | -2.5896e-05 | 0.000799109 | -0.000140452 | -0.00021606 |
| cell_hardtail_fallback | e90 | e85 | all | 0.6 | 1 | 1 | 1 | 0 | 0.000804976 | -2.62156e-05 | 0.000804976 | -2.62156e-05 | -2.62156e-05 | 0.000804976 | -0.000149842 | -0.000255226 |
| row_hardtail_fallback | e90 | e85 | all | 0.6 | 1 | 1 | 1 | 0 | 0.000806796 | -2.59407e-05 | 0.000806796 | -2.59407e-05 | -2.59407e-05 | 0.000806796 | -0.000189529 | -0.000261263 |
| row_hardtail_fallback | e90 | e85 | all | 0.7 | 1 | 1 | 1 | 0 | 0.000830228 | -2.62062e-05 | 0.000830228 | -2.62062e-05 | -2.62062e-05 | 0.000830228 | -0.000205747 | -0.000275608 |
| cell_hardtail_fallback | e86 | e85 | all | 0.6 | 1 | 1 | 1 | 0 | 0.000831305 | -2.67093e-05 | 0.000831305 | -2.67093e-05 | -2.67093e-05 | 0.000831305 | -0.000172483 | -0.000294667 |
| row_hardtail_fallback | e86 | e85 | all | 0.6 | 1 | 1 | 1 | 0 | 0.000833955 | -2.64924e-05 | 0.000833955 | -2.64924e-05 | -2.64924e-05 | 0.000833955 | -0.000206563 | -0.000297509 |
| cell_hardtail_fallback | e86 | e89 | all | 0.5 | 1 | 1 | 1 | 0 | 0.000836495 | -2.6515e-05 | 0.000836495 | -2.6515e-05 | -2.6515e-05 | 0.000836495 | -0.0001608 | -0.00025114 |
| row_hardtail_fallback | e86 | e89 | all | 0.5 | 1 | 1 | 1 | 0 | 0.000840606 | -2.66e-05 | 0.000840606 | -2.66e-05 | -2.66e-05 | 0.000840606 | -0.000193892 | -0.000265009 |
| cell_hardtail_fallback | e90 | e85 | all | 0.7 | 1 | 1 | 1 | 0 | 0.000842882 | -2.64773e-05 | 0.000842882 | -2.64773e-05 | -2.64773e-05 | 0.000842882 | -0.000190144 | -0.000275192 |
| cell_hardtail_fallback | e90 | e89 | all | 0.6 | 1 | 1 | 1 | 0 | 0.000845181 | -2.63244e-05 | 0.000845181 | -2.63244e-05 | -2.63244e-05 | 0.000845181 | -0.000171666 | -0.000255226 |
| row_hardtail_fallback | e90 | e89 | all | 0.6 | 1 | 1 | 1 | 0 | 0.000849524 | -2.64322e-05 | 0.000849524 | -2.64322e-05 | -2.64322e-05 | 0.000849524 | -0.000198444 | -0.000261263 |
| row_hardtail_fallback | e90 | e85 | s1s2s3 | 0.6 | 1 | 1 | 1 | 0 | 0.00085265 | -2.62008e-05 | 0.00085265 | -2.62008e-05 | -2.62008e-05 | 0.00085265 | -0.000223261 | -0.000291297 |
| cell_hardtail_fallback | e90 | e85 | s1s2s3 | 0.6 | 1 | 1 | 1 | 0 | 0.000853922 | -2.6507e-05 | 0.000853922 | -2.6507e-05 | -2.6507e-05 | 0.000853922 | -0.00020261 | -0.000291297 |
| cell_hardtail_fallback | e90 | e85 | s1s2s3 | 0.7 | 1 | 1 | 1 | 0 | 0.000866148 | -2.66568e-05 | 0.000866148 | -2.66568e-05 | -2.66568e-05 | 0.000866148 | -0.000215056 | -0.000292109 |
| cell_hardtail_fallback | e90 | e89 | q2s3 | 0.6 | 1 | 1 | 1 | 0 | 0.000866513 | -2.66052e-05 | 0.000866513 | -2.66052e-05 | -2.66052e-05 | 0.000866513 | -0.000190327 | -0.000255226 |
| row_hardtail_fallback | e90 | e89 | all | 0.7 | 1 | 1 | 1 | 0 | 0.000867603 | -2.66223e-05 | 0.000867603 | -2.66223e-05 | -2.66223e-05 | 0.000867603 | -0.000214912 | -0.000275608 |
| row_hardtail_fallback | e90 | e85 | all | 0.8 | 1 | 1 | 1 | 0 | 0.000869128 | -2.6617e-05 | 0.000869128 | -2.6617e-05 | -2.6617e-05 | 0.000869128 | -0.000237108 | -0.000283291 |
| row_hardtail_fallback | e90 | e85 | s1s2s3 | 0.7 | 1 | 1 | 1 | 0 | 0.000869171 | -2.6371e-05 | 0.000869171 | -2.6371e-05 | -2.6371e-05 | 0.000869171 | -0.000230979 | -0.000292775 |
| row_hardtail_fallback | e90 | e89 | q2s3 | 0.6 | 1 | 1 | 1 | 0 | 0.000869604 | -2.66451e-05 | 0.000869604 | -2.66451e-05 | -2.66451e-05 | 0.000869604 | -0.000215356 | -0.000261263 |

## Best Strict Non-Control Rows By Tail

| strategy | source | fallback | target_scope | tail_quantile | all_delta_vs_mixmin | e72_adverse_positive_exposure_all | tail_reduction_vs_e86 | tail_reduction_vs_e90 | tail_reduction_vs_e89 | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | mean_abs_logit_move_vs_mixmin | moved_cells_vs_mixmin | active_targets_vs_mixmin | strict_gate | beats_e90_tail_and_margin | beats_e89_tail_and_margin | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cell_hardtail_fallback | e86 | e85 | all | 0.5 | -2.62074e-05 | 0.000788914 | 0.000221328 | 0.000145117 | 1.01954e-05 | -0.000132931 | -0.00025114 | 0.75 | 0.972222 | 0.00554828 | 550 | Q2,S1,S2,S3 | True | False | True | e95_cell_hardtail_fallback_541e3973 |
| row_hardtail_fallback | e86 | e85 | all | 0.5 | -2.59456e-05 | 0.000793975 | 0.000216266 | 0.000140055 | 5.13417e-06 | -0.000176543 | -0.000265009 | 0.75 | 0.972222 | 0.00536976 | 550 | Q2,S1,S2,S3 | True | False | True | e95_row_hardtail_fallback_5ce3e8be |
| cell_hardtail_fallback | e90 | e85 | all | 0.6 | -2.62156e-05 | 0.000804976 | 0.000205265 | 0.000129054 | -5.86688e-06 | -0.000149842 | -0.000255226 | 0.75 | 0.972222 | 0.00549681 | 553 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_3c20b1c1 |
| row_hardtail_fallback | e90 | e85 | all | 0.6 | -2.59407e-05 | 0.000806796 | 0.000203446 | 0.000127235 | -7.6865e-06 | -0.000189529 | -0.000261263 | 0.75 | 0.972222 | 0.00538244 | 552 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_fb87fc08 |
| row_hardtail_fallback | e90 | e85 | all | 0.7 | -2.62062e-05 | 0.000830228 | 0.000180014 | 0.000103803 | -3.11183e-05 | -0.000205747 | -0.000275608 | 0.75 | 0.972222 | 0.00547325 | 554 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_5aea3065 |
| cell_hardtail_fallback | e86 | e85 | all | 0.6 | -2.67093e-05 | 0.000831305 | 0.000178937 | 0.000102726 | -3.21956e-05 | -0.000172483 | -0.000294667 | 0.777778 | 1 | 0.00567614 | 560 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_2d0f354b |
| blend_e90_e89 | e90 | e89 |  |  | -2.62617e-05 | 0.000832681 | 0.00017756 | 0.000101349 | -3.35719e-05 | -0.00017064 | -0.000237276 | 0.722222 | 0.944444 | 0.00548867 | 565 | Q2,S1,S2,S3 | True | False | False | e95_blend_e90_e89_58c18685 |
| row_hardtail_fallback | e86 | e85 | all | 0.6 | -2.64924e-05 | 0.000833955 | 0.000176287 | 0.000100076 | -3.48453e-05 | -0.000206563 | -0.000297509 | 0.777778 | 1 | 0.00552233 | 558 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_61415b77 |
| cell_hardtail_fallback | e86 | e89 | all | 0.5 | -2.6515e-05 | 0.000836495 | 0.000173747 | 9.75358e-05 | -3.73854e-05 | -0.0001608 | -0.00025114 | 0.75 | 0.972222 | 0.0056447 | 550 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_69e17831 |
| row_hardtail_fallback | e86 | e89 | all | 0.5 | -2.66e-05 | 0.000840606 | 0.000169635 | 9.34243e-05 | -4.14968e-05 | -0.000193892 | -0.000265009 | 0.75 | 0.972222 | 0.00560182 | 550 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_74bc369f |
| blend_e86_e89 | e86 | e89 |  |  | -2.64115e-05 | 0.000841155 | 0.000169086 | 9.28754e-05 | -4.20457e-05 | -0.000175802 | -0.000248771 | 0.722222 | 0.944444 | 0.00552689 | 579 | Q2,S1,S2,S3 | True | False | False | e95_blend_e86_e89_4f94b347 |
| cell_hardtail_fallback | e90 | e85 | all | 0.7 | -2.64773e-05 | 0.000842882 | 0.000167359 | 9.11482e-05 | -4.37729e-05 | -0.000190144 | -0.000275192 | 0.777778 | 1 | 0.00559501 | 560 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_32e29af2 |
| cell_hardtail_fallback | e90 | e89 | all | 0.6 | -2.63244e-05 | 0.000845181 | 0.000165061 | 8.885e-05 | -4.60712e-05 | -0.000171666 | -0.000255226 | 0.75 | 0.972222 | 0.0055648 | 553 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_dad44c39 |
| row_hardtail_fallback | e90 | e89 | all | 0.6 | -2.64322e-05 | 0.000849524 | 0.000160718 | 8.45066e-05 | -5.04145e-05 | -0.000198444 | -0.000261263 | 0.75 | 0.972222 | 0.00556669 | 552 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_5eb81208 |
| row_hardtail_fallback | e90 | e85 | s1s2s3 | 0.6 | -2.62008e-05 | 0.00085265 | 0.000157592 | 8.13808e-05 | -5.35404e-05 | -0.000223261 | -0.000291297 | 0.777778 | 1 | 0.00549176 | 565 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_344344b7 |
| cell_hardtail_fallback | e90 | e85 | s1s2s3 | 0.6 | -2.6507e-05 | 0.000853922 | 0.00015632 | 8.01088e-05 | -5.48123e-05 | -0.00020261 | -0.000291297 | 0.777778 | 1 | 0.00561578 | 565 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_884ba9d8 |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.5 | -2.69417e-05 | 0.000865828 | 0.000144414 | 6.82029e-05 | -6.67182e-05 | -0.000185811 | -0.00025114 | 0.75 | 0.972222 | 0.00571003 | 550 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_d4a64af7 |
| cell_hardtail_fallback | e90 | e85 | s1s2s3 | 0.7 | -2.66568e-05 | 0.000866148 | 0.000144094 | 6.78831e-05 | -6.70381e-05 | -0.000215056 | -0.000292109 | 0.777778 | 1 | 0.00564737 | 565 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_74acb402 |
| blend_e90_e89 | e90 | e89 |  |  | -2.6555e-05 | 0.000866354 | 0.000143888 | 6.76765e-05 | -6.72446e-05 | -0.000191046 | -0.000258312 | 0.722222 | 0.944444 | 0.00558463 | 565 | Q2,S1,S2,S3 | True | False | False | e95_blend_e90_e89_995f12c0 |
| cell_hardtail_fallback | e90 | e89 | q2s3 | 0.6 | -2.66052e-05 | 0.000866513 | 0.000143729 | 6.75181e-05 | -6.74031e-05 | -0.000190327 | -0.000255226 | 0.75 | 0.972222 | 0.00561556 | 553 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_99a3c5a4 |
| row_hardtail_fallback | e90 | e89 | all | 0.7 | -2.66223e-05 | 0.000867603 | 0.000142639 | 6.64279e-05 | -6.84933e-05 | -0.000214912 | -0.000275608 | 0.75 | 0.972222 | 0.00561736 | 554 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_e6abaed7 |
| row_hardtail_fallback | e90 | e85 | all | 0.8 | -2.6617e-05 | 0.000869128 | 0.000141114 | 6.4903e-05 | -7.00182e-05 | -0.000237108 | -0.000283291 | 0.75 | 0.972222 | 0.00559399 | 560 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_60ba55ce |
| row_hardtail_fallback | e90 | e85 | s1s2s3 | 0.7 | -2.6371e-05 | 0.000869171 | 0.000141071 | 6.48597e-05 | -7.00614e-05 | -0.000230979 | -0.000292775 | 0.777778 | 1 | 0.00556198 | 565 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_16886c59 |
| row_hardtail_fallback | e90 | e89 | q2s3 | 0.6 | -2.66451e-05 | 0.000869604 | 0.000140638 | 6.44265e-05 | -7.04947e-05 | -0.000215356 | -0.000261263 | 0.75 | 0.972222 | 0.00562521 | 552 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_1754e0b9 |
| row_hardtail_fallback | e86 | e89 | q2s3 | 0.5 | -2.71242e-05 | 0.00087068 | 0.000139562 | 6.33511e-05 | -7.157e-05 | -0.000202532 | -0.000265009 | 0.75 | 0.972222 | 0.00572276 | 550 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_4b166323 |
| cell_hardtail_fallback | e86 | e89 | all | 0.6 | -2.6816e-05 | 0.000871509 | 0.000138732 | 6.25212e-05 | -7.23999e-05 | -0.000193704 | -0.000294667 | 0.777778 | 1 | 0.00574413 | 560 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_73c7da19 |
| row_hardtail_fallback | e86 | e85 | all | 0.7 | -2.67305e-05 | 0.000872501 | 0.000137741 | 6.15297e-05 | -7.33914e-05 | -0.000221971 | -0.000318242 | 0.777778 | 1 | 0.00566069 | 564 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_f27b3a62 |
| blend_e86_e89 | e86 | e89 |  |  | -2.67443e-05 | 0.000872741 | 0.000137501 | 6.12901e-05 | -7.36311e-05 | -0.000201625 | -0.000273171 | 0.75 | 0.972222 | 0.00562737 | 579 | Q2,S1,S2,S3 | True | False | False | e95_blend_e86_e89_db23e1ce |
| row_hardtail_fallback | e86 | e89 | all | 0.6 | -2.69913e-05 | 0.000875912 | 0.00013433 | 5.81191e-05 | -7.68021e-05 | -0.000221847 | -0.000297509 | 0.777778 | 1 | 0.0057185 | 558 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_3dc609e2 |
| row_hardtail_fallback | e90 | e89 | q2s3 | 0.7 | -2.67593e-05 | 0.000876929 | 0.000133313 | 5.71016e-05 | -7.78195e-05 | -0.00022254 | -0.000275608 | 0.75 | 0.972222 | 0.00564909 | 554 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_137f7d5e |
| cell_hardtail_fallback | e86 | e85 | all | 0.7 | -2.6953e-05 | 0.000878103 | 0.000132139 | 5.59279e-05 | -7.89933e-05 | -0.000222766 | -0.000326244 | 0.777778 | 1 | 0.00580222 | 569 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_1d05306a |
| cell_hardtail_fallback | e90 | e89 | all | 0.7 | -2.6578e-05 | 0.000878342 | 0.0001319 | 5.56886e-05 | -7.92326e-05 | -0.000205394 | -0.000275192 | 0.777778 | 1 | 0.0056548 | 560 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_9977682c |
| cell_hardtail_fallback | e90 | e85 | all | 0.8 | -2.66835e-05 | 0.000882942 | 0.0001273 | 5.1089e-05 | -8.38322e-05 | -0.000227025 | -0.000293237 | 0.777778 | 1 | 0.00568402 | 565 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_7fcee79e |
| row_hardtail_fallback | e90 | e85 | s1s2s3 | 0.8 | -2.66318e-05 | 0.000885443 | 0.000124799 | 4.8588e-05 | -8.63331e-05 | -0.0002349 | -0.000293069 | 0.777778 | 1 | 0.00562913 | 565 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_73430b61 |
| cell_hardtail_fallback | e90 | e89 | q2s3 | 0.7 | -2.67521e-05 | 0.000892475 | 0.000117766 | 4.15552e-05 | -9.3366e-05 | -0.000222202 | -0.000275192 | 0.777778 | 1 | 0.0056848 | 560 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_d330fac0 |
| cell_hardtail_fallback | e90 | e89 | s1s2s3 | 0.6 | -2.66261e-05 | 0.000894126 | 0.000116116 | 3.99046e-05 | -9.50166e-05 | -0.000220231 | -0.000291297 | 0.777778 | 1 | 0.00568377 | 565 | Q2,S1,S2,S3 | True | False | False | e95_cell_hardtail_fallback_36e41bd4 |
| row_hardtail_fallback | e90 | e89 | all | 0.8 | -2.6843e-05 | 0.000894671 | 0.00011557 | 3.93592e-05 | -9.55619e-05 | -0.000243079 | -0.000283291 | 0.75 | 0.972222 | 0.00568929 | 560 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_a59b0f3b |
| row_hardtail_fallback | e90 | e89 | s1s2s3 | 0.6 | -2.67341e-05 | 0.000895378 | 0.000114864 | 3.86528e-05 | -9.62684e-05 | -0.000230954 | -0.000291297 | 0.777778 | 1 | 0.00567601 | 565 | Q2,S1,S2,S3 | True | False | False | e95_row_hardtail_fallback_3102d89b |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.6 | -2.71924e-05 | 0.000898062 | 0.00011218 | 3.59687e-05 | -9.89525e-05 | -0.000215597 | -0.000294667 | 0.777778 | 1 | 0.00580175 | 560 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_9754cc88 |
| blend_e90_e89 | e90 | e89 |  |  | -2.67792e-05 | 0.000900134 | 0.000110108 | 3.38971e-05 | -0.000101024 | -0.000220753 | -0.000279166 | 0.722222 | 0.944444 | 0.00568085 | 565 | Q2,S1,S2,S3 | True | False | False | e95_blend_e90_e89_8d392ec7 |

## Non-Dominated Rows

| strategy | source | fallback | target_scope | tail_quantile | all_delta_vs_mixmin | e72_adverse_positive_exposure_all | tail_reduction_vs_e86 | tail_reduction_vs_e90 | tail_reduction_vs_e89 | world_support_minus_base | hidden_q2s3_mean_minus_base | block_q2s3_beats_base_rate | block_q2s3_tail_safe_rate | mean_abs_logit_move_vs_mixmin | moved_cells_vs_mixmin | active_targets_vs_mixmin | strict_gate | beats_e90_tail_and_margin | beats_e89_tail_and_margin | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cell_hardtail_fallback | e86 | e85 | all | 0.5 | -2.62074e-05 | 0.000788914 | 0.000221328 | 0.000145117 | 1.01954e-05 | -0.000132931 | -0.00025114 | 0.75 | 0.972222 | 0.00554828 | 550 | Q2,S1,S2,S3 | True | False | True | e95_cell_hardtail_fallback_541e3973 |
| row_hardtail_fallback | e86 | e85 | all | 0.5 | -2.59456e-05 | 0.000793975 | 0.000216266 | 0.000140055 | 5.13417e-06 | -0.000176543 | -0.000265009 | 0.75 | 0.972222 | 0.00536976 | 550 | Q2,S1,S2,S3 | True | False | True | e95_row_hardtail_fallback_5ce3e8be |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.5 | -2.69417e-05 | 0.000865828 | 0.000144414 | 6.82029e-05 | -6.67182e-05 | -0.000185811 | -0.00025114 | 0.75 | 0.972222 | 0.00571003 | 550 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_d4a64af7 |
| row_hardtail_fallback | e86 | e89 | q2s3 | 0.5 | -2.71242e-05 | 0.00087068 | 0.000139562 | 6.33511e-05 | -7.157e-05 | -0.000202532 | -0.000265009 | 0.75 | 0.972222 | 0.00572276 | 550 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_4b166323 |
| row_hardtail_fallback | e86 | e89 | all | 0.6 | -2.69913e-05 | 0.000875912 | 0.00013433 | 5.81191e-05 | -7.68021e-05 | -0.000221847 | -0.000297509 | 0.777778 | 1 | 0.0057185 | 558 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_3dc609e2 |
| cell_hardtail_fallback | e86 | e85 | all | 0.7 | -2.6953e-05 | 0.000878103 | 0.000132139 | 5.59279e-05 | -7.89933e-05 | -0.000222766 | -0.000326244 | 0.777778 | 1 | 0.00580222 | 569 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_1d05306a |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.6 | -2.71924e-05 | 0.000898062 | 0.00011218 | 3.59687e-05 | -9.89525e-05 | -0.000215597 | -0.000294667 | 0.777778 | 1 | 0.00580175 | 560 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_9754cc88 |
| row_hardtail_fallback | e86 | e89 | q2s3 | 0.6 | -2.73143e-05 | 0.000901704 | 0.000108537 | 3.23265e-05 | -0.000102595 | -0.000235245 | -0.000297509 | 0.777778 | 1 | 0.00580496 | 558 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_f4305cab |
| blend_e86_e89 | e86 | e89 |  |  | -2.70298e-05 | 0.000904382 | 0.000105859 | 2.96482e-05 | -0.000105273 | -0.000221854 | -0.000297457 | 0.777778 | 1 | 0.00572801 | 579 | Q2,S1,S2,S3 | True | True | False | e95_blend_e86_e89_26278436 |
| row_hardtail_fallback | e86 | e89 | all | 0.7 | -2.71622e-05 | 0.000910111 | 0.00010013 | 2.39192e-05 | -0.000111002 | -0.000241894 | -0.000318242 | 0.777778 | 1 | 0.00581427 | 564 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_e76599c3 |
| cell_hardtail_fallback | e86 | e89 | all | 0.7 | -2.7053e-05 | 0.000912654 | 9.75881e-05 | 2.13771e-05 | -0.000113544 | -0.000237398 | -0.000326244 | 0.777778 | 1 | 0.00585963 | 569 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_620ef906 |
| cell_hardtail_fallback | e86 | e85 | s1s2s3 | 0.6 | -2.71195e-05 | 0.000915951 | 9.42905e-05 | 1.80795e-05 | -0.000116842 | -0.000255236 | -0.00036655 | 0.777778 | 1 | 0.0058724 | 579 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_c5f34521 |
| row_hardtail_fallback | e86 | e85 | all | 0.8 | -2.71142e-05 | 0.000917382 | 9.28595e-05 | 1.66485e-05 | -0.000118273 | -0.00027505 | -0.000341482 | 0.777778 | 1 | 0.00579838 | 570 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_758de134 |
| row_hardtail_fallback | e90 | e89 | all | 0.9 | -2.69633e-05 | 0.000918731 | 9.15106e-05 | 1.52996e-05 | -0.000119622 | -0.000250969 | -0.000295936 | 0.777778 | 1 | 0.00574406 | 564 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_144d08a7 |
| row_hardtail_fallback | e90 | e89 | s1s2s3 | 0.9 | -2.69686e-05 | 0.000921424 | 8.88173e-05 | 1.26063e-05 | -0.000122315 | -0.000247944 | -0.000295935 | 0.777778 | 1 | 0.00575017 | 565 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_33e6356d |
| row_hardtail_fallback | e86 | e89 | q2s3 | 0.7 | -2.74426e-05 | 0.000925914 | 8.43273e-05 | 8.11625e-06 | -0.000126805 | -0.000244433 | -0.000318242 | 0.777778 | 1 | 0.00587126 | 564 | Q2,S1,S2,S3 | True | True | False | e95_row_hardtail_fallback_3d6d9def |
| cell_hardtail_fallback | e86 | e85 | all | 0.8 | -2.72613e-05 | 0.000928006 | 8.22357e-05 | 6.02474e-06 | -0.000128896 | -0.000278468 | -0.000361205 | 0.777778 | 1 | 0.00591787 | 576 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_20217984 |
| cell_hardtail_fallback | e86 | e85 | s1s2s3 | 0.7 | -2.72686e-05 | 0.000929031 | 8.12105e-05 | 4.99946e-06 | -0.000129922 | -0.00026756 | -0.000368073 | 0.777778 | 1 | 0.005911 | 579 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_d0c3a62c |
| cell_hardtail_fallback | e86 | e89 | q2s3 | 0.7 | -2.73349e-05 | 0.000932694 | 7.75476e-05 | 1.3366e-06 | -0.000133585 | -0.000252859 | -0.000326244 | 0.777778 | 1 | 0.00589829 | 569 | Q2,S1,S2,S3 | True | True | False | e95_cell_hardtail_fallback_aef05a3e |

## Decision

Materialized hard-tail gated candidate: `submission_e95_hardtail_541e3973.csv`.

This file should be read as a direct test that E94's hard-label tail localization adds information beyond the earlier E89/E90 decontamination gates.
