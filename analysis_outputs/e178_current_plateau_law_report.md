# E178 Current Plateau Law Audit

## Question

Given the resolved E101 public LB (`0.5763003660`) and the current E95
frontier (`0.5762913298`), what is the shortest law that explains why the
post-E95 plateau exists?

## Compressed Law

The current plateau is not mainly a model-capacity wall. A broad hidden body is
visible (`E166` focus-prior edge `-0.000332077`),
but public improvement after E95 is filtered through a few hard-label cells and
target-tail calibration. Ordinary CV/proxy ranking is too coarse: the best
known-LB selector p90 error is `53.33x` the E95-over-mixmin edge
(`0.0000153107`).

E101 is now the critical negative sensor: it loses to E95 by `0.0000090362`
while still beating mixmin. That means the Q2/S3 tail direction was not useless,
but it was not public-positive enough to become the next frontier.

## Candidate Geometry

| candidate | stage | known_public_lb | known_delta_vs_e95 | expected_delta_focus_mean | moved_cells | moved_rows | cells_for_e95_edge | cells_to_flip_expected_focus_mean | top1_swing_over_e95_edge | q2s3_share | bad_span_energy | max_bad_axis | max_bad_cos | hard_label_resolution_warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e101_q2s3tail | resolved negative sensor | 0.576300366 | 0.000009036 | 0.000046398 | 50 | 48 | 2 | 5 | 0.758893702 | 1.000000000 | 0.311462262 | e72 | 0.201134072 | True |
| mixmin | pre-hardtail anchor | 0.576306641 | 0.000015311 | 0.000144543 | 550 | 250 | 1 | 4 | 3.035574808 | 0.222307092 | 0.752971984 | e72 | 0.671902535 | True |
| e166_broad_raw | broad body before safety |  |  | -0.000332077 | 1750 | 250 | 3 | 74 | 0.506868169 | 0.250718585 | 0.450742441 | q2_bad | 0.268538582 | True |
| e174_full_q2_reopen | partial reopen max-edge |  |  | -0.000124367 | 904 | 193 | 4 | 33 | 0.380907323 | 0.339596661 | 0.263996062 | q2_bad | 0.163228574 | True |
| e176_q2_underopen | risk-adjusted current candidate |  |  | -0.000123384 | 904 | 193 | 4 | 33 | 0.380907323 | 0.334752793 | 0.261687078 | q2_bad | 0.158126325 | True |
| e169_context_veto | context safety mask |  |  | -0.000120457 | 904 | 193 | 4 | 32 | 0.380907323 | 0.347774767 | 0.295326361 | q2_bad | 0.222381361 | True |
| e172_tail_repair | visible-tail repair |  |  | -0.000112695 | 904 | 193 | 4 | 30 | 0.380907323 | 0.315865612 | 0.257873612 | q2_bad | 0.142927053 | True |
| e154_s3repair | conservative sibling |  |  | -0.000029838 | 294 | 139 | 1 | 3 | 1.001889767 | 0.152444765 | 0.313902067 | resid_bad | 0.205542728 | True |

## Evidence

| evidence | value | unit | read |
| --- | --- | --- | --- |
| frontier_edge_e95_vs_mixmin | 0.000015311 | logloss | E95 beat mixmin by a public-real but tiny hardtail edge. |
| e101_loss_vs_e95 | 0.000009036 | logloss | Q2/S3 tail rollback returned 59.02% of the E95-over-mixmin gain; the axis is fragile. |
| selector_p90_over_e95_edge | 53.328498494 | ratio | Known-LB selector p90 error is far too coarse for post-E95 ranking. |
| selector_mae_over_e95_edge | 33.969396044 | ratio | Even average selector error exceeds the frontier edge by an order of magnitude. |
| e166_broad_expected_over_e95_edge | 21.689184934 | ratio | A broad body exists in local/focus-prior space, but it is unsafe before safety controls. |
| e169_context_expected_over_e95_edge | 7.867486814 | ratio | Context/veto repair preserves a broad edge larger than E95's public gain. |
| e176_expected_over_e95_edge | 8.058660581 | ratio | Current E176 candidate is still broad on expected score, but public resolution is cell-scale. |
| e176_cells_for_e95_edge | 4.000000000 | cells | Only a few row-target hard labels can swing an entire E95-over-mixmin edge. |
| e101_cells_for_e95_edge | 2.000000000 | cells | Resolved E101 loss sits in the same small-cell readability regime. |
| e176_q2_damping_cost_over_e95_edge | 0.064224344 | ratio | The E176-vs-E174 Q2 damping decision is below public resolution from one scalar LB. |
| e176_bad_cos_reduction_vs_e174 | 0.005102249 | cosine_delta | E176 buys a small but real LeJEPA-style bad-axis safety improvement over E174. |
| e176_q2s3_share_reduction_vs_e174 | 0.004843869 | share_delta | The live candidate deliberately spends less Q2/S3 amplitude than E174. |

## Bottleneck Status

| category | status | reason | kill_condition |
| --- | --- | --- | --- |
| A_data_signal_shortage | evidence_mixed | E166/E169/E176 have large focus-prior expected edges, so signal is not absent; public-readable residuals are still cell-scale. | A non-public-aware validation object ranks E95/E101/E176 correctly with error below 5e-6. |
| B_validation_mismatch | evidence_strong | Known-LB selector p90 error is over 50x the E95 edge and E101 local stress was optimistic. | Independent local stress predicts the next public delta within the 3e-6 tie band. |
| C_public_subset_mismatch | evidence_strong_but_underidentified | E101 lost while preserving part of mixmin gain; public realizes some tail cells differently from broad local priors. | E176 cleanly wins without new public-subset machinery, implying the mismatch was mostly Q2 amplitude. |
| D_target_prior_calibration_tail | evidence_strong | Hardtail E95 survives, E101 Q2/S3 rollback fails, and E176 only changes Q2 damping to buy safety. | A broad all-target move beats E95 while increasing Q2/S3 and bad-axis exposure. |
| E_representation_capacity | evidence_weak | Representation/broad body exists, but LeJEPA-style bad-axis and tail-risk constraints dominate candidate acceptance. | A new latent creates a non-collinear movement with public-safe tail metrics and material expected edge. |
| F_candidate_selection | evidence_partial | E176 is a better risk-adjusted choice than E174, but the difference is too small to rank from current public sensors. | E176 public result falls into a clean-win or branch-loss band and separates the family. |

## E174 vs E176 Reading

E174 has the slightly better focus-prior edge
(`-0.000124367`), but E176 keeps almost the
same broad body (`-0.000123384`) while reducing
Q2/S3 share from `0.339597` to
`0.334753` and max bad-axis cosine from
`0.163229` to `0.158126`.

The E176-vs-E174 Q2 damping cost is below the scale that a single public score
can reliably decode. Therefore the current best submission action remains:
submit E176 if spending a slot, then decode the result with E177. Do not create
another same-family keep-factor sibling before that observation.

## What Would Kill This Law

- E176 cleanly beats E95 by at least the E95-over-mixmin edge: Q/S-asymmetric
  broad reopening is more real than the hard-label-resolution warning.
- E176 loses worse than E101: E174/E176 broad partial reopening is public
  misaligned and the branch should be closed.
- A new latent movement produces material expected edge, low Q2/S3 exposure,
  and low bad-axis energy while not depending on known public scores.

## Next Most Informative Action

No new submission is created here. The only current risk-adjusted public sensor
is still:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

Its claim is not "E176 is certainly better"; its claim is "the broad hidden body
survives if Q2 is under-opened." The public response will decide whether the
plateau is mostly target-amplitude calibration or a deeper public-subset/block
mismatch.
