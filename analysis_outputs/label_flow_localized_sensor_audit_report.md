# Label-Flow Localized Sensor Audit

Question: after scale failed to reconcile selectors, can row/subject/date/block localization make the S4/Q3 direction selector-consistent?

## Summary

- candidates scored: `960`.
- pair p90 negative: `807`.
- old majority: `0`.
- two-selector majority: `0`.
- localized sensor candidates: `8`.
- best rank file: `analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id07_s1p00_e1c5f36d.csv`, pair p90 `-0.000073768`, old p90 `0.000660069`, old rate `0.278`.
- lowest-old-risk pairwise-negative file: `analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_subject_phase_early_s0p65_9f872159.csv`, pair p90 `-0.000020181`, old p90 `0.000554202`, old rate `0.278`.

## By Row Mask Kind

| row_mask_kind | n | pair_p90_negative | pair_majority | old_majority | two_selector_majority | localized_sensor_candidate | best_file | best_pair_p90 | best_pair_rate | best_old_p90 | best_old_rate | best_bad_axis | best_movement | best_row_frac |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| date_block | 312 | 167 | 232 | 0 | 0 | 8 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_block_id02_b00_s1p00_c6a978ce.csv | -1.96694e-05 | 0.975676 | 0.000568333 | 0.277992 | 0.033321 | 0.00122891 | 0.064 |
| subject_complement | 80 | 80 | 80 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id07_s1p00_e1c5f36d.csv | -7.37685e-05 | 0.97027 | 0.000660069 | 0.277992 | 0.0162256 | 0.00622994 | 0.88 |
| date_block_complement | 312 | 312 | 312 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id07_b00_s1p00_ec45a2d0.csv | -7.12954e-05 | 0.967568 | 0.000666759 | 0.277992 | 0.0161267 | 0.00656375 | 0.94 |
| delta_energy | 24 | 16 | 16 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_delta_energy_top_20_s1p00_6ac43f67.csv | -6.13973e-05 | 0.967568 | 0.000670046 | 0.277992 | 0.0191924 | 0.00645602 | 0.2 |
| delta_sign | 16 | 16 | 16 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_s4_delta_negative_s1p00_460a4f85.csv | -5.1984e-05 | 0.97027 | 0.00063117 | 0.277992 | 0.0267482 | 0.00367559 | 0.144 |
| subject_energy | 16 | 16 | 16 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_subject_energy_high_half_s1p00_0829ab1b.csv | -4.5322e-05 | 0.972973 | 0.000604867 | 0.277992 | 0.0211975 | 0.00413107 | 0.496 |
| subject_phase | 40 | 40 | 40 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_subject_phase_first_half_s1p00_f8b55f2f.csv | -4.45946e-05 | 0.967568 | 0.000619804 | 0.277992 | 0.0317351 | 0.00390542 | 0.488 |
| global_tertile | 24 | 24 | 24 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_global_tertile_1_s1p00_ff808add.csv | -3.62036e-05 | 0.97027 | 0.000601278 | 0.277992 | 0.0293768 | 0.00307305 | 0.332 |
| calendar | 16 | 16 | 16 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_weekday_s1p00_abec76d8.csv | -3.54479e-05 | 0.967568 | 0.000603893 | 0.277992 | 0.0239971 | 0.00439164 | 0.728 |
| global_quintile | 40 | 40 | 40 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_global_quintile_2_s1p00_14efdc6d.csv | -2.44526e-05 | 0.972973 | 0.000564597 | 0.277992 | 0.0324419 | 0.00216394 | 0.2 |
| subject | 80 | 80 | 80 | 0 | 0 | 0 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_subject_id02_s1p00_adea3aeb.csv | -1.98841e-05 | 0.975676 | 0.000568284 | 0.277992 | 0.0332957 | 0.00124164 | 0.128 |

## By Sensor/Mask

| sensor_tag | target_mask_name | scale | n | pair_p90_negative | pair_majority | old_majority | two_selector_majority | localized_sensor_candidate | best_file | best_pair_p90 | best_pair_rate | best_old_p90 | best_old_rate | best_bad_axis | best_movement | best_row_frac |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| contrast_6b | q3_s4 | 1 | 120 | 101 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id07_s1p00_e1c5f36d.csv | -7.37685e-05 | 0.97027 | 0.000660069 | 0.277992 | 0.0162256 | 0.00622994 | 0.88 |
| contrast_6b | s4 | 1 | 120 | 100 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_not_subject_id07_s1p00_c5af6639.csv | -6.68058e-05 | 0.967568 | 0.000655642 | 0.277992 | 0.0273397 | 0.0055388 | 0.88 |
| conservative_1bb | q3_s4 | 1 | 120 | 101 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_subject_id07_s1p00_a4dd49e0.csv | -6.14483e-05 | 0.97027 | 0.000633513 | 0.277992 | 0.0200974 | 0.0051911 | 0.88 |
| conservative_1bb | s4 | 1 | 120 | 101 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_conservative_1bb_s4_not_subject_id07_s1p00_107752a3.csv | -5.59447e-05 | 0.967568 | 0.000634477 | 0.277992 | 0.028876 | 0.00463646 | 0.88 |
| contrast_6b | q3_s4 | 0.65 | 120 | 101 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id07_s0p65_97ace059.csv | -4.80182e-05 | 0.97027 | 0.000593761 | 0.277992 | 0.0234636 | 0.00404946 | 0.88 |
| contrast_6b | s4 | 0.65 | 120 | 101 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_not_subject_id07_s0p65_28f1a806.csv | -4.34336e-05 | 0.964865 | 0.000591627 | 0.277992 | 0.0306878 | 0.00360022 | 0.88 |
| conservative_1bb | q3_s4 | 0.65 | 120 | 101 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_subject_id07_s0p65_5424e649.csv | -3.99231e-05 | 0.97027 | 0.000563685 | 0.277992 | 0.0259803 | 0.00337422 | 0.88 |
| conservative_1bb | s4 | 0.65 | 120 | 101 | 109 | 0 | 0 | 1 | analysis_outputs/submission_label_flow_locsensor_conservative_1bb_s4_not_subject_id07_s0p65_48bfab1a.csv | -3.63605e-05 | 0.964865 | 0.000563068 | 0.277992 | 0.0316864 | 0.0030137 | 0.88 |

## Shortlist

| source_path | sensor_tag | target_mask_name | row_mask_kind | row_mask_name | scale | row_mask_frac | pair_delta_vs_a2c8_p90 | pair_beats_a2c8_rate | selector_p90_delta_vs_a2c8_public | beats_a2c8_scenario_rate | bad_axis_abs_load | movement_scale | two_selector_majority | localized_sensor_candidate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_block_id02_b02_s1p00_ea4fdc0b.csv | contrast_6b | q3_s4 | date_block | block_id02_b02 | 1 | 0.032 | -2.03151e-07 | 0.964865 | 0.000580036 | 0.413127 | 0.0368521 | 1.27234e-05 | False | True |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_block_id02_b02_s1p00_96c21f59.csv | contrast_6b | s4 | date_block | block_id02_b02 | 1 | 0.032 | -2.03151e-07 | 0.964865 | 0.000580036 | 0.413127 | 0.0368521 | 1.27234e-05 | False | True |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_block_id02_b02_s1p00_0900a1a4.csv | conservative_1bb | q3_s4 | date_block | block_id02_b02 | 1 | 0.032 | -1.69178e-07 | 0.964865 | 0.00058002 | 0.413127 | 0.036861 | 1.06104e-05 | False | True |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_s4_block_id02_b02_s1p00_a778791a.csv | conservative_1bb | s4 | date_block | block_id02_b02 | 1 | 0.032 | -1.69178e-07 | 0.964865 | 0.00058002 | 0.413127 | 0.036861 | 1.06104e-05 | False | True |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_block_id02_b02_s0p65_44a9a4aa.csv | contrast_6b | q3_s4 | date_block | block_id02_b02 | 0.65 | 0.032 | -1.31567e-07 | 0.964865 | 0.000580001 | 0.413127 | 0.0368709 | 8.27019e-06 | False | True |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_block_id02_b02_s0p65_8dbb9686.csv | contrast_6b | s4 | date_block | block_id02_b02 | 0.65 | 0.032 | -1.31567e-07 | 0.964865 | 0.000580001 | 0.413127 | 0.0368709 | 8.27019e-06 | False | True |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_block_id02_b02_s0p65_f709bfc3.csv | conservative_1bb | q3_s4 | date_block | block_id02_b02 | 0.65 | 0.032 | -1.09503e-07 | 0.964865 | 0.00057999 | 0.413127 | 0.0368767 | 6.89674e-06 | False | True |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_s4_block_id02_b02_s0p65_19409b4d.csv | conservative_1bb | s4 | date_block | block_id02_b02 | 0.65 | 0.032 | -1.09503e-07 | 0.964865 | 0.00057999 | 0.413127 | 0.0368767 | 6.89674e-06 | False | True |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id07_s1p00_e1c5f36d.csv | contrast_6b | q3_s4 | subject_complement | not_subject_id07 | 1 | 0.88 | -7.37685e-05 | 0.97027 | 0.000660069 | 0.277992 | 0.0162256 | 0.00622994 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id05_s1p00_23a548ed.csv | contrast_6b | q3_s4 | subject_complement | not_subject_id05 | 1 | 0.916 | -7.18266e-05 | 0.967568 | 0.000665789 | 0.277992 | 0.0160604 | 0.00657436 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id07_b00_s1p00_ec45a2d0.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id07_b00 | 1 | 0.94 | -7.12954e-05 | 0.967568 | 0.000666759 | 0.277992 | 0.0161267 | 0.00656375 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id05_b07_s1p00_88ed7366.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id05_b07 | 1 | 0.98 | -7.16592e-05 | 0.967568 | 0.000672139 | 0.277992 | 0.0173459 | 0.00690699 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id01_s1p00_9eeacf05.csv | contrast_6b | q3_s4 | subject_complement | not_subject_id01 | 1 | 0.892 | -7.09831e-05 | 0.967568 | 0.000671942 | 0.277992 | 0.0166418 | 0.00681038 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id04_s1p00_1a75e50d.csv | contrast_6b | q3_s4 | subject_complement | not_subject_id04 | 1 | 0.892 | -7.11468e-05 | 0.967568 | 0.000673477 | 0.277992 | 0.0173746 | 0.00697976 | False | False |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_subject_id07_s1p00_a4dd49e0.csv | conservative_1bb | q3_s4 | subject_complement | not_subject_id07 | 1 | 0.88 | -6.14483e-05 | 0.97027 | 0.000633513 | 0.277992 | 0.0200974 | 0.0051911 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id03_s1p00_81e5d1a6.csv | contrast_6b | q3_s4 | subject_complement | not_subject_id03 | 1 | 0.916 | -6.92308e-05 | 0.967568 | 0.000669371 | 0.277992 | 0.0183061 | 0.00673607 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_not_subject_id07_s1p00_c5af6639.csv | contrast_6b | s4 | subject_complement | not_subject_id07 | 1 | 0.88 | -6.68058e-05 | 0.967568 | 0.000655642 | 0.277992 | 0.0273397 | 0.0055388 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_not_subject_id05_s1p00_070b9d44.csv | contrast_6b | s4 | subject_complement | not_subject_id05 | 1 | 0.916 | -6.83951e-05 | 0.964865 | 0.0006606 | 0.277992 | 0.0288002 | 0.00574843 | False | False |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_block_id07_b00_s1p00_ae0279b0.csv | conservative_1bb | q3_s4 | date_block_complement | not_block_id07_b00 | 1 | 0.94 | -6.0176e-05 | 0.967568 | 0.000638481 | 0.277992 | 0.0192477 | 0.00546852 | False | False |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_subject_id05_s1p00_1feeefb7.csv | conservative_1bb | q3_s4 | subject_complement | not_subject_id05 | 1 | 0.916 | -5.99741e-05 | 0.967568 | 0.000638637 | 0.277992 | 0.0196777 | 0.00549749 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_not_block_id07_b00_s1p00_f2d58680.csv | contrast_6b | s4 | date_block_complement | not_block_id07_b00 | 1 | 0.94 | -6.69509e-05 | 0.967568 | 0.000661589 | 0.277992 | 0.0261388 | 0.00587261 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id01_b03_s1p00_14594db4.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id01_b03 | 1 | 0.984 | -6.66234e-05 | 0.967568 | 0.000674177 | 0.277992 | 0.016348 | 0.00706879 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_subject_id07_s0p65_97ace059.csv | contrast_6b | q3_s4 | subject_complement | not_subject_id07 | 0.65 | 0.88 | -4.80182e-05 | 0.97027 | 0.000593761 | 0.277992 | 0.0234636 | 0.00404946 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id04_b06_s1p00_c3e9ba2f.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id04_b06 | 1 | 0.988 | -6.64275e-05 | 0.967568 | 0.000674138 | 0.277992 | 0.017138 | 0.00707155 | False | False |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_block_id05_b07_s1p00_0c20b3aa.csv | conservative_1bb | q3_s4 | date_block_complement | not_block_id05_b07 | 1 | 0.98 | -5.97505e-05 | 0.967568 | 0.000644936 | 0.277992 | 0.0207502 | 0.00577502 | False | False |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_subject_id07_s0p65_5424e649.csv | conservative_1bb | q3_s4 | subject_complement | not_subject_id07 | 0.65 | 0.88 | -3.99231e-05 | 0.97027 | 0.000563685 | 0.277992 | 0.0259803 | 0.00337422 | False | False |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_subject_id01_s1p00_596e9b76.csv | conservative_1bb | q3_s4 | subject_complement | not_subject_id01 | 1 | 0.892 | -5.91931e-05 | 0.967568 | 0.000646039 | 0.277992 | 0.0201634 | 0.0056955 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id07_b04_s1p00_172bf526.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id07_b04 | 1 | 0.976 | -6.54888e-05 | 0.967568 | 0.000674307 | 0.277992 | 0.0178872 | 0.00707823 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_not_block_id05_b07_s1p00_6aa18401.csv | contrast_6b | s4 | date_block_complement | not_block_id05_b07 | 1 | 0.98 | -6.69539e-05 | 0.962162 | 0.000666251 | 0.277992 | 0.0300858 | 0.00608106 | False | False |
| analysis_outputs/submission_label_flow_locsensor_conservative_1bb_q3_s4_not_subject_id04_s1p00_6b778471.csv | conservative_1bb | q3_s4 | subject_complement | not_subject_id04 | 1 | 0.892 | -5.92666e-05 | 0.967568 | 0.000646824 | 0.277992 | 0.0207739 | 0.00583615 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_s4_not_subject_id01_s1p00_4c6d033a.csv | contrast_6b | s4 | subject_complement | not_subject_id01 | 1 | 0.892 | -6.62766e-05 | 0.964865 | 0.000666103 | 0.277992 | 0.0293817 | 0.00598445 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id03_b00_s1p00_a1e7c7b8.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id03_b00 | 1 | 0.98 | -6.52263e-05 | 0.967568 | 0.00067549 | 0.277992 | 0.0172133 | 0.0072301 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id04_b01_s1p00_07da8fed.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id04_b01 | 1 | 0.98 | -6.52278e-05 | 0.967568 | 0.000675507 | 0.277992 | 0.017247 | 0.00723233 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id04_b04_s1p00_992a3638.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id04_b04 | 1 | 0.976 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id01_b00_s1p00_464cac08.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id01_b00 | 1 | 0.98 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id02_b03_s1p00_a0dd0a60.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id02_b03 | 1 | 0.98 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id06_b01_s1p00_ce1b92bd.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id06_b01 | 1 | 0.984 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id07_b01_s1p00_a63d86d3.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id07_b01 | 1 | 0.984 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id02_b01_s1p00_9200be0c.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id02_b01 | 1 | 0.988 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | False | False |
| analysis_outputs/submission_label_flow_locsensor_contrast_6b_q3_s4_not_block_id03_b01_s1p00_9347922e.csv | contrast_6b | q3_s4 | date_block_complement | not_block_id03_b01 | 1 | 0.988 | -6.52173e-05 | 0.967568 | 0.000675515 | 0.277992 | 0.0172468 | 0.0072335 | False | False |

## Decision

- No subject/date/block/energy/sign localization created two-selector majority.
- This weakens the localization-fix hypothesis: the S4/Q3 pairwise direction remains old-selector-negative even when restricted to simple hidden-DGP row subsets.
- If a public sensor is used, choose it for selector calibration information, not because localization made it submit-safe.

## Files

- `label_flow_localized_sensor_audit.csv`
- `label_flow_localized_sensor_audit_by_zone.csv`
- `label_flow_localized_sensor_audit_by_mask.csv`
- `label_flow_localized_sensor_audit_shortlist.csv`
