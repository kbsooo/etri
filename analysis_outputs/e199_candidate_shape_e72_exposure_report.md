# E199 Candidate Clean-Shape E72 Exposure

## Question

E198 scored only the pressure-branch candidates present in E192. If E176 fails and the
next branch is E172/E154/E144/E166/E155, do any of those direct candidate movements
look E72-shaped under the boundary-clean detector?

## Detector Health

- Boundary-clean detector: `shape_target_context_abs / plain_logit_c025 / loo_pair_id` with AUC `0.978835979`, AP `0.80952381`, top-k recall `0.666666667`, exact E95/E101 mean probability `0.0576577108`.
- Thresholds from full known anatomy: non-E72 p95 `0.020814665`, non-E72 p99 `0.0448123614`, E72-positive floor `0.804849225`.

## Direct Candidate Scores

| candidate | candidate_role | surplus_to_tie_visible_mean | direct_shape_e72_prob | direct_shape_e72_band | branch_shape_e72_prob_max | top3_label_rate | top3_contexts | direct_verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e144 | conservative_repaired_tail_risk_control | 0.0115453359 | 0.0543852219 | non_e72_p99_tail | 0.0387227287 | 0 | a2c8_frontier__mixmin;a2c8_frontier__mixmin;a2c8_frontier__e101 | e144_direct_p99_tail_alarm_not_positive |
| e155 | low_body_repaired_branch_control | 0.0112267186 | 0.00928385886 | below_non_e72_p95 | NA | 0 | hybrid_stage2__mixmin;hybrid_stage2__mixmin;e95__hybrid_stage2 | thin_margin_clean_shape |
| e154 | first_repaired_branch_counterworld | 0.0102841947 | 0.00785967996 | below_non_e72_p95 | 0.00797273492 | 0 | hybrid_stage2__mixmin;hybrid_stage2__mixmin;a2c8_frontier__e95 | thin_margin_clean_shape |
| e166 | broad_safety_atlas_falsification_sensor | 0.0569679244 | 0.000676943944 | below_non_e72_p95 | NA | 0 | jepa_latent__raw_jepa;jepa_latent__raw_jepa;a2c8_frontier__jepa_latent | direct_clean_shape |
| e176 | first_sensor | 0.0617609208 | 9.71477075e-05 | below_non_e72_p95 | 8.33833847e-06 | 0 | a2c8_frontier__jepa_latent;a2c8_frontier__jepa_latent;jepa_latent__raw_jepa | direct_clean_shape |
| e174 | full_q2_reopen_contrast_after_feedback | 0.061081224 | 9.69540543e-05 | below_non_e72_p95 | NA | 0 | a2c8_frontier__jepa_latent;a2c8_frontier__jepa_latent;jepa_latent__raw_jepa | direct_clean_shape |
| e172 | same_family_safety_after_tie_or_small_loss | 0.0706130392 | 8.74249463e-05 | below_non_e72_p95 | NA | 0 | a2c8_frontier__jepa_latent;a2c8_frontier__jepa_latent;jepa_latent__raw_jepa | direct_clean_shape |

## Interpretation

- E172 and E174 are clean under direct candidate-vs-E95 shape scoring. This removes the main missing-shape caveat from E198 for the same-family safety and Q2-amplitude contrasts.
- E166 is also clean-shape non-E72. Its E197 hard-fail risk is therefore broad support-mass slippage/tail exposure, not visible E72 movement shape.
- E154 and E155 are clean-shape non-E72 but thin-margin. Their risk remains repaired-branch margin fragility rather than E72 contamination.
- E144 is the only direct movement with a p99 tail alarm (`non_e72_p99_tail`), still far below the E72-positive floor. This supports preferring E154 over E144 as the first repaired-branch counter-world after adverse E176 feedback.
- E176 remains clean by direct scoring too. E199 therefore reinforces the E198 distinction between algebraic E72-like slippage and visible E72 shape exposure.

## Decision

No submission is created. Keep E176 first. If E176 lands in a tie/small-loss band, E172 is a cleaner same-family safety contrast than E174 by information role and is not E72-shaped. If E176 lands in a branch/hard-loss band, E154 remains the first repaired-branch counter-world; E144 should be treated as a tail-risk control, not first follow-up.
