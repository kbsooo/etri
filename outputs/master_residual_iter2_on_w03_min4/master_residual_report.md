# Master Residual Decoder Report

- Base avg logloss: `0.583798`
- Final avg logloss: `0.583610`
- Target promotion rule: delta >= `5e-05` and improved folds >= `4/5`

## Selection

| target | log_loss | base_log_loss | delta_vs_base | candidate | spec | kind | feature_set | value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.636189 | 0.637368 | 0.001179 | blend_w0.2_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.200000 | 4 | True |
| Q2 | 0.650609 | 0.650305 | -0.000304 | blend_w0.05_logreg_core_C0.3 | logreg_core_C0.3 | logreg | core | 0.300000 | 0.050000 | 2 | False |
| Q3 | 0.621086 | 0.622920 | 0.001834 | blend_w0.1_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.100000 | 3 | False |
| S1 | 0.553523 | 0.554273 | 0.000749 | blend_w0.05_logreg_latent_core_C0.3 | logreg_latent_core_C0.3 | logreg | latent_core | 0.300000 | 0.050000 | 3 | False |
| S2 | 0.529832 | 0.529220 | -0.000613 | blend_w0.05_logreg_base_only_C0.3 | logreg_base_only_C0.3 | logreg | base_only | 0.300000 | 0.050000 | 2 | False |
| S3 | 0.499525 | 0.498416 | -0.001109 | blend_w0.05_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.050000 | 1 | False |
| S4 | 0.593951 | 0.594084 | 0.000133 | blend_w0.05_logreg_latent_core_C0.01 | logreg_latent_core_C0.01 | logreg | latent_core | 0.010000 | 0.050000 | 4 | True |

## Top Candidates

| name | spec | kind | feature_set | value | blend_weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.05_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.050000 | 0.584066 | 0.636694 | 0.650686 | 0.621686 | 0.553952 | 0.530798 | 0.500052 | 0.594592 |
| blend_w0.05_logreg_core_C0.3 | logreg_core_C0.3 | logreg | core | 0.300000 | 0.050000 | 0.584111 | 0.636943 | 0.650609 | 0.622033 | 0.553929 | 0.530684 | 0.499753 | 0.594825 |
| blend_w0.05_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.050000 | 0.584181 | 0.636551 | 0.651170 | 0.622693 | 0.553816 | 0.530802 | 0.499799 | 0.594436 |
| blend_w0.05_logreg_latent_core_C0.3 | logreg_latent_core_C0.3 | logreg | latent_core | 0.300000 | 0.050000 | 0.584228 | 0.636372 | 0.651214 | 0.622987 | 0.553523 | 0.530649 | 0.499869 | 0.594981 |
| blend_w0.05_logreg_core_C0.03 | logreg_core_C0.03 | logreg | core | 0.030000 | 0.050000 | 0.584235 | 0.636748 | 0.651126 | 0.622039 | 0.554370 | 0.530711 | 0.500312 | 0.594341 |
| blend_w0.05_logreg_latent_core_C0.03 | logreg_latent_core_C0.03 | logreg | latent_core | 0.030000 | 0.050000 | 0.584381 | 0.636999 | 0.651647 | 0.622981 | 0.554474 | 0.530712 | 0.499891 | 0.593966 |
| blend_w0.05_logreg_core_C0.01 | logreg_core_C0.01 | logreg | core | 0.010000 | 0.050000 | 0.584503 | 0.637070 | 0.651532 | 0.622662 | 0.554901 | 0.530601 | 0.500343 | 0.594409 |
| blend_w0.05_logreg_latent_core_C0.01 | logreg_latent_core_C0.01 | logreg | latent_core | 0.010000 | 0.050000 | 0.584655 | 0.637468 | 0.652110 | 0.623538 | 0.555008 | 0.530572 | 0.499938 | 0.593951 |
| blend_w0.05_logreg_core_C0.003 | logreg_core_C0.003 | logreg | core | 0.003000 | 0.050000 | 0.584817 | 0.637540 | 0.651737 | 0.623253 | 0.555359 | 0.530665 | 0.500315 | 0.594846 |
| blend_w0.05_hgb_core_l215 | hgb_core_l215 | hgb | core | 15.000000 | 0.050000 | 0.584826 | 0.636822 | 0.652141 | 0.623647 | 0.555186 | 0.531025 | 0.499525 | 0.595436 |
| blend_w0.05_logreg_latent_core_C0.003 | logreg_latent_core_C0.003 | logreg | latent_core | 0.003000 | 0.050000 | 0.584912 | 0.637843 | 0.652295 | 0.623880 | 0.555321 | 0.530582 | 0.499974 | 0.594491 |
| blend_w0.1_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.100000 | 0.584926 | 0.636685 | 0.651733 | 0.621086 | 0.554255 | 0.532874 | 0.502183 | 0.595664 |
