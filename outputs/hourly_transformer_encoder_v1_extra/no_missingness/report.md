# Hourly Transformer Encoder - no_missingness

## Representation

- Days: `700`
- Token shape: `24 x 58`
- Base hourly features selected: `52`
- Mean token missing fraction: `0.191884`
- Device: `mps`
- SSL final loss: `0.519439`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p1_w0p1 | 0.626219 | 0.672169 | 0.696362 | 0.673895 | 0.575562 | 0.582154 | 0.535327 | 0.648063 |
| transformer_logreg_c0p3_w0p1 | 0.626337 | 0.673083 | 0.695489 | 0.674372 | 0.575492 | 0.582319 | 0.535252 | 0.648352 |
| transformer_logreg_c0p03_w0p1 | 0.626410 | 0.671735 | 0.697456 | 0.673867 | 0.575708 | 0.582215 | 0.536018 | 0.647873 |
| transformer_logreg_c0p1_w0p05 | 0.626659 | 0.672457 | 0.700387 | 0.675651 | 0.575355 | 0.580618 | 0.534733 | 0.647409 |
| transformer_logreg_c0p3_w0p05 | 0.626673 | 0.672878 | 0.699895 | 0.675850 | 0.575285 | 0.580643 | 0.534644 | 0.647516 |
| transformer_logreg_c0p1_w0p2 | 0.626755 | 0.672796 | 0.689964 | 0.671422 | 0.577329 | 0.586919 | 0.538055 | 0.650800 |
| transformer_ridge_resid_a20_w0p1 | 0.626778 | 0.674509 | 0.700206 | 0.676458 | 0.575072 | 0.580120 | 0.533851 | 0.647231 |
| transformer_logreg_c0p03_w0p2 | 0.626786 | 0.671627 | 0.691667 | 0.671026 | 0.577353 | 0.586637 | 0.539069 | 0.650119 |

## Target-Wise Selection

- Target-wise avg logloss: `0.622597`
- Drift vs reference: `0.070938`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.671627 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.682902 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.668653 |
| S1 | transformer_ridge_resid_a20_w0p1 | 0.575072 |
| S2 | transformer_ridge_resid_a5_w0p05 | 0.579749 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a20_w0p05 | 0.647144 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.