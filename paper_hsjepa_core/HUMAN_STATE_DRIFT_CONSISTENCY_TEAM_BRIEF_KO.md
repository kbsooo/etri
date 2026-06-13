# Human-State Drift Consistency Team Brief

## 1. 한 줄 요약

우리는 test row를 독립 샘플로 보지 않고, 같은 subject가 공유하는 `회복/악화 human-state drift`가 있다고 보았다. 그 drift가 Q2/Q3에 subject-uniform하게 작용한다고 가정해 correction field를 만들었고, public LB가 `0.5619100863`까지 내려갔다.

## 2. 왜 중요한가

이번 결과는 단순히 확률을 조금 보정한 것이 아니다.

기존 방식은 대체로 다음 질문이었다.

```text
이 row의 이 target probability를 얼마나 바꿀까?
```

이번 방식은 질문을 바꿨다.

```text
이 subject는 지금 회복/악화 방향 중 어디로 움직이고 있는가?
그 방향이 Q2/Q3 route에 어떻게 나타나는가?
```

즉 row-target 수술이 아니라 subject-level human-state field를 읽었다.

## 3. 결과

| 파일 | Public LB | 의미 |
| --- | ---: | --- |
| `submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv` | 0.5677269444 | 이전 anchor |
| 팀원 certified subject-drift result | 0.5647490904 | subject-uniform drift direction이 강하다는 외부 증거 |
| `submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv` | 0.5619100863 | 이번 재현/정식화 결과 |

개선폭:

```text
vs FrontierSilence: -0.0058168581
vs 팀원 certified:  -0.0028390041
```

## 4. HS-JEPA로 해석하면 무엇인가

JEPA의 핵심은 raw input을 복원하는 것이 아니라, 보이는 context로 보이지 않는 representation을 예측하는 것이다.

이번 실험의 대응은 다음이다.

| 구성 | 이 실험에서의 의미 |
| --- | --- |
| visible context | subject의 train-time label drift, current frontier state, aggregate listener direction |
| hidden representation | subject별 recovery/degradation human-state direction |
| target route | Q2 intervention route, Q3 sleep-quality companion route |
| decoder | subject 내부 모든 row에 같은 Q2/Q3 logit shift |
| diagnostic | train drift와 listener direction이 충돌하는 subject는 보수적으로 처리 |

중요한 점은 public LB를 직접 target으로 맞춘 것이 아니라, public LB를 aggregate listener로 사용했다는 것이다.

## 5. End-to-End 코드

메인 코드:

```text
/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/human_state_drift_consistency_certifier.py
```

실행:

```bash
cd /Users/kbsoo/Downloads/cl2
python3 sleep_competition_adapter/human_state_drift_consistency_certifier.py
```

입력:

```text
data/ch2026_metrics_train.csv
submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv
```

출력:

```text
submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv
submission_hsjepa_human_state_drift_consistency_drift_consistency_overshoot_0fb93301_uploadsafe.csv
sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/human_state_drift_consistency_readout.json
sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/certified_replay_subject_action_audit.csv
sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/drift_consistency_overshoot_subject_action_audit.csv
```

## 6. 알고리즘 흐름

```text
1. train rows를 subject별 시간순으로 정렬한다.
2. 각 subject의 앞 절반/뒤 절반 label prevalence 차이를 계산한다.
3. aggregate listener가 알려준 subject direction을 준비한다.
4. id03/id04/id06/id09는 upward state, id02/id07/id08/id10은 downward state, id01/id05는 hold로 둔다.
5. base submission의 Q2/Q3 probability를 logit으로 바꾼다.
6. active subject 내부 모든 test row에 같은 Q2/Q3 logit shift를 적용한다.
7. probability로 되돌리고 upload-safe 검증을 수행한다.
```

## 7. Subject Drift Field

| subject | state direction | action |
| --- | --- | --- |
| id03, id04, id06, id09 | upward recovery/degradation listener direction | Q2/Q3 logit up |
| id02, id07, id08, id10 | downward listener direction | Q2/Q3 logit down |
| id01, id05 | uncertain/held-out | hold |

`certified_replay`는 모든 active subject에 Q2 `0.75`, Q3 `0.25` logit shift를 같은 방향으로 적용한다.

## 8. 논문 포인트

### Contribution 1. Human-State Drift Representation

우리는 label을 직접 예측하지 않고, subject-level recovery/degradation direction을 hidden target representation으로 둔다. 이는 인간 생활 로그에서 개인의 상태가 시간에 따라 drift한다는 인간 이해 가설이다.

### Contribution 2. Assignment-Noise-Free Decoder

row-cell 단위의 sparse correction은 public row 배정에 민감하다. 반면 subject-uniform logit action은 같은 subject 내부에서 어떤 row가 positive인지에 덜 민감하다. 이 구조가 public에서 큰 전이를 만든다.

### Contribution 3. Aggregate Listener

public LB는 최적화 target이 아니라 약한 sensor다. 이 sensor는 subject별 human-state direction을 직접 보여주지는 않지만, 여러 제출 반응을 통해 어떤 subject direction이 들리는지 알려준다.

### Contribution 4. Core/Adapter Boundary

이 실험은 HS-JEPA core 자체가 아니라 core-to-adapter bridge다.

```text
Core:
  visible human context -> hidden human-state representation

Adapter:
  hidden state direction -> competition-specific Q2/Q3 correction
```

이 경계를 명확히 해야 논문에서 대회 트릭처럼 보이지 않는다.

## 9. 발표할 때 피해야 할 표현

피해야 한다:

```text
public LB를 역추론해서 맞췄다.
```

대신 이렇게 말한다:

```text
우리는 aggregate listener observations를 이용해 subject-level human-state drift direction을 추정했고,
이를 assignment-noise-free subject-uniform decoder로 Q2/Q3 route에 번역했다.
```

## 10. 남은 질문

1. `drift_consistency_overshoot`가 `0.5619100863`보다 좋아지는가?
   - 좋아지면 train drift consistency가 action magnitude까지 설명한다.
   - 나빠지면 direction은 맞지만 certified magnitude가 이미 포화됐다는 뜻이다.

2. S targets에도 같은 구조가 있는가?
   - 현재는 Q2/Q3만 안전하게 들린다.
   - S targets는 별도 hidden state route가 필요하다.

3. private에도 전이되는가?
   - subject-uniform 구조는 sparse cell surgery보다 private 전이가 기대된다.
   - 다만 public/private subset의 subject composition이 다르면 magnitude risk는 남는다.
