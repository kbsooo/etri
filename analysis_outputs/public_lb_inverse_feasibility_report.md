# Public LB Inverse Feasibility

Question: do the known public LB observations identify target/row/public-prior structure strongly enough to rank candidate deltas, or are many hidden worlds still feasible?

## Fit

- known public observations used: `8`.
- cells: `1750` (`250` rows x `7` targets).
- all-test soft-label minimum total slack: `0`; max abs residual `9.99200722163e-16`.
- arbitrary cell-mixture minimum total slack: `0`; max abs residual `1.11022302463e-16`.

## Target Ranges

| target | alltest_prior_min | alltest_prior_max | alltest_prior_width | cellmix_positive_mass_min | cellmix_positive_mass_max | cellmix_target_mass_min | cellmix_target_mass_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0 | 1 | 1 | 0 | 0.996713 | 0 | 0.996713 |
| Q2 | 0.0337284 | 0.925325 | 0.891597 | 0 | 0.998155 | 0.00328677 | 0.998155 |
| Q3 | 0 | 1 | 1 | 0 | 0.894741 | 0 | 0.996713 |
| S1 | 0.000573746 | 1 | 0.999426 | 0 | 0.996713 | 0 | 0.996713 |
| S2 | 0 | 1 | 1 | 0 | 0.996713 | 0 | 0.996713 |
| S3 | 0 | 1 | 1 | 0 | 0.986994 | 0 | 0.986994 |
| S4 | 0 | 1 | 1 | 0 | 0.996713 | 0 | 0.996713 |

## Candidate Delta Ranges vs A2C8

| role | file | alltest_delta_min | alltest_delta_max | alltest_crosses_zero | cellmix_delta_min | cellmix_delta_max | cellmix_crosses_zero | mean_abs_prob_move_vs_a2c8 | mean_abs_logit_move_vs_a2c8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_0c916 | submission_mixmin_0c916bb4.csv | -0.0119541 | 0.010118 | True | -0.0351361 | 0.0363054 | True | 0.00849582 | 0.0456142 |
| direns_c4af | submission_direns_c4af1fd8.csv | -0.0116892 | 0.0099658 | True | -0.0341571 | 0.0352835 | True | 0.00835268 | 0.0448824 |
| targetabl_q3s234 | submission_targetabl_1049b8e7.csv | -0.0108742 | 0.00981486 | True | -0.0333477 | 0.0340625 | True | 0.00480937 | 0.0254551 |
| targetabl_q3stage | submission_targetabl_b19056bb.csv | -0.00888081 | 0.00764523 | True | -0.0257834 | 0.0263335 | True | 0.00445245 | 0.0248301 |
| pair_sensor_6b | submission_label_flow_focused_6b9335b1.csv | -0.00441576 | 0.00281774 | True | -0.102426 | 0.141397 | True | 0.00161225 | 0.0072335 |
| pair_sensor_1bb | submission_label_flow_focused_1bbfb735.csv | -0.00371472 | 0.00233289 | True | -0.0869166 | 0.115951 | True | 0.00134544 | 0.0060476 |
| inverse7blend_1040 | submission_inverse7blend_1040423d.csv | -0.00340276 | 0.00313789 | True | -0.0185375 | 0.0182943 | True | 0.00237389 | 0.0124131 |
| pair_sensor_1bb_s0p65 | submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | -0.00244606 | 0.00148488 | True | -0.0580233 | 0.0728819 | True | 0.00086877 | 0.00393094 |
| raw05_known | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 8.69762e-05 | 8.69962e-05 | False | 8.69762e-05 | 8.69962e-05 | False | 0.00164639 | 0.00853087 |

## Candidate Delta Ranges With Train-Prior Bands

| role | file | prior_band | fit_sum_slack | fit_max_abs_residual | delta_min | delta_max | crosses_zero |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin_0c916 | submission_mixmin_0c916bb4.csv | 0.05 | 0 | 1.22125e-15 | -0.01195 | 0.010118 | True |
| direns_c4af | submission_direns_c4af1fd8.csv | 0.05 | 0 | 1.22125e-15 | -0.0116845 | 0.00996578 | True |
| targetabl_q3s234 | submission_targetabl_1049b8e7.csv | 0.05 | 0 | 1.22125e-15 | -0.0108212 | 0.00973506 | True |
| targetabl_q3stage | submission_targetabl_b19056bb.csv | 0.05 | 0 | 1.22125e-15 | -0.00882686 | 0.00763153 | True |
| pair_sensor_6b | submission_label_flow_focused_6b9335b1.csv | 0.05 | 0 | 1.22125e-15 | -0.00441576 | 0.00281774 | True |
| pair_sensor_1bb | submission_label_flow_focused_1bbfb735.csv | 0.05 | 0 | 1.22125e-15 | -0.00371472 | 0.00233289 | True |
| inverse7blend_1040 | submission_inverse7blend_1040423d.csv | 0.05 | 0 | 1.22125e-15 | -0.00340264 | 0.00313635 | True |
| pair_sensor_1bb_s0p65 | submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | 0.05 | 0 | 1.22125e-15 | -0.00244606 | 0.00148488 | True |
| raw05_known | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.05 | 0 | 1.22125e-15 | 8.69762e-05 | 8.69962e-05 | False |
| mixmin_0c916 | submission_mixmin_0c916bb4.csv | 0.1 | 0 | 9.99201e-16 | -0.0119541 | 0.010118 | True |
| direns_c4af | submission_direns_c4af1fd8.csv | 0.1 | 0 | 9.99201e-16 | -0.0116892 | 0.0099658 | True |
| targetabl_q3s234 | submission_targetabl_1049b8e7.csv | 0.1 | 0 | 9.99201e-16 | -0.0108742 | 0.00980913 | True |
| targetabl_q3stage | submission_targetabl_b19056bb.csv | 0.1 | 0 | 9.99201e-16 | -0.0088793 | 0.00764523 | True |
| pair_sensor_6b | submission_label_flow_focused_6b9335b1.csv | 0.1 | 0 | 9.99201e-16 | -0.00441576 | 0.00281774 | True |
| pair_sensor_1bb | submission_label_flow_focused_1bbfb735.csv | 0.1 | 0 | 9.99201e-16 | -0.00371472 | 0.00233289 | True |
| inverse7blend_1040 | submission_inverse7blend_1040423d.csv | 0.1 | 0 | 9.99201e-16 | -0.00340276 | 0.00313789 | True |
| pair_sensor_1bb_s0p65 | submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | 0.1 | 0 | 9.99201e-16 | -0.00244606 | 0.00148488 | True |
| raw05_known | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.1 | 0 | 9.99201e-16 | 8.69762e-05 | 8.69962e-05 | False |
| mixmin_0c916 | submission_mixmin_0c916bb4.csv | 0.2 | 0 | 9.99201e-16 | -0.0119541 | 0.010118 | True |
| direns_c4af | submission_direns_c4af1fd8.csv | 0.2 | 0 | 9.99201e-16 | -0.0116892 | 0.0099658 | True |
| targetabl_q3s234 | submission_targetabl_1049b8e7.csv | 0.2 | 0 | 9.99201e-16 | -0.0108742 | 0.00981486 | True |
| targetabl_q3stage | submission_targetabl_b19056bb.csv | 0.2 | 0 | 9.99201e-16 | -0.00888081 | 0.00764523 | True |
| pair_sensor_6b | submission_label_flow_focused_6b9335b1.csv | 0.2 | 0 | 9.99201e-16 | -0.00441576 | 0.00281774 | True |
| pair_sensor_1bb | submission_label_flow_focused_1bbfb735.csv | 0.2 | 0 | 9.99201e-16 | -0.00371472 | 0.00233289 | True |
| inverse7blend_1040 | submission_inverse7blend_1040423d.csv | 0.2 | 0 | 9.99201e-16 | -0.00340276 | 0.00313789 | True |
| pair_sensor_1bb_s0p65 | submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | 0.2 | 0 | 9.99201e-16 | -0.00244606 | 0.00148488 | True |
| raw05_known | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.2 | 0 | 9.99201e-16 | 8.69762e-05 | 8.69962e-05 | False |

## Subject Mass Ranges Under Cell-Mixture Model

| subject_id | actual_test_row_frac | cellmix_subject_mass_min | cellmix_subject_mass_max | cellmix_subject_mass_width |
| --- | --- | --- | --- | --- |
| id01 | 0.108 | 0 | 1 | 1 |
| id02 | 0.128 | 0 | 1 | 1 |
| id03 | 0.084 | 0 | 1 | 1 |
| id04 | 0.108 | 0 | 1 | 1 |
| id05 | 0.084 | 0 | 1 | 1 |
| id06 | 0.096 | 0 | 1 | 1 |
| id07 | 0.12 | 0 | 1 | 1 |
| id08 | 0.076 | 0 | 1 | 1 |
| id09 | 0.108 | 0 | 1 | 1 |
| id10 | 0.088 | 0 | 1 | 1 |

## Decision

- `8` candidate delta intervals cross zero under the stricter all-test soft-label inverse model.
- Known public LB anchors are therefore not enough to determine those candidate signs without additional structural assumptions.
- `8` candidate delta intervals cross zero under the looser cell-mixture model.
- Train-prior band cross-zero counts: `{0.05: 8, 0.1: 8, 0.2: 8}`.
- If public subset/row/target weights are allowed to vary freely, the LB observations are highly underidentified.
- This supports using public LB as a sensor only after declaring a selector worldview, not as a standalone optimizer.
