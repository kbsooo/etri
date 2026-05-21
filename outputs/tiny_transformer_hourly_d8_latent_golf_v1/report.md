# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.623951`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.003703`
- Macro F1 @ 0.5: `0.711682`
- Drift vs v83 reference: `0.066299`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.003580 |
| Q2 | 0.012989 |
| Q3 | 0.006238 |
| S1 | 0.001453 |
| S2 | 0.000568 |
| S3 | 0.000000 |
| S4 | 0.001093 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.042180 |
| id02 | 0.054455 |
| id03 | 0.060000 |
| id04 | 0.070259 |
| id05 | 0.078327 |
| id06 | 0.071633 |
| id07 | 0.074649 |
| id08 | 0.084078 |
| id09 | 0.069198 |
| id10 | 0.066678 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_rhythm__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626613 | 0.706405 | 29 | 0.065966 | 0.671320 | 0.699270 | 0.675311 | 0.576196 | 0.579703 | 0.537652 | 0.646840 | only_rhythm::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626616 | 0.708920 | 23 | 0.065913 | 0.670726 | 0.698720 | 0.675003 | 0.576700 | 0.580522 | 0.537380 | 0.647261 | no_sleep::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute__linear_k4_b0.1 | 0.626736 | 0.706962 | 35 | 0.066028 | 0.672834 | 0.699079 | 0.675330 | 0.575469 | 0.579483 | 0.538499 | 0.646458 | only_rhythm::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626790 | 0.705773 | 29 | 0.066468 | 0.671588 | 0.699504 | 0.675362 | 0.575964 | 0.580175 | 0.537135 | 0.647800 | no_sleep::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626793 | 0.709688 | 29 | 0.065456 | 0.672385 | 0.699239 | 0.675231 | 0.575958 | 0.580265 | 0.536575 | 0.647895 | no_sleep::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626831 | 0.706674 | 29 | 0.065224 | 0.671402 | 0.702006 | 0.675338 | 0.574249 | 0.579990 | 0.538066 | 0.646767 | only_rhythm::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626862 | 0.707880 | 31 | 0.065632 | 0.672901 | 0.699879 | 0.674375 | 0.576505 | 0.580354 | 0.536806 | 0.647218 | no_sleep::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| full__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626875 | 0.705189 | 29 | 0.065987 | 0.672425 | 0.699602 | 0.675506 | 0.576235 | 0.580446 | 0.537257 | 0.646651 | full::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626883 | 0.707828 | 31 | 0.065350 | 0.671305 | 0.701425 | 0.674625 | 0.575407 | 0.580501 | 0.537883 | 0.647033 | only_rhythm::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626934 | 0.707421 | 35 | 0.066487 | 0.672073 | 0.699200 | 0.675253 | 0.576308 | 0.581016 | 0.537300 | 0.647389 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k1_b0.1 | 0.626952 | 0.708016 | 14 | 0.066048 | 0.671747 | 0.698903 | 0.675350 | 0.576413 | 0.580658 | 0.537765 | 0.647829 | no_sleep::deviation | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.626956 | 0.708112 | 18 | 0.066169 | 0.671547 | 0.698719 | 0.675341 | 0.576754 | 0.581001 | 0.537370 | 0.647960 | only_cross_modal::absolute | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626958 | 0.708312 | 17 | 0.065744 | 0.671618 | 0.699613 | 0.675241 | 0.576243 | 0.580881 | 0.537763 | 0.647350 | no_sleep::deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| full__absolute__mlp_h2_k4_wd0.1_b0.1 | 0.626979 | 0.706912 | 31 | 0.065897 | 0.672144 | 0.700077 | 0.675620 | 0.576390 | 0.580448 | 0.537230 | 0.646947 | full::absolute | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.626995 | 0.708325 | 18 | 0.065870 | 0.672554 | 0.699363 | 0.674913 | 0.576616 | 0.580289 | 0.537977 | 0.647253 | only_rhythm::absolute | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__mlp_h2_k2_wd0.1_b0.1 | 0.627013 | 0.710124 | 27 | 0.065615 | 0.671884 | 0.699632 | 0.675604 | 0.576119 | 0.581149 | 0.537231 | 0.647474 | no_sleep::absolute_plus_deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.627024 | 0.708135 | 15 | 0.065867 | 0.671760 | 0.700049 | 0.674779 | 0.576480 | 0.580470 | 0.538000 | 0.647628 | no_sleep::deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute__lowrank_r2_k4_wd0.1_b0.2 | 0.627034 | 0.711750 | 29 | 0.071489 | 0.670488 | 0.694878 | 0.673449 | 0.578463 | 0.581521 | 0.542820 | 0.647616 | only_rhythm::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.627035 | 0.706738 | 27 | 0.065834 | 0.671880 | 0.699741 | 0.674839 | 0.576659 | 0.580849 | 0.537640 | 0.647635 | no_sleep::deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| full__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.627036 | 0.708307 | 18 | 0.065750 | 0.672396 | 0.698919 | 0.675270 | 0.576884 | 0.580763 | 0.537809 | 0.647209 | full::absolute | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| full__absolute_plus_deviation__mlp_h1_k2_wd0.1_b0.1 | 0.627040 | 0.709602 | 17 | 0.065608 | 0.672261 | 0.699778 | 0.675093 | 0.576129 | 0.580502 | 0.538337 | 0.647178 | full::absolute_plus_deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| full__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.627049 | 0.707803 | 23 | 0.065582 | 0.672053 | 0.700625 | 0.674942 | 0.576431 | 0.580107 | 0.538677 | 0.646508 | full::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| full__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.627049 | 0.707803 | 23 | 0.065582 | 0.672053 | 0.700625 | 0.674942 | 0.576431 | 0.580107 | 0.538677 | 0.646508 | full::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute__mlp_h2_k2_wd0.1_b0.1 | 0.627058 | 0.704885 | 27 | 0.065899 | 0.672207 | 0.700014 | 0.675573 | 0.576025 | 0.579639 | 0.538902 | 0.647048 | only_rhythm::absolute | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__mlp_h2_k2_wd0.1_b0.1 | 0.627065 | 0.706001 | 27 | 0.065832 | 0.672615 | 0.700366 | 0.675173 | 0.576177 | 0.579709 | 0.538553 | 0.646861 | only_rhythm::absolute_plus_deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623951`
- Target-wise drift vs v83: `0.066299`

| target | source | loss |
| --- | --- | --- |
| Q1 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.669600 |
| Q2 | no_sleep__absolute__lowrank_r2_k4_wd0.1_b0.2 | 0.692021 |
| Q3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.671532 |
| S1 | only_rhythm__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.574249 |
| S2 | only_rhythm__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.579289 |
| S3 | subject_prior | 0.534788 |
| S4 | only_rhythm__deviation__linear_k2_b0.1 | 0.646179 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.