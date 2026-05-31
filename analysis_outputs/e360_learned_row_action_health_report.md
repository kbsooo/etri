# E360 Learned Row-Action-Health Generator

## Question

Can a learned nonlinear row-action generator do what E359 hand gates could not: preserve output visibility while lowering row-state public-survival risk?

## Method

- Training data: E359 row-gated compact action outcomes.
- Target representation: composite of E272 p90 visibility, mean visibility, bad-axis margin, row-state predicted public loss, row-state variance, bad-minus-good exposure, and movement size.
- Context: source action, gate/action geometry, movement-weighted E328 lifestyle state, and E268 story-tail exposures.
- Generator: random nonlinear row policies over risk/good clusters, ownlife PCs, and human/social story axes, shortlisted by the learned surrogate.
- Verification: actual E272 selector plus actual E358 row-state public-survival scoring.

## Surrogate Diagnostics

| model | split | spearman_health | spearman_visibility | spearman_rowloss | top20_overlap | n |
| --- | --- | --- | --- | --- | --- | --- |
| extratrees | random5 | 0.972450 | 0.118049 | 0.789205 | 0.208333 | 124 |
| randomforest | random5 | 0.953114 | 0.131323 | 0.769832 | 0.208333 | 124 |
| extratrees | leave_source | 0.639068 | 0.180223 | 0.504667 | 0.208333 | 124 |
| randomforest | leave_source | 0.600806 | 0.221986 | 0.463119 | 0.208333 | 124 |

## Decision

| decision | variant | selected_uploadsafe_file | e360_actual_score | pred_delta_vs_current_p90 | rowstate_pred_public_loss_mean | rowstate_bad_minus_good_exposure | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| no_rowaction_submission | e351_robust_center__learned_story_nonmonotone_s1_counter_1273 | none | 0.736369594 | -0.000035678 | 0.000592192 | 0.146408779 | Learned row-action generator did not clear strict E272 visibility plus E358 row-state health gates. |

## Source/Policy Summary

| source_id | policy_family | n | submit | near | strict | best_p90 | best_rowloss | best_exposure | best_actual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e351_robust_center | story_nonmonotone | 10 | 0 | 0 | 0 | -0.000044302 | 0.000592192 | 0.135116254 | 0.736369594 |
| e356_halfs3_amp | free_mixture | 10 | 0 | 0 | 0 | -0.000047272 | 0.000527409 | 0.145877304 | 0.728964613 |
| e351_robust_center | health_prior | 10 | 0 | 0 | 0 | -0.000047431 | 0.000852430 | 0.139959041 | 0.717627785 |
| e356_halfs3_amp | anti_bad_cluster | 10 | 0 | 0 | 0 | -0.000044273 | 0.000822141 | 0.128142726 | 0.703473132 |
| e351_robust_center | anti_bad_cluster | 10 | 0 | 0 | 0 | -0.000045034 | 0.000775181 | 0.120157646 | 0.661074705 |
| e356_halfs3_amp | health_prior | 10 | 0 | 0 | 0 | -0.000041951 | 0.000892940 | 0.135266687 | 0.657798165 |
| e349_compact_core | story_nonmonotone | 10 | 0 | 0 | 0 | -0.000047709 | 0.000829766 | 0.141863808 | 0.645740498 |
| e351_robust_center | pc_episode | 10 | 0 | 0 | 0 | -0.000040274 | 0.000657044 | 0.130173217 | 0.643971166 |
| e356_halfs3_amp | pc_episode | 10 | 0 | 0 | 0 | -0.000047126 | 0.000624116 | 0.122423410 | 0.639711664 |
| e349_compact_core | anti_bad_cluster | 10 | 0 | 0 | 0 | -0.000042420 | 0.000819240 | 0.126073259 | 0.622608126 |
| e349_compact_core | pc_episode | 10 | 0 | 0 | 0 | -0.000047493 | 0.000553111 | 0.138845198 | 0.587090433 |
| e351_robust_center | free_mixture | 10 | 0 | 0 | 1 | -0.000050147 | 0.000614242 | 0.157318069 | 0.585058978 |
| e349_compact_core | health_prior | 10 | 0 | 0 | 0 | -0.000044839 | 0.000976378 | 0.119787542 | 0.534338139 |
| e349_compact_core | free_mixture | 10 | 0 | 0 | 0 | -0.000043831 | 0.000651767 | 0.138255860 | 0.529161206 |

## Top Actual-Stress Candidates

| variant | source_id | policy_family | target_policy | e360_submission_gate | e360_nearmiss_gate | e360_actual_score | e360_surrogate_mean | pred_delta_vs_current_p90 | pred_beats_current_rate | incremental_bad_axis_vs_current | rowstate_pred_public_loss_mean | rowstate_pred_public_loss_std | rowstate_bad_minus_good_exposure | wmean_rowstate_bad_minus_good | move_l1 | gated_l1_ratio | share_S3 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e351_robust_center__learned_story_nonmonotone_s1_counter_1273 | e351_robust_center | story_nonmonotone | s1_counter | False | False | 0.736369594 | 0.530319819 | -0.000035678 | 0.972222222 | 0.009103242 | 0.000592192 | 0.000235768 | 0.146408779 | 0.146408779 | 2.924792947 | 0.631224584 | 0.000169372 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_story_nonmonotone_s1_counter_1273_7608db8d.csv |
| e356_halfs3_amp__learned_free_mixture_random_compact_0151 | e356_halfs3_amp | free_mixture | random_compact | False | False | 0.728964613 | 0.551640360 | -0.000040955 | 0.986111111 | 0.009883952 | 0.000830782 | 0.000465895 | 0.149550574 | 0.149550574 | 2.850028524 | 0.615342302 | 0.003630120 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_free_mixture_random_compact_0151_59bef8b2.csv |
| e351_robust_center__learned_health_prior_s1_counter_1134 | e351_robust_center | health_prior | s1_counter | False | False | 0.717627785 | 0.549079227 | -0.000040195 | 0.986111111 | 0.011059941 | 0.000852430 | 0.000489474 | 0.141328432 | 0.141328432 | 3.410930985 | 0.736142192 | 0.001439185 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_health_prior_s1_counter_1134_b67893dd.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_compact_qs1_0771 | e356_halfs3_amp | anti_bad_cluster | compact_qs1 | False | False | 0.703473132 | 0.549041811 | -0.000035153 | 0.986111111 | 0.010152524 | 0.000850792 | 0.000460467 | 0.140270987 | 0.140270987 | 2.925361219 | 0.631607190 | 0.001213430 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_compact_qs1_0771_ef014604.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_random_compact_0220 | e356_halfs3_amp | anti_bad_cluster | random_compact | False | False | 0.690760157 | 0.548594990 | -0.000033612 | 0.986111111 | 0.008625204 | 0.000853162 | 0.000447238 | 0.144841913 | 0.144841913 | 2.845228614 | 0.614305966 | 0.004020220 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_random_compact_0220_eea78eee.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_low_s3_1712 | e356_halfs3_amp | anti_bad_cluster | low_s3 | False | False | 0.679292267 | 0.548951588 | -0.000035493 | 0.986111111 | 0.010479684 | 0.000846622 | 0.000444352 | 0.144482160 | 0.144482160 | 3.037960428 | 0.655918194 | 0.001003388 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_low_s3_1712_71429eb0.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_random_compact_1058 | e356_halfs3_amp | anti_bad_cluster | random_compact | False | False | 0.673394495 | 0.539958172 | -0.000034094 | 0.986111111 | 0.010863384 | 0.000822141 | 0.000431671 | 0.135694022 | 0.135694022 | 2.930346106 | 0.632683464 | 0.003570620 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_random_compact_1058_24ffde30.csv |
| e351_robust_center__learned_anti_bad_cluster_compact_qs1_0477 | e351_robust_center | anti_bad_cluster | compact_qs1 | False | False | 0.661074705 | 0.545539873 | -0.000034095 | 0.986111111 | 0.010272106 | 0.000839680 | 0.000436029 | 0.143641379 | 0.143641379 | 2.957211226 | 0.638221050 | 0.000714609 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_anti_bad_cluster_compact_qs1_0477_85969e63.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_low_s3_1357 | e356_halfs3_amp | anti_bad_cluster | low_s3 | False | False | 0.660157274 | 0.548101247 | -0.000041186 | 0.986111111 | 0.011300400 | 0.000931775 | 0.000543430 | 0.141050951 | 0.141050951 | 3.391486450 | 0.732247085 | 0.001449626 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_low_s3_1357_f8fe86ce.csv |
| e356_halfs3_amp__learned_health_prior_s1_counter_1759 | e356_halfs3_amp | health_prior | s1_counter | False | False | 0.657798165 | 0.543421292 | -0.000039040 | 0.986111111 | 0.011116958 | 0.000892940 | 0.000500360 | 0.142818897 | 0.142818897 | 3.654360833 | 0.789003615 | 0.000123431 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_health_prior_s1_counter_1759_95c2394a.csv |
| e351_robust_center__learned_anti_bad_cluster_subjective_heavy_0199 | e351_robust_center | anti_bad_cluster | subjective_heavy | False | False | 0.656094364 | 0.501474220 | -0.000034315 | 0.986111111 | 0.009887189 | 0.000896716 | 0.000518607 | 0.120157646 | 0.120157646 | 2.835102263 | 0.611867670 | 0.000444996 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_anti_bad_cluster_subjective_heavy_0199_87e7cbb5.csv |
| e349_compact_core__learned_story_nonmonotone_compact_qs1_0051 | e349_compact_core | story_nonmonotone | compact_qs1 | False | False | 0.645740498 | 0.423055887 | -0.000039153 | 0.986111111 | 0.009207961 | 0.000884680 | 0.000528100 | 0.145441961 | 0.145441961 | 2.944067205 | 0.639984639 | 0.000000000 | analysis_outputs/submission_e360_rowaction_e349_compact_core__learned_story_nonmonotone_compact_qs1_0051_dc0ea793.csv |
| e356_halfs3_amp__learned_free_mixture_low_s3_1625 | e356_halfs3_amp | free_mixture | low_s3 | False | False | 0.645674967 | 0.542328486 | -0.000040985 | 0.972222222 | 0.011307167 | 0.000752061 | 0.000351838 | 0.167618750 | 0.167618750 | 3.157355172 | 0.681696405 | 0.001058324 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_free_mixture_low_s3_1625_27043cb5.csv |
| e351_robust_center__learned_anti_bad_cluster_random_compact_1556 | e351_robust_center | anti_bad_cluster | random_compact | False | False | 0.644036697 | 0.552581315 | -0.000032338 | 0.986111111 | 0.010727331 | 0.000775181 | 0.000362328 | 0.144983146 | 0.144983146 | 2.936684582 | 0.633791019 | 0.002057059 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_anti_bad_cluster_random_compact_1556_f435ecf2.csv |
| e351_robust_center__learned_pc_episode_compact_qs1_0576 | e351_robust_center | pc_episode | compact_qs1 | False | False | 0.643971166 | 0.525594864 | -0.000025763 | 0.986111111 | 0.010182057 | 0.000657044 | 0.000265552 | 0.131670755 | 0.131670755 | 2.545300129 | 0.549322993 | 0.000671868 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_pc_episode_compact_qs1_0576_df431c9d.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_s1_counter_0264 | e356_halfs3_amp | anti_bad_cluster | s1_counter | False | False | 0.642660550 | 0.523495101 | -0.000035016 | 0.986111111 | 0.010408303 | 0.000883510 | 0.000507002 | 0.134071307 | 0.134071307 | 2.961382771 | 0.639384510 | 0.000117102 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_s1_counter_0264_1b739291.csv |
| e351_robust_center__learned_pc_episode_s1_counter_0786 | e351_robust_center | pc_episode | s1_counter | False | False | 0.641087811 | 0.509774574 | -0.000024403 | 0.986111111 | 0.009217432 | 0.000773056 | 0.000388038 | 0.130173217 | 0.130173217 | 2.627820205 | 0.567132356 | 0.001316412 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_pc_episode_s1_counter_0786_4661d822.csv |
| e356_halfs3_amp__learned_pc_episode_compact_qs1_0804 | e356_halfs3_amp | pc_episode | compact_qs1 | False | False | 0.639711664 | 0.545428863 | -0.000043364 | 0.986111111 | 0.011332117 | 0.000923439 | 0.000526458 | 0.148995484 | 0.148995484 | 3.369053807 | 0.727403711 | 0.001230537 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_pc_episode_compact_qs1_0804_34f971fe.csv |
| e356_halfs3_amp__learned_free_mixture_random_compact_1098 | e356_halfs3_amp | free_mixture | random_compact | False | False | 0.639646134 | 0.541229307 | -0.000047272 | 0.986111111 | 0.011003440 | 0.000898963 | 0.000389564 | 0.171455379 | 0.171455379 | 3.995523284 | 0.862663119 | 0.003240093 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_free_mixture_random_compact_1098_38786310.csv |
| e351_robust_center__learned_anti_bad_cluster_random_compact_1553 | e351_robust_center | anti_bad_cluster | random_compact | False | False | 0.636566186 | 0.547813600 | -0.000042638 | 0.986111111 | 0.012320921 | 0.000900229 | 0.000499276 | 0.147841225 | 0.147841225 | 3.566965644 | 0.769817367 | 0.002571398 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_anti_bad_cluster_random_compact_1553_0dde5020.csv |
| e351_robust_center__learned_anti_bad_cluster_s1_counter_0869 | e351_robust_center | anti_bad_cluster | s1_counter | False | False | 0.635386632 | 0.545392123 | -0.000037046 | 0.986111111 | 0.010172722 | 0.000933569 | 0.000542675 | 0.142768209 | 0.142768209 | 3.189825186 | 0.688423458 | 0.000017250 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_anti_bad_cluster_s1_counter_0869_241f8283.csv |
| e356_halfs3_amp__learned_pc_episode_low_s3_0814 | e356_halfs3_amp | pc_episode | low_s3 | False | False | 0.632961992 | 0.495587527 | -0.000025117 | 0.986111111 | 0.007708678 | 0.000869913 | 0.000468657 | 0.122423410 | 0.122423410 | 2.426089273 | 0.523810673 | 0.000600114 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_pc_episode_low_s3_0814_55b0c47a.csv |
| e356_halfs3_amp__learned_health_prior_low_s3_0691 | e356_halfs3_amp | health_prior | low_s3 | False | False | 0.629292267 | 0.547107247 | -0.000040045 | 0.986111111 | 0.010237245 | 0.000956533 | 0.000567388 | 0.144853840 | 0.144853840 | 3.181809228 | 0.686976217 | 0.001457834 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_health_prior_low_s3_0691_b7411b1a.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_s1_counter_0107 | e356_halfs3_amp | anti_bad_cluster | s1_counter | False | False | 0.627981651 | 0.544003562 | -0.000031707 | 0.986111111 | 0.009324346 | 0.000849594 | 0.000451922 | 0.145921773 | 0.145921773 | 2.935771902 | 0.633854933 | 0.000426293 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_s1_counter_0107_e91b0bea.csv |
| e351_robust_center__learned_pc_episode_s1_counter_1364 | e351_robust_center | pc_episode | s1_counter | False | False | 0.626539974 | 0.522354923 | -0.000027650 | 0.986111111 | 0.010128537 | 0.000718521 | 0.000313107 | 0.141324819 | 0.141324819 | 2.795828863 | 0.603391742 | 0.000408952 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_pc_episode_s1_counter_1364_e914e5c0.csv |
| e351_robust_center__learned_health_prior_s1_counter_0592 | e351_robust_center | health_prior | s1_counter | False | False | 0.626343381 | 0.551757144 | -0.000035537 | 0.986111111 | 0.010405343 | 0.000911167 | 0.000520749 | 0.144959527 | 0.144959527 | 3.330635245 | 0.718812882 | 0.001528931 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_health_prior_s1_counter_0592_cb1eff5e.csv |
| e349_compact_core__learned_anti_bad_cluster_s1_counter_0870 | e349_compact_core | anti_bad_cluster | s1_counter | False | False | 0.622608126 | 0.418195065 | -0.000028913 | 0.972222222 | 0.010079823 | 0.000819240 | 0.000427084 | 0.127899941 | 0.127899941 | 2.897781497 | 0.629922999 | 0.000000000 | analysis_outputs/submission_e360_rowaction_e349_compact_core__learned_anti_bad_cluster_s1_counter_0870_f277d20f.csv |
| e356_halfs3_amp__learned_free_mixture_s1_counter_0299 | e356_halfs3_amp | free_mixture | s1_counter | False | False | 0.622280472 | 0.539012765 | -0.000027219 | 0.986111111 | 0.007714521 | 0.000669521 | 0.000268953 | 0.150113176 | 0.150113176 | 2.726151414 | 0.588596315 | 0.001918057 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_free_mixture_s1_counter_0299_6366c8d1.csv |
| e356_halfs3_amp__learned_free_mixture_compact_qs1_0291 | e356_halfs3_amp | free_mixture | compact_qs1 | False | False | 0.621756225 | 0.536230089 | -0.000035423 | 0.986111111 | 0.010138970 | 0.000870652 | 0.000468881 | 0.145877304 | 0.145877304 | 2.588203739 | 0.558812388 | 0.001148419 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_free_mixture_compact_qs1_0291_c7b7e50a.csv |
| e356_halfs3_amp__learned_health_prior_random_compact_1749 | e356_halfs3_amp | health_prior | random_compact | False | False | 0.621690695 | 0.540876666 | -0.000033114 | 0.986111111 | 0.009122827 | 0.000929648 | 0.000539620 | 0.139420252 | 0.139420252 | 2.776731729 | 0.599516980 | 0.002953803 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_health_prior_random_compact_1749_84071236.csv |
| e351_robust_center__learned_health_prior_low_s3_1015 | e351_robust_center | health_prior | low_s3 | False | False | 0.619462647 | 0.548081538 | -0.000043310 | 0.986111111 | 0.012408057 | 0.000947953 | 0.000569541 | 0.143024917 | 0.143024917 | 3.650386684 | 0.787821175 | 0.000473066 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_health_prior_low_s3_1015_8c60c1ed.csv |
| e351_robust_center__learned_pc_episode_low_s3_0805 | e351_robust_center | pc_episode | low_s3 | False | False | 0.607470511 | 0.538160118 | -0.000030861 | 0.986111111 | 0.009460918 | 0.000835556 | 0.000422179 | 0.148281921 | 0.148281921 | 2.765518435 | 0.596850189 | 0.000239113 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_pc_episode_low_s3_0805_c6877d19.csv |
| e351_robust_center__learned_health_prior_low_s3_0381 | e351_robust_center | health_prior | low_s3 | False | False | 0.605307995 | 0.543907404 | -0.000047431 | 0.986111111 | 0.012250082 | 0.000965948 | 0.000575724 | 0.144114468 | 0.144114468 | 3.788279685 | 0.817581043 | 0.000425119 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_health_prior_low_s3_0381_31cf530a.csv |
| e356_halfs3_amp__learned_health_prior_compact_qs1_0953 | e356_halfs3_amp | health_prior | compact_qs1 | False | False | 0.605242464 | 0.546118212 | -0.000035911 | 0.986111111 | 0.010246187 | 0.000959366 | 0.000581911 | 0.139291467 | 0.139291467 | 3.069648893 | 0.662759969 | 0.001245148 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_health_prior_compact_qs1_0953_02bbbdaf.csv |
| e351_robust_center__learned_health_prior_compact_qs1_1290 | e351_robust_center | health_prior | compact_qs1 | False | False | 0.594692005 | 0.545261961 | -0.000039352 | 0.986111111 | 0.011012452 | 0.000968288 | 0.000585784 | 0.139959041 | 0.139959041 | 3.294785982 | 0.711075946 | 0.000709081 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_health_prior_compact_qs1_1290_d37a51bf.csv |
| e351_robust_center__learned_pc_episode_subjective_heavy_0835 | e351_robust_center | pc_episode | subjective_heavy | False | False | 0.591939712 | 0.532851342 | -0.000038568 | 0.986111111 | 0.010874336 | 0.000857531 | 0.000451398 | 0.156921804 | 0.156921804 | 3.249622419 | 0.701328811 | 0.000085598 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_pc_episode_subjective_heavy_0835_c6dd37cb.csv |
| e356_halfs3_amp__learned_anti_bad_cluster_compact_qs1_0152 | e356_halfs3_amp | anti_bad_cluster | compact_qs1 | False | False | 0.587155963 | 0.555321321 | -0.000044273 | 0.986111111 | 0.012435245 | 0.000963419 | 0.000574200 | 0.147226374 | 0.147226374 | 3.766467879 | 0.813208358 | 0.001248498 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_anti_bad_cluster_compact_qs1_0152_e30ec05c.csv |
| e349_compact_core__learned_pc_episode_s1_counter_1196 | e349_compact_core | pc_episode | s1_counter | False | False | 0.587090433 | 0.423319417 | -0.000026448 | 1.000000000 | 0.010511326 | 0.000553111 | 0.000189919 | 0.142821408 | 0.142821408 | 2.796369442 | 0.607877933 | 0.000000000 | analysis_outputs/submission_e360_rowaction_e349_compact_core__learned_pc_episode_s1_counter_1196_2d4ed9bc.csv |
| e356_halfs3_amp__learned_pc_episode_subjective_heavy_0179 | e356_halfs3_amp | pc_episode | subjective_heavy | False | False | 0.585386632 | 0.541872622 | -0.000034055 | 0.972222222 | 0.011579874 | 0.000624116 | 0.000225855 | 0.154265434 | 0.154265434 | 2.924590239 | 0.631440730 | 0.000566739 | analysis_outputs/submission_e360_rowaction_e356_halfs3_amp__learned_pc_episode_subjective_heavy_0179_c6d60191.csv |
| e351_robust_center__learned_free_mixture_compact_qs1_1412 | e351_robust_center | free_mixture | compact_qs1 | False | False | 0.585058978 | 0.542629785 | -0.000036518 | 0.972222222 | 0.010855574 | 0.000851122 | 0.000432995 | 0.166958225 | 0.166958225 | 3.418897935 | 0.737861608 | 0.000709866 | analysis_outputs/submission_e360_rowaction_e351_robust_center__learned_free_mixture_compact_qs1_1412_30dea0a1.csv |

## Gate-Passing Candidates

_empty_

## Interpretation

- A pass would mean row-action health can be generated from lifestyle/story state rather than only diagnosed after the fact.
- No pass means the current compact action family still cannot separate output visibility from row-state risk, even with learned nonlinear row placement.
- The key next split is then whether to change the source action family or learn a lower-level cell-action generator instead of row-only gates.

## Counts

- E359 training rows: `124`
- generated prefilter pool: `1800`
- materialized shortlist: `140`
- strict output candidates: `1`
- near-miss candidates: `0`
- submission-gate candidates: `0`

## Files

- `analysis_outputs/e360_learned_row_action_health_pool_prefeatures.csv`
- `analysis_outputs/e360_learned_row_action_health_surrogate_diagnostics.csv`
- `analysis_outputs/e360_learned_row_action_health_candidates.csv`
- `analysis_outputs/e360_learned_row_action_health_scores.csv`
- `analysis_outputs/e360_learned_row_action_health_known.csv`
- `analysis_outputs/e360_learned_row_action_health_selection.csv`
- `analysis_outputs/e360_learned_row_action_health_report.md`
