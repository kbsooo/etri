# Sample-weighted Targetwise Blend Search

This selector optimizes target adoption under the submission sample panel-position distribution.

## Summary

| baseline | uniform_base_avg | uniform_final_avg | weighted_base_avg | weighted_final_avg | uniform_improvement | weighted_improvement | uniform_p025 | uniform_p500 | uniform_p975 | weighted_p025 | weighted_p500 | weighted_p975 | promote_weighted | promote_uniform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| multi_signal | 0.581592 | 0.581445 | 0.597026 | 0.596441 | 0.000148 | 0.000585 | -0.000072 | 0.000147 | 0.000370 | 0.000163 | 0.000584 | 0.001002 | True | False |

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
| S4 | support_s4w100 | 1.000000 | logit | 0.001034 | 0.004094 | 0.001070 | 0.003600 | 0.000023 | 0.004684 | -0.005917 |

## Block deltas

| block | rows | delta |
| --- | --- | --- |
| mid | 100 | 0.000514 |
| late_mid | 94 | 0.000003 |
| tail20 | 22 | 0.000669 |

## Top target options

| target | source | weight | mode | uniform_delta | weighted_delta | weighted_p025 | weighted_p500 | weighted_p975 | folds_improved | mid_delta | late_mid_delta | tail20_delta | worst_subject_delta | score | selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q1 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| Q2 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| Q3 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S1 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S2 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S3 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True |
| S4 | support_s4w100 | 1.000000 | logit | 0.001034 | 0.004094 | 0.001070 | 0.004073 | 0.007001 | 3 | 0.003600 | 0.000023 | 0.004684 | -0.005917 | 0.004125 | True |
| S4 | multi_signal | 0.000000 | base | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | False |
