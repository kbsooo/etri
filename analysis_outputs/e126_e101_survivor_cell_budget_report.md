# E126 E101 survivor cell-budget anatomy

## Question

E125 showed that E101-compatible scenarios are not q2s3-mask scenarios. E126
reconstructs the actual E72-adverse cells selected by the scenarios and asks:
what kind of public-miss budget makes E101's local rollback fail to transfer?

## Group Summary

| group_name | n_scenarios | avg_selected_weight_per_scenario | q_target_mass_share | s_target_mass_share | q2s3_mass_share | e101_active_mass_share | e95_fallback_mass_share | e95_moved_mass_share | edge_like_mass_share | between_train_runs_mass_share | median_alpha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| broad | 3452 | 23.037768 | 0.260431 | 0.739569 | 0.521544 | 0.354978 | 0.636322 | 0.738479 | 0.426235 | 0.540693 | 3.310470 |
| broad_all_or_top50 | 950 | 24.315679 | 0.394555 | 0.605445 | 0.374844 | 0.247347 | 0.454177 | 0.528440 | 0.446390 | 0.559606 | 1.961652 |
| broad_low_alpha | 373 | 33.335315 | 0.312772 | 0.687228 | 0.250406 | 0.120421 | 0.359532 | 0.644990 | 0.433949 | 0.595577 | 0.655417 |
| broad_q2s3 | 368 | 14.252241 | 0.486300 | 0.513700 | 1.000000 | 0.584840 | 0.918953 | 0.584840 | 0.418896 | 0.502913 | 5.755757 |
| broad_tail_equal | 37 | 33.405628 | 0.438927 | 0.561073 | 0.169618 | 0.000000 | 0.326862 | 0.444269 | 0.396016 | 0.632953 | 0.591283 |
| e101_plausible | 57 | 33.735806 | 0.431483 | 0.568517 | 0.180513 | 0.011234 | 0.356179 | 0.461882 | 0.403352 | 0.621562 | 0.791985 |

## Category Detail

| group_name | field | value | budget_share | weight_share | n_scenarios |
| --- | --- | --- | --- | --- | --- |
| broad_all_or_top50 | context_type | between_train_runs | 0.559606 | 0.602592 | 950 |
| broad_all_or_top50 | context_type | after_train_run | 0.440394 | 0.397408 | 950 |
| broad_all_or_top50 | e101_active | False | 0.752653 | 0.882748 | 950 |
| broad_all_or_top50 | e101_active | True | 0.247347 | 0.117252 | 921 |
| broad_all_or_top50 | e95_fallback_cell | False | 0.545823 | 0.725718 | 950 |
| broad_all_or_top50 | e95_fallback_cell | True | 0.454177 | 0.274282 | 950 |
| broad_all_or_top50 | pos_bin | interior | 0.553610 | 0.528431 | 950 |
| broad_all_or_top50 | pos_bin | near_edge | 0.211823 | 0.208439 | 945 |
| broad_all_or_top50 | pos_bin | left_edge | 0.125419 | 0.131947 | 903 |
| broad_all_or_top50 | pos_bin | right_edge | 0.105417 | 0.124166 | 893 |
| broad_all_or_top50 | pos_bin | single | 0.003731 | 0.007017 | 148 |
| broad_all_or_top50 | target | S3 | 0.226609 | 0.096754 | 895 |
| broad_all_or_top50 | target | S2 | 0.149918 | 0.163497 | 917 |
| broad_all_or_top50 | target | Q2 | 0.148235 | 0.094510 | 888 |
| broad_all_or_top50 | target | Q3 | 0.140259 | 0.174465 | 919 |
| broad_all_or_top50 | target | S1 | 0.131175 | 0.176808 | 920 |
| broad_all_or_top50 | target_group | S | 0.605445 | 0.585721 | 950 |
| broad_all_or_top50 | target_group | Q | 0.394555 | 0.414279 | 950 |
| broad_all_or_top50 | target_is_q2s3 | False | 0.625156 | 0.808736 | 950 |
| broad_all_or_top50 | target_is_q2s3 | True | 0.374844 | 0.191264 | 949 |
| broad_q2s3 | context_type | between_train_runs | 0.502913 | 0.546908 | 368 |
| broad_q2s3 | context_type | after_train_run | 0.497087 | 0.453092 | 368 |
| broad_q2s3 | e101_active | True | 0.584840 | 0.580201 | 368 |
| broad_q2s3 | e101_active | False | 0.415160 | 0.419799 | 368 |
| broad_q2s3 | e95_fallback_cell | True | 0.918953 | 0.823066 | 368 |
| broad_q2s3 | e95_fallback_cell | False | 0.081047 | 0.176934 | 303 |
| broad_q2s3 | pos_bin | interior | 0.581104 | 0.517350 | 368 |
| broad_q2s3 | pos_bin | near_edge | 0.235841 | 0.256804 | 364 |
| broad_q2s3 | pos_bin | left_edge | 0.132655 | 0.146182 | 332 |
| broad_q2s3 | pos_bin | right_edge | 0.049318 | 0.072801 | 250 |
| broad_q2s3 | pos_bin | single | 0.001083 | 0.006864 | 36 |
| broad_q2s3 | target | S3 | 0.513700 | 0.460511 | 368 |
| broad_q2s3 | target | Q2 | 0.486300 | 0.539489 | 368 |
| broad_q2s3 | target_group | S | 0.513700 | 0.460511 | 368 |
| broad_q2s3 | target_group | Q | 0.486300 | 0.539489 | 368 |
| broad_q2s3 | target_is_q2s3 | True | 1.000000 | 1.000000 | 368 |
| e101_plausible | context_type | between_train_runs | 0.621562 | 0.626104 | 57 |
| e101_plausible | context_type | after_train_run | 0.378438 | 0.373896 | 57 |
| e101_plausible | e101_active | False | 0.988766 | 0.988477 | 57 |
| e101_plausible | e101_active | True | 0.011234 | 0.011523 | 20 |
| e101_plausible | e95_fallback_cell | False | 0.643821 | 0.762558 | 54 |
| e101_plausible | e95_fallback_cell | True | 0.356179 | 0.237442 | 57 |
| e101_plausible | pos_bin | interior | 0.596648 | 0.558255 | 57 |
| e101_plausible | pos_bin | near_edge | 0.186369 | 0.200380 | 57 |
| e101_plausible | pos_bin | right_edge | 0.106456 | 0.114876 | 55 |
| e101_plausible | pos_bin | left_edge | 0.104390 | 0.115328 | 54 |
| e101_plausible | pos_bin | single | 0.006138 | 0.011161 | 17 |
| e101_plausible | target | S1 | 0.248260 | 0.336180 | 55 |
| e101_plausible | target | S2 | 0.202388 | 0.184916 | 53 |
| e101_plausible | target | Q2 | 0.176275 | 0.074550 | 46 |
| e101_plausible | target | Q3 | 0.148398 | 0.140028 | 43 |
| e101_plausible | target | S4 | 0.113631 | 0.135223 | 43 |
| e101_plausible | target_group | S | 0.568517 | 0.662642 | 56 |
| e101_plausible | target_group | Q | 0.431483 | 0.337358 | 49 |
| e101_plausible | target_is_q2s3 | False | 0.819487 | 0.919127 | 56 |
| e101_plausible | target_is_q2s3 | True | 0.180513 | 0.080873 | 50 |

## Interpretation

- E101-plausible selected budget has q2s3 mass share `0.180513` and E101-active mass share `0.011234`.
- Broad q2s3 worlds have q2s3 mass share `1.000000` and E101-active mass share `0.584840`.
- Broad all/top50 worlds have q2s3 mass share `0.374844` and E101-active mass share `0.247347`.

The E101-compatible budget is not concentrated on the cells E101 actually
changes. It is broader, more S-heavy, and closer to E95's generic hard-tail
field than to the active Q2/S3 rollback. That explains why local alpha collapses:
the public-compatible tail budget charges many cells outside the E101 move, so
E101's apparent local edge is mostly not on the realized public-loss surface.

## Decision

No submission. Same-line E95-to-E101 variants remain closed. The next useful
experiment should ask whether a different hidden structure can predict this
public-transfer shrinkage field before probability movement is attempted.
