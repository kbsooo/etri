# E180 Known-Anchor Decisive-Cell Visibility

## Question

E179 says E176's body and Q2 damping are visible-prior supported, but its top
public-decisive cells are weak. Is that weakness actually informative, or do
successful known anchors also look weak at the top-cell layer?

## Result In One Sentence

Known successful anchors are not visible-certified at the top-cell layer either:
E95's public-positive top4 support is only `0.100896`. E176 top4 support
`0.330699` is actually above the known-winner mean, so E179 is not a hard veto;
it is evidence that visible priors are too weak to certify decisive cells.

## Pair Summary

| pair | family | actual_delta | actual_direction | n_moved_cells | n_cells_for_actual_delta | n_cells_for_frontier_edge | all_expected_delta_visible_mean | top4_observed_support_visible | frontier_observed_support_visible | actual_edge_observed_support_visible |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e101_vs_e95 | frontier_near_loss | 0.000009036 | new_lost | 50 | 1.000000000 | 2 | 0.000014709 | 0.100895683 | 0.092013172 | 0.093095238 |
| e72_vs_mixmin | q2s3_gate_fail | 0.000101137 | new_lost | 893 | 4.000000000 | 1 | -0.000705694 | 0.793303634 | 0.870014758 | 0.793303634 |
| e72_vs_e95 | q2s3_gate_fail | 0.000116447 | new_lost | 1047 | 6.000000000 | 1 | -0.000513206 | 0.696441473 | 0.617505669 | 0.758862367 |
| mixmin_vs_a2c8 | broad_public_success | -0.001132680 | new_won | 1256 | 25.000000000 | 1 | 0.000028558 | 0.310903882 | 0.117480799 | 0.390672750 |
| e95_vs_mixmin | frontier_hardtail_success | -0.000015311 | new_won | 550 | 1.000000000 | 1 | -0.000192489 | 0.100895683 | 0.093095238 | 0.093095238 |
| e101_vs_mixmin | mixmin_relative_success | -0.000006275 | new_won | 550 | 1.000000000 | 1 | -0.000177780 | 0.100895683 | 0.093095238 | 0.093095238 |
| e176_vs_e95_pending | pending_broad_q2_underopen |  | pending_new_better | 904 |  | 4 | -0.000050824 | 0.330699094 | 0.330699094 |  |

## Top4 Anchor Calibration

| pair | set | actual_direction | n_cells | targets | expected_delta_visible_mean | observed_direction_support_swing_visible_mean | intended_support_swing_visible_mean | visible_sign_matches_actual | between_train_runs_rate | e72_active_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_vs_a2c8 | top4 | new_won | 4 | S1,S2,S3 | -0.000005725 | 0.310903882 | 0.310903882 | True | 1.000000000 | 0.750000000 |
| e95_vs_mixmin | top4 | new_won | 4 | S3 | -0.000007733 | 0.100895683 | 0.100895683 | True | 1.000000000 | 1.000000000 |
| e101_vs_mixmin | top4 | new_won | 4 | S3 | -0.000005871 | 0.100895683 | 0.100895683 | True | 1.000000000 | 1.000000000 |
| e101_vs_e95 | top4 | new_lost | 4 | S3 | 0.000001862 | 0.100895683 | 0.899104317 | True | 1.000000000 | 1.000000000 |
| e72_vs_mixmin | top4 | new_lost | 4 | S3 | 0.000003383 | 0.793303634 | 0.206696366 | True | 0.750000000 | 1.000000000 |
| e72_vs_e95 | top4 | new_lost | 4 | Q2,S1,S2 | -0.000001698 | 0.696441473 | 0.303558527 | False | 0.500000000 | 1.000000000 |
| e176_vs_e95_pending | top4 | pending_new_better | 4 | Q3,S1 | -0.000001965 | 0.330699094 | 0.330699094 |  | 1.000000000 | 0.750000000 |

## E176 Critical Sets

| pair | set | actual_direction | n_cells | targets | expected_delta_visible_mean | observed_direction_support_swing_visible_mean | intended_support_swing_visible_mean | visible_sign_matches_actual | between_train_runs_rate | e72_active_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176_vs_e95_pending | top4 | pending_new_better | 4 | Q3,S1 | -0.000001965 | 0.330699094 | 0.330699094 |  | 1.000000000 | 0.750000000 |
| e176_vs_e95_pending | top16 | pending_new_better | 16 | Q1,Q3,S1,S2,S3,S4 | -0.000005872 | 0.266074266 | 0.266074266 |  | 0.875000000 | 0.375000000 |

## Calibration Checks

| question | e176_top4_intended_support_visible | known_winner_min | known_winner_mean | known_winner_max | e176_below_winner_min | e176_above_winner_mean | e176_above_winner_max | known_loss_mean_observed_adverse_support | known_loss_max_observed_adverse_support | e176_lower_than_loss_adverse_mean | known_pairs | sign_accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176_top4_vs_known_winners | 0.330699094 | 0.100895683 | 0.170898416 | 0.310903882 | False | True | True |  |  |  |  |  |
| e176_top4_vs_known_losses_observed_adverse | 0.330699094 |  |  |  |  |  |  | 0.530213597 | 0.793303634 | True |  |  |
| known_anchor_visible_sign_accuracy_all_moved |  |  |  |  |  |  |  |  |  |  | 6.000000000 | 0.500000000 |

## Interpretation

- Known winners can have very weak top-cell support, so E179's weak top-cell
  read is not enough to reject E176.
- The all-moved visible-prior sign accuracy across known anchors is only `0.5`,
  so visible priors are not a reliable standalone public selector.
- Failed E72 has strong observed-adverse top-cell support, but the near-frontier
  E101 loss does not; decisive-cell visibility is therefore anchor-specific.
- E176 remains a sensor because it is body-supported, Q2-damping-supported, and
  no current public-free signal certifies the hidden top cells.

## Decision

No submission is created. Keep
`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the single
next public sensor if spending one slot, but do not describe it as locally
certified. The next representation problem is to predict decisive-cell support
below the current visible-prior resolution.
