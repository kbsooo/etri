# E367 Public Row-Mask Validity Latent

## Question

Can known public-good/public-bad movement support be converted into a lifestyle-predictable row-mask validity latent that improves the E365 donor-graft family and beats null row masks?

## Method

- Anchor: E247 public-best probability tensor.
- Context: E328/E358 own-lifestyle state plus human/social story axes.
- Target representation: row-level public-good support minus public-bad support, built from fixed known-public observations.
- Action: row-wise damp/boost and target-specific routing of the E365 donor-graft family.
- Anti-collapse: lifestyle predictability check, leave-public row-mask stability, and null/permuted row-mask candidate stress.

## Public Row-Mask Weights

| basename | file | public_lb | delta_vs_e247 | good_weight | bad_weight | excluded |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576281 | 0.000122 | 0.155967 | 0.005479 | none |
| submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | 0.576291 | 0.000132 | 0.150807 | 0.006144 | none |
| submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | 0.576300 | 0.000141 | 0.146607 | 0.006717 | none |
| submission_mixmin_0c916bb4.csv | submission_mixmin_0c916bb4.csv | 0.576307 | 0.000148 | 0.143759 | 0.007122 | none |
| submission_e176_abl_q2_to0p75_91e49725.csv | submission_e176_abl_q2_to0p75_91e49725.csv | 0.576312 | 0.000153 | 0.141446 | 0.007462 | none |
| submission_e267_humansocial_tail_balanced_2936100f.csv | submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329 | 0.000171 | 0.133846 | 0.008649 | none |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576408 | 0.000249 | 0.104793 | 0.014403 | none |
| submission_e323_5508f966_uploadsafe.csv | submission_e323_5508f966_uploadsafe.csv | 0.577036 | 0.000877 | 0.014727 | 0.078836 | none |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577287 | 0.001128 | 0.006720 | 0.110755 | none |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577945 | 0.001786 | 0.000858 | 0.206075 | none |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303 | 0.002144 | 0.000280 | 0.263781 | none |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427 | 0.002268 | 0.000190 | 0.284577 | none |

## Lifestyle Predictability Diagnostics

| target | kfold_spearman | group_spearman | null_p95 | beats_null_p95 | target_std | feature_count |
| --- | --- | --- | --- | --- | --- | --- |
| public_row_validity | 0.073804 | 0.064222 | 0.135689 | False | 0.368270 | 47 |
| public_bad_row_support | 0.141450 | 0.092218 | 0.100992 | True | 0.288673 | 47 |
| public_validity_Q1 | 0.123355 | 0.038101 | 0.169099 | False | 0.378295 | 47 |
| public_validity_Q2 | 0.392982 | 0.108419 | 0.105015 | True | 0.405204 | 47 |
| public_validity_Q3 | 0.033829 | -0.009188 | 0.034555 | False | 0.391328 | 47 |
| public_validity_S1 | 0.110407 | 0.131327 | 0.099875 | True | 0.305324 | 47 |
| public_signed_gap | 0.099758 | 0.072201 | 0.077407 | True | 0.288673 | 47 |

## Leave-Public Row-Mask Stability

| index | dropped_public | public_row_validity_spearman | public_bad_row_support_spearman | public_validity_Q3_spearman | public_validity_S1_spearman |
| --- | --- | --- | --- | --- | --- |
| count | 12 | 12.000000 | 12.000000 | 12.000000 | 12.000000 |
| unique | 12 |  |  |  |  |
| top | submission_hybrid_0p578_logit_after_subject_final9_strict.csv |  |  |  |  |
| freq | 1 |  |  |  |  |
| mean |  | 0.973382 | 0.960293 | 0.966165 | 0.946723 |
| std |  | 0.055809 | 0.088502 | 0.065970 | 0.072457 |
| min |  | 0.827446 | 0.735522 | 0.813759 | 0.790552 |
| 25% |  | 0.992910 | 0.992087 | 0.982289 | 0.910362 |
| 50% |  | 0.997247 | 0.999954 | 0.997296 | 0.982386 |
| 75% |  | 0.998029 | 0.999978 | 0.997557 | 0.998719 |
| max |  | 0.998950 | 1.000000 | 0.999984 | 0.999229 |

## Inputs

- generated candidates: `30`
- combined pool: `1616`
- feature views: `all`(164), `axis`(62), `target`(60), `anatomy`(18), `bad_good`(50), `compact`(20), `rowmask`(35)

## Scenario Summary

| feature_view | scenarios | top_generated_rate | top_e365_rate | e365_rank_mean | generated_gated_mean |
| --- | --- | --- | --- | --- | --- |
| all | 14 | 0.928571 | 0.071429 | 5.857143 | 9.714286 |
| anatomy | 14 | 1.000000 | 0.000000 | 5.142857 | 10.000000 |
| axis | 14 | 1.000000 | 0.000000 | 12.500000 | 10.000000 |
| bad_good | 14 | 1.000000 | 0.000000 | 15.428571 | 9.500000 |
| compact | 14 | 1.000000 | 0.000000 | 5.142857 | 10.000000 |
| rowmask | 14 | 1.000000 | 0.000000 | 5.642857 | 10.000000 |
| target | 14 | 1.000000 | 0.000000 | 5.857143 | 10.000000 |

## Top Jackknife Support

| variant | family | candidate_origin | top1_count | top5_count | top10_count | rank_mean | score_mean | pred_mean | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e367_null_validboost_baddamp_random_validity | null_public_rowmask_gate | e367_generated | 89 | 95 | 97 | 1.226804 | 6.332296 | 0.000397 | analysis_outputs/submission_e367_publicrowmask_e367_null_validboost_baddamp_random_validity_f634f0b3.csv |
| e367_null_source_switch_random_validity | null_public_rowmask_gate | e367_generated | 5 | 97 | 97 | 2.082474 | 6.241835 | 0.000408 | analysis_outputs/submission_e367_publicrowmask_e367_null_source_switch_random_validity_9c61acf7.csv |
| e367_direct_validboost_baddamp_amp0.97 | diagnostic_direct_public_rowmask_gate | e367_generated | 3 | 97 | 97 | 2.948454 | 6.078536 | 0.000332 | analysis_outputs/submission_e367_publicrowmask_e367_direct_validboost_baddamp_amp0_97_05227c33.csv |
| e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 1 | 34 | 76 | 7.938776 | 5.714310 | 0.000456 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_07638e6a.csv |
| e367_direct_validboost_baddamp_amp1.00 | diagnostic_direct_public_rowmask_gate | e367_generated | 0 | 95 | 97 | 4.020619 | 6.001932 | 0.000333 | analysis_outputs/submission_e367_publicrowmask_e367_direct_validboost_baddamp_amp1_00_08739715.csv |
| e367_direct_validboost_baddamp_amp1.03 | diagnostic_direct_public_rowmask_gate | e367_generated | 0 | 56 | 96 | 5.577320 | 5.894813 | 0.000333 | analysis_outputs/submission_e367_publicrowmask_e367_direct_validboost_baddamp_amp1_03_7e5abcb1.csv |
| e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 7 | 58 | 9.410959 | 5.545517 | 0.000487 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_3aeb0277.csv |
| e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 6 | 80 | 8.092784 | 5.675050 | 0.000444 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_1198dfee.csv |
| e367_null_target_validity_perm_validity_0 | null_public_rowmask_gate | e367_generated | 0 | 2 | 88 | 8.412371 | 5.655148 | 0.000436 | analysis_outputs/submission_e367_publicrowmask_e367_null_target_validity_perm_validity_0_9e2a3d59.csv |
| e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 1 | 11 | 13.485294 | 5.275220 | 0.000218 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_1f057e41.csv |
| e367_target_validity_amp1.00 | learned_public_rowmask_gate | e367_generated | 0 | 0 | 92 | 8.876289 | 5.632733 | 0.000395 | analysis_outputs/submission_e367_publicrowmask_e367_target_validity_amp1_00_f46fc0ab.csv |
| e367_target_validity_amp1.03 | learned_public_rowmask_gate | e367_generated | 0 | 0 | 57 | 10.237113 | 5.590840 | 0.000396 | analysis_outputs/submission_e367_publicrowmask_e367_target_validity_amp1_03_970904ce.csv |
| e367_direct_target_validity_amp1.03 | diagnostic_direct_public_rowmask_gate | e367_generated | 0 | 0 | 22 | 11.463918 | 5.542996 | 0.000396 | analysis_outputs/submission_e367_publicrowmask_e367_direct_target_validity_amp1_03_ce6ee54c.csv |
| e367_null_target_validity_perm_validity_1 | null_public_rowmask_gate | e367_generated | 0 | 0 | 2 | 19.604167 | 5.191150 | 0.000434 | analysis_outputs/submission_e367_publicrowmask_e367_null_target_validity_perm_validity_1_86ef167c.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.75_s11.30 | target_scale | e364_existing | 0 | 0 | 1 | 22.833333 | 4.849122 | 0.000278 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_75_s11_30_d02aaf2d.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.45_s11.00 | target_scale | e364_existing | 0 | 0 | 3 | 25.147541 | 4.730059 | 0.000188 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_45_s11_00_2ffbb23b.csv |
| e362_scale_g1.06_q11.08_q20.90_q31.00_s11.30 | target_scale | e364_existing | 0 | 0 | 0 | 27.578947 | 4.829831 | 0.000314 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q31_00_s11_30_bffaf250.csv |
| e362_scale_g1.03_q11.08_q20.90_q31.00_s11.30 | target_scale | e364_existing | 0 | 0 | 0 | 28.710526 | 4.802617 | 0.000314 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q31_00_s11_30_58916996.csv |
| e362_scale_g1.03_q11.08_q20.90_q30.45_s11.00 | target_scale | e364_existing | 0 | 0 | 1 | 32.950000 | 4.666404 | 0.000187 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q30_45_s11_00_de6e65a6.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.75_s11.00 | target_scale | e364_existing | 0 | 0 | 0 | 33.174603 | 4.616425 | 0.000210 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_75_s11_00_6b534dd4.csv |
| e362_scale_g1.03_q11.04_q20.90_q30.45_s11.00 | target_scale | e364_existing | 0 | 0 | 0 | 36.366667 | 4.626038 | 0.000186 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_04_q20_90_q30_45_s11_00_dd241ebc.csv |
| e362_scale_g1.06_q11.04_q20.90_q31.00_s11.30 | target_scale | e364_existing | 0 | 0 | 0 | 36.697368 | 4.701393 | 0.000314 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_04_q20_90_q31_00_s11_30_50acaf80.csv |
| e362_scale_g1.06_q11.08_q21.00_q30.45_s11.30 | target_scale | e364_existing | 0 | 0 | 1 | 38.193548 | 4.627716 | 0.000215 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q21_00_q30_45_s11_30_05f9c7f8.csv |
| e362_scale_g0.96_q11.08_q20.90_q30.75_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 39.573770 | 4.554713 | 0.000189 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q30_75_s10_90_f2243d75.csv |
| e362_scale_g0.96_q11.08_q20.90_q31.00_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 40.163934 | 4.542744 | 0.000189 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q31_00_s10_90_6cd43bb3.csv |
| e362_scale_g1.06_q11.08_q20.90_q31.00_s11.15 | target_scale | e364_existing | 0 | 0 | 0 | 40.257576 | 4.606687 | 0.000219 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q31_00_s11_15_31e02c1f.csv |
| e362_scale_g1.06_q11.08_q20.90_q30.45_s11.00 | target_scale | e364_existing | 0 | 0 | 0 | 40.766667 | 4.632244 | 0.000187 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_08_q20_90_q30_45_s11_00_3743ccda.csv |
| e362_scale_g1.03_q11.08_q20.90_q31.00_s11.15 | target_scale | e364_existing | 0 | 0 | 0 | 43.059701 | 4.575230 | 0.000229 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q31_00_s11_15_c0911ad0.csv |
| e362_scale_g1.03_q11.08_q21.00_q30.45_s11.30 | target_scale | e364_existing | 0 | 0 | 0 | 43.587302 | 4.582715 | 0.000215 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q21_00_q30_45_s11_30_7c3380a0.csv |
| e362_scale_g1.06_q11.04_q20.90_q30.45_s11.00 | target_scale | e364_existing | 0 | 0 | 0 | 46.883333 | 4.574581 | 0.000187 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_06_q11_04_q20_90_q30_45_s11_00_e0688e7d.csv |

## Top Public-Like Scores

| variant | family | candidate_origin | e367_public_like_score | e367_pred_public_delta_mean | e367_pred_public_delta_std | public_bad_axis_sum | rowstate_pred_public_loss_mean | rowmask_wmean_pred_public_row_validity | rowmask_wmean_pred_public_bad_row_support | rowmask_corr_pred_public_row_validity | e363_submission_gate | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e362_ablate_s1_only_amp1.00 | target_ablation | e364_existing | 6.878419 | 0.000171 | 0.000087 | 0.000899 | 0.000168 | -0.051309 | -0.030925 | 0.017256 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_00_28f4e72a.csv |
| e362_ablate_s1_only_amp1.08 | target_ablation | e364_existing | 6.871272 | 0.000171 | 0.000087 | 0.000971 | 0.000168 | -0.051309 | -0.030925 | 0.017256 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_08_cc145be9.csv |
| e362_ablate_s1_only_amp1.16 | target_ablation | e364_existing | 6.870900 | 0.000172 | 0.000087 | 0.001043 | 0.000168 | -0.051309 | -0.030925 | 0.017256 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_16_5a253895.csv |
| e362_ablate_s1_only_amp1.28 | target_ablation | e364_existing | 6.866136 | 0.000172 | 0.000087 | 0.001151 | 0.000169 | -0.051309 | -0.030925 | 0.017256 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_28_e777faa5.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.65 | donor_blend | e364_existing | 6.718874 | 0.000259 | 0.000148 | 0.000830 | 0.000258 | -0.028704 | 0.046508 | -0.010289 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_65_3399f779.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.65 | donor_blend | e364_existing | 6.696968 | 0.000236 | 0.000131 | 0.000638 | 0.000278 | -0.048609 | 0.032488 | -0.009916 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_65_9d18265d.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.65 | donor_blend | e364_existing | 6.670080 | 0.000257 | 0.000122 | 0.002357 | 0.000385 | -0.041721 | 0.025454 | -0.021477 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_65_0432e2d5.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.50 | donor_blend | e364_existing | 6.647958 | 0.000265 | 0.000162 | 0.001225 | 0.000333 | -0.046490 | 0.052587 | -0.015808 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_50_90363a99.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.50 | donor_blend | e364_existing | 6.632859 | 0.000250 | 0.000150 | 0.000843 | 0.000337 | -0.061276 | 0.041259 | -0.020794 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_50_5a835e8b.csv |
| e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185 | donor_graft | e364_existing | 6.600712 | 0.000256 | 0.000130 | 0.004126 | 0.000158 | -0.095504 | 0.058173 | -0.039179 | False | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185_1b400a58.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | e364_existing | 6.595575 | 0.000243 | 0.000142 | 0.003292 | 0.000355 | -0.071979 | 0.005625 | -0.016511 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_0087bcd7.csv |
| e367_null_validboost_baddamp_random_validity | null_public_rowmask_gate | e367_generated | 6.584220 | 0.000240 | 0.000103 | 0.001406 | 0.000454 | -0.024589 | -0.021965 | -0.018762 | True | analysis_outputs/submission_e367_publicrowmask_e367_null_validboost_baddamp_random_validity_f634f0b3.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.35 | donor_blend | e364_existing | 6.562562 | 0.000275 | 0.000155 | 0.001365 | 0.000409 | -0.074532 | 0.050438 | -0.029609 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_35_3a053152.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.50 | donor_blend | e364_existing | 6.543750 | 0.000265 | 0.000136 | 0.002993 | 0.000427 | -0.054412 | 0.034675 | -0.027168 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_50_79e0b113.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.35 | donor_blend | e364_existing | 6.510303 | 0.000286 | 0.000161 | 0.002152 | 0.000410 | -0.064578 | 0.058769 | -0.025197 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_35_421edebd.csv |
| e367_null_source_switch_random_validity | null_public_rowmask_gate | e367_generated | 6.509932 | 0.000246 | 0.000119 | 0.001919 | 0.000459 | -0.034458 | -0.010741 | -0.026583 | True | analysis_outputs/submission_e367_publicrowmask_e367_null_source_switch_random_validity_9c61acf7.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.25 | donor_blend | e364_existing | 6.477939 | 0.000286 | 0.000168 | 0.002274 | 0.000460 | -0.083717 | 0.056798 | -0.036910 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_25_25efe1f8.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.50 | donor_blend | e364_existing | 6.473360 | 0.000261 | 0.000154 | 0.003713 | 0.000411 | -0.080339 | 0.021403 | -0.022873 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_50_44b92316.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | e364_existing | 6.465099 | 0.000276 | 0.000157 | 0.001893 | 0.000407 | -0.088123 | 0.051063 | -0.026743 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_3c6c1204.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.35 | donor_blend | e364_existing | 6.443533 | 0.000285 | 0.000138 | 0.003629 | 0.000470 | -0.068468 | 0.044889 | -0.034278 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_35_7293d7e5.csv |
| e362_graft_donor_q2q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 6.433571 | 0.000254 | 0.000130 | 0.003790 | 0.000189 | -0.099346 | 0.065587 | -0.039918 | False | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11_9d0a49a1.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | e364_existing | 6.391770 | 0.000259 | 0.000162 | 0.000919 | 0.000344 | -0.071262 | 0.030172 | -0.058725 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_931f0560.csv |
| e367_direct_validboost_baddamp_amp0.97 | diagnostic_direct_public_rowmask_gate | e367_generated | 6.345545 | 0.000199 | 0.000082 | 0.002349 | 0.000469 | -0.002355 | -0.049437 | -0.008282 | True | analysis_outputs/submission_e367_publicrowmask_e367_direct_validboost_baddamp_amp0_97_05227c33.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.65 | donor_blend | e364_existing | 6.338769 | 0.000247 | 0.000119 | 0.000075 | 0.000249 | -0.001320 | 0.021213 | -0.007064 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_65_2b01442d.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.50 | donor_blend | e364_existing | 6.327568 | 0.000279 | 0.000161 | 0.001303 | 0.000392 | -0.079606 | 0.040039 | -0.059456 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_50_dd10e72d.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.25 | donor_blend | e364_existing | 6.320823 | 0.000294 | 0.000170 | 0.002998 | 0.000461 | -0.076807 | 0.062949 | -0.031178 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_25_350bc1d0.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.50 | donor_blend | e364_existing | 6.293410 | 0.000262 | 0.000137 | 0.000411 | 0.000313 | -0.024072 | 0.032388 | -0.015973 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_50_140b3162.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.50 | donor_blend | e364_existing | 6.290687 | 0.000288 | 0.000163 | 0.002636 | 0.000449 | -0.092659 | 0.056209 | -0.033095 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_50_903cca10.csv |
| e367_direct_validboost_baddamp_amp1.00 | diagnostic_direct_public_rowmask_gate | e367_generated | 6.276887 | 0.000202 | 0.000080 | 0.002421 | 0.000469 | -0.002355 | -0.049437 | -0.008282 | True | analysis_outputs/submission_e367_publicrowmask_e367_direct_validboost_baddamp_amp1_00_08739715.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.35 | donor_blend | e364_existing | 6.266337 | 0.000285 | 0.000158 | 0.004133 | 0.000465 | -0.088669 | 0.037128 | -0.031099 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_35_11e2d005.csv |

## Decision

| decision | variant | family | candidate_origin | selected_uploadsafe_file | scenario_count | rowmask_predictive_ok | rowmask_stable_ok | rowmask_stability_min | e365_top1_rate | best_real_top1_rate | best_null_top1_rate | e365_top10_rate | best_real_top10_rate | best_null_top10_rate | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reject_e367_rowmask_not_lifestyle_predictive_keep_e365 | e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | analysis_outputs/submission_e365_jackknife_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv | 98 | False | True | 0.827446 | 0.010204 | 0.000000 | 0.908163 | 0.775510 | 0.938776 | 0.989796 | The public row-mask target is not predicted by lifestyle/story context beyond permutation nulls; it is not yet a human/social latent. |

## Interpretation

- If lifestyle features cannot predict the public row-mask target, the target is an output-space artifact rather than a human/social latent.
- If a leave-public mask changes the row target too much, the public/private subset identity target is too scarce to generate submissions.
- If null row masks beat learned row masks, row placement is still a shortcut.
- Only a learned row-mask candidate that beats nulls and E365 should become a submission.

## Files

- `analysis_outputs/e367_public_rowmask_validity_rows.csv`
- `analysis_outputs/e367_public_rowmask_validity_known.csv`
- `analysis_outputs/e367_public_rowmask_validity_diagnostics.csv`
- `analysis_outputs/e367_public_rowmask_validity_stability.csv`
- `analysis_outputs/e367_public_rowmask_validity_candidates.csv`
- `analysis_outputs/e367_public_rowmask_validity_scores.csv`
- `analysis_outputs/e367_public_rowmask_validity_scenarios.csv`
- `analysis_outputs/e367_public_rowmask_validity_support.csv`
- `analysis_outputs/e367_public_rowmask_validity_selection.csv`
