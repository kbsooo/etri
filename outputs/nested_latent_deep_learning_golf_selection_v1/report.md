# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.625415` (`only_cross_modal__deviation__linear_k4_b0.2`)
- Full-OOF targetwise selection: `0.621691`
- Nested targetwise selection: `0.625650`
- Estimated selection optimism: `0.003959`
- Nested gain vs subject prior: `0.002004`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.673264 |
| Q2 | 0.695183 |
| Q3 | 0.667168 |
| S1 | 0.576671 |
| S2 | 0.582281 |
| S3 | 0.534597 |
| S4 | 0.650383 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 2 |
| Q1 | full__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q1 | full__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 1 |
| Q1 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| Q2 | no_sleep__deviation__linear_k4_b0.2 | 3 |
| Q2 | full__deviation__linear_k4_b0.2 | 1 |
| Q2 | no_sleep__deviation__mlp_h1_k2_wd0.1_b0.2 | 1 |
| Q3 | only_cross_modal__deviation__linear_k4_b0.2 | 3 |
| Q3 | no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.2 | 2 |
| S1 | only_cross_modal__deviation__linear_k4_b0.2 | 3 |
| S1 | full__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S1 | only_cross_modal__deviation__linear_k4_b0.1 | 1 |
| S2 | full__absolute_plus_deviation__linear_k2_b0.1 | 1 |
| S2 | full__absolute_plus_deviation__linear_k2_b0.2 | 1 |
| S2 | full__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 1 |
| S2 | full__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| S2 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k1_wd0.1_b0.1 | 1 |
| S3 | full__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 3 |
| S3 | full__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 2 |
| S4 | full__deviation__linear_k4_b0.2 | 2 |
| S4 | full__absolute_plus_deviation__linear_k4_b0.1 | 1 |
| S4 | full__deviation__linear_k4_b0.1 | 1 |
| S4 | full__deviation__mlp_h2_k2_wd0.1_b0.1 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668725 |
| Q2 | no_sleep__deviation__linear_k4_b0.2 | 0.686441 |
| Q3 | only_cross_modal__deviation__linear_k4_b0.2 | 0.663959 |
| S1 | only_cross_modal__deviation__linear_k4_b0.1 | 0.573616 |
| S2 | full__absolute_plus_deviation__linear_k2_b0.1 | 0.578591 |
| S3 | full__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.534145 |
| S4 | full__deviation__linear_k4_b0.1 | 0.646359 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__deviation__linear_k4_b0.2 | 0.625415 | 0.671802 | 0.693386 | 0.663959 | 0.573829 | 0.581593 | 0.544137 | 0.649197 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.625496 | 0.669502 | 0.692345 | 0.671798 | 0.575351 | 0.580172 | 0.540999 | 0.648302 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.625650 | 0.671841 | 0.698397 | 0.670054 | 0.573616 | 0.579544 | 0.538408 | 0.647689 |
| full__deviation__linear_k4_b0.2 | 0.625719 | 0.671925 | 0.687773 | 0.672838 | 0.576746 | 0.581879 | 0.542154 | 0.646716 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.625736 | 0.672508 | 0.688800 | 0.665119 | 0.577815 | 0.583295 | 0.544063 | 0.648550 |
| full__deviation__linear_k4_b0.1 | 0.625817 | 0.671929 | 0.695374 | 0.674758 | 0.575330 | 0.579780 | 0.537188 | 0.646359 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625834 | 0.668725 | 0.695762 | 0.673168 | 0.575329 | 0.580796 | 0.537701 | 0.649355 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625894 | 0.672226 | 0.695791 | 0.670814 | 0.575866 | 0.580713 | 0.538426 | 0.647422 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.625975 | 0.670883 | 0.698072 | 0.674289 | 0.574967 | 0.579266 | 0.537217 | 0.647132 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626073 | 0.672244 | 0.694687 | 0.671336 | 0.576649 | 0.581280 | 0.538712 | 0.647604 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626075 | 0.670990 | 0.690610 | 0.668446 | 0.578053 | 0.584061 | 0.541200 | 0.649161 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626106 | 0.671544 | 0.697044 | 0.672629 | 0.576042 | 0.581111 | 0.536668 | 0.647701 |
| no_sleep__deviation__linear_k4_b0.2 | 0.626154 | 0.672605 | 0.686441 | 0.666267 | 0.579505 | 0.584580 | 0.544692 | 0.648986 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.626163 | 0.669856 | 0.696377 | 0.671420 | 0.575105 | 0.580453 | 0.539894 | 0.650035 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626205 | 0.670538 | 0.699820 | 0.675126 | 0.574952 | 0.579570 | 0.535613 | 0.647814 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.