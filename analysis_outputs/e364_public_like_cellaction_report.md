# E364 Public-Like Cell-Action Calibration

## Question

E363 found many locally robust E362-neighborhood cell actions. Which of them still looks sane when viewed through fixed known-public movement axes and hidden lifestyle row-state exposure?

## Method

- Anchor: E247 public-best submission.
- Context view: output logit movement anatomy, projections onto known public-good/bad axes, and E363 row-state/story latent exposure.
- Target view: known public delta versus E247 for available public-observed submissions.
- Anti-collapse: leave-one-public-file-out public sensor; candidate replacement is allowed only if it clears E363's own local gate and does not increase bad-axis or row-state risk beyond E363-selected margins.

## Inputs

- known public rows available locally: `13`
- public-sensor feature columns: `129`
- E363 candidate rows scored: `1586`
- E363 submission-gate rows: `797`

## Public Sensor LOO

| model | known_rows | feature_count | loo_spearman | loo_mae | pred_std |
| --- | --- | --- | --- | --- | --- |
| extratrees | 13 | 129 | 0.895604396 | 0.000255617 | 0.000607816 |
| ridge_1 | 13 | 129 | 0.769230769 | 0.000975081 | 0.002801621 |
| ridge_10 | 13 | 129 | 0.686813187 | 0.000945050 | 0.002596755 |
| knn3 | 13 | 129 | 0.642857143 | 0.000367495 | 0.000585559 |

## Known Public Axis Summary

| basename | public_lb | delta_vs_e247 | available | cell_l1 | share_Q1 | share_Q2 | share_Q3 | share_S1 | share_S3 | public_bad_axis_sum | public_good_axis_sum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.000000000 | True | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.000121618 | True | 0.949893339 | 0.000000000 | 0.000000000 | 1.000000000 | 0.000000000 | 0.000000000 | 0.095521281 | 0.233868529 |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.000132380 | True | 15.677961133 | 0.052580068 | 0.000000000 | 0.469199580 | 0.000000000 | 0.034332557 | 0.795168706 | 4.752963263 |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.000141417 | True | 16.216321952 | 0.050834478 | 0.002134276 | 0.453622763 | 0.000000000 | 0.064257186 | 0.789692702 | 4.792854081 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.000147691 | True | 25.169198999 | 0.032752265 | 0.005500390 | 0.292265669 | 0.154626257 | 0.101594446 | 0.756269400 | 5.090775539 |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.000152882 | True | 16.592950542 | 0.057548942 | 0.014198792 | 0.445405471 | 0.013942978 | 0.043575358 | 0.792562992 | 4.729147244 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.000170548 | True | 3.375416139 | 0.000000000 | 0.000000000 | 0.855411481 | 0.000000000 | 0.000000000 | 1.062427622 | 0.534220345 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.000248828 | True | 27.982368332 | 0.090237172 | 0.033702584 | 0.267518013 | 0.134013217 | 0.044198883 | 0.762414889 | 4.771709513 |
| submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.000876552 | True | 44.448144216 | 0.258564395 | 0.000000001 | 0.000000001 | 0.263324602 | 0.478110999 | 2.136059820 | 0.877859326 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.001127559 | True | 36.225392867 | 0.000000000 | 0.000000000 | 0.183827960 | 0.000000000 | 0.000000000 | 1.665260566 | 4.404849355 |
|  | 0.577526307 | 0.001367358 | False |  |  |  |  |  |  | 0.000000000 | 0.000000000 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.001786026 | True | 113.371748406 | 0.162982041 | 0.057989246 | 0.188673357 | 0.129639621 | 0.181803372 | 1.972033001 | 3.949730111 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.002144416 | True | 199.288866708 | 0.181065224 | 0.029429392 | 0.225774193 | 0.112329030 | 0.172948587 | 4.493420292 | 0.019063132 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.002268403 | True | 273.224143466 | 0.189352104 | 0.082406474 | 0.147293967 | 0.101438663 | 0.171689234 | 4.295879718 | 2.437096363 |
|  | 0.579801286 | 0.003642337 | False |  |  |  |  |  |  | 0.000000000 | 0.000000000 |
|  | 0.580246819 | 0.004087870 | False |  |  |  |  |  |  | 0.000000000 | 0.000000000 |
|  | 0.581227328 | 0.005068378 | False |  |  |  |  |  |  | 0.000000000 | 0.000000000 |

## E363 Family Summary

| family | n | e363_submit | e364_score_mean | pred_public_mean | bad_axis_mean | rowstate_loss_mean |
| --- | --- | --- | --- | --- | --- | --- |
| donor_blend | 145 | 9 | 4.749012697 | 0.000200249 | 0.003136127 | 0.000542124 |
| donor_graft | 116 | 49 | 3.781407629 | 0.000204282 | 0.005688635 | 0.000513817 |
| seed | 1 | 1 | 3.648297604 | 0.000215876 | 0.005113595 | 0.000729697 |
| target_ablation | 24 | 6 | 3.378417271 | 0.000219046 | 0.003158768 | 0.000785794 |
| target_scale | 1279 | 723 | 3.069331645 | 0.000217793 | 0.004924435 | 0.000670680 |
| rowgate | 21 | 9 | 2.846161352 | 0.000222601 | 0.004663419 | 0.000778651 |

## Top E363 Public-Like Candidates

| variant | family | e364_public_like_score | e364_pred_public_delta_mean | e364_pred_public_delta_std | public_bad_axis_sum | public_bad_good_gap | rowstate_pred_public_loss_mean | rowstate_bad_minus_good_exposure | e363_robust_score | pred_delta_vs_current_p90 | e363_submission_gate | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e362_ablate_s1_only_amp1.00 | target_ablation | 5.950756620 | 0.000058309 | 0.000033881 | 0.000899428 | -0.001490704 | 0.000168089 | 0.116392734 | 0.640511500 | 0.000010388 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_00_28f4e72a.csv |
| e362_ablate_s1_only_amp1.08 | target_ablation | 5.944892812 | 0.000058653 | 0.000033580 | 0.000971383 | -0.001609960 | 0.000168310 | 0.116392734 | 0.640011256 | 0.000011113 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_08_cc145be9.csv |
| e362_ablate_s1_only_amp1.16 | target_ablation | 5.943411097 | 0.000059056 | 0.000033229 | 0.001043337 | -0.001729216 | 0.000168473 | 0.116392734 | 0.639907038 | 0.000011809 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_16_5a253895.csv |
| e362_ablate_s1_only_amp1.28 | target_ablation | 5.940132409 | 0.000059548 | 0.000032806 | 0.001151268 | -0.001908101 | 0.000168834 | 0.116392734 | 0.639714235 | 0.000012802 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_s1_only_amp1_28_e777faa5.csv |
| e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | 5.854823455 | 0.000183175 | 0.000093948 | 0.000260625 | 0.000260625 | 0.000223757 | 0.128674890 | 0.638257793 | -0.000016146 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_3de2bc86.csv |
| e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185 | donor_graft | 5.849810845 | 0.000168945 | 0.000080529 | 0.004125895 | 0.001154423 | 0.000158112 | 0.125741443 | 0.653773201 | -0.000027706 | False | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e360_e349_compact_core__learned_free_mixture_low_s3_0185_1b400a58.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | 5.848329130 | 0.000169062 | 0.000081950 | 0.000918830 | 0.000918830 | 0.000344183 | 0.132921268 | 0.637054079 | -0.000031449 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_931f0560.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.65 | donor_blend | 5.847604035 | 0.000188021 | 0.000084379 | 0.000829530 | 0.000829530 | 0.000258380 | 0.131736648 | 0.640696487 | -0.000027704 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_65_3399f779.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | 5.844419924 | 0.000175484 | 0.000081810 | 0.001395932 | 0.001395932 | 0.000444770 | 0.123080807 | 0.634631017 | -0.000031367 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_be304efd.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.50 | donor_blend | 5.798013871 | 0.000177418 | 0.000090600 | 0.001303009 | 0.001303009 | 0.000392405 | 0.133358647 | 0.633760800 | -0.000036192 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_50_dd10e72d.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.50 | donor_blend | 5.793379571 | 0.000193274 | 0.000089596 | 0.001224603 | 0.001224603 | 0.000333241 | 0.132434264 | 0.638054568 | -0.000033881 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_50_90363a99.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | 5.793158890 | 0.000175035 | 0.000087560 | 0.001745607 | 0.001745607 | 0.000486180 | 0.120835235 | 0.624349942 | -0.000031415 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_e213488e.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.65 | donor_blend | 5.786380832 | 0.000176054 | 0.000089344 | 0.000638335 | 0.000638335 | 0.000278191 | 0.129031587 | 0.597362771 | -0.000028544 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_65_9d18265d.csv |
| e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.50 | donor_blend | 5.784804540 | 0.000186251 | 0.000101698 | 0.000545249 | 0.000545249 | 0.000307955 | 0.130111838 | 0.631426323 | -0.000026083 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_50_3d505f1d.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.65 | donor_blend | 5.762358134 | 0.000195483 | 0.000079850 | 0.002357155 | 0.002357155 | 0.000385341 | 0.124019562 | 0.637397997 | -0.000035189 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_65_0432e2d5.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.50 | donor_blend | 5.746658260 | 0.000188796 | 0.000084247 | 0.002253854 | 0.002253854 | 0.000466534 | 0.125504757 | 0.628607235 | -0.000038183 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_50_515efd3f.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.50 | donor_blend | 5.737925599 | 0.000183132 | 0.000095439 | 0.000843201 | 0.000843201 | 0.000337457 | 0.130271909 | 0.595163778 | -0.000036499 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_50_5a835e8b.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | 5.731998739 | 0.000172283 | 0.000082859 | 0.003292308 | 0.003292308 | 0.000355090 | 0.124537479 | 0.644026242 | -0.000029191 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_0087bcd7.csv |
| e362_graft_donor_q2q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | 5.697509458 | 0.000163010 | 0.000072647 | 0.003789759 | 0.003789759 | 0.000189334 | 0.130608548 | 0.651652371 | -0.000031214 | False | analysis_outputs/submission_e363_cellrobust_e362_graft_donor_q2q3_e360_e349_compact_core__learned_pc_episode_s1_counter_11_9d0a49a1.csv |
| e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0.35 | donor_blend | 5.679382093 | 0.000189004 | 0.000103122 | 0.001365322 | 0.001365322 | 0.000408617 | 0.131569911 | 0.598165248 | -0.000042881 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e349_compact_core__learned_pc_episode_s1_counter_11_w0_35_3a053152.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.35 | donor_blend | 5.677269861 | 0.000199452 | 0.000095752 | 0.002151762 | 0.002151762 | 0.000409518 | 0.133143708 | 0.631791085 | -0.000038887 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_35_421edebd.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.35 | donor_blend | 5.648770492 | 0.000185966 | 0.000099446 | 0.002359256 | 0.002359256 | 0.000451263 | 0.133800164 | 0.625897575 | -0.000041339 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_35_489b55ae.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0.50 | donor_blend | 5.640195460 | 0.000199422 | 0.000085406 | 0.002993257 | 0.002993257 | 0.000426611 | 0.126092767 | 0.629305493 | -0.000039422 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_pc_episode_subjective_heav_w0_50_79e0b113.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.65 | donor_blend | 5.640037831 | 0.000186001 | 0.000099325 | 0.001893286 | 0.001893286 | 0.000406606 | 0.134368671 | 0.607159234 | -0.000040187 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_65_3c6c1204.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.50 | donor_blend | 5.638556116 | 0.000187893 | 0.000088753 | 0.002522835 | 0.002522835 | 0.000505932 | 0.123731913 | 0.608805874 | -0.000035992 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_50_c978a341.csv |
| e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.35 | donor_blend | 5.633953342 | 0.000191895 | 0.000106873 | 0.000829873 | 0.000829873 | 0.000395590 | 0.131541141 | 0.621025398 | -0.000035947 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_35_8b8fe11c.csv |
| e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0.65 | donor_blend | 5.633701135 | 0.000181980 | 0.000077740 | 0.003739499 | 0.003739499 | 0.000411471 | 0.128913236 | 0.634750868 | -0.000029578 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e351_robust_center__learned_story_nonmonotone_s1_co_w0_65_a08578d3.csv |
| e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.50 | donor_blend | 5.632124842 | 0.000180109 | 0.000091434 | 0.003712605 | 0.003712605 | 0.000410790 | 0.126930139 | 0.637439684 | -0.000035179 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e361_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_50_44b92316.csv |
| e362_ablate_q1_only_amp1.00 | target_ablation | 5.610939470 | 0.000174504 | 0.000086494 | 0.003679010 | 0.003211930 | 0.000097467 | 0.134271948 | 0.629323731 | -0.000012403 | False | analysis_outputs/submission_e363_cellrobust_e362_ablate_q1_only_amp1_00_c6299d65.csv |
| e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0.25 | donor_blend | 5.598423707 | 0.000205150 | 0.000102021 | 0.001305717 | 0.001305717 | 0.000452228 | 0.132489794 | 0.608326472 | -0.000041076 | False | analysis_outputs/submission_e363_cellrobust_e362_donorblend_e360_e356_halfs3_amp__learned_free_mixture_subjective_he_w0_25_b1369e0b.csv |

## Decision

| decision | variant | family | selected_uploadsafe_file | e364_public_like_score | e363_selected_e364_score | e364_pred_public_delta_mean | e363_selected_pred_public_delta_mean | public_bad_axis_sum | rowstate_bad_minus_good_exposure | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| select_e364_public_like_replacement | e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_counter_11 | donor_graft | analysis_outputs/submission_e364_publiclike_cellaction_selected_e362_graft_donor_q3s1_e360_e349_compact_core__learned_pc_episode_s1_co_b851baf9_uploadsafe.csv | 5.169167718 | 4.461601513 | 0.000203228 | 0.000208123 | 0.004203042 | 0.137438335 | A candidate inside the E363 basin keeps the local E363 gate and has lower known-public-like risk under movement-axis plus row-state sensors. |

## Interpretation

- If E364 keeps the E363 selected point, E363's target-scale source law is not contradicted by known public axes; the next useful experiment should seek a genuinely new row-state/action law, not a nearby public-risk rerank.
- If E364 selects another same-family point, the hidden lifestyle action appears to have a local basin but needs calibrated amplitude.
- If E364 selects a different family only by a large margin, E363's source-law preservation prior weakens and donor-graft structure becomes a credible next submission branch.

## Files

- `analysis_outputs/e364_public_like_cellaction_known.csv`
- `analysis_outputs/e364_public_like_cellaction_loocv.csv`
- `analysis_outputs/e364_public_like_cellaction_loo_predictions.csv`
- `analysis_outputs/e364_public_like_cellaction_scores.csv`
- `analysis_outputs/e364_public_like_cellaction_selection.csv`