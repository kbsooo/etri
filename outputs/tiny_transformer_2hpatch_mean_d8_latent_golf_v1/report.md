# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.623550`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.004103`
- Macro F1 @ 0.5: `0.705585`
- Drift vs v83 reference: `0.067173`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.002719 |
| Q2 | 0.015862 |
| Q3 | 0.005987 |
| S1 | 0.000405 |
| S2 | 0.000383 |
| S3 | 0.000000 |
| S4 | 0.003368 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.044248 |
| id02 | 0.053937 |
| id03 | 0.060494 |
| id04 | 0.071304 |
| id05 | 0.072795 |
| id06 | 0.069232 |
| id07 | 0.084256 |
| id08 | 0.083887 |
| id09 | 0.066923 |
| id10 | 0.070827 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626507 | 0.707034 | 29 | 0.067208 | 0.672564 | 0.698463 | 0.675387 | 0.576764 | 0.579730 | 0.536908 | 0.645736 | only_cross_modal::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.626585 | 0.706240 | 35 | 0.066572 | 0.672372 | 0.696200 | 0.675308 | 0.576956 | 0.580803 | 0.538696 | 0.645763 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626589 | 0.707326 | 29 | 0.066206 | 0.672560 | 0.697494 | 0.675153 | 0.576056 | 0.581043 | 0.538118 | 0.645702 | only_cross_modal::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.626624 | 0.704450 | 35 | 0.067351 | 0.672455 | 0.698379 | 0.675539 | 0.577566 | 0.579838 | 0.536614 | 0.645975 | only_cross_modal::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626681 | 0.704373 | 35 | 0.066137 | 0.671955 | 0.697706 | 0.675727 | 0.576137 | 0.581165 | 0.538265 | 0.645814 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626691 | 0.706700 | 29 | 0.066383 | 0.671978 | 0.700305 | 0.674928 | 0.576771 | 0.582150 | 0.535425 | 0.645277 | only_cross_modal::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626728 | 0.703930 | 31 | 0.065108 | 0.671994 | 0.700068 | 0.676060 | 0.576315 | 0.580680 | 0.535932 | 0.646049 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626736 | 0.703124 | 35 | 0.066853 | 0.672351 | 0.697554 | 0.675528 | 0.576749 | 0.581050 | 0.537316 | 0.646605 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.2 | 0.626749 | 0.712239 | 29 | 0.074397 | 0.672900 | 0.693287 | 0.673587 | 0.579366 | 0.581349 | 0.541154 | 0.645600 | only_cross_modal::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute__lowrank_r2_k2_wd0.1_b0.1 | 0.626767 | 0.708069 | 25 | 0.066688 | 0.671699 | 0.699144 | 0.675018 | 0.576471 | 0.580937 | 0.537562 | 0.646537 | only_cross_modal::absolute | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k2_b0.1 | 0.626794 | 0.703449 | 21 | 0.065946 | 0.672287 | 0.698169 | 0.675838 | 0.576126 | 0.581060 | 0.538713 | 0.645365 | no_sleep::deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__linear_k4_b0.1 | 0.626809 | 0.706011 | 35 | 0.066466 | 0.671778 | 0.699064 | 0.675262 | 0.576576 | 0.580934 | 0.538099 | 0.645952 | no_sleep::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626818 | 0.705387 | 23 | 0.065902 | 0.672471 | 0.698790 | 0.675544 | 0.576350 | 0.580630 | 0.539068 | 0.644876 | no_sleep::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.626819 | 0.706714 | 17 | 0.066362 | 0.671408 | 0.698490 | 0.675166 | 0.576521 | 0.580845 | 0.538183 | 0.647124 | only_event::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.626821 | 0.706791 | 17 | 0.066529 | 0.671640 | 0.699543 | 0.675405 | 0.576689 | 0.580452 | 0.537633 | 0.646380 | only_cross_modal::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626829 | 0.706570 | 31 | 0.069237 | 0.671612 | 0.696205 | 0.674901 | 0.577853 | 0.582821 | 0.538455 | 0.645955 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__linear_k1_b0.1 | 0.626838 | 0.705746 | 14 | 0.065993 | 0.672196 | 0.698739 | 0.675891 | 0.576317 | 0.580788 | 0.538860 | 0.645073 | no_sleep::deviation | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k1_b0.1 | 0.626852 | 0.707404 | 14 | 0.066393 | 0.671351 | 0.698345 | 0.675789 | 0.576524 | 0.581042 | 0.537436 | 0.647479 | only_event::absolute_plus_deviation | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute__linear_k1_b0.1 | 0.626852 | 0.707404 | 14 | 0.066393 | 0.671351 | 0.698345 | 0.675789 | 0.576524 | 0.581042 | 0.537436 | 0.647479 | only_event::absolute | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k2_b0.1 | 0.626853 | 0.705441 | 21 | 0.066187 | 0.671737 | 0.698760 | 0.675318 | 0.576726 | 0.580380 | 0.537297 | 0.647750 | only_event::absolute_plus_deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute__lowrank_r1_k1_wd0.1_b0.1 | 0.626853 | 0.706705 | 15 | 0.066129 | 0.671609 | 0.698235 | 0.675036 | 0.576569 | 0.580823 | 0.538146 | 0.647554 | only_event::absolute | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626853 | 0.706705 | 15 | 0.066129 | 0.671609 | 0.698235 | 0.675036 | 0.576569 | 0.580823 | 0.538146 | 0.647554 | only_event::absolute_plus_deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__deviation__linear_k4_b0.1 | 0.626854 | 0.704434 | 35 | 0.065974 | 0.672146 | 0.698428 | 0.675348 | 0.576132 | 0.580989 | 0.538097 | 0.646840 | only_event::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.626889 | 0.705193 | 18 | 0.066128 | 0.672109 | 0.699547 | 0.675526 | 0.576329 | 0.580837 | 0.538210 | 0.645666 | no_sleep::absolute | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626904 | 0.707588 | 29 | 0.065563 | 0.671858 | 0.699617 | 0.676013 | 0.576386 | 0.581040 | 0.537001 | 0.646416 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623550`
- Target-wise drift vs v83: `0.067173`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 0.670460 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 0.689148 |
| Q3 | only_rhythm__absolute__linear_k2_b0.2 | 0.671784 |
| S1 | only_rhythm__absolute__linear_k2_b0.1 | 0.575297 |
| S2 | only_rhythm__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.579473 |
| S3 | subject_prior | 0.534788 |
| S4 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.643904 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.