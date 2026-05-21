# Hourly Transformer Encoder - only_rhythm

## Representation

- Days: `700`
- Token shape: `48 x 131`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `0.538083`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p3_w0p1 | 0.627194 | 0.672259 | 0.699429 | 0.675666 | 0.577185 | 0.580201 | 0.538186 | 0.647431 |
| transformer_logreg_c0p1_w0p1 | 0.627194 | 0.672217 | 0.699637 | 0.675645 | 0.576812 | 0.580267 | 0.538304 | 0.647476 |
| transformer_logreg_c0p3_w0p05 | 0.627251 | 0.672602 | 0.702064 | 0.676622 | 0.576241 | 0.579759 | 0.536260 | 0.647209 |
| transformer_logreg_c0p1_w0p05 | 0.627258 | 0.672581 | 0.702176 | 0.676620 | 0.576061 | 0.579805 | 0.536326 | 0.647238 |
| transformer_logreg_c0p03_w0p1 | 0.627279 | 0.672180 | 0.699915 | 0.675719 | 0.576653 | 0.580413 | 0.538547 | 0.647525 |
| transformer_logreg_c0p03_w0p05 | 0.627308 | 0.672562 | 0.702324 | 0.676667 | 0.575992 | 0.579892 | 0.536451 | 0.647268 |
| transformer_ridge_resid_a1_w0p05 | 0.627624 | 0.673395 | 0.704490 | 0.677426 | 0.576527 | 0.579694 | 0.534785 | 0.647047 |
| transformer_ridge_resid_a20_w0p05 | 0.627625 | 0.673269 | 0.704491 | 0.677470 | 0.576097 | 0.579905 | 0.534777 | 0.647368 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624341`
- Drift vs reference: `0.066469`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.672053 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.690263 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673194 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | transformer_ridge_resid_a1_w0p2 | 0.579532 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.646614 |

## Interpretation

This is a self-supervised Transformer representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.