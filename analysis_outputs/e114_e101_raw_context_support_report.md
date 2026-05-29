# E114 E101 Raw-Context Support Audit

## Question

E113 rejected broad raw-context prediction. The smaller question is whether the
same raw context can still act as an energy for the `50` E101 active cells:
does it assign higher probability to the hard labels that would make E101 beat
E95?

## Summary

| probability_source | expected_delta_sum | mean_delta_vs_e95 | p_e101_beats_e95 | p_e101_matches_e95_edge | mean_support_probability | weighted_support_minus_subject | p95_delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| global_prior_y1 | 0.000024475 | 0.000024464 | 0.016490000 | 0.000185000 | 0.498000000 | -0.133278455 | 0.000043911 |
| subject_prior_y1 | 0.000003926 | 0.000003900 | 0.336655000 | 0.012200000 | 0.587685814 | 0.000000000 | 0.000018872 |
| full_subject_prior_y1 | 0.000004444 | 0.000004463 | 0.316950000 | 0.010790000 | 0.585846664 | -0.003359186 | 0.000019629 |
| raw_plus_prior_y1 | 0.000007010 | 0.000006997 | 0.238325000 | 0.007600000 | 0.579426216 | -0.020003127 | 0.000023290 |
| validation_gated_raw_y1 | 0.000007229 | 0.000007246 | 0.230710000 | 0.006940000 | 0.575835443 | -0.021417909 | 0.000023613 |

## By Target

| target | active_cells | temporal_raw_delta_vs_subject_prior | temporal_valid_raw_target | flip_benefit_share | subject_prior_y1_support_probability_mean | raw_plus_prior_y1_support_probability_mean | validation_gated_raw_y1_support_probability_mean | subject_prior_y1_expected_delta_per_all_cells_sum | raw_plus_prior_y1_expected_delta_per_all_cells_sum | validation_gated_raw_y1_expected_delta_per_all_cells_sum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S3 | 39 | -0.004642580 | True | 0.935862322 | 0.604450426 | 0.589463252 | 0.589463252 | 0.000002872 | 0.000006161 | 0.000006161 |
| Q2 | 11 | 0.030182110 | False | 0.064137678 | 0.528247641 | 0.543840359 | 0.527518665 | 0.000001054 | 0.000000849 | 0.000001067 |

## Interpretation

- Raw+prior does not support E101 more than subject prior.
- Validation-gated raw, which trusts raw only on temporal-valid targets, still fails after validation-gating.
- Temporal validation trusts S3 but rejects Q2: Q2 raw temporal delta is `+0.030182`, S3 raw temporal delta is `-0.004643`.

This is not a submission model. If raw support improves E101, it is only a weak
interpretation energy because E113 already rejected broad raw-context
calibration. If it does not improve E101, raw context is demoted further: it
cannot rescue Q temporal state and cannot pre-validate E101's active-cell label
world.

## Outputs

- `e114_e101_raw_context_support_cells.csv`
- `e114_e101_raw_context_support_by_target.csv`
- `e114_e101_raw_context_support_summary.csv`
