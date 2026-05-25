# V38 Target-wise CatBoost Prototype Report

## Validation Family Average

| family | anchor_loss | model_loss | best_blend_loss | delta_best_vs_anchor |
|---|---|---|---|---|
| chrono_tail | 0.63797 | 0.69678 | 0.63090 | -0.00707 |
| hole_v1 | 0.62593 | 0.66977 | 0.61834 | -0.00759 |
| mirror_v1 | 0.64229 | 0.71668 | 0.63490 | -0.00738 |

## Target Average

| target | anchor_loss | model_loss | best_blend_loss | delta_best_vs_anchor | best_weight |
|---|---|---|---|---|---|
| Q1 | 0.68206 | 0.75061 | 0.67603 | -0.00604 | 0.20000 |
| Q2 | 0.68591 | 0.77851 | 0.68315 | -0.00275 | 0.20000 |
| Q3 | 0.67887 | 0.72661 | 0.66755 | -0.01132 | 0.40000 |
| S1 | 0.58136 | 0.57949 | 0.55769 | -0.02366 | 0.55000 |
| S2 | 0.60281 | 0.66993 | 0.59852 | -0.00429 | 0.20000 |
| S3 | 0.56791 | 0.64471 | 0.56757 | -0.00034 | 0.10000 |
| S4 | 0.64885 | 0.71100 | 0.64581 | -0.00304 | 0.15000 |

## Safe Blend Weights

| target | safe_weight | hole_mirror_delta | chrono_delta |
|---|---|---|---|
| Q1 | 0.05000 | -0.00247 | -0.01317 |
| Q2 | 0.12500 | -0.00210 | -0.00405 |
| Q3 | 0.25000 | -0.01134 | -0.01129 |
| S1 | 0.25000 | -0.02632 | -0.01835 |
| S2 | 0.25000 | -0.00727 | 0.00169 |
| S3 | 0.12500 | -0.00114 | 0.00128 |
| S4 | 0.12500 | -0.00175 | -0.00561 |

## Submission Shift Summary

| submission | target | weight | changed_rows | mean_abs_delta | max_abs_delta |
|---|---|---|---|---|---|
| safe | Q1 | 0.05000 | 250 | 0.00716 | 0.02822 |
| publiclike_routed | Q1 | 0.05000 | 250 | 0.01443 | 0.06786 |
| safe | Q2 | 0.12500 | 250 | 0.02083 | 0.07513 |
| publiclike_routed | Q2 | 0.12500 | 250 | 0.01959 | 0.10818 |
| safe | Q3 | 0.25000 | 250 | 0.04557 | 0.15129 |
| publiclike_routed | Q3 | 0.25000 | 250 | 0.02575 | 0.12894 |
| safe | S1 | 0.25000 | 250 | 0.03007 | 0.13538 |
| publiclike_routed | S1 | 0.25000 | 250 | 0.01671 | 0.12473 |
| safe | S2 | 0.25000 | 250 | 0.03342 | 0.09852 |
| publiclike_routed | S2 | 0.25000 | 250 | 0.01911 | 0.08933 |
| safe | S3 | 0.12500 | 250 | 0.01574 | 0.05520 |
| publiclike_routed | S3 | 0.12500 | 250 | 0.01387 | 0.06797 |
| safe | S4 | 0.12500 | 250 | 0.01977 | 0.08633 |
| publiclike_routed | S4 | 0.12500 | 250 | 0.01792 | 0.08633 |

## Submission Validation

| file | rows | keys_ok | no_na | min_prob | max_prob |
|---|---|---|---|---|---|
| submission_v38_targetwise_catboost_proto_safe_prob.csv | 250 | True | True | 0.05728 | 0.97000 |
| submission_v38_targetwise_catboost_proto_publiclike_routed_prob.csv | 250 | True | True | 0.06063 | 0.97000 |
| submission_v38_targetwise_catboost_proto_raw_model_prob.csv | 250 | True | True | 0.07763 | 0.96760 |

## Notes

- Feature base: accumulated CL feature artifacts plus goal4 transition/rest features.
- State model: unsupervised PCA day-state embedding, subject prototypes, recent prototypes, target high/low margins, subject-target margins, volatility, trajectory speed/acceleration.
- Supervised model: target-wise CatBoost with fold-local label prototypes for validation.
- Submission candidates are anchored to `submission_meta_anchor_w02_noq3_prob.csv`; raw model output is also written for diagnostics, but the anchored candidates are the practical ones.
