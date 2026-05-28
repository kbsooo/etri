# E43 Selector Resolution Boundary Audit

## Observe

E42 shows that nonbaseline rank can improve while frontier-scale candidate edges remain below selector error.

## Wonder

Is the 0.577439 plateau mainly a candidate-quality problem, or are current selectors simply unable to read edges at the raw05-A2C8 scale?

## Hypothesis

H42: if a local selector can justify a normal near-frontier submission, its known-anchor error must be below the raw05-A2C8 public gap and at least one unobserved candidate edge must exceed that selector error.

## Method

- Raw05-A2C8 public gap: `0.0000869862`.
- Collected pairwise public-order selector reliability, old hidden-subset reliability, OOF public-rank sanity, E40 movement fingerprints, E41 movement+axis geometry, and E42 fixed-zero axis calibration.
- For candidate predictions, tested whether `predicted_delta + selector_error < 0` for A2C8 improvement and `< raw05_gap` for raw05 improvement.

## Result

- selector frontier-resolution gates: `0`.
- candidates certified better than A2C8 by error margin: `0`.
- candidates certified better than raw05 by error margin: `0`.
- public-edge-readable candidate rows: `0`.
- best selector by error: `pairwise_public_order_models` with best error `0.000218288`, raw05-gap/error ratio `0.398493`.

## Selector Resolution Summary

| selector | n_views | best_error | median_error | best_l2o_error | raw05_gap_to_best_error | raw05_gap_to_best_l2o_error | gate_count | frontier_resolution_gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pairwise_public_order_models | 36 | 0.000218288 | 0.000805613 | 0.000415499 | 0.398493 | 0.209353 | 33 | False |
| pairwise_public_order | 36 | 0.000218288 | 0.000850208 | 0.000444369 | 0.398493 | 0.195752 | 33 | False |
| old_hidden_subset | 7 | 0.000536411 | 0.000553668 | 0.000565765 | 0.162163 | 0.15375 | 0 | False |
| fixed_zero_anchor_axis | 5 | 0.000766262 | 0.000946776 |  | 0.11352 |  | 0 | False |
| test_movement_fingerprint | 5 | 0.000781461 | 0.00081491 |  | 0.111312 |  | 4 | False |
| movement_badaxis_geometry | 5 | 0.000827696 | 0.000935417 |  | 0.105094 |  | 0 | False |


## Top Candidate Edge Rows

| selector | view | name | role | predicted_delta | error_scale | edge_vs_a2c8_to_error | edge_vs_raw05_to_error | certified_better_than_a2c8 | certified_better_than_raw05 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_693b0ea9.csv | hiddenloc_bridge | -1.56228e-06 | 0.000218288 | 0.00715695 | 0.40565 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_76ae5309.csv | hiddenloc_bridge | -1.52079e-06 | 0.000218288 | 0.00696692 | 0.40546 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_b26a7e99.csv | hiddenloc_bridge | -1.50808e-06 | 0.000218288 | 0.00690867 | 0.405402 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_705a17ba.csv | hiddenloc_bridge | -1.49578e-06 | 0.000218288 | 0.00685234 | 0.405345 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_6dc9bfcc.csv | hiddenloc_bridge | -1.13739e-06 | 0.000218288 | 0.00521052 | 0.403704 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_a50b04d6.csv | hiddenloc_bridge | -1.11432e-06 | 0.000218288 | 0.0051048 | 0.403598 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_8ff484be.csv | hiddenloc_bridge | -1.06902e-06 | 0.000218288 | 0.00489731 | 0.40339 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_4fc2a73c.csv | hiddenloc_bridge | -1.00421e-06 | 0.000218288 | 0.0046004 | 0.403093 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_773913a3.csv | hiddenloc_bridge | -7.26319e-07 | 0.000218288 | 0.00332734 | 0.40182 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_81e7b614.csv | hiddenloc_bridge | -7.26319e-07 | 0.000218288 | 0.00332734 | 0.40182 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_07590a56.csv | hiddenloc_bridge | -6.79071e-07 | 0.000218288 | 0.00311089 | 0.401604 | False | False |
| pairwise_public_order_models | pair_p90 | submission_hiddenloc_bridge_16c6e986.csv | hiddenloc_bridge | -6.79071e-07 | 0.000218288 | 0.00311089 | 0.401604 | False | False |


## Decision

No audited selector has enough resolution to certify a near-frontier improvement. The best known-anchor selector error is still several times larger than the raw05-A2C8 public gap, and no candidate edge survives an error-margin test. This supports the bottleneck diagnosis: the current plateau is dominated by selector resolution/public-worldview uncertainty, not by lack of another small blend.

## Outputs

- `analysis_outputs/selector_resolution_boundary_audit_selectors.csv`
- `analysis_outputs/selector_resolution_boundary_audit_candidate_edges.csv`
- `analysis_outputs/selector_resolution_boundary_audit_report.md`
