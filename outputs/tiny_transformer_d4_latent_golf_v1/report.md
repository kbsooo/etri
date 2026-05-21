# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.623174`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.004480`
- Macro F1 @ 0.5: `0.711823`
- Drift vs v83 reference: `0.067455`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.004698 |
| Q2 | 0.011945 |
| Q3 | 0.009113 |
| S1 | 0.000824 |
| S2 | 0.002455 |
| S3 | 0.000000 |
| S4 | 0.002321 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.042158 |
| id02 | 0.052728 |
| id03 | 0.060978 |
| id04 | 0.070669 |
| id05 | 0.080873 |
| id06 | 0.076697 |
| id07 | 0.080647 |
| id08 | 0.075418 |
| id09 | 0.067509 |
| id10 | 0.074344 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625489 | 0.707817 | 31 | 0.070172 | 0.670268 | 0.695175 | 0.669096 | 0.575354 | 0.580180 | 0.538505 | 0.649848 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.625842 | 0.708234 | 31 | 0.065464 | 0.671228 | 0.699470 | 0.673117 | 0.574878 | 0.578837 | 0.535338 | 0.648023 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626038 | 0.710942 | 31 | 0.070425 | 0.668481 | 0.697866 | 0.668657 | 0.578027 | 0.581550 | 0.539828 | 0.647856 | only_event::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626133 | 0.706286 | 31 | 0.065601 | 0.670310 | 0.700926 | 0.672888 | 0.576207 | 0.579499 | 0.536032 | 0.647067 | only_event::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.626161 | 0.713421 | 35 | 0.070267 | 0.672200 | 0.695749 | 0.674488 | 0.576761 | 0.580797 | 0.538063 | 0.645067 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_event__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626220 | 0.708884 | 29 | 0.067125 | 0.670833 | 0.699309 | 0.675092 | 0.575485 | 0.579690 | 0.536289 | 0.646839 | only_event::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.626334 | 0.710667 | 29 | 0.074299 | 0.669780 | 0.694761 | 0.673057 | 0.577166 | 0.581582 | 0.540480 | 0.647513 | only_event::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626361 | 0.708010 | 35 | 0.065452 | 0.672252 | 0.699798 | 0.675845 | 0.575645 | 0.579565 | 0.535844 | 0.645574 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__deviation__mlp_h2_k2_wd0.1_b0.2 | 0.626383 | 0.712732 | 27 | 0.070712 | 0.669909 | 0.698194 | 0.671989 | 0.576554 | 0.577401 | 0.541447 | 0.649187 | only_event::deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_event__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.626383 | 0.709300 | 27 | 0.065695 | 0.671029 | 0.701148 | 0.674588 | 0.575516 | 0.577510 | 0.537146 | 0.647745 | only_event::deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.626572 | 0.705315 | 35 | 0.065754 | 0.672021 | 0.700558 | 0.673866 | 0.576577 | 0.580493 | 0.535557 | 0.646931 | only_event::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626608 | 0.705195 | 29 | 0.065577 | 0.671408 | 0.701555 | 0.675107 | 0.576189 | 0.579880 | 0.536184 | 0.645935 | only_cross_modal::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626626 | 0.709426 | 31 | 0.069927 | 0.671661 | 0.696376 | 0.673119 | 0.577267 | 0.583157 | 0.539076 | 0.645726 | only_cross_modal::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626633 | 0.704409 | 31 | 0.065373 | 0.671973 | 0.700139 | 0.675171 | 0.576043 | 0.580923 | 0.536228 | 0.645954 | only_cross_modal::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.626662 | 0.707816 | 35 | 0.065655 | 0.671805 | 0.698409 | 0.675637 | 0.576219 | 0.580369 | 0.538724 | 0.645471 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626704 | 0.709109 | 17 | 0.065737 | 0.670883 | 0.699357 | 0.674992 | 0.576883 | 0.580117 | 0.537338 | 0.647357 | only_event::deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626705 | 0.706576 | 29 | 0.065611 | 0.671608 | 0.699168 | 0.675402 | 0.575420 | 0.580555 | 0.539137 | 0.645645 | only_cross_modal::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h2_k2_wd0.1_b0.1 | 0.626705 | 0.709105 | 27 | 0.065851 | 0.671738 | 0.699444 | 0.675101 | 0.576748 | 0.579663 | 0.536836 | 0.647408 | only_event::absolute_plus_deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626717 | 0.707727 | 23 | 0.065895 | 0.670748 | 0.699071 | 0.675541 | 0.577112 | 0.579704 | 0.537606 | 0.647240 | only_event::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626719 | 0.707472 | 29 | 0.065560 | 0.671393 | 0.701183 | 0.674290 | 0.576656 | 0.579849 | 0.536815 | 0.646849 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.626734 | 0.709241 | 29 | 0.070344 | 0.670503 | 0.699075 | 0.672978 | 0.578318 | 0.581296 | 0.539323 | 0.645646 | only_cross_modal::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__linear_k2_b0.1 | 0.626749 | 0.707246 | 21 | 0.065673 | 0.672144 | 0.699763 | 0.675121 | 0.575958 | 0.580253 | 0.537421 | 0.646586 | only_cross_modal::absolute_plus_deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.626770 | 0.707549 | 23 | 0.066031 | 0.671062 | 0.698904 | 0.675649 | 0.577027 | 0.579953 | 0.537706 | 0.647084 | only_event::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.626772 | 0.705952 | 35 | 0.066352 | 0.672128 | 0.698503 | 0.675734 | 0.576517 | 0.579615 | 0.538518 | 0.646387 | only_cross_modal::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626773 | 0.706522 | 23 | 0.065879 | 0.670883 | 0.700107 | 0.675550 | 0.576334 | 0.579529 | 0.537846 | 0.647162 | only_event::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623174`
- Target-wise drift vs v83: `0.067455`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668481 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 0.693065 |
| Q3 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668657 |
| S1 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.574878 |
| S2 | only_event__deviation__mlp_h2_k2_wd0.1_b0.2 | 0.577401 |
| S3 | subject_prior | 0.534788 |
| S4 | only_cross_modal__deviation__linear_k4_b0.2 | 0.644951 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.