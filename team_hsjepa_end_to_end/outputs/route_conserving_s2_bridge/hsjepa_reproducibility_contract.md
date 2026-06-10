# HS-JEPA Reproducibility Contract

이 문서는 Route-Conserving S2 Bridge HS-JEPA가 어떤 입력을 쓰는지 명확히 분리한다.

핵심은 다음이다.

```text
OG raw data != public-LB sensor != generated action artifact
```

이 구분을 해야 논문에서 HS-JEPA의 representation claim과 competition-specific decoder claim을 과장하지 않을 수 있다.

## Status

- Contract passed: `True`
- Required missing records: `0`
- Public ledger rows: `26`
- Public ledger best LB: `0.5677475939`

## Category Summary

| Category | Records | Missing required | Meaning |
| --- | ---: | ---: | --- |
| `competition_anchor` | `21` | `0` | 현재 frontier와 listener/source action anchor |
| `derived_module` | `39` | `0` | 재생성 가능한 코드 모듈 |
| `generated_output` | `155` | `0` | one-command runner가 만든 산출물 |
| `og_raw` | `3` | `0` | 대회 원본 데이터 또는 원본 raw lifelog 묶음 |
| `public_sensor` | `7` | `0` | public LB 관측을 센서로 사용한 자산 |

## competition_anchor

| Role | Exists | Required | Name | Reason |
| --- | ---: | ---: | --- | --- |
| `current_best_anchor` | `True` | `True` | `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `toxicity_negative_sensor` | `True` | `True` | `submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `local_semantic_source_consensus` | `True` | `True` | `submission_h154_local_semantic_source_consensus_36eeef08_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `posterior_support_anchor` | `True` | `True` | `submission_h155_h061_all_cap1.0_k150_a1.15_0f87a1af_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `sparse_lossnull_anchor` | `True` | `True` | `submission_h158_sparse_lossnull_a1.8_b1.8_r1.0_k160_c7b38d35_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `competition_primary_output` | `True` | `True` | `submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `interpretable_s2_output` | `True` | `True` | `submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `human_state_probe_output` | `True` | `True` | `submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv` | frontier/source/output action anchor used by the packaged decoder |
| `source_action_submission` | `True` | `False` | `submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h074_antishortcut_inversion_816703df_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h075_antibad_transport_f6863945_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h126_coeffeq_3fe3eee4_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_bigbet1_public_listener_tomography_2687b6b6_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `source_action_submission` | `True` | `False` | `submission_h085_aug_public_equation_f154e2bb_uploadsafe.csv` | source/listener action proposal used by local semantic consensus if present |
| `h154_cell_candidates` | `True` | `True` | `hsjepa_jackpot/outputs/h154_cell_candidates.csv` | local semantic source-consensus cell table |
| `h061_cell_posterior` | `True` | `False` | `hitl/h061_h057_feedback_support_translator_jepa/h061_cell_posterior.csv` | posterior support feature for h155/h158 when available |

## derived_module

| Role | Exists | Required | Name | Reason |
| --- | ---: | ---: | --- | --- |
| `python_module` | `True` | `True` | `final_hsjepa_candidates/candidate_1_public_loss_sparse_tomography.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `hsjepa_jackpot/h154_local_semantic_source_consensus.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `hsjepa_jackpot/h155_h158_posterior_lossnull_jackpot.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `paper_hsjepa_core/stage_bridge_conservation_solver.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `paper_hsjepa_core/s2hub_bridge_solver.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `paper_hsjepa_core/s2hub_human_state_distillation.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/run_route_conserving_s2_bridge.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/audit_route_conserving_s2_bridge.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/validate_route_conserving_s2_bridge_package.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/run_full_team_hsjepa_package.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/build_hsjepa_architecture_readiness_report.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/build_hsjepa_mechanism_ablation_report.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/build_hsjepa_generality_report.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/audit_hsjepa_core_adapter_boundary.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/build_hsjepa_paper_method_packet.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/build_hsjepa_pipeline_manifest.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `team_hsjepa_end_to_end/build_hsjepa_release_checklist.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `hsjepa_core/core.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `hsjepa_core/build_core_architecture_manifest.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `hsjepa_core/run_core_reference_demo.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `hsjepa_core/run_core_module_benchmark.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/og_only_assignment_teacher_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/assignment_gap_decomposition_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/hidden_row_support_sensor_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/masked_row_support_objective_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/listener_invariant_contrastive_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/private_safe_toxicity_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/hardworld_toxicity_factorization_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/factorized_toxicity_decoder_candidate.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/factorized_toxicity_decoder_stress_audit.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/row_support_strict_action_decoder.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/route_frontier_action_decoder.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/route_toxicity_fusion_decoder.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/decoder_order_jury_solver.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/decoder_boundary_tomography_solver.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/core_mediated_action_release.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/core_release_ablation_probe.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/action_decoder_ablation_suite.py` | reproducible module in the role-based HS-JEPA package |
| `python_module` | `True` | `True` | `sleep_competition_adapter/build_sleep_competition_adapter_report.py` | reproducible module in the role-based HS-JEPA package |

## generated_output

| Role | Exists | Required | Name | Reason |
| --- | ---: | ---: | --- | --- |
| `team_package_output` | `True` | `True` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_package.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `True` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_evidence_table.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `True` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_stress_audit.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `True` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_stress_summary.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `True` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_validation_report.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `True` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_validation_report.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_team_handoff.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_team_handoff.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/route_conserving_s2_bridge_full_run_log.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_release_checklist.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_release_checklist_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_manifest.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_manifest_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_ablation_contract.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_ablation_contract_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_reference_run.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_reference_run_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_module_benchmark.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_module_benchmark_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `hsjepa_core/outputs/hsjepa_core_module_benchmark_cases.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/sleep_competition_adapter_report.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/og_only_assignment_teacher_probe.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/og_only_assignment_teacher_probe_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/og_only_assignment_teacher_ranked_cells.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/assignment_gap_decomposition_probe.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/assignment_gap_decomposition_probe_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/assignment_gap_decomposition_summary.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hidden_row_support_sensor_probe.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hidden_row_support_sensor_probe_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hidden_row_support_sensor_transfer_metrics.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/masked_row_support_objective_probe.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/masked_row_support_objective_probe_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/masked_row_support_objective_transfer_metrics.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/masked_row_support_objective_group_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/listener_invariant_contrastive_probe.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/listener_invariant_contrastive_probe_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/listener_invariant_contrastive_scored_bundles.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/private_safe_toxicity_probe.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/private_safe_toxicity_probe_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/private_safe_toxicity_scored_cells.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/private_safe_toxicity_loo_anchor_metrics.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/hardworld_toxicity_factorization_sectors.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_audit.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_audit_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_summary.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_audit.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_null_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/row_support_strict_action_decoder/submission_hsjepa_row_support_strict_route_support_gate_5ae5c515_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/row_support_strict_action_decoder/submission_hsjepa_row_support_exploratory_route_support_gate_97a2f8f5_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_row_support_strict_route_support_gate_5ae5c515_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_row_support_exploratory_route_support_gate_97a2f8f5_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_audit.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_null_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_frontier_action_decoder/submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_frontier_action_decoder/submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_frontier_action_decoder/submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_seed_route_frontier_1109c03f_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_s2_route_frontier_1d31aae8_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_audit.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_null_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_s2_route_toxicity_fusion_5ac75e44_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_seed_route_toxicity_fusion_ec01d56a_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_open_route_toxicity_fusion_bb0ca49f_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_s2_route_toxicity_fusion_5ac75e44_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_seed_route_toxicity_fusion_ec01d56a_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_open_route_toxicity_fusion_bb0ca49f_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_s2_driver_safe_route_fusion_6adf5b73_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_seed_driver_safe_route_fusion_62429a06_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_open_driver_safe_route_fusion_e50f0669_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_cells.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_null_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_route_majority_fusion_confirmed_1caf57fb_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_s2_pair_consensus_a71de0a7_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_order_jury_solver/submission_hsjepa_decoder_jury_seed_pair_consensus_e8a7ce4c_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_decoder_jury_route_majority_fusion_confirmed_1caf57fb_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_decoder_jury_s2_pair_consensus_a71de0a7_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_decoder_jury_seed_pair_consensus_e8a7ce4c_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_cells.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_null_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_boundary_dual_probe_528728bd_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_route_only_rescue_6c0f15eb_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_fusion_only_probe_8ce162dc_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/submission_hsjepa_boundary_tomography_consensus_shadow_all_soft_80850159_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_boundary_tomography_boundary_dual_probe_528728bd_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_boundary_tomography_route_only_rescue_6c0f15eb_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_boundary_tomography_fusion_only_probe_8ce162dc_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_boundary_tomography_consensus_shadow_all_soft_80850159_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_cells.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_null_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/submission_hsjepa_core_mediated_core_boundary_balanced_3b003319_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/submission_hsjepa_core_mediated_core_route_rescue_a37f6054_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_mediated_action_release/submission_hsjepa_core_mediated_core_jury_veto_a37f6054_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_mediated_core_boundary_balanced_3b003319_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_mediated_core_route_rescue_a37f6054_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_mediated_core_jury_veto_a37f6054_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_readout.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_readout_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_cells.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_null_stress.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/submission_hsjepa_core_ablation_invariant_only_6edb3385_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/submission_hsjepa_core_ablation_no_invariant_energy_363ccea6_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/core_release_ablation_probe/submission_hsjepa_core_ablation_no_listener_responsibility_d2560dc4_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_ablation_invariant_only_6edb3385_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_ablation_no_invariant_energy_363ccea6_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `submission_hsjepa_core_ablation_no_listener_responsibility_d2560dc4_uploadsafe.csv` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite.json` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite_ko.md` | generated by run_full_team_hsjepa_package.py |
| `team_package_output` | `True` | `False` | `sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite.csv` | generated by run_full_team_hsjepa_package.py |

## og_raw

| Role | Exists | Required | Name | Reason |
| --- | ---: | ---: | --- | --- |
| `train_metrics` | `True` | `True` | `data/ch2026_metrics_train.csv` | original train labels/metrics |
| `submission_sample` | `True` | `True` | `data/ch2026_submission_sample.csv` | original submission key/order contract |
| `raw_lifelog_items` | `True` | `True` | `data/ch2025_data_items` | original raw lifelog feature items |

## public_sensor

| Role | Exists | Required | Name | Reason |
| --- | ---: | ---: | --- | --- |
| `public_score_ledger` | `True` | `True` | `data_analytics/hsjepa_public_score_ledger.csv` | known public LB observations used as sensor |
| `public_loss_sensor_submission` | `True` | `False` | `submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv` | submission used to infer public loss/action toxicity when available |
| `public_loss_sensor_submission` | `True` | `False` | `submission_h042_target_Q2_phase_k45_s0.5_c45_50fc6607_uploadsafe.csv` | submission used to infer public loss/action toxicity when available |
| `public_loss_sensor_submission` | `True` | `False` | `submission_h088_dual_state_gate_c31cc15b_uploadsafe.csv` | submission used to infer public loss/action toxicity when available |
| `public_loss_sensor_submission` | `True` | `False` | `submission_h010_objective_s1s4_v2_uploadsafe.csv` | submission used to infer public loss/action toxicity when available |
| `public_loss_sensor_submission` | `True` | `False` | `submission_e323_5508f966_uploadsafe.csv` | submission used to infer public loss/action toxicity when available |
| `public_loss_sensor_submission` | `True` | `False` | `submission_h145_q3repair_2d818e46_uploadsafe.csv` | submission used to infer public loss/action toxicity when available |

## Interpretation Boundary

강하게 말할 수 있는 것:

```text
The package is end-to-end reproducible from the listed local OG data, public sensor ledger, and generated action anchors.
The decoder mechanism is tested by route-conservation and S2-hub stress audits.
```

조심해야 하는 것:

```text
This is not a pure OG-only model.
The competition decoder uses public-LB sensor observations.
The paper claim should separate human-state representation from competition-specific row-target assignment.
```
