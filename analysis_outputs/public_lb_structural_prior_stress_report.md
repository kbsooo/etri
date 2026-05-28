# Public LB Structural Prior Stress

Question: if E26 is underidentified, do weak structural priors from train target prevalence and subject-target priors collapse candidate signs enough to rank submissions?

## Scenario Feasibility

| scenario | global_band | subject_target_band | fit_ok | fit_sum_slack | fit_max_abs_residual | interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| alltest_no_prior |  |  | True | 0 | 9.99201e-16 | E26 control: all test cells, no structural prior. |
| global_t005 | 0.05 |  | True | 0 | 1.22125e-15 | All-test public world with train target prevalence +/-0.05. |
| global_t005_subject_t020 | 0.05 | 0.2 | True | 0 | 9.99201e-16 | Weak subject identity prior layered on global prevalence. |
| global_t005_subject_t015 | 0.05 | 0.15 | True | 0 | 9.99201e-16 | Moderate subject identity prior; still allows temporal drift. |
| global_t010_subject_t020 | 0.1 | 0.2 | True | 0 | 4.44208e-10 | Looser global prior with weak subject identity prior. |
| global_t010_subject_t015 | 0.1 | 0.15 | True | 0 | 1.22125e-15 | Balanced global/subject prior stress. |
| global_t010_subject_t010 | 0.1 | 0.1 | True | 0 | 1.22125e-15 | Tight subject identity prior; strong assumption stress. |

## Candidate Sign Stability

| role | file | scenarios | cross_zero_count | one_sided_negative_count | one_sided_positive_count | best_delta_min | worst_delta_max | median_width |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw05_known | submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 7 | 0 | 0 | 7 | 8.69762e-05 | 8.69962e-05 | 2e-08 |
| pair_sensor_1bb_s0p65 | submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | 7 | 7 | 0 | 0 | -0.00244606 | 0.00148488 | 0.00393094 |
| pair_sensor_1bb | submission_label_flow_focused_1bbfb735.csv | 7 | 7 | 0 | 0 | -0.00371472 | 0.00233289 | 0.0060476 |
| pair_sensor_6b | submission_label_flow_focused_6b9335b1.csv | 7 | 7 | 0 | 0 | -0.00441576 | 0.00281774 | 0.0072335 |
| inverse7blend_1040 | submission_inverse7blend_1040423d.csv | 7 | 7 | 0 | 0 | -0.00340276 | 0.00313789 | 0.00631422 |
| targetabl_q3stage | submission_targetabl_b19056bb.csv | 7 | 7 | 0 | 0 | -0.00888081 | 0.00764523 | 0.0159808 |
| targetabl_q3s234 | submission_targetabl_1049b8e7.csv | 7 | 7 | 0 | 0 | -0.0108742 | 0.00981486 | 0.0196939 |
| direns_c4af | submission_direns_c4af1fd8.csv | 7 | 7 | 0 | 0 | -0.0116892 | 0.0099658 | 0.0207566 |
| mixmin_0c916 | submission_mixmin_0c916bb4.csv | 7 | 7 | 0 | 0 | -0.0119541 | 0.010118 | 0.021077 |

## Scenario Summary

| scenario | candidates | cross_zero | one_sided_negative | one_sided_positive | median_width | fit_sum_slack | fit_max_abs_residual |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alltest_no_prior | 9 | 8 | 0 | 1 | 0.0072335 | 0 | 9.99201e-16 |
| global_t005 | 9 | 8 | 0 | 1 | 0.0072335 | 0 | 1.22125e-15 |
| global_t005_subject_t015 | 9 | 8 | 0 | 1 | 0.0072335 | 0 | 9.99201e-16 |
| global_t005_subject_t020 | 9 | 8 | 0 | 1 | 0.0072335 | 0 | 9.99201e-16 |
| global_t010_subject_t010 | 9 | 8 | 0 | 1 | 0.0072242 | 0 | 1.22125e-15 |
| global_t010_subject_t015 | 9 | 8 | 0 | 1 | 0.0072335 | 0 | 1.22125e-15 |
| global_t010_subject_t020 | 9 | 8 | 0 | 1 | 0.0072335 | 0 | 4.44208e-10 |

## Structured Scenarios Detail

| scenario | role | delta_min | delta_max | range_width | crosses_zero | one_sided_negative | one_sided_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_t005_subject_t015 | mixmin_0c916 | -0.0112084 | 0.00943571 | 0.0206441 | True | False | False |
| global_t005_subject_t015 | direns_c4af | -0.0110449 | 0.00931542 | 0.0203604 | True | False | False |
| global_t005_subject_t015 | targetabl_q3s234 | -0.00994404 | 0.00909638 | 0.0190404 | True | False | False |
| global_t005_subject_t015 | targetabl_q3stage | -0.00838472 | 0.00725892 | 0.0156436 | True | False | False |
| global_t005_subject_t015 | pair_sensor_6b | -0.00441576 | 0.00281774 | 0.0072335 | True | False | False |
| global_t005_subject_t015 | pair_sensor_1bb | -0.00371472 | 0.00233289 | 0.0060476 | True | False | False |
| global_t005_subject_t015 | inverse7blend_1040 | -0.00321647 | 0.00296765 | 0.00618413 | True | False | False |
| global_t005_subject_t015 | pair_sensor_1bb_s0p65 | -0.00244606 | 0.00148488 | 0.00393094 | True | False | False |
| global_t005_subject_t015 | raw05_known | 8.69762e-05 | 8.69962e-05 | 2e-08 | False | False | True |
| global_t005_subject_t020 | mixmin_0c916 | -0.0114197 | 0.00965732 | 0.021077 | True | False | False |
| global_t005_subject_t020 | direns_c4af | -0.011236 | 0.00952068 | 0.0207566 | True | False | False |
| global_t005_subject_t020 | targetabl_q3s234 | -0.0103155 | 0.00937837 | 0.0196939 | True | False | False |
| global_t005_subject_t020 | targetabl_q3stage | -0.00856512 | 0.00741568 | 0.0159808 | True | False | False |
| global_t005_subject_t020 | pair_sensor_6b | -0.00441576 | 0.00281774 | 0.0072335 | True | False | False |
| global_t005_subject_t020 | pair_sensor_1bb | -0.00371472 | 0.00233289 | 0.0060476 | True | False | False |
| global_t005_subject_t020 | inverse7blend_1040 | -0.00327396 | 0.00304026 | 0.00631422 | True | False | False |
| global_t005_subject_t020 | pair_sensor_1bb_s0p65 | -0.00244606 | 0.00148488 | 0.00393094 | True | False | False |
| global_t005_subject_t020 | raw05_known | 8.69762e-05 | 8.69962e-05 | 2e-08 | False | False | True |
| global_t010_subject_t010 | mixmin_0c916 | -0.0108919 | 0.00910661 | 0.0199985 | True | False | False |
| global_t010_subject_t010 | direns_c4af | -0.0107358 | 0.00899055 | 0.0197264 | True | False | False |
| global_t010_subject_t010 | targetabl_q3s234 | -0.00943015 | 0.00866438 | 0.0180945 | True | False | False |
| global_t010_subject_t010 | targetabl_q3stage | -0.0080924 | 0.00700619 | 0.0150986 | True | False | False |
| global_t010_subject_t010 | pair_sensor_6b | -0.00440646 | 0.00281774 | 0.0072242 | True | False | False |
| global_t010_subject_t010 | pair_sensor_1bb | -0.00370696 | 0.00233289 | 0.00603985 | True | False | False |
| global_t010_subject_t010 | inverse7blend_1040 | -0.00311572 | 0.00285657 | 0.00597229 | True | False | False |
| global_t010_subject_t010 | pair_sensor_1bb_s0p65 | -0.00244102 | 0.00148488 | 0.0039259 | True | False | False |
| global_t010_subject_t010 | raw05_known | 8.69762e-05 | 8.69962e-05 | 2e-08 | False | False | True |
| global_t010_subject_t015 | mixmin_0c916 | -0.0112117 | 0.00943571 | 0.0206474 | True | False | False |
| global_t010_subject_t015 | direns_c4af | -0.0110494 | 0.00931542 | 0.0203648 | True | False | False |
| global_t010_subject_t015 | targetabl_q3s234 | -0.0099473 | 0.00912497 | 0.0190723 | True | False | False |
| global_t010_subject_t015 | targetabl_q3stage | -0.00840163 | 0.00726565 | 0.0156673 | True | False | False |
| global_t010_subject_t015 | pair_sensor_6b | -0.00441576 | 0.00281774 | 0.0072335 | True | False | False |
| global_t010_subject_t015 | pair_sensor_1bb | -0.00371472 | 0.00233289 | 0.0060476 | True | False | False |
| global_t010_subject_t015 | inverse7blend_1040 | -0.0032167 | 0.00296765 | 0.00618435 | True | False | False |
| global_t010_subject_t015 | pair_sensor_1bb_s0p65 | -0.00244606 | 0.00148488 | 0.00393094 | True | False | False |
| global_t010_subject_t015 | raw05_known | 8.69762e-05 | 8.69962e-05 | 2e-08 | False | False | True |

## Decision

- Structured unobserved candidate-scenario cells crossing zero: `32`.
- Structured one-sided improvement cells: `0`.
- Structured one-sided degradation cells: `0`.
- No current unobserved candidate becomes a one-sided improvement even after adding weak/moderate subject-target priors.
- All tested structural priors fit known LB anchors exactly, so remaining sign ambiguity is not caused by infeasible prior assumptions.
