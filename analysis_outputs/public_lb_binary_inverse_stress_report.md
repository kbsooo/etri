# Public LB Binary Inverse Stress

Question: does enforcing binary hidden labels for the all-test public world make known LB anchors precise enough to rank current candidates?

## Fit Quality

| scenario | solver_success | fit_sum_slack_objective | max_abs_residual | max_residual_over_frontier_raw05_gap | mip_gap | elapsed_sec | message |
| --- | --- | --- | --- | --- | --- | --- | --- |
| binary_no_prior | False | 0.000526704 | 0.000145053 | 1.66754 | 1 | 18.0283 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| binary_global_t005 | False | 0.000406737 | 0.000202364 | 2.3264 | 1 | 18.0502 | Time limit reached. (HiGHS Status 13: Time limit reached) |
| binary_global_t010_subject_t010 | False | 0.00014995 | 6.12422e-05 | 0.704045 | 1 | 18.0737 | Time limit reached. (HiGHS Status 13: Time limit reached) |

## Candidate Incumbent Ranges

| scenario | role | file | max | min | incumbent_crosses_zero | incumbent_one_sided_negative | incumbent_one_sided_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| binary_no_prior | pair_sensor_6b | submission_label_flow_focused_6b9335b1.csv | 0.00281774 | -0.00441576 | True | False | False |
| binary_no_prior | pair_sensor_1bb | submission_label_flow_focused_1bbfb735.csv | 0.00233289 |  | False | False | False |
| binary_no_prior | pair_sensor_1bb_s0p65 | submission_label_flow_sensorcurve_conservative_1bb_full_s0p65_0ee928c4.csv | 0.00148488 |  | False | False | False |

## Decision

- Best incumbent max absolute LB residual: `0.000061242`.
- A2C8-vs-raw05 public gap: `0.000086986`.
- At least one binary all-test incumbent fits anchors within the raw05/a2c8 public gap.
- Unobserved incumbent range rows: `3`.
- Incumbent cross-zero rows: `1`.
- Incumbent one-sided improvement rows: `0`.
- No representative unobserved candidate gets a binary-inverse one-sided improvement signal.
- Treat this as a stress test, not exact public-set reconstruction: optimizers may hit time limits, and all-test public membership may itself be the wrong hidden-world assumption.
