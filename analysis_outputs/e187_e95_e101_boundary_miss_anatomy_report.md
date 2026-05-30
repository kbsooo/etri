# E187 E95/E101 Boundary Miss Anatomy

## Question

E186 repaired reciprocal geometry and made E176 look attractive, but the known
public sensor now says E101 (`0.576300366`) is still slightly worse than E95
(`0.5762913298`). Is the E95/E101 miss caused by a removable feature-family
shortcut, or by the same support structure that powers the E176 branch?

## Result In One Sentence

No file-LOO variant simultaneously fixes the E95/E101 boundary, keeps frontier stress above 0.80, and preserves the E176 branch.

## File-LOO Variant Stress

| variant | group_col | n_cols | accuracy | auc | logloss | frontier_accuracy | micro_accuracy | e95_edge_accuracy | e95_e101_accuracy | e95_prob_mean | e101_prob_mean | e176_favorable_rate | e176_prob_mean | action_grade_boundary_branch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | file | 280 | 0.795454545 | 0.880567034 | 0.496629149 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False |
| shape_axis_no_support | file | 328 | 0.795454545 | 0.880567034 | 0.496629149 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False |
| shape_support_drop_subject | file | 432 | 0.803030303 | 0.841023875 | 0.682062636 | 0.900000000 | 0.812500000 | 0.857142857 | 0.000000000 | 0.016390997 | 0.983609003 | 1.000000000 | 0.723510417 | False |
| shape_support_drop_global | file | 432 | 0.795454545 | 0.833735078 | 0.739277447 | 0.900000000 | 0.812500000 | 0.857142857 | 0.000000000 | 0.005875825 | 0.994124175 | 1.000000000 | 0.759663393 | False |
| shape_support_drop_top1 | file | 399 | 0.795454545 | 0.841769972 | 0.717374489 | 0.900000000 | 0.812500000 | 0.857142857 | 0.000000000 | 0.006588381 | 0.993411619 | 1.000000000 | 0.967894654 | False |
| shape_support_drop_top16_33 | file | 412 | 0.856060606 | 0.883551423 | 0.535496348 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.003879323 | 0.996120677 | 1.000000000 | 0.929906828 | False |
| shape_support_no_q2s3_targets | file | 408 | 0.825757576 | 0.879648760 | 0.541021539 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.010169625 | 0.989830375 | 1.000000000 | 0.834671515 | False |
| shape_support | file | 456 | 0.795454545 | 0.834768136 | 0.723760713 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.006929326 | 0.993070674 | 1.000000000 | 0.816469448 | False |
| shape_support_public_axis | file | 504 | 0.795454545 | 0.834768136 | 0.723760713 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.006929326 | 0.993070674 | 1.000000000 | 0.816469448 | False |
| shape_support_drop_nearest | file | 432 | 0.795454545 | 0.834653352 | 0.714977201 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.005357488 | 0.994642512 | 1.000000000 | 0.837251378 | False |
| shape_support_drop_focus | file | 432 | 0.795454545 | 0.833505510 | 0.714650728 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.007721379 | 0.992278621 | 1.000000000 | 0.788146821 | False |
| shape_support_drop_flank | file | 424 | 0.795454545 | 0.836030762 | 0.707271819 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.011671469 | 0.988328531 | 1.000000000 | 0.784092245 | False |
| shape_support_drop_visible | file | 432 | 0.795454545 | 0.834882920 | 0.709960365 | 0.866666667 | 0.812500000 | 0.857142857 | 0.000000000 | 0.010171495 | 0.989828505 | 1.000000000 | 0.782051777 | False |
| shape_support_drop_between | file | 336 | 0.750000000 | 0.724575298 | 1.155452499 | 0.766666667 | 0.687500000 | 0.714285714 | 0.000000000 | 0.002248376 | 0.997751624 | 1.000000000 | 0.940576942 | False |
| shape_support_drop_prior_split | file | 448 | 0.825757576 | 0.869203398 | 0.614361818 | 0.766666667 | 0.625000000 | 0.642857143 | 0.000000000 | 0.003986338 | 0.996013662 | 1.000000000 | 0.911637570 | False |
| shape_support_keep_hard_only | file | 160 | 0.787878788 | 0.813131313 | 0.638481202 | 0.733333333 | 0.625000000 | 0.642857143 | 0.000000000 | 0.050400189 | 0.949599811 | 1.000000000 | 0.956273490 | False |
| shape_support_keep_mean_only | file | 192 | 0.787878788 | 0.750344353 | 0.934710489 | 0.800000000 | 0.687500000 | 0.714285714 | 0.000000000 | 0.004501604 | 0.995498396 | 0.000000000 | 0.367678655 | False |

## Pair-LOO Variant Stress

| variant | group_col | n_cols | accuracy | auc | logloss | frontier_accuracy | micro_accuracy | e95_edge_accuracy | e95_e101_accuracy | e95_prob_mean | e101_prob_mean | e176_favorable_rate | e176_prob_mean | action_grade_boundary_branch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | pair | 280 | 0.969696970 | 0.995408632 | 0.117158497 | 0.933333333 | 0.875000000 | 1.000000000 | 1.000000000 | 0.819695770 | 0.180304230 | 1.000000000 | 0.925898875 | False |
| shape_axis_no_support | pair | 328 | 0.969696970 | 0.995408632 | 0.117158497 | 0.933333333 | 0.875000000 | 1.000000000 | 1.000000000 | 0.819695770 | 0.180304230 | 1.000000000 | 0.925898875 | False |
| shape_support_drop_global | pair | 432 | 0.969696970 | 0.977502296 | 0.140828997 | 0.933333333 | 0.750000000 | 0.857142857 | 0.000000000 | 0.006377481 | 0.993622519 | 1.000000000 | 0.759663393 | False |
| shape_support_drop_subject | pair | 432 | 0.969696970 | 0.983011938 | 0.124366524 | 0.933333333 | 0.750000000 | 0.857142857 | 0.000000000 | 0.016912441 | 0.983087559 | 1.000000000 | 0.723510417 | False |
| shape_support_drop_top1 | pair | 399 | 0.969696970 | 0.978879706 | 0.135868692 | 0.933333333 | 0.750000000 | 0.857142857 | 0.000000000 | 0.006308629 | 0.993691371 | 1.000000000 | 0.967894654 | False |
| shape_support | pair | 456 | 0.954545455 | 0.977731864 | 0.141430550 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.007317889 | 0.992682111 | 1.000000000 | 0.816469448 | False |
| shape_support_public_axis | pair | 504 | 0.954545455 | 0.977731864 | 0.141430550 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.007317889 | 0.992682111 | 1.000000000 | 0.816469448 | False |
| shape_support_drop_nearest | pair | 432 | 0.954545455 | 0.975436180 | 0.146519913 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.005621590 | 0.994378410 | 1.000000000 | 0.837251378 | False |
| shape_support_drop_focus | pair | 432 | 0.954545455 | 0.977731864 | 0.139922669 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.007939325 | 0.992060675 | 1.000000000 | 0.788146821 | False |
| shape_support_drop_flank | pair | 424 | 0.954545455 | 0.980486685 | 0.133386979 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.012419855 | 0.987580145 | 1.000000000 | 0.784092245 | False |
| shape_support_drop_visible | pair | 432 | 0.954545455 | 0.980486685 | 0.135326253 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.010749034 | 0.989250966 | 1.000000000 | 0.782051777 | False |
| shape_support_drop_top16_33 | pair | 412 | 0.954545455 | 0.975436180 | 0.152852696 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.004157761 | 0.995842239 | 1.000000000 | 0.929906828 | False |
| shape_support_no_q2s3_targets | pair | 408 | 0.954545455 | 0.980027548 | 0.146299109 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.011490789 | 0.988509211 | 1.000000000 | 0.834671515 | False |
| shape_support_drop_prior_split | pair | 448 | 0.939393939 | 0.971992654 | 0.170658079 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.004072661 | 0.995927339 | 1.000000000 | 0.911637570 | False |
| shape_support_drop_between | pair | 336 | 0.939393939 | 0.966942149 | 0.207998559 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.002276732 | 0.997723268 | 1.000000000 | 0.940576942 | False |
| shape_support_keep_hard_only | pair | 160 | 0.909090909 | 0.962350781 | 0.248616612 | 0.866666667 | 0.750000000 | 0.857142857 | 0.000000000 | 0.046636068 | 0.953363932 | 1.000000000 | 0.956273490 | False |
| shape_support_keep_mean_only | pair | 192 | 0.924242424 | 0.962580349 | 0.269548066 | 0.866666667 | 0.625000000 | 0.714285714 | 0.000000000 | 0.003781305 | 0.996218695 | 0.000000000 | 0.367678655 | False |

## Exact E95/E101 Boundary Predictions

| variant | group_col | heldout | new_file | base_file | actual_delta | prob_new_better | correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| shape_axis_no_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.238112055 | True |
| shape_axis_no_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.761887945 | True |
| shape_axis_no_support | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.236533826 | True |
| shape_axis_no_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.763466174 | True |
| shape_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.238112055 | True |
| shape_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.761887945 | True |
| shape_only | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.236533826 | True |
| shape_only | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.763466174 | True |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.991683161 | False |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.008316839 | False |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.994458188 | False |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.005541812 | False |
| shape_support_drop_between | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.997601513 | False |
| shape_support_drop_between | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.002398487 | False |
| shape_support_drop_between | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.997901735 | False |
| shape_support_drop_between | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.002098265 | False |
| shape_support_drop_flank | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.986318692 | False |
| shape_support_drop_flank | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.013681308 | False |
| shape_support_drop_flank | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.990338371 | False |
| shape_support_drop_flank | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.009661629 | False |
| shape_support_drop_focus | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.990808251 | False |
| shape_support_drop_focus | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.009191749 | False |
| shape_support_drop_focus | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.993748990 | False |
| shape_support_drop_focus | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.006251010 | False |
| shape_support_drop_global | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992834277 | False |
| shape_support_drop_global | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007165723 | False |
| shape_support_drop_global | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995414074 | False |
| shape_support_drop_global | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004585926 | False |
| shape_support_drop_nearest | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.993620818 | False |
| shape_support_drop_nearest | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.006379182 | False |
| shape_support_drop_nearest | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995664206 | False |
| shape_support_drop_nearest | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004335794 | False |
| shape_support_drop_prior_split | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995246709 | False |
| shape_support_drop_prior_split | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004753291 | False |
| shape_support_drop_prior_split | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.996780614 | False |
| shape_support_drop_prior_split | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.003219386 | False |
| shape_support_drop_subject | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.981613532 | False |
| shape_support_drop_subject | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.018386468 | False |
| shape_support_drop_subject | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.985604474 | False |
| shape_support_drop_subject | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.014395526 | False |
| shape_support_drop_top1 | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992131052 | False |
| shape_support_drop_top1 | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007868948 | False |
| shape_support_drop_top1 | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.994692186 | False |
| shape_support_drop_top1 | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.005307814 | False |
| shape_support_drop_top16_33 | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995141392 | False |
| shape_support_drop_top16_33 | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004858608 | False |
| shape_support_drop_top16_33 | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.997099962 | False |
| shape_support_drop_top16_33 | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.002900038 | False |
| shape_support_drop_visible | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.988020887 | False |
| shape_support_drop_visible | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.011979113 | False |
| shape_support_drop_visible | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.991636122 | False |
| shape_support_drop_visible | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.008363878 | False |
| shape_support_keep_hard_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.949375824 | False |
| shape_support_keep_hard_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.050624176 | False |
| shape_support_keep_hard_only | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.949823799 | False |
| shape_support_keep_hard_only | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.050176201 | False |
| shape_support_keep_mean_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995715062 | False |
| shape_support_keep_mean_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004284938 | False |
| shape_support_keep_mean_only | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995281730 | False |
| shape_support_keep_mean_only | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004718270 | False |
| shape_support_no_q2s3_targets | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.987082004 | False |
| shape_support_no_q2s3_targets | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.012917996 | False |
| shape_support_no_q2s3_targets | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992578747 | False |
| shape_support_no_q2s3_targets | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007421253 | False |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.991683161 | False |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.008316839 | False |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.994458188 | False |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.005541812 | False |
| shape_axis_no_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.180304230 | True |
| shape_axis_no_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.819695770 | True |
| shape_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.180304230 | True |
| shape_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.819695770 | True |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992682111 | False |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007317889 | False |
| shape_support_drop_between | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.997723268 | False |
| shape_support_drop_between | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.002276732 | False |
| shape_support_drop_flank | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.987580145 | False |
| shape_support_drop_flank | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.012419855 | False |
| shape_support_drop_focus | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992060675 | False |
| shape_support_drop_focus | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007939325 | False |
| shape_support_drop_global | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.993622519 | False |
| shape_support_drop_global | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.006377481 | False |
| shape_support_drop_nearest | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.994378410 | False |
| shape_support_drop_nearest | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.005621590 | False |
| shape_support_drop_prior_split | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995927339 | False |
| shape_support_drop_prior_split | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004072661 | False |
| shape_support_drop_subject | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.983087559 | False |
| shape_support_drop_subject | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.016912441 | False |
| shape_support_drop_top1 | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.993691371 | False |
| shape_support_drop_top1 | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.006308629 | False |
| shape_support_drop_top16_33 | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.995842239 | False |
| shape_support_drop_top16_33 | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.004157761 | False |
| shape_support_drop_visible | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.989250966 | False |
| shape_support_drop_visible | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.010749034 | False |
| shape_support_keep_hard_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.953363932 | False |
| shape_support_keep_hard_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.046636068 | False |
| shape_support_keep_mean_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.996218695 | False |
| shape_support_keep_mean_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.003781305 | False |
| shape_support_no_q2s3_targets | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.988509211 | False |
| shape_support_no_q2s3_targets | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.011490789 | False |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | 0.000009036 | 0.992682111 | False |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | -0.000009036 | 0.007317889 | False |

## Pressure-Branch Summary

| variant | candidate | prefers_favorable_min_rate | prob_mean | prob_min | prob_max |
| --- | --- | --- | --- | --- | --- |
| shape_axis_no_support | e144 | 0.000000000 | 0.016426756 | 0.005881782 | 0.026081579 |
| shape_axis_no_support | e154 | 0.000000000 | 0.001610088 | 0.001369363 | 0.001816185 |
| shape_axis_no_support | e176 | 1.000000000 | 0.925898875 | 0.920864017 | 0.933324089 |
| shape_only | e144 | 0.000000000 | 0.016426756 | 0.005881782 | 0.026081579 |
| shape_only | e154 | 0.000000000 | 0.001610088 | 0.001369363 | 0.001816185 |
| shape_only | e176 | 1.000000000 | 0.925898875 | 0.920864017 | 0.933324089 |
| shape_support | e144 | 0.000000000 | 0.005920824 | 0.002241587 | 0.008419755 |
| shape_support | e154 | 0.000000000 | 0.002305849 | 0.000940115 | 0.004709562 |
| shape_support | e176 | 1.000000000 | 0.816469448 | 0.754047547 | 0.875250196 |
| shape_support_drop_between | e144 | 0.000000000 | 0.081585071 | 0.021082952 | 0.123922947 |
| shape_support_drop_between | e154 | 0.000000000 | 0.038795487 | 0.018764809 | 0.071335805 |
| shape_support_drop_between | e176 | 1.000000000 | 0.940576942 | 0.926825091 | 0.961631310 |
| shape_support_drop_flank | e144 | 0.000000000 | 0.006185431 | 0.002622123 | 0.008008499 |
| shape_support_drop_flank | e154 | 0.000000000 | 0.002364102 | 0.000983588 | 0.004778126 |
| shape_support_drop_flank | e176 | 1.000000000 | 0.784092245 | 0.720037091 | 0.844984291 |
| shape_support_drop_focus | e144 | 0.000000000 | 0.007428539 | 0.002626154 | 0.010380636 |
| shape_support_drop_focus | e154 | 0.000000000 | 0.002674173 | 0.001100904 | 0.005436172 |
| shape_support_drop_focus | e176 | 1.000000000 | 0.788146821 | 0.726487655 | 0.847829594 |
| shape_support_drop_global | e144 | 0.000000000 | 0.004585350 | 0.001998397 | 0.007061475 |
| shape_support_drop_global | e154 | 0.000000000 | 0.002162358 | 0.000971774 | 0.004191549 |
| shape_support_drop_global | e176 | 1.000000000 | 0.759663393 | 0.677063440 | 0.834765655 |
| shape_support_drop_nearest | e144 | 0.000000000 | 0.009802993 | 0.003081977 | 0.013280546 |
| shape_support_drop_nearest | e154 | 0.000000000 | 0.003591347 | 0.001418965 | 0.007450815 |
| shape_support_drop_nearest | e176 | 1.000000000 | 0.837251378 | 0.789133784 | 0.880432623 |
| shape_support_drop_prior_split | e144 | 0.000000000 | 0.004516484 | 0.001530552 | 0.006866991 |
| shape_support_drop_prior_split | e154 | 0.000000000 | 0.001954213 | 0.000683598 | 0.004248550 |
| shape_support_drop_prior_split | e176 | 1.000000000 | 0.911637570 | 0.878909185 | 0.947408480 |
| shape_support_drop_subject | e144 | 0.000000000 | 0.005859712 | 0.002424999 | 0.008472622 |
| shape_support_drop_subject | e154 | 0.000000000 | 0.002256825 | 0.000954485 | 0.004554184 |
| shape_support_drop_subject | e176 | 1.000000000 | 0.723510417 | 0.641125843 | 0.805831197 |
| shape_support_drop_top1 | e144 | 0.000000000 | 0.017672338 | 0.005996830 | 0.038782210 |
| shape_support_drop_top1 | e154 | 0.000000000 | 0.005406421 | 0.002114620 | 0.011115741 |
| shape_support_drop_top1 | e176 | 1.000000000 | 0.967894654 | 0.955573213 | 0.979733947 |
| shape_support_drop_top16_33 | e144 | 0.000000000 | 0.005918104 | 0.001452961 | 0.008612246 |
| shape_support_drop_top16_33 | e154 | 0.000000000 | 0.001478575 | 0.000541616 | 0.003126667 |
| shape_support_drop_top16_33 | e176 | 1.000000000 | 0.929906828 | 0.907117694 | 0.947522825 |
| shape_support_drop_visible | e144 | 0.000000000 | 0.006465887 | 0.002666608 | 0.008497854 |
| shape_support_drop_visible | e154 | 0.000000000 | 0.002330199 | 0.000966298 | 0.004713006 |
| shape_support_drop_visible | e176 | 1.000000000 | 0.782051777 | 0.716198250 | 0.844011628 |
| shape_support_keep_hard_only | e144 | 0.000000000 | 0.178434862 | 0.089407418 | 0.297062081 |
| shape_support_keep_hard_only | e154 | 0.000000000 | 0.010871020 | 0.006958889 | 0.017595822 |
| shape_support_keep_hard_only | e176 | 1.000000000 | 0.956273490 | 0.943308988 | 0.979097212 |
| shape_support_keep_mean_only | e144 | 0.000000000 | 0.070514188 | 0.049537526 | 0.098746023 |
| shape_support_keep_mean_only | e154 | 0.000000000 | 0.029979088 | 0.013834428 | 0.059001975 |
| shape_support_keep_mean_only | e176 | 0.000000000 | 0.367678655 | 0.300089943 | 0.498194237 |
| shape_support_no_q2s3_targets | e144 | 0.000000000 | 0.005225342 | 0.002619255 | 0.007352187 |
| shape_support_no_q2s3_targets | e154 | 0.000000000 | 0.001916903 | 0.000852168 | 0.003810360 |
| shape_support_no_q2s3_targets | e176 | 1.000000000 | 0.834671515 | 0.767687918 | 0.896195423 |
| shape_support_public_axis | e144 | 0.000000000 | 0.005920824 | 0.002241587 | 0.008419755 |
| shape_support_public_axis | e154 | 0.000000000 | 0.002305849 | 0.000940115 | 0.004709562 |
| shape_support_public_axis | e176 | 1.000000000 | 0.816469448 | 0.754047547 | 0.875250196 |

## E95-over-E101 Family Contributions

| variant | group_col | heldout | new_file | base_file | family | family_contribution | family_abs_contribution | top_feature | top_feature_contribution |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.521978277 | 1.033988208 | z__target_between_Q2_support_swing | 0.550644561 |
| shape_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.641079833 | 0.792797115 | z__shape_between_support_label_swing | 0.333314201 |
| shape_only | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_only | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.537549142 | 1.030690534 | z__target_between_Q2_support_swing | 0.555179738 |
| shape_only | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.634228451 | 0.707860582 | z__shape_between_support_label_swing | 0.277132021 |
| shape_only | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.871877284 | 1.123888097 | z__target_between_Q2_support_swing | 0.698887202 |
| shape_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.642410385 | 0.685207621 | z__shape_between_support_label_swing | 0.309373341 |
| shape_only | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_flank | -1.346211421 | 2.264580341 | z__sup_between_flank_mean_mean | -0.395486536 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_visible | -1.193054597 | 2.074357157 | z__sup_between_visible_mean_mean | -0.324787104 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_subject | -1.084532682 | 1.775991638 | z__sup_between_subject_mean | -0.457125782 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_focus | -1.052004475 | 1.675182115 | z__sup_between_focus_mean_swing | -0.237550509 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_global | -0.429610039 | 1.427122757 | z__sup_top4_global_hard_rate | -0.403440023 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_nearest | -0.579885680 | 1.302903974 | z__sup_between_nearest_hard085_swing | -0.182572126 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_all_prior | -0.474293238 | 1.172158635 | z__sup_top4_all_prior_adverse_rate | -0.256814467 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.903568127 | 0.963308876 | z__shape_between_support_label_mean | 0.381461416 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.474902652 | 0.818081617 | z__target_between_Q2_support_swing | 0.436184817 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_prior_split | 0.000000000 | 0.000000000 | z__sup_all_prior_split_rate | -0.000000000 |
| shape_support | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_range | 0.000000000 | 0.000000000 | z__sup_all_range_mean | 0.000000000 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_flank | -1.407546907 | 2.332396616 | z__sup_between_flank_mean_swing | -0.398420125 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_visible | -1.246253397 | 2.134332132 | z__sup_between_visible_mean_swing | -0.350289440 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_subject | -1.274819575 | 1.977892199 | z__sup_between_subject_mean | -0.455924133 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_focus | -1.095568735 | 1.722461194 | z__sup_between_focus_mean_swing | -0.271269287 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_global | -0.463862489 | 1.399168277 | z__sup_top4_global_hard_rate | -0.404664189 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_nearest | -0.590232608 | 1.315599234 | z__sup_between_nearest_hard085_swing | -0.189477637 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_all_prior | -0.460008885 | 1.162048732 | z__sup_top4_all_prior_adverse_rate | -0.257780806 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.879793311 | 0.936022101 | z__shape_between_support_label_mean | 0.372019731 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.468622790 | 0.812504086 | z__target_between_Q2_support_swing | 0.430569048 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_prior_split | 0.000000000 | 0.000000000 | z__sup_all_prior_split_rate | -0.000000000 |
| shape_support | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_range | 0.000000000 | 0.000000000 | z__sup_all_range_mean | 0.000000000 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_flank | -1.382217803 | 2.316351789 | z__sup_between_flank_mean_mean | -0.409543089 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_visible | -1.224249083 | 2.115529231 | z__sup_between_visible_mean_mean | -0.338863640 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_subject | -1.138332045 | 1.824527958 | z__sup_between_subject_mean | -0.480021007 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_focus | -1.076428441 | 1.702359024 | z__sup_between_focus_mean_swing | -0.246668754 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_global | -0.487656461 | 1.457760835 | z__sup_top4_global_hard_rate | -0.406443964 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_nearest | -0.587095795 | 1.335292500 | z__sup_between_nearest_hard085_swing | -0.189654587 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_all_prior | -0.491367340 | 1.183141132 | z__sup_top4_all_prior_adverse_rate | -0.251524867 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.948423350 | 1.003641688 | z__shape_between_support_label_mean | 0.377909411 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.528835073 | 0.921393785 | z__target_between_Q2_support_swing | 0.467518950 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_prior_split | 0.000000000 | 0.000000000 | z__sup_all_prior_split_rate | -0.000000000 |
| shape_support | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_range | 0.000000000 | 0.000000000 | z__sup_all_range_mean | 0.000000000 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_flank | -1.346211421 | 2.264580341 | z__sup_between_flank_mean_mean | -0.395486536 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_visible | -1.193054597 | 2.074357157 | z__sup_between_visible_mean_mean | -0.324787104 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_subject | -1.084532682 | 1.775991638 | z__sup_between_subject_mean | -0.457125782 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_focus | -1.052004475 | 1.675182115 | z__sup_between_focus_mean_swing | -0.237550509 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_global | -0.429610039 | 1.427122757 | z__sup_top4_global_hard_rate | -0.403440023 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_nearest | -0.579885680 | 1.302903974 | z__sup_between_nearest_hard085_swing | -0.182572126 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_all_prior | -0.474293238 | 1.172158635 | z__sup_top4_all_prior_adverse_rate | -0.256814467 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.903568127 | 0.963308876 | z__shape_between_support_label_mean | 0.381461416 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.474902652 | 0.818081617 | z__target_between_Q2_support_swing | 0.436184817 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_e101 | 0.000000000 | 0.000000000 | z__axis_all_e101_active_rate | 0.000000000 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_e72 | 0.000000000 | 0.000000000 | z__axis_all_e72_active_rate | 0.000000000 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_other | 0.000000000 | 0.000000000 | z__axis_all_all_safe_density_mean | 0.000000000 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_prior_split | 0.000000000 | 0.000000000 | z__sup_all_prior_split_rate | -0.000000000 |
| shape_support_public_axis | file | submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_range | 0.000000000 | 0.000000000 | z__sup_all_range_mean | 0.000000000 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_flank | -1.407546907 | 2.332396616 | z__sup_between_flank_mean_swing | -0.398420125 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_visible | -1.246253397 | 2.134332132 | z__sup_between_visible_mean_swing | -0.350289440 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_subject | -1.274819575 | 1.977892199 | z__sup_between_subject_mean | -0.455924133 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_focus | -1.095568735 | 1.722461194 | z__sup_between_focus_mean_swing | -0.271269287 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_global | -0.463862489 | 1.399168277 | z__sup_top4_global_hard_rate | -0.404664189 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_nearest | -0.590232608 | 1.315599234 | z__sup_between_nearest_hard085_swing | -0.189477637 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_all_prior | -0.460008885 | 1.162048732 | z__sup_top4_all_prior_adverse_rate | -0.257780806 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.879793311 | 0.936022101 | z__shape_between_support_label_mean | 0.372019731 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.468622790 | 0.812504086 | z__target_between_Q2_support_swing | 0.430569048 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_e101 | 0.000000000 | 0.000000000 | z__axis_all_e101_active_rate | 0.000000000 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_e72 | 0.000000000 | 0.000000000 | z__axis_all_e72_active_rate | 0.000000000 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_other | 0.000000000 | 0.000000000 | z__axis_all_all_safe_density_mean | 0.000000000 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_prior_split | 0.000000000 | 0.000000000 | z__sup_all_prior_split_rate | -0.000000000 |
| shape_support_public_axis | file | submission_e95_hardtail_541e3973.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_range | 0.000000000 | 0.000000000 | z__sup_all_range_mean | 0.000000000 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_flank | -1.382217803 | 2.316351789 | z__sup_between_flank_mean_mean | -0.409543089 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_visible | -1.224249083 | 2.115529231 | z__sup_between_visible_mean_mean | -0.338863640 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_subject | -1.138332045 | 1.824527958 | z__sup_between_subject_mean | -0.480021007 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_focus | -1.076428441 | 1.702359024 | z__sup_between_focus_mean_swing | -0.246668754 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_global | -0.487656461 | 1.457760835 | z__sup_top4_global_hard_rate | -0.406443964 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_nearest | -0.587095795 | 1.335292500 | z__sup_between_nearest_hard085_swing | -0.189654587 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_all_prior | -0.491367340 | 1.183141132 | z__sup_top4_all_prior_adverse_rate | -0.251524867 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | shape | 0.948423350 | 1.003641688 | z__shape_between_support_label_mean | 0.377909411 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | target | 0.528835073 | 0.921393785 | z__target_between_Q2_support_swing | 0.467518950 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_e101 | 0.000000000 | 0.000000000 | z__axis_all_e101_active_rate | 0.000000000 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_e72 | 0.000000000 | 0.000000000 | z__axis_all_e72_active_rate | 0.000000000 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | axis_other | 0.000000000 | 0.000000000 | z__axis_all_all_safe_density_mean | 0.000000000 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | context | 0.000000000 | 0.000000000 | z__ctx_all_between_rate | 0.000000000 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_prior_split | 0.000000000 | 0.000000000 | z__sup_all_prior_split_rate | -0.000000000 |
| shape_support_public_axis | pair | submission_e95_hardtail_541e3973.csv__vs__submission_e101_q2s3tail_177569bc.csv | submission_e95_hardtail_541e3973.csv | submission_e101_q2s3tail_177569bc.csv | support_range | 0.000000000 | 0.000000000 | z__sup_all_range_mean | 0.000000000 |

## Interpretation

- If shape-only fixes E95/E101 while support variants miss it, support priors are
  not pure label signal; they carry a frontier-quality shortcut that can invert
  the tightest boundary.
- If a support ablation both fixes E95/E101 and still selects E176, then the
  shortcut is removable and the branch selector can be repaired.
- If no ablation survives both tests, the known-LB pair decoder should stay a
  sensor for hypotheses, not an automatic selector for submissions.

## Decision

Use `action_grade_boundary_branch` as the local decision flag. A false flag
means the next public-facing submission should not be chosen by this decoder
alone; it needs an orthogonal cell/target stress rationale.
