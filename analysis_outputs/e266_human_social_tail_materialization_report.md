# E266 Human/Social Tail Materialization Stress

## Question

Can the E264 human/social tail representation become a submission candidate after E265 blocked broad OOF gates?

Only sharper policies are tested. Broad `p15/p20` lifestyle rollbacks are excluded from the pool.

## Headline

- OOF pool rows: `80`.
- materialization rows: `160`.
- graft-side E237 gates: `22`.
- selected submissions: `22`.
- best expected_loss_vs_e224: `-0.000027985`.
- best adverse_reduction_vs_e224: `0.000589659`.
- best support_gain_vs_e224: `0.005063832`.

## Selected

| candidate_id | source_scope | view | model | split | target_kind | tail_q | policy | q3_dropped_cells | s4_dropped_cells | oof_loss_vs_full | oof_tail_auc | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | actual_support_gain_vs_e224 | q3_top1_over_abs_expected | q3_adverse_delta | e230_q3_risk_top21_overlap | e237_gate | e237_score | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top75 | 38 | 37 | -0.000453899 | 0.557152558 | 0.000010956 | 0.000509081 | 0.005063832 | 0.000010956 | 0.000457095 | 0.004505270 | 0.732938787 | 0.001855644 | 7 | True | 0.049779378 | submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75_c1e018aa.csv |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000408700 | 0.557152558 | -0.000004014 | 0.000418519 | 0.004541355 | -0.000004014 | 0.000383531 | 0.003984398 | 0.710932696 | 0.001905085 | 6 | True | 0.042777080 | submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50_2936100f.csv |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_p10 | 25 | 25 | -0.000508315 | 0.557152558 | -0.000004014 | 0.000418519 | 0.004541355 | -0.000004014 | 0.000383531 | 0.003984398 | 0.710932696 | 0.001905085 | 6 | True | 0.042777080 | submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10_2936100f.csv |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000408700 | 0.557152558 | -0.000004014 | 0.000418519 | 0.004541355 | -0.000004014 | 0.000383531 | 0.003984398 | 0.710932696 | 0.001905085 | 6 | True | 0.042777080 | submission_e237_cell_decisive_all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25_2936100f.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000519583 | 0.553870530 | -0.000005832 | 0.000385869 | 0.000595664 | -0.000005832 | 0.000361918 | 0.000651182 | 0.805704634 | 0.001964499 | 4 | True | 0.039450980 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50_257bc500.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000519583 | 0.553870530 | -0.000005832 | 0.000385869 | 0.000595664 | -0.000005832 | 0.000361918 | 0.000651182 | 0.805704634 | 0.001964499 | 4 | True | 0.039450980 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25_257bc500.csv |
| q3s4_latent_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | q3s4 | latent_human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_p10 | 23 | 27 | -0.000526683 | 0.578089633 | -0.000014764 | 0.000313036 | 0.003097727 | -0.000014764 | 0.000277779 | 0.002809169 | 0.700935793 | 0.001998156 | 4 | True | 0.033618429 | submission_e237_cell_decisive_q3s4_latent_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10_b50a8e24.csv |
| q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_each_top21 | q3s4 | human_late | lr_l2_c0p10 | subject5 | contrast | 0.100000000 | drop_each_top21 | 21 | 21 | -0.000353223 | 0.483878759 | -0.000014261 | 0.000313653 | 0.001657371 | -0.000014261 | 0.000293117 | 0.001513830 | 0.721244734 | 0.002000481 | 4 | True | 0.033494420 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_each_top21_584e3eff.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top21 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top21 | 21 | 21 | -0.000521701 | 0.553870530 | -0.000014261 | 0.000313653 | 0.001657371 | -0.000014261 | 0.000293117 | 0.001513830 | 0.721244734 | 0.002000481 | 4 | True | 0.033494420 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top21_584e3eff.csv |
| q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_global_top50 | q3s4 | human_late | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000782275 | 0.519019442 | -0.000019664 | 0.000306169 | 0.000395032 | -0.000019664 | 0.000264948 | 0.000607628 | 0.750118827 | 0.001963557 | 2 | True | 0.033401397 | submission_e237_cell_decisive_q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_global_top50_9b9f8d21.csv |
| q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_each_top25 | q3s4 | human_late | hgb_shallow | subject5 | contrast | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000782275 | 0.519019442 | -0.000019664 | 0.000306169 | 0.000395032 | -0.000019664 | 0.000264948 | 0.000607628 | 0.750118827 | 0.001963557 | 2 | True | 0.033401397 | submission_e237_cell_decisive_q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_each_top25_9b9f8d21.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_p10 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_global_p10 | 25 | 25 | -0.000518530 | 0.551977192 | 0.000011818 | 0.000348542 | 0.001454990 | 0.000011818 | 0.000314314 | 0.001436272 | 0.774258541 | 0.001969650 | 4 | True | 0.033316095 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_p10_8e9d00d3.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top25 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000517382 | 0.551977192 | 0.000011818 | 0.000348542 | 0.001454990 | 0.000011818 | 0.000314314 | 0.001436272 | 0.774258541 | 0.001969650 | 4 | True | 0.033316095 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top25_8e9d00d3.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top50 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000517382 | 0.551977192 | 0.000011818 | 0.000348542 | 0.001454990 | 0.000011818 | 0.000314314 | 0.001436272 | 0.774258541 | 0.001969650 | 4 | True | 0.033316095 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top50_8e9d00d3.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top40 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top40 | 20 | 20 | -0.000521463 | 0.553870530 | -0.000014050 | 0.000301369 | 0.002196155 | -0.000014050 | 0.000280833 | 0.001963363 | 0.722364523 | 0.002012765 | 4 | True | 0.032279551 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top40_1d7abd47.csv |
| q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_global_top40 | q3s4 | human_late | lr_l2_c0p10 | subject5 | contrast | 0.100000000 | drop_global_top40 | 20 | 20 | -0.000299493 | 0.483878759 | -0.000014050 | 0.000301369 | 0.002196155 | -0.000014050 | 0.000280833 | 0.001963363 | 0.722364523 | 0.002012765 | 4 | True | 0.032279551 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_global_top40_1d7abd47.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top21 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_each_top21 | 21 | 21 | -0.000517257 | 0.551977192 | -0.000008066 | 0.000287240 | 0.000728333 | -0.000008066 | 0.000258309 | 0.000799397 | 0.740763295 | 0.002003120 | 3 | True | 0.029911534 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top21_ad4f7cd2.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top40 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_global_top40 | 20 | 20 | -0.000545905 | 0.551977192 | -0.000010374 | 0.000274335 | 0.000683220 | -0.000010374 | 0.000245405 | 0.000762239 | 0.727068131 | 0.002009312 | 3 | True | 0.028940581 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top40_62bc4a86.csv |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top13 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top13 | 13 | 13 | -0.000437126 | 0.553870530 | -0.000027985 | 0.000243126 | 0.002967857 | -0.000027985 | 0.000228973 | 0.002572892 | 0.709167264 | 0.002038215 | 4 | True | 0.028467929 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top13_95bf3a1c.csv |
| q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_global_p05 | q3s4 | human_late | lr_l2_c0p10 | subject5 | contrast | 0.100000000 | drop_global_p05 | 13 | 12 | -0.000368376 | 0.483878759 | -0.000027985 | 0.000243126 | 0.002967857 | -0.000027985 | 0.000228973 | 0.002572892 | 0.709167264 | 0.002038215 | 4 | True | 0.028467929 | submission_e237_cell_decisive_q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_global_p05_95bf3a1c.csv |

## Best Materialized Graft Rows

| candidate_id | source_scope | view | model | split | target_kind | tail_q | policy | q3_dropped_cells | s4_dropped_cells | oof_loss_vs_full | oof_tail_auc | expected_loss_vs_e224 | adverse_reduction_vs_e224 | support_gain_vs_e224 | actual_expected_delta_vs_e224 | actual_adverse_reduction_vs_e224 | actual_support_gain_vs_e224 | q3_top1_over_abs_expected | q3_adverse_delta | e230_q3_risk_top21_overlap | e237_gate | e237_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top75 | 38 | 37 | -0.000453899 | 0.557152558 | 0.000010956 | 0.000509081 | 0.005063832 | 0.000010956 | 0.000457095 | 0.004505270 | 0.732938787 | 0.001855644 | 7 | True | 0.049779378 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top75 | 38 | 37 | -0.000690449 | 0.553870530 | 0.000030141 | 0.000541623 | -0.000586517 | 0.000030141 | 0.000506910 | -0.000244675 | 0.911273768 | 0.001878118 | 5 | False | 0.048449499 |
| q3s4_latent_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_top75 | q3s4 | latent_human_late | hgb_shallow | dateblock5 | contrast | 0.100000000 | drop_global_top75 | 35 | 40 | -0.000376862 | 0.578485740 | 0.000027149 | 0.000507761 | -0.000297265 | 0.000027149 | 0.000478958 | -0.000052604 | 0.784191885 | 0.001831534 | 3 | False | 0.046951444 |
| q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_global_top75 | q3s4 | human_late | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_top75 | 38 | 37 | -0.000474341 | 0.519019442 | 0.000029571 | 0.000466892 | 0.003458050 | 0.000029571 | 0.000410294 | 0.003227410 | 0.802013792 | 0.001854487 | 3 | False | 0.042825934 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000408700 | 0.557152558 | -0.000004014 | 0.000418519 | 0.004541355 | -0.000004014 | 0.000383531 | 0.003984398 | 0.710932696 | 0.001905085 | 6 | True | 0.042777080 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_p10 | 25 | 25 | -0.000508315 | 0.557152558 | -0.000004014 | 0.000418519 | 0.004541355 | -0.000004014 | 0.000383531 | 0.003984398 | 0.710932696 | 0.001905085 | 6 | True | 0.042777080 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | all3 | human_core | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000408700 | 0.557152558 | -0.000004014 | 0.000418519 | 0.004541355 | -0.000004014 | 0.000383531 | 0.003984398 | 0.710932696 | 0.001905085 | 6 | True | 0.042777080 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000519583 | 0.553870530 | -0.000005832 | 0.000385869 | 0.000595664 | -0.000005832 | 0.000361918 | 0.000651182 | 0.805704634 | 0.001964499 | 4 | True | 0.039450980 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000519583 | 0.553870530 | -0.000005832 | 0.000385869 | 0.000595664 | -0.000005832 | 0.000361918 | 0.000651182 | 0.805704634 | 0.001964499 | 4 | True | 0.039450980 |
| q3s4_latent_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | q3s4 | latent_human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_p10 | 23 | 27 | -0.000526683 | 0.578089633 | -0.000014764 | 0.000313036 | 0.003097727 | -0.000014764 | 0.000277779 | 0.002809169 | 0.700935793 | 0.001998156 | 4 | True | 0.033618429 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top21 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top21 | 21 | 21 | -0.000521701 | 0.553870530 | -0.000014261 | 0.000313653 | 0.001657371 | -0.000014261 | 0.000293117 | 0.001513830 | 0.721244734 | 0.002000481 | 4 | True | 0.033494420 |
| q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_each_top21 | q3s4 | human_late | lr_l2_c0p10 | subject5 | contrast | 0.100000000 | drop_each_top21 | 21 | 21 | -0.000353223 | 0.483878759 | -0.000014261 | 0.000313653 | 0.001657371 | -0.000014261 | 0.000293117 | 0.001513830 | 0.721244734 | 0.002000481 | 4 | True | 0.033494420 |
| q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_global_top50 | q3s4 | human_late | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000782275 | 0.519019442 | -0.000019664 | 0.000306169 | 0.000395032 | -0.000019664 | 0.000264948 | 0.000607628 | 0.750118827 | 0.001963557 | 2 | True | 0.033401397 |
| q3s4_human_late_hgb_shallow_subject5_contrast_q0p10_drop_each_top25 | q3s4 | human_late | hgb_shallow | subject5 | contrast | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000782275 | 0.519019442 | -0.000019664 | 0.000306169 | 0.000395032 | -0.000019664 | 0.000264948 | 0.000607628 | 0.750118827 | 0.001963557 | 2 | True | 0.033401397 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top50 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_global_top50 | 25 | 25 | -0.000517382 | 0.551977192 | 0.000011818 | 0.000348542 | 0.001454990 | 0.000011818 | 0.000314314 | 0.001436272 | 0.774258541 | 0.001969650 | 4 | True | 0.033316095 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top25 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_each_top25 | 25 | 25 | -0.000517382 | 0.551977192 | 0.000011818 | 0.000348542 | 0.001454990 | 0.000011818 | 0.000314314 | 0.001436272 | 0.774258541 | 0.001969650 | 4 | True | 0.033316095 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_p10 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_global_p10 | 25 | 25 | -0.000518530 | 0.551977192 | 0.000011818 | 0.000348542 | 0.001454990 | 0.000011818 | 0.000314314 | 0.001436272 | 0.774258541 | 0.001969650 | 4 | True | 0.033316095 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_q3_top40 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_q3_top40 | 40 | 0 | -0.000331825 | 0.553870530 | 0.000005710 | 0.000356090 | 0.001258227 | 0.000005710 | 0.000321378 | 0.001276673 | 0.921965691 | 0.001859547 | 5 | False | 0.033036536 |
| q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_global_top40 | q3s4 | human_late | lr_l2_c0p10 | subject5 | contrast | 0.100000000 | drop_global_top40 | 20 | 20 | -0.000299493 | 0.483878759 | -0.000014050 | 0.000301369 | 0.002196155 | -0.000014050 | 0.000280833 | 0.001963363 | 0.722364523 | 0.002012765 | 4 | True | 0.032279551 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top40 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_top40 | 20 | 20 | -0.000521463 | 0.553870530 | -0.000014050 | 0.000301369 | 0.002196155 | -0.000014050 | 0.000280833 | 0.001963363 | 0.722364523 | 0.002012765 | 4 | True | 0.032279551 |
| q3s4_latent_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p10 | q3s4 | latent_human_late | hgb_shallow | dateblock5 | contrast | 0.100000000 | drop_global_p10 | 25 | 25 | -0.000630667 | 0.578485740 | 0.000026453 | 0.000345823 | -0.000938339 | 0.000026453 | 0.000321219 | -0.000617198 | 0.895492903 | 0.001977686 | 2 | False | 0.029988919 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_each_top21 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_each_top21 | 21 | 21 | -0.000517257 | 0.551977192 | -0.000008066 | 0.000287240 | 0.000728333 | -0.000008066 | 0.000258309 | 0.000799397 | 0.740763295 | 0.002003120 | 3 | True | 0.029911534 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_global_top40 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_global_top40 | 20 | 20 | -0.000545905 | 0.551977192 | -0.000010374 | 0.000274335 | 0.000683220 | -0.000010374 | 0.000245405 | 0.000762239 | 0.727068131 | 0.002009312 | 3 | True | 0.028940581 |
| q3s4_human_late_lr_l2_c0p10_subject5_contrast_q0p10_drop_global_p05 | q3s4 | human_late | lr_l2_c0p10 | subject5 | contrast | 0.100000000 | drop_global_p05 | 13 | 12 | -0.000368376 | 0.483878759 | -0.000027985 | 0.000243126 | 0.002967857 | -0.000027985 | 0.000228973 | 0.002572892 | 0.709167264 | 0.002038215 | 4 | True | 0.028467929 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top13 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_each_top13 | 13 | 13 | -0.000437126 | 0.553870530 | -0.000027985 | 0.000243126 | 0.002967857 | -0.000027985 | 0.000228973 | 0.002572892 | 0.709167264 | 0.002038215 | 4 | True | 0.028467929 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p05 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | contrast | 0.100000000 | drop_global_p05 | 13 | 12 | -0.000613890 | 0.553870530 | -0.000027985 | 0.000243126 | 0.002967857 | -0.000027985 | 0.000228973 | 0.002572892 | 0.709167264 | 0.002038215 | 4 | True | 0.028467929 |
| q3s4_human_late_lr_l2_c0p10_dateblock5_risk_q0p10_drop_q3_top25 | q3s4 | human_late | lr_l2_c0p10 | dateblock5 | risk | 0.100000000 | drop_q3_top25 | 25 | 0 | -0.000352047 | 0.551977192 | -0.000014639 | 0.000245987 | 0.002025351 | -0.000014639 | 0.000211759 | 0.001917226 | 0.774258541 | 0.001969650 | 4 | True | 0.026810073 |
| all3_latent_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_q3_top40 | all3 | latent_human_late | hgb_shallow | dateblock5 | contrast | 0.100000000 | drop_q3_top40 | 40 | 0 | -0.000374461 | 0.661498416 | 0.000011834 | 0.000322114 | -0.004489722 | 0.000011834 | 0.000265409 | -0.003325714 | 0.978129173 | 0.001893523 | 1 | False | 0.026075079 |
| all3_latent_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_top75 | all3 | latent_human_late | hgb_shallow | dateblock5 | contrast | 0.100000000 | drop_global_top75 | 34 | 41 | -0.000797201 | 0.661498416 | 0.000026616 | 0.000340212 | -0.004429346 | 0.000026616 | 0.000297069 | -0.003374802 | 0.984116698 | 0.001957020 | 1 | False | 0.025580763 |
| all3_latent_human_late_hgb_shallow_subject5_contrast_q0p10_drop_global_top75 | all3 | latent_human_late | hgb_shallow | subject5 | contrast | 0.100000000 | drop_global_top75 | 34 | 41 | -0.000375785 | 0.583444028 | 0.000026616 | 0.000340212 | -0.004429346 | 0.000026616 | 0.000297069 | -0.003374802 | 0.984116698 | 0.001957020 | 1 | False | 0.025580763 |

## OOF Pool

| view | model | split | source_scope | target_kind | policy | tail_auc | loss_vs_full | q3_loss_vs_full | s4_loss_vs_full | subject_win_rate | dateblock_win_rate | dropped_cells | dropped_q3 | dropped_s4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_global_p10 | 0.582818294 | -0.000927595 | -0.000820028 | -0.001035162 | 0.900000000 | 0.671641791 | 90 | 45 | 45 |
| latent_human_late | hgb_shallow | dateblock5 | all3 | contrast | drop_global_top75 | 0.661498416 | -0.000797201 | -0.000735037 | -0.000859365 | 0.900000000 | 0.626865672 | 75 | 39 | 36 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_global_top50 | 0.519019442 | -0.000782275 | -0.000546492 | -0.001018057 | 0.800000000 | 0.626865672 | 50 | 25 | 25 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_each_top25 | 0.519019442 | -0.000782275 | -0.000546492 | -0.001018057 | 0.800000000 | 0.626865672 | 50 | 25 | 25 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_top75 | 0.553870530 | -0.000690449 | -0.000583834 | -0.000797065 | 0.700000000 | 0.641791045 | 75 | 38 | 37 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_s4_top50 | 0.582818294 | -0.000651173 | 0.000000000 | -0.001302346 | 0.700000000 | 0.626865672 | 50 | 0 | 50 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_q3_top50 | 0.582818294 | -0.000634511 | -0.001269023 | 0.000000000 | 0.700000000 | 0.641791045 | 50 | 50 | 0 |
| latent_human_late | hgb_shallow | dateblock5 | q3s4 | contrast | drop_global_p10 | 0.578485740 | -0.000630667 | -0.000928058 | -0.000333276 | 0.700000000 | 0.626865672 | 90 | 44 | 46 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_global_p05 | 0.519019442 | -0.000626499 | -0.000374786 | -0.000878213 | 0.700000000 | 0.626865672 | 45 | 23 | 22 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_p05 | 0.553870530 | -0.000613890 | -0.000635470 | -0.000592310 | 0.700000000 | 0.626865672 | 45 | 23 | 22 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_each_top21 | 0.519019442 | -0.000601807 | -0.000365882 | -0.000837731 | 0.700000000 | 0.626865672 | 42 | 21 | 21 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_global_top75 | 0.582818294 | -0.000579130 | -0.000656434 | -0.000501827 | 0.800000000 | 0.641791045 | 75 | 38 | 37 |
| latent_human_late | hgb_shallow | subject5 | all3 | contrast | drop_global_top50 | 0.583444028 | -0.000578649 | -0.000381891 | -0.000775407 | 0.600000000 | 0.641791045 | 50 | 24 | 26 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_global_top40 | 0.519019442 | -0.000577137 | -0.000465978 | -0.000688297 | 0.700000000 | 0.626865672 | 40 | 20 | 20 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_global_top40 | 0.551977192 | -0.000545905 | -0.000652424 | -0.000439386 | 0.600000000 | 0.611940299 | 40 | 20 | 20 |
| latent_human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_p10 | 0.578089633 | -0.000526683 | -0.000289679 | -0.000763686 | 0.700000000 | 0.611940299 | 90 | 43 | 47 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_each_top21 | 0.553870530 | -0.000521701 | -0.000451092 | -0.000592310 | 0.700000000 | 0.626865672 | 42 | 21 | 21 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_top40 | 0.553870530 | -0.000521463 | -0.000450616 | -0.000592310 | 0.700000000 | 0.626865672 | 40 | 20 | 20 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_top50 | 0.553870530 | -0.000519583 | -0.000491970 | -0.000547197 | 0.700000000 | 0.626865672 | 50 | 25 | 25 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_each_top25 | 0.553870530 | -0.000519583 | -0.000491970 | -0.000547197 | 0.700000000 | 0.626865672 | 50 | 25 | 25 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_global_p10 | 0.551977192 | -0.000518530 | -0.000217617 | -0.000819444 | 0.800000000 | 0.597014925 | 90 | 45 | 45 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_s4_p10 | 0.582818294 | -0.000517581 | 0.000000000 | -0.001035162 | 0.700000000 | 0.626865672 | 45 | 0 | 45 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_global_top50 | 0.551977192 | -0.000517382 | -0.000704094 | -0.000330670 | 0.700000000 | 0.611940299 | 50 | 25 | 25 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_each_top25 | 0.551977192 | -0.000517382 | -0.000704094 | -0.000330670 | 0.700000000 | 0.611940299 | 50 | 25 | 25 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_each_top21 | 0.551977192 | -0.000517257 | -0.000595128 | -0.000439386 | 0.600000000 | 0.611940299 | 42 | 21 | 21 |
| human_late | hgb_shallow | dateblock5 | all3 | contrast | drop_s4_top50 | 0.598687189 | -0.000516038 | 0.000000000 | -0.001032076 | 0.700000000 | 0.611940299 | 50 | 0 | 50 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_s4_top25 | 0.519019442 | -0.000509029 | 0.000000000 | -0.001018057 | 0.700000000 | 0.626865672 | 25 | 0 | 25 |
| human_core | lr_l2_c0p10 | dateblock5 | all3 | contrast | drop_global_p10 | 0.557152558 | -0.000508315 | -0.000364029 | -0.000652601 | 0.700000000 | 0.611940299 | 90 | 45 | 45 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_each_top13 | 0.551977192 | -0.000502938 | -0.000498622 | -0.000507254 | 0.600000000 | 0.611940299 | 26 | 13 | 13 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_s4_top50 | 0.551977192 | -0.000498112 | 0.000000000 | -0.000996223 | 0.800000000 | 0.611940299 | 50 | 0 | 50 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_global_top75 | 0.519019442 | -0.000474341 | -0.000330163 | -0.000618520 | 0.800000000 | 0.611940299 | 75 | 38 | 37 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_global_p05 | 0.551977192 | -0.000466216 | -0.000640208 | -0.000292223 | 0.600000000 | 0.611940299 | 45 | 23 | 22 |
| latent_human_late | hgb_shallow | subject5 | all3 | contrast | drop_each_top25 | 0.583444028 | -0.000464665 | -0.000269470 | -0.000659859 | 0.600000000 | 0.641791045 | 50 | 25 | 25 |
| human_late | hgb_shallow | subject5 | all3 | risk | drop_s4_top50 | 0.583334465 | -0.000464006 | 0.000000000 | -0.000928013 | 0.700000000 | 0.656716418 | 50 | 0 | 50 |
| latent_human_core | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_top50 | 0.564961521 | -0.000461258 | -0.000812527 | -0.000109988 | 0.700000000 | 0.641791045 | 50 | 22 | 28 |
| human_core | lr_l2_c0p10 | dateblock5 | all3 | contrast | drop_global_top75 | 0.557152558 | -0.000453899 | -0.000184228 | -0.000723571 | 0.700000000 | 0.626865672 | 75 | 38 | 37 |
| human_core | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_s4_top50 | 0.524332277 | -0.000447900 | 0.000000000 | -0.000895800 | 0.800000000 | 0.641791045 | 50 | 0 | 50 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_s4_top50 | 0.553870530 | -0.000446710 | 0.000000000 | -0.000893420 | 0.700000000 | 0.641791045 | 50 | 0 | 50 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_s4_p05 | 0.519019442 | -0.000439106 | 0.000000000 | -0.000878213 | 0.700000000 | 0.626865672 | 22 | 0 | 22 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_each_top13 | 0.553870530 | -0.000437126 | -0.000451312 | -0.000422941 | 0.700000000 | 0.626865672 | 26 | 13 | 13 |

## Target Breakdown

| candidate_id | target | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected |
| --- | --- | --- | --- | --- | --- |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | Q3 | -0.000132265 | 0.001905085 | 0.460342905 | 0.710932696 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | Q3 | -0.000133733 | 0.002076857 | 0.458526707 | 0.713249712 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | S4 | -0.000495100 | 0.001077171 | 0.484409907 | 0.170690429 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_each_top25 | S4 | -0.000517880 | 0.001131706 | 0.481340062 | 0.186799879 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | Q3 | -0.000132265 | 0.001905085 | 0.460342905 | 0.710932696 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | Q3 | -0.000133733 | 0.002076857 | 0.458526707 | 0.713249712 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | S4 | -0.000495100 | 0.001077171 | 0.484409907 | 0.170690429 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_p10 | S4 | -0.000517880 | 0.001131706 | 0.481340062 | 0.186799879 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | Q3 | -0.000132265 | 0.001905085 | 0.460342905 | 0.710932696 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | Q3 | -0.000133733 | 0.002076857 | 0.458526707 | 0.713249712 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | S4 | -0.000495100 | 0.001077171 | 0.484409907 | 0.170690429 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top50 | S4 | -0.000517880 | 0.001131706 | 0.481340062 | 0.186799879 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | Q3 | -0.000128294 | 0.001855644 | 0.461390360 | 0.732938787 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | Q3 | -0.000129761 | 0.002043992 | 0.459721701 | 0.735077835 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | S4 | -0.000484102 | 0.001036050 | 0.484277240 | 0.174568272 |
| all3_human_core_lr_l2_c0p10_dateblock5_contrast_q0p10_drop_global_top75 | S4 | -0.000506882 | 0.001091006 | 0.481120743 | 0.190852982 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p05 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p05 | Q3 | -0.000110980 | 0.002084542 | 0.454904160 | 0.886088679 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p05 | Q3 | -0.000112448 | 0.002221996 | 0.453021589 | 0.874524549 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p05 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p05 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p05 | S4 | -0.000502160 | 0.001132214 | 0.482927997 | 0.168290866 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_global_p05 | S4 | -0.000524940 | 0.001186749 | 0.480052803 | 0.184287809 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_p10 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_p10 | Q3 | -0.000112371 | 0.002215637 | 0.455478271 | 0.875120489 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_p10 | Q3 | -0.000113839 | 0.002352421 | 0.453648372 | 0.863839051 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_p10 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_p10 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_p10 | S4 | -0.000485699 | 0.001066750 | 0.484945733 | 0.173994476 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_p10 | S4 | -0.000508479 | 0.001121285 | 0.481806813 | 0.190253763 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_top50 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_top50 | Q3 | -0.000112371 | 0.002215637 | 0.455478271 | 0.875120489 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_top50 | Q3 | -0.000113839 | 0.002352421 | 0.453648372 | 0.863839051 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_top50 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_top50 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_top50 | S4 | -0.000469348 | 0.000941992 | 0.487464818 | 0.180055716 |
| all3_human_late_hgb_shallow_dateblock5_contrast_q0p10_drop_s4_top50 | S4 | -0.000492129 | 0.000996527 | 0.483865215 | 0.196574622 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_each_top21 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_each_top21 | Q3 | -0.000103525 | 0.002023488 | 0.453249756 | 0.949904515 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_each_top21 | Q3 | -0.000104992 | 0.002172965 | 0.451656372 | 0.936627192 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_each_top21 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_each_top21 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_each_top21 | S4 | -0.000468512 | 0.001103077 | 0.480680187 | 0.180377142 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_each_top21 | S4 | -0.000491292 | 0.001157612 | 0.477827463 | 0.196909265 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_global_p10 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_global_p10 | Q3 | -0.000101079 | 0.001999639 | 0.452609197 | 0.972886405 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_global_p10 | Q3 | -0.000102547 | 0.002149116 | 0.451044396 | 0.958963559 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_global_p10 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_global_p10 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_global_p10 | S4 | -0.000453955 | 0.001085108 | 0.480415025 | 0.186161378 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_global_p10 | S4 | -0.000476735 | 0.001139643 | 0.477520967 | 0.202921921 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_s4_p10 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_s4_p10 | Q3 | -0.000112371 | 0.002215637 | 0.455478271 | 0.875120489 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_s4_p10 | Q3 | -0.000113839 | 0.002352421 | 0.453648372 | 0.863839051 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_s4_p10 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_s4_p10 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_s4_p10 | S4 | -0.000453955 | 0.001085108 | 0.480415025 | 0.186161378 |
| all3_human_late_hgb_shallow_dateblock5_risk_q0p10_drop_s4_p10 | S4 | -0.000476735 | 0.001139643 | 0.477520967 | 0.202921921 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top40 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top40 | Q3 | -0.000112371 | 0.002215637 | 0.455478271 | 0.875120489 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top40 | Q3 | -0.000113839 | 0.002352421 | 0.453648372 | 0.863839051 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top40 | S2 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top40 | S3 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top40 | S4 | -0.000419850 | 0.000983082 | 0.475694369 | 0.201283666 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top40 | S4 | -0.000442630 | 0.001037618 | 0.472838573 | 0.218557358 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top50 | Q1 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top50 | Q3 | -0.000112371 | 0.002215637 | 0.455478271 | 0.875120489 |
| all3_human_late_hgb_shallow_subject5_risk_q0p10_drop_s4_top50 | Q3 | -0.000113839 | 0.002352421 | 0.453648372 | 0.863839051 |

## Decision Rule

- If selected submissions are non-empty, the top file is the first lifestyle-conditioned JEPA submission candidate.
- If selected is empty but expected/adverse/support improve separately, the branch remains diagnostic and needs a stricter learned cell target.
- If materialization is broadly adverse, E264 was mainly an OOF/broad-rollback artifact.
