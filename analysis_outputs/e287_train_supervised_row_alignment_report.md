# E287 Train-Supervised Row-Alignment Transfer Audit

## Question

Can human/social diary context learn a label-grounded row-action benefit target, and can that learned gate transfer to an E247-current tensor without public LB?

## Train Latent Health

- latent rows: `36`
- train-gated policy rows: `3`

| policy_id | split | model | n_cells | n_good | prevalence | auc | ap | ap_lift | mean_benefit_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bedtime_q3 | dateblock_oof | lr_l2 | 24 | 19 | 0.791666667 | 0.852631579 | 0.960890112 | 0.169223445 | -0.015525055 |
| bedtime_q3 | dateblock_oof | lr_l1 | 24 | 19 | 0.791666667 | 0.800000000 | 0.933668849 | 0.142002182 | -0.015525055 |
| bedtime_q3 | subject_oof | lr_l1 | 24 | 19 | 0.791666667 | 0.768421053 | 0.899285300 | 0.107618634 | -0.021279106 |
| bedtime_q3 | subject_oof | lr_l2 | 24 | 19 | 0.791666667 | 0.747368421 | 0.932129117 | 0.140462450 | -0.021279106 |
| mobility_q3 | dateblock_oof | lr_l1 | 51 | 36 | 0.705882353 | 0.618518519 | 0.798711174 | 0.092828821 | -0.006367875 |
| mobility_q3 | subject_oof | lr_l1 | 51 | 36 | 0.705882353 | 0.596296296 | 0.806791519 | 0.100909166 | -0.013298017 |
| mobility_q3 | dateblock_oof | hgb_shallow | 51 | 36 | 0.705882353 | 0.542592593 | 0.702770326 | -0.003112027 | -0.006367875 |
| attention_money_q3 | subject_oof | lr_l1 | 91 | 61 | 0.670329670 | 0.538797814 | 0.671255091 | 0.000925420 | -0.010703278 |
| mobility_q3 | subject_oof | lr_l2 | 51 | 36 | 0.705882353 | 0.537037037 | 0.703861429 | -0.002020924 | -0.013298017 |
| q3_only | subject_oof | lr_l1 | 160 | 121 | 0.756250000 | 0.518330155 | 0.757125771 | 0.000875771 | -0.011548495 |
| q3_only | dateblock_oof | lr_l1 | 160 | 121 | 0.756250000 | 0.511972876 | 0.773575685 | 0.017325685 | -0.007464694 |
| full_qsleep | dateblock_oof | lr_l1 | 232 | 171 | 0.737068966 | 0.509586809 | 0.736070150 | -0.000998816 | -0.007965327 |
| attention_money_q3 | subject_oof | hgb_shallow | 91 | 61 | 0.670329670 | 0.507103825 | 0.677423337 | 0.007093667 | -0.010703278 |
| mobility_q3 | subject_oof | hgb_shallow | 51 | 36 | 0.705882353 | 0.500000000 | 0.696391031 | -0.009491322 | -0.013298017 |
| attention_money_q3 | subject_oof | lr_l2 | 91 | 61 | 0.670329670 | 0.497814208 | 0.707395299 | 0.037065629 | -0.010703278 |
| q3_only | subject_oof | lr_l2 | 160 | 121 | 0.756250000 | 0.489086671 | 0.755591444 | -0.000658556 | -0.011548495 |
| jepa_only | subject_oof | lr_l2 | 121 | 89 | 0.735537190 | 0.483146067 | 0.732694741 | -0.002842449 | -0.014119184 |
| jepa_only | subject_oof | lr_l1 | 121 | 89 | 0.735537190 | 0.472612360 | 0.705541144 | -0.029996046 | -0.014119184 |
| q3_only | subject_oof | hgb_shallow | 160 | 121 | 0.756250000 | 0.471074380 | 0.746636930 | -0.009613070 | -0.011548495 |
| full_qsleep | dateblock_oof | lr_l2 | 232 | 171 | 0.737068966 | 0.470424696 | 0.728525825 | -0.008543140 | -0.007965327 |
| q3_only | dateblock_oof | hgb_shallow | 160 | 121 | 0.756250000 | 0.468107650 | 0.745226849 | -0.011023151 | -0.007464694 |
| full_qsleep | dateblock_oof | hgb_shallow | 232 | 171 | 0.737068966 | 0.463522193 | 0.710689670 | -0.026379295 | -0.007965327 |
| jepa_only | dateblock_oof | lr_l2 | 121 | 89 | 0.735537190 | 0.462429775 | 0.713007126 | -0.022530064 | -0.008968295 |
| full_qsleep | subject_oof | lr_l2 | 232 | 171 | 0.737068966 | 0.460358547 | 0.719078520 | -0.017990446 | -0.011667717 |
| q3_only | dateblock_oof | lr_l2 | 160 | 121 | 0.756250000 | 0.459419369 | 0.753319140 | -0.002930860 | -0.007464694 |
| attention_money_q3 | dateblock_oof | lr_l2 | 91 | 61 | 0.670329670 | 0.458469945 | 0.645180357 | -0.025149314 | -0.006113288 |
| attention_money_q3 | dateblock_oof | lr_l1 | 91 | 61 | 0.670329670 | 0.453551913 | 0.628792813 | -0.041536857 | -0.006113288 |
| jepa_only | dateblock_oof | hgb_shallow | 121 | 89 | 0.735537190 | 0.438553371 | 0.686412989 | -0.049124201 | -0.008968295 |
| mobility_q3 | dateblock_oof | lr_l2 | 51 | 36 | 0.705882353 | 0.437037037 | 0.673404540 | -0.032477813 | -0.006367875 |
| jepa_only | subject_oof | hgb_shallow | 121 | 89 | 0.735537190 | 0.436446629 | 0.698097465 | -0.037439725 | -0.014119184 |

## Train Row-Placement Policy Stress

| policy_id | split | model | top_frac | selected_cells | actual_delta | null_q20 | dominance | row_dominance | subject_dominance | dateblock_dominance | train_gate_bool |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mobility_q3 | dateblock_oof | hgb_shallow | 0.700000000 | 36.000000000 | -0.000253769 | -0.000200032 | 0.922222222 | 0.866666667 | 0.900000000 | 1.000000000 | True |
| q3_only | subject_oof | lr_l1 | 0.700000000 | 112.000000000 | -0.000978542 | -0.000950774 | 0.900000000 | 0.783333333 | 0.983333333 | 0.933333333 | True |
| mobility_q3 | dateblock_oof | lr_l2 | 0.700000000 | 36.000000000 | -0.000213950 | -0.000203608 | 0.844444444 | 0.800000000 | 0.783333333 | 0.950000000 | True |
| bedtime_q3 | subject_oof | lr_l2 | 0.350000000 | 8.000000000 | -0.000181068 | -0.000174526 | 0.888888889 | 0.866666667 | 0.866666667 | 0.933333333 | False |
| bedtime_q3 | dateblock_oof | lr_l2 | 0.200000000 | 5.000000000 | -0.000132562 | -0.000132562 | 0.761111111 | 1.000000000 | 0.483333333 | 0.800000000 | False |
| bedtime_q3 | subject_oof | lr_l2 | 0.200000000 | 5.000000000 | -0.000098606 | -0.000099525 | 0.750000000 | 0.600000000 | 0.883333333 | 0.766666667 | False |
| bedtime_q3 | dateblock_oof | lr_l2 | 0.350000000 | 8.000000000 | -0.000208930 | -0.000210074 | 0.738888889 | 1.000000000 | 0.450000000 | 0.766666667 | False |
| q3_only | dateblock_oof | lr_l1 | 0.700000000 | 112.000000000 | -0.000602610 | -0.000639305 | 0.727777778 | 0.500000000 | 0.716666667 | 0.966666667 | False |
| mobility_q3 | dateblock_oof | lr_l2 | 0.500000000 | 26.000000000 | -0.000142598 | -0.000167248 | 0.722222222 | 0.550000000 | 0.766666667 | 0.850000000 | False |
| mobility_q3 | dateblock_oof | lr_l1 | 0.500000000 | 26.000000000 | -0.000161409 | -0.000169940 | 0.683333333 | 0.833333333 | 0.816666667 | 0.400000000 | False |
| mobility_q3 | dateblock_oof | lr_l1 | 0.700000000 | 36.000000000 | -0.000189067 | -0.000198745 | 0.661111111 | 0.650000000 | 0.683333333 | 0.650000000 | False |
| full_qsleep | dateblock_oof | lr_l1 | 0.500000000 | 116.000000000 | -0.000668314 | -0.000723286 | 0.633333333 | 0.533333333 | 0.683333333 | 0.683333333 | False |
| bedtime_q3 | dateblock_oof | lr_l2 | 0.700000000 | 17.000000000 | -0.000323700 | -0.000323700 | 0.633333333 | 1.000000000 | 0.900000000 | 0.000000000 | False |
| bedtime_q3 | dateblock_oof | lr_l1 | 0.700000000 | 17.000000000 | -0.000310323 | -0.000310323 | 0.616666667 | 1.000000000 | 0.850000000 | 0.000000000 | False |
| bedtime_q3 | subject_oof | lr_l2 | 0.500000000 | 12.000000000 | -0.000243106 | -0.000247292 | 0.616666667 | 0.733333333 | 0.566666667 | 0.550000000 | False |
| bedtime_q3 | subject_oof | lr_l1 | 0.700000000 | 17.000000000 | -0.000430303 | -0.000430303 | 0.611111111 | 1.000000000 | 0.833333333 | 0.000000000 | False |
| jepa_only | dateblock_oof | lr_l2 | 0.350000000 | 42.000000000 | -0.000270083 | -0.000322778 | 0.611111111 | 0.533333333 | 0.466666667 | 0.833333333 | False |
| bedtime_q3 | subject_oof | lr_l2 | 0.700000000 | 17.000000000 | -0.000270702 | -0.000275817 | 0.605555556 | 0.583333333 | 0.616666667 | 0.616666667 | False |
| mobility_q3 | dateblock_oof | hgb_shallow | 0.500000000 | 26.000000000 | -0.000160591 | -0.000194202 | 0.605555556 | 0.700000000 | 0.683333333 | 0.433333333 | False |
| q3_only | dateblock_oof | lr_l2 | 0.200000000 | 32.000000000 | -0.000221229 | -0.000265120 | 0.600000000 | 0.766666667 | 0.750000000 | 0.283333333 | False |
| attention_money_q3 | subject_oof | hgb_shallow | 0.500000000 | 46.000000000 | -0.000246877 | -0.000345999 | 0.594444444 | 0.050000000 | 0.766666667 | 0.966666667 | False |
| bedtime_q3 | dateblock_oof | lr_l1 | 0.500000000 | 12.000000000 | -0.000220631 | -0.000220631 | 0.594444444 | 0.966666667 | 0.816666667 | 0.000000000 | False |
| full_qsleep | dateblock_oof | lr_l1 | 0.700000000 | 162.000000000 | -0.000899613 | -0.000982045 | 0.583333333 | 0.266666667 | 0.666666667 | 0.816666667 | False |
| bedtime_q3 | subject_oof | lr_l1 | 0.500000000 | 12.000000000 | -0.000241374 | -0.000241374 | 0.583333333 | 0.933333333 | 0.816666667 | 0.000000000 | False |
| q3_only | dateblock_oof | hgb_shallow | 0.200000000 | 32.000000000 | -0.000224602 | -0.000264732 | 0.572222222 | 0.650000000 | 0.566666667 | 0.500000000 | False |
| mobility_q3 | dateblock_oof | hgb_shallow | 0.350000000 | 18.000000000 | -0.000100320 | -0.000130506 | 0.566666667 | 0.650000000 | 0.650000000 | 0.400000000 | False |
| q3_only | subject_oof | hgb_shallow | 0.700000000 | 112.000000000 | -0.000951018 | -0.001000037 | 0.561111111 | 0.483333333 | 0.583333333 | 0.616666667 | False |
| jepa_only | dateblock_oof | lr_l2 | 0.500000000 | 60.000000000 | -0.000372027 | -0.000452122 | 0.533333333 | 0.383333333 | 0.350000000 | 0.866666667 | False |
| bedtime_q3 | dateblock_oof | lr_l1 | 0.200000000 | 5.000000000 | -0.000081909 | -0.000087533 | 0.533333333 | 0.716666667 | 0.550000000 | 0.333333333 | False |
| attention_money_q3 | dateblock_oof | lr_l2 | 0.700000000 | 64.000000000 | -0.000207089 | -0.000287500 | 0.527777778 | 0.133333333 | 0.566666667 | 0.883333333 | False |
| mobility_q3 | subject_oof | lr_l1 | 0.700000000 | 36.000000000 | -0.000425345 | -0.000466277 | 0.516666667 | 0.783333333 | 0.666666667 | 0.100000000 | False |
| q3_only | dateblock_oof | lr_l1 | 0.200000000 | 32.000000000 | -0.000156474 | -0.000219405 | 0.516666667 | 0.533333333 | 0.433333333 | 0.583333333 | False |
| q3_only | dateblock_oof | lr_l1 | 0.500000000 | 80.000000000 | -0.000373628 | -0.000468618 | 0.511111111 | 0.333333333 | 0.366666667 | 0.833333333 | False |
| bedtime_q3 | dateblock_oof | lr_l2 | 0.500000000 | 12.000000000 | -0.000247648 | -0.000274090 | 0.511111111 | 1.000000000 | 0.266666667 | 0.266666667 | False |
| jepa_only | dateblock_oof | hgb_shallow | 0.700000000 | 85.000000000 | -0.000518093 | -0.000607714 | 0.505555556 | 0.233333333 | 0.433333333 | 0.850000000 | False |
| mobility_q3 | subject_oof | lr_l1 | 0.500000000 | 26.000000000 | -0.000309139 | -0.000382196 | 0.505555556 | 0.750000000 | 0.666666667 | 0.100000000 | False |
| q3_only | dateblock_oof | lr_l1 | 0.350000000 | 56.000000000 | -0.000291692 | -0.000364387 | 0.488888889 | 0.433333333 | 0.533333333 | 0.500000000 | False |
| q3_only | dateblock_oof | hgb_shallow | 0.350000000 | 56.000000000 | -0.000289471 | -0.000360102 | 0.483333333 | 0.416666667 | 0.516666667 | 0.516666667 | False |
| mobility_q3 | dateblock_oof | lr_l2 | 0.200000000 | 10.000000000 | -0.000035644 | -0.000071570 | 0.455555556 | 0.416666667 | 0.400000000 | 0.550000000 | False |
| q3_only | subject_oof | hgb_shallow | 0.500000000 | 80.000000000 | -0.000561031 | -0.000666048 | 0.450000000 | 0.233333333 | 0.750000000 | 0.366666667 | False |

## Test Transfer Candidates

- materialized candidates: `3`
- public-free ready candidates: `0`

| basename | policy_id | split | model | top_frac | test_selected_cells | old_promotion_decision | actual_mean | actual_p90 | null_strict_rate | p90_dominance | worst_mode_p90_dominance | final_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| submission_e287_rowalign_q3_only_subject_oof_lr_l1_tf70_5fc12bc2.csv | q3_only | subject_oof | lr_l1 | 0.700000000 | 106 | too_small_to_submit | -0.000051070 | -0.000034973 | 0.047619048 | 0.714285714 | 0.428571429 | too_small_to_submit |
| submission_e287_rowalign_mobility_q3_dateblock_oof_hgb_shallow_tf70_c4b98b06.csv | mobility_q3 | dateblock_oof | hgb_shallow | 0.700000000 | 34 | below_selector_resolution | 0.000037869 | 0.000051525 | 0.000000000 | 0.000000000 | 0.000000000 | below_selector_resolution |
| submission_e287_rowalign_mobility_q3_dateblock_oof_lr_l2_tf70_1c3bd91e.csv | mobility_q3 | dateblock_oof | lr_l2 | 0.700000000 | 34 | below_selector_resolution | 0.000060097 | 0.000078696 | 0.000000000 | 0.238095238 | 0.000000000 | below_selector_resolution |

## Decision

No E287 candidate is public-free ready. The train row-action latent is useful only if it can beat test matched nulls; otherwise keep it diagnostic.

## Interpretation

This experiment distinguishes three states: train-label row-action learnability, train matched-null row placement, and test tensor transfer. A high train AUC without matched-null dominance is not enough. A train-gated row without E247-current null dominance is also not enough.

## Files

- `e287_train_supervised_row_alignment_latent_summary.csv`
- `e287_train_supervised_row_alignment_policy_summary.csv`
- `e287_train_supervised_row_alignment_transfer_summary.csv`
- `e287_train_supervised_row_alignment_candidate_summary.csv`
- `e287_train_supervised_row_alignment_governor_summary.csv`
