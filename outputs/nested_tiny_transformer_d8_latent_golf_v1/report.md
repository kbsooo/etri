# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626371` (`only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1`)
- Full-OOF targetwise selection: `0.623600`
- Nested targetwise selection: `0.625441`
- Estimated selection optimism: `0.001841`
- Nested gain vs subject prior: `0.002213`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.673116 |
| Q2 | 0.690139 |
| Q3 | 0.673699 |
| S1 | 0.575983 |
| S2 | 0.583431 |
| S3 | 0.535263 |
| S4 | 0.646455 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_rhythm__absolute__mlp_h1_k2_wd0.1_b0.2 | 2 |
| Q1 | only_rhythm__deviation__lowrank_r2_k1_wd0.1_b0.2 | 2 |
| Q1 | no_sleep__absolute__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 5 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h1_k1_wd0.1_b0.2 | 3 |
| Q3 | only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q3 | only_event__deviation__lowrank_r2_k2_wd0.1_b0.2 | 1 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 4 |
| S1 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 2 |
| S2 | no_sleep__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 1 |
| S2 | no_sleep__deviation__mlp_h2_k2_wd0.1_b0.1 | 1 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S3 | only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 4 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S4 | only_cross_modal__deviation__lowrank_r1_k4_wd0.1_b0.2 | 2 |
| S4 | only_cross_modal__deviation__linear_k2_b0.1 | 1 |
| S4 | only_cross_modal__deviation__linear_k4_b0.2 | 1 |
| S4 | only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_rhythm__absolute__mlp_h1_k2_wd0.1_b0.2 | 0.670182 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 0.690139 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h1_k1_wd0.1_b0.2 | 0.672089 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.575339 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.578979 |
| S3 | only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 0.534719 |
| S4 | only_cross_modal__deviation__lowrank_r1_k4_wd0.1_b0.2 | 0.643750 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626371 | 0.672390 | 0.698126 | 0.675252 | 0.576266 | 0.579893 | 0.536876 | 0.645794 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.2 | 0.626458 | 0.672586 | 0.692677 | 0.673331 | 0.578337 | 0.581646 | 0.541015 | 0.645614 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.626541 | 0.672344 | 0.697885 | 0.675477 | 0.577424 | 0.579763 | 0.536938 | 0.645954 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.626565 | 0.671959 | 0.696766 | 0.675358 | 0.576184 | 0.582260 | 0.538674 | 0.644755 |
| only_cross_modal__deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626665 | 0.672284 | 0.698709 | 0.675435 | 0.576314 | 0.580786 | 0.538390 | 0.644737 |
| only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626665 | 0.672233 | 0.698587 | 0.674821 | 0.576203 | 0.581303 | 0.538471 | 0.645037 |
| only_cross_modal__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.626700 | 0.672067 | 0.699220 | 0.675455 | 0.576611 | 0.580650 | 0.537032 | 0.645866 |
| only_cross_modal__absolute__linear_k4_b0.2 | 0.626755 | 0.672579 | 0.692288 | 0.673780 | 0.580508 | 0.581265 | 0.540792 | 0.646070 |
| only_cross_modal__absolute__linear_k2_b0.1 | 0.626765 | 0.672199 | 0.698850 | 0.675455 | 0.576763 | 0.581158 | 0.537169 | 0.645759 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626775 | 0.672264 | 0.698408 | 0.675672 | 0.576149 | 0.582287 | 0.536815 | 0.645833 |
| only_cross_modal__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.626795 | 0.671604 | 0.699148 | 0.675683 | 0.576911 | 0.580283 | 0.537685 | 0.646250 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626795 | 0.671604 | 0.699148 | 0.675683 | 0.576911 | 0.580283 | 0.537685 | 0.646250 |
| only_cross_modal__deviation__linear_k1_b0.1 | 0.626809 | 0.672246 | 0.698495 | 0.675649 | 0.576445 | 0.580650 | 0.538777 | 0.645404 |
| only_cross_modal__absolute__lowrank_r1_k2_wd0.1_b0.1 | 0.626825 | 0.672078 | 0.699536 | 0.675579 | 0.576707 | 0.580811 | 0.536843 | 0.646223 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626829 | 0.672246 | 0.700232 | 0.675071 | 0.576593 | 0.582696 | 0.535057 | 0.645906 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.