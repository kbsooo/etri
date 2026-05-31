# E357 Public-Survival Contrast Latent

## Question

Do known public observations see the E351/E356 compact lifestyle-state probes as E247-preserving and public-bad-axis avoiding?

## Method

- Anchor: E247 public-best submission.
- Context representation: logit-space movement anatomy relative to E247 plus projections onto known public-good/bad movement axes.
- Target representation: fixed known public delta versus E247.
- Anti-collapse: leave-one-public-file-out prediction plus permutation Spearman check.  This is a sensor, not an optimizer.

## Decision

- decision: `select_existing_publicsurvival_probe`
- selected/ranked file: `analysis_outputs/submission_e350_compactplateau_compact_t45_s1_000_s3a1_00_ce85e5c5.csv`
- selected upload-safe file: `analysis_outputs/submission_e357_publicsurvival_selected_compact_t45_s1_000_s3a1_00_a08a4957_uploadsafe.csv`
- selected variant: `compact_t45_s1.000_s3a1.00`
- E351 E357 rank: `70`
- E356 E357 rank: `50`
- reason: A different existing compact-basin point best balances public-survival contrast, E352 stability, and E356 transfer-latent support.

## Known Public Anchors

| basename | public_lb | delta_vs_e247 | cell_l1 | share_Q1 | share_Q2 | share_Q3 | share_S1 | share_S2 | share_S3 | share_S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.000121618 | 0.949893339 | 0.000000000 | 0.000000000 | 1.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000132380 | 15.677961133 | 0.052580068 | 0.000000000 | 0.469199580 | 0.000000000 | 0.030223065 | 0.034332557 | 0.413664730 |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.000141417 | 16.216321952 | 0.050834478 | 0.002134276 | 0.453622763 | 0.000000000 | 0.029219698 | 0.064257186 | 0.399931599 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000147691 | 25.169198999 | 0.032752265 | 0.005500390 | 0.292265669 | 0.154626257 | 0.155588112 | 0.101594446 | 0.257672863 |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.000152882 | 16.592950542 | 0.057548942 | 0.014198792 | 0.445405471 | 0.013942978 | 0.035641892 | 0.043575358 | 0.389686566 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.000170548 | 3.375416139 | 0.000000000 | 0.000000000 | 0.855411481 | 0.000000000 | 0.000000000 | 0.000000000 | 0.144588519 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.000248828 | 27.982368332 | 0.090237172 | 0.033702584 | 0.267518013 | 0.134013217 | 0.178155973 | 0.044198883 | 0.252174159 |
| submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.000876552 | 44.448144216 | 0.258564395 | 0.000000001 | 0.000000001 | 0.263324602 | 0.000000001 | 0.478110999 | 0.000000001 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.001127559 | 36.225392867 | 0.000000000 | 0.000000000 | 0.183827960 | 0.000000000 | 0.645901969 | 0.000000000 | 0.170270072 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.001786026 | 113.371748406 | 0.162982041 | 0.057989246 | 0.188673357 | 0.129639621 | 0.133689709 | 0.181803372 | 0.145222654 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.002144416 | 199.288866708 | 0.181065224 | 0.029429392 | 0.225774193 | 0.112329030 | 0.125443583 | 0.172948587 | 0.153009991 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.002268403 | 273.224143466 | 0.189352104 | 0.082406474 | 0.147293967 | 0.101438663 | 0.147498085 | 0.171689234 | 0.160321473 |

## LOO Diagnostics

| model | known_rows | feature_count | loo_spearman | loo_mae | perm_spearman_mean | perm_spearman_p95 | beats_perm_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| extratrees | 13 | 123 | 0.829670330 | 0.000215734 |  |  | False |
| ridge_10 | 13 | 123 | 0.659340659 | 0.001019057 | 0.021565934 | 0.621703297 | True |
| ridge_1 | 13 | 123 | 0.620879121 | 0.001045553 | 0.021565934 | 0.379395604 | True |
| knn3 | 13 | 123 | 0.472527473 | 0.000368869 | -0.072802198 | 0.447527473 | True |

## Top Compact-Basin Candidates

| variant | selection_role | e357_public_survival_score | e247_preservation_score | pred_public_loss_mean | pred_public_loss_std | public_bad_positive_projection_sum | cell_l1 | pred_delta_vs_current_p90 | e356_survival_score | e356_top3_rate | e352_top3_rate | e355_top3_rate | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| compact_t85_s1.005_s3a0.00 | e351_compat_pool | 2.135359116 | 0.734806630 | 0.000185878 | 0.000077827 | 0.001838674 | 4.625135520 | -0.000050174 | 1.293470483 | 0.000000000 | 0.052772809 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_005_s3a0_00_68311340.csv |
| compact_t75_s1.005_s3a0.00 | e351_compat_pool | 1.994889503 | 0.723756906 | 0.000190113 | 0.000083133 | 0.001838499 | 4.624345976 | -0.000050174 | 0.663342278 | 0.000000000 | 0.014311270 | 0.250000000 | analysis_outputs/submission_e350_compactplateau_compact_t75_s1_005_s3a0_00_50b9e54f.csv |
| compact_t70_s1.005_s3a0.00 | e351_compat_pool | 1.925046041 | 0.694290976 | 0.000191708 | 0.000084564 | 0.001838559 | 4.623911138 | -0.000050173 | 0.902623733 | 0.000000000 | 0.031305903 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t70_s1_005_s3a0_00_f3c4a624.csv |
| compact_t65_s1.005_s3a0.00 | e351_compat_pool | 1.908149171 | 0.729281768 | 0.000190796 | 0.000085520 | 0.001838049 | 4.623216500 | -0.000050161 | 0.329479726 | 0.000000000 | 0.000894454 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t65_s1_005_s3a0_00_2d7cace0.csv |
| compact_t45_s1.005_s3a0.00 | e351_compat_pool | 1.849815838 | 0.786372007 | 0.000190235 | 0.000097622 | 0.001836564 | 4.615746030 | -0.000050135 | 1.236270125 | 0.000000000 | 0.032200358 | 0.250000000 | analysis_outputs/submission_e350_compactplateau_compact_t45_s1_005_s3a0_00_f20d5420.csv |
| compact_t50_s1.005_s3a0.00 | e351_compat_pool | 1.820395948 | 0.797421731 | 0.000188389 | 0.000095759 | 0.001835998 | 4.618385650 | -0.000050124 | 0.377396392 | 0.000000000 | 0.000894454 | 0.500000000 | analysis_outputs/submission_e350_compactplateau_compact_t50_s1_005_s3a0_00_c20d8244.csv |
| compact_t80_s1.005_s3a0.00 | e351_compat_pool | 1.802670350 | 0.721915285 | 0.000188106 | 0.000079695 | 0.001838832 | 4.624891860 | -0.000050178 | 0.120833333 | 0.000000000 | 0.000000000 | 0.250000000 | analysis_outputs/submission_e350_compactplateau_compact_t80_s1_005_s3a0_00_9de66f2c.csv |
| compact_t35_s1.005_s3a0.00 | e351_compat_pool | 1.802578269 | 0.786372007 | 0.000191777 | 0.000098360 | 0.001835841 | 4.609546086 | -0.000050170 | 0.861680083 | 0.000000000 | 0.021466905 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t35_s1_005_s3a0_00_3f726b13.csv |
| compact_t40_s1.005_s3a0.00 | e351_compat_pool | 1.802348066 | 0.779005525 | 0.000190998 | 0.000097635 | 0.001837009 | 4.613466259 | -0.000050171 | 0.504792785 | 0.000000000 | 0.001788909 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t40_s1_005_s3a0_00_a68366db.csv |
| compact_t55_s1.005_s3a0.00 | e351_compat_pool | 1.709484346 | 0.769797422 | 0.000188623 | 0.000089726 | 0.001836777 | 4.621044113 | -0.000050145 | 0.262500000 | 0.000000000 | 0.000000000 | 0.500000000 | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_005_s3a0_00_6370a1fc.csv |
| compact_t55_s1.000_s3a1.00 | e351_compat_pool | 1.682965009 | 0.709023941 | 0.000193100 | 0.000095525 | 0.001830069 | 4.631674984 | -0.000050096 | 2.006231366 | 0.000000000 | 0.136851521 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_000_s3a1_00_5e75b324.csv |
| compact_t60_s1.005_s3a0.00 | e351_compat_pool | 1.633241252 | 0.714548803 | 0.000191602 | 0.000086222 | 0.001838257 | 4.622422814 | -0.000050163 | 0.045833333 | 0.000000000 | 0.000000000 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t60_s1_005_s3a0_00_645ab38c.csv |
| compact_t85_s1.000_s3a0.00 | plateau_noncompat | 1.629097606 | 0.918968692 | 0.000185861 | 0.000077816 | 0.001829526 | 4.602124896 | -0.000050048 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_000_s3a0_00_0deabd0c.csv |
| compact_t50_s1.005_s3a0.50 | e351_compat_pool | 1.623112339 | 0.644567219 | 0.000192689 | 0.000101300 | 0.001837046 | 4.634890379 | -0.000050160 | 2.093179785 | 0.083333333 | 0.087656530 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t50_s1_005_s3a0_50_b77c409a.csv |
| compact_t90_s1.000_s3a0.00 | plateau_noncompat | 1.618968692 | 0.915285451 | 0.000185971 | 0.000076634 | 0.001829526 | 4.602124896 | -0.000050048 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t90_s1_000_s3a0_00_459441a2.csv |
| compact_t55_s1.005_s3a0.50 | e351_compat_pool | 1.613996317 | 0.605893186 | 0.000193143 | 0.000095567 | 0.001837992 | 4.637854683 | -0.000050183 | 1.613796959 | 0.000000000 | 0.075134168 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_005_s3a0_50_cd730cb4.csv |
| compact_t90_s1.005_s3a0.00 | plateau_noncompat | 1.602854512 | 0.731123389 | 0.000185988 | 0.000076645 | 0.001838674 | 4.625135520 | -0.000050174 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t90_s1_005_s3a0_00_bfcd57ce.csv |
| compact_t85_s1.005_s3a0.25 | e351_compat_pool | 1.597191529 | 0.559852670 | 0.000193315 | 0.000087316 | 0.001839373 | 4.634330728 | -0.000050191 | 0.483959451 | 0.000000000 | 0.001788909 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_005_s3a0_25_4aa4eabd.csv |
| compact_t80_s1.000_s3a0.00 | plateau_noncompat | 1.593922652 | 0.906077348 | 0.000188089 | 0.000079683 | 0.001829684 | 4.601882448 | -0.000050052 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t80_s1_000_s3a0_00_ba431521.csv |
| compact_t50_s1.005_s3a0.25 | e351_compat_pool | 1.590976059 | 0.692449355 | 0.000192695 | 0.000101306 | 0.001836522 | 4.626638015 | -0.000050142 | 0.944700358 | 0.000000000 | 0.020572451 | 0.250000000 | analysis_outputs/submission_e350_compactplateau_compact_t50_s1_005_s3a0_25_b7352888.csv |
| compact_t85_s1.005_s3a0.50 | e351_compat_pool | 1.588305709 | 0.506445672 | 0.000193310 | 0.000087306 | 0.001840071 | 4.643525935 | -0.000050207 | 0.492918903 | 0.000000000 | 0.003577818 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_005_s3a0_50_06cf3cdf.csv |
| compact_t85_s1.010_s3a0.00 | plateau_noncompat | 1.573848987 | 0.510128913 | 0.000186282 | 0.000077697 | 0.001847822 | 4.648146145 | -0.000050298 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_010_s3a0_00_c5f1e511.csv |
| compact_t90_s1.010_s3a0.00 | plateau_noncompat | 1.569613260 | 0.508287293 | 0.000186393 | 0.000076541 | 0.001847822 | 4.648146145 | -0.000050298 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t90_s1_010_s3a0_00_ecbfdad7.csv |
| compact_t40_s1.000_s3a0.50 | e351_compat_pool | 1.552117864 | 0.744014733 | 0.000193695 | 0.000101892 | 0.001830424 | 4.605151868 | -0.000050118 | 2.417541244 | 0.305555556 | 0.177101968 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t40_s1_000_s3a0_50_41a14c1d.csv |
| compact_t80_s1.010_s3a0.00 | plateau_noncompat | 1.544567219 | 0.499079190 | 0.000188510 | 0.000079554 | 0.001847980 | 4.647901272 | -0.000050302 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t80_s1_010_s3a0_00_2473ad40.csv |
| compact_t75_s1.000_s3a0.00 | plateau_noncompat | 1.542817680 | 0.906077348 | 0.000190096 | 0.000083120 | 0.001829352 | 4.601339280 | -0.000050048 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t75_s1_000_s3a0_00_5faaa401.csv |
| compact_t55_s1.005_s3a0.25 | e351_compat_pool | 1.541712707 | 0.646408840 | 0.000193151 | 0.000095576 | 0.001837384 | 4.629449398 | -0.000050164 | 0.744171139 | 0.000000000 | 0.007155635 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_005_s3a0_25_68cd3099.csv |
| compact_t75_s1.010_s3a0.00 | plateau_noncompat | 1.492173112 | 0.500920810 | 0.000190518 | 0.000082954 | 0.001847646 | 4.647352673 | -0.000050298 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t75_s1_010_s3a0_00_bc015cba.csv |
| compact_t35_s1.000_s3a0.50 | e351_compat_pool | 1.487384899 | 0.736648250 | 0.000193872 | 0.000101852 | 0.001830204 | 4.600376910 | -0.000050141 | 1.856140678 | 0.055555556 | 0.102862254 | 0.250000000 | analysis_outputs/submission_e350_compactplateau_compact_t35_s1_000_s3a0_50_f0d50be4.csv |
| compact_t55_s1.000_s3a0.00 | plateau_noncompat | 1.485819521 | 0.948434622 | 0.000188606 | 0.000089711 | 0.001827638 | 4.598053844 | -0.000050020 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_000_s3a0_00_122aaee6.csv |
| compact_t40_s1.005_s3a0.50 | e351_compat_pool | 1.463259669 | 0.541436464 | 0.000193712 | 0.000101907 | 0.001839563 | 4.628104436 | -0.000050243 | 1.418567382 | 0.000000000 | 0.041144902 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t40_s1_005_s3a0_50_94fc5e67.csv |
| e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe | external_selected | 1.452117864 | 0.909760589 | 0.000190779 | 0.000085506 | 0.001828904 | 4.600215423 |  |  |  |  |  | analysis_outputs/submission_e349_lifestate_ablate_selected_cell_abs_top65_q1q2q3s1_93c55c92_uploadsafe.csv |
| compact_t70_s1.000_s3a0.00 | plateau_noncompat | 1.442173112 | 0.876611418 | 0.000191690 | 0.000084551 | 0.001829411 | 4.600906605 | -0.000050048 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t70_s1_000_s3a0_00_4087785a.csv |
| compact_t65_s1.010_s3a0.00 | plateau_noncompat | 1.441068140 | 0.506445672 | 0.000191201 | 0.000085312 | 0.001847193 | 4.646217577 | -0.000050285 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t65_s1_010_s3a0_00_352bfae7.csv |
| compact_t55_s1.010_s3a0.00 | plateau_noncompat | 1.439226519 | 0.546961326 | 0.000189392 | 0.000089184 | 0.001845915 | 4.644034382 | -0.000050269 |  |  |  |  | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_010_s3a0_00_d7a95aee.csv |

## Interpretation

E357 selects a different existing point in the compact lifestyle-state basin.
The selected point is not a new blend: it asks whether removing the tiny `1.005` amplification while keeping the full S3-tail view is a better public-survival compromise than E351/E356.
This is an information-rich probe because it directly tests the S3-tail versus micro-amplification tradeoff exposed by E350-E357.

## Files

- `analysis_outputs/e357_public_survival_contrast_known.csv`
- `analysis_outputs/e357_public_survival_contrast_loocv.csv`
- `analysis_outputs/e357_public_survival_contrast_pool.csv`
- `analysis_outputs/e357_public_survival_contrast_selection.csv`
- `analysis_outputs/e357_public_survival_contrast_report.md`
