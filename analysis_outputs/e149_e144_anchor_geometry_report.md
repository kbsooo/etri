# E149 E144 Anchor-Geometry Audit

## Question

Is E144 a new E95 successor law, or mostly a pruned E142/E143 residual branch that stays near the hardtail frontier while trying to avoid E72/E101 public-negative axes?

## Anchor Geometry Summary

| name | public_delta_vs_e95 | changed_cells_vs_e95 | l1_logit_vs_e95 | cos_hardtail_axis | cos_e101_loss_axis | cos_e72_fail_axis | q2s3_share | share_Q3 | share_S3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mixmin | 0.000015311 | 550 | 9.709487240 | -1.000000000 | 0.651026487 | 0.671902535 | 0.222307092 | 0.000000000 | 0.208048831 |
| failed_e72 | 0.000116447 | 1047 | 15.443905077 | -0.671902535 | 0.201134072 | 1.000000000 | 0.106376216 | 0.116377751 | 0.045311471 |
| e101 | 0.000009036 | 50 | 0.539621968 | -0.651026487 | 1.000000000 | 0.201134072 | 1.000000000 | 0.000000000 | 0.935862322 |
| e144 |  | 185 | 3.292000000 | 0.031301926 | -0.019625796 | -0.024358970 | 0.161603888 | 0.340218712 | 0.161603888 |

## Live Candidate Geometry

| name | changed_cells_vs_e95 | l1_logit_vs_e95 | cos_e101_loss_axis | cos_e72_fail_axis | cos_e142_branch_axis | cos_e143_branch_axis | resid_ratio_vs_e142_axis | resid_ratio_vs_e143_axis | q2s3_share | share_Q3 | share_S3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e101 | 50 | 0.539621968 | 1.000000000 | 0.201134072 | -0.038616538 | -0.015677498 | 0.999254103 | 0.999877100 | 1.000000000 | 0.000000000 | 0.935862322 |
| e142 | 185 | 3.700000000 | -0.038616538 | -0.026846588 | 1.000000000 | 0.941534113 | 0.000000000 | 0.336917666 | 0.254054054 | 0.302702703 | 0.254054054 |
| e143 | 164 | 3.280000000 | -0.015677498 | -0.023410044 | 0.941534113 | 1.000000000 | 0.336917666 | 0.000000000 | 0.158536585 | 0.341463415 | 0.158536585 |
| e144 | 185 | 3.292000000 | -0.019625796 | -0.024358970 | 0.952146833 | 0.991918719 | 0.305640978 | 0.126874959 | 0.161603888 | 0.340218712 | 0.161603888 |
| e85 | 445 | 1.433193109 | 0.153884764 | 0.597923472 | -0.015581910 | -0.016549491 | 0.999878595 | 0.999863048 | 0.124265011 | 0.000000000 | 0.027669235 |
| e86 | 134 | 0.902767117 | -0.183868470 | 0.194277680 | 0.010462926 | 0.004247727 | 0.999945262 | 0.999990978 | 0.686452323 | 0.000000000 | 0.133168395 |
| e89 | 158 | 0.617468014 | 0.211828002 | 0.154424655 | 0.000000000 | 0.000000000 | 1.000000000 | 1.000000000 | 0.288429121 | 0.000000000 | 0.064222528 |
| e90 | 162 | 0.792568156 | -0.053481434 | 0.207351434 | 0.015673085 | 0.012013231 | 0.999877170 | 0.999927839 | 0.460664259 | 0.000000000 | 0.146157196 |

## E144 Pairwise Axis Relations

| left | right | cosine | projection_left_on_right | projection_right_on_left |
| --- | --- | --- | --- | --- |
| e144_branch_minus_e95 | e144_minus_e143 | 0.004358133 | 0.034090909 | 0.000557138 |
| e144_branch_minus_e95 | e144_minus_e142 | -0.057817171 | -0.176470588 | -0.018942677 |
| e144_minus_e143 | e144_minus_e142 | -0.075377836 | -0.029411765 | -0.193181818 |

## E144 Target Anatomy

| target | changed_cells | l1_logit | mean_signed_logit | cos_hardtail_axis | cos_e101_loss_axis | cos_e72_fail_axis |
| --- | --- | --- | --- | --- | --- | --- |
| Q3 | 56 | 1.120000000 | -0.000960000 |  |  | 0.006145062 |
| Q1 | 38 | 0.760000000 | 0.001600000 |  |  | -0.006728430 |
| S3 | 47 | 0.532000000 | -0.001112000 | 0.051809642 | -0.051809642 | -0.049402707 |
| S2 | 23 | 0.460000000 | 0.000400000 | 0.093132121 |  | -0.071897416 |
| S4 | 21 | 0.420000000 | 0.000240000 |  |  | -0.039710004 |
| S1 | 0 | 0.000000000 | -0.000000000 |  |  |  |
| Q2 | 0 | 0.000000000 | 0.000000000 |  |  |  |

## Interpretation

- E144 changed cells versus E95: `185`; E142 `185`, E143 `164`.
- E144 cosine with E142 branch axis: `0.952146833`; residual ratio vs E142: `0.305640978`.
- E144 cosine with E143 branch axis: `0.991918719`; residual ratio vs E143: `0.126874959`.
- E144 cosine with E101 public-negative axis: `-0.019625796`; with E72 fail axis: `-0.024358970`.
- E144 target L1 shares: Q3 `0.340219`, S3 `0.161604`, S2 `0.139733`, Q1 `0.230863`, S4 `0.127582`.

Read: E144 should be interpreted as a branch-pruned residual sensor, not a new broad representation breakthrough. It is close to the E142/E143 branch geometry, while its public value depends on whether that small residual direction avoids the E101/E72 negative axes well enough on hidden public labels.

## Decision

No submission is created. E144 remains the next file. Public feedback should be read together with E145/E148 and this geometry audit: a win validates branch-pruned residual geometry; a loss requires checking whether the E142/E143 branch geometry itself failed or only the fine retained S3/Q3/S2 slices failed.
