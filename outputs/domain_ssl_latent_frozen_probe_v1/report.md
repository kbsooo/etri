# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `subject_token_event_cross_missing__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.626064`
- Delta vs subject prior: `-0.001590`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| subject_token_event_cross_missing__absolute_plus_deviation__c0.3_b0.2 | 0.626064 | 0.670670 | 0.703159 | 0.673943 | 0.576429 | 0.579977 | 0.531367 | 0.646903 |
| subject_token_event_cross_missing__absolute__c0.3_b0.1 | 0.626183 | 0.670163 | 0.701137 | 0.673837 | 0.576458 | 0.579850 | 0.535545 | 0.646291 |
| subject_token_event_cross_missing__absolute__c0.1_b0.1 | 0.626250 | 0.670533 | 0.701384 | 0.674018 | 0.576065 | 0.579728 | 0.536211 | 0.645810 |
| subject_token_event_cross_missing__absolute__c0.03_b0.1 | 0.626387 | 0.670988 | 0.701508 | 0.674413 | 0.575799 | 0.579718 | 0.536912 | 0.645369 |
| subject_token_event_cross_missing__absolute__c0.1_b0.2 | 0.626401 | 0.669141 | 0.698976 | 0.671088 | 0.577794 | 0.581822 | 0.540200 | 0.645786 |
| subject_token_event_cross_missing__absolute__c0.3_b0.2 | 0.626404 | 0.668518 | 0.698618 | 0.670838 | 0.578615 | 0.582207 | 0.539213 | 0.646822 |
| subject_token_event_cross_missing__absolute_plus_deviation__c0.3_b0.1 | 0.626411 | 0.671483 | 0.703720 | 0.675433 | 0.575744 | 0.579542 | 0.532289 | 0.646666 |
| subject_token_event_cross_missing__absolute__c0.03_b0.2 | 0.626523 | 0.669938 | 0.699086 | 0.671746 | 0.577205 | 0.581626 | 0.541235 | 0.644821 |
| global_event_cross_missing__absolute__c0.3_b0.1 | 0.626550 | 0.671069 | 0.699508 | 0.674045 | 0.575567 | 0.580136 | 0.539912 | 0.645612 |
| global_event_cross_missing__deviation__c0.3_b0.1 | 0.626569 | 0.671700 | 0.700102 | 0.676373 | 0.575561 | 0.579364 | 0.537756 | 0.645131 |
| global_event_cross_missing__absolute__c0.1_b0.1 | 0.626580 | 0.671094 | 0.699469 | 0.674308 | 0.575585 | 0.580157 | 0.539719 | 0.645728 |
| subject_token_event_cross_missing__deviation__c0.3_b0.1 | 0.626603 | 0.670697 | 0.702198 | 0.674224 | 0.576348 | 0.580205 | 0.535173 | 0.647377 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.