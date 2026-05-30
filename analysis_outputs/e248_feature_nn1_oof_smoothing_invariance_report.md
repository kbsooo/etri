# E248 Feature-NN1 OOF Smoothing Invariance

## Question

Does E247's feature-NN1 Q3 smoothing selector have a train/OOF analogue, or is it only a test-geometry stress survivor?

The target quantity is OOF `q3_e224` benefit: `base_loss - full_loss`. Negative selected benefit means rolling the full movement back to base would improve LogLoss.

## Full Train Ranking At E247 Fraction

| score | top_frac | selected_n | auc_harmful | auc_tail20 | benefit_spearman_neg | drop_delta_vs_full_per_row | harmful_rate_selected | tail20_rate_selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| score_neg_trainpca_smooth_sum | 0.136000000 | 61 | 0.532178413 | 0.494814815 | 0.022576643 | 0.000489209 | 0.557377049 | 0.360655738 |
| score_trainpca_incoming | 0.136000000 | 61 | 0.439090155 | 0.498518519 | -0.079551160 | 0.000885838 | 0.459016393 | 0.229508197 |
| score_allpca_incoming | 0.136000000 | 61 | 0.455446034 | 0.513611111 | -0.046749832 | 0.000891586 | 0.475409836 | 0.245901639 |
| score_trainpca_smooth_mean | 0.136000000 | 61 | 0.480365044 | 0.501913580 | -0.004347173 | 0.002078700 | 0.459016393 | 0.409836066 |
| score_amp | 0.136000000 | 61 | 0.513471871 | 0.814351852 | -0.011564370 | 0.002561583 | 0.459016393 | 0.459016393 |
| score_allpca_smooth_mean | 0.136000000 | 61 | 0.450290376 | 0.461820988 | -0.077989206 | 0.002698527 | 0.442622951 | 0.377049180 |
| score_trainpca_source | 0.136000000 | 61 | 0.491565265 | 0.500771605 | -0.002115895 | 0.002783109 | 0.442622951 | 0.393442623 |
| score_trainpca_amp_smooth | 0.136000000 | 61 | 0.470271018 | 0.499753086 | -0.024100547 | 0.002787074 | 0.409836066 | 0.393442623 |
| score_trainpca_smooth_sum | 0.136000000 | 61 | 0.467821587 | 0.505185185 | -0.022576643 | 0.002829987 | 0.409836066 | 0.344262295 |
| score_allpca_smooth_sum | 0.136000000 | 61 | 0.448561947 | 0.478256173 | -0.074155213 | 0.002922728 | 0.426229508 | 0.327868852 |
| score_allpca_amp_smooth | 0.136000000 | 61 | 0.447169327 | 0.469104938 | -0.083411498 | 0.003315449 | 0.393442623 | 0.344262295 |
| score_allpca_source | 0.136000000 | 61 | 0.466912927 | 0.468611111 | -0.065995980 | 0.003358665 | 0.426229508 | 0.360655738 |

## Split Stress At E247 Fraction

| score | top_frac | mode | folds | selected_n_mean | drop_delta_mean | drop_delta_std | win_rate | harmful_rate_selected_mean | tail20_rate_selected_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| score_neg_trainpca_smooth_sum | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.001066518 | 0.003193143 | 0.450000000 | 0.541964286 | 0.352976190 |
| score_trainpca_incoming | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.001096117 | 0.002144201 | 0.250000000 | 0.427083333 | 0.223511905 |
| score_allpca_incoming | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.001197085 | 0.002286116 | 0.300000000 | 0.425000000 | 0.254761905 |
| score_trainpca_source | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.002395004 | 0.003467875 | 0.350000000 | 0.457738095 | 0.421428571 |
| score_trainpca_amp_smooth | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.002562751 | 0.003266961 | 0.350000000 | 0.427678571 | 0.368452381 |
| score_trainpca_smooth_sum | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.002638697 | 0.003391257 | 0.300000000 | 0.419345238 | 0.347619048 |
| score_trainpca_smooth_mean | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.002700566 | 0.003567655 | 0.300000000 | 0.410119048 | 0.371726190 |
| score_amp | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.002733652 | 0.004036352 | 0.250000000 | 0.474404762 | 0.470238095 |
| score_allpca_smooth_mean | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.002889953 | 0.003368125 | 0.200000000 | 0.430357143 | 0.363988095 |
| score_allpca_smooth_sum | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.002950123 | 0.002856596 | 0.150000000 | 0.411309524 | 0.293154762 |
| score_allpca_amp_smooth | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.003045238 | 0.003955059 | 0.100000000 | 0.430952381 | 0.351190476 |
| score_allpca_source | 0.136000000 | valid_top_frac | 20 | 9.150000000 | 0.003442957 | 0.003475360 | 0.100000000 | 0.408035714 | 0.352083333 |

## E247-Analog Rows

| score | top_frac | selected_n | auc_harmful | auc_tail20 | benefit_spearman_neg | drop_delta_vs_full_per_row | harmful_rate_selected | tail20_rate_selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| score_trainpca_smooth_sum | 0.136000000 | 61 | 0.467821587 | 0.505185185 | -0.022576643 | 0.002829987 | 0.409836066 | 0.344262295 |
| score_allpca_smooth_sum | 0.136000000 | 61 | 0.448561947 | 0.478256173 | -0.074155213 | 0.002922728 | 0.426229508 | 0.327868852 |

## Test Context Sanity

| score | top_frac | selected_n | overlap_e247 | overlap_e237 | overlap_e230_swing25 | overlap_amp_top25 | jaccard_e247 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| single_row_smooth_gain_sum | 0.136000000 | 34 | 34 | 13 | 10 | 10 | 1.000000000 |
| amp_smooth_gain_sum | 0.136000000 | 34 | 29 | 14 | 12 | 12 | 0.743589744 |
| single_row_smooth_gain_mean | 0.136000000 | 34 | 28 | 13 | 10 | 10 | 0.700000000 |
| source_smooth_gain | 0.136000000 | 34 | 25 | 13 | 11 | 11 | 0.581395349 |
| incoming_smooth_gain_sum | 0.136000000 | 34 | 19 | 2 | 4 | 4 | 0.387755102 |
| rollback_amp_abs | 0.136000000 | 34 | 14 | 18 | 25 | 25 | 0.259259259 |

## Decision

- Best OOF score `score_neg_trainpca_smooth_sum` is still non-negative at `0.000489209`. E247 remains a high-information public sensor, not an OOF-certified selector.
- E247 train-only PCA analogue delta: `0.002829987`.
- E247 all-PCA analogue delta: `0.002922728`.
- No submission is created by E248.
