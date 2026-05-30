# E191 Boundary-Aware E72 Score

## Question

Can exact E95/E101 be used as an explicit hard negative so that E72-neighbor
contamination remains detectable while support-heavy false positives disappear?

## Result In One Sentence

Best pair-LOO boundary-aware row is `shape_target_context_abs` / `plain_logit_c025` with top-k recall `0.667` and exact E95/E101 mean `0.058`. No support-containing pair-LOO row passes the clean boundary gate; explicit hard-negative weighting does not rehabilitate support as a live gate.

## Summary

| feature_view | score_spec | split | n_rows | n_pos | auc | avg_precision | topk_precision | topk_recall | exact_e95_e101_mean_prob | exact_e95_e101_max_prob | e72_positive_min_prob | non_e72_p95_prob | boundary_clean_gate | skipped_rows | skipped_positive_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_target_context_abs | hardneg4_other1_c025 | loo_any_file | 242 | 6 | 0.968926554 | 0.738095238 | 0.666666667 | 0.666666667 | 0.088682979 | 0.090187467 | 0.038512612 | 0.070954290 | True | 22 | 6 |
| shape_target_context_abs | plain_logit_c025 | loo_any_file | 242 | 6 | 0.974576271 | 0.750000000 | 0.666666667 | 0.666666667 | 0.088682979 | 0.090187467 | 0.051936658 | 0.072362728 | True | 22 | 6 |
| shape_target_context_abs | hardneg4_other1_c025 | loo_pair_context | 132 | 6 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.057657711 | 0.057657711 | 0.034022603 | 0.042103525 | True | 0 | 0 |
| shape_target_context_abs | hardneg8_other025_c025 | loo_pair_context | 132 | 6 | 0.973544974 | 0.791666667 | 0.666666667 | 0.666666667 | 0.155756978 | 0.155756978 | 0.050242255 | 0.066711182 | True | 0 | 0 |
| shape_target_context_abs | plain_logit_c025 | loo_pair_context | 132 | 6 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.057657711 | 0.057657711 | 0.041220460 | 0.054290620 | True | 0 | 0 |
| shape_target_context_abs | hardneg4_other1_c025 | loo_pair_id | 132 | 6 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.057657711 | 0.057657711 | 0.034022603 | 0.042103525 | True | 0 | 0 |
| shape_target_context_abs | hardneg8_other025_c025 | loo_pair_id | 132 | 6 | 0.973544974 | 0.791666667 | 0.666666667 | 0.666666667 | 0.155756978 | 0.155756978 | 0.050242255 | 0.066711182 | True | 0 | 0 |
| shape_target_context_abs | plain_logit_c025 | loo_pair_id | 132 | 6 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.057657711 | 0.057657711 | 0.041220460 | 0.054290620 | True | 0 | 0 |
| shape_target_context_abs | hardneg8_other025_c025 | loo_any_file | 242 | 6 | 0.946327684 | 0.712121212 | 0.666666667 | 0.666666667 | 0.218092686 | 0.218841316 | 0.049165197 | 0.110233654 | False | 22 | 6 |
| all_abs | hardneg4_other1_c025 | loo_pair_context | 132 | 6 | 0.925925926 | 0.725490196 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003090902 | 0.010820132 | False | 0 | 0 |
| all_abs | hardneg8_other025_c025 | loo_pair_context | 132 | 6 | 0.915343915 | 0.719298246 | 0.666666667 | 0.666666667 | 0.824222642 | 0.824222642 | 0.007406108 | 0.030794307 | False | 0 | 0 |
| all_abs | plain_logit_c025 | loo_pair_context | 132 | 6 | 0.925925926 | 0.725490196 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003282593 | 0.010850806 | False | 0 | 0 |
| all_abs | prototype_pos_vs_boundary | loo_pair_context | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000027203 | 0.035165219 | False | 2 | 0 |
| shape_target_context_abs | prototype_pos_vs_boundary | loo_pair_context | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000719323 | 0.044915997 | False | 2 | 0 |
| shape_target_context_support_abs | hardneg4_other1_c025 | loo_pair_context | 132 | 6 | 0.925925926 | 0.725490196 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003090902 | 0.010820132 | False | 0 | 0 |
| shape_target_context_support_abs | hardneg8_other025_c025 | loo_pair_context | 132 | 6 | 0.915343915 | 0.719298246 | 0.666666667 | 0.666666667 | 0.824222642 | 0.824222642 | 0.007406108 | 0.030794307 | False | 0 | 0 |
| shape_target_context_support_abs | plain_logit_c025 | loo_pair_context | 132 | 6 | 0.925925926 | 0.725490196 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003282593 | 0.010850806 | False | 0 | 0 |
| shape_target_context_support_abs | prototype_pos_vs_boundary | loo_pair_context | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000027203 | 0.035165219 | False | 2 | 0 |
| support_abs | hardneg4_other1_c025 | loo_pair_context | 132 | 6 | 0.857142857 | 0.700000000 | 0.666666667 | 0.666666667 | 0.785757596 | 0.785757596 | 0.001425834 | 0.034691156 | False | 0 | 0 |
| support_abs | hardneg8_other025_c025 | loo_pair_context | 132 | 6 | 0.841269841 | 0.696969697 | 0.666666667 | 0.666666667 | 0.839112158 | 0.839112158 | 0.004570692 | 0.107668446 | False | 0 | 0 |
| support_abs | plain_logit_c025 | loo_pair_context | 132 | 6 | 0.851851852 | 0.698924731 | 0.666666667 | 0.666666667 | 0.785757596 | 0.785757596 | 0.001419162 | 0.035383795 | False | 0 | 0 |
| support_abs | prototype_pos_vs_boundary | loo_pair_context | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000007258 | 0.042808908 | False | 2 | 0 |
| all_abs | hardneg4_other1_c025 | loo_pair_id | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003090902 | 0.010820132 | False | 0 | 0 |
| all_abs | hardneg8_other025_c025 | loo_pair_id | 132 | 6 | 0.915343915 | 0.719298246 | 0.666666667 | 0.666666667 | 0.824222642 | 0.824222642 | 0.007406108 | 0.030794307 | False | 0 | 0 |
| all_abs | plain_logit_c025 | loo_pair_id | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003282593 | 0.010850806 | False | 0 | 0 |
| all_abs | prototype_pos_vs_boundary | loo_pair_id | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000027203 | 0.034446724 | False | 2 | 0 |
| shape_target_context_abs | prototype_pos_vs_boundary | loo_pair_id | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000719323 | 0.042986735 | False | 2 | 0 |
| shape_target_context_support_abs | hardneg4_other1_c025 | loo_pair_id | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003090902 | 0.010820132 | False | 0 | 0 |
| shape_target_context_support_abs | hardneg8_other025_c025 | loo_pair_id | 132 | 6 | 0.915343915 | 0.719298246 | 0.666666667 | 0.666666667 | 0.824222642 | 0.824222642 | 0.007406108 | 0.030794307 | False | 0 | 0 |
| shape_target_context_support_abs | plain_logit_c025 | loo_pair_id | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.766101605 | 0.766101605 | 0.003282593 | 0.010850806 | False | 0 | 0 |
| shape_target_context_support_abs | prototype_pos_vs_boundary | loo_pair_id | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000027203 | 0.034446724 | False | 2 | 0 |
| support_abs | hardneg4_other1_c025 | loo_pair_id | 132 | 6 | 0.857142857 | 0.700000000 | 0.666666667 | 0.666666667 | 0.785757596 | 0.785757596 | 0.001425834 | 0.034691156 | False | 0 | 0 |
| support_abs | hardneg8_other025_c025 | loo_pair_id | 132 | 6 | 0.841269841 | 0.696969697 | 0.666666667 | 0.666666667 | 0.839112158 | 0.839112158 | 0.004570692 | 0.107668446 | False | 0 | 0 |
| support_abs | plain_logit_c025 | loo_pair_id | 132 | 6 | 0.851851852 | 0.698924731 | 0.666666667 | 0.666666667 | 0.785757596 | 0.785757596 | 0.001419162 | 0.035383795 | False | 0 | 0 |
| support_abs | prototype_pos_vs_boundary | loo_pair_id | 130 | 6 | 0.666666667 | 0.682051282 | 0.666666667 | 0.666666667 |  |  | 0.000007258 | 0.042386755 | False | 2 | 0 |

## Pair-LOO Clean Boundary Rows

| feature_view | score_spec | auc | avg_precision | topk_precision | topk_recall | exact_e95_e101_mean_prob | exact_e95_e101_max_prob | e72_positive_min_prob | non_e72_p95_prob |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_target_context_abs | hardneg4_other1_c025 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.057657711 | 0.057657711 | 0.034022603 | 0.042103525 |
| shape_target_context_abs | hardneg8_other025_c025 | 0.973544974 | 0.791666667 | 0.666666667 | 0.666666667 | 0.155756978 | 0.155756978 | 0.050242255 | 0.066711182 |
| shape_target_context_abs | plain_logit_c025 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.057657711 | 0.057657711 | 0.041220460 | 0.054290620 |

## Positive Context Holdouts

| feature_view | score_spec | heldout | n | mean_prob | min_prob |
| --- | --- | --- | --- | --- | --- |
| all_abs | hardneg4_other1_c025 | e101__e72 | 2 | 0.943201948 | 0.943201948 |
| all_abs | hardneg4_other1_c025 | e72__e95 | 2 | 0.946830301 | 0.946830301 |
| all_abs | hardneg4_other1_c025 | e72__mixmin | 2 | 0.003090902 | 0.003090902 |
| all_abs | hardneg8_other025_c025 | e101__e72 | 2 | 0.951421005 | 0.951421005 |
| all_abs | hardneg8_other025_c025 | e72__e95 | 2 | 0.957117405 | 0.957117405 |
| all_abs | hardneg8_other025_c025 | e72__mixmin | 2 | 0.007406108 | 0.007406108 |
| all_abs | plain_logit_c025 | e101__e72 | 2 | 0.943334178 | 0.943334178 |
| all_abs | plain_logit_c025 | e72__e95 | 2 | 0.944317278 | 0.944317278 |
| all_abs | plain_logit_c025 | e72__mixmin | 2 | 0.003282593 | 0.003282593 |
| all_abs | prototype_pos_vs_boundary | e101__e72 | 2 | 0.998919997 | 0.998919997 |
| all_abs | prototype_pos_vs_boundary | e72__e95 | 2 | 0.999323401 | 0.999323401 |
| all_abs | prototype_pos_vs_boundary | e72__mixmin | 2 | 0.000027203 | 0.000027203 |
| shape_target_context_abs | hardneg4_other1_c025 | e101__e72 | 2 | 0.879987293 | 0.879987293 |
| shape_target_context_abs | hardneg4_other1_c025 | e72__e95 | 2 | 0.898033519 | 0.898033519 |
| shape_target_context_abs | hardneg4_other1_c025 | e72__mixmin | 2 | 0.034022603 | 0.034022603 |
| shape_target_context_abs | hardneg8_other025_c025 | e101__e72 | 2 | 0.898919551 | 0.898919551 |
| shape_target_context_abs | hardneg8_other025_c025 | e72__e95 | 2 | 0.914875281 | 0.914875281 |
| shape_target_context_abs | hardneg8_other025_c025 | e72__mixmin | 2 | 0.050242255 | 0.050242255 |
| shape_target_context_abs | plain_logit_c025 | e101__e72 | 2 | 0.880309034 | 0.880309034 |
| shape_target_context_abs | plain_logit_c025 | e72__e95 | 2 | 0.895674981 | 0.895674981 |
| shape_target_context_abs | plain_logit_c025 | e72__mixmin | 2 | 0.041220460 | 0.041220460 |
| shape_target_context_abs | prototype_pos_vs_boundary | e101__e72 | 2 | 0.992549220 | 0.992549220 |
| shape_target_context_abs | prototype_pos_vs_boundary | e72__e95 | 2 | 0.993166082 | 0.993166082 |
| shape_target_context_abs | prototype_pos_vs_boundary | e72__mixmin | 2 | 0.000719323 | 0.000719323 |
| shape_target_context_support_abs | hardneg4_other1_c025 | e101__e72 | 2 | 0.943201948 | 0.943201948 |
| shape_target_context_support_abs | hardneg4_other1_c025 | e72__e95 | 2 | 0.946830301 | 0.946830301 |
| shape_target_context_support_abs | hardneg4_other1_c025 | e72__mixmin | 2 | 0.003090902 | 0.003090902 |
| shape_target_context_support_abs | hardneg8_other025_c025 | e101__e72 | 2 | 0.951421005 | 0.951421005 |
| shape_target_context_support_abs | hardneg8_other025_c025 | e72__e95 | 2 | 0.957117405 | 0.957117405 |
| shape_target_context_support_abs | hardneg8_other025_c025 | e72__mixmin | 2 | 0.007406108 | 0.007406108 |
| shape_target_context_support_abs | plain_logit_c025 | e101__e72 | 2 | 0.943334178 | 0.943334178 |
| shape_target_context_support_abs | plain_logit_c025 | e72__e95 | 2 | 0.944317278 | 0.944317278 |
| shape_target_context_support_abs | plain_logit_c025 | e72__mixmin | 2 | 0.003282593 | 0.003282593 |
| shape_target_context_support_abs | prototype_pos_vs_boundary | e101__e72 | 2 | 0.998919997 | 0.998919997 |
| shape_target_context_support_abs | prototype_pos_vs_boundary | e72__e95 | 2 | 0.999323401 | 0.999323401 |
| shape_target_context_support_abs | prototype_pos_vs_boundary | e72__mixmin | 2 | 0.000027203 | 0.000027203 |
| support_abs | hardneg4_other1_c025 | e101__e72 | 2 | 0.903773657 | 0.903773657 |
| support_abs | hardneg4_other1_c025 | e72__e95 | 2 | 0.903871612 | 0.903871612 |
| support_abs | hardneg4_other1_c025 | e72__mixmin | 2 | 0.001425834 | 0.001425834 |
| support_abs | hardneg8_other025_c025 | e101__e72 | 2 | 0.919954945 | 0.919954945 |
| support_abs | hardneg8_other025_c025 | e72__e95 | 2 | 0.924467286 | 0.924467286 |
| support_abs | hardneg8_other025_c025 | e72__mixmin | 2 | 0.004570692 | 0.004570692 |
| support_abs | plain_logit_c025 | e101__e72 | 2 | 0.903799452 | 0.903799452 |
| support_abs | plain_logit_c025 | e72__e95 | 2 | 0.898510519 | 0.898510519 |
| support_abs | plain_logit_c025 | e72__mixmin | 2 | 0.001419162 | 0.001419162 |
| support_abs | prototype_pos_vs_boundary | e101__e72 | 2 | 0.908086905 | 0.908086905 |
| support_abs | prototype_pos_vs_boundary | e72__e95 | 2 | 0.929813691 | 0.929813691 |
| support_abs | prototype_pos_vs_boundary | e72__mixmin | 2 | 0.000007258 | 0.000007258 |

## Live Branch Scores

| feature_view | score_spec | candidate | scenario_count | contam_prob_mean | contam_prob_max | above_non_e72_p95_rate | above_min_positive_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shape_target_context_abs | hardneg4_other1_c025 | e144 | 3 | 0.025852005 | 0.045202656 | 0.666666667 | 0.000000000 |
| shape_target_context_abs | hardneg4_other1_c025 | e154 | 3 | 0.006746120 | 0.009377265 | 0.000000000 | 0.000000000 |
| shape_target_context_abs | hardneg4_other1_c025 | e176 | 3 | 0.000005742 | 0.000007980 | 0.000000000 | 0.000000000 |
| shape_target_context_abs | hardneg8_other025_c025 | e144 | 3 | 0.079557181 | 0.132977950 | 1.000000000 | 0.000000000 |
| shape_target_context_abs | hardneg8_other025_c025 | e154 | 3 | 0.025870726 | 0.035229211 | 0.000000000 | 0.000000000 |
| shape_target_context_abs | hardneg8_other025_c025 | e176 | 3 | 0.000043239 | 0.000062714 | 0.000000000 | 0.000000000 |
| shape_target_context_abs | plain_logit_c025 | e144 | 3 | 0.022666445 | 0.038722729 | 0.333333333 | 0.000000000 |
| shape_target_context_abs | plain_logit_c025 | e154 | 3 | 0.005852728 | 0.007972735 | 0.000000000 | 0.000000000 |
| shape_target_context_abs | plain_logit_c025 | e176 | 3 | 0.000006316 | 0.000008338 | 0.000000000 | 0.000000000 |

## Interpretation

- Passing pair-LOO is necessary but not sufficient, because all E72-positive
  examples still share one anchor file.
- If support-containing clean rows exist only by aggressively downweighting
  non-boundary negatives, they are narrow contrastive diagnostics rather than
  deployable gates.
- A deployable support gate still needs E72-heldout or one-class calibration;
  this experiment only tests whether the exact E95/E101 false positive can be
  controlled at all.

## Decision

No submission is created. Use this as an E72/support diagnostic only.
