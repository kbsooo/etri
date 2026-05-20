# Master Residual Decoder Report

- Base avg logloss: `0.584463`
- Final avg logloss: `0.583224`
- Target promotion rule: delta >= `5e-05` and improved folds >= `3/5`

## Selection

| target | log_loss | base_log_loss | delta_vs_base | candidate | spec | kind | feature_set | value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.636191 | 0.638349 | 0.002158 | blend_w0.2_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.200000 | 4 | True |
| Q2 | 0.650652 | 0.650305 | -0.000347 | blend_w0.05_logreg_core_C0.3 | logreg_core_C0.3 | logreg | core | 0.300000 | 0.050000 | 2 | False |
| Q3 | 0.620975 | 0.625491 | 0.004516 | blend_w0.2_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.200000 | 3 | True |
| S1 | 0.553503 | 0.555168 | 0.001665 | blend_w0.1_logreg_latent_core_C0.3 | logreg_latent_core_C0.3 | logreg | latent_core | 0.300000 | 0.100000 | 3 | True |
| S2 | 0.529862 | 0.529220 | -0.000642 | blend_w0.05_logreg_base_only_C0.3 | logreg_base_only_C0.3 | logreg | base_only | 0.300000 | 0.050000 | 2 | False |
| S3 | 0.499448 | 0.498416 | -0.001032 | blend_w0.05_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.050000 | 1 | False |
| S4 | 0.593962 | 0.594295 | 0.000333 | blend_w0.1_logreg_latent_core_C0.01 | logreg_latent_core_C0.01 | logreg | latent_core | 0.010000 | 0.100000 | 4 | True |

## Top Candidates

| name | spec | kind | feature_set | value | blend_weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.05_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.050000 | 0.584480 | 0.637481 | 0.650727 | 0.623275 | 0.554425 | 0.530822 | 0.500048 | 0.594580 |
| blend_w0.05_logreg_core_C0.3 | logreg_core_C0.3 | logreg | core | 0.300000 | 0.050000 | 0.584494 | 0.637744 | 0.650652 | 0.623531 | 0.554293 | 0.530720 | 0.499736 | 0.594782 |
| blend_w0.05_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.050000 | 0.584602 | 0.637391 | 0.651219 | 0.624284 | 0.554281 | 0.530819 | 0.499808 | 0.594414 |
| blend_w0.05_logreg_latent_core_C0.3 | logreg_latent_core_C0.3 | logreg | latent_core | 0.300000 | 0.050000 | 0.584619 | 0.637243 | 0.651258 | 0.624482 | 0.553869 | 0.530678 | 0.499873 | 0.594928 |
| blend_w0.05_logreg_core_C0.03 | logreg_core_C0.03 | logreg | core | 0.030000 | 0.050000 | 0.584698 | 0.637529 | 0.651159 | 0.623804 | 0.554978 | 0.530731 | 0.500318 | 0.594366 |
| blend_w0.05_logreg_latent_core_C0.03 | logreg_latent_core_C0.03 | logreg | latent_core | 0.030000 | 0.050000 | 0.584851 | 0.637824 | 0.651686 | 0.624747 | 0.555091 | 0.530727 | 0.499902 | 0.593978 |
| blend_w0.05_logreg_core_C0.01 | logreg_core_C0.01 | logreg | core | 0.010000 | 0.050000 | 0.585009 | 0.637852 | 0.651555 | 0.624606 | 0.555610 | 0.530622 | 0.500350 | 0.594466 |
| blend_w0.1_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.100000 | 0.585119 | 0.637301 | 0.651814 | 0.621793 | 0.554376 | 0.532921 | 0.502174 | 0.595453 |
| blend_w0.05_logreg_latent_core_C0.01 | logreg_latent_core_C0.01 | logreg | latent_core | 0.010000 | 0.050000 | 0.585166 | 0.638290 | 0.652134 | 0.625487 | 0.555726 | 0.530584 | 0.499944 | 0.593996 |
| blend_w0.1_logreg_core_C0.03 | logreg_core_C0.03 | logreg | core | 0.030000 | 0.100000 | 0.585353 | 0.637144 | 0.652442 | 0.622636 | 0.555184 | 0.532580 | 0.502640 | 0.594845 |
| blend_w0.05_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.050000 | 0.585357 | 0.637511 | 0.652202 | 0.625860 | 0.555937 | 0.531083 | 0.499448 | 0.595460 |
| blend_w0.1_logreg_core_C0.3 | logreg_core_C0.3 | logreg | core | 0.300000 | 0.100000 | 0.585358 | 0.638053 | 0.651886 | 0.622491 | 0.554395 | 0.532922 | 0.501672 | 0.596084 |
