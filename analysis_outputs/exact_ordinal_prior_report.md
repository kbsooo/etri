# Exact Ordinal Prior Report

Last updated: 2026-05-26

## Why This Was Tested

The submitted ordinal/ambnext file scored public `0.5783033652`, worse than the current stage2 public best `0.5779449757`. That makes the raw stage2 -> ordinal move an observed public-bad direction.

I re-tested the ordinal questionnaire rule with an exact 1-5 value-count prior instead of only feasible positive-count ranges:

```text
script  ordinal_q_exact_prior_count_audit.py
rule    Q1 positive if value > subject mean, Q2/Q3 positive if value < subject mean
prior   exact multinomial count distribution over values 1..5
cv      subject-block OOF, using only fold-train labels for count constraints
```

## Main Result

The exact value prior itself does not add a new public-safe signal. Posterior mean/mode targets consistently worsen OOF. The only useful operation is still `nearest feasible hidden-positive count`.

```text
orthcap010 + Q2/Q3 nearest     0.561989 -> 0.560448
orthcap030 + Q2/Q3 nearest     0.560427 -> 0.559355
orthcap010 + Q1/Q2/Q3 nearest  0.561989 -> 0.561125  (Q1 hurts)
```

Interpretation: this is not a new Bayesian prior discovery. It is a sharper count-quantization postprocess. Q1 should stay out; Q3 carries most of the gain.

## Target Split

```text
orthcap010 + Q3 only  0.561989 -> 0.560925, projection 0.101177
orthcap010 + Q2 only  0.561989 -> 0.561512, projection 0.104313
orthcap030 + Q3 only  0.560427 -> 0.559602, projection 0.302285
orthcap030 + Q2 only  0.560427 -> 0.560180, projection 0.303115
```

Q3-only is the cleaner variant: it captures most of the ordinal gain while changing fewer target cells.

## Public-Direction Audit

Projection is measured onto the observed failed `stage2 -> ordinal/ambnext` public-bad direction. Linear public estimate uses the public gap between stage2 and the failed ordinal submission.

```text
file                                                        OOF       projection  linear public est
submission_orthcap005c000_exact_q3_exact_value_nearest_w1   0.562810  -0.005704   0.577943
submission_orthcap005c000_exact_q2q3_exact_value_nearest_w1 0.562167  -0.001103   0.577945
submission_orthcap009c005_exact_q3_exact_value_nearest_w1   0.561856   0.050876   0.577963
submission_orthcap009c005_exact_q2q3_exact_value_nearest_w1 0.561729   0.051616   0.577963
submission_orthcap010_exact_q3_exact_value_nearest_w1       0.560925   0.101177   0.577981
submission_orthcap010_exact_q2q3_exact_value_nearest_w1     0.560448   0.105490   0.577983
submission_orthcap030_exact_q3_exact_value_nearest_w1       0.559602   0.302285   0.578053
submission_orthcap030_exact_q2q3_exact_value_nearest_w1     0.559355   0.305399   0.578054
```

Best low-risk exact-prior diagnostic: `submission_orthcap005c000_exact_q3_exact_value_nearest_w1.csv`.

Best balanced exact-prior single-source probe: `submission_orthcap009c005_exact_q2q3_exact_value_nearest_w1.csv`.

Best high-upside OOF probe: `submission_orthcap030_exact_q2q3_exact_value_nearest_w1.csv`, but its projection is similar to `orthcap030`, so it is not a safety submission.

Latest decision after projection-constrained blending: the exact-prior single-source files are now mostly diagnostics/endpoints. The preferred non-convex score ladder is:

```text
submission_projblend_cap0p0.csv   OOF 0.562144, projection -0.000049
submission_projblend_cap0p05.csv  OOF 0.561307, projection  0.048995
submission_projblend_cap0p1.csv   OOF 0.560523, projection  0.099482
```

## Submission Detail

For the safest Q3-only file, the count postprocess maps each subject's hidden Q3 probability sum to the nearest integer hidden-positive count:

```text
id01 16.054 -> 16
id02 21.617 -> 22
id03 15.460 -> 15
id04 20.691 -> 21
id05 13.651 -> 14
id06 17.734 -> 18
id07 16.379 -> 16
id08  5.651 ->  6
id09 13.169 -> 13
id10 12.116 -> 12
```

All generated exact-prior submissions passed integrity checks: 250 rows, no duplicate keys, no missing target probabilities, and probability ranges inside the clipped bounds.
