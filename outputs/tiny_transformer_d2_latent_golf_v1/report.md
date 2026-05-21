# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.624200`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.003454`
- Macro F1 @ 0.5: `0.702917`
- Drift vs v83 reference: `0.066118`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.002994 |
| Q2 | 0.012516 |
| Q3 | 0.006170 |
| S1 | 0.000534 |
| S2 | 0.001163 |
| S3 | 0.000000 |
| S4 | 0.000800 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.043649 |
| id02 | 0.051869 |
| id03 | 0.059871 |
| id04 | 0.070441 |
| id05 | 0.076505 |
| id06 | 0.074572 |
| id07 | 0.071408 |
| id08 | 0.084372 |
| id09 | 0.068928 |
| id10 | 0.069509 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626826 | 0.705212 | 31 | 0.065559 | 0.672490 | 0.700821 | 0.674878 | 0.575342 | 0.579483 | 0.538092 | 0.646675 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626993 | 0.704343 | 29 | 0.065527 | 0.672736 | 0.700962 | 0.675943 | 0.575168 | 0.578993 | 0.538677 | 0.646472 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627036 | 0.707992 | 31 | 0.065850 | 0.671838 | 0.700351 | 0.674605 | 0.576578 | 0.581001 | 0.537903 | 0.646978 | no_sleep::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.627071 | 0.708117 | 35 | 0.065872 | 0.672049 | 0.699997 | 0.675001 | 0.575772 | 0.580809 | 0.538450 | 0.647419 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627089 | 0.710187 | 31 | 0.065813 | 0.671806 | 0.700855 | 0.674670 | 0.576641 | 0.580545 | 0.537859 | 0.647249 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627102 | 0.707591 | 31 | 0.065861 | 0.672229 | 0.699298 | 0.675181 | 0.576380 | 0.581156 | 0.538154 | 0.647317 | only_event::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__linear_k4_b0.1 | 0.627112 | 0.708693 | 35 | 0.065582 | 0.671808 | 0.700954 | 0.674507 | 0.575794 | 0.580614 | 0.538295 | 0.647809 | only_rhythm::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.627115 | 0.703055 | 35 | 0.065444 | 0.672572 | 0.700096 | 0.675584 | 0.575760 | 0.579912 | 0.538862 | 0.647018 | only_event::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute__mlp_h2_k4_wd0.1_b0.1 | 0.627139 | 0.708544 | 31 | 0.065916 | 0.671682 | 0.700725 | 0.674941 | 0.575639 | 0.580659 | 0.538626 | 0.647702 | only_rhythm::absolute | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.627142 | 0.706439 | 17 | 0.065826 | 0.671586 | 0.700447 | 0.674894 | 0.576207 | 0.580758 | 0.538815 | 0.647288 | only_rhythm::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.627144 | 0.706377 | 23 | 0.065770 | 0.671286 | 0.700663 | 0.674974 | 0.576870 | 0.580156 | 0.538783 | 0.647277 | no_sleep::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.627145 | 0.705738 | 18 | 0.065685 | 0.672857 | 0.700689 | 0.676413 | 0.575549 | 0.579424 | 0.538497 | 0.646589 | only_event::absolute_plus_deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.627147 | 0.706882 | 23 | 0.066005 | 0.671087 | 0.699903 | 0.675891 | 0.576563 | 0.580139 | 0.539091 | 0.647357 | only_event::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.627147 | 0.706882 | 23 | 0.066005 | 0.671087 | 0.699903 | 0.675891 | 0.576563 | 0.580139 | 0.539091 | 0.647357 | only_event::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.627152 | 0.704899 | 35 | 0.065807 | 0.672295 | 0.700026 | 0.674976 | 0.575658 | 0.581086 | 0.538677 | 0.647345 | no_sleep::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.627158 | 0.708344 | 29 | 0.065963 | 0.672182 | 0.699890 | 0.675145 | 0.576024 | 0.580754 | 0.538701 | 0.647409 | only_event::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute__mlp_h1_k1_wd0.1_b0.1 | 0.627159 | 0.709010 | 16 | 0.065893 | 0.671600 | 0.701054 | 0.674572 | 0.576244 | 0.580712 | 0.538587 | 0.647344 | only_rhythm::absolute | tiny_mlp | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__lowrank_r2_k2_wd0.1_b0.1 | 0.627159 | 0.709154 | 25 | 0.065987 | 0.671573 | 0.700890 | 0.674801 | 0.575856 | 0.580562 | 0.538857 | 0.647577 | only_rhythm::deviation | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__linear_k2_b0.1 | 0.627163 | 0.705258 | 21 | 0.065875 | 0.671953 | 0.700099 | 0.674878 | 0.576794 | 0.580616 | 0.538539 | 0.647259 | no_sleep::absolute_plus_deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627166 | 0.705641 | 31 | 0.065501 | 0.671948 | 0.700698 | 0.674662 | 0.575856 | 0.581075 | 0.538612 | 0.647308 | only_rhythm::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.627169 | 0.699313 | 35 | 0.065727 | 0.672177 | 0.698085 | 0.676008 | 0.576085 | 0.580296 | 0.539712 | 0.647823 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.627175 | 0.706059 | 23 | 0.065811 | 0.671370 | 0.700697 | 0.674867 | 0.577005 | 0.580203 | 0.538732 | 0.647348 | no_sleep::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.627176 | 0.707933 | 18 | 0.065396 | 0.671959 | 0.701101 | 0.675405 | 0.575752 | 0.580233 | 0.538294 | 0.647487 | only_rhythm::absolute_plus_deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.627182 | 0.706866 | 35 | 0.065797 | 0.672295 | 0.698869 | 0.676040 | 0.576487 | 0.580461 | 0.538562 | 0.647562 | only_cross_modal::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__linear_k4_b0.1 | 0.627183 | 0.710147 | 35 | 0.065908 | 0.672184 | 0.700550 | 0.674605 | 0.576066 | 0.580844 | 0.538370 | 0.647663 | only_rhythm::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624200`
- Target-wise drift vs v83: `0.066118`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute__lowrank_r2_k1_wd0.1_b0.2 | 0.670185 |
| Q2 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.692494 |
| Q3 | only_rhythm__absolute_plus_deviation__linear_k2_b0.2 | 0.671600 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.575168 |
| S2 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.578694 |
| S3 | subject_prior | 0.534788 |
| S4 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.646472 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.