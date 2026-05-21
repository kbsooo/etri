# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626826` (`only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1`)
- Full-OOF targetwise selection: `0.624639`
- Nested targetwise selection: `0.627956`
- Estimated selection optimism: `0.003317`
- Nested gain vs subject prior: `-0.000302`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.672378 |
| Q2 | 0.697529 |
| Q3 | 0.674817 |
| S1 | 0.578354 |
| S2 | 0.582947 |
| S3 | 0.540121 |
| S4 | 0.649547 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_event__absolute__lowrank_r2_k1_wd0.1_b0.2 | 3 |
| Q1 | only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| Q1 | only_rhythm__absolute_plus_deviation__mlp_h1_k1_wd0.1_b0.2 | 1 |
| Q2 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 3 |
| Q2 | only_cross_modal__absolute__lowrank_r1_k1_wd0.1_b0.2 | 1 |
| Q2 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| Q3 | no_sleep__deviation__mlp_h2_k1_wd0.1_b0.2 | 1 |
| Q3 | only_rhythm__absolute__lowrank_r1_k4_wd0.1_b0.2 | 1 |
| Q3 | only_rhythm__absolute_plus_deviation__linear_k2_b0.2 | 1 |
| Q3 | only_rhythm__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q3 | only_rhythm__deviation__linear_k2_b0.2 | 1 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 2 |
| S1 | no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 1 |
| S1 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| S1 | only_rhythm__absolute__linear_k1_b0.1 | 1 |
| S2 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 2 |
| S2 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.2 | 1 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S3 | no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 2 |
| S3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S3 | only_rhythm__absolute__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S3 | only_rhythm__deviation__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S4 | only_cross_modal__absolute__lowrank_r1_k2_wd0.1_b0.1 | 1 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k2_wd0.1_b0.1 | 1 |
| S4 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S4 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S4 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.670185 |
| Q2 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.692494 |
| Q3 | only_rhythm__absolute_plus_deviation__linear_k2_b0.2 | 0.671600 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.575168 |
| S2 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.578694 |
| S3 | no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.537859 |
| S4 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.646472 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626826 | 0.672490 | 0.700821 | 0.674878 | 0.575342 | 0.579483 | 0.538092 | 0.646675 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626993 | 0.672736 | 0.700962 | 0.675943 | 0.575168 | 0.578993 | 0.538677 | 0.646472 |
| no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627036 | 0.671838 | 0.700351 | 0.674605 | 0.576578 | 0.581001 | 0.537903 | 0.646978 |
| no_sleep__deviation__linear_k4_b0.1 | 0.627071 | 0.672049 | 0.699997 | 0.675001 | 0.575772 | 0.580809 | 0.538450 | 0.647419 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627089 | 0.671806 | 0.700855 | 0.674670 | 0.576641 | 0.580545 | 0.537859 | 0.647249 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.627102 | 0.672229 | 0.699298 | 0.675181 | 0.576380 | 0.581156 | 0.538154 | 0.647317 |
| only_rhythm__absolute_plus_deviation__linear_k4_b0.1 | 0.627112 | 0.671808 | 0.700954 | 0.674507 | 0.575794 | 0.580614 | 0.538295 | 0.647809 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.627115 | 0.672572 | 0.700096 | 0.675584 | 0.575760 | 0.579912 | 0.538862 | 0.647018 |
| only_rhythm__absolute__mlp_h2_k4_wd0.1_b0.1 | 0.627139 | 0.671682 | 0.700725 | 0.674941 | 0.575639 | 0.580659 | 0.538626 | 0.647702 |
| only_rhythm__absolute__mlp_h1_k2_wd0.1_b0.1 | 0.627142 | 0.671586 | 0.700447 | 0.674894 | 0.576207 | 0.580758 | 0.538815 | 0.647288 |
| no_sleep__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.627144 | 0.671286 | 0.700663 | 0.674974 | 0.576870 | 0.580156 | 0.538783 | 0.647277 |
| only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.627145 | 0.672857 | 0.700689 | 0.676413 | 0.575549 | 0.579424 | 0.538497 | 0.646589 |
| only_event__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.627147 | 0.671087 | 0.699903 | 0.675891 | 0.576563 | 0.580139 | 0.539091 | 0.647357 |
| only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.627147 | 0.671087 | 0.699903 | 0.675891 | 0.576563 | 0.580139 | 0.539091 | 0.647357 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.627152 | 0.672295 | 0.700026 | 0.674976 | 0.575658 | 0.581086 | 0.538677 | 0.647345 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.