# HS-JEPA Adapter: Target-Route Conservation Decoder

## 한 줄 요약

listener-conditioned HS-JEPA action-support는 강하지만 S1/Q1/Q3 toxic pocket을 섞었다.
이번 실험은 target route별로 release / inverse / hold 정책을 고르고,
OOF gain, subject balance, target-shuffle stress를 통과한 route만 보존했다.

```text
masked world-state residual/energy
  -> target listener interaction support score
  -> target-route conservation gate
  -> anchor-free correction sensor
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.** 정확한 위치는 **HS-JEPA competition adapter**다.

```text
HS-JEPA core
  = visible human-life context -> hidden human-state world representation

이 문서의 역할
  = hidden world representation + target listener -> route-specific action decoder
```

따라서 이 실험을 논문에서 설명할 때 핵심 주장은 `target별 top-k가 좋다`가 아니다.
핵심 주장은 HS-JEPA core가 만든 masked world-state residual/energy가
target listener와 결합될 때 row-target action의 건강성을 route별로 분해할 수 있다는 것이다.

## 왜 중요한 adapter 실험인가

이 실험은 public LB, 기존 best submission probability, public score ledger를 쓰지 않는다.
action-support target은 train label에서만 만든다.

```text
raw lifelog KNN action vs train-fold prior
  -> realized logloss gain
  -> route-wise conservation policy
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `route_conservation_decoder_positive_public_free`
- OOF selected cells: `346`
- OOF selected gain sum: `15.595885`
- OOF selected positive gain rate: `0.734104`
- listener global gain reference: `6.192500`
- gain over listener global reference: `9.403385`
- accepted targets: `['Q1', 'Q2', 'Q3', 'S1', 'S2', 'S3', 'S4']`
- held targets: `[]`
- released test cells: `197`

## Selected Target Routes

| target | target_route_family | accepted | policy | decoder_action | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | negative_subjects | gain_lift_vs_null | gain_z_vs_null | conservation_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | subjective_q_shadow | True | release_high_decisive | raw_memory_release | 0.040000 | 13 | 0.700511 | 0.615385 | 3 | 0.728065 | 0.871009 | -0.549176 | positive_gain_null_lift_subject_balance |
| Q2 | intervention_stage_bridge | True | release_high_all | raw_memory_release | 0.250000 | 112 | 4.590855 | 0.633929 | 3 | 4.855424 | 2.181553 | 4.850757 | positive_gain_null_lift_subject_balance |
| Q3 | subjective_q_shadow | True | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.727263 | 0.857143 | 0 | 0.686533 | 1.441404 | 1.650075 | positive_gain_null_lift_subject_balance |
| S1 | objective_s1_toxic_watch | True | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.128822 | 0.714286 | 0 | 0.391156 | 0.548320 | 0.712975 | positive_gain_null_lift_subject_balance |
| S2 | intervention_stage_bridge | True | release_high_decisive | raw_memory_release | 0.250000 | 91 | 2.070093 | 0.769231 | 3 | 1.909956 | 0.788479 | 1.235391 | positive_gain_null_lift_subject_balance |
| S3 | objective_tail_bridge | True | inverse_low_decisive | inverse_toxic_memory | 0.100000 | 35 | 2.953439 | 0.942857 | 2 | 3.573659 | 2.614947 | 3.719955 | positive_gain_null_lift_subject_balance |
| S4 | objective_tail_bridge | True | release_high_all | raw_memory_release | 0.180000 | 81 | 4.424903 | 0.753086 | 2 | 4.274613 | 2.604900 | 5.304810 | positive_gain_null_lift_subject_balance |

## OOF Target Contribution

| target | selected_cells | selected_gain_sum | selected_mean_gain | selected_positive_gain_rate | active_subjects |
| --- | --- | --- | --- | --- | --- |
| Q1 | 13 | 0.700511 | 0.053885 | 0.615385 | 6 |
| Q2 | 112 | 4.590855 | 0.040990 | 0.633929 | 8 |
| Q3 | 7 | 0.727263 | 0.103895 | 0.857143 | 3 |
| S1 | 7 | 0.128822 | 0.018403 | 0.714286 | 1 |
| S2 | 91 | 2.070093 | 0.022748 | 0.769231 | 8 |
| S3 | 35 | 2.953439 | 0.084384 | 0.942857 | 7 |
| S4 | 81 | 4.424903 | 0.054628 | 0.753086 | 9 |

## Top Route Policy Candidates

| target | policy | decoder_action | fraction | selected_cells | selected_gain_sum | selected_positive_gain_rate | negative_subjects | gain_lift_vs_null | gain_z_vs_null | conservation_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | release_high_all | raw_memory_release | 0.180000 | 81 | 4.424903 | 0.753086 | 2 | 4.274613 | 2.604900 | 5.304810 |
| S4 | release_high_decisive | raw_memory_release | 0.180000 | 57 | 3.707510 | 0.736842 | 1 | 3.911611 | 2.362837 | 5.071981 |
| Q2 | release_high_all | raw_memory_release | 0.250000 | 112 | 4.590855 | 0.633929 | 3 | 4.855424 | 2.181553 | 4.850757 |
| S4 | release_high_all | raw_memory_release | 0.140000 | 63 | 4.057420 | 0.777778 | 2 | 3.848140 | 2.327121 | 4.766176 |
| Q2 | release_high_decisive | raw_memory_release | 0.250000 | 93 | 4.212391 | 0.612903 | 3 | 4.650244 | 2.130581 | 4.390031 |
| Q2 | release_high_decisive | raw_memory_release | 0.180000 | 67 | 2.734587 | 0.626866 | 0 | 2.312575 | 1.112368 | 3.964266 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.100000 | 35 | 2.953439 | 0.942857 | 2 | 3.573659 | 2.614947 | 3.719955 |
| Q2 | release_high_all | raw_memory_release | 0.180000 | 81 | 3.176745 | 0.617284 | 2 | 3.795196 | 1.822958 | 3.688537 |
| S4 | release_high_all | raw_memory_release | 0.250000 | 112 | 3.381716 | 0.669643 | 2 | 2.965569 | 1.904626 | 3.687133 |
| S4 | release_high_decisive | raw_memory_release | 0.140000 | 45 | 3.097754 | 0.755556 | 2 | 3.132875 | 2.351863 | 3.585767 |
| S4 | release_high_all | raw_memory_release | 0.100000 | 45 | 3.010721 | 0.755556 | 2 | 2.952226 | 2.555255 | 3.485217 |
| S4 | release_high_decisive | raw_memory_release | 0.250000 | 80 | 2.762745 | 0.637500 | 2 | 2.990713 | 2.029830 | 3.084675 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.080000 | 28 | 2.278917 | 0.928571 | 2 | 2.895874 | 2.415329 | 2.795030 |
| S4 | release_high_decisive | raw_memory_release | 0.020000 | 6 | 1.338938 | 1.000000 | 0 | 1.340953 | 2.173728 | 2.675970 |
| S3 | release_high_decisive | raw_memory_release | 0.060000 | 21 | 1.591564 | 0.857143 | 1 | 2.454832 | 2.099691 | 2.526524 |
| S4 | release_high_all | raw_memory_release | 0.060000 | 27 | 2.254243 | 0.814815 | 2 | 2.226155 | 2.137109 | 2.456919 |
| S4 | release_high_decisive | raw_memory_release | 0.080000 | 25 | 2.141701 | 0.800000 | 2 | 2.325276 | 1.888832 | 2.317050 |
| S4 | release_high_decisive | raw_memory_release | 0.100000 | 32 | 2.232549 | 0.750000 | 2 | 2.200187 | 1.675917 | 2.302789 |
| S4 | release_high_all | raw_memory_release | 0.080000 | 36 | 2.226643 | 0.750000 | 2 | 2.180741 | 1.717330 | 2.299332 |
| Q2 | release_high_all | raw_memory_release | 0.140000 | 63 | 1.983623 | 0.634921 | 1 | 1.497816 | 0.793605 | 2.259149 |
| S4 | release_high_all | raw_memory_release | 0.040000 | 18 | 1.343099 | 0.777778 | 1 | 1.334137 | 1.644407 | 1.811110 |
| S4 | release_high_decisive | raw_memory_release | 0.060000 | 19 | 1.816096 | 0.789474 | 2 | 1.688216 | 1.851327 | 1.787563 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.060000 | 21 | 1.604477 | 0.904762 | 2 | 1.987897 | 1.699252 | 1.693078 |
| S3 | release_high_all | raw_memory_release | 0.060000 | 27 | 1.406791 | 0.740741 | 2 | 2.698298 | 1.910588 | 1.668769 |
| Q2 | release_high_decisive | raw_memory_release | 0.140000 | 52 | 1.494031 | 0.596154 | 1 | 1.334495 | 0.579738 | 1.658404 |
| Q3 | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.727263 | 0.857143 | 0 | 0.686533 | 1.441404 | 1.650075 |
| S4 | release_high_decisive | raw_memory_release | 0.040000 | 13 | 1.178229 | 0.769231 | 1 | 1.343621 | 1.525658 | 1.621062 |
| S3 | release_high_decisive | raw_memory_release | 0.020000 | 7 | 0.524784 | 0.714286 | 0 | 0.949831 | 1.208814 | 1.408639 |
| S2 | release_high_decisive | raw_memory_release | 0.250000 | 91 | 2.070093 | 0.769231 | 3 | 1.909956 | 0.788479 | 1.235391 |
| S3 | release_high_decisive | raw_memory_release | 0.040000 | 14 | 0.708755 | 0.785714 | 1 | 1.482444 | 1.495188 | 1.195383 |
| S2 | release_high_all | raw_memory_release | 0.250000 | 112 | 1.993929 | 0.741071 | 3 | 2.041213 | 0.767010 | 1.180231 |
| S3 | release_high_all | raw_memory_release | 0.040000 | 18 | 0.691333 | 0.722222 | 1 | 1.451903 | 1.159897 | 1.069994 |
| S4 | release_high_all | raw_memory_release | 0.020000 | 9 | 0.782218 | 0.777778 | 1 | 0.858977 | 1.364741 | 1.051749 |
| S1 | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.128822 | 0.714286 | 0 | 0.391156 | 0.548320 | 0.712975 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.040000 | 14 | 0.929855 | 0.857143 | 2 | 0.827556 | 1.108525 | 0.528398 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.140000 | 49 | 1.452466 | 0.816327 | 4 | 2.447913 | 1.295560 | 0.254115 |
| Q2 | release_high_all | raw_memory_release | 0.020000 | 9 | 0.341410 | 0.555556 | 1 | 0.380167 | 0.491652 | 0.181568 |
| Q2 | release_high_all | raw_memory_release | 0.100000 | 45 | 0.306844 | 0.577778 | 1 | 0.519387 | 0.292433 | 0.160036 |
| Q2 | release_high_decisive | raw_memory_release | 0.020000 | 7 | 0.323780 | 0.428571 | 1 | 0.418141 | 0.527328 | 0.118974 |
| S2 | release_high_all | raw_memory_release | 0.140000 | 63 | 1.159725 | 0.761905 | 3 | 1.116391 | 0.559934 | 0.037582 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_target_route_conservation_decoder_anchor_free_4837b6ce_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.2750377200094735, 'probability_max': 0.9476666666666669}`

이 후보는 train prior에서 시작하고, accepted target route에 대해서만 raw-memory 또는 inverse action을 적용한다.

## 해석

성공 조건:

```text
listener-conditioned global release보다 독성 target route를 줄이고,
OOF selected gain과 positive gain rate가 올라가야 한다.
```

실패 조건:

```text
route conservation이 대부분 hold로 수렴하거나,
positive route만 train OOF에 과적합되고 subject balance가 무너지면 release-grade가 아니다.
```

현재 결론:

```text
HS-JEPA core만으로는 release law가 완성되지 않는다.
하지만 core residual/energy는 target listener와 결합될 때 action-health를 강하게 설명한다.
따라서 competition adapter는 target-route conservation decoder를 가져야 한다.
```
