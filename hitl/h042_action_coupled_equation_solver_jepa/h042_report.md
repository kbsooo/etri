# H042 Action-Coupled Public/Private Equation Solver HS-JEPA

## Question

Can the missing post-H012 decoder be learned by making upload action
coefficients first-class variables, rather than first estimating hidden
public labels and then pulling H012 toward a posterior?

## Action Decoder Fit

- known public sensors used: `21`
- action atoms: `36`
- best action decoder LOO MAE: `0.000665647`
- action decoder permutation p: `0.000000000`

Top action decoder fits:

| feature_set | alpha | n_features | loo_mae | loo_rmse | loo_spearman | loo_pair_acc |
| --- | --- | --- | --- | --- | --- | --- |
| coords_plus_world | 10.000000000 | 47 | 0.000665647 | 0.001056265 | 0.924675325 | 0.904761905 |
| compact | 1000.000000000 | 41 | 0.001013525 | 0.001348672 | 0.918181818 | 0.909523810 |
| compact | 1.000000000 | 41 | 0.001033968 | 0.003831283 | 0.954545455 | 0.933333333 |
| compact | 100.000000000 | 41 | 0.001063275 | 0.002521628 | 0.950649351 | 0.919047619 |
| coords_plus_world | 100.000000000 | 47 | 0.001065486 | 0.001380206 | 0.775324675 | 0.847619048 |
| compact | 10.000000000 | 41 | 0.001115004 | 0.003690682 | 0.979220779 | 0.957142857 |
| coords_plus_world | 1000.000000000 | 47 | 0.001192736 | 0.001547531 | 0.567532468 | 0.723809524 |
| compact | 0.010000000 | 41 | 0.001196858 | 0.004655609 | 0.980519481 | 0.961904762 |
| compact | 0.100000000 | 41 | 0.001216904 | 0.004484618 | 0.958441558 | 0.938095238 |
| coords_plus_world | 1.000000000 | 47 | 0.001271550 | 0.005188479 | 0.702597403 | 0.861904762 |
| coords | 1000.000000000 | 36 | 0.001284730 | 0.001689193 | -0.240259740 | 0.395238095 |
| coords_plus_world | 0.010000000 | 47 | 0.001556145 | 0.006945891 | 0.724675325 | 0.895238095 |
| coords | 100.000000000 | 36 | 0.001806249 | 0.003610793 | 0.389610390 | 0.614285714 |
| coords | 10.000000000 | 36 | 0.002077266 | 0.005026355 | 0.398701299 | 0.619047619 |

Top action atoms:

| name | group | changed_cells | strength |
| --- | --- | --- | --- |
| private_memory_k520 | private | 520 | 74.844568978 |
| private_memory_k260 | private | 260 | 71.919688592 |
| private_memory_k120 | private | 120 | 68.713888486 |
| private_rollback_k520 | private | 520 | 50.810454493 |
| private_rollback_k260 | private | 260 | 50.633640125 |
| private_rollback_k120 | private | 120 | 50.436067982 |
| phase_support_k520 | phase | 520 | 25.430406738 |
| phase_support_k260 | phase | 260 | 25.271294783 |
| phase_support_k120 | phase | 120 | 25.051814332 |
| public_cell_k700 | public | 700 | 23.583313491 |
| exception_world_k340 | exception | 340 | 23.485690442 |
| route_row_all_r70 | row | 490 | 23.439341644 |
| public_cell_k420 | public | 420 | 23.375294534 |
| exception_world_k180 | exception | 180 | 23.363996516 |
| route_row_top3_r70 | row | 210 | 23.355398720 |
| exception_world_k90 | exception | 90 | 23.220816951 |

## Candidate Ranking

| candidate_id | family | component_count | changed_cells_vs_h012 | pre_h012_action_margin_vs_h012_median | pre_h012_action_support_better_than_h012 | route_equation_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | h042_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h042_joint_public_private_public_cell_k240_private_rollback_k260_0.24_0.1_c380_3a0a9b30 | joint_public_private_public_cell_k240_private_rollback_k260_0.24_0.1 | 2 | 380 | 0.000793299 | 0.333333333 | -0.000537053 | 0.002010668 | 0.250000000 | -5.144375790 | 0.632908163 |
| h042_joint_public_private_public_cell_k120_private_rollback_k120_0.46_0.18_c171_cc041b63 | joint_public_private_public_cell_k120_private_rollback_k120_0.46_0.18 | 2 | 171 | 0.000790132 | 0.333333333 | -0.000405637 | 0.003333225 | 0.250000000 | -4.647969613 | 0.778265306 |
| h042_joint_public_private_public_cell_k420_private_rollback_k120_0.24_0.1_c451_8da57b14 | joint_public_private_public_cell_k420_private_rollback_k120_0.24_0.1 | 2 | 451 | 0.000951549 | 0.333333333 | -0.000919428 | 0.002272581 | 0.250000000 | -4.677893786 | 0.787500000 |
| h042_joint_public_private_phase_support_k120_private_rollback_k260_0.34_0.14_c297_9e8d0f40 | joint_public_private_phase_support_k120_private_rollback_k260_0.34_0.14 | 2 | 297 | 0.000672837 | 0.333333333 | -0.000280739 | 0.002404988 | 0.250000000 | -5.315768470 | 0.832644558 |
| h042_joint_public_exception_public_cell_k240_exception_world_k180_0.24_0.12_c248_55b5d3e6 | joint_public_exception_public_cell_k240_exception_world_k180_0.24_0.12 | 2 | 248 | 0.000963037 | 0.250000000 | -0.000683683 | 0.005503239 | 0.250000000 | -4.920437910 | 0.867784864 |
| h042_joint_public_private_public_cell_k240_private_rollback_k120_0.16_0.08_c278_40c23bf4 | joint_public_private_public_cell_k240_private_rollback_k120_0.16_0.08 | 2 | 278 | 0.000640894 | 0.333333333 | -0.000393249 | 0.001293142 | 0.333333333 | -5.220576692 | 0.887236395 |
| h042_triple_phase_exception_private_phase_support_k520_exception_world_k90_private_memory_k120_0 | triple_phase_exception_private_phase_support_k520_exception_world_k90_private_memory_k120_0.18_0.1_0.06 | 3 | 555 | 0.000957461 | 0.250000000 | -0.000599658 | 0.002729694 | 0.250000000 | -1.610336886 | 0.889047619 |
| h042_joint_public_private_public_cell_k120_private_rollback_k120_0.34_0.14_c171_bf7c37b1 | joint_public_private_public_cell_k120_private_rollback_k120_0.34_0.14 | 2 | 171 | 0.000678088 | 0.333333333 | -0.000320681 | 0.002509754 | 0.250000000 | -4.633312102 | 0.892963435 |
| h042_triple_phase_exception_private_phase_support_k260_exception_world_k180_private_memory_k120 | triple_phase_exception_private_phase_support_k260_exception_world_k180_private_memory_k120_0.18_0.1_0.06 | 3 | 323 | 0.000760650 | 0.250000000 | -0.000473163 | 0.002581921 | 0.250000000 | -4.177317932 | 0.897427721 |
| h042_joint_public_private_public_cell_k420_private_rollback_k120_0.16_0.08_c451_24178a7f | joint_public_private_public_cell_k420_private_rollback_k120_0.16_0.08 | 2 | 451 | 0.000689654 | 0.333333333 | -0.000630315 | 0.001524484 | 0.333333333 | -4.631460371 | 0.899927721 |
| h042_joint_public_private_phase_support_k260_private_rollback_k260_0.34_0.14_c404_0deb1169 | joint_public_private_phase_support_k260_private_rollback_k260_0.34_0.14 | 2 | 404 | 0.000890881 | 0.333333333 | -0.000744896 | 0.002670977 | 0.250000000 | -4.041861202 | 0.903626701 |
| h042_target_route_target_Q2_phase_k150_target_S3_phase_k150_0.18_0.12_c255_7056f113 | target_route_target_Q2_phase_k150_target_S3_phase_k150_0.18_0.12 | 2 | 255 | 0.000333044 | 0.333333333 | -0.000145217 | 0.000809204 | 0.250000000 | 0.047149742 | 0.956079932 |
| h042_joint_public_private_public_cell_k240_private_rollback_k120_0.34_0.14_c278_aa5a6e5e | joint_public_private_public_cell_k240_private_rollback_k120_0.34_0.14 | 2 | 278 | 0.000912950 | 0.333333333 | -0.000775496 | 0.002795910 | 0.250000000 | -5.272787577 | 0.978184524 |
| h042_joint_public_private_phase_support_k260_private_memory_k120_0.16_0.08_c305_51f36c0b | joint_public_private_phase_support_k260_private_memory_k120_0.16_0.08 | 2 | 305 | 0.000325934 | 0.333333333 | -0.000305453 | 0.001334506 | 0.416666667 | -4.059853498 | 0.980131803 |
| h042_joint_public_private_phase_support_k520_private_rollback_k120_0.34_0.14_c551_2706eae0 | joint_public_private_phase_support_k520_private_rollback_k120_0.34_0.14 | 2 | 551 | 0.001140361 | 0.333333333 | -0.001090792 | 0.003076222 | 0.250000000 | -1.438821920 | 0.982278912 |
| h042_joint_public_exception_public_cell_k700_exception_world_k90_0.16_0.08_c700_901b4a19 | joint_public_exception_public_cell_k700_exception_world_k90_0.16_0.08 | 2 | 700 | 0.001094660 | 0.250000000 | -0.000898055 | 0.004015589 | 0.250000000 | -1.522985932 | 0.991271259 |
| h042_triple_phase_exception_private_phase_support_k520_exception_world_k180_private_memory_k120 | triple_phase_exception_private_phase_support_k520_exception_world_k180_private_memory_k120_0.18_0.1_0.06 | 3 | 569 | 0.000995924 | 0.333333333 | -0.000642120 | 0.002779222 | 0.250000000 | -1.698706917 | 0.995280612 |
| h042_joint_public_private_public_cell_k700_private_rollback_k120_0.16_0.08_c721_efcc6df5 | joint_public_private_public_cell_k700_private_rollback_k120_0.16_0.08 | 2 | 721 | 0.000738850 | 0.333333333 | -0.000846590 | 0.001806434 | 0.333333333 | -1.920433476 | 0.995471939 |

## Decision

| decision | promote | selected_candidate_id | selected_file | selected_resolved_path | family | components | pre_h012_action_margin_vs_h012_median | pre_h012_action_support_better_than_h012 | route_equation_delta_vs_h012 | pre_h012_h024_margin_vs_h012_median | pre_h012_h024_support_better_than_h012 | h025_score | rowperm_real_top1200_sum | rowperm_p_perm_ge_real | best_action_decoder_loo_mae | action_decoder_perm_p | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| do_not_promote | False | h042_joint_public_private_public_cell_k240_private_rollback_k260_0.24_0.1_c380_3a0a9b30 | submission_h042_joint_public_private_public_cell_k240_private_rollback_k260_0.24_0.1_c380_3a0a9b30.csv | /Users/kbsoo/Downloads/cl2/hitl/h042_action_coupled_equation_solver_jepa/submission_h042_joint_public_private_public_cell_k240_private_rollback_k260_0.24_0.1_c380_3a0a9b30.csv | joint_public_private_public_cell_k240_private_rollback_k260_0.24_0.1 | public_cell_k240:0.24+private_rollback_k260:0.1 | 0.000793299 | 0.333333333 | -0.000537053 | 0.002010668 | 0.250000000 | -5.144375790 | 5.144390075 | 0.146666667 | 0.000665647 | 0.000000000 | action-coupled decoder does not predict enough gain; action decoder support below 50%; H024 pre-H012 does not prefer candidate; H024 support below 55% |

## Interpretation

- If the action decoder beats permutation nulls but candidates fail H024/H025,
  action response is learnable but still not sufficient to identify a safe
  upload action.
- If the action decoder itself fails, known public LB actions do not support
  a stable route-action equation at this granularity.
- Promotion requires action-equation gain, route-world gain, H024 agreement,
  and H025 row/action-health agreement together.
