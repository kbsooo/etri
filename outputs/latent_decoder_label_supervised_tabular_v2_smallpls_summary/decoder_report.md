# Latent decoder report

- Metric: Average Log-Loss
- Train rows: 450
- Test rows: 250
- Best candidate: `blend_w0.2_logreg_latent_dev_C0.1_subject_prior_a5`
- Best CV average log-loss: 0.625073
- Target-wise CV average log-loss: 0.617887

## Top candidates

| name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.2_logreg_latent_dev_C0.1_subject_prior_a5 | blend | 0.625073 | 0.669152 | 0.693644 | 0.680098 | 0.577364 | 0.577322 | 0.533584 | 0.644348 |
| blend_w0.2_logreg_latent_dev_C0.3_subject_prior_a10 | blend | 0.625128 | 0.668617 | 0.690369 | 0.678744 | 0.578593 | 0.578089 | 0.537150 | 0.644336 |
| blend_w0.2_logreg_latent_dev_C1_subject_prior_a10 | blend | 0.625196 | 0.669520 | 0.691349 | 0.680014 | 0.577663 | 0.577572 | 0.536555 | 0.643702 |
| blend_w0.15_logreg_latent_dev_C0.3_subject_prior_a10 | blend | 0.625242 | 0.669282 | 0.692871 | 0.677842 | 0.577399 | 0.578240 | 0.536425 | 0.644637 |
| blend_w0.2_logreg_latent_dev_C0.3_subject_prior_a5 | blend | 0.625265 | 0.669697 | 0.693567 | 0.681367 | 0.577358 | 0.577622 | 0.533427 | 0.643813 |
| blend_w0.15_logreg_latent_dev_C1_subject_prior_a10 | blend | 0.625332 | 0.669915 | 0.693636 | 0.678771 | 0.576861 | 0.577892 | 0.536078 | 0.644166 |
| blend_w0.15_logreg_latent_dev_C0.1_subject_prior_a5 | blend | 0.625363 | 0.670150 | 0.696534 | 0.679737 | 0.576289 | 0.577510 | 0.532664 | 0.644660 |
| blend_w0.15_logreg_latent_C1_subject_prior_a5 | blend | 0.625444 | 0.673592 | 0.695918 | 0.680919 | 0.575398 | 0.574953 | 0.531932 | 0.645394 |
| blend_w0.2_logreg_latent_meta_agg_C0.003_subject_prior_a10 | blend | 0.625457 | 0.667913 | 0.700223 | 0.678750 | 0.572847 | 0.576621 | 0.539101 | 0.642747 |
| blend_w0.15_logreg_latent_dev_C0.1_subject_prior_a10 | blend | 0.625464 | 0.669218 | 0.693201 | 0.677089 | 0.577677 | 0.578678 | 0.537027 | 0.645358 |

## Feature set sizes

- latent: 14
- latent_dev: 28
- latent_meta: 43
- meta_only: 15
- agg: 1667
- latent_agg: 1681
- latent_meta_agg: 1710

## Target-wise selection

| target | name | kind | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | blend_w0.4_logreg_agg_C0.003_subject_prior_a20 | blend | 0.628415 | 0.666225 | 0.699105 | 0.681137 | 0.574741 | 0.580592 | 0.550274 | 0.646833 |
| Q2 | blend_w0.4_logreg_latent_dev_C1_subject_prior_a100 | blend | 0.635179 | 0.672976 | 0.680453 | 0.681065 | 0.598901 | 0.591158 | 0.567716 | 0.653985 |
| Q3 | blend_w1_logreg_meta_only_C0.01_subject_prior_a5 | blend | 0.633993 | 0.675772 | 0.701137 | 0.664002 | 0.590386 | 0.595187 | 0.564176 | 0.647289 |
| S1 | blend_w0.2_logreg_latent_agg_C0.01_subject_prior_a10 | blend | 0.626341 | 0.668251 | 0.698992 | 0.681718 | 0.572057 | 0.577525 | 0.541921 | 0.643925 |
| S2 | blend_w0.2_logreg_latent_C1_subject_prior_a2 | blend | 0.625710 | 0.674727 | 0.695618 | 0.683835 | 0.575726 | 0.574129 | 0.530637 | 0.645295 |
| S3 | blend_w0.15_logreg_latent_C0.1_subject_prior_a2 | blend | 0.625958 | 0.674060 | 0.699910 | 0.682081 | 0.574933 | 0.575232 | 0.529541 | 0.645948 |
| S4 | blend_w0.3_logreg_latent_meta_C1_subject_prior_a10 | blend | 0.627482 | 0.673726 | 0.696805 | 0.684402 | 0.578462 | 0.580284 | 0.539894 | 0.638803 |

## Fold sizes

| fold | train_rows | valid_rows |
| --- | --- | --- |
| 1 | 355 | 95 |
| 2 | 358 | 92 |
| 3 | 359 | 91 |
| 4 | 363 | 87 |
| 5 | 365 | 85 |
