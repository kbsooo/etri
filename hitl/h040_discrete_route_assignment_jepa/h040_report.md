# H040 Discrete Route-Assignment HS-JEPA

## Question

Can post-H012 translation be solved by assigning whole rows to discrete public/private routes instead of applying smooth local cell projections?

## External observation absorbed

- Attached V106 note reports `submission_v106_sleep_state_conditioned_memory.csv` public LB `0.5703952266`, using same-subject date + sleep-state + sensor-quality memory. This supports repeated-subject human-state memory, but H012 is still better by `0.0022717435`.

## Row route state

- rows: `250`

- mean public-route score: `0.502000000`

- mean private-memory score: `0.501600000`

- mean transition-exception score: `0.502000000`


Top public-route rows:

| row | subject_id | sleep_date | public_route_score | private_memory_route_score | transition_exception_route_score | support_count | memory_disagree_rate | row_public_prob |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 143 | id06 | 2024-08-13 00:00:00 | 0.950360000 | 0.378480000 | 0.824240000 | 7 | 1.000000000 | 0.865564030 |
| 144 | id06 | 2024-08-14 00:00:00 | 0.942760000 | 0.214480000 | 0.866520000 | 7 | 1.000000000 | 0.862846853 |
| 141 | id06 | 2024-08-10 00:00:00 | 0.930840000 | 0.208760000 | 0.873480000 | 6 | 0.714285714 | 0.881621523 |
| 43 | id02 | 2024-09-29 00:00:00 | 0.927000000 | 0.093160000 | 0.893880000 | 6 | 0.714285714 | 0.865185420 |
| 140 | id06 | 2024-07-21 00:00:00 | 0.922920000 | 0.318480000 | 0.779400000 | 6 | 0.571428571 | 0.886586736 |
| 48 | id02 | 2024-10-05 00:00:00 | 0.918680000 | 0.554080000 | 0.785400000 | 7 | 0.571428571 | 0.908885420 |
| 151 | id06 | 2024-08-25 00:00:00 | 0.909880000 | 0.757120000 | 0.752840000 | 7 | 0.571428571 | 0.926057313 |
| 65 | id03 | 2024-08-24 00:00:00 | 0.908280000 | 0.546080000 | 0.847480000 | 7 | 0.714285714 | 0.902155957 |
| 59 | id03 | 2024-08-17 00:00:00 | 0.901000000 | 0.698720000 | 0.727640000 | 6 | 0.428571429 | 0.902248447 |
| 150 | id06 | 2024-08-24 00:00:00 | 0.901000000 | 0.565080000 | 0.873320000 | 6 | 0.714285714 | 0.873890922 |
| 147 | id06 | 2024-08-21 00:00:00 | 0.898840000 | 0.482160000 | 0.726000000 | 7 | 0.714285714 | 0.840999989 |
| 135 | id06 | 2024-07-14 00:00:00 | 0.889320000 | 0.453280000 | 0.872280000 | 7 | 0.714285714 | 0.841086653 |


## Candidate ranking

| candidate_id | family | route_public | public_rows | public_mode | alpha_public | route_private | private_rows | world_cell_delta_vs_h012 | posterior_delta_vs_h012 | route_delta_vs_h012 | changed_cells_vs_h012 | row_route_complete_rate | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | pred_gain_top1200_sum | h040_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h040_public_route_world_p140_world_high_a0.45_h012_v0_support_b0_all_0985acf7 | public_route | world | 140 | world_high | 0.450000000 | h012 | 0 | -0.001426068 | -0.001708677 | -0.000686116 | 334 | 0.215384615 | 0.007548586 | 0.250000000 | -3.854202503 | 3.854816788 | 0.328963415 |
| h040_public_route_posterior_world_p140_world_high_a0.7_h012_v0_support_b0_all_94945876 | public_route | posterior_world | 140 | world_high | 0.700000000 | h012 | 0 | -0.001424671 | -0.002007032 | -0.000730170 | 334 | 0.215384615 | 0.010157868 | 0.250000000 | -3.888593899 | 3.889208184 | 0.398475610 |
| h040_transition_exception_world_p140_world_high_a0.45_h012_v0_support_b0_all_96b84b21 | transition_exception | world | 140 | world_high | 0.450000000 | h012 | 0 | -0.001354702 | -0.001344194 | -0.000628099 | 324 | 0.210937500 | 0.007436993 | 0.250000000 | -3.767011534 | 3.767611534 | 0.404573171 |
| h040_public_route_world_p140_world_high_a0.7_h012_v0_support_b0_all_6c38d486 | public_route | world | 140 | world_high | 0.700000000 | h012 | 0 | -0.001822252 | -0.001877076 | -0.000757082 | 334 | 0.215384615 | 0.011741306 | 0.250000000 | -3.858184338 | 3.858841481 | 0.405640244 |
| h040_public_route_world_p110_all_a0.45_h012_v0_support_b0_all_6d031633 | public_route | world | 110 | all | 0.450000000 | h012 | 0 | -0.001375677 | -0.001394341 | -0.000665687 | 770 | 1.000000000 | 0.007772610 | 0.250000000 | -1.526015688 | 1.526615688 | 0.417225610 |
| h040_public_route_world_p140_support_a0.45_h012_v0_support_b0_all_ce9ecf28 | public_route | world | 140 | support | 0.450000000 | h012 | 0 | -0.001431591 | -0.001769125 | -0.000745563 | 758 | 0.964285714 | 0.007886970 | 0.250000000 | -0.389919490 | 0.390533776 | 0.436890244 |
| h040_public_route_world_p140_all_a0.45_h012_v0_support_b0_all_3c160462 | public_route | world | 140 | all | 0.450000000 | h012 | 0 | -0.001572754 | -0.001769125 | -0.000782169 | 980 | 1.000000000 | 0.008138367 | 0.250000000 | 0.641490818 | -0.640876532 | 0.439329268 |
| h040_public_route_posterior_world_p110_world_high_a0.7_h012_v0_support_b0_all_251c3ba9 | public_route | posterior_world | 110 | world_high | 0.700000000 | h012 | 0 | -0.001274380 | -0.001578577 | -0.000634952 | 296 | 0.254716981 | 0.009797437 | 0.250000000 | -4.042756162 | 4.043356162 | 0.451829268 |
| h040_public_route_world_p110_world_high_a0.7_h012_v0_support_b0_all_7ddf4b85 | public_route | world | 110 | world_high | 0.700000000 | h012 | 0 | -0.001625375 | -0.001454535 | -0.000658920 | 296 | 0.254716981 | 0.011434649 | 0.250000000 | -4.037346977 | 4.037989834 | 0.463109756 |
| h040_transition_exception_posterior_world_p140_world_high_a0.7_h012_v0_support_b0_all_9702e1 | transition_exception | posterior_world | 140 | world_high | 0.700000000 | h012 | 0 | -0.001341280 | -0.001561191 | -0.000662064 | 324 | 0.210937500 | 0.009987714 | 0.250000000 | -3.793370201 | 3.793970201 | 0.465243902 |
| h040_transition_exception_world_p140_world_high_a0.7_h012_v0_support_b0_all_7202fd10 | transition_exception | world | 140 | world_high | 0.700000000 | h012 | 0 | -0.001728970 | -0.001425444 | -0.000684988 | 324 | 0.210937500 | 0.011566560 | 0.250000000 | -3.761432277 | 3.762075134 | 0.480182927 |
| h040_public_route_world_p110_all_a0.7_h012_v0_support_b0_all_8a3bbe18 | public_route | world | 110 | all | 0.700000000 | h012 | 0 | -0.001756410 | -0.001485942 | -0.000726681 | 770 | 1.000000000 | 0.012069582 | 0.250000000 | -1.585478756 | 1.586121614 | 0.482621951 |
| h040_public_route_posterior_world_p110_all_a0.7_h012_v0_support_b0_all_69626934 | public_route | posterior_world | 110 | all | 0.700000000 | h012 | 0 | -0.001360410 | -0.001717271 | -0.000723406 | 770 | 1.000000000 | 0.010549068 | 0.250000000 | -1.655115136 | 1.655715136 | 0.484756098 |
| h040_public_route_world_p110_support_a0.45_h012_v0_support_b0_all_85b0266a | public_route | world | 110 | support | 0.450000000 | h012 | 0 | -0.001265257 | -0.001394341 | -0.000637302 | 607 | 0.954545455 | 0.007577927 | 0.250000000 | -2.143453406 | 2.144053406 | 0.491310976 |
| h040_public_route_posterior_world_p110_all_a0.45_h012_v0_support_b0_all_a59013d3 | public_route | posterior_world | 110 | all | 0.450000000 | h012 | 0 | -0.000992372 | -0.001398212 | -0.000560732 | 770 | 1.000000000 | 0.006795297 | 0.250000000 | -1.520764419 | 1.521335848 | 0.491463415 |
| h040_transition_exception_world_p80_all_a0.45_h012_v0_support_b0_all_4f7eb7f5 | transition_exception | world | 80 | all | 0.450000000 | h012 | 0 | -0.001070311 | -0.001186319 | -0.000505329 | 560 | 1.000000000 | 0.006755963 | 0.250000000 | -1.377906095 | 1.378391809 | 0.508993902 |
| h040_public_route_posterior_world_p140_all_a0.45_h012_v0_support_b0_all_af7044d2 | public_route | posterior_world | 140 | all | 0.450000000 | h012 | 0 | -0.001129908 | -0.001780271 | -0.000662502 | 979 | 1.000000000 | 0.007073278 | 0.250000000 | 0.620435355 | -0.619849640 | 0.518140244 |
| h040_transition_exception_world_p110_all_a0.45_h012_v0_support_b0_all_6501b78d | transition_exception | world | 110 | all | 0.450000000 | h012 | 0 | -0.001285541 | -0.001263769 | -0.000615639 | 770 | 1.000000000 | 0.007489671 | 0.250000000 | -0.313164454 | 0.313721597 | 0.518902439 |
| h040_public_route_posterior_world_p140_support_a0.45_h012_v0_support_b0_all_816e57de | public_route | posterior_world | 140 | support | 0.450000000 | h012 | 0 | -0.001047588 | -0.001780271 | -0.000634587 | 757 | 0.964285714 | 0.006936804 | 0.250000000 | -0.385091964 | 0.385677679 | 0.518902439 |
| h040_transition_exception_world_p110_world_high_a0.7_h012_v0_support_b0_all_c9477c20 | transition_exception | world | 110 | world_high | 0.700000000 | h012 | 0 | -0.001498017 | -0.001308300 | -0.000598851 | 278 | 0.252427184 | 0.010937521 | 0.250000000 | -3.702732238 | 3.703317952 | 0.522103659 |


Decision:

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | family | world_cell_delta_vs_h012 | posterior_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | rowperm_real_top1200_sum | rowperm_p_perm_ge_real | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| do_not_promote | False | h040_public_route_world_p140_world_high_a0.45_h012_v0_support_b0_all_0985acf7 | submission_h040_public_route_world_p140_world_high_a0.45_h012_v0_support_b0_all_0985acf7.csv | /Users/kbsoo/Downloads/cl2/hitl/h040_discrete_route_assignment_jepa/submission_h040_public_route_world_p140_world_high_a0.45_h012_v0_support_b0_all_0985acf7.csv | public_route | -0.001426068 | -0.001708677 | 0.007548586 | 0.250000000 | -3.854202503 | 3.854816788 | 0.280000000 | H024 pre-H012 does not prefer over H012; H024 support below 55% |


## Interpretation
- If H024/H025 still reject the best route candidates, simple row-level public/private assignment is not enough.
- If route candidates improve world/posterior proxies but fail action-health, H012 remains a locked public-equation basin.
- The next big-bet direction after failure is to resample hidden public/private subset equations directly, not to continue H012 by local edits.
