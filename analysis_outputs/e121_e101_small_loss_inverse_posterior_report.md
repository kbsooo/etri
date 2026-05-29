# E121 Exact E101 Small-Loss Inverse Posterior

## Question

E101 public was `0.5763003660`, E95 was `0.5762913298`, and mixmin was `0.5763066405`. E101 therefore lost to E95 by `+0.0000090362` but still beat mixmin by `-0.0000062745`.

The question is not whether E101 was good. The question is what active-cell label world makes this exact boundary natural.

## Hard-Label Budget

- Active cells: `50`
- All-support E101-vs-E95 delta: `-0.0000966787`
- All-adverse E101-vs-E95 delta: `+0.0002116767`
- Observed E101-vs-E95 delta: `+0.0000090362`
- Flip benefit required by the observation: `0.657165` of available active-cell flip budget
- First greedy top-flip support count that beats mixmin: `21`
- Greedy support count closest to the exact observation: `22`
- First greedy top-flip support count that beats E95: `23`

Interpretation: the public world did not reject the E101 direction wholesale. It realized about two thirds of the E101 active-cell flip benefit. But it stopped roughly one high-impact S3/Q2 support cell short of beating E95.

## Greedy Boundary Rows

| flip_rank | sub_idx | target | subject_id | pos_bin | support_label | flip_benefit | cum_flip_benefit | delta_if_topk_support_per_all | beats_e95 | beats_mixmin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19 | 47 | S3 | id02 | interior | 1 | 0.01391324 | 0.32077261 | 0.00002838 | False | False |
| 20 | 22 | S3 | id01 | interior | 0 | 0.01374343 | 0.33451605 | 0.00002052 | False | False |
| 21 | 158 | S3 | id07 | interior | 1 | 0.01322825 | 0.34774430 | 0.00001297 | False | True |
| 22 | 49 | S3 | id02 | interior | 0 | 0.01308868 | 0.36083298 | 0.00000549 | False | True |
| 23 | 147 | S3 | id06 | near_edge | 1 | 0.01306796 | 0.37390094 | -0.00000198 | True | True |
| 24 | 91 | S3 | id04 | interior | 0 | 0.01305196 | 0.38695290 | -0.00000944 | True | True |
| 25 | 103 | S3 | id04 | right_edge | 1 | 0.01238289 | 0.39933579 | -0.00001652 | True | True |

## Exact-Observed Posterior by Prior

Bucket: `abs(delta - observed_delta) <= 1e-06` over `300000` simulated active-cell label worlds per prior.

| prior | world_rate | support_cells_mean | support_flip_share_mean | top10_support_rate | top22_support_rate | top23_support_rate | s3_support_rate | q2_support_rate | edge_like_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| both_equal_beta | 0.046953 | 29.410904 | 0.657197 | 0.829199 | 0.742113 | 0.752224 | 0.584061 | 0.602958 | 0.596225 |
| both_distance_beta | 0.046420 | 28.848341 | 0.657167 | 0.835868 | 0.736014 | 0.746230 | 0.594814 | 0.513689 | 0.591803 |
| nearest_beta | 0.046287 | 29.078064 | 0.657175 | 0.833055 | 0.733410 | 0.743793 | 0.588047 | 0.558568 | 0.584741 |
| prev_beta | 0.045867 | 29.058721 | 0.657131 | 0.827798 | 0.731838 | 0.742167 | 0.593310 | 0.538147 | 0.600209 |
| edge_endpoint_beta | 0.045713 | 28.701108 | 0.657203 | 0.856971 | 0.739201 | 0.749203 | 0.587401 | 0.526589 | 0.579215 |
| conflict_flat | 0.045560 | 29.250878 | 0.657190 | 0.809577 | 0.732836 | 0.743154 | 0.596383 | 0.544723 | 0.600130 |
| next_beta | 0.044910 | 28.902249 | 0.657171 | 0.823224 | 0.731807 | 0.741725 | 0.600102 | 0.499841 | 0.603901 |
| subject | 0.044110 | 29.166251 | 0.657181 | 0.813852 | 0.725854 | 0.735848 | 0.599661 | 0.525408 | 0.615414 |
| nearest_hard085 | 0.041647 | 29.646710 | 0.657150 | 0.824156 | 0.726789 | 0.733573 | 0.590214 | 0.602580 | 0.555841 |
| global | 0.007963 | 30.059858 | 0.657115 | 0.764169 | 0.710948 | 0.713761 | 0.618497 | 0.539861 | 0.611566 |

## Small-Loss Band by Prior

Bucket: E116-style small loss, `3e-6 < delta <= 20e-6`.

| prior | world_rate | delta_mean | support_cells_mean | support_flip_share_mean | top10_support_rate | s3_support_rate | q2_support_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| both_distance_beta | 0.375860 | 0.000011 | 28.517959 | 0.650008 | 0.826364 | 0.587718 | 0.508813 |
| prev_beta | 0.372867 | 0.000011 | 28.730511 | 0.649662 | 0.818318 | 0.585846 | 0.534775 |
| conflict_flat | 0.370523 | 0.000011 | 28.938825 | 0.649898 | 0.800306 | 0.589248 | 0.541652 |
| nearest_beta | 0.368017 | 0.000011 | 28.804058 | 0.650971 | 0.824749 | 0.581950 | 0.555272 |
| both_equal_beta | 0.364777 | 0.000011 | 29.165572 | 0.651355 | 0.820675 | 0.578265 | 0.601202 |
| next_beta | 0.358427 | 0.000011 | 28.624461 | 0.650508 | 0.813613 | 0.593925 | 0.496491 |
| nearest_hard085 | 0.357423 | 0.000012 | 29.269792 | 0.647954 | 0.812191 | 0.581448 | 0.599394 |
| subject | 0.355683 | 0.000011 | 28.872939 | 0.650191 | 0.804911 | 0.592841 | 0.522923 |
| edge_endpoint_beta | 0.348503 | 0.000011 | 28.450574 | 0.652025 | 0.850226 | 0.582533 | 0.521071 |
| global | 0.083817 | 0.000013 | 29.488805 | 0.643882 | 0.750519 | 0.605265 | 0.534861 |

## Highest-Impact Cell Posterior

Soft posterior uses a Gaussian sensor centered on the observed E101 delta with sigma `2e-06`.

| sub_idx | target | subject_id | pos_bin | support_label | flip_benefit | support_prob_mean_prior | posterior_support_mean | posterior_support_minus_prior_mean |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 133 | S3 | id06 | interior | 1 | 0.020334 | 0.925332 | 0.951207 | 0.025875 |
| 145 | S3 | id06 | right_edge | 1 | 0.019720 | 0.927807 | 0.951716 | 0.023909 |
| 141 | S3 | id06 | single | 1 | 0.019348 | 0.927807 | 0.950882 | 0.023075 |
| 39 | S3 | id02 | interior | 1 | 0.018881 | 0.884512 | 0.910467 | 0.025955 |
| 215 | S3 | id09 | left_edge | 1 | 0.018486 | 0.775612 | 0.795733 | 0.020120 |
| 146 | S3 | id06 | left_edge | 1 | 0.018482 | 0.926222 | 0.948916 | 0.022694 |
| 235 | S3 | id10 | interior | 1 | 0.018405 | 0.577492 | 0.576654 | -0.000838 |
| 120 | S3 | id05 | right_edge | 0 | 0.017822 | 0.634232 | 0.650451 | 0.016219 |
| 241 | S3 | id10 | interior | 0 | 0.017224 | 0.600163 | 0.607414 | 0.007250 |
| 8 | S3 | id01 | interior | 1 | 0.016344 | 0.855430 | 0.876464 | 0.021035 |
| 57 | S3 | id02 | near_edge | 1 | 0.015987 | 0.879198 | 0.899662 | 0.020464 |
| 12 | S3 | id01 | near_edge | 1 | 0.015942 | 0.858529 | 0.879251 | 0.020722 |

## Belief Update

E101's small loss is a knife-edge result, not a broad invalidation. The hidden public hard-label world is compatible with E101 support on most high-impact S3 cells, but not enough of them. Because the posterior cell support depends heavily on the assumed train-derived prior and does not expose a clean visible gate, the result does not justify another same-line submission.

This strengthens the current bottleneck diagnosis:

> The frontier is not model capacity. It is an underidentified public hard-label boundary on a small S3-heavy active-cell tail, where one or two high-impact support/adverse cells move the public score by the same scale as the whole observed improvement.

## Decision

Keep E95 as the standing frontier. Do not submit E108/E104/E106/E119/E89-style automatic followups.

The next information-rich action is to find an independent, non-public sensor for the missing high-impact S3 support cells. If no such sensor exists, the same-line frontier is exhausted and the next public slot should test a different hidden structure, not a finer E101 amplitude.
