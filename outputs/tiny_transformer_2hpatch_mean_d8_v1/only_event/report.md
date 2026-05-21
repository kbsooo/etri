# Hourly Transformer Encoder - only_event

## Representation

- Encoder type: `transformer`
- Encoder params: `4275`
- Days: `700`
- Token shape: `12 x 187`
- Raw tokens per day: `48`
- Pooling: `len=4`, stats=`mean`
- Base hourly features selected: `45`
- Mean token missing fraction: `0.000000`
- Device: `mps`
- SSL final loss: `0.305107`

## Probe Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| transformer_ridge_resid_a5_w0p2 | 0.627164 | 0.674266 | 0.700599 | 0.679317 | 0.574208 | 0.580711 | 0.535291 | 0.645755 |
| transformer_ridge_resid_a20_w0p2 | 0.627173 | 0.673985 | 0.701082 | 0.679043 | 0.574198 | 0.580822 | 0.534841 | 0.646239 |
| transformer_ridge_resid_a20_w0p35 | 0.627175 | 0.674812 | 0.699101 | 0.680242 | 0.573397 | 0.581722 | 0.535143 | 0.645806 |
| transformer_logreg_c0p3_w0p1 | 0.627194 | 0.672461 | 0.698658 | 0.676248 | 0.575772 | 0.581350 | 0.538679 | 0.647193 |
| transformer_logreg_c0p1_w0p1 | 0.627235 | 0.672373 | 0.698920 | 0.676116 | 0.576129 | 0.581329 | 0.538422 | 0.647354 |
| transformer_logreg_c0p3_w0p05 | 0.627252 | 0.672696 | 0.701644 | 0.676931 | 0.575548 | 0.580372 | 0.536498 | 0.647075 |
| transformer_ridge_resid_a1_w0p2 | 0.627255 | 0.674527 | 0.700450 | 0.679560 | 0.574740 | 0.580516 | 0.535614 | 0.645377 |
| transformer_logreg_c0p03_w0p1 | 0.627276 | 0.672218 | 0.699263 | 0.675959 | 0.576563 | 0.581169 | 0.538289 | 0.647471 |

## Target-Wise Selection

- Target-wise avg logloss: `0.623620`
- Drift vs reference: `0.068051`

| target | source | loss |
| --- | --- | --- |
| Q1 | transformer_logreg_c0p03_w0p2 | 0.672138 |
| Q2 | transformer_logreg_c0p3_w0p35 | 0.688509 |
| Q3 | transformer_logreg_c0p03_w0p35 | 0.673786 |
| S1 | transformer_ridge_resid_a20_w0p35 | 0.573397 |
| S2 | subject_prior_a8 | 0.579856 |
| S3 | subject_prior_a4 | 0.533031 |
| S4 | transformer_ridge_resid_a1_w0p35 | 0.644622 |

## Interpretation

This is a self-supervised sequence representation probe. It uses all 700 provided train/sample days without labels for masked-token reconstruction, then evaluates whether the resulting day embedding helps a fold-safe label probe over the 450 labeled rows.