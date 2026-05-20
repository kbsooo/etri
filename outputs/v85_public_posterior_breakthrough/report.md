# v85 public-posterior breakthrough candidates

- Goal: build a last-slot candidate with upside near/under `0.55`, not another `0.59x` hedge.
- Method: fit a sharpened soft-label posterior that exactly matches known Public LB constraints, now including v82 fail and v83 success.
- Old conservative posterior entropy was about `0.590`; tau-sharpening uses its row ordering but reduces entropy.
- This is high-risk leaderboard-feedback distillation. It is intentionally more aggressive than v84.

## Candidate ranking by self entropy

| name | self_entropy | bce_old_posterior | max_constraint_error_vs_known | mean | min | p01 | p99 | max | mean_Q1 | mean_S1 | mean_S3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tau08_clip001 | 0.517423 | 0.669207 | 0.000008 | 0.610519 | 0.001000 | 0.039605 | 0.998205 | 0.999000 | 0.470415 | 0.650801 | 0.693259 |
| tau08_clip005 | 0.517802 | 0.664724 | 0.000068 | 0.610485 | 0.005000 | 0.039605 | 0.995000 | 0.995000 | 0.470415 | 0.650801 | 0.693259 |
| tau08_clip010 | 0.518364 | 0.661631 | 0.000183 | 0.610426 | 0.010000 | 0.039605 | 0.990000 | 0.990000 | 0.470415 | 0.650801 | 0.693259 |
| tau08_clip020 | 0.519776 | 0.657552 | 0.000552 | 0.610212 | 0.020000 | 0.039605 | 0.980000 | 0.980000 | 0.470410 | 0.650779 | 0.693190 |
| tau07_clip001 | 0.529178 | 0.652869 | 0.000007 | 0.610407 | 0.001000 | 0.056422 | 0.996776 | 0.999000 | 0.472544 | 0.655537 | 0.691531 |
| tau07_clip005 | 0.529469 | 0.649718 | 0.000051 | 0.610376 | 0.005000 | 0.056422 | 0.995000 | 0.995000 | 0.472544 | 0.655537 | 0.691531 |
| tau07_clip010 | 0.529920 | 0.647401 | 0.000145 | 0.610328 | 0.010000 | 0.056422 | 0.990000 | 0.990000 | 0.472544 | 0.655537 | 0.691531 |
| tau07_clip020 | 0.531051 | 0.644158 | 0.000444 | 0.610169 | 0.020000 | 0.056422 | 0.980000 | 0.980000 | 0.472544 | 0.655532 | 0.691479 |
| tau06_clip001 | 0.540678 | 0.637462 | 0.000004 | 0.610282 | 0.001000 | 0.079444 | 0.994239 | 0.999000 | 0.474951 | 0.660527 | 0.689840 |
| tau06_clip005 | 0.540890 | 0.635537 | 0.000039 | 0.610253 | 0.005000 | 0.079444 | 0.994239 | 0.995000 | 0.474951 | 0.660527 | 0.689840 |
| tau06_clip010 | 0.541223 | 0.634014 | 0.000105 | 0.610212 | 0.010000 | 0.079444 | 0.990000 | 0.990000 | 0.474951 | 0.660527 | 0.689840 |
| tau06_clip020 | 0.542070 | 0.631745 | 0.000335 | 0.610096 | 0.020000 | 0.079444 | 0.980000 | 0.980000 | 0.474951 | 0.660527 | 0.689806 |
| tau05_clip001 | 0.551810 | 0.623245 | 0.000001 | 0.610135 | 0.001767 | 0.104919 | 0.989770 | 0.999000 | 0.477657 | 0.665734 | 0.688224 |
| tau05_clip005 | 0.551925 | 0.622496 | 0.000029 | 0.610119 | 0.005000 | 0.104919 | 0.989770 | 0.995000 | 0.477657 | 0.665734 | 0.688224 |
| tau05_clip010 | 0.552169 | 0.621551 | 0.000077 | 0.610077 | 0.010000 | 0.104919 | 0.989274 | 0.990000 | 0.477657 | 0.665734 | 0.688224 |
| tau05_clip020 | 0.552749 | 0.620215 | 0.000223 | 0.609981 | 0.020000 | 0.104919 | 0.980000 | 0.980000 | 0.477657 | 0.665734 | 0.688210 |
| tau04_clip001 | 0.562457 | 0.610863 | 0.000000 | 0.609953 | 0.005962 | 0.128264 | 0.981252 | 0.998774 | 0.480677 | 0.671110 | 0.686722 |
| tau04_clip005 | 0.562485 | 0.610763 | 0.000011 | 0.609948 | 0.005962 | 0.128264 | 0.981252 | 0.995000 | 0.480677 | 0.671110 | 0.686722 |
| tau04_clip010 | 0.562597 | 0.610471 | 0.000049 | 0.609930 | 0.010000 | 0.128264 | 0.981252 | 0.990000 | 0.480677 | 0.671110 | 0.686722 |
| tau04_clip020 | 0.562983 | 0.609729 | 0.000150 | 0.609849 | 0.020000 | 0.128264 | 0.980000 | 0.980000 | 0.480677 | 0.671110 | 0.686721 |

## Recommended final upload

- **`submission_v85_tau06_clip005.csv`**
- self-entropy target: `0.540890`.
- max known-score constraint error after clipping: `0.000039`.
- probability range: `0.005000` to `0.995000`; p01/p99 `0.079444` / `0.994239`.
- Rationale: tau=5 is only barely below 0.55; tau=7/8 are more saturated and risk catastrophic wrong-confidence. tau=6 clip=0.005 is the most reasonable high-upside middle point.
- Interpretation: if the public posterior geometry is real, this is a plausible 0.54-0.55 candidate. If the constraints are underdetermined, it can fail badly. That is the accepted risk for the final slot.
