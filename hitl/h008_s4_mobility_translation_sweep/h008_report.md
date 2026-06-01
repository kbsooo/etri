# H008 S4 Mobility Translation Sweep

## Question

The S4 mobility latent is locally strong. Which translator from latent state to E247 S4 movement, if any, survives public-free selector stress?

## Bottleneck Diagnosis

- Data: the mobility state is real for S4 under subject/dateblock/null stress.
- Objective: local S4 logloss gains are much larger than the safe E247 postprocess edge, so translation/calibration is the bottleneck.
- Model capacity: not the first bottleneck for S4; the latent is already predictive.
- Evaluation: selector sees many positive-mean moves but rejects broad or over-amplified versions by p90/shape.

## Chosen H007 S4 Latent Model

- feature_set: `mobility_jepa`
- C: `0.05`

## H007 Local S4 Reminder

| feature_set | C | split | delta_logloss | null_median_delta | null_dominance | mean_delta | worst_delta | min_null_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mobility_jepa | 0.050000000 | subject5 | -0.008398233 | 0.008060209 | 1.000000000 | -0.010674892 | -0.008398233 | 1.000000000 |
| mobility_jepa | 0.050000000 | dateblock5 | -0.012951551 | 0.007754474 | 1.000000000 | -0.010674892 | -0.008398233 | 1.000000000 |
| mobility_hypotheses | 0.120000000 | subject5 | -0.008205692 | 0.002090464 | 1.000000000 | -0.009062160 | -0.008205692 | 1.000000000 |
| mobility_hypotheses | 0.120000000 | dateblock5 | -0.009918628 | 0.002985225 | 1.000000000 | -0.009062160 | -0.008205692 | 1.000000000 |
| mobility_hypotheses | 0.350000000 | subject5 | -0.007942409 | 0.002353733 | 1.000000000 | -0.008111187 | -0.007942409 | 1.000000000 |
| mobility_hypotheses | 0.350000000 | dateblock5 | -0.008279964 | 0.001144902 | 1.000000000 | -0.008111187 | -0.007942409 | 1.000000000 |
| mobility_hypotheses | 0.050000000 | subject5 | -0.007765471 | 0.001994070 | 1.000000000 | -0.008938855 | -0.007765471 | 0.916666667 |
| mobility_hypotheses | 0.050000000 | dateblock5 | -0.010112239 | 0.001025081 | 0.916666667 | -0.008938855 | -0.007765471 | 0.916666667 |
| mobility_jepa | 0.120000000 | subject5 | -0.007516982 | 0.004968514 | 1.000000000 | -0.010854691 | -0.007516982 | 1.000000000 |
| mobility_jepa | 0.120000000 | dateblock5 | -0.014192401 | 0.002006117 | 1.000000000 | -0.010854691 | -0.007516982 | 1.000000000 |
| mobility_jepa | 0.800000000 | subject5 | -0.007236747 | 0.010366728 | 0.916666667 | -0.010263650 | -0.007236747 | 0.916666667 |
| mobility_jepa | 0.800000000 | dateblock5 | -0.013290553 | 0.006227273 | 0.916666667 | -0.010263650 | -0.007236747 | 0.916666667 |
| mobility_hypotheses | 0.800000000 | subject5 | -0.007958507 | 0.005476749 | 1.000000000 | -0.007411939 | -0.006865370 | 0.916666667 |
| mobility_hypotheses | 0.800000000 | dateblock5 | -0.006865370 | 0.003743011 | 0.916666667 | -0.007411939 | -0.006865370 | 0.916666667 |
| mobility_jepa | 0.350000000 | subject5 | -0.006244174 | 0.006360705 | 0.916666667 | -0.010033011 | -0.006244174 | 0.916666667 |
| mobility_jepa | 0.350000000 | dateblock5 | -0.013821849 | 0.008591407 | 1.000000000 | -0.010033011 | -0.006244174 | 0.916666667 |
| mobility_routebook | 0.050000000 | subject5 | -0.005614019 | 0.005970320 | 1.000000000 | -0.006239232 | -0.005614019 | 1.000000000 |
| mobility_routebook | 0.050000000 | dateblock5 | -0.006864446 | 0.006182905 | 1.000000000 | -0.006239232 | -0.005614019 | 1.000000000 |
| mobility_routebook | 0.120000000 | subject5 | -0.004342370 | 0.004989098 | 0.916666667 | -0.005090630 | -0.004342370 | 0.833333333 |
| mobility_routebook | 0.120000000 | dateblock5 | -0.005838891 | 0.007674108 | 0.833333333 | -0.005090630 | -0.004342370 | 0.833333333 |

## Signal Summary

| signal | mean | std | min | p10 | median | p90 | max | positive_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| model_delta | 0.032931853 | 0.429423080 | -1.860073385 | -0.414321399 | 0.096210774 | 0.425922762 | 1.382378299 | 0.636000000 |
| model_delta_pos | 0.165591780 | 0.212795693 | 0.000000000 | 0.000000000 | 0.096210774 | 0.425922762 | 1.382378299 | 0.636000000 |
| toward_plus | -0.239868224 | 0.711951879 | -2.517248095 | -1.159697344 | -0.205530736 | 0.655964692 | 1.801605445 | 0.384000000 |
| teacher_rank_centered | -0.049119609 | 0.801959237 | -1.441993892 | -1.218573124 | 0.000000000 | 1.011867714 | 1.258360384 | 0.500000000 |
| balanced_state | -0.025994791 | 0.895756254 | -2.217657959 | -1.221375863 | 0.000000000 | 1.187955482 | 1.963735786 | 0.500000000 |
| anti_energy_state | 0.168967437 | 1.213771604 | -4.261784304 | -1.158235765 | 0.000000000 | 1.811023874 | 4.616494092 | 0.500000000 |
| weekend_state | -0.087484640 | 1.081179029 | -3.631277416 | -1.506929698 | -0.000000000 | 1.057377344 | 3.280326667 | 0.500000000 |
| consensus_score | 0.502000000 | 0.207519315 | 0.148200000 | 0.209600000 | 0.526700000 | 0.752640000 | 0.881600000 | 1.000000000 |
| support_score | 0.502000000 | 0.189619525 | 0.134800000 | 0.254700000 | 0.505700000 | 0.769980000 | 0.898400000 | 1.000000000 |
| low_energy_score | 0.502000000 | 0.288672825 | 0.004000000 | 0.103600000 | 0.502000000 | 0.900400000 | 1.000000000 | 1.000000000 |
| abs_delta_score | 0.502000000 | 0.288672825 | 0.004000000 | 0.103600000 | 0.502000000 | 0.900400000 | 1.000000000 | 1.000000000 |
| toward_abs_score | 0.502000000 | 0.288672825 | 0.004000000 | 0.103600000 | 0.502000000 | 0.900400000 | 1.000000000 | 1.000000000 |

## Translator Family Summary

| family | n | strict | resolution_escape | info | best_mean | best_p90 | best_beats | best_bad_axis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delta_pos | 24 | 0 | 0 | 24 | -0.000028850 | 0.000001621 | 0.861111111 | 0.000059665 |
| state_highlow | 36 | 0 | 0 | 21 | -0.000003521 | 0.000000838 | 0.861111111 | 0.000005109 |
| state_high | 20 | 0 | 0 | 17 | -0.000040187 | 0.000001707 | 0.888888889 | 0.000107873 |
| delta_signed | 20 | 0 | 0 | 15 | -0.000017161 | -0.000001016 | 0.916666667 | 0.000015429 |
| toward_plus | 24 | 0 | 0 | 15 | -0.000008088 | 0.000000969 | 0.861111111 | 0.000003342 |
| orthogonalized | 18 | 0 | 0 | 11 | -0.000035621 | 0.000000223 | 0.861111111 | 0.000017882 |
| continuous_all | 20 | 0 | 0 | 0 | -0.000011376 | -0.000000303 | 0.916666667 | 0.000000313 |
| continuous_orthogonalized | 9 | 0 | 0 | 0 | -0.000017816 | 0.000000706 | 0.583333333 | 0.000155189 |
| down_control | 6 | 0 | 0 | 0 | 0.000005428 | 0.000024243 | 0.180555556 | 0.000241354 |

## Top Candidate Gate

| candidate_id | family | h008_decision | changed_cells | max_abs_prob_delta | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current | shape_gate_70 | shape_gate_120 | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delta_signed_k60_s0.024_c0.01 | delta_signed | too_small_to_submit | 60 | 0.002499994 | -0.000008446 | -0.000026744 | -0.000001016 | 0.916666667 | 0.000119615 | False | True | submission_h008_delta_signed_k60_s0_024_c0_01_0bb3b071.csv |
| delta_signed_k60_s0.016_c0.008 | delta_signed | too_small_to_submit | 60 | 0.001999994 | -0.000006112 | -0.000018626 | -0.000000383 | 0.902777778 | 0.000076230 | True | True | submission_h008_delta_signed_k60_s0_016_c0_008_4fa22482.csv |
| delta_signed_k80_s0.006_c0.004 | delta_signed | too_small_to_submit | 80 | 0.000999995 | -0.000002761 | -0.000009768 | -0.000000154 | 0.902777778 | 0.000037323 | False | True | submission_h008_delta_signed_k80_s0_006_c0_004_40af3892.csv |
| delta_signed_k60_s0.006_c0.004 | delta_signed | too_small_to_submit | 60 | 0.000999995 | -0.000002424 | -0.000006518 | -0.000000065 | 0.902777778 | 0.000025654 | True | True | submission_h008_delta_signed_k60_s0_006_c0_004_99de218a.csv |
| delta_signed_k80_s0.016_c0.008 | delta_signed | too_small_to_submit | 80 | 0.001999994 | -0.000007075 | -0.000028466 | -0.000000064 | 0.902777778 | 0.000107347 | False | True | submission_h008_delta_signed_k80_s0_016_c0_008_00f145da.csv |
| delta_signed_k80_s0.01_c0.006 | delta_signed | too_small_to_submit | 80 | 0.001499995 | -0.000004473 | -0.000016650 | -0.000000058 | 0.902777778 | 0.000065038 | False | True | submission_h008_delta_signed_k80_s0_01_c0_006_f0be6a61.csv |
| delta_signed_k60_s0.01_c0.006 | delta_signed | too_small_to_submit | 60 | 0.001499995 | -0.000003898 | -0.000011240 | 0.000000049 | 0.888888889 | 0.000045590 | True | True | submission_h008_delta_signed_k60_s0_01_c0_006_903ad64d.csv |
| delta_signed_k80_s0.024_c0.01 | delta_signed | too_small_to_submit | 80 | 0.002499994 | -0.000010053 | -0.000042124 | 0.000000181 | 0.861111111 | 0.000166291 | False | True | submission_h008_delta_signed_k80_s0_024_c0_01_ccfa30bf.csv |
| orth_delta_k80_s0.01_c0.006 | orthogonalized | too_small_to_submit | 80 | 0.001499995 | -0.000004695 | -0.000018461 | 0.000000223 | 0.861111111 | 0.000117784 | False | True | submission_h008_orth_delta_k80_s0_01_c0_006_d6cfce4a.csv |
| delta_signed_k100_s0.006_c0.004 | delta_signed | too_small_to_submit | 100 | 0.000999995 | -0.000003576 | -0.000013891 | 0.000000223 | 0.847222222 | 0.000072062 | False | True | submission_h008_delta_signed_k100_s0_006_c0_004_0128af99.csv |
| delta_signed_k100_s0.01_c0.006 | delta_signed | too_small_to_submit | 100 | 0.001499995 | -0.000005840 | -0.000023522 | 0.000000574 | 0.777777778 | 0.000122936 | False | True | submission_h008_delta_signed_k100_s0_01_c0_006_8b0892ab.csv |
| orth_delta_k80_s0.018_c0.008 | orthogonalized | too_small_to_submit | 80 | 0.001999994 | -0.000007271 | -0.000031344 | 0.000000673 | 0.777777778 | 0.000172908 | False | True | submission_h008_orth_delta_k80_s0_018_c0_008_1d8df945.csv |
| balanced_state_highlow_k40_a0.0035 | state_highlow | too_small_to_submit | 80 | 0.000874995 | -0.000002036 | -0.000004425 | 0.000000838 | 0.819444444 | 0.000005109 | False | True | submission_h008_balanced_state_highlow_k40_a0_0035_f208dbc1.csv |
| balanced_state_highlow_k30_a0.0035 | state_highlow | too_small_to_submit | 60 | 0.000874995 | -0.000001631 | -0.000003321 | 0.000000855 | 0.861111111 | 0.000007640 | True | True | submission_h008_balanced_state_highlow_k30_a0_0035_ac239e56.csv |
| orth_delta_k110_s0.01_c0.006 | orthogonalized | too_small_to_submit | 110 | 0.001499995 | -0.000006527 | -0.000027972 | 0.000000911 | 0.597222222 | 0.000215688 | False | True | submission_h008_orth_delta_k110_s0_01_c0_006_08fe0d30.csv |
| toward_plus_cons_k80_s0.006_c0.004 | toward_plus | too_small_to_submit | 80 | 0.000999505 | -0.000003715 | -0.000008985 | 0.000000969 | 0.819444444 | 0.000029288 | False | True | submission_h008_toward_plus_cons_k80_s0_006_c0_004_b4218c21.csv |
| balanced_state_highlow_k20_a0.0035 | state_highlow | too_small_to_submit | 40 | 0.000874995 | -0.000000495 | -0.000001174 | 0.000000978 | 0.833333333 | -0.000017858 | True | True | submission_h008_balanced_state_highlow_k20_a0_0035_6d678736.csv |
| toward_plus_cons_k20_s0.006_c0.004 | toward_plus | too_small_to_submit | 20 | 0.000991760 | -0.000001128 | -0.000002544 | 0.000000991 | 0.777777778 | -0.000003342 | True | True | submission_h008_toward_plus_cons_k20_s0_006_c0_004_45203c16.csv |
| orth_delta_k80_s0.026_c0.01 | orthogonalized | too_small_to_submit | 80 | 0.002499994 | -0.000009655 | -0.000042185 | 0.000001000 | 0.736111111 | 0.000208266 | False | True | submission_h008_orth_delta_k80_s0_026_c0_01_6ec47691.csv |
| delta_signed_k100_s0.016_c0.008 | delta_signed | too_small_to_submit | 100 | 0.001999994 | -0.000009283 | -0.000038645 | 0.000001094 | 0.680555556 | 0.000199984 | False | True | submission_h008_delta_signed_k100_s0_016_c0_008_eed49fb2.csv |
| teacher_rank_centered_highlow_k30_a0.0035 | state_highlow | too_small_to_submit | 60 | 0.000874995 | -0.000001342 | -0.000003861 | 0.000001227 | 0.791666667 | -0.000006303 | True | True | submission_h008_teacher_rank_centered_highlow_k30_a0_0035_c3eb1925.csv |
| balanced_state_highlow_k30_a0.005 | state_highlow | too_small_to_submit | 60 | 0.001249995 | -0.000002417 | -0.000005391 | 0.000001317 | 0.861111111 | 0.000010915 | True | True | submission_h008_balanced_state_highlow_k30_a0_005_54f6ee89.csv |
| balanced_state_highlow_k40_a0.005 | state_highlow | too_small_to_submit | 80 | 0.001249995 | -0.000002962 | -0.000007245 | 0.000001345 | 0.819444444 | 0.000007298 | False | True | submission_h008_balanced_state_highlow_k40_a0_005_1196ffb7.csv |
| anti_energy_state_highlow_k40_a0.0035 | state_highlow | too_small_to_submit | 80 | 0.000874918 | -0.000000470 | -0.000001801 | 0.000001443 | 0.708333333 | -0.000153813 | False | True | submission_h008_anti_energy_state_highlow_k40_a0_0035_cac3f7c7.csv |
| balanced_state_highlow_k20_a0.005 | state_highlow | too_small_to_submit | 40 | 0.001249995 | -0.000000802 | -0.000002306 | 0.000001507 | 0.833333333 | -0.000025512 | True | True | submission_h008_balanced_state_highlow_k20_a0_005_85db0c37.csv |
| toward_plus_cons_k80_s0.01_c0.006 | toward_plus | too_small_to_submit | 80 | 0.001499223 | -0.000005740 | -0.000013805 | 0.000001509 | 0.833333333 | 0.000037812 | False | True | submission_h008_toward_plus_cons_k80_s0_01_c0_006_a14e0b02.csv |
| anti_energy_state_highlow_k30_a0.0035 | state_highlow | too_small_to_submit | 60 | 0.000874918 | -0.000000592 | -0.000001996 | 0.000001555 | 0.750000000 | -0.000137553 | True | True | submission_h008_anti_energy_state_highlow_k30_a0_0035_27a07daf.csv |
| delta_pos_k40_s0.008_c0.004 | delta_pos | too_small_to_submit | 40 | 0.000983097 | -0.000003779 | -0.000015334 | 0.000001621 | 0.861111111 | 0.000133181 | True | True | submission_h008_delta_pos_k40_s0_008_c0_004_4dce1b36.csv |
| toward_plus_cons_k20_s0.01_c0.006 | toward_plus | too_small_to_submit | 20 | 0.001487773 | -0.000001762 | -0.000003705 | 0.000001661 | 0.805555556 | -0.000004146 | True | True | submission_h008_toward_plus_cons_k20_s0_01_c0_006_11cc12ac.csv |
| delta_pos_k20_s0.008_c0.004 | delta_pos | too_small_to_submit | 20 | 0.000953099 | -0.000001750 | -0.000008304 | 0.000001675 | 0.819444444 | 0.000059665 | True | True | submission_h008_delta_pos_k20_s0_008_c0_004_a6c5c1e4.csv |
| toward_plus_cons_k40_s0.01_c0.006 | toward_plus | too_small_to_submit | 40 | 0.001498232 | -0.000003551 | -0.000009036 | 0.000001688 | 0.861111111 | 0.000075037 | True | True | submission_h008_toward_plus_cons_k40_s0_01_c0_006_9828b873.csv |
| delta_pos_k28_s0.008_c0.004 | delta_pos | too_small_to_submit | 28 | 0.000983097 | -0.000002850 | -0.000011668 | 0.000001699 | 0.861111111 | 0.000100241 | True | True | submission_h008_delta_pos_k28_s0_008_c0_004_49b66d96.csv |
| teacher_rank_centered_hi_k20_a0.0035 | state_high | too_small_to_submit | 20 | 0.000872400 | -0.000002635 | -0.000012635 | 0.000001707 | 0.819444444 | 0.000107873 | True | True | submission_h008_teacher_rank_centered_hi_k20_a0_0035_efea87a9.csv |
| toward_plus_cons_k40_s0.018_c0.008 | toward_plus | too_small_to_submit | 40 | 0.001997573 | -0.000005066 | -0.000012249 | 0.000001713 | 0.861111111 | 0.000106323 | True | True | submission_h008_toward_plus_cons_k40_s0_018_c0_008_488a7da7.csv |
| toward_plus_cons_k40_s0.006_c0.004 | toward_plus | too_small_to_submit | 40 | 0.000991760 | -0.000002276 | -0.000005574 | 0.000001763 | 0.847222222 | 0.000047259 | True | True | submission_h008_toward_plus_cons_k40_s0_006_c0_004_080b2992.csv |
| teacher_rank_centered_highlow_k30_a0.005 | state_highlow | too_small_to_submit | 60 | 0.001249995 | -0.000001951 | -0.000006107 | 0.000001894 | 0.791666667 | -0.000009004 | True | True | submission_h008_teacher_rank_centered_highlow_k30_a0_005_1eabf1b0.csv |
| teacher_rank_centered_highlow_k40_a0.0035 | state_highlow | too_small_to_submit | 80 | 0.000874995 | -0.000001689 | -0.000007014 | 0.000002019 | 0.736111111 | 0.000005792 | False | True | submission_h008_teacher_rank_centered_highlow_k40_a0_0035_c6d70a6b.csv |
| toward_plus_cons_k20_s0.018_c0.008 | toward_plus | too_small_to_submit | 20 | 0.001991480 | -0.000002354 | -0.000004827 | 0.000002098 | 0.805555556 | -0.000009628 | True | True | submission_h008_toward_plus_cons_k20_s0_018_c0_008_fef4caf2.csv |
| orth_balanced_k40_s0.01_c0.006 | orthogonalized | too_small_to_submit | 40 | 0.001499021 | -0.000009656 | -0.000040574 | 0.000002181 | 0.847222222 | 0.000412134 | True | True | submission_h008_orth_balanced_k40_s0_01_c0_006_4d6a7d33.csv |
| anti_energy_state_highlow_k40_a0.005 | state_highlow | too_small_to_submit | 80 | 0.001249891 | -0.000000711 | -0.000002800 | 0.000002217 | 0.555555556 | -0.000219733 | False | True | submission_h008_anti_energy_state_highlow_k40_a0_005_7c4df8f2.csv |
| teacher_rank_centered_hi_k36_a0.0035 | state_high | too_small_to_submit | 36 | 0.000874457 | -0.000005828 | -0.000022536 | 0.000002265 | 0.861111111 | 0.000246218 | True | True | submission_h008_teacher_rank_centered_hi_k36_a0_0035_6d631dd3.csv |
| toward_plus_cons_k80_s0.018_c0.008 | toward_plus | too_small_to_submit | 80 | 0.001998917 | -0.000008088 | -0.000019820 | 0.000002270 | 0.819444444 | 0.000012909 | False | True | submission_h008_toward_plus_cons_k80_s0_018_c0_008_e17c3610.csv |
| balanced_state_highlow_k20_a0.007 | state_highlow | too_small_to_submit | 40 | 0.001749995 | -0.000001315 | -0.000004244 | 0.000002298 | 0.819444444 | -0.000035717 | True | True | submission_h008_balanced_state_highlow_k20_a0_007_390e1b5e.csv |
| anti_energy_state_highlow_k30_a0.005 | state_highlow | too_small_to_submit | 60 | 0.001249891 | -0.000000886 | -0.000003279 | 0.000002303 | 0.722222222 | -0.000196504 | True | True | submission_h008_anti_energy_state_highlow_k30_a0_005_27c17a31.csv |
| delta_pos_k40_s0.012_c0.005 | delta_pos | too_small_to_submit | 40 | 0.001248548 | -0.000005291 | -0.000021827 | 0.000002305 | 0.861111111 | 0.000189354 | True | True | submission_h008_delta_pos_k40_s0_012_c0_005_c86b5951.csv |

## Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h008_delta_signed_k60_s0_024_c0_01_0bb3b071.csv | too_small_to_submit | -0.000008446 | -0.000026744 | -0.000001016 | 0.916666667 | 0.000119615 |
| submission_h008_delta_signed_k130_s0_006_c0_004_8bdf3d0c.csv | too_small_to_submit | -0.000004525 | -0.000017994 | -0.000000439 | 0.916666667 | 0.000117542 |
| submission_h008_delta_signed_k60_s0_016_c0_008_4fa22482.csv | too_small_to_submit | -0.000006112 | -0.000018626 | -0.000000383 | 0.902777778 | 0.000076230 |
| submission_h008_delta_signed_k130_s0_01_c0_006_59ed4732.csv | too_small_to_submit | -0.000007418 | -0.000030224 | -0.000000374 | 0.916666667 | 0.000198736 |
| submission_h008_continuous_model_delta_s0_008_c0_006_3cce3935.csv | too_small_to_submit | -0.000007600 | -0.000030723 | -0.000000303 | 0.916666667 | 0.000206909 |
| submission_h008_delta_signed_k130_s0_016_c0_008_d80de9bb.csv | too_small_to_submit | -0.000011801 | -0.000050375 | -0.000000285 | 0.916666667 | 0.000321265 |
| submission_h008_continuous_model_delta_s0_005_c0_005_4d14a44b.csv | too_small_to_submit | -0.000004703 | -0.000018517 | -0.000000195 | 0.902777778 | 0.000112984 |
| submission_h008_continuous_model_delta_s0_0025_c0_0025_f90d275b.csv | too_small_to_submit | -0.000002332 | -0.000009071 | -0.000000179 | 0.916666667 | 0.000056492 |
| submission_h008_delta_signed_k80_s0_006_c0_004_40af3892.csv | too_small_to_submit | -0.000002761 | -0.000009768 | -0.000000154 | 0.902777778 | 0.000037323 |
| submission_h008_delta_signed_k60_s0_006_c0_004_99de218a.csv | too_small_to_submit | -0.000002424 | -0.000006518 | -0.000000065 | 0.902777778 | 0.000025654 |
| submission_h008_delta_signed_k80_s0_016_c0_008_00f145da.csv | too_small_to_submit | -0.000007075 | -0.000028466 | -0.000000064 | 0.902777778 | 0.000107347 |
| submission_h008_delta_signed_k80_s0_01_c0_006_f0be6a61.csv | too_small_to_submit | -0.000004473 | -0.000016650 | -0.000000058 | 0.902777778 | 0.000065038 |
| submission_h008_continuous_model_delta_s0_012_c0_008_fb215c18.csv | too_small_to_submit | -0.000011376 | -0.000047300 | -0.000000021 | 0.888888889 | 0.000321911 |
| submission_h008_delta_signed_k130_s0_024_c0_01_38ff5841.csv | too_small_to_submit | -0.000017161 | -0.000074976 | -0.000000012 | 0.902777778 | 0.000487168 |
| submission_h008_delta_signed_k60_s0_01_c0_006_903ad64d.csv | too_small_to_submit | -0.000003898 | -0.000011240 | 0.000000049 | 0.888888889 | 0.000045590 |
| submission_h008_delta_signed_k80_s0_024_c0_01_ccfa30bf.csv | too_small_to_submit | -0.000010053 | -0.000042124 | 0.000000181 | 0.861111111 | 0.000166291 |
| submission_h008_orth_delta_k80_s0_01_c0_006_d6cfce4a.csv | too_small_to_submit | -0.000004695 | -0.000018461 | 0.000000223 | 0.861111111 | 0.000117784 |
| submission_h008_delta_signed_k100_s0_006_c0_004_0128af99.csv | too_small_to_submit | -0.000003576 | -0.000013891 | 0.000000223 | 0.847222222 | 0.000072062 |
| submission_h008_continuous_anti_energy_state_s0_0025_c0_0025_72f4cdeb.csv | too_small_to_submit | -0.000003287 | -0.000011105 | 0.000000346 | 0.875000000 | 0.000006281 |
| submission_h008_delta_signed_k100_s0_01_c0_006_8b0892ab.csv | too_small_to_submit | -0.000005840 | -0.000023522 | 0.000000574 | 0.777777778 | 0.000122936 |
| submission_h008_orth_delta_k80_s0_018_c0_008_1d8df945.csv | too_small_to_submit | -0.000007271 | -0.000031344 | 0.000000673 | 0.777777778 | 0.000172908 |
| submission_h008_orth_continuous_model_delta_s0_005_c0_005_e9608f10.csv | too_small_to_submit | -0.000005799 | -0.000025251 | 0.000000706 | 0.583333333 | 0.000204033 |
| submission_h008_balanced_state_highlow_k40_a0_0035_f208dbc1.csv | too_small_to_submit | -0.000002036 | -0.000004425 | 0.000000838 | 0.819444444 | 0.000005109 |
| submission_h008_balanced_state_highlow_k30_a0_0035_ac239e56.csv | too_small_to_submit | -0.000001631 | -0.000003321 | 0.000000855 | 0.861111111 | 0.000007640 |
| submission_h008_orth_delta_k110_s0_01_c0_006_08fe0d30.csv | too_small_to_submit | -0.000006527 | -0.000027972 | 0.000000911 | 0.597222222 | 0.000215688 |
| submission_h008_continuous_anti_energy_state_s0_005_c0_005_66410217.csv | too_small_to_submit | -0.000006583 | -0.000022707 | 0.000000933 | 0.875000000 | 0.000012563 |
| submission_h008_toward_plus_cons_k80_s0_006_c0_004_b4218c21.csv | too_small_to_submit | -0.000003715 | -0.000008985 | 0.000000969 | 0.819444444 | 0.000029288 |
| submission_h008_balanced_state_highlow_k20_a0_0035_6d678736.csv | too_small_to_submit | -0.000000495 | -0.000001174 | 0.000000978 | 0.833333333 | -0.000017858 |
| submission_h008_toward_plus_cons_k20_s0_006_c0_004_45203c16.csv | too_small_to_submit | -0.000001128 | -0.000002544 | 0.000000991 | 0.777777778 | -0.000003342 |
| submission_h008_orth_delta_k80_s0_026_c0_01_6ec47691.csv | too_small_to_submit | -0.000009655 | -0.000042185 | 0.000001000 | 0.736111111 | 0.000208266 |
| submission_h008_delta_signed_k100_s0_016_c0_008_eed49fb2.csv | too_small_to_submit | -0.000009283 | -0.000038645 | 0.000001094 | 0.680555556 | 0.000199984 |
| submission_h008_teacher_rank_centered_highlow_k30_a0_0035_c3eb1925.csv | too_small_to_submit | -0.000001342 | -0.000003861 | 0.000001227 | 0.791666667 | -0.000006303 |
| submission_h008_balanced_state_highlow_k30_a0_005_54f6ee89.csv | too_small_to_submit | -0.000002417 | -0.000005391 | 0.000001317 | 0.861111111 | 0.000010915 |
| submission_h008_balanced_state_highlow_k40_a0_005_1196ffb7.csv | too_small_to_submit | -0.000002962 | -0.000007245 | 0.000001345 | 0.819444444 | 0.000007298 |
| submission_h008_continuous_balanced_state_s0_0025_c0_0025_b7e555cd.csv | too_small_to_submit | -0.000001684 | -0.000004171 | 0.000001377 | 0.833333333 | -0.000042377 |
| submission_h008_anti_energy_state_highlow_k40_a0_0035_cac3f7c7.csv | too_small_to_submit | -0.000000470 | -0.000001801 | 0.000001443 | 0.708333333 | -0.000153813 |
| submission_h008_balanced_state_highlow_k20_a0_005_85db0c37.csv | too_small_to_submit | -0.000000802 | -0.000002306 | 0.000001507 | 0.833333333 | -0.000025512 |
| submission_h008_toward_plus_cons_k80_s0_01_c0_006_a14e0b02.csv | too_small_to_submit | -0.000005740 | -0.000013805 | 0.000001509 | 0.833333333 | 0.000037812 |
| submission_h008_anti_energy_state_highlow_k30_a0_0035_27a07daf.csv | too_small_to_submit | -0.000000592 | -0.000001996 | 0.000001555 | 0.750000000 | -0.000137553 |
| submission_h008_delta_pos_k40_s0_008_c0_004_4dce1b36.csv | too_small_to_submit | -0.000003779 | -0.000015334 | 0.000001621 | 0.861111111 | 0.000133181 |
| submission_h008_toward_plus_cons_k20_s0_01_c0_006_11cc12ac.csv | too_small_to_submit | -0.000001762 | -0.000003705 | 0.000001661 | 0.805555556 | -0.000004146 |
| submission_h008_delta_pos_k20_s0_008_c0_004_a6c5c1e4.csv | too_small_to_submit | -0.000001750 | -0.000008304 | 0.000001675 | 0.819444444 | 0.000059665 |
| submission_h008_toward_plus_cons_k40_s0_01_c0_006_9828b873.csv | too_small_to_submit | -0.000003551 | -0.000009036 | 0.000001688 | 0.861111111 | 0.000075037 |
| submission_h008_delta_pos_k28_s0_008_c0_004_49b66d96.csv | too_small_to_submit | -0.000002850 | -0.000011668 | 0.000001699 | 0.861111111 | 0.000100241 |
| submission_h008_teacher_rank_centered_hi_k20_a0_0035_efea87a9.csv | too_small_to_submit | -0.000002635 | -0.000012635 | 0.000001707 | 0.819444444 | 0.000107873 |

## Movement Anatomy

| basename | changed_rows_vs_current | changed_cells_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current | cos_delta_with_h003_tiny | l1_ratio_to_h003_tiny |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h008_delta_pos_k20_s0_008_c0_004_a6c5c1e4.csv | 20 | 20 | 0.045472992 | 0.000953099 | 0.001696009 | 0.003358112 |
| submission_h008_toward_plus_cons_k20_s0_006_c0_004_45203c16.csv | 20 | 20 | 0.053272136 | 0.000991760 | 0.082324629 | 0.003934067 |
| submission_h008_delta_pos_k28_s0_008_c0_004_49b66d96.csv | 28 | 28 | 0.064567636 | 0.000983097 | 0.003418458 | 0.004768222 |
| submission_h008_delta_pos_k20_s0_012_c0_005_d0104be6.csv | 20 | 20 | 0.065671716 | 0.001191245 | 0.000757148 | 0.004849757 |
| submission_h008_teacher_rank_centered_hi_k20_a0_0035_efea87a9.csv | 20 | 20 | 0.070000000 | 0.000872400 | -0.001238037 | 0.005169394 |
| submission_h008_toward_plus_abs_k20_s0_006_c0_004_5cd1b565.csv | 20 | 20 | 0.080000000 | 0.000999908 | 0.113405557 | 0.005907879 |
| submission_h008_toward_plus_cons_k20_s0_01_c0_006_11cc12ac.csv | 20 | 20 | 0.082543758 | 0.001487773 | 0.081719208 | 0.006095731 |
| submission_h008_delta_pos_k40_s0_008_c0_004_4dce1b36.csv | 40 | 40 | 0.084909643 | 0.000983097 | 0.001593395 | 0.006270448 |
| submission_h008_delta_pos_k28_s0_012_c0_005_ac9b6901.csv | 28 | 28 | 0.092408348 | 0.001248548 | 0.004687949 | 0.006824216 |
| submission_h008_teacher_rank_centered_hi_k20_a0_005_c721a3c0.csv | 20 | 20 | 0.100000000 | 0.001246234 | -0.001238037 | 0.007384848 |
| submission_h008_delta_pos_k20_s0_018_c0_008_e246fd57.csv | 20 | 20 | 0.100007574 | 0.001905370 | 0.001314897 | 0.007385408 |
| submission_h008_toward_plus_cons_k40_s0_006_c0_004_080b2992.csv | 40 | 40 | 0.102820522 | 0.000991760 | 0.114403553 | 0.007593140 |
| submission_h008_toward_plus_cons_k20_s0_018_c0_008_fef4caf2.csv | 20 | 20 | 0.118493241 | 0.001991480 | 0.081104809 | 0.008750546 |
| submission_h008_toward_plus_abs_k20_s0_01_c0_006_d298a76c.csv | 20 | 20 | 0.120000000 | 0.001499876 | 0.113405557 | 0.008861818 |
| submission_h008_delta_pos_k40_s0_012_c0_005_c86b5951.csv | 40 | 40 | 0.120971849 | 0.001248548 | 0.001556650 | 0.008933588 |
| submission_h008_teacher_rank_centered_hi_k36_a0_0035_6d631dd3.csv | 36 | 36 | 0.126000000 | 0.000874457 | -0.008939545 | 0.009304909 |
| submission_h008_delta_pos_k60_s0_008_c0_004_169ac783.csv | 59 | 59 | 0.133144314 | 0.000990164 | -0.009770068 | 0.009832506 |
| submission_h008_delta_pos_k20_s0_026_c0_01_161be920.csv | 20 | 20 | 0.139788718 | 0.002381192 | 0.000082576 | 0.010323185 |
| submission_h008_teacher_rank_centered_hi_k20_a0_007_dde3c0a2.csv | 20 | 20 | 0.140000000 | 0.001744630 | -0.001238037 | 0.010338788 |
| submission_h008_anti_energy_state_highlow_k20_a0_0035_55a31a5a.csv | 40 | 40 | 0.140000000 | 0.000874918 | 0.016182875 | 0.010338788 |
| submission_h008_balanced_state_highlow_k20_a0_0035_6d678736.csv | 40 | 40 | 0.140000000 | 0.000874995 | 0.044471146 | 0.010338788 |
| submission_h008_teacher_rank_centered_highlow_k20_a0_0035_c66153c6.csv | 40 | 40 | 0.140000000 | 0.000874995 | 0.069974889 | 0.010338788 |
| submission_h008_down_control_k28_a0_005_aee3c7d6.csv | 28 | 28 | 0.140000000 | 0.001248753 | -0.003962639 | 0.010338788 |
| submission_h008_delta_pos_k28_s0_018_c0_008_1fd07627.csv | 28 | 28 | 0.141112522 | 0.001997573 | 0.004418634 | 0.010420946 |
| submission_h008_toward_plus_cons_k60_s0_006_c0_004_e404e001.csv | 60 | 60 | 0.146423575 | 0.000991760 | 0.132122072 | 0.010813159 |
| submission_h008_delta_signed_k40_s0_006_c0_004_cc47b4bb.csv | 40 | 40 | 0.151301039 | 0.000999995 | 0.061976074 | 0.011173352 |
| submission_h008_toward_plus_abs_k40_s0_006_c0_004_14ad9d0c.csv | 40 | 40 | 0.160000000 | 0.000999995 | 0.179303496 | 0.011815758 |
| submission_h008_toward_plus_abs_k20_s0_018_c0_008_e9ec835a.csv | 20 | 20 | 0.160000000 | 0.001999851 | 0.113405557 | 0.011815758 |
| submission_h008_toward_plus_cons_k40_s0_01_c0_006_9828b873.csv | 40 | 40 | 0.160177378 | 0.001498232 | 0.114201776 | 0.011828857 |
| submission_h008_delta_pos_k80_s0_008_c0_004_d737fdb1.csv | 78 | 78 | 0.164534165 | 0.000990164 | -0.001525762 | 0.012150599 |
| submission_h008_teacher_rank_centered_hi_k50_a0_0035_e895f4f1.csv | 50 | 50 | 0.175000000 | 0.000874898 | -0.023721739 | 0.012923485 |
| submission_h008_continuous_model_delta_s0_0025_c0_0025_f90d275b.csv | 250 | 250 | 0.175626529 | 0.000624938 | 0.056561075 | 0.012969753 |
| submission_h008_teacher_rank_centered_hi_k36_a0_005_7c84f80c.csv | 36 | 36 | 0.180000000 | 0.001249200 | -0.008939545 | 0.013292727 |
| submission_h008_teacher_rank_centered_hi_k20_a0_009_f362fcbc.csv | 20 | 20 | 0.180000000 | 0.002242969 | -0.001238037 | 0.013292727 |
| submission_h008_delta_pos_k40_s0_018_c0_008_fd435586.csv | 40 | 40 | 0.185457773 | 0.001997573 | 0.002122968 | 0.013695776 |
| submission_h008_delta_pos_k60_s0_012_c0_005_b7982525.csv | 59 | 59 | 0.188586407 | 0.001249864 | -0.011381265 | 0.013926820 |
| submission_h008_toward_plus_cons_k80_s0_006_c0_004_b4218c21.csv | 80 | 80 | 0.194954313 | 0.000999505 | 0.148177824 | 0.014397081 |
| submission_h008_delta_pos_k28_s0_026_c0_01_98fcefc3.csv | 28 | 28 | 0.196051420 | 0.002496876 | 0.005009343 | 0.014478100 |
| submission_h008_teacher_rank_centered_highlow_k20_a0_005_13ee81de.csv | 40 | 40 | 0.200000000 | 0.001249995 | 0.069974890 | 0.014769697 |
| submission_h008_balanced_state_highlow_k20_a0_005_85db0c37.csv | 40 | 40 | 0.200000000 | 0.001249995 | 0.044471146 | 0.014769697 |
| submission_h008_anti_energy_state_highlow_k20_a0_005_335c6c08.csv | 40 | 40 | 0.200000000 | 0.001249891 | 0.016182875 | 0.014769697 |
| submission_h008_delta_pos_k100_s0_008_c0_004_e5edf6eb.csv | 94 | 94 | 0.202064677 | 0.000990164 | -0.006350690 | 0.014922170 |
| submission_h008_delta_signed_k60_s0_006_c0_004_99de218a.csv | 60 | 60 | 0.202340508 | 0.000999995 | 0.058937686 | 0.014942540 |
| submission_h008_anti_energy_state_highlow_k30_a0_0035_27a07daf.csv | 60 | 60 | 0.210000000 | 0.000874918 | 0.049980987 | 0.015508182 |
| submission_h008_teacher_rank_centered_highlow_k30_a0_0035_c3eb1925.csv | 60 | 60 | 0.210000000 | 0.000874995 | 0.061835851 | 0.015508182 |

## Selection

_empty_

## Interpretation

- candidates generated: `177`
- strict upload candidates: `0`
- resolution-escape candidates: `0`
- info-gate candidates: `103`
- best selector-ranked candidate: `submission_h008_delta_signed_k60_s0_024_c0_01_0bb3b071.csv` -> `too_small_to_submit`

The sweep confirms the latent direction repeatedly, but all safe movements remain below selector resolution. The next step is integrating the latent before E247 smoothing/stacking rather than post-hoc movement.

## Files

- `hitl/h008_s4_mobility_translation_sweep/h008_candidates.csv`
- `hitl/h008_s4_mobility_translation_sweep/h008_selector_scores.csv`
- `hitl/h008_s4_mobility_translation_sweep/h008_candidate_anatomy.csv`
- `hitl/h008_s4_mobility_translation_sweep/h008_gate_scores.csv`
- `hitl/h008_s4_mobility_translation_sweep/h008_family_summary.csv`
- `hitl/h008_s4_mobility_translation_sweep/h008_signal_summary.csv`
- `hitl/h008_s4_mobility_translation_sweep/h008_selection.csv`
