# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_cc_opportunity__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.619462`
- Delta vs subject prior: `-0.008192`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_cc_opportunity__absolute_plus_deviation__c0.3_b0.2 | 0.619462 | 0.654835 | 0.704474 | 0.679818 | 0.563862 | 0.568897 | 0.528417 | 0.635927 |
| best_plus_cc_opportunity__absolute_plus_deviation__c0.1_b0.2 | 0.620374 | 0.657347 | 0.702534 | 0.678395 | 0.564852 | 0.570082 | 0.532985 | 0.636425 |
| best_plus_cc_opportunity__deviation__c0.3_b0.2 | 0.620656 | 0.656311 | 0.700852 | 0.677053 | 0.564620 | 0.570662 | 0.535006 | 0.640090 |
| best_plus_cc_opportunity__absolute__c0.3_b0.2 | 0.621481 | 0.656065 | 0.698401 | 0.678766 | 0.569094 | 0.571536 | 0.539674 | 0.636827 |
| best_plus_cc_opportunity__deviation__c0.1_b0.2 | 0.621564 | 0.658420 | 0.698426 | 0.676332 | 0.566252 | 0.573059 | 0.538506 | 0.639956 |
| best_plus_cc_load__absolute_plus_deviation__c0.3_b0.2 | 0.621727 | 0.665587 | 0.701886 | 0.673113 | 0.571972 | 0.575476 | 0.526936 | 0.637118 |
| best_plus_cc_recovery__absolute_plus_deviation__c0.3_b0.2 | 0.622149 | 0.666302 | 0.700962 | 0.667912 | 0.572523 | 0.577921 | 0.526825 | 0.642596 |
| best_plus_cc_load__deviation__c0.3_b0.2 | 0.622176 | 0.665162 | 0.699238 | 0.670048 | 0.572379 | 0.575089 | 0.533184 | 0.640134 |
| best_plus_cc_opportunity__absolute_plus_deviation__c0.03_b0.2 | 0.622195 | 0.661098 | 0.700160 | 0.677467 | 0.567119 | 0.572849 | 0.538051 | 0.638619 |
| best_plus_cc_opportunity__absolute__c0.1_b0.2 | 0.622367 | 0.658548 | 0.697667 | 0.677471 | 0.571035 | 0.573224 | 0.540636 | 0.637989 |
| best_plus_cc_opportunity__absolute_plus_deviation__c0.3_b0.1 | 0.622399 | 0.662806 | 0.703672 | 0.677910 | 0.568502 | 0.572934 | 0.530308 | 0.640656 |
| best_plus_cc_load__absolute_plus_deviation__c0.1_b0.2 | 0.622565 | 0.666554 | 0.700555 | 0.673452 | 0.572197 | 0.574933 | 0.532143 | 0.638119 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.