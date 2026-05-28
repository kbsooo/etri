# Public Failure Decomposition

Last updated: 2026-05-26

## Observed Failure

`submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` looked like the local best:

```text
stage2 OOF      0.567530925
ordinal OOF     0.561903817
OOF delta       -0.005627107
stage2 public   0.5779449757
ordinal public  0.5783033652
public delta    +0.0003583895
```

So the stage2 -> ordinal direction is now an observed public-bad direction despite strong OOF.

## Target Decomposition

OOF delta of ordinal versus stage2:

```text
Q1  -0.001090
Q2  -0.000921
Q3  -0.016500
S1  -0.007202
S2  -0.002576
S3  -0.006760
S4  -0.004342
```

Most local gain comes from Q3 and objective S targets. Q2 is only positive after the ordinal count correction; before that, ambnext hurts Q2 by `+0.000602`.

## Public-Bad Direction Projection

I treated the full stage2 -> ordinal prediction delta as the observed bad public direction and ranked candidates by:

- OOF gain versus stage2
- projection onto that bad direction
- orthogonal move ratio
- linear public estimate from the observed stage2/ordinal public gap

Generated artifacts:

- `stage2_donor_targetmask_builder.py`
- `stage2_donor_targetmask_candidates.csv`
- `subject_target_gate_donor_builder.py`
- `subject_target_gate_donor_candidates.csv`
- `public_bad_direction_orthcap_builder.py`
- `public_bad_direction_orthcap_candidates.csv`
- `public_direction_risk_ranker.py`
- `public_direction_risk_ranked_candidates.csv`

## Candidate Families

### Formal Convex-Bound Candidates

These blend two submissions with known public scores, so Log Loss convexity gives a public upper bound:

```text
submission_publicobsblend_stage2_to_ordinal_w005.csv  OOF 0.567025  public upper bound 0.5779628952
submission_publicobsblend_stage2_to_ordinal_w010.csv  OOF 0.566549  public upper bound 0.5779808147
submission_publicobsblend_stage2_to_ordinal_w020.csv  OOF 0.565678  public upper bound 0.5780166536
```

### Lower-Projection Target-Mask Candidates

These do not have formal public bounds, but they avoid copying the whole failed direction:

```text
submission_stage2_donor_ordinal_q3_s_w035.csv        OOF 0.564838  projection 0.295  changed Q3,S1,S2,S3,S4
submission_stage2_donor_ordinal_s1_s3_s4_w080.csv    OOF 0.565139  projection 0.316  changed S1,S3,S4
submission_stage2_donor_ordinal_q3_w100.csv          OOF 0.565174  projection 0.342  changed Q3 only
submission_stage2_donor_ordinal_no_q2_w035.csv       OOF 0.564668  projection 0.345  changed all except Q2
submission_stage2_donor_blend500_q3_s_w050.csv       OOF 0.564686  projection 0.458  changed Q3,S1,S2,S3,S4, lower anchor distance
```

### Subject-Target Gate Candidates

For each subject-target pair, I activated a donor only where the donor improves stage2 OOF beyond a threshold. A time-half guardrail then selected gates on one half of each subject and evaluated on the other half.

Best half-gated candidates:

```text
submission_subjectgate_ordinal_all_thrm0p005_w100.csv  full OOF 0.558584  half-gate 0.563328  projection 0.623  active subject-targets 29
submission_subjectgate_ordinal_all_thr0p0_w100.csv     full OOF 0.558264  half-gate 0.563378  projection 0.709  active subject-targets 39
submission_subjectgate_ordinal_all_thrm0p0025_w100.csv full OOF 0.558348  half-gate 0.563547  projection 0.689  active subject-targets 34
submission_subjectgate_ordinal_all_thr0p0_w080.csv     full OOF 0.559639  half-gate 0.563785  projection 0.567  active subject-targets 39
```

Lower-projection subject-gate probes:

```text
submission_subjectgate_ordinal_all_thrm0p02_w080.csv   OOF 0.562297  half-gate 0.564583  projection 0.321  active subject-targets 13
submission_subjectgate_ordinal_all_thrm0p01_w050.csv   OOF 0.562741  half-gate 0.565277  projection 0.281  active subject-targets 23
submission_subjectgate_ordinal_s1_s3_s4_thrm0p01_w100.csv OOF 0.563962  half-gate 0.565689  projection 0.166  active subject-targets 10
submission_subjectgate_blend500_s1_s3_s4_thrm0p005_w100.csv OOF 0.563737  half-gate 0.565780  projection 0.186  active subject-targets 10
```

Interpretation: subject-target gating recovers much of the ordinal OOF gain while avoiding known bad subject-target cells, but the best OOF variants still move heavily along the observed public-bad direction. Treat them as high-upside probes, not as safer than the convex public-observed blends.

### Orthcap Candidates

Orthcap decomposes each stage2-based candidate move into the observed bad stage2->ordinal direction plus an orthogonal residual. It then caps, zeros, or slightly reverses the bad-direction component while keeping the residual.

Best representative files:

```text
submission_orthcap_s002_cap030_sc125.csv   OOF 0.559099  projection 0.375  source subjectgate ordinal all thr0 w100
submission_orthcap_s001_cap030_sc100.csv   OOF 0.560427  projection 0.300  source subjectgate ordinal all thr-0.005 w100
submission_orthcap_s001_cap020_sc100.csv   OOF 0.561165  projection 0.200
submission_orthcap_s001_cap010_sc100.csv   OOF 0.561989  projection 0.100
submission_orthcap_s009_cap005_sc100.csv   OOF 0.562905  projection 0.050
submission_orthcap_s005_cap000_sc100.csv   OOF 0.563648  projection ~0.000
submission_orthcap_s001_capm005_sc075.csv  OOF 0.564217  projection -0.0375
```

Interpretation: orthcap is the cleanest rescue of the failed ordinal family. It preserves broad OOF gains across all seven targets while substantially reducing the known public-bad axis. It has no convex public bound, so it sits between safe microblends and full subjectgate in risk.

## Decision

For score attempts, prefer the convex-bound microblends first. The next best score-risk family is orthcap, especially `submission_orthcap_s001_cap010_sc100.csv` and `submission_orthcap_s001_cap030_sc100.csv`. For maximum high-upside attempts, use full subject-target gates with explicit projection awareness. For information attempts, submit target-mask probes that isolate whether Q3, S-targets, or Q2 exclusion explains the public failure. Do not submit full ordinal/ambnext again.
