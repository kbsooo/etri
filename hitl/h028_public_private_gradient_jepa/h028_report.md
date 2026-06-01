# H028 Public/Private Action-Gradient HS-JEPA
## Question
H012 made a large public jump, but H015-H027 mostly failed when they tried to complete posterior targets after H012. H028 asks a different JEPA question: from the context of known public interventions, can we predict the hidden public/private action-gradient for each cell?
## Known public sensors
- sensors used: `20`
| file | public_lb | delta_vs_h012 | mean_abs_logit_move | changed_cells |
| --- | --- | --- | --- | --- |
| submission_h012_public_equation_top_all_k1200_a0.7_uploadsafe.csv | 0.568123483 | 0.000000000 | 0.000000000 | 0 |
| submission_e247_featnn1_nn_smooth_sum_top34_f1ff7e86.csv | 0.576158949 | 0.008035466 | 0.325325349 | 1200 |
| submission_e256_featnn1_top50_amp_then_smooth25_a3827329.csv | 0.576280568 | 0.008157084 | 0.325868145 | 1200 |
| submission_e368_q2s1rowmask_selected_e368_q2_damp_s1_recover_amp1_06_be814361_uploadsafe.csv | 0.576290429 | 0.008166946 | 0.326557183 | 1290 |
| submission_e95_hardtail_541e3973.csv | 0.576291330 | 0.008167847 | 0.328297710 | 1375 |
| submission_e101_q2s3tail_177569bc.csv | 0.576300366 | 0.008176883 | 0.328569406 | 1389 |
| submission_mixmin_0c916bb4.csv | 0.576306641 | 0.008183157 | 0.329731332 | 1477 |
| submission_e176_abl_q2_to0p75_91e49725.csv | 0.576311831 | 0.008188348 | 0.328790035 | 1600 |
| submission_e267_humansocial_tail_balanced_2936100f.csv | 0.576329497 | 0.008206014 | 0.327139418 | 1212 |
| submission_e72_topabs50_q2s3_gate_4e48cba2.csv | 0.576407777 | 0.008284294 | 0.331771074 | 1538 |
| submission_e323_5508f966_uploadsafe.csv | 0.577035502 | 0.008912018 | 0.340518100 | 1356 |
| submission_e216_maskfam_jepa_s2_rank_e154_s0p75_eaac6709.csv | 0.577286509 | 0.009163026 | 0.341758268 | 1370 |
| submission_raw_timeline_jepa_rescue_strict_scale0p5.csv | 0.577526307 | 0.009402824 | 0.356053733 | 1749 |
| submission_hybrid_0p567_foldsafe_stage2_q1_q3_s1_s2_s3_s4.csv | 0.577944976 | 0.009821493 | 0.364120232 | 1749 |
| submission_h010_objective_s1s4_v2_uploadsafe.csv | 0.578171818 | 0.010048334 | 0.353365855 | 1302 |
| submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv | 0.578303365 | 0.010179882 | 0.370932148 | 1750 |
| submission_hybrid_0p578_logit_after_subject_final9_strict.csv | 0.578427353 | 0.010303870 | 0.386405805 | 1750 |
| submission_jepa_latent_q2_w0p45.csv | 0.579801286 | 0.011677803 | 0.387332813 | 1750 |
| submission_lejepa_targetwise_strict_best_scale0p5.csv | 0.580246819 | 0.012123336 | 0.406775778 | 1750 |
| submission_jepa_latent_residual_probe.csv | 0.581227328 | 0.013103845 | 0.413914374 | 1750 |
## Gradient fit
- selected fit: `all` alpha `100.0` with `88` features
- LOO MAE `0.001204883`, RMSE `0.001485628`, Spearman `0.440602`, pairwise `0.657895`
- permutation p(best selected LOO MAE under shuffled public deltas): `0.000000000`
| feature_set | alpha | n_features | loo_mae | loo_rmse | loo_spearman | loo_pair_acc | public_perm_p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all | 100.000000000 | 88 | 0.001204883 | 0.001485628 | 0.440601504 | 0.657894737 | 0.000000000 |
| public_routes | 100.000000000 | 61 | 0.001208298 | 0.001627965 | 0.341353383 | 0.605263158 | 1.000000000 |
| human_memory | 100.000000000 | 64 | 0.001255547 | 0.001593827 | 0.344360902 | 0.610526316 | 1.000000000 |
| identity | 0.100000000 | 40 | 0.001323602 | 0.001996376 | 0.296240602 | 0.621052632 | 1.000000000 |
| routes_no_subject | 100.000000000 | 74 | 0.001494349 | 0.002118887 | 0.515789474 | 0.710526316 | 1.000000000 |
| routes_no_subject | 1000.000000000 | 74 | 0.001569217 | 0.002327329 | -0.210526316 | 0.426315789 | 1.000000000 |
| all | 1000.000000000 | 88 | 0.001569864 | 0.002370101 | -0.210526316 | 0.426315789 | 1.000000000 |
| human_memory | 1000.000000000 | 64 | 0.001564882 | 0.002361749 | -0.266165414 | 0.384210526 | 1.000000000 |
| identity | 100.000000000 | 40 | 0.001509375 | 0.002658060 | -0.027067669 | 0.447368421 | 1.000000000 |
| public_routes | 1000.000000000 | 61 | 0.001584470 | 0.002482300 | -0.342857143 | 0.352631579 | 1.000000000 |
| routes_no_subject | 10.000000000 | 74 | 0.001491968 | 0.002894668 | 0.603007519 | 0.726315789 | 1.000000000 |
| identity | 1000.000000000 | 40 | 0.001610726 | 0.002574618 | -0.618045113 | 0.226315789 | 1.000000000 |
## Generated variants
- generated variants: `820`
| file | mode | target_subset | top_k | alpha | gradient_pred_delta_vs_h012 | pred_public_median | pred_public_p10 | pred_public_p90 | support_better_than_h012 | h028_variant_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_all_k1200_a0p36_all_3a28ff89.csv | descent | all | 1200 | 0.360000000 | -0.004909201 | 0.576388429 | 0.572259856 | 0.601884165 | 0.083333333 | 18.340677931 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_QS_quality_k800_a0p36_all_754382e7.csv | descent | QS_quality | 800 | 0.360000000 | -0.003438338 | 0.575844829 | 0.570834968 | 0.604012935 | 0.083333333 | 15.067481511 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_QS_quality_k1200_a0p36_all_1f7abe90.csv | descent | QS_quality | 1200 | 0.360000000 | -0.005255311 | 0.576653200 | 0.572210144 | 0.600830309 | 0.083333333 | 14.867566530 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_all_k800_a0p36_all_00723992.csv | descent | all | 800 | 0.360000000 | -0.003054673 | 0.576356518 | 0.570928491 | 0.604759736 | 0.083333333 | 13.027752250 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_all_k1200_a0p22_all_fc5f4249.csv | descent | all | 1200 | 0.220000000 | -0.002754147 | 0.575767945 | 0.571052351 | 0.601931521 | 0.083333333 | 11.018453630 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_S_k520_a0p36_all_9d73a15d.csv | descent | S | 520 | 0.360000000 | -0.002193772 | 0.575807237 | 0.570243208 | 0.605273661 | 0.083333333 | 10.501579189 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_S_k800_a0p36_all_bd10430d.csv | descent | S | 800 | 0.360000000 | -0.003595219 | 0.576454328 | 0.571313727 | 0.602120909 | 0.083333333 | 10.258459920 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_QS_quality_k520_a0p36_all_5e99bd68.csv | descent | QS_quality | 520 | 0.360000000 | -0.002018330 | 0.575934792 | 0.570072175 | 0.606465216 | 0.083333333 | 9.677116625 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_QS_quality_k1200_a0p22_all_4119d6c3.csv | descent | QS_quality | 1200 | 0.220000000 | -0.002965659 | 0.575630676 | 0.571138831 | 0.600866524 | 0.083333333 | 9.302040115 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_all_k520_a0p36_all_2092a99d.csv | descent | all | 520 | 0.360000000 | -0.001839077 | 0.575980489 | 0.570075441 | 0.606857909 | 0.083333333 | 8.866999939 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_QS_quality_k800_a0p22_all_a75d4fbe.csv | descent | QS_quality | 800 | 0.220000000 | -0.001855286 | 0.575537531 | 0.570135576 | 0.603972782 | 0.083333333 | 8.860536904 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_S1S2S3_k520_a0p36_all_ff1d8b04.csv | descent | S1S2S3 | 520 | 0.360000000 | -0.001899940 | 0.575188456 | 0.568619951 | 0.604310365 | 0.083333333 | 8.841619276 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_all_k1600_a0p36_all_2a6b7036.csv | descent | all | 1600 | 0.360000000 | -0.006526872 | 0.578163791 | 0.573399478 | 0.599142565 | 0.083333333 | 7.775805824 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_Q2S1S3_k520_a0p36_all_1e9f7653.csv | descent | Q2S1S3 | 520 | 0.360000000 | -0.001506279 | 0.575604576 | 0.568523701 | 0.603221999 | 0.100000000 | 7.684223566 |
| hitl/h028_public_private_gradient_jepa/submission_h028_pubgrad_descent_all_k800_a0p22_all_dd510785.csv | descent | all | 800 | 0.220000000 | -0.001620824 | 0.575823578 | 0.570023615 | 0.604757883 | 0.083333333 | 7.607516161 |
## Stress
- H024 decoder in H028 pool: `geometry` alpha `100.0`, MAE `0.000772855`, Spearman `0.969925`, pairwise `0.947368`
- H025 row-permutation p(higher top1200 gain): `0.710000000`
- real H025 top1200 gain: `-2.508311740`
- H024 public-score permutation p(lower margin): `0.918000000`
- selected predicted public margin vs H012: `0.008264946`
## Decision
- decision: `diagnostic_only_public_gradient_underidentified_or_stress_unsafe`
- promoted path: `none`

Interpretation: if H028 passes, HS-JEPA has learned a public/private intervention gradient rather than a posterior-completion gate. If it fails, the current public observations are insufficient to identify a new post-H012 action field; H012 remains an isolated public-equation event.
