# H151 H088-Hard-Veto Bundle HS-JEPA

Date: 2026-06-03

## Question

H150 role-holdout showed that removing H088 makes the listener equation predict
H088 in the wrong direction. H151 asks:

```text
Should H088 be a hard toxicity veto rather than a learned bad-anchor component?
```

## Candidate

| candidate_file | candidate_path | selected_cells | selected_rows | selected_source_mix | selected_target_mix | worldview | failure_interpretation | validation_path | validation_rows | validation_keys_match | validation_duplicate_keys | validation_nan_cells | validation_min_prob | validation_max_prob | validation_changed_cells_vs_h057_validation | validation_upload_safe | metric_changed_cells_vs_h057 | metric_changed_rows_vs_h057 | metric_move_l1 | metric_move_l2 | metric_h088_move_cosine | metric_all_full_pred_delta | metric_all_full_benefit_sum | metric_all_full_toxicity_sum | metric_no_pre_h_pred_delta | metric_no_pre_h_benefit_sum | metric_no_pre_h_toxicity_sum | metric_no_bad_pred_delta | metric_no_bad_benefit_sum | metric_no_bad_toxicity_sum | metric_frontier_only_pred_delta | metric_frontier_only_benefit_sum | metric_frontier_only_toxicity_sum | metric_no_human_social_pred_delta | metric_no_human_social_benefit_sum | metric_no_human_social_toxicity_sum | metric_no_subject_pred_delta | metric_no_subject_benefit_sum | metric_no_subject_toxicity_sum | metric_no_row_order_pred_delta | metric_no_row_order_benefit_sum | metric_no_row_order_toxicity_sum | metric_no_base_prob_pred_delta | metric_no_base_prob_benefit_sum | metric_no_base_prob_toxicity_sum | metric_structural_only_pred_delta | metric_structural_only_benefit_sum | metric_structural_only_toxicity_sum | metric_human_social_only_pred_delta | metric_human_social_only_benefit_sum | metric_human_social_only_toxicity_sum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | /Users/kbsoo/Downloads/cl2/submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 97 | 75 | {'submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv': 48, 'submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv': 16, 'submission_h126_coeffeq_3fe3eee4_uploadsafe.csv': 13, 'submission_h074_antishortcut_inversion_816703df_uploadsafe.csv': 11, 'submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv': 5, 'submission_h075_antibad_transport_f6863945_uploadsafe.csv': 4} | {'Q2': 23, 'S4': 18, 'Q1': 13, 'S2': 13, 'S1': 13, 'Q3': 11, 'S3': 6} | H088 is a non-substitutable toxicity sensor; same-direction cells are vetoed unless listener consensus is extremely strong. | If H151 underperforms H149/H150 offline or publicly, then the H088 axis is better as a soft penalty than a hard veto. | /Users/kbsoo/Downloads/cl2/submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 250 | True | 0 | 0 | 0.000004939 | 0.999998110 | 97 | True | 97 | 75 | 6.945176487 | 1.549877906 | 0.092965834 | -0.001567595 | 0.001567595 | 0.000000000 | -0.000865554 | 0.000893285 | 0.000027730 | -0.001225652 | 0.001235135 | 0.000009483 | -0.000298888 | 0.000374720 | 0.000075832 | -0.001675152 | 0.001715363 | 0.000040211 | -0.001625050 | 0.001643005 | 0.000017954 | -0.000758629 | 0.000761808 | 0.000003180 | -0.001598526 | 0.001600800 | 0.000002274 | -0.001675152 | 0.001715363 | 0.000040211 | -0.001022759 | 0.001550293 | 0.000527534 |

## H149/H150/H151 Comparison

| file | changed_cells_vs_h057 | changed_rows_vs_h057 | h088_move_cosine | robust_positive_variant_count | robust_mean_pred_delta | all_full_pred_delta | no_pre_h_pred_delta | frontier_only_pred_delta | human_social_only_pred_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_h151_h088_hardveto_bundle_efaa9c93_uploadsafe.csv | 97 | 75 | 0.092965834 | 10 | -0.001231296 | -0.001567595 | -0.000865554 | -0.000298888 | -0.001022759 |
| submission_h150_robust_bundle_listener_5e12f9bd_uploadsafe.csv | 364 | 157 | 0.188791860 | 10 | -0.002941128 | -0.003842840 | -0.002360980 | -0.000161581 | -0.002869942 |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 349 | 154 | 0.121063141 | 10 | -0.003753061 | -0.004994063 | -0.003198392 | -0.000168024 | -0.003068586 |

Source mix:

| source_file | cells |
| --- | --- |
| submission_h149_bundle_listener_route_d8e1d789_uploadsafe.csv | 48 |
| submission_h073_humanaction_bridge_7a2cbf07_uploadsafe.csv | 16 |
| submission_h126_coeffeq_3fe3eee4_uploadsafe.csv | 13 |
| submission_h074_antishortcut_inversion_816703df_uploadsafe.csv | 11 |
| submission_h071_rowtarget_assignment_a52b6b57_uploadsafe.csv | 5 |
| submission_h075_antibad_transport_f6863945_uploadsafe.csv | 4 |

Target mix:

| target | cells |
| --- | --- |
| Q2 | 23 |
| S4 | 18 |
| Q1 | 13 |
| S2 | 13 |
| S1 | 13 |
| Q3 | 11 |
| S3 | 6 |

## Interpretation

H151 is not meant to dominate H149 on upside.  It is a structural counterfactual:

- H149 = high-upside bundle listener, soft H088 penalty;
- H150 = robust consensus across listener worlds;
- H151 = hard H088 toxicity veto.

If H151 becomes the safest offline candidate, H088 should be formalized in
HS-JEPA as a hard anti-shortcut constraint.  If H149/H150 remain better, H088
should stay a stress diagnostic / soft toxicity energy.
