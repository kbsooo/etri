# HS-JEPA Paper Method Packet

이 문서는 팀원이 과거 제출 버전명을 몰라도 HS-JEPA를 논문/발표 아이디어로 설명할 수 있도록 만든 method packet이다.

## One-Sentence Contribution

HS-JEPA Core is a human-understanding architecture that predicts hidden human-state, listener responsibility, action-health, and invariant-preserving action representations before producing bounded predictions; the Sleep Competition Adapter instantiates that core as a Route-Conserving S2 Bridge case study.

## Abstract Draft

우리는 인간 생활 로그 예측을 label column에 대한 직접 분류 문제가 아니라, 숨은 인간 생활 상태가 여러 listener와 action으로 드러나는 representation prediction 문제로 재정의한다. 제안하는 HS-JEPA는 raw label을 직접 복원하지 않고 human-state, listener responsibility, action-health, invariant energy를 분리한다. 수면 로그 대회 case study에서는 이 일반 구조가 sparse row-target action decoding으로 구현되며, objective sleep-stage target에서는 public-sensitive driver action을 단독으로 적용하지 않고 train label에서 학습한 Q/S route manifold를 보존하는 bridge action을 함께 선택한다. 실험적으로 이 case-study decoder는 기존 public-equation 이전 최고 public LB 0.5761589494에서 현재 최고 0.5677475939까지 -0.0084113555 개선된 signal을 설명하며, 선택된 bridge는 random feasible bundle 대비 route energy를 -0.02457 vs -0.01090로 낮춘다. 또한 S2는 listener/hub로 반복 등장한다 (1.000 vs null 0.615). Human-state latent는 cell-level orientation AUC 0.775를 보이지만 row assignment AUC는 0.545에 그쳐, encoder와 assignment decoder를 분리해야 함을 보여준다.

## Method

HS-JEPA는 core와 adapter를 분리한다.

Core equation:

```text
partial_human_context -> hidden_human_state -> listener_responsibility -> action_health -> invariant_preserving_decoder -> anti_shortcut_validation
```

Core modules:

1. Human-State Context Encoder: Encode partial person, cohort, time, routine, social, and sensor context into a hidden human-state field.
2. Masked State Predictor: Predict unobserved state/listener representations from visible context without reconstructing raw inputs.
3. Listener Responsibility: Treat labels, sensors, surveys, or outcomes as listeners that react differently to the same human state.
4. Action-Health Decoder: Decide whether a latent signal is healthy enough to translate into an output action.
5. Invariant Energy: Score whether an action preserves the behavioral, physiological, temporal, or semantic manifold of the domain.
6. Anti-Shortcut Validation: Stress-test the representation and action field against nulls, cohort shifts, time shifts, counterfactual listener dropout, and shortcut sensors.

Sleep competition adapter:

This adapter converts HS-JEPA Core into a sleep-log competition system by supplying Q/S listeners, a route invariant, public-sensor action evidence, and upload-safe sparse row-target decoding.

이번 수면 대회에서는 listener가 Q1/Q2/Q3/S1/S2/S3/S4로, invariant가 Q/S route energy로, action-health가 public/private toxicity 및 feasible-bundle stress로 구현되었다. 새 hard-world probe는 broad toxicity와 H088 toxicity가 역상관될 수 있음을 보여주므로, action-health는 단일 위험 점수가 아니라 factorized energy head로 다루어야 한다. 이후 core-health calibrated release는 dataset-free core benchmark에서 action-health를 제거했을 때 false positive가 늘어난다는 실패 패턴을 실제 adapter release prior로 사용한다. cross-listener transport는 target-listener lift가 direct action generator로는 실패했다는 negative sensor를 보존하고, listener posterior를 route/fusion/core-safe action의 transport calibrator로만 사용한다. counterfactual listener-dropout은 listener 하나를 가려도 같은 row-target action이 살아남는지 묻고, 실패한 public sensor들을 버리는 대신 action-toxicity label로 사용한다. spectral public-tangent solver는 실패한 public action들을 저차원 negative representation으로 압축한 뒤 anti-tangent와 orthogonal residual release를 비교한다. negative tangent invariant projection은 여기서 한 단계 더 나아가, 그 반대 방향 action을 target-route/subject-prior invariant 위로 투영해야만 action-grade가 된다는 주장을 테스트한다. LB-conditioned responsibility solver는 public LB라는 scalar 외부 listener가 흘린 관측값에서 row-target action responsibility를 역추정한다. public/private subset tomography는 scalar feedback을 한 번 더 분해해 `public subset inclusion × hidden label direction`으로 해석하고, private-safety/toxicity head가 그 action을 외부 listener 밖에서도 보존할 수 있는지 묻는다. 핵심은 `S2` 자체가 아니라, hidden state를 직접 label로 쓰지 않고 core의 listener/action/invariant/anti-shortcut/negative-representation/responsibility/subset-tomography 경로를 adapter가 안전한 sparse row-target action으로 번역한다는 점이다.

## Core / Adapter Evidence

- Core status: `core_ready_for_adapter` (`5/5` gates)
- Core ablation contract: `ablation_contract_ready` (`6` ablations)
- Core reference run: `core_reference_ready`, released `['survey_small_shift']`, ablations `3`
- Core module benchmark: `core_module_benchmark_ready`, scenarios `5`, full-core F1 `1.000`, action-health FP lift `9`, invariant FP lift `1`
- Core/adapter boundary audit: `core_adapter_boundary_verified` (`6/6` checks)
- Core operational violations: imports `0`, strings `0`
- Adapter status: `adapter_ready_with_public_sensor_boundary`
- Big-bet queue: `big_bet_queue_ready` (`20` bets)

## Generality

HS-JEPA general architecture != Route-Conserving S2 Bridge competition case study

일반 HS-JEPA에서 재사용되는 것은 다음 구조다.

```text
partial human context
  -> hidden human-state representation
  -> listener responsibility
  -> action-health decision
  -> invariant-preserving decoder
  -> anti-shortcut validation
```

이번 대회의 S2/public-sensor 구조는 이 일반 구조의 case study다.

- Generality status: `general_architecture_separated_with_case_boundary`
- Portability checks: `10/11`
- Nonblocking boundaries: `remaining_generality_gap`
- OG-only assignment probe: `og_only_assignment_replacement_not_ready`
- Pure OG row-cap2 recall: `0.0404`
- Distilled row-cap2 recall: `0.1236`
- Assignment gap decomposition: `row_support_is_primary_bottleneck`
- Best portable recall: `0.1063`
- Row oracle + stage prior recall: `0.6896`
- Row-support gap: `0.5832`
- Hidden row-support transfer: `portable_row_support_sensor_alive_partial`
- Best row-support family: `portable_row_support_composite`
- Row-support row AUC: `0.8193`
- Row-support cell recall: `0.3289`
- Row-support AUC z: `6.4180`
- Masked row-support objective: `masked_row_support_objective_supported_with_stress_boundary`
- Masked full row AUC: `0.8193`
- Masked full cell recall: `0.3289`
- Masked human-only cell recall: `0.2713`
- Masked group stress AUC: `0.5584`
- Row-support strict action decoder: `row_support_action_decoder_alive_with_route_tradeoff`
- Recommended action variant: `exploratory_route_support_gate`
- Decoder changed cells: `34`
- Decoder safety z / combined z: `3.6437` / `1.3787`
- Decoder mean route gain: `0.02205`
- Route-frontier action decoder: `route_frontier_action_decoder_alive_with_matched_boundary`
- Route-frontier recommended variant: `seed_route_frontier`
- Route-frontier variant scores: `[{'variant': 'seed_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.631665028357059, 'matched_score_z': 3.6234736097578057, 'upload_safe': True}, {'variant': 's2_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.8237779101897877, 'matched_score_z': 3.3123857088533875, 'upload_safe': True}, {'variant': 'open_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.492261359647143, 'matched_score_z': 3.0831554042259524, 'upload_safe': True}]`
- Route-toxicity fusion decoder: `route_toxicity_fusion_decoder_alive`
- Route-toxicity fusion recommended variant: `seed_driver_safe_route_fusion`
- Route-toxicity fusion variant scores: `[{'variant': 's2_route_toxicity_fusion', 'changed_cells': 8, 'broad_route_z': -0.06361725497399186, 'toxicity_matched_safety_z': 0.0, 'toxicity_matched_fusion_z': 0.00022199529973856787, 'upload_safe': True}, {'variant': 'seed_route_toxicity_fusion', 'changed_cells': 8, 'broad_route_z': -0.05413537720642773, 'toxicity_matched_safety_z': 0.0, 'toxicity_matched_fusion_z': 0.00022199529973856787, 'upload_safe': True}, {'variant': 'open_route_toxicity_fusion', 'changed_cells': 4, 'broad_route_z': -0.16743111973717828, 'toxicity_matched_safety_z': 0.00022199529973856787, 'toxicity_matched_fusion_z': 0.0, 'upload_safe': True}, {'variant': 's2_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 2.5212391425980725, 'toxicity_matched_safety_z': 1.4350151378530516, 'toxicity_matched_fusion_z': 3.333896510179827, 'upload_safe': True}, {'variant': 'seed_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 1.956452255410393, 'toxicity_matched_safety_z': 1.1375544203021746, 'toxicity_matched_fusion_z': 4.040831045742473, 'upload_safe': True}, {'variant': 'open_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 1.2492144363720237, 'toxicity_matched_safety_z': 1.1862432357203119, 'toxicity_matched_fusion_z': 1.8706591048812475, 'upload_safe': True}]`
- Decoder-order jury solver: `decoder_order_jury_ready`
- Decoder-order jury recommended LB sensor: `{'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.392520579892158}`
- Decoder boundary tomography: `boundary_tomography_ready`
- Boundary tomography recommended LB sensor: `{'variant': 'consensus_shadow_plus', 'submission_file': 'submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv', 'priority': 0.6990859175252038}`
- Boundary inventory: `{'strict_jury_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'conflict_cells': 0}`
- Core-mediated action release: `core_mediated_action_release_ready`
- Core-mediated recommended LB sensor: `{'variant': 'core_consensus_shadow_plus', 'submission_file': 'submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv', 'priority': 0.8460231888716516}`
- Core-mediated inventory: `{'candidate_cells': 44, 'strict_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'default_core_released': 32}`
- Core release ablation: `core_release_ablation_ready`
- Core release full-core LB candidate: `{'variant': 'full_core_reference', 'submission_file': 'submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv', 'priority': 0.8314097090596275}`
- Core release architecture sensor: `{'variant': 'no_action_health', 'submission_file': 'submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv', 'priority': 0.3281725643379389}`
- Core-health calibrated release: `core_health_calibrated_release_ready`
- Core-health guarded LB candidate: `{'variant': 'benchmark_guarded_full_plus', 'submission_file': 'submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv', 'priority': 0.38818571481351827}`
- Core-health big-bet sensor: `{'variant': 'route_pressure_boundary_probe', 'submission_file': 'submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv', 'priority': 0.38337754232640875}`
- Core-health pressure sensor: `{'variant': 'health_relaxed_pressure_sensor', 'submission_file': 'submission_hsjepa_core_health_health_relaxed_pressure_sensor_7da82c23_uploadsafe.csv', 'priority': -0.21134339216533768}`
- Cross-listener transport: `cross_listener_transport_ready`
- Cross-listener recommended LB sensor: `{'variant': 'listener_confirmed_shadow', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': 0.5684860446, 'priority': 0.9427271560571463, 'config': {'name': 'listener_confirmed_shadow', 'boundary_classes': ['strict_jury', 'consensus_shadow'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.44, 'max_cells': 28, 'max_extra_cells': 6, 'strict_base_scale': 0.82, 'extra_base_scale': 0.34, 'listener_gain': 0.2, 's2_gain': 0.09, 'probe_role': 'tests whether target-listener confirmed shadow cells are safer than broad shadow release'}, 'rank': 1}`
- Cross-listener negative sensor: `{'file': 'submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv', 'public_lb': 0.5680255019, 'interpretation': 'direct listener-lift is not action-grade; use listener posterior only as a release/calibration prior'}`
- Counterfactual listener-dropout: `counterfactual_listener_dropout_ready`
- Listener-dropout information sensor: `{'variant': 'dropout_fullfield_aggressive', 'submission_file': 'submission_hsjepa_counterfactual_listener_dropout_dropout_fullfield_aggressive_a433fbc0_uploadsafe.csv', 'priority': 1.2860211183353285}`
- Listener-dropout thesis sensor: `{'variant': 'invariant_survivor', 'submission_file': 'submission_hsjepa_counterfactual_listener_dropout_invariant_survivor_7cde1a77_uploadsafe.csv', 'priority': 0.05}`
- Spectral public-tangent solver: `spectral_public_tangent_ready`
- Spectral first bad-mode variance: `0.9629`
- Spectral top-5 variance: `0.9947`
- Spectral information sensor: `{'variant': 'anti_bad_tangent_pressure', 'submission_file': 'submission_hsjepa_spectral_public_tangent_anti_bad_tangent_pressure_6a93251a_uploadsafe.csv', 'priority': 1.4947903603985548}`
- Spectral counter sensor: `{'variant': 'orthogonal_private_residual', 'submission_file': 'submission_hsjepa_spectral_public_tangent_orthogonal_private_residual_57ed54c2_uploadsafe.csv'}`
- LB-conditioned responsibility solver: `candidate_ready`
- LB responsibility recommended variant: `pure_lb_gradient_jackpot`
- LB responsibility LOO corr: `0.7300`
- LB responsibility cells: `115`
- Public/private subset tomography: `candidate_ready`
- Subset tomography recommended variant: `subset_label_direction_jackpot`
- Subset tomography source LOO corr: `0.7300`
- Subset tomography cells: `115`
- Listener-invariant probe: `listener_invariant_decoder_not_ready`
- Listener-route Spearman: `-0.0313`
- Private-safe toxicity probe: `toxicity_field_promising_with_hardworld_gap`
- Toxicity mean LOO AUC: `0.7880`
- Toxicity worst LOO AUC: `0.3683`
- Hard-world factorization probe: `hardworld_mixture_factorization_required`
- Broad toxicity -> H088 AUC: `0.3683`
- Broad/H088 Spearman: `-0.4276`

가장 중요한 남은 과제는 target route가 아니라 hidden row-support sensor를 안전한 row-target action으로 번역하는 것이다. 이제 row-support는 완전히 죽은 가설이 아니라 teacher-transfer와 masked-family objective에서 부분적으로 살아있는 가설로 바뀌었다. 특히 seven-target prediction landscape와 human/cohort context를 합친 portable composite가 row-support를 상당 부분 복원하고, human-only/prediction-only/masked-route view도 신호를 유지한다. 첫 strict action decoder는 null 대비 safety는 강하지만 route-gain 우위가 약했다. 새 route-frontier decoder는 반대로 route manifold frontier를 먼저 고르고 support/toxicity를 통과시키며, local broad/matched null은 이겼다. route-toxicity fusion decoder는 여기서 한 단계 더 나아가 route-first와 factorized action-health를 조합한다. decoder-order jury solver는 이 둘이 같은 row-target과 방향에 합의할 때만 action을 방출한다. boundary tomography는 그 strict jury가 너무 보수적인지 보기 위해 rejected cells를 weak-consensus, route-only, fusion-only로 쪼갠다. core-mediated release는 이 후보들을 다시 HS-JEPA Core의 context/listener/action-health/invariant 인터페이스로 통과시켜, core 자체가 action-grade release equation이 될 수 있는지 시험한다. core release ablation은 같은 cell에서 listener/action-health/invariant를 하나씩 제거해 module이 실제 release boundary를 바꾸는지 확인한다. core-health calibrated release는 dataset-free core benchmark에서 관측된 action-health false-positive lift를 adapter release prior로 사용해, generic core test가 실제 competition action boundary를 조절하는지 묻는다. cross-listener transport는 실패한 direct listener action을 버리지 않고, listener posterior를 route/fusion/core-safe action의 운송 보정자로만 써서 listener responsibility의 더 일반적인 역할을 시험한다. counterfactual listener-dropout은 어떤 listener를 빼도 살아남는 action과 실패한 public sensor에 공선적인 action을 분리한다. spectral public-tangent solver는 여기서 한 단계 더 나아가, 실패한 public action들을 하나의 negative representation space로 모으고 그 반대/직교 방향이 release 가능한 action equation인지 묻는다. negative tangent invariant projection은 그 질문을 더 강하게 바꿔, 반대 방향 action도 target-route/subject-prior invariant를 통과하지 못하면 release하지 않는다. 다만 이것들도 아직 sleep adapter의 LB sensor이지 private-safe release claim은 아니다.

## Algorithm

```text
Algorithm: HS-JEPA General Pattern with Sleep-Log Case Decoder

Input: human lifestyle/context logs, listener labels or sensor outcomes, optional deployment sensor, current prediction.
Output: bounded prediction/action field with invariant and shortcut checks.

1. Encode personal, cohort, time, routine, social, and sensor context into a human-state representation.
2. Predict masked listener/action representations from partial human context.
2a. Treat row-support as a hidden target representation and stress it under masked human/prediction/route views.
3. Estimate listener responsibility: which outcomes should react to the hidden state.
4. Estimate action-health: whether the latent signal is safe to translate into output movement.
5. Factorize action-health when shortcut modes are anti-correlated rather than scalar.
6. Translate row-support through a strict route-support action gate before changing outputs.
7. Prefer route-frontier actions when support-first decoding fails route/null stress.
8. Learn an invariant energy over valid output/action manifolds.
9. Release actions through a cross-decoder jury when route-first and action-health-first decoders agree.
10. Run boundary tomography on rejected cells to test whether the release rule is too conservative.
11. Calibrate adapter release with dataset-free core benchmark failure modes.
12. Use cross-listener posterior as a transport calibrator only after route/fusion/core action support exists.
13. Drop one listener view at a time and keep only actions whose health survives listener masking.
14. Treat failed public sensors as toxicity evidence and test same-direction release against direction inversion.
15. Decompose failed action fields into a spectral negative representation and test anti-tangent versus orthogonal residual release.
16. Project negative-representation actions onto target-route and subject-prior invariants before release.
17. Estimate scalar-listener responsibility from external outcome observations when explicit row-target labels are unavailable.
18. Factor scalar feedback into public subset inclusion and hidden label direction when the external listener is only partially observed.
19. Decode bounded actions that improve listener fit while preserving the invariant.
20. Reject shortcuts with cohort/time/group/null stress tests.
21. In the sleep-log case study, instantiate the invariant as Q/S route energy and the decoder as the S2 bridge.
```

## Evidence Snapshot

- Status: `paper_ready_with_boundary`
- Readiness gates: `7/7`
- Pre-public-equation best public LB: `0.5761589494`
- Current best public LB: `0.5677475939`
- Delta: `-0.0084113555`
- Route delta vs null: `-0.02457` vs `-0.01090`
- S2 usage vs null: `1.000` vs `0.615`
- Human-state cell AUC / row AUC: `0.775` / `0.545`
- Assignment gap: `row_support_is_primary_bottleneck`, row-support gap `0.5832`
- Hidden row-support sensor: `portable_row_support_sensor_alive_partial`, family `portable_row_support_composite`, row AUC `0.8193`, cell recall `0.3289`
- Masked row-support objective: `masked_row_support_objective_supported_with_stress_boundary`, row AUC `0.8193`, cell recall `0.3289`, group stress AUC `0.5584`
- Row-support action decoder: `row_support_action_decoder_alive_with_route_tradeoff`, recommended `exploratory_route_support_gate`, changed cells `34`, safety z `3.6437`, combined z `1.3787`
- Route-frontier action decoder: `route_frontier_action_decoder_alive_with_matched_boundary`, recommended `seed_route_frontier`, scores `[{'variant': 'seed_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.631665028357059, 'matched_score_z': 3.6234736097578057, 'upload_safe': True}, {'variant': 's2_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.8237779101897877, 'matched_score_z': 3.3123857088533875, 'upload_safe': True}, {'variant': 'open_route_frontier', 'changed_cells': 20, 'broad_route_z': 2.492261359647143, 'matched_score_z': 3.0831554042259524, 'upload_safe': True}]`
- Route-toxicity fusion decoder: `route_toxicity_fusion_decoder_alive`, recommended `seed_driver_safe_route_fusion`, scores `[{'variant': 's2_route_toxicity_fusion', 'changed_cells': 8, 'broad_route_z': -0.06361725497399186, 'toxicity_matched_safety_z': 0.0, 'toxicity_matched_fusion_z': 0.00022199529973856787, 'upload_safe': True}, {'variant': 'seed_route_toxicity_fusion', 'changed_cells': 8, 'broad_route_z': -0.05413537720642773, 'toxicity_matched_safety_z': 0.0, 'toxicity_matched_fusion_z': 0.00022199529973856787, 'upload_safe': True}, {'variant': 'open_route_toxicity_fusion', 'changed_cells': 4, 'broad_route_z': -0.16743111973717828, 'toxicity_matched_safety_z': 0.00022199529973856787, 'toxicity_matched_fusion_z': 0.0, 'upload_safe': True}, {'variant': 's2_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 2.5212391425980725, 'toxicity_matched_safety_z': 1.4350151378530516, 'toxicity_matched_fusion_z': 3.333896510179827, 'upload_safe': True}, {'variant': 'seed_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 1.956452255410393, 'toxicity_matched_safety_z': 1.1375544203021746, 'toxicity_matched_fusion_z': 4.040831045742473, 'upload_safe': True}, {'variant': 'open_driver_safe_route_fusion', 'changed_cells': 20, 'broad_route_z': 1.2492144363720237, 'toxicity_matched_safety_z': 1.1862432357203119, 'toxicity_matched_fusion_z': 1.8706591048812475, 'upload_safe': True}]`
- Decoder-order jury solver: `decoder_order_jury_ready`, recommended `{'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.392520579892158}`, file `submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv`, priority `1.3925`
- Decoder boundary tomography: `boundary_tomography_ready`, recommended `{'variant': 'consensus_shadow_plus', 'submission_file': 'submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv', 'priority': 0.6990859175252038}`, file `submission_hsjepa_boundary_tomography_consensus_shadow_plus_04b2c855_uploadsafe.csv`, priority `0.6991`, inventory `{'strict_jury_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'conflict_cells': 0}`
- Core-mediated action release: `core_mediated_action_release_ready`, recommended `{'variant': 'core_consensus_shadow_plus', 'submission_file': 'submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv', 'priority': 0.8460231888716516}`, file `submission_hsjepa_core_mediated_core_consensus_shadow_plus_3b0b1d0f_uploadsafe.csv`, priority `0.8460`, inventory `{'candidate_cells': 44, 'strict_cells': 19, 'consensus_shadow_cells': 13, 'route_only_cells': 6, 'fusion_only_cells': 6, 'default_core_released': 32}`
- Core release ablation: `core_release_ablation_ready`, full-core `{'variant': 'full_core_reference', 'submission_file': 'submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv', 'priority': 0.8314097090596275}`, file `submission_hsjepa_core_ablation_full_core_reference_513175a1_uploadsafe.csv`, priority `0.8314`
- Core release architecture sensor: `{'variant': 'no_action_health', 'submission_file': 'submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv', 'priority': 0.3281725643379389}`, file `submission_hsjepa_core_ablation_no_action_health_043b20c7_uploadsafe.csv`, priority `0.3282`
- Core-health calibrated release: `core_health_calibrated_release_ready`, guarded `{'variant': 'benchmark_guarded_full_plus', 'submission_file': 'submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv', 'priority': 0.38818571481351827}`, file `submission_hsjepa_core_health_benchmark_guarded_full_plus_8a3662bc_uploadsafe.csv`, priority `0.3882`
- Core-health big-bet sensor: `{'variant': 'route_pressure_boundary_probe', 'submission_file': 'submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv', 'priority': 0.38337754232640875}`, file `submission_hsjepa_core_health_route_pressure_boundary_probe_e8b904e5_uploadsafe.csv`, priority `0.3834`
- Core-health benchmark calibration: `{'action_health_fp_lift': 9.0, 'invariant_fp_lift': 1.0, 'listener_fp_lift': 3.0, 'scenario_count': 5.0, 'action_fp_weight': 0.6428571428571429, 'invariant_fp_weight': 0.16666666666666666, 'listener_fp_weight': 0.375}`
- Cross-listener transport: `cross_listener_transport_ready`, recommended `{'variant': 'listener_confirmed_shadow', 'status': 'upload_safe', 'submission_file': 'submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'root_path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'local_path': '/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'validation': {'path': '/Users/kbsoo/Downloads/cl2/submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv', 'rows': 250, 'keys_match': True, 'duplicate_keys': 0, 'nan_cells': 0, 'min_prob': 4.939277944527429e-06, 'max_prob': 0.9999967514907456, 'changed_cells_vs_current_best': 23, 'upload_safe': True}, 'selected_cells': 23, 'stress': {'actual': {'cells': 23.0, 'rows': 14.0, 'extra_cells': 4.0, 'mean_transport_score': 0.7302068187870411, 'mean_listener_score': 0.8462882569230102, 'mean_row_s2_score': 1.0329959500444077, 'mean_action_score': 2.8915693124517627, 'same_listener_direction_rate': 1.0, 'strict_rate': 0.8260869565217391, 'shadow_rate': 0.17391304347826086, 'route_only_rate': 0.0, 'fusion_only_rate': 0.0, 's2_rate': 0.5217391304347826}, 'tests': {'mean_transport_score': {'actual': 0.7302068187870411, 'null_mean': 0.6968019937164937, 'null_std': 0.010219840824461732, 'z': 3.268624790181781, 'p': 0.002}, 'mean_listener_score': {'actual': 0.8462882569230102, 'null_mean': 0.7444625704310898, 'null_std': 0.03044285443808385, 'z': 3.3448140252097085, 'p': 0.002}, 'mean_row_s2_score': {'actual': 1.0329959500444077, 'null_mean': 0.9270806241406666, 'null_std': 0.031060220363003797, 'z': 3.4099991779162684, 'p': 0.002}, 'mean_action_score': {'actual': 2.8915693124517627, 'null_mean': 2.8749905965360067, 'null_std': 0.01020187101819632, 'z': 1.6250662144410342, 'p': 0.058}, 'same_listener_direction_rate': {'actual': 1.0, 'null_mean': 1.0, 'null_std': 0.0, 'z': 0.0, 'p': 1.0}, 's2_rate': {'actual': 0.5217391304347826, 'null_mean': 0.4319130434782609, 'null_std': 0.030454194135711096, 'z': 2.9495473285628693, 'p': 0.012}}}, 'public_lb_observed': 0.5684860446, 'priority': 0.9427271560571463, 'config': {'name': 'listener_confirmed_shadow', 'boundary_classes': ['strict_jury', 'consensus_shadow'], 'require_cell_listener': True, 'require_row_s2_listener': True, 'min_transport_score': 0.44, 'max_cells': 28, 'max_extra_cells': 6, 'strict_base_scale': 0.82, 'extra_base_scale': 0.34, 'listener_gain': 0.2, 's2_gain': 0.09, 'probe_role': 'tests whether target-listener confirmed shadow cells are safer than broad shadow release'}, 'rank': 1}`, file `submission_hsjepa_cross_listener_transport_listener_confirmed_shadow_660faef3_uploadsafe.csv`, priority `0.9427`
- Cross-listener negative sensor: `{'file': 'submission_hsjepa_target_listener_route_lift_s2hub_listener_lift_jackpot_f2ab2816_uploadsafe.csv', 'public_lb': 0.5680255019, 'interpretation': 'direct listener-lift is not action-grade; use listener posterior only as a release/calibration prior'}`
- Counterfactual listener-dropout: `counterfactual_listener_dropout_ready`, information sensor `{'variant': 'dropout_fullfield_aggressive', 'submission_file': 'submission_hsjepa_counterfactual_listener_dropout_dropout_fullfield_aggressive_a433fbc0_uploadsafe.csv', 'priority': 1.2860211183353285}`, file `submission_hsjepa_counterfactual_listener_dropout_dropout_fullfield_aggressive_a433fbc0_uploadsafe.csv`, priority `1.2860`
- Listener-dropout thesis sensor: `{'variant': 'invariant_survivor', 'submission_file': 'submission_hsjepa_counterfactual_listener_dropout_invariant_survivor_7cde1a77_uploadsafe.csv', 'priority': 0.05}`, file `submission_hsjepa_counterfactual_listener_dropout_invariant_survivor_7cde1a77_uploadsafe.csv`, priority `0.0500`
- Spectral public-tangent solver: `spectral_public_tangent_ready`, first-mode variance `0.9629`, top-5 variance `0.9947`
- Spectral information sensor: `{'variant': 'anti_bad_tangent_pressure', 'submission_file': 'submission_hsjepa_spectral_public_tangent_anti_bad_tangent_pressure_6a93251a_uploadsafe.csv', 'priority': 1.4947903603985548}`, file `submission_hsjepa_spectral_public_tangent_anti_bad_tangent_pressure_6a93251a_uploadsafe.csv`, priority `1.4948`
- Spectral counter sensor: `{'variant': 'orthogonal_private_residual', 'submission_file': 'submission_hsjepa_spectral_public_tangent_orthogonal_private_residual_57ed54c2_uploadsafe.csv'}`, file `submission_hsjepa_spectral_public_tangent_orthogonal_private_residual_57ed54c2_uploadsafe.csv`
- Negative tangent invariant projection: `candidate_ready`, recommended `subject_prior_safe_projection`, file `submission_hsjepa_negative_tangent_invariant_subject_prior_safe_projection_ebdccca6_uploadsafe.csv`, bad cosine `-0.2259`, energy delta `-0.01685`, subject delta `-0.00106`
- LB-conditioned responsibility: `candidate_ready`, recommended `pure_lb_gradient_jackpot`, file `submission_hsjepa_lb_responsibility_pure_lb_gradient_jackpot_f0a8129d_uploadsafe.csv`, LOO corr `0.7300`, changed cells `24`, predicted delta `-7.11879`, energy delta `-0.03290`, bad cosine `0.0551`
- Mixture-listener responsibility: `candidate_ready`, recommended `target_listener_split_qs`, file `submission_hsjepa_mixture_listener_target_listener_split_qs_7a383104_uploadsafe.csv`, mixture LOO corr `0.9578` vs scalar `0.7300`, changed cells `30`, scalar delta `-4.34421`, mode delta `-0.53670`, conflict `0.2003`, bad cosine `-0.0042`
- Public/private subset tomography: `candidate_ready`, recommended `subset_label_direction_jackpot`, file `submission_hsjepa_subset_tomography_subset_label_direction_jackpot_d12af8ff_uploadsafe.csv`, source LOO corr `0.7300`, cells `115`, changed cells `18`, predicted delta `-4.92956`, inclusion `0.7612`, label confidence `0.8720`, private safety `0.5847`, toxicity `0.4255`
- Action decoder ablation: `action_decoder_ablation_ready_decoder_jury_leads`, recommended `{'family': 'decoder_order_jury', 'variant': 'family_supermajority', 'submission_file': 'submission_hsjepa_decoder_jury_family_supermajority_a7bc4ff7_uploadsafe.csv', 'priority': 1.394366527938867}`, big bet `{'family': 'route_frontier', 'variant': 'open_route_frontier', 'submission_file': 'submission_hsjepa_open_route_frontier_a1719e99_uploadsafe.csv', 'priority': 1.05448050759572}`

## Role-Based Outputs

| Role | Component | Changed cells | Changed rows | Claim |
| --- | --- | ---: | ---: | --- |
| `competition_primary` | Route-Conserving Objective Bridge | `82` | `41` | Public-sensitive S-stage driver actions should be paired with route-preserving bridge actions. |
| `interpretable_s2_hub` | S2 Listener Bridge | `68` | `34` | S2 acts as a public-sensitive listener/hub inside the objective sleep-stage route. |
| `human_state_probe` | Human-State Gated S2 Probe | `68` | `47` | OG human-state explains target/cell orientation, but not row assignment. |

## Stress Evidence

| Candidate | Route delta | Null route delta | S2 usage | Null S2 usage |
| --- | ---: | ---: | ---: | ---: |
| `route_conserving_objective_bridge_primary` | `-0.02457` | `-0.01090` | `0.780` | `0.615` |
| `s2_listener_bridge_interpretable` | `-0.02696` | `-0.01082` | `1.000` | `0.615` |

## Big-Bet Queue

다음 큰 실험은 HS-JEPA core/adaptor 경계를 바꾸는 실험이어야 한다.

- `Public/Private Subset Tomography Solver`: Scalar public feedback is generated by public subset inclusion times hidden label direction, while private action-health decides whether the move is safe outside that listener. Expected LB delta if true `-0.012`. Kill: Public-first, private-safe, boundary-probe, Q/S split, and orthogonal-private variants all fail public LB, meaning scalar public feedback is descriptive but not enough to identify an action-grade public/private subset equation.
- `Mixture-Listener Responsibility Solver`: The public LB is not one listener; it is a scalar readout of multiple latent listener heads, and Q/S actions may need different heads. Expected LB delta if true `-0.01`. Kill: Target-split, consensus, and residual-conflict variants all fail public LB, meaning public LB anchors are too scalar/noisy to identify action-grade latent listeners.
- `LB-Conditioned Responsibility Solver`: The public LB can be treated as an external listener whose scalar observations reveal row-target action responsibility. Expected LB delta if true `-0.008`. Kill: Pure-gradient and invariant-safe variants both fail public LB, meaning scalar public listener responsibility is descriptive but not enough without a hidden public/private row-support assignment.
- `Negative Tangent Invariant Projection Solver`: A negative public representation is useful only when its inverse can be projected onto label-valid human-state invariants. Expected LB delta if true `-0.006`. Kill: Projection candidates worsen public LB like naive anti-tangent probes, meaning public-bad geometry is diagnostic but not yet an invertible action equation even under target/subject invariants.
- `Spectral Public-Tangent Solver`: Known post-H057 public failures are not independent mistakes; they collapse onto a low-rank public-bad action tangent. Expected LB delta if true `-0.004`. Kill: Anti-tangent and orthogonal residual sensors both worsen public LB, meaning the low-rank tangent is descriptive but not an invertible action equation.
- `Counterfactual Listener-Dropout Solver`: A healthy HS-JEPA action should survive when one listener is masked, while failed public sensors become action-toxicity evidence rather than discarded submissions. Expected LB delta if true `-0.003`. Kill: Aggressive listener-dropout and inversion both fail public LB, meaning listener-dropout geometry is not enough to solve the public/private row-target equation.
- `Action Decoder Ablation Suite`: The next breakthrough comes from choosing the correct action-decoder order, not from adding more latent features. Expected LB delta if true `-0.0025`. Kill: Public LB contradicts the top-ranked decoder order, or route-first gains vanish under stronger null matching.
- `OG-only Human-State Assignment Teacher`: The public-sensor teacher can be replaced by personal/cohort/time human-state consistency. Expected LB delta if true `-0.003`. Kill: Masked row-support keeps failing subject/date/order stress or cannot be converted into safe row-target actions.
- `Route-Frontier Action Decoder`: The action decoder should select route-manifold frontier moves first, then check row-support and toxicity. Expected LB delta if true `-0.0025`. Kill: Public LB worsens or matched-null frontier score fails after larger candidate pools are used.
- `Route-Toxicity Fusion Decoder`: Route-frontier action ordering and factorized action-health are not alternatives; safe actions need both. Expected LB delta if true `-0.0025`. Kill: Public LB says plain route-frontier wins, or fusion only improves local toxicity while harming route/action response.
- `Decoder-Order Jury Solver`: Safe row-target assignment is a cross-decoder jury, not a single route or toxicity score. Expected LB delta if true `-0.0025`. Kill: Public LB worsens or underperforms route-frontier, meaning consensus is too conservative or action-health removes useful route signal.
- `Hard-World Mixture Toxicity Decoder`: H088-like hard-world toxicity is anti-correlated with broad public-bad toxicity, so action-health must be factorized. Expected LB delta if true `-0.0025`. Kill: Broad toxicity predicts H088 well, or mixture safety does not beat matched null after target/source matching.
- `Masked Row-Support Action Decoder`: The masked row-support representation can choose which route-conserving S2/stage bundles are safe enough to move. Expected LB delta if true `-0.002`. Kill: Public LB worsens or route/null stress remains weak after increasing row-support selectivity.
- `Decoder Boundary Tomography Solver`: The strict cross-decoder jury may be correct but too conservative; rejected cells split into weak consensus, route-only, and fusion-only worlds. Expected LB delta if true `-0.002`. Kill: All boundary probes worsen public LB, meaning strict cross-decoder consensus is the current safe frontier.
- `Core-Mediated Action Release`: A reusable HS-JEPA core should mediate real row-target actions before the sleep adapter releases them. Expected LB delta if true `-0.002`. Kill: Core-mediated candidates underperform the strict jury and boundary tomography, meaning generic core release is diagnostic but not yet the competition action equation.
- `Core Release Ablation Probe`: A real HS-JEPA architecture must expose which core module over-constrains or protects row-target action release. Expected LB delta if true `-0.002`. Kill: All module-removal probes match full-core and public LB cannot distinguish them, meaning this ablation axis is not the current bottleneck.
- `Core-Health Calibrated Release`: Dataset-free HS-JEPA action-health failure modes should calibrate the real sleep-adapter action boundary. Expected LB delta if true `-0.002`. Kill: Guarded release loses to relaxed pressure or to strict jury, meaning the current generic action-health prior is useful diagnostically but not action-grade for this adapter.
- `Cross-Listener Transport Decoder`: Target-listener posterior is not an action generator; it is a transport calibrator over route/fusion/core-safe actions. Expected LB delta if true `-0.002`. Kill: Public LB says listener-confirmed transport underperforms strict jury/core-health, meaning listener posterior remains diagnostic and not action-boundary evidence.
- `Listener-Invariant Contrastive Decoder`: A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone. Expected LB delta if true `-0.002`. Kill: Listener gain and invariant energy remain anti-correlated on strong candidates.
- `Private-Safe Toxicity Field`: The plateau comes from actions that help public-like rows but poison private-like rows. Expected LB delta if true `-0.0015`. Kill: Toxicity score only recovers known public failures, fails hard-world anchors, or does not separate matched local nulls.

## Boundaries

현재 패키지는 다음 경계를 명시한다.

- Pure OG-only model: `False`
- Uses public LB sensor: `True`
- Uses proprietary embedding API in team runner: `False`
- Human-state role: `orientation diagnostic, not complete row-target assignment solver`
- Competition decoder role: `public-sensitive row-target action solver with route-conserving S2 bridge`

따라서 논문에서는 HS-JEPA의 representation idea와 competition-specific action decoder를 분리해서 주장해야 한다.

## Team Reproduction

```bash
python3 team_hsjepa_end_to_end/run_full_team_hsjepa_package.py
```

Generated supporting reports:

- `/Users/kbsoo/Downloads/cl2/team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_architecture_readiness_report.json`
- `/Users/kbsoo/Downloads/cl2/team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_reproducibility_contract.json`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/hsjepa_core_manifest.json`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/hsjepa_core_ablation_contract.json`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/hsjepa_core_reference_run.json`
- `/Users/kbsoo/Downloads/cl2/hsjepa_core/outputs/hsjepa_core_module_benchmark.json`
- `/Users/kbsoo/Downloads/cl2/team_hsjepa_end_to_end/outputs/route_conserving_s2_bridge/hsjepa_core_adapter_boundary_audit.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/sleep_competition_adapter_report.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/hsjepa_big_bet_queue.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/assignment_gap_decomposition_probe.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/hidden_row_support_sensor_probe.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/masked_row_support_objective_probe.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/row_support_strict_action_decoder/row_support_strict_action_decoder_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/route_frontier_action_decoder/route_frontier_action_decoder_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/route_toxicity_fusion_decoder/route_toxicity_fusion_decoder_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/decoder_order_jury_solver/decoder_order_jury_solver_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/decoder_boundary_tomography_solver/decoder_boundary_tomography_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/core_mediated_action_release/core_mediated_action_release_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/core_release_ablation_probe/core_release_ablation_probe_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/core_health_calibrated_release/core_health_calibrated_release_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/cross_listener_transport_decoder/cross_listener_transport_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/counterfactual_listener_dropout_solver/counterfactual_listener_dropout_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/spectral_public_tangent_solver/spectral_public_tangent_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/negative_tangent_invariant_projection_solver/negative_tangent_invariant_projection_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/lb_conditioned_responsibility_solver/lb_conditioned_responsibility_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/mixture_listener_responsibility_solver/mixture_listener_responsibility_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite.json`
