# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626520` (`only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2`)
- Full-OOF targetwise selection: `0.624392`
- Nested targetwise selection: `0.627370`
- Estimated selection optimism: `0.002978`
- Nested gain vs subject prior: `0.000284`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.672465 |
| Q2 | 0.698350 |
| Q3 | 0.675821 |
| S1 | 0.577272 |
| S2 | 0.582006 |
| S3 | 0.538039 |
| S4 | 0.647637 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_event__absolute__linear_k1_b0.2 | 2 |
| Q1 | no_sleep__absolute__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q1 | no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 1 |
| Q1 | no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q2 | only_event__deviation__linear_k4_b0.2 | 3 |
| Q2 | no_sleep__absolute__linear_k4_b0.2 | 1 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 1 |
| Q3 | no_sleep__deviation__linear_k2_b0.2 | 1 |
| Q3 | no_sleep__deviation__lowrank_r2_k2_wd0.1_b0.2 | 1 |
| Q3 | no_sleep__deviation__mlp_h2_k1_wd0.1_b0.2 | 1 |
| Q3 | no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| Q3 | only_rhythm__absolute__lowrank_r2_k2_wd0.1_b0.2 | 1 |
| S1 | only_rhythm__absolute__mlp_h1_k4_wd0.1_b0.1 | 3 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S1 | only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S2 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 2 |
| S2 | only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S2 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 1 |
| S3 | only_event__absolute_plus_deviation__linear_k4_b0.1 | 3 |
| S3 | no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S3 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 1 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 3 |
| S4 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 1 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute__linear_k1_b0.2 | 0.669688 |
| Q2 | only_event__deviation__linear_k4_b0.2 | 0.692256 |
| Q3 | no_sleep__deviation__linear_k2_b0.2 | 0.672209 |
| S1 | only_rhythm__absolute__mlp_h1_k4_wd0.1_b0.1 | 0.574926 |
| S2 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 0.579488 |
| S3 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 0.536583 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.645594 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.626520 | 0.672458 | 0.695444 | 0.674367 | 0.575461 | 0.580735 | 0.540473 | 0.646700 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626591 | 0.672472 | 0.699663 | 0.675782 | 0.574942 | 0.579692 | 0.537093 | 0.646490 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626742 | 0.671426 | 0.699740 | 0.675869 | 0.575635 | 0.581195 | 0.536634 | 0.646695 |
| only_cross_modal__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626836 | 0.671865 | 0.699595 | 0.675271 | 0.575742 | 0.580543 | 0.538662 | 0.646176 |
| only_event__deviation__linear_k4_b0.1 | 0.626864 | 0.672249 | 0.697944 | 0.676151 | 0.575179 | 0.581462 | 0.538319 | 0.646744 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626892 | 0.671798 | 0.698510 | 0.675693 | 0.575561 | 0.580983 | 0.539887 | 0.645810 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626911 | 0.670610 | 0.695585 | 0.674527 | 0.576810 | 0.583790 | 0.539851 | 0.647208 |
| only_cross_modal__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.626915 | 0.672337 | 0.699335 | 0.675431 | 0.575819 | 0.580575 | 0.538253 | 0.646655 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.626916 | 0.672328 | 0.699674 | 0.676699 | 0.575686 | 0.580858 | 0.536607 | 0.646562 |
| only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 0.626926 | 0.671799 | 0.701191 | 0.676287 | 0.576210 | 0.579488 | 0.536583 | 0.646922 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626931 | 0.672122 | 0.700356 | 0.675677 | 0.575095 | 0.580970 | 0.537483 | 0.646815 |
| only_cross_modal__deviation__linear_k1_b0.1 | 0.626941 | 0.672171 | 0.698929 | 0.675820 | 0.575861 | 0.580541 | 0.538963 | 0.646304 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626948 | 0.671333 | 0.700214 | 0.675395 | 0.576158 | 0.581529 | 0.537366 | 0.646640 |
| only_cross_modal__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626973 | 0.672157 | 0.698868 | 0.675389 | 0.576063 | 0.581075 | 0.539086 | 0.646176 |
| only_event__absolute__lowrank_r1_k1_wd0.1_b0.1 | 0.626979 | 0.671446 | 0.698955 | 0.675013 | 0.576285 | 0.580859 | 0.538790 | 0.647503 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.