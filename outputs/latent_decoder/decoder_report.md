# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.4_logreg_latent_C0.1_subject_prior_a20`
- Best CV average log-loss: 0.625902
- Target-wise CV average log-loss: 0.616835

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.4_logreg_latent_C0.1_subject_prior_a20 | blend | 0.625902 | 0.660366 | 0.704872 | 0.677158 | 0.571838 | 0.582745 | 0.538683 | 0.645653 |
| blend_w0.5_logreg_latent_C0.1_subject_prior_a20 | blend | 0.626047 | 0.658369 | 0.707428 | 0.679028 | 0.570938 | 0.583301 | 0.537800 | 0.645467 |
| blend_w0.1_logreg_latent_meta_C1_subject_prior_a10 | blend | 0.626063 | 0.663496 | 0.704805 | 0.673497 | 0.574728 | 0.581614 | 0.537553 | 0.646745 |
| blend_w0.1_logreg_latent_meta_C3_subject_prior_a10 | blend | 0.626081 | 0.663256 | 0.704786 | 0.673563 | 0.575293 | 0.581455 | 0.537424 | 0.646788 |
| blend_w0.3_logreg_latent_C0.1_subject_prior_a20 | blend | 0.626101 | 0.662771 | 0.702610 | 0.675591 | 0.573063 | 0.582576 | 0.539914 | 0.646183 |
| blend_w0.1_logreg_latent_meta_C0.3_subject_prior_a10 | blend | 0.626137 | 0.664145 | 0.705103 | 0.674047 | 0.574079 | 0.581501 | 0.537514 | 0.646569 |
| blend_w0.3_logreg_latent_C0.3_subject_prior_a20 | blend | 0.626206 | 0.660445 | 0.703017 | 0.675999 | 0.571740 | 0.584314 | 0.541605 | 0.646323 |
| blend_w0.6_logreg_latent_C0.1_subject_prior_a50 | blend | 0.626275 | 0.655931 | 0.705885 | 0.678013 | 0.571179 | 0.585419 | 0.541539 | 0.645962 |
| blend_w0.1_logreg_latent_meta_C0.1_subject_prior_a10 | blend | 0.626323 | 0.665088 | 0.705521 | 0.674982 | 0.573708 | 0.581212 | 0.537379 | 0.646374 |
| blend_w0.3_logreg_latent_C0.1_subject_prior_a10 | blend | 0.626409 | 0.663766 | 0.707483 | 0.678978 | 0.572311 | 0.581396 | 0.535299 | 0.645632 |

## Feature set sizes

- latent: 64
- latent_dev: 128
- latent_meta: 143
- meta_only: 15
- agg: 320
- latent_agg: 384
- latent_meta_agg: 463

## Target-wise selection

| target | name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_w0.6_logreg_latent_meta_C0.1_subject_prior_a100 | blend | 0.638276 | 0.647975 | 0.726443 | 0.680027 | 0.582122 | 0.603329 | 0.564208 | 0.663827 |
| Q2 | blend_w0.1_logreg_latent_C3_subject_prior_a100 | blend | 0.640149 | 0.674045 | 0.692051 | 0.667770 | 0.593723 | 0.608214 | 0.582951 | 0.662288 |
| Q3 | blend_w0.2_logreg_latent_meta_C1_subject_prior_a100 | blend | 0.636234 | 0.660740 | 0.696784 | 0.664758 | 0.590929 | 0.604994 | 0.576352 | 0.659079 |
| S1 | blend_w0.6_logreg_latent_C0.3_subject_prior_a20 | blend | 0.628846 | 0.654680 | 0.713659 | 0.683735 | 0.569479 | 0.589817 | 0.541981 | 0.648572 |
| S2 | blend_w0.2_logreg_agg_C3_subject_prior_a5 | blend | 0.635079 | 0.689270 | 0.731737 | 0.687237 | 0.576072 | 0.571491 | 0.544257 | 0.645489 |
| S3 | blend_w0.1_logreg_agg_C0.03_subject_prior_a2 | blend | 0.630437 | 0.678922 | 0.716515 | 0.682854 | 0.576586 | 0.580696 | 0.531800 | 0.645684 |
| S4 | blend_w0.8_logreg_meta_only_C0.03_subject_prior_a2 | blend | 0.628441 | 0.675465 | 0.711541 | 0.670255 | 0.580370 | 0.581099 | 0.540063 | 0.640292 |

## Fold sizes

| fold | train_rows | valid_rows |
| --- | --- | --- |
| 1 | 355 | 95 |
| 2 | 358 | 92 |
| 3 | 359 | 91 |
| 4 | 363 | 87 |
| 5 | 365 | 85 |
