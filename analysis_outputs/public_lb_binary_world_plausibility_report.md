# Binary Frontier World Plausibility Audit

Question: are E30's adverse mixmin/inverse7 frontier worlds structurally implausible under train label dynamics?

## Method

- No target labels from test are used.
- Each E30 binary world is scored against train-only label geometry: target priors, subject-target priors, pairwise co-occurrence, target correlation, row-cardinality histogram, temporal flip rates, run lengths, and train/test edge continuity.
- Lower `plausibility_energy` means closer to train label dynamics under these diagnostics.

## Candidate Support By Plausibility Band

| band | role | worlds | better_rate | min_delta | median_delta | max_delta | median_energy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | mixmin_0c916 | 29 | 0.931034 | -0.01018 | -0.000806675 | 0.00877411 | -1.09446 |
| all | inverse7blend_1040 | 29 | 0.896552 | -0.00304302 | -0.000158965 | 0.00278211 | -1.09446 |
| all | pair_sensor_1bb | 29 | 0.413793 | -0.00370497 | 0.000123341 | 0.00233289 | -1.09446 |
| all | pair_sensor_1bb_s0p65 | 29 | 0.413793 | -0.00243973 | 4.86761e-05 | 0.00148488 | -1.09446 |
| all | pair_sensor_6b | 29 | 0.37931 | -0.00440408 | 0.000170019 | 0.00281774 | -1.09446 |
| random_plus_fit | mixmin_0c916 | 19 | 1 | -0.00127493 | -0.000804652 | -0.000315338 | -0.388072 |
| random_plus_fit | inverse7blend_1040 | 19 | 0.947368 | -0.000362361 | -0.000128254 | 6.01494e-05 | -0.388072 |
| random_plus_fit | pair_sensor_1bb | 19 | 0.421053 | -0.000922232 | 0.000103122 | 0.000490769 | -0.388072 |
| random_plus_fit | pair_sensor_1bb_s0p65 | 19 | 0.421053 | -0.000630946 | 3.5534e-05 | 0.000287504 | -0.388072 |
| random_plus_fit | pair_sensor_6b | 19 | 0.368421 | -0.00109371 | 0.000133448 | 0.000614961 | -0.388072 |
| low_energy_half | mixmin_0c916 | 14 | 0.857143 | -0.01018 | -0.000805664 | 0.00877411 | -3.23028 |
| low_energy_half | inverse7blend_1040 | 14 | 0.857143 | -0.00304302 | -0.000191852 | 0.00278211 | -3.23028 |
| low_energy_half | pair_sensor_1bb | 14 | 0.285714 | -0.00370497 | 0.000156509 | 0.00233289 | -3.23028 |
| low_energy_half | pair_sensor_1bb_s0p65 | 14 | 0.285714 | -0.00243973 | 7.02353e-05 | 0.00148488 | -3.23028 |
| low_energy_half | pair_sensor_6b | 14 | 0.285714 | -0.00440408 | 0.000219853 | 0.00281774 | -3.23028 |
| low_energy_quarter | mixmin_0c916 | 7 | 0.714286 | -0.01018 | -0.000765005 | 0.00877411 | -5.85415 |
| low_energy_quarter | inverse7blend_1040 | 7 | 0.714286 | -0.00304302 | -0.00014834 | 0.00278211 | -5.85415 |
| low_energy_quarter | pair_sensor_1bb | 7 | 0.142857 | -0.000122416 | 0.00015651 | 0.00185244 | -5.85415 |
| low_energy_quarter | pair_sensor_1bb_s0p65 | 7 | 0.142857 | -0.000111066 | 7.02361e-05 | 0.00117259 | -5.85415 |
| low_energy_quarter | pair_sensor_6b | 7 | 0.142857 | -0.000179568 | 0.000245738 | 0.00224221 | -5.85415 |
| low_energy_random_plus_fit | mixmin_0c916 | 6 | 1 | -0.00096212 | -0.000670874 | -0.00043625 | -2.77541 |
| low_energy_random_plus_fit | inverse7blend_1040 | 6 | 1 | -0.00022214 | -0.000151828 | -6.84005e-05 | -2.77541 |
| low_energy_random_plus_fit | pair_sensor_1bb | 6 | 0.333333 | -0.000922232 | 9.6537e-05 | 0.000181205 | -2.77541 |
| low_energy_random_plus_fit | pair_sensor_1bb_s0p65 | 6 | 0.333333 | -0.000630946 | 3.12538e-05 | 8.62878e-05 | -2.77541 |
| low_energy_random_plus_fit | pair_sensor_6b | 6 | 0.333333 | -0.00109371 | 0.000151733 | 0.000225569 | -2.77541 |
| high_energy_half | mixmin_0c916 | 15 | 1 | -0.00137289 | -0.00110285 | -0.000315338 | 1.68559 |
| high_energy_half | inverse7blend_1040 | 15 | 0.933333 | -0.000463388 | -0.000152013 | 6.01494e-05 | 1.68559 |
| high_energy_half | pair_sensor_1bb | 15 | 0.533333 | -0.00370497 | -3.44324e-05 | 0.000490769 | 1.68559 |
| high_energy_half | pair_sensor_1bb_s0p65 | 15 | 0.533333 | -0.00243973 | -5.38763e-05 | 0.000287504 | 1.68559 |
| high_energy_half | pair_sensor_6b | 15 | 0.466667 | -0.00440408 | 9.90933e-06 | 0.000614961 | 1.68559 |

## Most Plausible Worlds

| objective | source_role | world_id | plausibility_energy | plausibility_rank | mixmin_0c916 | inverse7blend_1040 | pair_sensor_1bb | pair_sensor_6b |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inverse7blend_1040_max | inverse7blend_1040 | 3d35ba77dad0 | -12.6463 | 1 | 0.00433237 | 0.00278211 | 0.000156507 | 0.000245738 |
| mixmin_0c916_max | mixmin_0c916 | 5528fcf0b22c | -10.5282 | 2 | 0.00877411 | 0.00158685 | 0.000501442 | 0.000645056 |
| mixmin_0c916_min | mixmin_0c916 | 9ae600f0db62 | -6.35028 | 3 | -0.01018 | -0.00185962 | -0.000122416 | -0.000179568 |
| inverse7blend_1040_min | inverse7blend_1040 | e5b3428f2f46 | -5.85415 | 4 | -0.00728194 | -0.00304302 | 0.00022492 | 0.000248525 |
| pair_sensor_1bb_s0p65_max | pair_sensor_1bb_s0p65 | f590efd660f5 | -5.04486 | 5 | -0.000765005 | -0.00014834 | 0.00185244 | 0.00224221 |
| frontier_box_fit | slack | c0bf242d5185 | -3.75198 | 6 | -0.00043625 | -6.84005e-05 | 0.000103122 | 0.000170019 |
| frontier_random_05 | random | a416a1fce3ce | -3.51553 | 7 | -0.000804652 | -0.000190932 | 0.00015651 | 0.000225569 |
| frontier_random_11 | random | f4ea2d44adb6 | -2.94503 | 8 | -0.000950361 | -8.93515e-05 | -9.5389e-05 | -7.93818e-05 |
| frontier_random_14 | random | fb117db632d8 | -2.60579 | 9 | -0.000532597 | -0.000112723 | 8.99522e-05 | 0.000133448 |
| frontier_random_06 | random | cb089e691932 | -2.45083 | 10 | -0.000537096 | -0.000192773 | -0.000922232 | -0.00109371 |

## Least Plausible Worlds

| objective | source_role | world_id | plausibility_energy | plausibility_rank | mixmin_0c916 | inverse7blend_1040 | pair_sensor_1bb | pair_sensor_6b |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| frontier_random_00 | random | a8dc30df1cbc | 6.59759 | 29 | -0.00111399 | -0.000227082 | 0.000219718 | 0.000267891 |
| frontier_random_17 | random | 3d226cd68855 | 6.53186 | 28 | -0.000630918 | -3.52737e-05 | -5.00174e-05 | 9.90933e-06 |
| frontier_random_16 | random | 7200ad876873 | 5.55784 | 27 | -0.00127493 | -0.000344812 | -0.000236174 | -0.000268503 |
| frontier_random_12 | random | 8254bf184843 | 4.28498 | 26 | -0.00116104 | -0.000362361 | 0.000123341 | 0.000130531 |
| frontier_random_07 | random | 8bbc350246a3 | 2.10302 | 25 | -0.000602114 | -0.000128254 | -0.000324824 | -0.000378313 |
| pair_sensor_1bb_min | pair_sensor_1bb | 15e0682b980e | 2.02818 | 24 | -0.00137289 | -0.000463388 | -0.00370497 | -0.00440408 |
| frontier_random_15 | random | 38768d53eec3 | 1.90328 | 23 | -0.000822891 | -0.000230271 | 0.0001393 | 0.00020008 |
| frontier_random_13 | random | e6e102dc8a8b | 1.68559 | 22 | -0.000315338 | 6.01494e-05 | 0.000268853 | 0.000314335 |
| frontier_random_04 | random | c70bb0a802ed | 0.300691 | 21 | -0.00120947 | -0.000158965 | -3.44324e-05 | -3.73536e-06 |
| frontier_random_10 | random | 867fc3d20831 | -0.0578097 | 20 | -0.00114376 | -0.000152013 | 0.000246767 | 0.000290006 |

## Adverse Worlds

- mixmin adverse worlds: `2`.
- inverse7 adverse worlds: `3`.

### Mixmin Adverse Worlds

| objective | source_role | world_id | plausibility_energy | plausibility_rank | target_prior_mae | subject_target_mae | pair_joint_mae | flip_subject_mae | mixmin_0c916 | inverse7blend_1040 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_0c916_max | mixmin_0c916 | 5528fcf0b22c | -10.5282 | 2 | 0.0114286 | 0.0606733 | 0.0281481 | 0.111934 | 0.00877411 | 0.00158685 |
| inverse7blend_1040_max | inverse7blend_1040 | 3d35ba77dad0 | -12.6463 | 1 | 0.00946032 | 0.0612061 | 0.0258624 | 0.104939 | 0.00433237 | 0.00278211 |

### Inverse7 Adverse Worlds

| objective | source_role | world_id | plausibility_energy | plausibility_rank | target_prior_mae | subject_target_mae | pair_joint_mae | flip_subject_mae | mixmin_0c916 | inverse7blend_1040 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inverse7blend_1040_max | inverse7blend_1040 | 3d35ba77dad0 | -12.6463 | 1 | 0.00946032 | 0.0612061 | 0.0258624 | 0.104939 | 0.00433237 | 0.00278211 |
| mixmin_0c916_max | mixmin_0c916 | 5528fcf0b22c | -10.5282 | 2 | 0.0114286 | 0.0606733 | 0.0281481 | 0.111934 | 0.00877411 | 0.00158685 |
| frontier_random_13 | random | e6e102dc8a8b | 1.68559 | 22 | 0.0659048 | 0.072502 | 0.0712593 | 0.121591 | -0.000315338 | 6.01494e-05 |

## Decision

- worlds scored: `29`.
- low-energy-half mixmin better_rate: `0.857143`.
- At least one mixmin-adverse world is among the most plausible quartile; plausibility diagnostics cannot safely discard it.
- This is a LeJEPA-style world-geometry gate: useful for probe ranking, not a leaderboard prior.
