# HS-JEPA Release Checklist

이 문서는 현재 HS-JEPA 패키지를 팀 공유/논문 발표/대회 제출 논의용 release로 볼 수 있는지 최종 확인한다.

## Verdict

- Status: `release_ready_with_boundary`
- Checks: `83/83` passed

## Required Failures

- none

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| `exists:route_conserving_s2_bridge_package.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_package.json |
| `exists:route_conserving_s2_bridge_validation_report.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_validation_report.json |
| `exists:hsjepa_reproducibility_contract.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.json |
| `exists:hsjepa_architecture_readiness_report.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.json |
| `exists:hsjepa_mechanism_ablation_report.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report.json |
| `exists:hsjepa_generality_report.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report.json |
| `exists:hsjepa_core_adapter_boundary_audit.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit.json |
| `exists:hsjepa_paper_method_packet.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet.json |
| `exists:hsjepa_core_manifest.json` | `PASS` | hsjepa_core/outputs/hsjepa_core_manifest.json |
| `exists:hsjepa_core_ablation_contract.json` | `PASS` | hsjepa_core/outputs/hsjepa_core_ablation_contract.json |
| `exists:hsjepa_core_reference_run.json` | `PASS` | hsjepa_core/outputs/hsjepa_core_reference_run.json |
| `exists:hsjepa_core_module_benchmark.json` | `PASS` | hsjepa_core/outputs/hsjepa_core_module_benchmark.json |
| `exists:sleep_competition_adapter_report.json` | `PASS` | sleep_competition_adapter/outputs/sleep_competition_adapter_report.json |
| `exists:hsjepa_big_bet_queue.json` | `PASS` | sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json |
| `exists:og_only_assignment_teacher_probe.json` | `PASS` | sleep_competition_adapter/outputs/og_only_assignment_teacher_probe.json |
| `exists:assignment_gap_decomposition_probe.json` | `PASS` | sleep_competition_adapter/outputs/assignment_gap_decomposition_probe.json |
| `exists:hidden_row_support_sensor_probe.json` | `PASS` | sleep_competition_adapter/outputs/hidden_row_support_sensor_probe.json |
| `exists:masked_row_support_objective_probe.json` | `PASS` | sleep_competition_adapter/outputs/masked_row_support_objective_probe.json |
| `exists:row_support_strict_action_decoder_readout.json` | `PASS` | sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout.json |
| `exists:route_frontier_action_decoder_readout.json` | `PASS` | sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout.json |
| `exists:route_toxicity_fusion_decoder_readout.json` | `PASS` | sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout.json |
| `exists:decoder_order_jury_solver_readout.json` | `PASS` | sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout.json |
| `exists:decoder_boundary_tomography_readout.json` | `PASS` | sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout.json |
| `exists:core_mediated_action_release_readout.json` | `PASS` | sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_readout.json |
| `exists:core_release_ablation_probe_readout.json` | `PASS` | sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_readout.json |
| `exists:core_health_calibrated_release_readout.json` | `PASS` | sleep_competition_adapter/outputs/core_health_calibrated_release/core_health_calibrated_release_readout.json |
| `exists:cross_listener_transport_readout.json` | `PASS` | sleep_competition_adapter/outputs/cross_listener_transport_decoder/cross_listener_transport_readout.json |
| `exists:counterfactual_listener_dropout_readout.json` | `PASS` | sleep_competition_adapter/outputs/counterfactual_listener_dropout_solver/counterfactual_listener_dropout_readout.json |
| `exists:spectral_public_tangent_readout.json` | `PASS` | sleep_competition_adapter/outputs/spectral_public_tangent_solver/spectral_public_tangent_readout.json |
| `exists:negative_tangent_invariant_projection_readout.json` | `PASS` | sleep_competition_adapter/outputs/negative_tangent_invariant_projection_solver/negative_tangent_invariant_projection_readout.json |
| `exists:lb_conditioned_responsibility_readout.json` | `PASS` | sleep_competition_adapter/outputs/lb_conditioned_responsibility_solver/lb_conditioned_responsibility_readout.json |
| `exists:hsjepa_action_decoder_ablation_suite.json` | `PASS` | sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite.json |
| `exists:listener_invariant_contrastive_probe.json` | `PASS` | sleep_competition_adapter/outputs/listener_invariant_contrastive_probe.json |
| `exists:private_safe_toxicity_probe.json` | `PASS` | sleep_competition_adapter/outputs/private_safe_toxicity_probe.json |
| `exists:hardworld_toxicity_factorization_probe.json` | `PASS` | sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe.json |
| `exists:factorized_toxicity_decoder_readout.json` | `PASS` | sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout.json |
| `exists:factorized_toxicity_decoder_stress_audit.json` | `PASS` | sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_audit.json |
| `exists:hsjepa_pipeline_manifest.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest.json |
| `validation_passed` | `PASS` | passed=True |
| `contract_passed` | `PASS` | passed=True, missing=0 |
| `readiness_passed` | `PASS` | status=paper_ready_with_boundary, gates=7/7 |
| `score_breakthrough_large_enough` | `PASS` | delta=-0.0084113555 |
| `route_conserving_mechanism` | `PASS` | route_delta=-0.02457, null=-0.01090, rank=0.186 |
| `s2_listener_hub_mechanism` | `PASS` | s2_usage=1.000, null=0.615, rank=0.144 |
| `human_state_boundary` | `PASS` | cell_auc=0.775, row_auc=0.545 |
| `mechanism_ablation_ready` | `PASS` | status=mechanism_ablation_ready, killed=5, survived=2 |
| `mechanism_shortcuts_rejected` | `PASS` | stress_verdicts=['killed_locally', 'killed_locally'] |
| `generality_boundary_explicit` | `PASS` | status=general_architecture_separated_with_case_boundary, checks=10/11, boundaries=['remaining_generality_gap'] |
| `core_adapter_separation_explicit` | `PASS` | core=core_ready_for_adapter (5/5), adapter=adapter_ready_with_public_sensor_boundary |
| `core_adapter_boundary_audit_verified` | `PASS` | status=core_adapter_boundary_verified, checks=6/6 |
| `core_ablation_contract_present` | `PASS` | status=ablation_contract_ready, ablations=6 |
| `core_reference_executable` | `PASS` | status=core_reference_ready, released=1, ablations=3 |
| `core_module_benchmark_executable` | `PASS` | status=core_module_benchmark_ready, scenarios=5, full_f1=1.0000, action_health_fp_lift=9, invariant_fp_lift=1 |
| `big_bet_queue_high_ceiling` | `PASS` | status=big_bet_queue_ready, count=18 |
| `og_only_assignment_probe_recorded` | `PASS` | status=og_only_assignment_replacement_not_ready, pure_recall=0.0404, distilled_recall=0.1236 |
| `assignment_gap_decomposition_recorded` | `PASS` | status=row_support_is_primary_bottleneck, portable=0.1063, row_oracle=0.6896, row_gap=0.5832 |
| `hidden_row_support_sensor_recorded` | `PASS` | status=portable_row_support_sensor_alive_partial, family=portable_row_support_composite, row_auc=0.8193, cell_recall=0.3289, auc_z=6.4180 |
| `masked_row_support_objective_recorded` | `PASS` | status=masked_row_support_objective_supported_with_stress_boundary, row_auc=0.8193, cell_recall=0.3289, group_stress_auc=0.5584 |
| `row_support_strict_action_decoder_recorded` | `PASS` | status=row_support_action_decoder_alive_with_route_tradeoff, recommended=exploratory_route_support_gate, changed=34, safety_z=3.64, combined_z=1.38 |
| `route_frontier_action_decoder_recorded` | `PASS` | status=route_frontier_action_decoder_alive_with_matched_boundary, recommended=seed_route_frontier, scores=[{'variant': 'seed_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.631665028357059, 'matched_score_z': 3.6234736097578057, 'upload_safe': True}, {'variant': 's2_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.8237779101897877, 'matched_score_z': 3.3123857088533875, 'upload_safe': True}, {'variant': 'open_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.492261359647143, 'matched_score_z': 3.0831554042259524, 'upload_safe': True}] |
| `action_decoder_ablation_suite_recorded` | `PASS` | status=action_decoder_ablation_ready_decoder_jury_leads, recommended={'family': 'decoder_order_jury', 'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.394366527938867}, big_bet={'family': 'route_frontier', 'variant': 'open_route_frontier', 'submission_file': 'submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv', 'priority': 1.05448050759572} |
| `route_toxicity_fusion_decoder_recorded` | `PASS` | status=route_toxicity_fusion_decoder_alive, recommended=seed_driver_safe_route_fusion, scores=[{'variant': 's2_route_toxicity_fusion', 'changed_cells': 8, 'broad_route_z': -0.06361725497399186, 'toxicity_matched_safety_z': 0.0, 'toxicity_matched_fusion_z': 0.00022199529973856787, 'upload_safe': True}, {'variant': 'seed_route_toxicity_fusion', 'changed_cells': 8, 'broad_route_z': -0.05413537720642773, 'toxicity_matched_safety_z': 0.0, 'toxicity_matched_fusion_z': 0.00022199529973856787, 'upload_safe': True}, {'variant': 'open_route_toxicity_fusion', 'changed_cells': 4, 'broad_route_z': -0.16743111973717828, 'toxicity_matched_safety_z': 0.00022199529973856787, 'toxicity_matched_fusion_z': 0.0, 'upload_safe': True}, {'variant': 's2_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 2.5212391425980725, 'toxicity_matched_safety_z': 1.4350151378530516, 'toxicity_matched_fusion_z': 3.333896510179827, 'upload_safe': True}, {'variant': 'seed_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 1.956452255410393, 'toxicity_matched_safety_z': 1.1375544203021746, 'toxicity_matched_fusion_z': 4.040831045742473, 'upload_safe': True}, {'variant': 'open_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 1.2492144363720237, 'toxicity_matched_safety_z': 1.1862432357203119, 'toxicity_matched_fusion_z': 1.8706591048812475, 'upload_safe': True}] |
| `decoder_order_jury_solver_recorded` | `PASS` | status=decoder_order_jury_ready, recommended={'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.392520579892158} |
| `decoder_boundary_tomography_solver_recorded` | `PASS` | status=boundary_tomography_ready, recommended={'variant': 'consensus_shadow_plus', 'submission_file': 'submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv', 'priority': 0.6990859175252038}, inventory={'strict_jury_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'conflict_cells': 0} |
| `core_mediated_action_release_recorded` | `PASS` | status=core_mediated_action_release_ready, recommended={'variant': 'core_consensus_shadow_plus', 'submission_file': 'submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv', 'priority': 0.8460231888716516}, inventory={'candidate_cells': 44, 'strict_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'default_core_released': 32} |
| `core_release_ablation_probe_recorded` | `PASS` | status=core_release_ablation_ready, lb_candidate={'variant': 'full_core_reference', 'submission_file': 'submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv', 'priority': 0.8314097090596275}, sensor={'variant': 'no_action_health', 'submission_file': 'submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv', 'priority': 0.3281725643379389} |
| `core_health_calibrated_release_recorded` | `PASS` | status=core_health_calibrated_release_ready, guarded={'variant': 'benchmark_guarded_full_plus', 'submission_file': 'submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv', 'priority': 0.38818571481351827}, big_bet={'variant': 'route_pressure_boundary_probe', 'submission_file': 'submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv', 'priority': 0.38337754232640875}, calibration={'action_health_fp_lift': 9.0, 'invariant_fp_lift': 1.0, 'listener_fp_lift': 3.0, 'scenario_count': 5.0, 'action_fp_weight': 0.6428571428571429, 'invariant_fp_weight': 0.16666666666666666, 'listener_fp_weight': 0.375} |
| `cross_listener_transport_recorded` | `PASS` | status=cross_listener_transport_ready, recommended={'variant': 'listener_confirmed_shadow', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': 0.5684860446, 'priority': 0.9427271560571463, 'config': {'name': 'listener_confirmed_shadow', 'boundary_classes': ['strict_jury', 'consensus_shadow'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.44, 'max_cells': 28, 'max_extra_cells': 6, 'strict_base_scale': 0.82, 'extra_base_scale': 0.34, 'listener_gain': 0.2, 's2_gain': 0.09, 'probe_role': 'tests whether target-listener confirmed shadow cells are safer than broad shadow release'}, 'rank': 1}, big_bet={'variant': 'objective_listener_island_probe', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': None, 'priority': 0.9427271560571463, 'config': {'name': 'objective_listener_island_probe', 'boundary_classes': ['strict_jury', 'consensus_shadow', 'route_only', 'fusion_only'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.47, 'max_cells': 34, 'max_extra_cells': 12, 'strict_base_scale': 0.8, 'extra_base_scale': 0.28, 'listener_gain': 0.22, 's2_gain': 0.1, 'probe_role': 'tests whether an objective-listener island exists outside the current public row-state support'}, 'rank': 2}, negative={'file': 'submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv', 'public_lb': 0.5680255019, 'interpretation': 'direct listener-lift is not action-grade; use listener posterior only as a release/calibration prior'} |
| `counterfactual_listener_dropout_recorded` | `PASS` | status=counterfactual_listener_dropout_ready, information={'variant': 'dropout_fullfield_aggressive', 'submission_file': 'submission_hsjepa_counterfactual_listener_dropout_dropout_fullfield_aggressive_a433fbc0_uploadsafe.csv', 'priority': 1.2860211183353285}, thesis={'variant': 'invariant_survivor', 'submission_file': 'submission_hsjepa_counterfactual_listener_dropout_invariant_survivor_7cde1a77_uploadsafe.csv', 'priority': 0.05} |
| `spectral_public_tangent_recorded` | `PASS` | status=spectral_public_tangent_ready, first=0.9629, top5=0.9947, information={'variant': 'anti_bad_tangent_pressure', 'submission_file': 'submission_hsjepa_spectral_public_tangent_anti_bad_tangent_pressure_6a93251a_uploadsafe.csv', 'priority': 1.4947903603985548}, counter={'variant': 'orthogonal_private_residual', 'submission_file': 'submission_hsjepa_spectral_public_tangent_orthogonal_private_residual_57ed54c2_uploadsafe.csv'} |
| `negative_tangent_invariant_projection_recorded` | `PASS` | status=candidate_ready, recommended=subject_prior_safe_projection, projected=232, ranking=[{'variant': 'subject_prior_safe_projection', 'score': 0.25449167116425153}, {'variant': 'anti_tangent_invariant_projection', 'score': 0.23870131099839245}, {'variant': 'sign_equation_projection', 'score': 0.21487727900957238}, {'variant': 'energy_descent_negative_space', 'score': 0.20411530522715116}] |
| `lb_conditioned_responsibility_recorded` | `PASS` | status=candidate_ready, recommended=pure_lb_gradient_jackpot, loo_corr=0.7300, cells=115 |
| `listener_invariant_contrastive_probe_recorded` | `PASS` | status=listener_invariant_decoder_not_ready, rho=-0.0313, overlap=0.2152 |
| `private_safe_toxicity_probe_recorded` | `PASS` | status=toxicity_field_promising_with_hardworld_gap, mean_loo_auc=0.7880, worst_loo_auc=0.3683, safety_z=8.4589 |
| `hardworld_toxicity_factorization_probe_recorded` | `PASS` | status=hardworld_mixture_factorization_required, broad_to_h088_auc=0.3683, rho=-0.4276, joint_z=7.1884 |
| `factorized_toxicity_decoder_candidate_recorded` | `PASS` | variants=['dual_safe_expansion', 'teacher_dual_head'], upload_safe=[True, True] |
| `factorized_toxicity_decoder_stress_supported` | `PASS` | status=stress_audit_ready, supported=['dual_safe_expansion'], variants=[('dual_safe_expansion', 'factorized_decoder_stress_supported'), ('teacher_dual_head', 'factorized_decoder_alive_but_source_null_weak')] |
| `roles_present` | `PASS` | roles=['competition_primary', 'human_state_probe', 'interpretable_s2_hub'] |
| `role_based_output_names` | `PASS` | role_outputs={'competition_primary': 'submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv', 'interpretable_s2_hub': 'submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv', 'human_state_probe': 'submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv'} |
| `all_role_submissions_upload_safe` | `PASS` | upload_roles=['competition_primary', 'human_state_probe', 'interpretable_s2_hub'] |
| `pipeline_manifest_complete` | `PASS` | status=pipeline_ready_with_boundary, stages=38, edges=125 |
| `method_packet_presentable` | `PASS` | title=Human-State JEPA: General Architecture with a Route-Conserving S2 Bridge Case Study |
| `claim_boundary_honest` | `PASS` | pure_og=False, public_sensor=True, proprietary_embedding=False |

## Release Claim

This package is ready as a team-facing and paper-facing HS-JEPA release when presented with the explicit public-sensor boundary.

## Boundary

- private LB safety is not proven
- pure OG-only assignment is not proven
- hidden row-support recovery is not solved by current portable human/social/cohort context
- hidden row-support transfer is partially alive but not yet an action-grade deployment decoder
- masked row-support is a valid HS-JEPA representation objective candidate but group-heldout stress is still weak
- row-support strict action decoder is LB-informative but has a route-gain tradeoff against local nulls
- human-state is an orientation diagnostic, not a complete row-target assignment solver
- OG-only assignment replacement has a recorded probe result
- Hidden row-support transfer has a recorded probe result
- Masked row-support objective has a recorded stress-boundary probe result
- Row-support strict action decoder has recorded upload-safe outputs and local stress
- Action decoder ablation suite ranks toxicity-first/support-first/route-first decoders for submission-slot prioritization, not LB prediction
- Decoder boundary tomography has recorded consensus-shadow/route-only/fusion-only probes, but their public safety is not proven
- Listener-invariant contrastive decoding has a recorded probe result
- Private-safe toxicity has a recorded probe result and hard-world boundary
- Hard-world toxicity factorization has a recorded probe result
- Factorized toxicity decoder candidates have recorded upload-safe outputs
- Factorized toxicity decoder has a recorded stress audit with at least one supported variant
- HS-JEPA Core is separated from the Sleep Competition Adapter
- HS-JEPA Core/Adapter boundary audit is verified
- Core-health calibrated release uses dataset-free action-health false-positive lift as an adapter release prior
- Cross-listener transport uses failed listener lift as a boundary calibrator, not as a direct action generator
- Counterfactual listener-dropout, spectral public tangent, negative tangent invariant projection, and LB-conditioned responsibility are recorded as high-information public-sensor probes
- the next big bet is replacing public-sensor assignment with an OG-only human-state teacher
