# Master Residual Decoder Report

- Base avg logloss: `0.581592`
- Final avg logloss: `0.581592`
- Target promotion rule: delta >= `2e-05` and improved folds >= `4/5`

## Selection

| target | log_loss | base_log_loss | delta_vs_base | candidate | spec | kind | feature_set | value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.633673 | 0.635456 | 0.001783 | blend_w0.1_logreg_rankdev_C0.1 | logreg_rankdev_C0.1 | logreg | rankdev | 0.100000 | 0.100000 | 3 | False |
| Q2 | 0.639724 | 0.639543 | -0.000182 | blend_w0.01_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.010000 | 2 | False |
| Q3 | 0.619849 | 0.621282 | 0.001434 | blend_w0.1_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.100000 | 3 | False |
| S1 | 0.552994 | 0.553868 | 0.000874 | blend_w0.08_logreg_rankdev_C0.03 | logreg_rankdev_C0.03 | logreg | rankdev | 0.030000 | 0.080000 | 3 | False |
| S2 | 0.529084 | 0.529019 | -0.000064 | blend_w0.01_logreg_nosubject_rankdev_C0.01 | logreg_nosubject_rankdev_C0.01 | logreg | nosubject_rankdev | 0.010000 | 0.010000 | 2 | False |
| S3 | 0.498643 | 0.498396 | -0.000247 | blend_w0.01_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.010000 | 2 | False |
| S4 | 0.593348 | 0.593582 | 0.000234 | blend_w0.03_logreg_rankdev_C0.1 | logreg_rankdev_C0.1 | logreg | rankdev | 0.100000 | 0.030000 | 3 | False |

## Top Candidates

| name | spec | kind | feature_set | value | blend_weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.01_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.010000 | 0.581661 | 0.635329 | 0.639724 | 0.621028 | 0.553824 | 0.529370 | 0.498689 | 0.593660 |
| blend_w0.01_logreg_latent_core_C0.1 | logreg_latent_core_C0.1 | logreg | latent_core | 0.100000 | 0.010000 | 0.581665 | 0.635278 | 0.639769 | 0.621215 | 0.553788 | 0.529333 | 0.498643 | 0.593630 |
| blend_w0.01_logreg_core_C0.03 | logreg_core_C0.03 | logreg | core | 0.030000 | 0.010000 | 0.581698 | 0.635342 | 0.639807 | 0.621105 | 0.553917 | 0.529343 | 0.498749 | 0.593622 |
| blend_w0.01_logreg_latent_core_C0.03 | logreg_latent_core_C0.03 | logreg | latent_core | 0.030000 | 0.010000 | 0.581712 | 0.635374 | 0.639866 | 0.621278 | 0.553926 | 0.529318 | 0.498671 | 0.593547 |
| blend_w0.01_logreg_nosubject_rankdev_C0.1 | logreg_nosubject_rankdev_C0.1 | logreg | nosubject_rankdev | 0.100000 | 0.010000 | 0.581712 | 0.635102 | 0.640491 | 0.621324 | 0.553651 | 0.529105 | 0.498853 | 0.593456 |
| blend_w0.01_logreg_rankdev_C0.1 | logreg_rankdev_C0.1 | logreg | rankdev | 0.100000 | 0.010000 | 0.581713 | 0.635102 | 0.640486 | 0.621332 | 0.553648 | 0.529115 | 0.498855 | 0.593452 |
| blend_w0.01_logreg_nosubject_rankdev_C0.03 | logreg_nosubject_rankdev_C0.03 | logreg | nosubject_rankdev | 0.030000 | 0.010000 | 0.581717 | 0.635192 | 0.640391 | 0.621363 | 0.553659 | 0.529101 | 0.498761 | 0.593554 |
| blend_w0.01_logreg_rankdev_C0.03 | logreg_rankdev_C0.03 | logreg | rankdev | 0.030000 | 0.010000 | 0.581717 | 0.635190 | 0.640386 | 0.621370 | 0.553657 | 0.529107 | 0.498761 | 0.593550 |
| blend_w0.01_logreg_rankdev_C0.01 | logreg_rankdev_C0.01 | logreg | rankdev | 0.010000 | 0.010000 | 0.581736 | 0.635309 | 0.640279 | 0.621358 | 0.553758 | 0.529086 | 0.498724 | 0.593637 |
| blend_w0.01_logreg_nosubject_rankdev_C0.01 | logreg_nosubject_rankdev_C0.01 | logreg | nosubject_rankdev | 0.010000 | 0.010000 | 0.581736 | 0.635310 | 0.640282 | 0.621353 | 0.553760 | 0.529084 | 0.498724 | 0.593640 |
| blend_w0.01_logreg_core_C0.01 | logreg_core_C0.01 | logreg | core | 0.010000 | 0.010000 | 0.581748 | 0.635409 | 0.639882 | 0.621233 | 0.554022 | 0.529299 | 0.498749 | 0.593641 |
| blend_w0.02_logreg_core_C0.1 | logreg_core_C0.1 | logreg | core | 0.100000 | 0.020000 | 0.581753 | 0.635229 | 0.639932 | 0.620799 | 0.553807 | 0.529742 | 0.499002 | 0.593761 |
