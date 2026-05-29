# E179 E176 Critical-Cell Visibility Audit

## Question

E178 says E176 has a broad expected edge, but only a few hard-label cells can
decide its public score. Are those cells visible to train-derived priors and
flanks before public feedback?

## Result In One Sentence

E176's full body and Q2 damping are favorable under visible priors, but its top
public-decisive cells are weak versus target-matched nulls; E176 is therefore
better supported than raw broad siblings but still not locally certified at
hard-label resolution.

## Critical E176-vs-E95 Cells

| sub_idx | target | swing_rank | swing | support_label | support_probability_visible_mean | support_prob_min | support_prob_range | n_priors_support_ge_05 | context_type | pos_bin | e72_active | e101_active | flank_conflict | p_y1_subject | p_y1_edge_endpoint_beta | p_y1_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 141 | S1 | 1 | 0.000005832 | 0 | 0.098647741 | 0.038461538 | 0.279316239 | 0 | between_train_runs | single | False | False | False | 0.937500000 | 0.958333333 | 0.850000000 |
| 196 | Q3 | 2 | 0.000004562 | 1 | 0.335671769 | 0.150000000 | 0.450000000 | 1 | between_train_runs | right_edge | True | False | False | 0.446428571 | 0.297619048 | 0.150000000 |
| 190 | Q3 | 3 | 0.000004531 | 1 | 0.603741497 | 0.446428571 | 0.403571429 | 9 | between_train_runs | left_edge | True | False | True | 0.446428571 | 0.630952381 | 0.850000000 |
| 194 | Q3 | 4 | 0.000004466 | 1 | 0.351615646 | 0.150000000 | 0.450000000 | 1 | between_train_runs | near_edge | True | False | False | 0.446428571 | 0.297619048 | 0.150000000 |
| 67 | S4 | 5 | 0.000004432 | 1 | 0.187647908 | 0.101010101 | 0.458989899 | 1 | between_train_runs | interior | False | False | False | 0.151515152 | 0.101010101 | 0.150000000 |
| 135 | S1 | 6 | 0.000004082 | 0 | 0.099087302 | 0.040000000 | 0.277777778 | 0 | between_train_runs | right_edge | True | False | False | 0.937500000 | 0.958333333 | 0.850000000 |
| 143 | S1 | 7 | 0.000004017 | 0 | 0.100263772 | 0.041666667 | 0.276111111 | 0 | between_train_runs | near_edge | False | False | False | 0.937500000 | 0.958333333 | 0.850000000 |
| 182 | Q3 | 8 | 0.000004015 | 1 | 0.332482993 | 0.150000000 | 0.450000000 | 1 | between_train_runs | left_edge | True | False | False | 0.446428571 | 0.297619048 | 0.150000000 |
| 205 | S2 | 9 | 0.000003995 | 0 | 0.199375846 | 0.146341463 | 0.202547425 | 0 | between_train_runs | interior | False | False | False | 0.780487805 | 0.853658537 | 0.850000000 |
| 136 | S1 | 10 | 0.000003981 | 0 | 0.098936926 | 0.039473684 | 0.278304094 | 0 | between_train_runs | left_edge | True | False | False | 0.937500000 | 0.958333333 | 0.850000000 |
| 139 | S3 | 11 | 0.000003936 | 0 | 0.092788018 | 0.027777778 | 0.310000000 | 0 | between_train_runs | near_edge | False | False | False | 0.958333333 | 0.972222222 | 0.850000000 |
| 180 | S1 | 12 | 0.000003915 | 0 | 0.191585726 | 0.136054422 | 0.181723356 | 0 | after_train_run | near_edge | False | False | False | 0.795918367 | 0.863945578 | 0.850000000 |
| 63 | S1 | 13 | 0.000003819 | 0 | 0.428938284 | 0.181818182 | 0.668181818 | 2 | between_train_runs | interior | False | False | True | 0.818181818 | 0.545454545 | 0.150000000 |
| 70 | S4 | 14 | 0.000003816 | 1 | 0.425093795 | 0.151515152 | 0.698484848 | 3 | after_train_run | left_edge | False | False | False | 0.151515152 | 0.434343434 | 0.850000000 |
| 113 | Q1 | 15 | 0.000003792 | 1 | 0.654638594 | 0.495555556 | 0.354444444 | 9 | between_train_runs | right_edge | False | False | True | 0.613636364 | 0.742424242 | 0.850000000 |
| 132 | S1 | 16 | 0.000003791 | 0 | 0.102235990 | 0.041666667 | 0.276111111 | 0 | between_train_runs | interior | False | False | False | 0.937500000 | 0.958333333 | 0.850000000 |
| 5 | Q1 | 17 | 0.000003755 | 1 | 0.352165684 | 0.150000000 | 0.345555556 | 0 | between_train_runs | interior | True | False | False | 0.439024390 | 0.292682927 | 0.150000000 |
| 138 | S3 | 18 | 0.000003626 | 0 | 0.092788018 | 0.027777778 | 0.310000000 | 0 | between_train_runs | interior | False | False | False | 0.958333333 | 0.972222222 | 0.850000000 |
| 163 | Q1 | 19 | 0.000003596 | 1 | 0.387238188 | 0.150000000 | 0.360204082 | 1 | between_train_runs | interior | True | False | False | 0.510204082 | 0.340136054 | 0.150000000 |
| 141 | Q1 | 20 | 0.000003521 | 1 | 0.166474359 | 0.089743590 | 0.405811966 | 0 | between_train_runs | single | False | False | False | 0.145833333 | 0.097222222 | 0.150000000 |
| 164 | S1 | 21 | 0.000003515 | 0 | 0.183236703 | 0.136054422 | 0.181723356 | 0 | between_train_runs | interior | True | False | False | 0.795918367 | 0.863945578 | 0.850000000 |
| 0 | Q1 | 22 | 0.000003508 | 1 | 0.336730630 | 0.150000000 | 0.345555556 | 0 | between_train_runs | left_edge | True | False | False | 0.439024390 | 0.292682927 | 0.150000000 |
| 204 | S2 | 23 | 0.000003452 | 0 | 0.198346755 | 0.146341463 | 0.202547425 | 0 | between_train_runs | interior | False | False | False | 0.780487805 | 0.853658537 | 0.850000000 |
| 79 | S4 | 24 | 0.000003436 | 1 | 0.394869474 | 0.151515152 | 0.698484848 | 3 | after_train_run | right_edge | False | False | False | 0.151515152 | 0.434343434 | 0.850000000 |
| 160 | S1 | 25 | 0.000003382 | 0 | 0.186591613 | 0.136054422 | 0.181723356 | 0 | between_train_runs | interior | False | False | False | 0.795918367 | 0.863945578 | 0.850000000 |
| 78 | Q2 | 26 | 0.000003359 | 0 | 0.195417089 | 0.121212121 | 0.316565657 | 0 | after_train_run | near_edge | False | False | False | 0.818181818 | 0.878787879 | 0.850000000 |
| 142 | S1 | 27 | 0.000003316 | 0 | 0.098647741 | 0.038461538 | 0.279316239 | 0 | between_train_runs | left_edge | True | False | False | 0.937500000 | 0.958333333 | 0.850000000 |
| 43 | S2 | 28 | 0.000003315 | 0 | 0.114920635 | 0.055555556 | 0.293333333 | 0 | after_train_run | left_edge | False | False | False | 0.916666667 | 0.944444444 | 0.850000000 |
| 79 | Q2 | 29 | 0.000003309 | 0 | 0.195577856 | 0.121212121 | 0.316565657 | 0 | after_train_run | right_edge | False | False | False | 0.818181818 | 0.878787879 | 0.850000000 |
| 67 | S1 | 30 | 0.000003265 | 0 | 0.225645743 | 0.121212121 | 0.378787879 | 1 | between_train_runs | interior | True | False | True | 0.818181818 | 0.878787879 | 0.850000000 |
| 150 | S3 | 31 | 0.000003250 | 0 | 0.094393939 | 0.027777778 | 0.310000000 | 0 | after_train_run | near_edge | False | False | False | 0.958333333 | 0.972222222 | 0.850000000 |
| 195 | S1 | 32 | 0.000003173 | 1 | 0.360462791 | 0.150000000 | 0.532222222 | 1 | between_train_runs | near_edge | False | False | False | 0.446428571 | 0.297619048 | 0.150000000 |
| 166 | S1 | 33 | 0.000003171 | 0 | 0.172880241 | 0.133096717 | 0.184681061 | 0 | between_train_runs | right_edge | False | False | False | 0.795918367 | 0.863945578 | 0.850000000 |

## Set Summary

| set | n_cells | n_rows | targets | expected_delta_visible_mean | support_swing_weighted_visible_mean | hard_support_rate_visible_mean | support_prob_min_mean | all_prior_support_rate | prior_split_rate | ambiguous_visible_rate | flank_conflict_rate | between_train_runs_rate | e72_active_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_moved | 904 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000050824 | 0.373623439 | 0.330752212 | 0.242887267 | 0.134955752 | 0.559734513 | 0.066371681 | 0.268805310 | 0.819690265 | 0.268805310 |
| top1_swing | 1 | 1 | S1 | -0.000000164 | 0.098647741 | 0.000000000 | 0.038461538 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 1.000000000 | 0.000000000 |
| top4_e95_edge | 4 | 4 | Q3,S1 | -0.000001965 | 0.330699094 | 0.250000000 | 0.196222527 | 0.000000000 | 0.750000000 | 0.000000000 | 0.250000000 | 1.000000000 | 0.750000000 |
| top8_swing | 8 | 8 | Q3,S1,S4 | -0.000002948 | 0.261188735 | 0.125000000 | 0.139695860 | 0.000000000 | 0.625000000 | 0.000000000 | 0.125000000 | 1.000000000 | 0.625000000 |
| top16_swing | 16 | 16 | Q1,Q3,S1,S2,S3,S4 | -0.000005872 | 0.266074266 | 0.125000000 | 0.146110611 | 0.000000000 | 0.500000000 | 0.000000000 | 0.187500000 | 0.875000000 | 0.375000000 |
| top33_expected_flip | 33 | 30 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000010469 | 0.245771136 | 0.060606061 | 0.128599532 | 0.000000000 | 0.363636364 | 0.000000000 | 0.121212121 | 0.787878788 | 0.363636364 |
| top33_expected_benefit | 33 | 28 | Q1,Q3,S1,S3,S4 | -0.000018440 | 0.374573580 | 0.363636364 | 0.239501586 | 0.030303030 | 0.757575758 | 0.060606061 | 0.181818182 | 0.757575758 | 0.363636364 |
| between_train_runs | 741 | 156 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000038589 | 0.368379559 | 0.341430499 | 0.245085674 | 0.143049933 | 0.556005398 | 0.070175439 | 0.327935223 | 1.000000000 | 0.267206478 |
| not_e72_active | 661 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000032310 | 0.363578681 | 0.326777610 | 0.242231407 | 0.130105900 | 0.558245083 | 0.062027231 | 0.270801815 | 0.821482602 | 0.000000000 |
| between_and_not_e72 | 543 | 156 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000024707 | 0.364265303 | 0.335174954 | 0.244799521 | 0.143646409 | 0.548802947 | 0.066298343 | 0.329650092 | 1.000000000 | 0.000000000 |
| target_Q1 | 121 | 121 | Q1 | -0.000010373 | 0.406551509 | 0.289256198 | 0.237226963 | 0.041322314 | 0.735537190 | 0.024793388 | 0.289256198 | 0.818181818 | 0.388429752 |
| target_Q2 | 165 | 165 | Q2 | -0.000004525 | 0.459311936 | 0.345454545 | 0.258395818 | 0.090909091 | 0.612121212 | 0.018181818 | 0.278787879 | 0.824242424 | 0.006060606 |
| target_Q3 | 117 | 117 | Q3 | -0.000006584 | 0.556798445 | 0.581196581 | 0.336260729 | 0.401709402 | 0.521367521 | 0.205128205 | 0.410256410 | 0.837606838 | 0.401709402 |
| target_S1 | 95 | 95 | S1 | -0.000011408 | 0.267517091 | 0.210526316 | 0.178667048 | 0.021052632 | 0.463157895 | 0.010526316 | 0.147368421 | 0.831578947 | 0.536842105 |
| target_S2 | 122 | 122 | S2 | -0.000001756 | 0.346102357 | 0.336065574 | 0.259344266 | 0.237704918 | 0.401639344 | 0.106557377 | 0.155737705 | 0.745901639 | 0.393442623 |
| target_S3 | 168 | 168 | S3 | -0.000004020 | 0.216502661 | 0.196428571 | 0.179080042 | 0.089285714 | 0.392857143 | 0.035714286 | 0.166666667 | 0.839285714 | 0.053571429 |
| target_S4 | 116 | 116 | S4 | -0.000012157 | 0.434874934 | 0.387931034 | 0.260249949 | 0.077586207 | 0.827586207 | 0.086206897 | 0.456896552 | 0.836206897 | 0.344827586 |

## Prior-Implied E177 Outcome Summary

| prior | mean_delta_vs_e95 | p05_delta_vs_e95 | p50_delta_vs_e95 | p95_delta_vs_e95 | win_rate | e95_edge_or_better_rate | worse_than_e101_rate | worse_than_mixmin_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | -0.000128899 | -0.000160606 | -0.000128824 | -0.000097460 | 1.000000000 | 1.000000000 | 0.000000000 | 0.000000000 |
| subject | -0.000030590 | -0.000057937 | -0.000030438 | -0.000003581 | 0.969900000 | 0.823840000 | 0.007420000 | 0.002360000 |
| nearest_beta | -0.000033700 | -0.000059193 | -0.000033680 | -0.000008545 | 0.986460000 | 0.884880000 | 0.002740000 | 0.000700000 |
| both_distance_beta | -0.000027715 | -0.000053991 | -0.000027595 | -0.000001658 | 0.960620000 | 0.780820000 | 0.009340000 | 0.002640000 |
| edge_endpoint_beta | -0.000033391 | -0.000058829 | -0.000033279 | -0.000008047 | 0.985920000 | 0.879080000 | 0.002480000 | 0.000580000 |
| nearest_hard085 | -0.000074739 | -0.000098191 | -0.000074581 | -0.000051794 | 1.000000000 | 1.000000000 | 0.000000000 | 0.000000000 |
| conflict_flat | -0.000026737 | -0.000053452 | -0.000026602 | -0.000000243 | 0.951740000 | 0.760480000 | 0.012380000 | 0.003720000 |
| focus_mean | -0.000078030 | -0.000107406 | -0.000077920 | -0.000049096 | 1.000000000 | 0.999840000 | 0.000000000 | 0.000000000 |
| flank_mean | -0.000030431 | -0.000056619 | -0.000030360 | -0.000004521 | 0.973240000 | 0.829160000 | 0.005800000 | 0.001380000 |
| visible_mean | -0.000050866 | -0.000078605 | -0.000050829 | -0.000023222 | 0.999080000 | 0.982740000 | 0.000120000 | 0.000020000 |

## Prior-Implied Band Mass

| prior | outcome | world_rate | mean_delta_vs_e95 | p50_delta_vs_e95 |
| --- | --- | --- | --- | --- |
| both_distance_beta | q2_underopen_breakthrough | 0.440080000 | -0.000042002 | -0.000040010 |
| both_distance_beta | clean_win | 0.340740000 | -0.000022976 | -0.000023094 |
| both_distance_beta | micro_win | 0.159220000 | -0.000010071 | -0.000010569 |
| both_distance_beta | tie | 0.034840000 | -0.000000327 | -0.000000505 |
| both_distance_beta | small_loss | 0.015780000 | 0.000005419 | 0.000005205 |
| both_distance_beta | e101_worse_mixmin_safe | 0.006700000 | 0.000011469 | 0.000011284 |
| both_distance_beta | branch_loss | 0.002640000 | 0.000019148 | 0.000018039 |
| conflict_flat | q2_underopen_breakthrough | 0.416780000 | -0.000041871 | -0.000039832 |
| conflict_flat | clean_win | 0.343700000 | -0.000022928 | -0.000023063 |
| conflict_flat | micro_win | 0.168460000 | -0.000009972 | -0.000010371 |
| conflict_flat | tie | 0.038660000 | -0.000000362 | -0.000000532 |
| conflict_flat | small_loss | 0.020020000 | 0.000005574 | 0.000005361 |
| conflict_flat | e101_worse_mixmin_safe | 0.008660000 | 0.000011776 | 0.000011613 |
| conflict_flat | branch_loss | 0.003720000 | 0.000020049 | 0.000018932 |
| edge_endpoint_beta | q2_underopen_breakthrough | 0.585580000 | -0.000043602 | -0.000041636 |
| edge_endpoint_beta | clean_win | 0.293500000 | -0.000023516 | -0.000023890 |
| edge_endpoint_beta | micro_win | 0.097600000 | -0.000010397 | -0.000010927 |
| edge_endpoint_beta | tie | 0.015020000 | -0.000000431 | -0.000000628 |
| edge_endpoint_beta | small_loss | 0.005820000 | 0.000005481 | 0.000005122 |
| edge_endpoint_beta | e101_worse_mixmin_safe | 0.001900000 | 0.000011540 | 0.000011213 |
| edge_endpoint_beta | branch_loss | 0.000580000 | 0.000019131 | 0.000018239 |
| flank_mean | q2_underopen_breakthrough | 0.509360000 | -0.000042900 | -0.000040909 |
| flank_mean | clean_win | 0.319800000 | -0.000023124 | -0.000023334 |
| flank_mean | micro_win | 0.129680000 | -0.000010121 | -0.000010584 |
| flank_mean | tie | 0.024900000 | -0.000000382 | -0.000000531 |
| flank_mean | small_loss | 0.010460000 | 0.000005528 | 0.000005272 |
| flank_mean | e101_worse_mixmin_safe | 0.004420000 | 0.000011682 | 0.000011282 |
| flank_mean | branch_loss | 0.001380000 | 0.000020108 | 0.000018746 |
| focus_mean | q2_underopen_breakthrough | 0.997220000 | -0.000078179 | -0.000077975 |
| focus_mean | clean_win | 0.002620000 | -0.000025375 | -0.000026727 |
| focus_mean | micro_win | 0.000160000 | -0.000010105 | -0.000010466 |
| global | q2_underopen_breakthrough | 1.000000000 | -0.000128899 | -0.000128824 |
| nearest_beta | q2_underopen_breakthrough | 0.592620000 | -0.000043775 | -0.000041846 |
| nearest_beta | clean_win | 0.292260000 | -0.000023428 | -0.000023800 |
| nearest_beta | micro_win | 0.092460000 | -0.000010464 | -0.000010990 |
| nearest_beta | tie | 0.014900000 | -0.000000538 | -0.000000750 |
| nearest_beta | small_loss | 0.005020000 | 0.000005470 | 0.000005370 |
| nearest_beta | e101_worse_mixmin_safe | 0.002040000 | 0.000011672 | 0.000011460 |
| nearest_beta | branch_loss | 0.000700000 | 0.000019813 | 0.000018290 |
| nearest_hard085 | q2_underopen_breakthrough | 0.999360000 | -0.000074770 | -0.000074595 |
| nearest_hard085 | clean_win | 0.000640000 | -0.000026091 | -0.000027433 |
| subject | q2_underopen_breakthrough | 0.510960000 | -0.000043419 | -0.000041177 |
| subject | clean_win | 0.312880000 | -0.000023164 | -0.000023406 |
| subject | micro_win | 0.130020000 | -0.000010151 | -0.000010634 |
| subject | tie | 0.026600000 | -0.000000379 | -0.000000541 |
| subject | small_loss | 0.012120000 | 0.000005571 | 0.000005364 |
| subject | e101_worse_mixmin_safe | 0.005060000 | 0.000011521 | 0.000011316 |
| subject | branch_loss | 0.002360000 | 0.000019933 | 0.000018920 |
| visible_mean | q2_underopen_breakthrough | 0.895120000 | -0.000054255 | -0.000052989 |
| visible_mean | clean_win | 0.087620000 | -0.000024367 | -0.000025086 |
| visible_mean | micro_win | 0.015460000 | -0.000010895 | -0.000011635 |
| visible_mean | tie | 0.001380000 | -0.000000742 | -0.000001239 |
| visible_mean | small_loss | 0.000300000 | 0.000005880 | 0.000006149 |
| visible_mean | e101_worse_mixmin_safe | 0.000100000 | 0.000011763 | 0.000011326 |
| visible_mean | branch_loss | 0.000020000 | 0.000022171 | 0.000022171 |

## Target-Matched Null For Top Critical Sets

| set | n_cells | observed_support_swing_weighted_visible_mean | null_mean | null_p05 | null_p50 | null_p95 | z | p_low | p_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top4_e95_edge | 4 | 0.330699094 | 0.468114375 | 0.222226145 | 0.471250274 | 0.691001898 | -0.949666066 | 0.194666667 | 0.805333333 |
| top16_swing | 16 | 0.266074266 | 0.349756587 | 0.243283948 | 0.346181005 | 0.469107665 | -1.224780309 | 0.105000000 | 0.895000000 |
| top33_expected_flip | 33 | 0.245771136 | 0.335712623 | 0.264934721 | 0.333266695 | 0.413421470 | -1.983811226 | 0.014666667 | 0.985333333 |

## Q2 Damping Contrast: E176 vs E174

| prior | expected_delta | support_swing_weighted | hard_support_rate | flank_conflict_rate | between_train_runs_rate | e72_active_rate |
| --- | --- | --- | --- | --- | --- | --- |
| global | 0.000000983 | 0.495994153 | 0.571428571 | 0.047619048 | 0.714285714 | 0.000000000 |
| subject | 0.000000042 | 0.651912179 | 0.904761905 | 0.047619048 | 0.714285714 | 0.000000000 |
| nearest_beta | -0.000000480 | 0.738363677 | 0.904761905 | 0.047619048 | 0.714285714 | 0.000000000 |
| both_distance_beta | -0.000000323 | 0.712400697 | 0.952380952 | 0.047619048 | 0.714285714 | 0.000000000 |
| edge_endpoint_beta | -0.000000480 | 0.738363677 | 0.904761905 | 0.047619048 | 0.714285714 | 0.000000000 |
| nearest_hard085 | -0.000000778 | 0.787886670 | 0.904761905 | 0.047619048 | 0.714285714 | 0.000000000 |
| conflict_flat | -0.000000300 | 0.708543190 | 0.952380952 | 0.047619048 | 0.714285714 | 0.000000000 |
| focus_mean | 0.000000082 | 0.645264334 | 0.904761905 | 0.047619048 | 0.714285714 | 0.000000000 |
| flank_mean | -0.000000395 | 0.724417810 | 0.904761905 | 0.047619048 | 0.714285714 | 0.000000000 |
| visible_mean | -0.000000191 | 0.690494892 | 0.904761905 | 0.047619048 | 0.714285714 | 0.000000000 |

## Key Read

- Full E176 body visible-mean expected delta: `-0.000050824`.
- Top4 visible-mean swing-weighted support: `0.330699`.
- Visible-mean prior simulated win rate: `0.999080`.
- Focus-mean prior simulated win rate: `1.000000`.
- E176-vs-E174 Q2 damping visible-mean delta: `-0.000000191`.
- E176-vs-E174 Q2 damping focus-mean delta under this flank-prior view: `0.000000082`.

## Interpretation

- If E176 wins public, this audit says the win came from a hidden/public-tail
  realization that was only partially visible from train flanks.
- If E176 ties or small-loses, this audit supports the E178 plateau law: broad
  body signal exists, but the top cells are not locally resolved enough.
- If E176 loses worse than E101, the same-family partial-reopen lane is likely
  public-misaligned; do not rescue it by retuning Q2 amplitude from this audit.

## Decision

No submission is created. Keep
`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the next
single public sensor if spending a slot, and decode it with E177. This audit
does not justify another E176/E174 keep-factor sibling.
