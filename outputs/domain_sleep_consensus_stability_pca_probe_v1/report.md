# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_scs_pca32__absolute__c0.3_b0.2`
- Avg logloss: `0.622164`
- Delta vs subject prior: `-0.005490`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_scs_pca32__absolute__c0.3_b0.2 | 0.622164 | 0.660049 | 0.697756 | 0.677221 | 0.570190 | 0.569041 | 0.536971 | 0.643920 |
| best_plus_scs_pca16__absolute_plus_deviation__c0.3_b0.2 | 0.622576 | 0.662713 | 0.703982 | 0.676701 | 0.569886 | 0.576690 | 0.527961 | 0.640096 |
| best_plus_scs_pca32__absolute__c0.1_b0.2 | 0.622610 | 0.661148 | 0.697231 | 0.677325 | 0.569991 | 0.570420 | 0.538720 | 0.643433 |
| best_plus_scs_pca32__absolute_plus_deviation__c0.3_b0.2 | 0.622748 | 0.662371 | 0.703706 | 0.679871 | 0.566333 | 0.573237 | 0.531326 | 0.642391 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best_plus_scs_pca32__absolute_plus_deviation__c0.1_b0.2 | 0.623084 | 0.663044 | 0.702075 | 0.679328 | 0.567098 | 0.571838 | 0.535585 | 0.642620 |
| best_plus_scs_pca64__absolute_plus_deviation__c0.1_b0.2 | 0.623200 | 0.664563 | 0.706508 | 0.684054 | 0.569863 | 0.570225 | 0.532430 | 0.634755 |
| best_plus_scs_pca16__absolute_plus_deviation__c0.1_b0.2 | 0.623323 | 0.664417 | 0.703073 | 0.676196 | 0.569934 | 0.575915 | 0.533632 | 0.640090 |
| best_plus_scs_pca64__absolute_plus_deviation__c0.3_b0.2 | 0.623389 | 0.664225 | 0.709200 | 0.684647 | 0.571031 | 0.570812 | 0.529296 | 0.634510 |
| best_plus_scs_pca32__absolute__c0.3_b0.1 | 0.623504 | 0.665221 | 0.699885 | 0.676562 | 0.571418 | 0.573012 | 0.534162 | 0.644267 |
| best_plus_scs_pca64__absolute_plus_deviation__c0.03_b0.2 | 0.623515 | 0.665580 | 0.703113 | 0.682133 | 0.569772 | 0.570998 | 0.535980 | 0.637025 |
| best_plus_scs_pca16__absolute__c0.3_b0.2 | 0.623519 | 0.663440 | 0.699752 | 0.674301 | 0.574713 | 0.574104 | 0.537582 | 0.640741 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.