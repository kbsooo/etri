# Raw-KNN Override Safety Jury

## 한 줄 요약

HS-JEPA core/context를 raw KNN을 대체하는 전체 모델로 쓰지 않고, raw KNN이 실패할 row-target cell을 감지하는 safety jury로 사용했다.

## 왜 중요한가

이 실험은 public LB, 기존 submission probability, action teacher, frontier file을 사용하지 않는다. 따라서 결과가 좋다면 HS-JEPA core가 competition anchor 없이도 action-health를 판별한다는 증거가 된다.

## 핵심 결과

- raw KNN OOF logloss: `0.636997`
- best safety-jury policy: `gradient_boosted_gain_unguarded_topfrac_0.03`
- best safety-jury OOF logloss: `0.632478`
- delta vs raw KNN: `-0.004519`
- OOF switched cells: `22`
- target matched-null p(gain >= observed): `0.001000`
- target+family matched-null p(gain >= observed): `0.000500`
- best guarded policy: `gradient_boosted_gain_votes2_topfrac_0.02`
- best guarded OOF logloss: `0.635705`
- guarded delta vs raw KNN: `-0.001292`
- generated candidate: `submission_hsjepa_raw_knn_override_safety_jury_50450d26_uploadsafe.csv`

## Best policy target counts

| target | count |
| --- | --- |
| Q1 | 4 |
| Q2 | 0 |
| Q3 | 0 |
| S1 | 1 |
| S2 | 5 |
| S3 | 9 |
| S4 | 3 |

## Best policy expert-family counts

| expert_family | count |
| --- | --- |
| prior | 15 |
| core_geometry | 6 |
| core_action_health | 1 |

## Top local policies

| policy_name | logloss | switched_cells | mean_realized_gain_all_cells | positive_true_gain_rate | target_null_p_ge_observed | target_family_null_p_ge_observed |
| --- | --- | --- | --- | --- | --- | --- |
| gradient_boosted_gain_unguarded_topfrac_0.03 | 0.632478 | 22 | 0.004519 | 0.590909 | 0.001000 | 0.000500 |
| gradient_boosted_gain_unguarded_topfrac_0.04 | 0.632612 | 29 | 0.004385 | 0.586207 | 0.002000 | 0.001750 |
| gradient_boosted_gain_unguarded_threshold_0.080 | 0.632801 | 27 | 0.004197 | 0.592593 | 0.003250 | 0.001750 |
| gradient_boosted_gain_unguarded_topfrac_0.01 | 0.633543 | 7 | 0.003454 | 0.571429 | 0.001750 | 0.000750 |
| gradient_boosted_gain_unguarded_threshold_0.120 | 0.633591 | 6 | 0.003406 | 0.500000 | 0.000750 | 0.000500 |
| gradient_boosted_gain_unguarded_topfrac_0.02 | 0.633642 | 15 | 0.003355 | 0.466667 | 0.007250 | 0.008250 |
| gradient_boosted_gain_unguarded_topfrac_0.06 | 0.633932 | 44 | 0.003065 | 0.568182 | 0.021500 | 0.024000 |
| gradient_boosted_gain_unguarded_topfrac_0.08 | 0.635216 | 59 | 0.001781 | 0.576271 | 0.083750 | 0.085500 |
| gradient_boosted_gain_votes2_topfrac_0.02 | 0.635705 | 15 | 0.001292 | 0.666667 | 0.070000 | 0.064500 |
| gradient_boosted_gain_votes2_topfrac_0.03 | 0.635835 | 22 | 0.001162 | 0.636364 | 0.110750 | 0.096500 |
| gradient_boosted_gain_strong_votes2_topfrac_0.03 | 0.635841 | 22 | 0.001156 | 0.681818 | 0.103000 | 0.138250 |
| gradient_boosted_gain_votes3_topfrac_0.04 | 0.635867 | 29 | 0.001130 | 0.724138 | 0.109250 | 0.094250 |
| gradient_boosted_gain_votes3_topfrac_0.03 | 0.635983 | 22 | 0.001014 | 0.727273 | 0.106750 | 0.139500 |
| gradient_boosted_gain_core_families_votes2_topfrac_0.02 | 0.636095 | 15 | 0.000902 | 0.666667 | 0.105000 | 0.022000 |

## 논문용 해석

HS-JEPA의 역할은 모든 예측을 직접 만드는 것이 아니라, 강한 base world model이 언제 실패하는지 판별하는 latent action-health layer가 될 수 있다.

중요한 부정 결과도 있다. 여러 모델이 동시에 동의하는 consensus guard는 positive true-gain rate를 올리지만, 전체 logloss gain은 크게 줄였다. 즉 현재 신호는 넓고 안정적인 상식 consensus가 아니라 특정 route-risk surface에서만 드러나는 sharp failure boundary에 가깝다.

따라서 safety jury는 최종 release 장치라기보다, sharp boundary가 shortcut인지 아닌지 확인하는 stress diagnostic으로 쓰는 편이 맞다.

matched-null stress를 함께 기록하는 이유는 단순히 cell 몇 개를 운 좋게 고른 것인지, target/family 조건을 맞춘 무작위 선택보다 실제로 gain이 큰지를 구분하기 위해서다.