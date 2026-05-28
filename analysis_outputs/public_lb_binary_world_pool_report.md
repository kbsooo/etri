# Public LB Binary World Pool

Question: if binary hidden-label worlds can fit known public anchors, do multiple binary incumbents agree on candidate signs?

## World Fit Summary

| objective | source_role | world_id | duplicate_world | max_abs_residual | max_residual_over_frontier_raw05_gap | sum_abs_residual | positive_cell_count | frontier_scale_fit | elapsed_sec | message |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fit | slack | d21746c7211f | False | 0.000157515 | 1.81081 | 0.000578596 | 980 | False | 7.17451 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| pair_sensor_1bb_min | pair_sensor_1bb | 1ea3f588da8e | False | 0.000195904 | 2.25212 | 0.000692968 | 1167 | False | 7.02869 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| pair_sensor_1bb_max | pair_sensor_1bb | 68aed6b78e65 | False | 0.000102213 | 1.17505 | 0.000351428 | 1149 | False | 7.04765 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| pair_sensor_1bb_s0p65_min | pair_sensor_1bb_s0p65 | e2f4462eae7e | False | 0.000165821 | 1.90629 | 0.000821469 | 957 | False | 7.0711 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| pair_sensor_1bb_s0p65_max | pair_sensor_1bb_s0p65 | 02aa0b37dd00 | False | 0.000117363 | 1.34922 | 0.00026435 | 950 | False | 7.01934 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| pair_sensor_6b_min | pair_sensor_6b | 970797f6aadc | False | 0.000174271 | 2.00343 | 0.00065728 | 959 | False | 7.01331 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| pair_sensor_6b_max | pair_sensor_6b | 28647a286205 | False | 0.000253788 | 2.91757 | 0.000856617 | 960 | False | 7.01602 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| mixmin_0c916_min | mixmin_0c916 | f152c42bfa5b | False | 0.000179407 | 2.06248 | 0.000518836 | 1044 | False | 7.02146 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| mixmin_0c916_max | mixmin_0c916 | 9924544c710d | False | 0.000114628 | 1.31778 | 0.000299371 | 1055 | False | 7.02024 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| inverse7blend_1040_min | inverse7blend_1040 | 56340f4d15b9 | False | 0.00013675 | 1.57209 | 0.000240377 | 1037 | False | 7.03255 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| inverse7blend_1040_max | inverse7blend_1040 | 635dfb658d30 | False | 0.000339294 | 3.90055 | 0.000652666 | 1069 | False | 7.02637 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| random_world_0 | random | 73acfc9bcb30 | False | 0.000139467 | 1.60333 | 0.000268215 | 1086 | False | 7.02784 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| random_world_1 | random | 8ab10ff0a536 | False | 9.0427e-05 | 1.03956 | 0.000214295 | 965 | False | 7.026 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| random_world_2 | random | 4ed0a2623236 | False | 0.000109783 | 1.26208 | 0.000312658 | 1111 | False | 7.01706 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| random_world_3 | random | a6a24807e989 | False | 8.4491e-05 | 0.971315 | 0.000311826 | 1057 | True | 7.01145 | Time limit reached. (HiGHS Status 13: Time limit reached) |

## Candidate Delta Summary

| role | worlds | better_rate | min_delta | median_delta | max_delta | frontier_worlds |
| --- | --- | --- | --- | --- | --- | --- |
| mixmin_0c916 | 15 | 0.866667 | -0.0106886 | -0.00101263 | 0.0087649 | 1 |
| inverse7blend_1040 | 15 | 0.733333 | -0.0030288 | -0.000212969 | 0.00276219 | 1 |
| pair_sensor_1bb_s0p65 | 15 | 0.333333 | -0.00243973 | 0.000114703 | 0.00148488 | 1 |
| pair_sensor_1bb | 15 | 0.266667 | -0.00370497 | 0.00022492 | 0.00233289 | 1 |
| pair_sensor_6b | 15 | 0.266667 | -0.00440408 | 0.000248525 | 0.00281774 | 1 |

## Frontier-Scale Worlds Only

| role | frontier_worlds | frontier_better_rate | frontier_min_delta | frontier_median_delta | frontier_max_delta |
| --- | --- | --- | --- | --- | --- |
| mixmin_0c916 | 1 | 1 | -0.00107366 | -0.00107366 | -0.00107366 |
| inverse7blend_1040 | 1 | 1 | -0.000277011 | -0.000277011 | -0.000277011 |
| pair_sensor_1bb_s0p65 | 1 | 0 | 0.000313073 | 0.000313073 | 0.000313073 |
| pair_sensor_1bb | 1 | 0 | 0.000530105 | 0.000530105 | 0.000530105 |
| pair_sensor_6b | 1 | 0 | 0.00061523 | 0.00061523 | 0.00061523 |

## Decision

- objectives attempted: `15`.
- incumbent worlds: `15`.
- unique worlds: `15`.
- frontier-scale worlds: `1`.
- frontier-stable roles: `5`; stable-improving roles: `2`.
- Some candidates are consistently better inside this binary-world pool; treat as a hypothesis-specific signal requiring selector stress.
- This pool is a diagnostic sample, not proof of the exact public set; all worlds are solver incumbents under time limits.
