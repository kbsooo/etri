# E188 Shape/Support Logit Blend Stress

## Question

Can a very small support prior improve E95-edge stress without destroying the
exact E95/E101 public boundary that shape-only gets right?

## Result In One Sentence

No positive shape/support logit blend repairs the conflict: edge-band accuracy stays at shape-only levels until E95/E101 flips.

## Best Per Support Variant

| support_variant | alpha | accuracy | frontier_accuracy | micro_accuracy | edge_accuracy | e95_e101_accuracy | e95_prob_mean | e101_prob_mean | e176_favorable_rate | e176_prob_mean | action_grade | first_e95_e101_failure_alpha |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| shape_support | 0.000000000 | 0.795454545 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False | 0.185000000 |
| shape_support_drop_subject | 0.000000000 | 0.795454545 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False | 0.220000000 |
| shape_support_drop_global | 0.000000000 | 0.795454545 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False | 0.180000000 |
| shape_support_drop_top16_33 | 0.000000000 | 0.795454545 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False | 0.170000000 |
| shape_support_no_q2s3_targets | 0.000000000 | 0.795454545 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False | 0.195000000 |
| shape_support_keep_hard_only | 0.000000000 | 0.795454545 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False | 0.285000000 |
| shape_support_drop_visible | 0.000000000 | 0.795454545 | 0.833333333 | 0.750000000 | 0.785714286 | 1.000000000 | 0.762677059 | 0.237322941 | 1.000000000 | 0.925898875 | False | 0.200000000 |

## Best Action-Grade Rows

_empty_

## Interpretation

- Shape-only is the only family that respects the exact E95/E101 boundary.
- Support variants add useful wider edge-band signal, but the useful threshold
  is beyond the alpha where E95/E101 already flips.
- Therefore support is not a weak repair prior; it is a different public-quality
  shortcut. It can be used as a sensor, but not as an automatic frontier
  selector without an external boundary veto.
