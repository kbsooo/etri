# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_sot_micro_rolling_context_only__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.622049`
- Delta vs subject prior: `-0.005605`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_sot_micro_rolling_context_only__absolute_plus_deviation__c0.3_b0.2 | 0.622049 | 0.667957 | 0.696029 | 0.676203 | 0.571188 | 0.575524 | 0.524392 | 0.643049 |
| best_plus_sot_micro_readiness_rolling__absolute_plus_deviation__c0.3_b0.2 | 0.622138 | 0.667000 | 0.696108 | 0.676698 | 0.572309 | 0.576419 | 0.522618 | 0.643815 |
| best_plus_sot_micro_s3_final_hour_core__absolute_plus_deviation__c0.3_b0.2 | 0.622282 | 0.670589 | 0.697838 | 0.673567 | 0.573072 | 0.579180 | 0.519293 | 0.642435 |
| best_plus_sot_micro_settled_no_phone__absolute_plus_deviation__c0.3_b0.2 | 0.622462 | 0.665224 | 0.701209 | 0.677231 | 0.570008 | 0.579674 | 0.519503 | 0.644386 |
| best_plus_sot_micro_charging_timing__absolute_plus_deviation__c0.3_b0.2 | 0.622572 | 0.671794 | 0.701967 | 0.675393 | 0.570006 | 0.575698 | 0.517765 | 0.645378 |
| best_plus_sot_micro_readiness_rolling__absolute__c0.3_b0.2 | 0.622870 | 0.669270 | 0.691633 | 0.674670 | 0.575651 | 0.573774 | 0.531558 | 0.643533 |
| best_plus_sot_micro_s3_final_hour_core__absolute_plus_deviation__c0.1_b0.2 | 0.622883 | 0.671903 | 0.698218 | 0.675405 | 0.572150 | 0.578557 | 0.522870 | 0.641076 |
| best_plus_sot_micro_readiness_rolling__absolute_plus_deviation__c0.1_b0.2 | 0.622901 | 0.668732 | 0.696858 | 0.676161 | 0.571735 | 0.575574 | 0.527948 | 0.643296 |
| best_plus_sot_micro_rolling_context_only__absolute_plus_deviation__c0.1_b0.2 | 0.622942 | 0.669794 | 0.697076 | 0.675359 | 0.571252 | 0.574993 | 0.529857 | 0.642263 |
| best_plus_sot_micro_settled_no_phone__absolute_plus_deviation__c0.1_b0.2 | 0.622945 | 0.666426 | 0.699662 | 0.676575 | 0.570001 | 0.578545 | 0.525726 | 0.643683 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best_plus_sot_micro_pre30m_settle__absolute_plus_deviation__c0.3_b0.2 | 0.622978 | 0.669167 | 0.700643 | 0.674928 | 0.571878 | 0.579654 | 0.523844 | 0.640731 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.