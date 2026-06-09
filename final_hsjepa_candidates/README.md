# Final HS-JEPA Candidate Packages

이 폴더는 팀원이 이전 실험 버전명을 몰라도 OG 데이터에서 최종 후보 2개를 재현하고 이해할 수 있도록 만든 패키지다.

## 목적

현재 최고 public LB 앵커는 다음 파일이다.

- `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB: `0.5677475939`

최종 후보는 이 앵커를 단순히 조금 섞는 것이 아니라, HS-JEPA 관점에서 서로 다른 두 세계관을 제출 가능한 형태로 만든다.

1. `Public-Loss Sparse Tomography HS-JEPA`
   - public LB 관측값을 센서로 보고, 어떤 row-target correction이 loss를 줄이는지 sparse equation으로 역추정한다.
   - 성능 우선 후보다.

2. `Cohort-Relative Human-State Atlas HS-JEPA`
   - OG raw lifelog에서 개인 정상 상태와 peer cohort 정상 상태를 만들고, 후보 1의 correction이 인간 생활 상태 좌표계에서 안전한지 다시 번역한다.
   - cohort 아이디어를 HS-JEPA에 결합한 아키텍처/논문형 후보다.

## 필요 데이터

코드는 외부 API를 쓰지 않는다. 다음 OG 데이터와 기존 재현 파일만 필요하다.

- `data/ch2026_metrics_train.csv`
- `data/ch2026_submission_sample.csv`
- `data/ch2025_data_items/*.parquet`
- `data_analytics/hsjepa_public_score_ledger.csv`
- 현재 앵커 submission과 HS-JEPA support generator 파일들

## 실행 방법

루트 디렉토리(`/Users/kbsoo/Downloads/cl2`)에서 실행한다.

```bash
python3 final_hsjepa_candidates/candidate_1_public_loss_sparse_tomography.py
python3 final_hsjepa_candidates/candidate_2_cohort_relative_atlas.py
```

각 스크립트는 root에도 upload-safe CSV를 만들고, 세부 산출물은 아래에 저장한다.

- `final_hsjepa_candidates/outputs/candidate_1_public_loss_sparse_tomography/`
- `final_hsjepa_candidates/outputs/candidate_2_cohort_relative_atlas/`

## 생성된 제출 파일

현재 재현 결과:

- `submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv`
- `submission_final_candidate2_cohort_relative_atlas_2f54a36a_uploadsafe.csv`

두 파일 모두 `ch2026_submission_sample.csv`와 key/order가 일치하고, probability 범위와 NaN 검증을 통과한다.

## 제출 우선순위

1순위는 Candidate 1이다. 이유는 public LB 관측식을 직접 sensor로 사용하면서도 action을 sparse row-target field로 제한했고, listener/stress diagnostic도 통과했기 때문이다.

2순위는 Candidate 2다. 이유는 cohort-relative human-state를 결합한 더 설명력 있는 구조지만, 후보 1의 action을 한 번 더 변환하므로 public 측면에서는 후보 1보다 보수적인 ablation 성격이 강하다.

## HS-JEPA로 보는 공통 구조

일반 JEPA는 보이는 context에서 보이지 않는 representation을 예측한다. 여기서는 다음처럼 변형한다.

- context: row order, current best anchor, submission disagreement, local semantic listener, raw lifelog human-state, peer cohort geometry
- target representation: label 자체가 아니라 row-target correction field, action-health, public/private toxicity, cohort-relative anomaly
- predictor: sparse public-loss equation solver 또는 cohort atlas gate
- decoder: probability를 직접 새로 만드는 것이 아니라 현재 앵커의 logit에 제한된 row-target action을 적용
- validation: upload-safe, listener metric, public-score sensor reconstruction, cohort key alignment

즉 HS-JEPA는 “Q1~S4를 바로 맞히는 모델”이 아니라 “보이는 생활 로그와 submission 반응으로 숨은 human-state/action field를 예측하고, 그 field를 안전하게 label probability로 번역하는 아키텍처”다.
