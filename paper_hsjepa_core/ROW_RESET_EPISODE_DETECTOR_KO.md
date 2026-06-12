# Row Reset Episode Detector

## 한 줄 요약

cell-level failure boundary를 full-row hidden episode reset 문제로 재정의했다.

이 실험은 HS-JEPA를 `확률값을 조금 보정하는 모델`이 아니라,
`raw lifelog memory를 계속 믿어도 되는 날인지, 아니면 row 전체를 더 안전한 route로 reset해야 하는 날인지`를 판별하는 hidden episode detector로 사용한다.

## 재현 명령

```bash
python3 sleep_competition_adapter/row_reset_episode_detector.py
```

입력은 OG feature/label/sample만 사용한다. public score ledger, 기존 submission probability, action teacher, frontier file은 사용하지 않는다.

중요한 leakage guard:

- 학습 target은 train OOF의 `raw row loss - reset route row loss`다.
- feature에서는 모든 loss-derived column과 detector OOF score column을 제거한다.
- test에서는 label/loss가 없으므로 같은 context/route feature만 만들고 detector가 reset route를 고른다.

## 핵심 결과

- raw KNN OOF logloss: `0.636997`
- best row reset law: `full_row_context__elasticnet_sparse`
- best OOF logloss: `0.634030`
- delta vs raw KNN: `-0.002967`
- selected OOF rows: `6`
- row-null p(gain >= observed): `0.005833`
- generated candidate: `submission_hsjepa_row_reset_episode_detector_9054c5d1_uploadsafe.csv`
- submission priority: `high_information_sensor_row_episode_reset`
- test switched rows: `15`
- test switched cells: `105`
- test route counts: `{'subject_prior': 49, 'global_prior': 35, 'core_knn_blend': 21}`

## 무엇을 발견했나

이전 failure-boundary law는 cell-level detector였지만, 실제 선택은 여러 target에 흩어진 독립 cell이 아니라 특정 row 전체를 움직이는 형태에 가까웠다.
따라서 이 실험은 문제를 `어느 target을 고칠까`가 아니라 `어느 day episode에서 raw memory가 통째로 실패하는가`로 바꿨다.

clean OOF에서도 top 6개 row reset이 raw KNN 대비 `-0.002967` logloss를 만들었고, row-null p-value는 `0.005833`이다.
이는 row episode reset이 단순 랜덤 row 선택보다는 강한 구조라는 뜻이다.

다만 효과 크기는 failure-boundary law보다 작다. 즉 row episode는 존재하지만, 최종 release에는 여전히 target/listener별 assignment decoder가 필요하다.

## Top features

| feature | coef | abs_coef |
| --- | --- | --- |
| route_confidence_mean | 0.042102 | 0.042102 |
| route_is_global_prior | 0.027621 | 0.027621 |
| global_prior__pred_std | 0.024490 | 0.024490 |
| expert_prob_range__std | -0.017458 | 0.017458 |
| route_abs_vs_raw_max | -0.017307 | 0.017307 |
| raw_knn_blend__pred_min | 0.016168 | 0.016168 |
| core_knn_blend__pred_mean | -0.015746 | 0.015746 |
| raw_knn_blend__pred_max | 0.013443 | 0.013443 |
| raw_action_core_health__high_margin_listener_health__pred_min | -0.012204 | 0.012204 |
| route_abs_vs_core_mean | -0.008985 | 0.008985 |
| row_mod_28 | 0.008234 | 0.008234 |
| subject_row_index_norm | 0.007584 | 0.007584 |
| route_is_subject_prior | -0.006845 | 0.006845 |
| subject_global_gap__mean | -0.006151 | 0.006151 |
| peer_outlier_rank | 0.005855 | 0.005855 |
| subject_minus_peer_dist | -0.004397 | 0.004397 |
| month_end | -0.004338 | 0.004338 |
| subject_prior__confidence_mean | -0.004224 | 0.004224 |

## Top policies

| law_name | policy | param | logloss | selected_rows | switched_cells | mean_realized_gain_all_rows | positive_row_gain_rate | row_null_p_ge_observed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_row_context__elasticnet_sparse | topfrac | 0.060000 | 0.634030 | 6 | 42 | 0.002967 | 0.833333 | 0.005833 |
| full_row_context__elasticnet_sparse | topfrac | 0.080000 | 0.634182 | 8 | 56 | 0.002815 | 0.750000 | 0.012000 |
| full_row_context__elasticnet_sparse | threshold | 0.040000 | 0.634327 | 9 | 63 | 0.002670 | 0.666667 | 0.015000 |
| full_row_context__elasticnet_sparse | topfrac | 0.040000 | 0.634454 | 4 | 28 | 0.002543 | 1.000000 | 0.007167 |
| episode_context__elasticnet_sparse | topfrac | 0.150000 | 0.634654 | 16 | 112 | 0.002343 | 0.750000 | 0.017167 |
| episode_context__elasticnet_sparse | topfrac | 0.200000 | 0.634921 | 21 | 147 | 0.002076 | 0.714286 | 0.016333 |
| full_row_context__elasticnet_sparse | topfrac | 0.150000 | 0.635072 | 16 | 112 | 0.001926 | 0.687500 | 0.033167 |
| full_row_context__elasticnet_sparse | topfrac | 0.100000 | 0.635257 | 10 | 70 | 0.001740 | 0.600000 | 0.052000 |
| full_row_context__elasticnet_sparse | topfrac | 0.200000 | 0.635387 | 21 | 147 | 0.001610 | 0.571429 | 0.033667 |
| route_reset_context__elasticnet_sparse | topfrac | 0.040000 | 0.635473 | 4 | 28 | 0.001524 | 0.750000 | 0.040833 |
| route_reset_context__elasticnet_sparse | topfrac | 0.020000 | 0.635863 | 2 | 14 | 0.001134 | 1.000000 | 0.048500 |
| route_reset_context__elasticnet_sparse | topfrac | 0.060000 | 0.635887 | 6 | 42 | 0.001110 | 0.666667 | 0.086333 |
| full_row_context__elasticnet_sparse | topfrac | 0.020000 | 0.635981 | 2 | 14 | 0.001016 | 1.000000 | 0.067667 |
| episode_context__tree_depth2_leaf5 | topfrac | 0.010000 | 0.635990 | 1 | 7 | 0.001007 | 1.000000 | 0.122667 |

## 논문용 해석

이 실험은 HS-JEPA release를 row-target micro action이 아니라 hidden episode reset으로 재정의한다.

성공하면 raw lifelog memory가 전체 target vector 차원에서 무너지는 episode가 있고, HS-JEPA context가 그 episode를 탐지한다는 증거다.

실패하면 직전 prior-reset law는 cell-pair ranking의 산물이지 독립적인 row episode detector로 일반화되지는 않는다는 뜻이다.

현재 결과는 중간 결론이다.

- `살아남은 주장`: raw memory가 row 전체 차원에서 실패하는 hidden episode가 있고, HS-JEPA context는 이를 OOF에서 일부 탐지한다.
- `죽은 과장`: row reset detector만으로 최종 문제를 해결할 수 있다는 주장은 아직 부족하다.
- `다음 과제`: row episode detector를 target/listener assignment solver와 결합해, row 전체 reset과 target별 selective reset을 구분해야 한다.