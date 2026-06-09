# HS-JEPA 최종 아이디어 2개

이 문서는 팀원이 이전 실험 번호를 몰라도 이해할 수 있도록, HS-JEPA 최종
프로토타입 두 개를 아이디어 중심으로 설명한다.

현재 최고 public 관측값은 다음 파일이다.

- `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB: `0.5677475939`

이 파일은 목표가 아니라 기준점이다. 최종 아이디어는 이 기준점을 더 잘 설명하고,
그 설명을 바탕으로 다음 correction action을 고르는 구조다.

## 공통 출발점

우리는 이 문제를 단순한 `feature -> 7개 label` 예측으로 보지 않는다.

수면/생활 로그에는 사람이 하루를 살아가는 숨은 상태가 있다.

- 피로 누적
- 루틴 붕괴
- 보상 수면
- 야간 스크린/소셜 사용
- 이동량/외출
- 충전/화면/센서 품질
- subject별 생활 리듬
- public/private subset에서 다르게 보이는 action 반응

HS-JEPA의 핵심은 이 숨은 상태를 직접 label로 찍는 것이 아니라,
먼저 hidden human-state representation으로 만든 다음,
그 representation이 어떤 row-target correction으로 번역되어야 안전한지 푸는 것이다.

JEPA식으로 말하면:

- context: 관측 가능한 로그와 기존 public sensor 반응
- target representation: label 자체가 아니라 listener posterior, row-target route, action-health field
- predictor: context에서 hidden representation을 예측
- planner/decoder: 그 hidden representation을 safe correction action으로 번역

LeCun의 JEPA/world-model 관점에서 중요한 차이는 이것이다.

행동을 바로 imitation하지 않는다.
행동의 결과를 먼저 예측하고, 그 결과가 안전한 action만 선택한다.

이 대회에서는 “행동”이 robot action이 아니라 확률표 correction action이다.

## 아이디어 1: Public-Private Equation HS-JEPA Solver

### 한 줄 요약

cohort를 쓰지 않고, public에서 관측된 좋은/나쁜 submission movement를 이용해
row-target action toxicity를 추정한 뒤, 현재 best에서 안전해 보이는 cell만 움직인다.

### 왜 필요한가

현재 best 근처에서는 단순히 더 좋은 feature를 붙인다고 크게 좋아지지 않는다.

이유는 모델이 signal을 못 봐서라기보다,
어떤 row-target을 움직이면 public이 벌주는지 모르는 상태에서 action을 내기 때문이다.

즉 병목은 prediction capacity보다 action translation에 가깝다.

### 구조

1. 현재 best prediction을 상태 anchor로 둔다.
2. listener posterior를 hidden target representation으로 둔다.
3. public score가 알려진 submission들을 public sensor observation으로 읽는다.
4. current best보다 나빴던 movement를 action-toxicity axis로 만든다.
5. 각 row-target cell에 대해 다음을 계산한다.
   - listener 방향으로 움직이면 soft target상 이득이 있는가?
   - 그 방향이 public-bad movement와 같은 방향인가?
   - 현재 best가 이미 발견한 row-state route와 연결되는가?
   - Q2/S1/S4처럼 public에서 민감한 target인가?
6. toxicity가 낮고 listener gain이 큰 cell만 선택한다.
7. current best에서 선택된 cell만 logit space에서 이동한다.

### 생성 후보

- `submission_final_no_cohort_equation_hsjepa_414e7077_uploadsafe.csv`

### 현재 산출물 기준 특징

- changed rows: 104
- changed cells: 260
- Q2 changed cells: 0
- soft listener delta vs current best: `-0.0003502623`
- H088 bad-action axis cosine: `0.0110420`
- H010 objective S1/S4 bad route cosine: `-0.1214526`

### 이 후보가 베팅하는 세계관

현재 best는 hidden row-state를 일부 맞혔다.
하지만 아직 모든 row-target cell이 최적으로 번역된 것은 아니다.

public에서 실패한 action 방향을 피하면서 listener representation 쪽으로
조금 더 이동하면, current best보다 좋은 public response가 나올 수 있다.

### public LB가 좋아지면 의미

HS-JEPA의 핵심 병목이 hidden state discovery 이후의
row-target action translation이었다는 해석이 강해진다.

즉 이 대회에서 중요한 것은 feature를 더 만드는 것보다,
이미 발견한 hidden state를 어떤 target/cell에 안전하게 번역할지라는 뜻이다.

### public LB가 나빠지면 의미

listener posterior 자체가 아직 public-specific shortcut일 수 있다.

또는 current best 이후의 추가 이동은 이미 irreducible risk에 가까워서,
더 강한 action-world model이 필요하다는 뜻이다.

## 아이디어 2: Personal-Cohort Atlas HS-JEPA Solver

### 한 줄 요약

하루를 개인의 평소 상태와만 비교하지 않고, 비슷한 생활 패턴의 peer cohort 안에서도
비교한 뒤, 그 cohort coordinate가 뒷받침하는 row-target action만 선택한다.

### 왜 필요한가

같은 사람의 과거만 보면 그 사람이 어떤 생활 유형인지 알기 어렵다.

예를 들어 어떤 하루가 개인 기준으로는 평범해 보여도,
비슷한 사람들 사이에서는 매우 튀는 날일 수 있다.

반대로 개인 기준으로는 특이해 보여도,
그 사람의 cohort 안에서는 자연스러운 변화일 수 있다.

따라서 hidden human-state는 최소 두 좌표계에서 봐야 한다.

- personal coordinate: 이 사람의 평소 기준
- cohort coordinate: 비슷한 사람들의 상태 공간 기준

### 구조

1. OG raw lifelog parquet에서 daily feature를 만든다.
   - screen
   - charging
   - activity
   - pedometer
   - heart rate
   - usage stats
   - GPS
   - WiFi/BLE
   - ambience
   - calendar/day signal
2. daily feature를 PCA latent로 압축한다.
3. subject별 latent 평균/분산으로 lifestyle fingerprint를 만든다.
4. subject를 4개 peer cohort로 묶는다.
5. 각 test row에 대해 다음을 계산한다.
   - 오늘이 subject normal에서 얼마나 먼가?
   - 오늘이 peer normal에서 얼마나 먼가?
   - subject normal과 peer normal의 차이는 어떤가?
   - peer group 안에서 target-positive 상태와 가까운가?
6. 이 cohort coordinate를 Public-Private Equation Solver의 action score에 붙인다.
7. cohort evidence가 있는 row-target action만 더 강하게 선택한다.

### 생성 후보

- `submission_final_with_cohort_atlas_hsjepa_bfeccc43_uploadsafe.csv`

### 현재 산출물 기준 특징

- changed rows: 96
- changed cells: 220
- Q2 changed cells: 0
- soft listener delta vs current best: `-0.0003179116`
- H088 bad-action axis cosine: `0.0295209`
- H010 objective S1/S4 bad route cosine: `-0.1221567`
- cohort latent dimensions: 8
- peer cohort count: 4
- raw daily feature count: 99

### 이 후보가 베팅하는 세계관

row-target action은 public sensor만으로는 불안정하다.

하지만 어떤 row가 personal/cohort coordinate에서 동시에 설명되면,
그 action은 단순 public overfit이 아니라 실제 human-state correction일 가능성이 커진다.

즉 cohort는 label rule이 아니라 action safety context다.

### public LB가 좋아지면 의미

HS-JEPA에 cohort atlas를 붙이는 방향이 유효하다.

개인의 과거뿐 아니라 peer group 안에서의 이상성이
수면/생활 상태 correction에 실제로 기여한다는 뜻이다.

### public LB가 나빠지면 의미

현재 cohort latent가 아직 action-grade representation은 아니라는 뜻이다.

이 경우 cohort 아이디어 자체를 버리기보다,
cohort를 직접 correction gate로 쓰지 말고 contrastive/self-supervised target으로
다시 학습해야 한다.

## 두 아이디어의 차이

| 항목 | Public-Private Equation Solver | Personal-Cohort Atlas Solver |
| --- | --- | --- |
| cohort 사용 | 안 함 | 사용 |
| 핵심 질문 | public이 벌주는 action 방향은 무엇인가? | 이 action이 개인/peer 상태 좌표계에서도 설명되는가? |
| 주요 context | public-observed submissions, listener posterior, current best route | raw lifelog latent, subject fingerprint, peer cohort, personal/cohort anomaly |
| target representation | listener/action-health field | listener/action-health field + cohort coordinate |
| 장점 | 더 직접적으로 public-private action toxicity를 겨냥 | 논문적으로 human-state architecture가 더 분명함 |
| 위험 | listener posterior shortcut 가능성 | cohort latent가 action-grade가 아닐 수 있음 |

## 팀원에게 보여줄 코드 포인트

핵심 파일은 하나다.

- `final_hsjepa_prototypes/run_final_hsjepa_prototypes.py`

이 파일에서 볼 부분:

1. `build_cell_frame`
   - public sensor와 listener posterior에서 row-target action score를 만든다.

2. `build_or_load_cohort_features`
   - OG raw lifelog에서 human-state latent와 peer cohort를 만든다.

3. `add_cohort_scores`
   - cohort coordinate를 action score에 붙인다.

4. `choose_actions`
   - row-target assignment solver 역할을 한다.

5. `materialize_candidate`
   - 선택된 action을 실제 submission probability로 번역한다.

6. `summarize_candidate`
   - listener gain과 bad-axis cosine으로 action safety를 진단한다.

## 현재 가장 중요한 판단

이 두 후보는 단순한 blend가 아니다.

둘 다 다음 주장 중 하나를 테스트한다.

1. 0.567대 병목은 hidden state 발견 부족이 아니라 action toxicity translation이다.
2. cohort coordinate는 label rule이 아니라 action safety context로 써야 한다.

따라서 public LB 확인 가치가 있는 순서는 다음이다.

1. `submission_final_no_cohort_equation_hsjepa_414e7077_uploadsafe.csv`
2. `submission_final_with_cohort_atlas_hsjepa_bfeccc43_uploadsafe.csv`

첫 번째가 좋아지면 action equation solver가 핵심이다.
두 번째까지 좋아지면 cohort atlas를 HS-JEPA의 정식 구성 요소로 가져갈 수 있다.
