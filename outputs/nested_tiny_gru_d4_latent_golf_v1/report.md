# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.626403` (`no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1`)
- Full-OOF targetwise selection: `0.623327`
- Nested targetwise selection: `0.625675`
- Estimated selection optimism: `0.002347`
- Nested gain vs subject prior: `0.001979`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.671440 |
| Q2 | 0.697794 |
| Q3 | 0.674156 |
| S1 | 0.577848 |
| S2 | 0.578848 |
| S3 | 0.534884 |
| S4 | 0.644754 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 3 |
| Q1 | only_event__absolute__lowrank_r2_k1_wd0.1_b0.2 | 1 |
| Q1 | only_rhythm__absolute_plus_deviation__mlp_h1_k2_wd0.1_b0.2 | 1 |
| Q2 | no_sleep__absolute__linear_k4_b0.2 | 1 |
| Q2 | no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| Q2 | only_cross_modal__absolute__linear_k4_b0.2 | 1 |
| Q2 | only_cross_modal__absolute__mlp_h1_k4_wd0.1_b0.2 | 1 |
| Q2 | only_event__deviation__linear_k4_b0.2 | 1 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h2_k1_wd0.1_b0.2 | 2 |
| Q3 | only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.2 | 1 |
| Q3 | only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| Q3 | only_rhythm__deviation__mlp_h2_k4_wd0.1_b0.2 | 1 |
| S1 | only_event__deviation__mlp_h2_k2_wd0.1_b0.1 | 2 |
| S1 | no_sleep__absolute__linear_k4_b0.1 | 1 |
| S1 | no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 1 |
| S1 | only_event__deviation__mlp_h2_k2_wd0.1_b0.2 | 1 |
| S2 | only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 4 |
| S2 | only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |
| S3 | only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 5 |
| S4 | only_cross_modal__absolute_plus_deviation__mlp_h2_k2_wd0.1_b0.2 | 3 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k2_wd0.1_b0.2 | 1 |
| S4 | only_cross_modal__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | only_rhythm__absolute_plus_deviation__mlp_h1_k2_wd0.1_b0.2 | 0.668803 |
| Q2 | no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.691920 |
| Q3 | only_rhythm__absolute_plus_deviation__mlp_h2_k1_wd0.1_b0.2 | 0.671160 |
| S1 | only_event__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.575014 |
| S2 | only_cross_modal__deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.578155 |
| S3 | only_event__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.534884 |
| S4 | only_cross_modal__absolute_plus_deviation__mlp_h2_k2_wd0.1_b0.2 | 0.643356 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626403 | 0.671569 | 0.697886 | 0.675027 | 0.575507 | 0.580510 | 0.537414 | 0.646910 |
| no_sleep__deviation__mlp_h2_k4_wd0.1_b0.2 | 0.626429 | 0.671015 | 0.691920 | 0.672909 | 0.576679 | 0.582730 | 0.542051 | 0.647703 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.1 | 0.626517 | 0.671786 | 0.698901 | 0.675444 | 0.575248 | 0.580308 | 0.537895 | 0.646036 |
| no_sleep__absolute_plus_deviation__linear_k4_b0.2 | 0.626634 | 0.671351 | 0.694014 | 0.673693 | 0.576384 | 0.582432 | 0.542464 | 0.646100 |
| only_event__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626640 | 0.670526 | 0.701064 | 0.674472 | 0.576021 | 0.582182 | 0.535762 | 0.646453 |
| no_sleep__deviation__linear_k4_b0.1 | 0.626658 | 0.672237 | 0.698629 | 0.675132 | 0.575983 | 0.579947 | 0.538697 | 0.645982 |
| no_sleep__absolute_plus_deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626773 | 0.672135 | 0.699052 | 0.674880 | 0.575890 | 0.581475 | 0.537276 | 0.646702 |
| no_sleep__absolute_plus_deviation__lowrank_r1_k4_wd0.1_b0.1 | 0.626788 | 0.671507 | 0.700777 | 0.675791 | 0.575354 | 0.580912 | 0.536492 | 0.646683 |
| only_cross_modal__deviation__mlp_h2_k2_wd0.1_b0.1 | 0.626829 | 0.672329 | 0.699472 | 0.675266 | 0.576150 | 0.580995 | 0.538680 | 0.644915 |
| no_sleep__absolute_plus_deviation__lowrank_r2_k4_wd0.1_b0.1 | 0.626838 | 0.672365 | 0.700157 | 0.675109 | 0.575050 | 0.580908 | 0.538143 | 0.646132 |
| only_cross_modal__absolute__mlp_h1_k4_wd0.1_b0.1 | 0.626844 | 0.671307 | 0.698256 | 0.675220 | 0.576403 | 0.580843 | 0.537993 | 0.647886 |
| only_cross_modal__absolute__lowrank_r2_k4_wd0.1_b0.1 | 0.626855 | 0.671430 | 0.698850 | 0.675586 | 0.577040 | 0.580490 | 0.538327 | 0.646261 |
| only_event__deviation__linear_k4_b0.1 | 0.626877 | 0.672476 | 0.698710 | 0.675037 | 0.576225 | 0.581441 | 0.537399 | 0.646852 |
| only_event__deviation__mlp_h2_k4_wd0.1_b0.1 | 0.626882 | 0.672285 | 0.701150 | 0.675086 | 0.575632 | 0.580934 | 0.536318 | 0.646768 |
| no_sleep__absolute__linear_k4_b0.1 | 0.626907 | 0.672632 | 0.698528 | 0.675628 | 0.575273 | 0.581033 | 0.538664 | 0.646593 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.