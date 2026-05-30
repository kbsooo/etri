# E256 E247-Family Follow-Up Materializer

## Question

Did public like broad feature-neighbor Q3 smoothness, or only high-amplitude smooth cells?

## Selected Candidate

| file_name | selector_id | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_adverse_reduction_vs_e224 | q3_top1_over_abs_expected | selected_smooth_gain_sum | global_pair_abs_delta | affected_pair_abs_delta | overlap_e237 | overlap_e230_swing25 | overlap_amp_top25 | changed_cells_vs_e224 | sha256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | top50_amp_then_smooth25 | -0.000047418 | 0.000615602 | 0.003037928 | 0.000592484 | 0.615425803 | 2.602320463 | -0.010409282 | -0.070332985 | 14 | 14 | 14 | 25 | 630ea5e2ebedd2b970d87c1a0f7e81d467b7a571dfbd0c3587e35a5d18d2c131 |

## Integrity

- exact sample columns: `True`
- exact sample key order: `True`
- finite probabilities: `True`
- probabilities in [0, 1]: `True`
- changed cells vs E224: `25`, Q3-only: `25`

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
| 158 | id07 | 2024-07-19 | 176 | 8.400505751 | 0.087624411 | 0.087624411 | True | True | False | 15.000000000 | 14.000000000 |
| 222 | id09 | 2024-09-13 | 127 | 11.328305169 | 0.087079113 | 0.087079113 | True | True | False | 16.000000000 | 15.000000000 |
| 105 | id04 | 2024-10-28 | 92 | 6.976889511 | 0.084639705 | 0.084639705 | False | True | False | 19.000000000 | 16.000000000 |
| 230 | id10 | 2024-08-06 | 11 | 12.431508998 | 0.079469447 | 0.079469447 | True | True | False | 24.000000000 | 19.000000000 |
| 236 | id10 | 2024-08-18 | 249 | 24.194023458 | 0.073516109 | 0.073516109 | False | False | False | 27.000000000 | 23.000000000 |
| 164 | id07 | 2024-07-25 | 145 | 7.187945777 | 0.072837843 | 0.072837843 | True | False | False | 29.000000000 | 24.000000000 |
| 166 | id07 | 2024-07-27 | 225 | 9.522033582 | 0.067158810 | 0.067158810 | True | False | False | 37.000000000 | 25.000000000 |
| 247 | id10 | 2024-09-24 | 229 | 9.988407219 | 0.061142840 | 0.061142840 | True | False | False | 43.000000000 | 26.000000000 |
| 231 | id10 | 2024-08-07 | 62 | 7.559314486 | 0.059677581 | 0.059677581 | True | False | False | 46.000000000 | 28.000000000 |
| 116 | id05 | 2024-10-15 | 192 | 12.365574710 | 0.059233896 | 0.059233896 | True | False | False | 47.000000000 | 29.000000000 |
| 109 | id05 | 2024-09-30 | 101 | 7.692863509 | 0.059075977 | 0.059075977 | False | False | False | 49.000000000 | 30.000000000 |
| 87 | id04 | 2024-09-19 | 97 | 6.507120275 | 0.098062305 | 0.029819379 | False | True | False | 13.000000000 | 56.000000000 |
| 188 | id08 | 2024-08-09 | 187 | 6.840844610 | 0.148117043 | 0.019470495 | True | True | False | 4.000000000 | 73.000000000 |
| 138 | id06 | 2024-07-17 | 148 | 8.162324540 | 0.076694286 | -0.000000000 | False | True | False | 25.000000000 | 112.000000000 |
| 96 | id04 | 2024-10-16 | 91 | 7.411892949 | 0.118394039 | -0.000000000 | False | True | False | 10.000000000 | 110.000000000 |

## Public Feedback Decoder

- If E256 beats E247, public prefers high-amplitude smoothing cells and E247 included too much broad smoothness.
- If E256 is close but worse, E247's broader top34 smoothing cells are probably carrying real public signal.
- If E256 fails hard, E247 may depend on a nonlocal interaction between the E224 body and the exact top34 smoothness set.
