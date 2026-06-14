# Human-State Drift Line Explorer

## 핵심 질문

`certified_replay`가 public LB `0.5619100863`을 기록했으므로, 이제 direction은 강하게 살아 있다.
다음 질문은 magnitude다.

```text
Q2/Q3 subject drift line은 아직 더 밀 수 있는가?
아니면 confirmed replay 지점이 이미 포화점인가?
```

## 후보

| variant | worldview | Q2 step | Q3 step | changed cells | upload safe |
| --- | --- | ---: | ---: | ---: | --- |
| q2_dominant_forward_axis | The confirmed drift direction is right, and Q2 is the real intervention/degradation axis.  Push Q2 beyond the certified replay while keeping Q3 at the confirmed companion strength. | 0.9000 | 0.2500 | 404 | True |
| joint_forward_axis | The whole Q2/Q3 drift line is under-powered.  Move both Q2 and Q3 forward along the same hidden state axis. | 0.8625 | 0.2875 | 404 | True |
| q2_forward_q3_pullback_axis | Q2 carries the true human-state drift, but Q3 is a noisy companion. Push Q2 while pulling Q3 slightly back from the confirmed replay. | 0.9000 | 0.1800 | 404 | True |
| silent_subject_reentry_axis | id05 was silent in the aggregate listener field, but train history shows the strongest Q2 downward drift.  Keep the confirmed axis and test whether this silent subject should re-enter Q2. | 0.7500 | 0.2500 | 425 | True |

## 제출 우선순위

가장 정보량이 큰 후보는 `q2_dominant_forward_axis`다.

좋아지면:

- Q2 intervention/degradation route가 아직 under-powered였다는 뜻이다.
- HS-JEPA 논문에는 `drift line control axis`와 `route-specific magnitude decoder`를 추가할 수 있다.

나빠지면:

- `0.75` Q2 logit step 부근이 이미 public aggregate optimum에 가깝다는 뜻이다.
- 다음 breakthrough는 같은 line overshoot가 아니라 S-target hidden route 또는 private-state factorization이어야 한다.

## 산출물

- readout: `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/human_state_drift_line_explorer/human_state_drift_line_readout.json`
- output_dir: `/Users/kbsoo/Downloads/cl2/sleep_competition_adapter/outputs/human_state_drift_line_explorer`