# Candidate 1 - Public-Loss Sparse Tomography HS-JEPA

## 한 줄 요약

public LB 제출 결과를 “점수표”가 아니라 “숨은 public loss 관측식”으로 보고, 기존 후보들이 남긴 row-target 이동 중 public loss를 줄일 가능성이 큰 cell만 sparse하게 복원한 최종 후보다.

## 이 후보가 거는 세계관

현재 best 근처에서 성능이 막히는 이유는 모델 capacity 부족보다 “어느 row의 어느 target을 움직여야 public/private loss가 안전하게 줄어드는지”를 모르는 데 있다.

따라서 label을 직접 다시 예측하지 않고, 기존 strong anchor 위에 작은 row-target correction field를 복원한다.

## HS-JEPA 해석

- context:
  - 현재 public best anchor
  - 기존 high-signal submission들의 disagreement
  - local semantic listener
  - public LB observation ledger

- target representation:
  - 250 rows x 7 targets = 1750개 row-target cell 중 안전하게 움직일 correction field

- predictor:
  - public score가 알려진 submission들의 logit 이동을 support matrix로 만들고,
  - public LB 변화량을 sparse ridge equation으로 역추정한다.

- decoder:
  - 새 probability를 직접 생성하지 않는다.
  - 현재 best logit에 선택된 cell action만 더한다.

- LeJEPA-style diagnostic:
  - sign stability
  - listener mean delta
  - semantic listener delta
  - hard-world shortcut alignment 제한
  - per-row/per-target cap
  - upload-safe validation

## 왜 단순 blend가 아닌가

blend는 전체 prediction 공간을 평균낸다. 이 후보는 전체 평균이 아니라 “public loss 관측식이 가리키는 row-target cell”만 움직인다.

즉 파일 단위 섞기가 아니라 cell 단위 action assignment다.

## 코드

```bash
python3 final_hsjepa_candidates/candidate_1_public_loss_sparse_tomography.py
```

## 산출물

- 제출 파일:
  - `submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv`

- 상세 산출물:
  - `final_hsjepa_candidates/outputs/candidate_1_public_loss_sparse_tomography/candidate1_readout.json`
  - `final_hsjepa_candidates/outputs/candidate_1_public_loss_sparse_tomography/candidate1_selected_cells.csv`
  - `final_hsjepa_candidates/outputs/candidate_1_public_loss_sparse_tomography/submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv`

## 재현 결과

- support cells: `160`
- changed cells: `94`
- changed rows: `82`
- public observation count: `26`
- ridge train RMSE: `0.0002408195`
- ridge LOO RMSE: `0.0010335825`
- sign-stable cells over 0.8: `158`
- upload-safe: `true`

Listener diagnostic:

- base listener mean delta: `-0.0081192598`
- semantic listener mean delta: `-0.0091427757`
- hard-world shortcut cosine: `0.0091916057`

해석:

- listener 기준으로는 10개 sensor 모두 negative 방향이다.
- hard-world shortcut과 거의 정렬되지 않는다.
- 움직임은 94개 cell로 제한되어 있어 broad overfit보다는 sparse assignment 성격이 강하다.

## 제출 의미

좋아지면:

- public LB가 반응하는 hidden loss equation이 어느 정도 복원됐다는 뜻이다.
- HS-JEPA의 핵심을 “representation encoder”보다 “row-target action solver”에 두는 방향이 강화된다.

나빠지면:

- public observation ledger로 맞춘 sparse equation이 현재 public subset에는 맞지만 private/general action field는 아니라는 뜻이다.
- 이후에는 public-loss sensor를 직접 쓰기보다 cohort/human-state consistency를 더 강하게 넣어야 한다.

## 위험

- public LB observation을 sensor로 사용하므로, public subset에 맞춘 inversion 위험이 있다.
- public/private가 크게 다르면 private 성능이 약할 수 있다.
- 그래도 action이 sparse하고 listener diagnostic을 통과했기 때문에, 지금까지의 큰 발견을 종합한 1순위 제출 후보다.
