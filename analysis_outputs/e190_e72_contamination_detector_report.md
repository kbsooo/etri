# E190 E72 Contamination Detector

## Question

E189 localized support's useful E95-edge wins to E72-neighbor rows. Can a
filename-free movement representation detect that contamination, or was the
support gate just known-file identity?

## Result In One Sentence

Best E72-neighbor detection under pair-LOO is `shape_target_context_abs` pair-LOO AUC `0.979`, AP `0.810`, top-k recall `0.667`, but file-LOO
cannot hold out E72 itself because all positive labels contain E72; therefore
the detector is a diagnostic, not yet a deployable live gate.

## E72-Neighbor Detection Summary

| task | feature_view | split | n_rows | n_pos | auc | avg_precision | topk_precision | topk_recall | exact_e95_e101_mean_prob | skipped_rows | skipped_positive_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e72_frontier_neighbor | shape_target_context_abs | loo_any_file | 242 | 6 | 0.974576271 | 0.750000000 | 0.666666667 | 0.666666667 | 0.263135746 | 22 | 6.000000000 |
| e72_frontier_neighbor | shape_target_context_support_abs | loo_any_file | 242 | 6 | 0.943502825 | 0.710144928 | 0.666666667 | 0.666666667 | 0.971763450 | 22 | 6.000000000 |
| e72_frontier_neighbor | all_axis_free_abs | loo_any_file | 242 | 6 | 0.943502825 | 0.710144928 | 0.666666667 | 0.666666667 | 0.971763450 | 22 | 6.000000000 |
| e72_frontier_neighbor | all_abs | loo_any_file | 242 | 6 | 0.943502825 | 0.710144928 | 0.666666667 | 0.666666667 | 0.971763450 | 22 | 6.000000000 |
| e72_frontier_neighbor | support_abs | loo_any_file | 242 | 6 | 0.870056497 | 0.687074830 | 0.666666667 | 0.666666667 | 0.975040441 | 22 | 6.000000000 |
| e72_frontier_neighbor | shape_target_context_abs | loo_base_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.113544369 | 0 |  |
| e72_frontier_neighbor | support_abs | loo_base_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.082685357 | 0 |  |
| e72_frontier_neighbor | shape_target_context_support_abs | loo_base_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.070253330 | 0 |  |
| e72_frontier_neighbor | all_axis_free_abs | loo_base_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.070253330 | 0 |  |
| e72_frontier_neighbor | all_abs | loo_base_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.070253330 | 0 |  |
| e72_frontier_neighbor | shape_target_context_abs | loo_new_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.113544369 | 0 |  |
| e72_frontier_neighbor | support_abs | loo_new_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.082685357 | 0 |  |
| e72_frontier_neighbor | shape_target_context_support_abs | loo_new_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.070253330 | 0 |  |
| e72_frontier_neighbor | all_axis_free_abs | loo_new_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.070253330 | 0 |  |
| e72_frontier_neighbor | all_abs | loo_new_file | 132 | 6 | 1.000000000 | 1.000000000 | 1.000000000 | 1.000000000 | 0.070253330 | 0 |  |
| e72_frontier_neighbor | shape_target_context_abs | loo_pair_context | 132 | 6 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.161306239 | 0 |  |
| e72_frontier_neighbor | shape_target_context_support_abs | loo_pair_context | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.957369024 | 0 |  |
| e72_frontier_neighbor | all_axis_free_abs | loo_pair_context | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.957369024 | 0 |  |
| e72_frontier_neighbor | all_abs | loo_pair_context | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.957369024 | 0 |  |
| e72_frontier_neighbor | support_abs | loo_pair_context | 132 | 6 | 0.867724868 | 0.702380952 | 0.666666667 | 0.666666667 | 0.967965256 | 0 |  |
| e72_frontier_neighbor | shape_target_context_abs | loo_pair_id | 132 | 6 | 0.978835979 | 0.809523810 | 0.666666667 | 0.666666667 | 0.161306239 | 0 |  |
| e72_frontier_neighbor | shape_target_context_support_abs | loo_pair_id | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.957369024 | 0 |  |
| e72_frontier_neighbor | all_axis_free_abs | loo_pair_id | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.957369024 | 0 |  |
| e72_frontier_neighbor | all_abs | loo_pair_id | 132 | 6 | 0.931216931 | 0.729166667 | 0.666666667 | 0.666666667 | 0.957369024 | 0 |  |
| e72_frontier_neighbor | support_abs | loo_pair_id | 132 | 6 | 0.867724868 | 0.702380952 | 0.666666667 | 0.666666667 | 0.967965256 | 0 |  |

## Support-Needed E95-Edge Summary

| task | feature_view | split | n_rows | n_pos | auc | avg_precision | topk_precision | topk_recall | exact_e95_e101_mean_prob | skipped_rows | skipped_positive_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| support_needed_e95_edge | shape_target_context_abs | loo_heldout | 4 | 0 |  |  |  |  | 0.051377410 | 6 |  |
| support_needed_e95_edge | support_abs | loo_heldout | 4 | 0 |  |  |  |  | 0.018213455 | 6 |  |
| support_needed_e95_edge | shape_target_context_support_abs | loo_heldout | 4 | 0 |  |  |  |  | 0.015200379 | 6 |  |
| support_needed_e95_edge | all_axis_free_abs | loo_heldout | 4 | 0 |  |  |  |  | 0.015200379 | 6 |  |
| support_needed_e95_edge | all_abs | loo_heldout | 4 | 0 |  |  |  |  | 0.015200379 | 6 |  |
| support_needed_e95_edge | shape_target_context_abs | loo_pair_context | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | support_abs | loo_pair_context | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | shape_target_context_support_abs | loo_pair_context | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | all_axis_free_abs | loo_pair_context | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | all_abs | loo_pair_context | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | shape_target_context_abs | loo_pair_id | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | support_abs | loo_pair_id | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | shape_target_context_support_abs | loo_pair_id | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | all_axis_free_abs | loo_pair_id | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |
| support_needed_e95_edge | all_abs | loo_pair_id | 6 | 6 |  |  | 1.000000000 | 1.000000000 |  | 4 |  |

## Positive Context Holdouts

| feature_view | heldout | n | mean_prob | min_prob | max_prob |
| --- | --- | --- | --- | --- | --- |
| all_abs | e101__e72 | 2 | 0.995720993 | 0.995720993 | 0.995720993 |
| all_abs | e72__e95 | 2 | 0.995792994 | 0.995792994 | 0.995792994 |
| all_abs | e72__mixmin | 2 | 0.008060637 | 0.008060637 | 0.008060637 |
| all_axis_free_abs | e101__e72 | 2 | 0.995720993 | 0.995720993 | 0.995720993 |
| all_axis_free_abs | e72__e95 | 2 | 0.995792994 | 0.995792994 | 0.995792994 |
| all_axis_free_abs | e72__mixmin | 2 | 0.008060637 | 0.008060637 | 0.008060637 |
| shape_target_context_abs | e101__e72 | 2 | 0.990353969 | 0.990353969 | 0.990353969 |
| shape_target_context_abs | e72__e95 | 2 | 0.992196547 | 0.992196547 | 0.992196547 |
| shape_target_context_abs | e72__mixmin | 2 | 0.147339478 | 0.147339478 | 0.147339478 |
| shape_target_context_support_abs | e101__e72 | 2 | 0.995720993 | 0.995720993 | 0.995720993 |
| shape_target_context_support_abs | e72__e95 | 2 | 0.995792994 | 0.995792994 | 0.995792994 |
| shape_target_context_support_abs | e72__mixmin | 2 | 0.008060637 | 0.008060637 | 0.008060637 |
| support_abs | e101__e72 | 2 | 0.992571283 | 0.992571283 | 0.992571283 |
| support_abs | e72__e95 | 2 | 0.992026046 | 0.992026046 | 0.992026046 |
| support_abs | e72__mixmin | 2 | 0.002989376 | 0.002989376 | 0.002989376 |

## Exact E95/E101 False Positive Check

| feature_view | exact_e95_e101_mean_prob | exact_e95_e101_max_prob |
| --- | --- | --- |
| all_abs | 0.957369024 | 0.957369024 |
| all_axis_free_abs | 0.957369024 | 0.957369024 |
| shape_target_context_abs | 0.161306239 | 0.161306239 |
| shape_target_context_support_abs | 0.957369024 | 0.957369024 |
| support_abs | 0.967965256 | 0.967965256 |

## Live Pressure Branch Contamination Scores

| feature_view | candidate | scenario_count | contam_prob_mean | contam_prob_max | above_non_e72_p95_rate | above_min_positive_rate | support_minus_shape_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all_abs | e144 | 3 | 0.001063073 | 0.001562159 | 0.000000000 | 0.000000000 | -0.010505932 |
| all_abs | e154 | 3 | 0.002154108 | 0.003033256 | 0.000000000 | 0.000000000 | 0.000695761 |
| all_abs | e176 | 3 | 0.000178492 | 0.000223050 | 0.000000000 | 0.000000000 | -0.109429427 |
| all_axis_free_abs | e144 | 3 | 0.001063073 | 0.001562159 | 0.000000000 | 0.000000000 | -0.010505932 |
| all_axis_free_abs | e154 | 3 | 0.002154108 | 0.003033256 | 0.000000000 | 0.000000000 | 0.000695761 |
| all_axis_free_abs | e176 | 3 | 0.000178492 | 0.000223050 | 0.000000000 | 0.000000000 | -0.109429427 |
| shape_target_context_abs | e144 | 3 | 0.073884999 | 0.134665403 | 0.666666667 | 0.000000000 | -0.010505932 |
| shape_target_context_abs | e154 | 3 | 0.016034876 | 0.023510557 | 0.000000000 | 0.000000000 | 0.000695761 |
| shape_target_context_abs | e176 | 3 | 0.000003558 | 0.000005037 | 0.000000000 | 0.000000000 | -0.109429427 |
| shape_target_context_support_abs | e144 | 3 | 0.001063073 | 0.001562159 | 0.000000000 | 0.000000000 | -0.010505932 |
| shape_target_context_support_abs | e154 | 3 | 0.002154108 | 0.003033256 | 0.000000000 | 0.000000000 | 0.000695761 |
| shape_target_context_support_abs | e176 | 3 | 0.000178492 | 0.000223050 | 0.000000000 | 0.000000000 | -0.109429427 |
| support_abs | e144 | 3 | 0.000315395 | 0.000498444 | 0.000000000 | 0.000000000 | -0.010505932 |
| support_abs | e154 | 3 | 0.002026370 | 0.002422502 | 0.000000000 | 0.000000000 | 0.000695761 |
| support_abs | e176 | 3 | 0.002206860 | 0.002620166 | 0.000000000 | 0.000000000 | -0.109429427 |

## Top Branch Rows

| feature_view | candidate | scenario | e72_contam_prob | known_non_e72_p95 | known_min_positive | above_non_e72_p95 | above_min_positive | shape_prob | support_prob | support_minus_shape_prob | top_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_abs | e154 | global_t010 | 0.003033256 | 0.014775788 | 0.990999795 | False | False | 0.001369363 | 0.000940115 | -0.000429248 | Q3,Q3,Q3,Q3 |
| all_abs | e154 | global_t010_subject_t020 | 0.002137143 | 0.014775788 | 0.990999795 | False | False | 0.001644717 | 0.001267870 | -0.000376846 | Q3,Q3,Q3,Q3 |
| all_abs | e144 | global_t010_subject_t020 | 0.001562159 | 0.014775788 | 0.990999795 | False | False | 0.017316907 | 0.002241587 | -0.015075320 | S2,Q1,Q1,Q3 |
| all_abs | e154 | global_t010_subject_t010 | 0.001291925 | 0.014775788 | 0.990999795 | False | False | 0.001816185 | 0.004709562 | 0.002893377 | Q3,Q3,Q3,Q3 |
| all_abs | e144 | global_t010 | 0.001274160 | 0.014775788 | 0.990999795 | False | False | 0.026081579 | 0.008419755 | -0.017661824 | S2,Q1,Q3,Q1 |
| all_abs | e144 | global_t010_subject_t010 | 0.000352900 | 0.014775788 | 0.990999795 | False | False | 0.005881782 | 0.007101130 | 0.001219348 | Q1,Q1,Q1,Q3 |
| all_abs | e176 | global_t010 | 0.000223050 | 0.014775788 | 0.990999795 | False | False | 0.920864017 | 0.820110603 | -0.100753415 | S1,Q3,Q3,Q3 |
| all_abs | e176 | global_t010_subject_t020 | 0.000193767 | 0.014775788 | 0.990999795 | False | False | 0.923508519 | 0.754047547 | -0.169460973 | S1,Q3,Q3,Q3 |
| all_abs | e176 | global_t010_subject_t010 | 0.000118659 | 0.014775788 | 0.990999795 | False | False | 0.933324089 | 0.875250196 | -0.058073893 | S1,Q3,Q3,Q3 |
| all_axis_free_abs | e154 | global_t010 | 0.003033256 | 0.014775788 | 0.990999795 | False | False | 0.001369363 | 0.000940115 | -0.000429248 | Q3,Q3,Q3,Q3 |
| all_axis_free_abs | e154 | global_t010_subject_t020 | 0.002137143 | 0.014775788 | 0.990999795 | False | False | 0.001644717 | 0.001267870 | -0.000376846 | Q3,Q3,Q3,Q3 |
| all_axis_free_abs | e144 | global_t010_subject_t020 | 0.001562159 | 0.014775788 | 0.990999795 | False | False | 0.017316907 | 0.002241587 | -0.015075320 | S2,Q1,Q1,Q3 |
| all_axis_free_abs | e154 | global_t010_subject_t010 | 0.001291925 | 0.014775788 | 0.990999795 | False | False | 0.001816185 | 0.004709562 | 0.002893377 | Q3,Q3,Q3,Q3 |
| all_axis_free_abs | e144 | global_t010 | 0.001274160 | 0.014775788 | 0.990999795 | False | False | 0.026081579 | 0.008419755 | -0.017661824 | S2,Q1,Q3,Q1 |
| all_axis_free_abs | e144 | global_t010_subject_t010 | 0.000352900 | 0.014775788 | 0.990999795 | False | False | 0.005881782 | 0.007101130 | 0.001219348 | Q1,Q1,Q1,Q3 |
| all_axis_free_abs | e176 | global_t010 | 0.000223050 | 0.014775788 | 0.990999795 | False | False | 0.920864017 | 0.820110603 | -0.100753415 | S1,Q3,Q3,Q3 |
| all_axis_free_abs | e176 | global_t010_subject_t020 | 0.000193767 | 0.014775788 | 0.990999795 | False | False | 0.923508519 | 0.754047547 | -0.169460973 | S1,Q3,Q3,Q3 |
| all_axis_free_abs | e176 | global_t010_subject_t010 | 0.000118659 | 0.014775788 | 0.990999795 | False | False | 0.933324089 | 0.875250196 | -0.058073893 | S1,Q3,Q3,Q3 |
| shape_target_context_abs | e144 | global_t010_subject_t020 | 0.134665403 | 0.054051995 | 0.976955975 | True | False | 0.017316907 | 0.002241587 | -0.015075320 | S2,Q1,Q1,Q3 |
| shape_target_context_abs | e144 | global_t010 | 0.056837012 | 0.054051995 | 0.976955975 | True | False | 0.026081579 | 0.008419755 | -0.017661824 | S2,Q1,Q3,Q1 |
| shape_target_context_abs | e144 | global_t010_subject_t010 | 0.030152582 | 0.054051995 | 0.976955975 | False | False | 0.005881782 | 0.007101130 | 0.001219348 | Q1,Q1,Q1,Q3 |
| shape_target_context_abs | e154 | global_t010 | 0.023510557 | 0.054051995 | 0.976955975 | False | False | 0.001369363 | 0.000940115 | -0.000429248 | Q3,Q3,Q3,Q3 |
| shape_target_context_abs | e154 | global_t010_subject_t020 | 0.014010396 | 0.054051995 | 0.976955975 | False | False | 0.001644717 | 0.001267870 | -0.000376846 | Q3,Q3,Q3,Q3 |
| shape_target_context_abs | e154 | global_t010_subject_t010 | 0.010583675 | 0.054051995 | 0.976955975 | False | False | 0.001816185 | 0.004709562 | 0.002893377 | Q3,Q3,Q3,Q3 |
| shape_target_context_abs | e176 | global_t010 | 0.000005037 | 0.054051995 | 0.976955975 | False | False | 0.920864017 | 0.820110603 | -0.100753415 | S1,Q3,Q3,Q3 |
| shape_target_context_abs | e176 | global_t010_subject_t020 | 0.000003149 | 0.054051995 | 0.976955975 | False | False | 0.923508519 | 0.754047547 | -0.169460973 | S1,Q3,Q3,Q3 |
| shape_target_context_abs | e176 | global_t010_subject_t010 | 0.000002489 | 0.054051995 | 0.976955975 | False | False | 0.933324089 | 0.875250196 | -0.058073893 | S1,Q3,Q3,Q3 |
| shape_target_context_support_abs | e154 | global_t010 | 0.003033256 | 0.014775788 | 0.990999795 | False | False | 0.001369363 | 0.000940115 | -0.000429248 | Q3,Q3,Q3,Q3 |
| shape_target_context_support_abs | e154 | global_t010_subject_t020 | 0.002137143 | 0.014775788 | 0.990999795 | False | False | 0.001644717 | 0.001267870 | -0.000376846 | Q3,Q3,Q3,Q3 |
| shape_target_context_support_abs | e144 | global_t010_subject_t020 | 0.001562159 | 0.014775788 | 0.990999795 | False | False | 0.017316907 | 0.002241587 | -0.015075320 | S2,Q1,Q1,Q3 |
| shape_target_context_support_abs | e154 | global_t010_subject_t010 | 0.001291925 | 0.014775788 | 0.990999795 | False | False | 0.001816185 | 0.004709562 | 0.002893377 | Q3,Q3,Q3,Q3 |
| shape_target_context_support_abs | e144 | global_t010 | 0.001274160 | 0.014775788 | 0.990999795 | False | False | 0.026081579 | 0.008419755 | -0.017661824 | S2,Q1,Q3,Q1 |
| shape_target_context_support_abs | e144 | global_t010_subject_t010 | 0.000352900 | 0.014775788 | 0.990999795 | False | False | 0.005881782 | 0.007101130 | 0.001219348 | Q1,Q1,Q1,Q3 |
| shape_target_context_support_abs | e176 | global_t010 | 0.000223050 | 0.014775788 | 0.990999795 | False | False | 0.920864017 | 0.820110603 | -0.100753415 | S1,Q3,Q3,Q3 |
| shape_target_context_support_abs | e176 | global_t010_subject_t020 | 0.000193767 | 0.014775788 | 0.990999795 | False | False | 0.923508519 | 0.754047547 | -0.169460973 | S1,Q3,Q3,Q3 |
| shape_target_context_support_abs | e176 | global_t010_subject_t010 | 0.000118659 | 0.014775788 | 0.990999795 | False | False | 0.933324089 | 0.875250196 | -0.058073893 | S1,Q3,Q3,Q3 |
| support_abs | e176 | global_t010_subject_t020 | 0.002620166 | 0.046836547 | 0.987024306 | False | False | 0.923508519 | 0.754047547 | -0.169460973 | S1,Q3,Q3,Q3 |
| support_abs | e154 | global_t010 | 0.002422502 | 0.046836547 | 0.987024306 | False | False | 0.001369363 | 0.000940115 | -0.000429248 | Q3,Q3,Q3,Q3 |
| support_abs | e176 | global_t010 | 0.002408185 | 0.046836547 | 0.987024306 | False | False | 0.920864017 | 0.820110603 | -0.100753415 | S1,Q3,Q3,Q3 |
| support_abs | e154 | global_t010_subject_t020 | 0.002257655 | 0.046836547 | 0.987024306 | False | False | 0.001644717 | 0.001267870 | -0.000376846 | Q3,Q3,Q3,Q3 |
| support_abs | e176 | global_t010_subject_t010 | 0.001592229 | 0.046836547 | 0.987024306 | False | False | 0.933324089 | 0.875250196 | -0.058073893 | S1,Q3,Q3,Q3 |
| support_abs | e154 | global_t010_subject_t010 | 0.001398953 | 0.046836547 | 0.987024306 | False | False | 0.001816185 | 0.004709562 | 0.002893377 | Q3,Q3,Q3,Q3 |
| support_abs | e144 | global_t010 | 0.000498444 | 0.046836547 | 0.987024306 | False | False | 0.026081579 | 0.008419755 | -0.017661824 | S2,Q1,Q3,Q1 |
| support_abs | e144 | global_t010_subject_t020 | 0.000304883 | 0.046836547 | 0.987024306 | False | False | 0.017316907 | 0.002241587 | -0.015075320 | S2,Q1,Q1,Q3 |
| support_abs | e144 | global_t010_subject_t010 | 0.000142859 | 0.046836547 | 0.987024306 | False | False | 0.005881782 | 0.007101130 | 0.001219348 | Q1,Q1,Q1,Q3 |

## Top Structural Features

| task | feature | auc_abs_directionless | signed_auc | positive_mean | negative_mean | mean_diff_pos_minus_neg |
| --- | --- | --- | --- | --- | --- | --- |
| e72_frontier_neighbor | abs__z__sup_all_prior_split_rate | 1.000000000 | 1.000000000 | 0.024240324 | 0.006352659 | 0.017887665 |
| e72_frontier_neighbor | abs__z__sup_between_prior_split_rate | 1.000000000 | 1.000000000 | 0.029649711 | 0.007178202 | 0.022471508 |
| e72_frontier_neighbor | abs__z__target_top16_Q2_support_swing | 0.984126984 | 0.984126984 | 1.000000000 | 0.181686666 | 0.818313334 |
| e72_frontier_neighbor | abs__z__sup_all_global_swing | 0.968253968 | 0.031746032 | 0.003168466 | 0.035072538 | -0.031904072 |
| e72_frontier_neighbor | abs__z__target_between_not_e72_Q1_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.160996034 | -0.160996034 |
| e72_frontier_neighbor | abs__z__target_between_not_e72_Q2_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.272298323 | -0.272298323 |
| e72_frontier_neighbor | abs__z__target_between_not_e72_Q3_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.290084848 | -0.290084848 |
| e72_frontier_neighbor | abs__z__target_between_not_e72_S4_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.232058388 | -0.232058388 |
| e72_frontier_neighbor | abs__z__target_not_e72_Q1_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.258057478 | -0.258057478 |
| e72_frontier_neighbor | abs__z__target_not_e72_Q2_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.309034626 | -0.309034626 |
| e72_frontier_neighbor | abs__z__target_not_e72_Q3_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.312371429 | -0.312371429 |
| e72_frontier_neighbor | abs__z__target_not_e72_S4_support_swing | 0.968253968 | 0.031746032 | 0.000000000 | 0.150223552 | -0.150223552 |
| e72_frontier_neighbor | abs__z__sup_between_not_e72_global_hard_rate | 0.965608466 | 0.034391534 | 0.014492754 | 0.115964189 | -0.101471436 |
| e72_frontier_neighbor | abs__z__sup_between_not_e72_global_mean | 0.965608466 | 0.034391534 | 0.002576490 | 0.029873788 | -0.027297299 |
| e72_frontier_neighbor | abs__z__sup_not_e72_global_hard_rate | 0.965608466 | 0.034391534 | 0.017316017 | 0.134800757 | -0.117484740 |
| e72_frontier_neighbor | abs__z__sup_top33_subject_mean | 0.962962963 | 0.962962963 | 0.372664108 | 0.166144724 | 0.206519384 |
| e72_frontier_neighbor | abs__z__sup_all_global_hard_rate | 0.957671958 | 0.042328042 | 0.012910561 | 0.107996462 | -0.095085901 |
| e72_frontier_neighbor | abs__z__sup_top16_visible_mean_swing | 0.952380952 | 0.952380952 | 0.494849001 | 0.229238141 | 0.265610860 |
| e72_frontier_neighbor | abs__z__target_between_not_e72_S3_support_swing | 0.952380952 | 0.047619048 | 0.000000000 | 0.470582769 | -0.470582769 |
| e72_frontier_neighbor | abs__z__target_not_e72_S3_support_swing | 0.952380952 | 0.047619048 | 0.000000000 | 0.485368676 | -0.485368676 |
| e72_frontier_neighbor | abs__z__sup_between_global_hard_rate | 0.947089947 | 0.052910053 | 0.034062783 | 0.097430228 | -0.063367445 |
| e72_frontier_neighbor | abs__z__sup_between_global_swing | 0.947089947 | 0.052910053 | 0.003459381 | 0.030428090 | -0.026968709 |
| e72_frontier_neighbor | abs__z__sup_top16_flank_mean_mean | 0.947089947 | 0.947089947 | 0.560967633 | 0.242753678 | 0.318213955 |
| e72_frontier_neighbor | abs__z__sup_top16_flank_mean_swing | 0.947089947 | 0.947089947 | 0.567235061 | 0.253615306 | 0.313619755 |
| e72_frontier_neighbor | abs__z__sup_top16_subject_mean | 0.947089947 | 0.947089947 | 0.523884855 | 0.219127603 | 0.304757252 |
| e72_frontier_neighbor | abs__z__sup_top16_subject_swing | 0.947089947 | 0.947089947 | 0.529639697 | 0.227222481 | 0.302417216 |
| e72_frontier_neighbor | abs__z__sup_top33_subject_swing | 0.947089947 | 0.947089947 | 0.384004384 | 0.176169496 | 0.207834888 |
| e72_frontier_neighbor | abs__z__sup_not_e72_global_mean | 0.944444444 | 0.055555556 | 0.003347763 | 0.032871312 | -0.029523549 |
| e72_frontier_neighbor | abs__z__sup_top16_visible_mean_mean | 0.941798942 | 0.941798942 | 0.489176696 | 0.215110478 | 0.274066218 |
| e72_frontier_neighbor | abs__z__sup_top16_focus_mean_swing | 0.931216931 | 0.931216931 | 0.398334254 | 0.198612229 | 0.199722025 |
| e72_frontier_neighbor | abs__z__shape_all_support_label_mean | 0.925925926 | 0.074074074 | 0.003249655 | 0.067086011 | -0.063836356 |
| e72_frontier_neighbor | abs__z__sup_top16_focus_mean_mean | 0.925925926 | 0.925925926 | 0.393455446 | 0.184767457 | 0.208687988 |
| e72_frontier_neighbor | abs__z__target_top33_Q1_support_swing | 0.920634921 | 0.079365079 | 0.000000000 | 0.565126349 | -0.565126349 |
| e72_frontier_neighbor | abs__z__shape_between_support_label_swing | 0.920634921 | 0.079365079 | 0.018008955 | 0.120506059 | -0.102497104 |
| e72_frontier_neighbor | abs__z__sup_all_global_mean | 0.910052910 | 0.089947090 | 0.008789145 | 0.022994169 | -0.014205024 |
| e72_frontier_neighbor | abs__z__sup_top16_all_prior_adverse_rate | 0.904761905 | 0.904761905 | 0.583333333 | 0.289682540 | 0.293650794 |
| e72_frontier_neighbor | abs__z__sup_between_not_e72_global_swing | 0.902116402 | 0.097883598 | 0.010551810 | 0.047214670 | -0.036662860 |
| e72_frontier_neighbor | abs__z__sup_top33_flank_mean_mean | 0.899470899 | 0.899470899 | 0.400446563 | 0.183180715 | 0.217265847 |
| e72_frontier_neighbor | abs__z__target_top33_Q2_support_swing | 0.899470899 | 0.899470899 | 0.781159768 | 0.185346940 | 0.595812828 |
| e72_frontier_neighbor | abs__z__shape_all_support_label_swing | 0.894179894 | 0.105820106 | 0.017018958 | 0.131574676 | -0.114555718 |
| e72_frontier_neighbor | abs__z__sup_top4_nearest_hard085_swing | 0.888888889 | 0.888888889 | 0.700000000 | 0.454774280 | 0.245225720 |
| e72_frontier_neighbor | abs__z__sup_top33_visible_mean_mean | 0.888888889 | 0.888888889 | 0.342821111 | 0.161807396 | 0.181013716 |
| e72_frontier_neighbor | abs__z__sup_top33_focus_mean_mean | 0.883597884 | 0.883597884 | 0.265987176 | 0.140698137 | 0.125289038 |
| e72_frontier_neighbor | abs__z__shape_between_not_e72_support_label_mean | 0.880952381 | 0.119047619 | 0.014492754 | 0.096831735 | -0.082338982 |
| e72_frontier_neighbor | abs__z__sup_top33_focus_mean_swing | 0.878306878 | 0.878306878 | 0.273230662 | 0.154069122 | 0.119161540 |
| e72_frontier_neighbor | abs__z__sup_top33_flank_mean_swing | 0.873015873 | 0.873015873 | 0.411203605 | 0.194127657 | 0.217075947 |
| e72_frontier_neighbor | abs__z__sup_top33_visible_mean_swing | 0.873015873 | 0.873015873 | 0.352072343 | 0.173602303 | 0.178470040 |
| e72_frontier_neighbor | abs__z__shape_not_e72_support_label_mean | 0.870370370 | 0.129629630 | 0.017316017 | 0.103652469 | -0.086336451 |
| e72_frontier_neighbor | abs__z__target_all_Q2_support_swing | 0.857142857 | 0.142857143 | 0.011360643 | 0.298393206 | -0.287032562 |
| e72_frontier_neighbor | abs__z__target_between_Q1_support_swing | 0.857142857 | 0.142857143 | 0.039850406 | 0.214644913 | -0.174794507 |
| e72_frontier_neighbor | abs__z__sup_all_flank_mean_hard_rate | 0.841269841 | 0.841269841 | 0.159099052 | 0.094420298 | 0.064678754 |
| e72_frontier_neighbor | abs__z__sup_all_visible_mean_hard_rate | 0.841269841 | 0.841269841 | 0.157079025 | 0.090483150 | 0.066595875 |
| e72_frontier_neighbor | abs__z__target_all_Q1_support_swing | 0.841269841 | 0.158730159 | 0.039259003 | 0.284166651 | -0.244907649 |
| e72_frontier_neighbor | abs__z__target_all_S4_support_swing | 0.841269841 | 0.841269841 | 0.325270376 | 0.152898264 | 0.172372112 |
| e72_frontier_neighbor | abs__z__target_top16_Q1_support_swing | 0.841269841 | 0.158730159 | 0.000000000 | 0.552335246 | -0.552335246 |
| e72_frontier_neighbor | abs__z__sup_all_subject_swing | 0.841269841 | 0.841269841 | 0.089004240 | 0.042927542 | 0.046076698 |
| e72_frontier_neighbor | abs__z__sup_not_e72_global_swing | 0.838624339 | 0.161375661 | 0.018165653 | 0.052785408 | -0.034619756 |
| e72_frontier_neighbor | abs__z__sup_all_flank_mean_swing | 0.830687831 | 0.830687831 | 0.116948640 | 0.061036043 | 0.055912597 |
| e72_frontier_neighbor | abs__z__sup_top16_all_prior_support_rate | 0.830687831 | 0.830687831 | 0.583333333 | 0.317460317 | 0.265873016 |
| e72_frontier_neighbor | abs__z__shape_between_not_e72_support_label_swing | 0.828042328 | 0.171957672 | 0.046543397 | 0.171652519 | -0.125109122 |
| e72_frontier_neighbor | abs__z__sup_all_nearest_hard085_hard_rate | 0.825396825 | 0.825396825 | 0.139645329 | 0.074273925 | 0.065371404 |
| e72_frontier_neighbor | abs__z__sup_all_nearest_hard085_mean | 0.825396825 | 0.825396825 | 0.097751731 | 0.051991748 | 0.045759983 |
| e72_frontier_neighbor | abs__z__target_top1_S2_support_swing | 0.825396825 | 0.825396825 | 0.666666667 | 0.015873016 | 0.650793651 |
| e72_frontier_neighbor | abs__z__sup_all_subject_mean | 0.820105820 | 0.820105820 | 0.064736178 | 0.038603760 | 0.026132418 |
| e72_frontier_neighbor | abs__z__sup_all_visible_mean_swing | 0.820105820 | 0.820105820 | 0.099108162 | 0.056593783 | 0.042514379 |
| e72_frontier_neighbor | abs__z__sup_top4_focus_mean_swing | 0.820105820 | 0.820105820 | 0.411427244 | 0.322738293 | 0.088688951 |
| e72_frontier_neighbor | abs__z__sup_all_flank_mean_mean | 0.809523810 | 0.809523810 | 0.084329642 | 0.044458873 | 0.039870769 |
| e72_frontier_neighbor | abs__z__target_all_S3_support_swing | 0.804232804 | 0.195767196 | 0.221008030 | 0.487773380 | -0.266765349 |
| e72_frontier_neighbor | abs__z__sup_between_nearest_hard085_hard_rate | 0.798941799 | 0.798941799 | 0.136718110 | 0.082406993 | 0.054311117 |
| e72_frontier_neighbor | abs__z__sup_between_nearest_hard085_mean | 0.798941799 | 0.798941799 | 0.095702677 | 0.057684895 | 0.038017782 |
| e72_frontier_neighbor | abs__z__sup_between_subject_swing | 0.798941799 | 0.798941799 | 0.081526058 | 0.052251630 | 0.029274429 |
| e72_frontier_neighbor | abs__z__sup_top4_focus_mean_mean | 0.798941799 | 0.798941799 | 0.411462501 | 0.312541281 | 0.098921220 |
| e72_frontier_neighbor | abs__z__sup_all_focus_mean_swing | 0.793650794 | 0.793650794 | 0.075320858 | 0.052590853 | 0.022730005 |
| e72_frontier_neighbor | abs__z__target_top33_S3_support_swing | 0.793650794 | 0.206349206 | 0.123115424 | 0.526272694 | -0.403157270 |
| e72_frontier_neighbor | abs__z__sup_all_nearest_hard085_swing | 0.788359788 | 0.788359788 | 0.138727099 | 0.090701213 | 0.048025886 |
| e72_frontier_neighbor | abs__z__sup_all_visible_mean_mean | 0.788359788 | 0.788359788 | 0.070145333 | 0.039040585 | 0.031104748 |
| e72_frontier_neighbor | abs__z__sup_top4_nearest_hard085_hard_rate | 0.785714286 | 0.785714286 | 1.000000000 | 0.634920635 | 0.365079365 |
| e72_frontier_neighbor | abs__z__sup_top4_nearest_hard085_mean | 0.785714286 | 0.785714286 | 0.700000000 | 0.444444444 | 0.255555556 |
| e72_frontier_neighbor | abs__z__target_top33_S4_support_swing | 0.785714286 | 0.214285714 | 0.000000000 | 0.510835287 | -0.510835287 |
| e72_frontier_neighbor | abs__z__target_top4_S2_support_swing | 0.780423280 | 0.780423280 | 0.004646529 | 0.063492063 | -0.058845534 |

## Interpretation

- There is movement-shape signal for E72-neighbor contamination under pair and
  non-E72 file holdouts.
- The strongest stress still has a blind spot: if the E72 file itself is held
  out, no positive examples remain. That means this is not a public-free law in
  the strictest sense; it is an E72-observation-derived diagnostic.
- A usable support gate must not only identify E72-neighbor anchors; it must
  keep exact E95/E101 probability low and score live pressure branches with a
  predeclared threshold.

## Decision

No submission is created. Support may be used as an E72-contamination diagnostic
only when a structural score is high and exact E95/E101 false-positive risk is
low. Current live branch scores remain evidence, not a gate.
