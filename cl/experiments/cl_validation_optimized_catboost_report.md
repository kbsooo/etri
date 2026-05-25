# CL Validation-Optimized CatBoost Candidates

## Validation Scores

| candidate | local_weighted | chrono_tail | hole_v1 | mirror_v1 | mirror_hole_avg | mean_abs_move |
|---|---|---|---|---|---|---|
| validation_optimized_targetwise | 0.629769 | 0.633274 | 0.617919 | 0.634454 | 0.626187 | 0.033716 |
| validation_optimized_guarded | 0.629769 | 0.633274 | 0.617919 | 0.634454 | 0.626187 | 0.033716 |

Public-calibrated estimate using the bridge from `cl_public_calibrated_validation_report.md`: approximately `0.6133`.

## Best Target Weights

| target | mode | weight | temp | score | mirror_hole | chrono | hole | mirror | chrono_delta | hole_delta | mirror_delta | mean_abs_move |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | logit | 0.100000 | 1.160000 | 0.683343 | 0.683343 | 0.667228 | 0.682786 | 0.683899 | -0.005288 | -0.004281 | -0.002223 | 0.017727 |
| Q2 | logit | 0.100000 | 1.160000 | 0.686953 | 0.686953 | 0.672906 | 0.673507 | 0.700399 | -0.003090 | -0.000877 | -0.006873 | 0.019781 |
| Q3 | logit | 0.350000 | 1.160000 | 0.663580 | 0.663580 | 0.665230 | 0.648643 | 0.678518 | -0.012366 | -0.016717 | -0.011789 | 0.060393 |
| S1 | logit | 0.600000 | 1.160000 | 0.568537 | 0.568537 | 0.540213 | 0.572778 | 0.564296 | -0.017712 | -0.029025 | -0.023448 | 0.082497 |
| S2 | logit | 0.150000 | 1.080000 | 0.583329 | 0.583329 | 0.635328 | 0.570799 | 0.595859 | 0.003497 | -0.002139 | -0.008025 | 0.022000 |
| S3 | logit | 0.100000 | 1.000000 | 0.552836 | 0.552836 | 0.596815 | 0.530124 | 0.575548 | 0.003269 | -0.001917 | -0.001533 | 0.016623 |
| S4 | logit | 0.100000 | 1.000000 | 0.644730 | 0.644730 | 0.655195 | 0.646799 | 0.642661 | -0.001258 | -0.001114 | -0.000947 | 0.016991 |

## Guarded Target Weights

| target | mode | weight | temp | score | mirror_hole | chrono | hole | mirror | chrono_delta | hole_delta | mirror_delta | mean_abs_move |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | logit | 0.100000 | 1.160000 | 0.683343 | 0.683343 | 0.667228 | 0.682786 | 0.683899 | -0.005288 | -0.004281 | -0.002223 | 0.017727 |
| Q2 | logit | 0.100000 | 1.160000 | 0.686953 | 0.686953 | 0.672906 | 0.673507 | 0.700399 | -0.003090 | -0.000877 | -0.006873 | 0.019781 |
| Q3 | logit | 0.350000 | 1.160000 | 0.663580 | 0.663580 | 0.665230 | 0.648643 | 0.678518 | -0.012366 | -0.016717 | -0.011789 | 0.060393 |
| S1 | logit | 0.600000 | 1.160000 | 0.568537 | 0.568537 | 0.540213 | 0.572778 | 0.564296 | -0.017712 | -0.029025 | -0.023448 | 0.082497 |
| S2 | logit | 0.150000 | 1.080000 | 0.583329 | 0.583329 | 0.635328 | 0.570799 | 0.595859 | 0.003497 | -0.002139 | -0.008025 | 0.022000 |
| S3 | logit | 0.100000 | 1.000000 | 0.552836 | 0.552836 | 0.596815 | 0.530124 | 0.575548 | 0.003269 | -0.001917 | -0.001533 | 0.016623 |
| S4 | logit | 0.100000 | 1.000000 | 0.644730 | 0.644730 | 0.655195 | 0.646799 | 0.642661 | -0.001258 | -0.001114 | -0.000947 | 0.016991 |

## File Summary

| file | target | keys_ok | no_na | mean_abs_vs_anchor | max_abs_vs_anchor | mean_abs_vs_model | mean | std | min | max |
|---|---|---|---|---|---|---|---|---|---|---|
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | Q1 | True | True | 0.021925 | 0.077042 | 0.129521 | 0.510793 | 0.153074 | 0.083150 | 0.869943 |
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | Q2 | True | True | 0.018901 | 0.071421 | 0.150686 | 0.532839 | 0.094786 | 0.125999 | 0.765499 |
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | Q3 | True | True | 0.061994 | 0.246685 | 0.121633 | 0.604033 | 0.083162 | 0.387795 | 0.770359 |
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | S1 | True | True | 0.066342 | 0.289229 | 0.060428 | 0.674687 | 0.157482 | 0.253390 | 0.926234 |
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | S2 | True | True | 0.020775 | 0.068058 | 0.114832 | 0.599635 | 0.168452 | 0.341455 | 0.926990 |
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | S3 | True | True | 0.013539 | 0.048136 | 0.112133 | 0.651104 | 0.194678 | 0.217498 | 0.970000 |
| submission_cl_catboost_validation_optimized_targetwise_prob.csv | S4 | True | True | 0.014733 | 0.061338 | 0.143435 | 0.556465 | 0.201940 | 0.073903 | 0.943229 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | Q1 | True | True | 0.021925 | 0.077042 | 0.129521 | 0.510793 | 0.153074 | 0.083150 | 0.869943 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | Q2 | True | True | 0.018901 | 0.071421 | 0.150686 | 0.532839 | 0.094786 | 0.125999 | 0.765499 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | Q3 | True | True | 0.061994 | 0.246685 | 0.121633 | 0.604033 | 0.083162 | 0.387795 | 0.770359 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | S1 | True | True | 0.066342 | 0.289229 | 0.060428 | 0.674687 | 0.157482 | 0.253390 | 0.926234 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | S2 | True | True | 0.020775 | 0.068058 | 0.114832 | 0.599635 | 0.168452 | 0.341455 | 0.926990 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | S3 | True | True | 0.013539 | 0.048136 | 0.112133 | 0.651104 | 0.194678 | 0.217498 | 0.970000 |
| submission_cl_catboost_validation_optimized_guarded_prob.csv | S4 | True | True | 0.014733 | 0.061338 | 0.143435 | 0.556465 | 0.201940 | 0.073903 | 0.943229 |
