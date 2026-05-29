# E157 E156 Axis Response Audit

## Question

Did E156's Q1/S2/S4 minimum-body row reveal a target law, or did the all-four gate saturate so that body-minimization selected a low-information point?

## Strange Point

- E156 lattice variants: `3125`.
- all-four variants: `3125`.
- strict candidates: `2984`.
- all-minus-E95 span across the whole lattice: `0.000002432120`.
- E156 min-body file: `submission_e156_targetaxis_757546d2.csv`, axes `Q1+S2+S4`, body `0.171266666658`.

## Finite-Difference Axis Response

| axis | metric | mean_delta | p_favorable | lowbody_mean_delta | lowbody_p_favorable |
| --- | --- | --- | --- | --- | --- |
| Q3 | all_minus_base | -0.000000383335 | 1.000000000000 | -0.000000403328 | 1.000000000000 |
| Q1 | all_minus_base | -0.000000121912 | 1.000000000000 | -0.000000121289 | 1.000000000000 |
| S2 | all_minus_base | -0.000000043238 | 1.000000000000 | -0.000000041998 | 1.000000000000 |
| S4 | all_minus_base | -0.000000030784 | 1.000000000000 | -0.000000029953 | 1.000000000000 |
| S3 | all_minus_base | -0.000000029436 | 1.000000000000 | -0.000000028965 | 1.000000000000 |

| axis | metric | mean_delta | p_favorable | lowbody_mean_delta | lowbody_p_favorable |
| --- | --- | --- | --- | --- | --- |
| Q3 | post101_p95_vs_e95_e101_sensor | -0.000000132956 | 1.000000000000 | -0.000000140330 | 1.000000000000 |
| Q1 | post101_p95_vs_e95_e101_sensor | -0.000000082175 | 1.000000000000 | -0.000000083918 | 1.000000000000 |
| S2 | post101_p95_vs_e95_e101_sensor | -0.000000073006 | 1.000000000000 | -0.000000081276 | 1.000000000000 |
| S4 | post101_p95_vs_e95_e101_sensor | -0.000000010678 | 1.000000000000 | -0.000000010381 | 1.000000000000 |
| S3 | post101_p95_vs_e95_e101_sensor | -0.000000010209 | 1.000000000000 | -0.000000010051 | 1.000000000000 |

| axis | metric | mean_delta | p_favorable | lowbody_mean_delta | lowbody_p_favorable |
| --- | --- | --- | --- | --- | --- |
| S2 | e72_plausible_gap_vs_e95 | -0.000000714955 | 1.000000000000 | -0.000000738444 | 1.000000000000 |
| S4 | e72_plausible_gap_vs_e95 | -0.000000000000 | 0.150400000000 | -0.000000000000 | 0.178571428571 |
| Q1 | e72_plausible_gap_vs_e95 | 0.000000000000 | 0.000800000000 | 0.000000000000 | 0.006369426752 |
| Q3 | e72_plausible_gap_vs_e95 | 0.000000000000 | 0.000800000000 | 0.000000000000 | 0.006369426752 |
| S3 | e72_plausible_gap_vs_e95 | 0.000000000000 | 0.000800000000 | 0.000000000000 | 0.006369426752 |

## E155-Dominating Low-Body Rows

| tag | target_axes | body_norm_ratio | all_minus_base | delta_all_vs_e155 | post101_p95_vs_e95_e101_sensor | delta_post101_p95_vs_e155 | e72_plausible_gap_vs_e95 | delta_e72_gap_vs_e155 | alpha_Q1 | alpha_Q3 | alpha_S2 | alpha_S3 | alpha_S4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e156_bd67930d | Q1+Q3+S2+S4 | 0.240336138684 | -0.000010404446 | -0.000000041955 | -0.000003807382 | -0.000000061140 | -0.000001671496 | -0.000000594234 | 0.250000000000 | 0.250000000000 | 0.500000000000 | 0.000000000000 | 0.500000000000 |
| e156_46a3fcce | Q1+Q3+S2+S4 | 0.242888182723 | -0.000010392131 | -0.000000029641 | -0.000003756697 | -0.000000010455 | -0.000001077261 | 0.000000000000 | 0.250000000000 | 0.250000000000 | 0.250000000000 | 0.000000000000 | 0.750000000000 |
| e156_7bf43ae0 | Q1+Q3+S2+S4 | 0.229994221190 | -0.000010374494 | -0.000000012003 | -0.000003796818 | -0.000000050575 | -0.000001671496 | -0.000000594234 | 0.250000000000 | 0.250000000000 | 0.500000000000 | 0.000000000000 | 0.250000000000 |

## Decision

Materialized `submission_e157_lowbodypareto_bd67930d.csv` because it uses less body than E155 while improving local all-minus, post-E101 p95, and E72 gap.

Selected axes: `Q1+Q3+S2+S4`.
Selected all-minus-E95: `-0.000010404446` vs E155 `-0.000010362491`.
Selected body ratio: `0.240336138684` vs E155 `0.250000000000`.

This is not a new first sensor. The E155-dominating edge is far below public-resolution scale, and the finite-difference audit shows Q3 is locally favorable rather than rejected. E157 is a tuned low-body Pareto control; E154 remains the first public sensor and E155 remains the cleaner amplitude-control interpretation.
