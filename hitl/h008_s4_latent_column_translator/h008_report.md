# H008 S4 Latent Column Translator

## Question

Can the strong H007 S4 mobility latent beat the tiny-edit bottleneck by blending the S4 column toward a supervised latent model?

## S4 Model Prediction Summary

| n_test | s4_latent_prob_mean | s4_calendar_prob_mean | latent_minus_calendar_logit_mean | latent_minus_calendar_logit_std |
| --- | --- | --- | --- | --- |
| 250 | 0.519105462 | 0.512206578 | 0.032931853 | 0.429423080 |

## Candidate Gate

| candidate_id | h008_decision | mode | changed_cells | max_abs_prob_delta | pred_delta_vs_current_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current | shape_soft_gate | h008_strict_upload_gate | h008_aggressive_gate | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| delta_two_tail_top60_w0p055_cap0p018 | hitl_aggressive_candidate | delta_two_tail | 60 | 0.004499804 | -0.000024789 | -0.000001341 | 0.916666667 | 0.000645407 | True | False | True | submission_h008_delta_two_tail_top60_w0p055_cap0p018_8c3be15b.csv |
| delta_two_tail_top40_w0p06_cap0p018 | hitl_aggressive_candidate | delta_two_tail | 40 | 0.004499804 | -0.000014591 | -0.000000865 | 0.902777778 | 0.000268902 | True | False | True | submission_h008_delta_two_tail_top40_w0p06_cap0p018_8b8f36d8.csv |
| delta_two_tail_top80_w0p045_cap0p015 | hitl_aggressive_candidate | delta_two_tail | 80 | 0.003749981 | -0.000024241 | 0.000000489 | 0.888888889 | 0.000267230 | True | False | True | submission_h008_delta_two_tail_top80_w0p045_cap0p015_547cbcc2.csv |
| two_tail_refine_top40_w0p078_cap0p02 | hitl_aggressive_candidate | two_tail | 40 | 0.004999942 | -0.000014006 | 0.000003470 | 0.819444444 | -0.000115509 | True | False | True | submission_h008_two_tail_refine_top40_w0p078_cap0p02_de3c9844.csv |
| two_tail_refine_top40_w0p07_cap0p02 | hitl_aggressive_candidate | two_tail | 40 | 0.004999942 | -0.000013403 | 0.000004798 | 0.819444444 | -0.000143537 | True | False | True | submission_h008_two_tail_refine_top40_w0p07_cap0p02_cf14d4ad.csv |
| two_tail_refine_top60_w0p06_cap0p018 | hitl_aggressive_candidate | two_tail | 56 | 0.004499962 | -0.000011716 | 0.000008552 | 0.861111111 | -0.000116131 | True | False | True | submission_h008_two_tail_refine_top60_w0p06_cap0p018_e7267013.csv |
| two_tail_top60_w0p07_cap0p02 | hitl_aggressive_candidate | two_tail | 56 | 0.004999942 | -0.000013224 | 0.000008971 | 0.847222222 | -0.000118467 | True | False | True | submission_h008_two_tail_top60_w0p07_cap0p02_2a35fb28.csv |
| two_tail_refine_top50_w0p07_cap0p02 | hitl_aggressive_candidate | two_tail | 49 | 0.004999942 | -0.000013409 | 0.000011967 | 0.861111111 | -0.000133541 | True | False | True | submission_h008_two_tail_refine_top50_w0p07_cap0p02_244cc9c6.csv |
| pos_consensus_top40_w0p06_cap0p02 | hitl_aggressive_candidate | pos_consensus | 35 | 0.004992809 | -0.000031995 | 0.000011978 | 0.847222222 | 0.000834765 | True | False | True | submission_h008_pos_consensus_top40_w0p06_cap0p02_3b6dcb31.csv |
| two_tail_refine_top30_w0p075_cap0p02 | too_small_to_submit | two_tail | 30 | 0.004999942 | -0.000009208 | 0.000008858 | 0.833333333 | -0.000118996 | True | False | False | submission_h008_two_tail_refine_top30_w0p075_cap0p02_a47ca1a1.csv |
| lowenergy_signed_top60_w0p07_cap0p02 | too_small_to_submit | lowenergy_signed | 60 | 0.004999459 | -0.000011860 | 0.000013948 | 0.819444444 | -0.000130613 | True | False | False | submission_h008_lowenergy_signed_top60_w0p07_cap0p02_392260e9.csv |
| pos_consensus_top80_w0p05_cap0p018 | too_small_to_submit | pos_consensus | 57 | 0.004496989 | -0.000044516 | 0.000016478 | 0.847222222 | 0.001142098 | True | False | False | submission_h008_pos_consensus_top80_w0p05_cap0p018_68342464.csv |
| pos_consensus_top60_w0p06_cap0p02 | too_small_to_submit | pos_consensus | 47 | 0.004996517 | -0.000044027 | 0.000016519 | 0.861111111 | 0.001156036 | True | False | False | submission_h008_pos_consensus_top60_w0p06_cap0p02_f5b53b78.csv |
| pos_consensus_top120_w0p04_cap0p015 | too_small_to_submit | pos_consensus | 75 | 0.003748884 | -0.000045978 | 0.000019136 | 0.861111111 | 0.001102730 | True | False | False | submission_h008_pos_consensus_top120_w0p04_cap0p015_d217451c.csv |
| lowenergy_signed_top90_w0p06_cap0p018 | too_small_to_submit | lowenergy_signed | 90 | 0.004499564 | -0.000013740 | 0.000019715 | 0.833333333 | -0.000240114 | True | False | False | submission_h008_lowenergy_signed_top90_w0p06_cap0p018_c9d070a4.csv |
| lowenergy_signed_top120_w0p05_cap0p016 | too_small_to_submit | lowenergy_signed | 120 | 0.003999976 | -0.000003760 | 0.000054090 | 0.722222222 | -0.000981130 | True | False | False | submission_h008_lowenergy_signed_top120_w0p05_cap0p016_cc51269e.csv |
| two_tail_top40_w0p08_cap0p022 | reject_shape_or_bad_axis | two_tail | 40 | 0.005499916 | -0.000014952 | 0.000004666 | 0.819444444 | -0.000145704 | False | False | False | submission_h008_two_tail_top40_w0p08_cap0p022_4adeaffd.csv |
| full_logit_blend_w0p015 | reject_shape_or_bad_axis | full_blend | 250 | 0.007877345 | -0.000000453 | 0.000088501 | 0.694444444 | -0.001627249 | False | False | False | submission_h008_full_logit_blend_w0p015_0dcd5e48.csv |
| full_logit_blend_w0p025 | reject_shape_or_bad_axis | full_blend | 250 | 0.013128434 | -0.000001625 | 0.000138662 | 0.680555556 | -0.002712081 | False | False | False | submission_h008_full_logit_blend_w0p025_1abf6cae.csv |
| down_control_highmob_top60_w0p06_cap0p02 | shape_ok_but_selector_rejects | down_control | 47 | 0.004998639 | 0.000037654 | 0.000138754 | 0.194444444 | -0.001156036 | True | False | False | submission_h008_down_control_highmob_top60_w0p06_cap0p02_c0efea43.csv |
| full_logit_blend_w0p04 | reject_shape_or_bad_axis | full_blend | 250 | 0.019995555 | -0.000004639 | 0.000182032 | 0.652777778 | -0.004279857 | False | False | False | submission_h008_full_logit_blend_w0p04_704ab61d.csv |
| full_logit_blend_w0p065 | reject_shape_or_bad_axis | full_blend | 250 | 0.019995555 | 0.000003451 | 0.000230587 | 0.333333333 | -0.006449755 | False | False | False | submission_h008_full_logit_blend_w0p065_62ea8f37.csv |
| full_logit_blend_w0p09 | reject_shape_or_bad_axis | full_blend | 250 | 0.019995555 | 0.000005668 | 0.000335486 | 0.347222222 | -0.007879083 | False | False | False | submission_h008_full_logit_blend_w0p09_094917ab.csv |

## Candidate Geometry

| candidate_id | mode | changed_cells | l1_logit_move | max_abs_prob_delta | selected_raw_delta_mean | selected_mobility_rank_mean | selected_low_energy_mean | basename |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_logit_blend_w0p015 | full_blend | 250 | 2.173443351 | 0.007877345 | -0.239868224 | 0.517074783 | 0.501000000 | submission_h008_full_logit_blend_w0p015_0dcd5e48.csv |
| full_logit_blend_w0p025 | full_blend | 250 | 3.622405585 | 0.013128434 | -0.239868224 | 0.517074783 | 0.501000000 | submission_h008_full_logit_blend_w0p025_1abf6cae.csv |
| full_logit_blend_w0p04 | full_blend | 250 | 5.749775102 | 0.019995555 | -0.239868224 | 0.517074783 | 0.501000000 | submission_h008_full_logit_blend_w0p04_704ab61d.csv |
| full_logit_blend_w0p065 | full_blend | 250 | 8.790130345 | 0.019995555 | -0.239868224 | 0.517074783 | 0.501000000 | submission_h008_full_logit_blend_w0p065_62ea8f37.csv |
| full_logit_blend_w0p09 | full_blend | 250 | 11.003809584 | 0.019995555 | -0.239868224 | 0.517074783 | 0.501000000 | submission_h008_full_logit_blend_w0p09_094917ab.csv |
| pos_consensus_top40_w0p06_cap0p02 | pos_consensus | 35 | 0.584849606 | 0.004992809 | 0.536101191 | 0.841962733 | 0.696257143 | submission_h008_pos_consensus_top40_w0p06_cap0p02_3b6dcb31.csv |
| pos_consensus_top60_w0p06_cap0p02 | pos_consensus | 47 | 0.776609541 | 0.004996517 | 0.516290466 | 0.802405180 | 0.688531915 | submission_h008_pos_consensus_top60_w0p06_cap0p02_f5b53b78.csv |
| pos_consensus_top80_w0p05_cap0p018 | pos_consensus | 57 | 0.818167623 | 0.004496989 | 0.498951550 | 0.778474447 | 0.667701754 | submission_h008_pos_consensus_top80_w0p05_cap0p018_68342464.csv |
| pos_consensus_top120_w0p04_cap0p015 | pos_consensus | 75 | 0.883435111 | 0.003748884 | 0.493780705 | 0.725739130 | 0.610946667 | submission_h008_pos_consensus_top120_w0p04_cap0p015_d217451c.csv |
| lowenergy_signed_top60_w0p07_cap0p02 | lowenergy_signed | 60 | 1.065027241 | 0.004999459 | -0.126516394 | 0.834333333 | 0.835866667 | submission_h008_lowenergy_signed_top60_w0p07_cap0p02_392260e9.csv |
| lowenergy_signed_top90_w0p06_cap0p018 | lowenergy_signed | 90 | 1.466740925 | 0.004499564 | -0.323701667 | 0.680676329 | 0.707000000 | submission_h008_lowenergy_signed_top90_w0p06_cap0p018_c9d070a4.csv |
| lowenergy_signed_top120_w0p05_cap0p016 | lowenergy_signed | 120 | 1.739730828 | 0.003999976 | -0.362989472 | 0.603615942 | 0.647133333 | submission_h008_lowenergy_signed_top120_w0p05_cap0p016_cc51269e.csv |
| two_tail_top40_w0p08_cap0p022 | two_tail | 40 | 0.818552070 | 0.005499916 | -0.373917567 | 0.454760870 | 0.442300000 | submission_h008_two_tail_top40_w0p08_cap0p022_4adeaffd.csv |
| two_tail_top60_w0p07_cap0p02 | two_tail | 56 | 1.018503317 | 0.004999942 | -0.332311064 | 0.441009317 | 0.429142857 | submission_h008_two_tail_top60_w0p07_cap0p02_2a35fb28.csv |
| two_tail_refine_top30_w0p075_cap0p02 | two_tail | 30 | 0.553087009 | 0.004999942 | -0.451131406 | 0.455507246 | 0.470466667 | submission_h008_two_tail_refine_top30_w0p075_cap0p02_a47ca1a1.csv |
| two_tail_refine_top40_w0p07_cap0p02 | two_tail | 40 | 0.739483061 | 0.004999942 | -0.373917567 | 0.454760870 | 0.442300000 | submission_h008_two_tail_refine_top40_w0p07_cap0p02_cf14d4ad.csv |
| two_tail_refine_top40_w0p078_cap0p02 | two_tail | 40 | 0.752307060 | 0.004999942 | -0.373917567 | 0.454760870 | 0.442300000 | submission_h008_two_tail_refine_top40_w0p078_cap0p02_de3c9844.csv |
| two_tail_refine_top50_w0p07_cap0p02 | two_tail | 49 | 0.882133291 | 0.004999942 | -0.328082248 | 0.446690328 | 0.432224490 | submission_h008_two_tail_refine_top50_w0p07_cap0p02_244cc9c6.csv |
| two_tail_refine_top60_w0p06_cap0p018 | two_tail | 56 | 0.909859986 | 0.004499962 | -0.332311064 | 0.441009317 | 0.429142857 | submission_h008_two_tail_refine_top60_w0p06_cap0p018_e7267013.csv |
| delta_two_tail_top40_w0p06_cap0p018 | delta_two_tail | 40 | 0.710103306 | 0.004499804 | -0.384210983 | 0.643434783 | 0.666500000 | submission_h008_delta_two_tail_top40_w0p06_cap0p018_8b8f36d8.csv |
| delta_two_tail_top60_w0p055_cap0p018 | delta_two_tail | 60 | 1.055914594 | 0.004499804 | -0.344042108 | 0.621405797 | 0.637000000 | submission_h008_delta_two_tail_top60_w0p055_cap0p018_8c3be15b.csv |
| delta_two_tail_top80_w0p045_cap0p015 | delta_two_tail | 80 | 1.176382305 | 0.003749981 | -0.325085272 | 0.589847826 | 0.590450000 | submission_h008_delta_two_tail_top80_w0p045_cap0p015_547cbcc2.csv |
| down_control_highmob_top60_w0p06_cap0p02 | down_control | 47 | 0.776609541 | 0.004998639 | 0.516290466 | 0.802405180 | 0.688531915 | submission_h008_down_control_highmob_top60_w0p06_cap0p02_c0efea43.csv |

## Selector Scores

| basename | promotion_decision | pred_delta_vs_current_mean | pred_delta_vs_current_p10 | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h008_delta_two_tail_top60_w0p055_cap0p018_8c3be15b.csv | too_small_to_submit | -0.000024789 | -0.000047595 | -0.000001341 | 0.916666667 | 0.000645407 |
| submission_h008_delta_two_tail_top40_w0p06_cap0p018_8b8f36d8.csv | too_small_to_submit | -0.000014591 | -0.000025474 | -0.000000865 | 0.902777778 | 0.000268902 |
| submission_h008_delta_two_tail_top80_w0p045_cap0p015_547cbcc2.csv | too_small_to_submit | -0.000024241 | -0.000050404 | 0.000000489 | 0.888888889 | 0.000267230 |
| submission_h008_two_tail_refine_top40_w0p078_cap0p02_de3c9844.csv | too_small_to_submit | -0.000014006 | -0.000041654 | 0.000003470 | 0.819444444 | -0.000115509 |
| submission_h008_two_tail_top40_w0p08_cap0p022_4adeaffd.csv | too_small_to_submit | -0.000014952 | -0.000045091 | 0.000004666 | 0.819444444 | -0.000145704 |
| submission_h008_two_tail_refine_top40_w0p07_cap0p02_cf14d4ad.csv | too_small_to_submit | -0.000013403 | -0.000039960 | 0.000004798 | 0.819444444 | -0.000143537 |
| submission_h008_two_tail_refine_top60_w0p06_cap0p018_e7267013.csv | too_small_to_submit | -0.000011716 | -0.000023181 | 0.000008552 | 0.861111111 | -0.000116131 |
| submission_h008_two_tail_refine_top30_w0p075_cap0p02_a47ca1a1.csv | too_small_to_submit | -0.000009208 | -0.000021493 | 0.000008858 | 0.833333333 | -0.000118996 |
| submission_h008_two_tail_top60_w0p07_cap0p02_2a35fb28.csv | too_small_to_submit | -0.000013224 | -0.000027321 | 0.000008971 | 0.847222222 | -0.000118467 |
| submission_h008_two_tail_refine_top50_w0p07_cap0p02_244cc9c6.csv | too_small_to_submit | -0.000013409 | -0.000032936 | 0.000011967 | 0.861111111 | -0.000133541 |
| submission_h008_pos_consensus_top40_w0p06_cap0p02_3b6dcb31.csv | too_small_to_submit | -0.000031995 | -0.000109787 | 0.000011978 | 0.847222222 | 0.000834765 |
| submission_h008_lowenergy_signed_top60_w0p07_cap0p02_392260e9.csv | too_small_to_submit | -0.000011860 | -0.000028425 | 0.000013948 | 0.819444444 | -0.000130613 |
| submission_h008_pos_consensus_top80_w0p05_cap0p018_68342464.csv | too_small_to_submit | -0.000044516 | -0.000155662 | 0.000016478 | 0.847222222 | 0.001142098 |
| submission_h008_pos_consensus_top60_w0p06_cap0p02_f5b53b78.csv | too_small_to_submit | -0.000044027 | -0.000153025 | 0.000016519 | 0.861111111 | 0.001156036 |
| submission_h008_pos_consensus_top120_w0p04_cap0p015_d217451c.csv | too_small_to_submit | -0.000045978 | -0.000179833 | 0.000019136 | 0.861111111 | 0.001102730 |
| submission_h008_lowenergy_signed_top90_w0p06_cap0p018_c9d070a4.csv | too_small_to_submit | -0.000013740 | -0.000028157 | 0.000019715 | 0.833333333 | -0.000240114 |
| submission_h008_lowenergy_signed_top120_w0p05_cap0p016_cc51269e.csv | too_small_to_submit | -0.000003760 | -0.000036152 | 0.000054090 | 0.722222222 | -0.000981130 |
| submission_h008_full_logit_blend_w0p015_0dcd5e48.csv | too_small_to_submit | -0.000000453 | -0.000059406 | 0.000088501 | 0.694444444 | -0.001627249 |
| submission_h008_full_logit_blend_w0p025_1abf6cae.csv | too_small_to_submit | -0.000001625 | -0.000099880 | 0.000138662 | 0.680555556 | -0.002712081 |
| submission_h008_full_logit_blend_w0p04_704ab61d.csv | too_small_to_submit | -0.000004639 | -0.000158998 | 0.000182032 | 0.652777778 | -0.004279857 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | below_selector_resolution | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_h008_down_control_highmob_top60_w0p06_cap0p02_c0efea43.csv | below_selector_resolution | 0.000037654 | -0.000021084 | 0.000138754 | 0.194444444 | -0.001156036 |
| submission_h008_full_logit_blend_w0p065_62ea8f37.csv | below_selector_resolution | 0.000003451 | -0.000230881 | 0.000230587 | 0.333333333 | -0.006449755 |
| submission_h008_full_logit_blend_w0p09_094917ab.csv | below_selector_resolution | 0.000005668 | -0.000306808 | 0.000335486 | 0.347222222 | -0.007879083 |

## Movement Anatomy

| basename | changed_cells_vs_current | l1_logit_delta_vs_current | max_abs_prob_delta_vs_current | cos_delta_with_h003_tiny | l1_ratio_to_h003_tiny |
| --- | --- | --- | --- | --- | --- |
| submission_h008_two_tail_refine_top30_w0p075_cap0p02_a47ca1a1.csv | 30 | 0.553087009 | 0.004999942 | 0.113299426 | 0.040844638 |
| submission_h008_pos_consensus_top40_w0p06_cap0p02_3b6dcb31.csv | 35 | 0.584849606 | 0.004992809 | 0.077745316 | 0.043190257 |
| submission_h008_delta_two_tail_top40_w0p06_cap0p018_8b8f36d8.csv | 40 | 0.710103306 | 0.004499804 | 0.165225325 | 0.052440053 |
| submission_h008_two_tail_refine_top40_w0p07_cap0p02_cf14d4ad.csv | 40 | 0.739483061 | 0.004999942 | 0.138952845 | 0.054609704 |
| submission_h008_two_tail_refine_top40_w0p078_cap0p02_de3c9844.csv | 40 | 0.752307060 | 0.004999942 | 0.138658716 | 0.055556737 |
| submission_h008_pos_consensus_top60_w0p06_cap0p02_f5b53b78.csv | 47 | 0.776609541 | 0.004996517 | 0.097523594 | 0.057351438 |
| submission_h008_down_control_highmob_top60_w0p06_cap0p02_c0efea43.csv | 47 | 0.776609541 | 0.004998639 | -0.097523594 | 0.057351438 |
| submission_h008_pos_consensus_top80_w0p05_cap0p018_68342464.csv | 57 | 0.818167623 | 0.004496989 | 0.100482670 | 0.060420439 |
| submission_h008_two_tail_top40_w0p08_cap0p022_4adeaffd.csv | 40 | 0.818552070 | 0.005499916 | 0.138834597 | 0.060448830 |
| submission_h008_two_tail_refine_top50_w0p07_cap0p02_244cc9c6.csv | 49 | 0.882133291 | 0.004999942 | 0.133372499 | 0.065144207 |
| submission_h008_pos_consensus_top120_w0p04_cap0p015_d217451c.csv | 75 | 0.883435111 | 0.003748884 | 0.100020068 | 0.065240344 |
| submission_h008_two_tail_refine_top60_w0p06_cap0p018_e7267013.csv | 56 | 0.909859986 | 0.004499962 | 0.129712173 | 0.067191781 |
| submission_h008_two_tail_top60_w0p07_cap0p02_2a35fb28.csv | 56 | 1.018503317 | 0.004999942 | 0.129497752 | 0.075214927 |
| submission_h008_delta_two_tail_top60_w0p055_cap0p018_8c3be15b.csv | 60 | 1.055914594 | 0.004499804 | 0.178601553 | 0.077977693 |
| submission_h008_lowenergy_signed_top60_w0p07_cap0p02_392260e9.csv | 60 | 1.065027241 | 0.004999459 | 0.153499398 | 0.078650648 |
| submission_h008_delta_two_tail_top80_w0p045_cap0p015_547cbcc2.csv | 80 | 1.176382305 | 0.003749981 | 0.203511476 | 0.086874051 |
| submission_h008_lowenergy_signed_top90_w0p06_cap0p018_c9d070a4.csv | 90 | 1.466740925 | 0.004499564 | 0.194527990 | 0.108316595 |
| submission_h008_lowenergy_signed_top120_w0p05_cap0p016_cc51269e.csv | 120 | 1.739730828 | 0.003999976 | 0.220307559 | 0.128476486 |
| submission_h008_full_logit_blend_w0p015_0dcd5e48.csv | 250 | 2.173443351 | 0.007877345 | 0.257688013 | 0.160505498 |
| submission_h008_full_logit_blend_w0p025_1abf6cae.csv | 250 | 3.622405585 | 0.013128434 | 0.257688013 | 0.267509164 |
| submission_h008_full_logit_blend_w0p04_704ab61d.csv | 250 | 5.749775102 | 0.019995555 | 0.259659344 | 0.424612180 |
| submission_h008_full_logit_blend_w0p065_62ea8f37.csv | 250 | 8.790130345 | 0.019995555 | 0.266481581 | 0.649137808 |
| submission_h008_full_logit_blend_w0p09_094917ab.csv | 250 | 11.003809584 | 0.019995555 | 0.266366471 | 0.812614666 |

## Selection

_empty_

## Interpretation

No strict candidate, but `9` HITL-aggressive candidate(s) survived the soft shape gate. Best: `submission_h008_delta_two_tail_top60_w0p055_cap0p018_8c3be15b.csv`.

## Files

- `hitl/h008_s4_latent_column_translator/h008_s4_model_test_predictions.csv`
- `hitl/h008_s4_latent_column_translator/h008_candidates.csv`
- `hitl/h008_s4_latent_column_translator/h008_selector_scores.csv`
- `hitl/h008_s4_latent_column_translator/h008_candidate_anatomy.csv`
- `hitl/h008_s4_latent_column_translator/h008_gate_scores.csv`
- `hitl/h008_s4_latent_column_translator/h008_selection.csv`
