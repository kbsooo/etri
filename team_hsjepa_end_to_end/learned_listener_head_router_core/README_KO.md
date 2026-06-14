# Learned Listener-Head Router Core

## 목적

이 패키지는 HS-JEPA의 listener-router를 사람이 고정한 semantic prior에서 한 단계 더 밀어낸다.

기존 실험은 `current / future / cohort` listener head를 그냥 concat하면 약하고,
target 의미에 따라 어떤 head를 읽을지 라우팅하면 좋아진다는 결과를 냈다.
하지만 그 router는 사람이 넣은 semantic prior에 의존했다.

이 실험은 다음 질문을 검증한다.

```text
visible human-life context와 predicted listener heads만으로
어떤 row-target이 current/future/cohort 중 어느 head를 들어야 하는지
label 없이 학습할 수 있는가?
```

## 구조

```text
OG train lifelog table
  -> subject-relative visible human-life context
  -> current / future / cohort listener-responsibility heads
  -> label-free hidden head-suitability teacher
  -> learned listener-head router
  -> routed HS-JEPA interface
  -> frozen downstream probe
```

## 실행

프로젝트 루트에서 실행한다.

```bash
python3 team_hsjepa_end_to_end/learned_listener_head_router_core/run_end_to_end.py
```

## 출력

```text
hsjepa_core/outputs/learned_listener_head_router_core/
```

주요 파일:

- `learned_listener_head_router_summary.json`
- `LEARNED_LISTENER_HEAD_ROUTER_CORE_KO.md`
- `learned_listener_head_router_probe_metrics.csv`
- `learned_listener_head_router_pretext_metrics.csv`
- `learned_listener_head_router_subject_leakage.csv`
- `learned_listener_head_router_weights.csv`

논문용 문서는 다음에도 복사된다.

```text
paper_hsjepa_core/LEARNED_LISTENER_HEAD_ROUTER_CORE_KO.md
```

## 현재 결론

현재 best learned router는 fixed semantic-prior router와 best single future head를 모두 이긴다.

```text
best learned router logloss: 0.677359
fixed semantic-prior router logloss: 0.677427
best single future head logloss: 0.677463
delta vs fixed semantic router: -0.000068
delta vs best single head: -0.000103
```

subject leakage도 낮아진다.

```text
best learned router leakage: 0.446667
fixed semantic-prior router leakage: 0.462222
best single future head leakage: 0.475556
raw lifelog PCA leakage: 0.940000
```

## 논문적으로 쓰기 좋은 문장

HS-JEPA는 단순히 여러 hidden-state head를 concat하지 않는다.
각 downstream listener가 current, future, cohort head 중 무엇을 들어야 하는지를
label-free hidden suitability pretext로 학습한다.

이 결과는 human-state representation이 고정된 feature bundle이 아니라,
listener-specific routing interface여야 한다는 점을 보여준다.

## 과장하면 안 되는 점

이 실험은 아직 subject-heldout global transported prototype grammar를 넘지는 못한다.
따라서 “완성된 decoder”가 아니라
`learned listener routing core evidence with global-transport boundary`로 해석해야 한다.
