# E290 Lifestyle Row-Placement Law Audit

## Question

Can the Q3/S4 lifestyle slices from E289 learn where they should be applied, rather than being applied as a global target shift?

## Train Placement Stress

- placement rows: `420`
- train placement gates: `59`

| policy_id | target | label_mode | gate_group | model | top_frac | full_aug_delta | actual_delta | null_median | dominance | row_dominance | subject_dominance | dateblock_dominance | train_gate_bool |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow | Q3 | strong35 | dateblock5 | hgb_shallow | 0.350000 | -0.014466 | -0.024399 | -0.009823 | 0.968750 | 1.000000 | 1.000000 | 0.906250 | True |
| Q3_raw_human_context_subject5_pc_strong35_dateblock5_lr_l1 | Q3 | strong35 | dateblock5 | lr_l1 | 0.500000 | -0.014466 | -0.024376 | -0.014842 | 0.864583 | 1.000000 | 0.968750 | 0.625000 | True |
| Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2 | Q3 | good | dateblock5 | lr_l2 | 0.500000 | -0.014466 | -0.022813 | -0.010690 | 0.958333 | 1.000000 | 0.937500 | 0.937500 | True |
| Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow | Q3 | good | dateblock5 | hgb_shallow | 0.500000 | -0.014466 | -0.020271 | -0.008925 | 0.989583 | 1.000000 | 0.968750 | 1.000000 | True |
| Q3_raw_human_context_subject5_pc_strong35_subject5_hgb_shallow | Q3 | strong35 | subject5 | hgb_shallow | 0.500000 | -0.014466 | -0.020097 | -0.012493 | 0.895833 | 1.000000 | 0.968750 | 0.718750 | True |
| Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow | Q3 | good | dateblock5 | hgb_shallow | 0.700000 | -0.014466 | -0.019908 | -0.010952 | 0.916667 | 0.937500 | 0.875000 | 0.937500 | True |
| Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow | Q3 | strong35 | dateblock5 | hgb_shallow | 0.250000 | -0.014466 | -0.019893 | -0.008489 | 0.947917 | 1.000000 | 0.968750 | 0.875000 | True |
| Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2 | Q3 | good | dateblock5 | lr_l2 | 0.250000 | -0.014466 | -0.018877 | -0.009574 | 0.906250 | 1.000000 | 0.968750 | 0.750000 | True |
| Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow | Q3 | good | dateblock5 | hgb_shallow | 0.350000 | -0.014466 | -0.018466 | -0.009008 | 0.937500 | 0.968750 | 0.906250 | 0.937500 | True |
| Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow | Q3 | good | dateblock5 | hgb_shallow | 0.250000 | -0.014466 | -0.016563 | -0.006226 | 0.947917 | 1.000000 | 1.000000 | 0.843750 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1 | Q3 | strong35 | dateblock5 | lr_l1 | 0.700000 | -0.006200 | -0.015035 | -0.006395 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l2 | Q3 | strong35 | dateblock5 | lr_l2 | 0.500000 | -0.006200 | -0.014861 | -0.007124 | 0.958333 | 1.000000 | 0.875000 | 1.000000 | True |
| Q3_raw_human_context_subject5_pc_good_subject5_lr_l2 | Q3 | good | subject5 | lr_l2 | 0.250000 | -0.014466 | -0.013714 | -0.004763 | 0.885417 | 0.906250 | 1.000000 | 0.750000 | True |
| S4_family_jepa_context_dateblock5_cluster6_strong35_dateblock5_lr_l2 | S4 | strong35 | dateblock5 | lr_l2 | 0.700000 | -0.011131 | -0.013574 | -0.010376 | 0.885417 | 0.875000 | 0.906250 | 0.875000 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1 | Q3 | strong35 | dateblock5 | lr_l1 | 0.500000 | -0.006200 | -0.013270 | -0.005110 | 0.916667 | 0.968750 | 0.812500 | 0.968750 | True |
| S4_raw_human_context_dateblock5_cluster6_strong35_subject5_hgb_shallow | S4 | strong35 | subject5 | hgb_shallow | 0.700000 | -0.009936 | -0.013192 | -0.009600 | 0.875000 | 0.937500 | 0.968750 | 0.718750 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l2 | Q3 | strong35 | dateblock5 | lr_l2 | 0.350000 | -0.006200 | -0.013022 | -0.005419 | 0.989583 | 1.000000 | 0.968750 | 1.000000 | True |
| S4_family_jepa_context_dateblock5_cluster6_strong35_subject5_lr_l2 | S4 | strong35 | subject5 | lr_l2 | 0.500000 | -0.011131 | -0.012482 | -0.007069 | 0.927083 | 0.906250 | 0.906250 | 0.968750 | True |
| S4_raw_human_context_dateblock5_cluster6_good_subject5_hgb_shallow | S4 | good | subject5 | hgb_shallow | 0.350000 | -0.009936 | -0.012366 | -0.003272 | 0.989583 | 1.000000 | 1.000000 | 0.968750 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1 | Q3 | strong35 | dateblock5 | lr_l1 | 0.350000 | -0.006200 | -0.011782 | -0.005591 | 0.958333 | 0.968750 | 0.906250 | 1.000000 | True |
| S4_raw_human_context_dateblock5_cluster6_good_subject5_hgb_shallow | S4 | good | subject5 | hgb_shallow | 0.500000 | -0.009936 | -0.011747 | -0.005146 | 0.927083 | 0.906250 | 0.937500 | 0.937500 | True |
| S4_family_jepa_context_dateblock5_cluster6_strong35_subject5_hgb_shallow | S4 | strong35 | subject5 | hgb_shallow | 0.500000 | -0.011131 | -0.011504 | -0.006705 | 0.854167 | 0.843750 | 0.937500 | 0.781250 | True |
| S4_raw_human_context_dateblock5_cluster6_strong35_dateblock5_hgb_shallow | S4 | strong35 | dateblock5 | hgb_shallow | 0.500000 | -0.009936 | -0.010997 | -0.004479 | 0.937500 | 0.812500 | 1.000000 | 1.000000 | True |
| S4_family_jepa_context_dateblock5_cluster6_strong35_subject5_hgb_shallow | S4 | strong35 | subject5 | hgb_shallow | 0.350000 | -0.011131 | -0.010933 | -0.005842 | 0.906250 | 0.937500 | 0.968750 | 0.812500 | True |
| Q3_family_jepa_context_dateblock5_pc_good_subject5_lr_l1 | Q3 | good | subject5 | lr_l1 | 0.500000 | -0.006200 | -0.010729 | -0.002992 | 0.927083 | 0.937500 | 0.843750 | 1.000000 | True |
| Q3_family_jepa_context_dateblock5_pc_good_subject5_lr_l2 | Q3 | good | subject5 | lr_l2 | 0.700000 | -0.006200 | -0.010596 | -0.006827 | 0.802083 | 0.843750 | 0.781250 | 0.781250 | True |
| Q3_family_jepa_context_dateblock5_pc_good_dateblock5_lr_l1 | Q3 | good | dateblock5 | lr_l1 | 0.700000 | -0.006200 | -0.009317 | -0.005239 | 0.822917 | 0.875000 | 0.718750 | 0.875000 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_hgb_shallow | Q3 | strong35 | dateblock5 | hgb_shallow | 0.350000 | -0.006200 | -0.009048 | -0.003537 | 0.895833 | 0.937500 | 0.750000 | 1.000000 | True |
| Q3_family_jepa_context_dateblock5_pc_good_subject5_hgb_shallow | Q3 | good | subject5 | hgb_shallow | 0.700000 | -0.006200 | -0.008493 | -0.004432 | 0.822917 | 0.781250 | 0.875000 | 0.812500 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_subject5_hgb_shallow | Q3 | strong35 | subject5 | hgb_shallow | 0.350000 | -0.006200 | -0.008238 | -0.001818 | 0.927083 | 0.968750 | 0.937500 | 0.875000 | True |
| S4_family_jepa_context_dateblock5_cluster6_strong35_subject5_lr_l1 | S4 | strong35 | subject5 | lr_l1 | 0.350000 | -0.011131 | -0.008214 | -0.003736 | 0.822917 | 0.718750 | 0.875000 | 0.875000 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_subject5_lr_l1 | Q3 | strong35 | subject5 | lr_l1 | 0.700000 | -0.006200 | -0.007976 | -0.004501 | 0.822917 | 0.718750 | 0.875000 | 0.875000 | True |
| S4_family_jepa_context_dateblock5_cluster6_strong35_subject5_hgb_shallow | S4 | strong35 | subject5 | hgb_shallow | 0.150000 | -0.011131 | -0.007849 | -0.003390 | 0.833333 | 0.968750 | 0.843750 | 0.687500 | True |
| S4_raw_human_context_dateblock5_cluster6_strong35_dateblock5_hgb_shallow | S4 | strong35 | dateblock5 | hgb_shallow | 0.350000 | -0.009936 | -0.007645 | -0.003134 | 0.885417 | 0.937500 | 0.781250 | 0.937500 | True |
| S4_raw_human_context_dateblock5_cluster6_good_subject5_hgb_shallow | S4 | good | subject5 | hgb_shallow | 0.250000 | -0.009936 | -0.007557 | -0.001460 | 0.937500 | 0.906250 | 0.937500 | 0.968750 | True |
| S1_raw_human_context_dateblock5_pc_strong35_subject5_lr_l1 | S1 | strong35 | subject5 | lr_l1 | 0.150000 | -0.003654 | -0.006888 | -0.000962 | 0.906250 | 0.968750 | 0.812500 | 0.937500 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_subject5_lr_l2 | Q3 | strong35 | subject5 | lr_l2 | 0.350000 | -0.006200 | -0.006664 | -0.002785 | 0.833333 | 0.812500 | 0.875000 | 0.812500 | True |
| S4_raw_human_context_dateblock5_cluster6_strong35_dateblock5_hgb_shallow | S4 | strong35 | dateblock5 | hgb_shallow | 0.250000 | -0.009936 | -0.006649 | -0.002567 | 0.864583 | 0.843750 | 0.812500 | 0.937500 | True |
| Q3_family_jepa_context_dateblock5_pc_good_subject5_hgb_shallow | Q3 | good | subject5 | hgb_shallow | 0.500000 | -0.006200 | -0.006498 | -0.001798 | 0.802083 | 0.656250 | 0.875000 | 0.875000 | True |
| Q3_family_jepa_context_dateblock5_pc_strong35_subject5_lr_l1 | Q3 | strong35 | subject5 | lr_l1 | 0.250000 | -0.006200 | -0.006400 | -0.000915 | 0.895833 | 0.843750 | 0.843750 | 1.000000 | True |

## Materialization Governor

- candidates: `48`
- public-free ready candidates: `0`

| basename | target | label_mode | gate_group | model | top_frac | delta_mode | scale | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf50_centered_s050_4bfc096b.csv | Q3 | good | dateblock5 | lr_l2 | 0.500000 | centered | 0.500000 | promote_candidate | -0.000495 | -0.000308 | 1.000000 | 0.000000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf50_centered_s050_ca3a22bc.csv | Q3 | good | dateblock5 | hgb_shallow | 0.500000 | centered | 0.500000 | promote_candidate | -0.000471 | -0.000299 | 1.000000 | 0.133333 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf70_centered_s050_6b9b622c.csv | Q3 | good | dateblock5 | hgb_shallow | 0.700000 | centered | 0.500000 | promote_candidate | -0.000450 | -0.000278 | 1.000000 | 0.066667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf35_centered_s050_25de31de.csv | Q3 | good | dateblock5 | hgb_shallow | 0.350000 | centered | 0.500000 | promote_candidate | -0.000381 | -0.000256 | 1.000000 | 0.266667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf50_raw_s050_b7ccfa00.csv | Q3 | good | dateblock5 | lr_l2 | 0.500000 | raw | 0.500000 | promote_candidate | -0.000414 | -0.000243 | 1.000000 | 0.000000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf25_centered_s050_f1fad500.csv | Q3 | good | dateblock5 | lr_l2 | 0.250000 | centered | 0.500000 | promote_candidate | -0.000363 | -0.000236 | 1.000000 | 0.133333 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf25_raw_s050_51cf24a7.csv | Q3 | good | dateblock5 | lr_l2 | 0.250000 | raw | 0.500000 | promote_candidate | -0.000363 | -0.000235 | 1.000000 | 0.066667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1_tf70_centered_s050_30606fbd.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.700000 | centered | 0.500000 | promote_candidate | -0.000344 | -0.000233 | 1.000000 | 1.000000 | 1.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf50_raw_s050_74939ffd.csv | Q3 | good | dateblock5 | hgb_shallow | 0.500000 | raw | 0.500000 | promote_candidate | -0.000383 | -0.000226 | 1.000000 | 0.066667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf35_raw_s050_1ea8a352.csv | Q3 | good | dateblock5 | hgb_shallow | 0.350000 | raw | 0.500000 | promote_candidate | -0.000328 | -0.000219 | 1.000000 | 0.066667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l2_tf50_centered_s050_158fd2bf.csv | Q3 | strong35 | dateblock5 | lr_l2 | 0.500000 | centered | 0.500000 | promote_candidate | -0.000271 | -0.000183 | 1.000000 | 0.866667 | 0.600000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf25_centered_s050_b6dfaaae.csv | Q3 | good | dateblock5 | hgb_shallow | 0.250000 | centered | 0.500000 | promote_candidate | -0.000281 | -0.000180 | 1.000000 | 0.600000 | 0.400000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf50_centered_s025_806d8c73.csv | Q3 | good | dateblock5 | lr_l2 | 0.500000 | centered | 0.250000 | promote_candidate | -0.000236 | -0.000155 | 1.000000 | 0.266667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf25_raw_s050_d7b9f020.csv | Q3 | good | dateblock5 | hgb_shallow | 0.250000 | raw | 0.500000 | promote_candidate | -0.000239 | -0.000154 | 1.000000 | 0.133333 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf50_centered_s025_036ece27.csv | Q3 | good | dateblock5 | hgb_shallow | 0.500000 | centered | 0.250000 | promote_candidate | -0.000222 | -0.000149 | 1.000000 | 0.400000 | 0.200000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_subject5_hgb_shallow_tf50_centered_s050_699d69ad.csv | Q3 | strong35 | subject5 | hgb_shallow | 0.500000 | centered | 0.500000 | promote_candidate | -0.000268 | -0.000143 | 1.000000 | 0.200000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf70_centered_s025_b791a8a5.csv | Q3 | good | dateblock5 | hgb_shallow | 0.700000 | centered | 0.250000 | promote_candidate | -0.000211 | -0.000140 | 1.000000 | 0.133333 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf50_raw_s025_4cb9a5d6.csv | Q3 | good | dateblock5 | lr_l2 | 0.500000 | raw | 0.250000 | promote_candidate | -0.000191 | -0.000122 | 1.000000 | 0.000000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf35_centered_s025_d778c3b2.csv | Q3 | good | dateblock5 | hgb_shallow | 0.350000 | centered | 0.250000 | promote_candidate | -0.000180 | -0.000119 | 1.000000 | 0.133333 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf25_centered_s025_cdb403c2.csv | Q3 | good | dateblock5 | lr_l2 | 0.250000 | centered | 0.250000 | promote_candidate | -0.000175 | -0.000118 | 1.000000 | 0.266667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_lr_l2_tf25_raw_s025_1a67bec3.csv | Q3 | good | dateblock5 | lr_l2 | 0.250000 | raw | 0.250000 | promote_candidate | -0.000175 | -0.000118 | 1.000000 | 0.200000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf50_raw_s025_7f258c7f.csv | Q3 | good | dateblock5 | hgb_shallow | 0.500000 | raw | 0.250000 | promote_candidate | -0.000177 | -0.000114 | 1.000000 | 0.066667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1_tf70_centered_s025_c02282a5.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.700000 | centered | 0.250000 | promote_candidate | -0.000167 | -0.000113 | 1.000000 | 0.400000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf35_centered_s050_46d350a9.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.350000 | centered | 0.500000 | promote_candidate | -0.000202 | -0.000105 | 1.000000 | 0.000000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf35_raw_s025_c9190990.csv | Q3 | good | dateblock5 | hgb_shallow | 0.350000 | raw | 0.250000 | promote_candidate | -0.000152 | -0.000101 | 1.000000 | 0.000000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf25_centered_s025_b696c851.csv | Q3 | good | dateblock5 | hgb_shallow | 0.250000 | centered | 0.250000 | promote_candidate | -0.000133 | -0.000090 | 1.000000 | 0.400000 | 0.200000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l2_tf50_centered_s025_1e7ae419.csv | Q3 | strong35 | dateblock5 | lr_l2 | 0.500000 | centered | 0.250000 | promote_candidate | -0.000131 | -0.000089 | 1.000000 | 0.600000 | 0.400000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf25_raw_s025_4f2eacc1.csv | Q3 | good | dateblock5 | hgb_shallow | 0.250000 | raw | 0.250000 | promote_candidate | -0.000112 | -0.000077 | 1.000000 | 0.333333 | 0.200000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_subject5_hgb_shallow_tf50_centered_s025_0c5b1a14.csv | Q3 | strong35 | subject5 | hgb_shallow | 0.500000 | centered | 0.250000 | promote_candidate | -0.000124 | -0.000072 | 1.000000 | 0.200000 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf70_raw_s025_106cecf4.csv | Q3 | good | dateblock5 | hgb_shallow | 0.700000 | raw | 0.250000 | promote_candidate | -0.000120 | -0.000066 | 1.000000 | 0.066667 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf25_centered_s050_4bad5abb.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.250000 | centered | 0.500000 | promote_candidate | -0.000114 | -0.000058 | 0.933333 | 0.333333 | 0.200000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf35_centered_s025_7e33df7a.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.350000 | centered | 0.250000 | promote_candidate | -0.000098 | -0.000053 | 1.000000 | 0.133333 | 0.000000 | blocked_by_matched_nulls |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_good_dateblock5_hgb_shallow_tf70_raw_s050_82a3c9e4.csv | Q3 | good | dateblock5 | hgb_shallow | 0.700000 | raw | 0.500000 | information_sensor_only | -0.000271 | -0.000131 | 0.466667 | 0.066667 | 0.000000 | information_sensor_only |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_lr_l1_tf50_centered_s050_3577ff3f.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.500000 | centered | 0.500000 | too_small_to_submit | -0.000156 | -0.000048 | 0.866667 | 0.066667 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_subject5_hgb_shallow_tf50_raw_s050_00923401.csv | Q3 | strong35 | subject5 | hgb_shallow | 0.500000 | raw | 0.500000 | too_small_to_submit | -0.000151 | -0.000038 | 0.333333 | 0.400000 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf35_raw_s050_88246d9b.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.350000 | raw | 0.500000 | too_small_to_submit | -0.000117 | -0.000034 | 0.266667 | 0.266667 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf25_centered_s025_5fbb93fd.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.250000 | centered | 0.250000 | too_small_to_submit | -0.000056 | -0.000029 | 0.000000 | 0.466667 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_lr_l1_tf50_centered_s025_ef7d491f.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.500000 | centered | 0.250000 | too_small_to_submit | -0.000070 | -0.000024 | 0.000000 | 0.133333 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_subject5_hgb_shallow_tf50_raw_s025_aaad99b3.csv | Q3 | strong35 | subject5 | hgb_shallow | 0.500000 | raw | 0.250000 | too_small_to_submit | -0.000060 | -0.000020 | 0.000000 | 0.133333 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf35_raw_s025_4acef983.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.350000 | raw | 0.250000 | too_small_to_submit | -0.000053 | -0.000017 | 0.000000 | 0.333333 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf25_raw_s050_16fa5d4e.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.250000 | raw | 0.500000 | too_small_to_submit | -0.000045 | -0.000002 | 0.000000 | 0.533333 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_hgb_shallow_tf25_raw_s025_4ed0d068.csv | Q3 | strong35 | dateblock5 | hgb_shallow | 0.250000 | raw | 0.250000 | too_small_to_submit | -0.000021 | -0.000001 | 0.000000 | 0.600000 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_lr_l1_tf50_raw_s025_77b15632.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.500000 | raw | 0.250000 | below_selector_resolution | 0.000010 | 0.000045 | 0.000000 | 0.066667 | 0.000000 | below_selector_resolution |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l2_tf50_raw_s025_c9c5f463.csv | Q3 | strong35 | dateblock5 | lr_l2 | 0.500000 | raw | 0.250000 | below_selector_resolution | 0.000067 | 0.000084 | 0.000000 | 0.400000 | 0.200000 | below_selector_resolution |
| submission_e290_lifeplace_Q3_raw_human_context_subject5_pc_strong35_dateblock5_lr_l1_tf50_raw_s050_d61c5c1d.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.500000 | raw | 0.500000 | too_small_to_submit | -0.000012 | 0.000089 | 0.000000 | 0.200000 | 0.000000 | too_small_to_submit |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1_tf70_raw_s025_49580099.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.700000 | raw | 0.250000 | block_or_reject | 0.000119 | 0.000148 | 0.000000 | 0.533333 | 0.200000 | block_or_reject |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l2_tf50_raw_s050_f36736d0.csv | Q3 | strong35 | dateblock5 | lr_l2 | 0.500000 | raw | 0.500000 | block_or_reject | 0.000106 | 0.000157 | 0.000000 | 0.333333 | 0.200000 | block_or_reject |
| submission_e290_lifeplace_Q3_family_jepa_context_dateblock5_pc_strong35_dateblock5_lr_l1_tf70_raw_s050_6f0bd0d8.csv | Q3 | strong35 | dateblock5 | lr_l1 | 0.700000 | raw | 0.500000 | block_or_reject | 0.000205 | 0.000269 | 0.000000 | 0.400000 | 0.400000 | block_or_reject |

## Decision

No E290 candidate is public-free ready. Lifestyle row-placement remains a diagnostic target, not a submission translator.

## Interpretation

This audit asks whether the E289 signal failed because placement was unknown. A train placement gate is necessary but not sufficient: it must also produce an E247-current movement that beats matched test nulls.

## Files

- `e290_lifestyle_row_placement_train_summary.csv`
- `e290_lifestyle_row_placement_candidate_summary.csv`
- `e290_lifestyle_row_placement_governor_summary.csv`
