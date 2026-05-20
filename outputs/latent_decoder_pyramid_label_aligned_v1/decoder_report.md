# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.2_logreg_agg_C0.003_subject_prior_a10`
- Best CV average log-loss: 0.625700
- Target-wise CV average log-loss: 0.619118

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.2_logreg_agg_C0.003_subject_prior_a10 | blend | 0.625700 | 0.667554 | 0.700618 | 0.677906 | 0.572888 | 0.577844 | 0.539107 | 0.643985 |
| blend_w0.15_logreg_agg_C0.003_subject_prior_a10 | blend | 0.625755 | 0.668458 | 0.700821 | 0.677150 | 0.573307 | 0.578108 | 0.538095 | 0.644343 |
| blend_w0.2_logreg_agg_C0.001_subject_prior_a10 | blend | 0.625849 | 0.668470 | 0.701039 | 0.675525 | 0.574574 | 0.578111 | 0.539101 | 0.644121 |
| blend_w0.3_logreg_agg_C0.001_subject_prior_a5 | blend | 0.625858 | 0.667668 | 0.704080 | 0.678128 | 0.573968 | 0.576601 | 0.537685 | 0.642873 |
| blend_w0.3_logreg_agg_C0.001_subject_prior_a10 | blend | 0.625958 | 0.667301 | 0.700860 | 0.675875 | 0.574662 | 0.577890 | 0.541456 | 0.643662 |
| blend_w0.15_logreg_agg_C0.001_subject_prior_a10 | blend | 0.626011 | 0.669281 | 0.701344 | 0.675564 | 0.574703 | 0.578408 | 0.538141 | 0.644638 |
| blend_w0.1_logreg_agg_C0.01_subject_prior_a10 | blend | 0.626050 | 0.669134 | 0.700231 | 0.677567 | 0.573302 | 0.578687 | 0.538312 | 0.645121 |
| blend_w0.1_logreg_agg_C0.003_subject_prior_a10 | blend | 0.626056 | 0.669608 | 0.701306 | 0.676670 | 0.573931 | 0.578567 | 0.537283 | 0.645026 |
| blend_w0.2_logreg_agg_C0.001_subject_prior_a5 | blend | 0.626064 | 0.669214 | 0.704930 | 0.678189 | 0.574087 | 0.577181 | 0.535290 | 0.643555 |
| blend_w0.15_logreg_agg_C0.01_subject_prior_a10 | blend | 0.626072 | 0.668047 | 0.699631 | 0.678898 | 0.572663 | 0.578558 | 0.539865 | 0.644839 |

## Feature set sizes

- latent: 128
- latent_dev: 256
- latent_meta: 271
- meta_only: 15
- agg: 1667
- latent_agg: 1795
- latent_meta_agg: 1938

## Target-wise selection

| target | name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_w0.4_logreg_agg_C0.003_subject_prior_a20 | blend | 0.628415 | 0.666225 | 0.699105 | 0.681137 | 0.574741 | 0.580592 | 0.550274 | 0.646833 |
| Q2 | blend_w0.15_logreg_latent_meta_agg_C0.3_subject_prior_a100 | blend | 0.641965 | 0.681494 | 0.687078 | 0.680517 | 0.593488 | 0.602568 | 0.586105 | 0.662502 |
| Q3 | blend_w1_logreg_meta_only_C0.01_subject_prior_a100 | blend | 0.634043 | 0.676257 | 0.701528 | 0.663971 | 0.590444 | 0.594975 | 0.564056 | 0.647069 |
| S1 | blend_w0.2_logreg_agg_C0.01_subject_prior_a10 | blend | 0.626558 | 0.667405 | 0.699581 | 0.680777 | 0.572430 | 0.578810 | 0.541786 | 0.645119 |
| S2 | blend_w0.2_logreg_latent_C1_subject_prior_a5 | blend | 0.633305 | 0.685458 | 0.721960 | 0.681824 | 0.588036 | 0.573019 | 0.544330 | 0.638509 |
| S3 | blend_w0.1_logreg_agg_C0.001_subject_prior_a2 | blend | 0.628518 | 0.673299 | 0.710585 | 0.681514 | 0.575772 | 0.579902 | 0.532651 | 0.645902 |
| S4 | blend_w0.3_logreg_latent_C0.3_subject_prior_a5 | blend | 0.638092 | 0.692533 | 0.732617 | 0.685401 | 0.590736 | 0.578350 | 0.548554 | 0.638454 |

## Fold sizes

| fold | train_rows | valid_rows |
| --- | --- | --- |
| 1 | 355 | 95 |
| 2 | 358 | 92 |
| 3 | 359 | 91 |
| 4 | 363 | 87 |
| 5 | 365 | 85 |
