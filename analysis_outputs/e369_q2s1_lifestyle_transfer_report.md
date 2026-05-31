# E369 Q2/S1 Lifestyle-Transfer Audit

## Question

Does the E368 Q2/S1 cell action correspond to a hidden lifestyle state that can be learned from train labels and context views, without using public LB as the teacher?

## Construction

- Base: subject/calendar model for Q2 and S1.
- Teacher: train residual after the base model.
- Context: family, JEPA residual, social/cash/raw story bundles, and combined lifestyle views.
- Tests: masked residual student, kNN residual analogy, and cluster residual analogy.
- Null: each alignment is compared against 160 permuted test-gate/movement controls.

## Decision

| target | supporting_rows | student_support_rows | knn_support_rows | cluster_support_rows | best_abs_gate_spearman | best_abs_delta_spearman | target_decision | global_decision | reason | all_target_cos_e323_bad_vs_e365 | q2_cos_e323_bad_vs_e365 | q2_cos_e323_bad_vs_e247 | s1_cos_e323_bad_vs_e365 | target_risk_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | 64 | 5 | 24 | 35 | 0.369591524 | 0.421146983 | strong_public_free_transfer | support_e368_hidden_lifestyle_state | Q2 has independent public-free lifestyle transfer and S1 is not dead; E368 movement is not E323-like. | 0.001520053 | 0.591734547 | -0.014661258 | -0.063200462 | Q2-only movement is E323-like versus E365, but it is not E323-like versus E247 and the all-target movement is near orthogonal. |
| S1 | 42 | 5 | 18 | 19 | 0.232457868 | 0.181905879 | strong_public_free_transfer | support_e368_hidden_lifestyle_state | Q2 has independent public-free lifestyle transfer and S1 is not dead; E368 movement is not E323-like. | 0.001520053 | 0.591734547 | -0.014661258 | -0.063200462 | Q2-only movement is E323-like versus E365, but it is not E323-like versus E247 and the all-target movement is near orthogonal. |

## E368 Movement Audit

| scope | changed_rows | changed_cells | mean_abs_logit_delta | max_abs_logit_delta | signed_sum | cos_e323_bad_vs_e365 | cos_e323_bad_vs_e247 | gate_spearman | abs_gate_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all_targets | 168 | 194 | 0.000106680 | 0.021592199 | 0.051683116 | 0.001520053 | -0.024472314 |  |  |
| Q1 | 0 | 0 | 0.000000000 | 0.000000000 | -0.000000000 | 0.000024678 | 0.000024827 |  |  |
| Q2 | 34 | 34 | 0.000309659 | 0.021592199 | 0.064131358 | 0.591734547 | -0.014661258 | -0.165007771 | 0.037461311 |
| Q3 | 0 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |  |  |
| S1 | 160 | 160 | 0.000437104 | 0.011185590 | -0.012448242 | -0.063200462 | -0.075880886 | 0.190909348 | -0.065898388 |
| S2 | 0 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |  |  |
| S3 | 0 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |  |  |
| S4 | 0 | 0 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 | 0.000000000 |  |  |

Movement-risk nuance: all-target E368-vs-E365 movement is almost orthogonal to the E323 bad axis, but the Q2-only slice has a high E323 cosine versus E365. Because the same Q2 slice is not E323-like versus E247 and the move is very small, this is a monitored amplitude risk rather than a veto.

## Top Transfer Alignments

| target | view_id | split | method | score_std | gate_spearman | abs_delta_spearman | signed_delta_spearman | gate_top20_lift | abs_delta_top20_lift | base_logloss | aug_logloss | logloss_delta | teacher_r2 | teacher_spearman | gate_null_abs_p95 | abs_delta_null_abs_p95 | signed_delta_null_abs_p95 | gate_support | abs_delta_support | signed_delta_support | any_transfer_support |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | family | dateblock | knn16_train_residual | 0.131167473 | 0.217505388 | 0.138612123 | -0.069819707 | 0.064163062 | 0.000000000 |  |  |  |  |  | 0.115549240 | 0.120865991 | 0.128173759 | True | True | False | True |
| Q2 | family | dateblock | knn32_train_residual | 0.073369539 | 0.209790621 | 0.190180905 | -0.066722985 | 0.022195115 | 0.000000000 |  |  |  |  |  | 0.138711506 | 0.102802803 | 0.131554731 | True | True | False | True |
| Q2 | jepa_resid | dateblock | kmeans8_train_residual | 0.049951855 | 0.193439663 | 0.137718429 | -0.034125204 | 0.009175526 | 0.000000000 |  |  |  |  |  | 0.110108123 | 0.114050362 | 0.134188139 | True | True | False | True |
| Q2 | jepa_resid | dateblock | kmeans10_train_residual | 0.064902038 | 0.192826101 | 0.140700842 | -0.049933229 | 0.008189450 | 0.000000000 |  |  |  |  |  | 0.118417763 | 0.133918431 | 0.109997601 | True | True | False | True |
| Q2 | jepa_resid | dateblock | masked_residual_student_test | 0.105208042 | 0.189581145 | 0.150410446 | -0.050635638 | 0.010332110 | 0.000000000 | 0.715333740 | 0.708028054 | -0.007305686 | -0.110750906 | -0.088994612 | 0.111822013 | 0.115853101 | 0.114088983 | True | True | False | True |
| Q2 | family | dateblock | masked_residual_student_test | 0.143430419 | 0.188810829 | 0.164998748 | 0.007821975 | 0.003772379 | 0.000000000 | 0.715333740 | 0.722895599 | 0.007561860 | -0.127743977 | 0.012906796 | 0.130892757 | 0.128591764 | 0.123546567 | True | True | False | True |
| Q2 | family | dateblock | knn8_train_residual | 0.185220115 | 0.165710042 | 0.189978510 | -0.034284431 | 0.043519032 | 0.000000000 |  |  |  |  |  | 0.105518388 | 0.120425132 | 0.119954360 | True | True | False | True |
| Q2 | jepa_resid | subject | masked_residual_student_test | 0.117692714 | 0.159914367 | -0.130050240 | -0.038251435 | 0.043762374 | 0.000000000 | 0.765899724 | 0.735689108 | -0.030210616 | -0.195539000 | -0.234482211 | 0.114473000 | 0.108540872 | 0.115542432 | True | True | False | True |
| Q2 | raw_day | dateblock | kmeans6_train_residual | 0.035708044 | 0.135726050 | 0.134269970 | -0.192664044 | 0.003254554 | 0.000000000 |  |  |  |  |  | 0.104659102 | 0.116634465 | 0.126781144 | True | True | True | True |
| Q2 | jepa_resid | dateblock | knn8_train_residual | 0.180921075 | 0.134217521 | 0.162090333 | -0.041589187 | -0.003602481 | 0.000000000 |  |  |  |  |  | 0.119936094 | 0.108632837 | 0.116533780 | True | True | False | True |
| Q2 | raw_day | subject | knn16_train_residual | 0.138321560 | -0.143874458 | -0.207916856 | 0.027523535 | -0.013578254 | 0.000000000 |  |  |  |  |  | 0.126005439 | 0.119672386 | 0.139063260 | True | True | False | True |
| S1 | family | dateblock | knn16_train_residual | 0.105210895 | 0.145828309 | -0.124840321 | 0.005696799 | 0.021690022 | -0.018224645 |  |  |  |  |  | 0.118396705 | 0.117310773 | 0.123100949 | True | True | False | True |
| S1 | family | dateblock | knn32_train_residual | 0.074106975 | 0.144016512 | -0.150970419 | 0.070283957 | 0.019067205 | -0.010903041 |  |  |  |  |  | 0.114311525 | 0.109854827 | 0.152112236 | True | True | False | True |
| S1 | family_jepa_story | dateblock | knn8_train_residual | 0.169333045 | -0.113961185 | -0.181905879 | 0.023406631 | -0.008914214 | -0.006770236 |  |  |  |  |  | 0.107829717 | 0.122111515 | 0.110764264 | True | True | False | True |
| Q2 | family | subject | kmeans8_train_residual | 0.082626381 | 0.369591524 | 0.076817249 | -0.086245163 | 0.026757447 | 0.000000000 |  |  |  |  |  | 0.118310602 | 0.118255746 | 0.129003275 | True | False | False | True |
| Q2 | story_bundle | subject | kmeans8_train_residual | 0.045147545 | 0.312741810 | 0.055759123 | -0.092783045 | 0.025039601 | 0.000000000 |  |  |  |  |  | 0.121538772 | 0.126035952 | 0.133736832 | True | False | False | True |
| Q2 | family_jepa_story | subject | kmeans6_train_residual | 0.043982342 | 0.307517513 | 0.020978878 | -0.016226643 | 0.026021620 | 0.000000000 |  |  |  |  |  | 0.137324139 | 0.109844670 | 0.116727380 | True | False | False | True |
| Q2 | story_bundle | subject | kmeans10_train_residual | 0.049251127 | 0.293904076 | 0.007787814 | 0.022209186 | 0.028185494 | 0.000000000 |  |  |  |  |  | 0.106922683 | 0.125045222 | 0.146505343 | True | False | False | True |
| Q2 | jepa_resid | dateblock | knn16_train_residual | 0.130284593 | 0.280184868 | 0.117275876 | -0.027350504 | 0.030943960 | 0.000000000 |  |  |  |  |  | 0.110222038 | 0.125729149 | 0.127722426 | True | False | False | True |
| Q2 | family_story | subject | kmeans6_train_residual | 0.044303103 | 0.278783645 | 0.031434935 | -0.017598319 | 0.024576315 | 0.000000000 |  |  |  |  |  | 0.141778193 | 0.125890229 | 0.118573035 | True | False | False | True |
| Q2 | family_story | subject | kmeans8_train_residual | 0.034652191 | 0.276435369 | 0.023796203 | 0.029214038 | 0.021355940 | 0.000000000 |  |  |  |  |  | 0.132159781 | 0.128544658 | 0.148787796 | True | False | False | True |
| Q2 | family_jepa_story | subject | kmeans10_train_residual | 0.090644438 | 0.262970065 | -0.015776339 | -0.054280904 | 0.045336384 | 0.000000000 |  |  |  |  |  | 0.117249510 | 0.123351108 | 0.131497529 | True | False | False | True |
| Q2 | jepa_resid | subject | knn16_train_residual | 0.125289244 | 0.257387612 | -0.051212803 | -0.006785344 | 0.039757539 | 0.000000000 |  |  |  |  |  | 0.125470763 | 0.128448515 | 0.122777289 | True | False | False | True |
| Q2 | jepa_resid | dateblock | knn32_train_residual | 0.080323448 | 0.244066241 | 0.096415168 | -0.071996067 | 0.014981346 | 0.000000000 |  |  |  |  |  | 0.114733778 | 0.115702842 | 0.109089448 | True | False | False | True |
| Q2 | family | dateblock | kmeans10_train_residual | 0.081591423 | 0.241552087 | 0.045656350 | -0.089378178 | -0.000356923 | 0.000000000 |  |  |  |  |  | 0.115274470 | 0.107179076 | 0.119020922 | True | False | False | True |
| Q2 | family | subject | knn16_train_residual | 0.130251837 | 0.225186238 | 0.035993851 | -0.056027958 | 0.071481206 | 0.000000000 |  |  |  |  |  | 0.129748424 | 0.133340286 | 0.128330164 | True | False | False | True |
| Q2 | family_story | subject | kmeans10_train_residual | 0.061908316 | 0.222390401 | 0.021318027 | -0.007133801 | 0.038067387 | 0.000000000 |  |  |  |  |  | 0.117304910 | 0.120810594 | 0.119797226 | True | False | False | True |
| Q2 | family | subject | knn32_train_residual | 0.077457989 | 0.198589161 | 0.049240997 | 0.001583471 | 0.025675937 | 0.000000000 |  |  |  |  |  | 0.125497086 | 0.131527566 | 0.122765466 | True | False | False | True |
| Q2 | jepa_resid | subject | kmeans10_train_residual | 0.088938735 | 0.196796417 | -0.061556503 | -0.082501226 | 0.031935861 | 0.000000000 |  |  |  |  |  | 0.115114198 | 0.129121312 | 0.131136725 | True | False | False | True |
| Q2 | story_bundle | subject | kmeans12_train_residual | 0.076524320 | 0.196043085 | -0.000295757 | -0.001371414 | 0.039652254 | 0.000000000 |  |  |  |  |  | 0.120696861 | 0.137810642 | 0.135563995 | True | False | False | True |
| Q2 | family | subject | masked_residual_student_test | 0.160435145 | 0.193473432 | 0.061737983 | 0.028626224 | 0.015378140 | 0.000000000 | 0.765899724 | 0.761606748 | -0.004292977 | -0.332970101 | -0.103548495 | 0.113790083 | 0.125205668 | 0.119073051 | True | False | False | True |
| Q2 | family_jepa_story | subject | kmeans12_train_residual | 0.101279695 | 0.192611293 | 0.026056914 | -0.094846100 | 0.036318304 | 0.000000000 |  |  |  |  |  | 0.142978089 | 0.123026761 | 0.139903926 | True | False | False | True |
| Q2 | jepa_resid | dateblock | kmeans6_train_residual | 0.040120182 | 0.186132292 | 0.097668635 | -0.106281067 | 0.005026695 | 0.000000000 |  |  |  |  |  | 0.107714714 | 0.115971103 | 0.129995268 | True | False | False | True |
| Q2 | family | dateblock | kmeans8_train_residual | 0.045132956 | 0.178774287 | 0.042818149 | -0.056604998 | 0.000654592 | 0.000000000 |  |  |  |  |  | 0.116482288 | 0.128366987 | 0.125849491 | True | False | False | True |
| Q2 | family_story | subject | knn8_train_residual | 0.195329644 | 0.177104922 | 0.103211220 | 0.051592721 | 0.066226912 | 0.000000000 |  |  |  |  |  | 0.134276952 | 0.111604608 | 0.130761243 | True | False | False | True |
| Q2 | family | subject | knn8_train_residual | 0.178373936 | 0.172315957 | 0.093990929 | -0.021394648 | 0.053187893 | 0.000000000 |  |  |  |  |  | 0.114665390 | 0.123559668 | 0.108533983 | True | False | False | True |
| Q2 | jepa_resid | dateblock | kmeans12_train_residual | 0.087398836 | 0.171622367 | 0.063601377 | 0.047398467 | 0.007525124 | 0.000000000 |  |  |  |  |  | 0.111608060 | 0.124786288 | 0.105787369 | True | False | False | True |
| Q2 | family_jepa_story | subject | kmeans8_train_residual | 0.094714171 | 0.169218408 | -0.031437610 | -0.050047719 | 0.040939381 | 0.000000000 |  |  |  |  |  | 0.127388414 | 0.118023004 | 0.132604163 | True | False | False | True |
| Q2 | family_story | dateblock | knn8_train_residual | 0.165597100 | 0.148470031 | 0.090641452 | 0.071042986 | 0.039247089 | 0.000000000 |  |  |  |  |  | 0.114144348 | 0.118623111 | 0.125294983 | True | False | False | True |
| Q2 | family | subject | kmeans6_train_residual | 0.043101590 | 0.142969798 | 0.046920691 | -0.013626003 | -0.009993522 | 0.000000000 |  |  |  |  |  | 0.139630017 | 0.129760243 | 0.120046220 | True | False | False | True |

## Local Residual Students

| target | view_id | split | method | base_logloss | aug_logloss | logloss_delta | teacher_r2 | teacher_spearman |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q2 | jepa_resid | subject | masked_residual_student | 0.765899724 | 0.735689108 | -0.030210616 | -0.195539000 | -0.234482211 |
| Q2 | jepa_resid | dateblock | masked_residual_student | 0.715333740 | 0.708028054 | -0.007305686 | -0.110750906 | -0.088994612 |
| Q2 | family | subject | masked_residual_student | 0.765899724 | 0.761606748 | -0.004292977 | -0.332970101 | -0.103548495 |
| Q2 | raw_day | dateblock | masked_residual_student | 0.715333740 | 0.711928737 | -0.003405003 | -0.447152259 | -0.098722397 |
| Q2 | story_bundle | subject | masked_residual_student | 0.765899724 | 0.766593370 | 0.000693646 | -0.618885224 | 0.005532406 |
| Q2 | raw_day | subject | masked_residual_student | 0.765899724 | 0.766970810 | 0.001071086 | -0.689105363 | -0.027644515 |
| Q2 | family_story | subject | masked_residual_student | 0.765899724 | 0.770449492 | 0.004549768 | -0.836716541 | -0.016266945 |
| Q2 | family_jepa_story | subject | masked_residual_student | 0.765899724 | 0.770790649 | 0.004890925 | -0.967908666 | -0.044308828 |
| Q2 | family_jepa_story | dateblock | masked_residual_student | 0.715333740 | 0.720775443 | 0.005441703 | -0.666899494 | 0.008571104 |
| Q2 | family_story | dateblock | masked_residual_student | 0.715333740 | 0.721037940 | 0.005704201 | -0.560867910 | 0.041964257 |
| Q2 | story_bundle | dateblock | masked_residual_student | 0.715333740 | 0.721137997 | 0.005804258 | -0.495583097 | -0.001654329 |
| Q2 | family | dateblock | masked_residual_student | 0.715333740 | 0.722895599 | 0.007561860 | -0.127743977 | 0.012906796 |
| S1 | family_jepa_story | subject | masked_residual_student | 0.656678990 | 0.647551344 | -0.009127646 | -0.633356974 | 0.172189624 |
| S1 | family_story | subject | masked_residual_student | 0.656678990 | 0.651570480 | -0.005108509 | -0.593627916 | 0.114382985 |
| S1 | raw_day | subject | masked_residual_student | 0.656678990 | 0.652535907 | -0.004143083 | -0.733518096 | 0.152536391 |
| S1 | story_bundle | dateblock | masked_residual_student | 0.581863284 | 0.579225211 | -0.002638073 | -0.341165327 | 0.108914118 |
| S1 | jepa_resid | subject | masked_residual_student | 0.656678990 | 0.656101108 | -0.000577882 | -0.023097456 | 0.145106955 |
| S1 | family_story | dateblock | masked_residual_student | 0.581863284 | 0.581563659 | -0.000299625 | -0.478699268 | 0.056807984 |
| S1 | jepa_resid | dateblock | masked_residual_student | 0.581863284 | 0.581948825 | 0.000085541 | -0.069786831 | -0.071653687 |
| S1 | family_jepa_story | dateblock | masked_residual_student | 0.581863284 | 0.582536384 | 0.000673100 | -0.576157169 | 0.034721554 |
| S1 | raw_day | dateblock | masked_residual_student | 0.581863284 | 0.584148004 | 0.002284720 | -0.424538548 | -0.077356826 |
| S1 | story_bundle | subject | masked_residual_student | 0.656678990 | 0.659098167 | 0.002419177 | -0.545947541 | 0.062858780 |
| S1 | family | dateblock | masked_residual_student | 0.581863284 | 0.585872054 | 0.004008770 | -0.107208364 | -0.057954854 |
| S1 | family | subject | masked_residual_student | 0.656678990 | 0.667162911 | 0.010483921 | -0.304805406 | -0.040220446 |

## kNN Residual Probes

| target | view_id | split | method | mean_neighbor_dist | std_score |
| --- | --- | --- | --- | --- | --- |
| Q2 | story_bundle | subject | knn8_train_residual | 12.771306407 | 0.198134939 |
| Q2 | family_story | subject | knn8_train_residual | 14.370126635 | 0.195329644 |
| Q2 | family_jepa_story | subject | knn8_train_residual | 15.584188488 | 0.193024756 |
| Q2 | raw_day | subject | knn8_train_residual | 10.226874033 | 0.192288122 |
| Q2 | family | dateblock | knn8_train_residual | 4.467540137 | 0.185220115 |
| Q2 | raw_day | dateblock | knn8_train_residual | 10.226874033 | 0.183324522 |
| Q2 | jepa_resid | dateblock | knn8_train_residual | 3.611749484 | 0.180921075 |
| Q2 | family | subject | knn8_train_residual | 4.467540137 | 0.178373936 |
| Q2 | jepa_resid | subject | knn8_train_residual | 3.611749484 | 0.175612146 |
| Q2 | family_story | dateblock | knn8_train_residual | 14.370126635 | 0.165597100 |
| Q2 | family_jepa_story | dateblock | knn8_train_residual | 15.584188488 | 0.164761039 |
| Q2 | story_bundle | dateblock | knn8_train_residual | 12.771306407 | 0.164143389 |
| Q2 | family_story | subject | knn16_train_residual | 15.155084596 | 0.146374865 |
| Q2 | story_bundle | subject | knn16_train_residual | 13.512259025 | 0.145008071 |
| Q2 | raw_day | subject | knn16_train_residual | 10.836067782 | 0.138321560 |
| Q2 | family | dateblock | knn16_train_residual | 4.899129258 | 0.131167473 |
| Q2 | jepa_resid | dateblock | knn16_train_residual | 3.924288482 | 0.130284593 |
| Q2 | family | subject | knn16_train_residual | 4.899129258 | 0.130251837 |
| Q2 | family_story | dateblock | knn16_train_residual | 15.155084596 | 0.125759544 |
| Q2 | jepa_resid | subject | knn16_train_residual | 3.924288482 | 0.125289244 |
| Q2 | family_jepa_story | subject | knn16_train_residual | 16.407844595 | 0.119019978 |
| Q2 | story_bundle | dateblock | knn16_train_residual | 13.512259025 | 0.118096612 |
| Q2 | raw_day | dateblock | knn16_train_residual | 10.836067782 | 0.117142767 |
| Q2 | family_jepa_story | dateblock | knn16_train_residual | 16.407844595 | 0.107250758 |
| Q2 | raw_day | subject | knn32_train_residual | 11.602596543 | 0.099175777 |
| Q2 | jepa_resid | subject | knn32_train_residual | 4.316059409 | 0.087746816 |
| Q2 | story_bundle | subject | knn32_train_residual | 14.486325269 | 0.082525183 |
| Q2 | raw_day | dateblock | knn32_train_residual | 11.602596543 | 0.082248396 |
| Q2 | jepa_resid | dateblock | knn32_train_residual | 4.316059409 | 0.080323448 |
| Q2 | family_story | subject | knn32_train_residual | 16.125213921 | 0.079079289 |

## Cluster Residual Probes

| target | view_id | split | method | min_train_cluster_count | max_train_cluster_count | std_score |
| --- | --- | --- | --- | --- | --- | --- |
| Q2 | family | dateblock | kmeans12_train_residual | 5 | 157 | 0.108785067 |
| Q2 | raw_day | dateblock | kmeans12_train_residual | 12 | 74 | 0.107949073 |
| Q2 | raw_day | subject | kmeans10_train_residual | 12 | 96 | 0.106978881 |
| Q2 | jepa_resid | subject | kmeans12_train_residual | 11 | 87 | 0.103213120 |
| Q2 | family_jepa_story | subject | kmeans12_train_residual | 7 | 63 | 0.101279695 |
| Q2 | raw_day | subject | kmeans12_train_residual | 13 | 115 | 0.100382402 |
| Q2 | raw_day | dateblock | kmeans10_train_residual | 12 | 80 | 0.097414615 |
| Q2 | family_jepa_story | subject | kmeans8_train_residual | 22 | 98 | 0.094714171 |
| Q2 | family_jepa_story | subject | kmeans10_train_residual | 21 | 71 | 0.090644438 |
| Q2 | jepa_resid | subject | kmeans10_train_residual | 12 | 93 | 0.088938735 |
| Q2 | jepa_resid | dateblock | kmeans12_train_residual | 10 | 93 | 0.087398836 |
| Q2 | family | subject | kmeans10_train_residual | 14 | 153 | 0.086065632 |
| Q2 | raw_day | subject | kmeans8_train_residual | 15 | 189 | 0.083612919 |
| Q2 | family | subject | kmeans8_train_residual | 13 | 169 | 0.082626381 |
| Q2 | family | dateblock | kmeans10_train_residual | 17 | 153 | 0.081591423 |
| Q2 | story_bundle | subject | kmeans12_train_residual | 13 | 67 | 0.076524320 |
| Q2 | jepa_resid | subject | kmeans8_train_residual | 30 | 133 | 0.072423248 |
| Q2 | family_jepa_story | dateblock | kmeans10_train_residual | 20 | 67 | 0.071805882 |
| Q2 | family_story | subject | kmeans12_train_residual | 18 | 60 | 0.069663290 |
| Q2 | family | subject | kmeans12_train_residual | 10 | 131 | 0.066741342 |
| Q2 | raw_day | dateblock | kmeans8_train_residual | 15 | 139 | 0.066197409 |
| Q2 | jepa_resid | dateblock | kmeans10_train_residual | 24 | 80 | 0.064902038 |
| Q2 | family_story | subject | kmeans10_train_residual | 17 | 69 | 0.061908316 |
| Q2 | family_jepa_story | dateblock | kmeans8_train_residual | 23 | 94 | 0.060925843 |
| Q2 | jepa_resid | subject | kmeans6_train_residual | 37 | 141 | 0.060647732 |
| Q2 | story_bundle | dateblock | kmeans12_train_residual | 12 | 62 | 0.060106258 |
| Q2 | family_jepa_story | dateblock | kmeans12_train_residual | 17 | 63 | 0.059208771 |
| Q2 | family_story | dateblock | kmeans12_train_residual | 13 | 58 | 0.054210415 |
| Q2 | family_story | dateblock | kmeans10_train_residual | 18 | 58 | 0.052227901 |
| Q2 | story_bundle | subject | kmeans6_train_residual | 50 | 110 | 0.051973246 |

## Interpretation

E368 is no longer only a public-sensor artifact: at least part of its Q2/S1 movement is recoverable from train-side lifestyle residual structure. Keep E368 as the current information-rich submission candidate.

## Files

- `e369_q2s1_lifestyle_transfer_summary.csv`
- `e369_q2s1_lifestyle_transfer_local_residual.csv`
- `e369_q2s1_lifestyle_transfer_knn.csv`
- `e369_q2s1_lifestyle_transfer_clusters.csv`
- `e369_q2s1_lifestyle_transfer_nulls.csv`
- `e369_q2s1_lifestyle_transfer_movement.csv`
- `e369_q2s1_lifestyle_transfer_decision.csv`
