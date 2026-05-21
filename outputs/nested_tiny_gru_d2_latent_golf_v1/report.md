# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626739` (`no_sleep__absolute_plus_deviation__linear_k4_b0.1`)
- Full-OOF targetwise selection: `0.624638`
- Nested targetwise selection: `0.627061`
- Estimated selection optimism: `0.002423`
- Nested gain vs subject prior: `0.000593`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.674973 |
| Q2 | 0.700515 |
| Q3 | 0.673011 |
| S1 | 0.577678 |
| S2 | 0.581335 |
| S3 | 0.538951 |
| S4 | 0.642963 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | no_sleep__absolute__linear_k1_b0.2 | 1 |
| Q1 | no_sleep__absolute__linear_k2_b0.2 | 1 |
| Q1 | only_cross_modal__deviation__lowrank_r1_k2_wd0.1_b0.2 | 1 |
| Q1 | only_cross_modal__deviation__mlp_h1_k1_wd0.1_b0.2 | 1 |
| Q1 | only_rhythm__deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| Q2 | no_sleep__deviation__linear_k2_b0.2 | 3 |
| Q2 | only_rhythm__absolute__linear_k1_b0.2 | 1 |
| Q2 | only_rhythm__absolute_plus_deviation__linear_k4_b0.2 | 1 |
| Q3 | no_sleep__absolute_plus_deviation__lowrank_r2_k2_wd0.1_b0.2 | 3 |
| Q3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 2 |
| S1 | no_sleep__deviation__linear_k2_b0.1 | 2 |
| S1 | no_sleep__deviation__linear_k2_b0.2 | 1 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S1 | only_rhythm__absolute__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 3 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S2 | no_sleep__deviation__lowrank_r1_k1_wd0.1_b0.1 | 1 |
| S3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 2 |
| S3 | only_cross_modal__deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S3 | only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S3 | only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S4 | no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 5 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | no_sleep__absolute__linear_k1_b0.2 | 0.670697 |
| Q2 | no_sleep__deviation__linear_k2_b0.2 | 0.695579 |
| Q3 | no_sleep__absolute_plus_deviation__lowrank_r2_k2_wd0.1_b0.2 | 0.671722 |
| S1 | no_sleep__deviation__linear_k2_b0.1 | 0.574972 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.579023 |
| S3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.537510 |
| S4 | no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 0.642963 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.626739 | 0.672251 | 0.701252 | 0.675538 | 0.575378 | 0.580124 | 0.538149 | 0.644484 |
| no_sleep__deviation__linear_k2_b0.1 | 0.626808 | 0.672055 | 0.699745 | 0.675369 | 0.574972 | 0.579897 | 0.539076 | 0.646541 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626826 | 0.672130 | 0.700493 | 0.675301 | 0.575523 | 0.579797 | 0.539053 | 0.645489 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626873 | 0.672319 | 0.701097 | 0.674465 | 0.575652 | 0.579826 | 0.537510 | 0.647245 |
| no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626901 | 0.671793 | 0.701229 | 0.675204 | 0.576236 | 0.579303 | 0.538874 | 0.645666 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626901 | 0.672323 | 0.701606 | 0.674479 | 0.575975 | 0.579621 | 0.538978 | 0.645326 |
| no_sleep__deviation__lowrank_r2_k2_wd0.1_b0.1 | 0.626901 | 0.671724 | 0.700303 | 0.674542 | 0.575872 | 0.579870 | 0.539433 | 0.646566 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626905 | 0.672447 | 0.702567 | 0.675269 | 0.575086 | 0.579023 | 0.538894 | 0.645050 |
| no_sleep__deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626934 | 0.672053 | 0.700878 | 0.674740 | 0.576047 | 0.579779 | 0.538833 | 0.646208 |
| no_sleep__deviation__linear_k1_b0.1 | 0.626941 | 0.671890 | 0.700707 | 0.675384 | 0.576193 | 0.579892 | 0.538934 | 0.645589 |
| no_sleep__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626974 | 0.671770 | 0.700207 | 0.674914 | 0.576319 | 0.580378 | 0.539233 | 0.645995 |
| no_sleep__deviation__lowrank_r1_k2_wd0.1_b0.1 | 0.626983 | 0.671873 | 0.701148 | 0.675007 | 0.576113 | 0.579679 | 0.539065 | 0.645999 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 0.627006 | 0.672274 | 0.698414 | 0.673920 | 0.576420 | 0.581908 | 0.543144 | 0.642963 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627012 | 0.672440 | 0.701332 | 0.674819 | 0.576252 | 0.579904 | 0.538606 | 0.645733 |
| only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627070 | 0.671905 | 0.700585 | 0.675332 | 0.576075 | 0.580879 | 0.537659 | 0.647054 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.