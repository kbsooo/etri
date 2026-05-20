# Hourly Sequence Decoder Report

## Sources

| source | oof_path | submission_path |
| --- | --- | --- |
| hourly_logreg_k80_c003_sample | outputs/hourly_fused_sequence_decoder_on_v14/oof_hourly_logreg_k80_c003_sample.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_hourly_logreg_k80_c003_sample.csv |
| hourly_logreg_k120_c01_midtail | outputs/hourly_fused_sequence_decoder_on_v14/oof_hourly_logreg_k120_c01_midtail.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_hourly_logreg_k120_c01_midtail.csv |
| hourly_hgb_k80_l2_1_support | outputs/hourly_fused_sequence_decoder_on_v14/oof_hourly_hgb_k80_l2_1_support.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_hourly_hgb_k80_l2_1_support.csv |
| hourly_hgb_k120_l2_5_midtail | outputs/hourly_fused_sequence_decoder_on_v14/oof_hourly_hgb_k120_l2_5_midtail.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_hourly_hgb_k120_l2_5_midtail.csv |
| hourly_et_leaf4_k160_sample | outputs/hourly_fused_sequence_decoder_on_v14/oof_hourly_et_leaf4_k160_sample.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_hourly_et_leaf4_k160_sample.csv |
| hourly_et_leaf8_k160_midtail | outputs/hourly_fused_sequence_decoder_on_v14/oof_hourly_et_leaf8_k160_midtail.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_hourly_et_leaf8_k160_midtail.csv |
| fused_logreg_k200_c003_sample | outputs/hourly_fused_sequence_decoder_on_v14/oof_fused_logreg_k200_c003_sample.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_fused_logreg_k200_c003_sample.csv |
| fused_logreg_k260_c01_midtail | outputs/hourly_fused_sequence_decoder_on_v14/oof_fused_logreg_k260_c01_midtail.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_fused_logreg_k260_c01_midtail.csv |
| fused_logreg_k320_c03_tail | outputs/hourly_fused_sequence_decoder_on_v14/oof_fused_logreg_k320_c03_tail.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_fused_logreg_k320_c03_tail.csv |
| fused_hgb_k200_l2_5_midtail | outputs/hourly_fused_sequence_decoder_on_v14/oof_fused_hgb_k200_l2_5_midtail.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_fused_hgb_k200_l2_5_midtail.csv |
| fused_hgb_k260_l2_15_sample | outputs/hourly_fused_sequence_decoder_on_v14/oof_fused_hgb_k260_l2_15_sample.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_fused_hgb_k260_l2_15_sample.csv |
| fused_et_leaf12_k260_midtail | outputs/hourly_fused_sequence_decoder_on_v14/oof_fused_et_leaf12_k260_midtail.csv | outputs/hourly_fused_sequence_decoder_on_v14/submission_fused_et_leaf12_k260_midtail.csv |

## Top Window Scores

| source | target | window | blend_weight | applied_rows | uniform_improvement | uniform_avg_log_loss | weighted_improvement | weighted_p025 | weighted_p500 | weighted_p975 | target_delta | weighted_target_delta | mid_delta | late_delta | tail20_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fused_hgb_k260_l2_15_sample | S4 | tail | 1.000000 | 22 | 0.000696 | 0.575529 | 0.006833 | 0.005047 | 0.006819 | 0.008727 | 0.004871 | 0.047828 | 0.000000 | 0.002700 | 0.014234 |
| fused_hgb_k260_l2_15_sample | S4 | tail | 0.800000 | 22 | 0.000594 | 0.575631 | 0.005830 | 0.004361 | 0.005818 | 0.007415 | 0.004157 | 0.040810 | 0.000000 | 0.002304 | 0.012146 |
| fused_hgb_k260_l2_15_sample | S4 | tail | 0.650000 | 22 | 0.000506 | 0.575719 | 0.004963 | 0.003744 | 0.004954 | 0.006277 | 0.003539 | 0.034742 | 0.000000 | 0.001961 | 0.010340 |
| fused_hgb_k200_l2_5_midtail | S4 | tail | 1.000000 | 22 | 0.000506 | 0.575718 | 0.004968 | 0.003136 | 0.004912 | 0.006942 | 0.003542 | 0.034777 | 0.000000 | 0.001963 | 0.010350 |
| fused_hgb_k260_l2_15_sample | S4 | tail | 0.500000 | 22 | 0.000407 | 0.575818 | 0.003994 | 0.003033 | 0.003987 | 0.005025 | 0.002848 | 0.027958 | 0.000000 | 0.001578 | 0.008321 |
| fused_hgb_k200_l2_5_midtail | S4 | tail | 0.800000 | 22 | 0.000445 | 0.575779 | 0.004372 | 0.002856 | 0.004317 | 0.006039 | 0.003117 | 0.030607 | 0.000000 | 0.001728 | 0.009109 |
| fused_hgb_k200_l2_5_midtail | S4 | tail | 0.650000 | 22 | 0.000388 | 0.575837 | 0.003806 | 0.002552 | 0.003754 | 0.005192 | 0.002714 | 0.026643 | 0.000000 | 0.001504 | 0.007929 |
| fused_hgb_k200_l2_5_midtail | S4 | tail | 0.500000 | 22 | 0.000319 | 0.575906 | 0.003129 | 0.002142 | 0.003094 | 0.004239 | 0.002231 | 0.021906 | 0.000000 | 0.001236 | 0.006520 |
| fused_hgb_k260_l2_15_sample | S4 | tail | 0.300000 | 22 | 0.000259 | 0.575966 | 0.002539 | 0.001935 | 0.002534 | 0.003183 | 0.001810 | 0.017773 | 0.000000 | 0.001003 | 0.005290 |
| hourly_hgb_k120_l2_5_midtail | S4 | tail | 1.000000 | 22 | 0.000380 | 0.575845 | 0.003730 | 0.001797 | 0.003716 | 0.005661 | 0.002660 | 0.026113 | 0.000000 | 0.001474 | 0.007772 |
| hourly_hgb_k120_l2_5_midtail | S4 | tail | 0.800000 | 22 | 0.000337 | 0.575887 | 0.003311 | 0.001743 | 0.003304 | 0.004871 | 0.002361 | 0.023178 | 0.000000 | 0.001308 | 0.006898 |
| fused_logreg_k320_c03_tail | S3 | tail | 0.300000 | 22 | 0.000309 | 0.575915 | 0.003038 | 0.001704 | 0.003095 | 0.004462 | 0.002166 | 0.021264 | 0.000000 | 0.001200 | 0.006329 |
| hourly_hgb_k120_l2_5_midtail | S4 | tail | 0.650000 | 22 | 0.000295 | 0.575930 | 0.002896 | 0.001607 | 0.002884 | 0.004163 | 0.002065 | 0.020272 | 0.000000 | 0.001144 | 0.006033 |
| fused_logreg_k320_c03_tail | S3 | tail | 0.500000 | 22 | 0.000363 | 0.575861 | 0.003567 | 0.001572 | 0.003660 | 0.005763 | 0.002543 | 0.024970 | 0.000000 | 0.001409 | 0.007432 |
| hourly_hgb_k120_l2_5_midtail | S3 | tail | 0.800000 | 22 | 0.000344 | 0.575880 | 0.003379 | 0.001507 | 0.003284 | 0.005408 | 0.002409 | 0.023650 | 0.000000 | 0.001335 | 0.007039 |
| hourly_hgb_k120_l2_5_midtail | S3 | tail | 0.650000 | 22 | 0.000308 | 0.575917 | 0.003020 | 0.001461 | 0.002952 | 0.004680 | 0.002153 | 0.021138 | 0.000000 | 0.001193 | 0.006291 |
| fused_hgb_k200_l2_5_midtail | S4 | tail | 0.300000 | 22 | 0.000208 | 0.576016 | 0.002044 | 0.001425 | 0.002021 | 0.002749 | 0.001458 | 0.014311 | 0.000000 | 0.000808 | 0.004259 |
| hourly_hgb_k120_l2_5_midtail | S4 | tail | 0.500000 | 22 | 0.000243 | 0.575981 | 0.002390 | 0.001387 | 0.002390 | 0.003387 | 0.001704 | 0.016728 | 0.000000 | 0.000944 | 0.004979 |
| hourly_hgb_k120_l2_5_midtail | S3 | tail | 0.500000 | 22 | 0.000258 | 0.575966 | 0.002537 | 0.001321 | 0.002478 | 0.003827 | 0.001809 | 0.017758 | 0.000000 | 0.001002 | 0.005285 |
| fused_logreg_k200_c003_sample | Q2 | tail | 0.500000 | 22 | 0.000250 | 0.575975 | 0.002453 | 0.001318 | 0.002455 | 0.003775 | 0.001749 | 0.017170 | 0.000000 | 0.000969 | 0.005110 |
