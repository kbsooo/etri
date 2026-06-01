# H018 Hard-Label Public-World HS-JEPA

## Question

Does the public-equation latent survive when the hidden public labels are forced to be binary worlds?

- sampled hard worlds: `90000`

## Top Hard-World Posteriors

| posterior_id | method | temperature | top_k | weight_power | posterior_pred_mae | posterior_pred_p90_abs | best_world_mae | top100_world_mae | ess | ess_rate | q_prior_abs_shift | q_prior_corr | hardness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| soft_t0.00035_p1.5 | soft | 0.000350000 | 0 | 1.500000000 | 0.000005557 | 0.000017261 | 0.000167740 | 0.000252967 | 19756.395104281 | 0.219515501 | 0.002394823 | 0.999879785 | 0.701796427 |
| soft_t0.0002_p1 | soft | 0.000200000 | 0 | 1.000000000 | 0.000005742 | 0.000017890 | 0.000167740 | 0.000252967 | 16293.344045887 | 0.181037156 | 0.002643677 | 0.999855917 | 0.701821408 |
| soft_t0.0006_p2 | soft | 0.000600000 | 0 | 2.000000000 | 0.000005928 | 0.000015853 | 0.000167740 | 0.000252967 | 25989.928040797 | 0.288776978 | 0.002081166 | 0.999909162 | 0.701765617 |
| soft_t0.00035_p1 | soft | 0.000350000 | 0 | 1.000000000 | 0.000006313 | 0.000014713 | 0.000167740 | 0.000252967 | 30129.045634861 | 0.334767174 | 0.001930519 | 0.999921690 | 0.701749718 |
| soft_t0.00035_p2 | soft | 0.000350000 | 0 | 2.000000000 | 0.000006072 | 0.000018338 | 0.000167740 | 0.000252967 | 13542.473483608 | 0.150471928 | 0.002900427 | 0.999825174 | 0.701846812 |
| soft_t0.0006_p1.5 | soft | 0.000600000 | 0 | 1.500000000 | 0.000006694 | 0.000013555 | 0.000167740 | 0.000252967 | 33879.930271161 | 0.376443670 | 0.001817918 | 0.999929612 | 0.701737060 |
| soft_t0.00012_p1.5 | soft | 0.000120000 | 0 | 1.500000000 | 0.000008532 | 0.000017526 | 0.000167740 | 0.000252967 | 2914.214676873 | 0.032380163 | 0.006373895 | 0.999189579 | 0.702249223 |
| elite1000 | elite | 0.000000000 | 1000 | 1.000000000 | 0.000009382 | 0.000024686 | 0.000167740 | 0.000252967 | 1000.000000000 | 0.011111111 | 0.010751188 | 0.997824724 | 0.702755974 |
| soft_t0.00012_p2 | soft | 0.000120000 | 0 | 2.000000000 | 0.000009579 | 0.000021013 | 0.000167740 | 0.000252967 | 1308.968650621 | 0.014544096 | 0.009492043 | 0.998204319 | 0.702567280 |
| top1000_t0.001 | topk | 0.001000000 | 1000 | 1.000000000 | 0.000009425 | 0.000025996 | 0.000167740 | 0.000252967 | 998.571330201 | 0.011095237 | 0.010771421 | 0.997816441 | 0.702770771 |
| soft_t0.0002_p1.5 | soft | 0.000200000 | 0 | 1.500000000 | 0.000006945 | 0.000019127 | 0.000167740 | 0.000252967 | 8739.363902094 | 0.097104043 | 0.003628380 | 0.999727010 | 0.701923868 |
| soft_t0.00012_p1 | soft | 0.000120000 | 0 | 1.000000000 | 0.000007287 | 0.000019427 | 0.000167740 | 0.000252967 | 7190.764504420 | 0.079897383 | 0.004009856 | 0.999671248 | 0.701971542 |
| top1000_t0.0005 | topk | 0.000500000 | 1000 | 1.000000000 | 0.000009504 | 0.000027284 | 0.000167740 | 0.000252967 | 994.090011449 | 0.011045445 | 0.010811432 | 0.997800501 | 0.702786103 |
| soft_t0.0002_p2 | soft | 0.000200000 | 0 | 2.000000000 | 0.000007847 | 0.000019950 | 0.000167740 | 0.000252967 | 4942.131641474 | 0.054912574 | 0.004868577 | 0.999524401 | 0.702077948 |
| top1000_t0.00025 | topk | 0.000250000 | 1000 | 1.000000000 | 0.000009668 | 0.000029785 | 0.000167740 | 0.000252967 | 974.910276506 | 0.010832336 | 0.010951113 | 0.997725442 | 0.702820550 |
| top5000_t0.00012 | topk | 0.000120000 | 5000 | 1.000000000 | 0.000009069 | 0.000020380 | 0.000167740 | 0.000252967 | 3416.796201897 | 0.037964402 | 0.005861206 | 0.999318765 | 0.702201529 |
| soft_t0.001_p2 | soft | 0.001000000 | 0 | 2.000000000 | 0.000008284 | 0.000013526 | 0.000167740 | 0.000252967 | 40420.577578972 | 0.449117529 | 0.001663633 | 0.999940521 | 0.701717758 |
| top5000_t0.00025 | topk | 0.000250000 | 5000 | 1.000000000 | 0.000008898 | 0.000020054 | 0.000167740 | 0.000252967 | 4623.942992043 | 0.051377144 | 0.004997204 | 0.999505669 | 0.702039252 |
| top5000_t0.0005 | topk | 0.000500000 | 5000 | 1.000000000 | 0.000008871 | 0.000019942 | 0.000167740 | 0.000252967 | 4910.948700202 | 0.054566097 | 0.004830303 | 0.999536658 | 0.701988685 |
| elite5000 | elite | 0.000000000 | 5000 | 1.000000000 | 0.000008874 | 0.000019851 | 0.000167740 | 0.000252967 | 5000.000000000 | 0.055555556 | 0.004778679 | 0.999550292 | 0.701950490 |
| top5000_t0.001 | topk | 0.001000000 | 5000 | 1.000000000 | 0.000008874 | 0.000019894 | 0.000167740 | 0.000252967 | 4978.628919792 | 0.055318099 | 0.004790346 | 0.999543539 | 0.701968373 |
| top2500_t0.00012 | topk | 0.000120000 | 2500 | 1.000000000 | 0.000010233 | 0.000022652 | 0.000167740 | 0.000252967 | 1985.461302117 | 0.022060681 | 0.007739903 | 0.998817450 | 0.702478405 |
| top2500_t0.00025 | topk | 0.000250000 | 2500 | 1.000000000 | 0.000010872 | 0.000023552 | 0.000167740 | 0.000252967 | 2386.969022892 | 0.026521878 | 0.007012782 | 0.999036368 | 0.702361469 |
| soft_t0.0006_p1 | soft | 0.000600000 | 0 | 1.000000000 | 0.000009796 | 0.000015011 | 0.000167740 | 0.000252967 | 45928.275436205 | 0.510314172 | 0.001561191 | 0.999947193 | 0.701704053 |
| top1000_t0.00012 | topk | 0.000120000 | 1000 | 1.000000000 | 0.000010931 | 0.000034782 | 0.000167740 | 0.000252967 | 881.506286962 | 0.009794514 | 0.011531510 | 0.997461807 | 0.702913708 |
| top2500_t0.0005 | topk | 0.000500000 | 2500 | 1.000000000 | 0.000011261 | 0.000024000 | 0.000167740 | 0.000252967 | 2473.443492058 | 0.027482705 | 0.006845551 | 0.999081670 | 0.702320420 |
| top2500_t0.001 | topk | 0.001000000 | 2500 | 1.000000000 | 0.000011471 | 0.000024191 | 0.000167740 | 0.000252967 | 2493.612059978 | 0.027706801 | 0.006798595 | 0.999091705 | 0.702305100 |
| elite2500 | elite | 0.000000000 | 2500 | 1.000000000 | 0.000011690 | 0.000024397 | 0.000167740 | 0.000252967 | 2500.000000000 | 0.027777778 | 0.006773874 | 0.999099171 | 0.702290947 |
| soft_t0.001_p1.5 | soft | 0.001000000 | 0 | 1.500000000 | 0.000010683 | 0.000015867 | 0.000167740 | 0.000252967 | 49134.471004954 | 0.545938567 | 0.001508898 | 0.999950319 | 0.701696918 |
| elite50 | elite | 0.000000000 | 50 | 1.000000000 | 0.000029022 | 0.000056186 | 0.000167740 | 0.000252967 | 50.000000000 | 0.000555556 | 0.047504900 | 0.959956683 | 0.710582821 |

## Null Stress

Known public deltas are permuted while the same sampled hard-world predictions are kept fixed.

| metric | real | null_mean | null_p10 | null_p50 | null_p90 | real_percentile_vs_null | one_sided_p_lower |
| --- | --- | --- | --- | --- | --- | --- | --- |
| best_world_mae | 0.000167740 | 0.000965433 | 0.000777596 | 0.000965302 | 0.001143212 | 0.000000000 | 0.003322259 |
| top100_world_mae | 0.000252967 | 0.001111925 | 0.000913165 | 0.001119873 | 0.001293277 | 0.000000000 | 0.003322259 |
| median_world_mae | 0.001398174 | 0.002089863 | 0.001886180 | 0.002086283 | 0.002280816 | 0.000000000 | 0.003322259 |
| p01_world_mae | 0.000371385 | 0.001301588 | 0.001086047 | 0.001298033 | 0.001496090 | 0.000000000 | 0.003322259 |
| p05_world_mae | 0.000505695 | 0.001463741 | 0.001230014 | 0.001466632 | 0.001676491 | 0.000000000 | 0.003322259 |

## Target Summary

| target | mean_q_hard | mean_q_prior | mean_shock | mean_gain | mean_weight | mean_confidence |
| --- | --- | --- | --- | --- | --- | --- |
| Q3 | 0.606503043 | 0.606364463 | 0.002478071 | 0.000000461 | 0.000565306 | 0.653837898 |
| S2 | 0.640376790 | 0.639981860 | 0.002488914 | 0.000000407 | 0.000580134 | 0.726116105 |
| S1 | 0.658907064 | 0.658566120 | 0.001975456 | 0.000000368 | 0.000581314 | 0.772540369 |
| S4 | 0.566914333 | 0.567064905 | 0.002608899 | 0.000000354 | 0.000575261 | 0.690559519 |
| S3 | 0.674030699 | 0.673788260 | 0.002119430 | 0.000000321 | 0.000563439 | 0.740489018 |
| Q1 | 0.493603298 | 0.493527969 | 0.002382402 | 0.000000308 | 0.000569972 | 0.702042065 |
| Q2 | 0.549280563 | 0.549236349 | 0.002710590 | 0.000000193 | 0.000564574 | 0.626990014 |

## Candidate Selection

| candidate_id | h018_decision | mode | target_kind | target_subset | changed_cells | hard_delta_vs_h012 | uniform_hard_delta_vs_h012 | max_abs_prob_delta_vs_h012 | file |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| combined_all_k1750_a1 | hard_world_sensor | combined | posterior | all | 1750 | -0.000603041 | -0.000579620 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1750_a1_0c12f8da.csv |
| gain_all_k1750_a1 | hard_world_sensor | gain | posterior | all | 1750 | -0.000603041 | -0.000579620 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1750_a1_0c12f8da.csv |
| shock_all_k1750_a1 | hard_world_sensor | shock | posterior | all | 1750 | -0.000603041 | -0.000579620 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1750_a1_0c12f8da.csv |
| confidence_all_k1750_a1 | hard_world_sensor | confidence | posterior | all | 1750 | -0.000603041 | -0.000579620 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_confidence_all_k1750_a1_0c12f8da.csv |
| h017_gain_all_k1750_a1 | hard_world_sensor | h017_gain | posterior | all | 1750 | -0.000603041 | -0.000579620 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1750_a1_0c12f8da.csv |
| gain_all_k1600_a1 | hard_world_sensor | gain | posterior | all | 1600 | -0.000602480 | -0.000579052 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1600_a1_c90701c0.csv |
| h017_gain_all_k1600_a1 | hard_world_sensor | h017_gain | posterior | all | 1600 | -0.000601097 | -0.000577652 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1600_a1_ca49797f.csv |
| combined_all_k1600_a1 | hard_world_sensor | combined | posterior | all | 1600 | -0.000600520 | -0.000577034 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1600_a1_fdbd2d6b.csv |
| gain_all_k1300_a1 | hard_world_sensor | gain | posterior | all | 1300 | -0.000594224 | -0.000570815 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1300_a1_07ad43d1.csv |
| h017_gain_all_k1300_a1 | hard_world_sensor | h017_gain | posterior | all | 1300 | -0.000593791 | -0.000570387 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1300_a1_8192cf16.csv |
| combined_all_k1300_a1 | hard_world_sensor | combined | posterior | all | 1300 | -0.000587255 | -0.000563473 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1300_a1_cdc27378.csv |
| gain_all_k1000_a1 | hard_world_sensor | gain | posterior | all | 1000 | -0.000570007 | -0.000546197 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1000_a1_3e95a50a.csv |
| h017_gain_all_k1000_a1 | hard_world_sensor | h017_gain | posterior | all | 1000 | -0.000569587 | -0.000545766 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1000_a1_456dc7dc.csv |
| confidence_all_k1600_a1 | hard_world_sensor | confidence | posterior | all | 1600 | -0.000568506 | -0.000544897 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_confidence_all_k1600_a1_812ff29a.csv |
| combined_all_k1750_a1.25 | hard_world_sensor | combined | posterior | all | 1750 | -0.000567307 | -0.000545062 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1750_a1.25_78dbbe09.csv |
| gain_all_k1750_a1.25 | hard_world_sensor | gain | posterior | all | 1750 | -0.000567307 | -0.000545062 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1750_a1.25_78dbbe09.csv |
| shock_all_k1750_a1.25 | hard_world_sensor | shock | posterior | all | 1750 | -0.000567307 | -0.000545062 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1750_a1.25_78dbbe09.csv |
| confidence_all_k1750_a1.25 | hard_world_sensor | confidence | posterior | all | 1750 | -0.000567307 | -0.000545062 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_confidence_all_k1750_a1.25_78dbbe09.csv |
| h017_gain_all_k1750_a1.25 | hard_world_sensor | h017_gain | posterior | all | 1750 | -0.000567307 | -0.000545062 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1750_a1.25_78dbbe09.csv |
| gain_all_k1600_a1.25 | hard_world_sensor | gain | posterior | all | 1600 | -0.000566780 | -0.000544529 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1600_a1.25_01eda82e.csv |
| combined_all_k1750_a0.75 | hard_world_sensor | combined | posterior | all | 1750 | -0.000566626 | -0.000544473 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1750_a0.75_25ad9990.csv |
| gain_all_k1750_a0.75 | hard_world_sensor | gain | posterior | all | 1750 | -0.000566626 | -0.000544473 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1750_a0.75_25ad9990.csv |
| shock_all_k1750_a0.75 | hard_world_sensor | shock | posterior | all | 1750 | -0.000566626 | -0.000544473 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1750_a0.75_25ad9990.csv |
| confidence_all_k1750_a0.75 | hard_world_sensor | confidence | posterior | all | 1750 | -0.000566626 | -0.000544473 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_confidence_all_k1750_a0.75_25ad9990.csv |
| h017_gain_all_k1750_a0.75 | hard_world_sensor | h017_gain | posterior | all | 1750 | -0.000566626 | -0.000544473 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1750_a0.75_25ad9990.csv |
| gain_all_k1600_a0.75 | hard_world_sensor | gain | posterior | all | 1600 | -0.000566099 | -0.000543939 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1600_a0.75_0f0f9bb6.csv |
| h017_gain_all_k1600_a1.25 | hard_world_sensor | h017_gain | posterior | all | 1600 | -0.000565485 | -0.000543217 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1600_a1.25_5cd67855.csv |
| combined_all_k1600_a1.25 | hard_world_sensor | combined | posterior | all | 1600 | -0.000564944 | -0.000542637 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1600_a1.25_c6347502.csv |
| h017_gain_all_k1600_a0.75 | hard_world_sensor | h017_gain | posterior | all | 1600 | -0.000564804 | -0.000542627 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1600_a0.75_3528772a.csv |
| combined_all_k1600_a0.75 | hard_world_sensor | combined | posterior | all | 1600 | -0.000564263 | -0.000542048 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1600_a0.75_12a13986.csv |
| combined_all_k1000_a1 | hard_world_sensor | combined | posterior | all | 1000 | -0.000559255 | -0.000534883 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1000_a1_3be78760.csv |
| gain_all_k1300_a1.25 | hard_world_sensor | gain | posterior | all | 1300 | -0.000558997 | -0.000536772 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1300_a1.25_ad2b686a.csv |
| h017_gain_all_k1300_a1.25 | hard_world_sensor | h017_gain | posterior | all | 1300 | -0.000558592 | -0.000536371 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1300_a1.25_bc0d0069.csv |
| gain_all_k1300_a0.75 | hard_world_sensor | gain | posterior | all | 1300 | -0.000558329 | -0.000536194 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1300_a0.75_2292531e.csv |
| shock_all_k1600_a1 | hard_world_sensor | shock | posterior | all | 1600 | -0.000558329 | -0.000537476 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1600_a1_78054082.csv |
| h017_gain_all_k1300_a0.75 | hard_world_sensor | h017_gain | posterior | all | 1300 | -0.000557924 | -0.000535792 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1300_a0.75_7a818b8e.csv |
| combined_all_k1300_a1.25 | hard_world_sensor | combined | posterior | all | 1300 | -0.000552507 | -0.000529924 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1300_a1.25_03e1fe5a.csv |
| combined_all_k1300_a0.75 | hard_world_sensor | combined | posterior | all | 1300 | -0.000551826 | -0.000529334 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1300_a0.75_65b8d553.csv |
| gain_all_k1000_a1.25 | hard_world_sensor | gain | posterior | all | 1000 | -0.000536291 | -0.000513691 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1000_a1.25_77fb5dd8.csv |
| h017_gain_all_k1000_a1.25 | hard_world_sensor | h017_gain | posterior | all | 1000 | -0.000535899 | -0.000513288 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1000_a1.25_b1ea23af.csv |
| gain_all_k1000_a0.75 | hard_world_sensor | gain | posterior | all | 1000 | -0.000535625 | -0.000513113 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k1000_a0.75_52e91a57.csv |
| h017_gain_all_k1000_a0.75 | hard_world_sensor | h017_gain | posterior | all | 1000 | -0.000535232 | -0.000512710 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k1000_a0.75_21d2cdcb.csv |
| confidence_all_k1600_a1.25 | hard_world_sensor | confidence | posterior | all | 1600 | -0.000534931 | -0.000512509 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_confidence_all_k1600_a1.25_2a09a695.csv |
| confidence_all_k1600_a0.75 | hard_world_sensor | confidence | posterior | all | 1600 | -0.000534250 | -0.000511919 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_confidence_all_k1600_a0.75_5af10515.csv |
| combined_all_k1000_a1.25 | hard_world_sensor | combined | posterior | all | 1000 | -0.000526258 | -0.000503120 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1000_a1.25_7ad3e2c8.csv |
| combined_all_k1000_a0.75 | hard_world_sensor | combined | posterior | all | 1000 | -0.000525576 | -0.000502531 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_combined_all_k1000_a0.75_fa640adc.csv |
| shock_all_k1600_a1.25 | hard_world_sensor | shock | posterior | all | 1600 | -0.000525078 | -0.000505281 | 0.136697900 | hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1600_a1.25_1f428410.csv |
| shock_all_k1600_a0.75 | hard_world_sensor | shock | posterior | all | 1600 | -0.000524502 | -0.000504784 | 0.087392489 | hitl/h018_hard_label_world_jepa/submission_h018_shock_all_k1600_a0.75_f4903dac.csv |
| gain_all_k700_a1 | hard_world_sensor | gain | posterior | all | 700 | -0.000521992 | -0.000497406 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_gain_all_k700_a1_49eefcd0.csv |
| h017_gain_all_k700_a1 | hard_world_sensor | h017_gain | posterior | all | 700 | -0.000521545 | -0.000496970 | 0.112988157 | hitl/h018_hard_label_world_jepa/submission_h018_h017_gain_all_k700_a1_7e64dc6e.csv |

## Decision

- Primary upload-safe candidate: `submission_h018_hard_label_world_combined_all_k1750_a1_uploadsafe.csv`.
- Interpretation: this file bets that the binary public-world posterior exposes a sharper target than continuous posterior-completion.

## Files

- `hitl/h018_hard_label_world_jepa/h018_world_posterior_configs.csv`
- `hitl/h018_hard_label_world_jepa/h018_world_null_stress.csv`
- `hitl/h018_hard_label_world_jepa/h018_cell_hard_posterior.csv`
- `hitl/h018_hard_label_world_jepa/h018_candidates.csv`
