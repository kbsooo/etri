# E247 Feature-NN1 Smoothing Materializer

## Selected Candidate

| file_name | selector_id | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_adverse_reduction_vs_e224 | q3_top1_over_abs_expected | selected_smooth_gain_sum | global_pair_abs_delta | affected_pair_abs_delta | overlap_e237 | overlap_e230_swing25 | overlap_amp_top25 | changed_cells_vs_e224 | sha256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | nn_smooth_sum_top34 | -0.000066519 | 0.000632592 | 0.005788959 | 0.000596176 | 0.549713494 | 3.555889570 | -0.014223558 | -0.057353058 | 13 | 10 | 10 | 34 | 3f4086d73b23a9c87294986aaa3a8ff32613312e69a398352d6744b8646ce839 |

## Integrity

- exact sample columns: `True`
- exact sample key order: `True`
- finite probabilities: `True`
- probabilities in [0, 1]: `True`
- changed cells vs E224: `34`, Q3-only: `34`

## Selected Rows

| row_idx | subject_id | lifelog_date | nn_row_idx | nn_dist | rollback_amp_abs | single_row_smooth_gain_sum | e237_drop | e230_swing25 | e230_risk21 | amp_rank | smooth_sum_rank |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | id01 | 2024-08-05 | 11 | 5.756405478 | 0.073173666 | 0.292694665 | True | False | True | 28.000000000 | 1.000000000 |
| 150 | id06 | 2024-08-23 | 149 | 7.804752591 | 0.130790886 | 0.261581773 | False | True | True | 7.000000000 | 2.000000000 |
| 212 | id09 | 2024-08-16 | 227 | 5.582383700 | 0.061698478 | 0.185095435 | False | False | False | 41.000000000 | 3.000000000 |
| 51 | id02 | 2024-10-07 | 57 | 5.758088414 | 0.086342959 | 0.172685918 | False | True | True | 17.000000000 | 4.000000000 |
| 223 | id09 | 2024-09-15 | 216 | 10.892144421 | 0.164555230 | 0.164555230 | True | True | True | 2.000000000 | 5.000000000 |
| 196 | id08 | 2024-09-10 | 93 | 6.724752710 | 0.081640143 | 0.163280286 | False | True | False | 21.000000000 | 6.000000000 |
| 52 | id02 | 2024-10-08 | 58 | 8.525645771 | 0.076433549 | 0.152867097 | True | False | True | 26.000000000 | 7.000000000 |
| 235 | id10 | 2024-08-17 | 149 | 24.507019557 | 0.126970109 | 0.126970109 | True | True | True | 8.000000000 | 8.000000000 |
| 237 | id10 | 2024-08-19 | 31 | 21.952995420 | 0.125254982 | 0.125254982 | True | True | True | 9.000000000 | 9.000000000 |
| 160 | id07 | 2024-07-21 | 176 | 7.502250760 | 0.058294682 | 0.116589363 | False | False | False | 50.000000000 | 10.000000000 |
| 162 | id07 | 2024-07-23 | 178 | 7.605421900 | 0.055237816 | 0.110475632 | False | False | False | 55.000000000 | 11.000000000 |
| 168 | id07 | 2024-08-15 | 41 | 6.857151060 | 0.055018176 | 0.110036352 | False | False | False | 56.000000000 | 12.000000000 |
| 76 | id03 | 2024-10-03 | 61 | 5.076948463 | 0.053821989 | 0.107643979 | False | False | False | 58.000000000 | 13.000000000 |
| 158 | id07 | 2024-07-19 | 176 | 8.400505751 | 0.087624411 | 0.087624411 | True | True | False | 15.000000000 | 14.000000000 |
| 222 | id09 | 2024-09-13 | 127 | 11.328305169 | 0.087079113 | 0.087079113 | True | True | False | 16.000000000 | 15.000000000 |
| 105 | id04 | 2024-10-28 | 92 | 6.976889511 | 0.084639705 | 0.084639705 | False | True | False | 19.000000000 | 16.000000000 |
| 48 | id02 | 2024-10-04 | 40 | 5.388359291 | 0.023102742 | 0.084078983 | False | False | False | 139.000000000 | 17.000000000 |
| 64 | id03 | 2024-08-22 | 61 | 7.582414843 | 0.041985655 | 0.083971310 | False | False | False | 85.000000000 | 18.000000000 |
| 230 | id10 | 2024-08-06 | 11 | 12.431508998 | 0.079469447 | 0.079469447 | True | True | False | 24.000000000 | 19.000000000 |
| 46 | id02 | 2024-10-02 | 54 | 6.552474134 | 0.039047327 | 0.078094654 | False | False | False | 92.000000000 | 20.000000000 |
| 134 | id06 | 2024-07-12 | 130 | 4.906629945 | 0.038831354 | 0.077662709 | False | False | False | 94.000000000 | 21.000000000 |
| 99 | id04 | 2024-10-19 | 135 | 5.456103937 | 0.038028851 | 0.076057702 | False | False | False | 95.000000000 | 22.000000000 |
| 236 | id10 | 2024-08-18 | 249 | 24.194023458 | 0.073516109 | 0.073516109 | False | False | False | 27.000000000 | 23.000000000 |
| 164 | id07 | 2024-07-25 | 145 | 7.187945777 | 0.072837843 | 0.072837843 | True | False | False | 29.000000000 | 24.000000000 |
| 166 | id07 | 2024-07-27 | 225 | 9.522033582 | 0.067158810 | 0.067158810 | True | False | False | 37.000000000 | 25.000000000 |
| 247 | id10 | 2024-09-24 | 229 | 9.988407219 | 0.061142840 | 0.061142840 | True | False | False | 43.000000000 | 26.000000000 |
| 108 | id05 | 2024-09-29 | 107 | 6.636000847 | 0.030376547 | 0.060753094 | False | False | False | 114.000000000 | 27.000000000 |
| 231 | id10 | 2024-08-07 | 62 | 7.559314486 | 0.059677581 | 0.059677581 | True | False | False | 46.000000000 | 28.000000000 |
| 116 | id05 | 2024-10-15 | 192 | 12.365574710 | 0.059233896 | 0.059233896 | True | False | False | 47.000000000 | 29.000000000 |
| 109 | id05 | 2024-09-30 | 101 | 7.692863509 | 0.059075977 | 0.059075977 | False | False | False | 49.000000000 | 30.000000000 |
| 90 | id04 | 2024-09-23 | 93 | 5.574703104 | 0.028711579 | 0.057423159 | False | False | False | 118.000000000 | 31.000000000 |
| 77 | id03 | 2024-10-04 | 74 | 5.423085664 | 0.026772210 | 0.053544419 | False | False | False | 126.000000000 | 32.000000000 |
| 65 | id03 | 2024-08-23 | 74 | 5.832526616 | 0.052265851 | 0.052265851 | False | False | False | 59.000000000 | 33.000000000 |
| 103 | id04 | 2024-10-25 | 101 | 6.654290177 | 0.025425569 | 0.050851138 | False | False | False | 133.000000000 | 34.000000000 |

## Submission Interpretation

- This file bets that the recoverable hidden law is not the masked-family S2 translator from E216, but Q3 local consistency under the E207 broad-stage2 feature-nearest-neighbor representation.
- A public improvement would promote feature-NN1 JEPA from diagnostic geometry to actionable selector.
- A public loss would mean the E246 local stress gate is still too close to calibration-prior smoothing and not enough to identify public-safe labels.
