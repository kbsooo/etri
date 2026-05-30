# E184 Public-Anchor Motif Pressure Selector

## Question

E183 killed visible/subject/flank priors as pressure-branch selectors. This
audit asks whether a non-visible cell motif learned from known public
transitions can select the favorable E182 branch for E176/E154/E144.

This is not a submission generator. If the motif cannot survive leave-one-pair
or leave-one-family stress, its live branch score is treated as diagnostic only.

## Result In One Sentence

Direct public-anchor motifs fail: the best direct pair-LOO model `meta_public_axis_plus_swing` has sign accuracy `0.333` and AUC `0.425`. The strongest pair signal is polarity-inverted (`meta_core`, best-polarity accuracy `1.000`), but family-level best direct accuracy/AUC are only `0.600` / `0.178`. Live branch preferences are feature-set unstable: meta_core=0.000, meta_public_axis=1.000, meta_public_axis_plus_support_label=1.000, meta_public_axis_plus_swing=0.000. Under the best direct pair model, candidate rates are e176 `0.000`, e154 `0.000`, e144 `0.000`.

## CV Metrics

| feature_set | group_col | groups_evaluated | cell_count | oof_auc | oof_logloss | oof_brier | group_sign_accuracy | polarity_best_auc | auc_polarity | polarity_best_group_accuracy | group_polarity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meta_public_axis_plus_swing | family | 5 | 4346 | 0.177583778 | 0.969896160 | 0.349300579 | 0.600000000 | 0.822416222 | inverted | 0.600000000 | direct |
| meta_public_axis_plus_support_label | family | 5 | 4346 | 0.045352306 | 1.097806940 | 0.400265946 | 0.600000000 | 0.954647694 | inverted | 0.600000000 | direct |
| meta_public_axis | family | 5 | 4346 | 0.044770071 | 1.095842161 | 0.399975346 | 0.600000000 | 0.955229929 | inverted | 0.600000000 | direct |
| meta_core | family | 5 | 4346 | 0.005559318 | 1.047437780 | 0.398965329 | 0.400000000 | 0.994440682 | inverted | 0.600000000 | inverted |
| meta_public_axis_plus_swing | pair | 6 | 4346 | 0.425169756 | 0.802247646 | 0.295086332 | 0.333333333 | 0.574830244 | inverted | 0.666666667 | inverted |
| meta_public_axis | pair | 6 | 4346 | 0.181497680 | 0.967161513 | 0.372634767 | 0.000000000 | 0.818502320 | inverted | 1.000000000 | inverted |
| meta_public_axis_plus_support_label | pair | 6 | 4346 | 0.180216062 | 0.968741968 | 0.373212017 | 0.000000000 | 0.819783938 | inverted | 1.000000000 | inverted |
| meta_core | pair | 6 | 4346 | 0.022738551 | 0.974943294 | 0.382287715 | 0.000000000 | 0.977261449 | inverted | 1.000000000 | inverted |

## Pair LOO

| feature_set | group_col | heldout | actual_support_compatible | n_cells | motif_score | predicted_support_compatible | correct | cell_logloss | cell_brier | prob_min | prob_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meta_core | pair | e101_vs_e95 | 0 | 50 | 0.649576879 | True | False | 1.056729913 | 0.424444578 | 0.449985413 | 0.690675203 |
| meta_core | pair | e101_vs_mixmin | 1 | 550 | 0.441766650 | False | False | 0.824965094 | 0.314385130 | 0.303926673 | 0.507349697 |
| meta_core | pair | e72_vs_e95 | 0 | 1047 | 0.637614175 | True | False | 1.043697019 | 0.414187609 | 0.429648703 | 0.758989524 |
| meta_core | pair | e72_vs_mixmin | 0 | 893 | 0.604243921 | True | False | 0.941660962 | 0.369645807 | 0.445514332 | 0.728736199 |
| meta_core | pair | e95_vs_mixmin | 1 | 550 | 0.437502510 | False | False | 0.838069475 | 0.320251864 | 0.293969702 | 0.512668109 |
| meta_core | pair | mixmin_vs_a2c8 | 1 | 1256 | 0.339813125 | False | False | 1.144537302 | 0.450811304 | 0.187287239 | 0.543833645 |
| meta_public_axis | pair | e101_vs_e95 | 0 | 50 | 0.644264891 | True | False | 1.041771854 | 0.417595825 | 0.407887449 | 0.704003867 |
| meta_public_axis | pair | e101_vs_mixmin | 1 | 550 | 0.464197536 | False | False | 0.828918400 | 0.310104075 | 0.134891299 | 0.698110994 |
| meta_public_axis | pair | e72_vs_e95 | 0 | 1047 | 0.648210672 | True | False | 1.172692152 | 0.448346907 | 0.067385134 | 0.892562197 |
| meta_public_axis | pair | e72_vs_mixmin | 0 | 893 | 0.583177313 | True | False | 0.906288400 | 0.351405439 | 0.250962731 | 0.773995498 |
| meta_public_axis | pair | e95_vs_mixmin | 1 | 550 | 0.453289876 | False | False | 0.866245296 | 0.325303106 | 0.122090049 | 0.706444871 |
| meta_public_axis | pair | mixmin_vs_a2c8 | 1 | 1256 | 0.394261595 | False | False | 0.987052977 | 0.383053250 | 0.117330633 | 0.658354418 |
| meta_public_axis_plus_support_label | pair | e101_vs_e95 | 0 | 50 | 0.645733854 | True | False | 1.046466842 | 0.419599243 | 0.415626017 | 0.711903890 |
| meta_public_axis_plus_support_label | pair | e101_vs_mixmin | 1 | 550 | 0.464169515 | False | False | 0.829033168 | 0.310152199 | 0.134563288 | 0.698557048 |
| meta_public_axis_plus_support_label | pair | e72_vs_e95 | 0 | 1047 | 0.648469525 | True | False | 1.175471455 | 0.448973397 | 0.067319053 | 0.896512758 |
| meta_public_axis_plus_support_label | pair | e72_vs_mixmin | 0 | 893 | 0.583527364 | True | False | 0.907665757 | 0.351943891 | 0.243668160 | 0.779419891 |
| meta_public_axis_plus_support_label | pair | e95_vs_mixmin | 1 | 550 | 0.453223012 | False | False | 0.866568052 | 0.325440400 | 0.122765511 | 0.707657487 |
| meta_public_axis_plus_support_label | pair | mixmin_vs_a2c8 | 1 | 1256 | 0.394180895 | False | False | 0.987246532 | 0.383162970 | 0.120036565 | 0.661752873 |
| meta_public_axis_plus_swing | pair | e101_vs_e95 | 0 | 50 | 0.479085063 | False | True | 0.669750519 | 0.240627577 | 0.137005073 | 0.627086281 |
| meta_public_axis_plus_swing | pair | e101_vs_mixmin | 1 | 550 | 0.429404126 | False | False | 0.896894310 | 0.340111235 | 0.019727119 | 0.632998199 |
| meta_public_axis_plus_swing | pair | e72_vs_e95 | 0 | 1047 | 0.604757016 | True | False | 1.083840230 | 0.404914527 | 0.098972242 | 0.889155421 |
| meta_public_axis_plus_swing | pair | e72_vs_mixmin | 0 | 893 | 0.503899534 | True | False | 0.714467380 | 0.260322348 | 0.166145518 | 0.730938520 |
| meta_public_axis_plus_swing | pair | e95_vs_mixmin | 1 | 550 | 0.447559731 | False | False | 0.851411042 | 0.319854827 | 0.023245110 | 0.645595880 |
| meta_public_axis_plus_swing | pair | mixmin_vs_a2c8 | 1 | 1256 | 0.574013133 | True | True | 0.597122393 | 0.204687479 | 0.081462013 | 0.864283082 |

## Family LOO

| feature_set | group_col | heldout | actual_support_compatible | n_cells | motif_score | predicted_support_compatible | correct | cell_logloss | cell_brier | prob_min | prob_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meta_core | family | broad_public_success | 1 | 1256 | 0.451690633 | False | False | 0.820715594 | 0.311658051 | 0.314328038 | 0.641967627 |
| meta_core | family | frontier_hardtail_success | 1 | 550 | 0.536578174 | True | True | 0.633279086 | 0.220206903 | 0.366270163 | 0.628290378 |
| meta_core | family | frontier_near_loss | 0 | 50 | 0.772530474 | True | False | 1.487310590 | 0.597631191 | 0.654744160 | 0.799088996 |
| meta_core | family | mixmin_relative_success | 1 | 550 | 0.542843322 | True | True | 0.618887281 | 0.213116049 | 0.376011040 | 0.622245607 |
| meta_core | family | q2s3_gate_fail | 0 | 1940 | 0.805065984 | True | False | 1.676996349 | 0.652214449 | 0.550617008 | 0.892723287 |
| meta_public_axis | family | broad_public_success | 1 | 1256 | 0.521111451 | True | True | 0.674529630 | 0.241041234 | 0.257496458 | 0.742877062 |
| meta_public_axis | family | frontier_hardtail_success | 1 | 550 | 0.550878220 | True | True | 0.656620134 | 0.231151675 | 0.142975666 | 0.783819536 |
| meta_public_axis | family | frontier_near_loss | 0 | 50 | 0.769290277 | True | False | 1.474350690 | 0.592810804 | 0.612102800 | 0.804831376 |
| meta_public_axis | family | mixmin_relative_success | 1 | 550 | 0.565361188 | True | True | 0.618332208 | 0.213872742 | 0.159170660 | 0.777973582 |
| meta_public_axis | family | q2s3_gate_fail | 0 | 1940 | 0.840557994 | True | False | 2.055378144 | 0.721000275 | 0.253675309 | 0.979570906 |
| meta_public_axis_plus_support_label | family | broad_public_success | 1 | 1256 | 0.521414891 | True | True | 0.674197124 | 0.240894890 | 0.252963108 | 0.749653177 |
| meta_public_axis_plus_support_label | family | frontier_hardtail_success | 1 | 550 | 0.551121551 | True | True | 0.655969551 | 0.230770147 | 0.140354340 | 0.786925591 |
| meta_public_axis_plus_support_label | family | frontier_near_loss | 0 | 50 | 0.769823913 | True | False | 1.477070773 | 0.593666266 | 0.616884104 | 0.808395990 |
| meta_public_axis_plus_support_label | family | mixmin_relative_success | 1 | 550 | 0.565576779 | True | True | 0.617707276 | 0.213508312 | 0.155875624 | 0.781691245 |
| meta_public_axis_plus_support_label | family | q2s3_gate_fail | 0 | 1940 | 0.841354995 | True | False | 2.064089977 | 0.722490113 | 0.232935581 | 0.981424373 |
| meta_public_axis_plus_swing | family | broad_public_success | 1 | 1256 | 0.705860836 | True | True | 0.360061832 | 0.097061581 | 0.258406069 | 0.891284477 |
| meta_public_axis_plus_swing | family | frontier_hardtail_success | 1 | 550 | 0.539817570 | True | True | 0.645089858 | 0.225845757 | 0.075482091 | 0.728863408 |
| meta_public_axis_plus_swing | family | frontier_near_loss | 0 | 50 | 0.682200137 | True | False | 1.170943420 | 0.471825977 | 0.377395896 | 0.772811825 |
| meta_public_axis_plus_swing | family | mixmin_relative_success | 1 | 550 | 0.529289471 | True | True | 0.667554932 | 0.236190710 | 0.065318809 | 0.719038136 |
| meta_public_axis_plus_swing | family | q2s3_gate_fail | 0 | 1940 | 0.839142817 | True | False | 2.005830759 | 0.715578873 | 0.321367638 | 0.974937635 |

## Pressure Branch Summary

| feature_set | candidate | scenario_count | motif_prefers_min_rate | min_minus_max_ce_mean | min_branch_prob_mean | max_branch_prob_mean | motif_prob_support_public_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| meta_core | e144 | 3 | 0.000000000 | 0.205234080 | 0.449196832 | 0.550803168 | 0.447593625 |
| meta_core | e154 | 3 | 0.000000000 | 0.211117275 | 0.447719420 | 0.552280580 | 0.447719420 |
| meta_core | e176 | 3 | 0.000000000 | 0.109240812 | 0.472922333 | 0.527077667 | 0.472604782 |
| meta_public_axis | e144 | 3 | 1.000000000 | -0.455237122 | 0.608440421 | 0.391559579 | 0.608763447 |
| meta_public_axis | e154 | 3 | 1.000000000 | -0.468806197 | 0.611602645 | 0.388397355 | 0.611602645 |
| meta_public_axis | e176 | 3 | 1.000000000 | -0.538404770 | 0.626846343 | 0.373153657 | 0.627350635 |
| meta_public_axis_plus_support_label | e144 | 3 | 1.000000000 | -0.454939857 | 0.608342512 | 0.391657488 | 0.608691806 |
| meta_public_axis_plus_support_label | e154 | 3 | 1.000000000 | -0.468843743 | 0.611588755 | 0.388411245 | 0.611588755 |
| meta_public_axis_plus_support_label | e176 | 3 | 1.000000000 | -0.537209904 | 0.626491916 | 0.373508084 | 0.626986474 |
| meta_public_axis_plus_swing | e144 | 3 | 0.000000000 | 0.044158582 | 0.490786549 | 0.509213451 | 0.489302369 |
| meta_public_axis_plus_swing | e154 | 3 | 0.000000000 | 0.164946066 | 0.468610051 | 0.531389949 | 0.468610051 |
| meta_public_axis_plus_swing | e176 | 3 | 0.000000000 | 1.613836758 | 0.183022705 | 0.816977295 | 0.181302947 |

## Pressure Branch Scenario Details

| feature_set | candidate | scenario | n_diff_cells | motif_prob_support_public_mean | min_branch_prob_mean | max_branch_prob_mean | min_minus_max_ce | motif_prefers_favorable_min | between_train_runs_rate | e72_active_rate | e101_active_rate | top_targets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| meta_core | e144 | global_t010 | 143 | 0.448093831 | 0.452903452 | 0.547096548 | 0.190301558 | False | 0.489510490 | 0.237762238 | 0.020979021 | Q3,Q1,S3,S2 |
| meta_core | e144 | global_t010_subject_t010 | 171 | 0.446950311 | 0.446950311 | 0.553049689 | 0.214249586 | False | 0.508771930 | 0.245614035 | 0.017543860 | Q3,Q1,S3,S2 |
| meta_core | e144 | global_t010_subject_t020 | 178 | 0.447736732 | 0.447736732 | 0.552263268 | 0.211151095 | False | 0.494382022 | 0.230337079 | 0.016853933 | Q3,Q1,S3,S2 |
| meta_core | e154 | global_t010 | 292 | 0.448817607 | 0.448817607 | 0.551182393 | 0.206686778 | False | 0.472602740 | 0.311643836 | 0.017123288 | Q3,Q1,S3,S2 |
| meta_core | e154 | global_t010_subject_t010 | 271 | 0.445548593 | 0.445548593 | 0.554451407 | 0.219906581 | False | 0.487084871 | 0.309963100 | 0.014760148 | Q3,Q1,S3,S4 |
| meta_core | e154 | global_t010_subject_t020 | 285 | 0.448792061 | 0.448792061 | 0.551207939 | 0.206758464 | False | 0.470175439 | 0.312280702 | 0.014035088 | Q3,Q1,S3,S2 |
| meta_core | e176 | global_t010 | 605 | 0.472620881 | 0.472620881 | 0.527379119 | 0.110434280 | False | 0.826446281 | 0.272727273 | 0.011570248 | Q2,S1,S3,S4 |
| meta_core | e176 | global_t010_subject_t010 | 587 | 0.472363100 | 0.473217616 | 0.526782384 | 0.108070378 | False | 0.822827939 | 0.286201022 | 0.010221465 | Q2,S2,S4,S1 |
| meta_core | e176 | global_t010_subject_t020 | 613 | 0.472830364 | 0.472928501 | 0.527071499 | 0.109217779 | False | 0.831973899 | 0.285481240 | 0.011419250 | Q2,S1,S4,Q3 |
| meta_public_axis | e144 | global_t010 | 143 | 0.611682447 | 0.610713369 | 0.389286631 | -0.464342186 | True | 0.489510490 | 0.237762238 | 0.020979021 | Q3,Q1,S3,S2 |
| meta_public_axis | e144 | global_t010_subject_t010 | 171 | 0.605659921 | 0.605659921 | 0.394340079 | -0.443852033 | True | 0.508771930 | 0.245614035 | 0.017543860 | Q3,Q1,S3,S2 |
| meta_public_axis | e144 | global_t010_subject_t020 | 178 | 0.608947972 | 0.608947972 | 0.391052028 | -0.457517147 | True | 0.494382022 | 0.230337079 | 0.016853933 | Q3,Q1,S3,S2 |
| meta_public_axis | e154 | global_t010 | 292 | 0.611908741 | 0.611908741 | 0.388091259 | -0.470401484 | True | 0.472602740 | 0.311643836 | 0.017123288 | Q3,Q1,S3,S2 |
| meta_public_axis | e154 | global_t010_subject_t010 | 271 | 0.610389364 | 0.610389364 | 0.389610636 | -0.462992556 | True | 0.487084871 | 0.309963100 | 0.014760148 | Q3,Q1,S3,S4 |
| meta_public_axis | e154 | global_t010_subject_t020 | 285 | 0.612509829 | 0.612509829 | 0.387490171 | -0.473024551 | True | 0.470175439 | 0.312280702 | 0.014035088 | Q3,Q1,S3,S2 |
| meta_public_axis | e176 | global_t010 | 605 | 0.627876924 | 0.627876924 | 0.372123076 | -0.542584403 | True | 0.826446281 | 0.272727273 | 0.011570248 | Q2,S1,S3,S4 |
| meta_public_axis | e176 | global_t010_subject_t010 | 587 | 0.626669446 | 0.625237099 | 0.374762901 | -0.531969076 | True | 0.822827939 | 0.286201022 | 0.010221465 | Q2,S2,S4,S1 |
| meta_public_axis | e176 | global_t010_subject_t020 | 613 | 0.627505535 | 0.627425005 | 0.372574995 | -0.540660832 | True | 0.831973899 | 0.285481240 | 0.011419250 | Q2,S1,S4,Q3 |
| meta_public_axis_plus_support_label | e144 | global_t010 | 143 | 0.611606090 | 0.610558207 | 0.389441793 | -0.463827663 | True | 0.489510490 | 0.237762238 | 0.020979021 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_support_label | e144 | global_t010_subject_t010 | 171 | 0.605581609 | 0.605581609 | 0.394418391 | -0.443635742 | True | 0.508771930 | 0.245614035 | 0.017543860 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_support_label | e144 | global_t010_subject_t020 | 178 | 0.608887719 | 0.608887719 | 0.391112281 | -0.457356166 | True | 0.494382022 | 0.230337079 | 0.016853933 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_support_label | e154 | global_t010 | 292 | 0.611873536 | 0.611873536 | 0.388126464 | -0.470328585 | True | 0.472602740 | 0.311643836 | 0.017123288 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_support_label | e154 | global_t010_subject_t010 | 271 | 0.610384499 | 0.610384499 | 0.389615501 | -0.463097264 | True | 0.487084871 | 0.309963100 | 0.014760148 | Q3,Q1,S3,S4 |
| meta_public_axis_plus_support_label | e154 | global_t010_subject_t020 | 285 | 0.612508230 | 0.612508230 | 0.387491770 | -0.473105380 | True | 0.470175439 | 0.312280702 | 0.014035088 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_support_label | e176 | global_t010 | 605 | 0.627600357 | 0.627600357 | 0.372399643 | -0.541731250 | True | 0.826446281 | 0.272727273 | 0.011570248 | Q2,S1,S3,S4 |
| meta_public_axis_plus_support_label | e176 | global_t010_subject_t010 | 587 | 0.626242570 | 0.624837475 | 0.375162525 | -0.530573818 | True | 0.822827939 | 0.286201022 | 0.010221465 | Q2,S2,S4,S1 |
| meta_public_axis_plus_support_label | e176 | global_t010_subject_t020 | 613 | 0.627116495 | 0.627037915 | 0.372962085 | -0.539324644 | True | 0.831973899 | 0.285481240 | 0.011419250 | Q2,S1,S4,Q3 |
| meta_public_axis_plus_swing | e144 | global_t010 | 143 | 0.492672302 | 0.497124843 | 0.502875157 | 0.018335614 | False | 0.489510490 | 0.237762238 | 0.020979021 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_swing | e144 | global_t010_subject_t010 | 171 | 0.486702965 | 0.486702965 | 0.513297035 | 0.060237420 | False | 0.508771930 | 0.245614035 | 0.017543860 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_swing | e144 | global_t010_subject_t020 | 178 | 0.488531840 | 0.488531840 | 0.511468160 | 0.053902713 | False | 0.494382022 | 0.230337079 | 0.016853933 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_swing | e154 | global_t010 | 292 | 0.468301311 | 0.468301311 | 0.531698689 | 0.167225523 | False | 0.472602740 | 0.311643836 | 0.017123288 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_swing | e154 | global_t010_subject_t010 | 271 | 0.469362024 | 0.469362024 | 0.530637976 | 0.159657063 | False | 0.487084871 | 0.309963100 | 0.014760148 | Q3,Q1,S3,S4 |
| meta_public_axis_plus_swing | e154 | global_t010_subject_t020 | 285 | 0.468166816 | 0.468166816 | 0.531833184 | 0.167955611 | False | 0.470175439 | 0.312280702 | 0.014035088 | Q3,Q1,S3,S2 |
| meta_public_axis_plus_swing | e176 | global_t010 | 605 | 0.183015295 | 0.183015295 | 0.816984705 | 1.610323819 | False | 0.826446281 | 0.272727273 | 0.011570248 | Q2,S1,S3,S4 |
| meta_public_axis_plus_swing | e176 | global_t010_subject_t010 | 587 | 0.178999699 | 0.183787651 | 0.816212349 | 1.612077625 | False | 0.822827939 | 0.286201022 | 0.010221465 | Q2,S2,S4,S1 |
| meta_public_axis_plus_swing | e176 | global_t010_subject_t020 | 613 | 0.181893848 | 0.182265168 | 0.817734832 | 1.619108830 | False | 0.831973899 | 0.285481240 | 0.011419250 | Q2,S1,S4,Q3 |

## Interpretation

- A usable branch selector must first recover known public transition signs
  when a whole pair or family is held out.
- Feature sets that include `support_label` are intentionally listed as a
  target-prior stress, but they are weaker evidence than support-label-free
  metadata because they can learn label-direction quirks.
- If a feature set has weak LOO/LOFO accuracy, its pressure-branch preference is
  not action-grade even when it selects a live branch.

## Decision

No submission. Use this audit to decide whether the next local step should be a
stronger non-visible decisive-cell representation or a public-feedback decoder
for a chosen worldview.
