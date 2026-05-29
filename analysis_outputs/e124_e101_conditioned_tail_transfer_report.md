# E124 E101-conditioned tail transfer audit

## Question

E99 explained E72 failure and E95 success with a two-term world:

`public_delta = alpha * local_margin + lambda * E72_hard_tail_delta`.

E101 is now a third public observation. The question is whether this same world
family also predicts E101's small loss, and whether conditioning on E101 changes
the next public-sensor queue.

Observed public deltas versus mixmin:

- E72: `0.0001011367`
- E95: `-0.0000153107`
- E101: `-0.0000062745`

## Filter Health

| filter | n_scenarios | alpha_median | lambda_median | e101_residual_mean | e101_abs_residual_median | e101_order_match_rate | winner_live_mode | winner_future_mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| broad_plausible | 3452 | 3.310469910 | 1.345191741 | -0.000025241 | 0.000023324 | 0.016512167 | e95 | e89 |
| e101_order_match | 57 | 0.791985050 | 1.082582445 | -0.000008444 | 0.000008570 | 1.000000000 | e95 | e85 |
| e101_close_pm10e6 | 121 | 0.839337993 | 1.087520066 | -0.000009038 | 0.000009135 | 0.471074380 | e95 | e89 |
| e101_sensor_plausible | 57 | 0.791985050 | 1.082582445 | -0.000008444 | 0.000008570 | 1.000000000 | e95 | e85 |

In broad-plausible E99 worlds, mean predicted E101 delta is `-0.000031516`
and p95 is `-0.000016875` versus actual `-0.000006275`.

E101-plausible scenario count: `57`.

## Candidate Summary

| filter | candidate | n_scenarios | mean_pred_delta | p90_pred_delta | p95_pred_delta | mean_vs_e95 | p95_vs_e95 | beat_e95_rate | win_rate_live | win_rate_future |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| broad_plausible | e85 | 3452 | -0.000005652 | 0.000001578 | 0.000002961 | 0.000009659 | 0.000018271 | 0.031865585 | 0.002607184 | 0.059965238 |
| broad_plausible | e86 | 3452 | 0.000005034 | 0.000026676 | 0.000031296 | 0.000020345 | 0.000046606 | 0.000289687 | 0.000289687 | 0.040266512 |
| broad_plausible | noq2 | 3452 | -0.000000021 | 0.000013658 | 0.000016182 | 0.000015290 | 0.000031492 | 0.023174971 | 0.006083430 | 0.022885284 |
| broad_plausible | e90 | 3452 | -0.000001938 | 0.000009905 | 0.000015934 | 0.000013372 | 0.000031244 | 0.002607184 | 0.001738123 | 0.099362688 |
| broad_plausible | e89 | 3452 | -0.000011477 | -0.000004841 | -0.000002759 | 0.000003833 | 0.000012552 | 0.195828505 | 0.188876014 | 0.777520278 |
| broad_plausible | e95 | 3452 | -0.000015311 | -0.000015311 | -0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 0.800405562 |  |
| broad_plausible | e101 | 3452 | -0.000031516 | -0.000018674 | -0.000016875 | -0.000016205 | -0.000001564 | 0.983487833 |  |  |
| e101_order_match | e85 | 57 | -0.000010838 | -0.000007120 | -0.000006287 | 0.000004472 | 0.000009023 | 0.017543860 | 0.017543860 | 0.350877193 |
| e101_order_match | e86 | 57 | 0.000001219 | 0.000011414 | 0.000027739 | 0.000016530 | 0.000043050 | 0.000000000 | 0.000000000 | 0.017543860 |
| e101_order_match | noq2 | 57 | -0.000009656 | -0.000004009 | -0.000000748 | 0.000005655 | 0.000014563 | 0.035087719 | 0.017543860 | 0.315789474 |
| e101_order_match | e90 | 57 | -0.000004423 | 0.000003446 | 0.000011815 | 0.000010888 | 0.000027126 | 0.000000000 | 0.000000000 | 0.105263158 |
| e101_order_match | e89 | 57 | -0.000010140 | -0.000005158 | -0.000001883 | 0.000005171 | 0.000013427 | 0.052631579 | 0.035087719 | 0.210526316 |
| e101_order_match | e95 | 57 | -0.000015311 | -0.000015311 | -0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 0.929824561 |  |
| e101_order_match | e101 | 57 | -0.000014718 | -0.000014266 | -0.000013027 | 0.000000592 | 0.000002283 | 0.000000000 |  |  |
| e101_close_pm10e6 | e85 | 121 | -0.000011202 | -0.000007188 | -0.000006410 | 0.000004109 | 0.000008901 | 0.099173554 | 0.024793388 | 0.305785124 |
| e101_close_pm10e6 | e86 | 121 | 0.000000527 | 0.000010944 | 0.000023914 | 0.000015837 | 0.000039225 | 0.000000000 | 0.000000000 | 0.024793388 |
| e101_close_pm10e6 | noq2 | 121 | -0.000010265 | -0.000004133 | -0.000001220 | 0.000005045 | 0.000014090 | 0.123966942 | 0.082644628 | 0.280991736 |
| e101_close_pm10e6 | e90 | 121 | -0.000004566 | 0.000004513 | 0.000010557 | 0.000010745 | 0.000025867 | 0.008264463 | 0.000000000 | 0.049586777 |
| e101_close_pm10e6 | e89 | 121 | -0.000011104 | -0.000005501 | -0.000003047 | 0.000004207 | 0.000012264 | 0.173553719 | 0.090909091 | 0.338842975 |
| e101_close_pm10e6 | e95 | 121 | -0.000015311 | -0.000015311 | -0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 0.801652893 |  |
| e101_close_pm10e6 | e101 | 121 | -0.000015312 | -0.000014625 | -0.000014386 | -0.000000002 | 0.000000925 | 0.528925620 |  |  |
| e101_sensor_plausible | e85 | 57 | -0.000010838 | -0.000007120 | -0.000006287 | 0.000004472 | 0.000009023 | 0.017543860 | 0.017543860 | 0.350877193 |
| e101_sensor_plausible | e86 | 57 | 0.000001219 | 0.000011414 | 0.000027739 | 0.000016530 | 0.000043050 | 0.000000000 | 0.000000000 | 0.017543860 |
| e101_sensor_plausible | noq2 | 57 | -0.000009656 | -0.000004009 | -0.000000748 | 0.000005655 | 0.000014563 | 0.035087719 | 0.017543860 | 0.315789474 |
| e101_sensor_plausible | e90 | 57 | -0.000004423 | 0.000003446 | 0.000011815 | 0.000010888 | 0.000027126 | 0.000000000 | 0.000000000 | 0.105263158 |
| e101_sensor_plausible | e89 | 57 | -0.000010140 | -0.000005158 | -0.000001883 | 0.000005171 | 0.000013427 | 0.052631579 | 0.035087719 | 0.210526316 |
| e101_sensor_plausible | e95 | 57 | -0.000015311 | -0.000015311 | -0.000015311 | 0.000000000 | 0.000000000 | 0.000000000 | 0.929824561 |  |
| e101_sensor_plausible | e101 | 57 | -0.000014718 | -0.000014266 | -0.000013027 | 0.000000592 | 0.000002283 | 0.000000000 |  |  |

## Interpretation

- If E101-plausible scenarios are rare or empty, the E99 two-term abstraction is
  missing a boundary variable: it can explain E72/E95 but not E101.
- If many E101-plausible scenarios survive and still keep E95 best, the hard-tail
  plateau explanation strengthens.
- If a future candidate beats E95 often inside the E101-plausible subset, that
  candidate becomes the next information sensor, not because of CV but because it
  tests the residual world left after E101.

Highest beat-E95 future candidate under the E101-plausible subset is `e89` with beat-E95 rate `0.052632` and mean vs E95 `0.000005171`. Highest future winner-mode candidate is `e85` with future win rate `0.350877`.

## Decision

Do not create a submission from E124. Use it as the post-E101 validity check for
the old E99 transfer world. If the E101-plausible subset is weak, the next
experiment should leave `local + E72 hard-tail` transfer and test a different
hidden structure rather than submit E89/E85/E90/E86 by inherited pre-E101 order.
