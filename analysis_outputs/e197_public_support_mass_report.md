# E197 Public Support-Mass Inverse

## Question

Can known public LB observations be rewritten as a reusable hidden-label support-mass slippage law, and does that law certify or demote E176 before feedback?

## Result

Known public pairs do expose a useful support-mass quantity, but it is not a submission selector. E176 survives every non-E72 slippage analogue as a clean win, and fails only under E72-like adverse slippage. That is exactly the current live uncertainty: whether E176 is a clean broad/Q2-underopen repair or another E72-contaminated broad move.

E154/E144/E155 are much more slippage-fragile: their visible-prior win margins are real but thin, so any E95/E101/E72-like negative slippage turns them into branch-loss or hard-fail analogues. This supports keeping E154 as the counter-world after adverse E176 feedback, not as the first sensor.

## Known Public Pair Inversion

| pair | family | actual_delta | q_tie | q_observed | q_visible_mean | slippage_vs_visible_mean | pred_delta_visible_mean | pred_error_visible_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e101_vs_e95 | frontier_near_loss | 9.0362e-06 | 0.686469943 | 0.657165446 | 0.638769876 | 0.01839557 | 1.47085735e-05 | 5.67237352e-06 |
| e101_vs_mixmin | mixmin_relative_success | -6.2745e-06 | 0.497158314 | 0.498355755 | 0.531086313 | -0.0327305579 | -0.000177780103 | -0.000171505603 |
| e72_vs_e95 | q2s3_gate_fail | 0.0001164474 | 0.393624086 | 0.380429046 | 0.451777103 | -0.0713480571 | -0.000513205527 | -0.000629652927 |
| e72_vs_mixmin | q2s3_gate_fail | 0.0001011367 | 0.348723434 | 0.333592771 | 0.454299556 | -0.120706785 | -0.000705694204 | -0.000806830904 |
| e95_vs_mixmin | frontier_hardtail_success | -1.53107e-05 | 0.486952848 | 0.489712389 | 0.521646254 | -0.0319338655 | -0.000192488677 | -0.000177177977 |
| mixmin_vs_a2c8 | broad_public_success | -0.0011326805 | 0.505655819 | 0.530487571 | 0.505029749 | 0.0254578219 | 2.85576784e-05 | 0.00116123818 |

## Candidate Profiles

| candidate | world | n_cells | swing_sum | q_tie | q_visible_mean | surplus_to_tie_visible_mean | pred_delta_visible_mean | q_focus_mean | surplus_to_tie_focus_mean | pred_delta_focus_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e166 | broad_plateau_break_safety_atlas_test | 1750 | 0.00224398639 | 0.317761712 | 0.374729637 | 0.0569679244 | -0.000127835247 | 0.402898083 | 0.0851363705 | -0.000191044857 |
| e172 | safer_tail_repair_contrast | 904 | 0.00074849351 | 0.318570558 | 0.389183597 | 0.0706130392 | -5.28534016e-05 | 0.42046019 | 0.101889633 | -7.62637287e-05 |
| e176 | broad_q2_underopen | 904 | 0.000822914339 | 0.311862518 | 0.373623439 | 0.0617609208 | -5.08239473e-05 | 0.40669858 | 0.0948360616 | -7.80419549e-05 |
| e174 | full_q2_reopen_contrast | 904 | 0.000828950179 | 0.31207535 | 0.373156574 | 0.061081224 | -5.06332915e-05 | 0.406320222 | 0.0942448721 | -7.81243036e-05 |
| e144 | conservative_unrepaired_branch | 185 | 0.00188114286 | 0.457646083 | 0.469191419 | 0.0115453359 | -2.17184261e-05 | 0.473846848 | 0.0162007655 | -3.04759543e-05 |
| e155 | low_body_repaired_branch_control | 294 | 0.00191526888 | 0.457724214 | 0.468950933 | 0.0112267186 | -2.15021848e-05 | 0.473566508 | 0.0158422936 | -3.03422519e-05 |
| e154 | repaired_branch_counterworld | 294 | 0.00201764695 | 0.457994091 | 0.468278286 | 0.0102841947 | -2.0749874e-05 | 0.472782386 | 0.0147882949 | -2.9837558e-05 |

## Visible-Prior Slippage Stress

| candidate | world | stress_score | adverse_slippage_tolerance_to_loss | clean_or_better_rate | win_rate | branch_or_hard_fail_rate | worst_analogue | worst_delta_vs_e95 | ordered_outcomes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e172 | safer_tail_repair_contrast | 1.04166667 | 0.0706130392 | 0.666666667 | 0.666666667 | 0.166666667 | e72_vs_mixmin | 3.74948435e-05 | mixmin_vs_a2c8:clean_or_better;e101_vs_e95:clean_or_better;e95_vs_mixmin:clean_or_better;e101_vs_mixmin:clean_or_better;e72_vs_e95:tie;e72_vs_mixmin:branch_loss |
| e176 | broad_q2_underopen | 1.04166667 | 0.0617609208 | 0.666666667 | 0.666666667 | 0.166666667 | e72_vs_mixmin | 4.85073967e-05 | mixmin_vs_a2c8:clean_or_better;e101_vs_e95:clean_or_better;e95_vs_mixmin:clean_or_better;e101_vs_mixmin:clean_or_better;e72_vs_e95:small_loss;e72_vs_mixmin:branch_loss |
| e174 | full_q2_reopen_contrast | 1.04166667 | 0.061081224 | 0.666666667 | 0.666666667 | 0.166666667 | e72_vs_mixmin | 4.94266193e-05 | mixmin_vs_a2c8:clean_or_better;e101_vs_e95:clean_or_better;e95_vs_mixmin:clean_or_better;e101_vs_mixmin:clean_or_better;e72_vs_e95:small_loss;e72_vs_mixmin:branch_loss |
| e166 | broad_plateau_break_safety_atlas_test | 0.833333333 | 0.0569679244 | 0.666666667 | 0.666666667 | 0.333333333 | e72_vs_mixmin | 0.000143029135 | mixmin_vs_a2c8:clean_or_better;e101_vs_e95:clean_or_better;e95_vs_mixmin:clean_or_better;e101_vs_mixmin:clean_or_better;e72_vs_e95:branch_loss;e72_vs_mixmin:hard_fail |
| e144 | conservative_unrepaired_branch | -0.0833333333 | 0.0115453359 | 0.333333333 | 0.333333333 | 0.666666667 | e72_vs_mixmin | 0.00020534828 | mixmin_vs_a2c8:clean_or_better;e101_vs_e95:clean_or_better;e95_vs_mixmin:branch_loss;e101_vs_mixmin:branch_loss;e72_vs_e95:hard_fail;e72_vs_mixmin:hard_fail |
| e155 | low_body_repaired_branch_control | -0.0833333333 | 0.0112267186 | 0.333333333 | 0.333333333 | 0.666666667 | e72_vs_mixmin | 0.000209683764 | mixmin_vs_a2c8:clean_or_better;e101_vs_e95:clean_or_better;e95_vs_mixmin:branch_loss;e101_vs_mixmin:branch_loss;e72_vs_e95:hard_fail;e72_vs_mixmin:hard_fail |
| e154 | repaired_branch_counterworld | -0.0833333333 | 0.0102841947 | 0.333333333 | 0.333333333 | 0.666666667 | e72_vs_mixmin | 0.000222793802 | mixmin_vs_a2c8:clean_or_better;e101_vs_e95:clean_or_better;e95_vs_mixmin:branch_loss;e101_vs_mixmin:branch_loss;e72_vs_e95:hard_fail;e72_vs_mixmin:hard_fail |

## Focus-Prior Slippage Stress

| candidate | world | stress_score | adverse_slippage_tolerance_to_loss | clean_or_better_rate | win_rate | branch_or_hard_fail_rate | worst_analogue | worst_delta_vs_e95 | ordered_outcomes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e166 | broad_plateau_break_safety_atlas_test | 1.125 | 0.0851363705 | 0.666666667 | 0.833333333 | 0.166666667 | e72_vs_mixmin | 0.000103988383 | e101_vs_e95:clean_or_better;mixmin_vs_a2c8:clean_or_better;e101_vs_mixmin:clean_or_better;e95_vs_mixmin:clean_or_better;e72_vs_e95:micro_win;e72_vs_mixmin:hard_fail |
| e172 | safer_tail_repair_contrast | 1.125 | 0.101889633 | 0.666666667 | 0.833333333 | 0.166666667 | e72_vs_mixmin | 2.21461663e-05 | e101_vs_e95:clean_or_better;mixmin_vs_a2c8:clean_or_better;e101_vs_mixmin:clean_or_better;e95_vs_mixmin:clean_or_better;e72_vs_e95:micro_win;e72_vs_mixmin:branch_loss |
| e176 | broad_q2_underopen | 1.125 | 0.0948360616 | 0.666666667 | 0.833333333 | 0.166666667 | e72_vs_mixmin | 3.01525886e-05 | e101_vs_e95:clean_or_better;mixmin_vs_a2c8:clean_or_better;e101_vs_mixmin:clean_or_better;e95_vs_mixmin:clean_or_better;e72_vs_e95:micro_win;e72_vs_mixmin:branch_loss |
| e174 | full_q2_reopen_contrast | 1.125 | 0.0942448721 | 0.666666667 | 0.833333333 | 0.166666667 | e72_vs_mixmin | 3.08638159e-05 | e101_vs_e95:clean_or_better;mixmin_vs_a2c8:clean_or_better;e101_vs_mixmin:clean_or_better;e95_vs_mixmin:clean_or_better;e72_vs_e95:micro_win;e72_vs_mixmin:branch_loss |
| e144 | conservative_unrepaired_branch | -0.0833333333 | 0.0162007655 | 0.333333333 | 0.333333333 | 0.666666667 | e72_vs_mixmin | 0.000216851602 | e101_vs_e95:clean_or_better;mixmin_vs_a2c8:clean_or_better;e101_vs_mixmin:branch_loss;e95_vs_mixmin:branch_loss;e72_vs_e95:hard_fail;e72_vs_mixmin:hard_fail |
| e155 | low_body_repaired_branch_control | -0.0833333333 | 0.0158422936 | 0.333333333 | 0.333333333 | 0.666666667 | e72_vs_mixmin | 0.000221472102 | e101_vs_e95:clean_or_better;mixmin_vs_a2c8:clean_or_better;e101_vs_mixmin:branch_loss;e95_vs_mixmin:branch_loss;e72_vs_e95:hard_fail;e72_vs_mixmin:hard_fail |
| e154 | repaired_branch_counterworld | -0.0833333333 | 0.0147882949 | 0.333333333 | 0.333333333 | 0.666666667 | e72_vs_mixmin | 0.000235437186 | e101_vs_e95:clean_or_better;mixmin_vs_a2c8:clean_or_better;e101_vs_mixmin:branch_loss;e95_vs_mixmin:branch_loss;e72_vs_e95:hard_fail;e72_vs_mixmin:hard_fail |

## Interpretation

- E176 visible support surplus over tie is positive but not huge. It can absorb E95/E101/mixmin-like slippage, but not E72-like adverse slippage.
- E172 has slightly more slippage tolerance than E176 in this lens, so it remains the safer same-family contrast if E176 lands in a tie or small-loss band.
- E166 has a large base edge but also a large E72-like hard-fail tail, matching its role as a broad safety-atlas falsification sensor rather than the first expected-score file.
- E154/E144/E155 are branch sensors with thin support-mass margins. They are not invalid, but the public slippage law says they are worse first sensors than E176 unless we deliberately trust the binary/repaired-branch counterworld.

## Decision

No new submission is created. Keep `analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv` as the next public sensor. E197 strengthens the decoder: an E176 loss should be read specifically as E72-like adverse public slippage, not as a generic failure of visible support.
