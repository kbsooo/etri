# Sample-weighted Targetwise Blend Search

This selector optimizes target adoption under the submission sample panel-position distribution.

## Summary

| baseline | uniform_base_avg | uniform_final_avg | weighted_base_avg | weighted_final_avg | uniform_improvement | weighted_improvement | uniform_p025 | uniform_p500 | uniform_p975 | weighted_p025 | weighted_p500 | weighted_p975 | promote_weighted | promote_uniform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.581592 | 0.581519 | 0.597026 | 0.596546 | 0.000074 | 0.000480 | -0.000295 | 0.000074 | 0.000427 | 0.000142 | 0.000479 | 0.000813 | True | False |

## Position bins

| bin | train_frac | sample_frac | weight_ratio |
| --- | --- | --- | --- |
| [0.000,0.333) | 0.520000 | 0.000000 | 0.000000 |
| [0.333,0.667) | 0.226667 | 0.520000 | 2.294118 |
| [0.667,0.800) | 0.204444 | 0.000000 | 0.000000 |
| [0.800,1.000) | 0.048889 | 0.480000 | 9.818182 |

## Selected options

| target | source | weight | mode | uniform_delta | weighted_delta | weighted_p025 | mid_delta | late_mid_delta | tail20_delta | worst_subject_delta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Q2 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Q3 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| S1 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| S2 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| S3 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| S4 | dloss_q2s4 | 0.800000 | logit | 0.000516 | 0.003359 | 0.001026 | 0.002967 | -0.003840 | 0.003828 | -0.011451 |

## Block deltas

| block | rows | delta |
| --- | --- | --- |
| mid | 100 | 0.000424 |
| late_mid | 94 | -0.000549 |
| tail20 | 22 | 0.000547 |

## Top target options

| target | source | weight | mode | uniform_delta | weighted_delta | weighted_p025 | weighted_p500 | weighted_p975 | folds_improved | mid_delta | late_mid_delta | tail20_delta | worst_subject_delta | score | selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| Q2 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| Q3 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S1 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S2 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S3 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S4 | dloss_q2s4 | 0.800000 | logit | 0.000516 | 0.003359 | 0.001026 | 0.003338 | 0.005796 | 3 | 0.002967 | -0.003840 | 0.003828 | -0.011451 | 0.003157 | True |
| S4 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
