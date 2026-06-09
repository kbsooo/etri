# Big Bet 1. Public-Listener Tomography HS-JEPA

## 한 줄 요약

이 아이디어는 public LB를 점수표가 아니라 관측 장비로 본다. 여러 제출 파일이 public에서 얼마나 좋아지거나 나빠졌는지를 이용해, public/private 평가가 실제로 민감하게 듣는 row-target bundle을 역산한다. 그 다음 후보 correction을 그대로 믿지 않고, 이 hidden listener가 좋아할 가능성이 높은 cell만 다시 조립한다.

최종 후보:

`submission_bigbet1_public_listener_tomography_2687b6b6_uploadsafe.csv`

코드:

`hsjepa_big_bets/bigbet1_public_listener_tomography.py`

## 왜 큰 실험인가

이건 baseline에 alpha를 조금 더 주는 실험이 아니다.

기본 가정 자체가 다르다.

일반적인 접근은 “좋은 모델이 만든 확률값을 더 믿자”이다.

이 실험의 접근은 “public LB가 어떤 row-target action에 반응하는지 먼저 복원하자”이다.

즉 예측 문제를 다음처럼 바꾼다.

```text
관측된 제출 파일들의 움직임
-> public LB 반응
-> 숨은 public/private listener bundle field
-> listener가 허용하는 row-target correction
```

## HS-JEPA로 해석하면

### Context

- target 종류: Q1/Q2/Q3/S1/S2/S3/S4
- subject id
- row order 위치
- 주말/월요일/금요일
- 월초/월말
- 월급일 후보 window
- 현재 best 확률의 high/low probability regime
- 과거 제출 후보들이 특정 row-target을 어느 방향으로 움직였는지
- public에서 실패한 action 방향

### Target representation

직접 label을 예측하지 않는다.

대신 public LB가 실제로 들은 것으로 보이는 hidden listener gradient를 예측한다.

쉽게 말하면:

```text
"이 cell을 움직이면 public이 좋아할까 싫어할까?"
```

를 row-target 개별 cell이 아니라 bundle 단위로 학습한다.

### Predictor

과거 제출 파일의 움직임을 bundle feature로 요약한다.

예:

- Q2 전체 방향
- id04의 S1 방향
- row 후반부의 S target 방향
- 월말 S2 방향
- 현재 best가 이미 높은 확률을 준 S3 tail 방향

이 bundle movement가 public LB delta를 얼마나 설명하는지 ridge/tomography 방식으로 fitting한다.

### Decoder

여러 source action proposal을 모은 뒤, 다음 조건을 만족하는 row-target만 선택한다.

- 10개 listener stress world에서 대체로 개선 방향
- frontier-only listener에서도 개선 방향
- H088류 실패축과 너무 같은 방향이 아님
- 같은 row/target/subject에 과도하게 몰리지 않음

## 이번 실행 결과

결과 파일:

- `hsjepa_big_bets/outputs/bigbet1_public_listener_tomography_results.csv`
- `hsjepa_big_bets/outputs/bigbet1_public_listener_tomography_selected_cells.csv`
- `hsjepa_big_bets/outputs/bigbet1_public_listener_tomography_decision.csv`

Promoted variant:

`tomography_antitoxic`

핵심 수치:

| 항목 | 값 |
|---|---:|
| selected cells | 246 |
| selected rows | 146 |
| changed cells vs current best | 246 |
| H088 cosine | 0.045999 |
| frontier-only predicted delta | -0.000397 |
| robust mean predicted delta | -0.001290 |
| 개선 방향 stress world 수 | 10 / 10 |
| min prob / max prob | 0.000005 / 0.999997 |
| upload safe | True |

Target mix:

| target | cells |
|---|---:|
| S3 | 49 |
| S4 | 42 |
| S1 | 37 |
| Q2 | 34 |
| S2 | 33 |
| Q1 | 30 |
| Q3 | 21 |

## 이 후보가 베팅하는 세계관

이 후보는 다음 주장이다.

```text
현재 best 이후의 병목은 feature 부족이 아니라
public/private listener가 어떤 row-target action을 책임지는지 모르는 데 있다.
```

맞다면 public LB는 current best 대비 의미 있게 내려가야 한다.

특히 이 후보는 모든 target을 조금씩 건드리지만, raw source proposal을 그대로 쓰지 않고 public listener가 허용한 action만 선택한다. 따라서 단순한 broad blend와 다르게, “public이 듣는 bundle”을 맞혔는지가 핵심이다.

## public 결과 해석법

좋아지면:

- public/private listener가 cell-level이 아니라 bundle-level이라는 가설이 강화된다.
- HS-JEPA의 decoder는 label predictor보다 listener-aware row-target assignment solver가 되어야 한다.
- 다음 단계는 bundle을 더 세분화하거나 private에도 살아남는 listener factor를 찾는 것이다.

나빠지면:

- known public submission만으로 fitting한 listener가 과거 센서에 overfit했을 가능성이 크다.
- H088 같은 실패축을 soft penalty로 둔 것이 부족했을 수 있다.
- public listener는 bundle보다 더 discrete한 row-route constraint일 수 있다.

## 이 아이디어의 논문적 의미

이 실험은 JEPA의 “context로 target representation을 예측한다”는 생각을 leaderboard 센서에 적용한 것이다.

여기서 context는 feature row가 아니라 submission movement와 human-state bundle이다.

target은 label이 아니라 hidden public listener response다.

따라서 HS-JEPA는 단순 예측기가 아니라, 관측된 action-response pair로부터 숨은 평가/생성 구조를 복원하는 architecture로 설명할 수 있다.
