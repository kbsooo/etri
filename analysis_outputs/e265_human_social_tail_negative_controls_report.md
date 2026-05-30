# E265 Human/Social Tail Negative Controls

## Question

Did E264 find real lifestyle tail signal, or is the E237 rollback policy gate so easy that random cell scores also pass?

## Headline

- random control rows: `220`.
- random strict gate rate: `0.290909`.
- best random loss_vs_full: `-0.000723735`.
- best E264 human-only loss_vs_full: `-0.001689622`.
- verdict: `gate_too_easy_or_needs_sharper_control`.

## Summary

| section | rows | strict_gates | best_loss_vs_full | best_q3_loss_vs_full | best_tail_auc | random_p01_loss_vs_full | random_p05_loss_vs_full | random_strict_rate | random_strict_best_loss | best_e264_file_view |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e264_all | 2184 | 725 | -0.001689622 | -0.001493975 | 0.918417718 | -0.000690262 | -0.000550585 | 0.290909091 | -0.000723735 | human_late |
| e264_human_only | 936 | 443 | -0.001689622 | -0.001493975 | 0.612833861 | -0.000690262 | -0.000550585 | 0.290909091 | -0.000723735 | human_late |
| random_cell_noise | 220 | 64 | -0.000723735 | -0.000718634 | 0.564279835 | -0.000690262 | -0.000550585 | 0.290909091 | -0.000723735 | human_late |

## Best Random Control Rows

| view | model | source_scope | target_kind | policy | tail_auc | loss_vs_full | q3_loss_vs_full | s4_loss_vs_full | subject_win_rate | dateblock_win_rate | dropped_cells | dropped_q3 | dropped_s4 | dropped_mean_benefit | strict_lifestyle_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_cell_noise | rng001 | q3s4 | contrast | drop_global_p20 | 0.553168724 | -0.000723735 | -0.000114717 | -0.001332754 | 0.700000000 | 0.671641791 | 180 | 89 | 91 | -0.003618677 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_global_p20 | 0.553168724 | -0.000723735 | -0.000114717 | -0.001332754 | 0.700000000 | 0.671641791 | 180 | 89 | 91 | -0.003618677 | True |
| random_cell_noise | rng001 | q3s4 | contrast | drop_global_p15 | 0.553168724 | -0.000690262 | -0.000536476 | -0.000844048 | 0.700000000 | 0.671641791 | 135 | 67 | 68 | -0.004601749 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_global_p15 | 0.553168724 | -0.000690262 | -0.000536476 | -0.000844048 | 0.700000000 | 0.671641791 | 135 | 67 | 68 | -0.004601749 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_each_top25 | 0.553168724 | -0.000680887 | -0.000672460 | -0.000689313 | 0.700000000 | 0.671641791 | 50 | 25 | 25 | -0.012255960 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_global_top50 | 0.553168724 | -0.000680887 | -0.000672460 | -0.000689313 | 0.700000000 | 0.671641791 | 50 | 25 | 25 | -0.012255960 | True |
| random_cell_noise | rng001 | q3s4 | contrast | drop_global_top50 | 0.553168724 | -0.000680887 | -0.000672460 | -0.000689313 | 0.700000000 | 0.671641791 | 50 | 25 | 25 | -0.012255960 | True |
| random_cell_noise | rng001 | q3s4 | contrast | drop_each_top25 | 0.553168724 | -0.000680887 | -0.000672460 | -0.000689313 | 0.700000000 | 0.671641791 | 50 | 25 | 25 | -0.012255960 | True |
| random_cell_noise | rng001 | q3s4 | contrast | drop_s4_p20 | 0.553168724 | -0.000581335 | 0.000000000 | -0.001162670 | 0.600000000 | 0.671641791 | 90 | 0 | 90 | -0.005813349 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_s4_p20 | 0.553168724 | -0.000581335 | 0.000000000 | -0.001162670 | 0.600000000 | 0.671641791 | 90 | 0 | 90 | -0.005813349 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_global_top75 | 0.553168724 | -0.000550585 | -0.000718634 | -0.000382536 | 0.700000000 | 0.671641791 | 75 | 36 | 39 | -0.006607021 | True |
| random_cell_noise | rng001 | q3s4 | contrast | drop_global_top75 | 0.553168724 | -0.000550585 | -0.000718634 | -0.000382536 | 0.700000000 | 0.671641791 | 75 | 36 | 39 | -0.006607021 | True |
| random_cell_noise | rng003 | q3s4 | contrast | drop_s4_p20 | 0.520370370 | -0.000501737 | 0.000000000 | -0.001003474 | 0.600000000 | 0.656716418 | 90 | 0 | 90 | -0.005017372 | True |
| random_cell_noise | rng003 | q3s4 | risk | drop_s4_p20 | 0.520370370 | -0.000501737 | 0.000000000 | -0.001003474 | 0.600000000 | 0.656716418 | 90 | 0 | 90 | -0.005017372 | True |
| random_cell_noise | rng001 | q3s4 | contrast | drop_global_top100 | 0.553168724 | -0.000420647 | -0.000516092 | -0.000325202 | 0.700000000 | 0.671641791 | 100 | 49 | 51 | -0.003785820 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_global_top100 | 0.553168724 | -0.000420647 | -0.000516092 | -0.000325202 | 0.700000000 | 0.671641791 | 100 | 49 | 51 | -0.003785820 | True |
| random_cell_noise | rng004 | q3s4 | contrast | drop_global_top100 | 0.509163237 | -0.000384793 | -0.000710004 | -0.000059581 | 0.600000000 | 0.671641791 | 100 | 52 | 48 | -0.003463133 | True |
| random_cell_noise | rng004 | q3s4 | risk | drop_global_top100 | 0.509163237 | -0.000384793 | -0.000710004 | -0.000059581 | 0.600000000 | 0.671641791 | 100 | 52 | 48 | -0.003463133 | True |
| random_cell_noise | rng001 | q3s4 | contrast | drop_global_p10 | 0.553168724 | -0.000366350 | -0.000370832 | -0.000361869 | 0.700000000 | 0.671641791 | 90 | 44 | 46 | -0.003663501 | True |
| random_cell_noise | rng001 | q3s4 | risk | drop_global_p10 | 0.553168724 | -0.000366350 | -0.000370832 | -0.000361869 | 0.700000000 | 0.671641791 | 90 | 44 | 46 | -0.003663501 | True |

## Best E264 Rows For Reference

| view | model | split | source_scope | target_kind | policy | tail_auc | loss_vs_full | q3_loss_vs_full | s4_loss_vs_full | subject_win_rate | dateblock_win_rate | dropped_cells | dropped_q3 | dropped_s4 | dropped_mean_benefit | strict_lifestyle_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_global_p20 | 0.582818294 | -0.001689622 | -0.001493975 | -0.001885269 | 0.900000000 | 0.701492537 | 180 | 90 | 90 | -0.008448111 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_global_top100 | 0.582818294 | -0.001285685 | -0.001269023 | -0.001302346 | 0.900000000 | 0.671641791 | 100 | 50 | 50 | -0.011571161 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_global_p15 | 0.582818294 | -0.001228427 | -0.001259706 | -0.001197148 | 0.900000000 | 0.671641791 | 135 | 68 | 67 | -0.008189514 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_s4_p20 | 0.582818294 | -0.000942635 | 0.000000000 | -0.001885269 | 0.800000000 | 0.626865672 | 90 | 0 | 90 | -0.009426346 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_global_p10 | 0.582818294 | -0.000927595 | -0.000820028 | -0.001035162 | 0.900000000 | 0.671641791 | 90 | 45 | 45 | -0.009275948 | True |
| latent_human_late | hgb_shallow | dateblock5 | all3 | contrast | drop_global_top75 | 0.661498416 | -0.000797201 | -0.000735037 | -0.000859365 | 0.900000000 | 0.626865672 | 75 | 39 | 36 | -0.009566409 | True |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_global_top50 | 0.519019442 | -0.000782275 | -0.000546492 | -0.001018057 | 0.800000000 | 0.626865672 | 50 | 25 | 25 | -0.014080945 | True |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_each_top25 | 0.519019442 | -0.000782275 | -0.000546492 | -0.001018057 | 0.800000000 | 0.626865672 | 50 | 25 | 25 | -0.014080945 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_q3_p20 | 0.582818294 | -0.000746988 | -0.001493975 | 0.000000000 | 0.800000000 | 0.656716418 | 90 | 90 | 0 | -0.007469876 | True |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_top75 | 0.553870530 | -0.000690449 | -0.000583834 | -0.000797065 | 0.700000000 | 0.641791045 | 75 | 38 | 37 | -0.008285389 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_s4_top50 | 0.582818294 | -0.000651173 | 0.000000000 | -0.001302346 | 0.700000000 | 0.626865672 | 50 | 0 | 50 | -0.011721117 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_q3_top50 | 0.582818294 | -0.000634511 | -0.001269023 | 0.000000000 | 0.700000000 | 0.641791045 | 50 | 50 | 0 | -0.011421204 | True |
| latent_human_late | hgb_shallow | dateblock5 | q3s4 | contrast | drop_global_p10 | 0.578485740 | -0.000630667 | -0.000928058 | -0.000333276 | 0.700000000 | 0.626865672 | 90 | 44 | 46 | -0.006306671 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_q3_p15 | 0.582818294 | -0.000629853 | -0.001259706 | 0.000000000 | 0.700000000 | 0.641791045 | 68 | 68 | 0 | -0.008336291 | True |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_global_p05 | 0.519019442 | -0.000626499 | -0.000374786 | -0.000878213 | 0.700000000 | 0.626865672 | 45 | 23 | 22 | -0.012529988 | True |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_p05 | 0.553870530 | -0.000613890 | -0.000635470 | -0.000592310 | 0.700000000 | 0.626865672 | 45 | 23 | 22 | -0.012277804 | True |
| human_late | hgb_shallow | subject5 | q3s4 | contrast | drop_each_top21 | 0.519019442 | -0.000601807 | -0.000365882 | -0.000837731 | 0.700000000 | 0.626865672 | 42 | 21 | 21 | -0.012895863 | True |
| human_late | hgb_shallow | subject5 | q3s4 | risk | drop_s4_p15 | 0.582818294 | -0.000598574 | 0.000000000 | -0.001197148 | 0.700000000 | 0.626865672 | 68 | 0 | 68 | -0.007922303 | True |
| human_late | lr_l2_c0p10 | dateblock5 | q3s4 | risk | drop_global_p20 | 0.551977192 | -0.000582951 | -0.000024462 | -0.001141440 | 0.900000000 | 0.611940299 | 180 | 90 | 90 | -0.002914755 | True |
| human_core | lr_l2_c0p10 | dateblock5 | q3s4 | contrast | drop_global_top100 | 0.524332277 | -0.000582766 | -0.000269732 | -0.000895800 | 0.800000000 | 0.626865672 | 100 | 50 | 50 | -0.005244892 | True |

## Interpretation

If random controls pass frequently, E264's policy-level strict gate is not enough. The lifestyle representation can still be useful, but the next target must be sharper: cell-tail ranking AUC, top-cell overlap, and materialization-side public-free stress, not just broad rollback policy improvement.
