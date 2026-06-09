# H154 로컬 Semantic Source-Consensus Jackpot HS-JEPA

Date: 2026-06-09

## 질문

Gemini 기반 human narrative latent를 완전히 로컬에서 재현 가능한
TF-IDF + SVD semantic encoder로 바꿔도 public-safe high-responsibility
row-target action을 찾을 수 있는가?

## 세계관

이 실험은 hidden state를 단순한 row나 target으로 보지 않는다.
진짜 hidden state는 listener가 얼마나 듣는지까지 포함한 action field다.

```text
human-state narrative
  -> 로컬 semantic latent
  -> listener responsibility
  -> source-route consensus
  -> anti-H088 toxicity veto
  -> row-target correction
```

이게 맞으면 HS-JEPA 논문/팀 코드에서 closed embedding model에 의존할
필요가 줄어든다. semantic encoder는 context view일 뿐이고, 핵심은
보이는 human-state narrative와 source disagreement로 보이지 않는
listener/action representation을 예측하는 JEPA식 decoder다.

## 후보 결정표

| spec | selected_pairs | changed_cells_vs_h057 | changed_rows_vs_h057 | semantic_robust_mean_delta | semantic_robust_max_delta | base_robust_mean_delta | base_robust_max_delta | h088_move_cosine | decision_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| local_semantic_source_consensus | 374 | 109 | 85 | -0.002454049 | -0.000026202 | -0.003083789 | -0.000973448 | 0.001849670 | 5.223072975 |
| local_semantic_jackpot_balanced | 420 | 124 | 92 | -0.002888252 | 0.000410547 | -0.003433016 | -0.001085019 | 0.008113592 | 5.203628566 |
| local_semantic_frontier_needle | 82 | 55 | 44 | -0.000680963 | -0.000405536 | -0.000909498 | -0.000251367 | -0.000776679 | 3.243298239 |

## Semantic Listener 기준 후보 비교

| spec | file | changed_cells_vs_h057 | changed_rows_vs_h057 | h088_move_cosine | robust_positive_variant_count | robust_mean_pred_delta | robust_max_pred_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| local_semantic_source_consensus | submission_h154_local_semantic_source_consensus_36eeef08.csv | 109 | 85 | 0.001849670 | 10 | -0.002454049 | -0.000026202 |
| reference | submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 363 | 159 | 0.214751899 | 10 | -0.002386654 | -0.000624442 |
| local_semantic_frontier_needle | submission_h154_local_semantic_frontier_needle_381c3d03.csv | 55 | 44 | -0.000776679 | 10 | -0.000680963 | -0.000405536 |
| local_semantic_jackpot_balanced | submission_h154_local_semantic_jackpot_balanced_44c7c414.csv | 124 | 92 | 0.008113592 | 9 | -0.002888252 | 0.000410547 |
| reference | submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 349 | 154 | 0.121063141 | 9 | -0.002207993 | 0.001016602 |
| reference | submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 364 | 157 | 0.188791860 | 9 | -0.001815873 | 0.001138718 |
| reference | submission_bigbet1_public_listener_tomography_2687b6b6_uploadsafe.csv | 246 | 146 | 0.045999462 | 9 | -0.000952270 | 0.000518208 |

## 승격 후보

```json
{
  "embedding_source": "local_tfidf_svd",
  "uses_external_embedding_api": false,
  "base_file": "submission_h057_q2row_fullvector_state_7cde1a77_uploadsafe.csv",
  "best_spec": "local_semantic_source_consensus",
  "best_root_path": "/Users/kbsoo/Downloads/cl2/submission_h154_local_semantic_source_consensus_36eeef08_uploadsafe.csv",
  "best_upload_safe": true,
  "best_changed_cells_vs_h057": 95,
  "best_base_robust_mean_delta": -0.003083789142163823,
  "best_base_robust_max_delta": -0.0009734483945564275,
  "best_semantic_robust_mean_delta": -0.002454048860656497,
  "best_semantic_robust_max_delta": -2.620166081847813e-05,
  "best_h088_move_cosine": 0.0018496703697592563
}
```

## 해석

승격 후보는 calibration 미세조정이 아니라 jackpot 시도다.
베팅은 다음과 같다.

```text
여러 독립 HS-JEPA source route가 같은 방향을 가리키고,
그 action이 local human-state semantic latent 안에서도 좋게 읽히며,
H088 독성축과 거의 직교한다면,
그 row-target correction은 public-safe일 가능성이 있다.
```

public LB가 의미 있게 좋아지면 다음 아키텍처 단계는
`source-consensus listener responsibility`를 HS-JEPA의 메인 decoder로
정식화하는 것이다. 실패하면 그것도 정보가 있다. 그 경우 semantic
context는 offline ranking에는 도움을 주지만, 실제 public listener는
아직 narrative/cohort/source feature보다 더 날카로운 hidden subset에
지배된다는 뜻이다.
