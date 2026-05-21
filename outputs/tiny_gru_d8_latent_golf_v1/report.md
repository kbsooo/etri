# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.624135`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.003519`
- Macro F1 @ 0.5: `0.704170`
- Drift vs v83 reference: `0.067700`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.003492 |
| Q2 | 0.012754 |
| Q3 | 0.005561 |
| S1 | 0.000776 |
| S2 | 0.000368 |
| S3 | 0.000000 |
| S4 | 0.001678 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.042097 |
| id02 | 0.052633 |
| id03 | 0.065499 |
| id04 | 0.072315 |
| id05 | 0.081064 |
| id06 | 0.073475 |
| id07 | 0.080285 |
| id08 | 0.082642 |
| id09 | 0.067275 |
| id10 | 0.068878 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.626520 | 0.712001 | 29 | 0.070781 | 0.672458 | 0.695444 | 0.674367 | 0.575461 | 0.580735 | 0.540473 | 0.646700 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626591 | 0.705748 | 29 | 0.065597 | 0.672472 | 0.699663 | 0.675782 | 0.574942 | 0.579692 | 0.537093 | 0.646490 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626742 | 0.706425 | 31 | 0.065349 | 0.671426 | 0.699740 | 0.675869 | 0.575635 | 0.581195 | 0.536634 | 0.646695 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626836 | 0.705930 | 23 | 0.065599 | 0.671865 | 0.699595 | 0.675271 | 0.575742 | 0.580543 | 0.538662 | 0.646176 | only_cross_modal::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__deviation__linear_k4_b0.1 | 0.626864 | 0.705026 | 35 | 0.065874 | 0.672249 | 0.697944 | 0.676151 | 0.575179 | 0.581462 | 0.538319 | 0.646744 | only_event::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626892 | 0.706827 | 29 | 0.065853 | 0.671798 | 0.698510 | 0.675693 | 0.575561 | 0.580983 | 0.539887 | 0.645810 | only_cross_modal::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626911 | 0.710314 | 31 | 0.070041 | 0.670610 | 0.695585 | 0.674527 | 0.576810 | 0.583790 | 0.539851 | 0.647208 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.626915 | 0.707736 | 18 | 0.065784 | 0.672337 | 0.699335 | 0.675431 | 0.575819 | 0.580575 | 0.538253 | 0.646655 | only_cross_modal::absolute | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.626916 | 0.703482 | 35 | 0.065964 | 0.672328 | 0.699674 | 0.676699 | 0.575686 | 0.580858 | 0.536607 | 0.646562 | only_event::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 0.626926 | 0.703127 | 19 | 0.065444 | 0.671799 | 0.701191 | 0.676287 | 0.576210 | 0.579488 | 0.536583 | 0.646922 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626931 | 0.705066 | 31 | 0.065384 | 0.672122 | 0.700356 | 0.675677 | 0.575095 | 0.580970 | 0.537483 | 0.646815 | only_event::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k1_b0.1 | 0.626941 | 0.706730 | 14 | 0.065676 | 0.672171 | 0.698929 | 0.675820 | 0.575861 | 0.580541 | 0.538963 | 0.646304 | only_cross_modal::deviation | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626948 | 0.705945 | 29 | 0.065478 | 0.671333 | 0.700214 | 0.675395 | 0.576158 | 0.581529 | 0.537366 | 0.646640 | no_sleep::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626973 | 0.706198 | 17 | 0.065730 | 0.672157 | 0.698868 | 0.675389 | 0.576063 | 0.581075 | 0.539086 | 0.646176 | only_cross_modal::deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__absolute__lowrank_r1_k1_wd0.1_b0.1 | 0.626979 | 0.705333 | 15 | 0.066207 | 0.671446 | 0.698955 | 0.675013 | 0.576285 | 0.580859 | 0.538790 | 0.647503 | only_event::absolute | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626982 | 0.708199 | 18 | 0.065742 | 0.671863 | 0.699343 | 0.675728 | 0.575540 | 0.580792 | 0.538261 | 0.647349 | only_event::deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k2_b0.1 | 0.626990 | 0.707424 | 21 | 0.065646 | 0.672206 | 0.698847 | 0.675299 | 0.575735 | 0.581493 | 0.538793 | 0.646558 | only_cross_modal::deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626991 | 0.706822 | 18 | 0.065648 | 0.672586 | 0.701273 | 0.675128 | 0.575185 | 0.579644 | 0.537752 | 0.647367 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.627000 | 0.708067 | 17 | 0.065937 | 0.671632 | 0.699398 | 0.675336 | 0.576418 | 0.581079 | 0.538864 | 0.646275 | only_cross_modal::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.627007 | 0.707029 | 29 | 0.066565 | 0.671022 | 0.700021 | 0.675134 | 0.575809 | 0.581029 | 0.538608 | 0.647428 | no_sleep::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.627009 | 0.706463 | 27 | 0.065693 | 0.671903 | 0.699452 | 0.675728 | 0.575818 | 0.580694 | 0.538927 | 0.646541 | only_cross_modal::deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute__linear_k4_b0.1 | 0.627022 | 0.705916 | 35 | 0.066875 | 0.672513 | 0.698372 | 0.675496 | 0.576597 | 0.580780 | 0.538648 | 0.646750 | only_event::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.627039 | 0.703437 | 27 | 0.065588 | 0.672198 | 0.700252 | 0.675094 | 0.576938 | 0.579899 | 0.537940 | 0.646954 | no_sleep::deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.627040 | 0.706741 | 17 | 0.066336 | 0.671382 | 0.699296 | 0.675401 | 0.576632 | 0.580579 | 0.538840 | 0.647150 | only_event::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.627042 | 0.704819 | 35 | 0.065698 | 0.672698 | 0.697898 | 0.675971 | 0.576113 | 0.581497 | 0.538658 | 0.646461 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624135`
- Target-wise drift vs v83: `0.067700`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute__linear_k1_b0.2 | 0.669688 |
| Q2 | only_event__deviation__linear_k4_b0.2 | 0.692256 |
| Q3 | no_sleep__deviation__linear_k2_b0.2 | 0.672209 |
| S1 | only_rhythm__absolute__mlp_h1_k4_wd0.1_b0.1 | 0.574926 |
| S2 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 0.579488 |
| S3 | subject_prior | 0.534788 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.645594 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.