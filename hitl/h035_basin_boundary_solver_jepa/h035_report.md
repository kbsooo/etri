# H035 Basin-Boundary Solver HS-JEPA

## Question

H035 asks whether H012 is an editable row-target identity basin. It keeps the public-equation posterior direction, but swaps H012 support cells under target/row/support-count constraints before action-health stress.

## Route Fit

| n | mae | rmse | pred_min | pred_median | pred_max | target_min | target_median | target_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4262 | 0.000938787 | 0.001165757 | 0.011126055 | 0.016379230 | 0.032548316 | 0.009811799 | 0.016231420 | 0.033173893 |

## Generated Candidate Summary

| family | preserve | n | best_q_delta | best_route_margin | best_basin_score |
| --- | --- | --- | --- | --- | --- |
| swap | support_count | 216 | -0.000283191 | 0.013908583 | 0.010734391 |
| swap | row | 117 | -0.000286222 | 0.015266957 | 0.010843490 |
| swap | target | 216 | -0.000272973 | 0.014651648 | 0.010900471 |
| soften_tail | support | 36 | -0.000172570 | 0.027720251 | 0.013151107 |

## Top Candidate Actions

| candidate_id | family | preserve | drop_metric | add_metric | k | alpha | changed_cells_vs_h012 | max_abs_prob_vs_h012 | q_loss_delta_vs_h012 | route_mean_margin_pred | pre_state_margin_vs_h012_pred | pre_state_mean | h035_action_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| swap_support_count_drop_memory_conflict_to_add_no_h012_k7_a0.58 | swap | support_count | drop_memory_conflict | add_no_h012 | 7 | 0.580000000 | 1206 | 0.084415982 | 0.000512108 | 0.017292336 | 0.012214437 | 0.576654930 | 0.021381226 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_no_h012_k7_a0.58_63c6a3d9.csv |
| swap_support_count_drop_memory_conflict_to_add_public_vector_k7_a0.58 | swap | support_count | drop_memory_conflict | add_public_vector | 7 | 0.580000000 | 1206 | 0.084415982 | 0.000512108 | 0.017302373 | 0.012214256 | 0.576654749 | 0.021385562 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_public_vector_k7_a0.58_7f99427b.csv |
| swap_support_count_drop_memory_conflict_to_add_memory_public_k7_a0.58 | swap | support_count | drop_memory_conflict | add_memory_public | 7 | 0.580000000 | 1206 | 0.084415982 | 0.000511775 | 0.017365723 | 0.012217938 | 0.576658431 | 0.021417635 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_memory_public_k7_a0.58_a636898f.csv |
| swap_target_drop_memory_conflict_to_add_memory_public_k7_a0.58 | swap | target | drop_memory_conflict | add_memory_public | 7 | 0.580000000 | 1207 | 0.084415982 | 0.000520486 | 0.017478670 | 0.012196609 | 0.576637102 | 0.021451181 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_memory_public_k7_a0.58_d9d7784c.csv |
| swap_target_drop_memory_conflict_to_add_no_h012_k7_a0.58 | swap | target | drop_memory_conflict | add_no_h012 | 7 | 0.580000000 | 1207 | 0.084415982 | 0.000520837 | 0.017497877 | 0.012198087 | 0.576638580 | 0.021461425 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_no_h012_k7_a0.58_86d9fbba.csv |
| swap_target_drop_memory_conflict_to_add_public_vector_k7_a0.58 | swap | target | drop_memory_conflict | add_public_vector | 7 | 0.580000000 | 1207 | 0.084415982 | 0.000520733 | 0.017493019 | 0.012211646 | 0.576652139 | 0.021472761 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_public_vector_k7_a0.58_4d9316d9.csv |
| swap_support_count_drop_memory_conflict_to_add_no_h012_k14_a0.58 | swap | support_count | drop_memory_conflict | add_no_h012 | 14 | 0.580000000 | 1212 | 0.084415982 | 0.000535517 | 0.017192197 | 0.012358937 | 0.576799430 | 0.021494856 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_no_h012_k14_a0.58_40079c62.csv |
| swap_support_count_drop_memory_conflict_to_add_public_vector_k14_a0.58 | swap | support_count | drop_memory_conflict | add_public_vector | 14 | 0.580000000 | 1212 | 0.084415982 | 0.000534959 | 0.017162594 | 0.012386198 | 0.576826691 | 0.021508600 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_public_vector_k14_a0.58_4267d5b0.csv |
| swap_support_count_drop_memory_conflict_to_add_memory_public_k14_a0.58 | swap | support_count | drop_memory_conflict | add_memory_public | 14 | 0.580000000 | 1212 | 0.084415982 | 0.000534869 | 0.017213751 | 0.012374234 | 0.576814727 | 0.021519626 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_memory_public_k14_a0.58_85dac99b.csv |
| swap_target_drop_memory_conflict_to_add_public_vector_k14_a0.58 | swap | target | drop_memory_conflict | add_public_vector | 14 | 0.580000000 | 1214 | 0.084415982 | 0.000546683 | 0.017402300 | 0.012327992 | 0.576768485 | 0.021564366 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_public_vector_k14_a0.58_36531ae4.csv |
| swap_row_drop_memory_conflict_to_add_public_vector_k28_a0.58 | swap | row | drop_memory_conflict | add_public_vector | 28 | 0.580000000 | 1212 | 0.056598509 | 0.000509101 | 0.017354197 | 0.012369586 | 0.576810079 | 0.021569160 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_row_drop_memory_conflict_to_add_public_vector_k28_a0.58_3be92b4e.csv |
| swap_target_drop_memory_conflict_to_add_no_h012_k14_a0.58 | swap | target | drop_memory_conflict | add_no_h012 | 14 | 0.580000000 | 1214 | 0.084415982 | 0.000546889 | 0.017467250 | 0.012305485 | 0.576745978 | 0.021571159 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_no_h012_k14_a0.58_db774af0.csv |
| swap_target_drop_memory_conflict_to_add_memory_public_k14_a0.58 | swap | target | drop_memory_conflict | add_memory_public | 14 | 0.580000000 | 1214 | 0.084415982 | 0.000546260 | 0.017467412 | 0.012321692 | 0.576762185 | 0.021587219 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_memory_public_k14_a0.58_2db57c64.csv |
| swap_row_drop_boundary_to_add_public_vector_k28_a0.58 | swap | row | drop_boundary | add_public_vector | 28 | 0.580000000 | 1212 | 0.189622758 | 0.000856116 | 0.016566152 | 0.012596988 | 0.577037482 | 0.021841888 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_row_drop_boundary_to_add_public_vector_k28_a0.58_33170904.csv |
| swap_support_count_drop_memory_conflict_to_add_memory_public_k28_a0.58 | swap | support_count | drop_memory_conflict | add_memory_public | 28 | 0.580000000 | 1225 | 0.084415982 | 0.000584278 | 0.017275134 | 0.012802763 | 0.577243256 | 0.022006071 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_memory_public_k28_a0.58_fbd8bda2.csv |
| swap_support_count_drop_memory_conflict_to_add_public_vector_k28_a0.58 | swap | support_count | drop_memory_conflict | add_public_vector | 28 | 0.580000000 | 1225 | 0.084415982 | 0.000585163 | 0.017272209 | 0.012808415 | 0.577248908 | 0.022010716 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_public_vector_k28_a0.58_fdc845f5.csv |
| swap_support_count_drop_memory_conflict_to_add_no_h012_k28_a0.58 | swap | support_count | drop_memory_conflict | add_no_h012 | 28 | 0.580000000 | 1225 | 0.084415982 | 0.000585906 | 0.017358708 | 0.012770170 | 0.577210663 | 0.022011656 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_support_count_drop_memory_conflict_to_add_no_h012_k28_a0.58_02906313.csv |
| swap_target_drop_boundary_to_add_memory_public_k7_a0.58 | swap | target | drop_boundary | add_memory_public | 7 | 0.580000000 | 1207 | 0.087565878 | 0.000571512 | 0.017643912 | 0.012784538 | 0.577225032 | 0.022131328 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_boundary_to_add_memory_public_k7_a0.58_bcc1e0fc.csv |
| swap_target_drop_boundary_to_add_no_h012_k7_a0.58 | swap | target | drop_boundary | add_no_h012 | 7 | 0.580000000 | 1207 | 0.087565878 | 0.000571863 | 0.017664150 | 0.012786300 | 0.577226793 | 0.022142320 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_boundary_to_add_no_h012_k7_a0.58_88bc5740.csv |
| swap_target_drop_boundary_to_add_public_vector_k7_a0.58 | swap | target | drop_boundary | add_public_vector | 7 | 0.580000000 | 1207 | 0.087565878 | 0.000571759 | 0.017658261 | 0.012799426 | 0.577239920 | 0.022152760 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_boundary_to_add_public_vector_k7_a0.58_d2cc8d38.csv |
| swap_target_drop_memory_conflict_to_add_public_vector_k28_a0.58 | swap | target | drop_memory_conflict | add_public_vector | 28 | 0.580000000 | 1228 | 0.087565878 | 0.000598387 | 0.017538040 | 0.012851825 | 0.577292319 | 0.022181379 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_public_vector_k28_a0.58_d504ec39.csv |
| swap_target_drop_memory_conflict_to_add_no_h012_k28_a0.58 | swap | target | drop_memory_conflict | add_no_h012 | 28 | 0.580000000 | 1228 | 0.087565878 | 0.000598558 | 0.017642981 | 0.012820396 | 0.577260889 | 0.022197233 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_no_h012_k28_a0.58_3f4929f9.csv |
| swap_target_drop_memory_conflict_to_add_memory_public_k28_a0.58 | swap | target | drop_memory_conflict | add_memory_public | 28 | 0.580000000 | 1228 | 0.087565878 | 0.000596870 | 0.017610426 | 0.012916630 | 0.577357123 | 0.022278226 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_target_drop_memory_conflict_to_add_memory_public_k28_a0.58_a8d6fcd9.csv |
| swap_row_drop_memory_conflict_to_add_public_vector_k56_a0.58 | swap | row | drop_memory_conflict | add_public_vector | 56 | 0.580000000 | 1240 | 0.084415982 | 0.000606075 | 0.017267582 | 0.013308588 | 0.577749081 | 0.022531126 | hitl/h035_basin_boundary_solver_jepa/submission_h035_swap_row_drop_memory_conflict_to_add_public_vector_k56_a0.58_a0e62f3c.csv |

## Boundary Audit

| generated_candidates | q_improving_vs_h012 | route_safe_count | pre_state_better_count | strict_gate_count | best_q_delta | best_route_margin | best_pre_state_margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 585 | 55 | 0 | 0 | 0 | -0.000286222 | 0.013908583 | 0.012196609 |

- best q-improving candidate: `swap_row_drop_memory_conflict_to_add_public_vector_k28_a0.82`, q delta `-0.000286222`, route margin `0.019320985`, pre-state margin `0.015982303`
- best route-margin candidate: `swap_support_count_drop_boundary_to_add_memory_public_k224_a0.58`, q delta `0.003616250`, route margin `0.013908583`, pre-state margin `0.015028310`

## Stress

- decision: `diagnostic_only_h012_basin_locked_no_swap_clears_stress`
- promoted path: `none`
- selected candidate: `swap_support_count_drop_memory_conflict_to_add_no_h012_k7_a0.58`
- selected q-loss delta vs H012: `0.000512108`
- selected route margin prediction: `0.017292336`
- selected pre-state margin vs H012 prediction: `0.012214437`
- pre-H012 public-score permutation p(lower margin): `0.660666667`
- H025 row-permutation p(higher top1200 gain): `0.610000000`
- real H025 top1200 gain: `-3.082300124`

## Interpretation

The solver found `55` posterior-improving swaps, so the public-equation posterior alone still has local directions. However, none survived the route/pre-state gates: route-safe count is `0` and pre-state-better count is `0`. The selected combined-score action is q-worse than H012, while the best q-improving action is still route/pre-state bad. That strengthens the locked-basin view: H012 is not safely editable by local support replacement even when target/row structure is preserved. The next big-bet should stop doing local swaps and solve the hidden public labels/subset jointly, or seek new external constraints on private/public split.

## Files

- `hitl/h035_basin_boundary_solver_jepa/h035_cell_state.csv`
- `hitl/h035_basin_boundary_solver_jepa/h035_route_model_fit.csv`
- `hitl/h035_basin_boundary_solver_jepa/h035_generated_basin_candidates.csv`
- `hitl/h035_basin_boundary_solver_jepa/h035_candidate_scores.csv`
- `hitl/h035_basin_boundary_solver_jepa/h035_selected_pre_h012_public_perm_stress.csv`
- `hitl/h035_basin_boundary_solver_jepa/h035_selected_h025_rowperm_stress.csv`
- `hitl/h035_basin_boundary_solver_jepa/h035_decision.csv`
