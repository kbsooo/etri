# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.2_logreg_latent_meta_C0.03_subject_prior_a10`
- Best CV average log-loss: 0.624824
- Target-wise CV average log-loss: 0.615452

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.2_logreg_latent_meta_C0.03_subject_prior_a10 | blend | 0.624824 | 0.669012 | 0.708536 | 0.661675 | 0.574144 | 0.575771 | 0.537578 | 0.647052 |
| blend_w0.2_logreg_latent_meta_C0.01_subject_prior_a10 | blend | 0.625220 | 0.672949 | 0.701769 | 0.663661 | 0.575901 | 0.577307 | 0.537876 | 0.647079 |
| blend_w0.2_logreg_latent_meta_C0.1_subject_prior_a10 | blend | 0.625227 | 0.663811 | 0.715313 | 0.661941 | 0.573334 | 0.575167 | 0.539417 | 0.647610 |
| blend_w0.1_logreg_latent_meta_C0.1_subject_prior_a10 | blend | 0.625313 | 0.667165 | 0.707806 | 0.667968 | 0.573735 | 0.576724 | 0.537121 | 0.646673 |
| blend_w0.1_logreg_latent_meta_C0.3_subject_prior_a10 | blend | 0.625323 | 0.664989 | 0.709138 | 0.668123 | 0.573708 | 0.576588 | 0.538161 | 0.646556 |
| blend_w0.2_logreg_latent_dev_C0.03_subject_prior_a10 | blend | 0.625325 | 0.671527 | 0.705520 | 0.662598 | 0.575129 | 0.576016 | 0.537484 | 0.649002 |
| blend_w0.3_logreg_latent_meta_C0.01_subject_prior_a5 | blend | 0.625380 | 0.675004 | 0.706303 | 0.660430 | 0.575997 | 0.576261 | 0.535945 | 0.647722 |
| blend_w0.2_logreg_latent_C0.1_subject_prior_a10 | blend | 0.625383 | 0.677382 | 0.705426 | 0.666434 | 0.574488 | 0.573296 | 0.534180 | 0.646475 |
| blend_w0.2_logreg_latent_meta_agg_C0.01_subject_prior_a10 | blend | 0.625412 | 0.672995 | 0.703394 | 0.666739 | 0.575406 | 0.577244 | 0.538035 | 0.644076 |
| blend_w0.2_logreg_latent_meta_C0.01_subject_prior_a5 | blend | 0.625420 | 0.673749 | 0.705491 | 0.665890 | 0.575086 | 0.576546 | 0.534181 | 0.646997 |

## Feature set sizes

- latent: 96
- latent_dev: 192
- latent_meta: 207
- meta_only: 15
- agg: 320
- latent_agg: 416
- latent_meta_agg: 527

## Target-wise selection

| target | name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_w0.3_logreg_latent_meta_C0.3_subject_prior_a20 | blend | 0.629157 | 0.657762 | 0.727246 | 0.659626 | 0.577422 | 0.577784 | 0.552687 | 0.651572 |
| Q2 | blend_w0.5_logreg_latent_C0.003_subject_prior_a50 | blend | 0.640459 | 0.689578 | 0.688561 | 0.667991 | 0.597708 | 0.599343 | 0.577704 | 0.662325 |
| Q3 | blend_w0.5_logreg_latent_meta_C0.03_subject_prior_a100 | blend | 0.635616 | 0.677276 | 0.722891 | 0.648501 | 0.588817 | 0.588370 | 0.566512 | 0.656946 |
| S1 | blend_w0.1_logreg_latent_meta_agg_C0.3_subject_prior_a5 | blend | 0.626834 | 0.667183 | 0.713873 | 0.676327 | 0.572487 | 0.576482 | 0.539708 | 0.641776 |
| S2 | blend_w0.3_logreg_latent_C0.1_subject_prior_a5 | blend | 0.627033 | 0.683209 | 0.712962 | 0.665592 | 0.575513 | 0.571741 | 0.531999 | 0.648215 |
| S3 | blend_w0.2_logreg_latent_C0.1_subject_prior_a2 | blend | 0.627191 | 0.679846 | 0.712821 | 0.670653 | 0.574751 | 0.574330 | 0.529932 | 0.648005 |
| S4 | blend_w0.2_logreg_latent_agg_C0.3_subject_prior_a10 | blend | 0.630506 | 0.677045 | 0.722065 | 0.677132 | 0.578497 | 0.571816 | 0.547803 | 0.639183 |

## Fold sizes

| fold | train_rows | valid_rows |
| --- | --- | --- |
| 1 | 355 | 95 |
| 2 | 358 | 92 |
| 3 | 359 | 91 |
| 4 | 363 | 87 |
| 5 | 365 | 85 |
