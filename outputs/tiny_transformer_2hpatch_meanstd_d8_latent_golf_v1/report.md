# Latent Deep Learning Golf v1

## Goal

Apply the minimum-parameter golf decoder discipline to existing channel-patch Transformer CLS latents.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.623365`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.004289`
- Macro F1 @ 0.5: `0.710504`
- Drift vs v83 reference: `0.067642`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.004577 |
| Q2 | 0.017617 |
| Q3 | 0.005875 |
| S1 | 0.000357 |
| S2 | 0.000031 |
| S3 | 0.000000 |
| S4 | 0.001568 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.042171 |
| id02 | 0.054454 |
| id03 | 0.058799 |
| id04 | 0.070808 |
| id05 | 0.072664 |
| id06 | 0.077044 |
| id07 | 0.085289 |
| id08 | 0.085221 |
| id09 | 0.066541 |
| id10 | 0.069701 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.626070 | 0.713381 | 35 | 0.071472 | 0.672253 | 0.688113 | 0.674479 | 0.579795 | 0.582515 | 0.539628 | 0.645704 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.200000 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626305 | 0.708947 | 35 | 0.066061 | 0.672390 | 0.695647 | 0.675875 | 0.576997 | 0.580540 | 0.536774 | 0.645913 | only_cross_modal::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626571 | 0.707829 | 31 | 0.066117 | 0.671722 | 0.697941 | 0.674937 | 0.575751 | 0.580696 | 0.538058 | 0.646895 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__linear_k2_b0.1 | 0.626583 | 0.707555 | 21 | 0.066337 | 0.672263 | 0.696501 | 0.675118 | 0.575678 | 0.581060 | 0.539050 | 0.646409 | only_cross_modal::deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626590 | 0.706403 | 15 | 0.066186 | 0.671846 | 0.696765 | 0.674881 | 0.575876 | 0.580505 | 0.539020 | 0.647238 | only_cross_modal::deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.626614 | 0.707058 | 35 | 0.065922 | 0.671811 | 0.698616 | 0.675709 | 0.576448 | 0.580771 | 0.536744 | 0.646197 | no_sleep::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.626628 | 0.707391 | 23 | 0.066268 | 0.670264 | 0.699663 | 0.675614 | 0.576949 | 0.579826 | 0.537281 | 0.646800 | only_event::absolute | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626628 | 0.707391 | 23 | 0.066268 | 0.670264 | 0.699663 | 0.675614 | 0.576949 | 0.579826 | 0.537281 | 0.646800 | only_event::absolute_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.626631 | 0.707340 | 35 | 0.066655 | 0.671329 | 0.695337 | 0.676127 | 0.577173 | 0.580323 | 0.539083 | 0.647043 | only_cross_modal::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626647 | 0.706986 | 35 | 0.066079 | 0.671796 | 0.697022 | 0.675556 | 0.576475 | 0.580658 | 0.538439 | 0.646583 | no_sleep::deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626671 | 0.715134 | 31 | 0.071757 | 0.671197 | 0.692302 | 0.672736 | 0.576925 | 0.582980 | 0.542944 | 0.647615 | no_sleep::deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| no_sleep__absolute_plus_deviation__linear_k2_b0.1 | 0.626672 | 0.708589 | 21 | 0.066277 | 0.671461 | 0.698503 | 0.675088 | 0.576503 | 0.581171 | 0.537598 | 0.646377 | no_sleep::absolute_plus_deviation | linear | 2.000000 | 0.000000 | 0.100000 | 0.100000 |
| no_sleep__deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626705 | 0.705111 | 15 | 0.065929 | 0.671720 | 0.697508 | 0.674837 | 0.576270 | 0.580487 | 0.538682 | 0.647429 | no_sleep::deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_event__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626720 | 0.708184 | 29 | 0.065934 | 0.672011 | 0.698530 | 0.674964 | 0.576510 | 0.580110 | 0.538213 | 0.646700 | only_event::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.626720 | 0.706947 | 35 | 0.065994 | 0.672027 | 0.699032 | 0.675581 | 0.576055 | 0.580499 | 0.536707 | 0.647143 | only_event::absolute_plus_deviation | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626724 | 0.707333 | 17 | 0.066201 | 0.671507 | 0.697952 | 0.675157 | 0.575883 | 0.580783 | 0.539144 | 0.646641 | only_cross_modal::deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute_plus_deviation__mlp_h2_k2_wd0.1_b0.1 | 0.626726 | 0.709437 | 27 | 0.066369 | 0.671383 | 0.697434 | 0.675507 | 0.577319 | 0.581883 | 0.537307 | 0.646249 | no_sleep::absolute_plus_deviation | tiny_mlp | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626727 | 0.704211 | 29 | 0.066415 | 0.672702 | 0.697123 | 0.674796 | 0.576851 | 0.580622 | 0.538653 | 0.646344 | only_cross_modal::deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| no_sleep__absolute__linear_k4_b0.1 | 0.626742 | 0.707126 | 35 | 0.066673 | 0.671615 | 0.697565 | 0.675697 | 0.576704 | 0.580044 | 0.538393 | 0.647173 | no_sleep::absolute | linear | 4.000000 | 0.000000 | 0.100000 | 0.100000 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626742 | 0.705634 | 31 | 0.065826 | 0.671965 | 0.700034 | 0.675692 | 0.575985 | 0.581117 | 0.535949 | 0.646448 | only_event::absolute_plus_deviation | tiny_mlp | 4.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626745 | 0.706830 | 23 | 0.066350 | 0.671855 | 0.698221 | 0.674915 | 0.575962 | 0.580599 | 0.538950 | 0.646710 | only_cross_modal::deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__deviation__lowrank_r2_k2_wd0.1_b0.1 | 0.626748 | 0.707023 | 25 | 0.066154 | 0.672050 | 0.697649 | 0.675076 | 0.576106 | 0.580355 | 0.539202 | 0.646796 | only_cross_modal::deviation | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute_plus_deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626752 | 0.705388 | 15 | 0.066387 | 0.671357 | 0.698072 | 0.675077 | 0.576306 | 0.580639 | 0.538279 | 0.647535 | only_cross_modal::absolute_plus_deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r1_k1_wd0.1_b0.1 | 0.626752 | 0.705388 | 15 | 0.066387 | 0.671357 | 0.698072 | 0.675077 | 0.576306 | 0.580639 | 0.538279 | 0.647535 | only_cross_modal::absolute | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.100000 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626761 | 0.708528 | 29 | 0.066507 | 0.671049 | 0.697595 | 0.675394 | 0.577437 | 0.580183 | 0.537903 | 0.647766 | only_cross_modal::absolute | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623365`
- Target-wise drift vs v83: `0.067642`

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute__lowrank_r2_k1_wd0.1_b0.2 | 0.668602 |
| Q2 | only_cross_modal__absolute__linear_k4_b0.2 | 0.687393 |
| Q3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.671895 |
| S1 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.575345 |
| S2 | only_event__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.579826 |
| S3 | subject_prior | 0.534788 |
| S4 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.645704 |

## Decision

This tests whether the existing Transformer SSL latent is label-readable under a tiny fixed decoder. Targetwise gains are diagnostic only until nested selection is run.