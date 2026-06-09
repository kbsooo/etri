# Final HS-JEPA Prototypes

이 디렉터리는 팀원이 과거 실험 히스토리를 몰라도 HS-JEPA 최종 아이디어 두 개를
OG 데이터에서 재현해 볼 수 있게 만든 end-to-end 프로토타입이다.

현재 기준 public best anchor는 다음 파일이다.

- `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB: `0.5677475939`

## 실행

프로젝트 루트(`/Users/kbsoo/Downloads/cl2`)에서 실행한다.

```bash
python3 final_hsjepa_prototypes/run_final_hsjepa_prototypes.py
```

스크립트는 다음을 한 번에 수행한다.

1. OG metric data와 raw lifelog parquet를 읽는다.
2. public score ledger에서 public-observed submission들을 읽는다.
3. 현재 best prediction을 hidden human-state anchor로 사용한다.
4. listener posterior를 target representation으로 사용한다.
5. public에서 벌점이 컸던 prediction 방향을 action-toxicity axis로 만든다.
6. cohort 없는 solver 후보 하나와 cohort 포함 solver 후보 하나를 생성한다.
7. upload-safe submission, action audit, diagnostic report를 쓴다.

## 생성되는 최종 후보

현재 기본 설정으로 생성되는 후보는 다음 두 개다.

1. `submission_final_no_cohort_equation_hsjepa_414e7077_uploadsafe.csv`
   - cohort를 쓰지 않는 Public-Private Equation HS-JEPA Solver
   - 현재 best에서 104개 row, 260개 row-target cell을 수정한다.
   - Q2는 움직이지 않는다.

2. `submission_final_with_cohort_atlas_hsjepa_bfeccc43_uploadsafe.csv`
   - cohort를 포함한 Personal-Cohort Atlas HS-JEPA Solver
   - 현재 best에서 96개 row, 220개 row-target cell을 수정한다.
   - Q2는 움직이지 않는다.

두 파일은 루트와 `final_hsjepa_prototypes/outputs/` 양쪽에 저장된다.

## 핵심 산출물

- `outputs/final_hsjepa_prototype_report.md`
  - 두 후보가 무엇을 바꿨고 어떤 세계관에 베팅하는지 요약한다.

- `outputs/prototype_summaries.json`
  - changed row/cell 수, target별 변경량, soft listener gain, bad-axis cosine을 기록한다.

- `outputs/no_cohort_action_audit.csv`
  - cohort 없는 solver가 선택한 row-target action 목록이다.

- `outputs/cohort_action_audit.csv`
  - cohort 포함 solver가 선택한 row-target action 목록이다.

- `outputs/no_cohort_cell_scores.csv`
  - 모든 test row-target cell의 no-cohort action score이다.

- `outputs/cohort_cell_scores.csv`
  - cohort feature가 붙은 모든 test row-target cell의 action score이다.

- `outputs/cohort_human_state_features_test.csv`
  - OG raw lifelog에서 만든 test-side human-state latent/cohort feature이다.

## HS-JEPA 해석

기존 tabular 모델은 보통 `feature -> label`을 직접 학습한다.

여기서 HS-JEPA는 다음처럼 문제를 바꾼다.

1. context를 만든다.
   - row order
   - subject-like signal
   - raw lifestyle/sensor logs
   - public-observed submission movement
   - current best와 failed action의 disagreement

2. hidden target representation을 만든다.
   - listener posterior
   - row-target route
   - action-health/toxicity field
   - personal/cohort anomaly coordinate

3. action을 바로 복제하지 않고 계획한다.
   - 어떤 row-target cell을 움직일지 선택한다.
   - public이 벌준 action direction과 정렬되면 억제한다.
   - listener direction이 강하고 toxicity가 낮은 cell만 움직인다.

즉 HS-JEPA는 label을 바로 맞히는 모델이 아니라,
보이는 생활 로그와 public sensor에서 보이지 않는 human-state/action-state를 예측한 뒤
그 representation을 안전한 correction field로 번역하는 구조다.

## 주의점

이 코드는 public LB oracle이 아니다.

`outputs/public_equation_proxy_loo.csv`는 public-observed file 7개만 사용한 작은
stress diagnostic이다. 이 proxy의 LOO MAE는 크기 때문에, public score를 직접
예측한다고 보면 안 된다.

하지만 이 proxy는 중요한 한 가지를 강제한다.

좋아 보이는 listener 방향이라도 이미 public에서 벌점이 컸던 action 방향과
정렬되면 다시 쓰지 않는다.

이 제약이 HS-JEPA를 단순 blend나 직접 prior tweaking과 구분한다.
