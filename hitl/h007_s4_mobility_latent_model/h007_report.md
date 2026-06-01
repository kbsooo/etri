# H007 S4 Mobility Latent Model

## Question

Does the H006 S4 mobility signal become useful when used as an internal HS-JEPA latent feature rather than a direct postprocess?

## Chosen Downstream Model

- feature_set: `mobility_jepa`
- C: `0.05`
- robust feature-set passes: `16`

## S4 Feature Ablation

| feature_set | C | split | n_added_features | base_loss | plus_loss | delta_logloss | null_median_delta | null_dominance | mean_delta | worst_delta | min_null_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mobility_jepa | 0.050000000 | subject5 | 6 | 0.705569397 | 0.697171163 | -0.008398233 | 0.008060209 | 1.000000000 | -0.010674892 | -0.008398233 | 1.000000000 |
| mobility_jepa | 0.050000000 | dateblock5 | 6 | 0.657419199 | 0.644467648 | -0.012951551 | 0.007754474 | 1.000000000 | -0.010674892 | -0.008398233 | 1.000000000 |
| mobility_hypotheses | 0.120000000 | subject5 | 5 | 0.711608912 | 0.703403221 | -0.008205692 | 0.002090464 | 1.000000000 | -0.009062160 | -0.008205692 | 1.000000000 |
| mobility_hypotheses | 0.120000000 | dateblock5 | 5 | 0.663842884 | 0.653924255 | -0.009918628 | 0.002985225 | 1.000000000 | -0.009062160 | -0.008205692 | 1.000000000 |
| mobility_hypotheses | 0.350000000 | subject5 | 5 | 0.722684352 | 0.714741943 | -0.007942409 | 0.002353733 | 1.000000000 | -0.008111187 | -0.007942409 | 1.000000000 |
| mobility_hypotheses | 0.350000000 | dateblock5 | 5 | 0.670939855 | 0.662659891 | -0.008279964 | 0.001144902 | 1.000000000 | -0.008111187 | -0.007942409 | 1.000000000 |
| mobility_hypotheses | 0.050000000 | subject5 | 5 | 0.705569397 | 0.697803926 | -0.007765471 | 0.001994070 | 1.000000000 | -0.008938855 | -0.007765471 | 0.916666667 |
| mobility_hypotheses | 0.050000000 | dateblock5 | 5 | 0.657419199 | 0.647306960 | -0.010112239 | 0.001025081 | 0.916666667 | -0.008938855 | -0.007765471 | 0.916666667 |
| mobility_jepa | 0.120000000 | subject5 | 6 | 0.711608912 | 0.704091931 | -0.007516982 | 0.004968514 | 1.000000000 | -0.010854691 | -0.007516982 | 1.000000000 |
| mobility_jepa | 0.120000000 | dateblock5 | 6 | 0.663842884 | 0.649650483 | -0.014192401 | 0.002006117 | 1.000000000 | -0.010854691 | -0.007516982 | 1.000000000 |
| mobility_jepa | 0.800000000 | subject5 | 6 | 0.738710010 | 0.731473263 | -0.007236747 | 0.010366728 | 0.916666667 | -0.010263650 | -0.007236747 | 0.916666667 |
| mobility_jepa | 0.800000000 | dateblock5 | 6 | 0.674705420 | 0.661414867 | -0.013290553 | 0.006227273 | 0.916666667 | -0.010263650 | -0.007236747 | 0.916666667 |
| mobility_hypotheses | 0.800000000 | subject5 | 5 | 0.738710010 | 0.730751504 | -0.007958507 | 0.005476749 | 1.000000000 | -0.007411939 | -0.006865370 | 0.916666667 |
| mobility_hypotheses | 0.800000000 | dateblock5 | 5 | 0.674705420 | 0.667840050 | -0.006865370 | 0.003743011 | 0.916666667 | -0.007411939 | -0.006865370 | 0.916666667 |
| mobility_jepa | 0.350000000 | subject5 | 6 | 0.722684352 | 0.716440178 | -0.006244174 | 0.006360705 | 0.916666667 | -0.010033011 | -0.006244174 | 0.916666667 |
| mobility_jepa | 0.350000000 | dateblock5 | 6 | 0.670939855 | 0.657118006 | -0.013821849 | 0.008591407 | 1.000000000 | -0.010033011 | -0.006244174 | 0.916666667 |
| mobility_routebook | 0.050000000 | subject5 | 10 | 0.705569397 | 0.699955378 | -0.005614019 | 0.005970320 | 1.000000000 | -0.006239232 | -0.005614019 | 1.000000000 |
| mobility_routebook | 0.050000000 | dateblock5 | 10 | 0.657419199 | 0.650554753 | -0.006864446 | 0.006182905 | 1.000000000 | -0.006239232 | -0.005614019 | 1.000000000 |
| mobility_routebook | 0.120000000 | subject5 | 10 | 0.711608912 | 0.707266542 | -0.004342370 | 0.004989098 | 0.916666667 | -0.005090630 | -0.004342370 | 0.833333333 |
| mobility_routebook | 0.120000000 | dateblock5 | 10 | 0.663842884 | 0.658003993 | -0.005838891 | 0.007674108 | 0.833333333 | -0.005090630 | -0.004342370 | 0.833333333 |
| mobility_teacher | 0.050000000 | subject5 | 3 | 0.705569397 | 0.701929406 | -0.003639991 | 0.002536060 | 1.000000000 | -0.006175632 | -0.003639991 | 0.833333333 |
| mobility_teacher | 0.050000000 | dateblock5 | 3 | 0.657419199 | 0.648707926 | -0.008711273 | -0.000872348 | 0.833333333 | -0.006175632 | -0.003639991 | 0.833333333 |
| mobility_teacher | 0.120000000 | subject5 | 3 | 0.711608912 | 0.708630229 | -0.002978683 | 0.000931694 | 0.750000000 | -0.006481661 | -0.002978683 | 0.750000000 |
| mobility_teacher | 0.120000000 | dateblock5 | 3 | 0.663842884 | 0.653858245 | -0.009984639 | -0.001688031 | 0.833333333 | -0.006481661 | -0.002978683 | 0.750000000 |
| mobility_teacher | 0.800000000 | subject5 | 3 | 0.738710010 | 0.737108977 | -0.001601033 | 0.002516582 | 0.750000000 | -0.005566939 | -0.001601033 | 0.750000000 |
| mobility_teacher | 0.800000000 | dateblock5 | 3 | 0.674705420 | 0.665172575 | -0.009532845 | 0.000177469 | 1.000000000 | -0.005566939 | -0.001601033 | 0.750000000 |
| mobility_routebook | 0.350000000 | subject5 | 10 | 0.722684352 | 0.721124130 | -0.001560222 | 0.012190123 | 0.916666667 | -0.002507367 | -0.001560222 | 0.916666667 |
| mobility_routebook | 0.350000000 | dateblock5 | 10 | 0.670939855 | 0.667485343 | -0.003454512 | 0.012327651 | 0.916666667 | -0.002507367 | -0.001560222 | 0.916666667 |
| mobility_teacher | 0.350000000 | subject5 | 3 | 0.722684352 | 0.721326596 | -0.001357756 | 0.001314555 | 0.750000000 | -0.005718857 | -0.001357756 | 0.750000000 |
| mobility_teacher | 0.350000000 | dateblock5 | 3 | 0.670939855 | 0.660859896 | -0.010079959 | 0.002603372 | 0.916666667 | -0.005718857 | -0.001357756 | 0.750000000 |
| mobility_interactions | 0.050000000 | subject5 | 10 | 0.705569397 | 0.702613424 | -0.002955973 | 0.005349290 | 0.833333333 | -0.001645680 | -0.000335387 | 0.750000000 |
| mobility_interactions | 0.050000000 | dateblock5 | 10 | 0.657419199 | 0.657083812 | -0.000335387 | 0.007194723 | 0.750000000 | -0.001645680 | -0.000335387 | 0.750000000 |
| mobility_routebook | 0.800000000 | subject5 | 10 | 0.738710010 | 0.739011534 | 0.000301524 | 0.016199027 | 1.000000000 | -0.000611154 | 0.000301524 | 1.000000000 |
| mobility_routebook | 0.800000000 | dateblock5 | 10 | 0.674705420 | 0.673181588 | -0.001523832 | 0.013162343 | 1.000000000 | -0.000611154 | 0.000301524 | 1.000000000 |
| mobility_interactions | 0.120000000 | subject5 | 10 | 0.711608912 | 0.709434860 | -0.002174052 | 0.011057833 | 0.916666667 | 0.000069432 | 0.002312916 | 0.750000000 |
| mobility_interactions | 0.120000000 | dateblock5 | 10 | 0.663842884 | 0.666155800 | 0.002312916 | 0.008064210 | 0.750000000 | 0.000069432 | 0.002312916 | 0.750000000 |
| mobility_interactions | 0.350000000 | subject5 | 10 | 0.722684352 | 0.721063600 | -0.001620752 | 0.014929461 | 1.000000000 | 0.001895542 | 0.005411836 | 0.916666667 |
| mobility_interactions | 0.350000000 | dateblock5 | 10 | 0.670939855 | 0.676351691 | 0.005411836 | 0.010555192 | 0.916666667 | 0.001895542 | 0.005411836 | 0.916666667 |
| mobility_interactions | 0.800000000 | subject5 | 10 | 0.738710010 | 0.734925264 | -0.003784747 | 0.015643556 | 0.916666667 | 0.001741986 | 0.007268719 | 0.916666667 |
| mobility_interactions | 0.800000000 | dateblock5 | 10 | 0.674705420 | 0.681974139 | 0.007268719 | 0.011467120 | 0.916666667 | 0.001741986 | 0.007268719 | 0.916666667 |

## Feature Sources

| hypothesis_id | hidden_human_state | route_key | h005_avg_delta | h005_worst_delta | matched_feature_count | fallback_episodes |
| --- | --- | --- | --- | --- | --- | --- |
| H0704 | weekend_obligation_commute | S4_up|Q2_up|S1_down | -0.000095356 | -0.000085065 | 23 | routine_fragmentation,commute_pressure |
| H0774 | errand_physical_drain | Q1_down|S4_up|S1_down | -0.000093091 | -0.000081202 | 28 | home_recovery,routine_anchor_recovery,routine_fragmentation,physiology_strain |
| H0646 | high_confidence_vehicle_exposure | S4_up|S1_down | -0.000064124 | -0.000062271 | 12 | commute_pressure,measurement_wear_confidence |
| H0568 | errand_fragmentation | S1_down|S4_up|Q1_down | -0.000095829 | -0.000091426 | 4 | routine_fragmentation,cashflow_stress,cashflow_relief_spend |
| H0562 | errand_fragmentation | S1_down|S4_up|Q1_down | -0.000085028 | -0.000081919 | 9 | routine_fragmentation,commute_pressure |
| H0094 | forced_commute_after_badnight | Q3_up|S4_up|Q1_down | -0.000083732 | -0.000079826 | 4 | badnight_aftereffect,bedtime_arousal,commute_pressure |

## Candidate Gate

| candidate_id | h007_decision | mode | rank | changed_cells | max_abs_prob_delta | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current | shape_gate | h007_strict_upload_gate | h007_info_gate | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s4latent_pos_top20_a018_cap008 | too_small_to_submit | pos | consensus | 20 | 0.001999810 | -0.000007911 | 0.000000923 | 0.791666667 | 0.000270199 | True | False | True | submission_h007_s4latent_pos_top20_a018_cap008_4eab106c.csv |
| s4latent_signed_top40_a008_cap004 | too_small_to_submit | signed | absdelta | 40 | 0.000999995 | -0.000000792 | 0.000003002 | 0.777777778 | -0.000016659 | True | False | True | submission_h007_s4latent_signed_top40_a008_cap004_8aef9545.csv |
| s4latent_lowenergy_top28_a016_cap006 | too_small_to_submit | pos | lowenergy | 28 | 0.001499376 | -0.000006740 | 0.000003138 | 0.819444444 | 0.000262428 | True | False | True | submission_h007_s4latent_lowenergy_top28_a016_cap006_21a42c54.csv |
| s4latent_pos_top50_a012_cap005 | too_small_to_submit | pos | consensus | 50 | 0.001249864 | -0.000011392 | 0.000005042 | 0.861111111 | 0.000503240 | True | False | True | submission_h007_s4latent_pos_top50_a012_cap005_2c6bc5c9.csv |
| s4latent_pos_top36_a015_cap006 | too_small_to_submit | pos | consensus | 36 | 0.001499844 | -0.000008642 | 0.000005517 | 0.819444444 | 0.000309330 | True | False | True | submission_h007_s4latent_pos_top36_a015_cap006_3b5b1e47.csv |
| s4latent_lowenergy_top60_a018_cap008 | too_small_to_submit | pos | lowenergy | 57 | 0.001999125 | -0.000016090 | 0.000014160 | 0.722222222 | 0.000636406 | True | False | True | submission_h007_s4latent_lowenergy_top60_a018_cap008_f9f31a85.csv |
| s4latent_signed_top80_a010_cap006 | reject_shape_or_bad_axis | signed | absdelta | 80 | 0.001499995 | -0.000006295 | -0.000000265 | 0.916666667 | 0.000108541 | False | False | False | submission_h007_s4latent_signed_top80_a010_cap006_37820f4c.csv |
| s4latent_pos_top80_a014_cap006 | reject_shape_or_bad_axis | pos | consensus | 80 | 0.001499844 | -0.000020291 | 0.000009124 | 0.861111111 | 0.000878727 | False | False | False | submission_h007_s4latent_pos_top80_a014_cap006_31d9abce.csv |
| s4latent_pos_top50_a024_cap010 | reject_shape_or_bad_axis | pos | consensus | 50 | 0.002499785 | -0.000023174 | 0.000010154 | 0.861111111 | 0.001006480 | False | False | False | submission_h007_s4latent_pos_top50_a024_cap010_1860fc52.csv |
| s4latent_pos_top80_a020_cap008 | reject_shape_or_bad_axis | pos | consensus | 80 | 0.001999810 | -0.000025894 | 0.000012872 | 0.791666667 | 0.001174843 | False | False | False | submission_h007_s4latent_pos_top80_a020_cap008_6e21f037.csv |
| s4latent_down_control_top28_a016_cap006 | shape_ok_but_selector_rejects | down_control | lowenergy | 28 | 0.001499546 | 0.000006695 | 0.000027004 | 0.166666667 | -0.000262428 | True | False | False | submission_h007_s4latent_down_control_top28_a016_cap006_a3613ab8.csv |

## Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h007_s4latent_signed_top80_a010_cap006_37820f4c.csv | too_small_to_submit | -0.000006295 | -0.000025998 | -0.000000265 | 0.916666667 | 0.000108541 |
| submission_h007_s4latent_pos_top20_a018_cap008_4eab106c.csv | too_small_to_submit | -0.000007911 | -0.000033796 | 0.000000923 | 0.791666667 | 0.000270199 |
| submission_h007_s4latent_signed_top40_a008_cap004_8aef9545.csv | too_small_to_submit | -0.000000792 | -0.000002125 | 0.000003002 | 0.777777778 | -0.000016659 |
| submission_h007_s4latent_lowenergy_top28_a016_cap006_21a42c54.csv | too_small_to_submit | -0.000006740 | -0.000028965 | 0.000003138 | 0.819444444 | 0.000262428 |
| submission_h007_s4latent_pos_top50_a012_cap005_2c6bc5c9.csv | too_small_to_submit | -0.000011392 | -0.000048336 | 0.000005042 | 0.861111111 | 0.000503240 |
| submission_h007_s4latent_pos_top36_a015_cap006_3b5b1e47.csv | too_small_to_submit | -0.000008642 | -0.000040959 | 0.000005517 | 0.819444444 | 0.000309330 |
| submission_h007_s4latent_pos_top80_a014_cap006_31d9abce.csv | too_small_to_submit | -0.000020291 | -0.000091065 | 0.000009124 | 0.861111111 | 0.000878727 |
| submission_h007_s4latent_pos_top50_a024_cap010_1860fc52.csv | too_small_to_submit | -0.000023174 | -0.000097971 | 0.000010154 | 0.861111111 | 0.001006480 |
| submission_h007_s4latent_pos_top80_a020_cap008_6e21f037.csv | too_small_to_submit | -0.000025894 | -0.000121102 | 0.000012872 | 0.791666667 | 0.001174843 |
| submission_h007_s4latent_lowenergy_top60_a018_cap008_f9f31a85.csv | too_small_to_submit | -0.000016090 | -0.000079315 | 0.000014160 | 0.722222222 | 0.000636406 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | below_selector_resolution | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_h007_s4latent_down_control_top28_a016_cap006_a3613ab8.csv | below_selector_resolution | 0.000006695 | -0.000003542 | 0.000027004 | 0.166666667 | -0.000262428 |

## Movement Anatomy

| basename | changed_rows_vs_current | changed_cells_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current | cos_delta_with_h003_tiny | l1_ratio_to_h003_tiny |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h007_s4latent_signed_top40_a008_cap004_8aef9545.csv | 40 | 40 | 0.160000000 | 0.000999995 | 0.061189182 | 0.011815758 |
| submission_h007_s4latent_pos_top20_a018_cap008_4eab106c.csv | 20 | 20 | 0.160000000 | 0.001999810 | 0.010096889 | 0.011815758 |
| submission_h007_s4latent_lowenergy_top28_a016_cap006_21a42c54.csv | 28 | 28 | 0.163232953 | 0.001499376 | -0.005703256 | 0.012054506 |
| submission_h007_s4latent_down_control_top28_a016_cap006_a3613ab8.csv | 28 | 28 | 0.163232953 | 0.001499546 | 0.005703256 | 0.012054506 |
| submission_h007_s4latent_pos_top36_a015_cap006_3b5b1e47.csv | 36 | 36 | 0.216000000 | 0.001499844 | -0.009494659 | 0.015951273 |
| submission_h007_s4latent_pos_top50_a012_cap005_2c6bc5c9.csv | 50 | 50 | 0.250000000 | 0.001249864 | -0.009538467 | 0.018462121 |
| submission_h007_s4latent_lowenergy_top60_a018_cap008_f9f31a85.csv | 57 | 57 | 0.425464589 | 0.001999125 | -0.028415947 | 0.031419915 |
| submission_h007_s4latent_pos_top80_a014_cap006_31d9abce.csv | 80 | 80 | 0.466363781 | 0.001499844 | -0.027618202 | 0.034440259 |
| submission_h007_s4latent_signed_top80_a010_cap006_37820f4c.csv | 80 | 80 | 0.480000000 | 0.001499995 | 0.044805760 | 0.035447273 |
| submission_h007_s4latent_pos_top50_a024_cap010_1860fc52.csv | 50 | 50 | 0.500000000 | 0.002499785 | -0.009538467 | 0.036924242 |
| submission_h007_s4latent_pos_top80_a020_cap008_6e21f037.csv | 80 | 80 | 0.623376831 | 0.001999810 | -0.027635883 | 0.046035434 |

## Selection

_empty_

## Interpretation

The mobility latent is locally real for S4: best robust feature set `mobility_jepa` improves both splits with worst delta `-0.008398233`.
No strict upload candidate. Best diagnostic sensor: `submission_h007_s4latent_pos_top20_a018_cap008_4eab106c.csv`.

## Files

- `hitl/h007_s4_mobility_latent_model/h007_s4_mobility_latent_features.parquet`
- `hitl/h007_s4_mobility_latent_model/h007_feature_meta.csv`
- `hitl/h007_s4_mobility_latent_model/h007_s4_feature_ablation.csv`
- `hitl/h007_s4_mobility_latent_model/h007_s4_feature_nulls.csv`
- `hitl/h007_s4_mobility_latent_model/h007_candidates.csv`
- `hitl/h007_s4_mobility_latent_model/h007_selector_scores.csv`
- `hitl/h007_s4_mobility_latent_model/h007_candidate_anatomy.csv`
- `hitl/h007_s4_mobility_latent_model/h007_gate_scores.csv`
- `hitl/h007_s4_mobility_latent_model/h007_selection.csv`
