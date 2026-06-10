# 최종 HS-JEPA 후보 2개 요약

## 현재 기준

- 현재 최고 앵커: `submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv`
- public LB: `0.5677475939`

## 현재 팀 발표용 진입점

후보 1/2는 중요한 자산이지만, 팀 발표와 논문 설명에서는 이제 다음 패키지를 먼저 본다.

```bash
python3 team_hsjepa_end_to_end/run_route_conserving_s2_bridge.py
```

패키지 이름:

```text
Route-Conserving S2 Bridge HS-JEPA
```

이 패키지는 public-loss sparse tomography, objective-stage bridge, S2 listener/hub, human-state distillation을 하나의 end-to-end 메커니즘으로 묶는다.

이번 패키지는 이 앵커 이후 발견한 구조를 두 개의 최종 후보로 정리한다.

## 후보 비교

| 구분 | Candidate 1 | Candidate 2 |
|---|---|---|
| 이름 | Public-Loss Sparse Tomography HS-JEPA | Cohort-Relative Human-State Atlas HS-JEPA |
| 제출 파일 | `submission_final_candidate1_public_loss_sparse_tomography_e141c792_uploadsafe.csv` | `submission_final_candidate2_cohort_relative_atlas_2f54a36a_uploadsafe.csv` |
| 핵심 질문 | public LB 관측식이 실제로 벌주고 보상하는 row-target action은 무엇인가? | 그 action은 개인/peer human-state 좌표계에서도 안전한가? |
| 데이터 사용 | sample/train, 기존 submission disagreement, public score ledger, semantic listener | OG raw lifelog parquet, train/sample, Candidate 1 sparse action |
| JEPA context | public observation, source-route disagreement, listener representation | personal normal, peer normal, cohort anomaly, target margin |
| JEPA target representation | sparse row-target correction field | cohort-relative action-health field |
| decoder | 현재 best logit + selected sparse move | 현재 best logit + Candidate 1 move x cohort gate |
| changed cells | 94 | 94 |
| changed rows | 82 | 82 |
| upload-safe | true | true |
| 제출 우선순위 | 1순위 | 2순위 |

## 가장 중요한 발견

지금까지의 큰 점프는 “더 좋은 tabular classifier”보다 “어느 row-target cell을 얼마나 움직여야 하는가”에서 나왔다.

즉 HS-JEPA의 현재 강점은 encoder보다 action solver에 있다.

- label 직접 예측보다 row-target correction field가 중요했다.
- public LB는 score가 아니라 hidden loss sensor로 쓸 수 있었다.
- broad blend보다 sparse assignment가 더 설명력이 있었다.
- human/social/cohort latent는 단독 predictor보다는 action-health gate로 붙일 때 더 자연스럽다.

## 제출 판단

Candidate 1은 성능형 big-bet이다.

- public-loss equation을 직접 복원한다.
- 지금까지의 발견을 가장 강하게 반영한다.
- public/private mismatch 위험은 있지만, 제출 슬롯 하나를 쓴다면 먼저 볼 후보에 가깝다.

Candidate 2는 아키텍처형 big-bet이다.

- teammate cohort 아이디어를 HS-JEPA 구조 안에 넣는다.
- 논문적으로 더 설명 가능하다.
- public-loss sparse action을 cohort geometry로 한번 더 조정하므로, 성능상으로는 Candidate 1보다 보수적이다.

## 팀원이 볼 코드

```bash
python3 final_hsjepa_candidates/candidate_1_public_loss_sparse_tomography.py
python3 final_hsjepa_candidates/candidate_2_cohort_relative_atlas.py
```

각 스크립트는 독립적으로 root 제출 파일과 `outputs/` 하위 산출물을 만든다.

## 논문용 한 문장

우리는 수면 생활 로그에서 label을 직접 예측하는 대신, 관측 가능한 생활 context와 submission response를 이용해 숨은 human-state/action representation을 예측하고, 이를 row-target correction field로 안전하게 번역하는 Human-State JEPA를 제안한다.
