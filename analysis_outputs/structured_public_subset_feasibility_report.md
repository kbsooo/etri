# E45 Structured Public-Subset Feasibility

## Observe

E43-E44 showed that current candidate edges are smaller than selector error and the existing scored universe has no hidden large safe movement. The next cheap falsification is whether the public subset itself is a simple structured mask that can be used as an independent selector target.

## Wonder

Can subject/date/order/raw-domain masks plus train-derived priors predict held-out known public anchors at selector-scale error, or are public-subset inverse worlds still too underdetermined?

## Hypothesis

H44: if public LB is dominated by a simple structured subset, then at least one predeclared mask family should produce leave-one-anchor-out public-LB predictions with MAE below the current selector error and feasible ranges narrow enough to beat the raw05-A2C8 gap.

## Method

- known anchors: `8`.
- masks tested: `145`.
- raw05-A2C8 public gap: `0.0000869862`.
- best audited selector error: `0.000218288`.
- For each mask and held-out anchor, fit soft hidden labels on the remaining anchors under train global +/-0.10 and subject-target +/-0.20 prior constraints, then choose the minimum-deviation solution from shrunk subject train priors.
- Stress tests: anchor-LOO, structured-vs-random mask comparison, train-prior plausibility, raw05/A2C8 known-direction check, and feasible interval width on the best masks.

## Result

- selector-scale gates: `0`.
- strict sub-gap gates: `0`.
- best LOO MAE: `0.000429528`.
- best LOO MAE / raw05 gap: `4.938`.
- best LOO MAE / selector error: `1.968`.

### Family Summary

| mask_kind | masks | best_mae | median_mae | best_max_abs | best_rank_accuracy | selector_scale_gates | strict_subgap_gates | a2c8_best_rate | raw05_direction_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_key_order | 14 | 0.000429528 | 0.00136074 | 0.00129817 | 0.892857 | 0 | 0 | 0.571429 | 1 |
| raw_cluster | 8 | 0.000662463 | 0.00178165 | 0.00173839 | 0.857143 | 0 | 0 | 0.5 | 0.75 |
| random_control | 24 | 0.000798105 | 0.00151503 | 0.00213114 | 0.821429 | 0 | 0 | 0.0833333 | 1 |
| global_key_mod | 21 | 0.00094081 | 0.00149705 | 0.00232261 | 0.75 | 0 | 0 | 0.190476 | 1 |
| raw_domain | 12 | 0.000984003 | 0.00132261 | 0.00177438 | 0.785714 | 0 | 0 | 0 | 1 |
| subject_order | 9 | 0.000989163 | 0.00129386 | 0.00315139 | 0.785714 | 0 | 0 | 0.222222 | 1 |
| single_subject | 7 | 0.00110306 | 0.0035916 | 0.0028191 | 0.714286 | 0 | 0 | 0 | 0.142857 |
| month | 4 | 0.00112105 | 0.00144125 | 0.00324527 | 0.75 | 0 | 0 | 0.5 | 1 |
| subject_group | 4 | 0.00117881 | 0.00147544 | 0.00279693 | 0.75 | 0 | 0 | 0.25 | 1 |
| subject_complement | 10 | 0.00119001 | 0.00150822 | 0.00366373 | 0.714286 | 0 | 0 | 0 | 1 |
| calendar | 2 | 0.0012759 | 0.00143976 | 0.00441729 | 0.75 | 0 | 0 | 0 | 1 |
| dow | 7 | 0.0013411 | 0.00144276 | 0.00364032 | 0.714286 | 0 | 0 | 0.285714 | 1 |
| calendar_order | 14 | 0.00138529 | 0.00152694 | 0.00372302 | 0.75 | 0 | 0 | 0.571429 | 1 |
| global_key_window | 5 | 0.00138828 | 0.00155159 | 0.0043084 | 0.714286 | 0 | 0 | 0 | 1 |
| all | 1 | 0.00156469 | 0.00156469 | 0.00471052 | 0.642857 | 0 | 0 | 0 | 1 |

### Best Masks

| mask_kind | mask_name | rows | loocv_mae | loocv_max_abs | rank_accuracy | a2c8_predicted_best | raw05_direction_correct | selector_scale_gate | strict_subgap_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_key_order | suffix_frac0.20 | 50 | 0.000429528 | 0.00129817 | 0.892857 | True | True | False | False |
| raw_cluster | cluster_7_domain_auc_1.000 | 23 | 0.000662463 | 0.00173839 | 0.857143 | True | True | False | False |
| global_key_order | suffix_frac0.30 | 75 | 0.000759177 | 0.00194239 | 0.892857 | True | True | False | False |
| random_control | frac0.30_rep04 | 75 | 0.000798105 | 0.00213114 | 0.821429 | True | True | False | False |
| global_key_mod | mod7_rem4 | 36 | 0.00094081 | 0.0025577 | 0.75 | False | True | False | False |
| raw_domain | missing_high30 | 75 | 0.000984003 | 0.00371027 | 0.75 | False | True | False | False |
| subject_order | per_subject_head_frac0.30 | 75 | 0.000989163 | 0.00315139 | 0.75 | False | True | False | False |
| global_key_order | prefix_frac0.40 | 100 | 0.00100523 | 0.00403669 | 0.821429 | True | True | False | False |
| raw_domain | density_radius_low30 | 75 | 0.00100737 | 0.00177438 | 0.785714 | False | True | False | False |
| raw_domain | missing_low40 | 104 | 0.00105381 | 0.00273785 | 0.714286 | False | True | False | False |
| subject_order | per_subject_mid_frac0.30 | 75 | 0.00105619 | 0.0045233 | 0.75 | False | True | False | False |
| global_key_order | prefix_frac0.30 | 75 | 0.00110019 | 0.00479558 | 0.785714 | True | True | False | False |
| single_subject | subject_id04 | 27 | 0.00110306 | 0.0028191 | 0.678571 | False | False | False | False |
| month | month_8 | 89 | 0.00112105 | 0.00385446 | 0.714286 | False | True | False | False |
| random_control | frac0.30_rep03 | 75 | 0.00112129 | 0.00299427 | 0.678571 | False | True | False | False |

### Feasible Range Check

| mask_kind | mask_name | range_mean_width | range_max_width | range_coverage | range_nearest_mae |
| --- | --- | --- | --- | --- | --- |
| single_subject | subject_id04 | 0.0287288 | 0.0824278 | 1 | 0 |
| subject_order | per_subject_head_frac0.30 | 0.0369223 | 0.0972527 | 1 | 0 |
| calendar_order | date_suffix_frac0.30 | 0.0389647 | 0.102578 | 1 | 0 |
| month | month_8 | 0.0395944 | 0.103414 | 1 | 0 |
| global_key_order | prefix_frac0.40 | 0.0401057 | 0.0996422 | 1 | 0 |
| raw_domain | missing_high30 | 0.0411978 | 0.104985 | 1 | 0 |
| raw_cluster | cluster_7_domain_auc_1.000 | 0.0422411 | 0.0872478 | 1 | 0 |
| global_key_window | start062_len125 | 0.0425177 | 0.105811 | 1 | 0 |
| global_key_mod | mod7_rem4 | 0.042685 | 0.0990313 | 1 | 0 |
| calendar | weekend | 0.0427022 | 0.101028 | 1 | 0 |
| global_key_order | suffix_frac0.20 | 0.0427582 | 0.0940986 | 1 | 0 |
| global_key_order | suffix_frac0.30 | 0.0430878 | 0.100761 | 1 | 0 |
| dow | Tuesday | 0.0442541 | 0.0979637 | 1 | 0 |
| random_control | frac0.30_rep04 | 0.0448116 | 0.104099 | 1 | 0 |
| all | all_rows | 0.0455258 | 0.109545 | 1 | 0 |
| subject_complement | not_subject_id06 | 0.0456389 | 0.109101 | 1 | 0 |
| subject_group | odd_subjects | 0.0462598 | 0.106411 | 1 | 0 |

## Decision

No structured mask produced selector-scale held-out-anchor predictions. Simple public-subset structure is not the missing selector target under these priors.
This strengthens the bottleneck diagnosis: the plateau is not explained by an obvious subject/order/date/raw-domain public split that we can locally recover.

## Outputs

- `analysis_outputs/structured_public_subset_feasibility_loocv.csv`
- `analysis_outputs/structured_public_subset_feasibility_masks.csv`
- `analysis_outputs/structured_public_subset_feasibility_ranges.csv`
- `analysis_outputs/structured_public_subset_feasibility_summary.csv`
- `analysis_outputs/structured_public_subset_feasibility_report.md`
