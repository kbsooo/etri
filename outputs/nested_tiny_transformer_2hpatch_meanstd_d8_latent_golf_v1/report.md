# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626070` (`only_cross_modal__absolute_plus_deviation__linear_k4_b0.2`)
- Full-OOF targetwise selection: `0.623447`
- Nested targetwise selection: `0.626027`
- Estimated selection optimism: `0.002580`
- Nested gain vs subject prior: `0.001627`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.671508 |
| Q2 | 0.688253 |
| Q3 | 0.674981 |
| S1 | 0.577536 |
| S2 | 0.581547 |
| S3 | 0.538185 |
| S4 | 0.650177 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 3 |
| Q1 | only_cross_modal__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 1 |
| Q1 | only_event__absolute__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| Q2 | only_cross_modal__absolute__linear_k4_b0.2 | 4 |
| Q2 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 1 |
| Q3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 3 |
| Q3 | only_event__absolute_plus_deviation__mlp_h1_k4_wd0.1_b0.2 | 1 |
| Q3 | only_event__deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| S1 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 2 |
| S1 | only_cross_modal__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S1 | only_cross_modal__deviation__linear_k2_b0.1 | 1 |
| S1 | only_rhythm__absolute__lowrank_r2_k2_wd0.1_b0.1 | 1 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 3 |
| S2 | no_sleep__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 1 |
| S2 | only_event__deviation__lowrank_r1_k1_wd0.1_b0.1 | 1 |
| S3 | no_sleep__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 2 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 2 |
| S3 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 1 |
| S4 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 2 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 1 |
| S4 | only_event__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| S4 | only_event__deviation__mlp_h1_k2_wd0.1_b0.1 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.668602 |
| Q2 | only_cross_modal__absolute__linear_k4_b0.2 | 0.687393 |
| Q3 | no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.2 | 0.671895 |
| S1 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.575345 |
| S2 | only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.579826 |
| S3 | only_cross_modal__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.535364 |
| S4 | only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.645704 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.2 | 0.626070 | 0.672253 | 0.688113 | 0.674479 | 0.579795 | 0.582515 | 0.539628 | 0.645704 |
| only_cross_modal__absolute_plus_deviation__linear_k4_b0.1 | 0.626305 | 0.672390 | 0.695647 | 0.675875 | 0.576997 | 0.580540 | 0.536774 | 0.645913 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626571 | 0.671722 | 0.697941 | 0.674937 | 0.575751 | 0.580696 | 0.538058 | 0.646895 |
| only_cross_modal__deviation__linear_k2_b0.1 | 0.626583 | 0.672263 | 0.696501 | 0.675118 | 0.575678 | 0.581060 | 0.539050 | 0.646409 |
| only_cross_modal__deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626590 | 0.671846 | 0.696765 | 0.674881 | 0.575876 | 0.580505 | 0.539020 | 0.647238 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.626614 | 0.671811 | 0.698616 | 0.675709 | 0.576448 | 0.580771 | 0.536744 | 0.646197 |
| only_event__absolute_plus_deviation__lowrank_r2_k1_wd0.1_b0.1 | 0.626628 | 0.670264 | 0.699663 | 0.675614 | 0.576949 | 0.579826 | 0.537281 | 0.646800 |
| only_event__absolute__lowrank_r2_k1_wd0.1_b0.1 | 0.626628 | 0.670264 | 0.699663 | 0.675614 | 0.576949 | 0.579826 | 0.537281 | 0.646800 |
| only_cross_modal__absolute__linear_k4_b0.1 | 0.626631 | 0.671329 | 0.695337 | 0.676127 | 0.577173 | 0.580323 | 0.539083 | 0.647043 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626647 | 0.671796 | 0.697022 | 0.675556 | 0.576475 | 0.580658 | 0.538439 | 0.646583 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626671 | 0.671197 | 0.692302 | 0.672736 | 0.576925 | 0.582980 | 0.542944 | 0.647615 |
| no_sleep__absolute_plus_deviation__linear_k2_b0.1 | 0.626672 | 0.671461 | 0.698503 | 0.675088 | 0.576503 | 0.581171 | 0.537598 | 0.646377 |
| no_sleep__deviation__lowrank_r1_k1_wd0.1_b0.1 | 0.626705 | 0.671720 | 0.697508 | 0.674837 | 0.576270 | 0.580487 | 0.538682 | 0.647429 |
| only_event__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626720 | 0.672011 | 0.698530 | 0.674964 | 0.576510 | 0.580110 | 0.538213 | 0.646700 |
| only_event__absolute_plus_deviation__linear_k4_b0.1 | 0.626720 | 0.672027 | 0.699032 | 0.675581 | 0.576055 | 0.580499 | 0.536707 | 0.647143 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.