# Temporal Deviation Target Diagnostics

## Purpose

Check whether 3/7/14/28-day novelty, recovery, and trajectory features are globally useful or only target-specific.

## Main Result

- Base late-fusion diagnostic source: `best__absolute_plus_deviation__c0.3_b0.2`
- Base avg logloss: `0.622961`
- Best avg source in subset probe: `best__absolute_plus_deviation__c0.3_b0.2` at `0.622961`
- Conclusion: temporal deviation worsens the average if used globally, but exposes strong target-specific axes.

## Target-Specific Best Sources

| target | source_family | best_loss | base_loss | delta_vs_base | best_source |
| --- | --- | --- | --- | --- | --- |
| Q1 | future | 0.666953 | 0.668986 | -0.002033 | td_future__absolute__c0.3_b0.2 |
| Q2 | trajectory | 0.692265 | 0.702098 | -0.009833 | td_trajectory__deviation__c0.3_b0.2 |
| Q3 | trajectory | 0.667198 | 0.674157 | -0.006959 | td_trajectory__deviation__c0.03_b0.2 |
| S1 | best_late_fusion | 0.570927 | 0.570959 | -0.000032 | best__absolute_plus_deviation__c0.1_b0.2 |
| S2 | future | 0.573965 | 0.577501 | -0.003536 | td_future__absolute__c0.3_b0.2 |
| S3 | best_late_fusion | 0.523927 | 0.523927 | 0.000000 | best__absolute_plus_deviation__c0.3_b0.2 |
| S4 | best_late_fusion | 0.643038 | 0.643102 | -0.000063 | best__absolute_plus_deviation__c0.1_b0.2 |

## Read

- `trajectory` is the strongest new family for Q2/Q3, suggesting multi-day movement through latent space matters more than absolute day state for those targets.
- `future` is strongest for Q1/S2, which may reflect recovery/after-effect structure around a day rather than only prior baseline.
- S3 remains best served by the current late-fusion latent, so a one-size-fits-all temporal-deviation encoder would damage useful signal.
- Next decoder should treat these as candidate target-specific state features with nested source selection, not as a direct global replacement.