# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_sot_micro_readiness_rolling__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.622138`
- Delta vs subject prior: `-0.005516`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_sot_micro_readiness_rolling__absolute_plus_deviation__c0.3_b0.2 | 0.622138 | 0.667000 | 0.696108 | 0.676698 | 0.572309 | 0.576419 | 0.522618 | 0.643815 |
| best_plus_sot_micro_settled_no_phone__absolute_plus_deviation__c0.3_b0.2 | 0.622462 | 0.665224 | 0.701209 | 0.677231 | 0.570008 | 0.579674 | 0.519503 | 0.644386 |
| best_plus_sot_micro_charging_timing__absolute_plus_deviation__c0.3_b0.2 | 0.622572 | 0.671794 | 0.701967 | 0.675393 | 0.570006 | 0.575698 | 0.517765 | 0.645378 |
| best_plus_sot_micro_readiness_rolling__absolute__c0.3_b0.2 | 0.622870 | 0.669270 | 0.691633 | 0.674670 | 0.575651 | 0.573774 | 0.531558 | 0.643533 |
| best_plus_sot_micro_readiness_rolling__absolute_plus_deviation__c0.1_b0.2 | 0.622901 | 0.668732 | 0.696858 | 0.676161 | 0.571735 | 0.575574 | 0.527948 | 0.643296 |
| best_plus_sot_micro_settled_no_phone__absolute_plus_deviation__c0.1_b0.2 | 0.622945 | 0.666426 | 0.699662 | 0.676575 | 0.570001 | 0.578545 | 0.525726 | 0.643683 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best_plus_sot_micro_pre30m_settle__absolute_plus_deviation__c0.3_b0.2 | 0.622978 | 0.669167 | 0.700643 | 0.674928 | 0.571878 | 0.579654 | 0.523844 | 0.640731 |
| best_plus_sot_micro_readiness_rolling__deviation__c0.3_b0.2 | 0.623386 | 0.666346 | 0.696301 | 0.672884 | 0.573402 | 0.577927 | 0.530962 | 0.645883 |
| best_plus_sot_micro_charging_timing__absolute_plus_deviation__c0.1_b0.2 | 0.623474 | 0.672795 | 0.700994 | 0.675119 | 0.569868 | 0.575880 | 0.524955 | 0.644709 |
| best_plus_sot_micro_phone_charging_conflict__absolute_plus_deviation__c0.3_b0.2 | 0.623498 | 0.672012 | 0.705633 | 0.675444 | 0.572847 | 0.575196 | 0.518784 | 0.644572 |
| best_plus_sot_micro_settled_charging__absolute_plus_deviation__c0.3_b0.2 | 0.623531 | 0.670242 | 0.695307 | 0.680171 | 0.574762 | 0.579175 | 0.521901 | 0.643160 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.