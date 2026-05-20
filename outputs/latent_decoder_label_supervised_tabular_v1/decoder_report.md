# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.3_logreg_latent_meta_agg_C0.003_subject_prior_a10`
- Best CV average log-loss: 0.623734
- Target-wise CV average log-loss: 0.616355

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.3_logreg_latent_meta_agg_C0.003_subject_prior_a10 | blend | 0.623734 | 0.663172 | 0.697819 | 0.678042 | 0.573613 | 0.573250 | 0.539626 | 0.640617 |
| blend_w0.2_logreg_latent_meta_agg_C0.003_subject_prior_a10 | blend | 0.623793 | 0.665161 | 0.698248 | 0.676219 | 0.573342 | 0.574722 | 0.537477 | 0.641380 |
| blend_w0.2_logreg_latent_meta_agg_C0.01_subject_prior_a10 | blend | 0.623816 | 0.665197 | 0.695331 | 0.677695 | 0.574563 | 0.574926 | 0.538874 | 0.640126 |
| blend_w0.15_logreg_latent_meta_agg_C0.01_subject_prior_a10 | blend | 0.623876 | 0.666214 | 0.696237 | 0.676440 | 0.574135 | 0.575615 | 0.537532 | 0.640960 |
| blend_w0.15_logreg_latent_meta_agg_C0.03_subject_prior_a10 | blend | 0.623964 | 0.666708 | 0.693671 | 0.676712 | 0.576314 | 0.575642 | 0.539248 | 0.639457 |
| blend_w0.4_logreg_latent_meta_agg_C0.001_subject_prior_a5 | blend | 0.623987 | 0.663530 | 0.701361 | 0.677025 | 0.573954 | 0.572441 | 0.539167 | 0.640431 |
| blend_w0.3_logreg_latent_meta_agg_C0.001_subject_prior_a5 | blend | 0.623992 | 0.665106 | 0.702157 | 0.676749 | 0.573498 | 0.573307 | 0.536344 | 0.640782 |
| blend_w0.4_logreg_latent_meta_agg_C0.001_subject_prior_a2 | blend | 0.624101 | 0.663820 | 0.703691 | 0.678521 | 0.573709 | 0.571792 | 0.537108 | 0.640065 |
| blend_w0.3_logreg_latent_meta_agg_C0.001_subject_prior_a10 | blend | 0.624138 | 0.664824 | 0.698819 | 0.674547 | 0.574252 | 0.574750 | 0.540147 | 0.641627 |
| blend_w0.3_logreg_latent_meta_C0.003_subject_prior_a2 | blend | 0.624165 | 0.669965 | 0.699766 | 0.676123 | 0.575190 | 0.573903 | 0.534353 | 0.639853 |

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
| Q1 | blend_w0.5_logreg_latent_agg_C0.003_subject_prior_a20 | blend | 0.628200 | 0.661970 | 0.699355 | 0.681936 | 0.575735 | 0.577371 | 0.551549 | 0.649485 |
| Q2 | blend_w0.2_logreg_latent_meta_agg_C0.1_subject_prior_a100 | blend | 0.636031 | 0.673461 | 0.682306 | 0.672439 | 0.598303 | 0.594864 | 0.581478 | 0.649363 |
| Q3 | blend_w1_logreg_meta_only_C0.01_subject_prior_a10 | blend | 0.633993 | 0.675772 | 0.701137 | 0.664002 | 0.590386 | 0.595187 | 0.564176 | 0.647289 |
| S1 | blend_w0.3_logreg_latent_agg_C0.003_subject_prior_a5 | blend | 0.624984 | 0.663860 | 0.702826 | 0.679926 | 0.572026 | 0.575053 | 0.537219 | 0.643978 |
| S2 | blend_w0.5_logreg_latent_meta_agg_C0.001_subject_prior_a2 | blend | 0.624603 | 0.662731 | 0.703062 | 0.679228 | 0.574628 | 0.571377 | 0.540713 | 0.640484 |
| S3 | blend_w0.15_logreg_latent_C0.03_subject_prior_a2 | blend | 0.626333 | 0.671445 | 0.707727 | 0.679818 | 0.575317 | 0.574777 | 0.529445 | 0.645801 |
| S4 | blend_w0.4_logreg_latent_meta_C0.03_subject_prior_a5 | blend | 0.635445 | 0.683514 | 0.716459 | 0.699681 | 0.594325 | 0.579991 | 0.540785 | 0.633359 |

## Fold sizes

| fold | train_rows | valid_rows |
| --- | --- | --- |
| 1 | 355 | 95 |
| 2 | 358 | 92 |
| 3 | 359 | 91 |
| 4 | 363 | 87 |
| 5 | 365 | 85 |
