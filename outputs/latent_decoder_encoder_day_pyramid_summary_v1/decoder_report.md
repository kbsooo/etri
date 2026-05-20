# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.3_logreg_latent_dev_C0.03_subject_prior_a10`
- Best CV average log-loss: 0.622389
- Target-wise CV average log-loss: 0.614797

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.3_logreg_latent_dev_C0.03_subject_prior_a10 | blend | 0.622389 | 0.664907 | 0.708592 | 0.665749 | 0.576664 | 0.572392 | 0.534327 | 0.634089 |
| blend_w0.3_logreg_latent_meta_C0.03_subject_prior_a20 | blend | 0.622524 | 0.662885 | 0.707117 | 0.663621 | 0.577015 | 0.573491 | 0.539241 | 0.634299 |
| blend_w0.3_logreg_latent_meta_C0.03_subject_prior_a10 | blend | 0.622541 | 0.663773 | 0.711885 | 0.666606 | 0.576170 | 0.571877 | 0.534252 | 0.633226 |
| blend_w0.4_logreg_latent_meta_C0.03_subject_prior_a20 | blend | 0.622648 | 0.662091 | 0.712988 | 0.662827 | 0.578141 | 0.572406 | 0.538542 | 0.631537 |
| blend_w0.4_logreg_latent_dev_C0.03_subject_prior_a10 | blend | 0.622723 | 0.664605 | 0.712936 | 0.664178 | 0.578408 | 0.572174 | 0.534800 | 0.631960 |
| blend_w0.3_logreg_latent_dev_C0.03_subject_prior_a20 | blend | 0.622736 | 0.664336 | 0.704245 | 0.662884 | 0.577873 | 0.574423 | 0.539884 | 0.635505 |
| blend_w0.4_logreg_latent_dev_C0.03_subject_prior_a20 | blend | 0.622800 | 0.663946 | 0.709007 | 0.661637 | 0.579181 | 0.573542 | 0.539252 | 0.633035 |
| blend_w0.4_logreg_latent_meta_C0.01_subject_prior_a10 | blend | 0.622842 | 0.663031 | 0.715102 | 0.662866 | 0.577882 | 0.571951 | 0.537072 | 0.631989 |
| blend_w0.3_logreg_latent_dev_C0.1_subject_prior_a20 | blend | 0.622843 | 0.666292 | 0.702561 | 0.665945 | 0.578418 | 0.573311 | 0.537615 | 0.635756 |
| blend_w0.2_logreg_latent_dev_C0.1_subject_prior_a10 | blend | 0.622993 | 0.667426 | 0.704058 | 0.670110 | 0.575930 | 0.572993 | 0.533065 | 0.637366 |

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
| Q1 | blend_w0.5_logreg_latent_meta_C0.01_subject_prior_a20 | blend | 0.623606 | 0.661935 | 0.716909 | 0.659252 | 0.580436 | 0.573232 | 0.542227 | 0.631248 |
| Q2 | blend_w0.15_logreg_agg_C0.03_subject_prior_a100 | blend | 0.639318 | 0.673911 | 0.689439 | 0.673011 | 0.592232 | 0.603611 | 0.583217 | 0.659804 |
| Q3 | blend_w1_logreg_latent_meta_C0.001_subject_prior_a50 | blend | 0.640441 | 0.669928 | 0.716400 | 0.652077 | 0.609728 | 0.597255 | 0.585915 | 0.651784 |
| S1 | blend_w0.2_logreg_agg_C0.01_subject_prior_a10 | blend | 0.626558 | 0.667405 | 0.699581 | 0.680777 | 0.572430 | 0.578810 | 0.541786 | 0.645119 |
| S2 | blend_w0.4_logreg_latent_C0.3_subject_prior_a10 | blend | 0.625455 | 0.678864 | 0.715282 | 0.668749 | 0.577222 | 0.570815 | 0.530466 | 0.636785 |
| S3 | blend_w0.3_logreg_latent_C0.3_subject_prior_a2 | blend | 0.626890 | 0.678794 | 0.717569 | 0.673862 | 0.577549 | 0.573658 | 0.528234 | 0.638565 |
| S4 | blend_w0.6_logreg_latent_meta_C0.01_subject_prior_a2 | blend | 0.625370 | 0.663777 | 0.730301 | 0.662936 | 0.581503 | 0.573230 | 0.537191 | 0.628650 |

## Fold sizes

| fold | train_rows | valid_rows |
| --- | --- | --- |
| 1 | 355 | 95 |
| 2 | 358 | 92 |
| 3 | 359 | 91 |
| 4 | 363 | 87 |
| 5 | 365 | 85 |
