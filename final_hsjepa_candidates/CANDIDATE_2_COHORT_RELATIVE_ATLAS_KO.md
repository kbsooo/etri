# Candidate 2 - Cohort-Relative Human-State Atlas HS-JEPA

## 한 줄 요약

하루를 “이 사람의 평소”와 “비슷한 사람들의 평소”라는 두 좌표계에서 해석한 뒤, Candidate 1의 row-target correction을 cohort-relative human-state 기준으로 다시 번역한 최종 후보다.

## 이 후보가 거는 세계관

Candidate 1은 public-loss sensor 관점에서 강하다. 하지만 그 action이 인간 생활 상태 관점에서도 안전한지는 별도 문제다.

이 후보는 다음 질문을 건다.

> 어떤 row-target action은 public sensor에서는 좋아 보이지만, 개인/peer cohort 좌표계에서 보면 toxic할 수 있지 않은가?

따라서 OG raw lifelog에서 human-state atlas를 만들고, Candidate 1의 sparse action을 그대로 새 label로 쓰지 않고 row별/target별 gate로 재해석한다.

## teammate cohort 아이디어와의 결합

기존 cohort 아이디어의 핵심은 다음이었다.

- 이 사람은 어떤 생활 패턴 그룹에 속하는가?
- 오늘은 이 사람의 평소와 다른가?
- 오늘은 비슷한 사람들 사이에서도 튀는 날인가?

HS-JEPA는 여기에 한 가지 제약을 추가한다.

> cohort anomaly를 label에 직접 꽂지 말고, row-target action이 안전한지를 판단하는 hidden state context로 써야 한다.

즉 cohort module은 label predictor가 아니라 action-health gate다.

## HS-JEPA 해석

- context:
  - OG raw lifelog daily aggregation
  - 개인별 normal state
  - peer cohort normal state
  - Q/S peer target margin
  - Candidate 1 sparse action field

- target representation:
  - cohort-relative action-health
  - peer-only toxicity
  - personal/cohort axis disagreement

- predictor:
  - PCA human-state latent
  - subject fingerprint
  - KMeans peer cohort
  - subject normal distance / peer normal distance / target route margin

- decoder:
  - Candidate 1의 선택 cell은 유지한다.
  - 다만 cell별 logit 이동 강도를 cohort gate로 0.52~1.34배 조정한다.

## 코드

```bash
python3 final_hsjepa_candidates/candidate_2_cohort_relative_atlas.py
```

이 스크립트는 내부적으로 Candidate 1을 먼저 재현한 뒤, OG parquet에서 cohort atlas를 새로 만든다.

## 산출물

- 제출 파일:
  - `submission_final_candidate2_cohort_relative_atlas_2f54a36a_uploadsafe.csv`

- 상세 산출물:
  - `final_hsjepa_candidates/outputs/candidate_2_cohort_relative_atlas/candidate2_readout.json`
  - `final_hsjepa_candidates/outputs/candidate_2_cohort_relative_atlas/candidate2_action_audit.csv`
  - `final_hsjepa_candidates/outputs/candidate_2_cohort_relative_atlas/candidate2_test_cohort_atlas.csv`
  - `final_hsjepa_candidates/outputs/candidate_2_cohort_relative_atlas/submission_final_candidate2_cohort_relative_atlas_2f54a36a_uploadsafe.csv`

## 사용한 OG human-state latent

원본 parquet에서 하루 단위 feature를 만든다.

- screen/charging/light/activity
- step/distance/speed/calorie
- heart rate
- app usage category
- GPS movement
- Wi-Fi/BLE proximity
- ambience
- calendar/day-of-week/month-position

그 다음:

1. daily feature를 impute/standardize한다.
2. PCA 8차원 human-state latent를 만든다.
3. subject별 latent 평균/분산으로 lifestyle fingerprint를 만든다.
4. subject를 4개 peer cohort로 묶는다.
5. 각 row에 대해 개인 normal distance와 peer normal distance를 계산한다.
6. Q/S target margin을 peer cohort 안에서 계산한다.

## 재현 결과

- raw daily numeric feature count: `99`
- latent dims: `8`
- peer groups: `4`
- subjects: `10`
- changed cells: `94`
- changed rows: `82`
- mean cohort gate: `0.9848033735`
- min cohort gate: `0.7268048374`
- max cohort gate: `1.3240094788`
- upload-safe: `true`

Target별 changed cells:

- Q1: `9`
- Q2: `20`
- Q3: `11`
- S1: `14`
- S2: `14`
- S3: `11`
- S4: `15`

Listener diagnostic:

- base listener mean delta: `-0.0080667933`
- semantic listener mean delta: `-0.0091070752`
- hard-world shortcut cosine: `0.0091021034`

## Candidate 1과의 차이

Candidate 1:

- public-loss sensor가 고른 cell을 강하게 믿는다.
- 성능 우선 제출 후보다.

Candidate 2:

- cell 선택은 Candidate 1을 따르지만,
- 이동 강도는 인간 생활 상태 atlas로 다시 조절한다.
- cohort 아이디어를 논문 구조로 보여주기에 더 좋다.

## 제출 의미

좋아지면:

- public-loss action이 human-state/cohort geometry와 결합될 때 더 안전해진다는 뜻이다.
- HS-JEPA에서 “representation -> action-health -> row-target correction” 구조가 강화된다.

나빠지면:

- cohort anomaly는 설명력 있는 context이지만, 현재 public-loss action을 직접 개선하는 gate로는 아직 부족하다는 뜻이다.
- 이 경우 cohort module은 제출용 decoder가 아니라 논문용 representation/diagnostic module로 남기는 것이 맞다.

## 위험

- cohort는 subject가 10명뿐이라 peer group 안정성이 제한적이다.
- Candidate 1의 sparse action을 변환하므로, 좋은 public-loss action을 과도하게 약화할 수 있다.
- 그래서 제출 우선순위는 Candidate 1 다음이다.
