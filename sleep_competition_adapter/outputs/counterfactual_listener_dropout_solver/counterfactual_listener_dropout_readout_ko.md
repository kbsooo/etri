# Counterfactual Listener-Dropout Solver

## 핵심 주장

이 실험은 HS-JEPA를 label predictor가 아니라 action-health architecture로 검증한다.
row-target action은 route/fusion/target-listener/anti-shortcut listener 중 하나가 사라져도 살아남아야 하며, 이미 public에서 나빴던 listener-confirmed action과 같은 방향이면 독성으로 본다.

## 왜 논문용인가

- `listener dropout`: 특정 관측자에만 맞는 shortcut action을 제거한다.
- `negative public sensor`: 실패한 제출을 점수표가 아니라 action toxicity label로 재해석한다.
- `invariant action`: 좋은 확률값이 아니라 보이지 않는 human-state에서 건강한 이동만 release한다.

## Ranking

| Rank | Variant | Cells | Rows | Health z | Min-score z | Survival z | Same-negative z | Opposite-negative z | Priority | File |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `dropout_fullfield_aggressive` | 17 | 10 | 4.8297 | 5.2360 | 5.5625 | 2.7925 | -2.0238 | 1.2860 | `submission_hsjepa_counterfactual_listener_dropout_dropout_fullfield_aggressive_a433fbc0_uploadsafe.csv` |
| 2 | `toxic_direction_inversion` | 15 | 8 | 4.5056 | 4.8430 | 4.9093 | 3.6885 | -0.9322 | 1.2648 | `submission_hsjepa_counterfactual_listener_dropout_toxic_direction_inversion_f0101750_uploadsafe.csv` |
| 3 | `negative_space_rescue` | 1 | 1 | 0.4890 | 0.2508 | 0.5442 | -1.2987 | -0.4602 | 0.1826 | `submission_hsjepa_counterfactual_listener_dropout_negative_space_rescue_d2465fcd_uploadsafe.csv` |
| 4 | `invariant_survivor` | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0500 | `submission_hsjepa_counterfactual_listener_dropout_invariant_survivor_7cde1a77_uploadsafe.csv` |
| 5 | `anti_listener_toxicity_veto` | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0500 | `submission_hsjepa_counterfactual_listener_dropout_anti_listener_toxicity_veto_7cde1a77_uploadsafe.csv` |

## Verdict

- Status: `counterfactual_listener_dropout_ready`
- Recommended information sensor: `submission_hsjepa_counterfactual_listener_dropout_dropout_fullfield_aggressive_a433fbc0_uploadsafe.csv`
- Recommended thesis sensor: `submission_hsjepa_counterfactual_listener_dropout_invariant_survivor_7cde1a77_uploadsafe.csv`

## Public LB 해석

- 좋아지면: HS-JEPA의 contribution은 `더 좋은 feature`가 아니라 `listener가 바뀌어도 안전한 action만 release하는 구조`라는 주장이 강해진다.
- 나빠지면: listener-dropout은 local geometry는 좋지만 public/private action equation에는 과하게 보수적이거나, negative sensor의 cell-level toxicity 전이가 틀렸다는 뜻이다.
- `negative_space_rescue`가 좋아지면: 실패 제출들이 단순히 버릴 것이 아니라, 반대 방향 action manifold를 가리키는 센서였다는 세계관이 살아난다.
