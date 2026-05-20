# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.2_logreg_latent_meta_agg_C0.03_subject_prior_a10`
- Best CV average log-loss: 0.622180
- Target-wise CV average log-loss: 0.613964

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.2_logreg_latent_meta_agg_C0.03_subject_prior_a10 | blend | 0.622180 | 0.662353 | 0.697883 | 0.667328 | 0.572471 | 0.575492 | 0.540429 | 0.639302 |
| blend_w0.3_logreg_latent_dev_C0.03_subject_prior_a10 | blend | 0.622389 | 0.664907 | 0.708592 | 0.665749 | 0.576664 | 0.572392 | 0.534327 | 0.634089 |
| blend_w0.3_logreg_latent_meta_C0.03_subject_prior_a20 | blend | 0.622524 | 0.662885 | 0.707117 | 0.663621 | 0.577015 | 0.573491 | 0.539241 | 0.634299 |
| blend_w0.2_logreg_latent_meta_agg_C0.03_subject_prior_a20 | blend | 0.622537 | 0.661643 | 0.693135 | 0.664029 | 0.573952 | 0.577853 | 0.546294 | 0.640856 |
| blend_w0.3_logreg_latent_meta_C0.03_subject_prior_a10 | blend | 0.622541 | 0.663773 | 0.711885 | 0.666606 | 0.576170 | 0.571877 | 0.534252 | 0.633226 |
| blend_w0.4_logreg_latent_meta_C0.03_subject_prior_a20 | blend | 0.622648 | 0.662091 | 0.712988 | 0.662827 | 0.578141 | 0.572406 | 0.538542 | 0.631537 |
| blend_w0.4_logreg_latent_dev_C0.03_subject_prior_a10 | blend | 0.622723 | 0.664605 | 0.712936 | 0.664178 | 0.578408 | 0.572174 | 0.534800 | 0.631960 |
| blend_w0.3_logreg_latent_dev_C0.03_subject_prior_a20 | blend | 0.622736 | 0.664336 | 0.704245 | 0.662884 | 0.577873 | 0.574423 | 0.539884 | 0.635505 |
| blend_w0.4_logreg_latent_dev_C0.03_subject_prior_a20 | blend | 0.622800 | 0.663946 | 0.709007 | 0.661637 | 0.579181 | 0.573542 | 0.539252 | 0.633035 |
| blend_w0.3_logreg_latent_dev_C0.1_subject_prior_a20 | blend | 0.622843 | 0.666292 | 0.702561 | 0.665945 | 0.578418 | 0.573311 | 0.537615 | 0.635756 |

## Feature set sizes

- latent: 128
- latent_dev: 256
- latent_meta: 271
- meta_only: 15
- agg: 218
- latent_agg: 346
- latent_meta_agg: 489

## Target-wise selection

| target | name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_w0.3_logreg_latent_meta_agg_C0.03_subject_prior_a20 | blend | 0.622985 | 0.659996 | 0.695084 | 0.663830 | 0.574495 | 0.577905 | 0.549148 | 0.640434 |
| Q2 | blend_w0.2_logreg_latent_agg_C0.3_subject_prior_a100 | blend | 0.635759 | 0.670573 | 0.684449 | 0.666087 | 0.586590 | 0.599179 | 0.583381 | 0.660054 |
| Q3 | blend_w0.6_logreg_latent_C0.03_subject_prior_a100 | blend | 0.630664 | 0.676373 | 0.715127 | 0.655825 | 0.590406 | 0.581089 | 0.557230 | 0.638594 |
| S1 | blend_w0.2_logreg_latent_meta_agg_C0.1_subject_prior_a10 | blend | 0.623035 | 0.662253 | 0.696002 | 0.670830 | 0.570941 | 0.576225 | 0.544307 | 0.640688 |
| S2 | blend_w0.3_logreg_latent_C3_subject_prior_a10 | blend | 0.628155 | 0.682138 | 0.711581 | 0.678019 | 0.581270 | 0.568598 | 0.531467 | 0.644015 |
| S3 | blend_w0.3_logreg_latent_C0.3_subject_prior_a2 | blend | 0.626890 | 0.678794 | 0.717569 | 0.673862 | 0.577549 | 0.573658 | 0.528234 | 0.638565 |
| S4 | blend_w0.5_logreg_latent_meta_C0.03_subject_prior_a10 | blend | 0.624585 | 0.663716 | 0.724406 | 0.665531 | 0.580308 | 0.572546 | 0.535885 | 0.629703 |

## Fold sizes

| fold | train_rows | valid_rows |
| --- | --- | --- |
| 1 | 355 | 95 |
| 2 | 358 | 92 |
| 3 | 359 | 91 |
| 4 | 363 | 87 |
| 5 | 365 | 85 |
