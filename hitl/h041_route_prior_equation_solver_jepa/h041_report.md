# H041 Route-Prior Public/Private Equation Solver HS-JEPA

## Question

Can H040 route state help when used inside hidden public-subset equation inference, rather than as a post-hoc edit gate?

## Public-equation fit

- known public sensors used: `21`

- best route-prior LOFO MAE: `0.000132093`

- best uniform LOFO MAE: `0.000187170`

- route LOFO gain vs uniform: `0.000055077`


Top config families:

| q_source | row_prior | subset_size | label_mode | particles | best_mae | median_mae | best_spearman | lofo_mae | lofo_max_abs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h041_route_public_hardmix | h041_support_public | 155 | sample | 18 | 0.000775747 | 0.001640720 | 0.923308271 | 0.000132093 | 0.000412954 |
| posterior_vector_mid | h041_public_x_transition | 125 | sample | 18 | 0.000643191 | 0.001550720 | 0.935338346 | 0.000138825 | 0.000431745 |
| h012posterior | h041_public_route | 230 | sample | 18 | 0.000339283 | 0.001334416 | 0.953383459 | 0.000138988 | 0.000839616 |
| h041_route_transition_q | h041_public_x_transition | 190 | sample | 18 | 0.000567335 | 0.001219281 | 0.977443609 | 0.000140534 | 0.000643807 |
| h041_route_transition_q | h041_uncertain_public | 190 | sample | 18 | 0.000387467 | 0.001104506 | 0.959398496 | 0.000140620 | 0.000558951 |
| posterior_vector_mid | h041_public_route_sharp | 155 | sample | 18 | 0.000474781 | 0.002316389 | 0.954887218 | 0.000142404 | 0.000791510 |
| posterior_vector_mid | h041_uncertain_public | 230 | sample | 18 | 0.000465680 | 0.002158912 | 0.954887218 | 0.000154515 | 0.000422310 |
| posterior_vector_mid | h041_transition_exception | 190 | sample | 18 | 0.000575153 | 0.001542989 | 0.972932331 | 0.000154577 | 0.000568122 |
| h041_route_transition_q | h041_public_not_private | 125 | sample | 18 | 0.000690279 | 0.001653709 | 0.954887218 | 0.000155070 | 0.000823549 |
| h041_route_transition_q | h041_transition_exception | 230 | sample | 18 | 0.000434971 | 0.001050088 | 0.969924812 | 0.000160647 | 0.001392495 |
| h041_route_public_hardmix | h041_public_route | 230 | sample | 18 | 0.000318029 | 0.001236976 | 0.971428571 | 0.000164104 | 0.001081887 |
| h012posterior | h041_transition_exception_sharp | 190 | sample | 18 | 0.000592177 | 0.002548530 | 0.948872180 | 0.000164361 | 0.000720870 |
| h041_route_public_hardmix | h041_support_public | 190 | sample | 18 | 0.000374259 | 0.001542564 | 0.959398496 | 0.000166733 | 0.000642616 |
| h041_route_transition_q | h041_support_public | 125 | sample | 18 | 0.000807847 | 0.003193206 | 0.930827068 | 0.000166752 | 0.000741133 |
| h041_route_public_q | h041_world_public_prior | 190 | sample | 18 | 0.000523749 | 0.001363790 | 0.966917293 | 0.000168638 | 0.000547258 |
| h041_route_transition_q | h041_private_inverse | 155 | sample | 18 | 0.000558835 | 0.001094253 | 0.929323308 | 0.000168724 | 0.000588377 |


Top worlds:

| particle | q_source | row_prior | subset_size | label_mode | actual_mae | selection_mae | lofo_mae | spearman | posterior_weight |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8780 | posterior_vector_mid | h041_world_public_prior | 230 | sample | 0.000212924 | 0.000317148 | 0.000192254 | 0.945864662 | 0.027101883 |
| 15173 | h041_route_transition_q | h041_reliable_transition | 190 | sample | 0.000280707 | 0.000357555 | 0.000172974 | 0.945864662 | 0.021735258 |
| 19731 | h041_route_public_hardmix | h041_transition_exception_sharp | 230 | sample | 0.000267170 | 0.000363504 | 0.000192283 | 0.939849624 | 0.021040389 |
| 20651 | h041_route_public_hardmix | h041_support_public | 190 | sample | 0.000374259 | 0.000366834 | 0.000166733 | 0.875187970 | 0.020661232 |
| 3544 | h012posterior | h041_public_route | 230 | sample | 0.000339283 | 0.000386086 | 0.000138988 | 0.887218045 | 0.018599235 |
| 20410 | h041_route_public_hardmix | h041_uncertain_public | 190 | sample | 0.000386789 | 0.000388159 | 0.000195381 | 0.947368421 | 0.018389811 |
| 19726 | h041_route_public_hardmix | h041_transition_exception_sharp | 230 | sample | 0.000331861 | 0.000388624 | 0.000192283 | 0.914285714 | 0.018343150 |
| 14225 | h041_route_transition_q | h041_uncertain_public | 190 | sample | 0.000387467 | 0.000393526 | 0.000140620 | 0.911278195 | 0.017858650 |
| 13303 | h041_route_transition_q | h041_transition_exception | 230 | sample | 0.000434971 | 0.000421501 | 0.000160647 | 0.969924812 | 0.015328393 |
| 6811 | posterior_vector_mid | h041_public_route_sharp | 155 | sample | 0.000474781 | 0.000447386 | 0.000142404 | 0.954887218 | 0.013307694 |
| 19016 | h041_route_public_hardmix | h041_public_route | 230 | sample | 0.000318029 | 0.000453394 | 0.000164104 | 0.971428571 | 0.012878192 |
| 25402 | h041_e247_phase_q | h041_public_route_sharp | 190 | sample | 0.000493177 | 0.000463046 | 0.000201652 | 0.957894737 | 0.012216935 |
| 8778 | posterior_vector_mid | h041_world_public_prior | 230 | sample | 0.000382898 | 0.000468120 | 0.000192254 | 0.936842105 | 0.011883050 |
| 20168 | h041_route_public_hardmix | h041_public_not_private | 190 | sample | 0.000409766 | 0.000468123 | 0.000184112 | 0.957894737 | 0.011882861 |


Top posterior rows:

| row | subject_id | sleep_date | world_public_prob | mean_cell_world_score | public_route_score | transition_exception_route_score | private_memory_route_score | support_count | memory_disagree_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 144 | id06 | 2024-08-14 00:00:00 | 0.990778201 | 1.165332298 | 0.942760000 | 0.866520000 | 0.214480000 | 7 | 1.000000000 |
| 163 | id07 | 2024-07-25 00:00:00 | 0.982373042 | 0.137502177 | 0.759000000 | 0.872280000 | 0.161560000 | 6 | 0.714285714 |
| 52 | id02 | 2024-10-09 00:00:00 | 0.981745349 | 0.685208322 | 0.848360000 | 0.884440000 | 0.358880000 | 5 | 0.714285714 |
| 70 | id03 | 2024-09-16 00:00:00 | 0.981639291 | 1.564332957 | 0.885720000 | 0.751280000 | 0.286560000 | 6 | 0.571428571 |
| 143 | id06 | 2024-08-13 00:00:00 | 0.981587358 | 1.886043593 | 0.950360000 | 0.824240000 | 0.378480000 | 7 | 1.000000000 |
| 146 | id06 | 2024-08-20 00:00:00 | 0.981173096 | 1.270054423 | 0.872280000 | 0.787160000 | 0.542240000 | 7 | 0.714285714 |
| 148 | id06 | 2024-08-22 00:00:00 | 0.980253084 | 0.777460631 | 0.886440000 | 0.818120000 | 0.397800000 | 6 | 0.714285714 |
| 29 | id02 | 2024-08-28 00:00:00 | 0.979860500 | 0.366770235 | 0.686520000 | 0.742120000 | 0.269000000 | 5 | 0.571428571 |
| 128 | id06 | 2024-07-07 00:00:00 | 0.979822620 | 0.564372832 | 0.847560000 | 0.784680000 | 0.404840000 | 6 | 0.714285714 |
| 140 | id06 | 2024-07-21 00:00:00 | 0.979089559 | 1.733905030 | 0.922920000 | 0.779400000 | 0.318480000 | 6 | 0.571428571 |
| 141 | id06 | 2024-08-10 00:00:00 | 0.978345473 | 1.151359469 | 0.930840000 | 0.873480000 | 0.208760000 | 6 | 0.714285714 |
| 147 | id06 | 2024-08-21 00:00:00 | 0.976380823 | 0.993424010 | 0.898840000 | 0.726000000 | 0.482160000 | 7 | 0.714285714 |
| 48 | id02 | 2024-10-05 00:00:00 | 0.975392568 | 0.580451071 | 0.918680000 | 0.785400000 | 0.554080000 | 7 | 0.571428571 |
| 124 | id05 | 2024-11-17 00:00:00 | 0.975276817 | 0.127787756 | 0.747720000 | 0.713320000 | 0.665160000 | 6 | 0.714285714 |


Candidate ranking:

| candidate_id | family | alpha | changed_cells_vs_h012 | route_equation_delta_vs_h012 | h012posterior_delta_vs_h012 | h036world_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | pred_gain_top1200_sum | h041_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h041_route_celltop_k420_a0.18_c420_c5275704 | route_celltop_k420 | 0.180000000 | 420 | -0.001074309 | -0.000205969 | -0.000487601 | 0.004066028 | 0.250000000 | -3.847057412 | 3.847143127 | 0.486250000 |
| h041_route_celltop_k240_a0.18_c240_d3754d22 | route_celltop_k240 | 0.180000000 | 240 | -0.000698919 | -0.000191584 | -0.000438276 | 0.003775390 | 0.250000000 | -4.370573495 | 4.370659210 | 0.610729167 |
| h041_phase_preserve_support_k260_a0.36_c227_633b4ea9 | phase_preserve_support_k260 | 0.360000000 | 227 | -0.000849927 | -0.000247174 | -0.000594330 | 0.006289125 | 0.250000000 | -4.435562826 | 4.436234255 | 0.612812500 |
| h041_route_celltop_k420_a0.32_c420_95136443 | route_celltop_k420 | 0.320000000 | 420 | -0.001731595 | -0.000163348 | -0.000621655 | 0.007208851 | 0.250000000 | -3.971938596 | 3.972452881 | 0.622187500 |
| h041_phase_preserve_support_k520_a0.36_c371_04f75682 | phase_preserve_support_k520 | 0.360000000 | 371 | -0.001129894 | -0.000293423 | -0.000703130 | 0.006572093 | 0.250000000 | -2.985754419 | 2.986425848 | 0.648750000 |
| h041_phase_preserve_support_k260_a0.2_c227_0681d840 | phase_preserve_support_k260 | 0.200000000 | 227 | -0.000515234 | -0.000211961 | -0.000418850 | 0.003494527 | 0.250000000 | -4.311543360 | 4.311586217 | 0.672187500 |
| h041_route_celltop_k700_a0.18_c700_0e15cde3 | route_celltop_k700 | 0.180000000 | 700 | -0.001438017 | -0.000197369 | -0.000486454 | 0.004417779 | 0.250000000 | -1.228885243 | 1.228970957 | 0.685729167 |
| h041_route_celltop_k240_a0.32_c240_89faa46a | route_celltop_k240 | 0.320000000 | 240 | -0.001119027 | -0.000160282 | -0.000563853 | 0.006702054 | 0.250000000 | -4.490112887 | 4.490627172 | 0.697708333 |
| h041_phase_preserve_support_k520_a0.2_c371_a671fc2b | phase_preserve_support_k520 | 0.200000000 | 371 | -0.000681752 | -0.000243959 | -0.000486799 | 0.003653796 | 0.250000000 | -2.836542753 | 2.836585610 | 0.705000000 |
| h041_phase_preserve_support_k900_a0.36_c515_668443b2 | phase_preserve_support_k900 | 0.360000000 | 515 | -0.001262028 | -0.000317396 | -0.000773467 | 0.006789876 | 0.250000000 | -1.724108661 | 1.724780089 | 0.725833333 |
| h041_phase_preserve_support_k260_a0.55_c227_d615e483 | phase_preserve_support_k260 | 0.550000000 | 227 | -0.001171032 | -0.000189425 | -0.000684741 | 0.009604484 | 0.250000000 | -4.502146653 | 4.502860938 | 0.737291667 |
| h041_route_celltop_k1050_a0.18_c1050_01fde696 | route_celltop_k1050 | 0.180000000 | 1050 | -0.001695635 | -0.000188372 | -0.000491985 | 0.004761030 | 0.250000000 | 0.940811407 | -0.940725693 | 0.745104167 |
| h041_phase_preserve_support_k900_a0.2_c515_87890d42 | phase_preserve_support_k900 | 0.200000000 | 515 | -0.000760669 | -0.000260437 | -0.000529854 | 0.003778199 | 0.250000000 | -1.513460824 | 1.513503681 | 0.749791667 |
| h041_phase_preserve_support_k520_a0.55_c371_d04cf682 | phase_preserve_support_k520 | 0.550000000 | 371 | -0.001563055 | -0.000239631 | -0.000826557 | 0.010034036 | 0.250000000 | -3.044699390 | 3.045413675 | 0.765416667 |
| h041_route_celltop_k140_a0.18_c140_dc9fed9b | route_celltop_k140 | 0.180000000 | 140 | -0.000387505 | -0.000179853 | -0.000374399 | 0.003562853 | 0.250000000 | -4.741939780 | 4.742025494 | 0.798229167 |
| h041_phase_preserve_support_k900_a0.55_c515_91a184c5 | phase_preserve_support_k900 | 0.550000000 | 515 | -0.001746967 | -0.000265954 | -0.000921033 | 0.010362721 | 0.250000000 | -1.767153136 | 1.767867422 | 0.819062500 |
| h041_route_celltop_k140_a0.32_c140_c126ba9c | route_celltop_k140 | 0.320000000 | 140 | -0.000611516 | -0.000162388 | -0.000477139 | 0.006334780 | 0.250000000 | -4.845877431 | 4.846391717 | 0.872708333 |
| h041_route_rows_r95_top3_a0.22_c285_d7e8ece5 | route_rows_r95_top3 | 0.220000000 | 285 | -0.000628332 | -0.000177290 | -0.000421969 | 0.004322601 | 0.250000000 | -3.137813394 | 3.137884822 | 0.873229167 |


Decision:

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | family | route_equation_delta_vs_h012 | h012posterior_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | rowperm_real_top1200_sum | rowperm_p_perm_ge_real | route_lofo_gain_vs_uniform | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| do_not_promote | False | h041_route_celltop_k420_a0.18_c420_c5275704 | submission_h041_route_celltop_k420_a0.18_c420_c5275704.csv | /Users/kbsoo/Downloads/cl2/hitl/h041_route_prior_equation_solver_jepa/submission_h041_route_celltop_k420_a0.18_c420_c5275704.csv | route_celltop_k420 | -0.001074309 | -0.000205969 | 0.004066028 | 0.250000000 | -3.847057412 | 3.847143127 | 0.290000000 | 0.000055077 | H024 pre-H012 does not prefer over H012; H024 support below 55% |


## Interpretation
- If route LOFO improves over uniform but candidates fail H024/H025, route is a real public-subset prior but not enough to decode actions.
- If route LOFO does not improve, H040's route latent is only descriptive and should not guide future equation solvers.
- Promotion requires both equation-level evidence and action-health survival because H012 is a locked public-equation phase point.
