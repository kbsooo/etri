# Deep Learning Golf v1

## Goal

Start the neural encoder-decoder path from the smallest possible parameter counts. This run avoids teacher submissions and uses v83 only as a drift reference.

## Setup

- Device: `mps`
- Base daily/window features: `629`
- Input top-k: small supervised fold-local selections only.
- Decoder families: bias-only, subject prior, linear, low-rank rank 1-4, tiny tanh MLP hidden 1-4.

## Result

- Best source: `targetwise`
- OOF avg logloss: `0.622155`
- Subject-prior OOF avg logloss: `0.627654`
- Gain vs subject prior: `0.005499`
- Macro F1 @ 0.5: `0.706096`
- Drift vs v83 reference: `0.067578`

## Target Gain vs Subject Prior

| target | gain |
| --- | --- |
| Q1 | 0.007254 |
| Q2 | 0.012439 |
| Q3 | 0.011960 |
| S1 | 0.000410 |
| S2 | 0.000816 |
| S3 | 0.002547 |
| S4 | 0.003067 |

## Subject Drift vs v83

| subject_id | mean_abs_drift |
| --- | --- |
| id01 | 0.038606 |
| id02 | 0.050093 |
| id03 | 0.069530 |
| id04 | 0.063168 |
| id05 | 0.081525 |
| id06 | 0.076057 |
| id07 | 0.077166 |
| id08 | 0.094785 |
| id09 | 0.063648 |
| id10 | 0.077806 |

## Top Scores

| source | avg_log_loss | macro_f1_at_0p5 | mean_params | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | mode | model | top_k | bottleneck | weight_decay | blend |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| raw_plus_deviation__lowrank_r3_k2_wd0.1_b0.2 | 0.625725 | 0.707124 | 34 | 0.068649 | 0.668183 | 0.700656 | 0.670797 | 0.576963 | 0.582260 | 0.532272 | 0.648944 | raw_plus_deviation | lowrank | 2.000000 | 3.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__lowrank_r3_k2_wd0.03_b0.2 | 0.625750 | 0.707124 | 34 | 0.068625 | 0.668148 | 0.700782 | 0.670845 | 0.576980 | 0.582285 | 0.532240 | 0.648972 | raw_plus_deviation | lowrank | 2.000000 | 3.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r1_k2_wd0.03_b0.2 | 0.625771 | 0.707966 | 16 | 0.068988 | 0.669611 | 0.698768 | 0.671158 | 0.577498 | 0.580917 | 0.533402 | 0.649040 | raw_plus_deviation | lowrank | 2.000000 | 1.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.2 | 0.625791 | 0.711585 | 23 | 0.069397 | 0.668195 | 0.697900 | 0.669850 | 0.578723 | 0.582401 | 0.536525 | 0.646941 | raw_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r1_k2_wd0.1_b0.2 | 0.625797 | 0.708274 | 16 | 0.069021 | 0.669651 | 0.698715 | 0.671170 | 0.577488 | 0.580910 | 0.533583 | 0.649060 | raw_plus_deviation | lowrank | 2.000000 | 1.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__lowrank_r2_k1_wd0.1_b0.2 | 0.625833 | 0.710726 | 23 | 0.069390 | 0.668248 | 0.698052 | 0.669835 | 0.578796 | 0.582441 | 0.536576 | 0.646886 | raw_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__lowrank_r4_k1_wd0.1_b0.2 | 0.625856 | 0.709001 | 39 | 0.069078 | 0.668335 | 0.698587 | 0.670801 | 0.578351 | 0.582152 | 0.536676 | 0.646089 | raw_plus_deviation | lowrank | 1.000000 | 4.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__lowrank_r4_k1_wd0.03_b0.2 | 0.625860 | 0.708870 | 39 | 0.069061 | 0.668324 | 0.698709 | 0.670813 | 0.578340 | 0.582173 | 0.536584 | 0.646075 | raw_plus_deviation | lowrank | 1.000000 | 4.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__linear_k1_b0.2 | 0.625873 | 0.705828 | 14 | 0.069382 | 0.668323 | 0.699396 | 0.670818 | 0.578335 | 0.581988 | 0.536109 | 0.646138 | raw_plus_deviation | linear | 1.000000 | 0.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r2_k2_wd0.1_b0.2 | 0.625881 | 0.706965 | 25 | 0.069155 | 0.669084 | 0.699970 | 0.671014 | 0.578295 | 0.581703 | 0.534539 | 0.646564 | raw_plus_deviation | lowrank | 2.000000 | 2.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__lowrank_r2_k2_wd0.03_b0.2 | 0.625884 | 0.707486 | 25 | 0.069176 | 0.669114 | 0.699904 | 0.670981 | 0.578362 | 0.581698 | 0.534504 | 0.646627 | raw_plus_deviation | lowrank | 2.000000 | 2.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r2_k4_wd0.03_b0.2 | 0.625902 | 0.705109 | 29 | 0.066864 | 0.669439 | 0.701285 | 0.673074 | 0.576584 | 0.581406 | 0.533870 | 0.645659 | raw_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r2_k4_wd0.1_b0.2 | 0.625914 | 0.704429 | 29 | 0.066884 | 0.669388 | 0.701293 | 0.673037 | 0.576544 | 0.581445 | 0.534001 | 0.645689 | raw_plus_deviation | lowrank | 4.000000 | 2.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__mlp_h4_k4_wd0.03_b0.2 | 0.625937 | 0.707934 | 55 | 0.066029 | 0.668939 | 0.700051 | 0.672919 | 0.577430 | 0.579294 | 0.534200 | 0.648728 | raw_plus_deviation | tiny_mlp | 4.000000 | 4.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__mlp_h4_k4_wd0.1_b0.2 | 0.625952 | 0.707712 | 55 | 0.065981 | 0.668845 | 0.700188 | 0.673025 | 0.577453 | 0.579321 | 0.534199 | 0.648634 | raw_plus_deviation | tiny_mlp | 4.000000 | 4.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__lowrank_r1_k1_wd0.03_b0.2 | 0.625972 | 0.708496 | 15 | 0.068638 | 0.668412 | 0.699607 | 0.670179 | 0.578034 | 0.581682 | 0.536585 | 0.647303 | raw_plus_deviation | lowrank | 1.000000 | 1.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r1_k1_wd0.1_b0.2 | 0.625981 | 0.708496 | 15 | 0.068668 | 0.668437 | 0.699551 | 0.670190 | 0.578155 | 0.581684 | 0.536659 | 0.647192 | raw_plus_deviation | lowrank | 1.000000 | 1.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__mlp_h1_k2_wd0.03_b0.2 | 0.626002 | 0.707386 | 17 | 0.068583 | 0.670033 | 0.698472 | 0.671808 | 0.577909 | 0.580770 | 0.534044 | 0.648978 | raw_plus_deviation | tiny_mlp | 2.000000 | 1.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r4_k4_wd0.03_b0.2 | 0.626028 | 0.705200 | 51 | 0.066753 | 0.669517 | 0.697404 | 0.673051 | 0.578800 | 0.582265 | 0.536501 | 0.644659 | raw_plus_deviation | lowrank | 4.000000 | 4.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r4_k4_wd0.1_b0.2 | 0.626038 | 0.704664 | 51 | 0.066781 | 0.669552 | 0.697492 | 0.673018 | 0.578781 | 0.582218 | 0.536546 | 0.644658 | raw_plus_deviation | lowrank | 4.000000 | 4.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__linear_k4_b0.2 | 0.626098 | 0.707088 | 35 | 0.066168 | 0.669367 | 0.700733 | 0.673562 | 0.576864 | 0.581321 | 0.534737 | 0.646103 | raw_plus_deviation | linear | 4.000000 | 0.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.1 | 0.626108 | 0.705855 | 23 | 0.064778 | 0.670140 | 0.700965 | 0.673429 | 0.576650 | 0.580163 | 0.534776 | 0.646630 | raw_plus_deviation | lowrank | 1.000000 | 2.000000 | 0.030000 | 0.100000 |
| raw_plus_deviation__mlp_h4_k1_wd0.03_b0.2 | 0.626111 | 0.708970 | 43 | 0.068998 | 0.669233 | 0.698861 | 0.670496 | 0.579151 | 0.581213 | 0.537155 | 0.646670 | raw_plus_deviation | tiny_mlp | 1.000000 | 4.000000 | 0.030000 | 0.200000 |
| raw_plus_deviation__mlp_h1_k2_wd0.1_b0.2 | 0.626125 | 0.707251 | 17 | 0.068604 | 0.670149 | 0.698612 | 0.672087 | 0.577825 | 0.580939 | 0.534279 | 0.648984 | raw_plus_deviation | tiny_mlp | 2.000000 | 1.000000 | 0.100000 | 0.200000 |
| raw_plus_deviation__lowrank_r3_k2_wd0.1_b0.1 | 0.626128 | 0.706800 | 34 | 0.064592 | 0.670174 | 0.702320 | 0.673876 | 0.575771 | 0.580508 | 0.532614 | 0.647634 | raw_plus_deviation | lowrank | 2.000000 | 3.000000 | 0.100000 | 0.100000 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622155`
- Target-wise drift vs v83: `0.067578`

| target | source | loss |
| --- | --- | --- |
| Q1 | raw_plus_deviation__lowrank_r3_k4_wd0.03_b0.35 | 0.665925 |
| Q2 | deviation__mlp_h1_k2_wd0.1_b0.35 | 0.692571 |
| Q3 | raw_plus_deviation__lowrank_r2_k1_wd0.03_b0.35 | 0.665810 |
| S1 | deviation__mlp_h2_k8_wd0.03_b0.1 | 0.575292 |
| S2 | raw_plus_deviation__mlp_h2_k2_wd0.03_b0.1 | 0.579040 |
| S3 | raw_plus_deviation__lowrank_r3_k2_wd0.03_b0.2 | 0.532240 |
| S4 | raw_plus_deviation__lowrank_r3_k8_wd0.03_b0.2 | 0.644205 |

## Decision

This is the minimum-parameter neural floor. If a rank-1/hidden-1 model beats subject prior with low drift, the signal is probably a simple subject-relative axis. If only larger or target-wise selected models win, the branch needs stronger validation before it can be trusted.