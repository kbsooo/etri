# HS-JEPA Core-First Thesis

## 한 줄 요약

HS-JEPA는 대회용 row-target correction 묶음이 아니라, 인간 생활 로그에서
보이는 context로 보이지 않는 human-state representation을 먼저 예측하고,
그 representation이 어떤 listener/action으로 안전하게 번역될 수 있는지 검사하는
core-first 아키텍처다.

```text
visible human context
  -> predict hidden human-state target representation
  -> test listener/action responsibility
  -> decode only invariant-preserving healthy actions
```

따라서 HS-JEPA의 본체는 제출 파일이 아니다.
본체는 `hsjepa_core/`에 있는 competition-agnostic mechanism이고,
`sleep_competition_adapter/`는 그 core를 수면 대회 row-target 형식으로 번역하는 case study다.

## 왜 JEPA인가

일반적인 JEPA 질문은 다음이다.

```text
보이는 일부 context만 보고, 보이지 않는 target representation을 예측할 수 있는가?
```

HS-JEPA는 이 질문을 인간 이해 문제로 바꾼다.

```text
관측 가능한 생활 로그 일부만 보고,
보이지 않는 인간 상태, listener route, action-support representation을 예측할 수 있는가?
```

여기서 target representation은 raw label이나 raw feature 복원이 아니다.

- masked lifelog-view latent
- row episode state
- listener responsibility state
- action-support geometry
- action toxicity / health field
- invariant-preserving correction field

이 중 어떤 representation이 실제로 유효한지는 adapter와 diagnostic으로 검증한다.

## Core와 Adapter를 반드시 분리해야 하는 이유

HS-JEPA를 처음 보는 팀원이 `Cross-Subject Episode Prototype Transport`나
`Subject-Invariant Episode Controller`부터 읽으면, HS-JEPA가 kNN transport나
row-target veto trick처럼 보일 수 있다.

정확한 층은 다음과 같다.

| Layer | 질문 | 산출물 | 일반성 |
| --- | --- | --- | --- |
| Core | 보이는 인간 context로 숨은 state representation을 예측하는가? | hidden state, prediction energy, listener responsibility, invariant energy | 대회 밖에도 재사용 가능 |
| Probe | core representation이 label/row/action 구조와 연결되는가? | masked-view prediction, nearest-neighbor consistency, action-health audit | 도메인 검증 |
| Adapter | core/probe 신호를 현재 대회 output으로 어떻게 번역하는가? | sparse row-target correction, submission CSV | 대회 특화 |
| Diagnostic | action이 shortcut/collapse/public luck인지 어떻게 거르는가? | subject-LOO, action-health, route guard, toxicity veto | 일반 검증 원리 |

논문 contribution은 core와 diagnostic 원리에 있어야 한다.
adapter는 "수면 기반 생활습관 로그 대회에서 이 architecture가 어떻게 작동했는가"를 보여주는 실험장이다.

## 현재 구현의 정확한 위치

### `hsjepa_core/core.py`

가장 일반적인 reference implementation이다.

```text
ContextView
  -> HiddenStatePrediction
  -> ListenerPrototype responsibility
  -> CandidateAction health score
  -> invariant-preserving release decision
```

이 파일은 target 이름, public LB, submission schema를 모른다.
따라서 HS-JEPA를 architecture로 설명할 때 가장 먼저 보여줘야 하는 코드는 이 파일이다.

### `hsjepa_core/run_masked_context_world_model.py`

가장 직접적인 JEPA-style real-data core probe다.

```text
visible lifelog views
  -> predict masked target-view PCA representation
  -> residual surprise energy
  -> hidden human-state episode / action-health diagnostic
```

현재 evidence:

- `app_social_context` masked-view representation은 null 대비 component-correlation lift `+0.248882`.
- predicted/full world state의 nearest-neighbor target match lift는 약 `+0.031`.
- direct label probe는 prior보다 나쁘다.
- S3/S4 action-health diagnostic에서는 residual energy가 toxic pocket을 분리했다.

해석:

```text
HS-JEPA core는 label classifier가 아니다.
하지만 hidden human-state geometry와 residual energy는 action-health를 설명한다.
```

### `Cross-Subject Episode Prototype Transport`

이 문서는 core가 아니라 adapter/probe다.

JEPA적인 점:

```text
current row-target context
  -> predict/retrieve peer subject's hidden episode-action target representation
```

대회 특화인 점:

```text
retrieved action representation
  -> sparse row-target correction
  -> upload-safe submission
```

따라서 논문 표현은 다음이 안전하다.

```text
We use cross-subject prototype transport as a non-parametric readout to test
whether HS-JEPA representations support hidden action-representation transfer.
```

### `Subject-Invariant Episode Controller`

이 문서는 core도 positive adapter도 아니다.
LeJEPA-style diagnostic이다.

역할:

```text
full OOF에서 좋아 보이는 action controller가
subject shift에서도 살아남는지 검사한다.
```

결론:

```text
좋아 보이는 episode action controller도 subject-heldout에서는 inactive/safe 쪽으로 수렴한다.
따라서 HS-JEPA decoder에는 anti-shortcut diagnostic이 필수다.
```

## 지금까지의 핵심 암묵지를 논문 언어로 바꾸면

대회 실험을 많이 해본 뒤 남은 핵심은 다음이다.

1. 인간 생활 로그에는 row-level hidden episode가 있다.
2. 그 episode는 label을 직접 맞히기보다 action-support와 action-toxicity를 더 잘 설명한다.
3. 같은 hidden state라도 Q/S listener가 다르게 반응하므로 flat multi-label classifier는 구조를 잃는다.
4. 좋아 보이는 action은 subject-tail 또는 public-like shortcut일 수 있으므로 LeJEPA-style health check가 필요하다.
5. 안전한 decoder는 하나의 global rule이 아니라 listener/target-route responsibility를 가져야 한다.

이것이 HS-JEPA의 architecture thesis다.

```text
HS-JEPA learns a hidden human-state representation by predicting masked or
unobserved state representations from visible lifelog context. It then treats
labels, sensors, and target routes as listeners over that state, releasing only
actions that remain healthy under listener responsibility and invariant-energy
diagnostics.
```

## 무엇을 HS-JEPA라고 부르면 안 되는가

다음은 HS-JEPA 자체가 아니다.

- 특정 public LB 점수
- 특정 submission 파일
- 특정 target 이름의 hand-tuned correction
- kNN transport 자체
- top-k, alpha, damp, veto threshold
- public score ledger 기반 inversion

이들은 adapter 또는 실험 도구일 수는 있지만, core contribution은 아니다.

## 팀원에게 보여줄 최소 읽는 순서

1. `hsjepa_core/README.md`
2. `hsjepa_core/core.py`
3. `paper_hsjepa_core/HS_JEPA_CORE_FIRST_THESIS_KO.md`
4. `paper_hsjepa_core/MASKED_CONTEXT_WORLD_MODEL_CORE_KO.md`
5. `paper_hsjepa_core/HS_JEPA_CORE_ADAPTER_DIAGNOSTIC_BOUNDARY_KO.md`
6. 이후 adapter evidence:
   - `paper_hsjepa_core/CROSS_SUBJECT_EPISODE_PROTOTYPE_TRANSPORT_KO.md`
   - `paper_hsjepa_core/TARGET_ROUTE_GUARDED_ACTION_EPISODE_TRANSPORT_KO.md`
   - `paper_hsjepa_core/SUBJECT_INVARIANT_EPISODE_CONTROLLER_KO.md`

이 순서로 읽어야 HS-JEPA가 대회용 후처리가 아니라,
인간 생활 상태 representation architecture라는 점이 유지된다.
