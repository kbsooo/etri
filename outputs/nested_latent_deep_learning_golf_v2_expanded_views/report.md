# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.624475` (`only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2`)
- Full-OOF targetwise selection: `0.621446`
- Nested targetwise selection: `0.626385`
- Estimated selection optimism: `0.004939`
- Nested gain vs subject prior: `0.001269`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.673442 |
| Q2 | 0.695183 |
| Q3 | 0.667542 |
| S1 | 0.576573 |
| S2 | 0.583435 |
| S3 | 0.538139 |
| S4 | 0.650383 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 2 |
| Q1 | full__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q1 | full__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 1 |
| Q1 | only_rhythm__deviation__mlp_h2_k2_wd0.1_b0.2 | 1 |
| Q2 | no_sleep__deviation__linear_k4_b0.2 | 3 |
| Q2 | full__deviation__linear_k4_b0.2 | 1 |
| Q2 | no_sleep__deviation__mlp_h1_k2_wd0.1_b0.2 | 1 |
| Q3 | only_cross_modal__deviation__linear_k4_b0.2 | 2 |
| Q3 | only_event__deviation__linear_k2_b0.2 | 2 |
| Q3 | only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 2 |
| S1 | only_cross_modal__deviation__linear_k4_b0.1 | 1 |
| S1 | only_cross_modal__deviation__linear_k4_b0.2 | 1 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| S2 | full__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 1 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S2 | only_event__absolute_plus_deviation__mlp_h1_k2_wd0.1_b0.2 | 1 |
| S2 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S2 | only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S3 | only_event__absolute_plus_deviation__lowrank_r1_k2_wd0.1_b0.1 | 2 |
| S3 | only_event__absolute_plus_deviation__mlp_h1_k2_wd0.1_b0.1 | 1 |
| S3 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 1 |
| S3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| S4 | full__deviation__linear_k4_b0.2 | 2 |
| S4 | full__absolute_plus_deviation__linear_k4_b0.1 | 1 |
| S4 | full__deviation__linear_k4_b0.1 | 1 |
| S4 | full__deviation__mlp_h2_k2_wd0.1_b0.1 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.668725 |
| Q2 | no_sleep__deviation__linear_k4_b0.2 | 0.686441 |
| Q3 | only_event__deviation__linear_k2_b0.2 | 0.663937 |
| S1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.573058 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.578312 |
| S3 | only_event__absolute_plus_deviation__lowrank_r1_k2_wd0.1_b0.1 | 0.533290 |
| S4 | full__deviation__linear_k4_b0.1 | 0.646359 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.624475 | 0.671309 | 0.694722 | 0.670161 | 0.573058 | 0.578439 | 0.533860 | 0.649777 |
| only_event__absolute_plus_deviation__linear_k4_b0.2 | 0.624517 | 0.672140 | 0.693708 | 0.669661 | 0.573520 | 0.578951 | 0.533983 | 0.649657 |
| only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.624903 | 0.669217 | 0.693161 | 0.664391 | 0.575596 | 0.580348 | 0.543851 | 0.647757 |
| only_cross_modal__deviation__linear_k4_b0.2 | 0.625415 | 0.671802 | 0.693386 | 0.663959 | 0.573829 | 0.581593 | 0.544137 | 0.649197 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625433 | 0.671875 | 0.699184 | 0.673557 | 0.573717 | 0.578312 | 0.533344 | 0.648044 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.625471 | 0.672284 | 0.698738 | 0.673289 | 0.574011 | 0.578578 | 0.533449 | 0.647951 |
| only_rhythm__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625484 | 0.670595 | 0.698319 | 0.670360 | 0.574790 | 0.578946 | 0.538366 | 0.647010 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.625496 | 0.669502 | 0.692345 | 0.671798 | 0.575351 | 0.580172 | 0.540999 | 0.648302 |
| only_cross_modal__deviation__linear_k4_b0.1 | 0.625650 | 0.671841 | 0.698397 | 0.670054 | 0.573616 | 0.579544 | 0.538408 | 0.647689 |
| full__deviation__linear_k4_b0.2 | 0.625719 | 0.671925 | 0.687773 | 0.672838 | 0.576746 | 0.581879 | 0.542154 | 0.646716 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.625736 | 0.672508 | 0.688800 | 0.665119 | 0.577815 | 0.583295 | 0.544063 | 0.648550 |
| full__deviation__linear_k4_b0.1 | 0.625817 | 0.671929 | 0.695374 | 0.674758 | 0.575330 | 0.579780 | 0.537188 | 0.646359 |
| only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625834 | 0.668725 | 0.695762 | 0.673168 | 0.575329 | 0.580796 | 0.537701 | 0.649355 |
| only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.625835 | 0.672416 | 0.693369 | 0.665979 | 0.575855 | 0.580223 | 0.544020 | 0.648981 |
| no_sleep__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.625894 | 0.672226 | 0.695791 | 0.670814 | 0.575866 | 0.580713 | 0.538426 | 0.647422 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.