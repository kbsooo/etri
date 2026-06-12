# HS-JEPA Diagnostic Adapter: Subject-Balanced Route Conservation Decoder

## 한 줄 요약

`Target-Route Conservation Decoder`가 OOF에서는 강했지만 subject-tail shortcut일 수 있다.
이번 실험은 같은 HS-JEPA listener-conditioned route law를 subject-balanced objective로 다시 고른다.

```text
masked world-state residual/energy
  -> target listener interaction support
  -> subject-balanced route conservation
  -> anchor-free correction sensor
```

## 빠른 판정: 이것은 HS-JEPA인가?

**HS-JEPA core 자체는 아니다.**
정확한 위치는 **HS-JEPA competition adapter + LeJEPA-style diagnostic**이다.

```text
HS-JEPA core
  = visible human-life context -> hidden world-state representation

이 문서의 역할
  = hidden world-state route law가 subject-tail shortcut인지 stress한다.
```

## 사용하지 않은 정보

- public LB ledger: `False`
- prior submission probability: `False`
- proprietary embedding API: `False`

## Verdict

- verdict: `subject_balanced_route_conservation_positive`
- OOF selected cells: `166`
- OOF selected gain sum: `10.122799`
- OOF selected positive gain rate: `0.740964`
- listener global gain reference: `6.192500`
- route conservation gain reference: `15.595885`
- gain over listener global reference: `3.930299`
- gain retained vs route conservation reference: `0.649069`
- accepted targets: `['Q2', 'Q3', 'S3', 'S4']`
- held targets: `['Q1', 'S1', 'S2']`
- released test cells: `96`

## Selected Subject-Balanced Routes

| target | accepted | policy | decoder_action | fraction | selected_cells | selected_gain_sum | subject_selected_positive_gain_rate | subject_positive_count | subject_negative_count | subject_active_count | subject_min_gain | gain_lift_vs_null | subject_balance_score | accept_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | False | hold | none | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0.000000 | 0.000000 | -1.200000 | no_policy_passed_subject_balance_gate |
| Q2 | True | release_high_decisive | raw_memory_release | 0.180000 | 67 | 2.734587 | 0.626866 | 7 | 0 | 7 | 0.000000 | 2.312575 | 6.337799 | positive_gain_subject_balance_target_shuffle_lift |
| Q3 | True | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.727263 | 0.857143 | 3 | 0 | 3 | 0.000000 | 0.686533 | 1.477549 | positive_gain_subject_balance_target_shuffle_lift |
| S1 | False | hold | none | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0.000000 | 0.000000 | -1.200000 | no_policy_passed_subject_balance_gate |
| S2 | False | hold | none | 0.000000 | 0 | 0.000000 | NA | 0 | 0 | 0 | 0.000000 | 0.000000 | -1.200000 | no_policy_passed_subject_balance_gate |
| S3 | True | inverse_low_decisive | inverse_toxic_memory | 0.100000 | 35 | 2.953439 | 0.942857 | 5 | 2 | 7 | -0.433514 | 3.573659 | 4.134112 | positive_gain_subject_balance_target_shuffle_lift |
| S4 | True | release_high_decisive | raw_memory_release | 0.180000 | 57 | 3.707510 | 0.736842 | 8 | 1 | 9 | -0.375628 | 3.911611 | 7.502094 | positive_gain_subject_balance_target_shuffle_lift |

## OOF Target Contribution

| target | selected_cells | selected_gain_sum | selected_mean_gain | selected_positive_gain_rate | active_subjects |
| --- | --- | --- | --- | --- | --- |
| Q2 | 67 | 2.734587 | 0.040815 | 0.626866 | 7 |
| Q3 | 7 | 0.727263 | 0.103895 | 0.857143 | 3 |
| S3 | 35 | 2.953439 | 0.084384 | 0.942857 | 7 |
| S4 | 57 | 3.707510 | 0.065044 | 0.736842 | 9 |

## Subject Stress Summary

| subject_id | selected_cells | gain_sum | positive_targets | negative_targets |
| --- | --- | --- | --- | --- |
| id01 | 67 | 2.891576 | 2 | 0 |
| id02 | 12 | 1.436526 | 1 | 0 |
| id03 | 3 | 0.527612 | 2 | 0 |
| id04 | 10 | 0.203427 | 2 | 0 |
| id05 | 16 | 0.975038 | 2 | 0 |
| id06 | 13 | 1.109605 | 3 | 0 |
| id07 | 22 | 1.202522 | 4 | 0 |
| id08 | 9 | 1.198587 | 3 | 1 |
| id09 | 6 | 0.430053 | 2 | 0 |
| id10 | 8 | 0.147854 | 2 | 2 |

## Top Subject-Balanced Policy Candidates

| target | policy | decoder_action | fraction | selected_cells | selected_gain_sum | subject_selected_positive_gain_rate | subject_positive_count | subject_negative_count | subject_min_gain | gain_lift_vs_null | subject_balance_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | release_high_decisive | raw_memory_release | 0.180000 | 57 | 3.707510 | 0.736842 | 8 | 1 | -0.375628 | 3.911611 | 7.502094 |
| S4 | release_high_all | raw_memory_release | 0.180000 | 81 | 4.424903 | 0.753086 | 7 | 2 | -0.544303 | 4.274613 | 6.942947 |
| S4 | release_high_all | raw_memory_release | 0.140000 | 63 | 4.057420 | 0.777778 | 7 | 2 | -0.261429 | 3.848140 | 6.582193 |
| Q2 | release_high_decisive | raw_memory_release | 0.180000 | 67 | 2.734587 | 0.626866 | 7 | 0 | 0.000000 | 2.312575 | 6.337799 |
| Q2 | release_high_all | raw_memory_release | 0.250000 | 112 | 4.590855 | 0.633929 | 5 | 3 | -0.212215 | 4.855424 | 5.599082 |
| S4 | release_high_all | raw_memory_release | 0.250000 | 112 | 3.381716 | 0.669643 | 7 | 2 | -0.385298 | 2.965569 | 5.523753 |
| S4 | release_high_decisive | raw_memory_release | 0.140000 | 45 | 3.097754 | 0.755556 | 7 | 2 | -0.375628 | 3.132875 | 5.299678 |
| Q2 | release_high_all | raw_memory_release | 0.180000 | 81 | 3.176745 | 0.617284 | 6 | 2 | -0.168896 | 3.795196 | 5.163726 |
| Q2 | release_high_decisive | raw_memory_release | 0.250000 | 93 | 4.212391 | 0.612903 | 5 | 3 | -0.212215 | 4.650244 | 5.141396 |
| S4 | release_high_decisive | raw_memory_release | 0.250000 | 80 | 2.762745 | 0.637500 | 7 | 2 | -0.499497 | 2.990713 | 4.841957 |
| S4 | release_high_all | raw_memory_release | 0.100000 | 45 | 3.010721 | 0.755556 | 6 | 2 | -0.321562 | 2.952226 | 4.611063 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.100000 | 35 | 2.953439 | 0.942857 | 5 | 2 | -0.433514 | 3.573659 | 4.134112 |
| Q2 | release_high_all | raw_memory_release | 0.140000 | 63 | 1.983623 | 0.634921 | 6 | 1 | -0.040401 | 1.497816 | 3.973618 |
| S4 | release_high_all | raw_memory_release | 0.040000 | 18 | 1.343099 | 0.777778 | 7 | 1 | -0.243270 | 1.334137 | 3.726269 |
| S4 | release_high_all | raw_memory_release | 0.060000 | 27 | 2.254243 | 0.814815 | 6 | 2 | -0.321562 | 2.226155 | 3.600460 |
| S4 | release_high_decisive | raw_memory_release | 0.040000 | 13 | 1.178229 | 0.769231 | 7 | 1 | -0.243270 | 1.343621 | 3.572323 |
| S4 | release_high_all | raw_memory_release | 0.080000 | 36 | 2.226643 | 0.750000 | 6 | 2 | -0.321562 | 2.180741 | 3.556966 |
| S4 | release_high_decisive | raw_memory_release | 0.100000 | 32 | 2.232549 | 0.750000 | 6 | 2 | -0.375628 | 2.200187 | 3.537238 |
| S4 | release_high_decisive | raw_memory_release | 0.080000 | 25 | 2.141701 | 0.800000 | 6 | 2 | -0.375628 | 2.325276 | 3.490171 |
| S4 | release_high_decisive | raw_memory_release | 0.020000 | 6 | 1.338938 | 1.000000 | 5 | 0 | 0.000000 | 1.340953 | 3.458272 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.080000 | 28 | 2.278917 | 0.928571 | 5 | 2 | -0.433514 | 2.895874 | 3.222365 |
| S4 | release_high_decisive | raw_memory_release | 0.060000 | 19 | 1.816096 | 0.789474 | 6 | 2 | -0.243270 | 1.688216 | 3.021010 |
| S3 | release_high_decisive | raw_memory_release | 0.060000 | 21 | 1.591564 | 0.857143 | 4 | 1 | -0.112817 | 2.454832 | 2.733065 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.060000 | 21 | 1.604477 | 0.904762 | 5 | 2 | -0.433514 | 1.987897 | 2.230133 |
| Q2 | release_high_decisive | raw_memory_release | 0.140000 | 52 | 1.494031 | 0.596154 | 4 | 1 | -0.227971 | 1.334495 | 2.174321 |
| S3 | release_high_all | raw_memory_release | 0.060000 | 27 | 1.406791 | 0.740741 | 4 | 2 | -0.211998 | 2.698298 | 1.843997 |
| Q3 | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.727263 | 0.857143 | 3 | 0 | 0.000000 | 0.686533 | 1.477549 |
| S4 | release_high_all | raw_memory_release | 0.020000 | 9 | 0.782218 | 0.777778 | 4 | 1 | -0.056190 | 0.858977 | 1.399147 |
| S3 | release_high_decisive | raw_memory_release | 0.040000 | 14 | 0.708755 | 0.785714 | 4 | 1 | -0.371663 | 1.482444 | 1.354613 |
| S3 | release_high_all | raw_memory_release | 0.040000 | 18 | 0.691333 | 0.722222 | 4 | 1 | -0.470844 | 1.451903 | 1.266992 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.040000 | 14 | 0.929855 | 0.857143 | 5 | 2 | -0.433514 | 0.827556 | 1.149392 |
| S3 | release_high_decisive | raw_memory_release | 0.020000 | 7 | 0.524784 | 0.714286 | 2 | 0 | 0.000000 | 0.949831 | 0.797224 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.140000 | 49 | 1.452466 | 0.816327 | 5 | 4 | -0.644395 | 2.447913 | 0.533857 |
| S3 | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.255289 | 0.714286 | 5 | 2 | -0.433514 | 0.306025 | 0.292289 |
| Q3 | release_high_all | raw_memory_release | 0.100000 | 45 | 0.496588 | 0.666667 | 4 | 3 | -0.225822 | 2.291275 | 0.032965 |
| S4 | inverse_low_decisive | inverse_toxic_memory | 0.140000 | 45 | -0.136128 | 0.622222 | 5 | 2 | -1.324237 | 1.668862 | -0.156569 |
| Q3 | release_high_decisive | raw_memory_release | 0.100000 | 35 | 0.373324 | 0.657143 | 4 | 3 | -0.225822 | 1.995735 | -0.219481 |
| Q3 | release_high_decisive | raw_memory_release | 0.080000 | 28 | 0.461770 | 0.678571 | 4 | 3 | -0.225822 | 1.630751 | -0.240870 |
| S1 | inverse_low_decisive | inverse_toxic_memory | 0.020000 | 7 | 0.128822 | 0.714286 | 1 | 0 | 0.000000 | 0.391156 | -0.364274 |
| Q3 | release_high_all | raw_memory_release | 0.060000 | 27 | 0.391209 | 0.666667 | 4 | 3 | -0.225822 | 1.298181 | -0.443706 |

## Anchor-Free Candidate

- candidate: `submission_hsjepa_subject_balanced_route_conservation_anchor_free_74ca928e_uploadsafe.csv`
- validation: `{'valid': True, 'problems': [], 'rows': 250, 'probability_min': 0.3002330190252523, 'probability_max': 0.9046971565053001}`

## 해석

좋은 결과:

```text
subject-balanced route selection이 listener-global reference를 넘고,
route-conservation gain의 의미 있는 부분을 보존하면,
HS-JEPA route law가 단순 subject-tail shortcut만은 아니라는 증거가 된다.
```

나쁜 결과:

```text
subject balance를 걸자 gain이 대부분 사라지면,
target-route conservation은 OOF adapter로는 유효하지만 subject-general law는 아니다.
그 경우 다음 논문 주장은 core representation + diagnostic necessity로 낮춰야 한다.
```

현재 결론:

```text
HS-JEPA core residual/energy는 target listener route action을 설명한다.
하지만 release-grade architecture가 되려면 subject-balanced route responsibility가 필요하다.
```
