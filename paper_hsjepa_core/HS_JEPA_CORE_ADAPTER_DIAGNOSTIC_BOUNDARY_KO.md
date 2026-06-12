# HS-JEPA Core / Adapter / Diagnostic Boundary

## 한 줄 요약

HS-JEPA는 하나의 제출 파일 이름이 아니라 세 층으로 나뉘는 아키텍처다.

```text
Core       = 보이는 생활 context로 보이지 않는 human-state representation을 예측한다.
Adapter    = 그 representation을 row-target correction/action으로 번역한다.
Diagnostic = 그 action이 shortcut, collapse, subject-tail, public-luck인지 검사한다.
```

이 구분을 하지 않으면 HS-JEPA가 대회용 후처리처럼 보인다.

## 왜 이 문서가 필요한가

최근 실험 중 `Cross-Subject Episode Prototype Transport`와 `Subject-Invariant Episode Controller`는 모두 HS-JEPA 세계 안에 있지만, 둘 다 core 자체는 아니다.

- `Cross-Subject Episode Prototype Transport`: HS-JEPA adapter
- `Subject-Invariant Episode Controller`: LeJEPA-style diagnostic
- `Masked View Surprise Action Release`: core에 가장 가까운 masked context prediction probe
- `Surprise Responsibility Toxicity Veto`: adapter와 diagnostic 사이의 action-health gate

따라서 논문에서는 이들을 같은 레벨로 소개하면 안 된다.

## HS-JEPA Core

Core의 질문은 JEPA와 가장 직접적으로 맞닿아 있다.

```text
visible human-life context만 보고,
masked or hidden human-state target representation을 예측할 수 있는가?
```

Core가 다루는 것은 label probability가 아니다.

Core target representation 예시:

- masked feature-family latent
- row episode state
- target listener route state
- action support geometry
- masked-view residual energy
- human-state surprise field

Core의 좋은 증거:

- masked context prediction이 random/null보다 의미 있게 낫다.
- residual energy가 label shift, row-state frontier, action toxicity와 연결된다.
- public LB나 기존 submission teacher 없이도 row/action support 일부를 회수한다.

대표 문서:

- `LIFELOG_CORE_STATE_EVIDENCE_KO.md`
- `MASKED_VIEW_SURPRISE_ACTION_RELEASE_KO.md`
- `HS_JEPA_JEPA_CONTRACT_KO.md`

## HS-JEPA Adapter

Adapter는 core representation을 대회 task의 row-target correction으로 번역한다.

Adapter의 질문:

```text
예측된 human-state/action representation을 어떤 listener, target, row에 release할 것인가?
```

Adapter가 다루는 것은 competition-specific이다.

- Q1/Q2/Q3/S1/S2/S3/S4 listener schema
- row-target sparse submission format
- raw lifelog KNN fallback
- target route 선택
- public/private-safe correction field
- cross-subject prototype transport

대표 문서:

- `CROSS_SUBJECT_EPISODE_PROTOTYPE_TRANSPORT_KO.md`
- `FAILURE_BOUNDARY_LAW_DISTILLATION_KO.md`
- `EPISODE_ACTION_SPACE_RESTRICTION_DECODER_KO.md`
- `CROSS_SUBJECT_SURPRISE_RESPONSIBILITY_VETO_KO.md`

Adapter는 HS-JEPA의 일부지만, 논문 contribution을 adapter에만 두면 일반성이 약해진다.

## LeJEPA-style Diagnostic

Diagnostic은 representation/action이 진짜 구조인지 검사한다.

Diagnostic의 질문:

```text
이 representation이 subject shortcut, public overfit, collapsed action tail,
calibration luck이 아니라는 증거가 있는가?
```

Diagnostic 지표:

- subject-LOO
- active subject coverage
- negative active subject count
- heldout action gain
- surprise responsibility veto
- target-specific toxicity
- route consistency energy

대표 문서:

- `SUBJECT_INVARIANT_EPISODE_CONTROLLER_KO.md`
- `EPISODE_CONTROLLER_STRESS_AUDIT_KO.md`
- `SURPRISE_RESPONSIBILITY_TOXICITY_VETO_KO.md`
- `CROSS_SUBJECT_SURPRISE_RESPONSIBILITY_VETO_KO.md`

## 최근 두 문서의 정확한 위치

### Cross-Subject Episode Prototype Transport

이 문서는 HS-JEPA core가 아니라 adapter다.

JEPA 느낌이 남아 있는 이유:

```text
current row-target context
  -> predict/retrieve hidden episode-action representation from peer subjects
```

JEPA 느낌이 흐려지는 이유:

```text
최종 산출물이 kNN transport, topfrac release, submission candidate로 표현된다.
```

논문에서의 올바른 표현:

```text
We use a non-parametric adapter to test whether HS-JEPA representations support
cross-subject transport of hidden episode-action prototypes.
```

### Subject-Invariant Episode Controller

이 문서는 HS-JEPA core가 아니라 diagnostic이다.

JEPA 느낌이 약한 이유:

```text
새 representation을 예측하지 않고,
이미 만든 episode-action controller가 subject shift에서 살아남는지 검사한다.
```

논문에서의 올바른 표현:

```text
We use subject-invariant controller selection as a LeJEPA-style anti-collapse
diagnostic for the action decoder.
```

## 지금 논문에 써야 하는 구조

논문 본문은 다음 순서로 써야 한다.

1. HS-JEPA Core
   - human-state latent를 어떻게 정의하는가
   - masked context-to-target representation prediction을 어떻게 구성하는가

2. Adapter
   - core representation을 row-target action으로 어떻게 번역하는가
   - target listener route와 correction field를 어떻게 다루는가

3. Diagnostic
   - subject shift, collapse, shortcut, public-luck을 어떻게 검사하는가

4. Competition Case Study
   - 이 구조가 수면 기반 생활습관 로그 예측에서 어떤 OOF/LB evidence를 만들었는가

## 현재 가장 정확한 주장

강하게 말할 수 있는 것:

```text
HS-JEPA core는 직접 label classifier보다 hidden human-state/action-support
representation으로 더 잘 작동한다.
```

조건부로 말할 수 있는 것:

```text
이 representation은 adapter와 diagnostic을 거치면 row-target action toxicity를 줄이고,
cross-subject action prototype transport를 일부 가능하게 한다.
```

아직 말하면 안 되는 것:

```text
HS-JEPA core alone solves the competition.
```

현재 증거는 그 반대에 가깝다. Core alone은 충분하지 않고, adapter와 diagnostic이 필요하다.

