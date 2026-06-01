# H033 Phase-Lock Contrastive HS-JEPA

## Question

H032 recovered H012 but found no stronger sibling. H033 asks which row-target operations make those siblings fail, and whether the learned phase-lock law contains any negative-cost move away from H012.

## Phase-Lock Model Health

- best all-OOF alpha: `100.0` MAE `0.000814682`, Spearman `0.954416119`, pairwise `0.912785497`
- full-fit train MAE: `0.000756047`
- full-fit train Spearman: `0.960697069`
- H012-support cells with negative rollback cost: `538` / `1200`
- outside-support cells with negative add cost: `247` / `550`

## Best CV Rows

| alpha | fold | n_test | mae | rmse | spearman | pair_acc | pred_min | pred_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100.000000000 | __all_oof__ | 4262 | 0.000814682 | 0.001559049 | 0.954416119 | 0.912785497 | 0.009563318 | 0.029591197 |
| 1000.000000000 | __all_oof__ | 4262 | 0.000819474 | 0.001569502 | 0.956011736 | 0.912217997 | 0.010406788 | 0.027647559 |
| 10.000000000 | __all_oof__ | 4262 | 0.000841048 | 0.001587558 | 0.950073659 | 0.909106387 | 0.009250044 | 0.029739987 |
| 1.000000000 | __all_oof__ | 4262 | 0.000878111 | 0.001630640 | 0.945074315 | 0.904827841 | 0.008807192 | 0.029446660 |
| 0.100000000 | __all_oof__ | 4262 | 0.000903552 | 0.001662673 | 0.941550085 | 0.901877021 | 0.008252438 | 0.029601471 |

## Target Phase-Lock Summary

| target | n | support_rate | rollback_beta_mean_support | rollback_beta_p90_support | add_beta_mean_outside | add_beta_p90_outside | negative_rollback_cells | negative_add_cells | memory_disagree_rate_support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 250 | 0.668000000 | -0.000074106 | 0.000439256 | -0.012266913 | 0.003249126 | 110 | 35 | 0.550898204 |
| Q2 | 250 | 0.420000000 | 0.000155951 | 0.001029267 | -0.009639053 | 0.005856122 | 48 | 59 | 0.609523810 |
| Q3 | 250 | 0.564000000 | 0.000208748 | 0.000593028 | 0.002027406 | 0.014754968 | 54 | 51 | 0.446808511 |
| S1 | 250 | 0.776000000 | 0.000073150 | 0.000471126 | 0.002376531 | 0.017399870 | 89 | 29 | 0.685567010 |
| S2 | 250 | 0.828000000 | 0.000026890 | 0.000309347 | 0.003569070 | 0.011899111 | 94 | 27 | 0.579710145 |
| S3 | 250 | 0.776000000 | 0.000163568 | 0.000534635 | -0.007140499 | 0.003409578 | 72 | 21 | 0.572164948 |
| S4 | 250 | 0.768000000 | 0.000082993 | 0.000375582 | 0.004949701 | 0.017645352 | 71 | 25 | 0.682291667 |

## Top Candidate Actions

| candidate_id | family | op | k | alpha | changed_cells_vs_h012 | max_abs_prob_vs_h012 | pre_state_mean | pre_state_margin_vs_h012_pred | pre_geometry_mean | h033_action_score | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| negative_add_add_k10_a0.1 | negative_add | add | 10 | 0.100000000 | 10 | 0.000070989 | 0.580715618 | 0.016275125 | 0.554915153 | 0.577417535 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k10_a0.1_03b6cd61.csv |
| negative_add_add_k10_a0.25 | negative_add | add | 10 | 0.250000000 | 10 | 0.000177488 | 0.580715617 | 0.016275124 | 0.554917190 | 0.577418044 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k10_a0.25_3704fce9.csv |
| negative_add_add_k10_a0.4 | negative_add | add | 10 | 0.400000000 | 10 | 0.000284004 | 0.580715616 | 0.016275123 | 0.554919227 | 0.577418552 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k10_a0.4_9ff4b24c.csv |
| negative_add_add_k10_a0.7 | negative_add | add | 10 | 0.700000000 | 10 | 0.000497088 | 0.580715614 | 0.016275121 | 0.554921737 | 0.577419178 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k10_a0.7_9bbecb0d.csv |
| negative_rollback_rollback_k50_a0.1 | negative_rollback | rollback | 50 | 0.100000000 | 50 | 0.004488508 | 0.586752596 | 0.022312102 | 0.554987905 | 0.583488701 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k50_a0.1_a744e87a.csv |
| negative_rollback_rollback_k50_a0.25 | negative_rollback | rollback | 50 | 0.250000000 | 50 | 0.011333213 | 0.586752695 | 0.022312202 | 0.555043616 | 0.583502728 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k50_a0.25_14e4bd23.csv |
| negative_rollback_rollback_k50_a0.4 | negative_rollback | rollback | 50 | 0.400000000 | 50 | 0.018311433 | 0.586752795 | 0.022312301 | 0.555099521 | 0.583516804 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k50_a0.4_770e5854.csv |
| negative_rollback_rollback_k50_a0.6 | negative_rollback | rollback | 50 | 0.600000000 | 50 | 0.027821438 | 0.586752928 | 0.022312435 | 0.555174361 | 0.583535647 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k50_a0.6_ecb6cddc.csv |
| negative_combo_rollback_add_k50_a0.1 | negative_combo | rollback_add | 50 | 0.100000000 | 100 | 0.004488508 | 0.587087894 | 0.022647401 | 0.555007568 | 0.583848915 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_combo_rollback_add_k50_a0.1_f02c3120.csv |
| negative_combo_rollback_add_k50_a0.25 | negative_combo | rollback_add | 50 | 0.250000000 | 100 | 0.011333213 | 0.587087969 | 0.022647476 | 0.555068644 | 0.583864259 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_combo_rollback_add_k50_a0.25_182b539b.csv |
| negative_combo_rollback_add_k50_a0.4 | negative_combo | rollback_add | 50 | 0.400000000 | 100 | 0.018311433 | 0.587088044 | 0.022647551 | 0.555127449 | 0.583879036 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_combo_rollback_add_k50_a0.4_5500f19e.csv |
| negative_add_add_k25_a0.1 | negative_add | add | 25 | 0.100000000 | 25 | 0.000158368 | 0.587782887 | 0.023342394 | 0.554921474 | 0.584492385 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k25_a0.1_0e0ef35a.csv |
| negative_add_add_k25_a0.25 | negative_add | add | 25 | 0.250000000 | 25 | 0.000395920 | 0.587782882 | 0.023342389 | 0.554927183 | 0.584493807 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k25_a0.25_3515b990.csv |
| negative_add_add_k25_a0.4 | negative_add | add | 25 | 0.400000000 | 25 | 0.000633474 | 0.587782877 | 0.023342383 | 0.554930819 | 0.584494711 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k25_a0.4_a5649842.csv |
| negative_add_add_k25_a0.7 | negative_add | add | 25 | 0.700000000 | 25 | 0.001108583 | 0.587782866 | 0.023342373 | 0.554935285 | 0.584495816 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_add_add_k25_a0.7_22d3fe8c.csv |
| negative_rollback_rollback_k80_a0.1 | negative_rollback | rollback | 80 | 0.100000000 | 80 | 0.007573832 | 0.588145517 | 0.023705024 | 0.555036739 | 0.584905831 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k80_a0.1_5c2ab66e.csv |
| negative_rollback_rollback_k80_a0.25 | negative_rollback | rollback | 80 | 0.250000000 | 80 | 0.018949515 | 0.588145698 | 0.023705205 | 0.555135299 | 0.584930652 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k80_a0.25_989959ed.csv |
| negative_rollback_rollback_k80_a0.4 | negative_rollback | rollback | 80 | 0.400000000 | 80 | 0.030332659 | 0.588145880 | 0.023705387 | 0.555234048 | 0.584955521 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k80_a0.4_55c07d54.csv |
| negative_rollback_rollback_k80_a0.6 | negative_rollback | rollback | 80 | 0.600000000 | 80 | 0.045501406 | 0.588146124 | 0.023705631 | 0.555365990 | 0.584988751 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_rollback_rollback_k80_a0.6_b156d0da.csv |
| negative_combo_rollback_add_k80_a0.1 | negative_combo | rollback_add | 80 | 0.100000000 | 160 | 0.007573832 | 0.588349445 | 0.023908952 | 0.555080453 | 0.585152688 | hitl/h033_phase_lock_contrast_jepa/submission_h033_negative_combo_rollback_add_k80_a0.1_e50b4800.csv |

## Stress

- decision: `diagnostic_only_no_phase_lock_action_clears_stress`
- promoted path: `none`
- selected candidate: `negative_add_add_k10_a0.1`
- selected pre-state margin vs H012 prediction: `0.016275125`
- pre-H012 public-score permutation p(lower margin): `0.861333333`
- H025 row-permutation p(higher top1200 gain): `0.710000000`
- real H025 top1200 gain: `0.089013449`

## Interpretation

The H032 sibling failures are learnable as a phase-lock contrast, but the negative-cost operations do not yet clear public-free action stress. This supports the discrete-translation-law direction while rejecting a direct H012 edit from the first linear contrast model.

## Files

- `hitl/h033_phase_lock_contrast_jepa/h033_break_dataset_meta.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_phase_lock_cv.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_cell_phase_lock_coefficients.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_target_phase_lock_summary.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_top_phase_lock_cells.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_generated_phase_lock_candidates.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_candidate_scores.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_selected_pre_h012_public_perm_stress.csv`
- `hitl/h033_phase_lock_contrast_jepa/h033_selected_h025_rowperm_stress.csv`
