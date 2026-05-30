# E234 Tail-Contrastive JEPA Target

## Question

Does changing the JEPA target from all-row support to high-impact tail representation make the E216/E224 movement more translatable?

## Observed Read

- Promoted tail-contrastive policies: `323`.
- Best Q3 dropped-row overlap with E230 risk-top21 among selected rows: `5`.

A healthy result needs more than tail AUC: it must beat the full movement OOF, keep subject stress alive, and for Q3 it should drop rows that resemble the E230 public-free fragile tail.

## Task Summary

| task | best_loss_vs_full | best_delta | full_delta | max_tail_auc | promote_count |
| --- | --- | --- | --- | --- | --- |
| s2_e216 | -0.002653627 | -0.007024051 | -0.004370425 | 0.862392482 | 215 |
| q3_e224 | -0.000870181 | -0.005132294 | -0.004262113 | 0.832222222 | 53 |
| s4_e224 | -0.000833194 | -0.004263330 | -0.003430136 | 0.916358025 | 55 |

## Promoted Policies

| task | view | model | split | target_kind | tail_q | policy | tail_auc | target_delta | loss_vs_full | subject_win_rate | dropped_rows | dropped_mean_benefit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.862392482 | -0.007024051 | -0.002653627 | 0.900000000 | 68 | -0.017560765 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top50 | 0.848757347 | -0.006511272 | -0.002140847 | 0.800000000 | 50 | -0.019267622 |
| s2_e216 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.754844042 | -0.006406024 | -0.002035599 | 0.900000000 | 68 | -0.013470879 |
| s2_e216 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.754844042 | -0.006406024 | -0.002035599 | 0.900000000 | 68 | -0.013470879 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p10 | 0.848757347 | -0.006318801 | -0.001948376 | 0.800000000 | 45 | -0.019483761 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top21 | 0.848757347 | -0.006027595 | -0.001657170 | 0.600000000 | 21 | -0.035510785 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_p05 | 0.581457199 | -0.006024314 | -0.001653890 | 0.700000000 | 22 | -0.033829562 |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p05 | 0.862392482 | -0.006008474 | -0.001638049 | 0.900000000 | 22 | -0.033505556 |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_top25 | 0.862392482 | -0.005932355 | -0.001561931 | 0.900000000 | 25 | -0.028114750 |
| s2_e216 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_top50 | 0.754844042 | -0.005883142 | -0.001512717 | 0.800000000 | 50 | -0.013614457 |
| s2_e216 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_top50 | 0.754844042 | -0.005883142 | -0.001512717 | 0.800000000 | 50 | -0.013614457 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.300000000 | drop_risk_top50 | 0.778303892 | -0.005849972 | -0.001479547 | 0.800000000 | 50 | -0.013315923 |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_top21 | 0.862392482 | -0.005831161 | -0.001460737 | 0.900000000 | 21 | -0.031301500 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p05 | 0.848757347 | -0.005780397 | -0.001409972 | 0.600000000 | 22 | -0.028840341 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_p20 | 0.581457199 | -0.005763350 | -0.001392925 | 0.800000000 | 90 | -0.006964626 |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p10 | 0.862392482 | -0.005746819 | -0.001376394 | 0.800000000 | 45 | -0.013763940 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_p10 | 0.581457199 | -0.005717331 | -0.001346906 | 0.700000000 | 45 | -0.013469059 |
| s2_e216 | latent_no_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p15 | 0.841489905 | -0.005690750 | -0.001320325 | 0.700000000 | 68 | -0.008737447 |
| s2_e216 | latent_with_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p15 | 0.841489905 | -0.005690750 | -0.001320325 | 0.700000000 | 68 | -0.008737447 |
| s2_e216 | latent_with_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_top21 | 0.841562337 | -0.005669868 | -0.001299443 | 0.700000000 | 21 | -0.027845210 |
| s2_e216 | latent_no_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_top21 | 0.841562337 | -0.005669868 | -0.001299443 | 0.700000000 | 21 | -0.027845210 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top25 | 0.581457199 | -0.005669282 | -0.001298857 | 0.700000000 | 25 | -0.023379423 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top50 | 0.581457199 | -0.005660154 | -0.001289729 | 0.700000000 | 50 | -0.011607563 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.300000000 | drop_lowpos_top13 | 0.579724616 | -0.005566444 | -0.001196019 | 0.600000000 | 13 | -0.041400664 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top21 | 0.581457199 | -0.005555832 | -0.001185407 | 0.700000000 | 21 | -0.025401581 |
| s2_e216 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | risk_linear_t0p60 | 0.754844042 | -0.005539198 | -0.001168773 | 0.900000000 | 6 | -0.038310250 |
| s2_e216 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | risk_linear_t0p60 | 0.754844042 | -0.005539198 | -0.001168773 | 0.900000000 | 6 | -0.038310250 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_p15 | 0.581457199 | -0.005521037 | -0.001150612 | 0.800000000 | 68 | -0.007614346 |
| s2_e216 | latent_with_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p10 | 0.841489905 | -0.005468608 | -0.001098184 | 0.700000000 | 45 | -0.010981835 |
| s2_e216 | latent_no_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p10 | 0.841489905 | -0.005468608 | -0.001098184 | 0.700000000 | 45 | -0.010981835 |
| s2_e216 | latent_no_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_top13 | 0.841562337 | -0.005451222 | -0.001080798 | 0.600000000 | 13 | -0.037412224 |
| s2_e216 | latent_with_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_top13 | 0.841562337 | -0.005451222 | -0.001080798 | 0.600000000 | 13 | -0.037412224 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p20 | 0.848757347 | -0.005431089 | -0.001060665 | 0.800000000 | 90 | -0.005303323 |
| s2_e216 | movement | lr_l2_c0p10 | subject5 | contrast | 0.200000000 | drop_lowpos_p05 | 0.481197427 | -0.005403778 | -0.001033353 | 0.600000000 | 22 | -0.021136765 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.300000000 | drop_risk_p10 | 0.778303892 | -0.005396778 | -0.001026353 | 0.800000000 | 45 | -0.010263529 |
| s2_e216 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | risk_linear_t0p50 | 0.754844042 | -0.005389480 | -0.001019056 | 0.900000000 | 6 | -0.038310250 |
| s2_e216 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | risk_linear_t0p50 | 0.754844042 | -0.005389480 | -0.001019056 | 0.900000000 | 6 | -0.038310250 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.300000000 | drop_risk_top13 | 0.778303892 | -0.005383467 | -0.001013043 | 0.600000000 | 13 | -0.035066865 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top13 | 0.581457199 | -0.005372347 | -0.001001922 | 0.600000000 | 13 | -0.034681912 |
| s2_e216 | movement | lr_l2_c0p10 | subject5 | contrast | 0.200000000 | drop_lowpos_top21 | 0.481197427 | -0.005372166 | -0.001001742 | 0.600000000 | 21 | -0.021465893 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.300000000 | drop_lowpos_top10 | 0.579724616 | -0.005312529 | -0.000942104 | 0.600000000 | 10 | -0.042394682 |
| s2_e216 | movement | hgb_shallow | subject5 | contrast | 0.300000000 | drop_lowpos_p15 | 0.579724616 | -0.005294934 | -0.000924509 | 0.700000000 | 68 | -0.006118076 |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_top50 | 0.862392482 | -0.005291882 | -0.000921457 | 0.800000000 | 50 | -0.008293116 |
| s2_e216 | latent_no_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top25 | 0.841489905 | -0.005289389 | -0.000918965 | 0.700000000 | 25 | -0.016541362 |
| s2_e216 | latent_with_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top25 | 0.841489905 | -0.005289389 | -0.000918965 | 0.700000000 | 25 | -0.016541362 |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | risk_linear_t0p50 | 0.862392482 | -0.005282422 | -0.000911998 | 0.700000000 | 0 |  |
| s2_e216 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_p10 | 0.754844042 | -0.005266810 | -0.000896386 | 0.700000000 | 45 | -0.008963856 |
| s2_e216 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_p10 | 0.754844042 | -0.005266810 | -0.000896386 | 0.700000000 | 45 | -0.008963856 |
| s2_e216 | latent_with_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.841562337 | -0.005260800 | -0.000890375 | 0.900000000 | 68 | -0.005892188 |
| s2_e216 | latent_no_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.841562337 | -0.005260800 | -0.000890375 | 0.900000000 | 68 | -0.005892188 |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p15 | 0.848757347 | -0.005258969 | -0.000888544 | 0.800000000 | 68 | -0.005880070 |
| s2_e216 | latent_no_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p05 | 0.841562337 | -0.005251573 | -0.000881149 | 0.700000000 | 22 | -0.018023494 |
| s2_e216 | latent_with_targetid | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p05 | 0.841562337 | -0.005251573 | -0.000881149 | 0.700000000 | 22 | -0.018023494 |
| q3_e224 | latent_no_targetid | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top25 | 0.503702819 | -0.005132294 | -0.000870181 | 0.700000000 | 25 | -0.015663261 |
| q3_e224 | latent_with_targetid | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top25 | 0.503702819 | -0.005132294 | -0.000870181 | 0.700000000 | 25 | -0.015663261 |
| s2_e216 | movement | hgb_shallow | stratified5 | contrast | 0.200000000 | drop_lowpos_p20 | 0.624260355 | -0.005239714 | -0.000869290 | 0.700000000 | 90 | -0.004346449 |
| s2_e216 | latent_no_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top13 | 0.841489905 | -0.005231259 | -0.000860834 | 0.600000000 | 13 | -0.029798099 |
| s2_e216 | latent_with_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top13 | 0.841489905 | -0.005231259 | -0.000860834 | 0.600000000 | 13 | -0.029798099 |
| s2_e216 | latent_with_targetid | hgb_shallow | subject5 | risk | 0.300000000 | drop_risk_top10 | 0.731366900 | -0.005222028 | -0.000851604 | 0.700000000 | 10 | -0.038322164 |
| s2_e216 | latent_no_targetid | hgb_shallow | subject5 | risk | 0.300000000 | drop_risk_top10 | 0.731366900 | -0.005222028 | -0.000851604 | 0.700000000 | 10 | -0.038322164 |

## Best Policies By Task

| task | view | model | split | target_kind | tail_q | policy | tail_auc | corr_benefit | target_delta | full_target_delta | loss_vs_full | subject_win_rate | dropped_rows | dropped_mean_benefit | stress_promote |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_e224 | latent_no_targetid | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top25 | 0.503702819 | 0.050013984 | -0.005132294 | -0.004262113 | -0.000870181 | 0.700000000 | 25 | -0.015663261 | True |
| q3_e224 | latent_with_targetid | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_top25 | 0.503702819 | 0.050013984 | -0.005132294 | -0.004262113 | -0.000870181 | 0.700000000 | 25 | -0.015663261 | True |
| q3_e224 | latent_no_targetid | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_p20 | 0.503702819 | 0.050013984 | -0.004922648 | -0.004262113 | -0.000660535 | 0.600000000 | 90 | -0.003302675 | True |
| q3_e224 | latent_with_targetid | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_p20 | 0.503702819 | 0.050013984 | -0.004922648 | -0.004262113 | -0.000660535 | 0.600000000 | 90 | -0.003302675 | True |
| q3_e224 | latent_no_targetid | hgb_shallow | subject5 | contrast | 0.200000000 | drop_lowpos_p15 | 0.503702819 | 0.050013984 | -0.004880964 | -0.004262113 | -0.000618851 | 0.700000000 | 68 | -0.004095337 | True |
| s2_e216 | movement | hgb_shallow | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.862392482 | -0.064069246 | -0.007024051 | -0.004370425 | -0.002653627 | 0.900000000 | 68 | -0.017560765 | True |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top50 | 0.848757347 | -0.047673600 | -0.006511272 | -0.004370425 | -0.002140847 | 0.800000000 | 50 | -0.019267622 | True |
| s2_e216 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.754844042 | -0.017876168 | -0.006406024 | -0.004370425 | -0.002035599 | 0.900000000 | 68 | -0.013470879 | True |
| s2_e216 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.200000000 | drop_risk_p15 | 0.754844042 | -0.017876168 | -0.006406024 | -0.004370425 | -0.002035599 | 0.900000000 | 68 | -0.013470879 | True |
| s2_e216 | movement | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_p10 | 0.848757347 | -0.047673600 | -0.006318801 | -0.004370425 | -0.001948376 | 0.800000000 | 45 | -0.019483761 | True |
| s4_e224 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.300000000 | drop_risk_p15 | 0.718944749 | -0.025187166 | -0.004263330 | -0.003430136 | -0.000833194 | 0.800000000 | 68 | -0.005513783 | True |
| s4_e224 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.300000000 | drop_risk_p15 | 0.718944749 | -0.025187166 | -0.004263330 | -0.003430136 | -0.000833194 | 0.800000000 | 68 | -0.005513783 | True |
| s4_e224 | latent_no_targetid | lr_l2_c0p10 | stratified5 | risk | 0.300000000 | drop_risk_top50 | 0.718944749 | -0.025187166 | -0.004048227 | -0.003430136 | -0.000618092 | 0.800000000 | 50 | -0.005562824 | True |
| s4_e224 | latent_with_targetid | lr_l2_c0p10 | stratified5 | risk | 0.300000000 | drop_risk_top50 | 0.718944749 | -0.025187166 | -0.004048227 | -0.003430136 | -0.000618092 | 0.800000000 | 50 | -0.005562824 | True |
| s4_e224 | latent_no_targetid | hgb_shallow | subject5 | risk | 0.200000000 | drop_risk_top13 | 0.866802283 | 0.153238301 | -0.004033465 | -0.003430136 | -0.000603330 | 0.800000000 | 13 | -0.020884488 | True |

## Selected Test Alignment

| task | view | model | target_kind | tail_q | policy | sub_mean_prob | sub_mean_amp | sub_dropped_rows | sub_p10_prob | sub_p50_prob | sub_p90_prob | e230_q3_risk_top21_overlap | e230_q3_risk_top21_jaccard | e230_q3_swing_top25_overlap | e230_q3_swing_top25_jaccard | e230_q3_expected_positive_overlap | e230_q3_expected_positive_jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q3_e224 | latent_no_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_top25 | 0.495629845 | 0.900000000 | 25 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.045454545 | 3 | 0.063829787 | 8 | 0.062500000 |
| q3_e224 | latent_with_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_top25 | 0.495629845 | 0.900000000 | 25 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.045454545 | 3 | 0.063829787 | 8 | 0.062500000 |
| q3_e224 | latent_no_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p20 | 0.495629845 | 0.800000000 | 50 | 0.276365159 | 0.500867507 | 0.705760609 | 3 | 0.044117647 | 3 | 0.041666667 | 20 | 0.141843972 |
| q3_e224 | latent_with_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p20 | 0.495629845 | 0.800000000 | 50 | 0.276365159 | 0.500867507 | 0.705760609 | 3 | 0.044117647 | 3 | 0.041666667 | 20 | 0.141843972 |
| q3_e224 | latent_no_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p15 | 0.495629845 | 0.848000000 | 38 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.035087719 | 3 | 0.050000000 | 15 | 0.111940299 |
| q3_e224 | latent_with_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p15 | 0.495629845 | 0.848000000 | 38 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.035087719 | 3 | 0.050000000 | 15 | 0.111940299 |
| q3_e224 | latent_no_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_top50 | 0.495629845 | 0.800000000 | 50 | 0.276365159 | 0.500867507 | 0.705760609 | 3 | 0.044117647 | 3 | 0.041666667 | 20 | 0.141843972 |
| q3_e224 | latent_with_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_top50 | 0.495629845 | 0.800000000 | 50 | 0.276365159 | 0.500867507 | 0.705760609 | 3 | 0.044117647 | 3 | 0.041666667 | 20 | 0.141843972 |
| q3_e224 | latent_no_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p10 | 0.495629845 | 0.900000000 | 25 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.045454545 | 3 | 0.063829787 | 8 | 0.062500000 |
| q3_e224 | latent_with_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p10 | 0.495629845 | 0.900000000 | 25 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.045454545 | 3 | 0.063829787 | 8 | 0.062500000 |
| q3_e224 | latent_no_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p05 | 0.495629845 | 0.952000000 | 12 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.064516129 | 3 | 0.088235294 | 3 | 0.025000000 |
| q3_e224 | latent_with_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_p05 | 0.495629845 | 0.952000000 | 12 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.064516129 | 3 | 0.088235294 | 3 | 0.025000000 |
| q3_e224 | latent_no_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_top21 | 0.495629845 | 0.916000000 | 21 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.050000000 | 3 | 0.069767442 | 5 | 0.039370079 |
| q3_e224 | latent_with_targetid | hgb_shallow | contrast | 0.200000000 | drop_lowpos_top21 | 0.495629845 | 0.916000000 | 21 | 0.276365159 | 0.500867507 | 0.705760609 | 2 | 0.050000000 | 3 | 0.069767442 | 5 | 0.039370079 |
| q3_e224 | latent_no_targetid | hgb_shallow | risk | 0.300000000 | drop_risk_p20 | 0.270638873 | 0.800000000 | 50 | 0.030247885 | 0.230584766 | 0.588790835 | 5 | 0.075757576 | 6 | 0.086956522 | 14 | 0.095238095 |
| q3_e224 | latent_with_targetid | hgb_shallow | risk | 0.300000000 | drop_risk_p20 | 0.270638873 | 0.800000000 | 50 | 0.030247885 | 0.230584766 | 0.588790835 | 5 | 0.075757576 | 6 | 0.086956522 | 14 | 0.095238095 |
| q3_e224 | latent_no_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top13 | 0.396912058 | 0.948000000 | 13 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.030303030 | 2 | 0.055555556 | 6 | 0.050847458 |
| q3_e224 | latent_with_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top13 | 0.396912058 | 0.948000000 | 13 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.030303030 | 2 | 0.055555556 | 6 | 0.050847458 |
| q3_e224 | latent_no_targetid | lr_l2_c0p10 | contrast | 0.300000000 | drop_lowpos_p05 | 0.391428024 | 0.952000000 | 12 | 0.085580976 | 0.348775060 | 0.768110017 | 1 | 0.031250000 | 1 | 0.027777778 | 6 | 0.051282051 |
| q3_e224 | latent_with_targetid | lr_l2_c0p10 | contrast | 0.300000000 | drop_lowpos_p05 | 0.391428024 | 0.952000000 | 12 | 0.085580976 | 0.348775060 | 0.768110017 | 1 | 0.031250000 | 1 | 0.027777778 | 6 | 0.051282051 |
| q3_e224 | latent_no_targetid | lr_l2_c0p10 | contrast | 0.300000000 | drop_lowpos_top21 | 0.391428024 | 0.916000000 | 21 | 0.085580976 | 0.348775060 | 0.768110017 | 3 | 0.076923077 | 1 | 0.022222222 | 8 | 0.064516129 |
| q3_e224 | latent_with_targetid | lr_l2_c0p10 | contrast | 0.300000000 | drop_lowpos_top21 | 0.391428024 | 0.916000000 | 21 | 0.085580976 | 0.348775060 | 0.768110017 | 3 | 0.076923077 | 1 | 0.022222222 | 8 | 0.064516129 |
| q3_e224 | latent_no_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_p05 | 0.396912058 | 0.952000000 | 12 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.031250000 | 2 | 0.057142857 | 5 | 0.042372881 |
| q3_e224 | latent_with_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_p05 | 0.396912058 | 0.952000000 | 12 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.031250000 | 2 | 0.057142857 | 5 | 0.042372881 |
| q3_e224 | latent_no_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top21 | 0.396912058 | 0.916000000 | 21 | 0.090522649 | 0.347079677 | 0.784107053 | 3 | 0.076923077 | 3 | 0.069767442 | 8 | 0.064516129 |
| q3_e224 | latent_with_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top21 | 0.396912058 | 0.916000000 | 21 | 0.090522649 | 0.347079677 | 0.784107053 | 3 | 0.076923077 | 3 | 0.069767442 | 8 | 0.064516129 |
| q3_e224 | latent_no_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top10 | 0.396912058 | 0.960000000 | 10 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.033333333 | 2 | 0.060606061 | 4 | 0.034188034 |
| q3_e224 | latent_with_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top10 | 0.396912058 | 0.960000000 | 10 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.033333333 | 2 | 0.060606061 | 4 | 0.034188034 |
| q3_e224 | latent_no_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top13 | 0.396912058 | 0.948000000 | 13 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.030303030 | 2 | 0.055555556 | 6 | 0.050847458 |
| q3_e224 | latent_with_targetid | lr_l2_c0p10 | contrast | 0.200000000 | drop_lowpos_top13 | 0.396912058 | 0.948000000 | 13 | 0.090522649 | 0.347079677 | 0.784107053 | 1 | 0.030303030 | 2 | 0.055555556 | 6 | 0.050847458 |

## Decision

- At least one tail-contrastive policy beat full OOF movement under stress.
- Treat promoted rows as materialization candidates only after checking target-side public-free tail anatomy and collinearity with E224/E216.
