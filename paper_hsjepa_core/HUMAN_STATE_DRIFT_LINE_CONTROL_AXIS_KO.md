# Human-State Drift Line Control Axis

## 한 줄 요약

`certified_replay`가 public LB `0.5619100863`을 기록하면서 subject-level drift direction은 강하게 살아났다. 이제 HS-JEPA의 다음 질문은 방향이 아니라 `magnitude decoder`다.

```text
보이는 context로 subject hidden drift direction을 찾았다면,
그 direction을 얼마나 세게 Q2/Q3 route에 번역해야 하는가?
```

## 왜 필요한가

`Human-State Drift Consistency Certifier`는 Q2/Q3에 subject-uniform logit shift를 적용해 큰 개선을 만들었다.

```text
FrontierSilence: 0.5677269444
certified_replay: 0.5619100863
delta: -0.0058168581
```

이 결과는 direction이 맞다는 증거다. 하지만 논문적으로 더 중요한 질문은 남아 있다.

```text
HS-JEPA가 hidden human-state direction만 찾는가?
아니면 그 direction을 route별 magnitude까지 조절할 수 있는가?
```

이 문서는 그 다음 모듈을 `Drift Line Control Axis`로 정의한다.

## JEPA 관점

| JEPA 구성 | Drift Line Control에서의 의미 |
| --- | --- |
| context | confirmed subject drift field, train drift, Q2/Q3 route semantics |
| target representation | one-dimensional subject-level recovery/degradation axis |
| predictor | route별 magnitude 선택 |
| decoder | Q2/Q3 subject-uniform logit step |
| diagnostic | overshoot가 좋아지는지, Q3 pullback이 좋아지는지, silent subject가 살아나는지 |

## 생성된 후보

실행:

```bash
cd /Users/kbsoo/Downloads/cl2
python3 sleep_competition_adapter/human_state_drift_line_explorer.py
```

후보:

| 후보 | 의미 |
| --- | --- |
| `q2_dominant_forward_axis` | Q2 route가 아직 under-powered인지 확인한다. |
| `joint_forward_axis` | Q2/Q3 전체 drift line이 아직 약한지 확인한다. |
| `q2_forward_q3_pullback_axis` | Q2는 강하게, Q3는 줄이는 것이 맞는지 확인한다. |
| `silent_subject_reentry_axis` | aggregate listener가 놓친 id05 Q2 downward drift가 살아 있는지 확인한다. |

가장 정보량이 큰 다음 제출 후보:

```text
submission_hsjepa_human_state_drift_line_q2_dominant_forward_axis_03b49564_uploadsafe.csv
```

## 결과를 어떻게 읽을 것인가

`q2_dominant_forward_axis`가 `0.5619100863`보다 좋아지면:

- Q2 intervention/degradation route가 아직 under-powered였다.
- HS-JEPA는 hidden state direction뿐 아니라 route-specific magnitude decoder도 가져야 한다.

나빠지면:

- Q2 logit step `0.75` 부근이 public aggregate optimum에 가깝다.
- 다음 breakthrough는 같은 drift line overshoot가 아니라 S-target route, private-state factorization, 또는 label-free listener route selection이어야 한다.

## 논문 contribution으로 정리

이 모듈은 HS-JEPA를 다음처럼 확장한다.

```text
1. Context-to-state:
   visible human context -> subject-level hidden drift direction

2. State-to-route:
   hidden drift direction -> Q2/Q3 route-specific action

3. Route magnitude control:
   route-specific action -> calibrated subject-uniform logit step
```

즉 HS-JEPA는 단순히 hidden state를 찾는 모델이 아니라, hidden state를 route별로 읽고 action magnitude까지 조절하는 architecture로 정립된다.
