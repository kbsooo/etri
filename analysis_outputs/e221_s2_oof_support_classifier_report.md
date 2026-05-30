# E221 S2 OOF Support Classifier

## Question

Can E216's S2 masked-family JEPA movement be rescued by a train/OOF-reproducible classifier that predicts where the movement helps?

## Setup

- Train support-label rate: `0.551111`.
- Full E216 S2 target OOF delta versus stage2: `-0.004370425`.
- Public miss to explain: E216-E95 `+0.0009951790`.

## Support Classifier Stress

| model | split | auc | logloss | brier | corr_benefit | mean_prob | n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_shallow | rowcontig5 | 0.717482434 | 0.615115856 | 0.212470531 | -0.000190009 | 0.559474487 | 450 |
| gb_shallow | rowcontig5 | 0.695045513 | 0.631933274 | 0.220132264 | -0.039118251 | 0.556847404 | 450 |
| lr_l1_c0p05 | rowcontig5 | 0.628094059 | 0.658986472 | 0.233013415 | -0.042910061 | 0.497440638 | 450 |
| lr_l2_c0p15 | rowcontig5 | 0.579687001 | 0.984940761 | 0.308507433 | -0.039119169 | 0.439704663 | 450 |
| gb_shallow | stratified5 | 0.748103641 | 0.603511436 | 0.207021624 | 0.011504097 | 0.553347854 | 450 |
| hgb_shallow | stratified5 | 0.740438358 | 0.598239150 | 0.204897958 | 0.002722817 | 0.560972655 | 450 |
| lr_l1_c0p05 | stratified5 | 0.637116736 | 0.656387533 | 0.231771246 | -0.075782531 | 0.501674722 | 450 |
| lr_l2_c0p15 | stratified5 | 0.625998084 | 0.750774539 | 0.258643771 | -0.017545504 | 0.511650629 | 450 |
| hgb_shallow | subject5 | 0.696682370 | 0.630024178 | 0.220409181 | -0.003371558 | 0.565279358 | 450 |
| gb_shallow | subject5 | 0.690853561 | 0.638790669 | 0.223898099 | -0.020323862 | 0.568931387 | 450 |
| lr_l1_c0p05 | subject5 | 0.604858671 | 0.667259861 | 0.237028063 | -0.048553765 | 0.496771150 | 450 |
| lr_l2_c0p15 | subject5 | 0.588330406 | 0.848031099 | 0.286295602 | -0.024138917 | 0.504513966 | 450 |
| hgb_shallow | subject_loo | 0.713729639 | 0.620669236 | 0.215173853 | 0.000170632 | 0.562346376 | 450 |
| gb_shallow | subject_loo | 0.686821303 | 0.638359243 | 0.223450584 | -0.028059397 | 0.560579152 | 450 |
| lr_l2_c0p15 | subject_loo | 0.595516608 | 0.830539191 | 0.283420879 | -0.002417569 | 0.500532519 | 450 |
| lr_l1_c0p05 | subject_loo | 0.563737624 | 0.672779211 | 0.239552628 | -0.045170419 | 0.498031598 | 450 |

## Best OOF Gates

| model_split | gate | selected_rows | support_precision | support_recall | s2_target_delta | overall_delta | subject_win_rate | oof_gate_pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hgb_shallow__subject_loo | top250 | 250 | 0.704000000 | 0.709677419 | -0.004050232 | -0.000578605 | 0.700000000 | True |
| hgb_shallow__rowcontig5 | prob_ge_0p45 | 309 | 0.669902913 | 0.834677419 | -0.004037587 | -0.000576798 | 0.700000000 | True |
| hgb_shallow__rowcontig5 | prob_ge_0p4 | 347 | 0.642651297 | 0.899193548 | -0.004059742 | -0.000579963 | 0.600000000 | True |
| hgb_shallow__subject_loo | prob_ge_0p55 | 251 | 0.701195219 | 0.709677419 | -0.003865314 | -0.000552188 | 0.700000000 | True |
| hgb_shallow__stratified5 | prob_ge_0p5 | 287 | 0.707317073 | 0.818548387 | -0.003689747 | -0.000527107 | 0.700000000 | True |
| lr_l2_c0p15__stratified5 | prob_ge_0p45 | 254 | 0.641732283 | 0.657258065 | -0.003506732 | -0.000500962 | 0.700000000 | True |
| gb_shallow__subject5 | prob_ge_0p45 | 360 | 0.611111111 | 0.887096774 | -0.003518437 | -0.000502634 | 0.700000000 | True |
| hgb_shallow__stratified5 | prob_ge_0p55 | 244 | 0.725409836 | 0.713709677 | -0.003243299 | -0.000463328 | 0.800000000 | True |
| gb_shallow__rowcontig5 | prob_ge_0p4 | 365 | 0.621917808 | 0.915322581 | -0.003545675 | -0.000506525 | 0.600000000 | True |
| hgb_shallow__subject5 | prob_ge_0p7 | 112 | 0.803571429 | 0.362903226 | -0.003086569 | -0.000440938 | 0.800000000 | True |
| hgb_shallow__stratified5 | prob_ge_0p6 | 217 | 0.746543779 | 0.653225806 | -0.003111149 | -0.000444450 | 0.900000000 | True |
| hgb_shallow__subject_loo | prob_ge_0p5 | 290 | 0.675862069 | 0.790322581 | -0.003317196 | -0.000473885 | 0.700000000 | True |
| lr_l2_c0p15__stratified5 | top250 | 250 | 0.640000000 | 0.645161290 | -0.003254436 | -0.000464919 | 0.700000000 | True |
| hgb_shallow__rowcontig5 | prob_ge_0p55 | 242 | 0.702479339 | 0.685483871 | -0.003243631 | -0.000463376 | 0.600000000 | True |
| hgb_shallow__subject_loo | top100 | 100 | 0.800000000 | 0.322580645 | -0.002842503 | -0.000406072 | 0.900000000 | True |
| hgb_shallow__stratified5 | top250 | 250 | 0.728000000 | 0.733870968 | -0.003038730 | -0.000434104 | 0.700000000 | True |
| gb_shallow__subject5 | top175 | 175 | 0.748571429 | 0.528225806 | -0.002855601 | -0.000407943 | 0.800000000 | True |
| gb_shallow__stratified5 | score_top80 | 80 | 0.625000000 | 0.201612903 | -0.003004577 | -0.000429225 | 0.600000000 | True |
| hgb_shallow__subject5 | prob_ge_0p65 | 164 | 0.743902439 | 0.491935484 | -0.002817304 | -0.000402472 | 0.700000000 | True |
| hgb_shallow__subject5 | score_top80 | 80 | 0.612500000 | 0.197580645 | -0.002962059 | -0.000423151 | 0.600000000 | True |
| lr_l2_c0p15__subject5 | top125 | 125 | 0.712000000 | 0.358870968 | -0.002714825 | -0.000387832 | 0.900000000 | True |
| hgb_shallow__subject5 | top175 | 175 | 0.742857143 | 0.524193548 | -0.002752936 | -0.000393277 | 0.800000000 | True |
| lr_l2_c0p15__subject_loo | top100 | 100 | 0.760000000 | 0.306451613 | -0.002655704 | -0.000379386 | 0.900000000 | True |
| gb_shallow__stratified5 | prob_ge_0p4 | 364 | 0.626373626 | 0.919354839 | -0.003100427 | -0.000442918 | 0.600000000 | True |
| gb_shallow__stratified5 | prob_ge_0p45 | 328 | 0.655487805 | 0.866935484 | -0.003036886 | -0.000433841 | 0.600000000 | True |
| hgb_shallow__subject5 | prob_ge_0p45 | 326 | 0.625766871 | 0.822580645 | -0.003049531 | -0.000435647 | 0.600000000 | True |
| hgb_shallow__subject_loo | prob_ge_0p7 | 112 | 0.785714286 | 0.354838710 | -0.002617768 | -0.000373967 | 0.800000000 | True |
| hgb_shallow__subject_loo | top175 | 175 | 0.742857143 | 0.524193548 | -0.002662259 | -0.000380323 | 0.800000000 | True |
| hgb_shallow__subject_loo | prob_ge_0p65 | 165 | 0.751515152 | 0.500000000 | -0.002619293 | -0.000374185 | 0.800000000 | True |
| hgb_shallow__stratified5 | prob_ge_0p4 | 335 | 0.647761194 | 0.875000000 | -0.002870107 | -0.000410015 | 0.700000000 | True |
| hgb_shallow__subject_loo | top150 | 150 | 0.753333333 | 0.455645161 | -0.002607477 | -0.000372497 | 0.700000000 | True |
| hgb_shallow__subject5 | prob_ge_0p55 | 259 | 0.679536680 | 0.709677419 | -0.002739500 | -0.000391357 | 0.700000000 | True |
| lr_l2_c0p15__rowcontig5 | top100 | 100 | 0.750000000 | 0.302419355 | -0.002475154 | -0.000353593 | 0.900000000 | True |
| lr_l2_c0p15__rowcontig5 | prob_ge_0p7 | 119 | 0.697478992 | 0.334677419 | -0.002556103 | -0.000365158 | 0.800000000 | True |
| gb_shallow__subject_loo | score_top125 | 125 | 0.568000000 | 0.286290323 | -0.002755509 | -0.000393644 | 0.600000000 | True |
| lr_l2_c0p15__subject_loo | score_top80 | 80 | 0.575000000 | 0.185483871 | -0.002664889 | -0.000380698 | 0.700000000 | True |
| hgb_shallow__subject_loo | score_top40 | 40 | 0.675000000 | 0.108870968 | -0.002614311 | -0.000373473 | 0.600000000 | True |
| hgb_shallow__subject_loo | prob_ge_0p45 | 321 | 0.647975078 | 0.838709677 | -0.002780561 | -0.000397223 | 0.600000000 | True |
| lr_l2_c0p15__stratified5 | prob_ge_0p5 | 234 | 0.641025641 | 0.604838710 | -0.002644744 | -0.000377821 | 0.700000000 | True |
| hgb_shallow__stratified5 | top200 | 200 | 0.750000000 | 0.604838710 | -0.002463134 | -0.000351876 | 0.800000000 | True |

## Submission-Side Tail Stress

| model_split | gate | scale | selected_rows_sub | expected_focus | adverse_delta | adverse_over_observed_miss | support_prob_focus_weighted | top1_swing_share | oof_gate_pass | submission_gate_pass | joint_gate_pass | submission_file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lr_l2_c0p15__subject_loo | score_top40 | 0.350000000 | 40 | -0.000048509 | 0.000771214 | 0.774949591 | 0.489613713 | 0.029982543 | True | False | False |  |
| lr_l2_c0p15__subject5 | score_top40 | 0.350000000 | 40 | -0.000048509 | 0.000771214 | 0.774949591 | 0.489613713 | 0.029982543 | False | False | False |  |
| hgb_shallow__subject_loo | score_top40 | 0.350000000 | 40 | 0.000047397 | 0.000877068 | 0.881317216 | 0.493474314 | 0.029165548 | True | False | False |  |
| lr_l2_c0p15__subject5 | top75 | 0.350000000 | 75 | 0.000021951 | 0.000914900 | 0.919332055 | 0.582824232 | 0.031605365 | True | False | False |  |
| lr_l2_c0p15__subject_loo | top75 | 0.350000000 | 75 | 0.000021951 | 0.000914900 | 0.919332055 | 0.582824232 | 0.031605365 | True | False | False |  |
| lr_l2_c0p15__subject5 | prob_ge_0p8 | 0.350000000 | 67 | 0.000039264 | 0.000843265 | 0.847349758 | 0.590770295 | 0.035580480 | True | False | False |  |
| hgb_shallow__rowcontig5 | score_top20 | 0.350000000 | 20 | 0.000027295 | 0.000447724 | 0.449893020 | 0.480973723 | 0.056097135 | True | False | False |  |
| lr_l2_c0p15__subject_loo | prob_ge_0p75 | 0.350000000 | 86 | 0.000016646 | 0.001021085 | 1.026031314 | 0.577559444 | 0.027843440 | True | False | False |  |
| lr_l2_c0p15__rowcontig5 | prob_ge_0p75 | 0.350000000 | 86 | 0.000016646 | 0.001021085 | 1.026031314 | 0.577559444 | 0.027843440 | True | False | False |  |
| lr_l2_c0p15__rowcontig5 | prob_ge_0p8 | 0.350000000 | 67 | 0.000039264 | 0.000843265 | 0.847349758 | 0.590770295 | 0.035580480 | True | False | False |  |
| hgb_shallow__rowcontig5 | score_top20 | 0.500000000 | 20 | 0.000043978 | 0.000644590 | 0.647712836 | 0.480973723 | 0.056097135 | True | False | False |  |
| lr_l2_c0p15__subject5 | prob_ge_0p75 | 0.350000000 | 86 | 0.000016646 | 0.001021085 | 1.026031314 | 0.577559444 | 0.027843440 | True | False | False |  |
| lr_l2_c0p15__rowcontig5 | top75 | 0.350000000 | 75 | 0.000021951 | 0.000914900 | 0.919332055 | 0.582824232 | 0.031605365 | True | False | False |  |
| hgb_shallow__subject5 | prob_ge_0p7 | 0.350000000 | 54 | 0.000155806 | 0.001021775 | 1.026725153 | 0.598751093 | 0.033480638 | True | False | False |  |
| hgb_shallow__rowcontig5 | score_top20 | 0.750000000 | 20 | 0.000078414 | 0.000979333 | 0.984077285 | 0.480973723 | 0.056097135 | True | False | False |  |
| hgb_shallow__subject_loo | score_top20 | 0.350000000 | 20 | 0.000027295 | 0.000447724 | 0.449893020 | 0.480973723 | 0.056097135 | True | False | False |  |
| lr_l2_c0p15__subject_loo | top50 | 0.350000000 | 50 | 0.000036869 | 0.000626219 | 0.629252506 | 0.608958186 | 0.050033898 | True | False | False |  |
| lr_l2_c0p15__subject5 | score_top20 | 0.350000000 | 20 | 0.000005728 | 0.000423485 | 0.425536470 | 0.478406929 | 0.055662749 | False | False | False |  |
| lr_l2_c0p15__subject5 | top50 | 0.350000000 | 50 | 0.000036869 | 0.000626219 | 0.629252506 | 0.608958186 | 0.050033898 | True | False | False |  |
| lr_l2_c0p15__subject_loo | score_top20 | 0.350000000 | 20 | 0.000005728 | 0.000423485 | 0.425536470 | 0.478406929 | 0.055662749 | False | False | False |  |
| lr_l1_c0p05__subject_loo | top50 | 0.500000000 | 50 | -0.000049959 | 0.000873192 | 0.877422101 | 0.652582215 | 0.048900629 | False | True | False |  |
| hgb_shallow__stratified5 | score_top20 | 0.350000000 | 20 | 0.000027295 | 0.000447724 | 0.449893020 | 0.480973723 | 0.056097135 | False | False | False |  |
| lr_l2_c0p15__subject_loo | top40 | 0.350000000 | 40 | 0.000026200 | 0.000553848 | 0.556531180 | 0.616014785 | 0.056532272 | True | False | False |  |
| hgb_shallow__subject5 | score_top20 | 0.350000000 | 20 | 0.000027295 | 0.000447724 | 0.449893020 | 0.480973723 | 0.056097135 | True | False | False |  |
| hgb_shallow__subject_loo | score_top20 | 0.500000000 | 20 | 0.000043978 | 0.000644590 | 0.647712836 | 0.480973723 | 0.056097135 | True | False | False |  |
| lr_l2_c0p15__subject5 | score_top20 | 0.500000000 | 20 | 0.000013060 | 0.000609856 | 0.612810185 | 0.478406929 | 0.055662749 | False | False | False |  |
| lr_l2_c0p15__subject_loo | top50 | 0.500000000 | 50 | 0.000054968 | 0.000896896 | 0.901241021 | 0.608958186 | 0.050033898 | True | False | False |  |
| lr_l2_c0p15__subject_loo | score_top20 | 0.500000000 | 20 | 0.000013060 | 0.000609856 | 0.612810185 | 0.478406929 | 0.055662749 | False | False | False |  |
| lr_l1_c0p05__subject_loo | top50 | 0.350000000 | 50 | -0.000036900 | 0.000609306 | 0.612257522 | 0.652582215 | 0.048900629 | False | True | False |  |
| lr_l2_c0p15__subject5 | top40 | 0.350000000 | 40 | 0.000026200 | 0.000553848 | 0.556531180 | 0.616014785 | 0.056532272 | True | False | False |  |
| gb_shallow__subject5 | prob_ge_0p7 | 0.350000000 | 32 | 0.000094281 | 0.000545215 | 0.547856067 | 0.654360653 | 0.057543834 | True | False | False |  |
| lr_l2_c0p15__subject5 | top50 | 0.500000000 | 50 | 0.000054968 | 0.000896896 | 0.901241021 | 0.608958186 | 0.050033898 | True | False | False |  |
| lr_l2_c0p15__subject_loo | top40 | 0.500000000 | 40 | 0.000039563 | 0.000793346 | 0.797189549 | 0.616014785 | 0.056532272 | True | False | False |  |
| lr_l2_c0p15__stratified5 | score_top20 | 0.350000000 | 20 | 0.000005728 | 0.000423485 | 0.425536470 | 0.478406929 | 0.055662749 | False | False | False |  |
| hgb_shallow__subject5 | score_top40 | 0.350000000 | 40 | 0.000047397 | 0.000877068 | 0.881317216 | 0.493474314 | 0.029165548 | True | False | False |  |
| hgb_shallow__stratified5 | score_top20 | 0.500000000 | 20 | 0.000043978 | 0.000644590 | 0.647712836 | 0.480973723 | 0.056097135 | False | False | False |  |
| hgb_shallow__subject5 | score_top20 | 0.500000000 | 20 | 0.000043978 | 0.000644590 | 0.647712836 | 0.480973723 | 0.056097135 | True | False | False |  |
| lr_l2_c0p15__subject5 | score_top20 | 0.750000000 | 20 | 0.000031790 | 0.000926983 | 0.931473572 | 0.478406929 | 0.055662749 | False | False | False |  |
| lr_l2_c0p15__stratified5 | score_top20 | 0.500000000 | 20 | 0.000013060 | 0.000609856 | 0.612810185 | 0.478406929 | 0.055662749 | False | False | False |  |
| lr_l2_c0p15__subject_loo | score_top20 | 0.750000000 | 20 | 0.000031790 | 0.000926983 | 0.931473572 | 0.478406929 | 0.055662749 | False | False | False |  |

## Decision

- No E221 gate passed both OOF support reproduction and submission-side tail capacity stress.
- This rejects the simplest trainable rescue of E216 S2. The masked-family JEPA representation remains diagnostic, but S2 probability translation should stay closed until a different target representation or non-S2 translator appears.
