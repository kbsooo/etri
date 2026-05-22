# S2 Opportunity Drift Calibration

## Purpose

Stress-test the strongest fixed S2 opportunity/Q-state readout with fold-safe, train-derived calibration rules. The v83 S2 drift is recorded only as a diagnostic; candidate selection uses train rates and sample subject composition.

## Result

- Raw fixed S2 logloss: `0.558302`
- Raw projected fixed-map avg: `0.608974`
- Raw sample S2 mean: `0.678904`
- Raw posterior subject gap: `0.025971`
- Selected train-safe candidate: `subject_anchor_posterior_s0.75`
- Selected S2 logloss: `0.555910`
- Selected projected fixed-map avg: `0.608632`
- Selected sample S2 mean: `0.663356`
- Selected posterior subject gap: `0.006493`
- Protected fixed-map S2 reference: `0.567195`

## Top By S2 Loss

| candidate | family | s2_log_loss | delta_vs_raw | delta_vs_protected | projected_fixed_map_avg | sample_s2_mean | mean_abs_subject_gap_posterior | folds_better_than_raw | mean_abs_s2_drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_intercept_s1 | global_intercept | 0.555725 | 0.002577 | 0.011470 | 0.608606 | 0.651111 | 0.020416 | 2 | 0.082620 |
| subject_anchor_posterior_s0.75 | subject_anchor_posterior | 0.555910 | 0.002392 | 0.011285 | 0.608632 | 0.663356 | 0.006493 | 3 | 0.079255 |
| subject_cap_posterior_m0.03 | subject_cap_posterior | 0.555968 | 0.002334 | 0.011227 | 0.608641 | 0.672787 | 0.019774 | 3 | 0.083058 |
| subject_anchor_posterior_s1 | subject_anchor_posterior | 0.556087 | 0.002214 | 0.011108 | 0.608658 | 0.658174 | 0.000000 | 3 | 0.079256 |
| global_intercept_s0.75 | global_intercept | 0.556098 | 0.002204 | 0.011097 | 0.608659 | 0.658059 | 0.019443 | 3 | 0.082186 |
| subject_anchor_posterior_s0.5 | subject_anchor_posterior | 0.556204 | 0.002098 | 0.010991 | 0.608674 | 0.668539 | 0.012986 | 3 | 0.080430 |
| subject_cap_posterior_m0.05 | subject_cap_posterior | 0.556278 | 0.002024 | 0.010917 | 0.608685 | 0.678063 | 0.025087 | 3 | 0.083924 |
| subject_anchor_posterior_s0.35 | subject_anchor_posterior | 0.556615 | 0.001687 | 0.010580 | 0.608733 | 0.671648 | 0.016881 | 3 | 0.081409 |
| global_intercept_s0.5 | global_intercept | 0.556649 | 0.001653 | 0.010546 | 0.608738 | 0.665008 | 0.019461 | 3 | 0.082424 |
| subject_cap_posterior_m0.08 | subject_cap_posterior | 0.557059 | 0.001243 | 0.010136 | 0.608796 | 0.678904 | 0.025971 | 3 | 0.084029 |
| global_intercept_s0.35 | global_intercept | 0.557067 | 0.001235 | 0.010128 | 0.608798 | 0.669177 | 0.020832 | 3 | 0.082809 |
| subject_anchor_posterior_s0.2 | subject_anchor_posterior | 0.557210 | 0.001092 | 0.009985 | 0.608818 | 0.674758 | 0.020777 | 3 | 0.082451 |
| global_intercept_s0.2 | global_intercept | 0.557551 | 0.000750 | 0.009644 | 0.608867 | 0.673345 | 0.022271 | 3 | 0.083273 |
| subject_cap_posterior_m0.1 | subject_cap_posterior | 0.557620 | 0.000682 | 0.009575 | 0.608877 | 0.678904 | 0.025971 | 1 | 0.084029 |
| subject_anchor_posterior_s0.1 | subject_anchor_posterior | 0.557712 | 0.000590 | 0.009483 | 0.608890 | 0.676831 | 0.023374 | 3 | 0.083209 |

## Train-Safe Frontier

| candidate | s2_log_loss | delta_vs_protected | projected_fixed_map_avg | sample_s2_mean | abs_sample_mean_gap_posterior | mean_abs_subject_gap_posterior | folds_better_than_raw | mean_abs_s2_drift |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject_anchor_posterior_s0.75 | 0.555910 | 0.011285 | 0.608632 | 0.663356 | 0.005183 | 0.006493 | 3 | 0.079255 |
| subject_cap_posterior_m0.03 | 0.555968 | 0.011227 | 0.608641 | 0.672787 | 0.014613 | 0.019774 | 3 | 0.083058 |
| subject_anchor_posterior_s1 | 0.556087 | 0.011108 | 0.608658 | 0.658174 | 0.000000 | 0.000000 | 3 | 0.079256 |
| global_intercept_s0.75 | 0.556098 | 0.011097 | 0.608659 | 0.658059 | 0.000114 | 0.019443 | 3 | 0.082186 |
| subject_anchor_posterior_s0.5 | 0.556204 | 0.010991 | 0.608674 | 0.668539 | 0.010365 | 0.012986 | 3 | 0.080430 |
| subject_cap_posterior_m0.05 | 0.556278 | 0.010917 | 0.608685 | 0.678063 | 0.019889 | 0.025087 | 3 | 0.083924 |
| subject_anchor_posterior_s0.35 | 0.556615 | 0.010580 | 0.608733 | 0.671648 | 0.013475 | 0.016881 | 3 | 0.081409 |
| global_intercept_s0.5 | 0.556649 | 0.010546 | 0.608738 | 0.665008 | 0.006834 | 0.019461 | 3 | 0.082424 |
| subject_cap_posterior_m0.08 | 0.557059 | 0.010136 | 0.608796 | 0.678904 | 0.020730 | 0.025971 | 3 | 0.084029 |
| global_intercept_s0.35 | 0.557067 | 0.010128 | 0.608798 | 0.669177 | 0.011003 | 0.020832 | 3 | 0.082809 |
| subject_anchor_posterior_s0.2 | 0.557210 | 0.009985 | 0.608818 | 0.674758 | 0.016584 | 0.020777 | 3 | 0.082451 |
| global_intercept_s0.2 | 0.557551 | 0.009644 | 0.608867 | 0.673345 | 0.015172 | 0.022271 | 3 | 0.083273 |
| subject_anchor_posterior_s0.1 | 0.557712 | 0.009483 | 0.608890 | 0.676831 | 0.018657 | 0.023374 | 3 | 0.083209 |
| global_intercept_s0.1 | 0.557912 | 0.009283 | 0.608918 | 0.676125 | 0.017951 | 0.024041 | 3 | 0.083617 |
| subject_anchor_posterior_s0.05 | 0.557996 | 0.009199 | 0.608930 | 0.677868 | 0.019694 | 0.024673 | 3 | 0.083601 |

## Read

- A global intercept gives the lowest single OOF loss, but it improves only 2/5 folds versus the raw readout.
- The selected posterior anchor keeps the S2 gain, improves 3/5 folds, and reduces train-derived posterior rate stress without using v83 as a teacher.
- A candidate is useful only if it still beats the protected S2 scout after fold and rate-stress checks.
