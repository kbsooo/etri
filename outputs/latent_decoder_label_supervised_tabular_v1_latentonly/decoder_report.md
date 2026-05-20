# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.3_logreg_latent_meta_C0.003_subject_prior_a2`
- Best CV average log-loss: 0.624165
- Target-wise CV average log-loss: 0.618805

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.3_logreg_latent_meta_C0.003_subject_prior_a2 | blend | 0.624165 | 0.669965 | 0.699766 | 0.676123 | 0.575190 | 0.573903 | 0.534353 | 0.639853 |
| blend_w0.3_logreg_latent_dev_C0.003_subject_prior_a2 | blend | 0.624518 | 0.669745 | 0.697957 | 0.676854 | 0.574978 | 0.574191 | 0.535927 | 0.641974 |
| blend_w0.2_logreg_latent_dev_C0.003_subject_prior_a2 | blend | 0.624595 | 0.670101 | 0.701246 | 0.677554 | 0.573875 | 0.574605 | 0.532444 | 0.642342 |
| blend_w0.2_logreg_latent_meta_C0.003_subject_prior_a5 | blend | 0.624657 | 0.670229 | 0.700050 | 0.675515 | 0.574888 | 0.575455 | 0.534528 | 0.641931 |
| blend_w0.3_logreg_latent_meta_C0.003_subject_prior_a5 | blend | 0.624666 | 0.670147 | 0.697848 | 0.674883 | 0.576214 | 0.575221 | 0.537410 | 0.640935 |
| blend_w0.2_logreg_latent_meta_C0.003_subject_prior_a2 | blend | 0.624740 | 0.670658 | 0.702762 | 0.677263 | 0.574401 | 0.574805 | 0.531940 | 0.641351 |
| blend_w0.2_logreg_latent_dev_C0.003_subject_prior_a5 | blend | 0.624766 | 0.669921 | 0.698737 | 0.675920 | 0.574609 | 0.575556 | 0.535400 | 0.643215 |
| blend_w0.2_logreg_latent_dev_C0.01_subject_prior_a5 | blend | 0.624876 | 0.670446 | 0.699519 | 0.679961 | 0.575392 | 0.573873 | 0.533912 | 0.641034 |
| blend_w0.3_logreg_latent_C0.003_subject_prior_a2 | blend | 0.624945 | 0.668211 | 0.699995 | 0.673713 | 0.573937 | 0.576129 | 0.535540 | 0.647091 |
| blend_w0.2_logreg_latent_C0.01_subject_prior_a5 | blend | 0.624956 | 0.669026 | 0.701666 | 0.675479 | 0.573722 | 0.574977 | 0.533135 | 0.646688 |

## Feature set sizes

- latent: 128
- latent_dev: 256
- latent_meta: 271
- meta_only: 15

## Target-wise selection

| target | name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_w0.3_logreg_latent_C0.003_subject_prior_a2 | blend | 0.624945 | 0.668211 | 0.699995 | 0.673713 | 0.573937 | 0.576129 | 0.535540 | 0.647091 |
| Q2 | blend_w0.15_logreg_latent_dev_C0.01_subject_prior_a50 | blend | 0.635564 | 0.676736 | 0.691100 | 0.672910 | 0.590055 | 0.594586 | 0.568222 | 0.655343 |
| Q3 | blend_w1_logreg_meta_only_C0.01_subject_prior_a100 | blend | 0.633993 | 0.675772 | 0.701137 | 0.664002 | 0.590386 | 0.595187 | 0.564176 | 0.647289 |
| S1 | blend_w0.2_logreg_latent_C0.01_subject_prior_a2 | blend | 0.625055 | 0.669369 | 0.704420 | 0.677194 | 0.573219 | 0.574465 | 0.530504 | 0.646218 |
| S2 | blend_w0.3_logreg_latent_dev_C0.01_subject_prior_a2 | blend | 0.625503 | 0.671422 | 0.700470 | 0.684027 | 0.576754 | 0.572298 | 0.534078 | 0.639474 |
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
