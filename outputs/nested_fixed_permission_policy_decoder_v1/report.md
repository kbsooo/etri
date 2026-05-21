# Nested Fixed Permission Policy Decoder

This stress test selects among fixed permission policies on each outer fold's train rows and scores on held-out rows. It estimates how much of the fixed-policy improvement is policy-search optimism.

## Scores

| source | avg_log_loss | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 | drift_vs_reference | corr_vs_reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_policy_best | 0.615095 | 0.663133 | 0.685743 | 0.665606 | 0.565500 | 0.572205 | 0.528019 | 0.625461 | 0.070382 | 0.858505 |
| nested_global_policy | 0.615224 | 0.663133 | 0.685743 | 0.665606 | 0.565500 | 0.572205 | 0.528917 | 0.625461 | 0.070513 | 0.858122 |
| extended_full_oof_winners | 0.616766 | 0.664980 | 0.689098 | 0.665606 | 0.565500 | 0.572205 | 0.534513 | 0.625461 | 0.069892 | 0.860714 |
| nested_target_policy | 0.617663 | 0.665012 | 0.689120 | 0.665606 | 0.570403 | 0.572205 | 0.531513 | 0.629784 | 0.070845 | 0.857785 |
| stable_signal_s4_temporal | 0.620281 | 0.670652 | 0.685743 | 0.665606 | 0.572511 | 0.577195 | 0.529419 | 0.640842 | 0.068726 | 0.871113 |

## Selection Counts

| selection | target | selected | outer_count |
| --- | --- | --- | --- |
| global | ALL | nested_majority_policy | 3 |
| global | ALL | q1s3_signed_s1s2s4_extended_q3_stable | 2 |
| targetwise | Q1 | q1s3_signed_rest_stable | 4 |
| targetwise | Q1 | extended_full_oof_winners | 1 |
| targetwise | Q2 | global_signed_s100_c050 | 3 |
| targetwise | Q2 | stable_signal_s4_temporal | 2 |
| targetwise | Q3 | stable_signal_s4_temporal | 4 |
| targetwise | Q3 | global_signed_s100_c050 | 1 |
| targetwise | S1 | extended_full_oof_winners | 3 |
| targetwise | S1 | global_signed_s100_c050 | 2 |
| targetwise | S2 | extended_full_oof_winners | 5 |
| targetwise | S3 | nested_majority_policy | 3 |
| targetwise | S3 | q1s3_signed_rest_stable | 1 |
| targetwise | S3 | stable_signal_s4_temporal | 1 |
| targetwise | S4 | extended_full_oof_winners | 4 |
| targetwise | S4 | global_signed_s100_c050 | 1 |
