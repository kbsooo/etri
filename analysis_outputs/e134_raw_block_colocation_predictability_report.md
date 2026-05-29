# E134 Raw/Block Co-location Predictability

## Question

E133 found that the useful post-E95 remainder is a small Q3/Q1-heavy overlap between local upside and veto-null/public-safe density. This experiment asks whether that field is visible from raw overnight/block context under hidden-block holdout, or whether it is mostly a submission-geometry artifact.

Primary teacher: `all_sign_co_vetonull_density` from `e133_local_safety_colocation_atlas_cell_detail.csv`.

## Decision Result

- Best overall primary predictor: `night_all_blockknn` / `target_knn8`.
- Best primary truth mass in predicted top50: `0.073497`; cosine `0.498528`; JS `0.260922`.
- Best metadata-only truth mass in predicted top50: `0.063040` from `submission_metadata` / `ridge`.
- Best raw/block truth mass in predicted top50: `0.073497` from `night_all_blockknn` / `target_knn8`.
- Best predicted top50 target counts: `Q1:37,Q3:4,S4:9`; Q2/S3 fraction `0.000000`; Q1/Q3 truth mass `0.060497`.

E133 metadata benchmark to beat was top50 truth-mass capture `0.048280` for the all-sign co-located field. A useful raw/block representation should clear that by a material margin and keep the Q2/S3 tail suppressed.

## Top Primary Predictors

| feature_set | model | n_features | truth_mass_in_pred_top50 | cosine | spearman | js | top50_overlap | q1q3_mass_in_pred_top50 | q2s3_frac_in_pred_top50 | target_counts_pred_top50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| night_all_blockknn | target_knn8 | 124.000000 | 0.073497 | 0.498528 | 0.234990 | 0.260922 | 0.160000 | 0.060497 | 0.000000 | Q1:37,Q3:4,S4:9 |
| night_mobility_blockknn | target_knn8 | 124.000000 | 0.069146 | 0.500008 | 0.263350 | 0.256133 | 0.140000 | 0.058281 | 0.000000 | Q1:24,Q3:20,S4:6 |
| night_all_submission_meta | ridge | 178.000000 | 0.064347 | 0.533220 | 0.350689 | 0.253039 | 0.060000 | 0.064347 | 0.000000 | Q1:12,Q3:38 |
| submission_metadata | ridge | 54.000000 | 0.063040 | 0.537499 | 0.347996 | 0.248723 | 0.040000 | 0.063040 | 0.000000 | Q1:11,Q3:39 |
| all_raw_views_blockknn | target_knn8 | 936.000000 | 0.062453 | 0.514770 | 0.251054 | 0.254044 | 0.140000 | 0.052726 | 0.000000 | Q1:28,Q3:15,S4:7 |
| night_phone_submission_meta | ridge | 178.000000 | 0.061559 | 0.529011 | 0.329505 | 0.254072 | 0.040000 | 0.061559 | 0.000000 | Q1:14,Q3:36 |
| night_context_blockknn | target_knn8 | 124.000000 | 0.060452 | 0.487214 | 0.225420 | 0.265073 | 0.120000 | 0.050725 | 0.000000 | Q1:28,Q3:15,S4:7 |
| night_light_blockknn | target_knn8 | 124.000000 | 0.059206 | 0.486920 | 0.198299 | 0.269430 | 0.080000 | 0.044663 | 0.000000 | Q1:7,Q3:29,S4:14 |
| visible_metadata | ridge | 34.000000 | 0.058121 | 0.522835 | 0.221232 | 0.257708 | 0.080000 | 0.058121 | 0.000000 | Q1:13,Q3:37 |
| night_all_target | ridge | 131.000000 | 0.056587 | 0.519814 | 0.186164 | 0.259890 | 0.100000 | 0.056587 | 0.000000 | Q1:4,Q3:46 |
| all_raw_views_submission_meta | ridge | 990.000000 | 0.055511 | 0.532406 | 0.350519 | 0.252747 | 0.040000 | 0.055511 | 0.000000 | Q1:11,Q3:39 |
| night_watch_target | ridge | 131.000000 | 0.054961 | 0.508656 | 0.177051 | 0.266728 | 0.100000 | 0.054961 | 0.000000 | Q1:7,Q3:43 |
| night_coverage_visible_meta | ridge | 102.000000 | 0.053295 | 0.531358 | 0.221004 | 0.255246 | 0.040000 | 0.053295 | 0.000000 | Q1:8,Q3:42 |
| night_usage_ambience_target | ridge | 131.000000 | 0.052134 | 0.509758 | 0.201096 | 0.265492 | 0.020000 | 0.052134 | 0.000000 | Q1:2,Q3:48 |
| night_coverage_blockknn | target_knn8 | 68.000000 | 0.051350 | 0.448220 | 0.149823 | 0.285299 | 0.080000 | 0.045598 | 0.000000 | Q1:10,Q3:21,S4:19 |

## Interpretation

Raw/block context does not materially beat the metadata visibility bar. The E133 safe-remainder field is therefore not obviously present in observed raw overnight/block geometry. This strengthens the plateau explanation: the local-upside direction and public-safe tail geometry overlap in probability/submission space, but the overlap is weakly visible from current raw/block context.

## Outputs

- Summary: `e134_raw_block_colocation_predictability_summary.csv`
- Geometry summary: `e134_raw_block_colocation_predictability_geometry_summary.csv`
- Primary predictions: `e134_raw_block_colocation_predictability_primary_predictions.csv`
