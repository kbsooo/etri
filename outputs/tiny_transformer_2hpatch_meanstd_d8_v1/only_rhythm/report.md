# Hourly Transformer Encoder - only_rhythm

## Representation

- Encoder type: `transformer`
- Encoder params: `5550`
- Days: `700`
- Token shape: `12 x 262`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean_std`
- Base hourly features selected: `31`
- Mean token missing fraction: `0.174404`
- Device: `mps`
- SSL final loss: `0.264092`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_logreg_c0p03_w0p05 | 0.627491 | 0.672935 | 0.702458 | 0.676870 | 0.576129 | 0.580081 | 0.536571 | 0.647397 |
| transformer_logreg_c0p1_w0p05 | 0.627539 | 0.673003 | 0.702420 | 0.676959 | 0.576322 | 0.580089 | 0.536527 | 0.647452 |
| transformer_logreg_c0p3_w0p05 | 0.627557 | 0.672965 | 0.702406 | 0.677034 | 0.576459 | 0.580115 | 0.536425 | 0.647492 |
| transformer_logreg_c0p03_w0p1 | 0.627646 | 0.672932 | 0.700188 | 0.676118 | 0.576893 | 0.580795 | 0.538819 | 0.647780 |
| subject_prior_a8 | 0.627654 | 0.673179 | 0.705010 | 0.677770 | 0.575702 | 0.579856 | 0.534788 | 0.647272 |
| transformer_logreg_c0p1_w0p1 | 0.627747 | 0.673066 | 0.700127 | 0.676301 | 0.577280 | 0.580821 | 0.538739 | 0.647895 |
| transformer_logreg_c0p3_w0p1 | 0.627788 | 0.672988 | 0.700106 | 0.676455 | 0.577555 | 0.580881 | 0.538549 | 0.647981 |
| subject_prior_a16 | 0.627839 | 0.672177 | 0.699188 | 0.673823 | 0.577202 | 0.582206 | 0.541687 | 0.648586 |

## Target-Wise Selection

- Target-wise avg logloss: `0.624916`
- Drift vs reference: `0.063950`

| target | source | loss |
| --- | --- | --- |
| Q1 | subject_prior_a16 | 0.672177 |
| Q2 | transformer_logreg_c0p03_w0p35 | 0.692548 |
| Q3 | subject_prior_a16 | 0.673823 |
| S1 | subject_prior_a8 | 0.575702 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | subject_prior_a8 | 0.647272 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.