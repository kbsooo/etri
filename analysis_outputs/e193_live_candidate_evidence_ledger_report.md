# E193 Live Candidate Evidence Ledger

## Question

Can the current evidence justify one live public sensor among E176, E154, and E144 without pretending that local diagnostics certify expected public LogLoss?

## Result

E176 remains the highest-information next public sensor, not because it is certified to beat E95, but because its evidence balance is the only positive one after combining visible-body/Q2 support, antisymmetric pair geometry, pressure-range width, and clean-E72 diagnostics. The counter-evidence is real: inherited binary worlds prefer E154/E144, and local priors reject all favorable pressure branches.

E176 evidence balance: `3.1` with `8` support axes, `4` warning axes, `0` underidentified axes, and `0` missing comparable axes.

## Candidate Summary

| candidate | role | file | support_axes | warning_axes | underidentified_axes | missing_axes | evidence_balance | recommended_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176 | visible_body_q2_underopen | submission_e176_abl_q2_to0p75_91e49725.csv | 8 | 4 | 0 | 0 | 3.1 | first public sensor if spending one slot: broad/Q2-underopen worldview has the strongest cross-sensor balance, but still needs E177 decoding |
| e154 | repaired_branch_s3 | submission_e154_s3repair_9f2e2e73.csv | 4 | 4 | 1 | 3 | -0.225 | alternate repaired-branch worldview: inherited binary support remains alive, but pressure/pair/E72 diagnostics do not promote it over E176 |
| e144 | unrepaired_repaired_branch_contrast | submission_e144_activeboundary_d7b4b331.csv | 3 | 5 | 1 | 3 | -1.725 | unrepaired contrast/control: useful if repaired branch needs falsification, but mild shape-tail risk and pair-geometry rejection block first priority |

## Signal Audit

| candidate | axis | source | value | direction | axis_weight | evidence_balance_contribution | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e144 | q2_damping_visible_prior | E179 | NA | missing | 0 | 0 | No comparable E154/E144 Q2 damping branch exists. |
| e144 | visible_full_body_prior | E179 | NA | missing | 0 | 0 | Do not infer support or rejection from E176-only E179 evidence. |
| e144 | known_winner_topcell_calibration | E180 | NA | missing | 0 | 0 | No branch-specific veto or support is assigned here. |
| e144 | binary_world_all_binary_worlds | E181 | 2.01685955e-05 | underidentified | 0.5 | -0.125 | mean delta vs E95 2.01685955e-05; negative rate 0.379310345; worlds 29 |
| e144 | binary_world_best10_current_anchor_residual | E181 | -4.1662614e-07 | support | 1 | 1 | mean delta vs E95 -4.1662614e-07; negative rate 0.6; worlds 10 |
| e144 | binary_world_best5_current_anchor_residual | E181 | -5.14451976e-05 | support | 1 | 1 | mean delta vs E95 -5.14451976e-05; negative rate 1; worlds 5 |
| e144 | refreshed_pressure_range_width | E182/E183 | 0.00167219048 | warning | 0.75 | -0.75 | mean width 0.00167219048; min live width 0.000656640739; differing cells 164 |
| e144 | global_prior_pressure_branch_exception | E183 | 0 | warning | 0.35 | -0.35 | global favorable-min rate 0 |
| e144 | local_prior_pressure_branch_selector | E183 | 0 | warning | 0.75 | -0.75 | subject/flank/visible favorable-min rates 0/0/0; support-gap 0.888922641 |
| e144 | antisymmetric_pair_geometry | E186 | 0 | warning | 1.5 | -1.5 | favorable rate 0; mean prob 0.00942280145; min/max prob 0.00224158713/0.0260815789 |
| e144 | clean_shape_e72_tail_risk | E192 | 0.0387227287 | warning | 0.75 | -0.75 | max prob 0.0387227287; above p95 rate 0.333333333; above p99 rate 0; nearest positive rate 0 |
| e144 | e72_positive_nearest_neighbor | E192 | 0 | support | 0.5 | 0.5 | top-3 nearest positive rate 0 |
| e154 | q2_damping_visible_prior | E179 | NA | missing | 0 | 0 | No comparable E154/E144 Q2 damping branch exists. |
| e154 | visible_full_body_prior | E179 | NA | missing | 0 | 0 | Do not infer support or rejection from E176-only E179 evidence. |
| e154 | known_winner_topcell_calibration | E180 | NA | missing | 0 | 0 | No branch-specific veto or support is assigned here. |
| e154 | binary_world_all_binary_worlds | E181 | 1.72241196e-05 | underidentified | 0.5 | -0.125 | mean delta vs E95 1.72241196e-05; negative rate 0.379310345; worlds 29 |
| e154 | binary_world_best10_current_anchor_residual | E181 | -5.17532286e-06 | support | 1 | 1 | mean delta vs E95 -5.17532286e-06; negative rate 0.6; worlds 10 |
| e154 | binary_world_best5_current_anchor_residual | E181 | -5.14512978e-05 | support | 1 | 1 | mean delta vs E95 -5.14512978e-05; negative rate 1; worlds 5 |
| e154 | refreshed_pressure_range_width | E182/E183 | 0.00196429726 | warning | 0.75 | -0.75 | mean width 0.00196429726; min live width 0.000656640739; differing cells 282.666667 |
| e154 | global_prior_pressure_branch_exception | E183 | 0 | warning | 0.35 | -0.35 | global favorable-min rate 0 |
| e154 | local_prior_pressure_branch_selector | E183 | 0 | warning | 0.75 | -0.75 | subject/flank/visible favorable-min rates 0/0/0; support-gap 0.973558461 |
| e154 | antisymmetric_pair_geometry | E186 | 0 | warning | 1.5 | -1.5 | favorable rate 0; mean prob 0.00207392861; min/max prob 0.000940114893/0.00470956151 |
| e154 | clean_shape_e72_tail_risk | E192 | 0.00797273492 | support | 0.75 | 0.75 | max prob 0.00797273492; above p95 rate 0; above p99 rate 0; nearest positive rate 0 |
| e154 | e72_positive_nearest_neighbor | E192 | 0 | support | 0.5 | 0.5 | top-3 nearest positive rate 0 |
| e176 | q2_damping_visible_prior | E179 | -1.90655745e-07 | support | 0.75 | 0.75 | visible expected delta -1.90655745e-07; focus expected delta 8.23486789e-08; visible swing support 0.690494892; hard support 0.904761905 |
| e176 | visible_full_body_prior | E179 | -5.08239473e-05 | support | 1.25 | 1.25 | visible expected delta -5.08239473e-05; swing support 0.373623439; hard support 0.330752212 |
| e176 | known_winner_topcell_calibration | E180 | 0.330699094 | support | 0.5 | 0.5 | E176 top4 support 0.330699094; known-winner mean 0.170898416; known-winner max 0.310903882 |
| e176 | binary_world_all_binary_worlds | E181 | 1.19502993e-05 | warning | 0.5 | -0.5 | mean delta vs E95 1.19502993e-05; negative rate 0.206896552; worlds 29 |
| e176 | binary_world_best10_current_anchor_residual | E181 | 7.44223827e-06 | warning | 1 | -1 | mean delta vs E95 7.44223827e-06; negative rate 0.3; worlds 10 |
| e176 | binary_world_best5_current_anchor_residual | E181 | 3.91957556e-06 | warning | 1 | -1 | mean delta vs E95 3.91957556e-06; negative rate 0.4; worlds 5 |
| e176 | refreshed_pressure_range_width | E182/E183 | 0.000656640739 | support | 0.75 | 0.75 | mean width 0.000656640739; min live width 0.000656640739; differing cells 601.666667 |
| e176 | global_prior_pressure_branch_exception | E183 | 1 | support | 0.35 | 0.35 | global favorable-min rate 1 |
| e176 | local_prior_pressure_branch_selector | E183 | 0 | warning | 0.75 | -0.75 | subject/flank/visible favorable-min rates 0/0/0; support-gap 0.797945435 |
| e176 | antisymmetric_pair_geometry | E186 | 1 | support | 1.5 | 1.5 | favorable rate 1; mean prob 0.852945924; min/max prob 0.754047547/0.933324089 |
| e176 | clean_shape_e72_tail_risk | E192 | 8.33833847e-06 | support | 0.75 | 0.75 | max prob 8.33833847e-06; above p95 rate 0; above p99 rate 0; nearest positive rate 0 |
| e176 | e72_positive_nearest_neighbor | E192 | 0 | support | 0.5 | 0.5 | top-3 nearest positive rate 0 |

## Interpretation

- E176's live claim is narrow: it is the broad/Q2-underopen sensor, not a generic expected-score winner.
- E154/E144 are not dead. They are the alternate repaired-branch worldview supported by inherited binary counterpriors.
- The refreshed current-anchor worlds remain sign-underidentified, so no branch should be promoted solely from binary-world pressure.
- E183 turns visible/subject/flank local priors into anti-selectors for pressure branches. That means the local priors cannot settle the frontier.
- E186 pair geometry and E192 clean-shape diagnostics keep E176 ahead as a sensor-role choice.

## Decision

No new submission is created. The next single public file remains `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` if the goal is to maximize information from one slot. After feedback, decode it with `analysis_outputs/e177_e176_public_feedback_decoder.py --score <PUBLIC_LB>`.

If E176 improves public LB, the broad/Q2-underopen worldview is strengthened. If it ties or small-loses, the plateau law and hidden-label resolution bottleneck are strengthened. If it loses worse than E101, demote the partial-reopen family instead of tuning another keep factor.
