# Block Geometry and Orthcap Residual Audit

Last updated: 2026-05-26

## Split Geometry

Submission rows are not a single future holdout. They are interleaved same-subject hidden blocks surrounded by train blocks.

```text
id01  T28 S14 T13 S13
id02  T32 S16 T16 S16
id03  T22 S11 T11 S10
id04  T34 S1 T1 S5 T2 S8 T17 S6 T1 S1 T1 S3 T1 S3
id05  T26 S7 T1 S5 T13 S2 T3 S2 T1 S5
id06  T30 S8 T1 S5 T14 S1 T1 S4 T2 S6
id07  T33 S15 T16 S15
id08  T32 S2 T2 S6 T1 S2 T17 S1 T1 S4 T1 S2 T2 S2
id09  T28 S14 T13 S13
id10  T22 S11 T11 S11
```

This confirms why block-local priors can help: the hidden rows are often directly bracketed by known labels from the same subject.

## Subject Label Extremes

The target base rates are strongly subject-specific, especially for objective S labels.

```text
id06 S1/S2/S3/S4 train rates 0.938 / 0.917 / 0.958 / 0.854
id05 S1/S2/S3/S4 train rates 0.477 / 0.250 / 0.136 / 0.409
id03 Q1/Q2/Q3 train rates    0.848 / 0.818 / 0.727
id06 Q1/Q2/Q3 train rates    0.146 / 0.396 / 0.500
```

Interpretation: global calibration is weak. Subject identity and within-subject block position are mandatory features/postprocess dimensions.

## Re-Tested Block Label Residual On Orthcap

I re-ran the weak surrounding-label block residual on the new orthcap bases.

```text
orthcap010 base 0.561989
S4 blend weight 0.05: OOF delta -0.000413, geometry delta +0.000640
S2 blend weight 0.05: OOF delta -0.000289, geometry delta -0.000079

orthcap030 base 0.560427
S4 blend weight 0.03: OOF delta -0.000317, geometry delta +0.000315
S2 blend weight 0.03: OOF delta -0.000238, geometry delta -0.000138
```

Decision: do not stack this residual on orthcap. S4 is the larger apparent OOF gain but fails actual submission-geometry masks. S2 is too small to justify the extra public risk.

## Practical Consequence

The current useful block/subject structure is not another neighbor-label smoother. It is:

1. Preserve subject-specific residuals that are orthogonal to the failed public direction.
2. Use ordinal hidden-count quantization only where it changes a whole subject-target sum cleanly, especially Q3.
3. Treat block-label smoothing as exhausted at the current frontier unless a new representation predicts block rates directly.
