# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.624249`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.003405`
- Macro F1 @ 0.5: `0.709528`
- Drift vs v83 reference: `0.068315`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.002482 |
| Q2 | 0.009431 |
| Q3 | 0.006048 |
| S1 | 0.000730 |
| S2 | 0.000834 |
| S3 | 0.000000 |
| S4 | 0.004309 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.042647 |
| id02 | 0.053293 |
| id03 | 0.063711 |
| id04 | 0.074925 |
| id05 | 0.075738 |
| id06 | 0.070454 |
| id07 | 0.080865 |
| id08 | 0.085200 |
| id09 | 0.070597 |
| id10 | 0.074037 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.626739 | 0.706326 | 35 | 0.065663 | 0.672251 | 0.701252 | 0.675538 | 0.575378 | 0.580124 | 0.538149 | 0.644484 | no_sleep::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k2_b0.1 | 0.626808 | 0.707261 | 21 | 0.065685 | 0.672055 | 0.699745 | 0.675369 | 0.574972 | 0.579897 | 0.539076 | 0.646541 | no_sleep::deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626826 | 0.707567 | 35 | 0.065862 | 0.672130 | 0.700493 | 0.675301 | 0.575523 | 0.579797 | 0.539053 | 0.645489 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626873 | 0.707767 | 31 | 0.065700 | 0.672319 | 0.701097 | 0.674465 | 0.575652 | 0.579826 | 0.537510 | 0.647245 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626901 | 0.707601 | 23 | 0.065800 | 0.671793 | 0.701229 | 0.675204 | 0.576236 | 0.579303 | 0.538874 | 0.645666 | no_sleep::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626901 | 0.708833 | 29 | 0.066055 | 0.672323 | 0.701606 | 0.674479 | 0.575975 | 0.579621 | 0.538978 | 0.645326 | no_sleep::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r2_k2_wd0.1_b0.1 | 0.626901 | 0.707837 | 25 | 0.065845 | 0.671724 | 0.700303 | 0.674542 | 0.575872 | 0.579870 | 0.539433 | 0.646566 | no_sleep::deviation | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626905 | 0.707598 | 29 | 0.065881 | 0.672447 | 0.702567 | 0.675269 | 0.575086 | 0.579023 | 0.538894 | 0.645050 | no_sleep::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626934 | 0.707929 | 15 | 0.066013 | 0.672053 | 0.700878 | 0.674740 | 0.576047 | 0.579779 | 0.538833 | 0.646208 | no_sleep::deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k1_b0.1 | 0.626941 | 0.709237 | 14 | 0.066090 | 0.671890 | 0.700707 | 0.675384 | 0.576193 | 0.579892 | 0.538934 | 0.645589 | no_sleep::deviation | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626974 | 0.707903 | 17 | 0.066089 | 0.671770 | 0.700207 | 0.674914 | 0.576319 | 0.580378 | 0.539233 | 0.645995 | no_sleep::deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r1_k2_wd0.1_b0.1 | 0.626983 | 0.708275 | 16 | 0.066072 | 0.671873 | 0.701148 | 0.675007 | 0.576113 | 0.579679 | 0.539065 | 0.645999 | no_sleep::deviation | lowrank | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 0.627006 | 0.715000 | 35 | 0.070804 | 0.672274 | 0.698414 | 0.673920 | 0.576420 | 0.581908 | 0.543144 | 0.642963 | no_sleep::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627012 | 0.708555 | 31 | 0.065747 | 0.672440 | 0.701332 | 0.674819 | 0.576252 | 0.579904 | 0.538606 | 0.645733 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627070 | 0.709348 | 31 | 0.065616 | 0.671905 | 0.700585 | 0.675332 | 0.576075 | 0.580879 | 0.537659 | 0.647054 | only_rhythm::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__linear_k1_b0.1 | 0.627122 | 0.708291 | 14 | 0.066819 | 0.671429 | 0.700179 | 0.675393 | 0.576425 | 0.581060 | 0.538235 | 0.647132 | no_sleep::absolute | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__linear_k1_b0.1 | 0.627141 | 0.707599 | 14 | 0.066295 | 0.671641 | 0.700614 | 0.675036 | 0.576380 | 0.580800 | 0.538833 | 0.646683 | no_sleep::absolute_plus_deviation | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627157 | 0.707009 | 31 | 0.065474 | 0.672540 | 0.702849 | 0.675177 | 0.576104 | 0.580071 | 0.538143 | 0.645213 | no_sleep::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.627158 | 0.707584 | 18 | 0.065827 | 0.672433 | 0.700932 | 0.674800 | 0.576303 | 0.579915 | 0.539026 | 0.646694 | no_sleep::deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.627181 | 0.707296 | 23 | 0.066296 | 0.671546 | 0.700724 | 0.674930 | 0.576632 | 0.581090 | 0.538225 | 0.647123 | no_sleep::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.627185 | 0.707678 | 29 | 0.065676 | 0.671843 | 0.700457 | 0.675404 | 0.575931 | 0.580961 | 0.538581 | 0.647116 | only_rhythm::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.627189 | 0.706868 | 17 | 0.066627 | 0.671655 | 0.700384 | 0.675182 | 0.576480 | 0.581184 | 0.538189 | 0.647252 | no_sleep::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_rhythm__deviation__lowrank_r2_k2_wd0.1_b0.1 | 0.627191 | 0.707868 | 25 | 0.065810 | 0.671951 | 0.700043 | 0.674558 | 0.576442 | 0.581358 | 0.538823 | 0.647163 | only_rhythm::deviation | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.627196 | 0.708932 | 29 | 0.065828 | 0.672496 | 0.700571 | 0.675034 | 0.576153 | 0.580471 | 0.538900 | 0.646748 | only_cross_modal::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_rhythm__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627200 | 0.708528 | 31 | 0.065575 | 0.671854 | 0.700788 | 0.674805 | 0.576137 | 0.581706 | 0.537845 | 0.647262 | only_rhythm::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624249`
- Target-wise drift vs v83: `0.068315`

| target | source | loss |
| --- | --- | --- |
| Q1 | no_sleep__absolute__linear_k1_b0.2 | 0.670697 |
| Q2 | no_sleep__deviation__linear_k2_b0.2 | 0.695579 |
| Q3 | no_sleep__absolute_plus_deviation__lowrank_r2_k2_wd0.1_b0.2 | 0.671722 |
| S1 | no_sleep__deviation__linear_k2_b0.1 | 0.574972 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.579023 |
| S3 | subject_prior | 0.534788 |
| S4 | no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 0.642963 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.