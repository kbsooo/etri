# Target-Route Toxicity Head HS-JEPA

## 실험 목적

직전 `Public/Private Toxicity Head`는 의미 있는 big-bet이었지만, extra cell을 56개나 추가했다.

그 결과 구조적으로는 흥미롭지만 제출 리스크가 크다.

이번 실험은 더 명확한 가설을 건다.

> toxicity tolerance는 target마다 다르다. Q2 route는 source/listener responsibility가 강하므로 제한적으로 확장할 수 있고, S1/S3/S4 같은 objective tail은 public-bad anchor에 민감하므로 teacher action만 보수적으로 calibration해야 한다.

## 핵심 한 줄

Target-route별 decoder를 도입해, Candidate 1 teacher 94개만 조정한 `teacher_only` 후보와 Q2만 14개 확장한 `q2_extra` 후보를 만들었다.

## 코드

```bash
python3 paper_hsjepa_core/target_route_toxicity_head.py
```

## 산출물

제출 후보:

- `submission_hsjepa_target_route_toxicity_teacher_only_66f1f5b4_uploadsafe.csv`
- `submission_hsjepa_target_route_toxicity_q2_extra_90b62d2d_uploadsafe.csv`

세부 산출물:

- `paper_hsjepa_core/outputs/target_route_toxicity_head/target_route_toxicity_readout.json`
- `paper_hsjepa_core/outputs/target_route_toxicity_head/target_route_toxicity_teacher_only_audit.csv`
- `paper_hsjepa_core/outputs/target_route_toxicity_head/target_route_toxicity_q2_extra_audit.csv`

## Variant 1: teacher_only

Candidate 1이 고른 94개 cell만 유지한다.

다만 target-route별 toxicity에 따라 amp를 다르게 준다.

- Q2: 더 공격적인 amp 허용
- S1/S3/S4: amp cap을 낮춤
- S2: 중간
- Q1/Q3: 일반 calibration

결과:

| 항목 | 값 |
|---|---:|
| teacher cells | 94 |
| Q2 extra cells | 0 |
| changed cells | 94 |
| changed rows | 82 |
| teacher mean amp | 1.122797 |
| teacher min amp | 0.880566 |
| teacher max amp | 1.280000 |
| upload-safe | true |

Listener diagnostic:

| Metric | Value |
|---|---:|
| base listener mean delta | -0.009594 |
| semantic listener mean delta | -0.010819 |
| hard-world cosine | 0.008965 |

해석:

이 후보는 Candidate 1의 support를 유지하므로 구조적으로 가장 안전한 ablation이다. public LB가 좋아지면 “support는 맞고 target-route별 amplitude가 병목이었다”는 뜻이다.

## Variant 2: q2_extra

teacher_only에 Q2 extra cell만 14개 추가한다.

Q2 extra 조건:

- Listener Responsibility selection score 높음
- toxic_same_rank 낮음
- h088_safe_rank 충분히 높음
- target이 Q2

결과:

| 항목 | 값 |
|---|---:|
| teacher cells | 94 |
| Q2 extra cells | 14 |
| changed cells | 108 |
| changed rows | 90 |
| teacher mean amp | 1.122797 |
| upload-safe | true |

Listener diagnostic:

| Metric | Value |
|---|---:|
| base listener mean delta | -0.012516 |
| semantic listener mean delta | -0.012895 |
| hard-world cosine | 0.011160 |

Q2 extra rows:

- 78, 164, 151, 221, 8, 244, 144, 185, 169, 121, 187, 225, 84, 247

해석:

이 후보는 Q2 route 가설에 베팅한다. 직전 Listener Responsibility 실험에서 Q2는 selected 31개 중 19개가 teacher와 겹쳤고 sign도 모두 맞았다. 따라서 Q2 extra는 다른 target extra보다 근거가 강하다.

## 제출 판단

1. `teacher_only`
   - 가장 안전한 toxicity-calibrated ablation
   - Candidate 1과 같은 94개 cell만 움직임
   - 제출 결과가 좋으면 amplitude calibration이 병목이었다는 뜻

2. `q2_extra`
   - 더 큰 정보량을 가진 target-route big-bet
   - Q2만 확장하므로 150-cell high-risk 후보보다 훨씬 통제됨
   - 좋아지면 Q2 listener route가 public/private 모두에서 살아 있다는 뜻
   - 나빠지면 Q2 extra도 아직 assignment toxicity를 못 피했다는 뜻

## 논문형 의미

이 실험은 HS-JEPA decoder가 target-agnostic이면 안 된다는 증거를 남긴다.

정리하면:

```text
Human-State Encoder
    -> state context

Listener Responsibility JEPA
    -> row-target support 후보

Target-Route Toxicity Head
    -> target별 action tolerance를 반영한 decoder
```

즉 HS-JEPA는 하나의 통합 classifier가 아니라, support, route, toxicity를 분리한 joint embedding/action system으로 설명하는 것이 더 정확하다.
