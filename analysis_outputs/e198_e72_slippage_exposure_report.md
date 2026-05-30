# E198 E72 Slippage Exposure

## Question

E197 says E176 only loses under E72-like adverse public slippage. Does E176 also look
E72-like under the boundary-clean E191/E192 shape diagnostic, or is that failure only
an algebraic stress case?

## Detector Health

- Boundary-clean detector: `shape_target_context_abs / plain_logit_c025 / loo_pair_id` with AUC `0.978835979`, AP `0.80952381`, top-k recall `0.666666667`, exact E95/E101 mean probability `0.0576577108`.
- Branch anatomy thresholds: non-E72 p95 `0.020814665`, non-E72 p99 `0.0448123614`, known positive floor `0.804849225`.

## Known E72 Slippage

| pair | actual_delta | q_tie | q_observed | q_visible_mean | slippage_vs_visible_mean | q_focus_mean | slippage_vs_focus_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e72_vs_mixmin | 0.0001011367 | 0.348723434 | 0.333592771 | 0.454299556 | -0.120706785 | 0.465070057 | -0.131477286 |
| e72_vs_e95 | 0.0001164474 | 0.393624086 | 0.380429046 | 0.451777103 | -0.0713480571 | 0.463444937 | -0.0830158913 |

## Candidate Join

| candidate | world | surplus_to_tie_visible_mean | surplus_to_tie_focus_mean | visible_outcome_e72_vs_e95 | visible_outcome_e72_vs_mixmin | focus_outcome_e72_vs_e95 | focus_outcome_e72_vs_mixmin | shape_e72_prob_max | shape_e72_band | scenarios_above_non_e72_p95 | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e176 | broad_q2_underopen | 0.0617609208 | 0.0948360616 | small_loss | branch_loss | micro_win | branch_loss | 8.33833847e-06 | below_non_e72_p95 | 0 | failure_algebraic_not_shape_supported |
| e144 | conservative_unrepaired_branch | 0.0115453359 | 0.0162007655 | hard_fail | hard_fail | hard_fail | hard_fail | 0.0387227287 | non_e72_p95_tail | 1 | thin_margin_plus_shape_tail_alarm |
| e154 | repaired_branch_counterworld | 0.0102841947 | 0.0147882949 | hard_fail | hard_fail | hard_fail | hard_fail | 0.00797273492 | below_non_e72_p95 | 0 | thin_margin_not_e72_shape |
| e155 | low_body_repaired_branch_control | 0.0112267186 | 0.0158422936 | hard_fail | hard_fail | hard_fail | hard_fail | NA | not_scored | NA | needs_shape_score_if_prioritized |
| e166 | broad_plateau_break_safety_atlas_test | 0.0569679244 | 0.0851363705 | branch_loss | hard_fail | micro_win | hard_fail | NA | not_scored | NA | needs_shape_score_if_prioritized |
| e172 | safer_tail_repair_contrast | 0.0706130392 | 0.101889633 | tie | branch_loss | micro_win | branch_loss | NA | not_scored | NA | needs_shape_score_if_prioritized |
| e174 | full_q2_reopen_contrast | 0.061081224 | 0.0942448721 | small_loss | branch_loss | micro_win | branch_loss | NA | not_scored | NA | needs_shape_score_if_prioritized |

## Interpretation

- E176 still has an E72-like algebraic failure mode: visible-prior stress loses under both E72 analogues, and focus-prior stress loses under the harsher E72-vs-mixmin analogue.
- But E176's maximum clean shape E72 probability is far below the non-E72 p95 and far below the known-positive floor. That means the E72 failure mode is not structurally supported by the only boundary-clean E72 detector we have.
- E154 remains a thin-margin repaired-branch counterworld rather than an E72-contaminated branch. It fails easily because its support-mass surplus is small, not because the clean E72 shape detector lights up.
- E144 is the only scored branch with a mild non-E72-p95 tail alarm, but it still sits below p99 and nowhere near positive scale; this is tail-risk anatomy, not E72 certification.
- Candidates not scored by E192 should not be promoted solely from E197. If one of them becomes next, it needs a direct shape-anatomy score first.

## Decision

No new submission is created. E198 strengthens the current read: keep E176 as the next public sensor, but if it fails, interpret the failure by the pre-registered LB band rather than by claiming E176 was structurally E72-like before feedback.
