# E260 Post-E247 Next-Slot Risk Atlas

## Question

E259 says E256 and E224 are the two clean next public observations. E260 asks which one is safer as a score attempt and how hard-label-fragile each observation is relative to the current E247 anchor.

Negative `expected_focus` means the candidate is favored over E247 by the public-free focus prior. Positive means the prior still favors E247.

## Pair Summary

| pair_id | moved_cells | moved_rows | expected_focus | adverse_delta | support_prob_focus_swing_weighted | swing_sum | top1_over_abs_expected | cells_to_overturn_expected_focus | cells_for_e259_clean_band | expected_vs_e247_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224_vs_e247 | 34 | 34 | 0.000066519 | 0.000632592 | 0.433489917 | 0.001305849 | 1.413603067 | 1 | 1 | candidate_expected_worse_than_e247 |
| e256_vs_e247 | 17 | 17 | 0.000019101 | 0.000269142 | 0.460653445 | 0.000542796 | 4.431072193 | 1 | 1 | candidate_expected_worse_than_e247 |

## Key Read

- E256 expected penalty vs E247 is `0.000019101`; E224 expected penalty is `0.000066519` (`3.482x` larger for E224).
- Inside E256, removing E247-only broad cells is slightly favorable under focus prior (`-0.000001767`), while the four E256-only high-amplitude cells are adverse (`0.000020868`).
- E224-vs-E247 risk is dominated by removing the common rollback core (`0.000068286` over `21` cells).


## Target Summary

| pair_id | target | moved_cells | moved_rows | subjects_moved | targets_moved | expected_focus | expected_global | expected_subject | expected_nearest_hard085 | support_delta | adverse_delta | swing_sum | top1_swing | top3_swing | top5_swing | top10_swing | support_prob_focus_mean | support_prob_focus_swing_weighted | mean_abs_prob_delta | mean_abs_logit_delta | max_abs_logit_delta | cells_for_2e6_guard | cells_for_e95_over_mixmin_edge | cells_for_e259_clean_band | cells_for_e247_over_e95_edge | cells_to_overturn_expected_focus | top1_over_abs_expected | top5_over_abs_expected | top1_swing_share | top5_swing_share | expected_vs_e247_interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224_vs_e247 | Q3 | 34 | 34 | 10 | Q3 | 0.000066519 | 0.000064469 | 0.000055881 | 0.000079207 | -0.000673258 | 0.000632592 | 0.001305849 | 0.000094032 | 0.000241324 | 0.000362969 | 0.000602495 | 0.453374583 | 0.433489917 | 0.015299830 | 0.067212826 | 0.164555230 | 1 | 1 | 1 | 2 | 1 | 1.413603067 | 5.456614619 | 0.072007978 | 0.277956236 | candidate_expected_worse_than_e247 |
| e256_vs_e247 | Q3 | 17 | 17 | 7 | Q3 | 0.000019101 | 0.000018442 | 0.000010422 | 0.000028439 | -0.000273654 | 0.000269142 | 0.000542796 | 0.000084638 | 0.000208328 | 0.000283717 | 0.000422083 | 0.475025465 | 0.460653445 | 0.011328145 | 0.055876079 | 0.148117043 | 1 | 1 | 1 | 2 | 1 | 4.431072193 | 14.853467377 | 0.155930184 | 0.522696042 | candidate_expected_worse_than_e247 |

## E257 Cell-Group Summary

| pair_id | e257_group | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- | --- |
| e224_vs_e247 | common | 21 | 0.000068286 | 0.000502431 | 0.427641668 | 1.377017065 |
| e224_vs_e247 | e247_only | 13 | -0.000001767 | 0.000130161 | 0.453917630 | 17.859802610 |
| e256_vs_e247 | e247_only | 13 | -0.000001767 | 0.000130161 | 0.453917630 | 17.859802610 |
| e256_vs_e247 | e256_only | 4 | 0.000020868 | 0.000138981 | 0.468417459 | 4.055804917 |

## Top Swing Cells

| pair_id | row_idx | target | subject_id | lifelog_date | e257_group | action | prob_delta | swing | expected_focus | support_prob_focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e224_vs_e247 | 223 | Q3 | id09 | 2024-09-15 00:00:00 | common | remove_e247_rollback_cell | -0.041105376 | 0.000094032 | 0.000012936 | 0.370325203 |
| e224_vs_e247 | 150 | Q3 | id06 | 2024-08-23 00:00:00 | common | remove_e247_rollback_cell | -0.026276056 | 0.000074738 | -0.000009077 | 0.400000000 |
| e224_vs_e247 | 235 | Q3 | id10 | 2024-08-17 00:00:00 | common | remove_e247_rollback_cell | -0.027060676 | 0.000072554 | -0.000006665 | 0.400000000 |
| e224_vs_e247 | 237 | Q3 | id10 | 2024-08-19 00:00:00 | common | remove_e247_rollback_cell | -0.031297530 | 0.000071574 | 0.000013495 | 0.304545455 |
| e224_vs_e247 | 158 | Q3 | id07 | 2024-07-19 00:00:00 | common | remove_e247_rollback_cell | 0.021424015 | 0.000050071 | -0.000001306 | 0.600000000 |
| e224_vs_e247 | 222 | Q3 | id09 | 2024-09-13 00:00:00 | common | remove_e247_rollback_cell | -0.021534327 | 0.000049759 | 0.000007545 | 0.400000000 |
| e224_vs_e247 | 51 | Q3 | id02 | 2024-10-07 00:00:00 | common | remove_e247_rollback_cell | -0.021575006 | 0.000049339 | 0.000010714 | 0.273611111 |
| e224_vs_e247 | 105 | Q3 | id04 | 2024-10-28 00:00:00 | common | remove_e247_rollback_cell | -0.019229194 | 0.000048366 | -0.000002463 | 0.400000000 |
| e224_vs_e247 | 196 | Q3 | id08 | 2024-09-10 00:00:00 | common | remove_e247_rollback_cell | -0.016896392 | 0.000046652 | 0.000014341 | 0.400000000 |
| e224_vs_e247 | 230 | Q3 | id10 | 2024-08-06 00:00:00 | common | remove_e247_rollback_cell | -0.019702691 | 0.000045411 | 0.000006592 | 0.400000000 |
| e224_vs_e247 | 52 | Q3 | id02 | 2024-10-08 00:00:00 | common | remove_e247_rollback_cell | -0.018168139 | 0.000043676 | 0.000005049 | 0.273611111 |
| e224_vs_e247 | 236 | Q3 | id10 | 2024-08-18 00:00:00 | common | remove_e247_rollback_cell | 0.014967214 | 0.000042009 | 0.000004847 | 0.600000000 |
| e256_vs_e247 | 188 | Q3 | id08 | 2024-08-09 00:00:00 | e256_only | add_e256_high_amp_cell | -0.033627922 | 0.000084638 | 0.000023984 | 0.367857143 |
| e256_vs_e247 | 96 | Q3 | id04 | 2024-10-16 00:00:00 | e256_only | add_e256_high_amp_cell | -0.018814299 | 0.000067654 | -0.000013650 | 0.400000000 |
| e256_vs_e247 | 87 | Q3 | id04 | 2024-09-19 00:00:00 | e256_only | add_e256_high_amp_cell | 0.017811359 | 0.000056036 | 0.000009045 | 0.600000000 |
| e256_vs_e247 | 138 | Q3 | id06 | 2024-07-17 00:00:00 | e256_only | add_e256_high_amp_cell | 0.017794964 | 0.000043825 | 0.000001489 | 0.600000000 |
| e256_vs_e247 | 162 | Q3 | id07 | 2024-07-23 00:00:00 | e247_only | remove_e247_broad_smooth_cell | -0.013749755 | 0.000031564 | 0.000004187 | 0.400000000 |
| e256_vs_e247 | 168 | Q3 | id07 | 2024-08-15 00:00:00 | e247_only | remove_e247_broad_smooth_cell | -0.012832415 | 0.000031439 | -0.000000925 | 0.400000000 |
| e256_vs_e247 | 76 | Q3 | id03 | 2024-10-03 00:00:00 | e247_only | remove_e247_broad_smooth_cell | -0.011543070 | 0.000030755 | -0.000002721 | 0.400000000 |
| e256_vs_e247 | 65 | Q3 | id03 | 2024-08-23 00:00:00 | e247_only | remove_e247_broad_smooth_cell | -0.010284578 | 0.000029866 | -0.000007116 | 0.507575758 |

## Decision

E256 has the smaller public-free expected penalty versus E247, so it remains the score-plus-information next slot.

Operationally:

- E256 remains the right next file when the goal is score plus information.
- E224 remains the right next file only when the goal is clean body attribution.
- Both observations are hard-label sensitive, so neither should be followed by a sibling sweep without public feedback.
