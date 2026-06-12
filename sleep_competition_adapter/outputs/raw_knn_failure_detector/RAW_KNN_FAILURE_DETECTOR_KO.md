# Raw-KNN Failure Detector

## 목적

full contextual router가 raw KNN을 넘지 못했기 때문에, 이번에는 raw KNN을 기본값으로 두고 실패할 가능성이 높은 row-target cell만 다른 listener route로 전환한다.

이 실험은 public LB, 기존 submission probability, action teacher, frontier file을 쓰지 않는다.

## 핵심 결과

- raw KNN OOF logloss: `0.636997`
- best detector model: `gradient_boosted_gain`
- best detector policy: `topfrac` `0.04`
- best detector OOF logloss: `0.632612`
- delta vs raw KNN: `-0.004385`
- OOF switched cells: `29`
- generated candidate: `submission_hsjepa_raw_knn_failure_detector_2a097b16_uploadsafe.csv`

## Top OOF policies

| model | policy | param | logloss | switched_cells | switched_rate | mean_realized_gain |
| --- | --- | --- | --- | --- | --- | --- |
| gradient_boosted_gain | topfrac | 0.040000 | 0.632612 | 29 | 0.039456 | 0.004385 |
| gradient_boosted_gain | threshold | 0.080000 | 0.632801 | 27 | 0.036735 | 0.004197 |
| gradient_boosted_gain | threshold | 0.120000 | 0.633591 | 6 | 0.008163 | 0.003406 |
| gradient_boosted_gain | topfrac | 0.020000 | 0.633642 | 15 | 0.020408 | 0.003355 |
| gradient_boosted_gain | topfrac | 0.060000 | 0.633932 | 44 | 0.059864 | 0.003065 |
| gradient_boosted_gain | topfrac | 0.080000 | 0.635216 | 59 | 0.080272 | 0.001781 |
| gradient_boosted_gain | threshold | 0.040000 | 0.636646 | 66 | 0.089796 | 0.000351 |
| raw_knn_blend | baseline | 0.000000 | 0.636997 | 0 | 0.000000 | 0.000000 |
| random_forest_gain | threshold | 0.120000 | 0.637585 | 3 | 0.004082 | -0.000588 |
| gradient_boosted_gain | topfrac | 0.100000 | 0.637932 | 74 | 0.100680 | -0.000935 |
| extra_trees_gain | topfrac | 0.020000 | 0.638800 | 15 | 0.020408 | -0.001803 |
| extra_trees_gain | threshold | 0.120000 | 0.638842 | 1 | 0.001361 | -0.001845 |
| extra_trees_gain | topfrac | 0.040000 | 0.639330 | 29 | 0.039456 | -0.002333 |
| extra_trees_gain | threshold | 0.080000 | 0.639471 | 6 | 0.008163 | -0.002474 |
| gradient_boosted_gain | topfrac | 0.150000 | 0.639478 | 110 | 0.149660 | -0.002481 |
| gradient_boosted_gain | threshold | 0.020000 | 0.639555 | 134 | 0.182313 | -0.002558 |

## 해석

HS-JEPA route-risk signal은 broad router로 쓰면 불안정하지만, raw KNN failure detector로 좁히면 raw KNN보다 좋은 OOF 결과를 만든다.

이 결과는 HS-JEPA를 `full router`보다 `failure-aware listener override`로 정립하는 편이 현재 데이터에서는 더 강하다는 뜻이다.