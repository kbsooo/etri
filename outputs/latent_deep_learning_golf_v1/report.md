# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.621691`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.005963`
- Macro F1 @ 0.5: `0.710951`
- Drift vs v83 reference: `0.071488`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.004454 |
| Q2 | 0.018569 |
| Q3 | 0.013811 |
| S1 | 0.002086 |
| S2 | 0.001265 |
| S3 | 0.000643 |
| S4 | 0.000913 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.049652 |
| id02 | 0.052907 |
| id03 | 0.056657 |
| id04 | 0.073407 |
| id05 | 0.086178 |
| id06 | 0.089983 |
| id07 | 0.078308 |
| id08 | 0.076923 |
| id09 | 0.076129 |
| id10 | 0.083229 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__deviation__linear_k4_b0.2 | 0.625415 | 0.719220 | 35 | 0.075137 | 0.671802 | 0.693386 | 0.663959 | 0.573829 | 0.581593 | 0.544137 | 0.649197 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.625496 | 0.716497 | 35 | 0.074925 | 0.669502 | 0.692345 | 0.671798 | 0.575351 | 0.580172 | 0.540999 | 0.648302 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.625650 | 0.712992 | 35 | 0.067438 | 0.671841 | 0.698397 | 0.670054 | 0.573616 | 0.579544 | 0.538408 | 0.647689 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| full__deviation__linear_k4_b0.2 | 0.625719 | 0.710821 | 35 | 0.076390 | 0.671925 | 0.687773 | 0.672838 | 0.576746 | 0.581879 | 0.542154 | 0.646716 | full::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.625736 | 0.711980 | 29 | 0.071683 | 0.672508 | 0.688800 | 0.665119 | 0.577815 | 0.583295 | 0.544063 | 0.648550 | no_sleep::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| full__deviation__linear_k4_b0.1 | 0.625817 | 0.707947 | 35 | 0.068122 | 0.671929 | 0.695374 | 0.674758 | 0.575330 | 0.579780 | 0.537188 | 0.646359 | full::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625834 | 0.711139 | 31 | 0.072774 | 0.668725 | 0.695762 | 0.673168 | 0.575329 | 0.580796 | 0.537701 | 0.649355 | only_cross_modal::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625894 | 0.704198 | 29 | 0.065756 | 0.672226 | 0.695791 | 0.670814 | 0.575866 | 0.580713 | 0.538426 | 0.647422 | no_sleep::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.625975 | 0.709733 | 35 | 0.066961 | 0.670883 | 0.698072 | 0.674289 | 0.574967 | 0.579266 | 0.537217 | 0.647132 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626073 | 0.703014 | 35 | 0.065843 | 0.672244 | 0.694687 | 0.671336 | 0.576649 | 0.581280 | 0.538712 | 0.647604 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626075 | 0.712550 | 31 | 0.070705 | 0.670990 | 0.690610 | 0.668446 | 0.578053 | 0.584061 | 0.541200 | 0.649161 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626106 | 0.708715 | 31 | 0.065605 | 0.671544 | 0.697044 | 0.672629 | 0.576042 | 0.581111 | 0.536668 | 0.647701 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.2 | 0.626154 | 0.712635 | 35 | 0.071956 | 0.672605 | 0.686441 | 0.666267 | 0.579505 | 0.584580 | 0.544692 | 0.648986 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.626163 | 0.712473 | 29 | 0.073895 | 0.669856 | 0.696377 | 0.671420 | 0.575105 | 0.580453 | 0.539894 | 0.650035 | only_cross_modal::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626205 | 0.708070 | 31 | 0.066293 | 0.670538 | 0.699820 | 0.675126 | 0.574952 | 0.579570 | 0.535613 | 0.647814 | only_cross_modal::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| full__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626235 | 0.705944 | 31 | 0.077588 | 0.670332 | 0.700002 | 0.673903 | 0.577210 | 0.579494 | 0.535133 | 0.647569 | full::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626325 | 0.710110 | 23 | 0.065719 | 0.671168 | 0.699597 | 0.672265 | 0.574898 | 0.579786 | 0.538600 | 0.647961 | only_cross_modal::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626328 | 0.705687 | 29 | 0.066567 | 0.671076 | 0.700107 | 0.674155 | 0.574843 | 0.579368 | 0.536604 | 0.648145 | only_cross_modal::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626373 | 0.709120 | 29 | 0.066499 | 0.671258 | 0.699751 | 0.672584 | 0.574727 | 0.579952 | 0.538216 | 0.648122 | only_cross_modal::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626383 | 0.704928 | 18 | 0.065824 | 0.671970 | 0.696536 | 0.672096 | 0.577035 | 0.580943 | 0.538326 | 0.647776 | no_sleep::deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| full__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626403 | 0.704350 | 29 | 0.067776 | 0.671712 | 0.698187 | 0.674515 | 0.574969 | 0.579599 | 0.538946 | 0.646894 | full::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626411 | 0.707002 | 18 | 0.066894 | 0.671302 | 0.698722 | 0.673466 | 0.574852 | 0.580577 | 0.538257 | 0.647699 | only_cross_modal::deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| full__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626438 | 0.707230 | 31 | 0.068582 | 0.671410 | 0.702203 | 0.675548 | 0.575911 | 0.578925 | 0.534145 | 0.646922 | full::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.626454 | 0.717763 | 23 | 0.071110 | 0.670315 | 0.695446 | 0.668179 | 0.575573 | 0.581678 | 0.544226 | 0.649762 | only_cross_modal::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__deviation__lowrank_r1_k2_wd0.1_b0.1 | 0.626487 | 0.709764 | 16 | 0.065332 | 0.671586 | 0.698919 | 0.671479 | 0.576123 | 0.580813 | 0.538595 | 0.647896 | only_cross_modal::deviation | lowrank | 2.000000 | 1.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.621691`
- Target-wise drift vs v83: `0.071488`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668725 |
| Q2 | no_sleep__deviation__linear_k4_b0.2 | 0.686441 |
| Q3 | only_cross_modal__deviation__linear_k4_b0.2 | 0.663959 |
| S1 | only_cross_modal__deviation__linear_k4_b0.1 | 0.573616 |
| S2 | full__absolute_plus_deviation__linear_k2_b0.1 | 0.578591 |
| S3 | full__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.534145 |
| S4 | full__deviation__linear_k4_b0.1 | 0.646359 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.