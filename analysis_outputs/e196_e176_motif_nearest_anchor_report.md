# E196 E176 Motif Nearest-Anchor Stress

## Question

Can row/order/block/target motif alone resolve whether E176's public-decisive cells resemble known public-winning or public-losing critical-cell patterns?

## Result

No motif view is action-grade. The best view is `sequence_axis_flank` on `top4` with known-pair LOO accuracy `0.833333`, exact E101 boundary correctness `0`, and mixmin broad-success correctness `1`.

E176's nearest anchors in that best view lean `new_lost` with inverse-distance vote new_won `0.505761`, but this is not action-grade because the known-anchor stress is too weak.

## Summary

| set | view | known_loo_accuracy | known_loo_correct | known_loo_n | exact_e101_boundary_correct | mixmin_broad_success_correct | e176_nearest_direction | e176_nearest_pair | e176_nearest_distance | e176_nearest_win_distance | e176_nearest_loss_distance | e176_win_distance_advantage | e176_inverse_distance_vote_new_won | e176_inverse_distance_vote_new_lost | action_grade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top4 | sequence_axis_flank | 0.833333333 | 5 | 6 | 0 | 1 | new_lost | e72_vs_e95 | 18.8709663 | 19.6816033 | 18.8709663 | -0.810637062 | 0.505761232 | 0.494238768 | False |
| top4 | sequence_axis | 0.833333333 | 5 | 6 | 0 | 1 | new_lost | e72_vs_e95 | 18.687274 | 19.5810292 | 18.687274 | -0.893755214 | 0.505578785 | 0.494421215 | False |
| top16 | sequence_only | 0.666666667 | 4 | 6 | 0 | 0 | new_lost | e72_vs_e95 | 18.511364 | 19.4051271 | 18.511364 | -0.893763162 | 0.492729056 | 0.507270944 | False |
| top16 | sequence_axis_flank | 0.5 | 3 | 6 | 0 | 0 | new_lost | e72_vs_e95 | 23.9068118 | 23.9418771 | 23.9068118 | -0.0350653445 | 0.501920728 | 0.498079272 | False |
| top16 | sequence_axis | 0.5 | 3 | 6 | 0 | 0 | new_lost | e72_vs_e95 | 23.1433631 | 23.603244 | 23.1433631 | -0.45988092 | 0.499268641 | 0.500731359 | False |
| top4 | sequence_only | 0.5 | 3 | 6 | 0 | 0 | new_lost | e72_vs_e95 | 15.6577523 | 17.148794 | 15.6577523 | -1.4910417 | 0.497548178 | 0.502451822 | False |
| top33 | sequence_only | 0.333333333 | 2 | 6 | 0 | 0 | new_won | mixmin_vs_a2c8 | 11.5502876 | 11.5502876 | 14.5335367 | 2.98324912 | 0.537886919 | 0.462113081 | False |
| top33 | sequence_axis_flank | 0.333333333 | 2 | 6 | 0 | 0 | new_won | mixmin_vs_a2c8 | 13.8754845 | 13.8754845 | 17.8496409 | 3.97415641 | 0.537664388 | 0.462335612 | False |
| top33 | sequence_axis | 0.333333333 | 2 | 6 | 0 | 0 | new_won | mixmin_vs_a2c8 | 13.5674498 | 13.5674498 | 17.0698444 | 3.50239452 | 0.536023565 | 0.463976435 | False |

## E176 Profiles

| pair | set | top_n | actual_direction | known_status | family | actual_delta | n_cells | n_rows | n_subjects | n_blocks | swing_sum | top_swing_share | row_coverage | subject_coverage | block_coverage | between_train_runs_rate | edge_like_rate | is_weekend_rate | flank_conflict_rate | both_flanks_rate | e72_active_rate | e101_active_rate | all_veto_null_rate | all_safe_density_mean | broad_low_alpha_mass_mean | e101_plausible_mass_mean | target_Q1 | target_Q2 | target_Q3 | target_S1 | target_S2 | target_S3 | target_S4 | context_between_train_runs | context_after_train_run | context_before_train_run | context_isolated | pos_single | pos_left_edge | pos_right_edge | pos_near_edge | pos_interior | block_len_1-2 | block_len_3-5 | block_len_6-10 | block_len_11-16 | q_share | s_share | q2s3_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176_vs_e95_pending | top4 | 4 | pending_new_better | pending | pending_broad_q2_underopen | NA | 4 | 4 | 2 | 3 | 1.93910568e-05 | 0.300755025 | 0.016 | 0.2 | 0.0833333333 | 1 | 1 | 0.230323576 | 0.233675179 | 1 | 0.699244975 | 0 | 1 | 0.438823504 | 0.0206905822 | 0.0050989898 | 0 | 0 | 0.699244975 | 0.300755025 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0.300755025 | 0.233675179 | 0.23524622 | 0.230323576 | 0 | 0.534430204 | 0.465569796 | 0 | 0 | 0.699244975 | 0.300755025 | 0 |
| e176_vs_e95_pending | top16 | 16 | pending_new_better | pending | pending_broad_q2_underopen | NA | 16 | 16 | 6 | 12 | 6.69824968e-05 | 0.0870668912 | 0.064 | 0.6 | 0.333333333 | 0.884585346 | 0.760575914 | 0.299645156 | 0.181273462 | 0.884585346 | 0.382750464 | 0 | 1 | 0.413636138 | 0.00899844257 | 0.00173272489 | 0.0566071808 | 0 | 0.262373214 | 0.439483957 | 0.0596420567 | 0.0587600125 | 0.123133579 | 0.884585346 | 0.115414654 | 0 | 0 | 0.0870668912 | 0.243998139 | 0.18565558 | 0.243855305 | 0.239424086 | 0.214660263 | 0.312947878 | 0.231129852 | 0.241262007 | 0.318980395 | 0.681019605 | 0.0587600125 |
| e176_vs_e95_pending | top33 | 33 | pending_new_better | pending | pending_broad_q2_underopen | NA | 33 | 30 | 8 | 16 | 0.000124930771 | 0.0466815156 | 0.12 | 0.8 | 0.444444444 | 0.804692079 | 0.674806693 | 0.293079829 | 0.123323207 | 0.804692079 | 0.37294329 | 0 | 1 | 0.395088305 | 0.0091348367 | 0.0016755015 | 0.14544865 | 0.0533753084 | 0.140673212 | 0.394298012 | 0.0861446658 | 0.0865417817 | 0.0935183691 | 0.804692079 | 0.195307921 | 0 | 0 | 0.0748668605 | 0.211982805 | 0.178906614 | 0.209050413 | 0.325193307 | 0.143276929 | 0.248758801 | 0.230811376 | 0.377152894 | 0.339497171 | 0.660502829 | 0.13991709 |

## Best-View E176 Neighbors

| set | view | pending_pair | neighbor_rank | neighbor_pair | neighbor_family | neighbor_direction | distance | vote_new_won | vote_new_lost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top4 | sequence_axis_flank | e176_vs_e95_pending | 1 | e72_vs_e95 | q2s3_gate_fail | new_lost | 18.8709663 | 0.505761232 | 0.494238768 |
| top4 | sequence_axis_flank | e176_vs_e95_pending | 2 | mixmin_vs_a2c8 | broad_public_success | new_won | 19.6816033 | 0.505761232 | 0.494238768 |
| top4 | sequence_axis_flank | e176_vs_e95_pending | 3 | e101_vs_mixmin | mixmin_relative_success | new_won | 20.1888097 | 0.505761232 | 0.494238768 |

## Leave-One-Known-Pair Stress

| set | view | heldout_pair | heldout_family | actual_direction | nearest_pair | nearest_family | pred_direction | correct | nearest_distance | min_distance_new_won | min_distance_new_lost | margin_new_won_minus_new_lost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| top16 | sequence_axis | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 7.81616813e-13 | 7.81616813e-13 | 5.86958025 | -5.86958025 |
| top16 | sequence_axis | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 2.61468704e-13 | 2.61468704e-13 | 1.04327435e-12 | -7.81805649e-13 |
| top16 | sequence_axis | e72_vs_e95 | q2s3_gate_fail | new_lost | mixmin_vs_a2c8 | broad_public_success | new_won | 0 | 15.4272694 | 15.4272694 | 15.9531585 | -0.525889114 |
| top16 | sequence_axis | e72_vs_mixmin | q2s3_gate_fail | new_lost | e101_vs_e95 | frontier_near_loss | new_lost | 1 | 6.91967061 | 6.91967061 | 6.91967061 | 1.54543045e-13 |
| top16 | sequence_axis | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 2.61628788e-13 | 2.61628788e-13 | 7.81634374e-13 | -5.20005586e-13 |
| top16 | sequence_axis | mixmin_vs_a2c8 | broad_public_success | new_won | e72_vs_e95 | q2s3_gate_fail | new_lost | 0 | 276.580326 | 279.975642 | 276.580326 | 3.39531594 |
| top16 | sequence_axis_flank | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 7.8237209e-13 | 7.8237209e-13 | 6.17317195 | -6.17317195 |
| top16 | sequence_axis_flank | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 2.61724202e-13 | 2.61724202e-13 | 1.04428476e-12 | -7.82560555e-13 |
| top16 | sequence_axis_flank | e72_vs_e95 | q2s3_gate_fail | new_lost | mixmin_vs_a2c8 | broad_public_success | new_won | 0 | 15.6793616 | 15.6793616 | 16.1588515 | -0.47948995 |
| top16 | sequence_axis_flank | e72_vs_mixmin | q2s3_gate_fail | new_lost | e101_vs_e95 | frontier_near_loss | new_lost | 1 | 7.25387374 | 7.25387374 | 7.25387374 | 1.58983937e-13 |
| top16 | sequence_axis_flank | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 2.6188413e-13 | 2.6188413e-13 | 7.82389634e-13 | -5.20505504e-13 |
| top16 | sequence_axis_flank | mixmin_vs_a2c8 | broad_public_success | new_won | e72_vs_e95 | q2s3_gate_fail | new_lost | 0 | 276.58814 | 279.986861 | 276.58814 | 3.39872097 |
| top16 | sequence_only | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 7.81514918e-13 | 7.81514918e-13 | 5.68822333 | -5.68822333 |
| top16 | sequence_only | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 2.61436216e-13 | 2.61436216e-13 | 1.04313965e-12 | -7.81703435e-13 |
| top16 | sequence_only | e72_vs_e95 | q2s3_gate_fail | new_lost | e72_vs_mixmin | q2s3_gate_fail | new_lost | 1 | 11.0516814 | 11.7816968 | 11.0516814 | 0.730015377 |
| top16 | sequence_only | e72_vs_mixmin | q2s3_gate_fail | new_lost | e101_vs_e95 | frontier_near_loss | new_lost | 1 | 6.75719249 | 6.75719249 | 6.75719249 | 1.58983937e-13 |
| top16 | sequence_only | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 2.6159722e-13 | 2.6159722e-13 | 7.81532481e-13 | -5.1993526e-13 |
| top16 | sequence_only | mixmin_vs_a2c8 | broad_public_success | new_won | e72_vs_e95 | q2s3_gate_fail | new_lost | 0 | 276.519752 | 279.894508 | 276.519752 | 3.37475538 |
| top33 | sequence_axis | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 2.67529452 | 2.67529452 | 7.73438445 | -5.05908993 |
| top33 | sequence_axis | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 3.06832346 | 3.06832346 | 3.36893411 | -0.300610642 |
| top33 | sequence_axis | e72_vs_e95 | q2s3_gate_fail | new_lost | mixmin_vs_a2c8 | broad_public_success | new_won | 0 | 13.6859169 | 13.6859169 | 15.7821183 | -2.09620138 |
| top33 | sequence_axis | e72_vs_mixmin | q2s3_gate_fail | new_lost | e72_vs_e95 | q2s3_gate_fail | new_lost | 1 | 21.1383165 | 23.4322536 | 21.1383165 | 2.29393712 |
| top33 | sequence_axis | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_e95 | frontier_near_loss | new_lost | 0 | 2.3222568 | 2.83436383 | 2.3222568 | 0.512107027 |
| top33 | sequence_axis | mixmin_vs_a2c8 | broad_public_success | new_won | e72_vs_e95 | q2s3_gate_fail | new_lost | 0 | 23.6167317 | 23.8256816 | 23.6167317 | 0.208949867 |
| top33 | sequence_axis_flank | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 2.69326395 | 2.69326395 | 7.8863668 | -5.19310285 |
| top33 | sequence_axis_flank | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 3.19547903 | 3.19547903 | 3.49897983 | -0.303500792 |
| top33 | sequence_axis_flank | e72_vs_e95 | q2s3_gate_fail | new_lost | mixmin_vs_a2c8 | broad_public_success | new_won | 0 | 14.0121744 | 14.0121744 | 15.8085288 | -1.79635435 |
| top33 | sequence_axis_flank | e72_vs_mixmin | q2s3_gate_fail | new_lost | e72_vs_e95 | q2s3_gate_fail | new_lost | 1 | 21.2097004 | 23.4837543 | 21.2097004 | 2.2740539 |
| top33 | sequence_axis_flank | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_e95 | frontier_near_loss | new_lost | 0 | 2.34300347 | 2.94779426 | 2.34300347 | 0.604790793 |
| top33 | sequence_axis_flank | mixmin_vs_a2c8 | broad_public_success | new_won | e72_vs_e95 | q2s3_gate_fail | new_lost | 0 | 24.5779301 | 24.8331196 | 24.5779301 | 0.255189477 |
| top33 | sequence_only | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 2.66629382 | 2.66629382 | 7.30526921 | -4.63897539 |
| top33 | sequence_only | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 3.02922559 | 3.02922559 | 3.30305481 | -0.273829219 |
| top33 | sequence_only | e72_vs_e95 | q2s3_gate_fail | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 10.456748 | 10.456748 | 11.3297073 | -0.87295922 |
| top33 | sequence_only | e72_vs_mixmin | q2s3_gate_fail | new_lost | e72_vs_e95 | q2s3_gate_fail | new_lost | 1 | 20.61862 | 23.0987009 | 20.61862 | 2.48008084 |
| top33 | sequence_only | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_e95 | frontier_near_loss | new_lost | 0 | 2.31222201 | 2.79017554 | 2.31222201 | 0.477953535 |
| top33 | sequence_only | mixmin_vs_a2c8 | broad_public_success | new_won | e72_vs_e95 | q2s3_gate_fail | new_lost | 0 | 17.7445719 | 19.1709183 | 17.7445719 | 1.42634639 |
| top4 | sequence_axis | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 2.60572544e-12 | 2.60572544e-12 | 6.84132374 | -6.84132374 |
| top4 | sequence_axis | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 8.77431751e-13 | 8.77431751e-13 | 3.48313356e-12 | -2.60570181e-12 |
| top4 | sequence_axis | e72_vs_e95 | q2s3_gate_fail | new_lost | e72_vs_mixmin | q2s3_gate_fail | new_lost | 1 | 67.2930739 | 67.5392662 | 67.2930739 | 0.246192327 |
| top4 | sequence_axis | e72_vs_mixmin | q2s3_gate_fail | new_lost | e101_vs_e95 | frontier_near_loss | new_lost | 1 | 9.06383451 | 9.06383451 | 9.06383451 | 3.30402372e-13 |
| top4 | sequence_axis | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 8.77431744e-13 | 8.77431744e-13 | 2.60553486e-12 | -1.72810312e-12 |
| top4 | sequence_axis | mixmin_vs_a2c8 | broad_public_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 52.1570109 | 52.1570109 | 52.1570109 | -2.5721647e-12 |
| top4 | sequence_axis_flank | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 2.60572544e-12 | 2.60572544e-12 | 7.24008319 | -7.24008319 |
| top4 | sequence_axis_flank | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 8.77431751e-13 | 8.77431751e-13 | 3.48313356e-12 | -2.60570181e-12 |
| top4 | sequence_axis_flank | e72_vs_e95 | q2s3_gate_fail | new_lost | e72_vs_mixmin | q2s3_gate_fail | new_lost | 1 | 67.3412108 | 67.7755866 | 67.3412108 | 0.434375784 |
| top4 | sequence_axis_flank | e72_vs_mixmin | q2s3_gate_fail | new_lost | e101_vs_e95 | frontier_near_loss | new_lost | 1 | 9.46971065 | 9.46971065 | 9.46971065 | 3.16191517e-13 |
| top4 | sequence_axis_flank | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 8.77431744e-13 | 8.77431744e-13 | 2.60553486e-12 | -1.72810312e-12 |
| top4 | sequence_axis_flank | mixmin_vs_a2c8 | broad_public_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 52.1570109 | 52.1570109 | 52.1570109 | -2.5721647e-12 |
| top4 | sequence_only | e101_vs_e95 | frontier_near_loss | new_lost | e95_vs_mixmin | frontier_hardtail_success | new_won | 0 | 2.60353722e-12 | 2.60353722e-12 | 6.63905863 | -6.63905863 |
| top4 | sequence_only | e101_vs_mixmin | mixmin_relative_success | new_won | e95_vs_mixmin | frontier_hardtail_success | new_won | 1 | 8.7669524e-13 | 8.7669524e-13 | 3.48020883e-12 | -2.60351359e-12 |
| top4 | sequence_only | e72_vs_e95 | q2s3_gate_fail | new_lost | mixmin_vs_a2c8 | broad_public_success | new_won | 0 | 59.3993016 | 59.3993016 | 59.9419649 | -0.542663243 |
| top4 | sequence_only | e72_vs_mixmin | q2s3_gate_fail | new_lost | e101_vs_e95 | frontier_near_loss | new_lost | 1 | 8.86574875 | 8.86574875 | 8.86574875 | 3.37507799e-13 |
| top4 | sequence_only | e95_vs_mixmin | frontier_hardtail_success | new_won | e101_vs_mixmin | mixmin_relative_success | new_won | 1 | 8.76695234e-13 | 8.76695234e-13 | 2.60334648e-12 | -1.72665125e-12 |
| top4 | sequence_only | mixmin_vs_a2c8 | broad_public_success | new_won | e101_vs_e95 | frontier_near_loss | new_lost | 0 | 9.61510978 | 9.61510978 | 9.61510978 | 1.26654243e-12 |

## Interpretation

- E176's critical-cell motif has weak winner-neighbor evidence, but the nearest-anchor rule misses important known anchors, especially the exact E101/E95 frontier boundary in several views.
- This kills the shortcut "use row/order motif nearest anchors as a decisive-cell selector."
- The result does not demote E176: E195's information-value argument remains stronger because E176 is a public sensor with a pre-registered decoder, not a motif-certified expected-score file.

## Decision

No submission is created. Keep `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the next public sensor. E196 adds only a weak anatomy note: E176's top4/top16 motifs are closest to a known loss in the best high-accuracy views, while top33 motifs drift toward mixmin. That split is anatomy, not an actionable selector.
