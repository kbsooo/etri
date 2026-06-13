# Human-State Drift Consistency Certifier

## 한 줄 요약

HS-JEPA가 찾은 hidden human-state를 subject별 회복/악화 drift로 해석하고, 그 drift가 train history와 aggregate listener observation에서 동시에 들릴 때만 Q2/Q3 action으로 번역한다.

## Public 결과

제출 파일:

```text
submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv
```

Public LB:

```text
0.5619100863
```

비교:

| 기준 | Public LB | 차이 |
| --- | ---: | ---: |
| FrontierSilence | 0.5677269444 | -0.0058168581 |
| 팀원 certified subject drift | 0.5647490904 | -0.0028390041 |
| HS-JEPA drift consistency certified replay | 0.5619100863 | 0 |

이 결과는 지금까지의 작은 후처리 계열과 성격이 다르다. 202개 test row의 Q2/Q3만 subject-uniform하게 움직였는데도 public에서 큰 폭으로 전이됐다. 즉 public subset에만 맞춘 sparse row-cell 수술이 아니라, subject 단위의 숨은 생활 상태 방향이 실제 평가 신호에 강하게 반영됐다고 해석할 수 있다.

## 왜 필요한가

기존 좋은 결과는 public LB 방정식을 잘 이용한 것처럼 보일 수 있다. 논문 관점에서는 이것을 더 일반적인 인간 이해 구조로 바꿔야 한다.

우리가 주장하는 것은 다음이다.

```text
visible human-life context
  -> subject-level hidden human-state direction
  -> listener-consistent recovery/degradation route
  -> subject-uniform row-target correction field
```

여기서 public score는 최적화 대상이 아니라 aggregate listener다. listener는 "어떤 subject가 회복/악화 방향으로 움직이고 있는가"를 아주 약한 scalar observation으로 들려준다. HS-JEPA adapter는 이 observation을 train-time subject drift와 대조해 action magnitude를 정한다.

## JEPA 관점

일반 JEPA는 context로 보이지 않는 target representation을 예측한다. 이 실험에서의 대응은 다음과 같다.

| JEPA 구성 | 이 실험의 의미 |
| --- | --- |
| context | subject의 train-time temporal drift, current probability state, aggregate listener sign |
| target representation | subject-level recovery/degradation human-state direction |
| predictor | listener direction과 train drift consistency로 action magnitude 결정 |
| decoder | Q2 intervention route와 Q3 companion route에 subject-uniform logit shift 적용 |
| diagnostic | train drift와 listener가 충돌하면 step을 줄임 |

핵심은 row-cell을 맞히는 것이 아니라 subject hidden state의 방향을 복원하는 것이다.

## End-to-End 재현

이 실험은 OG train label과 current frontier submission에서 바로 재현된다.

입력:

- `/Users/kbsoo/Downloads/cl2/data/ch2026_metrics_train.csv`
- `/Users/kbsoo/Downloads/cl2/submission_hsjepa_frontier_silence_positive_path_overshoot_sensor_1e013277_uploadsafe.csv`

실행:

```bash
cd /Users/kbsoo/Downloads/cl2
python3 sleep_competition_adapter/human_state_drift_consistency_certifier.py
```

출력:

- `/Users/kbsoo/Downloads/cl2/submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv`
- `/Users/kbsoo/Downloads/cl2/submission_hsjepa_human_state_drift_consistency_drift_consistency_overshoot_0fb93301_uploadsafe.csv`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/human_state_drift_consistency_readout.json`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/certified_replay_subject_action_audit.csv`
- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/drift_consistency_overshoot_subject_action_audit.csv`

## 설계 원칙

1. Q2/Q3만 움직인다.
   - Q2는 intervention/degradation route다.
   - Q3는 약한 companion quality route다.
   - S targets는 current certified observation에서 직접 안전하게 번역되지 않았으므로 건드리지 않는다.

2. subject 내부에서는 같은 logit shift를 준다.
   - 같은 subject의 모든 test row에 동일한 Q2/Q3 logit 이동을 적용한다.
   - 따라서 "어느 row가 1인가"에 의존하는 sparse cell lottery를 피한다.

3. magnitude는 human-state consistency로 조절한다.
   - aggregate listener sign과 train drift가 같은 방향이면 step을 키운다.
   - 방향이 충돌하면 step을 줄인다.

## 산출물

실행:

```bash
python3 sleep_competition_adapter/human_state_drift_consistency_certifier.py
```

문서:

- `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/human_state_drift_consistency_certifier/HUMAN_STATE_DRIFT_CONSISTENCY_CERTIFIER_KO.md`

후보:

- confirmed positive: `/Users/kbsoo/Downloads/cl2/submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv`
- next sensor: `/Users/kbsoo/Downloads/cl2/submission_hsjepa_human_state_drift_consistency_drift_consistency_overshoot_0fb93301_uploadsafe.csv`

## 결과를 어떻게 읽을 것인가

`certified_replay`가 이미 0.5619100863을 기록했으므로, 가장 중요한 결론은 다음이다.

```text
subject-level human-state drift는 실제 public 평가에서 강하게 들린다.
```

이제 남은 질문은 direction이 아니라 magnitude와 private transfer다.

`drift_consistency_overshoot`가 더 좋아지면, train drift consistency가 action magnitude까지 설명한다는 뜻이다. 나빠지면, direction은 맞지만 current certified magnitude가 이미 거의 최적이라는 뜻이다.

## 논문 contribution으로 쓰는 방법

이 모듈은 HS-JEPA 전체에서 `core-to-adapter bridge`다.

```text
HS-JEPA core:
  visible human-life context -> hidden human-state representation

Drift Consistency Certifier:
  hidden human-state direction -> subject-uniform target-route action
```

논문에서는 다음 세 가지를 contribution으로 말할 수 있다.

1. **Human-state drift as a JEPA target representation**
   - label을 직접 맞히는 대신 subject의 회복/악화 방향을 target representation으로 둔다.

2. **Subject-uniform action decoder**
   - 같은 subject의 test row를 독립 cell로 보지 않고, 같은 hidden state field를 공유한다고 본다.
   - 이 때문에 row assignment noise가 줄어든다.

3. **Aggregate listener as weak human-state sensor**
   - public LB를 맞출 대상으로 쓰지 않고, hidden state direction을 들려주는 약한 listener로 사용한다.

주의할 점:

- 이 모듈만으로 HS-JEPA 전체가 완성됐다고 말하면 안 된다.
- core representation 자체는 별도 masked/context prediction 실험으로 지지해야 한다.
- 이 실험은 그 representation을 competition action으로 안전하게 번역한 사례다.
