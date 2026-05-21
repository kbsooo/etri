# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.623314`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.004340`
- Macro F1 @ 0.5: `0.707648`
- Drift vs v83 reference: `0.066387`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.004377 |
| Q2 | 0.013090 |
| Q3 | 0.006611 |
| S1 | 0.000688 |
| S2 | 0.001701 |
| S3 | 0.000000 |
| S4 | 0.003916 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.042189 |
| id02 | 0.051292 |
| id03 | 0.059647 |
| id04 | 0.071312 |
| id05 | 0.072850 |
| id06 | 0.072696 |
| id07 | 0.079135 |
| id08 | 0.081300 |
| id09 | 0.068373 |
| id10 | 0.072681 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626403 | 0.707611 | 31 | 0.065780 | 0.671569 | 0.697886 | 0.675027 | 0.575507 | 0.580510 | 0.537414 | 0.646910 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626429 | 0.709874 | 31 | 0.070838 | 0.671015 | 0.691920 | 0.672909 | 0.576679 | 0.582730 | 0.542051 | 0.647703 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.626517 | 0.704889 | 35 | 0.066270 | 0.671786 | 0.698901 | 0.675444 | 0.575248 | 0.580308 | 0.537895 | 0.646036 | no_sleep::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 0.626634 | 0.707662 | 35 | 0.071871 | 0.671351 | 0.694014 | 0.673693 | 0.576384 | 0.582432 | 0.542464 | 0.646100 | no_sleep::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626640 | 0.705020 | 29 | 0.066398 | 0.670526 | 0.701064 | 0.674472 | 0.576021 | 0.582182 | 0.535762 | 0.646453 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626658 | 0.705561 | 35 | 0.066252 | 0.672237 | 0.698629 | 0.675132 | 0.575983 | 0.579947 | 0.538697 | 0.645982 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626773 | 0.706609 | 31 | 0.065635 | 0.672135 | 0.699052 | 0.674880 | 0.575890 | 0.581475 | 0.537276 | 0.646702 | no_sleep::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626788 | 0.708334 | 18 | 0.065871 | 0.671507 | 0.700777 | 0.675791 | 0.575354 | 0.580912 | 0.536492 | 0.646683 | no_sleep::absolute_plus_deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.626829 | 0.709560 | 27 | 0.066176 | 0.672329 | 0.699472 | 0.675266 | 0.576150 | 0.580995 | 0.538680 | 0.644915 | only_cross_modal::deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626838 | 0.703097 | 29 | 0.066110 | 0.672365 | 0.700157 | 0.675109 | 0.575050 | 0.580908 | 0.538143 | 0.646132 | no_sleep::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__mlp_h1_k4_wd0.1_b0.1 | 0.626844 | 0.707467 | 19 | 0.066331 | 0.671307 | 0.698256 | 0.675220 | 0.576403 | 0.580843 | 0.537993 | 0.647886 | only_cross_modal::absolute | tiny_mlp | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626855 | 0.706260 | 29 | 0.066268 | 0.671430 | 0.698850 | 0.675586 | 0.577040 | 0.580490 | 0.538327 | 0.646261 | only_cross_modal::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__deviation__linear_k4_b0.1 | 0.626877 | 0.704702 | 35 | 0.066075 | 0.672476 | 0.698710 | 0.675037 | 0.576225 | 0.581441 | 0.537399 | 0.646852 | only_event::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626882 | 0.702766 | 31 | 0.065306 | 0.672285 | 0.701150 | 0.675086 | 0.575632 | 0.580934 | 0.536318 | 0.646768 | only_event::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__linear_k4_b0.1 | 0.626907 | 0.702950 | 35 | 0.066612 | 0.672632 | 0.698528 | 0.675628 | 0.575273 | 0.581033 | 0.538664 | 0.646593 | no_sleep::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__linear_k4_b0.1 | 0.626916 | 0.708424 | 35 | 0.065119 | 0.672443 | 0.700240 | 0.674865 | 0.576904 | 0.580502 | 0.537354 | 0.646101 | only_rhythm::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__mlp_h2_k4_wd0.1_b0.1 | 0.626931 | 0.709414 | 31 | 0.066190 | 0.671930 | 0.699683 | 0.674651 | 0.576048 | 0.580553 | 0.538094 | 0.647559 | only_cross_modal::absolute | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626934 | 0.707882 | 31 | 0.065001 | 0.671104 | 0.701102 | 0.674349 | 0.576032 | 0.580881 | 0.537809 | 0.647262 | only_rhythm::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k2_wd0.1_b0.1 | 0.626938 | 0.705231 | 25 | 0.066275 | 0.672178 | 0.699958 | 0.675377 | 0.576220 | 0.580237 | 0.538875 | 0.645721 | only_cross_modal::absolute | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.626939 | 0.704381 | 35 | 0.066434 | 0.671331 | 0.700118 | 0.674934 | 0.576579 | 0.582751 | 0.536253 | 0.646608 | only_event::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r1_k1_wd0.1_b0.1 | 0.626940 | 0.706842 | 15 | 0.065950 | 0.671773 | 0.699085 | 0.674933 | 0.576580 | 0.580329 | 0.538769 | 0.647113 | only_cross_modal::absolute | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.626942 | 0.707978 | 17 | 0.066366 | 0.671074 | 0.699200 | 0.675318 | 0.576311 | 0.580720 | 0.538947 | 0.647026 | no_sleep::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.626947 | 0.708979 | 23 | 0.066464 | 0.670538 | 0.699673 | 0.675377 | 0.576926 | 0.581182 | 0.538176 | 0.646759 | only_event::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k2_wd0.1_b0.1 | 0.626952 | 0.707479 | 25 | 0.066084 | 0.672145 | 0.699867 | 0.674834 | 0.577281 | 0.580135 | 0.539349 | 0.645056 | only_cross_modal::deviation | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626957 | 0.709856 | 17 | 0.065937 | 0.671879 | 0.699158 | 0.675171 | 0.576619 | 0.580706 | 0.538947 | 0.646221 | only_cross_modal::deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623314`
- Target-wise drift vs v83: `0.066387`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_rhythm__absolute_plus_deviation__mlp_h1_k2_wd0.1_b0.2 | 0.668803 |
| Q2 | no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.691920 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h2_k1_wd0.1_b0.2 | 0.671160 |
| S1 | only_event__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.575014 |
| S2 | only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.578155 |
| S3 | subject_prior | 0.534788 |
| S4 | only_cross_modal__absolute_plus_deviation__mlp_h2_k2_wd0.1_b0.2 | 0.643356 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.