# Master Residual Decoder Report

- Base avg logloss: `0.573015`
- Final avg logloss: `0.572535`
- Target promotion rule: delta >= `1e-05` and improved folds >= `3/5`

## Selection

| target | log_loss | base_log_loss | delta_vs_base | candidate | spec | kind | feature_set | value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.629802 | 0.632767 | 0.002965 | blend_w0.1_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.100000 | 4 | True |
| Q2 | 0.632301 | 0.631432 | -0.000869 | blend_w0.03_logreg_latent_core_C0.01 | logreg_latent_core_C0.01 | logreg | latent_core | 0.010000 | 0.030000 | 1 | False |
| Q3 | 0.597426 | 0.597823 | 0.000397 | blend_w0.05_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.050000 | 4 | True |
| S1 | 0.547403 | 0.547464 | 0.000061 | blend_w0.03_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.030000 | 2 | False |
| S2 | 0.522368 | 0.522044 | -0.000324 | blend_w0.03_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.030000 | 2 | False |
| S3 | 0.494218 | 0.493610 | -0.000608 | blend_w0.03_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.030000 | 2 | False |
| S4 | 0.586374 | 0.585965 | -0.000409 | blend_w0.03_logreg_core_C0.01 | logreg_core_C0.01 | logreg | core | 0.010000 | 0.030000 | 2 | False |

## Top Candidates

| name | spec | kind | feature_set | value | blend_weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.03_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.030000 | 0.573300 | 0.631518 | 0.632630 | 0.597479 | 0.547403 | 0.522368 | 0.494656 | 0.587044 |
| blend_w0.03_logreg_latent_core_C0.03 | logreg_latent_core_C0.03 | logreg | latent_core | 0.030000 | 0.030000 | 0.573448 | 0.632220 | 0.632372 | 0.597814 | 0.547836 | 0.522476 | 0.494664 | 0.586754 |
| blend_w0.03_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.030000 | 0.573505 | 0.632393 | 0.632390 | 0.597546 | 0.547933 | 0.523095 | 0.494544 | 0.586632 |
| blend_w0.03_logreg_core_C0.03 | logreg_core_C0.03 | logreg | core | 0.030000 | 0.030000 | 0.573614 | 0.632468 | 0.632495 | 0.597868 | 0.548138 | 0.523173 | 0.494769 | 0.586387 |
| blend_w0.03_logreg_latent_core_C0.01 | logreg_latent_core_C0.01 | logreg | latent_core | 0.010000 | 0.030000 | 0.573651 | 0.632824 | 0.632301 | 0.598303 | 0.548206 | 0.522649 | 0.494637 | 0.586637 |
| blend_w0.05_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.050000 | 0.573662 | 0.630858 | 0.633579 | 0.597426 | 0.547544 | 0.522727 | 0.495593 | 0.587908 |
| blend_w0.03_logreg_core_C0.01 | logreg_core_C0.01 | logreg | core | 0.010000 | 0.030000 | 0.573767 | 0.632700 | 0.632620 | 0.598281 | 0.548384 | 0.523144 | 0.494869 | 0.586374 |
| blend_w0.03_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.030000 | 0.573841 | 0.632643 | 0.632913 | 0.598849 | 0.548362 | 0.523128 | 0.494218 | 0.586774 |
| blend_w0.05_logreg_latent_core_C0.03 | logreg_latent_core_C0.03 | logreg | latent_core | 0.030000 | 0.050000 | 0.573846 | 0.631960 | 0.633098 | 0.597921 | 0.548194 | 0.522853 | 0.495518 | 0.587376 |
| blend_w0.03_logreg_latent_core_C0.003 | logreg_latent_core_C0.003 | logreg | latent_core | 0.003000 | 0.030000 | 0.573864 | 0.633232 | 0.632400 | 0.598701 | 0.548436 | 0.522884 | 0.494630 | 0.586762 |
| blend_w0.03_hgb_latent_core_l215 | hgb_latent_core_l215 | hgb | latent_core | 15.000000 | 0.030000 | 0.573899 | 0.632560 | 0.633018 | 0.598936 | 0.548463 | 0.522827 | 0.494527 | 0.586961 |
| blend_w0.03_logreg_core_C0.003 | logreg_core_C0.003 | logreg | core | 0.003000 | 0.030000 | 0.573932 | 0.633005 | 0.632708 | 0.598645 | 0.548519 | 0.523128 | 0.494881 | 0.586635 |
