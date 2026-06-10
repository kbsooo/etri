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
6. Anti-Shortcut Validation: Stress-test the representation and action field against nulls, cohort shifts, time shifts, and shortcut sensors.

Sleep competition adapter:

This adapter converts HS-JEPA Core into a sleep-log competition system by supplying Q/S listeners, a route invariant, public-sensor action evidence, and upload-safe sparse row-target decoding.

이번 수면 대회에서는 listener가 Q1/Q2/Q3/S1/S2/S3/S4로, invariant가 Q/S route energy로, action-health가 public/private toxicity 및 feasible-bundle stress로 구현되었다. 새 hard-world probe는 broad toxicity와 H088 toxicity가 역상관될 수 있음을 보여주므로, action-health는 단일 위험 점수가 아니라 factorized energy head로 다루어야 한다. 핵심은 `S2` 자체가 아니라, hidden state를 직접 label로 쓰지 않고 core의 listener/action/invariant 경로를 adapter가 안전한 sparse row-target action으로 번역한다는 점이다.

## Core / Adapter Evidence

- Core status: `core_ready_for_adapter` (`5/5` gates)
- Core ablation contract: `ablation_contract_ready` (`6` ablations)
- Core/adapter boundary audit: `core_adapter_boundary_verified` (`6/6` checks)
- Core operational violations: imports `0`, strings `0`
- Adapter status: `adapter_ready_with_public_sensor_boundary`
- Big-bet queue: `big_bet_queue_ready` (`10` bets)

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
- Portability checks: `5/6`
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
- Listener-invariant probe: `listener_invariant_decoder_not_ready`
- Listener-route Spearman: `-0.0313`
- Private-safe toxicity probe: `toxicity_field_promising_with_hardworld_gap`
- Toxicity mean LOO AUC: `0.7880`
- Toxicity worst LOO AUC: `0.3683`
- Hard-world factorization probe: `hardworld_mixture_factorization_required`
- Broad toxicity -> H088 AUC: `0.3683`
- Broad/H088 Spearman: `-0.4276`

가장 중요한 남은 과제는 target route가 아니라 hidden row-support sensor를 안전한 row-target action으로 번역하는 것이다. 이제 row-support는 완전히 죽은 가설이 아니라 teacher-transfer와 masked-family objective에서 부분적으로 살아있는 가설로 바뀌었다. 특히 seven-target prediction landscape와 human/cohort context를 합친 portable composite가 row-support를 상당 부분 복원하고, human-only/prediction-only/masked-route view도 신호를 유지한다. 첫 strict action decoder는 null 대비 safety는 강하지만 route-gain 우위가 약했다. 새 route-frontier decoder는 반대로 route manifold frontier를 먼저 고르고 support/toxicity를 통과시키며, local broad/matched null은 이겼다. route-toxicity fusion decoder는 여기서 한 단계 더 나아가 route-first와 factorized action-health를 조합한다. decoder-order jury solver는 이 둘이 같은 row-target과 방향에 합의할 때만 action을 방출한다. 다만 이것도 아직 sleep adapter의 LB sensor이지 private-safe release claim은 아니다.

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
9. Decode bounded actions that improve listener fit while preserving the invariant.
10. Reject shortcuts with cohort/time/group/null stress tests.
11. In the sleep-log case study, instantiate the invariant as Q/S route energy and the decoder as the S2 bridge.
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

- `Action Decoder Ablation Suite`: The next breakthrough comes from choosing the correct action-decoder order, not from adding more latent features. Expected LB delta if true `-0.0025`. Kill: Public LB contradicts the top-ranked decoder order, or route-first gains vanish under stronger null matching.
- `OG-only Human-State Assignment Teacher`: The public-sensor teacher can be replaced by personal/cohort/time human-state consistency. Expected LB delta if true `-0.003`. Kill: Masked row-support keeps failing subject/date/order stress or cannot be converted into safe row-target actions.
- `Masked Row-Support Action Decoder`: The masked row-support representation can choose which route-conserving S2/stage bundles are safe enough to move. Expected LB delta if true `-0.002`. Kill: Public LB worsens or route/null stress remains weak after increasing row-support selectivity.
- `Route-Frontier Action Decoder`: The action decoder should select route-manifold frontier moves first, then check row-support and toxicity. Expected LB delta if true `-0.0025`. Kill: Public LB worsens or matched-null frontier score fails after larger candidate pools are used.
- `Route-Toxicity Fusion Decoder`: Route-frontier action ordering and factorized action-health are not alternatives; safe actions need both. Expected LB delta if true `-0.0025`. Kill: Public LB says plain route-frontier wins, or fusion only improves local toxicity while harming route/action response.
- `Decoder-Order Jury Solver`: Safe row-target assignment is a cross-decoder jury, not a single route or toxicity score. Expected LB delta if true `-0.0025`. Kill: Public LB worsens or underperforms route-frontier, meaning consensus is too conservative or action-health removes useful route signal.
- `Listener-Invariant Contrastive Decoder`: A correction should be selected by agreement between listener responsibility and invariant energy, not public utility alone. Expected LB delta if true `-0.002`. Kill: Listener gain and invariant energy remain anti-correlated on strong candidates.
- `Private-Safe Toxicity Field`: The plateau comes from actions that help public-like rows but poison private-like rows. Expected LB delta if true `-0.0015`. Kill: Toxicity score only recovers known public failures, fails hard-world anchors, or does not separate matched local nulls.
- `Hard-World Mixture Toxicity Decoder`: H088-like hard-world toxicity is anti-correlated with broad public-bad toxicity, so action-health must be factorized. Expected LB delta if true `-0.0025`. Kill: Broad toxicity predicts H088 well, or mixture safety does not beat matched null after target/source matching.
- `Cross-Listener Human-State Transport`: Subjective Q and objective S labels are different listeners of one human state, not separate tasks. Expected LB delta if true `-0.001`. Kill: Q-S bridge actions fail null tests or replicate the already-killed subjective-shadow bridge.

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
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/action_decoder_ablation_suite/hsjepa_action_decoder_ablation_suite.json`
