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
| external_action_replay_geometry | core_to_adapter_probe | row_auc_z_vs_permuted_train | 8.375849 | permuted_teacher | strong_positive_probe |
| subject_invariant_listener_manifold | core | hsjepa_listener_ap_lift_minus_action_only | 0.191742 | action_geometry_only | strong_positive |
| listener_responsibility_field | core | masked_pretext_ap_lift_minus_listener_only | 0.014785 | listener_only | positive_but_small |
| signed_direction_translation | adapter_boundary | gain_sum_repaired_vs_previous_decoder | 2.206488 | previous_responsibility_decoder | adapter_positive_core_boundary |
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

### 2. Subject-Invariant Listener Manifold

subject-invariant jury release target은 action geometry만으로도 어느 정도 분리될 수 있지만,
HS-JEPA listener manifold는 action-only 대비 AP lift가 `0.191742` 더 크다.

이 결과는 HS-JEPA core가 단순 action magnitude가 아니라,
row-target listener가 어떤 hidden state에서 반응해야 하는지를 더 잘 표현한다는 증거다.

### 3. Listener Responsibility Field

action을 바로 고르지 않고 먼저 `어느 row-target listener가 책임을 가져야 하는가`를 예측하면,
masked-pretext responsibility가 listener-only보다 AP lift `0.014785`만큼 앞선다.

이 증거는 크지는 않지만 논문적으로 중요하다.
HS-JEPA contribution을 `확률값 보정`이 아니라 `listener responsibility representation`으로 둘 수 있기 때문이다.

## 무엇을 과장하면 안 되는가

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
| subject_invariant_listener_manifold | submission_hsjepa_subject_invariant_listener_manifold_anchor_free_40628330_uploadsafe.csv | core |
| listener_responsibility_field | submission_hsjepa_subject_invariant_listener_responsibility_field_a9a2ea47_uploadsafe.csv | core |
| signed_direction_translation | submission_hsjepa_signed_listener_responsibility_direction_3a0fba1d_uploadsafe.csv | adapter_boundary |

## Paper Thesis로 쓰기 좋은 문장

> HS-JEPA는 생활 로그를 직접 label로 매핑하지 않는다. 대신 보이는 인간 생활 context에서
> 보이지 않는 human-state와 listener-responsibility representation을 예측하고,
> 이 representation이 row-target action-health를 더 잘 분리하도록 만든다.
> 대회 adapter는 이 core geometry를 sparse correction으로 번역하는 별도 층이다.

## 다음 Big Bet

현재 가장 중요한 미해결 문제는 direction이다.

```text
responsibility field: positive
direction/action translation: adapter 의존
direct label prediction: negative
```

따라서 다음 실험은 action probability를 더 쓰는 것이 아니라,
`counterfactual raw/inverse direction representation` 자체를 HS-JEPA pretext target으로 끌어올려야 한다.
그래야 core가 "어디를 볼지"뿐 아니라 "어느 방향이 건강한지"까지 representation 안에서 표현하는지 검증할 수 있다.
