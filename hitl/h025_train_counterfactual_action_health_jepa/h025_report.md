# H025 Train-Counterfactual Action-Health JEPA
## Question
Can HS-JEPA learn action health from train labels by generating counterfactual probability moves, then use that independent supervision to select post-H012 test actions without regressing public LB?
## Base model
| target | oof_logloss | target_rate | fold_logloss_mean | fold_logloss_max |
| --- | --- | --- | --- | --- |
| Q1 | 0.682013932 | 0.495555556 | 0.682516039 | 0.703105170 |
| Q2 | 0.691636721 | 0.562222222 | 0.692083414 | 0.769031975 |
| Q3 | 0.661034120 | 0.600000000 | 0.660548081 | 0.677697913 |
| S1 | 0.606657170 | 0.682222222 | 0.607025542 | 0.644358448 |
| S2 | 0.610014546 | 0.651111111 | 0.610625545 | 0.666400427 |
| S3 | 0.589734115 | 0.662222222 | 0.591078366 | 0.683110307 |
| S4 | 0.672372395 | 0.560000000 | 0.672119999 | 0.699168651 |
## Proposal families
| proposal | kind | group | k | subject_only | mean_train_prob | mean_test_prob |
| --- | --- | --- | --- | --- | --- | --- |
| global_prior | global | all | 24 | False | 0.602028280 | 0.601904762 |
| subject_prior | subject | all | 24 | False | 0.602236901 | 0.606992113 |
| subject_time_decay14 | time | all | 24 | False | 0.604063114 | 0.608304972 |
| subject_time_decay35 | time | all | 24 | False | 0.602962722 | 0.607718897 |
| knn_all_k16 | knn | all | 16 | False | 0.595189717 | 0.596592381 |
| knn_all_k40 | knn | all | 40 | False | 0.595656062 | 0.599910366 |
| knn_sleep_k24 | knn | sleep | 24 | False | 0.606646588 | 0.605398617 |
| knn_social_sleep_k32 | knn | social_sleep | 32 | False | 0.587950546 | 0.593151619 |
| knn_quality_k24 | knn | quality | 24 | False | 0.617458567 | 0.604548543 |
| knn_body_calendar_k32 | knn | body_calendar | 32 | False | 0.609305920 | 0.605469969 |
| subject_knn_all_k10 | knn | all | 10 | True | 0.603592983 | 0.598371852 |
| subject_knn_social_sleep_k12 | knn | social_sleep | 12 | True | 0.595256115 | 0.593678646 |
## Action-health stress
| stress | fold | n | spearman | top10_gain_mean | all_gain_mean | top10_lift | top10_good_rate | all_good_rate | family |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| row_time_fold_overall | -1.000000000 | 151200 | 0.021090879 | 0.004574032 | 0.000148274 | 0.004425758 | 0.571230159 | 0.550238095 |  |
| row_time_fold | 0.000000000 | 31920 | 0.002908810 | -0.007311332 | -0.002109751 | -0.005201581 | 0.552944862 | 0.547117794 |  |
| row_time_fold | 1.000000000 | 30576 | 0.001437480 | 0.006946832 | -0.004530227 | 0.011477060 | 0.598757358 | 0.553506018 |  |
| row_time_fold | 2.000000000 | 29568 | 0.045087491 | 0.019895290 | -0.001049560 | 0.020944850 | 0.615826852 | 0.548160173 |  |
| row_time_fold | 3.000000000 | 30576 | -0.003883485 | 0.000340102 | 0.001089101 | -0.000749000 | 0.554283846 | 0.548011512 |  |
| row_time_fold | 4.000000000 | 28560 | 0.067282980 | 0.036531818 | 0.007913569 | 0.028618250 | 0.610294118 | 0.554761905 |  |
| leave_family_out |  | 12600 | 0.240729872 | 0.048770761 | -0.007374628 | 0.056145389 | 0.557936508 | 0.454920635 | global_prior |
| leave_family_out |  | 12600 | 0.368025319 | 0.091626630 | -0.005731437 | 0.097358067 | 0.798412698 | 0.536507937 | knn_all_k16 |
| leave_family_out |  | 12600 | 0.422896329 | 0.096615280 | -0.000460420 | 0.097075700 | 0.817460317 | 0.514603175 | knn_all_k40 |
| leave_family_out |  | 12600 | 0.315639123 | 0.065870419 | -0.006922431 | 0.072792850 | 0.680158730 | 0.498730159 | knn_body_calendar_k32 |
| leave_family_out |  | 12600 | 0.319326646 | 0.091896302 | -0.003061143 | 0.094957446 | 0.758730159 | 0.537777778 | knn_quality_k24 |
| leave_family_out |  | 12600 | 0.358998712 | 0.095377458 | -0.006697336 | 0.102074794 | 0.746825397 | 0.512380952 | knn_sleep_k24 |
| leave_family_out |  | 12600 | 0.417568685 | 0.096473371 | -0.003064564 | 0.099537935 | 0.790476190 | 0.514920635 | knn_social_sleep_k32 |
| leave_family_out |  | 12600 | 0.364289776 | 0.145292115 | -0.009218720 | 0.154510836 | 0.835714286 | 0.600000000 | subject_knn_all_k10 |
| leave_family_out |  | 12600 | 0.411910229 | 0.157337541 | -0.000277829 | 0.157615369 | 0.846825397 | 0.600317460 | subject_knn_social_sleep_k12 |
| leave_family_out |  | 12600 | 0.514196419 | 0.175199602 | 0.015286361 | 0.159913241 | 0.909523810 | 0.602857143 | subject_prior |
| leave_family_out |  | 12600 | 0.419047986 | 0.184550397 | 0.012259573 | 0.172290824 | 0.886507937 | 0.618095238 | subject_time_decay14 |
| leave_family_out |  | 12600 | 0.469636479 | 0.176942262 | 0.017041861 | 0.159900401 | 0.911904762 | 0.611746032 | subject_time_decay35 |
- row/time OOF Spearman: `0.021090879`; top10 lift: `0.004425758`
## Candidate ranking
| file | resolved_path | source | changed_cells | changed_rows | pred_gain_sum_moved | pred_gain_mean_moved | pred_gain_top1200_sum | pred_gain_top1200_mean | pred_positive_rate_moved | mean_abs_delta_prob | max_abs_delta_prob | ood_abs_delta_rate | h024_pred_public_median | h024_pred_public_p10 | h024_pred_public_p90 | h024_support_better_than_h012 | h024_decoder_score | h024_bad_to_good_load_ratio | h025_score |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_jepa_latent_q2_w0p45.csv | /Users/kbsoo/Downloads/cl2/jepa/submission_jepa_latent_q2_w0p45.csv | known_public | 1750 | 250 | -4.149763817 | -0.002371294 | 20.861140501 | 0.017384284 | 0.430857143 | 0.036834694 | 0.338478693 | 0.040000000 | 0.579560797 | 0.578898099 | 0.579798328 | 0.000000000 | 0.580616094 | 2.114903831 | -20.855910693 |
| submission_jepa_latent_residual_probe.csv | /Users/kbsoo/Downloads/cl2/jepa/submission_jepa_latent_residual_probe.csv | known_public | 1750 | 250 | -4.481192577 | -0.002560681 | 20.455219182 | 0.017046016 | 0.426857143 | 0.042379911 | 0.330304756 | 0.037714286 | 0.581185812 | 0.580035852 | 0.581231263 | 0.000000000 | 0.582645469 | 2.975038483 | -20.448326248 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a1.2_a639be88.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a1.2_a639be88.csv | h023 | 1750 | 250 | -6.287183911 | -0.003592677 | 19.183437103 | 0.015986198 | 0.426857143 | 0.024759290 | 0.136062370 | 0.038285714 | 0.576030190 | 0.572247880 | 0.594504555 | 0.100000000 | 0.585482719 | 4.793406962 | -19.172893146 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a1.2_a639be88.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a1.2_a639be88.csv | h023 | 1750 | 250 | -6.287183911 | -0.003592677 | 19.183437103 | 0.015986198 | 0.426857143 | 0.024759290 | 0.136062370 | 0.038285714 | 0.576030190 | 0.572247880 | 0.594504555 | 0.100000000 | 0.585482719 | 4.793406962 | -19.172893146 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a1_415f284b.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a1_415f284b.csv | h023 | 1750 | 250 | -6.238584296 | -0.003564905 | 19.137755701 | 0.015948130 | 0.433142857 | 0.020826312 | 0.116505173 | 0.034285714 | 0.575438732 | 0.571580977 | 0.593352419 | 0.100000000 | 0.584634641 | 4.545441384 | -19.127807675 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a1_415f284b.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a1_415f284b.csv | h023 | 1750 | 250 | -6.238584296 | -0.003564905 | 19.137755701 | 0.015948130 | 0.433142857 | 0.020826312 | 0.116505173 | 0.034285714 | 0.575438732 | 0.571580977 | 0.593352419 | 0.100000000 | 0.584634641 | 4.545441384 | -19.127807675 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a0.75_63837b78.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a0.75_63837b78.csv | h023 | 1750 | 250 | -6.636975453 | -0.003792557 | 18.643794937 | 0.015536496 | 0.429142857 | 0.015808359 | 0.090235240 | 0.029714286 | 0.575014320 | 0.569108867 | 0.593357497 | 0.100000000 | 0.585012841 | 4.361431786 | -18.634329216 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a0.75_63837b78.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a0.75_63837b78.csv | h023 | 1750 | 250 | -6.636975453 | -0.003792557 | 18.643794937 | 0.015536496 | 0.429142857 | 0.015808359 | 0.090235240 | 0.029714286 | 0.575014320 | 0.569108867 | 0.593357497 | 0.100000000 | 0.585012841 | 4.361431786 | -18.634329216 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a0.6_efa7843b.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_gain_all_k1750_a0.6_efa7843b.csv | h023 | 1750 | 250 | -6.976404968 | -0.003986517 | 18.321980889 | 0.015268317 | 0.428000000 | 0.012741215 | 0.073517868 | 0.028000000 | 0.574833412 | 0.567623483 | 0.593366503 | 0.100000000 | 0.585312717 | 4.240709130 | -18.312799471 |
| hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a0.6_efa7843b.csv | /Users/kbsoo/Downloads/cl2/hitl/h023_hs_pareto_proposal_vector_jepa/submission_h023_shift_all_k1750_a0.6_efa7843b.csv | h023 | 1750 | 250 | -6.976404968 | -0.003986517 | 18.321980889 | 0.015268317 | 0.428000000 | 0.012741215 | 0.073517868 | 0.028000000 | 0.574833412 | 0.567623483 | 0.593366503 | 0.100000000 | 0.585312717 | 4.240709130 | -18.312799471 |
| hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.45_ad724a1d.csv | /Users/kbsoo/Downloads/cl2/hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.45_ad724a1d.csv | h015 | 1750 | 250 | -7.570635346 | -0.004326077 | 17.888881092 | 0.014907401 | 0.430285714 | 0.008040816 | 0.035869661 | 0.026857143 | 0.573835901 | 0.566640028 | 0.587306744 | 0.116666667 | 0.582677427 | 4.644787803 | -17.878920088 |
| hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.3_c8366e21.csv | /Users/kbsoo/Downloads/cl2/hitl/h015_public_equation_self_feedback/submission_h015_direct_all_a0.3_c8366e21.csv | h015 | 1750 | 250 | -7.742481140 | -0.004424275 | 17.641860705 | 0.014701551 | 0.429714286 | 0.005421945 | 0.025050211 | 0.016000000 | 0.573557799 | 0.564981189 | 0.587332299 | 0.116666667 | 0.582867446 | 4.297883289 | -17.632864939 |
| submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv | /Users/kbsoo/Downloads/cl2/submission_h020_joint_vector_world_combined_all_k1750_a1_uploadsafe.csv | h025_extra | 1750 | 250 | -7.960833085 | -0.004549047 | 17.443687705 | 0.014536406 | 0.423428571 | 0.015251317 | 0.123283706 | 0.029142857 |  |  |  |  |  |  | -17.442959133 |
| hitl/h020_joint_vector_world_jepa/submission_h020_combined_all_k1750_a1_4e9832a3.csv | /Users/kbsoo/Downloads/cl2/hitl/h020_joint_vector_world_jepa/submission_h020_combined_all_k1750_a1_4e9832a3.csv | h020 | 1750 | 250 | -7.960833085 | -0.004549047 | 17.443687705 | 0.014536406 | 0.423428571 | 0.015251317 | 0.123283706 | 0.029142857 | 0.574214805 | 0.569958760 | 0.588551883 | 0.100000000 | 0.582211833 | 4.298384238 | -17.434362365 |
| hitl/h020_joint_vector_world_jepa/submission_h020_gain_all_k1750_a1_4e9832a3.csv | /Users/kbsoo/Downloads/cl2/hitl/h020_joint_vector_world_jepa/submission_h020_gain_all_k1750_a1_4e9832a3.csv | h020 | 1750 | 250 | -7.960833085 | -0.004549047 | 17.443687705 | 0.014536406 | 0.423428571 | 0.015251317 | 0.123283706 | 0.029142857 | 0.574214805 | 0.569958760 | 0.588551883 | 0.100000000 | 0.582211833 | 4.298384238 | -17.434362365 |
| hitl/h020_joint_vector_world_jepa/submission_h020_shift_all_k1750_a1_4e9832a3.csv | /Users/kbsoo/Downloads/cl2/hitl/h020_joint_vector_world_jepa/submission_h020_shift_all_k1750_a1_4e9832a3.csv | h020 | 1750 | 250 | -7.960833085 | -0.004549047 | 17.443687705 | 0.014536406 | 0.423428571 | 0.015251317 | 0.123283706 | 0.029142857 | 0.574214805 | 0.569958760 | 0.588551883 | 0.100000000 | 0.582211833 | 4.298384238 | -17.434362365 |
| hitl/h020_joint_vector_world_jepa/submission_h020_move_all_k1750_a1_4e9832a3.csv | /Users/kbsoo/Downloads/cl2/hitl/h020_joint_vector_world_jepa/submission_h020_move_all_k1750_a1_4e9832a3.csv | h020 | 1750 | 250 | -7.960833085 | -0.004549047 | 17.443687705 | 0.014536406 | 0.423428571 | 0.015251317 | 0.123283706 | 0.029142857 | 0.574214805 | 0.569958760 | 0.588551883 | 0.100000000 | 0.582211833 | 4.298384238 | -17.434362365 |
| hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1750_a0.75_25ad9990.csv | /Users/kbsoo/Downloads/cl2/hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1750_a0.75_25ad9990.csv | h018 | 1750 | 250 | -7.881638284 | -0.004503793 | 17.426362292 | 0.014521969 | 0.424000000 | 0.008451065 | 0.087392489 | 0.025714286 | 0.573360128 | 0.567156306 | 0.586834419 | 0.116666667 | 0.581590936 | 3.888480716 | -17.417942474 |
| hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1750_a0.75_25ad9990.csv | /Users/kbsoo/Downloads/cl2/hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1750_a0.75_25ad9990.csv | h018 | 1750 | 250 | -7.881638284 | -0.004503793 | 17.426362292 | 0.014521969 | 0.424000000 | 0.008451065 | 0.087392489 | 0.025714286 | 0.573360128 | 0.567156306 | 0.586834419 | 0.116666667 | 0.581590936 | 3.888480716 | -17.417942474 |
| hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1750_a0.75_25ad9990.csv | /Users/kbsoo/Downloads/cl2/hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1750_a0.75_25ad9990.csv | h018 | 1750 | 250 | -7.881638284 | -0.004503793 | 17.426362292 | 0.014521969 | 0.424000000 | 0.008451065 | 0.087392489 | 0.025714286 | 0.573360128 | 0.567156306 | 0.586834419 | 0.116666667 | 0.581590936 | 3.888480716 | -17.417942474 |
- selected row-permutation p(higher top1200 gain): `0.576666667`; real top1200 sum `19.183437103`
## Decision
- decision: `diagnostic_only_action_health_not_transfer_safe`
- promoted path: `none`

Interpretation: H025 is independent action-health supervision. It promotes a submission only if train-counterfactual action health transfers across row-time folds, across proposal families, and beats row-permuted test-state controls.
