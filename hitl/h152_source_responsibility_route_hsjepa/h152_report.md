# H152 Source-Responsibility Row-Route HS-JEPA

Date: 2026-06-03

## Question

H149/H150 select source actions mostly at cell level. H152 asks whether the
decoder should instead assign one source-action route per row, then select a
target subset inside that route.

```text
row context -> source responsibility -> target route subset -> correction
```

## Route Specs

| name | max_cells | max_rows | max_per_subject | max_per_target | max_per_source | max_per_row_cells | amp | min_positive_variants | max_positive_delta | require_frontier_negative | require_no_pre_negative | description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_responsibility_upside | 430 | 165 | 112 | 96 | 150 | 5 | 0.640000000 | 8 | 0.000240000 | False | False | row-source route assignment with broad listener consensus |
| route_responsibility_consensus | 360 | 155 | 98 | 82 | 120 | 4 | 0.600000000 | 9 | 0.000120000 | False | True | source route must survive no-pre-H listener |
| route_responsibility_frontier_guard | 300 | 140 | 88 | 70 | 100 | 4 | 0.580000000 | 9 | 0.000060000 | True | True | route assignment only when frontier-only listener also agrees |

## Promoted Decision

| spec | description | local_path | hash | selected_routes | selected_cells | selected_rows | selected_source_mix | selected_target_mix | validation_path | validation_rows | validation_keys_match | validation_duplicate_keys | validation_nan_cells | validation_min_prob | validation_max_prob | validation_changed_cells_vs_h057_validation | validation_upload_safe | metric_changed_cells_vs_h057 | metric_changed_rows_vs_h057 | metric_move_l1 | metric_move_l2 | metric_h088_move_cosine | metric_all_full_pred_delta | metric_all_full_benefit_sum | metric_all_full_toxicity_sum | metric_no_pre_h_pred_delta | metric_no_pre_h_benefit_sum | metric_no_pre_h_toxicity_sum | metric_no_bad_pred_delta | metric_no_bad_benefit_sum | metric_no_bad_toxicity_sum | metric_frontier_only_pred_delta | metric_frontier_only_benefit_sum | metric_frontier_only_toxicity_sum | metric_no_human_social_pred_delta | metric_no_human_social_benefit_sum | metric_no_human_social_toxicity_sum | metric_no_subject_pred_delta | metric_no_subject_benefit_sum | metric_no_subject_toxicity_sum | metric_no_row_order_pred_delta | metric_no_row_order_benefit_sum | metric_no_row_order_toxicity_sum | metric_no_base_prob_pred_delta | metric_no_base_prob_benefit_sum | metric_no_base_prob_toxicity_sum | metric_structural_only_pred_delta | metric_structural_only_benefit_sum | metric_structural_only_toxicity_sum | metric_human_social_only_pred_delta | metric_human_social_only_benefit_sum | metric_human_social_only_toxicity_sum | metric_robust_positive_variant_count | metric_robust_mean_pred_delta | metric_robust_min_pred_delta | metric_robust_max_pred_delta | decision_score | root_uploadsafe_path | root_path | root_rows | root_keys_match | root_duplicate_keys | root_nan_cells | root_min_prob | root_max_prob | root_changed_cells_vs_h057_validation | root_upload_safe |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| route_responsibility_upside | row-source route assignment with broad listener consensus | /Users/kbsoo/Downloads/cl2/hitl/h152_source_responsibility_route_hsjepa/submission_h152_route_responsibility_upside_1e8b9fcc.csv | 1e8b9fcc | 159 | 363 | 159 | {'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 134, 'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 120, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 62, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 20, 'submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv': 16, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 6, 'submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv': 3, 'submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv': 2} | {'S3': 90, 'S1': 60, 'S4': 58, 'S2': 55, 'Q1': 36, 'Q2': 33, 'Q3': 31} | /Users/kbsoo/Downloads/cl2/hitl/h152_source_responsibility_route_hsjepa/submission_h152_route_responsibility_upside_1e8b9fcc.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 363 | True | 363 | 159 | 29.379744416 | 2.092114498 | 0.214751899 | -0.004841317 | 0.004841317 | 0.000000000 | -0.002474268 | 0.002569061 | 0.000094793 | -0.003263335 | 0.003417334 | 0.000153999 | -0.000381632 | 0.000755797 | 0.000374165 | -0.005201865 | 0.005261293 | 0.000059428 | -0.004739108 | 0.004791053 | 0.000051945 | -0.002053524 | 0.002137219 | 0.000083695 | -0.004983861 | 0.005008146 | 0.000024285 | -0.005201865 | 0.005261293 | 0.000059428 | -0.003589297 | 0.004476227 | 0.000886930 | 10 | -0.003673007 | -0.005201865 | -0.000381632 | 4.979343904 | /Users/kbsoo/Downloads/cl2/submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | /Users/kbsoo/Downloads/cl2/submission_h152_source_route_route_responsibility_upside_1e8b9fcc_uploadsafe.csv | 250.000000000 | True | 0.000000000 | 0.000000000 | 0.000004939 | 0.999996751 | 363.000000000 | True |
| route_responsibility_consensus | source route must survive no-pre-H listener | /Users/kbsoo/Downloads/cl2/hitl/h152_source_responsibility_route_hsjepa/submission_h152_route_responsibility_consensus_f5b28b01.csv | f5b28b01 | 138 | 328 | 138 | {'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 114, 'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 106, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 58, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 19, 'submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv': 18, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 6, 'submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv': 5, 'submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv': 2} | {'S3': 82, 'S2': 53, 'S1': 52, 'S4': 51, 'Q1': 33, 'Q2': 29, 'Q3': 28} | /Users/kbsoo/Downloads/cl2/hitl/h152_source_responsibility_route_hsjepa/submission_h152_route_responsibility_consensus_f5b28b01.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 328 | True | 328 | 138 | 24.398939594 | 1.863002639 | 0.212655989 | -0.003970392 | 0.003970392 | 0.000000000 | -0.002039603 | 0.002081982 | 0.000042379 | -0.002785565 | 0.002867603 | 0.000082038 | -0.000311212 | 0.000609475 | 0.000298263 | -0.004167641 | 0.004217451 | 0.000049810 | -0.003953374 | 0.003997040 | 0.000043666 | -0.001638090 | 0.001713509 | 0.000075419 | -0.004082215 | 0.004100829 | 0.000018614 | -0.004167641 | 0.004217451 | 0.000049810 | -0.002966795 | 0.003487799 | 0.000521003 | 10 | -0.003008253 | -0.004167641 | -0.000311212 | 4.297823222 |  |  |  |  |  |  |  |  |  |  |
| route_responsibility_frontier_guard | route assignment only when frontier-only listener also agrees | /Users/kbsoo/Downloads/cl2/hitl/h152_source_responsibility_route_hsjepa/submission_h152_route_responsibility_frontier_guard_c0d72206.csv | c0d72206 | 84 | 182 | 84 | {'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 72, 'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 46, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 29, 'submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv': 15, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 10, 'submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv': 7, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 2, 'submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv': 1} | {'S1': 32, 'S4': 32, 'S3': 31, 'S2': 26, 'Q1': 23, 'Q2': 22, 'Q3': 16} | /Users/kbsoo/Downloads/cl2/hitl/h152_source_responsibility_route_hsjepa/submission_h152_route_responsibility_frontier_guard_c0d72206.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999996751 | 182 | True | 182 | 84 | 12.113004634 | 1.244213214 | 0.146953658 | -0.002661806 | 0.002661806 | 0.000000000 | -0.001366059 | 0.001384507 | 0.000018448 | -0.002017912 | 0.002077290 | 0.000059378 | -0.000475987 | 0.000539828 | 0.000063842 | -0.002780994 | 0.002818197 | 0.000037203 | -0.002738082 | 0.002779568 | 0.000041487 | -0.001034649 | 0.001084753 | 0.000050105 | -0.002790397 | 0.002799268 | 0.000008871 | -0.002780994 | 0.002818197 | 0.000037203 | -0.001968575 | 0.002229469 | 0.000260894 | 10 | -0.002061545 | -0.002790397 | -0.000475987 | 3.301111719 |  |  |  |  |  |  |  |  |  |  |

## Candidate Comparison

| spec | file | changed_cells_vs_h057 | changed_rows_vs_h057 | h088_move_cosine | robust_positive_variant_count | robust_mean_pred_delta | robust_min_pred_delta | robust_max_pred_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reference | submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 349 | 154 | 0.121063141 | 10 | -0.003753061 | -0.005149816 | -0.000168024 |
| route_responsibility_upside | submission_h152_route_responsibility_upside_1e8b9fcc.csv | 363 | 159 | 0.214751899 | 10 | -0.003673007 | -0.005201865 | -0.000381632 |
| route_responsibility_consensus | submission_h152_route_responsibility_consensus_f5b28b01.csv | 328 | 138 | 0.212655989 | 10 | -0.003008253 | -0.004167641 | -0.000311212 |
| reference | submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 364 | 157 | 0.188791860 | 10 | -0.002941128 | -0.003981643 | -0.000161581 |
| route_responsibility_frontier_guard | submission_h152_route_responsibility_frontier_guard_c0d72206.csv | 182 | 84 | 0.146953658 | 10 | -0.002061545 | -0.002790397 | -0.000475987 |
| reference | submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 97 | 75 | 0.092965834 | 10 | -0.001231296 | -0.001675152 | -0.000298888 |

## Top Route Candidates

| source_file | row | subject_id | sleep_date | mode | targets | n_cells | route_score | robust_positive_variant_count | robust_mean_pred_delta | robust_max_pred_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | no_pre_safe | Q1,S1,S3 | 3 | 4.365694335 | 10 | -0.000444538 | -0.000020996 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | consensus_any | Q1,S1,S3 | 3 | 4.365694335 | 10 | -0.000444538 | -0.000020996 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | q_route | Q1 | 1 | 4.106284688 | 10 | -0.000442703 | -0.000020988 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | consensus_any | Q1,Q3,S1,S3 | 4 | 3.688942802 | 10 | -0.000310567 | -0.000010990 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | consensus_any | Q1,Q3,S1,S3 | 4 | 3.688942802 | 10 | -0.000310567 | -0.000010990 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | consensus_any | Q1,S1,S3,S4 | 4 | 3.651012988 | 10 | -0.000304535 | -0.000008931 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | no_pre_safe | Q1,S1,S3,S4 | 4 | 3.651012988 | 10 | -0.000304535 | -0.000008931 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | no_pre_safe | Q1,S1,S3 | 3 | 3.562294269 | 10 | -0.000304359 | -0.000014472 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | no_pre_safe | Q1,S1,S3 | 3 | 3.562294269 | 10 | -0.000304359 | -0.000014472 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | q_route | Q1,Q3 | 2 | 3.500424475 | 10 | -0.000308960 | -0.000011046 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | q_route | Q1,Q3 | 2 | 3.500424475 | 10 | -0.000308960 | -0.000011046 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 131 | id06 | 2024-07-10 00:00:00 | q_route | Q1 | 1 | 3.297291268 | 10 | -0.000302753 | -0.000014353 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 138 | id06 | 2024-07-18 00:00:00 | no_pre_safe | Q1,Q3,S2 | 3 | 2.998005337 | 9 | -0.000242990 | 0.000007384 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 138 | id06 | 2024-07-18 00:00:00 | consensus_any | Q1,Q3,S2 | 3 | 2.998005337 | 9 | -0.000242990 | 0.000007384 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | frontier_safe | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | consensus_any | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | no_pre_safe | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | frontier_safe | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | q_route | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | q_route | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | consensus_any | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | no_pre_safe | Q2 | 1 | 2.970501074 | 10 | -0.000174822 | -0.000055302 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 194 | id08 | 2024-09-09 00:00:00 | q_route | Q2 | 1 | 2.948387340 | 9 | -0.000256802 | 0.000215383 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 194 | id08 | 2024-09-09 00:00:00 | no_pre_safe | Q2 | 1 | 2.948387340 | 9 | -0.000256802 | 0.000215383 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 194 | id08 | 2024-09-09 00:00:00 | frontier_safe | Q2 | 1 | 2.948387340 | 9 | -0.000256802 | 0.000215383 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 194 | id08 | 2024-09-09 00:00:00 | consensus_any | Q2 | 1 | 2.948387340 | 9 | -0.000256802 | 0.000215383 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | consensus_any | Q2 | 1 | 2.931880041 | 10 | -0.000168631 | -0.000053344 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | frontier_safe | Q2 | 1 | 2.931880041 | 10 | -0.000168631 | -0.000053344 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | q_route | Q2 | 1 | 2.931880041 | 10 | -0.000168631 | -0.000053344 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 98 | id04 | 2024-10-19 00:00:00 | no_pre_safe | Q2 | 1 | 2.931880041 | 10 | -0.000168631 | -0.000053344 |

## Interpretation

H152 is a row-route assignment counterfactual:

- if H152 beats H149/H150 offline or publicly, source responsibility is the
  missing decoder layer;
- if H152 is weaker, H149/H150's cell-level mixing is not the immediate
  bottleneck, and the next big bet should move to public/private subset
  factorization or new target-route states.
