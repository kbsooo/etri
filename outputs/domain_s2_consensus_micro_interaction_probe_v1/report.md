# Domain SSL Latent Frozen Probe

## Purpose

Probe whether the label-free SSL encoder latents contain readable label signal. The encoder is frozen; only small fold-safe logistic probes are trained.

## Baseline

- Subject-prior avg logloss: `0.627654`

## Best

- Source: `best_plus_s2cmi__absolute_plus_deviation__c0.3_b0.2`
- Avg logloss: `0.620955`
- Delta vs subject prior: `-0.006699`

## Top Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| best_plus_s2cmi__absolute_plus_deviation__c0.3_b0.2 | 0.620955 | 0.663404 | 0.692400 | 0.671287 | 0.578897 | 0.581358 | 0.521190 | 0.638149 |
| best_plus_s2cmi__absolute_plus_deviation__c0.1_b0.2 | 0.621037 | 0.660724 | 0.692996 | 0.672155 | 0.576392 | 0.578349 | 0.526477 | 0.640167 |
| best_plus_s2cmi__deviation__c0.3_b0.2 | 0.621114 | 0.660986 | 0.689543 | 0.670102 | 0.578398 | 0.579132 | 0.526861 | 0.642777 |
| best_plus_s2cmi__absolute__c0.3_b0.2 | 0.621709 | 0.653797 | 0.690119 | 0.668526 | 0.584513 | 0.581966 | 0.533638 | 0.639402 |
| best_plus_s2cmi__deviation__c0.1_b0.2 | 0.621778 | 0.659606 | 0.690652 | 0.671346 | 0.576785 | 0.578224 | 0.531606 | 0.644223 |
| best_plus_s2cmi__absolute_plus_deviation__c0.03_b0.2 | 0.622203 | 0.660151 | 0.694038 | 0.673039 | 0.574460 | 0.577527 | 0.532847 | 0.643359 |
| best_plus_s2cmi__absolute__c0.1_b0.2 | 0.622251 | 0.654863 | 0.691424 | 0.670127 | 0.581054 | 0.580766 | 0.535432 | 0.642089 |
| best_plus_s2cmi__absolute_plus_deviation__c0.3_b0.1 | 0.622502 | 0.666360 | 0.696750 | 0.672802 | 0.575372 | 0.579046 | 0.526029 | 0.641160 |
| best_plus_s2cmi__deviation__c0.3_b0.1 | 0.622703 | 0.665363 | 0.695552 | 0.672401 | 0.575332 | 0.577731 | 0.528926 | 0.643619 |
| best_plus_s2cmi__absolute__c0.3_b0.1 | 0.622859 | 0.661679 | 0.695713 | 0.671613 | 0.578400 | 0.579010 | 0.531743 | 0.641852 |
| best__absolute_plus_deviation__c0.3_b0.2 | 0.622961 | 0.668986 | 0.702098 | 0.674157 | 0.570959 | 0.577501 | 0.523927 | 0.643102 |
| best_plus_s2cmi__absolute_plus_deviation__c0.1_b0.1 | 0.622984 | 0.665497 | 0.697541 | 0.673700 | 0.574564 | 0.577834 | 0.529141 | 0.642611 |

## Decision Rule

Carry a latent forward only if it improves the subject-prior baseline without target-wise source cherry-picking. Treat this as a diagnostic, not a submission candidate.