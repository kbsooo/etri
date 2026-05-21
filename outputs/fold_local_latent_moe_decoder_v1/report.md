# Fold-Local Latent MoE Decoder v1

## Goal

Move the MoE experiment before probability stacking: target-specific expert latent blocks are subject-centered inside each fold, scaled per block, augmented with block statistics, concatenated, and decoded with small fold-safe residual heads.

## Result

- Best source: `baseline_targetwise_hybrid`
- OOF avg logloss: `0.612448`
- Drift vs v83 reference: `0.095652`

## Top Latent MoE Scores

| source | avg_log_loss | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| selected_single__logreg_c0.03_b0.35 | 0.616397 | 0.097019 | 0.664090 | 0.663244 | 0.666035 | 0.571208 | 0.575222 | 0.522792 | 0.652187 |
| selected_single__logreg_c0.1_b0.2 | 0.617284 | 0.079983 | 0.664651 | 0.676745 | 0.666416 | 0.569526 | 0.574620 | 0.521706 | 0.647327 |
| selected_single__logreg_c0.03_b0.2 | 0.617661 | 0.076130 | 0.665460 | 0.675200 | 0.665955 | 0.570545 | 0.574392 | 0.523170 | 0.648908 |
| selected_single__ridge_a80_b0.2 | 0.617855 | 0.081925 | 0.666422 | 0.679913 | 0.664402 | 0.567320 | 0.575440 | 0.526224 | 0.645264 |
| selected_single__logreg_c0.1_b0.35 | 0.618079 | 0.106145 | 0.665281 | 0.669011 | 0.670509 | 0.571506 | 0.577047 | 0.523288 | 0.649914 |
| selected_single__ridge_a5_b0.1 | 0.619367 | 0.080584 | 0.663355 | 0.696221 | 0.664015 | 0.565215 | 0.578524 | 0.524310 | 0.643927 |
| selected_single__ridge_a20_b0.1 | 0.619688 | 0.072854 | 0.666210 | 0.691232 | 0.665859 | 0.567446 | 0.577703 | 0.524577 | 0.644786 |
| selected_single__ridge_a20_b0.2 | 0.619872 | 0.096613 | 0.663547 | 0.685084 | 0.661269 | 0.563139 | 0.577653 | 0.545147 | 0.643266 |
| selected_single__logreg_c0.1_b0.1 | 0.620763 | 0.067300 | 0.667603 | 0.688129 | 0.669644 | 0.571347 | 0.575808 | 0.526010 | 0.646803 |
| selected_single__ridge_a80_b0.1 | 0.621096 | 0.067300 | 0.668613 | 0.690143 | 0.669091 | 0.570151 | 0.577021 | 0.526685 | 0.645966 |
| selected_single__logreg_c0.03_b0.1 | 0.621398 | 0.066278 | 0.668490 | 0.687945 | 0.670106 | 0.572251 | 0.575976 | 0.527338 | 0.647682 |
| target_moe__logreg_c0.03_b0.2 | 0.622256 | 0.076693 | 0.667766 | 0.677534 | 0.666212 | 0.574880 | 0.587634 | 0.526107 | 0.655660 |
| selected_plus_target_moe__logreg_c0.03_b0.2 | 0.622256 | 0.076693 | 0.667766 | 0.677534 | 0.666212 | 0.574880 | 0.587634 | 0.526107 | 0.655660 |
| selected_single__ridge_a5_b0.05 | 0.622413 | 0.066912 | 0.667331 | 0.699064 | 0.669481 | 0.569576 | 0.578763 | 0.527249 | 0.645428 |
| selected_single__ridge_a20_b0.05 | 0.623017 | 0.064335 | 0.669181 | 0.697154 | 0.670919 | 0.571088 | 0.578519 | 0.528345 | 0.645912 |
| selected_plus_target_moe__logreg_c0.03_b0.1 | 0.623156 | 0.065821 | 0.668702 | 0.688328 | 0.670039 | 0.573606 | 0.582420 | 0.528692 | 0.650307 |
| target_moe__logreg_c0.03_b0.1 | 0.623156 | 0.065821 | 0.668702 | 0.688328 | 0.670039 | 0.573606 | 0.582420 | 0.528692 | 0.650307 |
| target_moe__logreg_c0.1_b0.1 | 0.623345 | 0.066912 | 0.667999 | 0.688669 | 0.669146 | 0.573657 | 0.584590 | 0.528021 | 0.651336 |
| selected_plus_target_moe__logreg_c0.1_b0.1 | 0.623345 | 0.066912 | 0.667999 | 0.688669 | 0.669146 | 0.573657 | 0.584590 | 0.528021 | 0.651336 |
| selected_plus_target_moe__ridge_a80_b0.1 | 0.623652 | 0.073331 | 0.667832 | 0.691773 | 0.668046 | 0.569948 | 0.587113 | 0.528498 | 0.652358 |

## Target-Wise Latent Gate

- Target-wise avg logloss: `0.612530`
- Target-wise drift vs v83: `0.095479`

| target | source | loss |
| --- | --- | --- |
| Q1 | selected_single__ridge_a5_b0.1 | 0.663355 |
| Q2 | selected_single__logreg_c0.03_b0.35 | 0.663244 |
| Q3 | selected_single__ridge_a20_b0.2 | 0.661269 |
| S1 | selected_single__ridge_a5_b0.2 | 0.561740 |
| S2 | selected_single__logreg_c0.03_b0.2 | 0.574392 |
| S3 | selected_single__logreg_c0.1_b0.2 | 0.521706 |
| S4 | selected_single__ridge_a5_b0.2 | 0.642003 |

## Baseline Hybrid

- Hybrid avg logloss: `0.612448`
- Hybrid drift vs v83: `0.095652`

| target | source | loss |
| --- | --- | --- |
| Q1 | baseline | 0.662785 |
| Q2 | selected_single__logreg_c0.03_b0.35 | 0.663244 |
| Q3 | selected_single__ridge_a20_b0.2 | 0.661269 |
| S1 | selected_single__ridge_a5_b0.2 | 0.561740 |
| S2 | selected_single__logreg_c0.03_b0.2 | 0.574392 |
| S3 | selected_single__logreg_c0.1_b0.2 | 0.521706 |
| S4 | selected_single__ridge_a5_b0.2 | 0.642003 |

## Hybrid Shrinkage

Blend the no-PCA fold-local baseline with the latent-MoE hybrid to expose the OOF/drift tradeoff.

| latent_weight | avg_log_loss | drift_vs_reference | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.000000 | 0.617748 | 0.076986 | 0.662785 | 0.687463 | 0.663960 | 0.564505 | 0.575859 | 0.525808 | 0.643854 |
| 0.150000 | 0.616567 | 0.079303 | 0.662785 | 0.682414 | 0.663220 | 0.563657 | 0.575522 | 0.524917 | 0.643456 |
| 0.250000 | 0.615858 | 0.080976 | 0.662785 | 0.679340 | 0.662792 | 0.563175 | 0.575322 | 0.524378 | 0.643213 |
| 0.350000 | 0.615209 | 0.082733 | 0.662785 | 0.676492 | 0.662416 | 0.562761 | 0.575141 | 0.523882 | 0.642989 |
| 0.500000 | 0.614350 | 0.085501 | 0.662785 | 0.672635 | 0.661951 | 0.562266 | 0.574903 | 0.523219 | 0.642687 |
| 0.650000 | 0.613624 | 0.088428 | 0.662785 | 0.669264 | 0.661604 | 0.561925 | 0.574706 | 0.522653 | 0.642429 |
| 0.800000 | 0.613031 | 0.091454 | 0.662785 | 0.666369 | 0.661379 | 0.561739 | 0.574546 | 0.522183 | 0.642215 |
| 1.000000 | 0.612448 | 0.095652 | 0.662785 | 0.663244 | 0.661269 | 0.561740 | 0.574392 | 0.521706 | 0.642003 |

## Decision

This is the first decoder that gates raw channel-patch expert latents before final probability formation. A positive target-specific result should feed the next Transformer decoder head; a negative result means expert disagreement is only useful after each expert has already been separately regularized.