# Nested Deep Learning Golf Selection

## Result

- Subject-prior baseline: `0.627654`
- Best global tiny decoder: `0.625725` (`raw_plus_deviation__lowrank_r3_k2_wd0.1_b0.2`)
- Full-OOF targetwise selection: `0.622155`
- Nested targetwise selection: `0.627983`
- Estimated selection optimism: `0.005829`
- Nested gain vs subject prior: `-0.000329`

## Nested Per Target

| target | nested_loss |
| --- | --- |
| Q1 | 0.676308 |
| Q2 | 0.702214 |
| Q3 | 0.669374 |
| S1 | 0.578060 |
| S2 | 0.584228 |
| S3 | 0.538127 |
| S4 | 0.647572 |

## Nested Selection Counts

| target | source | count |
| --- | --- | --- |
| Q1 | raw_plus_deviation__lowrank_r3_k4_wd0.03_b0.35 | 2 |
| Q1 | deviation__mlp_h3_k8_wd0.03_b0.35 | 1 |
| Q1 | deviation__mlp_h4_k8_wd0.03_b0.35 | 1 |
| Q1 | raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.35 | 1 |
| Q2 | deviation__mlp_h1_k2_wd0.1_b0.35 | 2 |
| Q2 | raw_plus_deviation__lowrank_r4_k4_wd0.03_b0.35 | 2 |
| Q2 | deviation__linear_k8_b0.35 | 1 |
| Q3 | raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.35 | 2 |
| Q3 | raw_plus_deviation__lowrank_r2_k1_wd0.1_b0.35 | 1 |
| Q3 | raw_plus_deviation__mlp_h3_k1_wd0.03_b0.35 | 1 |
| Q3 | raw_plus_deviation__mlp_h4_k1_wd0.03_b0.35 | 1 |
| S1 | deviation__mlp_h2_k8_wd0.03_b0.1 | 2 |
| S1 | deviation__lowrank_r2_k4_wd0.03_b0.1 | 1 |
| S1 | raw_plus_deviation__lowrank_r2_k4_wd0.03_b0.1 | 1 |
| S1 | raw_plus_deviation__mlp_h2_k8_wd0.03_b0.1 | 1 |
| S2 | deviation__mlp_h1_k8_wd0.1_b0.1 | 1 |
| S2 | raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.1 | 1 |
| S2 | raw_plus_deviation__mlp_h4_k4_wd0.03_b0.1 | 1 |
| S2 | raw_plus_deviation__mlp_h4_k4_wd0.03_b0.2 | 1 |
| S2 | raw_plus_deviation__mlp_h4_k8_wd0.03_b0.2 | 1 |
| S3 | raw_plus_deviation__lowrank_r3_k2_wd0.03_b0.2 | 2 |
| S3 | raw_plus_deviation__lowrank_r4_k8_wd0.1_b0.2 | 2 |
| S3 | raw_plus_deviation__lowrank_r3_k8_wd0.03_b0.2 | 1 |
| S4 | raw_plus_deviation__linear_k8_b0.2 | 1 |
| S4 | raw_plus_deviation__lowrank_r3_k8_wd0.03_b0.2 | 1 |
| S4 | raw_plus_deviation__lowrank_r3_k8_wd0.1_b0.35 | 1 |
| S4 | raw_plus_deviation__lowrank_r4_k4_wd0.03_b0.2 | 1 |
| S4 | raw_plus_deviation__lowrank_r4_k4_wd0.1_b0.35 | 1 |

## Full Targetwise Selection

| target | source | loss |
| --- | --- | --- |
| Q1 | raw_plus_deviation__lowrank_r3_k4_wd0.03_b0.35 | 0.665925 |
| Q2 | deviation__mlp_h1_k2_wd0.1_b0.35 | 0.692571 |
| Q3 | raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.35 | 0.665810 |
| S1 | deviation__mlp_h2_k8_wd0.03_b0.1 | 0.575292 |
| S2 | raw_plus_deviation__mlp_h2_k2_wd0.03_b0.1 | 0.579040 |
| S3 | raw_plus_deviation__lowrank_r3_k2_wd0.03_b0.2 | 0.532240 |
| S4 | raw_plus_deviation__lowrank_r3_k8_wd0.03_b0.2 | 0.644205 |

## Top Global Sources

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw_plus_deviation__lowrank_r3_k2_wd0.1_b0.2 | 0.625725 | 0.668183 | 0.700656 | 0.670797 | 0.576963 | 0.582260 | 0.532272 | 0.648944 |
| raw_plus_deviation__lowrank_r3_k2_wd0.03_b0.2 | 0.625750 | 0.668148 | 0.700782 | 0.670845 | 0.576980 | 0.582285 | 0.532240 | 0.648972 |
| raw_plus_deviation__lowrank_r1_k2_wd0.03_b0.2 | 0.625771 | 0.669611 | 0.698768 | 0.671158 | 0.577498 | 0.580917 | 0.533402 | 0.649040 |
| raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.2 | 0.625791 | 0.668195 | 0.697900 | 0.669850 | 0.578723 | 0.582401 | 0.536525 | 0.646941 |
| raw_plus_deviation__lowrank_r1_k2_wd0.1_b0.2 | 0.625797 | 0.669651 | 0.698715 | 0.671170 | 0.577488 | 0.580910 | 0.533583 | 0.649060 |
| raw_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.625833 | 0.668248 | 0.698052 | 0.669835 | 0.578796 | 0.582441 | 0.536576 | 0.646886 |
| raw_plus_deviation__lowrank_r4_k1_wd0.1_b0.2 | 0.625856 | 0.668335 | 0.698587 | 0.670801 | 0.578351 | 0.582152 | 0.536676 | 0.646089 |
| raw_plus_deviation__lowrank_r4_k1_wd0.03_b0.2 | 0.625860 | 0.668324 | 0.698709 | 0.670813 | 0.578340 | 0.582173 | 0.536584 | 0.646075 |
| raw_plus_deviation__linear_k1_b0.2 | 0.625873 | 0.668323 | 0.699396 | 0.670818 | 0.578335 | 0.581988 | 0.536109 | 0.646138 |
| raw_plus_deviation__lowrank_r2_k2_wd0.1_b0.2 | 0.625881 | 0.669084 | 0.699970 | 0.671014 | 0.578295 | 0.581703 | 0.534539 | 0.646564 |
| raw_plus_deviation__lowrank_r2_k2_wd0.03_b0.2 | 0.625884 | 0.669114 | 0.699904 | 0.670981 | 0.578362 | 0.581698 | 0.534504 | 0.646627 |
| raw_plus_deviation__lowrank_r2_k4_wd0.03_b0.2 | 0.625902 | 0.669439 | 0.701285 | 0.673074 | 0.576584 | 0.581406 | 0.533870 | 0.645659 |
| raw_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.625914 | 0.669388 | 0.701293 | 0.673037 | 0.576544 | 0.581445 | 0.534001 | 0.645689 |
| raw_plus_deviation__mlp_h4_k4_wd0.03_b0.2 | 0.625937 | 0.668939 | 0.700051 | 0.672919 | 0.577430 | 0.579294 | 0.534200 | 0.648728 |
| raw_plus_deviation__mlp_h4_k4_wd0.1_b0.2 | 0.625952 | 0.668845 | 0.700188 | 0.673025 | 0.577453 | 0.579321 | 0.534199 | 0.648634 |

This diagnostic uses the saved fold-level losses from the golf run. It does not retrain models or reconstruct OOF predictions; it estimates the selection bias of choosing target-specific tiny decoders on the same OOF labels.