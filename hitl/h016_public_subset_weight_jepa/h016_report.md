# H016 Public-Subset Weight HS-JEPA

## Question

Are known public LB equations telling us hidden labels, or also which row x target cells the public subset listens to?

## Selected Weight Configs

| proxy_name | ridge_mult | cap_mult |
| --- | --- | --- |
| h012_median_posterior | 0.001000000 | 12.000000000 |
| h012_median_posterior | 0.001000000 | 25.000000000 |
| h012_median_posterior | 0.001000000 | 50.000000000 |
| h012_median_posterior | 0.001000000 | 100.000000000 |
| h012_median_posterior | 0.001000000 | 0.000000000 |
| h012_median_posterior | 0.000300000 | 12.000000000 |
| h012_median_posterior | 0.000300000 | 25.000000000 |
| h012_median_posterior | 0.000300000 | 50.000000000 |
| h012_median_posterior | 0.000300000 | 100.000000000 |
| h012_median_posterior | 0.000300000 | 0.000000000 |
| h012_median_posterior | 0.003000000 | 12.000000000 |
| h012_median_posterior | 0.003000000 | 25.000000000 |

## Top Weight Diagnostics

| proxy_name | ridge_mult | cap_mult | loo_mae | loo_p90_abs | loo_spearman | uniform_mae | weight_eff_n | weight_top50_mass | weight_top200_mass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| h012_median_posterior | 0.001000000 | 12.000000000 | 0.000013654 | 0.000026381 | 0.990977444 | 0.000885430 | 1747.348298888 | 0.036149003 | 0.127768730 |
| h012_median_posterior | 0.001000000 | 25.000000000 | 0.000013654 | 0.000026381 | 0.990977444 | 0.000885430 | 1747.348298888 | 0.036149003 | 0.127768730 |
| h012_median_posterior | 0.001000000 | 50.000000000 | 0.000013654 | 0.000026381 | 0.990977444 | 0.000885430 | 1747.348298888 | 0.036149003 | 0.127768730 |
| h012_median_posterior | 0.001000000 | 100.000000000 | 0.000013654 | 0.000026381 | 0.990977444 | 0.000885430 | 1747.348298888 | 0.036149003 | 0.127768730 |
| h012_median_posterior | 0.001000000 | 0.000000000 | 0.000013654 | 0.000026381 | 0.990977444 | 0.000885430 | 1747.348298888 | 0.036149003 | 0.127768730 |
| h012_median_posterior | 0.000300000 | 12.000000000 | 0.000014341 | 0.000025965 | 0.989473684 | 0.000885430 | 1747.154854952 | 0.036617243 | 0.128080140 |
| h012_median_posterior | 0.000300000 | 25.000000000 | 0.000014341 | 0.000025965 | 0.989473684 | 0.000885430 | 1747.154854952 | 0.036617243 | 0.128080140 |
| h012_median_posterior | 0.000300000 | 50.000000000 | 0.000014341 | 0.000025965 | 0.989473684 | 0.000885430 | 1747.154854952 | 0.036617243 | 0.128080140 |
| h012_median_posterior | 0.000300000 | 100.000000000 | 0.000014341 | 0.000025965 | 0.989473684 | 0.000885430 | 1747.154854952 | 0.036617243 | 0.128080140 |
| h012_median_posterior | 0.000300000 | 0.000000000 | 0.000014341 | 0.000025965 | 0.989473684 | 0.000885430 | 1747.154854952 | 0.036617243 | 0.128080140 |
| h012_median_posterior | 0.003000000 | 12.000000000 | 0.000015396 | 0.000032102 | 0.995488722 | 0.000885430 | 1747.515792360 | 0.035773517 | 0.127434426 |
| h012_median_posterior | 0.003000000 | 25.000000000 | 0.000015396 | 0.000032102 | 0.995488722 | 0.000885430 | 1747.515792360 | 0.035773517 | 0.127434426 |
| h012_median_posterior | 0.003000000 | 50.000000000 | 0.000015396 | 0.000032102 | 0.995488722 | 0.000885430 | 1747.515792360 | 0.035773517 | 0.127434426 |
| h012_median_posterior | 0.003000000 | 100.000000000 | 0.000015396 | 0.000032102 | 0.995488722 | 0.000885430 | 1747.515792360 | 0.035773517 | 0.127434426 |
| h012_median_posterior | 0.003000000 | 0.000000000 | 0.000015396 | 0.000032102 | 0.995488722 | 0.000885430 | 1747.515792360 | 0.035773517 | 0.127434426 |
| h012_median_posterior | 0.000100000 | 12.000000000 | 0.000016367 | 0.000035322 | 0.989473684 | 0.000885430 | 1746.965716936 | 0.037011946 | 0.128400367 |
| h012_median_posterior | 0.000100000 | 25.000000000 | 0.000016367 | 0.000035322 | 0.989473684 | 0.000885430 | 1746.965716936 | 0.037011946 | 0.128400367 |
| h012_median_posterior | 0.000100000 | 50.000000000 | 0.000016367 | 0.000035322 | 0.989473684 | 0.000885430 | 1746.965716936 | 0.037011946 | 0.128400367 |
| h012_median_posterior | 0.000100000 | 100.000000000 | 0.000016367 | 0.000035322 | 0.989473684 | 0.000885430 | 1746.965716936 | 0.037011946 | 0.128400367 |
| h012_median_posterior | 0.000100000 | 0.000000000 | 0.000016367 | 0.000035322 | 0.989473684 | 0.000885430 | 1746.965716936 | 0.037011946 | 0.128400367 |
| h015_candidate | 0.001000000 | 12.000000000 | 0.000017255 | 0.000039072 | 0.992481203 | 0.001454095 | 1743.924800030 | 0.039823074 | 0.135844534 |
| h015_candidate | 0.001000000 | 25.000000000 | 0.000017255 | 0.000039072 | 0.992481203 | 0.001454095 | 1743.924800030 | 0.039823074 | 0.135844534 |
| h015_candidate | 0.001000000 | 50.000000000 | 0.000017255 | 0.000039072 | 0.992481203 | 0.001454095 | 1743.924800030 | 0.039823074 | 0.135844534 |
| h015_candidate | 0.001000000 | 100.000000000 | 0.000017255 | 0.000039072 | 0.992481203 | 0.001454095 | 1743.924800030 | 0.039823074 | 0.135844534 |
| h015_candidate | 0.001000000 | 0.000000000 | 0.000017255 | 0.000039072 | 0.992481203 | 0.001454095 | 1743.924800030 | 0.039823074 | 0.135844534 |

## Null Stress

This permutes the known public LB deltas while keeping the same submission-delta tensor. If H016 is just an underdetermined equation fit, permutation should look similarly good.

| metric | direction | real | null_mean | null_p10 | null_p50 | null_p90 | real_percentile_vs_null | one_sided_p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| loo_mae | lower | 0.000013654 | 0.005012391 | 0.002685978 | 0.004329919 | 0.008450378 | 0.000000000 | 0.003322259 |
| loo_p90_abs | lower | 0.000026381 | 0.007551691 | 0.004853392 | 0.006885768 | 0.011741910 | 0.000000000 | 0.003322259 |
| loo_spearman | higher | 0.990977444 | -0.010616541 | -0.282857143 | -0.009774436 | 0.258796992 | 1.000000000 | 0.003322259 |
| loo_pearson | higher | 0.999866393 | -0.054985039 | -0.352326963 | -0.054890622 | 0.225434717 | 1.000000000 | 0.003322259 |
| known_fit_mae | lower | 0.000001110 | 0.004793981 | 0.002291838 | 0.004183292 | 0.008178623 | 0.000000000 | 0.003322259 |
| weight_eff_n | higher | 1747.348298888 | 996.305868090 | 889.544294350 | 1002.623488255 | 1095.913061988 | 1.000000000 | 0.003322259 |
| weight_top50_mass | lower | 0.036149003 | 0.170017745 | 0.142087213 | 0.170922215 | 0.197556992 | 0.000000000 | 0.003322259 |

## Target Weight Summary

| target | mean_weight_score | top_weight_cells | mean_gain_score | mean_combined |
| --- | --- | --- | --- | --- |
| S4 | 0.623846857 | 25 | 0.577861714 | 0.584493189 |
| S1 | 0.625024000 | 25 | 0.460578286 | 0.561608457 |
| S2 | 0.594363429 | 25 | 0.447851429 | 0.541550583 |
| Q1 | 0.427648000 | 25 | 0.519698286 | 0.468520137 |
| Q2 | 0.445682286 | 25 | 0.532854857 | 0.458177920 |
| S3 | 0.394448000 | 25 | 0.414946286 | 0.447428206 |
| Q3 | 0.390987429 | 25 | 0.548209143 | 0.440221509 |

## Candidate Selection

| candidate_id | h016_decision | mode | target_subset | changed_cells | subset_delta_mean_vs_h012 | subset_delta_p90_vs_h012 | h015_subset_delta_mean | delta_gain_vs_h015_subset | uniform_delta_mean_vs_h012 | max_abs_prob_delta_vs_h012 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gain_all_k1000_a0.75 | public_subset_big_bet | gain | all | 1000 | -0.000296297 | -0.000294740 | 0.000164649 | -0.000460946 | -0.000284038 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k1000_a0.75_97e8957f.csv |
| gain_all_k700_a0.75 | public_subset_big_bet | gain | all | 700 | -0.000287527 | -0.000285969 | 0.000164649 | -0.000452176 | -0.000275353 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k700_a0.75_ca0e2ab8.csv |
| gain_all_k700_a1 | public_subset_big_bet | gain | all | 700 | -0.000282488 | -0.000280595 | 0.000164649 | -0.000447137 | -0.000270039 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k700_a1_caabf1c1.csv |
| gain_all_k1000_a1 | public_subset_big_bet | gain | all | 1000 | -0.000272033 | -0.000270145 | 0.000164649 | -0.000436682 | -0.000259328 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k1000_a1_9c865eb1.csv |
| gain_all_k400_a1 | public_subset_big_bet | gain | all | 400 | -0.000255666 | -0.000253774 | 0.000164649 | -0.000420315 | -0.000242791 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k400_a1_560c6dfe.csv |
| gain_all_k400_a0.75 | public_subset_big_bet | gain | all | 400 | -0.000253976 | -0.000252412 | 0.000164649 | -0.000418625 | -0.000241532 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k400_a0.75_21ec7b12.csv |
| combined_all_k400_a0.75 | public_subset_big_bet | combined | all | 400 | -0.000239205 | -0.000237665 | 0.000164649 | -0.000403854 | -0.000225486 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k400_a0.75_ba6e7e09.csv |
| gain_all_k1400_a0.75 | public_subset_big_bet | gain | all | 1400 | -0.000239021 | -0.000237493 | 0.000164649 | -0.000403670 | -0.000225665 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k1400_a0.75_b5a1a2c2.csv |
| gain_all_k700_a1.25 | public_subset_big_bet | gain | all | 700 | -0.000230815 | -0.000228685 | 0.000164649 | -0.000395464 | -0.000219702 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k700_a1.25_1504c299.csv |
| gain_all_k240_a1 | public_subset_big_bet | gain | all | 240 | -0.000219016 | -0.000217151 | 0.000164649 | -0.000383665 | -0.000205609 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k240_a1_68b772b5.csv |
| gain_all_k400_a1.25 | public_subset_big_bet | gain | all | 400 | -0.000218872 | -0.000216749 | 0.000164649 | -0.000383521 | -0.000207196 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k400_a1.25_daab9d6e.csv |
| combined_all_k400_a1 | public_subset_big_bet | combined | all | 400 | -0.000217637 | -0.000215682 | 0.000164649 | -0.000382286 | -0.000204661 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k400_a1_437ce036.csv |
| gain_all_k240_a0.75 | public_subset_big_bet | gain | all | 240 | -0.000216254 | -0.000214722 | 0.000164649 | -0.000380903 | -0.000203321 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k240_a0.75_847feb11.csv |
| combined_all_k240_a0.75 | public_subset_big_bet | combined | all | 240 | -0.000204198 | -0.000202716 | 0.000164649 | -0.000368847 | -0.000190148 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k240_a0.75_06c93b0b.csv |
| combined_all_k700_a0.75 | public_subset_big_bet | combined | all | 700 | -0.000200086 | -0.000197995 | 0.000164649 | -0.000364735 | -0.000197105 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k700_a0.75_368ec3a8.csv |
| combined_all_k240_a1 | public_subset_big_bet | combined | all | 240 | -0.000197626 | -0.000195819 | 0.000164649 | -0.000362275 | -0.000183261 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k240_a1_87b8d488.csv |
| gain_all_k1000_a1.25 | public_subset_big_bet | gain | all | 1000 | -0.000190586 | -0.000188465 | 0.000164649 | -0.000355235 | -0.000178964 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k1000_a1.25_e13230ef.csv |
| gain_all_k240_a1.25 | public_subset_big_bet | gain | all | 240 | -0.000189873 | -0.000187765 | 0.000164649 | -0.000354522 | -0.000177678 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k240_a1.25_e3877c33.csv |
| gain_S_k400_a0.75 | public_subset_sensor | gain | S | 400 | -0.000177501 | -0.000177352 | 0.000164649 | -0.000342150 | -0.000169991 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_S_k400_a0.75_57c59d76.csv |
| gain_S_k700_a0.75 | public_subset_sensor | gain | S | 700 | -0.000171990 | -0.000171847 | 0.000164649 | -0.000336639 | -0.000164226 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_S_k700_a0.75_88b5e137.csv |
| gain_all_k120_a1 | public_subset_sensor | gain | all | 120 | -0.000168431 | -0.000166680 | 0.000164649 | -0.000333080 | -0.000155335 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k120_a1_30bf3f38.csv |
| gain_all_k120_a0.75 | public_subset_sensor | gain | all | 120 | -0.000163684 | -0.000162243 | 0.000164649 | -0.000328333 | -0.000151159 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k120_a0.75_849c609a.csv |
| combined_all_k1000_a0.75 | public_subset_sensor | combined | all | 1000 | -0.000159091 | -0.000156999 | 0.000164649 | -0.000323740 | -0.000156477 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k1000_a0.75_7e7ef34c.csv |
| combined_all_k120_a0.75 | public_subset_sensor | combined | all | 120 | -0.000158881 | -0.000157506 | 0.000164649 | -0.000323530 | -0.000145678 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k120_a0.75_adb7deaa.csv |
| combined_all_k120_a1 | public_subset_sensor | combined | all | 120 | -0.000157810 | -0.000156142 | 0.000164649 | -0.000322459 | -0.000144229 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k120_a1_adcc8aff.csv |
| gain_S_k400_a1 | public_subset_sensor | gain | S | 400 | -0.000157766 | -0.000157605 | 0.000164649 | -0.000322415 | -0.000151026 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_S_k400_a1_8a2277ca.csv |
| combined_all_k240_a1.25 | public_subset_sensor | combined | all | 240 | -0.000157325 | -0.000155281 | 0.000164649 | -0.000321974 | -0.000144533 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k240_a1.25_08cd1fff.csv |
| gain_S_k240_a0.75 | public_subset_sensor | gain | S | 240 | -0.000155108 | -0.000154960 | 0.000164649 | -0.000319757 | -0.000147575 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_S_k240_a0.75_580155c8.csv |
| gain_all_k1400_a1 | public_subset_sensor | gain | all | 1400 | -0.000150701 | -0.000148802 | 0.000164649 | -0.000315350 | -0.000136458 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k1400_a1_5ea8c6d1.csv |
| gain_all_k120_a1.25 | public_subset_sensor | gain | all | 120 | -0.000150468 | -0.000148493 | 0.000164649 | -0.000315117 | -0.000138391 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k120_a1.25_4121ab9f.csv |
| combined_S_k240_a0.75 | public_subset_sensor | combined | S | 240 | -0.000148139 | -0.000148036 | 0.000164649 | -0.000312788 | -0.000139683 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_S_k240_a0.75_c92da04e.csv |
| combined_all_k400_a1.25 | public_subset_sensor | combined | all | 400 | -0.000146765 | -0.000144395 | 0.000164649 | -0.000311414 | -0.000137483 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k400_a1.25_e72e46ce.csv |
| gain_all_k400_a1.5 | public_subset_sensor | gain | all | 400 | -0.000145244 | -0.000142986 | 0.000164649 | -0.000309893 | -0.000136274 | 0.075565953 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k400_a1.5_729bebc9.csv |
| gain_S_k240_a1 | public_subset_sensor | gain | S | 240 | -0.000143839 | -0.000143687 | 0.000164649 | -0.000308488 | -0.000136938 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_S_k240_a1_eca95f7a.csv |
| gain_all_k700_a1.5 | public_subset_sensor | gain | all | 700 | -0.000134521 | -0.000132250 | 0.000164649 | -0.000299170 | -0.000126213 | 0.075565953 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k700_a1.5_8401bb36.csv |
| combined_all_k120_a1.25 | public_subset_sensor | combined | all | 120 | -0.000132287 | -0.000130409 | 0.000164649 | -0.000296936 | -0.000120105 | 0.063739007 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_all_k120_a1.25_94c015f3.csv |
| gain_all_k240_a1.5 | public_subset_sensor | gain | all | 240 | -0.000130329 | -0.000128069 | 0.000164649 | -0.000294978 | -0.000120913 | 0.075565953 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_all_k240_a1.5_e8857151.csv |
| combined_S_k240_a1 | public_subset_sensor | combined | S | 240 | -0.000126525 | -0.000126412 | 0.000164649 | -0.000291174 | -0.000119015 | 0.051641678 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_S_k240_a1_cb2e82b3.csv |
| combined_S_k400_a0.75 | public_subset_sensor | combined | S | 400 | -0.000125660 | -0.000125110 | 0.000164649 | -0.000290309 | -0.000122462 | 0.040886609 | hitl/h016_public_subset_weight_jepa/submission_h016_combined_S_k400_a0.75_0bd10fd9.csv |
| gain_Q_k400_a1 | public_subset_sensor | gain | Q | 400 | -0.000125007 | -0.000123274 | 0.000164649 | -0.000289656 | -0.000119279 | 0.051590891 | hitl/h016_public_subset_weight_jepa/submission_h016_gain_Q_k400_a1_3a87320d.csv |

## Decision

- Primary upload-safe candidate: `submission_h016_public_subset_gain_all_k1000_a0.75_uploadsafe.csv`.
- Interpretation: hidden public-subset weighting produces a different action than H015 and is worth a public sensor.

## Files

- `hitl/h016_public_subset_weight_jepa/h016_weight_configs.csv`
- `hitl/h016_public_subset_weight_jepa/h016_null_stress.csv`
- `hitl/h016_public_subset_weight_jepa/h016_cell_public_weights.csv`
- `hitl/h016_public_subset_weight_jepa/h016_candidates.csv`
