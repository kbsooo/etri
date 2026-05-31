# E358 Row-State Public-Survival Audit

## Question

Does the E357 compact-basin choice still look valid when candidate movement is projected onto row-level hidden lifestyle states rather than only output-space movement anatomy?

## Method

- Row state: E328 own-latent lifestyle state over the 250 test days.
- Human semantics: top E268 story axes most aligned with E328 bad-vs-good cluster markers.
- Context representation: how much each candidate's logit movement lands on ownlife clusters, high-energy rows, E323-heavy row-state clusters, E247-only row-state clusters, and human/social story tails.
- Target representation: known public delta versus E247.
- Anti-collapse: leave-one-public-file-out regressors plus permutation checks.

## Inputs

- base row-state columns: `19`
- selected story columns: `28`
- known local public files: `13`
- compact candidate pool: `181`

## LOO Diagnostics

| model | known_rows | feature_count | loo_spearman | loo_mae | perm_spearman_mean | perm_spearman_p95 | beats_perm_p95 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| extratrees | 13 | 120 | 0.873626374 | 0.000269659 |  |  | False |
| knn3 | 13 | 120 | 0.692307692 | 0.000357425 | 0.020260989 | 0.577747253 | True |
| ridge_10 | 13 | 120 | 0.494505495 | 0.000607586 | 0.025618132 | 0.460164835 | True |
| ridge_1 | 13 | 120 | 0.483516484 | 0.000837419 | -0.087843407 | 0.401373626 | True |

## Known Public Row-State Exposure

| basename | public_lb | delta_vs_e247 | cell_l1 | rowstate_bad_exposure | rowstate_good_exposure | rowstate_bad_minus_good_exposure |
| --- | --- | --- | --- | --- | --- | --- |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.000121618 | 0.949893339 | 0.215767603 | 0.071009817 | 0.144757786 |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000132380 | 15.677961133 | 0.215888645 | 0.050642525 | 0.165246120 |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.000141417 | 16.216321952 | 0.216331903 | 0.050680254 | 0.165651650 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000147691 | 25.169198999 | 0.215915305 | 0.050204831 | 0.165710474 |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.000152882 | 16.592950542 | 0.215582600 | 0.050597488 | 0.164985112 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.000170548 | 3.375416139 | 0.200594158 | 0.040119387 | 0.160474771 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.000248828 | 27.982368332 | 0.216416998 | 0.050618638 | 0.165798361 |
| submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.000876552 | 44.448144216 | 0.238326773 | 0.057325725 | 0.181001049 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.001127559 | 36.225392867 | 0.209038407 | 0.049550848 | 0.159487559 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.001786026 | 113.371748406 | 0.216177209 | 0.051964553 | 0.164212656 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.002144416 | 199.288866708 | 0.214390287 | 0.051036869 | 0.163353418 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.002268403 | 273.224143466 | 0.217953789 | 0.053779887 | 0.164173902 |

## Top Compact Candidates

| variant | selection_role | rowstate_public_survival_score | rowstate_pred_public_loss_mean | rowstate_pred_public_loss_std | rowstate_bad_minus_good_exposure | wmean_rowstate_e323_cluster_rate | wmean_rowstate_e247_cluster_rate | e357_public_survival_score | e356_survival_score | e352_top3_rate | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| compact_t45_s1.000_s3a1.00 | e351_compat_pool | 5.021639042 | 0.000956664 | 0.000461797 | 0.170344140 | 0.202347978 | 0.049671073 | 1.302854512 | 3.935716060 | 0.201252236 | analysis_outputs/submission_e350_compactplateau_compact_t45_s1_000_s3a1_00_ce85e5c5.csv |
| compact_t40_s1.000_s3a0.50 | e351_compat_pool | 4.789134438 | 0.000955707 | 0.000460786 | 0.170387690 | 0.202404294 | 0.049696120 | 1.552117864 | 2.417541244 | 0.177101968 | analysis_outputs/submission_e350_compactplateau_compact_t40_s1_000_s3a0_50_41a14c1d.csv |
| compact_t55_s1.000_s3a1.00 | e351_compat_pool | 4.700276243 | 0.000957237 | 0.000462358 | 0.170294286 | 0.202300214 | 0.049678286 | 1.682965009 | 2.006231366 | 0.136851521 | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_000_s3a1_00_5e75b324.csv |
| compact_t45_s1.005_s3a0.50 | e351_compat_pool | 4.383824432 | 0.000956974 | 0.000461976 | 0.170384582 | 0.202407480 | 0.049700313 | 1.238167587 | 4.337753429 | 0.238819320 | analysis_outputs/submission_e350_compactplateau_compact_t45_s1_005_s3a0_50_0ace76e5.csv |
| compact_t40_s1.005_s3a0.50 | e351_compat_pool | 4.239564150 | 0.000955799 | 0.000460866 | 0.170387867 | 0.202404552 | 0.049696257 | 1.463259669 | 1.418567382 | 0.041144902 | analysis_outputs/submission_e350_compactplateau_compact_t40_s1_005_s3a0_50_94fc5e67.csv |
| compact_t75_s1.005_s3a0.25 | e351_compat_pool | 4.112952732 | 0.000957333 | 0.000462244 | 0.170358371 | 0.202399729 | 0.049724826 | 1.106721915 | 3.528992745 | 0.277280859 | analysis_outputs/submission_e350_compactplateau_compact_t75_s1_005_s3a0_25_58e03127.csv |
| compact_t75_s1.005_s3a0.50 | e351_compat_pool | 3.736034377 | 0.000957109 | 0.000462087 | 0.170335509 | 0.202368964 | 0.049711724 | 1.022836096 | 1.325432320 | 0.025044723 | analysis_outputs/submission_e350_compactplateau_compact_t75_s1_005_s3a0_50_ed7a68ac.csv |
| compact_t55_s1.005_s3a0.50 | e351_compat_pool | 3.731890731 | 0.000957640 | 0.000462626 | 0.170340988 | 0.202366600 | 0.049707668 | 1.613996317 | 1.613796959 | 0.075134168 | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_005_s3a0_50_cd730cb4.csv |
| compact_t50_s1.005_s3a0.50 | e351_compat_pool | 3.705340700 | 0.000957634 | 0.000462625 | 0.170364419 | 0.202382228 | 0.049697281 | 1.623112339 | 2.093179785 | 0.087656530 | analysis_outputs/submission_e350_compactplateau_compact_t50_s1_005_s3a0_50_b77c409a.csv |
| compact_t85_s1.005_s3a0.50 | e351_compat_pool | 3.616635973 | 0.000957002 | 0.000461974 | 0.170338025 | 0.202371776 | 0.049711732 | 1.588305709 | 0.492918903 | 0.003577818 | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_005_s3a0_50_06cf3cdf.csv |
| compact_t70_s1.005_s3a0.25 | e351_compat_pool | 3.451043585 | 0.000957557 | 0.000462476 | 0.170354673 | 0.202395457 | 0.049724598 | 0.953222836 | 1.619767442 | 0.127906977 | analysis_outputs/submission_e350_compactplateau_compact_t70_s1_005_s3a0_25_edf1c1d2.csv |
| compact_t40_s1.005_s3a0.25 | e351_compat_pool | 3.323664825 | 0.000955909 | 0.000460922 | 0.170405561 | 0.202430374 | 0.049709999 | 1.376151013 | 0.385524747 | 0.006261181 | analysis_outputs/submission_e350_compactplateau_compact_t40_s1_005_s3a0_25_63515200.csv |
| compact_t80_s1.005_s3a0.25 | e351_compat_pool | 3.317449355 | 0.000957251 | 0.000462157 | 0.170360303 | 0.202401493 | 0.049724502 | 1.215331492 | 1.025842278 | 0.014311270 | analysis_outputs/submission_e350_compactplateau_compact_t80_s1_005_s3a0_25_5fe14097.csv |
| compact_t35_s1.000_s3a0.50 | e351_compat_pool | 3.285297729 | 0.000957573 | 0.000462724 | 0.170393994 | 0.202412908 | 0.049697593 | 1.487384899 | 1.856140678 | 0.102862254 | analysis_outputs/submission_e350_compactplateau_compact_t35_s1_000_s3a0_50_f0d50be4.csv |
| compact_t45_s1.005_s3a0.25 | e351_compat_pool | 3.260282382 | 0.000957082 | 0.000462025 | 0.170404707 | 0.202437089 | 0.049714864 | 1.134622468 | 1.178659809 | 0.022361360 | analysis_outputs/submission_e350_compactplateau_compact_t45_s1_005_s3a0_25_8a1a58a4.csv |
| compact_t60_s1.005_s3a0.50 | e351_compat_pool | 3.212553714 | 0.000957916 | 0.000462908 | 0.170332962 | 0.202356130 | 0.049704183 | 1.070073665 | 1.460569469 | 0.077817531 | analysis_outputs/submission_e350_compactplateau_compact_t60_s1_005_s3a0_50_7177a045.csv |
| compact_t60_s1.005_s3a0.25 | e351_compat_pool | 3.169275629 | 0.000958116 | 0.000463044 | 0.170356367 | 0.202389517 | 0.049718836 | 1.105064457 | 1.737578265 | 0.125223614 | analysis_outputs/submission_e350_compactplateau_compact_t60_s1_005_s3a0_25_de9919ff.csv |
| compact_t85_s1.005_s3a0.25 | e351_compat_pool | 3.088627993 | 0.000957231 | 0.000462136 | 0.170360764 | 0.202402358 | 0.049724781 | 1.597191529 | 0.483959451 | 0.001788909 | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_005_s3a0_25_4aa4eabd.csv |
| compact_t50_s1.005_s3a0.25 | e351_compat_pool | 2.618631062 | 0.000957793 | 0.000462724 | 0.170386941 | 0.202415431 | 0.049712704 | 1.590976059 | 0.944700358 | 0.020572451 | analysis_outputs/submission_e350_compactplateau_compact_t50_s1_005_s3a0_25_b7352888.csv |
| compact_t85_s1.005_s3a0.00 | e351_compat_pool | 2.609576427 | 0.001041097 | 0.000548836 | 0.170383593 | 0.202433061 | 0.049737883 | 2.135359116 | 1.293470483 | 0.052772809 | analysis_outputs/submission_e350_compactplateau_compact_t85_s1_005_s3a0_00_68311340.csv |
| compact_t55_s1.005_s3a0.25 | e351_compat_pool | 2.584254144 | 0.000957794 | 0.000462720 | 0.170364235 | 0.202399645 | 0.049722293 | 1.541712707 | 0.744171139 | 0.007155635 | analysis_outputs/submission_e350_compactplateau_compact_t55_s1_005_s3a0_25_68cd3099.csv |
| compact_t45_s1.005_s3a0.00 | e351_compat_pool | 2.575966851 | 0.001037582 | 0.000545342 | 0.170424901 | 0.202466800 | 0.049729464 | 1.849815838 | 1.236270125 | 0.032200358 | analysis_outputs/submission_e350_compactplateau_compact_t45_s1_005_s3a0_00_f20d5420.csv |
| compact_t70_s1.005_s3a0.00 | e351_compat_pool | 2.552946593 | 0.001039971 | 0.000547751 | 0.170378064 | 0.202427161 | 0.049737904 | 1.925046041 | 0.902623733 | 0.031305903 | analysis_outputs/submission_e350_compactplateau_compact_t70_s1_005_s3a0_00_f3c4a624.csv |
| compact_t35_s1.005_s3a0.25 | e351_compat_pool | 2.492326581 | 0.000957779 | 0.000462864 | 0.170413792 | 0.202443942 | 0.049713731 | 1.433057090 | 0.968664281 | 0.029516995 | analysis_outputs/submission_e350_compactplateau_compact_t35_s1_005_s3a0_25_aeb128bf.csv |
| compact_t35_s1.000_s3a0.25 | e351_compat_pool | 2.314149785 | 0.000957687 | 0.000462784 | 0.170413694 | 0.202443788 | 0.049713651 | 1.410036832 | 0.768761181 | 0.017889088 | analysis_outputs/submission_e350_compactplateau_compact_t35_s1_000_s3a0_25_87f24092.csv |
| compact_t35_s1.005_s3a0.00 | e351_compat_pool | 2.303560467 | 0.001036619 | 0.000544528 | 0.170433453 | 0.202474761 | 0.049729758 | 1.802578269 | 0.861680083 | 0.021466905 | analysis_outputs/submission_e350_compactplateau_compact_t35_s1_005_s3a0_00_3f726b13.csv |
| compact_t65_s1.005_s3a0.50 | e351_compat_pool | 2.285527931 | 0.000957355 | 0.000462342 | 0.170332295 | 0.202360359 | 0.049708434 | 0.774953959 | 0.125000000 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t65_s1_005_s3a0_50_2dd749ed.csv |
| compact_t70_s1.005_s3a0.50 | e351_compat_pool | 2.263581952 | 0.000957331 | 0.000462316 | 0.170331373 | 0.202363876 | 0.049711344 | 0.613720074 | 0.143750000 | 0.000000000 | analysis_outputs/submission_e350_compactplateau_compact_t70_s1_005_s3a0_50_bb89bc29.csv |
| compact_t75_s1.005_s3a0.00 | e351_compat_pool | 2.156154082 | 0.001040262 | 0.000548027 | 0.170381324 | 0.202430615 | 0.049737980 | 1.994889503 | 0.663342278 | 0.014311270 | analysis_outputs/submission_e350_compactplateau_compact_t75_s1_005_s3a0_00_50b9e54f.csv |
| compact_t40_s1.005_s3a0.00 | e351_compat_pool | 1.950813382 | 0.001036994 | 0.000544773 | 0.170423311 | 0.202456278 | 0.049723784 | 1.802348066 | 0.504792785 | 0.001788909 | analysis_outputs/submission_e350_compactplateau_compact_t40_s1_005_s3a0_00_a68366db.csv |

## Decision

| decision | variant | selected_uploadsafe_file | rowstate_public_survival_score | rowstate_pred_public_loss_mean | rowstate_bad_minus_good_exposure | e357_public_survival_score | e356_survival_score | e352_top3_rate | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_rowstate_submission | compact_t45_s1.000_s3a1.00 | none | 5.021639042 | 0.000956664 | 0.170344140 | 1.302854512 | 3.935716060 | 0.201252236 | No compact candidate passed row-state public-survival plus E352/E356/E357 gates. |

## Interpretation

- If E358 selects the same basin as E357, row-state semantics support the S3-tail/no-extra-amplification probe.
- If E358 demotes E357 but keeps E351/E356, the row-state view says output-space survival and human-day survival disagree.
- If no gated candidate survives, the compact lifestyle-state branch should be treated as a local/output-space basin, not the hidden public row-state law.

## Files

- `analysis_outputs/e358_rowstate_public_survival_known.csv`
- `analysis_outputs/e358_rowstate_public_survival_loocv.csv`
- `analysis_outputs/e358_rowstate_public_survival_loo_predictions.csv`
- `analysis_outputs/e358_rowstate_public_survival_pool.csv`
- `analysis_outputs/e358_rowstate_public_survival_selection.csv`