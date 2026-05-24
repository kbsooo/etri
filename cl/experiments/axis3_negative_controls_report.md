# Axis 3 — Negative controls

Each model is scored on real labels (C0) and on multiple null controls.
If a control's logloss is close to C0_real, the model's apparent skill
is not day-varying signal — it is captured by subject or static context.


## Model: subj_tokens

| control_group | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | Tavg |
|---|---|---|---|---|---|---|---|---|
| C0_real | 0.7307 | 0.7688 | 0.7538 | 0.5860 | 0.5943 | 0.5945 | 0.6303 | 0.6655 |
| C1_within_subj_perm | 0.7238 | 0.7801 | 0.7637 | 0.5912 | 0.6023 | 0.5974 | 0.6364 | 0.6707 |
| C2_date_shifted_feats | 0.7291 | 0.7676 | 0.7616 | 0.5866 | 0.5892 | 0.5941 | 0.6394 | 0.6668 |
| C5_fake_target | 0.7313 | 0.8081 | 0.8143 | 0.6304 | 0.6373 | 0.6314 | 0.6541 | 0.7010 |

## Model: subj_cov

| control_group | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | Tavg |
|---|---|---|---|---|---|---|---|---|
| C0_real | 0.7652 | 0.7493 | 0.7579 | 0.6090 | 0.5988 | 0.6025 | 0.6518 | 0.6764 |
| C1_within_subj_perm | 0.7324 | 0.7816 | 0.7665 | 0.5990 | 0.6054 | 0.5994 | 0.6460 | 0.6758 |
| C2_date_shifted_feats | 0.7661 | 0.7610 | 0.7711 | 0.6035 | 0.5975 | 0.6021 | 0.6448 | 0.6780 |
| C5_fake_target | 0.7425 | 0.7891 | 0.8271 | 0.6243 | 0.6285 | 0.6033 | 0.6621 | 0.6967 |

## Global controls (no token / no cov mixed)

| model | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | Tavg |
|---|---|---|---|---|---|---|---|---|
| coverage_only | 0.7286 | 0.7239 | 0.6745 | 0.6359 | 0.6725 | 0.6912 | 0.6870 | 0.6877 |
| subject_only | 0.7119 | 0.7660 | 0.7515 | 0.5851 | 0.5894 | 0.5798 | 0.6275 | 0.6587 |

## Gap: C0_real − C1_within_subject_perm (negative = real model worse than perm)

If close to 0, model has no day-level signal beyond subject prevalence.

|  | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|
| subj_tokens: real − perm | 0.0069 | -0.0113 | -0.0099 | -0.0052 | -0.0080 | -0.0029 | -0.0061 |
|  | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|---|---|
| subj_cov: real − perm | 0.0328 | -0.0323 | -0.0086 | 0.0100 | -0.0066 | 0.0031 | 0.0058 |