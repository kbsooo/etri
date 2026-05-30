# E200 E176 vs E172 First-Sensor Resolution

## Question

E199 made E172 slightly cleaner than E176 on direct clean-shape E72 exposure. Should E172 replace E176 as the next public file, or should it stay a conditional fallback after E176 feedback?

## Result

E172 should not replace E176 as the first sensor.

The safety gain is real but too small and too narrow for the first slot. E172 has higher visible/focus support surplus by `0.00885211845` / `0.00705357098` and a slightly lower clean-shape E72 probability by `9.72276116e-06`. But choosing E172 first gives up E176's expected focus edge of `1.06885128e-05`, which is `0.698x` of the entire E95-over-mixmin public edge. It also converts the first public question from the broad E176-vs-E154 worldview conflict into a narrow E176-vs-E172 rollback contrast.

Recommended first sensor remains:

`analysis_outputs/submission_e176_abl_q2_to0p75_91e49725.csv`

E172 remains the correct same-family safety follow-up if E176 lands in the E177 tie/small-loss bands.

## Candidate Comparison

| candidate | file | role | focus_expected_delta_vs_e95 | edge_fraction_of_e95_mixmin | surplus_to_tie_visible | surplus_to_tie_focus | direct_shape_e72_prob | direct_shape_e72_band | visible_e72_vs_e95_outcome | visible_e72_vs_mixmin_outcome | focus_e72_vs_e95_outcome | focus_e72_vs_mixmin_outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e172 | submission_e172_vis_pos_all_keep0p25_d90f4407.csv | same_family_safety_after_tie_or_small_loss | -0.000112695222 | 7.36055319 | 0.0706130392 | 0.101889633 | 8.74249463e-05 | below_non_e72_p95 | tie | branch_loss | micro_win | branch_loss |
| e176 | submission_e176_abl_q2_to0p75_91e49725.csv | first_sensor_broad_q2_underopen | -0.000123383735 | 8.05866058 | 0.0617609208 | 0.0948360616 | 9.71477075e-05 | below_non_e72_p95 | small_loss | branch_loss | micro_win | branch_loss |
| e174 | submission_e174_ro_fc_top75_to1p0_95638e73.csv | full_q2_reopen_max_edge_contrast | -0.000124367054 | 8.12288492 | 0.061081224 | 0.0942448721 | 9.69540543e-05 | below_non_e72_p95 | small_loss | branch_loss | micro_win | branch_loss |

## Decision Metrics

| metric | value | scale | read |
| --- | --- | --- | --- |
| e176_expected_edge_over_e172 | 1.06885128e-05 | logloss | E176 is lower than E172 by this focus-prior expected amount. |
| e176_edge_as_fraction_of_e95_mixmin_edge | 0.698107388 | ratio | Choosing E172 first gives up about this fraction of the current E95-over-mixmin public edge. |
| e172_visible_surplus_advantage | 0.00885211845 | support_mass | E172 is safer than E176 under the visible support-mass lens by this amount. |
| e172_focus_surplus_advantage | 0.00705357098 | support_mass | E172 is safer than E176 under the focus support-mass lens by this amount. |
| e172_clean_shape_e72_advantage | 9.72276116e-06 | probability | E172 has this tiny lower clean-shape E72 probability; both are far below non-E72 p95. |
| same_family_contrast_cells | 75 | cells | E176-vs-E172 is a narrow rollback contrast. |
| counterworld_contrast_cells | 1027 | cells | E176-vs-E154 is the broad counter-world contrast. |
| same_family_to_counterworld_delta_ratio | 0.114259216 | ratio | E172-first mostly tests a narrow same-family safety rollback, not the broad world conflict. |
| e176_cells_for_e95_edge | 4 | cells | E176 is still hard-label fragile at public-edge scale. |
| e176_vs_e172_cells_for_e95_edge | 7 | cells | The E176/E172 difference is public-readable but very thin. |

## Policy Table

| choice | worldview_bet | what_it_resolves | main_downside | followup_if_good | followup_if_bad | decision |
| --- | --- | --- | --- | --- | --- | --- |
| E176 first | pair/shape/broad-body plus Q2-underopen is public-real and not E72-shaped | validates or demotes the current broad Q2-underopen worldview | slightly lower support-mass surplus than E172; E72-like slippage can small/branch-lose | promote E176; decompose non-Q2/S3/S2/S1 responsibility | route by E177: E172 after tie/small-loss, E154/search after branch/hard-loss | keep_first |
| E172 first | same-family visible-tail safety matters more than the extra E176 edge | tests safer tail-repair rollback but leaves E176 Q2-underopen mostly unobserved | gives up most of the E176-over-E172 edge and asks a lower-information question first | E176 still remains untested unless a second slot is spent | broad family becomes suspicious, but E176 can still be the better unresolved branch | conditional_after_e176_tie_or_small_loss |

## Interpretation

- E172's safety advantage is not imaginary. It is cleaner under support-mass and clean-shape E72 diagnostics.
- The advantage is not first-slot decisive. The clean-shape difference is tiny in absolute probability, and both E172/E176 are far below the non-E72 p95 threshold from E199.
- E176-vs-E172 moves only `75` cells, and its focus expected delta is only `0.114x` of the E176-vs-E154 counter-world contrast. That makes E172 a follow-up contrast, not the main worldview test.
- E172-first is coherent only if the chosen objective is private-risk minimization or same-family safety before information. The current goal is public-sensor information and frontier challenge, so E176 stays first.

## Decision

No new submission is created. Keep the conditional order:

1. E176 first.
2. If E176 ties or small-loses, E172 is the same-family safety contrast.
3. If E176 branch-loses or hard-fails, E154 is the repaired-branch counter-world.
