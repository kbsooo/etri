# E181 E176 Binary-World Counterprior Audit

## Question

E180 says visible priors cannot certify frontier decisive cells. If the existing
binary hidden-label worlds are rescored against all current known public anchors,
do they support E176, or do they point to a different live branch?

No submission is created.

## Result In One Sentence

The current-anchor best binary worlds are a counterprior against E176: in the
best-5 residual worlds E176 averages `0.000003920`
versus E95 with negative rate `0.400`, while
E154 and E144 are negative in all best-5 worlds
(`-0.000051451` and
`-0.000051445`). This is not enough to demote
E176 by itself, but it cleanly splits the live world models.

## Current-Anchor Best Worlds

| current_anchor_residual_rank | label_world_idx | objective | source_role | current_anchor_sum_abs_residual | current_anchor_max_abs_residual | anchor_energy_quantile | mixmin_0c916 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 27 | frontier_random_16 | random | 0.00051834 | 0.000194476 | 0.241379 | -0.00127493 |
| 2 | 21 | frontier_random_10 | random | 0.000575602 | 0.000314735 | 0.172414 | -0.00114376 |
| 3 | 11 | frontier_random_00 | random | 0.000656432 | 0.000256965 | 0.310345 | -0.00111399 |
| 4 | 23 | frontier_random_12 | random | 0.000692347 | 0.000136555 | 0.344828 | -0.00116104 |
| 5 | 19 | frontier_random_08 | random | 0.000744416 | 0.000221474 | 0.206897 | -0.00110285 |
| 6 | 15 | frontier_random_04 | random | 0.000930058 | 0.000212498 | 0.37931 | -0.00120947 |
| 7 | 20 | frontier_random_09 | random | 0.00104727 | 0.000311711 | 0.137931 | -0.00096212 |
| 8 | 22 | frontier_random_11 | random | 0.00116915 | 0.000358591 | 0.62069 | -0.000950361 |
| 9 | 2 | pair_sensor_1bb_max | pair_sensor_1bb | 0.00146706 | 0.000345408 | 0.5 | -0.000806675 |
| 10 | 6 | pair_sensor_6b_max | pair_sensor_6b | 0.00146706 | 0.000345408 | 0.5 | -0.000806675 |

## Candidate Bands Versus E95

| band | candidate | delta_mean_vs_e95 | delta_min_vs_e95 | delta_max_vs_e95 | negative_rate | current_anchor_sum_abs_residual_max |
| --- | --- | --- | --- | --- | --- | --- |
| best10_current_anchor_residual | e154 | -5.17532e-06 | -8.65922e-05 | 6.67884e-05 | 0.6 | 0.00146706 |
| best10_current_anchor_residual | e144 | -4.16626e-07 | -8.02452e-05 | 8.14691e-05 | 0.6 | 0.00146706 |
| best10_current_anchor_residual | e172 | 4.77621e-06 | -1.11751e-05 | 2.35138e-05 | 0.4 | 0.00146706 |
| best10_current_anchor_residual | e176 | 7.44224e-06 | -6.66717e-06 | 2.53111e-05 | 0.3 | 0.00146706 |
| best10_current_anchor_residual | e174 | 7.71876e-06 | -5.3649e-06 | 2.66004e-05 | 0.3 | 0.00146706 |
| best3_current_anchor_residual | e144 | -4.74833e-05 | -7.68166e-05 | -3.28166e-05 | 1 | 0.000656432 |
| best3_current_anchor_residual | e154 | -4.30364e-05 | -7.43851e-05 | -2.58e-05 | 1 | 0.000656432 |
| best3_current_anchor_residual | e172 | 4.08863e-07 | -1.05653e-05 | 6.35948e-06 | 0.333333 | 0.000656432 |
| best3_current_anchor_residual | e176 | 2.31918e-06 | -6.66717e-06 | 7.07676e-06 | 0.333333 | 0.000656432 |
| best3_current_anchor_residual | e174 | 2.38823e-06 | -5.3649e-06 | 7.33324e-06 | 0.333333 | 0.000656432 |
| best5_current_anchor_residual | e154 | -5.14513e-05 | -8.65922e-05 | -2.58e-05 | 1 | 0.000744416 |
| best5_current_anchor_residual | e144 | -5.14452e-05 | -8.02452e-05 | -3.28166e-05 | 1 | 0.000744416 |
| best5_current_anchor_residual | e172 | -2.81854e-07 | -1.11751e-05 | 8.5392e-06 | 0.4 | 0.000744416 |
| best5_current_anchor_residual | e176 | 3.91958e-06 | -6.66717e-06 | 1.63397e-05 | 0.4 | 0.000744416 |
| best5_current_anchor_residual | e174 | 3.98626e-06 | -5.3649e-06 | 1.66262e-05 | 0.4 | 0.000744416 |

## E176 Band Summary

| band | candidate | delta_mean_vs_e95 | delta_min_vs_e95 | delta_max_vs_e95 | negative_rate | current_anchor_sum_abs_residual_max |
| --- | --- | --- | --- | --- | --- | --- |
| all_binary_worlds | e176 | 1.19503e-05 | -2.40384e-05 | 3.54303e-05 | 0.206897 | 0.0371949 |
| best10_current_anchor_residual | e176 | 7.44224e-06 | -6.66717e-06 | 2.53111e-05 | 0.3 | 0.00146706 |
| best15_current_anchor_residual | e176 | 6.72556e-06 | -6.66717e-06 | 2.53111e-05 | 0.266667 | 0.00172354 |
| best3_current_anchor_residual | e176 | 2.31918e-06 | -6.66717e-06 | 7.07676e-06 | 0.333333 | 0.000656432 |
| best5_current_anchor_residual | e176 | 3.91958e-06 | -6.66717e-06 | 1.63397e-05 | 0.4 | 0.000744416 |

## E176 Decisive-Cell Support Under Binary Worlds

| band | top_n | world_support_swing | visible_support_swing | hard_world_support_rate | hard_visible_support_rate |
| --- | --- | --- | --- | --- | --- |
| best3_current_anchor_residual | 4 | 0.467804 | 0.330699 | 0.5 | 0.25 |
| best3_current_anchor_residual | 8 | 0.330763 | 0.261189 | 0.25 | 0.125 |
| best3_current_anchor_residual | 16 | 0.235081 | 0.266074 | 0.1875 | 0.125 |
| best5_current_anchor_residual | 4 | 0.433633 | 0.330699 | 0.5 | 0.25 |
| best5_current_anchor_residual | 8 | 0.305649 | 0.261189 | 0.25 | 0.125 |
| best5_current_anchor_residual | 16 | 0.221275 | 0.266074 | 0.1875 | 0.125 |
| best10_current_anchor_residual | 4 | 0.262881 | 0.330699 | 0 | 0.25 |
| best10_current_anchor_residual | 8 | 0.190011 | 0.261189 | 0 | 0.125 |
| best10_current_anchor_residual | 16 | 0.17636 | 0.266074 | 0.0625 | 0.125 |
| all_binary_worlds | 4 | 0.283306 | 0.330699 | 0.25 | 0.25 |
| all_binary_worlds | 8 | 0.204612 | 0.261189 | 0.125 | 0.125 |
| all_binary_worlds | 16 | 0.174947 | 0.266074 | 0.0625 | 0.125 |

## Best-5 E176 Top Cells

| swing_rank | sub_idx | target | support_label | visible_support | world_p_y1 | world_support | hidden_block_id | context_type | e72_active | e101_active |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 141 | S1 | 0 | 0.0986477 | 0.8 | 0.2 | id06_b6 | between_train_runs | False | False |
| 2 | 196 | Q3 | 1 | 0.335672 | 0.6 | 0.6 | id08_b10 | between_train_runs | True | False |
| 3 | 190 | Q3 | 1 | 0.603741 | 0.6 | 0.6 | id08_b6 | between_train_runs | True | False |
| 4 | 194 | Q3 | 1 | 0.351616 | 0.4 | 0.4 | id08_b10 | between_train_runs | True | False |
| 5 | 67 | S4 | 1 | 0.187648 | 0.4 | 0.4 | id03_b2 | between_train_runs | False | False |
| 6 | 135 | S1 | 0 | 0.0990873 | 1 | 0 | id06_b2 | between_train_runs | True | False |
| 7 | 143 | S1 | 0 | 0.100264 | 1 | 0 | id06_b8 | between_train_runs | False | False |
| 8 | 182 | Q3 | 1 | 0.332483 | 0.2 | 0.2 | id08_b2 | between_train_runs | True | False |

## Interpretation

- E176 survives E180 because weak visible top-cell support is common among
  known winners. E181 adds the opposite stress: binary worlds that best fit the
  current public anchors do not like the E176/E174/E169 broad reopening family.
- This does not prove E176 will lose. The world pool is inherited from the
  older frontier-box construction and its current-anchor residuals are still
  larger than the E95 public edge. It is a counterprior, not a selector.
- The split is informative: visible/flank/body evidence points to E176 as the
  next broad hidden-tail sensor, while current-anchor binary worlds point toward
  the repaired E154/E144 branch.
- The next decisive local experiment should regenerate or stress a current-anchor
  binary-world pool with explicit objectives for E176, E154, and E144. If that
  fresh pool keeps E154/E144 one-sided while E176 remains mixed/adverse, the
  next submission priority should be reconsidered.

## Decision

No new submission. Keep E176 as an available public sensor only if the next slot
is meant to test the visible-body/Q2-underopen world. Do not call it the most
supported world across representations. The strongest unresolved conflict is now
E176 broad-body support versus E154/E144 binary-world counterprior.
