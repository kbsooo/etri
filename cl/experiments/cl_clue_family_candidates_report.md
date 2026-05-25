# CL Clue Family Candidates

## Best Feature-Family Blends Over Sleep-State

| feature_file | target | mode | weight | temp | delta_mirror_hole_vs_sleep | delta_chrono_vs_sleep | mean_move_vs_sleep | selection_score |
|---|---|---|---|---|---|---|---|---|
| prior_sleep_proxy_features_v1.parquet | S1 | logit | 0.300000 | 1.160000 | -0.023715 | -0.003993 | 0.057731 | -0.022169 |
| goal4_sleep_boundary_rest_features_v1.parquet | Q1 | logit | 0.300000 | 1.250000 | -0.022430 | -0.019964 | 0.059968 | -0.020436 |
| prior_sleep_window_features_v1.parquet | S1 | logit | 0.300000 | 1.160000 | -0.019316 | -0.027166 | 0.057577 | -0.017800 |
| goal4_sleep_boundary_rest_features_v1.parquet | S1 | logit | 0.300000 | 1.250000 | -0.010904 | -0.014597 | 0.051481 | -0.010608 |
| goal4_sleep_boundary_rest_features_v1.parquet | S4 | prob | 0.200000 | 1.000000 | -0.008270 | -0.008222 | 0.038504 | -0.008270 |
| goal4_hour_transition_features_v1.parquet | Q3 | logit | 0.000000 | 1.250000 | -0.006034 | -0.005116 | 0.027458 | -0.006034 |
| goal4_sleep_boundary_rest_features_v1.parquet | S2 | prob | 0.200000 | 1.000000 | -0.004787 | -0.010860 | 0.035743 | -0.004787 |
| goal4_hour_transition_features_v1.parquet | S2 | prob | 0.150000 | 1.000000 | -0.001846 | -0.001861 | 0.025018 | -0.001846 |

## Candidate Files

| file | target | keys_ok | no_na | mean_abs_vs_sleep | mean | min | max |
|---|---|---|---|---|---|---|---|
| submission_cl_clue_s1_only_sleep_family_prob.csv | Q1 | True | True | 0.000000 | 0.510739 | 0.068851 | 0.887831 |
| submission_cl_clue_s1_only_sleep_family_prob.csv | Q2 | True | True | 0.000000 | 0.533640 | 0.107519 | 0.787555 |
| submission_cl_clue_s1_only_sleep_family_prob.csv | Q3 | True | True | 0.000000 | 0.613825 | 0.326062 | 0.815152 |
| submission_cl_clue_s1_only_sleep_family_prob.csv | S1 | True | True | 0.052766 | 0.687224 | 0.247100 | 0.921404 |
| submission_cl_clue_s1_only_sleep_family_prob.csv | S2 | True | True | 0.000000 | 0.611200 | 0.271819 | 0.928022 |
| submission_cl_clue_s1_only_sleep_family_prob.csv | S3 | True | True | 0.000000 | 0.644345 | 0.235852 | 0.967321 |
| submission_cl_clue_s1_only_sleep_family_prob.csv | S4 | True | True | 0.000000 | 0.553642 | 0.094154 | 0.926143 |
| submission_cl_clue_q1_s1_sleep_boundary_prob.csv | Q1 | True | True | 0.067279 | 0.509036 | 0.110550 | 0.846134 |
| submission_cl_clue_q1_s1_sleep_boundary_prob.csv | Q2 | True | True | 0.000000 | 0.533640 | 0.107519 | 0.787555 |
| submission_cl_clue_q1_s1_sleep_boundary_prob.csv | Q3 | True | True | 0.000000 | 0.613825 | 0.326062 | 0.815152 |
| submission_cl_clue_q1_s1_sleep_boundary_prob.csv | S1 | True | True | 0.052766 | 0.687224 | 0.247100 | 0.921404 |
| submission_cl_clue_q1_s1_sleep_boundary_prob.csv | S2 | True | True | 0.000000 | 0.611200 | 0.271819 | 0.928022 |
| submission_cl_clue_q1_s1_sleep_boundary_prob.csv | S3 | True | True | 0.000000 | 0.644345 | 0.235852 | 0.967321 |
| submission_cl_clue_q1_s1_sleep_boundary_prob.csv | S4 | True | True | 0.000000 | 0.553642 | 0.094154 | 0.926143 |
| submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv | Q1 | True | True | 0.067279 | 0.509036 | 0.110550 | 0.846134 |
| submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv | Q2 | True | True | 0.000000 | 0.533640 | 0.107519 | 0.787555 |
| submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv | Q3 | True | True | 0.000000 | 0.613825 | 0.326062 | 0.815152 |
| submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv | S1 | True | True | 0.052766 | 0.687224 | 0.247100 | 0.921404 |
| submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv | S2 | True | True | 0.034771 | 0.625203 | 0.235550 | 0.930238 |
| submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv | S3 | True | True | 0.000000 | 0.644345 | 0.235852 | 0.967321 |
| submission_cl_clue_q1_q3_s1_s2_s4_family_prob.csv | S4 | True | True | 0.034894 | 0.555269 | 0.107774 | 0.921453 |

## Interpretation

- These candidates are not broad CatBoost extrapolations. They only apply feature families that improved over the current sleep-state baseline in fold-local OOF.
- The strictest candidate is S1-only because S1 has the largest stable signal and today's public feedback says overmoving S2/Q3 is dangerous.