# Fixed Permission Policy Decoder

This experiment removes full target-wise grid selection and tests fixed decoder policies derived from nested cap-gate evidence: Q1/S3 get signed-margin residual permission, Q3 stays stable, and S1/S2/S4 are compared as stable vs aggressive extended residuals.

## Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | drift_vs_reference | corr_vs_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| q1s3_signed_s1s2s4_extended_q3_stable | 0.615095 | 0.663133 | 0.685743 | 0.665606 | 0.565500 | 0.572205 | 0.528019 | 0.625461 | 0.070382 | 0.858505 |
| nested_majority_policy | 0.615110 | 0.663133 | 0.685743 | 0.665606 | 0.565500 | 0.572205 | 0.528123 | 0.625461 | 0.070605 | 0.857834 |
| global_signed_s100_c050 | 0.616528 | 0.663909 | 0.684610 | 0.665606 | 0.566594 | 0.578284 | 0.528562 | 0.628134 | 0.071953 | 0.855875 |
| extended_full_oof_winners | 0.616766 | 0.664980 | 0.689098 | 0.665606 | 0.565500 | 0.572205 | 0.534513 | 0.625461 | 0.069892 | 0.860714 |
| q1s3_signed_s1s2_extended_rest_stable | 0.617292 | 0.663133 | 0.685743 | 0.665606 | 0.565500 | 0.572205 | 0.528019 | 0.640842 | 0.069658 | 0.862420 |
| q1s3_signed_s2_extended_rest_stable | 0.618294 | 0.663133 | 0.685743 | 0.665606 | 0.572511 | 0.572205 | 0.528019 | 0.640842 | 0.070121 | 0.864275 |
| q1s3_signed_rest_stable | 0.619007 | 0.663133 | 0.685743 | 0.665606 | 0.572511 | 0.577195 | 0.528019 | 0.640842 | 0.070383 | 0.863898 |
| stable_signal_s4_temporal | 0.620281 | 0.670652 | 0.685743 | 0.665606 | 0.572511 | 0.577195 | 0.529419 | 0.640842 | 0.068726 | 0.871113 |

## Policy Definitions

| policy | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_signed_s100_c050 | signed_margin_s100_c050 | signed_margin_s100_c050 | signed_margin_s100_c050 | signed_margin_s100_c050 | signed_margin_s100_c050 | signed_margin_s100_c050 | signed_margin_s100_c050 |
| q1s3_signed_rest_stable | signed_margin_s125_c030 | stable | stable | stable | stable | signed_margin_s100_c030 | stable |
| q1s3_signed_s2_extended_rest_stable | signed_margin_s125_c030 | stable | stable | stable | extended | signed_margin_s100_c030 | stable |
| q1s3_signed_s1s2_extended_rest_stable | signed_margin_s125_c030 | stable | stable | extended | extended | signed_margin_s100_c030 | stable |
| q1s3_signed_s1s2s4_extended_q3_stable | signed_margin_s125_c030 | stable | stable | extended | extended | signed_margin_s100_c030 | extended |
| nested_majority_policy | signed_margin_s125_c030 | stable | stable | extended | extended | signed_margin_s125_c030 | extended |
