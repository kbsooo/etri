# Binary Anchor Loss Family/Null Audit

Question: is the E32/E33 anchor-loss gate a structural signal, or an artifact of one anchor family or target-axis alignment?

## Method

- Recompute anchor-loss energy after omitting or isolating anchor families: raw05, medium non-JEPA anchors, and bad JEPA anchors.
- Ablate energy components: cancellation, positive-share alignment, and movement/loss correlation.
- Run a target-axis null by permuting moved-target weights inside each anchor row while preserving per-target loss deltas and cancellation.

## Family Holdout Low-Half Summary

| scenario | anchors | role | worlds | better_rate | max_delta | adverse_in_band | adverse_min_rank | adverse_max_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 7 | inverse7blend_1040 | 15 | 1 | -2.46186e-05 | 0 | 26 | 28 |
| all | 7 | mixmin_0c916 | 15 | 1 | -0.000537096 | 0 | 26 | 28 |
| all | 7 | pair_sensor_1bb | 15 | 0.4 | 0.00233289 | 0 | 26 | 28 |
| all | 7 | pair_sensor_6b | 15 | 0.333333 | 0.00281774 | 0 | 26 | 28 |
| no_bad_jepa | 4 | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 27 | 28 |
| no_bad_jepa | 4 | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 27 | 28 |
| no_bad_jepa | 4 | pair_sensor_1bb | 14 | 0.428571 | 0.00233289 | 0 | 27 | 28 |
| no_bad_jepa | 4 | pair_sensor_6b | 14 | 0.357143 | 0.00281774 | 0 | 27 | 28 |
| no_medium_non_jepa | 4 | inverse7blend_1040 | 14 | 0.928571 | 6.01494e-05 | 0 | 18 | 29 |
| no_medium_non_jepa | 4 | mixmin_0c916 | 14 | 1 | -0.000315338 | 0 | 18 | 29 |
| no_medium_non_jepa | 4 | pair_sensor_1bb | 14 | 0.357143 | 0.00233289 | 0 | 18 | 29 |
| no_medium_non_jepa | 4 | pair_sensor_6b | 14 | 0.285714 | 0.00281774 | 0 | 18 | 29 |
| no_raw05 | 6 | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 27 | 29 |
| no_raw05 | 6 | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 27 | 29 |
| no_raw05 | 6 | pair_sensor_1bb | 14 | 0.428571 | 0.00185244 | 0 | 27 | 29 |
| no_raw05 | 6 | pair_sensor_6b | 14 | 0.357143 | 0.00224221 | 0 | 27 | 29 |
| only_bad_jepa | 3 | inverse7blend_1040 | 14 | 0.857143 | 0.00278211 | 2 | 5 | 10 |
| only_bad_jepa | 3 | mixmin_0c916 | 14 | 0.857143 | 0.00877411 | 2 | 5 | 10 |
| only_bad_jepa | 3 | pair_sensor_1bb | 14 | 0.357143 | 0.00185244 | 2 | 5 | 10 |
| only_bad_jepa | 3 | pair_sensor_6b | 14 | 0.357143 | 0.00224221 | 2 | 5 | 10 |
| only_medium_non_jepa | 3 | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 27 | 29 |
| only_medium_non_jepa | 3 | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 27 | 29 |
| only_medium_non_jepa | 3 | pair_sensor_1bb | 14 | 0.428571 | 0.00233289 | 0 | 27 | 29 |
| only_medium_non_jepa | 3 | pair_sensor_6b | 14 | 0.357143 | 0.00281774 | 0 | 27 | 29 |
| raw05_plus_bad_jepa | 4 | inverse7blend_1040 | 14 | 0.928571 | 6.01494e-05 | 0 | 18 | 29 |
| raw05_plus_bad_jepa | 4 | mixmin_0c916 | 14 | 1 | -0.000315338 | 0 | 18 | 29 |
| raw05_plus_bad_jepa | 4 | pair_sensor_1bb | 14 | 0.357143 | 0.00233289 | 0 | 18 | 29 |
| raw05_plus_bad_jepa | 4 | pair_sensor_6b | 14 | 0.285714 | 0.00281774 | 0 | 18 | 29 |
| raw05_plus_medium | 4 | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 27 | 28 |
| raw05_plus_medium | 4 | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 27 | 28 |
| raw05_plus_medium | 4 | pair_sensor_1bb | 14 | 0.428571 | 0.00233289 | 0 | 27 | 28 |
| raw05_plus_medium | 4 | pair_sensor_6b | 14 | 0.357143 | 0.00281774 | 0 | 27 | 28 |

## Component Ablation Low-Half Summary

| component_mode | role | worlds | better_rate | max_delta | adverse_mixmin_worlds_in_band | adverse_mixmin_min_rank | adverse_mixmin_max_rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full | mixmin_0c916 | 15 | 1 | -0.000537096 | 0 | 26 | 28 |
| full | inverse7blend_1040 | 15 | 1 | -2.46186e-05 | 0 | 26 | 28 |
| full | pair_sensor_1bb | 15 | 0.4 | 0.00233289 | 0 | 26 | 28 |
| full | pair_sensor_6b | 15 | 0.333333 | 0.00281774 | 0 | 26 | 28 |
| no_cancellation | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 21 | 27 |
| no_cancellation | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 21 | 27 |
| no_cancellation | pair_sensor_1bb | 14 | 0.428571 | 0.00233289 | 0 | 21 | 27 |
| no_cancellation | pair_sensor_6b | 14 | 0.357143 | 0.00281774 | 0 | 21 | 27 |
| no_positive | mixmin_0c916 | 14 | 1 | -0.000315338 | 0 | 26 | 29 |
| no_positive | inverse7blend_1040 | 14 | 0.928571 | 6.01494e-05 | 0 | 26 | 29 |
| no_positive | pair_sensor_1bb | 14 | 0.428571 | 0.000490769 | 0 | 26 | 29 |
| no_positive | pair_sensor_6b | 14 | 0.357143 | 0.000614961 | 0 | 26 | 29 |
| no_corr | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 25 | 28 |
| no_corr | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 25 | 28 |
| no_corr | pair_sensor_1bb | 14 | 0.357143 | 0.00233289 | 0 | 25 | 28 |
| no_corr | pair_sensor_6b | 14 | 0.285714 | 0.00281774 | 0 | 25 | 28 |
| cancellation_only | mixmin_0c916 | 14 | 1 | -0.000315338 | 0 | 26 | 29 |
| cancellation_only | inverse7blend_1040 | 14 | 0.928571 | 6.01494e-05 | 0 | 26 | 29 |
| cancellation_only | pair_sensor_1bb | 14 | 0.357143 | 0.000490769 | 0 | 26 | 29 |
| cancellation_only | pair_sensor_6b | 14 | 0.285714 | 0.000614961 | 0 | 26 | 29 |
| alignment_only | mixmin_0c916 | 14 | 1 | -0.000537096 | 0 | 21 | 27 |
| alignment_only | inverse7blend_1040 | 14 | 1 | -2.46186e-05 | 0 | 21 | 27 |
| alignment_only | pair_sensor_1bb | 14 | 0.428571 | 0.00233289 | 0 | 21 | 27 |
| alignment_only | pair_sensor_6b | 14 | 0.357143 | 0.00281774 | 0 | 21 | 27 |

## Target-Axis Permutation Null

| band | permutations | mixmin_full_support_rate | no_adverse_rate | adverse_min_rank_median | adverse_min_rank_p10 | mixmin_max_delta_median | mixmin_max_delta_p90 | pair1bb_better_rate_median | pair6b_better_rate_median |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| perm_low_half | 500 | 1 | 1 | 25 | 22 | -0.000315338 | -0.000315338 | 0.357143 | 0.285714 |
| perm_low_quarter | 500 | 1 | 1 | 25 | 22 | -0.000537096 | -0.000315338 | 0.428571 | 0.285714 |

## Decision

- Mixmin survives the main family holdouts: no raw05, no medium anchors, and no bad-JEPA anchors all keep low-half support at `1.0`.
- The failure case is `only_bad_jepa`: adverse mixmin worlds enter the low-energy half and mixmin better_rate drops to `0.857143`.
- Medium non-JEPA anchors alone are sufficient for the E32/E33 gate, while bad-JEPA anchors alone are not.
- Component ablations keep mixmin one-sided, so the signal is not dependent on a single energy component.
- Target-axis permutation null also keeps mixmin one-sided in all 500 permutations. This means the gate is not mainly using exact moved-target axis semantics; it is dominated by broader known-anchor loss/cancellation geometry.
- Update the interpretation: E32/E33 are useful as anchor-loss geometry diagnostics, but weaker as evidence for a JEPA-style target-axis semantic alignment.
- Use this as a falsification stress for E32/E33, not as a direct submission optimizer.
