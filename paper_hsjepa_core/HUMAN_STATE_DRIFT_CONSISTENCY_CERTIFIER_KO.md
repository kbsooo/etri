# Human-State Drift Consistency Certifier

## 한 줄 요약

HS-JEPA가 찾은 hidden human-state를 subject별 회복/악화 drift로 해석하고, 그 drift가 train history와 aggregate listener observation에서 동시에 들릴 때만 Q2/Q3 action으로 번역한다.

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

- control: `/Users/kbsoo/Downloads/cl2/submission_hsjepa_human_state_drift_consistency_certified_replay_76bb1a88_uploadsafe.csv`
- primary: `/Users/kbsoo/Downloads/cl2/submission_hsjepa_human_state_drift_consistency_drift_consistency_overshoot_0fb93301_uploadsafe.csv`

## 결과를 어떻게 읽을 것인가

primary 후보가 0.564749보다 좋아지면, subject-level human-state drift가 단순 public equation의 방향뿐 아니라 action magnitude까지 설명한다는 강한 증거가 된다.

나빠지면, 지금 aggregate listener는 방향은 알려주지만 magnitude는 이미 certified max-min 해법 근처에서 포화됐다는 뜻이다. 그 경우 다음 breakthrough는 overshoot가 아니라 S target 또는 private-state factorization을 새 target representation으로 잡아야 한다.
