# H026 Public/Private Calibration-Veto HS-JEPA
## Question
H025 showed that train-counterfactual action health likes public-bad Q2/residual shortcuts. H026 asks whether a public/private calibration veto can keep the train-health signal while cutting those shortcut axes.
## Source sanity
- known public anchors ranked by H026 source score:
| file | public_lb | is_known_bad_shortcut | h026_source_score | pred_gain_top1200_sum | h024_pred_public_median | h024_bad_to_good_load_ratio |
| --- | --- | --- | --- | --- | --- | --- |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.568123483 | False | 9.777519626 | 18.463337348 | 0.568132834 | 3.659418798 |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | False | -0.971239336 | 13.939588951 | 0.576345593 | 1.670963196 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | False | -1.041729596 | 8.414446967 | 0.576333718 | 1.527615849 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | False | -1.205780342 | 10.030289076 | 0.576427454 | 1.616303971 |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | False | -1.516011373 | 5.249368794 | 0.576303169 | 1.643523843 |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | False | -1.595385048 | 4.616627218 | 0.576296616 | 1.661833042 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | True | -3.391988113 | 18.493223064 | 0.577686196 | 1.736934200 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | True | -4.368696632 | 18.510886853 | 0.577992865 | 2.080504753 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | True | -4.679053329 | 5.210791129 | 0.577267972 | 2.101231829 |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | True | -5.856040126 | 21.471037354 | 0.579560797 | 2.114903831 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | True | -7.595414361 | 19.121552948 | 0.578432968 | 3.548457330 |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | True | -9.029535817 | 21.789634916 | 0.581185812 | 2.975038483 |
## Generated variants
- generated variants: `272`
| file | source_file | top_k | alpha | veto_lambda | pred_gain_sum | public_bad_energy_mean | q2_share | pred_public_median | pred_public_p10 | pred_public_p90 | support_better_than_h012 | h026_variant_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a0p35_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 240 | 0.350000000 | 0.350000000 | 9.529811897 | 0.000001788 | 0.370833333 | 0.574388293 | 0.561070999 | 0.597525659 | 0.166666667 | 3.043687354 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a0p55_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 240 | 0.550000000 | 0.350000000 | 9.529811897 | 0.000001788 | 0.370833333 | 0.574398649 | 0.561094168 | 0.597535211 | 0.166666667 | 3.015435769 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a0p75_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 240 | 0.750000000 | 0.350000000 | 9.529811897 | 0.000001788 | 0.370833333 | 0.574405117 | 0.561113332 | 0.597543630 | 0.150000000 | 2.526167102 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a1p0_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 240 | 1.000000000 | 0.350000000 | 9.529811897 | 0.000001788 | 0.370833333 | 0.574412197 | 0.561135945 | 0.597554818 | 0.150000000 | 2.507343942 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a0p35_v0p75_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 240 | 0.350000000 | 0.750000000 | 9.384879161 | 0.000000892 | 0.366666667 | 0.574522449 | 0.560997674 | 0.598401570 | 0.166666667 | 2.412051061 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k240_a0p55_v0p75_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 240 | 0.550000000 | 0.750000000 | 9.384879161 | 0.000000892 | 0.366666667 | 0.574533049 | 0.561020609 | 0.598401743 | 0.166666667 | 2.385183243 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a0p35_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 0.350000000 | 0.350000000 | 10.887259299 | 0.000002690 | 0.287500000 | 0.574612992 | 0.561248024 | 0.599015224 | 0.150000000 | 2.302790918 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a0p55_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 0.550000000 | 0.350000000 | 10.887259299 | 0.000002690 | 0.287500000 | 0.574627205 | 0.561281543 | 0.599025622 | 0.150000000 | 2.265046491 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a0p75_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 0.750000000 | 0.350000000 | 10.887259299 | 0.000002690 | 0.287500000 | 0.574636268 | 0.561307897 | 0.599034444 | 0.150000000 | 2.241626739 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a1p0_v0p35_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 1.000000000 | 0.350000000 | 10.887259299 | 0.000002690 | 0.287500000 | 0.574646278 | 0.561337533 | 0.599046740 | 0.150000000 | 2.215291028 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_11_k400_a0p35_v2p0_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv | submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv | 400 | 0.350000000 | 2.000000000 | 14.797576808 | 0.000042522 | 0.332500000 | 0.574666274 | 0.565844468 | 0.600415851 | 0.133333333 | 2.202023188 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a0p35_v0p75_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 0.350000000 | 0.750000000 | 10.393187556 | 0.000000875 | 0.277500000 | 0.574638775 | 0.561209809 | 0.599085886 | 0.150000000 | 2.126896623 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a0p55_v0p75_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 0.550000000 | 0.750000000 | 10.393187556 | 0.000000875 | 0.277500000 | 0.574652785 | 0.561243518 | 0.599096102 | 0.150000000 | 2.089855275 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a0p75_v0p75_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 0.750000000 | 0.750000000 | 10.393187556 | 0.000000875 | 0.277500000 | 0.574662017 | 0.561270225 | 0.599104768 | 0.150000000 | 2.066039988 |
| hitl/h026_public_private_calibration_veto_jepa/submission_h026_veto_03_k400_a1p0_v0p75_h015_direct_all_a0.1_35c68bc9.csv | hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.1_35c68bc9.csv | 400 | 1.000000000 | 0.750000000 | 10.393187556 | 0.000000875 | 0.277500000 | 0.574671399 | 0.561299934 | 0.599116813 | 0.150000000 | 2.041683202 |
## H024 stress
- best public decoder in H026 pool: `geometry` alpha `100.0`, MAE `0.000773`, Spearman `0.969925`, pairwise `0.947368`
## Selected stress
- H025 row-permutation p(higher top1200 gain): `0.000000000`
- real top1200 H025 gain: `9.470154134`
- H024 public-score permutation p(lower margin): `0.898000000`
- selected predicted public margin vs H012: `0.006264810`
## Decision
- decision: `diagnostic_only_public_private_veto_not_transfer_safe`
- promoted path: `none`

Interpretation: H026 promotes only if train action-health, public-bad shortcut veto, and public/free permutation stresses agree. If it fails, the live bottleneck is a deeper public/private calibration target rather than a scalar veto on H025.
