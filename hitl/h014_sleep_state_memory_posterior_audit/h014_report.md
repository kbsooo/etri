# H014 Sleep-State Memory Posterior Audit

## Question

Do H012's high-impact public-equation cells agree with same-subject sleep-state and sensor-quality memory?

## Main Findings

- H012 changed cells audited: `1200`.
- Memory agrees with H012 direction on `0.405000` of changed cells.
- Memory disagrees on `0.595000` of changed cells.
- Memory-agree cells carry `0.279671` of H012 posterior gain.
- High alignment + high reliability cells: `196` cells, `0.101482` posterior-gain share.

## Target Summary

| target | changed_cells | posterior_gain_sum | posterior_gain_share | memory_agree_rate | memory_disagree_rate | memory_agree_gain_share_within_target | memory_disagree_gain_share_within_target | mean_alignment | mean_reliability_q |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S2 | 207 | 2.732941 | 0.218011 | 0.420290 | 0.579710 | 0.201235 | 0.798765 | -1.115059 | 0.512368 |
| S1 | 194 | 2.546571 | 0.203144 | 0.314433 | 0.685567 | 0.217477 | 0.782523 | -2.071727 | 0.479154 |
| Q3 | 141 | 1.931075 | 0.154045 | 0.553191 | 0.446809 | 0.549864 | 0.450136 | -0.055707 | 0.501609 |
| Q1 | 167 | 1.716408 | 0.136921 | 0.449102 | 0.550898 | 0.260078 | 0.739922 | -0.408243 | 0.511892 |
| S4 | 192 | 1.649612 | 0.131592 | 0.317708 | 0.682292 | 0.159738 | 0.840262 | -0.319747 | 0.515792 |
| S3 | 194 | 1.486706 | 0.118597 | 0.427835 | 0.572165 | 0.317860 | 0.682140 | -0.324538 | 0.525545 |
| Q2 | 105 | 0.472474 | 0.037690 | 0.390476 | 0.609524 | 0.334031 | 0.665969 | -0.019843 | 0.463875 |

## Bucket Summary

| bucket | cells | cell_share | posterior_gain_sum | posterior_gain_share | mean_gain | mean_alignment | targets |
| --- | --- | --- | --- | --- | --- | --- | --- |
| agree | 486 | 0.405000 | 3.505901 | 0.279671 | 0.007214 | 0.166956 | Q1,Q2,Q3,S1,S2,S3,S4 |
| disagree | 714 | 0.595000 | 9.029885 | 0.720329 | 0.012647 | -1.283388 | Q1,Q2,Q3,S1,S2,S3,S4 |
| high_align_q75 | 300 | 0.250000 | 2.899484 | 0.231297 | 0.009665 | 0.256916 | Q1,Q2,Q3,S1,S2,S3,S4 |
| high_align_q60 | 480 | 0.400000 | 3.487583 | 0.278210 | 0.007266 | 0.169036 | Q1,Q2,Q3,S1,S2,S3,S4 |
| high_rel_q60 | 483 | 0.402500 | 4.943533 | 0.394354 | 0.010235 | -0.710221 | Q1,Q2,Q3,S1,S2,S3,S4 |
| high_align_and_rel | 196 | 0.163333 | 1.272153 | 0.101482 | 0.006491 | 0.168378 | Q1,Q2,Q3,S1,S2,S3,S4 |
| low_align_or_low_rel | 688 | 0.573333 | 9.798688 | 0.781657 | 0.014242 | -1.280914 | Q1,Q2,Q3,S1,S2,S3,S4 |

## Candidate Summary

| candidate_id | mode | file | changed_cells | changed_rows | posterior_delta_vs_e247 | h012_posterior_delta_vs_e247 | kept_h012_posterior_gain_rate | mean_abs_prob_delta_vs_h012 | max_abs_prob_delta_vs_h012 | h014_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| memory_conflict_revert_q35_k300 | revert_conflict | submission_h014_memory_conflict_revert_q35_k300_1cd8ff27_uploadsafe.csv | 900 | 249 | -0.002565 | -0.007163 | 0.358133 | 0.009619 | 0.189623 | diagnostic_only |
| memory_compat_q60_rel40_k900 | keep_h012 | submission_h014_memory_compat_q60_rel40_k900_eb309f4d_uploadsafe.csv | 290 | 132 | -0.001072 | -0.007163 | 0.149715 | 0.018235 | 0.294110 | diagnostic_only |
| memory_compat_q65_rel50_k750 | keep_h012 | submission_h014_memory_compat_q65_rel50_k750_eb097c8a_uploadsafe.csv | 208 | 101 | -0.000866 | -0.007163 | 0.120850 | 0.019512 | 0.294110 | diagnostic_only |
| memory_compat_q70_rel55_k600 | keep_h012 | submission_h014_memory_compat_q70_rel55_k600_8e1482cb_uploadsafe.csv | 162 | 90 | -0.000748 | -0.007163 | 0.104355 | 0.020234 | 0.294110 | diagnostic_only |
| memory_compat_q75_rel60_k450 | keep_h012 | submission_h014_memory_compat_q75_rel60_k450_c6e8d810_uploadsafe.csv | 124 | 73 | -0.000624 | -0.007163 | 0.087179 | 0.020887 | 0.294110 | diagnostic_only |

## Interpretation

- If memory-compatible cells keep most of H012's posterior gain, H012 is not only public-equation fitting; it overlaps with within-subject human-state continuity.
- If memory-compatible cells are low-gain or target-skewed, H012 remains the best public file but should not be blindly amplified for private risk.
- Best generated H014 candidate is `submission_h014_memory_conflict_revert_q35_k300_1cd8ff27_uploadsafe.csv` with kept posterior-gain rate `0.358133`.

## Decision

- No H014 candidate is promoted above H012.
- Keep H012 as the current frontier and use memory compatibility as diagnostics/paper evidence.
