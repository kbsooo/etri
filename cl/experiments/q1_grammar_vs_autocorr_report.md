# Q1 — Q-family grammar vs autocorr

For each Q target, we test whether *cross-target* lags (Q1→Q3, Q2→Q3 etc.) add information *beyond* own-target lag. If yes → grammar is real. If only own-lag works → it's just temporal autocorrelation.


## 1. Per-family × target × model (mean logloss across folds)


### chrono_tail

| model | Q1 | Q2 | Q3 | Qavg |
|---|---|---|---|---|
| M0_anchor | 0.6732 | 0.6893 | 0.7054 | 0.6893 |
| M1_own_lag_back | 0.6753 | 0.6828 | 0.6931 | 0.6837 |
| M2_neighbor_mean_3 | 0.6767 | 0.6775 | 0.6949 | 0.6830 |
| M3_own_lag_back_fwd | 0.6750 | 0.6773 | 0.6845 | 0.6789 |
| M4_all_q_lags_back | 0.6751 | 0.6848 | 0.6878 | 0.6826 |
| M5_all_q_lags_back_fwd | 0.6746 | 0.6798 | 0.6794 | 0.6779 |

### hole_v1

| model | Q1 | Q2 | Q3 | Qavg |
|---|---|---|---|---|
| M0_anchor | 0.7092 | 0.6846 | 0.6680 | 0.6873 |
| M1_own_lag_back | 0.6966 | 0.6510 | 0.6614 | 0.6697 |
| M2_neighbor_mean_3 | 0.6975 | 0.6357 | 0.6588 | 0.6640 |
| M3_own_lag_back_fwd | 0.6825 | 0.6476 | 0.6484 | 0.6595 |
| M4_all_q_lags_back | 0.6977 | 0.6570 | 0.6645 | 0.6731 |
| M5_all_q_lags_back_fwd | 0.6844 | 0.6526 | 0.6509 | 0.6626 |

### mirror_v1

| model | Q1 | Q2 | Q3 | Qavg |
|---|---|---|---|---|
| M0_anchor | 0.7148 | 0.7566 | 0.7368 | 0.7361 |
| M1_own_lag_back | 0.7133 | 0.7351 | 0.7271 | 0.7252 |
| M2_neighbor_mean_3 | 0.7190 | 0.7098 | 0.7242 | 0.7177 |
| M3_own_lag_back_fwd | 0.7077 | 0.7146 | 0.7179 | 0.7134 |
| M4_all_q_lags_back | 0.7124 | 0.7311 | 0.7163 | 0.7199 |
| M5_all_q_lags_back_fwd | 0.7069 | 0.7122 | 0.7077 | 0.7089 |


## 2. Key contrasts (averaged across folds)

Negative = better. M1=own lag, M2=neighbor mean, M3=+forward, M4=+cross-Q lags, M5=full.

| target | chrono_tail: M1-M0 | chrono_tail: M2-M1 | chrono_tail: M3-M1 | chrono_tail: M4-M1 | chrono_tail: M5-M4 | hole_v1: M1-M0 | hole_v1: M2-M1 | hole_v1: M3-M1 | hole_v1: M4-M1 | hole_v1: M5-M4 | mirror_v1: M1-M0 | mirror_v1: M2-M1 | mirror_v1: M3-M1 | mirror_v1: M4-M1 | mirror_v1: M5-M4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | 0.0021 | 0.0014 | -0.0004 | -0.0003 | -0.0005 | -0.0126 | 0.0009 | -0.0141 | 0.0011 | -0.0133 | -0.0016 | 0.0058 | -0.0055 | -0.0008 | -0.0056 |
| Q2 | -0.0064 | -0.0053 | -0.0055 | 0.0020 | -0.0050 | -0.0336 | -0.0152 | -0.0033 | 0.0060 | -0.0044 | -0.0214 | -0.0253 | -0.0205 | -0.0040 | -0.0189 |
| Q3 | -0.0122 | 0.0017 | -0.0087 | -0.0053 | -0.0084 | -0.0066 | -0.0026 | -0.0130 | 0.0031 | -0.0136 | -0.0098 | -0.0029 | -0.0092 | -0.0108 | -0.0087 |


## 3. Interpretation rules
- **M2 ≈ M1 across families** → naive neighbor smoothing adds nothing over own-lag.
- **M3 << M1 on hole_v1 only** → forward neighbor labels are huge on holes (structurally legitimate; 62% of test). Their absence on chrono_tail is expected.
- **M4 < M1 on chrono_tail and mirror_v1 by > 0.005** → cross-Q grammar is real *causal* info.
- **M4 ≈ M1** → 'grammar' is a misnomer, Q-lag effects are just autocorr.
- **M5 - M4 ≈ M3 - M1** → forward info is additive to grammar (no interaction).
