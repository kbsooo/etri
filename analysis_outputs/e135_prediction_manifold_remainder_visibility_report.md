# E135 Prediction-Manifold Remainder Visibility

## Question

E134 says raw/block context only weakly sees E133's safe remainder. This audit asks whether the disagreement geometry of the main existing submissions sees it better under hidden-block holdout.

Primary teacher: `all_sign_co_vetonull_density`.

## Decision Result

- Best predictor: `row_prediction_pca_meta` / `ridge`.
- Best top50 truth-mass capture: `0.063430`; cosine `0.531360`; JS `0.251301`.
- Metadata-only best top50 truth-mass capture: `0.063040` from `submission_metadata` / `ridge`.
- Prediction-manifold best top50 truth-mass capture: `0.063430` from `row_prediction_pca_meta` / `ridge`.
- Best predicted top50 target counts: `Q1:11,Q3:38,S4:1`; Q2/S3 fraction `0.000000`; Q1/Q3 truth mass `0.063213`.

Reference bars: E133 metadata `0.048280`, E134 metadata `0.063040`, E134 raw/block `0.073497`. A useful prediction-manifold target should clear raw/block by a material margin and not revive Q2/S3.

## Top Predictors

| feature_set | model | n_features | truth_mass_in_pred_top50 | cosine | spearman | js | top50_overlap | q1q3_mass_in_pred_top50 | q2s3_frac_in_pred_top50 | target_counts_pred_top50 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| row_prediction_pca_meta | ridge | 66.000000 | 0.063430 | 0.531360 | 0.338283 | 0.251301 | 0.040000 | 0.063213 | 0.000000 | Q1:11,Q3:38,S4:1 |
| submission_metadata | ridge | 54.000000 | 0.063040 | 0.537499 | 0.347996 | 0.248723 | 0.040000 | 0.063040 | 0.000000 | Q1:11,Q3:39 |
| row_prediction_pca_target | ridge | 19.000000 | 0.058282 | 0.528856 | 0.221953 | 0.255810 | 0.080000 | 0.058282 | 0.000000 | Q1:5,Q3:45 |
| visible_metadata | ridge | 34.000000 | 0.058121 | 0.522835 | 0.221232 | 0.257708 | 0.080000 | 0.058121 | 0.000000 | Q1:13,Q3:37 |
| cell_prediction_scalars_meta | ridge | 102.000000 | 0.057816 | 0.540788 | 0.350192 | 0.248076 | 0.000000 | 0.057055 | 0.000000 | Q1:13,Q3:36,S4:1 |
| row_uncertainty_target | ridge | 28.000000 | 0.054774 | 0.522412 | 0.223673 | 0.259132 | 0.080000 | 0.054774 | 0.000000 | Q1:4,Q3:46 |
| prediction_manifold_full | ridge | 135.000000 | 0.053883 | 0.524656 | 0.332959 | 0.255805 | 0.020000 | 0.052426 | 0.000000 | Q1:15,Q3:31,S2:1,S4:3 |
| cell_prediction_scalars | ridge | 55.000000 | 0.036354 | 0.530826 | 0.228856 | 0.256809 | 0.040000 | 0.036354 | 0.000000 | Q1:3,Q3:47 |
| row_prediction_full_target | ridge | 329.000000 | 0.033219 | 0.493751 | 0.162245 | 0.268825 | 0.040000 | 0.032970 | 0.040000 | Q1:12,Q2:1,Q3:33,S1:1,S2:1,S3:1,S4:1 |
| target_only | ridge | 7.000000 | 0.022240 | 0.522705 | 0.147259 | 0.258100 | 0.020000 | 0.022240 | 0.000000 | Q3:50 |
| target_only | extratrees | 7.000000 | 0.007432 | 0.358950 | -0.132509 | 0.329335 | 0.000000 | 0.003367 | 0.260000 | Q1:8,Q2:7,Q3:7,S1:7,S2:8,S3:6,S4:7 |
| visible_metadata | extratrees | 34.000000 | 0.007432 | 0.358950 | -0.132509 | 0.329335 | 0.000000 | 0.003367 | 0.260000 | Q1:8,Q2:7,Q3:7,S1:7,S2:8,S3:6,S4:7 |
| submission_metadata | extratrees | 54.000000 | 0.007432 | 0.358950 | -0.132509 | 0.329335 | 0.000000 | 0.003367 | 0.260000 | Q1:8,Q2:7,Q3:7,S1:7,S2:8,S3:6,S4:7 |
| cell_prediction_scalars_meta | extratrees | 102.000000 | 0.007432 | 0.358950 | -0.132509 | 0.329335 | 0.000000 | 0.003367 | 0.260000 | Q1:8,Q2:7,Q3:7,S1:7,S2:8,S3:6,S4:7 |
| row_prediction_pca_meta | extratrees | 66.000000 | 0.007432 | 0.358950 | -0.132509 | 0.329335 | 0.000000 | 0.003367 | 0.260000 | Q1:8,Q2:7,Q3:7,S1:7,S2:8,S3:6,S4:7 |

## Interpretation

The prediction manifold does not materially improve over E134 raw/block visibility. This closes the cheap old-submission-disagreement path: the E133 safe remainder is weak in raw context and weak in the existing prediction manifold. The next useful representation must change the target itself or use a new source of supervision, not just rerank old submission disagreement.

## Outputs

- Summary: `e135_prediction_manifold_remainder_visibility_summary.csv`
- Predictions: `e135_prediction_manifold_remainder_visibility_predictions.csv`
