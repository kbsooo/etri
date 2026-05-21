# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626613` (`only_rhythm__absolute__lowrank_r2_k4_wd0.1_b0.1`)
- Full-OOF targetwise selection: `0.624144`
- Nested targetwise selection: `0.626537`
- Estimated selection optimism: `0.002392`
- Nested gain vs subject prior: `0.001117`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.672336 |
| Q2 | 0.694581 |
| Q3 | 0.673921 |
| S1 | 0.575511 |
| S2 | 0.580561 |
| S3 | 0.538593 |
| S4 | 0.650253 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.2 | 4 |
| Q1 | only_rhythm__absolute__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q2 | no_sleep__absolute__lowrank_r2_k4_wd0.1_b0.2 | 4 |
| Q2 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 1 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 3 |
| Q3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 2 |
| S1 | only_rhythm__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 3 |
| S1 | only_rhythm__absolute_plus_deviation__linear_k4_b0.1 | 1 |
| S1 | only_rhythm__absolute_plus_deviation__linear_k4_b0.2 | 1 |
| S2 | only_rhythm__absolute__lowrank_r2_k1_wd0.1_b0.1 | 2 |
| S2 | only_rhythm__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 2 |
| S2 | only_rhythm__absolute_plus_deviation__lowrank_r1_k1_wd0.1_b0.1 | 1 |
| S3 | full__absolute_plus_deviation__linear_k4_b0.1 | 2 |
| S3 | no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S3 | only_cross_modal__deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S4 | full__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 1 |
| S4 | full__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| S4 | only_rhythm__deviation__linear_k1_b0.1 | 1 |
| S4 | only_rhythm__deviation__linear_k2_b0.1 | 1 |
| S4 | only_rhythm__deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.669600 |
| Q2 | no_sleep__absolute__lowrank_r2_k4_wd0.1_b0.2 | 0.692021 |
| Q3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.671532 |
| S1 | only_rhythm__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.574249 |
| S2 | only_rhythm__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.579289 |
| S3 | full__absolute_plus_deviation__linear_k4_b0.1 | 0.536139 |
| S4 | only_rhythm__deviation__linear_k2_b0.1 | 0.646179 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_rhythm__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626613 | 0.671320 | 0.699270 | 0.675311 | 0.576196 | 0.579703 | 0.537652 | 0.646840 |
| no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626616 | 0.670726 | 0.698720 | 0.675003 | 0.576700 | 0.580522 | 0.537380 | 0.647261 |
| only_rhythm__absolute__linear_k4_b0.1 | 0.626736 | 0.672834 | 0.699079 | 0.675330 | 0.575469 | 0.579483 | 0.538499 | 0.646458 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626790 | 0.671588 | 0.699504 | 0.675362 | 0.575964 | 0.580175 | 0.537135 | 0.647800 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626793 | 0.672385 | 0.699239 | 0.675231 | 0.575958 | 0.580265 | 0.536575 | 0.647895 |
| only_rhythm__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626831 | 0.671402 | 0.702006 | 0.675338 | 0.574249 | 0.579990 | 0.538066 | 0.646767 |
| no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626862 | 0.672901 | 0.699879 | 0.674375 | 0.576505 | 0.580354 | 0.536806 | 0.647218 |
| full__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626875 | 0.672425 | 0.699602 | 0.675506 | 0.576235 | 0.580446 | 0.537257 | 0.646651 |
| only_rhythm__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626883 | 0.671305 | 0.701425 | 0.674625 | 0.575407 | 0.580501 | 0.537883 | 0.647033 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626934 | 0.672073 | 0.699200 | 0.675253 | 0.576308 | 0.581016 | 0.537300 | 0.647389 |
| no_sleep__deviation__linear_k1_b0.1 | 0.626952 | 0.671747 | 0.698903 | 0.675350 | 0.576413 | 0.580658 | 0.537765 | 0.647829 |
| only_cross_modal__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.626956 | 0.671547 | 0.698719 | 0.675341 | 0.576754 | 0.581001 | 0.537370 | 0.647960 |
| no_sleep__deviation__mlp_h1_k2_wd0.1_b0.1 | 0.626958 | 0.671618 | 0.699613 | 0.675241 | 0.576243 | 0.580881 | 0.537763 | 0.647350 |
| full__absolute__mlp_h2_k4_wd0.1_b0.1 | 0.626979 | 0.672144 | 0.700077 | 0.675620 | 0.576390 | 0.580448 | 0.537230 | 0.646947 |
| only_rhythm__absolute__lowrank_r1_k4_wd0.1_b0.1 | 0.626995 | 0.672554 | 0.699363 | 0.674913 | 0.576616 | 0.580289 | 0.537977 | 0.647253 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.