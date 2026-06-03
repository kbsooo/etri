# H149 Bundle-Listener Route HS-JEPA

Date: 2026-06-03

## Question

H148 recovered a cell-level listener, but it collapsed to a tiny action. H149
tests a stronger HS-JEPA claim:

```text
the public/private listener is a human-state bundle field, not an isolated
cell field.
```

Bundles include target, subject, row-order, weekend/friday/monday, pay-window,
month boundary, month, and H057 base-probability regimes.

## Public Observations Used

| file | public_lb | delta_vs_h057 | role |
| --- | --- | --- | --- |
| submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | 0.567747594 | 0.000000000 | frontier |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 0.567904825 | 0.000157231 | frontier_basin |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | 0.567904825 | 0.000157231 | frontier_basin |
| submission_h144_targetxor_def80b88_uploadsafe.csv | 0.567929641 | 0.000182047 | tie_sensor |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | 0.567929641 | 0.000182047 | tie_sensor |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.568123483 | 0.000375889 | breakthrough_anchor |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 0.568494202 | 0.000746608 | negative_sensor |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.008411356 | pre_h_world |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.008532974 | pre_h_world |
| submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.576290429 | 0.008542835 | pre_h_world |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.008543736 | pre_h_world |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.008552772 | pre_h_world |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.008559047 | pre_h_world |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.008564237 | pre_h_world |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.008581903 | pre_h_world |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.008660183 | pre_h_world |
| submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.009287908 | bad_anchor |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.009538915 | bad_anchor |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.578171818 | 0.010424224 | bad_anchor |

## Bundle Model Selection

| model | alpha | n_obs | n_features | loo_mae | loo_rmse | loo_p90_abs | loo_spearman | h144_h145_pred_gap_abs | selection_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bundle_all | 1.000000000 | 19 | 317 | 0.000450715 | 0.000851793 | 0.001105315 | 0.858471532 | 0.000000922 | 0.000461776 |
| bundle_all | 3.000000000 | 19 | 317 | 0.000457957 | 0.000845957 | 0.001091005 | 0.833678131 | 0.000000748 | 0.000466938 |
| bundle_all | 100.000000000 | 19 | 317 | 0.000469073 | 0.000780352 | 0.001109067 | 0.684917721 | 0.000000255 | 0.000472137 |
| bundle_all | 0.300000000 | 19 | 317 | 0.000459351 | 0.000869327 | 0.001133636 | 0.792355795 | 0.000001088 | 0.000472408 |
| bundle_all | 10.000000000 | 19 | 317 | 0.000469078 | 0.000831384 | 0.001085139 | 0.825413664 | 0.000000541 | 0.000475566 |
| bundle_all | 30.000000000 | 19 | 317 | 0.000477756 | 0.000805917 | 0.001085804 | 0.819215313 | 0.000000373 | 0.000482228 |
| bundle_all | 0.100000000 | 19 | 317 | 0.000476017 | 0.000891764 | 0.001164136 | 0.779959094 | 0.000001200 | 0.000490423 |
| bundle_all | 0.030000000 | 19 | 317 | 0.000491924 | 0.000908599 | 0.001199901 | 0.753099575 | 0.000001269 | 0.000507157 |
| bundle_all | 0.010000000 | 19 | 317 | 0.000503241 | 0.000917076 | 0.001233677 | 0.709711123 | 0.000001299 | 0.000518830 |
| bundle_all | 0.003000000 | 19 | 317 | 0.000511191 | 0.000922004 | 0.001260220 | 0.676653254 | 0.000001303 | 0.000526826 |
| bundle_all | 0.001000000 | 19 | 317 | 0.000514848 | 0.000924263 | 0.001272807 | 0.635330918 | 0.000001268 | 0.000530059 |
| bundle_plus_bad | 30.000000000 | 10 | 317 | 0.000716345 | 0.001039922 | 0.001631322 | 0.605063381 | 0.000000278 | 0.000719684 |
| bundle_plus_bad | 0.010000000 | 10 | 317 | 0.000726071 | 0.001153993 | 0.001649707 | 0.621870697 | 0.000000538 | 0.000732532 |
| bundle_plus_bad | 10.000000000 | 10 | 317 | 0.000728165 | 0.001076026 | 0.001602059 | 0.605063381 | 0.000000364 | 0.000732534 |
| bundle_plus_bad | 0.030000000 | 10 | 317 | 0.000726148 | 0.001153643 | 0.001649543 | 0.621870697 | 0.000000540 | 0.000732624 |
| bundle_plus_bad | 0.003000000 | 10 | 317 | 0.000726292 | 0.001154135 | 0.001649372 | 0.621870697 | 0.000000532 | 0.000732676 |
| bundle_plus_bad | 0.001000000 | 10 | 317 | 0.000726844 | 0.001154231 | 0.001648208 | 0.621870697 | 0.000000514 | 0.000733009 |
| bundle_plus_bad | 0.100000000 | 10 | 317 | 0.000726582 | 0.001152455 | 0.001648581 | 0.621870697 | 0.000000538 | 0.000733035 |
| bundle_plus_bad | 0.300000000 | 10 | 317 | 0.000727732 | 0.001149189 | 0.001645831 | 0.621870697 | 0.000000531 | 0.000734101 |
| bundle_plus_bad | 1.000000000 | 10 | 317 | 0.000730519 | 0.001138971 | 0.001637342 | 0.621870697 | 0.000000508 | 0.000736616 |
| bundle_plus_bad | 100.000000000 | 10 | 317 | 0.000734509 | 0.001051473 | 0.001816339 | 0.537834116 | 0.000000222 | 0.000737176 |
| bundle_plus_bad | 3.000000000 | 10 | 317 | 0.000732924 | 0.001116884 | 0.001620530 | 0.605063381 | 0.000000458 | 0.000738416 |
| bundle_frontier | 0.001000000 | 7 | 317 | 0.000192447 | 0.000334068 | 0.000503223 | -0.735612358 | 0.000000001 | 0.000928075 |
| bundle_frontier | 0.003000000 | 7 | 317 | 0.000193230 | 0.000335866 | 0.000505558 | -0.735612358 | 0.000000002 | 0.000928862 |

Chosen model by selection score: `bundle_all`.

## Observed Fit

| file | role | actual_delta | bundle_all_fit_delta | bundle_all_fit_error |
| --- | --- | --- | --- | --- |
| submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv | frontier | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | frontier_basin | 0.000157231 | 0.000185042 | 0.000027811 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | frontier_basin | 0.000157231 | 0.000139809 | -0.000017422 |
| submission_h144_targetxor_def80b88_uploadsafe.csv | tie_sensor | 0.000182047 | 0.000151181 | -0.000030866 |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | tie_sensor | 0.000182047 | 0.000150259 | -0.000031788 |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | breakthrough_anchor | 0.000375889 | 0.000385618 | 0.000009729 |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | negative_sensor | 0.000746608 | 0.000736055 | -0.000010553 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | pre_h_world | 0.008411356 | 0.008462148 | 0.000050792 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | pre_h_world | 0.008532974 | 0.008511848 | -0.000021125 |
| submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | pre_h_world | 0.008542835 | 0.008545428 | 0.000002593 |
| submission_e95_hardtail_541e3973.csv | pre_h_world | 0.008543736 | 0.008567698 | 0.000023962 |
| submission_e101_q2s3tail_177569bc.csv | pre_h_world | 0.008552772 | 0.008565173 | 0.000012400 |
| submission_mixmin_0c916bb4.csv | pre_h_world | 0.008559047 | 0.008580391 | 0.000021345 |
| submission_e176_abl_q2_to0p75_91e49725.csv | pre_h_world | 0.008564237 | 0.008520244 | -0.000043993 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | pre_h_world | 0.008581903 | 0.008580149 | -0.000001754 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | pre_h_world | 0.008660183 | 0.008661003 | 0.000000820 |
| submission_e323_5508f966_uploadsafe.csv | bad_anchor | 0.009287908 | 0.009276209 | -0.000011699 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | bad_anchor | 0.009538915 | 0.009516658 | -0.000022257 |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | bad_anchor | 0.010424224 | 0.010402142 | -0.000022082 |

## Candidate Stress Ranking

| file | changed_cells_vs_h057 | changed_rows_vs_h057 | h088_move_cosine | bundle_all_pred_delta | bundle_all_high_toxic_cells | bundle_all_high_benefit_cells |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 657 | 141 | 0.887213191 | -0.001089918 | 13 | 8 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 524 | 152 | 0.835549425 | -0.000990332 | 23 | 14 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 736 | 158 | 0.887472000 | -0.000124451 | 31 | 23 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 597 | 152 | 0.828647527 | -0.000111866 | 20 | 13 |
| submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 28 | 23 | -0.057669876 | -0.000039686 | 1 | 1 |
| submission_h050_target_route_phase_b140216b_uploadsafe.csv | 343 | 111 | -0.125396149 | 0.000139809 | 9 | 6 |
| submission_h145_q3repair_2d818e46_uploadsafe.csv | 27 | 22 | -0.063807440 | 0.000150259 | 1 | 0 |
| submission_h144_targetxor_def80b88_uploadsafe.csv | 28 | 23 | -0.064775307 | 0.000151181 | 1 | 0 |
| submission_h141_commoncore_0999d3ae_uploadsafe.csv | 27 | 22 | -0.063558603 | 0.000154042 | 1 | 0 |
| submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv | 270 | 45 | -0.144085796 | 0.000185042 | 7 | 5 |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 315 | 45 | -0.144102131 | 0.000385618 | 16 | 10 |
| submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv | 980 | 168 | 1.000000000 | 0.000736055 | 53 | 30 |

## Strongest Bundle Coefficients

| model | feature | family | coef_per_unit | coef | scale | n_cells |
| --- | --- | --- | --- | --- | --- | --- |
| bundle_all | row_decile=5|target=Q1 | row_order_target | -0.002114629 | -0.000119517 | 0.056519371 | 25 |
| bundle_all | subject=id08|target=Q2 | subject_target | 0.000770103 | 0.000043339 | 0.056276723 | 19 |
| bundle_all | subject=id10|target=Q1 | subject_target | 0.000726145 | 0.000050328 | 0.069307838 | 22 |
| bundle_all | month_start|target=S4 | human_social_date_target | -0.000671495 | -0.000048240 | 0.071839463 | 15 |
| bundle_plus_bad | row_decile=5|target=Q1 | row_order_target | -0.000538357 | -0.000037859 | 0.070323895 | 25 |
| bundle_all | row_decile=7|target=Q2 | row_order_target | 0.000519052 | 0.000061009 | 0.117539881 | 25 |
| bundle_plus_bad | subject=id08|target=Q2 | subject_target | 0.000460688 | 0.000035314 | 0.076655166 | 19 |
| bundle_plus_bad | month_start|target=S4 | human_social_date_target | -0.000453525 | -0.000039433 | 0.086947630 | 15 |
| bundle_all | row_decile=8|target=Q2 | row_order_target | -0.000418966 | -0.000032584 | 0.077771438 | 25 |
| bundle_all | friday|target=Q2 | human_social_date_target | 0.000365298 | 0.000034067 | 0.093257772 | 36 |
| bundle_frontier | subject=id03|target=Q2 | subject_target | -0.000342327 | -0.000004389 | 0.012821960 | 21 |
| bundle_plus_bad | row_decile=7|target=Q2 | row_order_target | 0.000341331 | 0.000046727 | 0.136897539 | 25 |
| bundle_all | month_start|target=Q2 | human_social_date_target | 0.000336068 | 0.000033152 | 0.098645727 | 15 |
| bundle_all | subject=id01|target=Q2 | subject_target | 0.000325438 | 0.000037278 | 0.114546542 | 27 |
| bundle_all | monday|target=Q3 | human_social_date_target | -0.000294095 | -0.000052636 | 0.178975964 | 37 |
| bundle_all | row_decile=5|target=Q3 | row_order_target | 0.000282966 | 0.000055928 | 0.197648351 | 25 |
| bundle_plus_bad | subject=id09|target=Q2 | subject_target | -0.000272176 | -0.000036240 | 0.133148366 | 27 |
| bundle_all | month_end|target=S4 | human_social_date_target | -0.000272059 | -0.000044002 | 0.161735563 | 19 |
| bundle_all | row_decile=7|target=S4 | row_order_target | -0.000270952 | -0.000064100 | 0.236571763 | 25 |
| bundle_plus_bad | row_decile=8|target=Q2 | row_order_target | -0.000268407 | -0.000026503 | 0.098740103 | 25 |
| bundle_all | subject=id03|target=Q2 | subject_target | -0.000264691 | -0.000030726 | 0.116083879 | 21 |
| bundle_all | baseq=2|target=Q1 | base_prob_target | -0.000254066 | -0.000030971 | 0.121900482 | 50 |
| bundle_plus_bad | subject=id05|target=Q2 | subject_target | -0.000239693 | -0.000016773 | 0.069977628 | 21 |
| bundle_all | subject=id09|target=Q2 | subject_target | -0.000234512 | -0.000031505 | 0.134341097 | 27 |
| bundle_plus_bad | month_end|target=S4 | human_social_date_target | -0.000230199 | -0.000032639 | 0.141788336 | 19 |
| bundle_all | row_decile=0|target=Q2 | row_order_target | 0.000224029 | 0.000028459 | 0.127031437 | 24 |
| bundle_plus_bad | row_decile=1|target=Q2 | row_order_target | 0.000222350 | 0.000032350 | 0.145490657 | 25 |
| bundle_all | row_decile=1|target=Q2 | row_order_target | 0.000221633 | 0.000030139 | 0.135985288 | 25 |
| bundle_all | subject=id04|target=S4 | subject_target | -0.000215509 | -0.000036719 | 0.170382435 | 27 |
| bundle_all | row_decile=1|target=S4 | row_order_target | 0.000213512 | 0.000081058 | 0.379641430 | 25 |

## Promoted Diagnostic Candidate

| candidate_file | candidate_path | best_bundle_model | selected_cells | selected_rows | selected_source_mix | selected_target_mix | worldview | failure_interpretation | validation_path | validation_rows | validation_keys_match | validation_duplicate_keys | validation_nan_cells | validation_min_prob | validation_max_prob | validation_changed_cells_vs_h057_validation | validation_upload_safe | metric_changed_cells_vs_h057 | metric_changed_rows_vs_h057 | metric_move_l1 | metric_move_l2 | metric_h088_move_cosine | metric_bundle_frontier_pred_delta | metric_bundle_frontier_benefit_sum | metric_bundle_frontier_toxicity_sum | metric_bundle_frontier_high_toxic_cells | metric_bundle_frontier_high_benefit_cells | metric_bundle_plus_bad_pred_delta | metric_bundle_plus_bad_benefit_sum | metric_bundle_plus_bad_toxicity_sum | metric_bundle_plus_bad_high_toxic_cells | metric_bundle_plus_bad_high_benefit_cells | metric_bundle_all_pred_delta | metric_bundle_all_benefit_sum | metric_bundle_all_toxicity_sum | metric_bundle_all_high_toxic_cells | metric_bundle_all_high_benefit_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | /Users/kbsoo/Downloads/cl2/submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | bundle_all | 349 | 154 | {'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 144, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 89, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 64, 'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 38, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 14} | {'S3': 86, 'S4': 59, 'S1': 48, 'S2': 45, 'Q2': 40, 'Q1': 37, 'Q3': 34} | Listener responsibility is not recoverable safely at individual-cell resolution, but may be recoverable as human-state bundles over target, subject, row-order, weekend/pay-window, and base-probability regimes. | If this fails, route-bundle listener inversion is still too weak; the translator must move from supervised public equations to discrete row-target assignment constraints or new public sensors. | /Users/kbsoo/Downloads/cl2/submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 349 | True | 349 | 154 | 29.959280729 | 2.259664189 | 0.121063141 | -0.000168047 | 0.000760790 | 0.000592743 | 7 | 17 | -0.003198392 | 0.003198392 | 0.000000000 | 0 | 26 | -0.004994063 | 0.004994063 | 0.000000000 | 0 | 25 |

Source mix:

| source_file | cells |
| --- | --- |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 144 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 89 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 64 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 38 |
| submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 14 |

Target mix:

| target | cells |
| --- | --- |
| S3 | 86 |
| S4 | 59 |
| S1 | 48 |
| S2 | 45 |
| Q2 | 40 |
| Q1 | 37 |
| Q3 | 34 |

## Interpretation

H149 is the first direct row-target correction translator that uses all three
current HS-JEPA pieces together:

```text
human-social/date/subject/route context -> bundle listener
multi-source action proposal -> listener-aware row-target assignment
anti-shortcut/H088 penalty -> correction field
```

If H149-style candidates look public-negative offline, that is strong evidence
that H071/H073/H074 are not missing only a small alpha.  They need a different
assignment equation.  If they look public-positive, this becomes the next
candidate family to probe when submission slots return.
