# E173 E172 Public Feedback Decoder

## Question

If `submission_e172_vis_pos_all_keep0p25_d90f4407.csv` is submitted, how should
its public LB update the broad-branch world model without post-hoc threshold
tuning?

Current anchors:

- E95 public LB: `0.5762913298`
- E101 public LB: `0.5763003660`
- mixmin public LB: `0.5763066405`
- E95 edge over mixmin: `-0.0000153107`

## Decoder Bands

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | beats_e95 | beats_e101 | beats_mixmin | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| tail_repair_breakthrough | -inf | 0.576261330 | True | True | True | Promote E172 as a new anchor; decompose rollback keep by target/context before considering larger broad moves. |  |
| clean_win | 0.576261330 | 0.576276019 | True | True | True | Use E172 as broad-branch anchor and test target/context ablations around visible-positive-loss rollback. | conditional:e172_target_context_ablation |
| micro_win | 0.576276019 | 0.576288330 | True | True | True | Promote cautiously. Prefer rollback responsibility analysis before any amplitude increase. |  |
| tie | 0.576288330 | 0.576294330 | False | True | True | Keep E95 as practical frontier. E169 is information-only; raw E166 only tests whether the safety atlas was overconservative. | conditional:E169_or_E166_information_only |
| small_loss | 0.576294330 | 0.576300366 | False | False | True | Do not submit E169 automatically. Compare E172-vs-E169 rollback cells; E154 becomes the cleaner conservative branch if using a slot. | conditional:E154_or_raw_E169_by_question |
| e101_worse_mixmin_safe | 0.576300366 | 0.576306641 | False | False | False | Demote E172/E169 as expected-score files. Prefer E154 if the next public question is conservative repaired-branch structure. | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| branch_loss | 0.576306641 | 0.576341330 | False | False | False | Close E172/E169 same-family expected-score followups and rebuild the broad safety axis. | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| hard_fail | 0.576341330 | inf | False | False | False | Close E172/E169/E166 same-family broad-lane followups and use the failure to rebuild bad-axis geometry. |  |

## Prior-Moment Tail Repair

| candidate | mean_delta_focus_mean | mean_delta_visible_mean | p95_delta_norm_visible_mean | worse_than_e101_norm_visible_mean | mean_delta_subject | mean_delta_flank_mean | delta_mean_delta_visible_mean_vs_e169 | delta_p95_delta_norm_visible_mean_vs_e169 | delta_worse_than_e101_norm_visible_mean_vs_e169 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e169_unrolled_vs_e95 | -0.000053816 | -0.000022620 | 0.000010607 | 0.058544723 | -0.000021099 | 0.000000777 | 0.000000000 | 0.000000000 | 0.000000000 |
| e172_tail_repair_vs_e95 | -0.000076264 | -0.000052853 | -0.000026683 | 0.000050143 | -0.000030978 | -0.000035296 | -0.000030234 | -0.000037290 | -0.058494580 |

## Pairwise Hard-Label Readability

| new | base | moved_cells | moved_rows | targets_moved | expected_delta_focus_mean | cells_to_flip_expected_focus_mean | top1_swing | top5_swing | cells_for_2e6_guard | cells_for_e95_edge | support_prob_swing_weighted_focus_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e172_tail_repair | e95 | 904 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000112695 | 30 | 0.000005832 | 0.000023823 | 1 | 4 | 0.469133282 |
| e169_unrolled | e95 | 904 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000120457 | 32 | 0.000005832 | 0.000023823 | 1 | 4 | 0.459906676 |
| e172_tail_repair | e169_unrolled | 410 | 178 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.000007762 | 3 | 0.000002996 | 0.000013312 | 1 | 6 | 0.559970603 |
| e172_tail_repair | e166_raw | 1256 | 250 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.000219381 | 46 | 0.000007761 | 0.000034557 | 1 | 3 | 0.535948078 |
| e172_tail_repair | e154 | 1027 | 238 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000082858 | 6 | 0.000015957 | 0.000073374 | 1 | 1 | 0.512319158 |
| e172_tail_repair | e101 | 944 | 201 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000159093 | 16 | 0.000014271 | 0.000057948 | 1 | 2 | 0.467588156 |
| e172_tail_repair | mixmin | 1227 | 250 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000257238 | 6 | 0.000049128 | 0.000223837 | 1 | 1 | 0.508050582 |
| e172_tail_repair | e169_high_density | 417 | 179 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.000006385 | 3 | 0.000002996 | 0.000013467 | 1 | 6 | 0.555404900 |

## E172 Group Attribution

| pair | group_kind | group | n_cells | n_rows | expected_delta_focus_mean | abs_expected_share | support_prob_swing_weighted | mean_safe_density | e72_active_rate | context_high_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e172_vs_e169 | context_type | after_train_run | 63 | 33 | 0.000000881 | 0.113472505 | 0.562901754 | 0.324978312 | 0.206349206 | 1.000000000 |
| e172_vs_e169 | context_type | between_train_runs | 347 | 145 | 0.000006881 | 0.886527495 | 0.559591945 | 0.332946977 | 0.250720461 | 1.000000000 |
| e172_vs_e169 | e72_active | True | 100 | 83 | -0.000000393 | 0.050695672 | 0.567689208 | 0.480076020 | 1.000000000 | 1.000000000 |
| e172_vs_e169 | e72_active | False | 310 | 163 | 0.000008155 | 1.050695672 | 0.557009472 | 0.283866557 | 0.000000000 | 1.000000000 |
| e172_vs_e169 | target | Q1 | 46 | 46 | -0.000002791 | 0.359553013 | 0.550796972 | 0.440579278 | 0.478260870 | 1.000000000 |
| e172_vs_e169 | target | Q3 | 51 | 51 | -0.000001985 | 0.255727821 | 0.492011773 | 0.439380928 | 0.450980392 | 1.000000000 |
| e172_vs_e169 | target | S4 | 43 | 43 | 0.000000762 | 0.098129836 | 0.478546261 | 0.448274035 | 0.418604651 | 1.000000000 |
| e172_vs_e169 | target | S3 | 91 | 91 | 0.000001084 | 0.139654413 | 0.667732629 | 0.183196386 | 0.021978022 | 1.000000000 |
| e172_vs_e169 | target | S1 | 33 | 33 | 0.000001905 | 0.245440570 | 0.641711039 | 0.466605575 | 0.454545455 | 1.000000000 |
| e172_vs_e169 | target | S2 | 54 | 54 | 0.000002950 | 0.380140049 | 0.576470452 | 0.464866609 | 0.351851852 | 1.000000000 |
| e172_vs_e169 | target | Q2 | 92 | 92 | 0.000005836 | 0.751915966 | 0.477943430 | 0.183518750 | 0.010869565 | 1.000000000 |
| e172_vs_e169 | target_context | Q1:between_train_runs | 39 | 39 | -0.000002635 | 0.339448319 | 0.554460960 | 0.438609037 | 0.487179487 | 1.000000000 |
| e172_vs_e169 | target_context | Q3:between_train_runs | 41 | 41 | -0.000002009 | 0.258783809 | 0.483339442 | 0.440689903 | 0.487804878 | 1.000000000 |
| e172_vs_e169 | target_context | Q1:after_train_run | 7 | 7 | -0.000000156 | 0.020104694 | 0.512213779 | 0.451556331 | 0.428571429 | 1.000000000 |
| e172_vs_e169 | target_context | S3:after_train_run | 17 | 17 | 0.000000019 | 0.002484752 | 0.653195250 | 0.184815876 | 0.000000000 | 1.000000000 |
| e172_vs_e169 | target_context | Q3:after_train_run | 10 | 10 | 0.000000024 | 0.003055987 | 0.595463655 | 0.434014129 | 0.300000000 | 1.000000000 |
| e172_vs_e169 | target_context | S4:after_train_run | 6 | 6 | 0.000000043 | 0.005502537 | 0.461665607 | 0.439472603 | 0.500000000 | 1.000000000 |
| e172_vs_e169 | target_context | S1:after_train_run | 5 | 5 | 0.000000154 | 0.019785831 | 0.682222222 | 0.454547184 | 0.600000000 | 1.000000000 |
| e172_vs_e169 | target_context | S2:after_train_run | 6 | 6 | 0.000000157 | 0.020258206 | 0.506070032 | 0.450561018 | 0.166666667 | 1.000000000 |
| e172_vs_e169 | target_context | Q2:after_train_run | 12 | 12 | 0.000000640 | 0.082489886 | 0.505396863 | 0.184815876 | 0.000000000 | 1.000000000 |
| e172_vs_e169 | target_context | S4:between_train_runs | 37 | 37 | 0.000000719 | 0.092627299 | 0.481795592 | 0.449701294 | 0.405405405 | 1.000000000 |
| e172_vs_e169 | target_context | S3:between_train_runs | 74 | 74 | 0.000001065 | 0.137169661 | 0.670551676 | 0.182824341 | 0.027027027 | 1.000000000 |
| e172_vs_e169 | target_context | S1:between_train_runs | 28 | 28 | 0.000001751 | 0.225654739 | 0.637432179 | 0.468758860 | 0.428571429 | 1.000000000 |
| e172_vs_e169 | target_context | S2:between_train_runs | 48 | 48 | 0.000002793 | 0.359881842 | 0.582308986 | 0.466654807 | 0.375000000 | 1.000000000 |
| e172_vs_e169 | target_context | Q2:between_train_runs | 80 | 80 | 0.000005196 | 0.669426081 | 0.473652168 | 0.183324181 | 0.012500000 | 1.000000000 |
| e172_vs_e95 | context_type | between_train_runs | 741 | 156 | -0.000090820 | 0.805892003 | 0.466901208 | 0.344889297 | 0.267206478 | 1.000000000 |
| e172_vs_e95 | context_type | after_train_run | 163 | 37 | -0.000021875 | 0.194107997 | 0.478835392 | 0.351883483 | 0.276073620 | 1.000000000 |
| e172_vs_e95 | e72_active | False | 661 | 193 | -0.000080679 | 0.715908117 | 0.469237808 | 0.305594769 | 0.000000000 | 1.000000000 |
| e172_vs_e95 | e72_active | True | 243 | 147 | -0.000032016 | 0.284091883 | 0.468872688 | 0.456468452 | 1.000000000 | 1.000000000 |
| e172_vs_e95 | target | S1 | 95 | 95 | -0.000021933 | 0.194620555 | 0.361775574 | 0.455104170 | 0.536842105 | 1.000000000 |
| e172_vs_e95 | target | S3 | 168 | 168 | -0.000021877 | 0.194123154 | 0.379278269 | 0.178804235 | 0.053571429 | 1.000000000 |
| e172_vs_e95 | target | S4 | 116 | 116 | -0.000018050 | 0.160170377 | 0.489935930 | 0.435114405 | 0.344827586 | 1.000000000 |
| e172_vs_e95 | target | Q1 | 121 | 121 | -0.000017131 | 0.152008009 | 0.480734133 | 0.433137833 | 0.388429752 | 1.000000000 |
| e172_vs_e95 | target | Q2 | 165 | 165 | -0.000013011 | 0.115451880 | 0.540221298 | 0.184092630 | 0.006060606 | 1.000000000 |
| e172_vs_e95 | target | S2 | 122 | 122 | -0.000011004 | 0.097643117 | 0.459352704 | 0.453014613 | 0.393442623 | 1.000000000 |
| e172_vs_e95 | target | Q3 | 117 | 117 | -0.000009690 | 0.085982908 | 0.598280837 | 0.436922678 | 0.401709402 | 1.000000000 |
| e172_vs_e95 | target_context | S3:between_train_runs | 141 | 141 | -0.000019913 | 0.176693794 | 0.383604181 | 0.177653070 | 0.063829787 | 1.000000000 |
| e172_vs_e95 | target_context | S1:between_train_runs | 79 | 79 | -0.000019057 | 0.169099428 | 0.358959913 | 0.456701058 | 0.544303797 | 1.000000000 |
| e172_vs_e95 | target_context | Q1:between_train_runs | 99 | 99 | -0.000013439 | 0.119253363 | 0.476370374 | 0.433220050 | 0.363636364 | 1.000000000 |
| e172_vs_e95 | target_context | S4:between_train_runs | 97 | 97 | -0.000012757 | 0.113197809 | 0.480412932 | 0.436260083 | 0.350515464 | 1.000000000 |
| e172_vs_e95 | target_context | Q2:between_train_runs | 136 | 136 | -0.000010151 | 0.090078642 | 0.547353801 | 0.183938408 | 0.007352941 | 1.000000000 |
| e172_vs_e95 | target_context | Q3:between_train_runs | 98 | 98 | -0.000008132 | 0.072158423 | 0.589845636 | 0.436983080 | 0.408163265 | 1.000000000 |
| e172_vs_e95 | target_context | S2:between_train_runs | 91 | 91 | -0.000007371 | 0.065410545 | 0.459617902 | 0.454818945 | 0.384615385 | 1.000000000 |
| e172_vs_e95 | target_context | S4:after_train_run | 19 | 19 | -0.000005294 | 0.046972568 | 0.527519318 | 0.429265418 | 0.315789474 | 1.000000000 |
| e172_vs_e95 | target_context | Q1:after_train_run | 22 | 22 | -0.000003691 | 0.032754646 | 0.506989034 | 0.432767856 | 0.500000000 | 1.000000000 |
| e172_vs_e95 | target_context | S2:after_train_run | 31 | 31 | -0.000003632 | 0.032232572 | 0.458969399 | 0.447718026 | 0.419354839 | 1.000000000 |
| e172_vs_e95 | target_context | S1:after_train_run | 16 | 16 | -0.000002876 | 0.025521128 | 0.377496406 | 0.447219538 | 0.500000000 | 1.000000000 |
| e172_vs_e95 | target_context | Q2:after_train_run | 29 | 29 | -0.000002859 | 0.025373238 | 0.505142727 | 0.184815876 | 0.000000000 | 1.000000000 |
| e172_vs_e95 | target_context | S3:after_train_run | 27 | 27 | -0.000001964 | 0.017429360 | 0.346228918 | 0.184815876 | 0.000000000 | 1.000000000 |
| e172_vs_e95 | target_context | Q3:after_train_run | 19 | 19 | -0.000001558 | 0.013824485 | 0.645245227 | 0.436611131 | 0.368421053 | 1.000000000 |

## Top E172-vs-E95 Hard-Label Cells

| pair | sub_idx | target | swing | support_label | p_y1_focus_mean | p_y1_subject | p_y1_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e172_tail_repair_vs_e95 | 141 | S1 | 0.000005832 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 196 | Q3 | 0.000004562 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e172_tail_repair_vs_e95 | 190 | Q3 | 0.000004531 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e172_tail_repair_vs_e95 | 194 | Q3 | 0.000004466 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e172_tail_repair_vs_e95 | 67 | S4 | 0.000004432 | 1 | 0.287171717 | 0.151515152 | 0.150000000 |
| e172_tail_repair_vs_e95 | 135 | S1 | 0.000004082 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 143 | S1 | 0.000004017 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 182 | Q3 | 0.000004015 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e172_tail_repair_vs_e95 | 136 | S1 | 0.000003981 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 139 | S3 | 0.000003936 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e172_tail_repair_vs_e95 | 180 | S1 | 0.000003915 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 63 | S1 | 0.000003819 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 70 | S4 | 0.000003816 | 1 | 0.560000000 | 0.560000000 | 0.560000000 |
| e172_tail_repair_vs_e95 | 113 | Q1 | 0.000003792 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e172_tail_repair_vs_e95 | 132 | S1 | 0.000003791 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 5 | Q1 | 0.000003755 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e172_tail_repair_vs_e95 | 138 | S3 | 0.000003626 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e172_tail_repair_vs_e95 | 163 | Q1 | 0.000003596 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e172_tail_repair_vs_e95 | 141 | Q1 | 0.000003521 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e172_tail_repair_vs_e95 | 164 | S1 | 0.000003515 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 0 | Q1 | 0.000003508 | 1 | 0.361526649 | 0.439024390 | 0.150000000 |
| e172_tail_repair_vs_e95 | 79 | S4 | 0.000003436 | 1 | 0.560000000 | 0.560000000 | 0.560000000 |
| e172_tail_repair_vs_e95 | 160 | S1 | 0.000003382 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e95 | 78 | Q2 | 0.000003359 | 0 | 0.562222222 | 0.562222222 | 0.562222222 |
| e172_tail_repair_vs_e95 | 142 | S1 | 0.000003316 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |

## Top E172-vs-E169 Rollback Cells

| pair | sub_idx | target | swing | support_label | p_y1_focus_mean | p_y1_subject | p_y1_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e172_tail_repair_vs_e169_unrolled | 205 | S2 | 0.000002996 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 190 | Q2 | 0.000002703 | 1 | 0.562222222 | 0.562222222 | 0.562222222 |
| e172_tail_repair_vs_e169_unrolled | 204 | S2 | 0.000002589 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 166 | S2 | 0.000002527 | 1 | 0.738465608 | 0.714285714 | 0.850000000 |
| e172_tail_repair_vs_e169_unrolled | 71 | Q2 | 0.000002496 | 1 | 0.562222222 | 0.562222222 | 0.562222222 |
| e172_tail_repair_vs_e169_unrolled | 70 | Q2 | 0.000002399 | 1 | 0.562222222 | 0.562222222 | 0.562222222 |
| e172_tail_repair_vs_e169_unrolled | 157 | S2 | 0.000002393 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 69 | S1 | 0.000002388 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e169_unrolled | 153 | S2 | 0.000002386 | 1 | 0.738465608 | 0.714285714 | 0.850000000 |
| e172_tail_repair_vs_e169_unrolled | 166 | S1 | 0.000002378 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e169_unrolled | 207 | S2 | 0.000002374 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 155 | S2 | 0.000002364 | 1 | 0.738465608 | 0.714285714 | 0.850000000 |
| e172_tail_repair_vs_e169_unrolled | 208 | S2 | 0.000002317 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 213 | S2 | 0.000002297 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 163 | S2 | 0.000002295 | 1 | 0.738465608 | 0.714285714 | 0.850000000 |
| e172_tail_repair_vs_e169_unrolled | 214 | S2 | 0.000002294 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 209 | S2 | 0.000002283 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 152 | S2 | 0.000002282 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 165 | S2 | 0.000002233 | 1 | 0.738465608 | 0.714285714 | 0.850000000 |
| e172_tail_repair_vs_e169_unrolled | 115 | S2 | 0.000002205 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 37 | Q3 | 0.000002191 | 0 | 0.493055556 | 0.729166667 | 0.150000000 |
| e172_tail_repair_vs_e169_unrolled | 159 | S2 | 0.000002178 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 206 | S2 | 0.000002158 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e172_tail_repair_vs_e169_unrolled | 157 | S1 | 0.000002132 | 1 | 0.682222222 | 0.682222222 | 0.682222222 |
| e172_tail_repair_vs_e169_unrolled | 248 | S2 | 0.000002117 | 1 | 0.388249158 | 0.363636364 | 0.150000000 |

## Observed Score Decision

_No observed E172 public score supplied._

## Decision

E173 creates no submission. The pre-feedback first broad expected-score file is
`analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv`.

- A win below E95 validates visible-positive-loss rollback as the missing broad
  branch constraint.
- A tie or small loss keeps E95 practical and makes raw E169 information-only.
- A worse-than-E101 result demotes visible-tail repair and shifts priority to
  E154 or a new broad safety-axis search.
- A worse-than-mixmin result blocks E172/E169/E166 same-family broad followups.
