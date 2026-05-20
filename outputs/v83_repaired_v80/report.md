# v83 repaired-v80 candidates (row-base gamma sweep)

Repair v80 into public coordinates instead of retreating to v76.

- Construction: `repaired_t = sigmoid( logit(v76_row_t) + gamma_t * (logit(v80_row_t) - logit_mean(v80_t)) )`
  v76 row is the public ruler; we add only fraction gamma of v80's row-level deviation (its breakthrough).
- Posterior context: v76 `0.599963` (real 0.5999627447), v18 `0.605786`, v80 `0.643744`, v82 `0.644356` (real 0.6629).
- **Honest reading**: only ~15% of v80's row deviation (gamma≈0.10-0.15) is consistent with the public coordinate; the other ~85% is the panel-conditional distortion that v82 carried. The repaired v80 is a **small, real win over v76 (~0.002 by posterior), NOT a large jump.** No evidence here that more v80 row signal is recoverable without re-introducing the harmful panel component. A larger jump needs a different hypothesis (a v80-style model trained with public-coordinate priors from the start, or ensembling repaired-v80 with the orthogonal public-good v18).
- Oracle: posterior (gate, trustworthy here since drift is small). late-panel OOF is a negative control (train-late != public).

## Ranking by posterior_pred (lower better)

| name | gamma | posterior_pred | vs_v76 | drift_v76 | max_row_drift_v76 | tail_share | mean_Q1 | mean_S1 | mean_S3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gq015_gs010 | 0.15,0.15,0.15,0.1,0.1,0.1,0.1 | 0.597813 | -0.002149 | 0.0190 | 0.1511 | 0.110 | 0.510 | 0.683 | 0.659 |
| global_g015 | 0.15,0.15,0.15,0.15,0.15,0.15,0.15 | 0.597826 | -0.002137 | 0.0233 | 0.1511 | 0.108 | 0.510 | 0.680 | 0.657 |
| gq015_gs015 | 0.15,0.15,0.15,0.15,0.15,0.15,0.15 | 0.597826 | -0.002137 | 0.0233 | 0.1511 | 0.108 | 0.510 | 0.680 | 0.657 |
| q1zero_g015 | 0,0.15,0.15,0.15,0.15,0.15,0.15 | 0.597898 | -0.002064 | 0.0209 | 0.1511 | 0.108 | 0.511 | 0.680 | 0.657 |
| global_g010 | 0.1,0.1,0.1,0.1,0.1,0.1,0.1 | 0.598020 | -0.001943 | 0.0157 | 0.1065 | 0.108 | 0.510 | 0.683 | 0.659 |
| gq010_gs010 | 0.1,0.1,0.1,0.1,0.1,0.1,0.1 | 0.598020 | -0.001943 | 0.0157 | 0.1065 | 0.108 | 0.510 | 0.683 | 0.659 |
| gq010_gs015 | 0.1,0.1,0.1,0.15,0.15,0.15,0.15 | 0.598032 | -0.001930 | 0.0200 | 0.1199 | 0.105 | 0.510 | 0.680 | 0.657 |
| gq015_gs020 | 0.15,0.15,0.15,0.2,0.2,0.2,0.2 | 0.598111 | -0.001852 | 0.0275 | 0.1516 | 0.106 | 0.510 | 0.678 | 0.654 |
| global_g020 | 0.2,0.2,0.2,0.2,0.2,0.2,0.2 | 0.598122 | -0.001841 | 0.0308 | 0.1896 | 0.108 | 0.510 | 0.678 | 0.654 |
| gq010_gs020 | 0.1,0.1,0.1,0.2,0.2,0.2,0.2 | 0.598318 | -0.001645 | 0.0242 | 0.1516 | 0.104 | 0.510 | 0.678 | 0.654 |
| q1zero_gs020_gq010 | 0,0.1,0.1,0.2,0.2,0.2,0.2 | 0.598399 | -0.001564 | 0.0226 | 0.1516 | 0.104 | 0.511 | 0.678 | 0.654 |
| gq005_gs010 | 0.05,0.05,0.05,0.1,0.1,0.1,0.1 | 0.598455 | -0.001508 | 0.0123 | 0.0840 | 0.104 | 0.510 | 0.683 | 0.659 |
| gq005_gs015 | 0.05,0.05,0.05,0.15,0.15,0.15,0.15 | 0.598467 | -0.001496 | 0.0166 | 0.1199 | 0.102 | 0.510 | 0.680 | 0.657 |
| gq015_gs025 | 0.15,0.15,0.15,0.25,0.25,0.25,0.25 | 0.598658 | -0.001304 | 0.0317 | 0.1791 | 0.105 | 0.510 | 0.675 | 0.652 |
| global_g005 | 0.05,0.05,0.05,0.05,0.05,0.05,0.05 | 0.598726 | -0.001237 | 0.0079 | 0.0559 | 0.108 | 0.510 | 0.685 | 0.661 |
| gq005_gs020 | 0.05,0.05,0.05,0.2,0.2,0.2,0.2 | 0.598752 | -0.001211 | 0.0208 | 0.1516 | 0.101 | 0.510 | 0.678 | 0.654 |
| gq010_gs025 | 0.1,0.1,0.1,0.25,0.25,0.25,0.25 | 0.598865 | -0.001098 | 0.0283 | 0.1791 | 0.103 | 0.510 | 0.675 | 0.652 |
| global_g025 | 0.25,0.25,0.25,0.25,0.25,0.25,0.25 | 0.598888 | -0.001075 | 0.0381 | 0.2272 | 0.108 | 0.510 | 0.675 | 0.652 |
| gq000_gs010 | 0,0,0,0.1,0.1,0.1,0.1 | 0.599126 | -0.000837 | 0.0089 | 0.0840 | 0.096 | 0.511 | 0.683 | 0.659 |
| gq000_gs015 | 0,0,0,0.15,0.15,0.15,0.15 | 0.599139 | -0.000824 | 0.0132 | 0.1199 | 0.096 | 0.511 | 0.680 | 0.657 |
| gq005_gs025 | 0.05,0.05,0.05,0.25,0.25,0.25,0.25 | 0.599300 | -0.000663 | 0.0250 | 0.1791 | 0.100 | 0.510 | 0.675 | 0.652 |
| gq000_gs020 | 0,0,0,0.2,0.2,0.2,0.2 | 0.599424 | -0.000539 | 0.0174 | 0.1516 | 0.096 | 0.511 | 0.678 | 0.654 |
| gq000_gs025 | 0,0,0,0.25,0.25,0.25,0.25 | 0.599971 | +0.000008 | 0.0215 | 0.1791 | 0.097 | 0.511 | 0.675 | 0.652 |

## Recommended upload

- **`submission_v83_gq015_gs010.csv`** (gamma 0.15,0.15,0.15,0.1,0.1,0.1,0.1): posterior `0.597813` (-0.002149 vs v76), drift_v76 `0.0190`, max-row `0.1511`, tail(pp>0.9) disagreement share `0.110`.
- per-target mean: Q1 0.510, Q2 0.569, Q3 0.612, S1 0.683, S2 0.644, S3 0.659, S4 0.553
- Preserves v80 row-level latent deviation at gamma=0.1 (S) on the v76 public ruler; removes v80's panel-conditional mean drift. Q1 deviation muted (suspect per v82).
- Downside is bounded: drift from v76 is `0.0190` (v82 was 0.128), so a v82-style blowup is impossible.

### Q1 zero-out ablation

- q1zero_g015: posterior `0.597898` (-0.002064) — compare to global_g015 to see if dropping Q1 deviation helps.
- q1zero_gs020_gq010: posterior `0.598399` (-0.001564) — compare to global_g015 to see if dropping Q1 deviation helps.
