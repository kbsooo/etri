# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.621446`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.006208`
- Macro F1 @ 0.5: `0.711068`
- Drift vs v83 reference: `0.073280`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.004454 |
| Q2 | 0.018569 |
| Q3 | 0.013833 |
| S1 | 0.002644 |
| S2 | 0.001544 |
| S3 | 0.001498 |
| S4 | 0.000913 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.049162 |
| id02 | 0.057491 |
| id03 | 0.061455 |
| id04 | 0.069718 |
| id05 | 0.093041 |
| id06 | 0.098913 |
| id07 | 0.071857 |
| id08 | 0.079395 |
| id09 | 0.075404 |
| id10 | 0.088734 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.624475 | 0.712969 | 29 | 0.076352 | 0.671309 | 0.694722 | 0.670161 | 0.573058 | 0.578439 | 0.533860 | 0.649777 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__linear_k4_b0.2 | 0.624517 | 0.711639 | 35 | 0.075763 | 0.672140 | 0.693708 | 0.669661 | 0.573520 | 0.578951 | 0.533983 | 0.649657 | only_event::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.624903 | 0.713795 | 29 | 0.077759 | 0.669217 | 0.693161 | 0.664391 | 0.575596 | 0.580348 | 0.543851 | 0.647757 | only_rhythm::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__deviation__linear_k4_b0.2 | 0.625415 | 0.719220 | 35 | 0.075137 | 0.671802 | 0.693386 | 0.663959 | 0.573829 | 0.581593 | 0.544137 | 0.649197 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625433 | 0.704305 | 29 | 0.067992 | 0.671875 | 0.699184 | 0.673557 | 0.573717 | 0.578312 | 0.533344 | 0.648044 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.625471 | 0.706030 | 35 | 0.067629 | 0.672284 | 0.698738 | 0.673289 | 0.574011 | 0.578578 | 0.533449 | 0.647951 | only_event::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625484 | 0.708705 | 29 | 0.068969 | 0.670595 | 0.698319 | 0.670360 | 0.574790 | 0.578946 | 0.538366 | 0.647010 | only_rhythm::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.625496 | 0.716497 | 35 | 0.074925 | 0.669502 | 0.692345 | 0.671798 | 0.575351 | 0.580172 | 0.540999 | 0.648302 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.625650 | 0.712992 | 35 | 0.067438 | 0.671841 | 0.698397 | 0.670054 | 0.573616 | 0.579544 | 0.538408 | 0.647689 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| full__deviation__linear_k4_b0.2 | 0.625719 | 0.710821 | 35 | 0.076390 | 0.671925 | 0.687773 | 0.672838 | 0.576746 | 0.581879 | 0.542154 | 0.646716 | full::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.625736 | 0.711980 | 29 | 0.071683 | 0.672508 | 0.688800 | 0.665119 | 0.577815 | 0.583295 | 0.544063 | 0.648550 | no_sleep::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| full__deviation__linear_k4_b0.1 | 0.625817 | 0.707947 | 35 | 0.068122 | 0.671929 | 0.695374 | 0.674758 | 0.575330 | 0.579780 | 0.537188 | 0.646359 | full::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625834 | 0.711139 | 31 | 0.072774 | 0.668725 | 0.695762 | 0.673168 | 0.575329 | 0.580796 | 0.537701 | 0.649355 | only_cross_modal::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625835 | 0.711414 | 31 | 0.075446 | 0.672416 | 0.693369 | 0.665979 | 0.575855 | 0.580223 | 0.544020 | 0.648981 | only_rhythm::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625894 | 0.704198 | 29 | 0.065756 | 0.672226 | 0.695791 | 0.670814 | 0.575866 | 0.580713 | 0.538426 | 0.647422 | no_sleep::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h1_k2_wd0.1_b0.2 | 0.625934 | 0.710479 | 17 | 0.075486 | 0.672287 | 0.697207 | 0.675598 | 0.574587 | 0.578528 | 0.534172 | 0.649159 | only_event::absolute_plus_deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625938 | 0.709358 | 31 | 0.075036 | 0.670733 | 0.699331 | 0.673482 | 0.573895 | 0.578794 | 0.534533 | 0.650796 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.625975 | 0.709733 | 35 | 0.066961 | 0.670883 | 0.698072 | 0.674289 | 0.574967 | 0.579266 | 0.537217 | 0.647132 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.625988 | 0.711866 | 31 | 0.068010 | 0.672199 | 0.698600 | 0.671259 | 0.574956 | 0.579008 | 0.538313 | 0.647579 | only_rhythm::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.626020 | 0.711123 | 23 | 0.074949 | 0.671902 | 0.697582 | 0.674183 | 0.573450 | 0.580444 | 0.535657 | 0.648921 | only_event::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__lowrank_r1_k2_wd0.1_b0.2 | 0.626026 | 0.709288 | 16 | 0.075325 | 0.672216 | 0.697626 | 0.673028 | 0.574767 | 0.581496 | 0.533994 | 0.649054 | only_event::absolute_plus_deviation | lowrank | 2.000000 | 1.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__lowrank_r1_k1_wd0.1_b0.2 | 0.626060 | 0.712007 | 15 | 0.074103 | 0.671294 | 0.697464 | 0.672916 | 0.573428 | 0.580191 | 0.538053 | 0.649076 | only_event::absolute_plus_deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.200000 |
| only_event__absolute_plus_deviation__linear_k2_b0.2 | 0.626070 | 0.709760 | 21 | 0.075848 | 0.672047 | 0.699170 | 0.673599 | 0.573910 | 0.579573 | 0.534337 | 0.649857 | only_event::absolute_plus_deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626073 | 0.703014 | 35 | 0.065843 | 0.672244 | 0.694687 | 0.671336 | 0.576649 | 0.581280 | 0.538712 | 0.647604 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626075 | 0.712550 | 31 | 0.070705 | 0.670990 | 0.690610 | 0.668446 | 0.578053 | 0.584061 | 0.541200 | 0.649161 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.621446`
- Target-wise drift vs v83: `0.073280`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668725 |
| Q2 | no_sleep__deviation__linear_k4_b0.2 | 0.686441 |
| Q3 | only_event__deviation__linear_k2_b0.2 | 0.663937 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.573058 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.578312 |
| S3 | only_event__absolute_plus_deviation__lowrank_r1_k2_wd0.1_b0.1 | 0.533290 |
| S4 | full__deviation__linear_k4_b0.1 | 0.646359 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.