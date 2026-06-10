# HS-JEPA Release Checklist

이 문서는 현재 HS-JEPA 패키지를 팀 공유/논문 발표/대회 제출 논의용 release로 볼 수 있는지 최종 확인한다.

## Verdict

- Status: `release_ready_with_boundary`
- Checks: `41/41` passed

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
| `exists:hsjepa_paper_method_packet.json` | `PASS` | team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet.json |
| `exists:hsjepa_core_manifest.json` | `PASS` | hsjepa_core/outputs/hsjepa_core_manifest.json |
| `exists:hsjepa_core_ablation_contract.json` | `PASS` | hsjepa_core/outputs/hsjepa_core_ablation_contract.json |
| `exists:sleep_competition_adapter_report.json` | `PASS` | sleep_competition_adapter/outputs/sleep_competition_adapter_report.json |
| `exists:hsjepa_big_bet_queue.json` | `PASS` | sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json |
| `exists:og_only_assignment_teacher_probe.json` | `PASS` | sleep_competition_adapter/outputs/og_only_assignment_teacher_probe.json |
| `exists:listener_invariant_contrastive_probe.json` | `PASS` | sleep_competition_adapter/outputs/listener_invariant_contrastive_probe.json |
| `exists:private_safe_toxicity_probe.json` | `PASS` | sleep_competition_adapter/outputs/private_safe_toxicity_probe.json |
| `exists:hardworld_toxicity_factorization_probe.json` | `PASS` | sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe.json |
| `exists:factorized_toxicity_decoder_readout.json` | `PASS` | sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout.json |
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
| `generality_boundary_explicit` | `PASS` | status=general_architecture_separated_with_case_boundary, checks=5/6, boundaries=['remaining_generality_gap'] |
| `core_adapter_separation_explicit` | `PASS` | core=core_ready_for_adapter (5/5), adapter=adapter_ready_with_public_sensor_boundary |
| `core_ablation_contract_present` | `PASS` | status=ablation_contract_ready, ablations=6 |
| `big_bet_queue_high_ceiling` | `PASS` | status=big_bet_queue_ready, count=5 |
| `og_only_assignment_probe_recorded` | `PASS` | status=og_only_assignment_replacement_not_ready, pure_recall=0.0404, distilled_recall=0.1236 |
| `listener_invariant_contrastive_probe_recorded` | `PASS` | status=listener_invariant_decoder_not_ready, rho=-0.0313, overlap=0.2152 |
| `private_safe_toxicity_probe_recorded` | `PASS` | status=toxicity_field_promising_with_hardworld_gap, mean_loo_auc=0.7880, worst_loo_auc=0.3683, safety_z=8.4589 |
| `hardworld_toxicity_factorization_probe_recorded` | `PASS` | status=hardworld_mixture_factorization_required, broad_to_h088_auc=0.3683, rho=-0.4276, joint_z=7.1884 |
| `factorized_toxicity_decoder_candidate_recorded` | `PASS` | variants=['dual_safe_expansion', 'teacher_dual_head'], upload_safe=[True, True] |
| `roles_present` | `PASS` | roles=['competition_primary', 'human_state_probe', 'interpretable_s2_hub'] |
| `role_based_output_names` | `PASS` | role_outputs={'competition_primary': 'submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv', 'interpretable_s2_hub': 'submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv', 'human_state_probe': 'submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv'} |
| `all_role_submissions_upload_safe` | `PASS` | upload_roles=['competition_primary', 'human_state_probe', 'interpretable_s2_hub'] |
| `pipeline_manifest_complete` | `PASS` | status=pipeline_ready_with_boundary, stages=17, edges=32 |
| `method_packet_presentable` | `PASS` | title=Human-State JEPA: General Architecture with a Route-Conserving S2 Bridge Case Study |
| `claim_boundary_honest` | `PASS` | pure_og=False, public_sensor=True, proprietary_embedding=False |

## Release Claim

This package is ready as a team-facing and paper-facing HS-JEPA release when presented with the explicit public-sensor boundary.

## Boundary

- private LB safety is not proven
- pure OG-only assignment is not proven
- human-state is an orientation diagnostic, not a complete row-target assignment solver
- OG-only assignment replacement has a recorded probe result
- Listener-invariant contrastive decoding has a recorded probe result
- Private-safe toxicity has a recorded probe result and hard-world boundary
- Hard-world toxicity factorization has a recorded probe result
- Factorized toxicity decoder candidates have recorded upload-safe outputs
- HS-JEPA Core is separated from the Sleep Competition Adapter
- the next big bet is replacing public-sensor assignment with an OG-only human-state teacher
