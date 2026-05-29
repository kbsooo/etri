# E175 E174 Public Feedback Decoder

## Question

If `submission_e174_ro_fc_top75_to1p0_95638e73.csv` is submitted, how should
its public LB update the broad-branch world model without post-hoc keep-factor
tuning?

Current anchors:

- E95 public LB: `0.5762913298`
- E101 public LB: `0.5763003660`
- mixmin public LB: `0.5763066405`
- E95 edge over mixmin: `-0.0000153107`

## Decoder Bands

| outcome | public_lb_lo_exclusive | public_lb_hi_inclusive | beats_e95 | beats_e101 | beats_mixmin | next_action | candidate_to_test |
| --- | --- | --- | --- | --- | --- | --- | --- |
| partial_reopen_breakthrough | -inf | 0.576261330 | True | True | True | Promote E174 as a new broad anchor; decompose the top-75 reopened cells by target/context before any larger reopening. | conditional:e174_reopen_decomposition |
| clean_win | 0.576261330 | 0.576276019 | True | True | True | Use E174 as the broad expected-score anchor. Next experiment should localize whether S3, Q2, or S2 carried the reopening gain. | conditional:e174_target_context_ablation |
| micro_win | 0.576276019 | 0.576288330 | True | True | True | Promote cautiously. Prefer a responsibility audit over same-family keep-factor tuning. | conditional:e174_responsibility_audit |
| tie | 0.576288330 | 0.576294330 | False | True | True | Keep E95 practical. If spending another broad slot, E172 is the cleaner contrast because it tests whether reopening was the error. | analysis_outputs/submission_e172_vis_pos_all_keep0p25_d90f4407.csv |
| small_loss | 0.576294330 | 0.576300366 | False | False | True | Use E172 as the only same-family contrast if the next question remains broad tail repair. Otherwise shift to E154/conservative branch. | conditional:E172_or_E154_by_question |
| e101_worse_mixmin_safe | 0.576300366 | 0.576306641 | False | False | False | Demote E174. E172 is information-only unless we explicitly need to test whether full damping saves the broad body; otherwise prefer E154. | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| branch_loss | 0.576306641 | 0.576341330 | False | False | False | Close E174 same-family reopening and make E172 only a low-risk contrast, not an automatic next file. | analysis_outputs/submission_e154_s3repair_9f2e2e73.csv |
| hard_fail | 0.576341330 | inf | False | False | False | Close E174/E172/E169 same-family broad expected-score followups and rebuild the bad-axis geometry. |  |

## Prior-Moment Reopening Tradeoff

| candidate | mean_delta_focus_mean | mean_delta_visible_mean | p95_delta_norm_visible_mean | worse_than_e101_norm_visible_mean | mean_delta_subject | mean_delta_flank_mean | delta_mean_delta_focus_mean_vs_e172 | delta_mean_delta_visible_mean_vs_e172 | delta_p95_delta_norm_visible_mean_vs_e172 | delta_worse_than_e101_norm_visible_mean_vs_e172 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e169_unrolled_vs_e95 | -0.000053816 | -0.000022620 | 0.000010607 | 0.058544723 | -0.000021099 | 0.000000777 | 0.000022448 | 0.000030234 | 0.000037290 | 0.058494580 |
| e172_tail_repair_vs_e95 | -0.000076264 | -0.000052853 | -0.000026683 | 0.000050143 | -0.000030978 | -0.000035296 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| e174_partial_reopen_vs_e95 | -0.000078124 | -0.000050633 | -0.000022709 | 0.000220012 | -0.000030479 | -0.000030015 | -0.000001861 | 0.000002220 | 0.000003974 | 0.000169869 |

## Pairwise Hard-Label Readability

| new | base | moved_cells | moved_rows | targets_moved | expected_delta_focus_mean | cells_to_flip_expected_focus_mean | top1_swing | top5_swing | cells_for_2e6_guard | cells_for_e95_edge | support_prob_swing_weighted_focus_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e174_partial_reopen | e95 | 904 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000124367 | 33 | 0.000005832 | 0.000023823 | 1 | 4 | 0.462104938 |
| e172_tail_repair | e95 | 904 | 193 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000112695 | 30 | 0.000005832 | 0.000023823 | 1 | 4 | 0.469133282 |
| e174_partial_reopen | e172_tail_repair | 75 | 65 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000011672 | 5 | 0.000002996 | 0.000012859 | 1 | 7 | 0.396719811 |
| e174_partial_reopen | e169_unrolled | 335 | 166 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000003910 | 2 | 0.000002703 | 0.000012397 | 1 | 7 | 0.546918792 |
| e174_partial_reopen | e166_raw | 1181 | 250 | Q1,Q2,Q3,S1,S2,S3,S4 | 0.000207710 | 43 | 0.000007761 | 0.000034557 | 1 | 3 | 0.532119683 |
| e174_partial_reopen | e154 | 1027 | 238 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000094529 | 7 | 0.000015957 | 0.000074980 | 1 | 1 | 0.508876615 |
| e174_partial_reopen | e101 | 944 | 201 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000170765 | 17 | 0.000014271 | 0.000057948 | 1 | 2 | 0.462484580 |
| e174_partial_reopen | mixmin | 1227 | 250 | Q1,Q2,Q3,S1,S2,S3,S4 | -0.000268910 | 7 | 0.000049128 | 0.000223837 | 1 | 1 | 0.506614395 |

## E174 Group Attribution

| pair | group_kind | group | n_cells | n_rows | expected_delta_focus_mean | abs_expected_share | support_prob_swing_weighted | mean_safe_density | e72_active_rate | context_high_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e174_vs_e169 | context_type | between_train_runs | 289 | 139 | -0.000002623 | 0.670901369 | 0.547127194 | 0.345385035 | 0.283737024 | 1.000000000 |
| e174_vs_e169 | context_type | after_train_run | 46 | 27 | -0.000001287 | 0.329098631 | 0.544905433 | 0.332799188 | 0.260869565 | 1.000000000 |
| e174_vs_e169 | e72_active | False | 241 | 144 | -0.000002184 | 0.558576226 | 0.536013615 | 0.288703695 | 0.000000000 | 1.000000000 |
| e174_vs_e169 | e72_active | True | 94 | 78 | -0.000001726 | 0.441423774 | 0.568514735 | 0.484547313 | 1.000000000 | 1.000000000 |
| e174_vs_e169 | target | Q1 | 41 | 41 | -0.000003624 | 0.926761733 | 0.554724388 | 0.439443908 | 0.487804878 | 1.000000000 |
| e174_vs_e169 | target | Q3 | 47 | 47 | -0.000002399 | 0.613558741 | 0.487571986 | 0.440809263 | 0.468085106 | 1.000000000 |
| e174_vs_e169 | target | S3 | 66 | 66 | -0.000002150 | 0.549756522 | 0.653858533 | 0.183008034 | 0.015151515 | 1.000000000 |
| e174_vs_e169 | target | S2 | 43 | 43 | 0.000000269 | 0.068741941 | 0.580538970 | 0.474977577 | 0.395348837 | 1.000000000 |
| e174_vs_e169 | target | S1 | 26 | 26 | 0.000000434 | 0.111111187 | 0.618709297 | 0.478880324 | 0.576923077 | 1.000000000 |
| e174_vs_e169 | target | S4 | 41 | 41 | 0.000000676 | 0.172994063 | 0.476320521 | 0.449603809 | 0.439024390 | 1.000000000 |
| e174_vs_e169 | target | Q2 | 71 | 71 | 0.000002883 | 0.737229805 | 0.472376986 | 0.183135093 | 0.014084507 | 1.000000000 |
| e174_vs_e169 | target_context | Q1:between_train_runs | 36 | 36 | -0.000003381 | 0.864698845 | 0.558866880 | 0.439770891 | 0.500000000 | 1.000000000 |
| e174_vs_e169 | target_context | Q3:between_train_runs | 39 | 39 | -0.000002314 | 0.591738928 | 0.480169885 | 0.441536446 | 0.487179487 | 1.000000000 |
| e174_vs_e169 | target_context | S3:between_train_runs | 52 | 52 | -0.000001785 | 0.456451184 | 0.656004536 | 0.182521307 | 0.019230769 | 1.000000000 |
| e174_vs_e169 | target_context | S3:after_train_run | 14 | 14 | -0.000000365 | 0.093305337 | 0.645028625 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e169 | target_context | Q2:after_train_run | 6 | 6 | -0.000000336 | 0.085904655 | 0.452302090 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e169 | target_context | Q1:after_train_run | 5 | 5 | -0.000000243 | 0.062062888 | 0.508013374 | 0.437089626 | 0.400000000 | 1.000000000 |
| e174_vs_e169 | target_context | S2:after_train_run | 3 | 3 | -0.000000194 | 0.049608440 | 0.420722931 | 0.480108383 | 0.333333333 | 1.000000000 |
| e174_vs_e169 | target_context | S1:after_train_run | 4 | 4 | -0.000000107 | 0.027319353 | 0.682222222 | 0.462930566 | 0.750000000 | 1.000000000 |
| e174_vs_e169 | target_context | Q3:after_train_run | 8 | 8 | -0.000000085 | 0.021819813 | 0.594071341 | 0.437264248 | 0.375000000 | 1.000000000 |
| e174_vs_e169 | target_context | S4:after_train_run | 6 | 6 | 0.000000043 | 0.010921855 | 0.461665607 | 0.439472603 | 0.500000000 | 1.000000000 |
| e174_vs_e169 | target_context | S2:between_train_runs | 40 | 40 | 0.000000463 | 0.118350381 | 0.590287597 | 0.474592766 | 0.400000000 | 1.000000000 |
| e174_vs_e169 | target_context | S1:between_train_runs | 22 | 22 | 0.000000541 | 0.138430539 | 0.612932462 | 0.481780279 | 0.545454545 | 1.000000000 |
| e174_vs_e169 | target_context | S4:between_train_runs | 35 | 35 | 0.000000634 | 0.162072208 | 0.479233827 | 0.451340588 | 0.428571429 | 1.000000000 |
| e174_vs_e169 | target_context | Q2:between_train_runs | 65 | 65 | 0.000003219 | 0.823134460 | 0.473668724 | 0.182979944 | 0.015384615 | 1.000000000 |
| e174_vs_e169 | target_group | Q | 159 | 123 | -0.000003140 | 0.803090669 | 0.500395705 | 0.325395140 | 0.270440252 | 1.000000000 |
| e174_vs_e169 | target_group | S | 176 | 123 | -0.000000770 | 0.196909331 | 0.592170182 | 0.360154606 | 0.289772727 | 1.000000000 |
| e174_vs_e172 | context_type | between_train_runs | 58 | 51 | -0.000009504 | 0.814287940 | 0.394543180 | 0.270971133 | 0.086206897 | 1.000000000 |
| e174_vs_e172 | context_type | after_train_run | 17 | 14 | -0.000002168 | 0.185712060 | 0.406451863 | 0.303815940 | 0.058823529 | 1.000000000 |
| e174_vs_e172 | e72_active | False | 69 | 60 | -0.000010339 | 0.885824696 | 0.392455934 | 0.266971624 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | e72_active | True | 6 | 6 | -0.000001333 | 0.114175304 | 0.443262888 | 0.410025768 | 1.000000000 | 1.000000000 |
| e174_vs_e172 | target | S3 | 25 | 25 | -0.000003234 | 0.277047754 | 0.311228885 | 0.183693635 | 0.040000000 | 1.000000000 |
| e174_vs_e172 | target | Q2 | 21 | 21 | -0.000002953 | 0.253018963 | 0.504005847 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target | S2 | 11 | 11 | -0.000002682 | 0.229754584 | 0.437656519 | 0.425341915 | 0.181818182 | 1.000000000 |
| e174_vs_e172 | target | S1 | 7 | 7 | -0.000001471 | 0.125987790 | 0.322315306 | 0.421013653 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target | Q1 | 5 | 5 | -0.000000833 | 0.071391079 | 0.490822096 | 0.449889309 | 0.400000000 | 1.000000000 |
| e174_vs_e172 | target | Q3 | 4 | 4 | -0.000000414 | 0.035502540 | 0.462727806 | 0.422597985 | 0.250000000 | 1.000000000 |
| e174_vs_e172 | target | S4 | 2 | 2 | -0.000000085 | 0.007297291 | 0.440000000 | 0.421013653 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | S3:between_train_runs | 22 | 22 | -0.000002850 | 0.244136083 | 0.309458771 | 0.183540602 | 0.045454545 | 1.000000000 |
| e174_vs_e172 | target_context | S2:between_train_runs | 8 | 8 | -0.000002330 | 0.199663395 | 0.448154326 | 0.426965014 | 0.250000000 | 1.000000000 |
| e174_vs_e172 | target_context | Q2:between_train_runs | 15 | 15 | -0.000001977 | 0.169385054 | 0.526428862 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | S1:between_train_runs | 6 | 6 | -0.000001210 | 0.103678061 | 0.322902312 | 0.421013653 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | Q2:after_train_run | 6 | 6 | -0.000000976 | 0.083633910 | 0.467029437 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | Q1:between_train_runs | 3 | 3 | -0.000000747 | 0.063967803 | 0.495555556 | 0.424666786 | 0.333333333 | 1.000000000 |
| e174_vs_e172 | target_context | S3:after_train_run | 3 | 3 | -0.000000384 | 0.032911671 | 0.325230824 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | S2:after_train_run | 3 | 3 | -0.000000351 | 0.030091188 | 0.374674934 | 0.421013653 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | Q3:between_train_runs | 2 | 2 | -0.000000305 | 0.026160253 | 0.478738037 | 0.424182316 | 0.500000000 | 1.000000000 |
| e174_vs_e172 | target_context | S1:after_train_run | 1 | 1 | -0.000000260 | 0.022309729 | 0.317777778 | 0.421013653 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | Q3:after_train_run | 2 | 2 | -0.000000109 | 0.009342287 | 0.400000000 | 0.421013653 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_context | Q1:after_train_run | 2 | 2 | -0.000000087 | 0.007423276 | 0.462350745 | 0.487723093 | 0.500000000 | 1.000000000 |
| e174_vs_e172 | target_context | S4:between_train_runs | 2 | 2 | -0.000000085 | 0.007297291 | 0.440000000 | 0.421013653 | 0.000000000 | 1.000000000 |
| e174_vs_e172 | target_group | S | 45 | 41 | -0.000007471 | 0.640087418 | 0.351412806 | 0.290227218 | 0.066666667 | 1.000000000 |
| e174_vs_e172 | target_group | Q | 30 | 28 | -0.000004201 | 0.359912582 | 0.496541612 | 0.260699062 | 0.100000000 | 1.000000000 |
| e174_vs_e95 | context_type | between_train_runs | 741 | 156 | -0.000100324 | 0.806679960 | 0.459845072 | 0.344889297 | 0.267206478 | 1.000000000 |
| e174_vs_e95 | context_type | after_train_run | 163 | 37 | -0.000024043 | 0.193320040 | 0.471954595 | 0.351883483 | 0.276073620 | 1.000000000 |
| e174_vs_e95 | e72_active | False | 661 | 193 | -0.000091019 | 0.731854766 | 0.459928737 | 0.305594769 | 0.000000000 | 1.000000000 |
| e174_vs_e95 | e72_active | True | 243 | 147 | -0.000033348 | 0.268145234 | 0.468090344 | 0.456468452 | 1.000000000 | 1.000000000 |
| e174_vs_e95 | target | S3 | 168 | 168 | -0.000025110 | 0.201905617 | 0.366243850 | 0.178804235 | 0.053571429 | 1.000000000 |
| e174_vs_e95 | target | S1 | 95 | 95 | -0.000023403 | 0.188179379 | 0.358247766 | 0.455104170 | 0.536842105 | 1.000000000 |
| e174_vs_e95 | target | S4 | 116 | 116 | -0.000018136 | 0.145823257 | 0.489680190 | 0.435114405 | 0.344827586 | 1.000000000 |
| e174_vs_e95 | target | Q1 | 121 | 121 | -0.000017964 | 0.144442120 | 0.481093327 | 0.433137833 | 0.388429752 | 1.000000000 |
| e174_vs_e95 | target | Q2 | 165 | 165 | -0.000015964 | 0.128362533 | 0.535559334 | 0.184092630 | 0.006060606 | 1.000000000 |
| e174_vs_e95 | target | S2 | 122 | 122 | -0.000013686 | 0.110041761 | 0.456153547 | 0.453014613 | 0.393442623 | 1.000000000 |
| e174_vs_e95 | target | Q3 | 117 | 117 | -0.000010104 | 0.081245332 | 0.593498594 | 0.436922678 | 0.401709402 | 1.000000000 |
| e174_vs_e95 | target_context | S3:between_train_runs | 141 | 141 | -0.000022762 | 0.183023244 | 0.369356545 | 0.177653070 | 0.063829787 | 1.000000000 |
| e174_vs_e95 | target_context | S1:between_train_runs | 79 | 79 | -0.000020267 | 0.162959641 | 0.355607541 | 0.456701058 | 0.544303797 | 1.000000000 |
| e174_vs_e95 | target_context | Q1:between_train_runs | 99 | 99 | -0.000014186 | 0.114064820 | 0.477053460 | 0.433220050 | 0.363636364 | 1.000000000 |
| e174_vs_e95 | target_context | S4:between_train_runs | 97 | 97 | -0.000012842 | 0.103259058 | 0.480153856 | 0.436260083 | 0.350515464 | 1.000000000 |
| e174_vs_e95 | target_context | Q2:between_train_runs | 136 | 136 | -0.000012128 | 0.097521539 | 0.545268706 | 0.183938408 | 0.007352941 | 1.000000000 |
| e174_vs_e95 | target_context | S2:between_train_runs | 91 | 91 | -0.000009702 | 0.078010158 | 0.457319231 | 0.454818945 | 0.384615385 | 1.000000000 |
| e174_vs_e95 | target_context | Q3:between_train_runs | 98 | 98 | -0.000008437 | 0.067841501 | 0.586154130 | 0.436983080 | 0.408163265 | 1.000000000 |
| e174_vs_e95 | target_context | S4:after_train_run | 19 | 19 | -0.000005294 | 0.042564199 | 0.527519318 | 0.429265418 | 0.315789474 | 1.000000000 |
| e174_vs_e95 | target_context | S2:after_train_run | 31 | 31 | -0.000003984 | 0.032031603 | 0.454166224 | 0.447718026 | 0.419354839 | 1.000000000 |
| e174_vs_e95 | target_context | Q2:after_train_run | 29 | 29 | -0.000003836 | 0.030840995 | 0.495684345 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e95 | target_context | Q1:after_train_run | 22 | 22 | -0.000003778 | 0.030377300 | 0.505399268 | 0.432767856 | 0.500000000 | 1.000000000 |
| e174_vs_e95 | target_context | S1:after_train_run | 16 | 16 | -0.000003137 | 0.025219738 | 0.373379760 | 0.447219538 | 0.500000000 | 1.000000000 |
| e174_vs_e95 | target_context | S3:after_train_run | 27 | 27 | -0.000002348 | 0.018882373 | 0.342306100 | 0.184815876 | 0.000000000 | 1.000000000 |
| e174_vs_e95 | target_context | Q3:after_train_run | 19 | 19 | -0.000001667 | 0.013403831 | 0.633825972 | 0.436611131 | 0.368421053 | 1.000000000 |
| e174_vs_e95 | target_group | S | 501 | 192 | -0.000080335 | 0.645950014 | 0.411407867 | 0.357315492 | 0.295409182 | 1.000000000 |
| e174_vs_e95 | target_group | Q | 403 | 184 | -0.000044032 | 0.354049986 | 0.535590667 | 0.332270261 | 0.235732010 | 1.000000000 |

## Top E174-vs-E95 Hard-Label Cells

| pair | sub_idx | target | swing | support_label | p_y1_focus_mean | p_y1_subject | p_y1_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e174_partial_reopen_vs_e95 | 141 | S1 | 0.000005832 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 196 | Q3 | 0.000004562 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e174_partial_reopen_vs_e95 | 190 | Q3 | 0.000004531 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e174_partial_reopen_vs_e95 | 194 | Q3 | 0.000004466 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e174_partial_reopen_vs_e95 | 67 | S4 | 0.000004432 | 1 | 0.287171717 | 0.151515152 | 0.150000000 |
| e174_partial_reopen_vs_e95 | 135 | S1 | 0.000004082 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 143 | S1 | 0.000004017 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 182 | Q3 | 0.000004015 | 1 | 0.600000000 | 0.600000000 | 0.600000000 |
| e174_partial_reopen_vs_e95 | 205 | S2 | 0.000003995 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e174_partial_reopen_vs_e95 | 136 | S1 | 0.000003981 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 139 | S3 | 0.000003936 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e174_partial_reopen_vs_e95 | 180 | S1 | 0.000003915 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 63 | S1 | 0.000003819 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 70 | S4 | 0.000003816 | 1 | 0.560000000 | 0.560000000 | 0.560000000 |
| e174_partial_reopen_vs_e95 | 113 | Q1 | 0.000003792 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e174_partial_reopen_vs_e95 | 132 | S1 | 0.000003791 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 5 | Q1 | 0.000003755 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e174_partial_reopen_vs_e95 | 138 | S3 | 0.000003626 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e174_partial_reopen_vs_e95 | 163 | Q1 | 0.000003596 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e174_partial_reopen_vs_e95 | 141 | Q1 | 0.000003521 | 1 | 0.495555556 | 0.495555556 | 0.495555556 |
| e174_partial_reopen_vs_e95 | 164 | S1 | 0.000003515 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e95 | 0 | Q1 | 0.000003508 | 1 | 0.361526649 | 0.439024390 | 0.150000000 |
| e174_partial_reopen_vs_e95 | 204 | S2 | 0.000003452 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e174_partial_reopen_vs_e95 | 79 | S4 | 0.000003436 | 1 | 0.560000000 | 0.560000000 | 0.560000000 |
| e174_partial_reopen_vs_e95 | 160 | S1 | 0.000003382 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |

## Top E174-vs-E172 Reopened Cells

| pair | sub_idx | target | swing | support_label | p_y1_focus_mean | p_y1_subject | p_y1_nearest_hard085 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e174_partial_reopen_vs_e172_tail_repair | 205 | S2 | 0.000002996 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e174_partial_reopen_vs_e172_tail_repair | 204 | S2 | 0.000002589 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e174_partial_reopen_vs_e172_tail_repair | 71 | Q2 | 0.000002496 | 0 | 0.562222222 | 0.562222222 | 0.562222222 |
| e174_partial_reopen_vs_e172_tail_repair | 70 | Q2 | 0.000002399 | 0 | 0.562222222 | 0.562222222 | 0.562222222 |
| e174_partial_reopen_vs_e172_tail_repair | 166 | S1 | 0.000002378 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e172_tail_repair | 213 | S2 | 0.000002297 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e174_partial_reopen_vs_e172_tail_repair | 115 | S2 | 0.000002205 | 1 | 0.651111111 | 0.651111111 | 0.651111111 |
| e174_partial_reopen_vs_e172_tail_repair | 157 | S1 | 0.000002132 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e172_tail_repair | 215 | S2 | 0.000002089 | 0 | 0.651111111 | 0.651111111 | 0.651111111 |
| e174_partial_reopen_vs_e172_tail_repair | 159 | S1 | 0.000002060 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e172_tail_repair | 2 | S3 | 0.000001989 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e174_partial_reopen_vs_e172_tail_repair | 162 | S1 | 0.000001900 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e172_tail_repair | 67 | S2 | 0.000001876 | 1 | 0.438754209 | 0.515151515 | 0.150000000 |
| e174_partial_reopen_vs_e172_tail_repair | 152 | S1 | 0.000001848 | 0 | 0.682222222 | 0.682222222 | 0.682222222 |
| e174_partial_reopen_vs_e172_tail_repair | 4 | S3 | 0.000001743 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e174_partial_reopen_vs_e172_tail_repair | 161 | S3 | 0.000001712 | 0 | 0.769380197 | 0.795918367 | 0.850000000 |
| e174_partial_reopen_vs_e172_tail_repair | 9 | S3 | 0.000001705 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e174_partial_reopen_vs_e172_tail_repair | 0 | S3 | 0.000001628 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e174_partial_reopen_vs_e172_tail_repair | 212 | Q3 | 0.000001605 | 1 | 0.396341463 | 0.439024390 | 0.150000000 |
| e174_partial_reopen_vs_e172_tail_repair | 165 | Q2 | 0.000001588 | 1 | 0.562222222 | 0.562222222 | 0.562222222 |
| e174_partial_reopen_vs_e172_tail_repair | 106 | Q2 | 0.000001583 | 1 | 0.562222222 | 0.562222222 | 0.562222222 |
| e174_partial_reopen_vs_e172_tail_repair | 14 | S3 | 0.000001511 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |
| e174_partial_reopen_vs_e172_tail_repair | 152 | Q2 | 0.000001450 | 1 | 0.562222222 | 0.562222222 | 0.562222222 |
| e174_partial_reopen_vs_e172_tail_repair | 157 | S3 | 0.000001387 | 0 | 0.769380197 | 0.795918367 | 0.850000000 |
| e174_partial_reopen_vs_e172_tail_repair | 10 | S3 | 0.000001378 | 0 | 0.662222222 | 0.662222222 | 0.662222222 |

## Observed Score Decision

_No observed E174 public score supplied._

## Decision

E175 creates no submission. The pre-feedback highest-upside broad expected-score
file is `analysis_outputs/submission_e174_ro_fc_top75_to1p0_95638e73.csv`.

- A win below E95 validates partial rollback reopening as public-real.
- A tie or small loss keeps E95 practical and makes E172 the only clean
  same-family contrast.
- A worse-than-E101 result demotes E174 and blocks top-N reopening siblings.
- A worse-than-mixmin result closes E174/E172/E169 same-family broad expected
  score followups unless a new public-independent bad axis explains the miss.
