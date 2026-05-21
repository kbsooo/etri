# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.625489` (`only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2`)
- Full-OOF targetwise selection: `0.623253`
- Nested targetwise selection: `0.626112`
- Estimated selection optimism: `0.002860`
- Nested gain vs subject prior: `0.001542`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.670882 |
| Q2 | 0.698558 |
| Q3 | 0.669105 |
| S1 | 0.578881 |
| S2 | 0.579503 |
| S3 | 0.538003 |
| S4 | 0.647854 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 4 |
| Q1 | only_rhythm__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 2 |
| Q2 | only_cross_modal__absolute__linear_k4_b0.2 | 1 |
| Q2 | only_cross_modal__deviation__linear_k2_b0.2 | 1 |
| Q2 | only_event__absolute__linear_k1_b0.2 | 1 |
| Q3 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 4 |
| Q3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| S1 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 2 |
| S1 | no_sleep__absolute__mlp_h2_k1_wd0.1_b0.2 | 1 |
| S1 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| S1 | only_event__deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S2 | only_event__deviation__mlp_h2_k2_wd0.1_b0.2 | 3 |
| S2 | only_event__deviation__mlp_h2_k2_wd0.1_b0.1 | 2 |
| S3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 2 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S3 | only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.1 | 1 |
| S4 | only_cross_modal__deviation__linear_k4_b0.2 | 2 |
| S4 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 1 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S4 | only_cross_modal__deviation__linear_k4_b0.1 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668481 |
| Q2 | only_cross_modal__deviation__linear_k4_b0.2 | 0.693065 |
| Q3 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668657 |
| S1 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.574878 |
| S2 | only_event__deviation__mlp_h2_k2_wd0.1_b0.2 | 0.577401 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.535337 |
| S4 | only_cross_modal__deviation__linear_k4_b0.2 | 0.644951 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625489 | 0.670268 | 0.695175 | 0.669096 | 0.575354 | 0.580180 | 0.538505 | 0.649848 |
| only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.625842 | 0.671228 | 0.699470 | 0.673117 | 0.574878 | 0.578837 | 0.535338 | 0.648023 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626038 | 0.668481 | 0.697866 | 0.668657 | 0.578027 | 0.581550 | 0.539828 | 0.647856 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626133 | 0.670310 | 0.700926 | 0.672888 | 0.576207 | 0.579499 | 0.536032 | 0.647067 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.626161 | 0.672200 | 0.695749 | 0.674488 | 0.576761 | 0.580797 | 0.538063 | 0.645067 |
| only_event__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626220 | 0.670833 | 0.699309 | 0.675092 | 0.575485 | 0.579690 | 0.536289 | 0.646839 |
| only_event__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.626334 | 0.669780 | 0.694761 | 0.673057 | 0.577166 | 0.581582 | 0.540480 | 0.647513 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626361 | 0.672252 | 0.699798 | 0.675845 | 0.575645 | 0.579565 | 0.535844 | 0.645574 |
| only_event__deviation__mlp_h2_k2_wd0.1_b0.2 | 0.626383 | 0.669909 | 0.698194 | 0.671989 | 0.576554 | 0.577401 | 0.541447 | 0.649187 |
| only_event__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.626383 | 0.671029 | 0.701148 | 0.674588 | 0.575516 | 0.577510 | 0.537146 | 0.647745 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.626572 | 0.672021 | 0.700558 | 0.673866 | 0.576577 | 0.580493 | 0.535557 | 0.646931 |
| only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626608 | 0.671408 | 0.701555 | 0.675107 | 0.576189 | 0.579880 | 0.536184 | 0.645935 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626626 | 0.671661 | 0.696376 | 0.673119 | 0.577267 | 0.583157 | 0.539076 | 0.645726 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626633 | 0.671973 | 0.700139 | 0.675171 | 0.576043 | 0.580923 | 0.536228 | 0.645954 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.626662 | 0.671805 | 0.698409 | 0.675637 | 0.576219 | 0.580369 | 0.538724 | 0.645471 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.