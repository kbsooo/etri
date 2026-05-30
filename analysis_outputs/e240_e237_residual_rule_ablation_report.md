# E240 E237 Residual-Rule Ablation

## Question

Can the E239 residual-energy motif replace the learned E237 Q3 cell selector with a simple public-free rule?

## Control Selectors

| candidate_id | rule_family | pruned_cells | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | actual_support_gain_vs_e224 | q3_top1_over_abs_expected | q3_adverse_delta | overlap_e237 | overlap_e230_swing25 | overlap_e230_risk21 | e230_gate | e237_like_gate | e237_like_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| control_e237_learned_cell25 | control | 25 | -0.000005612 | 0.000576400 | 0.006450259 | -0.000005612 | 0.000553281 | 0.005439067 | 0.747139811 | 0.001639237 | 25 | 13 | 11 | True | True | 0.058941606 |
| control_e230_risk21 | control | 21 | -0.000067892 | 0.000444730 | 0.021076971 | -0.000067892 | 0.000421879 | 0.017510382 | 0.469524979 | 0.001770907 | 11 | 11 | 21 | True | True | 0.055664125 |
| control_e230_swing25 | control | 25 | 0.000023308 | 0.000633168 | 0.009873471 | 0.000023308 | 0.000612558 | 0.008182936 | 0.490395991 | 0.001582469 | 13 | 25 | 11 | True | False | 0.060843558 |

## Simple-Rule Ranking

| candidate_id | rule_family | pruned_cells | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | actual_support_gain_vs_e224 | q3_top1_over_abs_expected | q3_adverse_delta | overlap_e237 | overlap_e230_swing25 | overlap_e230_risk21 | e230_gate | e237_like_gate | e237_like_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| simple_pc10_top25 | simple | 25 | -0.000062119 | 0.000594489 | 0.016747154 | -0.000062119 | 0.000573879 | 0.013846657 | 0.485060793 | 0.001621148 | 14 | 18 | 13 | True | True | 0.069485298 |
| global_e239_combo25 | combined | 25 | -0.000067196 | 0.000550992 | 0.014862033 | -0.000067196 | 0.000541143 | 0.012289634 | 0.471346320 | 0.001664645 | 12 | 14 | 12 | True | True | 0.065695591 |
| top50_amp_then_resid_combo25 | top50_residual | 25 | -0.000047923 | 0.000575462 | 0.015351938 | -0.000047923 | 0.000565613 | 0.012661420 | 0.528017394 | 0.001640175 | 13 | 15 | 13 | True | True | 0.065483593 |
| top50_amp_then_nn25 | top50_residual | 25 | -0.000026258 | 0.000593089 | 0.011727599 | -0.000026258 | 0.000581644 | 0.009685125 | 0.610535533 | 0.001622548 | 16 | 15 | 12 | True | True | 0.063923267 |
| top50_amp_then_resid_abs25 | top50_residual | 25 | -0.000026457 | 0.000575137 | 0.011513988 | -0.000026457 | 0.000563692 | 0.009520011 | 0.609662394 | 0.001640500 | 14 | 15 | 11 | True | True | 0.062138798 |
| global_amp_resid_combo25 | combined | 25 | -0.000057936 | 0.000525465 | 0.013502227 | -0.000057936 | 0.000510999 | 0.011208569 | 0.496972571 | 0.001690172 | 12 | 13 | 11 | True | True | 0.061737760 |
| global_e215_e208_combo25 | combined | 25 | -0.000038381 | 0.000542740 | 0.013011916 | -0.000038381 | 0.000528275 | 0.010785951 | 0.561440504 | 0.001672897 | 13 | 14 | 12 | True | True | 0.060688281 |
| simple_resid_abs_top25 | simple | 25 | -0.000037922 | 0.000362654 | 0.004356968 | -0.000037922 | 0.000342563 | 0.003751339 | 0.563154736 | 0.001852983 | 6 | 6 | 5 | True | True | 0.041923026 |
| simple_nn_dist_top25 | simple | 25 | -0.000038335 | 0.000354167 | 0.003471613 | -0.000038335 | 0.000340710 | 0.002974025 | 0.584910666 | 0.001861470 | 8 | 6 | 4 | True | True | 0.041061345 |

## Simple E237-Like Gate Passes

| candidate_id | rule_family | pruned_cells | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | actual_support_gain_vs_e224 | q3_top1_over_abs_expected | q3_adverse_delta | overlap_e237 | overlap_e230_swing25 | overlap_e230_risk21 | e230_gate | e237_like_gate | e237_like_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| simple_pc10_top25 | simple | 25 | -0.000062119 | 0.000594489 | 0.016747154 | -0.000062119 | 0.000573879 | 0.013846657 | 0.485060793 | 0.001621148 | 14 | 18 | 13 | True | True | 0.069485298 |
| global_e239_combo25 | combined | 25 | -0.000067196 | 0.000550992 | 0.014862033 | -0.000067196 | 0.000541143 | 0.012289634 | 0.471346320 | 0.001664645 | 12 | 14 | 12 | True | True | 0.065695591 |
| top50_amp_then_resid_combo25 | top50_residual | 25 | -0.000047923 | 0.000575462 | 0.015351938 | -0.000047923 | 0.000565613 | 0.012661420 | 0.528017394 | 0.001640175 | 13 | 15 | 13 | True | True | 0.065483593 |
| top50_amp_then_nn25 | top50_residual | 25 | -0.000026258 | 0.000593089 | 0.011727599 | -0.000026258 | 0.000581644 | 0.009685125 | 0.610535533 | 0.001622548 | 16 | 15 | 12 | True | True | 0.063923267 |
| top50_amp_then_resid_abs25 | top50_residual | 25 | -0.000026457 | 0.000575137 | 0.011513988 | -0.000026457 | 0.000563692 | 0.009520011 | 0.609662394 | 0.001640500 | 14 | 15 | 11 | True | True | 0.062138798 |
| global_amp_resid_combo25 | combined | 25 | -0.000057936 | 0.000525465 | 0.013502227 | -0.000057936 | 0.000510999 | 0.011208569 | 0.496972571 | 0.001690172 | 12 | 13 | 11 | True | True | 0.061737760 |
| global_e215_e208_combo25 | combined | 25 | -0.000038381 | 0.000542740 | 0.013011916 | -0.000038381 | 0.000528275 | 0.010785951 | 0.561440504 | 0.001672897 | 13 | 14 | 12 | True | True | 0.060688281 |
| simple_resid_abs_top25 | simple | 25 | -0.000037922 | 0.000362654 | 0.004356968 | -0.000037922 | 0.000342563 | 0.003751339 | 0.563154736 | 0.001852983 | 6 | 6 | 5 | True | True | 0.041923026 |
| simple_nn_dist_top25 | simple | 25 | -0.000038335 | 0.000354167 | 0.003471613 | -0.000038335 | 0.000340710 | 0.002974025 | 0.584910666 | 0.001861470 | 8 | 6 | 4 | True | True | 0.041061345 |

## Overlap

| selector_id | rule_family | reference | selected_n | reference_n | intersection | jaccard |
| --- | --- | --- | --- | --- | --- | --- |
| control_e230_risk21 | control | e230_risk21 | 21 | 21 | 21 | 1.000000000 |
| control_e230_risk21 | control | e230_swing25 | 21 | 25 | 11 | 0.314285714 |
| control_e230_risk21 | control | e237 | 21 | 25 | 11 | 0.314285714 |
| control_e230_swing25 | control | e230_risk21 | 25 | 21 | 11 | 0.314285714 |
| control_e230_swing25 | control | e230_swing25 | 25 | 25 | 25 | 1.000000000 |
| control_e230_swing25 | control | e237 | 25 | 25 | 13 | 0.351351351 |
| control_e237_learned_cell25 | control | e230_risk21 | 25 | 21 | 11 | 0.314285714 |
| control_e237_learned_cell25 | control | e230_swing25 | 25 | 25 | 13 | 0.351351351 |
| control_e237_learned_cell25 | control | e237 | 25 | 25 | 25 | 1.000000000 |
| global_amp_resid_combo25 | combined | e230_risk21 | 25 | 21 | 11 | 0.314285714 |
| global_amp_resid_combo25 | combined | e230_swing25 | 25 | 25 | 13 | 0.351351351 |
| global_amp_resid_combo25 | combined | e237 | 25 | 25 | 12 | 0.315789474 |
| global_e215_e208_combo25 | combined | e230_risk21 | 25 | 21 | 12 | 0.352941176 |
| global_e215_e208_combo25 | combined | e230_swing25 | 25 | 25 | 14 | 0.388888889 |
| global_e215_e208_combo25 | combined | e237 | 25 | 25 | 13 | 0.351351351 |
| global_e239_combo25 | combined | e230_risk21 | 25 | 21 | 12 | 0.352941176 |
| global_e239_combo25 | combined | e230_swing25 | 25 | 25 | 14 | 0.388888889 |
| global_e239_combo25 | combined | e237 | 25 | 25 | 12 | 0.315789474 |
| simple_nn_dist_top25 | simple | e230_risk21 | 25 | 21 | 4 | 0.095238095 |
| simple_nn_dist_top25 | simple | e230_swing25 | 25 | 25 | 6 | 0.136363636 |
| simple_nn_dist_top25 | simple | e237 | 25 | 25 | 8 | 0.190476190 |
| simple_pc10_top25 | simple | e230_risk21 | 25 | 21 | 13 | 0.393939394 |
| simple_pc10_top25 | simple | e230_swing25 | 25 | 25 | 18 | 0.562500000 |
| simple_pc10_top25 | simple | e237 | 25 | 25 | 14 | 0.388888889 |
| simple_resid_abs_top25 | simple | e230_risk21 | 25 | 21 | 5 | 0.121951220 |
| simple_resid_abs_top25 | simple | e230_swing25 | 25 | 25 | 6 | 0.136363636 |
| simple_resid_abs_top25 | simple | e237 | 25 | 25 | 6 | 0.136363636 |
| top50_amp_then_nn25 | top50_residual | e230_risk21 | 25 | 21 | 12 | 0.352941176 |
| top50_amp_then_nn25 | top50_residual | e230_swing25 | 25 | 25 | 15 | 0.428571429 |
| top50_amp_then_nn25 | top50_residual | e237 | 25 | 25 | 16 | 0.470588235 |
| top50_amp_then_resid_abs25 | top50_residual | e230_risk21 | 25 | 21 | 11 | 0.314285714 |
| top50_amp_then_resid_abs25 | top50_residual | e230_swing25 | 25 | 25 | 15 | 0.428571429 |
| top50_amp_then_resid_abs25 | top50_residual | e237 | 25 | 25 | 14 | 0.388888889 |
| top50_amp_then_resid_combo25 | top50_residual | e230_risk21 | 25 | 21 | 13 | 0.393939394 |
| top50_amp_then_resid_combo25 | top50_residual | e230_swing25 | 25 | 25 | 15 | 0.428571429 |
| top50_amp_then_resid_combo25 | top50_residual | e237 | 25 | 25 | 13 | 0.351351351 |

## Target Breakdown

| candidate_id | target | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- | --- |
| control_e230_risk21 | Q3 | 229 | -0.000180264 | 0.001770907 | 0.492256130 | 0.469524979 |
| control_e230_risk21 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| control_e230_swing25 | Q3 | 225 | -0.000089063 | 0.001582469 | 0.470538218 | 0.490395991 |
| control_e230_swing25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| control_e237_learned_cell25 | Q3 | 225 | -0.000117983 | 0.001639237 | 0.464254276 | 0.747139811 |
| control_e237_learned_cell25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| global_amp_resid_combo25 | Q3 | 225 | -0.000170308 | 0.001690172 | 0.477917736 | 0.496972571 |
| global_amp_resid_combo25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| global_e215_e208_combo25 | Q3 | 225 | -0.000150752 | 0.001672897 | 0.476947021 | 0.561440504 |
| global_e215_e208_combo25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| global_e239_combo25 | Q3 | 225 | -0.000179567 | 0.001664645 | 0.480503895 | 0.471346320 |
| global_e239_combo25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| simple_nn_dist_top25 | Q3 | 225 | -0.000150706 | 0.001861470 | 0.459977950 | 0.584910666 |
| simple_nn_dist_top25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| simple_pc10_top25 | Q3 | 225 | -0.000174490 | 0.001621148 | 0.484168631 | 0.485060793 |
| simple_pc10_top25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| simple_resid_abs_top25 | Q3 | 225 | -0.000150293 | 0.001852983 | 0.461508425 | 0.563154736 |
| simple_resid_abs_top25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| top50_amp_then_nn25 | Q3 | 225 | -0.000138630 | 0.001622548 | 0.474382131 | 0.610535533 |
| top50_amp_then_nn25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| top50_amp_then_resid_abs25 | Q3 | 225 | -0.000138828 | 0.001640500 | 0.474004538 | 0.609662394 |
| top50_amp_then_resid_abs25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |
| top50_amp_then_resid_combo25 | Q3 | 225 | -0.000160295 | 0.001640175 | 0.481446525 | 0.528017394 |
| top50_amp_then_resid_combo25 | S4 | 105 | -0.000510980 | 0.001185138 | 0.481218875 | 0.165385780 |

## Decision

- Simple rule `simple_pc10_top25` passed the E237-like gate. This weakens the learned-cell claim and should be used only as a diagnostic until E237 public feedback is known.
- No submission is created from E240.
