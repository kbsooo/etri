# E47 Block-Context JEPA Target Audit

## Question

Can fold-safe context predict the held-out block-rate representation strongly enough to recover a meaningful part of the validation block-rate oracle gap?

## Summary

- Temporal row LogLoss: `0.624765`.
- Validation block-rate oracle LogLoss: `0.517878`.
- Temporal-to-oracle gap available to a perfect block-state representation: `0.106888`.
- Best tested view by 25% row blend: `label_context_ridge` at `0.623260`.
- Best non-base recovered oracle-gap fraction: `0.014083`.

## View Results

| view | n_features | block_weighted_logloss | block_rate_mae | block_rate_r2 | row_blend025_logloss | delta_blend025_vs_temporal | oracle_gap_recovered_blend025 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| label_context_ridge | 164.000000 | 0.635888 | 0.165528 | 0.246598 | 0.623260 | -0.001505 | 0.014083 |
| missingness_ridge | 1396.000000 | 0.639375 | 0.179074 | 0.189484 | 0.623939 | -0.000826 | 0.007728 |
| combined_ridge | 5652.000000 | 0.648390 | 0.169521 | 0.220683 | 0.624561 | -0.000204 | 0.001907 |
| temporal_base | 0.000000 | 0.623448 | 0.160394 | 0.306123 | 0.624765 | 0.000000 | 0.000000 |
| sensor_values_ridge | 4140.000000 | 0.657811 | 0.178975 | 0.154092 | 0.625425 | 0.000660 | -0.006174 |

## Latent Geometry

| view | block_weighted_logloss | anisotropy | effective_rank | nn_true_rate_mae | energy_p90 | top20_block_energy_share |
| --- | --- | --- | --- | --- | --- | --- |
| label_context_ridge | 0.635888 | 0.466748 | 3.547232 | 0.214740 | 0.729318 | 0.235049 |
| missingness_ridge | 0.639375 | 0.332154 | 5.369291 | 0.230369 | 0.745224 | 0.216671 |
| combined_ridge | 0.648390 | 0.414961 | 4.491825 | 0.204202 | 0.727554 | 0.243606 |
| sensor_values_ridge | 0.657811 | 0.375375 | 5.007055 | 0.224155 | 0.739039 | 0.235307 |

## Interpretation

This is a JEPA-style target-representation test: context consists of fold-safe same-subject label context plus sensor/missingness block summaries; target is the held-out block-rate vector, not raw reconstruction.

A useful representation should reduce block-rate loss, improve row LogLoss under a conservative blend, and keep a non-collapsed geometry. If it only improves an auxiliary score or shows anisotropic high-energy concentration, it is evidence for a representation bottleneck rather than a submission candidate.

## Decision

No tested fold-safe context representation recovers useful oracle gap under block-rate stress. The best non-base row blend moves only `0.014083` of the oracle gap, and its block-rate loss is `0.012440` worse than temporal block context.

The small row-level gains are therefore better interpreted as weak calibration perturbations, not successful hidden block-state recovery.

Do not submit a file from this audit. The next useful branch is to change the target/context construction itself, not add another ridge-style block regressor.
