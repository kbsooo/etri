# E319 Mode-Specialized Generator

Public LB was not used. E318 route policies were used only to build fresh consensus/blend/residual tensors; selected E315 null-control files were not promoted directly.

## Question

Can the hidden placement-regime signal become a new probability tensor that is both selector-visible and rare under matched row/subject/dateblock/target/sign controls?

## Route Readout

| policy | placement_mode | count | true_rank_mean |
| --- | --- | --- | --- |
| human_action_p90_rank | subject | 31 | 0.699596774 |
| human_action_p90_rank | row | 14 | 0.562500000 |
| human_action_p90_rank | dateblock | 13 | 0.596153846 |
| human_action_p90_rank | actual | 9 | 0.645833333 |
| human_identity_action_p90_rank | subject | 37 | 0.677364865 |
| human_identity_action_p90_rank | dateblock | 14 | 0.580357143 |
| human_identity_action_p90_rank | row | 10 | 0.568750000 |
| human_identity_action_p90_rank | actual | 6 | 0.770833333 |
| human_regime_only | subject | 42 | 0.592261905 |
| human_regime_only | dateblock | 17 | 0.444852941 |
| human_regime_only | row | 5 | 0.250000000 |
| human_regime_only | actual | 3 | 0.770833333 |
| oracle_p90_rank | subject | 31 | 0.937500000 |
| oracle_p90_rank | dateblock | 18 | 0.937500000 |
| oracle_p90_rank | row | 16 | 0.937500000 |
| oracle_p90_rank | actual | 2 | 0.937500000 |
| regime_then_geometry | subject | 51 | 0.618872549 |
| regime_then_geometry | dateblock | 10 | 0.512500000 |
| regime_then_geometry | actual | 3 | 0.750000000 |
| regime_then_geometry | row | 3 | 0.458333333 |

## Prefilter

- generated candidates: `540`
- old strict candidates: `403`
- info candidates: `103`
- null-evaluated candidates: `54`

| recipe | oracle_control | generated | old_strict | info | best_p90 | best_mean | median_l1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| policy_all | False | 120 | 113 | 4 | -0.003591197 | -0.007918767 | 11.903974288 |
| policy_mode | False | 120 | 106 | 11 | -0.002083285 | -0.005001558 | 11.576724478 |
| policy_top | False | 100 | 82 | 16 | -0.004283155 | -0.009265194 | 11.200000000 |
| policy_recipe | False | 110 | 56 | 43 | -0.001552520 | -0.004613502 | 13.495290954 |
| policy_recipe_mode | True | 80 | 40 | 25 | -0.000849225 | -0.001529640 | 11.200000000 |
| policy_recipe | True | 10 | 6 | 4 | -0.001047971 | -0.001661534 | 11.200000000 |

## Matched Null Governor

- public-free ready candidates: `0`

| slice | rows | old_strict | info | ready | best_p90 | best_mean | best_null_strict | best_worst_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| prefilter_all | 540 | 403 | 103 |  | -0.004283155 | -0.009265194 |  |  |
| governor_non_oracle | 47 | 30 | 12 | 0.000000000 | -0.004283155 | -0.009265194 | 0.000000000 | 1.000000000 |
| governor_all | 54 | 30 | 16 | 0.000000000 | -0.004283155 | -0.009265194 | 0.000000000 | 1.000000000 |

| recipe | oracle_control | evaluated | old_strict | ready | best_p90 | best_null_strict | best_worst_mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| policy_all | False | 17 | 17 | 0 | -0.003591197 | 0.000000000 | 0.750000000 |
| policy_top | False | 11 | 6 | 0 | -0.004283155 | 0.111111111 | 1.000000000 |
| policy_recipe | False | 7 | 4 | 0 | -0.001552520 | 0.055555556 | 0.750000000 |
| policy_mode | False | 12 | 3 | 0 | -0.002083285 | 0.250000000 | 1.000000000 |
| policy_recipe | True | 4 | 0 | 0 | -0.001047971 | 0.000000000 | 1.000000000 |
| policy_recipe_mode | True | 3 | 0 | 0 | -0.000849225 | 0.166666667 | 1.000000000 |

| basename | recipe | policy | group_key | base_variant | source_count | selected_mode_mix | oracle_control | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__call__w8_00_9d8aa4da.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.004566994 | -0.002656406 | 0.000000000 | 0.777777778 | 0.555555556 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__call__w5_00_aa1046bd.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003345549 | -0.002303764 | 0.000000000 | 0.722222222 | 0.555555556 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w3_00_bddd61ce.csv | policy_recipe | human_regime_only | human_regime_only__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|row:1|subject:15 | False | -0.002898039 | -0.001552520 | 0.166666667 | 0.944444444 | 0.833333333 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__call__w5_00_267d18b2.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.005951404 | -0.002774506 | 0.222222222 | 0.388888889 | 0.555555556 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w5_00_1691fcba.csv | policy_recipe | human_regime_only | human_regime_only__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|row:1|subject:15 | False | -0.003717209 | -0.001311870 | 0.222222222 | 0.833333333 | 0.944444444 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w5_00_b43c1dd0.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.004194943 | -0.002312305 | 0.277777778 | 0.722222222 | 0.722222222 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w8_00_2f5f5a54.csv | policy_mode | regime_then_geometry | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | False | -0.005001558 | -0.001959936 | 0.277777778 | 1.000000000 | 0.944444444 | 1.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w8_00_d150a0e8.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.004723574 | -0.002547032 | 0.333333333 | 0.555555556 | 0.611111111 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c128__w8_00_ce1c1638.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003268116 | -0.002091436 | 0.333333333 | 0.944444444 | 1.000000000 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_row2__c128__w8_00_6143e1ae.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_row2 | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.002966364 | -0.001672529 | 0.388888889 | 0.888888889 | 0.722222222 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__call__w3_00_30eb2465.csv | policy_recipe | regime_then_geometry | regime_then_geometry__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|subject:16 | False | -0.002904923 | -0.001488928 | 0.388888889 | 0.888888889 | 0.777777778 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w8_00_fa27c6ce.csv | policy_recipe | human_regime_only | human_regime_only__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|row:1|subject:15 | False | -0.004613502 | -0.001177752 | 0.388888889 | 0.722222222 | 0.666666667 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w5_00_3ba4b8d2.csv | policy_mode | regime_then_geometry | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | False | -0.004927804 | -0.001980488 | 0.444444444 | 0.944444444 | 0.888888889 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_row2__call__w8_00_7e58b2a7.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_row2 | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003718085 | -0.001787983 | 0.444444444 | 0.555555556 | 0.611111111 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__c128__w3_00_8a995cdb.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003103948 | -0.001748576 | 0.444444444 | 0.722222222 | 0.666666667 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__call__w8_00_d677a6c0.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.007918767 | -0.003591197 | 0.500000000 | 0.444444444 | 0.666666667 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__call__w8_00_3ee568b1.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_row2 | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.004426633 | -0.001997973 | 0.500000000 | 0.944444444 | 1.000000000 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_maxmean__call__w3_00_10bfa82d.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_maxmean | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003982354 | -0.001906503 | 0.500000000 | 0.500000000 | 0.611111111 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__c128__w8_00_c4221343.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_row2 | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.003601097 | -0.001540569 | 0.500000000 | 0.888888889 | 0.722222222 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_tbal__c64__w8_00_7cf38a1d.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_tbal | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.002261094 | -0.001851735 | 0.555555556 | 1.000000000 | 0.888888889 | 1.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_l1sum__call__w8_00_3f7aa99b.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_l1sum | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003223974 | -0.001840221 | 0.555555556 | 0.500000000 | 0.611111111 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__call__w3_00_1dcc4429.csv | policy_mode | regime_then_geometry | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | False | -0.004311833 | -0.001798804 | 0.555555556 | 0.833333333 | 0.888888889 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c128__w5_00_ec3ac8dd.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.002745679 | -0.001718306 | 0.555555556 | 0.944444444 | 1.000000000 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c128__w3_00_7a6bc150.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_maxmean | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.003738829 | -0.001596724 | 0.555555556 | 0.944444444 | 0.888888889 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__call__w3_00_cb7f8573.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_tbal | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.002235899 | -0.001588372 | 0.555555556 | 0.611111111 | 0.555555556 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_tbal__c64__w5_00_fd5d9107.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_tbal | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.001964846 | -0.001565622 | 0.611111111 | 1.000000000 | 1.000000000 | 1.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_l1sum__c128__w8_00_e4639ff1.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_l1sum | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.002526786 | -0.001690386 | 0.666666667 | 0.944444444 | 0.888888889 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_vote2__c128__w8_00_cdf28ac1.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_vote2 | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003047958 | -0.001662836 | 0.666666667 | 0.888888889 | 0.722222222 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_vote2__call__w8_00_d351d124.csv | policy_all | human_identity_action_p90_rank | human_identity_action_p90_rank__all | selected_vote2 | 67 | actual:6|dateblock:14|row:10|subject:37 | False | -0.003978004 | -0.001878901 | 0.722222222 | 0.666666667 | 0.611111111 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_vote2__c128__w8_00_fc7b441d.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_vote2 | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.003593804 | -0.001548065 | 0.722222222 | 0.888888889 | 0.833333333 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_tbal__c64__w3_00_8eb17e14.csv | policy_recipe | human_regime_only | human_regime_only__recipe_family_consensus | selected_tbal | 18 | dateblock:2|row:1|subject:15 | False | -0.001797370 | -0.001171026 | 0.055555556 | 0.888888889 | 0.833333333 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__call__w8_00_cfb40433.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_maxmean | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.009265194 | -0.004283155 | 0.111111111 | 0.944444444 | 1.000000000 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__call__w1_50_83ddd459.csv | policy_recipe | human_regime_only | human_regime_only__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|row:1|subject:15 | False | -0.001822526 | -0.001296973 | 0.111111111 | 0.944444444 | 0.944444444 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__call__w1_50_09016658.csv | policy_recipe | regime_then_geometry | regime_then_geometry__recipe_family_consensus | selected_maxmean | 18 | dateblock:2|subject:16 | False | -0.001800435 | -0.001259343 | 0.111111111 | 0.722222222 | 0.833333333 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__c128__w8_00_4c1487aa.csv | policy_mode | regime_then_geometry | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | False | -0.004660923 | -0.002083285 | 0.250000000 | 0.850000000 | 1.000000000 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__mode_actual__selected_maxmean__call__w5_00_73a40dff.csv | policy_mode | human_action_p90_rank | human_action_p90_rank__mode_actual | selected_maxmean | 9 | actual:9 | False | -0.002582257 | -0.001331255 | 0.277777778 | 0.666666667 | 0.611111111 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__c128__w5_00_4c1487aa.csv | policy_mode | regime_then_geometry | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | False | -0.004660923 | -0.002083285 | 0.350000000 | 0.850000000 | 0.900000000 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__mode_actual__selected_maxmean__c128__w5_00_f049f8af.csv | policy_mode | human_action_p90_rank | human_action_p90_rank__mode_actual | selected_maxmean | 9 | actual:9 | False | -0.002551198 | -0.001317788 | 0.388888889 | 0.666666667 | 0.611111111 | 0.000000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__mode_actual__selected_maxmean__call__w8_00_ace546fc.csv | policy_mode | human_action_p90_rank | human_action_p90_rank__mode_actual | selected_maxmean | 9 | actual:9 | False | -0.002647721 | -0.001304466 | 0.388888889 | 0.666666667 | 0.555555556 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__mode_actual__selected_maxmean__call__w3_00_f9525f06.csv | policy_mode | human_action_p90_rank | human_action_p90_rank__mode_actual | selected_maxmean | 9 | actual:9 | False | -0.002435095 | -0.001300985 | 0.388888889 | 0.611111111 | 0.500000000 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__mode_actual__selected_maxmean__c128__w8_00_5fad52f9.csv | policy_mode | human_action_p90_rank | human_action_p90_rank__mode_actual | selected_maxmean | 9 | actual:9 | False | -0.002598054 | -0.001282925 | 0.388888889 | 0.833333333 | 0.611111111 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__call__w5_00_d817faa8.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_maxmean | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.007214700 | -0.003330909 | 0.500000000 | 0.944444444 | 0.944444444 | 0.750000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c128__w8_00_95c22dad.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_maxmean | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.005092966 | -0.002072023 | 0.555555556 | 0.888888889 | 0.944444444 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c128__w5_00_a992efd3.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_maxmean | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.004720558 | -0.001974388 | 0.555555556 | 0.888888889 | 0.833333333 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_maxmean__c128__w3_00_202c266c.csv | policy_mode | regime_then_geometry | regime_then_geometry__mode_dateblock | selected_maxmean | 10 | dateblock:10 | False | -0.004239311 | -0.001915775 | 0.555555556 | 0.722222222 | 0.944444444 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__call__w3_00_1ca2778a.csv | policy_top | human_action_p90_rank | human_action_p90_rank__top24 | selected_maxmean | 24 | actual:5|dateblock:1|row:8|subject:10 | False | -0.005086598 | -0.002276280 | 0.611111111 | 0.833333333 | 0.888888889 | 0.500000000 | blocked_by_e319_nulls |
| submission_e319_modespec_human_action_p90_rank__mode_actual__selected_maxmean__c128__w3_00_433a4a1a.csv | policy_mode | human_action_p90_rank | human_action_p90_rank__mode_actual | selected_maxmean | 9 | actual:9 | False | -0.002416453 | -0.001292904 | 0.611111111 | 0.722222222 | 0.722222222 | 0.250000000 | blocked_by_e319_nulls |
| submission_e319_modespec_oracle_p90_rank__recipe_family_consensus__selected_maxmean__c64__w3_00_ca5c38e2.csv | policy_recipe | oracle_p90_rank | oracle_p90_rank__recipe_family_consensus | selected_maxmean | 18 | dateblock:5|row:2|subject:11 | True | -0.001660246 | -0.001047971 | 0.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | oracle_control_not_submittable |
| submission_e319_modespec_oracle_p90_rank__recipe_family_consensus__selected_maxmean__c64__w5_00_eeb6f457.csv | policy_recipe | oracle_p90_rank | oracle_p90_rank__recipe_family_consensus | selected_maxmean | 18 | dateblock:5|row:2|subject:11 | True | -0.001661534 | -0.001047480 | 0.050000000 | 1.000000000 | 1.000000000 | 1.000000000 | oracle_control_not_submittable |
| submission_e319_modespec_oracle_p90_rank__recipe_family_consensus__selected_maxmean__c64__w8_00_eeb6f457.csv | policy_recipe | oracle_p90_rank | oracle_p90_rank__recipe_family_consensus | selected_maxmean | 18 | dateblock:5|row:2|subject:11 | True | -0.001661534 | -0.001047480 | 0.050000000 | 1.000000000 | 1.000000000 | 1.000000000 | oracle_control_not_submittable |
| submission_e319_modespec_oracle_p90_rank__recipe_family_consensus__mode_dateblock__selected_maxmean__call__w3_00_0b6cc60f.csv | policy_recipe_mode | oracle_p90_rank | oracle_p90_rank__recipe_family_consensus__mode_dateblock | selected_maxmean | 5 | dateblock:5 | True | -0.001529640 | -0.000786184 | 0.166666667 | 1.000000000 | 1.000000000 | 1.000000000 | oracle_control_not_submittable |
| submission_e319_modespec_oracle_p90_rank__recipe_family_consensus__mode_dateblock__selected_tbal__call__w1_50_f7b67327.csv | policy_recipe_mode | oracle_p90_rank | oracle_p90_rank__recipe_family_consensus__mode_dateblock | selected_tbal | 5 | dateblock:5 | True | -0.001436309 | -0.000737422 | 0.166666667 | 1.000000000 | 1.000000000 | 1.000000000 | oracle_control_not_submittable |
| submission_e319_modespec_oracle_p90_rank__recipe_family_consensus__selected_maxmean__c64__w1_50_85f02c63.csv | policy_recipe | oracle_p90_rank | oracle_p90_rank__recipe_family_consensus | selected_maxmean | 18 | dateblock:5|row:2|subject:11 | True | -0.001284789 | -0.000844127 | 0.222222222 | 0.944444444 | 1.000000000 | 0.750000000 | oracle_control_not_submittable |
| submission_e319_modespec_oracle_p90_rank__recipe_family_consensus__mode_dateblock__selected_maxmean__call__w1_50_e1f6703a.csv | policy_recipe_mode | oracle_p90_rank | oracle_p90_rank__recipe_family_consensus__mode_dateblock | selected_maxmean | 5 | dateblock:5 | True | -0.001509170 | -0.000849225 | 0.333333333 | 1.000000000 | 1.000000000 | 1.000000000 | oracle_control_not_submittable |

## Decision

- No E319 fresh mode-specialized tensor is public-free ready.
- If old-strict tensors are null-common, the E318 regime signal is still diagnostic rather than generative.
- If oracle-control tensors also fail, the archive's placement oracle cannot be translated by consensus alone.
- The next branch should learn mode-specific action geometry directly instead of averaging selected placements.

## Outputs

- `analysis_outputs/e319_mode_specialized_generator_candidates.csv`
- `analysis_outputs/e319_mode_specialized_generator_selected.csv`
- `analysis_outputs/e319_mode_specialized_generator_governor.csv`
- `analysis_outputs/e319_mode_specialized_generator_summary.csv`
- `analysis_outputs/e319_mode_specialized_generator_report.md`
