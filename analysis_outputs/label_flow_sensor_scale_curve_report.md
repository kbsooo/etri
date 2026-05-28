# Label-Flow Sensor Scale Curve

Question: can the E22 pair-only S4/Q3 diagnostic be made smaller while retaining pairwise signal and reducing old-selector downside?

## Reference Full Sensors

- `1bbfb735` full scale: pair p90 `-0.000054316`, old p90 `0.000638679`, pair rate `0.968`, old rate `0.278`.
- `6b9335b1` full scale: pair p90 `-0.000065217`, old p90 `0.000675515`, pair rate `0.968`, old rate `0.278`.

## Summary By Sensor And Mask

| sensor_tag | mask_name | n | pair_p90_negative | scaled_sensor_candidate | two_selector_majority | best_rank_file | best_rank_scale | best_rank_pair_p90 | best_rank_old_p90 | best_rank_pair_rate | best_rank_old_rate | best_pair_file | best_pair_scale | best_pair_p90 | best_pair_old_p90 | best_pair_rate | best_pair_bad_axis | best_pair_movement |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conservative_1bb | full | 9 | 9 | 9 | 0 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s1p00_2d194ea2.csv | 1 | -5.43159e-05 | 0.000638679 | 0.967568 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s1p00_2d194ea2.csv | 1 | -5.43159e-05 | 0.000638679 | 0.967568 | 0.0206675 | 0.0060476 |
| conservative_1bb | q2_q3_s4 | 9 | 9 | 9 | 0 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q2_q3_s4_s1p00_b52c49ad.csv | 1 | -5.43159e-05 | 0.000638679 | 0.967568 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q2_q3_s4_s1p00_b52c49ad.csv | 1 | -5.43159e-05 | 0.000638679 | 0.967568 | 0.0206675 | 0.0060476 |
| conservative_1bb | q3_s4 | 9 | 9 | 9 | 0 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s4_s1p00_51b85df3.csv | 1 | -5.43159e-05 | 0.000638679 | 0.967568 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s4_s1p00_51b85df3.csv | 1 | -5.43159e-05 | 0.000638679 | 0.967568 | 0.0206675 | 0.0060476 |
| conservative_1bb | s3_s4 | 9 | 9 | 9 | 0 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s3_s4_s0p65_6506a412.csv | 0.65 | -3.06422e-05 | 0.000575778 | 0.962162 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s3_s4_s1p00_c3ef8f38.csv | 1 | -4.78974e-05 | 0.000638096 | 0.962162 | 0.0310718 | 0.00535818 |
| conservative_1bb | s4 | 9 | 9 | 9 | 0 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s4_s0p65_58b118ac.csv | 0.65 | -3.06422e-05 | 0.000575778 | 0.962162 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s4_s1p00_987f05e5.csv | 1 | -4.78974e-05 | 0.000638096 | 0.962162 | 0.0310718 | 0.00535818 |
| conservative_1bb | q3 | 9 | 9 | 9 | 0 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s1p00_23ff432f.csv | 1 | -3.86849e-06 | 0.000585813 | 0.940541 | 0.254826 | analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s1p00_23ff432f.csv | 1 | -3.86849e-06 | 0.000585813 | 0.940541 | 0.026682 | 0.000689429 |
| contrast_6b | q3 | 9 | 9 | 9 | 0 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q3_s0p75_6ff5ca87.csv | 0.75 | -3.30134e-06 | 0.000584887 | 0.943243 | 0.243243 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q3_s1p00_6f5c91bf.csv | 1 | -4.43898e-06 | 0.000589757 | 0.937838 | 0.0252286 | 0.000825926 |
| contrast_6b | full | 9 | 9 | 7 | 0 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_full_s1p00_c524cc11.csv | 1 | -6.52173e-05 | 0.000675515 | 0.967568 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_full_s1p00_c524cc11.csv | 1 | -6.52173e-05 | 0.000675515 | 0.967568 | 0.0172468 | 0.0072335 |
| contrast_6b | q2_q3_s4 | 9 | 9 | 7 | 0 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q2_q3_s4_s1p00_224dffb3.csv | 1 | -6.52173e-05 | 0.000675515 | 0.967568 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q2_q3_s4_s1p00_224dffb3.csv | 1 | -6.52173e-05 | 0.000675515 | 0.967568 | 0.0172468 | 0.0072335 |
| contrast_6b | q3_s4 | 9 | 9 | 7 | 0 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q3_s4_s1p00_e5c4b68f.csv | 1 | -6.52173e-05 | 0.000675515 | 0.967568 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q3_s4_s1p00_e5c4b68f.csv | 1 | -6.52173e-05 | 0.000675515 | 0.967568 | 0.0172468 | 0.0072335 |
| contrast_6b | s3_s4 | 9 | 9 | 7 | 0 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_s3_s4_s0p50_39d955a3.csv | 0.5 | -2.81677e-05 | 0.000560863 | 0.962162 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_s3_s4_s1p00_917de0b1.csv | 1 | -5.73718e-05 | 0.000669738 | 0.962162 | 0.0299867 | 0.00640758 |
| contrast_6b | s4 | 9 | 9 | 7 | 0 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_s4_s0p50_a2fe323a.csv | 0.5 | -2.81677e-05 | 0.000560863 | 0.962162 | 0.277992 | analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_s4_s1p00_a86a6272.csv | 1 | -5.73718e-05 | 0.000669738 | 0.962162 | 0.0299867 | 0.00640758 |

## Shortlist

| source_path | sensor_tag | mask_name | scale | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | movement_scale | two_selector_majority | sensor_curve_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s1p00_2d194ea2.csv | conservative_1bb | full | 1 | -5.43159e-05 | 0.967568 | 0.000638679 | 0.277992 | 0.0206675 | 0.0060476 | False | 9.45602e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s4_s1p00_51b85df3.csv | conservative_1bb | q3_s4 | 1 | -5.43159e-05 | 0.967568 | 0.000638679 | 0.277992 | 0.0206675 | 0.0060476 | False | 9.45602e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q2_q3_s4_s1p00_b52c49ad.csv | conservative_1bb | q2_q3_s4 | 1 | -5.43159e-05 | 0.967568 | 0.000638679 | 0.277992 | 0.0206675 | 0.0060476 | False | 9.45602e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | conservative_1bb | full | 0.65 | -3.4496e-05 | 0.967568 | 0.000571958 | 0.277992 | 0.0263509 | 0.00393094 | False | 9.56152e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s4_s0p65_4ee051ec.csv | conservative_1bb | q3_s4 | 0.65 | -3.4496e-05 | 0.967568 | 0.000571958 | 0.277992 | 0.0263509 | 0.00393094 | False | 9.56152e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q2_q3_s4_s0p65_12898629.csv | conservative_1bb | q2_q3_s4 | 0.65 | -3.4496e-05 | 0.967568 | 0.000571958 | 0.277992 | 0.0263509 | 0.00393094 | False | 9.56152e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p85_7ac268f8.csv | conservative_1bb | full | 0.85 | -4.58032e-05 | 0.967568 | 0.000612811 | 0.277992 | 0.0231033 | 0.00514046 | False | 9.5849e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s4_s0p85_164a5702.csv | conservative_1bb | q3_s4 | 0.85 | -4.58032e-05 | 0.967568 | 0.000612811 | 0.277992 | 0.0231033 | 0.00514046 | False | 9.5849e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q2_q3_s4_s0p85_4a59326c.csv | conservative_1bb | q2_q3_s4 | 0.85 | -4.58032e-05 | 0.967568 | 0.000612811 | 0.277992 | 0.0231033 | 0.00514046 | False | 9.5849e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q3_s4_s0p50_82ebf12c.csv | contrast_6b | q3_s4 | 0.5 | -3.11672e-05 | 0.967568 | 0.000564391 | 0.277992 | 0.0270763 | 0.00361675 | False | 9.68302e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q2_q3_s4_s0p50_381c4aab.csv | contrast_6b | q2_q3_s4 | 0.5 | -3.11672e-05 | 0.967568 | 0.000564391 | 0.277992 | 0.0270763 | 0.00361675 | False | 9.68302e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_full_s0p50_4e81a042.csv | contrast_6b | full | 0.5 | -3.11672e-05 | 0.967568 | 0.000564391 | 0.277992 | 0.0270763 | 0.00361675 | False | 9.68302e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_full_s0p75_9b3cec74.csv | contrast_6b | full | 0.75 | -4.7858e-05 | 0.967568 | 0.000626328 | 0.277992 | 0.0221616 | 0.00542513 | False | 9.76365e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q3_s4_s0p75_970b225b.csv | contrast_6b | q3_s4 | 0.75 | -4.7858e-05 | 0.967568 | 0.000626328 | 0.277992 | 0.0221616 | 0.00542513 | False | 9.76365e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q2_q3_s4_s0p75_9d7b1906.csv | contrast_6b | q2_q3_s4 | 0.75 | -4.7858e-05 | 0.967568 | 0.000626328 | 0.277992 | 0.0221616 | 0.00542513 | False | 9.76365e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_full_s0p65_106628a6.csv | contrast_6b | full | 0.65 | -4.10967e-05 | 0.967568 | 0.000603824 | 0.277992 | 0.0241275 | 0.00470178 | False | 9.808e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q3_s4_s0p65_6e481f88.csv | contrast_6b | q3_s4 | 0.65 | -4.10967e-05 | 0.967568 | 0.000603824 | 0.277992 | 0.0241275 | 0.00470178 | False | 9.808e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q2_q3_s4_s0p65_c629d990.csv | contrast_6b | q2_q3_s4 | 0.65 | -4.10967e-05 | 0.967568 | 0.000603824 | 0.277992 | 0.0241275 | 0.00470178 | False | 9.808e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p75_d5c565bc.csv | conservative_1bb | full | 0.75 | -4.01105e-05 | 0.967568 | 0.000600326 | 0.277992 | 0.0247271 | 0.0045357 | False | 9.81536e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s4_s0p75_b542e805.csv | conservative_1bb | q3_s4 | 0.75 | -4.01105e-05 | 0.967568 | 0.000600326 | 0.277992 | 0.0247271 | 0.0045357 | False | 9.81536e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q2_q3_s4_s0p75_f3f5d85e.csv | conservative_1bb | q2_q3_s4 | 0.75 | -4.01105e-05 | 0.967568 | 0.000600326 | 0.277992 | 0.0247271 | 0.0045357 | False | 9.81536e-05 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_s3_s4_s0p50_39d955a3.csv | contrast_6b | s3_s4 | 0.5 | -2.81677e-05 | 0.962162 | 0.000560863 | 0.277992 | 0.0334462 | 0.00320379 | False | 0.000100601 |
| analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_s4_s0p50_a2fe323a.csv | contrast_6b | s4 | 0.5 | -2.81677e-05 | 0.962162 | 0.000560863 | 0.277992 | 0.0334462 | 0.00320379 | False | 0.000100601 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q2_q3_s4_s0p50_d36c2306.csv | conservative_1bb | q2_q3_s4 | 0.5 | -2.62271e-05 | 0.967568 | 0.000561146 | 0.277992 | 0.0287866 | 0.0030238 | False | 0.000101177 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_q3_s4_s0p50_33c76a92.csv | conservative_1bb | q3_s4 | 0.5 | -2.62271e-05 | 0.967568 | 0.000561146 | 0.277992 | 0.0287866 | 0.0030238 | False | 0.000101177 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p50_810ea5b1.csv | conservative_1bb | full | 0.5 | -2.62271e-05 | 0.967568 | 0.000561146 | 0.277992 | 0.0287866 | 0.0030238 | False | 0.000101177 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s4_s0p65_58b118ac.csv | conservative_1bb | s4 | 0.65 | -3.06422e-05 | 0.962162 | 0.000575778 | 0.277992 | 0.0331137 | 0.00348281 | False | 0.00010254 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s3_s4_s0p65_6506a412.csv | conservative_1bb | s3_s4 | 0.65 | -3.06422e-05 | 0.962162 | 0.000575778 | 0.277992 | 0.0331137 | 0.00348281 | False | 0.00010254 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s4_s1p00_987f05e5.csv | conservative_1bb | s4 | 1 | -4.78974e-05 | 0.962162 | 0.000638096 | 0.277992 | 0.0310718 | 0.00535818 | False | 0.00010362 |
| analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s3_s4_s1p00_c3ef8f38.csv | conservative_1bb | s3_s4 | 1 | -4.78974e-05 | 0.962162 | 0.000638096 | 0.277992 | 0.0310718 | 0.00535818 | False | 0.00010362 |

## Decision

- Best balanced lower-risk sensor is `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv`: pair p90 `-0.000034496`, old p90 `0.000571958`, movement `0.003931`.
- Lowest-old-risk pairwise-negative sensor is `analysis_outputs/submission_label_flow_sensorcurve_conservative_1bb_s3_s4_s0p35_1a1ac81b.csv`: pair p90 `-0.000016726`, old p90 `0.000550965`, movement `0.001875`.
- Maximum pairwise contrast remains `analysis_outputs/submission_label_flow_sensorcurve_contrast_6b_q2_q3_s4_s1p00_224dffb3.csv` with pair p90 `-0.000065217`, but it has old p90 `0.000675515`.
- No scale or mask creates two-selector majority. Scaling lowers old p90, but the old scenario beat rate stays below majority, so the conflict is directional rather than only amplitude-driven.
- E23 therefore does not create an improvement candidate. It only offers a lower-movement diagnostic alternative if public risk control matters more than maximum contrast.

## Files

- `label_flow_sensor_scale_curve.csv`
- `label_flow_sensor_scale_curve_summary.csv`
- `label_flow_sensor_scale_curve_shortlist.csv`
