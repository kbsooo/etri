# Hourly Sequence Decoder Report

## Sources

| source | oof_path | submission_path |
| --- | --- | --- |
| hourly_logreg_k80_c003_sample | outputs/hourly_sequence_decoder_v1/oof_hourly_logreg_k80_c003_sample.csv | outputs/hourly_sequence_decoder_v1/submission_hourly_logreg_k80_c003_sample.csv |
| hourly_logreg_k120_c01_midtail | outputs/hourly_sequence_decoder_v1/oof_hourly_logreg_k120_c01_midtail.csv | outputs/hourly_sequence_decoder_v1/submission_hourly_logreg_k120_c01_midtail.csv |
| hourly_hgb_k80_l2_1_support | outputs/hourly_sequence_decoder_v1/oof_hourly_hgb_k80_l2_1_support.csv | outputs/hourly_sequence_decoder_v1/submission_hourly_hgb_k80_l2_1_support.csv |
| hourly_hgb_k120_l2_5_midtail | outputs/hourly_sequence_decoder_v1/oof_hourly_hgb_k120_l2_5_midtail.csv | outputs/hourly_sequence_decoder_v1/submission_hourly_hgb_k120_l2_5_midtail.csv |
| hourly_et_leaf4_k160_sample | outputs/hourly_sequence_decoder_v1/oof_hourly_et_leaf4_k160_sample.csv | outputs/hourly_sequence_decoder_v1/submission_hourly_et_leaf4_k160_sample.csv |
| hourly_et_leaf8_k160_midtail | outputs/hourly_sequence_decoder_v1/oof_hourly_et_leaf8_k160_midtail.csv | outputs/hourly_sequence_decoder_v1/submission_hourly_et_leaf8_k160_midtail.csv |

## Top Window Scores

| source | target | window | blend_weight | applied_rows | uniform_improvement | uniform_avg_log_loss | weighted_improvement | weighted_p025 | weighted_p500 | weighted_p975 | target_delta | weighted_target_delta | mid_delta | late_delta | tail20_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hourly_logreg_k80_c003_sample | S2 | tail | 0.650000 | 22 | 0.000416 | 0.577690 | 0.004086 | 0.002049 | 0.004110 | 0.006358 | 0.002913 | 0.028603 | 0.000000 | 0.001615 | 0.008513 |
| hourly_logreg_k80_c003_sample | S2 | tail | 0.500000 | 22 | 0.000384 | 0.577723 | 0.003770 | 0.002037 | 0.003790 | 0.005732 | 0.002688 | 0.026389 | 0.000000 | 0.001490 | 0.007854 |
| hourly_logreg_k80_c003_sample | S2 | tail | 0.800000 | 22 | 0.000424 | 0.577683 | 0.004160 | 0.001841 | 0.004200 | 0.006732 | 0.002966 | 0.029118 | 0.000000 | 0.001644 | 0.008666 |
| hourly_logreg_k80_c003_sample | S2 | tail | 0.300000 | 22 | 0.000289 | 0.577817 | 0.002841 | 0.001635 | 0.002853 | 0.004224 | 0.002026 | 0.019888 | 0.000000 | 0.001123 | 0.005919 |
| hourly_logreg_k80_c003_sample | S2 | tail | 1.000000 | 22 | 0.000405 | 0.577701 | 0.003978 | 0.001293 | 0.004024 | 0.006856 | 0.002836 | 0.027846 | 0.000000 | 0.001572 | 0.008287 |
| hourly_logreg_k120_c01_midtail | S2 | tail | 0.300000 | 22 | 0.000232 | 0.577874 | 0.002281 | 0.000671 | 0.002314 | 0.003941 | 0.001626 | 0.015969 | 0.000000 | 0.000901 | 0.004753 |
| hourly_logreg_k120_c01_midtail | Q2 | tail | 0.300000 | 22 | 0.000277 | 0.577830 | 0.002718 | 0.000592 | 0.002755 | 0.004822 | 0.001938 | 0.019025 | 0.000000 | 0.001074 | 0.005662 |
| hourly_hgb_k120_l2_5_midtail | Q3 | mid | 0.300000 | 102 | 0.000650 | 0.577456 | 0.001492 | 0.000550 | 0.001492 | 0.002386 | 0.004553 | 0.010444 | 0.002783 | 0.000124 | 0.000000 |
| hourly_hgb_k120_l2_5_midtail | Q3 | mid | 0.500000 | 102 | 0.000898 | 0.577209 | 0.002060 | 0.000495 | 0.002062 | 0.003531 | 0.006286 | 0.014420 | 0.003807 | 0.000202 | 0.000000 |
| hourly_et_leaf4_k160_sample | S2 | tail | 0.300000 | 22 | 0.000121 | 0.577985 | 0.001192 | 0.000421 | 0.001201 | 0.002060 | 0.000850 | 0.008346 | 0.000000 | 0.000471 | 0.002484 |
| hourly_et_leaf4_k160_sample | S2 | tail | 0.500000 | 22 | 0.000169 | 0.577937 | 0.001662 | 0.000411 | 0.001679 | 0.003078 | 0.001185 | 0.011632 | 0.000000 | 0.000657 | 0.003462 |
| hourly_et_leaf8_k160_midtail | Q3 | mid | 0.500000 | 102 | 0.000596 | 0.577511 | 0.001367 | 0.000378 | 0.001378 | 0.002387 | 0.004171 | 0.009568 | 0.002630 | 0.000044 | 0.000000 |
| hourly_logreg_k80_c003_sample | Q2 | tail | 0.300000 | 22 | 0.000165 | 0.577942 | 0.001616 | 0.000377 | 0.001632 | 0.002857 | 0.001152 | 0.011313 | 0.000000 | 0.000639 | 0.003367 |
| hourly_et_leaf8_k160_midtail | Q3 | mid | 0.300000 | 102 | 0.000411 | 0.577696 | 0.000942 | 0.000349 | 0.000946 | 0.001560 | 0.002876 | 0.006597 | 0.001817 | 0.000027 | 0.000000 |
| hourly_et_leaf8_k160_midtail | Q3 | mid | 0.650000 | 102 | 0.000688 | 0.577418 | 0.001579 | 0.000310 | 0.001591 | 0.002886 | 0.004819 | 0.011056 | 0.003032 | 0.000057 | 0.000000 |
| hourly_logreg_k80_c003_sample | S2 | mid_tail | 0.300000 | 124 | -0.000057 | 0.578164 | 0.002046 | 0.000275 | 0.002058 | 0.003878 | -0.000401 | 0.014321 | -0.001831 | 0.001356 | 0.005919 |
| hourly_hgb_k120_l2_5_midtail | Q3 | mid | 0.650000 | 102 | 0.000992 | 0.577115 | 0.002275 | 0.000256 | 0.002270 | 0.004170 | 0.006942 | 0.015926 | 0.004165 | 0.000257 | 0.000000 |
| hourly_et_leaf8_k160_midtail | S4 | tail | 0.500000 | 22 | 0.000091 | 0.578016 | 0.000891 | 0.000223 | 0.000896 | 0.001559 | 0.000635 | 0.006237 | 0.000000 | 0.000352 | 0.001856 |
| hourly_et_leaf4_k160_sample | S2 | tail | 0.650000 | 22 | 0.000188 | 0.577919 | 0.001845 | 0.000219 | 0.001868 | 0.003645 | 0.001315 | 0.012912 | 0.000000 | 0.000729 | 0.003843 |
| hourly_et_leaf8_k160_midtail | S2 | tail | 0.300000 | 22 | 0.000093 | 0.578014 | 0.000910 | 0.000214 | 0.000917 | 0.001716 | 0.000649 | 0.006368 | 0.000000 | 0.000359 | 0.001895 |
