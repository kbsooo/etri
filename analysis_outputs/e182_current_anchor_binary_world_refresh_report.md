# E182 Current-Anchor Binary-World Refresh

## Question

E181 says inherited binary worlds are a counterprior against E176 and favor
E154/E144. Is that still true if the binary-world stress is regenerated from
the current public anchors and the E176/E154/E144 objectives are asked
explicitly?

No submission is created.

## Result In One Sentence

Refreshed current-anchor worlds do not certify E176, E154, or E144 one-sided:
under objective-pressure worlds E176/E154/E144 cross zero in
`1.000` / `1.000` / `1.000` of scenarios. The
strict residual-budget range solver only found incumbents in
`0.233` of rows, which is itself a warning that this inverse
problem is still hard at frontier scale. E181's counterprior remains useful, but
it is not enough to promote E154/E144 as certified replacements.

## Scenario Fits

| scenario | has_incumbent | slack_sum | sum_abs_residual | max_abs_residual | positive_cell_count | frontier_scale_fit | elapsed_sec |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_t010 | True | 0.00041235 | 0.00041235 | 7.84319e-05 | 881 | True | 6.02603 |
| global_t010_subject_t020 | True | 0.000207364 | 0.000207364 | 5.13148e-05 | 899 | True | 6.02306 |
| global_t010_subject_t010 | True | 0.000494357 | 0.000494357 | 7.62925e-05 | 975 | True | 6.01652 |

## Candidate Ranges Versus E95

| scenario | candidate | min_delta_vs_e95 | max_delta_vs_e95 | range_width | crosses_zero | one_sided_negative | one_sided_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_t010 | e144 | -0.00102025 | 0.000849469 | 0.00186971 | True | False | False |
| global_t010 | e176 | -0.000436604 |  |  | False | False | False |
| global_t010_subject_t010 | e144 | -0.000983674 | 0.000815183 | 0.00179886 | True | False | False |
| global_t010_subject_t010 | e176 | -0.000386481 |  |  | False | False | False |
| global_t010_subject_t010 | e172 | -0.000356607 |  |  | False | False | False |

## Objective-Pressure Worlds Versus E95

| scenario | candidate | pressure_min_delta_vs_e95 | pressure_max_delta_vs_e95 | pressure_range_width | pressure_crosses_zero | pressure_one_sided_negative | pressure_one_sided_positive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_t010 | e154 | -0.00109286 | 0.000923535 | 0.00201639 | True | False | False |
| global_t010 | e144 | -0.000645959 | 0.000741469 | 0.00138743 | True | False | False |
| global_t010 | e176 | -0.000421216 | 0.000254123 | 0.000675339 | True | False | False |
| global_t010_subject_t010 | e154 | -0.00103192 | 0.000887734 | 0.00191966 | True | False | False |
| global_t010_subject_t010 | e144 | -0.000972245 | 0.000826612 | 0.00179886 | True | False | False |
| global_t010_subject_t010 | e176 | -0.000382384 | 0.000244934 | 0.000627318 | True | False | False |
| global_t010_subject_t020 | e154 | -0.00106669 | 0.000890156 | 0.00195684 | True | False | False |
| global_t010_subject_t020 | e144 | -0.000992245 | 0.000838041 | 0.00183029 | True | False | False |
| global_t010_subject_t020 | e176 | -0.000416038 | 0.000251227 | 0.000667266 | True | False | False |

## Raw Range Solver Rows

| scenario | candidate | direction | has_incumbent | delta_vs_e95 | sum_abs_residual | max_abs_residual | slack_sum | status | elapsed_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_t010 | e144 | max | True | 0.000849469 | 0.000351193 | 8.36299e-05 | 0.00041236 | 1 | 6.00956 |
| global_t010 | e144 | min | True | -0.00102025 | 0.000372066 | 5.87923e-05 | 0.00041236 | 0 | 1.07752 |
| global_t010 | e154 | max | False |  |  |  |  | 1 | 6.0318 |
| global_t010 | e154 | min | False |  |  |  |  | 1 | 6.01975 |
| global_t010 | e172 | max | False |  |  |  |  | 1 | 6.0065 |
| global_t010 | e172 | min | False |  |  |  |  | 1 | 6.02576 |
| global_t010 | e174 | max | False |  |  |  |  | 1 | 6.00637 |
| global_t010 | e174 | min | False |  |  |  |  | 1 | 6.0351 |
| global_t010 | e176 | max | False |  |  |  |  | 1 | 6.00674 |
| global_t010 | e176 | min | True | -0.000436604 | 0.000387402 | 7.95989e-05 | 0.00041236 | 1 | 6.00743 |
| global_t010_subject_t010 | e144 | max | True | 0.000815183 | 0.000484871 | 7.61107e-05 | 0.000494367 | 1 | 6.02239 |
| global_t010_subject_t010 | e144 | min | True | -0.000983674 | 0.000331706 | 6.44286e-05 | 0.000331706 | 0 | 4.50373 |
| global_t010_subject_t010 | e154 | max | False |  |  |  |  | 1 | 6.02012 |
| global_t010_subject_t010 | e154 | min | False |  |  |  |  | 1 | 6.00908 |
| global_t010_subject_t010 | e172 | max | False |  |  |  |  | 1 | 6.01939 |
| global_t010_subject_t010 | e172 | min | True | -0.000356607 | 0.000480576 | 8.23028e-05 | 0.000494367 | 1 | 6.00815 |
| global_t010_subject_t010 | e174 | max | False |  |  |  |  | 1 | 6.02625 |
| global_t010_subject_t010 | e174 | min | False |  |  |  |  | 1 | 6.01827 |
| global_t010_subject_t010 | e176 | max | False |  |  |  |  | 1 | 6.01713 |
| global_t010_subject_t010 | e176 | min | True | -0.000386481 | 0.000436557 | 8.63654e-05 | 0.000436064 | 1 | 6.0119 |
| global_t010_subject_t020 | e144 | max | False |  |  |  |  | 1 | 6.01891 |
| global_t010_subject_t020 | e144 | min | False |  |  |  |  | 1 | 6.01145 |
| global_t010_subject_t020 | e154 | max | False |  |  |  |  | 1 | 6.01197 |
| global_t010_subject_t020 | e154 | min | False |  |  |  |  | 1 | 6.01171 |
| global_t010_subject_t020 | e172 | max | False |  |  |  |  | 1 | 6.01706 |
| global_t010_subject_t020 | e172 | min | False |  |  |  |  | 1 | 6.01788 |
| global_t010_subject_t020 | e174 | max | False |  |  |  |  | 1 | 6.01585 |
| global_t010_subject_t020 | e174 | min | False |  |  |  |  | 1 | 6.01873 |
| global_t010_subject_t020 | e176 | max | False |  |  |  |  | 1 | 6.01624 |
| global_t010_subject_t020 | e176 | min | False |  |  |  |  | 1 | 6.02038 |

## Raw Pressure Solver Rows

| scenario | candidate | direction | has_incumbent | delta_vs_e95 | sum_abs_residual | max_abs_residual | slack_sum | status | elapsed_sec |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| global_t010 | e144 | max | True | 0.000741469 | 0.000575343 | 8.12783e-05 | 0.00104383 | 1 | 5.02063 |
| global_t010 | e144 | min | True | -0.000645959 | 0.000613105 | 8.67318e-05 | 0.00104383 | 1 | 5.01584 |
| global_t010 | e154 | max | True | 0.000923535 | 0.000347905 | 7.68114e-05 | 0.000347905 | 1 | 5.00664 |
| global_t010 | e154 | min | True | -0.00109286 | 0.000380261 | 6.64259e-05 | 0.000380261 | 1 | 5.0066 |
| global_t010 | e176 | max | True | 0.000254123 | 0.000277027 | 4.85323e-05 | 0.000277027 | 1 | 5.00637 |
| global_t010 | e176 | min | True | -0.000421216 | 0.000223444 | 4.94733e-05 | 0.000223444 | 1 | 5.00872 |
| global_t010_subject_t010 | e144 | max | True | 0.000826612 | 0.000223294 | 3.79531e-05 | 0.000223294 | 1 | 5.02604 |
| global_t010_subject_t010 | e144 | min | True | -0.000972245 | 0.000312243 | 6.95007e-05 | 0.000312243 | 1 | 5.01049 |
| global_t010_subject_t010 | e154 | max | True | 0.000887734 | 0.000423991 | 7.29611e-05 | 0.000423991 | 1 | 5.00731 |
| global_t010_subject_t010 | e154 | min | True | -0.00103192 | 0.00022706 | 7.60565e-05 | 0.00022706 | 1 | 5.00747 |
| global_t010_subject_t010 | e176 | max | True | 0.000244934 | 0.000302612 | 4.26507e-05 | 0.000302612 | 1 | 5.01034 |
| global_t010_subject_t010 | e176 | min | True | -0.000382384 | 0.000417167 | 7.69856e-05 | 0.000417167 | 1 | 5.00768 |
| global_t010_subject_t020 | e144 | max | True | 0.000838041 | 0.000500293 | 7.98126e-05 | 0.000500293 | 1 | 5.02647 |
| global_t010_subject_t020 | e144 | min | True | -0.000992245 | 0.000454003 | 7.23456e-05 | 0.000454003 | 1 | 5.01567 |
| global_t010_subject_t020 | e154 | max | True | 0.000890156 | 0.000282913 | 8.23664e-05 | 0.000282913 | 1 | 5.00731 |
| global_t010_subject_t020 | e154 | min | True | -0.00106669 | 0.000478925 | 7.6558e-05 | 0.000478925 | 1 | 5.00738 |
| global_t010_subject_t020 | e176 | max | True | 0.000251227 | 0.000345513 | 8.66142e-05 | 0.000345513 | 1 | 5.00714 |
| global_t010_subject_t020 | e176 | min | True | -0.000416038 | 0.000177544 | 5.72791e-05 | 0.000177544 | 1 | 5.00907 |

## Interpretation

- E181's inherited-world ranking was a useful counterprior, but E182 shows it is
  not strong enough to promote E154/E144 as certified replacements. Under a
  refreshed current-anchor stress, objective pressure can produce both favorable
  and adverse worlds for E176, E154, and E144.
- The plateau law survives: current public anchors and structural priors still
  underidentify frontier-scale candidate signs. The hidden label space can
  support E176-like and E154/E144-like worlds depending on objective pressure.
- E176 should still be described as a conditional visible-body/Q2-underopen
  sensor, not a certified improvement. E154/E144 become the main alternate
  worldview to test, but E182 says they need either public feedback or an
  additional non-public selector before promotion.

## Decision

No new submission. The next public candidate remains a worldview choice rather
than an expected-score certificate. If spending one slot to test the broad
visible-body law, use E176 and decode with E177/E179/E180/E181/E182. If the
question is binary-world repaired-branch validity, E154 or E144 should first get
a fresh decoder and public-feedback interpretation comparable to E177.
