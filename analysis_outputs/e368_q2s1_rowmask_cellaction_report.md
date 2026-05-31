# E368 Q2/S1 Row-Mask Cell-Action Latent

## Question

Can the Q2 and S1 parts of known public row-validity be translated from lifestyle/story context into a target-cell action that improves the E365 donor-graft family?

## Method

- Anchor: E247 public-best probability tensor.
- Context: E328/E358 own-lifestyle state plus human/social story axes.
- Target representation: Q2/S1 row-level public-good support minus public-bad support, built from fixed known-public observations.
- Action: preserve E365 globally, then change only Q2/S1 cells through learned row-validity masks.
- Anti-collapse: Q2/S1 predictability check, leave-public stability, direct-public diagnostic veto, and null/permuted row-mask candidate stress.

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
| public_row_validity | 0.067508 | 0.075610 | 0.180219 | False | 0.368270 | 47 |
| public_bad_row_support | 0.099054 | 0.126167 | 0.096753 | True | 0.288673 | 47 |
| public_validity_Q1 | 0.104477 | 0.091095 | 0.158534 | False | 0.378295 | 47 |
| public_validity_Q2 | 0.426940 | 0.061183 | 0.102237 | True | 0.405204 | 47 |
| public_validity_Q3 | 0.050074 | -0.039849 | 0.149478 | False | 0.391328 | 47 |
| public_validity_S1 | 0.157989 | 0.096909 | 0.102777 | True | 0.305324 | 47 |
| public_signed_gap | 0.121610 | 0.031037 | 0.090855 | True | 0.288673 | 47 |

## Leave-Public Row-Mask Stability

| index | dropped_public | public_row_validity_spearman | public_bad_row_support_spearman | public_validity_Q2_spearman | public_validity_S1_spearman |
| --- | --- | --- | --- | --- | --- |
| count | 12 | 12.000000 | 12.000000 | 12.000000 | 12.000000 |
| unique | 12 |  |  |  |  |
| top | submission_hybrid_0p578_logit_after_subject_final9_strict.csv |  |  |  |  |
| freq | 1 |  |  |  |  |
| mean |  | 0.973382 | 0.960293 | 0.935957 | 0.946723 |
| std |  | 0.055809 | 0.088502 | 0.111940 | 0.072457 |
| min |  | 0.827446 | 0.735522 | 0.692973 | 0.790552 |
| 25% |  | 0.992910 | 0.992087 | 0.945808 | 0.910362 |
| 50% |  | 0.997247 | 0.999954 | 0.997980 | 0.982386 |
| 75% |  | 0.998029 | 0.999978 | 0.998483 | 0.998719 |
| max |  | 0.998950 | 1.000000 | 0.999010 | 0.999229 |

## Inputs

- generated candidates: `52`
- combined pool: `1638`
- feature views: `all`(164), `axis`(62), `target`(60), `anatomy`(18), `bad_good`(50), `compact`(20), `rowmask`(35)

## Scenario Summary

| feature_view | scenarios | top_generated_rate | top_e365_rate | e365_rank_mean | generated_gated_mean |
| --- | --- | --- | --- | --- | --- |
| all | 14 | 1.000000 | 0.000000 | 13.071429 | 14.857143 |
| anatomy | 14 | 1.000000 | 0.000000 | 13.357143 | 15.000000 |
| axis | 14 | 1.000000 | 0.000000 | 17.000000 | 15.000000 |
| bad_good | 14 | 1.000000 | 0.000000 | 13.785714 | 15.000000 |
| compact | 14 | 1.000000 | 0.000000 | 13.714286 | 15.000000 |
| rowmask | 14 | 1.000000 | 0.000000 | 16.714286 | 14.500000 |
| target | 14 | 1.000000 | 0.000000 | 36.857143 | 15.000000 |

## Top Jackknife Support

| variant | family | candidate_origin | top1_count | top5_count | top10_count | rank_mean | score_mean | pred_mean | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e368_q2_damp_s1_recover_amp1.06 | learned_q2s1_lifestyle_cell_gate | e368_generated | 73 | 87 | 97 | 2.051020 | 7.749766 | 0.000345 | analysis_outputs/submission_e368_q2s1rowmask_e368_q2_damp_s1_recover_amp1_06_dece31af.csv |
| e368_direct_q2s1_validity_scale_amp1.06 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 19 | 89 | 98 | 3.081633 | 7.707707 | 0.000328 | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp1_06_7c3c875f.csv |
| e368_null_q2s1_validity_scale_perm_q2s1_1 | null_q2s1_cell_gate | e368_generated | 4 | 85 | 98 | 4.112245 | 7.658679 | 0.000349 | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2s1_validity_scale_perm_q2s1_1_f0400e8d.csv |
| e368_direct_q2s1_validity_scale_amp0.88 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 1 | 23 | 97 | 5.928571 | 7.588398 | 0.000329 | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp0_88_06867ecb.csv |
| e368_null_q2s1_validity_scale_swap_q2_s1 | null_q2s1_cell_gate | e368_generated | 1 | 13 | 98 | 7.653061 | 7.504361 | 0.000347 | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2s1_validity_scale_swap_q2_s1_f7e35207.csv |
| e368_direct_q2s1_validity_scale_amp1.00 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 0 | 81 | 98 | 4.867347 | 7.628522 | 0.000328 | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp1_00_c8f46dcf.csv |
| e368_q2_damp_s1_recover_amp1.00 | learned_q2s1_lifestyle_cell_gate | e368_generated | 0 | 79 | 97 | 3.295918 | 7.669309 | 0.000347 | analysis_outputs/submission_e368_q2s1rowmask_e368_q2_damp_s1_recover_amp1_00_bb59656b.csv |
| e368_direct_q2s1_validity_scale_amp0.94 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 0 | 17 | 96 | 6.897959 | 7.575413 | 0.000329 | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp0_94_8bac3ba9.csv |
| e368_q2_damp_s1_recover_amp0.94 | learned_q2s1_lifestyle_cell_gate | e368_generated | 0 | 14 | 93 | 8.938776 | 7.446536 | 0.000350 | analysis_outputs/submission_e368_q2s1rowmask_e368_q2_damp_s1_recover_amp0_94_6568372d.csv |
| e368_null_s1_source_q2_mask_swap_q2_s1 | null_q2s1_cell_gate | e368_generated | 0 | 1 | 85 | 8.865979 | 7.420848 | 0.000359 | analysis_outputs/submission_e368_q2s1rowmask_e368_null_s1_source_q2_mask_swap_q2_s1_aca0d16b.csv |
| e368_direct_q2_damp_s1_recover_amp1.06 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 0 | 1 | 17 | 10.663265 | 7.224145 | 0.000342 | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2_damp_s1_recover_amp1_06_73e701e1.csv |
| e368_null_q2s1_validity_scale_random_q2s1 | null_q2s1_cell_gate | e368_generated | 0 | 0 | 4 | 11.846939 | 7.091463 | 0.000351 | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2s1_validity_scale_random_q2s1_e033a4f9.csv |
| e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 0 | 2 | 16.388889 | 6.340206 | 0.000355 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_1198dfee.csv |
| e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 0 | 0 | 17.785714 | 6.317634 | 0.000370 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_07638e6a.csv |
| e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 0 | 0 | 19.402439 | 6.273716 | 0.000369 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_3aeb0277.csv |
| e368_null_s1_source_q2_mask_inverse_q2s1 | null_q2s1_cell_gate | e368_generated | 0 | 0 | 0 | 20.884211 | 6.232961 | 0.000351 | analysis_outputs/submission_e368_q2s1rowmask_e368_null_s1_source_q2_mask_inverse_q2s1_9f7d293d.csv |
| e368_null_q2s1_sparse_tail_perm_q2s1_0 | null_q2s1_cell_gate | e368_generated | 0 | 0 | 0 | 21.463158 | 6.188216 | 0.000348 | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2s1_sparse_tail_perm_q2s1_0_6b10a5bc.csv |
| e362_scale_g0.96_q11.08_q20.90_q30.75_s10.70 | target_scale | e364_existing | 0 | 0 | 0 | 25.698630 | 5.641519 | 0.000221 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q30_75_s10_70_b4153387.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.75_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 27.013699 | 5.591911 | 0.000220 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_75_s10_90_7376bcc9.csv |
| e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | e364_existing | 0 | 0 | 0 | 27.157895 | 5.978191 | 0.000233 | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11_1f057e41.csv |
| e368_null_q2_damp_s1_recover_inverse_q2s1 | null_q2s1_cell_gate | e368_generated | 0 | 0 | 0 | 28.885417 | 6.079690 | 0.000355 | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2_damp_s1_recover_inverse_q2s1_72e0e1b3.csv |
| e362_scale_g0.96_q11.08_q20.90_q31.00_s10.70 | target_scale | e364_existing | 0 | 0 | 0 | 29.520548 | 5.598250 | 0.000222 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q31_00_s10_70_5cfec73f.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.45_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 29.821918 | 5.576614 | 0.000219 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_45_s10_90_bda152a3.csv |
| e362_scale_g1.00_q11.08_q20.90_q31.00_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 30.824324 | 5.570553 | 0.000223 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q31_00_s10_90_bac251d6.csv |
| e362_scale_g1.00_q11.04_q20.90_q30.75_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 34.013699 | 5.509171 | 0.000220 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_04_q20_90_q30_75_s10_90_ef2f5082.csv |
| e362_scale_g0.96_q11.04_q20.90_q31.00_s10.70 | target_scale | e364_existing | 0 | 0 | 0 | 34.369863 | 5.550534 | 0.000222 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_04_q20_90_q31_00_s10_70_c6b55cd5.csv |
| e362_scale_g1.00_q11.08_q20.90_q30.45_s11.00 | target_scale | e364_existing | 0 | 0 | 0 | 34.479452 | 5.529966 | 0.000217 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_08_q20_90_q30_45_s11_00_2ffbb23b.csv |
| e362_scale_g0.96_q11.08_q20.90_q30.75_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 34.917808 | 5.498183 | 0.000219 | analysis_outputs/submission_e363_cellrobust_e362_scale_g0_96_q11_08_q20_90_q30_75_s10_90_f2243d75.csv |
| e362_scale_g1.03_q11.08_q20.90_q31.00_s11.30 | target_scale | e364_existing | 0 | 0 | 0 | 36.206897 | 5.565019 | 0.000328 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_03_q11_08_q20_90_q31_00_s11_30_58916996.csv |
| e362_scale_g1.00_q11.04_q20.90_q30.45_s10.90 | target_scale | e364_existing | 0 | 0 | 0 | 36.917808 | 5.499855 | 0.000219 | analysis_outputs/submission_e363_cellrobust_e362_scale_g1_00_q11_04_q20_90_q30_45_s10_90_4d59cd43.csv |

## Top Public-Like Scores

| variant | family | candidate_origin | e368_public_like_score | e368_pred_public_delta_mean | e368_pred_public_delta_std | public_bad_axis_sum | rowstate_pred_public_loss_mean | rowmask_wmean_pred_public_row_validity | rowmask_wmean_pred_public_bad_row_support | rowmask_corr_pred_public_row_validity | rowmask_Q2_wmean_pred_public_validity_Q2 | rowmask_S1_wmean_pred_public_validity_S1 | e363_submission_gate | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e368_q2_damp_s1_recover_amp1.06 | learned_q2s1_lifestyle_cell_gate | e368_generated | 8.357921 | 0.000197 | 0.000047 | 0.003809 | 0.000403 | 0.050740 | 0.094748 | 0.030008 | 0.256339 | 0.196656 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_q2_damp_s1_recover_amp1_06_dece31af.csv |
| e368_q2_damp_s1_recover_amp1.00 | learned_q2s1_lifestyle_cell_gate | e368_generated | 8.278455 | 0.000197 | 0.000048 | 0.003824 | 0.000408 | 0.049937 | 0.095644 | 0.030056 | 0.252868 | 0.192381 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_q2_damp_s1_recover_amp1_00_bb59656b.csv |
| e368_direct_q2s1_validity_scale_amp1.06 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 8.273602 | 0.000190 | 0.000025 | 0.004220 | 0.000407 | 0.048039 | 0.094500 | 0.030809 | 0.230080 | 0.152434 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp1_06_7c3c875f.csv |
| e368_null_q2s1_validity_scale_perm_q2s1_1 | null_q2s1_cell_gate | e368_generated | 8.238669 | 0.000199 | 0.000041 | 0.003640 | 0.000399 | 0.045209 | 0.100151 | 0.032909 | 0.217007 | 0.134472 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2s1_validity_scale_perm_q2s1_1_f0400e8d.csv |
| e368_direct_q2s1_validity_scale_amp1.00 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 8.192216 | 0.000191 | 0.000025 | 0.004207 | 0.000406 | 0.048370 | 0.094432 | 0.030553 | 0.230078 | 0.151259 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp1_00_c8f46dcf.csv |
| e368_direct_q2s1_validity_scale_amp0.88 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 8.146020 | 0.000193 | 0.000025 | 0.004188 | 0.000402 | 0.048827 | 0.094537 | 0.031257 | 0.229087 | 0.147481 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp0_88_06867ecb.csv |
| e368_direct_q2s1_validity_scale_amp0.94 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 8.138480 | 0.000192 | 0.000025 | 0.004197 | 0.000404 | 0.048597 | 0.094484 | 0.030966 | 0.229589 | 0.149397 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2s1_validity_scale_amp0_94_8bac3ba9.csv |
| e368_q2s1_validity_scale_amp0.88 | learned_q2s1_lifestyle_cell_gate | e368_generated | 8.122534 | 0.000195 | 0.000037 | 0.003714 | 0.000401 | 0.055797 | 0.094038 | 0.032921 | 0.287221 | 0.236217 | False | analysis_outputs/submission_e368_q2s1rowmask_e368_q2s1_validity_scale_amp0_88_ea4c1f3c.csv |
| e368_null_q2s1_validity_scale_swap_q2_s1 | null_q2s1_cell_gate | e368_generated | 8.086746 | 0.000200 | 0.000043 | 0.003756 | 0.000366 | 0.041536 | 0.098295 | 0.026770 | 0.210708 | 0.133316 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2s1_validity_scale_swap_q2_s1_f7e35207.csv |
| e368_q2_damp_s1_recover_amp0.94 | learned_q2s1_lifestyle_cell_gate | e368_generated | 8.061648 | 0.000198 | 0.000049 | 0.003840 | 0.000412 | 0.049123 | 0.096546 | 0.029753 | 0.249393 | 0.187698 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_q2_damp_s1_recover_amp0_94_6568372d.csv |
| e368_null_s1_source_q2_mask_swap_q2_s1 | null_q2s1_cell_gate | e368_generated | 8.048779 | 0.000211 | 0.000047 | 0.003967 | 0.000386 | 0.042725 | 0.100482 | 0.025048 | 0.205493 | 0.112839 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_null_s1_source_q2_mask_swap_q2_s1_aca0d16b.csv |
| e368_q2s1_validity_scale_amp0.94 | learned_q2s1_lifestyle_cell_gate | e368_generated | 8.026044 | 0.000195 | 0.000036 | 0.003691 | 0.000403 | 0.056003 | 0.093954 | 0.032562 | 0.290907 | 0.243103 | False | analysis_outputs/submission_e368_q2s1rowmask_e368_q2s1_validity_scale_amp0_94_a4700cd3.csv |
| e368_q2s1_validity_scale_amp1.06 | learned_q2s1_lifestyle_cell_gate | e368_generated | 8.008657 | 0.000201 | 0.000028 | 0.003657 | 0.000408 | 0.056367 | 0.093801 | 0.031965 | 0.298006 | 0.253578 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_q2s1_validity_scale_amp1_06_dfcb437e.csv |
| e368_q2s1_validity_scale_amp1.00 | learned_q2s1_lifestyle_cell_gate | e368_generated | 7.923596 | 0.000198 | 0.000032 | 0.003668 | 0.000405 | 0.056208 | 0.093870 | 0.032292 | 0.294501 | 0.249822 | False | analysis_outputs/submission_e368_q2s1rowmask_e368_q2s1_validity_scale_amp1_00_58aca6c2.csv |
| e368_direct_q2_damp_s1_recover_amp1.06 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 7.813178 | 0.000192 | 0.000044 | 0.004275 | 0.000408 | 0.047332 | 0.098884 | 0.030008 | 0.231531 | 0.131788 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2_damp_s1_recover_amp1_06_73e701e1.csv |
| e368_q2_damp_s1_recover_amp0.88 | learned_q2s1_lifestyle_cell_gate | e368_generated | 7.747662 | 0.000199 | 0.000050 | 0.003856 | 0.000417 | 0.048309 | 0.097457 | 0.029539 | 0.245945 | 0.182942 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_q2_damp_s1_recover_amp0_88_9b4d7e92.csv |
| e368_null_q2s1_validity_scale_random_q2s1 | null_q2s1_cell_gate | e368_generated | 7.708065 | 0.000207 | 0.000049 | 0.004098 | 0.000406 | 0.040329 | 0.095726 | 0.025499 | 0.208575 | 0.073631 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2s1_validity_scale_random_q2s1_e033a4f9.csv |
| e368_direct_s1_source_q2_mask_amp0.88 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 7.680647 | 0.000207 | 0.000036 | 0.004155 | 0.000416 | 0.045521 | 0.097806 | 0.027541 | 0.218933 | 0.119934 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_s1_source_q2_mask_amp0_88_5e299e4b.csv |
| e368_s1_source_q2_mask_amp0.88 | learned_q2s1_lifestyle_cell_gate | e368_generated | 7.656007 | 0.000205 | 0.000047 | 0.003919 | 0.000414 | 0.050697 | 0.096856 | 0.029955 | 0.260739 | 0.159878 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_s1_source_q2_mask_amp0_88_13c6371d.csv |
| e368_null_s1_source_q2_mask_perm_q2s1_1 | null_q2s1_cell_gate | e368_generated | 7.645079 | 0.000207 | 0.000050 | 0.003821 | 0.000415 | 0.046629 | 0.099228 | 0.029706 | 0.209998 | 0.113158 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_null_s1_source_q2_mask_perm_q2s1_1_62e214da.csv |
| e368_s1_source_q2_mask_amp0.94 | learned_q2s1_lifestyle_cell_gate | e368_generated | 7.604365 | 0.000204 | 0.000046 | 0.003907 | 0.000416 | 0.050785 | 0.096825 | 0.030100 | 0.263647 | 0.163460 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_s1_source_q2_mask_amp0_94_8689a74f.csv |
| e368_direct_q2_damp_s1_recover_amp1.00 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 7.569371 | 0.000193 | 0.000045 | 0.004265 | 0.000412 | 0.046703 | 0.099709 | 0.029344 | 0.229049 | 0.130432 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_q2_damp_s1_recover_amp1_00_1e1b2844.csv |
| e368_direct_s1_source_q2_mask_amp0.94 | diagnostic_direct_q2s1_public_cell_gate | e368_generated | 7.551123 | 0.000206 | 0.000035 | 0.004159 | 0.000418 | 0.045275 | 0.097835 | 0.027479 | 0.219396 | 0.121012 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_direct_s1_source_q2_mask_amp0_94_3580dec0.csv |
| e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185 | donor_graft | e364_existing | 7.541789 | 0.000193 | 0.000049 | 0.004126 | 0.000158 | 0.029277 | 0.140258 | -0.015043 | 0.373649 | -0.057355 | False | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185_1b400a58.csv |
| e368_s1_source_q2_mask_amp1.00 | learned_q2s1_lifestyle_cell_gate | e368_generated | 7.539206 | 0.000207 | 0.000042 | 0.003896 | 0.000418 | 0.050873 | 0.096793 | 0.030298 | 0.266503 | 0.167003 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_s1_source_q2_mask_amp1_00_1da6100e.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.25 | donor_blend | e364_existing | 7.537711 | 0.000225 | 0.000069 | 0.001604 | 0.000450 | 0.052974 | 0.114847 | 0.008985 | 0.214621 | -0.018703 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_25_e7186d4b.csv |
| e368_null_q2_damp_s1_recover_perm_q2s1_1 | null_q2s1_cell_gate | e368_generated | 7.500586 | 0.000202 | 0.000053 | 0.003874 | 0.000402 | 0.040479 | 0.105558 | 0.028079 | 0.210062 | 0.118613 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2_damp_s1_recover_perm_q2s1_1_2cac37b6.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.65 | donor_blend | e364_existing | 7.500055 | 0.000191 | 0.000050 | 0.000638 | 0.000278 | 0.061497 | 0.086478 | 0.038710 | 0.134892 | 0.059301 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_65_9d18265d.csv |
| e368_s1_source_q2_mask_amp1.06 | learned_q2s1_lifestyle_cell_gate | e368_generated | 7.499542 | 0.000207 | 0.000042 | 0.003884 | 0.000420 | 0.050960 | 0.096762 | 0.030524 | 0.269308 | 0.170506 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_s1_source_q2_mask_amp1_06_ef08de27.csv |
| e368_null_q2_damp_s1_recover_swap_q2_s1 | null_q2s1_cell_gate | e368_generated | 7.484493 | 0.000203 | 0.000054 | 0.003743 | 0.000418 | 0.044653 | 0.096209 | 0.027296 | 0.213012 | 0.118100 | True | analysis_outputs/submission_e368_q2s1rowmask_e368_null_q2_damp_s1_recover_swap_q2_s1_9d8fc10d.csv |

## Decision

| decision | variant | family | candidate_origin | selected_uploadsafe_file | scenario_count | q2_predictive_ok | s1_predictive_ok | rowmask_predictive_ok | rowmask_stable_ok | direct_public_veto | rowmask_stability_min | e365_top1_rate | best_real_top1_rate | best_null_top1_rate | e365_top10_rate | best_real_top10_rate | best_null_top10_rate | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| select_e368_q2s1_lifestyle_cell_replacement | e368_q2_damp_s1_recover_amp1.06 | learned_q2s1_lifestyle_cell_gate | e368_generated | analysis_outputs/submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 98 | True | True | True | True | False | 0.692973 | 0.000000 | 0.744898 | 0.040816 | 0.000000 | 0.989796 | 1.000000 | The learned Q2/S1 lifestyle cell gate beats E365, direct-public controls, and null masks under jackknife stress. |

## Interpretation

- If Q2 or S1 cannot be predicted from lifestyle context, the joint hidden-life-state translator is not established.
- If direct public masks beat learned masks, the row target exists but our context-to-target translator is still missing.
- If null row masks beat learned row masks, row placement is still a shortcut.
- Only a learned Q2/S1 candidate that beats direct/null controls and E365 should become a submission.

## Files

- `analysis_outputs/e368_q2s1_rowmask_cellaction_rows.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_known.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_diagnostics.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_stability.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_candidates.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_scores.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_scenarios.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_support.csv`
- `analysis_outputs/e368_q2s1_rowmask_cellaction_selection.csv`
