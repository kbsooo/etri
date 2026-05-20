# Master Residual Decoder Report

- Base avg logloss: `0.583798`
- Final avg logloss: `0.583798`
- Target promotion rule: delta >= `5e-05` and improved folds >= `4/5`

## Selection

| target | log_loss | base_log_loss | delta_vs_base | candidate | spec | kind | feature_set | value | blend_weight | folds_improved | used |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | 0.634829 | 0.637368 | 0.002539 | blend_w0.1_logreg_all_C0.03 | logreg_all_C0.03 | logreg | all | 0.030000 | 0.100000 | 3 | False |
| Q2 | 0.652626 | 0.650305 | -0.002321 | blend_w0.05_hgb_rankdev_l250 | hgb_rankdev_l250 | hgb | rankdev | 50.000000 | 0.050000 | 0 | False |
| Q3 | 0.623221 | 0.622920 | -0.000301 | blend_w0.05_logreg_nosubject_rankdev_C0.003 | logreg_nosubject_rankdev_C0.003 | logreg | nosubject_rankdev | 0.003000 | 0.050000 | 1 | False |
| S1 | 0.551703 | 0.554273 | 0.002569 | blend_w0.1_logreg_all_C0.03 | logreg_all_C0.03 | logreg | all | 0.030000 | 0.100000 | 3 | False |
| S2 | 0.529813 | 0.529220 | -0.000593 | blend_w0.05_logreg_nosubject_rankdev_C0.01 | logreg_nosubject_rankdev_C0.01 | logreg | nosubject_rankdev | 0.010000 | 0.050000 | 2 | False |
| S3 | 0.500129 | 0.498416 | -0.001713 | blend_w0.05_logreg_all_C0.003 | logreg_all_C0.003 | logreg | all | 0.003000 | 0.050000 | 0 | False |
| S4 | 0.593698 | 0.594084 | 0.000386 | blend_w0.05_logreg_rankdev_C0.1 | logreg_rankdev_C0.1 | logreg | rankdev | 0.100000 | 0.050000 | 3 | False |

## Top Candidates

| name | spec | kind | feature_set | value | blend_weight | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blend_w0.05_logreg_all_C0.01 | logreg_all_C0.01 | logreg | all | 0.010000 | 0.050000 | 0.584493 | 0.636099 | 0.652913 | 0.624010 | 0.553016 | 0.530421 | 0.500318 | 0.594677 |
| blend_w0.05_logreg_all_C0.03 | logreg_all_C0.03 | logreg | all | 0.030000 | 0.050000 | 0.584568 | 0.635723 | 0.653243 | 0.624093 | 0.552613 | 0.530939 | 0.500895 | 0.594467 |
| blend_w0.05_logreg_nosubject_rankdev_C0.03 | logreg_nosubject_rankdev_C0.03 | logreg | nosubject_rankdev | 0.030000 | 0.050000 | 0.584575 | 0.636035 | 0.654160 | 0.623583 | 0.553270 | 0.530052 | 0.500838 | 0.594085 |
| blend_w0.05_logreg_rankdev_C0.03 | logreg_rankdev_C0.03 | logreg | rankdev | 0.030000 | 0.050000 | 0.584575 | 0.636032 | 0.654148 | 0.623621 | 0.553260 | 0.530073 | 0.500827 | 0.594065 |
| blend_w0.05_logreg_rankdev_C0.01 | logreg_rankdev_C0.01 | logreg | rankdev | 0.010000 | 0.050000 | 0.584585 | 0.636520 | 0.653604 | 0.623451 | 0.553706 | 0.529818 | 0.500567 | 0.594429 |
| blend_w0.05_logreg_nosubject_rankdev_C0.01 | logreg_nosubject_rankdev_C0.01 | logreg | nosubject_rankdev | 0.010000 | 0.050000 | 0.584587 | 0.636524 | 0.653610 | 0.623422 | 0.553714 | 0.529813 | 0.500578 | 0.594447 |
| blend_w0.05_logreg_all_C0.003 | logreg_all_C0.003 | logreg | all | 0.003000 | 0.050000 | 0.584604 | 0.636743 | 0.652644 | 0.623623 | 0.553923 | 0.530223 | 0.500129 | 0.594943 |
| blend_w0.05_logreg_nosubject_rankdev_C0.1 | logreg_nosubject_rankdev_C0.1 | logreg | nosubject_rankdev | 0.100000 | 0.050000 | 0.584643 | 0.635703 | 0.654639 | 0.623536 | 0.553296 | 0.530290 | 0.501318 | 0.593720 |
| blend_w0.05_logreg_rankdev_C0.1 | logreg_rankdev_C0.1 | logreg | rankdev | 0.100000 | 0.050000 | 0.584648 | 0.635702 | 0.654624 | 0.623573 | 0.553284 | 0.530332 | 0.501322 | 0.593698 |
| blend_w0.05_logreg_all_C0.1 | logreg_all_C0.1 | logreg | all | 0.100000 | 0.050000 | 0.584739 | 0.635622 | 0.653510 | 0.624004 | 0.552629 | 0.531459 | 0.501685 | 0.594264 |
| blend_w0.05_logreg_rankdev_C0.003 | logreg_rankdev_C0.003 | logreg | rankdev | 0.003000 | 0.050000 | 0.584741 | 0.637138 | 0.653054 | 0.623237 | 0.554536 | 0.529974 | 0.500549 | 0.594702 |
| blend_w0.05_logreg_nosubject_rankdev_C0.003 | logreg_nosubject_rankdev_C0.003 | logreg | nosubject_rankdev | 0.003000 | 0.050000 | 0.584743 | 0.637140 | 0.653054 | 0.623221 | 0.554542 | 0.529975 | 0.500558 | 0.594714 |
