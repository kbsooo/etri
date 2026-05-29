# E163 Candidate Edge Breadth Audit

## Question

Was E162's one-cell fragility only an E154 sibling artifact, or is the current post-E95 plateau broadly hidden-label-resolution limited?

## Summary

- known public transitions audited: `7`.
- known transitions whose whole actual public delta can be moved by one top hard-label cell: `3/7`.
- known transitions whose whole actual public delta can be moved by five top hard-label cells: `5/7`.
- live post-E95 candidates with one-cell `2e-6` readability fragility: `7/7`.

## Known Public Transitions

| new | base | actual_public_delta | actual_delta_vs_e95_edge_abs_ratio | moved_cells | expected_delta_focus_mean | top1_swing | top5_swing | cells_for_actual_abs_delta | top1_over_actual_abs_delta | top5_over_actual_abs_delta | actual_focus_sign_match | targets_moved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin | a2c8 | -0.001132680 | 73.979667814 | 1256 | -0.000198388 | 0.000046919 | 0.000234596 | 25.000000000 | 0.041423105 | 0.207115523 | True | Q1,Q2,Q3,S1,S2,S3,S4 |
| e72 | e95 | 0.000116447 | 7.605622212 | 1047 | -0.000869985 | 0.000023431 | 0.000115937 | 6.000000000 | 0.201214368 | 0.995613865 | False | Q1,Q2,Q3,S1,S2,S3,S4 |
| e72 | mixmin | 0.000101137 | 6.605622212 | 893 | -0.001014528 | 0.000028770 | 0.000141459 | 4.000000000 | 0.284469844 | 1.398694945 | False | Q1,Q2,Q3,S1,S2,S3,S4 |
| raw05 | a2c8 | 0.000086986 | 5.681399283 | 1750 | 0.000935252 | 0.000059132 | 0.000201177 | 2.000000000 | 0.679786701 | 2.312745814 | True | Q1,Q2,Q3,S1,S2,S3,S4 |
| e95 | mixmin | -0.000015311 | 1.000000000 | 550 | -0.000144543 | 0.000046477 | 0.000221185 | 1.000000000 | 3.035574808 | 14.446455307 | True | Q2,S1,S2,S3 |
| e101 | e95 | 0.000009036 | 0.590188561 | 50 | 0.000046398 | 0.000011619 | 0.000055296 | 1.000000000 | 1.285849561 | 6.119423631 | True | Q2,S3 |
| e101 | mixmin | -0.000006275 | 0.409811439 | 550 | -0.000098145 | 0.000034858 | 0.000165889 | 1.000000000 | 5.555435717 | 26.438601872 | True | Q2,S1,S2,S3 |

## Live Post-E95 Candidates Versus E95

| new | base | moved_cells | moved_rows | expected_delta_focus_mean | support_prob_swing_weighted_focus_mean | top1_swing | top5_swing | cells_for_2e6_guard | cells_for_e95_edge | cells_to_flip_expected_focus_mean | targets_moved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e156 | e95 | 246 | 125 | -0.000031056 | 0.474104932 | 0.000012011 | 0.000059020 | 1 | 2 | 3 | Q1,Q3,S2,S3,S4 |
| e157 | e95 | 285 | 139 | -0.000030962 | 0.473851008 | 0.000012406 | 0.000060206 | 1 | 2 | 3 | Q1,Q3,S2,S3,S4 |
| e144 | e95 | 185 | 108 | -0.000030476 | 0.473846848 | 0.000011429 | 0.000057143 | 1 | 2 | 3 | Q1,Q3,S2,S3,S4 |
| e155 | e95 | 294 | 139 | -0.000030342 | 0.473566508 | 0.000012406 | 0.000060188 | 1 | 2 | 3 | Q1,Q3,S2,S3,S4 |
| e154 | e95 | 294 | 139 | -0.000029838 | 0.472782386 | 0.000015340 | 0.000070460 | 1 | 1 | 3 | Q1,Q3,S2,S3,S4 |
| e142 | e95 | 185 | 108 | -0.000027544 | 0.467177807 | 0.000011429 | 0.000057143 | 1 | 2 | 3 | Q1,Q3,S2,S3,S4 |
| e143 | e95 | 164 | 106 | -0.000025185 | 0.473219778 | 0.000011429 | 0.000057143 | 1 | 2 | 3 | Q1,Q3,S2,S3,S4 |

## Repaired Sibling Controls

| new | base | moved_cells | expected_delta_focus_mean | top1_swing | top5_swing | cells_for_2e6_guard | cells_to_flip_expected_focus_mean | targets_moved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e154 | e144 | 294 | 0.000000638 | 0.000014420 | 0.000040971 | 1 | 1 | Q1,Q3,S2,S3,S4 |
| e154 | e155 | 294 | 0.000000505 | 0.000010815 | 0.000030729 | 1 | 1 | Q1,Q3,S2,S3,S4 |
| e156 | e155 | 190 | -0.000000713 | 0.000003605 | 0.000010448 | 1 | 1 | Q3,S2,S3 |
| e157 | e155 | 129 | -0.000000619 | 0.000002185 | 0.000006176 | 1 | 1 | S2,S3,S4 |

## Top Swing Cells

| pair_group | new | base | swing_rank | sub_idx | target | swing | delta_y1 | delta_y0 | support_label | p_y1_focus_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| known_transition | e101 | e95 | 1 | 133 | S3 | 0.000011619 | -0.000000653 | 0.000010966 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 2 | 145 | S3 | 0.000011269 | -0.000000495 | 0.000010773 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 3 | 141 | S3 | 0.000011056 | -0.000000473 | 0.000010583 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 4 | 39 | S3 | 0.000010789 | -0.000001029 | 0.000009760 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 5 | 215 | S3 | 0.000010563 | -0.000003057 | 0.000007506 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 6 | 146 | S3 | 0.000010561 | -0.000000490 | 0.000010071 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 7 | 235 | S3 | 0.000010517 | -0.000005641 | 0.000004876 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 8 | 120 | S3 | 0.000010184 | 0.000008915 | -0.000001269 | 0 | 0.662222222 |
| known_transition | e101 | e95 | 9 | 241 | S3 | 0.000009842 | 0.000005061 | -0.000004782 | 0 | 0.432356902 |
| known_transition | e101 | e95 | 10 | 8 | S3 | 0.000009340 | -0.000001335 | 0.000008004 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 11 | 57 | S3 | 0.000009135 | -0.000000907 | 0.000008229 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 12 | 12 | S3 | 0.000009110 | -0.000001212 | 0.000007898 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 13 | 129 | S3 | 0.000008876 | -0.000000549 | 0.000008328 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 14 | 86 | S3 | 0.000008811 | 0.000004313 | -0.000004498 | 0 | 0.662222222 |
| known_transition | e101 | e95 | 15 | 144 | S3 | 0.000008632 | -0.000000549 | 0.000008083 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 16 | 180 | S3 | 0.000008531 | -0.000001776 | 0.000006756 | 1 | 0.769380197 |
| known_transition | e101 | e95 | 17 | 25 | S3 | 0.000008389 | 0.000001530 | -0.000006859 | 0 | 0.662222222 |
| known_transition | e101 | e95 | 18 | 115 | S3 | 0.000008122 | 0.000007255 | -0.000000868 | 0 | 0.662222222 |
| known_transition | e101 | e95 | 19 | 47 | S3 | 0.000007950 | -0.000000750 | 0.000007201 | 1 | 0.662222222 |
| known_transition | e101 | e95 | 20 | 22 | S3 | 0.000007853 | 0.000001493 | -0.000006360 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 1 | 133 | S3 | 0.000034858 | 0.000001886 | -0.000032972 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 2 | 145 | S3 | 0.000033806 | 0.000001431 | -0.000032374 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 3 | 141 | S3 | 0.000033169 | 0.000001368 | -0.000031801 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 4 | 39 | S3 | 0.000032367 | 0.000002984 | -0.000029383 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 5 | 215 | S3 | 0.000031690 | 0.000008932 | -0.000022758 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 6 | 146 | S3 | 0.000031684 | 0.000001420 | -0.000030265 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 7 | 235 | S3 | 0.000031551 | 0.000016634 | -0.000014916 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 8 | 120 | S3 | 0.000030551 | -0.000026861 | 0.000003691 | 1 | 0.662222222 |
| known_transition | e101 | mixmin | 9 | 241 | S3 | 0.000029527 | -0.000015436 | 0.000014091 | 1 | 0.432356902 |
| known_transition | e101 | mixmin | 10 | 8 | S3 | 0.000028019 | 0.000003895 | -0.000024124 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 11 | 57 | S3 | 0.000027406 | 0.000002644 | -0.000024763 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 12 | 12 | S3 | 0.000027329 | 0.000003537 | -0.000023792 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 13 | 129 | S3 | 0.000026629 | 0.000001599 | -0.000025030 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 14 | 86 | S3 | 0.000026433 | -0.000013144 | 0.000013289 | 1 | 0.662222222 |
| known_transition | e101 | mixmin | 15 | 144 | S3 | 0.000025897 | 0.000001601 | -0.000024296 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 16 | 180 | S3 | 0.000025594 | 0.000005203 | -0.000020391 | 0 | 0.769380197 |
| known_transition | e101 | mixmin | 17 | 25 | S3 | 0.000025168 | -0.000004701 | 0.000020467 | 1 | 0.662222222 |
| known_transition | e101 | mixmin | 18 | 115 | S3 | 0.000024367 | -0.000021829 | 0.000002538 | 1 | 0.662222222 |
| known_transition | e101 | mixmin | 19 | 47 | S3 | 0.000023851 | 0.000002193 | -0.000021658 | 0 | 0.662222222 |
| known_transition | e101 | mixmin | 20 | 22 | S3 | 0.000023560 | -0.000004580 | 0.000018981 | 1 | 0.662222222 |
| known_transition | e72 | e95 | 1 | 191 | S2 | 0.000023431 | 0.000009127 | -0.000014304 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 2 | 242 | Q2 | 0.000023381 | -0.000014900 | 0.000008481 | 1 | 0.562222222 |
| known_transition | e72 | e95 | 3 | 239 | S2 | 0.000023107 | -0.000015322 | 0.000007784 | 1 | 0.388249158 |
| known_transition | e72 | e95 | 4 | 139 | S1 | 0.000023023 | 0.000001124 | -0.000021900 | 0 | 0.682222222 |
| known_transition | e72 | e95 | 5 | 141 | S2 | 0.000022995 | 0.000001358 | -0.000021638 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 6 | 143 | S2 | 0.000022916 | 0.000001220 | -0.000021696 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 7 | 130 | S2 | 0.000022884 | 0.000001303 | -0.000021581 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 8 | 151 | S2 | 0.000022863 | 0.000001254 | -0.000021609 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 9 | 34 | S1 | 0.000022830 | 0.000002324 | -0.000020506 | 0 | 0.682222222 |
| known_transition | e72 | e95 | 10 | 142 | S2 | 0.000022810 | 0.000001389 | -0.000021421 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 11 | 136 | S1 | 0.000022794 | 0.000000727 | -0.000022067 | 0 | 0.682222222 |
| known_transition | e72 | e95 | 12 | 227 | S2 | 0.000022789 | 0.000004051 | -0.000018739 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 13 | 74 | S2 | 0.000022777 | -0.000010723 | 0.000012054 | 1 | 0.651111111 |
| known_transition | e72 | e95 | 14 | 144 | S2 | 0.000022743 | 0.000001315 | -0.000021429 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 15 | 15 | S2 | 0.000022733 | -0.000009842 | 0.000012891 | 1 | 0.651111111 |
| known_transition | e72 | e95 | 16 | 221 | S2 | 0.000022712 | 0.000004449 | -0.000018264 | 0 | 0.651111111 |
| known_transition | e72 | e95 | 17 | 231 | S1 | 0.000022700 | -0.000013231 | 0.000009469 | 1 | 0.682222222 |
| known_transition | e72 | e95 | 18 | 14 | S2 | 0.000022689 | -0.000009428 | 0.000013260 | 1 | 0.651111111 |
| known_transition | e72 | e95 | 19 | 30 | S1 | 0.000022684 | 0.000002426 | -0.000020258 | 0 | 0.682222222 |
| known_transition | e72 | e95 | 20 | 18 | S2 | 0.000022657 | -0.000008662 | 0.000013995 | 1 | 0.651111111 |
| known_transition | e72 | mixmin | 1 | 39 | S3 | 0.000028770 | 0.000002645 | -0.000026125 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 2 | 133 | S3 | 0.000028670 | 0.000001543 | -0.000027127 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 3 | 215 | S3 | 0.000028169 | 0.000007922 | -0.000020247 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 4 | 235 | S3 | 0.000028045 | 0.000014765 | -0.000013280 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 5 | 145 | S3 | 0.000027805 | 0.000001171 | -0.000026633 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 6 | 141 | S3 | 0.000027281 | 0.000001120 | -0.000026161 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 7 | 120 | S3 | 0.000027157 | -0.000023885 | 0.000003272 | 1 | 0.662222222 |
| known_transition | e72 | mixmin | 8 | 241 | S3 | 0.000026246 | -0.000013740 | 0.000012506 | 1 | 0.432356902 |
| known_transition | e72 | mixmin | 9 | 146 | S3 | 0.000026060 | 0.000001162 | -0.000024898 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 10 | 8 | S3 | 0.000024906 | 0.000003454 | -0.000021452 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 11 | 57 | S3 | 0.000024361 | 0.000002344 | -0.000022017 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 12 | 12 | S3 | 0.000024292 | 0.000003137 | -0.000021156 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 13 | 86 | S3 | 0.000023496 | -0.000011699 | 0.000011797 | 1 | 0.662222222 |
| known_transition | e72 | mixmin | 14 | 242 | Q2 | 0.000023381 | -0.000014900 | 0.000008481 | 1 | 0.562222222 |
| known_transition | e72 | mixmin | 15 | 180 | S3 | 0.000022750 | 0.000004615 | -0.000018135 | 0 | 0.769380197 |
| known_transition | e72 | mixmin | 16 | 25 | S3 | 0.000022371 | -0.000004187 | 0.000018185 | 1 | 0.662222222 |
| known_transition | e72 | mixmin | 17 | 129 | S3 | 0.000021902 | 0.000001310 | -0.000020592 | 0 | 0.662222222 |
| known_transition | e72 | mixmin | 18 | 115 | S3 | 0.000021660 | -0.000019408 | 0.000002251 | 1 | 0.662222222 |
| known_transition | e72 | mixmin | 19 | 173 | Q2 | 0.000021375 | -0.000013381 | 0.000007993 | 1 | 0.562222222 |
| known_transition | e72 | mixmin | 20 | 144 | S3 | 0.000021300 | 0.000001312 | -0.000019988 | 0 | 0.662222222 |

## Decision

E162 is not just an E154-local curiosity. The mixmin breakthrough is broad, but the post-mixmin/E95 frontier refinements live at a scale where one or a few hidden row-target labels can dominate the measured public delta. This supports the plateau diagnosis: candidate selection is hard-label-resolution and calibration-tail limited, not model-capacity limited.

No new submission is created by E163. The next public sensor remains `analysis_outputs/submission_e154_s3repair_9f2e2e73.csv`, because it asks the repaired all-four branch question. E155/E157/E156 remain post-feedback instruments.
