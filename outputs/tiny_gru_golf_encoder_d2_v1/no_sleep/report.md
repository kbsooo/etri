# Hourly Transformer Encoder - no_sleep

## Representation

- Encoder type: `gru`
- Encoder params: `1727`
- Days: `700`
- Token shape: `48 x 335`
- Base hourly features selected: `82`
- Mean token missing fraction: `0.084437`
- Device: `mps`
- SSL final loss: `0.671745`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627347 | 0.672385 | 0.702787 | 0.676408 | 0.575925 | 0.580364 | 0.536335 | 0.647224 |
| transformer_logreg_c0p1_w0p05 | 0.627349 | 0.672377 | 0.702776 | 0.676412 | 0.575935 | 0.580403 | 0.536314 | 0.647228 |
| transformer_logreg_c0p3_w0p05 | 0.627350 | 0.672374 | 0.702772 | 0.676414 | 0.575938 | 0.580417 | 0.536307 | 0.647229 |
| transformer_logreg_c0p03_w0p1 | 0.627358 | 0.671853 | 0.700812 | 0.675191 | 0.576483 | 0.581331 | 0.538382 | 0.647455 |
| transformer_logreg_c0p1_w0p1 | 0.627364 | 0.671841 | 0.700792 | 0.675200 | 0.576500 | 0.581407 | 0.538346 | 0.647464 |
| transformer_logreg_c0p3_w0p1 | 0.627367 | 0.671837 | 0.700786 | 0.675202 | 0.576506 | 0.581434 | 0.538334 | 0.647467 |
| transformer_ridge_resid_a20_w0p35 | 0.627480 | 0.673410 | 0.704655 | 0.677840 | 0.575379 | 0.579747 | 0.535388 | 0.645942 |
| transformer_ridge_resid_a5_w0p35 | 0.627481 | 0.673419 | 0.704651 | 0.677843 | 0.575376 | 0.579753 | 0.535401 | 0.645927 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624398`
- Drift vs reference: `0.066493`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p1_w0p2 | 0.671481 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.694122 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.671158 |
| S1 | transformer_ridge_resid_a1_w0p35 | 0.575375 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.579698 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.645922 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.