# E264 Human/Social Tail JEPA OOF

## Question

Can the E262 human diary representation predict held-out Q3/S4 harmful tail cells under subject/date-block stress?

This is the OOF analogue required after E263. No public LB is fit and no submission is created.

## Headline

- scanned rows: `2184` policies.
- strict lifestyle gates: `725`.
- human-only strict gates: `443`.
- human-containing strict gates: `682`.
- best overall loss_vs_full: `-0.001689622`.
- best human-only loss_vs_full: `-0.001689622`.

## Top Strict Rows

| view | model | split | source_scope | target_kind | tail_q | policy | tail_auc | loss_vs_full | q3_loss_vs_full | s4_loss_vs_full | subject_win_rate | dateblock_win_rate | dropped_cells | dropped_q3 | dropped_s4 | dropped_mean_benefit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_global_p20 | 0.582818294 | -0.001689622 | -0.001493975 | -0.001885269 | 0.900000000 | 0.701492537 | 180 | 90 | 90 | -0.008448111 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_global_top100 | 0.582818294 | -0.001285685 | -0.001269023 | -0.001302346 | 0.900000000 | 0.671641791 | 100 | 50 | 50 | -0.011571161 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_global_p15 | 0.582818294 | -0.001228427 | -0.001259706 | -0.001197148 | 0.900000000 | 0.671641791 | 135 | 68 | 67 | -0.008189514 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_s4_p20 | 0.582818294 | -0.000942635 | 0.000000000 | -0.001885269 | 0.800000000 | 0.626865672 | 90 | 0 | 90 | -0.009426346 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_global_p10 | 0.582818294 | -0.000927595 | -0.000820028 | -0.001035162 | 0.900000000 | 0.671641791 | 90 | 45 | 45 | -0.009275948 |
| latent_human_late | hgb_shallow | dateblock5 | all3 | contrast | 0.100000000 | drop_global_top75 | 0.661498416 | -0.000797201 | -0.000735037 | -0.000859365 | 0.900000000 | 0.626865672 | 75 | 39 | 36 | -0.009566409 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | 0.100000000 | drop_global_top50 | 0.519019442 | -0.000782275 | -0.000546492 | -0.001018057 | 0.800000000 | 0.626865672 | 50 | 25 | 25 | -0.014080945 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | 0.100000000 | drop_each_top25 | 0.519019442 | -0.000782275 | -0.000546492 | -0.001018057 | 0.800000000 | 0.626865672 | 50 | 25 | 25 | -0.014080945 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_q3_p20 | 0.582818294 | -0.000746988 | -0.001493975 | 0.000000000 | 0.800000000 | 0.656716418 | 90 | 90 | 0 | -0.007469876 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | 0.100000000 | drop_global_top75 | 0.553870530 | -0.000690449 | -0.000583834 | -0.000797065 | 0.700000000 | 0.641791045 | 75 | 38 | 37 | -0.008285389 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_s4_top50 | 0.582818294 | -0.000651173 | 0.000000000 | -0.001302346 | 0.700000000 | 0.626865672 | 50 | 0 | 50 | -0.011721117 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_q3_top50 | 0.582818294 | -0.000634511 | -0.001269023 | 0.000000000 | 0.700000000 | 0.641791045 | 50 | 50 | 0 | -0.011421204 |
| latent_human_late | hgb_shallow | dateblock5 | q3s4 | contrast | 0.100000000 | drop_global_p10 | 0.578485740 | -0.000630667 | -0.000928058 | -0.000333276 | 0.700000000 | 0.626865672 | 90 | 44 | 46 | -0.006306671 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_q3_p15 | 0.582818294 | -0.000629853 | -0.001259706 | 0.000000000 | 0.700000000 | 0.641791045 | 68 | 68 | 0 | -0.008336291 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | 0.100000000 | drop_global_p05 | 0.519019442 | -0.000626499 | -0.000374786 | -0.000878213 | 0.700000000 | 0.626865672 | 45 | 23 | 22 | -0.012529988 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | 0.100000000 | drop_global_p05 | 0.553870530 | -0.000613890 | -0.000635470 | -0.000592310 | 0.700000000 | 0.626865672 | 45 | 23 | 22 | -0.012277804 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | 0.100000000 | drop_each_top21 | 0.519019442 | -0.000601807 | -0.000365882 | -0.000837731 | 0.700000000 | 0.626865672 | 42 | 21 | 21 | -0.012895863 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_s4_p15 | 0.582818294 | -0.000598574 | 0.000000000 | -0.001197148 | 0.700000000 | 0.626865672 | 68 | 0 | 68 | -0.007922303 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | 0.100000000 | drop_global_p20 | 0.551977192 | -0.000582951 | -0.000024462 | -0.001141440 | 0.900000000 | 0.611940299 | 180 | 90 | 90 | -0.002914755 |
| human_core | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | 0.100000000 | drop_global_top100 | 0.524332277 | -0.000582766 | -0.000269732 | -0.000895800 | 0.800000000 | 0.626865672 | 100 | 50 | 50 | -0.005244892 |
| human_late | hgb_shallow | subject5 | q3s4 | risk | 0.100000000 | drop_global_top75 | 0.582818294 | -0.000579130 | -0.000656434 | -0.000501827 | 0.800000000 | 0.641791045 | 75 | 38 | 37 | -0.006949562 |
| latent_human_late | hgb_shallow | subject5 | all3 | contrast | 0.100000000 | drop_global_top50 | 0.583444028 | -0.000578649 | -0.000381891 | -0.000775407 | 0.600000000 | 0.641791045 | 50 | 24 | 26 | -0.010415684 |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | 0.100000000 | drop_global_top40 | 0.519019442 | -0.000577137 | -0.000465978 | -0.000688297 | 0.700000000 | 0.626865672 | 40 | 20 | 20 | -0.012985591 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | 0.100000000 | drop_s4_p20 | 0.551977192 | -0.000570720 | 0.000000000 | -0.001141440 | 0.800000000 | 0.611940299 | 90 | 0 | 90 | -0.005707202 |
| latent_human_late | hgb_shallow | subject5 | all3 | contrast | 0.100000000 | drop_global_p15 | 0.583444028 | -0.000561424 | -0.001002395 | -0.000120453 | 0.700000000 | 0.626865672 | 135 | 68 | 67 | -0.003742826 |
| latent_human_late | hgb_shallow | dateblock5 | all3 | contrast | 0.100000000 | drop_q3_p20 | 0.661498416 | -0.000546008 | -0.001092016 | 0.000000000 | 0.600000000 | 0.626865672 | 90 | 90 | 0 | -0.005460080 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | 0.100000000 | drop_global_top40 | 0.551977192 | -0.000545905 | -0.000652424 | -0.000439386 | 0.600000000 | 0.611940299 | 40 | 20 | 20 | -0.012282871 |
| latent_human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | 0.100000000 | drop_global_p10 | 0.578089633 | -0.000526683 | -0.000289679 | -0.000763686 | 0.700000000 | 0.611940299 | 90 | 43 | 47 | -0.005266829 |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | 0.100000000 | drop_global_top100 | 0.551977192 | -0.000525945 | -0.000055666 | -0.000996223 | 0.700000000 | 0.597014925 | 100 | 50 | 50 | -0.004733502 |
| latent_human_late | hgb_shallow | subject5 | all3 | contrast | 0.100000000 | drop_global_p20 | 0.583444028 | -0.000524159 | -0.000922272 | -0.000126046 | 0.700000000 | 0.626865672 | 180 | 88 | 92 | -0.002620797 |

## View Summary

| view | model | split | rows | strict_gates | stress_promotes | best_loss_vs_full | best_q3_loss_vs_full | median_tail_auc | best_tail_auc | best_subject_win | best_dateblock_win |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human_late | lr_l2_c0p10 | dateblock5 | 156 | 103 | 103 | -0.000690449 | -0.000704094 | 0.548510099 | 0.553870530 | 0.900000000 | 0.656716418 |
| human_core | lr_l2_c0p10 | dateblock5 | 156 | 92 | 92 | -0.000582766 | -0.000364029 | 0.521154576 | 0.557152558 | 0.800000000 | 0.641791045 |
| human_late | hgb_shallow | subject5 | 156 | 84 | 84 | -0.001689622 | -0.001493975 | 0.550918868 | 0.583334465 | 0.900000000 | 0.701492537 |
| latent_human_late | hgb_shallow | dateblock5 | 156 | 76 | 76 | -0.000797201 | -0.001153433 | 0.785658531 | 0.918417718 | 0.900000000 | 0.656716418 |
| human_late | hgb_shallow | dateblock5 | 156 | 73 | 73 | -0.000516038 | -0.000865192 | 0.578975082 | 0.612833861 | 0.800000000 | 0.671641791 |
| human_late | lr_l2_c0p10 | subject5 | 156 | 60 | 60 | -0.000368376 | -0.000547849 | 0.501563254 | 0.520035589 | 0.800000000 | 0.641791045 |
| latent_human_core | lr_l2_c0p10 | dateblock5 | 156 | 55 | 55 | -0.000461258 | -0.000812527 | 0.709628836 | 0.846338630 | 0.900000000 | 0.641791045 |
| latent_human_late | lr_l2_c0p10 | dateblock5 | 156 | 48 | 48 | -0.000526683 | -0.000314484 | 0.691894455 | 0.813381025 | 0.800000000 | 0.641791045 |
| latent_human_late | hgb_shallow | subject5 | 156 | 47 | 47 | -0.000578649 | -0.001002395 | 0.738895977 | 0.903048126 | 0.800000000 | 0.656716418 |
| latent_no_targetid | lr_l2_c0p10 | dateblock5 | 156 | 41 | 41 | -0.000522498 | -0.001005427 | 0.701746015 | 0.845124333 | 0.800000000 | 0.656716418 |
| human_core | lr_l2_c0p10 | subject5 | 156 | 31 | 31 | -0.000292221 | -0.000315482 | 0.490843299 | 0.496400386 | 0.800000000 | 0.671641791 |
| latent_human_late | lr_l2_c0p10 | subject5 | 156 | 7 | 7 | -0.000083670 | -0.000167340 | 0.585427660 | 0.728249501 | 0.800000000 | 0.641791045 |
| latent_human_core | lr_l2_c0p10 | subject5 | 156 | 6 | 6 | -0.000056626 | -0.000088844 | 0.605975987 | 0.784518942 | 0.800000000 | 0.641791045 |
| latent_no_targetid | lr_l2_c0p10 | subject5 | 156 | 2 | 2 | -0.000225846 | -0.000451692 | 0.636266408 | 0.832719814 | 0.800000000 | 0.641791045 |

## Human-Added Pair Deltas

| pair | model | split | rows | plus_strict_only | median_delta_loss | best_delta_loss | median_delta_q3_loss | median_delta_tail_auc | better_loss_rate | better_q3_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| latent_human_late_vs_latent_no_targetid | lr_l2_c0p10 | dateblock5 | 156 | 25 | -0.000000588 | -0.001095246 | 0.000000000 | -0.016840017 | 0.506410256 | 0.326923077 |
| latent_human_core_vs_latent_no_targetid | lr_l2_c0p10 | dateblock5 | 156 | 22 | 0.000000270 | -0.000749484 | 0.000000000 | 0.006605338 | 0.435897436 | 0.320512821 |
| latent_human_late_vs_latent_no_targetid | lr_l2_c0p10 | subject5 | 156 | 6 | -0.000146327 | -0.001498258 | 0.000000000 | -0.050838748 | 0.608974359 | 0.448717949 |
| latent_human_core_vs_latent_no_targetid | lr_l2_c0p10 | subject5 | 156 | 5 | -0.000020845 | -0.000694703 | 0.000000000 | -0.029021339 | 0.519230769 | 0.288461538 |

## Interpretation Rule

- If human-only or human-added views produce strict gates on `dateblock5` and `subject5`, the lifestyle representation is real enough to become a JEPA target/gate candidate.
- If only row5 works, it is likely local row/order leakage.
- If human-added views improve tail AUC but not policy loss, the representation is diagnostic energy only.
- If human views fail while latent baselines pass, E263's four-cell lifestyle contrast is likely not broad enough for a deployable gate.

## Decision

Use this report to decide whether to build E265 materialization. A submission is allowed only if a lifestyle-conditioned row/cell gate survives blocked OOF and does not reduce to subject/domain prediction.
