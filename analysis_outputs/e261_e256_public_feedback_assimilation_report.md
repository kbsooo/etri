# E261 E256 Public Feedback Assimilation

## Observation

`submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv` public LB is `0.5762805676`.

## Decoded Result

| item | value |
| --- | --- |
| delta_vs_E247 | 0.000121618 |
| delta_vs_E95 | -0.000010762 |
| delta_vs_mixmin | -0.000026073 |
| E259 outcome | same_family_loss |
| world update | rejection |
| branch read | same_family_loss_but_not_hard_loss |

E256 lost the E247 edge by `0.000121618`, but it still beats E95 by `0.000010762`. This is not a hard collapse of the feature-NN1 smoothing family. It is a rejection of the high-amplitude constrained refinement as the next score route.

## E260 Stress Check

| item | value |
| --- | --- |
| E260 expected E256-vs-E247 | 0.000019101 |
| actual minus expected | 0.000102517 |
| actual / expected_abs | 6.367 |
| E260 swing sum | 0.000542796 |
| min top cells for actual delta | 2 |
| min top cells for surprise over expected | 2 |

The observed loss is much larger than the E260 focus-prior expectation, but it is still hard-label-plausible: the top two E256-vs-E247 swing cells can explain the actual delta scale.

## Group Read

| pair_id | e257_group | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | post_public_read |
| --- | --- | --- | --- | --- | --- | --- | --- |
| e256_vs_e247 | e247_only | 13 | -0.000001767 | 0.000130161 | 0.453917630 | 17.859802610 | not_proven_causal_by_E256_loss |
| e256_vs_e247 | e256_only | 4 | 0.000020868 | 0.000138981 | 0.468417459 | 4.055804917 | first_suspect_after_E256_loss |

## Top E256 Swing Cells

| row_idx | target | subject_id | lifelog_date | e257_group | action | prob_delta | swing | expected_focus | support_prob_focus |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 188 | Q3 | id08 | 2024-08-09 | e256_only | add_e256_high_amp_cell | -0.033627922 | 0.000084638 | 0.000023984 | 0.367857143 |
| 96 | Q3 | id04 | 2024-10-16 | e256_only | add_e256_high_amp_cell | -0.018814299 | 0.000067654 | -0.000013650 | 0.400000000 |
| 87 | Q3 | id04 | 2024-09-19 | e256_only | add_e256_high_amp_cell | 0.017811359 | 0.000056036 | 0.000009045 | 0.600000000 |
| 138 | Q3 | id06 | 2024-07-17 | e256_only | add_e256_high_amp_cell | 0.017794964 | 0.000043825 | 0.000001489 | 0.600000000 |
| 162 | Q3 | id07 | 2024-07-23 | e247_only | remove_e247_broad_smooth_cell | -0.013749755 | 0.000031564 | 0.000004187 | 0.400000000 |
| 168 | Q3 | id07 | 2024-08-15 | e247_only | remove_e247_broad_smooth_cell | -0.012832415 | 0.000031439 | -0.000000925 | 0.400000000 |
| 76 | Q3 | id03 | 2024-10-03 | e247_only | remove_e247_broad_smooth_cell | -0.011543070 | 0.000030755 | -0.000002721 | 0.400000000 |
| 65 | Q3 | id03 | 2024-08-23 | e247_only | remove_e247_broad_smooth_cell | -0.010284578 | 0.000029866 | -0.000007116 | 0.507575758 |
| 64 | Q3 | id03 | 2024-08-22 | e247_only | remove_e247_broad_smooth_cell | -0.009412055 | 0.000023992 | -0.000001456 | 0.400000000 |
| 46 | Q3 | id02 | 2024-10-02 | e247_only | remove_e247_broad_smooth_cell | -0.009625782 | 0.000022313 | 0.000003736 | 0.273611111 |

## World Update

- Strengthened: E247 exact top34 / body-plus-rollback interaction.
- Weakened: high-amplitude constrained smoothing as a score route.
- Not proven: that E247-only broad cells alone caused the win. E260 says the four E256-only high-amplitude cells remain the first suspect.

## Next Action

Stop sibling sweeps. Submit E224 only if the next question is body attribution; otherwise search non-collinear structure.

Operational rule: do not submit another E246/E256 sibling from scalar threshold tuning. If the next question is attribution, use E224. If the next question is score, refresh non-collinear candidates under the updated E247/E256 anchors.
