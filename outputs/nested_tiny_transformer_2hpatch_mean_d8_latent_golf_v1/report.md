# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626507` (`only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1`)
- Full-OOF targetwise selection: `0.623597`
- Nested targetwise selection: `0.625922`
- Estimated selection optimism: `0.002325`
- Nested gain vs subject prior: `0.001732`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.673371 |
| Q2 | 0.689148 |
| Q3 | 0.673140 |
| S1 | 0.577955 |
| S2 | 0.583611 |
| S3 | 0.538309 |
| S4 | 0.645917 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 3 |
| Q1 | no_sleep__absolute__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h1_k1_wd0.1_b0.2 | 1 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 5 |
| Q3 | only_rhythm__absolute__linear_k2_b0.2 | 3 |
| Q3 | no_sleep__absolute__lowrank_r2_k2_wd0.1_b0.2 | 2 |
| S1 | only_event__deviation__mlp_h1_k4_wd0.1_b0.1 | 2 |
| S1 | only_rhythm__absolute__linear_k2_b0.1 | 2 |
| S1 | only_rhythm__deviation__linear_k2_b0.2 | 1 |
| S2 | only_cross_modal__absolute__linear_k4_b0.1 | 1 |
| S2 | only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S2 | only_rhythm__absolute__lowrank_r2_k1_wd0.1_b0.1 | 1 |
| S2 | only_rhythm__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S2 | only_rhythm__deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| S3 | only_cross_modal__absolute__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S3 | only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 1 |
| S3 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S4 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.2 | 3 |
| S4 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 1 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 0.670460 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 0.689148 |
| Q3 | only_rhythm__absolute__linear_k2_b0.2 | 0.671784 |
| S1 | only_rhythm__absolute__linear_k2_b0.1 | 0.575297 |
| S2 | only_rhythm__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.579473 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.535110 |
| S4 | no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.643904 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626507 | 0.672564 | 0.698463 | 0.675387 | 0.576764 | 0.579730 | 0.536908 | 0.645736 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.626585 | 0.672372 | 0.696200 | 0.675308 | 0.576956 | 0.580803 | 0.538696 | 0.645763 |
| only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626589 | 0.672560 | 0.697494 | 0.675153 | 0.576056 | 0.581043 | 0.538118 | 0.645702 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.626624 | 0.672455 | 0.698379 | 0.675539 | 0.577566 | 0.579838 | 0.536614 | 0.645975 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626681 | 0.671955 | 0.697706 | 0.675727 | 0.576137 | 0.581165 | 0.538265 | 0.645814 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626691 | 0.671978 | 0.700305 | 0.674928 | 0.576771 | 0.582150 | 0.535425 | 0.645277 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626728 | 0.671994 | 0.700068 | 0.676060 | 0.576315 | 0.580680 | 0.535932 | 0.646049 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626736 | 0.672351 | 0.697554 | 0.675528 | 0.576749 | 0.581050 | 0.537316 | 0.646605 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.2 | 0.626749 | 0.672900 | 0.693287 | 0.673587 | 0.579366 | 0.581349 | 0.541154 | 0.645600 |
| only_cross_modal__absolute__lowrank_r2_k2_wd0.1_b0.1 | 0.626767 | 0.671699 | 0.699144 | 0.675018 | 0.576471 | 0.580937 | 0.537562 | 0.646537 |
| no_sleep__deviation__linear_k2_b0.1 | 0.626794 | 0.672287 | 0.698169 | 0.675838 | 0.576126 | 0.581060 | 0.538713 | 0.645365 |
| no_sleep__absolute__linear_k4_b0.1 | 0.626809 | 0.671778 | 0.699064 | 0.675262 | 0.576576 | 0.580934 | 0.538099 | 0.645952 |
| no_sleep__deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626818 | 0.672471 | 0.698790 | 0.675544 | 0.576350 | 0.580630 | 0.539068 | 0.644876 |
| only_event__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.626819 | 0.671408 | 0.698490 | 0.675166 | 0.576521 | 0.580845 | 0.538183 | 0.647124 |
| only_cross_modal__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.626821 | 0.671640 | 0.699543 | 0.675405 | 0.576689 | 0.580452 | 0.537633 | 0.646380 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.