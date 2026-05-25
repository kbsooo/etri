# CL Public-Calibrated Validation

## What Changed

This validation keeps fold-local CatBoost predictions for every validation row instead of only aggregate fold losses. It then scores the same blend recipes used for tomorrow's candidate files.

Public labels are unavailable, so this is not a literal perfect validator. The improvement is that the validator is now calibrated against today's observed public feedback and explicitly reports when a candidate is an extrapolation beyond known feedback.

## Known Public Bridge

| recipe | mirror_hole_avg | public_calibrated_lb_estimate | known_public_lb |
|---|---|---|---|
| sleep_state | 0.627562 | 0.616498 | 0.614622 |
| catboost_safe | 0.628868 | 0.619521 | 0.621864 |
| anchor | 0.634109 | 0.631654 | 0.631187 |

## Candidate Ranking

| recipe | local_weighted | chrono_tail | hole_v1 | mirror_v1 | mirror_hole_avg | worst_family | mean_abs_move | public_calibrated_lb_estimate | known_public_lb |
|---|---|---|---|---|---|---|---|---|---|
| sleep_state | 0.631710 | 0.636806 | 0.619343 | 0.635781 | 0.627562 | 0.636806 | 0.039847 | 0.616498 | 0.614622 |
| consensus | 0.632374 | 0.638040 | 0.619534 | 0.636388 | 0.627961 | 0.638040 | 0.043894 | 0.617422 | nan |
| rowgate | 0.632944 | 0.639277 | 0.619785 | 0.636758 | 0.628272 | 0.639277 | 0.045307 | 0.618141 | nan |
| catboost_safe | 0.632362 | 0.635890 | 0.620950 | 0.636785 | 0.628868 | 0.636785 | 0.026797 | 0.619521 | 0.621864 |
| public_axis_step2 | 0.634169 | 0.640106 | 0.620765 | 0.638347 | 0.629556 | 0.640106 | 0.050033 | 0.621114 | nan |
| public_axis_step3 | 0.636645 | 0.643404 | 0.622511 | 0.640767 | 0.631639 | 0.643404 | 0.058370 | 0.625936 | nan |
| anchor | 0.636816 | 0.637980 | 0.625929 | 0.642288 | 0.634109 | 0.642288 | 0.000000 | 0.631654 | 0.631187 |

## Target Diagnostics

| recipe | target | loss | delta_vs_anchor | mean_abs_move |
|---|---|---|---|---|
| anchor | Q1 | 0.682063 | 0.000000 | 0.000000 |
| anchor | Q2 | 0.685906 | 0.000000 | 0.000000 |
| anchor | Q3 | 0.678874 | 0.000000 | 0.000000 |
| anchor | S1 | 0.581357 | 0.000000 | 0.000000 |
| anchor | S2 | 0.602809 | 0.000000 | 0.000000 |
| anchor | S3 | 0.567907 | 0.000000 | 0.000000 |
| anchor | S4 | 0.648849 | 0.000000 | 0.000000 |
| catboost_safe | Q1 | 0.680687 | -0.001377 | 0.008433 |
| catboost_safe | Q2 | 0.684279 | -0.001627 | 0.022463 |
| catboost_safe | Q3 | 0.668714 | -0.010161 | 0.045388 |
| catboost_safe | S1 | 0.565748 | -0.015609 | 0.037241 |
| catboost_safe | S2 | 0.603138 | 0.000329 | 0.037652 |
| catboost_safe | S3 | 0.568586 | 0.000679 | 0.017415 |
| catboost_safe | S4 | 0.647340 | -0.001510 | 0.018983 |
| consensus | Q1 | 0.680258 | -0.001806 | 0.006955 |
| consensus | Q2 | 0.683366 | -0.002540 | 0.015584 |
| consensus | Q3 | 0.670438 | -0.008436 | 0.093922 |
| consensus | S1 | 0.557909 | -0.023448 | 0.079383 |
| consensus | S2 | 0.609077 | 0.006268 | 0.070190 |
| consensus | S3 | 0.568947 | 0.001040 | 0.012898 |
| consensus | S4 | 0.648999 | 0.000150 | 0.028327 |
| public_axis_step2 | Q1 | 0.681079 | -0.000984 | 0.006529 |
| public_axis_step2 | Q2 | 0.683592 | -0.002314 | 0.009971 |
| public_axis_step2 | Q3 | 0.675344 | -0.003530 | 0.111052 |
| public_axis_step2 | S1 | 0.558511 | -0.022847 | 0.092698 |
| public_axis_step2 | S2 | 0.613207 | 0.010398 | 0.081606 |
| public_axis_step2 | S3 | 0.570033 | 0.002126 | 0.015126 |
| public_axis_step2 | S4 | 0.649306 | 0.000457 | 0.033246 |
| public_axis_step3 | Q1 | 0.680766 | -0.001297 | 0.009409 |
| public_axis_step3 | Q2 | 0.683451 | -0.002455 | 0.011236 |
| public_axis_step3 | Q3 | 0.682900 | 0.004026 | 0.130718 |
| public_axis_step3 | S1 | 0.560247 | -0.021110 | 0.103904 |
| public_axis_step3 | S2 | 0.619211 | 0.016402 | 0.093479 |
| public_axis_step3 | S3 | 0.571439 | 0.003532 | 0.021956 |
| public_axis_step3 | S4 | 0.650352 | 0.001502 | 0.037887 |
| rowgate | Q1 | 0.680258 | -0.001806 | 0.006955 |
| rowgate | Q2 | 0.683366 | -0.002540 | 0.015584 |
| rowgate | Q3 | 0.671195 | -0.007680 | 0.096899 |
| rowgate | S1 | 0.557923 | -0.023434 | 0.080913 |
| rowgate | S2 | 0.611723 | 0.008914 | 0.073237 |
| rowgate | S3 | 0.568947 | 0.001040 | 0.012898 |
| rowgate | S4 | 0.649792 | 0.000942 | 0.030661 |
| sleep_state | Q1 | 0.680258 | -0.001806 | 0.006955 |
| sleep_state | Q2 | 0.683366 | -0.002540 | 0.015584 |
| sleep_state | Q3 | 0.668685 | -0.010189 | 0.083869 |
| sleep_state | S1 | 0.558211 | -0.023147 | 0.071961 |
| sleep_state | S2 | 0.606270 | 0.003460 | 0.062959 |
| sleep_state | S3 | 0.568947 | 0.001040 | 0.012898 |
| sleep_state | S4 | 0.648600 | -0.000250 | 0.024702 |

## Decision Rule

- Trust only rank/order among `anchor`, `catboost_safe`, and `sleep_state`; those are public-anchored.
- Treat `public_axis_step2`, `rowgate`, `consensus`, and `public_axis_step3` as extrapolations. They need movement in the same Q3/S1/S2 axis without turning Q1/Q2/S3 into the failed imported-v81 shape.
- A candidate is valid for the 0.57 attempt only if it improves calibrated estimate versus `sleep_state` and does not make `worst_family` worse than `sleep_state` by more than 0.015.