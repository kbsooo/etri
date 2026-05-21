# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_s2ma_sleep_micro_core__absolute__c0.3_b0.2`
- Avg logloss: `0.619103`
- Delta vs subject prior: `-0.008551`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_s2ma_sleep_micro_core__absolute__c0.3_b0.2 | 0.619103 | 0.656303 | 0.692903 | 0.672578 | 0.568504 | 0.574470 | 0.527509 | 0.641456 |
| best_plus_s2ma_sleep_micro_core__absolute_plus_deviation__c0.3_b0.2 | 0.619297 | 0.658726 | 0.693782 | 0.672639 | 0.567576 | 0.577097 | 0.522416 | 0.642842 |
| best_plus_s2ma_sleep_micro_core__absolute_plus_deviation__c0.1_b0.2 | 0.619760 | 0.659604 | 0.695254 | 0.673626 | 0.567454 | 0.574222 | 0.526623 | 0.641537 |
| best_plus_s2ma_sleep_micro_core__deviation__c0.3_b0.2 | 0.619904 | 0.658576 | 0.695363 | 0.671752 | 0.565212 | 0.575199 | 0.529102 | 0.644121 |
| best_plus_s2ma_subject_relative_sleep_micro__absolute_plus_deviation__c0.3_b0.2 | 0.620181 | 0.659519 | 0.691359 | 0.667915 | 0.570321 | 0.580883 | 0.520971 | 0.650298 |
| best_plus_s2ma_sleep_micro_core__absolute__c0.1_b0.2 | 0.620497 | 0.657890 | 0.694762 | 0.674368 | 0.569492 | 0.573745 | 0.531900 | 0.641324 |
| best_plus_s2ma_rolling_sleep_micro__absolute_plus_deviation__c0.1_b0.2 | 0.620548 | 0.663752 | 0.698215 | 0.672474 | 0.566946 | 0.571401 | 0.530339 | 0.640713 |
| best_plus_s2ma_subject_relative_sleep_micro__deviation__c0.3_b0.2 | 0.620553 | 0.658739 | 0.694275 | 0.667822 | 0.568080 | 0.578745 | 0.526475 | 0.649738 |
| best_plus_s2ma_subject_relative_sleep_micro__absolute__c0.3_b0.2 | 0.620638 | 0.659756 | 0.690537 | 0.669654 | 0.568745 | 0.580774 | 0.523459 | 0.651541 |
| best_plus_s2ma_rolling_sleep_micro__absolute_plus_deviation__c0.3_b0.2 | 0.620647 | 0.664280 | 0.699258 | 0.673126 | 0.568019 | 0.572819 | 0.525144 | 0.641886 |
| best_plus_s2ma_subject_relative_sleep_micro__absolute_plus_deviation__c0.1_b0.2 | 0.620729 | 0.660859 | 0.694144 | 0.671182 | 0.567604 | 0.578788 | 0.525379 | 0.647149 |
| best_plus_s2ma_sleep_micro_core__deviation__c0.1_b0.2 | 0.620829 | 0.660237 | 0.696380 | 0.672889 | 0.565660 | 0.574566 | 0.533103 | 0.642968 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.