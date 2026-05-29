# E147 E144/E95 Prior-World Audit

## Question

E146 showed E144's fine S3 tail is prior-supported versus E143. E147 asks the larger question: do public-free global/subject/flank priors support E144 as a whole versus the current E95 frontier?

## Cell Anatomy

- E144-vs-E95 moved cells: `185`
- rows touched: `108`
- subjects touched: `9`
- edge-like cells: `62`
- flank-conflict cells: `26`
- total flip benefit: `3.292000000000`

Target counts:

| target | cells | rows | flip_benefit |
| --- | --- | --- | --- |
| Q3 | 56 | 56 | 1.120000 |
| S3 | 47 | 47 | 0.532000 |
| Q1 | 38 | 38 | 0.760000 |
| S2 | 23 | 23 | 0.460000 |
| S4 | 21 | 21 | 0.420000 |

Component counts:

| component | cells | rows | flip_benefit |
| --- | --- | --- | --- |
| e144_fine_tail_delta | 24 | 24 | 0.072000 |
| inherited_e143_body | 161 | 106 | 3.220000 |

## Prior Summary

| prior | expected_delta_e144_minus_e95 | expected_delta_total | expected_lb_if_full_test_prior | prefers_e144 | hard_support_cells | hard_support_flip_share | mean_support_probability | top20_support_rate | fine_tail_hard_support_rate | body_hard_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | -0.000049865515 | -0.087264651300 | 0.576241464285 | True | 71 | 0.384872417983 | 0.481429429429 | 0.400000000000 | 0.375000000000 | 0.385093167702 |
| prev_beta | -0.000021732090 | -0.038031157975 | 0.576269597710 | True | 78 | 0.437727825030 | 0.464609514851 | 0.450000000000 | 0.291666666667 | 0.440993788820 |
| nearest_hard085 | -0.000021673769 | -0.037929095744 | 0.576269656031 | True | 81 | 0.455953827461 | 0.456486486486 | 0.550000000000 | 0.291666666667 | 0.459627329193 |
| conflict_flat | -0.000020485736 | -0.035850037399 | 0.576270844064 | True | 90 | 0.510631834751 | 0.462716039668 | 0.500000000000 | 0.291666666667 | 0.515527950311 |
| subject | -0.000019888579 | -0.034805013217 | 0.576271441221 | True | 92 | 0.507290400972 | 0.463617505065 | 0.500000000000 | 0.416666666667 | 0.509316770186 |
| both_distance_beta | -0.000015719528 | -0.027509174165 | 0.576275610272 | True | 76 | 0.425577156744 | 0.460461752308 | 0.500000000000 | 0.291666666667 | 0.428571428571 |
| next_beta | -0.000013299040 | -0.023273320403 | 0.576278030760 | True | 75 | 0.419501822600 | 0.459135398765 | 0.550000000000 | 0.291666666667 | 0.422360248447 |
| both_equal_beta | -0.000012853752 | -0.022494066732 | 0.576278476048 | True | 88 | 0.498481166464 | 0.454151013681 | 0.550000000000 | 0.291666666667 | 0.503105590062 |
| nearest_beta | -0.000012197928 | -0.021346374059 | 0.576279131872 | True | 85 | 0.480255164034 | 0.455024282656 | 0.550000000000 | 0.291666666667 | 0.484472049689 |
| edge_endpoint_beta | -0.000012197928 | -0.021346374059 | 0.576279131872 | True | 85 | 0.480255164034 | 0.455024282656 | 0.550000000000 | 0.291666666667 | 0.484472049689 |

## Simulation Summary

| prior | sim_mean_delta_e144_minus_e95 | sim_p05 | sim_p50 | sim_p95 | p_e144_beats_e95 | sim_expected_lb_if_full_test_prior | support_cells_mean | support_flip_share_mean | top20_support_rate | fine_tail_support_rate | body_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global | -0.000049975255 | -0.000167102340 | -0.000049388055 | 0.000066611945 | 0.762700000000 | 0.576241354545 | 89.072715000000 | 0.484212515188 | 0.485397250000 | 0.459379166667 | 0.484767795031 |
| prev_beta | -0.000021718743 | -0.000127673769 | -0.000021959483 | 0.000084326231 | 0.639670000000 | 0.576269611057 | 85.956000000000 | 0.469191587181 | 0.449100250000 | 0.427797291667 | 0.470117173913 |
| nearest_hard085 | -0.000021564938 | -0.000106530912 | -0.000021388055 | 0.000063183374 | 0.663765000000 | 0.576269764862 | 84.443975000000 | 0.469109825334 | 0.534574750000 | 0.354338125000 | 0.471676149068 |
| conflict_flat | -0.000020529400 | -0.000127673769 | -0.000021388055 | 0.000087754802 | 0.629900000000 | 0.576270800400 | 85.601735000000 | 0.468559342345 | 0.459394000000 | 0.415532708333 | 0.469745031056 |
| subject | -0.000019912478 | -0.000127673769 | -0.000020245198 | 0.000087754802 | 0.627440000000 | 0.576271417322 | 85.769175000000 | 0.468231391252 | 0.444920750000 | 0.426386666667 | 0.469167049689 |
| both_distance_beta | -0.000015852518 | -0.000122530912 | -0.000015102340 | 0.000089469088 | 0.604045000000 | 0.576275477282 | 85.195555000000 | 0.466073150061 | 0.459378750000 | 0.415682083333 | 0.467199906832 |
| next_beta | -0.000013194480 | -0.000121388055 | -0.000013388055 | 0.000092897660 | 0.585960000000 | 0.576278135320 | 84.926550000000 | 0.464660159478 | 0.455301250000 | 0.413896458333 | 0.465795248447 |
| both_equal_beta | -0.000012891949 | -0.000112816626 | -0.000011673769 | 0.000087754802 | 0.589005000000 | 0.576278437851 | 84.021340000000 | 0.464499336270 | 0.492473500000 | 0.370821041667 | 0.466594006211 |
| edge_endpoint_beta | -0.000012190212 | -0.000112816626 | -0.000011673769 | 0.000089469088 | 0.585215000000 | 0.576279139588 | 84.179850000000 | 0.464126298603 | 0.480197250000 | 0.381601041667 | 0.465971583851 |
| nearest_beta | -0.000011986932 | -0.000114530912 | -0.000011673769 | 0.000089469088 | 0.583850000000 | 0.576279342868 | 84.154345000000 | 0.464018236634 | 0.479621250000 | 0.381222708333 | 0.465869565217 |

## Nearest-Hard Target Contributions

| prior | target | cells | expected_delta_per_all | expected_delta_total | prefers_e144 | hard_support_cells | mean_support_probability | flip_benefit_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nearest_hard085 | Q1 | 38 | -0.000035329747 | -0.061827057775 | True | 22 | 0.555263157895 | 0.760000000000 |
| nearest_hard085 | S4 | 21 | -0.000022307601 | -0.039038302178 | True | 9 | 0.450000000000 | 0.420000000000 |
| nearest_hard085 | S2 | 23 | -0.000007249103 | -0.012685930016 | True | 15 | 0.606521739130 | 0.460000000000 |
| nearest_hard085 | Q3 | 56 | 0.000008466410 | 0.014816217365 | False | 24 | 0.450000000000 | 1.120000000000 |
| nearest_hard085 | S3 | 47 | 0.000034746272 | 0.060805976860 | False | 11 | 0.313829787234 | 0.532000000000 |

## Subject-Prior Target Contributions

| prior | target | cells | expected_delta_per_all | expected_delta_total | prefers_e144 | hard_support_cells | mean_support_probability | flip_benefit_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject | Q3 | 56 | -0.000009800661 | -0.017151156923 | True | 27 | 0.478542298471 | 1.120000000000 |
| subject | Q1 | 38 | -0.000007490336 | -0.013108088591 | True | 24 | 0.491159251074 | 0.760000000000 |
| subject | S4 | 21 | -0.000003744831 | -0.006553453693 | True | 6 | 0.372655122655 | 0.420000000000 |
| subject | S2 | 23 | -0.000000238590 | -0.000417531748 | True | 15 | 0.579851308112 | 0.460000000000 |
| subject | S3 | 47 | 0.000001385839 | 0.002425217738 | False | 20 | 0.407329372755 | 0.532000000000 |

## Nearest-Hard Component Contributions

| prior | component | cells | expected_delta_per_all | expected_delta_total | prefers_e144 | hard_support_cells | mean_support_probability | flip_benefit_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nearest_hard085 | inherited_e143_body | 161 | -0.000024556352 | -0.042973616756 | True | 74 | 0.471739130435 | 3.220000000000 |
| nearest_hard085 | e144_fine_tail_delta | 24 | 0.000002882583 | 0.005044521011 | False | 7 | 0.354166666667 | 0.072000000000 |

## Highest Impact Cells

| sub_idx | subject_id | lifelog_date | target | component | p_e95 | p_e144 | support_y_for_e144 | flip_benefit | pos_bin | flank_conflict | support_probability_subject | support_probability_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 59 | id03 | 2024-08-16 00:00:00 | Q1 | inherited_e143_body | 0.913103 | 0.911503 | 0 | 0.020000 | left_edge | False | 0.151515 | 0.150000 |
| 47 | id02 | 2024-10-03 00:00:00 | S2 | inherited_e143_body | 0.923882 | 0.925276 | 1 | 0.020000 | interior | False | 0.916667 | 0.850000 |
| 66 | id03 | 2024-08-24 00:00:00 | Q1 | inherited_e143_body | 0.944659 | 0.943604 | 0 | 0.020000 | interior | False | 0.151515 | 0.150000 |
| 55 | id02 | 2024-10-12 00:00:00 | Q3 | inherited_e143_body | 0.770802 | 0.767250 | 0 | 0.020000 | interior | False | 0.270833 | 0.150000 |
| 57 | id02 | 2024-10-14 00:00:00 | S2 | inherited_e143_body | 0.939706 | 0.938563 | 0 | 0.020000 | near_edge | False | 0.083333 | 0.150000 |
| 55 | id02 | 2024-10-12 00:00:00 | S2 | inherited_e143_body | 0.902213 | 0.903964 | 1 | 0.020000 | interior | False | 0.916667 | 0.850000 |
| 69 | id03 | 2024-08-28 00:00:00 | Q1 | inherited_e143_body | 0.902535 | 0.900762 | 0 | 0.020000 | right_edge | False | 0.151515 | 0.150000 |
| 248 | id10 | 2024-09-25 00:00:00 | S2 | inherited_e143_body | 0.305673 | 0.301445 | 0 | 0.020000 | near_edge | False | 0.636364 | 0.850000 |
| 168 | id07 | 2024-08-15 00:00:00 | Q1 | inherited_e143_body | 0.731562 | 0.735472 | 1 | 0.020000 | near_edge | False | 0.510204 | 0.150000 |
| 241 | id10 | 2024-09-17 00:00:00 | Q1 | inherited_e143_body | 0.596051 | 0.600857 | 1 | 0.020000 | interior | False | 0.484848 | 0.850000 |
| 160 | id07 | 2024-07-21 00:00:00 | S4 | inherited_e143_body | 0.572630 | 0.577517 | 1 | 0.020000 | interior | False | 0.469388 | 0.850000 |
| 117 | id05 | 2024-10-16 00:00:00 | Q3 | inherited_e143_body | 0.718765 | 0.714705 | 0 | 0.020000 | near_edge | False | 0.318182 | 0.850000 |
| 225 | id09 | 2024-09-19 00:00:00 | Q1 | inherited_e143_body | 0.798525 | 0.801724 | 1 | 0.020000 | interior | False | 0.512195 | 0.850000 |
| 214 | id09 | 2024-08-20 00:00:00 | Q3 | inherited_e143_body | 0.429866 | 0.424971 | 0 | 0.020000 | right_edge | False | 0.560976 | 0.850000 |
| 61 | id03 | 2024-08-18 00:00:00 | S4 | inherited_e143_body | 0.100978 | 0.102808 | 1 | 0.020000 | interior | False | 0.151515 | 0.150000 |

## Interpretation

- Priors preferring E144 over E95: `10/10`.
- Best expected prior: `global` with delta `-0.000049865515`.
- Worst expected prior: `edge_endpoint_beta` with delta `-0.000012197928`.
- Read: visible priors broadly support E144 over E95.

## Decision

No submission is created. E144 remains the next public sensor. This audit defines what that sensor is betting on: not just the E146 fine-tail delta, but the full inherited residual body versus E95. If public feedback disagrees with the visible-prior direction, the next analysis should identify the target/component whose prior contribution failed rather than tune the whole E142/E143/E144 family.
