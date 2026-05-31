# E320 E319 Failure Anatomy

Public LB was not used. This analyzes why E319 generated many locally visible tensors but no public-free ready candidate.

## Main Read

- non-oracle governed candidates: `47`
- old-strict candidates inside governor: `30`
- public-free ready candidates: `0`
- target/sign/QS mean dominance: `{'target_perm': 1.0, 'sign_flip': 1.0, 'q_s_swap': 0.9787234042553191}`

The failure is not primarily target permutation, sign, or Q/S swap. Those controls are mostly beaten. The blocker is row/subject/dateblock placement ambiguity.

## Mode Dominance

| mode | mean_dominance | min_dominance | p25_dominance | pass_0p8_count | pass_0p8_rate |
| --- | --- | --- | --- | --- | --- |
| subject | 0.611702128 | 0.000000000 | 0.250000000 | 16 | 0.340425532 |
| dateblock | 0.702127660 | 0.000000000 | 0.500000000 | 22 | 0.468085106 |
| row | 0.755319149 | 0.250000000 | 0.500000000 | 21 | 0.446808511 |
| q_s_swap | 0.978723404 | 0.000000000 | 1.000000000 | 46 | 0.978723404 |
| sign_flip | 1.000000000 | 1.000000000 | 1.000000000 | 47 | 1.000000000 |
| target_perm | 1.000000000 | 1.000000000 | 1.000000000 | 47 | 1.000000000 |

## Killer Modes

| killer_mode | count |
| --- | --- |
| row | 16 |
| subject | 15 |
| dateblock | 15 |
| q_s_swap | 1 |

## Relaxed Promotion Gates

| null_threshold | base_count | pass_p90_dom | pass_mean_dom | pass_worst_dom | all_promotion_except_null_threshold |
| --- | --- | --- | --- | --- | --- |
| 0.000000000 | 2 | 0 | 0 | 0 | 0 |
| 0.050000000 | 2 | 0 | 0 | 0 | 0 |
| 0.100000000 | 2 | 0 | 0 | 0 | 0 |
| 0.200000000 | 3 | 1 | 1 | 1 | 1 |
| 0.350000000 | 9 | 4 | 5 | 3 | 3 |
| 0.500000000 | 19 | 9 | 10 | 8 | 8 |

## Closest Near Misses

| basename | policy | recipe | group_key | base_variant | source_count | selected_mode_mix | old_strict_promote | actual_p90 | actual_mean | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | killer_mode | def_null | def_p90 | def_mean | def_worst | def_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w3_00_bddd61ce.csv | human_regime_only | policy_recipe | human_regime_only__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|row:1|subject:15 | True | -0.001552520 | -0.002898039 | 0.166666667 | 0.944444444 | 0.833333333 | 0.750000000 | subject | 0.074074074 | 0.000000000 | 0.000000000 | 0.000000000 | 0.074074074 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w8_00_2f5f5a54.csv | regime_then_geometry | policy_mode | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | True | -0.001959936 | -0.005001558 | 0.277777778 | 1.000000000 | 0.944444444 | 1.000000000 | dateblock | 0.197530864 | 0.000000000 | 0.000000000 | 0.000000000 | 0.197530864 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c128__w8_00_ce1c1638.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.002091436 | -0.003268116 | 0.333333333 | 0.944444444 | 1.000000000 | 0.750000000 | subject | 0.259259259 | 0.000000000 | 0.000000000 | 0.000000000 | 0.259259259 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_row2__c128__w8_00_6143e1ae.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_row2 | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001672529 | -0.002966364 | 0.388888889 | 0.888888889 | 0.722222222 | 0.750000000 | row | 0.320987654 | 0.000000000 | 0.000000000 | 0.000000000 | 0.320987654 |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__call__w3_00_30eb2465.csv | regime_then_geometry | policy_recipe | regime_then_geometry__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|subject:16 | True | -0.001488928 | -0.002904923 | 0.388888889 | 0.888888889 | 0.777777778 | 0.750000000 | row | 0.320987654 | 0.000000000 | 0.000000000 | 0.000000000 | 0.320987654 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__call__w8_00_9d8aa4da.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.002656406 | -0.004566994 | 0.000000000 | 0.777777778 | 0.555555556 | 0.500000000 | subject | 0.000000000 | 0.027777778 | 0.206349206 | 0.090909091 | 0.325036075 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w5_00_3ba4b8d2.csv | regime_then_geometry | policy_mode | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | True | -0.001980488 | -0.004927804 | 0.444444444 | 0.944444444 | 0.888888889 | 0.750000000 | row | 0.382716049 | 0.000000000 | 0.000000000 | 0.000000000 | 0.382716049 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__call__w8_00_3ee568b1.csv | human_action_p90_rank | policy_top | human_action_p90_rank__top24 | selected_row2 | 24 | actual:5|dateblock:1|row:8|subject:10 | True | -0.001997973 | -0.004426633 | 0.500000000 | 0.944444444 | 1.000000000 | 0.750000000 | row | 0.444444444 | 0.000000000 | 0.000000000 | 0.000000000 | 0.444444444 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__c128__w8_00_c4221343.csv | human_action_p90_rank | policy_top | human_action_p90_rank__top24 | selected_row2 | 24 | actual:5|dateblock:1|row:8|subject:10 | True | -0.001540569 | -0.003601097 | 0.500000000 | 0.888888889 | 0.722222222 | 0.750000000 | row | 0.444444444 | 0.000000000 | 0.000000000 | 0.000000000 | 0.444444444 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_tbal__c64__w8_00_7cf38a1d.csv | human_action_p90_rank | policy_top | human_action_p90_rank__top24 | selected_tbal | 24 | actual:5|dateblock:1|row:8|subject:10 | True | -0.001851735 | -0.002261094 | 0.555555556 | 1.000000000 | 0.888888889 | 1.000000000 | dateblock | 0.506172840 | 0.000000000 | 0.000000000 | 0.000000000 | 0.506172840 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c128__w5_00_ec3ac8dd.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001718306 | -0.002745679 | 0.555555556 | 0.944444444 | 1.000000000 | 0.750000000 | dateblock | 0.506172840 | 0.000000000 | 0.000000000 | 0.000000000 | 0.506172840 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c128__w3_00_7a6bc150.csv | human_action_p90_rank | policy_top | human_action_p90_rank__top24 | selected_maxmean | 24 | actual:5|dateblock:1|row:8|subject:10 | True | -0.001596724 | -0.003738829 | 0.555555556 | 0.944444444 | 0.888888889 | 0.750000000 | row | 0.506172840 | 0.000000000 | 0.000000000 | 0.000000000 | 0.506172840 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_tbal__c64__w5_00_fd5d9107.csv | human_action_p90_rank | policy_top | human_action_p90_rank__top24 | selected_tbal | 24 | actual:5|dateblock:1|row:8|subject:10 | True | -0.001565622 | -0.001964846 | 0.611111111 | 1.000000000 | 1.000000000 | 1.000000000 | dateblock | 0.567901235 | 0.000000000 | 0.000000000 | 0.000000000 | 0.567901235 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w3_00_1dcc4429.csv | regime_then_geometry | policy_mode | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | True | -0.001798804 | -0.004311833 | 0.555555556 | 0.833333333 | 0.888888889 | 0.500000000 | row | 0.506172840 | 0.000000000 | 0.000000000 | 0.090909091 | 0.597081930 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_l1sum__c128__w8_00_e4639ff1.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_l1sum | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001690386 | -0.002526786 | 0.666666667 | 0.944444444 | 0.888888889 | 0.750000000 | dateblock | 0.629629630 | 0.000000000 | 0.000000000 | 0.000000000 | 0.629629630 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w5_00_1691fcba.csv | human_regime_only | policy_recipe | human_regime_only__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|row:1|subject:15 | True | -0.001311870 | -0.003717209 | 0.222222222 | 0.833333333 | 0.944444444 | 0.250000000 | row | 0.135802469 | 0.000000000 | 0.000000000 | 0.545454545 | 0.681257015 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_vote2__c128__w8_00_cdf28ac1.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_vote2 | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001662836 | -0.003047958 | 0.666666667 | 0.888888889 | 0.722222222 | 0.500000000 | subject | 0.629629630 | 0.000000000 | 0.000000000 | 0.090909091 | 0.720538721 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_vote2__c128__w8_00_fc7b441d.csv | human_action_p90_rank | policy_top | human_action_p90_rank__top24 | selected_vote2 | 24 | actual:5|dateblock:1|row:8|subject:10 | True | -0.001548065 | -0.003593804 | 0.722222222 | 0.888888889 | 0.833333333 | 0.500000000 | row | 0.691358025 | 0.000000000 | 0.000000000 | 0.090909091 | 0.782267116 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w5_00_b43c1dd0.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.002312305 | -0.004194943 | 0.277777778 | 0.722222222 | 0.722222222 | 0.250000000 | subject | 0.197530864 | 0.097222222 | 0.000000000 | 0.545454545 | 0.840207632 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__call__w5_00_aa1046bd.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.002303764 | -0.003345549 | 0.000000000 | 0.722222222 | 0.555555556 | 0.250000000 | subject | 0.000000000 | 0.097222222 | 0.206349206 | 0.545454545 | 0.849025974 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w8_00_fa27c6ce.csv | human_regime_only | policy_recipe | human_regime_only__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|row:1|subject:15 | True | -0.001177752 | -0.004613502 | 0.388888889 | 0.722222222 | 0.666666667 | 0.250000000 | row | 0.320987654 | 0.097222222 | 0.047619048 | 0.545454545 | 1.011283470 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w3_00_8a995cdb.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001748576 | -0.003103948 | 0.444444444 | 0.722222222 | 0.666666667 | 0.250000000 | subject | 0.382716049 | 0.097222222 | 0.047619048 | 0.545454545 | 1.073011865 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_vote2__call__w8_00_d351d124.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_vote2 | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001878901 | -0.003978004 | 0.722222222 | 0.666666667 | 0.611111111 | 0.250000000 | dateblock | 0.691358025 | 0.166666667 | 0.126984127 | 0.545454545 | 1.530463364 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w8_00_d150a0e8.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.002547032 | -0.004723574 | 0.333333333 | 0.555555556 | 0.611111111 | 0.000000000 | subject | 0.259259259 | 0.305555556 | 0.126984127 | 1.000000000 | 1.691798942 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_row2__call__w8_00_7e58b2a7.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_row2 | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001787983 | -0.003718085 | 0.444444444 | 0.555555556 | 0.611111111 | 0.000000000 | dateblock | 0.382716049 | 0.305555556 | 0.126984127 | 1.000000000 | 1.815255732 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__call__w5_00_267d18b2.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.002774506 | -0.005951404 | 0.222222222 | 0.388888889 | 0.555555556 | 0.000000000 | dateblock | 0.135802469 | 0.513888889 | 0.206349206 | 1.000000000 | 1.856040564 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__call__w8_00_d677a6c0.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.003591197 | -0.007918767 | 0.500000000 | 0.444444444 | 0.666666667 | 0.000000000 | dateblock | 0.444444444 | 0.444444444 | 0.047619048 | 1.000000000 | 1.936507937 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__call__w3_00_10bfa82d.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001906503 | -0.003982354 | 0.500000000 | 0.500000000 | 0.611111111 | 0.000000000 | dateblock | 0.444444444 | 0.375000000 | 0.126984127 | 1.000000000 | 1.946428571 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__call__w3_00_cb7f8573.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001588372 | -0.002235899 | 0.555555556 | 0.611111111 | 0.555555556 | 0.000000000 | subject | 0.506172840 | 0.236111111 | 0.206349206 | 1.000000000 | 1.948633157 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_l1sum__call__w8_00_3f7aa99b.csv | human_identity_action_p90_rank | policy_all | human_identity_action_p90_rank__all | selected_l1sum | 67 | actual:6|dateblock:14|row:10|subject:37 | True | -0.001840221 | -0.003223974 | 0.555555556 | 0.500000000 | 0.611111111 | 0.000000000 | dateblock | 0.506172840 | 0.375000000 | 0.126984127 | 1.000000000 | 2.008156966 |

## Decision

- E319 average-consensus generation should not be scaled or public-tested.
- The next generator needs explicit adversarial row/subject/dateblock geometry, not broader averaging of selected placements.
- The most useful next target is mode-specific action health: for a chosen regime, learn which delta shapes beat same-regime nulls before old-selector visibility is considered.

## Outputs

- `analysis_outputs/e320_e319_failure_anatomy_summary.csv`
- `analysis_outputs/e320_e319_failure_anatomy_near_misses.csv`
- `analysis_outputs/e320_e319_failure_anatomy_report.md`
