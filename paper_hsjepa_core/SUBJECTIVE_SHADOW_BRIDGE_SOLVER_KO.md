# Subjective Shadow Bridge Solver HS-JEPA

## 실험 목적

`Objective-Stage Bridge Conservation Solver`는 S1/S2/S3/S4 objective-stage
target에서 강한 구조를 보여줬다.

특히 S-stage action은 단일 cell로 움직일 때보다,

```text
public-sensitive driver action
+ route-preserving bridge action
```

으로 움직일 때 route energy가 크게 낮아졌다.

이번 실험은 이 구조를 Q target까지 확장할 수 있는지 물었다.

> objective sleep-stage bridge가 row의 수면 상태를 바꾼다면,
> Q1 주관적 수면 만족도도 그 변화의 그림자처럼 같이 움직여야 하는가?

이 질문은 논문적으로 중요하다.

HS-JEPA가 단순히 S-stage 내부 구조만 잡는 모델인지,
아니면 objective 수면 상태와 subjective 만족도 사이의 latent route까지 복원하는 모델인지
가르는 실험이기 때문이다.

## 핵심 한 줄

Q1 shadow를 붙이면 route energy는 더 낮아졌지만,
Q1-S target 상관 구조를 랜덤으로 섞은 null stress보다 강하지 않았다.

따라서 현재 증거로는:

```text
S-stage bridge는 action-grade 구조지만,
Q1 subjective shadow는 아직 action-grade 구조가 아니다.
```

## 코드

```bash
python3 paper_hsjepa_core/subjective_shadow_bridge_solver.py
```

## 산출물

제출 후보:

- `submission_hsjepa_subjective_shadow_bridge_q1shadow_guarded_7fab5753_uploadsafe.csv`
- `submission_hsjepa_subjective_shadow_bridge_q1shadow_jackpot_59852a64_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/subjective_shadow_bridge_solver/subjective_shadow_bridge_readout.json`
- `paper_hsjepa_core/outputs/subjective_shadow_bridge_solver/subjective_shadow_q1shadow_guarded_selected.csv`
- `paper_hsjepa_core/outputs/subjective_shadow_bridge_solver/subjective_shadow_q1shadow_jackpot_selected.csv`
- `paper_hsjepa_core/outputs/subjective_shadow_bridge_solver/subjective_shadow_q1shadow_guarded_candidates.csv`
- `paper_hsjepa_core/outputs/subjective_shadow_bridge_solver/subjective_shadow_q1shadow_jackpot_candidates.csv`

## 사용한 target geometry

Train target에서 Q1과 S-stage target의 상관은 다음과 같다.

| pair | corr |
|---|---:|
| Q1-S1 | 0.361 |
| Q1-S2 | 0.073 |
| Q1-S3 | -0.119 |
| Q1-S4 | 0.019 |

이를 정규화하면 Q1 shadow pressure는 다음처럼 계산된다.

| stage target | normalized weight |
|---|---:|
| S1 | 0.631559 |
| S2 | 0.127132 |
| S3 | -0.208141 |
| S4 | 0.033168 |

즉 S1이 증가하거나 S3이 감소하는 objective-stage 변화는 Q1 증가 pressure로 본다.
반대로 S1이 감소하거나 S3이 증가하면 Q1 감소 pressure로 본다.

중요한 점:

이 방향은 public LB에서 직접 가져온 것이 아니라 train label의 target geometry에서 가져왔다.
public-loss 계수는 이후 action toxicity/utility sensor로만 사용했다.

## 구조

먼저 stagebridge solver를 그대로 실행한다.

```text
current best
  -> S-stage driver action
  -> S-stage route-preserving bridge action
```

그 다음 각 selected row에 대해 Q1 shadow pressure를 계산한다.

```text
Q1 pressure =
  S1_step * corr(Q1,S1)
+ S2_step * corr(Q1,S2)
+ S3_step * corr(Q1,S3)
+ S4_step * corr(Q1,S4)
```

Q1 shadow action은 다음 조건을 통과해야 한다.

1. Q1 pressure가 충분히 큼
2. Q/S route energy를 크게 깨지 않음
3. public utility가 나쁘면 route energy gain이 충분해야 함
4. H088 bad action 방향과 강하게 겹치지 않음

## 결과 요약

### Q1 Shadow Guarded

제출 파일:

```text
submission_hsjepa_subjective_shadow_bridge_q1shadow_guarded_7fab5753_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| stage variant | stagebridge |
| stage cells | 60 |
| Q1 shadow candidates | 67 |
| selected Q1 shadow cells | 18 |
| total changed cells | 78 |
| mean route energy | 0.725130 |
| stage-only route energy | 0.725652 |
| current best route energy | 0.728381 |
| selected mean Q1 route delta | -0.007249 |
| selected negative-energy Q1 cells | 14 |
| H088 cosine | 0.001103 |
| upload-safe | true |

### Q1 Shadow Jackpot

제출 파일:

```text
submission_hsjepa_subjective_shadow_bridge_q1shadow_jackpot_59852a64_uploadsafe.csv
```

| 항목 | 값 |
|---|---:|
| stage variant | stagebridge_jackpot |
| stage cells | 82 |
| Q1 shadow candidates | 121 |
| selected Q1 shadow cells | 29 |
| total changed cells | 111 |
| mean route energy | 0.723289 |
| stage-only route energy | 0.724352 |
| current best route energy | 0.728381 |
| selected mean Q1 route delta | -0.009168 |
| selected negative-energy Q1 cells | 17 |
| H088 cosine | -0.012274 |
| upload-safe | true |

표면적으로는 Q1 shadow가 좋아 보인다.
둘 다 stage-only보다 route energy를 더 낮춘다.

하지만 이것만으로는 부족하다.
route energy 자체가 Q1을 움직이면 쉽게 낮아지는 구조일 수 있기 때문이다.

## Null Stress

Q1-S 상관 방향이 진짜인지 확인하기 위해 null stress를 넣었다.

방법:

- Q1-S target correlation magnitude는 유지
- 어떤 S target에 어떤 magnitude가 붙는지 랜덤 셔플
- sign도 랜덤으로 뒤집음
- 128회 반복
- 실제 Q1-S 구조가 null보다 top score와 energy gain에서 강한지 확인

### Guarded null stress

| 항목 | 값 |
|---|---:|
| actual top score sum | 0.068343 |
| null top score mean | 0.077008 |
| actual score z | -0.439 |
| p(null >= actual) | 0.656 |
| actual top energy gain | 0.103187 |
| null top energy gain mean | 0.106646 |
| energy gain z | -0.060 |
| p(null >= actual) | 0.406 |

### Jackpot null stress

| 항목 | 값 |
|---|---:|
| actual top score sum | 0.190927 |
| null top score mean | 0.227395 |
| actual score z | -0.909 |
| p(null >= actual) | 0.828 |
| actual top energy gain | 0.174206 |
| null top energy gain mean | 0.276899 |
| energy gain z | -0.711 |
| p(null >= actual) | 0.656 |

## 해석

이 실험은 처음에는 좋아 보였다.

Q1 shadow를 붙이면:

- route energy가 더 낮아지고,
- H088과도 크게 겹치지 않으며,
- upload-safe submission이 만들어진다.

하지만 null stress가 결정적이다.

실제 Q1-S correlation 방향이 랜덤 correlation보다 강하지 않았다.
특히 jackpot variant는 null이 실제보다 더 강했다.

따라서 현재 결론은:

```text
Q1 subjective satisfaction을 S-stage bridge의 직접 shadow로 번역하는 것은
아직 action-grade structure가 아니다.
```

## HS-JEPA 아키텍처에 주는 의미

이 결과는 실패지만 쓸모 있는 실패다.

HS-JEPA를 다음처럼 과장하면 안 된다.

```text
하나의 human-state latent가 Q와 S를 모두 자연스럽게 설명한다.
```

현재 증거는 더 좁고 더 정확하다.

```text
S-stage에는 objective conservation bridge가 있다.
Q1/Q3 subjective label은 그 bridge의 단순한 그림자가 아니다.
```

따라서 HS-JEPA decoder는 다음처럼 분리되어야 한다.

```text
Human-State Encoder
  -> Objective-Stage Driver/Bridge Decoder
  -> Subjective Decoder
  -> Public/Private Action Safety Head
```

Q와 S를 같은 decoder에서 억지로 묶으면 논문적으로는 그럴듯하지만,
실험적으로는 shortcut일 가능성이 높다.

## 제출 판단

두 CSV 모두 upload-safe지만, 현재는 public 제출 우선순위가 낮다.

이유:

- route energy는 좋아졌지만 null stress를 통과하지 못했다.
- Q1 shadow의 방향성이 target geometry 고유 구조라는 증거가 약하다.
- stagebridge_jackpot 자체가 더 깨끗한 big-bet이다.

현재 우선순위는 유지한다.

1. `submission_hsjepa_stage_bridge_conservation_stagebridge_jackpot_89d16116_uploadsafe.csv`
2. `submission_hsjepa_stage_bridge_conservation_stagebridge_2cf2f795_uploadsafe.csv`
3. `submission_hsjepa_energy_utility_solver_jackpot_5254f82c_uploadsafe.csv`

Q1 shadow 후보는 제출 후보가 아니라, Q/S decoder 분리의 부정 증거로 남긴다.
