# Binary Anchor Loss Geometry Audit

Question: do known-public anchor loss decompositions reject the E30 adverse mixmin/inverse7 worlds?

## Method

- For each E30 binary world, compute per-target log-loss deltas of every known public anchor versus A2C8.
- Score whether each known public-worse anchor's loss delta is aligned with its moved target axes, and whether total public delta requires large target-level cancellation.
- Lower `anchor_energy` means less cancellation and better sign/movement alignment with known public anchors.

## Candidate Support By Anchor Geometry Band

| band | role | worlds | better_rate | min_delta | median_delta | max_delta | median_anchor_energy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | mixmin_0c916 | 29 | 0.931034 | -0.01018 | -0.000806675 | 0.00877411 | -0.189324 |
| all | inverse7blend_1040 | 29 | 0.896552 | -0.00304302 | -0.000158965 | 0.00278211 | -0.189324 |
| all | pair_sensor_1bb | 29 | 0.413793 | -0.00370497 | 0.000123341 | 0.00233289 | -0.189324 |
| all | pair_sensor_1bb_s0p65 | 29 | 0.413793 | -0.00243973 | 4.86761e-05 | 0.00148488 | -0.189324 |
| all | pair_sensor_6b | 29 | 0.37931 | -0.00440408 | 0.000170019 | 0.00281774 | -0.189324 |
| random_plus_fit | mixmin_0c916 | 19 | 1 | -0.00127493 | -0.000804652 | -0.000315338 | -0.911549 |
| random_plus_fit | inverse7blend_1040 | 19 | 0.947368 | -0.000362361 | -0.000128254 | 6.01494e-05 | -0.911549 |
| random_plus_fit | pair_sensor_1bb | 19 | 0.421053 | -0.000922232 | 0.000103122 | 0.000490769 | -0.911549 |
| random_plus_fit | pair_sensor_1bb_s0p65 | 19 | 0.421053 | -0.000630946 | 3.5534e-05 | 0.000287504 | -0.911549 |
| random_plus_fit | pair_sensor_6b | 19 | 0.368421 | -0.00109371 | 0.000133448 | 0.000614961 | -0.911549 |
| low_anchor_energy_half | mixmin_0c916 | 15 | 1 | -0.00127493 | -0.000806675 | -0.000537096 | -1.11728 |
| low_anchor_energy_half | inverse7blend_1040 | 15 | 1 | -0.000362361 | -0.000190932 | -2.46186e-05 | -1.11728 |
| low_anchor_energy_half | pair_sensor_1bb | 15 | 0.4 | -0.000922232 | 0.00015651 | 0.00233289 | -1.11728 |
| low_anchor_energy_half | pair_sensor_1bb_s0p65 | 15 | 0.4 | -0.000630946 | 7.02361e-05 | 0.00148488 | -1.11728 |
| low_anchor_energy_half | pair_sensor_6b | 15 | 0.333333 | -0.00109371 | 0.000214136 | 0.00281774 | -1.11728 |
| low_anchor_energy_quarter | mixmin_0c916 | 7 | 1 | -0.00127493 | -0.00096212 | -0.000537096 | -2.0751 |
| low_anchor_energy_quarter | inverse7blend_1040 | 7 | 1 | -0.000344812 | -0.000152013 | -3.52737e-05 | -2.0751 |
| low_anchor_energy_quarter | pair_sensor_1bb | 7 | 0.571429 | -0.000922232 | -5.00174e-05 | 0.000490769 | -2.0751 |
| low_anchor_energy_quarter | pair_sensor_1bb_s0p65 | 7 | 0.571429 | -0.000630946 | -6.40065e-05 | 0.000287504 | -2.0751 |
| low_anchor_energy_quarter | pair_sensor_6b | 7 | 0.428571 | -0.00109371 | 9.90933e-06 | 0.000614961 | -2.0751 |
| low_anchor_energy_random_plus_fit | mixmin_0c916 | 12 | 1 | -0.00127493 | -0.00103249 | -0.000537096 | -1.56441 |
| low_anchor_energy_random_plus_fit | inverse7blend_1040 | 12 | 1 | -0.000362361 | -0.000174948 | -2.46186e-05 | -1.56441 |
| low_anchor_energy_random_plus_fit | pair_sensor_1bb | 12 | 0.5 | -0.000922232 | 4.44541e-05 | 0.000490769 | -1.56441 |
| low_anchor_energy_random_plus_fit | pair_sensor_1bb_s0p65 | 12 | 0.5 | -0.000630946 | -2.60011e-06 | 0.000287504 | -1.56441 |
| low_anchor_energy_random_plus_fit | pair_sensor_6b | 12 | 0.416667 | -0.00109371 | 7.02202e-05 | 0.000614961 | -1.56441 |

## Lowest Anchor-Energy Worlds

| objective | source_role | world_id | anchor_energy | anchor_energy_rank | anchor_cancellation_mean | anchor_positive_share_mean | anchor_movement_loss_corr_mean | mixmin_0c916 | inverse7blend_1040 | pair_sensor_1bb |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| frontier_random_17 | random | 3d226cd68855 | -2.71827 | 1 | 2.15274 | 0.715252 | 0.45231 | -0.000630918 | -3.52737e-05 | -5.00174e-05 |
| frontier_random_07 | random | 8bbc350246a3 | -2.33461 | 2 | 3.07175 | 0.730752 | 0.592817 | -0.000602114 | -0.000128254 | -0.000324824 |
| frontier_random_06 | random | cb089e691932 | -2.10379 | 3 | 2.83127 | 0.689554 | 0.634948 | -0.000537096 | -0.000192773 | -0.000922232 |
| frontier_random_09 | random | 4f73f92bbcb0 | -2.0751 | 4 | 2.76088 | 0.718182 | 0.504157 | -0.00096212 | -0.00022214 | 0.000181205 |
| frontier_random_10 | random | 867fc3d20831 | -1.92637 | 5 | 2.97055 | 0.742015 | 0.450714 | -0.00114376 | -0.000152013 | 0.000246767 |
| frontier_random_08 | random | dde8304218cd | -1.60104 | 6 | 2.92374 | 0.664199 | 0.667034 | -0.00110285 | -9.94904e-05 | 0.000490769 |
| frontier_random_16 | random | 7200ad876873 | -1.52778 | 7 | 2.50706 | 0.692478 | 0.429968 | -0.00127493 | -0.000344812 | -0.000236174 |
| frontier_random_05 | random | a416a1fce3ce | -1.11728 | 8 | 2.99161 | 0.68599 | 0.521629 | -0.000804652 | -0.000190932 | 0.00015651 |
| frontier_random_00 | random | a8dc30df1cbc | -1.01174 | 9 | 2.66203 | 0.65752 | 0.513116 | -0.00111399 | -0.000227082 | 0.000219718 |
| frontier_random_12 | random | 8254bf184843 | -0.911549 | 10 | 2.5974 | 0.653171 | 0.49299 | -0.00116104 | -0.000362361 | 0.000123341 |

## Highest Anchor-Energy Worlds

| objective | source_role | world_id | anchor_energy | anchor_energy_rank | anchor_cancellation_mean | anchor_positive_share_mean | anchor_movement_loss_corr_mean | mixmin_0c916 | inverse7blend_1040 | pair_sensor_1bb |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inverse7blend_1040_min | inverse7blend_1040 | e5b3428f2f46 | 6.83133 | 29 | 6.67765 | 0.637286 | 0.371983 | -0.00728194 | -0.00304302 | 0.00022492 |
| inverse7blend_1040_max | inverse7blend_1040 | 3d35ba77dad0 | 6.66712 | 28 | 8.19238 | 0.663087 | 0.316836 | 0.00433237 | 0.00278211 | 0.000156507 |
| pair_sensor_6b_min | pair_sensor_6b | d42d7be6d14c | 4.08448 | 27 | 5.18518 | 0.629001 | 0.453249 | -0.00134049 | -0.000377617 | -0.00370497 |
| mixmin_0c916_max | mixmin_0c916 | 5528fcf0b22c | 3.93699 | 26 | 4.60536 | 0.619355 | 0.347559 | 0.00877411 | 0.00158685 | 0.000501442 |
| frontier_random_03 | random | 4f54d6754a50 | 3.52212 | 25 | 3.65522 | 0.535862 | 0.454096 | -0.000740159 | -2.74541e-05 | -0.000240021 |
| pair_sensor_1bb_s0p65_min | pair_sensor_1bb_s0p65 | 154255b46d2b | 3.2461 | 24 | 4.58812 | 0.629001 | 0.427962 | -0.00125193 | -0.000387935 | -0.00370497 |
| frontier_random_02 | random | e6bfbdfa87c1 | 2.49321 | 23 | 4.03817 | 0.575651 | 0.597871 | -0.000791158 | -3.53472e-05 | 0.000443174 |
| pair_sensor_1bb_min | pair_sensor_1bb | 15e0682b980e | 2.37159 | 22 | 4.36092 | 0.650417 | 0.436636 | -0.00137289 | -0.000463388 | -0.00370497 |
| frontier_random_14 | random | fb117db632d8 | 1.7229 | 21 | 3.70727 | 0.605251 | 0.528273 | -0.000532597 | -0.000112723 | 8.99522e-05 |
| mixmin_0c916_min | mixmin_0c916 | 9ae600f0db62 | 1.53426 | 20 | 4.54801 | 0.686803 | 0.502996 | -0.01018 | -0.00185962 | -0.000122416 |

## Adverse Mixmin Worlds

- mixmin adverse worlds: `2`.
| objective | source_role | world_id | anchor_energy | anchor_energy_rank | anchor_cancellation_mean | anchor_positive_share_mean | anchor_movement_loss_corr_mean | mixmin_0c916 | inverse7blend_1040 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_0c916_max | mixmin_0c916 | 5528fcf0b22c | 3.93699 | 26 | 4.60536 | 0.619355 | 0.347559 | 0.00877411 | 0.00158685 |
| inverse7blend_1040_max | inverse7blend_1040 | 3d35ba77dad0 | 6.66712 | 28 | 8.19238 | 0.663087 | 0.316836 | 0.00433237 | 0.00278211 |

## Decision

- worlds scored: `29`.
- low-anchor-energy-half mixmin better_rate: `1.000000`.
- Adverse mixmin worlds have worse anchor geometry; this strengthens mixmin but remains a diagnostic gate.
- This is not a public-LB optimizer; it is a stress test for hidden-world plausibility.
