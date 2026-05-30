# E226 Non-Collinear Candidate Scan

## Question

After the E216 public miss and before overusing the E224 axis, which existing materialized candidates remain distinct enough to test a different hidden-world law?

## Scan Size

- evaluated files: `73`
- skipped missing references: `2`

## Main Finding

- Best independent live sensor by this scan: `submission_e166_broadsurv_s0p01_d8bfa94b.csv` with role `broad_survivor_counterworld`, score `1.686847`, cos(E224) `0.074348`, cos(E72) `0.108706`, expected focus `-0.000332077`, support `0.465747`.
- This is a sensor ranking, not a certified improvement claim. Known-public-negative lanes are penalized, and E224-neighbor files are treated as same-family amplitude tests.

## Top Independent Counter-World Sensors

| file_name | family | candidate_role | submission_sensor_score | known_public_state | public_delta_vs_e95 | cos_vs_e224 | cos_vs_e216 | cos_vs_e176 | cos_vs_e72 | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_for_e95_edge | targets_moved_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | e166 | broad_survivor_counterworld | 1.686847335 | unknown |  | 0.074348354 | 0.055998599 | 0.604828951 | 0.108705614 | -0.000332077 | 0.000713053 | 0.465746836 | 0.023369627 | 3 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e144_activeboundary_d7b4b331.csv | e144 | repaired_branch_family | 1.683335951 | unknown |  | 0.289065225 | 0.132542585 | 0.089762825 | -0.024358970 | -0.000030476 | 0.000860898 | 0.473846848 | 0.375002906 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e156_targetaxis_757546d2.csv | e156 | repaired_branch_family | 1.683077052 | unknown |  | 0.290165807 | 0.132943006 | 0.092760110 | -0.027413915 | -0.000031056 | 0.000869101 | 0.474104932 | 0.386754694 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e157_lowbodypareto_bd67930d.csv | e157 | repaired_branch_family | 1.683000895 | unknown |  | 0.297006826 | 0.133484250 | 0.090718331 | -0.027706442 | -0.000030962 | 0.000878230 | 0.473851008 | 0.400698978 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e155_bodytemp_d27e7965.csv | e155 | repaired_branch_family | 1.682771277 | unknown |  | 0.296845318 | 0.133638050 | 0.089680795 | -0.026268269 | -0.000030342 | 0.000876665 | 0.473566508 | 0.408879901 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e143_activeq2s3repair_68ca656f.csv | e143 | repaired_branch_family | 1.682595709 | unknown |  | 0.286638466 | 0.131389876 | 0.087309928 | -0.023410044 | -0.000025185 | 0.000861764 | 0.473219778 | 0.453780990 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e142_transferclip_09a92236.csv | e142 | repaired_branch_family | 1.679492558 | unknown |  | 0.274987816 | 0.126865279 | 0.087653799 | -0.026846588 | -0.000027544 | 0.000960203 | 0.467177807 | 0.414916696 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e154_s3repair_9f2e2e73.csv | e154 | repaired_branch_counterworld | 1.671770965 | unknown |  | 0.316350240 | 0.135253079 | 0.088331868 | -0.031628728 | -0.000029838 | 0.000924070 | 0.472782386 | 0.514104862 | 1 | Q1,Q3,S2,S3,S4 |

## Locally Rejected Near-Tie Sensors

| file_name | family | candidate_role | submission_sensor_score | known_public_state | public_delta_vs_e95 | cos_vs_e224 | cos_vs_e216 | cos_vs_e176 | cos_vs_e72 | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_for_e95_edge | targets_moved_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bridge_scan_candidates/submission_bridge_blend_m0p75_s1p25.csv | other | local_rejected_neartie | -1.205242361 | unknown |  | 0.071164989 | 0.027481380 | 0.022244523 | 0.684626320 | -0.000120680 | 0.003455801 | 0.490770410 | 0.351941597 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Top Live Non-Collinear Sensors

| file_name | family | candidate_role | submission_sensor_score | known_public_state | public_delta_vs_e95 | cos_vs_e224 | cos_vs_e216 | cos_vs_e176 | cos_vs_e72 | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_for_e95_edge | targets_moved_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | e166 | broad_survivor_counterworld | 1.686847335 | unknown |  | 0.074348354 | 0.055998599 | 0.604828951 | 0.108705614 | -0.000332077 | 0.000713053 | 0.465746836 | 0.023369627 | 3 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e144_activeboundary_d7b4b331.csv | e144 | repaired_branch_family | 1.683335951 | unknown |  | 0.289065225 | 0.132542585 | 0.089762825 | -0.024358970 | -0.000030476 | 0.000860898 | 0.473846848 | 0.375002906 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e156_targetaxis_757546d2.csv | e156 | repaired_branch_family | 1.683077052 | unknown |  | 0.290165807 | 0.132943006 | 0.092760110 | -0.027413915 | -0.000031056 | 0.000869101 | 0.474104932 | 0.386754694 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e157_lowbodypareto_bd67930d.csv | e157 | repaired_branch_family | 1.683000895 | unknown |  | 0.297006826 | 0.133484250 | 0.090718331 | -0.027706442 | -0.000030962 | 0.000878230 | 0.473851008 | 0.400698978 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e155_bodytemp_d27e7965.csv | e155 | repaired_branch_family | 1.682771277 | unknown |  | 0.296845318 | 0.133638050 | 0.089680795 | -0.026268269 | -0.000030342 | 0.000876665 | 0.473566508 | 0.408879901 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e143_activeq2s3repair_68ca656f.csv | e143 | repaired_branch_family | 1.682595709 | unknown |  | 0.286638466 | 0.131389876 | 0.087309928 | -0.023410044 | -0.000025185 | 0.000861764 | 0.473219778 | 0.453780990 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e142_transferclip_09a92236.csv | e142 | repaired_branch_family | 1.679492558 | unknown |  | 0.274987816 | 0.126865279 | 0.087653799 | -0.026846588 | -0.000027544 | 0.000960203 | 0.467177807 | 0.414916696 | 2 | Q1,Q3,S2,S3,S4 |
| submission_e154_s3repair_9f2e2e73.csv | e154 | repaired_branch_counterworld | 1.671770965 | unknown |  | 0.316350240 | 0.135253079 | 0.088331868 | -0.031628728 | -0.000029838 | 0.000924070 | 0.472782386 | 0.514104862 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e172_vis_pos_all_keep0p25_d90f4407.csv | e172 | broad_bad_axis_neighbor | 1.164278092 | unknown |  | 0.068566317 | 0.029440273 | 0.963210611 | 0.078968707 | -0.000112695 | 0.000238448 | 0.469133282 | 0.051749823 | 4 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e169_ctx_high_density_p50_51110c7e.csv | e169 | broad_bad_axis_neighbor | 1.159479547 | unknown |  | 0.055359074 | 0.051510418 | 0.913754203 | 0.023648294 | -0.000119080 | 0.000381174 | 0.460701782 | 0.048975175 | 4 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e169_ctx_veto_c5e806e3.csv | e169 | broad_repaired_counterworld | 1.158486031 | unknown |  | 0.055150681 | 0.051316513 | 0.918674842 | 0.018111840 | -0.000120457 | 0.000383568 | 0.459906676 | 0.048415375 | 4 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e174_ro_fc_top75_to1p0_95638e73.csv | e174 | broad_bad_axis_neighbor | 1.149251348 | unknown |  | 0.063957464 | 0.049861092 | 0.999068967 | 0.061211896 | -0.000124367 | 0.000258695 | 0.462104938 | 0.046893108 | 4 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e216_maskfam_jepa_s2_rank_e95_s0p5_4516fb93.csv | e216 | s2_bad_axis_neighbor | 1.009586191 | unknown |  | -0.002149808 | 0.989524249 | 0.037787847 | 0.025402506 | -0.000227532 | 0.003996996 | 0.473944871 | 0.384999738 | 1 | S2 |
| submission_e86_e85_consensus_a3f7c96f.csv | e86 | hardtail_parent_diagnostic | 0.985811936 | unknown |  | 0.000300553 | 0.002436981 | 0.004685774 | 0.194277680 | -0.000053163 | 0.000221328 | 0.532095690 | 0.259410418 | 2 | Q2,S1,S2,S3 |
| submission_e90_e72pareto_28925de5.csv | e90 | hardtail_parent_diagnostic | 0.980330422 | unknown |  | 0.002201607 | 0.001097877 | 0.018638427 | 0.207351434 | -0.000038273 | 0.000202082 | 0.530707906 | 0.329408836 | 2 | Q2,S1,S2,S3 |
| submission_e87_noq2_source_consensus_a85c4e39.csv | e87 | hardtail_parent_diagnostic | 0.976231378 | unknown |  | 0.001045647 | 0.003299633 | 0.019199862 | -0.205673091 | -0.000033001 | 0.000198035 | 0.527701427 | 0.342550581 | 2 | Q2,S1,S2,S3 |
| submission_e108_if_e101win_amp050_079aab57.csv | e108 | hardtail_parent_diagnostic | 0.966609971 | unknown |  | -0.001290180 | -0.000797466 | -0.026343500 | 0.201134072 | 0.000093362 | 0.000423919 | 0.536000920 | 0.248907244 | 1 | Q2,S3 |
| submission_e108_if_e101win_strict_amp038_64514c53.csv | e108 | hardtail_parent_diagnostic | 0.966609971 | unknown |  | -0.001290180 | -0.000797466 | -0.026343500 | 0.201134072 | 0.000070749 | 0.000321972 | 0.536000920 | 0.249632812 | 1 | Q2,S3 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p5_0ca3d931.csv | e216 | s2_bad_axis_neighbor | 0.958089485 | unknown |  | 0.065572345 | 0.997500845 | 0.055884289 | 0.018098168 | -0.000257716 | 0.004783952 | 0.473056070 | 0.384324401 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e84_inverse_sensor_1c74da00.csv | e84 | hardtail_parent_diagnostic | 0.953827884 | unknown |  | -0.039748737 | 0.016067177 | 0.089713745 | 0.157538307 | -0.000180634 | 0.002797143 | 0.496988797 | 0.092347788 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |

## E224-Axis Neighbors

| file_name | family | candidate_role | submission_sensor_score | known_public_state | public_delta_vs_e95 | cos_vs_e224 | cos_vs_e216 | cos_vs_e176 | cos_vs_e72 | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_for_e95_edge | targets_moved_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv | e224 | current_e224_sensor | -0.090514874 | unknown |  | 1.000000000 | 0.043542250 | 0.064385682 | 0.056401060 | -0.000653189 | 0.004094069 | 0.465789507 | 0.150551319 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e223_jepa_q3s0p75_s4closer_e154_a0p5_794b0349.csv | e223 | same_q3s4_jepa_family | -0.092263665 | unknown |  | 0.996077734 | 0.040747266 | 0.052635751 | 0.054332748 | -0.000666805 | 0.004533247 | 0.464769102 | 0.176972452 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e154_a0p5_c20eee9c.csv | e211 | same_q3s4_jepa_family | -0.246840243 | unknown |  | 0.975464053 | 0.035944464 | 0.034198536 | 0.050421343 | -0.000685115 | 0.005426827 | 0.463226350 | 0.229657247 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e154_a0p5_50e6b7ec.csv | e211 | same_q3s4_jepa_family | -0.258403446 | unknown |  | 0.971904608 | 0.035813303 | 0.031838692 | 0.050237356 | -0.000680355 | 0.005489897 | 0.463542317 | 0.231263944 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e224_e224_q3s0p625_s4toward_e95_a0p5_9c52abe2.csv | e224 | same_q3s4_jepa_family | -0.083142484 | unknown |  | 0.965656532 | 0.012461027 | 0.042509489 | 0.066512664 | -0.000621278 | 0.003461158 | 0.466427860 | 0.158284310 | 1 | Q3,S4 |
| submission_e223_jepa_q3s0p75_s4toward_e95_a0p5_55d326e5.csv | e223 | same_q3s4_jepa_family | -0.080054055 | unknown |  | 0.963286687 | 0.012569332 | 0.032385764 | 0.063269901 | -0.000635269 | 0.003912769 | 0.465282775 | 0.185757873 | 1 | Q3,S4 |
| submission_e211_jepa_q3rawcloser_q3s1p0_s4s1p0_e95_a0p5_8e3dc02d.csv | e211 | same_q3s4_jepa_family | -0.123465474 | unknown |  | 0.947998609 | 0.013121824 | 0.019309343 | 0.056625576 | -0.000647387 | 0.004753401 | 0.463062456 | 0.243040999 | 1 | Q3,S4 |
| submission_e211_jepa_q3rawtoward_q3s1p0_s4s1p0_e95_a0p5_e4e44d91.csv | e211 | same_q3s4_jepa_family | -0.134133884 | unknown |  | 0.945402141 | 0.012542203 | 0.016906362 | 0.057522327 | -0.000654330 | 0.004824911 | 0.463586825 | 0.240462280 | 1 | Q3,S4 |
| submission_e209_jepa_q3_center_c010_s4_rank_e154_s0p25_1e4591ca.csv | e209 | same_q3s4_jepa_family | 0.642719456 | unknown |  | 0.885748129 | 0.049203491 | 0.009750344 | 0.023476417 | -0.000217865 | 0.004177469 | 0.472159087 | 0.361098020 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e154_s0p75_67d1b011.csv | e210 | same_q3s4_jepa_family | 0.763546817 | unknown |  | 0.846545997 | 0.028637450 | 0.071838879 | 0.104887139 | -0.001363609 | 0.004923478 | 0.464612904 | 0.173079247 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e209_jepa_q3_center_c010_s4_rank_e95_s0p25_08289063.csv | e209 | same_q3s4_jepa_family | 0.650013359 | unknown |  | 0.845108822 | 0.008817355 | -0.018188514 | 0.035363779 | -0.000189667 | 0.003542916 | 0.474058397 | 0.414782960 | 1 | Q3,S4 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e154_s1p0_2f69729d.csv | e210 | same_q3s4_jepa_family | 0.800783729 | unknown |  | 0.827420308 | 0.031641694 | 0.072125253 | 0.107932107 | -0.001378733 | 0.004734999 | 0.466528572 | 0.171180589 | 1 | Q1,Q3,S2,S3,S4 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh1p0_e95_s0p75_35e6b0a9.csv | e210 | same_q3s4_jepa_family | 0.843790928 | unknown |  | 0.817912161 | 0.009560093 | 0.062391743 | 0.111610204 | -0.001347552 | 0.004155987 | 0.464322854 | 0.175141515 | 1 | Q3,S4 |
| submission_e210_jepa_depgate_q3_center_c010_s4_rank_closer_sh0p75_e95_s1p0_49d77d44.csv | e210 | same_q3s4_jepa_family | 0.848612411 | unknown |  | 0.803130010 | 0.011456088 | 0.061356010 | 0.114954831 | -0.001369060 | 0.003963756 | 0.466027223 | 0.172390045 | 1 | Q3,S4 |

## Known Public Anchors In Scan

| file_name | family | candidate_role | submission_sensor_score | known_public_state | public_delta_vs_e95 | cos_vs_e224 | cos_vs_e216 | cos_vs_e176 | cos_vs_e72 | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | cells_for_e95_edge | targets_moved_vs_e95 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e95_hardtail_541e3973.csv | e95 | diagnostic_only | -3.986000000 | known_e95 | 0.000000000 |  |  |  |  | 0.000000000 | 0.000000000 |  |  | -1 |  |
| submission_e101_q2s3tail_177569bc.csv | e101 | known_public_negative | -1.023390029 | known_mixmin_safe_loss | 0.000009036 | -0.001290180 | -0.000797466 | -0.026343500 | 0.201134072 | 0.000046398 | 0.000211677 | 0.536000920 | 0.250424793 | 2 | Q2,S3 |
| submission_mixmin_0c916bb4.csv | mixmin | known_public_negative | -0.277340852 | known_mixmin_safe_loss | 0.000015311 | -0.005554926 | 0.024899308 | -0.009782260 | 0.671902535 | 0.000144543 | 0.002846528 | 0.486995349 | 0.321543667 | 1 | Q2,S1,S2,S3 |
| submission_e176_abl_q2_to0p75_91e49725.csv | e176 | known_public_negative | -0.851411321 | known_bad_vs_mixmin | 0.000020501 | 0.064385682 | 0.050194929 | 1.000000000 | 0.061621732 | -0.000123384 | 0.000256636 | 0.461797607 | 0.047266828 | 4 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | e72 | known_public_negative | -1.323063020 | known_bad_vs_mixmin | 0.000116447 | 0.056401060 | 0.020603820 | 0.061621732 | 1.000000000 | -0.000869985 | 0.003473767 | 0.492205013 | 0.026932509 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | e216 | known_public_negative | -2.199594982 | known_bad_vs_mixmin | 0.000995179 | 0.043542250 | 1.000000000 | 0.050194929 | 0.020603820 | -0.000318150 | 0.006833222 | 0.473309107 | 0.448991031 | 1 | Q1,Q3,S2,S3,S4 |
| submission_frontier_cvjepa_refine_a2c8d2c8.csv | other | known_public_negative | -4.387600356 | known_bad_vs_mixmin | 0.001147991 | -0.009056733 | 0.000264040 | 0.072060661 | -0.256339104 | 0.000342931 | 0.020380179 | 0.487150323 | 0.224057231 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | hybrid | known_public_negative | -6.450081419 | known_bad_vs_mixmin | 0.001653646 | -0.015256853 | -0.004290046 | 0.085348855 | -0.230280495 | 0.000103872 | 0.031120013 | 0.492776368 | 2.182635498 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | ordinal | known_public_negative | -12.043835601 | known_bad_vs_mixmin | 0.002012035 | 0.181774394 | 0.000925882 | -0.073442390 | 0.002873472 | 0.004357625 | 0.063018044 | 0.510883112 | 0.203932489 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | hybrid | known_public_negative | -13.061946358 | known_bad_vs_mixmin | 0.002136023 | 0.039174728 | 0.008446922 | 0.055799332 | 0.305195172 | -0.011293298 | 0.070221947 | 0.521135155 | 0.061268611 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_jepa_latent_q2_w0p45.csv | jepa_latent | known_public_negative | -8.548924878 | known_bad_vs_mixmin | 0.003509956 | -0.008431853 | -0.002370937 | 0.158126325 | -0.097510787 | -0.000943508 | 0.044330824 | 0.504197760 | 0.801699978 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | lejepa | known_public_negative | -11.436816707 | known_bad_vs_mixmin | 0.003955489 | 0.128200167 | 0.029345612 | 0.018791776 | -0.122229388 | -0.002346961 | 0.060934763 | 0.463828770 | 0.146775247 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |
| submission_jepa_latent_residual_probe.csv | jepa_latent | known_public_negative | -12.793788811 | known_bad_vs_mixmin | 0.004935998 | 0.044990470 | 0.022365831 | 0.127885521 | -0.263511897 | 0.002496322 | 0.067011218 | 0.490153725 | 0.233379785 | 1 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Target Tail Anatomy For Key Branches

| file_name | target | moved_cells | expected_focus | adverse_delta | support_prob_focus_swing_weighted | top1_over_abs_expected | e222_decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e154_s3repair_9f2e2e73.csv | S4 | 34 | -0.000022780 | 0.000088632 | 0.446507150 | 0.543942472 | expected_good_but_low_support |
| submission_e154_s3repair_9f2e2e73.csv | Q1 | 70 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 | expected_good_tail_unclear |
| submission_e154_s3repair_9f2e2e73.csv | Q3 | 95 | -0.000001468 | 0.000333463 | 0.466003422 | 10.452680074 | expected_good_but_low_support |
| submission_e154_s3repair_9f2e2e73.csv | S2 | 39 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 | expected_bad_or_neutral |
| submission_e154_s3repair_9f2e2e73.csv | S3 | 56 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 | expected_bad_or_neutral |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | S1 | 250 | -0.000107340 | 0.000085758 | 0.414557261 | 0.063828642 | expected_good_but_low_support |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | Q1 | 250 | -0.000049465 | 0.000090969 | 0.479486516 | 0.115440480 | expected_good_but_low_support |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | S4 | 250 | -0.000047743 | 0.000090938 | 0.498305429 | 0.103991236 | expected_good_but_low_support |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | S2 | 250 | -0.000045531 | 0.000128561 | 0.454338803 | 0.170445586 | expected_good_but_low_support |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | S3 | 250 | -0.000036472 | 0.000062677 | 0.350508827 | 0.110182792 | expected_good_but_low_support |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | Q2 | 250 | -0.000026794 | 0.000121297 | 0.529392936 | 0.160423406 | tail_supported |
| submission_e166_broadsurv_s0p01_d8bfa94b.csv | Q3 | 250 | -0.000018732 | 0.000132853 | 0.580297993 | 0.327221356 | tail_supported |
| submission_e169_ctx_veto_c5e806e3.csv | S1 | 95 | -0.000023838 | 0.000030572 | 0.361074405 | 0.244651721 | expected_good_but_low_support |
| submission_e169_ctx_veto_c5e806e3.csv | S3 | 168 | -0.000022961 | 0.000042783 | 0.361719227 | 0.171418800 | expected_good_but_low_support |
| submission_e169_ctx_veto_c5e806e3.csv | Q2 | 165 | -0.000018847 | 0.000087469 | 0.533222074 | 0.191259074 | tail_supported |
| submission_e169_ctx_veto_c5e806e3.csv | S4 | 116 | -0.000018812 | 0.000045314 | 0.495046639 | 0.235570559 | expected_good_but_low_support |
| submission_e169_ctx_veto_c5e806e3.csv | Q1 | 121 | -0.000014340 | 0.000051763 | 0.471280950 | 0.264415349 | expected_good_but_low_support |
| submission_e169_ctx_veto_c5e806e3.csv | S2 | 122 | -0.000013954 | 0.000058772 | 0.443728661 | 0.286288311 | expected_good_but_low_support |
| submission_e169_ctx_veto_c5e806e3.csv | Q3 | 117 | -0.000007705 | 0.000066897 | 0.572054126 | 0.592038350 | expected_good_tail_unclear |
| submission_e176_abl_q2_to0p75_91e49725.csv | S3 | 168 | -0.000025110 | 0.000026473 | 0.366243850 | 0.156743472 | expected_good_but_low_support |
| submission_e176_abl_q2_to0p75_91e49725.csv | S1 | 95 | -0.000023403 | 0.000023958 | 0.358247766 | 0.249193661 | expected_good_but_low_support |
| submission_e176_abl_q2_to0p75_91e49725.csv | S4 | 116 | -0.000018136 | 0.000035283 | 0.489680190 | 0.244357400 | expected_good_but_low_support |
| submission_e176_abl_q2_to0p75_91e49725.csv | Q1 | 121 | -0.000017964 | 0.000031029 | 0.481093327 | 0.211073473 | expected_good_but_low_support |
| submission_e176_abl_q2_to0p75_91e49725.csv | Q2 | 165 | -0.000014981 | 0.000057311 | 0.536973981 | 0.224247114 | tail_supported |
| submission_e176_abl_q2_to0p75_91e49725.csv | S2 | 122 | -0.000013686 | 0.000035761 | 0.456153547 | 0.291911404 | expected_good_but_low_support |
| submission_e176_abl_q2_to0p75_91e49725.csv | Q3 | 117 | -0.000010104 | 0.000046821 | 0.593498594 | 0.451461131 | tail_supported |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | S2 | 250 | -0.000286933 | 0.006064686 | 0.475334407 | 0.497839361 | expected_good_but_low_support |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | S4 | 34 | -0.000022780 | 0.000088632 | 0.446507150 | 0.543942472 | expected_good_but_low_support |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | Q1 | 70 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 | expected_good_tail_unclear |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | Q3 | 95 | -0.000001468 | 0.000333463 | 0.466003422 | 10.452680074 | expected_good_but_low_support |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | S3 | 56 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 | expected_bad_or_neutral |
| submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv | S4 | 119 | -0.000533760 | 0.001239673 | 0.478536176 | 0.181242349 | expected_good_but_low_support |
| submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv | Q3 | 250 | -0.000113839 | 0.002352421 | 0.453648372 | 0.863839051 | expected_good_but_low_support |
| submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv | Q1 | 70 | -0.000017548 | 0.000225641 | 0.516263266 | 0.763908782 | expected_good_tail_unclear |
| submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv | S2 | 39 | 0.000001380 | 0.000155534 | 0.569334514 | 8.847437629 | expected_bad_or_neutral |
| submission_e224_e224_q3s0p625_s4closer_e154_a0p5_10aed60b.csv | S3 | 56 | 0.000010579 | 0.000120801 | 0.358352446 | 1.188791018 | expected_bad_or_neutral |

## Decision

- E216 S2 remains closed as a submission lane because the public miss is large and the scan marks S2-neighbor directions as bad-axis risk.
- E224 is not a new family; it is a capped-amplitude E211/E223 translator. If it loses worse than mixmin, the right next action is non-collinear search or a support-regularized JEPA objective.
- The raw-bridge `bridge_blend_m0p75_s1p25` file is not promoted despite good E226 shape because E52 already rejected it as a mixmin-relative near-tie, not a replacement.
- Among existing files, the repaired-branch and broad-survivor files are the only plausible already-documented counter-world sensors after removing E72-neighbors, hardtail parents, and same-Q3/S4-JEPA translators. They should be submitted only as worldview tests, not as CV-ranked successors.

## Outputs

- summary: `analysis_outputs/e226_noncollinear_candidate_scan_summary.csv`
- target tail anatomy: `analysis_outputs/e226_noncollinear_candidate_scan_targets.csv`
- skipped references: `analysis_outputs/e226_noncollinear_candidate_scan_skipped.csv`