# HS-JEPA Core Evidence Ledger

## 한 줄 결론

HS-JEPA core는 label을 직접 맞히는 classifier가 아니다.
현재 증거상 더 정확한 정의는 다음이다.

```text
visible human-life context
  -> hidden human-state / listener-responsibility representation
  -> action-health geometry
  -> competition adapter가 sparse row-target correction으로 번역
```

즉 논문에서 HS-JEPA를 설명할 때, row-target 후처리 트릭이 아니라
`보이는 생활 context로 보이지 않는 인간 상태 표현을 예측하는 core`를 먼저 세워야 한다.

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probabilities: `False`
- proprietary embedding API: `False`

## Evidence Table

| case | layer | metric | value | baseline | support |
| --- | --- | --- | --- | --- | --- |
| lifelog_core_state_geometry | core | neighbor_consistency_lift | 0.050603 | random_neighbor | positive |
| masked_context_world_model | core | component_corr_lift_vs_null | 0.248882 | shuffled_target_view | positive |
| subject_relative_human_state_world_model | core | calibrated_subject_heldout_delta_vs_prior | -0.000201 | fold_prior_low_trust_probe | positive_but_tiny |
| subject_invariant_prototype_grammar | core | predicted_energy_delta_vs_prior_logloss | -0.000484 | fold_prior_low_trust_probe | subject_invariant_prototype_grammar_core_positive_boundary |
| cross_subject_prototype_transport | core | transported_stats_probabilities_delta_vs_prior_logloss | -0.002026 | fold_prior_low_trust_probe | cross_subject_prototype_transport_core_positive |
| transported_prototype_listener_readout | frozen_probe_diagnostic | listener_conditioned_delta_vs_global_transport_logloss | -0.001376 | global_transported_prototype_stats_probabilities | transported_listener_readout_global_positive |
| label_free_transported_listener_responsibility | core_boundary | semantic_listener_delta_vs_global_transport_logloss | 0.000914 | global_transported_prototype | label_free_listener_responsibility_prior_positive |
| learned_listener_responsibility_pretext | core | best_learned_delta_vs_handcoded_semantic_logloss | -0.000495 | hand_coded_semantic_listener_responsibility | learned_listener_responsibility_beats_handcoded_positive |
| invariant_listener_responsibility_pretext | core_boundary | best_invariant_delta_vs_current_relative_logloss | -0.000258 | current_relative_semantic_listener_responsibility | invariant_listener_responsibility_beats_current_positive |
| multi_head_listener_responsibility_pretext | core_boundary | best_single_head_delta_vs_direct_semantic_logloss | -0.000175 | hand_coded_direct_semantic_listener_responsibility | future_head_positive_multihead_concat_boundary |
| listener_head_router_pretext | core_boundary | best_router_delta_vs_single_head_logloss | -0.000036 | best_single_future_listener_head | listener_head_router_beats_single_positive |
| learned_listener_head_router_core | core_boundary | best_learned_router_delta_vs_semantic_prior_logloss | -0.000068 | fixed_semantic_prior_listener_head_router | learned_listener_head_router_beats_semantic_positive |
| global_transport_residual_listener_router_core | core | best_learned_residual_delta_vs_global_transport_logloss | -0.000907 | global_transported_prototype | global_transport_residual_listener_router_positive |
| rhythm_conditioned_residual_listener_core | core | chronological_best_rhythm_delta_vs_global_transport_logloss | -0.002237 | global_transported_prototype | rhythm_context_temporal_decoder_with_gated_residual_subject_positive |
| rhythm_conditioned_action_health_core | negative_boundary | accepted_target_count_total | 0.000000 | listener_support_baseline_tail_safe_policy | negative |
| routine_break_world_model | core | routine_full_delta_vs_prior_logloss | -0.001673 | fold_prior_low_trust_probe | positive_but_small |
| sleep_pressure_world_model | core | sleep_pressure_full_delta_vs_prior_logloss | -0.000867 | fold_prior_low_trust_probe | positive_but_small |
| cohort_relative_world_model | core | cohort_relative_predicted_delta_vs_prior_logloss | -0.001381 | fold_prior_low_trust_probe | positive_with_leakage_boundary |
| multi_target_human_state_world_model | core | multi_target_predicted_delta_vs_prior_logloss | -0.001499 | fold_prior_low_trust_probe | positive_with_route_preservation |
| route_responsibility_world_model | core_diagnostic | route_weighted_delta_vs_base_multi_target_logloss | 0.000780 | route_preserving_multi_target_predicted | pretext_positive_downstream_negative_vs_base |
| listener_conditioned_route_readout | frozen_probe_diagnostic | listener_conditioned_delta_vs_multi_target_logloss | -0.001747 | route_preserving_multi_target_predicted | strong_positive_probe |
| subject_drift_world_model | core_boundary | subject_hsjepa_delta_vs_prior_logloss | -0.000168 | fold_prior_low_trust_probe | core_drift_weak_positive_boundary |
| episode_transition_retrieval | core_boundary | subject_rank_pct_lift_vs_random | 0.044611 | random_episode_candidate | rhythm_dominant_boundary |
| external_action_replay_geometry | core_to_adapter_probe | row_auc_z_vs_permuted_train | 8.375849 | permuted_teacher | strong_positive_probe |
| subject_invariant_listener_manifold | core | hsjepa_listener_ap_lift_minus_action_only | 0.191742 | action_geometry_only | strong_positive |
| listener_responsibility_field | core | masked_pretext_ap_lift_minus_listener_only | 0.014785 | listener_only | positive_but_small |
| signed_direction_translation | adapter_boundary | gain_sum_repaired_vs_previous_decoder | 2.206488 | previous_responsibility_decoder | adapter_positive_core_boundary |
| counterfactual_direction_pretext | negative_boundary | best_core_responsibility_gain_sum | -0.848511 | oracle_direction_available_but_hidden | negative |
| direct_label_prediction | negative_boundary | hsjepa_state_delta_vs_prior_logloss | 0.052697 | label_prior | negative |

## 무엇이 진짜 HS-JEPA Core 증거인가

### 1. Masked Context World Model

생활 로그를 semantic view로 나눈 뒤, 일부 view만 보고 가려진 target-view representation을 예측했다.
best view의 component-correlation lift는 `0.248882`로 shuffled target-view null보다 높다.

이것이 JEPA 느낌의 핵심이다.

```text
raw label prediction이 아니라
visible context -> hidden target representation prediction
```

### 2. Subject-Relative Human-State World Model

absolute state는 subject identity를 강하게 담지만, subject-relative world-state는
subject identity leakage를 크게 줄이면서 low-trust frozen probe에서 prior를 아주 작게 이겼다.
subject-heldout delta vs prior는 `-0.000201`이다.

이 결과는 효과 크기가 작다. 하지만 HS-JEPA를 competition adapter가 아니라
label-free human-state world model로 정립하는 데 필요한 첫 positive evidence다.

### 3. Subject-Invariant Prototype Grammar

absolute lifelog feature를 그대로 쓰면 subject identity shortcut이 강해진다.
이 실험은 각 subject 내부에서 raw lifelog를 상대화한 뒤, semantic view별 episode prototype을 만들고
보이는 view들로 가려진 prototype responsibility를 예측했다.

```text
subject-relative visible lifelog views
  -> hidden episode prototype grammar
  -> masked context predicts prototype responsibility
```

masked prototype pretext의 mean cross-entropy lift는
`0.072856`이고,
subject-heldout frozen probe에서 predicted grammar energy의 prior 대비 delta는
`-0.000484`이다.

중요한 점은 subject leakage가 크게 낮다는 것이다.
predicted grammar energy의 subject-id accuracy는
`0.231111`이고,
raw lifelog PCA reference는 약 `0.957778`이다.

따라서 이 실험은 다음 thesis를 지지한다.

```text
HS-JEPA는 사람마다 다른 절대 센서 크기를 외우는 대신,
각자의 평소 기준에서 오늘이 어떤 생활 episode 원형인지 표현한다.
```

다만 label-probe 효과는 아직 작다. LB breakthrough로 번역하려면
이 grammar를 listener/drift decoder가 읽어야 한다.

### 4. Cross-Subject Prototype Transport

이전 prototype grammar 실험이 full cohort 안에서만 성립한 것인지 확인하기 위해,
이번에는 fold마다 train subjects/blocks에서만 prototype grammar를 정의하고 held-out subject/block으로 운반했다.

```text
train subjects define subject-relative episode grammar
  -> held-out subject is transported into that grammar
  -> visible context predicts hidden transported prototype responsibilities
```

subject-heldout label-free pretext의 mean cross-entropy lift는
`0.060052`이다.
transported stats+probabilities frozen probe의 prior 대비 delta는
`-0.002026`이고,
stats-only frozen probe의 prior 대비 delta는
`-0.001411`이다.

raw lifelog PCA 대비 stats-only delta는
`-0.002261`이다.
subject-id leakage 기준으로 transported stats accuracy는
`0.273333`이고,
raw lifelog PCA reference는 `0.957778`이다.

따라서 이 실험은 HS-JEPA core에 더 강한 문장을 허용한다.

```text
HS-JEPA는 full cohort 안에서만 쓸 수 있는 subject-relative grammar가 아니라,
train subjects가 정의한 생활 episode grammar를 held-out subject로 운반할 수 있다.
```

단, probability-rich readout은 leakage가 커질 수 있다.
논문에서는 transport 가능성과 readout leakage risk를 분리해서 써야 한다.

### 5. Transported Prototype Listener Readout

cross-subject transport가 global representation으로만 의미 있는지, 아니면 target/listener별로
서로 다른 transported grammar view를 읽어야 하는지 검증했다.

```text
transported prototype grammar
  -> Q/S listener chooses a transported view
  -> frozen low-trust probe reads target-specific interface
```

subject-heldout에서 listener-conditioned readout은 global transported grammar 대비
`-0.001376` logloss 개선을 보였다.
prior 대비 delta는 `-0.002509`이고,
raw lifelog PCA 대비 delta는 `-0.003359`이다.
fold-level route win은 `23/35`이다.

stress 결과는 더 조심스럽다.

```text
row-block delta vs global: 0.000010
chronological delta vs global: -0.000919
```

따라서 이 결과는 core pretext가 아니라 core-interface diagnostic으로 둔다.
정확한 논문 문장은 다음이다.

```text
Transported grammar는 하나의 global latent보다,
listener별로 선택적으로 읽히는 interface일 때 더 강하다.
```

### 6. Label-Free Transported Listener Responsibility

위 listener readout은 frozen labels로 target별 view를 선택했다.
이 실험은 그 선택을 제거하고, target 설명과 transported prototype reliability만으로 listener responsibility를 만들었다.

```text
target description + transported prototype reliability
  -> label-free listener responsibility
  -> frozen low-trust probe
```

결과는 boundary다.

```text
delta vs prior: -0.000219
delta vs raw lifelog PCA: -0.001069
delta vs global transport: 0.000914
row-block delta vs global: 0.000044
chronological delta vs global: -0.001343
```

subject leakage는 raw/global보다 낮아진다.

```text
semantic listener leakage: 0.437778
global transport leakage: 0.542222
raw lifelog leakage: 0.957778
```

따라서 이 실험이 죽인 믿음은 분명하다.

```text
target 설명만으로 hand-coded listener responsibility를 만들면 충분하다.
```

살아남은 믿음은 이것이다.

```text
label-free listener responsibility 방향은 맞지만, 사람이 고정한 profile보다
pretext로 학습된 listener responsibility가 필요하다.
```

### 7. Learned Listener Responsibility Pretext

직전 boundary를 그대로 실험으로 바꿨다.
이번에는 hand-coded profile을 바로 쓰지 않고, visible human-life context가
transported prototype reliability에서 만든 hidden listener responsibility field를 예측하게 했다.

```text
visible human-life context
  -> hidden transported listener responsibility
  -> frozen low-trust probe
```

핵심 결과:

```text
best learned feature set: learned_semantic_balanced_listener_responsibility_calibrated10
delta vs hand-coded semantic: -0.000495
delta vs prior: -0.000715
delta vs raw lifelog PCA: -0.001565
delta vs global transport: 0.000419
row-block delta vs global: -0.000051
chronological delta vs global: -0.001510
```

가장 중요한 점은 open-loop prediction이 아니라 calibrated responsibility prediction이다.
open-loop는 top-1은 맞혀도 확률 geometry가 과신되어 pretext CE가 나빠진다.
prior-shrunk balanced responsibility는 pretext CE를 prior보다 이긴다.

subject-relative context variant는 더 논문적이다.

```text
relative balanced pretext CE lift vs prior: 0.029806
relative balanced subject leakage: 0.480000
global transport subject leakage: 0.542222
raw lifelog subject leakage: 0.957778
```

따라서 이번 결과는 HS-JEPA thesis를 강화하지만 동시에 제한한다.

```text
강화:
  listener responsibility는 label 없이 visible context에서 학습 가능하다.
  learned responsibility는 hand-coded semantic profile보다 downstream probe가 좋다.

제한:
  absolute context encoder는 subject shortcut을 많이 담는다.
  subject-heldout global transported grammar를 아직 넘지는 못한다.
```

다음 core는 learned responsibility를 유지하되,
subject-relative/future/cohort consistency로 shortcut을 누르는 방향이어야 한다.

### 8. Invariant Listener Responsibility Pretext

직전 learned responsibility는 hand-coded semantic profile을 이겼지만,
teacher가 current transported responsibility에 묶여 있었다.
이번에는 hidden teacher 자체를 더 human-state답게 바꿨다.

```text
current transported responsibility
  + same-subject future episode consistency
  + cross-subject cohort consistency
  -> invariant listener responsibility teacher
```

핵심 결과:

```text
best invariant feature set: future_only_relative_balanced_listener_responsibility_calibrated10
delta vs current-relative responsibility: -0.000258
delta vs prior: -0.000214
delta vs raw lifelog PCA: -0.001064
delta vs direct semantic responsibility: 0.000005
delta vs global transport: 0.000919
row-block delta vs global: -0.000612
chronological delta vs global: -0.001460
```

가장 중요한 positive signal은 future-only invariant responsibility다.
같은 사람의 미래 episode에서 반복되는 listener state를 teacher에 넣으면,
current-only subject-relative responsibility보다 subject-heldout downstream이 좋아진다.
또 row-block/chronological stress에서는 global transported grammar도 이긴다.

하지만 cohort-only result는 더 조심스럽다.

```text
cohort-only pretext CE lift vs prior: 0.025017
future-only pretext CE lift vs prior: 0.011514
best invariant subject leakage: 0.480000
current-relative subject leakage: 0.480000
global transport subject leakage: 0.542222
raw lifelog subject leakage: 0.957778
```

cohort-only는 pretext/top-1은 강하지만 downstream utility는 약하다.
이 결과가 죽인 믿음은 다음이다.

```text
pretext를 잘 맞히는 invariant teacher는 그대로 downstream label utility가 된다.
```

살아남은 더 정확한 믿음은 이것이다.

```text
HS-JEPA core에서 좋은 human-state teacher는
현재 상태, 개인의 미래 consistency, peer cohort consistency를 한 벡터로 섞는 것이 아니라
multi-head로 보존하고 listener가 필요한 head를 읽게 해야 한다.
```

### 9. Multi-Head Listener Responsibility Pretext

직전 결론을 그대로 반증했다.
이번에는 current/future/cohort responsibility를 하나의 smoothed teacher로 만들지 않고,
세 head를 따로 예측한 뒤 frozen listener probe가 single/concat/delta geometry를 읽게 했다.

```text
subject-relative visible context
  -> current listener responsibility head
  -> future-consistent listener responsibility head
  -> cohort-consistent listener responsibility head
  -> frozen listener reads head geometry
```

결과는 positive와 negative가 같이 나왔다.

```text
best single head: head_future_relative_listener_responsibility_calibrated10
best single-head logloss: 0.677463
best multi-head feature set: multihead_current_future_listener_responsibility_calibrated10
best multi-head logloss: 0.677735
single delta vs direct semantic: -0.000175
single delta vs prior: -0.000395
single delta vs raw lifelog PCA: -0.001050
multi delta vs single: 0.000272
multi delta vs global transport: 0.001011
row-block multi delta vs global: -0.000265
chronological multi delta vs global: -0.001451
```

살아남은 core evidence:

```text
future-consistent listener responsibility is the strongest compact head.
It beats prior, raw lifelog PCA, and hand-coded direct semantic responsibility.
```

죽은 믿음:

```text
Naively concatenating current/future/cohort heads lets the downstream listener automatically route.
```

leakage 관점에서는 multi-head가 single future head보다 약간 낮지만,
subject-heldout utility는 낮다.

```text
best single-head leakage: 0.475556
best multi-head leakage: 0.466667
```

따라서 다음 architecture 문장은 더 정확해졌다.

```text
HS-JEPA does not need a larger undifferentiated latent bundle.
It needs a listener router that chooses current/future/cohort heads per target.
```

### 10. Listener Head Router Pretext

직전 실험은 "router가 필요하다"는 결론을 남겼다.
이번에는 concat을 버리고 label-free router가 current/future/cohort head를 soft routing하게 했다.

```text
current / future / cohort listener heads
  -> label-free head router
  -> routed human-state interface
```

결과는 작지만 architecture 관점에서 중요하다.

```text
best router: semantic_prior_router_listener_responsibility_calibrated10
best router logloss: 0.677427
best single head: head_future_relative_listener_responsibility_calibrated10
best single-head logloss: 0.677463
router delta vs single: -0.000036
router delta vs prior: -0.000430
router delta vs raw lifelog PCA: -0.001086
router delta vs direct semantic: -0.000211
router delta vs naive multi-head: -0.000539
router delta vs global transport: 0.000703
row-block router delta vs global: -0.000166
chronological router delta vs global: -0.001477
```

살아남은 믿음:

```text
Target-aware listener-head routing is useful.
It beats best single future head and naive multi-head concat without using labels in the router.
```

죽은 믿음 또는 약해진 믿음:

```text
confidence / entropy / energy heuristics alone are already a sufficient learned router.
```

best가 dynamic confidence router가 아니라 semantic-prior router였다는 점을 과장 없이 남긴다.

```text
best router leakage: 0.462222
best single-head leakage: 0.475556
```

따라서 다음 core target은 분명하다.

```text
Learn the listener-head router as a JEPA pretext objective,
instead of relying on fixed semantic priors.
```

### 11. Learned Listener-Head Router Core

직전 실험은 fixed semantic-prior router가 best single future head를 이긴다는 결과를 남겼다.
이번 실험은 그 prior를 사람이 고정하지 않고, label-free hidden head-suitability field를
visible context와 predicted current/future/cohort heads에서 예측하게 했다.

```text
visible subject-relative human-life context
  + predicted current/future/cohort listener heads
  -> hidden head-suitability field prediction
  -> learned listener-head router
  -> routed HS-JEPA interface
```

핵심 결과:

```text
best learned router: learned_semantic_router_context_headsignal_listener_responsibility_calibrated10
best learned router logloss: 0.677359
fixed semantic-prior router logloss: 0.677427
best single head: head_future_relative_listener_responsibility_calibrated10
best single-head logloss: 0.677463
learned delta vs fixed semantic router: -0.000068
learned delta vs single: -0.000103
learned delta vs prior: -0.000498
learned delta vs raw lifelog PCA: -0.001154
learned delta vs direct semantic: -0.000279
learned delta vs naive multi-head: -0.000606
learned delta vs global transport: 0.000636
row-block learned delta vs global: -0.000505
chronological learned delta vs global: -0.001486
```

leakage도 의미가 있다.

```text
best learned router leakage: 0.446667
fixed semantic-prior router leakage: 0.462222
best single future head leakage: 0.475556
```

살아난 믿음:

```text
HS-JEPA can learn listener-head routing as a label-free hidden-state pretext,
not only as a hand-fixed semantic prior.
```

아직 죽지 않은 경계:

```text
The learned router beats semantic prior and best single head,
but it still does not beat global transported prototype grammar on subject-heldout.
```

따라서 논문적으로는 이 실험을 "완성된 decoder"가 아니라
`learned listener routing core evidence with global-transport boundary`로 기록한다.

### 12. Global Transport Residual Listener-Router Core

직전 실험에서 learned listener-head router는 fixed semantic prior와 best single head를 이겼지만,
subject-heldout global transport는 넘지 못했다. 그래서 질문을 replacement가 아니라 interface로 바꿨다.

```text
cross-subject transported prototype grammar
  + semantic listener router
  + learned listener-head router
  + learned-minus-semantic residual delta
  -> residual listener interface
```

핵심 결과:

```text
best residual feature set: global_plus_semantic_and_learned_router_calibrated10
best residual logloss: 0.675817
global transport logloss: 0.676724
learned router alone logloss: 0.677359
residual delta vs global: -0.000907
residual delta vs learned alone: -0.001542
row-block delta vs global: -0.000428
chronological delta vs global: 0.001965
```

subject leakage도 중요한 증거다.

```text
best residual leakage: 0.440000
global transport leakage: 0.542222
raw lifelog leakage: 0.940000
```

살아난 믿음:

```text
HS-JEPA core는 하나의 monolithic human-state vector가 아니다.
운반 가능한 human-state grammar를 backbone으로 두고,
listener-specific residual router가 target별 readout을 조절해야 한다.
```

하지만 같은 결과가 죽인 믿음도 있다.

```text
residual listener routing만 키우면 temporal drift까지 해결된다.
```

chronological delta가 양수이므로 temporal drift/action-health decoder는 별도 인터페이스로 풀어야 한다.

### 13. Rhythm-Conditioned Residual Listener Core

global residual listener router가 chronological에서 독성을 보였기 때문에,
이번 실험은 visible calendar/rhythm context가 temporal decoder와 residual listener readout을 분리할 수 있는지 검증했다.

```text
calendar rhythm confidence / entropy / energy
  -> rhythm stability gate
  -> stable residual listener channel
  -> unstable residual listener channel
  -> frozen subject-heldout / row-block / chronological probes
```

핵심 결과:

```text
subject best feature: global_plus_residual_and_rhythm_gated_residual_calibrated10
subject delta vs global: -0.001443
subject delta vs plain residual: -0.000537
row-block best feature: global_plus_rhythm_context_calibrated10
row-block delta vs global: -0.000968
row-block delta vs plain residual: -0.000541
chronological best feature: rhythm_context_calibrated10
chronological best logloss: 0.669300
chronological plain residual delta vs global: 0.001965
chronological rhythm delta vs global: -0.002237
chronological rhythm delta vs plain residual: -0.004202
chronological gated residual delta vs global: 0.000027
```

subject leakage:

```text
rhythm context leakage: 0.113333
best gated residual leakage: 0.420000
plain residual leakage: 0.440000
global transport leakage: 0.542222
raw lifelog leakage: 0.940000
```

정확한 해석은 다음이다.

```text
temporal drift는 rhythm context가 가장 잘 읽는다.
subject/block readability는 rhythm-gated residual이 더 좋다.
따라서 HS-JEPA core는 rhythm-conditioned temporal decoder와
rhythm-gated listener residual interface를 분리해야 한다.
```

과장하면 안 되는 점도 분명하다.

```text
gated residual이 chronological을 완전히 해결한 것은 아니다.
chronological에서 best는 gated residual이 아니라 rhythm_context다.
```

논문 문장으로는 다음이 가장 안전하다.

```text
HS-JEPA separates human-state readability into two interfaces:
a rhythm-conditioned temporal decoder for chronological drift, and a
rhythm-gated listener residual for subject/block-invariant readout.
```

### 14. Rhythm-Conditioned Action-Health Boundary

직전 실험이 temporal decoder와 residual listener interface를 분리했다면,
이번 실험은 그 분리가 곧바로 action-health release gate가 되는지 검증했다.

```text
transported human-state grammar
  + listener residual interface
  + rhythm-conditioned temporal decoder
  -> hidden action-health / toxicity representation
  -> tail-safe row-target release policy
```

핵심 결과:

```text
accepted target count total: 0
subject health-AUC delta vs listener baseline: -0.006253
chronological health-AUC delta vs listener baseline: -0.001439
subject toxic-tail-AUC delta vs listener baseline: 0.001081
chronological toxic-tail-AUC delta vs listener baseline: -0.001028
```

죽은 믿음:

```text
rhythm-conditioned residual interface alone is already an action-grade decoder.
```

정확한 해석:

```text
HS-JEPA core는 hidden human-state/readability representation을 만든다.
하지만 release-grade row-target action은 별도의 action-tail teacher,
tail-safe utility objective, 또는 competition adapter를 거쳐야 한다.
```

이 negative boundary는 논문적으로 중요하다.
HS-JEPA를 "label predictor"나 "제출값 생성기"로 과장하지 않고,
human-state world model과 action decoder 사이의 경계를 분명히 해주기 때문이다.

### 15. Routine-Break World Model

단순 current-state target 대신 subject-relative current state, previous-episode jump,
rolling personal-baseline residual을 hidden target으로 만들었다.
즉 질문을 다음처럼 바꿨다.

```text
visible human-life context
  -> hidden routine-break / episode-reset representation
```

subject-heldout low-trust frozen probe에서 prior 대비 delta는
`-0.001673`이다.
효과 크기는 여전히 작지만, 이전 subject-relative world model보다 더 선명한 core-positive signal이다.

### 15. Sleep-Pressure World Model

수면 label을 직접 target으로 쓰지 않고, night disturbance, physiological load,
social/cognitive arousal, rest-environment stability, calendar routine pressure를
label-free hidden target으로 만들었다.

```text
visible daily human-life context
  -> hidden sleep-pressure / recovery-load representation
```

subject-heldout low-trust frozen probe에서 prior 대비 delta는
`-0.000867`이다.
pretext 예측성은 강하지만 label probe 효과는 작다. 이 결과는 HS-JEPA가
sleep-pressure representation을 만들 수 있다는 core evidence이면서,
그 representation을 Q/S label로 번역하려면 listener/action-health adapter가 필요하다는 경계이기도 하다.

### 16. Cohort-Relative World Model

routine-break와 sleep-pressure 기반 subject fingerprint로 singleton 없는 peer cohort를 만들고,
오늘의 state를 개인 기준과 peer 기준에서 동시에 해석했다.

```text
visible daily human-life context
  -> hidden personal-vs-peer cohort-relative representation
```

subject-heldout low-trust frozen probe에서 predicted cohort state의 prior 대비 delta는
`-0.001381`이다.
이는 현재 core world-model 계열에서 가장 강한 축에 속한다.

다만 중요한 경계가 있다.

```text
observed/full cohort geometry는 subject identity shortcut이 강하다.
core evidence는 observed state가 아니라 predicted cohort-relative state에만 둔다.
```

### 17. Multi-Target Human-State World Model

routine-break, sleep-pressure, cohort-relative hidden target을 따로 쓰지 않고,
하나의 route-preserving predicted bundle로 묶었다.

```text
visible human-life context
  -> predicted routine-break state
  -> predicted sleep-pressure state
  -> predicted personal-vs-peer cohort state
  -> route-preserving human-state bundle
```

subject-heldout low-trust frozen probe에서 이 bundle의 prior 대비 delta는
`-0.001499`이다.

중요한 ablation은 다음이다.

```text
predicted axes를 그대로 보존하면 positive.
PCA로 하나의 compressed latent로 뭉치면 negative.
```

따라서 HS-JEPA core thesis는 "모든 상태를 하나의 벡터로 압축한다"가 아니다.
더 정확한 thesis는 다음이다.

```text
여러 hidden human-state target representation을 예측하되,
downstream listener가 구분할 수 있도록 route axes를 보존한다.
```

### 18. Route-Responsibility Diagnostic

multi-target bundle 위에서 다른 route들로 held-out route를 예측하고,
그 residual energy로 label-free route responsibility를 만들었다.

```text
other predicted routes
  -> held-out route representation
  -> cross-route residual energy
  -> route responsibility
```

route pretext lift는 `0.872891`로 매우 강하다.
하지만 responsibility-weighted axes는 base multi-target predicted bundle 대비
`0.000780`만큼 logloss가 악화된다.

따라서 현재 결론은 다음이다.

```text
route responsibility는 label 없이 관측 가능하다.
하지만 단순 route weighting은 좋은 route-preserving bundle을 대체하지 못한다.
```

이것은 실패라기보다 HS-JEPA architecture boundary다.
다음 core는 route를 누르는 것이 아니라, listener가 route를 선택적으로 읽는 구조여야 한다.

### 19. Listener-Conditioned Route Readout

route-preserving multi-target bundle을 만든 뒤, frozen probe에서 target/listener별 route readout을 선택했다.
이 단계는 label-free core pretext가 아니라 frozen probe diagnostic이다.
하지만 논문적으로 중요하다.

```text
same HS-JEPA route bundle
  -> Q2 reads sleep-pressure
  -> S2 reads routine+cohort
  -> S3 reads cohort-relative
  -> S4 reads routine-break
```

subject-heldout low-trust probe에서 listener-conditioned route readout은
base multi-target bundle 대비 `-0.001747` logloss 개선을 보였다.
선택 route는 fold 단위로 `25/35` wins를 기록했다.

이 결과가 의미하는 바는 다음이다.

```text
HS-JEPA core의 좋은 interface는 하나의 압축 latent도,
하나의 global route bundle도 아니다.
route axes를 보존하고, downstream listener가 target별로 다른 route를 읽게 해야 한다.
```

### 20. Subject-Invariant Listener Manifold

subject-invariant jury release target은 action geometry만으로도 어느 정도 분리될 수 있지만,
HS-JEPA listener manifold는 action-only 대비 AP lift가 `0.191742` 더 크다.

이 결과는 HS-JEPA core가 단순 action magnitude가 아니라,
row-target listener가 어떤 hidden state에서 반응해야 하는지를 더 잘 표현한다는 증거다.

### 21. Listener Responsibility Field

action을 바로 고르지 않고 먼저 `어느 row-target listener가 책임을 가져야 하는가`를 예측하면,
masked-pretext responsibility가 listener-only보다 AP lift `0.014785`만큼 앞선다.

이 증거는 크지는 않지만 논문적으로 중요하다.
HS-JEPA contribution을 `확률값 보정`이 아니라 `listener responsibility representation`으로 둘 수 있기 때문이다.

## 무엇을 과장하면 안 되는가

### Counterfactual Direction은 아직 Core가 아니다

raw/inverse direction oracle은 responsibility-selected cells에서 큰 양수 gain을 갖지만,
action-probability-free core가 복원한 best direction gain은 `-0.848511`이다.

따라서 현재는 다음 문장이 더 정확하다.

```text
HS-JEPA core는 어디를 볼지(listener responsibility)는 일부 복원하지만,
raw/inverse direction 자체는 아직 release-grade core representation으로 복원하지 못했다.
```

이것은 실패가 아니라 중요한 경계다.
논문에서 direction까지 core 성과로 과장하지 않게 해준다.

### Direct Label Classifier는 아니다

HS-JEPA state-only label probe는 prior 대비 logloss가 `0.052697` 악화된다.
따라서 다음 문장은 쓰면 안 된다.

```text
HS-JEPA core만으로 Q/S label을 직접 잘 예측한다.
```

정확한 문장은 이렇다.

```text
HS-JEPA core는 label classifier가 아니라,
hidden human-state와 action-health를 더 읽기 쉬운 geometry로 바꾸는 representation module이다.
```

### Signed Direction은 Adapter Boundary다

signed listener direction 실험은 이전 responsibility decoder의 OOF gain을
`2.206488`만큼 수리했다.
하지만 best direction family는 action geometry다.

따라서 이것은 pure core 승리가 아니라,
core가 위치를 좁히고 adapter가 방향 독성을 수리한 boundary case다.

## Candidate Files

| case | candidate | role |
| --- | --- | --- |
| masked_context_world_model | submission_hsjepa_masked_context_world_model_core_ff673c9a_uploadsafe.csv | core |
| subject_relative_human_state_world_model | submission_hsjepa_human_state_world_model_probe_69ab0808_uploadsafe.csv | core |
| routine_break_world_model | submission_hsjepa_routine_break_world_model_probe_1cc38f16_uploadsafe.csv | core |
| sleep_pressure_world_model | submission_hsjepa_sleep_pressure_world_model_probe_2ed37b9a_uploadsafe.csv | core |
| cohort_relative_world_model | submission_hsjepa_cohort_relative_world_model_probe_24fd334b_uploadsafe.csv | core |
| multi_target_human_state_world_model | submission_hsjepa_multi_target_human_state_world_model_probe_d3165dfa_uploadsafe.csv | core |
| route_responsibility_world_model | submission_hsjepa_route_responsibility_world_model_probe_bab0d5b7_uploadsafe.csv | core_diagnostic |
| listener_conditioned_route_readout | submission_hsjepa_listener_conditioned_route_readout_probe_74befb45_uploadsafe.csv | frozen_probe_diagnostic |
| subject_invariant_listener_manifold | submission_hsjepa_subject_invariant_listener_manifold_anchor_free_40628330_uploadsafe.csv | core |
| listener_responsibility_field | submission_hsjepa_subject_invariant_listener_responsibility_field_a9a2ea47_uploadsafe.csv | core |
| signed_direction_translation | submission_hsjepa_signed_listener_responsibility_direction_3a0fba1d_uploadsafe.csv | adapter_boundary |
| counterfactual_direction_pretext | submission_hsjepa_counterfactual_direction_pretext_d9e2a870_uploadsafe.csv | negative_boundary |

## Paper Thesis로 쓰기 좋은 문장

> HS-JEPA는 생활 로그를 직접 label로 매핑하지 않는다. 대신 보이는 인간 생활 context에서
> 보이지 않는 human-state와 listener-responsibility representation을 예측하고,
> 이 representation이 row-target action-health를 더 잘 분리하도록 만든다.
> 대회 adapter는 이 core geometry를 sparse correction으로 번역하는 별도 층이다.

## 다음 Big Bet

현재 가장 중요한 미해결 문제는 core representation의 효과 크기다.

```text
subject-relative world model: tiny positive
subject-invariant prototype grammar: pretext positive, low subject leakage, weak probe positive
cross-subject prototype transport: train-subject grammar transports to held-out subjects, but readout leakage must be controlled
transported prototype listener readout: global transported grammar보다 listener-specific readout이 subject-heldout에서 강하지만 frozen-probe diagnostic이다
label-free transported listener responsibility: prior/raw는 이기지만 global transport는 못 이겨 hand-coded semantic profile의 한계를 보인다
learned listener responsibility pretext: labels 없이 hand-coded profile보다 좋은 responsibility를 학습하지만 shortcut/leakage control이 남았다
invariant listener responsibility pretext: future consistency는 current-only보다 좋고 row/chron stress에서 강하지만, cohort pretext accuracy는 downstream utility와 분리된다
multi-head listener responsibility pretext: compact future head는 positive지만 naive head concat은 best single을 못 이겨 listener router가 필요하다
listener-head router pretext: semantic-prior router가 best single future head와 naive concat을 이기지만 confidence-only router는 아직 약하다
learned listener-head router core: hidden head-suitability pretext가 fixed semantic-prior router와 best single head를 이기지만 global transport는 아직 못 넘는다
routine-break world model: small positive and stronger hidden target
sleep-pressure world model: strong pretext, small label-probe positive
cohort-relative world model: predicted state positive, observed/full shortcut 위험
multi-target world model: route-preserving bundle positive, compressed latent negative
route responsibility diagnostic: pretext positive, route weighting은 base를 못 이김
listener-conditioned route readout: frozen probe에서 route별 listener interface positive
responsibility field: positive but small
direction/action translation: adapter 의존
direct label prediction: mostly negative without low-trust calibration
```

따라서 다음 실험은 adapter를 더 조정하는 것이 아니라,
subject-relative human-state target을 더 강하게 만들어야 한다.
후보는 global transport를 넘는 stronger head-suitability teacher,
sleep-pressure와 routine-break를 결합한 future-responsibility pretext,
cross-subject sleep-pressure prototype, listener-router를 action-health로 직접 연결하는 learned release gate,
그리고 hidden state를 action-health로 번역하는
open-loop world model이다.
