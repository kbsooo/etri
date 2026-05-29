# E161 E154 Inherited-Body Pruning Audit

## Question

E159 says E154 failures can be inherited-body dominated. E161 asks whether those risky cells are actually removable before public feedback, or whether pruning only creates another sub-resolution branch control.

## Counts

- pruning rows: `1608`.
- all-four rows: `631`.
- control-grade rows: `299`.
- submission-grade rows: `0`.
- materialized submission: ``.

## Controls

| strategy | all_minus_base | local_delta_vs_e154 | expected_delta_focus_mean | focus_expected_delta_vs_e154 | all_four_health | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | changed_cells_vs_e154 | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control_e154 | -0.000012158 | 0.000000000 | -0.000029838 | 0.000000000 | True | -0.000004653 | -0.000002860 | 0 | e161_9f2e2e73 |
| control_e157 | -0.000010404 | 0.000001754 | -0.000030962 | -0.000001124 | False | -0.000003807 | -0.000001671 | 294 | e161_bd67930d |
| control_e155 | -0.000010362 | 0.000001796 | -0.000030342 | -0.000000505 | False | -0.000003746 | -0.000001077 | 294 | e161_d27e7965 |
| control_e156 | -0.000010004 | 0.000002154 | -0.000031056 | -0.000001218 | False | -0.000003712 | -0.000002266 | 294 | e161_757546d2 |
| control_e144 | -0.000009726 | 0.000002432 | -0.000030476 | -0.000000638 | False | -0.000003430 | -0.000000000 | 294 | e161_d7b4b331 |
| control_e95 | 0.000000000 | 0.000012158 | 0.000000000 | 0.000029838 | False | 0.000000000 | 0.000000000 | 294 | e161_541e3973 |

## Summary

| prior_view | component_scope | target_scope | prune_mode | rows | all_four_health | control_grade | e161_submit | best_all_minus_base | best_local_delta_vs_e154 | best_focus_expected_delta | best_focus_delta_vs_e154 | best_safe_all_minus_base | best_safe_top_n | best_safe_tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject | added | S3 | to_e144 | 7 | 6 | 5 | 0 | -0.000012159 | -0.000000001 | -0.000030622 | -0.000000785 | -0.000012085 | 21 | e161_ead6c3ea |
| subject | all | S3 | to_e144 | 7 | 6 | 5 | 0 | -0.000012159 | -0.000000001 | -0.000030622 | -0.000000785 | -0.000012085 | 21 | e161_ead6c3ea |
| subject | adjustment | S3 | to_e144 | 7 | 6 | 5 | 0 | -0.000012159 | -0.000000001 | -0.000030606 | -0.000000768 | -0.000012088 | 21 | e161_3f584d5b |
| subject | inherited | S3 | to_e144 | 7 | 6 | 5 | 0 | -0.000012159 | -0.000000001 | -0.000030606 | -0.000000768 | -0.000012088 | 21 | e161_3f584d5b |
| nearest_hard085 | added | Q1 | to_e144 | 7 | 5 | 5 | 0 | -0.000012157 | 0.000000001 | -0.000032675 | -0.000002837 | -0.000012014 | 21 | e161_9f324911 |
| nearest_hard085 | all | Q1 | to_e144 | 7 | 5 | 5 | 0 | -0.000012157 | 0.000000001 | -0.000032675 | -0.000002837 | -0.000012014 | 21 | e161_9f324911 |
| focus_mean | added | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030887 | -0.000001049 | -0.000012089 | 13 | e161_164e97b0 |
| focus_mean | adjustment | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030887 | -0.000001049 | -0.000012089 | 13 | e161_164e97b0 |
| focus_mean | all | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030887 | -0.000001049 | -0.000012089 | 13 | e161_164e97b0 |
| focus_mean | inherited | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030887 | -0.000001049 | -0.000012089 | 13 | e161_164e97b0 |
| global | added | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030857 | -0.000001020 | -0.000012089 | 13 | e161_14b1f859 |
| global | adjustment | S3 | to_e144 | 6 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030857 | -0.000001020 | -0.000012089 | 13 | e161_14b1f859 |
| global | all | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030857 | -0.000001020 | -0.000012089 | 13 | e161_14b1f859 |
| global | inherited | S3 | to_e144 | 6 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030857 | -0.000001020 | -0.000012089 | 13 | e161_14b1f859 |
| nearest_hard085 | inherited | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030811 | -0.000000973 | -0.000012114 | 21 | e161_8f97b246 |
| nearest_hard085 | added | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030807 | -0.000000970 | -0.000012099 | 21 | e161_657e43b7 |
| nearest_hard085 | all | S3 | to_e144 | 7 | 5 | 5 | 0 | -0.000012143 | 0.000000015 | -0.000030807 | -0.000000970 | -0.000012099 | 21 | e161_657e43b7 |
| nearest_hard085 | extra | S4 | to_e144 | 5 | 5 | 5 | 0 | -0.000012155 | 0.000000003 | -0.000030429 | -0.000000591 | -0.000012144 | 8 | e161_0800089c |
| nearest_hard085 | extra | S4 | to_e95 | 5 | 5 | 5 | 0 | -0.000012155 | 0.000000003 | -0.000030429 | -0.000000591 | -0.000012144 | 8 | e161_0800089c |
| nearest_hard085 | adjustment | Q1 | to_e144 | 6 | 6 | 4 | 0 | -0.000012179 | -0.000000021 | -0.000030261 | -0.000000423 | -0.000012155 | 2 | e161_1c018b07 |
| nearest_hard085 | inherited | Q1 | to_e144 | 6 | 6 | 4 | 0 | -0.000012179 | -0.000000021 | -0.000030261 | -0.000000423 | -0.000012155 | 2 | e161_1c018b07 |
| focus_mean | adjustment | Q1 | to_e144 | 6 | 6 | 4 | 0 | -0.000012177 | -0.000000018 | -0.000030222 | -0.000000384 | -0.000012156 | 3 | e161_656b7c6b |
| focus_mean | inherited | Q1 | to_e144 | 6 | 6 | 4 | 0 | -0.000012177 | -0.000000018 | -0.000030222 | -0.000000384 | -0.000012156 | 3 | e161_656b7c6b |
| focus_mean | added | Q1 | to_e144 | 8 | 5 | 4 | 0 | -0.000012157 | 0.000000001 | -0.000033146 | -0.000003308 | -0.000011946 | 34 | e161_2cb39e72 |
| focus_mean | all | Q1 | to_e144 | 8 | 5 | 4 | 0 | -0.000012157 | 0.000000001 | -0.000033146 | -0.000003308 | -0.000011946 | 34 | e161_2cb39e72 |
| nearest_hard085 | adjustment | S3 | to_e144 | 7 | 4 | 4 | 0 | -0.000012143 | 0.000000015 | -0.000030811 | -0.000000973 | -0.000012114 | 21 | e161_8f97b246 |
| focus_mean | extra | S4 | to_e144 | 4 | 4 | 4 | 0 | -0.000012155 | 0.000000003 | -0.000030373 | -0.000000536 | -0.000012148 | 5 | e161_df7be437 |
| focus_mean | extra | S4 | to_e95 | 4 | 4 | 4 | 0 | -0.000012155 | 0.000000003 | -0.000030373 | -0.000000536 | -0.000012148 | 5 | e161_df7be437 |
| global | extra | S4 | to_e144 | 4 | 4 | 4 | 0 | -0.000012155 | 0.000000003 | -0.000030373 | -0.000000536 | -0.000012148 | 5 | e161_df7be437 |
| global | extra | S4 | to_e95 | 4 | 4 | 4 | 0 | -0.000012155 | 0.000000003 | -0.000030373 | -0.000000536 | -0.000012148 | 5 | e161_df7be437 |
| subject | extra | S4 | to_e144 | 4 | 4 | 4 | 0 | -0.000012155 | 0.000000003 | -0.000030304 | -0.000000467 | -0.000012148 | 5 | e161_6176d38d |
| subject | extra | S4 | to_e95 | 4 | 4 | 4 | 0 | -0.000012155 | 0.000000003 | -0.000030304 | -0.000000467 | -0.000012148 | 5 | e161_6176d38d |
| nearest_hard085 | extra | S2 | to_e144 | 4 | 4 | 4 | 0 | -0.000012147 | 0.000000011 | -0.000030022 | -0.000000184 | -0.000012143 | 3 | e161_4580e607 |
| nearest_hard085 | extra | S2 | to_e95 | 4 | 4 | 4 | 0 | -0.000012147 | 0.000000011 | -0.000030022 | -0.000000184 | -0.000012143 | 3 | e161_4580e607 |
| subject | added | all | to_e144 | 10 | 8 | 3 | 0 | -0.000012159 | -0.000000001 | -0.000032566 | -0.000002729 | -0.000011623 | 89 | e161_de34af5e |
| subject | all | all | to_e144 | 10 | 8 | 3 | 0 | -0.000012159 | -0.000000001 | -0.000032566 | -0.000002729 | -0.000011623 | 89 | e161_de34af5e |
| subject | adjustment | all | to_e144 | 10 | 8 | 3 | 0 | -0.000012159 | -0.000000001 | -0.000029881 | -0.000000043 | -0.000012146 | 13 | e161_245d3133 |
| subject | inherited | all | to_e144 | 10 | 8 | 3 | 0 | -0.000012159 | -0.000000001 | -0.000029881 | -0.000000043 | -0.000012146 | 13 | e161_245d3133 |
| subject | adjustment | Q1 | to_e144 | 7 | 7 | 3 | 0 | -0.000012158 | 0.000000000 | -0.000029869 | -0.000000031 | -0.000012156 | 5 | e161_65201c96 |
| subject | inherited | Q1 | to_e144 | 7 | 7 | 3 | 0 | -0.000012158 | 0.000000000 | -0.000029869 | -0.000000031 | -0.000012156 | 5 | e161_65201c96 |
| subject | added | Q1 | to_e144 | 8 | 6 | 3 | 0 | -0.000012158 | 0.000000000 | -0.000032668 | -0.000002830 | -0.000011939 | 34 | e161_c12416b7 |
| subject | all | Q1 | to_e144 | 8 | 6 | 3 | 0 | -0.000012158 | 0.000000000 | -0.000032668 | -0.000002830 | -0.000011939 | 34 | e161_c12416b7 |
| focus_mean | added | S4 | to_e95 | 5 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000041504 | -0.000011666 | -0.000012060 | 8 | e161_7d4eff7f |
| focus_mean | all | S4 | to_e95 | 5 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000041504 | -0.000011666 | -0.000012060 | 8 | e161_7d4eff7f |
| focus_mean | adjustment | S4 | to_e95 | 3 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000039562 | -0.000009724 | -0.000012106 | 3 | e161_48547e5b |
| focus_mean | inherited | S4 | to_e95 | 3 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000039562 | -0.000009724 | -0.000012106 | 3 | e161_48547e5b |
| nearest_hard085 | added | S4 | to_e95 | 6 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000039562 | -0.000009724 | -0.000012106 | 3 | e161_48547e5b |
| nearest_hard085 | adjustment | S4 | to_e95 | 4 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000039562 | -0.000009724 | -0.000012106 | 3 | e161_48547e5b |
| nearest_hard085 | all | S4 | to_e95 | 6 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000039562 | -0.000009724 | -0.000012106 | 3 | e161_48547e5b |
| nearest_hard085 | inherited | S4 | to_e95 | 4 | 3 | 3 | 0 | -0.000012145 | 0.000000013 | -0.000039562 | -0.000009724 | -0.000012106 | 3 | e161_48547e5b |
| focus_mean | extra | S2 | to_e144 | 5 | 3 | 3 | 0 | -0.000012122 | 0.000000036 | -0.000030210 | -0.000000372 | -0.000012033 | 8 | e161_f3869f40 |
| focus_mean | extra | S2 | to_e95 | 5 | 3 | 3 | 0 | -0.000012122 | 0.000000036 | -0.000030210 | -0.000000372 | -0.000012033 | 8 | e161_f3869f40 |
| focus_mean | extra | S3 | to_e144 | 3 | 3 | 3 | 0 | -0.000012126 | 0.000000032 | -0.000029912 | -0.000000075 | -0.000012098 | 3 | e161_4f656752 |
| focus_mean | extra | S3 | to_e95 | 3 | 3 | 3 | 0 | -0.000012126 | 0.000000032 | -0.000029912 | -0.000000075 | -0.000012098 | 3 | e161_4f656752 |
| focus_mean | added | Q3 | to_e95 | 8 | 2 | 2 | 0 | -0.000012204 | -0.000000046 | -0.000063922 | -0.000034085 | -0.000009474 | 34 | e161_4389caab |
| focus_mean | all | Q3 | to_e95 | 8 | 2 | 2 | 0 | -0.000012204 | -0.000000046 | -0.000063922 | -0.000034085 | -0.000009474 | 34 | e161_4389caab |
| focus_mean | adjustment | Q3 | to_e95 | 7 | 2 | 2 | 0 | -0.000012204 | -0.000000046 | -0.000059618 | -0.000029781 | -0.000010425 | 21 | e161_1cd0b65d |
| focus_mean | inherited | Q3 | to_e95 | 7 | 2 | 2 | 0 | -0.000012204 | -0.000000046 | -0.000059618 | -0.000029781 | -0.000010425 | 21 | e161_1cd0b65d |
| focus_mean | added | S2 | to_e95 | 7 | 2 | 2 | 0 | -0.000012141 | 0.000000017 | -0.000043595 | -0.000013757 | -0.000011673 | 21 | e161_5d179049 |
| focus_mean | all | S2 | to_e95 | 7 | 2 | 2 | 0 | -0.000012141 | 0.000000017 | -0.000043595 | -0.000013757 | -0.000011673 | 21 | e161_5d179049 |

## Frontier Rows

| strategy | prune_mode | prior_view | component_scope | target_scope | top_n | reverted_cells | all_minus_base | local_delta_vs_e154 | local_delta_vs_e155 | expected_delta_focus_mean | focus_expected_delta_vs_e154 | all_four_health | e161_control_grade | e161_submit | beats_e144_local | beats_e154_readable | public_free_safer_than_e154 | relaxed_structural_tol1e12 | budget_ok | post101_ok | gate_strict_actionable | post101_p95_vs_e95_e101_sensor | e72_plausible_gap_vs_e95 | changed_cells_vs_e154 | cos_vs_e154_axis | cos_vs_e144_axis | tag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| risk_prune | to_e95 | nearest_hard085 | all | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | nearest_hard085 | inherited | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | nearest_hard085 | added | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | nearest_hard085 | adjustment | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | focus_mean | all | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | focus_mean | inherited | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | focus_mean | added | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | focus_mean | adjustment | S4 | 3 | 3 | -0.000012106 | 0.000000052 | -0.000001744 | -0.000039562 | -0.000009724 | True | True | False | True | False | True | True | True | True | True | -0.000004282 | -0.000002860 | 3 | 0.991859285 | 0.974146282 | e161_48547e5b |
| risk_prune | to_e95 | focus_mean | all | Q3 | 3 | 3 | -0.000012111 | 0.000000047 | -0.000001749 | -0.000038863 | -0.000009025 | True | True | False | True | False | True | True | True | True | True | -0.000004343 | -0.000002860 | 3 | 0.991499141 | 0.974126589 | e161_9a56c90b |
| risk_prune | to_e95 | focus_mean | inherited | Q3 | 3 | 3 | -0.000012111 | 0.000000047 | -0.000001749 | -0.000038863 | -0.000009025 | True | True | False | True | False | True | True | True | True | True | -0.000004343 | -0.000002860 | 3 | 0.991499141 | 0.974126589 | e161_9a56c90b |
| risk_prune | to_e95 | focus_mean | added | Q3 | 3 | 3 | -0.000012111 | 0.000000047 | -0.000001749 | -0.000038863 | -0.000009025 | True | True | False | True | False | True | True | True | True | True | -0.000004343 | -0.000002860 | 3 | 0.991499141 | 0.974126589 | e161_9a56c90b |
| risk_prune | to_e95 | focus_mean | adjustment | Q3 | 3 | 3 | -0.000012111 | 0.000000047 | -0.000001749 | -0.000038863 | -0.000009025 | True | True | False | True | False | True | True | True | True | True | -0.000004343 | -0.000002860 | 3 | 0.991499141 | 0.974126589 | e161_9a56c90b |
| risk_prune | to_e95 | nearest_hard085 | all | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | nearest_hard085 | inherited | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | nearest_hard085 | added | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | nearest_hard085 | adjustment | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | focus_mean | all | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | focus_mean | inherited | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | focus_mean | added | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | focus_mean | adjustment | S4 | 2 | 2 | -0.000012112 | 0.000000046 | -0.000001750 | -0.000036449 | -0.000006612 | True | True | False | True | False | True | True | True | True | True | -0.000004284 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_95c71507 |
| risk_prune | to_e95 | focus_mean | all | Q3 | 2 | 2 | -0.000012190 | -0.000000032 | -0.000001828 | -0.000036098 | -0.000006261 | True | True | False | True | False | True | True | True | True | True | -0.000004364 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_3ff5dbfe |
| risk_prune | to_e95 | focus_mean | inherited | Q3 | 2 | 2 | -0.000012190 | -0.000000032 | -0.000001828 | -0.000036098 | -0.000006261 | True | True | False | True | False | True | True | True | True | True | -0.000004364 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_3ff5dbfe |
| risk_prune | to_e95 | focus_mean | added | Q3 | 2 | 2 | -0.000012190 | -0.000000032 | -0.000001828 | -0.000036098 | -0.000006261 | True | True | False | True | False | True | True | True | True | True | -0.000004364 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_3ff5dbfe |
| risk_prune | to_e95 | focus_mean | adjustment | Q3 | 2 | 2 | -0.000012190 | -0.000000032 | -0.000001828 | -0.000036098 | -0.000006261 | True | True | False | True | False | True | True | True | True | True | -0.000004364 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_3ff5dbfe |
| risk_prune | to_e95 | global | all | S4 | 2 | 2 | -0.000012106 | 0.000000052 | -0.000001743 | -0.000034630 | -0.000004793 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994378097 | 0.977283349 | e161_ba6a697b |
| risk_prune | to_e95 | global | inherited | S4 | 2 | 2 | -0.000012106 | 0.000000052 | -0.000001743 | -0.000034630 | -0.000004793 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994378097 | 0.977283349 | e161_ba6a697b |
| risk_prune | to_e95 | global | added | S4 | 2 | 2 | -0.000012106 | 0.000000052 | -0.000001743 | -0.000034630 | -0.000004793 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994378097 | 0.977283349 | e161_ba6a697b |
| risk_prune | to_e95 | global | adjustment | S4 | 2 | 2 | -0.000012106 | 0.000000052 | -0.000001743 | -0.000034630 | -0.000004793 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994378097 | 0.977283349 | e161_ba6a697b |
| risk_prune | to_e95 | nearest_hard085 | all | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | nearest_hard085 | inherited | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | nearest_hard085 | added | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | nearest_hard085 | adjustment | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | focus_mean | all | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | focus_mean | inherited | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | focus_mean | added | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | focus_mean | adjustment | S4 | 1 | 1 | -0.000012145 | 0.000000013 | -0.000001783 | -0.000033161 | -0.000003324 | True | True | False | True | False | True | True | True | True | True | -0.000004649 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_39854cf7 |
| risk_prune | to_e95 | focus_mean | all | S2 | 2 | 2 | -0.000012108 | 0.000000050 | -0.000001745 | -0.000032507 | -0.000002670 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994391165 | 0.977284013 | e161_f85cb5cd |
| risk_prune | to_e95 | focus_mean | inherited | S2 | 2 | 2 | -0.000012108 | 0.000000050 | -0.000001745 | -0.000032507 | -0.000002670 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994391165 | 0.977284013 | e161_f85cb5cd |
| risk_prune | to_e95 | focus_mean | added | S2 | 2 | 2 | -0.000012108 | 0.000000050 | -0.000001745 | -0.000032507 | -0.000002670 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994391165 | 0.977284013 | e161_f85cb5cd |
| risk_prune | to_e95 | focus_mean | adjustment | S2 | 2 | 2 | -0.000012108 | 0.000000050 | -0.000001745 | -0.000032507 | -0.000002670 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 2 | 0.994391165 | 0.977284013 | e161_f85cb5cd |
| risk_prune | to_e95 | global | all | Q1 | 1 | 1 | -0.000012153 | 0.000000005 | -0.000001791 | -0.000031310 | -0.000001473 | True | True | False | True | False | True | True | True | True | True | -0.000004651 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_7e926077 |
| risk_prune | to_e95 | global | inherited | Q1 | 1 | 1 | -0.000012153 | 0.000000005 | -0.000001791 | -0.000031310 | -0.000001473 | True | True | False | True | False | True | True | True | True | True | -0.000004651 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_7e926077 |
| risk_prune | to_e95 | global | added | Q1 | 1 | 1 | -0.000012153 | 0.000000005 | -0.000001791 | -0.000031310 | -0.000001473 | True | True | False | True | False | True | True | True | True | True | -0.000004651 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_7e926077 |
| risk_prune | to_e95 | global | adjustment | Q1 | 1 | 1 | -0.000012153 | 0.000000005 | -0.000001791 | -0.000031310 | -0.000001473 | True | True | False | True | False | True | True | True | True | True | -0.000004651 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_7e926077 |
| risk_prune | to_e95 | nearest_hard085 | all | S2 | 2 | 2 | -0.000012133 | 0.000000025 | -0.000001770 | -0.000031203 | -0.000001366 | True | True | False | True | False | True | True | True | True | True | -0.000004644 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_0d1ae8bd |
| risk_prune | to_e95 | nearest_hard085 | inherited | S2 | 2 | 2 | -0.000012133 | 0.000000025 | -0.000001770 | -0.000031203 | -0.000001366 | True | True | False | True | False | True | True | True | True | True | -0.000004644 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_0d1ae8bd |
| risk_prune | to_e95 | nearest_hard085 | added | S2 | 2 | 2 | -0.000012133 | 0.000000025 | -0.000001770 | -0.000031203 | -0.000001366 | True | True | False | True | False | True | True | True | True | True | -0.000004644 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_0d1ae8bd |
| risk_prune | to_e95 | nearest_hard085 | adjustment | S2 | 2 | 2 | -0.000012133 | 0.000000025 | -0.000001770 | -0.000031203 | -0.000001366 | True | True | False | True | False | True | True | True | True | True | -0.000004644 | -0.000002860 | 2 | 0.994580261 | 0.977297152 | e161_0d1ae8bd |
| risk_prune | to_e95 | focus_mean | all | S2 | 1 | 1 | -0.000012141 | 0.000000017 | -0.000001779 | -0.000031187 | -0.000001349 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_c1caf87f |
| risk_prune | to_e95 | focus_mean | inherited | S2 | 1 | 1 | -0.000012141 | 0.000000017 | -0.000001779 | -0.000031187 | -0.000001349 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_c1caf87f |
| risk_prune | to_e95 | focus_mean | added | S2 | 1 | 1 | -0.000012141 | 0.000000017 | -0.000001779 | -0.000031187 | -0.000001349 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_c1caf87f |
| risk_prune | to_e95 | focus_mean | adjustment | S2 | 1 | 1 | -0.000012141 | 0.000000017 | -0.000001779 | -0.000031187 | -0.000001349 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_c1caf87f |
| risk_prune | to_e95 | nearest_hard085 | all | S2 | 1 | 1 | -0.000012142 | 0.000000016 | -0.000001779 | -0.000030830 | -0.000000992 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_f2db03b5 |
| risk_prune | to_e95 | nearest_hard085 | inherited | S2 | 1 | 1 | -0.000012142 | 0.000000016 | -0.000001779 | -0.000030830 | -0.000000992 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_f2db03b5 |
| risk_prune | to_e95 | nearest_hard085 | added | S2 | 1 | 1 | -0.000012142 | 0.000000016 | -0.000001779 | -0.000030830 | -0.000000992 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_f2db03b5 |
| risk_prune | to_e95 | nearest_hard085 | adjustment | S2 | 1 | 1 | -0.000012142 | 0.000000016 | -0.000001779 | -0.000030830 | -0.000000992 | True | True | False | True | False | True | True | True | True | True | -0.000004647 | -0.000002860 | 1 | 0.997293812 | 0.980438127 | e161_f2db03b5 |
| risk_prune | to_e144 | global | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e95 | global | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e144 | subject | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e95 | subject | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e144 | nearest_hard085 | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e95 | nearest_hard085 | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e144 | focus_mean | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e95 | focus_mean | extra | Q1 | 1 | 1 | -0.000012111 | 0.000000047 | -0.000001748 | -0.000030785 | -0.000000948 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 1 | 0.999630717 | 0.983932649 | e161_5f82c003 |
| risk_prune | to_e144 | nearest_hard085 | all | S3 | 8 | 8 | -0.000012095 | 0.000000063 | -0.000001732 | -0.000030769 | -0.000000931 | True | True | False | True | False | True | True | True | True | True | -0.000004631 | -0.000002860 | 8 | 0.999898599 | 0.983625188 | e161_b2e63dc0 |
| risk_prune | to_e144 | nearest_hard085 | inherited | S3 | 8 | 8 | -0.000012095 | 0.000000063 | -0.000001732 | -0.000030769 | -0.000000931 | True | True | False | True | False | True | True | True | True | True | -0.000004631 | -0.000002860 | 8 | 0.999898599 | 0.983625188 | e161_b2e63dc0 |
| risk_prune | to_e144 | nearest_hard085 | added | S3 | 8 | 8 | -0.000012095 | 0.000000063 | -0.000001732 | -0.000030769 | -0.000000931 | True | True | False | True | False | True | True | True | True | True | -0.000004631 | -0.000002860 | 8 | 0.999898599 | 0.983625188 | e161_b2e63dc0 |
| risk_prune | to_e144 | nearest_hard085 | all | Q1 | 8 | 8 | -0.000012128 | 0.000000030 | -0.000001766 | -0.000030701 | -0.000000864 | True | True | False | True | False | True | True | True | True | True | -0.000004643 | -0.000002860 | 8 | 0.999548984 | 0.984028309 | e161_1d15de11 |
| risk_prune | to_e144 | nearest_hard085 | added | Q1 | 8 | 8 | -0.000012128 | 0.000000030 | -0.000001766 | -0.000030701 | -0.000000864 | True | True | False | True | False | True | True | True | True | True | -0.000004643 | -0.000002860 | 8 | 0.999548984 | 0.984028309 | e161_1d15de11 |
| risk_prune | to_e144 | focus_mean | all | S3 | 8 | 8 | -0.000012108 | 0.000000050 | -0.000001746 | -0.000030603 | -0.000000765 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 8 | 0.999922607 | 0.983601955 | e161_f185d258 |
| risk_prune | to_e144 | focus_mean | inherited | S3 | 8 | 8 | -0.000012108 | 0.000000050 | -0.000001746 | -0.000030603 | -0.000000765 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 8 | 0.999922607 | 0.983601955 | e161_f185d258 |
| risk_prune | to_e144 | focus_mean | added | S3 | 8 | 8 | -0.000012108 | 0.000000050 | -0.000001746 | -0.000030603 | -0.000000765 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 8 | 0.999922607 | 0.983601955 | e161_f185d258 |
| risk_prune | to_e144 | focus_mean | adjustment | S3 | 8 | 8 | -0.000012108 | 0.000000050 | -0.000001746 | -0.000030603 | -0.000000765 | True | True | False | True | False | True | True | True | True | True | -0.000004636 | -0.000002860 | 8 | 0.999922607 | 0.983601955 | e161_f185d258 |
| risk_prune | to_e144 | global | all | S3 | 8 | 8 | -0.000012107 | 0.000000051 | -0.000001745 | -0.000030586 | -0.000000748 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 8 | 0.999912831 | 0.983616551 | e161_af0b0e62 |
| risk_prune | to_e144 | global | inherited | S3 | 8 | 8 | -0.000012107 | 0.000000051 | -0.000001745 | -0.000030586 | -0.000000748 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 8 | 0.999912831 | 0.983616551 | e161_af0b0e62 |
| risk_prune | to_e144 | global | added | S3 | 8 | 8 | -0.000012107 | 0.000000051 | -0.000001745 | -0.000030586 | -0.000000748 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 8 | 0.999912831 | 0.983616551 | e161_af0b0e62 |
| risk_prune | to_e144 | global | adjustment | S3 | 8 | 8 | -0.000012107 | 0.000000051 | -0.000001745 | -0.000030586 | -0.000000748 | True | True | False | True | False | True | True | True | True | True | -0.000004635 | -0.000002860 | 8 | 0.999912831 | 0.983616551 | e161_af0b0e62 |
| risk_prune | to_e144 | global | all | S3 | 5 | 5 | -0.000012113 | 0.000000045 | -0.000001751 | -0.000030530 | -0.000000692 | True | True | False | True | False | True | True | True | True | True | -0.000004637 | -0.000002860 | 5 | 0.999929716 | 0.983599400 | e161_4f40cef2 |
| risk_prune | to_e144 | global | inherited | S3 | 5 | 5 | -0.000012113 | 0.000000045 | -0.000001751 | -0.000030530 | -0.000000692 | True | True | False | True | False | True | True | True | True | True | -0.000004637 | -0.000002860 | 5 | 0.999929716 | 0.983599400 | e161_4f40cef2 |
| risk_prune | to_e144 | global | added | S3 | 5 | 5 | -0.000012113 | 0.000000045 | -0.000001751 | -0.000030530 | -0.000000692 | True | True | False | True | False | True | True | True | True | True | -0.000004637 | -0.000002860 | 5 | 0.999929716 | 0.983599400 | e161_4f40cef2 |

## Decision

No submission. Some pruned rows are safer than E154 and not worse than E155, but none beat E154 by a public-readable local margin.
