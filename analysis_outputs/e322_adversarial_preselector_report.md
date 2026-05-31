# E322 Adversarial Preselector Null Check

Public LB was not used. This audits unevaluated E319 candidates selected by the E321 actual-geometry health target.

## Question

Can E321-style adversarial health select better unevaluated E319 candidates before fresh null evaluation?

## Preselector OOF

| target | n_train | target_mean | oof_spearman | oof_pearson | oof_rmse | pred_min | pred_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| target_worst_placement_dominance | 47 | 0.452128 | 0.492946 | 0.536005 | 0.259181 | -0.134057 | 1.198741 |
| null_strict_rate | 47 | 0.409929 | 0.564957 | 0.515731 | 0.167086 | 0.000069 | 1.076115 |
| target_adversarial_health | 47 | 0.042199 | 0.423243 | 0.457315 | 0.321047 | -1.036937 | 1.198672 |
| row_p90_dominance | 47 | 0.755319 | 0.208598 | 0.215498 | 0.293427 | 0.282577 | 1.339503 |
| subject_p90_dominance | 47 | 0.611702 | 0.589744 | 0.620573 | 0.290005 | -0.086786 | 1.208639 |
| dateblock_p90_dominance | 47 | 0.702128 | 0.721851 | 0.754040 | 0.226452 | -0.084350 | 1.269438 |

## Candidate Universe

| slice | rows | old_strict | previously_null_evaluated | best_pred_ready | best_pred_health | ready | best_fresh_p90 | best_null_strict | best_worst_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_non_oracle_e319 | 450 | 357 | 47.000000 | 1.049599 | 1.198672 |  |  |  |  |
| selected_for_fresh_null | 36 | 36 | 0.000000 | 0.818363 | 0.844700 |  |  |  |  |
| fresh_governor | 36 | 36 |  |  |  | 0.000000 | -0.001453 | 0.136364 | 1.000000 |

## Selected For Fresh Null

| basename | policy | recipe | base_variant | selection_reason | actual_p90 | pred_ready_score | pred_worst_placement_dominance | pred_null_strict_rate | pred_adversarial_health |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_row2__c128__w8_00_b0dfdc5e.csv | human_regime_only | policy_recipe | selected_row2 | guided_global | -0.001077 | 0.818363 | 0.935037 | 0.093339 | 0.841698 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_vote2__c128__w8_00_b6aa3bb6.csv | human_regime_only | policy_recipe | selected_vote2 | guided_global | -0.001145 | 0.808565 | 0.989239 | 0.144539 | 0.844700 |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__c128__w3_00_913e0d2c.csv | regime_then_geometry | policy_recipe | selected_maxmean | guided_global | -0.001063 | 0.757306 | 0.901924 | 0.115695 | 0.786229 |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__c128__w8_00_b25b3202.csv | regime_then_geometry | policy_recipe | selected_maxmean | guided_global | -0.000738 | 0.710564 | 0.950076 | 0.191610 | 0.758466 |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__c128__w5_00_20b420b7.csv | regime_then_geometry | policy_recipe | selected_maxmean | guided_global | -0.000879 | 0.668971 | 0.898186 | 0.183372 | 0.714814 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__c128__w3_00_3f0dceb3.csv | human_regime_only | policy_recipe | selected_maxmean | guided_global | -0.001100 | 0.634604 | 0.785981 | 0.121102 | 0.664879 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__c128__w8_00_c5f91ab9.csv | human_regime_only | policy_recipe | selected_maxmean | guided_global | -0.001015 | 0.500560 | 0.721250 | 0.176552 | 0.544698 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c128__w8_00_53bc1fa6.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.001019 | 0.466581 | 0.913602 | 0.357617 | 0.555985 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__c128__w5_00_14b24973.csv | human_regime_only | policy_recipe | selected_maxmean | guided_global | -0.001044 | 0.458370 | 0.685717 | 0.181877 | 0.503840 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__c128__w8_00_c01ecffd.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001249 | 0.421786 | 0.927480 | 0.404555 | 0.522925 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__call__w8_00_3cd3168f.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001160 | 0.397061 | 0.922344 | 0.420226 | 0.502118 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c64__w8_00_854895be.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000496 | 0.388037 | 0.925211 | 0.429739 | 0.495472 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_row2__c128__w3_00_00c567e5.csv | human_regime_only | policy_recipe | selected_row2 | guided_global | -0.000671 | 0.349366 | 0.779833 | 0.344373 | 0.435460 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c128__w5_00_607aa700.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000775 | 0.320586 | 0.840903 | 0.416254 | 0.424649 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c64__w5_00_43599c81.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000466 | 0.315275 | 0.881175 | 0.452719 | 0.428455 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_vote2__c128__w3_00_2c6c6a7f.csv | human_regime_only | policy_recipe | selected_vote2 | guided_global | -0.000696 | 0.286139 | 0.785114 | 0.399180 | 0.385934 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_vote2__call__w3_00_2409a948.csv | human_regime_only | policy_recipe | selected_vote2 | guided_global | -0.000691 | 0.279269 | 0.790734 | 0.409172 | 0.381562 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__c64__w8_00_17696bbe.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001056 | 0.200471 | 0.704877 | 0.403525 | 0.301352 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c64__w3_00_a25c8594.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000389 | 0.191495 | 0.891185 | 0.559752 | 0.331433 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__c128__w5_00_74984e2e.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001067 | 0.174839 | 0.739903 | 0.452051 | 0.287852 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c128__w3_00_9d3bc186.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000519 | 0.162806 | 0.828258 | 0.532362 | 0.295896 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__call__w5_00_986c103c.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001011 | 0.151404 | 0.728326 | 0.461538 | 0.266789 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__c64__w8_00_cdc28f59.csv | human_action_p90_rank | policy_top | selected_row2 | guided_recipe | -0.001084 | 0.039544 | 0.740865 | 0.561057 | 0.179809 |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_l1sum__c32__w8_00_2aa61eb7.csv | regime_then_geometry | policy_mode | selected_l1sum | guided_variant | -0.000474 | 0.025045 | 0.757002 | 0.585565 | 0.171437 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_l1sum__c128__w5_00_30a616b1.csv | human_regime_only | policy_recipe | selected_l1sum | guided_variant | -0.000599 | 0.023641 | 0.614330 | 0.472551 | 0.141779 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c64__w8_00_17ed7ded.csv | human_action_p90_rank | policy_top | selected_maxmean | guided_recipe | -0.001131 | 0.012100 | 0.701059 | 0.551167 | 0.149891 |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_l1sum__c64__w5_00_69912a58.csv | human_regime_only | policy_recipe | selected_l1sum | guided_variant | -0.000367 | -0.027329 | 0.617481 | 0.515848 | 0.101633 |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c64__w8_00_efc83a6b.csv | human_identity_action_p90_rank | policy_all | selected_tbal | guided_recipe | -0.001362 | -0.038296 | 0.502002 | 0.432238 | 0.069764 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c64__w5_00_17ed7ded.csv | human_action_p90_rank | policy_top | selected_maxmean | guided_recipe | -0.001131 | -0.045730 | 0.657724 | 0.562763 | 0.094961 |
| submission_e319_modespec_human_action_p90_rank__top24__selected_vote2__c64__w8_00_cdc28f59.csv | human_action_p90_rank | policy_top | selected_vote2 | guided_recipe | -0.001084 | -0.059325 | 0.708405 | 0.614184 | 0.094221 |

## Fresh Governor

| basename | policy | recipe | base_variant | selection_reason | fresh_actual_p90 | fresh_null_strict_rate | fresh_p90_dominance | fresh_mean_dominance | fresh_worst_mode_p90_dominance | fresh_row_p90_dominance | fresh_subject_p90_dominance | fresh_dateblock_p90_dominance | fresh_public_free_submission_ready | fresh_final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_row2__c128__w8_00_b0dfdc5e.csv | human_regime_only | policy_recipe | selected_row2 | guided_global | -0.001077 | 0.136364 | 0.954545 | 0.909091 | 0.800000 | 1.000000 | 1.000000 | 0.800000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_vote2__c128__w8_00_b6aa3bb6.csv | human_regime_only | policy_recipe | selected_vote2 | guided_global | -0.001145 | 0.181818 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__c128__w3_00_913e0d2c.csv | regime_then_geometry | policy_recipe | selected_maxmean | guided_global | -0.001063 | 0.272727 | 0.818182 | 0.863636 | 0.600000 | 1.000000 | 0.600000 | 0.600000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_vote2__call__w3_00_2409a948.csv | human_regime_only | policy_recipe | selected_vote2 | guided_global | -0.000691 | 0.272727 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_row2__c128__w3_00_00c567e5.csv | human_regime_only | policy_recipe | selected_row2 | guided_global | -0.000671 | 0.272727 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__c128__w3_00_3f0dceb3.csv | human_regime_only | policy_recipe | selected_maxmean | guided_global | -0.001100 | 0.318182 | 0.909091 | 0.909091 | 0.600000 | 1.000000 | 1.000000 | 0.600000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__c128__w5_00_20b420b7.csv | regime_then_geometry | policy_recipe | selected_maxmean | guided_global | -0.000879 | 0.318182 | 0.954545 | 0.818182 | 0.800000 | 1.000000 | 1.000000 | 0.800000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__recipe_family_consensus__selected_maxmean__c128__w8_00_b25b3202.csv | regime_then_geometry | policy_recipe | selected_maxmean | guided_global | -0.000738 | 0.318182 | 1.000000 | 0.772727 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_vote2__c128__w3_00_2c6c6a7f.csv | human_regime_only | policy_recipe | selected_vote2 | guided_global | -0.000696 | 0.409091 | 0.954545 | 0.909091 | 0.800000 | 1.000000 | 1.000000 | 0.800000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__blend35_maxmean__call__w3_00_2bba2e57.csv | human_identity_action_p90_rank | policy_all | blend35_maxmean | guided_variant | -0.001453 | 0.454545 | 0.727273 | 0.727273 | 0.200000 | 1.000000 | 0.200000 | 0.600000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__c128__w8_00_c5f91ab9.csv | human_regime_only | policy_recipe | selected_maxmean | guided_global | -0.001015 | 0.454545 | 1.000000 | 0.818182 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_l1sum__c128__w5_00_30a616b1.csv | human_regime_only | policy_recipe | selected_l1sum | guided_variant | -0.000599 | 0.454545 | 0.863636 | 0.863636 | 0.400000 | 1.000000 | 1.000000 | 0.400000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_l1sum__c32__w8_00_b3f78db7.csv | human_identity_action_p90_rank | policy_all | selected_l1sum | guided_recipe | -0.000515 | 0.454545 | 0.772727 | 0.727273 | 0.200000 | 1.000000 | 0.200000 | 0.800000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__blend35_maxmean__c128__w3_00_11473046.csv | human_identity_action_p90_rank | policy_all | blend35_maxmean | guided_variant | -0.001318 | 0.500000 | 0.818182 | 0.772727 | 0.600000 | 0.600000 | 0.800000 | 0.800000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c64__w5_00_49444db7.csv | human_identity_action_p90_rank | policy_all | selected_tbal | guided_recipe | -0.001242 | 0.500000 | 0.954545 | 1.000000 | 0.800000 | 1.000000 | 0.800000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_maxmean__c128__w5_00_14b24973.csv | human_regime_only | policy_recipe | selected_maxmean | guided_global | -0.001044 | 0.500000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c128__w8_00_53bc1fa6.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.001019 | 0.500000 | 0.909091 | 1.000000 | 0.600000 | 1.000000 | 0.600000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_row2__c32__w8_00_0162dc1f.csv | human_identity_action_p90_rank | policy_all | selected_row2 | guided_recipe | -0.000565 | 0.500000 | 0.954545 | 0.863636 | 0.800000 | 1.000000 | 0.800000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_regime_only__recipe_family_consensus__selected_l1sum__c64__w5_00_69912a58.csv | human_regime_only | policy_recipe | selected_l1sum | guided_variant | -0.000367 | 0.500000 | 0.681818 | 0.772727 | 0.000000 | 1.000000 | 0.600000 | 0.200000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__blend35_maxmean__c64__w8_00_777d98a1.csv | human_identity_action_p90_rank | policy_all | blend35_maxmean | guided_variant | -0.001282 | 0.545455 | 0.863636 | 0.545455 | 0.600000 | 0.600000 | 1.000000 | 0.800000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c128__w5_00_607aa700.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000775 | 0.545455 | 0.954545 | 0.954545 | 0.800000 | 1.000000 | 0.800000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c64__w5_00_43599c81.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000466 | 0.545455 | 0.909091 | 0.909091 | 0.000000 | 1.000000 | 0.800000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c64__w3_00_a25c8594.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000389 | 0.545455 | 0.772727 | 0.727273 | 0.000000 | 1.000000 | 0.200000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c64__w8_00_17ed7ded.csv | human_action_p90_rank | policy_top | selected_maxmean | guided_recipe | -0.001131 | 0.583333 | 0.958333 | 0.666667 | 0.800000 | 0.800000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_identity_action_p90_rank__all__selected_tbal__c64__w8_00_efc83a6b.csv | human_identity_action_p90_rank | policy_all | selected_tbal | guided_recipe | -0.001362 | 0.590909 | 0.954545 | 1.000000 | 0.800000 | 1.000000 | 0.800000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__c128__w8_00_c01ecffd.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001249 | 0.590909 | 0.409091 | 0.954545 | 0.000000 | 0.200000 | 0.000000 | 0.200000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c64__w8_00_854895be.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000496 | 0.590909 | 0.818182 | 0.772727 | 0.000000 | 1.000000 | 0.600000 | 0.800000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__call__w8_00_3cd3168f.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001160 | 0.636364 | 0.409091 | 0.818182 | 0.000000 | 0.000000 | 0.000000 | 0.400000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__c128__w5_00_74984e2e.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001067 | 0.636364 | 0.500000 | 0.772727 | 0.200000 | 0.400000 | 0.200000 | 0.200000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__call__w5_00_986c103c.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001011 | 0.636364 | 0.500000 | 0.818182 | 0.200000 | 0.400000 | 0.200000 | 0.200000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_tbal__c128__w3_00_9d3bc186.csv | regime_then_geometry | policy_mode | selected_tbal | guided_global | -0.000519 | 0.636364 | 0.818182 | 0.818182 | 0.000000 | 1.000000 | 0.400000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_maxmean__c64__w5_00_17ed7ded.csv | human_action_p90_rank | policy_top | selected_maxmean | guided_recipe | -0.001131 | 0.708333 | 0.916667 | 0.666667 | 0.600000 | 0.600000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_vote2__c64__w8_00_cdc28f59.csv | human_action_p90_rank | policy_top | selected_vote2 | guided_recipe | -0.001084 | 0.727273 | 0.909091 | 0.772727 | 0.600000 | 0.600000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_human_action_p90_rank__top24__selected_row2__c64__w8_00_cdc28f59.csv | human_action_p90_rank | policy_top | selected_row2 | guided_recipe | -0.001084 | 0.727273 | 0.954545 | 0.727273 | 0.800000 | 0.800000 | 1.000000 | 1.000000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_row2__c64__w8_00_17696bbe.csv | regime_then_geometry | policy_mode | selected_row2 | guided_global | -0.001056 | 0.772727 | 0.590909 | 0.772727 | 0.200000 | 0.200000 | 0.400000 | 0.600000 | False | blocked_by_e322_nulls |
| submission_e319_modespec_regime_then_geometry__mode_dateblock__selected_l1sum__c32__w8_00_2aa61eb7.csv | regime_then_geometry | policy_mode | selected_l1sum | guided_variant | -0.000474 | 0.772727 | 0.818182 | 0.954545 | 0.400000 | 1.000000 | 0.400000 | 0.800000 | False | blocked_by_e322_nulls |

## Decision

- E321-guided preselection did not find a public-free E319 candidate.
- This weakens the idea that a good candidate was merely skipped by E319's original null-eval budget.
- The useful signal is still the action-health target itself; it needs to be used during generation, not only after E319 averaging.

## Outputs

- `analysis_outputs/e322_adversarial_preselector_all_audit.csv`
- `analysis_outputs/e322_adversarial_preselector_oof_audit.csv`
- `analysis_outputs/e322_adversarial_preselector_selected_audit.csv`
- `analysis_outputs/e322_adversarial_preselector_governor_audit.csv`
- `analysis_outputs/e322_adversarial_preselector_summary.csv`
- `analysis_outputs/e322_adversarial_preselector_report.md`
