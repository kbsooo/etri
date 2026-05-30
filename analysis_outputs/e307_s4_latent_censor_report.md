# E307 S4 Latent Censor Materializer

Public LB는 사용하지 않았다. E304/E306 latent를 positive S4 generator로 쓰지 않고, current S4 과신을 누그러뜨리는 censor/calibration action으로 바꿔 검증했다.

## Question

S4 병목이 `어디를 올릴까`가 아니라 `어디가 과신인가`라면, hidden block/row state와 current S4 logit의 충돌 row를 0.5 쪽으로 tempering하는 편이 dateblock null보다 건강해야 한다.

## Summary

| n_rows | corr_latent_current_logit | corr_block_row_state | mismatch_top24_current_mean | mismatch_top24_latent_mean | generated_candidates | old_strict | null_evaluated | ready_32rep | best_null_strict_rate | best_mean_dominance | best_dateblock_p90_dominance | best_actual_p90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 250 | 0.302062074 | -0.000000000 | 0.615838046 | 0.261463854 | 765 | 106 | 22 | 0 | 0.750000000 | 0.546875000 | 0.656250000 | -0.000197843 |

## Best Prefilter Rows

| basename | family | nonzero_rows | active_mismatch_mean | delta_latent_alignment | delta_current_alignment | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | strict_promote_gate | pred_beats_current_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e307_s4latentcensor_up_underconf_top64_a0_0700_c4504a0a.csv | up_underconf | 64 | 1.491403393 | 0.418520614 | -0.456319405 | -0.000690069 | -0.000197843 | True | 0.941176471 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_22_cap0_0900_50a04c8a.csv | control_sharpen | 64 | 1.421768395 | -0.145373554 | 0.588857091 | -0.000550715 | -0.000176593 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_up_overconf_top64_a0_0700_6e2d1164.csv | control_wrong_overconf | 64 | 1.421768395 | -0.294323479 | 0.539669455 | -0.000548859 | -0.000175983 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_30_cap0_0900_8c836b44.csv | control_sharpen | 64 | 1.421768395 | -0.140991910 | 0.582813921 | -0.000548545 | -0.000173720 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_16_cap0_0900_c117bd48.csv | control_sharpen | 64 | 1.421768395 | -0.140361285 | 0.599143483 | -0.000538089 | -0.000173081 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_12_cap0_0900_d1965608.csv | control_sharpen | 64 | 1.421768395 | -0.134370341 | 0.612317739 | -0.000518342 | -0.000166624 | True | 0.911764706 |
| submission_e307_s4latentcensor_up_underconf_top50_a0_0700_f2b169c1.csv | up_underconf | 50 | 1.649353493 | 0.385760495 | -0.438916251 | -0.000520732 | -0.000155676 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_08_cap0_0900_64b1dc05.csv | control_sharpen | 64 | 1.421768395 | -0.115691830 | 0.637442671 | -0.000457762 | -0.000147086 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_22_cap0_0700_8a7d369f.csv | control_sharpen | 64 | 1.421768395 | -0.142964147 | 0.583420021 | -0.000437404 | -0.000140489 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_16_cap0_0700_41b622f6.csv | control_sharpen | 64 | 1.421768395 | -0.144761326 | 0.591061367 | -0.000436093 | -0.000139997 | True | 0.911764706 |
| submission_e307_s4latentcensor_up_underconf_top64_a0_0520_170cc538.csv | up_underconf | 64 | 1.491403393 | 0.418520614 | -0.456319405 | -0.000524994 | -0.000139716 | True | 0.941176471 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_30_cap0_0700_1fcab085.csv | control_sharpen | 64 | 1.421768395 | -0.131335006 | 0.579244905 | -0.000428985 | -0.000137864 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_12_cap0_0700_6c77aa36.csv | control_sharpen | 64 | 1.421768395 | -0.139632248 | 0.600170269 | -0.000426435 | -0.000136833 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_up_overconf_top64_a0_0520_625bdcf9.csv | control_wrong_overconf | 64 | 1.421768395 | -0.294323479 | 0.539669455 | -0.000415046 | -0.000128867 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_08_cap0_0700_5018ac6e.csv | control_sharpen | 64 | 1.421768395 | -0.128412230 | 0.620968773 | -0.000396976 | -0.000127320 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_up_overconf_top50_a0_0700_efaacf17.csv | control_wrong_overconf | 50 | 1.590672976 | -0.268904383 | 0.526432105 | -0.000396463 | -0.000127269 | True | 0.911764706 |
| submission_e307_s4latentcensor_up_underconf_top40_a0_0700_d4798834.csv | up_underconf | 40 | 1.779472094 | 0.318094359 | -0.458530933 | -0.000408288 | -0.000125949 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_22_cap0_0900_43cb228e.csv | control_sharpen | 50 | 1.590672976 | -0.138654153 | 0.570616018 | -0.000395992 | -0.000121815 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_30_cap0_0900_9bcb0e28.csv | control_sharpen | 50 | 1.590672976 | -0.135731945 | 0.564363428 | -0.000396361 | -0.000120906 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_16_cap0_0900_366032ce.csv | control_sharpen | 50 | 1.590672976 | -0.132324688 | 0.582157929 | -0.000382627 | -0.000118614 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_12_cap0_0900_0e6969eb.csv | control_sharpen | 50 | 1.590672976 | -0.127468663 | 0.593136810 | -0.000370533 | -0.000116265 | True | 0.911764706 |
| submission_e307_s4latentcensor_up_underconf_top50_a0_0520_53596ba2.csv | up_underconf | 50 | 1.649353493 | 0.385760495 | -0.438916251 | -0.000396951 | -0.000109647 | True | 0.941176471 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_08_cap0_0900_1daced72.csv | control_sharpen | 50 | 1.590672976 | -0.113008205 | 0.608970846 | -0.000342289 | -0.000108246 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_16_cap0_0520_f0593b36.csv | control_sharpen | 64 | 1.421768395 | -0.143516856 | 0.583750388 | -0.000332560 | -0.000105577 | True | 0.911764706 |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_22_cap0_0520_8e185bb8.csv | control_sharpen | 64 | 1.421768395 | -0.131658333 | 0.579378077 | -0.000326253 | -0.000104577 | True | 0.911764706 |

## Governor Rows

| basename | family | nonzero_rows | actual_mean | actual_p90 | null_strict_rate | p90_dominance | mean_dominance | dateblock_p90_dominance | dateblock_mean_dominance | sign_p90_dominance | public_free_ready | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e307_s4latentcensor_up_underconf_top64_a0_0520_170cc538.csv | up_underconf | 64 | -0.000524994 | -0.000139716 | 0.750000000 | 0.421875000 | 0.546875000 | 0.093750000 | 0.343750000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_up_underconf_top64_a0_0700_c4504a0a.csv | up_underconf | 64 | -0.000690069 | -0.000197843 | 0.750000000 | 0.476562500 | 0.515625000 | 0.218750000 | 0.406250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_up_underconf_top50_a0_0520_53596ba2.csv | up_underconf | 50 | -0.000396951 | -0.000109647 | 0.750000000 | 0.445312500 | 0.507812500 | 0.156250000 | 0.562500000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_up_underconf_top40_a0_0700_d4798834.csv | up_underconf | 40 | -0.000408288 | -0.000125949 | 0.750000000 | 0.640625000 | 0.476562500 | 0.437500000 | 0.406250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_up_underconf_top50_a0_0700_f2b169c1.csv | up_underconf | 50 | -0.000520732 | -0.000155676 | 0.750000000 | 0.554687500 | 0.460937500 | 0.218750000 | 0.531250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_12_cap0_0900_0e6969eb.csv | control_sharpen | 50 | -0.000370533 | -0.000116265 | 0.750000000 | 0.492187500 | 0.281250000 | 0.656250000 | 0.125000000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_30_cap0_0900_8c836b44.csv | control_sharpen | 64 | -0.000548545 | -0.000173720 | 0.750000000 | 0.437500000 | 0.281250000 | 0.375000000 | 0.125000000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_30_cap0_0900_9bcb0e28.csv | control_sharpen | 50 | -0.000396361 | -0.000120906 | 0.750000000 | 0.468750000 | 0.273437500 | 0.593750000 | 0.093750000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_16_cap0_0700_41b622f6.csv | control_sharpen | 64 | -0.000436093 | -0.000139997 | 0.750000000 | 0.328125000 | 0.273437500 | 0.187500000 | 0.093750000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_30_cap0_0700_1fcab085.csv | control_sharpen | 64 | -0.000428985 | -0.000137864 | 0.750000000 | 0.359375000 | 0.265625000 | 0.218750000 | 0.062500000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_12_cap0_0700_6c77aa36.csv | control_sharpen | 64 | -0.000426435 | -0.000136833 | 0.750000000 | 0.296875000 | 0.265625000 | 0.093750000 | 0.062500000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_up_overconf_top64_a0_0520_625bdcf9.csv | control_wrong_overconf | 64 | -0.000415046 | -0.000128867 | 0.750000000 | 0.562500000 | 0.257812500 | 0.500000000 | 0.031250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_16_cap0_0900_366032ce.csv | control_sharpen | 50 | -0.000382627 | -0.000118614 | 0.750000000 | 0.421875000 | 0.257812500 | 0.437500000 | 0.031250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_22_cap0_0900_50a04c8a.csv | control_sharpen | 64 | -0.000550715 | -0.000176593 | 0.750000000 | 0.382812500 | 0.257812500 | 0.343750000 | 0.031250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_12_cap0_0900_d1965608.csv | control_sharpen | 64 | -0.000518342 | -0.000166624 | 0.750000000 | 0.429687500 | 0.257812500 | 0.343750000 | 0.031250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_08_cap0_0900_64b1dc05.csv | control_sharpen | 64 | -0.000457762 | -0.000147086 | 0.750000000 | 0.351562500 | 0.257812500 | 0.187500000 | 0.031250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_up_overconf_top64_a0_0700_6e2d1164.csv | control_wrong_overconf | 64 | -0.000548859 | -0.000175983 | 0.750000000 | 0.390625000 | 0.257812500 | 0.156250000 | 0.031250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_22_cap0_0700_8a7d369f.csv | control_sharpen | 64 | -0.000437404 | -0.000140489 | 0.750000000 | 0.312500000 | 0.257812500 | 0.125000000 | 0.000000000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_08_cap0_0700_5018ac6e.csv | control_sharpen | 64 | -0.000396976 | -0.000127320 | 0.750000000 | 0.312500000 | 0.257812500 | 0.125000000 | 0.031250000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top50_s0_22_cap0_0900_43cb228e.csv | control_sharpen | 50 | -0.000395992 | -0.000121815 | 0.750000000 | 0.421875000 | 0.250000000 | 0.531250000 | 0.000000000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_sharpen_overconf_top64_s0_16_cap0_0900_c117bd48.csv | control_sharpen | 64 | -0.000538089 | -0.000173081 | 0.750000000 | 0.343750000 | 0.250000000 | 0.218750000 | 0.000000000 | 1.000000000 | False | do_not_submit |
| submission_e307_s4latentcensor_control_up_overconf_top50_a0_0700_efaacf17.csv | control_wrong_overconf | 50 | -0.000396463 | -0.000127269 | 0.750000000 | 0.312500000 | 0.250000000 | 0.125000000 | 0.000000000 | 1.000000000 | False | do_not_submit |

## Decision

- No E307 candidate survives the local governor.
- This rejects simple S4 latent-vs-current censoring as a direct submission path.
- The useful signal remains diagnostic: hidden row/block state exposes calibration-risk rows, but action health still needs a learned/null-aware translator.

## Outputs

- `analysis_outputs/e307_s4_latent_censor_candidates.csv`
- `analysis_outputs/e307_s4_latent_censor_prefilter.csv`
- `analysis_outputs/e307_s4_latent_censor_governor.csv`
- `analysis_outputs/e307_s4_latent_censor_summary.csv`
- `analysis_outputs/e307_s4_latent_censor_report.md`
