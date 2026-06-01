# H045 Conditional Route-to-Action Decoder HS-JEPA

## Question

Can human-state route context price Q2 actions better than scalar route thresholding?

## Decoder

| feature_set | alpha | n_features | loo_mae | loo_rmse | loo_spearman | loo_pair_acc |
| --- | --- | --- | --- | --- | --- | --- |
| cond_plus_world | 0.010000000 | 131 | 0.000349501 | 0.000804617 | 0.990965556 | 0.969696970 |
| cond_plus_world | 0.100000000 | 131 | 0.000355230 | 0.000621111 | 0.980801807 | 0.956709957 |
| cond_plus_world | 1.000000000 | 131 | 0.000597946 | 0.000897132 | 0.964991530 | 0.935064935 |
| cond_cos_compact | 1.000000000 | 265 | 0.000812961 | 0.001825694 | 0.960474308 | 0.917748918 |
| cond_plus_world | 10.000000000 | 131 | 0.000857759 | 0.001455784 | 0.936758893 | 0.904761905 |
| cond_plus_world | 100.000000000 | 131 | 0.000909338 | 0.001279261 | 0.832862789 | 0.835497835 |
| cond_plus_coords | 100.000000000 | 129 | 0.000977971 | 0.001377009 | 0.702992660 | 0.766233766 |
| cond_cos_compact | 0.010000000 | 265 | 0.000980412 | 0.003057885 | 0.710897798 | 0.857142857 |
| cond_cos_compact | 1000.000000000 | 265 | 0.001038343 | 0.001532711 | 0.793337098 | 0.813852814 |
| cond_only | 100.000000000 | 93 | 0.001077068 | 0.001785334 | 0.675889328 | 0.740259740 |

## Top Candidates

| candidate_id | candidate_source | changed_cells_vs_h012 | full_known_cond_margin_vs_h012_median | full_known_cond_support_better_than_h012 | pre_h042_cond_margin_vs_h012_median | pre_h012_action_margin_vs_h012_median | route_equation_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | h025_score | h045_promotable | h045_conditional_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h044_h043support_q2regime_top75_a0.66_c75_5988dfb9 | h044 | 75 | -0.000126787 | 0.583333333 | -0.000665132 | -0.000052181 | -0.000171330 | 0.000547357 | -1.693362091 | True | 1.379843750 |
| h044_q2regime_top75_a0.66_c75_5988dfb9 | h044 | 75 | -0.000126787 | 0.583333333 | -0.000665132 | -0.000052181 | -0.000171330 | 0.000547357 | -1.693362091 | True | 1.380781250 |
| h043_q2_top55_a0.92_c55_774a85c6 | h043 | 55 | -0.000140322 | 0.583333333 | -0.000598376 | 0.000041751 | -0.000224194 | 0.000785009 | -1.028666578 | True | 1.439791667 |
| h043_q2_top55_a0.78_c55_41de2e67 | h043 | 55 | -0.000176247 | 0.583333333 | -0.000522059 | 0.000009692 | -0.000202072 | 0.000665693 | -1.041620998 | True | 1.452187500 |
| h044_h042core0.58_phaseenergy_tail18_b0.44_c63_dbbcb814 | h044 | 63 | -0.000155974 | 0.583333333 | -0.000513272 | -0.000047752 | -0.000168158 | 0.000496647 | -1.293476642 | True | 1.459583333 |
| h043_q2_top55_a0.66_c55_5e57cffe | h043 | 55 | -0.000206451 | 0.583333333 | -0.000456391 | -0.000010034 | -0.000179721 | 0.000563168 | -1.037858131 | True | 1.475416667 |
| h043_h042core0.9_tail20_b0.18_c65_47e3088b | h043 | 65 | -0.000178062 | 0.583333333 | -0.000405743 | 0.000021035 | -0.000219889 | 0.000741927 | -1.212426456 | True | 1.476041667 |
| h043_h042core0.78_tail20_b0.18_c65_31fb6ad9 | h043 | 65 | -0.000204827 | 0.583333333 | -0.000351272 | -0.000001278 | -0.000201005 | 0.000643880 | -1.232447625 | True | 1.486458333 |
| h043_h042core0.9_tail20_b0.12_c65_9a5b283d | h043 | 65 | -0.000183055 | 0.583333333 | -0.000378101 | 0.000023522 | -0.000218419 | 0.000739840 | -1.220949701 | True | 1.490208333 |
| h043_h042core0.78_tail20_b0.12_c65_0a86526c | h043 | 65 | -0.000210627 | 0.583333333 | -0.000319372 | 0.000000287 | -0.000199536 | 0.000641695 | -1.240970870 | True | 1.493229167 |
| h043_h042core0.78_tail20_b0.08_c65_ae4f4cdc | h043 | 65 | -0.000213021 | 0.583333333 | -0.000296791 | 0.000003206 | -0.000198516 | 0.000640401 | -1.243059528 | True | 1.515416667 |
| h043_h042core0.78_tail20_b0.04_c65_0ce8c7ee | h043 | 65 | -0.000215484 | 0.583333333 | -0.000273671 | 0.000005977 | -0.000197465 | 0.000639304 | -1.242468454 | True | 1.529166667 |
| h043_h042core0.9_tail20_b0.08_c65_99e970bb | h043 | 65 | -0.000185346 | 0.583333333 | -0.000358707 | 0.000026491 | -0.000217400 | 0.000738589 | -1.223038359 | True | 1.540833333 |
| h043_q2_top55_a0.58_c55_5061e807 | h043 | 55 | -0.000215932 | 0.583333333 | -0.000412456 | -0.000022090 | -0.000163071 | 0.000494678 | -1.033243510 | True | 1.551979167 |
| h043_h042core0.78_tail10_b0.18_c55_6e1a0dab | h043 | 55 | -0.000198190 | 0.583333333 | -0.000349562 | 0.000021053 | -0.000198237 | 0.000643113 | -1.044593154 | True | 1.572187500 |
| h043_h042core0.78_tail10_b0.12_c55_a4d75865 | h043 | 55 | -0.000199894 | 0.583333333 | -0.000330320 | 0.000022474 | -0.000197655 | 0.000641636 | -1.052529187 | True | 1.574166667 |
| h043_h042core0.9_tail20_b0.04_c65_9cdffb7f | h043 | 65 | -0.000187807 | 0.583333333 | -0.000338957 | 0.000029187 | -0.000216349 | 0.000737518 | -1.222447285 | True | 1.574791667 |
| h043_h042core0.66_tail20_b0.12_c65_3b4a2780 | h043 | 65 | -0.000205634 | 0.583333333 | -0.000263888 | -0.000021084 | -0.000177664 | 0.000543351 | -1.239177943 | True | 1.575416667 |
| h043_h042core0.9_tail10_b0.18_c55_7cfb15f2 | h043 | 55 | -0.000170612 | 0.583333333 | -0.000410037 | 0.000044524 | -0.000217121 | 0.000741249 | -1.024571985 | True | 1.575833333 |
| h043_h042core0.78_tail10_b0.08_c55_44d58fc2 | h043 | 55 | -0.000201361 | 0.583333333 | -0.000317438 | 0.000022947 | -0.000197247 | 0.000640732 | -1.054004383 | True | 1.576979167 |

## Decision

| decision | promote | selected_candidate_id | selected_file | candidate_source | selected_resolved_path | root_uploadsafe_path | expected_relation | reason | changed_cells_vs_h012 | full_known_cond_margin_vs_h012_median | full_known_cond_support_better_than_h012 | pre_h042_cond_margin_vs_h012_median | pre_h042_cond_support_better_than_h012 | pre_h012_action_margin_vs_h012_median | route_equation_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | h025_score | h045_conditional_score | h045_promotable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| promote | True | h044_h043support_q2regime_top75_a0.66_c75_5988dfb9 | submission_h044_h043support_q2regime_top75_a0.66_c75_5988dfb9.csv | h044 | /Users/kbsoo/Downloads/cl2/hitl/h044_q2_human_route_split_jepa/submission_h044_h043support_q2regime_top75_a0.66_c75_5988dfb9.csv | /Users/kbsoo/Downloads/cl2/submission_h045_condroute_q2regime75_a0.66_5988dfb9_uploadsafe.csv | beats H043 if route-conditioned action pricing fixes Q2 support/amplitude | conditional route-action decoder gate passed | 75 | -0.000126787 | 0.583333333 | -0.000665132 | 0.583333333 | -0.000052181 | -0.000171330 | 0.000547357 | -1.693362091 | 1.379843750 | True |

## Interpretation

- If promoted, the file is a public sensor for conditional route-to-action pricing, not scalar route gating.
- If not promoted, H044's failure stands: the current route latent is explanatory but not yet an upload-action decoder.
