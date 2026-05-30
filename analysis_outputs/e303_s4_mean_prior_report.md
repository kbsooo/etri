# E303 S4 Mean-Placement Prior Materializer

Public LB는 사용하지 않았다. E302 mean-placement decoder를 실제 S4 mask generator로 바꿔도 large-null gate를 통과하는지 검사했다.

## Summary

| generated_candidates | prefilter_scored | old_strict | null_evaluated | ready_32rep | best_null_strict_rate | best_mean_dominance | best_actual_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 260 | 260 | 183 | 12 | 0 | 0.187500000 | 0.695312500 | -0.000074119 |

## Best Row Prior Scores

| row_idx | subject_id | sleep_date | dateblock_group | s4_source_delta | sign | singleton_prior_score | drop_improvement_vs_all | human_all_single_mean | story_single_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | id01 | 2024-09-04 | id01_b8 | 0.038800000 | pos | -0.000571195 | 0.000011992 | -0.000320677 | -0.000255522 |
| 2 | id01 | 2024-08-02 | id01_b4 | 0.038800000 | pos | -0.000564131 | 0.000011762 | -0.000300208 | -0.000329469 |
| 3 | id01 | 2024-08-03 | id01_b4 | 0.038800000 | pos | -0.000546638 | 0.000011263 | -0.000301201 | -0.000245376 |
| 173 | id07 | 2024-08-23 | id07_b10 | 0.038800000 | pos | -0.000511485 | 0.000010420 | -0.000270106 | -0.000254902 |
| 178 | id07 | 2024-08-29 | id07_b10 | 0.038800000 | pos | -0.000469739 | 0.000009369 | -0.000265554 | -0.000138746 |
| 17 | id01 | 2024-09-05 | id01_b8 | 0.038800000 | pos | -0.000457137 | 0.000009526 | -0.000266026 | -0.000110422 |
| 179 | id07 | 2024-08-30 | id07_b10 | 0.038800000 | pos | -0.000453135 | 0.000009005 | -0.000258359 | -0.000083217 |
| 15 | id01 | 2024-09-03 | id01_b8 | 0.038800000 | pos | -0.000452794 | 0.000009345 | -0.000257880 | -0.000174588 |
| 4 | id01 | 2024-08-04 | id01_b4 | 0.038800000 | pos | -0.000429052 | 0.000008863 | -0.000235808 | -0.000191953 |
| 14 | id01 | 2024-09-02 | id01_b7 | 0.038800000 | pos | -0.000407653 | 0.000008357 | -0.000241322 | -0.000099671 |
| 171 | id07 | 2024-08-20 | id07_b9 | 0.038800000 | pos | -0.000407124 | 0.000008158 | -0.000217843 | -0.000196297 |
| 157 | id07 | 2024-07-19 | id07_b5 | 0.017605788 | pos | -0.000403190 | 0.000005558 | -0.000198990 | -0.000248489 |
| 30 | id02 | 2024-08-29 | id02_b5 | 0.038800000 | pos | -0.000400048 | 0.000007697 | -0.000234274 | -0.000161680 |
| 172 | id07 | 2024-08-21 | id07_b9 | 0.038800000 | pos | -0.000385278 | 0.000007574 | -0.000196279 | -0.000205118 |
| 165 | id07 | 2024-07-27 | id07_b6 | 0.020149540 | pos | -0.000382396 | 0.000006732 | -0.000219312 | -0.000064508 |
| 50 | id02 | 2024-10-07 | id02_b10 | 0.038800000 | pos | -0.000370763 | 0.000007351 | -0.000217511 | -0.000159048 |
| 177 | id07 | 2024-08-28 | id07_b10 | 0.038800000 | pos | -0.000369194 | 0.000007283 | -0.000212083 | -0.000064410 |
| 74 | id03 | 2024-09-21 | id03_b6 | 0.028148106 | pos | -0.000368595 | 0.000005706 | -0.000215423 | -0.000270081 |
| 154 | id07 | 2024-07-16 | id07_b5 | 0.038800000 | pos | -0.000349212 | 0.000006794 | -0.000198561 | -0.000057095 |
| 13 | id01 | 2024-08-17 | id01_b5 | 0.038800000 | pos | -0.000346190 | 0.000007065 | -0.000183758 | -0.000172044 |

## Best Prefilter Rows

| basename | mask_name | multiplier | nonzero_rows | prior_score | human_all_mean_pred | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | strict_promote_gate | pred_beats_current_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m1p16_49421da7.csv | single_prior_drop_worst12 | 1.160000000 | 38 | -0.000557674 | -0.000290856 | -0.000248597 | -0.000072505 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m1p08_2e9c6b0a.csv | single_prior_drop_worst12 | 1.080000000 | 38 | -0.000555852 | -0.000290856 | -0.000232026 | -0.000067198 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m1p00_c641eea9.csv | single_prior_drop_worst12 | 1.000000000 | 38 | -0.000554031 | -0.000290856 | -0.000215251 | -0.000062001 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m0p97_17998fcd.csv | single_prior_drop_worst12 | 0.970000000 | 38 | -0.000553348 | -0.000290856 | -0.000208876 | -0.000060097 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m0p85_709df9bb.csv | single_prior_drop_worst12 | 0.850000000 | 38 | -0.000550617 | -0.000290856 | -0.000183378 | -0.000052481 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m1p16_bd3f44a6.csv | drop_prior_bestdrop12 | 1.160000000 | 38 | -0.000532215 | -0.000280014 | -0.000255293 | -0.000074119 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m1p08_2f81dbc2.csv | drop_prior_bestdrop12 | 1.080000000 | 38 | -0.000530295 | -0.000280014 | -0.000238271 | -0.000068703 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m1p00_1384a0a8.csv | drop_prior_bestdrop12 | 1.000000000 | 38 | -0.000528375 | -0.000280014 | -0.000221041 | -0.000063396 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m0p97_dc251286.csv | drop_prior_bestdrop12 | 0.970000000 | 38 | -0.000527655 | -0.000280014 | -0.000214497 | -0.000061451 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m0p85_a6c6d69b.csv | drop_prior_bestdrop12 | 0.850000000 | 38 | -0.000524774 | -0.000280014 | -0.000188315 | -0.000053669 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_top40_raw_m1p16_7b87b845.csv | single_prior_top40 | 1.160000000 | 40 | -0.000513713 | -0.000263911 | -0.000239368 | -0.000068424 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_top40_raw_m1p08_5da67037.csv | single_prior_top40 | 1.080000000 | 40 | -0.000511995 | -0.000263911 | -0.000223425 | -0.000063397 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_top40_raw_m1p00_9939c182.csv | single_prior_top40 | 1.000000000 | 40 | -0.000510277 | -0.000263911 | -0.000207279 | -0.000058480 | True | 0.941176471 |
| submission_e303_s4meanprior_single_prior_top40_raw_m0p97_09fbd6d8.csv | single_prior_top40 | 0.970000000 | 40 | -0.000509633 | -0.000263911 | -0.000201141 | -0.000056681 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop8_raw_m1p16_54858e5d.csv | drop_prior_bestdrop8 | 1.160000000 | 42 | -0.000508956 | -0.000259559 | -0.000245102 | -0.000068982 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop8_raw_m1p08_b6f4c95d.csv | drop_prior_bestdrop8 | 1.080000000 | 42 | -0.000507178 | -0.000259559 | -0.000228772 | -0.000063918 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop8_raw_m1p00_fe3a8ec8.csv | drop_prior_bestdrop8 | 1.000000000 | 42 | -0.000505400 | -0.000259559 | -0.000212237 | -0.000058964 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_bestdrop8_raw_m0p97_4742f419.csv | drop_prior_bestdrop8 | 0.970000000 | 42 | -0.000504733 | -0.000259559 | -0.000205953 | -0.000057151 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_dateblocks_id03_b4_id08_b5_id08_b9_id03_b6_raw_m1p16_5c5df2d7.csv | drop_prior_dateblocks_id03_b4_id08_b5_id08_b9_id03_b6 | 1.160000000 | 38 | -0.000496012 | -0.000254334 | -0.000222242 | -0.000062132 | True | 0.941176471 |
| submission_e303_s4meanprior_drop_prior_dateblocks_id03_b4_id08_b5_id03_b7_id03_b6_raw_m1p16_b7e0dad9.csv | drop_prior_dateblocks_id03_b4_id08_b5_id03_b7_id03_b6 | 1.160000000 | 36 | -0.000495396 | -0.000256406 | -0.000214077 | -0.000062392 | True | 0.941176471 |

## Governor Rows

| basename | mask_name | multiplier | nonzero_rows | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | worst_mode_p90_dominance | worst_mode_mean_dominance | public_free_ready | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m0p85_709df9bb.csv | single_prior_drop_worst12 | 0.850000000 | 38 | -0.000183378 | -0.000052481 | 0.187500000 | 0.960937500 | 0.593750000 | 0.906250000 | 0.218750000 | False | do_not_submit |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m0p97_17998fcd.csv | single_prior_drop_worst12 | 0.970000000 | 38 | -0.000208876 | -0.000060097 | 0.601562500 | 0.921875000 | 0.617187500 | 0.781250000 | 0.250000000 | False | do_not_submit |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m1p00_c641eea9.csv | single_prior_drop_worst12 | 1.000000000 | 38 | -0.000215251 | -0.000062001 | 0.648437500 | 0.953125000 | 0.609375000 | 0.843750000 | 0.250000000 | False | do_not_submit |
| submission_e303_s4meanprior_single_prior_top44_raw_m1p16_7d5a3340.csv | single_prior_top44 | 1.160000000 | 44 | -0.000219272 | -0.000065931 | 0.687500000 | 0.867187500 | 0.695312500 | 0.625000000 | 0.281250000 | False | do_not_submit |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m1p08_2e9c6b0a.csv | single_prior_drop_worst12 | 1.080000000 | 38 | -0.000232026 | -0.000067198 | 0.703125000 | 0.937500000 | 0.671875000 | 0.812500000 | 0.343750000 | False | do_not_submit |
| submission_e303_s4meanprior_drop_prior_dateblocks_id03_b4_id08_b5_raw_m1p16_a92299fa.csv | drop_prior_dateblocks_id03_b4_id08_b5 | 1.160000000 | 44 | -0.000220837 | -0.000068992 | 0.703125000 | 0.921875000 | 0.546875000 | 0.781250000 | 0.125000000 | False | do_not_submit |
| submission_e303_s4meanprior_drop_prior_dateblocks_id03_b4_id08_b5_id08_b9_id03_b7_raw_m1p16_256222f0.csv | drop_prior_dateblocks_id03_b4_id08_b5_id08_b9_id03_b7 | 1.160000000 | 40 | -0.000234151 | -0.000070968 | 0.718750000 | 0.921875000 | 0.546875000 | 0.843750000 | 0.125000000 | False | do_not_submit |
| submission_e303_s4meanprior_drop_prior_dateblocks_id03_b4_id08_b5_id03_b7_id03_b3_raw_m1p16_5eced2c9.csv | drop_prior_dateblocks_id03_b4_id08_b5_id03_b7_id03_b3 | 1.160000000 | 39 | -0.000223813 | -0.000070189 | 0.718750000 | 0.968750000 | 0.531250000 | 0.906250000 | 0.093750000 | False | do_not_submit |
| submission_e303_s4meanprior_drop_prior_dateblocks_id03_b4_id08_b5_id02_b11_raw_m1p16_5072395d.csv | drop_prior_dateblocks_id03_b4_id08_b5_id02_b11 | 1.160000000 | 43 | -0.000213710 | -0.000068519 | 0.718750000 | 0.984375000 | 0.523437500 | 0.937500000 | 0.093750000 | False | do_not_submit |
| submission_e303_s4meanprior_drop_prior_dateblocks_id03_b4_id08_b5_id03_b7_raw_m1p16_e4320616.csv | drop_prior_dateblocks_id03_b4_id08_b5_id03_b7 | 1.160000000 | 41 | -0.000223411 | -0.000070110 | 0.726562500 | 0.914062500 | 0.617187500 | 0.812500000 | 0.281250000 | False | do_not_submit |
| submission_e303_s4meanprior_single_prior_drop_worst12_raw_m1p16_49421da7.csv | single_prior_drop_worst12 | 1.160000000 | 38 | -0.000248597 | -0.000072505 | 0.734375000 | 0.906250000 | 0.648437500 | 0.750000000 | 0.281250000 | False | do_not_submit |
| submission_e303_s4meanprior_drop_prior_bestdrop12_raw_m1p16_bd3f44a6.csv | drop_prior_bestdrop12 | 1.160000000 | 38 | -0.000255293 | -0.000074119 | 0.742187500 | 0.867187500 | 0.601562500 | 0.593750000 | 0.281250000 | False | do_not_submit |

## Decision

- No E303 candidate survives the 32-rep/mode large-null governor.
- The E302 mean-placement prior is diagnostic, not yet a submission generator.
- This weakens the current S4 mask-surgery branch; the next S4 attempt must add a genuinely new block-placement target or the branch should yield to broader episode/block-state work.

## Outputs

- `analysis_outputs/e303_s4_mean_prior_row_scores.csv`
- `analysis_outputs/e303_s4_mean_prior_candidates.csv`
- `analysis_outputs/e303_s4_mean_prior_prefilter.csv`
- `analysis_outputs/e303_s4_mean_prior_governor.csv`
- `analysis_outputs/e303_s4_mean_prior_summary.csv`
- `analysis_outputs/e303_s4_mean_prior_report.md`
