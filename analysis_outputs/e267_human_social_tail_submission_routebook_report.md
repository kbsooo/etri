# E267 Human/Social Tail Submission Routebook

## Question

E266 produced 22 lifestyle-conditioned Q3/S4 materializations. Which one should be used as a public sensor if only one file is submitted?

## Decision

Recommended next social/JEPA file:

`submission_e267_humansocial_tail_balanced_2936100f.csv`

Source file:

`submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50_2936100f.csv`

This is the balanced `2936100f` prediction: `25` Q3 cells and `25` S4 cells are rolled back toward E154 using the E264/E266 human-core late-lifelog cell-tail representation.

## Why This One

- It keeps expected loss versus E224 non-positive: `-0.000004014`.
- It reduces adverse capacity versus E224: `0.000418519`.
- It improves support mass versus E224: `0.004541355`.
- It also survives actual-vs-E95 stress: expected `-0.000004014`, adverse reduction `0.000383531`, support gain `0.003984398`.
- It is not the broadest support sensor. The broader `c1e018aa` file has higher E237 score but positive expected loss and 75 dropped cells, which is too close to the E265 broad-gate failure mode.
- It is more informative than the sharp `95bf3a1c` file because it keeps much more support/adverse movement while still avoiding positive expected loss.

## Top Canonical Candidates

| route_label | candidate_id | submission_file | social_jepa_survival_score | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | actual_support_gain_vs_e224 | q3_top1_over_abs_expected | e230_q3_risk_top21_overlap | total_dropped_cells | duplicate_prediction_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submit_1_balanced | all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50_2936100f.csv | 8.230181390 | -0.000004014 | 0.000418519 | 0.004541355 | -0.000004014 | 0.000383531 | 0.003984398 | 0.710932696 | 6 | 50 | 3 |
| candidate | q3s4_latent_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | submission_e237_cell_decisive_q3s4_latent_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10_b50a8e24.csv | 6.673020407 | -0.000014764 | 0.000313036 | 0.003097727 | -0.000014764 | 0.000277779 | 0.002809169 | 0.700935793 | 4 | 50 | 1 |
| candidate | q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top40 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top40_1d7abd47.csv | 6.235999525 | -0.000014050 | 0.000301369 | 0.002196155 | -0.000014050 | 0.000280833 | 0.001963363 | 0.722364523 | 4 | 40 | 2 |
| sharp_sensor | q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top13 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top13_95bf3a1c.csv | 6.175074471 | -0.000027985 | 0.000243126 | 0.002967857 | -0.000027985 | 0.000228973 | 0.002572892 | 0.709167264 | 4 | 26 | 3 |
| candidate | q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_each_top21 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_each_top21_584e3eff.csv | 6.089427525 | -0.000014261 | 0.000313653 | 0.001657371 | -0.000014261 | 0.000293117 | 0.001513830 | 0.721244734 | 4 | 42 | 2 |
| candidate | q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50_257bc500.csv | 5.632502549 | -0.000005832 | 0.000385869 | 0.000595664 | -0.000005832 | 0.000361918 | 0.000651182 | 0.805704634 | 4 | 50 | 2 |
| candidate | q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top21 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top21_ad4f7cd2.csv | 5.380228942 | -0.000008066 | 0.000287240 | 0.000728333 | -0.000008066 | 0.000258309 | 0.000799397 | 0.740763295 | 3 | 42 | 1 |
| candidate | q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top40 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top40_62bc4a86.csv | 5.269358602 | -0.000010374 | 0.000274335 | 0.000683220 | -0.000010374 | 0.000245405 | 0.000762239 | 0.727068131 | 3 | 40 | 1 |
| candidate | q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_q3_top25 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_q3_top25_5c252a83.csv | 5.237591466 | -0.000014639 | 0.000245987 | 0.002025351 | -0.000014639 | 0.000211759 | 0.001917226 | 0.774258541 | 4 | 25 | 1 |
| candidate | q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_global_top50 | submission_e237_cell_decisive_q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_global_top50_9b9f8d21.csv | 4.740986600 | -0.000019664 | 0.000306169 | 0.000395032 | -0.000019664 | 0.000264948 | 0.000607628 | 0.750118827 | 2 | 50 | 2 |
| support_sensor | all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75_c1e018aa.csv | 4.678327042 | 0.000010956 | 0.000509081 | 0.005063832 | 0.000010956 | 0.000457095 | 0.004505270 | 0.732938787 | 7 | 75 | 1 |
| candidate | q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top50 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top50_8e9d00d3.csv | 2.829415426 | 0.000011818 | 0.000348542 | 0.001454990 | 0.000011818 | 0.000314314 | 0.001436272 | 0.774258541 | 4 | 50 | 3 |

## Movement Against Known Anchors

| submission_file | reference | moved_cells_vs_ref | moved_rows_vs_ref | Q3_moved_vs_ref | S4_moved_vs_ref | mean_abs_logit_delta_vs_ref | max_abs_logit_delta_vs_ref |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e267_humansocial_tail_balanced_2936100f.csv | e247_public_best | 60 | 54 | 51 | 9 | 0.001928809 | 0.172092355 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | e256_same_family_loss | 51 | 45 | 42 | 9 | 0.001890319 | 0.172092355 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | e224_body | 34 | 25 | 25 | 9 | 0.000964290 | 0.172092355 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | e95_hardtail | 512 | 240 | 235 | 112 | 0.009297540 | 0.169294968 |

## Public LB Interpretation

- If this beats E247 `0.5761589494`, the strongest read is that human/social day state is a missing Q3/S4 tail law, not just a numeric feature-NN smoothing artifact.
- If it lands between E247 and E256 `0.5762805676`, the lifestyle state is real but weaker than E247's exact Q3 smoothing/body interaction.
- If it is near or worse than E95 `0.5762913298`, E266's materialization stress is likely overfitting the E224/E154 local geometry; next step should be a direct human/social overlay on E247 rather than another E224-family rollback.

## Hidden-World Bet

The bet is that some Q3/S4 tail errors correspond to human days: presleep cognitive load, social-message load, routine/commute rhythm, charging/screen/onset fragmentation, and sensor coverage jointly mark when the E224 body should be trusted or rolled back. This is JEPA-style because the model does not reconstruct raw app usage; it predicts the hidden target representation "which row-target cells are unsafe to keep" from partial human-day context.
