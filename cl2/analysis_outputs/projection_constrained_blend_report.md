# Projection-Constrained Blend Report

Last updated: 2026-05-26

## Purpose

`submission_ordinal_q_constraints_ambnext_Q2Q3_nearest_w0.75.csv` improved OOF to `0.561904` but scored public `0.5783033652`, worse than the current public best stage2 file by `+0.0003583895`. I therefore treat the stage2-to-ordinal move as an observed public-bad direction.

The projection blend search minimizes OOF while explicitly capping projection onto that failed direction. It only blends already generated orthcap/exact-count submissions in probability space, then audits the resulting OOF, probability validity, and projection.

## Key Output

| Cap | File | OOF | Projection | Linear public estimate | Components |
| ---: | --- | ---: | ---: | ---: | --- |
| -0.005 | `submission_projblend_capm0p005.csv` | 0.562665 | -0.005014 | 0.577943 | 85% Q3-only pure orthcap exact + 15% Q2/Q3 pure orthcap exact |
| 0.000 | `submission_projblend_cap0p0.csv` | 0.562144 | -0.000049 | 0.577945 | 98% pure Q2/Q3 exact + 2% low-projection Q2/Q3 exact |
| 0.025 | `submission_projblend_cap0p025.csv` | 0.561715 | 0.024479 | 0.577954 | 76% pure Q2/Q3 exact + 24% cap010 Q2/Q3 exact |
| 0.050 | `submission_projblend_cap0p05.csv` | 0.561307 | 0.048995 | 0.577963 | 53% pure Q2/Q3 exact + 47% cap010 Q2/Q3 exact |
| 0.075 | `submission_projblend_cap0p075.csv` | 0.560904 | 0.074578 | 0.577972 | 29% pure Q2/Q3 exact + 71% cap010 Q2/Q3 exact |
| 0.100 | `submission_projblend_cap0p1.csv` | 0.560523 | 0.099482 | 0.577981 | 11% low-projection Q3 exact + 89% cap010 Q2/Q3 exact |
| 0.150 | `submission_projblend_cap0p15.csv` | 0.560170 | 0.149470 | 0.577999 | 78% cap010 Q2/Q3 exact + 22% cap030 Q2/Q3 exact |
| 0.200 | `submission_projblend_cap0p2.csv` | 0.559879 | 0.199447 | 0.578016 | 53% cap010 Q2/Q3 exact + 47% cap030 Q2/Q3 exact |
| 0.300 | `submission_projblend_cap0p3.csv` | 0.559381 | 0.299402 | 0.578052 | 3% cap010 Q2/Q3 exact + 97% cap030 Q2/Q3 exact |

## Integrity

All generated submissions have:

- 250 rows
- 0 duplicate keys
- 0 missing predictions
- probabilities inside `[0.05844, 0.98373]` for the main low/mid-risk files

Per-target OOF deltas versus stage2 are favorable for every cap. For example:

| File | Q1 | Q2 | Q3 | S1 | S2 | S3 | S4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `submission_projblend_cap0p05.csv` | -0.002899 | -0.010036 | -0.014922 | -0.005740 | -0.002602 | -0.003393 | -0.003978 |
| `submission_projblend_cap0p1.csv` | -0.003226 | -0.009855 | -0.017437 | -0.006733 | -0.003087 | -0.004197 | -0.004517 |

## Decision

This is now the cleanest non-convex risk ladder.

Recommended public probe order:

1. `submission_projblend_cap0p0.csv` - near-zero projection diagnostic.
2. `submission_projblend_cap0p05.csv` - same projection class as low-risk orthcap, but better OOF.
3. `submission_projblend_cap0p1.csv` - balanced score/projection tradeoff.
4. `submission_projblend_cap0p15.csv` - high-upside if cap0p1 transfers.
5. `submission_projblend_cap0p2.csv` or `submission_projblend_cap0p3.csv` - score-first only.

The S2 label-prior variants are not promoted as score candidates. They look favorable under public-direction geometry, but their full OOF worsens S2 by about `+0.0020`, so they remain diagnostics only.

## Reproducibility

Generator:

```text
analysis_outputs/projection_constrained_blend_optimizer.py
```

Main generated tables:

```text
analysis_outputs/projection_constrained_blend_summary.csv
analysis_outputs/projection_constrained_blend_integrity_and_deltas.csv
analysis_outputs/projection_constrained_blend_candidates.csv
analysis_outputs/public_direction_risk_ranked_candidates.csv
```
