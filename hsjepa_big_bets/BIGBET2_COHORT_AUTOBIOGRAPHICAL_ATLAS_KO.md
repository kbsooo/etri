# Big Bet 2. Cohort-Autobiographical Atlas HS-JEPA

## 한 줄 요약

이 아이디어는 test row를 독립 샘플로 보지 않는다.

각 test day를 “같은 subject의 생활 궤적 안에 있는 숨은 하루 상태”로 보고, 그 하루가 자기 과거와 얼마나 비슷한지, 동시에 비슷한 사람들의 peer cohort 안에서 얼마나 튀는지를 함께 본다.

최종 후보:

`submission_bigbet2_cohort_autobiographical_atlas_2258cf87_uploadsafe.csv`

코드:

`hsjepa_big_bets/bigbet2_cohort_autobiographical_atlas.py`

## 왜 큰 실험인가

이 실험은 단순 cohort feature 추가가 아니다.

데이터 생성 세계관을 다음처럼 바꾼다.

일반적인 접근:

```text
오늘의 feature -> 오늘의 label
```

이 실험의 접근:

```text
오늘의 sensor context
-> 같은 사람의 과거 human-state 중 비슷한 날 검색
-> autobiographical memory posterior
-> peer cohort 기준으로 오늘이 튀는지 확인
-> row-target correction으로 번역
```

즉 하루를 두 좌표계에서 해석한다.

1. Personal coordinate: 이 사람의 과거 기준으로 오늘은 어떤 날인가?
2. Cohort coordinate: 비슷한 생활 패턴을 가진 사람들 기준으로 오늘은 어떤 날인가?

## HS-JEPA로 해석하면

### Context

- official train/sample row
- 같은 subject의 과거 label trajectory
- sensor-derived human-state latent
- calendar context
- raw sensor PCA state
- peer group outlier score
- subject normal distance
- peer normal distance
- peer target margin

### Target representation

직접 label을 예측하지 않는다.

먼저 숨은 human-state target representation을 만든다.

```text
이 subject가 과거에 오늘과 비슷한 상태였을 때
Q/S target은 어떤 posterior를 가졌는가?
```

이 posterior가 `autobiographical memory posterior`다.

### Predictor

target별로 다른 memory view를 쓴다.

| target | memory view |
|---|---|
| Q1 | latent + calendar |
| Q2 | latent + calendar |
| Q3 | latent + calendar |
| S1 | raw sensor PCA |
| S2 | raw sensor PCA + latent |
| S3 | latent + calendar |
| S4 | latent |

이건 “라벨별로 다른 모델을 쓴다”는 의미가 아니라, target마다 인간 상태를 보는 좌표계가 다르다는 가설이다.

Q2/Q3는 생활 리듬과 subjective state에 민감하고, S1/S2/S3는 sensor/body state에 더 민감하다고 본다.

### Decoder

memory posterior가 current best와 다른 방향을 말해도 바로 움직이지 않는다.

다음 조건을 만족하는 row-target만 움직인다.

- 같은 subject 과거 memory가 강하게 다른 posterior를 줌
- peer cohort 기준으로도 outlier 성격이 있음
- peer target margin과 memory 방향이 충돌하지 않음
- Q2/Q3/S1/S2/S3 중심으로 제한함
- Q1/S4는 이번 promoted 후보에서는 제외함

## 이번 실행 결과

결과 파일:

- `hsjepa_big_bets/outputs/bigbet2_cohort_autobiographical_atlas_cv.csv`
- `hsjepa_big_bets/outputs/bigbet2_cohort_autobiographical_atlas_results.csv`
- `hsjepa_big_bets/outputs/bigbet2_cohort_autobiographical_atlas_selected_cells.csv`
- `hsjepa_big_bets/outputs/bigbet2_cohort_autobiographical_test_memory_posterior.csv`
- `hsjepa_big_bets/outputs/bigbet2_cohort_autobiographical_atlas_decision.csv`

Promoted variant:

`cohort_memory_stage_heavy`

핵심 수치:

| 항목 | 값 |
|---|---:|
| selected cells | 430 |
| selected rows | 203 |
| move L1 | 155.508734 |
| move L2 | 9.108945 |
| cosine with H088 failure axis | -0.191307 |
| cosine with listener-tomography candidate | -0.044375 |
| cosine with robust listener candidate | -0.055615 |
| min prob / max prob | 0.000005 / 0.999997 |

Target mix:

| target | cells |
|---|---:|
| S2 | 95 |
| Q2 | 90 |
| Q3 | 85 |
| S1 | 85 |
| S3 | 75 |

## Local validation에서 얻은 신호

같은 subject의 단순 평균보다 autobiographical memory posterior가 target별로 얼마나 좋아지는지 봤다.

| target | subject mean logloss | memory logloss | gain |
|---|---:|---:|---:|
| Q1 | 0.658703 | 0.641172 | 0.017531 |
| Q2 | 0.663979 | 0.605724 | 0.058255 |
| Q3 | 0.660265 | 0.611985 | 0.048280 |
| S1 | 0.574629 | 0.562962 | 0.011667 |
| S2 | 0.575728 | 0.554420 | 0.021308 |
| S3 | 0.539529 | 0.526612 | 0.012917 |
| S4 | 0.641883 | 0.630688 | 0.011195 |

가장 중요한 발견은 Q2/Q3다.

Q2/Q3는 단순 subject mean으로는 약했지만, 같은 subject의 비슷한 latent day를 찾으면 크게 좋아졌다. 즉 Q2/Q3는 “subject prior”만으로는 부족하고, 같은 사람의 생활 상태 trajectory 안에서 위치를 찾아야 한다는 뜻이다.

## 이 후보가 베팅하는 세계관

이 후보는 다음 주장이다.

```text
test row의 숨은 label state는 같은 subject의 과거에서 이미 반복적으로 관측되었다.
하지만 그것을 그대로 복사하면 위험하고,
peer cohort가 그 row를 outlier로 인정할 때만 action으로 번역해야 한다.
```

즉 V131C류 cohort 아이디어를 단독 gate로 쓰지 않고, autobiographical memory posterior를 action으로 번역하는 안전장치로 쓴다.

## public 결과 해석법

좋아지면:

- 같은 subject trajectory가 실제 public/private label 생성 과정에 강하게 연결되어 있다는 뜻이다.
- cohort outlier는 단독 predictor가 아니라 memory posterior의 action gate로 가치가 있다는 뜻이다.
- HS-JEPA의 human-state representation은 subject autobiography + peer coordinate를 모두 가져야 한다.

나빠지면:

- local memory signal은 진짜지만 public/private row-target action으로 번역하는 과정이 아직 안전하지 않다는 뜻이다.
- peer margin이 public listener와 다르게 움직였을 수 있다.
- Q2/Q3/S-stage를 한 번에 크게 움직인 것이 Log Loss tail을 키웠을 수 있다.

## 이 아이디어의 논문적 의미

이 실험은 JEPA의 핵심을 생활 로그에 맞게 바꾼다.

I-JEPA가 image context로 missing target representation을 예측했다면, 여기서는 다음을 예측한다.

```text
현재 하루 context + subject autobiography + peer cohort context
-> 보이지 않는 human-state posterior
```

LeJEPA식 의심도 들어간다.

memory posterior가 좋아 보여도 바로 label로 쓰지 않는다. peer cohort, target별 reliability, failure-axis cosine을 통해 shortcut인지 확인한다.

그래서 이 architecture는 단순 memory model이 아니라, human-state representation을 action-safe row-target correction으로 번역하는 HS-JEPA decoder다.
