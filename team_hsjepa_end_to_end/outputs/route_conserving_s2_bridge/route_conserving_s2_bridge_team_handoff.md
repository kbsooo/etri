# Route-Conserving S2 Bridge HS-JEPA Team Handoff

이 파일은 팀원이 과거 실험 버전명을 몰라도 현재 HS-JEPA 패키지의 실행 결과와 논문용 주장을 한 번에 이해하도록 만든 최종 핸드오프 요약이다.

## One-Command Reproduction

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py
```

전체 dependency까지 재생성하려면:

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py --refresh
```

## Core Mechanism

```text
HS-JEPA Core:
partial human context
  -> hidden human-state representation
  -> listener responsibility
  -> action-health decision
  -> invariant-preserving decoder
  -> anti-shortcut validation

Sleep Competition Adapter:
public-sensitive driver action
  + route-conserving bridge action
  + S2 listener/hub constraint
  + upload-safe sparse row-target decoder
```

축구 비유로 말하면, HS-JEPA Core는 `상황을 읽고, listener와 action 위험을 분리한 뒤, 궤적 불변성을 보존하는 슛 기술`이다. Sleep Adapter의 S2 bridge는 그 기술이 이번 경기장에서 구현된 case-study 궤적이다.

## Core / Adapter Separation

- Core status: `core_ready_for_adapter` (`5/5` gates)
- Core ablation contract: `6` modules, `20` big-bet followups
- Core reference run: `core_reference_ready`, released actions `['survey_small_shift']`
- Core module benchmark: `core_module_benchmark_ready`, full-core F1 `1.0`, action-health FP lift `9`
- Adapter status: `adapter_ready_with_public_sensor_boundary`
- Adapter score delta: `-0.00841135550000005`
- OG-only assignment probe: `og_only_assignment_replacement_not_ready`
- Assignment-gap decomposition: `row_support_is_primary_bottleneck`
- Hidden row-support sensor: `portable_row_support_sensor_alive_partial`
- Masked row-support objective: `masked_row_support_objective_supported_with_stress_boundary`
- Row-support strict action decoder: `row_support_action_decoder_alive_with_route_tradeoff`
- Route-frontier action decoder: `route_frontier_action_decoder_alive_with_matched_boundary`
- Route-toxicity fusion decoder: `route_toxicity_fusion_decoder_alive`
- Decoder-order jury solver: `decoder_order_jury_ready`
- Decoder boundary tomography: `boundary_tomography_ready`
- Core-mediated action release: `core_mediated_action_release_ready`
- Core release ablation probe: `core_release_ablation_ready`
- Core-health calibrated release: `core_health_calibrated_release_ready`
- Cross-listener transport decoder: `cross_listener_transport_ready`
- Counterfactual listener-dropout solver: `counterfactual_listener_dropout_ready`
- Spectral public tangent solver: `spectral_public_tangent_ready`
- Negative-tangent invariant projection: `candidate_ready`
- LB-conditioned responsibility solver: `candidate_ready`
- Mixture-listener responsibility solver: `candidate_ready`
- Public/private subset tomography solver: `candidate_ready`
- Action decoder ablation suite: `action_decoder_ablation_ready_decoder_jury_leads`
- Listener-invariant contrastive probe: `listener_invariant_decoder_not_ready`
- Private-safe toxicity probe: `toxicity_field_promising_with_hardworld_gap`
- Hard-world toxicity factorization probe: `hardworld_mixture_factorization_required`
- Factorized toxicity decoder variants: `2`
- Factorized toxicity stress audit: `stress_audit_ready`
- Core/adapter boundary audit: `core_adapter_boundary_verified` (`6/6` checks)

Core 문서:

```text
hsjepa_core/outputs/hsjepa_core_manifest_ko.md
hsjepa_core/outputs/hsjepa_core_ablation_contract_ko.md
```

Adapter 문서:

```text
sleep_competition_adapter/outputs/sleep_competition_adapter_report_ko.md
sleep_competition_adapter/outputs/hsjepa_big_bet_queue_ko.md
sleep_competition_adapter/outputs/og_only_assignment_teacher_probe_ko.md
sleep_competition_adapter/outputs/assignment_gap_decomposition_probe_ko.md
sleep_competition_adapter/outputs/hidden_row_support_sensor_probe_ko.md
sleep_competition_adapter/outputs/masked_row_support_objective_probe_ko.md
sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout_ko.md
sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout_ko.md
sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout_ko.md
sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout_ko.md
sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout_ko.md
sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_readout_ko.md
sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_readout_ko.md
sleep_competition_adapter/outputs/core_health_calibrated_release/core_health_calibrated_release_readout_ko.md
sleep_competition_adapter/outputs/cross_listener_transport_decoder/cross_listener_transport_readout_ko.md
sleep_competition_adapter/outputs/counterfactual_listener_dropout_solver/counterfactual_listener_dropout_readout_ko.md
sleep_competition_adapter/outputs/spectral_public_tangent_solver/spectral_public_tangent_readout_ko.md
sleep_competition_adapter/outputs/negative_tangent_invariant_projection_solver/negative_tangent_invariant_projection_readout.md
sleep_competition_adapter/outputs/lb_conditioned_responsibility_solver/lb_conditioned_responsibility_readout_ko.md
sleep_competition_adapter/outputs/mixture_listener_responsibility_solver/mixture_listener_responsibility_readout_ko.md
sleep_competition_adapter/outputs/public_private_subset_tomography_solver/public_private_subset_tomography_readout_ko.md
sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite_ko.md
sleep_competition_adapter/outputs/listener_invariant_contrastive_probe_ko.md
sleep_competition_adapter/outputs/private_safe_toxicity_probe_ko.md
sleep_competition_adapter/outputs/hardworld_toxicity_factorization_probe_ko.md
sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_readout_ko.md
sleep_competition_adapter/outputs/factorized_toxicity_decoder_candidate/factorized_toxicity_decoder_stress_audit_ko.md
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit_ko.md
```

## Generated Submission Roles

| Role | File | Upload-safe | Changed cells |
| --- | --- | ---: | ---: |
| `competition_primary` | `submission_team_hsjepa_route_conserving_objective_bridge_primary_89d16116_uploadsafe.csv` | `True` | `82` |
| `interpretable_s2_hub` | `submission_team_hsjepa_s2_listener_bridge_interpretable_f0866f50_uploadsafe.csv` | `True` | `68` |
| `human_state_probe` | `submission_team_hsjepa_human_state_gated_s2_bridge_probe_38d995b0_uploadsafe.csv` | `True` | `68` |

## Mechanism Evidence

| Candidate | Route delta | Null route delta | S2 usage | Null S2 usage | Route p | S2 p |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `route_conserving_objective_bridge_primary` | `-0.02457` | `-0.01090` | `0.780` | `0.615` | `0.0000` | `0.0006` |
| `s2_listener_bridge_interpretable` | `-0.02696` | `-0.01082` | `1.000` | `0.615` | `0.0000` | `0.0000` |

자동 validator가 확인한 핵심 수치:

- Primary route z-score: `-9.66`
- S2 listener route z-score: `-9.46`
- S2 listener usage: `1.000` vs null `0.615`
- Package validation passed: `True`
- Architecture readiness: `paper_ready_with_boundary` (`7/7` gates)
- Mechanism ablation: `mechanism_ablation_ready` (`5` public worldviews killed, `2` survived)
- Generality boundary: `general_architecture_separated_with_case_boundary` (`10/11` portability checks, nonblocking boundaries: `1`)
- Core/adapter boundary: core `core_ready_for_adapter`, adapter `adapter_ready_with_public_sensor_boundary`
- OG-only assignment boundary: pure recall `0.0404`, distilled recall `0.1236`
- Assignment gap: `row_support_is_primary_bottleneck`, row-support gap `0.5832`
- Hidden row-support sensor: `portable_row_support_composite`, row AUC `0.8193`, cell recall `0.3289`
- Masked row-support objective: row AUC `0.8193`, cell recall `0.3289`, group stress AUC `0.5584`
- Row-support strict decoder: recommended `exploratory_route_support_gate`, changed cells `34`, safety z `3.64`
- Route-frontier decoder: recommended `seed_route_frontier`, status `route_frontier_action_decoder_alive_with_matched_boundary`
- Route-toxicity fusion decoder: recommended `seed_driver_safe_route_fusion`, status `route_toxicity_fusion_decoder_alive`
- Decoder-order jury: recommended `{'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.392520579892158}`, status `decoder_order_jury_ready`
- Decoder boundary tomography: recommended `{'variant': 'consensus_shadow_plus', 'submission_file': 'submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv', 'priority': 0.6990859175252038}`, status `boundary_tomography_ready`, inventory `{'strict_jury_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'conflict_cells': 0}`
- Core-mediated action release: recommended `{'variant': 'core_consensus_shadow_plus', 'submission_file': 'submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv', 'priority': 0.8460231888716516}`, status `core_mediated_action_release_ready`, inventory `{'candidate_cells': 44, 'strict_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'default_core_released': 32}`
- Core release ablation: full-core `{'variant': 'full_core_reference', 'submission_file': 'submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv', 'priority': 0.8314097090596275}`, sensor `{'variant': 'no_action_health', 'submission_file': 'submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv', 'priority': 0.3281725643379389}`, status `core_release_ablation_ready`
- Core-health calibrated release: guarded `{'variant': 'benchmark_guarded_full_plus', 'submission_file': 'submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv', 'priority': 0.38818571481351827}`, big bet `{'variant': 'route_pressure_boundary_probe', 'submission_file': 'submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv', 'priority': 0.38337754232640875}`, status `core_health_calibrated_release_ready`
- Cross-listener transport: recommended `{'variant': 'listener_confirmed_shadow', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': 0.5684860446, 'priority': 0.9427271560571463, 'config': {'name': 'listener_confirmed_shadow', 'boundary_classes': ['strict_jury', 'consensus_shadow'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.44, 'max_cells': 28, 'max_extra_cells': 6, 'strict_base_scale': 0.82, 'extra_base_scale': 0.34, 'listener_gain': 0.2, 's2_gain': 0.09, 'probe_role': 'tests whether target-listener confirmed shadow cells are safer than broad shadow release'}, 'rank': 1}`, big bet `{'variant': 'objective_listener_island_probe', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_objective_listener_island_probe_8d2046bf_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': None, 'priority': 0.9427271560571463, 'config': {'name': 'objective_listener_island_probe', 'boundary_classes': ['strict_jury', 'consensus_shadow', 'route_only', 'fusion_only'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.47, 'max_cells': 34, 'max_extra_cells': 12, 'strict_base_scale': 0.8, 'extra_base_scale': 0.28, 'listener_gain': 0.22, 's2_gain': 0.1, 'probe_role': 'tests whether an objective-listener island exists outside the current public row-state support'}, 'rank': 2}`, status `cross_listener_transport_ready`
- Counterfactual listener-dropout: information sensor `dropout_fullfield_aggressive`, status `counterfactual_listener_dropout_ready`
- Spectral public tangent: information sensor `anti_bad_tangent_pressure`, status `spectral_public_tangent_ready`
- Negative-tangent invariant projection: recommended `subject_prior_safe_projection`, status `candidate_ready`
- LB-conditioned responsibility: recommended `pure_lb_gradient_jackpot`, file `submission_hsjepa_lb_responsibility_pure_lb_gradient_jackpot_f0a8129d_uploadsafe.csv`, LOO corr `0.7300005193514604`, changed cells `24`
- Mixture-listener responsibility: recommended `target_listener_split_qs`, file `submission_hsjepa_mixture_listener_target_listener_split_qs_7a383104_uploadsafe.csv`, mixture LOO `0.9578327145275477`, scalar LOO `0.7300005193514604`, changed cells `30`
- Public/private subset tomography: recommended `subset_label_direction_jackpot`, file `submission_hsjepa_subset_tomography_subset_label_direction_jackpot_d12af8ff_uploadsafe.csv`, source LOO `0.7300005193514604`, changed cells `18`, predicted delta `-4.929555282376722`
- Action decoder ablation: recommended `{'family': 'decoder_order_jury', 'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.394366527938867}`, big bet `{'family': 'route_frontier', 'variant': 'open_route_frontier', 'submission_file': 'submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv', 'priority': 1.05448050759572}`
- Listener-invariant boundary: listener-route rho `-0.0313`, contrastive overlap `0.2152`
- Private-safe toxicity boundary: mean LOO AUC `0.7880`, worst LOO AUC `0.3683`
- Hard-world factorization: broad->H088 AUC `0.3683`, broad/H088 rho `-0.4276`
- Factorized decoder candidates: `dual_safe_expansion, teacher_dual_head`
- Factorized decoder stress: `dual_safe_expansion:factorized_decoder_stress_supported, teacher_dual_head:factorized_decoder_alive_but_source_null_weak`
- Boundary tomography inventory: `{'strict_jury_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'conflict_cells': 0}`
- Core-mediated release inventory: `{'candidate_cells': 44, 'strict_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'default_core_released': 32}`
- Core/adapter boundary audit: `core_adapter_boundary_verified`
- Release checklist: `release_ready_with_boundary` (`87/87` checks)

## Paper Claim

강하게 주장할 수 있는 내용:

```text
HS-JEPA is a core architecture for human-understanding prediction.
It predicts hidden human-state, listener responsibility, action-health, and invariant-preserving action representations.
The sleep competition adapter instantiates the invariant as Q/S route energy and the listener bridge as S2.
The current LB breakthrough is evidence for this adapter, while the reusable claim is the core/action separation.
```

## Big-Bet Queue

다음 큰 실험은 단순 alpha 조정이 아니라 core/adaptor 경계를 바꾸는 실험이다.

- `Public/Private Subset Tomography Solver`: Scalar public feedback is generated by public subset inclusion times hidden label direction, while private action-health decides whether the move is safe outside that listener. Expected LB delta if true `-0.012`.
- `Mixture-Listener Responsibility Solver`: The public LB is not one listener; it is a scalar readout of multiple latent listener heads, and Q/S actions may need different heads. Expected LB delta if true `-0.01`.
- `LB-Conditioned Responsibility Solver`: The public LB can be treated as an external listener whose scalar observations reveal row-target action responsibility. Expected LB delta if true `-0.008`.
- `Negative Tangent Invariant Projection Solver`: A negative public representation is useful only when its inverse can be projected onto label-valid human-state invariants. Expected LB delta if true `-0.006`.
- `Spectral Public-Tangent Solver`: Known post-H057 public failures are not independent mistakes; they collapse onto a low-rank public-bad action tangent. Expected LB delta if true `-0.004`.
- `Counterfactual Listener-Dropout Solver`: A healthy HS-JEPA action should survive when one listener is masked, while failed public sensors become action-toxicity evidence rather than discarded submissions. Expected LB delta if true `-0.003`.
- `Action Decoder Ablation Suite`: The next breakthrough comes from choosing the correct action-decoder order, not from adding more latent features. Expected LB delta if true `-0.0025`.
- `OG-only Human-State Assignment Teacher`: The public-sensor teacher can be replaced by personal/cohort/time human-state consistency. Expected LB delta if true `-0.003`.
- `Route-Frontier Action Decoder`: The action decoder should select route-manifold frontier moves first, then check row-support and toxicity. Expected LB delta if true `-0.0025`.
- `Route-Toxicity Fusion Decoder`: Route-frontier action ordering and factorized action-health are not alternatives; safe actions need both. Expected LB delta if true `-0.0025`.
- `Decoder-Order Jury Solver`: Safe row-target assignment is a cross-decoder jury, not a single route or toxicity score. Expected LB delta if true `-0.0025`.
- `Hard-World Mixture Toxicity Decoder`: H088-like hard-world toxicity is anti-correlated with broad public-bad toxicity, so action-health must be factorized. Expected LB delta if true `-0.0025`.
- `Masked Row-Support Action Decoder`: The masked row-support representation can choose which route-conserving S2/stage bundles are safe enough to move. Expected LB delta if true `-0.002`.
- `Decoder Boundary Tomography Solver`: The strict cross-decoder jury may be correct but too conservative; rejected cells split into weak consensus, route-only, and fusion-only worlds. Expected LB delta if true `-0.002`.
- `Core-Mediated Action Release`: A reusable HS-JEPA core should mediate real row-target actions before the sleep adapter releases them. Expected LB delta if true `-0.002`.
- `Core Release Ablation Probe`: A real HS-JEPA architecture must expose which core module over-constrains or protects row-target action release. Expected LB delta if true `-0.002`.
- `Core-Health Calibrated Release`: Dataset-free HS-JEPA action-health failure modes should calibrate the real sleep-adapter action boundary. Expected LB delta if true `-0.002`.
- `Cross-Listener Transport Decoder`: Target-listener posterior is not an action generator; it is a transport calibrator over route/fusion/core-safe actions. Expected LB delta if true `-0.002`.
- `Listener-Invariant Contrastive Decoder`: A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone. Expected LB delta if true `-0.002`.
- `Private-Safe Toxicity Field`: The plateau comes from actions that help public-like rows but poison private-like rows. Expected LB delta if true `-0.0015`.

## Competition Use

제출 슬롯이 있다면 우선순위는 다음이다.

1. `competition_primary`: 성능 중심 Route-Conserving Objective Bridge
2. `interpretable_s2_hub`: 논문 설명력이 가장 강한 S2 Listener Bridge
3. `human_state_probe`: OG human-state orientation diagnostic

## Reproducibility Contract

이 패키지는 입력을 다음처럼 분리해서 기록한다.

```text
OG raw data != public-LB sensor != generated action artifact
```

계약 문서:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.md
```

## Boundary

이 패키지가 증명하지 않는 것:

- private leaderboard safety
- OG human-state encoder 단독으로 row-target assignment 해결
- S2가 모든 수면 생리학적 factor의 중심이라는 주장

정확한 결론은 더 좁고 강하다.

```text
Given a public-sensitive action field, route conservation plus S2 listener usage selects a statistically unusual and interpretable correction path.
```

## Architecture Readiness Report

논문/팀 공유용 gate 판정:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.md
```

## Paper Method Packet

논문 초안/발표에 바로 옮길 수 있는 method packet:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_paper_method_packet_ko.md
```

## Mechanism Ablation Report

대체 세계관 중 무엇이 public sensor/stress audit에서 죽었고 무엇이 살아남았는지 정리한 knockout report:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_mechanism_ablation_report_ko.md
```

## Generality Report

HS-JEPA의 범용 아키텍처와 이번 대회의 Route-Conserving S2 Bridge case study를 분리한 portability report:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_generality_report_ko.md
```

## Pipeline Manifest

OG 데이터에서 public sensor, latent/context, route decoder, submission, paper packet까지 이어지는 역할 기반 pipeline:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_pipeline_manifest_ko.md
```

## Release Checklist

팀 공유/논문 발표/제출 논의용 최종 release gate:

```text
team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_release_checklist_ko.md
```
