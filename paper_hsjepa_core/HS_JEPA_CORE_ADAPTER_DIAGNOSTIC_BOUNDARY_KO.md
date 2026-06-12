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
- `Masked Context World Model`: HS-JEPA core evidence
- `Action Support World Model Core`: HS-JEPA core evidence
- `Subject-Contrastive Action-Support Core`: HS-JEPA core evidence
- `Tail-Safe Expected Utility Core`: core geometry를 Log Loss utility / tail risk로 번역하는 decoder-boundary evidence
- `Subject-Normalized Tail Field Core`: absolute utility 대신 subject-relative badness를 예측하는 core-decoder boundary evidence
- `Episode-Conditioned Relative Tail Core`: subject-relative badness를 episode/reset/transition context로 조건화한 core-decoder boundary evidence
- `Masked-View Consensus Tail Core`: 여러 context mask가 같은 hidden tail representation에 동의하는지 검사하는 LeJEPA-style core-decoder boundary evidence
- `Masked View Surprise Action Release`: core residual을 action release로 번역한 adapter/probe
- `Surprise Responsibility Toxicity Veto`: adapter와 diagnostic 사이의 action-health gate

따라서 논문에서는 이들을 같은 레벨로 소개하면 안 된다.

## JEPA 느낌이 흐려지는 지점

HS-JEPA 실험이 submission CSV, top-k release, kNN transport, veto rule로 표현되기 시작하면
겉으로는 JEPA가 아니라 대회용 post-processing처럼 보인다.

이 문제를 피하려면 모든 실험 문서를 다음 질문으로 먼저 분류해야 한다.

```text
Q1. 보이는 context로 보이지 않는 representation을 예측하는가?
    -> Core 또는 core probe

Q2. 이미 만들어진 representation을 row-target action으로 번역하는가?
    -> Adapter

Q3. 그 action/representation이 shortcut, collapse, subject-tail인지 검사하는가?
    -> Diagnostic
```

`Core`가 논문 contribution의 중심이고, `Adapter`와 `Diagnostic`은 그 core가 실제 대회 환경에서
어떻게 작동하고 어디서 실패하는지 보여주는 case study다.

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
- `MASKED_CONTEXT_WORLD_MODEL_CORE_KO.md`
- `ACTION_SUPPORT_WORLD_MODEL_CORE_KO.md`
- `ACTION_SUPPORT_VIEW_INVARIANCE_CORE_KO.md`
- `LISTENER_CONDITIONED_ACTION_SUPPORT_CORE_KO.md`
- `SUBJECT_CONTRASTIVE_ACTION_SUPPORT_CORE_KO.md`
- `TAIL_SAFE_EXPECTED_UTILITY_CORE_KO.md`
- `SUBJECT_NORMALIZED_TAIL_FIELD_CORE_KO.md`
- `EPISODE_CONDITIONED_RELATIVE_TAIL_CORE_KO.md`
- `MASKED_VIEW_CONSENSUS_TAIL_CORE_KO.md`
- `HS_JEPA_JEPA_CONTRACT_KO.md`

Core evidence ladder:

```text
1. masked context prediction
   visible lifelog views -> masked target-view representation

2. world-state residual / surprise
   predicted representation vs observed representation mismatch

3. action-support prediction
   world-state geometry -> raw action success/toxicity representation

4. listener-conditioned support
   world-state geometry + target listener -> route-specific action-health

5. subject-contrastive support
   same-subject/same-target action pair -> episode-level action-health ordering

6. tail-safe expected utility
   action-health geometry -> expected Log Loss gain / negative-tail risk

7. subject-normalized tail field
   absolute action utility -> human-specific relative badness / tail representation

8. episode-conditioned relative tail field
   visible episode context -> hidden episode-conditioned relative badness / tail representation

9. masked-view consensus tail field
   multiple masked context views -> same hidden tail representation -> disagreement-aware action safety
```

이 ladder가 HS-JEPA의 JEPA성을 만든다. 즉 HS-JEPA는 label probability를 바로 맞히는 classifier가 아니라,
보이는 인간 생활 context에서 보이지 않는 human-state/action-support representation을 예측하는 모델이다.

주의할 점은 6번, 7번, 8번, 9번이 pure core라기보다 core-decoder boundary라는 것이다. 여기서부터는 representation을 실제
row-target action으로 번역하는 문제가 들어오므로, 논문에서는 `HS-JEPA core가 action-health geometry를 제공하고,
tail-safe/subject-normalized/episode-conditioned/masked-view-consensus decoder가 이를 Log Loss action으로 해석한다`고 써야 한다.

현재 ladder에서 가장 강한 evidence는 `Masked-View Consensus Tail Core`다. 이유는 처음으로 nested subject-heldout
gain이 양수(`+0.578637`)가 되었기 때문이다. 다만 stable target이 `S2`, `S4`에 집중되어 있으므로,
논문 주장은 universal label predictor가 아니라 `masked-view invariant hidden tail representation for safer
row-target action decoding`으로 제한해야 한다.

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
- `MASKED_VIEW_SURPRISE_ACTION_RELEASE_KO.md`
- `FAILURE_BOUNDARY_LAW_DISTILLATION_KO.md`
- `EPISODE_ACTION_SPACE_RESTRICTION_DECODER_KO.md`
- `CROSS_SUBJECT_SURPRISE_RESPONSIBILITY_VETO_KO.md`
- `SUBJECT_RELATIVE_RESPONSIBILITY_ASSIGNMENT_KO.md`

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
- `SUBJECT_HELDOUT_ROUTE_RESPONSIBILITY_DIAGNOSTIC_KO.md`
- `SUBJECT_HELDOUT_ACTION_TOXICITY_FIELD_KO.md`

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

### Subject-Relative Responsibility Assignment

이 문서는 HS-JEPA core가 아니라 adapter/diagnostic hybrid다.

JEPA 느낌이 남아 있는 이유:

```text
predicted action-health representation
  -> subject-relative / pairwise responsibility field
  -> row-target assignment decision
```

JEPA 느낌이 약한 이유:

```text
새 hidden representation을 학습하는 실험이 아니라,
이미 읽은 action-health score를 어떤 좌표계에서 action으로 번역할지 검사한다.
```

논문에서의 올바른 표현:

```text
We treat subject-relative responsibility assignment as an action decoder
stress test, not as the HS-JEPA world model itself.
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

## 팀 공유용 표현 규칙

팀원에게 설명할 때는 다음 표현을 지킨다.

- `HS-JEPA core`라고 부를 수 있는 것:
  masked-context world model, action-support world model, listener-conditioned support core.
- `HS-JEPA adapter`라고 불러야 하는 것:
  transport, route decoder, sparse correction, assignment solver, submission generator.
- `LeJEPA-style diagnostic`이라고 불러야 하는 것:
  subject-LOO, heldout action toxicity, collapse/shortcut audit, negative active subject stress.

금지 표현:

```text
Cross-subject transport is HS-JEPA.
Subject-invariant controller is HS-JEPA.
This submission is HS-JEPA.
```

권장 표현:

```text
Cross-subject transport is an adapter that probes whether HS-JEPA
representations support transfer of hidden episode-action prototypes.

Subject-invariant controller is a LeJEPA-style diagnostic for the
action decoder built on top of HS-JEPA representations.

The submission is a competition adapter output, not the architecture itself.
```
