# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.623600`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.004054`
- Macro F1 @ 0.5: `0.709489`
- Drift vs v83 reference: `0.068172`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.002997 |
| Q2 | 0.014871 |
| Q3 | 0.005682 |
| S1 | 0.000363 |
| S2 | 0.000877 |
| S3 | 0.000068 |
| S4 | 0.003522 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.043805 |
| id02 | 0.052347 |
| id03 | 0.063261 |
| id04 | 0.073426 |
| id05 | 0.074149 |
| id06 | 0.074714 |
| id07 | 0.083673 |
| id08 | 0.082436 |
| id09 | 0.068254 |
| id10 | 0.072930 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626371 | 0.707657 | 29 | 0.067286 | 0.672390 | 0.698126 | 0.675252 | 0.576266 | 0.579893 | 0.536876 | 0.645794 | only_cross_modal::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.2 | 0.626458 | 0.713448 | 29 | 0.074503 | 0.672586 | 0.692677 | 0.673331 | 0.578337 | 0.581646 | 0.541015 | 0.645614 | only_cross_modal::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.626541 | 0.706642 | 35 | 0.067446 | 0.672344 | 0.697885 | 0.675477 | 0.577424 | 0.579763 | 0.536938 | 0.645954 | only_cross_modal::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.626565 | 0.707156 | 35 | 0.066382 | 0.671959 | 0.696766 | 0.675358 | 0.576184 | 0.582260 | 0.538674 | 0.644755 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626665 | 0.707559 | 18 | 0.066214 | 0.672284 | 0.698709 | 0.675435 | 0.576314 | 0.580786 | 0.538390 | 0.644737 | only_cross_modal::deviation | lowrank | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626665 | 0.705907 | 29 | 0.066377 | 0.672233 | 0.698587 | 0.674821 | 0.576203 | 0.581303 | 0.538471 | 0.645037 | only_cross_modal::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.626700 | 0.706908 | 17 | 0.066657 | 0.672067 | 0.699220 | 0.675455 | 0.576611 | 0.580650 | 0.537032 | 0.645866 | only_cross_modal::absolute | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__linear_k4_b0.2 | 0.626755 | 0.711299 | 35 | 0.074856 | 0.672579 | 0.692288 | 0.673780 | 0.580508 | 0.581265 | 0.540792 | 0.646070 | only_cross_modal::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute__linear_k2_b0.1 | 0.626765 | 0.707160 | 21 | 0.066834 | 0.672199 | 0.698850 | 0.675455 | 0.576763 | 0.581158 | 0.537169 | 0.645759 | only_cross_modal::absolute | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626775 | 0.705824 | 35 | 0.066466 | 0.672264 | 0.698408 | 0.675672 | 0.576149 | 0.582287 | 0.536815 | 0.645833 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626795 | 0.707225 | 23 | 0.066368 | 0.671604 | 0.699148 | 0.675683 | 0.576911 | 0.580283 | 0.537685 | 0.646250 | only_cross_modal::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.626795 | 0.707225 | 23 | 0.066368 | 0.671604 | 0.699148 | 0.675683 | 0.576911 | 0.580283 | 0.537685 | 0.646250 | only_cross_modal::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k1_b0.1 | 0.626809 | 0.705426 | 14 | 0.066202 | 0.672246 | 0.698495 | 0.675649 | 0.576445 | 0.580650 | 0.538777 | 0.645404 | only_cross_modal::deviation | linear | 1.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r1_k2_wd0.1_b0.1 | 0.626825 | 0.708116 | 16 | 0.066816 | 0.672078 | 0.699536 | 0.675579 | 0.576707 | 0.580811 | 0.536843 | 0.646223 | only_cross_modal::absolute | lowrank | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626829 | 0.708000 | 29 | 0.066640 | 0.672246 | 0.700232 | 0.675071 | 0.576593 | 0.582696 | 0.535057 | 0.645906 | only_cross_modal::absolute_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__mlp_h2_k4_wd0.1_b0.1 | 0.626852 | 0.705774 | 31 | 0.066655 | 0.672101 | 0.699765 | 0.675146 | 0.576795 | 0.580721 | 0.536679 | 0.646756 | only_cross_modal::absolute | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.626858 | 0.706890 | 23 | 0.066652 | 0.671521 | 0.700227 | 0.675667 | 0.576681 | 0.578979 | 0.537579 | 0.647349 | no_sleep::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626858 | 0.706890 | 23 | 0.066652 | 0.671521 | 0.700227 | 0.675667 | 0.576681 | 0.578979 | 0.537579 | 0.647349 | no_sleep::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626862 | 0.702877 | 31 | 0.065857 | 0.672401 | 0.699676 | 0.674800 | 0.576089 | 0.580645 | 0.538046 | 0.646377 | only_event::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.626862 | 0.704609 | 35 | 0.066572 | 0.672678 | 0.700789 | 0.675733 | 0.576429 | 0.579210 | 0.536676 | 0.646523 | no_sleep::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__mlp_h1_k4_wd0.1_b0.1 | 0.626867 | 0.707078 | 19 | 0.066666 | 0.672199 | 0.699080 | 0.675455 | 0.576535 | 0.580857 | 0.537307 | 0.646639 | only_cross_modal::absolute | tiny_mlp | 4.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626868 | 0.706024 | 15 | 0.066665 | 0.671717 | 0.698746 | 0.675254 | 0.576791 | 0.580570 | 0.538060 | 0.646938 | only_cross_modal::absolute_plus_deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r1_k1_wd0.1_b0.1 | 0.626868 | 0.706024 | 15 | 0.066665 | 0.671717 | 0.698746 | 0.675254 | 0.576791 | 0.580570 | 0.538060 | 0.646938 | only_cross_modal::absolute | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k2_wd0.1_b0.1 | 0.626869 | 0.708626 | 25 | 0.066647 | 0.672152 | 0.699196 | 0.675049 | 0.576578 | 0.581041 | 0.537593 | 0.646475 | only_cross_modal::absolute | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k4_b0.2 | 0.626876 | 0.711456 | 35 | 0.072286 | 0.671782 | 0.690139 | 0.673560 | 0.578105 | 0.586323 | 0.544308 | 0.643914 | only_cross_modal::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623600`
- Target-wise drift vs v83: `0.068172`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_rhythm__absolute__mlp_h1_k2_wd0.1_b0.2 | 0.670182 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 0.690139 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h1_k1_wd0.1_b0.2 | 0.672089 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.575339 |
| S2 | no_sleep__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.578979 |
| S3 | only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 0.534719 |
| S4 | only_cross_modal__deviation__lowrank_r1_k4_wd0.1_b0.2 | 0.643750 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.